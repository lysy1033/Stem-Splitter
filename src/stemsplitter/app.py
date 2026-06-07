import zipfile
from pathlib import Path

import gradio as gr

from . import engine, media, paths, pipeline, youtube
from .i18n import PRESET_KEYS, STEM_KEYS, TEXT, pick_lang


def _ensure_ffmpeg():
    """Dodaje ffmpeg/ffprobe (z pakietu static-ffmpeg) do PATH, jezeli sa.
    Dzieki temu nie trzeba instalowac ffmpeg systemowo (brak Homebrew/winget)."""
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()  # 1. wywolanie pobiera binaria
    except Exception:
        pass  # gdy systemowy ffmpeg jest na PATH, tez zadziala


def _zip_results(result: dict[str, str], output_dir: Path) -> str:
    zip_path = output_dir / "stems.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        for stem, fpath in result.items():
            z.write(fpath, arcname=f"{stem}{Path(fpath).suffix}")
    return str(zip_path)


def separate(file_path, url, chosen_stems, preset_key, split_vocals, split_drums, lang,
             progress=gr.Progress()):
    t = TEXT.get(lang, TEXT["en"])
    if not chosen_stems:
        raise gr.Error(t["err_no_stem"])

    _ensure_ffmpeg()
    dirs = paths.ensure_data_dirs()
    if url and url.strip():
        progress(0.05, desc=t["dl"])
        source = youtube.download_audio(url.strip(), dirs.work)
    elif file_path:
        source = Path(file_path)
    else:
        raise gr.Error(t["err_no_input"])

    progress(0.1, desc=t["prep"])
    prepared = media.prepare_input(source, work_dir=dirs.work)

    extensions = []
    requested = list(chosen_stems)
    if split_vocals and "wokal" in chosen_stems:
        extensions.append("lead_chorki")
        requested += ["lead", "chorki"]
    if split_drums and "perkusja" in chosen_stems:
        extensions.append("perkusja_elementy")
        requested += ["stopa", "werbel", "tomy", "hihat", "ride", "crash"]

    pipe = pipeline.load_preset(preset_key, extensions=extensions)
    accel = engine.detect_acceleration()
    progress(0.3, desc=t["sep"].format(accel=accel))

    def on_stage(done: int, total: int, model_id: str):
        # postep rosnie z kazdym etapem kaskady; pokazujemy ktory model pracuje
        frac = 0.3 + 0.6 * (done / total)
        progress(frac, desc=t["sep_stage"].format(n=done + 1, total=total,
                                                   model=model_id, accel=accel))

    result = engine.run_pipeline(prepared, pipe, requested, output_dir=dirs.output,
                                 progress_cb=on_stage)
    progress(0.95, desc=t["pack"])
    return _zip_results(result, dirs.output)


def _localize(request: gr.Request):
    """Na zaladowanie strony: ustaw jezyk wg przegladarki i przetlumacz etykiety."""
    lang = pick_lang(request)
    t = TEXT[lang]
    accel = engine.detect_acceleration()
    return (
        lang,
        gr.update(value=f"# {t['title']}\n{t['accel']}: **{accel}**"),
        gr.update(label=t["file"]),
        gr.update(label=t["url"], placeholder=t["url_ph"]),
        gr.update(choices=[(t["stem_labels"][k], k) for k in STEM_KEYS], label=t["stems"]),
        gr.update(choices=[(t["presets"][k], k) for k in PRESET_KEYS], label=t["quality"]),
        gr.update(label=t["split_vocals"]),
        gr.update(label=t["split_drums"]),
        gr.update(value=t["run"]),
        gr.update(label=t["result"]),
    )


def build_ui() -> gr.Blocks:
    en = TEXT["en"]
    with gr.Blocks(title="StemSplitter") as demo:
        lang_state = gr.State("en")
        header = gr.Markdown(f"# {en['title']}")
        file_in = gr.File(label=en["file"], type="filepath")
        url_in = gr.Textbox(label=en["url"], placeholder=en["url_ph"])
        stems = gr.CheckboxGroup(
            choices=[(en["stem_labels"][k], k) for k in STEM_KEYS],
            value=["wokal", "perkusja", "bas", "inne"],
            label=en["stems"],
        )
        preset = gr.Radio(
            choices=[(en["presets"][k], k) for k in PRESET_KEYS],
            value="najlepsza",
            label=en["quality"],
        )
        split_vocals = gr.Checkbox(label=en["split_vocals"], value=False)
        split_drums = gr.Checkbox(label=en["split_drums"], value=False)
        btn = gr.Button(en["run"], variant="primary")
        out = gr.File(label=en["result"])

        btn.click(separate,
                  [file_in, url_in, stems, preset, split_vocals, split_drums, lang_state], out)
        demo.load(_localize, None,
                  [lang_state, header, file_in, url_in, stems, preset,
                   split_vocals, split_drums, btn, out])
    return demo


def main():
    _ensure_ffmpeg()  # pobierz/ustaw ffmpeg juz przy starcie
    build_ui().launch(inbrowser=True)


if __name__ == "__main__":
    main()

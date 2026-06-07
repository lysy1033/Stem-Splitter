import sys
import zipfile
from pathlib import Path

import gradio as gr

from . import engine, media, paths, pipeline, youtube
from .i18n import PRESET_KEYS, STEM_KEYS, TEXT, pick_lang


def _force_utf8_io() -> None:
    """Wymusza UTF-8 na stdout/stderr (Windows: domyslnie cp1250).

    Paski postepu tqdm (pobieranie modelu w audio-separator) uzywaja znakow
    blokowych Unicode (np. ▏). Konsola PL ma kodowanie cp1250, ktore ich nie
    zna -> UnicodeEncodeError. errors='replace' dodatkowo zabezpiecza przed
    pojedynczymi nieenkodowalnymi znakami zamiast wywalac caly proces."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass  # brak reconfigure (np. przekierowany strumien) — pomijamy


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
             progress=gr.Progress(track_tqdm=True)):
    # Generator: na biezaco aktualizuje TRWALA linie statusu (ktory etap) + plik na koncu.
    # track_tqdm=True: pasek postepu podaza za wewnetrznym tqdm modelu (ruch w trakcie etapu).
    t = TEXT.get(lang, TEXT["en"])
    if not chosen_stems:
        raise gr.Error(t["err_no_stem"])

    _ensure_ffmpeg()
    dirs = paths.ensure_data_dirs()
    if url and url.strip():
        yield t["dl"], None
        source = youtube.download_audio(url.strip(), dirs.work)
    elif file_path:
        source = Path(file_path)
    else:
        raise gr.Error(t["err_no_input"])

    yield t["prep"], None
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

    result: dict[str, str] = {}
    for event in engine.run_pipeline_steps(prepared, pipe, requested, output_dir=dirs.output):
        if event[0] == "stage":
            _, idx, total, model_id = event
            label = t["stage_labels"].get(model_id, model_id)
            yield t["sep_stage"].format(n=idx + 1, total=total, label=label, accel=accel), None
        else:
            result = event[1]

    yield t["pack"], None
    zip_path = _zip_results(result, dirs.output)
    yield t["done"], zip_path


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
        status = gr.Markdown("")  # trwala informacja o biezacym etapie
        out = gr.File(label=en["result"])

        btn.click(separate,
                  [file_in, url_in, stems, preset, split_vocals, split_drums, lang_state],
                  [status, out])
        demo.load(_localize, None,
                  [lang_state, header, file_in, url_in, stems, preset,
                   split_vocals, split_drums, btn, out])
    return demo


def main():
    _force_utf8_io()  # zapobiega UnicodeEncodeError na konsoli PL (cp1250)
    _ensure_ffmpeg()  # pobierz/ustaw ffmpeg juz przy starcie
    # allowed_paths: pozwol Gradio serwowac pliki wynikowe z ~/StemSplitter (poza cwd/temp)
    out_dir = str(paths.ensure_data_dirs().base)
    build_ui().launch(inbrowser=True, allowed_paths=[out_dir])


if __name__ == "__main__":
    main()

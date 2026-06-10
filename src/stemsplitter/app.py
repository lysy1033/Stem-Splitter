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


def _zip_results(result: dict[str, str], output_dir: Path, title: str,
                 extras: list[Path] | None = None) -> str:
    zip_path = output_dir / f"{media.safe_filename(title)}.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        for stem, fpath in result.items():
            z.write(fpath, arcname=f"{stem}{Path(fpath).suffix}")
        for extra in extras or []:
            z.write(extra, arcname=Path(extra).name)
    return str(zip_path)


def separate(file_path, url, chosen_stems, preset_key, yt_full, split_vocals, split_drums, lang,
             progress=gr.Progress(track_tqdm=True)):
    # Generator: na biezaco aktualizuje TRWALA linie statusu (ktory etap) + plik na koncu.
    # track_tqdm=True: pasek postepu podaza za wewnetrznym tqdm modelu (ruch w trakcie etapu).
    t = TEXT.get(lang, TEXT["en"])
    if not chosen_stems:
        raise gr.Error(t["err_no_stem"])

    _ensure_ffmpeg()
    dirs = paths.ensure_data_dirs()
    extras: list[Path] = []
    if url and url.strip():
        yield t["dl"], gr.update(visible=False)
        source, title = youtube.download_audio(url.strip(), dirs.work)
        if yt_full:
            extras.append(media.to_mp3(source, dirs.work, title))
    elif file_path:
        source = Path(file_path)
        title = source.stem
    else:
        raise gr.Error(t["err_no_input"])

    yield t["prep"], gr.update(visible=False)
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
            _, idx, total, model_id, passes = event
            label = t["stage_labels"].get(model_id, model_id)
            key = "sep_stage_multi" if passes > 1 else "sep_stage"
            yield t[key].format(n=idx + 1, total=total, label=label,
                                accel=accel, passes=passes), gr.update(visible=False)
        else:
            result = event[1]

    yield t["pack"], gr.update(visible=False)
    zip_path = _zip_results(result, dirs.output, title, extras)
    done = t["done"]
    missing = [s for s in requested if s not in result]
    if missing:
        labels = ", ".join(t["stem_labels"].get(s, s) for s in missing)
        done = f"{done} {t['missing_stems'].format(stems=labels)}"
    yield done, gr.update(value=zip_path, visible=True)


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
        gr.update(choices=[(t["presets"][k], k) for k in PRESET_KEYS], label=t["quality"]),
        gr.update(choices=[(t["stem_labels"][k], k) for k in STEM_KEYS], label=t["stems"]),
        gr.update(label=t["yt_full"]),
        gr.update(label=t["split_vocals"]),
        gr.update(label=t["split_drums"]),
        gr.update(value=t["run"]),
        gr.update(value=t["stop"]),
        gr.update(label=t["result"]),
        gr.update(value=t["idle"]),
    )


# Gradio wstrzykuje ten skrypt do strony doslownie, wiec musi sie sam wywolac (IIFE).
_FORCE_DARK_JS = """
(() => {
  const url = new URL(window.location);
  if (url.searchParams.get('__theme') !== 'dark') {
    url.searchParams.set('__theme', 'dark');
    window.location.href = url.href;
  }
})();
"""

_CSS = """
.gradio-container {max-width: 1100px !important; margin: 0 auto !important;}
footer {display: none !important;}
h1 {text-transform: uppercase; letter-spacing: .14em; font-size: 1.1rem !important; font-weight: 600;}
#console {font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace; font-size: .85rem;
          border: 1px solid var(--border-color-primary); padding: 14px 16px; min-height: 140px;}
#console p {margin: 0 0 6px 0;}
button {text-transform: uppercase; letter-spacing: .05em;}
"""


def build_ui() -> gr.Blocks:
    en = TEXT["en"]
    with gr.Blocks(title="StemSplitter") as demo:
        lang_state = gr.State("en")
        header = gr.Markdown(f"# {en['title']}")

        with gr.Row():
            with gr.Column(scale=5):
                # zrodlo
                file_in = gr.File(label=en["file"], type="filepath")
                url_in = gr.Textbox(label=en["url"], placeholder=en["url_ph"])
                # preset
                preset = gr.Radio(
                    choices=[(en["presets"][k], k) for k in PRESET_KEYS],
                    value="normalna",
                    label=en["quality"],
                )
                # sciezki
                stems = gr.CheckboxGroup(
                    choices=[(en["stem_labels"][k], k) for k in STEM_KEYS],
                    value=["wokal", "perkusja", "bas", "inne"],
                    label=en["stems"],
                )
                # opcje dodatkowe
                yt_full = gr.Checkbox(label=en["yt_full"], value=False)
                split_vocals = gr.Checkbox(label=en["split_vocals"], value=False)
                split_drums = gr.Checkbox(label=en["split_drums"], value=False)
            with gr.Column(scale=4):
                # konsola statusu (trwala informacja o biezacym etapie)
                status = gr.Markdown("", elem_id="console")
                # wynik ukryty do czasu gotowej paczki (pusty wyglada jak drugi upload)
                out = gr.File(label=en["result"], visible=False)

        with gr.Row():
            btn = gr.Button(en["run"], variant="primary")
            stop_btn = gr.Button(en["stop"], variant="stop")

        # Na czas pracy blokujemy wszystko poza Stop; odblokowanie po zakonczeniu
        # (sukces: .then; blad gr.Error: .failure — w Gradio 6 .then nie odpala sie po bledzie)
        # lub w handlerze Stop (anulowany lancuch nie wykona juz swojego .then).
        lockable = [file_in, url_in, preset, stems, yt_full, split_vocals, split_drums, btn]

        def _set_interactive(value):
            return lambda: [gr.update(interactive=value)] * len(lockable)

        sep_event = btn.click(
            _set_interactive(False), None, lockable,
        ).then(
            separate,
            [file_in, url_in, stems, preset, yt_full, split_vocals, split_drums, lang_state],
            [status, out],
        )
        sep_event.then(_set_interactive(True), None, lockable)
        sep_event.failure(_set_interactive(True), None, lockable)

        def _on_stop(lang):
            t = TEXT.get(lang, TEXT["en"])
            return [t["stopped"]] + [gr.update(interactive=True)] * len(lockable)

        # Pipeline oddaje sterowanie MIEDZY etapami, wiec zatrzymanie zadziala
        # po zakonczeniu biezacego kroku (wywolania modelu nie da sie przerwac w polowie).
        stop_btn.click(_on_stop, [lang_state], [status] + lockable, cancels=[sep_event])

        demo.load(_localize, None,
                  [lang_state, header, file_in, url_in, preset, stems, yt_full,
                   split_vocals, split_drums, btn, stop_btn, out, status])
    return demo


def main():
    _force_utf8_io()  # zapobiega UnicodeEncodeError na konsoli PL (cp1250)
    _ensure_ffmpeg()  # pobierz/ustaw ffmpeg juz przy starcie
    # allowed_paths: pozwol Gradio serwowac pliki wynikowe z ~/StemSplitter (poza cwd/temp)
    out_dir = str(paths.ensure_data_dirs().base)
    build_ui().launch(inbrowser=True, allowed_paths=[out_dir],
                      theme=gr.themes.Base(primary_hue="amber", neutral_hue="zinc",
                                           radius_size=gr.themes.sizes.radius_none,
                                           font=["system-ui", "-apple-system", "sans-serif"],
                                           font_mono=["ui-monospace", "SF Mono", "Menlo", "Consolas", "monospace"]),
                      css=_CSS, js=_FORCE_DARK_JS)


if __name__ == "__main__":
    main()

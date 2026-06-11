import datetime
import sys
import zipfile
from pathlib import Path

import gradio as gr

from . import engine, media, paths, pipeline, update, youtube
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


def _latest_zip(output_dir: Path) -> Path | None:
    """Najnowsza gotowa paczka w folderze wynikowym (None, gdy brak)."""
    zips = list(output_dir.glob("*.zip"))
    return max(zips, key=lambda p: p.stat().st_mtime) if zips else None


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

    # Uspiona karta przegladarki zrywa polaczenie -> Gradio zamyka generator
    # (GeneratorExit na yield). Wyniki sa juz policzone, wiec paczka musi
    # powstac mimo to — po powrocie na strone _localize pokaze ja do pobrania.
    try:
        yield t["pack"], gr.update(visible=False)
    except GeneratorExit:
        _zip_results(result, dirs.output, title, extras)
        raise
    zip_path = _zip_results(result, dirs.output, title, extras)
    done = t["done"]
    missing = [s for s in requested if s not in result]
    if missing:
        labels = ", ".join(t["stem_labels"].get(s, s) for s in missing)
        done = f"{done} {t['missing_stems'].format(stems=labels)}"
    yield done, gr.update(value=zip_path, visible=True)


def _localize(request: gr.Request):
    """Na zaladowanie strony: ustaw jezyk wg przegladarki i przetlumacz etykiety.

    Odpala sie tez po obudzeniu uspionej karty (przegladarka laduje strone od
    nowa po zerwanym polaczeniu), wiec pokazuje najnowsza gotowa paczke —
    bez tego wynik dlugiej pracy bylby niemozliwy do pobrania z GUI."""
    lang = pick_lang(request)
    t = TEXT[lang]
    accel = engine.detect_acceleration()
    upd = update.update_available()
    upd_text = t["upd_available"].format(current=upd[0], latest=upd[1]) if upd else ""
    status_text = t["idle"]
    last = _latest_zip(paths.ensure_data_dirs().output)
    if last is not None:
        when = datetime.datetime.fromtimestamp(last.stat().st_mtime).strftime("%d.%m %H:%M")
        status_text = f"{t['idle']}\n\n{t['last_pack'].format(name=last.name, time=when)}"
    return (
        lang,
        gr.update(value=f"# {t['title']}\n{t['accel']}: **{accel}** · v **{update.current_version()}**"),
        gr.update(label=t["file"]),
        gr.update(label=t["url"], placeholder=t["url_ph"]),
        gr.update(choices=[(t["presets"][k], k) for k in PRESET_KEYS], label=t["quality"]),
        gr.update(choices=[(t["stem_labels"][k], k) for k in STEM_KEYS], label=t["stems"]),
        gr.update(label=t["yt_full"]),
        gr.update(label=t["split_vocals"]),
        gr.update(label=t["split_drums"]),
        gr.update(value=t["run"]),
        gr.update(value=t["stop"]),
        gr.update(label=t["result"], value=str(last) if last else None,
                  visible=last is not None),
        gr.update(value=status_text),
        gr.update(visible=upd is not None),
        gr.update(value=upd_text),
        gr.update(value=t["upd_button"]),
    )


# Gradio wstrzykuje ten skrypt doslownie, wiec musi sie sam wywolac (IIFE).
# Dwie rzeczy: wymusza ciemny motyw i dogrywa fonty (offline: fallback systemowy).
_BOOT_JS = """
(() => {
  const url = new URL(window.location);
  if (url.searchParams.get('__theme') !== 'dark') {
    url.searchParams.set('__theme', 'dark');
    window.location.href = url.href;
    return;
  }
  if (!document.getElementById('hud-fonts')) {
    const l = document.createElement('link');
    l.id = 'hud-fonts';
    l.rel = 'stylesheet';
    l.href = 'https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap';
    document.head.appendChild(l);
  }
})();
"""

_CSS = """
:root {--hud: #f59e0b; --hud-dim: rgba(245,158,11,.55); --ink: #e7e9ee; --mut: #d4d8df; --line: #24272e;}
body {background:
  radial-gradient(900px 420px at 50% -10%, rgba(245,158,11,.07), transparent 60%),
  repeating-linear-gradient(0deg, transparent 0 23px, rgba(255,255,255,.012) 23px 24px),
  repeating-linear-gradient(90deg, transparent 0 23px, rgba(255,255,255,.012) 23px 24px),
  #06070a !important;}
.gradio-container {max-width: 1160px !important; margin: 0 auto !important; font-family: 'Chakra Petch', system-ui, sans-serif !important;}
footer {display: none !important;}
.block, .form {background: linear-gradient(180deg, #0d0f13, #0a0c10) !important; border: 1px solid var(--line) !important;
  box-shadow: 0 1px 0 rgba(255,255,255,.025) inset, 0 8px 24px rgba(0,0,0,.35) !important;}
/* masthead */
.block:has(h1) {padding: 14px 18px !important; border-left: 3px solid var(--hud) !important;}
.prose:has(> h1), .md:has(> h1) {display: flex !important; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;}
h1 {font-family: 'Chakra Petch', system-ui, sans-serif !important; font-weight: 700 !important; font-size: 1.5rem !important;
  letter-spacing: .34em !important; color: var(--ink) !important; margin: 2px 0 !important;}
h1::after {content: "_"; color: var(--hud); animation: blink 1.1s steps(1) infinite; margin-left: 2px;}
@keyframes blink {50% {opacity: 0;}}
h1 + p {font-family: 'IBM Plex Mono', ui-monospace, monospace !important; display: inline-block; font-size: 10px !important;
  letter-spacing: .18em; text-transform: uppercase; color: var(--mut) !important; border: 1px solid var(--line);
  padding: 4px 10px; background: #08090c; margin: 0 !important;}
h1 + p strong {color: var(--hud) !important; font-weight: 600 !important;}
/* etykiety sekcji */
label > span, span[data-testid="block-info"] {font-family: 'IBM Plex Mono', ui-monospace, monospace !important;
  text-transform: uppercase !important; letter-spacing: .22em !important; font-size: 10px !important; color: #c9cdd6 !important;}
span[data-testid="block-info"]::before {content: "// "; color: var(--hud-dim);}
/* strefa uploadu */
.boundedheight {max-height: 150px !important; min-height: 130px !important; border: 1px dashed #2c3038 !important;
  margin: 8px; background: rgba(255,255,255,.012) !important;}
.boundedheight * {font-family: 'IBM Plex Mono', ui-monospace, monospace !important; font-size: 11.5px !important;
  font-weight: 400 !important; letter-spacing: .12em; color: #c9cdd6 !important; text-transform: uppercase;}
/* pola tekstowe */
input[type=text], textarea {background: #08090c !important; border: 1px solid var(--line) !important;
  font-family: 'IBM Plex Mono', ui-monospace, monospace !important; font-size: 12.5px !important; color: var(--ink) !important;}
input::placeholder, textarea::placeholder {color: #878e99 !important; opacity: 1 !important;}
input[type=text]:focus, textarea:focus {border-color: var(--hud-dim) !important; box-shadow: 0 0 0 1px var(--hud-dim) !important;}
/* chipy wyboru (grupy radio i checkbox) */
[data-testid="checkbox-group"] label, fieldset label {background: transparent !important; border: 1px solid #424854 !important;
  color: #dfe3e9 !important; font-family: 'IBM Plex Mono', ui-monospace, monospace !important; font-size: 11px !important;
  letter-spacing: .1em; text-transform: uppercase; transition: all .15s ease;}
[data-testid="checkbox-group"] label:hover, fieldset label:hover {border-color: #5a616d !important; color: #f2f4f7 !important;}
[data-testid="checkbox-group"] label.selected, fieldset label.selected {border-color: var(--hud) !important;
  color: #ffd789 !important; background: rgba(245,158,11,.09) !important; box-shadow: 0 0 10px rgba(245,158,11,.12);}
/* sciezki: rowna siatka 3xN, dioda LED zamiast kwadratu checkboxa */
[data-testid="checkbox-group"] {display: grid !important; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 8px !important;}
[data-testid="checkbox-group"] label {margin: 0 !important; padding: 12px 14px !important; font-size: 12.5px !important;
  letter-spacing: .14em; display: flex !important; align-items: center; gap: 11px; justify-content: flex-start;}
[data-testid="checkbox-group"] label input[type=checkbox] {appearance: none; -webkit-appearance: none;
  width: 9px; height: 9px; min-width: 9px; border-radius: 50%; background: #2e333b; border: none; margin: 0;
  transition: all .15s ease;}
[data-testid="checkbox-group"] label input[type=checkbox]:checked {background: var(--hud); box-shadow: 0 0 9px var(--hud);}
/* pojedyncze checkboxy (opcje) */
label.checkbox-container {font-family: 'IBM Plex Mono', ui-monospace, monospace !important; font-size: 11.5px !important;
  letter-spacing: .1em; text-transform: uppercase; color: #dfe3e9 !important;}
input[type=checkbox], input[type=radio] {accent-color: var(--hud);}
/* konsola statusu */
#console {font-family: 'IBM Plex Mono', ui-monospace, monospace !important; font-size: .82rem !important;
  background: linear-gradient(180deg, #050607, #07080a) !important; color: #fcbf49 !important;
  border: 1px solid #2b2f37 !important; box-shadow: inset 0 0 36px rgba(0,0,0,.75) !important;
  padding: 38px 18px 58px !important; min-height: 330px !important; position: relative; overflow: hidden;}
#console::before {content: "MONITOR"; position: absolute; top: 0; left: 0; right: 0; height: 24px;
  font-size: 9.5px; letter-spacing: .3em; color: #c9cdd6; background: #0b0d11; border-bottom: 1px solid #23262c;
  display: flex; align-items: center; padding-left: 30px;}
#console::after {content: ""; position: absolute; top: 8px; left: 14px; width: 8px; height: 8px; border-radius: 50%;
  background: var(--hud); box-shadow: 0 0 8px var(--hud); animation: pulse 2.2s ease-in-out infinite;}
@keyframes pulse {50% {opacity: .35;}}
#console p {margin: 0 0 7px 0 !important; text-shadow: 0 0 6px rgba(252,191,73,.25);}
#console strong {color: #ffe1a6 !important;}
/* pasek postepu Gradio (status-tracker): zamiast nakladki u gory (wjezdzala na
   belke MONITOR i tekst) — zadokowany na dole konsoli jak linia statusu terminala */
#console > .wrap {position: absolute !important; inset: auto 0 0 0 !important;
  background: #0b0d11 !important; border-top: 1px solid #23262c !important; margin: 0 !important;
  padding: 8px 14px 9px !important; display: flex !important; flex-direction: column-reverse;
  gap: 5px; align-items: stretch; min-height: 0 !important; backdrop-filter: none !important;}
#console > .wrap .progress-text {position: static !important; margin: 0 !important;
  font-family: 'IBM Plex Mono', ui-monospace, monospace !important; font-size: 9.5px !important;
  letter-spacing: .18em; text-transform: uppercase; color: #d4d8df !important; text-align: right;}
#console > .wrap .progress-level {width: 100% !important; margin: 0 !important;}
#console > .wrap .progress-level-inner {font-family: 'IBM Plex Mono', ui-monospace,
  monospace !important; font-size: 9.5px !important; letter-spacing: .18em; color: #fcbf49 !important;
  text-align: left; margin-bottom: 4px;}
#console > .wrap .progress-bar-wrap {background: #15171c !important;
  border: 1px solid #23262c !important; border-radius: 0 !important; height: 8px !important;
  margin: 0 !important; width: 100% !important;}
#console > .wrap .progress-bar {background: linear-gradient(90deg, #d97706, #f59e0b)
  !important; box-shadow: 0 0 10px rgba(245,158,11,.45); height: 100% !important;}
/* przyciski */
button {font-family: 'Chakra Petch', system-ui, sans-serif !important; text-transform: uppercase;
  letter-spacing: .14em; font-weight: 600 !important;}
button.primary {background: linear-gradient(180deg, #f6a722, #d97706) !important; color: #160f02 !important;
  border: 1px solid #b45309 !important; box-shadow: 0 0 18px rgba(245,158,11,.22), 0 1px 0 rgba(255,255,255,.25) inset !important;}
button.primary:hover {filter: brightness(1.08); box-shadow: 0 0 26px rgba(245,158,11,.35) !important;}
button.stop {background: #0c0e12 !important; color: #dfe3e9 !important; border: 1px solid #4a505b !important;}
button.stop:hover {border-color: #b91c1c !important; color: #ef9a9a !important;}
/* scrollbar */
::-webkit-scrollbar {width: 10px; height: 10px;}
::-webkit-scrollbar-thumb {background: #23262c; border: 2px solid #06070a;}
::-webkit-scrollbar-track {background: transparent;}
"""


def _do_update(lang):
    t = TEXT.get(lang, TEXT["en"])
    update.start_update()
    return t["upd_running"]


def build_ui() -> gr.Blocks:
    en = TEXT["en"]
    with gr.Blocks(title="StemSplitter") as demo:
        lang_state = gr.State("en")
        header = gr.Markdown(f"# {en['title']}")

        # baner nowej wersji (widoczny tylko, gdy update_available cos zwroci)
        with gr.Row(visible=False) as upd_row:
            upd_info = gr.Markdown("")
            upd_btn = gr.Button(en["upd_button"], variant="primary")

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

        upd_btn.click(_do_update, [lang_state], [status])

        demo.load(_localize, None,
                  [lang_state, header, file_in, url_in, preset, stems, yt_full,
                   split_vocals, split_drums, btn, stop_btn, out, status,
                   upd_row, upd_info, upd_btn])
    return demo


def main():
    _force_utf8_io()  # zapobiega UnicodeEncodeError na konsoli PL (cp1250)
    _ensure_ffmpeg()  # pobierz/ustaw ffmpeg juz przy starcie
    # allowed_paths: pozwol Gradio serwowac pliki wynikowe z ~/StemSplitter (poza cwd/temp)
    out_dir = str(paths.ensure_data_dirs().base)
    build_ui().launch(inbrowser=True, allowed_paths=[out_dir],
                      theme=gr.themes.Base(primary_hue="amber", neutral_hue="zinc",
                                           radius_size=gr.themes.sizes.radius_none,
                                           font=[gr.themes.Font("system-ui"),
                                                 gr.themes.Font("-apple-system"), "sans-serif"],
                                           font_mono=[gr.themes.Font("ui-monospace"),
                                                      gr.themes.Font("SF Mono"),
                                                      gr.themes.Font("Menlo"),
                                                      gr.themes.Font("Consolas"), "monospace"]),
                      css=_CSS, js=_BOOT_JS)


if __name__ == "__main__":
    main()

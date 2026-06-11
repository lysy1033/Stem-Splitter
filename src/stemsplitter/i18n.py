"""Dwujezyczne teksty UI (EN/PL) + dobor jezyka wg preferencji przegladarki."""

STEM_KEYS = ["wokal", "perkusja", "bas", "gitara", "pianino", "inne"]
PRESET_KEYS = ["normalna", "ultra"]

TEXT = {
    "en": {
        "title": "StemSplitter",
        "accel": "Acceleration",
        "file": "Audio/Video file (MP3 or MP4)",
        "url": "...or paste a YouTube link",
        "url_ph": "https://www.youtube.com/watch?v=...",
        "stems": "Which stems do you want?",
        "quality": "Quality",
        "split_vocals": "Split vocals into lead + backing",
        "split_drums": "Split drums into elements (kick/snare/toms/hi-hat/ride/crash)",
        "run": "Separate",
        "stop": "Stop",
        "stopped": "■ Stopping — finishes the current step, then stops.",
        "result": "Download stems (ZIP)",
        "err_no_input": "Add an MP3/MP4 file or paste a YouTube link first.",
        "err_no_stem": "Select at least one stem.",
        "dl": "▸ Downloading audio from the link...",
        "prep": "▸ Preparing file...",
        "sep_stage": "▸ **Step {n}/{total}: {label}** — running on {accel} (first run downloads the model)",
        "sep_stage_multi": "▸ **Step {n}/{total}: {label}** — the model passes over the track "
                           "{passes} times; the progress bar restarts at each pass ({accel})",
        "pack": "▸ Packing results...",
        "done": "✓ Done — your package is ready to download.",
        "upd_available": "▲ **New version {latest} is available** (you have {current}).",
        "upd_button": "Update now",
        "upd_running": "▸ Updating — an update window just opened. The app will restart "
                       "by itself; refresh this page in a minute or two.",
        "idle": "▸ Idle — waiting for a job.",
        "last_pack": "▸ Last finished package: **{name}** ({time}) — ready to download below.",
        "yt_full": "Also add the full track as MP3 to the package (YouTube links)",
        "missing_stems": "! Could not produce: {stems}.",
        "stage_labels": {
            "htdemucs_6s": "splitting instruments (incl. guitar/piano)",
            "roformer_vocals": "isolating vocals",
            "roformer_karaoke": "vocals → lead + backing",
            "drumsep": "splitting drums into elements",
        },
        "stem_labels": {"wokal": "Vocals", "perkusja": "Drums", "bas": "Bass",
                        "gitara": "Guitar", "pianino": "Piano", "inne": "Other"},
        "presets": {"normalna": "Normal quality (6 stems, 2 passes)",
                    "ultra": "Ultra (best vocals, 8 passes)"},
    },
    "pl": {
        "title": "StemSplitter",
        "accel": "Akceleracja",
        "file": "Plik audio/wideo (MP3 lub MP4)",
        "url": "...albo wklej link YouTube",
        "url_ph": "https://www.youtube.com/watch?v=...",
        "stems": "Które stemy chcesz dostać?",
        "quality": "Jakość",
        "split_vocals": "Rozbij wokal na lead + chórki",
        "split_drums": "Rozbij perkusję na elementy (stopa/werbel/tomy/hi-hat/ride/crash)",
        "run": "Rozdziel",
        "stop": "Stop",
        "stopped": "■ Zatrzymuję — kończę bieżący krok i przerywam.",
        "result": "Pobierz stemy (ZIP)",
        "err_no_input": "Najpierw dodaj plik MP3/MP4 albo wklej link YouTube.",
        "err_no_stem": "Zaznacz przynajmniej jeden stem.",
        "dl": "▸ Pobieram audio z linku...",
        "prep": "▸ Przygotowuję plik...",
        "sep_stage": "▸ **Krok {n}/{total}: {label}** — na {accel} (pierwszy raz pobiera model)",
        "sep_stage_multi": "▸ **Krok {n}/{total}: {label}** — model przejdzie utwór {passes} razy; "
                           "pasek postępu startuje od nowa przy każdym przejściu ({accel})",
        "pack": "▸ Pakuję wyniki...",
        "done": "✓ Gotowe — paczka gotowa do pobrania.",
        "upd_available": "▲ **Dostępna nowa wersja {latest}** (masz {current}).",
        "upd_button": "Aktualizuj",
        "upd_running": "▸ Aktualizuję — właśnie otworzyło się okno aktualizacji. Aplikacja "
                       "uruchomi się ponownie sama; odśwież tę stronę za minutę–dwie.",
        "idle": "▸ Czekam na zadanie.",
        "last_pack": "▸ Ostatnia gotowa paczka: **{name}** ({time}) — do pobrania poniżej.",
        "yt_full": "Dodaj też cały utwór jako MP3 do paczki (linki YouTube)",
        "missing_stems": "! Nie udało się wyprodukować: {stems}.",
        "stage_labels": {
            "htdemucs_6s": "rozdzielanie instrumentów (z gitarą/pianinem)",
            "roformer_vocals": "izolacja wokalu",
            "roformer_karaoke": "wokal → lead + chórki",
            "drumsep": "rozbijanie perkusji na elementy",
        },
        "stem_labels": {"wokal": "Wokal", "perkusja": "Perkusja", "bas": "Bas",
                        "gitara": "Gitara", "pianino": "Pianino", "inne": "Reszta"},
        "presets": {"normalna": "Jakość normalna (6 ścieżek, 2 przejścia)",
                    "ultra": "Ultra (najlepszy wokal, 8 przejść)"},
    },
}


def pick_lang(request) -> str:
    """Zwraca 'pl' jesli przegladarka preferuje polski, inaczej 'en'."""
    accept = ""
    if request is not None:
        accept = (request.headers.get("accept-language", "") or "").lower()
    return "pl" if "pl" in accept else "en"

"""Dwujezyczne teksty UI (EN/PL) + dobor jezyka wg preferencji przegladarki."""

STEM_KEYS = ["wokal", "perkusja", "bas", "gitara", "pianino", "inne"]
PRESET_KEYS = ["szybko", "najlepsza", "maksymalna"]

TEXT = {
    "en": {
        "title": "🎵 StemSplitter",
        "accel": "Acceleration",
        "file": "Audio/Video file (MP3 or MP4)",
        "url": "...or paste a YouTube link",
        "url_ph": "https://www.youtube.com/watch?v=...",
        "stems": "Which stems do you want?",
        "quality": "Quality",
        "split_vocals": "Split vocals into lead + backing",
        "split_drums": "Split drums into elements (kick/snare/cymbals/toms)",
        "run": "Separate",
        "result": "Download stems (ZIP)",
        "err_no_input": "Add an MP3/MP4 file or paste a YouTube link first.",
        "err_no_stem": "Select at least one stem.",
        "dl": "Downloading audio from the link...",
        "prep": "Preparing file...",
        "sep": "Loading models ({accel})... first run downloads them",
        "sep_stage": "Separating — step {n}/{total}: {model} ({accel})",
        "pack": "Packing results...",
        "stem_labels": {"wokal": "🎤 Vocals", "perkusja": "🥁 Drums", "bas": "🎸 Bass",
                        "gitara": "🎸 Guitar", "pianino": "🎹 Piano", "inne": "🎛️ Other"},
        "presets": {"szybko": "Fast", "najlepsza": "Best quality",
                    "maksymalna": "Maximum (cascade)"},
    },
    "pl": {
        "title": "🎵 StemSplitter",
        "accel": "Akceleracja",
        "file": "Plik audio/wideo (MP3 lub MP4)",
        "url": "...albo wklej link YouTube",
        "url_ph": "https://www.youtube.com/watch?v=...",
        "stems": "Które stemy chcesz dostać?",
        "quality": "Jakość",
        "split_vocals": "Rozbij wokal na lead + chórki",
        "split_drums": "Rozbij perkusję na elementy (stopa/werbel/talerze/tomy)",
        "run": "Rozdziel",
        "result": "Pobierz stemy (ZIP)",
        "err_no_input": "Najpierw dodaj plik MP3/MP4 albo wklej link YouTube.",
        "err_no_stem": "Zaznacz przynajmniej jeden stem.",
        "dl": "Pobieram audio z linku...",
        "prep": "Przygotowuję plik...",
        "sep": "Ładuję modele ({accel})... pierwszy raz są pobierane",
        "sep_stage": "Separacja — krok {n}/{total}: {model} ({accel})",
        "pack": "Pakuję wyniki...",
        "stem_labels": {"wokal": "🎤 wokal", "perkusja": "🥁 perkusja", "bas": "🎸 bas",
                        "gitara": "🎸 gitara", "pianino": "🎹 pianino", "inne": "🎛️ reszta"},
        "presets": {"szybko": "Szybko", "najlepsza": "Najlepsza jakość",
                    "maksymalna": "Maksymalna (kaskada)"},
    },
}


def pick_lang(request) -> str:
    """Zwraca 'pl' jesli przegladarka preferuje polski, inaczej 'en'."""
    accept = ""
    if request is not None:
        accept = (request.headers.get("accept-language", "") or "").lower()
    return "pl" if "pl" in accept else "en"

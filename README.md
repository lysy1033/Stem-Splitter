# 🎵 StemSplitter

Simple, free, fully local stem separator for **MP3 and MP4** files (or a **YouTube link**).
Runs on macOS (Apple Silicon), Windows (NVIDIA GPU) and Windows (CPU only).
The browser UI is bilingual (English / Polish) and switches automatically based on your
browser language.

**[English](#english) · [Polski](#polski)**

---

## English

### What it does

Splits a song (MP3), a video's audio track (MP4), or audio from a **YouTube link** into separate
stems — vocals, drums, bass, guitar, piano, other — using the best free open-source AI models
(Demucs, RoFormer). It can optionally split vocals into lead + backing, and drums into
kick/snare/cymbals/toms. While it works it shows which model is running and the progress.

### Requirements

- macOS (Apple Silicon recommended) **or** Windows 10/11.
- ~3–5 GB free disk space (Python env + AI models, downloaded on first use).
- Internet connection on first run (to download models).

Everything heavy (Python environment, models, output files) is stored in `~/.stem-splitter/`,
**outside** any OneDrive-synced folder.

### Before you install (prerequisites)

The installer automatically sets up Python, `ffmpeg` and `yt-dlp` for you. You only need a few
basics in place first:

**macOS**
- **Command Line Tools** (needed so Homebrew/curl work). Install once by running in Terminal:
  ```
  xcode-select --install
  ```
- That's it — the installer brings in Homebrew (if missing), `uv`, Python, `ffmpeg`.

**Windows 10/11**
- **App Installer (winget)** — preinstalled on Windows 10/11. If `winget` is missing, install
  "App Installer" from the Microsoft Store.
- **NVIDIA GPU users:** make sure your normal NVIDIA driver is installed (so `nvidia-smi` works).
  You do **not** need to install CUDA separately — the right build is fetched automatically.
- That's it — the installer brings in `uv`, Python, `ffmpeg`.

**Both systems**
- Get the project files: either download the ZIP from GitHub (green **Code** button →
  **Download ZIP**) and unzip, or, if you use git, `git clone` the repository.

### Installation

1. Download/clone this project to a folder (see prerequisites above).
2. Run the installer for your system — **just double-click it**:
   - **macOS:** `installers/install-mac.command`
     (if macOS blocks it: right-click → Open → Open; or run `bash installers/install-mac.command`)
   - **Windows:** `installers/install-windows.bat`
     (it auto-detects an NVIDIA card and installs the GPU build, otherwise the CPU build)
3. The installer sets up Python (via `uv`), all libraries, `ffmpeg` and `yt-dlp`. Wait until it
   prints **Done**.

### Running

- **macOS:** double-click `installers/run-mac.command`
- **Windows:** double-click `installers/run-windows.bat`

The app opens in your web browser. **The first separation downloads the AI models — this can
take a few minutes. Later runs are fast.**

### How to use

1. Provide input — either **drag & drop an MP3/MP4 file**, or **paste a YouTube link**
   (the audio is downloaded locally first). If both are given, the link wins.
2. Tick the **stems** you want (vocals, drums, bass, guitar, piano, other).
3. Pick a **quality** preset (see below).
4. (Optional) enable **Split vocals into lead + backing** and/or
   **Split drums into elements**.
5. Click **Separate**. When it finishes, download the **ZIP** with your stems.

> YouTube downloading is for your own lawful use only; respect copyright and YouTube's Terms.

### Quality presets

- **Fast** — `htdemucs`, 4 stems. Quickest.
- **Best quality** — `htdemucs_ft` (fine-tuned). Cleaner, a bit slower.
- **Maximum (cascade)** — RoFormer isolates clean vocals first, then `htdemucs_6s` runs on the
  vocal-free instrumental → noticeably better **guitar** and other instruments. Slowest.

### Notes on quality

Vocals, bass and drums separate best. Guitar, piano, backing vocals and individual drum
elements are inherently harder — results are good but not studio-perfect.

### Swapping / adding models (advanced)

Models and presets are declared in YAML, no code changes needed:
- `config/models.yaml` — the model registry (id → model file).
- `config/pipelines.yaml` — presets and optional extensions, defined as pipeline stages.

### Troubleshooting

- **"ffmpeg not found"** — re-run the installer; it installs ffmpeg.
- **First run seems frozen** — it's downloading models; watch the progress text.
- **Slow on Windows CPU** — expected; a separation can take several minutes without a GPU.

---

## Polski

### Co to robi

Rozdziela utwór (MP3), ścieżkę dźwiękową z wideo (MP4) albo audio z **linku YouTube** na osobne
stemy — wokal, perkusja, bas, gitara, pianino, reszta — przy użyciu najlepszych darmowych modeli
open source (Demucs, RoFormer). Opcjonalnie potrafi rozbić wokal na lead + chórki, a perkusję na
stopę/werbel/talerze/tomy. W trakcie pracy pokazuje, który model działa, oraz postęp.

### Wymagania

- macOS (najlepiej Apple Silicon) **lub** Windows 10/11.
- ~3–5 GB wolnego miejsca (środowisko Pythona + modele AI pobierane przy pierwszym użyciu).
- Internet przy pierwszym uruchomieniu (do pobrania modeli).

Wszystko ciężkie (środowisko Pythona, modele, pliki wynikowe) trafia do `~/.stem-splitter/`,
**poza** folderem synchronizowanym przez OneDrive.

### Zanim zainstalujesz (wymagania wstępne)

Instalator automatycznie stawia Pythona, `ffmpeg` i `yt-dlp`. Wcześniej potrzebujesz tylko kilku
podstaw:

**macOS**
- **Command Line Tools** (potrzebne, by działał Homebrew/curl). Zainstaluj raz w Terminalu:
  ```
  xcode-select --install
  ```
- To wszystko — instalator dociągnie Homebrew (jeśli go nie ma), `uv`, Pythona, `ffmpeg`.

**Windows 10/11**
- **App Installer (winget)** — wbudowany w Windows 10/11. Jeśli `winget` nie działa, zainstaluj
  „App Installer" ze sklepu Microsoft Store.
- **Karty NVIDIA:** upewnij się, że masz zainstalowany zwykły sterownik NVIDIA (żeby działało
  `nvidia-smi`). **Nie** musisz osobno instalować CUDA — właściwa wersja pobierze się sama.
- To wszystko — instalator dociągnie `uv`, Pythona, `ffmpeg`.

**Oba systemy**
- Pobierz pliki projektu: albo ZIP z GitHuba (zielony przycisk **Code** → **Download ZIP**)
  i rozpakuj, albo `git clone`, jeśli używasz gita.

### Instalacja

1. Pobierz/sklonuj ten projekt do folderu (patrz wymagania wstępne wyżej).
2. Uruchom instalator dla swojego systemu — **wystarczy dwuklik**:
   - **macOS:** `installers/install-mac.command`
     (jeśli macOS zablokuje: prawy przycisk → Otwórz → Otwórz; albo `bash installers/install-mac.command`)
   - **Windows:** `installers/install-windows.bat`
     (sam wykrywa kartę NVIDIA i instaluje wersję GPU, w przeciwnym razie wersję CPU)
3. Instalator stawia Pythona (przez `uv`), wszystkie biblioteki, `ffmpeg` i `yt-dlp`. Poczekaj aż
   wypisze **Gotowe**.

### Uruchamianie

- **macOS:** dwuklik `installers/run-mac.command`
- **Windows:** dwuklik `installers/run-windows.bat`

Aplikacja otworzy się w przeglądarce. **Pierwsza separacja pobiera modele AI — to może potrwać
kilka minut. Kolejne są szybkie.**

### Jak używać

1. Podaj wejście — albo **przeciągnij i upuść plik MP3/MP4**, albo **wklej link YouTube**
   (audio zostanie najpierw pobrane lokalnie). Jeśli podasz oba, wygrywa link.
2. Zaznacz **stemy**, które chcesz dostać (wokal, perkusja, bas, gitara, pianino, reszta).
3. Wybierz **preset jakości** (poniżej).
4. (Opcjonalnie) włącz **Rozbij wokal na lead + chórki** i/lub
   **Rozbij perkusję na elementy**.
5. Kliknij **Rozdziel**. Po zakończeniu pobierz **ZIP** ze stemami.

> Pobieranie z YouTube wyłącznie do własnego, legalnego użytku; szanuj prawa autorskie i regulamin YouTube.

### Presety jakości

- **Szybko** — `htdemucs`, 4 stemy. Najszybszy.
- **Najlepsza jakość** — `htdemucs_ft` (fine-tuned). Czystszy, trochę wolniejszy.
- **Maksymalna (kaskada)** — najpierw RoFormer wyciąga czysty wokal, potem `htdemucs_6s`
  działa na instrumentalu bez wokalu → wyraźnie lepsza **gitara** i inne instrumenty. Najwolniejszy.

### Uwagi o jakości

Najlepiej wychodzą wokal, bas i perkusja. Gitara, pianino, chórki i pojedyncze elementy
perkusji są trudniejsze — wyniki są dobre, ale nie idealne studyjnie.

### Wymiana / dodawanie modeli (zaawansowane)

Modele i presety opisane są w YAML, bez zmian w kodzie:
- `config/models.yaml` — rejestr modeli (id → plik modelu).
- `config/pipelines.yaml` — presety i opcjonalne rozszerzenia jako etapy pipeline.

### Rozwiązywanie problemów

- **„ffmpeg not found"** — uruchom instalator ponownie; instaluje ffmpeg.
- **Pierwsze uruchomienie wygląda na zawieszone** — pobiera modele; patrz na tekst postępu.
- **Wolno na Windows CPU** — to normalne; separacja bez GPU może trwać kilka minut.

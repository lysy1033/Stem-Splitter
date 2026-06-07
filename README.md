# 🎵 StemSplitter

Split any song into separate tracks (vocals, drums, bass, guitar, piano…) on your own computer —
**for free**. Works with **MP3 / MP4 files or a YouTube link**. The app opens in your web browser
and speaks **English and Polish** (it picks your language automatically).

**[English](#english) · [Polski](#polski)**

---

## English

### What you get

Drop in a song and get back separate audio files — vocals, drums, bass, guitar, piano, and the
rest — neatly zipped. Optionally split vocals into lead + backing, or drums into
kick/snare/toms/hi-hat/ride/crash. You pick the quality; the app shows what it's doing and how far
along it is.

### Get started — macOS (3 steps)

1. **Download the app.** On the project's GitHub page click the green **Code** button →
   **Download ZIP**. Double-click the downloaded ZIP to unzip it. Open the unzipped folder.
2. **Open the `installers` folder and double-click `install-mac.command`.**

   The first time, macOS will probably block it (it's not from the App Store). If you only see
   **"Move to Trash" / "Done"** and no way to open it, use **one** of these (just once):

   - **Easiest — no Terminal:** in the warning click **Done**. Open
     **System Settings → Privacy & Security**, scroll down to the line
     *"install-mac.command was blocked…"* and click **Open Anyway**, then confirm with **Open**
     and your password / Touch ID. Double-click the file again if needed.
   - **Always works — Terminal:** open the **Terminal** app (Spotlight → type *Terminal*),
     type `bash` followed by a space, then **drag the `install-mac.command` file into the Terminal
     window** and press **Enter**.

   *(The old "right-click → Open" trick no longer shows an Open button on recent macOS — use one
   of the two methods above.)*
3. **Wait.** A black window shows the progress. When it's done, **StemSplitter opens in your web
   browser by itself.** First time only, it downloads the AI brains — that's the longest part.

Next time, just double-click **`run-mac.command`** to start it again.

### Get started — Windows (3 steps)

1. **Download the app.** On the project's GitHub page click the green **Code** button →
   **Download ZIP**. Right-click the ZIP → **Extract All**. Open the extracted folder.
2. **Open the `installers` folder and double-click `install-windows.bat`.**
   - If a blue "Windows protected your PC" box appears, click **More info** → **Run anyway**.
   - It automatically uses your **NVIDIA** graphics card if you have one (faster), otherwise it
     runs on the processor.
3. **Wait.** A black window shows the progress. When it's done, **StemSplitter opens in your web
   browser by itself.** First time only, it downloads the AI brains — that's the longest part.

Next time, just double-click **`run-windows.bat`** to start it again.

> The installer sets up everything it needs by itself (no separate downloads to chase).
> It needs an internet connection and about 3–5 GB of free disk space.

### Where are my files?

Everything the app makes — and your separated tracks — goes into a plain, visible folder called
**`StemSplitter`** in your home/user folder (e.g. `/Users/yourname/StemSplitter` on Mac,
`C:\Users\yourname\StemSplitter` on Windows). Your finished stems are in the `output` subfolder.
Nothing is hidden, and nothing is put in your OneDrive.

### How to use it

1. **Give it a song** — either drag in an **MP3/MP4 file**, or **paste a YouTube link**.
2. **Tick the tracks** you want (vocals, drums, bass, guitar, piano, other).
3. **Choose quality** (see below).
4. *(Optional)* turn on **split vocals into lead + backing** and/or **split drums into elements**.
5. Click **Separate**, wait, then **download the ZIP** with your tracks.

> Only download from YouTube for your own lawful use; respect copyright and YouTube's Terms.

### Quality options

- **Fast** — quick, 4 tracks (vocals/drums/bass/other).
- **Best quality** — cleaner, a little slower (recommended for most songs).
- **Maximum** — does two passes so **guitar and other instruments come out clearer**. Slowest.

### Good to know about quality

Vocals, bass and drums come out best. Guitar, piano, backing vocals and individual drum pieces are
harder for any AI — results are good, but not studio-perfect.

### If something goes wrong

- **macOS only offers "Move to Trash" / "Done"** — that's the security block; follow the two
  methods in step 2 above (System Settings → Privacy & Security → **Open Anyway**, or run it from
  Terminal with `bash` + dragging the file).
- **The black window closed instantly / nothing happened** — on Windows: More info → Run anyway.
- **It looks stuck on the first run** — it's downloading the AI models; watch the progress text,
  it will continue.
- **No NVIDIA graphics card on Windows** — that's fine, it still works, just slower (a song can
  take a few minutes).

### For advanced users — swapping models

Models and the quality presets are plain text files; change them without touching code:
`config/models.yaml` (which model) and `config/pipelines.yaml` (the steps each preset runs).

---

## Polski

### Co dostajesz

Wrzucasz utwór i dostajesz osobne pliki audio — wokal, perkusja, bas, gitara, pianino i reszta —
spakowane w ZIP. Opcjonalnie wokal na lead + chórki, a perkusję na
stopę/werbel/tomy/hi-hat/ride/crash. Wybierasz jakość; aplikacja pokazuje, co robi i ile zostało.

### Zacznij — macOS (3 kroki)

1. **Pobierz aplikację.** Na stronie projektu na GitHubie kliknij zielony przycisk **Code** →
   **Download ZIP**. Kliknij dwukrotnie pobrany ZIP, żeby go rozpakować. Otwórz rozpakowany folder.
2. **Wejdź do folderu `installers` i kliknij dwukrotnie `install-mac.command`.**

   Za pierwszym razem macOS prawdopodobnie to zablokuje (plik nie jest ze sklepu App Store).
   Jeśli widzisz tylko **„Przenieś do Kosza" / „Gotowe"** i nie da się otworzyć, użyj **jednej**
   z poniższych metod (tylko raz):

   - **Najprościej — bez Terminala:** w ostrzeżeniu kliknij **Gotowe**. Otwórz
     **Ustawienia systemowe → Prywatność i bezpieczeństwo**, zjedź na dół do napisu
     *„Plik install-mac.command został zablokowany…"* i kliknij **Otwórz mimo to**, potem
     potwierdź **Otwórz** hasłem / Touch ID. W razie potrzeby kliknij plik dwukrotnie jeszcze raz.
   - **Zawsze działa — Terminal:** otwórz program **Terminal** (Spotlight → wpisz *Terminal*),
     wpisz `bash` i spację, a następnie **przeciągnij plik `install-mac.command` na okno Terminala**
     i naciśnij **Enter**.

   *(Dawna sztuczka „prawy klik → Otwórz" na nowszym macOS nie pokazuje już przycisku Otwórz —
   użyj jednej z dwóch metod powyżej.)*
3. **Poczekaj.** Czarne okno pokazuje postęp. Po zakończeniu **StemSplitter sam otworzy się w
   przeglądarce.** Tylko za pierwszym razem pobiera „mózgi" AI — to najdłuższy etap.

Następnym razem po prostu kliknij dwukrotnie **`run-mac.command`**.

### Zacznij — Windows (3 kroki)

1. **Pobierz aplikację.** Na stronie projektu na GitHubie kliknij zielony przycisk **Code** →
   **Download ZIP**. Kliknij ZIP prawym przyciskiem → **Wyodrębnij wszystko**. Otwórz folder.
2. **Wejdź do folderu `installers` i kliknij dwukrotnie `install-windows.bat`.**
   - Jeśli pojawi się niebieskie okno „System Windows ochronił Twój komputer", kliknij
     **Więcej informacji** → **Uruchom mimo to**.
   - Automatycznie użyje karty **NVIDIA**, jeśli ją masz (szybciej), w przeciwnym razie procesora.
3. **Poczekaj.** Czarne okno pokazuje postęp. Po zakończeniu **StemSplitter sam otworzy się w
   przeglądarce.** Tylko za pierwszym razem pobiera „mózgi" AI — to najdłuższy etap.

Następnym razem po prostu kliknij dwukrotnie **`run-windows.bat`**.

> Instalator sam ustawia wszystko, czego potrzebuje (nie musisz nic dodatkowo szukać i pobierać).
> Potrzebny jest internet i około 3–5 GB wolnego miejsca na dysku.

### Gdzie są moje pliki?

Wszystko, co tworzy aplikacja — i Twoje rozdzielone ścieżki — trafia do zwykłego, **widocznego**
folderu **`StemSplitter`** w Twoim katalogu domowym (np. `/Users/twojeimie/StemSplitter` na Macu,
`C:\Users\twojeimie\StemSplitter` na Windows). Gotowe stemy są w podfolderze `output`. Nic nie jest
ukryte i nic nie ląduje w OneDrive.

### Jak używać

1. **Podaj utwór** — przeciągnij **plik MP3/MP4** albo **wklej link YouTube**.
2. **Zaznacz ścieżki**, które chcesz (wokal, perkusja, bas, gitara, pianino, reszta).
3. **Wybierz jakość** (poniżej).
4. *(Opcjonalnie)* włącz **rozbij wokal na lead + chórki** i/lub **rozbij perkusję na elementy**.
5. Kliknij **Rozdziel**, poczekaj i **pobierz ZIP** ze ścieżkami.

> Pobieraj z YouTube tylko do własnego, legalnego użytku; szanuj prawa autorskie i regulamin YouTube.

### Opcje jakości

- **Szybko** — szybkie, 4 ścieżki (wokal/perkusja/bas/reszta).
- **Najlepsza jakość** — czystsze, trochę wolniejsze (polecane do większości utworów).
- **Maksymalna** — robi dwa przejścia, dzięki czemu **gitara i inne instrumenty wychodzą czyściej**.
  Najwolniejsze.

### Warto wiedzieć o jakości

Najlepiej wychodzą wokal, bas i perkusja. Gitara, pianino, chórki i pojedyncze elementy perkusji są
trudniejsze dla każdego AI — wyniki są dobre, ale nie idealne studyjnie.

### Gdy coś nie działa

- **macOS daje tylko „Przenieś do Kosza" / „Gotowe"** — to blokada bezpieczeństwa; użyj dwóch
  metod z kroku 2 powyżej (Ustawienia systemowe → Prywatność i bezpieczeństwo → **Otwórz mimo to**,
  albo uruchom z Terminala: `bash` + przeciągnięcie pliku).
- **Czarne okno zamknęło się od razu / nic się nie stało** — na Windows: Więcej informacji →
  Uruchom mimo to.
- **Wygląda, jakby się zawiesiło przy pierwszym razie** — pobiera modele AI; popatrz na tekst
  postępu, za chwilę ruszy dalej.
- **Brak karty NVIDIA na Windows** — to nic, też działa, tylko wolniej (utwór może zająć kilka minut).

### Dla zaawansowanych — wymiana modeli

Modele i presety jakości to zwykłe pliki tekstowe; zmieniasz je bez ruszania kodu:
`config/models.yaml` (jaki model) i `config/pipelines.yaml` (kroki każdego presetu).

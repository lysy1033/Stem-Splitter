import re
from pathlib import Path

from . import paths, registry
from .pipeline import Pipeline, Stage

_STEM_RE = re.compile(r"\(([^)]+)\)")


def _parse_stem_name(filename: str) -> str | None:
    # audio-separator dokleja stem na koncu: input_(Stem)_model.wav.
    # W kaskadzie nazwa wejscia juz zawiera nawias (np. (Instrumental)),
    # wiec stem tego etapu to OSTATNIA grupa w nawiasie, nie pierwsza.
    matches = _STEM_RE.findall(Path(filename).name)
    return matches[-1] if matches else None


def _onnx_providers() -> list[str]:
    try:
        import onnxruntime as ort
        return list(ort.get_available_providers())
    except Exception:
        return []


def _torch_device() -> str | None:
    """Zwraca 'cuda'/'mps' jesli PyTorch widzi akcelerator, inaczej None.
    Modele Roformer/MDXC licza przez PyTorch, wiec to ono (a nie onnxruntime)
    decyduje o realnym uzyciu GPU dla tych modeli."""
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        mps = getattr(torch.backends, "mps", None)
        if mps is not None and mps.is_available():
            return "mps"
    except Exception:
        pass
    return None


def detect_acceleration() -> str:
    # Najpierw PyTorch (modele Roformer/MDXC), potem onnxruntime jako fallback.
    device = _torch_device()
    if device == "cuda":
        return "CUDA (NVIDIA GPU)"
    if device == "mps":
        return "MPS (Apple Silicon)"
    providers = _onnx_providers()
    if "CUDAExecutionProvider" in providers:
        return "CUDA (NVIDIA GPU)"
    if "CoreMLExecutionProvider" in providers:
        return "CoreML (Apple Silicon)"
    return "CPU"


def _load_separator(model_file: str, output_dir: str, shifts: int = 0):
    """Tworzy Separator i wczytuje model (pobiera go, jesli go nie ma)."""
    from audio_separator.separator import Separator

    separator = Separator(output_dir=str(output_dir),
                          model_file_dir=str(paths.ensure_data_dirs().models),
                          demucs_params={"segment_size": "Default", "shifts": shifts,
                                         "overlap": 0.25, "segments_enabled": True})
    separator.load_model(model_filename=model_file)
    return separator


def _purge_model_files(model_file: str) -> list[str]:
    """Kasuje (potencjalnie uszkodzony) plik modelu i pliki towarzyszace
    (np. .yaml) o tej samej nazwie, by audio-separator pobral je od nowa."""
    models_dir = paths.ensure_data_dirs().models
    stem = Path(model_file).stem
    removed: list[str] = []
    for f in models_dir.glob(f"{stem}.*"):
        try:
            f.unlink()
            removed.append(f.name)
        except OSError:
            pass
    return removed


def _separate_with_model(model_file: str, input_path: str, output_dir: str,
                         shifts: int = 0) -> dict[str, str]:
    """Realne wywolanie audio-separator. Zwraca {nazwa_stemu_z_separatora: sciezka}.

    Przerwane pobieranie zostawia czesciowy plik modelu, a audio-separator
    sprawdza tylko jego OBECNOSC (nie integralnosc) -> przy nastepnym starcie
    wczytanie uszkodzonego .ckpt pada. mdxc_separator sygnalizuje to wewnetrznym
    sys.exit(1) (-> SystemExit); inne architektury moga rzucic RuntimeError.
    Wtedy kasujemy plik(i) modelu i ponawiamy raz, wymuszajac czyste pobranie."""
    try:
        separator = _load_separator(model_file, output_dir, shifts)
    except (SystemExit, RuntimeError):
        removed = _purge_model_files(model_file)
        if not removed:
            raise  # nie bylo czego skasowac -> to nie problem z plikiem modelu
        print(f"StemSplitter: uszkodzony model ({model_file}) usuniety, "
              f"pobieram od nowa / corrupt model removed, re-downloading...")
        separator = _load_separator(model_file, output_dir, shifts)  # czyste pobranie; blad propaguje
    files = separator.separate(str(input_path))
    out: dict[str, str] = {}
    for f in files:
        stem = _parse_stem_name(f)
        if stem:
            out[stem] = str(Path(output_dir) / Path(f).name)
    return out


def run_pipeline_steps(input_path, pipe: Pipeline, requested_stems: list[str], output_dir):
    """Generator wykonujacy pipeline etap po etapie.

    Przed kazdym etapem oddaje ('stage', done, total, model_id), a na koncu
    ('result', {stem: sciezka}). Pozwala UI pokazywac, na ktorym etapie jestesmy.
    """
    reg = registry.load_registry()
    output_dir = Path(output_dir)
    # mapa: nazwa_kanoniczna -> sciezka pliku
    produced: dict[str, str] = {"mix": str(input_path)}

    total = len(pipe.stages)
    for i, stage in enumerate(pipe.stages):
        spec = reg[stage.model_id]
        # demucs: kazdy pod-model leci max(shifts,1) razy; inne architektury ignoruja shifts
        runs = spec.passes * max(stage.shifts, 1) if spec.architecture == "demucs" else spec.passes
        yield ("stage", i, total, stage.model_id, runs)
        stage_input = produced.get(stage.input)
        if stage_input is None:
            raise ValueError(f"Etap wymaga wejscia '{stage.input}', ktorego brak")
        raw = _separate_with_model(spec.file, stage_input, str(output_dir), shifts=stage.shifts)
        for sep_name, canonical in stage.outputs.items():
            if sep_name in raw:
                produced[canonical] = raw[sep_name]

    yield ("result", {stem: produced[stem] for stem in requested_stems if stem in produced})


def run_pipeline(input_path, pipe: Pipeline, requested_stems: list[str],
                 output_dir, progress_cb=None) -> dict[str, str]:
    """Cienka nakladka na run_pipeline_steps (zachowuje stare API i progress_cb)."""
    result: dict[str, str] = {}
    for event in run_pipeline_steps(input_path, pipe, requested_stems, output_dir):
        if event[0] == "stage":
            if progress_cb is not None:
                progress_cb(event[1], event[2], event[3])
        elif event[0] == "result":
            result = event[1]
    return result

import re
from pathlib import Path

from . import paths, registry
from .pipeline import Pipeline, Stage

_STEM_RE = re.compile(r"\(([^)]+)\)")


def _parse_stem_name(filename: str) -> str | None:
    matches = _STEM_RE.findall(Path(filename).name)
    return matches[0] if matches else None


def _onnx_providers() -> list[str]:
    try:
        import onnxruntime as ort
        return list(ort.get_available_providers())
    except Exception:
        return []


def detect_acceleration() -> str:
    providers = _onnx_providers()
    if "CUDAExecutionProvider" in providers:
        return "CUDA (NVIDIA GPU)"
    if "CoreMLExecutionProvider" in providers:
        return "CoreML (Apple Silicon)"
    return "CPU"


def _separate_with_model(model_file: str, input_path: str, output_dir: str) -> dict[str, str]:
    """Realne wywolanie audio-separator. Zwraca {nazwa_stemu_z_separatora: sciezka}."""
    from audio_separator.separator import Separator

    separator = Separator(output_dir=str(output_dir),
                          model_file_dir=str(paths.ensure_data_dirs().models))
    separator.load_model(model_filename=model_file)
    files = separator.separate(str(input_path))
    out: dict[str, str] = {}
    for f in files:
        stem = _parse_stem_name(f)
        if stem:
            out[stem] = str(Path(output_dir) / Path(f).name)
    return out


def run_pipeline(input_path, pipe: Pipeline, requested_stems: list[str],
                 output_dir) -> dict[str, str]:
    reg = registry.load_registry()
    output_dir = Path(output_dir)
    # mapa: nazwa_kanoniczna -> sciezka pliku
    produced: dict[str, str] = {"mix": str(input_path)}

    for stage in pipe.stages:
        stage_input = produced.get(stage.input)
        if stage_input is None:
            raise ValueError(f"Etap wymaga wejscia '{stage.input}', ktorego brak")
        model_file = reg[stage.model_id].file
        raw = _separate_with_model(model_file, stage_input, str(output_dir))
        for sep_name, canonical in stage.outputs.items():
            if sep_name in raw:
                produced[canonical] = raw[sep_name]

    return {stem: produced[stem] for stem in requested_stems if stem in produced}

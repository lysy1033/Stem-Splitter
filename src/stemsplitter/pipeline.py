from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Stage:
    input: str          # "mix" lub nazwa stemu kanonicznego
    model_id: str
    outputs: dict[str, str]   # nazwa_z_separatora -> nazwa_kanoniczna
    shifts: int = 0     # demucs: ile razy kazdy pod-model przelatuje utwor (0 = raz)


@dataclass(frozen=True)
class Pipeline:
    name: str
    stages: list[Stage]


def _default_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "pipelines.yaml"


def _load_yaml(path: Path | None) -> dict:
    path = path or _default_path()
    return yaml.safe_load(path.read_text()) or {}


def _stage_from_dict(d: dict) -> Stage:
    return Stage(input=d["input"], model_id=d["model"], outputs=dict(d["outputs"]),
                 shifts=int(d.get("shifts", 0)))


def _produced_stems(stages: list[Stage]) -> set[str]:
    produced: set[str] = set()
    for s in stages:
        produced.update(s.outputs.values())
    return produced


def _validate_extension_requirement(ext_name: str, produced: set[str], path: Path | None = None) -> None:
    data = _load_yaml(path)
    ext = (data.get("extensions") or {}).get(ext_name)
    if ext is None:
        raise ValueError(f"Nieznane rozszerzenie: {ext_name}")
    required = ext["requires"]
    if required not in produced:
        raise ValueError(
            f"Rozszerzenie '{ext_name}' wymaga stemu '{required}', ktory nie jest produkowany przez ten preset"
        )


def load_preset(name: str, extensions: list[str] | None = None, path: Path | None = None) -> Pipeline:
    data = _load_yaml(path)
    presets = data.get("presets") or {}
    if name not in presets:
        raise ValueError(f"Nieznany preset: {name}")
    stages = [_stage_from_dict(s) for s in presets[name]["stages"]]

    for ext_name in extensions or []:
        _validate_extension_requirement(ext_name, _produced_stems(stages), path)
        ext = data["extensions"][ext_name]
        stages.append(_stage_from_dict(ext["stage"]))

    return Pipeline(name=name, stages=stages)

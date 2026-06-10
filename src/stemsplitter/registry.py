from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class ModelSpec:
    id: str
    file: str
    architecture: str
    role: str
    passes: int = 1   # ile pod-modeli liczy jeden przebieg (pakiet htdemucs_ft = 4)


def _default_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "models.yaml"


def load_registry(path: Path | None = None) -> dict[str, ModelSpec]:
    path = path or _default_path()
    data = yaml.safe_load(path.read_text()) or {}
    models = data.get("models") or {}
    result: dict[str, ModelSpec] = {}
    for model_id, spec in models.items():
        if "file" not in spec or "architecture" not in spec:
            raise ValueError(f"Model '{model_id}' wymaga pol 'file' i 'architecture'")
        result[model_id] = ModelSpec(
            id=model_id,
            file=spec["file"],
            architecture=spec["architecture"],
            role=spec.get("role", ""),
            passes=int(spec.get("passes", 1)),
        )
    return result

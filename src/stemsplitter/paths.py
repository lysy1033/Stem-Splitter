from dataclasses import dataclass
from pathlib import Path


def _base_dir() -> Path:
    return Path.home() / ".stem-splitter"


@dataclass(frozen=True)
class DataDirs:
    base: Path
    models: Path
    output: Path
    work: Path


def ensure_data_dirs() -> DataDirs:
    base = _base_dir()
    models = base / "models"
    output = base / "output"
    work = base / "work"
    for d in (models, output, work):
        d.mkdir(parents=True, exist_ok=True)
    return DataDirs(base=base, models=models, output=output, work=work)

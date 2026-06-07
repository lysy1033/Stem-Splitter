from pathlib import Path
from stemsplitter import paths


def test_data_dirs_live_outside_project(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "_base_dir", lambda: tmp_path / "StemSplitter")
    dirs = paths.ensure_data_dirs()
    assert dirs.models.exists()
    assert dirs.output.exists()
    assert dirs.work.exists()
    # wszystkie pod wspolnym katalogiem bazowym
    assert dirs.models.parent == tmp_path / "StemSplitter"


def test_default_base_is_visible_home_dir():
    base = paths._base_dir()
    assert base == Path.home() / "StemSplitter"
    # folder NIE moze byc ukryty (bez kropki na poczatku)
    assert not base.name.startswith(".")

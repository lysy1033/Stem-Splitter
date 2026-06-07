from pathlib import Path
from stemsplitter import paths


def test_data_dirs_live_outside_project(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "_base_dir", lambda: tmp_path / ".stem-splitter")
    dirs = paths.ensure_data_dirs()
    assert dirs.models.exists()
    assert dirs.output.exists()
    assert dirs.work.exists()
    # wszystkie pod wspolnym katalogiem bazowym
    assert dirs.models.parent == tmp_path / ".stem-splitter"


def test_default_base_is_home_dot_dir():
    assert paths._base_dir() == Path.home() / ".stem-splitter"

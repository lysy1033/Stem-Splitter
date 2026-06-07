import pytest
from stemsplitter import registry


def test_load_registry_returns_known_models():
    reg = registry.load_registry()
    assert "htdemucs" in reg
    assert reg["htdemucs"].file == "htdemucs.yaml"
    assert reg["roformer_vocals"].architecture == "roformer"


def test_load_registry_from_explicit_path(tmp_path):
    p = tmp_path / "m.yaml"
    p.write_text(
        "models:\n  x:\n    file: x.ckpt\n    architecture: roformer\n    role: test\n"
    )
    reg = registry.load_registry(p)
    assert reg["x"].file == "x.ckpt"


def test_missing_required_field_raises(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("models:\n  x:\n    architecture: roformer\n")
    with pytest.raises(ValueError):
        registry.load_registry(p)

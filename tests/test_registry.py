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


def test_passes_defaults_to_one(tmp_path):
    p = tmp_path / "m.yaml"
    p.write_text(
        "models:\n  x:\n    file: x.ckpt\n    architecture: roformer\n    role: test\n"
    )
    assert registry.load_registry(p)["x"].passes == 1


def test_passes_read_from_yaml(tmp_path):
    p = tmp_path / "m.yaml"
    p.write_text(
        "models:\n  x:\n    file: x.yaml\n    architecture: demucs\n    role: test\n    passes: 4\n"
    )
    assert registry.load_registry(p)["x"].passes == 4


def test_real_registry_knows_bag_models():
    reg = registry.load_registry()
    # htdemucs_ft to pakiet 4 pod-modeli; pojedyncze modele maja 1
    assert reg["htdemucs_ft"].passes == 4
    assert reg["htdemucs_6s"].passes == 1

from pathlib import Path
from stemsplitter import engine, pipeline, registry


def test_parse_stem_name_from_filename():
    assert engine._parse_stem_name("song_(Vocals)_htdemucs.wav") == "Vocals"
    assert engine._parse_stem_name("song_(Backing Vocals)_mel.wav") == "Backing Vocals"
    assert engine._parse_stem_name("noparen.wav") is None


def test_detect_acceleration_cuda(monkeypatch):
    monkeypatch.setattr(engine, "_onnx_providers", lambda: ["CUDAExecutionProvider"])
    assert "CUDA" in engine.detect_acceleration()


def test_detect_acceleration_coreml(monkeypatch):
    monkeypatch.setattr(engine, "_onnx_providers", lambda: ["CoreMLExecutionProvider"])
    assert "CoreML" in engine.detect_acceleration()


def test_detect_acceleration_cpu(monkeypatch):
    monkeypatch.setattr(engine, "_onnx_providers", lambda: [])
    assert engine.detect_acceleration() == "CPU"


def test_run_pipeline_chains_stages_and_filters(monkeypatch, tmp_path):
    # Mock: separator dla danego modelu zwraca z gory ustalone stemy.
    fake_outputs = {
        "roformer_vocals": {"Vocals": "v.wav", "Instrumental": "inst.wav"},
        "htdemucs_6s": {
            "Bass": "b.wav", "Drums": "d.wav", "Guitar": "g.wav",
            "Piano": "p.wav", "Other": "o.wav",
        },
    }

    seen_inputs: dict[str, str] = {}

    def fake_separate(model_file, input_path, output_dir):
        # zmapuj id modelu z pliku przez rejestr (odwrotnie) — uproszczone: po pliku
        reg = registry.load_registry()
        model_id = next(m.id for m in reg.values() if m.file == model_file)
        seen_inputs[model_id] = input_path
        return {stem: str(Path(output_dir) / name)
                for stem, name in fake_outputs[model_id].items()}

    monkeypatch.setattr(engine, "_separate_with_model", fake_separate)

    p = pipeline.load_preset("maksymalna")
    result = engine.run_pipeline(
        input_path=tmp_path / "song.wav",
        pipe=p,
        requested_stems=["wokal", "gitara"],
        output_dir=tmp_path,
    )
    # tylko zadane stemy w wyniku
    assert set(result.keys()) == {"wokal", "gitara"}
    assert result["gitara"].endswith("g.wav")

    # etap 1 otrzymuje oryginalny miks
    assert seen_inputs["roformer_vocals"] == str(tmp_path / "song.wav")
    # etap 2 otrzymuje instrumental wyprodukowany przez etap 1, nie oryginalny miks
    assert seen_inputs["htdemucs_6s"] == str(Path(tmp_path) / "inst.wav")

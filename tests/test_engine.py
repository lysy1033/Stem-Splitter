from pathlib import Path
from stemsplitter import engine, pipeline, registry


def test_parse_stem_name_from_filename():
    assert engine._parse_stem_name("song_(Vocals)_htdemucs.wav") == "Vocals"
    assert engine._parse_stem_name("song_(Backing Vocals)_mel.wav") == "Backing Vocals"
    assert engine._parse_stem_name("noparen.wav") is None


def test_parse_stem_name_cascade_takes_last_group():
    # W kaskadzie wejscie etapu 2 juz zawiera nawias (np. (Instrumental));
    # stem tego etapu to OSTATNIA grupa, nie pierwsza.
    name = "song_(Instrumental)_bsroformer_(Bass)_htdemucs.wav"
    assert engine._parse_stem_name(name) == "Bass"
    name2 = "clip_(Vocals)_bsroformer_(Vocals)_mel_band_roformer_karaoke.wav"
    assert engine._parse_stem_name(name2) == "Vocals"


def test_detect_acceleration_torch_cuda(monkeypatch):
    monkeypatch.setattr(engine, "_torch_device", lambda: "cuda")
    assert "CUDA" in engine.detect_acceleration()


def test_detect_acceleration_torch_mps(monkeypatch):
    monkeypatch.setattr(engine, "_torch_device", lambda: "mps")
    assert "MPS" in engine.detect_acceleration()


def test_detect_acceleration_onnx_cuda_fallback(monkeypatch):
    # Bez akceleratora torch, ale onnxruntime ma providera CUDA.
    monkeypatch.setattr(engine, "_torch_device", lambda: None)
    monkeypatch.setattr(engine, "_onnx_providers", lambda: ["CUDAExecutionProvider"])
    assert "CUDA" in engine.detect_acceleration()


def test_detect_acceleration_onnx_coreml_fallback(monkeypatch):
    monkeypatch.setattr(engine, "_torch_device", lambda: None)
    monkeypatch.setattr(engine, "_onnx_providers", lambda: ["CoreMLExecutionProvider"])
    assert "CoreML" in engine.detect_acceleration()


def test_detect_acceleration_cpu(monkeypatch):
    monkeypatch.setattr(engine, "_torch_device", lambda: None)
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

    def fake_separate(model_file, input_path, output_dir, shifts=0):
        # zmapuj id modelu z pliku przez rejestr (odwrotnie) — uproszczone: po pliku
        reg = registry.load_registry()
        model_id = next(m.id for m in reg.values() if m.file == model_file)
        seen_inputs[model_id] = input_path
        return {stem: str(Path(output_dir) / name)
                for stem, name in fake_outputs[model_id].items()}

    monkeypatch.setattr(engine, "_separate_with_model", fake_separate)

    p = pipeline.load_preset("ultra")
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


def test_run_pipeline_steps_yields_stages_then_result(monkeypatch, tmp_path):
    def fake_separate(model_file, input_path, output_dir, shifts=0):
        reg = registry.load_registry()
        mid = next(m.id for m in reg.values() if m.file == model_file)
        return {"Instrumental": "x.wav"} if mid == "roformer_vocals" else {"Guitar": "g.wav"}

    monkeypatch.setattr(engine, "_separate_with_model", fake_separate)
    p = pipeline.load_preset("ultra")
    events = list(engine.run_pipeline_steps(tmp_path / "s.wav", p, ["gitara"], output_dir=tmp_path))
    assert [e[0] for e in events] == ["stage", "stage", "result"]
    assert events[0][1:] == (0, 2, "roformer_vocals", 1)
    assert events[1][1:] == (1, 2, "htdemucs_6s", 8)
    assert events[-1][1]["gitara"].endswith("g.wav")


def test_run_pipeline_reports_progress_per_stage(monkeypatch, tmp_path):
    def fake_separate(model_file, input_path, output_dir, shifts=0):
        from stemsplitter import registry
        reg = registry.load_registry()
        model_id = next(m.id for m in reg.values() if m.file == model_file)
        # etap 1 musi zwrocic 'Instrumental' zeby etap 2 mial wejscie
        if model_id == "roformer_vocals":
            return {"Instrumental": str(Path(output_dir) / "inst.wav")}
        return {}

    monkeypatch.setattr(engine, "_separate_with_model", fake_separate)

    calls = []
    p = pipeline.load_preset("ultra")
    engine.run_pipeline(tmp_path / "song.wav", p, [], output_dir=tmp_path,
                        progress_cb=lambda done, total, model_id: calls.append((done, total, model_id)))
    assert calls == [(0, 2, "roformer_vocals"), (1, 2, "htdemucs_6s")]


def test_normalna_reports_two_passes(monkeypatch, tmp_path):
    monkeypatch.setattr(engine, "_separate_with_model",
                        lambda mf, ip, od, shifts=0: {"Vocals": "v.wav"})
    p = pipeline.load_preset("normalna")
    events = list(engine.run_pipeline_steps(tmp_path / "s.wav", p, ["wokal"], output_dir=tmp_path))
    # htdemucs_6s (1 pod-model) x shifts=2
    assert events[0][1:] == (0, 1, "htdemucs_6s", 2)


def test_stage_shifts_flow_into_separation(monkeypatch, tmp_path):
    seen = {}

    def fake_separate(model_file, input_path, output_dir, shifts=0):
        reg = registry.load_registry()
        mid = next(m.id for m in reg.values() if m.file == model_file)
        seen[mid] = shifts
        return {"Instrumental": "x.wav"} if mid == "roformer_vocals" else {"Guitar": "g.wav"}

    monkeypatch.setattr(engine, "_separate_with_model", fake_separate)
    p = pipeline.load_preset("ultra")
    list(engine.run_pipeline_steps(tmp_path / "s.wav", p, ["gitara"], output_dir=tmp_path))
    assert seen == {"roformer_vocals": 0, "htdemucs_6s": 8}


def test_separate_with_model_passes_shifts_to_separator(monkeypatch, tmp_path):
    import sys
    import types

    captured = {}

    class FakeSeparator:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def load_model(self, model_filename):
            captured["model_filename"] = model_filename

        def separate(self, path):
            return []

    pkg = types.ModuleType("audio_separator")
    mod = types.ModuleType("audio_separator.separator")
    mod.Separator = FakeSeparator
    pkg.separator = mod
    monkeypatch.setitem(sys.modules, "audio_separator", pkg)
    monkeypatch.setitem(sys.modules, "audio_separator.separator", mod)
    monkeypatch.setattr(engine.paths, "ensure_data_dirs",
                        lambda: types.SimpleNamespace(models=tmp_path))

    engine._separate_with_model("htdemucs_6s.yaml", tmp_path / "s.wav", str(tmp_path), shifts=2)
    assert captured["demucs_params"]["shifts"] == 2

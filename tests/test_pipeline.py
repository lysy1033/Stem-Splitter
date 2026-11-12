import pytest
from stemsplitter import pipeline, registry


def test_normalna_single_6stem_roformer_stage():
    p = pipeline.load_preset("normalna")
    assert [s.model_id for s in p.stages] == ["roformer_sw"]
    assert p.stages[0].input == "mix"
    assert p.stages[0].shifts == 0          # roformer: shifts nie dotyczy
    assert p.stages[0].outputs["guitar"] == "gitara"
    assert p.stages[0].outputs["vocals"] == "wokal"


def test_ultra_cascade_vocals_then_sw():
    p = pipeline.load_preset("ultra")
    assert [s.model_id for s in p.stages] == ["roformer_vocals", "roformer_sw"]
    assert p.stages[0].shifts == 0          # roformer: shifts nie dotyczy
    assert p.stages[1].input == "instrumental"
    assert p.stages[1].outputs["guitar"] == "gitara"
    assert "vocals" not in p.stages[1].outputs   # resztki wokalu z etapu 2 pomijane


def test_both_presets_produce_all_six_stems():
    expected = {"wokal", "perkusja", "bas", "gitara", "pianino", "inne"}
    for name in ["normalna", "ultra"]:
        produced = pipeline._produced_stems(pipeline.load_preset(name).stages)
        assert expected <= produced, name


def test_extension_appended_when_requirement_met():
    p = pipeline.load_preset("normalna", extensions=["perkusja_elementy"])
    assert p.stages[-1].model_id == "drumsep"
    assert p.stages[-1].input == "perkusja"


def test_unknown_preset_raises():
    with pytest.raises(ValueError):
        pipeline.load_preset("nie_ma_takiego")


def test_extension_requirement_not_met_raises():
    # 'lead_chorki' wymaga stemu 'wokal'; gdy go brak w wyprodukowanych -> blad
    with pytest.raises(ValueError):
        pipeline._validate_extension_requirement("lead_chorki", produced={"perkusja"})


def test_all_referenced_models_exist_in_registry():
    reg = registry.load_registry()
    for name in ["normalna", "ultra"]:
        for stage in pipeline.load_preset(name).stages:
            assert stage.model_id in reg

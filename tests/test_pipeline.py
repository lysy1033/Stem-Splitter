import pytest
from stemsplitter import pipeline, registry


def test_load_preset_stages_in_order():
    p = pipeline.load_preset("maksymalna")
    assert [s.model_id for s in p.stages] == ["roformer_vocals", "htdemucs_6s"]
    assert p.stages[0].input == "mix"
    assert p.stages[1].input == "instrumental"
    assert p.stages[1].outputs["Guitar"] == "gitara"


def test_unknown_preset_raises():
    with pytest.raises(ValueError):
        pipeline.load_preset("nie_ma_takiego")


def test_extension_appended_when_requirement_met():
    p = pipeline.load_preset("najlepsza", extensions=["perkusja_elementy"])
    assert p.stages[-1].model_id == "drumsep"
    assert p.stages[-1].input == "perkusja"


def test_extension_requirement_not_met_raises():
    # 'lead_chorki' wymaga stemu 'wokal'; gdy go brak w wyprodukowanych -> blad
    with pytest.raises(ValueError):
        pipeline._validate_extension_requirement("lead_chorki", produced={"perkusja"})


def test_all_referenced_models_exist_in_registry():
    reg = registry.load_registry()
    for name in ["szybko", "najlepsza", "maksymalna"]:
        for stage in pipeline.load_preset(name).stages:
            assert stage.model_id in reg

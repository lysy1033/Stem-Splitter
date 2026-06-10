from stemsplitter import i18n


class _Req:
    def __init__(self, accept):
        self.headers = {"accept-language": accept}


def test_pick_lang_polish_from_header():
    assert i18n.pick_lang(_Req("pl-PL,pl;q=0.9,en;q=0.8")) == "pl"


def test_pick_lang_defaults_to_english():
    assert i18n.pick_lang(_Req("de-DE,de;q=0.9")) == "en"
    assert i18n.pick_lang(None) == "en"


def test_both_languages_have_identical_keys():
    en, pl = i18n.TEXT["en"], i18n.TEXT["pl"]
    assert set(en.keys()) == set(pl.keys())
    assert set(en["stem_labels"].keys()) == set(pl["stem_labels"].keys())
    assert set(en["presets"].keys()) == set(pl["presets"].keys())


def test_preset_keys_are_normalna_ultra():
    assert i18n.PRESET_KEYS == ["normalna", "ultra"]
    for lang in ("en", "pl"):
        assert set(i18n.TEXT[lang]["presets"].keys()) == {"normalna", "ultra"}


def test_sep_stage_multi_mentions_pass_count():
    for lang in ("en", "pl"):
        assert "{passes}" in i18n.TEXT[lang]["sep_stage_multi"]


def test_new_ui_texts_present():
    for lang in ("en", "pl"):
        t = i18n.TEXT[lang]
        assert t["yt_full"]
        assert "{stems}" in t["missing_stems"]

from stemsplitter import update


def test_is_newer_basic():
    assert update.is_newer("1.1", "1.0")
    assert not update.is_newer("1.0", "1.0")
    assert not update.is_newer("0.9", "1.0")


def test_is_newer_numeric_not_lexicographic():
    assert update.is_newer("1.10", "1.9")
    assert update.is_newer("1.0.1", "1.0")


def test_is_newer_tolerates_garbage():
    # nieparsowalne czlony traktujemy jak 0 — nigdy wyjatku
    assert not update.is_newer("abc", "1.0")


def test_current_version_reads_repo_file():
    v = update.current_version()
    assert v and v[0].isdigit()


def test_latest_version_returns_none_on_network_error(monkeypatch):
    import urllib.request

    def boom(*args, **kwargs):
        raise OSError("offline")

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    assert update.latest_version() is None


def test_update_available_pairs_versions(monkeypatch):
    monkeypatch.setattr(update, "current_version", lambda: "1.0")
    monkeypatch.setattr(update, "latest_version", lambda: "1.1")
    assert update.update_available() == ("1.0", "1.1")


def test_update_available_none_when_offline_or_current(monkeypatch):
    monkeypatch.setattr(update, "current_version", lambda: "1.0")
    monkeypatch.setattr(update, "latest_version", lambda: None)
    assert update.update_available() is None
    monkeypatch.setattr(update, "latest_version", lambda: "1.0")
    assert update.update_available() is None


def test_updater_script_matches_platform(monkeypatch):
    monkeypatch.setattr(update.sys, "platform", "darwin")
    assert update._updater_script().name == "update-mac.command"
    monkeypatch.setattr(update.sys, "platform", "win32")
    assert update._updater_script().name == "update-windows.bat"

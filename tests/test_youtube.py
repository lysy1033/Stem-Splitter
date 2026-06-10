import sys
import types
from stemsplitter import youtube


def test_is_url():
    assert youtube.is_url("https://youtu.be/abc")
    assert youtube.is_url("http://example.com/x")
    assert not youtube.is_url("song.mp3")
    assert not youtube.is_url("")
    assert not youtube.is_url(None)


def test_download_audio_uses_ytdlp(monkeypatch, tmp_path):
    created = {}

    class FakeYDL:
        def __init__(self, opts):
            created["opts"] = opts

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def extract_info(self, url, download):
            created["url"] = url
            created["download"] = download
            (tmp_path / "yt_ID.wav").write_bytes(b"wav")
            return {"id": "ID", "title": "My Song"}

    fake = types.ModuleType("yt_dlp")
    fake.YoutubeDL = FakeYDL
    monkeypatch.setitem(sys.modules, "yt_dlp", fake)

    out = youtube.download_audio("https://youtu.be/ID", tmp_path)
    assert out == (tmp_path / "yt_ID.wav", "My Song")
    assert created["url"] == "https://youtu.be/ID"
    assert created["download"] is True
    assert created["opts"]["noplaylist"] is True


def test_download_audio_falls_back_to_id_when_no_title(monkeypatch, tmp_path):
    class FakeYDL:
        def __init__(self, opts):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def extract_info(self, url, download):
            (tmp_path / "yt_X.wav").write_bytes(b"wav")
            return {"id": "X"}

    fake = types.ModuleType("yt_dlp")
    fake.YoutubeDL = FakeYDL
    monkeypatch.setitem(sys.modules, "yt_dlp", fake)
    assert youtube.download_audio("u", tmp_path)[1] == "X"


def test_download_audio_falls_back_to_id_when_title_blank(monkeypatch, tmp_path):
    class FakeYDL:
        def __init__(self, opts):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def extract_info(self, url, download):
            (tmp_path / "yt_X.wav").write_bytes(b"wav")
            return {"id": "X", "title": "   "}

    fake = types.ModuleType("yt_dlp")
    fake.YoutubeDL = FakeYDL
    monkeypatch.setitem(sys.modules, "yt_dlp", fake)
    assert youtube.download_audio("u", tmp_path)[1] == "X"

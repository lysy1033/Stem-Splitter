import pytest
from pathlib import Path
from stemsplitter import media


def test_audio_input_passthrough(tmp_path):
    src = tmp_path / "song.mp3"
    src.write_bytes(b"fake")
    out = media.prepare_input(src, work_dir=tmp_path)
    assert out == src  # audio nie wymaga ekstrakcji


def test_unsupported_extension_raises(tmp_path):
    src = tmp_path / "doc.txt"
    src.write_bytes(b"x")
    with pytest.raises(media.UnsupportedFormatError):
        media.prepare_input(src, work_dir=tmp_path)


def test_video_builds_ffmpeg_command(tmp_path, monkeypatch):
    src = tmp_path / "clip.mp4"
    src.write_bytes(b"fake")
    calls = {}

    def fake_run(cmd, check, capture_output):
        calls["cmd"] = cmd
        (tmp_path / "clip.wav").write_bytes(b"wav")
        class R: returncode = 0
        return R()

    monkeypatch.setattr(media.subprocess, "run", fake_run)
    out = media.prepare_input(src, work_dir=tmp_path)
    assert out.suffix == ".wav"
    assert "ffmpeg" in calls["cmd"][0]
    assert str(src) in calls["cmd"]


def test_safe_filename_strips_illegal_and_trims():
    assert media.safe_filename('A/B: "C"?*') == "AB C"
    assert media.safe_filename("  zwykły   tytuł  ") == "zwykły tytuł"
    assert media.safe_filename("...") == "utwor"
    assert len(media.safe_filename("x" * 200)) == 80


def test_to_mp3_invokes_ffmpeg(monkeypatch, tmp_path):
    seen = {}

    def fake_run(cmd, check, capture_output):
        seen["cmd"] = cmd
        Path(cmd[-1]).write_bytes(b"mp3")
        return None

    monkeypatch.setattr(media.subprocess, "run", fake_run)
    out = media.to_mp3(tmp_path / "in.wav", tmp_path, "Tytuł: utwór?")
    assert out == tmp_path / "Tytuł utwór.mp3"
    assert seen["cmd"][0] == "ffmpeg"
    assert "libmp3lame" in seen["cmd"]

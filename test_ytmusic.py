#!/usr/bin/env python3
"""Offline command-line checks: python3 test_ytmusic.py."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


with tempfile.TemporaryDirectory(prefix="ytmusic test ") as directory:
    root = Path(directory)
    script = root / "ytmusic"
    shutil.copy2(Path(__file__).with_name("ytmusic"), script)
    fake = root / ".venv/bin/yt-dlp"
    fake.parent.mkdir(parents=True)
    fake.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "with open(os.environ['YTMUSIC_TEST_ARGS'], 'w') as output:\n"
        "    json.dump(sys.argv[1:], output)\n"
        "sys.exit(int(os.environ.get('YTMUSIC_TEST_STATUS', '0')))\n"
    )
    fake.chmod(0o755)
    capture = root / "arguments.json"
    environment = dict(os.environ, YTMUSIC_TEST_ARGS=str(capture))

    def run(*arguments, status=0):
        capture.unlink(missing_ok=True)
        result = subprocess.run(
            [str(script), *arguments], capture_output=True, text=True,
            env=dict(environment, YTMUSIC_TEST_STATUS=str(status)),
        )
        passed = json.loads(capture.read_text()) if capture.exists() else None
        return result, passed

    canonical = "https://music.youtube.com/watch?v=abcDEF12_-3"
    url = canonical + "&list=album;$(printf bad)`printf bad`#ignored"
    output = str(root / "audio & spaces;$(printf bad)`printf bad`")
    result, arguments = run(url, output)
    assert result.returncode == 0, result.stderr
    assert arguments[arguments.index("--format") + 1] == "bestaudio"
    assert "--no-playlist" in arguments and "--no-overwrites" in arguments
    assert "--ignore-config" in arguments
    assert arguments[arguments.index("--audio-format") + 1] == "mp3"
    assert "--extract-audio" in arguments
    assert arguments[arguments.index("--paths") + 1] == f"home:{output}"
    assert arguments[-2:] == ["--", canonical]
    assert "--cookies-from-browser" not in arguments

    result, arguments = run("--audio-format", "flac", url, output)
    assert result.returncode == 0, result.stderr
    assert "--extract-audio" in arguments
    assert arguments[arguments.index("--audio-format") + 1] == "flac"

    result, arguments = run("--ffmpeg-location", "/opt/ffmpeg", url, output)
    assert result.returncode == 0, result.stderr
    assert arguments[arguments.index("--ffmpeg-location") + 1] == "/opt/ffmpeg"

    playlist = "https://music.youtube.com/playlist?list=PL_test-123"
    for link in (playlist, canonical + "&list=PL_test-123&index=4",
                 "https://www.youtube.com/playlist?list=PL_test-123#fragment"):
        result, arguments = run("--playlist", link, output)
        assert result.returncode == 0, result.stderr
        assert arguments[-2:] == ["--", playlist]
        assert "--yes-playlist" in arguments and "--no-playlist" not in arguments
        assert "--cookies-from-browser" not in arguments
        assert arguments[arguments.index("--format") + 1] == "bestaudio"
        assert arguments[arguments.index("--paths") + 1] == f"home:{output}"
        template = arguments[arguments.index("--output") + 1]
        assert "%(playlist_title,playlist_id)" in template and "%(playlist_id)s]/" in template
        assert template.split("/")[1].startswith("%(playlist_index)03d - ")

    for scope, link in (((), canonical), (("--playlist",), playlist)):
        for browser in ("chrome", "firefox", "safari", "chrome:Profile 1;$(printf bad)`printf bad`"):
            result, arguments = run(*scope, "--login", browser, link)
            assert result.returncode == 0, result.stderr
            assert arguments.count("--cookies-from-browser") == 1
            assert arguments[arguments.index("--cookies-from-browser") + 1] == browser
            assert arguments[-2:] == ["--", link]

    result, arguments = run("https://youtu.be/abcDEF12_-3?list=ignored#fragment")
    assert result.returncode == 0, result.stderr
    assert arguments[-1] == canonical
    assert arguments[arguments.index("--paths") + 1] == f"home:{os.environ['HOME']}/Downloads/YouTube Music"

    for help_flag in ("-h", "--help"):
        result, arguments = run(help_flag)
        assert result.returncode == 0 and "usage:" in result.stdout
        assert arguments is None
    for invalid in (
        (), (url, output, "extra"), (url, ""), ("--version",),
        ("https://example.com/watch?v=abcDEF12_-3",),
        ("--audio-format", "drm", canonical),
        ("https://music.youtube.com.evil.test/watch?v=abcDEF12_-3",),
        ("https://music.youtube.com@evil.test/watch?v=abcDEF12_-3",),
        ("https://music.youtube.com/playlist?list=album",),
        ("https://music.youtube.com/watch?list=album",),
        ("https://music.youtube.com/watch?v=&list=album",),
        ("https://music.youtube.com/watch#v=abcDEF12_-3",),
        ("https://music.youtube.com/watch?v=short",),
        (canonical + "&v=abcDEF12_-3",),
        (canonical + "&v=",),
    ):
        result, arguments = run(*invalid)
        assert result.returncode == 2 and result.stderr, (invalid, result)
        assert arguments is None, invalid

    for link in (
        "https://music.youtube.com/playlist", playlist + "&list=other",
        playlist + "&list=", "https://music.youtube.com/playlist?list=",
        "https://music.youtube.com/playlist?list=bad%20id",
        "https://music.youtube.com/playlist?list=bad;$(printf%20bad)",
        playlist.replace("https:", "http:"), playlist.replace("https:", "file:"),
        playlist.replace("music.youtube.com", "music.youtube.com.evil.test"),
        playlist.replace("music.youtube.com", "music.youtube.com@evil.test"),
        playlist.replace("/playlist", "/channel"), canonical,
    ):
        result, arguments = run("--playlist", link)
        assert result.returncode == 2 and result.stderr and arguments is None, link
    for browser in ("", "unknown", "chrome:", "--cookies", "chrome\nfirefox"):
        result, arguments = run("--playlist", "--login", browser, playlist)
        assert result.returncode == 2 and result.stderr and arguments is None, browser

    result, arguments = run(url, status=19)
    assert result.returncode == 19 and arguments[-1] == canonical
    result, arguments = run("--playlist", playlist, status=19)
    assert result.returncode == 19 and arguments[-1] == playlist

    # Verify PATH fallback without relying on any installed downloader.
    fallback = root / "bin"
    fallback.mkdir()
    shutil.move(fake, fallback / "yt-dlp")
    environment["PATH"] = f"{fallback}{os.pathsep}{os.environ.get('PATH', '')}"
    result, arguments = run(url)
    assert result.returncode == 0 and arguments[-1] == canonical

print("PASS: native audio, track/playlist scope, ordered folders, browser login, literal arguments, defaults, validation, help, exit status, PATH fallback")

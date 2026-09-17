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
    assert not {"-x", "--extract-audio", "--audio-format", "--recode-video"}.intersection(arguments)
    assert arguments[arguments.index("--paths") + 1] == f"home:{output}"
    assert arguments[-2:] == ["--", canonical]

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

    result, arguments = run(url, status=19)
    assert result.returncode == 19 and arguments[-1] == canonical

    # Verify PATH fallback without relying on any installed downloader.
    fallback = root / "bin"
    fallback.mkdir()
    shutil.move(fake, fallback / "yt-dlp")
    environment["PATH"] = f"{fallback}{os.pathsep}{os.environ.get('PATH', '')}"
    result, arguments = run(url)
    assert result.returncode == 0 and arguments[-1] == canonical

print("PASS: native audio flags, literal output paths, canonical track URLs, defaults, validation, help, exit status, PATH fallback")

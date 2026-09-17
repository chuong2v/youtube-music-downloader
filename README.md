# YouTube Music downloader

Download one track's best available audio-only stream, keeping the original codec
and container. The result is typically `.webm` (Opus) or `.m4a` (AAC); there is no
MP3 conversion or re-encoding. Quality is limited to the formats YouTube makes
available to yt-dlp for that request.

```sh
./ytmusic "https://music.youtube.com/watch?v=VIDEO_ID"
./ytmusic "https://music.youtube.com/watch?v=VIDEO_ID" "$HOME/Music"
```

Downloads default to `~/Downloads/YouTube Music`. Filenames include the track's
title and video ID. Existing files are not overwritten; interrupted downloads
can resume. A track link containing a playlist parameter downloads just that
track. Playlist-only links are rejected.

## Setup on macOS

The launcher requires Python 3.9 or newer.

```sh
brew install yt-dlp deno
chmod +x ytmusic
```

Alternatively, install yt-dlp in a Python 3.10+ virtual environment named `.venv`
beside the script. The script prefers that installation if present. A supported
Deno or Node.js runtime must also be available on `PATH`.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -U 'yt-dlp[default]'
```

Update yt-dlp with the same package manager if YouTube changes break downloads.
Login-required tracks may fail; this tool does not access browser cookies.

The options follow the official [yt-dlp documentation](https://github.com/yt-dlp/yt-dlp#format-selection)
and [JavaScript runtime setup](https://github.com/yt-dlp/yt-dlp/wiki/EJS).

## Offline checks

```sh
python3 test_ytmusic.py
```

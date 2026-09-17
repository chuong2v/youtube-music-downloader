# YouTube Music downloader

Download tracks or playlists as MP3 by default. Use `--audio-format` for WMA, OGG, M4A, ACELP, FLAC,
WAV, or APE conversion through FFmpeg. DRM is not an output format; `.webm` is never kept.

```sh
./ytmusic "https://music.youtube.com/watch?v=VIDEO_ID"
./ytmusic "https://music.youtube.com/watch?v=VIDEO_ID" "$HOME/Music"
./ytmusic --audio-format mp3 "https://music.youtube.com/watch?v=VIDEO_ID"
```

Conversion requires both `ffmpeg` and `ffprobe` on `PATH`. If they are elsewhere, use
`--ffmpeg-location /path/to/bin`.

Downloads default to `~/Downloads/YouTube Music`. Filenames include the track's
title and video ID. Existing files are not overwritten; interrupted downloads
can resume. A track link containing a playlist parameter downloads just that
track. Add `--playlist` to download a whole playlist.

## Playlists and login

Sign in to YouTube Music in your browser first, then use that browser's session:

```sh
./ytmusic --playlist --login chrome "https://music.youtube.com/playlist?list=PLAYLIST_ID"
./ytmusic --playlist "https://music.youtube.com/playlist?list=PLAYLIST_ID" "$HOME/Music"
./ytmusic --login "chrome:Profile 1" "https://music.youtube.com/watch?v=VIDEO_ID"
```

`--login` reads the selected browser's cookies through yt-dlp. It does not open
a login page or ask for your password. Chrome, Firefox, Safari, Brave, Chromium,
Edge, Opera, Vivaldi, and Whale are supported. Omit it for public downloads.
On macOS, your browser's cookies may require a Keychain or system permission prompt.
The tool does not export cookies to a file. Access still depends on your account
and the formats YouTube makes available.

Playlist tracks go into a playlist-named subfolder and include their playlist
position in the filename. Both playlist links and full YouTube watch links with
`list=` are accepted in playlist mode. Unavailable tracks are reported by yt-dlp;
it continues to subsequent entries and returns a nonzero status on download errors.

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
For login-required tracks or private playlists, use `--login` with a browser
signed into an account that can access them.

The options follow the official [yt-dlp documentation](https://github.com/yt-dlp/yt-dlp#format-selection)
and [JavaScript runtime setup](https://github.com/yt-dlp/yt-dlp/wiki/EJS).
Browser login uses yt-dlp's documented
[cookie support](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp).

## Offline checks

```sh
python3 test_ytmusic.py
```


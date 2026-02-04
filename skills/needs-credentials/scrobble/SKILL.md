---
name: scrobble
description: Scrobble music to Last.fm. Use when user wants to record/scrobble album plays, individual tracks, or NTS radio shows. Handles named albums (looks up tracklist), provided tracklists, and NTS radio show format (auto-detects by timestamp patterns like 0:00:10 and show metadata). Reports success after scrobbling.
---

# Scrobble to Last.fm

Scrobble albums, tracks, or NTS radio shows to your Last.fm profile.

## Credentials

Store your Last.fm API credentials in `~/.config/secrets/lastfm/`:

```
~/.config/secrets/lastfm/
├── api-key
├── api-secret
├── session-key
└── username
```

See SETUP.md for how to obtain these.

## Workflows

### 1. Scrobble a Named Album

1. Search the web for the album's tracklist
2. Extract track names and durations
3. Run the scrobble script with tracks

### 2. Scrobble a Provided Tracklist

Parse the user's tracklist and scrobble directly.

### 3. Scrobble an NTS Radio Show

**Detection:** NTS format has:
- Header with date · location (e.g., "26 Nov 2025 · Los Angeles")
- Show name line
- Tracklist with timestamps like `0:00:10` or `--:--`
- Artist on one line, track title on next line

**Parsing:**
1. Extract show name, location, date from header
2. Parse each track: timestamp line → artist line → track line
3. Album field = `NTS: Show Name - Location (Date)`

**Example NTS format:**
```
26 Nov 2025 · Los Angeles

The Windmills of Your Mind w/ Taylor Rowley
...
0:00:10
Dorothy Ashby
The Windmills Of Your Mind
0:00:51
Vivi, Les Soul Men
Toe Même Maloya
```

## Scrobble Script

Run this Python script to scrobble. It uses only stdlib (hashlib, urllib, json, time).

```python
#!/usr/bin/env python3
"""Last.fm scrobbler - stdlib only"""
import hashlib
import json
import os
import time
import urllib.request
import urllib.parse
from pathlib import Path

# Load credentials from files
SECRETS_DIR = Path.home() / '.config' / 'secrets' / 'lastfm'
API_KEY = (SECRETS_DIR / 'api-key').read_text().strip()
API_SECRET = (SECRETS_DIR / 'api-secret').read_text().strip()
SESSION_KEY = (SECRETS_DIR / 'session-key').read_text().strip()
USERNAME = (SECRETS_DIR / 'username').read_text().strip()

API_URL = 'https://ws.audioscrobbler.com/2.0/'

def get_sig(params):
    """Generate API signature"""
    sig_string = ''.join(f'{k}{params[k]}' for k in sorted(params))
    sig_string += API_SECRET
    return hashlib.md5(sig_string.encode()).hexdigest()

def api_call(method, params, post=False):
    """Make Last.fm API call"""
    params['method'] = method
    params['api_key'] = API_KEY
    params['sk'] = SESSION_KEY
    params['api_sig'] = get_sig(params)
    params['format'] = 'json'

    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(API_URL, data=data if post else None)
    if not post:
        req = urllib.request.Request(f'{API_URL}?{data.decode()}')

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def scrobble_track(artist, track, album, timestamp):
    """Scrobble a single track"""
    params = {
        'artist': artist,
        'track': track,
        'album': album,
        'timestamp': str(timestamp)
    }
    return api_call('track.scrobble', params, post=True)

def scrobble_tracks(tracks, album, start_time=None):
    """
    Scrobble multiple tracks.
    tracks: list of (artist, track_name, duration_seconds)
    """
    if start_time is None:
        # Start from now minus total duration
        total_duration = sum(t[2] for t in tracks)
        start_time = int(time.time()) - total_duration

    current_time = start_time
    results = []

    for artist, track_name, duration in tracks:
        result = scrobble_track(artist, track_name, album, current_time)
        results.append((artist, track_name, result))
        current_time += duration
        time.sleep(0.5)  # Rate limit

    return results

# Example usage:
# tracks = [
#     ("Dorothy Ashby", "The Windmills Of Your Mind", 41),
#     ("Vivi, Les Soul Men", "Toe Même Maloya", 199),
#     ...
# ]
# results = scrobble_tracks(tracks, "NTS: Show Name - Location (Date)")
```

## After Scrobbling

Report:
- Number of tracks scrobbled
- Album/show name
- Link to Last.fm profile: `https://www.last.fm/user/YOUR_USERNAME`

## Duration Estimation

When timestamps are missing (`--:--`), estimate duration as 3-4 minutes per track (180-240 seconds).

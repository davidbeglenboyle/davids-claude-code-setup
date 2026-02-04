# Scrobble Skill Setup (Last.fm)

How to set up Last.fm API access for scrobbling music.

## Overview

This skill uses the Last.fm API to scrobble (record) your music listening. You'll need:
1. A Last.fm account
2. An API application (API key + secret)
3. A session key (authenticated access to your account)

## Setup Steps

### 1. Create Last.fm Account

If you don't have one:
1. Go to [Last.fm](https://www.last.fm/)
2. Sign up for a free account
3. Note your username

### 2. Create an API Application

1. Go to [Last.fm API Account](https://www.last.fm/api/account/create)
2. Fill in:
   - **Application name**: "Claude Code Scrobbler" (or your choice)
   - **Application description**: "Personal scrobbling tool"
   - **Application homepage**: Can be blank or your website
   - **Callback URL**: Can be blank
3. Click **Submit**
4. You'll see your **API Key** and **Shared Secret**
5. Save both securely

### 3. Get a Session Key

The session key authenticates your account. This is a one-time process.

**Method 1: Web Authentication (Recommended)**

1. Create this auth script:

```python
#!/usr/bin/env python3
"""Get Last.fm session key via web auth."""
import hashlib
import urllib.request
import urllib.parse
import json
import webbrowser
from pathlib import Path

# Your API credentials (from step 2)
API_KEY = "YOUR_API_KEY_HERE"
API_SECRET = "YOUR_API_SECRET_HERE"

API_URL = "https://ws.audioscrobbler.com/2.0/"

def get_sig(params):
    sig_string = ''.join(f'{k}{params[k]}' for k in sorted(params))
    sig_string += API_SECRET
    return hashlib.md5(sig_string.encode()).hexdigest()

def api_call(method, params, post=False):
    params['method'] = method
    params['api_key'] = API_KEY
    params['api_sig'] = get_sig(params)
    params['format'] = 'json'

    data = urllib.parse.urlencode(params).encode()
    if post:
        req = urllib.request.Request(API_URL, data=data)
    else:
        req = urllib.request.Request(f'{API_URL}?{data.decode()}')

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

# Step 1: Get auth token
result = api_call('auth.getToken', {})
token = result['token']

# Step 2: User authorizes in browser
auth_url = f"https://www.last.fm/api/auth/?api_key={API_KEY}&token={token}"
print(f"Opening browser for authorization...")
print(f"URL: {auth_url}")
webbrowser.open(auth_url)

input("\nPress Enter after authorizing in the browser...")

# Step 3: Get session key
result = api_call('auth.getSession', {'token': token})
session_key = result['session']['key']
username = result['session']['name']

print(f"\n✅ Success!")
print(f"Username: {username}")
print(f"Session Key: {session_key}")
print(f"\nSave this session key - you won't need to do this again.")
```

2. Replace `YOUR_API_KEY_HERE` and `YOUR_API_SECRET_HERE`
3. Run: `python3 lastfm_auth.py`
4. Authorize in the browser when it opens
5. Copy the session key from the output

### 4. Store Credentials

```bash
# Create secrets directory
mkdir -p ~/.config/secrets/lastfm

# Save each credential
echo "YOUR_API_KEY" > ~/.config/secrets/lastfm/api-key
echo "YOUR_API_SECRET" > ~/.config/secrets/lastfm/api-secret
echo "YOUR_SESSION_KEY" > ~/.config/secrets/lastfm/session-key
echo "YOUR_USERNAME" > ~/.config/secrets/lastfm/username

# Set permissions
chmod 700 ~/.config/secrets/lastfm
chmod 600 ~/.config/secrets/lastfm/*
```

### 5. Test the Setup

```python
from pathlib import Path
import hashlib
import urllib.request
import urllib.parse
import json

SECRETS_DIR = Path.home() / '.config' / 'secrets' / 'lastfm'
API_KEY = (SECRETS_DIR / 'api-key').read_text().strip()
API_SECRET = (SECRETS_DIR / 'api-secret').read_text().strip()
SESSION_KEY = (SECRETS_DIR / 'session-key').read_text().strip()

def get_sig(params):
    sig_string = ''.join(f'{k}{params[k]}' for k in sorted(params))
    sig_string += API_SECRET
    return hashlib.md5(sig_string.encode()).hexdigest()

# Test: get user info
params = {
    'method': 'user.getInfo',
    'api_key': API_KEY,
    'sk': SESSION_KEY,
}
params['api_sig'] = get_sig(params)
params['format'] = 'json'

url = f"https://ws.audioscrobbler.com/2.0/?{urllib.parse.urlencode(params)}"
with urllib.request.urlopen(url) as resp:
    data = json.loads(resp.read())
    print(f"✅ Connected as: {data['user']['name']}")
    print(f"Playcount: {data['user']['playcount']}")
```

## Multi-Machine Setup

All credentials are account-based, not machine-specific — sync them:

```bash
# Move to synced secrets
mv ~/.config/secrets/lastfm ~/Dropbox/.secrets/

# Symlink (if not already done)
ln -s ~/Dropbox/.secrets ~/.config/secrets
```

## Session Key Validity

Session keys are **permanent** unless:
- You revoke API access in Last.fm settings
- You change your Last.fm password
- The application is deleted

If your session key stops working, re-run the auth process.

## Troubleshooting

### "Invalid session key"
1. Re-run the authentication process
2. Verify session key is stored correctly (no extra whitespace)

### "Invalid API key"
1. Check API key is correct
2. Verify application still exists at last.fm/api/accounts

### "Scrobbles not appearing"
1. Last.fm has a ~2 minute delay for scrobbles to appear
2. Check your recent tracks: `https://www.last.fm/user/USERNAME`
3. Verify timestamps are in the past (not future)

## AI Agent Instructions

When setting this up via Claude Code:

1. Cannot create Last.fm account — user must do this
2. Cannot authorize API access — requires browser interaction
3. Can help store credentials once user provides them
4. Can test API connection and run scrobbles

Tell the user: "Please create a Last.fm API application and run the auth script to get a session key. Once you have the API key, secret, and session key, I can help you configure everything."

# Calendar Skill Setup

How to set up Google Calendar API access for this skill.

## Overview

This skill uses Google Calendar API with OAuth 2.0 authentication. You'll need:
1. A Google Cloud project with Calendar API enabled
2. OAuth credentials (credentials.json)
3. An authenticated token (token.json) — generated on first run

## Setup Steps

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Note the project name

### 2. Enable Calendar API

1. Go to **APIs & Services** → **Library**
2. Search for "Google Calendar API"
3. Click **Enable**

### 3. Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. If prompted, configure OAuth consent screen first:
   - User Type: **External** (or Internal if using Google Workspace)
   - Add your email as a test user
4. Application type: **Desktop app**
5. Name: "Calendar CLI" (or your preference)
6. Click **Create**
7. Download the JSON file

### 4. Install Credentials

```bash
# Create config directory
mkdir -p ~/.config/google-calendar

# Move downloaded credentials (rename to credentials.json)
mv ~/Downloads/client_secret_*.json ~/.config/google-calendar/credentials.json

# Set permissions
chmod 600 ~/.config/google-calendar/credentials.json
```

### 5. First Authentication

Create this auth script:

```python
#!/usr/bin/env python3
"""One-time authentication for Google Calendar API."""
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar']
CONFIG_DIR = Path.home() / '.config' / 'google-calendar'
CREDS_PATH = CONFIG_DIR / 'credentials.json'
TOKEN_PATH = CONFIG_DIR / 'token.json'

def authenticate():
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_PATH.write_text(creds.to_json())
        print(f"✅ Token saved to {TOKEN_PATH}")

    print("✅ Authentication successful!")

if __name__ == '__main__':
    authenticate()
```

Save as `~/.config/google-calendar/auth.py` and run:

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
python3 ~/.config/google-calendar/auth.py
```

This opens a browser. Sign in and grant calendar access. The token is saved automatically.

### 6. Verify Setup

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

TOKEN_PATH = os.path.expanduser("~/.config/google-calendar/token.json")
creds = Credentials.from_authorized_user_file(TOKEN_PATH, ['https://www.googleapis.com/auth/calendar'])
service = build('calendar', 'v3', credentials=creds)

# List calendars
calendars = service.calendarList().list().execute()
for cal in calendars['items']:
    print(f"- {cal['summary']}")
```

## Multi-Machine Setup

If you sync credentials between machines:

1. **credentials.json** — Can be synced (it's your OAuth client config)
2. **token.json** — Can be synced (same Google account)

Both files can live in your synced secrets directory:

```bash
ln -s ~/Dropbox/.secrets/google-calendar ~/.config/google-calendar
```

## Token Refresh

The token auto-refreshes when expired. If you get authentication errors:

1. Delete `~/.config/google-calendar/token.json`
2. Re-run `auth.py`
3. Re-authenticate in browser

## AI Agent Instructions

If setting this up via Claude Code:

1. Check if `~/.config/google-calendar/` exists
2. Look for `credentials.json` — if missing, tell user to follow steps 1-4 above
3. Look for `token.json` — if missing, run auth script (requires browser)
4. Test with a simple calendar list query

The browser-based OAuth flow must be done interactively — an AI agent cannot complete this step automatically.

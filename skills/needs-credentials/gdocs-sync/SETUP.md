# Google Docs Sync Setup

How to set up Google Docs API access for syncing Markdown files.

## Overview

This skill uses Google Docs API with OAuth 2.0 authentication. You'll need:
1. A Google Cloud project with Docs API enabled
2. OAuth credentials (credentials.json)
3. An authenticated token (token.json) — generated on first run
4. The sync scripts installed

## Setup Steps

### 1. Create Google Cloud Project

If you already have a project for Google Calendar, you can reuse it.

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Note the project name

### 2. Enable Google Docs API

1. Go to **APIs & Services** → **Library**
2. Search for "Google Docs API"
3. Click **Enable**
4. Also enable "Google Drive API" (needed for creating docs)

### 3. Create OAuth Credentials

If you already have Desktop app credentials (e.g., for Calendar), you can reuse them — just add the Docs scopes.

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Application type: **Desktop app**
4. Name: "Docs CLI" (or your preference)
5. Download the JSON file

### 4. Install Credentials

```bash
# Create config directory
mkdir -p ~/.config/google-docs

# Move downloaded credentials
mv ~/Downloads/client_secret_*.json ~/.config/google-docs/credentials.json

# Set permissions
chmod 600 ~/.config/google-docs/credentials.json
```

### 5. Create Auth Script

Save as `~/.config/google-docs/gdocs_auth.py`:

```python
#!/usr/bin/env python3
"""One-time authentication for Google Docs API."""
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]
CONFIG_DIR = Path.home() / '.config' / 'google-docs'
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

### 6. Create Sync Script

Save as `~/.config/google-docs/gdocs_sync.py`:

```python
#!/usr/bin/env python3
"""Sync Markdown to Google Docs with stable URLs."""
import argparse
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

CONFIG_DIR = Path.home() / '.config' / 'google-docs'
TOKEN_PATH = CONFIG_DIR / 'token.json'
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]

def get_services():
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    docs = build('docs', 'v1', credentials=creds)
    drive = build('drive', 'v3', credentials=creds)
    return docs, drive

def markdown_to_requests(content):
    """Convert Markdown to Google Docs API requests."""
    requests = []
    index = 1

    for line in content.split('\n'):
        if line.startswith('# '):
            requests.append({
                'insertText': {'location': {'index': index}, 'text': line[2:] + '\n'}
            })
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': index, 'endIndex': index + len(line[2:]) + 1},
                    'paragraphStyle': {'namedStyleType': 'HEADING_1'},
                    'fields': 'namedStyleType'
                }
            })
            index += len(line[2:]) + 1
        elif line.startswith('## '):
            requests.append({
                'insertText': {'location': {'index': index}, 'text': line[3:] + '\n'}
            })
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': index, 'endIndex': index + len(line[3:]) + 1},
                    'paragraphStyle': {'namedStyleType': 'HEADING_2'},
                    'fields': 'namedStyleType'
                }
            })
            index += len(line[3:]) + 1
        else:
            requests.append({
                'insertText': {'location': {'index': index}, 'text': line + '\n'}
            })
            index += len(line) + 1

    return requests

def sync(markdown_path, doc_id_path, title):
    docs, drive = get_services()

    # Read markdown
    content = Path(markdown_path).read_text()

    # Load or create doc ID
    doc_id_file = Path(doc_id_path)
    if doc_id_file.exists():
        doc_id = json.loads(doc_id_file.read_text()).get('doc_id')
        print(f"Updating existing document: {doc_id}")
    else:
        doc_id = None

    if doc_id:
        # Clear and update existing doc
        doc = docs.documents().get(documentId=doc_id).execute()
        end_index = doc['body']['content'][-1]['endIndex'] - 1
        if end_index > 1:
            docs.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': [{'deleteContentRange': {'range': {'startIndex': 1, 'endIndex': end_index}}}]}
            ).execute()
    else:
        # Create new doc
        doc = docs.documents().create(body={'title': title}).execute()
        doc_id = doc['documentId']
        doc_id_file.write_text(json.dumps({'doc_id': doc_id}, indent=2))
        print(f"Created new document: {doc_id}")

    # Insert content
    requests = markdown_to_requests(content)
    if requests:
        docs.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"✅ Document updated")
    print(f"📄 URL: {url}")
    return url

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('markdown_file')
    parser.add_argument('doc_id_file')
    parser.add_argument('--title', default='Untitled Document')
    args = parser.parse_args()

    sync(args.markdown_file, args.doc_id_file, args.title)
```

### 7. Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

### 8. Authenticate

```bash
python3 ~/.config/google-docs/gdocs_auth.py
```

This opens a browser. Sign in and grant Docs access.

### 9. Test

```bash
echo "# Test Document\n\nThis is a test." > /tmp/test.md
python3 ~/.config/google-docs/gdocs_sync.py /tmp/test.md /tmp/test_doc_id.json --title "Test Doc"
```

Check the output URL — you should see your document.

## Multi-Machine Setup

**credentials.json** — Can be synced (your OAuth client config)
**token.json** — Syncing may work, but Google sometimes invalidates tokens used from multiple IPs. If you get auth errors on the second machine, re-run `gdocs_auth.py`.

Safer approach: Keep credentials.json synced, but authenticate separately on each machine.

## AI Agent Instructions

When setting this up via Claude Code:

1. Cannot create Google Cloud project — user must do this
2. Cannot complete OAuth flow — requires browser
3. Can create the scripts once credentials.json is in place
4. Can run sync once token.json exists

Tell the user: "Please create a Google Cloud project with Docs API enabled and download OAuth credentials. I can then set up the sync scripts."

#!/usr/bin/env python3
"""One-time authentication for Google Docs API (branded docs).

Requires documents + drive scopes (drive scope needed to copy templates).
"""
import os
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive',
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
            if not CREDS_PATH.exists():
                print(f"ERROR: No credentials.json found at {CREDS_PATH}")
                print("Download OAuth credentials from Google Cloud Console first.")
                print("See SETUP.md for instructions.")
                raise SystemExit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)

        # Create the token private (0600) from the first byte, not chmod afterwards
        fd = os.open(TOKEN_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as f:
            f.write(creds.to_json())
        print(f"Token saved to {TOKEN_PATH}")

    print("Authentication successful!")


if __name__ == '__main__':
    authenticate()

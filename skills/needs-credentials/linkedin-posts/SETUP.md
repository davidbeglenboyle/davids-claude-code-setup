# LinkedIn Posts Setup

How to install the skill and its prerequisites. This takes about five minutes and requires no API keys.

## Overview

This skill doesn't use an OAuth flow or stored credential file. Instead, it reads LinkedIn's session cookies directly from your logged-in Chrome browser. That means:

* **No Google Cloud project** to create
* **No OAuth client** to register
* **No API keys** to rotate
* **No tokens** to refresh

But there is a prerequisite you cannot skip: **you must be signed into LinkedIn in Chrome on the same machine where the script runs.**

## Prerequisites

1. Google Chrome installed (the regular desktop Chrome, not a debug build)
2. Signed into linkedin.com in Chrome
3. Python 3.9 or later

## Installation

### 1. Copy the skill files

```bash
mkdir -p ~/.claude/skills/linkedin-posts
cp linkedin-posts/* ~/.claude/skills/linkedin-posts/
```

Or, if you're pulling this repo from git, symlink instead:

```bash
ln -s "$(pwd)/skills/needs-credentials/linkedin-posts" ~/.claude/skills/linkedin-posts
```

### 2. Install Python dependencies

```bash
pip3 install --user linkedin-api browser_cookie3
```

On macOS with Homebrew Python, you may need `--break-system-packages`:

```bash
pip3 install --break-system-packages --user linkedin-api browser_cookie3
```

Both packages:

* `linkedin-api` — the Python client for LinkedIn's Voyager API
* `browser_cookie3` — reads session cookies from Chrome's SQLite cookie store

### 3. Sign into LinkedIn in Chrome

Open Chrome and make sure you're logged into linkedin.com. You can close the tab afterwards — cookies persist. You do NOT need to leave Chrome running while the script executes.

### 4. (macOS only) Grant Python access to Chrome's cookie store

On macOS, Chrome stores cookies in an encrypted SQLite database, and decryption requires access to your Keychain. The first time you run `fetch_posts.py`, macOS will prompt:

> "Python wants to use your confidential information stored in 'Chrome' in your keychain."

Click **Allow** (once), not **Always Allow**. "Always Allow" gives that Python binary a standing right to read the key that decrypts every cookie in your Chrome profile, for any script you ever run with it, not just this skill. Allowing once means a prompt on each run, which is the safer trade. If you want no prompts, run the skill from a dedicated Python virtual environment and grant "Always Allow" only to that interpreter, never to the system or Homebrew Python. If you click **Deny**, future runs will fail silently and you'll need to reset the Keychain entry for Chrome Safe Storage.

## Test

Run the skill against a single public person to verify it works:

```bash
cd ~/.claude/skills/linkedin-posts
python3 fetch_posts.py \
    --config partners.example.json \
    --output /tmp/linkedin-test \
    --max-posts 5
```

Expected output:

```
Fetching posts for 1 partner(s), max 5 each
Extracting LinkedIn cookies from Chrome...
Authenticated!

[1/1] Example Person (example-slug)...
  Got 5 posts, 3 comments-on-others

Done! 5 posts + 3 comments from 1 partners saved to /tmp/linkedin-test/2026-04-11.json

Summary:
  Example Person: 4 original, 1 reshares, 3 comments, 127 likes
```

If you see `ERROR: No li_at cookie found`, you're not signed into LinkedIn in Chrome. If you see a macOS Keychain prompt, click **Allow** (once).

## Troubleshooting

### "No li_at cookie found"

You're not signed into LinkedIn in Chrome. Open Chrome, go to linkedin.com, sign in, then re-run.

### macOS Keychain prompt keeps appearing

Click "Allow" each time (see step 4 for why not "Always Allow"). If you accidentally denied, open **Keychain Access** → search for "Chrome Safe Storage" → delete the entry → run the script again → re-approve.

### HTTP 400 on comments fetch

LinkedIn has rotated its GraphQL `queryId` hashes. See `SKILL.md` → "When LinkedIn rotates GraphQL query IDs" for the re-capture procedure.

### HTTP 401 / auth errors

Your `li_at` cookie has expired (typically after 6-12 months). Sign out of LinkedIn in Chrome and sign back in. The next fetch will pick up the new cookie automatically.

### Fetches are suddenly empty or blocked

You may have been rate-limited or challenged by LinkedIn. Slow down (increase `--delay`), reduce `--max-posts`, and stop running batch fetches more than once a day against the same people. If the problem persists, sign into linkedin.com in a normal browser window and solve any security challenge.

### `fetch_posts.py` can't find `linkedin_posts_lib.py`

`fetch_posts.py` expects the library file to be in the same directory. Make sure both files are in `~/.claude/skills/linkedin-posts/` together.

## Multi-machine setup

The cookies are machine-local — each machine reads its own Chrome cookie store. You need to be signed into LinkedIn in Chrome on **every** machine where you run the skill.

There is no shared secret or token file to sync between machines. You can freely copy the skill files to each machine, install the Python dependencies, sign in once, and go.

## Security notes

* The `li_at` cookie is roughly equivalent to a LinkedIn password for session access. Don't log the full cookie value, don't commit it to git, and don't share it.
* The `browser_cookie3` library reads cookies via Chrome's standard cookie store and macOS Keychain. It doesn't bypass any security — it uses the same path Chrome itself uses.
* If you're uncomfortable with that trust model, don't install this skill. There is no safer alternative that accesses LinkedIn posts without a paid API contract.

## AI agent instructions

When setting this skill up via Claude Code:

1. Cannot sign the user into LinkedIn — the user must do this in Chrome
2. Cannot install the Python packages without the user's approval — use the `Bash` tool and expect permission prompts
3. Cannot dismiss the macOS Keychain prompt — the user must click "Allow" on first run (not "Always Allow")
4. Can copy the skill files into `~/.claude/skills/linkedin-posts/`
5. Can run the test fetch once signed-in status is confirmed

Tell the user: "Please make sure you're signed into LinkedIn in Chrome, then I'll install the Python dependencies and run a test fetch against one person to confirm it's working."

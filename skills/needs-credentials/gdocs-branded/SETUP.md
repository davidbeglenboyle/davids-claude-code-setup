# Branded Google Docs Setup

How to set up Google Docs API access for generating branded documents from Markdown.

## Overview

This skill uses Google Docs API and Google Drive API with OAuth 2.0 authentication. You'll need:

1. A Google Cloud project with Docs and Drive APIs enabled
2. OAuth credentials (credentials.json)
3. An authenticated token (token.json) — generated on first run
4. At least one Google Docs template document
5. The scripts installed

## Setup Steps

### 1. Create Google Cloud Project

If you already have a project (e.g., for Google Calendar), you can reuse it.

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Note the project name

### 2. Enable APIs

1. Go to **APIs & Services** > **Library**
2. Search for "Google Docs API" and click **Enable**
3. Search for "Google Drive API" and click **Enable**

Both APIs are required. The Drive API is needed to copy template documents.

### 3. Create OAuth Credentials

If you already have Desktop app credentials (e.g., for Calendar or gdocs-sync), you can reuse them.

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. Application type: **Desktop app**
4. Name: "Docs CLI" (or your preference)
5. Download the JSON file

**Note on scopes:** This skill requests full Drive access (`drive` scope, not `drive.file`) because it copies template documents that the OAuth app did not create. The consent screen will say "See, edit, create, and delete all of your Google Drive files." This broader scope is required for the template-copy workflow.

### 4. Install Credentials

```bash
# Create config directory
mkdir -p ~/.config/google-docs

# Move downloaded credentials
mv ~/Downloads/client_secret_*.json ~/.config/google-docs/credentials.json

# Set permissions
chmod 600 ~/.config/google-docs/credentials.json
```

### 5. Install Scripts

Copy the scripts from this skill directory to the config location:

```bash
cp gdocs_branded.py ~/.config/google-docs/
cp gdocs_auth.py ~/.config/google-docs/
```

### 6. Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

### 7. Authenticate

```bash
python3 ~/.config/google-docs/gdocs_auth.py
```

This opens a browser. Sign in with the Google account that owns (or has access to) your template documents. Grant Docs and Drive access.

### 8. Create Template Documents

Unlike `gdocs-sync` (which creates documents from scratch), `gdocs-branded` copies a template for each run. This preserves headers, footers, margins, and page setup that can't be set via the API.

**Quick start (blank template):**

1. Create a new Google Doc
2. Optionally set margins, headers, or footers
3. Copy the document ID from the URL: `https://docs.google.com/document/d/THIS_PART_IS_THE_ID/edit`

**Full branded template:**

1. Create a Google Doc with your organisation's header/footer (logo, page numbers, etc.)
2. Set page margins and orientation as desired
3. The body content doesn't matter — the script clears it before inserting
4. Copy the document ID from the URL

Create one template per brand. Each brand maps to a template ID.

### 9. Configure Templates

Create `~/.config/google-docs/templates.json`:

```json
{
  "editorial": {
    "template_id": "YOUR_TEMPLATE_ID_HERE",
    "name": "Editorial Template"
  },
  "corporate": {
    "template_id": "YOUR_TEMPLATE_ID_HERE",
    "name": "Corporate Template"
  }
}
```

Replace `YOUR_TEMPLATE_ID_HERE` with the actual document IDs from step 8. You only need entries for brands you plan to use.

### 10. Configure Custom Brands (Optional)

The script includes three built-in brands (`editorial`, `corporate`, `modern`). To add your own or override the defaults, create `~/.config/google-docs/brands.json`:

```json
{
  "my-brand": {
    "header_bg": {"red": 0.2, "green": 0.4, "blue": 0.8},
    "header_text": {"red": 1.0, "green": 1.0, "blue": 1.0},
    "body_color": {"red": 0.2, "green": 0.2, "blue": 0.2},
    "table_font": "Arial",
    "table_font_size": 10,
    "heading_styles": {
      "1": {"font": "Arial", "size": 24, "bold": true, "color": {"red": 0.2, "green": 0.4, "blue": 0.8}},
      "2": {"font": "Arial", "size": 18, "bold": true, "color": {"red": 0.2, "green": 0.4, "blue": 0.8}},
      "3": {"font": "Arial", "size": 14, "bold": true, "color": {"red": 0.2, "green": 0.4, "blue": 0.8}}
    },
    "body_font": {"font": "Arial", "size": 11, "color": {"red": 0.2, "green": 0.2, "blue": 0.2}}
  }
}
```

**Brand config fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `header_bg` | Yes | Table header row background colour (RGB 0.0-1.0) |
| `header_text` | Yes | Table header row text colour |
| `body_color` | Yes | Table data cell text colour |
| `table_font` | Yes | Font for table cells |
| `table_font_size` | Yes | Font size for table cells (PT) |
| `heading_styles` | Yes | Font, size, bold, colour per heading level (keys: `"1"`, `"2"`, `"3"`) |
| `body_font` | Yes | Font, size, colour for body paragraphs |
| `row_header_bg` | No | If set, first column of data rows gets this background colour |
| `body_spacing` | No | If set, overrides paragraph spacing inline: `{"space_above": 10, "line_spacing": 115}` |

**Notes:**
* Colours use Google Docs RGB fractions (0.0-1.0), not hex. Convert: divide each RGB component by 255
* Use [Google Fonts](https://fonts.google.com/) for reliable rendering in Google Docs
* `heading_styles` keys must be strings in JSON (`"1"`, `"2"`, `"3"`), not integers
* `body_spacing` is only needed if your template has 0pt paragraph spacing. Most templates have sensible defaults
* `row_header_bg` is optional — useful for tables where the first column contains row labels

### 11. Test

```bash
echo "# Test Report

This is a test paragraph with **bold** and *italic* text.

## Section One

* First bullet point
* Second bullet point
  * Nested bullet

| Header A | Header B |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
" > /tmp/test-branded.md

python3 ~/.config/google-docs/gdocs_branded.py \
    /tmp/test-branded.md \
    --brand editorial \
    --doc-id-file /tmp/test_branded_id.json \
    --title "Test Branded Doc"
```

Check the output URL — you should see a branded document with styled headings, formatted body text, bullet points, and a table with coloured headers.

## Multi-Machine Setup

**credentials.json** — Can be synced (your OAuth client config, not secret enough to worry about).

**token.json** — Syncing may work, but Google sometimes invalidates tokens used from multiple IPs. If you get auth errors on the second machine, re-run `gdocs_auth.py`.

**templates.json** — Can be synced. Template document IDs are stable.

**brands.json** — Can be synced. Brand configs are just styling preferences.

Safer approach: Keep all config files synced, but authenticate separately on each machine.

## AI Agent Instructions

When setting this up via Claude Code:

1. Cannot create Google Cloud project — user must do this
2. Cannot complete OAuth flow — requires browser
3. Can create the scripts and config files once credentials.json is in place
4. Can create templates.json once user provides template document IDs
5. Can run the branded doc generation once token.json exists

Tell the user: "Please create a Google Cloud project with Docs and Drive APIs enabled, download OAuth credentials, and create at least one template Google Doc. I can then set up the scripts and generate branded documents."

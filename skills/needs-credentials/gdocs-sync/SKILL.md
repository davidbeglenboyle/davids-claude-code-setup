---
name: gdocs-sync
description: |
  Sync Markdown files to Google Docs, preserving a stable URL. Use when:
  - User says "sync to Google Docs", "push to gdocs", "update the Google Doc"
  - User wants a Markdown file available at a permanent Google Docs URL
  - After generating a context file or report that should be accessible via Google Docs
  - User asks to "create a Google Doc" from a Markdown file

  Creates new Google Docs on first run, updates the same document on subsequent runs.
  The document ID is stored in a JSON file alongside the source, so the URL never changes.
---

# Google Docs Sync

Sync Markdown files to Google Docs with stable URLs. Creates on first run, updates on subsequent runs.

## Prerequisites

**First-time setup** (one-time only):
```bash
python3 ~/.config/google-docs/gdocs_auth.py
```
This opens a browser to authorise Google Docs access. See SETUP.md for details.

## Usage

### Basic Sync

```bash
python3 ~/.config/google-docs/gdocs_sync.py \
    "<markdown_file>" \
    "<doc_id_file>" \
    --title "<Document Title>"
```

**Arguments:**
- `markdown_file` — Path to the Markdown source
- `doc_id_file` — JSON file to store the Google Doc ID (create alongside the markdown file)
- `--title` — Title for new documents (ignored on updates)

### Example: Project Context File

```bash
python3 ~/.config/google-docs/gdocs_sync.py \
    "/path/to/project/summary/context.md" \
    "/path/to/project/summary/gdocs_id.json" \
    --title "Project Context"
```

**First run:** Creates Google Doc, saves ID to `gdocs_id.json`, outputs URL.
**Subsequent runs:** Updates same document, URL unchanged.

## Workflow Integration

When creating consolidated context files for projects:

1. Generate the Markdown context file
2. Sync to Google Docs
3. Store the URL in the project README
4. On future updates, regenerate context file and re-run sync

## Output

The script outputs:
- Status message (creating vs updating)
- The permanent Google Doc URL

Example:
```
Updating existing document: 1w5mHT-E0qLXYcyYfet8g3UswhVd9AQ41yo-bs_XZavk
✅ Document updated
📄 URL: https://docs.google.com/document/d/1w5mHT-E0qLXYcyYfet8g3UswhVd9AQ41yo-bs_XZavk/edit
```

## Troubleshooting

**"No token found"** — Run `python3 ~/.config/google-docs/gdocs_auth.py`

**"Document not found"** — The doc was deleted. Script will create a new one and update the ID file.

**Formatting issues** — The script converts basic Markdown (headers, bullets, tables). Complex formatting may simplify.

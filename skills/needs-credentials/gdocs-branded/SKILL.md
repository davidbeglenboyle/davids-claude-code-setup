---
name: gdocs-branded
description: |
  Generate branded Google Docs from Markdown with full formatting.
  Only use when the user explicitly asks to create a branded Google Doc,
  generate a Google Doc with branding, or says "branded gdoc".
---

# Branded Google Docs

Convert Markdown files into fully branded Google Docs with proper typography, colours, tables, and stable URLs.

## Prerequisites

First-time setup (one-time only):

```bash
python3 ~/.config/google-docs/gdocs_auth.py
```

This opens a browser to authorise Google Docs and Drive access. See SETUP.md for full instructions.

## Usage

```bash
python3 ~/.config/google-docs/gdocs_branded.py <markdown_file> --brand <name> [--doc-id-file gdocs_id.json] [--title "Title"]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `markdown_file` | Yes | Path to the Markdown source file |
| `--brand` | Yes | Brand name (built-in or custom) |
| `--doc-id-file` | No | JSON file to store/retrieve the Doc ID for stable URLs |
| `--title` | No | Document title (used on first create only) |
| `--folder-id` | No | Google Drive folder ID to create the doc in |

### Built-in Brands

| Brand | Headings | Body | Style |
|-------|----------|------|-------|
| `editorial` | Source Serif 4 (serif) | DM Sans 11pt | Elegant, warm tones |
| `corporate` | Arial (bold) | Arial 11pt | Clean with single accent colour |
| `modern` | Poppins (geometric) | Poppins 11pt | Contemporary with bold colours |

### Custom Brands

Create `~/.config/google-docs/brands.json` to add your own brands or override the defaults. See SETUP.md for the JSON schema.

## Examples

### Create a new branded document

```bash
python3 ~/.config/google-docs/gdocs_branded.py \
    report.md \
    --brand editorial \
    --doc-id-file report_id.json \
    --title "Q4 Strategy Report"
```

### Update the same document (stable URL)

```bash
python3 ~/.config/google-docs/gdocs_branded.py \
    report.md \
    --brand editorial \
    --doc-id-file report_id.json
```

The `--doc-id-file` stores the Google Doc ID on first run. Subsequent runs update the same document at the same URL.

## How It Works

1. Copies a brand-specific Google Docs template (preserving headers, footers, margins)
2. Clears the body content
3. Forces PAGES mode (prevents tables from overflowing page width)
4. Parses Markdown into structured blocks (headings, paragraphs, bullets, numbered lists, tables)
5. Inserts content via Google Docs API with inline brand-specific formatting
6. Styles tables with brand colours (header row background, text colours, fonts)

## Supported Markdown

* Headings (H1-H6)
* **Bold**, *italic*, ***bold+italic***
* Bullet lists (two nesting levels)
* Numbered lists (two nesting levels)
* Pipe-separated tables with header rows
* Page breaks (`===` on its own line)

## Known Limitations

* No images (Google Docs API can insert images but not from local paths)
* No code blocks (rendered as plain paragraphs)
* Table cells lose inline bold/italic markers (stripped to plain text)
* Horizontal rules (`---`) are skipped (use headings to separate sections)

## Troubleshooting

**"No token found"** — Run `python3 ~/.config/google-docs/gdocs_auth.py` to authenticate.

**"No template configured"** — Add the brand to `~/.config/google-docs/templates.json` with the template Google Doc ID.

**"Unknown brand"** — Check available brands with `--brand nonexistent` (error message lists all available brands).

**Tables too wide** — The script forces PAGES mode automatically. If tables still overflow, reduce column count or content length.

**Numbered lists restart at 1** — Ensure numbered items are contiguous in the Markdown (no blank lines between items).

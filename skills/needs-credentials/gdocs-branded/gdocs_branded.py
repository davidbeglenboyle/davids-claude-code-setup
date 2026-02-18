#!/usr/bin/env python3
"""
Generate branded Google Docs from Markdown.

Copies a brand-specific template Google Doc, clears the body,
and inserts content from a Markdown file with proper formatting:
headings, bold/italic, bullets, numbered lists, native tables,
and brand-coloured table headers.

Usage:
    python3 gdocs_branded.py <markdown_file> --brand editorial [--doc-id-file gdocs_id.json] [--title "Title"]

Arguments:
    markdown_file   Path to the Markdown source file
    --brand         Brand name (built-in: editorial, corporate, modern — or custom via brands.json)
    --doc-id-file   JSON file to store/retrieve the Google Doc ID (for stable URLs)
    --title         Title for the Google Doc (used on first create only)
"""

import os
import sys
import re
import json
import argparse
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CONFIG_DIR = os.path.expanduser("~/.config/google-docs")
TOKEN_PATH = os.path.join(CONFIG_DIR, "token.json")
TEMPLATES_PATH = os.path.join(CONFIG_DIR, "templates.json")
BRANDS_PATH = os.path.join(CONFIG_DIR, "brands.json")
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive',
]

# ---------------------------------------------------------------------------
# Default brand configurations — colours as Google Docs RGB fractions (0.0-1.0)
#
# These three brands demonstrate different typographic strategies:
#   editorial: serif headings + sans-serif body (elegant, warm)
#   corporate: single font family, bold accent colour (clean, professional)
#   modern:    geometric sans-serif with bold colour accents (contemporary)
#
# To add your own brands, create ~/.config/google-docs/brands.json
# (see SETUP.md for the schema). Custom brands override these defaults.
# ---------------------------------------------------------------------------

DEFAULT_BRANDS = {
    'editorial': {
        'header_bg': {'red': 0.059, 'green': 0.161, 'blue': 0.259},    # #0F2942
        'header_text': {'red': 1.0, 'green': 1.0, 'blue': 1.0},        # white
        'body_color': {'red': 0.239, 'green': 0.255, 'blue': 0.278},    # #3D4147
        'table_font': 'DM Sans',
        'table_font_size': 10,
        # Inline overrides ensure correct fonts regardless of template state
        'heading_styles': {
            1: {'font': 'Source Serif 4', 'size': 22, 'bold': False,
                'color': {'red': 0.059, 'green': 0.161, 'blue': 0.259}},    # #0F2942
            2: {'font': 'Source Serif 4', 'size': 18, 'bold': False,
                'color': {'red': 0.761, 'green': 0.478, 'blue': 0.361}},    # #C27A5C
            3: {'font': 'Source Serif 4', 'size': 13, 'bold': False,
                'color': {'red': 0.059, 'green': 0.161, 'blue': 0.259}},    # #0F2942
        },
        'body_font': {'font': 'DM Sans', 'size': 11,
                      'color': {'red': 0.239, 'green': 0.255, 'blue': 0.278}},  # #3D4147
        # Some templates have 0pt paragraph spacing — use body_spacing to override inline
        'body_spacing': {'space_above': 10, 'line_spacing': 115},
    },
    'corporate': {
        'header_bg': {'red': 0.004, 'green': 0.588, 'blue': 0.231},    # #01963B
        'header_text': {'red': 1.0, 'green': 1.0, 'blue': 1.0},        # white
        # Optional: first column of data rows gets a subtle background
        'row_header_bg': {'red': 0.886, 'green': 0.910, 'blue': 0.922}, # #E2E8EB
        'body_color': {'red': 0.314, 'green': 0.337, 'blue': 0.357},    # #50565B
        'table_font': 'Arial',
        'table_font_size': 10,
        'heading_styles': {
            1: {'font': 'Arial', 'size': 24, 'bold': True,
                'color': {'red': 0.004, 'green': 0.588, 'blue': 0.231}},    # #01963B
            2: {'font': 'Arial', 'size': 18, 'bold': True,
                'color': {'red': 0.004, 'green': 0.588, 'blue': 0.231}},    # #01963B
            3: {'font': 'Arial', 'size': 14, 'bold': True,
                'color': {'red': 0.004, 'green': 0.588, 'blue': 0.231}},    # #01963B
        },
        'body_font': {'font': 'Arial', 'size': 11,
                      'color': {'red': 0.314, 'green': 0.337, 'blue': 0.357}},  # #50565B
    },
    'modern': {
        'header_bg': {'red': 0.435, 'green': 0.141, 'blue': 0.420},    # #6F246B
        'header_text': {'red': 1.0, 'green': 1.0, 'blue': 1.0},        # white
        'body_color': {'red': 0.200, 'green': 0.200, 'blue': 0.200},    # #333333
        'table_font': 'Poppins',
        'table_font_size': 10,
        'heading_styles': {
            1: {'font': 'Poppins', 'size': 24, 'bold': True,
                'color': {'red': 0.200, 'green': 0.200, 'blue': 0.200}},    # #333333
            2: {'font': 'Poppins', 'size': 18, 'bold': False,
                'color': {'red': 0.435, 'green': 0.141, 'blue': 0.420}},    # #6F246B
            3: {'font': 'Poppins', 'size': 12, 'bold': False,
                'color': {'red': 0.733, 'green': 0.200, 'blue': 0.310}},    # #BB334F
        },
        'body_font': {'font': 'Poppins', 'size': 11,
                      'color': {'red': 0.200, 'green': 0.200, 'blue': 0.200}},  # #333333
    },
}


def load_brands():
    """Load brand configs: defaults merged with optional user overrides."""
    brands = dict(DEFAULT_BRANDS)

    if os.path.exists(BRANDS_PATH):
        with open(BRANDS_PATH) as f:
            custom = json.load(f)
        for name, config in custom.items():
            # Convert heading_styles keys from strings (JSON) to ints (Python)
            if 'heading_styles' in config:
                config['heading_styles'] = {
                    int(k): v for k, v in config['heading_styles'].items()
                }
            brands[name] = config

    return brands


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def get_credentials():
    """Load and refresh credentials."""
    if not os.path.exists(TOKEN_PATH):
        print(f"ERROR: No token found at {TOKEN_PATH}")
        print("Run: python3 ~/.config/google-docs/gdocs_auth.py")
        sys.exit(1)
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    return creds


def load_templates():
    """Load template doc IDs from config."""
    if not os.path.exists(TEMPLATES_PATH):
        print(f"ERROR: No templates config at {TEMPLATES_PATH}")
        print("Create templates.json with your brand template IDs.")
        print("See SETUP.md for instructions.")
        sys.exit(1)
    with open(TEMPLATES_PATH) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Markdown Parser
# ---------------------------------------------------------------------------

def parse_inline(text):
    """Parse bold and italic markers from text.

    Returns (plain_text, format_ranges) where format_ranges is a list of
    dicts with keys: start, end, bold, italic (offsets relative to plain_text).
    """
    ranges = []
    result = []
    i = 0
    pos = 0  # position in output string

    while i < len(text):
        # Bold+italic: ***text*** or ___text___
        if text[i:i+3] in ('***', '___'):
            marker = text[i:i+3]
            end = text.find(marker, i + 3)
            if end != -1:
                inner = text[i+3:end]
                ranges.append({'start': pos, 'end': pos + len(inner), 'bold': True, 'italic': True})
                result.append(inner)
                pos += len(inner)
                i = end + 3
                continue

        # Bold: **text** or __text__
        if text[i:i+2] in ('**', '__'):
            marker = text[i:i+2]
            end = text.find(marker, i + 2)
            if end != -1:
                inner = text[i+2:end]
                ranges.append({'start': pos, 'end': pos + len(inner), 'bold': True, 'italic': False})
                result.append(inner)
                pos += len(inner)
                i = end + 2
                continue

        # Italic: *text* or _text_ (but not ** or __)
        if text[i] in ('*', '_') and (i + 1 < len(text) and text[i+1] not in ('*', '_')):
            marker = text[i]
            end = text.find(marker, i + 1)
            if end != -1 and end > i + 1:
                inner = text[i+1:end]
                ranges.append({'start': pos, 'end': pos + len(inner), 'bold': False, 'italic': True})
                result.append(inner)
                pos += len(inner)
                i = end + 1
                continue

        result.append(text[i])
        pos += 1
        i += 1

    return ''.join(result), ranges


def parse_markdown(content):
    """Parse markdown content into a list of blocks.

    Each block is a dict with 'type' and type-specific fields:
    - heading: level, text, inline_formats
    - paragraph: text, inline_formats
    - bullet: text, inline_formats, level
    - numbered: text, inline_formats, level
    - table: rows (list of lists of strings), has_header (bool)
    - blank: (no extra fields)
    """
    blocks = []
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            blocks.append({'type': 'blank'})
            i += 1
            continue

        # Page break marker (===)
        if stripped == '===':
            blocks.append({'type': 'pagebreak'})
            i += 1
            continue

        # Horizontal rule — skip entirely (no dividers in branded docs)
        if stripped in ('---', '***', '___') and len(stripped) >= 3:
            i += 1
            continue

        # Headings
        heading_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if heading_match:
            level = len(heading_match.group(1))
            raw_text = heading_match.group(2).strip()
            plain, formats = parse_inline(raw_text)
            blocks.append({
                'type': 'heading',
                'level': level,
                'text': plain,
                'inline_formats': formats,
            })
            i += 1
            continue

        # Table (pipe-separated)
        if '|' in line and stripped.startswith('|'):
            table_rows = []
            while i < len(lines) and '|' in lines[i]:
                row = lines[i]
                # Skip separator rows (|---|---|)
                if not all(c in '|-: ' for c in row):
                    cells = [c.strip() for c in row.split('|')[1:-1]]
                    if cells:
                        table_rows.append(cells)
                i += 1

            if table_rows:
                blocks.append({
                    'type': 'table',
                    'rows': table_rows,
                    'has_header': len(table_rows) > 1,
                })
            continue

        # Bullet list
        bullet_match = re.match(r'^(\s*)[*\-]\s+(.*)', line)
        if bullet_match:
            indent = len(bullet_match.group(1))
            level = indent // 2  # 0 for top-level, 1 for indented
            raw_text = bullet_match.group(2).strip()
            plain, formats = parse_inline(raw_text)
            blocks.append({
                'type': 'bullet',
                'text': plain,
                'inline_formats': formats,
                'level': level,
            })
            i += 1
            continue

        # Numbered list
        numbered_match = re.match(r'^(\s*)\d+\.\s+(.*)', line)
        if numbered_match:
            indent = len(numbered_match.group(1))
            level = indent // 3
            raw_text = numbered_match.group(2).strip()
            plain, formats = parse_inline(raw_text)
            blocks.append({
                'type': 'numbered',
                'text': plain,
                'inline_formats': formats,
                'level': level,
            })
            i += 1
            continue

        # Regular paragraph
        plain, formats = parse_inline(stripped)
        blocks.append({
            'type': 'paragraph',
            'text': plain,
            'inline_formats': formats,
        })
        i += 1

    # Post-process: remove all blank blocks. Google Docs templates have
    # paragraph-level spacing (spaceAbove/spaceBelow on named styles), so
    # blank lines from markdown would double the gaps. This also keeps
    # numbered lists contiguous (preventing restart-at-1 bugs).
    cleaned = [b for b in blocks if b['type'] != 'blank']

    return cleaned


# ---------------------------------------------------------------------------
# Google Docs API Request Builders
# ---------------------------------------------------------------------------

def build_text_style_requests(base_index, text, inline_formats):
    """Build updateTextStyle requests for bold/italic ranges."""
    requests = []
    for fmt in inline_formats:
        style = {}
        fields = []
        if fmt.get('bold'):
            style['bold'] = True
            fields.append('bold')
        if fmt.get('italic'):
            style['italic'] = True
            fields.append('italic')
        if fields:
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': base_index + fmt['start'],
                        'endIndex': base_index + fmt['end'],
                    },
                    'textStyle': style,
                    'fields': ','.join(fields),
                }
            })
    return requests


def build_non_table_requests(blocks, start_index, brand_config=None):
    """Build API requests for non-table blocks.

    Returns (requests, formatting_requests, new_index, table_indices).
    - requests: insertText + paragraph style requests (applied immediately)
    - formatting_requests: text style requests (applied after all text is in)
    - new_index: the document index after all content
    - table_indices: list of (block_index, current_doc_index) for tables
    """
    requests = []
    format_requests = []
    table_positions = []
    # Deferred bullet/numbered list ranges — applied after all text is inserted
    # so contiguous items share a single list context
    bullet_ranges = []   # [(start_idx, end_idx)]
    numbered_ranges = []  # [(start_idx, end_idx)]
    idx = start_index
    heading_styles = (brand_config or {}).get('heading_styles')
    body_font = (brand_config or {}).get('body_font')
    body_spacing = (brand_config or {}).get('body_spacing')

    for bi, block in enumerate(blocks):
        btype = block['type']

        if btype == 'blank':
            requests.append({
                'insertText': {
                    'location': {'index': idx},
                    'text': '\n',
                }
            })
            idx += 1

        elif btype == 'pagebreak':
            # Insert a newline then a page break character
            requests.append({
                'insertText': {
                    'location': {'index': idx},
                    'text': '\n',
                }
            })
            idx += 1
            requests.append({
                'insertPageBreak': {
                    'location': {'index': idx},
                }
            })
            idx += 1

        elif btype == 'heading':
            text = block['text'] + '\n'
            requests.append({
                'insertText': {
                    'location': {'index': idx},
                    'text': text,
                }
            })
            level = min(block['level'], 6)
            style_map = {
                1: 'HEADING_1', 2: 'HEADING_2', 3: 'HEADING_3',
                4: 'HEADING_4', 5: 'HEADING_5', 6: 'HEADING_6',
            }
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': idx, 'endIndex': idx + len(text)},
                    'paragraphStyle': {'namedStyleType': style_map[level]},
                    'fields': 'namedStyleType',
                }
            })
            # Inline heading style override (for brands without named style config)
            if heading_styles and level in heading_styles:
                hs = heading_styles[level]
                format_requests.append({
                    'updateTextStyle': {
                        'range': {'startIndex': idx, 'endIndex': idx + len(text) - 1},
                        'textStyle': {
                            'weightedFontFamily': {'fontFamily': hs['font']},
                            'fontSize': {'magnitude': hs['size'], 'unit': 'PT'},
                            'bold': hs.get('bold', False),
                            'foregroundColor': {'color': {'rgbColor': hs['color']}},
                        },
                        'fields': 'weightedFontFamily,fontSize,bold,foregroundColor',
                    }
                })
            format_requests.extend(
                build_text_style_requests(idx, text, block.get('inline_formats', []))
            )
            idx += len(text)

        elif btype in ('paragraph',):
            text = block['text'] + '\n'
            requests.append({
                'insertText': {
                    'location': {'index': idx},
                    'text': text,
                }
            })
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': idx, 'endIndex': idx + len(text)},
                    'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT'},
                    'fields': 'namedStyleType',
                }
            })
            # Inline paragraph spacing override (for templates with 0pt spacing)
            if body_spacing:
                requests.append({
                    'updateParagraphStyle': {
                        'range': {'startIndex': idx, 'endIndex': idx + len(text)},
                        'paragraphStyle': {
                            'spaceAbove': {'magnitude': body_spacing['space_above'], 'unit': 'PT'},
                            'lineSpacing': body_spacing['line_spacing'],
                        },
                        'fields': 'spaceAbove,lineSpacing',
                    }
                })
            # Inline body font override
            if body_font:
                format_requests.append({
                    'updateTextStyle': {
                        'range': {'startIndex': idx, 'endIndex': idx + len(text) - 1},
                        'textStyle': {
                            'weightedFontFamily': {'fontFamily': body_font['font']},
                            'fontSize': {'magnitude': body_font['size'], 'unit': 'PT'},
                            'foregroundColor': {'color': {'rgbColor': body_font['color']}},
                        },
                        'fields': 'weightedFontFamily,fontSize,foregroundColor',
                    }
                })
            format_requests.extend(
                build_text_style_requests(idx, text, block.get('inline_formats', []))
            )
            idx += len(text)

        elif btype == 'bullet':
            text = block['text'] + '\n'
            requests.append({
                'insertText': {
                    'location': {'index': idx},
                    'text': text,
                }
            })
            # Defer createParagraphBullets — merge contiguous ranges later
            bullet_ranges.append((idx, idx + len(text)))
            # Inline paragraph spacing override (for templates with 0pt spacing)
            if body_spacing:
                requests.append({
                    'updateParagraphStyle': {
                        'range': {'startIndex': idx, 'endIndex': idx + len(text)},
                        'paragraphStyle': {
                            'spaceAbove': {'magnitude': body_spacing['space_above'], 'unit': 'PT'},
                            'lineSpacing': body_spacing['line_spacing'],
                        },
                        'fields': 'spaceAbove,lineSpacing',
                    }
                })
            # Handle nesting level
            if block.get('level', 0) > 0:
                requests.append({
                    'updateParagraphStyle': {
                        'range': {'startIndex': idx, 'endIndex': idx + len(text)},
                        'paragraphStyle': {
                            'indentStart': {'magnitude': 36 * (block['level'] + 1), 'unit': 'PT'},
                            'indentFirstLine': {'magnitude': 18 * (block['level'] + 1), 'unit': 'PT'},
                        },
                        'fields': 'indentStart,indentFirstLine',
                    }
                })
            if body_font:
                format_requests.append({
                    'updateTextStyle': {
                        'range': {'startIndex': idx, 'endIndex': idx + len(text) - 1},
                        'textStyle': {
                            'weightedFontFamily': {'fontFamily': body_font['font']},
                            'fontSize': {'magnitude': body_font['size'], 'unit': 'PT'},
                            'foregroundColor': {'color': {'rgbColor': body_font['color']}},
                        },
                        'fields': 'weightedFontFamily,fontSize,foregroundColor',
                    }
                })
            format_requests.extend(
                build_text_style_requests(idx, text, block.get('inline_formats', []))
            )
            idx += len(text)

        elif btype == 'numbered':
            text = block['text'] + '\n'
            requests.append({
                'insertText': {
                    'location': {'index': idx},
                    'text': text,
                }
            })
            # Defer createParagraphBullets — merge contiguous ranges later
            numbered_ranges.append((idx, idx + len(text)))
            # Inline paragraph spacing override (for templates with 0pt spacing)
            if body_spacing:
                requests.append({
                    'updateParagraphStyle': {
                        'range': {'startIndex': idx, 'endIndex': idx + len(text)},
                        'paragraphStyle': {
                            'spaceAbove': {'magnitude': body_spacing['space_above'], 'unit': 'PT'},
                            'lineSpacing': body_spacing['line_spacing'],
                        },
                        'fields': 'spaceAbove,lineSpacing',
                    }
                })
            if body_font:
                format_requests.append({
                    'updateTextStyle': {
                        'range': {'startIndex': idx, 'endIndex': idx + len(text) - 1},
                        'textStyle': {
                            'weightedFontFamily': {'fontFamily': body_font['font']},
                            'fontSize': {'magnitude': body_font['size'], 'unit': 'PT'},
                            'foregroundColor': {'color': {'rgbColor': body_font['color']}},
                        },
                        'fields': 'weightedFontFamily,fontSize,foregroundColor',
                    }
                })
            format_requests.extend(
                build_text_style_requests(idx, text, block.get('inline_formats', []))
            )
            idx += len(text)

        elif btype == 'table':
            # Record position — tables handled separately
            table_positions.append((bi, idx))
            # Reserve a newline placeholder (will be replaced by table)
            requests.append({
                'insertText': {
                    'location': {'index': idx},
                    'text': '\n',
                }
            })
            idx += 1

    # Merge contiguous bullet/numbered ranges into single createParagraphBullets calls
    # This ensures numbered lists increment (1, 2, 3) instead of restarting at 1
    def merge_contiguous(ranges):
        """Merge adjacent ranges into contiguous spans."""
        if not ranges:
            return []
        merged = [ranges[0]]
        for start, end in ranges[1:]:
            prev_start, prev_end = merged[-1]
            if start == prev_end:  # contiguous
                merged[-1] = (prev_start, end)
            else:
                merged.append((start, end))
        return merged

    for start, end in merge_contiguous(bullet_ranges):
        requests.append({
            'createParagraphBullets': {
                'range': {'startIndex': start, 'endIndex': end},
                'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE',
            }
        })

    for start, end in merge_contiguous(numbered_ranges):
        requests.append({
            'createParagraphBullets': {
                'range': {'startIndex': start, 'endIndex': end},
                'bulletPreset': 'NUMBERED_DECIMAL_ALPHA_ROMAN',
            }
        })

    return requests, format_requests, idx, table_positions


# ---------------------------------------------------------------------------
# Table Operations
# ---------------------------------------------------------------------------

def find_table_at_approx_index(doc, target_index):
    """Find a table in the document near the target index.

    Returns dict with: start_index, end_index, cell_indices (list of lists).
    """
    body = doc.get('body', {}).get('content', [])
    for element in body:
        if 'table' in element:
            start = element['startIndex']
            end = element['endIndex']
            if abs(start - target_index) <= 5:
                cell_indices = []
                for row in element['table'].get('tableRows', []):
                    row_cells = []
                    for cell in row.get('tableCells', []):
                        # Each cell has content with paragraphs
                        cell_content = cell.get('content', [])
                        if cell_content:
                            first_para = cell_content[0]
                            para_start = first_para.get('startIndex', 0)
                            row_cells.append(para_start)
                    cell_indices.append(row_cells)
                return {
                    'start_index': start,
                    'end_index': end,
                    'cell_indices': cell_indices,
                    'rows': len(cell_indices),
                    'cols': len(cell_indices[0]) if cell_indices else 0,
                }
    return None


def insert_and_populate_table(docs_service, doc_id, block, insert_index, brand_config):
    """Insert a table at insert_index, populate cells, apply brand styling.

    This performs multiple API calls:
    1. Delete the placeholder newline
    2. Insert the table structure
    3. Read back document to get cell indices
    4. Populate cells with text
    5. Apply header row styling
    """
    rows = block['rows']
    num_rows = len(rows)
    num_cols = max(len(r) for r in rows) if rows else 0

    if num_rows == 0 or num_cols == 0:
        return insert_index

    # Step 1: Delete the placeholder newline at insert_index
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': [{
            'deleteContentRange': {
                'range': {'startIndex': insert_index, 'endIndex': insert_index + 1}
            }
        }]}
    ).execute()

    # Step 2: Insert the table
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': [{
            'insertTable': {
                'rows': num_rows,
                'columns': num_cols,
                'location': {'index': insert_index},
            }
        }]}
    ).execute()

    # Step 3: Read back to get cell indices
    doc = docs_service.documents().get(documentId=doc_id).execute()
    table_info = find_table_at_approx_index(doc, insert_index)

    if not table_info:
        print(f"  WARNING: Could not find table at index {insert_index}")
        return insert_index + 10  # rough estimate

    # Step 4: Populate cells (REVERSE order to avoid index shifting)
    cell_requests = []
    for ri in range(num_rows - 1, -1, -1):
        row = rows[ri]
        for ci in range(min(num_cols, len(row)) - 1, -1, -1):
            cell_text = row[ci] if ci < len(row) else ''
            # Strip markdown bold markers from cell text
            cell_text = cell_text.replace('**', '')
            if cell_text and ri < len(table_info['cell_indices']) and ci < len(table_info['cell_indices'][ri]):
                cell_idx = table_info['cell_indices'][ri][ci]
                cell_requests.append({
                    'insertText': {
                        'location': {'index': cell_idx},
                        'text': cell_text,
                    }
                })

    if cell_requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': cell_requests}
        ).execute()

    # Step 5: Read back again to get updated indices for formatting
    doc = docs_service.documents().get(documentId=doc_id).execute()
    table_info = find_table_at_approx_index(doc, insert_index)
    if not table_info:
        return insert_index + 10

    # Step 6: Style header row (first row)
    style_requests = []

    # Header row background
    for ci in range(num_cols):
        style_requests.append({
            'updateTableCellStyle': {
                'tableRange': {
                    'tableCellLocation': {
                        'tableStartLocation': {'index': table_info['start_index']},
                        'rowIndex': 0,
                        'columnIndex': ci,
                    },
                    'rowSpan': 1,
                    'columnSpan': 1,
                },
                'tableCellStyle': {
                    'backgroundColor': {
                        'color': {'rgbColor': brand_config['header_bg']}
                    },
                    'paddingTop': {'magnitude': 4, 'unit': 'PT'},
                    'paddingBottom': {'magnitude': 4, 'unit': 'PT'},
                    'paddingLeft': {'magnitude': 5, 'unit': 'PT'},
                    'paddingRight': {'magnitude': 5, 'unit': 'PT'},
                },
                'fields': 'backgroundColor,paddingTop,paddingBottom,paddingLeft,paddingRight',
            }
        })

    # Data cell padding
    for ri in range(1, num_rows):
        for ci in range(num_cols):
            style_requests.append({
                'updateTableCellStyle': {
                    'tableRange': {
                        'tableCellLocation': {
                            'tableStartLocation': {'index': table_info['start_index']},
                            'rowIndex': ri,
                            'columnIndex': ci,
                        },
                        'rowSpan': 1,
                        'columnSpan': 1,
                    },
                    'tableCellStyle': {
                        'paddingTop': {'magnitude': 3, 'unit': 'PT'},
                        'paddingBottom': {'magnitude': 3, 'unit': 'PT'},
                        'paddingLeft': {'magnitude': 5, 'unit': 'PT'},
                        'paddingRight': {'magnitude': 5, 'unit': 'PT'},
                    },
                    'fields': 'paddingTop,paddingBottom,paddingLeft,paddingRight',
                }
            })

    # Row headers: first column of data rows gets subtle background (optional)
    if 'row_header_bg' in brand_config:
        for ri in range(1, num_rows):
            style_requests.append({
                'updateTableCellStyle': {
                    'tableRange': {
                        'tableCellLocation': {
                            'tableStartLocation': {'index': table_info['start_index']},
                            'rowIndex': ri,
                            'columnIndex': 0,
                        },
                        'rowSpan': 1,
                        'columnSpan': 1,
                    },
                    'tableCellStyle': {
                        'backgroundColor': {
                            'color': {'rgbColor': brand_config['row_header_bg']}
                        },
                    },
                    'fields': 'backgroundColor',
                }
            })

    # Header row text styling: white, bold, brand font
    # Need to find text ranges in header cells from the re-read document
    body_content = doc.get('body', {}).get('content', [])
    for element in body_content:
        if 'table' in element and element['startIndex'] == table_info['start_index']:
            header_row = element['table']['tableRows'][0]
            for cell in header_row.get('tableCells', []):
                for para in cell.get('content', []):
                    if 'paragraph' in para:
                        for elem in para['paragraph'].get('elements', []):
                            text_run = elem.get('textRun', {})
                            content = text_run.get('content', '')
                            if content.strip():
                                style_requests.append({
                                    'updateTextStyle': {
                                        'range': {
                                            'startIndex': elem['startIndex'],
                                            'endIndex': elem['endIndex'],
                                        },
                                        'textStyle': {
                                            'bold': True,
                                            'foregroundColor': {
                                                'color': {'rgbColor': brand_config['header_text']}
                                            },
                                            'weightedFontFamily': {
                                                'fontFamily': brand_config['table_font'],
                                            },
                                            'fontSize': {
                                                'magnitude': brand_config['table_font_size'],
                                                'unit': 'PT',
                                            },
                                        },
                                        'fields': 'bold,foregroundColor,weightedFontFamily,fontSize',
                                    }
                                })

            # Style data cell text with brand font
            for ri, table_row in enumerate(element['table']['tableRows'][1:], 1):
                for cell in table_row.get('tableCells', []):
                    for para in cell.get('content', []):
                        if 'paragraph' in para:
                            for elem in para['paragraph'].get('elements', []):
                                text_run = elem.get('textRun', {})
                                content = text_run.get('content', '')
                                if content.strip():
                                    style_requests.append({
                                        'updateTextStyle': {
                                            'range': {
                                                'startIndex': elem['startIndex'],
                                                'endIndex': elem['endIndex'],
                                            },
                                            'textStyle': {
                                                'foregroundColor': {
                                                    'color': {'rgbColor': brand_config['body_color']}
                                                },
                                                'weightedFontFamily': {
                                                    'fontFamily': brand_config['table_font'],
                                                },
                                                'fontSize': {
                                                    'magnitude': brand_config['table_font_size'],
                                                    'unit': 'PT',
                                                },
                                            },
                                            'fields': 'foregroundColor,weightedFontFamily,fontSize',
                                        }
                                    })
            break

    if style_requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': style_requests}
        ).execute()

    return table_info['end_index']


# ---------------------------------------------------------------------------
# Document Operations
# ---------------------------------------------------------------------------

def copy_template(drive_service, template_id, title, folder_id=None):
    """Copy a template Google Doc. Returns new doc ID."""
    body = {'name': title}
    if folder_id:
        body['parents'] = [folder_id]
    result = drive_service.files().copy(
        fileId=template_id, body=body, supportsAllDrives=True
    ).execute()
    return result['id']


def clear_body(docs_service, doc_id):
    """Delete all body content from a document (preserving headers/footers)."""
    doc = docs_service.documents().get(documentId=doc_id).execute()
    body_content = doc.get('body', {}).get('content', [])
    if not body_content:
        return

    end_index = body_content[-1]['endIndex'] - 1
    if end_index > 1:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': [{
                'deleteContentRange': {
                    'range': {'startIndex': 1, 'endIndex': end_index}
                }
            }]}
        ).execute()


def ensure_pages_mode(docs_service, doc_id):
    """Force document to PAGES mode (not pageless).

    Pageless mode allows tables to extend beyond page width, making them
    unreadable. This ensures all branded documents use traditional pagination.
    """
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': [{
            'updateDocumentStyle': {
                'documentStyle': {
                    'documentFormat': {'documentMode': 'PAGES'}
                },
                'fields': 'documentFormat',
            }
        }]}
    ).execute()


def populate_document(docs_service, doc_id, blocks, brand_config):
    """Insert parsed markdown blocks into a cleared document."""
    # Separate tables from other blocks
    table_block_indices = [i for i, b in enumerate(blocks) if b['type'] == 'table']

    if not table_block_indices:
        # Simple case: no tables, single batch
        requests, format_requests, _, _ = build_non_table_requests(blocks, 1, brand_config)
        if requests:
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
        if format_requests:
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': format_requests}
            ).execute()
        return

    # Complex case: process in segments around tables
    # Split blocks into segments: [non-table, table, non-table, table, ...]
    segments = []
    prev = 0
    for ti in table_block_indices:
        if ti > prev:
            segments.append(('text', blocks[prev:ti]))
        segments.append(('table', blocks[ti]))
        prev = ti + 1
    if prev < len(blocks):
        segments.append(('text', blocks[prev:]))

    current_index = 1

    for seg_type, seg_data in segments:
        if seg_type == 'text':
            requests, format_requests, new_idx, _ = build_non_table_requests(seg_data, current_index, brand_config)
            if requests:
                docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': requests}
                ).execute()
            if format_requests:
                docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': format_requests}
                ).execute()
            current_index = new_idx
        else:
            # Table
            print(f"  Inserting table ({len(seg_data['rows'])} rows x {max(len(r) for r in seg_data['rows'])} cols)...")
            # Insert a placeholder newline for the table
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': [{
                    'insertText': {
                        'location': {'index': current_index},
                        'text': '\n',
                    }
                }]}
            ).execute()
            end_idx = insert_and_populate_table(
                docs_service, doc_id, seg_data, current_index, brand_config
            )
            current_index = end_idx

    # Format requests applied per-segment above (before table insertions shift indices)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Generate branded Google Docs from Markdown')
    parser.add_argument('markdown_file', help='Path to Markdown file')
    parser.add_argument('--brand', required=True,
                        help='Brand name (built-in: editorial, corporate, modern — or custom)')
    parser.add_argument('--doc-id-file', help='JSON file to store/retrieve Doc ID (for stable URLs)')
    parser.add_argument('--title', default='Branded Document', help='Document title')
    parser.add_argument('--folder-id', help='Google Drive folder ID to create the doc in')
    args = parser.parse_args()

    # Load brands (built-in defaults + optional user overrides)
    brands = load_brands()

    if args.brand not in brands:
        available = ', '.join(sorted(brands.keys()))
        print(f"ERROR: Unknown brand '{args.brand}'")
        print(f"Available brands: {available}")
        print(f"\nTo add custom brands, create {BRANDS_PATH}")
        sys.exit(1)

    brand_config = brands[args.brand]

    # Read markdown
    with open(args.markdown_file, 'r') as f:
        content = f.read()

    # Parse
    print(f"Parsing markdown ({len(content)} chars)...")
    blocks = parse_markdown(content)
    table_count = sum(1 for b in blocks if b['type'] == 'table')
    print(f"  {len(blocks)} blocks, {table_count} tables")

    # Auth and services
    creds = get_credentials()
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    # Load templates
    templates = load_templates()
    template_id = templates.get(args.brand, {}).get('template_id')
    if not template_id:
        print(f"ERROR: No template configured for brand '{args.brand}'")
        print(f"Add an entry for '{args.brand}' in {TEMPLATES_PATH}")
        sys.exit(1)

    # Check for existing doc
    doc_id = None
    if args.doc_id_file and os.path.exists(args.doc_id_file):
        with open(args.doc_id_file) as f:
            data = json.load(f)
            doc_id = data.get('doc_id')

    try:
        if doc_id:
            # Update existing doc
            print(f"Updating existing document: {doc_id}")
            clear_body(docs_service, doc_id)
        else:
            # Copy template
            print(f"Copying {args.brand} template...")
            folder_id = getattr(args, 'folder_id', None)
            doc_id = copy_template(drive_service, template_id, args.title, folder_id=folder_id)
            print(f"  New doc: {doc_id}")
            clear_body(docs_service, doc_id)

            # Save doc ID if file specified
            if args.doc_id_file:
                with open(args.doc_id_file, 'w') as f:
                    json.dump({'doc_id': doc_id, 'title': args.title, 'brand': args.brand}, f, indent=2)

        # Force pages mode (pageless mode makes tables too wide)
        ensure_pages_mode(docs_service, doc_id)

        # Populate
        print("Inserting content...")
        populate_document(docs_service, doc_id, blocks, brand_config)

        url = f"https://docs.google.com/document/d/{doc_id}/edit"
        print(f"\nDone: {url}")

    except HttpError as e:
        if e.resp.status == 404 and doc_id:
            print(f"Document {doc_id} not found. Creating new...")
            folder_id = getattr(args, 'folder_id', None)
            doc_id = copy_template(drive_service, template_id, args.title, folder_id=folder_id)
            clear_body(docs_service, doc_id)
            ensure_pages_mode(docs_service, doc_id)
            populate_document(docs_service, doc_id, blocks, brand_config)
            if args.doc_id_file:
                with open(args.doc_id_file, 'w') as f:
                    json.dump({'doc_id': doc_id, 'title': args.title, 'brand': args.brand}, f, indent=2)
            print(f"\nDone: https://docs.google.com/document/d/{doc_id}/edit")
        else:
            raise


if __name__ == '__main__':
    main()

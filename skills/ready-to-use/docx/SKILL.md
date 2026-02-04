---
name: docx
description: "Convert a markdown file to a Word document using a template."
license: MIT
---

# Word Document Generation Skill

## Overview

This skill converts Markdown files to professionally formatted Word documents using branded templates. It automatically selects the appropriate template based on project context.

## Template Selection Logic

| Context | Template | Notes |
|---------|----------|-------|
| Client project | Client-specific template | When working directory indicates a specific client |
| Default | Your standard template | For general work |

### Template Location

Store your templates in a consistent location:

```
~/templates/                        # Or your preferred location
├── Default Template.docx           # Your standard template
└── Client A Template.docx          # Client-specific templates
```

**Tip:** Update the `TEMPLATES_DIR` path below to match your setup.

---

## Template Styles (Example)

Your template should define these styles with your preferred fonts and colours.

### Typography (Example)

| Style | Font | Size | Notes |
|-------|------|------|-------|
| Title | Your Brand Font | 72pt | Bold, centered |
| Heading 1 | Your Brand Font | 24pt | Bold |
| Heading 2 | Your Brand Font | 18pt | Accent colour |
| Heading 3 | Your Brand Font | 12pt | Secondary colour |
| Normal | Your Body Font | 11pt | Body text |

---

## Using with python-docx

When generating Word documents programmatically, **load the template** rather than creating from scratch. The template's built-in styles preserve your fonts and brand colours.

### Basic Template Usage

```python
from docx import Document
from pathlib import Path

# UPDATE THIS PATH to your templates location
TEMPLATES_DIR = Path.home() / "templates"

def get_template(project_path=None):
    """Return appropriate template path based on project context."""
    # Add your own logic here to select client-specific templates
    # Example: check for client name in project path
    return TEMPLATES_DIR / "Default Template.docx"

# Load template
template_path = get_template()
doc = Document(template_path)

# Clear existing content (template may have placeholder text)
doc._body.clear_content()
```

### Applying Styles

When using the template, apply styles by name. The template defines these styles with correct fonts and colours.

```python
# Title (uses template's Title style)
doc.add_heading('Document Title', level=0)

# Heading 1
doc.add_heading('I. Executive Summary', level=1)

# Heading 2
doc.add_heading('A. Key Findings', level=2)

# Heading 3
doc.add_heading('1. First Finding', level=3)

# Normal body text
doc.add_paragraph('Body text uses the Normal style.')
```

### Important Notes

1. **Always load the template** — don't create `Document()` without arguments
2. **Clear content before adding** — templates may have placeholder text
3. **Use `level=0` for title** — this applies the Title style
4. **Styles are pre-defined** — no need to manually set fonts or colours

---

## Using with pandoc

For Markdown to Word conversion, use pandoc with the `--reference-doc` flag:

```bash
pandoc input.md -o output.docx \
  --reference-doc="~/templates/Default Template.docx"
```

This preserves template styles for headings, body text, and other elements.

---

## Client-Specific Templates

For client projects with specific branding requirements:

1. Create a separate template with the client's fonts and colours
2. Store in your templates directory
3. Update `get_template()` logic to detect and select the right template

Consider creating a separate skill (e.g., `client-docx`) with detailed brand guidelines if a client has complex requirements.

---

## File Naming

When creating deliverables, use professional naming:
- Use proper capitalisation with spaces
- Include date in brackets at the end
- Format: `Descriptive Name (21st Jan 2026).docx`

Example: `Q1 Sales Report (21st Jan 2026).docx`

---

## Dependencies

- **python-docx**: `pip install python-docx` — for programmatic generation
- **pandoc**: `brew install pandoc` — for Markdown conversion

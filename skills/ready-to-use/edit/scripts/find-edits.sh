#!/bin/bash
# Find all {instruction} markers in markdown files
# Usage: find-edits.sh [file|directory]
#
# Outputs: filepath:line_number:{instruction content}
# Skips: empty braces {}, braces inside code blocks
#
# Examples:
#   find-edits.sh draft.md           # Single file
#   find-edits.sh ./posts/           # Directory
#   find-edits.sh                    # Current directory

set -euo pipefail

TARGET="${1:-.}"

# Use ripgrep if available, fall back to grep
if command -v rg &> /dev/null; then
    # ripgrep: faster, respects .gitignore
    # Pattern: {content} where content is non-empty and doesn't contain }
    # --type md limits to markdown files
    # -n shows line numbers
    # --no-heading groups by file
    if [[ -f "$TARGET" ]]; then
        # Single file mode
        rg -n '\{[^}]+\}' "$TARGET" 2>/dev/null | head -50 || true
    else
        # Directory mode
        rg -n '\{[^}]+\}' --type md "$TARGET" 2>/dev/null | head -50 || true
    fi
else
    # Fallback to grep
    if [[ -f "$TARGET" ]]; then
        grep -n '{[^}]\+}' "$TARGET" 2>/dev/null | head -50 || true
    else
        find "$TARGET" -name "*.md" -type f -exec grep -Hn '{[^}]\+}' {} \; 2>/dev/null | head -50 || true
    fi
fi

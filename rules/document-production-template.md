# Document Production

## Generation Recipes

* Word documents: use pandoc with `--reference-doc` for consistent styling
* DocX to PDF: use LibreOffice headless: `soffice --headless --convert-to pdf --outdir [dir] [file.docx]`
* Content-first for presentations: iterate on markdown, generate visuals only after approval
* The markdown file is the "source of truth" for presentation content

## Approval Workflow

* Square bracket `[approval]` workflow for sensitive documents: mark uncertain/pending items with brackets, user approves, then remove
* Use `quality-score` to check for unresolved brackets before sharing

<!--
Add your own brand-specific patterns here. Examples:
* Client brand guidelines (colours, fonts, templates)
* Excel handoff tools: use formulas (VLOOKUP, COUNTIFS) so recipients can add data interactively
-->

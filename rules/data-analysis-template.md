# Data Analysis Patterns

## Workflow Principles

* Validate scaling/threshold assumptions with spot-checks before proceeding
* Explicitly document limitations and caveats in reports
* CSV files: inspect structure first; column names may be misleading
* Volume metrics: prefer absolute counts over shares (shares confound with denominator changes)
* File/entity matching: use case-insensitive comparison by default
* Processed data: include Source column for provenance (official/estimated/calculated)
* Data structure verification: run 3-4 Python one-liners (type(), keys(), sample values) before coding against assumed JSON/API structure
* Never synthesize or impute data silently: fabricated data is worse than gaps. If synthesis is unavoidable, label explicitly

## Data Hoarding

Err heavily on the side of keeping data. The cost of re-fetching (rate limits, API changes, pages disappearing) far exceeds the cost of storage:

* Save full/raw API responses alongside any processed outputs
* Save web search results and fetched page content to project folders
* Never discard fields, rows, or files during extraction; filter at query time, not at collection time
* When updating a dataset, save the previous version (date-suffixed) before overwriting

## Processing Patterns

* Batch by size not count: group by KB target (40-50KB) for content-heavy files
* Manifest-before-execute: generate reviewable manifest → get approval → execute from manifest
* Multi-angle verification: check count, size, structure, sample content, dates, provenance
* Long API batch jobs: save results after each item/segment, not at the end

## Python Environment Strategy

* **Tool packages** (pandas, requests): `pip3 install --user` — globally available
* **CLI tools** (black, ruff): `pipx install` — isolated but global
* **Project venvs**: Only when project has specific version requirements or conflicts
* **Decision test**: Before creating a venv, ask "Will this project need different versions than other projects?"

<!--
Add your own patterns here as you learn them. Examples:
* API-specific pagination quirks
* Database query patterns
* Visualisation style conventions
-->

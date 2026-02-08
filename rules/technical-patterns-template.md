# Technical Patterns

## General

* Prefer reusable scripts over one-off operations; save alongside outputs
* Long-running scripts: implement progress tracking and resume capability
* Pausable projects: README must include status, resume commands, and next steps
* HTTP clients: add per-request timeouts (30s) to prevent indefinite hangs
* Complex shell operations: write to /tmp/*.sh and execute with bash to avoid quoting issues
* Dynamic file discovery: never hardcode dates in paths; use sorted glob to find latest file

## File Operations

* Deletion safety: verify duplicates with signature comparison (filename + size) before any deletion
* Duplicate handling: merge unique files to destination before deleting source
* Deduplication: use filename + size as signature (faster than hashing, sufficient for personal archives)
* Version before overwrite: save the old version with a date suffix before writing the new one

## Sub-Agents

* Sub-agent output: write to individual files (resumable, auditable) rather than returning text in memory
* Sub-agents: use Write tool for file creation (auto-approved), not Bash heredocs (requires permission)
* Long-running tasks (1+ hours): send hourly progress updates with counts, percentages, and ETAs
* Verify agent reports: exploration agents may report incorrect details; always verify with direct tools
* Large files (100KB+) may fail or timeout via sub-agents — use direct bash instead

## Cloud Sync

<!--
If you use Dropbox/iCloud for development, add patterns here:
* High-volume small files (.venv, node_modules, .git) cause sync storms
* The `.nosync` suffix excludes files from Dropbox/iCloud sync
* Symlink pattern: `.venv.nosync` + symlink to `.venv`
* Use `trash` command instead of `rm -rf` for synced folders
-->

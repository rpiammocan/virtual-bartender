# Milestone 11 — Export, Backup & Restore

Implemented:

## Recipe export
- Markdown (.md)
- Plain text (.txt)
- human-readable ingredient and instruction formatting
- source/provenance included when available
- existing browser print remains supported

## Backups
- manual Backup Now
- SQLite online backup API for consistent copies
- versioned ZIP backup format
- manifest.json inside each backup
- backup history stored in the app database
- keeps the 10 most recent backups
- daily scheduled local backup thread
- backup UI in Settings

## Restore
- restore from a listed local backup
- explicit confirmation in UI
- creates a pre-restore safety copy first
- validates backup version/manifest
- advises backend restart after restore

Notes:
- automatic backups are local to the configured backups directory
- backup scheduling is intentionally simple for V1 and can later move to CasaOS/cron if desired

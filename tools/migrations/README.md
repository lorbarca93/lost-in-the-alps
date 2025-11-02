# Migration Scripts

One-off helpers that evolve the SQLite schema. Each script should be
idempotent and safe to re-run.

- `migrate_database.py` – adds detailed boudy.info columns introduced in
  late 2025.

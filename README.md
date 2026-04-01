# School Bookstore - Inventory System

## Course Subject
Human Computer Interaction 2

## Educational Disclaimer
This project is an educational and student-focused system for learning Human Computer Interaction and software development practices.
It is designed for school demonstration and internal operations, not public internet deployment.

## Quick Overview
This system helps a school bookstore manage:
- products (books, supplies, uniforms, exclusive materials)
- suppliers
- stock adjustments and low-stock alerts
- sales and purchase transactions
- role-based user access (admin/staff)
- reports (sales, inventory, stock movements, cashflow, profitability, audit)

## What Has Been Added
- Product sorting and Excel export.
- Supplier management and supplier-linked purchases.
- Finance tracking: cash ledger, opening balance setup, cashflow and profitability reports.
- Historical sale cost snapshots for better COGS reporting.
- Dashboard finance KPIs (available cash, COGS, gross profit, gross margin).
- Datetime cleanup to UTC-aware timestamps.
- One-time legacy timestamp normalization script: `scripts/normalize_legacy_utc_timestamps.py`.
- Backup and restore operating procedure for SQLite.

## Setup After Cloning (School Computer)
### Requirements
- Windows computer (recommended for this setup guide)
- Python 3.10+ installed
- Git installed
- Internet connection on first run (for dependency download)

### Steps
1. Clone the repository:
  ```bash
  git clone <your-repository-url>
  ```
2. Open terminal inside the project folder:
  ```bash
  cd inventory-system
  ```
3. Run the startup script:
  ```bash
  python start.py
  ```
4. Open browser:
  ```
  http://127.0.0.1:5000
  ```

### What `python start.py` does
- Creates `.venv` if missing.
- Installs/updates dependencies from `requirements.txt`.
- Ensures the `instance/` folder exists.
- Starts the Flask app on port 5000.

## Default Accounts (if fresh DB is auto-created)
- Admin: username `admin`, password `admin123`
- Staff: username `staff`, password `staff123`

## First-Run Fallback
If `instance/inventory.db` is missing, the app auto-creates tables and seeds default users/categories.

## Shared Database Note (Team Demo Setup)
This repository currently tracks `instance/inventory.db` so teammates can share the same demo data state.
Avoid editing DB-heavy data in multiple branches at the same time to reduce merge conflicts.

## Backup and Restore (SQLite)
This project uses local SQLite at `instance/inventory.db`.

### Backup Procedure
1. Stop the app (`CTRL + C` in terminal).
2. Copy DB with a timestamped filename:
  ```bash
  copy instance\inventory.db instance\inventory.db.backup-YYYY-MM-DD-HH-MM-SS
  ```
3. Start app again when done.

### Restore Procedure
1. Stop the app (`CTRL + C`).
2. Replace active DB from backup:
  ```bash
  copy /Y instance\inventory.db.backup-YYYY-MM-DD-HH-MM-SS instance\inventory.db
  ```
3. Start app:
  ```bash
  python start.py
  ```

### Factory Reset
1. Stop app.
2. Delete `instance/inventory.db`.
3. Run `python start.py` to reinitialize schema and default records.

### Post-Restore Checks
- Login works.
- Dashboard loads.
- Products and transactions pages load.

Important: always stop the app before backup/restore to avoid SQLite lock/corruption risk.

## Additional Documentation
- [System Usage Guide and Strict Rules](SYSTEM_USAGE_GUIDE_AND_RULES.md)
- [System Development and Technical Overview](SYSTEM_DEVELOPMENT_OVERVIEW.md)

## Project Structure (Quick Map)
- `app/routes/` - route handlers
- `app/templates/` - HTML templates
- `app/static/` - CSS, JS, images
- `app/models.py` - database models
- `run.py` - Flask entry point
- `start.py` - one-command setup and run
- `scripts/normalize_legacy_utc_timestamps.py` - one-time timestamp normalization utility

## Troubleshooting
- Python not found: reinstall Python and enable Add Python to PATH.
- Pip install fails: run `python -m pip install --upgrade pip`, then rerun `python start.py`.
- Port already in use: stop process using port 5000, then run `python start.py` again.
- ModuleNotFoundError after pull: rerun `python start.py`; if still failing, delete `.venv` then rerun `python start.py`.

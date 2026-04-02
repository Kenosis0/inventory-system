# School Bookstore Inventory System

## Course Subject
Human Computer Interaction 2

## Educational Scope
This project is an educational inventory and transaction management system designed for school bookstore operations. It is intended for classroom demonstration, team review, and internal school workflow simulation.

It is not intended for direct public internet deployment in its current form.

## What the System Covers
The application supports end-to-end bookstore operations:

- product and stock management
- supplier management
- sale and purchase transactions
- stock movement traceability
- role-based access (admin/staff)
- finance tracking through cash ledger
- reporting (sales, inventory, stock movements, cashflow, profitability, audit)

## Recent Project Updates
Recent iterations focused on usability, especially mobile-first operation and clearer visual reporting.

### Mobile UX improvements
- mixed responsive strategy: card layouts where identity and actions matter, priority-column tables where numeric comparison matters
- compact mobile rows with expandable metadata/actions
- hybrid mobile navigation (bottom app bar + drawer menu)
- additional bottom spacing fixes to prevent pagination/content overlap with fixed mobile navigation
- mobile dashboard compaction (primary KPIs first, secondary finance KPIs in expandable section)
- quick action area compressed for smaller screens

### Visual analytics improvements
- Chart.js-powered infographic cards on dashboard and key report pages
- chart data is generated server-side and passed as template JSON arrays
- chart density intentionally limited per page to avoid mobile overload

### Financial and data integrity enhancements
- cash ledger with running balance and opening balance setup
- historical COGS support via `unit_cost_at_sale` snapshots on sale items
- UTC timestamp normalization utility for legacy records

## Tech Stack
- Backend: Flask
- Data access: SQLAlchemy / Flask-SQLAlchemy
- Auth/session: Flask-Login
- Form security: Flask-WTF CSRF
- Frontend: Jinja templates, CSS, vanilla JavaScript
- Charts: Chart.js (CDN)
- Export: openpyxl
- Testing: pytest

## Project Structure
- `app/routes/` - feature route modules
- `app/templates/` - HTML templates
- `app/static/` - CSS, JS, image assets
- `app/models.py` - database schema and relationships
- `run.py` - Flask run entrypoint
- `start.py` - setup-and-run helper script
- `scripts/normalize_legacy_utc_timestamps.py` - one-time timestamp normalization utility

## Setup After Cloning

### Requirements
- Python 3.10+
- Git
- Internet connection for first dependency install

### Quick start
1. Clone repository.
2. Open terminal in project root.
3. Run:

```bash
python start.py
```

4. Open browser:

```text
http://127.0.0.1:5000
```

### What `python start.py` does
- creates `.venv` if missing
- installs dependencies from `requirements.txt` when needed
- ensures `instance/` exists
- starts the Flask application

## Default Accounts (Fresh Database)
- Admin: `admin` / `admin123`
- Staff: `staff` / `staff123`

On first run with no existing database, tables and baseline records are automatically created.

## Database and Backup Notes
The project uses local SQLite at `instance/inventory.db`.

### Backup
1. Stop app (`CTRL + C`).
2. Copy database file with timestamp:

```bash
copy instance\inventory.db instance\inventory.db.backup-YYYY-MM-DD-HH-MM-SS
```

### Restore
1. Stop app.
2. Restore database from backup:

```bash
copy /Y instance\inventory.db.backup-YYYY-MM-DD-HH-MM-SS instance\inventory.db
```

3. Start app again with `python start.py`.

Important: always stop the application before backup/restore to avoid SQLite file lock or corruption risk.

## Additional Documentation
- [System Usage Guide and Rules](SYSTEM_USAGE_GUIDE_AND_RULES.md)
- [System Development Overview](SYSTEM_DEVELOPMENT_OVERVIEW.md)

## Troubleshooting
- `python` not found: reinstall Python and enable PATH option.
- dependency errors after pull: rerun `python start.py`.
- virtual environment corruption: delete `.venv` and rerun `python start.py`.
- port 5000 in use: stop conflicting process and restart.

## Current Scope Limits
- SQLite is best for local or low-concurrency scenarios.
- deployment profile is currently optimized for development and academic demo use.
- production migration/deployment hardening is planned as future work.
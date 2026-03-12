# Inventory System (School Bookstore)

## Educational Disclaimer
This project is an **educational/student project** for learning Human-Computer Interaction and software development practices.
It is not designed for production or commercial deployment.

## Quick Project Overview
This system helps a school bookstore manage:
- products (books, supplies, uniforms, exclusive materials)
- stock adjustments and low-stock checks
- sales and purchase transactions
- user roles (admin/staff)
- reports (sales, inventory, stock movements, audit)

## What You Need
- Python 3.10+ installed
- Git installed

That is all.

## Super Easy Run (for everyone)
1. Download or clone this project.
2. Open a terminal inside the project folder.
3. Run:
   ```bash
   python start.py
   ```
4. Wait until you see the server start message.
5. Open your browser to:
   ```
   http://127.0.0.1:5000
   ```

That command automatically:
- creates `.venv` if missing
- installs requirements
- prepares `instance/`
- starts the Flask app

## Shared Database (1:1 Team Setup)
This repository tracks `instance/inventory.db` so teammates can clone the **same current database state**.

Meaning:
- if you commit database updates, teammates can pull and get the same data
- if they add data, they can commit/push that updated database for others
- everyone can stay in sync at a 1:1 state using normal Git pull/push workflow

### Important Team Note
Because the database is a single file, avoid editing it at the same time in different branches to reduce merge conflicts.

## Daily Use
- Start app anytime:
  ```bash
  python start.py
  ```
- Stop app:
  - press `CTRL + C` in the terminal

## First-Run Fallback
If `instance/inventory.db` is missing, the app creates tables and seeds default starter records automatically.

## Project Structure (quick map)
- `app/routes/` - route handlers
- `app/templates/` - HTML templates
- `app/static/` - CSS, JS, images
- `app/models.py` - database models
- `run.py` - Flask entry point
- `start.py` - one-command setup + run

## Troubleshooting
- **python not found**: reinstall Python and check "Add Python to PATH"
- **pip install fails**: run `python -m pip install --upgrade pip` then `python start.py`
- **port already in use**: close other app using port 5000, then run `python start.py` again

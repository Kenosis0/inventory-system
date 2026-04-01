# School Bookstore - Inventory System

## Course Subject
Human Computer Interaction 2

## Document Purpose
This document explains the full development and implementation of the system, including architecture, features, scripts, and major functionality delivered.

## 1. Project Summary
School Bookstore - Inventory System is a Flask-based web application designed for private school premises operations. It manages inventory, sales, purchases, users, suppliers, stock history, financial tracking, and reporting.

Primary objectives:
- Centralize bookstore operations.
- Improve stock visibility and reduce stockouts.
- Track transactions and audit key changes.
- Provide role-based controls and reporting for admin/staff users.

## 2. Development Approach
- Methodology: Agile (4 sprint progression with post-sprint enhancements).
- Scope: Internal school use and demonstration.
- Database: SQLite for simplicity and portability.
- Testing strategy: Pytest suite with route/model/behavior coverage.

## 3. Technology Stack
- Backend: Flask
- ORM: SQLAlchemy + Flask-SQLAlchemy
- Authentication: Flask-Login
- Security: Flask-WTF CSRF protection
- Frontend: HTML/CSS/Vanilla JS with Jinja templates
- Reporting export: openpyxl (Excel)
- Testing: pytest

## 4. System Architecture
The system follows a clear layered structure:
- Presentation layer: Jinja templates and static assets.
- Application layer: Flask blueprints in `app/routes/`.
- Data layer: SQLAlchemy models in `app/models.py`.

Core blueprints:
- auth: login/logout
- main: dashboard
- products: inventory catalog and stock controls
- transactions: sales and purchases
- users: user account administration
- suppliers: supplier records
- reports: operational, financial, and audit reporting

## 5. Data Model and Core Entities
Key entities:
- User: authentication, role, account status, last login.
- Category: product grouping.
- Product: SKU, pricing, quantity, reorder thresholds.
- Supplier: procurement source details.
- Transaction: sale/purchase header record.
- TransactionItem: line items including sale-time cost snapshot.
- StockMovement: signed stock delta audit trail.
- CashLedger: running balance for finance monitoring.
- AuditLog: system activity trace.

## 6. Functional Modules
### 6.1 Authentication and RBAC
- Login/logout flow.
- Admin/staff access restrictions with decorators.
- Account activation/deactivation logic.

### 6.2 Product and Inventory Management
- Product create/view/edit/deactivate.
- Search, filter, pagination, and sorting.
- Stock adjustment with reason tracking.
- Low-stock detection and alert display.

### 6.3 Transactions
- Multi-item sale transactions with stock-out validation.
- Multi-item purchase transactions with supplier linkage.
- Automatic stock updates and movement records.
- Reference number generation with UUID suffix.

### 6.4 Supplier Management
- Admin-managed supplier CRUD.
- Supplier linkage to purchase transactions.
- Supplier-aware transaction list search.

### 6.5 Reports
- Sales report.
- Inventory report.
- Stock movements report.
- Cashflow report.
- Profitability report.
- Audit log report (admin only).

### 6.6 Finance Tracking
- Opening balance setup.
- Sale inflow and purchase outflow ledger entries.
- Running cash balance.
- Historical COGS using sale-time snapshots.
- Dashboard finance KPIs.

## 7. Scripts and Operational Utilities
### `start.py`
One-command runner for setup and launch:
- creates virtual environment
- installs dependencies
- ensures instance directory
- runs app

### `run.py`
Direct Flask launcher used by `start.py`.

### `scripts/normalize_legacy_utc_timestamps.py`
One-time maintenance script to normalize legacy naive timestamps to UTC-aware values.
Supports dry-run and idempotent marker behavior.

## 8. Quality and Validation
- Automated tests currently pass end-to-end.
- Coverage includes auth, models, products, transactions, and reports.
- Additional polish implemented:
  - UTC-aware datetime cleanup
  - backup and restore operator documentation

## 9. Security and Governance Controls
- CSRF protection enabled for form workflows.
- Password hashing via Werkzeug.
- Role-protected admin routes.
- Audit logging for key data-changing actions.

## 10. Backup and Data Safety
- SQLite DB stored at `instance/inventory.db`.
- Backup and restore procedure documented in README.
- App must be stopped before file-level DB operations.

## 11. Current Limitations
- SQLite file-based concurrency limits.
- Debug mode currently used for educational/demo run profile.
- Production migration tooling (Alembic) intentionally deferred as future hardening work.

## 12. Future Improvement Roadmap
- Add configurable cash deficit policy for purchases.
- Add migration framework for multi-environment schema management.
- Expand report edge-case tests and operational automation.
- Package deployment checklist for school IT handoff.

## 13. Conclusion
The system now provides a complete, demonstration-ready internal bookstore management workflow aligned with Human Computer Interaction 2 project goals. It combines usability-focused workflows with traceability, reporting, and operational safety practices for private school premises use.

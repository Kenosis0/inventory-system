# School Bookstore Inventory System

## Course Subject
Human Computer Interaction 2

## Why This Document Exists
This document is written as a technical narrative for team reviewers, faculty evaluators, and future maintainers who need to understand not only what the system does, but how and why it was designed this way. It explains the application from three perspectives at once: user experience decisions, implementation mechanics, and database logic.

The system itself is a Flask-based Inventory Management System for a school bookstore environment. It supports day-to-day bookstore operations such as maintaining products, processing sales and purchases, tracking stock movement, monitoring cash flow, and preserving accountability through audit logging.

## 1. Problem Context and Design Intent
The project started from a common school operations problem: inventory and transaction records were fragmented, hard to audit, and difficult to summarize quickly. Staff needed a workflow that was easy to use during active transactions, while administrators needed controls and traces for governance.

From an HCI perspective, the solution is guided by four principles:

1. Reduce cognitive load during operational tasks.
2. Preserve data traceability for every meaningful change.
3. Enforce role-appropriate access without making normal tasks difficult.
4. Keep the interface usable on both desktop and mobile, especially for table-heavy pages.

These principles shaped architecture choices, database structure, and recent mobile UX refinements.

## 2. System Architecture in Practice
The application follows a layered Flask architecture with clear boundaries between presentation, application logic, and data models.

### 2.1 Presentation Layer
The UI is rendered with Jinja templates located in `app/templates/`. Global styling and interaction behavior are provided by `app/static/css/main.css` and `app/static/js/main.js`. This keeps the rendering server-side, while adding lightweight JavaScript only where interaction quality benefits from it (navigation toggles, chart rendering, dismissible messages).

### 2.2 Application Layer
Business logic is grouped through Flask blueprints under `app/routes/`:

- `auth`: login and logout workflows
- `main`: dashboard and operational summary
- `products`: catalog, adjustments, export, low stock, and product lookup API
- `transactions`: sales and purchases with stock and cash effects
- `users`: account and role management
- `suppliers`: supplier lifecycle and transaction linkage
- `reports`: sales, inventory, stock movements, cashflow, profitability, audit logs

This separation keeps each area focused and easier to review independently.

### 2.3 Data Layer
`app/models.py` defines SQLAlchemy models and relationships for users, products, suppliers, transactions, stock movements, finance ledger entries, and audit logs. The schema is normalized enough for reporting clarity while keeping operational reads simple.

### 2.4 Startup Lifecycle
At runtime, `create_app()` in `app/__init__.py` initializes extensions and registers blueprints. During application startup, three important setup actions happen:

1. `db.create_all()` creates missing tables.
2. `ensure_schema_updates()` applies a lightweight SQLite-safe schema update for `unit_cost_at_sale` in `transaction_items` if missing.
3. `seed_initial_data()` creates default users and base categories if the database is empty.

This approach avoids hard failure on first run and supports classroom/demo portability.

## 3. Core Feature Mechanics
This section describes what happens internally when users perform operational tasks.

### 3.1 Authentication and Session Control
The login process validates credentials, checks active status, updates last login timestamp, writes an audit record, then creates a Flask-Login session. Logout also writes an audit record before ending the session.

Design significance:

- Every session boundary (login/logout) is traceable.
- Deactivated users are blocked before entering protected workflows.
- Redirect-to-next behavior keeps the login interruption minimal.

### 3.2 Role-Based Access Control
Role enforcement is handled through decorators in `app/utils/decorators.py`:

- `admin_required`: restricts management/governance functions.
- `staff_required`: permits admin and staff for operational tasks.

RBAC is therefore explicit at route level, making permission intent visible during code review.

### 3.3 Product and Inventory Management
Product flows include create, edit, view, soft-delete, stock adjustment, low-stock listing, and Excel export.

Important operational mechanics:

- Product creation supports initial stock. If initial quantity is greater than zero, a stock movement entry is automatically created so starting quantity has provenance.
- Product deletion is soft (`is_active=False`) instead of destructive deletion, preserving historical integrity.
- Stock adjustments require quantity validation and mandatory reason text, then generate both stock movement and audit entries.
- Product list supports search, filters, sorting, and pagination, with an API endpoint (`/products/api/search`) used by transaction forms.

### 3.4 Transaction Processing (Sales and Purchases)
The `transactions` blueprint is the most integrity-critical module because each transaction can affect stock, finance, and audit records in one flow.

#### Sale transaction flow
When a sale is submitted:

1. The form payload is parsed and validated row by row.
2. Each row checks product existence, numeric validity, and stock sufficiency.
3. Subtotal, discount, tax, and total are calculated.
4. A `Transaction` record is created with unique reference number.
5. A `TransactionItem` row is created for each sold item, including `unit_cost_at_sale` snapshot.
6. A negative `StockMovement` is recorded per item.
7. Product quantity is reduced.
8. A positive cash ledger entry (`sale_inflow`) is recorded with updated running balance.
9. An `AuditLog` entry captures metadata for the action.

The `unit_cost_at_sale` snapshot is especially important: it prevents later cost edits from distorting historical profitability reports.

#### Purchase transaction flow
When a purchase is submitted:

1. Supplier selection and item rows are validated.
2. A purchase `Transaction` record is created.
3. Item rows are inserted to `TransactionItem`.
4. Positive `StockMovement` rows are recorded.
5. Product quantities increase.
6. Product `cost_price` is updated to latest purchase unit cost.
7. A negative cash ledger entry (`purchase_outflow`) is recorded.
8. Audit metadata is written.

This keeps procurement and inventory synchronized while maintaining financial traceability.

### 3.5 Supplier and User Administration
Supplier and user modules follow a consistent governance pattern:

- create/update/deactivate workflows
- duplicate prevention checks
- route-level role protection
- audit entries for modifications

User management includes protections against self-lockout behavior, such as preventing administrators from deactivating or downgrading their own active admin account.

## 4. Reporting and Analytics Mechanics
Reports are not static pages; each report computes aggregates from transactional records and returns both table data and chart-ready arrays.

### 4.1 Sales Report
Computes date-range totals, counts, and daily breakdown. The chart arrays are zero-filled across the selected range, so chart continuity is preserved even on days with no sales.

### 4.2 Inventory Report
Computes total units, inventory value, retail value, low/out-of-stock counts, and category-level value distribution. Category value data powers an inventory mix chart.

### 4.3 Cashflow Report
Reads ledger entries in a selected date range, derives opening balance from the latest pre-range entry, then computes inflow, outflow, closing balance, and current balance. Daily net and daily running balance arrays drive the chart.

### 4.4 Profitability Report
Builds per-sale profitability rows using historical cost snapshots (`unit_cost_at_sale` fallback to product cost if absent), then computes total revenue, COGS, gross profit, margin percent, and net cash movement against purchase totals.

### 4.5 Audit and Stock Movement Reports
Audit logs and stock movement history provide forensic visibility with filtering and pagination. This supports accountability and anomaly tracing.

### 4.6 Dashboard Analytics
The dashboard combines KPI cards and compact charts:

- 7-day sales trend
- top product categories
- low stock alerts
- recent transactions

Recent UX refinement separates primary and secondary KPIs on mobile to reduce vertical overload while preserving access to financial context.

## 5. Mobile UX and Interaction Design Decisions
Early evaluation identified that desktop-oriented tables were difficult to scan and operate on small screens. The system now uses a mixed responsive strategy instead of forcing one pattern everywhere.

### 5.1 Mixed responsive table strategy
- Card-based mobile layouts for entity-management pages where row details and actions are identity-focused (users and suppliers).
- Priority-column responsive tables for transaction/report-heavy pages where comparative numeric scanning is still valuable.
- Inline mobile metadata for hidden columns, so context remains available when columns collapse.

### 5.2 Mobile navigation redesign
Navigation now uses a hybrid pattern:

- bottom app bar for frequent primary destinations (Dashboard, Products, Transactions, Reports, Menu)
- drawer sidebar for secondary and role-specific destinations
- scrim overlay and keyboard/resize close behavior for safer focus handling

This balances one-tap speed with IA depth.

### 5.3 Dashboard mobile compaction
To reduce scroll fatigue:

- only the most actionable KPI cards are shown first
- secondary finance KPIs move into a collapsible section
- quick actions use a compact 2-column mobile grid
- chart density remains controlled to avoid overload

The goal is progressive disclosure rather than information removal.

## 6. Database Design Rationale
The data model is intentionally centered on operational truth and traceability.

### 6.1 Entity overview

| Entity | Purpose | Critical fields and design reason |
| --- | --- | --- |
| `User` | Authentication and ownership | `role`, `is_active`, `last_login` support RBAC and account lifecycle |
| `Category` | Product grouping | Stable grouping for filtering, reporting, and chart segmentation |
| `Supplier` | Procurement source | Linked to purchase transactions for sourcing history |
| `Product` | Stocked item record | `sku` uniqueness, pricing fields, stock quantity, reorder threshold |
| `Transaction` | Header for sale/purchase event | `transaction_type`, totals, reference number, actor, optional supplier/customer |
| `TransactionItem` | Line-level detail | Per-item quantity, price, line total, historical cost snapshot |
| `StockMovement` | Immutable stock trail | signed quantity delta with before/after state and reason/reference |
| `CashLedger` | Running cash state | signed amount and `running_balance` for financial continuity |
| `AuditLog` | Governance trace | actor, action, table, record, old/new values, request metadata |

### 6.2 Relationship logic
The relationship graph enforces business interpretation:

- one user to many transactions, audits, and cash entries
- one category to many products
- one supplier to many purchase transactions
- one transaction to many transaction items and optional cash entries
- one product to many transaction items and stock movements

These relationships enable operational screens and reports without complex joins beyond what SQLAlchemy already handles cleanly.

### 6.3 Soft deletion and historical integrity
Products, suppliers, and users are deactivated rather than hard-deleted. This prevents historical transaction records from losing meaningful references and protects report consistency.

### 6.4 Time and schema evolution considerations
Timestamps are UTC-aware through `utc_now()`, and a maintenance script exists to normalize legacy naive timestamps. A lightweight startup schema check supports one critical column evolution (`unit_cost_at_sale`) without introducing a full migration framework during class development.

## 7. Security and Governance Controls
Security in this project is practical and layered for an internal school setting:

- CSRF protection enabled for form workflows
- password hashing via Werkzeug
- route-level role restrictions
- account activation checks before session issuance
- audit metadata capture (IP and user-agent)

These controls are designed to discourage unsafe operational behavior and simplify post-incident review.

## 8. Operational Tooling and Scripts

### 8.1 `start.py`
Provides one-command setup and execution:

- creates virtual environment if absent
- installs dependencies when needed
- ensures instance directory exists
- starts the Flask app through the environment Python

### 8.2 `run.py`
Simple execution entrypoint that creates and runs the Flask application.

### 8.3 `scripts/normalize_legacy_utc_timestamps.py`
One-time utility to convert legacy naive timestamps to UTC-aware values, with dry-run and marker-file safety.

## 9. Quality Assurance Strategy
The project includes a pytest-based test suite covering key functional domains:

- authentication
- models
- products
- transactions
- reports

This suite is used to validate route behavior and data logic during iteration. Because the project uses SQLite with a local instance database, operational discipline for backup/restore is part of development and demo workflow.

## 10. Current Trade-Offs and Limitations
The system is stable for educational and internal demo use, with known trade-offs:

- SQLite concurrency is limited for high parallel write loads.
- Full migration orchestration (for example, Alembic) is intentionally deferred.
- Deployment profile is currently tuned for local development and school presentation contexts.

These are acceptable within current scope, but should be addressed for production hardening.

## 11. Recommended Next-Stage Enhancements
If this project is extended beyond course scope, the most valuable next steps are:

1. introduce structured migrations for repeatable schema evolution
2. formalize deployment and secret management for non-local environments
3. expand report validation for more edge-case financial scenarios
4. add deeper observability (structured logs and operation metrics)
5. evaluate database scaling strategy if concurrent usage grows

## 12. Conclusion
This Inventory System demonstrates a complete school bookstore workflow where usability, integrity, and traceability are designed to work together. The implementation is not only feature-complete for the intended context, but also explicit in its operational reasoning: transactions update stock and finance in lockstep, governance logs preserve accountability, and the mobile UX has been refined to keep real-world use practical on smaller screens.

For reviewers, the central takeaway is that the system design is intentional. It is not a collection of disconnected screens; it is a coordinated operational platform where each module reinforces the others.
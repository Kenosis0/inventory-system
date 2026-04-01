# School Bookstore - Inventory System

## Course Subject
Human Computer Interaction 2

## Purpose of This Guide
This document explains exactly how to operate the system for school bookstore use, including strict do and do not rules for safe and consistent operation.

## Intended Operating Scope
- Private school premises use only.
- Users are limited to school staff and students.
- This is not for open public access.

## Access Roles and Responsibility
### Admin
- Manage users and suppliers.
- Configure finance opening balance.
- Access all reports including audit logs.
- Maintain data quality and backup routines.

### Staff
- Manage products and stock adjustments.
- Process sales and purchases.
- View operational reports (except admin-only pages).

## Startup and Shutdown Procedure
### Start the System
1. Open terminal in project folder.
2. Run:
   ```bash
   python start.py
   ```
3. Wait for startup output.
4. Open browser at:
   ```
   http://127.0.0.1:5000
   ```

### Stop the System
- Press `CTRL + C` in the terminal running the server.

## Standard Daily Workflow
1. Login with correct role.
2. Check dashboard for low-stock alerts and finance summary.
3. Record purchases before selling if stock is low.
4. Process sales transactions.
5. Use stock adjustment only when there is an actual correction reason.
6. Review reports before day-end.
7. Perform backup if needed.

## Functional Use Instructions
### 1. Product Management
- Go to Products.
- Add/edit product details: SKU, category, cost price, selling price, quantity, reorder level.
- Use search, sort, and Excel export for inventory monitoring.

### 2. Supplier Management (Admin)
- Go to Suppliers.
- Add supplier with complete contact details.
- Keep supplier names consistent to avoid duplicate entries.

### 3. Purchase Transactions
- Go to Transactions > New Purchase.
- Select supplier first.
- Add product lines with quantity and unit cost.
- Submit and verify transaction reference and stock increase.

### 4. Sale Transactions
- Go to Transactions > New Sale.
- Add products and quantities.
- Confirm total and submit.
- Verify stock decreases and cash inflow is reflected.

### 5. Stock Adjustment
- Use only for correction cases (damaged, count discrepancy, approved correction).
- Always provide clear reason in notes.

### 6. Reports
- Sales report: sales totals and date-range breakdown.
- Inventory report: stock and value overview.
- Stock movements report: stock audit trail.
- Cashflow report: running cash balance and entries.
- Profitability report: revenue, COGS, and gross margin.
- Audit log (Admin): security and data-change trace.

## Strict Rules: Do and Do Not

## DO
1. Do keep SKU unique and consistent.
2. Do record purchases before processing new sales when stock is insufficient.
3. Do check low-stock alerts daily.
4. Do create DB backup before any reset or risky change.
5. Do stop the app before backup or restore operations.
6. Do use notes fields for traceability on adjustments and transactions.
7. Do use admin account only for admin tasks.
8. Do verify reports at end of day/week for anomalies.

## DO NOT
1. Do not edit `instance/inventory.db` manually while app is running.
2. Do not process fake adjustment entries just to force stock values.
3. Do not share admin credentials with non-admin users.
4. Do not deactivate your own active admin account.
5. Do not run multiple server instances against the same SQLite file.
6. Do not delete `.venv` or DB file unless you understand recovery steps.
7. Do not ignore low-stock alerts for fast-moving items.
8. Do not skip backup before migration or normalization scripts.

## Backup and Recovery Quick Rules
1. Stop app.
2. Copy DB to timestamped backup filename.
3. Restore only while app is stopped.
4. Restart and verify login, dashboard, products, and transactions pages.

## Demonstration Checklist
1. Show login with role awareness.
2. Show low-stock alerts.
3. Process one purchase and one sale.
4. Show stock movement trail.
5. Show cashflow and profitability report updates.
6. Export product list to Excel.

## Known Operating Limits
- SQLite is file-based and best for low to moderate concurrent local usage.
- App runs in debug mode for educational/demo context.
- For production-grade deployment, migration and security hardening are separate next steps.

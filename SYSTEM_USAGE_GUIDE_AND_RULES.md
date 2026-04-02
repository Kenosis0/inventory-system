# School Bookstore Inventory System

## Course Subject
Human Computer Interaction 2

## Document Type
This file is the official **Manual, Guide, and Rules** for operating the web application.

Use this document as the standard operating procedure (SOP) for:

1. day-to-day operations
2. correct webapp navigation
3. preventing user mistakes
4. protecting the database from unsafe actions

## 1. Purpose and Scope
This system is for internal school bookstore use only.

This manual explains:

1. what each role should do
2. where to click in the webapp for each task
3. the correct sequence of operations
4. what to do and what not to do
5. what to do when errors happen

## 2. Roles and Access Boundaries

### 2.1 Admin
Admin can:

1. manage users
2. manage suppliers
3. configure opening cash balance (Finance Setup)
4. access all reports, including Audit Log

Admin must:

1. enforce backup discipline
2. monitor unusual activity
3. avoid sharing admin credentials

### 2.2 Staff
Staff can:

1. manage products
2. process sales and purchases
3. adjust stock with reasons
4. view operational reports

Staff cannot:

1. manage users
2. manage suppliers
3. access admin-only pages (Finance Setup and Audit Log)

## 3. Navigation Map of the Webapp

### 3.1 Desktop Navigation (Sidebar)
Main pages:

1. Dashboard
2. Products
3. Transactions
4. Reports
5. Users (Admin only)
6. Suppliers (Admin only)

Reports submenu:

1. Sales Report
2. Inventory Report
3. Stock Movements
4. Cashflow Report
5. Profitability Report
6. Finance Setup (Admin only)
7. Audit Log (Admin only)

### 3.2 Mobile Navigation
Bottom app bar:

1. Home
2. Products
3. Txns
4. Reports
5. Menu

Use **Menu** to open the drawer and access secondary pages such as Users, Suppliers, Profile, and Logout.

## 4. Startup and Shutdown Procedure

### 4.1 Start the System
1. Open terminal in the project folder.
2. Run:

```bash
python start.py
```

3. Wait for startup output.
4. Open:

```text
http://127.0.0.1:5000
```

### 4.2 Stop the System
Press `CTRL + C` in the running terminal.

Never keep multiple server instances running against the same `instance/inventory.db`.

## 5. First-Time Setup SOP (Admin)
Run this sequence on a new or reset database.

1. Login as admin.
2. Open Reports -> Finance Setup.
3. Enter opening balance once, then save.
4. Open Suppliers -> Add Supplier and encode suppliers first.
5. Open Products -> Add Product and encode initial catalog.
6. Open Users and create staff accounts.
7. Process a small purchase transaction to validate stock and cashflow.
8. Verify Dashboard, Cashflow, and Inventory report values.

## 6. Daily Operating Workflow SOP

### 6.1 Opening Checklist
1. Login with correct role.
2. Go to Dashboard.
3. Check low stock alerts.
4. Check available cash and recent transactions.
5. If stock is low, prioritize purchase entries first.

### 6.2 Operating Cycle
1. Record incoming stock through New Purchase.
2. Process customer sales through New Sale.
3. Use stock adjustment only for corrections.
4. Keep notes meaningful for adjustments and special cases.

### 6.3 Closing Checklist
1. Open Sales Report and verify totals.
2. Open Inventory Report and verify low/out-of-stock items.
3. Open Cashflow and Profitability reports.
4. Admin reviews Audit Log for unusual actions.
5. Perform backup if needed.

## 7. Click-by-Click Task Procedures

### 7.1 Add Product
Path: **Sidebar -> Products -> Add Product**

Steps:

1. Fill SKU (must be unique).
2. Fill Name and Category.
3. Fill Cost Price and Selling Price.
4. Fill Quantity and Reorder Level.
5. Save product.
6. Verify it appears in Products list.

### 7.2 Edit Product
Path: **Products -> row action -> Edit**

Steps:

1. Open product edit form.
2. Update allowed fields.
3. Save.
4. Verify updated values in product detail page.

### 7.3 Adjust Stock (Correction Only)
Path: **Products -> row action -> Adjust Stock**

Steps:

1. Select adjustment type (add or subtract).
2. Enter quantity.
3. Enter required reason.
4. Save adjustment.
5. Verify new quantity and stock movement history.

Rule: never use stock adjustment to replace proper sale/purchase transactions.

### 7.4 Create Purchase Transaction
Path: **Sidebar -> Transactions -> New Purchase**

Steps:

1. Select supplier.
2. Add each product line.
3. Enter quantity and unit cost per line.
4. Submit.
5. Verify reference number appears.
6. Verify product quantity increased.
7. Verify cash outflow in Cashflow report.

### 7.5 Create Sale Transaction
Path: **Sidebar -> Transactions -> New Sale**

Steps:

1. Add products and quantities.
2. Confirm stock is sufficient.
3. Add customer name (optional) and notes when needed.
4. Submit.
5. Verify reference number appears.
6. Verify product quantity decreased.
7. Verify inflow in Cashflow report and impact in Profitability report.

### 7.6 Manage Suppliers (Admin)
Path: **Sidebar -> Suppliers**

Steps:

1. Add supplier with complete contact details.
2. Edit supplier when details change.
3. Deactivate supplier instead of deleting history.
4. Validate supplier appears in purchase form.

### 7.7 Manage Users (Admin)
Path: **Sidebar -> Users**

Steps:

1. Add user with correct role.
2. Edit role/status only when authorized.
3. Do not deactivate your own active admin account.
4. Verify login works for newly created account.

### 7.8 Generate Reports
Path: **Sidebar -> Reports -> select report**

Use each report for the right question:

1. Sales Report: sales amount and volume by date range
2. Inventory Report: stock posture and value
3. Stock Movements: why stock changed
4. Cashflow Report: inflow/outflow and running balance
5. Profitability Report: revenue vs COGS and margin
6. Audit Log (Admin): who changed what and when

## 8. Rules to Prevent Errors and Database Damage

### 8.1 DO (Required)
1. Keep SKU values unique.
2. Process purchases before sales when stock is low.
3. Use transaction forms for normal movement of stock.
4. Use stock adjustment only for correction cases with clear notes.
5. Stop app before backup or restore.
6. Verify reports at end of day.
7. Keep admin access restricted.

### 8.2 DO NOT (Prohibited)
1. Do not edit `instance/inventory.db` manually while app is running.
2. Do not run more than one server instance on the same DB file.
3. Do not use fake adjustments to force balances.
4. Do not skip backup before risky maintenance.
5. Do not share admin credentials.
6. Do not deactivate your own last active admin account.

## 9. Common Errors and Correct Action

| Error or situation | Most likely cause | Correct action |
| --- | --- | --- |
| Invalid username/password | wrong credentials | retry carefully, reset through admin if needed |
| SKU already exists | duplicate SKU entry | use existing SKU record or create new unique SKU |
| Insufficient stock on sale | sale quantity exceeds available stock | reduce quantity or encode purchase first |
| Supplier required on purchase | no supplier selected | select valid supplier before submit |
| Quantity must be valid | non-numeric or negative input | enter whole number >= 0 |
| Cannot subtract more than stock | invalid stock adjustment | reduce adjustment or re-check physical count |
| Access denied page | wrong role | login with authorized account |

## 10. Database Protection Protocol

### 10.1 Strict Safety Rules
1. Always stop the app before direct DB file operations.
2. Always back up before running scripts or large data changes.
3. Never run tests against the only copy of demo data without backup.
4. Never perform manual SQLite edits during active app runtime.

### 10.2 Backup Procedure
1. Stop app.
2. Run:

```bash
copy instance\inventory.db instance\inventory.db.backup-YYYY-MM-DD-HH-MM-SS
```

3. Confirm backup file exists.

### 10.3 Restore Procedure
1. Stop app.
2. Run:

```bash
copy /Y instance\inventory.db.backup-YYYY-MM-DD-HH-MM-SS instance\inventory.db
```

3. Restart app.
4. Validate:
1. login works
2. Dashboard loads
3. Products list loads
4. Transactions list loads
5. latest expected records are present

## 11. Safe Maintenance Workflow
Use this sequence before maintenance tasks (normalization script, resets, heavy refactors, test runs against shared DB):

1. Stop app.
2. Create backup.
3. Perform maintenance task.
4. Start app and run smoke checks.
5. If results are wrong, stop app and restore immediately.

## 12. Demonstration SOP for Reviewers or Professor
1. Login and show role difference.
2. Show Dashboard summary and charts.
3. Encode one purchase transaction.
4. Encode one sale transaction.
5. Show Stock Movements for traceability.
6. Show Cashflow and Profitability updates.
7. Show Audit Log as governance proof.
8. Export products to Excel.

## 13. Escalation Procedure
Escalate to admin/supervisor immediately when:

1. repeated login issues happen for active accounts
2. stock totals and transaction records do not match
3. audit log shows suspicious actions
4. database restore is required

## 14. Final Operating Principle
If a user is unsure what to do, do not guess and do not force data edits.

Follow this order:

1. pause
2. check this manual
3. back up database
4. ask admin/supervisor

This protects both data integrity and operational reliability.
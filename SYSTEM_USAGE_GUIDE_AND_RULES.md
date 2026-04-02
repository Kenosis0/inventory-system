# School Bookstore Inventory System

## Course Subject
Human Computer Interaction 2

## Purpose of This Guide
This guide explains how to operate the system safely and consistently in a school bookstore context. It is written for both daily users and supervisors so that operations remain accurate, traceable, and easy to review.

This document answers three practical questions:

1. How should the system be used during normal daily operations?
2. What rules must always be followed to avoid data quality problems?
3. What checks should be done before demonstration, reporting, or handover?

## 1. Who Should Use the System
The system is designed for internal school use only. It is intended for bookstore staff, school administration, and supervised student assistants (if approved by the school).

It is not intended for public internet exposure.

## 2. Access Roles and Responsibility Boundaries
The system enforces role-based access to prevent accidental misuse.

### 2.1 Admin Role
Admins are responsible for system governance and high-impact records.

Admin responsibilities include:

- managing user accounts
- managing suppliers
- setting opening cash balance (one-time setup)
- accessing all reports, including audit logs
- ensuring backup and recovery discipline

### 2.2 Staff Role
Staff members are responsible for day-to-day operations.

Staff responsibilities include:

- maintaining products and stock adjustments
- processing sales and purchases
- monitoring low-stock alerts
- reviewing operational reports

Staff should not perform admin-only tasks through shared credentials.

## 3. Startup and Shutdown Procedure

### 3.1 Start the System
1. Open terminal in the project folder.
2. Run:

```bash
python start.py
```

3. Wait for the startup output to confirm URLs.
4. Open the browser using the local URL:

```text
http://127.0.0.1:5000
```

### 3.2 Stop the System
Press `CTRL + C` in the terminal running the app.

Do not leave multiple active server processes using the same SQLite file.

## 4. Recommended Daily Operating Flow
The best results come from using a consistent daily sequence.

### 4.1 Opening routine
1. Log in with the correct account role.
2. Open Dashboard and check:
- low stock count
- available cash
- recent transaction activity
3. If inventory is low, encode purchase transactions before peak selling periods.

### 4.2 During operations
1. Encode purchases as inventory arrives.
2. Process sales as they happen.
3. Use stock adjustment only for real corrections (count mismatch, damaged item, approved reconciliation).
4. Include meaningful notes when requested by form fields.

### 4.3 Closing routine
1. Review Sales, Inventory, Cashflow, and Profitability reports.
2. Confirm no suspicious stock movements or unusual audit activity.
3. Back up the database when needed (especially before major edits, script runs, or demos).

## 5. Module-by-Module Usage Instructions

### 5.1 Product Management
Use Products to maintain inventory records.

Standard practice:

1. Keep SKU unique and stable.
2. Enter accurate pricing (cost and selling price).
3. Set practical reorder levels based on item velocity.
4. Use low-stock views for restock planning.
5. Use Excel export for offline review and supervisor reporting.

### 5.2 Supplier Management (Admin)
Use Suppliers for procurement source control.

Standard practice:

1. Keep supplier names normalized (avoid near-duplicate spellings).
2. Maintain contact details for follow-up.
3. Use supplier records when processing purchases so procurement history remains analyzable.

### 5.3 Purchase Transactions
Use `Transactions > New Purchase`.

Required workflow:

1. Select supplier.
2. Add line items with quantity and unit cost.
3. Submit and verify generated reference.
4. Confirm stock increased correctly.
5. Confirm cash outflow appears in cashflow report.

### 5.4 Sale Transactions
Use `Transactions > New Sale`.

Required workflow:

1. Add product line items and quantities.
2. Confirm stock availability warnings are resolved before submit.
3. Submit and verify generated reference.
4. Confirm stock decreased correctly.
5. Confirm inflow appears in cashflow and contributes to profitability reporting.

### 5.5 Stock Adjustment
Use stock adjustment only for correction cases.

Required discipline:

1. Choose correct adjustment direction.
2. Enter valid quantity.
3. Provide clear reason text.
4. Verify resulting stock and movement history.

### 5.6 Reports and Interpretation
Each report serves a different operational question:

- Sales report: How much sold and how often in a period?
- Inventory report: What is the stock/value posture right now?
- Stock movements: Why did stock change for a specific item?
- Cashflow: How did cash move over time and what is current balance?
- Profitability: Is revenue covering COGS and by how much?
- Audit log (admin): Who changed what, and when?

## 6. Mobile Usage Notes
The system supports mobile operation with responsive patterns optimized for readability.

What users should expect on mobile:

- a bottom app bar for fast access to primary pages
- a menu trigger that opens the sidebar drawer for secondary/admin pages
- card views for user/supplier management areas
- compact priority-column tables for transaction and report-heavy pages
- dashboard KPI compaction with expandable secondary finance details

If data appears condensed on small screens, use row-level expandable sections and details toggles provided in-table.

## 7. Strict Rules: Required and Prohibited Actions

### 7.1 Required actions (DO)
1. Keep SKU values unique and consistent.
2. Record purchases before selling when stock is insufficient.
3. Check low-stock indicators daily.
4. Stop the app before backup or restore operations.
5. Use descriptive notes for adjustments and unusual transactions.
6. Reserve admin credentials for admin-level work only.
7. Review reports routinely for anomalies.

### 7.2 Prohibited actions (DO NOT)
1. Do not manually edit `instance/inventory.db` while the app is running.
2. Do not create fake adjustments to force inventory values.
3. Do not share admin credentials with non-admin users.
4. Do not deactivate your own active admin account.
5. Do not run multiple app instances against the same SQLite file.
6. Do not skip backups before risky maintenance changes.

## 8. Backup and Recovery Procedure

### 8.1 Backup
1. Stop the app.
2. Copy database with timestamped name:

```bash
copy instance\inventory.db instance\inventory.db.backup-YYYY-MM-DD-HH-MM-SS
```

3. Restart app if needed.

### 8.2 Restore
1. Stop the app.
2. Restore from backup:

```bash
copy /Y instance\inventory.db.backup-YYYY-MM-DD-HH-MM-SS instance\inventory.db
```

3. Start app and validate login, dashboard, products, and transactions pages.

## 9. Demonstration Checklist (Reviewer/Professor)
Use this checklist before formal project demonstration:

1. Login and role behavior shown (admin vs staff).
2. Dashboard KPIs and chart widgets displayed.
3. One purchase flow completed and reflected in stock/cashflow.
4. One sale flow completed and reflected in stock/profitability.
5. Stock movement history shown for traceability.
6. Audit log sample shown (admin view).
7. Product export to Excel demonstrated.

## 10. Operational Limits and Scope Notes
- SQLite is suitable for school demo and low-concurrency operations.
- Current deployment profile is local/dev-oriented.
- Production-grade hardening (deployment controls, migration strategy, scaling) is outside immediate class-scope operations.

## 11. Escalation Guidance
Escalate to admin/supervisor when:

1. repeated login issues occur for active users
2. stock and transaction totals appear inconsistent
3. unusual audit entries appear without a known operator action
4. database recovery is required after failed maintenance

Consistent use of this guide protects both data quality and demonstration reliability.
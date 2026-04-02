from datetime import UTC, datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Transaction, Product, Category, AuditLog, StockMovement, CashLedger
from app.utils.decorators import admin_required
from sqlalchemy import func

reports_bp = Blueprint('reports', __name__)


def _parse_date_range(default_days=30):
    """Parse report date range from query params with sensible defaults."""
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    if not date_from:
        date_from = (datetime.now(UTC) - timedelta(days=default_days)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = datetime.now(UTC).strftime('%Y-%m-%d')

    try:
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
        end_date = datetime.strptime(date_to, '%Y-%m-%d')
        end_date = datetime.combine(end_date.date(), datetime.max.time())
    except ValueError:
        start_date = datetime.now(UTC) - timedelta(days=default_days)
        end_date = datetime.now(UTC)
        date_from = start_date.strftime('%Y-%m-%d')
        date_to = end_date.strftime('%Y-%m-%d')

    return date_from, date_to, start_date, end_date

@reports_bp.route('/sales')
@login_required
def sales_report():
    """Generate sales report."""
    # Get date range
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Default to last 30 days
    if not date_from:
        date_from = (datetime.now(UTC) - timedelta(days=30)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = datetime.now(UTC).strftime('%Y-%m-%d')
    
    try:
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
        end_date = datetime.strptime(date_to, '%Y-%m-%d')
        end_date = datetime.combine(end_date.date(), datetime.max.time())
    except ValueError:
        start_date = datetime.now(UTC) - timedelta(days=30)
        end_date = datetime.now(UTC)
    
    # Get sales in date range
    sales = Transaction.query.filter(
        Transaction.transaction_type == 'sale',
        Transaction.created_at >= start_date,
        Transaction.created_at <= end_date
    ).order_by(Transaction.created_at.desc()).all()
    
    # Calculate totals
    total_sales = sum(s.total for s in sales)
    total_transactions = len(sales)
    
    # Daily breakdown
    daily_sales = db.session.query(
        func.date(Transaction.created_at).label('date'),
        func.sum(Transaction.total).label('total'),
        func.count(Transaction.id).label('count')
    ).filter(
        Transaction.transaction_type == 'sale',
        Transaction.created_at >= start_date,
        Transaction.created_at <= end_date
    ).group_by(func.date(Transaction.created_at)).all()

    daily_sales_map = {}
    for row in daily_sales:
        row_key = row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date)
        daily_sales_map[row_key] = {
            'total': float(row.total or 0),
            'count': int(row.count or 0),
        }

    sales_chart_labels = []
    sales_chart_totals = []
    sales_chart_counts = []
    current_day = start_date.date()
    end_day = end_date.date()

    while current_day <= end_day:
        day_key = current_day.isoformat()
        day_data = daily_sales_map.get(day_key, {'total': 0.0, 'count': 0})
        sales_chart_labels.append(current_day.strftime('%b %d'))
        sales_chart_totals.append(round(day_data['total'], 2))
        sales_chart_counts.append(day_data['count'])
        current_day += timedelta(days=1)
    
    return render_template('reports/sales.html',
        sales=sales,
        total_sales=total_sales,
        total_transactions=total_transactions,
        daily_sales=daily_sales,
        sales_chart_labels=sales_chart_labels,
        sales_chart_totals=sales_chart_totals,
        sales_chart_counts=sales_chart_counts,
        date_from=date_from,
        date_to=date_to
    )

@reports_bp.route('/inventory')
@login_required
def inventory_report():
    """Generate inventory report."""
    # Get all active products
    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    
    # Calculate totals
    total_items = sum(p.quantity for p in products)
    total_value = sum(p.quantity * p.cost_price for p in products)
    total_retail_value = sum(p.quantity * p.selling_price for p in products)
    
    # Low stock items
    low_stock = [p for p in products if p.is_low_stock]
    out_of_stock = [p for p in products if p.quantity == 0]
    
    # By category
    category_stats = db.session.query(
        Category.name,
        func.count(Product.id).label('count'),
        func.sum(Product.quantity).label('quantity'),
        func.sum(Product.quantity * Product.cost_price).label('value')
    ).outerjoin(Product, db.and_(
        Product.category_id == Category.id,
        Product.is_active == True
    )).group_by(Category.id).all()

    inventory_chart_pairs = sorted(
        [
            (name, float(value or 0))
            for name, _count, _quantity, value in category_stats
            if float(value or 0) > 0
        ],
        key=lambda pair: pair[1],
        reverse=True
    )[:8]
    inventory_chart_labels = [pair[0] for pair in inventory_chart_pairs]
    inventory_chart_values = [round(pair[1], 2) for pair in inventory_chart_pairs]
    
    return render_template('reports/inventory.html',
        products=products,
        total_items=total_items,
        total_value=total_value,
        total_retail_value=total_retail_value,
        low_stock_count=len(low_stock),
        out_of_stock_count=len(out_of_stock),
        category_stats=category_stats,
        inventory_chart_labels=inventory_chart_labels,
        inventory_chart_values=inventory_chart_values
    )

@reports_bp.route('/finance/setup', methods=['GET', 'POST'])
@login_required
@admin_required
def finance_setup():
    """Set opening cash balance once for the cash ledger."""
    opening_entry = CashLedger.query.filter_by(entry_type='opening_balance').order_by(CashLedger.id.asc()).first()

    if request.method == 'POST':
        if opening_entry:
            flash('Opening cash balance has already been configured.', 'error')
            return redirect(url_for('reports.cashflow_report'))

        opening_balance_raw = request.form.get('opening_balance', '').strip()
        notes = request.form.get('notes', '').strip()

        try:
            opening_balance = float(opening_balance_raw)
        except ValueError:
            flash('Opening balance must be a valid number.', 'error')
            return render_template('reports/finance_setup.html', opening_entry=opening_entry)

        if opening_balance < 0:
            flash('Opening balance cannot be negative.', 'error')
            return render_template('reports/finance_setup.html', opening_entry=opening_entry)

        entry = CashLedger(
            entry_type='opening_balance',
            amount=opening_balance,
            running_balance=opening_balance,
            user_id=current_user.id,
            notes=notes or 'Opening cash balance',
        )
        db.session.add(entry)
        db.session.commit()

        flash('Opening cash balance has been saved successfully.', 'success')
        return redirect(url_for('reports.cashflow_report'))

    return render_template('reports/finance_setup.html', opening_entry=opening_entry)

@reports_bp.route('/cashflow')
@login_required
def cashflow_report():
    """Show cash inflow/outflow ledger and running balance."""
    date_from, date_to, start_date, end_date = _parse_date_range()

    entries = CashLedger.query.filter(
        CashLedger.created_at >= start_date,
        CashLedger.created_at <= end_date,
    ).order_by(CashLedger.created_at.asc(), CashLedger.id.asc()).all()

    previous_entry = CashLedger.query.filter(
        CashLedger.created_at < start_date,
    ).order_by(CashLedger.created_at.desc(), CashLedger.id.desc()).first()

    opening_balance = previous_entry.running_balance if previous_entry else 0.0
    inflow = sum(entry.amount for entry in entries if entry.amount > 0)
    outflow = abs(sum(entry.amount for entry in entries if entry.amount < 0))
    closing_balance = opening_balance + inflow - outflow

    latest_entry = CashLedger.query.order_by(CashLedger.id.desc()).first()
    current_balance = latest_entry.running_balance if latest_entry else 0.0

    cashflow_daily = {}
    for entry in entries:
        day_key = entry.created_at.date().isoformat()
        if day_key not in cashflow_daily:
            cashflow_daily[day_key] = {
                'label': entry.created_at.strftime('%b %d'),
                'net': 0.0,
                'running_balance': float(entry.running_balance),
            }

        cashflow_daily[day_key]['net'] += float(entry.amount)
        cashflow_daily[day_key]['running_balance'] = float(entry.running_balance)

    cashflow_chart_labels = [day_data['label'] for day_data in cashflow_daily.values()]
    cashflow_chart_net = [round(day_data['net'], 2) for day_data in cashflow_daily.values()]
    cashflow_chart_balance = [round(day_data['running_balance'], 2) for day_data in cashflow_daily.values()]

    return render_template(
        'reports/cashflow.html',
        entries=entries,
        date_from=date_from,
        date_to=date_to,
        opening_balance=opening_balance,
        inflow=inflow,
        outflow=outflow,
        closing_balance=closing_balance,
        current_balance=current_balance,
        cashflow_chart_labels=cashflow_chart_labels,
        cashflow_chart_net=cashflow_chart_net,
        cashflow_chart_balance=cashflow_chart_balance,
    )

@reports_bp.route('/profitability')
@login_required
def profitability_report():
    """Show profitability with COGS snapshot support."""
    date_from, date_to, start_date, end_date = _parse_date_range()

    sales = Transaction.query.filter(
        Transaction.transaction_type == 'sale',
        Transaction.created_at >= start_date,
        Transaction.created_at <= end_date,
    ).order_by(Transaction.created_at.desc()).all()

    purchases = Transaction.query.filter(
        Transaction.transaction_type == 'purchase',
        Transaction.created_at >= start_date,
        Transaction.created_at <= end_date,
    ).all()

    rows = []
    total_revenue = 0.0
    total_cogs = 0.0

    for sale in sales:
        revenue = sale.total
        cogs = 0.0

        for item in sale.items:
            unit_cost = item.unit_cost_at_sale if item.unit_cost_at_sale is not None else item.product.cost_price
            cogs += unit_cost * item.quantity

        gross_profit = revenue - cogs
        margin_percent = (gross_profit / revenue * 100) if revenue > 0 else 0

        rows.append({
            'transaction': sale,
            'revenue': revenue,
            'cogs': cogs,
            'gross_profit': gross_profit,
            'margin_percent': margin_percent,
        })

        total_revenue += revenue
        total_cogs += cogs

    total_gross_profit = total_revenue - total_cogs
    overall_margin_percent = (total_gross_profit / total_revenue * 100) if total_revenue > 0 else 0
    purchase_total = sum(p.total for p in purchases)
    net_cash_movement = total_revenue - purchase_total

    profitability_daily = {}
    for row in rows:
        day_value = row['transaction'].created_at.date()
        day_key = day_value.isoformat()
        if day_key not in profitability_daily:
            profitability_daily[day_key] = {
                'label': day_value.strftime('%b %d'),
                'revenue': 0.0,
                'cogs': 0.0,
                'gross_profit': 0.0,
            }

        profitability_daily[day_key]['revenue'] += float(row['revenue'])
        profitability_daily[day_key]['cogs'] += float(row['cogs'])
        profitability_daily[day_key]['gross_profit'] += float(row['gross_profit'])

    profitability_keys = sorted(profitability_daily.keys())
    profitability_chart_labels = [profitability_daily[key]['label'] for key in profitability_keys]
    profitability_chart_revenue = [round(profitability_daily[key]['revenue'], 2) for key in profitability_keys]
    profitability_chart_cogs = [round(profitability_daily[key]['cogs'], 2) for key in profitability_keys]
    profitability_chart_profit = [round(profitability_daily[key]['gross_profit'], 2) for key in profitability_keys]

    return render_template(
        'reports/profitability.html',
        rows=rows,
        date_from=date_from,
        date_to=date_to,
        total_revenue=total_revenue,
        total_cogs=total_cogs,
        total_gross_profit=total_gross_profit,
        overall_margin_percent=overall_margin_percent,
        purchase_total=purchase_total,
        net_cash_movement=net_cash_movement,
        profitability_chart_labels=profitability_chart_labels,
        profitability_chart_revenue=profitability_chart_revenue,
        profitability_chart_cogs=profitability_chart_cogs,
        profitability_chart_profit=profitability_chart_profit,
    )


@reports_bp.route('/audit')
@login_required
@admin_required
def audit_log():
    """View audit log (Admin only)."""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Get filter parameters
    action = request.args.get('action')
    table_name = request.args.get('table')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Build query
    query = AuditLog.query
    
    if action:
        query = query.filter_by(action=action)
    
    if table_name:
        query = query.filter_by(table_name=table_name)
    
    if date_from:
        try:
            date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(AuditLog.created_at >= date_from_dt)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
            date_to_dt = datetime.combine(date_to_dt.date(), datetime.max.time())
            query = query.filter(AuditLog.created_at <= date_to_dt)
        except ValueError:
            pass
    
    # Order by date (newest first)
    query = query.order_by(AuditLog.created_at.desc())
    
    logs = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get unique actions and tables for filters
    actions = db.session.query(AuditLog.action.distinct()).all()
    tables = db.session.query(AuditLog.table_name.distinct()).all()
    
    return render_template('reports/audit.html',
        logs=logs,
        actions=[a[0] for a in actions],
        tables=[t[0] for t in tables],
        current_action=action,
        current_table=table_name,
        date_from=date_from or '',
        date_to=date_to or ''
    )

@reports_bp.route('/stock-movements')
@login_required
def stock_movements():
    """View stock movement history."""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    product_id = request.args.get('product_id', type=int)
    movement_type = request.args.get('type')
    
    query = StockMovement.query
    
    if product_id:
        query = query.filter_by(product_id=product_id)
    
    if movement_type:
        query = query.filter_by(movement_type=movement_type)
    
    query = query.order_by(StockMovement.created_at.desc())
    
    movements = query.paginate(page=page, per_page=per_page, error_out=False)
    
    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    
    return render_template('reports/stock_movements.html',
        movements=movements,
        products=products,
        current_product=product_id,
        current_type=movement_type
    )

from datetime import datetime, timedelta
from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models import db, Transaction, Product, Category, AuditLog, StockMovement
from app.utils.decorators import admin_required
from sqlalchemy import func

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/sales')
@login_required
def sales_report():
    """Generate sales report."""
    # Get date range
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Default to last 30 days
    if not date_from:
        date_from = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = datetime.utcnow().strftime('%Y-%m-%d')
    
    try:
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
        end_date = datetime.strptime(date_to, '%Y-%m-%d')
        end_date = datetime.combine(end_date.date(), datetime.max.time())
    except ValueError:
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
    
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
    
    return render_template('reports/sales.html',
        sales=sales,
        total_sales=total_sales,
        total_transactions=total_transactions,
        daily_sales=daily_sales,
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
    
    return render_template('reports/inventory.html',
        products=products,
        total_items=total_items,
        total_value=total_value,
        total_retail_value=total_retail_value,
        low_stock_count=len(low_stock),
        out_of_stock_count=len(out_of_stock),
        category_stats=category_stats
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

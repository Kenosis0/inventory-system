from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import db, Product, Transaction, Category, User
from sqlalchemy import func
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get statistics for dashboard
    total_products = Product.query.filter_by(is_active=True).count()
    total_categories = Category.query.count()
    
    # Low stock products (at or below reorder level)
    low_stock_products = Product.query.filter(
        Product.quantity <= Product.reorder_level,
        Product.is_active == True
    ).all()
    low_stock_count = len(low_stock_products)
    
    # Today's transactions
    today = datetime.utcnow().date()
    today_sales = Transaction.query.filter(
        Transaction.transaction_type == 'sale',
        func.date(Transaction.created_at) == today
    ).all()
    today_sales_total = sum(t.total for t in today_sales)
    today_sales_count = len(today_sales)
    
    # Recent transactions (last 5)
    recent_transactions = Transaction.query.order_by(
        Transaction.created_at.desc()
    ).limit(5).all()
    
    # Total inventory value
    inventory_value = db.session.query(
        func.sum(Product.quantity * Product.cost_price)
    ).filter(Product.is_active == True).scalar() or 0
    
    # Products by category
    category_stats = db.session.query(
        Category.name,
        func.count(Product.id)
    ).outerjoin(Product).group_by(Category.id).all()
    
    return render_template('dashboard.html',
        total_products=total_products,
        total_categories=total_categories,
        low_stock_count=low_stock_count,
        low_stock_products=low_stock_products[:5],  # Show top 5 low stock items
        today_sales_total=today_sales_total,
        today_sales_count=today_sales_count,
        recent_transactions=recent_transactions,
        inventory_value=inventory_value,
        category_stats=category_stats
    )

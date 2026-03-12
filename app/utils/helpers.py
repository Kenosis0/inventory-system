import json
from datetime import datetime
from flask import request
from flask_login import current_user

def generate_reference_number(prefix='TXN'):
    """Generate a unique reference number for transactions."""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    return f"{prefix}-{timestamp}"

def log_audit(db, AuditLog, action, table_name, record_id=None, old_values=None, new_values=None):
    """
    Create an audit log entry.
    
    Args:
        db: SQLAlchemy database instance
        AuditLog: AuditLog model class
        action: Type of action ('create', 'update', 'delete', 'login', 'logout')
        table_name: Name of the affected table
        record_id: ID of the affected record
        old_values: Dictionary of old values (for updates/deletes)
        new_values: Dictionary of new values (for creates/updates)
    """
    audit = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        action=action,
        table_name=table_name,
        record_id=record_id,
        old_values=json.dumps(old_values) if old_values else None,
        new_values=json.dumps(new_values) if new_values else None,
        ip_address=request.remote_addr if request else None,
        user_agent=str(request.user_agent)[:255] if request else None
    )
    db.session.add(audit)
    db.session.commit()

def record_stock_movement(db, StockMovement, product, user_id, movement_type, quantity_change, reference=None, notes=None):
    """
    Record a stock movement for audit trail.
    
    Args:
        db: SQLAlchemy database instance
        StockMovement: StockMovement model class
        product: Product instance
        user_id: ID of the user making the change
        movement_type: Type of movement ('sale', 'purchase', 'adjustment', 'return')
        quantity_change: Change in quantity (positive for in, negative for out)
        reference: Transaction reference or reason
        notes: Additional notes
    """
    quantity_before = product.quantity
    quantity_after = product.quantity + quantity_change
    
    movement = StockMovement(
        product_id=product.id,
        user_id=user_id,
        movement_type=movement_type,
        quantity_change=quantity_change,
        quantity_before=quantity_before,
        quantity_after=quantity_after,
        reference=reference,
        notes=notes
    )
    db.session.add(movement)
    
    # Update product quantity
    product.quantity = quantity_after
    db.session.commit()
    
    return movement

def get_low_stock_products(Product):
    """Get all products that are at or below their reorder level."""
    return Product.query.filter(
        Product.quantity <= Product.reorder_level,
        Product.is_active == True
    ).all()

def format_currency(amount):
    """Format a number as currency."""
    return f"₱{amount:,.2f}"

def validate_positive_number(value, field_name):
    """Validate that a value is a positive number."""
    try:
        num = float(value)
        if num < 0:
            return False, f"{field_name} cannot be negative."
        return True, num
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid number."

def validate_positive_integer(value, field_name):
    """Validate that a value is a positive integer."""
    try:
        num = int(value)
        if num < 0:
            return False, f"{field_name} cannot be negative."
        return True, num
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid whole number."

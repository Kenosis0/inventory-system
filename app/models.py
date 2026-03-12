from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# User Roles
class Role:
    ADMIN = 'admin'
    STAFF = 'staff'

class User(UserMixin, db.Model):
    """User model for authentication and RBAC."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=Role.STAFF)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the password against the hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == Role.ADMIN
    
    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    """Product categories: Books, School Supplies, Uniforms, Exclusive Materials."""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    """Product model for inventory items."""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)  # Stock Keeping Unit
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Pricing
    cost_price = db.Column(db.Float, nullable=False, default=0.0)  # Purchase cost
    selling_price = db.Column(db.Float, nullable=False, default=0.0)
    
    # Stock management
    quantity = db.Column(db.Integer, nullable=False, default=0)
    reorder_level = db.Column(db.Integer, nullable=False, default=10)  # Low stock threshold
    
    # Book-specific fields (nullable for non-book items)
    isbn = db.Column(db.String(20))
    author = db.Column(db.String(200))
    publisher = db.Column(db.String(200))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stock_movements = db.relationship('StockMovement', backref='product', lazy='dynamic')
    transaction_items = db.relationship('TransactionItem', backref='product', lazy='dynamic')
    
    @property
    def is_low_stock(self):
        """Check if product is below reorder level."""
        return self.quantity <= self.reorder_level
    
    def __repr__(self):
        return f'<Product {self.name}>'


class Transaction(db.Model):
    """Sales and Purchase transactions."""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'sale' or 'purchase'
    reference_number = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Transaction details
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    tax = db.Column(db.Float, nullable=False, default=0.0)
    discount = db.Column(db.Float, nullable=False, default=0.0)
    total = db.Column(db.Float, nullable=False, default=0.0)
    
    # For purchases - supplier info
    supplier_name = db.Column(db.String(200))
    
    # For sales - customer info (optional)
    customer_name = db.Column(db.String(200))
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('TransactionItem', backref='transaction', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Transaction {self.reference_number}>'


class TransactionItem(db.Model):
    """Individual items in a transaction."""
    __tablename__ = 'transaction_items'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<TransactionItem {self.product_id} x {self.quantity}>'


class StockMovement(db.Model):
    """Track all stock changes for audit trail."""
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    movement_type = db.Column(db.String(30), nullable=False)  # 'sale', 'purchase', 'adjustment', 'return'
    quantity_change = db.Column(db.Integer, nullable=False)  # Positive for in, negative for out
    quantity_before = db.Column(db.Integer, nullable=False)
    quantity_after = db.Column(db.Integer, nullable=False)
    
    reference = db.Column(db.String(100))  # Transaction reference or adjustment reason
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = db.relationship('User', backref='stock_movements')
    
    def __repr__(self):
        return f'<StockMovement {self.movement_type} {self.quantity_change}>'


class AuditLog(db.Model):
    """Comprehensive audit trail for all system changes."""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable for system actions
    
    action = db.Column(db.String(50), nullable=False)  # 'create', 'update', 'delete', 'login', 'logout'
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer)
    
    # Store what changed
    old_values = db.Column(db.Text)  # JSON string of old values
    new_values = db.Column(db.Text)  # JSON string of new values
    
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AuditLog {self.action} on {self.table_name}>'

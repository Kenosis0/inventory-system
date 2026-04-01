import pytest
import os
import sys
import tempfile

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Category, Product, Role


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    # Create a temporary database
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    # Create tables and seed data
    with app.app_context():
        db.create_all()
        # Seed default categories
        if Category.query.first() is None:
            categories = [
                Category(name='Books', description='Textbooks and reading materials'),
                Category(name='School Supplies', description='Notebooks, pens, pencils'),
                Category(name='Uniforms', description='School uniforms'),
                Category(name='Exclusive Materials', description="School's exclusive supplies")
            ]
            db.session.add_all(categories)
            db.session.commit()
    
    yield app
    
    # Cleanup
    with app.app_context():
        db.session.remove()
        db.drop_all()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def admin_user(app):
    """Create an admin user for testing."""
    user_id = None
    with app.app_context():
        # Delete any existing admin user to avoid conflicts
        existing = User.query.filter_by(username='admin').first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
        
        admin = User(
            username='admin',
            email='admin@test.com',
            role=Role.ADMIN
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        user_id = admin.id
    
    # Return a simple object that acts like the user for ID access
    class UserStub:
        def __init__(self, uid):
            self.id = uid
            self.username = 'admin'
    
    return UserStub(user_id)


@pytest.fixture
def staff_user(app):
    """Create a staff user for testing."""
    user_id = None
    with app.app_context():
        # Delete any existing staff user to avoid conflicts
        existing = User.query.filter_by(username='staff').first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
        
        staff = User(
            username='staff',
            email='staff@test.com',
            role=Role.STAFF
        )
        staff.set_password('staff123')
        db.session.add(staff)
        db.session.commit()
        user_id = staff.id
    
    # Return a simple object that acts like the user for ID access
    class UserStub:
        def __init__(self, uid):
            self.id = uid
            self.username = 'staff'
    
    return UserStub(user_id)


@pytest.fixture
def test_product(app):
    """Create a test product and return its ID."""
    with app.app_context():
        category = Category.query.first()
        product = Product(
            sku='TEST001',
            name='Test Product',
            category_id=category.id,
            cost_price=10.0,
            selling_price=15.0,
            quantity=100,
            reorder_level=10
        )
        db.session.add(product)
        db.session.commit()
        product_id = product.id
    
    # Return a simple object that acts like the product for ID access
    class ProductStub:
        def __init__(self, pid):
            self.id = pid
    
    return ProductStub(product_id)

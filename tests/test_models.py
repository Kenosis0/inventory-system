"""Tests for database models."""
import pytest
from app.models import User, Category, Product, Transaction, TransactionItem, StockMovement, Role, db


class TestUserModel:
    """Test cases for the User model."""
    
    def test_user_creation(self, app):
        """Test creating a user."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com', role=Role.STAFF)
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == 'testuser'
            assert user.role == Role.STAFF
            assert user.is_active
    
    def test_user_is_admin(self, app):
        """Test the is_admin method."""
        with app.app_context():
            admin = User(username='admin', email='admin@example.com', role=Role.ADMIN)
            staff = User(username='staff', email='staff@example.com', role=Role.STAFF)
            
            assert admin.is_admin()
            assert not staff.is_admin()
    
    def test_duplicate_username_raises_error(self, app, admin_user):
        """Test that duplicate usernames raise an error."""
        with app.app_context():
            with pytest.raises(Exception):  # Should raise IntegrityError
                duplicate = User(username='admin', email='different@example.com')
                db.session.add(duplicate)
                db.session.commit()


class TestProductModel:
    """Test cases for the Product model."""
    
    def test_product_creation(self, app, test_product):
        """Test creating a product."""
        with app.app_context():
            product = db.session.get(Product, test_product.id)
            assert product.sku == 'TEST001'
            assert product.name == 'Test Product'
            assert product.quantity == 100
            assert product.is_active
    
    def test_is_low_stock_property(self, app, test_product):
        """Test the is_low_stock computed property."""
        with app.app_context():
            product = db.session.get(Product, test_product.id)
            
            # Initially not low stock
            assert product.is_low_stock is False
            
            # Lower quantity to trigger low stock
            product.quantity = 5
            db.session.commit()
            product = db.session.get(Product, test_product.id)
            assert product.is_low_stock is True
            
            # Exactly at reorder level
            product.quantity = 10
            db.session.commit()
            product = db.session.get(Product, test_product.id)
            assert product.is_low_stock is True
    
    def test_duplicate_sku_raises_error(self, app, test_product):
        """Test that duplicate SKUs raise an error."""
        with app.app_context():
            with pytest.raises(Exception):  # Should raise IntegrityError
                duplicate = Product(
                    sku='TEST001',  # Same as test_product
                    name='Another Product',
                    category_id=1,
                    cost_price=10.0,
                    selling_price=15.0,
                    quantity=50
                )
                db.session.add(duplicate)
                db.session.commit()


class TestCategoryModel:
    """Test cases for the Category model."""
    
    def test_category_has_products(self, app, test_product):
        """Test that categories have a relationship to products."""
        with app.app_context():
            category = Category.query.first()
            product = db.session.get(Product, test_product.id)
            
            assert product in category.products
            assert category.products.count() > 0


class TestTransactionModel:
    """Test cases for the Transaction model."""
    
    def test_transaction_creation(self, app, admin_user, test_product):
        """Test creating a transaction."""
        with app.app_context():
            user = db.session.get(User, admin_user.id)
            transaction = Transaction(
                transaction_type='sale',
                reference_number='SAL-20260401120000-ABC123',
                user_id=user.id,
                subtotal=100.0,
                tax=0.0,
                discount=0.0,
                total=100.0,
                customer_name='Test Customer'
            )
            db.session.add(transaction)
            db.session.commit()
            
            assert transaction.id is not None
            assert transaction.reference_number == 'SAL-20260401120000-ABC123'
            assert transaction.transaction_type == 'sale'
    
    def test_transaction_items_cascade_delete(self, app, admin_user, test_product):
        """Test that deleting a transaction deletes its items."""
        with app.app_context():
            user = db.session.get(User, admin_user.id)
            product = db.session.get(Product, test_product.id)
            
            transaction = Transaction(
                transaction_type='sale',
                reference_number='SAL-20260401120001-XYZ789',
                user_id=user.id,
                subtotal=50.0,
                tax=0.0,
                discount=0.0,
                total=50.0
            )
            db.session.add(transaction)
            db.session.flush()
            
            item = TransactionItem(
                transaction_id=transaction.id,
                product_id=product.id,
                quantity=5,
                unit_price=10.0,
                total_price=50.0
            )
            db.session.add(item)
            db.session.commit()
            
            transaction_id = transaction.id
            item_count_before = TransactionItem.query.filter_by(transaction_id=transaction_id).count()
            assert item_count_before == 1
            
            # Delete transaction
            db.session.delete(transaction)
            db.session.commit()
            
            # Check that items were deleted
            item_count_after = TransactionItem.query.filter_by(transaction_id=transaction_id).count()
            assert item_count_after == 0


class TestStockMovementModel:
    """Test cases for the StockMovement model."""
    
    def test_stock_movement_creation(self, app, admin_user, test_product):
        """Test creating a stock movement record."""
        with app.app_context():
            user = db.session.get(User, admin_user.id)
            product = db.session.get(Product, test_product.id)
            
            movement = StockMovement(
                product_id=product.id,
                user_id=user.id,
                movement_type='sale',
                quantity_change=-10,
                quantity_before=100,
                quantity_after=90,
                reference='SAL-TEST',
                notes='Test sale'
            )
            db.session.add(movement)
            db.session.commit()
            
            assert movement.id is not None
            assert movement.quantity_change == -10
            assert movement.movement_type == 'sale'

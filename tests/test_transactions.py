"""Tests for transaction functionality."""
import pytest
from app.models import Transaction, TransactionItem, Product, Supplier, StockMovement, db


class TestTransactionList:
    """Test cases for listing transactions."""
    
    def test_transaction_list_displays(self, client, staff_user):
        """Test that the transaction list page displays."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        response = client.get('/transactions/')
        assert response.status_code == 200
        assert b'Transaction' in response.data or b'transaction' in response.data


class TestSaleTransaction:
    """Test cases for sale transactions."""
    
    def test_sale_form_loads(self, client, staff_user):
        """Test that the sale form loads."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        response = client.get('/transactions/new-sale')
        assert response.status_code == 200
        assert b'Sale' in response.data or b'sale' in response.data
    
    def test_create_sale_transaction(self, client, staff_user, test_product, app):
        """Test creating a sale transaction."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        
        response = client.post('/transactions/new-sale', data={
            'customer_name': 'Test Customer',
            'product_id[]': [str(test_product.id)],
            'quantity[]': ['5'],
            'discount': '0',
            'notes': 'Test sale'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should show success message or transaction details
        assert b'successfully' in response.data.lower() or b'Sale' in response.data
        
        # Verify stock was decremented
        with app.app_context():
            product = db.session.get(Product, test_product.id)
            assert product.quantity == 95  # 100 - 5
    
    def test_sale_with_insufficient_stock(self, client, staff_user, test_product):
        """Test that sales with insufficient stock are rejected."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        
        response = client.post('/transactions/new-sale', data={
            'customer_name': 'Test Customer',
            'product_id[]': [str(test_product.id)],
            'quantity[]': ['200'],  # More than available (100)
            'discount': '0'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'insufficient' in response.data.lower() or b'error' in response.data.lower()
    
    def test_sale_stock_movement_recorded(self, client, staff_user, test_product, app):
        """Test that stock movements are recorded for sales."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        
        client.post('/transactions/new-sale', data={
            'customer_name': 'Test Customer',
            'product_id[]': [str(test_product.id)],
            'quantity[]': ['10'],
            'discount': '0'
        }, follow_redirects=True)
        
        # Verify stock movement was recorded
        with app.app_context():
            movement = StockMovement.query.filter_by(
                product_id=test_product.id,
                movement_type='sale'
            ).first()
            assert movement is not None
            assert movement.quantity_change == -10
            assert movement.quantity_before == 100
            assert movement.quantity_after == 90


class TestPurchaseTransaction:
    """Test cases for purchase transactions."""
    
    def test_purchase_form_loads(self, client, staff_user):
        """Test that the purchase form loads."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        response = client.get('/transactions/new-purchase')
        assert response.status_code == 200
        assert b'Purchase' in response.data or b'purchase' in response.data
    
    def test_create_purchase_transaction(self, client, staff_user, test_product, app):
        """Test creating a purchase transaction."""
        # Create a supplier first
        with app.app_context():
            supplier = Supplier(
                name='Test Supplier',
                contact_person='John Doe',
                email='supplier@test.com',
                phone='555-1234',
                address='123 Main St'
            )
            db.session.add(supplier)
            db.session.commit()
            supplier_id = supplier.id
        
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        
        response = client.post('/transactions/new-purchase', data={
            'supplier_id': str(supplier_id),
            'product_id[]': [str(test_product.id)],
            'quantity[]': ['20'],
            'unit_cost[]': ['8.00'],
            'notes': 'Test purchase'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'successfully' in response.data.lower() or b'Purchase' in response.data
        
        # Verify stock was incremented
        with app.app_context():
            product = db.session.get(Product, test_product.id)
            assert product.quantity == 120  # 100 + 20
    
    def test_purchase_without_supplier(self, client, staff_user, test_product):
        """Test that purchase without supplier is rejected."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        
        response = client.post('/transactions/new-purchase', data={
            'supplier_id': '',  # No supplier
            'product_id[]': [str(test_product.id)],
            'quantity[]': ['20'],
            'unit_cost[]': ['8.00']
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'supplier' in response.data.lower() or b'error' in response.data.lower()
    
    def test_purchase_stock_movement_recorded(self, client, staff_user, test_product, app):
        """Test that stock movements are recorded for purchases."""
        with app.app_context():
            supplier = Supplier(name='Test Supplier')
            db.session.add(supplier)
            db.session.commit()
            supplier_id = supplier.id
        
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        
        client.post('/transactions/new-purchase', data={
            'supplier_id': str(supplier_id),
            'product_id[]': [str(test_product.id)],
            'quantity[]': ['15'],
            'unit_cost[]': ['9.00']
        }, follow_redirects=True)
        
        # Verify stock movement was recorded
        with app.app_context():
            movement = StockMovement.query.filter_by(
                product_id=test_product.id,
                movement_type='purchase'
            ).first()
            assert movement is not None
            assert movement.quantity_change == 15
            assert movement.quantity_before == 100
            assert movement.quantity_after == 115


class TestTransactionView:
    """Test cases for viewing transaction details."""
    
    def test_view_transaction_details(self, client, staff_user, app):
        """Test viewing transaction details."""
        with app.app_context():
            user = app.config.get('TEST_USER') or staff_user
            from app.models import User
            staff = User.query.filter_by(username='staff').first()
            
            transaction = Transaction(
                transaction_type='sale',
                reference_number='SAL-20260401120000-ABC123',
                user_id=staff.id,
                subtotal=100.0,
                tax=0.0,
                discount=0.0,
                total=100.0
            )
            db.session.add(transaction)
            db.session.commit()
            transaction_id = transaction.id
        
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        
        response = client.get(f'/transactions/{transaction_id}')
        assert response.status_code == 200
        assert b'SAL-20260401120000-ABC123' in response.data


class TestStockAdjustment:
    """Test cases for manual stock adjustments."""
    
    def test_adjust_stock_page_loads(self, client, staff_user, test_product):
        """Test that the adjust stock page loads."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        response = client.get(f'/products/{test_product.id}/adjust-stock')
        assert response.status_code == 200
        assert b'Adjust' in response.data or b'stock' in response.data.lower()
    
    def test_add_stock(self, client, staff_user, test_product, app):
        """Test adding stock via adjustment."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        
        response = client.post(f'/products/{test_product.id}/adjust-stock', data={
            'adjustment_type': 'add',
            'quantity': '25',
            'reason': 'Inventory correction'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify stock was increased
        with app.app_context():
            product = db.session.get(Product, test_product.id)
            assert product.quantity == 125  # 100 + 25
    
    def test_subtract_stock(self, client, staff_user, test_product, app):
        """Test subtracting stock via adjustment."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        
        response = client.post(f'/products/{test_product.id}/adjust-stock', data={
            'adjustment_type': 'subtract',
            'quantity': '15',
            'reason': 'Damaged items'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify stock was decreased
        with app.app_context():
            product = db.session.get(Product, test_product.id)
            assert product.quantity == 85  # 100 - 15
    
    def test_stock_adjustment_movement_recorded(self, client, staff_user, test_product, app):
        """Test that stock movements are recorded for adjustments."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        
        client.post(f'/products/{test_product.id}/adjust-stock', data={
            'adjustment_type': 'add',
            'quantity': '10',
            'reason': 'Test adjustment'
        }, follow_redirects=True)
        
        # Verify stock movement was recorded
        with app.app_context():
            movement = StockMovement.query.filter_by(
                product_id=test_product.id,
                movement_type='adjustment'
            ).first()
            assert movement is not None
            assert movement.quantity_change == 10

"""Tests for product management functionality."""
import pytest
from app.models import Product, Category, db


class TestProductList:
    """Test cases for listing products."""
    
    def test_product_list_displays(self, client, admin_user, test_product):
        """Test that the product list page displays products."""
        client.post('/', data={
            'username': 'admin',
            'password': 'admin123'
        })
        response = client.get('/products/')
        assert response.status_code == 200
        assert b'Test Product' in response.data or b'TEST001' in response.data
    
    def test_product_list_pagination(self, client, admin_user, app):
        """Test that product list includes pagination."""
        # Create multiple products
        with app.app_context():
            category = Category.query.first()
            for i in range(30):
                product = Product(
                    sku=f'TEST{i:03d}',
                    name=f'Test Product {i}',
                    category_id=category.id,
                    cost_price=10.0,
                    selling_price=15.0,
                    quantity=100
                )
                db.session.add(product)
            db.session.commit()
        
        client.post('/', data={
            'username': 'admin',
            'password': 'admin123'
        })
        response = client.get('/products/')
        assert response.status_code == 200
        # Should have pagination
        assert b'page' in response.data.lower() or b'2' in response.data
    
    def test_low_stock_filter(self, client, admin_user, app):
        """Test filtering for low stock products."""
        with app.app_context():
            category = Category.query.first()
            product = Product(
                sku='LOW001',
                name='Low Stock Product',
                category_id=category.id,
                cost_price=10.0,
                selling_price=15.0,
                quantity=5,  # Below default reorder level of 10
                reorder_level=10
            )
            db.session.add(product)
            db.session.commit()
        
        client.post('/', data={
            'username': 'admin',
            'password': 'admin123'
        })
        response = client.get('/products/low-stock')
        assert response.status_code == 200
        assert b'Low Stock Product' in response.data or b'LOW001' in response.data


class TestProductCreation:
    """Test cases for creating products."""
    
    def test_add_product_page_loads(self, client, staff_user):
        """Test that the add product page loads."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        response = client.get('/products/add')
        assert response.status_code == 200
        assert b'Add' in response.data or b'Product' in response.data
    
    def test_create_product_success(self, client, staff_user):
        """Test creating a new product successfully."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        response = client.post('/products/add', data={
            'sku': 'NEW001',
            'name': 'New Product',
            'description': 'A test product',
            'category_id': 1,
            'cost_price': '10.00',
            'selling_price': '15.00',
            'reorder_level': '10',
            'isbn': '',
            'author': '',
            'publisher': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'successfully' in response.data.lower() or b'New Product' in response.data
    
    def test_create_product_missing_name(self, client, staff_user):
        """Test creating a product without a name fails."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        response = client.post('/products/add', data={
            'sku': 'NEW002',
            'name': '',  # Missing name
            'description': 'A test product',
            'category_id': 1,
            'cost_price': '10.00',
            'selling_price': '15.00',
            'reorder_level': '10'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'required' in response.data.lower() or b'error' in response.data.lower()
    
    def test_duplicate_sku_fails(self, client, staff_user, test_product):
        """Test creating a product with duplicate SKU fails."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        response = client.post('/products/add', data={
            'sku': 'TEST001',  # Same as test_product
            'name': 'Another Product',
            'description': 'A test product',
            'category_id': 1,
            'cost_price': '10.00',
            'selling_price': '15.00',
            'reorder_level': '10'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'already exists' in response.data.lower() or b'error' in response.data.lower()


class TestProductEditing:
    """Test cases for editing products."""
    
    def test_edit_product_page_loads(self, client, staff_user, test_product):
        """Test that the edit product page loads."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        response = client.get(f'/products/{test_product.id}/edit')
        assert response.status_code == 200
        assert b'Test Product' in response.data
    
    def test_edit_product_success(self, client, staff_user, test_product):
        """Test editing a product successfully."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        response = client.post(f'/products/{test_product.id}/edit', data={
            'sku': 'TEST001',
            'name': 'Updated Product Name',
            'description': 'Updated description',
            'category_id': 1,
            'cost_price': '12.00',
            'selling_price': '18.00',
            'reorder_level': '15'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Updated Product Name' in response.data or b'successfully' in response.data.lower()


class TestProductView:
    """Test cases for viewing product details."""
    
    def test_view_product_details(self, client, staff_user, test_product):
        """Test viewing product details page."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        response = client.get(f'/products/{test_product.id}')
        assert response.status_code == 200
        assert b'Test Product' in response.data
        assert b'TEST001' in response.data


class TestProductSearch:
    """Test cases for searching products."""
    
    def test_product_search_by_name(self, client, staff_user, test_product):
        """Test searching for products by name."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        response = client.get('/products/?search=Test%20Product')
        assert response.status_code == 200
        assert b'Test Product' in response.data
    
    def test_product_search_by_sku(self, client, staff_user, test_product):
        """Test searching for products by SKU."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        response = client.get('/products/?search=TEST001')
        assert response.status_code == 200
        assert b'TEST001' in response.data
    
    def test_product_search_api(self, client, staff_user, test_product):
        """Test the product search API endpoint."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        response = client.get('/products/api/search?q=Test')
        assert response.status_code == 200
        # Should return JSON
        data = response.get_json()
        assert isinstance(data, list)

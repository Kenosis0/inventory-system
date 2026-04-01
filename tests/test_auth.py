"""Tests for authentication and authorization."""
import pytest
from app.models import User, Role, db


class TestAuthentication:
    """Test cases for login and logout functionality."""
    
    def test_login_page_loads(self, client):
        """Test that the login page loads successfully."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data
    
    def test_valid_login(self, client, admin_user):
        """Test login with valid credentials."""
        response = client.post('/', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Dashboard' in response.data
    
    def test_invalid_password(self, client, admin_user):
        """Test login with invalid password."""
        response = client.post('/', data={
            'username': 'admin',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'error' in response.data.lower()
    
    def test_nonexistent_user(self, client):
        """Test login with nonexistent username."""
        response = client.post('/', data={
            'username': 'nonexistent',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'error' in response.data.lower()
    
    def test_logout(self, client, admin_user):
        """Test logout functionality."""
        # Login first
        client.post('/', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        # Then logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data
    
    def test_deactivated_user_cannot_login(self, client, app):
        """Test that deactivated users cannot login."""
        with app.app_context():
            user = User.query.filter_by(username='admin').first()
            user.is_active = False
            db.session.commit()
        
        response = client.post('/', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'error' in response.data.lower()


class TestRoleBasedAccess:
    """Test cases for role-based access control."""
    
    def test_admin_can_access_users_page(self, client, admin_user):
        """Test that admin users can access the user management page."""
        client.post('/', data={
            'username': 'admin',
            'password': 'admin123'
        })
        response = client.get('/users/')
        assert response.status_code == 200
    
    def test_staff_cannot_access_users_page(self, client, staff_user):
        """Test that staff users cannot access the user management page."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })
        response = client.get('/users/')
        assert response.status_code in [302, 403]  # Redirect or Forbidden
    
    def test_unauthenticated_redirected_to_login(self, client):
        """Test that unauthenticated users are redirected to login."""
        response = client.get('/dashboard')
        assert response.status_code == 302  # Redirect
        assert '/login' in response.location or '/' in response.location


class TestPassword:
    """Test cases for password handling."""
    
    def test_password_hashing(self, app):
        """Test that passwords are properly hashed."""
        with app.app_context():
            user = User(username='test_user', email='test@example.com')
            user.set_password('mypassword')
            assert user.password_hash != 'mypassword'
            assert user.check_password('mypassword')
    
    def test_wrong_password_fails(self, app):
        """Test that wrong password fails verification."""
        with app.app_context():
            user = User(username='test_user', email='test@example.com')
            user.set_password('mypassword')
            assert not user.check_password('wrongpassword')

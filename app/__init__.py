from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from .models import db, User, Category, Supplier, Role

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

csrf = CSRFProtect()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.products import products_bp
    from .routes.transactions import transactions_bp
    from .routes.users import users_bp
    from .routes.suppliers import suppliers_bp
    from .routes.reports import reports_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(transactions_bp, url_prefix='/transactions')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(suppliers_bp, url_prefix='/suppliers')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    # Create database tables and seed initial data
    with app.app_context():
        db.create_all()
        seed_initial_data()
    
    return app

def seed_initial_data():
    """Seed the database with initial categories and admin user."""
    # Check if data already exists
    if User.query.first() is None:
        # Create default admin user
        admin = User(
            username='admin',
            email='admin@bookstore.local',
            role=Role.ADMIN
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create default staff user
        staff = User(
            username='staff',
            email='staff@bookstore.local',
            role=Role.STAFF
        )
        staff.set_password('staff123')
        db.session.add(staff)
    
    if Category.query.first() is None:
        # Create default categories
        categories = [
            Category(name='Books', description='Textbooks, novels, reference books, and other reading materials'),
            Category(name='School Supplies', description='Notebooks, pens, pencils, folders, and other school essentials'),
            Category(name='Uniforms', description='School uniforms, PE attire, and related clothing items'),
            Category(name='Exclusive Materials', description="School's exclusive supplies and special materials")
        ]
        db.session.add_all(categories)
    
    db.session.commit()

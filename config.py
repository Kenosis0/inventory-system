import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration for the Inventory System."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SQLite database - stored locally in instance folder
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'inventory.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application settings
    ITEMS_PER_PAGE = 20
    LOW_STOCK_THRESHOLD = 10  # Default threshold for low stock alerts

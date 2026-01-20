from flask import Flask

def create_app():
    app = Flask(__name__)

    from .routes.pages import pages_bp
    app.register_blueprint(pages_bp)

    return app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-key-123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'

    db.init_app(app)

    # Registering Blueprints instead of individual routes
    from app.auth import auth_bp
    from app.dashboard import dash_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dash_bp, url_prefix='/dashboard')

    with app.app_context():
        db.create_all()

    return app
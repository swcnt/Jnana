"""
Jnana Web Backend Application Factory.

This module creates and configures the Flask application for the Jnana web interface.
"""

import os
import sys
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO

# Add parent directory to path to import Jnana core
parent_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(parent_dir))

# Initialize extensions
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")

def create_app(config_name='development'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        f'sqlite:///{Path(__file__).parent.parent / "instance" / "jnana.db"}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Jnana configuration
    app.config['JNANA_CONFIG_PATH'] = os.environ.get(
        'JNANA_CONFIG_PATH',
        str(parent_dir / 'config' / 'models.yaml')
    )
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    socketio.init_app(app, async_mode='eventlet')
    
    # Register blueprints
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Initialize Jnana system
    from .services import JnanaWebService
    app.jnana_service = JnanaWebService(app.config['JNANA_CONFIG_PATH'])
    
    return app

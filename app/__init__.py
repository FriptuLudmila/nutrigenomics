"""
Flask Application Factory
=========================
Creates and configures the Flask application with MongoDB.
"""
from flask import Flask
from flask_cors import CORS
from .config import config
from .database import init_db


def create_app(config_name='default'):
    """
    Application factory function.

    Args:
        config_name: Configuration to use ('development', 'production', 'default')

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Enable CORS for frontend
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000"]}})

    # Initialize database connection
    with app.app_context():
        if not init_db(app):
            print("[WARNING] Database not connected. Some features may not work.")

    # Register blueprints (routes)
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register main route for health check
    @app.route('/')
    def index():
        from .database import db
        return {
            'status': 'running',
            'app': 'Nutrigenomics API',
            'version': '1.1.0',
            'database': 'connected' if db.is_connected else 'disconnected',
            'endpoints': {
                'upload': 'POST /api/upload',
                'analyze': 'POST /api/analyze',
                'questionnaire': 'POST /api/questionnaire',
                'recommendations': 'GET /api/recommendations/<session_id>',
                'delete_data': 'DELETE /api/session/<session_id>'
            }
        }
    
    return app

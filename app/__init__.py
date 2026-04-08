"""
Flask Application Factory
=========================
Creates and configures the Flask application with MongoDB.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_talisman import Talisman
from .config import config
from .database import init_db
from .limiter import limiter


def create_app(config_name='default'):
    """
    Application factory function.

    Args:
        config_name: Configuration to use ('development', 'production', 'default')

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    app.config.from_object(config[config_name])

    CORS(
        app,
        origins=app.config['CORS_ORIGINS'],
        supports_credentials=True,
        allow_headers=['Content-Type', 'Authorization'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    )

    Talisman(
        app,
        force_https=not app.config['DEBUG'],   # only enforce HTTPS in production
        strict_transport_security=not app.config['DEBUG'],
        content_security_policy=False,         # API serves JSON, not HTML — CSP not applicable
        x_content_type_options=True,           # X-Content-Type-Options: nosniff
        x_frame_options='DENY',                # X-Frame-Options: DENY
        referrer_policy='strict-origin-when-cross-origin',
    )

    limiter.init_app(app)

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({'error': 'Too many requests. Please slow down and try again later.'}), 429

    from .encryption import get_encryptor
    get_encryptor()

    with app.app_context():
        if not init_db(app):
            print("[WARNING] Database not connected. Some features may not work.")

    from .routes import api_bp
    from .auth_routes import auth_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
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

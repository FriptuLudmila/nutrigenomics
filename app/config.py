"""
Application Configuration
=========================
Settings for the Flask application with MongoDB.
"""

import os
from pathlib import Path

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    """Base configuration"""
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Upload settings
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'csv', 'zip'}
    
    # Ensure upload folder exists
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    
    # MongoDB settings
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB = os.environ.get('MONGODB_DB', 'nutrigenomics')
    
    # Encryption key (IMPORTANT: Set this in production!)
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', None)
    
    # Debug mode
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Required in production


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

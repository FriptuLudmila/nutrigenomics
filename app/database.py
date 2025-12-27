"""
Database Connection Module
==========================
Handles MongoDB connection and provides database access.
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os


class Database:
    """
    MongoDB database wrapper with connection management.
    
    Usage:
        from app.database import db
        
        # Access collections
        db.sessions.insert_one({...})
        db.genetic_results.find_one({...})
    """
    
    def __init__(self):
        self.client = None
        self.db = None
        self._connected = False
    
    def connect(self, uri=None, db_name=None):
        """
        Connect to MongoDB.
        
        Args:
            uri: MongoDB connection string (default: localhost)
            db_name: Database name (default: nutrigenomics)
        """
        # Get connection settings from environment or use defaults
        uri = uri or os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
        db_name = db_name or os.environ.get('MONGODB_DB', 'nutrigenomics')
        
        try:
            # Create client with timeout
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            
            # Test connection
            self.client.admin.command('ping')
            
            # Select database
            self.db = self.client[db_name]
            self._connected = True
            
            print(f"[OK] Connected to MongoDB: {db_name}")
            
            # Create indexes for better performance
            self._create_indexes()
            
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"[ERROR] MongoDB connection failed: {e}")
            print("Make sure MongoDB is running on localhost:27017")
            self._connected = False
            return False
    
    def _create_indexes(self):
        """Create database indexes for performance"""
        # Sessions collection - index on session_id
        self.db.sessions.create_index("session_id", unique=True)
        
        # Sessions - index on created_at for cleanup of old sessions
        self.db.sessions.create_index("created_at")
        
        # Genetic results - index on session_id
        self.db.genetic_results.create_index("session_id", unique=True)
        
        print("    Database indexes created")
    
    def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            self._connected = False
            print("[OK] Disconnected from MongoDB")
    
    @property
    def is_connected(self):
        """Check if database is connected"""
        return self._connected
    
    # Collection shortcuts
    @property
    def sessions(self):
        """Sessions collection"""
        return self.db.sessions if self.db is not None else None

    @property
    def genetic_results(self):
        """Genetic results collection"""
        return self.db.genetic_results if self.db is not None else None

    @property
    def questionnaires(self):
        """Questionnaires collection"""
        return self.db.questionnaires if self.db is not None else None

    @property
    def recommendations(self):
        """Recommendations collection"""
        return self.db.recommendations if self.db is not None else None


# Global database instance
db = Database()


def init_db(app=None):
    """
    Initialize database connection.
    Call this when starting the Flask app.
    
    Args:
        app: Flask application (optional, for getting config)
    """
    if app:
        uri = app.config.get('MONGODB_URI', 'mongodb://localhost:27017/')
        db_name = app.config.get('MONGODB_DB', 'nutrigenomics')
    else:
        uri = None
        db_name = None
    
    return db.connect(uri, db_name)


def get_db():
    """Get database instance"""
    if not db.is_connected:
        db.connect()
    return db

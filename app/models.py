"""
Database Models
===============
Data models and schemas for MongoDB collections.
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
import uuid


@dataclass
class Session:
    """
    User session model.
    Tracks the state of a user's analysis workflow.
    """
    session_id: str
    filepath: str
    original_filename: str
    status: str  # 'uploaded', 'analyzed', 'questionnaire_completed', 'complete'
    created_at: datetime
    updated_at: datetime
    file_size_bytes: int = 0
    
    # Flags for what data exists
    has_genetic_results: bool = False
    has_questionnaire: bool = False
    has_recommendations: bool = False
    
    @classmethod
    def create_new(cls, filepath: str, filename: str, file_size: int = 0):
        """Create a new session"""
        now = datetime.utcnow()
        return cls(
            session_id=str(uuid.uuid4()),
            filepath=filepath,
            original_filename=filename,
            status='uploaded',
            created_at=now,
            updated_at=now,
            file_size_bytes=file_size,
            has_genetic_results=False,
            has_questionnaire=False,
            has_recommendations=False
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for MongoDB"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from MongoDB document"""
        return cls(**data)


@dataclass
class GeneticResults:
    """
    Genetic analysis results model.
    Stores the analyzed SNP data (encrypted).
    """
    session_id: str
    source: str  # '23andMe', 'AncestryDNA', etc.
    snp_count: int
    build: int  # Reference genome build (37, 38)
    findings_encrypted: List[Dict]  # Encrypted genetic findings
    summary: Dict  # Risk level counts (not encrypted)
    analyzed_at: datetime
    
    @classmethod
    def create(cls, session_id: str, file_info: Dict, encrypted_findings: List[Dict], summary: Dict):
        """Create genetic results entry"""
        return cls(
            session_id=session_id,
            source=file_info.get('source', 'Unknown'),
            snp_count=file_info.get('snp_count', 0),
            build=file_info.get('build', 37),
            findings_encrypted=encrypted_findings,
            summary=summary,
            analyzed_at=datetime.utcnow()
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for MongoDB"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from MongoDB document"""
        return cls(**data)


@dataclass
class Questionnaire:
    """
    Lifestyle questionnaire responses model.
    """
    session_id: str
    answers: Dict[str, Any]
    submitted_at: datetime
    
    # Individual fields for easier querying
    age: Optional[int] = None
    sex: Optional[str] = None
    activity_level: Optional[str] = None
    diet_type: Optional[str] = None
    alcohol_frequency: Optional[str] = None
    caffeine_cups_per_day: Optional[int] = None
    digestive_issues: Optional[List[str]] = None
    health_goals: Optional[List[str]] = None
    current_supplements: Optional[List[str]] = None
    known_allergies: Optional[List[str]] = None
    
    @classmethod
    def create(cls, session_id: str, answers: Dict):
        """Create questionnaire entry"""
        return cls(
            session_id=session_id,
            answers=answers,
            submitted_at=datetime.utcnow(),
            age=answers.get('age'),
            sex=answers.get('sex'),
            activity_level=answers.get('activity_level'),
            diet_type=answers.get('diet_type'),
            alcohol_frequency=answers.get('alcohol_frequency'),
            caffeine_cups_per_day=answers.get('caffeine_cups_per_day'),
            digestive_issues=answers.get('digestive_issues', []),
            health_goals=answers.get('health_goals', []),
            current_supplements=answers.get('current_supplements', []),
            known_allergies=answers.get('known_allergies', [])
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for MongoDB"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from MongoDB document"""
        return cls(**data)


@dataclass
class Recommendations:
    """
    Generated recommendations model.
    """
    session_id: str
    recommendations: Dict[str, Any]
    generated_at: datetime
    
    @classmethod
    def create(cls, session_id: str, recommendations: Dict):
        """Create recommendations entry"""
        return cls(
            session_id=session_id,
            recommendations=recommendations,
            generated_at=datetime.utcnow()
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for MongoDB"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from MongoDB document"""
        return cls(**data)


# ============================================
# Database Operations Helper Functions
# ============================================

def save_session(db, session: Session) -> bool:
    """Save or update a session in the database"""
    try:
        session.updated_at = datetime.utcnow()
        db.sessions.update_one(
            {'session_id': session.session_id},
            {'$set': session.to_dict()},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save session: {e}")
        return False


def get_session(db, session_id: str) -> Optional[Session]:
    """Get a session by ID"""
    try:
        doc = db.sessions.find_one({'session_id': session_id})
        if doc:
            doc.pop('_id', None)  # Remove MongoDB _id
            return Session.from_dict(doc)
        return None
    except Exception as e:
        print(f"[ERROR] Failed to get session: {e}")
        return None


def save_genetic_results(db, results: GeneticResults) -> bool:
    """Save genetic analysis results"""
    try:
        db.genetic_results.update_one(
            {'session_id': results.session_id},
            {'$set': results.to_dict()},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save genetic results: {e}")
        return False


def get_genetic_results(db, session_id: str) -> Optional[GeneticResults]:
    """Get genetic results by session ID"""
    try:
        doc = db.genetic_results.find_one({'session_id': session_id})
        if doc:
            doc.pop('_id', None)
            return GeneticResults.from_dict(doc)
        return None
    except Exception as e:
        print(f"[ERROR] Failed to get genetic results: {e}")
        return None


def save_questionnaire(db, questionnaire: Questionnaire) -> bool:
    """Save questionnaire responses"""
    try:
        db.questionnaires.update_one(
            {'session_id': questionnaire.session_id},
            {'$set': questionnaire.to_dict()},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save questionnaire: {e}")
        return False


def get_questionnaire(db, session_id: str) -> Optional[Questionnaire]:
    """Get questionnaire by session ID"""
    try:
        doc = db.questionnaires.find_one({'session_id': session_id})
        if doc:
            doc.pop('_id', None)
            return Questionnaire.from_dict(doc)
        return None
    except Exception as e:
        print(f"[ERROR] Failed to get questionnaire: {e}")
        return None


def save_recommendations(db, recommendations: Recommendations) -> bool:
    """Save generated recommendations"""
    try:
        db.recommendations.update_one(
            {'session_id': recommendations.session_id},
            {'$set': recommendations.to_dict()},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save recommendations: {e}")
        return False


def get_recommendations(db, session_id: str) -> Optional[Recommendations]:
    """Get recommendations by session ID"""
    try:
        doc = db.recommendations.find_one({'session_id': session_id})
        if doc:
            doc.pop('_id', None)
            return Recommendations.from_dict(doc)
        return None
    except Exception as e:
        print(f"[ERROR] Failed to get recommendations: {e}")
        return None


def delete_session_data(db, session_id: str) -> bool:
    """Delete all data for a session (GDPR compliance)"""
    try:
        db.sessions.delete_one({'session_id': session_id})
        db.genetic_results.delete_one({'session_id': session_id})
        db.questionnaires.delete_one({'session_id': session_id})
        db.recommendations.delete_one({'session_id': session_id})
        return True
    except Exception as e:
        print(f"[ERROR] Failed to delete session data: {e}")
        return False

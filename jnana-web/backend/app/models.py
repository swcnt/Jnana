"""
Database models for Jnana web interface.

This module defines SQLAlchemy models for storing sessions, hypotheses,
and other data in the web interface.
"""

from datetime import datetime
from . import db


class Session(db.Model):
    """Research session model."""
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False)
    research_goal = db.Column(db.Text, nullable=False)
    mode = db.Column(db.String(20), default='interactive')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert session to dictionary."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'research_goal': self.research_goal,
            'mode': self.mode,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'hypothesis_count': 0  # Will be implemented later
        }

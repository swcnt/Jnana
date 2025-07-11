"""
Storage management for Jnana system.

This module provides unified storage capabilities for hypotheses and session data,
supporting both file-based and database storage options.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging

from .unified_hypothesis import UnifiedHypothesis
from .data_migration import DataMigration


class JnanaStorage:
    """Unified storage manager for Jnana system."""
    
    def __init__(self, storage_path: Union[str, Path], storage_type: str = "json"):
        """
        Initialize storage manager.
        
        Args:
            storage_path: Path to storage location (file or database)
            storage_type: Type of storage ("json", "sqlite")
        """
        self.storage_path = Path(storage_path)
        self.storage_type = storage_type.lower()
        self.logger = logging.getLogger(__name__)
        
        if self.storage_type == "sqlite":
            self._init_database()
        elif self.storage_type == "json":
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
    
    def _init_database(self):
        """Initialize SQLite database schema."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS hypotheses (
                    hypothesis_id TEXT PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    description TEXT,
                    experimental_validation TEXT,
                    created_at REAL,
                    updated_at REAL,
                    generation_timestamp TEXT,
                    version INTEGER,
                    version_string TEXT,
                    hypothesis_type TEXT,
                    hypothesis_number INTEGER,
                    parent_id TEXT,
                    generation_strategy TEXT,
                    notes TEXT,
                    improvements_made TEXT,
                    user_feedback TEXT,
                    data_json TEXT,  -- Full JSON representation
                    FOREIGN KEY (parent_id) REFERENCES hypotheses (hypothesis_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    research_goal TEXT,
                    created_at REAL,
                    updated_at REAL,
                    metadata_json TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_hypotheses (
                    session_id TEXT,
                    hypothesis_id TEXT,
                    added_at REAL,
                    PRIMARY KEY (session_id, hypothesis_id),
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id),
                    FOREIGN KEY (hypothesis_id) REFERENCES hypotheses (hypothesis_id)
                )
            """)
            
            conn.commit()
    
    def save_hypothesis(self, hypothesis: UnifiedHypothesis) -> None:
        """Save a single hypothesis."""
        if self.storage_type == "sqlite":
            self._save_hypothesis_sqlite(hypothesis)
        else:
            # For JSON, we need to load existing data, update, and save
            hypotheses = self.load_all_hypotheses()
            
            # Update existing or add new
            updated = False
            for i, existing in enumerate(hypotheses):
                if existing.hypothesis_id == hypothesis.hypothesis_id:
                    hypotheses[i] = hypothesis
                    updated = True
                    break
            
            if not updated:
                hypotheses.append(hypothesis)
            
            self._save_hypotheses_json(hypotheses)
    
    def _save_hypothesis_sqlite(self, hypothesis: UnifiedHypothesis) -> None:
        """Save hypothesis to SQLite database."""
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO hypotheses (
                    hypothesis_id, title, content, description, experimental_validation,
                    created_at, updated_at, generation_timestamp, version, version_string,
                    hypothesis_type, hypothesis_number, parent_id, generation_strategy,
                    notes, improvements_made, user_feedback, data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                hypothesis.hypothesis_id,
                hypothesis.title,
                hypothesis.content,
                hypothesis.description,
                hypothesis.experimental_validation,
                hypothesis.created_at,
                hypothesis.updated_at,
                hypothesis.generation_timestamp,
                hypothesis.version,
                hypothesis.version_string,
                hypothesis.hypothesis_type,
                hypothesis.hypothesis_number,
                hypothesis.parent_id,
                hypothesis.generation_strategy,
                hypothesis.notes,
                hypothesis.improvements_made,
                hypothesis.user_feedback,
                hypothesis.to_json()
            ))
            conn.commit()
    
    def _save_hypotheses_json(self, hypotheses: List[UnifiedHypothesis]) -> None:
        """Save hypotheses to JSON file."""
        session_data = {
            "format_version": "jnana-1.0",
            "created_at": datetime.now().isoformat(),
            "hypotheses": [hyp.to_dict() for hyp in hypotheses]
        }
        
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    def load_hypothesis(self, hypothesis_id: str) -> Optional[UnifiedHypothesis]:
        """Load a specific hypothesis by ID."""
        if self.storage_type == "sqlite":
            return self._load_hypothesis_sqlite(hypothesis_id)
        else:
            hypotheses = self.load_all_hypotheses()
            for hyp in hypotheses:
                if hyp.hypothesis_id == hypothesis_id:
                    return hyp
            return None
    
    def _load_hypothesis_sqlite(self, hypothesis_id: str) -> Optional[UnifiedHypothesis]:
        """Load hypothesis from SQLite database."""
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.execute(
                "SELECT data_json FROM hypotheses WHERE hypothesis_id = ?",
                (hypothesis_id,)
            )
            row = cursor.fetchone()
            
            if row:
                data = json.loads(row[0])
                return UnifiedHypothesis.from_dict(data)
            return None
    
    def load_all_hypotheses(self) -> List[UnifiedHypothesis]:
        """Load all hypotheses."""
        if self.storage_type == "sqlite":
            return self._load_all_hypotheses_sqlite()
        else:
            return self._load_all_hypotheses_json()
    
    def _load_all_hypotheses_sqlite(self) -> List[UnifiedHypothesis]:
        """Load all hypotheses from SQLite database."""
        hypotheses = []
        
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.execute("SELECT data_json FROM hypotheses ORDER BY created_at")
            
            for row in cursor:
                try:
                    data = json.loads(row[0])
                    hypothesis = UnifiedHypothesis.from_dict(data)
                    hypotheses.append(hypothesis)
                except Exception as e:
                    self.logger.warning(f"Failed to load hypothesis: {e}")
                    continue
        
        return hypotheses
    
    def _load_all_hypotheses_json(self) -> List[UnifiedHypothesis]:
        """Load all hypotheses from JSON file."""
        if not self.storage_path.exists():
            return []
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            hypotheses = []
            hypotheses_data = session_data.get("hypotheses", [])
            
            for hyp_data in hypotheses_data:
                try:
                    hypothesis = UnifiedHypothesis.from_dict(hyp_data)
                    hypotheses.append(hypothesis)
                except Exception as e:
                    self.logger.warning(f"Failed to load hypothesis: {e}")
                    continue
            
            return hypotheses
            
        except Exception as e:
            self.logger.error(f"Failed to load session file: {e}")
            return []
    
    def delete_hypothesis(self, hypothesis_id: str) -> bool:
        """Delete a hypothesis."""
        if self.storage_type == "sqlite":
            return self._delete_hypothesis_sqlite(hypothesis_id)
        else:
            hypotheses = self.load_all_hypotheses()
            original_count = len(hypotheses)
            hypotheses = [h for h in hypotheses if h.hypothesis_id != hypothesis_id]
            
            if len(hypotheses) < original_count:
                self._save_hypotheses_json(hypotheses)
                return True
            return False
    
    def _delete_hypothesis_sqlite(self, hypothesis_id: str) -> bool:
        """Delete hypothesis from SQLite database."""
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.execute(
                "DELETE FROM hypotheses WHERE hypothesis_id = ?",
                (hypothesis_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def search_hypotheses(self, query: str, field: str = "content") -> List[UnifiedHypothesis]:
        """Search hypotheses by content."""
        hypotheses = self.load_all_hypotheses()
        results = []
        
        query_lower = query.lower()
        
        for hyp in hypotheses:
            if field == "content" and query_lower in hyp.content.lower():
                results.append(hyp)
            elif field == "title" and query_lower in hyp.title.lower():
                results.append(hyp)
            elif field == "description" and query_lower in hyp.description.lower():
                results.append(hyp)
            elif field == "all":
                if (query_lower in hyp.content.lower() or 
                    query_lower in hyp.title.lower() or 
                    query_lower in hyp.description.lower()):
                    results.append(hyp)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics."""
        hypotheses = self.load_all_hypotheses()
        
        stats = {
            "total_hypotheses": len(hypotheses),
            "hypothesis_types": {},
            "generation_strategies": {},
            "average_version": 0,
            "total_feedback_entries": 0,
            "storage_type": self.storage_type,
            "storage_path": str(self.storage_path)
        }
        
        if not hypotheses:
            return stats
        
        # Calculate statistics
        total_versions = 0
        total_feedback = 0
        
        for hyp in hypotheses:
            # Count by type
            hyp_type = hyp.hypothesis_type
            stats["hypothesis_types"][hyp_type] = stats["hypothesis_types"].get(hyp_type, 0) + 1
            
            # Count by generation strategy
            strategy = hyp.generation_strategy or "unknown"
            stats["generation_strategies"][strategy] = stats["generation_strategies"].get(strategy, 0) + 1
            
            # Sum versions and feedback
            total_versions += hyp.version
            total_feedback += len(hyp.feedback_history)
        
        stats["average_version"] = total_versions / len(hypotheses)
        stats["total_feedback_entries"] = total_feedback
        
        return stats

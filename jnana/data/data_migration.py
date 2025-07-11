"""
Data migration utilities for converting between Wisteria, ProtoGnosis, and Jnana formats.

This module provides functions to convert hypothesis data between different formats,
enabling seamless integration and backward compatibility.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from .unified_hypothesis import (
    UnifiedHypothesis, FeedbackEntry, Reference, 
    ScientificHallmarks, TournamentRecord, AgentContribution
)


class DataMigration:
    """Handles data migration between different hypothesis formats."""
    
    @staticmethod
    def from_wisteria(wisteria_data: Dict[str, Any]) -> UnifiedHypothesis:
        """
        Convert Wisteria hypothesis format to UnifiedHypothesis.
        
        Args:
            wisteria_data: Dictionary containing Wisteria hypothesis data
            
        Returns:
            UnifiedHypothesis object
        """
        # Extract basic information
        hypothesis_id = wisteria_data.get("hypothesis_id", "")
        if not hypothesis_id:
            import uuid
            hypothesis_id = str(uuid.uuid4())
        
        title = wisteria_data.get("title", "")
        description = wisteria_data.get("description", "")
        experimental_validation = wisteria_data.get("experimental_validation", "")
        
        # Handle version information
        version_string = wisteria_data.get("version", "1.0")
        try:
            # Convert version string to integer (1.0 -> 1, 1.1 -> 2, etc.)
            if "." in version_string:
                major, minor = version_string.split(".", 1)
                version = int(minor) + 1 if minor else 1
            else:
                version = int(version_string)
        except (ValueError, AttributeError):
            version = 1
            version_string = "1.0"
        
        # Convert timestamps
        generation_timestamp = wisteria_data.get("generation_timestamp", datetime.now().isoformat())
        try:
            created_at = datetime.fromisoformat(generation_timestamp.replace('Z', '+00:00')).timestamp()
        except (ValueError, AttributeError):
            created_at = time.time()
        
        # Convert hallmarks
        hallmarks_data = wisteria_data.get("hallmarks", {})
        hallmarks = ScientificHallmarks(
            testability=hallmarks_data.get("testability", ""),
            specificity=hallmarks_data.get("specificity", ""),
            grounded_knowledge=hallmarks_data.get("grounded_knowledge", ""),
            predictive_power=hallmarks_data.get("predictive_power", ""),
            parsimony=hallmarks_data.get("parsimony", "")
        )
        
        # Convert references
        references = []
        refs_data = wisteria_data.get("references", [])
        for ref_data in refs_data:
            if isinstance(ref_data, dict):
                references.append(Reference(
                    citation=ref_data.get("citation", ""),
                    annotation=ref_data.get("annotation", ""),
                    url=ref_data.get("url"),
                    doi=ref_data.get("doi")
                ))
            elif isinstance(ref_data, str):
                references.append(Reference(citation=ref_data))
        
        # Convert feedback history
        feedback_history = []
        feedback_data = wisteria_data.get("feedback_history", [])
        for fb_data in feedback_data:
            if isinstance(fb_data, dict):
                feedback_history.append(FeedbackEntry(
                    feedback=fb_data.get("feedback", ""),
                    timestamp=fb_data.get("timestamp", datetime.now().isoformat()),
                    version_before=fb_data.get("version_before", "1.0"),
                    version_after=fb_data.get("version_after", "1.1"),
                    user_id=fb_data.get("user_id"),
                    feedback_type=fb_data.get("feedback_type", "user")
                ))
        
        # Create unified hypothesis
        unified = UnifiedHypothesis(
            hypothesis_id=hypothesis_id,
            title=title,
            content=description,  # Use description as content
            description=description,
            experimental_validation=experimental_validation,
            created_at=created_at,
            updated_at=created_at,
            generation_timestamp=generation_timestamp,
            version=version,
            version_string=version_string,
            hypothesis_type=wisteria_data.get("type", "original"),
            hypothesis_number=wisteria_data.get("hypothesis_number", 1),
            hallmarks=hallmarks,
            references=references,
            feedback_history=feedback_history,
            notes=wisteria_data.get("notes", ""),
            improvements_made=wisteria_data.get("improvements_made", ""),
            user_feedback=wisteria_data.get("user_feedback", ""),
            metadata=wisteria_data.get("metadata", {})
        )
        
        return unified
    
    @staticmethod
    def from_protognosis(protognosis_data: Dict[str, Any]) -> UnifiedHypothesis:
        """
        Convert ProtoGnosis hypothesis format to UnifiedHypothesis.
        
        Args:
            protognosis_data: Dictionary containing ProtoGnosis hypothesis data
            
        Returns:
            UnifiedHypothesis object
        """
        # Extract basic information
        hypothesis_id = protognosis_data.get("hypothesis_id", "")
        if not hypothesis_id:
            import uuid
            hypothesis_id = str(uuid.uuid4())
        
        content = protognosis_data.get("content", "")
        metadata = protognosis_data.get("metadata", {})
        
        # Extract metadata fields
        title = metadata.get("title", "")
        description = metadata.get("description", content)  # Use content if no description
        generation_strategy = metadata.get("generation_strategy", "")
        
        # Handle timestamps
        created_at = protognosis_data.get("created_at", time.time())
        updated_at = protognosis_data.get("updated_at", created_at)
        
        # Convert tournament record
        tournament_data = protognosis_data.get("tournament_record", {})
        tournament_record = TournamentRecord(
            wins=tournament_data.get("wins", 0),
            losses=tournament_data.get("losses", 0),
            matches=tournament_data.get("matches", []),
            elo_rating=tournament_data.get("elo_rating"),
            last_match_timestamp=tournament_data.get("last_match_timestamp")
        )
        
        # Create unified hypothesis
        unified = UnifiedHypothesis(
            hypothesis_id=hypothesis_id,
            title=title,
            content=content,
            description=description,
            created_at=created_at,
            updated_at=updated_at,
            generation_timestamp=datetime.fromtimestamp(created_at).isoformat(),
            version=protognosis_data.get("version", 1),
            parent_id=protognosis_data.get("parent_id"),
            children_ids=protognosis_data.get("children_ids", []),
            evaluation_scores=protognosis_data.get("evaluation_scores", {}),
            tournament_record=tournament_record,
            generation_strategy=generation_strategy,
            metadata=metadata
        )
        
        return unified

    @staticmethod
    def load_wisteria_session(file_path: Union[str, Path]) -> List[UnifiedHypothesis]:
        """
        Load hypotheses from a Wisteria session file.

        Args:
            file_path: Path to the Wisteria JSON session file

        Returns:
            List of UnifiedHypothesis objects
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Wisteria session file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            session_data = json.load(f)

        hypotheses = []

        # Handle different Wisteria session formats
        if isinstance(session_data, dict):
            # Check if it's a session with metadata
            if "hypotheses" in session_data:
                hypotheses_data = session_data["hypotheses"]
            else:
                # Assume the entire dict is hypothesis data
                hypotheses_data = [session_data]
        elif isinstance(session_data, list):
            hypotheses_data = session_data
        else:
            raise ValueError("Invalid Wisteria session format")

        for hyp_data in hypotheses_data:
            try:
                unified = DataMigration.from_wisteria(hyp_data)
                hypotheses.append(unified)
            except Exception as e:
                print(f"Warning: Failed to convert hypothesis: {e}")
                continue

        return hypotheses

    @staticmethod
    def load_protognosis_session(file_path: Union[str, Path]) -> List[UnifiedHypothesis]:
        """
        Load hypotheses from a ProtoGnosis session file.

        Args:
            file_path: Path to the ProtoGnosis JSON session file

        Returns:
            List of UnifiedHypothesis objects
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"ProtoGnosis session file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            session_data = json.load(f)

        hypotheses = []

        # ProtoGnosis format typically has hypotheses in the data
        if isinstance(session_data, dict) and "hypotheses" in session_data:
            hypotheses_data = session_data["hypotheses"]
        else:
            raise ValueError("Invalid ProtoGnosis session format")

        for hyp_data in hypotheses_data:
            try:
                # Convert from ProtoGnosis ResearchHypothesis format
                if hasattr(hyp_data, 'to_dict'):
                    hyp_dict = hyp_data.to_dict()
                else:
                    hyp_dict = hyp_data

                unified = DataMigration.from_protognosis(hyp_dict)
                hypotheses.append(unified)
            except Exception as e:
                print(f"Warning: Failed to convert hypothesis: {e}")
                continue

        return hypotheses

    @staticmethod
    def save_unified_session(hypotheses: List[UnifiedHypothesis],
                           file_path: Union[str, Path],
                           metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Save unified hypotheses to a Jnana session file.

        Args:
            hypotheses: List of UnifiedHypothesis objects
            file_path: Path to save the session file
            metadata: Optional session metadata
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        session_data = {
            "format_version": "jnana-1.0",
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "hypotheses": [hyp.to_dict() for hyp in hypotheses]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

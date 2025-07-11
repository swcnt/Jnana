"""
Unified hypothesis data model for Jnana system.

This module provides a unified data structure that can represent hypotheses
from both Wisteria and ProtoGnosis systems, enabling seamless integration.
"""

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class FeedbackEntry:
    """Represents a single feedback entry in the hypothesis refinement process."""
    feedback: str
    timestamp: str
    version_before: str
    version_after: str
    user_id: Optional[str] = None
    feedback_type: str = "user"  # "user", "agent", "system"


@dataclass_json
@dataclass
class Reference:
    """Represents a scientific reference."""
    citation: str
    annotation: str = ""
    url: Optional[str] = None
    doi: Optional[str] = None
    relevance_score: Optional[float] = None


@dataclass_json
@dataclass
class ScientificHallmarks:
    """Scientific evaluation criteria from Wisteria."""
    testability: str = ""
    specificity: str = ""
    grounded_knowledge: str = ""
    predictive_power: str = ""
    parsimony: str = ""


@dataclass_json
@dataclass
class TournamentRecord:
    """Tournament performance tracking from ProtoGnosis."""
    wins: int = 0
    losses: int = 0
    matches: List[Dict[str, Any]] = field(default_factory=list)
    elo_rating: Optional[float] = None
    last_match_timestamp: Optional[str] = None


@dataclass_json
@dataclass
class AgentContribution:
    """Tracks contributions from different agents."""
    agent_id: str
    agent_type: str
    contribution_type: str  # "generation", "refinement", "evaluation", etc.
    timestamp: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass_json
@dataclass
class BiomniVerification:
    """Biomni verification results for biomedical hypotheses."""
    verification_id: str
    verification_type: str  # "general", "genomics", "drug_discovery", "protein", etc.
    is_biologically_plausible: bool
    confidence_score: float  # 0.0 to 1.0
    evidence_strength: str  # "weak", "moderate", "strong"

    # Evidence and insights
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    suggested_experiments: List[str] = field(default_factory=list)
    related_pathways: List[str] = field(default_factory=list)
    molecular_mechanisms: List[str] = field(default_factory=list)

    # Technical metadata
    tools_used: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    biomni_response: str = ""


@dataclass_json
@dataclass
class UnifiedHypothesis:
    """
    Unified hypothesis data structure supporting both Wisteria and ProtoGnosis features.
    
    This class combines the interactive features of Wisteria (feedback tracking,
    scientific evaluation) with the multi-agent capabilities of ProtoGnosis
    (tournament ranking, agent contributions).
    """
    
    # Core identification
    hypothesis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Content (compatible with both systems)
    title: str = ""
    content: str = ""  # ProtoGnosis primary content field
    description: str = ""  # Wisteria detailed description
    experimental_validation: str = ""  # Wisteria experimental plan
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    generation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Version tracking (Wisteria style)
    version: int = 1
    version_string: str = "1.0"  # Human-readable version
    hypothesis_type: str = "original"  # "original", "improvement", "new_alternative"
    
    # Hierarchy (ProtoGnosis style)
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    hypothesis_number: int = 1  # Wisteria numbering system
    
    # Scientific evaluation
    hallmarks: ScientificHallmarks = field(default_factory=ScientificHallmarks)
    evaluation_scores: Dict[str, float] = field(default_factory=dict)
    
    # References and citations
    references: List[Reference] = field(default_factory=list)
    
    # Interactive features (Wisteria)
    feedback_history: List[FeedbackEntry] = field(default_factory=list)
    notes: str = ""
    improvements_made: str = ""
    user_feedback: str = ""  # Latest user feedback
    
    # Multi-agent features (ProtoGnosis)
    tournament_record: TournamentRecord = field(default_factory=TournamentRecord)
    agent_contributions: List[AgentContribution] = field(default_factory=list)
    generation_strategy: str = ""  # ProtoGnosis generation strategy used

    # Biomedical verification (Biomni)
    biomni_verification: Optional[BiomniVerification] = None
    is_biomedical: bool = False
    biomedical_domains: List[str] = field(default_factory=list)  # e.g., ["genomics", "drug_discovery"]

    # System metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Ensure content and description are synchronized
        if self.content and not self.description:
            self.description = self.content
        elif self.description and not self.content:
            self.content = self.description
            
        # Initialize empty hallmarks if needed
        if not isinstance(self.hallmarks, ScientificHallmarks):
            self.hallmarks = ScientificHallmarks()
            
        # Initialize empty tournament record if needed
        if not isinstance(self.tournament_record, TournamentRecord):
            self.tournament_record = TournamentRecord()
    
    def add_feedback(self, feedback: str, user_id: Optional[str] = None, 
                    feedback_type: str = "user") -> None:
        """Add a feedback entry to the hypothesis."""
        old_version = self.version_string
        self.increment_version()
        
        feedback_entry = FeedbackEntry(
            feedback=feedback,
            timestamp=datetime.now().isoformat(),
            version_before=old_version,
            version_after=self.version_string,
            user_id=user_id,
            feedback_type=feedback_type
        )
        
        self.feedback_history.append(feedback_entry)
        self.user_feedback = feedback
        self.updated_at = time.time()
    
    def increment_version(self) -> None:
        """Increment the hypothesis version."""
        self.version += 1
        # Convert to Wisteria-style version string (1.0, 1.1, 1.2, etc.)
        major = 1
        minor = self.version - 1
        self.version_string = f"{major}.{minor}"
        self.updated_at = time.time()
    
    def add_agent_contribution(self, agent_id: str, agent_type: str, 
                             contribution_type: str, details: Dict[str, Any] = None) -> None:
        """Record a contribution from an agent."""
        contribution = AgentContribution(
            agent_id=agent_id,
            agent_type=agent_type,
            contribution_type=contribution_type,
            timestamp=datetime.now().isoformat(),
            details=details or {}
        )
        self.agent_contributions.append(contribution)
        self.updated_at = time.time()
    
    def update_tournament_record(self, won: bool, opponent_id: str, 
                               match_details: Dict[str, Any] = None) -> None:
        """Update tournament performance record."""
        if won:
            self.tournament_record.wins += 1
        else:
            self.tournament_record.losses += 1
        
        match_record = {
            "opponent_id": opponent_id,
            "won": won,
            "timestamp": datetime.now().isoformat(),
            "details": match_details or {}
        }
        self.tournament_record.matches.append(match_record)
        self.tournament_record.last_match_timestamp = match_record["timestamp"]
        self.updated_at = time.time()
    
    def add_reference(self, citation: str, annotation: str = "", 
                     url: Optional[str] = None, doi: Optional[str] = None) -> None:
        """Add a scientific reference."""
        reference = Reference(
            citation=citation,
            annotation=annotation,
            url=url,
            doi=doi
        )
        self.references.append(reference)
        self.updated_at = time.time()
    
    def get_win_rate(self) -> float:
        """Calculate tournament win rate."""
        total_matches = self.tournament_record.wins + self.tournament_record.losses
        if total_matches == 0:
            return 0.0
        return self.tournament_record.wins / total_matches
    
    def get_latest_feedback(self) -> Optional[FeedbackEntry]:
        """Get the most recent feedback entry."""
        if not self.feedback_history:
            return None
        return self.feedback_history[-1]
    
    def to_wisteria_format(self) -> Dict[str, Any]:
        """Convert to Wisteria-compatible format."""
        return {
            "title": self.title,
            "description": self.description,
            "experimental_validation": self.experimental_validation,
            "hallmarks": {
                "testability": self.hallmarks.testability,
                "specificity": self.hallmarks.specificity,
                "grounded_knowledge": self.hallmarks.grounded_knowledge,
                "predictive_power": self.hallmarks.predictive_power,
                "parsimony": self.hallmarks.parsimony
            },
            "references": [ref.to_dict() for ref in self.references],
            "feedback_history": [fb.to_dict() for fb in self.feedback_history],
            "version": self.version_string,
            "type": self.hypothesis_type,
            "hypothesis_number": self.hypothesis_number,
            "generation_timestamp": self.generation_timestamp,
            "notes": self.notes,
            "improvements_made": self.improvements_made
        }
    
    def to_protognosis_format(self) -> Dict[str, Any]:
        """Convert to ProtoGnosis-compatible format."""
        return {
            "hypothesis_id": self.hypothesis_id,
            "content": self.content,
            "metadata": {
                **self.metadata,
                "title": self.title,
                "description": self.description,
                "generation_strategy": self.generation_strategy
            },
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
            "parent_id": self.parent_id,
            "children_ids": self.children_ids,
            "evaluation_scores": self.evaluation_scores,
            "tournament_record": self.tournament_record.to_dict()
        }

    def set_biomni_verification(self, verification: BiomniVerification) -> None:
        """Set Biomni verification results for this hypothesis."""
        self.biomni_verification = verification
        self.is_biomedical = True

        # Update biomedical domains if not already set
        if verification.verification_type not in self.biomedical_domains:
            self.biomedical_domains.append(verification.verification_type)

        # Update metadata
        self.metadata["biomni_verified"] = True
        self.metadata["biomni_confidence"] = verification.confidence_score
        self.metadata["biomni_plausible"] = verification.is_biologically_plausible

        # Update updated timestamp
        self.updated_at = time.time()

    def get_biomni_summary(self) -> Dict[str, Any]:
        """Get a summary of Biomni verification results."""
        if not self.biomni_verification:
            return {"verified": False, "message": "No Biomni verification available"}

        return {
            "verified": True,
            "biologically_plausible": self.biomni_verification.is_biologically_plausible,
            "confidence_score": self.biomni_verification.confidence_score,
            "evidence_strength": self.biomni_verification.evidence_strength,
            "verification_type": self.biomni_verification.verification_type,
            "supporting_evidence_count": len(self.biomni_verification.supporting_evidence),
            "contradicting_evidence_count": len(self.biomni_verification.contradicting_evidence),
            "suggested_experiments_count": len(self.biomni_verification.suggested_experiments),
            "timestamp": self.biomni_verification.timestamp
        }

    def is_biomni_verified(self) -> bool:
        """Check if this hypothesis has been verified by Biomni."""
        return self.biomni_verification is not None

    def get_biomedical_confidence(self) -> float:
        """Get the biomedical confidence score from Biomni verification."""
        if self.biomni_verification:
            return self.biomni_verification.confidence_score
        return 0.0

"""
Data Converter for ProtoGnosis-Jnana Integration.

This module provides conversion utilities between ProtoGnosis ResearchHypothesis
and Jnana UnifiedHypothesis formats.
"""

import time
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..core.agent_core import ResearchHypothesis
from ...data.unified_hypothesis import UnifiedHypothesis, ScientificHallmarks, TournamentRecord


class ProtoGnosisDataConverter:
    """
    Converter for data between ProtoGnosis and Jnana formats.
    """
    
    @staticmethod
    def protognosis_to_unified(pg_hypothesis: ResearchHypothesis) -> UnifiedHypothesis:
        """
        Convert a ProtoGnosis ResearchHypothesis to Jnana UnifiedHypothesis.
        
        Args:
            pg_hypothesis: ProtoGnosis ResearchHypothesis object
            
        Returns:
            UnifiedHypothesis object
        """
        
        # Extract metadata
        metadata = pg_hypothesis.metadata or {}
        
        # Create scientific hallmarks from ProtoGnosis data
        scientific_hallmarks = ScientificHallmarks(
            testability=metadata.get("testability_score", 7.0),
            specificity=metadata.get("specificity_score", 7.0),
            grounded_knowledge=metadata.get("grounded_knowledge_score", 7.0),
            predictive_power=metadata.get("predictive_power_score", 7.0),
            parsimony=metadata.get("parsimony_score", 7.0)
        )
        
        # Create tournament record from ProtoGnosis data
        tournament_record = TournamentRecord(
            matches=pg_hypothesis.tournament_matches,
            wins=pg_hypothesis.tournament_wins,
            losses=pg_hypothesis.tournament_losses,
            elo_rating=pg_hypothesis.elo_rating,
            last_match_timestamp=pg_hypothesis.last_tournament_time
        )
        
        # Create unified hypothesis
        unified_hypothesis = UnifiedHypothesis(
            hypothesis_id=pg_hypothesis.hypothesis_id,
            title=ProtoGnosisDataConverter._extract_title(pg_hypothesis.content),
            description=pg_hypothesis.summary,
            content=pg_hypothesis.content,
            
            # Scientific evaluation
            hallmarks=scientific_hallmarks,
            
            # Timestamps
            created_at=pg_hypothesis.created_at,
            updated_at=time.time(),
            
            # ProtoGnosis specific data
            generation_strategy=metadata.get("strategy", "unknown"),
            tournament_record=tournament_record,
            
            # System metadata
            hypothesis_type="protognosis_generated",
            version_string="1.0"
        )
        
        # Add ProtoGnosis metadata
        unified_hypothesis.metadata.update({
            "protognosis_agent_id": pg_hypothesis.agent_id,
            "protognosis_metadata": metadata,
            "conversion_timestamp": time.time()
        })
        
        return unified_hypothesis
    
    @staticmethod
    def unified_to_protognosis(unified_hypothesis: UnifiedHypothesis) -> ResearchHypothesis:
        """
        Convert a Jnana UnifiedHypothesis to ProtoGnosis ResearchHypothesis.
        
        Args:
            unified_hypothesis: Jnana UnifiedHypothesis object
            
        Returns:
            ResearchHypothesis object
        """
        
        # Extract agent ID from metadata or use default
        agent_id = unified_hypothesis.metadata.get("protognosis_agent_id", "jnana_converter")
        
        # Create ProtoGnosis metadata from unified hypothesis
        pg_metadata = {
            "strategy": unified_hypothesis.generation_strategy,
            "testability_score": unified_hypothesis.hallmarks.testability,
            "specificity_score": unified_hypothesis.hallmarks.specificity,
            "grounded_knowledge_score": unified_hypothesis.hallmarks.grounded_knowledge,
            "predictive_power_score": unified_hypothesis.hallmarks.predictive_power,
            "parsimony_score": unified_hypothesis.hallmarks.parsimony,
            "jnana_metadata": unified_hypothesis.metadata,
            "conversion_timestamp": time.time()
        }
        
        # Create ProtoGnosis hypothesis
        pg_hypothesis = ResearchHypothesis(
            content=unified_hypothesis.content,
            summary=unified_hypothesis.description,
            agent_id=agent_id,
            hypothesis_id=unified_hypothesis.hypothesis_id,
            elo_rating=unified_hypothesis.tournament_record.elo_rating,
            metadata=pg_metadata
        )
        
        # Set tournament data
        pg_hypothesis.tournament_matches = unified_hypothesis.tournament_record.matches
        pg_hypothesis.tournament_wins = unified_hypothesis.tournament_record.wins
        pg_hypothesis.tournament_losses = unified_hypothesis.tournament_record.losses
        pg_hypothesis.last_tournament_time = unified_hypothesis.tournament_record.last_match_timestamp
        
        # Set timestamps
        pg_hypothesis.created_at = unified_hypothesis.created_at
        
        return pg_hypothesis
    
    @staticmethod
    def batch_protognosis_to_unified(pg_hypotheses: List[ResearchHypothesis]) -> List[UnifiedHypothesis]:
        """
        Convert a batch of ProtoGnosis hypotheses to unified format.
        
        Args:
            pg_hypotheses: List of ProtoGnosis ResearchHypothesis objects
            
        Returns:
            List of UnifiedHypothesis objects
        """
        return [
            ProtoGnosisDataConverter.protognosis_to_unified(pg_hyp) 
            for pg_hyp in pg_hypotheses
        ]
    
    @staticmethod
    def batch_unified_to_protognosis(unified_hypotheses: List[UnifiedHypothesis]) -> List[ResearchHypothesis]:
        """
        Convert a batch of unified hypotheses to ProtoGnosis format.
        
        Args:
            unified_hypotheses: List of UnifiedHypothesis objects
            
        Returns:
            List of ResearchHypothesis objects
        """
        return [
            ProtoGnosisDataConverter.unified_to_protognosis(unified_hyp)
            for unified_hyp in unified_hypotheses
        ]
    
    @staticmethod
    def _extract_title(content: str) -> str:
        """
        Extract a title from hypothesis content.
        
        Args:
            content: Hypothesis content text
            
        Returns:
            Extracted title string
        """
        # Try to find a title in the content
        lines = content.split('\n')
        
        # Look for lines that might be titles
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and (
                line.startswith('Title:') or 
                line.startswith('Hypothesis:') or
                line.isupper() or
                len(line) < 100
            ):
                # Clean up the title
                title = line.replace('Title:', '').replace('Hypothesis:', '').strip()
                if title:
                    return title
        
        # Fallback: use first sentence
        sentences = content.split('.')
        if sentences:
            title = sentences[0].strip()
            if len(title) > 100:
                title = title[:100] + "..."
            return title
        
        # Final fallback
        return "Generated Hypothesis"
    
    @staticmethod
    def create_conversion_summary(original_count: int, converted_count: int, 
                                 conversion_type: str) -> Dict[str, Any]:
        """
        Create a summary of the conversion process.
        
        Args:
            original_count: Number of original hypotheses
            converted_count: Number of successfully converted hypotheses
            conversion_type: Type of conversion performed
            
        Returns:
            Dictionary containing conversion summary
        """
        return {
            "conversion_type": conversion_type,
            "original_count": original_count,
            "converted_count": converted_count,
            "success_rate": converted_count / original_count if original_count > 0 else 0,
            "timestamp": datetime.now().isoformat(),
            "conversion_id": str(uuid.uuid4())
        }

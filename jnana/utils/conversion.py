"""
Conversion utilities for Jnana system.
"""

from typing import Dict, List, Any, Optional
from ..data.unified_hypothesis import UnifiedHypothesis
from ..data.data_migration import DataMigration


def convert_wisteria_to_unified(wisteria_data: Dict[str, Any]) -> UnifiedHypothesis:
    """
    Convert Wisteria hypothesis format to UnifiedHypothesis.
    
    Args:
        wisteria_data: Wisteria hypothesis data
        
    Returns:
        UnifiedHypothesis object
    """
    return DataMigration.from_wisteria(wisteria_data)


def convert_protognosis_to_unified(protognosis_data: Dict[str, Any]) -> UnifiedHypothesis:
    """
    Convert ProtoGnosis hypothesis format to UnifiedHypothesis.
    
    Args:
        protognosis_data: ProtoGnosis hypothesis data
        
    Returns:
        UnifiedHypothesis object
    """
    return DataMigration.from_protognosis(protognosis_data)


def convert_unified_to_wisteria(hypothesis: UnifiedHypothesis) -> Dict[str, Any]:
    """
    Convert UnifiedHypothesis to Wisteria format.
    
    Args:
        hypothesis: UnifiedHypothesis object
        
    Returns:
        Wisteria-compatible dictionary
    """
    return hypothesis.to_wisteria_format()


def convert_unified_to_protognosis(hypothesis: UnifiedHypothesis) -> Dict[str, Any]:
    """
    Convert UnifiedHypothesis to ProtoGnosis format.
    
    Args:
        hypothesis: UnifiedHypothesis object
        
    Returns:
        ProtoGnosis-compatible dictionary
    """
    return hypothesis.to_protognosis_format()


def batch_convert_wisteria(wisteria_hypotheses: List[Dict[str, Any]]) -> List[UnifiedHypothesis]:
    """
    Convert multiple Wisteria hypotheses to unified format.
    
    Args:
        wisteria_hypotheses: List of Wisteria hypothesis data
        
    Returns:
        List of UnifiedHypothesis objects
    """
    unified_hypotheses = []
    
    for wisteria_data in wisteria_hypotheses:
        try:
            unified = convert_wisteria_to_unified(wisteria_data)
            unified_hypotheses.append(unified)
        except Exception as e:
            print(f"Warning: Failed to convert Wisteria hypothesis: {e}")
            continue
    
    return unified_hypotheses


def batch_convert_protognosis(protognosis_hypotheses: List[Dict[str, Any]]) -> List[UnifiedHypothesis]:
    """
    Convert multiple ProtoGnosis hypotheses to unified format.
    
    Args:
        protognosis_hypotheses: List of ProtoGnosis hypothesis data
        
    Returns:
        List of UnifiedHypothesis objects
    """
    unified_hypotheses = []
    
    for protognosis_data in protognosis_hypotheses:
        try:
            unified = convert_protognosis_to_unified(protognosis_data)
            unified_hypotheses.append(unified)
        except Exception as e:
            print(f"Warning: Failed to convert ProtoGnosis hypothesis: {e}")
            continue
    
    return unified_hypotheses

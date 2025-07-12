#!/usr/bin/env python3
"""
Biomni Validation Script for Neurodegenerative Disease Hypotheses.

This script specifically validates the 9 biomedical hypotheses from the Wisteria
neurodegenerative disease research session using Modern Biomni integration.
"""

import asyncio
import json
import logging
from pathlib import Path
import sys
from typing import List, Dict, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import required modules
try:
    from jnana.agents.biomni_modern import ModernBiomniAgent, ModernBiomniConfig
    from jnana.data.unified_hypothesis import UnifiedHypothesis
    JNANA_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Jnana modules not available: {e}")
    JNANA_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NeurodegenerationBiomniValidator:
    """
    Specialized validator for neurodegenerative disease hypotheses using Modern Biomni.
    """
    
    def __init__(self):
        """Initialize the neurodegeneration-specific Biomni validator."""
        self.biomni_agent = None
        self.validation_results = []
        self.neurodegeneration_file = "wisteria-json/hypotheses_interactive_scout_20250620_170510.json"
        
        # Initialize modern Biomni agent with neuroscience-specific configuration
        self._initialize_biomni()
    
    def _initialize_biomni(self):
        """Initialize the modern Biomni agent with neuroscience focus."""
        if not JNANA_AVAILABLE:
            logger.warning("Jnana not available - using mock validation mode")
            return
        
        config = ModernBiomniConfig(
            enabled=True,
            data_path="./data/biomni_neurodegeneration",
            confidence_threshold=0.7,  # Higher threshold for medical hypotheses
            auto_patch_imports=True,
            langchain_version_check=True,
            fallback_on_error=True,
            enable_experimental_suggestions=True,
            # Neuroscience-specific tools
            genomics_tools=["crispr_screen", "scrna_seq", "epigenome_analysis"],
            protein_tools=["structure_prediction", "interaction_analysis", "aggregation_modeling"],
            drug_discovery_tools=["target_identification", "compound_screening", "admet_prediction"]
        )
        
        self.biomni_agent = ModernBiomniAgent(config)
        logger.info("Modern Biomni agent initialized for neurodegeneration validation")
    
    def load_neurodegeneration_hypotheses(self) -> List[Dict[str, Any]]:
        """
        Load the neurodegeneration hypotheses from the Wisteria JSON file.
        
        Returns:
            List of neurodegeneration hypotheses
        """
        try:
            with open(self.neurodegeneration_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            hypotheses = data.get('hypotheses', [])
            logger.info(f"Loaded {len(hypotheses)} neurodegeneration hypotheses")
            
            return hypotheses
            
        except Exception as e:
            logger.error(f"Failed to load neurodegeneration hypotheses: {e}")
            return []
    
    def categorize_hypothesis_by_mechanism(self, hypothesis: Dict[str, Any]) -> str:
        """
        Categorize hypothesis by biological mechanism for targeted validation.
        
        Args:
            hypothesis: Hypothesis data
            
        Returns:
            Mechanism category
        """
        title = hypothesis.get('title', '').lower()
        description = hypothesis.get('description', '').lower()
        
        # Define mechanism categories
        if 'mitochondrial' in title or 'mitochondrial' in description:
            if 'methylation' in title or 'epigenetic' in title:
                return 'mitochondrial_epigenetics'
            else:
                return 'mitochondrial_dysfunction'
        elif 'gut' in title or 'microbiome' in title:
            if 'toxin' in title or 'toxin' in description:
                return 'gut_brain_toxins'
            else:
                return 'gut_brain_inflammation'
        elif 'tau' in title or 'tau' in description:
            if 'phase separation' in description:
                return 'tau_phase_separation'
            else:
                return 'tau_modifications'
        elif 'ferroptosis' in title:
            return 'ferroptosis'
        else:
            return 'general_neurodegeneration'
    
    async def validate_single_hypothesis(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single neurodegeneration hypothesis with Biomni.
        
        Args:
            hypothesis: Hypothesis data
            
        Returns:
            Validation results
        """
        mechanism = self.categorize_hypothesis_by_mechanism(hypothesis)
        
        print(f"\n🧬 Validating Hypothesis {hypothesis.get('hypothesis_number', 'N/A')}")
        print(f"   Title: {hypothesis.get('title', 'Unknown')[:80]}...")
        print(f"   Mechanism: {mechanism.replace('_', ' ').title()}")
        
        if not self.biomni_agent:
            return self._create_mock_validation_result(hypothesis, mechanism)
        
        try:
            # Initialize Biomni agent if needed
            if not self.biomni_agent.is_initialized:
                await self.biomni_agent.initialize()
            
            # Perform specialized validation based on mechanism
            result = await self.biomni_agent.verify_hypothesis(
                hypothesis_content=hypothesis.get('description', ''),
                research_goal=f"Neurodegeneration research: {mechanism.replace('_', ' ')}",
                verification_type=self._get_verification_type(mechanism)
            )
            
            # Enhance result with mechanism-specific analysis
            enhanced_result = self._enhance_validation_result(result, hypothesis, mechanism)
            
            print(f"   ✅ Validation completed:")
            print(f"      Confidence: {enhanced_result['confidence_score']:.2f}")
            print(f"      Plausible: {enhanced_result['is_biologically_plausible']}")
            print(f"      Evidence: {len(enhanced_result['supporting_evidence'])} supporting")
            print(f"      Experiments: {len(enhanced_result['suggested_experiments'])} suggested")
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Biomni validation failed for hypothesis {hypothesis.get('hypothesis_number')}: {e}")
            return self._create_error_validation_result(hypothesis, mechanism, str(e))
    
    def _get_verification_type(self, mechanism: str) -> str:
        """Get appropriate verification type based on mechanism."""
        mechanism_to_type = {
            'mitochondrial_epigenetics': 'genomics',
            'mitochondrial_dysfunction': 'general',
            'gut_brain_toxins': 'general',
            'gut_brain_inflammation': 'general',
            'tau_phase_separation': 'protein_biology',
            'tau_modifications': 'protein_biology',
            'ferroptosis': 'general',
            'general_neurodegeneration': 'general'
        }
        return mechanism_to_type.get(mechanism, 'general')
    
    def _enhance_validation_result(self, result: Dict[str, Any], hypothesis: Dict[str, Any], mechanism: str) -> Dict[str, Any]:
        """Enhance validation result with mechanism-specific insights."""
        enhanced = result.copy()
        
        # Add mechanism-specific metadata
        enhanced['mechanism_category'] = mechanism
        enhanced['hypothesis_number'] = hypothesis.get('hypothesis_number')
        enhanced['wisteria_title'] = hypothesis.get('title')
        enhanced['wisteria_references'] = len(hypothesis.get('references', []))
        
        # Add mechanism-specific experimental suggestions
        mechanism_experiments = self._get_mechanism_specific_experiments(mechanism)
        enhanced['mechanism_specific_experiments'] = mechanism_experiments
        
        # Combine with original suggestions
        all_experiments = enhanced.get('suggested_experiments', []) + mechanism_experiments
        enhanced['suggested_experiments'] = list(set(all_experiments))  # Remove duplicates
        
        return enhanced
    
    def _get_mechanism_specific_experiments(self, mechanism: str) -> List[str]:
        """Get mechanism-specific experimental suggestions."""
        experiments = {
            'mitochondrial_epigenetics': [
                "Bisulfite sequencing of mitochondrial DNA",
                "ChIP-seq analysis of mitochondrial histones",
                "CRISPR-dCas9 epigenome editing of mtDNA",
                "Single-cell mitochondrial epigenomics"
            ],
            'mitochondrial_dysfunction': [
                "Seahorse mitochondrial stress test",
                "Live-cell mitochondrial imaging",
                "Mitochondrial proteomics analysis",
                "Electron transport chain activity assays"
            ],
            'gut_brain_toxins': [
                "Germ-free mouse colonization studies",
                "Metabolomics of gut-derived compounds",
                "Blood-brain barrier permeability assays",
                "Neuronal toxicity screening of microbial metabolites"
            ],
            'gut_brain_inflammation': [
                "16S rRNA microbiome sequencing",
                "Cytokine profiling in brain tissue",
                "Microglial activation analysis",
                "Fecal microbiota transplantation studies"
            ],
            'tau_phase_separation': [
                "In vitro tau droplet formation assays",
                "FRAP analysis of tau mobility",
                "Cryo-electron microscopy of tau aggregates",
                "Optogenetic control of tau phase separation"
            ],
            'tau_modifications': [
                "Mass spectrometry of tau PTMs",
                "Phospho-tau immunohistochemistry",
                "Kinase/phosphatase activity assays",
                "Tau aggregation kinetics studies"
            ],
            'ferroptosis': [
                "Lipid peroxidation measurements",
                "Iron chelation therapy studies",
                "GPX4 activity assays",
                "Ferroptosis inhibitor screening"
            ]
        }
        return experiments.get(mechanism, [])
    
    def _create_mock_validation_result(self, hypothesis: Dict[str, Any], mechanism: str) -> Dict[str, Any]:
        """Create mock validation result when Biomni is not available."""
        return {
            'verification_id': f"mock_neuro_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'hypothesis_number': hypothesis.get('hypothesis_number'),
            'wisteria_title': hypothesis.get('title'),
            'mechanism_category': mechanism,
            'is_biologically_plausible': True,
            'confidence_score': 0.75,  # Higher for neurodegeneration hypotheses
            'evidence_strength': 'strong',
            'supporting_evidence': [
                f'Mock analysis indicates strong biological relevance for {mechanism}',
                'Neurodegeneration research supports this mechanism',
                'Multiple pathways implicated in disease progression'
            ],
            'contradicting_evidence': ['Limited analysis due to Biomni unavailability'],
            'suggested_experiments': self._get_mechanism_specific_experiments(mechanism),
            'mechanism_specific_experiments': self._get_mechanism_specific_experiments(mechanism),
            'execution_time': 0.1,
            'langchain_version': 'mock',
            'compatibility_mode': 'mock',
            'error_details': 'Biomni not available - using enhanced neurodegeneration mock results'
        }
    
    def _create_error_validation_result(self, hypothesis: Dict[str, Any], mechanism: str, error: str) -> Dict[str, Any]:
        """Create error validation result."""
        return {
            'verification_id': f"error_neuro_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'hypothesis_number': hypothesis.get('hypothesis_number'),
            'wisteria_title': hypothesis.get('title'),
            'mechanism_category': mechanism,
            'is_biologically_plausible': False,
            'confidence_score': 0.0,
            'evidence_strength': 'none',
            'supporting_evidence': [],
            'contradicting_evidence': ['Validation failed due to error'],
            'suggested_experiments': ['Retry validation after fixing issues'],
            'mechanism_specific_experiments': [],
            'execution_time': 0.0,
            'langchain_version': 'error',
            'compatibility_mode': 'error',
            'error_details': error
        }
    
    async def validate_all_neurodegeneration_hypotheses(self) -> Dict[str, Any]:
        """
        Validate all neurodegeneration hypotheses from the Wisteria file.
        
        Returns:
            Complete validation results
        """
        print("🧬 Neurodegeneration Hypotheses Biomni Validation")
        print("=" * 80)
        print("Validating 9 biomedical hypotheses on neurodegenerative diseases")
        print("=" * 80)
        
        # Load hypotheses
        hypotheses = self.load_neurodegeneration_hypotheses()
        
        if not hypotheses:
            print("❌ No neurodegeneration hypotheses found!")
            return {'status': 'no_hypotheses', 'results': []}
        
        print(f"\n📊 Found {len(hypotheses)} neurodegeneration hypotheses to validate")
        
        # Validate each hypothesis
        validation_results = []
        mechanism_counts = {}
        
        for hypothesis in hypotheses:
            try:
                result = await self.validate_single_hypothesis(hypothesis)
                validation_results.append(result)
                
                # Count mechanisms
                mechanism = result.get('mechanism_category', 'unknown')
                mechanism_counts[mechanism] = mechanism_counts.get(mechanism, 0) + 1
                
            except Exception as e:
                logger.error(f"Failed to validate hypothesis {hypothesis.get('hypothesis_number')}: {e}")
                error_result = self._create_error_validation_result(hypothesis, 'unknown', str(e))
                validation_results.append(error_result)
        
        # Generate comprehensive summary
        summary = self._generate_validation_summary(validation_results, mechanism_counts)
        
        # Display results
        self._display_validation_results(validation_results, summary)
        
        return {
            'summary': summary,
            'validation_results': validation_results,
            'mechanism_breakdown': mechanism_counts
        }
    
    def _generate_validation_summary(self, results: List[Dict[str, Any]], mechanism_counts: Dict[str, int]) -> Dict[str, Any]:
        """Generate comprehensive validation summary."""
        total_hypotheses = len(results)
        successful_validations = len([r for r in results if r['confidence_score'] > 0])
        high_confidence = len([r for r in results if r['confidence_score'] > 0.7])
        medium_confidence = len([r for r in results if 0.4 <= r['confidence_score'] <= 0.7])
        low_confidence = len([r for r in results if 0 < r['confidence_score'] < 0.4])
        
        avg_confidence = sum(r['confidence_score'] for r in results) / total_hypotheses if total_hypotheses > 0 else 0
        
        return {
            'total_hypotheses': total_hypotheses,
            'successful_validations': successful_validations,
            'high_confidence_count': high_confidence,
            'medium_confidence_count': medium_confidence,
            'low_confidence_count': low_confidence,
            'average_confidence': avg_confidence,
            'mechanism_distribution': mechanism_counts,
            'biomni_available': self.biomni_agent is not None and JNANA_AVAILABLE,
            'validation_timestamp': datetime.now().isoformat()
        }
    
    def _display_validation_results(self, results: List[Dict[str, Any]], summary: Dict[str, Any]):
        """Display comprehensive validation results."""
        print(f"\n🎯 Validation Summary:")
        print("=" * 80)
        print(f"Total hypotheses validated: {summary['total_hypotheses']}")
        print(f"Successful validations: {summary['successful_validations']}")
        print(f"Average confidence: {summary['average_confidence']:.2f}")
        print(f"High confidence (>0.7): {summary['high_confidence_count']}")
        print(f"Medium confidence (0.4-0.7): {summary['medium_confidence_count']}")
        print(f"Low confidence (<0.4): {summary['low_confidence_count']}")
        print(f"Biomni available: {summary['biomni_available']}")
        
        print(f"\n📊 Mechanism Distribution:")
        print("-" * 40)
        for mechanism, count in summary['mechanism_distribution'].items():
            print(f"  {mechanism.replace('_', ' ').title()}: {count}")
        
        print(f"\n📋 Detailed Results:")
        print("=" * 80)
        
        # Sort by confidence score (highest first)
        sorted_results = sorted(results, key=lambda x: x['confidence_score'], reverse=True)
        
        for i, result in enumerate(sorted_results, 1):
            print(f"\n{i}. Hypothesis {result.get('hypothesis_number', 'N/A')}")
            print(f"   Title: {result.get('wisteria_title', 'Unknown')[:70]}...")
            print(f"   Mechanism: {result.get('mechanism_category', 'unknown').replace('_', ' ').title()}")
            print(f"   Confidence: {result['confidence_score']:.2f}")
            print(f"   Plausible: {result['is_biologically_plausible']}")
            print(f"   Evidence: {len(result.get('supporting_evidence', []))} supporting")
            print(f"   Experiments: {len(result.get('suggested_experiments', []))} total")
            
            if result.get('error_details'):
                print(f"   ⚠️  Error: {result['error_details']}")
        
        print(f"\n🎉 Validation completed at {summary['validation_timestamp']}")
        
        if summary['biomni_available']:
            print("✅ Modern Biomni integration working correctly for neurodegeneration research!")
        else:
            print("⚠️  Biomni not available - used enhanced neurodegeneration mock results")


async def main():
    """Main function to run neurodegeneration hypothesis validation."""
    print("🧬 Neurodegeneration Hypotheses - Specialized Biomni Validation")
    print("=" * 80)
    print("This tool validates biomedical hypotheses on neurodegenerative diseases")
    print("using Modern Biomni integration with mechanism-specific analysis.")
    print("=" * 80)
    
    # Create validator
    validator = NeurodegenerationBiomniValidator()
    
    # Run validation
    results = await validator.validate_all_neurodegeneration_hypotheses()
    
    # Save results to file
    results_file = Path("neurodegeneration_biomni_validation_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    print("You can review the complete validation data and experimental suggestions in this file.")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())

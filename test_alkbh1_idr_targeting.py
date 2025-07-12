#!/usr/bin/env python3
"""
Biomni Test for ALKBH1 IDR Targeting Research.

This script tests Biomni validation for the specific research problem:
"Find ways to target the intrinsically disordered regions in the protein ALKBH1 
which are biologics based (based on affitin, nanobody and affibody templates)"
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


class ALKBH1IDRTargetingValidator:
    """
    Specialized validator for ALKBH1 IDR targeting research using biologics.
    """
    
    def __init__(self):
        """Initialize the ALKBH1 IDR targeting validator."""
        self.biomni_agent = None
        self.research_problem = (
            "Find ways to target the intrinsically disordered regions in the protein ALKBH1 "
            "which are biologics based (based on affitin, nanobody and affibody templates)"
        )
        
        # Define research hypotheses for ALKBH1 IDR targeting
        self.research_hypotheses = self._generate_alkbh1_hypotheses()
        
        # Initialize modern Biomni agent with protein biology focus
        self._initialize_biomni()
    
    def _initialize_biomni(self):
        """Initialize the modern Biomni agent with protein biology focus."""
        if not JNANA_AVAILABLE:
            logger.warning("Jnana not available - using enhanced mock validation mode")
            return
        
        config = ModernBiomniConfig(
            enabled=True,
            data_path="./data/biomni_alkbh1_idr",
            confidence_threshold=0.7,  # High threshold for protein targeting
            auto_patch_imports=True,
            langchain_version_check=True,
            fallback_on_error=True,
            enable_experimental_suggestions=True,
            # Protein biology specific tools
            protein_tools=["structure_prediction", "idr_analysis", "binding_prediction", "affinity_modeling"],
            genomics_tools=["protein_expression", "mutagenesis_design"],
            drug_discovery_tools=["biologics_design", "binding_affinity", "selectivity_analysis"]
        )
        
        self.biomni_agent = ModernBiomniAgent(config)
        logger.info("Modern Biomni agent initialized for ALKBH1 IDR targeting research")
    
    def _generate_alkbh1_hypotheses(self) -> List[Dict[str, Any]]:
        """
        Generate research hypotheses for ALKBH1 IDR targeting.
        
        Returns:
            List of research hypotheses
        """
        hypotheses = [
            {
                "hypothesis_id": "alkbh1_idr_h1",
                "title": "Affitin-Based Targeting of ALKBH1 IDRs",
                "description": (
                    "Engineered affitins can be designed to specifically bind to intrinsically "
                    "disordered regions of ALKBH1 by targeting transient secondary structures "
                    "and conserved sequence motifs within the IDRs, providing selective inhibition "
                    "of ALKBH1's demethylase activity through allosteric modulation."
                ),
                "biologics_type": "affitin",
                "target_region": "intrinsically_disordered_regions",
                "mechanism": "allosteric_inhibition",
                "confidence": 0.8
            },
            {
                "hypothesis_id": "alkbh1_idr_h2", 
                "title": "Nanobody Recognition of ALKBH1 IDR Conformational States",
                "description": (
                    "Single-domain nanobodies can be selected to recognize specific conformational "
                    "states of ALKBH1's intrinsically disordered regions, particularly targeting "
                    "the N-terminal IDR that regulates substrate accessibility and the C-terminal "
                    "IDR involved in protein-protein interactions, thereby disrupting ALKBH1's "
                    "cellular localization and enzymatic function."
                ),
                "biologics_type": "nanobody",
                "target_region": "n_terminal_c_terminal_idrs",
                "mechanism": "conformational_stabilization",
                "confidence": 0.85
            },
            {
                "hypothesis_id": "alkbh1_idr_h3",
                "title": "Affibody-Mediated Disruption of ALKBH1 IDR Interactions",
                "description": (
                    "Affibody scaffolds can be engineered to mimic natural binding partners of "
                    "ALKBH1's IDRs, competing for binding sites and disrupting critical protein-protein "
                    "interactions mediated by the disordered regions. This approach could prevent "
                    "ALKBH1's recruitment to chromatin and its interaction with DNA repair complexes."
                ),
                "biologics_type": "affibody",
                "target_region": "protein_interaction_motifs",
                "mechanism": "competitive_inhibition",
                "confidence": 0.75
            },
            {
                "hypothesis_id": "alkbh1_idr_h4",
                "title": "Multi-Domain Biologics for ALKBH1 IDR Targeting",
                "description": (
                    "Chimeric biologics combining elements from affitin, nanobody, and affibody "
                    "scaffolds can provide multivalent targeting of different IDR regions in ALKBH1, "
                    "achieving higher specificity and affinity through avidity effects while "
                    "simultaneously disrupting multiple functional aspects of the IDRs."
                ),
                "biologics_type": "chimeric_multi_domain",
                "target_region": "multiple_idr_sites",
                "mechanism": "multivalent_inhibition",
                "confidence": 0.7
            },
            {
                "hypothesis_id": "alkbh1_idr_h5",
                "title": "IDR-Specific Biologics for ALKBH1 Subcellular Localization Control",
                "description": (
                    "Biologics targeting ALKBH1's IDRs can be designed to specifically disrupt "
                    "nuclear localization signals and chromatin-binding motifs within the "
                    "disordered regions, effectively sequestering ALKBH1 in the cytoplasm and "
                    "preventing its access to nuclear DNA substrates, thereby inhibiting its "
                    "demethylase activity in a spatially controlled manner."
                ),
                "biologics_type": "localization_disruptor",
                "target_region": "nuclear_localization_motifs",
                "mechanism": "subcellular_sequestration",
                "confidence": 0.8
            }
        ]
        
        return hypotheses
    
    def get_alkbh1_background_info(self) -> Dict[str, Any]:
        """
        Get background information about ALKBH1 and IDR targeting.
        
        Returns:
            Background information dictionary
        """
        return {
            "protein_info": {
                "name": "ALKBH1",
                "full_name": "AlkB Homolog 1, DNA Repair Protein",
                "function": "DNA/RNA demethylase, removes methyl groups from damaged nucleotides",
                "domains": ["AlkB domain (catalytic)", "N-terminal IDR", "C-terminal IDR"],
                "cellular_role": "DNA repair, RNA modification, chromatin regulation"
            },
            "idr_characteristics": {
                "definition": "Intrinsically Disordered Regions - protein segments lacking stable secondary structure",
                "alkbh1_idrs": ["N-terminal IDR (residues 1-130)", "C-terminal IDR (residues 230-389)"],
                "functions": ["Protein-protein interactions", "Subcellular localization", "Regulatory control"],
                "targeting_challenges": ["Lack of stable structure", "Dynamic conformations", "Large surface area"]
            },
            "biologics_templates": {
                "affitin": {
                    "description": "Small protein scaffolds based on Sac7d from Sulfolobus acidocaldarius",
                    "advantages": ["High stability", "Small size (~7 kDa)", "Easy to engineer"],
                    "applications": ["Protein-protein interaction inhibitors", "Diagnostic tools"]
                },
                "nanobody": {
                    "description": "Single-domain antibodies derived from camelid heavy-chain antibodies",
                    "advantages": ["High specificity", "Tissue penetration", "Conformational flexibility"],
                    "applications": ["Therapeutic antibodies", "Research tools", "Imaging agents"]
                },
                "affibody": {
                    "description": "Small protein scaffolds based on protein A domain",
                    "advantages": ["High affinity", "Rapid folding", "Chemical stability"],
                    "applications": ["Molecular imaging", "Targeted therapy", "Biosensors"]
                }
            },
            "research_significance": {
                "cancer_relevance": "ALKBH1 overexpression in various cancers",
                "therapeutic_potential": "Novel approach to target 'undruggable' proteins",
                "technical_innovation": "IDR targeting represents frontier in protein therapeutics"
            }
        }
    
    async def validate_single_hypothesis(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single ALKBH1 IDR targeting hypothesis with Biomni.
        
        Args:
            hypothesis: Hypothesis data
            
        Returns:
            Validation results
        """
        print(f"\n🧬 Validating Hypothesis: {hypothesis['hypothesis_id']}")
        print(f"   Title: {hypothesis['title']}")
        print(f"   Biologics Type: {hypothesis['biologics_type']}")
        print(f"   Target Region: {hypothesis['target_region']}")
        print(f"   Mechanism: {hypothesis['mechanism']}")
        
        if not self.biomni_agent:
            return self._create_enhanced_mock_validation(hypothesis)
        
        try:
            # Initialize Biomni agent if needed
            if not self.biomni_agent.is_initialized:
                await self.biomni_agent.initialize()
            
            # Perform specialized validation for protein biology
            result = await self.biomni_agent.verify_hypothesis(
                hypothesis_content=hypothesis['description'],
                research_goal=f"ALKBH1 IDR targeting using {hypothesis['biologics_type']} biologics",
                verification_type="protein_biology"
            )
            
            # Enhance result with ALKBH1-specific analysis
            enhanced_result = self._enhance_alkbh1_validation(result, hypothesis)
            
            print(f"   ✅ Validation completed:")
            print(f"      Confidence: {enhanced_result['confidence_score']:.2f}")
            print(f"      Plausible: {enhanced_result['is_biologically_plausible']}")
            print(f"      Feasibility: {enhanced_result['technical_feasibility']}")
            print(f"      Evidence: {len(enhanced_result['supporting_evidence'])} supporting")
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Biomni validation failed for {hypothesis['hypothesis_id']}: {e}")
            return self._create_error_validation_result(hypothesis, str(e))
    
    def _enhance_alkbh1_validation(self, result: Dict[str, Any], hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance validation result with ALKBH1-specific insights."""
        # Convert result to dict if it's not already
        if hasattr(result, '__dict__'):
            enhanced = result.__dict__.copy()
        else:
            enhanced = dict(result) if result else {}
        
        # Add ALKBH1-specific metadata
        enhanced['hypothesis_id'] = hypothesis['hypothesis_id']
        enhanced['biologics_type'] = hypothesis['biologics_type']
        enhanced['target_region'] = hypothesis['target_region']
        enhanced['mechanism'] = hypothesis['mechanism']
        enhanced['original_confidence'] = hypothesis['confidence']
        
        # Add technical feasibility assessment
        enhanced['technical_feasibility'] = self._assess_technical_feasibility(hypothesis)
        
        # Add ALKBH1-specific experimental suggestions
        alkbh1_experiments = self._get_alkbh1_specific_experiments(hypothesis)
        enhanced['alkbh1_specific_experiments'] = alkbh1_experiments
        
        # Combine with original suggestions
        all_experiments = enhanced.get('suggested_experiments', []) + alkbh1_experiments
        enhanced['suggested_experiments'] = list(set(all_experiments))
        
        # Add biologics development pathway
        enhanced['development_pathway'] = self._get_biologics_development_pathway(hypothesis['biologics_type'])
        
        return enhanced
    
    def _assess_technical_feasibility(self, hypothesis: Dict[str, Any]) -> str:
        """Assess technical feasibility of the biologics approach."""
        biologics_type = hypothesis['biologics_type']
        
        feasibility_map = {
            'affitin': 'high',  # Well-established scaffold
            'nanobody': 'high',  # Proven for IDR targeting
            'affibody': 'medium',  # Good scaffold, IDR targeting less proven
            'chimeric_multi_domain': 'medium',  # Complex but feasible
            'localization_disruptor': 'high'  # Established approach
        }
        
        return feasibility_map.get(biologics_type, 'medium')
    
    def _get_alkbh1_specific_experiments(self, hypothesis: Dict[str, Any]) -> List[str]:
        """Get ALKBH1-specific experimental suggestions."""
        biologics_type = hypothesis['biologics_type']
        
        base_experiments = [
            "ALKBH1 protein expression and purification",
            "IDR characterization using NMR or CD spectroscopy",
            "Binding affinity measurements (SPR, ITC)",
            "Enzymatic activity assays (demethylase activity)",
            "Cell-based functional assays"
        ]
        
        specific_experiments = {
            'affitin': [
                "Affitin library screening against ALKBH1 IDRs",
                "Affitin engineering for improved IDR binding",
                "Thermal stability analysis of affitin-ALKBH1 complexes",
                "Competition assays with natural ALKBH1 partners"
            ],
            'nanobody': [
                "Camelid immunization with ALKBH1 IDR peptides",
                "Phage display selection of IDR-specific nanobodies",
                "Nanobody humanization for therapeutic development",
                "Cryo-EM structure determination of nanobody-ALKBH1 complexes"
            ],
            'affibody': [
                "Affibody library construction and selection",
                "Affibody maturation through directed evolution",
                "Biophysical characterization of affibody-IDR interactions",
                "In vivo stability and pharmacokinetics studies"
            ],
            'chimeric_multi_domain': [
                "Multi-domain construct design and optimization",
                "Avidity measurements for multivalent binding",
                "Structural analysis of multi-domain biologics",
                "Cooperative binding studies"
            ],
            'localization_disruptor': [
                "Nuclear/cytoplasmic fractionation assays",
                "Fluorescence microscopy localization studies",
                "Chromatin immunoprecipitation (ChIP) assays",
                "Live-cell imaging of ALKBH1 dynamics"
            ]
        }
        
        return base_experiments + specific_experiments.get(biologics_type, [])
    
    def _get_biologics_development_pathway(self, biologics_type: str) -> List[str]:
        """Get development pathway for the biologics type."""
        pathways = {
            'affitin': [
                "1. Library construction and screening",
                "2. Lead optimization and affinity maturation",
                "3. Stability and solubility optimization",
                "4. In vitro efficacy validation",
                "5. Cell-based functional studies",
                "6. In vivo proof-of-concept studies"
            ],
            'nanobody': [
                "1. Immunization and library generation",
                "2. Phage display selection",
                "3. Nanobody characterization and ranking",
                "4. Humanization and optimization",
                "5. Preclinical efficacy studies",
                "6. IND-enabling studies"
            ],
            'affibody': [
                "1. Library design and construction",
                "2. Selection and screening",
                "3. Affinity maturation",
                "4. Biophysical characterization",
                "5. Functional validation",
                "6. Lead optimization"
            ]
        }
        
        return pathways.get(biologics_type, [
            "1. Target validation",
            "2. Biologics design and engineering",
            "3. In vitro characterization",
            "4. Cell-based validation",
            "5. In vivo studies",
            "6. Clinical development"
        ])
    
    def _create_enhanced_mock_validation(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """Create enhanced mock validation result for ALKBH1 research."""
        return {
            'verification_id': f"alkbh1_mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'hypothesis_id': hypothesis['hypothesis_id'],
            'biologics_type': hypothesis['biologics_type'],
            'target_region': hypothesis['target_region'],
            'mechanism': hypothesis['mechanism'],
            'original_confidence': hypothesis['confidence'],
            'is_biologically_plausible': True,
            'confidence_score': hypothesis['confidence'],
            'technical_feasibility': self._assess_technical_feasibility(hypothesis),
            'evidence_strength': 'strong',
            'supporting_evidence': [
                f'{hypothesis["biologics_type"].title()} scaffolds have proven success in protein targeting',
                'IDR targeting is an emerging and promising therapeutic approach',
                'ALKBH1 is a validated target in cancer research',
                f'{hypothesis["mechanism"].replace("_", " ").title()} is a well-established mechanism',
                'Multiple successful examples of biologics targeting disordered regions exist'
            ],
            'contradicting_evidence': [
                'IDR targeting remains technically challenging due to conformational flexibility',
                'Limited structural information available for ALKBH1 IDRs'
            ],
            'suggested_experiments': self._get_alkbh1_specific_experiments(hypothesis),
            'alkbh1_specific_experiments': self._get_alkbh1_specific_experiments(hypothesis),
            'development_pathway': self._get_biologics_development_pathway(hypothesis['biologics_type']),
            'execution_time': 0.1,
            'langchain_version': 'mock',
            'compatibility_mode': 'enhanced_mock',
            'error_details': 'Biomni not available - using enhanced ALKBH1-specific mock results'
        }
    
    def _create_error_validation_result(self, hypothesis: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Create error validation result."""
        return {
            'verification_id': f"alkbh1_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'hypothesis_id': hypothesis['hypothesis_id'],
            'biologics_type': hypothesis['biologics_type'],
            'is_biologically_plausible': False,
            'confidence_score': 0.0,
            'technical_feasibility': 'unknown',
            'evidence_strength': 'none',
            'supporting_evidence': [],
            'contradicting_evidence': ['Validation failed due to error'],
            'suggested_experiments': ['Retry validation after fixing issues'],
            'development_pathway': [],
            'execution_time': 0.0,
            'langchain_version': 'error',
            'compatibility_mode': 'error',
            'error_details': error
        }
    
    async def run_complete_alkbh1_validation(self) -> Dict[str, Any]:
        """
        Run complete ALKBH1 IDR targeting validation.
        
        Returns:
            Complete validation results
        """
        print("🧬 ALKBH1 IDR Targeting - Biomni Validation Test")
        print("=" * 80)
        print("Research Problem:")
        print(f"'{self.research_problem}'")
        print("=" * 80)
        
        # Display background information
        background = self.get_alkbh1_background_info()
        print(f"\n📋 ALKBH1 Background:")
        print(f"   Protein: {background['protein_info']['full_name']}")
        print(f"   Function: {background['protein_info']['function']}")
        print(f"   IDRs: {', '.join(background['idr_characteristics']['alkbh1_idrs'])}")
        print(f"   Biologics Templates: {len(background['biologics_templates'])} types")
        
        print(f"\n🧪 Testing {len(self.research_hypotheses)} Research Hypotheses:")
        for i, hyp in enumerate(self.research_hypotheses, 1):
            print(f"   {i}. {hyp['title']} ({hyp['biologics_type']})")
        
        # Validate each hypothesis
        validation_results = []
        biologics_performance = {}
        
        for hypothesis in self.research_hypotheses:
            try:
                result = await self.validate_single_hypothesis(hypothesis)
                validation_results.append(result)
                
                # Track biologics type performance
                biologics_type = result.get('biologics_type', 'unknown')
                if biologics_type not in biologics_performance:
                    biologics_performance[biologics_type] = []
                biologics_performance[biologics_type].append(result['confidence_score'])
                
            except Exception as e:
                logger.error(f"Failed to validate {hypothesis['hypothesis_id']}: {e}")
                error_result = self._create_error_validation_result(hypothesis, str(e))
                validation_results.append(error_result)
        
        # Generate comprehensive summary
        summary = self._generate_alkbh1_summary(validation_results, biologics_performance, background)
        
        # Display results
        self._display_alkbh1_results(validation_results, summary, background)
        
        return {
            'research_problem': self.research_problem,
            'background_info': background,
            'summary': summary,
            'validation_results': validation_results,
            'biologics_performance': biologics_performance
        }
    
    def _generate_alkbh1_summary(self, results: List[Dict[str, Any]], biologics_performance: Dict[str, List[float]], background: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive ALKBH1 validation summary."""
        total_hypotheses = len(results)
        successful_validations = len([r for r in results if r['confidence_score'] > 0])
        avg_confidence = sum(r['confidence_score'] for r in results) / total_hypotheses if total_hypotheses > 0 else 0
        
        # Calculate biologics type rankings
        biologics_rankings = {}
        for biologics_type, scores in biologics_performance.items():
            biologics_rankings[biologics_type] = {
                'avg_confidence': sum(scores) / len(scores) if scores else 0,
                'count': len(scores)
            }
        
        # Sort by average confidence
        ranked_biologics = sorted(biologics_rankings.items(), key=lambda x: x[1]['avg_confidence'], reverse=True)
        
        return {
            'total_hypotheses': total_hypotheses,
            'successful_validations': successful_validations,
            'average_confidence': avg_confidence,
            'biologics_rankings': dict(biologics_rankings),
            'top_biologics_approach': ranked_biologics[0][0] if ranked_biologics else 'none',
            'biomni_available': self.biomni_agent is not None and JNANA_AVAILABLE,
            'validation_timestamp': datetime.now().isoformat(),
            'research_feasibility': 'high' if avg_confidence > 0.7 else 'medium' if avg_confidence > 0.5 else 'low'
        }
    
    def _display_alkbh1_results(self, results: List[Dict[str, Any]], summary: Dict[str, Any], background: Dict[str, Any]):
        """Display comprehensive ALKBH1 validation results."""
        print(f"\n🎯 ALKBH1 IDR Targeting Validation Summary:")
        print("=" * 80)
        print(f"Research Problem: Target ALKBH1 IDRs with biologics")
        print(f"Hypotheses validated: {summary['total_hypotheses']}")
        print(f"Successful validations: {summary['successful_validations']}")
        print(f"Average confidence: {summary['average_confidence']:.2f}")
        print(f"Research feasibility: {summary['research_feasibility']}")
        print(f"Top biologics approach: {summary['top_biologics_approach']}")
        print(f"Biomni available: {summary['biomni_available']}")
        
        print(f"\n📊 Biologics Type Performance:")
        print("-" * 50)
        for biologics_type, performance in summary['biologics_rankings'].items():
            print(f"  {biologics_type.replace('_', ' ').title()}: {performance['avg_confidence']:.2f} confidence")
        
        print(f"\n📋 Detailed Hypothesis Results:")
        print("=" * 80)
        
        # Sort by confidence score
        sorted_results = sorted(results, key=lambda x: x['confidence_score'], reverse=True)
        
        for i, result in enumerate(sorted_results, 1):
            print(f"\n{i}. {result.get('hypothesis_id', 'Unknown')}")
            print(f"   Biologics: {result.get('biologics_type', 'Unknown').replace('_', ' ').title()}")
            print(f"   Target: {result.get('target_region', 'Unknown').replace('_', ' ').title()}")
            print(f"   Mechanism: {result.get('mechanism', 'Unknown').replace('_', ' ').title()}")
            print(f"   Confidence: {result['confidence_score']:.2f}")
            print(f"   Feasibility: {result.get('technical_feasibility', 'Unknown')}")
            print(f"   Plausible: {result['is_biologically_plausible']}")
            print(f"   Evidence: {len(result.get('supporting_evidence', []))} supporting")
            print(f"   Experiments: {len(result.get('suggested_experiments', []))} suggested")
            
            if result.get('error_details'):
                print(f"   ⚠️  Note: {result['error_details']}")
        
        print(f"\n🔬 Research Recommendations:")
        print("=" * 40)
        
        top_result = sorted_results[0] if sorted_results else None
        if top_result:
            print(f"1. PRIORITY APPROACH: {top_result.get('biologics_type', 'Unknown').replace('_', ' ').title()}")
            print(f"   Confidence: {top_result['confidence_score']:.2f}")
            print(f"   Feasibility: {top_result.get('technical_feasibility', 'Unknown')}")
            
            print(f"\n2. IMMEDIATE NEXT STEPS:")
            experiments = top_result.get('alkbh1_specific_experiments', [])[:5]
            for j, exp in enumerate(experiments, 1):
                print(f"   {j}. {exp}")
            
            print(f"\n3. DEVELOPMENT PATHWAY:")
            pathway = top_result.get('development_pathway', [])[:4]
            for step in pathway:
                print(f"   • {step}")
        
        print(f"\n🎉 Validation completed at {summary['validation_timestamp']}")
        
        if summary['biomni_available']:
            print("✅ Modern Biomni integration working for ALKBH1 research!")
        else:
            print("⚠️  Biomni not available - used enhanced ALKBH1-specific mock results")


async def main():
    """Main function to run ALKBH1 IDR targeting validation."""
    print("🧬 ALKBH1 IDR Targeting - Specialized Biomni Validation")
    print("=" * 80)
    print("Testing Biomni validation for targeting intrinsically disordered")
    print("regions in ALKBH1 using biologics (affitin, nanobody, affibody).")
    print("=" * 80)
    
    # Create validator
    validator = ALKBH1IDRTargetingValidator()
    
    # Run validation
    results = await validator.run_complete_alkbh1_validation()
    
    # Save results to file
    results_file = Path("alkbh1_idr_targeting_biomni_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    print("You can review the complete validation data, experimental suggestions,")
    print("and biologics development pathways in this file.")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())

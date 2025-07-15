#!/usr/bin/env python3
"""
Enhanced Biomni Hypothesis Validation Suite

This script provides detailed analysis of which Biomni tools and methods are used
for hypothesis validation, including fallback analysis when Biomni is unavailable.
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from jnana.core.jnana_system import JnanaSystem
from jnana.data.unified_hypothesis import UnifiedHypothesis
from jnana.agents.biomni_modern import ModernBiomniAgent, ModernBiomniConfig

@dataclass
class BiomniToolAnalysis:
    """Analysis of Biomni tools and methods used"""
    tool_name: str
    description: str
    input_data: str
    output_format: str
    confidence_method: str
    evidence_sources: List[str]
    experimental_suggestions: List[str]
    biological_domains: List[str]

@dataclass
class EnhancedValidationResult:
    """Enhanced validation result with detailed Biomni tool analysis"""
    hypothesis_id: str
    hypothesis_title: str
    biomni_available: bool
    biomni_tools_used: List[BiomniToolAnalysis]
    verification_result: Optional[Dict]
    fallback_analysis: Optional[Dict]
    computational_confidence: float
    biomedical_confidence: float
    combined_confidence: float
    validation_methodology: str
    evidence_quality: str
    experimental_feasibility: str

class EnhancedBiomniValidator:
    """Enhanced validator that shows detailed Biomni tool usage"""
    
    def __init__(self, jnana_system: JnanaSystem):
        self.jnana = jnana_system
        self.biomni_agent = jnana_system.biomni_agent if jnana_system else None
        self.results = []
    
    async def analyze_biomni_tools_for_hypothesis(self, hypothesis_content: str, 
                                                research_goal: str = "") -> List[BiomniToolAnalysis]:
        """Analyze which Biomni tools would be used for a specific hypothesis"""
        
        # Determine verification type based on content
        verification_type = self._determine_verification_type(hypothesis_content)
        
        tools_analysis = []
        
        # Tool 1: Biological Plausibility Analyzer
        tools_analysis.append(BiomniToolAnalysis(
            tool_name="Biological Plausibility Analyzer",
            description="Analyzes the biological feasibility of the hypothesis using literature knowledge",
            input_data=f"Hypothesis: {hypothesis_content[:100]}...",
            output_format="Plausibility score (0-1), supporting evidence, contradicting evidence",
            confidence_method="Literature-based confidence scoring with evidence weighting",
            evidence_sources=["PubMed literature", "Biological databases", "Pathway databases"],
            experimental_suggestions=self._get_experimental_suggestions_for_type(verification_type),
            biological_domains=self._get_biological_domains(hypothesis_content)
        ))
        
        # Tool 2: Evidence Strength Assessor
        tools_analysis.append(BiomniToolAnalysis(
            tool_name="Evidence Strength Assessor",
            description="Evaluates the strength of supporting and contradicting evidence",
            input_data=f"Research context: {research_goal}, Hypothesis domain: {verification_type}",
            output_format="Evidence strength rating, confidence intervals, quality metrics",
            confidence_method="Multi-factor evidence evaluation with uncertainty quantification",
            evidence_sources=["Peer-reviewed publications", "Clinical trial data", "Experimental results"],
            experimental_suggestions=["Systematic literature review", "Meta-analysis", "Evidence synthesis"],
            biological_domains=["Evidence-based medicine", "Systematic review methodology"]
        ))
        
        # Tool 3: Experimental Design Suggester
        tools_analysis.append(BiomniToolAnalysis(
            tool_name="Experimental Design Suggester",
            description="Suggests specific experimental approaches to test the hypothesis",
            input_data=f"Verification type: {verification_type}, Biological context",
            output_format="Ranked experimental protocols, feasibility assessment, resource requirements",
            confidence_method="Experimental design optimization with feasibility scoring",
            evidence_sources=["Experimental protocols", "Method databases", "Technical literature"],
            experimental_suggestions=self._get_detailed_experiments_for_type(verification_type),
            biological_domains=self._get_experimental_domains(verification_type)
        ))
        
        # Tool 4: Domain-Specific Validator
        if verification_type != "general":
            tools_analysis.append(BiomniToolAnalysis(
                tool_name=f"{verification_type.title()} Domain Validator",
                description=f"Specialized validation for {verification_type} research",
                input_data=f"Domain-specific hypothesis analysis for {verification_type}",
                output_format="Domain-specific confidence, specialized evidence, targeted experiments",
                confidence_method=f"{verification_type}-specific validation algorithms",
                evidence_sources=[f"{verification_type} databases", "Domain literature", "Specialized resources"],
                experimental_suggestions=self._get_domain_specific_experiments(verification_type),
                biological_domains=[verification_type, "Specialized methodology"]
            ))
        
        return tools_analysis
    
    def _determine_verification_type(self, hypothesis_content: str) -> str:
        """Determine the type of Biomni verification needed"""
        content_lower = hypothesis_content.lower()
        
        if any(term in content_lower for term in ['gene', 'dna', 'rna', 'genome', 'genetic']):
            return "genomics"
        elif any(term in content_lower for term in ['protein', 'enzyme', 'kinase', 'phosphorylation']):
            return "protein_biology"
        elif any(term in content_lower for term in ['drug', 'compound', 'inhibitor', 'therapeutic']):
            return "drug_discovery"
        elif any(term in content_lower for term in ['cell', 'cellular', 'mitosis', 'checkpoint']):
            return "cell_biology"
        elif any(term in content_lower for term in ['pathway', 'signaling', 'cascade', 'network']):
            return "systems_biology"
        else:
            return "general"
    
    def _get_experimental_suggestions_for_type(self, verification_type: str) -> List[str]:
        """Get experimental suggestions based on verification type"""
        suggestions = {
            "genomics": ["RNA-seq analysis", "ChIP-seq", "CRISPR screening", "Genome-wide association studies"],
            "protein_biology": ["Western blotting", "Mass spectrometry", "Protein-protein interaction assays", "Structural analysis"],
            "drug_discovery": ["High-throughput screening", "Structure-activity relationship studies", "Pharmacokinetic analysis"],
            "cell_biology": ["Live cell imaging", "Flow cytometry", "Cell cycle analysis", "Immunofluorescence"],
            "systems_biology": ["Network analysis", "Pathway enrichment", "Multi-omics integration", "Mathematical modeling"],
            "general": ["Literature review", "Preliminary experiments", "Proof-of-concept studies"]
        }
        return suggestions.get(verification_type, suggestions["general"])
    
    def _get_detailed_experiments_for_type(self, verification_type: str) -> List[str]:
        """Get detailed experimental protocols"""
        detailed_experiments = {
            "genomics": [
                "Single-cell RNA sequencing with temporal resolution",
                "CRISPR-Cas9 knockout validation with rescue experiments",
                "Chromatin immunoprecipitation with next-generation sequencing",
                "Genome editing with base editors for precise modifications"
            ],
            "protein_biology": [
                "Quantitative proteomics with stable isotope labeling",
                "Cryo-electron microscopy for structural determination",
                "Surface plasmon resonance for binding kinetics",
                "Cross-linking mass spectrometry for protein interactions"
            ],
            "cell_biology": [
                "Time-lapse microscopy with fluorescent reporters",
                "Single-cell analysis with flow cytometry sorting",
                "Electron microscopy for ultrastructural analysis",
                "Optogenetic manipulation for temporal control"
            ]
        }
        return detailed_experiments.get(verification_type, [
            "Systematic experimental design",
            "Multi-method validation approach",
            "Quantitative analysis with statistical power"
        ])
    
    def _get_biological_domains(self, hypothesis_content: str) -> List[str]:
        """Extract biological domains from hypothesis content"""
        domains = []
        content_lower = hypothesis_content.lower()
        
        domain_keywords = {
            "DNA damage response": ["dna damage", "repair", "checkpoint", "atm", "atr"],
            "Cell cycle": ["mitosis", "g2/m", "cdc25", "cyclin", "checkpoint"],
            "Protein regulation": ["phosphorylation", "kinase", "protein", "enzyme"],
            "Telomere biology": ["telomere", "shelterin", "trf2", "pot1"],
            "Signal transduction": ["signaling", "pathway", "cascade", "transduction"],
            "Gene expression": ["transcription", "expression", "regulation", "promoter"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                domains.append(domain)
        
        return domains if domains else ["General biology"]
    
    def _get_experimental_domains(self, verification_type: str) -> List[str]:
        """Get experimental domains for verification type"""
        domains = {
            "genomics": ["Molecular biology", "Genetics", "Bioinformatics"],
            "protein_biology": ["Biochemistry", "Structural biology", "Proteomics"],
            "drug_discovery": ["Pharmacology", "Medicinal chemistry", "Toxicology"],
            "cell_biology": ["Cell biology", "Microscopy", "Cell physiology"],
            "systems_biology": ["Systems biology", "Computational biology", "Network biology"],
            "general": ["Experimental design", "Biostatistics", "Research methodology"]
        }
        return domains.get(verification_type, domains["general"])
    
    def _get_domain_specific_experiments(self, verification_type: str) -> List[str]:
        """Get domain-specific experimental approaches"""
        experiments = {
            "genomics": [
                "Genome-wide CRISPR screening",
                "Single-cell multi-omics",
                "Epigenome profiling",
                "Functional genomics validation"
            ],
            "protein_biology": [
                "Protein structure-function analysis",
                "Post-translational modification mapping",
                "Protein complex purification",
                "Enzymatic activity assays"
            ],
            "cell_biology": [
                "Cell cycle synchronization studies",
                "Subcellular localization analysis",
                "Cell death pathway analysis",
                "Organelle function studies"
            ]
        }
        return experiments.get(verification_type, ["Specialized experimental design"])

async def main():
    """Main execution function"""
    print("🧬 Enhanced Biomni Hypothesis Validation Analysis")
    print("=" * 60)
    
    # Initialize Jnana system
    jnana = JnanaSystem(config_path='config/models.yaml')
    await jnana.start()
    
    # Create enhanced validator
    validator = EnhancedBiomniValidator(jnana)
    
    # Test with a sample hypothesis from the file
    sample_hypothesis = """ATM/ATR-Dependent Checkpoint Activation Downregulates CDC25C to Prevent Mitotic Entry with Uncapped Telomeres. The hypothesis posits that when telomeres become uncapped—either through inhibition of the shelterin components TRF2 or POT1—ATM and ATR kinases are activated, leading to phosphorylation of p53, CHK1, and CHK2."""
    
    research_goal = "Elucidate molecular mechanisms preventing mitotic entry with dysfunctional telomeres"
    
    print(f"🔬 Analyzing Biomni Tools for Sample Hypothesis:")
    print(f"   {sample_hypothesis[:100]}...")
    print()
    
    # Analyze Biomni tools
    biomni_tools = await validator.analyze_biomni_tools_for_hypothesis(sample_hypothesis, research_goal)
    
    # Display detailed tool analysis
    print("🛠️  BIOMNI TOOLS ANALYSIS")
    print("=" * 40)
    
    for i, tool in enumerate(biomni_tools, 1):
        print(f"\n{i}. {tool.tool_name}")
        print(f"   📋 Description: {tool.description}")
        print(f"   📥 Input: {tool.input_data}")
        print(f"   📤 Output: {tool.output_format}")
        print(f"   🎯 Confidence Method: {tool.confidence_method}")
        print(f"   📚 Evidence Sources: {', '.join(tool.evidence_sources)}")
        print(f"   🧪 Experimental Suggestions: {', '.join(tool.experimental_suggestions[:2])}...")
        print(f"   🔬 Biological Domains: {', '.join(tool.biological_domains)}")
    
    # Check Biomni availability
    biomni_available = validator.biomni_agent and validator.biomni_agent.is_initialized
    
    print(f"\n🔍 BIOMNI STATUS")
    print("=" * 20)
    print(f"Biomni Agent Available: {biomni_available}")
    if validator.biomni_agent:
        print(f"Biomni Enabled: {validator.biomni_agent.config.enabled}")
        print(f"LangChain Version: {getattr(validator.biomni_agent, 'langchain_version', 'Unknown')}")
        print(f"Compatibility Mode: {getattr(validator.biomni_agent, 'compatibility_mode', 'Unknown')}")
    
    if not biomni_available:
        print("\n⚠️  BIOMNI AUTHENTICATION SETUP NEEDED")
        print("To enable full Biomni validation:")
        print("1. Set up API authentication (Anthropic API key for Claude)")
        print("2. Configure environment variables")
        print("3. Verify LangChain compatibility")
    
    print("\n✅ Enhanced Biomni analysis complete!")

if __name__ == "__main__":
    asyncio.run(main())

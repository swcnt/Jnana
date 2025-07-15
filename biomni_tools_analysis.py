#!/usr/bin/env python3
"""
Biomni Tools Analysis for Hypothesis Validation

This script analyzes which specific Biomni tools and methods would be used
for validating the DNA damage response hypotheses from hypothesis_extraction.txt
"""

import json
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

@dataclass
class BiomniTool:
    """Represents a specific Biomni validation tool"""
    name: str
    description: str
    input_type: str
    output_format: str
    confidence_method: str
    evidence_sources: List[str]
    experimental_suggestions: List[str]
    biological_domains: List[str]
    validation_approach: str

class BiomniToolsAnalyzer:
    """Analyzes which Biomni tools would be used for hypothesis validation"""
    
    def __init__(self):
        self.tools_catalog = self._initialize_biomni_tools()
    
    def _initialize_biomni_tools(self) -> Dict[str, BiomniTool]:
        """Initialize the catalog of available Biomni tools"""
        return {
            "biological_plausibility_analyzer": BiomniTool(
                name="Biological Plausibility Analyzer",
                description="Evaluates biological feasibility using literature knowledge and pathway analysis",
                input_type="Hypothesis text + research context",
                output_format="Plausibility score (0-1), evidence list, confidence intervals",
                confidence_method="Literature-weighted evidence scoring with uncertainty quantification",
                evidence_sources=["PubMed abstracts", "Pathway databases (KEGG, Reactome)", "Protein interaction databases"],
                experimental_suggestions=["Literature validation", "Pathway analysis", "Protein interaction studies"],
                biological_domains=["Molecular biology", "Cell biology", "Biochemistry"],
                validation_approach="Evidence-based literature mining with pathway context"
            ),
            
            "evidence_strength_assessor": BiomniTool(
                name="Evidence Strength Assessor",
                description="Quantifies supporting and contradicting evidence strength",
                input_type="Hypothesis + domain context",
                output_format="Evidence strength rating, quality metrics, reliability scores",
                confidence_method="Multi-source evidence weighting with publication quality assessment",
                evidence_sources=["Peer-reviewed publications", "Clinical trial databases", "Experimental datasets"],
                experimental_suggestions=["Systematic review", "Meta-analysis", "Evidence synthesis"],
                biological_domains=["Evidence-based medicine", "Biostatistics", "Research methodology"],
                validation_approach="Quantitative evidence evaluation with quality control"
            ),
            
            "experimental_design_suggester": BiomniTool(
                name="Experimental Design Suggester",
                description="Recommends specific experimental protocols to test hypotheses",
                input_type="Hypothesis + verification type + biological context",
                output_format="Ranked experimental protocols, feasibility scores, resource estimates",
                confidence_method="Protocol optimization with feasibility and statistical power analysis",
                evidence_sources=["Protocol databases", "Method publications", "Experimental guidelines"],
                experimental_suggestions=["Protocol optimization", "Statistical design", "Resource planning"],
                biological_domains=["Experimental design", "Biostatistics", "Laboratory methods"],
                validation_approach="Protocol-based experimental validation design"
            ),
            
            "domain_specific_validator": BiomniTool(
                name="Domain-Specific Validator",
                description="Specialized validation for specific biological domains",
                input_type="Domain-classified hypothesis + specialized context",
                output_format="Domain-specific confidence, specialized evidence, targeted experiments",
                confidence_method="Domain-specific algorithms with specialized knowledge bases",
                evidence_sources=["Domain databases", "Specialized literature", "Expert knowledge bases"],
                experimental_suggestions=["Domain-specific protocols", "Specialized assays", "Targeted validation"],
                biological_domains=["Variable by domain", "Specialized methodology"],
                validation_approach="Domain-expert knowledge with specialized validation criteria"
            ),
            
            "pathway_interaction_analyzer": BiomniTool(
                name="Pathway Interaction Analyzer",
                description="Analyzes molecular pathways and protein interactions relevant to hypothesis",
                input_type="Protein/gene names + pathway context",
                output_format="Pathway maps, interaction networks, regulatory relationships",
                confidence_method="Network topology analysis with pathway enrichment scoring",
                evidence_sources=["STRING database", "BioGRID", "Reactome pathways", "KEGG pathways"],
                experimental_suggestions=["Pathway perturbation", "Network analysis", "Systems biology approaches"],
                biological_domains=["Systems biology", "Network biology", "Pathway analysis"],
                validation_approach="Network-based validation with pathway context"
            ),
            
            "literature_evidence_miner": BiomniTool(
                name="Literature Evidence Miner",
                description="Mines scientific literature for supporting and contradicting evidence",
                input_type="Hypothesis keywords + biological entities",
                output_format="Evidence statements, citation quality, temporal trends",
                confidence_method="Citation-weighted evidence scoring with recency bias",
                evidence_sources=["PubMed Central", "Semantic Scholar", "bioRxiv preprints"],
                experimental_suggestions=["Literature gap analysis", "Citation network analysis", "Trend analysis"],
                biological_domains=["Scientific literature", "Knowledge discovery", "Text mining"],
                validation_approach="Comprehensive literature analysis with evidence quality assessment"
            )
        }
    
    def analyze_hypothesis_for_tools(self, hypothesis_text: str, hypothesis_title: str) -> Dict:
        """Analyze which Biomni tools would be used for a specific hypothesis"""
        
        # Determine biological domain
        domain = self._classify_biological_domain(hypothesis_text)
        
        # Determine verification type
        verification_type = self._determine_verification_type(hypothesis_text)
        
        # Select appropriate tools
        selected_tools = self._select_tools_for_hypothesis(hypothesis_text, domain, verification_type)
        
        # Generate detailed analysis
        analysis = {
            "hypothesis_title": hypothesis_title,
            "hypothesis_excerpt": hypothesis_text[:200] + "...",
            "biological_domain": domain,
            "verification_type": verification_type,
            "selected_tools": selected_tools,
            "validation_workflow": self._generate_validation_workflow(selected_tools),
            "expected_outputs": self._generate_expected_outputs(selected_tools),
            "confidence_methodology": self._generate_confidence_methodology(selected_tools)
        }
        
        return analysis
    
    def _classify_biological_domain(self, hypothesis_text: str) -> str:
        """Classify the biological domain of the hypothesis"""
        text_lower = hypothesis_text.lower()
        
        domain_keywords = {
            "DNA Damage Response": ["dna damage", "repair", "checkpoint", "atm", "atr", "chk1", "chk2"],
            "Cell Cycle Control": ["mitosis", "g2/m", "cdc25", "cyclin", "cell cycle"],
            "Protein Regulation": ["phosphorylation", "kinase", "protein", "enzyme", "regulation"],
            "Telomere Biology": ["telomere", "shelterin", "trf2", "pot1", "telomeric"],
            "Signal Transduction": ["signaling", "pathway", "cascade", "transduction", "activation"],
            "Gene Expression": ["transcription", "expression", "promoter", "transcriptional"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return domain
        
        return "General Biology"
    
    def _determine_verification_type(self, hypothesis_text: str) -> str:
        """Determine the type of verification needed"""
        text_lower = hypothesis_text.lower()
        
        if any(term in text_lower for term in ['protein', 'kinase', 'phosphorylation', 'enzyme']):
            return "protein_biology"
        elif any(term in text_lower for term in ['gene', 'transcription', 'expression']):
            return "genomics"
        elif any(term in text_lower for term in ['cell', 'cellular', 'mitosis']):
            return "cell_biology"
        elif any(term in text_lower for term in ['pathway', 'signaling', 'network']):
            return "systems_biology"
        else:
            return "general"
    
    def _select_tools_for_hypothesis(self, hypothesis_text: str, domain: str, verification_type: str) -> List[Dict]:
        """Select appropriate Biomni tools for the hypothesis"""
        selected = []
        
        # Always use core tools
        core_tools = ["biological_plausibility_analyzer", "evidence_strength_assessor", "literature_evidence_miner"]
        
        for tool_id in core_tools:
            tool = self.tools_catalog[tool_id]
            selected.append({
                "tool": asdict(tool),
                "relevance_score": 0.9,
                "usage_rationale": f"Core validation tool for {domain} hypotheses"
            })
        
        # Add experimental design suggester
        exp_tool = self.tools_catalog["experimental_design_suggester"]
        selected.append({
            "tool": asdict(exp_tool),
            "relevance_score": 0.8,
            "usage_rationale": f"Experimental validation design for {verification_type} research"
        })
        
        # Add domain-specific validator if not general
        if verification_type != "general":
            domain_tool = self.tools_catalog["domain_specific_validator"]
            selected.append({
                "tool": asdict(domain_tool),
                "relevance_score": 0.85,
                "usage_rationale": f"Specialized validation for {verification_type} domain"
            })
        
        # Add pathway analyzer for systems-level hypotheses
        if any(term in hypothesis_text.lower() for term in ['pathway', 'signaling', 'network', 'interaction']):
            pathway_tool = self.tools_catalog["pathway_interaction_analyzer"]
            selected.append({
                "tool": asdict(pathway_tool),
                "relevance_score": 0.75,
                "usage_rationale": "Pathway and interaction analysis for systems-level validation"
            })
        
        return selected
    
    def _generate_validation_workflow(self, selected_tools: List[Dict]) -> List[str]:
        """Generate the validation workflow steps"""
        workflow = [
            "1. Hypothesis preprocessing and biological entity extraction",
            "2. Literature evidence mining and quality assessment",
            "3. Biological plausibility analysis with pathway context",
            "4. Evidence strength quantification and confidence scoring",
            "5. Experimental design optimization and feasibility assessment",
            "6. Domain-specific validation with specialized criteria",
            "7. Results integration and final confidence calculation"
        ]
        return workflow
    
    def _generate_expected_outputs(self, selected_tools: List[Dict]) -> Dict:
        """Generate expected outputs from the validation process"""
        return {
            "confidence_score": "Quantitative confidence (0-1) with uncertainty bounds",
            "evidence_summary": "Supporting and contradicting evidence with quality scores",
            "experimental_protocols": "Ranked list of experimental approaches with feasibility",
            "biological_assessment": "Domain-specific biological plausibility evaluation",
            "literature_analysis": "Comprehensive literature evidence with citation quality",
            "pathway_context": "Relevant biological pathways and molecular interactions",
            "validation_report": "Structured validation report with methodology details"
        }
    
    def _generate_confidence_methodology(self, selected_tools: List[Dict]) -> Dict:
        """Generate confidence calculation methodology"""
        return {
            "evidence_weighting": "Literature quality × citation count × recency factor",
            "plausibility_scoring": "Biological feasibility × pathway consistency × experimental precedent",
            "uncertainty_quantification": "Confidence intervals based on evidence quality and consistency",
            "domain_adjustment": "Domain-specific confidence modifiers based on specialized knowledge",
            "final_integration": "Weighted combination of all tool outputs with uncertainty propagation"
        }

def main():
    """Main analysis function"""
    print("🧬 BIOMNI TOOLS ANALYSIS FOR HYPOTHESIS VALIDATION")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = BiomniToolsAnalyzer()
    
    # Sample hypotheses from the file
    sample_hypotheses = [
        {
            "title": "ATM/ATR-Dependent Checkpoint Activation",
            "text": "ATM/ATR-Dependent Checkpoint Activation Downregulates CDC25C to Prevent Mitotic Entry with Uncapped Telomeres. The hypothesis posits that when telomeres become uncapped—either through inhibition of the shelterin components TRF2 or POT1—ATM and ATR kinases are activated, leading to phosphorylation of p53, CHK1, and CHK2."
        },
        {
            "title": "p53/p21 Pathway Requirement",
            "text": "p53/p21 Pathway Is Required to Prevent Mitotic Entry When Telomeres Are Uncapped by TRF2 or POT1 Inhibition. This hypothesis asserts that the p53/p21 pathway is essential for preventing mitotic entry when telomeres are rendered dysfunctional by loss of TRF2 or POT1."
        },
        {
            "title": "Proteasome-Mediated CDC25C Degradation",
            "text": "Proteasome-mediated degradation of CDC25C is required for the G2/M checkpoint response to telomere dysfunction. The hypothesis proposes that CDC25C phosphatase undergoes proteasome-dependent degradation following telomere uncapping."
        }
    ]
    
    # Analyze each hypothesis
    for i, hyp in enumerate(sample_hypotheses, 1):
        print(f"\n🔬 HYPOTHESIS {i}: {hyp['title']}")
        print("-" * 50)
        
        analysis = analyzer.analyze_hypothesis_for_tools(hyp['text'], hyp['title'])
        
        print(f"📋 Biological Domain: {analysis['biological_domain']}")
        print(f"🔍 Verification Type: {analysis['verification_type']}")
        print(f"🛠️  Selected Tools: {len(analysis['selected_tools'])} tools")
        
        print(f"\n🛠️  BIOMNI TOOLS TO BE USED:")
        for j, tool_info in enumerate(analysis['selected_tools'], 1):
            tool = tool_info['tool']
            print(f"   {j}. {tool['name']}")
            print(f"      📝 Description: {tool['description']}")
            print(f"      📊 Relevance: {tool_info['relevance_score']:.2f}")
            print(f"      💡 Rationale: {tool_info['usage_rationale']}")
            print(f"      🔬 Validation: {tool['validation_approach']}")
        
        print(f"\n📈 EXPECTED VALIDATION OUTPUTS:")
        for output_type, description in analysis['expected_outputs'].items():
            print(f"   • {output_type.replace('_', ' ').title()}: {description}")
        
        print(f"\n🎯 CONFIDENCE METHODOLOGY:")
        for method_type, description in analysis['confidence_methodology'].items():
            print(f"   • {method_type.replace('_', ' ').title()}: {description}")
    
    print(f"\n📊 BIOMNI TOOLS CATALOG SUMMARY:")
    print(f"   Total Available Tools: {len(analyzer.tools_catalog)}")
    print(f"   Core Validation Tools: 3 (always used)")
    print(f"   Specialized Tools: 3 (domain-dependent)")
    print(f"   Average Tools per Hypothesis: 4-6 tools")
    
    print(f"\n✅ Biomni tools analysis complete!")
    print(f"   This analysis shows which specific Biomni tools would be used")
    print(f"   for validating each type of biological hypothesis.")

if __name__ == "__main__":
    main()

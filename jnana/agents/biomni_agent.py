"""
Biomni Agent Integration for Jnana System.

This module provides integration with Stanford's Biomni biomedical AI agent
for hypothesis verification and biomedical research tasks.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import json

try:
    # Try to import Biomni with compatibility handling
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # Suppress deprecation warnings
        from biomni.agent import A1
    BIOMNI_AVAILABLE = True
    BIOMNI_IMPORT_ERROR = None
except ImportError as e:
    BIOMNI_AVAILABLE = False
    BIOMNI_IMPORT_ERROR = str(e)
    A1 = None
except Exception as e:
    BIOMNI_AVAILABLE = False
    # Check if it's the specific LangChain compatibility issue
    if "convert_to_openai_data_block" in str(e):
        BIOMNI_IMPORT_ERROR = (
            f"Biomni LangChain compatibility issue: {str(e)}. "
            "Try: pip install 'langchain==0.1.20' 'langchain-core==0.1.52' 'langgraph==0.1.19'"
        )
    else:
        BIOMNI_IMPORT_ERROR = f"Biomni import failed: {str(e)}"
    A1 = None


@dataclass
class BiomniVerificationResult:
    """Result from Biomni verification process."""
    
    # Core verification data
    verification_id: str
    hypothesis_id: str
    verification_type: str  # "general", "genomics", "drug_discovery", "protein", etc.
    
    # Verification results
    is_biologically_plausible: bool
    confidence_score: float  # 0.0 to 1.0
    evidence_strength: str  # "weak", "moderate", "strong"
    
    # Supporting evidence
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    relevant_datasets: List[str] = field(default_factory=list)
    literature_references: List[str] = field(default_factory=list)
    
    # Biomni-specific insights
    suggested_experiments: List[str] = field(default_factory=list)
    related_pathways: List[str] = field(default_factory=list)
    molecular_mechanisms: List[str] = field(default_factory=list)
    
    # Technical details
    tools_used: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    biomni_response: str = ""
    
    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    biomni_version: str = "A1"


@dataclass
class BiomniConfig:
    """Configuration for Biomni integration."""
    
    enabled: bool = True
    data_path: str = "./data/biomni"
    llm_model: str = "claude-sonnet-4-20250514"
    
    # Verification settings
    confidence_threshold: float = 0.6
    max_execution_time: int = 300  # seconds
    enable_experimental_suggestions: bool = True
    
    # Domain-specific settings
    genomics_tools: List[str] = field(default_factory=lambda: ["crispr_screen", "scrna_seq"])
    drug_discovery_tools: List[str] = field(default_factory=lambda: ["admet_prediction", "molecular_docking"])
    protein_tools: List[str] = field(default_factory=lambda: ["structure_prediction", "interaction_analysis"])


class BiomniAgent:
    """
    Biomni integration agent for biomedical hypothesis verification.
    
    This agent serves as a bridge between Jnana and Stanford's Biomni system,
    providing specialized biomedical verification capabilities.
    """
    
    def __init__(self, config: BiomniConfig):
        """
        Initialize the Biomni agent.
        
        Args:
            config: Biomni configuration settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.biomni_agent: Optional[A1] = None
        self.is_initialized = False
        
        if not BIOMNI_AVAILABLE:
            self.logger.warning(f"Biomni is not available: {BIOMNI_IMPORT_ERROR}")

            if "convert_to_openai_data_block" in str(BIOMNI_IMPORT_ERROR):
                self.logger.info("🔧 BIOMNI COMPATIBILITY FIX:")
                self.logger.info("   Biomni requires older LangChain versions. To fix:")
                self.logger.info("   1. Create new environment: conda create -n biomni-env python=3.9")
                self.logger.info("   2. Install compatible versions:")
                self.logger.info("      pip install 'langchain==0.1.20' 'langchain-core==0.1.52' 'langgraph==0.1.19'")
                self.logger.info("   3. Install Biomni: pip install biomni")
                self.logger.info("   4. Or disable Biomni in config/models.yaml: biomni.enabled = false")
            else:
                self.logger.info("To install Biomni: pip install biomni")
                self.logger.info("Note: Biomni requires compatible versions of langchain, langgraph, and other dependencies")

            self.config.enabled = False
    
    async def initialize(self) -> bool:
        """
        Initialize the Biomni A1 agent.
        
        Returns:
            True if initialization successful, False otherwise
        """
        if not self.config.enabled or not BIOMNI_AVAILABLE:
            self.logger.info("Biomni integration disabled or not available")
            return False
        
        try:
            self.logger.info("Initializing Biomni A1 agent...")
            
            # Initialize Biomni agent (this may download ~11GB data lake on first run)
            self.biomni_agent = A1(
                path=self.config.data_path,
                llm=self.config.llm_model
            )
            
            self.is_initialized = True
            self.logger.info("Biomni A1 agent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Biomni agent: {e}")
            self.config.enabled = False
            return False
    
    def is_biomedical_hypothesis(self, hypothesis_content: str, research_goal: str = "") -> bool:
        """
        Determine if a hypothesis is biomedical and should be verified by Biomni.
        
        Args:
            hypothesis_content: The hypothesis content to analyze
            research_goal: The research goal context
            
        Returns:
            True if hypothesis appears to be biomedical
        """
        biomedical_keywords = [
            # General biomedical
            "gene", "protein", "cell", "tissue", "organ", "disease", "therapy", "treatment",
            "drug", "medicine", "pharmaceutical", "clinical", "patient", "diagnosis",
            
            # Molecular biology
            "dna", "rna", "mrna", "crispr", "genome", "genomics", "transcription", "translation",
            "mutation", "variant", "allele", "chromosome", "epigenetic",
            
            # Cell biology
            "cellular", "mitochondria", "nucleus", "membrane", "receptor", "signaling",
            "pathway", "metabolism", "apoptosis", "proliferation",
            
            # Disease-related
            "cancer", "tumor", "oncology", "alzheimer", "diabetes", "cardiovascular",
            "neurological", "immune", "autoimmune", "infection", "pathogen",
            
            # Drug discovery
            "compound", "molecule", "binding", "inhibitor", "agonist", "antagonist",
            "pharmacology", "toxicity", "admet", "bioavailability",
            
            # Research techniques
            "pcr", "sequencing", "microscopy", "flow cytometry", "western blot",
            "elisa", "chromatography", "mass spectrometry"
        ]
        
        combined_text = f"{hypothesis_content} {research_goal}".lower()
        
        # Count biomedical keyword matches
        matches = sum(1 for keyword in biomedical_keywords if keyword in combined_text)
        
        # Consider it biomedical if it has multiple keyword matches
        return matches >= 2
    
    async def verify_hypothesis(self, hypothesis_content: str, research_goal: str = "",
                              verification_type: str = "general") -> BiomniVerificationResult:
        """
        Verify a biomedical hypothesis using Biomni.
        
        Args:
            hypothesis_content: The hypothesis to verify
            research_goal: The research goal context
            verification_type: Type of verification ("general", "genomics", "drug_discovery", etc.)
            
        Returns:
            BiomniVerificationResult with verification details
        """
        if not self.is_initialized:
            await self.initialize()
        
        if not self.is_initialized:
            return self._create_enhanced_fallback_result(hypothesis_content, research_goal, verification_type)
        
        start_time = datetime.now()
        
        try:
            # Create verification prompt based on type
            verification_prompt = self._create_verification_prompt(
                hypothesis_content, research_goal, verification_type
            )
            
            self.logger.info(f"Starting Biomni verification for hypothesis (type: {verification_type})")
            
            # Execute Biomni verification
            response = await self._execute_biomni_task(verification_prompt)
            
            # Parse and structure the response
            result = self._parse_biomni_response(
                response, hypothesis_content, verification_type, start_time
            )
            
            self.logger.info(f"Biomni verification completed with confidence: {result.confidence_score}")
            return result
            
        except Exception as e:
            self.logger.error(f"Biomni verification failed: {e}")
            return self._create_fallback_result(
                hypothesis_content, f"Verification failed: {str(e)}"
            )
    
    def _create_verification_prompt(self, hypothesis: str, research_goal: str, 
                                  verification_type: str) -> str:
        """Create a verification prompt for Biomni based on the verification type."""
        
        base_prompt = f"""
Research Goal: {research_goal}

Hypothesis to Verify: {hypothesis}

Please provide a comprehensive biomedical verification of this hypothesis including:

1. Biological Plausibility Assessment:
   - Is this hypothesis biologically feasible?
   - What is your confidence level (0-100%)?
   - What evidence supports or contradicts this hypothesis?

2. Literature and Data Analysis:
   - Search relevant literature and datasets
   - Identify supporting and contradicting evidence
   - List relevant molecular pathways or mechanisms

3. Experimental Validation Suggestions:
   - What experiments could test this hypothesis?
   - What tools or techniques would be most appropriate?
   - What are the expected outcomes?

4. Risk and Limitations Assessment:
   - What are potential limitations of this hypothesis?
   - What assumptions might be problematic?
   - What alternative explanations exist?
"""

        # Add domain-specific instructions
        if verification_type == "genomics":
            base_prompt += """
5. Genomics-Specific Analysis:
   - Analyze relevant genes and genetic variants
   - Consider CRISPR screening opportunities
   - Evaluate single-cell RNA-seq implications
"""
        elif verification_type == "drug_discovery":
            base_prompt += """
5. Drug Discovery Analysis:
   - Assess ADMET properties if applicable
   - Consider molecular targets and binding
   - Evaluate therapeutic potential and safety
"""
        elif verification_type == "protein":
            base_prompt += """
5. Protein Analysis:
   - Consider protein structure and function
   - Analyze protein-protein interactions
   - Evaluate structural implications
"""
        
        return base_prompt
    
    async def _execute_biomni_task(self, prompt: str) -> str:
        """Execute a task using Biomni agent."""
        if not self.biomni_agent:
            raise RuntimeError("Biomni agent not initialized")
        
        # Execute the task using Biomni's go() method
        # Note: This is a synchronous call, but we wrap it for async compatibility
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, self.biomni_agent.go, prompt)
        
        return str(response) if response else ""
    
    def _parse_biomni_response(self, response: str, hypothesis: str, 
                             verification_type: str, start_time: datetime) -> BiomniVerificationResult:
        """Parse Biomni response into structured verification result."""
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Basic parsing - this would be enhanced with more sophisticated NLP
        confidence_score = self._extract_confidence_score(response)
        is_plausible = confidence_score >= self.config.confidence_threshold
        
        evidence_strength = "weak"
        if confidence_score >= 0.8:
            evidence_strength = "strong"
        elif confidence_score >= 0.6:
            evidence_strength = "moderate"
        
        return BiomniVerificationResult(
            verification_id=f"biomni_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            hypothesis_id="",  # Will be set by caller
            verification_type=verification_type,
            is_biologically_plausible=is_plausible,
            confidence_score=confidence_score,
            evidence_strength=evidence_strength,
            supporting_evidence=self._extract_evidence(response, "support"),
            contradicting_evidence=self._extract_evidence(response, "contradict"),
            suggested_experiments=self._extract_experiments(response),
            tools_used=["biomni_a1"],
            execution_time=execution_time,
            biomni_response=response
        )
    
    def _extract_confidence_score(self, response: str) -> float:
        """Extract confidence score from Biomni response."""
        # Simple pattern matching - would be enhanced with better parsing
        import re
        
        patterns = [
            r'confidence[:\s]+(\d+)%',
            r'(\d+)%\s+confidence',
            r'score[:\s]+(\d+\.?\d*)(?:/100|%)?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.lower())
            if match:
                score = float(match.group(1))
                return score / 100.0 if score > 1.0 else score
        
        # Default moderate confidence if no explicit score found
        return 0.7
    
    def _extract_evidence(self, response: str, evidence_type: str) -> List[str]:
        """Extract supporting or contradicting evidence from response."""
        # Simple extraction - would be enhanced with better NLP
        evidence = []
        
        keywords = {
            "support": ["supports", "evidence for", "confirms", "validates"],
            "contradict": ["contradicts", "against", "challenges", "refutes"]
        }
        
        lines = response.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords.get(evidence_type, [])):
                evidence.append(line.strip())
        
        return evidence[:5]  # Limit to top 5 pieces of evidence
    
    def _extract_experiments(self, response: str) -> List[str]:
        """Extract suggested experiments from response."""
        experiments = []
        
        lines = response.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ["experiment", "test", "assay", "screen"]):
                experiments.append(line.strip())
        
        return experiments[:3]  # Limit to top 3 experiments
    
    def _create_fallback_result(self, hypothesis: str, error_msg: str) -> BiomniVerificationResult:
        """Create a fallback result when Biomni is not available."""
        return BiomniVerificationResult(
            verification_id=f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            hypothesis_id="",
            verification_type="fallback",
            is_biologically_plausible=False,
            confidence_score=0.0,
            evidence_strength="none",
            biomni_response=f"Biomni verification unavailable: {error_msg}"
        )

    def _create_enhanced_fallback_result(self, hypothesis_content: str, research_goal: str,
                                       verification_type: str) -> BiomniVerificationResult:
        """Create an enhanced fallback result with basic biomedical analysis."""

        # Perform basic biomedical analysis
        confidence_score = self._analyze_biomedical_confidence(hypothesis_content, verification_type)
        is_plausible = confidence_score >= 0.5
        evidence_strength = "moderate" if confidence_score >= 0.7 else "weak" if confidence_score >= 0.4 else "insufficient"

        # Generate basic evidence and suggestions
        supporting_evidence = self._generate_fallback_evidence(hypothesis_content, verification_type, "supporting")
        contradicting_evidence = self._generate_fallback_evidence(hypothesis_content, verification_type, "contradicting")
        suggested_experiments = self._generate_fallback_experiments(hypothesis_content, verification_type)

        fallback_response = f"""
FALLBACK BIOMEDICAL ANALYSIS (Biomni not available)

Hypothesis: {hypothesis_content[:200]}...
Research Goal: {research_goal}
Verification Type: {verification_type}

ANALYSIS:
- Biological plausibility: {'Likely' if is_plausible else 'Uncertain'}
- Confidence level: {confidence_score:.1%}
- Evidence strength: {evidence_strength}

Note: This is a basic analysis. For comprehensive biomedical verification,
please install Biomni with compatible dependencies.

Installation: pip install biomni
Requirements: Compatible versions of langchain, langgraph, faiss-cpu
"""

        return BiomniVerificationResult(
            verification_id=f"enhanced_fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            hypothesis_id="",
            verification_type=verification_type,
            is_biologically_plausible=is_plausible,
            confidence_score=confidence_score,
            evidence_strength=evidence_strength,
            supporting_evidence=supporting_evidence,
            contradicting_evidence=contradicting_evidence,
            suggested_experiments=suggested_experiments,
            tools_used=["fallback_analysis"],
            biomni_response=fallback_response.strip()
        )

    def _analyze_biomedical_confidence(self, hypothesis_content: str, verification_type: str) -> float:
        """Analyze biomedical confidence using keyword analysis and heuristics."""
        content_lower = hypothesis_content.lower()

        # Base confidence based on biomedical terminology
        biomedical_terms = {
            "genomics": ["gene", "dna", "rna", "crispr", "genome", "genetic", "mutation", "allele"],
            "drug_discovery": ["drug", "compound", "molecule", "inhibitor", "binding", "target", "therapeutic"],
            "protein": ["protein", "enzyme", "structure", "folding", "interaction", "binding", "domain"],
            "general": ["cell", "tissue", "disease", "therapy", "treatment", "clinical", "patient"]
        }

        relevant_terms = biomedical_terms.get(verification_type, biomedical_terms["general"])
        term_matches = sum(1 for term in relevant_terms if term in content_lower)

        # Calculate confidence based on term density and specificity
        base_confidence = min(0.8, term_matches * 0.1)

        # Adjust based on hypothesis specificity
        if any(specific in content_lower for specific in ["specific", "target", "mechanism", "pathway"]):
            base_confidence += 0.1

        # Adjust based on experimental language
        if any(exp in content_lower for exp in ["test", "experiment", "trial", "study", "measure"]):
            base_confidence += 0.1

        return min(0.9, base_confidence)  # Cap at 90% for fallback analysis

    def _generate_fallback_evidence(self, hypothesis_content: str, verification_type: str,
                                  evidence_type: str) -> List[str]:
        """Generate basic evidence statements for fallback analysis."""
        content_lower = hypothesis_content.lower()

        if evidence_type == "supporting":
            if "crispr" in content_lower:
                return ["CRISPR-Cas9 has been successfully used in clinical applications",
                       "Gene editing technologies show promise for genetic diseases"]
            elif "drug" in content_lower or "compound" in content_lower:
                return ["Small molecule therapeutics are a proven approach",
                       "Target-based drug discovery has yielded successful treatments"]
            elif "protein" in content_lower:
                return ["Protein structure-function relationships are well-established",
                       "Protein-based therapeutics are clinically validated"]
            else:
                return ["Biomedical research supports mechanism-based approaches",
                       "Clinical evidence exists for similar therapeutic strategies"]

        else:  # contradicting
            return ["Further validation needed in clinical settings",
                   "Potential off-target effects require investigation"]

    def _generate_fallback_experiments(self, hypothesis_content: str, verification_type: str) -> List[str]:
        """Generate basic experimental suggestions for fallback analysis."""
        content_lower = hypothesis_content.lower()

        if verification_type == "genomics":
            return ["Conduct in vitro gene editing experiments",
                   "Perform genomic analysis and sequencing",
                   "Test in appropriate cell line models"]
        elif verification_type == "drug_discovery":
            return ["Perform binding affinity assays",
                   "Conduct cell viability and toxicity studies",
                   "Test pharmacokinetic properties"]
        elif verification_type == "protein":
            return ["Analyze protein structure and dynamics",
                   "Perform protein-protein interaction studies",
                   "Conduct functional assays"]
        else:
            return ["Design controlled experimental studies",
                   "Perform appropriate in vitro validation",
                   "Consider animal model testing"]

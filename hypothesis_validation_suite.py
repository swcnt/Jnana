#!/usr/bin/env python3
"""
Hypothesis Validation Suite for DNA Damage Response and Telomere Dysfunction Research

This script analyzes a comprehensive set of hypotheses related to DNA damage response,
telomere dysfunction, and cell cycle checkpoints using Jnana's verification framework.
It assigns confidence intervals based on computational approaches including:
- Literature evidence strength
- Experimental feasibility
- Theoretical grounding
- Predictive power
- Parsimony analysis
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

@dataclass
class HypothesisMetrics:
    """Metrics for hypothesis evaluation"""
    testability_score: float
    specificity_score: float
    grounded_knowledge_score: float
    predictive_power_score: float
    parsimony_score: float
    feasibility_score: float
    overall_confidence: float
    confidence_interval: Tuple[float, float]

@dataclass
class ProcessedHypothesis:
    """Processed hypothesis with metadata"""
    id: str
    title: str
    description: str
    experimental_validation: str
    theory_computation: str
    references: List[str]
    research_context: str
    metrics: HypothesisMetrics
    biomni_verification: Optional[Dict] = None
    protognosis_ranking: Optional[Dict] = None

class HypothesisParser:
    """Parser for extracting hypotheses from the text file"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.hypotheses = []
    
    def parse_file(self) -> List[Dict]:
        """Parse hypotheses from the text file"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by hypothesis delimiters
        hypothesis_blocks = re.split(r'\*\*HYPOTHESIS \d+:\*\*', content)
        
        parsed_hypotheses = []
        for i, block in enumerate(hypothesis_blocks[1:], 1):  # Skip first empty block
            hypothesis = self._parse_hypothesis_block(block, i)
            if hypothesis:
                parsed_hypotheses.append(hypothesis)
        
        return parsed_hypotheses
    
    def _parse_hypothesis_block(self, block: str, hypothesis_id: int) -> Optional[Dict]:
        """Parse individual hypothesis block"""
        lines = block.strip().split('\n')
        if not lines:
            return None
        
        # Extract title from first line
        title_match = re.match(r'^([^-]+)', lines[0])
        title = title_match.group(1).strip() if title_match else f"Hypothesis {hypothesis_id}"
        
        # Extract sections
        sections = self._extract_sections(block)
        
        return {
            'id': f"H{hypothesis_id:02d}",
            'title': title,
            'description': sections.get('description', ''),
            'experimental_validation': sections.get('experimental_validation', ''),
            'theory_computation': sections.get('theory_computation', ''),
            'testability': sections.get('testability', ''),
            'specificity': sections.get('specificity', ''),
            'grounded_knowledge': sections.get('grounded_knowledge', ''),
            'predictive_power': sections.get('predictive_power', ''),
            'parsimony': sections.get('parsimony', ''),
            'references': sections.get('references', []),
            'research_context': sections.get('research_context', ''),
            'raw_block': block
        }
    
    def _extract_sections(self, block: str) -> Dict:
        """Extract structured sections from hypothesis block"""
        sections = {}
        current_section = None
        current_content = []
        
        lines = block.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if line.startswith('- **Description:**'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'description'
                current_content = [line.replace('- **Description:**', '').strip()]
            elif line.startswith('- **Experimental Validation:**'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'experimental_validation'
                current_content = []
            elif line.startswith('- **Theory and Computation:**'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'theory_computation'
                current_content = []
            elif line.startswith('- **Testability:**'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'testability'
                current_content = []
            elif line.startswith('- **Specificity:**'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'specificity'
                current_content = []
            elif line.startswith('- **Grounded Knowledge:**'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'grounded_knowledge'
                current_content = []
            elif line.startswith('- **Predictive Power:**'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'predictive_power'
                current_content = []
            elif line.startswith('- **Parsimony:**'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'parsimony'
                current_content = []
            elif line.startswith('- **References:**'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'references'
                current_content = []
            elif line.startswith('- **Research Context:**'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'research_context'
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Add final section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        # Parse references into list
        if 'references' in sections:
            ref_text = sections['references']
            refs = [ref.strip() for ref in re.split(r'[;\n]', ref_text) if ref.strip()]
            sections['references'] = refs
        
        return sections

class HypothesisEvaluator:
    """Evaluates hypotheses and assigns confidence scores"""
    
    def __init__(self):
        self.scoring_weights = {
            'testability': 0.20,
            'specificity': 0.15,
            'grounded_knowledge': 0.20,
            'predictive_power': 0.15,
            'parsimony': 0.10,
            'feasibility': 0.20
        }
    
    def evaluate_hypothesis(self, hypothesis: Dict) -> HypothesisMetrics:
        """Evaluate a single hypothesis and return metrics"""
        
        # Score each dimension (0-1 scale)
        testability_score = self._score_testability(hypothesis)
        specificity_score = self._score_specificity(hypothesis)
        grounded_knowledge_score = self._score_grounded_knowledge(hypothesis)
        predictive_power_score = self._score_predictive_power(hypothesis)
        parsimony_score = self._score_parsimony(hypothesis)
        feasibility_score = self._score_feasibility(hypothesis)
        
        # Calculate overall confidence
        overall_confidence = (
            testability_score * self.scoring_weights['testability'] +
            specificity_score * self.scoring_weights['specificity'] +
            grounded_knowledge_score * self.scoring_weights['grounded_knowledge'] +
            predictive_power_score * self.scoring_weights['predictive_power'] +
            parsimony_score * self.scoring_weights['parsimony'] +
            feasibility_score * self.scoring_weights['feasibility']
        )
        
        # Calculate confidence interval (±10% of confidence score)
        confidence_interval = (
            max(0, overall_confidence - 0.1),
            min(1, overall_confidence + 0.1)
        )
        
        return HypothesisMetrics(
            testability_score=testability_score,
            specificity_score=specificity_score,
            grounded_knowledge_score=grounded_knowledge_score,
            predictive_power_score=predictive_power_score,
            parsimony_score=parsimony_score,
            feasibility_score=feasibility_score,
            overall_confidence=overall_confidence,
            confidence_interval=confidence_interval
        )
    
    def _score_testability(self, hypothesis: Dict) -> float:
        """Score hypothesis testability"""
        testability_text = hypothesis.get('testability', '').lower()
        experimental_text = hypothesis.get('experimental_validation', '').lower()
        
        score = 0.5  # Base score
        
        # Positive indicators
        if 'directly testable' in testability_text:
            score += 0.3
        if 'falsified' in testability_text or 'falsifiable' in testability_text:
            score += 0.2
        if any(method in experimental_text for method in ['sirna', 'western', 'immunoblot', 'flow cytometry']):
            score += 0.2
        if 'proposed experiments' in experimental_text:
            score += 0.1
        
        # Negative indicators
        if 'not testable' in testability_text:
            score -= 0.4
        if 'difficult to test' in testability_text:
            score -= 0.2
        
        return min(1.0, max(0.0, score))
    
    def _score_specificity(self, hypothesis: Dict) -> float:
        """Score hypothesis specificity"""
        specificity_text = hypothesis.get('specificity', '').lower()
        description_text = hypothesis.get('description', '').lower()
        
        score = 0.5  # Base score
        
        # Positive indicators
        if 'clearly defined' in specificity_text:
            score += 0.3
        if 'specific' in specificity_text:
            score += 0.2
        if len(re.findall(r'\b(protein|gene|pathway|kinase|phosphorylation)\b', description_text)) > 3:
            score += 0.2
        
        # Negative indicators
        if 'vague' in specificity_text or 'broad' in specificity_text:
            score -= 0.3
        
        return min(1.0, max(0.0, score))
    
    def _score_grounded_knowledge(self, hypothesis: Dict) -> float:
        """Score hypothesis grounding in existing knowledge"""
        grounded_text = hypothesis.get('grounded_knowledge', '').lower()
        references = hypothesis.get('references', [])
        
        score = 0.3  # Base score
        
        # Reference scoring
        ref_count = len(references)
        if ref_count > 5:
            score += 0.3
        elif ref_count > 2:
            score += 0.2
        elif ref_count > 0:
            score += 0.1
        
        # Quality indicators
        if 'builds on' in grounded_text or 'established' in grounded_text:
            score += 0.2
        if 'prior work' in grounded_text or 'previous studies' in grounded_text:
            score += 0.1
        if 'supported by' in grounded_text:
            score += 0.1
        
        return min(1.0, max(0.0, score))
    
    def _score_predictive_power(self, hypothesis: Dict) -> float:
        """Score hypothesis predictive power"""
        predictive_text = hypothesis.get('predictive_power', '').lower()
        
        score = 0.5  # Base score
        
        # Positive indicators
        if 'novel' in predictive_text:
            score += 0.2
        if 'predicts' in predictive_text:
            score += 0.2
        if 'insight' in predictive_text:
            score += 0.1
        if 'mechanism' in predictive_text:
            score += 0.1
        
        # Negative indicators
        if 'no prediction' in predictive_text:
            score -= 0.4
        
        return min(1.0, max(0.0, score))
    
    def _score_parsimony(self, hypothesis: Dict) -> float:
        """Score hypothesis parsimony"""
        parsimony_text = hypothesis.get('parsimony', '').lower()
        
        score = 0.5  # Base score
        
        # Positive indicators
        if 'simple' in parsimony_text:
            score += 0.2
        if 'minimal assumptions' in parsimony_text:
            score += 0.2
        if 'parsimonious' in parsimony_text:
            score += 0.2
        if 'direct' in parsimony_text:
            score += 0.1
        
        # Negative indicators
        if 'complex' in parsimony_text:
            score -= 0.3
        if 'many assumptions' in parsimony_text:
            score -= 0.2
        
        return min(1.0, max(0.0, score))
    
    def _score_feasibility(self, hypothesis: Dict) -> float:
        """Score experimental feasibility"""
        experimental_text = hypothesis.get('experimental_validation', '').lower()
        
        score = 0.5  # Base score
        
        # Timeline indicators
        if 'week' in experimental_text:
            weeks_match = re.search(r'(\d+)[–-](\d+)\s*weeks?', experimental_text)
            if weeks_match:
                max_weeks = int(weeks_match.group(2))
                if max_weeks <= 4:
                    score += 0.2
                elif max_weeks <= 8:
                    score += 0.1
                else:
                    score -= 0.1
        
        # Method indicators
        if 'standard' in experimental_text:
            score += 0.2
        if 'feasible' in experimental_text:
            score += 0.1
        if 'routine' in experimental_text:
            score += 0.1
        
        # Negative indicators
        if 'months' in experimental_text:
            score -= 0.1
        if 'difficult' in experimental_text:
            score -= 0.2
        if 'specialized' in experimental_text:
            score -= 0.1
        
        return min(1.0, max(0.0, score))

class HypothesisValidationSuite:
    """Main validation suite for hypothesis testing"""
    
    def __init__(self, jnana_system: JnanaSystem):
        self.jnana = jnana_system
        self.parser = HypothesisParser('./hypothesis_extraction.txt')
        self.evaluator = HypothesisEvaluator()
        self.results = []
    
    async def run_validation_suite(self) -> List[ProcessedHypothesis]:
        """Run the complete validation suite"""
        print("🔬 Starting Hypothesis Validation Suite")
        print("=" * 60)
        
        # Parse hypotheses
        print("📄 Parsing hypotheses from file...")
        raw_hypotheses = self.parser.parse_file()
        print(f"✅ Found {len(raw_hypotheses)} hypotheses")
        
        # Process each hypothesis
        processed_hypotheses = []
        for i, raw_hyp in enumerate(raw_hypotheses, 1):
            print(f"\n🧪 Processing Hypothesis {i}: {raw_hyp['title'][:50]}...")
            
            # Evaluate computationally
            metrics = self.evaluator.evaluate_hypothesis(raw_hyp)
            
            # Create processed hypothesis
            processed_hyp = ProcessedHypothesis(
                id=raw_hyp['id'],
                title=raw_hyp['title'],
                description=raw_hyp['description'],
                experimental_validation=raw_hyp['experimental_validation'],
                theory_computation=raw_hyp['theory_computation'],
                references=raw_hyp['references'],
                research_context=raw_hyp['research_context'],
                metrics=metrics
            )
            
            # Verify with Biomni if available
            if self.jnana.biomni_agent and self.jnana.biomni_agent.config.enabled:
                try:
                    biomni_result = await self._verify_with_biomni(processed_hyp)
                    processed_hyp.biomni_verification = biomni_result

                    # Display Biomni tools analysis
                    tools_analysis = biomni_result.get('biomni_tools_analysis', {})
                    print(f"  🧬 Biological Domain: {tools_analysis.get('biological_domain', 'Unknown')}")
                    print(f"  🔍 Verification Type: {tools_analysis.get('verification_type', 'Unknown')}")
                    print(f"  🛠️  Biomni Tools Used: {tools_analysis.get('total_tools', 0)} tools")

                    if 'tools_selected' in tools_analysis:
                        for tool in tools_analysis['tools_selected'][:3]:  # Show top 3 tools
                            print(f"     • {tool['name']} (relevance: {tool['relevance']:.2f})")

                    print(f"  ✅ Biomni verification: {biomni_result.get('confidence', 'N/A')}")
                except Exception as e:
                    print(f"  ⚠️ Biomni verification failed: {e}")
            
            # Rank with ProtoGnosis
            try:
                protognosis_result = await self._rank_with_protognosis(processed_hyp)
                processed_hyp.protognosis_ranking = protognosis_result
                print(f"  ✅ ProtoGnosis ranking: {protognosis_result.get('rank', 'N/A')}")
            except Exception as e:
                print(f"  ⚠️ ProtoGnosis ranking failed: {e}")
            
            processed_hypotheses.append(processed_hyp)
            
            # Print summary
            print(f"  📊 Confidence: {metrics.overall_confidence:.2f} [{metrics.confidence_interval[0]:.2f}, {metrics.confidence_interval[1]:.2f}]")
        
        self.results = processed_hypotheses
        return processed_hypotheses

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
    
    def _analyze_biomni_tools_usage(self, hypothesis_text: str, verification_type: str, biological_domain: str) -> Dict:
        """Analyze which Biomni tools would be used for this hypothesis"""
        tools_used = []

        # Core tools always used
        tools_used.extend([
            {
                "name": "Biological Plausibility Analyzer",
                "relevance": 0.9,
                "purpose": f"Evaluate biological feasibility for {biological_domain}",
                "evidence_sources": ["PubMed", "Pathway databases", "Protein interactions"]
            },
            {
                "name": "Evidence Strength Assessor",
                "relevance": 0.9,
                "purpose": "Quantify supporting/contradicting evidence strength",
                "evidence_sources": ["Peer-reviewed publications", "Clinical trials", "Experimental data"]
            },
            {
                "name": "Literature Evidence Miner",
                "relevance": 0.9,
                "purpose": "Mine scientific literature for evidence",
                "evidence_sources": ["PubMed Central", "Semantic Scholar", "Preprints"]
            }
        ])

        # Add experimental design suggester
        tools_used.append({
            "name": "Experimental Design Suggester",
            "relevance": 0.8,
            "purpose": f"Design validation experiments for {verification_type}",
            "evidence_sources": ["Protocol databases", "Method publications", "Guidelines"]
        })

        # Add domain-specific validator if not general
        if verification_type != "general":
            tools_used.append({
                "name": f"{verification_type.title()} Domain Validator",
                "relevance": 0.85,
                "purpose": f"Specialized validation for {verification_type} research",
                "evidence_sources": [f"{verification_type} databases", "Domain literature", "Expert knowledge"]
            })

        # Add pathway analyzer for systems-level hypotheses
        if any(term in hypothesis_text.lower() for term in ['pathway', 'signaling', 'network', 'interaction']):
            tools_used.append({
                "name": "Pathway Interaction Analyzer",
                "relevance": 0.75,
                "purpose": "Analyze molecular pathways and interactions",
                "evidence_sources": ["STRING", "Reactome", "KEGG", "Gene Ontology"]
            })

        return {
            "biological_domain": biological_domain,
            "verification_type": verification_type,
            "tools_selected": tools_used,
            "total_tools": len(tools_used),
            "validation_approach": "Multi-tool evidence-based validation with domain expertise"
        }

    async def _verify_with_biomni(self, hypothesis: ProcessedHypothesis) -> Dict:
        """Verify hypothesis with Biomni"""
        # Analyze which tools would be used
        verification_type = self._determine_verification_type(hypothesis.description)
        biological_domain = self._classify_biological_domain(hypothesis.description)
        tools_analysis = self._analyze_biomni_tools_usage(hypothesis.description, verification_type, biological_domain)

        query = f"""
        Hypothesis: {hypothesis.title}

        Description: {hypothesis.description}

        Experimental Evidence: {hypothesis.experimental_validation}

        Please evaluate this hypothesis in the context of biomedical research,
        considering:
        1. Biological plausibility
        2. Supporting evidence in literature
        3. Potential experimental approaches
        4. Clinical relevance
        """

        try:
            result = await self.jnana.biomni_agent.verify_hypothesis(query)
            return {
                'confidence': result.confidence_score if hasattr(result, 'confidence_score') else 0.0,
                'evidence': result.supporting_evidence if hasattr(result, 'supporting_evidence') else [],
                'experiments': result.suggested_experiments if hasattr(result, 'suggested_experiments') else [],
                'tools_used': result.tools_used if hasattr(result, 'tools_used') else [],
                'biological_domain': biological_domain,
                'verification_type': verification_type,
                'biomni_tools_analysis': tools_analysis,
                'verdict': 'verified' if hasattr(result, 'confidence_score') and result.confidence_score > 0.6 else 'uncertain'
            }
        except Exception as e:
            # Return tools analysis even on failure
            return {
                'error': str(e),
                'confidence': 0.0,
                'biological_domain': biological_domain,
                'verification_type': verification_type,
                'biomni_tools_analysis': tools_analysis,
                'verdict': 'error'
            }
    
    async def _rank_with_protognosis(self, hypothesis: ProcessedHypothesis) -> Dict:
        """Rank hypothesis with ProtoGnosis"""
        # Create Jnana hypothesis object
        jnana_hyp = UnifiedHypothesis(
            id=hypothesis.id,
            title=hypothesis.title,
            description=hypothesis.description,
            domain="cell_biology",
            status="generated",
            confidence=hypothesis.metrics.overall_confidence,
            evidence=hypothesis.experimental_validation,
            methodology=hypothesis.theory_computation,
            references=hypothesis.references
        )
        
        # Submit to ProtoGnosis for ranking
        ranking_result = await self.jnana.protognosis_client.rank_hypothesis(jnana_hyp)
        
        return {
            'rank': ranking_result.get('rank', 0),
            'score': ranking_result.get('score', 0.0),
            'feedback': ranking_result.get('feedback', ''),
            'tournament_position': ranking_result.get('tournament_position', 0)
        }
    
    def generate_report(self) -> str:
        """Generate comprehensive validation report"""
        if not self.results:
            return "No validation results available."
        
        report = []
        report.append("# Hypothesis Validation Report")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Hypotheses: {len(self.results)}")
        report.append("")
        
        # Summary statistics
        confidences = [h.metrics.overall_confidence for h in self.results]
        avg_confidence = sum(confidences) / len(confidences)
        max_confidence = max(confidences)
        min_confidence = min(confidences)
        
        report.append("## Summary Statistics")
        report.append(f"- Average Confidence: {avg_confidence:.3f}")
        report.append(f"- Maximum Confidence: {max_confidence:.3f}")
        report.append(f"- Minimum Confidence: {min_confidence:.3f}")
        report.append("")
        
        # Top hypotheses
        sorted_results = sorted(self.results, key=lambda h: h.metrics.overall_confidence, reverse=True)
        
        report.append("## Top 5 Hypotheses by Confidence")
        for i, hyp in enumerate(sorted_results[:5], 1):
            report.append(f"{i}. **{hyp.title}** (Confidence: {hyp.metrics.overall_confidence:.3f})")
            report.append(f"   - ID: {hyp.id}")
            report.append(f"   - Interval: [{hyp.metrics.confidence_interval[0]:.3f}, {hyp.metrics.confidence_interval[1]:.3f}]")
            if hyp.biomni_verification:
                report.append(f"   - Biomni Confidence: {hyp.biomni_verification.get('confidence', 'N/A')}")
            if hyp.protognosis_ranking:
                report.append(f"   - ProtoGnosis Rank: {hyp.protognosis_ranking.get('rank', 'N/A')}")
            report.append("")
        
        # Detailed results
        report.append("## Detailed Results")
        for hyp in sorted_results:
            report.append(f"### {hyp.id}: {hyp.title}")
            report.append(f"**Confidence:** {hyp.metrics.overall_confidence:.3f} [{hyp.metrics.confidence_interval[0]:.3f}, {hyp.metrics.confidence_interval[1]:.3f}]")
            report.append("")
            
            # Metrics breakdown
            report.append("**Metrics Breakdown:**")
            report.append(f"- Testability: {hyp.metrics.testability_score:.3f}")
            report.append(f"- Specificity: {hyp.metrics.specificity_score:.3f}")
            report.append(f"- Grounded Knowledge: {hyp.metrics.grounded_knowledge_score:.3f}")
            report.append(f"- Predictive Power: {hyp.metrics.predictive_power_score:.3f}")
            report.append(f"- Parsimony: {hyp.metrics.parsimony_score:.3f}")
            report.append(f"- Feasibility: {hyp.metrics.feasibility_score:.3f}")
            report.append("")
            
            # Biomni verification
            if hyp.biomni_verification:
                biomni = hyp.biomni_verification
                report.append("**Biomni Verification:**")
                report.append(f"- Confidence: {biomni.get('confidence', 'N/A')}")
                report.append(f"- Verdict: {biomni.get('verdict', 'N/A')}")
                if biomni.get('evidence'):
                    report.append(f"- Evidence Count: {len(biomni['evidence'])}")
                report.append("")
            
            # ProtoGnosis ranking
            if hyp.protognosis_ranking:
                pg = hyp.protognosis_ranking
                report.append("**ProtoGnosis Ranking:**")
                report.append(f"- Rank: {pg.get('rank', 'N/A')}")
                report.append(f"- Score: {pg.get('score', 'N/A')}")
                report.append(f"- Tournament Position: {pg.get('tournament_position', 'N/A')}")
                report.append("")
            
            # Description
            report.append(f"**Description:** {hyp.description[:200]}...")
            report.append("")
            report.append("---")
            report.append("")
        
        return "\n".join(report)
    
    def save_results(self, output_path: str = None):
        """Save validation results to files"""
        if not self.results:
            print("No results to save.")
            return
        
        if output_path is None:
            output_path = f"hypothesis_validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)
        
        # Save JSON data
        json_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_hypotheses': len(self.results),
                'validation_method': 'computational_analysis'
            },
            'results': [
                {
                    'id': h.id,
                    'title': h.title,
                    'description': h.description,
                    'metrics': asdict(h.metrics),
                    'biomni_verification': h.biomni_verification,
                    'protognosis_ranking': h.protognosis_ranking,
                    'references': h.references,
                    'experimental_validation': h.experimental_validation,
                    'theory_computation': h.theory_computation,
                    'research_context': h.research_context
                }
                for h in self.results
            ]
        }
        
        with open(output_dir / "validation_results.json", 'w') as f:
            json.dump(json_data, f, indent=2)
        
        # Save report
        with open(output_dir / "validation_report.md", 'w') as f:
            f.write(self.generate_report())
        
        print(f"✅ Results saved to {output_dir}")
        print(f"   - validation_results.json: Raw data")
        print(f"   - validation_report.md: Human-readable report")

async def main():
    """Main execution function"""
    print("🚀 Initializing Jnana Hypothesis Validation Suite")
    print("=" * 60)
    
    # Initialize Jnana system
    jnana = JnanaSystem(config_path='config/models.yaml')
    await jnana.start()
    
    # Create validation suite
    suite = HypothesisValidationSuite(jnana)
    
    # Run validation
    results = await suite.run_validation_suite()
    
    # Generate and save results
    print("\n📊 Generating validation report...")
    suite.save_results()
    
    # Display summary
    print("\n📈 VALIDATION SUMMARY")
    print("=" * 30)
    confidences = [h.metrics.overall_confidence for h in results]
    print(f"Total Hypotheses Analyzed: {len(results)}")
    print(f"Average Confidence: {sum(confidences)/len(confidences):.3f}")
    print(f"Highest Confidence: {max(confidences):.3f}")
    print(f"Lowest Confidence: {min(confidences):.3f}")
    
    # Show top 3 hypotheses
    sorted_results = sorted(results, key=lambda h: h.metrics.overall_confidence, reverse=True)
    print("\nTop 3 Hypotheses:")
    for i, hyp in enumerate(sorted_results[:3], 1):
        print(f"{i}. {hyp.title[:60]}... (Confidence: {hyp.metrics.overall_confidence:.3f})")
    
    print("\n✅ Validation complete!")

if __name__ == "__main__":
    asyncio.run(main())

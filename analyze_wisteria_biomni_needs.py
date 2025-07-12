#!/usr/bin/env python3
"""
Wisteria JSON Analysis for Biomni Validation Needs.

This script analyzes all Wisteria JSON files to determine which hypotheses
require biomedical validation and creates targeted validation scripts.
"""

import json
import logging
from pathlib import Path
import sys
from typing import List, Dict, Any, Tuple
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WisteriaBiomniAnalyzer:
    """
    Analyzer to determine which Wisteria hypotheses need Biomni validation.
    """
    
    def __init__(self, json_directory: str = "wisteria-json"):
        """
        Initialize the analyzer.
        
        Args:
            json_directory: Directory containing Wisteria JSON files
        """
        self.json_directory = Path(json_directory)
        self.analysis_results = {}
        
        # Biomedical keywords for classification
        self.biomedical_keywords = {
            'diseases': [
                'alzheimer', 'parkinson', 'neurodegenerative', 'cancer', 'diabetes',
                'cardiovascular', 'stroke', 'epilepsy', 'depression', 'autism',
                'huntington', 'als', 'multiple sclerosis', 'dementia'
            ],
            'biological_systems': [
                'mitochondrial', 'neuronal', 'synaptic', 'cellular', 'molecular',
                'genetic', 'epigenetic', 'protein', 'dna', 'rna', 'enzyme',
                'receptor', 'neurotransmitter', 'hormone', 'immune', 'inflammatory'
            ],
            'biological_processes': [
                'apoptosis', 'autophagy', 'ferroptosis', 'aggregation', 'folding',
                'methylation', 'phosphorylation', 'oxidative stress', 'metabolism',
                'signaling', 'transcription', 'translation', 'replication'
            ],
            'anatomy': [
                'brain', 'neuron', 'synapse', 'hippocampus', 'cortex', 'cerebellum',
                'gut', 'microbiome', 'blood-brain barrier', 'nervous system'
            ],
            'medical_interventions': [
                'therapy', 'treatment', 'drug', 'pharmaceutical', 'clinical',
                'therapeutic', 'medicine', 'biomarker', 'diagnosis'
            ],
            'research_methods': [
                'crispr', 'gene editing', 'sequencing', 'proteomics', 'genomics',
                'metabolomics', 'immunohistochemistry', 'microscopy', 'spectroscopy'
            ]
        }
    
    def discover_wisteria_files(self) -> List[Path]:
        """
        Discover all Wisteria JSON files.
        
        Returns:
            List of Wisteria JSON file paths
        """
        # Look for files with 'hypotheses_' prefix
        wisteria_files = list(self.json_directory.glob("hypotheses_*.json"))
        logger.info(f"Discovered {len(wisteria_files)} Wisteria JSON files")
        
        return wisteria_files
    
    def load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load and parse a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Parsed JSON data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            logger.error(f"Failed to load {file_path.name}: {e}")
            return {}
    
    def classify_hypothesis_biomedical_relevance(self, hypothesis: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
        """
        Classify if a hypothesis is biomedically relevant.
        
        Args:
            hypothesis: Hypothesis data
            
        Returns:
            Tuple of (is_biomedical, confidence_score, matched_keywords)
        """
        title = hypothesis.get('title', '').lower()
        description = hypothesis.get('description', '').lower()
        text = f"{title} {description}"
        
        matched_keywords = []
        total_matches = 0
        
        # Check for biomedical keywords
        for category, keywords in self.biomedical_keywords.items():
            category_matches = []
            for keyword in keywords:
                if keyword in text:
                    category_matches.append(keyword)
                    total_matches += 1
            
            if category_matches:
                matched_keywords.extend([f"{category}:{kw}" for kw in category_matches])
        
        # Calculate confidence based on matches and text length
        text_length = len(text.split())
        confidence = min(1.0, total_matches / max(10, text_length * 0.1))
        
        # Determine if biomedical (threshold: at least 2 matches or confidence > 0.3)
        is_biomedical = total_matches >= 2 or confidence > 0.3
        
        return is_biomedical, confidence, matched_keywords
    
    def analyze_research_domain(self, metadata: Dict[str, Any], hypotheses: List[Dict[str, Any]]) -> str:
        """
        Analyze the overall research domain of the session.
        
        Args:
            metadata: Session metadata
            hypotheses: List of hypotheses
            
        Returns:
            Research domain classification
        """
        research_goal = metadata.get('research_goal', '').lower()
        
        # Domain classification based on research goal and hypothesis content
        if any(keyword in research_goal for keyword in ['neurodegenerative', 'alzheimer', 'parkinson', 'brain', 'neurological']):
            return 'neuroscience'
        elif any(keyword in research_goal for keyword in ['cancer', 'tumor', 'oncology', 'immunotherapy']):
            return 'oncology'
        elif any(keyword in research_goal for keyword in ['energy', 'battery', 'storage', 'renewable']):
            return 'energy_materials'
        elif any(keyword in research_goal for keyword in ['machine learning', 'ai', 'algorithm', 'data']):
            return 'computational'
        elif any(keyword in research_goal for keyword in ['drug', 'pharmaceutical', 'therapy', 'medicine']):
            return 'pharmacology'
        else:
            # Analyze hypotheses for domain clues
            biomedical_count = sum(1 for h in hypotheses if self.classify_hypothesis_biomedical_relevance(h)[0])
            if biomedical_count > len(hypotheses) * 0.5:
                return 'biomedical_general'
            else:
                return 'non_biomedical'
    
    def analyze_single_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a single Wisteria JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Analysis results for the file
        """
        logger.info(f"Analyzing file: {file_path.name}")
        
        # Load JSON data
        data = self.load_json_file(file_path)
        if not data:
            return {'file': file_path.name, 'status': 'failed', 'error': 'Failed to load JSON'}
        
        metadata = data.get('metadata', {})
        hypotheses = data.get('hypotheses', [])
        
        if not hypotheses:
            return {'file': file_path.name, 'status': 'no_hypotheses', 'error': 'No hypotheses found'}
        
        # Analyze research domain
        research_domain = self.analyze_research_domain(metadata, hypotheses)
        
        # Analyze each hypothesis
        hypothesis_analyses = []
        biomedical_count = 0
        
        for hypothesis in hypotheses:
            is_biomedical, confidence, keywords = self.classify_hypothesis_biomedical_relevance(hypothesis)
            
            analysis = {
                'hypothesis_number': hypothesis.get('hypothesis_number'),
                'title': hypothesis.get('title'),
                'is_biomedical': is_biomedical,
                'biomedical_confidence': confidence,
                'matched_keywords': keywords,
                'needs_biomni': is_biomedical
            }
            
            hypothesis_analyses.append(analysis)
            
            if is_biomedical:
                biomedical_count += 1
        
        # Determine if file needs Biomni validation
        needs_biomni = biomedical_count > 0
        biomni_priority = 'high' if biomedical_count == len(hypotheses) else 'medium' if biomedical_count > 0 else 'none'
        
        return {
            'file': file_path.name,
            'status': 'success',
            'metadata': {
                'research_goal': metadata.get('research_goal'),
                'timestamp': metadata.get('timestamp'),
                'model': metadata.get('model'),
                'session_type': metadata.get('session_type')
            },
            'research_domain': research_domain,
            'total_hypotheses': len(hypotheses),
            'biomedical_hypotheses': biomedical_count,
            'non_biomedical_hypotheses': len(hypotheses) - biomedical_count,
            'needs_biomni_validation': needs_biomni,
            'biomni_priority': biomni_priority,
            'hypothesis_analyses': hypothesis_analyses
        }
    
    def generate_validation_recommendations(self, analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate recommendations for Biomni validation.
        
        Args:
            analysis_results: Results from analyzing all files
            
        Returns:
            Validation recommendations
        """
        files_needing_biomni = [r for r in analysis_results if r.get('needs_biomni_validation', False)]
        high_priority_files = [r for r in files_needing_biomni if r.get('biomni_priority') == 'high']
        
        total_biomedical_hypotheses = sum(r.get('biomedical_hypotheses', 0) for r in analysis_results)
        
        recommendations = {
            'total_files_analyzed': len(analysis_results),
            'files_needing_biomni': len(files_needing_biomni),
            'high_priority_files': len(high_priority_files),
            'total_biomedical_hypotheses': total_biomedical_hypotheses,
            'recommended_actions': []
        }
        
        # Generate specific recommendations
        for result in high_priority_files:
            recommendations['recommended_actions'].append({
                'action': 'run_specialized_validation',
                'file': result['file'],
                'research_domain': result['research_domain'],
                'biomedical_hypotheses': result['biomedical_hypotheses'],
                'script_recommendation': self._get_script_recommendation(result['research_domain'])
            })
        
        return recommendations
    
    def _get_script_recommendation(self, research_domain: str) -> str:
        """Get script recommendation based on research domain."""
        domain_scripts = {
            'neuroscience': 'validate_neurodegeneration_hypotheses.py',
            'oncology': 'validate_cancer_hypotheses.py',
            'pharmacology': 'validate_drug_discovery_hypotheses.py',
            'biomedical_general': 'test_wisteria_json_biomni.py'
        }
        return domain_scripts.get(research_domain, 'test_wisteria_json_biomni.py')
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Run comprehensive analysis of all Wisteria files.
        
        Returns:
            Complete analysis results
        """
        print("🔍 Comprehensive Wisteria JSON Analysis for Biomni Validation")
        print("=" * 80)
        
        # Discover files
        wisteria_files = self.discover_wisteria_files()
        
        if not wisteria_files:
            print(f"\n📁 No Wisteria JSON files found in {self.json_directory}")
            return {'status': 'no_files', 'files_analyzed': 0}
        
        print(f"\n📁 Found {len(wisteria_files)} Wisteria JSON files:")
        for file_path in wisteria_files:
            print(f"   - {file_path.name}")
        
        # Analyze each file
        analysis_results = []
        
        for file_path in wisteria_files:
            try:
                result = self.analyze_single_file(file_path)
                analysis_results.append(result)
            except Exception as e:
                logger.error(f"Failed to analyze {file_path.name}: {e}")
                analysis_results.append({
                    'file': file_path.name,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Generate recommendations
        recommendations = self.generate_validation_recommendations(analysis_results)
        
        # Display results
        self._display_analysis_results(analysis_results, recommendations)
        
        return {
            'analysis_results': analysis_results,
            'recommendations': recommendations,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _display_analysis_results(self, results: List[Dict[str, Any]], recommendations: Dict[str, Any]):
        """Display comprehensive analysis results."""
        print(f"\n🎯 Analysis Summary:")
        print("=" * 80)
        print(f"Files analyzed: {recommendations['total_files_analyzed']}")
        print(f"Files needing Biomni validation: {recommendations['files_needing_biomni']}")
        print(f"High priority files: {recommendations['high_priority_files']}")
        print(f"Total biomedical hypotheses: {recommendations['total_biomedical_hypotheses']}")
        
        print(f"\n📊 Detailed File Analysis:")
        print("=" * 80)
        
        for result in results:
            print(f"\n📄 File: {result['file']}")
            print(f"   Status: {result['status']}")
            
            if result['status'] == 'success':
                print(f"   Research Domain: {result['research_domain']}")
                print(f"   Research Goal: {result['metadata']['research_goal'][:60]}...")
                print(f"   Total Hypotheses: {result['total_hypotheses']}")
                print(f"   Biomedical Hypotheses: {result['biomedical_hypotheses']}")
                print(f"   Needs Biomni: {result['needs_biomni_validation']}")
                print(f"   Priority: {result['biomni_priority']}")
                
                if result['needs_biomni_validation']:
                    print(f"   🧬 BIOMNI VALIDATION REQUIRED")
                    
                    # Show biomedical hypotheses
                    biomedical_hyps = [h for h in result['hypothesis_analyses'] if h['is_biomedical']]
                    for hyp in biomedical_hyps[:3]:  # Show first 3
                        print(f"      • H{hyp['hypothesis_number']}: {hyp['title'][:50]}...")
                        print(f"        Keywords: {', '.join(hyp['matched_keywords'][:3])}")
                    
                    if len(biomedical_hyps) > 3:
                        print(f"      ... and {len(biomedical_hyps) - 3} more biomedical hypotheses")
                else:
                    print(f"   ✅ No Biomni validation needed (non-biomedical)")
                    
            elif result['status'] == 'error':
                print(f"   Error: {result['error']}")
        
        print(f"\n🚀 Recommended Actions:")
        print("=" * 40)
        
        if recommendations['recommended_actions']:
            for i, action in enumerate(recommendations['recommended_actions'], 1):
                print(f"\n{i}. File: {action['file']}")
                print(f"   Domain: {action['research_domain']}")
                print(f"   Biomedical Hypotheses: {action['biomedical_hypotheses']}")
                print(f"   Recommended Script: {action['script_recommendation']}")
                print(f"   Command: python {action['script_recommendation']}")
        else:
            print("\n✅ No Biomni validation needed for any files")
            print("   All hypotheses are non-biomedical (energy, materials, computational)")
        
        print(f"\n📋 Next Steps:")
        print("1. Review the biomedical hypotheses identified above")
        print("2. Run the recommended validation scripts")
        print("3. Analyze the Biomni validation results")
        print("4. Use insights for research planning and experimental design")


def main():
    """Main function to run the comprehensive analysis."""
    print("🔍 Wisteria JSON Analysis for Biomni Validation Needs")
    print("=" * 80)
    print("This tool analyzes all Wisteria JSON files to determine which")
    print("hypotheses require biomedical validation using Biomni.")
    print("=" * 80)
    
    # Create analyzer
    analyzer = WisteriaBiomniAnalyzer()
    
    # Run analysis
    results = analyzer.run_comprehensive_analysis()
    
    # Save results to file
    results_file = Path("wisteria_biomni_analysis_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed analysis saved to: {results_file}")
    print("You can review the complete analysis and recommendations in this file.")
    
    return results


if __name__ == "__main__":
    main()

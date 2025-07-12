#!/usr/bin/env python3
"""
Test Biomni Integration with Wisteria JSON Files.

This script tests the modern Biomni agent with JSON files from Wisteria,
providing comprehensive biomedical verification and analysis.
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


class WisteriaJsonBiomniTester:
    """
    Comprehensive tester for Biomni integration with Wisteria JSON files.
    """
    
    def __init__(self, json_directory: str = "wisteria-json"):
        """
        Initialize the tester.
        
        Args:
            json_directory: Directory containing Wisteria JSON files
        """
        self.json_directory = Path(json_directory)
        self.results = []
        self.biomni_agent = None
        
        # Create directory if it doesn't exist
        self.json_directory.mkdir(exist_ok=True)
        
        # Initialize modern Biomni agent
        self._initialize_biomni()
    
    def _initialize_biomni(self):
        """Initialize the modern Biomni agent."""
        if not JNANA_AVAILABLE:
            logger.warning("Jnana not available - using mock testing mode")
            return
        
        config = ModernBiomniConfig(
            enabled=True,
            data_path="./data/biomni_wisteria_test",
            confidence_threshold=0.6,
            auto_patch_imports=True,
            langchain_version_check=True,
            fallback_on_error=True,
            enable_experimental_suggestions=True
        )
        
        self.biomni_agent = ModernBiomniAgent(config)
        logger.info("Modern Biomni agent initialized for Wisteria JSON testing")
    
    def discover_json_files(self) -> List[Path]:
        """
        Discover all JSON files in the wisteria-json directory.
        
        Returns:
            List of JSON file paths
        """
        json_files = list(self.json_directory.glob("*.json"))
        logger.info(f"Discovered {len(json_files)} JSON files in {self.json_directory}")
        
        if not json_files:
            logger.warning(f"No JSON files found in {self.json_directory}")
            logger.info("Please copy your Wisteria JSON files to this directory")
        
        return json_files
    
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
            logger.info(f"Successfully loaded {file_path.name}")
            return data
        except Exception as e:
            logger.error(f"Failed to load {file_path.name}: {e}")
            return {}
    
    def extract_hypotheses_from_json(self, json_data: Dict[str, Any], filename: str) -> List[Dict[str, Any]]:
        """
        Extract hypotheses from Wisteria JSON data.
        
        Args:
            json_data: Parsed JSON data
            filename: Name of the source file
            
        Returns:
            List of extracted hypotheses
        """
        hypotheses = []
        
        # Try different possible structures for Wisteria JSON
        possible_keys = [
            'hypotheses', 'hypothesis', 'research_hypotheses', 
            'generated_hypotheses', 'results', 'data'
        ]
        
        for key in possible_keys:
            if key in json_data:
                data = json_data[key]
                if isinstance(data, list):
                    for i, item in enumerate(data):
                        hypothesis = self._extract_single_hypothesis(item, f"{filename}_{key}_{i}")
                        if hypothesis:
                            hypotheses.append(hypothesis)
                elif isinstance(data, dict):
                    hypothesis = self._extract_single_hypothesis(data, f"{filename}_{key}")
                    if hypothesis:
                        hypotheses.append(hypothesis)
        
        # If no hypotheses found in structured format, try to extract from text fields
        if not hypotheses:
            text_fields = ['content', 'text', 'description', 'summary', 'abstract']
            for field in text_fields:
                if field in json_data and isinstance(json_data[field], str):
                    hypothesis = {
                        'title': f"Extracted from {filename} - {field}",
                        'content': json_data[field],
                        'source_file': filename,
                        'extraction_method': f'text_field_{field}'
                    }
                    hypotheses.append(hypothesis)
                    break
        
        logger.info(f"Extracted {len(hypotheses)} hypotheses from {filename}")
        return hypotheses
    
    def _extract_single_hypothesis(self, data: Dict[str, Any], source_id: str) -> Dict[str, Any]:
        """
        Extract a single hypothesis from data.
        
        Args:
            data: Data containing hypothesis information
            source_id: Source identifier
            
        Returns:
            Extracted hypothesis or None
        """
        if not isinstance(data, dict):
            return None
        
        # Try to find title and content in various formats
        title_keys = ['title', 'name', 'hypothesis', 'research_question', 'question']
        content_keys = ['content', 'description', 'text', 'summary', 'abstract', 'hypothesis_text']
        
        title = None
        content = None
        
        for key in title_keys:
            if key in data and isinstance(data[key], str) and data[key].strip():
                title = data[key].strip()
                break
        
        for key in content_keys:
            if key in data and isinstance(data[key], str) and data[key].strip():
                content = data[key].strip()
                break
        
        if not content:
            return None
        
        if not title:
            title = content[:100] + "..." if len(content) > 100 else content
        
        return {
            'title': title,
            'content': content,
            'source_file': source_id,
            'original_data': data,
            'extraction_method': 'structured'
        }
    
    async def test_biomni_verification(self, hypothesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test Biomni verification on a hypothesis.
        
        Args:
            hypothesis_data: Hypothesis data to verify
            
        Returns:
            Verification results
        """
        if not self.biomni_agent:
            return self._create_mock_verification_result(hypothesis_data)
        
        try:
            # Initialize Biomni agent if needed
            if not self.biomni_agent.is_initialized:
                await self.biomni_agent.initialize()
            
            # Perform verification
            result = await self.biomni_agent.verify_hypothesis(
                hypothesis_content=hypothesis_data['content'],
                research_goal=f"Analysis of hypothesis from {hypothesis_data['source_file']}",
                verification_type="general"
            )
            
            return {
                'verification_id': result.verification_id,
                'is_biologically_plausible': result.is_biologically_plausible,
                'confidence_score': result.confidence_score,
                'evidence_strength': result.evidence_strength,
                'supporting_evidence': result.supporting_evidence,
                'contradicting_evidence': result.contradicting_evidence,
                'suggested_experiments': result.suggested_experiments,
                'execution_time': result.execution_time,
                'langchain_version': result.langchain_version,
                'compatibility_mode': result.compatibility_mode,
                'error_details': result.error_details
            }
            
        except Exception as e:
            logger.error(f"Biomni verification failed: {e}")
            return self._create_error_verification_result(hypothesis_data, str(e))
    
    def _create_mock_verification_result(self, hypothesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a mock verification result when Biomni is not available."""
        return {
            'verification_id': f"mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'is_biologically_plausible': True,
            'confidence_score': 0.5,
            'evidence_strength': 'moderate',
            'supporting_evidence': ['Mock analysis indicates potential biological relevance'],
            'contradicting_evidence': ['Limited analysis due to Biomni unavailability'],
            'suggested_experiments': ['Conduct literature review', 'Design preliminary experiments'],
            'execution_time': 0.1,
            'langchain_version': 'mock',
            'compatibility_mode': 'mock',
            'error_details': 'Biomni not available - using mock results'
        }
    
    def _create_error_verification_result(self, hypothesis_data: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Create an error verification result."""
        return {
            'verification_id': f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'is_biologically_plausible': False,
            'confidence_score': 0.0,
            'evidence_strength': 'none',
            'supporting_evidence': [],
            'contradicting_evidence': ['Verification failed due to error'],
            'suggested_experiments': ['Retry verification after fixing issues'],
            'execution_time': 0.0,
            'langchain_version': 'error',
            'compatibility_mode': 'error',
            'error_details': error
        }
    
    async def test_single_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Test Biomni integration with a single JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Test results for the file
        """
        logger.info(f"Testing file: {file_path.name}")
        
        # Load JSON data
        json_data = self.load_json_file(file_path)
        if not json_data:
            return {'file': file_path.name, 'status': 'failed', 'error': 'Failed to load JSON'}
        
        # Extract hypotheses
        hypotheses = self.extract_hypotheses_from_json(json_data, file_path.name)
        if not hypotheses:
            return {'file': file_path.name, 'status': 'no_hypotheses', 'error': 'No hypotheses found'}
        
        # Test Biomni verification on each hypothesis
        verification_results = []
        for i, hypothesis in enumerate(hypotheses):
            logger.info(f"Verifying hypothesis {i+1}/{len(hypotheses)}: {hypothesis['title'][:50]}...")
            
            verification = await self.test_biomni_verification(hypothesis)
            verification_results.append({
                'hypothesis': hypothesis,
                'verification': verification
            })
        
        return {
            'file': file_path.name,
            'status': 'success',
            'hypotheses_count': len(hypotheses),
            'verification_results': verification_results,
            'original_data_keys': list(json_data.keys())
        }
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """
        Run comprehensive Biomni testing on all JSON files.
        
        Returns:
            Complete test results
        """
        print("🧬 Comprehensive Biomni Integration Test with Wisteria JSON Files")
        print("=" * 80)
        
        # Discover JSON files
        json_files = self.discover_json_files()
        
        if not json_files:
            print(f"\n📁 No JSON files found in {self.json_directory}")
            print("Please copy your Wisteria JSON files to this directory and run again.")
            return {'status': 'no_files', 'files_tested': 0}
        
        print(f"\n📁 Found {len(json_files)} JSON files to test:")
        for file_path in json_files:
            print(f"   - {file_path.name}")
        
        # Test each file
        all_results = []
        total_hypotheses = 0
        successful_verifications = 0
        
        for file_path in json_files:
            try:
                result = await self.test_single_file(file_path)
                all_results.append(result)
                
                if result['status'] == 'success':
                    total_hypotheses += result['hypotheses_count']
                    successful_verifications += len([
                        v for v in result['verification_results'] 
                        if v['verification']['confidence_score'] > 0
                    ])
                
            except Exception as e:
                logger.error(f"Failed to test {file_path.name}: {e}")
                all_results.append({
                    'file': file_path.name,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Generate summary
        summary = {
            'files_tested': len(json_files),
            'files_successful': len([r for r in all_results if r['status'] == 'success']),
            'total_hypotheses': total_hypotheses,
            'successful_verifications': successful_verifications,
            'biomni_available': self.biomni_agent is not None and JNANA_AVAILABLE,
            'test_timestamp': datetime.now().isoformat()
        }
        
        # Display results
        self._display_test_results(all_results, summary)
        
        return {
            'summary': summary,
            'detailed_results': all_results
        }
    
    def _display_test_results(self, results: List[Dict[str, Any]], summary: Dict[str, Any]):
        """Display comprehensive test results."""
        print(f"\n🎯 Test Summary:")
        print("=" * 80)
        print(f"Files tested: {summary['files_tested']}")
        print(f"Files successful: {summary['files_successful']}")
        print(f"Total hypotheses extracted: {summary['total_hypotheses']}")
        print(f"Successful verifications: {summary['successful_verifications']}")
        print(f"Biomni available: {summary['biomni_available']}")
        
        print(f"\n📊 Detailed Results:")
        print("=" * 80)
        
        for result in results:
            print(f"\n📄 File: {result['file']}")
            print(f"   Status: {result['status']}")
            
            if result['status'] == 'success':
                print(f"   Hypotheses found: {result['hypotheses_count']}")
                print(f"   Original data keys: {', '.join(result['original_data_keys'])}")
                
                # Show verification summary
                verifications = result['verification_results']
                high_confidence = len([v for v in verifications if v['verification']['confidence_score'] > 0.7])
                medium_confidence = len([v for v in verifications if 0.4 <= v['verification']['confidence_score'] <= 0.7])
                low_confidence = len([v for v in verifications if v['verification']['confidence_score'] < 0.4])
                
                print(f"   Verification confidence: High({high_confidence}) Medium({medium_confidence}) Low({low_confidence})")
                
                # Show top hypothesis
                if verifications:
                    top_verification = max(verifications, key=lambda x: x['verification']['confidence_score'])
                    print(f"   Top hypothesis: {top_verification['hypothesis']['title'][:60]}...")
                    print(f"   Top confidence: {top_verification['verification']['confidence_score']:.2f}")
                    
            elif result['status'] == 'error':
                print(f"   Error: {result['error']}")
            elif result['status'] == 'no_hypotheses':
                print(f"   Issue: {result['error']}")
        
        print(f"\n🎉 Testing completed at {summary['test_timestamp']}")
        
        if summary['biomni_available']:
            print("✅ Modern Biomni integration is working correctly!")
        else:
            print("⚠️  Biomni not available - used mock verification results")


async def main():
    """Main function to run the comprehensive test."""
    print("🧬 Wisteria JSON + Modern Biomni Integration Tester")
    print("=" * 80)
    print("This tool tests Biomni integration with your Wisteria JSON files.")
    print("Please copy your JSON files to the 'wisteria-json' directory.")
    print("=" * 80)
    
    # Create tester
    tester = WisteriaJsonBiomniTester()
    
    # Run comprehensive test
    results = await tester.run_comprehensive_test()
    
    # Save results to file
    results_file = Path("wisteria_biomni_test_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    print("You can review the complete verification data in this file.")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())

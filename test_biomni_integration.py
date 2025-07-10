#!/usr/bin/env python3
"""
Test Biomni integration with Jnana system.

This script tests the integration of Stanford's Biomni biomedical AI agent
with Jnana for hypothesis verification.
"""

import asyncio
import logging
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent))

from jnana import JnanaSystem
from jnana.agents.biomni_agent import BiomniAgent, BiomniConfig
from jnana.data.unified_hypothesis import UnifiedHypothesis

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_biomni_agent_initialization():
    """Test Biomni agent initialization."""
    print("\n🧬 Testing Biomni Agent Initialization")
    print("=" * 50)
    
    config = BiomniConfig(
        enabled=True,
        data_path="./data/biomni_test",
        confidence_threshold=0.6
    )
    
    agent = BiomniAgent(config)
    
    # Test initialization
    success = await agent.initialize()
    
    if success:
        print("✅ Biomni agent initialized successfully")
    else:
        print("⚠️  Biomni agent initialization failed (this is expected if Biomni is not installed)")
    
    return agent


async def test_biomedical_detection():
    """Test biomedical hypothesis detection."""
    print("\n🔍 Testing Biomedical Hypothesis Detection")
    print("=" * 50)
    
    config = BiomniConfig(enabled=True)
    agent = BiomniAgent(config)
    
    test_cases = [
        {
            "hypothesis": "CRISPR-Cas9 gene editing can be used to treat sickle cell disease by correcting the mutation in the HBB gene",
            "research_goal": "Develop gene therapies for genetic diseases",
            "expected": True,
            "description": "Genomics hypothesis"
        },
        {
            "hypothesis": "A novel small molecule inhibitor targeting the PD-1/PD-L1 pathway could enhance T-cell activation in cancer immunotherapy",
            "research_goal": "Improve cancer treatment outcomes",
            "expected": True,
            "description": "Drug discovery hypothesis"
        },
        {
            "hypothesis": "Machine learning algorithms can improve weather prediction accuracy by 15%",
            "research_goal": "Enhance meteorological forecasting",
            "expected": False,
            "description": "Non-biomedical hypothesis"
        },
        {
            "hypothesis": "Protein folding dynamics of amyloid-beta aggregates contribute to Alzheimer's disease pathogenesis",
            "research_goal": "Understand neurodegenerative diseases",
            "expected": True,
            "description": "Protein biology hypothesis"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        is_biomedical = agent.is_biomedical_hypothesis(case["hypothesis"], case["research_goal"])
        status = "✅" if is_biomedical == case["expected"] else "❌"
        
        print(f"{status} Test {i}: {case['description']}")
        print(f"   Hypothesis: {case['hypothesis'][:80]}...")
        print(f"   Detected as biomedical: {is_biomedical} (expected: {case['expected']})")
        print()


async def test_biomni_verification_fallback():
    """Test Biomni verification with fallback when Biomni is not available."""
    print("\n🧪 Testing Biomni Verification (Fallback Mode)")
    print("=" * 50)
    
    config = BiomniConfig(enabled=True)
    agent = BiomniAgent(config)
    
    hypothesis = "CRISPR-Cas9 can be used to edit the CFTR gene to treat cystic fibrosis"
    research_goal = "Develop gene therapies for cystic fibrosis"
    
    try:
        result = await agent.verify_hypothesis(hypothesis, research_goal, "genomics")
        
        print(f"✅ Verification completed")
        print(f"   Verification ID: {result.verification_id}")
        print(f"   Verification Type: {result.verification_type}")
        print(f"   Biologically Plausible: {result.is_biologically_plausible}")
        print(f"   Confidence Score: {result.confidence_score}")
        print(f"   Evidence Strength: {result.evidence_strength}")
        print(f"   Execution Time: {result.execution_time:.2f}s")
        
        if result.biomni_response:
            print(f"   Response Length: {len(result.biomni_response)} characters")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")


async def test_jnana_biomni_integration():
    """Test full Jnana-Biomni integration."""
    print("\n🔬 Testing Jnana-Biomni Integration")
    print("=" * 50)
    
    try:
        # Initialize Jnana with Biomni integration
        jnana = JnanaSystem(
            config_path="config/models.yaml",
            storage_path="test_biomni_integration.json",
            storage_type="json",
            enable_ui=False
        )
        
        await jnana.start()
        print("✅ Jnana system started")
        
        # Set a biomedical research goal
        research_goal = "How can we use CRISPR technology to treat genetic diseases more effectively?"
        session_id = await jnana.set_research_goal(research_goal)
        print(f"✅ Research session created: {session_id[:8]}...")
        
        # Generate a biomedical hypothesis
        print("\n🧬 Generating biomedical hypothesis...")
        hypothesis = await jnana.generate_single_hypothesis("literature_exploration")
        
        print(f"✅ Generated hypothesis: {hypothesis.title}")
        print(f"   Content: {hypothesis.content[:100]}...")
        print(f"   Is biomedical: {hypothesis.is_biomedical}")
        
        # Check if Biomni verification was applied
        if hypothesis.is_biomni_verified():
            biomni_summary = hypothesis.get_biomni_summary()
            print(f"✅ Biomni verification applied:")
            print(f"   Biologically plausible: {biomni_summary['biologically_plausible']}")
            print(f"   Confidence: {biomni_summary['confidence_score']:.2f}")
            print(f"   Evidence strength: {biomni_summary['evidence_strength']}")
        else:
            print("⚠️  No Biomni verification applied (Biomni may not be available)")
        
        # Test batch mode with biomedical hypotheses
        print("\n🔬 Testing batch mode with biomedical focus...")
        await jnana.run_batch_mode(
            hypothesis_count=3,
            strategies=["literature_exploration", "scientific_debate"]
        )
        
        print("✅ Batch mode completed")
        
        # Get system status
        status = jnana.get_system_status()
        print(f"\n📊 System Status:")
        print(f"   Biomni available: {status.get('biomni_available', 'Unknown')}")
        print(f"   Session hypotheses: {status['session']['hypotheses_count'] if status['session'] else 0}")
        
        await jnana.stop()
        print("✅ Jnana system stopped")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_hypothesis_biomni_methods():
    """Test UnifiedHypothesis Biomni-related methods."""
    print("\n🧪 Testing UnifiedHypothesis Biomni Methods")
    print("=" * 50)
    
    from jnana.agents.biomni_agent import BiomniVerificationResult
    
    # Create a test hypothesis
    hypothesis = UnifiedHypothesis(
        title="Test CRISPR Hypothesis",
        content="CRISPR-Cas9 can be used to correct genetic mutations in sickle cell disease",
        description="A hypothesis about using CRISPR for genetic disease treatment"
    )
    
    print(f"✅ Created test hypothesis: {hypothesis.title}")
    print(f"   Initially biomedical: {hypothesis.is_biomedical}")
    print(f"   Initially verified: {hypothesis.is_biomni_verified()}")
    
    # Create mock verification result
    verification = BiomniVerificationResult(
        verification_id="test_verification_001",
        hypothesis_id=hypothesis.hypothesis_id,
        verification_type="genomics",
        is_biologically_plausible=True,
        confidence_score=0.85,
        evidence_strength="strong",
        supporting_evidence=["CRISPR has been successfully used in clinical trials", "Sickle cell disease is caused by a single gene mutation"],
        suggested_experiments=["Conduct in vitro CRISPR editing experiments", "Test in mouse models"]
    )
    
    # Set verification results
    hypothesis.set_biomni_verification(verification)
    
    print(f"✅ Added Biomni verification")
    print(f"   Now biomedical: {hypothesis.is_biomedical}")
    print(f"   Now verified: {hypothesis.is_biomni_verified()}")
    print(f"   Confidence: {hypothesis.get_biomedical_confidence()}")
    
    # Test summary
    summary = hypothesis.get_biomni_summary()
    print(f"✅ Biomni summary:")
    for key, value in summary.items():
        print(f"   {key}: {value}")


async def main():
    """Run all Biomni integration tests."""
    print("🧬 Biomni-Jnana Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Biomni Agent Initialization", test_biomni_agent_initialization),
        ("Biomedical Detection", test_biomedical_detection),
        ("Biomni Verification Fallback", test_biomni_verification_fallback),
        ("UnifiedHypothesis Biomni Methods", test_hypothesis_biomni_methods),
        ("Full Jnana-Biomni Integration", test_jnana_biomni_integration)
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running: {test_name}")
            await test_func()
            print(f"✅ {test_name} completed")
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "-" * 60)
    
    print("\n🎉 Biomni integration test suite completed!")
    print("\nNote: Some tests may show warnings if Biomni is not installed.")
    print("To install Biomni: pip install biomni")


if __name__ == "__main__":
    asyncio.run(main())

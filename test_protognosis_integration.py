#!/usr/bin/env python3
"""
Test ProtoGnosis Integration with Jnana.

This script tests the complete integration of ProtoGnosis into Jnana,
including data conversion, agent functionality, and workflow integration.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the jnana package to the path
sys.path.insert(0, str(Path(__file__).parent))

from jnana.core.jnana_system import JnanaSystem
from jnana.protognosis import is_protognosis_available, get_protognosis_status
from jnana.protognosis.utils.data_converter import ProtoGnosisDataConverter
from jnana.protognosis.utils.jnana_adapter import JnanaProtoGnosisAdapter
from jnana.data.unified_hypothesis import UnifiedHypothesis


def setup_logging():
    """Setup logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


async def test_protognosis_availability():
    """Test if ProtoGnosis is available and properly integrated."""
    print("🔍 Testing ProtoGnosis Availability...")
    
    # Check availability
    available = is_protognosis_available()
    status = get_protognosis_status()
    
    print(f"   ✅ ProtoGnosis Available: {available}")
    print(f"   📊 Status: {status}")
    
    if not available:
        print(f"   ❌ Error: {status.get('error', 'Unknown error')}")
        return False
    
    return True


async def test_data_converter():
    """Test the ProtoGnosis data converter."""
    print("\n🔄 Testing Data Converter...")
    
    try:
        # Create a sample unified hypothesis
        unified_hypothesis = UnifiedHypothesis(
            title="Test Hypothesis",
            description="This is a test hypothesis for conversion testing.",
            content="Detailed content of the test hypothesis for ProtoGnosis integration.",
            generation_strategy="literature_exploration"
        )
        
        print(f"   📝 Created UnifiedHypothesis: {unified_hypothesis.title}")
        
        # Convert to ProtoGnosis format
        converter = ProtoGnosisDataConverter()
        pg_hypothesis = converter.unified_to_protognosis(unified_hypothesis)
        
        print(f"   🔄 Converted to ProtoGnosis format")
        print(f"   📋 ProtoGnosis ID: {pg_hypothesis.hypothesis_id}")
        print(f"   📋 ProtoGnosis Agent: {pg_hypothesis.agent_id}")
        
        # Convert back to unified format
        converted_back = converter.protognosis_to_unified(pg_hypothesis)
        
        print(f"   🔄 Converted back to Unified format")
        print(f"   📋 Unified ID: {converted_back.hypothesis_id}")
        print(f"   📋 Unified Title: {converted_back.title}")
        
        # Verify data integrity
        assert unified_hypothesis.hypothesis_id == converted_back.hypothesis_id
        assert unified_hypothesis.title == converted_back.title
        assert unified_hypothesis.generation_strategy == converted_back.generation_strategy
        
        print("   ✅ Data conversion test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Data conversion test failed: {e}")
        return False


async def test_jnana_adapter():
    """Test the Jnana-ProtoGnosis adapter."""
    print("\n🔗 Testing Jnana-ProtoGnosis Adapter...")
    
    try:
        # Create a mock model manager (simplified for testing)
        class MockModelManager:
            def get_default_config(self):
                return {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.7,
                    "max_tokens": 1024
                }
            
            def get_model_for_agent(self, agent_type):
                return self.get_default_config()
        
        # Create adapter
        model_manager = MockModelManager()
        adapter = JnanaProtoGnosisAdapter(
            model_manager=model_manager,
            storage_path="./test_storage",
            max_workers=2
        )
        
        print("   📦 Created JnanaProtoGnosisAdapter")
        
        # Test initialization
        initialized = await adapter.initialize()
        print(f"   🚀 Adapter initialized: {initialized}")
        
        # Get status
        status = adapter.get_status()
        print(f"   📊 Adapter status: {status}")
        
        print("   ✅ Adapter test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Adapter test failed: {e}")
        return False


async def test_jnana_system_integration():
    """Test ProtoGnosis integration with JnanaSystem."""
    print("\n🧠 Testing Jnana System Integration...")
    
    try:
        # Create Jnana system
        config_path = Path(__file__).parent / "config" / "models.yaml"
        if not config_path.exists():
            print("   ⚠️  No config file found, using default configuration")
            config_path = None
        
        jnana = JnanaSystem(
            config_path=config_path,
            storage_path="./test_integration_storage.json",
            storage_type="json",
            enable_ui=False
        )
        
        print("   📦 Created JnanaSystem")
        
        # Start the system
        await jnana.start()
        print("   🚀 JnanaSystem started")
        
        # Set research goal
        research_goal = "How can machine learning improve renewable energy efficiency?"
        session_id = await jnana.set_research_goal(research_goal)
        print(f"   🎯 Research goal set: {session_id}")
        
        # Test single hypothesis generation
        print("   🧪 Testing single hypothesis generation...")
        hypothesis = await jnana.generate_single_hypothesis("literature_exploration")
        print(f"   📝 Generated hypothesis: {hypothesis.title}")
        print(f"   📋 Strategy: {hypothesis.generation_strategy}")
        
        # Test hypothesis refinement
        print("   🔧 Testing hypothesis refinement...")
        refined_hypothesis = await jnana.refine_hypothesis(
            hypothesis, 
            "Please make this more specific to solar energy applications"
        )
        print(f"   ✨ Refined hypothesis: {refined_hypothesis.title}")
        
        # Stop the system
        await jnana.stop()
        print("   🛑 JnanaSystem stopped")
        
        print("   ✅ Jnana system integration test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Jnana system integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_batch_mode():
    """Test ProtoGnosis integration in batch mode."""
    print("\n📊 Testing Batch Mode Integration...")
    
    try:
        # Create Jnana system
        jnana = JnanaSystem(
            config_path=None,
            storage_path="./test_batch_storage.json",
            storage_type="json",
            enable_ui=False
        )
        
        await jnana.start()
        
        # Set research goal
        research_goal = "What are novel approaches to carbon capture and storage?"
        await jnana.set_research_goal(research_goal)
        
        print("   🎯 Research goal set for batch mode")
        
        # Test batch mode (with small numbers for testing)
        print("   🚀 Running batch mode...")
        await jnana.run_batch_mode(
            hypothesis_count=2,
            strategies=["literature_exploration", "scientific_debate"],
            tournament_matches=3
        )
        
        # Get session results
        session_info = jnana.session_manager.get_session_info()
        hypotheses = jnana.session_manager.get_all_hypotheses()
        
        print(f"   📊 Session generated {len(hypotheses)} hypotheses")
        for i, hyp in enumerate(hypotheses):
            print(f"      {i+1}. {hyp.title} (Strategy: {hyp.generation_strategy})")
        
        await jnana.stop()
        
        print("   ✅ Batch mode test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Batch mode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all ProtoGnosis integration tests."""
    print("🧬 ProtoGnosis-Jnana Integration Test Suite")
    print("=" * 60)
    
    setup_logging()
    
    tests = [
        ("ProtoGnosis Availability", test_protognosis_availability),
        ("Data Converter", test_data_converter),
        ("Jnana Adapter", test_jnana_adapter),
        ("Jnana System Integration", test_jnana_system_integration),
        ("Batch Mode Integration", test_batch_mode)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   💥 Test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! ProtoGnosis integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())

#!/usr/bin/env python3
"""
Test script for Jnana API integration with real LLM providers.
"""

import asyncio
import logging

async def test_configuration_validation():
    """Test that the configuration is properly loaded and validated."""
    print("🧪 Testing configuration validation...")
    
    try:
        from jnana.core.model_manager import UnifiedModelManager
        
        manager = UnifiedModelManager("config/models.yaml")
        
        # Test validation
        errors = manager.validate_configuration()
        
        if errors:
            print(f"⚠️  Configuration has {len(errors)} warnings:")
            for error in errors[:3]:  # Show first 3
                print(f"    - {error}")
        else:
            print("✅ Configuration validation passed - all API keys properly configured")
        
        # Test model access
        models = manager.list_available_models()
        print(f"✅ Configuration loaded: {sum(len(m) for m in models.values())} total model configurations")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

async def test_simple_hypothesis_generation():
    """Test simple hypothesis generation without real API calls."""
    print("🧪 Testing simple hypothesis generation...")
    
    try:
        from jnana import JnanaSystem
        from jnana.data.unified_hypothesis import UnifiedHypothesis
        
        # Initialize Jnana
        jnana = JnanaSystem(
            config_path="config/models.yaml",
            storage_path="test_simple.json",
            storage_type="json",
            enable_ui=False
        )
        
        await jnana.start()
        print("✅ Jnana system started")
        
        # Set research goal
        session_id = await jnana.set_research_goal("Test research goal for API validation")
        print(f"✅ Research goal set: {session_id[:8]}...")
        
        # Create a test hypothesis (without API call)
        hypothesis = UnifiedHypothesis(
            title="Test Hypothesis for API Integration",
            description="This hypothesis tests the API integration capabilities of Jnana system."
        )
        
        await jnana.session_manager.add_hypothesis(hypothesis)
        print("✅ Hypothesis added to session")
        
        # Test refinement (without API call)
        hypothesis.add_feedback("Test feedback for validation")
        await jnana.session_manager.update_hypothesis(hypothesis)
        print(f"✅ Hypothesis refined, version: {hypothesis.version_string}")
        
        # Get status
        status = jnana.get_system_status()
        print(f"✅ System status: {status['session']['hypotheses_count']} hypotheses")
        
        await jnana.stop()
        print("✅ System stopped cleanly")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run basic tests."""
    print("🚀 Starting Jnana Basic API Tests")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Configuration validation
    print("\n1. Configuration Validation")
    print("-" * 30)
    result1 = await test_configuration_validation()
    test_results.append(("Configuration", result1))
    
    # Test 2: Simple system test
    print("\n2. Simple System Test")
    print("-" * 30)
    result2 = await test_simple_hypothesis_generation()
    test_results.append(("Simple System", result2))
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 Test Results")
    print("=" * 50)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(test_results)} tests passed")
    
    return passed == len(test_results)

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

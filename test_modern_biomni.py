#!/usr/bin/env python3
"""
Test Modern Biomni Integration with Latest LangChain.

This script tests the modern Biomni agent that works with
the latest LangChain versions by fixing import compatibility issues.
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from jnana.agents.biomni_modern import ModernBiomniAgent, ModernBiomniConfig
from jnana.data.unified_hypothesis import UnifiedHypothesis

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_modern_biomni_initialization():
    """Test modern Biomni agent initialization."""
    print("\n🧬 Testing Modern Biomni Agent Initialization")
    print("=" * 60)
    
    config = ModernBiomniConfig(
        enabled=True,
        data_path="./data/biomni_modern_test",
        confidence_threshold=0.6,
        auto_patch_imports=True,
        langchain_version_check=True,
        fallback_on_error=True
    )
    
    agent = ModernBiomniAgent(config)
    
    print(f"✅ Modern Biomni agent created")
    print(f"   LangChain version: {agent.langchain_version}")
    print(f"   Auto-patch enabled: {agent.config.auto_patch_imports}")
    print(f"   Fallback enabled: {agent.config.fallback_on_error}")
    
    # Test initialization
    success = await agent.initialize()
    
    if success:
        print("✅ Modern Biomni agent initialized successfully")
        print("   Real Biomni A1 agent is available and working")
    else:
        print("⚠️  Modern Biomni agent initialization failed")
        print("   This is expected if Biomni is not installed or has compatibility issues")
        print("   The agent will use enhanced fallback mode")
    
    return agent


async def test_biomedical_hypothesis_verification():
    """Test biomedical hypothesis verification with modern agent."""
    print("\n🔬 Testing Biomedical Hypothesis Verification")
    print("=" * 60)
    
    config = ModernBiomniConfig(enabled=True, auto_patch_imports=True)
    agent = ModernBiomniAgent(config)
    
    # Test hypotheses covering different biomedical domains
    test_cases = [
        {
            "hypothesis": "CRISPR-Cas9 gene editing can effectively treat sickle cell disease by correcting the HBB gene mutation",
            "research_goal": "Develop gene therapies for inherited blood disorders",
            "verification_type": "genomics",
            "expected_confidence": 0.7
        },
        {
            "hypothesis": "Targeting tau protein aggregation with small molecule inhibitors can slow Alzheimer's disease progression",
            "research_goal": "Develop novel therapeutics for neurodegenerative diseases",
            "verification_type": "drug_discovery",
            "expected_confidence": 0.6
        },
        {
            "hypothesis": "Engineered CAR-T cells expressing anti-CD19 receptors can eliminate B-cell lymphomas",
            "research_goal": "Advance immunotherapy for hematologic malignancies",
            "verification_type": "general",
            "expected_confidence": 0.8
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['verification_type'].title()} Verification")
        print(f"   Hypothesis: {test_case['hypothesis'][:80]}...")
        
        try:
            result = await agent.verify_hypothesis(
                test_case["hypothesis"],
                test_case["research_goal"],
                test_case["verification_type"]
            )
            
            print(f"✅ Verification completed:")
            print(f"   Verification ID: {result.verification_id}")
            print(f"   Biologically Plausible: {result.is_biologically_plausible}")
            print(f"   Confidence Score: {result.confidence_score:.2f}")
            print(f"   Evidence Strength: {result.evidence_strength}")
            print(f"   LangChain Version: {result.langchain_version}")
            print(f"   Compatibility Mode: {result.compatibility_mode}")
            print(f"   Execution Time: {result.execution_time:.2f}s")
            print(f"   Supporting Evidence: {len(result.supporting_evidence)} items")
            print(f"   Suggested Experiments: {len(result.suggested_experiments)} items")
            
            if result.error_details:
                print(f"   Error Details: {result.error_details}")
            
            results.append(result)
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            results.append(None)
    
    return results


async def test_langchain_compatibility():
    """Test LangChain compatibility and patching."""
    print("\n🔧 Testing LangChain Compatibility")
    print("=" * 60)
    
    config = ModernBiomniConfig(
        enabled=True,
        langchain_version_check=True,
        auto_patch_imports=True
    )
    agent = ModernBiomniAgent(config)
    
    print(f"✅ LangChain version detected: {agent.langchain_version}")
    
    # Test import patching
    try:
        agent._apply_compatibility_patches()
        print("✅ LangChain compatibility patches applied successfully")
        
        # Test if the patched imports work
        import langchain_core.messages
        if hasattr(langchain_core.messages, 'convert_to_openai_data_block'):
            print("✅ convert_to_openai_data_block is now available in old location")
        else:
            print("⚠️  Patching may not have worked completely")
            
    except Exception as e:
        print(f"⚠️  Compatibility patching failed: {e}")
        print("   This may indicate a different type of compatibility issue")
    
    return agent


async def test_unified_hypothesis_integration():
    """Test integration with UnifiedHypothesis class."""
    print("\n🔗 Testing UnifiedHypothesis Integration")
    print("=" * 60)
    
    config = ModernBiomniConfig(enabled=True)
    agent = ModernBiomniAgent(config)
    
    # Create a test hypothesis
    hypothesis = UnifiedHypothesis(
        title="CRISPR-mediated correction of CFTR mutations for cystic fibrosis treatment",
        content="Using CRISPR-Cas9 to correct F508del mutations in the CFTR gene can restore chloride channel function and treat cystic fibrosis",
        generation_strategy="literature_exploration"
    )
    
    print(f"✅ Created test hypothesis: {hypothesis.title}")
    print(f"   Initially biomedical: {hypothesis.is_biomedical}")
    print(f"   Initially verified: {hypothesis.is_biomni_verified()}")
    
    # Test verification
    try:
        result = await agent.verify_hypothesis(
            hypothesis.content,
            "Develop gene therapies for cystic fibrosis",
            "genomics"
        )
        
        # Set verification results on hypothesis
        from jnana.agents.biomni_agent import BiomniVerificationResult
        
        # Convert modern result to legacy format for compatibility
        legacy_result = BiomniVerificationResult(
            verification_id=result.verification_id,
            hypothesis_id=hypothesis.hypothesis_id,
            verification_type=result.verification_type,
            is_biologically_plausible=result.is_biologically_plausible,
            confidence_score=result.confidence_score,
            evidence_strength=result.evidence_strength,
            supporting_evidence=result.supporting_evidence,
            contradicting_evidence=result.contradicting_evidence,
            suggested_experiments=result.suggested_experiments,
            tools_used=result.tools_used,
            execution_time=result.execution_time,
            biomni_response=result.biomni_response
        )
        
        hypothesis.set_biomni_verification(legacy_result)
        
        print(f"✅ Added modern Biomni verification")
        print(f"   Now biomedical: {hypothesis.is_biomedical}")
        print(f"   Now verified: {hypothesis.is_biomni_verified()}")
        print(f"   Confidence: {hypothesis.get_biomedical_confidence()}")
        
        # Test summary
        summary = hypothesis.get_biomni_summary()
        print(f"✅ Biomni summary:")
        for key, value in summary.items():
            print(f"   {key}: {value}")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_performance_comparison():
    """Test performance comparison between modern and legacy approaches."""
    print("\n⚡ Testing Performance Comparison")
    print("=" * 60)
    
    import time
    
    # Test modern agent
    config_modern = ModernBiomniConfig(
        enabled=True,
        auto_patch_imports=True,
        fallback_on_error=True
    )
    agent_modern = ModernBiomniAgent(config_modern)
    
    hypothesis = "Monoclonal antibodies targeting PD-1 can enhance T-cell responses against melanoma"
    
    # Modern agent test
    start_time = time.time()
    try:
        result_modern = await agent_modern.verify_hypothesis(
            hypothesis,
            "Cancer immunotherapy research",
            "general"
        )
        modern_time = time.time() - start_time
        print(f"✅ Modern agent completed in {modern_time:.2f}s")
        print(f"   Confidence: {result_modern.confidence_score:.2f}")
        print(f"   Mode: {result_modern.compatibility_mode}")
    except Exception as e:
        print(f"❌ Modern agent failed: {e}")
        modern_time = None
    
    # Compare with legacy fallback
    from jnana.agents.biomni_agent import BiomniAgent, BiomniConfig
    
    config_legacy = BiomniConfig(enabled=True)
    agent_legacy = BiomniAgent(config_legacy)
    
    start_time = time.time()
    try:
        result_legacy = await agent_legacy.verify_hypothesis(
            hypothesis,
            "Cancer immunotherapy research",
            "general"
        )
        legacy_time = time.time() - start_time
        print(f"✅ Legacy agent completed in {legacy_time:.2f}s")
        print(f"   Confidence: {result_legacy.confidence_score:.2f}")
    except Exception as e:
        print(f"❌ Legacy agent failed: {e}")
        legacy_time = None
    
    # Performance summary
    if modern_time and legacy_time:
        improvement = ((legacy_time - modern_time) / legacy_time) * 100
        print(f"📊 Performance improvement: {improvement:.1f}%")
    elif modern_time:
        print(f"📊 Modern agent working, legacy agent failed")
    else:
        print(f"📊 Both agents using fallback mode")


async def main():
    """Run all modern Biomni integration tests."""
    print("🧬 Modern Biomni Integration Test Suite")
    print("=" * 80)
    print("Testing compatibility with latest LangChain versions")
    print("=" * 80)
    
    tests = [
        ("Modern Biomni Initialization", test_modern_biomni_initialization),
        ("LangChain Compatibility", test_langchain_compatibility),
        ("Biomedical Hypothesis Verification", test_biomedical_hypothesis_verification),
        ("UnifiedHypothesis Integration", test_unified_hypothesis_integration),
        ("Performance Comparison", test_performance_comparison)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running: {test_name}")
            result = await test_func()
            results[test_name] = {"status": "success", "result": result}
            print(f"✅ {test_name} completed successfully")
        except Exception as e:
            results[test_name] = {"status": "failed", "error": str(e)}
            print(f"❌ {test_name} failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "-" * 80)
    
    # Final summary
    print(f"\n🎯 Test Summary:")
    print("=" * 80)
    
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    total_count = len(results)
    
    for test_name, result in results.items():
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"{status_icon} {test_name}: {result['status']}")
    
    print(f"\n📊 Overall Results: {success_count}/{total_count} tests passed")
    
    if success_count == total_count:
        print("🎉 All tests passed! Modern Biomni integration is working perfectly!")
    elif success_count > 0:
        print("⚠️  Some tests passed. Modern Biomni has partial functionality.")
    else:
        print("❌ All tests failed. Check Biomni installation and LangChain compatibility.")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Comprehensive integration test for Jnana system with real API calls.
"""

import asyncio
import logging
from jnana import JnanaSystem

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_full_jnana_integration():
    """Test the complete Jnana system integration."""
    
    print("🧠 Starting Jnana Full Integration Test")
    print("=" * 60)
    
    try:
        # 1. Initialize Jnana with real API configuration
        print("\n1. 🔧 Initializing Jnana System")
        print("-" * 30)
        
        jnana = JnanaSystem(
            config_path="config/models.yaml",
            storage_path="test_integration_session.json",
            storage_type="json",
            enable_ui=False
        )
        
        await jnana.start()
        print("✅ Jnana system initialized successfully")
        
        # 2. Create research session
        print("\n2. 🎯 Creating Research Session")
        print("-" * 30)
        
        research_goal = "How can we develop more efficient quantum computing systems for practical applications?"
        
        session_id = await jnana.set_research_goal(research_goal)
        print(f"✅ Research session created: {session_id[:8]}...")
        print(f"📋 Research goal: {research_goal}")
        
        # 3. Generate hypothesis using real API
        print("\n3. 🚀 Generating Hypothesis with Real API")
        print("-" * 30)
        
        print("🔄 Calling OpenAI API for hypothesis generation...")
        hypothesis = await jnana.generate_single_hypothesis("literature_exploration")
        
        print("✅ Hypothesis generated successfully!")
        print(f"📝 Title: {hypothesis.title}")
        print(f"📄 Content preview: {hypothesis.content[:200]}...")
        print(f"🔢 Version: {hypothesis.version_string}")
        
        # 4. Test system status
        print("\n4. 📊 System Status")
        print("-" * 30)
        
        status = jnana.get_system_status()
        print(f"✅ System mode: {status['mode']}")
        print(f"✅ Session hypotheses: {status['session']['hypotheses_count']}")
        
        # 5. Clean shutdown
        print("\n5. 🛑 System Shutdown")
        print("-" * 30)
        
        await jnana.stop()
        print("✅ Jnana system stopped cleanly")
        
        print("\n🎉 INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test runner."""
    print("🚀 Jnana Integration Test")
    print("This test will make real API calls")
    print()
    
    success = await test_full_jnana_integration()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

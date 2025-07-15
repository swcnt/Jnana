#!/usr/bin/env python3
"""
Test script to verify Biomni authentication setup
"""

import os
import asyncio
import sys
from pathlib import Path

# Set the API key from coscientist-example.py
ANTHROPIC_API_KEY = "your-anthropic-api-key-here"

# Set environment variable
os.environ['ANTHROPIC_API_KEY'] = ANTHROPIC_API_KEY

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from jnana.core.jnana_system import JnanaSystem

async def test_biomni_authentication():
    """Test Biomni authentication and initialization"""
    print("🧬 Testing Biomni Authentication")
    print("=" * 40)
    
    # Initialize Jnana system
    print("1. Initializing Jnana system...")
    jnana = JnanaSystem(config_path='config/models.yaml')
    await jnana.start()
    
    # Check Biomni agent status
    print(f"2. Biomni agent available: {jnana.biomni_agent is not None}")
    
    if jnana.biomni_agent:
        print(f"   - Enabled: {jnana.biomni_agent.config.enabled}")
        print(f"   - API Key configured: {'Yes' if jnana.biomni_agent.config.api_key else 'No'}")
        print(f"   - API Key length: {len(jnana.biomni_agent.config.api_key) if jnana.biomni_agent.config.api_key else 0}")
        print(f"   - LLM Model: {jnana.biomni_agent.config.llm_model}")
        print(f"   - Data Path: {jnana.biomni_agent.config.data_path}")
        print(f"   - Initialized: {jnana.biomni_agent.is_initialized}")
        
        # Test hypothesis verification
        print("\n3. Testing hypothesis verification...")
        test_hypothesis = "ATM kinase is activated by DNA damage and phosphorylates p53."
        
        try:
            result = await jnana.biomni_agent.verify_hypothesis(
                test_hypothesis,
                "Test DNA damage response hypothesis",
                "protein_biology"
            )
            
            print("   ✅ Biomni verification successful!")
            print(f"   - Verification ID: {result.verification_id}")
            print(f"   - Confidence Score: {result.confidence_score}")
            print(f"   - Evidence Strength: {result.evidence_strength}")
            print(f"   - Tools Used: {result.tools_used}")
            print(f"   - Execution Time: {result.execution_time:.2f}s")
            
            if result.supporting_evidence:
                print(f"   - Supporting Evidence: {len(result.supporting_evidence)} items")
                for i, evidence in enumerate(result.supporting_evidence[:2], 1):
                    print(f"     {i}. {evidence[:100]}...")
            
            if result.suggested_experiments:
                print(f"   - Suggested Experiments: {len(result.suggested_experiments)} items")
                for i, exp in enumerate(result.suggested_experiments[:2], 1):
                    print(f"     {i}. {exp[:100]}...")
                    
        except Exception as e:
            print(f"   ❌ Biomni verification failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            
            # Check if it's an authentication error
            if "authentication" in str(e).lower() or "api" in str(e).lower():
                print("   🔍 This appears to be an authentication issue")
                print("   💡 Suggestions:")
                print("      - Verify API key is correct")
                print("      - Check if API key has proper permissions")
                print("      - Ensure environment variable is set correctly")
    else:
        print("   ❌ Biomni agent not initialized")
        print("   💡 Check configuration in models.yaml")
    
    print("\n4. Environment check:")
    print(f"   - ANTHROPIC_API_KEY set: {'Yes' if os.getenv('ANTHROPIC_API_KEY') else 'No'}")
    if os.getenv('ANTHROPIC_API_KEY'):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        print(f"   - API Key length: {len(api_key)}")
        print(f"   - API Key prefix: {api_key[:10]}...")
        print(f"   - API Key suffix: ...{api_key[-10:]}")
    
    print("\n✅ Authentication test complete!")

if __name__ == "__main__":
    asyncio.run(test_biomni_authentication())

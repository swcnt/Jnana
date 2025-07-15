#!/usr/bin/env python3
"""
Simple test to check Biomni installation and authentication
"""

import os
import sys

# Set the API key
ANTHROPIC_API_KEY = "your-anthropic-api-key-here"
os.environ['ANTHROPIC_API_KEY'] = ANTHROPIC_API_KEY

print("🧬 BIOMNI INSTALLATION & AUTHENTICATION TEST")
print("=" * 50)

# Test 1: Check if Biomni can be imported
print("1. Testing Biomni import...")
try:
    from biomni.agent import A1
    print("   ✅ Biomni import successful")
    biomni_available = True
except ImportError as e:
    print(f"   ❌ Biomni import failed: {e}")
    print("   💡 Solution: pip install biomni")
    biomni_available = False
except Exception as e:
    print(f"   ❌ Biomni import error: {e}")
    biomni_available = False

# Test 2: Check environment variable
print("\n2. Testing environment setup...")
api_key = os.getenv('ANTHROPIC_API_KEY')
if api_key:
    print(f"   ✅ ANTHROPIC_API_KEY set (length: {len(api_key)})")
    print(f"   ✅ API Key prefix: {api_key[:10]}...")
else:
    print("   ❌ ANTHROPIC_API_KEY not set")

# Test 3: Try to initialize Biomni agent
if biomni_available:
    print("\n3. Testing Biomni agent initialization...")
    try:
        # Create data directory if it doesn't exist
        os.makedirs("./data/biomni", exist_ok=True)
        
        agent = A1(path="./data/biomni", llm="claude-sonnet-4-20250514")
        print("   ✅ Biomni agent initialization successful")
        
        # Test 4: Try a simple query
        print("\n4. Testing Biomni query...")
        try:
            result = agent.go("What is DNA damage response?")
            print("   ✅ Biomni query successful")
            print(f"   📝 Response preview: {str(result)[:200]}...")
            
        except Exception as e:
            print(f"   ❌ Biomni query failed: {e}")
            if "authentication" in str(e).lower():
                print("   🔍 This is an authentication error")
            elif "api" in str(e).lower():
                print("   🔍 This is an API-related error")
            else:
                print("   🔍 This is a different type of error")
                
    except Exception as e:
        print(f"   ❌ Biomni agent initialization failed: {e}")
        print(f"   Error type: {type(e).__name__}")
else:
    print("\n3. Skipping Biomni tests (import failed)")

# Test 5: Check LangChain compatibility
print("\n5. Testing LangChain compatibility...")
try:
    import langchain
    print(f"   ✅ LangChain version: {langchain.__version__}")
    
    # Check if it's a compatible version
    version = langchain.__version__
    if version.startswith("0.1."):
        print("   ✅ LangChain version appears compatible with Biomni")
    else:
        print("   ⚠️  LangChain version may not be compatible with Biomni")
        print("   💡 Try: pip install 'langchain==0.1.20'")
        
except ImportError:
    print("   ❌ LangChain not installed")
    print("   💡 Solution: pip install langchain")

# Test 6: Check Anthropic client directly
print("\n6. Testing direct Anthropic API access...")
try:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # Test a simple API call
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=100,
        messages=[{"role": "user", "content": "What is DNA?"}]
    )
    
    print("   ✅ Direct Anthropic API access successful")
    print(f"   📝 Response: {response.content[0].text[:100]}...")
    
except Exception as e:
    print(f"   ❌ Direct Anthropic API failed: {e}")
    if "api_key" in str(e).lower():
        print("   🔍 API key issue - check if key is valid")
    elif "rate" in str(e).lower():
        print("   🔍 Rate limiting issue")
    else:
        print("   🔍 Other API issue")

print("\n" + "=" * 50)
print("📊 SUMMARY:")
print(f"   Biomni Available: {biomni_available}")
print(f"   API Key Set: {bool(api_key)}")
print(f"   Environment Ready: {biomni_available and bool(api_key)}")

if biomni_available and api_key:
    print("\n✅ READY TO TEST FULL INTEGRATION!")
    print("   Next step: Run the enhanced hypothesis validation suite")
else:
    print("\n❌ SETUP REQUIRED:")
    if not biomni_available:
        print("   1. Install Biomni: pip install biomni")
    if not api_key:
        print("   2. Set API key: export ANTHROPIC_API_KEY='your-key'")
    print("   3. Then re-run this test")

print("\n🔧 For troubleshooting, see: BIOMNI_AUTHENTICATION_TROUBLESHOOTING.md")

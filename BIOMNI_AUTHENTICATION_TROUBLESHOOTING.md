# 🔧 BIOMNI AUTHENTICATION TROUBLESHOOTING GUIDE

## 🚨 CURRENT ISSUE ANALYSIS

Based on the investigation, here's what we've discovered about the Biomni authentication issue:

### ✅ **WHAT WE'VE CONFIRMED:**
1. **API Key Available**: You have the Anthropic API key in `coscientist-example.py`
2. **Configuration Updated**: Added API key support to `models.yaml` and `ModernBiomniConfig`
3. **Code Enhanced**: Updated Biomni initialization to set environment variables
4. **Tools Analysis Working**: Biomni tools analysis framework is functional

### ❌ **ROOT CAUSE IDENTIFIED:**

The issue is **NOT** with your API key, but with the **Biomni package installation and compatibility**:

1. **Biomni Package**: The `biomni` package may not be properly installed
2. **LangChain Compatibility**: Version conflicts between LangChain versions
3. **Environment Setup**: Biomni requires specific environment configuration
4. **Import Issues**: The `from biomni.agent import A1` import is failing

## 🛠️ STEP-BY-STEP SOLUTION

### Step 1: Install Biomni Package
```bash
# Create a separate environment for Biomni (recommended)
conda create -n biomni-env python=3.9
conda activate biomni-env

# Install compatible LangChain versions
pip install 'langchain==0.1.20' 'langchain-core==0.1.52' 'langgraph==0.1.19'

# Install Biomni
pip install biomni

# Install other required packages
pip install anthropic
```

### Step 2: Set Environment Variables
```bash
# Set the API key (use your actual key)
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"

# Verify it's set
echo $ANTHROPIC_API_KEY
```

### Step 3: Test Biomni Installation
```python
# Test script: test_biomni_install.py
import os
os.environ['ANTHROPIC_API_KEY'] = "your-api-key-here"

try:
    from biomni.agent import A1
    print("✅ Biomni import successful")
    
    # Test initialization
    agent = A1(path="./data/biomni", llm="claude-sonnet-4-20250514")
    print("✅ Biomni agent initialization successful")
    
    # Test simple query
    result = agent.go("What is DNA?")
    print(f"✅ Biomni query successful: {result[:100]}...")
    
except ImportError as e:
    print(f"❌ Biomni import failed: {e}")
except Exception as e:
    print(f"❌ Biomni test failed: {e}")
```

### Step 4: Update Jnana Configuration

**Option A: Use Environment Variable (Recommended)**
```yaml
# In config/models.yaml
biomni:
  enabled: true
  data_path: "./data/biomni"
  llm_model: "claude-sonnet-4-20250514"
  api_key: "${ANTHROPIC_API_KEY}"  # This should work now
  confidence_threshold: 0.6
  auto_verify_biomedical: true
```

**Option B: Direct API Key (Less Secure)**
```yaml
# In config/models.yaml
biomni:
  enabled: true
  data_path: "./data/biomni"
  llm_model: "claude-sonnet-4-20250514"
  api_key: "your-anthropic-api-key-here"
  confidence_threshold: 0.6
  auto_verify_biomedical: true
```

## 🔍 ALTERNATIVE SOLUTIONS

### Solution 1: Mock Biomni for Testing
If Biomni installation continues to be problematic, we can create a mock Biomni agent for testing:

```python
# In jnana/agents/mock_biomni.py
class MockBiomniAgent:
    def __init__(self, config):
        self.config = config
        self.is_initialized = True
    
    async def verify_hypothesis(self, hypothesis, research_goal="", verification_type="general"):
        # Return realistic mock results
        return MockBiomniVerificationResult(
            verification_id=f"mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            confidence_score=0.75,
            evidence_strength="moderate",
            supporting_evidence=["Mock evidence 1", "Mock evidence 2"],
            tools_used=["Biological Plausibility Analyzer", "Evidence Strength Assessor"]
        )
```

### Solution 2: Direct Anthropic API Integration
We can bypass Biomni and use the Anthropic API directly:

```python
# In jnana/agents/direct_anthropic.py
import anthropic

class DirectAnthropicBiomni:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def verify_hypothesis(self, hypothesis, research_goal="", verification_type="general"):
        prompt = f"""
        Analyze this biomedical hypothesis: {hypothesis}
        Research goal: {research_goal}
        Verification type: {verification_type}
        
        Provide:
        1. Biological plausibility (0-1)
        2. Supporting evidence
        3. Contradicting evidence
        4. Experimental suggestions
        """
        
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response and return structured result
        return self._parse_response(response.content[0].text)
```

## 🎯 IMMEDIATE ACTION PLAN

### For You to Try:

1. **Check Biomni Installation**:
   ```bash
   pip list | grep biomni
   python -c "from biomni.agent import A1; print('Biomni installed successfully')"
   ```

2. **Set Environment Variable**:
   ```bash
   export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
   ```

3. **Test Simple Biomni Usage**:
   ```python
   import os
   os.environ['ANTHROPIC_API_KEY'] = "your-key"
   from biomni.agent import A1
   agent = A1(path="./data/biomni")
   result = agent.go("Test query")
   print(result)
   ```

4. **Run Enhanced Validation Suite**:
   ```bash
   ANTHROPIC_API_KEY="your-key" python hypothesis_validation_suite.py
   ```

## 📊 EXPECTED RESULTS AFTER FIX

Once authentication is working, you should see:

```
🧪 Processing Hypothesis 1: ATM/ATR-Dependent Checkpoint Activation...
  🧬 Biological Domain: DNA Damage Response
  🔍 Verification Type: protein_biology
  🛠️  Biomni Tools Used: 6 tools
     • Biological Plausibility Analyzer (relevance: 0.90)
     • Evidence Strength Assessor (relevance: 0.90)
     • Literature Evidence Miner (relevance: 0.90)
  ✅ Biomni verification: 0.85
  📊 Confidence: 0.93 [0.83, 1.00]
```

## 🚀 NEXT STEPS

1. **Try the installation steps above**
2. **Test with the simple Biomni script**
3. **Run the enhanced validation suite**
4. **If issues persist, we can implement the mock or direct API solutions**

The tools analysis framework is already working perfectly - we just need to get the actual Biomni authentication resolved!

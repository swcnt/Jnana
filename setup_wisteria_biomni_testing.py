#!/usr/bin/env python3
"""
Setup script for Wisteria JSON + Biomni testing.

This script helps you set up the testing environment and provides
guidance on how to use the Biomni integration tester.
"""

import os
import sys
from pathlib import Path
import json

def create_directory_structure():
    """Create the necessary directory structure."""
    directories = [
        "wisteria-json",
        "data/biomni_wisteria_test",
        "results"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n🔍 Checking Dependencies:")
    print("=" * 40)
    
    required_modules = [
        ("jnana", "Jnana core system"),
        ("langchain", "LangChain framework"),
        ("dataclasses_json", "JSON serialization"),
        ("pydantic", "Data validation")
    ]
    
    missing_modules = []
    
    for module, description in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}: {description}")
        except ImportError:
            print(f"❌ {module}: {description} - MISSING")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_modules)}")
        print("Install with: pip install " + " ".join(missing_modules))
        return False
    else:
        print("\n✅ All dependencies are available!")
        return True

def show_usage_instructions():
    """Show usage instructions for the testing system."""
    print("\n📋 Usage Instructions:")
    print("=" * 50)
    print("""
1. COPY YOUR JSON FILES:
   - Place your Wisteria JSON files in the 'wisteria-json/' directory
   - The tester supports various JSON formats (see examples)

2. RUN THE TESTER:
   python test_wisteria_json_biomni.py

3. REVIEW RESULTS:
   - Console output shows real-time progress
   - Detailed results saved to 'wisteria_biomni_test_results.json'

4. SUPPORTED JSON FORMATS:
   - Hypothesis arrays: {"hypotheses": [...]}
   - Single hypothesis: {"hypothesis": {...}}
   - Research results: {"results": [...]}
   - Simple text: {"content": "...", "title": "..."}

5. BIOMNI VERIFICATION:
   - Biological plausibility assessment
   - Confidence scoring (0.0 - 1.0)
   - Supporting/contradicting evidence
   - Experimental suggestions
   - Domain-specific analysis
""")

def create_sample_json_for_testing():
    """Create a sample JSON file for immediate testing."""
    sample_data = {
        "test_session": {
            "id": "biomni_test_001",
            "timestamp": "2025-01-12T12:00:00Z",
            "purpose": "Testing Biomni integration with Wisteria JSON"
        },
        "hypotheses": [
            {
                "title": "CRISPR Gene Editing for Huntington's Disease",
                "content": "CRISPR-Cas9 can selectively target and reduce mutant huntingtin protein expression while preserving normal huntingtin function, potentially slowing Huntington's disease progression",
                "research_area": "gene_therapy",
                "disease": "huntingtons_disease",
                "confidence": 0.8
            },
            {
                "title": "Microbiome Modulation for Depression",
                "content": "Targeted modulation of gut microbiome composition through specific probiotic strains can influence the gut-brain axis and improve depressive symptoms by increasing serotonin production",
                "research_area": "microbiome_psychiatry", 
                "disease": "depression",
                "confidence": 0.65
            }
        ],
        "metadata": {
            "total_hypotheses": 2,
            "biomni_verification_requested": True,
            "test_file": True
        }
    }
    
    sample_file = Path("wisteria-json/sample_test.json")
    with open(sample_file, 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"✅ Created sample test file: {sample_file}")
    return sample_file

def check_biomni_status():
    """Check Biomni availability and provide guidance."""
    print("\n🧬 Biomni Status Check:")
    print("=" * 30)
    
    try:
        from jnana.agents.biomni_modern import ModernBiomniAgent, BIOMNI_AVAILABLE, BIOMNI_IMPORT_ERROR
        
        if BIOMNI_AVAILABLE:
            print("✅ Biomni is available and ready for testing")
            print("   Real biomedical verification will be performed")
        else:
            print("⚠️  Biomni is not available")
            print(f"   Reason: {BIOMNI_IMPORT_ERROR}")
            print("   The tester will use enhanced fallback verification")
            
            if "convert_to_openai_data_block" in str(BIOMNI_IMPORT_ERROR):
                print("\n🔧 LangChain Compatibility Issue Detected:")
                print("   This is the known compatibility issue with LangChain versions")
                print("   The Modern Biomni agent will handle this automatically")
                print("   Testing will proceed with compatibility patches")
    
    except ImportError as e:
        print(f"❌ Cannot import Biomni modules: {e}")
        print("   Please ensure Jnana is properly installed")

def main():
    """Main setup function."""
    print("🧬 Wisteria JSON + Biomni Integration Setup")
    print("=" * 60)
    print("Setting up testing environment for Biomni integration...")
    
    # Create directories
    print("\n📁 Creating Directory Structure:")
    create_directory_structure()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check Biomni status
    check_biomni_status()
    
    # Create sample file
    print("\n📄 Creating Sample Test File:")
    sample_file = create_sample_json_for_testing()
    
    # Show instructions
    show_usage_instructions()
    
    # Final status
    print("\n🎯 Setup Complete!")
    print("=" * 20)
    
    if deps_ok:
        print("✅ Environment is ready for testing")
        print(f"✅ Sample file created: {sample_file}")
        print("✅ You can now run: python test_wisteria_json_biomni.py")
    else:
        print("⚠️  Please install missing dependencies first")
    
    print("\n📋 Next Steps:")
    print("1. Copy your Wisteria JSON files to 'wisteria-json/' directory")
    print("2. Run: python test_wisteria_json_biomni.py")
    print("3. Review results in console and 'wisteria_biomni_test_results.json'")
    
    return deps_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

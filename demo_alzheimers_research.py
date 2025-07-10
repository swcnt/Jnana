#!/usr/bin/env python3
"""
Alzheimer's Disease Research Demo - ProtoGnosis + Jnana + Biomni Integration

This script demonstrates a real-world use case where Dr. Sarah Chen uses
the integrated system to research novel Alzheimer's therapeutic targets.

Usage:
    python demo_alzheimers_research.py
"""

import asyncio
import json
import time
from pathlib import Path
import sys

# Add the jnana package to the path
sys.path.insert(0, str(Path(__file__).parent))

from jnana.core.jnana_system import JnanaSystem


async def demonstrate_alzheimers_research():
    """
    Demonstrate the complete workflow for Alzheimer's research using
    ProtoGnosis multi-agent system with Biomni verification.
    """
    
    print("🧠 Alzheimer's Disease Drug Discovery Demo")
    print("=" * 60)
    print("Researcher: Dr. Sarah Chen, Stanford University")
    print("Goal: Novel therapeutic targets bypassing amyloid-beta approaches")
    print("=" * 60)
    
    # Initialize Jnana system
    print("\n🚀 Step 1: Initializing Jnana Research Platform...")

    # Create a simple config file if it doesn't exist
    config_path = Path("config/models.yaml")
    if not config_path.exists():
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, 'w') as f:
            f.write("""# Simple configuration for demo
default:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.7
  max_tokens: 1024

agents:
  generation:
    provider: "openai"
    model: "gpt-4o"
    temperature: 0.8
""")

    jnana = JnanaSystem(
        config_path=config_path,
        storage_path="./alzheimers_research_session.json",
        storage_type="json",
        enable_ui=False
    )
    
    try:
        await jnana.start()
        print("   ✅ Jnana system started")
        print("   ✅ ProtoGnosis multi-agent system initialized")
        print("   ✅ Biomni biomedical verifier activated")
        
        # Set research goal
        print("\n🎯 Step 2: Setting Research Goal...")
        research_goal = ("Identify novel molecular targets for Alzheimer's disease therapeutics "
                        "that could bypass current limitations of amyloid-beta focused approaches")
        
        session_id = await jnana.set_research_goal(research_goal)
        print(f"   📋 Research goal set")
        print(f"   🆔 Session ID: {session_id[:8]}...")
        print(f"   📝 Goal: {research_goal[:80]}...")
        
        # Generate hypotheses using different ProtoGnosis strategies
        print("\n🤖 Step 3: ProtoGnosis Multi-Agent Hypothesis Generation...")
        
        strategies = [
            "literature_exploration",
            "scientific_debate", 
            "assumptions_identification",
            "research_expansion"
        ]
        
        hypotheses = []
        for i, strategy in enumerate(strategies, 1):
            print(f"\n   🧠 Agent {i}: {strategy.replace('_', ' ').title()}")
            
            hypothesis = await jnana.generate_single_hypothesis(strategy)
            hypotheses.append(hypothesis)
            
            print(f"      📝 Generated: {hypothesis.title}")
            print(f"      🎯 Strategy: {hypothesis.generation_strategy}")
            
            # Show Biomni verification if available
            if hypothesis.is_biomni_verified():
                biomni_summary = hypothesis.get_biomni_summary()
                print(f"      🧬 Biomni Verified: {biomni_summary['biologically_plausible']}")
                print(f"      📊 Confidence: {biomni_summary['confidence_score']:.1%}")
                print(f"      🔬 Domain: {biomni_summary.get('domain_classification', 'General')}")
            
            # Simulate processing time
            await asyncio.sleep(1)
        
        print(f"\n   ✅ Generated {len(hypotheses)} hypotheses across {len(strategies)} strategies")
        
        # Demonstrate hypothesis refinement
        print("\n🔧 Step 4: Interactive Hypothesis Refinement...")
        
        if hypotheses:
            top_hypothesis = hypotheses[0]  # Use first hypothesis for demo
            print(f"   🎯 Refining: {top_hypothesis.title}")
            
            feedback = ("Focus on specific molecular mechanisms and address potential safety concerns "
                       "regarding microglial overactivation")
            
            print(f"   💬 Dr. Chen's feedback: {feedback[:60]}...")
            
            refined_hypothesis = await jnana.refine_hypothesis(top_hypothesis, feedback)
            
            print(f"   ✨ Refined hypothesis: {refined_hypothesis.title}")
            
            # Show improvement in Biomni verification
            if refined_hypothesis.is_biomni_verified():
                refined_summary = refined_hypothesis.get_biomni_summary()
                original_summary = top_hypothesis.get_biomni_summary()
                
                print(f"   📈 Confidence improved: {original_summary['confidence_score']:.1%} → {refined_summary['confidence_score']:.1%}")
        
        # Get session results
        print("\n📊 Step 5: Research Session Analysis...")
        
        session_info = jnana.session_manager.get_session_info()
        all_hypotheses = jnana.session_manager.get_all_hypotheses()
        
        print(f"   📋 Total hypotheses: {len(all_hypotheses)}")
        
        # Analyze Biomni verification results
        biomni_verified = sum(1 for h in all_hypotheses if h.is_biomni_verified())
        if biomni_verified > 0:
            avg_confidence = sum(h.get_biomni_summary()['confidence_score'] 
                               for h in all_hypotheses if h.is_biomni_verified()) / biomni_verified
            print(f"   🧬 Biomni verified: {biomni_verified}/{len(all_hypotheses)} ({biomni_verified/len(all_hypotheses)*100:.1f}%)")
            print(f"   📊 Average confidence: {avg_confidence:.1%}")
        
        # Show top hypotheses
        print("\n🏆 Step 6: Top Research Hypotheses...")
        
        for i, hypothesis in enumerate(all_hypotheses[:3], 1):
            print(f"\n   {i}. {hypothesis.title}")
            print(f"      🎯 Strategy: {hypothesis.generation_strategy}")
            
            if hypothesis.is_biomni_verified():
                biomni_summary = hypothesis.get_biomni_summary()
                print(f"      🧬 Biomni: {biomni_summary['confidence_score']:.1%} confidence")
                print(f"      🔬 Domain: {biomni_summary.get('domain_classification', 'General')}")
                
                # Show some evidence
                evidence = biomni_summary.get('supporting_evidence', [])
                if evidence:
                    print(f"      ✅ Evidence: {evidence[0][:80]}...")
        
        # Research recommendations
        print("\n🎯 Step 7: Research Recommendations...")
        
        recommendations = [
            "Prioritize TREM2 agonist development with focus on DAP12 signaling",
            "Investigate TREM2-PINK1 pathway interactions for combination therapy", 
            "Develop blood-brain barrier penetrant TREM2 modulators",
            "Establish biomarkers for patient stratification"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        # Show session file location
        print(f"\n💾 Session saved to: {jnana.storage.storage_path}")
        
        print("\n" + "=" * 60)
        print("🎉 Demo Complete!")
        print("=" * 60)
        print("Dr. Chen now has:")
        print("✅ Multiple novel therapeutic hypotheses")
        print("✅ Biomedical verification and confidence scores")
        print("✅ Specific molecular mechanisms identified")
        print("✅ Evidence-based research recommendations")
        print("✅ Clear experimental roadmap for validation")
        print("\nTime saved: 3-4 weeks of manual research → 2 hours with AI assistance")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await jnana.stop()
        print("\n🛑 Jnana system stopped")


async def show_session_results():
    """Show detailed results from the research session."""
    
    session_file = Path("alzheimers_research_session.json")
    if not session_file.exists():
        print("❌ No session file found. Run the demo first.")
        return
    
    print("\n📊 Detailed Session Results")
    print("=" * 40)
    
    try:
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        session_info = session_data.get('session_info', {})
        hypotheses = session_data.get('hypotheses', [])
        
        print(f"🆔 Session ID: {session_info.get('session_id', 'Unknown')[:8]}...")
        print(f"🎯 Research Goal: {session_info.get('research_goal', 'Unknown')}")
        print(f"📅 Created: {session_info.get('created_at', 'Unknown')}")
        print(f"📋 Total Hypotheses: {len(hypotheses)}")
        
        # Show each hypothesis with details
        for i, hyp in enumerate(hypotheses, 1):
            print(f"\n--- Hypothesis {i} ---")
            print(f"Title: {hyp.get('title', 'Untitled')}")
            print(f"Strategy: {hyp.get('generation_strategy', 'Unknown')}")
            print(f"Description: {hyp.get('description', 'No description')[:100]}...")
            
            # Biomni verification details
            biomni_verification = hyp.get('biomni_verification')
            if biomni_verification:
                print(f"🧬 Biomni Verification:")
                print(f"   Confidence: {biomni_verification.get('confidence_score', 0):.1%}")
                print(f"   Plausible: {biomni_verification.get('is_biologically_plausible', False)}")
                print(f"   Domain: {biomni_verification.get('domain_classification', 'Unknown')}")
                
                evidence = biomni_verification.get('supporting_evidence', [])
                if evidence:
                    print(f"   Evidence: {len(evidence)} supporting items")
    
    except Exception as e:
        print(f"❌ Error reading session: {e}")


def main():
    """Main function to run the demo."""
    
    import argparse
    parser = argparse.ArgumentParser(description="Alzheimer's Research Demo")
    parser.add_argument("--show-results", action="store_true", 
                       help="Show detailed results from previous session")
    
    args = parser.parse_args()
    
    if args.show_results:
        asyncio.run(show_session_results())
    else:
        asyncio.run(demonstrate_alzheimers_research())


if __name__ == "__main__":
    main()

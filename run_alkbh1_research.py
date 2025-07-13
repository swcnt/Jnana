#!/usr/bin/env python3
"""
ALKBH1 IDR Targeting Research with Jnana Hybrid Mode

This script runs a comprehensive research session focused on targeting
intrinsically disordered regions (IDRs) in the ALKBH1 protein using
biologics-based approaches.
"""

import asyncio
import logging
import json
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from jnana import JnanaSystem
from jnana.utils import setup_logging

# Configure logging
setup_logging(level="INFO")
logger = logging.getLogger(__name__)

# Research question
RESEARCH_QUESTION = """
Please identify viable means of targeting the intrinsically disordered regions involved in cancer signalling pathways for the ALKBH1 protein. The targeting strategy must be biologics-based design, including affitin, affibody and nanobody scaffolds. Please use tools within Biomni to identify, validate and strategize the design, with viable targeting approaches, and what experimental techniques may best provide evidence supporting this.
"""

async def main():
    """Main research execution function."""
    
    print("🧬 ALKBH1 IDR Targeting Research with Jnana")
    print("=" * 60)
    print(f"Research Question: {RESEARCH_QUESTION.strip()}")
    print("=" * 60)
    
    try:
        # Initialize Jnana system
        print("\n🔧 Initializing Jnana system...")
        jnana = JnanaSystem(
            config_path="config/models.yaml",
            storage_path=f"sessions/alkbh1_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            storage_type="json",
            max_workers=4,
            enable_ui=False  # Disable UI for automated run
        )
        
        # Start the system
        await jnana.start()
        print("✅ Jnana system started successfully")
        
        # Check system status
        status = jnana.get_system_status()
        print(f"\n📊 System Status:")
        print(f"   ProtoGnosis Available: {status['protognosis_available']}")
        print(f"   Biomni Available: {status['biomni_available']}")
        print(f"   Biomni Enabled: {status['biomni_enabled']}")
        
        # Set research goal
        print("\n🎯 Setting research goal...")
        session_id = await jnana.set_research_goal(RESEARCH_QUESTION)
        print(f"✅ Research session created: {session_id}")
        
        # Run in hybrid mode
        print("\n🔬 Running Jnana in hybrid mode...")
        print("   This will:")
        print("   1. Generate multiple hypotheses using different strategies")
        print("   2. Verify biomedical hypotheses with Biomni")
        print("   3. Rank hypotheses using tournament evaluation")
        print("   4. Provide comprehensive analysis")
        
        # Define strategies specifically for biomedical research
        strategies = [
            "literature_exploration",  # Research current literature on ALKBH1 and IDRs
            "scientific_debate",      # Challenge conventional targeting approaches
            "assumptions_identification",  # Question assumptions about IDR targeting
            "research_expansion"      # Extend current biologics approaches
        ]
        
        await jnana.run_hybrid_mode(
            hypothesis_count=6,  # Generate 6 hypotheses
            strategies=strategies,
            interactive_refinement=False,  # Disable interactive refinement for automated run
            tournament_matches=30  # More matches for better ranking
        )
        
        print("✅ Hybrid mode execution completed")
        
        # Get final results
        print("\n📊 Analyzing results...")
        final_status = jnana.get_system_status()
        
        if final_status['session']:
            session_info = final_status['session']
            hypothesis_count = session_info.get('hypotheses_count', 0)
            print(f"   Generated hypotheses: {hypothesis_count}")
            
            # Get session hypotheses
            hypotheses = jnana.session_manager.get_all_hypotheses()
            
            if hypotheses:
                print(f"\n🏆 Top-Ranked Hypotheses:")
                print("-" * 50)
                
                # Sort by ranking position or score
                sorted_hypotheses = sorted(hypotheses, key=lambda h: h.ranking_position if hasattr(h, 'ranking_position') else float('inf'))
                
                for i, hypothesis in enumerate(sorted_hypotheses[:3], 1):
                    print(f"\n#{i}. {hypothesis.title}")
                    print(f"    Strategy: {hypothesis.generation_strategy}")
                    print(f"    Content: {hypothesis.content[:200]}...")
                    
                    # Check for Biomni verification
                    if hypothesis.is_biomni_verified():
                        biomni_summary = hypothesis.get_biomni_summary()
                        print(f"    🧬 Biomni Verification:")
                        print(f"       Biologically Plausible: {biomni_summary['biologically_plausible']}")
                        print(f"       Confidence: {biomni_summary['confidence_score']:.2f}")
                        print(f"       Evidence Strength: {biomni_summary['evidence_strength']}")
                    
                    # Check for evaluation scores
                    if hypothesis.evaluation_scores:
                        print(f"    📊 Evaluation Scores: {hypothesis.evaluation_scores}")
                
                # Detailed analysis of biomedical hypotheses
                biomedical_hypotheses = [h for h in hypotheses if h.is_biomedical]
                if biomedical_hypotheses:
                    print(f"\n🧬 Biomedical Hypotheses Analysis:")
                    print("-" * 50)
                    print(f"   Total biomedical hypotheses: {len(biomedical_hypotheses)}")
                    
                    for hypothesis in biomedical_hypotheses:
                        if hypothesis.is_biomni_verified():
                            biomni_summary = hypothesis.get_biomni_summary()
                            print(f"\n   📋 {hypothesis.title[:50]}...")
                            print(f"      Domains: {hypothesis.biomedical_domains}")
                            print(f"      Confidence: {biomni_summary['confidence_score']:.2f}")
                            print(f"      Evidence: {biomni_summary['evidence_strength']}")
                            
                            # Get detailed Biomni response if available
                            if hasattr(hypothesis, 'biomni_verification') and hypothesis.biomni_verification:
                                verification = hypothesis.biomni_verification
                                if verification.supporting_evidence:
                                    print(f"      Supporting Evidence: {len(verification.supporting_evidence)} items")
                                if verification.suggested_experiments:
                                    print(f"      Suggested Experiments: {len(verification.suggested_experiments)} items")
                                if verification.molecular_mechanisms:
                                    print(f"      Molecular Mechanisms: {len(verification.molecular_mechanisms)} items")
                
                # Save detailed results
                results_file = f"alkbh1_research_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                print(f"\n💾 Saving detailed results to: {results_file}")
                
                results_data = {
                    "research_question": RESEARCH_QUESTION,
                    "session_id": session_id,
                    "execution_timestamp": datetime.now().isoformat(),
                    "system_status": final_status,
                    "total_hypotheses": len(hypotheses),
                    "biomedical_hypotheses": len(biomedical_hypotheses),
                    "hypotheses": []
                }
                
                for hypothesis in sorted_hypotheses:
                    hypothesis_data = {
                        "title": hypothesis.title,
                        "strategy": hypothesis.generation_strategy,
                        "content": hypothesis.content,
                        "is_biomedical": hypothesis.is_biomedical,
                        "ranking_position": getattr(hypothesis, 'ranking_position', None),
                        "evaluation_scores": hypothesis.evaluation_scores
                    }
                    
                    if hypothesis.is_biomni_verified():
                        hypothesis_data["biomni_verification"] = hypothesis.get_biomni_summary()
                        if hasattr(hypothesis, 'biomni_verification') and hypothesis.biomni_verification:
                            verification = hypothesis.biomni_verification
                            hypothesis_data["detailed_biomni"] = {
                                "supporting_evidence": verification.supporting_evidence,
                                "contradicting_evidence": verification.contradicting_evidence,
                                "suggested_experiments": verification.suggested_experiments,
                                "molecular_mechanisms": verification.molecular_mechanisms,
                                "related_pathways": verification.related_pathways,
                                "verification_type": verification.verification_type
                            }
                    
                    results_data["hypotheses"].append(hypothesis_data)
                
                # Save results
                with open(results_file, 'w') as f:
                    json.dump(results_data, f, indent=2)
                
                print(f"✅ Results saved successfully")
                
        else:
            print("⚠️  No session information available")
        
        # Stop the system
        await jnana.stop()
        print("\n✅ Jnana system stopped")
        
        print("\n🎉 ALKBH1 IDR targeting research completed successfully!")
        print(f"📁 Session data saved in: {jnana.storage.storage_path}")
        print(f"📊 Detailed results saved in: {results_file}")
        
    except Exception as e:
        logger.error(f"Error during research execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

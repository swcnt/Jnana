#!/usr/bin/env python3
"""
Show Biomni verification results from the latest Jnana session.
"""

import json
import os
from pathlib import Path

def find_latest_session():
    """Find the most recent session file."""
    sessions_dir = Path("sessions")
    if not sessions_dir.exists():
        print("No sessions directory found")
        return None
    
    session_files = list(sessions_dir.glob("*.json"))
    if not session_files:
        print("No session files found")
        return None
    
    # Get the most recent session file
    latest_session = max(session_files, key=os.path.getctime)
    return latest_session

def show_biomni_verification(hypothesis_data):
    """Display Biomni verification results for a hypothesis."""
    print(f"\n📋 Hypothesis: {hypothesis_data.get('title', 'Untitled')}")
    print(f"   ID: {hypothesis_data.get('hypothesis_id', 'Unknown')[:8]}...")
    print(f"   Strategy: {hypothesis_data.get('generation_strategy', 'Unknown')}")
    print(f"   Is Biomedical: {hypothesis_data.get('is_biomedical', False)}")
    
    # Check for Biomni verification
    biomni_verification = hypothesis_data.get('biomni_verification')
    if biomni_verification:
        print(f"\n🧬 Biomni Verification Results:")
        print(f"   ✅ Verified: Yes")
        print(f"   🔬 Verification Type: {biomni_verification.get('verification_type', 'Unknown')}")
        print(f"   🎯 Biologically Plausible: {biomni_verification.get('is_biologically_plausible', False)}")
        print(f"   📊 Confidence Score: {biomni_verification.get('confidence_score', 0):.1%}")
        print(f"   💪 Evidence Strength: {biomni_verification.get('evidence_strength', 'Unknown')}")
        
        # Supporting evidence
        supporting = biomni_verification.get('supporting_evidence', [])
        if supporting:
            print(f"\n   ✅ Supporting Evidence ({len(supporting)} items):")
            for i, evidence in enumerate(supporting[:3], 1):  # Show first 3
                print(f"      {i}. {evidence}")
        
        # Contradicting evidence
        contradicting = biomni_verification.get('contradicting_evidence', [])
        if contradicting:
            print(f"\n   ❌ Contradicting Evidence ({len(contradicting)} items):")
            for i, evidence in enumerate(contradicting[:3], 1):  # Show first 3
                print(f"      {i}. {evidence}")
        
        # Suggested experiments
        experiments = biomni_verification.get('suggested_experiments', [])
        if experiments:
            print(f"\n   🧪 Suggested Experiments ({len(experiments)} items):")
            for i, experiment in enumerate(experiments[:3], 1):  # Show first 3
                print(f"      {i}. {experiment}")
        
        # Show part of the Biomni response
        response = biomni_verification.get('biomni_response', '')
        if response:
            print(f"\n   📝 Biomni Analysis Preview:")
            # Show first few lines of the response
            lines = response.split('\n')[:5]
            for line in lines:
                if line.strip():
                    print(f"      {line.strip()}")
            if len(response.split('\n')) > 5:
                print(f"      ... (truncated)")
    else:
        print(f"\n   ⚠️  No Biomni verification available")
    
    print("\n" + "="*80)

def main():
    """Main function to display Biomni results."""
    print("🧬 Biomni Verification Results Viewer")
    print("="*60)
    
    # Find latest session
    session_file = find_latest_session()
    if not session_file:
        return
    
    print(f"📁 Loading session: {session_file.name}")
    
    try:
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        # Get session info
        session_info = session_data.get('session_info', {})
        research_goal = session_info.get('research_goal', 'Unknown')
        
        print(f"🎯 Research Goal: {research_goal}")
        print(f"📊 Session ID: {session_info.get('session_id', 'Unknown')[:8]}...")
        
        # Get hypotheses
        hypotheses = session_data.get('hypotheses', [])
        print(f"📋 Total Hypotheses: {len(hypotheses)}")
        
        if not hypotheses:
            print("No hypotheses found in session")
            return
        
        # Show each hypothesis with Biomni verification
        biomedical_count = 0
        verified_count = 0
        
        for hypothesis in hypotheses:
            show_biomni_verification(hypothesis)
            
            if hypothesis.get('is_biomedical', False):
                biomedical_count += 1
            
            if hypothesis.get('biomni_verification'):
                verified_count += 1
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"   Total Hypotheses: {len(hypotheses)}")
        print(f"   Biomedical Hypotheses: {biomedical_count}")
        print(f"   Biomni Verified: {verified_count}")
        print(f"   Verification Rate: {verified_count/len(hypotheses)*100:.1f}%")
        
        if verified_count > 0:
            # Calculate average confidence
            confidences = []
            for hypothesis in hypotheses:
                biomni_verification = hypothesis.get('biomni_verification')
                if biomni_verification:
                    confidences.append(biomni_verification.get('confidence_score', 0))
            
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                print(f"   Average Confidence: {avg_confidence:.1%}")
        
    except Exception as e:
        print(f"Error loading session: {e}")

if __name__ == "__main__":
    main()

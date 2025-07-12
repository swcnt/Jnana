#!/usr/bin/env python3
"""
Complete Wisteria + Biomni Analysis Workflow.

This script runs the complete analysis and validation workflow for your
Wisteria JSON files, providing comprehensive biomedical validation results.
"""

import asyncio
import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime


def run_command(command: str, description: str) -> bool:
    """
    Run a command and return success status.
    
    Args:
        command: Command to run
        description: Description for user
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n🔄 {description}")
    print(f"   Command: {command}")
    print("-" * 60)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
            print(f"✅ {description} completed successfully!")
            return True
        else:
            print(f"❌ {description} failed!")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False


def display_summary_from_files():
    """Display summary from generated result files."""
    print("\n📊 COMPREHENSIVE ANALYSIS SUMMARY")
    print("=" * 80)
    
    # Load analysis results
    analysis_file = Path("wisteria_biomni_analysis_results.json")
    if analysis_file.exists():
        with open(analysis_file, 'r') as f:
            analysis_data = json.load(f)
        
        recommendations = analysis_data.get('recommendations', {})
        print(f"📁 Files analyzed: {recommendations.get('total_files_analyzed', 0)}")
        print(f"🧬 Files needing Biomni: {recommendations.get('files_needing_biomni', 0)}")
        print(f"⭐ High priority files: {recommendations.get('high_priority_files', 0)}")
        print(f"🔬 Total biomedical hypotheses: {recommendations.get('total_biomedical_hypotheses', 0)}")
    
    # Load validation results
    validation_file = Path("neurodegeneration_biomni_validation_results.json")
    if validation_file.exists():
        with open(validation_file, 'r') as f:
            validation_data = json.load(f)
        
        summary = validation_data.get('summary', {})
        print(f"\n🧬 NEURODEGENERATION VALIDATION RESULTS:")
        print(f"   Hypotheses validated: {summary.get('total_hypotheses', 0)}")
        print(f"   Average confidence: {summary.get('average_confidence', 0):.2f}")
        print(f"   High confidence: {summary.get('high_confidence_count', 0)}")
        print(f"   Biomni available: {summary.get('biomni_available', False)}")
        
        mechanism_dist = summary.get('mechanism_distribution', {})
        if mechanism_dist:
            print(f"\n📊 Mechanism Distribution:")
            for mechanism, count in mechanism_dist.items():
                print(f"   • {mechanism.replace('_', ' ').title()}: {count}")


def display_next_steps():
    """Display next steps for the user."""
    print(f"\n🎯 NEXT STEPS & RECOMMENDATIONS")
    print("=" * 80)
    
    print("1. 📋 REVIEW DETAILED RESULTS:")
    print("   • wisteria_biomni_analysis_results.json - Complete file analysis")
    print("   • neurodegeneration_biomni_validation_results.json - Validation details")
    
    print("\n2. 🧬 FOR REAL BIOMNI INTEGRATION:")
    print("   • Install Biomni-compatible environment:")
    print("     conda create -n biomni-env python=3.9")
    print("     conda activate biomni-env")
    print("     pip install 'langchain==0.1.20' 'langchain-core==0.1.52' 'langgraph==0.1.19'")
    print("     pip install biomni")
    print("   • Enable Biomni in config/models.yaml")
    print("   • Re-run: python validate_neurodegeneration_hypotheses.py")
    
    print("\n3. 🔬 EXPERIMENTAL DESIGN:")
    print("   • Use mechanism-specific experimental suggestions")
    print("   • Plan research based on confidence scores")
    print("   • Consider hypothesis refinement for low-confidence results")
    
    print("\n4. 📈 FUTURE RESEARCH:")
    print("   • Apply this framework to new Wisteria sessions")
    print("   • Use validation insights for grant proposals")
    print("   • Integrate with laboratory planning workflows")


def main():
    """Main function to run the complete analysis workflow."""
    print("🧬 COMPLETE WISTERIA + BIOMNI ANALYSIS WORKFLOW")
    print("=" * 80)
    print("This script runs the complete analysis and validation pipeline")
    print("for your Wisteria JSON files with biomedical hypothesis validation.")
    print("=" * 80)
    
    # Track success of each step
    steps_completed = []
    
    # Step 1: Analyze all Wisteria files
    success = run_command(
        "python analyze_wisteria_biomni_needs.py",
        "Step 1: Analyzing Wisteria JSON files for Biomni validation needs"
    )
    steps_completed.append(("File Analysis", success))
    
    # Step 2: Validate neurodegeneration hypotheses
    success = run_command(
        "python validate_neurodegeneration_hypotheses.py",
        "Step 2: Validating neurodegeneration hypotheses with specialized Biomni analysis"
    )
    steps_completed.append(("Neurodegeneration Validation", success))
    
    # Step 3: Run general Wisteria JSON test (optional)
    success = run_command(
        "python test_wisteria_json_biomni.py",
        "Step 3: Running comprehensive Wisteria JSON + Biomni integration test"
    )
    steps_completed.append(("General Integration Test", success))
    
    # Display workflow summary
    print(f"\n🎉 WORKFLOW COMPLETION SUMMARY")
    print("=" * 80)
    
    successful_steps = 0
    for step_name, step_success in steps_completed:
        status = "✅ SUCCESS" if step_success else "❌ FAILED"
        print(f"{status}: {step_name}")
        if step_success:
            successful_steps += 1
    
    print(f"\nSteps completed successfully: {successful_steps}/{len(steps_completed)}")
    
    if successful_steps == len(steps_completed):
        print("🎉 All steps completed successfully!")
    elif successful_steps > 0:
        print("⚠️  Some steps completed - check individual results")
    else:
        print("❌ Workflow failed - check error messages above")
    
    # Display summary from generated files
    display_summary_from_files()
    
    # Display next steps
    display_next_steps()
    
    print(f"\n🕒 Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return successful_steps == len(steps_completed)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

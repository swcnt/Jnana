#!/usr/bin/env python3
"""
Test Agent States and Datasets Population.

This script tests whether agent states and datasets are being properly
populated in the ProtoGnosis system.
"""

import asyncio
import json
import time
from pathlib import Path
import sys

# Add the jnana package to the path
sys.path.insert(0, str(Path(__file__).parent))

from jnana.core.jnana_system import JnanaSystem


async def test_agent_states_and_datasets():
    """Test that agent states and datasets are properly populated."""
    
    print("🧪 Testing Agent States and Datasets Population")
    print("=" * 60)
    
    # Initialize Jnana system
    print("\n🚀 Step 1: Initializing Jnana System...")
    
    # Create a simple config file if it doesn't exist
    config_path = Path("config/models.yaml")
    if not config_path.exists():
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, 'w') as f:
            f.write("""# Simple configuration for testing
default:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.7
  max_tokens: 1024
""")
    
    jnana = JnanaSystem(
        config_path=config_path,
        storage_path="./test_agent_states_session.json",
        storage_type="json",
        enable_ui=False
    )
    
    try:
        await jnana.start()
        print("   ✅ Jnana system started")
        
        # Set research goal
        print("\n🎯 Step 2: Setting Research Goal...")
        research_goal = "Test research goal for agent state tracking"
        session_id = await jnana.set_research_goal(research_goal)
        print(f"   📋 Research goal set: {session_id[:8]}...")
        
        # Generate a single hypothesis to trigger agent activity
        print("\n🤖 Step 3: Generating Hypothesis to Trigger Agent Activity...")
        hypothesis = await jnana.generate_single_hypothesis("literature_exploration")
        print(f"   📝 Generated: {hypothesis.title}")
        
        # Wait a moment for all processing to complete
        await asyncio.sleep(2)
        
        # Check the session file for agent states and datasets
        print("\n📊 Step 4: Checking Session File...")
        session_file = Path("test_agent_states_session.json")
        
        if session_file.exists():
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            print(f"   📁 Session file exists: {session_file}")
            print(f"   📋 Session structure:")
            
            # Check main sections
            for key in session_data.keys():
                if isinstance(session_data[key], dict):
                    print(f"      {key}: {len(session_data[key])} items")
                elif isinstance(session_data[key], list):
                    print(f"      {key}: {len(session_data[key])} items")
                else:
                    print(f"      {key}: {type(session_data[key])}")
            
            # Check agent states
            agent_states = session_data.get('agent_states', {})
            print(f"\n   🤖 Agent States ({len(agent_states)} agents):")
            for agent_id, state in agent_states.items():
                print(f"      {agent_id}:")
                print(f"         Type: {state.get('agent_type', 'Unknown')}")
                print(f"         Status: {state.get('status', 'Unknown')}")
                print(f"         Tasks Completed: {state.get('total_tasks_completed', 0)}")
                print(f"         Last Activity: {time.ctime(state.get('last_activity', 0))}")
                
                # Show agent-specific metrics
                if state.get('agent_type') == 'generation':
                    print(f"         Hypotheses Generated: {state.get('hypotheses_generated', 0)}")
                    print(f"         Last Strategy: {state.get('last_strategy', 'None')}")
                elif state.get('agent_type') == 'reflection':
                    print(f"         Reviews Completed: {state.get('reviews_completed', 0)}")
                elif state.get('agent_type') == 'ranking':
                    print(f"         Rankings Completed: {state.get('rankings_completed', 0)}")
            
            # Check datasets
            datasets = session_data.get('datasets', {})
            print(f"\n   📊 Datasets ({len(datasets)} datasets):")
            for dataset_id, dataset in datasets.items():
                print(f"      {dataset_id}:")
                print(f"         Agent: {dataset.get('agent_id', 'Unknown')}")
                print(f"         Task: {dataset.get('task_id', 'Unknown')}")
                print(f"         Time: {time.ctime(dataset.get('generation_time', dataset.get('review_time', dataset.get('ranking_time', 0))))}")
                
                # Show dataset-specific metrics
                metrics = dataset.get('output_quality_metrics', {})
                if metrics:
                    print(f"         Quality Metrics:")
                    for metric, value in metrics.items():
                        print(f"            {metric}: {value}")
            
            # Check hypotheses (can be dict or list)
            hypotheses = session_data.get('hypotheses', {})
            if isinstance(hypotheses, dict):
                hypotheses_list = list(hypotheses.values())
                hypotheses_count = len(hypotheses)
            else:
                hypotheses_list = hypotheses
                hypotheses_count = len(hypotheses)

            print(f"\n   💡 Hypotheses ({hypotheses_count} hypotheses):")
            for i, hyp in enumerate(hypotheses_list[:5]):  # Show first 5
                if isinstance(hyp, dict):
                    hyp_id = hyp.get('hypothesis_id', f'hyp_{i}')
                    print(f"      {hyp_id}:")
                    print(f"         Agent: {hyp.get('agent_id', 'Unknown')}")
                    print(f"         Strategy: {hyp.get('metadata', {}).get('strategy', 'Unknown')}")
                    print(f"         Created: {time.ctime(hyp.get('created_at', 0))}")
                else:
                    print(f"      Hypothesis {i}: {type(hyp)} - {str(hyp)[:50]}...")
            
            # Summary
            print(f"\n📈 Summary:")
            print(f"   Agent States: {len(agent_states)} ({'✅ POPULATED' if agent_states else '❌ EMPTY'})")
            print(f"   Datasets: {len(datasets)} ({'✅ POPULATED' if datasets else '❌ EMPTY'})")
            print(f"   Hypotheses: {hypotheses_count} ({'✅ POPULATED' if hypotheses_count > 0 else '❌ EMPTY'})")
            
            # Check if we have the expected data
            success = len(agent_states) > 0 and len(datasets) > 0 and hypotheses_count > 0
            
            if success:
                print("\n🎉 SUCCESS: Agent states and datasets are being properly populated!")
            else:
                print("\n❌ ISSUE: Some data is missing. Check the implementation.")
                
            return success
        else:
            print("   ❌ Session file not found")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await jnana.stop()
        print("\n🛑 Jnana system stopped")


async def show_detailed_session_structure():
    """Show the detailed structure of the session file."""
    
    session_file = Path("test_agent_states_session.json")
    if not session_file.exists():
        print("❌ No session file found. Run the test first.")
        return
    
    print("\n📋 Detailed Session File Structure")
    print("=" * 50)
    
    try:
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        def print_structure(data, indent=0):
            """Recursively print the structure of the data."""
            prefix = "  " * indent
            
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        print(f"{prefix}{key}: {type(value).__name__} ({len(value)} items)")
                        if len(value) > 0:
                            print_structure(value, indent + 1)
                    else:
                        print(f"{prefix}{key}: {type(value).__name__} = {str(value)[:50]}...")
            elif isinstance(data, list):
                for i, item in enumerate(data[:3]):  # Show first 3 items
                    print(f"{prefix}[{i}]: {type(item).__name__}")
                    if isinstance(item, (dict, list)):
                        print_structure(item, indent + 1)
                if len(data) > 3:
                    print(f"{prefix}... and {len(data) - 3} more items")
        
        print_structure(session_data)
        
    except Exception as e:
        print(f"❌ Error reading session: {e}")


def main():
    """Main function to run the test."""
    
    import argparse
    parser = argparse.ArgumentParser(description="Test Agent States and Datasets")
    parser.add_argument("--show-structure", action="store_true", 
                       help="Show detailed structure of session file")
    
    args = parser.parse_args()
    
    if args.show_structure:
        asyncio.run(show_detailed_session_structure())
    else:
        success = asyncio.run(test_agent_states_and_datasets())
        exit(0 if success else 1)


if __name__ == "__main__":
    main()

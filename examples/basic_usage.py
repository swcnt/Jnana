#!/usr/bin/env python3
"""
Basic usage example for Jnana system.

This example demonstrates how to use Jnana for interactive hypothesis generation.
"""

import asyncio
import logging
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from jnana import JnanaSystem
from jnana.utils import setup_logging


async def basic_interactive_example():
    """Basic interactive example."""
    print("=== Jnana Basic Interactive Example ===\n")
    
    # Setup logging
    setup_logging(level="INFO")
    
    # Initialize Jnana system
    config_path = Path(__file__).parent.parent / "config" / "models.example.yaml"
    
    jnana = JnanaSystem(
        config_path=config_path,
        storage_path="examples/data/basic_example.json",
        storage_type="json",
        enable_ui=True
    )
    
    try:
        # Start the system
        await jnana.start()
        
        # Set research goal
        research_goal = """
        How can we develop more effective treatments for neurodegenerative diseases
        by targeting protein misfolding mechanisms?
        """
        
        session_id = await jnana.set_research_goal(research_goal)
        print(f"Created session: {session_id}")
        
        # Generate a single hypothesis
        print("\nGenerating initial hypothesis...")
        hypothesis = await jnana.generate_single_hypothesis("literature_exploration")
        
        print(f"Generated hypothesis: {hypothesis.title}")
        print(f"Description: {hypothesis.description}")
        
        # Refine the hypothesis with feedback
        print("\nRefining hypothesis with feedback...")
        feedback = "Please make the hypothesis more specific to Alzheimer's disease and include potential drug targets."
        
        refined_hypothesis = await jnana.refine_hypothesis(hypothesis, feedback)
        
        print(f"Refined hypothesis: {refined_hypothesis.title}")
        print(f"Updated description: {refined_hypothesis.description}")
        print(f"Version: {refined_hypothesis.version_string}")
        
        # Show system status
        status = jnana.get_system_status()
        print(f"\nSystem Status:")
        print(f"- Mode: {status['mode']}")
        print(f"- Session: {status['session']['session_id'] if status['session'] else 'None'}")
        print(f"- Hypotheses: {status['session']['hypotheses_count'] if status['session'] else 0}")
        
    finally:
        # Stop the system
        await jnana.stop()


async def batch_processing_example():
    """Example of batch processing mode."""
    print("=== Jnana Batch Processing Example ===\n")
    
    # Setup logging
    setup_logging(level="INFO")
    
    # Initialize Jnana system
    config_path = Path(__file__).parent.parent / "config" / "models.example.yaml"
    
    jnana = JnanaSystem(
        config_path=config_path,
        storage_path="examples/data/batch_example.json",
        storage_type="json",
        enable_ui=False  # No UI for batch mode
    )
    
    try:
        # Start the system
        await jnana.start()
        
        # Set research goal
        research_goal = """
        What are novel approaches to renewable energy storage that could
        address the intermittency problem of solar and wind power?
        """
        
        await jnana.set_research_goal(research_goal)
        
        # Run batch processing
        print("Running batch processing...")
        print("Note: This requires ProtoGnosis to be available")
        
        try:
            await jnana.run_batch_mode(
                hypothesis_count=10,
                strategies=["literature_exploration", "scientific_debate"],
                tournament_matches=15
            )
            
            print("Batch processing completed successfully!")
            
        except Exception as e:
            print(f"Batch processing failed (ProtoGnosis may not be available): {e}")
            
            # Fallback: generate hypotheses individually
            print("Falling back to individual generation...")
            
            for i in range(3):
                hypothesis = await jnana.generate_single_hypothesis("literature_exploration")
                print(f"{i+1}. {hypothesis.title}")
        
    finally:
        await jnana.stop()


async def data_migration_example():
    """Example of data migration between formats."""
    print("=== Jnana Data Migration Example ===\n")
    
    from jnana.data.data_migration import DataMigration
    from jnana.data.unified_hypothesis import UnifiedHypothesis
    
    # Create sample Wisteria-format data
    wisteria_data = {
        "title": "Sample Wisteria Hypothesis",
        "description": "This is a sample hypothesis in Wisteria format for testing migration.",
        "experimental_validation": "Conduct controlled experiments with proper controls.",
        "hallmarks": {
            "testability": "This hypothesis can be tested through controlled experiments.",
            "specificity": "The hypothesis is specific to the research domain.",
            "grounded_knowledge": "Based on existing literature and research.",
            "predictive_power": "Provides clear predictions for experimental outcomes.",
            "parsimony": "Simple and elegant explanation of the phenomenon."
        },
        "references": [
            {
                "citation": "Smith, J. (2024). Research Methods. Journal of Science, 1(1), 1-10.",
                "annotation": "Provides methodological foundation for the hypothesis."
            }
        ],
        "feedback_history": [
            {
                "feedback": "Please make the hypothesis more specific.",
                "timestamp": "2024-01-15T10:30:00",
                "version_before": "1.0",
                "version_after": "1.1"
            }
        ],
        "version": "1.1",
        "type": "improvement",
        "hypothesis_number": 1
    }
    
    # Convert to unified format
    print("Converting Wisteria data to unified format...")
    unified_hypothesis = DataMigration.from_wisteria(wisteria_data)
    
    print(f"Unified hypothesis: {unified_hypothesis.title}")
    print(f"Version: {unified_hypothesis.version_string}")
    print(f"Feedback entries: {len(unified_hypothesis.feedback_history)}")
    print(f"References: {len(unified_hypothesis.references)}")
    
    # Convert back to Wisteria format
    print("\nConverting back to Wisteria format...")
    converted_back = unified_hypothesis.to_wisteria_format()
    
    print(f"Converted title: {converted_back['title']}")
    print(f"Converted version: {converted_back['version']}")
    
    # Convert to ProtoGnosis format
    print("\nConverting to ProtoGnosis format...")
    protognosis_format = unified_hypothesis.to_protognosis_format()
    
    print(f"ProtoGnosis content: {protognosis_format['content'][:100]}...")
    print(f"ProtoGnosis metadata: {list(protognosis_format['metadata'].keys())}")


async def configuration_example():
    """Example of configuration management."""
    print("=== Jnana Configuration Example ===\n")
    
    from jnana.core.model_manager import UnifiedModelManager
    
    config_path = Path(__file__).parent.parent / "config" / "models.example.yaml"
    
    if not config_path.exists():
        print(f"Configuration file not found: {config_path}")
        print("Please copy models.example.yaml to models.yaml and configure your API keys.")
        return
    
    # Initialize model manager
    model_manager = UnifiedModelManager(config_path)
    
    # Show available models
    print("Available models:")
    models = model_manager.list_available_models()
    
    for category, model_list in models.items():
        print(f"\n{category.upper()}:")
        for model in model_list:
            print(f"  - {model}")
    
    # Get model configurations
    print("\nModel configurations:")
    
    # Interactive model
    interactive_model = model_manager.get_interactive_model()
    print(f"Interactive model: {interactive_model.provider}:{interactive_model.model}")
    
    # Agent models
    generation_model = model_manager.get_model_for_agent("generation")
    print(f"Generation agent: {generation_model.provider}:{generation_model.model}")
    
    # Task models
    refinement_model = model_manager.get_task_model("hypothesis_refinement")
    print(f"Refinement task: {refinement_model.provider}:{refinement_model.model}")
    
    # Validate configuration
    print("\nValidating configuration...")
    errors = model_manager.validate_configuration()
    
    if errors:
        print("Configuration errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration is valid!")


async def main():
    """Run all examples."""
    examples = [
        ("Basic Interactive", basic_interactive_example),
        ("Batch Processing", batch_processing_example),
        ("Data Migration", data_migration_example),
        ("Configuration", configuration_example)
    ]
    
    for name, example_func in examples:
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print(f"{'='*60}")
        
        try:
            await example_func()
        except Exception as e:
            print(f"Example failed: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n{name} completed.")
        
        # Wait for user input to continue
        input("\nPress Enter to continue to next example...")


if __name__ == "__main__":
    asyncio.run(main())

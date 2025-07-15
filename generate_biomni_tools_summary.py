#!/usr/bin/env python3
"""
Script to generate a detailed summary of Biomni tools used for hypotheses.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add current directory for imports
sys.path.insert(0, '.')

from enhanced_biomni_hypothesis_validation import EnhancedBiomniValidator
from jnana.core.jnana_system import JnanaSystem
from hypothesis_validation_suite import HypothesisParser

async def generate_tool_summary():
    print("🛠️ Generating Biomni Tools Summary")
    print("=" * 60)
    
    # Initialize Jnana system
    jnana = JnanaSystem(config_path='config/models.yaml')
    await jnana.start()
    
    # Create enhanced validator
    validator = EnhancedBiomniValidator(jnana)
    
    # Parse hypotheses
    parser = HypothesisParser('./hypothesis_extraction.txt')
    hypotheses = parser.parse_file()
    
    # Header for summary
    summary_report = ["# Biomni Tools Analysis Summary\n", "Generated: " + str(datetime.now()) + "\n"]
    
    # Process each hypothesis
    for i, hypothesis in enumerate(hypotheses[:5], 1):  # Limit to first 5 for demonstration
        print(f"\n🧪 Processing Hypothesis {i}: {hypothesis['title'][:60]}...")
        
        # Analyze tools
        tools = await validator.analyze_biomni_tools_for_hypothesis(hypothesis['description'])
        
        # Add to summary
        summary_report.append(f"\n## Hypothesis {i}: {hypothesis['title']}\n")
        
        for tool in tools:
            summary_report.append(f"- **Tool Name:** {tool.tool_name}")
            summary_report.append(f"  - Description: {tool.description}")
            summary_report.append(f"  - Input: {tool.input_data}")
            summary_report.append(f"  - Output: {tool.output_format}")
            summary_report.append(f"  - Confidence Method: {tool.confidence_method}")
            summary_report.append(f"  - Evidence Sources: {', '.join(tool.evidence_sources)}")
            summary_report.append(f"  - Experimental Suggestions: {', '.join(tool.experimental_suggestions[:2])}...")
            summary_report.append(f"  - Biological Domains: {', '.join(tool.biological_domains)}")
            summary_report.append("")
        summary_report.append("--\n")
    
    # Save summary to file
    with open('biomni_tools_summary.md', 'w') as f:
        f.write("\n".join(summary_report))
        
    await jnana.stop()
    print("\n✅ Summary generated and saved to biomni_tools_summary.md")

if __name__ == "__main__":
    asyncio.run(generate_tool_summary())

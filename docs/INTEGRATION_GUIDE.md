# Jnana Integration Guide

This guide explains how Jnana integrates Wisteria's interactive capabilities with ProtoGnosis's multi-agent system.

## Architecture Overview

Jnana follows a layered architecture that bridges two powerful systems:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
├─────────────────────────────────────────────────────────────┤
│  Interactive Interface  │  Monitoring Interface  │   CLI   │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Integration Layer                         │
├─────────────────────────────────────────────────────────────┤
│  Unified Model Manager  │  Session Manager  │ Event Manager │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                 Core Processing Layer                       │
├─────────────────────────────────────────────────────────────┤
│     ProtoGnosis Multi-Agent System     │  Wisteria Components│
│  ┌─────────────────────────────────┐   │  ┌─────────────────┐│
│  │ Supervisor │ Generation │ etc.  │   │  │ Hypothesis Gen  ││
│  └─────────────────────────────────┘   │  │ Feedback Track  ││
│                                        │  │ Scientific Eval ││
│                                        │  └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                             │
├─────────────────────────────────────────────────────────────┤
│    Unified Data Store    │   Context Memory   │ Tournament  │
└─────────────────────────────────────────────────────────────┘
```

## Key Integration Components

### 1. Unified Data Model

The `UnifiedHypothesis` class serves as the bridge between Wisteria and ProtoGnosis data formats:

```python
from jnana.data.unified_hypothesis import UnifiedHypothesis

# Create a hypothesis that works with both systems
hypothesis = UnifiedHypothesis(
    title="Novel Cancer Treatment Approach",
    description="Detailed hypothesis description...",
    experimental_validation="Experimental plan..."
)

# Add Wisteria-style feedback
hypothesis.add_feedback("Please make more specific to breast cancer")

# Add ProtoGnosis-style tournament record
hypothesis.update_tournament_record(won=True, opponent_id="hyp_002")

# Convert to either format
wisteria_format = hypothesis.to_wisteria_format()
protognosis_format = hypothesis.to_protognosis_format()
```

### 2. Unified Model Manager

Manages LLM configurations for both systems:

```python
from jnana.core.model_manager import UnifiedModelManager

manager = UnifiedModelManager("config/models.yaml")

# Get model for ProtoGnosis agent
generation_model = manager.get_model_for_agent("generation")

# Get model for Wisteria-style interaction
interactive_model = manager.get_interactive_model()

# Get model for specific task
refinement_model = manager.get_task_model("hypothesis_refinement")
```

### 3. Event-Driven Communication

The event system enables loose coupling between components:

```python
from jnana.core.event_manager import EventManager, EventType

event_manager = EventManager()

# Subscribe to hypothesis events
def handle_hypothesis_generated(event):
    print(f"New hypothesis: {event.data['title']}")

event_manager.subscribe(EventType.HYPOTHESIS_GENERATED, handle_hypothesis_generated)

# Publish events
await event_manager.publish(
    EventType.HYPOTHESIS_GENERATED,
    source="generation_agent",
    data={"hypothesis_id": "hyp_001", "title": "New Hypothesis"}
)
```

## Integration Patterns

### Pattern 1: Interactive Generation with Automated Refinement

```python
async def interactive_with_automation():
    jnana = JnanaSystem(config_path="config/models.yaml")
    await jnana.start()
    
    # Set research goal
    await jnana.set_research_goal("How can we improve solar cell efficiency?")
    
    # Generate initial hypothesis interactively
    hypothesis = await jnana.generate_single_hypothesis("literature_exploration")
    
    # User provides feedback through UI
    refined = await jnana.refine_hypothesis(hypothesis, "Focus on perovskite materials")
    
    # Automated evaluation using ProtoGnosis agents
    if jnana.coscientist:
        # Run tournament evaluation
        await jnana.run_batch_mode(hypothesis_count=5, tournament_matches=10)
```

### Pattern 2: Batch Processing with Interactive Review

```python
async def batch_with_review():
    jnana = JnanaSystem(config_path="config/models.yaml", enable_ui=True)
    await jnana.start()
    
    # Batch generate hypotheses
    await jnana.run_batch_mode(hypothesis_count=20)
    
    # Interactive review of top hypotheses
    await jnana.ui.start_refinement_session()
    
    # Final automated ranking
    if jnana.coscientist:
        jnana.coscientist.run_tournament(match_count=50)
```

### Pattern 3: Hybrid Workflow

```python
async def hybrid_workflow():
    jnana = JnanaSystem(config_path="config/models.yaml")
    await jnana.start()
    
    # Combined approach
    await jnana.run_hybrid_mode(
        hypothesis_count=10,
        interactive_refinement=True,
        tournament_matches=25
    )
```

## Data Migration

Jnana provides seamless migration between formats:

### From Wisteria to Jnana

```python
from jnana.data.data_migration import DataMigration

# Load Wisteria session
wisteria_hypotheses = DataMigration.load_wisteria_session("wisteria_session.json")

# Convert to unified format
unified_hypotheses = [DataMigration.from_wisteria(h) for h in wisteria_hypotheses]

# Save as Jnana session
DataMigration.save_unified_session(unified_hypotheses, "jnana_session.json")
```

### From ProtoGnosis to Jnana

```python
# Load ProtoGnosis session
protognosis_hypotheses = DataMigration.load_protognosis_session("protognosis_session.json")

# Already converted to unified format
# Save as Jnana session
DataMigration.save_unified_session(protognosis_hypotheses, "jnana_session.json")
```

## Configuration Integration

Jnana uses a unified configuration format that supports both systems:

```yaml
# config/models.yaml
default:
  provider: "openai"
  model: "gpt-4o"
  api_key: "${OPENAI_API_KEY}"

# ProtoGnosis agent configurations
agents:
  generation:
    provider: "openai"
    model: "gpt-4o"
    temperature: 0.8
  
  reflection:
    provider: "anthropic"
    model: "claude-3-5-sonnet-20241022"
    temperature: 0.6

# Wisteria interactive configurations
interactive:
  primary:
    provider: "openai"
    model: "gpt-4o"
    temperature: 0.7
  
  alternative:
    provider: "anthropic"
    model: "claude-3-5-sonnet-20241022"
    temperature: 0.7

# Task-specific configurations
tasks:
  hypothesis_generation:
    provider: "openai"
    model: "gpt-4o"
    temperature: 0.8
  
  hypothesis_refinement:
    provider: "anthropic"
    model: "claude-3-5-sonnet-20241022"
    temperature: 0.6
```

## Deployment Modes

### Mode 1: Interactive Research Session

Best for: Exploratory research, hypothesis refinement, real-time collaboration

```bash
python jnana.py --mode interactive --goal "Your research question"
```

Features:
- Real-time hypothesis generation
- Interactive feedback and refinement
- Wisteria-style UI with multi-pane layout
- Session persistence and resumption

### Mode 2: Batch Processing

Best for: Large-scale hypothesis generation, systematic evaluation

```bash
python jnana.py --mode batch --goal "Your research question" --count 50
```

Features:
- Automated hypothesis generation
- Tournament-based evaluation
- Scalable processing with multiple agents
- Comprehensive result analysis

### Mode 3: Hybrid Workflow

Best for: Combining automated generation with human insight

```bash
python jnana.py --mode hybrid --goal "Your research question" --interactive-refinement
```

Features:
- Initial batch generation
- Interactive refinement phase
- Final automated evaluation
- Best of both approaches

## Performance Considerations

### Scalability

- **Concurrent Processing**: Configure `max_concurrent_requests` in config
- **Memory Management**: Use SQLite storage for large datasets
- **Rate Limiting**: Built-in rate limiting for API calls

### Optimization Tips

1. **Model Selection**: Use faster models for initial generation, more capable models for refinement
2. **Batch Sizes**: Optimize batch sizes based on available resources
3. **Caching**: Enable caching for repeated operations
4. **Storage**: Choose appropriate storage backend (JSON for small datasets, SQLite for large)

## Troubleshooting

### Common Issues

1. **API Key Configuration**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   export ANTHROPIC_API_KEY="your-key-here"
   ```

2. **ProtoGnosis Integration**
   - Ensure ProtoGnosis is installed and accessible
   - Check import paths and dependencies

3. **Wisteria UI Issues**
   - Verify terminal compatibility for curses interface
   - Fall back to basic text interface if needed

### Debug Mode

```bash
python jnana.py --debug --log-file debug.log
```

## Extension Points

Jnana is designed to be extensible:

### Custom Agents

```python
from jnana.agents.interactive_agent_wrapper import InteractiveAgentWrapper

class CustomAgent(InteractiveAgentWrapper):
    async def process_task_interactive(self, task, allow_user_input=True):
        # Custom processing logic
        pass
```

### Custom UI Components

```python
from jnana.ui.interactive_interface import InteractiveInterface

class CustomInterface(InteractiveInterface):
    async def start_interactive_session(self, model_config):
        # Custom UI implementation
        pass
```

### Custom Storage Backends

```python
from jnana.data.storage import JnanaStorage

class CustomStorage(JnanaStorage):
    def save_hypothesis(self, hypothesis):
        # Custom storage implementation
        pass
```

This integration guide provides the foundation for understanding and extending Jnana's capabilities. The system is designed to grow with your research needs while maintaining compatibility with both Wisteria and ProtoGnosis ecosystems.

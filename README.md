# Jnana: AI Co-Scientist with Interactive Hypothesis Generation

Jnana (Sanskrit: ज्ञान, meaning "knowledge" or "wisdom") is an integrated AI co-scientist platform that combines the interactive capabilities of Wisteria with the scalable multi-agent system of ProtoGnosis.

## Overview

Jnana provides researchers with:
- **Interactive Hypothesis Generation**: Real-time hypothesis creation and refinement
- **Multi-Agent Processing**: Scalable automated hypothesis evaluation and ranking
- **Scientific Rigor**: Comprehensive evaluation against established scientific criteria
- **Flexible Deployment**: Support for interactive, batch, and hybrid workflows

## Architecture

Jnana integrates two powerful systems:
- **Wisteria**: Interactive terminal-based hypothesis generation with real-time feedback
- **ProtoGnosis**: Multi-agent system for scalable research hypothesis processing

## Key Features

### Interactive Capabilities (from Wisteria)
- Professional curses-based multi-pane interface
- Real-time hypothesis refinement with user feedback
- Scientific hallmarks evaluation (testability, specificity, etc.)
- Professional PDF export with comprehensive documentation
- Session management and version tracking

### Scalable Processing (from ProtoGnosis)
- Multi-agent system with specialized roles
- Tournament-based hypothesis ranking
- Support for multiple LLM providers
- Asynchronous processing for large datasets
- Comprehensive research workflow automation

### Unified Features (Jnana Integration)
- Seamless switching between interactive and automated modes
- Unified data model supporting both systems
- Combined evaluation framework
- Enhanced model management
- Comprehensive research session documentation

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd Jnana

# Install dependencies
pip install -r requirements.txt

# Configure models
cp config/models.example.yaml config/models.yaml
# Edit config/models.yaml with your API keys and model preferences
```

## Quick Start

### Interactive Mode
```bash
python jnana.py --mode interactive --goal "Your research question here"
```

### Batch Processing Mode
```bash
python jnana.py --mode batch --goal "Your research question here" --count 20
```

### Hybrid Mode
```bash
python jnana.py --mode hybrid --goal "Your research question here" --interactive-refinement
```

## Project Structure

```
Jnana/
├── jnana/                    # Core Jnana package
│   ├── core/                 # Core integration components
│   ├── data/                 # Unified data models
│   ├── ui/                   # User interface components
│   ├── agents/               # Agent wrappers and extensions
│   └── utils/                # Utility functions
├── config/                   # Configuration files
├── tests/                    # Test suite
├── docs/                     # Documentation
├── examples/                 # Example usage scripts
└── scripts/                  # Utility scripts
```

## Development Status

This project is currently in Phase 1 development, focusing on:
- [x] Repository structure setup
- [ ] Unified data model implementation
- [ ] Model configuration integration
- [ ] Core integration framework
- [ ] Basic UI integration

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

[License information to be added]

## Acknowledgments

- **Wisteria**: Interactive hypothesis generation system by Rick Stevens AI
- **ProtoGnosis**: Multi-agent AI co-scientist system

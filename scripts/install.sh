#!/bin/bash

# Jnana Installation Script

set -e

echo "=== Jnana Installation Script ==="

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.9 or higher is required. Found: $python_version"
    exit 1
fi

echo "✓ Python version check passed: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install Jnana in development mode
echo "Installing Jnana in development mode..."
pip install -e .

# Create necessary directories
echo "Creating directories..."
mkdir -p data sessions logs config

# Copy example configuration if config doesn't exist
if [ ! -f "config/models.yaml" ]; then
    echo "Copying example configuration..."
    cp config/models.example.yaml config/models.yaml
    echo "⚠️  Please edit config/models.yaml with your API keys"
fi

# Run basic tests
echo "Running basic tests..."
python -m pytest tests/ -v || echo "⚠️  Some tests failed (this may be expected if API keys are not configured)"

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit config/models.yaml with your API keys"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run Jnana: python jnana.py --help"
echo "4. Try the examples: python examples/basic_usage.py"
echo ""
echo "For more information, see README.md"

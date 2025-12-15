#!/bin/bash

# Documentation generation script for OSGenome
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the project root
if [ ! -f "pyproject.toml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if development dependencies are installed
print_status "Checking development dependencies..."
if ! uv run python -c "import sphinx" 2>/dev/null; then
    print_warning "Sphinx not found. Installing development dependencies..."
    uv sync --group dev
fi

# Create docs directory if it doesn't exist
mkdir -p docs/_static docs/_templates

print_status "Generating API documentation..."
cd docs

# Generate API documentation
print_status "Running sphinx-apidoc..."
uv run sphinx-apidoc -o api ../SNPedia --force --module-first

# Build HTML documentation
print_status "Building HTML documentation..."
uv run sphinx-build -b html . _build/html

# Check for warnings and errors
if [ $? -eq 0 ]; then
    print_success "Documentation built successfully!"
    print_status "Documentation available at: docs/_build/html/index.html"

    # Optionally open in browser
    if command -v python3 &> /dev/null; then
        read -p "Open documentation in browser? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python3 -m webbrowser "file://$(pwd)/_build/html/index.html"
        fi
    fi
else
    print_error "Documentation build failed!"
    exit 1
fi

# Generate coverage report
print_status "Generating documentation coverage report..."
uv run sphinx-build -b coverage . _build/coverage

if [ -f "_build/coverage/python.txt" ]; then
    print_status "Documentation coverage report:"
    cat _build/coverage/python.txt
fi

# Check for broken links (optional)
read -p "Check for broken links? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Checking for broken links..."
    uv run sphinx-build -b linkcheck . _build/linkcheck
fi

print_success "Documentation generation complete!"
print_status "Next steps:"
echo "  - Review the generated documentation at docs/_build/html/index.html"
echo "  - Check the coverage report for missing docstrings"
echo "  - Update any broken links found during link checking"
echo "  - Consider setting up automated documentation deployment"

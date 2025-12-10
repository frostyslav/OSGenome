#!/bin/bash

# Type checking script for OSGenome
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

# Check if mypy is installed
print_status "Checking mypy installation..."
if ! uv run python -c "import mypy" 2>/dev/null; then
    print_warning "MyPy not found. Installing development dependencies..."
    uv sync --group dev
fi

# Run type checking
print_status "Running type checking with mypy..."
echo "Checking SNPedia package..."

# Run mypy on the main package
if uv run mypy SNPedia/; then
    print_success "Type checking passed!"
    
    # Generate type checking report
    print_status "Generating detailed type checking report..."
    uv run mypy SNPedia/ --html-report mypy-report --txt-report mypy-report
    
    if [ -d "mypy-report" ]; then
        print_status "Type checking report generated at: mypy-report/index.html"
    fi
    
else
    print_error "Type checking failed!"
    print_status "Common issues and solutions:"
    echo "  - Missing type hints: Add type annotations to function parameters and return values"
    echo "  - Import errors: Check that all imports are correct and modules exist"
    echo "  - Third-party library issues: Add ignore_missing_imports to mypy.ini"
    echo "  - Optional types: Use Optional[Type] for values that can be None"
    exit 1
fi

# Optional: Check specific files or directories
if [ $# -gt 0 ]; then
    print_status "Running type checking on specified files/directories..."
    for target in "$@"; do
        print_status "Checking $target..."
        uv run mypy "$target"
    done
fi

print_success "Type checking complete!"
print_status "Next steps:"
echo "  - Review any warnings or errors above"
echo "  - Add missing type hints to improve code quality"
echo "  - Consider using stricter mypy settings for better type safety"
echo "  - Integrate type checking into your CI/CD pipeline"
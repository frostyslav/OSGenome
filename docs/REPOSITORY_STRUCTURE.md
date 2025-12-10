# Repository Structure Documentation

## Overview

OSGenome is a Flask-based web application for analyzing genetic data (SNPs) from services like Ancestry. The application processes genetic data locally, ensuring privacy, and fetches relevant information from SNPedia to help users understand their genome.

## Root Directory Structure

```
OSGenome/
├── SNPedia/              # Main application package
├── docs/                 # Documentation directory
│   ├── README.md         # Documentation index
│   ├── CONFIGURATION.md  # Configuration guide
│   ├── SECURITY.md       # Security documentation
│   ├── CACHING.md        # Performance and caching guide
│   ├── ERROR_HANDLING.md # Error handling and troubleshooting
│   ├── KEYBOARD_SHORTCUTS.md # Keyboard shortcuts guide
│   ├── REPOSITORY_STRUCTURE.md # This file
│   └── QUICK_REFERENCE.md # Quick reference guide
├── images/               # Documentation images and screenshots
├── .env.example          # Environment configuration template
├── .flake8.cfg          # Python linting configuration
├── .gitignore           # Git ignore rules
├── .pre-commit-config.yaml  # Pre-commit hooks configuration
├── Dockerfile           # Container configuration
├── pyproject.toml      # Python project configuration and dependencies
├── uv.lock             # Dependency lock file
├── requirements.txt     # Python dependencies (alternative to pyproject.toml)
├── tests/               # Test suite directory
│   ├── test_async_crawler.py    # Async crawler tests
│   ├── test_cache.py            # Caching system tests
│   ├── test_code_organization.py # Code structure tests
│   ├── test_configuration.py    # Configuration tests
│   ├── test_error_handling.py   # Error handling tests
│   ├── test_font_awesome.py     # Font Awesome integration tests
│   ├── test_keyboard_shortcuts.py # Keyboard shortcuts tests
│   └── test_security.py         # Security feature tests
├── README.md            # Main project documentation
└── LICENSE              # Project license
```

## SNPedia Package Structure

The `SNPedia/` directory contains the main application code organized into a modular architecture:

### Core Application Files

```
SNPedia/
├── __init__.py          # Package initialization
├── app.py               # Flask application entry point
├── data_crawler.py      # SNPedia data crawler with rate limiting
├── genome_importer.py   # Genetic data import and processing
└── gunicorn_config.py   # Production server configuration
```

### Core Module (`SNPedia/core/`)

Contains fundamental application components:

- `__init__.py` - Core module initialization
- `config.py` - Centralized configuration management
- `exceptions.py` - Custom exception classes
- `logger.py` - Logging configuration and utilities

### Utilities Module (`SNPedia/utils/`)

Reusable utility functions:

- `__init__.py` - Utils module initialization
- `file_utils.py` - File handling and validation
- `security.py` - Security utilities and input sanitization
- `validation.py` - Data validation functions

### Empty/Placeholder Modules

These directories are prepared for future expansion:

- `api/` - API endpoints (future REST API)
- `models/` - Data models (future database integration)
- `services/` - Business logic services (future service layer)

### Frontend Assets

```
SNPedia/
├── templates/           # HTML templates
│   └── snp_resource.html
├── css/                 # Stylesheets (Kendo UI)
│   ├── kendo-font-icons.css
│   ├── kendo-font-icons.ttf
│   ├── kendo.common-material.min.css
│   ├── kendo.material.min.css
│   └── kendo.material.mobile.min.css
├── js/                  # JavaScript libraries
│   ├── jquery.min.js
│   ├── jszip.min.js
│   └── kendo.all.min.js
└── images/              # Application images
    └── dna-body.png
```

### Data Directory (`data/`)

Runtime data storage:

- User genetic data files (generated at runtime)
- SNPedia crawled data (generated at runtime)
- `approved.json` - Cached list of approved SNPs from SNPedia

## Documentation Files

### Configuration Documentation

- **CONFIGURATION.md** - Comprehensive guide for environment setup, configuration options, and deployment settings
- **.env.example** - Template for environment variables including Flask settings, security keys, and rate limiting

### Security Documentation

- **SECURITY.md** - Security features, best practices, and vulnerability reporting
- **tests/test_security.py** - Security validation tests

### Error Handling

- **ERROR_HANDLING.md** - Error handling patterns and troubleshooting guide
- **tests/test_error_handling.py** - Error handling tests

### General Documentation

- **README.md** - Project overview, installation, and usage instructions
- **LICENSE** - Project licensing information

## Test Suite

Located in the `tests/` directory:

- `test_async_crawler.py` - Async crawler functionality tests
- `test_cache.py` - Caching system and performance tests
- `test_code_organization.py` - Code structure and organization tests
- `test_configuration.py` - Configuration validation tests
- `test_error_handling.py` - Error handling tests
- `test_font_awesome.py` - Font Awesome integration tests
- `test_keyboard_shortcuts.py` - Keyboard shortcuts functionality tests
- `test_security.py` - Security feature tests

## Images Directory

Contains screenshots and visual documentation:

- `OSGenome*.png` - Application screenshots
- `OSGenome_mp*.png` - Mobile/responsive screenshots
- `OSGenome_multixp.png` - Multi-platform demonstration

## Key Technologies

### Backend
- **Flask** - Web framework
- **BeautifulSoup** - Web scraping for SNPedia
- **Gunicorn** - Production WSGI server
- **Python 3.13+** - Programming language

### Frontend
- **Tabulator** - Grid component for data display with filtering, sorting, and Excel export
- **SheetJS** - Excel file generation library

### Development Tools
- **Flake8** - Python linting
- **Pre-commit hooks** - Code quality automation
- **Docker** - Containerization support

## Data Flow

1. **Import Phase** (`genome_importer.py`)
   - User provides Ancestry raw data file
   - Data is validated and parsed locally
   - SNP IDs are extracted

2. **Crawling Phase** (`data_crawler.py`)
   - Fetches SNP information from SNPedia API
   - Implements rate limiting to respect server resources
   - Stores data locally in `data/`

3. **Display Phase** (`app.py`)
   - Flask serves the web interface
   - Tabulator displays genetic data
   - Users can filter, export, and lookup SNPs

## Security Architecture

- **Input Validation** - All user inputs are sanitized (`utils/validation.py`)
- **Path Traversal Protection** - File operations are restricted (`utils/security.py`)
- **Rate Limiting** - Prevents abuse of SNPedia API
- **Local Processing** - No genetic data leaves the user's machine
- **Security Headers** - XSS and clickjacking protection
- **File Size Limits** - Prevents resource exhaustion

## Configuration Management

Configuration is centralized in `core/config.py` and can be customized via:

- Environment variables (`.env` file)
- Command-line arguments
- Default values with sensible security settings

## Future Architecture

The modular structure supports planned features:

- **API Module** - RESTful API for programmatic access
- **Models Module** - Database integration for persistent storage
- **Services Module** - Business logic separation from routes

## Development Workflow

1. Install dependencies: `uv sync`
2. Configure environment: Copy `.env.example` to `.env`
3. Run tests: `uv run python tests/test_*.py` or `uv run python -m pytest tests/`
4. Start development server: `uv run python SNPedia/app.py`
5. Access application: `http://127.0.0.1:5000`

## Production Deployment

- Use Gunicorn with configuration from `gunicorn_config.py`
- Set `FLASK_ENV=production`
- Configure secure `SECRET_KEY`
- Enable security headers
- Consider Docker deployment using provided `Dockerfile`

## Privacy & Data Storage

All genetic data is stored locally in the `data/` directory. The application:

- Never transmits genetic data to external servers
- Only fetches public SNP information from SNPedia
- Processes all data on the user's local machine
- Allows users to delete their data at any time

## Contributing

The project follows a modular architecture to facilitate contributions:

- Core functionality in `core/`
- Utilities in `utils/`
- Tests in root directory
- Documentation in markdown files

See the README.md for contributor acknowledgments and guidelines.

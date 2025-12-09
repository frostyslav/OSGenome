# Configuration Management

## Overview

OSGenome uses a centralized configuration system that supports multiple environments (development, production, testing) with validation and type-safe environment variable parsing.

## Configuration Files

### 1. `.env` - Environment Variables
Create from template:
```bash
cp .env.example .env
```

Edit `.env` to customize your configuration. **Never commit this file to version control.**

### 2. `SNPedia/config.py` - Configuration Classes
Defines configuration classes for different environments with validation.

## Environment Variables

### Flask Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `development` | Environment: development, production, testing |
| `FLASK_DEBUG` | `false` | Enable Flask debug mode (never in production) |
| `SECRET_KEY` | *random* | Secret key for sessions (required in production) |

### Logging

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level: DEBUG, INFO, WARNING, ERROR |

### File Upload Limits

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_CONTENT_LENGTH` | `16777216` | Max upload size in bytes (16MB) |
| `ALLOWED_EXTENSIONS` | `xlsx,xls` | Comma-separated allowed file extensions |

### Data Processing Limits

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_FILE_SIZE_IMPORT` | `104857600` | Max import file size in bytes (100MB) |
| `MAX_FILE_SIZE_LOAD` | `524288000` | Max JSON load size in bytes (500MB) |
| `MAX_LINE_COUNT` | `1000000` | Max lines to process in a file |

### Rate Limiting

| Variable | Default | Description |
|----------|---------|-------------|
| `RATELIMIT_ENABLED` | `true` | Enable rate limiting |
| `REQUEST_DELAY` | `1.0` | Seconds between SNPedia requests |
| `MAX_RETRIES` | `3` | Number of retry attempts |
| `RETRY_DELAY` | `5` | Seconds to wait before retry |
| `REQUEST_TIMEOUT` | `30` | Request timeout in seconds |

### Session Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SESSION_LIFETIME` | `3600` | Session lifetime in seconds (1 hour) |

### Data Directories

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_DIR` | `data` | Directory for data files |
| `BACKUP_DIR` | `data/backups` | Directory for backups |

### SNPedia Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SNPEDIA_BASE_URL` | `https://bots.snpedia.com` | SNPedia base URL |

### Progress Saving

| Variable | Default | Description |
|----------|---------|-------------|
| `SAVE_PROGRESS_INTERVAL` | `10` | Save progress every N requests |

### CORS

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `http://127.0.0.1:5000,http://localhost:5000` | Comma-separated allowed origins |

### Gunicorn (Production)

| Variable | Default | Description |
|----------|---------|-------------|
| `GUNICORN_PROCESSES` | `2` | Number of worker processes |
| `GUNICORN_THREADS` | `4` | Threads per worker |
| `GUNICORN_BIND` | `0.0.0.0:8080` | Host:port to bind |

## Configuration Environments

### Development

**Purpose:** Local development and testing

**Characteristics:**
- DEBUG mode enabled
- Faster rate limiting (0.5s delay)
- HTTP cookies allowed
- Detailed logging (DEBUG level)
- Random SECRET_KEY generated (with warning)

**Usage:**
```bash
export FLASK_ENV=development
python SNPedia/app.py
```

### Production

**Purpose:** Production deployment

**Characteristics:**
- DEBUG mode disabled
- Stricter rate limiting (1.0s delay)
- HTTPS-only cookies
- INFO level logging
- SECRET_KEY required from environment

**Usage:**
```bash
export FLASK_ENV=production
export SECRET_KEY=$(python -c "import os; print(os.urandom(32).hex())")
gunicorn --config SNPedia/gunicorn_config.py SNPedia.app:app
```

**Requirements:**
- SECRET_KEY must be set (at least 32 characters)
- DEBUG must be False
- HTTPS recommended

### Testing

**Purpose:** Automated testing

**Characteristics:**
- TESTING mode enabled
- Fast rate limiting (0.1s delay)
- Smaller file size limits
- Reduced retry attempts
- Short timeouts

**Usage:**
```bash
export FLASK_ENV=testing
python test_configuration.py
```

## Configuration API

### Get Configuration

```python
from config import get_config

# Get config for current environment
config = get_config()

# Get config for specific environment
config = get_config('production')
```

### Load Configuration into Flask

```python
from flask import Flask
from config import load_config

app = Flask(__name__)
config_class = load_config(app)
```

### Validate Configuration

```python
from config import DevelopmentConfig

validation = DevelopmentConfig.validate()

if validation['valid']:
    print("Configuration is valid")
else:
    print("Issues:", validation['issues'])
    print("Warnings:", validation['warnings'])
```

### Export Configuration (Non-Sensitive)

```python
from config import DevelopmentConfig

config_dict = DevelopmentConfig.to_dict()
# Returns dict without SECRET_KEY
```

## API Endpoints

### Health Check

```bash
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "data_loaded": true,
  "data_count": 20000,
  "config_valid": true,
  "config_warnings": [],
  "version": "2.0.0"
}
```

### Configuration Info

```bash
GET /api/config
```

**Response:**
```json
{
  "config": {
    "APP_NAME": "OSGenome",
    "APP_VERSION": "2.0.0",
    "MAX_CONTENT_LENGTH": 16777216,
    "ALLOWED_EXTENSIONS": ["xlsx", "xls"],
    "REQUEST_DELAY": 1.0,
    "MAX_RETRIES": 3
  },
  "environment": "development"
}
```

## Configuration Validation

The configuration system automatically validates settings on load:

### Validation Rules

1. **SECRET_KEY**
   - Must be set in production
   - Should be at least 32 characters
   - Warns if randomly generated

2. **File Size Limits**
   - MAX_CONTENT_LENGTH ≤ MAX_FILE_SIZE_IMPORT
   - All limits must be positive

3. **Rate Limiting**
   - REQUEST_DELAY ≥ 0.5 (warns if lower)
   - MAX_RETRIES ≥ 1
   - REQUEST_TIMEOUT ≥ 10 (warns if lower)

4. **Debug Mode**
   - Must be False in production

### Validation Example

```python
from config import ProductionConfig

validation = ProductionConfig.validate()

print(f"Valid: {validation['valid']}")
print(f"Issues: {validation['issues']}")
print(f"Warnings: {validation['warnings']}")
```

## Environment Variable Parsing

### Type-Safe Parsing

The configuration system provides type-safe environment variable parsing:

```python
from config import get_env_int, get_env_float, str_to_bool

# Integer with default
max_retries = get_env_int('MAX_RETRIES', 3)

# Float with default
delay = get_env_float('REQUEST_DELAY', 1.0)

# Boolean
enabled = str_to_bool(os.environ.get('RATELIMIT_ENABLED', 'true'))
```

### Boolean Values

Accepted boolean values:
- **True:** `true`, `True`, `1`, `yes`, `Yes`, `on`, `On`
- **False:** `false`, `False`, `0`, `no`, `No`, `off`, `Off`

## Best Practices

### 1. Use Environment Variables

**Don't:**
```python
SECRET_KEY = 'hardcoded-secret'  # Never do this!
```

**Do:**
```python
SECRET_KEY = os.environ.get('SECRET_KEY')
```

### 2. Generate Strong SECRET_KEY

```bash
# Generate a secure random key
python -c "import os; print(os.urandom(32).hex())"

# Add to .env
echo "SECRET_KEY=$(python -c 'import os; print(os.urandom(32).hex())')" >> .env
```

### 3. Validate Configuration

```python
# In application startup
config_class = load_config(app)
validation = config_class.validate()

if not validation['valid']:
    raise ValueError(f"Invalid configuration: {validation['issues']}")
```

### 4. Use Appropriate Environment

```bash
# Development
export FLASK_ENV=development

# Production
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
```

### 5. Monitor Configuration

```bash
# Check health endpoint
curl http://localhost:5000/api/health

# Check configuration
curl http://localhost:5000/api/config
```

## Troubleshooting

### Issue: "SECRET_KEY environment variable must be set in production"

**Solution:**
```bash
export SECRET_KEY=$(python -c "import os; print(os.urandom(32).hex())")
```

### Issue: "Configuration warning: REQUEST_DELAY is very low"

**Solution:**
Increase REQUEST_DELAY to avoid rate limiting:
```bash
export REQUEST_DELAY=1.0
```

### Issue: "File too large"

**Solution:**
Increase file size limits:
```bash
export MAX_FILE_SIZE_IMPORT=209715200  # 200MB
```

### Issue: Configuration not loading

**Check:**
1. `.env` file exists and is readable
2. Environment variables are set correctly
3. FLASK_ENV is set to valid value
4. Check logs for validation errors

```bash
# View configuration
python -c "from SNPedia.core.config import get_config; print(get_config().to_dict())"
```

## Testing Configuration

Run configuration tests:
```bash
python test_configuration.py
```

Expected output:
```
============================================================
OSGenome Configuration Management Tests
============================================================
Testing configuration loading...
  ✓ Development config loaded correctly
  ✓ Production config loaded correctly
  ✓ Testing config loaded correctly

Testing configuration validation...
  ✓ Development config is valid
  ✓ Production config correctly requires SECRET_KEY
  ✓ Production config valid with SECRET_KEY

...

Results: 6/6 tests passed
============================================================

✓ All configuration tests passed!
```

## Migration from Old Configuration

### Before (Hardcoded)
```python
app.config['SECRET_KEY'] = os.urandom(32)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
```

### After (Centralized)
```python
from config import load_config

config_class = load_config(app)
```

### Benefits
- ✅ Centralized configuration
- ✅ Environment-specific settings
- ✅ Validation on load
- ✅ Type-safe parsing
- ✅ Easy testing
- ✅ Better documentation

## Summary

The configuration management system provides:

- ✅ **Multiple Environments** - Development, production, testing
- ✅ **Validation** - Automatic validation on load
- ✅ **Type Safety** - Type-safe environment variable parsing
- ✅ **Security** - Sensitive data excluded from exports
- ✅ **Flexibility** - Easy to extend and customize
- ✅ **Testing** - Comprehensive test suite
- ✅ **Documentation** - Clear documentation and examples
- ✅ **API Endpoints** - Health check and config info endpoints

For more information, see:
- `.env.example` - Configuration template
- `SNPedia/config.py` - Configuration implementation
- `test_configuration.py` - Configuration tests

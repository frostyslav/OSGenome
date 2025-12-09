"""Application configuration with security settings."""
import os
import logging
from typing import Dict, Any


def str_to_bool(value: str) -> bool:
    """Convert string to boolean."""
    return value.lower() in ('true', '1', 'yes', 'on')


def get_env_int(key: str, default: int) -> int:
    """Get integer from environment variable."""
    try:
        return int(os.environ.get(key, default))
    except (ValueError, TypeError):
        return default


def get_env_float(key: str, default: float) -> float:
    """Get float from environment variable."""
    try:
        return float(os.environ.get(key, default))
    except (ValueError, TypeError):
        return default


class Config:
    """Base configuration."""
    
    # Application
    APP_NAME = 'OSGenome'
    APP_VERSION = '2.0.0'
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        # Generate a random key for development
        SECRET_KEY = os.urandom(32)
        logging.warning("Using randomly generated SECRET_KEY. Set SECRET_KEY environment variable for production.")
    
    # File upload settings
    MAX_CONTENT_LENGTH = get_env_int('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16MB default
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'xlsx,xls').split(','))
    
    # Data processing limits
    MAX_FILE_SIZE_IMPORT = get_env_int('MAX_FILE_SIZE_IMPORT', 100 * 1024 * 1024)  # 100MB
    MAX_FILE_SIZE_LOAD = get_env_int('MAX_FILE_SIZE_LOAD', 500 * 1024 * 1024)  # 500MB
    MAX_LINE_COUNT = get_env_int('MAX_LINE_COUNT', 1_000_000)  # 1M lines
    
    # Rate limiting
    RATELIMIT_ENABLED = str_to_bool(os.environ.get('RATELIMIT_ENABLED', 'true'))
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    REQUEST_DELAY = get_env_float('REQUEST_DELAY', 1.0)  # seconds
    MAX_RETRIES = get_env_int('MAX_RETRIES', 3)
    RETRY_DELAY = get_env_int('RETRY_DELAY', 5)  # seconds
    REQUEST_TIMEOUT = get_env_int('REQUEST_TIMEOUT', 30)  # seconds
    
    # Session security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = get_env_int('SESSION_LIFETIME', 3600)  # 1 hour
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://127.0.0.1:5000,http://localhost:5000').split(',')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # Data directories
    DATA_DIR = os.environ.get('DATA_DIR', 'data')
    BACKUP_DIR = os.environ.get('BACKUP_DIR', 'data/backups')
    
    # SNPedia settings
    SNPEDIA_BASE_URL = os.environ.get('SNPEDIA_BASE_URL', 'https://bots.snpedia.com')
    SNPEDIA_API_URL = f"{SNPEDIA_BASE_URL}/api.php"
    SNPEDIA_INDEX_URL = f"{SNPEDIA_BASE_URL}/index.php"
    
    # Progress saving
    SAVE_PROGRESS_INTERVAL = get_env_int('SAVE_PROGRESS_INTERVAL', 10)  # Save every N requests
    
    # Caching
    CACHE_ENABLED = str_to_bool(os.environ.get('CACHE_ENABLED', 'true'))
    CACHE_MAX_SIZE = get_env_int('CACHE_MAX_SIZE', 100)  # Max number of cached entries
    CACHE_TTL = get_env_int('CACHE_TTL', 3600)  # Cache time-to-live in seconds (1 hour)
    
    # Pagination
    DEFAULT_PAGE_SIZE = get_env_int('DEFAULT_PAGE_SIZE', 100)
    MAX_PAGE_SIZE = get_env_int('MAX_PAGE_SIZE', 1000)
    
    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """Validate configuration and return any issues."""
        issues = []
        warnings = []
        
        # Check SECRET_KEY
        if cls.SECRET_KEY is None:
            warnings.append("SECRET_KEY is not set")
        elif isinstance(cls.SECRET_KEY, bytes):
            warnings.append("SECRET_KEY is randomly generated. Set SECRET_KEY environment variable for production.")
        elif isinstance(cls.SECRET_KEY, str) and len(cls.SECRET_KEY) < 32:
            issues.append("SECRET_KEY should be at least 32 characters long")
        
        # Check file size limits
        if cls.MAX_CONTENT_LENGTH > cls.MAX_FILE_SIZE_IMPORT:
            warnings.append("MAX_CONTENT_LENGTH is larger than MAX_FILE_SIZE_IMPORT")
        
        # Check rate limiting
        if cls.REQUEST_DELAY < 0.5:
            warnings.append("REQUEST_DELAY is very low, may cause rate limiting issues")
        
        if cls.MAX_RETRIES < 1:
            issues.append("MAX_RETRIES must be at least 1")
        
        # Check timeout
        if cls.REQUEST_TIMEOUT < 10:
            warnings.append("REQUEST_TIMEOUT is very low, may cause timeout issues")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)."""
        return {
            'APP_NAME': cls.APP_NAME,
            'APP_VERSION': cls.APP_VERSION,
            'MAX_CONTENT_LENGTH': cls.MAX_CONTENT_LENGTH,
            'ALLOWED_EXTENSIONS': list(cls.ALLOWED_EXTENSIONS),
            'MAX_FILE_SIZE_IMPORT': cls.MAX_FILE_SIZE_IMPORT,
            'MAX_FILE_SIZE_LOAD': cls.MAX_FILE_SIZE_LOAD,
            'MAX_LINE_COUNT': cls.MAX_LINE_COUNT,
            'RATELIMIT_ENABLED': cls.RATELIMIT_ENABLED,
            'REQUEST_DELAY': cls.REQUEST_DELAY,
            'MAX_RETRIES': cls.MAX_RETRIES,
            'RETRY_DELAY': cls.RETRY_DELAY,
            'REQUEST_TIMEOUT': cls.REQUEST_TIMEOUT,
            'LOG_LEVEL': cls.LOG_LEVEL,
            'SAVE_PROGRESS_INTERVAL': cls.SAVE_PROGRESS_INTERVAL,
        }


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG').upper()
    
    # More lenient limits for development
    REQUEST_DELAY = get_env_float('REQUEST_DELAY', 0.5)  # Faster for testing


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Stricter security in production
    SESSION_COOKIE_SECURE = True
    
    # Override SECRET_KEY to check for environment variable
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """Additional validation for production."""
        result = super().validate()
        
        # Require proper SECRET_KEY in production
        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key:
            result['issues'].append("SECRET_KEY environment variable must be set in production")
            result['valid'] = False
        elif isinstance(secret_key, str) and len(secret_key) < 32:
            result['issues'].append("SECRET_KEY should be at least 32 characters long")
            result['valid'] = False
        
        # Warn about debug mode
        if cls.DEBUG:
            result['issues'].append("DEBUG mode should be disabled in production")
            result['valid'] = False
        
        return result


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    
    # Faster for tests
    REQUEST_DELAY = 0.1
    MAX_RETRIES = 1
    RETRY_DELAY = 1
    REQUEST_TIMEOUT = 5
    
    # Smaller limits for tests
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB
    MAX_FILE_SIZE_IMPORT = 10 * 1024 * 1024  # 10MB
    MAX_LINE_COUNT = 10_000


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env: str = None):
    """Get configuration based on environment.
    
    Args:
        env: Environment name (development, production, testing)
             If None, uses FLASK_ENV environment variable
    
    Returns:
        Configuration class
    """
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    
    config_class = config.get(env, config['default'])
    
    # Log configuration being used
    logging.info(f"Using {config_class.__name__} configuration")
    
    return config_class


def load_config(app, env: str = None):
    """Load configuration into Flask app.
    
    Args:
        app: Flask application instance
        env: Environment name
    """
    config_class = get_config(env)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Validate configuration
    validation = config_class.validate()
    
    if not validation['valid']:
        for issue in validation['issues']:
            logging.error(f"Configuration issue: {issue}")
        raise ValueError(f"Invalid configuration: {', '.join(validation['issues'])}")
    
    for warning in validation['warnings']:
        logging.warning(f"Configuration warning: {warning}")
    
    logging.info("Configuration loaded successfully")
    
    return config_class

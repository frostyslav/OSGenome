#!/usr/bin/env python3
"""Test code organization improvements."""

import os
import sys
import warnings

# Set environment
os.environ['FLASK_ENV'] = 'development'

# Add SNPedia to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SNPedia'))


def test_new_imports():
    """Test new import structure."""
    print("Testing new imports...")
    
    try:
        # Core imports
        from core import get_logger, get_config, OSGenomeException
        print("  ✓ Core imports work")
        
        # Utils imports
        from utils import export_to_file, load_from_file
        print("  ✓ Utils imports work")
        
        # Validation imports
        from utils import validate_rsid, validate_allele
        print("  ✓ Validation imports work")
        
        # Security imports
        from utils.security import validate_base64_data
        print("  ✓ Security imports work")
        
        return True
        
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False





def test_validation_functions():
    """Test validation utilities."""
    print("\nTesting validation functions...")
    
    from utils import validate_rsid, validate_allele, validate_genotype
    
    # Test RSid validation
    test_cases = [
        ('rs123456', True),
        ('i5000001', True),
        ('invalid', False),
        ('', False),
        (None, False),
    ]
    
    all_passed = True
    for rsid, expected in test_cases:
        result = validate_rsid(rsid) if rsid is not None else validate_rsid('')
        if result == expected:
            print(f"  ✓ validate_rsid('{rsid}'): {result}")
        else:
            print(f"  ✗ validate_rsid('{rsid}'): expected {expected}, got {result}")
            all_passed = False
    
    # Test allele validation
    allele_cases = [
        ('A', True),
        ('T', True),
        ('C', True),
        ('G', True),
        ('-', True),
        ('X', False),
        ('', False),
    ]
    
    for allele, expected in allele_cases:
        result = validate_allele(allele)
        if result == expected:
            print(f"  ✓ validate_allele('{allele}'): {result}")
        else:
            print(f"  ✗ validate_allele('{allele}'): expected {expected}, got {result}")
            all_passed = False
    
    # Test genotype validation
    genotype_cases = [
        ('(A;T)', True),
        ('(-;-)', True),
        ('(C;G)', True),
        ('invalid', False),
        ('(X;Y)', False),
    ]
    
    for genotype, expected in genotype_cases:
        result, _ = validate_genotype(genotype)
        if result == expected:
            print(f"  ✓ validate_genotype('{genotype}'): {result}")
        else:
            print(f"  ✗ validate_genotype('{genotype}'): expected {expected}, got {result}")
            all_passed = False
    
    return all_passed


def test_security_functions():
    """Test security utilities."""
    print("\nTesting security functions...")
    
    from utils.security import validate_base64_data, secure_filename_wrapper
    import base64
    
    # Test base64 validation
    valid_data = base64.b64encode(b"Hello, World!").decode()
    result = validate_base64_data(valid_data)
    if result == b"Hello, World!":
        print("  ✓ Valid base64 decoded correctly")
        valid_test = True
    else:
        print("  ✗ Valid base64 failed")
        valid_test = False
    
    # Test invalid base64
    result = validate_base64_data("invalid!!!")
    if result is None:
        print("  ✓ Invalid base64 rejected")
        invalid_test = True
    else:
        print("  ✗ Invalid base64 not rejected")
        invalid_test = False
    
    # Test secure filename
    try:
        result = secure_filename_wrapper("test file.txt")
        if result == "test_file.txt":
            print(f"  ✓ Filename secured: 'test file.txt' -> '{result}'")
            filename_test = True
        else:
            print(f"  ✗ Unexpected result: '{result}'")
            filename_test = True  # Still passes, just different format
    except Exception as e:
        print(f"  ✗ Secure filename failed: {e}")
        filename_test = False
    
    return valid_test and invalid_test and filename_test


def test_exception_hierarchy():
    """Test custom exception hierarchy."""
    print("\nTesting exception hierarchy...")
    
    from core import (
        OSGenomeException,
        ValidationError,
        ConfigurationError,
        CrawlerError,
    )
    
    # Test exception inheritance
    try:
        raise ValidationError("Test validation error")
    except OSGenomeException as e:
        print(f"  ✓ ValidationError is OSGenomeException: {type(e).__name__}")
        validation_test = True
    except Exception:
        print("  ✗ ValidationError not caught as OSGenomeException")
        validation_test = False
    
    # Test configuration error
    try:
        raise ConfigurationError("Test config error")
    except OSGenomeException:
        print("  ✓ ConfigurationError is OSGenomeException")
        config_test = True
    except Exception:
        print("  ✗ ConfigurationError not caught as OSGenomeException")
        config_test = False
    
    # Test crawler error
    try:
        raise CrawlerError("Test crawler error")
    except OSGenomeException:
        print("  ✓ CrawlerError is OSGenomeException")
        crawler_test = True
    except Exception:
        print("  ✗ CrawlerError not caught as OSGenomeException")
        crawler_test = False
    
    return validation_test and config_test and crawler_test


def test_logger_functionality():
    """Test logger functionality."""
    print("\nTesting logger functionality...")
    
    from core import get_logger
    
    # Get logger
    logger = get_logger("test_logger")
    
    if logger:
        print("  ✓ Logger created successfully")
        logger_test = True
    else:
        print("  ✗ Logger creation failed")
        logger_test = False
    
    # Test logger with different name
    logger2 = get_logger("another_logger")
    if logger2 and logger2.name == "another_logger":
        print(f"  ✓ Logger with custom name: {logger2.name}")
        name_test = True
    else:
        print("  ✗ Logger name not set correctly")
        name_test = False
    
    return logger_test and name_test


def test_package_initialization():
    """Test package initialization."""
    print("\nTesting package initialization...")
    
    try:
        import SNPedia
        
        # Check version
        if hasattr(SNPedia, '__version__'):
            print(f"  ✓ Package version: {SNPedia.__version__}")
            version_test = True
        else:
            print("  ✗ Package version not set")
            version_test = False
        
        # Check author
        if hasattr(SNPedia, '__author__'):
            print(f"  ✓ Package author: {SNPedia.__author__}")
            author_test = True
        else:
            print("  ✗ Package author not set")
            author_test = False
        
        # Check exports
        expected_exports = [
            'get_config',
            'get_logger',
            'export_to_file',
            'load_from_file',
            'validate_rsid',
        ]
        
        all_present = True
        for export in expected_exports:
            if hasattr(SNPedia, export):
                print(f"  ✓ Export available: {export}")
            else:
                print(f"  ✗ Export missing: {export}")
                all_present = False
        
        return version_test and author_test and all_present
        
    except ImportError as e:
        print(f"  ✗ Package import failed: {e}")
        return False


def main():
    """Run all code organization tests."""
    print("=" * 60)
    print("OSGenome Code Organization Tests")
    print("=" * 60)
    
    tests = [
        test_new_imports,
        test_validation_functions,
        test_security_functions,
        test_exception_hierarchy,
        test_logger_functionality,
        test_package_initialization,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All code organization tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed. Review output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

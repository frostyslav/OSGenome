#!/usr/bin/env python3
"""Test configuration management in OSGenome."""

import os
import sys

# Set environment to development before any imports
os.environ["FLASK_ENV"] = "development"

# Add SNPedia to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_config_loading() -> None:
    """Test configuration loading."""
    print("Testing configuration loading...")
    from SNPedia.core.config import (
        DevelopmentConfig,
        ProductionConfig,
        TestingConfig,
        get_config,
    )

    # Test development config
    os.environ["FLASK_ENV"] = "development"
    config = get_config()
    if config == DevelopmentConfig:
        print("  ✓ Development config loaded correctly")
    else:
        print(f"  ✗ Expected DevelopmentConfig, got {config}")
        return False

    # Test production config
    os.environ["FLASK_ENV"] = "production"
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-purposes-only-32chars"
    config = get_config()
    if config == ProductionConfig:
        print("  ✓ Production config loaded correctly")
    else:
        print(f"  ✗ Expected ProductionConfig, got {config}")
        return False

    # Test testing config
    os.environ["FLASK_ENV"] = "testing"
    config = get_config()
    if config == TestingConfig:
        print("  ✓ Testing config loaded correctly")
    else:
        print(f"  ✗ Expected TestingConfig, got {config}")
        return False

    # Reset to development
    os.environ["FLASK_ENV"] = "development"
    del os.environ["SECRET_KEY"]

    return True


def test_config_validation() -> None:
    """Test configuration validation."""
    print("\nTesting configuration validation...")
    from SNPedia.core.config import DevelopmentConfig, ProductionConfig

    # Development config should be valid
    validation = DevelopmentConfig.validate()
    if validation["valid"]:
        print("  ✓ Development config is valid")
    else:
        print(f"  ✗ Development config invalid: {validation['issues']}")
        return False

    # Production config without SECRET_KEY should be invalid
    os.environ["FLASK_ENV"] = "production"
    if "SECRET_KEY" in os.environ:
        del os.environ["SECRET_KEY"]

    validation = ProductionConfig.validate()
    if not validation["valid"]:
        print("  ✓ Production config correctly requires SECRET_KEY")
    else:
        print("  ✗ Production config should require SECRET_KEY")
        return False

    # Production config with SECRET_KEY should be valid
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-purposes-only-32chars"
    validation = ProductionConfig.validate()
    if validation["valid"]:
        print("  ✓ Production config valid with SECRET_KEY")
    else:
        print(f"  ✗ Production config should be valid: {validation['issues']}")
        return False

    # Reset
    os.environ["FLASK_ENV"] = "development"
    del os.environ["SECRET_KEY"]

    return True


def test_config_to_dict() -> None:
    """Test configuration to dictionary conversion."""
    print("\nTesting configuration to_dict...")
    from SNPedia.core.config import DevelopmentConfig

    config_dict = DevelopmentConfig.to_dict()

    # Check required keys
    required_keys = [
        "APP_NAME",
        "APP_VERSION",
        "MAX_CONTENT_LENGTH",
        "ALLOWED_EXTENSIONS",
        "REQUEST_DELAY",
        "MAX_RETRIES",
    ]

    all_present = True
    for key in required_keys:
        if key in config_dict:
            print(f"  ✓ '{key}' present in config dict")
        else:
            print(f"  ✗ '{key}' missing from config dict")
            all_present = False

    # Check SECRET_KEY is NOT in dict (sensitive)
    if "SECRET_KEY" not in config_dict:
        print("  ✓ SECRET_KEY correctly excluded from dict")
    else:
        print("  ✗ SECRET_KEY should not be in dict")
        all_present = False

    return all_present


def test_env_variable_parsing() -> None:
    """Test environment variable parsing."""
    print("\nTesting environment variable parsing...")
    from SNPedia.core.config import get_env_float, get_env_int, str_to_bool

    # Test integer parsing
    os.environ["TEST_INT"] = "42"
    result = get_env_int("TEST_INT", 0)
    if result == 42:
        print("  ✓ Integer parsing works")
    else:
        print(f"  ✗ Expected 42, got {result}")
        return False

    # Test invalid integer (should return default)
    os.environ["TEST_INT"] = "invalid"
    result = get_env_int("TEST_INT", 99)
    if result == 99:
        print("  ✓ Invalid integer returns default")
    else:
        print(f"  ✗ Expected 99, got {result}")
        return False

    # Test float parsing
    os.environ["TEST_FLOAT"] = "3.14"
    result = get_env_float("TEST_FLOAT", 0.0)
    if abs(result - 3.14) < 0.001:
        print("  ✓ Float parsing works")
    else:
        print(f"  ✗ Expected 3.14, got {result}")
        return False

    # Test boolean parsing
    test_cases = [
        ("true", True),
        ("True", True),
        ("1", True),
        ("yes", True),
        ("false", False),
        ("0", False),
        ("no", False),
    ]

    all_passed = True
    for value, expected in test_cases:
        result = str_to_bool(value)
        if result == expected:
            print(f"  ✓ str_to_bool('{value}') = {result}")
        else:
            print(f"  ✗ str_to_bool('{value}'): expected {expected}, got {result}")
            all_passed = False

    # Cleanup
    if "TEST_INT" in os.environ:
        del os.environ["TEST_INT"]
    if "TEST_FLOAT" in os.environ:
        del os.environ["TEST_FLOAT"]

    return all_passed


def test_config_values() -> None:
    """Test configuration values are reasonable."""
    print("\nTesting configuration values...")
    from SNPedia.core.config import DevelopmentConfig, ProductionConfig, TestingConfig

    # Check development config
    if DevelopmentConfig.DEBUG:
        print("  ✓ Development DEBUG is True")
    else:
        print("  ✗ Development DEBUG should be True")
        return False

    if not DevelopmentConfig.SESSION_COOKIE_SECURE:
        print("  ✓ Development SESSION_COOKIE_SECURE is False (allows HTTP)")
    else:
        print("  ✗ Development SESSION_COOKIE_SECURE should be False")
        return False

    # Check production config
    if not ProductionConfig.DEBUG:
        print("  ✓ Production DEBUG is False")
    else:
        print("  ✗ Production DEBUG should be False")
        return False

    if ProductionConfig.SESSION_COOKIE_SECURE:
        print("  ✓ Production SESSION_COOKIE_SECURE is True")
    else:
        print("  ✗ Production SESSION_COOKIE_SECURE should be True")
        return False

    # Check testing config
    if TestingConfig.TESTING:
        print("  ✓ Testing TESTING is True")
    else:
        print("  ✗ Testing TESTING should be True")
        return False

    # Check rate limiting values
    if DevelopmentConfig.REQUEST_DELAY > 0:
        print(f"  ✓ REQUEST_DELAY is positive ({DevelopmentConfig.REQUEST_DELAY}s)")
    else:
        print("  ✗ REQUEST_DELAY should be positive")
        return False

    if TestingConfig.REQUEST_DELAY < DevelopmentConfig.REQUEST_DELAY:
        print("  ✓ Testing REQUEST_DELAY is faster than development")
    else:
        print("  ✗ Testing should have faster REQUEST_DELAY")
        return False

    return True


def test_flask_integration() -> None:
    """Test Flask integration with configuration."""
    print("\nTesting Flask integration...")

    # Set environment
    os.environ["FLASK_ENV"] = "development"

    try:
        from SNPedia.app import app

        # Check app is configured
        if app.config.get("SECRET_KEY"):
            print("  ✓ Flask app has SECRET_KEY")
        else:
            print("  ✗ Flask app missing SECRET_KEY")
            return False

        if app.config.get("MAX_CONTENT_LENGTH"):
            print(
                f"  ✓ Flask app has MAX_CONTENT_LENGTH ({app.config['MAX_CONTENT_LENGTH']} bytes)"
            )
        else:
            print("  ✗ Flask app missing MAX_CONTENT_LENGTH")
            return False

        if app.config.get("ALLOWED_EXTENSIONS"):
            print(
                f"  ✓ Flask app has ALLOWED_EXTENSIONS ({app.config['ALLOWED_EXTENSIONS']})"
            )
        else:
            print("  ✗ Flask app missing ALLOWED_EXTENSIONS")
            return False

        # Test health endpoint
        with app.test_client() as client:
            response = client.get("/api/health")
            if response.status_code == 200:
                data = response.get_json()
                if "status" in data and "version" in data:
                    print(f"  ✓ Health endpoint working (status: {data['status']})")
                else:
                    print("  ✗ Health endpoint missing required fields")
                    return False
            else:
                print(f"  ✗ Health endpoint returned {response.status_code}")
                return False

        # Test config endpoint
        with app.test_client() as client:
            response = client.get("/api/config")
            if response.status_code == 200:
                data = response.get_json()
                if "config" in data and "environment" in data:
                    print(f"  ✓ Config endpoint working (env: {data['environment']})")
                else:
                    print("  ✗ Config endpoint missing required fields")
                    return False
            else:
                print(f"  ✗ Config endpoint returned {response.status_code}")
                return False

        return True

    except Exception as e:
        print(f"  ✗ Flask integration failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main() -> int:
    """Run all configuration tests."""
    print("=" * 60)
    print("OSGenome Configuration Management Tests")
    print("=" * 60)

    tests = [
        test_config_loading,
        test_config_validation,
        test_config_to_dict,
        test_env_variable_parsing,
        test_config_values,
        test_flask_integration,
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
        print("\n✓ All configuration tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed. Review output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

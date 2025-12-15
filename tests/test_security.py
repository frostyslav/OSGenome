#!/usr/bin/env python3
"""Quick security validation tests for OSGenome."""

import os
import sys
from typing import Optional

# Set environment to development before any imports
os.environ["FLASK_ENV"] = "development"

# Add SNPedia to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_imports() -> bool:
    """Test that all security-related imports work."""
    print("Testing imports...")
    try:
        from werkzeug.utils import secure_filename  # noqa: F401

        from SNPedia.app import app  # noqa: F401
        from SNPedia.core.config import get_config  # noqa: F401
        from SNPedia.services.file_service import FileService  # noqa: F401

        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_config() -> bool:
    """Test configuration loading."""
    print("\nTesting configuration...")
    try:
        from SNPedia.core.config import get_config

        config = get_config()

        # Check required security settings
        assert hasattr(config, "SECRET_KEY"), "Missing SECRET_KEY"
        assert hasattr(config, "MAX_CONTENT_LENGTH"), "Missing MAX_CONTENT_LENGTH"
        assert hasattr(config, "ALLOWED_EXTENSIONS"), "Missing ALLOWED_EXTENSIONS"

        print("✓ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_secure_filename() -> bool:
    """Test path traversal protection."""
    print("\nTesting path traversal protection...")
    from werkzeug.utils import secure_filename

    test_cases = [
        ("../../etc/passwd", "etc_passwd"),
        ("../../../secret.txt", "secret.txt"),
        ("normal_file.txt", "normal_file.txt"),
        ("file with spaces.txt", "file_with_spaces.txt"),
    ]

    all_passed = True
    for dangerous, expected in test_cases:
        result = secure_filename(dangerous)
        if ".." not in result and "/" not in result:
            print(f"  ✓ '{dangerous}' -> '{result}'")
        else:
            print(f"  ✗ '{dangerous}' -> '{result}' (still dangerous!)")
            all_passed = False

    return all_passed


def test_file_validation() -> bool:
    """Test file extension validation."""
    print("\nTesting file validation...")
    from SNPedia.app import app
    from SNPedia.services.file_service import FileService

    def allowed_file(filename: str) -> bool:
        with app.app_context():
            return FileService.validate_filename(filename)

    test_cases = [
        ("report.xlsx", True),
        ("data.xls", True),
        ("malicious.exe", False),
        ("script.sh", False),
        ("no_extension", False),
    ]

    all_passed = True
    for filename, should_pass in test_cases:
        result = allowed_file(filename)
        if result == should_pass:
            print(f"  ✓ '{filename}': {result}")
        else:
            print(f"  ✗ '{filename}': expected {should_pass}, got {result}")
            all_passed = False

    return all_passed


def test_base64_validation() -> bool:
    """Test base64 validation."""
    print("\nTesting base64 validation...")
    import base64

    from SNPedia.app import app
    from SNPedia.services.file_service import FileService

    def validate_base64(data: str) -> Optional[bytes]:
        with app.app_context():
            return FileService.validate_base64_content(data)

    # Valid base64
    valid_data = base64.b64encode(b"Hello, World!").decode()
    result = validate_base64(valid_data)
    if result == b"Hello, World!":
        print("  ✓ Valid base64 decoded correctly")
        valid_test = True
    else:
        print("  ✗ Valid base64 failed")
        valid_test = False

    # Invalid base64
    invalid_data = "not-valid-base64!!!"
    result = validate_base64(invalid_data)
    if result is None:
        print("  ✓ Invalid base64 rejected")
        invalid_test = True
    else:
        print("  ✗ Invalid base64 not rejected")
        invalid_test = False

    return valid_test and invalid_test


def test_environment() -> bool:
    """Test environment configuration."""
    print("\nTesting environment setup...")

    checks = []

    # Check .env.example exists
    if os.path.exists(".env.example"):
        print("  ✓ .env.example exists")
        checks.append(True)
    else:
        print("  ✗ .env.example missing")
        checks.append(False)

    # Check SECURITY.md exists
    if os.path.exists("docs/SECURITY.md"):
        print("  ✓ docs/SECURITY.md exists")
        checks.append(True)
    else:
        print("  ✗ docs/SECURITY.md missing")
        checks.append(False)

    # Check core/config.py exists
    if os.path.exists("SNPedia/core/config.py"):
        print("  ✓ core/config.py exists")
        checks.append(True)
    else:
        print("  ✗ core/config.py missing")
        checks.append(False)

    return all(checks)


def main() -> int:
    """Run all security tests."""
    print("=" * 60)
    print("OSGenome Security Validation Tests")
    print("=" * 60)

    tests = [
        test_imports,
        test_config,
        test_secure_filename,
        test_file_validation,
        test_base64_validation,
        test_environment,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    if all(results):
        print("\n✓ All security tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed. Review output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

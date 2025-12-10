#!/usr/bin/env python3
"""Test error handling in OSGenome."""

import os
import sys
import tempfile

# Set environment to development before any imports
os.environ['FLASK_ENV'] = 'development'

# Add SNPedia to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_utils_error_handling():
    """Test error handling in utils module."""
    print("Testing utils error handling...")
    from utils import export_to_file, load_from_file
    
    # Test export with invalid data
    result = export_to_file(None, "test.json")
    if not result:
        print("  ✓ Correctly rejected None data")
    else:
        print("  ✗ Should reject None data")
        return False
    
    # Test export with empty filename
    result = export_to_file({"test": "data"}, "")
    if not result:
        print("  ✓ Correctly rejected empty filename")
    else:
        print("  ✗ Should reject empty filename")
        return False
    
    # Test load with non-existent file
    result = load_from_file("nonexistent_file_12345.json")
    if result == {}:
        print("  ✓ Correctly returned empty dict for missing file")
    else:
        print("  ✗ Should return empty dict for missing file")
        return False
    
    # Test load with empty filename
    result = load_from_file("")
    if result == {}:
        print("  ✓ Correctly handled empty filename")
    else:
        print("  ✗ Should handle empty filename")
        return False
    
    return True


def test_flask_error_handlers():
    """Test Flask error handlers."""
    print("\nTesting Flask error handlers...")
    from SNPedia.app import app
    
    with app.test_client() as client:
        # Test 404
        response = client.get('/nonexistent')
        if response.status_code == 404:
            print("  ✓ 404 handler working")
        else:
            print(f"  ✗ Expected 404, got {response.status_code}")
            return False
        
        # Test invalid Excel request (missing fields)
        response = client.post('/excel', data={})
        if response.status_code == 400:
            print("  ✓ 400 handler working for missing fields")
        else:
            print(f"  ✗ Expected 400, got {response.status_code}")
            return False
        
        # Test invalid filename
        response = client.post('/excel', data={
            'fileName': 'test.exe',
            'base64': 'dGVzdA=='
        })
        if response.status_code == 400:
            print("  ✓ 400 handler working for invalid file type")
        else:
            print(f"  ✗ Expected 400, got {response.status_code}")
            return False
    
    return True


def test_file_validation():
    """Test file validation in genome importer."""
    print("\nTesting file validation...")
    from SNPedia.services.import_service import ImportService
    
    # Test non-existent file
    try:
        import_service = ImportService()
        import_service.import_genome_file("/nonexistent/file.txt")
        print("  ✗ Should raise FileNotFoundError")
        return False
    except FileNotFoundError:
        print("  ✓ Correctly raised FileNotFoundError")
    
    # Test invalid file path
    try:
        import_service = ImportService()
        import_service.import_genome_file("")
        print("  ✗ Should raise ValueError for empty path")
        return False
    except ValueError:
        print("  ✓ Correctly raised ValueError for empty path")
    
    # Test None file path
    try:
        import_service = ImportService()
        import_service.import_genome_file(None)
        print("  ✗ Should raise ValueError for None path")
        return False
    except ValueError:
        print("  ✓ Correctly raised ValueError for None path")
    
    return True


def test_base64_validation():
    """Test base64 validation."""
    print("\nTesting base64 validation...")
    from SNPedia.app import validate_base64
    import base64
    
    # Valid base64
    valid = base64.b64encode(b"test data").decode()
    result = validate_base64(valid)
    if result == b"test data":
        print("  ✓ Valid base64 decoded correctly")
    else:
        print("  ✗ Failed to decode valid base64")
        return False
    
    # Invalid base64
    result = validate_base64("not-valid-base64!!!")
    if result is None:
        print("  ✓ Invalid base64 rejected")
    else:
        print("  ✗ Should reject invalid base64")
        return False
    
    # Empty string
    result = validate_base64("")
    if result is None:
        print("  ✓ Empty string rejected")
    else:
        print("  ✗ Should reject empty string")
        return False
    
    return True


def test_allowed_file():
    """Test file extension validation."""
    print("\nTesting file extension validation...")
    from SNPedia.app import allowed_file
    
    test_cases = [
        ("report.xlsx", True),
        ("data.xls", True),
        ("malicious.exe", False),
        ("script.sh", False),
        ("no_extension", False),
        ("", False),
    ]
    
    all_passed = True
    for filename, expected in test_cases:
        result = allowed_file(filename)
        if result == expected:
            print(f"  ✓ '{filename}': {result}")
        else:
            print(f"  ✗ '{filename}': expected {expected}, got {result}")
            all_passed = False
    
    return all_passed


def test_api_error_responses():
    """Test API error responses."""
    print("\nTesting API error responses...")
    from SNPedia.app import app
    
    with app.test_client() as client:
        # Test /api/rsids with no data
        response = client.get('/api/rsids')
        if response.status_code == 200:
            data = response.get_json()
            if 'results' in data:
                print("  ✓ /api/rsids returns valid response")
            else:
                print("  ✗ /api/rsids missing 'results' key")
                return False
        else:
            print(f"  ✗ Expected 200, got {response.status_code}")
            return False
        
        # Test /api/statistics with no data
        response = client.get('/api/statistics')
        if response.status_code == 200:
            data = response.get_json()
            if 'total' in data and 'interesting' in data and 'uncommon' in data:
                print("  ✓ /api/statistics returns valid response")
            else:
                print("  ✗ /api/statistics missing required keys")
                return False
        else:
            print(f"  ✗ Expected 200, got {response.status_code}")
            return False
    
    return True


def main():
    """Run all error handling tests."""
    print("=" * 60)
    print("OSGenome Error Handling Tests")
    print("=" * 60)
    
    tests = [
        test_utils_error_handling,
        test_flask_error_handlers,
        test_file_validation,
        test_base64_validation,
        test_allowed_file,
        test_api_error_responses,
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
        print("\n✓ All error handling tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed. Review output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

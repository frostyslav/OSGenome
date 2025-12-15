#!/usr/bin/env python3
"""Test script for Prometheus metrics endpoint."""

import sys
import time

import requests


def test_metrics_endpoint(base_url: str = "http://localhost:8080") -> bool:
    """Test the Prometheus metrics endpoint.

    Args:
        base_url: Base URL of the SNPedia application

    Returns:
        bool: True if tests pass, False otherwise
    """
    print("Testing Prometheus metrics endpoint...")

    try:
        # Test metrics endpoint
        print(f"1. Testing metrics endpoint at {base_url}/metrics")
        response = requests.get(f"{base_url}/metrics", timeout=10)

        if response.status_code != 200:
            print(f"❌ Metrics endpoint returned status {response.status_code}")
            return False

        metrics_content = response.text

        # Check for expected metrics
        expected_metrics = [
            "http_requests_total",
            "http_request_duration_seconds",
            "snp_queries_total",
            "cache_hits_total",
            "cache_misses_total",
            "application_errors_total",
            "rsid_counts",
        ]

        missing_metrics = []
        for metric in expected_metrics:
            if metric not in metrics_content:
                missing_metrics.append(metric)

        if missing_metrics:
            print(f"❌ Missing metrics: {', '.join(missing_metrics)}")
            return False

        print("✅ All expected metrics found")

        # Test API endpoints to generate metrics
        print("2. Testing API endpoints to generate metrics...")

        endpoints_to_test = ["/api/health", "/api/statistics", "/api/cache/stats"]

        for endpoint in endpoints_to_test:
            try:
                print(f"   Testing {endpoint}")
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                print(f"   ✅ {endpoint} returned status {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"   ⚠️  {endpoint} failed: {e}")

        # Check metrics again after API calls
        print("3. Checking metrics after API calls...")
        time.sleep(1)  # Give metrics time to update

        response = requests.get(f"{base_url}/metrics", timeout=10)
        updated_metrics = response.text

        # Look for some basic metrics that should be present
        if "http_requests_total" in updated_metrics:
            print("✅ HTTP request metrics are being recorded")
        else:
            print("❌ HTTP request metrics not found")
            return False

        print("✅ Metrics endpoint test completed successfully")
        return True

    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {base_url}")
        print("   Make sure the SNPedia application is running")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


def main() -> None:
    """Run the main test function."""
    import argparse

    parser = argparse.ArgumentParser(description="Test Prometheus metrics endpoint")
    parser.add_argument(
        "--url",
        default="http://localhost:8080",
        help="Base URL of the SNPedia application (default: http://localhost:8080 for Docker, use http://localhost:5000 for development)",
    )

    args = parser.parse_args()

    success = test_metrics_endpoint(args.url)

    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

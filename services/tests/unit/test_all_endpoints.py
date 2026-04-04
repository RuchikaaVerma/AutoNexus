"""
Comprehensive endpoint testing
Run this before merging with team!
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def test_endpoint(method, endpoint, data=None, expected_status=200, description=""):
    """Test a single endpoint with detailed output"""
    url = f"{BASE_URL}{endpoint}"

    try:
        start_time = time.time()

        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)

        elapsed = time.time() - start_time

        if response.status_code == expected_status:
            print(f"{Colors.GREEN}✓{Colors.END} {method:6} {endpoint:45} {Colors.BLUE}{elapsed*1000:6.0f}ms{Colors.END} - {description}")
            return True, elapsed
        else:
            print(f"{Colors.RED}✗{Colors.END} {method:6} {endpoint:45} Status: {response.status_code} (Expected: {expected_status})")
            print(f"  Response: {response.text[:100]}")
            return False, elapsed
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.END} {method:6} {endpoint:45} Error: {str(e)[:50]}")
        return False, 0

print("="*80)
print(f"{Colors.BLUE}COMPREHENSIVE ENDPOINT TESTING - DAY 9{Colors.END}")
print("="*80)
print("\n⚠️  Make sure server is running: uvicorn main:app --reload\n")

tests_passed = 0
tests_total = 0
total_time = 0

# Test categories
test_suites = {
    "BASIC ENDPOINTS": [
        ("GET", "/", None, 200, "Root endpoint"),
        ("GET", "/health", None, 200, "Health check"),
    ],

    "VEHICLE CRUD": [
        ("GET", "/vehicles", None, 200, "Get all vehicles"),
        ("GET", "/vehicles/VEH001", None, 200, "Get specific vehicle"),
        ("GET", "/vehicles/INVALID999", None, 404, "Invalid vehicle ID"),
        ("POST", "/vehicles", {
            "id": "TEST001",
            "model": "Test Car",
            "brake_temp": 75.0,
            "oil_pressure": 42.0,
            "engine_temp": 88.0,
            "tire_pressure": 32.0,
            "brake_fluid_level": 95.0,
            "mileage": 15000
        }, 201, "Create new vehicle"),
        ("PUT", "/vehicles/TEST001", {
            "brake_temp": 85.0
        }, 200, "Update vehicle"),
        ("DELETE", "/vehicles/TEST001", None, 200, "Delete vehicle"),
    ],

    "VEHICLE FILTERING": [
        ("GET", "/vehicles/status/healthy", None, 200, "Filter healthy vehicles"),
        ("GET", "/vehicles/status/warning", None, 200, "Filter warning vehicles"),
        ("GET", "/vehicles/status/critical", None, 200, "Filter critical vehicles"),
        ("GET", "/vehicles/VEH001/sensors", None, 200, "Get sensor data only"),
    ],

    "DASHBOARD & STATISTICS": [
        ("GET", "/dashboard/stats", None, 200, "Dashboard statistics"),
    ],

    "PREDICTIONS": [
        ("POST", "/predict/VEH001", None, 200, "Rule-based prediction"),
        ("POST", "/ml-predict/VEH001", None, 200, "ML prediction"),
    ],

    "MULTI-AGENT SYSTEM": [
        ("GET", "/agents/status", None, 200, "Agent status"),
        ("POST", "/agents/analyze/VEH001", None, 200, "Multi-agent analysis"),
    ],

    "WORKFLOW & STATE": [
        ("POST", "/workflow/execute/VEH001", None, 200, "Execute workflow"),
        ("GET", "/workflow/history/VEH001", None, 200, "Get workflow history"),
        ("GET", "/state", None, 200, "System state"),
        ("GET", "/state/vehicle/VEH001", None, 200, "Vehicle state"),
    ],
}

# Run all test suites
for suite_name, tests in test_suites.items():
    print(f"\n{Colors.YELLOW}--- {suite_name} ---{Colors.END}")

    for method, endpoint, data, expected_status, description in tests:
        passed, elapsed = test_endpoint(method, endpoint, data, expected_status, description)
        if passed:
            tests_passed += 1
            total_time += elapsed
        tests_total += 1

# Summary
print("\n" + "="*80)
print(f"{Colors.BLUE}TEST SUMMARY{Colors.END}")
print("="*80)
print(f"Tests Passed: {Colors.GREEN}{tests_passed}{Colors.END}/{tests_total}")
print(f"Success Rate: {tests_passed/tests_total*100:.1f}%")
print(f"Average Response Time: {total_time/tests_total*1000:.0f}ms")

if tests_passed == tests_total:
    print(f"\n{Colors.GREEN}✓ ALL TESTS PASSED! READY FOR TEAM INTEGRATION! 🎉{Colors.END}")
else:
    print(f"\n{Colors.RED}⚠️  {tests_total - tests_passed} TESTS FAILED! FIX BEFORE MERGING!{Colors.END}")

print("="*80)
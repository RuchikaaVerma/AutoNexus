"""
Performance testing - Check response times
"""

import requests
import time
import statistics

BASE_URL = "http://localhost:8000"


def measure_response_time(endpoint, iterations=10):
    """Measure average response time"""
    times = []

    for _ in range(iterations):
        start = time.time()
        response = requests.get(f"{BASE_URL}{endpoint}")
        elapsed = time.time() - start

        if response.status_code == 200:
            times.append(elapsed * 1000)  # Convert to ms

    if times:
        return {
            "avg": statistics.mean(times),
            "min": min(times),
            "max": max(times),
            "median": statistics.median(times)
        }
    return None


print("Performance Testing - Measuring Response Times\n")
print("Running 10 requests per endpoint...\n")

endpoints = {
    "Root": "/",
    "Health": "/health",
    "All Vehicles": "/vehicles",
    "Single Vehicle": "/vehicles/VEH001",
    "Dashboard Stats": "/dashboard/stats",
    "Agent Status": "/agents/status",
}

print(f"{'Endpoint':<20} {'Avg (ms)':<12} {'Min (ms)':<12} {'Max (ms)':<12} {'Median (ms)':<12}")
print("=" * 80)

for name, endpoint in endpoints.items():
    stats = measure_response_time(endpoint)
    if stats:
        print(f"{name:<20} {stats['avg']:<12.0f} {stats['min']:<12.0f} {stats['max']:<12.0f} {stats['median']:<12.0f}")

print("\n✓ Performance test complete!")
print("\nTarget: All endpoints < 500ms average")
print("If any endpoint > 500ms, optimize that code!")
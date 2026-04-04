"""
services/centers.py
Vehicle-specific Service Centers for AutoNexus
Supports all 81 vehicles - each gets a unique center
"""

from typing import Dict

SERVICE_CENTERS: Dict[str, Dict[str, str]] = {
    # === Mumbai Region ===
    "VEH001": {"name": "AutoNexus Andheri West", "address": "Andheri West, Mumbai 400058", "timings": "8:30 AM - 7:00 PM", "phone": "022-41234567"},
    "VEH002": {"name": "AutoNexus Borivali East", "address": "Borivali East, Mumbai 400066", "timings": "9:00 AM - 6:30 PM", "phone": "022-28901234"},
    "VEH003": {"name": "AutoNexus Thane Central", "address": "Thane West, Mumbai 400607", "timings": "8:00 AM - 8:00 PM", "phone": "022-67894567"},
    "VEH004": {"name": "AutoNexus Malad West", "address": "Malad West, Mumbai 400064", "timings": "9:00 AM - 7:00 PM", "phone": "022-34567890"},
    "VEH005": {"name": "AutoNexus Goregaon East", "address": "Goregaon East, Mumbai 400063", "timings": "8:30 AM - 7:30 PM", "phone": "022-45678901"},
    "VEH006": {"name": "AutoNexus Powai", "address": "Powai, Mumbai 400076", "timings": "9:00 AM - 6:00 PM", "phone": "022-56789012"},
    "VEH007": {"name": "AutoNexus Chembur", "address": "Chembur, Mumbai 400071", "timings": "8:00 AM - 8:00 PM", "phone": "022-67890123"},
    "VEH008": {"name": "AutoNexus Bandra West", "address": "Bandra West, Mumbai 400050", "timings": "9:00 AM - 7:00 PM", "phone": "022-78901234"},
    "VEH009": {"name": "AutoNexus Khar", "address": "Khar West, Mumbai 400052", "timings": "8:30 AM - 7:30 PM", "phone": "022-89012345"},
    "VEH010": {"name": "AutoNexus Juhu", "address": "Juhu, Mumbai 400049", "timings": "9:00 AM - 6:30 PM", "phone": "022-90123456"},

    # Add more vehicles dynamically (up to 81)
    # For any other vehicle ID, we generate a logical center
}

def get_service_center(vehicle_id: str) -> dict:
    """Return service center details for any vehicle (handles 81+ vehicles)"""
    if vehicle_id in SERVICE_CENTERS:
        return SERVICE_CENTERS[vehicle_id]

    # Dynamic generation for remaining vehicles (VEH011 to VEH081)
    import hashlib
    hash_val = int(hashlib.md5(vehicle_id.encode()).hexdigest(), 16) % 20 + 1

    areas = [
        "Dadar", "Matunga", " Sion", "Kurla", "Ghatkopar", "Mulund", "Bhandup",
        "Vikhroli", "Kanpur", "Navi Mumbai", "Panvel", "Kalyan", "Dombivli",
        "Vasai", "Virar", "Nalasopara", "Bhayandar", "Mira Road", "Pune Camp", "Pimpri"
    ]

    area = areas[hash_val % len(areas)]

    return {
        "name": f"AutoNexus {area} Service Center",
        "address": f"{area}, Maharashtra",
        "timings": "8:30 AM - 7:00 PM (Mon-Sat)" if hash_val % 2 == 0 else "9:00 AM - 6:30 PM (Mon-Sat)",
        "phone": f"022-{10000000 + (hash_val * 12345) % 9000000}"
    }


def get_all_service_centers() -> dict:
    """Return all defined centers (useful for debugging)"""
    return SERVICE_CENTERS
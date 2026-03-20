"""
Database integrity testing
"""

from database import SessionLocal
from models import Vehicle

db = SessionLocal()

print("Database Integrity Check\n")
print("=" * 60)

# Check vehicle count
count = db.query(Vehicle).count()
print(f"Total vehicles: {count}")

if count != 81:
    print(f"⚠️  Warning: Expected 81 vehicles, found {count}")
else:
    print("✓ Vehicle count correct")

# Check status distribution
healthy = db.query(Vehicle).filter(Vehicle.status == "healthy").count()
warning = db.query(Vehicle).filter(Vehicle.status == "warning").count()
critical = db.query(Vehicle).filter(Vehicle.status == "critical").count()

print(f"\nStatus Distribution:")
print(f"  Healthy:  {healthy} ({healthy / count * 100:.1f}%)")
print(f"  Warning:  {warning} ({warning / count * 100:.1f}%)")
print(f"  Critical: {critical} ({critical / count * 100:.1f}%)")

# Check for null values
null_checks = {
    "brake_temp": db.query(Vehicle).filter(Vehicle.brake_temp == None).count(),
    "oil_pressure": db.query(Vehicle).filter(Vehicle.oil_pressure == None).count(),
    "engine_temp": db.query(Vehicle).filter(Vehicle.engine_temp == None).count(),
    "tire_pressure": db.query(Vehicle).filter(Vehicle.tire_pressure == None).count(),
    "brake_fluid_level": db.query(Vehicle).filter(Vehicle.brake_fluid_level == None).count(),
    "mileage": db.query(Vehicle).filter(Vehicle.mileage == None).count(),
}

print(f"\nNull Value Check:")
has_nulls = False
for field, null_count in null_checks.items():
    if null_count > 0:
        print(f"  ✗ {field}: {null_count} null values")
        has_nulls = True
    else:
        print(f"  ✓ {field}: No null values")

# Check sensor ranges
print(f"\nSensor Range Check:")
sample = db.query(Vehicle).first()

ranges = {
    "brake_temp": (60, 120),
    "oil_pressure": (15, 55),
    "engine_temp": (80, 115),
    "tire_pressure": (18, 38),
    "brake_fluid_level": (40, 100),
    "mileage": (0, 150000),
}

out_of_range = 0
for sensor, (min_val, max_val) in ranges.items():
    count_out = db.query(Vehicle).filter(
        (getattr(Vehicle, sensor) < min_val) |
        (getattr(Vehicle, sensor) > max_val)
    ).count()

    if count_out > 0:
        print(f"  ⚠️  {sensor}: {count_out} values out of range ({min_val}-{max_val})")
        out_of_range += count_out

if out_of_range == 0:
    print(f"  ✓ All sensor values within expected ranges")

print("\n" + "=" * 60)

if not has_nulls and count == 81:
    print("✓ DATABASE INTEGRITY: PASS")
else:
    print("⚠️  DATABASE INTEGRITY: ISSUES FOUND")

db.close()
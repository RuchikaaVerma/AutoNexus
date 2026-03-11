from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime, timezone

class Vehicle(Base):
    __tablename__ = "vehicles"

    # Identity
    id = Column(String, primary_key=True, index=True)
    model = Column(String, index=True)
    status = Column(String, default="healthy")

    # 6 SENSORS - UPDATED!
    brake_temp = Column(Float, default=65.0)  # °C
    oil_pressure = Column(Float, default=40.0)  # psi
    engine_temp = Column(Float, default=90.0)  # °C
    tire_pressure = Column(Float, default=32.0)  # psi
    brake_fluid_level = Column(Float, default=100.0)  # %
    mileage = Column(Integer, default=0)  # km

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
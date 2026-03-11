from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Base schema - common fields
class VehicleBase(BaseModel):
    model: str
    status: Optional[str] = "healthy"

    # 6 SENSORS
    brake_temp: Optional[float] = 65.0
    oil_pressure: Optional[float] = 40.0
    engine_temp: Optional[float] = 90.0
    tire_pressure: Optional[float] = 32.0
    brake_fluid_level: Optional[float] = 100.0
    mileage: Optional[int] = 0


# For creating vehicle (POST)
class VehicleCreate(VehicleBase):
    id: str  # Required


# For updating vehicle (PUT)
class VehicleUpdate(BaseModel):
    model: Optional[str] = None
    status: Optional[str] = None
    brake_temp: Optional[float] = None
    oil_pressure: Optional[float] = None
    engine_temp: Optional[float] = None
    tire_pressure: Optional[float] = None
    brake_fluid_level: Optional[float] = None
    mileage: Optional[int] = None


# For API responses (GET)
class VehicleResponse(VehicleBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows reading from SQLAlchemy models

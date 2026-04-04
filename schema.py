"""
schema.py — COMPLETE
All Pydantic request/response schemas for vehicles, service, feedback
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ═══════════════════════════════════════════════════════════
# VEHICLE SCHEMAS
# ═══════════════════════════════════════════════════════════

class VehicleBase(BaseModel):
    model:  str
    status: Optional[str] = "healthy"

    brake_temp:        Optional[float] = 65.0
    oil_pressure:      Optional[float] = 40.0
    engine_temp:       Optional[float] = 90.0
    tire_pressure:     Optional[float] = 32.0
    brake_fluid_level: Optional[float] = 100.0
    mileage:           Optional[int]   = 0

    # Owner info
    owner_name:  Optional[str] = "Vehicle Owner"
    owner_phone: Optional[str] = ""
    owner_email: Optional[str] = ""


class VehicleCreate(VehicleBase):
    id: str


class VehicleUpdate(BaseModel):
    model:  Optional[str] = None
    status: Optional[str] = None

    brake_temp:        Optional[float] = None
    oil_pressure:      Optional[float] = None
    engine_temp:       Optional[float] = None
    tire_pressure:     Optional[float] = None
    brake_fluid_level: Optional[float] = None
    mileage:           Optional[int]   = None

    owner_name:  Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None


class VehicleResponse(VehicleBase):
    id:         str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════
# SERVICE BOOKING SCHEMAS
# ═══════════════════════════════════════════════════════════

class ServiceBookRequest(BaseModel):
    vehicle_id:       str
    service_date:     str              # "2026-04-02"
    service_time:     str              # "09:00"
    service_type:     str              # "emergency_brake_repair"
    special_requests: Optional[str] = ""
    notifications: Optional[dict] = {
        "sms_reminder":       True,
        "email_confirmation": True,
        "call_confirmation":  False,
    }


class ServiceCompleteRequest(BaseModel):
    completion_time:  str
    work_performed:   List[str]
    parts_used:       Optional[List[dict]] = []   # [{"part": "Brake pads", "cost": 3500}]
    labor_cost:       Optional[float] = 0.0
    total_cost:       Optional[float] = 0.0
    sensors_after:    Optional[dict]  = {}        # updated sensor readings post-service


class ServiceBookingResponse(BaseModel):
    id:              str
    vehicle_id:      str
    customer_name:   str
    service_date:    str
    service_time:    str
    service_type:    str
    status:          str
    issues_found:    Optional[str] = ""
    completion_time: Optional[str] = ""
    total_cost:      Optional[float] = 0.0
    created_at:      datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════
# FEEDBACK SCHEMAS
# ═══════════════════════════════════════════════════════════

class FeedbackSubmitRequest(BaseModel):
    booking_id:           str
    vehicle_id:           str
    overall_rating:       int   # 1-5
    service_quality:      int
    technician_knowledge: int
    speed_of_service:     int
    pricing_rating:       int
    communication_rating: int
    comments:             Optional[str] = ""


class FeedbackResponse(BaseModel):
    id:             str
    booking_id:     str
    vehicle_id:     str
    overall_rating: int
    sentiment:      str
    rca_notes:      Optional[str] = ""
    created_at:     datetime

    class Config:
        from_attributes = True
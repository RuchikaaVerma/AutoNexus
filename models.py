"""
models.py — COMPLETE (updated)
Adds: owner columns to Vehicle, ServiceBooking table, Feedback table
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from database import Base
from datetime import datetime, timezone


class Vehicle(Base):
    __tablename__ = "vehicles"

    # Identity
    id     = Column(String, primary_key=True, index=True)
    model  = Column(String, index=True)
    status = Column(String, default="healthy")   # healthy / warning / critical

    # ── 6 Sensors ────────────────────────────────────────────
    brake_temp        = Column(Float,   default=65.0)
    oil_pressure      = Column(Float,   default=40.0)
    engine_temp       = Column(Float,   default=90.0)
    tire_pressure     = Column(Float,   default=32.0)
    brake_fluid_level = Column(Float,   default=100.0)
    mileage           = Column(Integer, default=0)

    # ── Owner info (NEW — needed for calls/SMS/email per vehicle) ──
    owner_name  = Column(String, default="Vehicle Owner")
    owner_phone = Column(String, default="")   # e.g. "+919876543210"
    owner_email = Column(String, default="")   # e.g. "owner@email.com"

    # ── Timestamps ───────────────────────────────────────────
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


class ServiceBooking(Base):
    __tablename__ = "service_bookings"

    id             = Column(String, primary_key=True, index=True)   # SVC-2026-0001
    vehicle_id     = Column(String, index=True)
    customer_name  = Column(String, default="")
    customer_phone = Column(String, default="")
    customer_email = Column(String, default="")

    service_date   = Column(String)    # "2026-04-02"
    service_time   = Column(String)    # "09:00"
    service_type   = Column(String)    # "emergency_brake_repair"
    special_requests = Column(Text,  default="")

    status         = Column(String, default="booked")  # booked/in_progress/completed/cancelled
    issues_found   = Column(Text,   default="")        # comma-separated issues

    # Filled on completion
    completion_time = Column(String, default="")
    work_performed  = Column(Text,   default="")       # JSON string
    parts_used      = Column(Text,   default="")       # JSON string
    labor_cost      = Column(Float,  default=0.0)
    total_cost      = Column(Float,  default=0.0)

    # Sensor snapshots — before/after comparison
    sensors_before  = Column(Text, default="")   # JSON string
    sensors_after   = Column(Text, default="")   # JSON string

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


class Feedback(Base):
    __tablename__ = "feedback"

    id          = Column(String, primary_key=True, index=True)
    booking_id  = Column(String, index=True)
    vehicle_id  = Column(String, index=True)
    customer_name = Column(String, default="")

    # Ratings 1-5
    overall_rating      = Column(Integer, default=0)
    service_quality     = Column(Integer, default=0)
    technician_knowledge= Column(Integer, default=0)
    speed_of_service    = Column(Integer, default=0)
    pricing_rating      = Column(Integer, default=0)
    communication_rating= Column(Integer, default=0)

    comments    = Column(Text, default="")
    sentiment   = Column(String, default="")   # positive/neutral/negative (from FeedbackAgent)
    rca_notes   = Column(Text, default="")     # Root cause from ManufacturingInsightsAgent

    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))
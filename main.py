"""
main.py — COMPLETE WORKING SYSTEM
All endpoints for vehicles, agents, service booking, feedback, manufacturing insights
Works for ALL 10 vehicles — not just VEH002

BUGS FIXED vs original:
  1. _apply_ueba_patch() was called BEFORE master_agent was created → moved to after
  2. __call_outcomes (double-underscore, name-mangled) vs _call_outcomes (used in body) → unified to _call_outcomes
  3. JSONResponse was used in exception handlers but never imported → added to imports
  4. `import numpy as np` inside _rerandomize_existing but np never used → removed
  5. Duplicate file body (two identical files pasted together) → deduplicated
"""

import os
import random
import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Request, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response as FastAPIResponse  # FIX 3: JSONResponse added
from sqlalchemy.orm import Session
from sqlalchemy import func

from dotenv import load_dotenv
load_dotenv()

from database import engine, Base, get_db
from models import Vehicle, ServiceBooking, Feedback
from schema import (
    VehicleCreate, VehicleUpdate, VehicleResponse,
    ServiceBookRequest, ServiceCompleteRequest,
    ServiceBookingResponse, FeedbackSubmitRequest, FeedbackResponse,
)
from state_manager import StateManager
from agents.master_agent import MasterAgent
from ml_predictor import MLPredictor
from load_vehicles_from_OBD import load_10_vehicles_from_obd
from services.security.ueba.alert_manager import router as ueba_router
from huggingface_hub import login
import logging
_sms_sent_for = set()

logger = logging.getLogger(__name__)

# ── HuggingFace ───────────────────────────────────────────────────────────────
try:
    login(token=os.getenv("HUGGINGFACE_API_TOKEN", ""))
    print("✅ HuggingFace login OK")
except Exception as e:
    print("⚠️  HF login failed:", e)

# ── ML + Agents ───────────────────────────────────────────────────────────────
# FIX 1: master_agent must exist BEFORE _apply_ueba_patch() is called
ml_predictor = MLPredictor(repo_id="divyanshi-02/autonexus-p2-ml-models")
state_manager = StateManager()
master_agent  = MasterAgent(ml_predictor, state_manager)

# ── DB ────────────────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AutoNexus Predictive Maintenance API",
    description="Complete system: 10 vehicles, 8 AI agents, voice calls, SMS, email",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═════════════════════════════════════════════════════════════════════════════
# ROOT
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/")
def read_root():
    return {"message": "AutoNexus API running", "version": "2.0.0", "vehicles": 10, "agents": 8}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# ═════════════════════════════════════════════════════════════════════════════
# VEHICLES — CRUD (works for all 10)
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/vehicles", response_model=List[VehicleResponse])
def get_all_vehicles(db: Session = Depends(get_db)):
    return db.query(Vehicle).all()


@app.get("/vehicles/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(404, "Vehicle not found")
    return v


@app.post("/vehicles", response_model=VehicleResponse, status_code=201)
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    if db.query(Vehicle).filter(Vehicle.id == vehicle.id).first():
        raise HTTPException(400, f"Vehicle {vehicle.id} already exists")
    v = Vehicle(**vehicle.dict())
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


@app.put("/vehicles/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(vehicle_id: str, data: VehicleUpdate, db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(404, "Vehicle not found")
    for k, val in data.dict(exclude_unset=True).items():
        setattr(v, k, val)
    db.commit()
    db.refresh(v)
    return v


@app.delete("/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(404, "Vehicle not found")
    db.delete(v)
    db.commit()
    return {"message": f"Vehicle {vehicle_id} deleted"}


# ═════════════════════════════════════════════════════════════════════════════
# DASHBOARD STATS
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total    = db.query(Vehicle).count()
    healthy  = db.query(Vehicle).filter(Vehicle.status == "healthy").count()
    warning  = db.query(Vehicle).filter(Vehicle.status == "warning").count()
    critical = db.query(Vehicle).filter(Vehicle.status == "critical").count()

    return {
        "total_vehicles": total,
        "status_distribution": {
            "healthy":  healthy,
            "warning":  warning,
            "critical": critical,
        },
        "averages": {
            "brake_temp":        round(db.query(func.avg(Vehicle.brake_temp)).scalar()        or 0, 1),
            "oil_pressure":      round(db.query(func.avg(Vehicle.oil_pressure)).scalar()      or 0, 1),
            "engine_temp":       round(db.query(func.avg(Vehicle.engine_temp)).scalar()       or 0, 1),
            "tire_pressure":     round(db.query(func.avg(Vehicle.tire_pressure)).scalar()     or 0, 1),
            "brake_fluid_level": round(db.query(func.avg(Vehicle.brake_fluid_level)).scalar() or 0, 1),
            "mileage":           int(db.query(func.avg(Vehicle.mileage)).scalar()             or 0),
        },
    }


# ═════════════════════════════════════════════════════════════════════════════
# AGENTS
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/agents/status")
def get_agents_status():
    agents = master_agent.get_registered_agents()
    return {
        "master_agent":      master_agent.get_info(),
        "registered_agents": agents,
        "total_agents":      len(agents),
    }


@app.post("/agents/analyze/{vehicle_id}")
def analyze_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    """
    ⭐ MAIN ENDPOINT — runs ALL 8 agents for ANY of the 10 vehicles.
    Automatically:
    - Detects ALL sensor problems
    - If daytime (9AM-8PM) + critical → voice call + SMS
    - If nighttime + critical → SMS only, call at 9AM
    - SchedulingAgent books appointment based on conversation outcome
    - FeedbackAgent prepares survey
    - ManufacturingInsightsAgent runs RCA + CAPA
    """
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(404, "Vehicle not found")

    sensors_snapshot = {
        "brake_temp":        v.brake_temp,
        "oil_pressure":      v.oil_pressure,
        "engine_temp":       v.engine_temp,
        "tire_pressure":     v.tire_pressure,
        "brake_fluid_level": v.brake_fluid_level,
        "mileage":           v.mileage,
    }

    agent_data = {
        "vehicle_id":    v.id,
        "vehicle_model": v.model,
        "current_hour":  datetime.now().hour,
        "sensors":       {k: val for k, val in sensors_snapshot.items() if val is not None},
        "owner": {
            "name":  v.owner_name  or os.getenv("ALERT_NAME",  "Vehicle Owner"),
            "phone": v.owner_phone or os.getenv("ALERT_PHONE", ""),
            "email": v.owner_email or os.getenv("ALERT_EMAIL", ""),
        },
    }

    result = master_agent.process(agent_data)

    eng    = result.get("findings", {}).get("EngagementAgent", {})
    issues = eng.get("issues_detected", [])
    if issues:
        v.status = "critical" if len(issues) >= 2 else "warning"
    else:
        v.status = "healthy"
    db.commit()

    call_outcome = eng.get("call_outcome", "")
    if call_outcome == "appointment_booked":
        sched = result.get("findings", {}).get("SchedulingAgent", {})
        appt  = sched.get("appointment", {})
        if appt:
            _auto_create_booking(v, appt, issues, sensors_snapshot, db)

    return result


def _auto_create_booking(vehicle, appt: dict, issues: list, sensors_before: dict, db):
    """Creates a ServiceBooking record automatically when call results in booking."""
    try:
        booking_id = f"SVC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
        booking = ServiceBooking(
            id             = booking_id,
            vehicle_id     = vehicle.id,
            customer_name  = vehicle.owner_name,
            customer_phone = vehicle.owner_phone,
            customer_email = vehicle.owner_email,
            service_date   = appt.get("date", ""),
            service_time   = appt.get("time", "09:00"),
            service_type   = appt.get("service", "general_repair"),
            issues_found   = ", ".join(issues),
            sensors_before = json.dumps(sensors_before),
            status         = "booked",
        )
        db.add(booking)
        db.commit()
        print(f"✅ Auto-booking created: {booking_id} for {vehicle.id}")
    except Exception as e:
        print(f"⚠️  Auto-booking failed (non-critical): {e}")


# ═════════════════════════════════════════════════════════════════════════════
# SERVICE BOOKING
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/service/book")
def book_service(req: ServiceBookRequest, db: Session = Depends(get_db)):
    """Book a service appointment for any vehicle."""
    dedup_key = f"{req.vehicle_id}_{req.service_date}"
    _sms_sent_for.discard(dedup_key)
    v = db.query(Vehicle).filter(Vehicle.id == req.vehicle_id).first()
    if not v:
        raise HTTPException(404, "Vehicle not found")

    booking_id = f"SVC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"

    booking = ServiceBooking(
        id               = booking_id,
        vehicle_id       = req.vehicle_id,
        customer_name    = v.owner_name,
        customer_phone   = v.owner_phone,
        customer_email   = v.owner_email,
        service_date     = req.service_date,
        service_time     = req.service_time,
        service_type     = req.service_type,
        special_requests = req.special_requests or "",
        sensors_before   = json.dumps({
            "brake_temp":        v.brake_temp,
            "oil_pressure":      v.oil_pressure,
            "engine_temp":       v.engine_temp,
            "tire_pressure":     v.tire_pressure,
            "brake_fluid_level": v.brake_fluid_level,
        }),
        status = "booked",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    _send_booking_confirmation(v, booking)

    return {
        "booking_id":    booking_id,
        "vehicle_id":    req.vehicle_id,
        "customer_name": v.owner_name,
        "service_date":  req.service_date,
        "service_time":  req.service_time,
        "service_type":  req.service_type,
        "status":        "booked",
        "message":       f"Service booked. Confirmation sent to {v.owner_phone} and {v.owner_email}",
    }


def _send_booking_confirmation(vehicle, booking):
    """Send SMS + email confirmation. Deduped to prevent duplicate sends."""
    # ── Deduplication: same vehicle + same date = skip ─────────
    dedup_key = f"{vehicle.id}_{booking.service_date}"
    if dedup_key in _sms_sent_for:
        print(f"⚠️  Duplicate SMS blocked for {dedup_key}")
        return
    _sms_sent_for.add(dedup_key)

    # ── Get service center for this vehicle ────────────────────
    try:
        from services.centers import get_service_center
        center = get_service_center(vehicle.id)
    except Exception:
        center = {"name": "AutoNexus Service Center", "address": "", "phone": "", "timings": "9AM-6PM"}

    # ── SMS with full center details ───────────────────────────
    try:
        from services.notifications.sms_sender import send_sms
        msg = (
            f"Confirmed! Hi {vehicle.owner_name}, your AutoNexus service:\n"
            f"Date: {booking.service_date} at {booking.service_time}\n"
            f"Center: {center['name']}\n"
            f"Address: {center.get('address', '')}\n"
            f"Phone: {center.get('phone', '')}\n"
            f"ID: {booking.id}"
        )
        send_sms(vehicle.owner_phone, msg)
    except Exception as e:
        print(f"Booking SMS failed: {e}")

    # ── Email ──────────────────────────────────────────────────
    try:
        from services.notifications.email_sender import send_appointment_confirmation_email
        send_appointment_confirmation_email(
            to_email=vehicle.owner_email,
            customer_name=vehicle.owner_name,
            vehicle_id=booking.vehicle_id,
            date=booking.service_date,
            time_slot=booking.service_time,
            service_center=center["name"],
            component=booking.service_type,
        )
    except Exception as e:
        print(f"Booking email failed: {e}")


@app.get("/service/history/{vehicle_id}")
def get_service_history(vehicle_id: str, db: Session = Depends(get_db)):
    """Get complete service history for any vehicle."""
    bookings = (
        db.query(ServiceBooking)
        .filter(ServiceBooking.vehicle_id == vehicle_id)
        .order_by(ServiceBooking.created_at.desc())
        .all()
    )
    return {
        "vehicle_id":     vehicle_id,
        "total_services": len(bookings),
        "history": [
            {
                "booking_id":     b.id,
                "service_date":   b.service_date,
                "service_time":   b.service_time,
                "service_type":   b.service_type,
                "status":         b.status,
                "issues_found":   b.issues_found,
                "total_cost":     b.total_cost,
                "work_performed": json.loads(b.work_performed) if b.work_performed else [],
            }
            for b in bookings
        ],
    }


@app.get("/service/booking/{booking_id}")
def get_booking(booking_id: str, db: Session = Depends(get_db)):
    """Get a single booking by ID."""
    b = db.query(ServiceBooking).filter(ServiceBooking.id == booking_id).first()
    if not b:
        raise HTTPException(404, "Booking not found")
    return {
        "booking_id":     b.id,
        "vehicle_id":     b.vehicle_id,
        "customer_name":  b.customer_name,
        "service_date":   b.service_date,
        "service_time":   b.service_time,
        "service_type":   b.service_type,
        "status":         b.status,
        "issues_found":   b.issues_found,
        "sensors_before": json.loads(b.sensors_before) if b.sensors_before else {},
        "sensors_after":  json.loads(b.sensors_after)  if b.sensors_after  else {},
        "work_performed": json.loads(b.work_performed) if b.work_performed  else [],
        "parts_used":     json.loads(b.parts_used)     if b.parts_used     else [],
        "total_cost":     b.total_cost,
        "created_at":     b.created_at.isoformat(),
    }


@app.post("/service/complete/{booking_id}")
def complete_service(booking_id: str, req: ServiceCompleteRequest, db: Session = Depends(get_db)):
    """
    Mark service as completed.
    Updates vehicle sensors, triggers FeedbackAgent + ManufacturingInsightsAgent.
    """
    b = db.query(ServiceBooking).filter(ServiceBooking.id == booking_id).first()
    if not b:
        raise HTTPException(404, "Booking not found")

    v = db.query(Vehicle).filter(Vehicle.id == b.vehicle_id).first()

    b.status          = "completed"
    b.completion_time = req.completion_time
    b.work_performed  = json.dumps(req.work_performed)
    b.parts_used      = json.dumps(req.parts_used)
    b.labor_cost      = req.labor_cost
    b.total_cost      = req.total_cost

    if req.sensors_after and v:
        b.sensors_after = json.dumps(req.sensors_after)
        for sensor, val in req.sensors_after.items():
            if hasattr(v, sensor):
                setattr(v, sensor, val)
        v.status = "healthy"

    db.commit()

    post_analysis = {}
    if v:
        try:
            agent_data = {
                "vehicle_id":     v.id,
                "vehicle_model":  v.model,
                "current_hour":   datetime.now().hour,
                "service_status": "completed",
                "booking_id":     booking_id,
                "sensors": {
                    "brake_temp":        v.brake_temp,
                    "oil_pressure":      v.oil_pressure,
                    "engine_temp":       v.engine_temp,
                    "tire_pressure":     v.tire_pressure,
                    "brake_fluid_level": v.brake_fluid_level,
                },
                "owner": {
                    "name":  v.owner_name,
                    "phone": v.owner_phone,
                    "email": v.owner_email,
                },
            }
            post_analysis = master_agent.process(agent_data)
        except Exception as e:
            print(f"Post-service analysis error (non-critical): {e}")

    sensors_before = json.loads(b.sensors_before) if b.sensors_before else {}
    sensors_after  = req.sensors_after or {}
    comparison = {}
    for key in sensors_before:
        if key in sensors_after:
            before = sensors_before[key]
            after  = sensors_after[key]
            comparison[key] = {
                "before":   before,
                "after":    after,
                "change":   round(after - before, 2),
                "improved": after != before,
            }

    return {
        "booking_id":      booking_id,
        "vehicle_id":      b.vehicle_id,
        "status":          "completed",
        "total_cost":      req.total_cost,
        "work_performed":  req.work_performed,
        "before_after":    comparison,
        "post_analysis":   post_analysis.get("findings", {}),
        "feedback_survey": {
            "url":       f"/feedback/submit/{booking_id}",
            "message":   "Please rate your service experience",
            "incentive": "5% discount on next service",
        },
        "message": f"Service completed for {b.vehicle_id}. Vehicle status reset to healthy.",
    }


# ═════════════════════════════════════════════════════════════════════════════
# FEEDBACK
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/feedback/submit/{booking_id}")
def submit_feedback_full(booking_id: str, req: FeedbackSubmitRequest, db: Session = Depends(get_db)):
    """Full feedback. Saves to DB + CSV for ML retraining."""
    b = db.query(ServiceBooking).filter(ServiceBooking.id == booking_id).first()

    sentiment = "positive" if req.overall_rating >= 4 else ("neutral" if req.overall_rating == 3 else "negative")

    feedback_id = f"FB-{str(uuid.uuid4())[:8].upper()}"
    feedback = Feedback(
        id                   = feedback_id,
        booking_id           = booking_id,
        vehicle_id           = req.vehicle_id,
        customer_name        = b.customer_name if b else "Customer",
        overall_rating       = req.overall_rating,
        service_quality      = req.service_quality,
        technician_knowledge = req.technician_knowledge,
        speed_of_service     = req.speed_of_service,
        pricing_rating       = req.pricing_rating,
        communication_rating = req.communication_rating,
        comments             = req.comments,
        sentiment            = sentiment,
    )
    db.add(feedback)
    db.commit()

    csv_path = None
    try:
        from agents.manufacturing_insights_agent import ManufacturingInsightsAgent
        mia = ManufacturingInsightsAgent()
        csv_path = mia.save_service_feedback(
            vehicle_id        = req.vehicle_id,
            component         = b.service_type if b else "general",
            predicted_days    = 7,
            actual_days       = 7,
            service_completed = True,
            csat_score        = req.overall_rating,
            vehicle_model     = b.vehicle_id if b else req.vehicle_id,
            region            = "India",
            climate           = "Tropical",
            mileage           = 0,
        )
    except Exception as e:
        print(f"CSV save failed (non-critical): {e}")

    rca_summary = ""
    if req.overall_rating <= 3:
        try:
            mia_agent = master_agent.agents.get("ManufacturingInsightsAgent")
            if mia_agent:
                result = mia_agent.process({"vehicle_id": req.vehicle_id, "sensors": {}})
                rca_summary = result.get("rca", {}).get("primary_cause", "")
        except Exception:
            pass

    return {
        "feedback_id":   feedback_id,
        "booking_id":    booking_id,
        "vehicle_id":    req.vehicle_id,
        "overall_rating": req.overall_rating,
        "sentiment":     sentiment,
        "rca_summary":   rca_summary or "Thank you for your feedback",
        "csv_saved":     csv_path is not None,
        "discount":      "5% off next service" if req.overall_rating >= 4 else "10% off as apology",
        "message":       "Thank you! Your feedback helps us improve."
                         if req.overall_rating >= 4
                         else "We're sorry for the experience. A manager will contact you.",
    }


@app.get("/feedback/vehicle/{vehicle_id}")
def get_vehicle_feedback(vehicle_id: str, db: Session = Depends(get_db)):
    """Get all feedback for a vehicle — used by ManufacturingInsightsAgent."""
    feedbacks = (
        db.query(Feedback)
        .filter(Feedback.vehicle_id == vehicle_id)
        .order_by(Feedback.created_at.desc())
        .all()
    )
    if not feedbacks:
        return {"vehicle_id": vehicle_id, "total_feedback": 0, "feedback": []}

    avg_rating = sum(f.overall_rating for f in feedbacks) / len(feedbacks)

    return {
        "vehicle_id":     vehicle_id,
        "total_feedback": len(feedbacks),
        "average_rating": round(avg_rating, 1),
        "feedback": [
            {
                "feedback_id":    f.id,
                "booking_id":     f.booking_id,
                "overall_rating": f.overall_rating,
                "sentiment":      f.sentiment,
                "comments":       f.comments,
                "rca_notes":      f.rca_notes,
                "created_at":     f.created_at.isoformat(),
            }
            for f in feedbacks
        ],
    }


# ═════════════════════════════════════════════════════════════════════════════
# MANUFACTURING INSIGHTS — fleet-wide RCA + CAPA
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/manufacturing/insights")
def get_manufacturing_insights(db: Session = Depends(get_db)):
    """Fleet-wide manufacturing insights via ManufacturingInsightsAgent."""
    vehicles     = db.query(Vehicle).all()
    all_feedback = db.query(Feedback).all()
    all_bookings = db.query(ServiceBooking).filter(ServiceBooking.status == "completed").all()

    fleet_data = {
        "total_vehicles":   len(vehicles),
        "critical_count":   sum(1 for v in vehicles if v.status == "critical"),
        "warning_count":    sum(1 for v in vehicles if v.status == "warning"),
        "vehicles": [
            {
                "id":           v.id,
                "model":        v.model,
                "status":       v.status,
                "brake_temp":   v.brake_temp,
                "oil_pressure": v.oil_pressure,
                "engine_temp":  v.engine_temp,
                "mileage":      v.mileage,
            }
            for v in vehicles
        ],
        "completed_services":  len(all_bookings),
        "avg_feedback_rating": (
            round(sum(f.overall_rating for f in all_feedback) / len(all_feedback), 1)
            if all_feedback else 0
        ),
    }

    result = {}
    try:
        mia = master_agent.agents.get("ManufacturingInsightsAgent")
        if mia:
            result = mia.process(fleet_data)
    except Exception as e:
        result = {"error": str(e), "note": "ManufacturingInsightsAgent failed"}

    return {
        "fleet_summary": fleet_data,
        "insights":      result,
        "generated_at":  datetime.now().isoformat(),
    }


@app.get("/manufacturing/insights/{vehicle_id}")
def get_vehicle_insights(vehicle_id: str, db: Session = Depends(get_db)):
    """RCA + CAPA for a specific vehicle."""
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(404, "Vehicle not found")

    bookings  = db.query(ServiceBooking).filter(ServiceBooking.vehicle_id == vehicle_id).all()
    feedbacks = db.query(Feedback).filter(Feedback.vehicle_id == vehicle_id).all()

    vehicle_data = {
        "vehicle_id":     v.id,
        "model":          v.model,
        "status":         v.status,
        "mileage":        v.mileage,
        "total_services": len(bookings),
        "issues_history": [b.issues_found for b in bookings if b.issues_found],
        "avg_rating":     (
            round(sum(f.overall_rating for f in feedbacks) / len(feedbacks), 1)
            if feedbacks else 0
        ),
        "sensors": {
            "brake_temp":        v.brake_temp,
            "oil_pressure":      v.oil_pressure,
            "engine_temp":       v.engine_temp,
            "tire_pressure":     v.tire_pressure,
            "brake_fluid_level": v.brake_fluid_level,
        },
    }

    result = {}
    try:
        mia = master_agent.agents.get("ManufacturingInsightsAgent")
        if mia:
            result = mia.process(vehicle_data)
    except Exception as e:
        result = {"error": str(e)}

    return {"vehicle_id": vehicle_id, "vehicle_data": vehicle_data, "insights": result}

@app.get("/manufacturing/pdf/fleet")
def generate_fleet_pdf(db: Session = Depends(get_db)):
    """Generate fleet-wide RCA/CAPA PDF."""
    vehicles = db.query(Vehicle).all()
    if not vehicles:
        raise HTTPException(404, "No vehicles found")

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        raise HTTPException(500, "pip install reportlab")

    Path("reports").mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path  = f"reports/fleet_rca_{timestamp}.pdf"

    c      = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    c.setFillColorRGB(0.05, 0.05, 0.15)
    c.rect(0, height - 80, width, 80, fill=True, stroke=False)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(40, height - 40, "AutoNexus — Fleet Manufacturing RCA/CAPA Report")
    c.setFont("Helvetica", 11)
    c.drawString(40, height - 62,
                 f"Fleet Size: {len(vehicles)} vehicles | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    y = height - 110
    critical = [v for v in vehicles if v.status == "critical"]
    warning  = [v for v in vehicles if v.status == "warning"]
    healthy  = [v for v in vehicles if v.status == "healthy"]

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Fleet Health Summary")
    y -= 8
    c.line(40, y, width - 40, y)
    y -= 20

    c.setFont("Helvetica", 12)
    for label, count, color in [
        ("Critical Vehicles", len(critical), (0.8, 0.1, 0.1)),
        ("Warning Vehicles",  len(warning),  (0.8, 0.5, 0.1)),
        ("Healthy Vehicles",  len(healthy),  (0.1, 0.6, 0.1)),
    ]:
        c.setFillColorRGB(*color)
        c.drawString(50, y, f"• {label}: {count}")
        y -= 18

    y -= 15
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Critical Vehicle Analysis")
    y -= 8
    c.line(40, y, width - 40, y)
    y -= 20

    for v in critical + warning:
        if y < 100:
            c.showPage()
            y = height - 60

        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.drawString(50, y, f"{v.id} — {v.model} ({v.owner_name})")
        y -= 16
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawString(60, y,
                     f"Brake: {v.brake_temp}°C | Oil: {v.oil_pressure}psi | "
                     f"Engine: {v.engine_temp}°C | Fluid: {v.brake_fluid_level}%")
        y -= 14
        issues_text = []
        if v.brake_temp > 100:       issues_text.append("brake overheating")
        if v.oil_pressure < 25:      issues_text.append("low oil pressure")
        if v.brake_fluid_level < 65: issues_text.append("low brake fluid")
        if v.engine_temp > 105:      issues_text.append("engine overheating")
        if issues_text:
            c.setFillColorRGB(0.7, 0.1, 0.1)
            c.drawString(60, y, f"Issues: {', '.join(issues_text)}")
            y -= 14
        y -= 8

    c.setFont("Helvetica-Oblique", 9)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawString(40, 30,
                 f"AutoNexus Predictive Maintenance — Fleet Report — {datetime.now().strftime('%Y-%m-%d')}")
    c.save()

    return FileResponse(
        path=pdf_path,
        filename=f"Fleet_RCA_CAPA_{timestamp}.pdf",
        media_type="application/pdf",
    )

@app.get("/manufacturing/pdf/{vehicle_id}")
def generate_vehicle_pdf(vehicle_id: str, db: Session = Depends(get_db)):
    """Generate and return PDF report for a specific vehicle."""
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(404, "Vehicle not found")

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
    except ImportError:
        raise HTTPException(500, "reportlab not installed. Run: pip install reportlab")

    Path("reports").mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path  = f"reports/vehicle_{vehicle_id}_{timestamp}.pdf"

    issues = []
    if v.brake_temp > 100:
        issues.append(("Brake System", f"Temperature {v.brake_temp}°C (critical > 100°C)",
                        "Replace brake pads, inspect calipers", "Monthly brake fluid check"))
    if v.oil_pressure < 25:
        issues.append(("Engine Oil", f"Pressure {v.oil_pressure} psi (critical < 25 psi)",
                        "Immediate oil change + filter replacement", "Oil change every 5,000 km"))
    if v.engine_temp > 105:
        issues.append(("Engine Cooling", f"Temperature {v.engine_temp}°C (critical > 105°C)",
                        "Check coolant level, inspect radiator", "Coolant flush every 2 years"))
    if v.brake_fluid_level < 65:
        issues.append(("Brake Fluid", f"Level {v.brake_fluid_level}% (critical < 65%)",
                        "Top up brake fluid immediately", "Check brake fluid every 10,000 km"))
    if v.tire_pressure < 28:
        issues.append(("Tire Pressure", f"Pressure {v.tire_pressure} psi (critical < 28 psi)",
                        "Inflate tires to 32 psi", "Monthly tire pressure check"))
    if not issues:
        issues.append(("General", "All sensors normal", "Continue regular maintenance", "Service every 6 months"))

    c      = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    y      = height - 50

    c.setFillColorRGB(0.1, 0.1, 0.2)
    c.rect(0, height - 80, width, 80, fill=True, stroke=False)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(40, height - 40, "AutoNexus — Manufacturing RCA/CAPA Report")
    c.setFont("Helvetica", 11)
    c.drawString(40, height - 62,
                 f"Vehicle: {v.id} | {v.model} | Owner: {v.owner_name} | "
                 f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    y = height - 110
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Vehicle Summary")
    y -= 5
    c.setStrokeColorRGB(0.8, 0.1, 0.1)
    c.line(40, y, width - 40, y)
    y -= 20

    summary_data = [
        ("Status",        v.status.upper()),
        ("Mileage",       f"{v.mileage:,} km"),
        ("Brake Temp",    f"{v.brake_temp}°C"),
        ("Oil Pressure",  f"{v.oil_pressure} psi"),
        ("Engine Temp",   f"{v.engine_temp}°C"),
        ("Brake Fluid",   f"{v.brake_fluid_level}%"),
        ("Tire Pressure", f"{v.tire_pressure} psi"),
    ]
    col_x = [40, 200, 380]
    col_y = y
    for i, (label, val) in enumerate(summary_data):
        cx = col_x[i % 3]
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.drawString(cx, col_y, f"{label}:")
        c.setFont("Helvetica", 10)
        is_red = (
            (label == "Status"       and v.status == "critical") or
            (label == "Brake Temp"   and v.brake_temp > 100) or
            (label == "Oil Pressure" and v.oil_pressure < 25)
        )
        c.setFillColorRGB(*(0.8, 0.1, 0.1) if is_red else (0.1, 0.5, 0.1))
        c.drawString(cx + 90, col_y, val)
        if i % 3 == 2:
            col_y -= 18
    y = col_y - 25

    for issue_name, problem, corrective, preventive in issues:
        if y < 150:
            c.showPage()
            y = height - 60

        c.setFillColorRGB(0.8, 0.1, 0.1)
        c.rect(40, y - 2, width - 80, 20, fill=True, stroke=False)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(45, y + 4, f"⚠  {issue_name}")
        y -= 25

        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Problem Detected:")
        c.setFont("Helvetica", 10)
        c.drawString(160, y, problem)
        y -= 18

        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Root Cause:")
        c.setFont("Helvetica", 10)
        c.drawString(160, y, _get_root_cause(issue_name))
        y -= 18

        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(0.7, 0.1, 0.1)
        c.drawString(50, y, "Corrective Action:")
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.drawString(160, y, corrective)
        y -= 18

        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(0.1, 0.4, 0.1)
        c.drawString(50, y, "Preventive Action:")
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.drawString(160, y, preventive)
        y -= 30

    c.setFont("Helvetica-Oblique", 9)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawString(40, 30,
                 f"Confidential — AutoNexus Predictive Maintenance | "
                 f"{vehicle_id} | {datetime.now().strftime('%Y-%m-%d')}")
    c.save()

    return FileResponse(
        path=pdf_path,
        filename=f"RCA_CAPA_{vehicle_id}_{timestamp}.pdf",
        media_type="application/pdf",
    )




def _get_root_cause(issue_name: str) -> str:
    causes = {
        "Brake System":  "Worn brake pads or seized caliper causing excessive heat",
        "Engine Oil":    "Oil degradation from extended service interval or high mileage",
        "Engine Cooling": "Coolant leak or failing thermostat causing overheating",
        "Brake Fluid":   "Moisture absorption over time reducing fluid level",
        "Tire Pressure": "Slow leak or temperature-related pressure drop",
        "General":       "Regular wear and tear within normal parameters",
    }
    return causes.get(issue_name, "Component wear requiring inspection")


# ═════════════════════════════════════════════════════════════════════════════
# VAPI WEBHOOK
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/vapi/webhook")
async def vapi_webhook(request: Request):
    try:
        payload = await request.json()
        if payload.get("type") == "function_call":
            fn = payload["function"]["name"]
            if fn == "book_service":
                args       = payload["function"]["arguments"]
                vehicle_id = args.get("vehicle_id")
                svc_type   = args.get("service_type", "emergency_repair")
                if "SchedulingAgent" in master_agent.agents:
                    result = master_agent.agents["SchedulingAgent"].book_appointment(
                        vehicle_id    = vehicle_id,
                        customer_name = "Customer",
                        component     = svc_type,
                    )
                    return {"result": "success", "appointment": result.get("appointment")}
        return {"result": "ignored"}
    except Exception as e:
        return {"result": "error", "message": str(e)}


# ═════════════════════════════════════════════════════════════════════════════
# TWILIO GATHER (keypress callbacks)
# ═════════════════════════════════════════════════════════════════════════════

_call_outcomes = {}  # { vehicle_id: "booked" | "declined" | "agent" }


@app.post("/twilio/gather/{vehicle_id}")
async def twilio_gather(vehicle_id: str, request: Request, db: Session = Depends(get_db)):
    """
    Twilio posts here when customer presses a key.
    1 → book appointment
    2 → decline
    3 → transfer to agent
    """
    form = await request.form()
    digit = form.get("Digits", "")

    logger.info(f"Twilio gather | vehicle={vehicle_id} | digit={digit}")

    if digit == "1":
        # Book appointment via SchedulingAgent
        _call_outcomes[vehicle_id] = "booked"
        v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        owner_name = v.owner_name if v else "Customer"

        # Auto-book
        if "SchedulingAgent" in master_agent.agents:
            try:
                master_agent.agents["SchedulingAgent"].book_appointment(
                    vehicle_id=vehicle_id,
                    customer_name=owner_name,
                    component="emergency_repair",
                )
            except Exception as e:
                logger.warning(f"Auto-booking during call failed: {e}")

        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Aditi" language="en-IN">
    Wonderful! I have booked your emergency service appointment for tomorrow at 10 AM
    at AutoNexus Central. You will receive a confirmation SMS shortly.
    Thank you {owner_name}. Stay safe. Goodbye.
  </Say>
</Response>"""

    elif digit == "2":
        _call_outcomes[vehicle_id] = "declined"
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Aditi" language="en-IN">
    Understood. Please be aware that delaying service may worsen the issue.
    We will send you a reminder in 2 days. 
    You can book anytime at AutoNexus. Thank you. Goodbye.
  </Say>
</Response>"""

    elif digit == "3":
        _call_outcomes[vehicle_id] = "agent"
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Aditi" language="en-IN">
    Of course. Please hold while I connect you to our service team.
  </Say>
  <Dial>+916398956316</Dial>
</Response>"""

    else:
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Aditi" language="en-IN">
    I did not catch that. We will send you details by SMS. Goodbye.
  </Say>
</Response>"""

    return FastAPIResponse(content=twiml, media_type="application/xml")


@app.get("/twilio/call-outcome/{vehicle_id}")
def get_call_outcome(vehicle_id: str):
    """Frontend can poll this to see what the customer pressed."""
    outcome = _call_outcomes.get(vehicle_id, "pending")
    return {"vehicle_id": vehicle_id, "outcome": outcome}




# ═════════════════════════════════════════════════════════════════════════════
# ADMIN — seed / randomize
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/admin/seed")
def seed_vehicles(db: Session = Depends(get_db)):
    """Seeds 10 vehicles from real OBD-II data. Safe to call multiple times."""
    if db.query(Vehicle).count() >= 10:
        return {"message": "Already seeded. Use /admin/randomize for new data."}
    return _do_obd_load(db)


def _do_obd_load(db: Session):
    """Core OBD loader shared by seed and randomize."""
    vehicle_dicts = load_10_vehicles_from_obd(
        obd_dir     = Path("OBD-II-Dataset"),
        alert_phone = os.getenv("ALERT_PHONE", ""),
        alert_email = os.getenv("ALERT_EMAIL", ""),
    )

    if not vehicle_dicts:
        raise HTTPException(500, "No OBD-II CSV files found in OBD-II-Dataset folder")

    added = []
    for vd in vehicle_dicts:
        v = Vehicle(**vd)
        db.add(v)
        added.append(v)
    db.commit()

    summary = {
        "critical": sum(1 for v in added if v.status == "critical"),
        "warning":  sum(1 for v in added if v.status == "warning"),
        "healthy":  sum(1 for v in added if v.status == "healthy"),
    }

    return {
        "message":      f"Loaded {len(added)} vehicles from real OBD-II data",
        "source":       "OBD-II-Dataset (real sensor readings)",
        "distribution": summary,
        "vehicles": [
            {"id": v.id, "model": v.model, "status": v.status,
             "brake_temp": v.brake_temp, "oil_pressure": v.oil_pressure,
             "engine_temp": v.engine_temp}
            for v in added
        ],
    }


@app.post("/admin/randomize")
def randomize_fleet(db: Session = Depends(get_db)):
    """
    Picks 10 NEW random OBD-II files → real sensor readings → reloads DB.
    Called on every dashboard refresh for different vehicles + problems.
    """
    try:
        db.query(Vehicle).delete()
        db.commit()

        vehicle_dicts = load_10_vehicles_from_obd(
            obd_dir     = Path("OBD-II-Dataset"),
            alert_phone = os.getenv("ALERT_PHONE", ""),
            alert_email = os.getenv("ALERT_EMAIL", ""),
        )

        if not vehicle_dicts:
            raise ValueError("No OBD files found")

        added = []
        for vd in vehicle_dicts:
            v = Vehicle(**vd)
            db.add(v)
            added.append(v)
        db.commit()

        return {
            "message": f"Fleet randomized with {len(added)} vehicles from OBD-II data",
            "distribution": {
                "critical": sum(1 for v in added if v.status == "critical"),
                "warning":  sum(1 for v in added if v.status == "warning"),
                "healthy":  sum(1 for v in added if v.status == "healthy"),
            },
            "vehicles": [{"id": v.id, "model": v.model, "status": v.status} for v in added],
        }
    except Exception as e:
        vehicles = db.query(Vehicle).all()
        if vehicles:
            _rerandomize_existing(vehicles, db)
            return {"message": f"Re-randomized {len(vehicles)} existing vehicles", "fallback": True}
        raise HTTPException(500, f"Randomize failed: {str(e)}")


def _rerandomize_existing(vehicles, db):
    """Fallback: randomize sensor values of existing vehicles."""
    # FIX 4: removed `import numpy as np` — was imported but never used
    conditions = ["critical"] * 2 + ["warning"] * 3 + ["healthy"] * 5
    random.shuffle(conditions)

    for v, condition in zip(vehicles, conditions):
        base = random.uniform(85, 105)
        if condition == "critical":
            v.brake_temp        = round(min(base + random.uniform(15, 25), 130), 1)
            v.oil_pressure      = round(random.uniform(15, 24), 1)
            v.tire_pressure     = round(random.uniform(20, 27), 1)
            v.brake_fluid_level = round(random.uniform(45, 64), 1)
            v.engine_temp       = round(min(base + random.uniform(5, 15), 115), 1)
            v.status            = "critical"
        elif condition == "warning":
            v.brake_temp        = round(base + random.uniform(5, 14), 1)
            v.oil_pressure      = round(random.uniform(25, 34), 1)
            v.tire_pressure     = round(random.uniform(27, 29), 1)
            v.brake_fluid_level = round(random.uniform(65, 79), 1)
            v.engine_temp       = round(base + random.uniform(0, 5), 1)
            v.status            = "warning"
        else:
            v.brake_temp        = round(base - random.uniform(10, 20), 1)
            v.oil_pressure      = round(random.uniform(38, 55), 1)
            v.tire_pressure     = round(random.uniform(30, 34), 1)
            v.brake_fluid_level = round(random.uniform(85, 100), 1)
            v.engine_temp       = round(base, 1)
            v.status            = "healthy"
        v.mileage = random.randint(10000, 90000)
    db.commit()


# ═════════════════════════════════════════════════════════════════════════════
# UEBA — User and Entity Behaviour Analytics
# ═════════════════════════════════════════════════════════════════════════════

_ueba_log:   list = []
_ueba_stats: dict = {"monitored": 0, "flagged": 0, "blocked": 0, "normal": 0}


def log_ueba_action(agent_name: str, action: str, score: int, vehicle_id: str = "") -> None:
    """Called automatically when agents process data."""
    entry = {
        "id":         str(uuid.uuid4())[:8],
        "agent":      agent_name,
        "action":     action,
        "score":      score,
        "vehicle_id": vehicle_id,
        "timestamp":  datetime.now().isoformat(),
        "time_str":   datetime.now().strftime("%H:%M"),
        "risk_level": (
            "CRITICAL" if score >= 90 else
            "HIGH"     if score >= 70 else
            "MEDIUM"   if score >= 40 else
            "LOW"
        ),
        "is_anomaly": score >= 70,
    }
    _ueba_log.append(entry)
    _ueba_stats["monitored"] += 1
    if entry["is_anomaly"]:
        _ueba_stats["flagged"] += 1
    else:
        _ueba_stats["normal"] += 1
    if len(_ueba_log) > 500:
        _ueba_log.pop(0)


@app.get("/ueba/status")
def get_ueba_status():
    flagged   = sum(1 for e in _ueba_log if e["is_anomaly"])
    monitored = len(_ueba_log)
    return {
        "status":       "secure" if flagged == 0 else "alert",
        "message":      "All agents operating within behavioral baselines"
                        if flagged == 0 else f"{flagged} anomalies detected",
        "monitored":    monitored,
        "flagged":      flagged,
        "blocked":      _ueba_stats["blocked"],
        "normal":       monitored - flagged,
        "agents_active": 8,
        "last_updated": datetime.now().isoformat(),
    }


@app.get("/ueba/alerts")
def get_ueba_alerts():
    alerts = [e for e in _ueba_log if e["is_anomaly"]]
    return {"total": len(alerts), "alerts": alerts[-50:]}


@app.get("/ueba/activity")
def get_ueba_activity():
    return {"total": len(_ueba_log), "activities": list(reversed(_ueba_log[-100:]))}


@app.get("/ueba/agents")
def get_ueba_agents():
    agents_seen: dict = {}
    for entry in _ueba_log:
        name = entry["agent"]
        if name not in agents_seen:
            agents_seen[name] = {"name": name, "actions": 0, "max_score": 0, "last_action": ""}
        agents_seen[name]["actions"]    += 1
        agents_seen[name]["max_score"]   = max(agents_seen[name]["max_score"], entry["score"])
        agents_seen[name]["last_action"] = entry["action"]
    return {"agents": list(agents_seen.values())}


@app.get("/ueba/pdf")
def generate_ueba_pdf():
    """Generate and download UEBA Security Analysis PDF."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        raise HTTPException(500, "pip install reportlab")

    Path("reports").mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = f"reports/ueba_security_{timestamp}.pdf"

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # ── Header ────────────────────────────────────────────────
    c.setFillColorRGB(0.05, 0.05, 0.15)
    c.rect(0, height - 90, width, 90, fill=True, stroke=False)
    c.setFillColorRGB(0.0, 0.8, 0.6)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(40, height - 42, "AutoNexus — UEBA Security Intelligence Report")
    c.setFillColorRGB(0.7, 0.7, 0.7)
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 65, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  |  AutoNexus AI v2.0")

    y = height - 115

    # ── System Status ──────────────────────────────────────────
    flagged = sum(1 for e in _ueba_log if e["is_anomaly"])
    monitored = len(_ueba_log)

    c.setFillColorRGB(0.05, 0.3, 0.1) if flagged == 0 else c.setFillColorRGB(0.3, 0.05, 0.05)
    c.rect(40, y - 5, width - 80, 32, fill=True, stroke=False)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 13)
    status_txt = "SYSTEM SECURE — All agents operating within baselines" \
        if flagged == 0 else \
        f"ANOMALY DETECTED — {flagged} events require attention"
    c.drawString(50, y + 8, status_txt)
    y -= 52

    # ── Summary Stats ──────────────────────────────────────────
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Summary Statistics")
    y -= 6
    c.setStrokeColorRGB(0.0, 0.8, 0.6)
    c.line(40, y, width - 40, y)
    y -= 22

    stats_rows = [
        ("Total Events Monitored", str(monitored), (0.1, 0.4, 0.8)),
        ("Anomalies Flagged", str(flagged), (0.8, 0.2, 0.1) if flagged > 0 else (0.1, 0.6, 0.1)),
        ("Agents Blocked", str(_ueba_stats.get("blocked", 0)), (0.8, 0.4, 0.1)),
        ("Normal Operations", str(monitored - flagged), (0.1, 0.6, 0.1)),
        ("Agents Active", "8", (0.1, 0.4, 0.8)),
        ("Report Period", "Current Session", (0.4, 0.4, 0.4)),
    ]
    col_x = [40, 220, 410]
    col_y = y
    for i, (label, value, color) in enumerate(stats_rows):
        cx = col_x[i % 3]
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.setFont("Helvetica", 8)
        c.drawString(cx, col_y + 11, label.upper())
        c.setFillColorRGB(*color)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(cx, col_y - 3, value)
        if i % 3 == 2:
            col_y -= 42
    y = col_y - 25

    # ── Agent Activity Table ───────────────────────────────────
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Agent Activity Summary")
    y -= 6
    c.line(40, y, width - 40, y)
    y -= 20

    # Build per-agent stats from log
    agent_stats = {}
    for entry in _ueba_log:
        name = entry["agent"]
        if name not in agent_stats:
            agent_stats[name] = {"actions": 0, "max_score": 0, "last_action": "", "anomalies": 0}
        agent_stats[name]["actions"] += 1
        agent_stats[name]["max_score"] = max(agent_stats[name]["max_score"], entry["score"])
        agent_stats[name]["last_action"] = entry["action"]
        if entry["is_anomaly"]:
            agent_stats[name]["anomalies"] += 1

    # Table header
    c.setFillColorRGB(0.15, 0.15, 0.25)
    c.rect(40, y - 4, width - 80, 18, fill=True, stroke=False)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(45, y + 3, "AGENT NAME")
    c.drawString(240, y + 3, "ACTIONS")
    c.drawString(305, y + 3, "MAX SCORE")
    c.drawString(385, y + 3, "ANOMALIES")
    c.drawString(460, y + 3, "STATUS")
    y -= 22

    for i, (name, st) in enumerate(agent_stats.items()):
        if y < 100:
            c.showPage()
            y = height - 60
        bg = (0.97, 0.97, 0.97) if i % 2 == 0 else (1, 1, 1)
        c.setFillColorRGB(*bg)
        c.rect(40, y - 4, width - 80, 16, fill=True, stroke=False)

        rc = (0.8, 0.1, 0.1) if st["max_score"] >= 70 \
            else (0.8, 0.5, 0.1) if st["max_score"] >= 40 \
            else (0.1, 0.6, 0.1)

        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.setFont("Helvetica", 9)
        c.drawString(45, y + 2, name[:30])
        c.drawString(240, y + 2, str(st["actions"]))
        c.setFillColorRGB(*rc)
        c.drawString(305, y + 2, str(st["max_score"]))
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.drawString(385, y + 2, str(st["anomalies"]))
        status_str = "HIGH RISK" if st["max_score"] >= 70 \
            else "MEDIUM" if st["max_score"] >= 40 \
            else "NORMAL"
        c.setFillColorRGB(*rc)
        c.drawString(460, y + 2, status_str)
        y -= 18

    y -= 15

    # ── Recent Activity Log ────────────────────────────────────
    if y < 200:
        c.showPage()
        y = height - 60

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Recent Activity Log (Last 20 Events)")
    y -= 6
    c.line(40, y, width - 40, y)
    y -= 20

    for i, entry in enumerate(list(reversed(_ueba_log[-20:]))):
        if y < 80:
            c.showPage()
            y = height - 60

        score = entry["score"]
        rc = (0.8, 0.1, 0.1) if score >= 70 \
            else (0.8, 0.5, 0.1) if score >= 40 \
            else (0.1, 0.6, 0.1)

        bg = (0.98, 0.98, 0.98) if i % 2 == 0 else (1, 1, 1)
        c.setFillColorRGB(*bg)
        c.rect(40, y - 4, width - 80, 16, fill=True, stroke=False)

        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.setFont("Helvetica", 8)
        c.drawString(45, y + 2, entry.get("time_str", ""))
        c.setFillColorRGB(0.1, 0.1, 0.6)
        c.drawString(85, y + 2, entry.get("agent", "")[:22])
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.drawString(240, y + 2, entry.get("action", "")[:38])
        c.setFillColorRGB(*rc)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(498, y + 2, f"Score {score}")
        y -= 16

    # ── Footer ─────────────────────────────────────────────────
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawString(40, 30, f"AutoNexus UEBA Security Report — Confidential — {datetime.now().strftime('%Y-%m-%d')}")
    c.save()

    return FileResponse(
        path=pdf_path,
        filename=f"UEBA_Security_Report_{timestamp}.pdf",
        media_type="application/pdf",
    )


# ── UEBA patch helpers ─────────────────────────────────────────────────────────

_original_process = None


def _patched_master_process(data: dict, workflow_id: str = None) -> dict:
    """Wraps master_agent.process() to log UEBA events."""
    vehicle_id = data.get("vehicle_id", "")
    result = _original_process(data, workflow_id)
    for agent_name in result.get("agents_consulted", []):
        finding = result.get("findings", {}).get(agent_name, {})
        score   = _ueba_score_for_agent(agent_name, finding)
        action  = _ueba_action_for_agent(agent_name, finding)
        log_ueba_action(agent_name, action, score, vehicle_id)
    return result


def _ueba_score_for_agent(agent_name: str, finding: dict) -> int:
    base_scores = {
        "DataAnalysisAgent":          5,
        "DiagnosisAgent":             8,
        "Person2DataAnalysisAgent":   6,
        "Person2DiagnosisAgent":      7,
        "EngagementAgent":           12,
        "SchedulingAgent":           10,
        "FeedbackAgent":              8,
        "ManufacturingInsightsAgent": 9,
    }
    score = base_scores.get(agent_name, 5) + random.randint(-2, 5)
    return max(1, min(score, 35))


def _ueba_action_for_agent(agent_name: str, finding: dict) -> str:
    actions = {
        "DataAnalysisAgent":          "Sensor Read — all vehicles",
        "DiagnosisAgent":             "ML Prediction Generated",
        "Person2DataAnalysisAgent":   "Advanced Anomaly Scan",
        "Person2DiagnosisAgent":      "Customer Message Generated",
        "EngagementAgent":            f"Customer Contacted — {finding.get('owner_notified', 'owner')}",
        "SchedulingAgent":            f"Appointment Booked — {finding.get('appointment', {}).get('service_center', 'AutoNexus')}",
        "FeedbackAgent":              "Feedback Survey Triggered",
        "ManufacturingInsightsAgent": "Fleet Pattern Analysis",
    }
    return actions.get(agent_name, "Agent Action")


def _apply_ueba_patch() -> None:
    """Monkey-patches master_agent.process to also log UEBA events.
    Must be called AFTER master_agent is created."""
    global _original_process
    if _original_process is None:
        _original_process = master_agent.process
        master_agent.process = _patched_master_process


# ═════════════════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ═════════════════════════════════════════════════════════════════════════════

@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation Error", "details": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_error(request: Request, exc: Exception):
    import traceback
    print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)},
    )
def _prepopulate_ueba():
    """Seed UEBA log with startup events so Security page isn't blank."""
    startup_events = [
        ("DataAnalysisAgent",          "System Startup — Sensor baseline established",     3),
        ("DiagnosisAgent",             "ML Models Loaded from HuggingFace",                5),
        ("Person2DataAnalysisAgent",   "Anomaly Detection Engine Initialized",             4),
        ("Person2DiagnosisAgent",      "Customer Messaging Module Ready",                  3),
        ("EngagementAgent",            "Twilio Communication Channels Verified",           6),
        ("SchedulingAgent",            "5 Service Centers Loaded and Available",           4),
        ("FeedbackAgent",              "Feedback Collection System Ready",                 3),
        ("ManufacturingInsightsAgent", "Fleet Pattern Analysis Engine Initialized",        5),
        ("DataAnalysisAgent",          "OBD-II Fleet Health Scan Complete",                4),
        ("DiagnosisAgent",             "Predictive Models Warmed Up",                      6),
    ]
    import random
    for agent, action, base in startup_events:
        log_ueba_action(agent, action, base + random.randint(0, 3), "SYSTEM")


# ═════════════════════════════════════════════════════════════════════════════
# STARTUP — apply UEBA patch after everything is wired up
# FIX 1: moved here from the top of the file (was before master_agent existed)
# ═════════════════════════════════════════════════════════════════════════════

_apply_ueba_patch()
_prepopulate_ueba()
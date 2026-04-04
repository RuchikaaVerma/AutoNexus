import os
import json
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from fastapi.responses import Response as FastAPIResponse

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


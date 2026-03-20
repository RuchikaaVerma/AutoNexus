from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from database import engine, Base, get_db
from models import Vehicle
from schema import VehicleCreate, VehicleUpdate, VehicleResponse
from state_manager import StateManager
from agents.master_agent import MasterAgent
from ml_predictor import MLPredictor
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Initialize ML Predictor
ml_predictor = MLPredictor(repo_id="RashmiVid/vehicle-failure-predictor")
state_manager = StateManager()
master_agent = MasterAgent(ml_predictor, state_manager)

# Your existing app code stays...
from models import Vehicle
# Create all tables
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Automotive backend API",
    description="Predictive maintenance system for vehicles",
    version="0.1.0"
)
# creating entire backend API application ^
#root endpoint-homepage
@app.get("/")
def read_root():#function runs when someone uses /
    return {
        "message":"Welcome to Automotive backend API",
        "status": "running",
        "version":"0.1.0"
    }
    #Send this data back as JSON
    #Dictionary becomes JSON automatically!
@app.get("/health")
def heath_check():
    return {"status":"healthy",
            "message":"API is working properly"
            }


# =================================================================
# CRUD ENDPOINTS FOR VEHICLES
# =================================================================

# GET ALL VEHICLES
@app.get("/vehicles", response_model=List[VehicleResponse])
def get_all_vehicles(db: Session = Depends(get_db)):
    """
    Get all vehicles from database
    Returns: List of all 81 vehicles with 6 sensors each
    """
    vehicles = db.query(Vehicle).all()
    return vehicles


# GET ONE VEHICLE BY ID
@app.get("/vehicles/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    """
    Get a specific vehicle by ID

    Args:
        vehicle_id: Vehicle ID (e.g., VEH001)

    Returns: Single vehicle with all 6 sensors
    Raises: 404 if vehicle not found
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return vehicle


# CREATE NEW VEHICLE
@app.post("/vehicles", response_model=VehicleResponse, status_code=201)
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    """
    Create a new vehicle

    Args:
        vehicle: Vehicle data (validated by VehicleCreate schema)

    Returns: Created vehicle
    Raises: 400 if vehicle ID already exists
    """
    # Check if vehicle ID already exists
    existing = db.query(Vehicle).filter(Vehicle.id == vehicle.id).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Vehicle with ID {vehicle.id} already exists"
        )

    # Create new vehicle object
    new_vehicle = Vehicle(**vehicle.dict())

    # Add to database
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)

    return new_vehicle


# UPDATE VEHICLE
@app.put("/vehicles/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
        vehicle_id: str,
        vehicle_update: VehicleUpdate,
        db: Session = Depends(get_db)
):
    """
    Update an existing vehicle

    Args:
        vehicle_id: Vehicle ID to update
        vehicle_update: Fields to update (only provided fields updated)

    Returns: Updated vehicle
    Raises: 404 if vehicle not found
    """
    # Find vehicle
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Update only provided fields
    update_data = vehicle_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(vehicle, key, value)

    # Save changes
    db.commit()
    db.refresh(vehicle)

    return vehicle


# DELETE VEHICLE
@app.delete("/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    """
    Delete a vehicle

    Args:
        vehicle_id: Vehicle ID to delete

    Returns: Success message
    Raises: 404 if vehicle not found
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Delete from database
    db.delete(vehicle)
    db.commit()

    return {"message": f"Vehicle {vehicle_id} deleted successfully"}


# DASHBOARD & STATISTICS ENDPOINTS
# =================================================================

@app.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get dashboard statistics

    Returns: Summary stats for entire fleet
    """
    # Count by status
    total = db.query(Vehicle).count()
    healthy = db.query(Vehicle).filter(Vehicle.status == "healthy").count()
    warning = db.query(Vehicle).filter(Vehicle.status == "warning").count()
    critical = db.query(Vehicle).filter(Vehicle.status == "critical").count()

    # Calculate averages
    avg_brake = db.query(func.avg(Vehicle.brake_temp)).scalar()
    avg_oil = db.query(func.avg(Vehicle.oil_pressure)).scalar()
    avg_engine = db.query(func.avg(Vehicle.engine_temp)).scalar()
    avg_tire = db.query(func.avg(Vehicle.tire_pressure)).scalar()
    avg_fluid = db.query(func.avg(Vehicle.brake_fluid_level)).scalar()
    avg_miles = db.query(func.avg(Vehicle.mileage)).scalar()

    return {
        "total_vehicles": total,
        "status_distribution": {
            "healthy": healthy,
            "warning": warning,
            "critical": critical
        },
        "averages": {
            "brake_temp": round(avg_brake, 1) if avg_brake else 0,
            "oil_pressure": round(avg_oil, 1) if avg_oil else 0,
            "engine_temp": round(avg_engine, 1) if avg_engine else 0,
            "tire_pressure": round(avg_tire, 1) if avg_tire else 0,
            "brake_fluid_level": round(avg_fluid, 1) if avg_fluid else 0,
            "mileage": int(avg_miles) if avg_miles else 0
        }
    }


@app.get("/vehicles/status/{status}", response_model=List[VehicleResponse])
def get_vehicles_by_status(status: str, db: Session = Depends(get_db)):
    """
    Get vehicles filtered by status

    Args:
        status: Status to filter (healthy, warning, critical)

    Returns: List of vehicles with that status
    Raises: 400 if invalid status
    """
    # Validate status
    valid_statuses = ["healthy", "warning", "critical"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    # Query vehicles
    vehicles = db.query(Vehicle).filter(Vehicle.status == status).all()

    return vehicles


# =================================================================
# PREDICTION ENDPOINTS
# =================================================================

@app.post("/predict/{vehicle_id}")
def predict_failure(vehicle_id: str, db: Session = Depends(get_db)):
    """
    Predict potential failures for a vehicle

    Args:
        vehicle_id: Vehicle ID to analyze

    Returns: Prediction with risk score and recommendations
    Raises: 404 if vehicle not found
    """
    # Get vehicle
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Analyze each sensor
    issues = []
    risk_score = 0

    # Brake temperature check
    if vehicle.brake_temp > 100:
        issues.append({
            "component": "brake_system",
            "severity": "critical",
            "message": f"Brake temperature very high ({vehicle.brake_temp}°C)"
        })
        risk_score += 30
    elif vehicle.brake_temp > 90:
        issues.append({
            "component": "brake_system",
            "severity": "warning",
            "message": f"Brake temperature elevated ({vehicle.brake_temp}°C)"
        })
        risk_score += 15

    # Oil pressure check
    if vehicle.oil_pressure < 25:
        issues.append({
            "component": "engine",
            "severity": "critical",
            "message": f"Oil pressure dangerously low ({vehicle.oil_pressure} psi)"
        })
        risk_score += 30
    elif vehicle.oil_pressure < 35:
        issues.append({
            "component": "engine",
            "severity": "warning",
            "message": f"Oil pressure below normal ({vehicle.oil_pressure} psi)"
        })
        risk_score += 15

    # Engine temperature check
    if vehicle.engine_temp > 105:
        issues.append({
            "component": "cooling_system",
            "severity": "critical",
            "message": f"Engine overheating ({vehicle.engine_temp}°C)"
        })
        risk_score += 25
    elif vehicle.engine_temp > 100:
        issues.append({
            "component": "cooling_system",
            "severity": "warning",
            "message": f"Engine temperature high ({vehicle.engine_temp}°C)"
        })
        risk_score += 10

    # Tire pressure check
    if vehicle.tire_pressure < 25:
        issues.append({
            "component": "tires",
            "severity": "critical",
            "message": f"Tire pressure very low ({vehicle.tire_pressure} psi)"
        })
        risk_score += 20
    elif vehicle.tire_pressure < 28:
        issues.append({
            "component": "tires",
            "severity": "warning",
            "message": f"Tire pressure low ({vehicle.tire_pressure} psi)"
        })
        risk_score += 10

    # Brake fluid check
    if vehicle.brake_fluid_level < 65:
        issues.append({
            "component": "brake_fluid",
            "severity": "critical",
            "message": f"Brake fluid critically low ({vehicle.brake_fluid_level}%)"
        })
        risk_score += 25
    elif vehicle.brake_fluid_level < 80:
        issues.append({
            "component": "brake_fluid",
            "severity": "warning",
            "message": f"Brake fluid getting low ({vehicle.brake_fluid_level}%)"
        })
        risk_score += 10

    # Mileage check
    if vehicle.mileage > 80000:
        issues.append({
            "component": "general_maintenance",
            "severity": "warning",
            "message": f"High mileage - service recommended ({vehicle.mileage} km)"
        })
        risk_score += 5

    # Generate recommendations
    recommendations = []
    if risk_score > 50:
        recommendations.append("Immediate inspection required")
        recommendations.append("Do not operate vehicle")
        failure_probability = "HIGH (>70%)"
        estimated_days = "1-3 days"
    elif risk_score > 25:
        recommendations.append("Schedule maintenance within 7 days")
        recommendations.append("Monitor vehicle closely")
        failure_probability = "MEDIUM (40-70%)"
        estimated_days = "7-14 days"
    else:
        recommendations.append("Regular maintenance schedule")
        recommendations.append("Continue normal operation")
        failure_probability = "LOW (<40%)"
        estimated_days = "30+ days"

    return {
        "vehicle_id": vehicle_id,
        "vehicle_model": vehicle.model,
        "current_status": vehicle.status,
        "risk_score": min(risk_score, 100),  # Cap at 100
        "failure_probability": failure_probability,
        "estimated_time_to_failure": estimated_days,
        "issues_detected": issues,
        "recommendations": recommendations,
        "sensor_readings": {
            "brake_temp": vehicle.brake_temp,
            "oil_pressure": vehicle.oil_pressure,
            "engine_temp": vehicle.engine_temp,
            "tire_pressure": vehicle.tire_pressure,
            "brake_fluid_level": vehicle.brake_fluid_level,
            "mileage": vehicle.mileage
        }
    }
#Sensor only Endpoints
@app.get("/vehicles/{vehicle_id}/sensors")
def get_vehicle_sensors(vehicle_id: str, db: Session = Depends(get_db)):
    """
    Get only sensor readings for a vehicle

    Args:
        vehicle_id: Vehicle ID

    Returns: Sensor data only (no timestamps, status, etc.)
    Raises: 404 if vehicle not found
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return {
        "vehicle_id": vehicle.id,
        "sensors": {
            "brake_temp": {
                "value": vehicle.brake_temp,
                "unit": "°C",
                "status": "critical" if vehicle.brake_temp > 100 else "warning" if vehicle.brake_temp > 90 else "normal"
            },
            "oil_pressure": {
                "value": vehicle.oil_pressure,
                "unit": "psi",
                "status": "critical" if vehicle.oil_pressure < 25 else "warning" if vehicle.oil_pressure < 35 else "normal"
            },
            "engine_temp": {
                "value": vehicle.engine_temp,
                "unit": "°C",
                "status": "critical" if vehicle.engine_temp > 105 else "warning" if vehicle.engine_temp > 100 else "normal"
            },
            "tire_pressure": {
                "value": vehicle.tire_pressure,
                "unit": "psi",
                "status": "critical" if vehicle.tire_pressure < 25 else "warning" if vehicle.tire_pressure < 28 else "normal"
            },
            "brake_fluid_level": {
                "value": vehicle.brake_fluid_level,
                "unit": "%",
                "status": "critical" if vehicle.brake_fluid_level < 65 else "warning" if vehicle.brake_fluid_level < 80 else "normal"
            },
            "mileage": {
                "value": vehicle.mileage,
                "unit": "km",
                "status": "warning" if vehicle.mileage > 80000 else "normal"
            }
        }
    }


from ml_predictor import MLPredictor

# Initialize ML predictor
ml_predictor = MLPredictor(repo_id="RashmiVid/vehicle-failure-predictor")


# =================================================================
# ML PREDICTION ENDPOINT
# =================================================================

@app.post("/ml-predict/{vehicle_id}")
def ml_predict_failure(vehicle_id: str, db: Session = Depends(get_db)):
    """
    ML-based failure prediction using Hugging Face model

    Uses trained XGBoost model (NOT an LLM!)
    Allowed in all hackathons!

    Args:
        vehicle_id: Vehicle ID to analyze

    Returns: ML prediction with probability
    """
    # Get vehicle
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Prepare vehicle data
    vehicle_data = {
        'brake_temp': vehicle.brake_temp,
        'oil_pressure': vehicle.oil_pressure,
        'engine_temp': vehicle.engine_temp,
        'tire_pressure': vehicle.tire_pressure,
        'brake_fluid_level': vehicle.brake_fluid_level,
        'mileage': vehicle.mileage
    }

    # Get ML prediction
    prediction = ml_predictor.predict(vehicle_data)

    # Add vehicle info
    result = {
        "vehicle_id": vehicle_id,
        "model": vehicle.model,
        "current_status": vehicle.status,
        "sensor_readings": vehicle_data,
        "ml_prediction": prediction
    }

    return result


# =================================================================
# AGENT SYSTEM ENDPOINTS
# =================================================================

@app.get("/agents/status")
def get_agents_status():
    """
    Get status of all registered agents

    Returns: List of all agents and their info
    """
    agents = master_agent.get_registered_agents()

    return {
        "master_agent": master_agent.get_info(),
        "registered_agents": agents,
        "total_agents": len(agents)
    }


@app.post("/agents/analyze/{vehicle_id}")
def analyze_vehicle_with_agents(vehicle_id: str, db: Session = Depends(get_db)):
    """
    Comprehensive vehicle analysis using multi-agent system

    Args:
        vehicle_id: Vehicle ID to analyze

    Returns: Complete analysis from all agents
    """
    # Get vehicle from database
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Prepare data for agents
    agent_data = {
        "vehicle_id": vehicle.id,
        "model": vehicle.model,
        "sensors": {
            "brake_temp": vehicle.brake_temp,
            "oil_pressure": vehicle.oil_pressure,
            "engine_temp": vehicle.engine_temp,
            "tire_pressure": vehicle.tire_pressure,
            "brake_fluid_level": vehicle.brake_fluid_level,
            "mileage": vehicle.mileage
        }
    }

    # Run multi-agent analysis
    analysis = master_agent.process(agent_data)

    return analysis


# =================================================================
# STATE MANAGEMENT & WORKFLOW ENDPOINTS
# =================================================================

@app.post("/workflow/execute/{vehicle_id}")
def execute_workflow(vehicle_id: str, db: Session = Depends(get_db)):
    """
    Execute complete analysis workflow with state tracking

    Args:
        vehicle_id: Vehicle ID to analyze

    Returns: Workflow execution results
    """
    # Get vehicle
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Create workflow
    workflow_id = state_manager.create_workflow(vehicle_id, "complete_analysis")

    # Prepare data
    agent_data = {
        "vehicle_id": vehicle.id,
        "model": vehicle.model,
        "sensors": {
            "brake_temp": vehicle.brake_temp,
            "oil_pressure": vehicle.oil_pressure,
            "engine_temp": vehicle.engine_temp,
            "tire_pressure": vehicle.tire_pressure,
            "brake_fluid_level": vehicle.brake_fluid_level,
            "mileage": vehicle.mileage
        }
    }

    try:
        # Execute analysis with workflow tracking
        results = master_agent.process(agent_data, workflow_id)

        return {
            "workflow_id": workflow_id,
            "vehicle_id": vehicle_id,
            "status": "completed",
            "results": results
        }

    except Exception as e:
        return {
            "workflow_id": workflow_id,
            "vehicle_id": vehicle_id,
            "status": "failed",
            "error": str(e)
        }


@app.get("/workflow/status/{workflow_id}")
def get_workflow_status(workflow_id: str):
    """
    Get status of a specific workflow

    Args:
        workflow_id: Workflow ID

    Returns: Workflow details
    """
    workflow = state_manager.get_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return workflow


@app.get("/workflow/history/{vehicle_id}")
def get_vehicle_workflow_history(vehicle_id: str, limit: int = 10):
    """
    Get workflow history for a vehicle

    Args:
        vehicle_id: Vehicle ID
        limit: Maximum number of workflows to return

    Returns: List of workflows
    """
    history = state_manager.get_vehicle_history(vehicle_id, limit)

    return {
        "vehicle_id": vehicle_id,
        "total_workflows": len(history),
        "workflows": history
    }


@app.get("/state")
def get_system_state():
    """
    Get current system state

    Returns: Complete system state and statistics
    """
    return {
        "statistics": state_manager.get_statistics(),
        "vehicle_states": state_manager.get_all_vehicle_states()
    }


@app.get("/state/vehicle/{vehicle_id}")
def get_vehicle_state_endpoint(vehicle_id: str):
    """
    Get current state of a specific vehicle

    Args:
        vehicle_id: Vehicle ID

    Returns: Vehicle state
    """
    state = state_manager.get_vehicle_state(vehicle_id)

    if not state:
        raise HTTPException(
            status_code=404,
            detail="Vehicle state not found. Vehicle not yet analyzed."
        )

    return state


@app.delete("/state/vehicle/{vehicle_id}")
def clear_vehicle_history(vehicle_id: str):
    """
    Clear workflow history for a vehicle

    Args:
        vehicle_id: Vehicle ID

    Returns: Success message
    """
    state_manager.clear_history(vehicle_id)

    return {
        "message": f"Cleared history for {vehicle_id}",
        "vehicle_id": vehicle_id
    }
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows Person 3's frontend to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom validation error handler"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "The request data is invalid",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all error handler"""
    import traceback

    # Print full traceback for debugging
    print("\n" + "=" * 60)
    print("ERROR OCCURRED:")
    print(traceback.format_exc())
    print("=" * 60 + "\n")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "detail": str(exc)  # Show actual error in dev mode
        }
    )
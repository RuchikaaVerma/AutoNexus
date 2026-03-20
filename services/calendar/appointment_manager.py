"""
PURPOSE: Persistent appointment storage using SQLite via SQLAlchemy.
CONNECTS TO: FILE 9 (scheduling_agent), FILE 13 (reminder_scheduler)
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from services.agents.config.hf_model_config import DATABASE_URL

logger = logging.getLogger(__name__)
Base   = declarative_base()


class Appointment(Base):
    __tablename__ = "appointments"
    id             = Column(Integer, primary_key=True, autoincrement=True)
    appointment_id = Column(String(50), unique=True, nullable=False)
    vehicle_id     = Column(String(20), nullable=False)
    customer_name  = Column(String(100), nullable=False)
    customer_phone = Column(String(20), default="")
    customer_email = Column(String(100), default="")
    component      = Column(String(50), nullable=False)
    date           = Column(String(20), nullable=False)
    time_slot      = Column(String(10), nullable=False)
    service_center = Column(String(100), default="AutoNexus Central")
    status         = Column(String(20), default="confirmed")
    notes          = Column(Text, default="")
    created_at     = Column(DateTime, default=datetime.now)
    reminder_24h   = Column(String(10), default="pending")
    reminder_1h    = Column(String(10), default="pending")


class AppointmentManager:
    """Manages appointment CRUD with SQLite persistence."""

    def __init__(self):
        self.engine  = create_engine(DATABASE_URL, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self._counter = 1
        logger.info(f"AppointmentManager ready | db={DATABASE_URL}")

    def create_appointment(
        self,
        vehicle_id: str,
        customer_name: str,
        component: str,
        date: str = None,
        time_slot: str = "10:00",
        customer_phone: str = "",
        customer_email: str = "",
    ) -> dict:
        appt_id     = f"APPT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self._counter}"
        self._counter += 1
        target_date = date or (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        with self.Session() as session:
            appt = Appointment(
                appointment_id = appt_id,
                vehicle_id     = vehicle_id,
                customer_name  = customer_name,
                customer_phone = customer_phone,
                customer_email = customer_email,
                component      = component,
                date           = target_date,
                time_slot      = time_slot,
            )
            session.add(appt)
            session.commit()
            logger.info(f"Appointment created | id={appt_id}")
            return {"success": True, "appointment_id": appt_id, "date": target_date, "time_slot": time_slot}

    def get_appointment(self, appointment_id: str) -> dict:
        with self.Session() as session:
            a = session.query(Appointment).filter_by(appointment_id=appointment_id).first()
            if not a:
                return {}
            return {c.name: getattr(a, c.name) for c in Appointment.__table__.columns}

    def get_upcoming_appointments(self, hours_ahead: int = 48) -> list:
        """Get appointments due within hours_ahead hours."""
        with self.Session() as session:
            appts = session.query(Appointment).filter_by(status="confirmed").all()
            now   = datetime.now()
            due   = []
            for a in appts:
                try:
                    appt_dt = datetime.strptime(f"{a.date} {a.time_slot}", "%Y-%m-%d %H:%M")
                    diff_h  = (appt_dt - now).total_seconds() / 3600
                    if 0 < diff_h <= hours_ahead:
                        due.append({c.name: getattr(a, c.name) for c in Appointment.__table__.columns})
                except Exception:
                    pass
            return due

    def update_reminder_status(self, appointment_id: str, reminder_type: str, status: str):
        with self.Session() as session:
            a = session.query(Appointment).filter_by(appointment_id=appointment_id).first()
            if a:
                if reminder_type == "24h": a.reminder_24h = status
                if reminder_type == "1h":  a.reminder_1h  = status
                session.commit()

    def cancel_appointment(self, appointment_id: str) -> dict:
        with self.Session() as session:
            a = session.query(Appointment).filter_by(appointment_id=appointment_id).first()
            if not a:
                return {"success": False, "error": "Not found"}
            a.status = "cancelled"
            session.commit()
            return {"success": True}


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 12: Appointment Manager — Self Test")
    print("="*55)
    mgr = AppointmentManager()
    r   = mgr.create_appointment("VEH001", "Rahul Sharma", "brakes",
                                  customer_phone="+919876543210",
                                  customer_email="rahul@example.com")
    print(f"  Create  : {'✅' if r['success'] else '❌'} | {r.get('appointment_id')}")
    fetched = mgr.get_appointment(r["appointment_id"])
    print(f"  Fetch   : {'✅' if fetched else '❌'}")
    cancel  = mgr.cancel_appointment(r["appointment_id"])
    print(f"  Cancel  : {'✅' if cancel['success'] else '❌'}")
    print("  FILE 12 complete!\n")

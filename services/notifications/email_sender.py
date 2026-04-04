"""
FILE 6: services/notifications/email_sender.py
PURPOSE: Sends HTML emails via Gmail SMTP (SendGrid removed).
AUTHOR: Person 4 (fixed by Person 1)

SETUP:
  1. Go to Google Account → Security → 2-Step Verification → App Passwords
  2. Create app password for "Mail"
  3. Add to .env:
       GMAIL_SENDER_EMAIL=yourname@gmail.com
       GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
"""

import smtplib
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from services.agents.config.hf_model_config import (
    GMAIL_SENDER_EMAIL,
    GMAIL_APP_PASSWORD,
)

logger = logging.getLogger(__name__)


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    plain_body: str = "",
) -> dict:
    """Send HTML email via Gmail SMTP."""
    if not to_email or not subject:
        return {"success": False, "error": "Missing to_email or subject"}

    # DEMO MODE — no credentials configured
    if not GMAIL_SENDER_EMAIL or not GMAIL_APP_PASSWORD:
        logger.warning(f"[DEMO] Email to {to_email} | Subject: {subject}")
        print(f"\n  📧 [DEMO EMAIL] To: {to_email} | Subject: {subject}")
        return {"success": True, "demo": True}

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"AutoNexus Alerts <{GMAIL_SENDER_EMAIL}>"
        msg["To"]      = to_email

        msg.attach(MIMEText(plain_body or "See HTML version.", "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_SENDER_EMAIL, to_email, msg.as_string())

        logger.info(f"Email sent | to={to_email} | subject={subject}")
        return {"success": True, "demo": False}

    except smtplib.SMTPAuthenticationError:
        logger.error("Gmail auth failed — check GMAIL_APP_PASSWORD in .env")
        return {"success": False, "error": "Gmail authentication failed"}

    except Exception as e:
        logger.error(f"Email failed to {to_email}: {e}")
        return {"success": False, "error": str(e)}


def send_service_reminder(
    to_email: str,
    customer_name: str,
    vehicle_id: str,
    component: str,
    days: int,
) -> dict:
    """Send vehicle service reminder email — called by EngagementAgent."""
    subject = f"🚨 URGENT: {vehicle_id} Requires Immediate Attention"
    html = f"""
    <html><body style='font-family:Arial;max-width:600px;margin:auto'>
      <div style='background:#1a1a2e;padding:20px;border-radius:8px 8px 0 0'>
        <h1 style='color:#e94560;margin:0'>🔧 AutoNexus</h1>
        <p style='color:#aaa;margin:5px 0'>Predictive Maintenance System</p>
      </div>
      <div style='padding:30px;border:1px solid #ddd;border-top:none'>
        <h2 style='color:#333'>Hello {customer_name},</h2>
        <p style='font-size:16px'>Our AI system has detected that your vehicle
           <strong>{vehicle_id}</strong> requires <strong>{component}</strong>
           attention within <strong style='color:#e94560'>{days} days</strong>.</p>
        <div style='background:#fff3cd;padding:15px;border-radius:5px;margin:20px 0;
                    border-left:5px solid #ff8f00'>
          <strong>⚠️ Issues Detected:</strong> {component}<br>
          <strong>📅 Action Required Within:</strong> {days} days<br>
          <strong>🚫 Do NOT drive</strong> this vehicle until serviced.
        </div>
        <p style='color:#666;margin-top:20px'>
          Our agent will call you during business hours (9 AM – 8 PM)
          to schedule a service appointment.<br><br>
          AutoNexus Team | 1800-AUTO-NEX
        </p>
      </div>
    </body></html>
    """
    plain = (
        f"URGENT: {customer_name}, your vehicle {vehicle_id} has critical issues: "
        f"{component}. Action required within {days} days. Do not drive."
    )
    return send_email(to_email, subject, html, plain)


def send_appointment_confirmation_email(
    to_email: str,
    customer_name: str,
    vehicle_id: str,
    date: str,
    time_slot: str,
    service_center: str,
    component: str,
) -> dict:
    """Send appointment booking confirmation email."""
    subject = f"✅ Service Confirmed — {vehicle_id} on {date}"
    html = f"""
    <html><body style='font-family:Arial;max-width:600px;margin:auto'>
      <div style='background:#1a1a2e;padding:20px;border-radius:8px 8px 0 0'>
        <h1 style='color:#4caf50;margin:0'>✅ AutoNexus</h1>
      </div>
      <div style='padding:30px;border:1px solid #ddd;border-top:none'>
        <h2>Appointment Confirmed!</h2>
        <p>Hello {customer_name}, your service is booked.</p>
        <table style='width:100%;border-collapse:collapse'>
          <tr style='background:#f5f5f5'>
            <td style='padding:10px;border:1px solid #ddd'><strong>Vehicle</strong></td>
            <td style='padding:10px;border:1px solid #ddd'>{vehicle_id}</td>
          </tr>
          <tr>
            <td style='padding:10px;border:1px solid #ddd'><strong>Service</strong></td>
            <td style='padding:10px;border:1px solid #ddd'>{component}</td>
          </tr>
          <tr style='background:#f5f5f5'>
            <td style='padding:10px;border:1px solid #ddd'><strong>Date</strong></td>
            <td style='padding:10px;border:1px solid #ddd'>{date}</td>
          </tr>
          <tr>
            <td style='padding:10px;border:1px solid #ddd'><strong>Time</strong></td>
            <td style='padding:10px;border:1px solid #ddd'>{time_slot}</td>
          </tr>
          <tr style='background:#f5f5f5'>
            <td style='padding:10px;border:1px solid #ddd'><strong>Location</strong></td>
            <td style='padding:10px;border:1px solid #ddd'>{service_center}</td>
          </tr>
        </table>
        <p style='color:#666;margin-top:20px'>See you soon! — AutoNexus Team</p>
      </div>
    </body></html>
    """
    plain = (
        f"Confirmed: {customer_name}, your {component} service for {vehicle_id} "
        f"is on {date} at {time_slot} at {service_center}."
    )
    return send_email(to_email, subject, html, plain)


def send_report_email(
    to_email: str,
    customer_name: str,
    report_type: str,
    pdf_path: str = None,
) -> dict:
    subject = f"AutoNexus {report_type} Report — {datetime.now().strftime('%b %d %Y')}"
    html = f"""
    <html><body style='font-family:Arial;max-width:600px;margin:auto;padding:30px'>
      <h2>Hello {customer_name},</h2>
      <p>Your <strong>{report_type}</strong> report is ready from AutoNexus.</p>
      <p style='color:#666'>AutoNexus Team</p>
    </body></html>
    """
    return send_email(to_email, subject, html)


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  email_sender.py — Self Test (Gmail SMTP)")
    print("="*55)
    r = send_service_reminder(
        to_email      = "test@example.com",
        customer_name = "Rahul Sharma",
        vehicle_id    = "VEH001",
        component     = "brakes",
        days          = 7,
    )
    print(f"  Result: {'✅ SUCCESS' if r['success'] else '❌ FAILED'} | {r}")
    print("="*55)
<<<<<<< HEAD
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
=======
import logging
from datetime import datetime
from services.agents.config.hf_model_config import (
    SENDGRID_API_KEY, SENDGRID_FROM_EMAIL, TEMPLATES_DIR
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
)

logger = logging.getLogger(__name__)


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    plain_body: str = "",
) -> dict:
<<<<<<< HEAD
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

=======
    """
    Send an HTML email via SendGrid.
    Falls back to demo mode if no API key configured.
    """
    if not to_email or not subject:
        return {"success": False, "error": "Missing to_email or subject"}

    # DEMO MODE
    if not SENDGRID_API_KEY:
        logger.warning(f"[DEMO] Email to {to_email} | Subject: {subject}")
        print(f"\n  📧 [DEMO EMAIL]\n  To     : {to_email}")
        print(f"  Subject: {subject}")
        print(f"  Body   : {plain_body[:100] if plain_body else html_body[:100]}...")
        return {"success": True, "demo": True}

    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Content

        message = Mail(
            from_email    = SENDGRID_FROM_EMAIL,
            to_emails     = to_email,
            subject       = subject,
            html_content  = html_body,
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"Email sent | to={to_email} | status={response.status_code}")
        return {"success": True, "status_code": response.status_code, "demo": False}

    except ImportError:
        logger.error("sendgrid not installed: pip install sendgrid")
        return {"success": False, "error": "sendgrid not installed"}
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
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
<<<<<<< HEAD
    """Send vehicle service reminder email — called by EngagementAgent."""
    subject = f"🚨 URGENT: {vehicle_id} Requires Immediate Attention"
=======
    """Send vehicle service reminder email."""
    subject = f"AutoNexus Alert: {vehicle_id} Requires Attention"
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
    html = f"""
    <html><body style='font-family:Arial;max-width:600px;margin:auto'>
      <div style='background:#1a1a2e;padding:20px;border-radius:8px 8px 0 0'>
        <h1 style='color:#e94560;margin:0'>🔧 AutoNexus</h1>
        <p style='color:#aaa;margin:5px 0'>Predictive Maintenance System</p>
      </div>
      <div style='padding:30px;border:1px solid #ddd;border-top:none'>
<<<<<<< HEAD
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
=======
        <h2>Hello {customer_name},</h2>
        <p>Our AI system has detected that your vehicle <strong>{vehicle_id}</strong>
           requires <strong>{component}</strong> attention within
           <strong style='color:#e94560'>{days} days</strong>.</p>
        <div style='background:#fff3cd;padding:15px;border-radius:5px;margin:20px 0'>
          <strong>⚠️ Component at Risk:</strong> {component.title()}<br>
          <strong>📅 Action Required Within:</strong> {days} days
        </div>
        <a href='http://localhost:3000/book'
           style='background:#e94560;color:white;padding:12px 25px;
                  text-decoration:none;border-radius:5px;display:inline-block'>
          Book Service Now
        </a>
        <p style='color:#666;margin-top:30px'>
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
          AutoNexus Team | 1800-AUTO-NEX
        </p>
      </div>
    </body></html>
    """
    plain = (
<<<<<<< HEAD
        f"URGENT: {customer_name}, your vehicle {vehicle_id} has critical issues: "
        f"{component}. Action required within {days} days. Do not drive."
=======
        f"Hello {customer_name}, your vehicle {vehicle_id} "
        f"{component} needs attention within {days} days. "
        f"Book at: http://localhost:3000/book"
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
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
<<<<<<< HEAD
    subject = f"✅ Service Confirmed — {vehicle_id} on {date}"
=======
    subject = f"Appointment Confirmed — {date} at {time_slot}"
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
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
<<<<<<< HEAD
            <td style='padding:10px;border:1px solid #ddd'>{component}</td>
=======
            <td style='padding:10px;border:1px solid #ddd'>{component.title()}</td>
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
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
<<<<<<< HEAD
        f"Confirmed: {customer_name}, your {component} service for {vehicle_id} "
=======
        f"Confirmed! {customer_name}, your {component} service for {vehicle_id} "
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
        f"is on {date} at {time_slot} at {service_center}."
    )
    return send_email(to_email, subject, html, plain)


def send_report_email(
    to_email: str,
    customer_name: str,
    report_type: str,
    pdf_path: str = None,
) -> dict:
<<<<<<< HEAD
=======
    """Send generated PDF report via email."""
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
    subject = f"AutoNexus {report_type} Report — {datetime.now().strftime('%b %d %Y')}"
    html = f"""
    <html><body style='font-family:Arial;max-width:600px;margin:auto;padding:30px'>
      <h2>Hello {customer_name},</h2>
<<<<<<< HEAD
      <p>Your <strong>{report_type}</strong> report is ready from AutoNexus.</p>
=======
      <p>Your <strong>{report_type}</strong> report is ready.</p>
      <p>Please find the attached PDF report generated by AutoNexus
         predictive maintenance system.</p>
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
      <p style='color:#666'>AutoNexus Team</p>
    </body></html>
    """
    return send_email(to_email, subject, html)


if __name__ == "__main__":
    print("\n" + "="*55)
<<<<<<< HEAD
    print("  email_sender.py — Self Test (Gmail SMTP)")
    print("="*55)
    r = send_service_reminder(
=======
    print("  FILE 6: Email Sender — Self Test")
    print("="*55)

    print("\n[1] Testing service reminder email...")
    r1 = send_service_reminder(
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
        to_email      = "test@example.com",
        customer_name = "Rahul Sharma",
        vehicle_id    = "VEH001",
        component     = "brakes",
        days          = 7,
    )
<<<<<<< HEAD
    print(f"  Result: {'✅ SUCCESS' if r['success'] else '❌ FAILED'} | {r}")
    print("="*55)
=======
    print(f"    Result: {'✅ SUCCESS' if r1['success'] else '❌ FAILED'}")

    print("\n[2] Testing appointment confirmation email...")
    r2 = send_appointment_confirmation_email(
        to_email       = "2k23.psitaiml2314065@gmail.com",
        customer_name  = "Rahul Sharma",
        vehicle_id     = "VEH001",
        date           = "Monday March 10",
        time_slot      = "10:00 AM",
        service_center = "AutoNexus Central",
        component      = "brakes",
    )
    print(f"    Result: {'✅ SUCCESS' if r2['success'] else '❌ FAILED'}")

    print("\n" + "="*55)
    print("  FILE 6 complete! Commit if all ✅")
    print("="*55 + "\n")
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73

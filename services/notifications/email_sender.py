import logging
from datetime import datetime
from services.agents.config.hf_model_config import (
    SENDGRID_API_KEY, SENDGRID_FROM_EMAIL, TEMPLATES_DIR
)

logger = logging.getLogger(__name__)


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    plain_body: str = "",
) -> dict:
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
    """Send vehicle service reminder email."""
    subject = f"AutoNexus Alert: {vehicle_id} Requires Attention"
    html = f"""
    <html><body style='font-family:Arial;max-width:600px;margin:auto'>
      <div style='background:#1a1a2e;padding:20px;border-radius:8px 8px 0 0'>
        <h1 style='color:#e94560;margin:0'>🔧 AutoNexus</h1>
        <p style='color:#aaa;margin:5px 0'>Predictive Maintenance System</p>
      </div>
      <div style='padding:30px;border:1px solid #ddd;border-top:none'>
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
          AutoNexus Team | 1800-AUTO-NEX
        </p>
      </div>
    </body></html>
    """
    plain = (
        f"Hello {customer_name}, your vehicle {vehicle_id} "
        f"{component} needs attention within {days} days. "
        f"Book at: http://localhost:3000/book"
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
    subject = f"Appointment Confirmed — {date} at {time_slot}"
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
            <td style='padding:10px;border:1px solid #ddd'>{component.title()}</td>
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
        f"Confirmed! {customer_name}, your {component} service for {vehicle_id} "
        f"is on {date} at {time_slot} at {service_center}."
    )
    return send_email(to_email, subject, html, plain)


def send_report_email(
    to_email: str,
    customer_name: str,
    report_type: str,
    pdf_path: str = None,
) -> dict:
    """Send generated PDF report via email."""
    subject = f"AutoNexus {report_type} Report — {datetime.now().strftime('%b %d %Y')}"
    html = f"""
    <html><body style='font-family:Arial;max-width:600px;margin:auto;padding:30px'>
      <h2>Hello {customer_name},</h2>
      <p>Your <strong>{report_type}</strong> report is ready.</p>
      <p>Please find the attached PDF report generated by AutoNexus
         predictive maintenance system.</p>
      <p style='color:#666'>AutoNexus Team</p>
    </body></html>
    """
    return send_email(to_email, subject, html)


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 6: Email Sender — Self Test")
    print("="*55)

    print("\n[1] Testing service reminder email...")
    r1 = send_service_reminder(
        to_email      = "test@example.com",
        customer_name = "Rahul Sharma",
        vehicle_id    = "VEH001",
        component     = "brakes",
        days          = 7,
    )
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
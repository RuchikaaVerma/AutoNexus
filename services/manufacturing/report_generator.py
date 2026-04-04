"""
PURPOSE: Generates professional PDF reports using ReportLab.
CONNECTS TO: FILES 18,19 (rca+capa), FILE 6 (email — sends report), P3 dashboard
"""
import logging
from pathlib import Path
from datetime import datetime
logger = logging.getLogger(__name__)
REPORTS_DIR = Path("services/manufacturing/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_vehicle_report(vehicle_id: str, rca: dict, capa: dict) -> str:
    """Generate PDF report for a single vehicle. Returns file path."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import inch

        filename = REPORTS_DIR / f"report_{vehicle_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        doc      = SimpleDocTemplate(str(filename), pagesize=A4)
        styles   = getSampleStyleSheet()
        story    = []

        # Title
        story.append(Paragraph("AutoNexus — Vehicle Health Report", styles["Title"]))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}", styles["Normal"]))
        story.append(Spacer(1, 20))

        # Vehicle Info
        story.append(Paragraph("Vehicle Information", styles["Heading2"]))
        info_data = [
            ["Vehicle ID",  vehicle_id],
            ["Component",   rca.get("component", "N/A")],
            ["Severity",    rca.get("severity", "N/A")],
            ["Analyzed At", rca.get("analyzed_at", "N/A")[:19]],
        ]
        t = Table(info_data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,-1), colors.lightgrey),
            ("GRID",       (0,0), (-1,-1), 0.5, colors.grey),
            ("FONTNAME",   (0,0), (-1,-1), "Helvetica"),
            ("FONTSIZE",   (0,0), (-1,-1), 10),
            ("PADDING",    (0,0), (-1,-1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

        # RCA
        story.append(Paragraph("Root Cause Analysis", styles["Heading2"]))
        story.append(Paragraph(f"Primary Cause: <b>{rca.get('primary_cause','N/A')}</b>", styles["Normal"]))
        story.append(Paragraph(f"Confidence: {rca.get('confidence','N/A')}%", styles["Normal"]))
        story.append(Spacer(1, 10))

        # CAPA
        story.append(Paragraph("Corrective & Preventive Actions", styles["Heading2"]))
        story.append(Paragraph(f"Priority: <b>{capa.get('priority','N/A')}</b>  |  Deadline: {capa.get('deadline','N/A')}", styles["Normal"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph("Corrective Actions:", styles["Heading3"]))
        for act in capa.get("corrective_actions", []):
            story.append(Paragraph(f"• {act}", styles["Normal"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph("Preventive Actions:", styles["Heading3"]))
        for act in capa.get("preventive_actions", []):
            story.append(Paragraph(f"• {act}", styles["Normal"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"Estimated Cost: {capa.get('estimated_cost','N/A')}", styles["Normal"]))
        story.append(Paragraph(f"Estimated Time: {capa.get('estimated_time','N/A')}", styles["Normal"]))

        doc.build(story)
        logger.info(f"PDF report generated: {filename}")
        return str(filename)

    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        return ""


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 20: Report Generator — Self Test")
    print("="*55)
    from services.manufacturing.rca_engine import RCAEngine
    from services.manufacturing.capa_generator import CAPAGenerator
    rca  = RCAEngine().analyze("VEH001", "brakes", {"brake_temp": 95, "brake_fluid": 25})
    capa = CAPAGenerator().generate(rca)
    path = generate_vehicle_report("VEH001", rca, capa)
    print(f"\n  PDF generated : {'✅' if path else '❌'}")
    print(f"  Path          : {path}")
    print("  FILE 20 complete!\n")
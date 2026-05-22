"""
FuelGuard AI - Report Generator
Generates PDF reports from transaction data.

On Vercel (read-only filesystem) reports are written to /tmp.
Locally they are written to the project-level reports/ directory.
"""

import os
import tempfile
from datetime import datetime

# Try to import reportlab; fall back gracefully if unavailable
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Vercel's filesystem is read-only except /tmp.
# Detect Vercel via its environment variable and use /tmp accordingly.
if os.environ.get("VERCEL"):
    REPORTS_DIR = os.path.join(tempfile.gettempdir(), "reports")
else:
    REPORTS_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports"
    )


def ensure_reports_dir():
    """Create the reports/ directory if it doesn't exist."""
    os.makedirs(REPORTS_DIR, exist_ok=True)


def generate_pdf_report(transactions: list[dict], analytics: dict) -> str | None:
    """
    Generate a professional PDF report and return the file path.
    Returns None if reportlab is not installed.
    """
    if not REPORTLAB_AVAILABLE:
        return None

    ensure_reports_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"FuelGuard_Report_{timestamp}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # --- Custom styles ---
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=22,
        spaceAfter=6,
        textColor=colors.HexColor("#111111"),
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#666666"),
        spaceAfter=20,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1a1a1a"),
        spaceBefore=16,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        spaceAfter=4,
    )

    # --- Title ---
    elements.append(Paragraph("FuelGuard AI — Fraud Detection Report", title_style))
    elements.append(
        Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            subtitle_style,
        )
    )
    elements.append(Spacer(1, 6 * mm))

    # --- Analytics Summary ---
    elements.append(Paragraph("Analytics Summary", heading_style))
    analytics_data = [
        ["Metric", "Value"],
        ["Total Transactions", str(analytics.get("total_transactions", 0))],
        ["Fraud Transactions", str(analytics.get("fraud_transactions", 0))],
        ["Safe Transactions", str(analytics.get("safe_transactions", 0))],
        ["Fraud Percentage", f"{analytics.get('fraud_percentage', 0)}%"],
        ["Average Shortage", f"{analytics.get('average_shortage', 0)}%"],
        ["Highest Shortage", f"{analytics.get('highest_shortage', 0)}%"],
    ]
    analytics_table = Table(analytics_data, colWidths=[200, 200])
    analytics_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a1a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elements.append(analytics_table)
    elements.append(Spacer(1, 8 * mm))

    # --- Transaction Details ---
    elements.append(Paragraph("Transaction Details", heading_style))
    if transactions:
        header = [
            "ID",
            "Requested (L)",
            "Delivered (L)",
            "Diff (L)",
            "Shortage %",
            "Fraud",
            "Risk",
            "Score",
        ]
        rows = [header]
        for t in transactions[:50]:  # limit rows for readability
            rows.append(
                [
                    str(t.get("transaction_id", "")),
                    str(t.get("requested_fuel", "")),
                    str(t.get("delivered_fuel", "")),
                    str(t.get("difference", "")),
                    f"{t.get('shortage_percentage', '')}%",
                    "Yes" if t.get("fraud_detected") else "No",
                    t.get("risk_level", ""),
                    str(t.get("risk_score", "")),
                ]
            )
        tx_table = Table(rows, colWidths=[35, 65, 65, 50, 60, 40, 50, 40])
        tx_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a1a")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        elements.append(tx_table)
    else:
        elements.append(Paragraph("No transactions recorded.", body_style))

    elements.append(Spacer(1, 10 * mm))

    # --- Footer ---
    elements.append(
        Paragraph(
            "This report was auto-generated by FuelGuard AI. "
            "Data is based on simulated fuel delivery transactions.",
            ParagraphStyle(
                "Footer",
                parent=styles["Normal"],
                fontSize=8,
                textColor=colors.HexColor("#999999"),
            ),
        )
    )

    doc.build(elements)
    return filepath

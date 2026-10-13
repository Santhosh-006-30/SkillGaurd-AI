"""
Audit Dossier and Report Generator Service — Phase 16
Generates downloadable PDF compliance dossiers and JSON audit packages.
All data clearly marked: [SIMULATED DEMO DATA — SIH 26245]
"""
import io
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from sqlalchemy.orm import Session

from app.database.models import TrainingCentre, ComplianceScore, AttendanceRecord, InventoryItem, Alert

def generate_centre_dossier_data(db: Session, centre_id: int) -> Optional[Dict[str, Any]]:
    """Assemble complete compliance dossier data dictionary for a training centre."""
    centre = db.query(TrainingCentre).filter(TrainingCentre.id == centre_id).first()
    if not centre:
        return None

    score = db.query(ComplianceScore).filter(ComplianceScore.centre_id == centre_id).order_by(ComplianceScore.timestamp.desc()).first()
    attendance = db.query(AttendanceRecord).filter(AttendanceRecord.centre_id == centre_id).order_by(AttendanceRecord.date.desc()).first()
    inventory = db.query(InventoryItem).filter(InventoryItem.centre_id == centre_id).all()
    alerts = db.query(Alert).filter(Alert.centre_id == centre_id).order_by(Alert.created_at.desc()).limit(10).all()

    inv_list = [
        {
            "asset_type": item.item_type.value if hasattr(item.item_type, "value") else str(item.item_type),
            "item_name": item.item_name,
            "sanctioned_count": item.sanctioned_quantity,
            "minimum_required": item.minimum_required,
            "zone": item.zone,
            "status": "COMPLIANT" if item.sanctioned_quantity >= item.minimum_required else "DEFICIT"
        }
        for item in inventory
    ]

    alert_list = [
        {
            "id": a.id,
            "alert_type": a.alert_type.value if hasattr(a.alert_type, "value") else str(a.alert_type),
            "severity": a.severity.value if hasattr(a.severity, "value") else str(a.severity),
            "description": a.description,
            "status": a.status.value if hasattr(a.status, "value") else str(a.status),
            "created_at": a.created_at.isoformat() if a.created_at else None
        }
        for a in alerts
    ]

    timestamp_str = datetime.now(timezone.utc).isoformat()
    raw_payload = f"{centre.centre_code}:{centre.name}:{timestamp_str}:{score.overall_score if score else 0.0}"
    dossier_hash = hashlib.sha256(raw_payload.encode()).hexdigest()

    reg_count = attendance.registered_count if attendance else 48
    pres_count = attendance.submitted_present if attendance else 42
    discrepancy = abs(reg_count - pres_count)

    return {
        "dossier_id": f"AUDIT-{centre.centre_code}-{datetime.now().strftime('%Y%m%d')}",
        "generated_at": timestamp_str,
        "integrity_hash_sha256": dossier_hash,
        "disclaimer": "SIMULATED DEMO DATA — For Demonstration & Evaluation Purposes Only",
        "centre": {
            "id": centre.id,
            "name": centre.name,
            "code": centre.centre_code,
            "address": centre.address,
            "state": centre.state,
            "district": centre.district,
            "active_status": centre.status.value if hasattr(centre.status, "value") else str(centre.status)
        },
        "compliance": {
            "composite_score": score.overall_score if score else 85.0,
            "attendance_score": score.attendance_score if score else 88.0,
            "infrastructure_score": score.infrastructure_score if score else 82.0,
            "activity_score": score.activity_score if score else 90.0,
            "consistency_score": score.data_consistency_score if score else 85.0,
            "risk_level": score.risk_level.value if (score and hasattr(score.risk_level, "value")) else "MEDIUM"
        },
        "attendance": {
            "date": attendance.date if attendance else "2026-10-08",
            "session": attendance.session if attendance else "Morning",
            "submitted_count": reg_count,
            "estimated_presence": pres_count,
            "discrepancy": discrepancy,
            "discrepancy_pct": round((discrepancy / max(1, reg_count)) * 100, 1),
            "flagged": (discrepancy / max(1, reg_count)) > 0.15
        },
        "inventory": inv_list,
        "recent_alerts": alert_list
    }

def generate_pdf_report(dossier_data: Dict[str, Any]) -> bytes:
    """Generate professional PDF compliance dossier using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=12
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # Title Banner
    story.append(Paragraph("SKILLGUARD AI — COMPLIANCE AUDIT DOSSIER", title_style))
    story.append(Paragraph(
        f"Generated: {dossier_data['generated_at'][:19]} UTC &nbsp;|&nbsp; "
        f"Dossier ID: <b>{dossier_data['dossier_id']}</b> &nbsp;|&nbsp; "
        f"<font color='#B45309'>[SIMULATED DEMO]</font>",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#CBD5E1'), spaceAfter=10))

    # Centre Metadata Table
    c = dossier_data['centre']
    comp = dossier_data['compliance']
    meta_data = [
        [
            Paragraph(f"<b>Centre Name:</b> {c['name']}", body_style),
            Paragraph(f"<b>Centre Code:</b> {c['code']}", body_style)
        ],
        [
            Paragraph(f"<b>Location:</b> {c['district']}, {c['state']}", body_style),
            Paragraph(f"<b>Composite Score:</b> <b>{comp['composite_score']}%</b> ({comp['risk_level']} RISK)", body_style)
        ],
        [
            Paragraph(f"<b>Integrity Hash (SHA256):</b> <font size=7>{dossier_data['integrity_hash_sha256'][:32]}...</font>", body_style),
            Paragraph(f"<b>Privacy Compliance:</b> DPDP Act / Zero Biometrics", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[270, 260])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # Attendance Reconciliation Section
    story.append(Paragraph("1. Attendance Reconciliation Analysis", section_heading))
    att = dossier_data['attendance']
    att_rows = [
        ["Date / Session", "Submitted Headcount", "AI-Estimated Presence", "Discrepancy", "Status"],
        [
            f"{att['date']} ({att['session']})",
            f"{att['submitted_count']} trainees",
            f"{att['estimated_presence']} trainees",
            f"{att['discrepancy']} ({att['discrepancy_pct']}%)",
            "FLAGGED" if att['flagged'] else "VERIFIED"
        ]
    ]
    att_table = Table(att_rows, colWidths=[120, 105, 115, 110, 80])
    att_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(att_table)
    story.append(Spacer(1, 12))

    # Infrastructure Inventory Section
    story.append(Paragraph("2. Sanctioned Infrastructure Inventory Compliance", section_heading))
    inv_data = [["Asset Type", "Item Name", "Sanctioned Qty", "Required Qty", "Audit Status"]]
    for item in dossier_data['inventory']:
        inv_data.append([
            item['asset_type'],
            item['item_name'],
            str(item['sanctioned_count']),
            str(item['minimum_required']),
            item['status']
        ])
    if len(inv_data) == 1:
        inv_data.append(["No records", "-", "-", "-", "-"])

    inv_table = Table(inv_data, colWidths=[110, 150, 90, 90, 90])
    inv_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(inv_table)
    story.append(Spacer(1, 12))

    # Alerts & Recommended Actions Section
    story.append(Paragraph("3. Non-Compliance Alerts & Remediation Actions", section_heading))
    alerts_data = [["Alert Type", "Severity", "Description", "Status"]]
    for a in dossier_data['recent_alerts'][:5]:
        alerts_data.append([
            a['alert_type'],
            a['severity'],
            Paragraph(a['description'], body_style),
            a['status']
        ])
    if len(alerts_data) == 1:
        alerts_data.append(["None", "NORMAL", Paragraph("Zero open alerts detected for this centre.", body_style), "CLEARED"])

    alert_table = Table(alerts_data, colWidths=[110, 70, 270, 80])
    alert_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(alert_table)
    story.append(Spacer(1, 14))

    # Official Disclaimer
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceAfter=6))
    story.append(Paragraph(
        "<b>CONFIDENTIAL & PRIVILEGED AUDIT RECORD</b> — SkillGuard AI Architecture strictly complies with India's "
        "Digital Personal Data Protection (DPDP) Act 2023. No raw biometric identities or personal facial representations "
        "are stored or exported. Simulated demonstration dataset for SIH 26245.",
        ParagraphStyle('FooterDisclaimer', parent=styles['Normal'], fontSize=7, leading=10, textColor=colors.HexColor('#94A3B8'))
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

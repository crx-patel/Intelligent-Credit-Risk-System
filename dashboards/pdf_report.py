import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# ── Color Palette ──────────────────────────────────────────────────────────────
DARK_BG      = colors.HexColor("#0f172a")
CARD_BG      = colors.HexColor("#1e293b")
BORDER       = colors.HexColor("#334155")
TEXT_PRIMARY = colors.HexColor("#e2e8f0")
TEXT_MUTED   = colors.HexColor("#94a3b8")
GREEN        = colors.HexColor("#22c55e")
ORANGE       = colors.HexColor("#f59e0b")
RED          = colors.HexColor("#ef4444")
BLUE         = colors.HexColor("#3b82f6")
WHITE        = colors.white


def get_risk_color(risk_label: str):
    return {
        "Low Risk":    GREEN,
        "Medium Risk": ORANGE,
        "High Risk":   RED,
    }.get(risk_label, BLUE)


def generate_pdf_report(
    customer_name: str,
    data: dict,
    risk: str,
    risk_score: float,
    fraud: str,
    explanation: str,
    advice: list,
) -> bytes:
    """
    Generate a professional PDF credit risk report.
    Returns PDF as bytes for Streamlit download.
    """

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    risk_color = get_risk_color(risk)
    styles     = getSampleStyleSheet()
    story      = []

    # ── Custom Styles ──────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "Title",
        fontSize=22,
        textColor=WHITE,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        fontSize=11,
        textColor=TEXT_MUTED,
        alignment=TA_CENTER,
        fontName="Helvetica",
        spaceAfter=2,
    )
    section_style = ParagraphStyle(
        "Section",
        fontSize=13,
        textColor=WHITE,
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=6,
    )
    normal_style = ParagraphStyle(
        "Normal",
        fontSize=10,
        textColor=TEXT_PRIMARY,
        fontName="Helvetica",
        spaceAfter=4,
        leading=16,
    )
    muted_style = ParagraphStyle(
        "Muted",
        fontSize=9,
        textColor=TEXT_MUTED,
        fontName="Helvetica",
        spaceAfter=2,
    )
    risk_style = ParagraphStyle(
        "Risk",
        fontSize=20,
        textColor=risk_color,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    # ── Header ─────────────────────────────────────────────────────────────────
    header_data = [[
        Paragraph("AI Credit Risk Advisor", title_style),
    ]]
    header_table = Table(header_data, colWidths=[170 * mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_BG),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(header_table)

    story.append(Paragraph("Credit Risk Assessment Report", subtitle_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
        muted_style,
    ))
    story.append(Spacer(1, 8 * mm))

    # ── Customer Details ───────────────────────────────────────────────────────
    story.append(Paragraph("Customer Details", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=6))

    customer_data = [
        ["Field", "Value"],
        ["Customer Name",      customer_name],
        ["Age",                f"{int(data.get('age', 0))} years"],
        ["Monthly Income",     f"Rs. {float(data.get('MonthlyIncome', 0)):,.0f}"],
        ["Debt Ratio",         f"{float(data.get('DebtRatio', 0)) * 100:.1f}%"],
        ["Credit Utilization", f"{float(data.get('RevolvingUtilizationOfUnsecuredLines', 0)) * 100:.1f}%"],
        ["Report Date",        datetime.now().strftime("%d-%m-%Y")],
    ]

    customer_table = Table(customer_data, colWidths=[70 * mm, 100 * mm])
    customer_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  CARD_BG),
        ("BACKGROUND",   (0, 1), (-1, -1), DARK_BG),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  TEXT_MUTED),
        ("TEXTCOLOR",    (0, 1), (-1, -1), TEXT_PRIMARY),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 0), (-1, -1), 10),
        ("GRID",         (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [DARK_BG, CARD_BG]),
        ("TOPPADDING",   (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(customer_table)
    story.append(Spacer(1, 6 * mm))

    # ── Risk Score ─────────────────────────────────────────────────────────────
    story.append(Paragraph("Risk Assessment", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=6))

    risk_data = [[
        Paragraph(f"Risk Score: {risk_score:.1f} / 20", risk_style),
        Paragraph(risk, risk_style),
    ]]
    risk_table = Table(risk_data, colWidths=[85 * mm, 85 * mm])
    risk_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), CARD_BG),
        ("GRID",         (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING",   (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 12),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 4 * mm))

    # Risk level bar
    bar_width   = 170 * mm
    low_w       = bar_width * 0.4
    med_w       = bar_width * 0.3
    high_w      = bar_width * 0.3
    bar_data    = [[
        Paragraph("LOW RISK", ParagraphStyle("b", fontSize=8, textColor=WHITE,
                  fontName="Helvetica-Bold", alignment=TA_CENTER)),
        Paragraph("MEDIUM RISK", ParagraphStyle("b", fontSize=8, textColor=WHITE,
                  fontName="Helvetica-Bold", alignment=TA_CENTER)),
        Paragraph("HIGH RISK", ParagraphStyle("b", fontSize=8, textColor=WHITE,
                  fontName="Helvetica-Bold", alignment=TA_CENTER)),
    ]]
    bar_table = Table(bar_data, colWidths=[low_w, med_w, high_w])
    bar_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (0, 0), GREEN),
        ("BACKGROUND",   (1, 0), (1, 0), ORANGE),
        ("BACKGROUND",   (2, 0), (2, 0), RED),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("BOX",          (0, 0), (-1, -1), 1, BORDER),
    ]))
    story.append(bar_table)
    story.append(Spacer(1, 6 * mm))

    # ── Fraud Status ───────────────────────────────────────────────────────────
    story.append(Paragraph("Fraud Detection", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=6))

    fraud_color = RED if "Suspected" in str(fraud) else GREEN
    fraud_style = ParagraphStyle("fraud", fontSize=12, textColor=fraud_color,
                                  fontName="Helvetica-Bold", alignment=TA_CENTER)
    fraud_data = [[Paragraph(str(fraud), fraud_style)]]
    fraud_table = Table(fraud_data, colWidths=[170 * mm])
    fraud_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), CARD_BG),
        ("GRID",         (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
    ]))
    story.append(fraud_table)
    story.append(Spacer(1, 6 * mm))

    # ── AI Explanation ─────────────────────────────────────────────────────────
    story.append(Paragraph("AI Explanation", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=6))

    explanation_clean = str(explanation).replace("<", "&lt;").replace(">", "&gt;")
    exp_data = [[Paragraph(explanation_clean, normal_style)]]
    exp_table = Table(exp_data, colWidths=[170 * mm])
    exp_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), CARD_BG),
        ("GRID",         (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
        ("LEFTPADDING",  (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(exp_table)
    story.append(Spacer(1, 6 * mm))

    # ── Financial Advice ───────────────────────────────────────────────────────
    story.append(Paragraph("Financial Advice", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=6))

    advice_rows = []
    for i, tip in enumerate(advice):
        tip_clean = str(tip).replace("<", "&lt;").replace(">", "&gt;")
        advice_rows.append([
            Paragraph(f"{i + 1}.", ParagraphStyle("num", fontSize=10,
                      textColor=BLUE, fontName="Helvetica-Bold",
                      alignment=TA_CENTER)),
            Paragraph(tip_clean, normal_style),
        ])

    if advice_rows:
        advice_table = Table(advice_rows, colWidths=[12 * mm, 158 * mm])
        advice_table.setStyle(TableStyle([
            ("BACKGROUND",     (0, 0), (-1, -1), DARK_BG),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [DARK_BG, CARD_BG]),
            ("GRID",           (0, 0), (-1, -1), 0.5, BORDER),
            ("TOPPADDING",     (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING",  (0, 0), (-1, -1), 7),
            ("LEFTPADDING",    (0, 0), (-1, -1), 8),
            ("VALIGN",         (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(advice_table)

    story.append(Spacer(1, 8 * mm))

    # ── Footer ─────────────────────────────────────────────────────────────────
    footer_style = ParagraphStyle("footer", fontSize=8, textColor=TEXT_MUTED,
                                   alignment=TA_CENTER, fontName="Helvetica")
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=4))
    story.append(Paragraph(
        "This report is generated by AI Credit Risk Advisor. "
        "For internal use only. Not a substitute for professional financial advice.",
        footer_style,
    ))
    story.append(Paragraph(
        f"Confidential | Generated on {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        footer_style,
    ))

    # ── Build PDF ──────────────────────────────────────────────────────────────
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

"""
Script to generate data/qatar_sla_policy.pdf for vector store ingestion.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_policy_pdf(output_path="./data/qatar_sla_policy.pdf"):
    # Ensure data directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#800020'),  # Qatar Maroon
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#111827'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#374151'),
        spaceAfter=8
    )

    elements = []

    # Title Header
    elements.append(Paragraph("Qatar Mobile - Enterprise Hardware Diagnostic & SLA Warranty Policy", title_style))
    elements.append(Paragraph("<b>Compliance Framework:</b> Qatar Consumer Protection Law No. 8 of 2008 & Ministry of Commerce and Industry (MOCI) Guidelines", body_style))
    elements.append(Spacer(1, 10))

    # Section 1: Standard Warranty Terms
    elements.append(Paragraph("1. Standard Device Warranty Terms", h2_style))
    elements.append(Paragraph("All mobile phones and tablet devices purchased through Qatar Mobile authorized outlets carry a mandatory 12-month limited manufacturer warranty from the date of purchase.", body_style))
    elements.append(Paragraph("<b>Covered Defects:</b> Manufacturing flaws, internal component defects, display degradation not caused by impact, battery capacity dropping below 80% within 6 months, and motherboard software boot loops.", body_style))
    elements.append(Paragraph("<b>Exclusions:</b> Physical impact damage, shattered glass, water immersion, unauthorized third-party repairs, device rooting, or jailbreaking.", body_style))
    elements.append(Spacer(1, 8))

    # Section 2: Service Level Agreement (SLA) Turnaround Matrix
    elements.append(Paragraph("2. Service Level Agreement (SLA) Repair Matrix", h2_style))
    
    table_data = [
        ["Service Category", "Issue Description", "SLA Turnaround", "Warranty Coverage"],
        ["Screen / Display", "OLED/LCD touch replacement", "1 to 2 Business Days", "Covered if manufacturing defect; Out-of-warranty if cracked"],
        ["Battery Replacement", "Battery depletion / swelling", "Same Day (4 Hours)", "Covered within first 12 months"],
        ["Software Re-flash", "Boot loop / OS corruption", "24 Hours", "Fully covered under warranty"],
        ["Motherboard Repair", "Power IC / Micro-soldering", "3 to 5 Business Days", "Subject to technician inspection"],
        ["Liquid Damage", "Corrosion / Water contact", "Inspection required", "Out of warranty (Paid repair only)"]
    ]

    t = Table(table_data, colWidths=[110, 150, 110, 160])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#800020')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 12))

    # Section 3: Consumer Protection Rights
    elements.append(Paragraph("3. Consumer Protection Rights (Qatar Law No. 8)", h2_style))
    elements.append(Paragraph("Under Qatar Consumer Protection Law, if a mobile device exhibits a recurring technical defect within 15 days of purchase, the consumer is entitled to an immediate replacement unit or full refund.", body_style))
    elements.append(Paragraph("If a repair turnaround exceeds the committed SLA timeframe without prior written consent from the customer, Qatar Mobile will provide a temporary loan phone unit.", body_style))
    elements.append(Spacer(1, 8))

    # Section 4: Refusal and Refurbishment Policies
    elements.append(Paragraph("4. Policy Refusals and Non-Supported Services", h2_style))
    elements.append(Paragraph("Qatar Mobile strictly enforces privacy and safety regulations. The following requests are explicitly non-serviced and will be refused:", body_style))
    elements.append(Paragraph("• Removal or bypass of iCloud / Google Factory Reset Protection (FRP) locks without original purchase receipt and QID verification.", body_style))
    elements.append(Paragraph("• Installation of custom firmware, device rooting, or iOS jailbreaking.", body_style))
    elements.append(Paragraph("• Non-mobile hardware service requests (e.g., automobile electronics, home appliances).", body_style))

    doc.build(elements)
    print(f"✅ Policy PDF generated successfully at: {output_path}")


if __name__ == "__main__":
    generate_policy_pdf()
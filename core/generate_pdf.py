"""
Generates data/qatar_sla_policy.pdf aligned with Qatar Consumer Protection Law No. 8 (2008)
and Ministerial Decision No. 68 of 2012 for ChromaDB vector store ingestion.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_policy_pdf(output_path: str = "./data/qatar_sla_policy.pdf") -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#800020"),
        spaceAfter=12,
    )
    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#111827"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#374151"),
        spaceAfter=8,
    )

    elements = [
        Paragraph("Qatar Mobile - Enterprise Hardware Diagnostic & SLA Warranty Policy", title_style),
        Paragraph(
            "<b>Compliance Framework:</b> Qatar Consumer Protection Law No. 8 of 2008, "
            "Ministerial Decision No. 68 of 2012 & CRA QoS Regulations",
            body_style,
        ),
        Spacer(1, 10),
        Paragraph("1. Standard Device Warranty Terms (Law No. 8 of 2008)", h2_style),
        Paragraph(
            "All smartphones, tablets, laptops, and gaming consoles purchased through Qatar Mobile authorized outlets "
            "carry a mandatory 2-year (24-month) statutory GCC/Qatar warranty against manufacturing defects from the date of purchase.",
            body_style,
        ),
        Paragraph(
            "<b>Covered Defects (Articles 1, 5 & 13):</b> Manufacturing flaws, internal component defects, "
            "display degradation not caused by impact, premature lithium-ion battery swelling, and motherboard faults.",
            body_style,
        ),
        Paragraph(
            "<b>Exclusions & Out-of-Warranty Repairs (Decision No. 68 of 2012, Reg. 11):</b> Physical impact damage, "
            "shattered glass, and liquid/port corrosion require a written cost and turnaround estimate approved by the "
            "consumer prior to repair, and replaced spare parts carry a mandatory 6-month warranty.",
            body_style,
        ),
        Spacer(1, 8),
        Paragraph("2. Service Level Agreement (SLA) Repair Matrix", h2_style),
    ]

    table_data = [
        ["Service Category", "Issue Description", "SLA Turnaround", "Warranty Coverage"],
        ["Screen / Display", "OLED/LCD touch replacement", "1 to 2 Business Days", "Covered if factory defect; Paid quote if cracked"],
        ["Battery Replacement", "Battery swelling / thermal defect", "Same Day to 3 Days", "Covered under 2-year statutory safety warranty"],
        ["Software Re-flash", "Boot loop / OS corruption", "24 Hours", "Fully covered under warranty"],
        ["Motherboard Repair", "Power IC / Micro-soldering", "3 to 5 Business Days", "Subject to technician inspection"],
        ["Liquid Damage", "USB-C / Port corrosion", "3 to 5 Business Days", "Out of warranty (6-month warranty on replaced parts)"],
    ]

    t = Table(table_data, colWidths=[110, 150, 110, 160])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#800020")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    elements.extend(
        [
            t,
            Spacer(1, 12),
            Paragraph("3. Statutory Consumer Protection Rights", h2_style),
            Paragraph(
                "<b>Substitute Loaner Device (Article 9 & Reg. 10):</b> Where executing warranty repairs exceeds "
                "fifteen (15) days, Qatar Mobile must provide a similar substitute device free of charge until repairs finish.",
                body_style,
            ),
            Paragraph(
                "<b>Repeat Defect Replacement/Refund (Article 16):</b> If the same manufacturing defect recurs after "
                "repeated repair attempts, the consumer has the statutory right to a brand-new replacement or full refund.",
                body_style,
            ),
        ]
    )

    doc.build(elements)
    print(f"Policy PDF generated successfully at: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_policy_pdf()
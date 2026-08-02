"""
Generates the Credit & Debit Requisition PDF from structured data captured
in the app -- replacing the manually hand-filled Excel/Word template.
All totals (credit value, re-invoice value, net value) are calculated
here, not typed by hand.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

NAVY = colors.HexColor("#1F3864")
LIGHT = colors.HexColor("#F2F2F2")

def generate_requisition_pdf(output_path, request, items, approvals):
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                             topMargin=20*mm, bottomMargin=15*mm,
                             leftMargin=15*mm, rightMargin=15*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleNavy", parent=styles["Title"], textColor=NAVY, fontSize=18)
    h2_style = ParagraphStyle("H2Navy", parent=styles["Heading2"], textColor=NAVY, fontSize=12)
    normal = styles["Normal"]

    story = []
    story.append(Paragraph("Credit &amp; Debit Requisition", title_style))
    story.append(Paragraph(f"Generated {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal))
    story.append(Spacer(1, 10*mm))

    header_data = [
        ["Client Name", request["client_name"], "Date", datetime.now().strftime("%d/%m/%Y")],
        ["Account Number", request["account_no"], "Region", request["region"]],
        ["Department", request["dept"], "Credit Controller", request["credit_controller"]],
    ]
    header_table = Table(header_data, colWidths=[35*mm, 55*mm, 35*mm, 55*mm])
    header_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
        ("BACKGROUND", (2, 0), (2, -1), LIGHT),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8*mm))

    story.append(Paragraph("Credit / Re-invoice Line Items", h2_style))
    story.append(Spacer(1, 3*mm))

    item_rows = [["Invoice No", "Charge Code", "Description", "Qty", "Rate", "Credit (Excl)", "Re-invoice (Excl)"]]
    total_credit = 0.0
    total_reinvoice = 0.0
    for it in items:
        credit = it["credit_amount"] or 0
        reinvoice = it["reinvoice_amount"] or 0
        total_credit += credit
        total_reinvoice += reinvoice
        item_rows.append([
            it["invoice_no"], it["charge_code"], it["description"],
            str(it["qty"]), f"R {it['rate']:.2f}" if it["rate"] else "",
            f"R {credit:,.2f}", f"R {reinvoice:,.2f}" if reinvoice else "-",
        ])
    item_rows.append(["", "", "", "", "TOTAL", f"R {total_credit:,.2f}", f"R {total_reinvoice:,.2f}"])

    item_table = Table(item_rows, colWidths=[28*mm, 20*mm, 45*mm, 12*mm, 20*mm, 25*mm, 30*mm])
    item_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), LIGHT),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(item_table)
    story.append(Spacer(1, 6*mm))

    net_value = total_credit - total_reinvoice
    summary_data = [
        ["Total Credit Value (Excl. VAT)", f"R {total_credit:,.2f}"],
        ["Total Re-invoice Value (Excl. VAT)", f"R {total_reinvoice:,.2f}"],
        ["Net Value", f"R {net_value:,.2f}"],
    ]
    summary_table = Table(summary_data, colWidths=[80*mm, 40*mm])
    summary_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("BACKGROUND", (0, -1), (-1, -1), LIGHT),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 8*mm))

    story.append(Paragraph("Reason for Credit", h2_style))
    reasons = "; ".join(sorted(set(it["reason"] for it in items if it["reason"])))
    story.append(Paragraph(reasons or "-", normal))
    story.append(Spacer(1, 3*mm))
    responsible = "; ".join(sorted(set(f"{it['responsible_person']} ({it['responsible_dept']})" for it in items)))
    story.append(Paragraph(f"<b>Person(s) Responsible:</b> {responsible}", normal))
    story.append(Spacer(1, 8*mm))

    story.append(Paragraph("Approval Chain", h2_style))
    story.append(Spacer(1, 3*mm))
    approval_rows = [["Role", "Name", "Status", "Signed At"]]
    for a in approvals:
        approval_rows.append([
            a["approver_role"], a["approver_name"],
            a["status"].upper(), a["signed_at"] or "-",
        ])
    approval_table = Table(approval_rows, colWidths=[45*mm, 45*mm, 30*mm, 40*mm])
    approval_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
    ]))
    story.append(approval_table)

    doc.build(story)
    return output_path

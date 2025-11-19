#!/usr/bin/env python3
"""
PDF Generation with ReportLab
Creates professional PDF documents from scratch
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime

def create_purchase_agreement_pdf(data):
    """Generate stock purchase agreement PDF"""

    filename = f"Agreement_{data['buyer_name'].replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Centered', parent=styles['Normal'],
                             alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Justified', parent=styles['Normal'],
                             alignment=TA_JUSTIFY))

    # Title
    title = Paragraph("<b>STOCK PURCHASE AGREEMENT</b>", styles['Centered'])
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))

    # Date
    date_text = f"Dated: {datetime.now().strftime('%B %d, %Y')}"
    elements.append(Paragraph(date_text, styles['Centered']))
    elements.append(Spacer(1, 0.5*inch))

    # Parties
    parties_text = f"""
    This Stock Purchase Agreement (the "Agreement") is entered into as of the date set forth above
    between {data['buyer_name']}, a {data['buyer_state']} corporation (the "Buyer"), and
    {data['seller_name']}, a {data['seller_state']} corporation (the "Seller").
    """
    elements.append(Paragraph(parties_text, styles['Justified']))
    elements.append(Spacer(1, 0.2*inch))

    # Recitals
    elements.append(Paragraph("<b>RECITALS</b>", styles['Heading2']))
    recital_text = f"""
    WHEREAS, Seller owns {data['shares_owned']:,} shares of {data['stock_class']} of
    {data['company_name']} (the "Company"); and
    <br/><br/>
    WHEREAS, Buyer desires to purchase and Seller desires to sell such shares upon the terms
    and conditions set forth in this Agreement.
    """
    elements.append(Paragraph(recital_text, styles['Justified']))
    elements.append(Spacer(1, 0.3*inch))

    # Agreement section
    elements.append(Paragraph("<b>AGREEMENT</b>", styles['Heading2']))
    elements.append(Paragraph("<b>1. Purchase and Sale</b>", styles['Heading3']))
    purchase_text = f"""
    Subject to the terms and conditions of this Agreement, Seller agrees to sell to Buyer,
    and Buyer agrees to purchase from Seller, {data['shares_owned']:,} shares of
    {data['stock_class']} of the Company for a purchase price of ${data['purchase_price']:,.2f}
    (the "Purchase Price").
    """
    elements.append(Paragraph(purchase_text, styles['Justified']))
    elements.append(Spacer(1, 0.2*inch))

    # Shareholders table
    elements.append(Paragraph("<b>Schedule A: Shareholders</b>", styles['Heading3']))
    table_data = [['Name', 'Shares', 'Percentage']]
    for shareholder in data.get('shareholders', []):
        table_data.append([
            shareholder['name'],
            f"{shareholder['shares']:,}",
            f"{shareholder['percentage']:.2f}%"
        ])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))

    # Signature blocks
    elements.append(PageBreak())
    elements.append(Paragraph("<b>SIGNATURES</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.3*inch))

    signature_text = f"""
    <b>BUYER:</b><br/>
    <br/>
    ________________________________<br/>
    {data['buyer_name']}<br/>
    <br/><br/>
    <b>SELLER:</b><br/>
    <br/>
    ________________________________<br/>
    {data['seller_name']}
    """
    elements.append(Paragraph(signature_text, styles['Normal']))

    # Build PDF
    doc.build(elements)
    print(f'Created: {filename}')

    return filename

if __name__ == '__main__':
    # Example data
    agreement_data = {
        'buyer_name': 'Acme Acquisition Corp',
        'buyer_state': 'Delaware',
        'seller_name': 'Smith Industries Inc',
        'seller_state': 'California',
        'company_name': 'Target Company LLC',
        'shares_owned': 1000,
        'stock_class': 'Common Stock',
        'purchase_price': 5000000,
        'shareholders': [
            {'name': 'John Smith', 'shares': 600, 'percentage': 60.0},
            {'name': 'Jane Doe', 'shares': 400, 'percentage': 40.0}
        ]
    }

    create_purchase_agreement_pdf(agreement_data)

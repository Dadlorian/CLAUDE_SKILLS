#!/usr/bin/env python3
"""
Advanced DOCX with Templates using docxtpl
Uses Jinja2 templating within Word documents
"""

from docxtpl import DocxTemplate
from datetime import datetime, timedelta

def generate_stock_purchase_agreement(data):
    """Generate stock purchase agreement from template"""

    # Load template
    doc = DocxTemplate("templates/stock_purchase_template.docx")

    # Calculate derived values
    data['ownership_percentage'] = (
        data['shares_purchased'] / data['total_shares'] * 100
    )
    data['payment_at_closing'] = data['purchase_price'] - data.get('escrow_amount', 0)

    # Format currency
    data['purchase_price_formatted'] = f"${data['purchase_price']:,.2f}"
    data['payment_at_closing_formatted'] = f"${data['payment_at_closing']:,.2f}"

    # Format dates
    effective_date = datetime.strptime(data['effective_date'], '%Y-%m-%d')
    data['effective_date_long'] = effective_date.strftime('%B %d, %Y')

    # Add closing date (30 days from effective)
    closing_date = effective_date + timedelta(days=30)
    data['closing_date'] = closing_date.strftime('%B %d, %Y')

    # Render template
    doc.render(data)

    # Save
    filename = f"SPA_{data['buyer_name']}_{data['seller_name']}.docx"
    doc.save(filename)
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
        'purchase_price': 5000000,
        'shares_purchased': 1000,
        'total_shares': 1000,
        'stock_class': 'Common Stock',
        'effective_date': '2025-11-19',
        'escrow_amount': 500000,
        'include_earnout': True,
        'earnout_amount': 1000000
    }

    generate_stock_purchase_agreement(agreement_data)

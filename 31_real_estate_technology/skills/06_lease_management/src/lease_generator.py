"""Lease Document Generator"""
from docx import Document
from datetime import datetime, timedelta

class LeaseGenerator:
    def __init__(self, template_path):
        self.template = Document(template_path)
        
    def generate_lease(self, lease_data):
        """Generate lease from template"""
        doc = self.template
        
        # Replace placeholders
        replacements = {
            '{{TENANT_NAME}}': lease_data['tenant_name'],
            '{{PROPERTY_ADDRESS}}': lease_data['property_address'],
            '{{MONTHLY_RENT}}': f"${lease_data['monthly_rent']:,.2f}",
            '{{LEASE_START}}': lease_data['start_date'].strftime('%B %d, %Y'),
            '{{LEASE_END}}': lease_data['end_date'].strftime('%B %d, %Y'),
            '{{SECURITY_DEPOSIT}}': f"${lease_data['security_deposit']:,.2f}"
        }
        
        for paragraph in doc.paragraphs:
            for key, value in replacements.items():
                if key in paragraph.text:
                    paragraph.text = paragraph.text.replace(key, value)
                    
        output_path = f"lease_{lease_data['tenant_name'].replace(' ', '_')}.docx"
        doc.save(output_path)
        return output_path
        
    def calculate_lease_dates(self, start_date, term_months=12):
        """Calculate lease end date"""
        end_date = start_date + timedelta(days=term_months * 30)
        return {
            'start_date': start_date,
            'end_date': end_date,
            'term_months': term_months
        }

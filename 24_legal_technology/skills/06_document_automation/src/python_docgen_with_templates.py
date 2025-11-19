#!/usr/bin/env python3
"""
Document generation using Jinja2 templates with python-docx
More flexible template approach
"""

from jinja2 import Template
from docx import Document
from io import BytesIO

class JinjaDocumentGenerator:
    def __init__(self, template_content):
        """Initialize with template content string."""
        self.template = Template(template_content)
    
    def render(self, data):
        """Render template with data."""
        return self.template.render(**data)
    
    def generate_document_from_template(self, data, output_path):
        """Generate Word document from Jinja2 template."""
        # First render the template
        rendered_content = self.render(data)
        
        # Create a Word document and add rendered content
        doc = Document()
        
        # Add paragraphs from rendered template
        for line in rendered_content.split('\n'):
            if line.strip():
                doc.add_paragraph(line)
        
        doc.save(output_path)
        return output_path


class TemplateLoader:
    """Load templates from various sources."""
    
    @staticmethod
    def load_from_file(filepath):
        """Load template from file."""
        with open(filepath, 'r') as f:
            return f.read()
    
    @staticmethod
    def load_from_string(template_string):
        """Load template from string."""
        return template_string


# Example template string
ENGAGEMENT_LETTER_TEMPLATE = """
ENGAGEMENT LETTER

Date: {{ date }}
Client: {{ client_name }}
Address: {{ client_address }}

Re: Legal Services

Dear {{ client_name }},

This engagement letter sets forth the terms of our representation.

Scope of Services:
{{ scope }}

Fees:
Our hourly rate is {{ hourly_rate }}

Terms:
- Retainer: {{ retainer }}
- Billing: {{ billing_frequency }}

{% if special_terms %}
Special Terms:
{{ special_terms }}
{% endif %}

Sincerely,
{{ attorney_name }}
{{ firm_name }}
"""

# Example usage
if __name__ == '__main__':
    data = {
        'date': '2024-01-15',
        'client_name': 'Smith & Co.',
        'client_address': '789 Business Blvd, Boston, MA',
        'scope': 'Corporate contract review and negotiation',
        'hourly_rate': '$350/hour',
        'retainer': '$5,000',
        'billing_frequency': 'Monthly',
        'special_terms': 'Includes up to 5 hours of preliminary consultation',
        'attorney_name': 'Sarah Johnson',
        'firm_name': 'Johnson & Associates LLP'
    }
    
    generator = JinjaDocumentGenerator(ENGAGEMENT_LETTER_TEMPLATE)
    output = generator.generate_document_from_template(data, 'output/engagement.docx')
    print(f"Generated: {output}")

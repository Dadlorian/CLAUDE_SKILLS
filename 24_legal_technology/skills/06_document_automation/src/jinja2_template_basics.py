#!/usr/bin/env python3
"""
Jinja2 template basics for legal document generation
"""

from jinja2 import Environment, FileSystemLoader, select_autoescape

class Jinja2DocumentEngine:
    def __init__(self, template_dir='templates'):
        """Initialize Jinja2 environment."""
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def render_template(self, template_name, context):
        """Render template with provided context."""
        template = self.env.get_template(template_name)
        return template.render(**context)
    
    def render_string(self, template_string, context):
        """Render template from string."""
        template = self.env.from_string(template_string)
        return template.render(**context)


# Example template for engagement letter
ENGAGEMENT_LETTER = """
ENGAGEMENT LETTER

Date: {{ date }}

{% if client.type == 'individual' %}
Re: Legal Representation - {{ client.first_name }} {{ client.last_name }}

Dear {{ client.first_name }},
{% else %}
Re: Legal Services - {{ client.company_name }}

Dear {{ client.contact_name }},
{% endif %}

This letter sets forth the terms of our engagement to provide legal services.

SCOPE OF SERVICES
We will provide the following services:
{% for service in services %}
  - {{ service.description }}
{% endfor %}

FEES AND BILLING
- Hourly rate: {{ billing.hourly_rate }}
- Retainer: {{ billing.retainer }}
- Billing frequency: {{ billing.frequency }}

{% if matter.is_contingency %}
CONTINGENCY ARRANGEMENT
This engagement is on a contingency basis. We will receive a fee equal to
{{ matter.contingency_percentage }}% of any recovery.
{% endif %}

TERMS
- Retainer is due upon receipt
- Monthly invoices for time billed in excess of retainer
- Disputes regarding invoices must be raised within 30 days

Sincerely,

{{ firm.attorney_name }}
{{ firm.firm_name }}
{{ firm.address }}
"""

# Example usage
if __name__ == '__main__':
    context = {
        'date': '2024-01-15',
        'client': {
            'type': 'individual',
            'first_name': 'John',
            'last_name': 'Smith',
        },
        'services': [
            {'description': 'Contract review and negotiation'},
            {'description': 'General legal advice'},
            {'description': 'Document preparation'},
        ],
        'billing': {
            'hourly_rate': '$350/hour',
            'retainer': '$5,000',
            'frequency': 'Monthly',
        },
        'matter': {
            'is_contingency': False,
        },
        'firm': {
            'attorney_name': 'Sarah Johnson',
            'firm_name': 'Johnson & Associates LLP',
            'address': '100 Legal Plaza, Boston, MA 02101',
        },
    }
    
    engine = Jinja2DocumentEngine()
    output = engine.render_string(ENGAGEMENT_LETTER, context)
    print(output)

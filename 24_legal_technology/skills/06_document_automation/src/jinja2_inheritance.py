#!/usr/bin/env python3
"""
Jinja2 template inheritance for legal document templates
Reuse common elements across multiple document types
"""

from jinja2 import Environment, DictLoader

# Base template with common structure
BASE_TEMPLATE = """
{%- block header %}
{%- if letterhead %}
{{ letterhead.firm_name }}
{{ letterhead.address }}
{{ letterhead.phone }}
{{ letterhead.email }}
{%- endif %}

[DATE]
{{ date }}

{%- endblock %}

{%- block recipient %}
{{ client.name }}
{{ client.address }}
{%- endblock %}

{%- block greeting %}
Dear {{ client.name }},
{%- endblock %}

{%- block body %}
{%- endblock %}

{%- block closing %}
Sincerely,

{{ attorney.signature_block }}
{{ attorney.bar_number }}
{%- endblock %}
"""

# Agreement template extending base
AGREEMENT_TEMPLATE = """
{% extends "base.html" %}

{% block body %}
AGREEMENT

This Agreement is made and entered into as of {{ date }} between {{ parties.first_name }} ("Party A") and {{ parties.second_name }} ("Party B").

RECITALS:
WHEREAS, the parties desire to enter into an agreement regarding {{ matter.description }};

NOW, THEREFORE, in consideration of the mutual covenants and agreements herein contained, the parties agree as follows:

{% for section in agreement.sections %}
{{ section.number }}. {{ section.title }}
{{ section.content }}

{% endfor %}

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

{% for party in agreement.signing_parties %}
{{ party.name }}
Signature: _____________________
Date: ___________________________

{% endfor %}
{% endblock %}
"""

# Letter template extending base
LETTER_TEMPLATE = """
{% extends "base.html" %}

{% block body %}
Re: {{ matter.subject }}

{{ letter.opening_paragraph }}

{% for paragraph in letter.body_paragraphs %}
{{ paragraph }}

{% endfor %}

{{ letter.closing_paragraph }}
{% endblock %}
"""

class TemplateInheritanceEngine:
    def __init__(self):
        """Initialize with all templates."""
        templates = {
            'base.html': BASE_TEMPLATE,
            'agreement.html': AGREEMENT_TEMPLATE,
            'letter.html': LETTER_TEMPLATE,
        }
        self.env = Environment(loader=DictLoader(templates))
    
    def render(self, template_name, context):
        """Render a template with inheritance."""
        template = self.env.get_template(template_name)
        return template.render(**context)


# Example usage
if __name__ == '__main__':
    engine = TemplateInheritanceEngine()
    
    agreement_context = {
        'letterhead': {
            'firm_name': 'Johnson & Associates LLP',
            'address': '100 Legal Plaza, Boston, MA',
            'phone': '(617) 555-0100',
            'email': 'info@johnson-law.com',
        },
        'date': 'January 15, 2024',
        'client': {
            'name': 'John Smith',
            'address': '123 Main St, Boston, MA 02101',
        },
        'attorney': {
            'signature_block': 'Sarah Johnson, Esq.',
            'bar_number': 'MA Bar #123456',
        },
        'matter': {
            'description': 'the purchase of real property',
        },
        'parties': {
            'first_name': 'John Smith',
            'second_name': 'Jane Doe',
        },
        'agreement': {
            'sections': [
                {
                    'number': '1',
                    'title': 'Agreement',
                    'content': 'The parties hereby agree to the following terms.',
                },
            ],
            'signing_parties': [
                {'name': 'John Smith'},
                {'name': 'Jane Doe'},
            ],
        },
    }
    
    output = engine.render('agreement.html', agreement_context)
    print(output)

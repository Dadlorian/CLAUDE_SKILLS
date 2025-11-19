"""
Template Engine for Document Generation
Uses Jinja2 to create dynamic legal documents from templates.

Dependencies: jinja2
Install: pip install jinja2
"""

from jinja2 import Template, Environment, FileSystemLoader
from typing import Dict, Any, Optional
from datetime import datetime
import os


class TemplateEngine:
    """Engine for generating documents from templates with variable substitution."""

    def __init__(self, template_dir: Optional[str] = None):
        """Initialize template engine."""
        if template_dir:
            self.env = Environment(loader=FileSystemLoader(template_dir))
        else:
            self.env = Environment()

    def render_string(self, template_str: str, context: Dict[str, Any]) -> str:
        """Render template string with context variables."""
        template = Template(template_str)
        return template.render(**context)

    def render_file(self, filename: str, context: Dict[str, Any]) -> str:
        """Render template file with context variables."""
        template = self.env.get_template(filename)
        return template.render(**context)

    def save_rendered(self, template_str: str, context: Dict[str, Any], output_file: str) -> None:
        """Render template and save to file."""
        rendered = self.render_string(template_str, context)
        with open(output_file, 'w') as f:
            f.write(rendered)
        print(f"Document saved to {output_file}")


# Template Examples

SERVICE_AGREEMENT_TEMPLATE = """
SERVICE AGREEMENT

THIS SERVICE AGREEMENT (the "Agreement") is entered into as of {{ date }}
between {{ client_name }} ("Client") and {{ provider_name }} ("Provider").

1. SERVICES
Provider agrees to provide the following services to Client:
{% for service in services %}
   - {{ service }}
{% endfor %}

2. FEES AND PAYMENT
The fees for services shall be as follows:
   - Hourly Rate: ${{ hourly_rate }}/hour
   - Monthly Retainer: ${{ monthly_retainer }}
   - Payment Terms: Due within {{ payment_terms }} days of invoice

3. TERM AND TERMINATION
This Agreement shall commence on {{ start_date }} and continue for {{ duration }} year(s).
Either party may terminate with {{ termination_notice }} days written notice.

4. CONFIDENTIALITY
Both parties agree to maintain strict confidentiality of all proprietary information
and trade secrets of the other party for a period of {{ confidentiality_period }} years.

5. LIABILITY LIMITATION
Neither party shall be liable for indirect, incidental, or consequential damages.
Total liability is limited to fees paid in the {{ months_lookback }} months preceding the claim.

6. GOVERNING LAW
This Agreement shall be governed by the laws of {{ governing_state }}.

7. ENTIRE AGREEMENT
This Agreement constitutes the entire agreement between parties.

IN WITNESS WHEREOF:

Client: ________________________     Date: __________
        {{ client_name }}

Provider: ________________________     Date: __________
          {{ provider_name }}
"""

NDA_TEMPLATE = """
NON-DISCLOSURE AGREEMENT

THIS AGREEMENT is made on {{ date }} between:

DISCLOSING PARTY: {{ disclosing_party }}
RECEIVING PARTY: {{ receiving_party }}

1. DEFINITION OF CONFIDENTIAL INFORMATION
Confidential Information includes:
{% for category in confidential_categories %}
   - {{ category }}
{% endfor %}

2. TERM OF CONFIDENTIALITY
The receiving party agrees to maintain confidentiality for {{ confidentiality_period }} years
from the date of disclosure.

3. PERMITTED USES
The Receiving Party may use Confidential Information only for:
{% for use in permitted_uses %}
   - {{ use }}
{% endfor %}

4. EXCLUSIONS
Information is not confidential if:
{% for exclusion in exclusions %}
   - {{ exclusion }}
{% endfor %}

5. RETURN OF INFORMATION
Upon request or termination, all Confidential Information shall be returned or destroyed.

6. REMEDIES
The parties acknowledge that breach may cause irreparable harm for which monetary damages
are insufficient. Injunctive relief is available.

AGREED AND ACCEPTED:

Disclosing Party: ________________________     Date: __________
                 {{ disclosing_party }}

Receiving Party: ________________________     Date: __________
                {{ receiving_party }}
"""

EMPLOYMENT_OFFER_TEMPLATE = """
EMPLOYMENT OFFER LETTER

{{ company_name }}
{{ company_address }}

{{ date }}

{{ candidate_name }}
{{ candidate_address }}

RE: OFFER OF EMPLOYMENT

Dear {{ candidate_name }},

We are pleased to offer you employment as {{ job_title }} with {{ company_name }}.

POSITION DETAILS:
- Title: {{ job_title }}
- Department: {{ department }}
- Location: {{ location }}
- Start Date: {{ start_date }}
- Reports To: {{ reports_to }}

COMPENSATION:
- Annual Salary: ${{ annual_salary }}
- Bonus Structure: {{ bonus_structure }}%
- Stock Options: {{ stock_options }} shares

BENEFITS:
- Health Insurance: {{ health_insurance_desc }}
- Retirement Plan: {{ retirement_plan_desc }}
- Paid Time Off: {{ pto_days }} days per year
- Professional Development: ${{ professional_development_budget }}/year

AT-WILL EMPLOYMENT:
Your employment is at-will and may be terminated by either party with {{ termination_notice }} days notice.

CONFIDENTIALITY:
You agree to maintain strict confidentiality of all Company proprietary information
as detailed in the attached Employee Agreement.

BACKGROUND CHECK:
This offer is contingent upon successful completion of background verification.

This offer expires on {{ offer_expiration_date }}.

To accept, please sign below and return by {{ response_deadline }}.

Sincerely,

________________________
{{ hiring_manager_name }}
{{ hiring_manager_title }}

ACCEPTANCE:

I accept this offer of employment.

Employee: ________________________     Date: __________
         {{ candidate_name }}
"""

INVOICE_TEMPLATE = """
INVOICE

INVOICE NUMBER: {{ invoice_number }}
DATE: {{ invoice_date }}
DUE DATE: {{ due_date }}

FROM:
{{ law_firm_name }}
{{ law_firm_address }}
{{ law_firm_phone }}

TO:
{{ client_name }}
{{ client_address }}

DESCRIPTION OF SERVICES:
{% for item in invoice_items %}
{{ item.description }} - Hours: {{ item.hours }} @ ${{ item.hourly_rate }}/hr = ${{ item.amount }}
{% endfor %}

SUMMARY:
Subtotal:           ${{ subtotal }}
Tax ({{ tax_rate }}%):          ${{ tax_amount }}
Total Due:          ${{ total_amount }}

PAYMENT TERMS:
Payment is due by {{ due_date }}.
Late payment subject to {{ late_fee_percent }}% monthly interest.

Payment should be made to:
{{ payment_instructions }}

Thank you for your business!
"""


def example_service_agreement():
    """Generate service agreement with template."""
    engine = TemplateEngine()

    context = {
        'date': datetime.now().strftime('%B %d, %Y'),
        'client_name': 'Acme Corporation',
        'provider_name': 'Legal Solutions LLC',
        'services': [
            'Contract drafting and review',
            'Legal research and analysis',
            'Compliance consulting',
            'Litigation support'
        ],
        'hourly_rate': 250,
        'monthly_retainer': 5000,
        'payment_terms': 30,
        'start_date': 'January 1, 2024',
        'duration': 1,
        'termination_notice': 30,
        'confidentiality_period': 3,
        'months_lookback': 12,
        'governing_state': 'California'
    }

    rendered = engine.render_string(SERVICE_AGREEMENT_TEMPLATE, context)
    with open('/tmp/service_agreement_template.txt', 'w') as f:
        f.write(rendered)
    print("Service Agreement generated: /tmp/service_agreement_template.txt")
    return rendered


def example_nda():
    """Generate NDA with template."""
    engine = TemplateEngine()

    context = {
        'date': datetime.now().strftime('%B %d, %Y'),
        'disclosing_party': 'TechStartup Inc.',
        'receiving_party': 'Potential Investor LLC',
        'confidential_categories': [
            'Business plans and strategies',
            'Financial information',
            'Technical specifications',
            'Customer lists and data',
            'Pricing information'
        ],
        'confidentiality_period': 3,
        'permitted_uses': [
            'Evaluating the business opportunity',
            'Due diligence review',
            'Internal discussion with advisors'
        ],
        'exclusions': [
            'Information already public',
            'Information independently developed',
            'Information rightfully obtained from third parties',
            'Information required by law to disclose'
        ]
    }

    rendered = engine.render_string(NDA_TEMPLATE, context)
    with open('/tmp/nda_template.txt', 'w') as f:
        f.write(rendered)
    print("NDA generated: /tmp/nda_template.txt")
    return rendered


def example_employment_offer():
    """Generate employment offer with template."""
    engine = TemplateEngine()

    context = {
        'company_name': 'TechCorp Industries',
        'company_address': '123 Business Ave, San Francisco, CA 94102',
        'date': datetime.now().strftime('%B %d, %Y'),
        'candidate_name': 'Jane Smith',
        'candidate_address': '456 Oak St, San Jose, CA 95110',
        'job_title': 'Senior Legal Counsel',
        'department': 'Legal & Compliance',
        'location': 'San Francisco, CA',
        'start_date': 'January 15, 2024',
        'reports_to': 'General Counsel',
        'annual_salary': 180000,
        'bonus_structure': 15,
        'stock_options': 5000,
        'health_insurance_desc': 'Comprehensive medical, dental, and vision coverage',
        'retirement_plan_desc': '401(k) with 4% company match',
        'pto_days': 20,
        'professional_development_budget': 5000,
        'termination_notice': 2,
        'offer_expiration_date': datetime.now().strftime('%B %d, %Y'),
        'response_deadline': datetime.now().strftime('%B %d, %Y'),
        'hiring_manager_name': 'John Doe',
        'hiring_manager_title': 'VP of Legal'
    }

    rendered = engine.render_string(EMPLOYMENT_OFFER_TEMPLATE, context)
    with open('/tmp/employment_offer_template.txt', 'w') as f:
        f.write(rendered)
    print("Employment Offer generated: /tmp/employment_offer_template.txt")
    return rendered


def example_invoice():
    """Generate invoice with template."""
    engine = TemplateEngine()

    context = {
        'invoice_number': 'INV-2024-001',
        'invoice_date': datetime.now().strftime('%B %d, %Y'),
        'due_date': 'January 31, 2024',
        'law_firm_name': 'Justice Legal Partners',
        'law_firm_address': '789 Law St, New York, NY 10001',
        'law_firm_phone': '(555) 123-4567',
        'client_name': 'Corporate Client LLC',
        'client_address': '999 Business Blvd, New York, NY 10002',
        'invoice_items': [
            {'description': 'Contract review and analysis', 'hours': 8, 'hourly_rate': 250, 'amount': 2000},
            {'description': 'Legal research and memo', 'hours': 12, 'hourly_rate': 200, 'amount': 2400},
            {'description': 'Litigation support', 'hours': 5, 'hourly_rate': 300, 'amount': 1500}
        ],
        'subtotal': 5900,
        'tax_rate': 8.5,
        'tax_amount': 501.50,
        'total_amount': 6401.50,
        'late_fee_percent': 1.5,
        'payment_instructions': 'Wire transfer or check payable to Justice Legal Partners'
    }

    rendered = engine.render_string(INVOICE_TEMPLATE, context)
    with open('/tmp/invoice_template.txt', 'w') as f:
        f.write(rendered)
    print("Invoice generated: /tmp/invoice_template.txt")
    return rendered


if __name__ == "__main__":
    example_service_agreement()
    example_nda()
    example_employment_offer()
    example_invoice()
    print("\nAll templates generated successfully!")

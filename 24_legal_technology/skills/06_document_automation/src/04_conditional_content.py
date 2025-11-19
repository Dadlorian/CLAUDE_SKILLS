"""
Conditional Content Generation
Dynamically include/exclude sections and content based on conditions.

Dependencies: jinja2
Install: pip install jinja2
"""

from jinja2 import Template
from typing import Dict, Any, List
from datetime import datetime
from enum import Enum


class ContractType(Enum):
    """Types of contracts."""
    SERVICE = "service"
    EMPLOYMENT = "employment"
    PURCHASE = "purchase"
    LEASE = "lease"
    NDA = "nda"


class PartyType(Enum):
    """Type of party."""
    INDIVIDUAL = "individual"
    CORPORATION = "corporation"
    LLC = "llc"
    PARTNERSHIP = "partnership"


class ConditionalDocumentGenerator:
    """Generate documents with conditional content based on rules."""

    @staticmethod
    def generate_contract(contract_type: ContractType, data: Dict[str, Any]) -> str:
        """Generate contract with conditional sections."""

        template_str = """
{{ contract_title }}

THIS AGREEMENT ("Agreement") is entered into as of {{ date }} between:

{% if party_a_type == "individual" %}
PARTY A: {{ party_a_first_name }} {{ party_a_last_name }} ("Party A")
{% else %}
PARTY A: {{ party_a_name }} ("Party A")
{% endif %}

{% if party_b_type == "individual" %}
PARTY B: {{ party_b_first_name }} {{ party_b_last_name }} ("Party B")
{% else %}
PARTY B: {{ party_b_name }} ("Party B")
{% endif %}

{% if include_recitals %}
RECITALS

WHEREAS, the parties desire to enter into this Agreement for the mutual benefit of both parties;

WHEREAS, Party A represents that it has the authority to enter into this Agreement;

WHEREAS, Party B accepts these terms and conditions;

NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree as follows:
{% endif %}

1. SCOPE OF AGREEMENT

{% if contract_type == "service" %}
Party A agrees to provide the following services to Party B:
{% for service in services %}
   - {{ service }}
{% endfor %}

1.1 SERVICE DELIVERABLES
The services shall include the following deliverables:
{% for deliverable in deliverables %}
   - {{ deliverable }}
{% endfor %}

1.2 TIMELINE
Party A shall complete services by {{ completion_date }}.

{% elif contract_type == "employment" %}
Party B hereby offers employment to Party A as {{ job_title }}.

1.1 POSITION DETAILS
- Title: {{ job_title }}
- Department: {{ department }}
- Location: {{ location }}
- Start Date: {{ start_date }}
- Reports To: {{ reports_to }}

1.2 COMPENSATION
Annual Salary: ${{ annual_salary }}
{% if include_bonus %}
Annual Bonus: {{ bonus_percentage }}% of annual salary
{% endif %}
{% if include_stock %}
Stock Options: {{ stock_options }} shares
{% endif %}

{% elif contract_type == "purchase" %}
Party A agrees to sell and Party B agrees to purchase the following:

Item Description: {{ item_description }}
Purchase Price: ${{ purchase_price }}
Payment Terms: {{ payment_terms }}

1.1 DELIVERY
Delivery shall occur on {{ delivery_date }} at {{ delivery_location }}.

1.2 CONDITION
Item is sold as-is / with warranties as follows:
{% if include_warranty %}
   - Material defects: {{ warranty_period }} year warranty
   - Workmanship: {{ warranty_period }} year warranty
{% endif %}

{% elif contract_type == "lease" %}
Party A (Landlord) leases to Party B (Tenant) the following property:

Property Address: {{ property_address }}
Lease Term: {{ lease_term }} months
Monthly Rent: ${{ monthly_rent }}
Security Deposit: ${{ security_deposit }}

1.1 RENT PAYMENT
Rent is due on {{ rent_due_day }} of each month.

1.2 LEASE RENEWAL
{% if auto_renew %}
This lease shall automatically renew for successive {{ renewal_term }}-month periods unless either party provides {{ termination_notice }} days notice.
{% else %}
This lease shall terminate on {{ lease_end_date }} unless renewed in writing by both parties.
{% endif %}

{% elif contract_type == "nda" %}
Party A discloses confidential information to Party B on a confidential basis.

1.1 DEFINITION
Confidential Information means all information disclosed by Party A to Party B, including:
{% for category in confidential_categories %}
   - {{ category }}
{% endfor %}

1.2 OBLIGATIONS
Party B agrees to:
   - Maintain strict confidentiality
   - Limit access to employees with need-to-know
   - Use only for permitted purposes
   - Return or destroy upon request

{% endif %}

2. PAYMENT AND FEES

{% if contract_type == "service" %}
2.1 FEES
   - Hourly Rate: ${{ hourly_rate }}/hour
   - Monthly Retainer: ${{ monthly_retainer }}
   - Payment Terms: Due within {{ payment_terms }} days of invoice

{% if include_expenses %}
2.2 EXPENSES
Party A may invoice for reasonable out-of-pocket expenses with supporting documentation.
{% endif %}

{% endif %}

3. TERM

{% if contract_type == "service" or contract_type == "employment" or contract_type == "nda" %}
This Agreement shall commence on {{ start_date }} and continue for {{ duration }} year(s).

{% if include_termination_for_cause %}
3.1 TERMINATION FOR CAUSE
Either party may terminate immediately upon material breach by the other party.
{% endif %}

{% if include_termination_convenience %}
3.2 TERMINATION FOR CONVENIENCE
Either party may terminate with {{ termination_notice }} days written notice.
{% endif %}

{% endif %}

4. CONFIDENTIALITY

{% if include_confidentiality %}
Both parties agree to maintain strict confidentiality of all proprietary information
of the other party for a period of {{ confidentiality_period }} years.

{% if include_non_compete %}
4.1 NON-COMPETE
Party A agrees not to compete with Party B's business for {{ non_compete_period }} years
within a {{ non_compete_radius }}-mile radius of Party B's principal place of business.
{% endif %}

{% if include_non_solicitation %}
4.2 NON-SOLICITATION
Party A agrees not to solicit Party B's employees or clients for {{ non_solicitation_period }} years.
{% endif %}

{% endif %}

5. LIABILITY AND INDEMNIFICATION

{% if include_liability_limitation %}
5.1 LIMITATION OF LIABILITY
Neither party shall be liable for indirect, incidental, or consequential damages.
Total liability is capped at {{ liability_cap }}.
{% endif %}

{% if include_indemnification %}
5.2 INDEMNIFICATION
Party A agrees to indemnify Party B against claims arising from Party A's breach.
{% endif %}

6. GOVERNING LAW

This Agreement shall be governed by the laws of {{ governing_state }}, without regard to conflict of laws.

{% if include_arbitration %}
6.1 ARBITRATION
Any disputes shall be resolved through binding arbitration in {{ arbitration_location }}.
{% endif %}

7. ENTIRE AGREEMENT

This Agreement constitutes the entire agreement between parties and supersedes all prior negotiations.

{% if include_amendment_clause %}
7.1 AMENDMENTS
This Agreement may be amended only in writing signed by both parties.
{% endif %}

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

PARTY A: ________________________     DATE: __________

PARTY B: ________________________     DATE: __________

"""

        template = Template(template_str)
        return template.render(**data)


def example_service_contract():
    """Generate conditional service contract."""
    context = {
        'contract_title': 'SERVICE AGREEMENT',
        'date': datetime.now().strftime('%B %d, %Y'),
        'contract_type': 'service',
        'party_a_type': 'corporation',
        'party_a_name': 'Professional Services Inc.',
        'party_b_type': 'llc',
        'party_b_name': 'TechCorp LLC',
        'include_recitals': True,
        'services': [
            'Legal consultation and advice',
            'Document drafting and review',
            'Litigation support',
            'Compliance consulting'
        ],
        'deliverables': [
            'Monthly legal memoranda',
            'Quarterly compliance reports',
            'Contract templates',
            'Policy recommendations'
        ],
        'completion_date': 'December 31, 2024',
        'hourly_rate': 250,
        'monthly_retainer': 5000,
        'payment_terms': 30,
        'include_expenses': True,
        'start_date': 'January 1, 2024',
        'duration': 1,
        'include_termination_for_cause': True,
        'include_termination_convenience': True,
        'termination_notice': 30,
        'include_confidentiality': True,
        'confidentiality_period': 3,
        'include_non_compete': True,
        'non_compete_period': 2,
        'non_compete_radius': 50,
        'include_non_solicitation': True,
        'non_solicitation_period': 1,
        'include_liability_limitation': True,
        'liability_cap': '$50,000',
        'include_indemnification': True,
        'governing_state': 'California',
        'include_arbitration': True,
        'arbitration_location': 'San Francisco, California',
        'include_amendment_clause': True
    }

    result = ConditionalDocumentGenerator.generate_contract(ContractType.SERVICE, context)
    with open('/tmp/conditional_service_contract.txt', 'w') as f:
        f.write(result)
    print("Service contract generated: /tmp/conditional_service_contract.txt")
    return result


def example_employment_contract():
    """Generate conditional employment contract."""
    context = {
        'contract_title': 'EMPLOYMENT AGREEMENT',
        'date': datetime.now().strftime('%B %d, %Y'),
        'contract_type': 'employment',
        'party_a_type': 'individual',
        'party_a_first_name': 'John',
        'party_a_last_name': 'Smith',
        'party_b_type': 'corporation',
        'party_b_name': 'GlobalTech Corporation',
        'include_recitals': True,
        'job_title': 'Senior Software Engineer',
        'department': 'Engineering',
        'location': 'San Francisco, CA',
        'start_date': 'January 15, 2024',
        'reports_to': 'Director of Engineering',
        'annual_salary': 180000,
        'include_bonus': True,
        'bonus_percentage': 20,
        'include_stock': True,
        'stock_options': 10000,
        'include_termination_for_cause': True,
        'include_termination_convenience': True,
        'termination_notice': 2,
        'include_confidentiality': True,
        'confidentiality_period': 3,
        'include_non_compete': True,
        'non_compete_period': 1,
        'non_compete_radius': 25,
        'include_non_solicitation': True,
        'non_solicitation_period': 1,
        'include_liability_limitation': False,
        'include_indemnification': False,
        'governing_state': 'California',
        'include_arbitration': False,
        'include_amendment_clause': True
    }

    result = ConditionalDocumentGenerator.generate_contract(ContractType.EMPLOYMENT, context)
    with open('/tmp/conditional_employment_contract.txt', 'w') as f:
        f.write(result)
    print("Employment contract generated: /tmp/conditional_employment_contract.txt")
    return result


def example_lease_contract():
    """Generate conditional lease contract."""
    context = {
        'contract_title': 'RESIDENTIAL LEASE AGREEMENT',
        'date': datetime.now().strftime('%B %d, %Y'),
        'contract_type': 'lease',
        'party_a_type': 'individual',
        'party_a_first_name': 'Margaret',
        'party_a_last_name': 'Johnson',
        'party_b_type': 'individual',
        'party_b_first_name': 'David',
        'party_b_last_name': 'Lee',
        'include_recitals': True,
        'property_address': '123 Main Street, Apartment 4B, San Francisco, CA 94102',
        'lease_term': 12,
        'monthly_rent': 2500,
        'security_deposit': 5000,
        'rent_due_day': 1,
        'auto_renew': True,
        'renewal_term': 12,
        'termination_notice': 60,
        'include_confidentiality': False,
        'include_liability_limitation': True,
        'liability_cap': '$10,000',
        'include_indemnification': True,
        'governing_state': 'California',
        'include_arbitration': False,
        'include_amendment_clause': True
    }

    result = ConditionalDocumentGenerator.generate_contract(ContractType.LEASE, context)
    with open('/tmp/conditional_lease_contract.txt', 'w') as f:
        f.write(result)
    print("Lease contract generated: /tmp/conditional_lease_contract.txt")
    return result


if __name__ == "__main__":
    example_service_contract()
    example_employment_contract()
    example_lease_contract()
    print("\nConditional contracts generated successfully!")

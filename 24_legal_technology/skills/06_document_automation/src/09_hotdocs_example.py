"""
HotDocs-Style Document Automation
Simulates HotDocs-style document assembly with variables, conditions, and repeats.

This demonstrates the concept of HotDocs, a professional legal document automation tool.
Note: This is a simplified implementation for educational purposes.

Dependencies: None (standard library)
Install: No additional dependencies required
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import re


class VariableType(Enum):
    """Types of variables in HotDocs."""
    TEXT = "text"
    DATE = "date"
    NUMBER = "number"
    CHECKBOX = "checkbox"
    MULTIPLE_CHOICE = "multiple_choice"
    REPEATED = "repeated"


@dataclass
class Variable:
    """Represents a HotDocs variable."""
    name: str
    var_type: VariableType
    prompt: str
    value: Any = None
    default: Any = None
    options: List[str] = None
    required: bool = True

    def get_value(self) -> Any:
        """Get variable value."""
        return self.value if self.value is not None else self.default


@dataclass
class ConditionalBlock:
    """Represents a conditional block in template."""
    condition: str
    true_content: str
    false_content: str = ""


class HotDocsTemplate:
    """Simulates HotDocs document automation."""

    def __init__(self, template_text: str):
        """Initialize template."""
        self.template_text = template_text
        self.variables: Dict[str, Variable] = {}
        self.repeating_sections: Dict[str, List[Dict[str, Any]]] = {}
        self._parse_template()

    def _parse_template(self) -> None:
        """Parse template for variables and conditionals."""
        # Extract variables: «variable_name»
        var_pattern = r'«(\w+)»'
        matches = re.findall(var_pattern, self.template_text)

        for match in set(matches):
            self.variables[match] = Variable(
                name=match,
                var_type=VariableType.TEXT,
                prompt=f"Enter {match}",
                value=None
            )

    def set_variable(self, name: str, value: Any) -> None:
        """Set variable value."""
        if name in self.variables:
            self.variables[name].value = value
        else:
            # Create new variable if it doesn't exist
            self.variables[name] = Variable(
                name=name,
                var_type=VariableType.TEXT,
                prompt=f"Enter {name}",
                value=value
            )

    def set_variables(self, data: Dict[str, Any]) -> None:
        """Set multiple variables at once."""
        for name, value in data.items():
            self.set_variable(name, value)

    def assemble(self) -> str:
        """Assemble document with variables."""
        result = self.template_text

        # Replace variables
        for var_name, variable in self.variables.items():
            placeholder = f"«{var_name}»"
            value = str(variable.get_value()) if variable.get_value() is not None else ""
            result = result.replace(placeholder, value)

        # Handle conditionals: [IF condition]content[END]
        result = self._process_conditionals(result)

        # Handle repeating sections: [REPEAT section_name]content[END REPEAT]
        result = self._process_repeating_sections(result)

        return result

    def _process_conditionals(self, text: str) -> str:
        """Process conditional blocks."""
        # Pattern: [IF var_name]content[ELSE]else_content[END]
        pattern = r'\[IF\s+(\w+)\](.*?)(?:\[ELSE\](.*?))?\[END\]'

        def replace_conditional(match):
            var_name = match.group(1)
            true_content = match.group(2)
            false_content = match.group(3) or ""

            if var_name in self.variables:
                value = self.variables[var_name].get_value()
                is_true = bool(value)
            else:
                is_true = False

            return true_content if is_true else false_content

        result = re.sub(pattern, replace_conditional, text, flags=re.DOTALL)
        return result

    def _process_repeating_sections(self, text: str) -> str:
        """Process repeating sections."""
        # Pattern: [REPEAT items_name]content[END REPEAT]
        pattern = r'\[REPEAT\s+(\w+)\](.*?)\[END\s+REPEAT\]'

        def replace_repeat(match):
            section_name = match.group(1)
            content = match.group(2)

            if section_name in self.repeating_sections:
                items = self.repeating_sections[section_name]
                output = ""

                for item_data in items:
                    item_content = content
                    # Replace variables in repeated section
                    for key, value in item_data.items():
                        placeholder = f"«{section_name}_{key}»"
                        item_content = item_content.replace(placeholder, str(value))
                    output += item_content

                return output

            return ""

        result = re.sub(pattern, replace_repeat, text, flags=re.DOTALL)
        return result

    def add_repeating_section(self, section_name: str, items: List[Dict[str, Any]]) -> None:
        """Add data for repeating section."""
        self.repeating_sections[section_name] = items

    def get_variable_prompts(self) -> List[tuple]:
        """Get list of variables that need values."""
        return [
            (var.name, var.prompt, var.var_type.value)
            for var in self.variables.values()
            if var.value is None
        ]


class ContractAssembler:
    """Assembles contracts using HotDocs-style templates."""

    # NDA Template
    NDA_TEMPLATE = """
NON-DISCLOSURE AGREEMENT

THIS AGREEMENT is made as of «agreement_date» between:

DISCLOSING PARTY: «disclosing_party_name»
Address: «disclosing_party_address»

RECEIVING PARTY: «receiving_party_name»
Address: «receiving_party_address»

1. DEFINITION OF CONFIDENTIAL INFORMATION

Confidential Information includes [IF include_trade_secrets]trade secrets, [END]technical data,
business information, [IF include_financial_data]financial information, [END]and other proprietary data.

2. OBLIGATIONS

The Receiving Party agrees to:
- Maintain strict confidentiality
- Limit access to employees with need-to-know basis
- Use Confidential Information only for «permitted_purpose»
[IF include_return_clause]- Return or destroy Confidential Information upon request[END]

3. TERM

This Agreement shall remain in effect for «confidentiality_period» years from the date of disclosure.

[IF include_governing_law]
4. GOVERNING LAW

This Agreement shall be governed by the laws of «governing_jurisdiction».
[END]

5. EXECUTION

Disclosing Party: _______________________________
                  «disclosing_party_name»

Receiving Party: _______________________________
                 «receiving_party_name»

Date: _______________________________
"""

    # Service Agreement Template
    SERVICE_AGREEMENT_TEMPLATE = """
SERVICE AGREEMENT

This Agreement is made as of «date» between:

SERVICE PROVIDER: «provider_name»
Address: «provider_address»

CLIENT: «client_name»
Address: «client_address»

1. SERVICES

Provider shall provide the following services:
[REPEAT services]- «services_description»
[END REPEAT]

2. FEES AND PAYMENT

[IF hourly_billing]
Hourly Rate: $«hourly_rate»/hour
[END]

[IF retainer_billing]
Monthly Retainer: $«monthly_retainer»
[END]

Payment Terms: Net «payment_terms» days from invoice date

3. TERM

This Agreement shall commence on «start_date» and continue for «contract_duration» year(s).

[IF auto_renewal]
This Agreement shall automatically renew for successive «renewal_period»-month periods
unless either party provides «termination_notice» days notice.
[END]

[IF include_non_compete]
4. NON-COMPETE

Provider agrees not to compete for «non_compete_period» years within «non_compete_radius» miles.
[END]

5. CONFIDENTIALITY

Both parties agree to maintain confidentiality of proprietary information.

IN WITNESS WHEREOF:

Provider: _______________________________
          «provider_name»

Client: _______________________________
        «client_name»

Date: _______________________________
"""

    @staticmethod
    def create_nda(data: Dict[str, Any]) -> str:
        """Create NDA from template."""
        template = HotDocsTemplate(ContractAssembler.NDA_TEMPLATE)
        template.set_variables(data)
        return template.assemble()

    @staticmethod
    def create_service_agreement(data: Dict[str, Any], services: List[Dict[str, str]]) -> str:
        """Create service agreement from template."""
        template = HotDocsTemplate(ContractAssembler.SERVICE_AGREEMENT_TEMPLATE)
        template.set_variables(data)
        template.add_repeating_section('services', services)
        return template.assemble()


def example_nda_assembly():
    """Example: Assemble NDA using HotDocs template."""

    nda_data = {
        'agreement_date': 'January 15, 2024',
        'disclosing_party_name': 'TechStartup Inc.',
        'disclosing_party_address': '123 Innovation Dr, San Francisco, CA',
        'receiving_party_name': 'Potential Investor LLC',
        'receiving_party_address': '456 Capital Ave, New York, NY',
        'include_trade_secrets': True,
        'include_financial_data': True,
        'permitted_purpose': 'Evaluating business opportunity',
        'include_return_clause': True,
        'confidentiality_period': 3,
        'include_governing_law': True,
        'governing_jurisdiction': 'California'
    }

    nda = ContractAssembler.create_nda(nda_data)

    with open('/tmp/hotdocs_nda.txt', 'w') as f:
        f.write(nda)

    print("NDA Generated:\n")
    print(nda)
    return nda


def example_service_agreement_assembly():
    """Example: Assemble service agreement with repeating sections."""

    services = [
        {'description': 'Legal consultation and advice'},
        {'description': 'Document drafting and review'},
        {'description': 'Compliance consulting'},
        {'description': 'Litigation support'}
    ]

    data = {
        'date': 'January 15, 2024',
        'provider_name': 'Legal Solutions LLC',
        'provider_address': '789 Law St, San Francisco, CA',
        'client_name': 'Acme Corporation',
        'client_address': '999 Business Ave, San Jose, CA',
        'hourly_billing': True,
        'hourly_rate': 250,
        'retainer_billing': True,
        'monthly_retainer': 5000,
        'payment_terms': 30,
        'start_date': 'February 1, 2024',
        'contract_duration': 1,
        'auto_renewal': True,
        'renewal_period': 12,
        'termination_notice': 30,
        'include_non_compete': True,
        'non_compete_period': 2,
        'non_compete_radius': 50
    }

    agreement = ContractAssembler.create_service_agreement(data, services)

    with open('/tmp/hotdocs_service_agreement.txt', 'w') as f:
        f.write(agreement)

    print("\n\nService Agreement Generated:\n")
    print(agreement)
    return agreement


if __name__ == "__main__":
    example_nda_assembly()
    example_service_agreement_assembly()
    print("\nHotDocs-style assembly examples completed!")

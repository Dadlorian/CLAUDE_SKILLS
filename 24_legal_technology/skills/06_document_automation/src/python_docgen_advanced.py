#!/usr/bin/env python3
"""
Advanced document generation with conditional logic and dynamic sections
"""

from docx import Document
from docx.oxml import OxmlElement
from docx.shared import Pt, RGBColor
from enum import Enum

class ClientType(Enum):
    INDIVIDUAL = 1
    CORPORATION = 2
    PARTNERSHIP = 3

class AdvancedDocumentGenerator:
    def __init__(self, template_path):
        self.template = Document(template_path)
    
    def remove_paragraph(self, paragraph):
        """Remove a paragraph from document."""
        p = paragraph._element
        p.getparent().remove(p)
    
    def remove_table(self, table):
        """Remove a table from document."""
        tbl = table._element
        tbl.getparent().remove(tbl)
    
    def add_paragraph_with_formatting(self, text, bold=False, italic=False, size=11):
        """Add formatted paragraph."""
        p = self.template.add_paragraph(text)
        for run in p.runs:
            run.font.bold = bold
            run.font.italic = italic
            run.font.size = Pt(size)
        return p
    
    def handle_conditional_sections(self, client_type):
        """Include/exclude sections based on client type."""
        for i, paragraph in enumerate(self.template.paragraphs):
            # Mark paragraphs with [[IF_INDIVIDUAL]] and [[ENDIF]] markers
            if '[[IF_CORPORATION]]' in paragraph.text:
                if client_type != ClientType.CORPORATION:
                    # Remove section
                    pass
    
    def populate_corporate_info(self, corp_data):
        """Populate corporation-specific information."""
        replacements = {
            '{CORPORATE_NAME}': corp_data.get('name', ''),
            '{STATE_OF_INCORPORATION}': corp_data.get('state', ''),
            '{REGISTERED_AGENT}': corp_data.get('agent', ''),
            '{PRINCIPAL_ADDRESS}': corp_data.get('address', ''),
        }
        return replacements
    
    def populate_individual_info(self, individual_data):
        """Populate individual-specific information."""
        replacements = {
            '{INDIVIDUAL_NAME}': individual_data.get('name', ''),
            '{DATE_OF_BIRTH}': individual_data.get('dob', ''),
            '{RESIDENCE_ADDRESS}': individual_data.get('address', ''),
        }
        return replacements
    
    def generate(self, client_type, client_data, output_path):
        """Generate document based on client type."""
        if client_type == ClientType.CORPORATION:
            replacements = self.populate_corporate_info(client_data)
        else:
            replacements = self.populate_individual_info(client_data)
        
        self._replace_in_document(replacements)
        self.template.save(output_path)
        return output_path
    
    def _replace_in_document(self, replacements):
        """Replace text throughout document."""
        for paragraph in self.template.paragraphs:
            for key, value in replacements.items():
                if key in paragraph.text:
                    paragraph.text = paragraph.text.replace(key, value)


# Example usage
if __name__ == '__main__':
    corp_data = {
        'name': 'Acme Corporation',
        'state': 'Delaware',
        'agent': 'Jane Smith',
        'address': '456 Corporate Ave, New York, NY'
    }
    
    generator = AdvancedDocumentGenerator('templates/operating_agreement.docx')
    output = generator.generate(ClientType.CORPORATION, corp_data, 'output/operating_agreement.docx')
    print(f"Generated: {output}")

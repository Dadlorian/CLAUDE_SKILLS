#!/usr/bin/env python3
"""
Fill PDF forms with data
Programmatically populate AcroForm fields in PDF documents
"""

import subprocess
from pypdf import PdfReader, PdfWriter
import pdfrw
from typing import Dict

class PDFFormFiller:
    def __init__(self, pdf_template_path):
        self.pdf_template_path = pdf_template_path
    
    def get_form_fields(self):
        """List all form fields in PDF."""
        reader = PdfReader(self.pdf_template_path)
        fields = reader.get_fields()
        return fields if fields else {}
    
    def fill_form_pdfrw(self, data: Dict, output_path: str):
        """Fill form using pdfrw library."""
        template = pdfrw.PdfReader(self.pdf_template_path)
        
        for field in pdfrw.get_object_from_stream(template.Root.AcroForm):
            if field['T']:
                field_name = field['T'][1:-1]  # Remove parentheses
                if field_name in data:
                    field.V = f'({data[field_name]})'
        
        pdfrw.PdfWriter().write(output_path, template)
        return output_path
    
    def fill_form_with_fdf(self, data: Dict, output_path: str):
        """Fill PDF using FDF (Forms Data Format)."""
        # Create FDF file
        fdf_content = "%FDF-1.2\n"
        fdf_content += "1 0 obj\n"
        fdf_content += "<< /FDF << /Fields [\n"
        
        for field_name, value in data.items():
            fdf_content += f'<< /T ({field_name}) /V ({value}) >>\n'
        
        fdf_content += "] >> >>\nendobj\n"
        fdf_content += "trailer\n"
        fdf_content += "<< /Root 1 0 R >>\n"
        fdf_content += "%%EOF\n"
        
        # Save FDF
        fdf_path = output_path.replace('.pdf', '.fdf')
        with open(fdf_path, 'w') as f:
            f.write(fdf_content)
        
        # Use pdftk or similar tool to fill PDF
        # This is a command-line approach
        cmd = [
            'pdftk',
            self.pdf_template_path,
            'fill_form',
            fdf_path,
            'output',
            output_path,
            'flatten'
        ]
        
        try:
            subprocess.run(cmd, check=True)
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"Error filling form: {e}")
            return None
    
    def fill_checkbox_fields(self, checkboxes: Dict[str, bool], output_path: str):
        """Fill checkbox fields (checked/unchecked)."""
        template = pdfrw.PdfReader(self.pdf_template_path)
        
        for field in pdfrw.get_object_from_stream(template.Root.AcroForm):
            if field['T']:
                field_name = field['T'][1:-1]
                if field_name in checkboxes:
                    # For checkboxes, set appearance state
                    if checkboxes[field_name]:
                        field.V = '/Yes'
                        field.AS = '/Yes'
                    else:
                        field.V = '/Off'
                        field.AS = '/Off'
        
        pdfrw.PdfWriter().write(output_path, template)
        return output_path
    
    def fill_dropdown_fields(self, dropdowns: Dict, output_path: str):
        """Fill dropdown/select fields."""
        template = pdfrw.PdfReader(self.pdf_template_path)
        
        for field in pdfrw.get_object_from_stream(template.Root.AcroForm):
            if field['T']:
                field_name = field['T'][1:-1]
                if field_name in dropdowns:
                    field.V = f'({dropdowns[field_name]})'
        
        pdfrw.PdfWriter().write(output_path, template)
        return output_path


# Example usage
if __name__ == '__main__':
    filler = PDFFormFiller('templates/court_filing_form.pdf')
    
    # Get available fields
    fields = filler.get_form_fields()
    print("Available form fields:")
    for field_name in fields:
        print(f"  - {field_name}")
    
    # Fill form with data
    form_data = {
        'case_number': '2024-CV-12345',
        'plaintiff': 'John Smith',
        'defendant': 'Jane Doe',
        'court': 'District Court',
        'filing_date': '01/15/2024',
    }
    
    checkbox_data = {
        'expedited_hearing': True,
        'jury_trial': False,
        'confidentiality_order': True,
    }
    
    output = filler.fill_form_pdfrw(form_data, 'output/filled_form.pdf')
    print(f"Form filled: {output}")

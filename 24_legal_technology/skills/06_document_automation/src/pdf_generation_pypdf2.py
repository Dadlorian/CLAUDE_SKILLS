#!/usr/bin/env python3
"""
PDF generation and manipulation using PyPDF2
Merge, split, and annotate PDF documents
"""

from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

class PDFManipulator:
    @staticmethod
    def merge_pdfs(pdf_list, output_path):
        """Merge multiple PDF files into one."""
        merger = PdfMerger()
        try:
            for pdf in pdf_list:
                merger.append(pdf)
            merger.write(output_path)
            merger.close()
            return output_path
        except Exception as e:
            print(f"Error merging PDFs: {e}")
            return None
    
    @staticmethod
    def split_pdf(input_pdf, start_page, end_page, output_path):
        """Extract pages from PDF."""
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        
        for page_num in range(start_page - 1, end_page):
            if page_num < len(reader.pages):
                writer.add_page(reader.pages[page_num])
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    
    @staticmethod
    def add_watermark(input_pdf, watermark_text, output_path):
        """Add watermark to PDF."""
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        
        # Create watermark
        watermark_buffer = io.BytesIO()
        c = canvas.Canvas(watermark_buffer, pagesize=letter)
        c.setFont("Helvetica", 60)
        c.setFillAlpha(0.3)
        c.rotate(45)
        c.drawString(200, 100, watermark_text)
        c.save()
        
        watermark_buffer.seek(0)
        watermark = PdfReader(watermark_buffer)
        watermark_page = watermark.pages[0]
        
        # Apply watermark to all pages
        for page in reader.pages:
            page.merge_page(watermark_page)
            writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    
    @staticmethod
    def add_page_numbers(input_pdf, output_path):
        """Add page numbers to PDF."""
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        
        for page_num, page in enumerate(reader.pages, 1):
            # Create page number canvas
            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=letter)
            c.setFont("Helvetica", 10)
            c.drawString(550, 20, f"Page {page_num}")
            c.save()
            
            packet.seek(0)
            page_number = PdfReader(packet)
            page.merge_page(page_number.pages[0])
            writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    
    @staticmethod
    def extract_text(input_pdf):
        """Extract text content from PDF."""
        reader = PdfReader(input_pdf)
        text = ""
        
        for page in reader.pages:
            text += page.extract_text()
        
        return text


# Example usage
if __name__ == '__main__':
    # Merge multiple documents
    pdf_files = [
        'documents/cover_page.pdf',
        'documents/engagement_letter.pdf',
        'documents/scope_of_work.pdf',
    ]
    
    manipulator = PDFManipulator()
    
    # Merge
    merged = manipulator.merge_pdfs(pdf_files, 'output/merged_document.pdf')
    print(f"Merged PDF: {merged}")
    
    # Add watermark
    watermarked = manipulator.add_watermark(
        merged, 
        'CONFIDENTIAL', 
        'output/confidential_document.pdf'
    )
    print(f"Watermarked: {watermarked}")
    
    # Add page numbers
    final = manipulator.add_page_numbers(
        watermarked,
        'output/final_document.pdf'
    )
    print(f"Final document: {final}")

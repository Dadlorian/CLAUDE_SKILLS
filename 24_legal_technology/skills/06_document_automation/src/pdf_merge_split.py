#!/usr/bin/env python3
"""
PDF merging and splitting operations
Combine or separate PDF documents for document assembly
"""

from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from pathlib import Path
from typing import List

class PDFProcessor:
    @staticmethod
    def merge_sequential(pdf_list: List[str], output_path: str, keep_bookmarks=True):
        """Merge PDFs in order, optionally preserving bookmarks."""
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
    def merge_with_covers(documents: dict, output_path: str):
        """
        Merge documents with cover pages.
        documents: {'cover.pdf': 'main.pdf', ...}
        """
        merger = PdfMerger()
        
        for cover, main in documents.items():
            merger.append(cover)
            merger.append(main)
        
        merger.write(output_path)
        merger.close()
        return output_path
    
    @staticmethod
    def split_by_ranges(pdf_path: str, ranges: List[tuple], output_dir: str):
        """Split PDF into multiple files based on page ranges."""
        reader = PdfReader(pdf_path)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        results = []
        for i, (start, end) in enumerate(ranges):
            writer = PdfWriter()
            
            for page_num in range(start - 1, min(end, len(reader.pages))):
                writer.add_page(reader.pages[page_num])
            
            output_file = Path(output_dir) / f"split_{i+1}.pdf"
            with open(output_file, 'wb') as f:
                writer.write(f)
            
            results.append(str(output_file))
        
        return results
    
    @staticmethod
    def split_by_count(pdf_path: str, pages_per_file: int, output_dir: str):
        """Split PDF into files with specified number of pages each."""
        reader = PdfReader(pdf_path)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        total_pages = len(reader.pages)
        results = []
        
        for i in range(0, total_pages, pages_per_file):
            writer = PdfWriter()
            
            for j in range(i, min(i + pages_per_file, total_pages)):
                writer.add_page(reader.pages[j])
            
            output_file = Path(output_dir) / f"split_{i//pages_per_file + 1}.pdf"
            with open(output_file, 'wb') as f:
                writer.write(f)
            
            results.append(str(output_file))
        
        return results
    
    @staticmethod
    def extract_even_odd(pdf_path: str, output_dir: str):
        """Extract even and odd pages separately."""
        reader = PdfReader(pdf_path)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        even_writer = PdfWriter()
        odd_writer = PdfWriter()
        
        for i, page in enumerate(reader.pages):
            if i % 2 == 0:
                even_writer.add_page(page)
            else:
                odd_writer.add_page(page)
        
        even_path = Path(output_dir) / "even_pages.pdf"
        odd_path = Path(output_dir) / "odd_pages.pdf"
        
        with open(even_path, 'wb') as f:
            even_writer.write(f)
        
        with open(odd_path, 'wb') as f:
            odd_writer.write(f)
        
        return {
            'even': str(even_path),
            'odd': str(odd_path),
        }
    
    @staticmethod
    def get_page_count(pdf_path: str):
        """Get total page count."""
        reader = PdfReader(pdf_path)
        return len(reader.pages)


# Example usage
if __name__ == '__main__':
    processor = PDFProcessor()
    
    # Merge documents
    documents_to_merge = [
        'cover_page.pdf',
        'main_document.pdf',
        'exhibits.pdf',
    ]
    
    merged = processor.merge_sequential(
        documents_to_merge,
        'output/complete_filing.pdf'
    )
    print(f"Merged document: {merged}")
    
    # Split by page ranges
    ranges = [(1, 10), (11, 20), (21, 30)]
    split_files = processor.split_by_ranges(merged, ranges, 'output/split')
    print(f"Split files: {split_files}")
    
    # Get page count
    page_count = processor.get_page_count(merged)
    print(f"Total pages: {page_count}")
    
    # Extract even/odd pages
    even_odd = processor.extract_even_odd(merged, 'output/even_odd')
    print(f"Even/Odd split: {even_odd}")

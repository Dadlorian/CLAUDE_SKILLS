"""
Load File Generation Example
Demonstrates creating industry-standard load files for document production
"""

from typing import List, Dict, Optional
import csv
import json
from datetime import datetime

class LoadFileGenerator:
    """Generates load files for e-discovery production"""

    def __init__(self, load_file_type: str = "fcp"):
        """
        Initialize load file generator

        Args:
            load_file_type: Type of load file (fcp, lfap, dat, csv)
        """
        self.load_file_type = load_file_type
        self.documents = []
        self.field_mapping = {}

    def set_field_mapping(self, mapping: Dict[str, str]) -> None:
        """
        Set mapping between document fields and load file fields

        Args:
            mapping: Dict mapping document field names to load file field names
        """
        self.field_mapping = mapping

    def add_document(self, document: Dict) -> None:
        """
        Add document to load file

        Args:
            document: Document data dictionary
        """
        self.documents.append(document)

    def generate_csv_load_file(self, output_path: str,
                              delimiter: str = ',') -> bool:
        """
        Generate CSV load file

        Args:
            output_path: Output file path
            delimiter: Field delimiter (comma or tab)

        Returns:
            True if successful
        """
        if not self.documents:
            return False

        try:
            # Get all unique fields
            all_fields = set()
            for doc in self.documents:
                all_fields.update(doc.keys())

            fieldnames = sorted(list(all_fields))

            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(self.documents)

            return True
        except IOError as e:
            print(f"Error writing load file: {e}")
            return False

    def generate_dat_load_file(self, output_path: str,
                              image_field: str = "ImageFileName",
                              native_field: str = "NativeFileName") -> bool:
        """
        Generate DAT format load file (Relativity format)

        Args:
            output_path: Output file path
            image_field: Field name for image files
            native_field: Field name for native files

        Returns:
            True if successful
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Write header
                headers = self._get_dat_headers()
                f.write('\t'.join(headers) + '\n')

                # Write document lines
                for doc in self.documents:
                    line = self._format_dat_line(doc, headers)
                    f.write(line + '\n')

            return True
        except IOError as e:
            print(f"Error writing DAT file: {e}")
            return False

    def generate_fcp_load_file(self, output_path: str) -> bool:
        """
        Generate FCP format load file (Relativity native)

        Args:
            output_path: Output file path

        Returns:
            True if successful
        """
        try:
            # FCP is tab-delimited with specific structure
            with open(output_path, 'w', encoding='utf-8') as f:
                # Write metadata header
                f.write("***LOAD FILE OPTIONS***\n")
                f.write(f"LOAD FILE TYPE:FCP\n")
                f.write(f"FILE PATH:.\n")
                f.write(f"IMAGE PATH:.\n")
                f.write(f"PRODUCTION DATE:{datetime.now().isoformat()}\n")
                f.write("***FIELDS***\n")

                # Write field definitions
                headers = self._get_fcp_headers()
                for header in headers:
                    f.write(f"{header}\t")
                f.write("\n")

                # Write document data
                for doc in self.documents:
                    values = []
                    for header in headers:
                        value = doc.get(header, "")
                        # Escape quotes and handle special characters
                        value = str(value).replace('"', '""')
                        values.append(f'"{value}"')
                    f.write('\t'.join(values) + '\n')

            return True
        except IOError as e:
            print(f"Error writing FCP file: {e}")
            return False

    def generate_json_load_file(self, output_path: str) -> bool:
        """
        Generate JSON format load file

        Args:
            output_path: Output file path

        Returns:
            True if successful
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, indent=2, default=str)
            return True
        except IOError as e:
            print(f"Error writing JSON file: {e}")
            return False

    @staticmethod
    def _get_dat_headers() -> List[str]:
        """Get standard DAT file headers"""
        return [
            "DocumentID",
            "Begdoc",
            "Enddoc",
            "Pages",
            "Author",
            "Subject",
            "DateCreated",
            "DateModified",
            "Custodian",
            "Filetype",
            "FileSize",
            "ImageFileName",
            "NativeFileName",
            "TextFileName",
            "Privilege",
            "Responsive"
        ]

    @staticmethod
    def _get_fcp_headers() -> List[str]:
        """Get standard FCP file headers"""
        return [
            "DocumentID",
            "Begdoc",
            "Enddoc",
            "Pages",
            "Author",
            "Subject",
            "DateCreated",
            "DateModified",
            "Custodian",
            "FileType",
            "FileSize",
            "ImageFileName",
            "NativeFileName",
            "TextFileName",
            "Privilege",
            "Responsive",
            "Issues"
        ]

    @staticmethod
    def _format_dat_line(document: Dict, headers: List[str]) -> str:
        """Format a single document line for DAT file"""
        values = []
        for header in headers:
            value = document.get(header, "")
            # Escape special characters
            value = str(value).replace('"', '""')
            if ',' in value or '\t' in value:
                value = f'"{value}"'
            values.append(value)
        return '\t'.join(values)


class BatesNumberAssigner:
    """Assigns and manages Bates numbers for production"""

    def __init__(self, prefix: str, start_number: int = 1):
        """
        Initialize Bates number assigner

        Args:
            prefix: Prefix for Bates numbers (e.g., "ACME")
            start_number: Starting number
        """
        self.prefix = prefix
        self.current_number = start_number
        self.bates_map = {}
        self.bates_assignments = []

    def assign_bates_numbers(self, documents: List[Dict],
                            pad_width: int = 6) -> Dict[int, str]:
        """
        Assign sequential Bates numbers to documents

        Args:
            documents: List of documents
            pad_width: Padding width for numbers

        Returns:
            Dict mapping document_id to Bates number
        """
        bates_assignments = {}

        for doc in documents:
            doc_id = doc.get('document_id') or doc.get('id')
            pages = doc.get('pages', 1)

            # Assign Bates range for multi-page documents
            bates_start = f"{self.prefix}-{str(self.current_number).zfill(pad_width)}"

            if pages > 1:
                bates_end = f"{self.prefix}-{str(self.current_number + pages - 1).zfill(pad_width)}"
                bates_range = f"{bates_start}:{bates_end}"
            else:
                bates_range = bates_start

            bates_assignments[doc_id] = bates_range

            self.bates_map[doc_id] = {
                "bates_start": self.current_number,
                "bates_end": self.current_number + pages - 1,
                "pages": pages,
                "bates_range": bates_range
            }

            self.current_number += pages

            self.bates_assignments.append({
                "document_id": doc_id,
                "bates_range": bates_range,
                "pages": pages
            })

        return bates_assignments

    def get_bates_number(self, document_id) -> Optional[str]:
        """
        Get Bates number for specific document

        Args:
            document_id: Document ID

        Returns:
            Bates number string or None
        """
        return self.bates_map.get(document_id, {}).get('bates_range')

    def get_bates_certificate(self) -> str:
        """
        Generate certification of Bates numbering

        Returns:
            Certification text
        """
        total_pages = max(
            (item['bates_end'] for item in self.bates_map.values()),
            default=0
        )

        certification = f"""
CERTIFICATION OF BATES NUMBERING

This document production contains {len(self.bates_map)} documents numbered
from {self.prefix}-000001 through {self.prefix}-{str(total_pages).zfill(6)}.

The Bates numbers are sequential and consecutive with no gaps.

All documents have been assigned Bates numbers prior to production.

Generated: {datetime.now().isoformat()}
"""
        return certification


class LoadFileValidator:
    """Validates load files for correctness"""

    @staticmethod
    def validate_required_fields(documents: List[Dict],
                                required_fields: List[str]) -> List[Dict]:
        """
        Validate that required fields are populated

        Args:
            documents: List of documents
            required_fields: Required field names

        Returns:
            List of validation errors
        """
        errors = []

        for doc in documents:
            doc_id = doc.get('document_id') or doc.get('id')

            for field in required_fields:
                if field not in doc or not doc[field]:
                    errors.append({
                        "document_id": doc_id,
                        "error_type": "missing_required_field",
                        "field": field
                    })

        return errors

    @staticmethod
    def validate_bates_continuity(bates_assignments: List[Dict]) -> List[str]:
        """
        Validate Bates numbering is continuous

        Args:
            bates_assignments: List of Bates assignments

        Returns:
            List of continuity errors
        """
        errors = []

        # Extract all Bates ranges
        ranges = []
        for assignment in bates_assignments:
            bates_range = assignment.get('bates_range')
            if ':' in bates_range:
                start, end = bates_range.split(':')
                start_num = int(start.split('-')[1])
                end_num = int(end.split('-')[1])
            else:
                start_num = int(bates_range.split('-')[1])
                end_num = start_num

            ranges.append((start_num, end_num))

        # Sort and check for gaps
        sorted_ranges = sorted(ranges)
        previous_end = 0

        for start, end in sorted_ranges:
            if start != previous_end + 1:
                errors.append(f"Gap in Bates numbering between {previous_end} and {start}")
            previous_end = end

        return errors


# Example usage
if __name__ == "__main__":
    # Sample documents
    documents = [
        {
            "DocumentID": 1,
            "Author": "john@company.com",
            "Subject": "Q3 Budget",
            "DateCreated": "2024-01-15",
            "Custodian": "john@company.com",
            "FileType": "Email",
            "Pages": 1
        },
        {
            "DocumentID": 2,
            "Author": "manager@company.com",
            "Subject": "Q4 Planning",
            "DateCreated": "2024-01-16",
            "Custodian": "manager@company.com",
            "FileType": "Document",
            "Pages": 5
        }
    ]

    # Generate load file
    generator = LoadFileGenerator()
    for doc in documents:
        generator.add_document(doc)

    generator.generate_csv_load_file("/tmp/production.csv")

    # Assign Bates numbers
    assigner = BatesNumberAssigner(prefix="ACME")
    bates_nums = assigner.assign_bates_numbers(documents)

    print("Bates Assignments:")
    for doc_id, bates in bates_nums.items():
        print(f"  Document {doc_id}: {bates}")

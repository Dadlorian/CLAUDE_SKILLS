"""
Load File Processing Example
Demonstrates parsing and manipulating load files
"""

from typing import List, Dict, Iterator
import csv
import json

class LoadFileParser:
    """Parses various load file formats"""

    @staticmethod
    def parse_csv_load_file(file_path: str,
                           delimiter: str = ',',
                           encoding: str = 'utf-8') -> List[Dict]:
        """
        Parse CSV format load file

        Args:
            file_path: Path to CSV load file
            delimiter: Field delimiter
            encoding: File encoding

        Returns:
            List of document records
        """
        documents = []

        try:
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                for row in reader:
                    # Clean up empty fields
                    cleaned_row = {k: v for k, v in row.items() if v}
                    documents.append(cleaned_row)
        except IOError as e:
            print(f"Error reading load file: {e}")

        return documents

    @staticmethod
    def parse_dat_load_file(file_path: str) -> List[Dict]:
        """
        Parse DAT format load file

        Args:
            file_path: Path to DAT load file

        Returns:
            List of document records
        """
        documents = []
        headers = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # First line contains headers
                headers = f.readline().strip().split('\t')

                # Subsequent lines contain data
                for line in f:
                    values = line.strip().split('\t')
                    if len(values) == len(headers):
                        doc = dict(zip(headers, values))
                        documents.append(doc)
        except IOError as e:
            print(f"Error reading DAT file: {e}")

        return documents

    @staticmethod
    def parse_json_load_file(file_path: str) -> List[Dict]:
        """
        Parse JSON format load file

        Args:
            file_path: Path to JSON load file

        Returns:
            List of document records
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading JSON file: {e}")
            return []

    @staticmethod
    def parse_fcp_load_file(file_path: str) -> List[Dict]:
        """
        Parse FCP format load file

        Args:
            file_path: Path to FCP load file

        Returns:
            List of document records
        """
        documents = []
        headers = []
        in_data_section = False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.rstrip('\n')

                    # Skip metadata section
                    if line.startswith("***"):
                        if "FIELDS" in line:
                            in_data_section = True
                        continue

                    # Parse headers
                    if in_data_section and not headers:
                        headers = [h.strip() for h in line.split('\t') if h.strip()]
                        continue

                    # Parse data
                    if in_data_section and headers:
                        values = [v.strip('"') for v in line.split('\t')]
                        if len(values) >= len(headers):
                            doc = dict(zip(headers, values[:len(headers)]))
                            documents.append(doc)
        except IOError as e:
            print(f"Error reading FCP file: {e}")

        return documents


class LoadFileProcessor:
    """Processes and manipulates load file data"""

    def __init__(self, documents: List[Dict]):
        """
        Initialize processor

        Args:
            documents: List of document records from load file
        """
        self.documents = documents
        self.original_count = len(documents)

    def filter_by_field_value(self, field: str, value: str) -> List[Dict]:
        """
        Filter documents by field value

        Args:
            field: Field name
            value: Field value to match

        Returns:
            Filtered documents
        """
        return [doc for doc in self.documents if doc.get(field) == value]

    def filter_by_field_values(self, field: str, values: List[str]) -> List[Dict]:
        """
        Filter documents by multiple field values

        Args:
            field: Field name
            values: List of values to match

        Returns:
            Filtered documents
        """
        return [doc for doc in self.documents if doc.get(field) in values]

    def filter_by_custodian(self, custodians: List[str]) -> List[Dict]:
        """
        Filter documents by custodian

        Args:
            custodians: List of custodian names

        Returns:
            Documents from specified custodians
        """
        return self.filter_by_field_values('Custodian', custodians)

    def filter_by_privilege(self) -> List[Dict]:
        """
        Filter privileged documents

        Returns:
            Documents marked as privileged
        """
        return [doc for doc in self.documents
                if doc.get('Privilege') and doc.get('Privilege').lower() != 'no']

    def filter_by_responsiveness(self, responsive: bool = True) -> List[Dict]:
        """
        Filter by responsiveness status

        Args:
            responsive: True for responsive, False for non-responsive

        Returns:
            Filtered documents
        """
        responsive_str = 'Responsive' if responsive else 'Non-Responsive'
        return [doc for doc in self.documents
                if doc.get('Responsive') == responsive_str]

    def add_field(self, field_name: str, default_value: str = "") -> None:
        """
        Add new field to all documents

        Args:
            field_name: Name of new field
            default_value: Default value for field
        """
        for doc in self.documents:
            if field_name not in doc:
                doc[field_name] = default_value

    def update_field(self, field_name: str, field_value: str,
                    where_field: str = None,
                    where_value: str = None) -> int:
        """
        Update field values for matching documents

        Args:
            field_name: Field to update
            field_value: New value
            where_field: Optional filter field
            where_value: Optional filter value

        Returns:
            Number of documents updated
        """
        count = 0

        for doc in self.documents:
            if where_field and where_value:
                if doc.get(where_field) == where_value:
                    doc[field_name] = field_value
                    count += 1
            else:
                doc[field_name] = field_value
                count += 1

        return count

    def get_field_statistics(self, field_name: str) -> Dict:
        """
        Get statistics about field values

        Args:
            field_name: Field to analyze

        Returns:
            Statistics dictionary
        """
        values = {}
        total = 0

        for doc in self.documents:
            value = doc.get(field_name, 'Unknown')
            values[value] = values.get(value, 0) + 1
            total += 1

        # Calculate percentages
        value_stats = {}
        for value, count in values.items():
            value_stats[value] = {
                "count": count,
                "percentage": round(count / total * 100, 1)
            }

        return {
            "field": field_name,
            "total_documents": total,
            "unique_values": len(values),
            "value_distribution": value_stats
        }

    def dedup_documents(self, dedup_field: str = 'SHA256') -> Dict:
        """
        Identify duplicate documents

        Args:
            dedup_field: Field containing hash values

        Returns:
            Dedup statistics and groups
        """
        hash_groups = {}
        duplicate_count = 0

        for doc in self.documents:
            hash_val = doc.get(dedup_field)
            if hash_val:
                if hash_val not in hash_groups:
                    hash_groups[hash_val] = []
                hash_groups[hash_val].append(doc.get('DocumentID'))

        # Find duplicates
        duplicates = {h: docs for h, docs in hash_groups.items() if len(docs) > 1}
        duplicate_count = sum(len(docs) - 1 for docs in duplicates.values())

        return {
            "total_documents": len(self.documents),
            "unique_documents": len(hash_groups),
            "duplicate_groups": len(duplicates),
            "total_duplicate_instances": duplicate_count,
            "deduplication_rate": round(duplicate_count / len(self.documents) * 100, 1)
        }

    def export_filtered(self, output_path: str, documents: List[Dict],
                       format: str = 'csv') -> bool:
        """
        Export filtered document set

        Args:
            output_path: Output file path
            documents: Documents to export
            format: Export format (csv, json)

        Returns:
            True if successful
        """
        try:
            if format == 'csv':
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    if documents:
                        writer = csv.DictWriter(f, fieldnames=documents[0].keys())
                        writer.writeheader()
                        writer.writerows(documents)
            elif format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(documents, f, indent=2)

            return True
        except IOError as e:
            print(f"Error exporting: {e}")
            return False


class LoadFileReporter:
    """Generates reports from load file data"""

    @staticmethod
    def generate_summary_report(documents: List[Dict]) -> Dict:
        """
        Generate summary report of load file

        Args:
            documents: List of documents

        Returns:
            Summary report
        """
        if not documents:
            return {}

        # Count by field values
        custodians = set()
        responsive_count = 0
        privileged_count = 0
        file_types = {}

        for doc in documents:
            if doc.get('Custodian'):
                custodians.add(doc['Custodian'])

            if doc.get('Responsive') == 'Responsive':
                responsive_count += 1

            if doc.get('Privilege') and doc.get('Privilege').lower() != 'no':
                privileged_count += 1

            file_type = doc.get('FileType', 'Unknown')
            file_types[file_type] = file_types.get(file_type, 0) + 1

        return {
            "total_documents": len(documents),
            "unique_custodians": len(custodians),
            "responsive_documents": responsive_count,
            "privileged_documents": privileged_count,
            "file_type_distribution": file_types,
            "responsive_percentage": round(responsive_count / len(documents) * 100, 1)
        }


# Example usage
if __name__ == "__main__":
    # Sample load file data
    documents = [
        {
            "DocumentID": "001",
            "Author": "john@company.com",
            "Custodian": "john@company.com",
            "Responsive": "Responsive",
            "Privilege": "No"
        },
        {
            "DocumentID": "002",
            "Author": "lawyer@company.com",
            "Custodian": "manager@company.com",
            "Responsive": "Non-Responsive",
            "Privilege": "Attorney-Client Privilege"
        }
    ]

    processor = LoadFileProcessor(documents)

    # Get statistics
    privilege_stats = processor.get_field_statistics('Privilege')
    print(f"Privilege Statistics: {privilege_stats}")

    # Filter privileged
    privileged = processor.filter_by_privilege()
    print(f"Privileged Documents: {len(privileged)}")

    # Generate report
    report = LoadFileReporter.generate_summary_report(documents)
    print(f"Summary: {report}")

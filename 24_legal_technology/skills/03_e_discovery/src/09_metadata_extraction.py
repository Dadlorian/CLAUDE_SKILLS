"""
Metadata Extraction Example
Demonstrates extracting and normalizing document metadata
"""

from typing import Dict, List, Optional
from datetime import datetime
import re
import hashlib
from pathlib import Path

class MetadataExtractor:
    """Extracts metadata from various document types"""

    @staticmethod
    def extract_email_metadata(email: Dict) -> Dict:
        """
        Extract standardized metadata from email

        Args:
            email: Email data dictionary

        Returns:
            Standardized metadata
        """
        return {
            "document_type": "Email",
            "message_id": email.get('message_id'),
            "date_created": email.get('date'),
            "date_modified": email.get('date'),  # Emails not typically modified
            "from": email.get('from'),
            "to": email.get('to', []),
            "cc": email.get('cc', []),
            "bcc": email.get('bcc', []),
            "subject": email.get('subject'),
            "body": email.get('body'),
            "has_attachments": email.get('has_attachments', False),
            "size_bytes": len(email.get('body', '').encode()),
            "custodian": MetadataExtractor._extract_custodian(email.get('from', '')),
            "participants": MetadataExtractor._get_all_participants(email),
            "sensitivity": email.get('sensitivity', 'Normal'),
            "importance": email.get('importance', 'Normal')
        }

    @staticmethod
    def extract_file_metadata(file_path: str) -> Dict:
        """
        Extract metadata from file system

        Args:
            file_path: Path to file

        Returns:
            File metadata
        """
        path = Path(file_path)

        return {
            "document_type": "File",
            "file_name": path.name,
            "file_extension": path.suffix,
            "file_path": str(path.absolute()),
            "size_bytes": path.stat().st_size if path.exists() else 0,
            "date_created": datetime.fromtimestamp(path.stat().st_ctime).isoformat()
            if path.exists() else None,
            "date_modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            if path.exists() else None,
            "date_accessed": datetime.fromtimestamp(path.stat().st_atime).isoformat()
            if path.exists() else None,
            "is_directory": path.is_dir()
        }

    @staticmethod
    def extract_office_document_metadata(doc: Dict) -> Dict:
        """
        Extract metadata from Office documents (Word, Excel, PowerPoint)

        Args:
            doc: Document data

        Returns:
            Office document metadata
        """
        return {
            "document_type": doc.get('file_type', 'Office Document'),
            "title": doc.get('title'),
            "subject": doc.get('subject'),
            "author": doc.get('author'),
            "last_modified_by": doc.get('last_modified_by'),
            "created_date": doc.get('created_date'),
            "modified_date": doc.get('modified_date'),
            "company": doc.get('company'),
            "keywords": doc.get('keywords', []),
            "comments": doc.get('comments'),
            "revision_number": doc.get('revision_number'),
            "total_edit_time": doc.get('total_edit_time')
        }

    @staticmethod
    def normalize_date(date_string: Optional[str]) -> Optional[str]:
        """
        Normalize date string to ISO format

        Args:
            date_string: Date in various formats

        Returns:
            Normalized ISO format date or None
        """
        if not date_string:
            return None

        # Try common formats
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y-%m-%dT%H:%M:%S",
            "%m/%d/%Y %H:%M:%S"
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(str(date_string), fmt)
                return parsed.isoformat()
            except ValueError:
                continue

        return None

    @staticmethod
    def calculate_hash(content: str, algorithm: str = 'sha256') -> str:
        """
        Calculate hash of document content

        Args:
            content: Document content
            algorithm: Hash algorithm (md5, sha1, sha256)

        Returns:
            Hash string
        """
        if algorithm == 'md5':
            return hashlib.md5(content.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(content.encode()).hexdigest()
        else:  # sha256
            return hashlib.sha256(content.encode()).hexdigest()

    @staticmethod
    def _extract_custodian(email_from: str) -> str:
        """Extract custodian name from email address"""
        # Extract email address
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', str(email_from))
        return email_match.group(0) if email_match else email_from

    @staticmethod
    def _get_all_participants(email: Dict) -> List[str]:
        """Get all participants in email"""
        participants = set()
        participants.add(email.get('from', ''))
        participants.update(email.get('to', []))
        participants.update(email.get('cc', []))
        participants.update(email.get('bcc', []))
        return list(filter(None, participants))


class MetadataNormalizer:
    """Normalizes and standardizes metadata"""

    @staticmethod
    def normalize_metadata(metadata: Dict) -> Dict:
        """
        Normalize metadata for production

        Args:
            metadata: Raw metadata

        Returns:
            Normalized metadata
        """
        normalized = {
            "document_id": metadata.get('document_id'),
            "document_type": metadata.get('document_type', 'Unknown'),
            "title": metadata.get('title') or metadata.get('subject') or
            metadata.get('file_name', 'Untitled'),
            "date_created": MetadataNormalizer._normalize_date(
                metadata.get('date_created') or metadata.get('created_date')
            ),
            "date_modified": MetadataNormalizer._normalize_date(
                metadata.get('date_modified') or metadata.get('modified_date')
            ),
            "author": metadata.get('author') or metadata.get('from'),
            "custodian": metadata.get('custodian'),
            "size_bytes": metadata.get('size_bytes', 0),
            "participants": metadata.get('participants') or
            metadata.get('to', []),
            "hash_value": metadata.get('hash_value'),
            "is_duplicate": False,
            "is_privileged": False,
            "is_responsive": None
        }

        return normalized

    @staticmethod
    def _normalize_date(date_val: Optional[str]) -> Optional[str]:
        """Normalize date to ISO format"""
        if isinstance(date_val, str):
            return MetadataExtractor.normalize_date(date_val)
        return date_val

    @staticmethod
    def identify_duplicates(metadata_list: List[Dict]) -> Dict[str, List]:
        """
        Identify duplicate documents by hash

        Args:
            metadata_list: List of metadata dicts with hash values

        Returns:
            Dict mapping hash to list of document IDs
        """
        hash_groups = {}

        for metadata in metadata_list:
            hash_val = metadata.get('hash_value')
            doc_id = metadata.get('document_id')

            if hash_val and doc_id:
                if hash_val not in hash_groups:
                    hash_groups[hash_val] = []
                hash_groups[hash_val].append(doc_id)

        # Return only hashes with duplicates
        duplicates = {h: docs for h, docs in hash_groups.items()
                     if len(docs) > 1}

        return duplicates

    @staticmethod
    def generate_metadata_report(metadata_list: List[Dict]) -> Dict:
        """
        Generate summary report of metadata

        Args:
            metadata_list: List of normalized metadata

        Returns:
            Summary statistics
        """
        if not metadata_list:
            return {}

        doc_types = {}
        custodians = set()
        date_range = {
            "earliest": None,
            "latest": None
        }

        for metadata in metadata_list:
            # Count by type
            doc_type = metadata.get('document_type', 'Unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

            # Track custodians
            if metadata.get('custodian'):
                custodians.add(metadata['custodian'])

            # Track date range
            date_created = metadata.get('date_created')
            if date_created:
                if not date_range["earliest"] or date_created < date_range["earliest"]:
                    date_range["earliest"] = date_created
                if not date_range["latest"] or date_created > date_range["latest"]:
                    date_range["latest"] = date_created

        total_size = sum(m.get('size_bytes', 0) for m in metadata_list)

        return {
            "total_documents": len(metadata_list),
            "document_types": doc_types,
            "total_custodians": len(custodians),
            "total_size_bytes": total_size,
            "average_doc_size": total_size / len(metadata_list) if metadata_list else 0,
            "date_range": date_range,
            "unique_authors": len(set(m.get('author') for m in metadata_list if m.get('author')))
        }


# Example usage
if __name__ == "__main__":
    # Sample email
    email = {
        "from": "john.doe@company.com",
        "to": ["manager@company.com"],
        "cc": ["legal@company.com"],
        "subject": "Q3 Budget Review",
        "body": "Please review the attached Q3 budget proposal.",
        "date": "2024-01-15T10:30:00",
        "has_attachments": True
    }

    extractor = MetadataExtractor()
    metadata = extractor.extract_email_metadata(email)

    normalizer = MetadataNormalizer()
    normalized = normalizer.normalize_metadata(metadata)

    print("Extracted Metadata:")
    print(f"  From: {normalized['author']}")
    print(f"  To: {normalized['participants']}")
    print(f"  Date: {normalized['date_created']}")

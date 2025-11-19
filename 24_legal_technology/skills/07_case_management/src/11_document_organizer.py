"""
Document Organizer - Practice Management Automation

Organizes case documents automatically by type, date, and matter.
Maintains folder structure and generates index files for quick retrieval.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pathlib import Path
import json


class DocumentType(Enum):
    """Document classification for legal matters"""
    PLEADING = "pleading"
    MOTION = "motion"
    DISCOVERY = "discovery"
    CORRESPONDENCE = "correspondence"
    EVIDENCE = "evidence"
    CONTRACT = "contract"
    COURT_ORDER = "court_order"
    MEMO = "memo"
    OTHER = "other"


@dataclass
class Document:
    """Represents a legal document with metadata"""
    name: str
    doc_type: DocumentType
    matter_id: str
    date_filed: datetime
    file_path: str
    tags: List[str] = None
    attorney: str = ""
    description: str = ""

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.doc_type.value,
            "matter_id": self.matter_id,
            "date_filed": self.date_filed.isoformat(),
            "file_path": self.file_path,
            "tags": self.tags or [],
            "attorney": self.attorney,
            "description": self.description
        }


class DocumentOrganizer:
    """Organizes legal documents by matter, type, and date"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.documents: List[Document] = []
        self.index_file = self.root_path / "document_index.json"

    def add_document(self, document: Document) -> None:
        """Add a document to the organizer"""
        self.documents.append(document)
        self._organize_file(document)

    def _organize_file(self, document: Document) -> None:
        """Organize document into matter and type directories"""
        # Create directory structure: matter_id/document_type/
        matter_dir = self.root_path / document.matter_id / document.doc_type.value
        matter_dir.mkdir(parents=True, exist_ok=True)

        # Rename file with date prefix for chronological sorting
        date_prefix = document.date_filed.strftime("%Y%m%d")
        new_filename = f"{date_prefix}_{document.name}"
        new_path = matter_dir / new_filename

        # Update document path
        document.file_path = str(new_path)

    def get_documents_by_matter(self, matter_id: str) -> List[Document]:
        """Retrieve all documents for a specific matter"""
        return [d for d in self.documents if d.matter_id == matter_id]

    def get_documents_by_type(self, doc_type: DocumentType) -> List[Document]:
        """Retrieve all documents of a specific type"""
        return [d for d in self.documents if d.doc_type == doc_type]

    def get_documents_by_date_range(self, start: datetime, end: datetime) -> List[Document]:
        """Retrieve documents filed within a date range"""
        return [d for d in self.documents if start <= d.date_filed <= end]

    def search_documents(self, query: str) -> List[Document]:
        """Search documents by name, tags, or description"""
        results = []
        query_lower = query.lower()

        for doc in self.documents:
            if (query_lower in doc.name.lower() or
                query_lower in doc.description.lower() or
                any(query_lower in tag.lower() for tag in (doc.tags or []))):
                results.append(doc)

        return results

    def generate_matter_index(self, matter_id: str) -> dict:
        """Generate an index for all documents in a matter"""
        matter_docs = self.get_documents_by_matter(matter_id)

        index = {
            "matter_id": matter_id,
            "generated_at": datetime.now().isoformat(),
            "total_documents": len(matter_docs),
            "documents_by_type": {},
            "chronological_list": []
        }

        # Group by type
        for doc_type in DocumentType:
            docs = [d for d in matter_docs if d.doc_type == doc_type]
            if docs:
                index["documents_by_type"][doc_type.value] = len(docs)

        # Chronological list
        sorted_docs = sorted(matter_docs, key=lambda d: d.date_filed)
        index["chronological_list"] = [d.to_dict() for d in sorted_docs]

        return index

    def export_index(self) -> None:
        """Export complete document index to JSON"""
        index = {
            "total_documents": len(self.documents),
            "generated_at": datetime.now().isoformat(),
            "documents": [d.to_dict() for d in sorted(
                self.documents, key=lambda x: x.date_filed
            )]
        }

        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)


# Example usage
if __name__ == "__main__":
    organizer = DocumentOrganizer("/home/legal/documents")

    doc1 = Document(
        name="complaint.pdf",
        doc_type=DocumentType.PLEADING,
        matter_id="MAT-2024-001",
        date_filed=datetime(2024, 1, 15),
        file_path="/uploads/complaint.pdf",
        attorney="John Smith",
        tags=["initial_filing", "plaintiff"],
        description="Initial complaint filed against defendant"
    )

    organizer.add_document(doc1)
    organizer.export_index()
    print(f"Document organized: {doc1.file_path}")

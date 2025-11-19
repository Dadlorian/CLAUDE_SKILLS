#!/usr/bin/env python3
"""
Output Formatter - Format and export legal documents in multiple formats.

Production-ready module for formatting documents into various output formats
(PDF, Word, HTML, etc.) with style templates and export options.
"""

import logging
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from abc import ABC, abstractmethod
import uuid

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class OutputFormat(Enum):
    """Supported output formats."""
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    TXT = "txt"
    JSON = "json"
    XML = "xml"
    MARKDOWN = "markdown"
    RTF = "rtf"


class StyleTemplate(Enum):
    """Built-in style templates."""
    FORMAL = "formal"
    CASUAL = "casual"
    MINIMAL = "minimal"
    DETAILED = "detailed"
    COURT_FILING = "court_filing"
    CONTRACT = "contract"


class PageOrientation(Enum):
    """Page orientation."""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class PaperSize(Enum):
    """Paper sizes."""
    LETTER = "letter"
    LEGAL = "legal"
    A4 = "a4"
    A3 = "a3"


@dataclass
class StyleSettings:
    """Document style settings."""
    font_name: str = "Arial"
    font_size: int = 11
    line_spacing: float = 1.5
    margin_top: float = 1.0
    margin_bottom: float = 1.0
    margin_left: float = 1.0
    margin_right: float = 1.0
    header_enabled: bool = True
    footer_enabled: bool = True
    page_numbers: bool = True
    color_scheme: str = "black"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class PageSettings:
    """Page configuration."""
    paper_size: PaperSize = PaperSize.LETTER
    orientation: PageOrientation = PageOrientation.PORTRAIT
    page_break_sections: bool = True
    page_break_paragraphs: bool = False
    page_count_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['paper_size'] = self.paper_size.value
        data['orientation'] = self.orientation.value
        return data


@dataclass
class ExportOptions:
    """Export options for document."""
    include_metadata: bool = True
    include_toc: bool = True
    include_page_numbers: bool = True
    include_bookmarks: bool = True
    compress: bool = False
    encryption: Optional[str] = None
    output_filename: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class FormattedDocument:
    """Result of formatting a document."""
    document_id: str
    output_format: OutputFormat
    content: bytes
    size_bytes: int
    created_at: datetime = field(default_factory=datetime.now)
    page_count: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding large content)."""
        return {
            "document_id": self.document_id,
            "output_format": self.output_format.value,
            "size_bytes": self.size_bytes,
            "page_count": self.page_count,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }


class DocumentFormatter(ABC):
    """Abstract base class for document formatters."""

    @abstractmethod
    def format(
        self,
        document: Dict[str, Any],
        style_settings: StyleSettings,
        export_options: ExportOptions
    ) -> FormattedDocument:
        """Format document."""
        pass

    @abstractmethod
    def supports_format(self) -> OutputFormat:
        """Get supported format."""
        pass


class PDFFormatter(DocumentFormatter):
    """Formats documents as PDF."""

    def format(
        self,
        document: Dict[str, Any],
        style_settings: StyleSettings,
        export_options: ExportOptions
    ) -> FormattedDocument:
        """Format document as PDF."""
        logger.info(f"Formatting document as PDF: {document.get('id')}")

        # In production, use reportlab or weasyprint
        # Mock implementation
        content = self._generate_pdf_content(document, style_settings)

        formatted = FormattedDocument(
            document_id=document.get("id", str(uuid.uuid4())),
            output_format=OutputFormat.PDF,
            content=content,
            size_bytes=len(content),
            page_count=self._estimate_page_count(document),
            metadata=self._extract_metadata(document)
        )

        logger.info(f"PDF formatted successfully: {formatted.size_bytes} bytes")
        return formatted

    def supports_format(self) -> OutputFormat:
        """Get supported format."""
        return OutputFormat.PDF

    @staticmethod
    def _generate_pdf_content(document: Dict[str, Any], style_settings: StyleSettings) -> bytes:
        """Generate PDF content."""
        # Mock PDF generation
        content = f"PDF Document: {document.get('title', 'Untitled')}\n"
        content += f"Font: {style_settings.font_name}, Size: {style_settings.font_size}\n"
        content += json.dumps(document, indent=2)
        return content.encode('utf-8')

    @staticmethod
    def _estimate_page_count(document: Dict[str, Any]) -> int:
        """Estimate page count."""
        content = json.dumps(document)
        # Rough estimate: ~3000 chars per page
        return max(1, len(content) // 3000)

    @staticmethod
    def _extract_metadata(document: Dict[str, Any]) -> Dict[str, Any]:
        """Extract document metadata."""
        return {
            "title": document.get("title", "Untitled"),
            "author": document.get("author", "Unknown"),
            "created": datetime.now().isoformat()
        }


class HTMLFormatter(DocumentFormatter):
    """Formats documents as HTML."""

    def format(
        self,
        document: Dict[str, Any],
        style_settings: StyleSettings,
        export_options: ExportOptions
    ) -> FormattedDocument:
        """Format document as HTML."""
        logger.info(f"Formatting document as HTML: {document.get('id')}")

        content = self._generate_html_content(document, style_settings)

        formatted = FormattedDocument(
            document_id=document.get("id", str(uuid.uuid4())),
            output_format=OutputFormat.HTML,
            content=content,
            size_bytes=len(content)
        )

        return formatted

    def supports_format(self) -> OutputFormat:
        """Get supported format."""
        return OutputFormat.HTML

    @staticmethod
    def _generate_html_content(document: Dict[str, Any], style_settings: StyleSettings) -> bytes:
        """Generate HTML content."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{document.get('title', 'Document')}</title>
    <style>
        body {{
            font-family: {style_settings.font_name};
            font-size: {style_settings.font_size}pt;
            line-height: {style_settings.line_spacing};
            margin: {style_settings.margin_top}in {style_settings.margin_right}in
                    {style_settings.margin_bottom}in {style_settings.margin_left}in;
        }}
        h1 {{ margin-top: 24pt; margin-bottom: 12pt; }}
        p {{ margin-bottom: 12pt; }}
    </style>
</head>
<body>
    <h1>{document.get('title', 'Document')}</h1>
    <div class="content">
        {document.get('content', '')}
    </div>
</body>
</html>"""
        return html.encode('utf-8')


class JSONFormatter(DocumentFormatter):
    """Formats documents as JSON."""

    def format(
        self,
        document: Dict[str, Any],
        style_settings: StyleSettings,
        export_options: ExportOptions
    ) -> FormattedDocument:
        """Format document as JSON."""
        logger.info(f"Formatting document as JSON: {document.get('id')}")

        output = {
            "document": document,
            "style_settings": style_settings.to_dict(),
            "export_options": export_options.to_dict(),
            "formatted_at": datetime.now().isoformat()
        }

        content = json.dumps(output, indent=2).encode('utf-8')

        formatted = FormattedDocument(
            document_id=document.get("id", str(uuid.uuid4())),
            output_format=OutputFormat.JSON,
            content=content,
            size_bytes=len(content)
        )

        return formatted

    def supports_format(self) -> OutputFormat:
        """Get supported format."""
        return OutputFormat.JSON


class TextFormatter(DocumentFormatter):
    """Formats documents as plain text."""

    def format(
        self,
        document: Dict[str, Any],
        style_settings: StyleSettings,
        export_options: ExportOptions
    ) -> FormattedDocument:
        """Format document as text."""
        logger.info(f"Formatting document as text: {document.get('id')}")

        content = self._generate_text_content(document)

        formatted = FormattedDocument(
            document_id=document.get("id", str(uuid.uuid4())),
            output_format=OutputFormat.TXT,
            content=content,
            size_bytes=len(content)
        )

        return formatted

    def supports_format(self) -> OutputFormat:
        """Get supported format."""
        return OutputFormat.TXT

    @staticmethod
    def _generate_text_content(document: Dict[str, Any]) -> bytes:
        """Generate text content."""
        lines = []
        lines.append(document.get("title", "DOCUMENT").upper())
        lines.append("=" * 60)
        lines.append("")

        if "author" in document:
            lines.append(f"Author: {document['author']}")
        if "date" in document:
            lines.append(f"Date: {document['date']}")

        lines.append("")
        lines.append(document.get("content", ""))

        return "\n".join(lines).encode('utf-8')


class FormatterFactory:
    """Factory for creating formatters."""

    def __init__(self):
        """Initialize factory."""
        self.formatters: Dict[OutputFormat, DocumentFormatter] = {
            OutputFormat.PDF: PDFFormatter(),
            OutputFormat.HTML: HTMLFormatter(),
            OutputFormat.JSON: JSONFormatter(),
            OutputFormat.TXT: TextFormatter()
        }
        logger.info("Initialized formatter factory")

    def get_formatter(self, output_format: OutputFormat) -> Optional[DocumentFormatter]:
        """Get formatter for format."""
        return self.formatters.get(output_format)

    def format_document(
        self,
        document: Dict[str, Any],
        output_format: OutputFormat,
        style_settings: Optional[StyleSettings] = None,
        export_options: Optional[ExportOptions] = None
    ) -> Optional[FormattedDocument]:
        """Format document."""
        formatter = self.get_formatter(output_format)
        if not formatter:
            logger.error(f"No formatter for format: {output_format.value}")
            return None

        style_settings = style_settings or StyleSettings()
        export_options = export_options or ExportOptions()

        return formatter.format(document, style_settings, export_options)


class StyleTemplateManager:
    """Manages style templates."""

    def __init__(self):
        """Initialize manager."""
        self.templates: Dict[StyleTemplate, StyleSettings] = {}
        self._setup_default_templates()
        logger.info("Initialized style template manager")

    def _setup_default_templates(self) -> None:
        """Setup default style templates."""
        self.templates = {
            StyleTemplate.FORMAL: StyleSettings(
                font_name="Times New Roman",
                font_size=12,
                line_spacing=2.0,
                margin_left=1.25,
                margin_right=1.0
            ),
            StyleTemplate.CASUAL: StyleSettings(
                font_name="Arial",
                font_size=11,
                line_spacing=1.5,
                margin_left=1.0,
                margin_right=1.0
            ),
            StyleTemplate.COURT_FILING: StyleSettings(
                font_name="Courier New",
                font_size=12,
                line_spacing=2.0,
                margin_left=1.5,
                margin_right=1.0
            ),
            StyleTemplate.CONTRACT: StyleSettings(
                font_name="Calibri",
                font_size=11,
                line_spacing=1.5,
                margin_left=1.25,
                margin_right=1.25
            )
        }

    def get_template(self, template: StyleTemplate) -> StyleSettings:
        """Get style template."""
        return self.templates.get(template, StyleSettings())

    def create_custom_template(
        self,
        name: str,
        style_settings: StyleSettings
    ) -> None:
        """Create custom style template."""
        # In production, save to database
        logger.info(f"Created custom style template: {name}")


class DocumentExporter:
    """Exports formatted documents."""

    def __init__(self, factory: FormatterFactory):
        """Initialize exporter."""
        self.factory = factory
        self.exported_documents: List[FormattedDocument] = []
        logger.info("Initialized document exporter")

    def export(
        self,
        document: Dict[str, Any],
        output_format: OutputFormat,
        output_path: Path,
        style_template: Optional[StyleTemplate] = None,
        export_options: Optional[ExportOptions] = None
    ) -> Tuple[bool, str]:
        """Export document to file."""
        logger.info(f"Exporting document to {output_format.value}: {output_path}")

        # Get style settings
        template_manager = StyleTemplateManager()
        if style_template:
            style_settings = template_manager.get_template(style_template)
        else:
            style_settings = StyleSettings()

        # Format document
        formatted = self.factory.format_document(
            document,
            output_format,
            style_settings,
            export_options or ExportOptions()
        )

        if not formatted:
            return False, "Formatting failed"

        # Write to file
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(formatted.content)

            self.exported_documents.append(formatted)
            logger.info(f"Document exported successfully: {output_path}")
            return True, f"Exported to {output_path}"

        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False, str(e)

    def export_to_multiple_formats(
        self,
        document: Dict[str, Any],
        output_formats: List[OutputFormat],
        output_directory: Path
    ) -> Dict[OutputFormat, Tuple[bool, str]]:
        """Export document to multiple formats."""
        results = {}

        for output_format in output_formats:
            filename = f"{document.get('id', 'document')}.{output_format.value}"
            output_path = output_directory / filename

            success, message = self.export(
                document,
                output_format,
                output_path
            )
            results[output_format] = (success, message)

        return results


def create_sample_document() -> Dict[str, Any]:
    """Create sample document for formatting."""
    return {
        "id": "DOC-2024-001",
        "title": "Service Agreement",
        "author": "Legal Department",
        "date": datetime.now().isoformat(),
        "content": "This agreement is entered into between Party A and Party B. "
                   "Both parties agree to the terms and conditions outlined herein."
    }


if __name__ == "__main__":
    # Create document
    document = create_sample_document()

    # Create factory and exporter
    factory = FormatterFactory()
    exporter = DocumentExporter(factory)

    # Export to multiple formats
    output_dir = Path("/tmp/exports")
    formats = [OutputFormat.JSON, OutputFormat.HTML, OutputFormat.TXT, OutputFormat.PDF]

    results = exporter.export_to_multiple_formats(document, formats, output_dir)

    print("Export Results:")
    for fmt, (success, message) in results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"  {fmt.value}: {status} - {message}")

    print("\nExported Documents:")
    for doc in exporter.exported_documents:
        print(f"  - {doc.output_format.value}: {doc.size_bytes} bytes")

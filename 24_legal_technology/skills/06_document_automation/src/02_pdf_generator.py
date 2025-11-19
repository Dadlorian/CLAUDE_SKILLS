"""
PDF Document Generator
Generates PDF documents for legal contracts, reports, and compliance documents.

Dependencies: reportlab, PyPDF2
Install: pip install reportlab PyPDF2
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime
from typing import List, Tuple
import io


class PDFGenerator:
    """Generate professional PDF documents for legal purposes."""

    def __init__(self, filename: str, title: str = "Legal Document"):
        """Initialize PDF document."""
        self.filename = filename
        self.title = title
        self.elements = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#003366'),
            spaceAfter=30,
            alignment=1  # CENTER
        ))

        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            spaceAfter=12,
            spaceBefore=12
        ))

        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leading=13
        ))

    def add_title(self, title: str):
        """Add document title."""
        self.elements.append(Paragraph(title, self.styles['CustomTitle']))
        self.elements.append(Spacer(1, 0.3 * inch))

    def add_heading(self, text: str):
        """Add section heading."""
        self.elements.append(Paragraph(text, self.styles['CustomHeading']))

    def add_paragraph(self, text: str):
        """Add paragraph of text."""
        self.elements.append(Paragraph(text, self.styles['CustomBody']))
        self.elements.append(Spacer(1, 0.1 * inch))

    def add_numbered_list(self, items: List[str]):
        """Add numbered list."""
        for i, item in enumerate(items, 1):
            self.add_paragraph(f"<b>{i}.</b> {item}")

    def add_table_data(self, data: List[List[str]], widths: List[float] = None):
        """Add table to document."""
        if widths is None:
            widths = [2 * inch] * len(data[0]) if data else []

        table = Table(data, colWidths=widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        self.elements.append(table)
        self.elements.append(Spacer(1, 0.2 * inch))

    def add_signature_block(self, party_name: str):
        """Add signature block."""
        self.elements.append(Spacer(1, 0.3 * inch))
        self.add_paragraph(f"<u>{party_name}:</u>")
        self.add_paragraph("_" * 40)
        self.add_paragraph("Signature")
        self.add_paragraph("")
        self.add_paragraph("_" * 40)
        self.add_paragraph("Date")

    def add_page_break(self):
        """Add page break."""
        self.elements.append(PageBreak())

    def generate(self):
        """Generate PDF document."""
        doc = SimpleDocTemplate(
            self.filename,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )

        doc.build(self.elements)
        print(f"PDF generated: {self.filename}")


def example_legal_notice():
    """Generate example legal notice PDF."""
    pdf = PDFGenerator("/tmp/legal_notice.pdf", "LEGAL NOTICE")

    pdf.add_title("CEASE AND DESIST LETTER")
    pdf.add_paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}")
    pdf.add_paragraph("")

    pdf.add_heading("TO WHOM IT MAY CONCERN:")
    pdf.add_paragraph(
        "This letter serves as formal notice to cease and desist from the unauthorized use, "
        "reproduction, or distribution of our copyrighted materials. "
    )

    pdf.add_heading("FACTUAL BACKGROUND")
    background_points = [
        "Our company owns exclusive copyrights to certain intellectual property",
        "You are currently using said property without authorization",
        "Such use violates federal copyright law",
        "We have not granted permission for your use"
    ]
    pdf.add_numbered_list(background_points)

    pdf.add_heading("DEMANDS")
    demands = [
        "Immediately cease all unauthorized use",
        "Remove all infringing content within 48 hours",
        "Provide written confirmation of compliance",
        "Reimburse damages for unauthorized use"
    ]
    pdf.add_numbered_list(demands)

    pdf.add_heading("LEGAL BASIS")
    pdf.add_paragraph(
        "Your actions constitute copyright infringement under 17 U.S.C. § 101 et seq. "
        "If you fail to comply, we will pursue all available legal remedies."
    )

    pdf.add_signature_block("Legal Counsel")

    pdf.generate()


def example_compliance_report():
    """Generate example compliance report PDF."""
    pdf = PDFGenerator("/tmp/compliance_report.pdf", "COMPLIANCE REPORT")

    pdf.add_title("ANNUAL COMPLIANCE REPORT")
    pdf.add_paragraph(f"<b>Reporting Period:</b> January 1 - December 31, 2024")
    pdf.add_paragraph(f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y')}")

    pdf.add_heading("EXECUTIVE SUMMARY")
    pdf.add_paragraph(
        "This report details the company's compliance status across all regulatory frameworks. "
        "Overall compliance rating: 98% with zero critical violations."
    )

    pdf.add_heading("COMPLIANCE METRICS")
    table_data = [
        ["Framework", "Status", "Score", "Notes"],
        ["GDPR", "Compliant", "100%", "All requirements met"],
        ["HIPAA", "Compliant", "97%", "Minor documentation gap"],
        ["SOC2", "Compliant", "95%", "Remediation in progress"],
        ["CCPA", "Compliant", "99%", "Full implementation complete"]
    ]
    pdf.add_table_data(table_data, [1.5 * inch, 1 * inch, 1 * inch, 2 * inch])

    pdf.add_heading("KEY FINDINGS")
    findings = [
        "All data protection policies updated and enforced",
        "Employee training completed with 100% participation",
        "Third-party vendor audits completed successfully",
        "Security incidents: 0 (zero) in reporting period"
    ]
    pdf.add_numbered_list(findings)

    pdf.add_heading("RECOMMENDATIONS")
    pdf.add_paragraph(
        "Continue quarterly audits and maintain current security protocols. "
        "Minor documentation improvements recommended for HIPAA."
    )

    pdf.generate()


if __name__ == "__main__":
    example_legal_notice()
    example_compliance_report()
    print("\nPDF examples generated successfully!")

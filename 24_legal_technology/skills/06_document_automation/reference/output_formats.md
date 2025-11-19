# Document Output Formats

## Overview

Document automation systems must generate output in various formats to meet different use cases, platforms, and user needs. Understanding the strengths, limitations, and best practices for each format is essential for effective automation.

## Microsoft Word (DOCX)

### Overview
- **Format**: Office Open XML (.docx)
- **Use Case**: Editable documents, further customization, track changes
- **Strengths**: Full editability, rich formatting, widely compatible
- **Limitations**: File size, potential formatting inconsistencies

### Best Practices

**Styles and Formatting**:
```
Use Word styles, not direct formatting:
- Heading 1, Heading 2, Heading 3
- Body Text, Body Text Indent
- List Paragraph
- Quote, Caption

Benefits:
- Consistent appearance
- Easy global updates
- Accessibility
- Table of contents generation
```

**Document Properties**:
```xml
<dc:title>Stock Purchase Agreement</dc:title>
<dc:creator>Law Firm Name</dc:creator>
<dc:subject>M&A Transaction</dc:subject>
<cp:keywords>stock purchase, acquisition, merger</cp:keywords>
<dcterms:created>2025-11-19T10:00:00Z</dcterms:created>
```

**Headers and Footers**:
```
Header:
  [Company Logo]  |  [Document Title]

Footer:
  Page [Page Number] of [Total Pages]
  [Document ID]: [Auto-generated ID]
  Generated: [Date and Time]
```

**Tables**:
```
- Use table styles for consistency
- Set column widths explicitly
- Use header rows
- Enable "repeat header rows" for multi-page tables
- Avoid merged cells when possible
```

**Lists and Numbering**:
```
- Use built-in list styles
- Define multi-level lists for legal numbering
- Example: 1., 1.1, 1.1.1, (a), (i)
- Avoid manual numbering
```

### Generation Techniques

**Using python-docx**:
```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

doc = Document()

# Add title
title = doc.add_heading('Stock Purchase Agreement', 0)
title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

# Add paragraph with formatting
p = doc.add_paragraph()
p.add_run('AGREEMENT').bold = True
p.add_run(' dated ').bold = False
p.add_run(effective_date).italic = True

# Add table
table = doc.add_table(rows=1, cols=3)
table.style = 'Light Grid Accent 1'
hdr_cells = table.rows[0].cells
hdr_cells[0].text = 'Name'
hdr_cells[1].text = 'Shares'
hdr_cells[2].text = 'Percentage'

for shareholder in shareholders:
    row_cells = table.add_row().cells
    row_cells[0].text = shareholder.name
    row_cells[1].text = str(shareholder.shares)
    row_cells[2].text = f"{shareholder.percentage}%"

doc.save('agreement.docx')
```

**Using docxtpl (Jinja2 templates)**:
```python
from docxtpl import DocxTemplate

doc = DocxTemplate("template.docx")

context = {
    'buyer_name': 'Acme Corporation',
    'seller_name': 'Smith Industries',
    'purchase_price': '$5,000,000',
    'shareholders': [
        {'name': 'John Smith', 'shares': 1000, 'percentage': 60},
        {'name': 'Jane Doe', 'shares': 667, 'percentage': 40}
    ]
}

doc.render(context)
doc.save("generated_agreement.docx")
```

## PDF (Portable Document Format)

### Overview
- **Format**: PDF/A for archival, PDF 1.7 for general use
- **Use Case**: Final documents, e-signatures, archival, distribution
- **Strengths**: Consistent rendering, security, universal compatibility
- **Limitations**: Not easily editable, larger file sizes

### PDF Variants

**PDF/A (Archival)**:
```
- PDF/A-1: Basic archival standard
- PDF/A-2: Unicode support, JPEG2000
- PDF/A-3: Embedded files allowed

Use for:
- Long-term archival
- Court filings
- Regulatory submissions
- Records retention
```

**PDF/UA (Universal Accessibility)**:
```
Requirements:
- Tagged PDF structure
- Logical reading order
- Alternative text for images
- Proper heading hierarchy
- Form field labels

Use for:
- Accessible documents
- Government submissions
- Compliance requirements
```

**PDF Forms**:
```
Interactive elements:
- Text fields
- Checkboxes
- Radio buttons
- Dropdown lists
- Digital signature fields
```

### Generation Techniques

**Using ReportLab**:
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

doc = SimpleDocTemplate("agreement.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# Title
title = Paragraph("Stock Purchase Agreement", styles['Title'])
story.append(title)
story.append(Spacer(1, 0.5*inch))

# Content
content = Paragraph(
    f"This Agreement is made on {effective_date} between {buyer_name} and {seller_name}.",
    styles['BodyText']
)
story.append(content)

# Table
data = [['Name', 'Shares', 'Percentage']]
for sh in shareholders:
    data.append([sh.name, str(sh.shares), f"{sh.percentage}%"])

table = Table(data)
table.setStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 14),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
])
story.append(table)

doc.build(story)
```

**Converting DOCX to PDF**:
```python
# Using python-docx and reportlab
import docx2pdf
docx2pdf.convert("agreement.docx", "agreement.pdf")

# Using LibreOffice headless
import subprocess
subprocess.run([
    'soffice',
    '--headless',
    '--convert-to', 'pdf',
    'agreement.docx'
])

# Using Microsoft Word API (Windows)
from docx2pdf import convert
convert("agreement.docx", "agreement.pdf")
```

### PDF Security

**Encryption**:
```python
from PyPDF2 import PdfWriter, PdfReader

reader = PdfReader("agreement.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Encrypt with password
writer.encrypt(
    user_password="client_password",
    owner_password="admin_password",
    permissions_flag=0b0100  # Allow printing only
)

with open("agreement_encrypted.pdf", "wb") as output_file:
    writer.write(output_file)
```

**Digital Signatures**:
```python
from endesive import pdf

# Sign PDF
date = datetime.datetime.now().strftime("%Y%m%d%H%M%S+00'00'")
dct = {
    "sigflags": 3,
    "contact": "signer@example.com",
    "location": "Springfield",
    "reason": "Document execution",
    "date": date
}

with open("agreement.pdf", "rb") as fp:
    datau = fp.read()

datas = pdf.sign(
    datau,
    dct,
    "certificate.p12",
    "password",
    "hash_algorithm"
)

with open("agreement_signed.pdf", "wb") as fp:
    fp.write(datau)
    fp.write(datas)
```

## HTML

### Overview
- **Format**: HTML5 with CSS
- **Use Case**: Web portals, email, preview, responsive display
- **Strengths**: Responsive, accessible, interactive
- **Limitations**: Inconsistent rendering, not ideal for printing

### Generation Techniques

**Using Jinja2**:
```python
from jinja2 import Template

template = Template("""
<!DOCTYPE html>
<html>
<head>
    <title>{{ document_title }}</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; }
        .signature-block { margin-top: 50px; }
    </style>
</head>
<body>
    <h1>{{ document_title }}</h1>

    <p>This Agreement is made on {{ effective_date }} between {{ buyer_name }} ("Buyer")
    and {{ seller_name }} ("Seller").</p>

    <h2>Shareholders</h2>
    <table>
        <tr><th>Name</th><th>Shares</th><th>Percentage</th></tr>
        {% for sh in shareholders %}
        <tr>
            <td>{{ sh.name }}</td>
            <td>{{ sh.shares }}</td>
            <td>{{ sh.percentage }}%</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
""")

html = template.render(
    document_title="Stock Purchase Agreement",
    effective_date="November 19, 2025",
    buyer_name="Acme Corporation",
    seller_name="Smith Industries",
    shareholders=shareholders
)

with open("agreement.html", "w") as f:
    f.write(html)
```

**Converting HTML to PDF**:
```python
# Using WeasyPrint
from weasyprint import HTML
HTML('agreement.html').write_pdf('agreement.pdf')

# Using pdfkit (wkhtmltopdf wrapper)
import pdfkit
pdfkit.from_file('agreement.html', 'agreement.pdf')
```

## Rich Text Format (RTF)

### Overview
- **Format**: RTF 1.9
- **Use Case**: Legacy system compatibility, cross-platform editing
- **Strengths**: Universal compatibility, smaller than DOCX
- **Limitations**: Limited formatting capabilities, obsolete

### Generation
```python
from pyrtf import Document, Section, Paragraph, Renderer

doc = Document()
section = Section()
doc.Sections.append(section)

# Add content
p = Paragraph("Stock Purchase Agreement")
section.append(p)

# Render to RTF
renderer = Renderer()
renderer.Write(doc, open('agreement.rtf', 'w'))
```

## Plain Text

### Overview
- **Format**: UTF-8 encoded text
- **Use Case**: Email body, simple contracts, data export
- **Strengths**: Universal compatibility, smallest size
- **Limitations**: No formatting, no visual structure

### Generation
```python
def generate_text_document(data):
    lines = []
    lines.append("STOCK PURCHASE AGREEMENT")
    lines.append("=" * 50)
    lines.append("")
    lines.append(f"Effective Date: {data['effective_date']}")
    lines.append(f"Buyer: {data['buyer_name']}")
    lines.append(f"Seller: {data['seller_name']}")
    lines.append("")
    lines.append("SHAREHOLDERS")
    lines.append("-" * 50)
    for sh in data['shareholders']:
        lines.append(f"  {sh['name']}: {sh['shares']} shares ({sh['percentage']}%)")

    return "\n".join(lines)

with open("agreement.txt", "w") as f:
    f.write(generate_text_document(data))
```

## XML/JSON (Structured Data)

### Overview
- **Use Case**: Data exchange, API responses, further processing
- **Strengths**: Machine-readable, structured, platform-independent
- **Limitations**: Not human-readable, requires transformation for presentation

### XML Example
```xml
<?xml version="1.0" encoding="UTF-8"?>
<StockPurchaseAgreement>
    <Metadata>
        <EffectiveDate>2025-11-19</EffectiveDate>
        <DocumentID>SPA-2025-001</DocumentID>
    </Metadata>
    <Parties>
        <Buyer>
            <Name>Acme Corporation</Name>
            <Address>123 Main St, Springfield</Address>
        </Buyer>
        <Seller>
            <Name>Smith Industries</Name>
            <Address>456 Oak Ave, Springfield</Address>
        </Seller>
    </Parties>
    <Terms>
        <PurchasePrice currency="USD">5000000</PurchasePrice>
        <Shareholders>
            <Shareholder>
                <Name>John Smith</Name>
                <Shares>1000</Shares>
                <Percentage>60.0</Percentage>
            </Shareholder>
        </Shareholders>
    </Terms>
</StockPurchaseAgreement>
```

### JSON Example
```json
{
  "documentType": "StockPurchaseAgreement",
  "metadata": {
    "effectiveDate": "2025-11-19",
    "documentId": "SPA-2025-001",
    "version": "1.0"
  },
  "parties": {
    "buyer": {
      "name": "Acme Corporation",
      "address": "123 Main St, Springfield"
    },
    "seller": {
      "name": "Smith Industries",
      "address": "456 Oak Ave, Springfield"
    }
  },
  "terms": {
    "purchasePrice": {
      "amount": 5000000,
      "currency": "USD"
    },
    "shareholders": [
      {
        "name": "John Smith",
        "shares": 1000,
        "percentage": 60.0
      }
    ]
  }
}
```

## Multi-Format Generation Strategy

### Master Template Approach
```
1. Create master template in DOCX or HTML
2. Generate primary format (DOCX or PDF)
3. Convert to other formats as needed

Workflow:
  Template (DOCX) →  Generated DOCX
                  ↓
                  ↓  (convert)
                  ↓
                  → PDF
                  → PDF/A
                  → HTML
                  → RTF
```

### Parallel Generation
```python
def generate_all_formats(data, template):
    """Generate document in all required formats"""

    # Generate DOCX
    docx_file = generate_docx(data, template)

    # Generate PDF from DOCX
    pdf_file = convert_docx_to_pdf(docx_file)

    # Generate PDF/A for archival
    pdfa_file = convert_to_pdfa(pdf_file)

    # Generate HTML for web display
    html_file = generate_html(data, template)

    # Generate plain text for email
    text_file = generate_text(data)

    return {
        'docx': docx_file,
        'pdf': pdf_file,
        'pdfa': pdfa_file,
        'html': html_file,
        'text': text_file
    }
```

## Format Selection Guidelines

### By Use Case

**Execution and Signatures**:
- Primary: PDF
- Alternative: DOCX (for track changes negotiations)

**Court Filings**:
- PDF or PDF/A (check local rules)
- Often with specific formatting requirements

**Client Delivery**:
- PDF (final, read-only)
- DOCX (if client needs to edit)

**Internal Review**:
- DOCX (for comments and track changes)
- PDF (for approval workflow)

**Archival**:
- PDF/A-1, PDF/A-2, or PDF/A-3
- Consider DOCX as source format

**Web Display**:
- HTML
- PDF (embedded viewer)

**Email**:
- PDF attachment
- HTML inline (for short documents)
- Plain text (for simple notices)

### By Platform Capabilities

**HotDocs**:
- Native: DOCX, PDF, RTF
- Best: DOCX → PDF conversion

**Contract Express**:
- Native: DOCX, PDF
- Best: DOCX with styles

**Documate**:
- Native: PDF, DOCX
- Best: PDF for delivery

**Custom Python**:
- DOCX (python-docx)
- PDF (ReportLab, WeasyPrint)
- HTML (Jinja2)
- All formats with conversion

## Best Practices

1. **Choose Format Based on Use Case**: Execution vs. Review vs. Archival
2. **Maintain Source Templates**: Keep in editable format (DOCX or HTML)
3. **Use Styles, Not Direct Formatting**: Ensures consistency
4. **Test Across Platforms**: Different viewers render differently
5. **Consider Accessibility**: Tagged PDFs, proper HTML semantics
6. **Implement Version Control**: Track template changes
7. **Validate Output**: Check formatting, completeness, accuracy
8. **Optimize File Size**: Compress images, remove unused styles
9. **Secure Sensitive Documents**: Encrypt PDFs, restrict permissions
10. **Maintain Metadata**: Document properties, version info, timestamps

## Quality Checks

### Pre-Generation
- Validate all input data
- Check for required fields
- Verify calculations
- Confirm logic paths

### Post-Generation
- Visual inspection
- Spell check
- Format verification
- Cross-reference validation
- Signature block placement
- Page numbering
- Table of contents accuracy

### Automated Checks
```python
def validate_pdf_output(pdf_path):
    """Run automated quality checks on generated PDF"""
    checks = []

    # Check file exists and is valid PDF
    checks.append(is_valid_pdf(pdf_path))

    # Check page count is reasonable
    checks.append(page_count_in_range(pdf_path, min=1, max=100))

    # Check for searchable text (not image-only)
    checks.append(has_searchable_text(pdf_path))

    # Check file size is reasonable
    checks.append(file_size_reasonable(pdf_path, max_mb=10))

    # Check for required metadata
    checks.append(has_required_metadata(pdf_path))

    return all(checks)
```

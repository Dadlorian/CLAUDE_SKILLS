# Accessibility Standards for Document Automation

## Overview

Accessible documents ensure that all users, including those with disabilities, can access and use automated legal documents. Compliance with accessibility standards is often required by law and demonstrates commitment to inclusive practice.

## Key Standards

### WCAG (Web Content Accessibility Guidelines)
- **WCAG 2.1 Level A**: Minimum accessibility
- **WCAG 2.1 Level AA**: Industry standard (recommended)
- **WCAG 2.1 Level AAA**: Enhanced accessibility

### PDF/UA (PDF Universal Accessibility)
- ISO 14289-1 standard for accessible PDFs
- Required for many government submissions
- Ensures PDFs work with assistive technology

### Section 508
- U.S. federal accessibility standard
- Required for government contractors
- Based on WCAG 2.0 Level AA

## Four Principles (POUR)

### 1. Perceivable
Information must be presentable to users in ways they can perceive

**Visual Content**:
- Provide text alternatives for images
- Ensure sufficient color contrast
- Don't rely solely on color to convey information

**Text Content**:
- Use readable fonts (minimum 12pt)
- Provide adequate line spacing
- Avoid all caps for long text

### 2. Operable
User interface components must be operable

**Keyboard Access**:
- All functionality available via keyboard
- Logical tab order
- Visible focus indicators

**Navigation**:
- Clear document structure
- Skip navigation links
- Descriptive headings

### 3. Understandable
Information and operation must be understandable

**Readability**:
- Plain language where possible
- Define legal terms
- Consistent terminology

**Predictability**:
- Consistent navigation
- Consistent identification
- Clear instructions

### 4. Robust
Content must be robust enough for assistive technologies

**Compatibility**:
- Use standard formats (DOCX, PDF/UA)
- Semantic markup
- Valid code/structure

## PDF Accessibility

### Tagged PDFs

**Document Structure**:
```xml
<Document>
  <H1>Stock Purchase Agreement</H1>
  <P>This Agreement is made on November 19, 2025...</P>

  <H2>Article 1. Purchase and Sale</H2>
  <P>The Seller agrees to sell...</P>

  <Table>
    <TR>
      <TH>Name</TH>
      <TH>Shares</TH>
    </TR>
    <TR>
      <TD>John Smith</TD>
      <TD>1,000</TD>
    </TR>
  </Table>
</Document>
```

**Creating Tagged PDFs with ReportLab**:
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.tableofcontents import TableOfContents

doc = SimpleDocTemplate(
    "accessible_agreement.pdf",
    pagesize=letter,
    title="Stock Purchase Agreement",
    author="Law Firm Name",
    subject="M&A Transaction"
)

styles = getSampleStyleSheet()
story = []

# Add tagged heading
title = Paragraph(
    "Stock Purchase Agreement",
    styles['Heading1']
)
story.append(title)

# Add tagged paragraph
p = Paragraph(
    "This Agreement is made on November 19, 2025...",
    styles['BodyText']
)
story.append(p)

# Add accessible table
data = [
    ['Name', 'Shares'],  # Header row
    ['John Smith', '1,000'],
    ['Jane Doe', '500']
]

table = Table(data)
table.setStyle([
    # Mark first row as header
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
])
story.append(table)

doc.build(story)

# Add PDF/UA metadata
from PyPDF2 import PdfWriter, PdfReader

reader = PdfReader("accessible_agreement.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Set PDF/UA identifier
writer.add_metadata({
    '/Title': 'Stock Purchase Agreement',
    '/Author': 'Law Firm Name',
    '/Subject': 'M&A Transaction',
    '/PDFVersion': '1.7',
    '/UA': 'True'  # PDF/UA identifier
})

with open("accessible_agreement_ua.pdf", "wb") as output:
    writer.write(output)
```

### Alternative Text for Images

```python
from docx import Document
from docx.shared import Inches

doc = Document()

# Add image with alt text
picture = doc.add_picture('company_logo.png', width=Inches(2))

# Access the underlying XML to add alt text
pic = picture._element
pic.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}title', 'Company Logo')
pic.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}descr',
        'Logo of Acme Corporation showing blue and white design')
```

### Reading Order

```python
def ensure_reading_order(doc):
    """Ensure logical reading order in document"""

    # Use proper heading hierarchy
    doc.add_heading('Main Title', 0)  # Title
    doc.add_heading('Section 1', 1)    # Heading 1
    doc.add_heading('Subsection 1.1', 2)  # Heading 2

    # Don't skip levels
    # Bad: H1 -> H3
    # Good: H1 -> H2 -> H3

    # Use styles, not manual formatting
    # Bad: Bold + Large font for heading
    # Good: Heading 1 style
```

## Microsoft Word Accessibility

### Accessibility Checker

```python
from docx import Document

def check_word_accessibility(docx_path):
    """Check Word document for common accessibility issues"""

    doc = Document(docx_path)
    issues = []

    # Check for alt text on images
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            # Image found - check for alt text
            # (Simplified - actual implementation more complex)
            issues.append("Verify alt text for all images")

    # Check heading structure
    headings = [p for p in doc.paragraphs if p.style.name.startswith('Heading')]
    if not headings:
        issues.append("No headings found - add document structure")

    # Check for proper lists
    # Manual numbering is not accessible
    for para in doc.paragraphs:
        text = para.text.strip()
        if text and text[0].isdigit() and '. ' in text[:5]:
            if para.style.name == 'Normal':
                issues.append(f"Use list style instead of manual numbering: {text[:50]}")

    # Check color contrast (requires more complex implementation)
    # Check table headers
    for table in doc.tables:
        # First row should be marked as header
        first_row = table.rows[0]
        # Check if it's styled as header

    return issues
```

### Creating Accessible Word Documents

```python
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Set document properties
core_props = doc.core_properties
core_props.title = "Stock Purchase Agreement"
core_props.subject = "M&A Transaction"
core_props.author = "Law Firm Name"
core_props.keywords = "stock purchase, acquisition"
core_props.language = "en-US"

# Use proper heading hierarchy
doc.add_heading('Stock Purchase Agreement', 0)
doc.add_heading('Article 1. Purchase and Sale', 1)
doc.add_heading('1.1 Shares to be Purchased', 2)

# Use styles for body text
para = doc.add_paragraph(
    'The Seller agrees to sell to the Buyer, and the Buyer agrees to purchase...',
    style='Body Text'
)

# Create accessible list
doc.add_paragraph('The purchase price includes:', style='List Bullet')
doc.add_paragraph('Cash payment of $5,000,000', style='List Bullet')
doc.add_paragraph('Assumption of specified liabilities', style='List Bullet')

# Create accessible table
table = doc.add_table(rows=3, cols=3)
table.style = 'Light Grid Accent 1'

# Header row
hdr_cells = table.rows[0].cells
hdr_cells[0].text = 'Shareholder'
hdr_cells[1].text = 'Shares'
hdr_cells[2].text = 'Percentage'

# Make header row bold
for cell in hdr_cells:
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.font.bold = True

# Data rows
data_row_1 = table.rows[1].cells
data_row_1[0].text = 'John Smith'
data_row_1[1].text = '1,000'
data_row_1[2].text = '60%'

# Ensure sufficient contrast
# Avoid light gray text on white background
# WCAG AA requires 4.5:1 for normal text, 3:1 for large text

# Good: Black on white (21:1)
# Good: #333333 on white (12.6:1)
# Bad: #999999 on white (2.8:1) - fails

# Set language for text-to-speech
for para in doc.paragraphs:
    para_elem = para._element
    para_elem.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-US')

doc.save('accessible_agreement.docx')
```

## Form Field Accessibility

### Accessible PDF Forms

```python
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def create_accessible_form(filename):
    """Create accessible PDF form"""

    c = canvas.Canvas(filename)

    # Add form fields with proper labels and descriptions
    c.acroForm.textfield(
        name='buyer_name',
        tooltip='Enter the legal name of the buyer',
        x=100,
        y=700,
        width=200,
        height=20,
        borderColor='black',
        fillColor='white',
        textColor='black',
        forceBorder=True
    )

    # Add label near field (not part of field, but visible)
    c.drawString(100, 720, "Buyer's Legal Name:")

    # Signature field with description
    c.acroForm.textfield(
        name='buyer_signature',
        tooltip='Signature of authorized representative of buyer',
        x=100,
        y=500,
        width=200,
        height=40
    )

    c.drawString(100, 545, "Buyer's Signature:")

    c.save()
```

### Accessible Web Forms

```html
<!-- Accessible questionnaire field -->
<div class="form-group">
  <label for="buyer_name" id="buyer_name_label">
    Buyer's Legal Name
    <span class="required" aria-label="required">*</span>
  </label>

  <input
    type="text"
    id="buyer_name"
    name="buyer_name"
    required
    aria-required="true"
    aria-labelledby="buyer_name_label"
    aria-describedby="buyer_name_help buyer_name_error"
  />

  <div id="buyer_name_help" class="help-text">
    Enter the full legal name as it appears on incorporation documents
  </div>

  <div id="buyer_name_error" class="error" role="alert" aria-live="polite">
    <!-- Error message appears here when validation fails -->
  </div>
</div>

<!-- Accessible select/dropdown -->
<div class="form-group">
  <label for="state">State of Incorporation</label>
  <select id="state" name="state" aria-describedby="state_help">
    <option value="">Select a state</option>
    <option value="DE">Delaware</option>
    <option value="CA">California</option>
    <option value="NY">New York</option>
  </select>
  <div id="state_help" class="help-text">
    Select the state where the corporation is incorporated
  </div>
</div>

<!-- Accessible checkbox group -->
<fieldset>
  <legend>Optional Provisions</legend>

  <div class="checkbox-group">
    <input
      type="checkbox"
      id="include_earnout"
      name="provisions"
      value="earnout"
    />
    <label for="include_earnout">Include Earnout Provisions</label>
  </div>

  <div class="checkbox-group">
    <input
      type="checkbox"
      id="include_escrow"
      name="provisions"
      value="escrow"
    />
    <label for="include_escrow">Include Escrow Agreement</label>
  </div>
</fieldset>
```

## Color and Contrast

### WCAG Color Contrast Requirements

```
Normal Text:
- AA: 4.5:1 minimum
- AAA: 7:1 minimum

Large Text (18pt+ or 14pt+ bold):
- AA: 3:1 minimum
- AAA: 4.5:1 minimum

Examples:
✓ Black (#000000) on White (#FFFFFF): 21:1
✓ Dark Gray (#333333) on White: 12.6:1
✓ Blue (#0066CC) on White: 7.5:1
✗ Light Gray (#999999) on White: 2.8:1 (fails AA)
✗ Yellow (#FFFF00) on White: 1.1:1 (fails)
```

### Testing Color Contrast

```python
def calculate_contrast_ratio(color1_rgb, color2_rgb):
    """Calculate WCAG contrast ratio between two colors"""

    def get_luminance(rgb):
        """Calculate relative luminance"""
        rgb = [c / 255.0 for c in rgb]
        rgb = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
        return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]

    l1 = get_luminance(color1_rgb)
    l2 = get_luminance(color2_rgb)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    ratio = (lighter + 0.05) / (darker + 0.05)
    return ratio

# Test examples
black_on_white = calculate_contrast_ratio((0, 0, 0), (255, 255, 255))
# Returns: 21.0 (excellent)

gray_on_white = calculate_contrast_ratio((153, 153, 153), (255, 255, 255))
# Returns: 2.8 (fails AA)

blue_on_white = calculate_contrast_ratio((0, 102, 204), (255, 255, 255))
# Returns: 7.5 (passes AAA)
```

## Testing Tools

### Automated Testing

```python
def run_accessibility_audit(document_path):
    """Run automated accessibility checks"""

    issues = []

    if document_path.endswith('.pdf'):
        issues.extend(check_pdf_accessibility(document_path))
    elif document_path.endswith('.docx'):
        issues.extend(check_word_accessibility(document_path))
    elif document_path.endswith('.html'):
        issues.extend(check_html_accessibility(document_path))

    return {
        'total_issues': len(issues),
        'critical': [i for i in issues if i['severity'] == 'critical'],
        'warnings': [i for i in issues if i['severity'] == 'warning'],
        'passed': all(i['severity'] != 'critical' for i in issues)
    }

def check_pdf_accessibility(pdf_path):
    """Check PDF for accessibility issues"""
    issues = []

    # Check if tagged
    if not is_tagged_pdf(pdf_path):
        issues.append({
            'severity': 'critical',
            'issue': 'PDF is not tagged',
            'recommendation': 'Create tagged PDF structure'
        })

    # Check for searchable text
    text = extract_text(pdf_path)
    if len(text) < 100:
        issues.append({
            'severity': 'critical',
            'issue': 'PDF appears to be image-only',
            'recommendation': 'Use OCR or generate from text source'
        })

    # Check metadata
    metadata = get_pdf_metadata(pdf_path)
    if not metadata.get('title'):
        issues.append({
            'severity': 'warning',
            'issue': 'PDF missing title metadata',
            'recommendation': 'Add document title in metadata'
        })

    return issues
```

### Manual Testing

**Screen Reader Testing**:
```
Tools:
- JAWS (Windows) - most common
- NVDA (Windows) - free
- VoiceOver (macOS) - built-in
- TalkBack (Android)
- VoiceOver (iOS)

Test scenarios:
1. Navigate by headings (H key)
2. Navigate by landmarks (D key)
3. Read all content (Down arrow)
4. Navigate tables (Ctrl+Alt+Arrow keys)
5. Fill out forms (Tab, Enter)
```

**Keyboard Navigation Testing**:
```
Test checklist:
□ Can reach all interactive elements with Tab
□ Can activate all controls with Enter/Space
□ Tab order is logical
□ Focus is always visible
□ Can navigate back with Shift+Tab
□ No keyboard traps
□ Skip links work (if applicable)
```

## Best Practices Summary

1. **Structure**: Use proper heading hierarchy
2. **Alternative Text**: Provide for all images
3. **Color**: Don't rely solely on color; ensure sufficient contrast
4. **Forms**: Label all form fields properly
5. **Tables**: Mark header rows and columns
6. **Language**: Specify document language
7. **Lists**: Use proper list markup, not manual numbering
8. **Links**: Use descriptive link text
9. **PDF**: Create tagged PDFs (PDF/UA)
10. **Testing**: Test with actual assistive technologies

## Compliance Checklist

```markdown
# Document Accessibility Compliance Checklist

## General
- [ ] Document has descriptive title
- [ ] Language is specified
- [ ] Logical reading order
- [ ] Sufficient color contrast (4.5:1 minimum)
- [ ] Text is selectable (not image-only)

## Structure
- [ ] Proper heading hierarchy (H1, H2, H3...)
- [ ] No skipped heading levels
- [ ] Headings describe content
- [ ] Lists use proper markup
- [ ] Tables have headers marked

## Images
- [ ] All images have alt text
- [ ] Decorative images marked as such
- [ ] Complex images have long descriptions

## Forms (if applicable)
- [ ] All fields have labels
- [ ] Required fields indicated
- [ ] Error messages are descriptive
- [ ] Instructions provided where needed

## PDF-Specific
- [ ] PDF is tagged
- [ ] Bookmarks provided (if long document)
- [ ] Tab order is logical
- [ ] Form fields are accessible

## Testing
- [ ] Passes automated accessibility checker
- [ ] Tested with screen reader
- [ ] Tested with keyboard only
- [ ] Tested with document reader
```

Accessibility is not optional—it's essential for inclusive legal services and often legally required. Build accessibility into your document automation from the start.

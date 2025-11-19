# Document Automation Examples for Legal Technology

This directory contains 10 comprehensive examples of document generation and automation for legal applications using Python and JavaScript.

## Files Overview

### 1. **01_docx_generator.py** (178 lines)
**Purpose:** Generate Microsoft Word (.docx) documents programmatically

**Key Features:**
- Create formatted Word documents with titles, headings, and paragraphs
- Add signature blocks for contract signing
- Create tables with data
- Generate numbered and bulleted lists
- Add footers with dates
- Example: Service agreements and NDAs

**Dependencies:** `python-docx`

**Example Usage:**
```python
doc = DocxGenerator("SERVICE AGREEMENT")
doc.add_heading("1. PARTIES", level=2)
doc.add_paragraph("This Agreement is between...")
doc.save("/tmp/service_agreement.docx")
```

---

### 2. **02_pdf_generator.py** (218 lines)
**Purpose:** Generate professional PDF documents for legal purposes

**Key Features:**
- Create formatted PDFs with custom styles
- Add tables with styled headers
- Generate numbered lists
- Create signature blocks
- Add page breaks
- Example: Legal notices and compliance reports

**Dependencies:** `reportlab`, `PyPDF2`

**Example Usage:**
```python
pdf = PDFGenerator("/tmp/legal_notice.pdf", "CEASE AND DESIST LETTER")
pdf.add_title("CEASE AND DESIST LETTER")
pdf.add_heading("FACTUAL BACKGROUND")
pdf.generate()
```

---

### 3. **03_template_engine.py** (378 lines)
**Purpose:** Dynamic document generation using Jinja2 templates

**Key Features:**
- Template variable substitution with context
- Service agreement template with dynamic content
- NDA template with flexible clauses
- Employment offer template
- Invoice template
- Filters and conditional rendering

**Dependencies:** `jinja2`

**Example Usage:**
```python
engine = TemplateEngine()
context = {
    'date': '2024-01-15',
    'client_name': 'Acme Corporation',
    'hourly_rate': 250
}
rendered = engine.render_string(SERVICE_AGREEMENT_TEMPLATE, context)
```

---

### 4. **04_conditional_content.py** (394 lines)
**Purpose:** Generate documents with dynamic conditional sections

**Key Features:**
- Service contracts with conditional service lists
- Employment contracts with optional bonuses and stock
- Purchase agreements with conditional warranties
- Lease agreements with auto-renewal options
- NDA with customizable confidentiality categories
- Non-compete and non-solicitation clauses

**Dependencies:** `jinja2`

**Example Usage:**
```python
context = {
    'contract_type': 'service',
    'include_expenses': True,
    'include_non_compete': True,
    'non_compete_period': 2
}
result = ConditionalDocumentGenerator.generate_contract(
    ContractType.SERVICE, context
)
```

---

### 5. **05_data_validation.py** (332 lines)
**Purpose:** Validate document data before generation

**Key Features:**
- Pydantic models for data validation
- Validate party information and emails
- Service agreement validation with rate checks
- Employment agreement salary validation
- NDA data validation
- Custom validators for dates and amounts
- Error handling and reporting

**Dependencies:** `pydantic`

**Example Usage:**
```python
data = {
    'party_a': {'name': 'Legal LLC', 'party_type': 'llc', 'address': '...'},
    'services': ['Consultation', 'Drafting'],
    'hourly_rate': 250.00
}
validated = DocumentValidator.validate_service_agreement(data)
```

---

### 6. **06_document_comparison.py** (346 lines)
**Purpose:** Compare documents and track changes

**Key Features:**
- Compare two document versions using difflib
- Identify added, removed, and modified lines
- Generate change reports and statistics
- Create side-by-side comparisons
- Redline versions with track changes
- Version control system with audit trails

**Example Usage:**
```python
comparator = DocumentComparator(contract_v1, contract_v2, "v1.0", "v1.1")
changes = comparator.compare()
report = comparator.get_change_report()
print(report)
```

---

### 7. **07_version_tracking.py** (472 lines)
**Purpose:** Track document versions with full audit trail

**Key Features:**
- Revision management with timestamps
- Approval workflow (Draft, Pending Review, Approved, Rejected)
- Negotiation status tracking
- Content hashing for integrity checking
- Comprehensive audit logs
- Export history to JSON
- Approval workflow status reports

**Example Usage:**
```python
vm = VersionManager("CONTRACT-2024-001", "Service Agreement")
rev1 = vm.create_revision(content, "John Smith", "Initial draft", "Created v1")
vm.submit_for_review(1, "John Smith")
vm.approve_revision(1, "Manager", "Approved")
vm.export_to_json('/tmp/history.json')
```

---

### 8. **08_accessibility_checker.py** (412 lines)
**Purpose:** Check documents for accessibility compliance (WCAG, ADA, Section 508)

**Key Features:**
- Check for document title
- Verify heading structure and hierarchy
- Detect walls of text
- Check font sizes and line spacing
- Validate link accessibility
- Check list formatting
- Verify page numbers on multi-page documents
- Generate accessibility compliance reports with scores

**Example Usage:**
```python
checker = AccessibilityChecker(document_text)
issues = checker.check_all()
report = checker.get_report()
print(report)
```

---

### 9. **09_hotdocs_example.py** (371 lines)
**Purpose:** Simulate HotDocs document automation with variables and conditionals

**Key Features:**
- Variable substitution: «variable_name»
- Conditional blocks: [IF condition]...content...[END]
- Repeating sections: [REPEAT items]...content...[END REPEAT]
- Service agreements with dynamic services
- NDAs with flexible clauses
- Approval workflow templates
- Variable prompt generation

**Dependencies:** None (standard library)

**Example Usage:**
```python
template = HotDocsTemplate(NDA_TEMPLATE)
template.set_variables({
    'agreement_date': '2024-01-15',
    'disclosing_party_name': 'TechStartup Inc.',
    'include_trade_secrets': True
})
nda = template.assemble()
```

---

### 10. **10_contract_express_script.js** (614 lines)
**Purpose:** ContractExpress-style document assembly using JavaScript

**Key Features:**
- DocumentTemplate class for variable substitution
- Variable placeholders: [VAR:variable_name]
- Conditional logic: [IF:condition]...[ELSE]...[END]
- Repeating sections: [REPEAT:section]...[END_REPEAT]
- ContractAssemblyEngine for high-level document creation
- NDA, Service Agreement, and Employment Agreement templates
- Invoice generation with line items
- Full test examples demonstrating all features

**Dependencies:** None (JavaScript ES6+)

**Example Usage:**
```javascript
const ndaData = {
    agreement_date: 'January 15, 2024',
    disclosing_party_name: 'TechStartup Inc.',
    include_trade_secrets: true
};
const nda = ContractAssemblyEngine.createNDA(ndaData);
console.log(nda);
```

---

## Common Use Cases

### Generate a Service Agreement
```bash
python 01_docx_generator.py    # DOCX format
python 02_pdf_generator.py     # PDF format
python 03_template_engine.py   # Template-based with Jinja2
python 09_hotdocs_example.py   # HotDocs-style
node 10_contract_express_script.js  # JavaScript
```

### Validate Data Before Generation
```python
from 05_data_validation import DocumentValidator
validated = DocumentValidator.validate_service_agreement(data)
```

### Compare Contract Versions
```python
from 06_document_comparison import DocumentComparator
comparator = DocumentComparator(doc1, doc2, "v1.0", "v2.0")
print(comparator.get_change_report())
```

### Track Changes with Version Control
```python
from 07_version_tracking import VersionManager
vm = VersionManager("CONTRACT-001", "Agreement")
vm.create_revision(content, "Author", "Description", "Changes")
vm.approve_revision(1, "Manager", "Approved")
```

### Check Accessibility
```python
from 08_accessibility_checker import AccessibilityChecker
checker = AccessibilityChecker(document_text)
report = checker.get_report()
```

---

## Installation

### Python Dependencies
```bash
pip install python-docx reportlab PyPDF2 jinja2 pydantic
```

### Running Examples

**Python Examples:**
```bash
python 01_docx_generator.py
python 02_pdf_generator.py
python 03_template_engine.py
python 04_conditional_content.py
python 05_data_validation.py
python 06_document_comparison.py
python 07_version_tracking.py
python 08_accessibility_checker.py
python 09_hotdocs_example.py
```

**JavaScript Examples:**
```bash
node 10_contract_express_script.js
```

---

## Key Concepts

### 1. Template Engines
- **Jinja2:** Industry-standard Python templating
- **HotDocs-style:** Variable placeholders with conditional logic
- **ContractExpress-style:** JavaScript-based document assembly

### 2. Conditional Content
- Dynamically include/exclude sections
- Complex branching logic based on user inputs
- Repeating sections for lists and tables

### 3. Data Validation
- Pydantic models for robust validation
- Email validation, date checks, amount validation
- Custom validators for domain-specific rules

### 4. Version Control & Comparison
- Track document changes over time
- Identify what changed and who changed it
- Generate redline versions with track changes
- Full audit trail for compliance

### 5. Accessibility
- WCAG compliance checking
- ADA and Section 508 standards
- Heading hierarchy validation
- Font size and spacing checks

---

## Architecture Patterns

### Generator Pattern
Create specialized generator classes for different document types

### Template Pattern
Use templates with variable substitution and conditional logic

### Builder Pattern
Build documents step-by-step with fluent API

### Validator Pattern
Validate all inputs before document generation

### Version Control Pattern
Track all changes with timestamps and approvals

---

## Legal Technology Applications

1. **Contract Assembly** - Rapidly generate contracts from templates
2. **Compliance Documents** - Create reports with proper formatting
3. **Document Review** - Track changes and compare versions
4. **Approval Workflows** - Manage document approvals and signatures
5. **Accessibility** - Ensure documents meet regulatory standards
6. **Data Validation** - Prevent errors in legal documents
7. **Audit Trails** - Maintain complete change history

---

## Notes

- All examples include sample data and can be run standalone
- Output files are generated in `/tmp/` for testing
- Each example demonstrates best practices for its approach
- Examples are designed for educational and reference purposes
- For production use, add proper error handling and security measures

---

## Contact & Support

For questions about specific examples, refer to the docstrings and example functions in each file.

# Multi-Document Assembly Guide

## Use Cases

1. **Transaction Sets**: Agreement + Schedules + Exhibits
2. **Corporate Packages**: Formation docs + Bylaws + Resolutions
3. **Litigation Bundles**: Complaint + Exhibits + Summons
4. **Estate Plans**: Will + Trust + Powers of Attorney
5. **Closing Binders**: All transaction documents

## Implementation Approaches

### Sequential Generation
```python
def generate_transaction_package(data):
    documents = []

    # Generate main agreement
    agreement = generate_document('stock_purchase_agreement', data)
    documents.append(agreement)

    # Generate schedules
    if data.get('include_disclosure_schedules'):
        schedules = generate_document('disclosure_schedules', data)
        documents.append(schedules)

    # Generate ancillary documents
    if data.get('include_escrow'):
        escrow = generate_document('escrow_agreement', data)
        documents.append(escrow)

    if data.get('include_employment'):
        employment = generate_document('employment_agreement', data)
        documents.append(employment)

    return documents
```

### Parallel Generation
```python
from concurrent.futures import ThreadPoolExecutor

def generate_package_parallel(data):
    templates = [
        'stock_purchase_agreement',
        'disclosure_schedules',
        'escrow_agreement',
        'employment_agreement'
    ]

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(generate_document, template, data)
            for template in templates
        ]
        documents = [f.result() for f in futures]

    return documents
```

### Master Document Approach
```
Main Agreement references:
- See Exhibit A (generated separately)
- See Schedule 1 (generated separately)
- See Attachment B (generated separately)

Final package combines all pieces
```

## Data Sharing

### Shared Variables
```python
# Common data for all documents
common_data = {
    'buyer_name': 'Acme Corp',
    'seller_name': 'Smith Industries',
    'effective_date': '2025-11-19',
    'purchase_price': 5000000
}

# Document-specific data
agreement_data = {**common_data, 'template_specific_field': 'value'}
schedule_data = {**common_data, 'schedule_items': [...]}
```

### Cross-References
```
Agreement Section 2.3: "See Disclosure Schedules attached as Exhibit A"
Disclosure Schedules: "This Exhibit A is attached to the Stock Purchase Agreement dated «effective_date»"
```

## Assembly Strategies

### Single Interview → Multiple Documents
One questionnaire generates entire package

### Multiple Interviews → Document Set
Separate interviews for each document, shared data

### Incremental Assembly
Generate documents as deal progresses

## Package Management

### Document Numbering
```
Main Agreement: Document 1
Exhibit A (Disclosure Schedules): Document 2
Exhibit B (Escrow Agreement): Document 3
Schedule 1 (Assets): Document 4
Schedule 2 (Liabilities): Document 5
```

### Version Control
```
Transaction Package v1.0
├── Stock_Purchase_Agreement_v1.0.pdf
├── Disclosure_Schedules_v1.0.pdf
├── Escrow_Agreement_v1.0.pdf
└── Employment_Agreement_v1.0.pdf

If any document changes:
Transaction Package v1.1 (entire package updated)
```

### Packaging Options
```python
# Individual PDFs
for doc in documents:
    save_as_pdf(doc, f"{doc.name}.pdf")

# Combined PDF
from PyPDF2 import PdfMerger
merger = PdfMerger()
for doc in documents:
    merger.append(doc.path)
merger.write("complete_package.pdf")

# ZIP archive
import zipfile
with zipfile.ZipFile('transaction_package.zip', 'w') as zipf:
    for doc in documents:
        zipf.write(doc.path, doc.name)
```

## Best Practices
1. Use shared data model
2. Maintain cross-reference consistency
3. Version entire package together
4. Test document interactions
5. Provide assembly log
6. Handle partial failures gracefully
7. Allow individual document regeneration

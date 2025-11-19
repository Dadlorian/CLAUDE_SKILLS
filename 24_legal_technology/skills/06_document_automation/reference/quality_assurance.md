# Quality Assurance for Document Automation

## Overview

Quality assurance ensures that automated documents are accurate, complete, and compliant. A robust QA process prevents errors, maintains professional standards, and builds trust in automation systems.

## QA Framework

### 1. Development Phase QA
- Template logic review
- Variable validation
- Conditional path testing
- Calculation verification
- Style consistency

### 2. Testing Phase QA
- Unit testing (individual components)
- Integration testing (full document assembly)
- User acceptance testing
- Edge case testing
- Regression testing

### 3. Deployment Phase QA
- Production validation
- Sample document review
- User feedback collection
- Ongoing monitoring

### 4. Maintenance Phase QA
- Periodic template review
- Update testing
- Version compatibility
- Performance monitoring

## Test Scenarios

### Happy Path Testing
```yaml
Scenario: Standard Stock Purchase Agreement
  Given: All required fields completed with valid data
  And: Standard transaction structure
  And: No special provisions
  When: Document is generated
  Then: Document should generate successfully
  And: All fields should be populated correctly
  And: Formatting should be consistent
  And: Calculations should be accurate
```

### Edge Case Testing
```yaml
Scenario: Maximum Shareholders
  Given: 50 shareholders (maximum allowed)
  When: Document is generated
  Then: All shareholders should appear
  And: Ownership percentages should total 100%
  And: Document should not exceed page limits
  And: Performance should be acceptable (<5 seconds)

Scenario: Minimum Data
  Given: Only required fields completed
  And: All optional fields left blank
  When: Document is generated
  Then: Document should generate successfully
  And: No placeholder text should appear
  And: Optional sections should be excluded cleanly

Scenario: Special Characters
  Given: Company name contains "&", quotes, apostrophes
  And: Address contains accented characters
  When: Document is generated
  Then: All special characters should render correctly
  And: No encoding errors should occur
```

### Error Condition Testing
```yaml
Scenario: Invalid Purchase Price
  Given: Purchase price = -1000000 (negative)
  When: User attempts to submit
  Then: Validation error should appear
  And: Error message should be clear
  And: User should remain on same page

Scenario: Date Logic Error
  Given: Contract end date before start date
  When: User attempts to continue
  Then: Validation error should appear
  And: Both dates should be highlighted
  And: Suggested correction should be provided

Scenario: Ownership Percentage Error
  Given: Shareholder percentages total 105%
  When: Document generation attempted
  Then: Error should be raised
  And: Current total should be displayed
  And: User should be prompted to correct
```

## Automated Testing

### Unit Tests
```python
import unittest
from document_automation import StockPurchaseAgreement

class TestStockPurchaseAgreement(unittest.TestCase):

    def test_ownership_percentage_calculation(self):
        """Test that ownership percentages calculate correctly"""
        agreement = StockPurchaseAgreement()
        agreement.total_shares = 1000
        agreement.add_shareholder("John Smith", 600)
        agreement.add_shareholder("Jane Doe", 400)

        self.assertEqual(agreement.shareholders[0].percentage, 60.0)
        self.assertEqual(agreement.shareholders[1].percentage, 40.0)

    def test_ownership_total_validation(self):
        """Test that ownership must total 100%"""
        agreement = StockPurchaseAgreement()
        agreement.total_shares = 1000
        agreement.add_shareholder("John Smith", 700)
        agreement.add_shareholder("Jane Doe", 400)

        with self.assertRaises(ValidationError):
            agreement.validate()

    def test_date_range_validation(self):
        """Test that end date must be after start date"""
        agreement = StockPurchaseAgreement()
        agreement.start_date = "2025-12-01"
        agreement.end_date = "2025-11-01"

        with self.assertRaises(ValidationError):
            agreement.validate()

    def test_earnout_calculation(self):
        """Test earnout payment calculations"""
        agreement = StockPurchaseAgreement()
        agreement.earnout_target = 5000000
        agreement.earnout_percentage = 10
        agreement.actual_revenue = 6000000

        self.assertEqual(agreement.calculate_earnout(), 100000)

    def test_required_fields(self):
        """Test that all required fields must be present"""
        agreement = StockPurchaseAgreement()

        with self.assertRaises(ValidationError) as context:
            agreement.validate()

        errors = context.exception.errors
        self.assertIn('buyer_name', errors)
        self.assertIn('seller_name', errors)
        self.assertIn('purchase_price', errors)
```

### Integration Tests
```python
def test_full_document_generation():
    """Test complete document generation workflow"""
    # Prepare test data
    data = {
        'buyer_name': 'Acme Corporation',
        'seller_name': 'Smith Industries',
        'purchase_price': 5000000,
        'effective_date': '2025-11-19',
        'shareholders': [
            {'name': 'John Smith', 'shares': 600, 'percentage': 60},
            {'name': 'Jane Doe', 'shares': 400, 'percentage': 40}
        ]
    }

    # Generate document
    template = load_template('stock_purchase_agreement.docx')
    output = generate_document(template, data)

    # Verify output
    assert output is not None
    assert os.path.exists(output)
    assert file_size(output) > 0

    # Verify content
    doc = open_document(output)
    assert 'Acme Corporation' in doc.text
    assert 'Smith Industries' in doc.text
    assert '$5,000,000' in doc.text or '5000000' in doc.text

    # Verify structure
    assert doc.section_count > 0
    assert doc.paragraph_count > 10
    assert has_signature_blocks(doc)

def test_multi_document_assembly():
    """Test assembly of multiple related documents"""
    data = load_test_data('complex_transaction.json')

    documents = generate_document_set(data, [
        'stock_purchase_agreement',
        'disclosure_schedules',
        'escrow_agreement',
        'non_compete_agreement'
    ])

    assert len(documents) == 4
    for doc in documents:
        assert os.path.exists(doc)
        assert validate_document(doc)
```

### Regression Tests
```python
def test_backward_compatibility():
    """Test that old answer files still work with new template"""
    # Load answer file from previous version
    old_answers = load_answer_file('v1.0_answers.json')

    # Generate with current template
    current_template = load_template('stock_purchase_agreement_v2.0.docx')

    # Should not raise errors
    output = generate_document(current_template, old_answers)

    # Verify essential fields populated
    doc = open_document(output)
    assert all_required_sections_present(doc)
```

## Manual Review Checklist

### Content Review
```
□ All required sections present
□ Client/party names correct
□ Dates accurate and formatted correctly
□ Dollar amounts correct and formatted consistently
□ Calculations accurate
□ Cross-references correct
□ Defined terms used consistently
□ No placeholder text remaining
□ No duplicate content
□ Exhibits/schedules properly referenced
```

### Formatting Review
```
□ Consistent font throughout
□ Proper heading hierarchy
□ Page numbers correct
□ Headers/footers present
□ Table of contents accurate (if applicable)
□ Tables formatted consistently
□ Lists and numbering correct
□ Signature blocks properly formatted
□ Page breaks appropriate
□ No orphaned headings
```

### Legal Review
```
□ Correct legal entity names
□ Proper jurisdiction references
□ Accurate legal citations
□ Appropriate boilerplate language
□ Correct execution requirements
□ Proper notice provisions
□ Compliance with applicable law
□ Attorney review completed
□ Client approval obtained
```

### Technical Review
```
□ Correct output format (PDF, DOCX, etc.)
□ File size reasonable
□ Metadata complete and accurate
□ Security settings appropriate
□ Accessibility compliance (if required)
□ Searchable text (PDFs)
□ No corrupted elements
□ Compatible with target systems
```

## Data Validation

### Input Validation
```python
class DocumentValidator:
    def validate_input_data(self, data):
        """Validate all input data before document generation"""
        errors = []

        # Required field validation
        required_fields = ['buyer_name', 'seller_name', 'purchase_price', 'effective_date']
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Required field missing: {field}")

        # Type validation
        if not isinstance(data.get('purchase_price'), (int, float)):
            errors.append("Purchase price must be numeric")

        # Range validation
        if data.get('purchase_price', 0) <= 0:
            errors.append("Purchase price must be positive")

        # Date validation
        try:
            effective_date = parse_date(data.get('effective_date'))
            if effective_date < date.today():
                errors.append("Warning: Effective date is in the past")
        except ValueError:
            errors.append("Invalid date format for effective_date")

        # Business rule validation
        if data.get('shareholders'):
            total_percentage = sum(sh['percentage'] for sh in data['shareholders'])
            if abs(total_percentage - 100) > 0.01:  # Allow for rounding
                errors.append(f"Ownership percentages must total 100%, currently {total_percentage}%")

        return errors

    def validate_output(self, document_path):
        """Validate generated document"""
        errors = []

        # File exists
        if not os.path.exists(document_path):
            errors.append("Document file not found")
            return errors

        # File not empty
        if os.path.getsize(document_path) == 0:
            errors.append("Document file is empty")

        # Valid format
        if document_path.endswith('.docx'):
            if not is_valid_docx(document_path):
                errors.append("Invalid DOCX format")
        elif document_path.endswith('.pdf'):
            if not is_valid_pdf(document_path):
                errors.append("Invalid PDF format")

        # Contains required text
        doc_text = extract_text(document_path)
        if len(doc_text) < 100:
            errors.append("Document appears incomplete (too short)")

        # No placeholder text
        placeholders = find_placeholders(doc_text)
        if placeholders:
            errors.append(f"Unfilled placeholders found: {', '.join(placeholders)}")

        return errors
```

## Continuous Monitoring

### Usage Analytics
```python
def track_document_generation(template_id, user_id, success, errors=None):
    """Track document generation for quality monitoring"""
    analytics.log({
        'event': 'document_generated',
        'timestamp': datetime.now(),
        'template_id': template_id,
        'user_id': user_id,
        'success': success,
        'errors': errors,
        'generation_time_ms': timer.elapsed()
    })

def generate_quality_report(template_id, start_date, end_date):
    """Generate quality metrics report"""
    events = analytics.query({
        'template_id': template_id,
        'date_range': (start_date, end_date)
    })

    total_generations = len(events)
    successful = sum(1 for e in events if e['success'])
    failed = total_generations - successful
    success_rate = successful / total_generations * 100 if total_generations > 0 else 0

    common_errors = Counter()
    for event in events:
        if event['errors']:
            for error in event['errors']:
                common_errors[error] += 1

    return {
        'total_generations': total_generations,
        'successful': successful,
        'failed': failed,
        'success_rate': success_rate,
        'avg_generation_time': mean(e['generation_time_ms'] for e in events),
        'common_errors': common_errors.most_common(10)
    }
```

### Error Tracking
```python
class ErrorTracker:
    def log_error(self, template_id, error_type, error_message, context):
        """Log error for analysis"""
        self.errors.append({
            'timestamp': datetime.now(),
            'template_id': template_id,
            'error_type': error_type,
            'message': error_message,
            'context': context
        })

    def get_error_trends(self, days=30):
        """Analyze error trends over time"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_errors = [e for e in self.errors if e['timestamp'] > cutoff]

        by_type = defaultdict(list)
        for error in recent_errors:
            by_type[error['error_type']].append(error)

        trends = {}
        for error_type, errors in by_type.items():
            by_date = defaultdict(int)
            for error in errors:
                date = error['timestamp'].date()
                by_date[date] += 1

            trends[error_type] = {
                'total': len(errors),
                'daily_average': len(errors) / days,
                'trend': 'increasing' if self._is_increasing(by_date) else 'stable'
            }

        return trends
```

## Best Practices

1. **Test Early and Often**: Don't wait until completion to test
2. **Automate Where Possible**: Automated tests catch regressions
3. **Use Real Data**: Test with realistic scenarios
4. **Document Test Cases**: Maintain test scenario library
5. **Track Metrics**: Monitor success rates and error patterns
6. **Review Regularly**: Periodic manual review of automated outputs
7. **Update Tests**: When templates change, update test cases
8. **User Feedback**: Collect and act on user-reported issues
9. **Version Control**: Track QA results across versions
10. **Continuous Improvement**: Use QA data to improve templates

## QA Metrics

### Key Performance Indicators
```
Success Rate: % of successful document generations
Error Rate: % of failed generations
Average Generation Time: Time to generate document
User Satisfaction: Rating from users
Template Accuracy: % of documents requiring no corrections
Time to Fix: Average time to resolve issues
```

### Quality Targets
```
Success Rate: > 99%
Error Rate: < 1%
Generation Time: < 5 seconds for standard documents
User Satisfaction: > 4.5/5.0
Template Accuracy: > 95% require no manual corrections
Time to Fix: < 1 business day for critical issues
```

## Issue Management

### Issue Prioritization
```
P0 - Critical: Document generation fails, data loss, security issue
P1 - High: Incorrect calculations, missing required content
P2 - Medium: Formatting issues, minor errors
P3 - Low: Cosmetic issues, enhancement requests
```

### Resolution Workflow
```
1. Issue Reported
   ↓
2. Triage (assign priority)
   ↓
3. Investigation (reproduce, identify root cause)
   ↓
4. Fix Development
   ↓
5. Testing (verify fix, check for regressions)
   ↓
6. Deployment
   ↓
7. Verification (confirm resolution)
   ↓
8. Documentation (update knowledge base)
```

Quality assurance is an ongoing process that requires commitment, tools, and continuous attention to maintain high-quality document automation systems.

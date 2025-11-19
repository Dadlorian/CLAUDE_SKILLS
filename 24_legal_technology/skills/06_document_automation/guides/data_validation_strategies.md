# Data Validation Strategies Guide

## Validation Levels

### 1. Client-Side Validation (Immediate)
```javascript
// Real-time validation
email.addEventListener('blur', function() {
  if (!isValidEmail(this.value)) {
    showError(this, "Invalid email format");
  }
});

// Before form submission
form.addEventListener('submit', function(e) {
  if (!validateForm()) {
    e.preventDefault();
    showErrors();
  }
});
```

### 2. Server-Side Validation (Required)
```python
def validate_purchase_agreement_data(data):
    errors = []

    # Required fields
    if not data.get('buyer_name'):
        errors.append("Buyer name is required")

    # Type validation
    if not isinstance(data.get('purchase_price'), (int, float)):
        errors.append("Purchase price must be numeric")

    # Range validation
    if data.get('purchase_price', 0) <= 0:
        errors.append("Purchase price must be positive")

    # Business rules
    if data.get('ownership_percentage', 0) > 100:
        errors.append("Ownership cannot exceed 100%")

    return errors
```

### 3. Database Validation (Constraints)
```sql
CREATE TABLE documents (
    purchase_price DECIMAL(15,2) CHECK (purchase_price > 0),
    effective_date DATE NOT NULL,
    email VARCHAR(255) CHECK (email LIKE '%@%.%')
);
```

## Validation Types

### Format Validation
```python
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PHONE_PATTERN = r'^\(\d{3}\)\s\d{3}-\d{4}$'
SSN_PATTERN = r'^\d{3}-\d{2}-\d{4}$'
ZIP_PATTERN = r'^\d{5}(-\d{4})?$'
```

### Business Rule Validation
```python
# Shareholder percentages must total 100%
total = sum(sh['percentage'] for sh in shareholders)
if abs(total - 100) > 0.01:
    raise ValidationError(f"Ownership must total 100%, currently {total}%")

# End date must be after start date
if end_date <= start_date:
    raise ValidationError("End date must be after start date")
```

### Cross-Field Validation
```python
# Accredited investor requirements
if investor_type == "accredited":
    if net_worth < 1000000 and annual_income < 200000:
        raise ValidationError("Does not meet accredited investor requirements")
```

## Error Messages

**Good Error Messages**:
- ✓ "Email must include @ symbol (e.g., name@example.com)"
- ✓ "Purchase price must be between $1 and $1,000,000,000"
- ✓ "End date (11/15/2025) must be after start date (11/20/2025)"

**Bad Error Messages**:
- ✗ "Invalid input"
- ✗ "Error"
- ✗ "Field validation failed"

## Best Practices
1. Validate on both client and server
2. Provide immediate feedback
3. Show helpful error messages
4. Validate on field blur, not just submit
5. Highlight problem fields
6. Suggest corrections
7. Prevent rather than correct
8. Test edge cases

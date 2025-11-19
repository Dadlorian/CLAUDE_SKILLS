# Template Optimization Guide

## Performance Optimization

### 1. Minimize Calculations
```
// Bad - recalculates every time
Ownership = (Shares / TotalShares) * 100  // Used 50 times in document

// Good - calculate once, reuse
COMPUTATION
  Ownership = (Shares / TotalShares) * 100
END COMPUTATION
// Use Ownership variable throughout
```

### 2. Simplify Logic
```
// Bad - deeply nested
IF A
  IF B
    IF C
      IF D
        Content
      END IF
    END IF
  END IF
END IF

// Good - combined conditions
IF A AND B AND C AND D
  Content
END IF
```

### 3. Optimize Loops
```
// Bad - expensive operation in loop
REPEAT FOR EACH item
  total_value = CALCULATE_TOTAL()  // Recalculates every iteration
  item_percentage = item.value / total_value
END REPEAT

// Good - calculate once
total_value = CALCULATE_TOTAL()
REPEAT FOR EACH item
  item_percentage = item.value / total_value
END REPEAT
```

### 4. Cache External Data
```python
# Bad - API call for each document
def generate_document(data):
    tax_rate = api.get_tax_rate(data['state'])  // API call
    # ... use tax_rate

# Good - cache tax rates
tax_rates = {}  # Cache
def generate_document(data):
    if data['state'] not in tax_rates:
        tax_rates[data['state']] = api.get_tax_rate(data['state'])
    tax_rate = tax_rates[data['state']]
    # ... use tax_rate
```

## Size Optimization

### Reduce Template Size
- Remove unused styles
- Compress images
- Delete unnecessary formatting
- Minimize whitespace
- Optimize tables

### Reduce Output Size
```python
# Compress images in DOCX
from PIL import Image

img = Image.open('logo.png')
img = img.resize((200, 100), Image.LANCZOS)
img.save('logo_optimized.png', optimize=True, quality=85)
```

## Maintenance Optimization

### Modular Design
```
template/
├── components/
│   ├── party_info.component
│   ├── signature_block.component
│   └── boilerplate.component
└── main_template.docx
```

### Clear Naming
```
// Bad
var1 = x * y
var2 = var1 / z

// Good
gross_amount = base_price * quantity
net_amount = gross_amount / shares
```

### Documentation
```
<!--
CALCULATION: Total Consideration
Formula: Base Price + Earnout - Escrow
Updated: 2025-11-19
Author: Jane Smith
-->
```

## User Experience Optimization

### Progressive Disclosure
Show only relevant questions based on previous answers

### Smart Defaults
Pre-fill with common values or previous entries

### Field Grouping
Group related fields on same page

### Clear Labels
Use descriptive, helpful field labels

## Monitoring & Metrics

Track:
- Generation time
- Template size
- Error rates
- User completion time
- Support requests

Optimize based on data, not assumptions.

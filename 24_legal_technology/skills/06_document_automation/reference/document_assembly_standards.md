# Document Assembly Standards and Best Practices

## Overview

Document assembly standards ensure consistency, quality, and maintainability across automated document templates. Following industry standards and best practices leads to more reliable automation systems and better outcomes.

## Industry Standards

### ABA (American Bar Association) Guidelines

**Competence**:
- Lawyers must understand the technology they use
- Review automated documents before delivery
- Ensure accuracy of templates and logic
- Maintain competence through training

**Confidentiality**:
- Protect client data in automation systems
- Encrypt sensitive information
- Secure answer files and generated documents
- Control access to templates and data

**Communication**:
- Explain automation process to clients
- Disclose limitations of automated documents
- Maintain clear communication channels

### Legal Document Standards

**Plain Language Movement**:
```
Traditional: "Notwithstanding any provision to the contrary herein contained..."
Modern: "Despite anything else in this agreement..."

Traditional: "Said party of the first part hereby agrees..."
Modern: "The Buyer agrees..."

Traditional: "Witnesseth"
Modern: "This Agreement states:"
```

**Drafting Standards**:
- Use consistent defined terms
- Capitalize defined terms
- Number sections logically
- Use active voice
- Avoid legalese where possible
- Write short sentences and paragraphs
- Use parallel structure in lists

### Technical Standards

**XML Standards**:
- Office Open XML (OOXML) for DOCX
- XHTML for web-based documents
- XML Schema for validation

**PDF Standards**:
- PDF/A for archival
- PDF/UA for accessibility
- PDF 1.7 for general use

**Character Encoding**:
- UTF-8 for all text content
- Handle special characters properly
- Support international characters

## Template Organization Standards

### Naming Conventions

**Template Files**:
```
[Practice Area]_[Document Type]_[Jurisdiction]_v[Version].ext

Examples:
Corporate_Stock_Purchase_Agreement_DE_v2.0.docx
Employment_Confidentiality_Agreement_CA_v1.5.docx
Real_Estate_Purchase_Agreement_Multi_State_v3.0.docx
```

**Variable Names**:
```
[Entity]_[Property]_[Type]

Examples:
buyer_legal_name
contract_effective_date
purchase_price_usd
seller_primary_contact_email
```

**Component Names**:
```
[Category]_[Component_Name].component

Examples:
common_party_information.component
boilerplate_force_majeure.component
signature_block_corporate.component
```

### Folder Structure

```
document_automation/
├── templates/
│   ├── corporate/
│   │   ├── mergers_acquisitions/
│   │   │   ├── stock_purchase_agreement/
│   │   │   ├── asset_purchase_agreement/
│   │   │   └── merger_agreement/
│   │   ├── formation/
│   │   └── governance/
│   ├── employment/
│   ├── real_estate/
│   └── litigation/
├── components/
│   ├── common/
│   ├── corporate/
│   └── jurisdictional/
├── clauses/
│   ├── boilerplate/
│   ├── industry_specific/
│   └── custom/
├── tests/
│   ├── test_data/
│   └── test_scenarios/
├── docs/
│   ├── user_guides/
│   ├── training/
│   └── api/
└── config/
```

## Quality Standards

### Template Quality Checklist

```markdown
# Template Quality Standards

## Legal Accuracy
- [ ] Reviewed by qualified attorney
- [ ] Citations are current and accurate
- [ ] Jurisdiction-specific provisions correct
- [ ] Complies with local rules and regulations
- [ ] Defined terms used consistently

## Technical Quality
- [ ] All variables defined
- [ ] All conditional logic tested
- [ ] Calculations verified
- [ ] No broken references
- [ ] No placeholder text in output
- [ ] Formatting consistent

## Usability
- [ ] Clear field labels
- [ ] Helpful instructions provided
- [ ] Logical question flow
- [ ] Appropriate defaults set
- [ ] Validation rules comprehensive
- [ ] Error messages helpful

## Documentation
- [ ] User guide complete
- [ ] Variable dictionary provided
- [ ] Logic documented
- [ ] Examples provided
- [ ] Version history maintained

## Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Edge cases tested
- [ ] User acceptance testing completed
- [ ] Backward compatibility verified

## Accessibility
- [ ] WCAG AA compliance
- [ ] Screen reader compatible
- [ ] Keyboard navigable
- [ ] Sufficient color contrast
- [ ] Alt text for images

## Security
- [ ] Access controls defined
- [ ] Sensitive data protected
- [ ] Audit logging enabled
- [ ] Compliance requirements met
```

### Code Quality Standards

**Conditional Logic**:
```
Good Practice:
- Keep conditions simple
- Use descriptive variable names
- Document complex logic
- Avoid deep nesting (max 3 levels)
- Prefer early returns over deep nesting

Example:
IF buyer_type = "Corporation"
  IF state_of_incorporation = ""
    ERROR "State of incorporation required for corporations"
    RETURN
  END IF

  Display corporation-specific provisions
END IF
```

**Calculations**:
```
Good Practice:
- Show formula in comments
- Validate inputs before calculation
- Handle division by zero
- Round appropriately
- Validate results

Example:
# Calculate ownership percentage
# Formula: (shares_owned / total_shares) * 100
IF total_shares > 0
  ownership_percentage = (shares_owned / total_shares) * 100
  IF ownership_percentage < 0 OR ownership_percentage > 100
    ERROR "Ownership percentage out of valid range"
  END IF
ELSE
  ERROR "Total shares must be greater than zero"
END IF
```

## Data Standards

### Data Validation

**Input Validation**:
```python
class InputValidator:
    """Standard input validation rules"""

    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("Invalid email format")

    @staticmethod
    def validate_phone(phone):
        """Validate US phone number"""
        # Accept various formats: (555) 555-5555, 555-555-5555, 5555555555
        cleaned = re.sub(r'[^\d]', '', phone)
        if len(cleaned) != 10:
            raise ValidationError("Phone number must be 10 digits")

    @staticmethod
    def validate_ssn(ssn):
        """Validate US Social Security Number"""
        pattern = r'^\d{3}-\d{2}-\d{4}$'
        if not re.match(pattern, ssn):
            raise ValidationError("SSN must be in format XXX-XX-XXXX")

    @staticmethod
    def validate_ein(ein):
        """Validate US Employer Identification Number"""
        pattern = r'^\d{2}-\d{7}$'
        if not re.match(pattern, ein):
            raise ValidationError("EIN must be in format XX-XXXXXXX")

    @staticmethod
    def validate_currency(amount, min_value=None, max_value=None):
        """Validate currency amount"""
        try:
            amount_float = float(amount)
        except (ValueError, TypeError):
            raise ValidationError("Amount must be a number")

        if min_value is not None and amount_float < min_value:
            raise ValidationError(f"Amount must be at least {min_value}")

        if max_value is not None and amount_float > max_value:
            raise ValidationError(f"Amount must not exceed {max_value}")

        return amount_float

    @staticmethod
    def validate_date(date_string, format='%Y-%m-%d'):
        """Validate date format and value"""
        try:
            date_obj = datetime.strptime(date_string, format)
        except ValueError:
            raise ValidationError(f"Date must be in format {format}")

        return date_obj
```

### Data Formatting

**Standardized Formats**:
```python
class DataFormatter:
    """Standard data formatting rules"""

    @staticmethod
    def format_currency(amount, currency='USD'):
        """Format currency consistently"""
        if currency == 'USD':
            return f"${amount:,.2f}"
        elif currency == 'EUR':
            return f"€{amount:,.2f}"
        elif currency == 'GBP':
            return f"£{amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"

    @staticmethod
    def format_date(date, format_type='long'):
        """Format dates consistently"""
        if format_type == 'long':
            return date.strftime("%B %d, %Y")  # November 19, 2025
        elif format_type == 'short':
            return date.strftime("%m/%d/%Y")   # 11/19/2025
        elif format_type == 'iso':
            return date.strftime("%Y-%m-%d")   # 2025-11-19
        else:
            return str(date)

    @staticmethod
    def format_phone(phone):
        """Format phone number consistently"""
        cleaned = re.sub(r'[^\d]', '', phone)
        if len(cleaned) == 10:
            return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
        return phone

    @staticmethod
    def format_ssn(ssn):
        """Format SSN consistently"""
        cleaned = re.sub(r'[^\d]', '', ssn)
        if len(cleaned) == 9:
            return f"{cleaned[:3]}-{cleaned[3:5]}-{cleaned[5:]}"
        return ssn

    @staticmethod
    def format_percentage(value, decimal_places=2):
        """Format percentage consistently"""
        return f"{value:.{decimal_places}f}%"

    @staticmethod
    def format_number(value, decimal_places=0):
        """Format numbers with thousands separators"""
        if decimal_places == 0:
            return f"{int(value):,}"
        else:
            return f"{value:,.{decimal_places}f}"
```

## Security Standards

### Access Control

```python
class AccessControl:
    """Standard access control for templates"""

    PERMISSION_LEVELS = {
        'viewer': ['read'],
        'editor': ['read', 'edit'],
        'publisher': ['read', 'edit', 'publish'],
        'admin': ['read', 'edit', 'publish', 'delete', 'manage_permissions']
    }

    def check_permission(self, user, resource, action):
        """Check if user has permission for action on resource"""
        user_role = self.get_user_role(user, resource)
        allowed_actions = self.PERMISSION_LEVELS.get(user_role, [])
        return action in allowed_actions

    def audit_access(self, user, resource, action, granted):
        """Log access attempts for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user.id,
            'user_email': user.email,
            'resource_type': resource.type,
            'resource_id': resource.id,
            'action': action,
            'granted': granted,
            'ip_address': request.remote_addr
        }
        self.audit_log.append(log_entry)
```

### Data Protection

```python
class DataProtection:
    """Standard data protection practices"""

    @staticmethod
    def encrypt_sensitive_data(data, encryption_key):
        """Encrypt sensitive data before storage"""
        from cryptography.fernet import Fernet
        f = Fernet(encryption_key)
        encrypted = f.encrypt(data.encode())
        return encrypted

    @staticmethod
    def decrypt_sensitive_data(encrypted_data, encryption_key):
        """Decrypt sensitive data for use"""
        from cryptography.fernet import Fernet
        f = Fernet(encryption_key)
        decrypted = f.decrypt(encrypted_data)
        return decrypted.decode()

    @staticmethod
    def mask_sensitive_field(value, field_type='ssn'):
        """Mask sensitive data for display"""
        if field_type == 'ssn':
            return f"***-**-{value[-4:]}"
        elif field_type == 'credit_card':
            return f"****-****-****-{value[-4:]}"
        elif field_type == 'account':
            return f"****{value[-4:]}"
        else:
            return "****"

    @staticmethod
    def sanitize_input(user_input):
        """Sanitize user input to prevent injection"""
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>\"\'%;()&+]', '', user_input)
        return sanitized.strip()
```

## Documentation Standards

### Template Documentation

```markdown
# Template Name: Stock Purchase Agreement

## Overview
Stock purchase agreement for acquisition of privately held companies.

## Version
Current Version: 2.0.0
Last Updated: 2025-11-19
Author: Jane Smith (jane.smith@firm.com)

## Use Cases
- Private company stock acquisitions
- Majority stake purchases (>50%)
- Minority stake purchases with specific rights
- Complex deal structures with earnouts and escrow

## Not Suitable For
- Public company acquisitions (use public M&A template)
- Asset purchases (use asset purchase agreement template)
- Simple stock transfers between existing shareholders

## Required Information
- Buyer entity information
- Seller entity information
- Target company information
- Stock details (class, shares)
- Purchase price and payment terms
- Closing date

## Optional Provisions
- Earnout provisions
- Escrow arrangements
- Employment agreements
- Non-compete provisions

## Jurisdictions
- Primary: Delaware (default)
- Supported: All US states
- Customization required for: International transactions

## Variables
See `variables.md` for complete field reference

## Logic
See `logic_documentation.md` for conditional logic details

## Testing
See `test_scenarios.md` for test cases

## Change Log
See `CHANGELOG.md` for version history

## Support
Contact: documentsupport@firm.com
```

### Variable Documentation

```markdown
# Variable Reference

## buyer_legal_name
- **Type**: Text
- **Required**: Yes
- **Description**: Full legal name of the acquiring entity
- **Example**: "Acme Acquisition Corp."
- **Validation**: Maximum 200 characters
- **Used In**: Throughout agreement, signature blocks

## purchase_price
- **Type**: Currency (USD)
- **Required**: Yes
- **Description**: Base purchase price (excluding earnout)
- **Minimum**: $1
- **Maximum**: $1,000,000,000
- **Format**: Displayed as $X,XXX,XXX.XX
- **Used In**: Purchase price section, calculation of total consideration

## ownership_percentage
- **Type**: Decimal (Percentage)
- **Required**: Yes (for each shareholder)
- **Description**: Percentage ownership of each shareholder
- **Minimum**: 0.01
- **Maximum**: 100.00
- **Validation**: Sum of all shareholders must equal 100%
- **Calculated**: Automatically from shares_owned / total_shares
- **Format**: XX.XX%
```

## Performance Standards

### Response Time Targets

```
Document Generation:
- Simple document (<10 pages): < 2 seconds
- Standard document (10-50 pages): < 5 seconds
- Complex document (50+ pages): < 15 seconds
- Bulk generation (10 documents): < 30 seconds

Interview/Questionnaire:
- Page load time: < 1 second
- Field validation: < 200ms
- Save progress: < 500ms
- Final submission: < 2 seconds

API Endpoints:
- GET requests: < 200ms
- POST requests: < 500ms
- Document generation: < 10 seconds
```

### Scalability Standards

```
Concurrent Users:
- 10 users: No performance degradation
- 100 users: < 10% performance degradation
- 1000 users: Requires load balancing

Document Volume:
- 100 documents/hour: Single instance
- 1000 documents/hour: Load balanced instances
- 10000 documents/hour: Distributed queue system
```

## Compliance Standards

### Regulatory Compliance

**GDPR (if handling EU data)**:
- Data minimization
- Purpose limitation
- Storage limitation
- Right to access
- Right to erasure
- Data portability

**CCPA (California clients)**:
- Consumer right to know
- Right to deletion
- Right to opt-out
- Non-discrimination

**Legal Ethics**:
- Competence (ABA Model Rule 1.1)
- Confidentiality (ABA Model Rule 1.6)
- Communication (ABA Model Rule 1.4)
- Fees (ABA Model Rule 1.5)

### Audit Requirements

```python
class AuditCompliance:
    """Ensure audit trail compliance"""

    def log_document_generation(self, template_id, user_id, data, output):
        """Log all document generations"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'document_generation',
            'template_id': template_id,
            'template_version': self.get_template_version(template_id),
            'user_id': user_id,
            'user_email': self.get_user_email(user_id),
            'input_hash': self.hash_data(data),  # Hash, don't store PII
            'output_id': output.id,
            'output_hash': self.hash_file(output.path),
            'success': True
        }
        self.write_audit_log(audit_entry)

    def generate_audit_report(self, start_date, end_date):
        """Generate compliance audit report"""
        entries = self.query_audit_log(start_date, end_date)

        report = {
            'period': f"{start_date} to {end_date}",
            'total_events': len(entries),
            'events_by_type': Counter(e['event_type'] for e in entries),
            'events_by_user': Counter(e['user_email'] for e in entries),
            'events_by_template': Counter(e['template_id'] for e in entries),
            'success_rate': sum(e['success'] for e in entries) / len(entries) * 100
        }

        return report
```

Following these standards ensures consistent, high-quality, compliant document automation that serves clients effectively while protecting the firm and maintaining professional obligations.

# HotDocs Platform Reference

## Overview

HotDocs is a leading document automation platform designed for creating sophisticated automated document templates. It's widely used in legal practices, corporate legal departments, and government organizations.

## Platform Editions

### HotDocs Advance
- Cloud-based subscription service
- Browser-based template authoring
- Integrated interview and assembly
- REST API for integrations
- Multi-tenant architecture
- Built-in analytics and reporting

### HotDocs Developer
- Desktop-based template development
- Full-featured authoring environment
- On-premises deployment option
- Legacy integration support
- Advanced scripting capabilities

## Core Components

### Template Files (.hdtt, .hdt)
- Binary template format
- Contains document structure and logic
- Supports DOCX, PDF, and RTF output
- Version-controlled through HotDocs

### Component Files (.hdc, .hdxml)
- Variable definitions and metadata
- Interview structure
- Computation scripts
- Reusable across templates

### Answer Files (.hda, .hdxml)
- Stores user responses
- Can be used for pre-filling
- Enables save/resume functionality
- JSON or XML format in Advance

## Variable Types

### Text Variables
```
TEXT Name
TEXT Address
TEXT Email
```

### Number Variables
```
NUMBER Age
NUMBER Income
NUMBER Percentage RANGE 0 TO 100
```

### Date Variables
```
DATE Hire Date
DATE Termination Date
DATE Birth Date FORMAT "MM/DD/YYYY"
```

### True/False Variables
```
TRUE/FALSE Is Married
TRUE/FALSE Has Children
TRUE/FALSE Owns Property
```

### Multiple Choice Variables
```
MULTIPLE CHOICE State
  Option 1: California
  Option 2: New York
  Option 3: Texas
END MULTIPLE CHOICE
```

### Repeated Dialogs
```
DIALOG Children [REPEAT]
  TEXT Child Name
  DATE Child Birth Date
  TRUE/FALSE Child Is Minor
END DIALOG
```

## Conditional Logic

### IF Statements in Templates
```
«IF Is Married»
Spouse Name: «Spouse Name»
Marriage Date: «Marriage Date»
«END IF»
```

### Nested Conditions
```
«IF Employment Status = "Employed"»
  Employer: «Employer Name»
  «IF Has Benefits»
    Benefits: «Benefits Description»
  «END IF»
«END IF»
```

### ELSE Clauses
```
«IF Entity Type = "Corporation"»
  This Corporation
«ELSE IF Entity Type = "LLC"»
  This Limited Liability Company
«ELSE»
  This Entity
«END IF»
```

## Computation Scripts

### DIALOG Scripts
```
DIALOG Client Information
  TEXT First Name
  TEXT Last Name
  COMPUTATION Full Name
    SET Full Name TO First Name + " " + Last Name
  END COMPUTATION
END DIALOG
```

### Complex Calculations
```
COMPUTATION Tax Calculation
  SET Federal Tax TO Income * 0.22
  SET State Tax TO Income * 0.05
  SET Total Tax TO Federal Tax + State Tax

  IF Income > 100000
    SET AMT TO (Income - 100000) * 0.26
    IF AMT > Total Tax
      SET Total Tax TO AMT
    END IF
  END IF
END COMPUTATION
```

### Date Computations
```
COMPUTATION Contract Dates
  SET Start Date TO TODAY
  SET End Date TO Start Date + 365 DAYS
  SET Notice Date TO End Date - 30 DAYS
END COMPUTATION
```

## Interview Customization

### Interview Hierarchy
- Organize questions in logical groups
- Use nested dialogs for related questions
- Implement progressive disclosure
- Show/hide based on previous answers

### Custom Interview Scripts (JavaScript)
```javascript
// Set default values
HotDocs.setAnswer('State', 'California');

// Conditional display
if (HotDocs.getAnswer('Entity Type') === 'Corporation') {
    HotDocs.showDialog('Corporate Information');
}

// Validation
if (HotDocs.getAnswer('Age') < 18) {
    HotDocs.showMessage('Must be 18 or older');
    return false;
}
```

### Interview Resources
- Custom help text and tooltips
- Example answers
- Warning messages
- Resource items for reusable text

## Output Formats

### Microsoft Word (DOCX)
- Full formatting support
- Tables and lists
- Headers and footers
- Page numbering
- Track changes compatible

### PDF
- Fixed layout
- Digital signatures
- Form fields
- Bookmarks and TOC
- PDF/A for archival

### RTF (Rich Text Format)
- Cross-platform compatibility
- Basic formatting
- Legacy system support

## Integration Capabilities

### HotDocs Advance API
```
POST /api/rest/v1.0/interviews
POST /api/rest/v1.0/assemble
GET /api/rest/v1.0/templates
PUT /api/rest/v1.0/answers
```

### Authentication
- OAuth 2.0
- API keys
- SAML SSO

### Webhooks
- Template published
- Assembly completed
- Interview started/completed
- Error notifications

## Best Practices

### Template Organization
1. Use consistent naming conventions
2. Modularize reusable components
3. Document complex logic
4. Version control all files
5. Maintain a component library

### Performance Optimization
1. Minimize computation complexity
2. Use caching where appropriate
3. Optimize repeat dialog usage
4. Limit external data calls
5. Test with realistic data volumes

### Security
1. Role-based access control
2. Encrypt answer files
3. Audit template access
4. Secure API credentials
5. Regular security updates

## Common Patterns

### Optional Sections
```
«IF Include Arbitration Clause»
ARBITRATION
«Arbitration Text»
«END IF»
```

### Numbered Lists
```
«REPEAT FOR EACH Obligation»
  «Counter». «Obligation Text»
«END REPEAT»
```

### Table Generation
```
| Name | Date | Amount |
«REPEAT FOR EACH Payment»
| «Payment Name» | «Payment Date» | «Payment Amount» |
«END REPEAT»
```

### Document Assembly Chain
```
COMPUTATION Document Set
  ASSEMBLE "Cover Letter"
  ASSEMBLE "Main Agreement"
  IF Include Exhibits
    ASSEMBLE "Exhibit A"
    ASSEMBLE "Exhibit B"
  END IF
END COMPUTATION
```

## Troubleshooting

### Common Issues
- Variable scope conflicts
- Circular computation references
- Date format inconsistencies
- Repeat dialog index errors
- Memory issues with large templates

### Debugging Tools
- Template tester
- Computation debugger
- Interview preview
- Log files review
- Answer file inspection

## Version Control

### Template Versioning
- Maintain version numbers in component properties
- Document changes in release notes
- Test backwards compatibility with old answer files
- Archive deprecated templates
- Implement rollback procedures

## Resources

- **Official Documentation**: https://help.hotdocs.com
- **Developer Community**: HotDocs Developer Forums
- **Training**: HotDocs University courses
- **Support**: HotDocs Technical Support
- **API Reference**: HotDocs Advance API documentation

## Licensing

- Named user licensing
- Concurrent user licensing
- Template-based licensing (Advance)
- Developer licensing
- Enterprise agreements

## Migration Considerations

### Moving to HotDocs Advance
1. Convert desktop templates to Advance format
2. Update integration code for REST API
3. Migrate answer files to new format
4. Retrain users on browser interface
5. Update deployment architecture

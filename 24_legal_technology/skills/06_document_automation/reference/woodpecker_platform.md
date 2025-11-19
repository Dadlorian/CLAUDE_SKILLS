# Woodpecker Platform Reference

## Overview

Woodpecker is a Microsoft Word-based document automation platform designed for legal professionals who want to automate document creation while staying within the familiar Word environment. It provides powerful automation capabilities without requiring users to learn complex programming languages.

## Platform Components

### Woodpecker for Word
- Microsoft Word add-in
- Ribbon-based interface
- Template authoring tools
- Testing and preview capabilities
- Field library management

### Woodpecker Server
- Centralized template repository
- User access control
- Document assembly engine
- Integration APIs
- Usage analytics

### Woodpecker Portal
- Web-based questionnaire interface
- Client-facing forms
- Document delivery system
- Mobile-responsive design

## Template Development

### Field Types

#### Text Fields
```
[[Client Name]]                    // Simple text
[[Address|multiline]]              // Multi-line text
[[Email|email]]                    // Email validation
[[Phone|phone]]                    // Phone formatting
[[SSN|mask:***-**-####]]          // Masked input
```

#### Date Fields
```
[[Effective Date|date]]
[[Birth Date|date:MM/DD/YYYY]]
[[Contract End|date|required]]
[[Today|date|auto:today]]
```

#### Number Fields
```
[[Purchase Price|number:currency]]
[[Interest Rate|number:percent:2]]
[[Quantity|number:integer]]
[[Decimal Value|number:decimal:3]]
```

#### Choice Fields
```
[[State|dropdown:CA,NY,TX,FL]]
[[Entity Type|radio:Corporation,LLC,Partnership]]
[[Services|checkbox:Legal,Accounting,Consulting]]
```

#### Calculated Fields
```
[[Total Amount|calc:=Purchase Price + Fees]]
[[Monthly Payment|calc:=Principal * Interest Rate / 12]]
[[Full Name|calc:=First Name & " " & Last Name]]
```

### Conditional Content

#### Simple IF Statements
```
{{IF [[Marital Status]] = "Married"}}
Spouse Information:
Name: [[Spouse Name]]
Date of Marriage: [[Marriage Date]]
{{ENDIF}}
```

#### IF-ELSE Statements
```
{{IF [[Entity Type]] = "Corporation"}}
This Corporation, a [[State of Incorporation]] corporation
{{ELSE}}
This [[Entity Type]], organized under the laws of [[State]]
{{ENDIF}}
```

#### Nested Conditions
```
{{IF [[Entity Type]] = "Corporation"}}
  {{IF [[Public Or Private]] = "Public"}}
    SEC Registration Number: [[SEC Number]]
    Stock Symbol: [[Stock Symbol]]
  {{ELSE}}
    This is a privately held corporation
  {{ENDIF}}
{{ENDIF}}
```

#### Complex Conditions
```
{{IF [[Annual Revenue]] > 1000000 AND [[Number of Employees]] > 50}}
This company qualifies as a large business enterprise
{{ENDIF}}

{{IF [[State]] IN ["CA", "NY", "MA"] AND [[Industry]] = "Healthcare"}}
Additional state-specific healthcare regulations apply
{{ENDIF}}
```

### Repeating Sections

#### Simple List
```
{{REPEAT [[Shareholder]]}}
[[Counter]]. [[Shareholder Name]]
   Shares Owned: [[Shares Owned]]
   Ownership Percentage: [[Ownership Percentage]]%
{{ENDREPEAT}}
```

#### Table Format
```
{TABLE:START}
| Name | Date | Amount |
{{REPEAT [[Payment]]}}
| [[Payment Name]] | [[Payment Date]] | [[Payment Amount]] |
{{ENDREPEAT}}
{TABLE:END}
```

#### Nested Repeating Sections
```
{{REPEAT [[Department]]}}
Department: [[Department Name]]
Manager: [[Department Manager]]

  {{REPEAT [[Employee]] IN [[Department]]}}
  - [[Employee Name]], [[Employee Title]]
  {{ENDREPEAT}}
{{ENDREPEAT}}
```

#### Repeating with Minimum/Maximum
```
{{REPEAT [[Beneficiary]] MIN:1 MAX:5}}
Beneficiary [[Counter]]:
  Name: [[Beneficiary Name]]
  Relationship: [[Beneficiary Relationship]]
  Percentage: [[Beneficiary Percentage]]%
{{ENDREPEAT}}
```

### Calculations and Formulas

#### Mathematical Operations
```
[[Total|calc:=Item1 + Item2 + Item3]]
[[Average|calc:=(Value1 + Value2 + Value3) / 3]]
[[Interest|calc:=Principal * Rate * Time]]
[[Percentage|calc:=(Part / Whole) * 100]]
```

#### Date Calculations
```
[[Contract End|calc:=Contract Start + 365 days]]
[[Notice Deadline|calc:=Termination Date - 30 days]]
[[Age|calc:=YEARS(Birth Date, Today)]]
[[Anniversary|calc:=DATE(YEAR(Today) + 1, MONTH(Start Date), DAY(Start Date))]]
```

#### Text Functions
```
[[Upper Name|calc:=UPPER(Client Name)]]
[[Initials|calc:=LEFT(First Name, 1) & LEFT(Last Name, 1)]]
[[Formatted Phone|calc:="(" & Area Code & ") " & Exchange & "-" & Number]]
```

#### Conditional Calculations
```
[[Discount|calc:=IF(Order Amount > 10000, Order Amount * 0.1, 0)]]
[[Tax Rate|calc:=IF(State = "CA", 0.0725, IF(State = "NY", 0.08, 0.06))]]
[[Final Price|calc:=Base Price - Discount + (Base Price * Tax Rate)]]
```

#### Aggregate Functions (in Repeating Sections)
```
[[Total Shares|calc:=SUM(Shares Owned)]]
[[Average Salary|calc:=AVERAGE(Employee Salary)]]
[[Max Value|calc:=MAX(Contract Values)]]
[[Count Employees|calc:=COUNT(Employee)]]
```

### Field Properties

#### Validation Rules
```
[[Email|validate:email]]
[[Website|validate:url]]
[[Zip Code|validate:regex:^\d{5}(-\d{4})?$]]
[[Contract Value|validate:range:1000-10000000]]
```

#### Formatting
```
[[Purchase Price|format:currency:USD]]
[[Interest Rate|format:percent:2]]
[[Effective Date|format:date:MMMM DD, YYYY]]
[[Phone|format:phone:(###) ###-####]]
```

#### Default Values
```
[[State|default:California]]
[[Effective Date|default:TODAY]]
[[Interest Rate|default:5.5]]
[[Notice Period|default:30]]
```

#### Help Text
```
[[Client Name|help:Enter the client's full legal name]]
[[Tax ID|help:Enter EIN in format 12-3456789]]
[[Revenue|help:Enter annual revenue in whole dollars]]
```

## Questionnaire Design

### Multi-Page Forms
```xml
<questionnaire>
  <page id="page1" title="Basic Information">
    <section title="Client Details">
      <field ref="Client Name" required="true" />
      <field ref="Client Email" required="true" />
      <field ref="Client Phone" required="true" />
    </section>
  </page>

  <page id="page2" title="Matter Information">
    <section title="Case Details">
      <field ref="Matter Type" required="true" />
      <field ref="Matter Description" />
    </section>
  </page>

  <page id="review" title="Review & Submit">
    <review-page show-all-fields="true" />
  </page>
</questionnaire>
```

### Conditional Pages
```xml
<page id="corporate_info" title="Corporate Information">
  <condition>
    <field ref="Entity Type" operator="equals" value="Corporation" />
  </condition>

  <section title="Corporation Details">
    <field ref="State of Incorporation" required="true" />
    <field ref="Date of Incorporation" required="true" />
    <field ref="Stock Information" />
  </section>
</page>
```

### Field Dependencies
```xml
<field ref="State of Incorporation">
  <show-when>
    <field ref="Entity Type" operator="equals" value="Corporation" />
  </show-when>
  <required-when>
    <field ref="Entity Type" operator="equals" value="Corporation" />
  </required-when>
</field>

<field ref="Spouse Name">
  <show-when>
    <field ref="Marital Status" operator="equals" value="Married" />
  </show-when>
</field>
```

### Custom Validation Messages
```xml
<field ref="Contract Value">
  <validation type="range" min="1000" max="10000000">
    <error-message>Contract value must be between $1,000 and $10,000,000</error-message>
  </validation>
</field>

<field ref="Email">
  <validation type="email">
    <error-message>Please enter a valid email address</error-message>
  </validation>
</field>

<custom-validation>
  <condition>
    <field ref="End Date" operator="less-than-or-equal" field-ref="Start Date" />
  </condition>
  <error-message>End date must be after start date</error-message>
</custom-validation>
```

## Advanced Features

### Document Assembly Chain
```
{{ASSEMBLE:Cover Letter}}
{{ASSEMBLE:Main Agreement}}
{{IF [[Include Exhibits]]}}
  {{ASSEMBLE:Exhibit A}}
  {{ASSEMBLE:Exhibit B}}
  {{IF [[Include Schedules]]}}
    {{ASSEMBLE:Schedule 1}}
    {{ASSEMBLE:Schedule 2}}
  {{ENDIF}}
{{ENDIF}}
```

### Clause Library Integration
```
{{INSERT CLAUSE:Force Majeure|Notice Period:[[Notice Period]]}}
{{INSERT CLAUSE:Confidentiality|Duration:[[Confidentiality Period]]}}
{{INSERT CLAUSE:Governing Law|Jurisdiction:[[Governing Law State]]}}

{{IF [[Include Arbitration]]}}
  {{INSERT CLAUSE:Arbitration|
    Arbitrator Count:[[Arbitrator Count]]|
    Arbitration Location:[[Arbitration City]]}}
{{ENDIF}}
```

### Cross-References
```
As defined in Section {{REF:Definitions}}, the term "Effective Date" means [[Effective Date]].

See Exhibit {{REF:Financial Statements}} for detailed financial information.

The parties' obligations under Section {{REF:Payment Terms}} shall survive termination.
```

### Automatic Numbering
```
{{AUTO NUMBER:Section|format:1.}}
{{AUTO NUMBER:Subsection|format:1.1|parent:Section}}
{{AUTO NUMBER:Paragraph|format:(a)|parent:Subsection}}

{{NUMBER RESET:Section}}  // Reset counter
```

### Table of Contents
```
{{TOC:START|title:Table of Contents|levels:3}}
// Automatically generates TOC based on headings
{{TOC:END}}
```

## Integration Capabilities

### Microsoft Office Integration
```javascript
// Word add-in integration
Woodpecker.Office.openDocument(templateId);
Woodpecker.Office.populateFields(answerData);
Woodpecker.Office.generateDocument();

// Excel data import
Woodpecker.importFromExcel({
  file: 'data.xlsx',
  sheet: 'Clients',
  mapping: {
    'Column A': 'Client Name',
    'Column B': 'Client Email',
    'Column C': 'Matter Type'
  }
});

// Outlook integration
Woodpecker.Outlook.sendDocument({
  to: '[[Client Email]]',
  subject: 'Your [[Document Type]]',
  body: 'Please find your document attached.',
  attachments: [generatedDocument]
});
```

### Practice Management Integration
```javascript
// Clio integration
Woodpecker.Clio.getMatterData(matterId)
  .then(matter => {
    populateFields({
      'Client Name': matter.client.name,
      'Matter Number': matter.number,
      'Matter Description': matter.description
    });
  });

// MyCase integration
Woodpecker.MyCase.createDocument({
  caseId: caseId,
  document: generatedDocument,
  documentType: 'Agreement'
});
```

### API Integration
```javascript
// REST API
POST /api/v1/assemble
{
  "templateId": "template-123",
  "answers": {
    "Client Name": "Acme Corporation",
    "Entity Type": "Corporation",
    "State": "Delaware"
  },
  "outputFormat": "docx"
}

// Response
{
  "documentId": "doc-456",
  "downloadUrl": "https://server.com/download/doc-456",
  "expiresAt": "2025-12-31T23:59:59Z"
}
```

### Webhook Notifications
```javascript
// Configure webhook
{
  "event": "document.generated",
  "url": "https://yourapp.com/webhooks/woodpecker",
  "secret": "webhook-secret-key"
}

// Webhook payload
{
  "event": "document.generated",
  "timestamp": "2025-11-19T10:30:00Z",
  "documentId": "doc-456",
  "templateId": "template-123",
  "userId": "user-789",
  "metadata": {
    "Client Name": "Acme Corporation",
    "Matter Type": "Business Formation"
  }
}
```

## Security & Compliance

### Access Control
```xml
<template id="employment-agreement">
  <permissions>
    <role name="attorney" actions="read,write,assemble" />
    <role name="paralegal" actions="read,assemble" />
    <role name="admin" actions="read,write,assemble,delete" />
  </permissions>
</template>
```

### Audit Trail
```javascript
// Audit log entries
{
  "timestamp": "2025-11-19T10:30:00Z",
  "user": "john.smith@lawfirm.com",
  "action": "document.generated",
  "templateId": "template-123",
  "documentId": "doc-456",
  "ipAddress": "192.168.1.100",
  "metadata": {
    "Client Name": "Acme Corporation"
  }
}
```

### Data Encryption
- Documents encrypted at rest (AES-256)
- SSL/TLS for data in transit
- Encrypted answer file storage
- Secure credential management

## Best Practices

### Template Design
1. Use clear, descriptive field names
2. Organize fields in logical groups
3. Provide helpful field descriptions
4. Implement appropriate validation
5. Test with diverse data scenarios

### Performance
1. Minimize complex calculations in large documents
2. Use field caching where appropriate
3. Optimize repeating section queries
4. Compress large output files
5. Monitor template performance metrics

### Maintenance
1. Version control all templates
2. Document template logic and dependencies
3. Regular testing after updates
4. Archive obsolete templates
4. Maintain template change log

### User Training
1. Provide template-specific instructions
2. Create video tutorials for complex forms
3. Offer context-sensitive help
4. Conduct regular training sessions
5. Gather user feedback for improvements

## Troubleshooting

### Common Issues

**Field Not Populating**
- Check field name spelling
- Verify field is included in questionnaire
- Check conditional display logic
- Validate data type compatibility

**Calculation Errors**
- Verify formula syntax
- Check for circular references
- Ensure all referenced fields have values
- Validate data types in calculations

**Formatting Issues**
- Check document styles
- Verify paragraph formatting
- Test across Word versions
- Review table structure

**Performance Problems**
- Simplify complex calculations
- Reduce repeating section complexity
- Optimize template size
- Check server resources

## Resources

- **User Guide**: Woodpecker Documentation Portal
- **Video Tutorials**: Woodpecker YouTube Channel
- **Support**: support@woodpecker.com
- **Community Forum**: Woodpecker User Community
- **Training**: Woodpecker Academy

# Contract Express Platform Reference

## Overview

Contract Express (now part of Thomson Reuters) is an enterprise document automation platform designed for creating, managing, and assembling complex legal documents. It integrates tightly with Microsoft Word and offers strong Salesforce integration capabilities.

## Platform Architecture

### Contract Express Author
- Microsoft Word add-in for template development
- Visual logic builder
- Template testing and preview
- Component library management
- Version control integration

### Contract Express Publisher
- Template deployment platform
- User access management
- Template organization and categorization
- Analytics and usage reporting
- Integration hub

### Contract Express Online
- Cloud-based execution environment
- Browser-based questionnaires
- Document assembly and download
- Collaboration features
- Mobile-responsive interface

## Template Development

### Template Structure
```
Document Template (.docx)
  ├── Field Definitions
  ├── Conditional Logic
  ├── Clause Library References
  ├── Styles and Formatting
  └── Metadata
```

### Field Types

#### Text Fields
```xml
<!-- Simple text field -->
<field name="CompanyName" type="text" />

<!-- Multi-line text -->
<field name="Description" type="textarea" rows="5" />

<!-- Rich text with formatting -->
<field name="CustomClause" type="richtext" />
```

#### Choice Fields
```xml
<!-- Single selection -->
<field name="EntityType" type="choice">
  <option value="Corp">Corporation</option>
  <option value="LLC">Limited Liability Company</option>
  <option value="LP">Limited Partnership</option>
</field>

<!-- Multiple selection -->
<field name="Jurisdictions" type="multichoice">
  <option value="CA">California</option>
  <option value="NY">New York</option>
  <option value="TX">Texas</option>
</field>
```

#### Date Fields
```xml
<field name="EffectiveDate" type="date" format="MM/DD/YYYY" />
<field name="ExpirationDate" type="date" minDays="30" />
```

#### Number Fields
```xml
<field name="PurchasePrice" type="number" format="currency" />
<field name="Shares" type="number" format="integer" min="1" />
<field name="InterestRate" type="number" format="percentage" decimal="2" />
```

### Conditional Logic with JavaScript

#### Basic Conditions
```javascript
// Show/hide content based on field value
if (EntityType == "Corp") {
    show("CorporateProvisions");
} else {
    hide("CorporateProvisions");
}

// Required field validation
if (EntityType == "Corp" && !StateOfIncorporation) {
    setRequired("StateOfIncorporation", true);
    setError("StateOfIncorporation", "Required for corporations");
}
```

#### Complex Business Logic
```javascript
// Calculate total consideration
function calculateTotalConsideration() {
    var cash = parseFloat(CashPayment) || 0;
    var stock = parseFloat(StockValue) || 0;
    var earnout = parseFloat(EarnoutAmount) || 0;

    TotalConsideration = cash + stock + earnout;

    // Format as currency
    TotalConsiderationFormatted = "$" + TotalConsideration.toLocaleString();
}

// Trigger calculation when any component changes
onFieldChange("CashPayment", calculateTotalConsideration);
onFieldChange("StockValue", calculateTotalConsideration);
onFieldChange("EarnoutAmount", calculateTotalConsideration);
```

#### Date Calculations
```javascript
// Calculate contract end date
var startDate = new Date(ContractStartDate);
var termMonths = parseInt(ContractTerm);
var endDate = new Date(startDate);
endDate.setMonth(endDate.getMonth() + termMonths);

ContractEndDate = formatDate(endDate, "MM/DD/YYYY");

// Calculate notice deadline
var noticeDate = new Date(endDate);
noticeDate.setDate(noticeDate.getDate() - 90); // 90 days before end
NoticeDeadline = formatDate(noticeDate, "MM/DD/YYYY");
```

### Clause Library Management

#### Standard Clause Structure
```xml
<clause id="ForceMajeure" category="General Provisions">
  <title>Force Majeure</title>
  <description>Standard force majeure provision</description>
  <parameters>
    <param name="NoticePeriod" type="number" default="5" />
    <param name="IncludeEpidemics" type="boolean" default="true" />
  </parameters>
  <content>
    <!-- Clause text with variables -->
  </content>
</clause>
```

#### Dynamic Clause Selection
```javascript
// Add clauses based on transaction type
if (TransactionType == "Stock Purchase") {
    includeClause("RepresentationsWarrantiesStock");
    includeClause("StockCertificates");
} else if (TransactionType == "Asset Purchase") {
    includeClause("RepresentationsWarrantiesAssets");
    includeClause("AssetSchedule");
}

// Optional clauses based on user selection
if (IncludeNonCompete) {
    includeClause("NonCompeteProvision", {
        duration: NonCompeteDuration,
        territory: NonCompeteTerritory
    });
}
```

### Repeating Sections

#### Table Rows
```javascript
// Define repeating structure
var shareholders = createRepeatGroup("Shareholder");

shareholders.addFields([
    { name: "ShareholderName", type: "text" },
    { name: "ShareholderAddress", type: "text" },
    { name: "SharesOwned", type: "number" },
    { name: "ShareholderPercentage", type: "number" }
]);

// Calculate percentage automatically
shareholders.onFieldChange("SharesOwned", function(index) {
    var totalShares = getTotalShares();
    var owned = shareholders.getValue(index, "SharesOwned");
    var percentage = (owned / totalShares) * 100;
    shareholders.setValue(index, "ShareholderPercentage", percentage.toFixed(2));
});
```

#### Nested Repeating Groups
```javascript
// Schedules with line items
var schedules = createRepeatGroup("Schedule");
schedules.addFields([
    { name: "ScheduleTitle", type: "text" },
    { name: "ScheduleDescription", type: "textarea" }
]);

// Nested items within each schedule
schedules.addNestedRepeatGroup("LineItem", [
    { name: "ItemDescription", type: "text" },
    { name: "ItemValue", type: "number" }
]);
```

## Questionnaire Design

### Interview Flow Control
```javascript
// Multi-page questionnaire
var interview = createInterview("ContractInterview");

// Page 1: Basic Information
interview.addPage("BasicInfo", {
    title: "Basic Information",
    fields: ["CompanyName", "EntityType", "State"],
    onComplete: validateBasicInfo
});

// Page 2: Conditional based on entity type
if (EntityType == "Corp") {
    interview.addPage("CorporateInfo", {
        title: "Corporate Information",
        fields: ["StateOfIncorporation", "CorporationNumber"],
        condition: function() { return EntityType == "Corp"; }
    });
}

// Navigation logic
interview.setNavigation({
    allowBack: true,
    allowSave: true,
    showProgress: true
});
```

### Field Validation
```javascript
// Custom validation rules
validation.addRule("Email", function(value) {
    var regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!regex.test(value)) {
        return "Please enter a valid email address";
    }
    return true;
});

validation.addRule("PurchasePrice", function(value) {
    if (value < 0) {
        return "Purchase price must be positive";
    }
    if (value > 1000000 && !BoardApprovalObtained) {
        return "Board approval required for amounts over $1,000,000";
    }
    return true;
});

// Cross-field validation
validation.addCrossFieldRule(["StartDate", "EndDate"], function(values) {
    var start = new Date(values.StartDate);
    var end = new Date(values.EndDate);

    if (end <= start) {
        return "End date must be after start date";
    }
    return true;
});
```

## Salesforce Integration

### Object Mapping
```javascript
// Map Salesforce objects to template fields
salesforce.mapObject("Account", {
    "Name": "CompanyName",
    "BillingStreet": "CompanyAddress",
    "BillingCity": "CompanyCity",
    "BillingState": "CompanyState",
    "BillingPostalCode": "CompanyZip"
});

salesforce.mapObject("Opportunity", {
    "Amount": "ContractValue",
    "CloseDate": "ExpectedCloseDate",
    "StageName": "DealStage"
});

// Custom object mapping
salesforce.mapObject("Contract__c", {
    "Term__c": "ContractTerm",
    "Renewal_Type__c": "RenewalType",
    "Governing_Law__c": "GoverningLaw"
});
```

### Data Retrieval
```javascript
// Query Salesforce data
salesforce.query("SELECT Name, Title, Email FROM Contact WHERE AccountId = :accountId")
    .then(function(contacts) {
        // Populate repeating section with contacts
        contacts.forEach(function(contact) {
            addRepeatInstance("Contact", {
                ContactName: contact.Name,
                ContactTitle: contact.Title,
                ContactEmail: contact.Email
            });
        });
    });

// Retrieve related records
salesforce.getRelatedRecords("Opportunity", "OpportunityLineItems")
    .then(function(lineItems) {
        populateProductTable(lineItems);
    });
```

### Document Upload
```javascript
// Upload assembled document to Salesforce
function uploadToSalesforce(documentBuffer, recordId) {
    salesforce.uploadFile({
        fileName: CompanyName + " - Agreement.docx",
        contentType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        body: documentBuffer,
        parentId: recordId,
        description: "Generated contract document"
    }).then(function(result) {
        console.log("Document uploaded: " + result.id);
        // Update opportunity stage
        salesforce.updateRecord("Opportunity", recordId, {
            StageName: "Contract Sent",
            Contract_Sent_Date__c: new Date()
        });
    });
}
```

## API Integration

### REST API Endpoints
```
POST /api/v1/assembly/start
POST /api/v1/assembly/answer
POST /api/v1/assembly/complete
GET /api/v1/templates
GET /api/v1/templates/{id}
POST /api/v1/templates/{id}/assemble
```

### Assembly API Example
```javascript
// Start document assembly
const response = await fetch('https://api.contractexpress.com/api/v1/assembly/start', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer ' + apiToken,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        templateId: 'template-123',
        answers: {
            CompanyName: 'Acme Corporation',
            EntityType: 'Corp',
            State: 'Delaware'
        }
    })
});

const assembly = await response.json();
const assemblyId = assembly.id;

// Complete assembly and download document
const docResponse = await fetch(`https://api.contractexpress.com/api/v1/assembly/${assemblyId}/complete`, {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer ' + apiToken
    }
});

const documentBlob = await docResponse.blob();
```

## Advanced Features

### Document Comparison
```javascript
// Compare two versions of a document
contractExpress.compareDocuments({
    original: originalDocumentId,
    revised: revisedDocumentId,
    options: {
        showFormatting: true,
        showComments: true,
        compareType: 'detailed'
    }
}).then(function(comparison) {
    // Display redline comparison
    displayComparison(comparison.redlineDocument);
});
```

### Workflow Automation
```javascript
// Multi-step approval workflow
var workflow = createWorkflow("ContractApproval");

workflow.addStep("LegalReview", {
    assignTo: "legal-team@company.com",
    dueInDays: 2,
    onApprove: function() {
        notifyNextReviewer("FinanceReview");
    },
    onReject: function(comments) {
        notifyOriginator(comments);
    }
});

workflow.addStep("FinanceReview", {
    assignTo: "finance-team@company.com",
    dueInDays: 1,
    condition: function() { return ContractValue > 50000; },
    onApprove: function() {
        finalizeDocument();
    }
});
```

### Electronic Signatures
```javascript
// DocuSign integration
contractExpress.sendForSignature({
    provider: 'DocuSign',
    document: assembledDocument,
    signers: [
        {
            name: CompanySignerName,
            email: CompanySignerEmail,
            role: 'Company',
            tabs: {
                signHereTabs: [{ page: 5, x: 100, y: 200 }],
                dateSignedTabs: [{ page: 5, x: 300, y: 200 }]
            }
        },
        {
            name: CounterpartySignerName,
            email: CounterpartySignerEmail,
            role: 'Counterparty',
            tabs: {
                signHereTabs: [{ page: 5, x: 100, y: 300 }],
                dateSignedTabs: [{ page: 5, x: 300, y: 300 }]
            }
        }
    ],
    callbackUrl: 'https://yourapp.com/api/signature-callback'
});
```

## Best Practices

### Template Design
1. Use consistent naming conventions for fields
2. Organize related fields into logical groups
3. Implement progressive disclosure for complex questionnaires
4. Provide helpful field descriptions and examples
5. Use default values where appropriate

### Performance
1. Minimize complex calculations in loops
2. Cache frequently accessed Salesforce data
3. Optimize clause library queries
4. Use async operations for external API calls
5. Implement pagination for large datasets

### Testing
1. Test with diverse data scenarios
2. Validate all conditional logic paths
3. Check document formatting across versions of Word
4. Test Salesforce integration thoroughly
5. Perform load testing for high-volume scenarios

### Security
1. Use role-based access control for templates
2. Encrypt sensitive data in transit and at rest
3. Implement audit logging for document generation
4. Follow principle of least privilege for API access
5. Regular security assessments

## Resources

- **Documentation**: Thomson Reuters Contract Express Help Center
- **Training**: Contract Express University
- **Community**: Contract Express User Forums
- **Support**: Thomson Reuters Technical Support
- **API Docs**: Contract Express Developer Portal

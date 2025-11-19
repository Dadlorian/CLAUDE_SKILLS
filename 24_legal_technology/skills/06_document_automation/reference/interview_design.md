# Interview Design Best Practices

## Overview

The interview (questionnaire) is the user-facing component of document automation. Effective interview design ensures accurate data collection, positive user experience, and successful document generation.

## Core Principles

### 1. User-Centric Design
- Design for your specific audience (attorneys, paralegals, clients)
- Match complexity to user sophistication
- Provide appropriate guidance and help
- Minimize cognitive load

### 2. Progressive Disclosure
- Show only relevant questions
- Break complex forms into manageable sections
- Reveal advanced options conditionally
- Guide users through logical flow

### 3. Clear Communication
- Use plain language for client-facing interviews
- Use precise legal terminology for attorney interviews
- Provide examples and help text
- Give clear error messages

### 4. Efficient Data Collection
- Minimize number of questions
- Use smart defaults
- Enable data reuse
- Support save and resume

## Interview Structure

### Multi-Page Organization

```
Page 1: Introduction
  - Welcome message
  - Instructions
  - Estimated time
  - Privacy notice

Page 2: Basic Information
  - Client/matter identification
  - Contact information
  - Required: Yes

Page 3-N: Specific Questions
  - Grouped by topic
  - Progressive disclosure
  - Conditional pages

Final Page: Review and Submit
  - Summary of answers
  - Edit links
  - Final confirmation
```

### Section Grouping

```yaml
Matter Intake Interview:

  Section: Client Information
    - Client name
    - Contact details
    - Entity information (if business)

  Section: Matter Details
    - Matter type
    - Matter description
    - Opposing party (if applicable)
    - Key dates

  Section: Conflict Check
    - Related parties
    - Related matters
    - Potential conflicts

  Section: Engagement Terms
    - Fee arrangement
    - Scope of representation
    - Terms acceptance
```

### Page Flow Logic

```
Start
  ↓
Introduction → Basic Info → Matter Type Selection
                               ↓
                        ┌──────┴──────┬──────────┬─────────┐
                        ↓             ↓          ↓         ↓
                   Litigation    Business    Estate    Real Estate
                        ↓             ↓          ↓         ↓
                   Lit Details   Corp Details  Estate  Property
                        └──────┬──────┴──────────┴─────────┘
                               ↓
                        Review & Submit
```

## Question Design

### Field Labels

**Good Labels**:
```
Client's Full Legal Name
Contract Effective Date
Annual Revenue (USD)
State of Incorporation
```

**Poor Labels**:
```
Name (too vague)
Date (which date?)
Amount (what amount?)
State (which state?)
```

### Help Text and Examples

```yaml
Field: Purchase Price
  Label: "Purchase Price"
  Help: "Enter the total purchase price in US dollars"
  Example: "5,000,000 for $5M purchase"
  Tooltip: "This is the base purchase price, excluding any earnout or contingent payments"

Field: Entity Type
  Label: "Type of Business Entity"
  Help: "Select the legal structure of your business"
  Options with descriptions:
    - Corporation: "A separate legal entity owned by shareholders"
    - LLC: "Flexible structure combining corporate liability protection with partnership taxation"
    - Partnership: "Two or more owners sharing profits and liability"
```

### Input Methods

**Text Input**: Simple text fields
```
Use for:
- Names
- Addresses
- Descriptions
- Custom text

Provide:
- Placeholder text
- Format examples
- Character limits
```

**Dropdowns**: Select from predefined list
```
Use for:
- States/countries
- Categories
- Standard options
- Long lists (>5 items)

Provide:
- Logical ordering
- Search capability (if long)
- "Other" option if needed
```

**Radio Buttons**: Mutually exclusive choices
```
Use for:
- 2-5 options
- Mutually exclusive
- Visually scannable choices

Example:
○ Individual
○ Business Entity
○ Trust
```

**Checkboxes**: Multiple selections
```
Use for:
- Multi-select options
- Boolean flags
- Feature selection

Example:
Services Requested:
☐ Estate Planning
☐ Business Formation
☐ Contract Review
☐ Litigation Support
```

**Date Pickers**: Calendar selection
```
Use for:
- All date fields
- Prevent format errors
- Enable date validation

Provide:
- Minimum/maximum dates
- Default to today (if appropriate)
- Clear format display
```

**Number Inputs**: Numeric data
```
Use for:
- Currency amounts
- Quantities
- Percentages

Provide:
- Min/max ranges
- Format hints
- Increment buttons (if appropriate)
```

**Text Areas**: Multi-line text
```
Use for:
- Descriptions
- Notes
- Custom provisions
- Long text content

Provide:
- Visible size (rows)
- Character/word count
- Optional formatting tools
```

## Conditional Display

### Show/Hide Logic

```javascript
// Show spouse fields only if married
if (marital_status === "Married") {
  show("spouse_section");
} else {
  hide("spouse_section");
}

// Show corporation fields for corporate entities
if (entity_type === "Corporation") {
  show("state_of_incorporation");
  show("corporation_number");
  show("stock_information");
}

// Show earnout section if earnout included
if (include_earnout === true) {
  show("earnout_amount");
  show("earnout_terms");
  show("earnout_schedule");
}
```

### Required Field Logic

```javascript
// Corporation name required if entity type is corporation
if (entity_type === "Corporation") {
  setRequired("corporation_name", true);
  setRequired("state_of_incorporation", true);
} else {
  setRequired("corporation_name", false);
  setRequired("state_of_incorporation", false);
}

// Board approval required for high-value transactions
if (purchase_price > 5000000) {
  setRequired("board_approval_date", true);
  show("board_approval_section");
}
```

### Page Navigation Logic

```javascript
// Skip entity details if individual client
if (client_type === "Individual") {
  skipPage("entity_details");
  goToPage("individual_details");
}

// Go to specific pages based on matter type
switch(matter_type) {
  case "Litigation":
    goToPage("litigation_details");
    break;
  case "Business Formation":
    goToPage("entity_formation_details");
    break;
  case "Real Estate":
    goToPage("property_details");
    break;
}
```

## Progress Indicators

### Progress Bar
```html
<div class="progress-bar">
  <div class="progress" style="width: 60%"></div>
</div>
<p>Page 3 of 5 - 60% Complete</p>
```

### Step Indicator
```
1. Basic Info ✓
2. Matter Details ✓
3. Financial Information ← You are here
4. Additional Details
5. Review & Submit
```

### Section Completion
```
Client Information          ✓ Complete
Matter Details             ✓ Complete
Entity Information         ⚠ In Progress (2 of 5 fields)
Conflict Check             ○ Not Started
Engagement Terms           ○ Not Started
```

## Validation and Error Handling

### Real-Time Validation

```javascript
// Email validation
email.addEventListener('blur', function() {
  if (!isValidEmail(this.value)) {
    showError(this, "Please enter a valid email address");
  } else {
    clearError(this);
  }
});

// Numeric range validation
purchase_price.addEventListener('input', function() {
  const value = parseFloat(this.value);
  if (value < 0) {
    showError(this, "Purchase price must be positive");
  } else if (value > 1000000000) {
    showWarning(this, "Large transaction may require additional review");
  } else {
    clearError(this);
  }
});

// Date validation
end_date.addEventListener('change', function() {
  if (new Date(this.value) <= new Date(start_date.value)) {
    showError(this, "End date must be after start date");
  } else {
    clearError(this);
  }
});
```

### Error Messages

**Good Error Messages**:
```
✓ "Email address must include @ symbol"
✓ "Purchase price must be between $1 and $1,000,000,000"
✓ "End date must be after start date (currently 11/15/2025)"
✓ "State of incorporation is required for corporations"
```

**Poor Error Messages**:
```
✗ "Invalid input"
✗ "Error"
✗ "Field required"
✗ "Wrong format"
```

### Error Display

```html
<!-- Inline errors -->
<div class="form-group error">
  <label for="email">Email Address *</label>
  <input type="email" id="email" class="error" value="invalid-email">
  <span class="error-message">Please enter a valid email address</span>
</div>

<!-- Summary errors at top of page -->
<div class="error-summary" role="alert">
  <h3>Please correct the following errors:</h3>
  <ul>
    <li><a href="#email">Email Address: Invalid format</a></li>
    <li><a href="#purchase_price">Purchase Price: Required field</a></li>
    <li><a href="#end_date">End Date: Must be after start date</a></li>
  </ul>
</div>
```

## Smart Defaults and Auto-Population

### Intelligent Defaults

```javascript
// Default to today's date for effective date
effective_date.value = new Date().toISOString().split('T')[0];

// Default state based on user location
state.value = getUserState(); // e.g., "CA"

// Default notice period to 30 days
notice_period_days.value = 30;

// Default governing law to primary state
governing_law.value = state.value;
```

### Auto-Population from Previous Data

```javascript
// Populate from previous matter
if (has_previous_matter) {
  client_name.value = previous_matter.client_name;
  client_email.value = previous_matter.client_email;
  client_phone.value = previous_matter.client_phone;
  // Mark as pre-filled
  markAsPreFilled([client_name, client_email, client_phone]);
}

// Populate from CRM
loadClientData(client_id).then(data => {
  client_name.value = data.name;
  client_address.value = data.address;
  client_email.value = data.email;
});
```

### Calculated Defaults

```javascript
// Calculate contract end date from start date and term
contract_start_date.addEventListener('change', updateEndDate);
contract_term_years.addEventListener('change', updateEndDate);

function updateEndDate() {
  if (contract_start_date.value && contract_term_years.value) {
    const start = new Date(contract_start_date.value);
    const years = parseInt(contract_term_years.value);
    const end = new Date(start.setFullYear(start.getFullYear() + years));
    contract_end_date.value = end.toISOString().split('T')[0];
  }
}

// Calculate ownership percentages
function updateOwnershipPercentages() {
  const total_shares = parseFloat(total_shares_input.value);
  shareholders.forEach(shareholder => {
    const shares = parseFloat(shareholder.shares_owned);
    shareholder.ownership_percentage = (shares / total_shares * 100).toFixed(2);
  });
}
```

## Save and Resume

### Auto-Save

```javascript
// Auto-save every 30 seconds
setInterval(saveProgress, 30000);

function saveProgress() {
  const formData = gatherFormData();
  localStorage.setItem('interview_draft_' + interview_id, JSON.stringify({
    data: formData,
    timestamp: new Date().toISOString(),
    page: current_page
  }));
  showSaveIndicator("Draft saved at " + new Date().toLocaleTimeString());
}

// Save on field change (debounced)
let saveTimeout;
document.querySelectorAll('input, select, textarea').forEach(field => {
  field.addEventListener('input', () => {
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(saveProgress, 3000);
  });
});
```

### Resume Session

```javascript
// Check for saved draft on load
window.addEventListener('load', function() {
  const draft = localStorage.getItem('interview_draft_' + interview_id);
  if (draft) {
    const savedData = JSON.parse(draft);
    const timestamp = new Date(savedData.timestamp);

    if (confirm(`Found a draft from ${timestamp.toLocaleString()}. Would you like to resume?`)) {
      restoreFormData(savedData.data);
      goToPage(savedData.page);
    }
  }
});
```

## Accessibility

### Keyboard Navigation

```html
<!-- Logical tab order -->
<input type="text" id="first_name" tabindex="1">
<input type="text" id="last_name" tabindex="2">
<input type="email" id="email" tabindex="3">

<!-- Skip to main content -->
<a href="#main-form" class="skip-link">Skip to form</a>

<!-- Keyboard-accessible custom controls -->
<div role="radiogroup" aria-labelledby="entity-type-label">
  <div role="radio" tabindex="0" aria-checked="false">Corporation</div>
  <div role="radio" tabindex="-1" aria-checked="false">LLC</div>
</div>
```

### Screen Reader Support

```html
<!-- Proper labels -->
<label for="client_name">Client Name <span aria-label="required">*</span></label>
<input type="text" id="client_name" required aria-required="true">

<!-- Descriptive help text -->
<label for="purchase_price" id="purchase_price_label">Purchase Price</label>
<input
  type="number"
  id="purchase_price"
  aria-labelledby="purchase_price_label"
  aria-describedby="purchase_price_help"
>
<div id="purchase_price_help">Enter the purchase price in US dollars</div>

<!-- Error announcements -->
<div role="alert" aria-live="assertive">
  Please correct 3 errors before proceeding
</div>
```

### Visual Accessibility

```css
/* Sufficient contrast */
.label { color: #333; } /* 12:1 contrast ratio */
.input { border: 2px solid #666; } /* Visible borders */

/* Focus indicators */
input:focus {
  outline: 3px solid #0066cc;
  outline-offset: 2px;
}

/* Don't rely solely on color */
.error {
  border-left: 4px solid #d32f2f; /* Color */
  background: #ffebee; /* Background */
}
.error::before {
  content: "⚠ "; /* Icon */
}

/* Readable text */
body {
  font-size: 16px; /* Minimum 12pt */
  line-height: 1.5;
}
```

## Mobile Optimization

### Responsive Design

```css
/* Mobile-first approach */
.form-group {
  margin-bottom: 1.5rem;
}

.input {
  width: 100%;
  font-size: 16px; /* Prevent iOS zoom */
  padding: 12px;
}

/* Larger touch targets */
.button {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 24px;
}

/* Stack on mobile, side-by-side on desktop */
@media (min-width: 768px) {
  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
}
```

### Mobile-Friendly Inputs

```html
<!-- Appropriate input types for mobile keyboards -->
<input type="email" inputmode="email">
<input type="tel" inputmode="tel">
<input type="number" inputmode="decimal">
<input type="url" inputmode="url">

<!-- Date pickers that work on mobile -->
<input type="date">

<!-- Large, tappable checkboxes and radio buttons -->
<input type="checkbox" class="large-checkbox">
<input type="radio" class="large-radio">
```

## Testing and Optimization

### Usability Testing

```
Test with:
- Attorney users
- Paralegal users
- Client users (if client-facing)
- Users with varying tech proficiency

Measure:
- Completion time
- Error rates
- Abandonment points
- User satisfaction
```

### A/B Testing

```
Test variations:
- Question wording
- Help text placement
- Page organization
- Progress indicators
- Default values

Measure impact on:
- Completion rate
- Time to complete
- Error rate
- User satisfaction
```

### Analytics

```javascript
// Track interview metrics
analytics.track('interview_started', {
  template_id: template_id,
  user_type: user_type
});

analytics.track('page_viewed', {
  page_number: page_number,
  page_name: page_name
});

analytics.track('field_error', {
  field_name: field_name,
  error_type: error_type
});

analytics.track('interview_abandoned', {
  last_page: current_page,
  completion_percentage: completion_percentage
});

analytics.track('interview_completed', {
  total_time_seconds: elapsed_time,
  num_pages: total_pages,
  num_errors: error_count
});
```

## Best Practices Summary

1. **Keep it simple**: Minimize questions, use plain language
2. **Guide users**: Provide help text, examples, and progress indicators
3. **Validate early**: Check inputs in real-time, show clear errors
4. **Save progress**: Auto-save and allow resume
5. **Be accessible**: Keyboard navigation, screen readers, mobile-friendly
6. **Test thoroughly**: With real users, measure and optimize
7. **Iterate**: Continuously improve based on feedback and data

Well-designed interviews lead to better data quality, higher completion rates, and more satisfied users.

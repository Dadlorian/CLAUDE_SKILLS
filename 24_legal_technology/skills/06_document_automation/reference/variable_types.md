# Variable Types and Management

## Overview

Variables are the building blocks of document automation. Understanding variable types, proper usage, and management strategies is essential for creating robust automated document templates.

## Common Variable Types

### Text Variables

**Purpose**: Store alphanumeric text data

**Use Cases**:
- Names (client, company, contact)
- Addresses
- Descriptions
- Email addresses
- Custom text content

**Variants**:
```
Short Text (Single Line)
  - Client_Name
  - Email_Address
  - City
  - State

Long Text (Multi-line)
  - Contract_Description
  - Terms_and_Conditions
  - Custom_Provisions
  - Notes

Rich Text (Formatted)
  - Custom_Clause_Text
  - Formatted_Provisions
  - Styled_Content
```

**Validation Patterns**:
```
Email: ^[^\s@]+@[^\s@]+\.[^\s@]+$
Phone: ^\(\d{3}\)\s\d{3}-\d{4}$
ZIP: ^\d{5}(-\d{4})?$
SSN: ^\d{3}-\d{2}-\d{4}$
URL: ^https?://[^\s]+$
```

**Example**:
```
TEXT Client_Name REQUIRED
  PROMPT "Client's full legal name"
  HELP "Enter the name exactly as it appears on legal documents"
  DEFAULT ""
  MAX_LENGTH 200

TEXT Email_Address REQUIRED
  PATTERN EMAIL
  ERROR_MESSAGE "Please enter a valid email address"

TEXT Contract_Description MULTILINE
  PROMPT "Brief description of contract"
  ROWS 5
  MAX_LENGTH 2000
```

### Number Variables

**Purpose**: Store numeric data for calculations and comparisons

**Use Cases**:
- Monetary amounts
- Quantities
- Percentages
- Counts
- Indices

**Subtypes**:
```
Integer
  - Number_of_Shares
  - Number_of_Employees
  - Term_in_Months

Decimal
  - Interest_Rate
  - Ownership_Percentage
  - Price_Per_Share

Currency
  - Purchase_Price
  - Annual_Salary
  - Earnout_Amount
```

**Formatting**:
```
Currency: $1,234,567.89
Percentage: 12.5%
Integer: 1,000,000
Decimal: 3.14159
```

**Example**:
```
NUMBER Purchase_Price CURRENCY REQUIRED
  PROMPT "Purchase price in USD"
  MIN 0
  MAX 1000000000
  DEFAULT 0
  FORMAT "$#,##0.00"

NUMBER Interest_Rate DECIMAL
  PROMPT "Annual interest rate"
  MIN 0
  MAX 100
  DECIMAL_PLACES 2
  FORMAT "#0.00%"

NUMBER Number_of_Shares INTEGER
  PROMPT "Number of shares"
  MIN 1
  FORMAT "#,##0"
```

### Date Variables

**Purpose**: Store and manipulate dates

**Use Cases**:
- Effective dates
- Birth dates
- Termination dates
- Deadlines
- Anniversaries

**Formats**:
```
MM/DD/YYYY: 11/19/2025
DD/MM/YYYY: 19/11/2025
YYYY-MM-DD: 2025-11-19 (ISO 8601)
MMMM DD, YYYY: November 19, 2025
Month DD, YYYY: Nov 19, 2025
```

**Operations**:
```
Addition: Contract_Start_Date + 365 days
Subtraction: Contract_End_Date - 30 days
Difference: DAYS_BETWEEN(Start_Date, End_Date)
Extraction: YEAR(Date), MONTH(Date), DAY(Date)
Comparison: Date1 < Date2, Date1 = Date2
```

**Example**:
```
DATE Contract_Effective_Date REQUIRED
  PROMPT "Contract effective date"
  FORMAT "MMMM DD, YYYY"
  DEFAULT TODAY
  MIN_DATE TODAY

DATE Birth_Date REQUIRED
  PROMPT "Date of birth"
  FORMAT "MM/DD/YYYY"
  MAX_DATE TODAY
  VALIDATE Age >= 18

DATE Contract_End_Date
  PROMPT "Contract end date"
  COMPUTED Contract_Start_Date + (Term_Years * 365) DAYS
  FORMAT "MMMM DD, YYYY"
```

### Boolean (True/False) Variables

**Purpose**: Store yes/no, true/false binary states

**Use Cases**:
- Feature flags (include/exclude clauses)
- Status indicators
- Checkboxes
- Eligibility checks

**Representation**:
```
TRUE/FALSE
YES/NO
1/0
Checked/Unchecked
```

**Example**:
```
TRUE/FALSE Include_Arbitration
  PROMPT "Include arbitration clause?"
  DEFAULT FALSE
  HELP "Select whether to include binding arbitration provisions"

TRUE/FALSE Is_Accredited_Investor
  PROMPT "Is the investor an accredited investor?"
  DEFAULT FALSE
  REQUIRED

TRUE/FALSE Has_Conflicts
  COMPUTED (Check_Conflicts() = TRUE)
```

### Choice (Dropdown/Radio) Variables

**Purpose**: Select from a predefined list of options

**Use Cases**:
- States/jurisdictions
- Entity types
- Contract types
- Categories

**Types**:
```
Single Select (Dropdown, Radio)
  - Select one option from list

Multi Select (Checkboxes)
  - Select multiple options from list
```

**Example**:
```
MULTIPLE_CHOICE State REQUIRED
  PROMPT "State"
  OPTION "Alabama" VALUE "AL"
  OPTION "Alaska" VALUE "AK"
  OPTION "Arizona" VALUE "AZ"
  ...
  OPTION "Wyoming" VALUE "WY"
  DEFAULT "CA"

MULTIPLE_CHOICE Entity_Type REQUIRED
  PROMPT "Type of business entity"
  OPTION "Corporation" VALUE "Corp"
  OPTION "Limited Liability Company" VALUE "LLC"
  OPTION "Partnership" VALUE "Partnership"
  OPTION "Sole Proprietorship" VALUE "Sole Prop"

CHECKBOX Services_Requested
  PROMPT "Services requested"
  OPTION "Estate Planning"
  OPTION "Business Formation"
  OPTION "Contract Review"
  OPTION "Litigation"
  OPTION "Tax Planning"
  MIN_SELECTIONS 1
```

### Computed/Calculated Variables

**Purpose**: Derive values from other variables

**Use Cases**:
- Mathematical calculations
- Text concatenation
- Conditional assignments
- Aggregations

**Calculation Types**:
```
Mathematical:
  Total = Price + Tax + Fees
  Monthly = Annual / 12
  Percentage = (Part / Whole) * 100

Text:
  Full_Name = First_Name + " " + Last_Name
  Full_Address = Street + ", " + City + ", " + State + " " + Zip

Date:
  End_Date = Start_Date + (Term * 365) days
  Age = YEARS_BETWEEN(Birth_Date, TODAY())

Conditional:
  Status = IF(Amount > 100000, "High Value", "Standard")
```

**Example**:
```
COMPUTED Total_Consideration
  FORMULA Purchase_Price + Earnout_Amount + Assumed_Liabilities
  FORMAT CURRENCY

COMPUTED Full_Name
  FORMULA First_Name + " " + Middle_Initial + ". " + Last_Name
  UPDATE_ON_CHANGE First_Name, Middle_Initial, Last_Name

COMPUTED Contract_End_Date
  FORMULA Contract_Start_Date + (Contract_Term_Years * 365) DAYS
  FORMAT "MMMM DD, YYYY"

COMPUTED Ownership_Percentage
  FORMULA (Shares_Owned / Total_Shares) * 100
  FORMAT "#0.00%"
  VALIDATE Result >= 0 AND Result <= 100
```

## Advanced Variable Types

### Repeating Groups (Arrays/Lists)

**Purpose**: Store multiple instances of related variables

**Use Cases**:
- Multiple parties
- Lists of items
- Schedules
- Tables

**Structure**:
```
REPEAT_GROUP Shareholder
  TEXT Shareholder_Name REQUIRED
  TEXT Shareholder_Address
  NUMBER Shares_Owned INTEGER REQUIRED
  NUMBER Ownership_Percentage DECIMAL
  TRUE/FALSE Is_Founder
  DATE Investment_Date
END REPEAT_GROUP

REPEAT_GROUP Payment_Schedule
  DATE Payment_Date REQUIRED
  NUMBER Payment_Amount CURRENCY REQUIRED
  TEXT Payment_Description
END REPEAT_GROUP
```

**Operations**:
```
COUNT(Shareholder)
SUM(Shareholder.Shares_Owned)
AVERAGE(Payment_Schedule.Payment_Amount)
MAX(Shareholder.Ownership_Percentage)
MIN(Payment_Schedule.Payment_Date)
```

**Example Usage in Template**:
```
SHAREHOLDERS

«REPEAT FOR EACH Shareholder»
«Counter». «Shareholder.Shareholder_Name»
    Shares: «Shareholder.Shares_Owned FORMATTED»
    Percentage: «Shareholder.Ownership_Percentage»%
    «IF Shareholder.Is_Founder»(Founder)«END IF»
«END REPEAT»

Total Shares: «SUM(Shareholder.Shares_Owned)»
```

### Nested Repeating Groups

**Purpose**: Create hierarchical data structures

**Example**:
```
REPEAT_GROUP Department
  TEXT Department_Name REQUIRED
  TEXT Department_Manager

  NESTED_REPEAT_GROUP Employee
    TEXT Employee_Name REQUIRED
    TEXT Employee_Title
    NUMBER Employee_Salary CURRENCY
    DATE Employee_Hire_Date
  END NESTED_REPEAT_GROUP
END REPEAT_GROUP
```

**Usage**:
```
«REPEAT FOR EACH Department»
Department: «Department.Department_Name»
Manager: «Department.Department_Manager»

Employees:
  «REPEAT FOR EACH Employee IN Department»
  - «Employee.Employee_Name», «Employee.Employee_Title»
  «END REPEAT»
«END REPEAT»
```

### Lookup/Reference Variables

**Purpose**: Reference data from external sources

**Sources**:
```
Database tables
API endpoints
Spreadsheets
JSON files
XML data
```

**Example**:
```
LOOKUP State_Tax_Rate
  SOURCE "tax_rates_db"
  QUERY "SELECT tax_rate FROM state_taxes WHERE state = :State"
  PARAMETER State = State_Variable
  RETURN_TYPE DECIMAL

LOOKUP Client_Data
  SOURCE API "https://crm.example.com/api/clients/:ClientID"
  PARAMETER ClientID = Client_ID_Variable
  MAPPING
    "name" -> Client_Name
    "email" -> Client_Email
    "address" -> Client_Address
  CACHE_DURATION 3600
```

## Variable Scope and Lifetime

### Global Variables

**Scope**: Available throughout entire document and all sub-templates

**Use Cases**:
- Client information
- Matter details
- Common dates
- Shared calculations

**Declaration**:
```
GLOBAL TEXT Client_Name
GLOBAL DATE Effective_Date
GLOBAL NUMBER Purchase_Price
```

### Local Variables

**Scope**: Available only within current template or section

**Use Cases**:
- Temporary calculations
- Section-specific data
- Helper variables

**Declaration**:
```
LOCAL TEXT Temp_Text
LOCAL NUMBER Running_Total
LOCAL DATE Temp_Date
```

### Template Variables

**Scope**: Available within a specific template and its includes

**Use Cases**:
- Template-specific settings
- Template configuration
- Template metadata

### Component Variables

**Scope**: Available only within a reusable component

**Use Cases**:
- Component parameters
- Component-specific logic
- Encapsulated data

## Variable Naming Conventions

### Standard Naming Patterns

```
Entity_Property_Descriptor

Examples:
  Buyer_Legal_Name
  Seller_Primary_Address
  Contract_Effective_Date
  Purchase_Price_USD
  Shareholder_Ownership_Percentage
```

### Prefixes

```
is_    Boolean flags: is_married, is_accredited_investor
has_   Boolean presence: has_children, has_liabilities
num_   Counts: num_employees, num_shares
total_ Sums: total_price, total_shares
max_   Maximum: max_earnout, max_liability
min_   Minimum: min_purchase_price
avg_   Average: avg_salary
calc_  Calculated: calc_tax_amount
temp_  Temporary: temp_counter
```

### Suffixes

```
_date       Dates: effective_date, termination_date
_amount     Currency: earnout_amount, payment_amount
_percentage Percentages: ownership_percentage, interest_percentage
_count      Counts: employee_count, transaction_count
_flag       Booleans: active_flag, enabled_flag
_id         Identifiers: client_id, matter_id
_usd        Currency in USD: price_usd
_days       Duration: notice_period_days
```

## Variable Metadata

### Documentation

```
VARIABLE Purchase_Price
  TYPE NUMBER
  SUBTYPE CURRENCY
  DESCRIPTION "Total purchase price for the transaction"
  BUSINESS_RULE "Must be greater than $0 and less than $1B"
  VALIDATION Range(0, 1000000000)
  FORMAT "$#,##0.00"
  REQUIRED TRUE
  DEPENDS_ON Transaction_Type
  USED_IN "Purchase Agreement", "Escrow Instructions"
  LAST_MODIFIED "2025-11-19"
  MODIFIED_BY "jane.smith@firm.com"
END VARIABLE
```

### Dependencies

```
VARIABLE Total_Consideration
  DEPENDS_ON
    - Purchase_Price
    - Earnout_Amount
    - Assumed_Liabilities
  FORMULA Purchase_Price + Earnout_Amount + Assumed_Liabilities
  TRIGGERS_RECALC
    - Tax_Amount (when Total_Consideration changes)
    - Filing_Fee (when Total_Consideration changes)
END VARIABLE
```

## Variable Validation

### Type Validation

```
Ensure data matches expected type
- Text is text
- Numbers are numeric
- Dates are valid dates
- Booleans are true/false
```

### Range Validation

```
NUMBER Age
  MIN 18
  MAX 120
  ERROR "Age must be between 18 and 120"

NUMBER Purchase_Price
  MIN 1
  MAX 1000000000
  ERROR "Purchase price must be between $1 and $1,000,000,000"

DATE Effective_Date
  MIN_DATE TODAY
  ERROR "Effective date cannot be in the past"
```

### Pattern Validation

```
TEXT Email
  PATTERN "^[^\s@]+@[^\s@]+\.[^\s@]+$"
  ERROR "Invalid email format"

TEXT Phone
  PATTERN "^\(\d{3}\)\s\d{3}-\d{4}$"
  ERROR "Phone must be in format (555) 555-5555"

TEXT SSN
  PATTERN "^\d{3}-\d{2}-\d{4}$"
  ERROR "SSN must be in format 123-45-6789"
```

### Business Rule Validation

```
VALIDATION "Ownership Must Total 100%"
  CONDITION SUM(Shareholder.Ownership_Percentage) = 100
  ERROR "Total ownership must equal 100%, currently: " + SUM(Shareholder.Ownership_Percentage) + "%"

VALIDATION "End Date After Start Date"
  CONDITION Contract_End_Date > Contract_Start_Date
  ERROR "Contract end date must be after start date"

VALIDATION "Accredited Investor Requirements"
  CONDITION
    IF Is_Accredited_Investor = TRUE
    THEN (Net_Worth > 1000000 OR Annual_Income > 200000)
  ERROR "Investor does not meet accredited investor requirements"
```

## Variable Organization

### Grouping Strategies

```
By Entity:
  Buyer_Name
  Buyer_Address
  Buyer_Email
  Seller_Name
  Seller_Address
  Seller_Email

By Function:
  Payment_Amount
  Payment_Date
  Payment_Method
  Payment_Terms

By Document Section:
  Recitals_Party_A
  Recitals_Party_B
  Recitals_Background
```

### Variable Libraries

```
Common_Party_Information/
  party_legal_name
  party_address
  party_city
  party_state
  party_zip
  party_email
  party_phone

Financial_Fields/
  amount_currency
  payment_terms
  interest_rate
  late_fee_percentage

Date_Fields/
  effective_date
  termination_date
  notice_period_days
```

## Best Practices

### 1. Use Descriptive Names
```
Good: buyer_legal_name, contract_effective_date
Bad: name, date1, x
```

### 2. Be Consistent
```
If using buyer_legal_name, also use:
  seller_legal_name (not sellerName or seller-legal-name)
```

### 3. Document Variable Purpose
```
Include help text, descriptions, and examples
```

### 4. Validate Early
```
Validate at point of entry, not at document generation
```

### 5. Provide Defaults
```
Where sensible, provide default values
```

### 6. Use Appropriate Types
```
Currency for money, not generic numbers
Dates for dates, not text strings
Booleans for yes/no, not text
```

### 7. Consider Maintenance
```
Design variables for reusability
Document dependencies
Version control variable definitions
```

### 8. Think About Users
```
Clear labels and prompts
Helpful error messages
Appropriate input methods (dropdown vs. text)
```

## Platform-Specific Considerations

Different automation platforms have different variable type capabilities. Consult platform documentation for:

- Available variable types
- Type conversion capabilities
- Custom type creation
- Variable scope rules
- Naming restrictions
- Reserved keywords

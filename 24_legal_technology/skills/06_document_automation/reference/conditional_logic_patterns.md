# Conditional Logic Patterns

## Overview

Conditional logic is the foundation of intelligent document automation. This guide covers common patterns, best practices, and advanced techniques for implementing conditional content in automated documents.

## Basic Conditional Patterns

### Simple IF Statements

**Pattern**: Show/hide content based on a single condition

```
«IF [field_name] = "value"»
Content to show when condition is true
«END IF»
```

**Examples**:
```
«IF Marital_Status = "Married"»
Spouse Name: «Spouse_Name»
Date of Marriage: «Marriage_Date»
«END IF»

«IF Include_Arbitration = TRUE»
ARBITRATION. Any disputes arising under this Agreement shall be resolved through binding arbitration.
«END IF»

«IF Number_of_Employees > 50»
This company is subject to FMLA requirements.
«END IF»
```

### IF-ELSE Statements

**Pattern**: Show one of two alternatives

```
«IF [condition]»
Content when true
«ELSE»
Content when false
«END IF»
```

**Examples**:
```
«IF Entity_Type = "Corporation"»
This Corporation, a «State_of_Incorporation» corporation
«ELSE»
This «Entity_Type», organized under the laws of «State_of_Formation»
«END IF»

«IF Payment_Method = "Cash"»
Payment shall be made by wire transfer to the account specified in Schedule A.
«ELSE»
Payment shall be made by «Payment_Method» as described in Section 3.
«END IF»
```

### IF-ELSE IF-ELSE Chains

**Pattern**: Select from multiple alternatives

```
«IF [condition1]»
First alternative
«ELSE IF [condition2]»
Second alternative
«ELSE IF [condition3]»
Third alternative
«ELSE»
Default alternative
«END IF»
```

**Examples**:
```
«IF Entity_Type = "Corporation"»
  «IF Corporation_Type = "C-Corp"»
This C Corporation shall be taxed as a separate entity.
  «ELSE IF Corporation_Type = "S-Corp"»
This S Corporation has elected pass-through taxation.
  «END IF»
«ELSE IF Entity_Type = "LLC"»
  «IF LLC_Tax_Election = "Partnership"»
This LLC shall be taxed as a partnership.
  «ELSE IF LLC_Tax_Election = "Corporation"»
This LLC has elected to be taxed as a corporation.
  «END IF»
«ELSE IF Entity_Type = "Partnership"»
This Partnership is a pass-through entity for tax purposes.
«END IF»
```

## Compound Conditions

### AND Logic

**Pattern**: All conditions must be true

```
«IF [condition1] AND [condition2]»
Content
«END IF»
```

**Examples**:
```
«IF Annual_Revenue > 1000000 AND Number_of_Employees > 50»
This company meets the requirements for mandatory external audit.
«END IF»

«IF State = "California" AND Industry = "Healthcare" AND Has_PHI = TRUE»
This business is subject to California's CMIA in addition to HIPAA.
«END IF»

«IF Is_Accredited_Investor = TRUE AND Investment_Amount >= 100000 AND Acknowledges_Risk = TRUE»
Investor qualifies for participation in this offering.
«END IF»
```

### OR Logic

**Pattern**: At least one condition must be true

```
«IF [condition1] OR [condition2]»
Content
«END IF»
```

**Examples**:
```
«IF State = "California" OR State = "New York" OR State = "Illinois"»
Additional state-specific employment law provisions apply.
«END IF»

«IF Transaction_Type = "Merger" OR Transaction_Type = "Consolidation"»
The surviving entity shall be «Surviving_Entity_Name».
«END IF»

«IF Force_Majeure_Event = "Natural Disaster" OR Force_Majeure_Event = "Pandemic" OR Force_Majeure_Event = "War"»
Performance under this Agreement is temporarily suspended.
«END IF»
```

### Complex Boolean Logic

**Pattern**: Combine AND, OR, and NOT operators

```
«IF ([condition1] OR [condition2]) AND NOT [condition3]»
Content
«END IF»
```

**Examples**:
```
«IF (Entity_Type = "Corporation" OR Entity_Type = "LLC") AND NOT Is_Nonprofit»
This entity is subject to federal corporate income tax.
«END IF»

«IF (Purchase_Price > 5000000 OR Has_Material_Liabilities = TRUE) AND Buyer_Type != "Individual"»
Enhanced due diligence and representations are required.
«END IF»

«IF ((State = "CA" AND Revenue > 500000) OR Has_CA_Employees > 0) AND NOT Has_CA_Registration»
WARNING: California registration may be required.
«END IF»
```

## Comparison Operators

### Numeric Comparisons

```
Equal to:                   =  or ==
Not equal to:               != or <>
Greater than:               >
Greater than or equal to:   >=
Less than:                  <
Less than or equal to:      <=
```

**Examples**:
```
«IF Purchase_Price > 1000000»
Purchase price exceeds $1,000,000
«END IF»

«IF Ownership_Percentage >= 50»
Buyer will have majority control
«END IF»

«IF Contract_Term_Months < 12»
This is a short-term agreement
«END IF»

«IF Number_of_Shares != 0»
Stock transfer provisions apply
«END IF»
```

### Text Comparisons

```
Exact match:           =
Case-insensitive:      EQUALS_IGNORE_CASE()
Contains:              CONTAINS()
Starts with:           STARTS_WITH()
Ends with:             ENDS_WITH()
In list:               IN [list]
```

**Examples**:
```
«IF State = "Delaware"»
Delaware corporate law applies
«END IF»

«IF CONTAINS(Description, "confidential")»
Additional confidentiality provisions apply
«END IF»

«IF STARTS_WITH(Entity_Name, "The ")»
«SUBSTRING(Entity_Name, 4)»
«ELSE»
«Entity_Name»
«END IF»

«IF Jurisdiction IN ["California", "New York", "Massachusetts"]»
State has strict employment laws
«END IF»
```

### Date Comparisons

```
«IF Contract_Start_Date > TODAY()»
This contract has not yet commenced
«END IF»

«IF Termination_Date < TODAY()»
This contract has expired
«END IF»

«IF DAYS_BETWEEN(Start_Date, End_Date) > 365»
This is a multi-year agreement
«END IF»

«IF YEAR(Effective_Date) = YEAR(TODAY())»
This agreement was executed in the current year
«END IF»
```

## Advanced Conditional Patterns

### Nested Conditions

**Pattern**: Conditions within conditions

```
«IF [outer_condition]»
  Content for outer condition
  «IF [inner_condition]»
    Content for both conditions
  «END IF»
  More content for outer condition
«END IF»
```

**Example**:
```
«IF Transaction_Type = "Stock Purchase"»
  STOCK PURCHASE

  The Buyer shall purchase «Number_of_Shares» shares of «Stock_Class» stock.

  «IF Minority_Shareholders_Exist = TRUE»
    MINORITY SHAREHOLDER RIGHTS

    «IF Include_Tag_Along_Rights = TRUE»
      Tag-along rights shall be granted to minority shareholders.
    «END IF»

    «IF Include_Drag_Along_Rights = TRUE»
      Drag-along rights shall be granted to the Buyer.
    «END IF»

    «IF Include_Preemptive_Rights = TRUE»
      Preemptive rights shall be preserved for minority shareholders.
    «END IF»
  «END IF»

  «IF Include_Earnout = TRUE»
    EARNOUT PROVISIONS

    An earnout payment of up to «Max_Earnout_Amount» shall be paid based on achievement of performance targets.

    «IF Earnout_Type = "Revenue Based"»
      The earnout shall be based on revenue performance as set forth in Schedule «Earnout_Schedule_Letter».
    «ELSE IF Earnout_Type = "EBITDA Based"»
      The earnout shall be based on EBITDA performance as set forth in Schedule «Earnout_Schedule_Letter».
    «END IF»
  «END IF»
«END IF»
```

### Switch/Case Pattern

**Pattern**: Multiple mutually exclusive conditions (using IF-ELSE IF chain)

```
«IF [field] = "option1"»
  Option 1 content
«ELSE IF [field] = "option2"»
  Option 2 content
«ELSE IF [field] = "option3"»
  Option 3 content
«ELSE»
  Default content
«END IF»
```

**Example**:
```
GOVERNING LAW

«IF Governing_Law = "Delaware"»
This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to its conflicts of law principles.
«ELSE IF Governing_Law = "New York"»
This Agreement shall be governed by and construed in accordance with the laws of the State of New York, without regard to its conflicts of law principles.
«ELSE IF Governing_Law = "California"»
This Agreement shall be governed by and construed in accordance with the laws of the State of California, without regard to its conflicts of law principles.
«ELSE IF Governing_Law = "Federal"»
This Agreement shall be governed by and construed in accordance with the federal laws of the United States.
«ELSE»
This Agreement shall be governed by and construed in accordance with the laws of «Governing_Law», without regard to its conflicts of law principles.
«END IF»
```

### Conditional Lists and Enumerations

**Pattern**: Build dynamic lists based on selections

```
The following provisions apply:
«IF Include_Provision_A = TRUE»
(a) Provision A text
«END IF»
«IF Include_Provision_B = TRUE»
(b) Provision B text
«END IF»
«IF Include_Provision_C = TRUE»
(c) Provision C text
«END IF»
```

**Better Pattern with Auto-Numbering**:
```
The following provisions apply:
«SET Counter = 0»
«IF Include_Confidentiality = TRUE»
  «SET Counter = Counter + 1»
(«Counter_As_Letter») Confidentiality provisions as set forth in Section «Confidentiality_Section»;
«END IF»
«IF Include_Non_Compete = TRUE»
  «SET Counter = Counter + 1»
(«Counter_As_Letter») Non-competition provisions as set forth in Section «Non_Compete_Section»;
«END IF»
«IF Include_Non_Solicitation = TRUE»
  «SET Counter = Counter + 1»
(«Counter_As_Letter») Non-solicitation provisions as set forth in Section «Non_Solicitation_Section»;
«END IF»
«IF Include_IP_Assignment = TRUE»
  «SET Counter = Counter + 1»
(«Counter_As_Letter») Intellectual property assignment as set forth in Section «IP_Assignment_Section».
«END IF»
```

### Conditional Sections with Headers

**Pattern**: Include entire sections with headers conditionally

```
«IF Include_Section = TRUE»
SECTION HEADER

Section content...
«END IF»
```

**Example**:
```
«IF Include_Indemnification = TRUE»
ARTICLE «Next_Article_Number». INDEMNIFICATION

«Next_Article_Number».1 Indemnification by Seller. The Seller shall indemnify and hold harmless the Buyer from and against any and all losses arising out of:

  «IF Include_Breach_of_Reps = TRUE»
  (a) any breach of any representation or warranty made by Seller in this Agreement;
  «END IF»

  «IF Include_Pre_Closing_Liabilities = TRUE»
  (b) any liabilities of the Company arising from events occurring prior to the Closing Date;
  «END IF»

  «IF Include_Excluded_Assets = TRUE»
  (c) any excluded assets or retained liabilities.
  «END IF»

«Next_Article_Number».2 Indemnification by Buyer. The Buyer shall indemnify and hold harmless the Seller from and against any and all losses arising out of:

  (a) any breach of any representation or warranty made by Buyer in this Agreement;

  (b) any liabilities assumed by Buyer under this Agreement.

«IF Include_Indemnity_Caps = TRUE»
«Next_Article_Number».3 Limitations on Indemnification.

  (a) Basket. No indemnification shall be payable unless and until the aggregate amount of indemnifiable losses exceeds «Basket_Amount», at which point the indemnifying party shall be liable for all such losses from the first dollar.

  (b) Cap. The maximum aggregate liability for indemnification shall not exceed «Cap_Amount».

  «IF Include_Survival_Periods = TRUE»
  (c) Survival. The representations and warranties shall survive the Closing for a period of «Survival_Period_Months» months, except that representations relating to taxes shall survive for the applicable statute of limitations period.
  «END IF»
«END IF»
«END IF»
```

### Conditional Clause Selection

**Pattern**: Select from a library of alternative clauses

```
«IF Clause_Version = "standard"»
  «INSERT_CLAUSE "Standard_Force_Majeure"»
«ELSE IF Clause_Version = "enhanced"»
  «INSERT_CLAUSE "Enhanced_Force_Majeure"»
«ELSE IF Clause_Version = "limited"»
  «INSERT_CLAUSE "Limited_Force_Majeure"»
«END IF»
```

## Repeating Section Conditionals

### Conditional Iteration

**Pattern**: Loop with conditions inside

```
«REPEAT FOR EACH [item]»
  «IF [item.condition]»
    Include this item
  «END IF»
«END REPEAT»
```

**Example**:
```
SHAREHOLDERS

The following shareholders own shares in the Company:

«REPEAT FOR EACH Shareholder»
  «IF Shareholder.Shares_Owned > 0»
  «Counter». «Shareholder.Name»
      Address: «Shareholder.Address»
      Shares Owned: «Shareholder.Shares_Owned FORMATTED WITH COMMAS»
      Ownership Percentage: «Shareholder.Ownership_Percentage»%
      «IF Shareholder.Ownership_Percentage >= 50»
      Status: Majority Shareholder
      «ELSE IF Shareholder.Ownership_Percentage >= 10»
      Status: Significant Minority Shareholder
      «ELSE»
      Status: Minority Shareholder
      «END IF»
  «END IF»
«END REPEAT»
```

### Conditional Repeating Sections

**Pattern**: Show entire repeating section conditionally

```
«IF Has_Items = TRUE»
  «REPEAT FOR EACH Item»
    Item content
  «END REPEAT»
«END IF»
```

**Example**:
```
«IF Number_of_Exhibits > 0»
EXHIBITS

The following exhibits are attached to and form part of this Agreement:

«REPEAT FOR EACH Exhibit»
Exhibit «Exhibit.Letter»: «Exhibit.Title»
«IF Exhibit.Description != ""»
  Description: «Exhibit.Description»
«END IF»
«END REPEAT»
«END IF»
```

## Calculation-Based Conditionals

### Threshold Testing

```
«IF Purchase_Price > 5000000»
  «SET Requires_Board_Approval = TRUE»
  «SET Requires_Legal_Opinion = TRUE»
  «SET Due_Diligence_Period_Days = 60»
«ELSE IF Purchase_Price > 1000000»
  «SET Requires_Board_Approval = TRUE»
  «SET Requires_Legal_Opinion = FALSE»
  «SET Due_Diligence_Period_Days = 45»
«ELSE»
  «SET Requires_Board_Approval = FALSE»
  «SET Requires_Legal_Opinion = FALSE»
  «SET Due_Diligence_Period_Days = 30»
«END IF»
```

### Percentage-Based Conditions

```
«COMPUTE Total_Ownership = SUM(Shareholder.Ownership_Percentage)»

«IF Total_Ownership != 100»
  ERROR: Ownership percentages must total 100%. Current total: «Total_Ownership»%
«END IF»

«IF Total_Ownership > 100»
  WARNING: Ownership percentages exceed 100% by «Total_Ownership - 100»%
«ELSE IF Total_Ownership < 100»
  WARNING: Ownership percentages are short by «100 - Total_Ownership»%
«END IF»
```

### Range Testing

```
«IF Age >= 18 AND Age < 65»
  Participant is of working age.
«ELSE IF Age >= 65»
  Participant has reached retirement age.
«ELSE»
  Participant is a minor.
«END IF»

«IF Contract_Value >= 0 AND Contract_Value < 100000»
  «SET Approval_Level = "Manager"»
«ELSE IF Contract_Value >= 100000 AND Contract_Value < 500000»
  «SET Approval_Level = "Director"»
«ELSE IF Contract_Value >= 500000 AND Contract_Value < 1000000»
  «SET Approval_Level = "VP"»
«ELSE»
  «SET Approval_Level = "CEO"»
«END IF»
```

## Error Handling Patterns

### Required Field Validation

```
«IF Client_Name = "" OR Client_Name IS NULL»
  ERROR: Client name is required
«END IF»

«IF Purchase_Price <= 0»
  ERROR: Purchase price must be greater than zero
«END IF»

«IF Contract_End_Date <= Contract_Start_Date»
  ERROR: Contract end date must be after start date
«END IF»
```

### Mutual Exclusivity Validation

```
«IF Transaction_Type = "Stock Purchase" AND Transaction_Type = "Asset Purchase"»
  ERROR: Cannot select both stock purchase and asset purchase
«END IF»

«IF (Include_Arbitration = TRUE AND Include_Litigation = TRUE)»
  ERROR: Cannot include both arbitration and litigation provisions
«END IF»
```

### Dependency Validation

```
«IF Include_Earnout = TRUE AND (Earnout_Amount <= 0 OR Earnout_Terms = "")»
  ERROR: Earnout amount and terms required when earnout is included
«END IF»

«IF Entity_Type = "Corporation" AND State_of_Incorporation = ""»
  ERROR: State of incorporation required for corporations
«END IF»

«IF Requires_Board_Approval = TRUE AND Board_Approval_Date = ""»
  WARNING: Board approval date not specified
«END IF»
```

## Best Practices

### 1. Keep Conditions Simple and Readable

**Good**:
```
«IF Is_Corporation = TRUE»
  Corporate provisions
«END IF»
```

**Bad**:
```
«IF ((Entity_Type = "Corporation" OR Entity_Type = "C-Corp" OR Entity_Type = "S-Corp") AND (State = "DE" OR State = "Delaware")) OR (Foreign_Corporation = TRUE AND Registered_In_DE = TRUE)»
  // Complex condition - hard to read and maintain
«END IF»
```

**Better**:
```
«SET Is_Delaware_Corporation = ((Entity_Type = "Corporation" OR Entity_Type = "C-Corp" OR Entity_Type = "S-Corp") AND (State = "DE" OR State = "Delaware")) OR (Foreign_Corporation = TRUE AND Registered_In_DE = TRUE)»

«IF Is_Delaware_Corporation = TRUE»
  Delaware corporate provisions
«END IF»
```

### 2. Use Descriptive Variable Names

**Good**:
```
«IF includes_arbitration_clause = TRUE»
«IF buyer_is_accredited_investor = TRUE»
«IF transaction_requires_hsr_filing = TRUE»
```

**Bad**:
```
«IF flag1 = TRUE»
«IF check2 = TRUE»
«IF condition3 = TRUE»
```

### 3. Provide Defaults and Fallbacks

```
Governing Law: «IF Governing_Law != ""»«Governing_Law»«ELSE»Delaware«END IF»

Notice Period: «IF Notice_Period_Days > 0»«Notice_Period_Days»«ELSE»30«END IF» days

Arbitration Location: «IF Arbitration_City != ""»«Arbitration_City»«ELSE»New York, New York«END IF»
```

### 4. Document Complex Logic

```
<!--
  Indemnification cap calculation:
  - For transactions < $1M: Cap = Purchase Price * 1.0 (100%)
  - For transactions $1M-$10M: Cap = Purchase Price * 0.5 (50%)
  - For transactions > $10M: Cap = $5M (fixed cap)
-->
«IF Purchase_Price < 1000000»
  «SET Indemnity_Cap = Purchase_Price»
«ELSE IF Purchase_Price <= 10000000»
  «SET Indemnity_Cap = Purchase_Price * 0.5»
«ELSE»
  «SET Indemnity_Cap = 5000000»
«END IF»
```

### 5. Test All Paths

Ensure every conditional path is tested:
- True branch
- False branch
- Edge cases (empty, null, zero, negative)
- Boundary conditions
- All combinations in compound conditions

## Common Pitfalls

### 1. Incorrect Operator Precedence

**Problem**:
```
«IF A = 1 OR B = 2 AND C = 3»
// May not behave as expected due to operator precedence
```

**Solution**:
```
«IF (A = 1) OR (B = 2 AND C = 3)»
// Use parentheses to make intention clear
```

### 2. String vs. Number Comparison

**Problem**:
```
«IF "100" > "20"»  // String comparison: FALSE (lexicographic)
«IF 100 > 20»      // Numeric comparison: TRUE
```

**Solution**:
```
«IF TO_NUMBER(Value) > 20»  // Ensure numeric comparison
```

### 3. Null/Empty Checks

**Problem**:
```
«IF Field_Name = ""»  // May fail if field is null vs. empty string
```

**Solution**:
```
«IF Field_Name = "" OR Field_Name IS NULL OR NOT EXISTS(Field_Name)»
```

### 4. Date Comparison Issues

**Problem**:
```
«IF Date_String > "2025-01-01"»  // String comparison may not work as expected
```

**Solution**:
```
«IF Date_Field > DATE("2025-01-01")»  // Use proper date objects
```

## Platform-Specific Syntax

Different platforms use different syntax for conditionals. Refer to platform-specific documentation:

- **HotDocs**: `«IF condition»...«END IF»`
- **Contract Express**: JavaScript-based conditions
- **Documate**: YAML-based conditions
- **Woodpecker**: `{{IF condition}}...{{ENDIF}}`

Always consult your specific platform's documentation for exact syntax and capabilities.

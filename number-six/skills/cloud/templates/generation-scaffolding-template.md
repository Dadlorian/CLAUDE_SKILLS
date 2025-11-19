# [Skill Name] - Generation & Scaffolding Pattern

## Purpose
[One-sentence description of what this skill generates]

## Requirements Gathering

### Essential Information

Before generating, collect these required parameters:

1. **[Parameter 1]**
   - Description: [What this parameter controls]
   - Type: [string/number/boolean/enum]
   - Example: [sample value]
   - Validation: [how to validate]

2. **[Parameter 2]**
   - Description: [What this parameter controls]
   - Type: [string/number/boolean/enum]
   - Example: [sample value]
   - Validation: [how to validate]

### Optional Customizations

Ask if the user wants to customize:

1. **[Optional parameter 1]** (default: [value])
   - Purpose: [What this affects]
   - Options: [Available choices]

2. **[Optional parameter 2]** (default: [value])
   - Purpose: [What this affects]
   - Options: [Available choices]

---

## Generation Strategy

### Step 1: Template Selection

Based on requirements, select the appropriate template:

#### Template A: [Name/Description]
**When to use**: [Conditions]
**Includes**: [What gets generated]
**Structure**:
```
[directory structure]
```

#### Template B: [Name/Description]
**When to use**: [Conditions]
**Includes**: [What gets generated]
**Structure**:
```
[directory structure]
```

#### Custom Template
**When to use**: [Conditions]
**Process**: [How to build custom]

---

### Step 2: Content Generation

For each file to be generated:

#### File 1: [Filename]

**Purpose**: [What this file does]
**Location**: [Where to place it]

**Generation process**:
1. Start with base template
2. Apply transformations:
   - [Transformation 1]: [How to apply]
   - [Transformation 2]: [How to apply]
3. Insert user-specific values:
   - [Where]: [What value]
   - [Where]: [What value]
4. Apply code style/formatting

**Template**:
```[language]
[base template with placeholders]
```

**Validation checks**:
- [ ] [Check 1]
- [ ] [Check 2]
- [ ] [Check 3]

---

#### File 2: [Filename]

**Purpose**: [What this file does]
**Location**: [Where to place it]

**Generation process**:
[Same structure as File 1]

---

### Step 3: Customization & Enhancement

Apply these enhancements based on configuration:

1. **Error Handling**
   - Add try-catch blocks around: [what operations]
   - Add validation for: [what inputs]
   - Add error messages for: [what scenarios]

2. **Documentation**
   - Add JSDoc/docstrings for: [what elements]
   - Include examples for: [what functions]
   - Document parameters: [which ones]

3. **Testing Setup**
   - Generate test file: [location/name]
   - Include test cases for: [what scenarios]
   - Add test utilities: [what helpers]

4. **Type Safety** (if applicable)
   - Add type definitions: [where]
   - Add interfaces: [for what]
   - Add validation: [what to validate]

---

### Step 4: Integration

**Objective**: Integrate generated code with existing project

1. **File Placement**
   - Create directories if needed: [which ones]
   - Place files in: [appropriate locations]
   - Follow project conventions: [what conventions]

2. **Dependency Management**
   - Identify required dependencies: [how]
   - Update package.json/requirements.txt: [with what]
   - Install dependencies: [command]

3. **Configuration Updates**
   - Update config files: [which files]
   - Add environment variables: [which variables]
   - Register new components: [where to register]

4. **Import/Export Setup**
   - Add exports: [where]
   - Update index files: [which files]
   - Add imports: [in which files]

---

### Step 5: Validation & Testing

**Pre-deployment checks**:

1. **Syntax Validation**
   - Run linter: [command]
   - Check for errors: [what to check]
   - Fix any issues: [how to fix]

2. **Type Checking** (if applicable)
   - Run type checker: [command]
   - Resolve type errors: [how]
   - Ensure type safety: [what to verify]

3. **Test Execution**
   - Run generated tests: [command]
   - Verify all pass: [what to check]
   - Check coverage: [target percentage]

4. **Build Verification**
   - Run build command: [command]
   - Ensure successful build: [what to verify]
   - Check output: [what to check]

---

## Quality Standards

All generated code must meet these criteria:

### Code Quality
- [ ] Follows project coding conventions
- [ ] Uses consistent naming patterns
- [ ] Has appropriate comments/documentation
- [ ] No linter warnings or errors
- [ ] Passes type checking (if applicable)

### Functionality
- [ ] Implements all required features
- [ ] Handles errors appropriately
- [ ] Validates inputs properly
- [ ] Returns expected outputs
- [ ] Works with existing code

### Maintainability
- [ ] Code is readable and clear
- [ ] No unnecessary complexity
- [ ] Follows DRY principle
- [ ] Uses appropriate abstractions
- [ ] Easy to modify and extend

### Testing
- [ ] Has comprehensive test coverage
- [ ] Tests are meaningful and assertive
- [ ] Edge cases are covered
- [ ] Error scenarios are tested
- [ ] Tests are maintainable

---

## Output Structure

After generation, provide:

### 1. Summary
```
Generated [number] files for [feature name]:
- [file 1]: [description]
- [file 2]: [description]
- [file 3]: [description]

Dependencies added:
- [package]: [version]
- [package]: [version]
```

### 2. File Contents
Show each generated file with syntax highlighting

### 3. Integration Instructions
```markdown
To integrate these files:
1. [Step 1]
2. [Step 2]
3. [Step 3]
```

### 4. Next Steps
```markdown
Recommended next steps:
1. [Action 1]
2. [Action 2]
3. [Action 3]
```

### 5. Usage Example
```[language]
// Example of how to use the generated code
[code example]
```

---

## Customization Options

Users can customize generation with:

### Style Options
- `naming_convention`: "camelCase" | "snake_case" | "PascalCase"
- `quote_style`: "single" | "double"
- `semicolons`: true | false
- `indent`: 2 | 4 | "tab"

### Feature Flags
- `include_tests`: true | false
- `include_docs`: true | false
- `include_examples`: true | false
- `strict_mode`: true | false

### Framework-Specific
- [Framework option 1]
- [Framework option 2]

---

## Error Recovery

If generation fails:

1. **Validation Failure**
   - Show what failed validation
   - Explain why it failed
   - Suggest corrections
   - Ask if user wants to retry

2. **Integration Failure**
   - Identify what couldn't integrate
   - Show the conflict
   - Offer solutions:
     - Manual integration steps
     - Alternative approach
     - Skip integration

3. **Test Failure**
   - Show which tests failed
   - Explain the failure
   - Offer to fix or let user fix

---

## Examples

### Example 1: [Scenario]
**Input**:
```
[input parameters]
```

**Output**:
```
[generated code]
```

### Example 2: [Scenario]
**Input**:
```
[input parameters]
```

**Output**:
```
[generated code]
```

---

## Notes

[Additional guidance, warnings, or tips]

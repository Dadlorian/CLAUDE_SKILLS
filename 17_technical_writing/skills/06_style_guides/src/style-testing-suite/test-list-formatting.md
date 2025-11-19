# Test: List Formatting Standards

## Purpose

Validate consistent list structure and formatting.

## Passing Examples

### Consistent Unordered Lists

- Install the package
- Configure the settings
- Run the tests

All items use the same marker and structure.

### Ordered Lists with Sequential Numbering

1. Download the installation file
2. Run the setup wizard
3. Verify the installation
4. Configure your preferences

Sequential numbering from 1 to N.

### Nested Lists with Proper Indentation

1. Main installation steps
   - Download package
   - Verify checksum
   - Extract files
2. Configuration steps
   - Edit config file
   - Set environment variables
   - Restart service
3. Verification
   - Run tests
   - Check logs

Proper indentation and hierarchy.

### Description Lists

**API**: Application Programming Interface - a contract for software communication
**REST**: Representational State Transfer - an architectural style for web services
**JSON**: JavaScript Object Notation - a lightweight data interchange format

### Task Lists

- [x] Complete documentation
- [x] Review with team
- [ ] Deploy to production
- [ ] Monitor for issues

### List with Continuation Paragraphs

1. First step in the process.

   This provides additional detail about the first step and explains why it's important for the overall workflow.

2. Second step in the process.

   Additional context and explanation for understanding the second step completely.

3. Final verification step.

   Concluding remarks about completing the entire process.

## Failing Examples

### Inconsistent List Markers

- Item one
* Item two (mixed marker)
+ Item three (mixed marker)

Using different markers in the same list.

### Non-Sequential Numbering

1. First step
3. Third step (skipped 2)
2. Second step (out of order)

Numbering should be sequential.

### Inconsistent Capitalization

- first item (lowercase)
- Second item (capitalized)
- Third item (capitalized)

First word capitalization should be consistent.

### Mixed Punctuation

- Item with period.
- Item without end punctuation
- Another item.

Inconsistent ending punctuation.

### Improper Nesting

- Parent item
- Indented child (wrong indentation)
  - Grandchild

Child items should be consistently indented.

### Excessive Nesting

- Level 1
  - Level 2
    - Level 3
      - Level 4
        - Level 5

Avoid nesting more than 3 levels deep.

## Notes

List formatting best practices:

1. **Consistency** - Use same marker throughout list
2. **Hierarchy** - Proper indentation for nested items
3. **Punctuation** - Consistent ending punctuation
4. **Capitalization** - Consistent first-word capitalization
5. **Brevity** - Keep list items concise
6. **Parallelism** - Use parallel grammatical structure

## Common Issues

- Switching between list marker types
- Non-sequential numbering
- Inconsistent indentation
- Mixed capitalization
- Inconsistent punctuation
- Items that are too long

## Related Rules

- TechWriter.Emphasis - Emphasis in lists
- TechWriter.Consistency - Terminology consistency
- TechWriter.Headings - List introduction text

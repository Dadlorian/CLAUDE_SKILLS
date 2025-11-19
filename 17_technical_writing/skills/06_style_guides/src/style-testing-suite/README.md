# Style Testing Suite

Automated testing framework for validating style guide compliance across documentation.

## Overview

This testing suite provides:

- **Automated Style Validation** - Run Vale rules against test documents
- **Test Coverage Tracking** - Ensure all style rules are tested
- **Regression Prevention** - Catch style violations before publication
- **CI/CD Integration** - Built for continuous integration pipelines

## Components

### Test Files

- `test-acronyms.md` - Acronym definition and usage tests
- `test-api-documentation.md` - API documentation standards
- `test-accessibility.md` - Screen reader optimization
- `test-capitalization.md` - Consistent product/term capitalization
- `test-code-formatting.md` - Command and code block formatting
- `test-consistency.md` - Terminology consistency tests
- `test-contractions.md` - Contraction usage validation
- `test-deprecated-terms.md` - Deprecated terminology detection
- `test-emphasis.md` - Bold/italic usage consistency
- `test-file-naming.md` - File naming convention validation
- `test-gender-neutrality.md` - Gender-neutral language checks
- `test-headings.md` - Heading structure validation
- `test-inclusive-language.md` - Inclusive terminology validation
- `test-jargon.md` - Unexplained jargon detection
- `test-list-formatting.md` - List structure consistency
- `test-metadata.md` - Document metadata requirements
- `test-passive-voice.md` - Passive voice detection
- `test-product-consistency.md` - Product name consistency
- `test-punctuation.md` - Punctuation standards
- `test-readability.md` - Readability metrics

### Test Runners

- `run-all-tests.sh` - Execute all test suites
- `test-runner.js` - JavaScript test framework
- `validate-rules.py` - Python validation script

## Test Structure

Each test file follows this pattern:

```markdown
# Test: [Rule Name]

## Passing Examples

Content that should pass validation...

## Failing Examples

Content that should fail validation...

## Notes

Additional context about the rule.
```

## Running Tests

### Run All Tests
```bash
./run-all-tests.sh
```

### Run Specific Test
```bash
vale --config=../complete-vale-config/.vale.ini test-acronyms.md
```

### Run with Node.js
```bash
node test-runner.js --pattern='test-*.md'
```

### Validate Against Rules
```bash
python validate-rules.py --config ../complete-vale-config/
```

## Test Configuration

### Vale Integration
```bash
# Run Vale against all tests
vale --config=../complete-vale-config/.vale.ini .

# Generate JSON output
vale --output=json test-*.md > test-results.json

# Check specific rule
vale --only=TechWriter.Acronyms test-acronyms.md
```

### Expected Results

Tests are designed with:

- **Positive cases** that should pass (no violations)
- **Negative cases** that should fail (violations expected)
- **Edge cases** for boundary conditions

## Continuous Integration

### GitHub Actions Example
```yaml
name: Style Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Style Tests
        run: ./run-all-tests.sh
```

### Exit Codes
- `0` - All tests passed
- `1` - Some tests failed
- `2` - Configuration error

## Rule Coverage

### Implemented Rules (20+)

- [x] Acronyms - Definition and expansion
- [x] API Documentation - Standard patterns
- [x] Accessibility - Screen reader optimization
- [x] Capitalization - Product name consistency
- [x] Code Formatting - Command and code block standards
- [x] Consistency - Terminology validation
- [x] Contractions - Usage control
- [x] Deprecated Terms - Flag outdated terminology
- [x] Emphasis - Bold/italic usage
- [x] File Naming - Naming conventions
- [x] Gender Neutrality - Inclusive pronouns
- [x] Headings - Structure validation
- [x] Inclusive Language - Non-discriminatory terms
- [x] Jargon - Unexplained technical terms
- [x] List Formatting - Structure consistency
- [x] Metadata - Document frontmatter
- [x] Passive Voice - Active voice preference
- [x] Product Consistency - Brand name usage
- [x] Punctuation - Standard punctuation
- [x] Readability - Complexity metrics

## Test Maintenance

### Adding New Tests

1. Create test file: `test-[rule-name].md`
2. Include passing and failing examples
3. Document the rule being tested
4. Add to test runner configuration

### Updating Existing Tests

```bash
# Run specific test with verbose output
vale --config=../complete-vale-config/.vale.ini test-*.md --verbose

# Check for regressions
git diff HEAD^ test-*.md
```

### Debugging Tests

```bash
# Enable verbose output
VERBOSE=1 ./run-all-tests.sh

# Check Vale configuration
vale --help

# Validate rule files
vale --list-config

# Test specific rule
vale --only=TechWriter.Acronyms test-acronyms.md
```

## Coverage Report

Generate test coverage metrics:

```bash
python validate-rules.py \
  --config ../complete-vale-config/ \
  --report=coverage
```

## Best Practices

1. **One Rule Per File** - Keep tests focused
2. **Clear Examples** - Use realistic markdown content
3. **Document Context** - Explain why rules matter
4. **Test Edge Cases** - Include boundary conditions
5. **Keep Updated** - Sync with rule changes

## Integration with Development

### Pre-commit Hook
```bash
#!/bin/bash
# Run style tests before commit
./run-all-tests.sh || exit 1
```

### CI/CD Pipeline
Tests run automatically on:
- Pull requests
- Commits to main
- Scheduled daily runs

## Performance

Test execution times:

- Individual test: ~100-500ms
- Full suite: ~5-10s
- CI/CD integration: ~15-30s

## Troubleshooting

### Tests Not Running
```bash
# Check Vale installation
vale --version

# Verify config path
ls -la ../complete-vale-config/.vale.ini

# Check file permissions
chmod +x run-all-tests.sh
```

### Unexpected Results
```bash
# Check rule definitions
ls ../complete-vale-config/rules/

# Validate YAML syntax
yamllint ../complete-vale-config/rules/

# Run with debug output
DEBUG=1 node test-runner.js
```

## References

- [Vale Documentation](https://vale.sh/)
- [Test-Driven Development](https://www.agilealliance.org/glossary/tdd/)
- [Quality Assurance Best Practices](https://en.wikipedia.org/wiki/Software_quality_assurance)

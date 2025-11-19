# Vale Custom Rules for Technical Writing

Production-ready Vale rules for enforcing consistent style and quality in technical documentation.

## Rule Overview

### 1. TechWriter.Passive
**Severity:** Warning
**Purpose:** Detect and flag passive voice constructions
**Goal:** Promote active, direct voice in technical writing

### 2. TechWriter.Jargon
**Severity:** Warning
**Purpose:** Flag unexplained technical jargon
**Goal:** Ensure jargon is defined on first use

### 3. TechWriter.Clichés
**Severity:** Warning
**Purpose:** Detect weak phrases and clichés
**Goal:** Improve writing strength and clarity

### 4. TechWriter.Contractions
**Severity:** Warning
**Purpose:** Flag contractions in formal writing
**Goal:** Maintain formal tone appropriate to technical documentation

### 5. TechWriter.Consistency
**Severity:** Warning
**Purpose:** Enforce consistent terminology
**Goal:** Maintain uniform technical term usage

### 6. TechWriter.Acronyms
**Severity:** Error
**Purpose:** Ensure acronyms are defined on first use
**Goal:** Improve accessibility and clarity

### 7. TechWriter.Headings
**Severity:** Warning
**Purpose:** Enforce Title Case in headings
**Goal:** Maintain consistent heading formatting

### 8. TechWriter.CodeFormatting
**Severity:** Warning
**Purpose:** Ensure proper code element formatting
**Goal:** Visually distinguish code from prose

### 9. TechWriter.Readability
**Severity:** Suggestion
**Purpose:** Flag excessively long sentences
**Goal:** Improve document readability

### 10. TechWriter.DeprecatedTerms
**Severity:** Error
**Purpose:** Flag deprecated or problematic terminology
**Goal:** Promote inclusive, modern language

### 11. TechWriter.Punctuation
**Severity:** Warning
**Purpose:** Detect punctuation inconsistencies
**Goal:** Ensure clean, professional formatting

### 12. TechWriter.Numbers
**Severity:** Warning
**Purpose:** Enforce consistent number and unit formatting
**Goal:** Improve technical precision and clarity

## Installation

1. Copy the `rules/` directory to your Vale configuration directory
2. Add rule references to your `.vale.ini` configuration file:

```ini
[*.md]
TechWriter.Passive = warning
TechWriter.Jargon = warning
TechWriter.Clichés = warning
TechWriter.Contractions = warning
TechWriter.Consistency = warning
TechWriter.Acronyms = error
TechWriter.Headings = warning
TechWriter.CodeFormatting = warning
TechWriter.Readability = suggestion
TechWriter.DeprecatedTerms = error
TechWriter.Punctuation = warning
TechWriter.Numbers = warning
```

## Running Tests

```bash
# Test individual rules
vale --config=.vale.ini tests/test-passive-voice.md
vale --config=.vale.ini tests/test-jargon.md
vale --config=.vale.ini tests/test-contractions.md

# Run all tests
vale --config=.vale.ini tests/
```

## Test Coverage

- **test-passive-voice.md** - Tests passive voice detection
- **test-jargon.md** - Tests unexplained jargon flagging
- **test-contractions.md** - Tests contraction detection
- **test-cliches.md** - Tests weak phrase detection
- **test-deprecated-terms.md** - Tests deprecated terminology
- **test-consistency.md** - Tests terminology consistency
- **test-acronyms.md** - Tests acronym definition checking
- **test-headings.md** - Tests heading capitalization
- **test-readability.md** - Tests sentence length detection

## Customization

### Adding New Rules

1. Create a new YAML file in the `rules/` directory
2. Follow the structure of existing rules
3. Add test cases in `tests/`
4. Update `.vale.ini` to enable the rule

### Rule Types

Vale supports several rule types:

- **existence**: Match words or phrases that should be removed
- **substitution**: Match and suggest replacements
- **capitalization**: Enforce capitalization patterns
- **spelling**: Check spelling against wordlists

See [Vale documentation](https://docs.errata.ai/vale/styles) for more details.

## Integration

### With Git Pre-Commit
```bash
vale --config=.vale.ini "$(git diff --name-only --cached)"
```

### With GitHub Actions
```yaml
- name: Lint with Vale
  run: vale --config=.vale.ini *.md
```

### With CI/CD
Include in your CI pipeline:
```bash
vale --config=.vale.ini --output=JSON > vale-report.json
```

## Best Practices

1. **Start permissive:** Begin with warnings, elevate to errors gradually
2. **Define exceptions:** Use `.vale-ignore` files for known exceptions
3. **Regular updates:** Review and update rules quarterly
4. **Team alignment:** Ensure team understands rule rationale
5. **Document decisions:** Keep changelog of rule modifications

## Troubleshooting

**Rule not triggering:**
- Verify rule is enabled in `.vale.ini`
- Check regex patterns with online regex testers
- Review Vale debug output: `vale --debug`

**Too many false positives:**
- Adjust severity level
- Refine regex patterns
- Use exclusion patterns

**Performance issues:**
- Limit rule scope with `scope` field
- Optimize regex patterns
- Cache results between runs

## Contributing

To contribute improvements:

1. Create test cases for the issue
2. Implement rule fixes
3. Verify all tests pass
4. Document the change

## References

- [Vale Documentation](https://docs.errata.ai/vale/)
- [YAML Syntax](https://yaml.org/)
- [Regular Expressions Guide](https://www.regular-expressions.info/)

# Complete Vale Configuration System

## Overview

This comprehensive Vale configuration provides enterprise-grade style enforcement for technical documentation. It includes 20+ custom rules covering acronyms, consistency, accessibility, and inclusive language.

## Components

### .vale.ini
Main Vale configuration file with:
- 25+ style rules with custom severity levels
- Format-specific configurations (Markdown, RST, AsciiDoc, Text)
- Token replacements for consistency and inclusivity
- Common typo corrections
- Rule customization options

### Included Rules

#### Accessibility & Inclusivity
- TechWriter.Inclusivity - Detects non-inclusive language
- TechWriter.GenderNeutrality - Promotes gender-neutral terms
- TechWriter.ScreenReaderOptimization - Ensures accessibility

#### Technical Consistency
- TechWriter.API - API documentation standards
- TechWriter.CommandFormatting - Command syntax enforcement
- TechWriter.ProductConsistency - Product name consistency
- TechWriter.FileNaming - File naming conventions

#### Readability
- TechWriter.Readability - Readability metrics enforcement
- TechWriter.Jargon - Detects unexplained technical jargon
- TechWriter.Numbers - Number formatting standards

#### Content Quality
- TechWriter.Consistency - Terminology consistency
- TechWriter.Headings - Heading structure validation
- TechWriter.CodeFormatting - Code block formatting
- TechWriter.MetaInformation - Metadata requirements

#### Grammar & Punctuation
- TechWriter.Passive - Passive voice detection
- TechWriter.Contractions - Contraction usage control
- TechWriter.Punctuation - Punctuation standards

#### Standards & Conventions
- TechWriter.Acronyms - Acronym definition requirements
- TechWriter.Clichés - Discourage overused phrases
- TechWriter.DeprecatedTerms - Flag deprecated terminology
- TechWriter.Emphasis - Emphasis usage control
- TechWriter.ListFormatting - List structure consistency
- TechWriter.CapitalizationConsistency - Capitalization rules
- TechWriter.Spelling - Spell checking

## Configuration Features

### Severity Levels
- **error** (3): Critical style violations that must be fixed
- **warning** (2): Important issues that should be reviewed
- **suggestion** (1): Optional improvements for consideration

### Format-Specific Rules
Different rules apply to different file types:
- Markdown (.md) - Full rule enforcement
- ReStructuredText (.rst) - Core technical rules
- AsciiDoc (.adoc) - Documentation rules
- Text (.txt) - Basic formatting rules

### Token Replacements
Automatic replacements for:
- Inclusive language (whitelist → allowlist)
- Technical consistency (REST → REST)
- Common typos (recieved → received)
- Spacing normalization

## Usage

### Basic Setup
```bash
# Copy to repository root
cp .vale.ini /path/to/your/repo/

# Run Vale on all markdown files
vale --config=/path/to/.vale.ini *.md

# Run on specific directory
vale --config=/path/to/.vale.ini docs/

# Generate report
vale --config=/path/to/.vale.ini --output=json docs/ > style-report.json
```

### Command Line Options
```bash
# Check all markdown files
vale *.md

# Exclude specific patterns
vale --ignore-pattern='(test|temp)' docs/

# Only show errors (skip warnings)
vale --min-alert-level=error docs/

# Generate JSON output
vale --output=json docs/

# Generate summary
vale --output=summary docs/
```

### Integration with CI/CD
```yaml
# GitHub Actions example
- name: Vale Style Check
  uses: errata-ai/vale-action@v2
  with:
    files: doc/**/*.md
    config: .vale.ini
```

## Customization

### Adding Custom Rules
1. Create new YAML rule files in `vale-custom-rules/rules/`
2. Reference in `.vale.ini` with `BasedOnStyles`
3. Set severity level for your use case

### Modifying Existing Rules
Edit `.vale.ini` to:
- Change severity levels
- Enable/disable specific rules
- Adjust token replacements
- Configure format-specific behavior

### Project-Specific Configuration
Create `.vale.ini` in project directories to override global settings:
```ini
[*.md]
TechWriter.Jargon = suggestion
BasedOnStyles = TechWriter
```

## Integration with Style System

This Vale configuration integrates with:
- **terminology-checker.js** - Custom term validation
- **markdown-formatter.js** - Automated formatting
- **style-report-generator.py** - Compliance reporting
- **style-testing-suite** - Automated test validation

## Performance Considerations

- Ignore patterns reduce check time significantly
- Use `MinAlertLevel` to focus on critical issues
- Cache results for faster iteration
- Run in parallel for large documentation sets

## Maintenance

### Updating Rules
1. Test changes with sample documents
2. Validate against style-testing-suite
3. Update documentation
4. Deploy to CI/CD pipeline

### Monitoring
- Track style violations over time
- Identify most common issues
- Adjust severity levels based on team needs
- Collect feedback from documentation team

## References

- Vale Documentation: https://vale.sh/
- Technical Writing Best Practices: https://developers.google.com/style
- Accessibility Guidelines: https://www.w3.org/WAI/
- Inclusive Language: https://www.inclusivity.io/

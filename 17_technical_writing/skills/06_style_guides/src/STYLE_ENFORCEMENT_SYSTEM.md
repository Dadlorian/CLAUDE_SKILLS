# Complete Style Enforcement System

Enterprise-grade automation for technical documentation style compliance and validation.

**Status**: Production Ready | **Version**: 1.0

## System Overview

This comprehensive style enforcement system provides automated tools for maintaining consistent, accessible, and inclusive technical documentation across large documentation sets.

### Components

1. **Complete Vale Config** - 20+ style rules with comprehensive documentation
2. **Terminology Checker** - Custom JavaScript validation tool for term consistency
3. **Markdown Formatter** - Automatic formatting with style rule enforcement
4. **Style Testing Suite** - Automated test framework with 15+ test files
5. **Report Generator** - HTML compliance reports with metrics and visualizations

## Architecture

```
/src/
├── complete-vale-config/           # Primary style validation engine
│   ├── .vale.ini                   # Main configuration file
│   ├── README.md                   # Documentation
│   └── rules/                      # 15+ Vale rule files
├── style-testing-suite/            # Test framework
│   ├── README.md                   # Testing documentation
│   ├── test-*.md                   # 15+ test files
│   └── run-all-tests.sh            # Test runner script
├── terminology-checker.js          # Custom term validation
├── markdown-formatter.js           # Auto-formatting tool
├── style-report-generator.py       # HTML report generation
└── STYLE_ENFORCEMENT_SYSTEM.md     # This file
```

## Quick Start

### 1. Setup

```bash
# Navigate to the src directory
cd /home/user/CLAUDE_SKILLS/17_technical_writing/skills/06_style_guides/src/

# Copy Vale configuration to your project
cp complete-vale-config/.vale.ini /path/to/your/project/

# Copy Vale rules (if using custom rules)
cp -r complete-vale-config/rules /path/to/your/project/styles/
```

### 2. Basic Usage

#### Run Style Checks
```bash
# Check markdown files
vale *.md

# Check specific directory
vale docs/

# Generate detailed report
vale --output=json docs/ > style-report.json
```

#### Auto-Format Files
```bash
# Format single file
node markdown-formatter.js --dry-run docs/guide.md

# Format all markdown files
node markdown-formatter.js docs/*.md

# Format with custom settings
node markdown-formatter.js --list-marker='*' --indent=4 docs/
```

#### Check Terminology
```bash
# Validate terminology consistency
node terminology-checker.js docs/*.md

# Generate detailed report
node terminology-checker.js --report-type=detailed docs/

# Output as JSON
node terminology-checker.js --report-type=json docs/ > terminology-report.json
```

#### Generate Compliance Reports
```bash
# Create HTML report
python3 style-report-generator.py --output=report.html docs/*.md

# Use Vale configuration
python3 style-report-generator.py --config=.vale.ini --output=report.html docs/

# Verbose output
python3 style-report-generator.py -v docs/
```

### 3. Run Tests

```bash
# Run all style tests
cd style-testing-suite/
./run-all-tests.sh

# Run with verbose output
VERBOSE=1 ./run-all-tests.sh

# Run specific test
vale --config=../complete-vale-config/.vale.ini test-api-documentation.md
```

## Core Features

### 1. Vale Configuration (20+ Rules)

**Accessibility & Inclusivity**
- Screen Reader Optimization - Document structure for screen readers
- Gender Neutrality - Gender-neutral language
- Inclusive Language - Non-discriminatory terms
- Accessibility Metadata - Document accessibility requirements

**Technical Standards**
- API Documentation - Endpoint documentation patterns
- Command Formatting - Command and code block standards
- Code Formatting - Consistent code presentation
- File Naming - File naming conventions
- Product Consistency - Product name consistency

**Content Quality**
- Acronyms - Acronym definition requirements
- Capitalization Consistency - Proper term capitalization
- Emphasis - Bold/italic usage control
- Headings - Document structure validation
- List Formatting - List consistency
- Metadata - Document frontmatter requirements
- Punctuation - Punctuation standards
- Readability - Readability metrics
- Spelling - Spell checking

**Advanced Features**
- Deprecated Terms - Flag outdated vocabulary
- Jargon - Unexplained technical terms
- Passive Voice - Active voice preference
- Contractions - Contraction usage control
- Clichés - Discourage overused phrases

### 2. Terminology Checker

Validates consistent product/technical term usage:

```javascript
// Built-in terminology databases:
- Framework names (React, Vue, Angular, etc.)
- Database names (MongoDB, PostgreSQL, MySQL)
- Protocol names (REST, GraphQL, JSON, YAML, HTTP)
- Tool names (Docker, Kubernetes, Git)
- Inclusive language replacements
```

Features:
- Case-sensitive and case-insensitive modes
- Category-based organization
- Multiple report formats (summary, detailed, JSON)
- Detailed context for each violation

### 3. Markdown Formatter

Automatic formatting with preservation of semantic content:

- Heading standardization (ATX style)
- List marker consistency (configurable: -, *, +)
- Code block formatting (fence markers, language tags)
- Paragraph normalization
- Whitespace optimization
- Trailing newlines

Options:
```bash
--indent <n>        # Indentation (default: 2)
--list-marker <m>   # Marker: -, *, + (default: -)
--dry-run          # Preview changes without applying
--verbose, -v      # Show detailed output
```

### 4. Style Testing Suite

Comprehensive testing framework:

**Test Coverage**
- 15+ markdown test files
- 200+ individual test cases
- Positive and negative examples
- Edge case validation

**Test Files**
- Accessibility standards
- API documentation patterns
- Inclusive language usage
- List formatting
- Metadata requirements
- And more...

**Execution**
```bash
./run-all-tests.sh              # Run all tests
VERBOSE=1 ./run-all-tests.sh   # Show detailed output
./run-all-tests.sh --pattern   # Custom pattern
```

### 5. HTML Report Generator

Beautiful, interactive compliance reports:

**Report Contents**
- Compliance score (0-100%)
- Issues by severity (error/warning/suggestion)
- Issues by category and rule
- Top issues and patterns
- Detailed issue tables
- Actionable recommendations

**Features**
- Responsive design
- Color-coded severity levels
- Rule frequency analysis
- File-by-file breakdown
- Printable format

```bash
python3 style-report-generator.py \
  --config=.vale.ini \
  --output=compliance-report.html \
  docs/
```

## Integration Guide

### With CI/CD Pipelines

#### GitHub Actions
```yaml
name: Style Check
on: [push, pull_request]
jobs:
  style:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: reviewdog/action-vale@v1
        with:
          files: doc/**/*.md
          config: src/complete-vale-config/.vale.ini
```

#### GitLab CI
```yaml
style-check:
  image: node:16
  script:
    - npm install -g vale
    - vale --config=src/complete-vale-config/.vale.ini docs/
```

#### Jenkins
```groovy
pipeline {
    stages {
        stage('Style Check') {
            steps {
                sh 'vale --config=src/complete-vale-config/.vale.ini docs/'
                sh 'node src/terminology-checker.js docs/'
            }
        }
    }
}
```

### Pre-commit Hooks

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run style checks
vale docs/ || exit 1
node src/terminology-checker.js docs/ || exit 1

# Auto-format files
node src/markdown-formatter.js docs/

exit 0
```

### Development Workflow

```bash
# 1. Edit documentation
vim docs/guide.md

# 2. Auto-format
node markdown-formatter.js docs/guide.md

# 3. Check terminology
node terminology-checker.js docs/guide.md

# 4. Run style validation
vale docs/guide.md

# 5. Generate compliance report
python3 style-report-generator.py docs/guide.md > report.html

# 6. Commit changes
git add docs/
git commit -m "docs: update guide with style compliance"
```

## Configuration

### Vale Configuration (.vale.ini)

Key sections:

```ini
# Severity levels
[*.md]
TechWriter.Acronyms = error        # Critical - must be fixed
TechWriter.Jargon = warning        # Important - should review
TechWriter.Readability = suggestion # Optional - consider improving

# Token replacements
match = '\bwhitelist\b'
replace = 'allowlist'
level = error
```

### Terminology Dictionary

Extend terminology validation:

```javascript
// Add to terminology-checker.js
TERMINOLOGY['custom'] = {
  'MyProduct': {
    variants: ['myproduct', 'my-product'],
    correct: 'MyProduct',
    context: 'Our primary product'
  }
};
```

### Markdown Formatter Options

```bash
# All options available
--indent <n>              # Spaces per indent (default: 2)
--line-length <n>        # Target line length (default: 80)
--list-marker <m>        # Bullet marker (default: -)
--bold <style>           # ** or __ (default: **)
--italic <style>         # * or _ (default: *)
--trailing-newline       # Add/remove trailing newline
--trim-trailing-space    # Remove trailing whitespace
--dry-run               # Preview without changes
--verbose               # Detailed output
```

## Customization

### Adding Custom Rules

1. Create new rule file in `complete-vale-config/rules/`

```yaml
---
name: My Custom Rule
desc: Rule description
message: "Custom message: '%s'"
level: warning
scope: paragraph
extends: existence
patterns:
  - 'pattern to match'
```

2. Add to `.vale.ini`:
```ini
[*.md]
MyCustom.MyRule = error
```

3. Test with Vale:
```bash
vale --only=MyCustom.MyRule docs/
```

### Custom Terminology

Edit `terminology-checker.js` to add custom terms:

```javascript
'custom_framework': {
  'MyFramework': {
    variants: ['myframework', 'my-framework'],
    correct: 'MyFramework',
    context: 'Internal framework'
  }
}
```

### Report Customization

Modify `style-report-generator.py` to:
- Add custom sections
- Change color scheme
- Add brand logos
- Include custom metrics

## Troubleshooting

### Vale Not Found
```bash
# Install Vale
brew install vale                    # macOS
choco install vale                   # Windows
apt-get install vale                 # Linux
npm install -g vale                  # npm
```

### Configuration Not Applied
```bash
# Verify config location
vale --list-config

# Check config syntax
cat .vale.ini

# Test with explicit config path
vale --config=/full/path/.vale.ini docs/
```

### Terminology Checker Issues
```bash
# Test with verbose output
node terminology-checker.js -v docs/

# Debug with specific file
node terminology-checker.js docs/single-file.md --verbose

# Check JavaScript syntax
node -c terminology-checker.js
```

### Formatter Not Working
```bash
# Dry run to preview changes
node markdown-formatter.js --dry-run docs/

# Check file permissions
ls -la docs/

# Test on single file
node markdown-formatter.js docs/test.md

# Verify Node.js installation
node --version
```

## Performance Optimization

### Speed Up Checks

```bash
# Parallel processing
parallel vale {} ::: docs/*.md

# Cache results
vale --cache docs/

# Ignore directories
vale --ignore-pattern='(test|build|dist)' docs/
```

### Large Documentation Sets

```bash
# Process in batches
find docs -name '*.md' -print0 | xargs -0 -n 10 vale

# Use summary output (faster)
vale --output=summary docs/

# Disable slow rules
# Edit .vale.ini to reduce rule count
```

## Best Practices

1. **Regular Execution** - Run checks on every commit
2. **Gradual Adoption** - Start with errors, add warnings over time
3. **Team Training** - Ensure team understands style guide
4. **Documentation** - Keep style guide accessible
5. **Iterative Improvement** - Adjust rules based on feedback
6. **Automate Formatting** - Use formatter before review
7. **Test Coverage** - Maintain comprehensive test suite
8. **Review Reports** - Analyze reports for patterns

## Maintenance

### Update Rules

```bash
# Test rule changes
./style-testing-suite/run-all-tests.sh

# Validate configuration
vale --help

# Update documentation
vim complete-vale-config/README.md
```

### Monitor Compliance

```bash
# Generate regular reports
python3 style-report-generator.py --output=reports/$(date +%Y-%m-%d).html docs/

# Track trends
git log --oneline -- style-enforcement-report.json
```

### Team Communication

- Share compliance reports with team
- Discuss high-impact rules
- Adjust rules based on feedback
- Document custom decisions

## Metrics & KPIs

Track documentation quality:

- **Compliance Score** - Overall style adherence (target: >95%)
- **Critical Issues** - Errors that must be fixed (target: 0)
- **Rule Coverage** - Percentage of rules tested (target: >90%)
- **Consistency** - Term usage consistency (target: >98%)
- **Readability** - Average grade level (target: <12)

## Resources

### Documentation
- [Vale Documentation](https://vale.sh/)
- [Style Guide Best Practices](https://developers.google.com/style)
- [Accessible Writing Guide](https://www.w3.org/WAI/)
- [Inclusive Language Guide](https://www.inclusivity.io/)

### Related Skills
- Technical Writing Fundamentals
- Documentation Patterns
- Content Strategy
- Information Architecture

## Support & Contribution

### Reporting Issues

Document issues with:
- Rule name and message
- Example text that triggers issue
- Expected vs actual behavior
- File and line number

### Contributing Improvements

1. Create test case for new rule
2. Implement rule validation
3. Update documentation
4. Run full test suite
5. Submit for review

## Version History

### v1.0 (Current)
- 20+ comprehensive rules
- Custom terminology checker
- Markdown auto-formatter
- Testing suite with 15+ tests
- HTML report generation
- Production-ready
- Full documentation
- CI/CD integration examples

## License & Attribution

This style enforcement system is built on:
- [Vale](https://vale.sh/) - Style checking engine
- Custom extensions for technical writing
- Best practices from industry standards

## Summary

The Complete Style Enforcement System provides:

✓ **Automated Validation** - Real-time style checking
✓ **Comprehensive Rules** - 20+ production-ready rules
✓ **Custom Tools** - Terminology checker, formatter, reporter
✓ **Testing Framework** - Full test coverage
✓ **Beautiful Reports** - Interactive HTML compliance reports
✓ **CI/CD Ready** - Easy pipeline integration
✓ **Highly Customizable** - Adapt to your needs
✓ **Well Documented** - Complete guides and examples

Use this system to:
- Enforce consistent style across teams
- Ensure document accessibility
- Promote inclusive language
- Maintain technical accuracy
- Improve document quality
- Automate compliance checking
- Generate compliance reports
- Track style metrics

Get started now and transform your documentation quality!

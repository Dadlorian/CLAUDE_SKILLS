# Style Enforcement System - Quick Reference

Fast lookup guide for the most common tasks.

## Installation

```bash
cd /home/user/CLAUDE_SKILLS/17_technical_writing/skills/06_style_guides/src/

# Copy to your project
cp complete-vale-config/.vale.ini /path/to/project/
cp -r complete-vale-config/rules /path/to/project/styles/
```

## Running Checks

### Vale (Style Validation)
```bash
# Check all markdown
vale *.md

# Check directory
vale docs/

# JSON output
vale --output=json docs/ > report.json

# Summary report
vale --output=summary docs/
```

### Terminology Checker
```bash
# Check terminology consistency
node terminology-checker.js docs/*.md

# Detailed report
node terminology-checker.js --report-type=detailed docs/

# JSON output
node terminology-checker.js --report-type=json docs/
```

### Markdown Formatter
```bash
# Preview changes (dry run)
node markdown-formatter.js --dry-run docs/*.md

# Apply formatting
node markdown-formatter.js docs/*.md

# Custom settings
node markdown-formatter.js --list-marker='*' --indent=4 docs/
```

### Style Tests
```bash
# Run all tests
cd style-testing-suite/
./run-all-tests.sh

# Verbose output
VERBOSE=1 ./run-all-tests.sh

# Single test
vale --config=../complete-vale-config/.vale.ini test-api-documentation.md
```

### Generate Reports
```bash
# HTML compliance report
python3 style-report-generator.py --output=report.html docs/*.md

# With configuration
python3 style-report-generator.py --config=.vale.ini --output=report.html docs/

# Verbose
python3 style-report-generator.py -v docs/
```

## Key Rules (20+)

### Critical (must fix)
- **Acronyms** - Define all acronyms on first use
- **API Documentation** - Complete endpoint documentation
- **Capitalization** - Correct product/term capitalization
- **Inclusivity** - No discriminatory language
- **Metadata** - Required document frontmatter

### Important (should fix)
- **Accessibility** - Screen reader optimization
- **Command Formatting** - Proper code block syntax
- **Consistency** - Terminology consistency
- **Headings** - Proper document structure
- **List Formatting** - Consistent list formatting
- **Passive Voice** - Prefer active voice

### Nice-to-Have (consider)
- **Clichés** - Reduce overused phrases
- **Jargon** - Explain technical terms
- **Readability** - Keep content understandable
- **Emphasis** - Consistent bold/italic usage

## 30-Second Setup

```bash
# 1. Copy config
cp .vale.ini /your/project/

# 2. Run check
vale docs/

# 3. Auto-format
node markdown-formatter.js docs/

# 4. Generate report
python3 style-report-generator.py -o report.html docs/
```

## Common Issues

| Problem | Solution |
|---------|----------|
| Vale not found | `npm install -g vale` |
| Config not loaded | Check path: `vale --list-config` |
| Rules not applying | Verify `.vale.ini` syntax |
| Formatter breaking content | Use `--dry-run` first |
| Tests failing | Check Vale rules exist |

## File Locations

```
/src/
├── .vale.ini                          # Main config
├── complete-vale-config/              # Vale setup
│   └── rules/                         # 15+ rule files
├── style-testing-suite/               # Tests
│   └── test-*.md                      # Test files
├── terminology-checker.js             # Term validation
├── markdown-formatter.js              # Auto-formatter
├── style-report-generator.py          # HTML reports
├── STYLE_ENFORCEMENT_SYSTEM.md        # Full docs
└── QUICK_REFERENCE.md                 # This file
```

## Integration Examples

### Pre-commit
```bash
#!/bin/bash
vale docs/ && node terminology-checker.js docs/ && \
node markdown-formatter.js docs/
```

### GitHub Actions
```yaml
- uses: reviewdog/action-vale@v1
  with:
    files: docs/**/*.md
    config: src/.vale.ini
```

### Jenkins
```groovy
sh 'vale --config=src/.vale.ini docs/'
```

## Configuration Quick Edit

Edit `.vale.ini` to:

```ini
# Make rule stricter
TechWriter.Acronyms = error

# Make rule optional
TechWriter.Readability = suggestion

# Disable rule
# TechWriter.Passive = NO
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | Style issues found |
| 2 | Configuration error |

## Performance Tips

- Exclude large dirs: `vale --ignore-pattern='(node_modules|build)'`
- Parallel: `parallel vale {} ::: docs/*.md`
- Cache: `vale --cache docs/`
- Batch: Process files in groups

## Most Common Violations

1. **Capitalization** - Product names
2. **Acronyms** - Not defined
3. **Passive Voice** - Too much passive
4. **Terminology** - Inconsistent terms
5. **Headings** - Wrong hierarchy

## Rules by Category

**Accessibility**: Screen readers, Images, Links
**Inclusive**: Language, Gender neutrality, Diversity
**Technical**: APIs, Commands, Code formatting
**Quality**: Consistency, Readability, Structure
**Grammar**: Spelling, Punctuation, Contractions

## Compliance Targets

- Compliance Score: >95%
- Critical Issues: 0
- Warnings: <5%
- Suggestions: Track trends

## Next Steps

1. Review full documentation: `STYLE_ENFORCEMENT_SYSTEM.md`
2. Run tests: `style-testing-suite/run-all-tests.sh`
3. Integrate into CI/CD pipeline
4. Customize rules for your needs
5. Train team on style guide

## Contact & Support

- Vale Docs: https://vale.sh/
- Style Guide: See `complete-vale-config/README.md`
- Tests: See `style-testing-suite/README.md`
- Full Docs: See `STYLE_ENFORCEMENT_SYSTEM.md`

## Commands Summary

```bash
# Check
vale docs/

# Format
node markdown-formatter.js docs/

# Terminology
node terminology-checker.js docs/

# Report
python3 style-report-generator.py -o report.html docs/

# Test
style-testing-suite/run-all-tests.sh
```

That's it! You're ready to enforce style automatically.

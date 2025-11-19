# Version Control for Document Automation

## Overview

Version control for document automation templates ensures change tracking, collaboration, rollback capability, and audit trails. Proper version management is critical for maintaining template integrity and compliance.

## Version Control Systems

### Git-Based Version Control

**Repository Structure**:
```
document-automation/
├── templates/
│   ├── stock_purchase_agreement/
│   │   ├── template.docx
│   │   ├── components.xml
│   │   ├── variables.json
│   │   └── logic.js
│   ├── employment_agreement/
│   └── lease_agreement/
├── components/
│   ├── common/
│   │   ├── party_information.component
│   │   ├── signature_blocks.component
│   │   └── boilerplate_clauses.component
│   └── industry_specific/
├── tests/
│   ├── test_data/
│   └── test_scenarios/
├── docs/
│   ├── user_guides/
│   └── development_guides/
├── .gitignore
├── README.md
└── CHANGELOG.md
```

**.gitignore**:
```
# Exclude generated documents
output/
generated/
*.pdf (in output directories)

# Exclude answer files with PII
answer_files/*.hda
answer_files/*.xml

# Exclude local configuration
config.local.json
.env

# Exclude temporary files
~$*.docx
*.tmp
.DS_Store

# Exclude large binary files (store separately)
media/large_images/

# Include template binaries (necessary)
!templates/**/*.docx
!templates/**/*.hdt
```

### Version Numbering Schemes

**Semantic Versioning (SemVer)**:
```
MAJOR.MINOR.PATCH

Examples:
1.0.0 - Initial release
1.1.0 - Added optional earnout provisions
1.1.1 - Fixed calculation error in earnout
2.0.0 - Complete redesign with new questionnaire

Rules:
MAJOR: Breaking changes (old answer files incompatible)
MINOR: New features (backward compatible)
PATCH: Bug fixes (backward compatible)
```

**Date-Based Versioning**:
```
YYYY.MM.DD or YYYY.MM.REVISION

Examples:
2025.11.19 - November 19, 2025 version
2025.11.1 - November 2025, first revision
2025.11.2 - November 2025, second revision

Use when:
- Templates updated frequently
- Date of version more important than change type
```

**Named Versions**:
```
v1.0 "Initial Release"
v2.0 "Enhanced Questionnaire"
v3.0 "Multi-State Support"

Use when:
- Major releases with significant changes
- Marketing/communication purposes
- Client-facing templates
```

## Change Management

### Commit Messages

**Good Commit Messages**:
```
feat: Add optional escrow provisions to stock purchase agreement
fix: Correct earnout calculation formula
docs: Update user guide with new field descriptions
refactor: Simplify conditional logic in employment agreement
test: Add test cases for multi-shareholder scenarios
style: Standardize heading styles across templates
```

**Commit Message Convention**:
```
<type>(<scope>): <subject>

<body>

<footer>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

Example:
feat(stock-purchase): Add working capital adjustment clause

Added configurable working capital adjustment provisions with:
- Target working capital field
- Adjustment calculation logic
- Payment terms for adjustments

Closes #123
```

### Branching Strategy

**Git Flow**:
```
main (production-ready templates)
  ↓
develop (integration branch)
  ↓
feature/add-earnout-provisions
feature/update-boilerplate
bugfix/calculation-error
hotfix/critical-date-bug
```

**Branch Naming**:
```
feature/[issue-id]-brief-description
  feature/SPA-101-earnout-provisions
  feature/EA-205-remote-work-clause

bugfix/[issue-id]-brief-description
  bugfix/SPA-150-ownership-calculation

hotfix/[issue-id]-critical-issue
  hotfix/SPA-175-signature-block-error

release/v2.0.0
```

**Workflow**:
```bash
# Create feature branch
git checkout -b feature/SPA-101-earnout-provisions develop

# Make changes and commit
git add templates/stock_purchase_agreement/
git commit -m "feat(stock-purchase): Add earnout provisions"

# Push to remote
git push origin feature/SPA-101-earnout-provisions

# Create pull request to develop
# After review and approval, merge to develop

# When ready for release
git checkout -b release/v2.0.0 develop
# Final testing and version updates
git checkout main
git merge release/v2.0.0
git tag -a v2.0.0 -m "Version 2.0.0"
git push origin main --tags
```

## Template Metadata

### Version Information in Templates

**DOCX Custom Properties**:
```xml
<customProperties>
  <property name="TemplateVersion" fmtid="{D5CDD505-...}">
    <vt:lpwstr>2.0.0</vt:lpwstr>
  </property>
  <property name="TemplateName">
    <vt:lpwstr>Stock Purchase Agreement</vt:lpwstr>
  </property>
  <property name="LastModified">
    <vt:lpwstr>2025-11-19</vt:lpwstr>
  </property>
  <property name="ModifiedBy">
    <vt:lpwstr>jane.smith@lawfirm.com</vt:lpwstr>
  </property>
  <property name="ChangeDescription">
    <vt:lpwstr>Added optional escrow provisions</vt:lpwstr>
  </property>
</customProperties>
```

**Template Header Comments**:
```
<!--
Template: Stock Purchase Agreement
Version: 2.0.0
Last Modified: 2025-11-19
Author: Jane Smith
Changes:
  - Added optional escrow provisions
  - Enhanced working capital adjustment clause
  - Updated boilerplate language per firm standards
-->
```

### Changelog

**CHANGELOG.md**:
```markdown
# Changelog

All notable changes to the Stock Purchase Agreement template will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [2.0.0] - 2025-11-19

### Added
- Optional escrow provisions with configurable terms
- Working capital adjustment clause
- Additional representations for regulated industries

### Changed
- Improved indemnification basket calculation
- Enhanced closing conditions section
- Updated boilerplate to current firm standards

### Deprecated
- Old stock certificate transfer method (use new electronic transfer)

### Fixed
- Calculation error in earnout cap
- Date formatting inconsistency in schedules

### Security
- Added data validation for purchase price field

## [1.1.1] - 2025-10-15

### Fixed
- Corrected ownership percentage calculation for partial shares
- Fixed signature block formatting issue

## [1.1.0] - 2025-10-01

### Added
- Optional earnout provisions
- Support for multiple share classes

### Changed
- Reorganized questionnaire for better flow

## [1.0.0] - 2025-09-01

### Added
- Initial release of Stock Purchase Agreement template
- Basic party information collection
- Standard representations and warranties
- Indemnification provisions
```

## Migration and Compatibility

### Answer File Migration

```python
class AnswerFileMigrator:
    """Migrate answer files between template versions"""

    def migrate(self, answer_file, from_version, to_version):
        """Migrate answer file from one version to another"""

        data = self.load_answer_file(answer_file)

        # Apply migration steps
        for version in self.get_migration_path(from_version, to_version):
            migration_func = getattr(self, f'migrate_to_{version}')
            data = migration_func(data)

        return data

    def migrate_to_2_0_0(self, data):
        """Migrate from 1.x to 2.0.0"""

        # Rename fields
        if 'company_name' in data:
            data['buyer_name'] = data.pop('company_name')

        # Add new required fields with defaults
        if 'include_escrow' not in data:
            data['include_escrow'] = False

        # Convert data types
        if 'purchase_price' in data:
            data['purchase_price'] = float(data['purchase_price'])

        # Handle removed fields
        if 'old_field' in data:
            self.log_warning(f"Field 'old_field' no longer supported, value discarded")
            del data['old_field']

        return data

    def validate_compatibility(self, answer_file_version, template_version):
        """Check if answer file is compatible with template version"""

        # Exact match - always compatible
        if answer_file_version == template_version:
            return True

        # Same major version - likely compatible
        if self.major_version(answer_file_version) == self.major_version(template_version):
            return True

        # Different major version - need migration
        return False
```

### Backward Compatibility Testing

```python
def test_backward_compatibility():
    """Test template with answer files from previous versions"""

    template_v2 = load_template('stock_purchase_agreement_v2.0.0.docx')

    # Test with v1.0.0 answer file
    answers_v1_0 = load_answer_file('test_data/answers_v1.0.0.json')
    doc = generate_document(template_v2, answers_v1_0)
    assert validate_document(doc)

    # Test with v1.1.0 answer file
    answers_v1_1 = load_answer_file('test_data/answers_v1.1.0.json')
    doc = generate_document(template_v2, answers_v1_1)
    assert validate_document(doc)

    # Test with v2.0.0 answer file (current)
    answers_v2_0 = load_answer_file('test_data/answers_v2.0.0.json')
    doc = generate_document(template_v2, answers_v2_0)
    assert validate_document(doc)
```

## Deployment and Release

### Release Checklist

```markdown
# Release Checklist for Template v2.0.0

## Pre-Release
- [ ] All tests passing
- [ ] Backward compatibility verified
- [ ] Migration scripts tested
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version numbers updated in all files
- [ ] Security review completed

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] User acceptance testing completed
- [ ] Performance testing acceptable
- [ ] Cross-platform testing completed

## Documentation
- [ ] User guide updated
- [ ] API documentation updated (if applicable)
- [ ] Training materials updated
- [ ] Release notes prepared

## Deployment
- [ ] Backup current production version
- [ ] Deploy to staging environment
- [ ] Verify staging deployment
- [ ] Deploy to production
- [ ] Verify production deployment
- [ ] Update version in template registry

## Post-Release
- [ ] Monitor error logs
- [ ] Collect user feedback
- [ ] Update support documentation
- [ ] Archive old version
```

### Release Process

```bash
#!/bin/bash
# Release script for template deployment

VERSION=$1
TEMPLATE_NAME=$2

echo "Releasing $TEMPLATE_NAME version $VERSION"

# Run tests
echo "Running tests..."
pytest tests/test_${TEMPLATE_NAME}.py
if [ $? -ne 0 ]; then
    echo "Tests failed. Aborting release."
    exit 1
fi

# Update version in metadata
echo "Updating version metadata..."
python scripts/update_version.py $TEMPLATE_NAME $VERSION

# Create git tag
echo "Creating git tag..."
git tag -a v$VERSION -m "Release version $VERSION"

# Build release package
echo "Building release package..."
python scripts/build_release.py $TEMPLATE_NAME $VERSION

# Deploy to production
echo "Deploying to production..."
python scripts/deploy.py $TEMPLATE_NAME $VERSION --environment production

# Create release notes
echo "Creating release notes..."
python scripts/generate_release_notes.py $VERSION > releases/v$VERSION.md

echo "Release complete!"
```

## Audit Trail

### Change Tracking

```python
class TemplateAuditLog:
    """Track all changes to templates"""

    def log_change(self, template_id, user, change_type, description, details=None):
        """Log a template change"""

        entry = {
            'timestamp': datetime.now().isoformat(),
            'template_id': template_id,
            'user': user,
            'change_type': change_type,  # created, modified, deleted, deployed
            'description': description,
            'details': details or {},
            'version': self.get_current_version(template_id)
        }

        self.audit_log.append(entry)
        self.persist_log()

    def get_change_history(self, template_id, start_date=None, end_date=None):
        """Retrieve change history for a template"""

        entries = [e for e in self.audit_log if e['template_id'] == template_id]

        if start_date:
            entries = [e for e in entries if e['timestamp'] >= start_date]
        if end_date:
            entries = [e for e in entries if e['timestamp'] <= end_date]

        return sorted(entries, key=lambda x: x['timestamp'], reverse=True)
```

## Best Practices

1. **Commit Often**: Small, focused commits are easier to understand and revert
2. **Use Branches**: Isolate changes in feature branches
3. **Write Clear Messages**: Future you will thank present you
4. **Tag Releases**: Tag production versions for easy reference
5. **Maintain Changelog**: Document what changed and why
6. **Test Before Committing**: Don't commit broken templates
7. **Review Changes**: Use pull requests for peer review
8. **Backup Before Major Changes**: Always have a rollback option
9. **Version Everything**: Templates, components, test data
10. **Document Breaking Changes**: Help users migrate smoothly

Version control is not just about tracking changes—it's about enabling collaboration, ensuring quality, and maintaining confidence in your document automation system.

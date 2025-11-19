# Keep a Changelog Format Reference

## Overview

Keep a Changelog is a standardized format for maintaining human-friendly changelogs. This reference provides guidelines and examples for implementing this format in your projects.

## Official Specification

Based on https://keepachangelog.com/ (v1.1.0)

## Format Structure

```
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Now removed features

### Fixed
- Any bug fixes

### Security
- Vulnerability fixes

## [1.0.0] - 2024-01-15

### Added
- Initial public release

[Unreleased]: https://github.com/user/project/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/user/project/releases/tag/v1.0.0
```

## Section Types

### Added
New features and functionality introduced in this release.

```markdown
### Added
- Support for custom configuration files
- New `--verbose` flag for detailed logging
- User authentication system with OAuth2 support
- Export functionality to JSON and CSV formats
```

### Changed
Changes to existing functionality. This typically includes improvements, refactoring, and behavior modifications.

```markdown
### Changed
- Improved performance of database queries by 50%
- Updated user interface with new design system
- Changed default timeout from 30s to 60s
- Refactored authentication module for better maintainability
```

### Deprecated
Features that will be removed in future releases. Guide users to alternatives.

```markdown
### Deprecated
- The `--old-format` flag is deprecated; use `--new-format` instead
- Function `getUser()` is deprecated; use `fetchUserData()` instead
- Legacy XML support will be removed in v3.0.0
- Environment variable `OLD_API_KEY` is deprecated; use `API_KEY` instead
```

### Removed
Features that have been removed in this release.

```markdown
### Removed
- Removed support for Python 2.7
- Removed deprecated `--old-format` flag
- Removed legacy XML parser (use JSON instead)
- Removed Internet Explorer 11 compatibility
```

### Fixed
Bug fixes and patches.

```markdown
### Fixed
- Fixed critical memory leak in background worker
- Fixed incorrect calculation in discount module
- Fixed crash when processing empty datasets
- Fixed encoding issue with special characters
```

### Security
Security fixes and vulnerability patches.

```markdown
### Security
- Fixed SQL injection vulnerability in search module
- Patched XSS vulnerability in comment system
- Updated dependencies to address CVE-2024-1234
- Fixed authentication bypass in API v1
```

## Complete Example

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Dark mode theme option
- User profile customization
- Performance metrics dashboard
- Export reports in PDF format

### Changed
- Improved email validation algorithm
- Updated documentation with new examples
- Refactored API authentication layer

### Deprecated
- Legacy CSV import method; use the new UI instead

### Fixed
- Fixed typo in welcome message
- Fixed race condition in concurrent uploads

## [2.1.0] - 2024-01-15

### Added
- Two-factor authentication support
- Mobile app companion application
- Advanced search filters
- User activity logging

### Changed
- Updated database schema for better performance
- Changed default language detection logic
- Improved error messages for clarity

### Deprecated
- Old authentication method deprecated in favor of OAuth2

### Fixed
- Fixed bug where passwords weren't encrypted properly
- Fixed issue with timezone conversion in reports

## [2.0.0] - 2023-12-01

### Added
- REST API v2 with improved endpoints
- Database query optimization
- Automated backup system
- New notification system

### Changed
- Major API redesign (breaking changes)
- Changed database structure
- Completely rewrote authentication module

### Removed
- Removed deprecated REST API v1
- Removed support for MySQL 5.5
- Removed legacy caching mechanism

### Fixed
- Fixed critical security vulnerability in login

### Security
- Implemented rate limiting on API endpoints
- Updated all dependencies to patch security issues

## [1.1.0] - 2023-10-15

### Added
- New admin dashboard
- User role-based access control
- Bulk import functionality
- Email notification templates

### Changed
- Simplified configuration process
- Improved database indexing

### Fixed
- Fixed bug in report generation
- Fixed email delivery issues

## [1.0.0] - 2023-08-01

### Added
- Initial release with core features
- User registration and login
- Basic content management
- Email notifications
- File upload capability

[Unreleased]: https://github.com/user/project/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/user/project/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/user/project/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/user/project/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/user/project/releases/tag/v1.0.0
```

## Best Practices

### Date Format
Use ISO 8601 format: `YYYY-MM-DD`

```markdown
## [1.0.0] - 2024-01-15 ✓ (Correct)
## [1.0.0] - January 15, 2024 ✗ (Less standardized)
## [1.0.0] - 01/15/2024 ✗ (Ambiguous)
```

### Version Links
Always provide links to compare versions and view releases:

```markdown
[Unreleased]: https://github.com/user/project/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/user/project/releases/tag/v1.0.0
```

### Unreleased Section
Keep an [Unreleased] section at the top for upcoming changes:

```markdown
## [Unreleased]

### Added
- Feature currently in development

### Changed
- Modification in progress
```

### Entry Organization
- Order entries by importance within each section
- Use verb + object format for clarity
- Keep entries concise but descriptive

```markdown
### Added
- User authentication system ✓ (Clear and specific)
- Feature ✗ (Too vague)
- Support for multiple language packs ✓ (Specific)
```

### Pre-release Versions
Include pre-release versions with appropriate sections:

```markdown
## [1.0.0-rc.1] - 2024-01-10

### Added
- Feature X
- Feature Y (may change before 1.0.0)

## [1.0.0-beta.1] - 2024-01-05

### Added
- Early version of feature Z
```

## Common Mistakes to Avoid

1. **Outdated [Unreleased] section**
   - ❌ Never updating [Unreleased] before releases
   - ✓ Keep it current with recent changes

2. **Missing version links**
   - ❌ No links to compare versions
   - ✓ Always include compare URLs

3. **Inconsistent formatting**
   - ❌ Mixing bullet styles: `- Item`, `* Item`, `+ Item`
   - ✓ Use consistent bullet markers

4. **Generic descriptions**
   - ❌ "Fixed stuff" or "Improved things"
   - ✓ "Fixed memory leak in cache" or "Improved API response time"

5. **Wrong date format**
   - ❌ Using American date format
   - ✓ Use ISO 8601: YYYY-MM-DD

6. **Sections for unreleased items**
   - ❌ Only showing "## [Unreleased]" without subsections
   - ✓ Organize with Added, Changed, Fixed, etc.

7. **Technical jargon without context**
   - ❌ "Refactored ORM layer"
   - ✓ "Refactored ORM layer for better query performance"

## Integration with Git

### Auto-generate Links
```bash
# GitHub
[Version]: https://github.com/user/project/compare/v1.0.0...v1.1.0

# GitLab
[Version]: https://gitlab.com/user/project/-/compare/v1.0.0...v1.1.0

# Gitea
[Version]: https://gitea.example.com/user/project/compare/v1.0.0...v1.1.0
```

### Git Tags
Tag each release to match changelog versions:

```bash
git tag v1.0.0
git tag v1.1.0
git tag v2.0.0
```

## Tools for Changelog Management

### Automated Generation
- **Keep a Changelog Bash Script:** Automate entry additions
- **Changelog Python Library:** Programmatic changelog management
- **auto:** Generates changelogs from commits

### Validation Tools
- **Validate Keep a Changelog:** Check format compliance
- **Markdownlint:** Validate markdown syntax

## Tips for Maintenance

1. **Update immediately:** Add entries as features are completed
2. **Be consistent:** Maintain consistent formatting and style
3. **Version control:** Keep changelog.md in version control
4. **Review before release:** Audit all entries before publishing
5. **Use templates:** Create section templates for faster entry
6. **Link everything:** Always provide context links

## Template

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [1.0.0] - YYYY-MM-DD

### Added
- Initial release

[Unreleased]: https://github.com/user/project/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/user/project/releases/tag/v1.0.0
```

## Summary

Keep a Changelog provides a standardized, human-readable format for documenting changes. Following this format makes it easier for users to understand what changed and why in each release.

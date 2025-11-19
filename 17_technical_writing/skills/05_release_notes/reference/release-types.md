# Release Types: Definitions and Guidelines

## Overview

Different types of releases serve different purposes in software development. This guide provides definitions, characteristics, and examples for each release type.

## Release Type Categories

## 1. Major Release

### Definition
A **major release** introduces significant new features, major improvements, or breaking changes that are incompatible with previous versions.

### Characteristics
- Version increment: `X.0.0` where X increases by 1
- Requires migration/upgrade from previous version
- May include removed or significantly changed APIs
- Extensive testing and documentation required
- Marketing and announcement typically involved

### Examples
```
0.1.0 → 1.0.0 (First stable release)
1.5.3 → 2.0.0 (Major redesign or breaking change)
2.3.1 → 3.0.0 (API overhaul)
```

### What Triggers a Major Release
- Complete API redesign
- Removing major features
- Fundamental architecture changes
- Large breaking changes that require code updates

### Release Notes Example
```markdown
## [2.0.0] - 2024-01-15

### Major Features
- Complete REST API redesign with new endpoint structure
- New authentication system replacing legacy approach
- Support for WebSocket connections for real-time updates

### Breaking Changes
- Removed XML support (use JSON instead)
- Changed all endpoint paths (/api/v1/* → /api/*)
- Renamed database models and fields
- Required Node 16+ (dropped Node 12 support)

### Migration Guide
[Detailed migration guide provided]

### Deprecation Timeline
- v1.x will receive critical security patches until 2024-06-01
- After that date, v1.x will be unsupported
```

### Release Checklist
- [ ] Security audit completed
- [ ] All tests passing
- [ ] Documentation updated for breaking changes
- [ ] Migration guide prepared
- [ ] Deprecation timeline communicated
- [ ] Beta/RC version released and tested
- [ ] API documentation updated
- [ ] Announcement prepared
- [ ] Launch scheduled with team alignment

---

## 2. Minor Release

### Definition
A **minor release** introduces new features and improvements while maintaining backward compatibility. Existing code continues to work without modification.

### Characteristics
- Version increment: `X.Y.0` where Y increases by 1, X stays same
- Backward compatible with previous versions in same major version
- May deprecate features (warning, not removal)
- New optional parameters or features
- Generally safe to upgrade

### Examples
```
1.0.0 → 1.1.0 (New feature added)
1.5.2 → 1.6.0 (Multiple features and improvements)
2.3.5 → 2.4.0 (New optional functionality)
```

### What Triggers a Minor Release
- New features without breaking changes
- New optional parameters to existing functions
- Enhanced functionality to existing features
- New modules or subsystems (backward compatible)
- Performance improvements

### Release Notes Example
```markdown
## [1.5.0] - 2024-01-10

### New Features
- Add batch processing API for bulk operations
- Implement caching layer for improved performance
- New export formats: Excel and PDF
- Dark mode support in web UI

### Enhancements
- Improved search algorithm accuracy by 25%
- Faster database query execution
- Better error messages for debugging

### Deprecations
- `getUser()` deprecated; use `fetchUser()` instead (will be removed in v2.0)
- Legacy CSV export format deprecated; use new format

### Bug Fixes
- Fixed typo in error message
- Fixed timezone conversion issue

### Migration Notes
No migration required. All existing code continues to work.
New features are opt-in and backward compatible.
```

### Release Checklist
- [ ] All tests passing
- [ ] Documentation updated for new features
- [ ] Backward compatibility verified
- [ ] Changelog updated
- [ ] Examples provided for new features
- [ ] Release notes prepared
- [ ] Version bumped appropriately
- [ ] Branch protection bypassed for merge

---

## 3. Patch Release

### Definition
A **patch release** contains bug fixes and security updates. No new features are added; it fixes existing functionality while maintaining complete backward compatibility.

### Characteristics
- Version increment: `X.Y.Z` where Z increases by 1
- 100% backward compatible
- Fast to develop and release
- Can be released frequently
- Usually low risk

### Examples
```
1.0.0 → 1.0.1 (Bug fix)
1.5.2 → 1.5.3 (Security patch)
2.3.5 → 2.3.6 (Bug fix)
```

### What Triggers a Patch Release
- Bug fixes
- Security vulnerabilities
- Performance improvements (non-breaking)
- Documentation corrections
- Test improvements

### Release Notes Example
```markdown
## [1.0.1] - 2024-01-05

### Bug Fixes
- Fixed memory leak in background worker
- Resolved race condition in concurrent file uploads
- Fixed incorrect tax calculation for certain regions
- Corrected validation logic for email addresses

### Security
- Updated dependency with security vulnerability patch
- Fixed XSS vulnerability in comment rendering

### Performance
- Improved database query performance by optimizing indexes
- Reduced API response time by 200ms

No breaking changes. Safe to upgrade.
```

### Release Checklist
- [ ] Bug verified and reproduced
- [ ] Fix implemented and tested
- [ ] Tests updated/added
- [ ] Documentation checked
- [ ] Changelog entry added
- [ ] Version bumped
- [ ] Release notes prepared

---

## 4. Hotfix Release

### Definition
A **hotfix** is an emergency release created to address critical issues in production. It's typically branched from the latest production release and fast-tracked to deployment.

### Characteristics
- Created from production branch (not development)
- Minimal changes (only the fix)
- Follows patch versioning: `X.Y.Z+1`
- Expedited review process
- Deployed immediately to production
- Merged back to development branch

### Examples
```
Production: 1.2.3
↓
Critical bug discovered
↓
Create hotfix/1.2.4 branch from v1.2.3 tag
↓
Apply minimal fix
↓
Test thoroughly
↓
Release as 1.2.4
↓
Merge back to main development branch
```

### When to Use Hotfix
- Security vulnerability in production
- Critical bug affecting users
- Data corruption issues
- Complete service outages
- Revenue/business impacting bugs

### Git Workflow (GitFlow)
```bash
# Start hotfix from production tag
git checkout -b hotfix/1.2.4 v1.2.3

# Minimal changes
# Fix the bug
git commit -m "fix: critical issue affecting login"

# Test thoroughly
npm test

# Merge to main/production
git checkout main
git merge --no-ff hotfix/1.2.4
git tag v1.2.4

# Merge back to develop
git checkout develop
git merge --no-ff hotfix/1.2.4

# Clean up
git branch -d hotfix/1.2.4
```

### Release Notes Example
```markdown
## [1.2.4] - 2024-01-03 - HOTFIX

### Critical Bug Fixes
- Fixed authentication bypass allowing unauthorized access (SECURITY)
- Resolved database connection crash on high load (CRITICAL)

This is a critical security and stability fix. All users should upgrade immediately.

**Impact:** Fixes complete service outage for 0.5% of users under specific conditions.
```

### Hotfix Checklist
- [ ] Verify bug is indeed critical
- [ ] Create branch from production tag
- [ ] Implement minimal fix only
- [ ] Thorough testing in staging
- [ ] Security review if applicable
- [ ] Get approval from leads
- [ ] Deploy to production
- [ ] Monitor after deployment
- [ ] Merge back to development
- [ ] Communicate with users
- [ ] Post-mortem scheduled

---

## 5. Release Candidate (RC)

### Definition
A **release candidate** is a pre-release version expected to be the final release unless significant bugs are found. It allows users to test before official release.

### Characteristics
- Version: `X.Y.Z-rc.N` (rc.1, rc.2, etc.)
- Feature complete
- All planned features included
- All tests passing
- Ready for production if no issues found
- Can iterate quickly if bugs discovered

### Examples
```
1.0.0-rc.1 → 1.0.0-rc.2 (bug found and fixed)
1.0.0-rc.2 → 1.0.0-rc.3 (another issue)
1.0.0-rc.3 → 1.0.0 (approved for release)
```

### When to Release RC
- Feature freeze complete
- All planned features implemented
- Comprehensive testing done
- Documentation prepared
- Ready for final evaluation

### Release Notes Example
```markdown
## [1.0.0-rc.1] - 2024-01-01

Release Candidate 1 for version 1.0.0

This is a pre-release version. Please test thoroughly and
report any issues. This is expected to become 1.0.0 unless
critical issues are discovered.

### What's Included
- All planned features for 1.0.0
- Complete API documentation
- Migration guides from 0.x versions

### Known Issues
- [List any known issues that will be addressed before 1.0.0]

### Test Focus Areas
- Please focus testing on: [specific areas]
- Known compatibility issues: [list if any]

## Feedback
Report issues at: [issue tracker or email]
Please include version 1.0.0-rc.1 in bug reports.
```

### RC Testing Checklist
- [ ] All features implemented and tested
- [ ] Documentation complete
- [ ] Known issues documented
- [ ] Test coverage adequate (>80%)
- [ ] Performance benchmarks met
- [ ] Security audit passed
- [ ] Compatibility testing done
- [ ] User feedback incorporated
- [ ] Deployment instructions verified

---

## 6. Beta Release

### Definition
A **beta** is a pre-release version with major features complete but may have bugs. It's released for wider testing and feedback.

### Characteristics
- Version: `X.Y.Z-beta.N`
- Not all features necessarily complete
- Known issues are expected
- Not recommended for production
- Used for community feedback
- Can be longer duration than RC

### Examples
```
1.0.0-beta.1 (initial beta)
1.0.0-beta.2 (feedback incorporated)
1.0.0-beta.3 (more refinement)
1.0.0-rc.1 (feature complete, move to RC)
```

### When to Release Beta
- Core functionality working
- Ready for external testing
- Want broader community feedback
- Need real-world usage data
- Not ready for RC yet

### Release Notes Example
```markdown
## [2.0.0-beta.1] - 2023-12-15

Beta 1 for version 2.0.0

We're excited to introduce the first beta of version 2.0.0!
This release includes major new features and improvements,
but is not yet recommended for production use.

### Major Features
- New REST API v2
- Enhanced authentication system
- Redesigned user interface

### Known Limitations
- Performance tuning not complete
- Some edge cases not handled
- Documentation still being written
- Mobile experience needs work

### Feedback Needed
- API design feedback
- Performance concerns
- Mobile usability
- Feature requests

### Issues and Support
Beta builds are not supported. For issues, use the
[GitHub Issues](github.com/project/issues) tracker.
```

### Beta Testing Checklist
- [ ] Core features working
- [ ] Known issues documented
- [ ] Community access set up
- [ ] Feedback channels open
- [ ] Issue tracking system ready
- [ ] Documentation in progress
- [ ] Performance baseline set

---

## 7. Alpha Release

### Definition
An **alpha** is an early pre-release for initial testing and feedback. Features may be incomplete or change significantly.

### Characteristics
- Version: `X.Y.Z-alpha.N`
- Early development phase
- Features may be incomplete
- Significant changes expected
- Internal testing focus
- Not for public use typically

### Examples
```
1.0.0-alpha.1 (initial version)
1.0.0-alpha.2 (more features added)
1.0.0-alpha.3 (more refinement)
1.0.0-beta.1 (move to beta)
```

### When to Release Alpha
- Want early feedback
- Getting team alignment
- Testing infrastructure
- Feature exploration
- Proof of concept validation

---

## 8. Development/Snapshot Release

### Definition
A **development** or **snapshot** release represents the current state of the development branch. Not recommended for any use except developers.

### Characteristics
- Version: `X.Y.Z-SNAPSHOT` or `X.Y.Z-dev`
- Highly unstable
- Changes frequently
- For development team only
- Not published typically

### Examples
```
2.0.0-SNAPSHOT
3.0.0-dev
4.1.0-dev-20240115
```

---

## Release Schedule Comparison

| Type | Version | Duration | Risk | Frequency |
|------|---------|----------|------|-----------|
| Major | X.0.0 | 3-6 months | High | 1-2/year |
| Minor | X.Y.0 | 2-4 weeks | Low | Monthly |
| Patch | X.Y.Z | 1-2 weeks | Very Low | As needed |
| Hotfix | X.Y.Z | 1-2 days | Emergency | As needed |
| RC | X.Y.Z-rc.N | 1-2 weeks | Medium | Per release |
| Beta | X.Y.Z-beta.N | 2-4 weeks | Medium-High | Per release |
| Alpha | X.Y.Z-alpha.N | 1-2 weeks | High | Per release |

---

## Branching Strategy by Release Type

### Semantic Branching
```
main              # Production (major/minor/patch releases)
  ├─ release/x.y.0   # Feature branch for release
  ├─ hotfix/x.y.z    # Critical fix branch
  └─ develop         # Development (alpha/beta/rc)
      ├─ feature/*   # Feature branches
      └─ bugfix/*    # Bug fix branches
```

### Release Flow
```
Development Cycle
develop → alpha → beta → rc → release
                              ↓
                            main (production)
                              ↓
              ← merge back ←
```

---

## Communication Template by Release Type

### Major Release Announcement
```
Subject: Version X.0.0 Available - Major Update with Breaking Changes

This major release includes significant improvements and new features.
Important: This version has breaking changes. See migration guide.

[Key features, benefits, breaking changes, migration instructions]
```

### Minor Release Announcement
```
Subject: Version X.Y.0 Available - New Features and Improvements

New features: [list]
No breaking changes. Existing code continues to work.
```

### Patch Release Announcement
```
Subject: Version X.Y.Z Available - Bug Fixes and Improvements

This patch release fixes critical issues:
- [bug 1]
- [bug 2]

Recommended to upgrade.
```

### Hotfix Release Announcement
```
Subject: URGENT: Version X.Y.Z Available - Critical Fix

A critical issue has been identified and fixed.
All users should upgrade immediately.
```

---

## Summary Table

| Release Type | Purpose | When | Version | Risk |
|--------------|---------|------|---------|------|
| Major | Breaking changes, major features | Planned | X.0.0 | High |
| Minor | New features, enhancements | Scheduled | X.Y.0 | Low |
| Patch | Bug fixes, security | Regular | X.Y.Z | Minimal |
| Hotfix | Critical production bugs | Emergency | X.Y.Z | Emergency |
| RC | Pre-release testing | Before release | X.Y.Z-rc.N | Medium |
| Beta | Early feedback | Weeks before | X.Y.Z-beta.N | Medium-High |
| Alpha | Initial feedback | Months before | X.Y.Z-alpha.N | High |

Each release type serves a specific purpose in the software development lifecycle and should be used appropriately based on project needs.

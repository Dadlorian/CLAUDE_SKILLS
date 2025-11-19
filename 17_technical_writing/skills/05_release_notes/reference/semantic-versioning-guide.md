# Semantic Versioning (SemVer) Complete Guide

## Overview

Semantic Versioning (SemVer) is a versioning scheme that uses three numbers separated by periods: **MAJOR.MINOR.PATCH**. This guide provides a comprehensive reference for implementing SemVer in your projects.

## Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]

Examples:
1.0.0
2.3.5
1.0.0-alpha
1.0.0-beta.1
1.0.0+20130313144700
1.0.0-beta+exp.sha.5114f85
```

## Core Principles

### MAJOR Version
- **Increment when:** Making incompatible API changes
- **Example:** Removing a public method, changing function signatures, breaking database schema
- **User impact:** HIGH - requires code updates
- **Reset:** MINOR and PATCH to 0

```
0.x.x → 1.0.0 (first stable release)
1.2.3 → 2.0.0 (breaking change)
```

### MINOR Version
- **Increment when:** Adding functionality in a backwards-compatible manner
- **Example:** New features, new optional parameters, deprecating functions
- **User impact:** LOW - existing code continues to work
- **Reset:** PATCH to 0, MAJOR stays same

```
1.0.0 → 1.1.0 (new feature)
1.5.2 → 1.6.0 (new feature)
```

### PATCH Version
- **Increment when:** Making backwards-compatible bug fixes
- **Example:** Bug fixes, performance improvements, security patches
- **User impact:** MINIMAL - transparent update
- **Reset:** None - just increment

```
1.0.0 → 1.0.1 (bug fix)
2.3.5 → 2.3.6 (security patch)
```

## Pre-release Versions

Pre-release versions are denoted by appending a hyphen and identifiers:

```
1.0.0-alpha         # Development version
1.0.0-alpha.1       # First alpha release
1.0.0-beta          # Beta version
1.0.0-beta.2        # Second beta version
1.0.0-rc.1          # Release candidate
1.0.0-rc.2          # Second release candidate
```

### Pre-release Ordering
```
1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-alpha.beta
< 1.0.0-beta < 1.0.0-beta.2 < 1.0.0-beta.11
< 1.0.0-rc.1 < 1.0.0
```

### When to Use
- **alpha:** Early development, expect significant changes
- **beta:** Feature complete, testing phase
- **rc (Release Candidate):** Ready for release, final testing
- **dev/snapshot:** Interim development builds

## Build Metadata

Build metadata is appended after a plus sign and is ignored when determining version precedence:

```
1.0.0+20130313144700       # Build timestamp
1.0.0+exp.sha.5114f85      # Build hash
1.0.0+001                   # Build number
1.0.0+build.123            # Build identifier
```

**Important:** Build metadata should NOT be used to differentiate versions for version control.

## Version Precedence

```
1.0.0 < 1.0.1 < 1.1.0 < 2.0.0

Comparison rules:
- Major, minor, patch are compared numerically
- Precedence is determined left to right
- Pre-release versions have lower precedence than release versions
- When major, minor, patch are equal, pre-release identifiers are compared
```

## Common Scenarios

### Scenario 1: First Release
```
Development phase: 0.1.0, 0.2.0, 0.3.0
↓
First stable release: 1.0.0
```

### Scenario 2: Adding Features
```
1.0.0 (release)
↓
1.1.0 (new feature)
↓
1.1.1 (bug fix)
↓
1.2.0 (new feature)
```

### Scenario 3: Breaking Change
```
1.5.3 (release)
↓
2.0.0 (breaking change - API redesign)
↓
2.0.1 (bug fix)
↓
2.1.0 (new feature)
```

### Scenario 4: Emergency Security Patch
```
1.2.5 (release)
↓
1.2.6 (security patch)
↓
2.0.0 (planned major release)
```

### Scenario 5: Development Release
```
1.0.0 (release)
↓
1.1.0-alpha (development)
↓
1.1.0-alpha.1 (first alpha)
↓
1.1.0-beta.1 (beta)
↓
1.1.0-rc.1 (release candidate)
↓
1.1.0 (official release)
```

## Special Cases

### Version 0.x.x (Pre-release)
- Everything may change
- Public API should not be considered stable
- Increment MINOR for breaking changes
- Increment PATCH for new features and bug fixes

```
0.0.1 → 0.1.0 (breaking change or API redesign)
0.1.0 → 0.1.1 (bug fix)
0.1.1 → 0.2.0 (new feature with no breaking changes)
```

### Version 1.0.0 (First Stable)
- Public API is now stable
- MAJOR changes reserved for incompatible changes only
- No longer treat as pre-release

### Yanked Versions
Mark versions as deprecated/yanked if they should not be used:
```
[YANKED] 1.2.3 - Critical bug, use 1.2.4 instead
```

## Implementation Guidelines

### Always Increment at Least One Number
```
1.0.0 → 1.0.1 ✓ (not 1.0.0 again)
```

### Clear Deprecation Path
```
Version 1.5.0:  Deprecate old_function()
Version 1.6.0:  Still available but with warning
Version 2.0.0:  Remove old_function()
```

### Document Changes
```
1.0.0 (2024-01-01)
- New: Added feature X
- Changed: Updated API for better usability
- Fixed: Critical bug in module Y
- Deprecated: old_method() - use new_method()
```

## Tools and Integration

### Version Management Tools
- **npm/yarn:** `package.json` versions
- **Python/pip:** `setup.py` or `pyproject.toml`
- **Java/Maven:** `pom.xml`
- **Ruby/Gems:** `Gemfile` and `.gemspec`
- **Rust/Cargo:** `Cargo.toml`

### Tagging and Release
```bash
git tag v1.0.0
git push origin v1.0.0
```

### Semantic Release Tools
- **semantic-release:** Automated versioning and changelog
- **Release Drafter:** Create release notes automatically
- **auto:** Semantic versioning automation
- **Standard Version:** Versioning and changelog generation

## Common Mistakes to Avoid

1. **Mixing version schemes**
   - ❌ Using 1.0 (2-digit), 1.0.0 (3-digit) inconsistently
   - ✓ Always use MAJOR.MINOR.PATCH format

2. **Not resetting patch on minor bump**
   - ❌ 1.2.5 → 1.3.0 (should be 1.3.0, not 1.3.5)
   - ✓ Always reset to 0 when incrementing a higher level

3. **Treating 0.x.x as stable**
   - ❌ Expecting no breaking changes in 0.x.x versions
   - ✓ All versions with major = 0 are unstable

4. **Breaking changes without major bump**
   - ❌ Removing method in 1.1.0
   - ✓ Save breaking changes for 2.0.0

5. **Inconsistent pre-release naming**
   - ❌ Using 1.0-dev, 1.0-alpha, 1.0-preview inconsistently
   - ✓ Use standard naming: alpha, beta, rc

## Summary

| Version | Type | When | Reset |
|---------|------|------|-------|
| MAJOR | Breaking | Incompatible API changes | Minor/Patch |
| MINOR | Feature | New functionality (backward-compatible) | Patch |
| PATCH | Fix | Bug fixes and patches | Nothing |

**Remember:** Once a version is released, never modify it. Always create a new version for any changes.

# API Versioning Strategies

## Overview

API versioning allows you to evolve your API while maintaining backward compatibility. This guide covers industry-standard versioning approaches.

---

## Versioning Strategies

### 1. URL Path Versioning (Recommended)

**Pattern**: `https://api.example.com/v1/users`

**Pros**:
- Clear and explicit
- Easy to route
- Simple for developers

**Cons**:
- URL changes with each version

**Example**:
```markdown
## API Versions

### v2 (Current)
Base URL: `https://api.example.com/v2`

### v1 (Deprecated)
Base URL: `https://api.example.com/v1`
Sunset date: 2026-01-01
```

### 2. Header Versioning

**Pattern**: `Accept: application/vnd.example.v2+json`

**Pros**:
- Clean URLs
- Flexible

**Cons**:
- Less obvious
- Harder to test

### 3. Query Parameter Versioning

**Pattern**: `https://api.example.com/users?version=2`

**Pros**:
- Simple

**Cons**:
- Easy to omit
- Not RESTful

---

## Semantic Versioning for APIs

Use **MAJOR.MINOR** versioning:

- **MAJOR** (v1, v2): Breaking changes
- **MINOR** (v1.1, v1.2): Backward-compatible additions

**What's a breaking change?**
- Removing endpoints
- Removing fields
- Changing field types
- Renaming fields
- Changing authentication

**What's non-breaking?**
- Adding endpoints
- Adding optional fields
- Adding enum values (carefully)
- Clarifying documentation

---

## Version Deprecation

```markdown
## Deprecation Policy

1. **Announcement**: 6 months before sunset
2. **Deprecation**: Mark version deprecated
3. **Feature Freeze**: No new features
4. **Sunset**: Remove version, return 410 Gone

### v1 Deprecation Timeline

- **2025-06-01**: v2 released, v1 marked deprecated
- **2025-09-01**: v1 feature freeze
- **2025-12-01**: Removal warnings in responses
- **2026-01-01**: v1 sunset (410 Gone)
```

---

## Migration Guides

```markdown
# Migrating from v1 to v2

## Breaking Changes

### 1. User email field renamed

**v1**:
```json
{
  "username": "alice@example.com"
}
```

**v2**:
```json
{
  "email": "alice@example.com"
}
```

**Migration**: Update code to use `email` instead of `username`.

### 2. Pagination changed to cursor-based

**v1**: Offset-based
```
GET /users?limit=10&offset=20
```

**v2**: Cursor-based
```
GET /users?limit=10&starting_after=usr_123
```

**Migration**: See [Pagination Guide](./pagination.md)
```

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Recommended**: URL path versioning with semantic versioning

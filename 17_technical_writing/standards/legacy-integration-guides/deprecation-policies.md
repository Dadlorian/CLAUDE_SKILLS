# Deprecation Policies

## Overview

How to deprecate features, APIs, and documentation without breaking customer trust.

---

## Deprecation Timeline

### Standard Timeline

```
┌─────────────────────────────────────────────────────┐
│  Month 0: Announcement                              │
│  ↓                                                   │
│  Month 3: Mark as deprecated in docs                │
│  ↓                                                   │
│  Month 6: Feature freeze (no new features)          │
│  ↓                                                   │
│  Month 9: Removal warnings in API responses         │
│  ↓                                                   │
│  Month 12: Sunset (feature removed)                 │
└─────────────────────────────────────────────────────┘
```

**Minimum**: 12 months for production APIs
**Exception**: Security vulnerabilities may require faster deprecation

---

## Announcement Template

```markdown
# Deprecation Notice: [Feature Name]

**Date**: 2025-11-19
**Deprecation Date**: 2025-12-01
**Sunset Date**: 2026-12-01
**Affected**: API v1, `/legacy-endpoint`

## What's changing

The `/legacy-endpoint` API endpoint will be removed on **December 1, 2026**.

## Why we're making this change

- Security: The legacy endpoint uses outdated authentication
- Performance: The new endpoint is 3x faster
- Features: v2 includes pagination, filtering, and sorting

## What you need to do

Migrate to the new `/v2/endpoint` before December 1, 2026.

### Migration steps

1. Update your API base URL from `/v1` to `/v2`
2. Update authentication to use Bearer tokens
3. Update response parsing (field names changed)

See our [migration guide](./migration-v1-to-v2.md) for details.

## Timeline

| Date | Status |
|------|--------|
| 2025-11-19 | Announcement |
| 2025-12-01 | Marked deprecated (still works) |
| 2026-06-01 | Deprecation warnings in responses |
| 2026-09-01 | Email reminders to active users |
| 2026-12-01 | Removed (returns 410 Gone) |

## Need help?

- [Migration guide](./migration.md)
- [v2 API documentation](./v2-docs.md)
- [Contact support](mailto:support@example.com)
```

---

## Documentation Updates

### Mark as Deprecated

```markdown
## ⚠️ DEPRECATED: Get User (v1)

**Status**: Deprecated as of December 1, 2025
**Sunset**: December 1, 2026
**Use instead**: [Get User (v2)](./v2/get-user.md)

This endpoint will be removed on December 1, 2026. Please migrate to v2.

---

### Original Documentation (for reference)

GET /v1/users/{id}

[Rest of documentation...]
```

### Add Migration Guide

```markdown
# Migrating from v1 to v2

## Breaking Changes

### 1. Authentication Changed

**v1**: API key in query parameter
```bash
GET /v1/users/123?api_key=abc123
```

**v2**: Bearer token in header
```bash
GET /v2/users/123
Authorization: Bearer abc123
```

**Migration**:
```javascript
// Before (v1)
const response = await fetch(`/v1/users/${id}?api_key=${apiKey}`);

// After (v2)
const response = await fetch(`/v2/users/${id}`, {
  headers: { 'Authorization': `Bearer ${apiKey}` }
});
```

### 2. Response Format Changed

**v1**:
```json
{
  "user_id": "123",
  "user_name": "Alice"
}
```

**v2**:
```json
{
  "id": "123",
  "name": "Alice",
  "email": "alice@example.com"
}
```

**Migration**:
```javascript
// Before (v1)
const userId = data.user_id;
const userName = data.user_name;

// After (v2)
const userId = data.id;
const userName = data.name;
```
```

---

## API Response Headers

Add deprecation warnings to API responses:

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 01 Dec 2026 00:00:00 GMT
Link: <https://docs.example.com/migration>; rel="deprecation"

{
  "data": {...}
}
```

**Headers**:
- `Deprecation: true` - RFC 8594 standard
- `Sunset: <date>` - RFC 8594 standard
- `Link: <url>; rel="deprecation"` - Link to migration docs

---

## Communication Plan

### 1. Announcement (Month 0)

- [ ] Publish deprecation notice
- [ ] Update documentation
- [ ] Blog post announcement
- [ ] Email to active API users
- [ ] Social media announcement

### 2. Ongoing Reminders

- [ ] Monthly: Update docs with countdown
- [ ] Month 6: Email to users still on v1
- [ ] Month 9: In-app notifications
- [ ] Month 10: Email final warning
- [ ] Month 11: Direct outreach to heavy users

### 3. Sunset (Month 12)

- [ ] Remove feature/endpoint
- [ ] Return 410 Gone with migration link
- [ ] Update documentation
- [ ] Monitor support tickets

---

## Sunset Response

```http
HTTP/1.1 410 Gone
Content-Type: application/json

{
  "error": {
    "code": "endpoint_removed",
    "message": "This endpoint was removed on December 1, 2026",
    "migration_guide": "https://docs.example.com/migration-v1-to-v2",
    "new_endpoint": "https://api.example.com/v2/users"
  }
}
```

---

## Best Practices

### ✅ Do

- Give ample notice (12+ months)
- Provide clear migration path
- Communicate multiple times
- Monitor usage before removing
- Keep deprecated docs accessible

### ❌ Don't

- Remove without warning
- Deprecate before alternative exists
- Change sunset date
- Ignore user feedback
- Delete documentation immediately

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Standards**: RFC 8594 (Sunset and Deprecation HTTP Headers)

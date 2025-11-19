# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New webhook event `payment.timeout` for failed payment attempts
- Support for scheduled refunds via API
- Bulk operations endpoint for processing multiple charges

### Changed
- Improved error messages to include actionable next steps
- Rate limit response headers now show reset time

### Security
- Updated dependencies to patch CVE-2025-0547

---

## [2.1.0] - 2025-11-19

### Added

#### New Features
- **Webhook Events**: New webhook event types for payment lifecycle:
  - `payment.queued` - When payment is queued for processing
  - `payment.timeout` - When payment processing times out
  - `payment.authorized` - When payment is authorized but not yet captured

- **Multi-Currency Support**:
  - Support for EUR, GBP, JPY, CAD, AUD
  - Automatic currency conversion (base: USD)
  - Region-specific decimal handling

- **Bulk Charges Endpoint** (`POST /v1/charges/bulk`):
  ```bash
  curl -X POST https://api.example.com/v1/charges/bulk \
    -H "Authorization: Bearer sk_live_KEY" \
    -d '{
      "charges": [
        {"amount": 1000, "currency": "usd"},
        {"amount": 2000, "currency": "eur"}
      ]
    }'
  ```

- **Rate Limit Headers**: All responses now include:
  - `X-RateLimit-Limit`: Total requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Unix timestamp of reset

#### Example Usage

```javascript
// New webhook event
webhook.on('payment.timeout', (event) => {
  console.log(`Payment ${event.charge_id} timed out after ${event.duration}ms`);
});

// New multi-currency
const charge = await api.createCharge({
  amount: 2000,
  currency: 'eur'  // NEW: Now supported
});
```

### Changed

#### Breaking Changes
- ⚠️ **Deprecated**: Query parameter API key authentication
  - **Before**: `GET /api/charges?api_key=sk_live_KEY`
  - **After**: `GET /api/charges` with header `Authorization: Bearer sk_live_KEY`
  - **Timeline**: Removed in v3.0 (December 2026)
  - **Migration Guide**: See below

- ⚠️ **Changed**: Error response format
  - **Before**: `{"error": "Error message"}`
  - **After**: `{"error": {"code": "invalid_request", "message": "..."}}`
  - **Migration**: Update error handling to use `error.code` instead of string matching

#### Enhancements
- Improved error messages now include:
  - Specific error code
  - Actionable next steps
  - Link to relevant documentation
  - Example of correct usage

**Before**:
```json
{
  "error": "Invalid amount"
}
```

**After**:
```json
{
  "error": {
    "code": "invalid_amount",
    "message": "Amount must be between $0.50 and $999,999.99",
    "documentation": "https://docs.example.com/errors#invalid_amount",
    "example": {
      "amount": 2000,
      "currency": "usd"
    }
  }
}
```

- Rate limit response headers improved:
  - More frequent updates
  - Include reset time in all responses
  - Better handling of edge cases

### Deprecated

- **API Key in Query Parameter** (`api_key=` query param):
  - Deprecated in v2.1.0
  - Marked as deprecated in v2.2.0
  - Will be removed in v3.0 (December 1, 2026)
  - Use `Authorization: Bearer` header instead

- **Legacy Authentication Header** (old format):
  - `X-API-Key: sk_live_KEY` still works but is deprecated
  - Switch to `Authorization: Bearer sk_live_KEY`
  - Old format will be removed in v3.0

### Fixed

- Fixed timeout issues with large file uploads (>100MB):
  - Increased timeout from 30s to 120s
  - Added streaming upload support
  - Resolves "Connection timeout" errors

- Fixed pagination cursor encoding:
  - Cursor now properly handles special characters
  - No longer requires manual URL encoding
  - Solves "Invalid cursor" errors

- Fixed webhook retry logic:
  - Now correctly retries failed webhooks with exponential backoff
  - Webhooks retry: 1m, 5m, 15m, 1h, 6h
  - Solves "Webhook never delivered" issues

- Fixed race condition in charge creation:
  - Duplicate charge prevention improved
  - Idempotent requests now fully supported
  - Better concurrent request handling

### Security

- Updated `uuid` dependency from 3.4.0 to 3.4.1 (patches CVE-2025-0547)
- All dependencies now use exact versions (no `~` or `^`)
- Added rate limiting to webhook endpoints (1000 req/min)

### Performance

- Improved database query performance (30% faster charge retrieval)
- Reduced API response latency by 20%
- Optimized webhook delivery (now async)

---

## [2.0.0] - 2025-10-15

### Added

- New REST API endpoints:
  - `POST /v1/charges` - Create a charge
  - `GET /v1/charges/:id` - Retrieve charge
  - `POST /v1/charges/:id/refund` - Refund charge
  - `GET /v1/customers` - List customers

- Webhook support:
  - `payment.succeeded`
  - `payment.failed`
  - `charge.refunded`

- Advanced filtering and sorting

### Changed

- **BREAKING**: Migrated from v1 to v2 API
  - Base URL: `https://api.example.com/v1/` (was v0)
  - Response format changed
  - Authentication method changed

### Removed

- **BREAKING**: Deprecated v0 API endpoints
  - Removed `POST /charges` (v0 format)
  - Removed `GET /status` endpoint
  - Removed legacy batch API

### Migration Guide

#### 1. Update base URL
```javascript
// Before (v1)
const api = 'https://api.example.com/v0/charges'

// After (v2)
const api = 'https://api.example.com/v1/charges'
```

#### 2. Update authentication
```javascript
// Before (v1)
headers: {
  'X-API-Key': 'sk_live_KEY'
}

// After (v2)
headers: {
  'Authorization': 'Bearer sk_live_KEY'
}
```

#### 3. Update response handling
```javascript
// Before (v1)
{
  "success": true,
  "data": { "id": "ch_123" }
}

// After (v2)
{
  "id": "ch_123",
  "status": "succeeded"
}
```

---

## [1.5.0] - 2025-09-01

### Added

- Bulk charging API
- Scheduled charges
- Refund support

### Fixed

- Security: Rate limiting now prevents brute force attacks
- Bug: Fixed concurrent request handling

---

## [1.0.0] - 2025-06-15

### Added

- Initial release
- Basic charge creation
- Webhook integration
- API authentication

---

## Format Guide

When adding new releases, use this format:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature 1
- New feature 2

### Changed
- Changed feature 1
- Changed feature 2

### Deprecated
- Deprecated feature 1

### Removed
- Removed feature 1

### Fixed
- Bug fix 1
- Bug fix 2

### Security
- Security update 1
```

## Version Numbering (SemVer)

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.Y.0): New features (backward compatible)
- **PATCH** (0.0.Z): Bug fixes (backward compatible)

## Release Schedule

- Patch releases: As needed (bug fixes)
- Minor releases: Monthly (new features)
- Major releases: Annually (breaking changes)

## Timeline for Deprecations

- v2.1.0: Feature deprecated, documented
- v2.2.0: Deprecation warnings added
- v2.3.0: Deprecation warnings continue
- v3.0.0: Feature removed

All deprecations include:
1. Clear messaging about what's deprecated
2. Why it's being removed
3. What to use instead
4. Timeline for removal
5. Migration examples

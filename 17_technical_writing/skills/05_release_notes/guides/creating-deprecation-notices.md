# Creating Deprecation Notices: Sunset Communication Strategy

## Table of Contents
- [Introduction](#introduction)
- [Understanding Deprecation](#understanding-deprecation)
- [Deprecation Lifecycle](#deprecation-lifecycle)
- [Communication Strategy](#communication-strategy)
- [Writing Effective Notices](#writing-effective-notices)
- [Technical Implementation](#technical-implementation)
- [Templates](#templates)
- [Examples](#examples)

## Introduction

Deprecation is the process of gradually phasing out features, APIs, or products. Unlike breaking changes that happen immediately, deprecation provides a runway—time for users to adapt before removal.

### The Business of Deprecation

Deprecation serves critical purposes:
- **Allows Evolution**: Remove technical debt while respecting users
- **Manages Expectations**: Clear timeline reduces confusion
- **Reduces Support**: Users understand what's happening
- **Builds Trust**: Demonstrates thoughtful product stewardship
- **Enables Modernization**: Free resources for new features

### Core Philosophy

Deprecation is not punishment. It's a **bridge** between old and new, giving users time to adapt while signaling the direction of product evolution.

## Understanding Deprecation

### Deprecation vs. Breaking Change

**Deprecation**:
- Feature still works
- Future removal announced
- Alternative provided
- Migration path available
- Time period given (typically 6-18 months)

**Breaking Change**:
- Feature is removed or changed
- Happens immediately
- No fallback available
- Requires urgent migration
- Usually part of major version

### What Can Be Deprecated?

- API endpoints or functions
- Configuration options
- Features or products
- Libraries or dependencies
- Workflows or user interfaces
- Behaviors or default values
- File formats or protocols

### Why Deprecate Rather Than Remove?

```
Immediate Removal
├─ Angry users
├─ Broken production systems
├─ High support burden
├─ Low product reputation
└─ Lost users to competitors

Deprecation
├─ Planned migrations
├─ Smooth transitions
├─ Reduced support issues
├─ Maintained reputation
└─ Higher user retention
```

## Deprecation Lifecycle

### Phase 1: Planning (Before Announcement)

**Activities**:
1. Identify what to deprecate and why
2. Plan replacement or alternative
3. Determine support timeline
4. Get stakeholder approval
5. Prepare communications
6. Brief support team

**Questions to Answer**:
- Why is this being deprecated?
- What's the replacement?
- How long will it be supported?
- What warnings/errors should show?
- How much notice will users get?
- What migration assistance is available?

### Phase 2: Announcement (Initial Communication)

**Timing**: 6-18 months before removal

**What to Communicate**:
- What's being deprecated
- Why it's being deprecated
- What to use instead
- Timeline for support
- Resources for migration

**Channels**:
- Blog post
- Email notification
- Release notes
- Product documentation
- In-app notifications
- Developer newsletter

**Tone**: Informational, supportive, forward-looking

```
"We're retiring the Legacy API to focus on our new REST API v2.
The Legacy API will be fully removed on [date]. We've created a
detailed migration guide to make the transition smooth. Start
migrating at your pace—you have until [date]."
```

### Phase 3: Warning Period (Active Deprecation)

**Timing**: From announcement until removal

**Technical Warnings**:
- Deprecation headers in HTTP responses
- Console warnings in libraries
- Compilation warnings
- Dashboard notifications
- Email reminders

**Support**:
- Dedicated migration guides
- Code examples
- Video tutorials
- Office hours or webinars
- Community forum support

**Resources**:
- Automated migration tools
- Configuration templates
- Reference implementations
- FAQs and troubleshooting

### Phase 4: Enforcement (Removal)

**Timing**: On scheduled removal date

**Actions**:
- Stop accepting deprecated input
- Throw clear error messages
- Return HTTP error codes
- Log removal attempts
- Provide error messages with resources

**Communication**:
- Release notes highlighting removal
- Email to users still using feature
- Updated documentation
- Support announcement

### Phase 5: Full Removal (Post-Enforcement)

**Timing**: 1-3 releases after enforcement

**Cleanup**:
- Remove deprecated code
- Delete legacy documentation
- Archive migration resources
- Update FAQ
- Close-out support tickets

## Communication Strategy

### Multi-Channel Approach

**Official Announcements**:
```
1. Blog Post
   - Detailed explanation
   - Timeline
   - Impact analysis
   - Migration resources

2. Email Notification
   - Direct to users
   - Personal and urgent
   - Include timeline
   - Link to resources

3. Release Notes
   - List under "Deprecations"
   - Explain impact
   - Link to migration guide

4. In-App Notification
   - Alert at login
   - Show only to affected users
   - Provide direct link to guide
   - Dismissible

5. Technical Warnings
   - HTTP headers
   - Console messages
   - Log entries
   - Error messages
```

### Message Hierarchy

**Level 1: The Why**
```
"We're deprecating the Legacy API v1 to improve performance,
security, and developer experience. Our new REST API v2 provides
better structure, faster responses, and more features."
```

**Level 2: The When**
```
Timeline:
- Now: Legacy API v1 available with deprecation warnings
- March 1, 2024: Warnings intensify
- June 1, 2024: Rate limiting begins
- September 1, 2024: Final support month
- October 1, 2024: Legacy API v1 fully removed
```

**Level 3: The Path**
```
Your migration path:
1. Review API v2 documentation
2. Update API client integration
3. Test in staging environment
4. Deploy to production
5. Monitor for issues
Estimated time: 4-8 hours
```

**Level 4: The Support**
```
Need help?
- Migration Guide: [link]
- API v2 Documentation: [link]
- Example Code: [link]
- Community Forum: [link]
- Support Email: [link]
- Office Hours: Every Wednesday at 2 PM EST
```

### Messaging Best Practices

1. **Be Clear About Impact**
   ```
   GOOD: "The `/users` endpoint is deprecated and will be removed
   in v4.0, affecting any code that calls this endpoint."

   POOR: "Legacy endpoint deprecated."
   ```

2. **Provide Clear Alternative**
   ```
   GOOD: "Use the `/api/v2/users` endpoint instead. See our
   migration guide for code examples."

   POOR: "Use the new endpoint."
   ```

3. **Give Specific Timeline**
   ```
   GOOD: "Support ends December 1, 2024. The endpoint will be
   completely removed in v5.0.0, released January 1, 2025."

   POOR: "Will be removed soon."
   ```

4. **Show Empathy**
   ```
   GOOD: "We understand this requires migration effort. We've
   created tools and guides to make it as smooth as possible."

   POOR: "Users must migrate immediately."
   ```

5. **Offer Support**
   ```
   GOOD: "Questions? Reply to this email, post in our forum, or
   join our office hours."

   POOR: "See documentation."
   ```

## Writing Effective Notices

### Structure of Deprecation Notice

```markdown
# [Feature Name] Deprecation Notice

## Summary
One sentence explaining what's deprecated.

## Details
- What's deprecated
- Why it's deprecated
- When it's being removed
- What to use instead

## Timeline

| Date | Event | Action |
|------|-------|--------|
| Now | Announcement | Review docs |
| [D1] | Warnings added | Begin migration |
| [D2] | Rate limiting | Accelerate migration |
| [D3] | Support ends | Complete migration |
| [D4] | Feature removed | Feature unavailable |

## Migration Guide

Link to detailed migration guide.

## Impact Analysis

Who needs to migrate:
- [User type 1]
- [User type 2]

Estimated effort:
- [Time estimate]

## Code Examples

Before and after examples.

## Support

Links to help resources.
```

### Content Guidelines

**Make It Scannable**:
```markdown
✓ Use clear headings
✓ Use bullet points
✓ Highlight key dates
✓ Use visual hierarchy
✗ Don't use paragraphs of text
✗ Don't bury important info
```

**Use Visual Markers**:
```
⚠️  WARNING: This feature will be removed.
📅 TIMELINE: [Important dates]
✅ ACTION: [What users must do]
🔗 RESOURCES: [Help links]
```

**Include Specific Information**:
```
❌ VAGUE: "The API may change in the future."
✅ SPECIFIC: "The /api/v1/users endpoint will be removed
   on June 1, 2024. Migrate to /api/v2/users by that date."
```

## Technical Implementation

### Adding Deprecation Warnings

**Python Example**:
```python
import warnings
from functools import wraps

def deprecated(message, removal_version):
    """Decorator to mark functions as deprecated."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated as of v2.0 and "
                f"will be removed in {removal_version}. "
                f"{message} "
                f"See: https://docs.example.com/migrate",
                category=DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@deprecated(
    "Use new_function() instead.",
    removal_version="v3.0"
)
def old_function():
    """This function is deprecated."""
    pass
```

**JavaScript Example**:
```javascript
function deprecated(message, removalVersion) {
    return function(target, propertyKey, descriptor) {
        const originalMethod = descriptor.value;
        descriptor.value = function(...args) {
            console.warn(
                `${propertyKey} is deprecated and will be ` +
                `removed in ${removalVersion}. ${message} ` +
                `See: https://docs.example.com/migrate`
            );
            return originalMethod.apply(this, args);
        };
        return descriptor;
    };
}

class MyClass {
    @deprecated("Use newMethod() instead.", "v3.0")
    oldMethod() {
        // Method implementation
    }
}
```

### HTTP Deprecation Headers

```
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sun, 01 Jun 2024 00:00:00 GMT
Deprecation-Date: Sun, 01 Mar 2024 00:00:00 GMT
Link: </api/v2/users>; rel="successor-version"
X-API-Warn: "This endpoint is deprecated. See docs."
```

### Error Messages

```javascript
// Clear, helpful error when deprecated feature is used
Error: The '/api/v1/users' endpoint has been removed as of v4.0.
       Migrate to '/api/v2/users' immediately.
       Migration guide: https://docs.example.com/v1-to-v2
       Contact: support@example.com
```

## Templates

### Full Deprecation Notice Template

```markdown
# [Feature/API] Deprecation Notice

**Effective**: [Version and date]
**Support Ends**: [Date]
**Removal Date**: [Version and date]

## What Is Deprecated

[Clear description of what's being deprecated]

## Why

[Explain the business and technical reasons]

## What To Do

### If You Don't Use This Feature
- No action needed
- Continue using the product normally

### If You Use This Feature

**Timeline**:
```
[Date]: Deprecation announced (now)
[Date]: Warnings added in code
[Date]: Support period begins winding down
[Date]: Feature removed (cutover date)
```

**Migration Path**:
1. [Action 1]
2. [Action 2]
3. [Action 3]

**Estimated Effort**: [X hours]

**Difficulty**: [Easy/Medium/Hard]

## Code Examples

### Before (Deprecated)
```
[code example]
```

### After (Recommended)
```
[code example]
```

## Migration Resources

- **Guide**: [Link]
- **Documentation**: [Link]
- **Examples**: [Link]
- **Community Forum**: [Link]
- **Support**: support@example.com

## FAQ

**Q: Do I need to migrate immediately?**
A: No, you have until [date]. Plan your migration accordingly.

**Q: What happens if I don't migrate by the deadline?**
A: The deprecated feature will stop working, and your application
   may fail. We strongly recommend migrating before the deadline.

**Q: Is there a tool to help with migration?**
A: Yes, see the [Migration Tool] section in our guide.

**Q: Can you migrate our code for us?**
A: Enterprise customers can request paid migration services.
   Contact sales for details.

**Q: What if I have questions?**
A: Join our community forum, attend office hours, or email support.
```

### Deprecation Notice for Release Notes

```markdown
## Deprecated Features

### Legacy Authentication System

The XML-based authentication method is deprecated as of v3.5 and
will be removed in v4.0.0 (planned for Q4 2024).

**Action Required**: Migrate to OAuth 2.0
**Timeline**: You have until [date] to migrate
**Resources**: See Authentication Migration Guide

**What You Need to Do**:
```bash
# Old (deprecated)
auth = LegacyAuth(api_key="...")

# New
auth = OAuth2(client_id="...", client_secret="...")
```

**More Info**: [Migration Guide](link)
```

### In-App Deprecation Notification

```markdown
# ⚠️  Legacy API Support Ending

Your application uses the Legacy API which will be removed on
[date].

**What This Means**:
- Your application will stop working after [date]
- You must migrate to API v2

**What You Need to Do**:
1. Review the Migration Guide
2. Update your integration
3. Test in staging
4. Deploy before [date]

**Estimated Time**: 2-4 hours

[Start Migration] [View Guide] [Get Help]
```

## Examples

### Example 1: API Endpoint Deprecation

```markdown
# /api/v1/users Endpoint Deprecation

**Status**: Deprecated as of v2.0 (March 1, 2024)
**Support Until**: June 1, 2024
**Removal**: July 1, 2024 (v2.3)

## What's Deprecated

The REST API v1 `/users` endpoint is deprecated and will be removed
in July 2024. This affects all direct API calls to:

```
GET  /api/v1/users
POST /api/v1/users
GET  /api/v1/users/{id}
PUT  /api/v1/users/{id}
DELETE /api/v1/users/{id}
```

## Why

The new API v2 provides:
- Better response structure
- Improved performance (40% faster)
- Enhanced error messages
- Better pagination
- Built-in rate limiting

## Migration Timeline

| Date | Version | Action | Your Deadline |
|------|---------|--------|---------------|
| Mar 1 | v2.0 | API v2 released | Start migration |
| Apr 1 | v2.1 | Deprecation warnings | Mid-migration |
| May 1 | v2.2 | Rate limiting starts | Final sprint |
| Jun 1 | v2.2 | Support ends | Must be done |
| Jul 1 | v2.3 | Endpoint removed | Too late! |

## How to Migrate

### Step 1: Update Your API Client

```python
# Old (deprecated)
import requests

response = requests.get('https://api.example.com/api/v1/users')
users = response.json()

# New
import requests

response = requests.get('https://api.example.com/api/v2/users')
data = response.json()
users = data['data']
```

### Step 2: Handle New Response Format

```python
# Old response format
[
  {"id": 1, "name": "John"},
  {"id": 2, "name": "Jane"}
]

# New response format
{
  "data": [
    {"id": 1, "name": "John"},
    {"id": 2, "name": "Jane"}
  ],
  "meta": {
    "total": 2,
    "page": 1
  }
}
```

### Step 3: Test

```bash
# Run your tests
pytest tests/

# Check for deprecation warnings
python -W error::DeprecationWarning your_script.py
```

### Step 4: Deploy

```bash
# Deploy to staging first
git push origin your-branch
# Verify in staging
# Deploy to production
```

## Automatic Migration Tool

We've provided a tool to help automate the migration:

```bash
# Install
npm install -g api-migrator

# Analyze your code
api-migrator analyze --path ./src --api v1

# Migrate automatically
api-migrator migrate --path ./src --from v1 --to v2

# Review changes
git diff

# Commit
git commit -m "migrate: Update API from v1 to v2"
```

## Need Help?

- **Full Migration Guide**: [Link with code examples]
- **API v2 Documentation**: [Complete API reference]
- **Code Examples**: [Python, JavaScript, Ruby, etc.]
- **Community Forum**: [Active discussion]
- **Office Hours**: Every Wednesday 2-3 PM EST
- **Enterprise Support**: support@example.com

Don't wait—start your migration today!
```

### Example 2: Configuration Option Deprecation

```markdown
# Config Option Deprecation: database_pool_size

**Status**: Deprecated in v5.1 (November 2024)
**Support Until**: December 31, 2024
**Removal**: January 1, 2025 (v5.2)

## What's Deprecated

The `database_pool_size` configuration option is deprecated. All
connection pooling is now automatic.

## Why

Our new automatic connection pooling:
- Adapts to load automatically
- Performs better in most cases
- Requires no configuration
- Reduces configuration errors

## What To Do

**Old Configuration** (deprecated):
```yaml
# config.yml
database:
  host: localhost
  pool_size: 20
  max_overflow: 10
```

**New Configuration** (recommended):
```yaml
# config.yml
database:
  host: localhost
  # pool_size removed - automatic now
```

## Remove the Option

```bash
# Option 1: Edit config.yml manually
# Remove the "pool_size" line

# Option 2: Use migration tool
config-migrator upgrade --config config.yml --target v5.2
```

## If You Don't Remove It

After January 1, 2025, this error will appear:

```
ConfigError: Unknown configuration option 'pool_size'.
This option was removed in v5.2. Remove it from your config.
See: https://docs.example.com/config-migration
```

## Verification

```bash
# Check your config has been updated
app start

# You should see:
# ✓ Configuration loaded
# ✓ Database connected (20 connections)
# [No warnings about pool_size]
```

## Questions?

- **Config Guide**: [Link]
- **Migration Docs**: [Link]
- **Community Forum**: [Link]
- **Support**: support@example.com
```

### Example 3: Feature Deprecation

```markdown
# Dashboard Widgets v1 Deprecation

**Status**: Deprecated in v6.0 (October 2024)
**Support Until**: March 31, 2025
**Removal**: April 1, 2025 (v6.2)

## What's Being Deprecated

The old Dashboard Widgets v1 system is being retired. This affects
any custom widgets built with the legacy widget API.

## New Dashboard Widgets v2

The new system offers:
- React-based components
- Better performance
- Enhanced data binding
- Improved styling options
- Community library

## Migration Path

### Check If You Have Legacy Widgets

```bash
# Run this command to identify legacy widgets
dashboard-cli find-legacy-widgets

# Output example:
# Found 3 legacy widgets:
# - /src/widgets/SalesChart.js (legacy)
# - /src/widgets/UserMetrics.js (legacy)
# - /src/widgets/ActivityFeed.js (v2 compatible)
```

### Migrate Each Widget

**Legacy Widget (v1)**:
```javascript
export class SalesChart extends Widget {
  constructor(props) {
    super(props);
    this.state = { data: [] };
  }

  render() {
    return <div>Chart: {this.state.data}</div>;
  }
}
```

**Modern Widget (v2)**:
```javascript
export function SalesChart(props) {
  const [data, setData] = useState([]);

  return <div>Chart: {data}</div>;
}

export const metadata = {
  name: "Sales Chart",
  version: "2.0",
  requiredScopes: ["sales.read"],
  configSchema: {...}
};
```

### Use Migration Tool

```bash
# Automated migration
widget-migrator migrate SalesChart.js

# Manual verification
git diff src/widgets/SalesChart.js

# Test
npm test src/widgets/SalesChart.test.js
```

## Timeline

- **Now (v6.0)**: Both v1 and v2 widgets work
- **Dec 2024 (v6.1)**: Warnings about v1 widgets
- **Jan 2025 (v6.1+)**: Deprecation notices in dashboard
- **Mar 31 (v6.1)**: Support ends
- **Apr 1 (v6.2)**: v1 widgets no longer load

## Full Audit

See all your legacy widgets:
```bash
dashboard-cli audit --legacy-only
```

## Support

- **Migration Guide**: [v1 to v2 guide]
- **Widget API Docs**: [v2 API reference]
- **Examples**: [10+ example widgets]
- **Migration Service**: [Paid widget conversion service]
- **Forum**: [Active discussions]
- **Office Hours**: Thursdays 3-4 PM EST

## Don't Delay

Start migrating your widgets today. The April 1 deadline will arrive
quickly!
```

## Best Practices Summary

1. **Announce Early**: 6-12 months before removal
2. **Be Specific**: Exact features, dates, and paths
3. **Provide Alternatives**: Always show what to use instead
4. **Make It Easy**: Tools, examples, and support
5. **Be Consistent**: Same message across channels
6. **Show Empathy**: Acknowledge user effort
7. **Follow Through**: Remove on schedule, no extensions
8. **Stay Available**: Support during transition period

## Conclusion

Deprecation is a tool for thoughtful product evolution. Done well, it
demonstrates respect for users' time and investment. Done poorly, it
creates chaos and erodes trust.

The key is **clear communication + ample time + adequate support**.

# Documenting Breaking Changes: Migration Guides and Timelines

## Table of Contents
- [Introduction](#introduction)
- [What Are Breaking Changes](#what-are-breaking-changes)
- [Communication Strategy](#communication-strategy)
- [Breaking Change Categories](#breaking-change-categories)
- [Creating Migration Guides](#creating-migration-guides)
- [Timeline Management](#timeline-management)
- [Templates](#templates)
- [Examples](#examples)

## Introduction

Breaking changes—modifications that require users to update their code, configuration, or processes—are critical moments in software evolution. Proper documentation and communication can mean the difference between smooth transitions and widespread user frustration.

### Why Breaking Changes Matter

Breaking changes impact:
- **User Workflows**: May require code changes or process updates
- **Production Systems**: Could affect live operations
- **Migration Effort**: Users must spend time updating
- **Support Load**: Increases questions and issues
- **Product Trust**: Demonstrates commitment or carelessness

### Core Principles

1. **Transparency First**: Communicate changes early and clearly
2. **Provide Path Forward**: Always offer migration guidance
3. **Give Time**: Provide adequate notice and support period
4. **Make It Easy**: Provide tools, examples, and automation
5. **Be Empathetic**: Acknowledge the burden on users

## What Are Breaking Changes

### Definition

A breaking change is any modification that causes existing code or configurations to stop working without updates from the user.

### Common Examples

**API Changes**:
- Endpoint removal or relocation
- Parameter name changes
- Response format changes
- Authentication method changes
- Rate limit changes

**Data Format Changes**:
- Database schema modifications
- File format updates
- JSON structure changes
- Serialization format changes

**Configuration Changes**:
- Deprecated config options
- Changed default behaviors
- New required parameters
- Removed configuration keys

**Library/Framework Changes**:
- Removed functions or methods
- Changed function signatures
- Modified class hierarchies
- Package structure reorganization

**Behavior Changes**:
- Changed algorithm results
- Modified sorting order
- Altered calculation methods
- Different error handling

## Communication Strategy

### Phase 1: Announcement (6 months before change)

**What to do**:
1. Publish breaking change notice
2. Explain what's changing and why
3. Announce timeline and deadlines
4. Provide migration documentation
5. Open feedback channels

**Communication Channels**:
- Blog post with comprehensive details
- Email to all users
- In-app notification
- Community forum thread
- API deprecation headers (HTTP)

**Message Template**:
```
We're improving [product/service] by [brief description of change].
This change will take effect in [version], released [date].

What you need to do:
1. [Action 1]
2. [Action 2]
3. [Action 3]

We've created a Migration Guide to help: [link]

Questions? Join our community forum: [link]
```

### Phase 2: Migration Support (3 months before change)

**What to do**:
1. Release migration tools if possible
2. Provide detailed migration guides
3. Offer migration assistance
4. Share community examples
5. Host webinars or workshops

**Activities**:
- Create video tutorials
- Publish migration checklist
- Offer code generation tools
- Provide sample configurations
- Host office hours for questions

### Phase 3: Enforcement (Release date)

**What to do**:
1. Release change in version X
2. Continue supporting old methods (with warnings)
3. Provide clear error messages
4. Link to migration resources in error text
5. Monitor user issues and update guides

**Implementation**:
```python
# Example: Deprecated method with helpful error
def old_method(param):
    raise DeprecationWarning(
        f"old_method() is deprecated as of v3.0. "
        f"Use new_method() instead. "
        f"See migration guide: https://docs.example.com/migrate"
    )
```

### Phase 4: Support Period (3-6 months after)

**What to do**:
1. Monitor and track migration issues
2. Provide extended support
3. Update guides based on feedback
4. Celebrate successful migrations
5. Plan removal of old methods

## Breaking Change Categories

### Category 1: API Endpoint Changes

**Type**: REST API, GraphQL, gRPC endpoints

**Complexity**: High (directly impacts production)

**Migration Difficulty**: Medium to High

**Example Documentation**:
```markdown
### API Endpoint Change: /api/users to /api/v2/users

**Affected Versions**: v1.0 - v1.9
**Change Version**: v2.0 (Released March 1, 2024)
**Support Until**: June 1, 2024
**Removal Version**: v3.0 (Planned December 1, 2024)

**What's Changing**:
The user endpoint is moving to the v2 API namespace.

**Before**:
```bash
GET /api/users
POST /api/users
DELETE /api/users/{id}
```

**After**:
```bash
GET /api/v2/users
POST /api/v2/users
DELETE /api/v2/users/{id}
```

**Migration Steps**:
1. Update all API endpoint URLs in your code
2. Test against staging environment
3. Deploy to production
4. Monitor error logs

**Helpful Error Message**:
```
HTTP 301 Moved Permanently
Location: /api/v2/users
X-Deprecated: true
Deprecation: true
Deprecation-Date: Sun, 01 Mar 2025 00:00:00 GMT
Sunset: Sun, 01 Dec 2025 00:00:00 GMT
Link: </api/v2/users>; rel="successor-version"
```

**Example Code**:

Python (requests):
```python
# Old (deprecated)
response = requests.get('https://api.example.com/api/users')

# New
response = requests.get('https://api.example.com/api/v2/users')
```

JavaScript (fetch):
```javascript
// Old (deprecated)
const response = await fetch('https://api.example.com/api/users');

// New
const response = await fetch('https://api.example.com/api/v2/users');
```

**Automated Migration**:
A migration tool is available: [link]
```bash
npm install -g example-api-migrator
example-api-migrator migrate --project ./
```
```

### Category 2: Data Format Changes

**Type**: Database schema, JSON structure, file formats

**Complexity**: Medium to High

**Migration Difficulty**: Medium

**Example Documentation**:
```markdown
### Response Format Change: Nested User Objects

**Summary**:
User objects are now returned in a nested structure for better
organization and to reduce redundancy.

**Before**:
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "company_id": 5,
  "company_name": "Acme Corp"
}
```

**After**:
```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  },
  "company": {
    "id": 5,
    "name": "Acme Corp"
  }
}
```

**Migration Checklist**:
- [ ] Update JSON parsing code
- [ ] Update field access patterns
- [ ] Test with new format
- [ ] Deploy to staging
- [ ] Monitor error logs
- [ ] Deploy to production

**Finding & Replacing**:

If you store JSON responses, use this script to update them:
```python
import json

def migrate_response(old_response):
    return {
        "user": {
            "id": old_response["id"],
            "name": old_response["name"],
            "email": old_response["email"]
        },
        "company": {
            "id": old_response["company_id"],
            "name": old_response["company_name"]
        }
    }
```
```

### Category 3: Configuration Changes

**Type**: Config files, environment variables, settings

**Complexity**: Medium

**Migration Difficulty**: Low to Medium

**Example Documentation**:
```markdown
### Configuration: DEPRECATED_KEY to NEW_KEY

**Old Config**:
```yaml
deprecated_key: value
```

**New Config**:
```yaml
new_key: value
```

**Migration Steps**:

1. **Update your configuration file**:
   Find and replace `deprecated_key` with `new_key`

2. **Verify behavior**:
   Test in development environment

3. **Deploy**:
   Update configuration in all environments

4. **Monitor**:
   Check logs for deprecation warnings

**Configuration Migration Tool**:
```bash
example-config-migrator --input config.yml --output config.new.yml
```
```

### Category 4: Behavioral Changes

**Type**: Algorithm changes, changed defaults, modified output

**Complexity**: Medium to High

**Migration Difficulty**: Medium to High

**Example Documentation**:
```markdown
### Behavior Change: Default Sorting Order

**What's Changing**:
Search results now sort by relevance (new behavior) instead of
creation date (old behavior).

**Why**:
Relevance-based sorting provides better results for most use cases.

**Migration**:

If you need results sorted by date, use the `sort_by` parameter:

```python
# Old (implicit behavior)
results = client.search("python")  # Sorted by date

# New (explicit control)
results = client.search("python", sort_by="relevance")
results = client.search("python", sort_by="date")
```

**Migration Checklist**:
- [ ] Review all search queries in your code
- [ ] Add explicit `sort_by` parameters where needed
- [ ] Test and verify expected sort order
- [ ] Deploy and monitor

**Before (Old)**:
```
1. Article from 2020
2. Tutorial from 2021
3. Guide from 2022
```

**After (New)**:
```
1. Guide from 2022 (most relevant)
2. Tutorial from 2021 (relevant)
3. Article from 2020 (less relevant)
```

To restore old behavior:
```python
results = client.search("python", sort_by="created_date", order="asc")
```
```

## Creating Migration Guides

### Structure of Effective Migration Guide

```markdown
# Migration Guide: Version X.Y to X+1.Y

## Overview
- Scope of changes
- Estimated migration time
- Difficulty level (easy/medium/hard)
- Who needs to migrate

## What's Changing
- Quick summary of changes
- Why the change was necessary
- Impact on users

## Step-by-Step Migration

### Step 1: [Description]
Detailed instructions with code examples

### Step 2: [Description]
Detailed instructions with code examples

## Code Examples

### Before/After Comparison
Side-by-side examples of old and new approaches

## Automated Migration
Tools, scripts, and utilities that help

## Testing Checklist
- [ ] Item 1
- [ ] Item 2

## Troubleshooting
Common issues and solutions

## Getting Help
Support resources and contacts
```

### Best Practices for Migration Guides

1. **Be Specific**
   - Exact version numbers
   - Precise changes required
   - Clear before/after examples

2. **Provide Code Examples**
   - Multiple programming languages if applicable
   - Copy-paste ready code
   - Complete, working examples

3. **Include Checklists**
   - Verifiable steps
   - Test confirmations
   - Go/no-go criteria

4. **Offer Tools**
   - Automated migration scripts
   - Configuration converters
   - Testing utilities

5. **Address Edge Cases**
   - Known gotchas
   - Conditional changes
   - Special scenarios

6. **Make It Scannable**
   - Clear headings
   - Bullet points
   - Code blocks
   - Visual hierarchy

## Timeline Management

### Semantic Versioning Approach

```
Current: v2.0.0
Breaking change planned: v3.0.0

Timeline:
v2.0: Original feature
v2.1: Deprecation warning added (Month 1)
v2.2: Better migration docs (Month 2)
v2.3-2.9: Feature still works with warnings (Months 3-6)
v3.0: Breaking change enforced (Month 6)
v4.0: Old method completely removed (Month 12)
```

### Recommended Timeline

**6 Month Minimum Deprecation**:
- **Month 0**: Feature works, no warnings
- **Month 1**: Announce deprecation, release migration guide
- **Month 2-3**: Deprecation warnings added, migration tools released
- **Month 4-5**: Migration support period, extended documentation
- **Month 6**: Breaking change released
- **Month 6-12**: Old method still works but unsupported
- **Month 12+**: Old method removed

### Communication Timeline

```
6 Months Before:
- Announce on blog
- Send email to users
- Update documentation
- Create migration guides

3 Months Before:
- Release first alpha/beta with change
- Host webinar
- Publish video tutorials
- Create code examples

1 Month Before:
- Release as stable
- Provide migration assistance
- Answer support questions
- Publish success stories

Release Day:
- Blog post announcing change
- Email notification
- Social media announcement
- In-app notification

1 Month After:
- Monitor adoption
- Publish migration stories
- Celebrate successful migrations
- Gather feedback

6 Months After:
- Plan removal of old method
- Plan next generation features
```

## Templates

### Breaking Change Notice Template

```markdown
# Breaking Change Notice: [Feature Name]

**Category**: [API/Data/Config/Behavior]
**Severity**: [Critical/High/Medium/Low]
**Affected Versions**: [v1.0 - v2.9]
**Change Version**: [v3.0]
**Release Date**: [Date]
**Support Until**: [Date]
**Full Removal**: [v4.0 planned for Date]

## Executive Summary

[1-2 sentence explanation of what's changing and why]

## What's Changing

[Detailed explanation with before/after examples]

## Who Is Affected

- [Audience 1]
- [Audience 2]
- [Audience 3]

## Impact

- [Impact 1]
- [Impact 2]
- [Impact 3]

## Migration Guide

See [Migration Guide Document] for step-by-step instructions.

Estimated migration time: [X hours/days]
Difficulty level: [Easy/Medium/Hard]

## Examples

### Before
```
[code example]
```

### After
```
[code example]
```

## Migration Tools

- [Tool 1]: [Description and link]
- [Tool 2]: [Description and link]

## Timeline

- [Date]: Deprecation announced (this release)
- [Date]: First beta release with change
- [Date]: Stable release with change
- [Date]: Sunset date - old method completely removed

## Support

- **Migration Guide**: [Link]
- **Discussion Forum**: [Link]
- **Office Hours**: [Time/Link]
- **Email Support**: support@example.com

## FAQ

**Q: Do I need to migrate immediately?**
A: No, you have until [date]. Gradual migration is recommended.

**Q: What happens if I don't migrate?**
A: Your application will stop working in version [X].

**Q: Can you migrate for me?**
A: Enterprise customers can request migration assistance.

**Q: Are there tools to help?**
A: Yes, see Migration Tools section above.
```

### Migration Guide Template

```markdown
# Migration Guide: [Old Feature] to [New Feature]

## Quick Start

For the impatient:
```bash
1. Replace [old] with [new]
2. Run test suite
3. Deploy
```

## Overview

- **Estimated Time**: X hours
- **Difficulty**: [Easy/Medium/Hard]
- **Prior Knowledge**: [Optional prerequisites]
- **Supported Until**: [Date]

## Step 1: Prepare

[Instructions on preparation]

## Step 2: Update Code

[Detailed code migration instructions with examples]

## Step 3: Update Configuration

[Configuration changes needed]

## Step 4: Test

[Testing strategies and checklist]

## Step 5: Deploy

[Deployment instructions]

## Troubleshooting

**Issue**: [Problem description]
**Solution**: [Fix]

**Issue**: [Problem description]
**Solution**: [Fix]

## Verification

After migration, verify:
- [ ] Tests pass
- [ ] Application starts
- [ ] Features work correctly
- [ ] No deprecation warnings
- [ ] Performance is acceptable

## Rollback

If needed, rollback with:
[Rollback instructions]

## Getting Help

- **Documentation**: [Link]
- **Support Forum**: [Link]
- **Email**: [Support email]
```

## Examples

### Example 1: Complete Breaking Change Documentation

```markdown
# Breaking Change: V3 API Restructure

**Affected**: All REST API clients
**Release**: v3.0.0 (March 1, 2024)
**EOL**: December 1, 2024
**Removal**: v4.0.0 (Planned)

## What's Changing

The entire API is being restructured under `/api/v2/` with improved
resource naming and response formats:

**Endpoints**:
- `/api/users` → `/api/v2/users`
- `/api/posts` → `/api/v2/posts`
- `/api/comments` → `/api/v2/comments`

**Response Format**:
Responses now include metadata:

Old:
```json
{
  "id": 1,
  "name": "John"
}
```

New:
```json
{
  "data": {
    "id": 1,
    "name": "John"
  },
  "meta": {
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

## Migration Checklist

- [ ] Update base URL in API client configuration
- [ ] Update all endpoint paths (remove old prefixes)
- [ ] Update response parsing to handle new format
- [ ] Test against staging API
- [ ] Update error handling for new error codes
- [ ] Deploy to production
- [ ] Monitor error logs for 48 hours

## Code Examples

### Python (requests)

```python
# Old (deprecated)
import requests

base_url = "https://api.example.com/api"
response = requests.get(f"{base_url}/users")
user = response.json()
print(user["name"])

# New
import requests

base_url = "https://api.example.com/api/v2"
response = requests.get(f"{base_url}/users")
data = response.json()
user = data["data"]
print(user["name"])
```

### JavaScript (Axios)

```javascript
// Old (deprecated)
import axios from 'axios';

const baseURL = 'https://api.example.com/api';
const response = await axios.get(`${baseURL}/users`);
const user = response.data;
console.log(user.name);

// New
import axios from 'axios';

const baseURL = 'https://api.example.com/api/v2';
const response = await axios.get(`${baseURL}/users`);
const user = response.data.data;
console.log(user.name);
```

## Automated Migration Tool

We've provided a migration tool to help:

```bash
# Install
npm install -g example-api-migrator

# Migrate your codebase
example-api-migrator migrate --path ./src --api-v1-to-v2

# Check for any manual changes needed
example-api-migrator check --path ./src
```

The tool handles most migrations automatically. Review the diff for
any manual changes needed.

## Timeline

- **Now (v3.0)**: New API available alongside old API
- **June 1, 2024 (v3.3)**: Deprecation warnings added to v1 API
- **September 1, 2024 (v3.6)**: v1 API rate-limited, warnings increased
- **December 1, 2024 (v3.9)**: Last release supporting v1 API
- **December 1, 2024+**: v1 API responses fail with helpful error
- **Q4 2024 (v4.0)**: v1 API completely removed

## Support

- **Migration Guide**: [Full guide with examples]
- **API Documentation**: [v2 API docs]
- **Video Tutorial**: [YouTube link]
- **Discussion**: [Forum thread]
- **Office Hours**: Every Wednesday 2-3 PM EST [Calendar invite]

## FAQ

**Can I use both old and new API?**
Yes, they work simultaneously until v4.0.

**What happens if I don't migrate?**
Your API requests will fail on v4.0.

**How long does migration take?**
Most projects: 2-4 hours. Larger projects: 1-2 days.

**Are there any breaking changes in data format?**
Response format changes (see above). Logic remains the same.
```

## Conclusion

Breaking changes are sometimes necessary for product evolution. By communicating clearly, providing comprehensive migration guidance, and giving users adequate time, you transform a potentially negative experience into an opportunity to demonstrate your commitment to continuous improvement.

Key takeaway: **Better to over-communicate than under-communicate about breaking changes.**

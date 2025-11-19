# Google Developer Documentation Style Guide - Implementation Guide

## Overview

The Google Developer Documentation Style Guide is the industry-standard reference for technical writing. This document provides an implementation guide for adopting Google's style principles in your organization's documentation.

**Official Source**: https://developers.google.com/style

**Why Google's Style Guide?**
- Industry-standard reference used by thousands of companies
- Designed specifically for developer documentation
- Clear, actionable guidelines
- Continuously updated by Google's technical writing team
- Proven track record of creating excellent developer experiences

---

## Core Principles

### 1. **Clarity Over Cleverness**

Write for global audiences with varying English proficiency levels.

**✅ Good Examples**:
```markdown
❌ BAD: "Don't put all your eggs in one basket when deploying."
✅ GOOD: "Deploy to multiple availability zones for redundancy."

❌ BAD: "The API will throw a tantrum if you send invalid data."
✅ GOOD: "The API returns a 400 error if the request data is invalid."
```

**Guidelines**:
- Avoid idioms, slang, and cultural references
- Use simple, direct language
- Define technical terms on first use
- Write for non-native English speakers

---

### 2. **Active Voice**

Use active voice to make actions clear.

**✅ Good Examples**:
```markdown
❌ PASSIVE: "The response is returned by the server."
✅ ACTIVE: "The server returns the response."

❌ PASSIVE: "Errors can be handled by implementing the catch block."
✅ ACTIVE: "Implement the catch block to handle errors."

❌ PASSIVE: "The function is called when the button is clicked."
✅ ACTIVE: "The system calls the function when you click the button."
```

**When Passive Voice is Acceptable**:
- When the actor is unknown: "The file was corrupted."
- When the action is more important than the actor: "The record was deleted."
- To avoid blaming the user: "The session was expired" (not "You let the session expire")

---

### 3. **Present Tense**

Use present tense to describe what happens, not what will happen.

**✅ Good Examples**:
```markdown
❌ FUTURE: "The function will return a promise."
✅ PRESENT: "The function returns a promise."

❌ FUTURE: "The API will respond with JSON."
✅ PRESENT: "The API responds with JSON."

❌ FUTURE: "You will see an error message."
✅ PRESENT: "An error message appears."
```

**Exception**: Use future tense for events that genuinely happen in the future:
- "The service will be unavailable during maintenance."
- "Version 2.0 will be released in Q2 2026."

---

### 4. **Second Person ("You")**

Address the reader directly.

**✅ Good Examples**:
```markdown
❌ THIRD PERSON: "The developer should configure the API key."
✅ SECOND PERSON: "Configure your API key."

❌ THIRD PERSON: "Users can authenticate using OAuth 2.0."
✅ SECOND PERSON: "You can authenticate using OAuth 2.0."
```

**Avoid**:
- "The user" (impersonal and awkward)
- "We" to refer to the reader (use "you" instead)
- "One" (overly formal)

**When to use "We"**: Only when referring to your company/product:
- "We recommend using environment variables for secrets."
- "We release updates monthly."

---

### 5. **Imperative Mood for Instructions**

Give clear, direct commands.

**✅ Good Examples**:
```markdown
❌ DESCRIPTIVE: "The next step is to install the package."
✅ IMPERATIVE: "Install the package."

❌ DESCRIPTIVE: "You should click the Save button."
✅ IMPERATIVE: "Click Save."

❌ DESCRIPTIVE: "Users are required to authenticate first."
✅ IMPERATIVE: "Authenticate before making API requests."
```

---

## Formatting Conventions

### Code Formatting

**Inline Code** - Use backticks for:
- Code elements: `function`, `variable`, `class`
- File paths: `/etc/config.yaml`
- Command-line utilities: `npm`, `git`, `docker`
- API endpoints: `POST /api/users`
- Status codes: `200 OK`, `404 Not Found`

**Code Blocks** - Use fenced code blocks with language identifiers:

```python
# ✅ Good - language specified, complete example
import os

api_key = os.getenv('API_KEY')
if not api_key:
    raise ValueError("API_KEY environment variable not set")
```

```javascript
// ✅ Good - realistic example with error handling
async function fetchUser(userId) {
  try {
    const response = await fetch(`/api/users/${userId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch user:', error);
    throw error;
  }
}
```

### Capitalization

**Title Case** - Use for:
- Document titles: "Getting Started with the API"
- H1 headings
- Product names: "Google Cloud Platform"

**Sentence Case** - Use for:
- H2-H6 headings: "Install the SDK"
- Table headers
- List items
- Navigation labels

**Examples**:
```markdown
✅ GOOD:
# Getting Started with the Authentication API

## Prerequisites

### Install the SDK

## Authenticate your requests

❌ BAD:
# getting started with the authentication api

## Prerequisites

### Install The SDK

## Authenticate Your Requests
```

### Lists

**Parallel Structure** - Keep list items grammatically consistent:

```markdown
✅ GOOD - All imperatives:
- Install Node.js
- Configure environment variables
- Run the development server

✅ GOOD - All nouns:
- Installation
- Configuration
- Execution

❌ BAD - Mixed:
- Install Node.js
- Configuration of environment variables
- Running the development server
```

**Punctuation**:
- Don't use periods for single-sentence list items
- Use periods for multi-sentence list items or when items are complete sentences

```markdown
✅ GOOD:
- Simple items without periods
- Another simple item
- Final item

✅ GOOD:
- First item is a complete sentence. It includes additional context.
- Second item is also complete. It follows the same pattern.

❌ BAD - inconsistent:
- Simple item
- Another simple item.
- Final item without punctuation
```

### Links

**Meaningful Link Text** - Link text should describe the destination:

```markdown
❌ BAD: "Click [here](https://example.com) to view documentation."
❌ BAD: "For more information, see [this page](https://example.com)."
❌ BAD: "Visit [https://example.com](https://example.com)."

✅ GOOD: "See the [API Reference](https://example.com) for details."
✅ GOOD: "Review the [authentication guide](https://example.com)."
✅ GOOD: "Learn more about [rate limiting](https://example.com)."
```

**Link Placement**: Place links at the end of sentences when possible:

```markdown
✅ BETTER: "To configure webhooks, see the webhooks guide."
    (Make "webhooks guide" a link)

⚠️ ACCEPTABLE: "See the [webhooks guide] to configure webhooks."
```

---

## Word Choice

### Preferred Terms

| ❌ Avoid | ✅ Use Instead | Reason |
|---------|---------------|---------|
| simply, just, easily, obviously | *omit* | Condescending, assumes knowledge |
| blacklist/whitelist | blocklist/allowlist | Inclusive language |
| master/slave | primary/replica, main/worker | Inclusive language |
| guys | everyone, folks, team | Gender-neutral |
| he, she | they | Gender-neutral |
| native feature | built-in feature | Inclusive language |
| sanity check | validation, verification | Ableist language |
| dummy value | placeholder, example | Ableist language |
| click here | *meaningful link text* | Accessibility, SEO |
| may | can, might | "may" implies permission |
| please | *omit in instructions* | Unnecessary in technical docs |
| e.g. | for example, such as | More accessible |
| i.e. | specifically, that is | More accessible |

### Technical Term Guidance

**API vs. Web Service**:
- Use "API" for programmatic interfaces
- Use "web service" when referring to the service itself

**Endpoint vs. Method vs. Operation**:
- **Endpoint**: The URL path (`/api/users`)
- **Method**: HTTP verb (`GET`, `POST`, `PUT`, `DELETE`)
- **Operation**: The combination (`GET /api/users`)

**Parameter vs. Argument**:
- **Parameter**: Variable in function definition (`function greet(name)`)
- **Argument**: Value passed when calling (`greet("Alice")`)
- **In practice**: These are often used interchangeably in API docs

---

## Common Patterns

### Tutorial Introduction

```markdown
# Build a real-time chat application

**Time to complete**: 30 minutes
**Prerequisites**:
- Node.js 18 or later
- Basic JavaScript knowledge
- A code editor

**What you'll learn**:
- How to establish WebSocket connections
- How to implement real-time messaging
- How to handle connection errors

By the end of this tutorial, you'll have a working chat application that supports
multiple concurrent users.

## What you'll build

[Screenshot or demo GIF]

## Before you begin

1. Install Node.js 18 or later.
2. Create a new project directory.
3. Obtain an API key from [your dashboard](https://example.com/dashboard).

## Step 1: Set up your project
```

### API Reference Entry

```markdown
## Create a user

Creates a new user account.

```http
POST /api/v1/users
```

### Request body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | User's email address. Must be unique. |
| `name` | string | Yes | User's full name. |
| `role` | string | No | User role. Default: `member`. Allowed values: `admin`, `member`, `guest`. |

### Example request

```bash
curl -X POST https://api.example.com/v1/users \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "name": "Alice Johnson",
    "role": "member"
  }'
```

### Response

Returns a `User` object if successful.

```json
{
  "id": "usr_1234567890",
  "email": "alice@example.com",
  "name": "Alice Johnson",
  "role": "member",
  "created_at": "2025-11-19T10:30:00Z"
}
```

### Errors

| Status | Error Code | Description |
|--------|------------|-------------|
| 400 | `invalid_email` | Email format is invalid |
| 409 | `email_exists` | Email already registered |
| 422 | `validation_error` | Request validation failed |
```

### Error Messages

```markdown
## Troubleshooting authentication errors

### Error: "Invalid API key"

**Cause**: The API key is malformed or doesn't exist.

**Solution**:
1. Verify you copied the full API key from your dashboard.
2. Ensure there are no extra spaces or characters.
3. Generate a new API key if the problem persists.

### Error: "API key expired"

**Cause**: API keys expire after 90 days of inactivity.

**Solution**:
1. Generate a new API key from [your dashboard](https://example.com/dashboard).
2. Update your application configuration.
3. Delete the expired key.

**Prevention**: Set up key rotation every 60 days.
```

---

## Accessibility

### Alt Text for Images

Always provide meaningful alt text:

```markdown
❌ BAD: ![image](screenshot.png)
❌ BAD: ![screenshot](screenshot.png)

✅ GOOD: ![API dashboard showing the API keys section with a "Generate New Key" button](screenshot.png)
```

### Heading Structure

Use logical heading hierarchy (don't skip levels):

```markdown
✅ GOOD:
# Document Title (H1)
## Major Section (H2)
### Subsection (H3)
#### Detail (H4)

❌ BAD:
# Document Title (H1)
### Subsection (H3) ← Skipped H2
## Major Section (H2) ← Out of order
```

### Color and Contrast

- Don't rely solely on color to convey information
- Use text labels in addition to color coding
- Ensure sufficient contrast ratios (WCAG AA minimum: 4.5:1)

```markdown
❌ BAD: "The red items are errors, green are successful."

✅ GOOD: "Failed requests are marked with ❌ and appear in red. Successful requests are marked with ✅ and appear in green."
```

---

## Numbers and Dates

### Numbers

**Spell out**:
- Numbers zero through nine (unless technical measurement)
- Numbers at the beginning of sentences

**Use numerals**:
- 10 and above
- Technical specifications (8 GB RAM, 4 CPU cores)
- Measurements (5 MB, 3.2 seconds)
- Versions (version 2, API v1)

```markdown
✅ GOOD: "The request takes approximately 200 milliseconds."
✅ GOOD: "You can create up to five API keys."
✅ GOOD: "Twenty-three users registered today." (beginning of sentence)
```

### Dates and Times

**Date Format**: Use ISO 8601 (YYYY-MM-DD) for clarity:

```markdown
✅ GOOD: 2025-11-19
⚠️ AMBIGUOUS: 11/19/2025 (US format)
⚠️ AMBIGUOUS: 19/11/2025 (EU format)
```

**Time**: Include timezone:

```markdown
✅ GOOD: "The maintenance window is 2025-11-20 02:00-04:00 UTC."
✅ GOOD: "Logs are retained for 30 days."

❌ BAD: "The meeting is at 2:00 PM." (which timezone?)
```

---

## Voice and Tone

### Professional Yet Approachable

```markdown
❌ TOO FORMAL: "One must configure the environment variables prior to execution."
✅ GOOD: "Configure your environment variables before running the application."

❌ TOO CASUAL: "Cool! Now let's install the thing and get this party started! 🎉"
✅ GOOD: "Next, install the SDK."
```

### Empathy for Errors

```markdown
❌ BLAME USER: "You forgot to set the API key."
✅ EMPATHETIC: "The API key is missing. Set the API_KEY environment variable."

❌ DISMISSIVE: "This error is obvious. Just fix your JSON."
✅ HELPFUL: "The JSON is malformed. Check for missing commas and quotes."
```

---

## Implementation Checklist

### For New Documentation

- [ ] Use active voice (90%+ of sentences)
- [ ] Use present tense for current actions
- [ ] Address reader as "you"
- [ ] Use imperative mood for instructions
- [ ] Apply consistent capitalization (sentence case for headings)
- [ ] Create parallel list structures
- [ ] Write meaningful link text
- [ ] Avoid condescending terms (simply, just, easily)
- [ ] Use inclusive language (no blacklist/whitelist, gendered pronouns)
- [ ] Provide alt text for all images
- [ ] Use logical heading hierarchy
- [ ] Format code with syntax highlighting
- [ ] Include complete, tested code examples
- [ ] Use ISO 8601 dates and include timezones

### For Existing Documentation Audits

1. **Scan for passive voice** - Use tools like Vale or Hemingway Editor
2. **Check for "you" vs "the user"** - Replace third person with second person
3. **Review word choice** - Replace non-inclusive terms
4. **Validate code samples** - Ensure all code executes successfully
5. **Check heading hierarchy** - Ensure no skipped levels
6. **Review link text** - Replace "click here" with meaningful text
7. **Verify alt text** - Add descriptions to all images

---

## Tools for Enforcement

### Vale (Automated Style Checking)

Vale is an open-source prose linter that can enforce Google's style guide.

**Installation**:
```bash
# macOS
brew install vale

# Linux/Windows
# Download from https://github.com/errata-ai/vale/releases
```

**Configuration** (`.vale.ini`):
```ini
StylesPath = styles
MinAlertLevel = suggestion

[*.md]
BasedOnStyles = Google
```

**Download Google style**:
```bash
vale sync
```

**Usage**:
```bash
# Check a file
vale docs/api-reference.md

# Check all markdown files
vale docs/**/*.md
```

### CI/CD Integration

```yaml
# .github/workflows/docs-quality.yml
name: Documentation Quality

on: [pull_request]

jobs:
  vale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: errata-ai/vale-action@v2
        with:
          files: docs
```

---

## Additional Resources

**Official Google Style Guide**:
- Full guide: https://developers.google.com/style
- Word list: https://developers.google.com/style/word-list
- Highlights: https://developers.google.com/style/highlights

**Style Guide Tools**:
- Vale: https://vale.sh
- Vale Google package: https://github.com/errata-ai/Google

**Related Guides**:
- Microsoft Writing Style Guide
- Red Hat documentation style guide
- GitLab documentation style guide

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Source**: Based on Google Developer Documentation Style Guide
**Maintenance**: Review quarterly, update with Google's style guide changes

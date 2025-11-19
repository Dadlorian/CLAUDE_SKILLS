# Formatting Conventions Guide

## Overview

Consistent formatting improves readability, scanability, and information hierarchy. This guide covers headings, lists, code, tables, and other structural elements.

## Heading Hierarchy

### Level 1 (H1)
- Used only for main document title
- One per page/section
- Style: Title Case

**Example:**
```markdown
# Getting Started with the API
```

### Level 2 (H2)
- Major section dividers
- Use for main topics
- Style: Title Case

**Example:**
```markdown
## Authentication
## Configuration
## Troubleshooting
```

### Level 3 (H3)
- Subsection dividers
- Use for sub-topics and specific contexts
- Style: Title Case

**Example:**
```markdown
### OAuth 2.0 Setup
### Bearer Token Configuration
### Session-based Authentication
```

### Level 4 (H4) and Beyond
- Rarely use beyond H4
- If needed, indicates over-complicated structure; consider restructuring
- Style: Title Case

**Example:**
```markdown
#### Generating Your Client ID
```

### Heading Guidelines

**Do:**
- Use descriptive, scannable headings
- Include keywords for search optimization
- Use parallel structure across similar headings
- Start with action words in procedural sections

**Don't:**
- Skip heading levels (don't jump from H2 to H4)
- Use ALL CAPS for headings
- Use punctuation at the end of headings
- Make headings longer than 8–10 words

**Examples:**

Good heading hierarchy:
```
# API Reference
## Authentication
### OAuth 2.0 Configuration
### Token Refresh
## Endpoints
### Users
#### Get User
#### Create User
```

Avoid:
```
# API REFERENCE
## AUTHENTICATION
### oauth2
### Refresh your tokens to maintain access
```

## List Formatting

### Unordered Lists

**Use for:**
- Items of equal importance
- Non-sequential information
- Feature lists and options

**Formatting rules:**
- Use bullets (not numbers)
- Parallel structure (all start same way grammatically)
- Capitalize first word
- No period at end if not a complete sentence; period if it is

**Examples:**

Good:
```markdown
The system supports:
- OAuth 2.0
- API keys
- Bearer tokens
```

Good (complete sentences):
```markdown
Before you start:
- Verify your internet connection is active.
- Obtain API credentials from the dashboard.
- Install the latest SDK version.
```

Avoid:
```markdown
Our system:
- OAuth 2.0 authentication
- you can use API keys
- Bearer tokens are supported
```

### Ordered Lists

**Use for:**
- Step-by-step instructions
- Ranked items
- Sequential processes

**Formatting rules:**
- Number items (1, 2, 3)
- Parallel structure
- Capitalize first word
- Use period only if items are complete sentences

**Examples:**

Good:
```markdown
To reset your password:
1. Click "Forgot Password"
2. Enter your email address
3. Check your inbox for reset link
4. Click the link and create a new password
```

Good (detailed steps):
```markdown
1. Open the dashboard and navigate to Settings.
2. Select "API Credentials" from the left menu.
3. Click "Generate New Key" and copy the value.
4. Paste the key into your application configuration.
```

### Nested Lists

**Use when:** Content has natural sub-categories

**Example:**

```markdown
1. Configure authentication
   - OAuth 2.0 setup
   - API key generation
   - Token management
2. Set up webhooks
   - Event types
   - Endpoint validation
3. Test your integration
```

**Rules for nesting:**
- Maximum 3 levels deep
- Increase indent by 2–4 spaces
- Keep consistent with parent structure
- Don't nest beyond readability

### List Punctuation

**No punctuation** (simple phrase lists):
```markdown
- Authentication
- Configuration
- Deployment
```

**With periods** (complete sentences or complex content):
```markdown
- Verify your credentials are correctly formatted.
- Update the configuration file with your API key.
- Restart the service to apply changes.
```

**Mixed approach** (when items vary in complexity):
```markdown
- API key
- OAuth 2.0 configuration (follows RFC 6749 standards)
- Bearer token (valid for 24 hours)
```

## Code Formatting

### Inline Code

**Use for:**
- Code terms, variable names, function names
- Commands, file names
- Technical identifiers

**Formatting:** Wrap in backticks

**Examples:**
```markdown
Call the `getUser()` function with the user ID.
Store the value in the `API_KEY` variable.
Edit the `config.yaml` file to enable logging.
```

**Don't:**
- Use inline code for emphasis (use **bold** instead)
- Overuse inline code (breaks readability if every other word is in code)

### Code Blocks

**Use for:**
- Multi-line code examples
- Full command blocks
- Configuration file samples
- Response examples

**Formatting rules:**
- Use three backticks with language identifier
- Indent if in a list item (4 spaces for list indentation, then code block)
- Include complete, runnable examples when possible
- Add comments explaining non-obvious lines

**Example:**

````markdown
```javascript
// Initialize the API client
const api = new APIClient({
  apiKey: process.env.API_KEY,
  timeout: 30000
});

// Make a request
api.users.get('user-123')
  .then(user => console.log(user))
  .catch(error => console.error('Error:', error));
```
````

### Code Block in Lists

**Example:**

```markdown
1. Install the SDK:
   ```bash
   npm install @company/sdk
   ```

2. Initialize in your app:
   ```javascript
   const { Client } = require('@company/sdk');
   const client = new Client({ apiKey: 'your-key' });
   ```
```

### Supported Code Block Languages

Use language identifiers for syntax highlighting:
- `bash`, `shell`
- `javascript`, `js`
- `python`
- `java`
- `json`
- `yaml`
- `xml`
- `sql`
- `go`
- `rust`

### Syntax Highlighting Rules

- Always include language identifier for color coding
- Use descriptive variable names in examples
- Show error cases and how to handle them
- Include comments for complex logic

**Good example:**

```python
# Example: Retry logic with exponential backoff
import time

def retry_request(url, max_attempts=3):
    """Make a request with automatic retry."""
    for attempt in range(max_attempts):
        try:
            response = make_request(url)
            return response
        except ConnectionError:
            wait_time = 2 ** attempt  # Exponential backoff
            time.sleep(wait_time)
    raise Exception("Failed after all retry attempts")
```

## Tables

### When to Use Tables

**Use for:**
- Parameter specifications
- Feature comparisons
- API response schemas
- Quick reference data

**Don't use for:**
- Lists (use bullet points instead)
- Complex nested data (use code blocks instead)
- Single-row data

### Table Structure

**Markdown table example:**

```markdown
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `api_key` | string | Yes | Your API authentication key |
| `timeout` | integer | No | Request timeout in seconds (default: 30) |
| `region` | string | No | Server region (default: us-east-1) |
```

### Table Formatting Rules

- Header row with column names
- Separator row with dashes
- Consistent column alignment
- Minimum 3–4 columns (if fewer, use list instead)
- Maximum 5–6 columns (if more, split or use code block)

**Alignment options:**
- Left-aligned: `|---|`
- Center-aligned: `|:-:|`
- Right-aligned: `|--:|`

**Example with alignment:**

```markdown
| Feature | Supported | Recommended |
|---------|:---------:|:-----------:|
| OAuth 2.0 | Yes | Yes |
| API Keys | Yes | No |
| Webhooks | Yes | Yes |
```

### Complex Table Content

**For complex data, consider alternative formatting:**

Instead of:
```
| Config | OAuth | Keys | Tokens |
| User ID | Required | Required | Not required |
| Callback | Required | N/A | N/A |
```

Use:
```markdown
### OAuth 2.0 Configuration
- Requires: User ID
- Requires: Callback URL
- Optional: Scopes

### API Keys
- Requires: User ID
- Generates: Secret key
```

## Special Elements

### Callouts and Warnings

**Note/Info callout:**
```markdown
> **Note:** This feature requires version 2.0 or later.
```

**Warning callout:**
```markdown
> **Warning:** Changing this setting may cause data loss.
```

**Tip callout:**
```markdown
> **Tip:** Use environment variables to store sensitive credentials.
```

### Links

**Inline links:**
```markdown
[Link text](https://example.com/page)
```

**Internal links:**
```markdown
[Configuration guide](/docs/configuration)
```

**Reference links (for long URLs):**
```markdown
For more information, see the [authentication guide][auth-guide].

[auth-guide]: https://example.com/docs/auth
```

### Emphasis

**Bold** for important terms or UI elements:
```markdown
Click the **Save** button to apply changes.
```

**Italics** for emphasis, technical titles, variable names:
```markdown
*Note: This is a required field*
```

**Code formatting** (backticks) for technical items, not emphasis.

## Whitespace and Visual Breaks

### Line Breaks

- Use blank lines between sections
- Use between lists and following text
- Use between headings and content

**Good spacing:**
```markdown
## Setup Instructions

1. Install dependencies
2. Configure settings

## Next Steps

To verify everything...
```

### Horizontal Rules

**Use sparingly** to separate major sections:
```markdown
---
```

Better alternatives:
- Use headings for section breaks
- Use whitespace between logical sections

### Indentation

- Use consistent indentation for nested lists (2–4 spaces)
- Use indentation for code blocks in lists
- Don't indent body text

## Lists and Tables Checklist

- [ ] All list items use parallel structure
- [ ] Nested lists indented consistently
- [ ] Ordered lists numbered sequentially
- [ ] Unordered lists use bullet points
- [ ] Complete sentences use periods; phrases don't
- [ ] Tables have clear header rows
- [ ] Code blocks include language identifiers
- [ ] Inline code uses backticks for technical terms only
- [ ] Bold used for emphasis and UI elements
- [ ] Proper whitespace around sections
- [ ] No lists with only one item
- [ ] No tables with fewer than 3 columns

## Heading and Structure Checklist

- [ ] One H1 per document
- [ ] No skipped heading levels
- [ ] Headings are descriptive and scannable
- [ ] No punctuation at end of headings
- [ ] Logical hierarchy throughout document
- [ ] Heading style consistent (Title Case)
- [ ] Major sections use H2
- [ ] Subsections use H3
- [ ] Related content grouped together

## Accessibility Considerations

### Alt Text for Images

```markdown
![Dashboard overview showing metrics and graphs](images/dashboard-overview.png)
```

### Color Independence

- Don't rely solely on color to convey information
- Use text labels and patterns in charts/tables

### Heading Structure

- Use proper heading hierarchy (helps screen readers)
- Don't skip levels
- Headings should outline document structure

### Link Text

- Use descriptive link text, not "click here"
- Good: "Read the [authentication guide]"
- Avoid: "Click [here] for more info"

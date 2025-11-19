# Vale Rules Reference Guide

## Overview

Vale is a command-line linter for prose. This guide documents our custom Vale rules that enforce the style guide standards across documentation. These rules align with the voice, tone, grammar, and formatting guidelines defined in other reference documents.

## What is Vale?

**Vale** is a free, language-agnostic prose linter that checks written content against style rules. It integrates with:
- CI/CD pipelines
- Code editors (VS Code, Vim, etc.)
- GitHub Actions
- Pre-commit hooks

**Benefits:**
- Catches style inconsistencies automatically
- Enforces organization standards across teams
- Reduces manual review time
- Provides consistent feedback

## Understanding Vale Rules

### Rule Structure

Each rule has:
- **Name:** Unique identifier for the rule
- **Description:** What the rule checks
- **Severity:** error, warning, or suggestion
- **Pattern:** Regex or token matching
- **Message:** Feedback when rule triggers

### Rule Severity Levels

**Error (blocks publishing):**
- Critical terminology mistakes
- Security-related issues
- Broken syntax

**Warning (should fix before review):**
- Grammar and active voice issues
- Inconsistent formatting
- Style guide violations

**Suggestion (nice to have):**
- Wordiness improvements
- Preference-based feedback
- Enhancement opportunities

## Core Style Guide Rules

### Rule: Style.ActiveVoice

**Category:** Grammar and Voice
**Severity:** warning
**Description:** Detects passive voice constructions; enforces active voice usage

**Pattern:** Matches "was [verb]", "were [verb]", "be [verb]", "been [verb]"

**Examples that trigger:**

```
The file was deleted by the user
→ The user deleted the file

Your password was reset
→ We reset your password

The configuration should be updated
→ Update the configuration
```

**Why this matters:** Active voice is clearer and more direct. Matches organizational voice standards.

**Message:** "Passive voice detected. Consider using active voice instead."

**Exceptions allowed:**
- Unknown actor: "Your account has been secured"
- Privacy: "Credentials are stored encrypted"
- Focus on receiver: "You've been granted admin access"

### Rule: Style.DontStart

**Category:** Writing Quality
**Severity:** suggestion
**Description:** Flags sentences starting with weak words that can be removed or restructured

**Patterns:** "There is", "There are", "There has been", "It is", "This is"

**Examples that trigger:**

```
There are three ways to configure authentication
→ Three ways to configure authentication exist
  (or better: "To configure authentication, you can use three approaches:")

It is important to test
→ Testing is important
  (or better: "Test your integration thoroughly")

There is a setting for this
→ A setting controls this
  (or better: "Configure this in Settings")
```

**Why this matters:** Direct sentences are more engaging and concise.

**Message:** "Consider removing '[word]'. Sentences are stronger without it."

### Rule: Style.TooWordy

**Category:** Clarity and Conciseness
**Severity:** suggestion
**Description:** Identifies verbose phrases with simpler alternatives

**Common patterns matched:**

| Wordy | Better |
|-------|--------|
| at the present time | now |
| at this point in time | currently |
| due to the fact that | because |
| in order to | to |
| prior to | before |
| subsequent to | after |
| a number of | several/many |
| whether or not | whether |
| in the event that | if |

**Examples:**

```
In order to access the API, you must provide credentials
→ To access the API, provide credentials

At the present time, webhooks are available
→ Webhooks are now available

Due to the fact that TCP is encrypted, data is secure
→ Because TCP is encrypted, data is secure
```

**Why this matters:** Concise language respects reader time and improves clarity.

**Message:** "Avoid '[phrase]'. Use '[suggestion]' instead."

### Rule: Grammar.ProperNouns

**Category:** Capitalization and Terminology
**Severity:** error
**Description:** Ensures product names and proper nouns are capitalized correctly

**Patterns:** Product names, company names, brand-specific terminology

**Examples that trigger:**

```
Connect to the api console
→ Connect to the API Console

Configure oauth 2.0 authentication
→ Configure OAuth 2.0 Authentication

The dashboard shows metrics
→ The Dashboard shows metrics
```

**Why this matters:** Consistent capitalization maintains brand identity and professionalism.

**Message:** "Capitalize '[term]' in documentation."

**Maintained list:**
- API Console
- Authentication Service
- Dashboard
- REST API
- OAuth 2.0
- Single Sign-On (SSO)
- [Your organization-specific terms]

### Rule: Grammar.SentenceLength

**Category:** Readability
**Severity:** suggestion
**Description:** Flags sentences exceeding 30 words (or configured threshold)

**Trigger condition:** Sentence has more than 30 words

**Example that triggers:**

```
In order to ensure that your account remains secure and that you can access
all features available to you, it is essential that you update your password
regularly, preferably every 90 days.
(43 words)

Better:
Update your password every 90 days to keep your account secure.
(13 words)
```

**Why this matters:** Long sentences are harder to parse and understand quickly.

**Message:** "Sentence length is 43 words. Consider breaking into shorter sentences."

**Threshold:** 30 words (can be adjusted for technical docs)

### Rule: Grammar.Contractions

**Category:** Voice and Tone
**Severity:** suggestion
**Description:** Flags forbidden contractions or encourages contractions for conversational tone

**Contractions to use (modern documentation):**
- can't, don't, won't, it's, we're, you'll, that's, here's

**Examples:**

```
Avoid: "Do not use this in production"
Better: "Don't use this in production"

Avoid: "The system will not process invalid data"
Better: "The system won't process invalid data"
```

**Why this matters:** Contractions make documentation feel more conversational and approachable.

**Message:** "Consider using '[contraction]' for a more conversational tone."

## Technical Writing Rules

### Rule: Tech.Acronyms

**Category:** Terminology
**Severity:** warning
**Description:** Detects acronyms without expansion on first use

**Pattern:** Matches known acronyms; checks if expanded before use

**Examples that trigger:**

```
Document starts: "Configure the API key in the settings"
→ Should be: "Configure the Application Programming Interface (API) key..."

Using unfamiliar acronym: "Enable SSO in your workspace"
→ Should be: "Enable Single Sign-On (SSO)..."
```

**Why this matters:** Acronym expansion aids accessibility and clarity for new readers.

**Message:** "Expand '[acronym]' on first use."

**Known acronyms requiring expansion:**
- API, SDK, JSON, XML, REST, SQL, JWT, OAuth, SSO
- [Add organization-specific acronyms]

### Rule: Tech.URLFormat

**Category:** Formatting and Consistency
**Severity:** error
**Description:** Ensures URLs are properly formatted in documentation

**Patterns:**
- Full URL: `https://example.com`
- Code block URLs with backticks: `` `https://example.com` ``
- Markdown links: `[text](url)`

**Examples that trigger:**

```
Visit example.com for more info
→ Visit https://example.com for more info

The endpoint is at api.example.com/v1/users
→ The endpoint is at https://api.example.com/v1/users

Don't: Using bare URL in body text
Do: [Link text](url) or `https://url`
```

**Why this matters:** Consistent URL formatting prevents broken links and improves clarity.

**Message:** "Format URLs with protocol (https://) and use markdown links: [text](url)"

### Rule: Tech.CaseSensitive

**Category:** Terminology
**Severity:** warning
**Description:** Ensures code terms maintain proper case (camelCase, snake_case, PascalCase)

**Patterns:** Matches common case errors for:
- camelCase variables: `userId`, `apiKey`
- snake_case variables: `user_id`, `api_key`
- PascalCase classes: `APIClient`, `UserManager`

**Examples that trigger:**

```
Store value in userid (should be: userId)
Call the GetUser function (should be: getUser)
Update Apikey variable (should be: apiKey)
```

**Why this matters:** Preserving case prevents syntax errors when copying code.

**Message:** "Preserve code case. Should be '[correct]', not '[incorrect]'"

### Rule: Tech.CodeBlockLanguage

**Category:** Formatting
**Severity:** warning
**Description:** Requires language identifier on code blocks

**Examples that trigger:**

```markdown
Missing language:
```
api.get('/users', options)
```

Should be:
```javascript
api.get('/users', options)
```
```

**Why this matters:** Language identifiers enable syntax highlighting for readability.

**Message:** "Specify language for code block (e.g., ``` javascript)"

**Supported languages:**
- javascript, python, bash, shell, java, sql, json, yaml, xml, go, rust, etc.

## Content Quality Rules

### Rule: Content.Bias

**Category:** Inclusive Language
**Severity:** warning
**Description:** Detects potentially biased or ableist language

**Patterns matched:**
- "dummy data" → "sample data"
- "simple/easy" (without context) → be specific about difficulty
- "obvious" → consider reader's perspective
- ableist terms: "blind copy", "deaf to errors"
- gendered pronouns → "they"

**Examples that trigger:**

```
Use dummy data for testing
→ Use sample data for testing

The solution is simple
→ The solution is straightforward (or: "takes 5 minutes to implement")

As anyone can see
→ Consider that: (acknowledges different perspectives)
```

**Why this matters:** Inclusive language welcomes diverse audiences and sets professional tone.

**Message:** "Avoid '[term]'. Use '[alternative]' instead."

### Rule: Content.Admonitions

**Category:** Formatting and Structure
**Severity:** suggestion
**Description:** Encourages use of structured callouts for important information

**Patterns:** Standalone sentences that should be callouts:
- "Note that..."
- "Important:"
- "Be sure to..."
- "Never do..."

**Examples that trigger:**

```
In the body text: "Be sure to test this before deploying"
→ Should be formatted as callout:
   > **Important:** Test this before deploying

"Never commit secrets to version control"
→ Should be:
   > **Warning:** Never commit secrets to version control
```

**Why this matters:** Callouts highlight critical information for scanning and visibility.

**Message:** "Use callout formatting for this advisory. Format as `> **Note:** [content]`"

### Rule: Content.HeadingCase

**Category:** Formatting
**Severity:** suggestion
**Description:** Ensures consistent heading capitalization (Title Case)

**Examples that trigger:**

```
## getting started (should be: Getting Started)
### configure your settings (should be: Configure Your Settings)
#### api endpoints (should be: API Endpoints)
```

**Why this matters:** Consistent heading capitalization maintains professional appearance.

**Message:** "Use Title Case for headings. Should be '[Proper Case]'"

## Vale Configuration Files

### .vale.ini (Project Configuration)

**Location:** Repository root

**Sample configuration:**

```ini
[core]
StylesPath = .github/styles
Vocab = Base

MinAlertLevel = warning
IgnoredScopes = code,pre

[formats]
markdown = md,mdx
asciidoc = adoc

[style.activeVoice]
level = warning

[style.tooWordy]
level = suggestion

[grammar.sentenceLength]
level = suggestion
threshold = 30
```

### Custom Rules Location

**Directory:** `.github/styles/Org/`

**Standard rule files:**
- Grammar.yml
- Style.yml
- Tech.yml
- Content.yml

## Running Vale

### Command Line

**Check single file:**
```bash
vale path/to/file.md
```

**Check entire directory:**
```bash
vale docs/
```

**Output formats:**
```bash
vale --output=line docs/  # Default format
vale --output=JSON docs/   # Machine-readable
vale --output=table docs/  # Pretty table
```

### Configuration Examples

**Strict mode (documentation QA):**
```bash
vale --minAlertLevel=error docs/
```

**Advisory mode (suggestions only):**
```bash
vale --minAlertLevel=suggestion docs/
```

**Ignore specific rules:**
```bash
vale --ignore=Org.ProperNouns docs/
```

### CI/CD Integration (GitHub Actions)

**Workflow example:**

```yaml
name: Lint Documentation

on: [push, pull_request]

jobs:
  vale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: errata-ai/vale-action@v1.3
        with:
          files: docs/
          fail-on-error: true
```

## Rule Customization

### Creating Custom Rules

**Basic rule structure:**

```yaml
---
extends: existence
message: "Use '[replacement]' instead of '[word]'"
level: warning
ignorecase: true
tokens:
  - "problematic_term"
```

**Pattern-based rule:**

```yaml
---
extends: repetition
message: "Repeated word: '[word]'"
level: warning
pattern: '\b(?P<word>\w+)\s+\1\b'
```

**Conditional rule:**

```yaml
---
extends: conditional
message: "Use active voice"
level: warning
ignorecase: true
swap:
  was (.+) by: '[1] was'
```

### When to Add New Rules

Add rules for:
1. Repeated style corrections across team
2. Common misunderstandings about guidelines
3. New standards or terminology
4. Accessibility requirements
5. Security-sensitive patterns

### Rule Testing

**Test rule on sample:**

```bash
vale --config=.vale.ini test-file.md
```

**Update configuration and retest:**
```bash
# Modify .vale.ini
vale --config=.vale.ini test-file.md
```

## Handling Vale Warnings

### False Positives and Exceptions

**Disable rule for block:**
```markdown
<!-- vale Org.ProperNouns = off -->
Use the old-system API for legacy integrations
<!-- vale Org.ProperNouns = on -->
```

**Disable for line:**
```markdown
Use the old-system API (legacy) <!-- vale Org.ProperNouns = off -->
```

**Disable for file:**
```markdown
---
title: Legacy Documentation
vale:disable: Org.ProperNouns, Style.Wordiness
---
```

### Addressing Common Issues

**Issue: Rule too strict**
- Adjust threshold in config (e.g., sentence length)
- Check if rule applies to all content types
- Consider making it "suggestion" instead of "warning"

**Issue: Rule catches unintended patterns**
- Review regex pattern
- Add exceptions list
- Make scope more specific

**Issue: False negatives (missing violations)**
- Check pattern accuracy
- Verify rule is enabled
- Test with verbose output: `vale --debug`

## Best Practices

### Implementation Timeline

**Phase 1 (Foundation):**
- Enable core grammar and voice rules
- Set all to "warning" level initially
- Allow time for team adjustment

**Phase 2 (Enforcement):**
- Graduate critical rules to "error"
- Add terminology rules
- Integrate into CI/CD

**Phase 3 (Enhancement):**
- Add custom organization rules
- Create domain-specific rules
- Regular reviews and updates

### Team Training

**Introduce Vale to team:**
1. Show what rules catch and why
2. Demonstrate how to fix issues
3. Provide examples from team documentation
4. Allow questions and feedback

**Ongoing support:**
- Include Vale output in code reviews
- Reference rules when giving feedback
- Update rules based on feedback
- Share updates in team documentation

## Troubleshooting Vale

### Common Problems

**Issue: Vale not finding files**
```bash
# Solution: Check path and glob patterns
vale --glob="*.md" docs/
```

**Issue: Rules not being applied**
```bash
# Check: Is StylesPath correct?
vale --config=.vale.ini test.md
```

**Issue: Performance is slow**
```bash
# Solution: Exclude large directories
# Add to .vale.ini:
[core]
Ignore = node_modules, .git, build
```

**Issue: False positives for abbreviations**
```bash
# Solution: Add to custom vocabulary
# Create .github/styles/Vocab/Base/accept.txt
API
SDK
JSON
```

## Checklist: Rule Implementation

- [ ] All team members have Vale installed
- [ ] .vale.ini configured in repository root
- [ ] Custom rules in .github/styles/ directory
- [ ] CI/CD workflow includes Vale linting
- [ ] Team training completed
- [ ] Documentation explains disabling rules
- [ ] Regular rule review scheduled (quarterly)
- [ ] Known false positives documented
- [ ] Performance acceptable (< 10 seconds per run)
- [ ] Pre-commit hook optional (not required)

## Resources

**Official Vale documentation:** https://vale.sh
**Vale GitHub Rules:** https://github.com/errata-ai/styles
**Configuration documentation:** https://vale.sh/docs/topics/config
**Rule development guide:** https://vale.sh/docs/topics/rules

## Custom Rules Inventory

**Rules specific to this organization:**

| Rule | Purpose | Severity |
|------|---------|----------|
| Org.ProductNames | Capitalize product names | error |
| Org.SecurityTerm | Flag security-related best practices | warning |
| Org.Audience | Check for audience-appropriate language | warning |
| Org.APIDocumentation | Specific API doc standards | warning |

(Add organization-specific rules here)

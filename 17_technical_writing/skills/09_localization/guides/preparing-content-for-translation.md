# Preparing Content for Translation: Comprehensive Checklist

## Overview

This guide provides a detailed checklist and step-by-step instructions for preparing content for translation. Proper preparation ensures faster, more accurate translations, reduces back-and-forth communication, and improves overall translation quality and consistency.

## Table of Contents

1. [Pre-Translation Audit](#pre-translation-audit)
2. [Content Cleanup and Standardization](#content-cleanup-and-standardization)
3. [Identifying Translatable Elements](#identifying-translatable-elements)
4. [Creating Context and Documentation](#creating-context-and-documentation)
5. [Technical Review](#technical-review)
6. [Creating Translation Assets](#creating-translation-assets)
7. [Establishing Glossaries](#establishing-glossaries)
8. [Handling Special Content Types](#handling-special-content-types)
9. [Markup and Formatting Standards](#markup-and-formatting-standards)
10. [Final Pre-Translation Checklist](#final-pre-translation-checklist)

## Pre-Translation Audit

### Step 1: Inventory All Content

Create a comprehensive content inventory:

**inventory.json:**

```json
{
  "documentation": {
    "gettingStarted": {
      "files": [
        "guides/installation.md",
        "guides/configuration.md",
        "guides/first-run.md"
      ],
      "wordCount": 4500,
      "complexity": "medium",
      "dependencies": ["api-reference"],
      "priority": "high"
    },
    "apiReference": {
      "files": [
        "reference/endpoints.md",
        "reference/authentication.md",
        "reference/error-codes.md"
      ],
      "wordCount": 8200,
      "complexity": "high",
      "dependencies": [],
      "priority": "high"
    },
    "tutorials": {
      "files": [
        "tutorials/basic-workflow.md",
        "tutorials/advanced-features.md",
        "tutorials/integration-guide.md"
      ],
      "wordCount": 6300,
      "complexity": "medium",
      "dependencies": ["api-reference", "getting-started"],
      "priority": "medium"
    },
    "faqs": {
      "files": ["faqs/common-issues.md"],
      "wordCount": 2100,
      "complexity": "low",
      "dependencies": ["getting-started"],
      "priority": "low"
    }
  },
  "summary": {
    "totalWords": 20100,
    "totalFiles": 10,
    "estimatedTranslationTime": "80-100 hours per language",
    "averageReadingLevel": "intermediate"
  }
}
```

### Step 2: Assess Content Quality

**Content Quality Checklist:**

- [ ] All sections have clear titles and headers
- [ ] Consistent capitalization throughout
- [ ] No duplicate content
- [ ] No outdated information
- [ ] Grammar and spelling correct
- [ ] Tone consistent across documents
- [ ] No mixed English/target language text
- [ ] No proprietary or confidential information
- [ ] All links functional
- [ ] Images and diagrams current

### Step 3: Analyze Content Dependencies

Create a dependency map:

```
Installation Guide
    └── Configuration Guide
        └── Basic Workflow Tutorial
            ├── API Reference
            │   └── Error Codes
            └── Advanced Features
                └── Integration Guide

FAQ → Getting Started Guide
```

**Use this map to:**
- Determine optimal translation order
- Identify content that should be translated together
- Plan resource allocation
- Estimate timeline

## Content Cleanup and Standardization

### Step 1: Remove Unnecessary Content

**Content Removal Checklist:**

- [ ] Delete placeholder text
- [ ] Remove TODO comments
- [ ] Delete internal notes or reminders
- [ ] Remove outdated version information
- [ ] Delete markup/code used only during development
- [ ] Remove test content
- [ ] Delete duplicate sections
- [ ] Remove commented-out code
- [ ] Delete sensitive information
- [ ] Remove author names or email addresses

**Example - Before:**

```markdown
# Installation Guide

TODO: Add Windows installation steps

## System Requirements

- CPU: 2+ GHz (TODO: verify minimum)
- RAM: 4GB minimum
- Disk: 2GB free space <!-- Need to update this -->

## Linux Installation

<!-- Alternative approach using package managers - decided against this -->
Regular installation method:
```

**Example - After:**

```markdown
# Installation Guide

## System Requirements

- CPU: 2+ GHz
- RAM: 4GB minimum
- Disk: 2GB free space

## Linux Installation

Standard installation method:
```

### Step 2: Standardize Formatting

**Formatting Standards Document:**

```markdown
# Formatting Standards for Translation

## Headings
- Use sentence case (not Title Case)
- Use consistent heading hierarchy
- Never skip heading levels (e.g., h1 -> h3)
- Include single space before heading

Example:
```markdown
# Main title

## First-level section

### Subsection
```

## Lists
- Use consistent bullet point style
- Don't mix ordered and unordered lists
- Use consistent indentation
- Add introductory text before lists
- Never use lists with single item

Example (Correct):
```markdown
The following options are available:

- Option A
- Option B
- Option C
```

Example (Incorrect):
```markdown
- Option A
```

## Code Blocks
- Use triple backticks with language specification
- Consistent indentation (2 or 4 spaces, not mixed)
- Never use tab indentation
- Include descriptive labels

Example:
```javascript
// Correct: Code block with language
const config = {
  timeout: 5000,
  retries: 3
};
```

## Emphasis
- Use *italic* for emphasis
- Use **bold** for important terms
- Use `code` for code references
- Don't use ALL CAPS for emphasis
- Don't mix styles within same sentence

## Tables
- Use consistent column alignment
- Include header row
- Ensure equal column spacing
- Add caption if needed
```

### Step 3: Standardize Language

Create a **LANGUAGE_STANDARDS.md**:

```markdown
# Language Standards for Technical Documentation

## Tense
- Use present tense: "The system processes requests"
- Avoid future tense: "will process"
- Avoid past tense: "processed"

## Voice
- Use active voice: "Click the button"
- Avoid passive voice: "The button should be clicked"

## Person
- Use second person: "You can configure..."
- Avoid first person: "I recommend..."
- Avoid third person: "The user should..."

## Contractions
- Avoid contractions in formal documentation
- Use: "do not" (not "don't")
- Use: "cannot" (not "can't")
- Use: "you are" (not "you're")

## Articles
- Use articles consistently
- Include: "the configuration file"
- Not: "configuration file" (unless plural/generic)

## Terminology
- Never use abbreviations without definition
- Define acronyms on first use: "API (Application Programming Interface)"
- Use term consistently throughout document

Example: Correct
```
The REST API (Representational State Transfer API) provides access to resources.
Use the API to query data...
The API documentation is available...
```

Example: Incorrect
```
The REST API provides access to resources.
Use the REST service to query data...
The service documentation is available...
```

## Numbers and Units
- Write out numbers one through nine: "five users"
- Use numerals for ten and above: "15 users"
- Include units: "5 GB", "100 ms"
- Use consistent decimal notation

## Punctuation
- Use Oxford comma in lists: "alpha, beta, and gamma"
- Use period after bullet points with complete sentences
- Use no period after fragments
- Use consistent spacing around punctuation
```

### Step 4: Consolidate Duplicate Content

**Duplication Check Process:**

```bash
#!/bin/bash

# Find similar content using fuzzy matching
# This script identifies duplicate or near-duplicate sections

find docs -name "*.md" -exec wc -w {} + | sort -rn | head -20

# Use diff to compare similar files
diff -u docs/guide1.md docs/guide2.md

# Generate duplication report
echo "Checking for duplicate content..."
# Implementation of duplication detection
```

**After identifying duplicates:**

1. Keep primary version in main location
2. Create reference/link to primary version
3. Remove duplicate content
4. Update internal links

Example of creating cross-references:

```markdown
# Installation on macOS

See [Installation on Linux](installation-linux.md) for similar instructions.

## Step 1: Download
## Step 2: Install
```

## Identifying Translatable Elements

### Step 1: Mark Translatable Content

**Translatable Content Categories:**

```
Category          | Examples                    | Action
------------------|-----------------------------|-----------
Headings          | Section titles              | Translate
Body text         | Paragraphs, descriptions    | Translate
Lists             | Bullet points, items        | Translate
Tables            | Cell content (not structure)| Translate
Captions          | Image/diagram descriptions  | Translate
Button labels     | "Submit", "Cancel"          | Translate
Navigation text   | Menu items, breadcrumbs     | Translate
Error messages    | User-facing errors          | Translate
Hints/Tips        | Helper text                 | Translate
---
Code comments     | Only language-specific      | Conditional
Code samples      | Do not translate            | Don't translate
URLs              | Do not translate            | Don't translate
API endpoints     | Do not translate            | Don't translate
Technical terms   | Context-dependent          | Glossary check
Variable names    | Do not translate            | Don't translate
File paths        | Do not translate            | Don't translate
Database names    | Do not translate            | Don't translate
```

### Step 2: Create Content Extraction Map

**extraction-map.json:**

```json
{
  "documentTypes": [
    {
      "type": "markdown",
      "extension": ".md",
      "extractableElements": [
        {
          "xpath": "h1, h2, h3, h4, h5, h6",
          "type": "heading",
          "translate": true
        },
        {
          "xpath": "p",
          "type": "paragraph",
          "translate": true
        },
        {
          "xpath": "li",
          "type": "list_item",
          "translate": true
        },
        {
          "xpath": "table > tr > td",
          "type": "table_cell",
          "translate": true
        },
        {
          "xpath": "code, pre",
          "type": "code",
          "translate": false
        },
        {
          "xpath": "a[href]",
          "type": "link",
          "translate": "text_only"
        }
      ]
    },
    {
      "type": "html",
      "extension": ".html",
      "extractableElements": [
        {
          "xpath": "//*[@data-translate='true']",
          "type": "tagged",
          "translate": true
        },
        {
          "xpath": "//button, //input[@type='button']",
          "type": "button",
          "translate": true,
          "attribute": "value"
        }
      ]
    }
  ]
}
```

### Step 3: Apply Translation Markers

**Markdown with translation markers:**

```markdown
# {start-translate} User Authentication {end-translate}

{start-translate}
This section describes how to authenticate users in your application.
{end-translate}

## Configuration

{start-translate}
To configure authentication, follow these steps:
{end-translate}

1. {start-translate} Create an authentication provider {end-translate}
2. {start-translate} Configure credentials {end-translate}
3. {start-translate} Enable authentication in settings {end-translate}

{start-notranslate}
```bash
# Code sample - do not translate
const auth = new AuthProvider({
  clientId: 'YOUR_CLIENT_ID',
  secret: 'YOUR_SECRET'
});
```
{end-notranslate}

## API Reference

{start-translate} The following endpoints are available: {end-translate}

| Endpoint | {start-translate} Description {end-translate} |
|----------|-------------------------------------------|
| `/auth/login` | {start-translate} User login endpoint {end-translate} |
| `/auth/logout` | {start-translate} User logout endpoint {end-translate} |
```

## Creating Context and Documentation

### Step 1: Create Context Documentation

**Context provides translators with necessary background:**

**context/authentication-guide-context.md:**

```markdown
# Context for "User Authentication" Guide

## Purpose
This guide helps developers implement user authentication in their applications.
It's a core feature that impacts security and user experience.

## Target Audience
- Junior to mid-level developers
- Those new to the product
- Developers implementing authentication for the first time

## Key Concepts
- **Authentication**: Process of verifying user identity
- **Authorization**: Process of granting permissions
- **Session**: Period during which user is logged in
- **Token**: Credential that proves authentication

## Product Context
- Authentication is central to product security
- Users expect simple but secure authentication
- Multiple authentication methods supported (OAuth, JWT, SAML)
- Performance critical - authentication happens on every request

## Translation Considerations
- Keep technical terminology consistent with glossary
- "Login" and "authentication" are different concepts - don't confuse
- Consider how authentication flows in target language culture
- Error messages must be clear and actionable

## Related Documentation
- [OAuth Integration Guide](../oauth-integration.md)
- [API Reference - Auth Endpoints](../api/auth.md)
- [Security Best Practices](../security.md)

## Screenshots/Diagrams
- [auth-flow.png](../images/auth-flow.png) - Shows authentication flow
- [login-screen.png](../images/login-screen.png) - Example login screen

## Glossary References
- authentication (Authentifizierung, Authentification, 認証)
- session (Sitzung, Session, セッション)
- token (Token, Jeton, トークン)
- credentials (Anmeldedaten, Identifiants, 認証情報)

## Revision History
- v1.0: Initial version
- v2.0: Added OAuth examples
- v2.1: Added SAML support
```

### Step 2: Create Translation Notes

**translation-notes.md:**

```markdown
# Translation Notes for All Guides

## General Notes
- This is technical documentation for developers
- Maintain technical precision while keeping language clear
- Adapt examples to local context where appropriate
- Preserve code structure and syntax exactly

## Document-Specific Notes

### Getting Started Guide
- Keep encouraging but professional tone
- Use "you" to address reader directly
- Example code should be clear to beginners
- Anticipate common questions

### API Reference
- Technical terminology must be exact
- Parameter descriptions need to be complete
- Error descriptions should be actionable
- Maintain consistency with API documentation

### Troubleshooting Guide
- Problem descriptions must be easy to understand
- Solutions should be step-by-step
- Keep a helpful, not frustrated tone
- Reference other sections for deeper information

## Style Guide References
- [Terminology Glossary](glossary.md)
- [Formatting Standards](formatting-standards.md)
- [Language Standards](language-standards.md)

## Contact for Questions
- Subject matter expert: product-team@company.com
- Localization lead: localization@company.com
- Response time: Within 24 hours
```

### Step 3: Create Terminology Reference

**glossary-with-context.md:**

```markdown
# Comprehensive Glossary with Context

## Core Terms

### API (Application Programming Interface)
- **Definition**: Set of rules and tools for building software
- **Usage**: "Use the API to query data"
- **Context**: Technical, never translate
- **Related terms**: Endpoint, Request, Response, Parameter
- **Translation**: API (all languages - preserve)

### Authentication
- **Definition**: Process of verifying user identity
- **Usage**: "Complete authentication to access features"
- **Context**: Security process
- **Related terms**: Credentials, Password, Session, Token
- **German**: Authentifizierung
- **French**: Authentification
- **Japanese**: 認証 (ninshō)
- **Avoid**: "Login" (different concept)

### Configuration
- **Definition**: Process of setting up system parameters
- **Usage**: "Configure the authentication settings"
- **Context**: System administration
- **Related terms**: Settings, Options, Properties, Parameters
- **German**: Konfiguration
- **French**: Configuration
- **Japanese**: 設定 (setchoku)
- **Note**: Not the same as "customization"

### Endpoint
- **Definition**: URL address for API access
- **Usage**: "Send requests to the /api/users endpoint"
- **Context**: Technical, API-specific
- **Related terms**: URL, Route, Path, URI
- **German**: Endpunkt
- **French**: Point de terminaison
- **Japanese**: エンドポイント (endopointo)
- **Never translate**: The actual endpoint path

### Session
- **Definition**: Period during which user is logged in
- **Usage**: "A session expires after 30 minutes"
- **Context**: User management
- **Related terms**: Login, Logout, Token, Authentication
- **German**: Sitzung
- **French**: Session
- **Japanese**: セッション (sesshon)

### Token
- **Definition**: Digital credential proving authentication
- **Usage**: "Include your token in the request header"
- **Context**: Security/API
- **Related terms**: Credential, Key, Certificate, Authentication
- **German**: Token
- **French**: Jeton
- **Japanese**: トークン (token)
- **Note**: In some contexts, "authentication token" might be "Authentifizierungstoken"

## Product-Specific Terms

### Dashboard
- **Definition**: Main user interface for monitoring/control
- **German**: Instrumententafel / Dashboard
- **French**: Tableau de bord / Tableau des statistiques
- **Japanese**: ダッシュボード (dasshubōdo)

### Repository
- **Definition**: Central location where data/code is stored
- **German**: Repository / Speicher
- **French**: Référentiel / Dépôt
- **Japanese**: リポジトリ (ripojiitori)

### Query
- **Definition**: Request for data from database
- **German**: Abfrage
- **French**: Requête
- **Japanese**: クエリ (kuer)

## Context-Dependent Terms

### Run
- **Meaning 1**: Execute a program
  - German: "ausführen"
  - French: "exécuter"
  - Japanese: "実行する" (jikkou suru)

- **Meaning 2**: Period of operation
  - German: "Durchlauf" / "Ausführung"
  - French: "exécution"
  - Japanese: "実行" (jikkou)

### Deploy
- **Definition**: Release software to production
- **German**: bereitstellen / implementieren
- **French**: déployer
- **Japanese**: デプロイする (depu roisu)
```

## Technical Review

### Step 1: Code Sample Audit

**Code Review Checklist:**

```markdown
# Code Sample Review Checklist

For each code sample in documentation:

- [ ] Code is syntactically correct
- [ ] Code runs without errors
- [ ] Code demonstrates intended concept
- [ ] Code is current with latest API version
- [ ] Variable/function names are clear
- [ ] Comments are in English (not to be translated)
- [ ] Code formatting is consistent
- [ ] Output examples are accurate
- [ ] Error handling is shown where relevant
- [ ] Security best practices demonstrated
- [ ] Performance considerations noted
- [ ] Platform-specific code marked

Example format:
```javascript
// ✓ Good: Clear, current, documented
const config = {
  timeout: 5000,      // milliseconds
  retries: 3,         // attempts
  endpoint: 'https://api.example.com'
};
```

```javascript
// ✗ Bad: Unclear, outdated, undocumented
var c = {
  t: 5000,
  r: 3,
  e: 'https://api.example.com'
};
```
```

### Step 2: Link Validation

**Link Checking Script:**

```bash
#!/bin/bash

echo "Validating all links in documentation..."

# Check internal links
for file in docs/**/*.md; do
  echo "Checking $file..."

  # Extract links
  grep -oE '\[.*\]\((.*\.md.*)\)' "$file" | cut -d'(' -f2 | cut -d')' -f1 | while read link; do
    if [[ "$link" == /* ]]; then
      # Absolute path
      if [[ ! -f "docs${link%#*}" ]]; then
        echo "ERROR: Broken link in $file: $link"
      fi
    else
      # Relative path
      dir=$(dirname "$file")
      resolved_path="$dir/$link"
      if [[ ! -f "${resolved_path%#*}" ]]; then
        echo "ERROR: Broken link in $file: $link"
      fi
    fi
  done
done

# Check external URLs (sample)
grep -h 'http[s]*://' docs/**/*.md | while read url; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  if [[ "$status" != "200" && "$status" != "301" && "$status" != "302" ]]; then
    echo "WARNING: Unreachable URL: $url (Status: $status)"
  fi
done

echo "Link validation complete"
```

### Step 3: Image and Diagram Review

**Image Asset Checklist:**

```markdown
# Image and Diagram Review

For each image in documentation:

- [ ] Image file exists and is referenced correctly
- [ ] Image has descriptive alt-text
- [ ] Image has descriptive caption
- [ ] Image quality is sufficient (not blurry)
- [ ] Image is properly sized (not stretched)
- [ ] Image file format appropriate (PNG for screenshots, SVG for diagrams)
- [ ] Image file size optimized
- [ ] Image contains no sensitive information
- [ ] Diagram uses simple, clear labels
- [ ] Diagram text can be understood in all languages

Example (Markdown):
```markdown
![System Architecture Diagram](../images/architecture.png)
*Figure 1: System architecture showing authentication flow*
```

Example (HTML):
```html
<figure>
  <img src="architecture.png" alt="System architecture diagram">
  <figcaption>Figure 1: System architecture showing authentication flow</figcaption>
</figure>
```
```

## Creating Translation Assets

### Step 1: Prepare Translation Kit

Create a comprehensive package for translators:

**translation-kit/README.md:**

```markdown
# Translation Kit

This kit contains everything needed to translate the documentation.

## Contents

### Documentation
- `source/` - All Markdown files to translate
- `extracted-strings.json` - All translatable strings

### Reference Materials
- `GLOSSARY.md` - Terms and translations
- `STYLE_GUIDE.md` - Writing standards
- `CONTEXT.md` - Background information
- `TRANSLATOR_NOTES.md` - Document-specific notes

### Examples
- `examples/translated-section.md` - Example translation
- `examples/common-mistakes.md` - Mistakes to avoid

### Tools
- `scripts/validate-translation.js` - Validation tool
- `scripts/build-translated-docs.js` - Build script

## Quick Start

1. Read GLOSSARY.md
2. Read STYLE_GUIDE.md
3. Review CONTEXT.md
4. Look at examples/translated-section.md
5. Set up translation tool
6. Begin translation
7. Run validation regularly
8. Submit for review

## Structure

All strings are extracted into `extracted-strings.json`:

```json
{
  "guides.gettingStarted.intro": {
    "source": "Getting started is easy",
    "context": "introduction paragraph",
    "location": "docs/guides/getting-started.md"
  }
}
```

Translate by creating translated version:

```json
{
  "guides.gettingStarted.intro": {
    "source": "Getting started is easy",
    "translation": "Am Anfang ist es ganz einfach",
    "translator": "translator@company.com",
    "date": "2024-01-15"
  }
}
```

## Support

- Questions: localization@company.com
- Response time: 24 hours
- Glossary updates: Twice weekly
- Context updates: As needed
```

### Step 2: Create String Extraction File

**extracted-strings.json (Template):**

```json
{
  "metadata": {
    "project": "Documentation",
    "version": "1.0",
    "extractedDate": "2024-01-15",
    "totalStrings": 1250,
    "sourceLanguage": "en"
  },
  "strings": {
    "gettingStarted.title": {
      "id": "getting-started-title",
      "context": "Main title for getting started guide",
      "source": "Getting Started",
      "sourceFile": "docs/guides/getting-started.md",
      "lineNumber": 1,
      "maxLength": 50,
      "type": "heading",
      "notes": "Keep concise, this is used in navigation"
    },
    "gettingStarted.intro.para1": {
      "id": "getting-started-intro-1",
      "context": "Introductory paragraph",
      "source": "This guide will show you how to set up and use the product effectively.",
      "sourceFile": "docs/guides/getting-started.md",
      "lineNumber": 3,
      "type": "paragraph",
      "notes": "Friendly but professional tone"
    },
    "gettingStarted.steps.step1": {
      "id": "getting-started-step1",
      "context": "First step in setup process",
      "source": "Download the latest version",
      "sourceFile": "docs/guides/getting-started.md",
      "lineNumber": 15,
      "type": "list_item",
      "notes": "Part of ordered list - don't add numbers"
    },
    "apiRef.endpoints.getUserTitle": {
      "id": "api-ref-get-user",
      "context": "API endpoint description",
      "source": "Retrieve user information",
      "sourceFile": "docs/reference/api.md",
      "lineNumber": 45,
      "type": "description",
      "maxLength": 100,
      "notes": "Technical description - maintain precision"
    }
  }
}
```

### Step 3: Prepare Format-Specific Assets

**For Markdown (Standard):**

```markdown
# String Format for Markdown

Source strings in Markdown use key-based translation:

```markdown
{i18n.key "Default text"}
```

Or with context:

```markdown
{i18n.key "Default text" context="This is about configuration"}
```
```

**For YAML Front Matter:**

```yaml
---
title: "Getting Started"
i18n_title: "gettingStarted.title"
description: "Learn how to get started"
i18n_description: "gettingStarted.description"
---

# {i18n gettingStarted.title}

{i18n gettingStarted.intro}
```

**For JSON (API Reference):**

```json
{
  "endpoints": [
    {
      "method": "GET",
      "path": "/api/users",
      "name": "getUsers",
      "description": "getUsers.description",
      "parameters": [
        {
          "name": "page",
          "description": "getUsers.parameters.page"
        }
      ]
    }
  ]
}
```

## Establishing Glossaries

### Step 1: Create Master Glossary

**glossary-master.json:**

```json
{
  "metadata": {
    "version": "2.0",
    "lastUpdated": "2024-01-15",
    "maintainer": "terminology@company.com",
    "reviewCycle": "monthly"
  },
  "categories": {
    "technical": {
      "database": {
        "en": "database",
        "de": "Datenbank",
        "fr": "base de données",
        "ja": "データベース",
        "context": "Data storage system",
        "priority": "critical",
        "related": ["table", "query", "index"]
      },
      "query": {
        "en": "query",
        "de": "Abfrage",
        "fr": "requête",
        "ja": "クエリ",
        "context": "Database or API request",
        "priority": "critical",
        "related": ["database", "filter", "parameter"]
      }
    },
    "product": {
      "dashboard": {
        "en": "dashboard",
        "de": "Dashboard",
        "fr": "tableau de bord",
        "ja": "ダッシュボード",
        "context": "Main user interface",
        "priority": "high",
        "related": ["widget", "report", "metric"]
      }
    },
    "ui": {
      "button": {
        "en": "button",
        "de": "Schaltfläche",
        "fr": "bouton",
        "ja": "ボタン",
        "context": "Interactive UI element",
        "priority": "medium",
        "examples": ["Submit button", "Cancel button"]
      }
    }
  }
}
```

### Step 2: Create Language-Specific Glossaries

**glossary-de.json:**

```json
{
  "language": "German",
  "code": "de",
  "entries": {
    "authentication": {
      "preferred": "Authentifizierung",
      "alternatives": ["Authentizierung (less common)"],
      "context": "Verification of user identity",
      "examples": [
        "Die Authentifizierung ist erforderlich",
        "Authentifizierungsmethoden konfigurieren"
      ],
      "notes": "Capital A when used at sentence start. Use 'Authentifizierung' not 'Authentizierung'"
    },
    "database": {
      "preferred": "Datenbank",
      "alternatives": ["DB (not recommended)"],
      "context": "Data storage and management",
      "examples": [
        "Die Datenbank speichert alle Benutzer",
        "Datenbankverbindung"
      ]
    }
  }
}
```

### Step 3: Set Up Glossary Management

**scripts/manage-glossary.js:**

```javascript
class GlossaryManager {
  constructor(glossaryPath) {
    this.glossary = this.loadGlossary(glossaryPath);
  }

  validateTerminology(text, language) {
    const issues = [];
    const glossaryTerms = Object.keys(this.glossary[language].entries);

    glossaryTerms.forEach(term => {
      const entry = this.glossary[language].entries[term];
      const alternatives = entry.alternatives || [];

      // Check for unapproved alternatives
      alternatives.forEach(alt => {
        if (text.includes(alt)) {
          issues.push({
            type: 'terminology',
            found: alt,
            recommended: entry.preferred,
            severity: 'warning'
          });
        }
      });
    });

    return issues;
  }

  suggestTerminology(text) {
    // Suggest glossary terms based on content
    // Implementation
  }

  loadGlossary(path) {
    // Load glossary from file
    // Implementation
  }
}
```

## Handling Special Content Types

### Step 1: Prepare Code and Commands

**Code Handling Guide:**

```markdown
# Code and Command Handling

## General Rules

- Never translate code identifiers
- Never translate language keywords
- Preserve exact formatting and indentation
- Only translate comments if language-appropriate

## Examples

### Python Example
```python
# English comment
def get_user_data(user_id):
    """Retrieve user information from database"""
    query = "SELECT * FROM users WHERE id = ?"
    return database.execute(query, user_id)
```

Translation: Comments translate if in target language

```python
# Kommentar auf Deutsch
def get_user_data(user_id):
    """Retrieve user information from database"""
    query = "SELECT * FROM users WHERE id = ?"
    return database.execute(query, user_id)
```

### Command Examples
```bash
# Good: Keep commands unchanged
npm install express
npm run build
npm test
```

```bash
# Bad: Never translate commands
npm installieren express  # ✗ Wrong
npm ausführen build      # ✗ Wrong
```

### Shell Output
```bash
# Keep literal output unchanged
$ npm list
your-project@1.0.0
├── express@4.18.0
└── react@18.0.0

# Translate explanatory text only
Verify your package list matches above
```
```

### Step 2: Handle Tables

**Table Translation Guide:**

```markdown
# Table Handling

## Table Structure
- Never modify table structure
- Never add or remove columns
- Keep alignment consistent
- Keep column widths proportional

## Content Translation

### Before Translation
```
| Parameter | Type | Description |
|-----------|------|-------------|
| userId | string | Unique user identifier |
| email | string | User email address |
| created | date | Account creation date |
```

### After Translation (German)
```
| Parameter | Type | Beschreibung |
|-----------|------|-------------|
| userId | string | Eindeutige Benutzerkennung |
| email | string | E-Mail-Adresse des Benutzers |
| created | date | Kontoerstellungsdatum |
```

## Important Rules
- Don't translate the "Parameter" or "Type" columns
- Preserve all code elements (userId, email, etc.)
- Maintain alignment with source
- Don't change data types
- Don't modify code examples
```

### Step 3: Prepare Visual Assets

**Visual Asset Handling:**

```markdown
# Visual Assets: Images and Diagrams

## Screenshots
- Don't embed text in screenshots if possible
- Provide text descriptions separately
- Create culture-specific screenshots if UI text differs
- Update screenshots when UI changes

## Diagrams
- For diagrams with text, create localized versions
- Use layered design tools (SVG, Figma) for easy translation
- Maintain consistent colors and styling
- Keep diagram proportions in all versions

## Example Process

1. Create diagram in source language
2. Export as SVG or layered file
3. Create copy for each target language
4. Translate text elements only
5. Maintain visual consistency
6. Version control all versions
```

## Markup and Formatting Standards

### Step 1: Define Markup Standards

**MARKUP_STANDARDS.md:**

```markdown
# Markup and Formatting Standards

## Markdown Standard

### Headers
```markdown
# H1: Main Title
## H2: Major Section
### H3: Subsection
#### H4: Detail Level
```

### Emphasis
```markdown
*italic text* for emphasis
**bold text** for important terms
`code` for inline code references
***bold italic*** rarely used
```

### Lists
```markdown
- Unordered list item
- Another item
  - Nested item
  - Another nested

1. Ordered item
2. Second item
   a. Sub-item
   b. Another sub-item
```

### Code Blocks
````markdown
```language
code here
```
````

### Links
```markdown
[Link text](url) for inline links
[Link text](url "tooltip") with tooltip
```

### Tables
```markdown
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
```

### Blockquotes
```markdown
> Quote text
> More quote text
>
> Still part of quote
```

### Horizontal Rule
```markdown
---
```

## HTML Standards

### Tags to Use
- `<h1>` through `<h6>` for headers
- `<p>` for paragraphs
- `<ul>` and `<li>` for unordered lists
- `<ol>` and `<li>` for ordered lists
- `<strong>` for emphasis
- `<em>` for emphasis
- `<code>` for code
- `<pre>` for code blocks
- `<table>` for tables
- `<a>` for links

### Don't Use
- Multiple `<br>` for spacing
- `<b>` or `<i>` (use `<strong>`/`<em>`)
- Inline styles
- Deprecated tags

## Special Characters

### Preserve These
- Curly braces: {}
- Square brackets: []
- Parentheses: ()
- Angle brackets: <>
- Backticks: `

### Replace These
- Straight quotes: " " with curly quotes: " "
- Apostrophes: ' with curly: '
- Hyphens: - with em-dash: —
- Three dots: ... with ellipsis: …

### Don't Modify
- XML entities: &nbsp;, &lt;, &gt;, &amp;
- HTML entities: &#123;, &#8364;
- Unicode characters
```

### Step 2: Create Validation Rules

**validation-rules.json:**

```json
{
  "rules": [
    {
      "name": "no_trailing_whitespace",
      "pattern": "\\s+$",
      "severity": "error",
      "message": "Remove trailing whitespace"
    },
    {
      "name": "consistent_spacing",
      "pattern": "  {2,}",
      "severity": "warning",
      "message": "Use single spaces between words"
    },
    {
      "name": "matching_quotes",
      "pattern": "['\"](?:[^'\"]|\\.)*(?:['\"]|$)",
      "severity": "error",
      "message": "Matching quotes required"
    },
    {
      "name": "placeholder_preservation",
      "pattern": "\\{[^}]+\\}",
      "severity": "error",
      "message": "Don't modify placeholders"
    },
    {
      "name": "code_block_formatting",
      "pattern": "```[a-z]*\\n[\\s\\S]*?\\n```",
      "severity": "error",
      "message": "Preserve code block formatting"
    }
  ]
}
```

## Final Pre-Translation Checklist

### Comprehensive Pre-Translation Checklist

Create and complete **PRE_TRANSLATION_CHECKLIST.md**:

```markdown
# Final Pre-Translation Checklist

## Content Preparation (Complete BEFORE extraction)

### Structure and Organization
- [ ] All content has descriptive titles
- [ ] Consistent heading hierarchy
- [ ] No duplicate sections
- [ ] Logical flow and organization
- [ ] Related content grouped together
- [ ] No orphaned or unused content

### Writing Quality
- [ ] No grammar or spelling errors
- [ ] Consistent tone throughout
- [ ] Consistent terminology
- [ ] No placeholder or TODO text
- [ ] Active voice preferred
- [ ] Present tense used consistently
- [ ] No mixed English/other language
- [ ] Contractions removed (don't → do not)

### Technical Accuracy
- [ ] All code samples tested and working
- [ ] API examples current and valid
- [ ] Command examples accurate
- [ ] File paths correct
- [ ] Version numbers current
- [ ] No outdated information
- [ ] Security best practices shown

### Formatting and Markup
- [ ] Consistent Markdown formatting
- [ ] All lists properly formatted
- [ ] Tables properly structured
- [ ] Code blocks properly marked
- [ ] Links functional (all paths correct)
- [ ] No broken internal references
- [ ] Consistent punctuation
- [ ] No trailing whitespace

### Content Assets
- [ ] All images present and referenced correctly
- [ ] Image alt-text descriptive
- [ ] Image captions accurate
- [ ] Image file sizes optimized
- [ ] No sensitive information in images
- [ ] Diagram labels clear
- [ ] Screenshots current

### Context and Resources
- [ ] Glossary complete and reviewed
- [ ] Translation guidelines created
- [ ] Context documentation prepared
- [ ] Examples provided
- [ ] Translator contact information available
- [ ] Support process documented

### Extraction and Organization
- [ ] String extraction keys defined
- [ ] Translation markers added
- [ ] Extraction tested successfully
- [ ] All strings accounted for
- [ ] No duplicate strings
- [ ] Metadata complete
- [ ] Dependencies documented

## Pre-Release Review (Complete BEFORE translator access)

- [ ] Content owner approval
- [ ] Technical review completed
- [ ] QA verification passed
- [ ] All checklists signed off
- [ ] Documentation complete
- [ ] Glossaries finalized
- [ ] Tools configured and tested
- [ ] Team trained on process
- [ ] Contingency plans in place

## Sign-Off

- [ ] Content prepared by: _________________ Date: ________
- [ ] Reviewed by: _________________ Date: ________
- [ ] Approved for translation by: _________________ Date: ________

## Notes

[Space for additional notes or special instructions]
```

### Sign-Off Process

Document completion with:

```markdown
# Pre-Translation Sign-Off

## Project: Documentation Localization

### Preparation Phase
- Start Date: 2024-01-01
- Completion Date: 2024-01-15
- Duration: 15 days

### Checklist Status
- Total Items: 47
- Completed: 47
- Issues Found: 2
- Issues Resolved: 2
- Overall Status: APPROVED

### Issues Resolved
1. ✓ Updated API endpoint version (v1 → v2)
2. ✓ Fixed broken link to security guide

### Sign-Offs
- Content Owner: John Smith (jan 15, 2024)
- Technical Lead: Jane Doe (Jan 15, 2024)
- Project Manager: Bob Johnson (Jan 15, 2024)

### Next Steps
1. Distribute translation kit to translators
2. Schedule translator kickoff meeting
3. Begin translation tracking
4. Set up review workflow
5. Configure QA automation

### Contact for Questions
- John Smith (Content): john@company.com
- Localization Lead: localization@company.com
```

## Conclusion

Proper preparation is crucial for successful translation:

- Well-organized content reduces translation time
- Clear context improves accuracy
- Consistent terminology ensures quality
- Complete documentation prevents delays
- Proper tooling enables efficiency

Invest time in preparation to save time and money in translation and review phases.

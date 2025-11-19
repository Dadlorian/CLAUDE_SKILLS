# Setting Up a Translation Workflow

## Overview

This guide provides comprehensive step-by-step instructions for establishing and managing a professional translation workflow. A well-designed workflow ensures consistent, high-quality translations while facilitating collaboration between technical writers, translators, and project managers.

## Table of Contents

1. [Workflow Architecture](#workflow-architecture)
2. [Defining Roles and Responsibilities](#defining-roles-and-responsibilities)
3. [Selecting Translation Management Tools](#selecting-translation-management-tools)
4. [Setting Up Extraction Process](#setting-up-extraction-process)
5. [Creating Translator Guidelines](#creating-translator-guidelines)
6. [Implementing Review Workflow](#implementing-review-workflow)
7. [Integration with Version Control](#integration-with-version-control)
8. [Automating Workflow Steps](#automating-workflow-steps)
9. [Monitoring and Metrics](#monitoring-and-metrics)
10. [Troubleshooting Workflow Issues](#troubleshooting-workflow-issues)

## Workflow Architecture

### End-to-End Workflow Overview

```
Content Updates
      ↓
Source Preparation
      ↓
String Extraction
      ↓
Translation Assignment
      ↓
Translation Work
      ↓
Translator Review
      ↓
Quality Assurance
      ↓
Project Manager Review
      ↓
Integration
      ↓
Build & Deploy
      ↓
Documentation Release
```

### Key Workflow Stages

**Stage 1: Preparation** - Source content is reviewed and prepared for translation

**Stage 2: Extraction** - Translatable strings are extracted from source documents

**Stage 3: Assignment** - Strings are assigned to translators based on expertise and language

**Stage 4: Translation** - Translators work on translations with provided guidelines and glossaries

**Stage 5: Self-Review** - Translators review their own work for accuracy and consistency

**Stage 6: QA Check** - Automated tools verify formatting, placeholders, and completeness

**Stage 7: Editorial Review** - Project manager or senior translator reviews translations

**Stage 8: Integration** - Approved translations are integrated into the project

**Stage 9: Build** - Build system compiles localized documentation

**Stage 10: Release** - Documentation is deployed to production

## Defining Roles and Responsibilities

### Step 1: Establish Role Structure

Create a **ROLES.md** file to document all participants:

```markdown
# Translation Workflow Roles

## Content Owner
- Responsibilities:
  - Ensures source content is translation-ready
  - Prepares content for extraction
  - Provides context and glossary terms
  - Validates translations against original intent
  - Approves final translations
- Qualifications:
  - Deep knowledge of product/documentation
  - Subject matter expertise
  - Understanding of target audiences

## Extraction Manager
- Responsibilities:
  - Manages string extraction process
  - Maintains extraction tools and scripts
  - Handles string key organization
  - Tracks extracted content versions
  - Manages extraction metadata
- Qualifications:
  - Technical knowledge of i18n systems
  - Understanding of documentation structure
  - Scripting/automation skills

## Translation Manager
- Responsibilities:
  - Assigns translation tasks to translators
  - Maintains translation schedules
  - Handles translator communications
  - Tracks translation progress
  - Manages translation budgets
- Qualifications:
  - Project management experience
  - Understanding of translation processes
  - Communication skills in multiple languages

## Professional Translator
- Responsibilities:
  - Translates assigned strings/documents
  - Maintains glossary consistency
  - Performs self-review
  - Documents translation decisions
  - Communicates ambiguities to content owner
- Qualifications:
  - Native fluency in target language
  - Technical translation experience
  - Understanding of product domain
  - Minimum 3 years professional experience

## QA Specialist
- Responsibilities:
  - Runs automated QA checks
  - Verifies formatting and placeholders
  - Checks for terminology consistency
  - Tests rendered translations
  - Generates QA reports
- Qualifications:
  - Understanding of QA processes
  - Technical knowledge of formats
  - Attention to detail
  - Experience with testing tools

## Project Manager
- Responsibilities:
  - Oversees entire workflow
  - Manages timeline and deadlines
  - Coordinates between teams
  - Handles escalations
  - Makes approval decisions
- Qualifications:
  - Project management experience
  - Understanding of localization
  - Leadership and communication skills
```

### Step 2: Create RACI Matrix

Develop a RACI (Responsible, Accountable, Consulted, Informed) matrix:

```
Activity                      | Content | Translation | QA    | Manager | Translator
                             | Owner   | Manager     | Spec. | (PM)    |
------------------------------|---------|-------------|-------|---------|----------
Prepare source content        | R/A     | -           | -     | C       | -
Extract strings               | C       | R/A         | -     | C       | I
Create glossaries             | R/A     | C           | -     | I       | I
Assign translation tasks      | -       | R/A         | -     | C       | I
Perform translation           | C       | -           | -     | I       | R/A
Self-review translation       | -       | -           | -     | -       | R/A
Run QA checks                 | -       | I           | R/A   | C       | -
Review translations           | R/A     | C           | C     | A       | I
Approve translations          | -       | -           | -     | R/A     | -
Integrate translations        | -       | R/A         | C     | C       | I
Build localized docs          | I       | -           | -     | R/A     | -
Deploy to production          | I       | I           | -     | R/A     | -
```

### Step 3: Define Communication Channels

```
Role                          | Daily Updates | Weekly Sync | Issues     | Final Approval
------------------------------|---------------|------------|------------|---------------
Content Owner                 | Email         | Video call | Slack      | Email
Translation Manager           | Slack         | Video call | Slack      | Email
Professional Translator       | Email         | Optional   | Email      | Email
QA Specialist                 | Dashboard     | Video call | Slack      | Email
Project Manager (PM)          | Dashboard     | Video call | Slack      | Email
```

## Selecting Translation Management Tools

### Step 1: Evaluate Available Tools

#### Option 1: Crowdsourced Translation Platforms

**Characteristics:**
- Global translator networks
- Competitive pricing
- Built-in QA tools
- Project management features

**Popular platforms:**
- Crowdin
- Lokalise
- OneSky
- Transifex

**Advantages:**
- Access to global talent
- Built-in platforms and workflows
- Automated progress tracking
- Integration with development tools

**Disadvantages:**
- Higher costs for quality
- Less control over translators
- Privacy considerations
- Potential quality variance

#### Option 2: Professional Translation Agencies

**Characteristics:**
- Dedicated team members
- Higher quality assurance
- Industry expertise
- Premium pricing

**Advantages:**
- Consistent translator team
- Subject matter expertise
- Dedicated project managers
- Premium quality control

**Disadvantages:**
- Higher costs
- Less flexibility for quick changes
- Longer turnaround times
- Potential communication barriers

#### Option 3: In-House Team

**Characteristics:**
- Full control over process
- Lower costs long-term
- Company culture alignment
- Flexibility

**Advantages:**
- Full control and visibility
- Product knowledge depth
- Direct communication
- Cost effective at scale

**Disadvantages:**
- Hiring and training required
- Limited language coverage
- Resource constraints
- Requires management overhead

### Step 2: Set Up Translation Management Platform

**Example: Setting up Lokalise**

```bash
# Step 1: Install Lokalise CLI
npm install -g @lokalise/node-cli

# Step 2: Authenticate
lokalise config set --api-key YOUR_API_KEY --project-id YOUR_PROJECT_ID

# Step 3: Create project structure
lokalise project create --name "Documentation Localization"

# Step 4: Configure languages
lokalise language create \
  --language de \
  --language fr \
  --language ja \
  --language es

# Step 5: Upload base language strings
lokalise file upload \
  --file i18n/locales/en.json \
  --language-id en \
  --file-format json
```

### Step 3: Configure Tool Settings

**Translation Tool Configuration Template:**

```json
{
  "tool": "lokalise",
  "projectId": "project_123456",
  "settings": {
    "baseLanguage": "en",
    "targetLanguages": ["de", "fr", "ja", "es"],
    "qualityChecks": {
      "missingTranslations": true,
      "emptyTranslations": true,
      "duplicateStrings": true,
      "unsafeHTML": true,
      "leading/trailingWhitespace": true
    },
    "automations": {
      "autoApprove": false,
      "autoSync": true,
      "autoArchive": true
    },
    "notifications": {
      "newStringEmail": true,
      "translationComplete": true,
      "reviewRequired": true
    },
    "accessControl": {
      "translatorCanEdit": true,
      "translatorCanComment": true,
      "translatorCanViewVocabulary": true
    }
  }
}
```

## Setting Up Extraction Process

### Step 1: Create Extraction Script

**scripts/extract-strings.js:**

```javascript
const fs = require('fs');
const path = require('path');
const marked = require('marked');

class StringExtractor {
  constructor(config) {
    this.config = config;
    this.strings = {};
    this.metadata = {};
  }

  extractFromMarkdown(filePath, locale = 'en') {
    const content = fs.readFileSync(filePath, 'utf-8');
    const tokens = marked.lexer(content);

    return this.processTokens(tokens, filePath);
  }

  processTokens(tokens, filePath) {
    const extracted = {};
    let keyPrefix = this.generateKeyPrefix(filePath);

    tokens.forEach((token, index) => {
      if (token.type === 'heading') {
        const key = `${keyPrefix}.heading.${index}`;
        extracted[key] = {
          text: token.text,
          context: 'heading',
          level: token.depth,
          source: filePath
        };
      } else if (token.type === 'paragraph') {
        const key = `${keyPrefix}.paragraph.${index}`;
        extracted[key] = {
          text: token.text,
          context: 'paragraph',
          source: filePath
        };
      } else if (token.type === 'list') {
        token.items.forEach((item, itemIndex) => {
          const key = `${keyPrefix}.listItem.${index}.${itemIndex}`;
          extracted[key] = {
            text: item.text,
            context: 'list_item',
            source: filePath
          };
        });
      }
    });

    return extracted;
  }

  generateKeyPrefix(filePath) {
    const relative = path.relative('source/', filePath);
    return relative
      .replace(/\.md$/, '')
      .replace(/\//g, '.')
      .replace(/\s+/g, '_');
  }

  extractFromDirectory(directory) {
    const allStrings = {};

    const walkDir = (dir) => {
      const files = fs.readdirSync(dir);

      files.forEach(file => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);

        if (stat.isDirectory()) {
          walkDir(filePath);
        } else if (file.endsWith('.md')) {
          const extracted = this.extractFromMarkdown(filePath);
          Object.assign(allStrings, extracted);
        }
      });
    };

    walkDir(directory);
    return allStrings;
  }

  generateTranslationFile(strings, locale = 'en') {
    const output = {
      language: locale,
      extracted: new Date().toISOString(),
      strings: {}
    };

    Object.entries(strings).forEach(([key, data]) => {
      output.strings[key] = data.text;
    });

    return output;
  }

  saveExtraction(strings, outputPath) {
    const output = this.generateTranslationFile(strings);
    fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
    console.log(`Extracted ${Object.keys(strings).length} strings`);
    console.log(`Saved to ${outputPath}`);
  }
}

// Run extraction
const config = require('../i18n/config.json');
const extractor = new StringExtractor(config);
const strings = extractor.extractFromDirectory('source/');
extractor.saveExtraction(strings, 'i18n/extracted/en.json');
```

### Step 2: Automate Extraction on Content Changes

**scripts/watch-and-extract.js:**

```javascript
const fs = require('fs');
const path = require('path');
const chokidar = require('chokidar');
const StringExtractor = require('./extract-strings');

class ExtractionWatcher {
  constructor(config) {
    this.config = config;
    this.extractor = new StringExtractor(config);
    this.debounceTimer = null;
  }

  watch() {
    const watcher = chokidar.watch('source/**/*.md', {
      persistent: true,
      ignoreInitial: true
    });

    console.log('Watching for content changes...');

    watcher.on('change', (filePath) => {
      console.log(`File changed: ${filePath}`);
      this.scheduleExtraction();
    });

    watcher.on('add', (filePath) => {
      console.log(`File added: ${filePath}`);
      this.scheduleExtraction();
    });

    watcher.on('unlink', (filePath) => {
      console.log(`File removed: ${filePath}`);
      this.scheduleExtraction();
    });
  }

  scheduleExtraction() {
    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => {
      this.performExtraction();
    }, 2000); // Wait 2 seconds after last change
  }

  performExtraction() {
    console.log('Running extraction...');
    try {
      const strings = this.extractor.extractFromDirectory('source/');
      this.extractor.saveExtraction(strings, 'i18n/extracted/en.json');
      console.log('Extraction complete');
    } catch (error) {
      console.error('Extraction error:', error);
    }
  }
}

// Run watcher
const config = require('../i18n/config.json');
const watcher = new ExtractionWatcher(config);
watcher.watch();
```

## Creating Translator Guidelines

### Step 1: Create Comprehensive Guidelines Document

**TRANSLATOR_GUIDELINES.md:**

```markdown
# Translator Guidelines

## General Principles

### 1. Maintain Tone and Style
- Technical but accessible
- Professional yet friendly
- Consistent with product voice
- Clear and concise

### 2. Cultural Adaptation
- Adapt examples to local context
- Use region-appropriate terminology
- Consider cultural sensitivities
- Maintain technical accuracy

### 3. Consistency
- Use approved glossary terms consistently
- Maintain consistent terminology across documents
- Follow established formatting conventions
- Apply consistent punctuation and spacing

## Language-Specific Guidelines

### German (Deutsch)
- Capitalization: Capitalize all nouns
- Compounds: Use modern spelling (e.g., "Datenbasis" not "Daten-Basis")
- Pronouns: Use formal "Sie" for documentation
- Examples:
  - "Konfiguration" (not "Einstellung" when technical)
  - "Abfrage" (for "query")

### French (Français)
- Spacing: Space before punctuation marks (!, ?, :, ;)
- Abbreviations: Expand abbreviations in French
- Articles: Pay attention to gender agreements
- Examples:
  - "Configuration" (la configuration)
  - "Requête" (for "query")
  - Use "vous" (formal) unless context requires "tu"

### Japanese (日本語)
- Writing system: Use hiragana, katakana, and kanji appropriately
- Technical terms: Use katakana for technical terms unless Japanese equivalent is standard
- Formality: Maintain polite form (丁寧形)
- Examples:
  - "設定" (seichi) for configuration
  - "クエリ" (kuer) for query

## Glossary Management

### Core Terms (English → Target Language)

[Maintain a glossary table with:]
- English term
- Target language translation
- Context/usage
- Example sentence
- Approved by (person/date)

### Term Variation Restrictions
- API → API (not translated)
- API Reference → [Language] - API リファレンス
- URL → URL (not translated)
- Database → Datenbank, Base de données, データベース

## Formatting Rules

### Placeholders
- Preserve: {variable_name}, {{placeholders}}, <placeholder>
- Don't translate placeholder content
- Don't change placeholder format
- Example: "Configure {hostname}" → "Konfigurieren Sie {hostname}"

### Code Blocks
- Don't translate code or command-line examples
- Translate comments in code if language-specific comments supported
- Maintain code formatting exactly

### Links and References
- Preserve all link structures
- Only translate link text/labels
- Don't translate anchors or IDs
- Example: `[Learn More](../guides/advanced)` → `[Weitere Informationen](../guides/advanced)`

### Special Formatting
- Preserve Markdown syntax (*italic*, **bold**, etc.)
- Preserve HTML tags and attributes
- Maintain spacing and line breaks
- Don't remove or add formatting

## Quality Standards

### Minimum Quality Criteria
- ✓ No untranslated strings
- ✓ No placeholder corruption
- ✓ No code/command corruption
- ✓ Consistency with glossary
- ✓ No formatting errors
- ✓ Readability check passed
- ✓ Context-appropriate terminology

### Common Mistakes to Avoid
1. Translating placeholders or variable names
2. Breaking code formatting
3. Adding/removing spaces incorrectly
4. Using inconsistent terminology
5. Changing list or numbering structures
6. Modifying links or references
7. Translating technical terms that should remain English

## Context and Resources

### For Translators
- Access: [Translation Platform Link]
- Glossary: [Glossary Link]
- Reference docs: [Reference Documents]
- Examples: [Example Translations]

### Asking for Clarification
- Comment in translation tool
- Use "Request for Context" feature
- Contact: [Contact Person/Email]
- Response time: Within 24 hours

## Feedback Process

- All feedback incorporated as updates to guidelines
- Monthly glossary review meetings
- Continuous improvement process
- Version control for guideline changes
```

### Step 2: Create Language-Specific Glossaries

**i18n/glossaries/de-glossary.json:**

```json
{
  "glossary": {
    "metadata": {
      "language": "German",
      "code": "de",
      "lastUpdated": "2024-01-15",
      "maintainer": "translation-team@company.com"
    },
    "terms": {
      "API": {
        "translation": "API",
        "context": "Application Programming Interface",
        "usage": "Always use 'API', never translate"
      },
      "authentication": {
        "translation": "Authentifizierung",
        "context": "Verification of identity",
        "usage": "Use for user verification processes",
        "example": "Authentifizierung ist erforderlich"
      },
      "configuration": {
        "translation": "Konfiguration",
        "context": "System setup and settings",
        "usage": "Technical configuration context",
        "example": "Passen Sie die Konfiguration an"
      },
      "database": {
        "translation": "Datenbank",
        "context": "Data storage system",
        "usage": "Technical database references",
        "example": "Die Datenbank speichert alle Daten"
      },
      "parameter": {
        "translation": "Parameter",
        "context": "Function or system parameters",
        "usage": "Technical parameters",
        "example": "Geben Sie den Parameter ein"
      },
      "query": {
        "translation": "Abfrage",
        "context": "Database or search query",
        "usage": "Database operations",
        "example": "Erstellen Sie eine neue Abfrage"
      }
    }
  }
}
```

## Implementing Review Workflow

### Step 1: Define Review Stages

**Review Process Flowchart:**

```
Translation Submitted
        ↓
Self-Review (Translator)
        ↓
    [Issues Found?]
    ↙           ↘
   Yes           No
    ↓             ↓
  Edit      Quality Check
    ↓             ↓
  Back      [QA Pass?]
         ↙           ↘
        No             Yes
        ↓              ↓
    Fix QA       Editorial Review
    Issues            ↓
        ↓         [Approved?]
      Back      ↙            ↘
                Yes             No
                ↓               ↓
            Integration      Feedback Loop
                ↓
            Build & Deploy
```

### Step 2: Create Review Checklist

**REVIEW_CHECKLIST.md:**

```markdown
# Translation Review Checklist

## Self-Review (By Translator)

- [ ] All strings translated (no English text remaining)
- [ ] Glossary terms used consistently
- [ ] Tone and style match guidelines
- [ ] No formatting errors
- [ ] No broken placeholders
- [ ] Punctuation and spacing correct
- [ ] Context makes sense in target language
- [ ] Cultural adaptation appropriate
- [ ] Grammar and spelling checked
- [ ] Read complete sentence aloud for naturalness

## QA Check (Automated + Manual)

### Formatting Checks
- [ ] No broken XML/HTML tags
- [ ] Placeholders intact and unchanged
- [ ] Code blocks unmodified
- [ ] Links and references preserved
- [ ] Markdown syntax intact
- [ ] Whitespace preserved

### Content Checks
- [ ] No missing translations
- [ ] No untranslated English strings
- [ ] No placeholder text left untranslated
- [ ] String count matches source
- [ ] No duplicate keys

### Consistency Checks
- [ ] Terminology matches glossary
- [ ] Consistent terminology across document
- [ ] Consistent punctuation patterns
- [ ] Consistent capitalization

## Editorial Review (By Project Manager/Senior Translator)

- [ ] Translation accuracy verified
- [ ] Technical terminology appropriate
- [ ] Tone and voice appropriate for audience
- [ ] Glossary terms used correctly
- [ ] No errors missed in QA
- [ ] Cultural adaptations appropriate
- [ ] Overall quality meets standards
- [ ] Ready for integration

## Final Approval

- [ ] All checklist items passed
- [ ] No outstanding issues
- [ ] Approved by: [Name]
- [ ] Approved on: [Date]
- [ ] Notes: [Any relevant notes]
```

### Step 3: Implement Review Workflow in Tool

**workflows/review.json:**

```json
{
  "workflow": "translation-review",
  "stages": [
    {
      "name": "translator-selfReview",
      "duration": "2 days",
      "assigned_to": "translator",
      "required_checks": [
        "completeness",
        "glossary-consistency",
        "formatting"
      ]
    },
    {
      "name": "qa-automated",
      "duration": "1 day",
      "assigned_to": "qa-system",
      "checks": [
        "syntax_validation",
        "placeholder_integrity",
        "string_count",
        "consistency",
        "terminology"
      ]
    },
    {
      "name": "editorial-review",
      "duration": "2 days",
      "assigned_to": "pm-or-senior-translator",
      "approval_required": true,
      "required_checklist": "REVIEW_CHECKLIST.md"
    },
    {
      "name": "final-approval",
      "duration": "1 day",
      "assigned_to": "pm",
      "approval_required": true
    }
  ],
  "escalation": {
    "unresolved_issues": "pm@company.com",
    "missed_deadline": "pm@company.com",
    "quality_concerns": "qa-lead@company.com"
  },
  "slas": {
    "translator_selfReview": "2 days",
    "qa_check": "1 day",
    "editorial_review": "2 days",
    "final_approval": "1 day",
    "total": "6 days"
  }
}
```

## Integration with Version Control

### Step 1: Set Up Git Integration

**Create .gitignore for translation files:**

```
# Translation working files
i18n/extracted/
translations/in-progress/
translations/review/

# Build artifacts
build/localized/

# Translation tool cache
.lokalise/
.crowdin/

# Temporary files
*.tmp
*.bak
*.swp
```

### Step 2: Create Git Workflow Hooks

**scripts/pre-commit-hook.sh:**

```bash
#!/bin/bash

echo "Running translation validation..."

# Check for untranslated files
if [ -f "i18n/extracted/untranslated.json" ]; then
  echo "ERROR: Untranslated strings found"
  exit 1
fi

# Validate JSON files
for file in i18n/locales/*.json; do
  if ! jq empty "$file" 2>/dev/null; then
    echo "ERROR: Invalid JSON in $file"
    exit 1
  fi
done

# Check for broken placeholders
node scripts/validate-placeholders.js
if [ $? -ne 0 ]; then
  echo "ERROR: Placeholder validation failed"
  exit 1
fi

echo "All validation checks passed"
exit 0
```

**scripts/post-merge-hook.sh:**

```bash
#!/bin/bash

echo "Post-merge: Checking translation integrity..."

# If localization files changed, regenerate builds
if git diff --name-only MERGE_HEAD | grep -q "i18n/"; then
  echo "Translation files changed - rebuilding..."
  npm run build:i18n
fi

exit 0
```

### Step 3: Create Commit Message Standards

**COMMIT_STANDARDS.md:**

```markdown
# Commit Message Standards for Translations

## Format

```
[LOCALE] type: description

Body (optional)
```

## Types
- `feat`: New translations
- `fix`: Translation fixes
- `refactor`: Restructuring translations
- `chore`: Maintenance tasks

## Examples

```
[de] feat: Complete German translation for API reference

Translates all 245 strings in the API reference guide.
Reviewed by: John Smith
QA Status: Passed
Completeness: 100%

[fr] fix: Correct terminology in authentication section

Changed "connexion" to "authentification" to match glossary.
Fixes issue #142
```

## Tools
- Enforce with husky hooks
- Validate with commitlint
- Track with commit metrics
```

## Automating Workflow Steps

### Step 1: Create Orchestration Script

**scripts/orchestrate-workflow.js:**

```javascript
const fs = require('fs');
const path = require('path');

class WorkflowOrchestrator {
  constructor(config) {
    this.config = config;
    this.workflowState = {};
  }

  async runWorkflow(sourceLocale = 'en') {
    console.log('Starting translation workflow orchestration...');

    try {
      // Step 1: Extract strings
      await this.extractStrings(sourceLocale);

      // Step 2: Prepare for translation
      await this.prepareForTranslation();

      // Step 3: Upload to translation platform
      await this.uploadToTranslationPlatform();

      // Step 4: Assign to translators
      await this.assignToTranslators();

      // Step 5: Monitor progress
      await this.monitorProgress();

      // Step 6: Run QA
      await this.runQAChecks();

      // Step 7: Generate reports
      await this.generateReports();

      console.log('Workflow completed successfully');
      return this.workflowState;
    } catch (error) {
      console.error('Workflow error:', error);
      throw error;
    }
  }

  async extractStrings(locale) {
    console.log('Step 1: Extracting strings...');
    // Implementation
  }

  async prepareForTranslation() {
    console.log('Step 2: Preparing for translation...');
    // Implementation
  }

  async uploadToTranslationPlatform() {
    console.log('Step 3: Uploading to translation platform...');
    // Implementation
  }

  async assignToTranslators() {
    console.log('Step 4: Assigning to translators...');
    // Implementation
  }

  async monitorProgress() {
    console.log('Step 5: Monitoring progress...');
    // Implementation
  }

  async runQAChecks() {
    console.log('Step 6: Running QA checks...');
    // Implementation
  }

  async generateReports() {
    console.log('Step 7: Generating reports...');
    // Implementation
  }

  saveState() {
    fs.writeFileSync(
      'workflow-state.json',
      JSON.stringify(this.workflowState, null, 2)
    );
  }
}

// Run workflow
const config = require('../i18n/config.json');
const orchestrator = new WorkflowOrchestrator(config);

orchestrator.runWorkflow()
  .then(() => orchestrator.saveState())
  .catch(error => process.exit(1));
```

### Step 2: Create Scheduling Script

**scripts/schedule-workflow.js:**

```javascript
const cron = require('node-cron');
const WorkflowOrchestrator = require('./orchestrate-workflow');

class ScheduledWorkflow {
  constructor(config) {
    this.config = config;
    this.orchestrator = new WorkflowOrchestrator(config);
  }

  scheduleWorkflows() {
    // Run workflow every Monday at 9 AM
    cron.schedule('0 9 * * MON', async () => {
      console.log('Running scheduled translation workflow...');
      try {
        await this.orchestrator.runWorkflow();
      } catch (error) {
        console.error('Scheduled workflow error:', error);
        this.notifyOnError(error);
      }
    });

    // Generate progress report every Friday
    cron.schedule('0 15 * * FRI', async () => {
      console.log('Generating weekly progress report...');
      // Implementation
    });

    // Check for translation completion daily
    cron.schedule('0 * * * *', async () => {
      console.log('Checking translation completion...');
      // Implementation
    });

    console.log('Translation workflows scheduled');
  }

  notifyOnError(error) {
    // Send notification to PM
    console.log('Sending error notification...');
  }
}

// Start scheduling
const config = require('../i18n/config.json');
const scheduler = new ScheduledWorkflow(config);
scheduler.scheduleWorkflows();

// Keep process running
process.on('SIGINT', () => {
  console.log('Scheduler shutting down...');
  process.exit(0);
});
```

## Monitoring and Metrics

### Step 1: Create Metrics Dashboard

**scripts/generate-metrics.js:**

```javascript
class MetricsGenerator {
  constructor(config) {
    this.config = config;
    this.metrics = {};
  }

  generateMetrics() {
    return {
      completionMetrics: this.calculateCompletion(),
      velocityMetrics: this.calculateVelocity(),
      qualityMetrics: this.calculateQuality(),
      timelineMetrics: this.calculateTimeline()
    };
  }

  calculateCompletion() {
    // Calculate percentage of strings translated per locale
    return {
      en: { total: 1000, translated: 1000, percentage: 100 },
      de: { total: 1000, translated: 950, percentage: 95 },
      fr: { total: 1000, translated: 920, percentage: 92 },
      ja: { total: 1000, translated: 850, percentage: 85 }
    };
  }

  calculateVelocity() {
    // Strings translated per day per translator
    return {
      translator1: 120,
      translator2: 150,
      translator3: 95,
      average: 121.7
    };
  }

  calculateQuality() {
    // QA pass rates and error counts
    return {
      qaPassRate: 94.2,
      avgIssuesPerTranslation: 1.3,
      commonIssues: {
        formatting: 12,
        terminology: 8,
        missing_translation: 5,
        placeholder_corruption: 2
      }
    };
  }

  calculateTimeline() {
    // Timeline tracking
    return {
      totalDays: 30,
      daysElapsed: 15,
      daysRemaining: 15,
      onTrack: true,
      riskFactors: []
    };
  }

  generateReport() {
    const metrics = this.generateMetrics();
    return {
      generatedAt: new Date().toISOString(),
      metrics: metrics,
      summary: this.generateSummary(metrics)
    };
  }

  generateSummary(metrics) {
    return `
Translation Project Status Report
==================================

Completion: ${metrics.completionMetrics.overall}%
Quality: ${metrics.qualityMetrics.qaPassRate}%
Timeline: On Track

Key Metrics:
- Total Strings: 1000
- Translated: 940
- In Review: 45
- Pending: 15

Next Steps:
- Complete Japanese translation (currently 85%)
- Resolve 8 terminology issues
- Deploy approved translations by Friday
    `;
  }
}
```

### Step 2: Create Reporting Infrastructure

**workflows/reporting.json:**

```json
{
  "reports": [
    {
      "name": "dailyProgressReport",
      "schedule": "daily at 5 PM",
      "recipients": ["pm@company.com", "team@company.com"],
      "content": [
        "translation_completion_percentage",
        "new_translations_today",
        "issues_resolved",
        "translator_activity"
      ]
    },
    {
      "name": "weeklyStatusReport",
      "schedule": "every Friday at 4 PM",
      "recipients": ["stakeholders@company.com"],
      "content": [
        "completion_status",
        "quality_metrics",
        "timeline_status",
        "risks_and_blockers"
      ]
    },
    {
      "name": "translatorPerformance",
      "schedule": "monthly",
      "recipients": ["pm@company.com"],
      "content": [
        "strings_translated_per_person",
        "qa_pass_rate",
        "average_turnaround_time",
        "common_errors"
      ]
    }
  ]
}
```

## Troubleshooting Workflow Issues

### Issue 1: Delayed Translations

**Problem**: Translators missing deadlines

**Solution**:
- Implement daily progress tracking
- Set intermediate milestones
- Redistribute work if needed
- Communicate blockers immediately

```javascript
class DeadlineMonitor {
  checkDeadlines() {
    const assignments = this.getAssignments();

    assignments.forEach(assignment => {
      const daysUntilDue = this.calculateDaysUntilDue(assignment.deadline);
      const percentComplete = this.getCompletionPercentage(assignment);
      const expectedComplete = daysUntilDue / assignment.totalDays;

      if (percentComplete < expectedComplete * 0.9) {
        this.raiseAlert(assignment, 'Behind Schedule');
      }
    });
  }
}
```

### Issue 2: Inconsistent Terminology

**Problem**: Different translators use different terms for same concept

**Solution**:
- Enforce glossary usage in tool
- Regular terminology reviews
- Automated consistency checks
- Translator training on glossary

### Issue 3: Quality Issues Discovered Late

**Problem**: Quality problems found after approval

**Solution**:
- Implement automated QA earlier in workflow
- Strengthen peer review process
- Create QA checklist
- Use machine learning for pattern detection

```javascript
class EarlyQADetection {
  runAutomatedChecks(translation) {
    return {
      formatting: this.checkFormatting(translation),
      placeholders: this.checkPlaceholders(translation),
      terminology: this.checkTerminology(translation),
      encoding: this.checkEncoding(translation),
      context: this.checkContext(translation)
    };
  }
}
```

## Conclusion

A well-designed translation workflow ensures:
- Consistent, high-quality translations
- Clear responsibilities and accountability
- Efficient progress tracking
- Scalable process for multiple languages
- Strong collaboration across teams
- Measurable quality improvements

Remember to continually refine your workflow based on team feedback and metrics.

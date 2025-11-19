# Maintaining Multilingual Documentation: Keeping Translations Current

## Overview

This guide provides comprehensive step-by-step instructions for maintaining and updating multilingual documentation over time. Keeping translations synchronized with source content updates is essential for maintaining quality, consistency, and user trust across all languages.

## Table of Contents

1. [Maintenance Strategy Overview](#maintenance-strategy-overview)
2. [Establishing Update Workflows](#establishing-update-workflows)
3. [Version Control and Tracking](#version-control-and-tracking)
4. [Change Detection and Synchronization](#change-detection-and-synchronization)
5. [Translator Communication](#translator-communication)
6. [Managing Incremental Updates](#managing-incremental-updates)
7. [Handling Deprecated Content](#handling-deprecated-content)
8. [Translation Memory and Reuse](#translation-memory-and-reuse)
9. [Quality Maintenance](#quality-maintenance)
10. [Deprecation and Sunset Procedures](#deprecation-and-sunset-procedures)

## Maintenance Strategy Overview

### Multi-Language Maintenance Approach

```
Source Content Updated
        ↓
Change Detection
        ↓
Impact Analysis
        ↓
Update Prioritization
        ↓
Translator Assignment
        ↓
Translation Update
        ↓
QA Review
        ↓
Integration
        ↓
Release Management
        ↓
Documentation Released
```

### Maintenance Principles

**Principle 1: Single Source of Truth**
- Source language (English) is authoritative
- All translations derived from source
- Maintain source as reference
- Don't modify translations directly

**Principle 2: Continuous Synchronization**
- Keep translations synchronized with source
- Update promptly after source changes
- Track update status per language
- Report synchronization metrics

**Principle 3: Efficiency**
- Only translate changed content
- Reuse existing translations
- Batch updates where possible
- Automate where feasible

**Principle 4: Quality Consistency**
- Apply same QA standards to updates
- Maintain terminology consistency
- Preserve previous quality level
- Test before release

**Principle 5: Communication**
- Inform translators of changes
- Provide context for updates
- Enable quick turnaround
- Track progress visibly

### Maintenance Timeline

```
Change Frequency → Maintenance Frequency
Minor (< 5% monthly) → Monthly updates
Moderate (5-10% monthly) → Bi-weekly updates
Frequent (> 10% monthly) → Weekly updates
Critical changes → Immediate updates
```

## Establishing Update Workflows

### Step 1: Create Update Process Documentation

**MAINTENANCE_PROCESS.md:**

```markdown
# Documentation Maintenance Process

## Process Overview

### Trigger Events

Documentation updates are triggered by:

1. **Product Updates**
   - New features released
   - Existing features changed
   - Deprecated features removed
   - Bug fixes affecting documentation
   - API changes

2. **Documentation Improvements**
   - Clarity improvements
   - Example updates
   - Error corrections
   - Structure reorganization
   - Link updates

3. **Localization Improvements**
   - Terminology refinement
   - Translation improvements
   - Cultural adaptation updates
   - Format updates

## Update Workflow

```
Change Identified in Source
        ↓
Document Change Details
        ↓
Assess Impact on Translations
        ↓
Prioritize Update
        ↓
Create Update Request
        ↓
Assign to Translators
        ↓
Translator Updates Content
        ↓
QA Review
        ↓
Staging/Testing
        ↓
Release Planning
        ↓
Release
```

## Update Classification

### Type 1: Minor Updates
- Fixing typos
- Formatting corrections
- Link updates
- Example improvements
- Estimated impact: 5-10% of strings

**Update Process:**
- Direct assignment to translators
- Fast-track QA (1-2 days)
- Can batch with other minor updates

### Type 2: Moderate Updates
- New sections added
- Existing sections rewritten (> 20% change)
- Terminology updates
- Example changes
- Estimated impact: 10-30% of strings

**Update Process:**
- Provide detailed change context
- Normal QA timeline (3-4 days)
- Plan for 1-2 week turnaround

### Type 3: Major Updates
- Significant restructuring
- Large content additions
- Multiple terminology changes
- Feature documentation
- Estimated impact: > 30% of strings

**Update Process:**
- Plan with translator lead
- Provide extensive context
- Extended QA timeline
- Plan for 2-4 week turnaround
- May require additional resources

## Scheduling and Planning

### Update Windows

**Monthly Release Cycle**
- Collect all changes during month
- Release all translations together
- Coordinate with product release
- Minimize user confusion

**Critical Hotfixes**
- Security issues → within 24 hours
- Breaking changes → within 2-3 days
- Major bugs → within 1 week

### Resource Planning

- Account for translator availability
- Plan for time zone differences
- Consider holidays and vacations
- Budget for additional QA if needed
- Allocate buffer time

## Approval Process

1. **Change Review**
   - Source change reviewed
   - Approval from content owner
   - Impact assessed

2. **Update Planning**
   - Priority determined
   - Resources allocated
   - Timeline set

3. **Translator Assignment**
   - Translator notified
   - Instructions provided
   - Deadline set

4. **Update Execution**
   - Translation completed
   - Self-review performed
   - Submitted for QA

5. **QA and Approval**
   - QA review completed
   - Issues resolved
   - Final approval obtained

6. **Release Planning**
   - Release coordinated
   - Testing completed
   - Release date set

7. **Release**
   - Translations published
   - Users notified
   - Feedback monitored
```

### Step 2: Create Change Request Template

**CHANGE_REQUEST_TEMPLATE.md:**

```markdown
# Change Request Template

## Basic Information

**Change ID**: [auto-generated]
**Submitted by**: [name]
**Submission Date**: [date]
**Change Type**: ☐ Minor ☐ Moderate ☐ Major
**Urgency**: ☐ Routine ☐ Priority ☐ Critical

## Change Details

### What Changed

**Document(s) Affected**
- [List affected documents]

**Location(s)**
- [Specific sections/pages]

**Type of Change**
- ☐ Addition
- ☐ Modification
- ☐ Deletion
- ☐ Reorganization

### Description

[Describe the change in detail]

### Before and After

**Before:**
[Original content]

**After:**
[New content]

### Change Context

**Why This Change?**
[Reason for the update]

**Related Issues/Features**
[Issue numbers, feature names, etc.]

**Product Version Affected**
[Applicable product versions]

### Impact Analysis

**Estimated Lines Changed**
[Number]

**Estimated Strings to Translate**
[Number]

**Affected Languages**
- ☐ All languages
- ☐ Specific: [list]

**Complexity**
☐ Simple (direct translation)
☐ Moderate (context needed)
☐ Complex (restructuring required)

### Timeline

**Source Change Date**
[When change is/was made]

**Translation Deadline**
[When translations must be complete]

**Release Date**
[When translated content must be live]

**Days to Complete**: [deadline - today]

### Resources Required

**Translator Hours Estimated**
[Estimated hours]

**QA Hours Estimated**
[Estimated hours]

**Review Expertise Needed**
- ☐ Product knowledge
- ☐ Technical expertise
- ☐ Cultural knowledge
- ☐ Terminology expertise

### Additional Context

**Glossary Updates Needed**
[List any new terms]

**Links or References**
[Related documentation links]

**Example Code Changes**
[If applicable]

**Attached Files**
[Change documentation, examples, etc.]

## Approval

- Requested by: [name] | Date: [date]
- Approved by: [name] | Date: [date]
- Assigned to: [name] | Date: [date]

## Tracking

**Status**: ☐ Submitted ☐ In Progress ☐ QA ☐ Complete
**Progress**: [percentage complete]
**Notes**: [any relevant notes]
```

## Version Control and Tracking

### Step 1: Implement Version Tracking

**version-tracking.json:**

```json
{
  "contentVersioning": {
    "strategy": "semantic-versioning",
    "format": "MAJOR.MINOR.PATCH",
    "examples": {
      "major": "Significant restructuring or large content changes",
      "minor": "New sections or moderate changes",
      "patch": "Fixes, typos, minor updates"
    }
  },
  "documents": {
    "getting-started.md": {
      "en": {
        "version": "2.1.3",
        "lastUpdated": "2024-01-15",
        "updateType": "patch",
        "updateReason": "Fixed typo in step 3"
      },
      "de": {
        "version": "2.1.2",
        "lastUpdated": "2024-01-10",
        "syncStatus": "outdated",
        "syncPercentage": 95,
        "missingUpdates": "Typo fix from en v2.1.3"
      },
      "fr": {
        "version": "2.1.3",
        "lastUpdated": "2024-01-16",
        "syncStatus": "current",
        "syncPercentage": 100
      },
      "ja": {
        "version": "2.0.0",
        "lastUpdated": "2023-11-20",
        "syncStatus": "outdated",
        "syncPercentage": 87,
        "missingUpdates": "Minor: New section added in v2.1.0, Patch: Typo fix in v2.1.3"
      }
    }
  }
}
```

### Step 2: Create Version Control Scripts

**scripts/track-versions.js:**

```javascript
const fs = require('fs');
const path = require('path');
const semver = require('semver');

class VersionTracker {
  constructor(config) {
    this.config = config;
    this.tracking = this.loadTracking();
  }

  recordUpdate(document, language, changeType, reason) {
    if (!this.tracking[document]) {
      this.tracking[document] = {};
    }

    const current = this.tracking[document][language] || {
      version: '1.0.0',
      lastUpdated: null
    };

    // Increment version based on change type
    let newVersion;
    switch (changeType) {
      case 'major':
        newVersion = semver.inc(current.version, 'major');
        break;
      case 'minor':
        newVersion = semver.inc(current.version, 'minor');
        break;
      case 'patch':
        newVersion = semver.inc(current.version, 'patch');
        break;
      default:
        newVersion = current.version;
    }

    this.tracking[document][language] = {
      version: newVersion,
      lastUpdated: new Date().toISOString(),
      updateType: changeType,
      updateReason: reason,
      syncStatus: language === 'en' ? 'current' : 'needs-review'
    };

    this.saveTracking();
    return newVersion;
  }

  getSyncStatus() {
    const status = {};
    const sourceVersion = this.tracking.en || {};

    Object.entries(this.tracking).forEach(([doc, langs]) => {
      status[doc] = {};
      const sourceVer = sourceVersion[doc]?.version || '0.0.0';

      Object.entries(langs).forEach(([lang, info]) => {
        if (lang === 'en') {
          status[doc][lang] = { status: 'current', version: info.version };
        } else {
          const targetVer = info.version || '0.0.0';
          const isOutdated = semver.lt(targetVer, sourceVer);

          status[doc][lang] = {
            status: isOutdated ? 'outdated' : 'current',
            currentVersion: targetVer,
            sourceVersion: sourceVer,
            lastUpdated: info.lastUpdated
          };
        }
      });
    });

    return status;
  }

  generateSyncReport() {
    const status = this.getSyncStatus();
    const report = {
      timestamp: new Date().toISOString(),
      documents: {},
      summary: {
        total: 0,
        current: 0,
        outdated: 0,
        percent: 0
      }
    };

    Object.entries(status).forEach(([doc, langs]) => {
      report.documents[doc] = langs;
      const langCount = Object.entries(langs).filter(([lang]) => lang !== 'en').length;
      const currentCount = Object.entries(langs)
        .filter(([lang, info]) => lang !== 'en' && info.status === 'current')
        .length;

      report.summary.total += langCount;
      report.summary.current += currentCount;
    });

    report.summary.outdated = report.summary.total - report.summary.current;
    report.summary.percent = ((report.summary.current / report.summary.total) * 100).toFixed(1);

    return report;
  }

  loadTracking() {
    const trackingPath = path.join(__dirname, '../tracking/version-tracking.json');
    if (fs.existsSync(trackingPath)) {
      return JSON.parse(fs.readFileSync(trackingPath, 'utf-8'));
    }
    return {};
  }

  saveTracking() {
    const trackingPath = path.join(__dirname, '../tracking/version-tracking.json');
    fs.writeFileSync(trackingPath, JSON.stringify(this.tracking, null, 2));
  }
}

module.exports = VersionTracker;
```

### Step 3: Set Up Git Tagging

**Create version tags in Git:**

```bash
#!/bin/bash

# Tag releases by language and version
# Format: docs-{language}-{version}

# After translation release
git tag docs-de-v2.1.3
git tag docs-fr-v2.1.3
git tag docs-ja-v2.0.5

# Push tags
git push origin --tags

# View tags for specific language
git tag | grep "docs-de"

# View changes since last release
git log docs-de-v2.1.2..docs-de-v2.1.3

# Create release notes from tags
git log docs-de-v2.1.2..docs-de-v2.1.3 --pretty=format:"%h - %s" > de-release-notes.txt
```

## Change Detection and Synchronization

### Step 1: Implement Change Detection

**scripts/detect-changes.js:**

```javascript
const fs = require('fs');
const path = require('path');
const diff = require('diff');

class ChangeDetector {
  constructor() {
    this.changes = [];
  }

  detectChanges(sourcePath, previousVersionPath) {
    const currentContent = fs.readFileSync(sourcePath, 'utf-8');
    const previousContent = fs.readFileSync(previousVersionPath, 'utf-8');

    const differences = diff.diffLines(previousContent, currentContent);
    const analysis = this.analyzeDifferences(differences);

    return {
      file: sourcePath,
      changeType: this.classifyChanges(analysis),
      changePercentage: this.calculateChangePercentage(analysis),
      affectedSections: this.identifyAffectedSections(differences),
      changes: differences.filter(d => d.added || d.removed)
    };
  }

  analyzeDifferences(diffs) {
    const analysis = {
      additions: [],
      deletions: [],
      modifications: []
    };

    for (let i = 0; i < diffs.length; i++) {
      if (diffs[i].added) {
        analysis.additions.push(diffs[i].value);
      } else if (diffs[i].removed) {
        analysis.deletions.push(diffs[i].value);
      }
    }

    return analysis;
  }

  classifyChanges(analysis) {
    const additionLines = analysis.additions.join('\n').split('\n').length;
    const deletionLines = analysis.deletions.join('\n').split('\n').length;
    const totalChanges = additionLines + deletionLines;

    if (totalChanges < 10) return 'patch';
    if (totalChanges < 50) return 'minor';
    return 'major';
  }

  calculateChangePercentage(analysis) {
    const totalLines = analysis.additions.length + analysis.deletions.length;
    return totalLines > 0 ? ((analysis.additions.length - analysis.deletions.length) / totalLines) * 100 : 0;
  }

  identifyAffectedSections(diffs) {
    const sections = [];
    let currentSection = null;

    diffs.forEach(diff => {
      if (diff.value.match(/^#+\s/)) {
        currentSection = diff.value.trim();
      }
      if ((diff.added || diff.removed) && currentSection) {
        if (!sections.includes(currentSection)) {
          sections.push(currentSection);
        }
      }
    });

    return sections;
  }

  detectAllChanges(sourceDir, baselineDir) {
    const changes = [];

    const sourceFiles = this.getMarkdownFiles(sourceDir);

    sourceFiles.forEach(file => {
      const relativePath = path.relative(sourceDir, file);
      const baselineFile = path.join(baselineDir, relativePath);

      if (fs.existsSync(baselineFile)) {
        const changeInfo = this.detectChanges(file, baselineFile);
        if (changeInfo.changes.length > 0) {
          changes.push(changeInfo);
        }
      } else {
        changes.push({
          file,
          changeType: 'new',
          status: 'new_file'
        });
      }
    });

    return {
      timestamp: new Date().toISOString(),
      totalFilesChanged: changes.length,
      changes: changes
    };
  }

  getMarkdownFiles(dir) {
    let files = [];

    const items = fs.readdirSync(dir);
    items.forEach(item => {
      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);

      if (stat.isDirectory()) {
        files = files.concat(this.getMarkdownFiles(fullPath));
      } else if (item.endsWith('.md')) {
        files.push(fullPath);
      }
    });

    return files;
  }

  generateChangeReport(changes) {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalChanges: changes.length,
        byType: { patch: 0, minor: 0, major: 0, new: 0 },
        affectedLanguages: []
      },
      changes: changes
    };

    changes.forEach(change => {
      if (change.changeType) {
        report.summary.byType[change.changeType]++;
      } else if (change.status === 'new_file') {
        report.summary.byType.new++;
      }
    });

    return report;
  }
}

module.exports = ChangeDetector;
```

### Step 2: Create Synchronization Dashboard

**Implement status tracking:**

```javascript
class SynchronizationDashboard {
  constructor() {
    this.syncData = {};
  }

  updateSyncStatus(document, language, status, percentage) {
    if (!this.syncData[document]) {
      this.syncData[document] = {};
    }

    this.syncData[document][language] = {
      status: status, // 'current', 'outdated', 'in-progress'
      percentage: percentage,
      lastUpdated: new Date().toISOString()
    };
  }

  generateDashboard() {
    const dashboard = {
      timestamp: new Date().toISOString(),
      overallStatus: this.calculateOverallStatus(),
      byDocument: {},
      byLanguage: {},
      alerts: this.generateAlerts()
    };

    // By document
    Object.entries(this.syncData).forEach(([doc, langs]) => {
      const stats = {
        total: Object.keys(langs).length,
        current: 0,
        outdated: 0,
        inProgress: 0
      };

      Object.values(langs).forEach(status => {
        if (status.status === 'current') stats.current++;
        if (status.status === 'outdated') stats.outdated++;
        if (status.status === 'in-progress') stats.inProgress++;
      });

      dashboard.byDocument[doc] = stats;
    });

    // By language
    const languages = new Set();
    Object.values(this.syncData).forEach(langs => {
      Object.keys(langs).forEach(lang => languages.add(lang));
    });

    languages.forEach(lang => {
      const stats = {
        total: 0,
        current: 0,
        outdated: 0,
        inProgress: 0
      };

      Object.values(this.syncData).forEach(docs => {
        if (docs[lang]) {
          stats.total++;
          if (docs[lang].status === 'current') stats.current++;
          if (docs[lang].status === 'outdated') stats.outdated++;
          if (docs[lang].status === 'in-progress') stats.inProgress++;
        }
      });

      dashboard.byLanguage[lang] = stats;
    });

    return dashboard;
  }

  calculateOverallStatus() {
    let total = 0;
    let current = 0;

    Object.values(this.syncData).forEach(langs => {
      Object.values(langs).forEach(status => {
        total++;
        if (status.status === 'current') current++;
      });
    });

    return {
      synchronizationPercentage: ((current / total) * 100).toFixed(1) + '%',
      outOfSync: total - current
    };
  }

  generateAlerts() {
    const alerts = [];

    Object.entries(this.syncData).forEach(([doc, langs]) => {
      Object.entries(langs).forEach(([lang, status]) => {
        if (status.status === 'outdated' && status.percentage < 50) {
          alerts.push({
            severity: 'critical',
            document: doc,
            language: lang,
            message: `${doc} in ${lang} is severely outdated (${status.percentage}%)`
          });
        }
      });
    });

    return alerts;
  }
}
```

## Translator Communication

### Step 1: Create Communication Template

**TRANSLATOR_UPDATE_NOTIFICATION.md:**

```markdown
# Translator Update Notification

Dear [Translator Name],

We have updates to the documentation that need translation.

## Summary

**Document**: [Document Name]
**Change Type**: ☐ Minor ☐ Moderate ☐ Major
**Impact**: Approximately [X]% of content changed
**Affected Sections**: [List sections]

## Change Details

### What Changed

[Description of changes]

### Why

[Reason for the changes]

### When

**Update Available**: [Date]
**Translator Deadline**: [Date]
**Release Target**: [Date]
**Days to Complete**: [X days]

## Resources Provided

- **Change Details**: [attached file]
- **Context Documentation**: [link]
- **Updated Glossary**: [link]
- **Examples**: [links if applicable]
- **Related Issues**: [issue numbers]

## Instructions

1. Review the attached change details
2. Read the context documentation
3. Check the updated glossary
4. Make necessary updates to translations
5. Perform self-review
6. Submit for QA

## Questions?

For questions or clarifications:
- **Contact**: [PM name] at [email]
- **Response Time**: Within 24 hours
- **Communication Channel**: [preferred method]

## Compensation

**Estimated Hours**: [estimated hours]
**Rate**: [rate if applicable]
**Payment Terms**: [terms]

Thank you for your prompt attention to this update!

Best regards,
[Project Manager Name]
```

### Step 2: Create Progress Tracking

**translator-progress.json:**

```json
{
  "updates": [
    {
      "updateId": "UPDATE-001",
      "document": "getting-started.md",
      "createdDate": "2024-01-15",
      "deadline": "2024-01-20",
      "languages": {
        "de": {
          "assignedTo": "translator-de@example.com",
          "status": "in-progress",
          "percentComplete": 75,
          "startedDate": "2024-01-15",
          "expectedCompletion": "2024-01-18"
        },
        "fr": {
          "assignedTo": "translator-fr@example.com",
          "status": "completed",
          "percentComplete": 100,
          "startedDate": "2024-01-15",
          "completedDate": "2024-01-17"
        },
        "ja": {
          "assignedTo": "translator-ja@example.com",
          "status": "not-started",
          "percentComplete": 0
        }
      }
    }
  ]
}
```

## Managing Incremental Updates

### Step 1: Create Update Batching Strategy

**UPDATE_BATCHING.md:**

```markdown
# Update Batching Strategy

## Batching Logic

### Batch Type 1: By Time
- Collect all changes for monthly cycle
- Process together for efficiency
- Reduces overhead of multiple submissions

### Batch Type 2: By Document
- Group all changes to single document
- Allows context consistency
- Easier for translator workflow

### Batch Type 3: By Change Type
- Group similar changes together
- Patch fixes processed separately
- Feature updates processed together

### Batch Type 4: By Urgency
- Critical changes processed immediately
- Routine changes batched
- Reduces context switching

## Recommended Strategy

**Default**: Monthly release cycle
- Collect changes during month
- Process all translations together
- Coordinate with product release
- Efficient use of resources

**Exception**: Critical changes
- Process immediately
- Separate from routine batches
- Notify users of critical updates
- Fast-track through QA

## Implementation

```
Week 1-3: Collect Changes
↓
End of Week 3: Analyze and Categorize
↓
Week 4: Assign to Translators
↓
Week 5-6: Translation Work
↓
Week 7: QA and Review
↓
Week 8: Release Coordination
↓
Release
```

## Change Threshold

**Include in Batch If:**
- > 5 strings changed
- >= 2 documents affected
- Affects > 1 section

**Handle Separately If:**
- Security issue or critical bug fix
- Breaking change
- Data loss risk
- Safety concern
```

### Step 2: Create Incremental Update Script

**scripts/manage-incremental-updates.js:**

```javascript
class IncrementalUpdateManager {
  constructor() {
    this.updates = [];
    this.batches = [];
  }

  addUpdate(update) {
    this.updates.push({
      id: this.generateId(),
      ...update,
      status: 'pending',
      createdDate: new Date().toISOString()
    });
  }

  createBatch(strategy = 'time') {
    const batch = {
      id: this.generateBatchId(),
      strategy: strategy,
      updates: [],
      languages: [],
      status: 'created',
      createdDate: new Date().toISOString()
    };

    switch (strategy) {
      case 'time':
        batch.updates = this.batchByTime();
        break;
      case 'document':
        batch.updates = this.batchByDocument();
        break;
      case 'change-type':
        batch.updates = this.batchByChangeType();
        break;
    }

    // Get all languages affected
    batch.languages = this.getAffectedLanguages(batch.updates);

    this.batches.push(batch);
    return batch;
  }

  batchByTime() {
    // Return updates from last X days
    const daysWindow = 30;
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysWindow);

    return this.updates.filter(u => new Date(u.createdDate) >= cutoffDate);
  }

  batchByDocument() {
    // Group updates by document
    const grouped = {};

    this.updates.forEach(update => {
      const doc = update.document;
      if (!grouped[doc]) {
        grouped[doc] = [];
      }
      grouped[doc].push(update);
    });

    return Object.values(grouped).flat();
  }

  batchByChangeType() {
    // Return highest priority changes first
    const priorityOrder = { critical: 0, major: 1, minor: 2, patch: 3 };

    return this.updates.sort((a, b) => {
      const priorityA = priorityOrder[a.changeType] || 999;
      const priorityB = priorityOrder[b.changeType] || 999;
      return priorityA - priorityB;
    });
  }

  getAffectedLanguages(updates) {
    const languages = new Set();

    updates.forEach(update => {
      if (update.affectedLanguages) {
        update.affectedLanguages.forEach(lang => languages.add(lang));
      }
    });

    return Array.from(languages);
  }

  assignBatchToTranslators(batchId, assignments) {
    const batch = this.batches.find(b => b.id === batchId);

    if (!batch) {
      throw new Error(`Batch ${batchId} not found`);
    }

    batch.assignments = assignments;
    batch.status = 'assigned';

    Object.entries(assignments).forEach(([language, translator]) => {
      // Create translator task
      this.createTranslatorTask(batch, language, translator);
    });

    return batch;
  }

  createTranslatorTask(batch, language, translator) {
    return {
      batchId: batch.id,
      language: language,
      assignedTo: translator,
      updates: batch.updates.filter(u => !u.affectedLanguages || u.affectedLanguages.includes(language)),
      status: 'assigned',
      deadline: this.calculateDeadline(batch),
      createdDate: new Date().toISOString()
    };
  }

  calculateDeadline(batch) {
    const baseDate = new Date();
    const estimatedDays = this.estimateWorkDays(batch);

    baseDate.setDate(baseDate.getDate() + estimatedDays);
    return baseDate.toISOString().split('T')[0];
  }

  estimateWorkDays(batch) {
    const avgStringsPerDay = 100; // Adjust based on experience
    const totalStrings = batch.updates.reduce((sum, u) => sum + (u.estimatedStrings || 10), 0);

    return Math.ceil(totalStrings / avgStringsPerDay);
  }

  generateBatchSummary(batchId) {
    const batch = this.batches.find(b => b.id === batchId);

    if (!batch) return null;

    return {
      batchId: batch.id,
      createdDate: batch.createdDate,
      strategy: batch.strategy,
      status: batch.status,
      totalUpdates: batch.updates.length,
      affectedLanguages: batch.languages,
      assignments: batch.assignments,
      estimatedCompletion: this.estimateCompletion(batch),
      totalStringsToTranslate: batch.updates.reduce((sum, u) => sum + (u.estimatedStrings || 10), 0)
    };
  }

  estimateCompletion(batch) {
    if (!batch.assignments) return null;

    const languages = Object.keys(batch.assignments);
    const earliest = languages.map(lang => {
      const task = this.createTranslatorTask(batch, lang, batch.assignments[lang]);
      return task.deadline;
    }).sort()[languages.length - 1]; // Get latest deadline

    return earliest;
  }

  generateId() {
    return `UPDATE-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  generateBatchId() {
    return `BATCH-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}

module.exports = IncrementalUpdateManager;
```

## Handling Deprecated Content

### Step 1: Create Deprecation Process

**DEPRECATION_PROCESS.md:**

```markdown
# Deprecation and Removal Process

## Deprecation Lifecycle

### Phase 1: Announcement (Week 1)
- Identify content to be deprecated
- Announce deprecation clearly
- Provide migration path
- Set sunset date (minimum 6 months)

### Phase 2: Migration (Weeks 2-20)
- Maintain full documentation
- Add deprecation warnings
- Provide replacement information
- Support users transitioning

### Phase 3: Sunset (Week 21+)
- Remove deprecated content
- Maintain redirects for 6 months
- Update all cross-references
- Release notes documenting removal

## Deprecation Markers

Add clear markers to deprecated content:

```markdown
> **DEPRECATED**: This feature is deprecated as of v2.0.
> It will be removed in v3.0 (Release Date: January 2025).
>
> **Migration**: Please see [New Feature Guide](../new-feature.md)
> for the recommended approach.
```

## Translation Updates

### For Deprecated Content

**Do Not Translate:**
- Minor UI text changes after deprecation announced
- Non-critical updates
- Cosmetic improvements

**Do Translate:**
- Major functionality changes affecting users
- Migration/upgrade instructions
- Critical bug fixes
- Security issues

### For Replacement Content

**Translate Immediately:**
- New replacement feature documentation
- Migration guides
- Updated API references

## Removal Process

When removing deprecated content:

1. Ensure all translations updated
2. Create redirect from old URL to new
3. Update all cross-references
4. Update table of contents
5. Update search indexes
6. Maintain removal in version history
7. Release notes document removal

## Translation Memory

For deprecated content:
- Keep in translation memory 12+ months
- Mark as "deprecated" in TM
- Don't reuse without review
- Maintain for reference
```

## Translation Memory and Reuse

### Step 1: Implement Translation Memory

**scripts/translation-memory.js:**

```javascript
class TranslationMemory {
  constructor() {
    this.entries = [];
  }

  addEntry(sourceText, targetText, language, context = '') {
    const entry = {
      id: this.generateId(),
      source: sourceText,
      target: targetText,
      language: language,
      context: context,
      addedDate: new Date().toISOString(),
      usage: 0,
      quality: 'new' // new, verified, excellent
    };

    this.entries.push(entry);
    return entry.id;
  }

  findMatches(sourceText, language, threshold = 0.8) {
    const matches = [];

    this.entries
      .filter(e => e.language === language)
      .forEach(entry => {
        const similarity = this.calculateSimilarity(sourceText, entry.source);

        if (similarity >= threshold) {
          matches.push({
            ...entry,
            matchPercentage: (similarity * 100).toFixed(1)
          });
        }
      });

    return matches.sort((a, b) => b.matchPercentage - a.matchPercentage);
  }

  findExactMatches(sourceText, language) {
    return this.entries.filter(
      e => e.language === language && e.source === sourceText
    );
  }

  calculateSimilarity(str1, str2) {
    // Implement similarity algorithm (e.g., Levenshtein distance)
    const longer = str1.length > str2.length ? str1 : str2;
    const shorter = str1.length > str2.length ? str2 : str1;

    if (longer.length === 0) return 1.0;

    const editDistance = this.getEditDistance(longer, shorter);
    return (longer.length - editDistance) / longer.length;
  }

  getEditDistance(s1, s2) {
    const matrix = [];

    for (let i = 0; i <= s2.length; i++) {
      matrix[i] = [i];
    }

    for (let j = 0; j <= s1.length; j++) {
      matrix[0][j] = j;
    }

    for (let i = 1; i <= s2.length; i++) {
      for (let j = 1; j <= s1.length; j++) {
        if (s2.charAt(i - 1) === s1.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          );
        }
      }
    }

    return matrix[s2.length][s1.length];
  }

  updateQuality(entryId, newQuality) {
    const entry = this.entries.find(e => e.id === entryId);
    if (entry) {
      entry.quality = newQuality;
    }
  }

  recordUsage(entryId) {
    const entry = this.entries.find(e => e.id === entryId);
    if (entry) {
      entry.usage++;
      entry.lastUsed = new Date().toISOString();
    }
  }

  generateReport() {
    return {
      timestamp: new Date().toISOString(),
      totalEntries: this.entries.length,
      byLanguage: this.groupByLanguage(),
      byQuality: this.groupByQuality(),
      mostUsed: this.getMostUsed(10),
      unused: this.getUnused()
    };
  }

  groupByLanguage() {
    const groups = {};

    this.entries.forEach(entry => {
      groups[entry.language] = (groups[entry.language] || 0) + 1;
    });

    return groups;
  }

  groupByQuality() {
    const groups = { new: 0, verified: 0, excellent: 0 };

    this.entries.forEach(entry => {
      groups[entry.quality]++;
    });

    return groups;
  }

  getMostUsed(count) {
    return this.entries
      .sort((a, b) => b.usage - a.usage)
      .slice(0, count);
  }

  getUnused() {
    return this.entries.filter(e => e.usage === 0);
  }

  generateId() {
    return `TM-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  exportForTranslator(language, context = null) {
    let filtered = this.entries.filter(e => e.language === language && e.quality === 'verified');

    if (context) {
      filtered = filtered.filter(e => e.context === context);
    }

    return filtered.map(e => ({
      source: e.source,
      target: e.target,
      context: e.context
    }));
  }
}

module.exports = TranslationMemory;
```

## Quality Maintenance

### Step 1: Establish Maintenance QA

**MAINTENANCE_QA.md:**

```markdown
# Quality Assurance for Updates

## QA Focus for Updates

When reviewing updated translations, focus on:

### Consistency with Previous Version
- ☐ Terminology unchanged (unless update requires change)
- ☐ Style consistent with existing content
- ☐ Formatting consistent
- ☐ Tone matches documentation

### Accuracy of Changes
- ☐ Changes match source document updates
- ☐ New terminology consistent with glossary
- ☐ Translations accurate
- ☐ Examples correct

### Completeness
- ☐ All changed sections translated
- ☐ No untranslated text
- ☐ All examples updated
- ☐ Links updated as needed

### Minimal Impact
- ☐ Unchanged sections not modified
- ☐ Only necessary changes made
- ☐ No formatting changes to unchanged sections
- ☐ File structure preserved

## QA Process for Updates

1. **Compare Versions**
   - Show old version and new version side-by-side
   - Highlight changed areas
   - Identify translator changes

2. **Validate Changes**
   - Verify translation of new content
   - Check consistency with surrounding text
   - Confirm accuracy of changes

3. **Check Integration**
   - Ensure changes integrate smoothly
   - Check cross-references updated
   - Verify related content consistent

4. **Final Verification**
   - Read in context
   - Test links and references
   - Verify all formatting correct
```

## Deprecation and Sunset Procedures

### Step 1: Create Sunset Planning

**SUNSET_PLANNING.md:**

```markdown
# Sunset and End-of-Life Process

## Content Sunset Timeline

### Months 1-3: Announcement
- Clearly mark as deprecated
- Announce in release notes
- Provide upgrade path
- Set sunset date

### Months 4-8: Transition
- Maintain documentation
- Support users transitioning
- Continue translations for updates
- Monitor adoption of replacement

### Months 9-12: Preparation
- Plan removal
- Prepare migration docs
- Update related content
- Finalize redirects

### Month 12+: Removal
- Remove deprecated content
- Activate redirects
- Archive translations
- Update search indexes
- Update documentation index

## Translation Considerations

### What to Translate for Sunset Content
- Deprecation notices
- Migration guides
- Replacement documentation
- Compatibility notes

### What Not to Translate
- Final removal (unless critical)
- Archival content
- Outdated examples

## Archival Process

1. Keep last translated version
2. Mark as archived in translation memory
3. Maintain in version control
4. Store documentation about deprecation
5. Maintain for 24 months minimum
6. Keep for historical reference

## User Communication

Notify users of deprecation in:
- Release notes (all languages)
- Documentation (top of deprecated section)
- API documentation
- Migration guides
- Email newsletter (if applicable)

Timeline:
- Initial announcement: 6 months before removal
- Final notice: 2 weeks before removal
- Removal date clearly marked
```

## Conclusion

Maintaining multilingual documentation requires:

1. **Systematic Updates** - Organized processes and workflows
2. **Version Control** - Clear tracking of synchronization status
3. **Efficient Communication** - Regular, clear translator communication
4. **Quality Standards** - Apply same QA standards to updates
5. **Translation Reuse** - Leverage translation memory effectively
6. **Change Management** - Structured approach to content changes
7. **User Communication** - Keep users informed of updates
8. **Scalability** - Processes that work as documentation grows

Regular maintenance ensures translations stay current, accurate, and valuable to users in all languages. Establish routines and monitor metrics to maintain multilingual documentation quality over the long term.

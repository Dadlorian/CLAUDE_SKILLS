# Automating Changelogs: GitHub Actions, Conventional Commits

## Table of Contents
- [Introduction](#introduction)
- [Conventional Commits Standard](#conventional-commits-standard)
- [Automated Changelog Generation](#automated-changelog-generation)
- [GitHub Actions Setup](#github-actions-setup)
- [Tools and Frameworks](#tools-and-frameworks)
- [Integration Patterns](#integration-patterns)
- [Templates](#templates)
- [Examples](#examples)

## Introduction

Manual changelog management is time-consuming and error-prone. Automation eliminates repetition, ensures consistency, and captures the complete history of changes automatically.

### Benefits of Automation

- **Consistency**: Same format for every release
- **Accuracy**: No forgotten changes
- **Efficiency**: Saves hours per release
- **Traceability**: Links commits to features
- **Audit Trail**: Complete change history
- **Reduced Friction**: Less manual work
- **Better Quality**: More detailed information

### How It Works

```
Developer writes commit → Follows Conventional Commits
                                ↓
Git hook validates → Commit follows standard
                                ↓
CI/CD Pipeline runs → Extracts commit messages
                                ↓
Changelog Generator → Organizes by type/feature
                                ↓
Release Notes created → Automatically formatted
                                ↓
Published → Website, GitHub releases, emails
```

## Conventional Commits Standard

### What Is Conventional Commits?

Conventional Commits is a specification for structured commit messages that enable automated changelog generation.

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

```
feat:       A new feature
fix:        A bug fix
docs:       Documentation only changes
style:      Changes that don't affect code meaning (spacing, etc.)
refactor:   Code change that neither fixes bug nor adds feature
perf:       Performance improvement
test:       Adding or updating tests
chore:      Changes to build system, dependencies, or tools
ci:         Changes to CI/CD configuration
revert:     Revert a previous commit
```

### Examples

**Simple Feature**:
```
feat: add dark mode toggle to settings
```

**Feature with Scope**:
```
feat(auth): implement OAuth 2.0 integration
```

**Bug Fix**:
```
fix(dashboard): correct timezone display for user reports
```

**Breaking Change**:
```
feat!(api): restructure response format

BREAKING CHANGE: Response format now wraps data in "data" field
```

**Complex Commit**:
```
feat(payment): add PayPal integration

- Add PayPal SDK to dependencies
- Create PaymentProvider abstraction
- Implement PayPal checkout flow
- Add unit tests

Fixes #1234
Related: #5678
```

### Breaking Changes in Conventional Commits

Mark breaking changes with `!` or in footer:

```
feat!: redesign API response structure

BREAKING CHANGE: The /api/users endpoint response now includes
metadata. Old format: {...}. New format: {data: {...}, meta: {...}}

Migration guide: https://docs.example.com/v1-to-v2
```

### Best Practices

1. **Use Lowercase**: Easier to parse and consistent
2. **Be Descriptive**: Enough context in subject line
3. **Use Active Voice**: "add feature" not "feature added"
4. **Reference Issues**: "Fixes #123" in commit
5. **Keep Scope Specific**: "auth" not "security" or "auth-system"
6. **One Logical Change**: Per commit when possible
7. **Meaningful Description**: Not "fixes stuff"

### Common Mistakes to Avoid

```
❌ "fixed bugs" - Too vague
✅ "fix(auth): resolve token expiration issue"

❌ "feat: did stuff" - Not descriptive
✅ "feat(search): add date range filter"

❌ "FEATURE: major redesign" - Wrong format
✅ "feat!: redesign dashboard UI"

❌ "chore: update packages" - No scope
✅ "chore(deps): update lodash to 4.17.21"

❌ "Random commit message" - Not conventional
✅ "fix(payment): handle PayPal API errors"
```

## Automated Changelog Generation

### How It Works

1. **Extract**: Pull all commits since last release
2. **Parse**: Parse conventional commit format
3. **Categorize**: Group by type (feat, fix, etc.)
4. **Organize**: Sort within categories
5. **Format**: Apply template and styling
6. **Generate**: Create CHANGELOG.md or release notes
7. **Publish**: Deploy to website, GitHub, email

### What Gets Generated

```markdown
# Changelog

## [5.2.0] - 2024-11-15

### Features
- Add dark mode support
- Implement OAuth 2.0 authentication
- Add export to PDF functionality

### Bug Fixes
- Fix timezone display in reports
- Correct CSV import encoding
- Resolve mobile layout issues

### Performance Improvements
- Optimize database queries (50% faster)
- Reduce bundle size by 30%
- Improve page load time

### Breaking Changes
- Remove legacy API v1 endpoints
- Restructure response format (migration guide required)
```

### Tools for Automation

**JavaScript/Node**:
- `semantic-release`: Full automation (commit → version → release)
- `conventional-changelog`: Generate changelogs
- `commitizen`: Interactive commit prompt

**Ruby**:
- `conventional_changelog`: Parse and generate changelogs
- `git-changelog`: Create changelogs from git history

**Python**:
- `python-semantic-release`: Automate versioning and releases
- `auto-changelog`: Generate from commit messages

**Go**:
- `git-chglog`: Create changelogs from git history

**General**:
- GitHub Actions: Automate with provided tools

## GitHub Actions Setup

### Basic Changelog Generation Workflow

```yaml
# .github/workflows/release.yml

name: Release

on:
  push:
    branches:
      - main
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for changelog

      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm install

      - name: Generate changelog
        uses: TriPSs/conventional-changelog-action@v3
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          git-commit-message: 'chore: update changelog'
          release-count: 0

      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body_path: CHANGELOG.md
```

### Full Semantic Release Workflow

```yaml
# .github/workflows/semantic-release.yml

name: Semantic Release

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
          persist-credentials: false

      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Run semantic-release
        uses: cycjimmy/semantic-release-action@v3
        with:
          semantic_version: 19.0.5
          extra_plugins: |
            @semantic-release/changelog
            @semantic-release/git
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### Changelog Generation on Tags

```yaml
# .github/workflows/changelog-on-tag.yml

name: Generate Changelog on Tag

on:
  push:
    tags:
      - 'v*'

jobs:
  changelog:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install conventional-changelog-cli
        run: npm install -g conventional-changelog-cli

      - name: Generate changelog
        run: |
          conventional-changelog -p angular -i CHANGELOG.md -s -r 0

      - name: Commit changelog
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add CHANGELOG.md
          git commit -m "docs: update changelog for ${{ github.ref }}" || true

      - name: Push changes
        uses: ad-m/github-push-action@master
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          branch: ${{ github.ref }}
```

## Tools and Frameworks

### semantic-release

Complete automation of versioning and releases.

**Features**:
- Analyzes commits to determine version bump
- Generates changelogs
- Publishes to npm, GitHub, etc.
- Creates GitHub releases
- Updates package.json

**Configuration**:
```js
// .releaserc.js
module.exports = {
  branches: ['main', 'next'],
  plugins: [
    '@semantic-release/commit-analyzer',
    '@semantic-release/release-notes-generator',
    '@semantic-release/changelog',
    '@semantic-release/npm',
    '@semantic-release/github',
    '@semantic-release/git'
  ]
};
```

### conventional-changelog

Generate changelogs from commits.

**Installation**:
```bash
npm install -g conventional-changelog-cli
```

**Usage**:
```bash
# Generate full changelog
conventional-changelog -p angular -i CHANGELOG.md -s -r 0

# Append to existing changelog
conventional-changelog -p angular -i CHANGELOG.md -s
```

### commitizen

Interactive commit message creation.

**Installation**:
```bash
npm install -g commitizen
npm install --save-dev cz-conventional-changelog
```

**Configuration**:
```json
{
  "commitizen": {
    "path": "./node_modules/cz-conventional-changelog"
  }
}
```

**Usage**:
```bash
# Interactive commit
git cz

# Or traditional git commit
git commit -m "feat: description"
```

### git-cliff

Changelog generator in Rust, very fast.

**Installation**:
```bash
brew install git-cliff
# or: cargo install git-cliff
```

**Configuration**:
```toml
# cliff.toml
[changelog]
trim = true

[[changelog.split]]
message_pattern = "^feat"
group_title = "Features"

[[changelog.split]]
message_pattern = "^fix"
group_title = "Bug Fixes"

[[changelog.split]]
message_pattern = "^perf"
group_title = "Performance"
```

**Usage**:
```bash
git cliff > CHANGELOG.md
git cliff --latest > latest.md
```

## Integration Patterns

### Pattern 1: Manual Release with Automated Changelog

**Workflow**:
1. Developer tags release: `git tag -a v1.2.0`
2. GitHub Actions triggered by tag
3. Changelog generated automatically
4. Release notes created
5. Deployed to website

**Setup**:
```bash
# On release day
git tag -a v1.2.0 -m "Release 1.2.0"
git push --tags
# GitHub Actions handles rest
```

### Pattern 2: Fully Automated Semantic Release

**Workflow**:
1. Developers commit with conventional format
2. Merge to main branch
3. GitHub Actions analyzes commits
4. Version auto-bumped
5. Changelog generated
6. Package published
7. GitHub release created

**Setup**:
```bash
npm install semantic-release
npx semantic-release
# Then configure CI/CD to run on main branch
```

### Pattern 3: Scheduled Changelog Updates

**Workflow**:
1. On schedule (weekly, monthly)
2. Fetch recent commits
3. Update CHANGELOG.md
4. Create pull request
5. Reviewer approves
6. Auto-merges

**Configuration**:
```yaml
# .github/workflows/weekly-changelog.yml
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: |
          conventional-changelog -p angular -i CHANGELOG.md -s
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v4
        with:
          commit-message: 'docs: update changelog'
          title: 'docs: weekly changelog update'
          body: 'Automated changelog update'
```

### Pattern 4: Custom Changelog with Templates

**Workflow**:
1. Parse commits
2. Apply custom template
3. Generate formatted output
4. Post to multiple channels

**Node.js Script**:
```javascript
// scripts/generate-changelog.js
const { execSync } = require('child_process');
const fs = require('fs');
const Handlebars = require('handlebars');

const getCommits = () => {
  const output = execSync(
    'git log --format=%B%n---END--- v1.0.0..HEAD'
  ).toString();

  return parseCommits(output);
};

const parseCommits = (output) => {
  const commits = [];
  const entries = output.split('---END---').filter(e => e.trim());

  entries.forEach(entry => {
    const match = entry.match(
      /^(feat|fix|docs|perf)(?:\((.+?)\))?!?:\s(.+)/
    );

    if (match) {
      commits.push({
        type: match[1],
        scope: match[2] || 'general',
        message: match[3]
      });
    }
  });

  return commits;
};

const generateChangelog = (commits) => {
  const template = fs.readFileSync(
    'changelog.template.hbs',
    'utf-8'
  );
  const hbs = Handlebars.compile(template);

  const grouped = {
    features: commits.filter(c => c.type === 'feat'),
    fixes: commits.filter(c => c.type === 'fix'),
    docs: commits.filter(c => c.type === 'docs'),
    performance: commits.filter(c => c.type === 'perf')
  };

  return hbs(grouped);
};

const commits = getCommits();
const changelog = generateChangelog(commits);
fs.writeFileSync('CHANGELOG.md', changelog);

console.log('Changelog generated');
```

## Templates

### Conventional Commit Hook Template

```bash
#!/bin/bash
# .husky/commit-msg

npx commitlint --edit "$1"
```

### Changelog Template (Handlebars)

```handlebars
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

{{#if unreleased.features}}
### Added
{{#each unreleased.features}}
- {{this.message}}{{#if this.scope}} ({{this.scope}}){{/if}}
{{/each}}
{{/if}}

{{#each releases}}
## [{{this.version}}] - {{this.date}}

{{#if this.breaking}}
### ⚠️  BREAKING CHANGES
{{#each this.breaking}}
- {{this.message}}
{{/each}}
{{/if}}

{{#if this.features}}
### Added
{{#each this.features}}
- {{this.message}}{{#if this.scope}} ({{this.scope}}){{/if}}
{{/each}}
{{/if}}

{{#if this.fixes}}
### Fixed
{{#each this.fixes}}
- {{this.message}}{{#if this.scope}} ({{this.scope}}){{/if}}
{{/each}}
{{/if}}

{{#if this.performance}}
### Performance
{{#each this.performance}}
- {{this.message}}{{#if this.scope}} ({{this.scope}}){{/if}}
{{/each}}
{{/if}}

{{/each}}
```

### GitHub Actions Workflow Template

```yaml
name: Automated Changelog

on:
  push:
    branches: [main]
    tags: ['v*']
  workflow_dispatch:

jobs:
  changelog:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write

    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: npm

      - run: npm ci

      - name: Generate changelog
        run: npm run changelog

      - name: Commit if changed
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add CHANGELOG.md
          git commit -m "docs: update changelog" || true
          git push
```

## Examples

### Example 1: Angular Conventional Commits Project

**Project Structure**:
```
my-project/
├── .github/
│   └── workflows/
│       └── release.yml
├── .commitlintrc.json
├── .releaserc.json
├── package.json
├── CHANGELOG.md
└── src/
```

**commitlintrc.json**:
```json
{
  "extends": ["@commitlint/config-conventional"]
}
```

**.releaserc.json**:
```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    "@semantic-release/npm",
    "@semantic-release/github",
    "@semantic-release/git"
  ]
}
```

**Workflow**:
```bash
# Developer creates feature
git checkout -b feat/dark-mode

# Make changes
vim src/theme.js

# Commit with conventional format
git commit -m "feat: add dark mode support"

# Push and create PR
git push origin feat/dark-mode

# After PR approval and merge to main
# GitHub Actions automatically:
# 1. Detects conventional commits
# 2. Bumps version (v1.2.0 -> v1.3.0)
# 3. Generates changelog entry
# 4. Creates GitHub release
# 5. Publishes to npm
```

**Generated Changelog Entry**:
```markdown
## [1.3.0] - 2024-11-15

### Features
- add dark mode support
```

### Example 2: Python Project with git-cliff

**Configuration** (pyproject.toml):
```toml
[tool.git-cliff.changelog]
# Remove duplicate entries
trim = true

[[tool.git-cliff.git.split_commits]]
message = "^feat"
group = "Features"

[[tool.git-cliff.git.split_commits]]
message = "^fix"
group = "Bug Fixes"

[[tool.git-cliff.git.split_commits]]
message = "^perf"
group = "Performance"

[[tool.git-cliff.git.split_commits]]
message = "^docs"
group = "Documentation"

[tool.git-cliff.git]
# Parse conventional commits
conventional_commits = true
filter_unconventional = false
```

**GitHub Actions**:
```yaml
name: Changelog

on:
  push:
    tags: ['v*']

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - uses: kenji-miyake/setup-git-cliff@v0.1.0

      - run: git-cliff > CHANGELOG.md

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          body_path: CHANGELOG.md
```

**Commits**:
```bash
git commit -m "feat(auth): add OAuth2 support"
git commit -m "fix(api): handle connection timeouts"
git commit -m "perf(db): optimize query performance"
git commit -m "docs: update README with examples"
```

**Generated Changelog**:
```markdown
## [Unreleased]

### Features
- auth: add OAuth2 support

### Bug Fixes
- api: handle connection timeouts

### Performance
- db: optimize query performance

### Documentation
- update README with examples
```

### Example 3: Custom Changelog Generator

**Node.js Script**:
```javascript
// scripts/changelog.js
const { execSync } = require('child_process');
const fs = require('fs');

function generateChangelog() {
  // Get commits since last tag
  const lastTag = execSync('git describe --tags --abbrev=0')
    .toString().trim();

  const commits = execSync(
    `git log ${lastTag}..HEAD --format=%B%n---COMMIT---`
  ).toString();

  // Parse commits
  const entries = {
    features: [],
    fixes: [],
    breaks: [],
    other: []
  };

  commits.split('---COMMIT---').forEach(commit => {
    const match = commit.match(/^(feat|fix|docs|chore)(?:\(([^)]+)\))?!?:\s(.+)/m);
    if (!match) return;

    const [, type, scope, message] = match;
    const item = `${message}${scope ? ` (${scope})` : ''}`;

    switch(type) {
      case 'feat': entries.features.push(item); break;
      case 'fix': entries.fixes.push(item); break;
      case 'chore': entries.other.push(item); break;
    }

    if (commit.includes('BREAKING CHANGE')) {
      entries.breaks.push(item);
    }
  });

  // Build changelog
  let output = '# Changelog\n\n';

  const now = new Date().toISOString().split('T')[0];
  output += `## [${getNextVersion()}] - ${now}\n\n`;

  if (entries.breaks.length > 0) {
    output += '### ⚠️  BREAKING CHANGES\n';
    entries.breaks.forEach(item => output += `- ${item}\n`);
    output += '\n';
  }

  if (entries.features.length > 0) {
    output += '### Features\n';
    entries.features.forEach(item => output += `- ${item}\n`);
    output += '\n';
  }

  if (entries.fixes.length > 0) {
    output += '### Bug Fixes\n';
    entries.fixes.forEach(item => output += `- ${item}\n`);
    output += '\n';
  }

  // Append existing changelog
  const existing = fs.existsSync('CHANGELOG.md')
    ? fs.readFileSync('CHANGELOG.md', 'utf-8')
    : '';

  output += existing;
  fs.writeFileSync('CHANGELOG.md', output);

  console.log('✓ Changelog generated');
}

function getNextVersion() {
  const pkg = JSON.parse(fs.readFileSync('package.json', 'utf-8'));
  const [major, minor, patch] = pkg.version.split('.').map(Number);
  return `${major}.${minor}.${patch + 1}`;
}

generateChangelog();
```

**Usage**:
```bash
npm run changelog
```

## Best Practices

1. **Enforce Conventional Commits**
   - Use commitlint in pre-commit hooks
   - Fail CI/CD if non-compliant
   - Educate team on format

2. **Keep Commits Atomic**
   - One logical change per commit
   - Makes changelog more meaningful
   - Easier to revert if needed

3. **Review Before Release**
   - Even automated changelogs should be reviewed
   - Check for formatting issues
   - Add important context if needed

4. **Version Correctly**
   - MAJOR.MINOR.PATCH
   - Major: Breaking changes
   - Minor: New features
   - Patch: Bug fixes

5. **Test Automation**
   - Test changelog generation in CI
   - Verify on pull requests
   - Catch issues early

6. **Maintain Consistency**
   - Same format for all entries
   - Consistent terminology
   - Clear categorization

## Conclusion

Automating changelog generation through conventional commits and CI/CD pipelines:
- Eliminates manual work
- Ensures consistency
- Provides complete history
- Reduces errors
- Improves team efficiency

Invest time in setup once, reap benefits forever.

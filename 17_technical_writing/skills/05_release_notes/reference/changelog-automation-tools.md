# Changelog Automation Tools Reference

## Overview

Modern release management tools automate version bumping, changelog generation, and release creation. This reference covers popular tools and their features.

## 1. Semantic Release

### Overview
Fully automated versioning and package publishing based on semantic versioning and conventional commits.

**Repository:** https://github.com/semantic-release/semantic-release

### Key Features
- Fully automated version bumping (MAJOR.MINOR.PATCH)
- Automatic changelog generation
- Automatic GitHub/GitLab release creation
- Automatic package publishing (npm, PyPI, etc.)
- Plugin ecosystem for customization
- Works with conventional commits

### Installation
```bash
npm install --save-dev semantic-release
npm install --save-dev @semantic-release/github @semantic-release/changelog @semantic-release/git
```

### Configuration
```javascript
// release.config.js
module.exports = {
  branches: ['main', { name: 'beta', prerelease: true }],
  plugins: [
    '@semantic-release/commit-analyzer',
    '@semantic-release/release-notes-generator',
    '@semantic-release/changelog',
    '@semantic-release/npm',
    '@semantic-release/github',
    '@semantic-release/git',
  ],
};
```

### GitHub Actions Workflow
```yaml
name: Release
on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: 18
      - run: npm ci
      - run: npm run build
      - run: npm test
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### Commit Examples for Automation
```
feat: add login page       → v1.1.0 (minor bump)
fix: resolve login bug      → v1.0.1 (patch bump)
feat!: redesign API         → v2.0.0 (major bump)
```

### Advantages
- Completely automated
- Eliminates version number guessing
- Enforces conventional commits
- Multi-platform support
- Highly customizable
- Excellent documentation

### Disadvantages
- Requires CI/CD setup
- Opinionated about workflow
- Needs specific commit format
- Setup can be complex

### Best For
- NPM packages
- Open source projects
- Strict versioning requirements
- Automated release pipelines

---

## 2. Release Drafter

### Overview
Drafts release notes from pull request titles and labels automatically. Creates draft releases on GitHub.

**Repository:** https://github.com/release-drafter/release-drafter

### Key Features
- Automatic release note draft creation
- Groups PRs by label (features, bugs, etc.)
- Pre-fills version number suggestion
- Customizable templates
- Works with GitHub only
- Manual publication step

### Installation
GitHub App: https://github.com/apps/release-drafter

### Configuration
```yaml
# .github/release-drafter.yml
name-template: 'v$RESOLVED_VERSION'
tag-template: 'v$RESOLVED_VERSION'
categories:
  - title: 'Features'
    labels:
      - 'type: feature'
      - 'type: enhancement'
  - title: 'Bug Fixes'
    labels:
      - 'type: bug'
  - title: 'Improvements'
    labels:
      - 'type: improvement'
  - title: 'Documentation'
    labels:
      - 'type: docs'
change-template: '- $TITLE (@$AUTHOR) in #$NUMBER'
template: |
  ## Changes

  $CHANGES
```

### GitHub Actions Integration
```yaml
name: Release Drafter
on:
  push:
    branches:
      - main
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  update_release_draft:
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v5
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Label Configuration
```yaml
# Use these labels on PRs for categorization
labels:
  - type: feature    # New features
  - type: bug        # Bug fixes
  - type: docs       # Documentation
  - type: improvement # Improvements
  - type: breaking   # Breaking changes
```

### Advantages
- Easy to set up
- GitHub native
- No code changes required
- Good for teams
- Manual control over publishing

### Disadvantages
- GitHub only
- Manual publishing step
- Less automation than semantic-release
- Requires PR labeling discipline

### Best For
- GitHub-hosted projects
- Teams that want some manual control
- Projects with varied commit standards
- Non-NPM projects

---

## 3. Auto

### Overview
Powerful automation tool for versioning, changelog generation, and package publishing.

**Repository:** https://github.com/intuit/auto

### Key Features
- Automated versioning from labels
- Multi-platform support (GitHub, GitLab)
- Custom release hooks
- Plugin system
- Can trigger without CI integration
- Great for monorepos

### Installation
```bash
npm install -g auto
# or
yarn add -D auto
```

### Configuration
```json
{
  "packages": [".", "packages/*"],
  "plugins": [
    "npm",
    ["git", { "baseBranch": "main" }],
    "github"
  ],
  "labels": {
    "Version: Major": { "releaseType": "major" },
    "Version: Minor": { "releaseType": "minor" },
    "Version: Patch": { "releaseType": "patch" }
  }
}
```

### GitHub Actions Workflow
```yaml
name: Release
on:
  push:
    branches:
      - main

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm install
      - run: npm test
      - run: npx auto shipit
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Commands
```bash
auto create-labels    # Create labels on repository
auto label            # Label the PR
auto changelog        # Generate changelog
auto bump             # Bump version
auto publish          # Publish package
auto shipit           # Full pipeline
```

### Advantages
- Multi-platform (GitHub, GitLab)
- Monorepo support
- Label-based versioning
- Flexible plugins
- Good documentation

### Disadvantages
- Smaller community
- Learning curve
- Complex configuration
- Label management required

### Best For
- Monorepos
- Multi-platform projects
- Label-based workflows
- Custom automation needs

---

## 4. Standard Version

### Overview
Follows Conventional Commits spec to automatically version and generate changelogs.

**Repository:** https://github.com/conventional-changelog/standard-version

### Key Features
- Semantic versioning automation
- Automatic changelog generation
- Git tag creation
- Conventional commits analysis
- Lightweight and simple
- Can be run locally or in CI

### Installation
```bash
npm install --save-dev standard-version
```

### Configuration
```json
{
  "scripts": {
    "release": "standard-version",
    "release:minor": "standard-version --release-as minor",
    "release:patch": "standard-version --release-as patch",
    "release:major": "standard-version --release-as major"
  }
}
```

### Usage
```bash
# Generate changelog and bump version
npm run release

# Pre-release
npm run release -- --prerelease alpha
npm run release -- --prerelease rc

# Manual version
npm run release -- --release-as 2.0.0

# Dry run
npm run release -- --dry-run
```

### Example Workflow
```bash
# Make commits with conventional format
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"

# Run standard-version
npm run release
# Creates/updates CHANGELOG.md
# Bumps version in package.json
# Creates git tag v1.1.0
# Stage these changes

# Review and push
git push --follow-tags origin main
```

### Configuration File
```javascript
// .versionrc.json
{
  "types": [
    { "type": "feat", "section": "Features" },
    { "type": "fix", "section": "Bug Fixes" },
    { "type": "docs", "section": "Documentation" }
  ],
  "commitUrlFormat": "https://github.com/user/repo/commits/{{hash}}",
  "compareUrlFormat": "https://github.com/user/repo/compare/{{previousTag}}...{{currentTag}}"
}
```

### Advantages
- Simple and lightweight
- No external services needed
- Can run locally
- Follows conventional commits
- Easy to integrate

### Disadvantages
- Manual step in CI/CD
- Doesn't auto-publish to npm
- Limited to changelog/versioning
- Smaller feature set

### Best For
- Simple projects
- Local development workflows
- Teams new to automation
- Lightweight solutions

---

## 5. Commitizen

### Overview
Interactive command line tool for creating conventional commit messages.

**Repository:** https://github.com/commitizen/cz-cli

### Key Features
- Interactive commit prompt
- Enforces conventional commits
- Changelog generation (with adapters)
- Customizable templates
- Works with all git projects

### Installation
```bash
npm install -g commitizen
npm install --save-dev cz-conventional-changelog
```

### Configuration
```json
{
  "scripts": {
    "commit": "cz"
  },
  "commitizen": {
    "path": "cz-conventional-changelog"
  }
}
```

### Usage
```bash
# Interactive commit
npm run commit
# or globally
cz commit

# or use git commit if configured with git-cz
git cz
```

### Interactive Prompt
```
? Select the type of change that you're committing:
> feat:     A new feature
  fix:      A bug fix
  docs:     Documentation only changes
  style:    Changes that don't affect code meaning
  refactor: A code change that neither fixes a bug nor adds a feature
  perf:     A code change that improves performance

? What is the scope of this change?
> auth

? Write a short, imperative tense description of the change:
> add login functionality

? Provide a longer description of the change:
> (press enter to skip)

? Are there any breaking changes?
> No

? Does this change affect any open issues?
> Closes #123
```

### Git Hooks Integration
```bash
npm install --save-dev husky @commitlint/cli
npx husky install
npx husky add .husky/commit-msg 'npx commitlint --edit "$1"'
```

### Advantages
- Enforces standards
- User-friendly
- Prevents bad commits
- Works standalone
- Widely adopted

### Disadvantages
- Manual process
- Requires discipline
- Not fully automated
- Best with other tools

### Best For
- Team standardization
- Preventing bad commits
- Combined with other tools
- Training new developers

---

## 6. Conventional Changelog

### Overview
Generates changelog from conventional commits and git history.

**Repository:** https://github.com/conventional-changelog/conventional-changelog

### Key Features
- Automatic changelog generation
- Conventional commits support
- Customizable templates
- Git history analysis
- Works with existing tools

### Installation
```bash
npm install --save-dev conventional-changelog-cli
```

### Configuration
```bash
# Generate initial changelog
npx conventional-changelog -p angular -i CHANGELOG.md -s

# Add to package.json
{
  "scripts": {
    "changelog": "conventional-changelog -p angular -i CHANGELOG.md -s"
  }
}
```

### Output Example
```markdown
# [1.1.0](https://github.com/user/repo/compare/v1.0.0...v1.1.0) (2024-01-15)

### Features
- add user authentication ([abc123](https://github.com/user/repo/commit/abc123))
- add password reset ([def456](https://github.com/user/repo/commit/def456))

### Bug Fixes
- fix login redirect ([ghi789](https://github.com/user/repo/commit/ghi789))
```

### Advantages
- Standalone tool
- Customizable output
- Well-documented
- Used by many projects

### Disadvantages
- Doesn't bump version
- Doesn't publish
- Additional tools needed
- Manual workflow

### Best For
- Documentation generation
- Component of larger pipeline
- Custom changelog formats
- Integration with other tools

---

## 7. Changelogithub

### Overview
Simple GitHub-native changelog generation from releases and pull requests.

**Repository:** https://github.com/Jaid/changelogithub

### Key Features
- GitHub releases based
- No configuration needed
- Simple setup
- GitHub-only
- Markdown output

### Installation
```bash
npx changelogithub
```

### GitHub Actions
```yaml
- name: Generate changelog
  uses: Jaid/changelogithub@v1
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Advantages
- Minimal setup
- No configuration
- GitHub native

### Disadvantages
- GitHub only
- Limited customization
- Basic features

### Best For
- Simple GitHub projects
- Quick setup
- Minimal configuration

---

## 8. Lerna with Conventional Commits

### Overview
Tool for managing JavaScript monorepos with automatic versioning and publishing.

**Repository:** https://github.com/lerna/lerna

### Key Features
- Monorepo management
- Conventional commits support
- Automatic changelog
- Independent versioning per package
- Batch publishing

### Installation
```bash
npm install -g lerna
lerna init
```

### Configuration
```json
{
  "packages": ["packages/*"],
  "version": "independent",
  "command": {
    "publish": {
      "conventionalCommits": true,
      "createRelease": "github"
    }
  }
}
```

### Commands
```bash
lerna version              # Bump versions
lerna publish              # Publish packages
lerna version --no-push    # Version without pushing
```

### Advantages
- Purpose-built for monorepos
- Powerful versioning
- Great documentation
- Widely used

### Disadvantages
- Monorepo only
- More complex
- Learning curve

### Best For
- JavaScript monorepos
- Multi-package projects
- Babel, React, Angular style projects

---

## Comparison Table

| Tool | Type | Automation | Setup | Multi-repo | Best For |
|------|------|-----------|-------|-----------|----------|
| semantic-release | Full | Complete | Medium | No | NPM packages |
| release-drafter | Draft | Partial | Easy | No | GitHub teams |
| auto | Full | Complete | Medium | Yes | Monorepos |
| standard-version | Version | Semi | Easy | No | Simple projects |
| commitizen | Commit | Helper | Easy | Yes | Team standards |
| conventional-changelog | Docs | Changelog | Medium | Yes | Documentation |
| changelogithub | Docs | Changelog | Very Easy | No | Simple projects |
| lerna | Full | Complete | Hard | Yes | JS monorepos |

---

## Tool Selection Guide

### Choose Semantic Release If:
- Publishing to npm
- Want full automation
- Using conventional commits
- CI/CD pipeline available
- Monorepo not needed

### Choose Release Drafter If:
- Using GitHub
- Want manual control
- PR labeling already done
- Team coordination needed
- Simple setup preferred

### Choose Auto If:
- Managing monorepo
- Multi-platform needed
- Custom workflows required
- Label-based versioning
- Maximum flexibility needed

### Choose Standard Version If:
- Simple project
- Lightweight solution
- Local or CI workflow
- Conventional commits
- No npm publishing

### Choose Commitizen If:
- Team standardization
- Preventing bad commits
- Training team members
- Enforcing standards
- As part of larger pipeline

---

## Integration Strategy

### Recommended Stack
```
Commitizen (commit format)
  ↓
Commitlint + Husky (enforce format)
  ↓
Conventional Changelog (generate docs)
  ↓
semantic-release or auto (full automation)
  ↓
GitHub Releases + npm publish
```

### Example Full Pipeline
```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: npm install
      - run: npm run lint
      - run: npm test

  release:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: npm install
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

---

## Summary

Modern changelog automation eliminates manual work and enforces standards. Choose tools based on:

1. **Automation level:** How much should be automated?
2. **Platform:** GitHub, GitLab, or multi-platform?
3. **Project type:** Monorepo, package, or application?
4. **Team workflow:** Manual, semi-auto, or fully automatic?
5. **Integration:** Existing tools and CI/CD pipeline?

Combine tools for maximum effectiveness. Most projects benefit from Commitizen + semantic-release or Commitizen + Release Drafter.

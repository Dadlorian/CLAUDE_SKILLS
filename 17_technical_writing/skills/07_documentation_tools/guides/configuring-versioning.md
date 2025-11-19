# Multi-Version Documentation Configuration Guide

## Overview

Versioning allows you to maintain and display multiple versions of your documentation. This is essential for projects that support multiple release versions and need to provide documentation matching each version's features.

## Prerequisites

- Docusaurus project already set up
- Understanding of your project's versioning strategy
- Git repository with tags or branches for versions
- Access to docusaurus.config.js

## Part 1: Understanding Docusaurus Versioning

### What is Versioning?

Versioning allows you to:
- Maintain separate documentation for different product versions
- Switch between versions in the UI
- Keep historical documentation accessible
- Serve version-specific URLs
- Support multiple documentation snapshots

### Version Structure

```
versioned_docs/
├── version-1.0/
│   ├── intro.md
│   ├── getting-started.md
│   └── api/
├── version-2.0/
│   ├── intro.md
│   ├── getting-started.md
│   └── api/
docs/                    # Next/upcoming version
├── intro.md
├── getting-started.md
└── api/

versions.json           # Version metadata
```

## Part 2: Enabling Versioning

### Step 1: Enable Versioning in Configuration

Update `docusaurus.config.js`:

```javascript
module.exports = {
  // ... other config
  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          lastVersion: 'current',
          versions: {
            current: {
              label: 'Next',
              path: 'next',
              banner: 'unreleased',
            },
            '2.0': {
              label: '2.0 (LTS)',
              path: '2.0',
            },
            '1.5': {
              label: '1.5',
              path: '1.5',
            },
            '1.0': {
              label: '1.0 (EOL)',
              path: '1.0',
              banner: 'unmaintained',
            },
          },
        },
      },
    ],
  ],
};
```

### Step 2: Understanding Version Configuration

```javascript
docs: {
  // Path to sidebars configuration
  sidebarPath: require.resolve('./sidebars.js'),

  // Default version when accessing /docs
  lastVersion: '2.0',

  // Version definitions
  versions: {
    // Next/unreleased version
    current: {
      label: 'Next',         // Display name
      path: 'next',          // URL path
      banner: 'unreleased',  // Show unreleased banner
    },

    // Released versions
    '2.0': {
      label: '2.0 (LTS)',
      path: '2.0',
    },

    '1.5': {
      label: '1.5',
      path: '1.5',
    },

    // EOL version
    '1.0': {
      label: '1.0 (EOL)',
      path: '1.0',
      banner: 'unmaintained',
    },
  },
}
```

## Part 3: Creating a Version

### Method 1: Using Docusaurus CLI

Create a new version snapshot:

```bash
npm run docusaurus docs:version 2.0
```

This command:
1. Copies current `docs/` to `versioned_docs/version-2.0/`
2. Creates `versioned_sidebars/sidebars-2.0.js`
3. Updates `versions.json`

### What Gets Created

```
versioned_docs/
└── version-2.0/
    ├── intro.md
    ├── getting-started.md
    └── api/
        └── reference.md

versioned_sidebars/
└── sidebars-2.0.js

versions.json
{
  "2.0": "2.0",
  "1.5": "1.5",
  "1.0": "1.0"
}
```

### Method 2: Manual Version Creation

For manual control:

```bash
# Copy current docs
cp -r docs versioned_docs/version-2.0

# Copy sidebar
cp sidebars.js versioned_sidebars/sidebars-2.0.js

# Update versions.json manually
```

## Part 4: Version Management

### Create Multiple Versions

```bash
# Create version 2.0
npm run docusaurus docs:version 2.0

# Modify docs for next features
# ... update docs/

# Create version 2.1
npm run docusaurus docs:version 2.1

# Create version 3.0 (major)
npm run docusaurus docs:version 3.0
```

### versions.json Structure

```json
{
  "3.0": "3.0",
  "2.1": "2.1",
  "2.0": "2.0",
  "1.5": "1.5",
  "1.0": "1.0"
}
```

The first entry is the default version.

### Update Version Labels

Edit `docusaurus.config.js`:

```javascript
versions: {
  current: {
    label: 'Next (3.1)',
    path: 'next',
  },
  '3.0': {
    label: '3.0 (LTS)',
    path: '3.0',
  },
  '2.0': {
    label: '2.0 (Maintenance)',
    path: '2.0',
  },
  '1.5': {
    label: '1.5 (EOL)',
    path: '1.5',
    banner: 'unmaintained',
  },
}
```

### Hide Old Versions

```javascript
versions: {
  '1.0': {
    label: '1.0',
    path: '1.0',
    badge: false,  // Hide from version selector
  },
}
```

## Part 5: Version-Specific Sidebars

### Create Version Sidebar

When you create a version, a sidebar file is generated:

```javascript
// versioned_sidebars/sidebars-2.0.js
module.exports = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/quickstart',
      ],
    },
  ],
};
```

### Update Version Sidebar

Modify version-specific sidebars independently:

```javascript
// versioned_sidebars/sidebars-1.5.js
// This sidebar configuration is specific to version 1.5
module.exports = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        // 'getting-started/advanced-setup' removed in 1.5
      ],
    },
  ],
};
```

## Part 6: Version-Specific Content

### Create Version-Specific Pages

Document pages can have version-specific variants:

```
versioned_docs/
├── version-2.0/
│   ├── intro.md           # Version 2.0 intro
│   └── getting-started.md
docs/
├── intro.md               # Next version intro
└── getting-started.md
```

Each version's intro.md can have different content.

### Cross-Version Links

Link between versions:

```markdown
[View 1.5 documentation](../../1.5/getting-started.md)
[Current documentation](/docs/getting-started.md)
[Next version](/docs/next/getting-started.md)
```

### Version Warnings and Notices

Add warnings to old versions:

```markdown
---
id: intro
title: Getting Started
---

:::warning Version Notice
You are viewing documentation for version 1.5.
This version is no longer maintained.
[View latest documentation](../../docs/intro.md)
:::

# Getting Started
```

## Part 7: Version Badges and Banners

### Add Version Badges

In navigation bar (docusaurus.config.js):

```javascript
themeConfig: {
  navbar: {
    items: [
      {
        type: 'docsVersionDropdown',
        position: 'left',
        dropdownItemsAfter: [
          {
            href: 'https://github.com/facebook/docusaurus/releases',
            label: 'All releases',
          },
        ],
      },
    ],
  },
}
```

### Version Banners

Automatically displayed based on version state:

```javascript
versions: {
  current: {
    label: 'Next',
    banner: 'unreleased',  // Shows "This is unreleased documentation"
  },
  '1.0': {
    label: '1.0 (EOL)',
    banner: 'unmaintained', // Shows "This is unmaintained documentation"
  },
}
```

## Part 8: Building and Testing Versions

### Build All Versions

```bash
# Builds all versions for production
npm run build
```

Build output:

```
build/
├── docs/                    # Latest version (2.0)
├── docs/next/              # Next version
├── docs/1.5/               # Version 1.5
├── docs/1.0/               # Version 1.0
└── versions.json           # Version metadata
```

### Test Version Locally

```bash
# Start dev server
npm start

# Navigate to different versions in browser:
# http://localhost:3000/docs/         (latest)
# http://localhost:3000/docs/next/    (next)
# http://localhost:3000/docs/1.5/     (version 1.5)
```

### Test Production Build

```bash
npm run build
npm run serve

# Then visit http://localhost:3000
```

## Part 9: Advanced Version Scenarios

### Migrate Documentation Between Versions

```bash
# Create version 2.0
npm run docusaurus docs:version 2.0

# Make breaking changes to docs/
# These changes are now in "next" version

# Later, create version 2.1
npm run docusaurus docs:version 2.1
```

### Delete a Version

Remove version files:

```bash
# 1. Remove versioned docs
rm -rf versioned_docs/version-1.0
rm -rf versioned_sidebars/sidebars-1.0.js

# 2. Update versions.json
# Remove "1.0" entry

# 3. Rebuild
npm run build
```

### Set Different Default Versions per Path

```javascript
docs: {
  // API docs use version 2.0 as default
  docs: {
    sidebarPath: require.resolve('./sidebars.js'),
    lastVersion: '2.0',
  },
  // Blog uses current version
  blog: {
    lastVersion: 'current',
  },
}
```

## Part 10: Automation and CI/CD

### Automated Version Creation

Create GitHub Actions workflow:

```yaml
# .github/workflows/create-version.yml
name: Create Documentation Version

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version number (e.g., 2.0)'
        required: true
        type: string

jobs:
  create-version:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm install

      - name: Create version
        run: npm run docusaurus docs:version ${{ github.event.inputs.version }}

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v4
        with:
          commit-message: 'docs: create version ${{ github.event.inputs.version }}'
          title: 'docs: create version ${{ github.event.inputs.version }}'
          body: |
            Automated version creation for ${{ github.event.inputs.version }}

            Please review and merge to create the new documentation version.
          branch: docs/version-${{ github.event.inputs.version }}
```

### Version-Aware Deployment

```yaml
name: Deploy Versions

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - run: npm install
      - run: npm run build

      - name: Deploy all versions
        run: |
          # Deploy to each version path
          netlify deploy --prod --dir=build
```

## Part 11: Best Practices

### Version Naming

Use semantic versioning:
```
2.0      # Major version
2.1      # Minor version
2.1.1    # Patch version (use 2.1 instead)
next     # Upcoming version
```

### Documentation Organization

- Keep current version (docs/) actively maintained
- Update versioned docs only for critical fixes
- Clearly mark EOL versions
- Provide migration guides between versions

### Communication Strategy

1. **In Code**: Add version banners and notices
2. **In Navigation**: Make version selector obvious
3. **In README**: Document supported versions
4. **In Migration Guides**: Help users upgrade

### Version Lifecycle

```
Development → 2.0 Release → 2.1 Update → EOL
↓                                          ↓
docs/ (next)  → version-2.0  → version-2.1  → archive
```

## Part 12: Troubleshooting

### Version Not Showing

Check versions.json:

```bash
cat versions.json
# Should show all versions

# Verify versioned files exist
ls -la versioned_docs/
ls -la versioned_sidebars/
```

### Broken Links Between Versions

Use relative paths:

```markdown
# Good - works across versions
[See next](/docs/next/getting-started.md)

# Better - use version-aware links
import { useDoc } from '@docusaurus/theme-common/internal';

export function VersionLink() {
  const { version } = useDoc();
  return <a href={`/docs/${version}/guide/`}>Guide</a>;
}
```

### Build Size Growing

Remove unused versions:

```bash
# Check build size per version
du -sh build/docs/*

# Remove old versions if needed
```

## Resources

- [Docusaurus Versioning](https://docusaurus.io/docs/versioning)
- [Versioning Strategies](https://docusaurus.io/docs/versioning/advanced)
- [Version Upgrade Guides](https://docusaurus.io/docs/versioning/intro)

## Next Steps

After configuring versioning:
- Set up automated version creation in CI/CD
- Create version-specific deployment strategies
- Monitor which versions users are accessing
- Plan version lifecycle and deprecation timelines
- Add internationalization support across versions

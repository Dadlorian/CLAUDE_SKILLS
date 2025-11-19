# Complete Docusaurus Setup Guide

## Overview

Docusaurus is a modern documentation site generator built with React and Node.js. It provides a complete solution for creating documentation websites with versioning, full-text search, multiple languages, and dark mode support out of the box.

## Prerequisites

- Node.js 16.14+ installed
- npm or yarn package manager
- Basic knowledge of command line
- Git (for version control)

## Part 1: Initial Setup

### Step 1: Create a New Docusaurus Project

The quickest way to get started is using the Docusaurus scaffold:

```bash
npx create-docusaurus@latest my-docs classic
cd my-docs
```

This creates a new Docusaurus project using the "classic" template, which includes:
- Pre-configured Markdown support
- Built-in versioning system
- Dark mode support
- Search functionality
- API documentation support

### Step 2: Understand the Project Structure

```
my-docs/
├── blog/                 # Blog posts (optional)
├── docs/                 # Documentation pages
│   ├── intro.md         # Getting started
│   ├── tutorial-basics/ # Tutorial section
│   └── tutorial-extras/ # Extra tutorials
├── src/
│   ├── pages/          # Custom pages
│   └── css/            # Global styles
├── static/             # Static assets
├── sidebars.js         # Sidebar configuration
├── docusaurus.config.js # Main configuration
└── package.json        # Dependencies
```

### Step 3: Install Dependencies

```bash
npm install
# or
yarn install
```

### Step 4: Start Development Server

```bash
npm start
# or
yarn start
```

Your documentation site will be available at `http://localhost:3000`.

## Part 2: Configuration

### Configure docusaurus.config.js

The main configuration file controls all aspects of your documentation site:

```javascript
// docusaurus.config.js
module.exports = {
  title: 'My Documentation',
  tagline: 'The best docs ever',
  url: 'https://mydocs.com',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'myorg',
  projectName: 'my-docs',

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/myorg/my-docs/edit/main/',
        },
        blog: {
          showReadingTime: true,
          editUrl: 'https://github.com/myorg/my-docs/edit/main/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'My Documentation',
      logo: {
        alt: 'My Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'doc',
          docId: 'intro',
          position: 'left',
          label: 'Docs',
        },
        { to: '/blog', label: 'Blog', position: 'left' },
        {
          href: 'https://github.com/myorg/my-docs',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Getting Started',
              to: '/docs/intro',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'Stack Overflow',
              href: 'https://stackoverflow.com',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} My Company.`,
    },
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
  },
};
```

### Configure Sidebars

Create `sidebars.js` to define your documentation structure:

```javascript
// sidebars.js
module.exports = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: ['getting-started/installation', 'getting-started/quickstart'],
    },
    {
      type: 'category',
      label: 'Guides',
      items: [
        'guides/basic-usage',
        'guides/advanced-configuration',
        'guides/troubleshooting',
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api/core',
        'api/utilities',
        'api/hooks',
      ],
    },
  ],
};
```

## Part 3: Creating Documentation

### Writing Markdown Files

Create documentation files in the `docs/` directory:

```markdown
---
id: getting-started
title: Getting Started
sidebar_position: 1
---

# Getting Started

## Installation

Install via npm:

\`\`\`bash
npm install my-package
\`\`\`

## Basic Usage

Here's a simple example:

\`\`\`javascript
const myPackage = require('my-package');

myPackage.initialize({
  apiKey: 'your-api-key',
});
\`\`\`

## Next Steps

Now that you're set up, check out our [advanced guide](./advanced.md).
```

### Front Matter Options

All Docusaurus markdown files support front matter metadata:

```yaml
---
id: unique-id
title: Page Title
sidebar_position: 1
sidebar_label: Shorter Title
description: SEO description
keywords: [keyword1, keyword2]
image: /img/preview.png
---
```

### Using React Components

Embed React components in markdown:

```markdown
import MyComponent from '@site/src/components/MyComponent';

# Using React Components

<MyComponent />
```

## Part 4: Styling and Customization

### Custom CSS

Create `src/css/custom.css` for global styles:

```css
/* Custom CSS overrides */
:root {
  --ifm-color-primary: #2e8555;
  --ifm-color-primary-dark: #29784c;
  --ifm-color-primary-darker: #277148;
  --ifm-color-primary-darkest: #205540;
  --ifm-color-primary-light: #378a61;
  --ifm-color-primary-lighter: #3f9970;
  --ifm-color-primary-lightest: #4ca181;
}

/* Dark mode colors */
[data-theme='dark'] {
  --ifm-color-primary: #25c2a0;
}

/* Custom component styling */
.custom-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  border-radius: 8px;
  color: white;
}
```

### Custom Themes

Create custom React components in `src/theme/`:

```typescript
// src/theme/Footer/index.tsx
import React from 'react';
import Layout from '@theme/Layout';

export default function CustomFooter() {
  return (
    <footer className="custom-footer">
      <div className="container">
        <p>Custom Footer Content</p>
      </div>
    </footer>
  );
}
```

## Part 5: Building for Production

### Build Static Site

```bash
npm run build
# or
yarn build
```

This generates a static site in the `build/` directory optimized for production.

### Serve Locally

Test the production build locally:

```bash
npm run serve
# or
yarn serve
```

### Deployment Options

**GitHub Pages:**

```bash
# Add to docusaurus.config.js
module.exports = {
  url: 'https://username.github.io',
  baseUrl: '/repo-name/',
  organizationName: 'username',
  projectName: 'repo-name',
};

npm run deploy
```

**Netlify:**

Connect your repository and configure build settings:
- Build command: `npm run build`
- Publish directory: `build`

**Vercel:**

```bash
vercel
```

## Part 6: Advanced Features

### Admonitions (Notes, Warnings, etc.)

```markdown
:::note
This is a note
:::

:::tip
This is a helpful tip
:::

:::warning
This is a warning
:::

:::danger
This is a dangerous operation
:::
```

### Code Block Features

```javascript title="example.js" showLineNumbers
function hello() {
  console.log('Hello, world!');
}
```

### Tabs

```markdown
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
  <TabItem value="js" label="JavaScript">
    ```js
    console.log('Hello');
    ```
  </TabItem>
  <TabItem value="py" label="Python">
    ```python
    print('Hello')
    ```
  </TabItem>
</Tabs>
```

## Common Issues and Solutions

### Port Already in Use

```bash
# Use a different port
npm start -- --port 3001
```

### Out of Memory

```bash
# Increase Node memory limit
NODE_OPTIONS=--max_old_space_size=4096 npm run build
```

### Build Errors

Clear cache and rebuild:

```bash
rm -rf build
npm run clear
npm run build
```

## Best Practices

1. **Organize Documentation Hierarchy**: Use clear categories and subcategories
2. **Write Clear Introductions**: Start each section with a brief overview
3. **Include Code Examples**: Make examples copy-paste ready
4. **Use Consistent Formatting**: Maintain consistent markdown style
5. **Regular Updates**: Keep documentation synchronized with code changes
6. **Test Links**: Verify all internal and external links work
7. **Optimize Images**: Compress images before adding to docs

## Resources

- [Official Docusaurus Documentation](https://docusaurus.io)
- [Docusaurus GitHub Repository](https://github.com/facebook/docusaurus)
- [Community Showcase](https://docusaurus.io/showcase)
- [Discussion Forum](https://github.com/facebook/docusaurus/discussions)

## Next Steps

Now that you have Docusaurus configured, consider:
- Setting up search with Algolia
- Implementing CI/CD for automated deployment
- Adding versioning for multiple documentation versions
- Configuring internationalization support
- Customizing the theme further

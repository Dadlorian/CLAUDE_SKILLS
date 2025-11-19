# Building Custom Docusaurus Plugins: A Comprehensive Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Plugin Architecture](#plugin-architecture)
3. [Core Concepts](#core-concepts)
4. [Plugin Development Environment](#plugin-development-environment)
5. [Creating Your First Plugin](#creating-your-first-plugin)
6. [Plugin Lifecycle](#plugin-lifecycle)
7. [Advanced Plugin Development](#advanced-plugin-development)
8. [Plugin Examples](#plugin-examples)
9. [Testing Plugins](#testing-plugins)
10. [Distribution and Sharing](#distribution-and-sharing)

## Introduction

Docusaurus plugins enable you to extend the framework's functionality by hooking into its build process, configuration system, and client-side runtime. This guide covers everything needed to develop production-grade plugins.

### Plugin Capabilities

- **Content Processing**: Transform content during build
- **File Generation**: Dynamically create pages and assets
- **Client Components**: Add custom React components
- **Build Optimization**: Modify webpack configuration
- **API Endpoints**: Add custom API routes
- **Theme Customization**: Extend theme behavior
- **Analytics Integration**: Connect tracking systems
- **Search Enhancement**: Customize search behavior

## Plugin Architecture

### Docusaurus Plugin Structure

```
plugin-example/
├── package.json
├── index.js                    # Main plugin file
├── lib/
│   ├── index.js               # Plugin implementation
│   ├── transform.js           # Content transformation
│   └── utils.js               # Helper functions
├── src/
│   ├── components/            # React components
│   ├── hooks/                 # Custom hooks
│   └── types/                 # TypeScript definitions
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

### Plugin Entry Point

```javascript
// index.js
module.exports = function(context, options) {
  return {
    name: 'my-plugin',
    async loadContent() {
      // Load content
    },
    async contentLoaded({content, actions}) {
      // Create routes/pages
    },
    getThemePath() {
      // Return custom theme path
    },
    getTypeScriptThemePath() {
      // Return TypeScript theme path
    },
    injectHtmlTags() {
      // Inject HTML tags
    },
    configureWebpack(config, isServer, utils) {
      // Modify webpack config
    },
    postBuild(props) {
      // Post-build actions
    },
    extendsConfig(config, configName) {
      // Extend Docusaurus config
    },
  };
};

module.exports.validateOptions = function({options, validate}) {
  const schema = Joi.object({
    optionA: Joi.string().required(),
    optionB: Joi.number().default(0),
  });
  return validate(schema, options);
};
```

## Core Concepts

### Plugin Context

The context object provides access to site configuration:

```javascript
function plugin(context, options) {
  const {siteDir, cacheDir, outDir, baseUrl} = context;

  return {
    name: 'my-plugin',
    async loadContent() {
      // context available here
      console.log('Site directory:', siteDir);
      console.log('Cache directory:', cacheDir);
      console.log('Output directory:', outDir);
      console.log('Base URL:', baseUrl);
    },
  };
}
```

### Plugin Configuration

```javascript
// docusaurus.config.js
module.exports = {
  plugins: [
    [
      'my-plugin',
      {
        // Plugin options
        optionA: 'value',
        optionB: 123,
        features: {
          enabled: true,
          verbose: false,
        },
      },
    ],
  ],
};
```

### Plugin Options Validation

```javascript
const Joi = require('joi');

module.exports.validateOptions = function({options, validate}) {
  const schema = Joi.object({
    id: Joi.string().required(),
    title: Joi.string().required(),
    description: Joi.string().optional(),
    tags: Joi.array().items(Joi.string()),
    config: Joi.object({
      enabled: Joi.boolean().default(true),
      verbose: Joi.boolean().default(false),
    }),
  });

  const {error, value} = schema.validate(options);
  if (error) {
    throw new Error(`Invalid plugin options: ${error.message}`);
  }
  return value;
};
```

## Plugin Development Environment

### Setup

```bash
# Create plugin scaffold
mkdir docusaurus-plugin-myfeature
cd docusaurus-plugin-myfeature

# Initialize package.json
npm init -y

# Install dependencies
npm install \
  @docusaurus/core \
  @docusaurus/types \
  joi \
  react \
  react-dom
```

### Package Configuration

```json
{
  "name": "docusaurus-plugin-myfeature",
  "version": "1.0.0",
  "description": "A custom Docusaurus plugin for...",
  "main": "lib/index.js",
  "types": "lib/index.d.ts",
  "peerDependencies": {
    "@docusaurus/core": "^2.0.0",
    "@docusaurus/types": "^2.0.0",
    "react": "^17.0.0 || ^18.0.0",
    "react-dom": "^17.0.0 || ^18.0.0"
  },
  "devDependencies": {
    "@docusaurus/types": "^2.4.0",
    "joi": "^17.9.0",
    "typescript": "^5.0.0"
  },
  "files": [
    "lib",
    "package.json"
  ],
  "scripts": {
    "build": "tsc",
    "test": "jest",
    "prepublishOnly": "npm run build"
  }
}
```

## Creating Your First Plugin

### Simple Blog Plugin

```javascript
// lib/index.js

module.exports = function(context, options) {
  const {siteDir, cacheDir} = context;

  return {
    name: 'docusaurus-plugin-custom-blog',

    async loadContent() {
      // Load blog posts from external source
      return {
        posts: [
          {
            id: 'post-1',
            title: 'My First Post',
            content: 'This is the content...',
            date: '2024-01-01',
          },
        ],
      };
    },

    async contentLoaded({content, actions}) {
      const {createData, addRoute} = actions;

      // Create route for each post
      content.posts.forEach((post) => {
        addRoute({
          path: `/blog/${post.id}`,
          component: '@theme/BlogPostPage',
          modules: {
            content: createData(
              `blog-${post.id}.json`,
              JSON.stringify(post),
            ),
          },
          exact: true,
        });
      });
    },

    injectHtmlTags() {
      return {
        headTags: [
          {
            tagName: 'meta',
            attributes: {
              name: 'blog-plugin',
              content: 'loaded',
            },
          },
        ],
      };
    },
  };
};

module.exports.validateOptions = ({options, validate}) => {
  const schema = require('joi').object({
    id: require('joi').string().default('custom-blog'),
  });
  return validate(schema, options);
};
```

## Plugin Lifecycle

### Execution Order

```
1. normalizeConfig() - Normalize plugin options
2. validateOptions() - Validate plugin options
3. loadContent() - Load/fetch content
4. contentLoaded() - Create routes/pages
5. configureWebpack() - Modify webpack
6. injectHtmlTags() - Inject HTML
7. getPathsToWatch() - Watch file changes
8. postBuild() - Post-build actions
```

### Lifecycle Hooks

```javascript
module.exports = function(context, options) {
  return {
    name: 'lifecycle-demo-plugin',

    // Phase 1: Setup
    extendCli(cli) {
      cli.command('custom-command')
        .description('Run custom command')
        .action(async () => {
          console.log('Custom command executed');
        });
    },

    // Phase 2: Content Loading
    getPathsToWatch() {
      return [
        `${context.siteDir}/custom-content/**/*.md`,
      ];
    },

    async loadContent() {
      console.log('Loading content...');
      // Simulate content loading
      return {loaded: true};
    },

    // Phase 3: Route Creation
    async contentLoaded({content, actions}) {
      console.log('Content loaded, creating routes...');
      // Create routes
    },

    // Phase 4: Webpack Configuration
    configureWebpack(config, isServer, utils) {
      console.log('Configuring webpack...');
      return {
        module: {
          rules: [
            {
              test: /\.custom$/,
              use: ['custom-loader'],
            },
          ],
        },
      };
    },

    // Phase 5: HTML Injection
    injectHtmlTags() {
      return {
        headTags: [],
        preBodyTags: [],
        postBodyTags: [],
      };
    },

    // Phase 6: Post Build
    postBuild({siteDir, outDir, baseUrl}) {
      console.log('Build complete, running post-build tasks...');
    },
  };
};
```

## Advanced Plugin Development

### Content Transformation Plugin

```javascript
// lib/markdown-transformer.js

const fs = require('fs').promises;
const path = require('path');

module.exports = function(context, options) {
  return {
    name: 'markdown-transformer-plugin',

    async getPathsToWatch() {
      return [
        `${context.siteDir}/docs/**/*.md`,
      ];
    },

    async loadContent() {
      const docsDir = path.join(context.siteDir, 'docs');
      const files = await this.getAllMdFiles(docsDir);

      const transformedContent = [];
      for (const file of files) {
        const content = await fs.readFile(file, 'utf-8');
        const transformed = this.transformMarkdown(content);
        transformedContent.push({
          path: file,
          original: content,
          transformed,
        });
      }

      return {files: transformedContent};
    },

    async contentLoaded({content, actions}) {
      const {createData} = actions;

      // Create a data file with transformation results
      await createData(
        'markdown-transformations.json',
        JSON.stringify(content, null, 2),
      );
    },

    transformMarkdown(content) {
      // Convert custom syntax
      content = content.replace(
        /\{\{([^}]+)\}\}/g,
        (match, variable) => `<Variable name="${variable}" />`,
      );

      // Add metadata
      content = content.replace(
        /^# ([^\n]+)/,
        (match, title) => `# ${title}\n\n*Updated: ${new Date().toISOString()}*`,
      );

      return content;
    },

    async getAllMdFiles(dir) {
      const files = [];
      const entries = await fs.readdir(dir, {withFileTypes: true});

      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          files.push(...await this.getAllMdFiles(fullPath));
        } else if (entry.isFile() && entry.name.endsWith('.md')) {
          files.push(fullPath);
        }
      }

      return files;
    },
  };
};
```

### API Route Plugin

```javascript
// lib/api-routes-plugin.js

module.exports = function(context, options) {
  return {
    name: 'api-routes-plugin',

    extendCli(cli) {
      cli
        .command('generate-api-docs')
        .description('Generate API documentation')
        .action(async () => {
          // Generate API docs from source
          console.log('Generating API documentation...');
        });
    },

    async loadContent() {
      // Load API specifications
      const apis = [
        {
          path: '/api/users',
          method: 'GET',
          description: 'Get all users',
          params: [],
          response: {type: 'array'},
        },
        {
          path: '/api/users/:id',
          method: 'GET',
          description: 'Get user by ID',
          params: [{name: 'id', type: 'string'}],
          response: {type: 'object'},
        },
      ];

      return {apis};
    },

    async contentLoaded({content, actions}) {
      const {createData, addRoute} = actions;

      // Generate API reference pages
      content.apis.forEach((api, index) => {
        const data = {
          ...api,
          documentation: `API documentation for ${api.path}`,
        };

        addRoute({
          path: `/api-reference/${api.path.replace(/\//g, '-')}`,
          component: '@theme/ApiReferencePage',
          modules: {
            api: createData(`api-${index}.json`, JSON.stringify(data)),
          },
        });
      });
    },
  };
};
```

### Theme Components Plugin

```javascript
// lib/theme-plugin.js

const path = require('path');

module.exports = function(context, options) {
  return {
    name: 'custom-theme-plugin',

    getThemePath() {
      return path.resolve(__dirname, '../src/theme');
    },

    getTypeScriptThemePath() {
      return path.resolve(__dirname, '../src/theme');
    },

    async contentLoaded({actions}) {
      const {addRoute} = actions;

      // Register custom pages
      addRoute({
        path: '/showcase',
        component: '@theme/ShowcasePage',
      });
    },
  };
};
```

## Plugin Examples

### Example 1: Changelog Plugin

```javascript
// lib/changelog-plugin.js

const fs = require('fs').promises;
const path = require('path');

module.exports = function(context, options) {
  return {
    name: 'changelog-plugin',

    async loadContent() {
      const changelogPath = path.join(
        context.siteDir,
        'CHANGELOG.md'
      );

      try {
        const content = await fs.readFile(changelogPath, 'utf-8');
        return {changelog: this.parseChangelog(content)};
      } catch (error) {
        console.error('Changelog not found');
        return {changelog: []};
      }
    },

    parseChangelog(content) {
      const entries = [];
      const lines = content.split('\n');
      let current = null;

      for (const line of lines) {
        if (line.match(/^## \[[\d.]+\]/)) {
          if (current) entries.push(current);
          const match = line.match(/^## \[([\d.]+)\] - ([\d-]+)/);
          current = {
            version: match[1],
            date: match[2],
            changes: [],
          };
        } else if (line.startsWith('- ') && current) {
          current.changes.push(line.substring(2));
        }
      }

      if (current) entries.push(current);
      return entries;
    },

    async contentLoaded({content, actions}) {
      const {createData, addRoute} = actions;

      addRoute({
        path: '/changelog',
        component: '@theme/ChangelogPage',
        modules: {
          changelog: createData(
            'changelog.json',
            JSON.stringify(content.changelog),
          ),
        },
      });
    },
  };
};
```

### Example 2: Social Media Preview Plugin

```javascript
// lib/social-preview-plugin.js

module.exports = function(context, options) {
  return {
    name: 'social-preview-plugin',

    injectHtmlTags({content}) {
      return {
        headTags: [
          {
            tagName: 'meta',
            attributes: {
              property: 'og:image',
              content: `${context.baseUrl}img/social-preview.png`,
            },
          },
          {
            tagName: 'meta',
            attributes: {
              property: 'og:description',
              content: 'Documentation for my project',
            },
          },
          {
            tagName: 'meta',
            attributes: {
              name: 'twitter:card',
              content: 'summary_large_image',
            },
          },
        ],
      };
    },
  };
};
```

## Testing Plugins

### Unit Tests

```javascript
// tests/unit/transformer.test.js

const plugin = require('../../lib/index');

describe('Custom Plugin', () => {
  let mockContext;
  let mockOptions;

  beforeEach(() => {
    mockContext = {
      siteDir: '/mock/site',
      cacheDir: '/mock/cache',
      outDir: '/mock/out',
      baseUrl: '/',
    };
    mockOptions = {
      id: 'test-plugin',
    };
  });

  test('should create plugin instance', () => {
    const instance = plugin(mockContext, mockOptions);
    expect(instance.name).toBe('test-plugin');
  });

  test('should validate options correctly', () => {
    const schema = plugin.validateOptions({
      options: mockOptions,
      validate: (schema, options) => ({value: options}),
    });
    expect(schema).toBeDefined();
  });

  test('should load content', async () => {
    const instance = plugin(mockContext, mockOptions);
    const content = await instance.loadContent();
    expect(content).toBeDefined();
  });
});
```

### Integration Tests

```javascript
// tests/integration/plugin.test.js

const path = require('path');
const fs = require('fs');

describe('Plugin Integration', () => {
  const testSiteDir = path.join(__dirname, '../fixtures/test-site');

  test('should build successfully', async () => {
    // Run full build with plugin
    const result = await runDocusaurusBuild(testSiteDir);
    expect(result.exitCode).toBe(0);
  });

  test('should generate expected output files', async () => {
    const outDir = path.join(testSiteDir, 'build');
    const files = fs.readdirSync(outDir);
    expect(files.length).toBeGreaterThan(0);
  });
});
```

## Distribution and Sharing

### Publishing to npm

```bash
# Update version
npm version patch

# Build plugin
npm run build

# Publish to npm
npm publish

# Or publish to GitHub Packages
npm publish --registry https://npm.pkg.github.com
```

### Documentation

```markdown
# docusaurus-plugin-myfeature

Custom Docusaurus plugin for [feature description].

## Installation

```bash
npm install docusaurus-plugin-myfeature
```

## Configuration

```javascript
// docusaurus.config.js
module.exports = {
  plugins: [
    [
      'docusaurus-plugin-myfeature',
      {
        // options
      },
    ],
  ],
};
```

## Options

- `id` (string): Plugin identifier
- `enabled` (boolean): Enable/disable plugin

## Examples

[Include usage examples]
```

### Plugin Template

```bash
# Use Docusaurus plugin template
npx create-docusaurus-plugin my-plugin
```

## Best Practices

### Performance Considerations

- Cache expensive computations
- Use incremental builds
- Minimize webpack bundle impact
- Lazy load large datasets

### Security

- Validate all options
- Sanitize user input
- Check file permissions
- Avoid code injection

### Maintainability

- Write comprehensive tests
- Document all options
- Include type definitions
- Follow Docusaurus conventions
- Maintain semantic versioning

## Conclusion

Custom Docusaurus plugins provide powerful extensibility:
- Content transformation
- Route generation
- Component customization
- Build optimization
- Theme enhancement

Key points:
- Understand plugin lifecycle
- Leverage Docusaurus APIs
- Test thoroughly
- Document clearly
- Share with community


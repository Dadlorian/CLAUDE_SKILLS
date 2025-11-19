# Internationalization (i18n) Setup Guide

## Overview

Internationalization enables your documentation to support multiple languages, making it accessible to a global audience. Docusaurus provides built-in i18n support through the Crowdin integration.

## Prerequisites

- Docusaurus project already set up and deployed
- Understanding of your target languages and locales
- Git repository management knowledge
- Access to crowdin.com (optional but recommended)
- Basic knowledge of locale codes (en, es, fr, etc.)

## Part 1: Understanding i18n in Docusaurus

### What is Internationalization?

i18n allows you to:
- Translate documentation to multiple languages
- Serve different language versions at different URLs
- Manage translations efficiently
- Use community translators
- Maintain language-specific content

### Language Structure

```
i18n/
├── en/              # English (default)
├── es/              # Spanish
├── fr/              # French
├── zh/              # Chinese
└── de/              # German

Resulting URLs:
/docs/               → English
/docs/es/           → Spanish
/docs/fr/           → French
/docs/zh/           → Chinese
/docs/de/           → German
```

## Part 2: Enabling i18n

### Step 1: Configure Locales

Update `docusaurus.config.js`:

```javascript
module.exports = {
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'es', 'fr', 'zh', 'de'],
    localeConfigs: {
      en: {
        label: 'English',
        direction: 'ltr',
        htmlLang: 'en-US',
      },
      es: {
        label: 'Español',
        direction: 'ltr',
        htmlLang: 'es-ES',
      },
      fr: {
        label: 'Français',
        direction: 'ltr',
        htmlLang: 'fr-FR',
      },
      zh: {
        label: '中文',
        direction: 'ltr',
        htmlLang: 'zh-CN',
      },
      de: {
        label: 'Deutsch',
        direction: 'ltr',
        htmlLang: 'de-DE',
      },
    },
  },
};
```

### Step 2: Create Language Directories

```bash
mkdir -p i18n/en
mkdir -p i18n/es
mkdir -p i18n/fr
mkdir -p i18n/zh
mkdir -p i18n/de
```

### Folder Structure

```
i18n/
├── en/
│   ├── docusaurus-plugin-content-docs/
│   │   └── current/
│   │       └── intro.md
│   ├── docusaurus-plugin-content-blog/
│   │   └── 2024-01-01-first-post.md
│   └── docusaurus-theme-classic/
│       └── navbar.json
├── es/
│   ├── docusaurus-plugin-content-docs/
│   └── docusaurus-theme-classic/
└── fr/
    └── ...
```

## Part 3: Setting Up Translations

### Step 1: Initialize Translations

```bash
npm run write-translations -- --locale en
npm run write-translations -- --locale es
npm run write-translations -- --locale fr
npm run write-translations -- --locale zh
npm run write-translations -- --locale de
```

This generates JSON files for translatable strings.

### Step 2: Translate UI Strings

Edit locale-specific translation files:

```json
// i18n/es/docusaurus-theme-classic/navbar.json
{
  "item.label.Docs": "Documentación",
  "item.label.Blog": "Blog",
  "item.label.GitHub": "GitHub",
  "logo.alt": "Logo de mi sitio"
}
```

```json
// i18n/fr/docusaurus-theme-classic/navbar.json
{
  "item.label.Docs": "Documentation",
  "item.label.Blog": "Blog",
  "item.label.GitHub": "GitHub",
  "logo.alt": "Logo de mon site"
}
```

### Step 3: Translate Documentation

Copy English docs to language directories:

```bash
# Copy docs structure to Spanish
cp -r docs/* i18n/es/docusaurus-plugin-content-docs/current/

# Copy docs structure to French
cp -r docs/* i18n/fr/docusaurus-plugin-content-docs/current/

# Translate the copied files in each language directory
```

### Manual Translation Example

```markdown
// docs/intro.md (English)
# Getting Started

Welcome to our documentation.

---

// i18n/es/docusaurus-plugin-content-docs/current/intro.md (Spanish)
# Comenzando

Bienvenido a nuestra documentación.

---

// i18n/fr/docusaurus-plugin-content-docs/current/intro.md (French)
# Démarrage

Bienvenue dans notre documentation.
```

## Part 4: Using Crowdin for Translations

### What is Crowdin?

Crowdin is a collaborative translation management platform that:
- Manages translation workflow
- Coordinates multiple translators
- Provides translation quality checks
- Automates language sync with Git
- Offers professional translation features

### Step 1: Create Crowdin Project

1. Sign up at [crowdin.com](https://crowdin.com)
2. Create a new project
3. Choose project type: "Other"
4. Set base language: English

### Step 2: Configure GitHub Integration

In Crowdin project settings:

1. Go to **Integrations → GitHub**
2. Authorize Crowdin to access your repository
3. Configure branch settings:

```
Repository: yourorg/your-docs
Base path: /
Translation path: /i18n
File export pattern: /%language%/
```

### Step 3: Upload Source Files

```bash
# Install Crowdin CLI
npm install -g @crowdin/cli

# Configure .crowdinrc.yml
```

Create `.crowdinrc.yml`:

```yaml
"project_id": "YOUR_PROJECT_ID"
"api_token": "YOUR_API_TOKEN"
"base_path": "./"
"base_url": "https://api.crowdin.com"

"preserve_hierarchy": true

"files":
  -
    "source": "/docs/**/*.md"
    "translation": "/i18n/%two_letters_code%/docusaurus-plugin-content-docs/current/%original_file_name%"

  -
    "source": "/blog/**/*.md"
    "translation": "/i18n/%two_letters_code%/docusaurus-plugin-content-blog/%original_file_name%"

  -
    "source": "/i18n/en/**/*.json"
    "translation": "/i18n/%two_letters_code%/%original_path%/%original_file_name%"
```

### Step 4: Upload and Sync

```bash
# Upload source files to Crowdin
crowdin upload sources

# Pull completed translations
crowdin download

# Commit translations to Git
git add i18n/
git commit -m "chore: sync translations from Crowdin"
```

## Part 5: Advanced i18n Configuration

### Right-to-Left (RTL) Languages

Configure for Arabic, Hebrew, etc.:

```javascript
i18n: {
  localeConfigs: {
    ar: {
      label: 'العربية',
      direction: 'rtl',
      htmlLang: 'ar-SA',
    },
    he: {
      label: 'עברית',
      direction: 'rtl',
      htmlLang: 'he-IL',
    },
  },
}
```

### Language-Specific Metadata

```javascript
i18n: {
  localeConfigs: {
    es: {
      label: 'Español',
      htmlLang: 'es-ES',
      calendar: 'gregorian',
      path: 'es',
    },
    zh: {
      label: '中文',
      htmlLang: 'zh-Hans-CN',
      calendar: 'chinese',
      path: 'zh',
    },
  },
}
```

### Language-Specific Styling

```css
/* src/css/custom.css */

/* Arabic RTL styles */
[lang='ar'] {
  direction: rtl;
  text-align: right;
}

[lang='ar'] .navbar__logo {
  margin-right: auto;
  margin-left: 0;
}

/* Chinese font customization */
[lang='zh'] {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 16px;
  line-height: 1.8;
}

/* Japanese font */
[lang='ja'] {
  font-family: 'Noto Sans JP', sans-serif;
}
```

## Part 6: Component Translation

### React Components with i18n

```typescript
// src/components/LanguageSwitcher.tsx
import React from 'react';
import { useLocation } from '@docusaurus/router';
import Link from '@docusaurus/Link';

const locales = {
  en: { label: 'English', flag: '🇺🇸' },
  es: { label: 'Español', flag: '🇪🇸' },
  fr: { label: 'Français', flag: '🇫🇷' },
  zh: { label: '中文', flag: '🇨🇳' },
};

export function LanguageSwitcher() {
  const location = useLocation();
  const currentLocale = location.pathname.split('/')[1] || 'en';

  return (
    <div className="language-switcher">
      {Object.entries(locales).map(([locale, { label, flag }]) => (
        <Link
          key={locale}
          href={`/${locale}${location.pathname.replace(/^\/[a-z]{2}/, '')}`}
          className={currentLocale === locale ? 'active' : ''}
        >
          {flag} {label}
        </Link>
      ))}
    </div>
  );
}
```

### Translation Hooks

```typescript
// src/components/TranslatedContent.tsx
import { useDocusaurusContext } from '@docusaurus/core/lib/contexts/docusaurusContext';
import { useLocation } from '@docusaurus/router';

export function TranslatedContent() {
  const { i18n } = useDocusaurusContext();
  const location = useLocation();
  const currentLocale = location.pathname.split('/')[1] || i18n.defaultLocale;

  return (
    <div>
      Current language: {currentLocale}
      Available languages: {i18n.locales.join(', ')}
    </div>
  );
}
```

### Dynamic Content Translation

```typescript
// src/hooks/useTranslate.ts
import { useMemo } from 'react';
import { useLocation } from '@docusaurus/router';

const translations = {
  en: {
    welcome: 'Welcome to our documentation',
    getStarted: 'Get Started',
  },
  es: {
    welcome: 'Bienvenido a nuestra documentación',
    getStarted: 'Comenzar',
  },
  fr: {
    welcome: 'Bienvenue dans notre documentation',
    getStarted: 'Commencer',
  },
};

export function useTranslate() {
  const location = useLocation();
  const locale = location.pathname.split('/')[1] || 'en';

  return useMemo(() => translations[locale] || translations.en, [locale]);
}
```

## Part 7: Building Multilingual Sites

### Build for All Languages

```bash
# Builds all language versions
npm run build
```

Output structure:

```
build/
├── index.html
├── en/
│   └── index.html
├── es/
│   └── index.html
├── fr/
│   └── index.html
└── zh/
    └── index.html
```

### Build Specific Language

```bash
# Build only English
DOCUSAURUS_CURRENT_LOCALE=en npm run build

# Build only Spanish
DOCUSAURUS_CURRENT_LOCALE=es npm run build
```

### Test Multilingual Build

```bash
npm run build
npm run serve

# Navigate to:
# http://localhost:3000          (English)
# http://localhost:3000/es/      (Spanish)
# http://localhost:3000/fr/      (French)
```

## Part 8: SEO for Multilingual Sites

### hreflang Tags

Docusaurus automatically generates hreflang tags:

```html
<!-- In English version -->
<link rel="alternate" hreflang="en" href="https://example.com/docs/" />
<link rel="alternate" hreflang="es" href="https://example.com/es/docs/" />
<link rel="alternate" hreflang="fr" href="https://example.com/fr/docs/" />
```

### Sitemap Configuration

```javascript
// docusaurus.config.js
module.exports = {
  plugins: [
    'plugin-sitemap',
  ],

  pluginConfig: {
    sitemap: {
      changefreq: 'weekly',
      priority: 0.8,
      trailingSlash: false,
    },
  },
};
```

### Language Metadata

```markdown
---
id: intro
title: Getting Started
description: Getting started with our product
keywords: [getting started, introduction, tutorial]
---
```

## Part 9: Crowdin Automation

### GitHub Action for Translation Sync

```yaml
# .github/workflows/crowdin-sync.yml
name: Sync Translations with Crowdin

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Upload source files to Crowdin
        uses: crowdin/github-action@v1
        with:
          upload_sources: true
          upload_sources_args: '--auto-update -b main'
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          CROWDIN_PROJECT_ID: ${{ secrets.CROWDIN_PROJECT_ID }}
          CROWDIN_PERSONAL_TOKEN: ${{ secrets.CROWDIN_PERSONAL_TOKEN }}

      - name: Download translations from Crowdin
        uses: crowdin/github-action@v1
        with:
          download_translations: true
          download_translations_args: '-b main'
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          CROWDIN_PROJECT_ID: ${{ secrets.CROWDIN_PROJECT_ID }}
          CROWDIN_PERSONAL_TOKEN: ${{ secrets.CROWDIN_PERSONAL_TOKEN }}

      - name: Commit translations
        run: |
          git config user.name "Translation Bot"
          git config user.email "translations@example.com"
          git add i18n/
          git commit -m "chore: sync translations from Crowdin" || true
          git push
```

### Configure Crowdin Secrets

In GitHub repository settings:

```
CROWDIN_PROJECT_ID: Your Crowdin project ID
CROWDIN_PERSONAL_TOKEN: Your Crowdin API token
```

## Part 10: Common Patterns

### Language-Specific Blog Posts

```bash
# English blog post
blog/2024-01-15-new-feature.md

# Spanish version
i18n/es/docusaurus-plugin-content-blog/2024-01-15-new-feature.md

# French version
i18n/fr/docusaurus-plugin-content-blog/2024-01-15-new-feature.md
```

### Language Fallback

Missing translations automatically fall back to default language:

```
User requests: /fr/docs/api/  (French API docs)
French version missing
↓
Falls back to: /docs/api/ (English)
```

### Partial Translations

You can translate only some sections:

```
/docs/                    # Fully translated
/docs/getting-started.md  # Translated to Spanish, French
/docs/api/               # Only in English
```

## Part 11: Troubleshooting

### Language Switcher Not Working

Verify configuration:

```javascript
// docusaurus.config.js
i18n: {
  defaultLocale: 'en',
  locales: ['en', 'es', 'fr'],  // Must include default
}
```

### Translations Not Loading

Check folder structure:

```bash
# Verify correct structure
find i18n/ -type f -name "*.json" | head -5
find i18n/ -type f -name "*.md" | head -5
```

### Build Errors with Multiple Languages

Clear cache and rebuild:

```bash
rm -rf .docusaurus build
npm run build
```

## Best Practices

1. **Use Professional Translators**: For quality and consistency
2. **Maintain Translation Memory**: Keep glossaries and style guides
3. **Update Regularly**: Sync with Crowdin frequently
4. **Test All Languages**: Verify rendering in each language
5. **Use Community Translators**: For open-source projects
6. **Set Translation Deadlines**: For synchronized releases
7. **Monitor Completion**: Track translation progress
8. **Provide Context**: Add translator notes for clarity

## Translation Quality Checklist

- [ ] Terminology consistent across translations
- [ ] Grammar and spelling verified
- [ ] Links and references updated
- [ ] Code examples preserved
- [ ] RTL languages tested
- [ ] Special characters rendered correctly
- [ ] Mobile responsiveness checked
- [ ] Search works in all languages

## Resources

- [Docusaurus i18n](https://docusaurus.io/docs/i18n/introduction)
- [Crowdin Integration](https://crowdin.com/integrations/docusaurus)
- [Translation Best Practices](https://crowdin.com/blog/translation-best-practices)
- [Unicode and Internationalization](https://unicode.org/)
- [Language Codes](https://www.loc.gov/standards/iso639-2/php/code_list.php)

## Next Steps

After setting up i18n:
- Recruit and onboard translators
- Establish translation workflow and deadlines
- Set up automated sync with Crowdin
- Monitor translation quality and completion
- Plan regular translation updates with releases
- Analyze user engagement by language
- Expand to additional languages based on demand

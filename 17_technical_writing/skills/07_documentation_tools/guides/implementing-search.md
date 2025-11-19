# Algolia DocSearch Integration Guide

## Overview

Algolia DocSearch is a free service that provides fast, accurate search for documentation sites. It crawls your documentation, indexes the content, and provides an optimized search experience with zero configuration.

## Prerequisites

- A Docusaurus documentation site (see Setting Up Docusaurus guide)
- Published documentation accessible online
- A GitHub account (for DocSearch application)
- Basic understanding of Algolia search concepts

## Part 1: Getting Started with Algolia DocSearch

### What is Algolia DocSearch?

Algolia DocSearch is a service that:
- Automatically crawls your documentation site
- Indexes content for instant search results
- Provides a free tier for open-source projects
- Offers a beautiful search UI out of the box
- Supports multiple languages and versions

### Benefits

- **Zero Configuration**: No complex setup required
- **Fast Search**: Returns results in milliseconds
- **Free for Open Source**: No cost for qualifying projects
- **Analytics**: Track search queries and user behavior
- **Multiple Versions**: Search across documentation versions
- **Smart Ranking**: Results ranked by relevance

## Part 2: Applying for DocSearch

### Step 1: Meet the Requirements

DocSearch is free for qualifying projects:
- Open-source or technical content projects
- Published on a public domain
- Well-structured documentation
- Good content quality

### Step 2: Submit Application

Navigate to [https://docsearch.algolia.com/apply](https://docsearch.algolia.com/apply) and fill out the form:

```
Project Name: Your Documentation Project
Project URL: https://yourdocs.example.com
Email: your-email@example.com
Repository URL: https://github.com/yourorg/your-docs
Documentation Type: Technical Documentation
Other details: Brief description of your project
```

### Step 3: Wait for Approval

The Algolia team reviews applications within 1-5 days. Once approved, you'll receive:
- An API Key
- An Application ID
- Indexing credentials
- Setup instructions

### Example Approval Email

```
Hello [Your Name],

Congratulations! Your application for Algolia DocSearch has been approved.

Here are your credentials:

Application ID: ABC123DEF456
Search-Only API Key: abcd1234ef5678

Your index name: your-project-prod

Next steps:
1. Add the search component to your documentation site
2. Configure it with the provided credentials
3. We'll automatically crawl and index your site

Documentation: https://docsearch.algolia.com/docs

Best regards,
Algolia Team
```

## Part 3: Integration with Docusaurus

### Step 1: Update docusaurus.config.js

Add Algolia configuration to your main config file:

```javascript
// docusaurus.config.js
module.exports = {
  // ... other config
  themeConfig: {
    // ... other theme config
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_SEARCH_KEY',
      indexName: 'your-project-prod',
      contextualSearch: true,
      externalUrlRegex: 'external\\.com|another-domain\\.fr',
      // Optional: Algolia search parameters
      searchParameters: {
        facetFilters: ['version:latest'],
      },
    },
  },
};
```

### Configuration Options

```javascript
algolia: {
  // Application ID provided by Algolia
  appId: 'YOUR_APP_ID',

  // Public API Key (search-only)
  apiKey: 'YOUR_SEARCH_KEY',

  // Index name provided by Algolia
  indexName: 'your-index-name',

  // Optional: Enable contextual search
  contextualSearch: true,

  // Optional: Regex to identify external URLs
  externalUrlRegex: 'external\\.com',

  // Optional: Search parameters
  searchParameters: {
    facetFilters: ['language:en'],
    attributesToSnippet: ['content:10'],
    snippetEllipsisText: '…',
  },

  // Optional: Placeholder text
  placeholder: 'Search docs',

  // Optional: Disable search input initially
  disableUserPersonalization: false,
}
```

### Step 2: Test the Integration

```bash
npm start
```

Look for the search icon in the navigation bar. Click it and test searching for documentation content.

### Verify Integration

```javascript
// Check browser console
// You should see search requests to Algolia API
// Example: GET https://abc123def456-dsn.algolia.net/1/indexes/your-project-prod/query
```

## Part 4: Advanced Configuration

### Configure Search Behavior

```javascript
// docusaurus.config.js
algolia: {
  appId: 'YOUR_APP_ID',
  apiKey: 'YOUR_SEARCH_KEY',
  indexName: 'your-project-prod',

  // Control facet filters
  searchParameters: {
    facetFilters: [
      'language:en',
      ['docusaurus_tag:docs-default', 'docusaurus_tag:blog']
    ],
    // Show snippet of content
    attributesToSnippet: ['content:15'],
    // Custom snippet ending
    snippetEllipsisText: '...',
    // Number of results per page
    hitsPerPage: 10,
  },

  // Customize placeholder
  placeholder: 'Search documentation...',

  // Trigger behavior
  insights: true,
}
```

### Multiple Versions Search

If you have multiple documentation versions, configure filters:

```javascript
algolia: {
  appId: 'YOUR_APP_ID',
  apiKey: 'YOUR_SEARCH_KEY',
  indexName: 'your-project-prod',

  searchParameters: {
    // Only search latest version
    facetFilters: ['version:latest'],

    // Or allow multiple versions
    facetFilters: [
      ['version:latest', 'version:1.0', 'version:1.1']
    ],
  },
}
```

### Multilingual Search

```javascript
algolia: {
  appId: 'YOUR_APP_ID',
  apiKey: 'YOUR_SEARCH_KEY',
  indexName: 'your-project-prod',

  contextualSearch: true, // Enable language context

  searchParameters: {
    facetFilters: [
      ['language:en', 'language:es', 'language:fr']
    ],
  },
}
```

## Part 5: Managing Your Index

### Monitor Indexing

Visit your Algolia Dashboard:

```
https://www.algolia.com/apps/YOUR_APP_ID
```

Key metrics to monitor:
- **Indexing Status**: Shows crawling progress
- **Record Count**: Total indexed documents
- **Index Size**: Memory usage
- **Last Updated**: Last crawl timestamp

### Manual Indexing

Request immediate reindexing through the DocSearch dashboard:

```bash
# Contact Algolia support for manual indexing
# Or visit: https://docsearch.algolia.com/admin
```

### Crawler Configuration

Docusaurus sites are auto-crawled. For custom sites, provide crawler config:

```json
{
  "index_name": "your-project-prod",
  "start_urls": [
    {
      "url": "https://yourdocs.example.com/docs",
      "selectors_key": "docusaurus"
    }
  ],
  "selectors": {
    "docusaurus": {
      "lvl0": {
        "selector": "header nav a:contains('Docs')",
        "global": true,
        "default_value": "Documentation"
      },
      "lvl1": "main h1",
      "lvl2": "main h2",
      "lvl3": "main h3",
      "lvl4": "main h4",
      "lvl5": "main h5",
      "content": "main p, main li",
      "lang": {
        "selectors": {
          "en": "html[lang=en]",
          "es": "html[lang=es]"
        }
      }
    }
  },
  "strip_chars": " .,;:#",
  "custom_settings": {
    "separatorsToIndex": "_",
    "attributeForDistinct": "url",
    "distinct": true,
    "attributesToRetrieve": ["hierarchy", "content", "anchor", "url"]
  }
}
```

## Part 6: Customizing Search UI

### Custom Search Modal Component

Create a custom search component:

```typescript
// src/theme/SearchBar.tsx
import React, { useEffect } from 'react';
import DocSearch from '@docsearch/react';
import '@docsearch/css';

export default function CustomSearchBar() {
  return (
    <DocSearch
      appId="YOUR_APP_ID"
      apiKey="YOUR_SEARCH_KEY"
      indexName="your-project-prod"
      placeholder="Search documentation..."
      transformItems={(items) => {
        // Transform search results before display
        return items.map((item) => ({
          ...item,
          // Customize how results appear
        }));
      }}
    />
  );
}
```

### Styling Search Results

```css
/* src/css/custom.css */

/* Search input styling */
.DocSearch-Input {
  font-size: 16px;
  color: var(--ifm-color-content);
}

/* Search result item styling */
.DocSearch-Hit {
  padding: 12px 16px;
  border-radius: 4px;
}

.DocSearch-Hit:hover {
  background-color: var(--ifm-color-primary-lightest);
}

/* Search modal styling */
.DocSearch-Modal {
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.15);
}

/* Dark mode adjustments */
[data-theme='dark'] .DocSearch-Modal {
  background: #1a1a1a;
}
```

### Handle Search Events

```typescript
// src/theme/SearchBar.tsx
import React from 'react';
import DocSearch from '@docsearch/react';

export default function SearchBar() {
  return (
    <DocSearch
      appId="YOUR_APP_ID"
      apiKey="YOUR_SEARCH_KEY"
      indexName="your-project-prod"
      onOpen={() => {
        console.log('Search opened');
      }}
      onClose={() => {
        console.log('Search closed');
      }}
      onInput={(event) => {
        console.log('Search input:', event.currentTarget.value);
      }}
    />
  );
}
```

## Part 7: Troubleshooting

### Search Returns No Results

**Possible causes:**
1. Index not yet crawled (takes 24 hours)
2. Content not properly formatted
3. Wrong API credentials

**Solutions:**
```bash
# Verify credentials are correct
# Check if site is publicly accessible
# Request manual reindexing from Algolia
```

### Slow Search Results

**Optimization strategies:**
```javascript
algolia: {
  searchParameters: {
    // Limit facets to reduce processing
    facetFilters: ['version:latest'],
    // Limit results returned
    hitsPerPage: 5,
  },
}
```

### Incorrect Search Ranking

Adjust Algolia ranking settings in dashboard:

```
Custom ranking (Ranking tab) → By attribute value
Ranking formula → Adjust weight of different attributes
```

### Missing Content in Results

Verify crawler selector configuration:

```javascript
// docusaurus.config.js must properly expose content
// through semantic HTML elements
```

## Performance Tips

1. **Use Contextual Search**: Limits results to current language/version
2. **Configure Facet Filters**: Narrows search scope
3. **Optimize Index Size**: Remove unnecessary content from indexing
4. **Cache Results**: Browser caches previous searches
5. **Lazy Load**: Search component loads asynchronously

## Analytics and Insights

Access search analytics in Algolia Dashboard:

- **Popular Searches**: Which terms users search for
- **No Results**: Searches that returned nothing
- **Click-Through Rate**: User engagement with results
- **Conversion Funnel**: Search to page conversion

### Enable Click Analytics

```javascript
algolia: {
  appId: 'YOUR_APP_ID',
  apiKey: 'YOUR_SEARCH_KEY',
  indexName: 'your-project-prod',
  insights: true, // Enable analytics

  searchParameters: {
    clickAnalytics: true,
  },
}
```

## Security Considerations

### API Key Protection

- **Search-Only Key**: Safe to expose publicly (used in browser)
- **Admin Key**: Keep secret, never expose in frontend code
- **Restricted Keys**: Create limited-scope keys for specific operations

### Monitor API Usage

```
Dashboard → Analytics → API calls
- Track search volume
- Identify unusual activity
- Set rate limits if needed
```

## Best Practices

1. **Regular Monitoring**: Check search analytics weekly
2. **Content Updates**: Ensure documentation is crawled after updates
3. **User Feedback**: Use search data to improve documentation
4. **Test Thoroughly**: Verify search in staging before production
5. **Documentation**: Keep track of your configuration changes
6. **Backup Credentials**: Securely store API keys

## Resources

- [Algolia DocSearch](https://docsearch.algolia.com)
- [DocSearch Documentation](https://docsearch.algolia.com/docs)
- [Algolia Dashboard](https://www.algolia.com/apps)
- [Docusaurus Search Integration](https://docusaurus.io/docs/search)
- [Algolia Support](https://support.algolia.com)

## Next Steps

After implementing search:
- Set up CI/CD for automated deployments
- Configure documentation versioning
- Add internationalization support
- Monitor search analytics and user behavior
- Continuously improve documentation based on search patterns

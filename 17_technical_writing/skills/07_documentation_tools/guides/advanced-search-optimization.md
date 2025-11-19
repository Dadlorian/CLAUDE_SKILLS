# Advanced Search Optimization: Algolia Configuration and Tuning

## Table of Contents

1. [Introduction](#introduction)
2. [Algolia Fundamentals](#algolia-fundamentals)
3. [Configuration](#configuration)
4. [Indexing Strategy](#indexing-strategy)
5. [Query Performance](#query-performance)
6. [Ranking and Relevance](#ranking-and-relevance)
7. [Analytics and Monitoring](#analytics-and-monitoring)
8. [Advanced Features](#advanced-features)
9. [Optimization Techniques](#optimization-techniques)
10. [Troubleshooting](#troubleshooting)

## Introduction

Algolia is a powerful hosted search platform that can dramatically improve documentation discoverability. This guide covers advanced configuration, optimization, and best practices for maximum search effectiveness.

### Why Algolia for Documentation

- Real-time indexing updates
- Fast response times (< 100ms)
- Advanced relevance tuning
- Analytics and insights
- Multi-language support
- Typo tolerance
- Faceted search

## Algolia Fundamentals

### Core Concepts

**Index**: A searchable database containing your content
**Record**: Individual items in an index (pages, sections)
**Attributes**: Properties of records (title, content, URL)
**Ranking**: Rules for determining search result relevance
**Analytics**: User behavior and search metrics

### Docusaurus Algolia Integration

```javascript
// docusaurus.config.js
module.exports = {
  themeConfig: {
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_SEARCH_API_KEY',
      indexName: 'your-doc-index',
      contextualSearch: true,
      searchParameters: {
        facetFilters: ['type:doc'],
      },
    },
  },
};
```

## Configuration

### Algolia Account Setup

```bash
# Install Algolia CLI
npm install -g algolia

# Login
algolia auth login

# View applications
algolia applications list

# Create index
algolia indices create --application-id YOUR_APP_ID \
  --name docusaurus
```

### Index Configuration

```python
#!/usr/bin/env python3
"""
Configure Algolia index
"""

import algoliasearch
from algoliasearch.search_client import SearchClient

# Initialize client
client = SearchClient.create('YOUR_APP_ID', 'YOUR_ADMIN_API_KEY')
index = client.init_index('docusaurus')

# Configure index settings
settings = {
    # Searchable attributes
    'searchableAttributes': [
        'title',
        'description',
        'content',
        'keywords',
    ],

    # Attributes for filtering
    'attributesForFaceting': [
        'type',
        'version',
        'language',
        'category',
    ],

    # Ranking strategy
    'ranking': [
        'typo',
        'geo',
        'words',
        'filters',
        'proximity',
        'attribute',
        'exact',
        'custom',
    ],

    # Custom ranking
    'customRanking': [
        'desc(popularity)',
        'asc(date)',
    ],

    # Pagination
    'paginationLimitedTo': 1000,
    'hitsPerPage': 20,

    # Typo tolerance
    'typoTolerance': {
        'enabled': True,
        'minWordSizeForTypos': {
            'oneTypo': 4,
            'twoTypos': 8,
        },
    },

    # Highlighting
    'attributesToHighlight': [
        'title',
        'content',
    ],

    # Snippeting
    'attributesToSnippet': [
        'content:50',
        'description:25',
    ],

    # Distinct
    'distinct': False,

    # Remove words if no results
    'removeWordsIfNoResults': 'lastWords',

    # Query strategy
    'queryType': 'prefixLast',

    # Relevance settings
    'minProximity': 1,
}

index.set_settings(settings)
print('Index configured successfully')
```

## Indexing Strategy

### Content Structure for Indexing

```python
#!/usr/bin/env python3
"""
Structure content for Algolia indexing
"""

def prepare_page_for_indexing(page):
    """
    Prepare a documentation page for Algolia indexing
    """
    import re

    # Extract sections from markdown
    sections = extract_sections(page['content'])

    # Create records for each section
    records = []

    for section in sections:
        record = {
            'objectID': f"{page['id']}#{section['anchor']}",
            'page_id': page['id'],
            'title': section['title'],
            'content': section['content'],
            'url': f"{page['url']}#{section['anchor']}",
            'section': section['title'],
            'type': 'doc',
            'version': page.get('version', '1.0'),
            'language': page.get('language', 'en'),
            'category': page.get('category', ''),
            'keywords': extract_keywords(section['content']),
            'popularity': page.get('views', 0),
            'lastModified': page.get('updated_at'),
            'author': page.get('author', ''),
        }
        records.append(record)

    return records

def extract_sections(markdown_content):
    """
    Extract sections from markdown content
    """
    import re

    sections = []
    current_section = None

    # Split by headings
    lines = markdown_content.split('\n')

    for line in lines:
        # Detect headings
        match = re.match(r'^(#{1,3})\s+(.+)$', line)
        if match:
            if current_section:
                sections.append(current_section)

            level = len(match.group(1))
            title = match.group(2)
            anchor = title.lower().replace(' ', '-').replace('/', '-')

            current_section = {
                'level': level,
                'title': title,
                'anchor': anchor,
                'content': '',
            }
        elif current_section:
            current_section['content'] += line + '\n'

    if current_section:
        sections.append(current_section)

    return sections

def extract_keywords(content):
    """
    Extract keywords from content
    """
    import re
    from collections import Counter

    # Remove code blocks
    content = re.sub(r'```[\s\S]*?```', '', content)

    # Extract words
    words = re.findall(r'\b\w{4,}\b', content.lower())

    # Filter common words
    stop_words = {
        'the', 'this', 'that', 'with', 'from', 'have', 'will',
        'your', 'their', 'which', 'when', 'where', 'what', 'how',
    }

    keywords = [w for w in words if w not in stop_words]

    # Return top 10
    return [word for word, _ in Counter(keywords).most_common(10)]

# Example usage
page = {
    'id': 'getting-started',
    'url': '/docs/getting-started',
    'content': '''
# Getting Started
## Installation
Install the package using npm...
## Configuration
Configure the settings...
''',
    'version': '2.0',
    'category': 'guides',
    'views': 1500,
}

records = prepare_page_for_indexing(page)
for record in records:
    print(record)
```

### Batch Indexing

```python
#!/usr/bin/env python3
"""
Batch index documents to Algolia
"""

import algoliasearch
from algoliasearch.search_client import SearchClient

def batch_index_documents(client, index_name, records, batch_size=1000):
    """
    Index documents in batches
    """
    index = client.init_index(index_name)

    total = len(records)
    batches = [
        records[i:i + batch_size]
        for i in range(0, total, batch_size)
    ]

    for i, batch in enumerate(batches):
        print(f"Indexing batch {i+1}/{len(batches)} ({len(batch)} records)")

        # Save objects
        response = index.save_objects(batch, {'autoGenerateObjectIDIfNotExist': True})

        # Wait for task
        index.wait_task(response['taskID'])

    print(f"Indexed {total} records successfully")

# Usage
client = SearchClient.create('YOUR_APP_ID', 'YOUR_ADMIN_API_KEY')

records = [
    {
        'title': 'Getting Started',
        'content': 'How to get started with...',
        'url': '/docs/getting-started',
        'type': 'doc',
    },
    # ... more records
]

batch_index_documents(client, 'docusaurus', records)
```

## Query Performance

### Query Optimization

```javascript
// React component with optimized Algolia queries

import React, {useState, useCallback, useMemo} from 'react';
import algoliasearch from 'algoliasearch/lite';

const searchClient = algoliasearch('YOUR_APP_ID', 'YOUR_SEARCH_API_KEY');

export function SearchComponent() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  // Debounced search
  const debouncedSearch = useCallback(
    debounce(async (searchQuery) => {
      if (!searchQuery.trim()) {
        setResults([]);
        return;
      }

      setLoading(true);

      try {
        const index = searchClient.initIndex('docusaurus');
        const {hits} = await index.search(searchQuery, {
          // Query parameters
          hitsPerPage: 10,
          facetFilters: ['type:doc'],
          attributesToRetrieve: [
            'title',
            'content',
            'url',
            'section',
          ],
          attributesToHighlight: ['title', 'content'],

          // Advanced options
          analytics: true,
          typoTolerance: 'min',
          minProximity: 2,

          // Facets
          facets: ['category', 'version'],
          maxFacetHits: 10,

          // Personalization
          personalizationImpact: 100,
          personalizationFilters: ['user_id:123'],
        });

        setResults(hits);
      } catch (error) {
        console.error('Search failed:', error);
      } finally {
        setLoading(false);
      }
    }, 300),
    [],
  );

  const handleInputChange = useCallback((e) => {
    const value = e.target.value;
    setQuery(value);
    debouncedSearch(value);
  }, [debouncedSearch]);

  return (
    <div>
      <input
        type="search"
        value={query}
        onChange={handleInputChange}
        placeholder="Search documentation..."
      />

      {loading && <div>Loading...</div>}

      <ul>
        {results.map((hit) => (
          <li key={hit.objectID}>
            <a href={hit.url}>{hit.title}</a>
            <p>{hit.content}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

function debounce(fn, delay) {
  let timeoutId;
  return function debounced(...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}
```

## Ranking and Relevance

### Custom Ranking Rules

```python
#!/usr/bin/env python3
"""
Configure custom ranking rules
"""

import algoliasearch

client = algoliasearch.search_client.SearchClient.create(
    'YOUR_APP_ID',
    'YOUR_ADMIN_API_KEY'
)
index = client.init_index('docusaurus')

# Define ranking strategy
settings = {
    'ranking': [
        'typo',           # Typo-tolerance first
        'geo',            # Geographic relevance
        'words',          # Word match quality
        'filters',        # Applied filters
        'proximity',      # Word proximity
        'attribute',      # Attribute importance
        'exact',          # Exact match
        'custom',         # Custom ranking
    ],

    'customRanking': [
        'desc(popularity)',    # More popular first
        'asc(date)',          # Newer content first
        'desc(views)',        # More viewed first
        'asc(doc_depth)',     # Shallower docs first
    ],

    # Attribute importance
    'attributeWeights': {
        'title': 100,
        'keywords': 50,
        'content': 10,
        'description': 30,
    },

    # Replicas for different sort orders
    'replicas': [
        'docusaurus-by-popularity',
        'docusaurus-by-date',
    ],
}

# Apply settings
index.set_settings(settings)

# Create replica indexes
popularity_index = client.init_index('docusaurus-by-popularity')
popularity_index.set_settings({
    'ranking': [
        'desc(popularity)',
        'typo',
        'geo',
        'words',
    ],
})

date_index = client.init_index('docusaurus-by-date')
date_index.set_settings({
    'ranking': [
        'desc(date)',
        'typo',
        'geo',
        'words',
    ],
})
```

## Analytics and Monitoring

### Tracking Search Analytics

```javascript
// Track search events with Algolia Analytics

import algoliasearch from 'algoliasearch/lite';

const searchClient = algoliasearch('YOUR_APP_ID', 'YOUR_SEARCH_API_KEY');

// Enable analytics
const index = searchClient.initIndex('docusaurus');

async function trackSearch(query, resultCount) {
  // This is automatically tracked if analytics is enabled
  const result = await index.search(query, {
    analytics: true, // Enable analytics
    clickAnalytics: true, // Track clicks
  });

  return result;
}

// Track conversions
function trackConversion(queryID, objectID) {
  // Algolia SDK tracks this automatically
  // But you can also track manually via API
  fetch('https://insights.algolia.io/1/events', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Algolia-Application-Id': 'YOUR_APP_ID',
      'X-Algolia-API-Key': 'YOUR_API_KEY',
    },
    body: JSON.stringify({
      events: [
        {
          eventType: 'click',
          eventName: 'doc-view',
          queryID: queryID,
          objectID: objectID,
          position: 1,
          timestamp: Date.now(),
        },
      ],
    }),
  });
}
```

### Performance Metrics

```python
#!/usr/bin/env python3
"""
Monitor Algolia performance metrics
"""

import algoliasearch
from datetime import datetime, timedelta

client = algoliasearch.search_client.SearchClient.create(
    'YOUR_APP_ID',
    'YOUR_ADMIN_API_KEY'
)

index = client.init_index('docusaurus')

def get_index_stats():
    """Get index statistics"""
    stats = index.get_settings()

    return {
        'entries': stats.get('entries', 0),
        'data_size': stats.get('dataSize', 0),
        'file_size': stats.get('fileSize', 0),
    }

def get_search_analytics(days=7):
    """Get search analytics for the past N days"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Analytics data can be accessed via Algolia dashboard
    # or via API for advanced usage

    metrics = {
        'period': f'{start_date.date()} to {end_date.date()}',
        'searches': 0,
        'searches_with_results': 0,
        'searches_without_results': 0,
        'average_result_count': 0,
        'click_through_rate': 0,
    }

    return metrics

def generate_performance_report():
    """Generate comprehensive performance report"""
    stats = get_index_stats()
    analytics = get_search_analytics()

    report = f"""
Search Performance Report
========================

Index Statistics
- Entries: {stats['entries']:,}
- Data Size: {stats['data_size'] / 1024 / 1024:.2f} MB
- File Size: {stats['file_size'] / 1024 / 1024:.2f} MB

Search Analytics (Last 7 Days)
- Total Searches: {analytics['searches']:,}
- With Results: {analytics['searches_with_results']:,}
- Without Results: {analytics['searches_without_results']:,}
- Avg Results: {analytics['average_result_count']:.1f}
- CTR: {analytics['click_through_rate']:.1%}
"""

    return report

# Print report
print(generate_performance_report())
```

## Advanced Features

### Faceted Search

```javascript
// Implement faceted search

async function searchWithFacets(query) {
  const index = searchClient.initIndex('docusaurus');

  const results = await index.search(query, {
    hitsPerPage: 20,
    facets: ['category', 'version', 'language'],
    facetFilters: [
      'type:doc',
      ['version:2.0', 'version:3.0'], // OR condition
      'language:en',
    ],
  });

  return {
    hits: results.hits,
    facets: results.facets,
    nbHits: results.nbHits,
  };
}

// Handle facet filtering
function handleFacetClick(facetName, facetValue) {
  // Add/remove facet filter
  const newFilters = [...currentFilters];

  const filterExists = newFilters.find(
    (f) => f.name === facetName && f.value === facetValue
  );

  if (filterExists) {
    newFilters.splice(newFilters.indexOf(filterExists), 1);
  } else {
    newFilters.push({name: facetName, value: facetValue});
  }

  // Re-search with new filters
  performSearch(query, newFilters);
}
```

### Autocomplete

```javascript
// Implement autocomplete with debouncing

import {autocomplete} from '@algolia/autocomplete-js';

autocomplete({
  container: '#autocomplete',
  openOnFocus: true,
  getSources() {
    return [
      {
        sourceId: 'queries',
        getItems({query}) {
          return getAlgoliaResults({
            searchClient,
            queries: [
              {
                indexName: 'docusaurus',
                query,
                params: {
                  hitsPerPage: 8,
                  attributesToSnippet: ['content:15'],
                },
              },
            ],
          });
        },
        templates: {
          item({item, components, html}) {
            return html`
              <a href="${item.url}" class="aa-ItemLink">
                <div class="aa-ItemContent">
                  <div class="aa-ItemTitle">
                    ${components.Highlight({hit: item, attribute: 'title'})}
                  </div>
                  <div class="aa-ItemDescription">
                    ${components.Snippet({hit: item, attribute: 'content'})}
                  </div>
                </div>
              </a>
            `;
          },
        },
      },
    ];
  },
});
```

## Optimization Techniques

### Synonym Management

```python
#!/usr/bin/env python3
"""
Configure search synonyms
"""

import algoliasearch

client = algoliasearch.search_client.SearchClient.create(
    'YOUR_APP_ID',
    'YOUR_ADMIN_API_KEY'
)
index = client.init_index('docusaurus')

# Define synonyms
synonyms = [
    {
        'objectID': '1',
        'type': 'synonym',
        'synonyms': ['quick', 'fast', 'rapid'],
    },
    {
        'objectID': '2',
        'type': 'onewaysynonym',
        'input': 'api',
        'synonyms': ['application programming interface'],
    },
    {
        'objectID': '3',
        'type': 'altcorrection1',
        'word': 'installed',
        'corrections': ['installed', 'install'],
    },
]

# Save synonyms
index.save_synonyms(synonyms)

# Alternatively, define in settings
settings = {
    'synonyms': [
        ['quick', 'fast'],
        ['api', 'application programming interface'],
    ],
}

index.set_settings(settings)
```

### Stopwords Configuration

```python
# Configure stopwords (words to ignore in search)

settings = {
    'disableExactOnAttributes': ['content'],
    'disablePrefixOnAttributes': ['content'],
    'separatorsToIndex': '_-',
    'optionalWords': [
        'a', 'an', 'the',
        'or', 'and',
        'to', 'for',
    ],
}

index.set_settings(settings)
```

## Troubleshooting

### Common Issues and Solutions

```python
#!/usr/bin/env python3
"""
Troubleshoot Algolia search issues
"""

class SearchTroubleshooter:
    def __init__(self, client, index_name):
        self.client = client
        self.index = client.init_index(index_name)

    def diagnose_poor_results(self, query):
        """Diagnose why a query returns poor results"""
        diagnostics = {}

        # Check index size
        settings = self.index.get_settings()
        diagnostics['index_size'] = settings.get('entries', 0)

        if diagnostics['index_size'] == 0:
            print("ERROR: Index is empty. Check your indexing process.")

        # Check query parsing
        try:
            results = self.index.search(query)
            diagnostics['results_count'] = results['nbHits']
            diagnostics['query_time'] = results['processingTimeMS']
        except Exception as e:
            diagnostics['query_error'] = str(e)

        # Check ranking settings
        ranking = settings.get('ranking', [])
        diagnostics['ranking_strategy'] = ranking

        # Suggestions
        diagnostics['suggestions'] = []
        if diagnostics['results_count'] == 0:
            diagnostics['suggestions'].append(
                'Try broadening search query'
            )
            diagnostics['suggestions'].append(
                'Check if content is properly indexed'
            )
            diagnostics['suggestions'].append(
                'Review ranking configuration'
            )

        return diagnostics

# Usage
troubleshooter = SearchTroubleshooter(client, 'docusaurus')
diagnostics = troubleshooter.diagnose_poor_results('python tutorial')
print(diagnostics)
```

## Conclusion

Advanced Algolia search optimization provides:
- Relevance tuning for better results
- Analytics for user insights
- Performance optimization
- Advanced features (facets, autocomplete)
- Extensive customization

Key takeaways:
- Proper indexing strategy is critical
- Custom ranking improves relevance
- Monitor analytics for insights
- Test different configurations
- Iterate based on user behavior


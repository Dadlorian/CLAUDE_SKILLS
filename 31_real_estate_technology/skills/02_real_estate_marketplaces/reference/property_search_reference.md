# Property Search Reference

## Quick Reference for Real Estate Search Implementation

### Elasticsearch Schema for Properties

```json
{
  "mappings": {
    "properties": {
      "property_id": { "type": "keyword" },
      "mls_number": { "type": "keyword" },
      "status": { "type": "keyword" },
      "address": {
        "type": "text",
        "fields": {
          "keyword": { "type": "keyword" }
        }
      },
      "city": { "type": "keyword" },
      "state": { "type": "keyword" },
      "zip": { "type": "keyword" },
      "location": { "type": "geo_point" },
      "price": { "type": "integer" },
      "bedrooms": { "type": "integer" },
      "bathrooms": { "type": "float" },
      "sqft": { "type": "integer" },
      "lot_size": { "type": "integer" },
      "year_built": { "type": "integer" },
      "property_type": { "type": "keyword" },
      "listing_date": { "type": "date" },
      "updated_at": { "type": "date" },
      "description": { "type": "text" },
      "features": { "type": "keyword" },
      "photos": {
        "type": "nested",
        "properties": {
          "url": { "type": "keyword" },
          "order": { "type": "integer" }
        }
      },
      "agent": {
        "properties": {
          "id": { "type": "keyword" },
          "name": { "type": "text" },
          "phone": { "type": "keyword" }
        }
      },
      "school_scores": {
        "properties": {
          "elementary": { "type": "integer" },
          "middle": { "type": "integer" },
          "high": { "type": "integer" }
        }
      }
    }
  }
}
```

### Common Search Queries

#### Basic Text Search
```json
{
  "query": {
    "multi_match": {
      "query": "downtown condo",
      "fields": ["address^3", "city^2", "description"]
    }
  }
}
```

#### Location-Based Search (Bounding Box)
```json
{
  "query": {
    "bool": {
      "must": { "match_all": {} },
      "filter": {
        "geo_bounding_box": {
          "location": {
            "top_left": { "lat": 40.8, "lon": -74.0 },
            "bottom_right": { "lat": 40.7, "lon": -73.9 }
          }
        }
      }
    }
  }
}
```

#### Radius Search
```json
{
  "query": {
    "bool": {
      "must": { "match_all": {} },
      "filter": {
        "geo_distance": {
          "distance": "5mi",
          "location": { "lat": 40.73, "lon": -73.93 }
        }
      }
    }
  }
}
```

#### Faceted Search with Filters
```json
{
  "query": {
    "bool": {
      "must": [
        { "term": { "status": "active" } }
      ],
      "filter": [
        { "range": { "price": { "gte": 300000, "lte": 500000 } } },
        { "range": { "bedrooms": { "gte": 3 } } },
        { "range": { "bathrooms": { "gte": 2 } } },
        { "term": { "property_type": "single_family" } }
      ]
    }
  },
  "sort": [
    { "listing_date": "desc" }
  ],
  "from": 0,
  "size": 20
}
```

#### Search with Aggregations
```json
{
  "query": { "match_all": {} },
  "aggs": {
    "by_property_type": {
      "terms": { "field": "property_type" }
    },
    "price_ranges": {
      "range": {
        "field": "price",
        "ranges": [
          { "to": 200000 },
          { "from": 200000, "to": 400000 },
          { "from": 400000, "to": 600000 },
          { "from": 600000 }
        ]
      }
    },
    "avg_price": {
      "avg": { "field": "price" }
    }
  }
}
```

### Search Ranking Formulas

#### Relevance Scoring
```json
{
  "query": {
    "function_score": {
      "query": { "match": { "description": "luxury waterfront" } },
      "functions": [
        {
          "filter": { "range": { "listing_date": { "gte": "now-7d" } } },
          "weight": 2
        },
        {
          "gauss": {
            "price": {
              "origin": "500000",
              "scale": "100000"
            }
          }
        },
        {
          "field_value_factor": {
            "field": "photos.count",
            "modifier": "log1p",
            "factor": 0.5
          }
        }
      ],
      "score_mode": "multiply",
      "boost_mode": "multiply"
    }
  }
}
```

### Filter Types

| Filter | Use Case | Example |
|--------|----------|---------|
| term | Exact match | `{ "term": { "city": "Austin" } }` |
| terms | Multiple values | `{ "terms": { "property_type": ["condo", "townhouse"] } }` |
| range | Numeric/date ranges | `{ "range": { "price": { "gte": 200000 } } }` |
| exists | Field has value | `{ "exists": { "field": "pool" } }` |
| geo_distance | Radius search | `{ "geo_distance": { "distance": "10km", "location": {...} } }` |
| geo_bounding_box | Map viewport | `{ "geo_bounding_box": { "location": {...} } }` |

### Common Property Types

```javascript
const PROPERTY_TYPES = {
  RESIDENTIAL: {
    SINGLE_FAMILY: 'single_family',
    CONDO: 'condo',
    TOWNHOUSE: 'townhouse',
    MULTI_FAMILY: 'multi_family',
    MANUFACTURED: 'manufactured',
    LAND: 'land'
  },
  COMMERCIAL: {
    OFFICE: 'office',
    RETAIL: 'retail',
    INDUSTRIAL: 'industrial',
    MIXED_USE: 'mixed_use',
    SPECIAL_PURPOSE: 'special_purpose'
  }
};
```

### Status Codes

```javascript
const LISTING_STATUS = {
  ACTIVE: 'active',
  PENDING: 'pending',
  UNDER_CONTRACT: 'under_contract',
  SOLD: 'sold',
  EXPIRED: 'expired',
  WITHDRAWN: 'withdrawn',
  COMING_SOON: 'coming_soon',
  TEMPORARILY_OFF_MARKET: 'temp_off_market'
};
```

### Search Performance Tips

1. **Use Filters Instead of Queries**
   - Filters are cached and faster
   - Use for exact matches, ranges

2. **Limit Result Size**
   - Default to 20-50 results
   - Use pagination (from/size)
   - Consider search_after for deep pagination

3. **Optimize Mappings**
   - Use keyword for exact match fields
   - Disable _source for large documents
   - Use doc_values for sorting/aggregations

4. **Caching Strategy**
   ```javascript
   // Cache popular searches
   const cacheKey = `search:${JSON.stringify(query)}`;
   let results = await redis.get(cacheKey);
   if (!results) {
     results = await elasticsearch.search(query);
     await redis.setex(cacheKey, 300, JSON.stringify(results)); // 5min TTL
   }
   ```

### Autocomplete Implementation

#### Index Configuration
```json
{
  "settings": {
    "analysis": {
      "analyzer": {
        "autocomplete": {
          "tokenizer": "autocomplete",
          "filter": ["lowercase"]
        },
        "autocomplete_search": {
          "tokenizer": "lowercase"
        }
      },
      "tokenizer": {
        "autocomplete": {
          "type": "edge_ngram",
          "min_gram": 2,
          "max_gram": 10,
          "token_chars": ["letter", "digit"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "city": {
        "type": "text",
        "analyzer": "autocomplete",
        "search_analyzer": "autocomplete_search"
      }
    }
  }
}
```

#### Autocomplete Query
```json
{
  "suggest": {
    "location-suggest": {
      "prefix": "san",
      "completion": {
        "field": "suggest",
        "size": 10,
        "fuzzy": {
          "fuzziness": "AUTO"
        }
      }
    }
  }
}
```

### Map-Based Search

#### Get Properties in Map Viewport
```javascript
function buildMapViewportQuery(bounds) {
  return {
    query: {
      bool: {
        must: [
          { term: { status: 'active' } }
        ],
        filter: [
          {
            geo_bounding_box: {
              location: {
                top_left: {
                  lat: bounds.north,
                  lon: bounds.west
                },
                bottom_right: {
                  lat: bounds.south,
                  lon: bounds.east
                }
              }
            }
          }
        ]
      }
    },
    size: 500, // Limit for map markers
    _source: ['property_id', 'location', 'price', 'bedrooms', 'photo_url']
  };
}
```

### Saved Search Alerts

```javascript
// Store user search criteria
const savedSearch = {
  user_id: '12345',
  name: 'My Dream Home',
  criteria: {
    location: { lat: 40.7, lon: -73.9, radius: '10mi' },
    price: { min: 400000, max: 600000 },
    bedrooms: { min: 3 },
    property_type: ['single_family', 'townhouse']
  },
  frequency: 'daily', // instant, daily, weekly
  created_at: '2025-01-15T00:00:00Z'
};

// Query for new matches
function findNewMatches(savedSearch, since) {
  return {
    query: {
      bool: {
        must: [
          { term: { status: 'active' } },
          { range: { listing_date: { gte: since } } }
        ],
        filter: buildFiltersFromCriteria(savedSearch.criteria)
      }
    }
  };
}
```

### Search Analytics Tracking

```javascript
// Track search events
const searchEvent = {
  event_type: 'search',
  user_id: '12345',
  session_id: 'abc-def-ghi',
  timestamp: new Date(),
  search_params: {
    query: 'downtown condo',
    filters: {
      price_min: 300000,
      bedrooms: 2
    },
    location: { city: 'Austin', state: 'TX' }
  },
  results_count: 47,
  results_shown: 20
};

// Track clicks
const clickEvent = {
  event_type: 'property_click',
  user_id: '12345',
  session_id: 'abc-def-ghi',
  property_id: 'prop-789',
  position: 3, // Position in search results
  timestamp: new Date()
};
```

### Performance Benchmarks

| Metric | Target | Notes |
|--------|--------|-------|
| Search latency | < 100ms | 95th percentile |
| Autocomplete | < 50ms | 95th percentile |
| Index update | < 5min | From MLS to searchable |
| Map search | < 200ms | For 500 markers |
| Aggregations | < 150ms | With results |

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Slow searches | Large result sets | Use pagination, add filters |
| Inaccurate results | Poor relevance tuning | Adjust boost values, use function_score |
| Memory issues | Too many aggregations | Limit agg size, use sampling |
| Stale results | Infrequent indexing | Increase sync frequency, use refresh API |
| Missing results | Incorrect mapping | Review field types, re-index |

## See Also
- mls_reso_standards.md
- listing_syndication_reference.md
- elasticsearch_setup.md

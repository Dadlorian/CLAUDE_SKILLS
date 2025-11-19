# Property Search Optimization Pattern

**Version:** 2.5
**Last Updated:** 2025-01-15
**Status:** Active Standard
**References:** Elasticsearch, MongoDB Geospatial, Zillow Search Architecture, Redfin Engineering Blog

## Table of Contents

1. [Overview](#overview)
2. [Elasticsearch Configuration](#elasticsearch-configuration)
3. [Geospatial Search Patterns](#geospatial-search-patterns)
4. [Faceted Search Implementation](#faceted-search-implementation)
5. [Autocomplete and Typeahead](#autocomplete-and-typeahead)
6. [Search Ranking Algorithms](#search-ranking-algorithms)
7. [Performance Optimization](#performance-optimization)
8. [Image Search and Visual Similarity](#image-search-and-visual-similarity)

## Overview

Property search is the most critical feature of any PropTech platform. Users expect Google-quality search: fast (<200ms), relevant, and intuitive.

### Search Requirements

**Performance Targets:**
- **Response Time:** <200ms (P95)
- **Availability:** 99.9%
- **Scalability:** Handle 10,000+ QPS
- **Relevance:** >90% user satisfaction

**Search Features:**
- Full-text search (property name, description, amenities)
- Geospatial search (near location, within radius, bounding box)
- Faceted filtering (price, bedrooms, bathrooms, amenities)
- Autocomplete/typeahead
- Fuzzy matching (typo tolerance)
- Relevance ranking
- Personalization

## Elasticsearch Configuration

### Index Mapping

```json
{
  "mappings": {
    "properties": {
      "property_id": {
        "type": "keyword"
      },
      "property_name": {
        "type": "text",
        "analyzer": "property_name_analyzer",
        "fields": {
          "keyword": {
            "type": "keyword"
          },
          "completion": {
            "type": "completion"
          }
        }
      },
      "description": {
        "type": "text",
        "analyzer": "standard"
      },
      "property_type": {
        "type": "keyword"
      },
      "location": {
        "type": "geo_point"
      },
      "address": {
        "type": "object",
        "properties": {
          "street": {"type": "text"},
          "city": {"type": "keyword"},
          "state": {"type": "keyword"},
          "postal_code": {"type": "keyword"},
          "country": {"type": "keyword"}
        }
      },
      "monthly_rent_amount": {
        "type": "integer"
      },
      "bedrooms": {
        "type": "integer"
      },
      "bathrooms": {
        "type": "float"
      },
      "square_feet": {
        "type": "integer"
      },
      "amenities": {
        "type": "keyword"
      },
      "is_available": {
        "type": "boolean"
      },
      "available_date": {
        "type": "date"
      },
      "year_built": {
        "type": "integer"
      },
      "listing_date": {
        "type": "date"
      },
      "popularity_score": {
        "type": "float"
      },
      "images": {
        "type": "nested",
        "properties": {
          "url": {"type": "keyword"},
          "is_primary": {"type": "boolean"}
        }
      }
    }
  },
  "settings": {
    "index": {
      "number_of_shards": 3,
      "number_of_replicas": 2,
      "refresh_interval": "5s"
    },
    "analysis": {
      "analyzer": {
        "property_name_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "asciifolding",
            "property_synonym"
          ]
        }
      },
      "filter": {
        "property_synonym": {
          "type": "synonym",
          "synonyms": [
            "apt, apartment",
            "condo, condominium",
            "loft, studio",
            "pool, swimming pool"
          ]
        }
      }
    }
  }
}
```

### Search Query DSL

```python
from elasticsearch import Elasticsearch

class PropertySearch:
    """
    Elasticsearch-powered property search
    """

    def __init__(self, es_client: Elasticsearch):
        self.es = es_client
        self.index = "properties"

    def search_properties(self, query_params):
        """
        Search properties with multiple filters
        """
        # Build Elasticsearch query
        query = {
            "bool": {
                "must": [],
                "filter": [],
                "should": []
            }
        }

        # Text search
        if query_params.get("search_query"):
            query["bool"]["must"].append({
                "multi_match": {
                    "query": query_params["search_query"],
                    "fields": [
                        "property_name^3",  # 3x boost
                        "description^2",
                        "address.street",
                        "address.city"
                    ],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            })

        # Geospatial filter
        if query_params.get("location") and query_params.get("radius"):
            query["bool"]["filter"].append({
                "geo_distance": {
                    "distance": query_params["radius"],
                    "location": {
                        "lat": query_params["location"]["lat"],
                        "lon": query_params["location"]["lon"]
                    }
                }
            })

        # Price range filter
        if query_params.get("min_price") or query_params.get("max_price"):
            price_filter = {"range": {"monthly_rent_amount": {}}}
            if query_params.get("min_price"):
                price_filter["range"]["monthly_rent_amount"]["gte"] = query_params["min_price"]
            if query_params.get("max_price"):
                price_filter["range"]["monthly_rent_amount"]["lte"] = query_params["max_price"]
            query["bool"]["filter"].append(price_filter)

        # Bedrooms filter
        if query_params.get("bedrooms"):
            query["bool"]["filter"].append({
                "term": {"bedrooms": query_params["bedrooms"]}
            })

        # Bathrooms filter
        if query_params.get("min_bathrooms"):
            query["bool"]["filter"].append({
                "range": {
                    "bathrooms": {
                        "gte": query_params["min_bathrooms"]
                    }
                }
            })

        # Amenities filter
        if query_params.get("amenities"):
            for amenity in query_params["amenities"]:
                query["bool"]["filter"].append({
                    "term": {"amenities": amenity}
                })

        # Availability filter
        query["bool"]["filter"].append({"term": {"is_available": True}})

        # Execute search
        response = self.es.search(
            index=self.index,
            body={
                "query": query,
                "sort": self.build_sort_criteria(query_params.get("sort")),
                "from": query_params.get("offset", 0),
                "size": query_params.get("limit", 20),
                "aggs": self.build_aggregations()
            }
        )

        # Parse results
        return self.parse_search_results(response)

    def build_sort_criteria(self, sort_param):
        """
        Build sort criteria
        """
        sort_options = {
            "relevance": ["_score"],
            "price_asc": [{"monthly_rent_amount": "asc"}],
            "price_desc": [{"monthly_rent_amount": "desc"}],
            "newest": [{"listing_date": "desc"}],
            "bedrooms": [{"bedrooms": "desc"}]
        }

        return sort_options.get(sort_param, ["_score"])

    def build_aggregations(self):
        """
        Build facet aggregations
        """
        return {
            "price_ranges": {
                "range": {
                    "field": "monthly_rent_amount",
                    "ranges": [
                        {"to": 1000},
                        {"from": 1000, "to": 2000},
                        {"from": 2000, "to": 3000},
                        {"from": 3000}
                    ]
                }
            },
            "bedrooms": {
                "terms": {
                    "field": "bedrooms",
                    "size": 10
                }
            },
            "property_types": {
                "terms": {
                    "field": "property_type",
                    "size": 10
                }
            },
            "amenities": {
                "terms": {
                    "field": "amenities",
                    "size": 20
                }
            },
            "cities": {
                "terms": {
                    "field": "address.city",
                    "size": 50
                }
            }
        }

    def parse_search_results(self, response):
        """
        Parse Elasticsearch response
        """
        return {
            "total": response["hits"]["total"]["value"],
            "properties": [
                hit["_source"] for hit in response["hits"]["hits"]
            ],
            "facets": {
                "price_ranges": response["aggregations"]["price_ranges"]["buckets"],
                "bedrooms": response["aggregations"]["bedrooms"]["buckets"],
                "property_types": response["aggregations"]["property_types"]["buckets"],
                "amenities": response["aggregations"]["amenities"]["buckets"],
                "cities": response["aggregations"]["cities"]["buckets"]
            }
        }
```

## Geospatial Search Patterns

### Radius Search

```python
def search_properties_near_location(self, lat, lon, radius_miles):
    """
    Search properties within radius of location
    """
    query = {
        "bool": {
            "filter": [
                {
                    "geo_distance": {
                        "distance": f"{radius_miles}mi",
                        "location": {
                            "lat": lat,
                            "lon": lon
                        }
                    }
                },
                {"term": {"is_available": True}}
            ]
        }
    }

    response = self.es.search(
        index=self.index,
        body={
            "query": query,
            "sort": [
                {
                    "_geo_distance": {
                        "location": {
                            "lat": lat,
                            "lon": lon
                        },
                        "order": "asc",
                        "unit": "mi"
                    }
                }
            ]
        }
    )

    return self.parse_search_results(response)
```

### Bounding Box Search

```python
def search_properties_in_bounding_box(self, top_left, bottom_right):
    """
    Search properties within bounding box (map viewport)

    Args:
        top_left: {"lat": 37.8, "lon": -122.5}
        bottom_right: {"lat": 37.7, "lon": -122.4}
    """
    query = {
        "bool": {
            "filter": [
                {
                    "geo_bounding_box": {
                        "location": {
                            "top_left": top_left,
                            "bottom_right": bottom_right
                        }
                    }
                }
            ]
        }
    }

    response = self.es.search(
        index=self.index,
        body={"query": query}
    )

    return self.parse_search_results(response)
```

### PostGIS Alternative

```sql
-- PostgreSQL with PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Add geometry column
ALTER TABLE properties ADD COLUMN location GEOMETRY(Point, 4326);

-- Create spatial index
CREATE INDEX idx_properties_location ON properties USING GIST(location);

-- Radius search (5 mile radius)
SELECT
    property_id,
    property_name,
    ST_Distance(
        location::geography,
        ST_MakePoint(-122.419, 37.775)::geography
    ) / 1609.34 AS distance_miles
FROM properties
WHERE ST_DWithin(
    location::geography,
    ST_MakePoint(-122.419, 37.775)::geography,
    5 * 1609.34  -- 5 miles in meters
)
ORDER BY distance_miles ASC;

-- Bounding box search
SELECT * FROM properties
WHERE location && ST_MakeEnvelope(-122.5, 37.7, -122.4, 37.8, 4326);
```

## Faceted Search Implementation

### Dynamic Facets

```python
class FacetedSearch:
    """
    Faceted search with dynamic filter generation
    """

    def search_with_facets(self, query_text, selected_facets):
        """
        Search with faceted filters

        Args:
            query_text: "2 bedroom apartment downtown"
            selected_facets: {
                "bedrooms": [2],
                "amenities": ["pool", "gym"],
                "price_range": {"min": 2000, "max": 3000}
            }
        """
        # Build query with selected facets
        query = self.build_faceted_query(query_text, selected_facets)

        # Execute search
        response = self.es.search(
            index="properties",
            body={
                "query": query,
                "aggs": self.build_facet_aggregations(selected_facets)
            }
        )

        # Parse results and facets
        results = self.parse_search_results(response)

        # Add facet counts
        results["facets"] = self.parse_facets(response["aggregations"], selected_facets)

        return results

    def parse_facets(self, aggregations, selected_facets):
        """
        Parse facets with counts and selection state
        """
        facets = {
            "bedrooms": [
                {
                    "value": bucket["key"],
                    "count": bucket["doc_count"],
                    "selected": bucket["key"] in selected_facets.get("bedrooms", [])
                }
                for bucket in aggregations["bedrooms"]["buckets"]
            ],
            "amenities": [
                {
                    "value": bucket["key"],
                    "count": bucket["doc_count"],
                    "selected": bucket["key"] in selected_facets.get("amenities", [])
                }
                for bucket in aggregations["amenities"]["buckets"]
            ]
        }

        return facets
```

## Autocomplete and Typeahead

### Completion Suggester

```python
def autocomplete(self, prefix):
    """
    Autocomplete property names, cities, neighborhoods
    """
    response = self.es.search(
        index=self.index,
        body={
            "suggest": {
                "property_suggest": {
                    "prefix": prefix,
                    "completion": {
                        "field": "property_name.completion",
                        "size": 10,
                        "fuzzy": {
                            "fuzziness": "AUTO"
                        }
                    }
                },
                "city_suggest": {
                    "prefix": prefix,
                    "completion": {
                        "field": "address.city.completion",
                        "size": 5
                    }
                }
            }
        }
    )

    # Parse suggestions
    suggestions = []

    # Property suggestions
    for option in response["suggest"]["property_suggest"][0]["options"]:
        suggestions.append({
            "type": "property",
            "text": option["text"],
            "property_id": option["_source"]["property_id"]
        })

    # City suggestions
    for option in response["suggest"]["city_suggest"][0]["options"]:
        suggestions.append({
            "type": "city",
            "text": option["text"]
        })

    return suggestions
```

### Prefix Search (Alternative)

```python
def typeahead_search(self, prefix):
    """
    Fast typeahead using prefix query
    """
    query = {
        "bool": {
            "should": [
                {
                    "prefix": {
                        "property_name.keyword": {
                            "value": prefix,
                            "boost": 3.0
                        }
                    }
                },
                {
                    "prefix": {
                        "address.city": {
                            "value": prefix,
                            "boost": 2.0
                        }
                    }
                },
                {
                    "match_phrase_prefix": {
                        "description": {
                            "query": prefix
                        }
                    }
                }
            ]
        }
    }

    response = self.es.search(
        index=self.index,
        body={
            "query": query,
            "size": 10,
            "_source": ["property_id", "property_name", "address"]
        }
    )

    return [hit["_source"] for hit in response["hits"]["hits"]]
```

## Search Ranking Algorithms

### Relevance Scoring

```python
def search_with_custom_scoring(self, query_text, user_preferences):
    """
    Custom relevance scoring based on multiple factors
    """
    query = {
        "function_score": {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": ["property_name^3", "description^2"]
                }
            },
            "functions": [
                # Boost recent listings
                {
                    "gauss": {
                        "listing_date": {
                            "origin": "now",
                            "scale": "30d",
                            "decay": 0.5
                        }
                    },
                    "weight": 1.5
                },
                # Boost popular properties (high view count)
                {
                    "field_value_factor": {
                        "field": "popularity_score",
                        "modifier": "log1p",
                        "factor": 0.5
                    }
                },
                # Personalization: boost properties matching user preferences
                {
                    "filter": {
                        "terms": {
                            "amenities": user_preferences.get("preferred_amenities", [])
                        }
                    },
                    "weight": 2.0
                },
                # Boost properties with photos
                {
                    "script_score": {
                        "script": {
                            "source": "Math.min(params.max_boost, doc['images'].size() * params.photo_boost)",
                            "params": {
                                "photo_boost": 0.1,
                                "max_boost": 1.5
                            }
                        }
                    }
                }
            ],
            "score_mode": "sum",
            "boost_mode": "multiply"
        }
    }

    response = self.es.search(
        index=self.index,
        body={"query": query}
    )

    return self.parse_search_results(response)
```

### Learning to Rank (LTR)

```python
from xgboost import XGBRanker
import numpy as np

class LearnToRankModel:
    """
    Machine learning-based search ranking
    """

    def __init__(self):
        self.model = XGBRanker(
            objective='rank:pairwise',
            n_estimators=100
        )

    def train(self, training_data):
        """
        Train ranking model

        Args:
            training_data: List of (query, properties, relevance_labels)
        """
        X = []  # Features
        y = []  # Relevance labels (0-4)
        groups = []  # Query groups

        for query, properties, labels in training_data:
            query_features = []

            for property in properties:
                features = self.extract_features(query, property)
                query_features.append(features)

            X.extend(query_features)
            y.extend(labels)
            groups.append(len(query_features))

        # Train model
        self.model.fit(
            np.array(X),
            np.array(y),
            group=groups
        )

    def extract_features(self, query, property):
        """
        Extract ranking features
        """
        return [
            # Text relevance features
            self.calculate_bm25_score(query, property["property_name"]),
            self.calculate_bm25_score(query, property["description"]),

            # Property features
            property["bedrooms"],
            property["bathrooms"],
            property["square_feet"],
            property["monthly_rent_amount"],

            # Engagement features
            property.get("views_30_days", 0),
            property.get("clicks_30_days", 0),
            property.get("inquiries_30_days", 0),

            # Freshness
            (datetime.now() - property["listing_date"]).days,

            # Quality indicators
            len(property.get("images", [])),
            1 if property.get("has_3d_tour") else 0,
            1 if property.get("has_video") else 0
        ]

    def rank_properties(self, query, properties):
        """
        Rank properties for query using trained model
        """
        # Extract features for each property
        features = [self.extract_features(query, p) for p in properties]

        # Predict scores
        scores = self.model.predict(np.array(features))

        # Sort by score
        ranked = sorted(
            zip(properties, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [p for p, score in ranked]
```

## Performance Optimization

### Caching Strategy

```python
from redis import Redis
import hashlib
import json

class SearchCache:
    """
    Cache search results in Redis
    """

    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.cache_ttl = 300  # 5 minutes

    def get_cache_key(self, query_params):
        """
        Generate cache key from query parameters
        """
        # Sort params for consistent keys
        sorted_params = json.dumps(query_params, sort_keys=True)

        # Hash for compact key
        key_hash = hashlib.md5(sorted_params.encode()).hexdigest()

        return f"search:results:{key_hash}"

    def get_cached_results(self, query_params):
        """
        Get cached search results
        """
        cache_key = self.get_cache_key(query_params)
        cached = self.redis.get(cache_key)

        if cached:
            return json.loads(cached)

        return None

    def cache_results(self, query_params, results):
        """
        Cache search results
        """
        cache_key = self.get_cache_key(query_params)
        self.redis.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(results)
        )

# Usage
cache = SearchCache(redis_client)

def search_properties(query_params):
    # Check cache first
    cached = cache.get_cached_results(query_params)
    if cached:
        return cached

    # Execute search
    results = elasticsearch_search(query_params)

    # Cache results
    cache.cache_results(query_params, results)

    return results
```

### Query Optimization

```python
# Bad: Deep pagination (slow)
response = es.search(
    index="properties",
    body={
        "query": query,
        "from": 9000,  # Skip 9000 results
        "size": 20
    }
)

# Good: Use search_after for deep pagination
response = es.search(
    index="properties",
    body={
        "query": query,
        "size": 20,
        "search_after": [previous_sort_value],  # Cursor from previous page
        "sort": [{"listing_date": "desc"}]
    }
)

# Good: Use Point in Time (PIT) for consistent pagination
pit = es.open_point_in_time(index="properties", keep_alive="5m")

response = es.search(
    body={
        "query": query,
        "size": 20,
        "pit": {
            "id": pit["id"],
            "keep_alive": "5m"
        }
    }
)
```

## Image Search and Visual Similarity

### Image Feature Extraction

```python
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing import image
import numpy as np

class ImageSimilaritySearch:
    """
    Visual similarity search for property images
    """

    def __init__(self):
        # Use pre-trained ResNet50 for feature extraction
        self.model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

    def extract_image_features(self, image_path):
        """
        Extract feature vector from image
        """
        # Load and preprocess image
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = tf.keras.applications.resnet50.preprocess_input(img_array)

        # Extract features
        features = self.model.predict(img_array)

        # Normalize
        features = features / np.linalg.norm(features)

        return features[0]  # 2048-dimensional vector

    def index_property_images(self, property_id, image_urls):
        """
        Index property images in Elasticsearch
        """
        for idx, image_url in enumerate(image_urls):
            # Download and extract features
            features = self.extract_image_features(image_url)

            # Index in Elasticsearch
            self.es.index(
                index="property_images",
                body={
                    "property_id": property_id,
                    "image_url": image_url,
                    "image_order": idx,
                    "features": features.tolist()
                }
            )

    def find_similar_properties(self, query_image_path, top_k=10):
        """
        Find properties with visually similar images
        """
        # Extract features from query image
        query_features = self.extract_image_features(query_image_path)

        # Search for similar images using cosine similarity
        query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'features') + 1.0",
                    "params": {
                        "query_vector": query_features.tolist()
                    }
                }
            }
        }

        response = self.es.search(
            index="property_images",
            body={
                "query": query,
                "size": top_k
            }
        )

        # Get unique property IDs
        property_ids = list(set([
            hit["_source"]["property_id"]
            for hit in response["hits"]["hits"]
        ]))

        return property_ids
```

---

## References

1. **Elasticsearch Documentation**: https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html
2. **Zillow Engineering Blog**: https://www.zillow.com/tech/
3. **Redfin Engineering**: https://redfin.engineering/
4. **MongoDB Geospatial**: https://www.mongodb.com/docs/manual/geospatial-queries/
5. **PostGIS**: https://postgis.net/

---

## Performance Benchmarks

**Zillow Search Performance (2024):**
- Query latency: P50: 85ms, P95: 180ms, P99: 320ms
- Throughput: 50,000 QPS
- Index size: 110M properties
- Infrastructure: Elasticsearch 8.x, 200+ nodes

**Redfin Search Performance (2024):**
- Query latency: P95: 150ms
- Autocomplete: P95: 50ms
- Index refresh: 1 second
- Search relevance: 92% user satisfaction

---

*This document is maintained by the PropTech Architecture Committee. For questions or updates, contact architecture@proptech.com.*

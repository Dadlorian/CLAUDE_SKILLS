"""
Advanced Asset Search System with Elasticsearch
Supports full-text, faceted, and similarity search
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from elasticsearch import Elasticsearch, helpers
import numpy as np


@dataclass
class SearchQuery:
    """Search query parameters"""
    keywords: Optional[str] = None
    facets: Dict[str, List] = None
    date_range: Optional[Dict] = None
    sort_by: str = "relevance"
    page: int = 0
    page_size: int = 20


@dataclass
class SearchResult:
    """Search result"""
    asset_id: str
    title: str
    description: str
    asset_type: str
    thumbnail_url: str
    score: float
    metadata: Dict


class AssetSearchEngine:
    """Asset search engine with Elasticsearch"""

    def __init__(self, elasticsearch_url: str):
        self.es = Elasticsearch([elasticsearch_url])
        self.index_name = "assets"

        # Create index if not exists
        self._ensure_index()

    def _ensure_index(self):
        """Create index with proper mappings"""

        if self.es.indices.exists(index=self.index_name):
            return

        mapping = {
            "mappings": {
                "properties": {
                    "asset_id": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "english",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "english"
                    },
                    "asset_type": {"type": "keyword"},
                    "creator": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "tags": {"type": "keyword"},
                    "genre": {"type": "keyword"},
                    "language": {"type": "keyword"},
                    "created_date": {"type": "date"},
                    "duration": {"type": "float"},
                    "resolution": {"type": "keyword"},
                    "format": {"type": "keyword"},
                    "file_size": {"type": "long"},
                    "rights_status": {"type": "keyword"},
                    "license_expiry": {"type": "date"},
                    "popularity_score": {"type": "float"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 512
                    }
                }
            }
        }

        self.es.indices.create(index=self.index_name, body=mapping)
        print(f"Created index: {self.index_name}")

    def index_asset(self, asset: Dict):
        """Index a single asset"""

        document = {
            "asset_id": asset["asset_id"],
            "title": asset["title"],
            "description": asset.get("description", ""),
            "asset_type": asset["asset_type"],
            "creator": asset.get("creator", ""),
            "tags": asset.get("tags", []),
            "genre": asset.get("genre", ""),
            "language": asset.get("language", "en"),
            "created_date": asset.get("created_date"),
            "duration": asset.get("duration"),
            "resolution": asset.get("resolution"),
            "format": asset.get("format"),
            "file_size": asset.get("file_size"),
            "rights_status": asset.get("rights_status"),
            "license_expiry": asset.get("license_expiry"),
            "popularity_score": asset.get("popularity_score", 0.0),
            "embedding": asset.get("embedding")  # For similarity search
        }

        self.es.index(
            index=self.index_name,
            id=asset["asset_id"],
            body=document
        )

        print(f"Indexed asset: {asset['asset_id']}")

    def bulk_index_assets(self, assets: List[Dict]):
        """Bulk index multiple assets"""

        actions = []
        for asset in assets:
            action = {
                "_index": self.index_name,
                "_id": asset["asset_id"],
                "_source": {
                    "asset_id": asset["asset_id"],
                    "title": asset["title"],
                    "description": asset.get("description", ""),
                    "asset_type": asset["asset_type"],
                    "creator": asset.get("creator", ""),
                    "tags": asset.get("tags", []),
                    "genre": asset.get("genre", ""),
                    "language": asset.get("language", "en"),
                    "created_date": asset.get("created_date"),
                    "duration": asset.get("duration"),
                    "resolution": asset.get("resolution"),
                    "format": asset.get("format"),
                    "file_size": asset.get("file_size"),
                    "rights_status": asset.get("rights_status"),
                    "license_expiry": asset.get("license_expiry"),
                    "popularity_score": asset.get("popularity_score", 0.0)
                }
            }
            actions.append(action)

        helpers.bulk(self.es, actions)
        print(f"Bulk indexed {len(assets)} assets")

    def search(self, query: SearchQuery) -> Dict:
        """Perform comprehensive search"""

        # Build Elasticsearch query
        es_query = self._build_query(query)

        # Execute search
        response = self.es.search(
            index=self.index_name,
            body=es_query,
            from_=query.page * query.page_size,
            size=query.page_size
        )

        # Parse results
        results = self._parse_results(response)

        # Get aggregations (facets)
        facets = self._parse_facets(response)

        return {
            "total": response["hits"]["total"]["value"],
            "results": results,
            "facets": facets,
            "page": query.page,
            "page_size": query.page_size
        }

    def _build_query(self, query: SearchQuery) -> Dict:
        """Build Elasticsearch query from search parameters"""

        es_query = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            },
            "aggs": {}
        }

        # Keyword search (full-text)
        if query.keywords:
            es_query["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": query.keywords,
                    "fields": [
                        "title^3",  # Boost title matches
                        "description^2",
                        "creator",
                        "tags"
                    ],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            })
        else:
            # Match all if no keywords
            es_query["query"]["bool"]["must"].append({
                "match_all": {}
            })

        # Facet filters
        if query.facets:
            for field, values in query.facets.items():
                if values:
                    es_query["query"]["bool"]["filter"].append({
                        "terms": {field: values}
                    })

        # Date range filter
        if query.date_range:
            es_query["query"]["bool"]["filter"].append({
                "range": {
                    "created_date": query.date_range
                }
            })

        # Sorting
        if query.sort_by == "relevance":
            es_query["sort"] = ["_score"]
        elif query.sort_by == "date_desc":
            es_query["sort"] = [{"created_date": "desc"}]
        elif query.sort_by == "date_asc":
            es_query["sort"] = [{"created_date": "asc"}]
        elif query.sort_by == "title":
            es_query["sort"] = [{"title.keyword": "asc"}]
        elif query.sort_by == "popularity":
            es_query["sort"] = [{"popularity_score": "desc"}]

        # Aggregations for facets
        es_query["aggs"] = {
            "asset_types": {
                "terms": {"field": "asset_type", "size": 10}
            },
            "genres": {
                "terms": {"field": "genre", "size": 20}
            },
            "languages": {
                "terms": {"field": "language", "size": 10}
            },
            "formats": {
                "terms": {"field": "format", "size": 10}
            },
            "creators": {
                "terms": {"field": "creator.keyword", "size": 20}
            },
            "year": {
                "date_histogram": {
                    "field": "created_date",
                    "calendar_interval": "year"
                }
            }
        }

        return es_query

    def _parse_results(self, response: Dict) -> List[SearchResult]:
        """Parse Elasticsearch response into SearchResult objects"""

        results = []

        for hit in response["hits"]["hits"]:
            source = hit["_source"]

            result = SearchResult(
                asset_id=source["asset_id"],
                title=source["title"],
                description=source.get("description", ""),
                asset_type=source["asset_type"],
                thumbnail_url=f"/thumbnails/{source['asset_id']}.jpg",
                score=hit["_score"],
                metadata={
                    "creator": source.get("creator"),
                    "created_date": source.get("created_date"),
                    "duration": source.get("duration"),
                    "format": source.get("format"),
                    "tags": source.get("tags", [])
                }
            )

            results.append(result)

        return results

    def _parse_facets(self, response: Dict) -> Dict:
        """Parse aggregations into facets"""

        facets = {}

        if "aggregations" in response:
            aggs = response["aggregations"]

            # Parse term aggregations
            for facet_name in ["asset_types", "genres", "languages", "formats", "creators"]:
                if facet_name in aggs:
                    facets[facet_name] = [
                        {
                            "value": bucket["key"],
                            "count": bucket["doc_count"]
                        }
                        for bucket in aggs[facet_name]["buckets"]
                    ]

            # Parse date histogram
            if "year" in aggs:
                facets["years"] = [
                    {
                        "year": bucket["key_as_string"][:4],
                        "count": bucket["doc_count"]
                    }
                    for bucket in aggs["year"]["buckets"]
                ]

        return facets

    def search_similar(self, asset_id: str, limit: int = 10) -> List[SearchResult]:
        """Find similar assets using vector similarity"""

        # Get asset embedding
        asset = self.es.get(index=self.index_name, id=asset_id)
        embedding = asset["_source"].get("embedding")

        if not embedding:
            return []

        # Search for similar embeddings
        es_query = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": embedding}
                    }
                }
            },
            "size": limit + 1  # +1 to exclude self
        }

        response = self.es.search(index=self.index_name, body=es_query)

        # Parse and filter out the query asset
        results = self._parse_results(response)
        return [r for r in results if r.asset_id != asset_id][:limit]

    def autocomplete(self, prefix: str, field: str = "title", limit: int = 10) -> List[str]:
        """Autocomplete suggestions"""

        es_query = {
            "query": {
                "match_phrase_prefix": {
                    field: {
                        "query": prefix,
                        "max_expansions": 10
                    }
                }
            },
            "_source": [field],
            "size": limit
        }

        response = self.es.search(index=self.index_name, body=es_query)

        suggestions = [
            hit["_source"][field]
            for hit in response["hits"]["hits"]
        ]

        return suggestions

    def get_trending(self, days: int = 7, limit: int = 20) -> List[SearchResult]:
        """Get trending assets based on popularity"""

        from_date = datetime.now().timestamp() - (days * 24 * 3600)

        es_query = {
            "query": {
                "range": {
                    "created_date": {
                        "gte": from_date
                    }
                }
            },
            "sort": [
                {"popularity_score": "desc"}
            ],
            "size": limit
        }

        response = self.es.search(index=self.index_name, body=es_query)

        return self._parse_results(response)

    def delete_asset(self, asset_id: str):
        """Remove asset from index"""

        self.es.delete(index=self.index_name, id=asset_id)
        print(f"Deleted asset from index: {asset_id}")

    def update_asset(self, asset_id: str, updates: Dict):
        """Update specific fields of an asset"""

        self.es.update(
            index=self.index_name,
            id=asset_id,
            body={"doc": updates}
        )

        print(f"Updated asset: {asset_id}")


# Example usage
def main():
    # Initialize search engine
    search = AssetSearchEngine("http://localhost:9200")

    # Index sample assets
    sample_assets = [
        {
            "asset_id": "asset_001",
            "title": "Sample Video 1",
            "description": "A great video about technology",
            "asset_type": "video",
            "creator": "John Doe",
            "tags": ["technology", "education"],
            "genre": "Documentary",
            "language": "en",
            "created_date": "2024-01-15",
            "duration": 1800.0,
            "resolution": "1920x1080",
            "format": "mp4",
            "file_size": 500000000,
            "rights_status": "available",
            "popularity_score": 0.85
        },
        {
            "asset_id": "asset_002",
            "title": "Sample Image 1",
            "description": "Beautiful landscape photography",
            "asset_type": "image",
            "creator": "Jane Smith",
            "tags": ["nature", "photography"],
            "genre": "Photography",
            "language": "en",
            "created_date": "2024-02-01",
            "resolution": "4096x2160",
            "format": "jpg",
            "file_size": 5000000,
            "rights_status": "available",
            "popularity_score": 0.72
        }
    ]

    search.bulk_index_assets(sample_assets)

    # Perform searches
    query = SearchQuery(
        keywords="technology video",
        facets={"asset_type": ["video"]},
        sort_by="relevance",
        page=0,
        page_size=20
    )

    results = search.search(query)

    print(f"Found {results['total']} results")
    for result in results['results']:
        print(f"- {result.title} (score: {result.score:.2f})")

    print(f"\nFacets:")
    for facet_name, facet_values in results['facets'].items():
        print(f"  {facet_name}: {facet_values}")


if __name__ == "__main__":
    main()

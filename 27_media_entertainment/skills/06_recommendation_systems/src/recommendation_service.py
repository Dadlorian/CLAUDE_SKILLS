"""
Complete Recommendation Service Implementation
Production-ready recommendation API with caching, A/B testing, and monitoring
"""

import asyncio
import hashlib
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np
import redis.asyncio as redis
import pickle

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Data Models
# ============================================================================

class RecommendationRequest(BaseModel):
    user_id: str
    n: int = 20
    context: Optional[Dict] = None
    experiment_id: Optional[str] = None

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[Dict]
    algorithm: str
    variant: Optional[str] = None
    cached: bool
    latency_ms: float

@dataclass
class UserProfile:
    user_id: str
    total_views: int
    preferred_genres: List[str]
    avg_watch_time: float
    last_active: datetime
    device_type: str

@dataclass
class ItemMetadata:
    item_id: str
    title: str
    genre: str
    release_year: int
    duration_minutes: int
    popularity_score: float
    avg_rating: float

# ============================================================================
# Recommendation Engine Core
# ============================================================================

class RecommendationEngine:
    """Core recommendation engine with multiple algorithms"""

    def __init__(self, config: Dict):
        self.config = config
        self.user_embeddings = {}
        self.item_embeddings = {}
        self.item_metadata = {}

        # Load model artifacts
        self._load_models()

    def _load_models(self):
        """Load pre-trained model embeddings"""
        # In production, load from S3/GCS
        logger.info("Loading model artifacts...")

        # Mock loading
        num_users = 10000
        num_items = 5000
        embedding_dim = 128

        self.user_embeddings = {
            f"user_{i}": np.random.randn(embedding_dim)
            for i in range(num_users)
        }

        self.item_embeddings = {
            f"item_{i}": np.random.randn(embedding_dim)
            for i in range(num_items)
        }

        self.item_ids = list(self.item_embeddings.keys())
        self.item_matrix = np.array(list(self.item_embeddings.values()))

        logger.info(f"Loaded {len(self.user_embeddings)} users, {len(self.item_embeddings)} items")

    def get_recommendations_collaborative(
        self,
        user_id: str,
        n: int = 20
    ) -> List[Dict]:
        """Collaborative filtering recommendations"""

        user_embedding = self.user_embeddings.get(user_id)
        if user_embedding is None:
            return self._get_popular_items(n)

        # Compute similarities
        similarities = np.dot(self.item_matrix, user_embedding)

        # Get top N
        top_indices = np.argsort(similarities)[-n:][::-1]

        recommendations = [
            {
                "item_id": self.item_ids[idx],
                "score": float(similarities[idx]),
                "algorithm": "collaborative_filtering"
            }
            for idx in top_indices
        ]

        return recommendations

    def get_recommendations_two_tower(
        self,
        user_id: str,
        n: int = 20
    ) -> List[Dict]:
        """Two-tower model recommendations (deep learning)"""

        user_embedding = self.user_embeddings.get(user_id)
        if user_embedding is None:
            return self._get_popular_items(n)

        # Normalize embeddings for cosine similarity
        user_norm = user_embedding / np.linalg.norm(user_embedding)
        item_norms = self.item_matrix / np.linalg.norm(
            self.item_matrix, axis=1, keepdims=True
        )

        # Compute cosine similarities
        similarities = np.dot(item_norms, user_norm)

        # Get top N
        top_indices = np.argsort(similarities)[-n:][::-1]

        recommendations = [
            {
                "item_id": self.item_ids[idx],
                "score": float(similarities[idx]),
                "algorithm": "two_tower"
            }
            for idx in top_indices
        ]

        return recommendations

    def get_recommendations_hybrid(
        self,
        user_id: str,
        n: int = 20
    ) -> List[Dict]:
        """Hybrid: combine collaborative + content-based"""

        # Get recommendations from multiple algorithms
        collab_recs = self.get_recommendations_collaborative(user_id, n * 2)
        two_tower_recs = self.get_recommendations_two_tower(user_id, n * 2)

        # Combine scores
        combined_scores = {}

        for rec in collab_recs:
            item_id = rec['item_id']
            combined_scores[item_id] = rec['score'] * 0.5

        for rec in two_tower_recs:
            item_id = rec['item_id']
            if item_id in combined_scores:
                combined_scores[item_id] += rec['score'] * 0.5
            else:
                combined_scores[item_id] = rec['score'] * 0.5

        # Sort and return top N
        sorted_items = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]

        recommendations = [
            {
                "item_id": item_id,
                "score": score,
                "algorithm": "hybrid"
            }
            for item_id, score in sorted_items
        ]

        return recommendations

    def _get_popular_items(self, n: int) -> List[Dict]:
        """Fallback: return popular items for cold start"""

        # Return first N items (in production, use actual popularity)
        recommendations = [
            {
                "item_id": self.item_ids[i],
                "score": 1.0 - (i * 0.01),
                "algorithm": "popularity"
            }
            for i in range(min(n, len(self.item_ids)))
        ]

        return recommendations

# ============================================================================
# A/B Testing Manager
# ============================================================================

class ABTestManager:
    """Manage A/B experiments for recommendation algorithms"""

    def __init__(self, experiments: Dict):
        self.experiments = experiments

    def get_variant(self, user_id: str, experiment_id: str) -> str:
        """Assign user to experiment variant"""

        experiment = self.experiments.get(experiment_id)
        if not experiment or not experiment.get('active', False):
            return 'control'

        # Consistent hashing for stable assignment
        hash_input = f"{user_id}:{experiment_id}:{experiment.get('salt', 'default')}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = hash_value % 100

        # Assign based on traffic allocation
        cumulative = 0
        for variant_name, traffic_percent in experiment['variants'].items():
            cumulative += traffic_percent
            if bucket < cumulative:
                return variant_name

        return 'control'

# ============================================================================
# Business Rules Engine
# ============================================================================

class BusinessRulesEngine:
    """Apply business rules to recommendations"""

    def __init__(self, user_service, item_service):
        self.user_service = user_service
        self.item_service = item_service

    async def apply_rules(
        self,
        user_id: str,
        recommendations: List[Dict],
        context: Optional[Dict] = None
    ) -> List[Dict]:
        """Apply filtering and boosting rules"""

        # Get user watch history
        watched_items = await self.user_service.get_watch_history(user_id)
        watched_set = set(watched_items)

        # Get user profile
        user_profile = await self.user_service.get_profile(user_id)

        filtered_recs = []

        for rec in recommendations:
            item_id = rec['item_id']

            # Filter: Remove already watched
            if item_id in watched_set:
                continue

            # Get item metadata
            metadata = await self.item_service.get_metadata(item_id)
            if not metadata:
                continue

            # Filter: Maturity rating
            if not self._check_maturity_rating(metadata, user_profile):
                continue

            # Boost: New releases
            if self._is_new_release(metadata):
                rec['score'] *= 1.2
                rec['boost_reason'] = 'new_release'

            # Boost: Trending
            if self._is_trending(metadata):
                rec['score'] *= 1.1
                rec['boost_reason'] = 'trending'

            # Add metadata to response
            rec['metadata'] = {
                'title': metadata.get('title'),
                'genre': metadata.get('genre'),
                'release_year': metadata.get('release_year'),
                'duration_minutes': metadata.get('duration_minutes')
            }

            filtered_recs.append(rec)

        # Re-sort by adjusted scores
        filtered_recs.sort(key=lambda x: x['score'], reverse=True)

        return filtered_recs

    def _check_maturity_rating(self, metadata: Dict, user_profile: Dict) -> bool:
        """Check if content is appropriate for user"""
        # Simplified - in production, use proper rating logic
        return True

    def _is_new_release(self, metadata: Dict) -> bool:
        """Check if item is a new release"""
        release_date = metadata.get('release_date')
        if not release_date:
            return False

        # Consider new if released within last 30 days
        days_since_release = (datetime.now() - release_date).days
        return days_since_release < 30

    def _is_trending(self, metadata: Dict) -> bool:
        """Check if item is trending"""
        # In production, check against trending data
        popularity_score = metadata.get('popularity_score', 0)
        return popularity_score > 0.8

# ============================================================================
# Cache Manager
# ============================================================================

class CacheManager:
    """Manage Redis cache for recommendations"""

    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=False)

    async def get_cached_recommendations(
        self,
        user_id: str,
        n: int,
        variant: str
    ) -> Optional[List[Dict]]:
        """Get cached recommendations"""

        cache_key = f"recs:{user_id}:{n}:{variant}"

        try:
            cached = await self.redis.get(cache_key)
            if cached:
                return pickle.loads(cached)
        except Exception as e:
            logger.error(f"Cache get error: {e}")

        return None

    async def cache_recommendations(
        self,
        user_id: str,
        n: int,
        variant: str,
        recommendations: List[Dict],
        ttl: int = 3600
    ):
        """Cache recommendations with TTL"""

        cache_key = f"recs:{user_id}:{n}:{variant}"

        try:
            await self.redis.setex(
                cache_key,
                ttl,
                pickle.dumps(recommendations)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")

# ============================================================================
# Mock Services (in production, these would be real services)
# ============================================================================

class MockUserService:
    async def get_watch_history(self, user_id: str) -> List[str]:
        return []  # Empty for mock

    async def get_profile(self, user_id: str) -> Dict:
        return {"max_maturity_rating": "R"}

class MockItemService:
    async def get_metadata(self, item_id: str) -> Dict:
        return {
            "title": f"Title {item_id}",
            "genre": "Action",
            "release_year": 2024,
            "duration_minutes": 120,
            "release_date": datetime.now() - timedelta(days=10),
            "popularity_score": 0.7
        }

# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(title="Recommendation Service")

# Initialize components
config = {
    "redis_url": "redis://localhost:6379",
    "experiments": {
        "algo_test_v1": {
            "active": True,
            "salt": "algo_test_2024",
            "variants": {
                "control": 50,  # 50% collaborative
                "two_tower": 25,  # 25% two-tower
                "hybrid": 25  # 25% hybrid
            }
        }
    }
}

engine = RecommendationEngine(config)
ab_manager = ABTestManager(config['experiments'])
cache_manager = CacheManager(config['redis_url'])
business_rules = BusinessRulesEngine(MockUserService(), MockItemService())

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    background_tasks: BackgroundTasks
):
    """Get personalized recommendations for user"""

    start_time = time.time()

    try:
        # Determine variant
        variant = 'control'
        if request.experiment_id:
            variant = ab_manager.get_variant(request.user_id, request.experiment_id)

        # Check cache
        cached_recs = await cache_manager.get_cached_recommendations(
            request.user_id,
            request.n,
            variant
        )

        if cached_recs:
            latency_ms = (time.time() - start_time) * 1000
            logger.info(f"Cache hit for user {request.user_id}, variant {variant}")

            return RecommendationResponse(
                user_id=request.user_id,
                recommendations=cached_recs,
                algorithm=cached_recs[0]['algorithm'] if cached_recs else 'unknown',
                variant=variant,
                cached=True,
                latency_ms=latency_ms
            )

        # Get recommendations based on variant
        if variant == 'two_tower':
            recs = engine.get_recommendations_two_tower(request.user_id, request.n * 2)
        elif variant == 'hybrid':
            recs = engine.get_recommendations_hybrid(request.user_id, request.n * 2)
        else:  # control
            recs = engine.get_recommendations_collaborative(request.user_id, request.n * 2)

        # Apply business rules
        recs = await business_rules.apply_rules(
            request.user_id,
            recs,
            request.context
        )

        # Limit to requested number
        recs = recs[:request.n]

        # Cache recommendations
        background_tasks.add_task(
            cache_manager.cache_recommendations,
            request.user_id,
            request.n,
            variant,
            recs
        )

        latency_ms = (time.time() - start_time) * 1000

        logger.info(
            f"Generated {len(recs)} recs for user {request.user_id}, "
            f"variant {variant}, latency {latency_ms:.2f}ms"
        )

        return RecommendationResponse(
            user_id=request.user_id,
            recommendations=recs,
            algorithm=recs[0]['algorithm'] if recs else 'unknown',
            variant=variant,
            cached=False,
            latency_ms=latency_ms
        )

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/experiments/{experiment_id}/variant/{user_id}")
async def get_experiment_variant(experiment_id: str, user_id: str):
    """Get experiment variant for user"""

    variant = ab_manager.get_variant(user_id, experiment_id)

    return {
        "user_id": user_id,
        "experiment_id": experiment_id,
        "variant": variant
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

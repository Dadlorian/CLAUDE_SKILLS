"""
Production Social Media Feed Generator
Implements hybrid fan-out with ML-based ranking
"""

import asyncio
import time
import hashlib
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import numpy as np
import redis.asyncio as redis


@dataclass
class Post:
    """Social media post"""
    id: str
    author_id: str
    content: str
    media_urls: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    created_at: float = 0.0
    engagement: Dict[str, int] = field(default_factory=dict)
    content_embedding: Optional[np.ndarray] = None


@dataclass
class UserProfile:
    """User profile and preferences"""
    id: str
    following: List[str] = field(default_factory=list)
    followers_count: int = 0
    interest_embedding: Optional[np.ndarray] = None
    affinity: Dict[str, float] = field(default_factory=dict)
    active_hours: List[int] = field(default_factory=list)
    prefers_media: float = 0.5


class FeedGenerator:
    """Generate personalized feeds with ML ranking"""

    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=False)
        self.CELEBRITY_THRESHOLD = 10000
        self.FEED_SIZE = 1000
        self.PAGE_SIZE = 20

    async def publish_post(self, post: Post, author: UserProfile):
        """Publish post and fan out to followers"""

        # Store post
        await self._store_post(post)

        # Determine fan-out strategy
        if author.followers_count < self.CELEBRITY_THRESHOLD:
            # Fan-out on write (push)
            await self._fanout_push(post, author)
        else:
            # Fan-out on read (pull) - mark as celebrity post
            await self._mark_celebrity_post(post)

        print(f"Published post {post.id} by {post.author_id}")

    async def _fanout_push(self, post: Post, author: UserProfile):
        """Push post to all followers' feeds"""

        # Get followers (in production, paginate this)
        followers = await self._get_followers(author.id)

        # Push to feeds in batches
        batch_size = 100
        for i in range(0, len(followers), batch_size):
            batch = followers[i:i + batch_size]

            tasks = [
                self._add_to_feed(follower_id, post.id, post.created_at)
                for follower_id in batch
            ]

            await asyncio.gather(*tasks)

        print(f"Fanned out to {len(followers)} followers")

    async def _mark_celebrity_post(self, post: Post):
        """Mark post for on-demand loading"""

        key = f"celebrity_posts:{post.author_id}"

        # Add to sorted set (score = timestamp)
        await self.redis.zadd(key, {post.id: post.created_at})

        # Keep only recent posts
        await self.redis.zremrangebyrank(key, 0, -1001)

        # Set expiry
        await self.redis.expire(key, 7 * 24 * 3600)

    async def _add_to_feed(self, user_id: str, post_id: str, timestamp: float):
        """Add post to user's feed"""

        feed_key = f"feed:{user_id}"

        # Add to sorted set
        await self.redis.zadd(feed_key, {post_id: timestamp})

        # Keep feed size limited
        await self.redis.zremrangebyrank(feed_key, 0, -self.FEED_SIZE - 1)

    async def get_feed(
        self,
        user_id: str,
        page: int = 0,
        page_size: int = 20
    ) -> List[Post]:
        """Get personalized feed for user"""

        # Get user profile
        user = await self._get_user_profile(user_id)

        # Get candidate posts
        candidates = await self._get_candidate_posts(user, page_size * 3)

        # Rank posts
        ranked_posts = await self._rank_posts(user, candidates)

        # Paginate
        start = page * page_size
        end = start + page_size

        return ranked_posts[start:end]

    async def _get_candidate_posts(
        self,
        user: UserProfile,
        count: int
    ) -> List[Post]:
        """Get candidate posts for ranking"""

        candidates = []

        # Get posts from feed cache (pushed posts)
        cached_posts = await self._get_cached_feed_posts(user.id, count)
        candidates.extend(cached_posts)

        # Get posts from celebrities user follows
        celebrity_posts = await self._get_celebrity_posts(user, count // 2)
        candidates.extend(celebrity_posts)

        # Deduplicate
        seen = set()
        unique_candidates = []
        for post in candidates:
            if post.id not in seen:
                seen.add(post.id)
                unique_candidates.append(post)

        return unique_candidates

    async def _get_cached_feed_posts(self, user_id: str, count: int) -> List[Post]:
        """Get posts from user's cached feed"""

        feed_key = f"feed:{user_id}"

        # Get post IDs (most recent first)
        post_ids = await self.redis.zrevrange(feed_key, 0, count - 1)

        if not post_ids:
            return []

        # Hydrate posts
        posts = await self._hydrate_posts([pid.decode() for pid in post_ids])

        return posts

    async def _get_celebrity_posts(self, user: UserProfile, count: int) -> List[Post]:
        """Get posts from celebrities user follows"""

        posts = []

        for author_id in user.following:
            # Check if celebrity
            is_celebrity = await self._is_celebrity(author_id)
            if not is_celebrity:
                continue

            # Get their recent posts
            key = f"celebrity_posts:{author_id}"
            post_ids = await self.redis.zrevrange(key, 0, 4)  # Get 5 recent

            if post_ids:
                author_posts = await self._hydrate_posts([pid.decode() for pid in post_ids])
                posts.extend(author_posts)

        return posts[:count]

    async def _rank_posts(self, user: UserProfile, posts: List[Post]) -> List[Post]:
        """Rank posts by relevance"""

        if not posts:
            return []

        scored_posts = []

        for post in posts:
            score = self._calculate_post_score(post, user)
            scored_posts.append((score, post))

        # Sort by score descending
        scored_posts.sort(key=lambda x: x[0], reverse=True)

        return [post for _, post in scored_posts]

    def _calculate_post_score(self, post: Post, user: UserProfile) -> float:
        """Calculate relevance score for post"""

        score = 0.0

        # Recency (exponential decay)
        age_hours = (time.time() - post.created_at) / 3600
        recency_score = 2.0 ** (-age_hours / 24)  # Half-life 24 hours
        score += recency_score * 10

        # Engagement score
        likes = post.engagement.get('likes', 0)
        comments = post.engagement.get('comments', 0)
        shares = post.engagement.get('shares', 0)

        engagement_score = (
            likes * 1.0 +
            comments * 3.0 +
            shares * 5.0
        )

        # Normalize by impressions
        impressions = post.engagement.get('impressions', 1)
        engagement_rate = engagement_score / max(impressions, 1)

        score += engagement_rate * 100

        # Author affinity
        author_affinity = user.affinity.get(post.author_id, 0)
        score += author_affinity * 20

        # Media preference
        has_media = len(post.media_urls) > 0
        if has_media:
            score += user.prefers_media * 5

        # Content similarity (if embeddings available)
        if post.content_embedding is not None and user.interest_embedding is not None:
            similarity = np.dot(post.content_embedding, user.interest_embedding)
            similarity = float(similarity)
            score += similarity * 15

        # Time-of-day match
        post_hour = int((post.created_at % 86400) / 3600)
        if post_hour in user.active_hours:
            score += 3

        return score

    # Helper methods

    async def _store_post(self, post: Post):
        """Store post in database"""

        # Store in Redis
        key = f"post:{post.id}"
        import pickle
        await self.redis.set(key, pickle.dumps(post))
        await self.redis.expire(key, 30 * 24 * 3600)  # 30 days

    async def _hydrate_posts(self, post_ids: List[str]) -> List[Post]:
        """Load full post objects from IDs"""

        if not post_ids:
            return []

        # Batch get from Redis
        keys = [f"post:{post_id}" for post_id in post_ids]
        values = await self.redis.mget(keys)

        posts = []
        import pickle
        for value in values:
            if value:
                post = pickle.loads(value)
                posts.append(post)

        return posts

    async def _get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile"""

        # Load from database/cache
        # Mock implementation
        return UserProfile(
            id=user_id,
            following=['author_1', 'author_2'],
            followers_count=500,
            affinity={'author_1': 0.8, 'author_2': 0.6},
            active_hours=[9, 10, 11, 18, 19, 20, 21],
            prefers_media=0.7
        )

    async def _get_followers(self, user_id: str) -> List[str]:
        """Get list of user's followers"""

        # Query from graph database
        # Mock implementation
        return [f"user_{i}" for i in range(100)]

    async def _is_celebrity(self, user_id: str) -> bool:
        """Check if user is a celebrity"""

        # Check if celebrity posts exist
        key = f"celebrity_posts:{user_id}"
        exists = await self.redis.exists(key)

        return exists > 0

    async def update_engagement(
        self,
        post_id: str,
        action: str,
        user_id: str
    ):
        """Update post engagement metrics"""

        # Increment engagement counter
        key = f"post:{post_id}:engagement"

        await self.redis.hincrby(key, action, 1)

        # Update user affinity
        await self._update_affinity(user_id, post_id, action)

        print(f"Updated engagement for post {post_id}: {action}")

    async def _update_affinity(self, user_id: str, post_id: str, action: str):
        """Update user's affinity for post author"""

        # Get post author
        post = await self._hydrate_posts([post_id])
        if not post:
            return

        author_id = post[0].author_id

        # Get current affinity
        affinity_key = f"affinity:{user_id}"
        current = await self.redis.hget(affinity_key, author_id)
        current_affinity = float(current.decode()) if current else 0.0

        # Update based on action
        affinity_delta = {
            'like': 0.1,
            'comment': 0.3,
            'share': 0.5,
            'follow': 1.0
        }.get(action, 0.0)

        new_affinity = min(current_affinity + affinity_delta, 1.0)

        await self.redis.hset(affinity_key, author_id, new_affinity)

        # Set expiry
        await self.redis.expire(affinity_key, 90 * 24 * 3600)


class TrendingDetector:
    """Detect trending posts and topics"""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.TRENDING_WINDOW = 3600  # 1 hour

    async def track_post(self, post: Post):
        """Track post for trending detection"""

        current_time = time.time()
        window = int(current_time / self.TRENDING_WINDOW)

        # Track hashtags
        for hashtag in post.hashtags:
            key = f"trending:hashtag:{hashtag}"
            await self.redis.hincrby(key, str(window), 1)
            await self.redis.expire(key, 24 * 3600)

        # Track post velocity
        engagement_key = f"trending:post:{post.id}"
        await self.redis.zadd(
            engagement_key,
            {f"{current_time}": sum(post.engagement.values())}
        )
        await self.redis.expire(engagement_key, 24 * 3600)

    async def get_trending_hashtags(self, top_n: int = 10) -> List[Dict]:
        """Get trending hashtags"""

        current_time = time.time()
        current_window = int(current_time / self.TRENDING_WINDOW)
        previous_window = current_window - 1

        # Scan all hashtag keys
        trending = []

        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(
                cursor,
                match="trending:hashtag:*",
                count=100
            )

            for key in keys:
                hashtag = key.decode().split(':')[-1]

                # Get current and previous counts
                current_count = await self.redis.hget(key, str(current_window))
                previous_count = await self.redis.hget(key, str(previous_window))

                current_count = int(current_count.decode()) if current_count else 0
                previous_count = int(previous_count.decode()) if previous_count else 0

                # Calculate velocity
                if previous_count > 0:
                    velocity = (current_count - previous_count) / previous_count
                else:
                    velocity = float(current_count)

                # Score
                score = current_count * (1 + velocity)

                trending.append({
                    'hashtag': hashtag,
                    'count': current_count,
                    'velocity': velocity,
                    'score': score
                })

            if cursor == 0:
                break

        # Sort by score
        trending.sort(key=lambda x: x['score'], reverse=True)

        return trending[:top_n]


# Example usage
async def main():
    redis_url = "redis://localhost:6379"
    feed_gen = FeedGenerator(redis_url)

    # Create test post
    post = Post(
        id="post_123",
        author_id="author_1",
        content="Hello world! #test #demo",
        media_urls=["https://example.com/image.jpg"],
        hashtags=["test", "demo"],
        created_at=time.time(),
        engagement={'likes': 10, 'comments': 2, 'shares': 1, 'impressions': 100}
    )

    # Mock author
    author = UserProfile(
        id="author_1",
        followers_count=5000
    )

    # Publish post
    await feed_gen.publish_post(post, author)

    # Get user feed
    user_id = "user_123"
    feed = await feed_gen.get_feed(user_id, page=0, page_size=20)

    print(f"Generated feed with {len(feed)} posts")


if __name__ == "__main__":
    asyncio.run(main())

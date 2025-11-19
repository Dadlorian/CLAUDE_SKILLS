# Building a Social Media Feed System

Complete guide to building scalable social media platforms like Twitter, Instagram, or TikTok, covering feed ranking, viral content detection, moderation, and real-time updates.

## Architecture Overview

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   User Posts    │─────>│  Content Store   │─────>│  Feed Generator │
│   & Actions     │      │  (Posts, Media)  │      │  (Ranked Feed)  │
└─────────────────┘      └──────────────────┘      └─────────────────┘
        │                                                     │
        ▼                                                     ▼
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Graph Database │─────>│  Ranking Model   │<─────│  User Profile   │
│  (Following)    │      │  (ML/Heuristic)  │      │  & Preferences  │
└─────────────────┘      └──────────────────┘      └─────────────────┘
        │                                                     │
        ▼                                                     ▼
┌─────────────────┐                                 ┌─────────────────┐
│  Real-Time      │                                 │   Cache Layer   │
│  Notifications  │                                 │   (Redis/CDN)   │
└─────────────────┘                                 └─────────────────┘
```

## Phase 1: Feed Generation System

### 1.1 Fan-Out Architecture

```python
# feed_fanout.py
import asyncio
from typing import List, Dict, Set
from dataclasses import dataclass
import redis.asyncio as redis

@dataclass
class Post:
    id: str
    author_id: str
    content: str
    media_urls: List[str]
    created_at: float
    engagement: Dict[str, int]  # likes, comments, shares

class FeedFanoutService:
    """
    Hybrid fan-out architecture:
    - Fan-out on write for small followings (< 10K followers)
    - Fan-out on read for large followings (> 10K followers)
    """

    def __init__(self, redis_client, db):
        self.redis = redis_client
        self.db = db
        self.CELEBRITY_THRESHOLD = 10000  # Followers

    async def publish_post(self, post: Post):
        """Publish new post and fan out to followers"""

        # Store post
        await self._store_post(post)

        # Get follower count
        follower_count = await self._get_follower_count(post.author_id)

        if follower_count < self.CELEBRITY_THRESHOLD:
            # Fan-out on write
            await self._fanout_on_write(post)
        else:
            # Fan-out on read (mark as celebrity)
            await self._mark_celebrity_post(post)

    async def _fanout_on_write(self, post: Post):
        """Push post to all followers' feeds"""

        # Get all followers
        followers = await self._get_followers(post.author_id)

        # Push to each follower's feed (in batches)
        batch_size = 1000
        for i in range(0, len(followers), batch_size):
            batch = followers[i:i + batch_size]

            # Async push to Redis
            tasks = [
                self._push_to_feed(follower_id, post)
                for follower_id in batch
            ]
            await asyncio.gather(*tasks)

        print(f"Fanned out post {post.id} to {len(followers)} followers")

    async def _mark_celebrity_post(self, post: Post):
        """Mark post for fan-out on read"""

        # Add to celebrity posts list
        await self.redis.zadd(
            f"celebrity_posts:{post.author_id}",
            {post.id: post.created_at}
        )

        # Set TTL (expire after 7 days)
        await self.redis.expire(f"celebrity_posts:{post.author_id}", 7 * 24 * 3600)

    async def _push_to_feed(self, user_id: str, post: Post):
        """Push post to user's feed"""

        feed_key = f"feed:{user_id}"

        # Add to sorted set (score = timestamp)
        await self.redis.zadd(
            feed_key,
            {post.id: post.created_at}
        )

        # Keep only recent 1000 posts
        await self.redis.zremrangebyrank(feed_key, 0, -1001)

    async def get_user_feed(
        self,
        user_id: str,
        limit: int = 20,
        cursor: float = None
    ) -> List[Post]:
        """Get personalized feed for user"""

        # Get feed from cache
        cached_posts = await self._get_cached_feed(user_id, limit, cursor)

        # Merge with celebrity posts (fan-out on read)
        celebrity_posts = await self._get_celebrity_posts(user_id, cursor)

        # Combine and rank
        all_posts = cached_posts + celebrity_posts
        ranked_posts = await self._rank_posts(user_id, all_posts)

        return ranked_posts[:limit]

    async def _get_cached_feed(
        self,
        user_id: str,
        limit: int,
        cursor: float
    ) -> List[Post]:
        """Get posts from pre-computed feed"""

        feed_key = f"feed:{user_id}"

        # Get post IDs from Redis
        if cursor:
            post_ids = await self.redis.zrevrangebyscore(
                feed_key,
                cursor,
                '-inf',
                start=0,
                num=limit
            )
        else:
            post_ids = await self.redis.zrevrange(feed_key, 0, limit - 1)

        # Hydrate posts
        posts = await self._hydrate_posts(post_ids)

        return posts

    async def _get_celebrity_posts(
        self,
        user_id: str,
        cursor: float
    ) -> List[Post]:
        """Get posts from celebrities user follows"""

        # Get celebrity users that user follows
        following = await self._get_following(user_id)
        celebrities = [
            uid for uid in following
            if await self._is_celebrity(uid)
        ]

        # Get their recent posts
        posts = []
        for celebrity_id in celebrities:
            celebrity_posts = await self.redis.zrevrangebyscore(
                f"celebrity_posts:{celebrity_id}",
                cursor or '+inf',
                '-inf',
                start=0,
                num=5  # Get recent 5 posts from each
            )
            posts.extend(await self._hydrate_posts(celebrity_posts))

        return posts

    async def _rank_posts(self, user_id: str, posts: List[Post]) -> List[Post]:
        """Rank posts using ML model or heuristics"""

        # Get user preferences
        user_profile = await self._get_user_profile(user_id)

        # Score each post
        scored_posts = []
        for post in posts:
            score = await self._calculate_post_score(post, user_profile)
            scored_posts.append((score, post))

        # Sort by score
        scored_posts.sort(key=lambda x: x[0], reverse=True)

        return [post for _, post in scored_posts]

    async def _calculate_post_score(
        self,
        post: Post,
        user_profile: Dict
    ) -> float:
        """Calculate relevance score for post"""

        score = 0.0

        # Recency (exponential decay)
        import time
        age_hours = (time.time() - post.created_at) / 3600
        recency_score = 2.0 ** (-age_hours / 24)  # Half-life of 24 hours
        score += recency_score * 10

        # Engagement
        likes = post.engagement.get('likes', 0)
        comments = post.engagement.get('comments', 0)
        shares = post.engagement.get('shares', 0)

        engagement_score = (
            likes * 1.0 +
            comments * 3.0 +  # Comments weighted higher
            shares * 5.0      # Shares weighted highest
        )
        score += engagement_score / 100

        # Author affinity
        author_affinity = user_profile.get('affinity', {}).get(post.author_id, 0)
        score += author_affinity * 5

        # Content type preference
        has_media = len(post.media_urls) > 0
        media_preference = user_profile.get('prefers_media', 0.5)
        if has_media and media_preference > 0.5:
            score += 5

        return score

    # Helper methods (mocked)
    async def _store_post(self, post: Post):
        """Store post in database"""
        pass

    async def _get_follower_count(self, user_id: str) -> int:
        """Get number of followers"""
        return 5000

    async def _get_followers(self, user_id: str) -> List[str]:
        """Get list of follower IDs"""
        return []

    async def _get_following(self, user_id: str) -> List[str]:
        """Get list of users being followed"""
        return []

    async def _is_celebrity(self, user_id: str) -> bool:
        """Check if user is celebrity"""
        return False

    async def _hydrate_posts(self, post_ids: List[str]) -> List[Post]:
        """Load full post objects from IDs"""
        return []

    async def _get_user_profile(self, user_id: str) -> Dict:
        """Get user preferences"""
        return {}
```

### 1.2 Feed Ranking Algorithm

```python
# feed_ranking.py
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier

class FeedRankingModel:
    """
    ML-based feed ranking using gradient boosting
    Predicts probability of user engaging with post
    """

    def __init__(self):
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5
        )
        self.feature_names = [
            'recency_score',
            'engagement_rate',
            'author_affinity',
            'content_similarity',
            'time_of_day_match',
            'has_media',
            'post_length',
            'hashtag_relevance'
        ]

    def extract_features(self, post: Post, user_profile: Dict) -> np.ndarray:
        """Extract features for ranking"""

        import time
        current_time = time.time()

        features = []

        # Recency (hours ago)
        age_hours = (current_time - post.created_at) / 3600
        recency_score = np.exp(-age_hours / 24)  # Exponential decay
        features.append(recency_score)

        # Engagement rate
        total_engagement = sum(post.engagement.values())
        impressions = post.engagement.get('impressions', 1)
        engagement_rate = total_engagement / impressions
        features.append(engagement_rate)

        # Author affinity (how much user interacts with author)
        author_affinity = user_profile.get('affinity', {}).get(post.author_id, 0)
        features.append(author_affinity)

        # Content similarity (cosine similarity of embeddings)
        post_embedding = post.content_embedding  # Assume pre-computed
        user_interests = user_profile.get('interest_embedding')
        content_similarity = np.dot(post_embedding, user_interests) if user_interests else 0
        features.append(content_similarity)

        # Time of day match
        post_hour = int((post.created_at % 86400) / 3600)
        user_active_hours = user_profile.get('active_hours', [])
        time_match = 1.0 if post_hour in user_active_hours else 0.0
        features.append(time_match)

        # Has media
        has_media = 1.0 if post.media_urls else 0.0
        features.append(has_media)

        # Post length
        post_length = len(post.content)
        normalized_length = min(post_length / 280, 1.0)  # Twitter-style
        features.append(normalized_length)

        # Hashtag relevance
        post_hashtags = set(post.hashtags)
        user_interests_hashtags = set(user_profile.get('interest_hashtags', []))
        hashtag_overlap = len(post_hashtags & user_interests_hashtags)
        features.append(hashtag_overlap / max(len(post_hashtags), 1))

        return np.array(features)

    def predict_engagement(self, post: Post, user_profile: Dict) -> float:
        """Predict probability of user engaging with post"""

        features = self.extract_features(post, user_profile)
        features = features.reshape(1, -1)

        # Predict probability
        prob = self.model.predict_proba(features)[0][1]  # Probability of positive class

        return prob

    def train(self, training_data):
        """Train ranking model"""

        X = np.array([item['features'] for item in training_data])
        y = np.array([item['engaged'] for item in training_data])  # Binary label

        self.model.fit(X, y)

        print("Model trained successfully")
```

## Phase 2: Viral Content Detection

### 2.1 Trending Detection

```python
# trending_detector.py
import time
from typing import List, Dict
from collections import defaultdict

class TrendingDetector:
    """Detect trending content and topics"""

    def __init__(self):
        self.topic_counts = defaultdict(lambda: defaultdict(int))
        self.topic_velocities = defaultdict(float)
        self.window_size = 3600  # 1 hour windows

    def record_post(self, post: Post):
        """Record post for trending analysis"""

        current_time = time.time()
        window = int(current_time / self.window_size)

        # Extract hashtags and topics
        topics = self._extract_topics(post)

        for topic in topics:
            self.topic_counts[topic][window] += 1

    def get_trending_topics(self, top_n: int = 10) -> List[Dict]:
        """Get currently trending topics"""

        current_time = time.time()
        current_window = int(current_time / self.window_size)

        trending = []

        for topic, windows in self.topic_counts.items():
            # Get counts for recent windows
            current_count = windows.get(current_window, 0)
            previous_count = windows.get(current_window - 1, 0)

            # Calculate velocity (rate of growth)
            if previous_count > 0:
                velocity = (current_count - previous_count) / previous_count
            else:
                velocity = current_count

            # Score combines volume and velocity
            score = current_count * (1 + velocity)

            trending.append({
                'topic': topic,
                'count': current_count,
                'velocity': velocity,
                'score': score
            })

        # Sort by score
        trending.sort(key=lambda x: x['score'], reverse=True)

        return trending[:top_n]

    def is_trending(self, topic: str) -> bool:
        """Check if topic is trending"""

        trending = self.get_trending_topics(top_n=100)
        return topic in [t['topic'] for t in trending]

    def _extract_topics(self, post: Post) -> List[str]:
        """Extract topics from post"""

        topics = []

        # Hashtags
        topics.extend(post.hashtags)

        # Keywords (simplified - in production use NLP)
        words = post.content.lower().split()
        topics.extend([w for w in words if len(w) > 5])

        return topics
```

## Phase 3: Content Moderation

### 3.1 Automated Moderation Pipeline

```python
# content_moderation.py
import asyncio
from typing import Dict, List
from enum import Enum

class ModerationAction(Enum):
    APPROVED = "approved"
    FLAGGED = "flagged"
    REMOVED = "removed"
    SHADOW_BANNED = "shadow_banned"

class ContentModerator:
    """Automated content moderation system"""

    def __init__(self):
        self.toxicity_threshold = 0.7
        self.spam_threshold = 0.8
        self.flagged_keywords = self._load_flagged_keywords()

    async def moderate_post(self, post: Post) -> Dict:
        """Run moderation checks on post"""

        results = {
            'post_id': post.id,
            'checks': {},
            'action': ModerationAction.APPROVED,
            'confidence': 1.0
        }

        # Run moderation checks in parallel
        checks = await asyncio.gather(
            self._check_toxicity(post),
            self._check_spam(post),
            self._check_keywords(post),
            self._check_image_content(post),
            self._check_user_history(post.author_id)
        )

        toxicity, spam, keywords, images, user_history = checks

        results['checks'] = {
            'toxicity': toxicity,
            'spam': spam,
            'keywords': keywords,
            'images': images,
            'user_history': user_history
        }

        # Determine action
        if toxicity['score'] > self.toxicity_threshold:
            results['action'] = ModerationAction.REMOVED
            results['reason'] = 'toxic_content'
        elif spam['is_spam']:
            results['action'] = ModerationAction.REMOVED
            results['reason'] = 'spam'
        elif keywords['flagged']:
            results['action'] = ModerationAction.FLAGGED
            results['reason'] = 'flagged_keywords'
        elif images['inappropriate']:
            results['action'] = ModerationAction.REMOVED
            results['reason'] = 'inappropriate_image'
        elif user_history['violations'] > 3:
            results['action'] = ModerationAction.SHADOW_BANNED
            results['reason'] = 'repeated_violations'

        return results

    async def _check_toxicity(self, post: Post) -> Dict:
        """Check for toxic/hateful content"""

        # In production: use Perspective API or similar
        # Mock implementation
        toxic_words = ['hate', 'violence', 'abuse']
        score = sum(1 for word in toxic_words if word in post.content.lower()) / 10

        return {
            'score': score,
            'categories': ['toxicity', 'profanity']
        }

    async def _check_spam(self, post: Post) -> Dict:
        """Check for spam content"""

        spam_indicators = 0

        # Check for excessive links
        if post.content.count('http') > 3:
            spam_indicators += 1

        # Check for repeated characters
        if any(char * 5 in post.content for char in 'abcdefghijklmnopqrstuvwxyz'):
            spam_indicators += 1

        # Check for all caps
        if post.content.isupper() and len(post.content) > 20:
            spam_indicators += 1

        is_spam = spam_indicators >= 2

        return {
            'is_spam': is_spam,
            'indicators': spam_indicators
        }

    async def _check_keywords(self, post: Post) -> Dict:
        """Check for flagged keywords"""

        flagged = any(
            keyword in post.content.lower()
            for keyword in self.flagged_keywords
        )

        return {'flagged': flagged}

    async def _check_image_content(self, post: Post) -> Dict:
        """Check images for inappropriate content"""

        if not post.media_urls:
            return {'inappropriate': False}

        # In production: use Google Cloud Vision API or AWS Rekognition
        return {'inappropriate': False}

    async def _check_user_history(self, user_id: str) -> Dict:
        """Check user's moderation history"""

        # Mock implementation
        return {
            'violations': 0,
            'warnings': 0
        }

    def _load_flagged_keywords(self) -> List[str]:
        """Load list of flagged keywords"""
        return ['spam', 'scam', 'fake']
```

## Phase 4: Real-Time Updates

### 4.1 WebSocket Notification System

```typescript
// realtime_notifications.ts
import WebSocket from 'ws';

interface Notification {
    type: 'like' | 'comment' | 'follow' | 'mention' | 'message';
    userId: string;
    actorId: string;
    postId?: string;
    content?: string;
    timestamp: number;
}

class RealtimeNotificationService {
    private wss: WebSocket.Server;
    private userConnections: Map<string, Set<WebSocket>>;

    constructor(port: number) {
        this.wss = new WebSocket.Server({ port });
        this.userConnections = new Map();

        this.setupWebSocketServer();
    }

    private setupWebSocketServer() {
        this.wss.on('connection', (ws: WebSocket, request) => {
            // Authenticate user
            const userId = this.authenticateConnection(request);

            if (!userId) {
                ws.close(1008, 'Authentication failed');
                return;
            }

            // Register connection
            this.registerConnection(userId, ws);

            // Handle messages
            ws.on('message', (data) => {
                this.handleMessage(userId, data.toString());
            });

            // Handle disconnect
            ws.on('close', () => {
                this.unregisterConnection(userId, ws);
            });

            // Send initial connection success
            ws.send(JSON.stringify({
                type: 'connected',
                userId: userId,
                timestamp: Date.now()
            }));
        });
    }

    private registerConnection(userId: string, ws: WebSocket) {
        if (!this.userConnections.has(userId)) {
            this.userConnections.set(userId, new Set());
        }

        this.userConnections.get(userId)!.add(ws);
        console.log(`User ${userId} connected (${this.userConnections.get(userId)!.size} connections)`);
    }

    private unregisterConnection(userId: string, ws: WebSocket) {
        const connections = this.userConnections.get(userId);
        if (connections) {
            connections.delete(ws);

            if (connections.size === 0) {
                this.userConnections.delete(userId);
            }
        }

        console.log(`User ${userId} disconnected`);
    }

    sendNotification(notification: Notification) {
        const connections = this.userConnections.get(notification.userId);

        if (connections) {
            const message = JSON.stringify(notification);

            connections.forEach(ws => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(message);
                }
            });

            console.log(`Sent notification to user ${notification.userId} (${connections.size} devices)`);
        }
    }

    broadcastToFollowers(userId: string, notification: any) {
        // Get all followers
        this.getFollowers(userId).then(followers => {
            followers.forEach(followerId => {
                this.sendNotification({
                    ...notification,
                    userId: followerId
                });
            });
        });
    }

    private authenticateConnection(request: any): string | null {
        // Extract token from query string or headers
        const token = new URL(request.url, 'ws://localhost').searchParams.get('token');

        if (!token) {
            return null;
        }

        // Verify token and extract user ID
        // In production: validate JWT or session token
        return 'user_123';
    }

    private handleMessage(userId: string, message: string) {
        try {
            const data = JSON.parse(message);

            // Handle different message types
            switch (data.type) {
                case 'ping':
                    this.sendToUser(userId, { type: 'pong', timestamp: Date.now() });
                    break;

                case 'typing':
                    // Broadcast typing indicator
                    break;

                default:
                    console.warn(`Unknown message type: ${data.type}`);
            }

        } catch (error) {
            console.error('Error handling message:', error);
        }
    }

    private sendToUser(userId: string, data: any) {
        const connections = this.userConnections.get(userId);

        if (connections) {
            const message = JSON.stringify(data);

            connections.forEach(ws => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(message);
                }
            });
        }
    }

    private async getFollowers(userId: string): Promise<string[]> {
        // Mock implementation
        return [];
    }

    getStats() {
        return {
            totalConnections: Array.from(this.userConnections.values())
                .reduce((sum, connections) => sum + connections.size, 0),
            uniqueUsers: this.userConnections.size
        };
    }
}

// Usage
const notificationService = new RealtimeNotificationService(8080);

// Send notification
notificationService.sendNotification({
    type: 'like',
    userId: 'user_123',
    actorId: 'user_456',
    postId: 'post_789',
    timestamp: Date.now()
});
```

## Best Practices

1. **Use hybrid fan-out**: Write for small accounts, read for celebrities
2. **Implement ranking algorithm**: Personalize feeds with ML
3. **Detect trending content**: Surface viral posts early
4. **Moderate automatically**: Use AI for toxicity/spam detection
5. **Real-time updates**: WebSocket for instant notifications
6. **Cache aggressively**: Redis for hot feeds
7. **Shard by user**: Distribute load across servers
8. **Implement rate limiting**: Prevent spam and abuse
9. **Monitor engagement**: Track CTR, time spent, interactions
10. **A/B test ranking**: Continuously improve feed quality

## Performance Targets

- **Feed generation**: < 200ms for 20 posts
- **Post fanout**: < 1 second for 10K followers
- **Notification delivery**: < 100ms real-time
- **Feed cache hit rate**: > 80%
- **Trending detection**: Update every 5 minutes
- **Moderation latency**: < 500ms per post

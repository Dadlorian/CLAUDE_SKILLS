# Social Media Feed Algorithms Reference

## Platform Comparison

| Platform | Primary Algorithm | Ranking Factors | Update Frequency |
|----------|------------------|-----------------|------------------|
| **Twitter/X** | Reverse chronological + "For You" | Recency, engagement, interests | Real-time |
| **Instagram** | Interest-based ranking | Relationships, interests, recency | Every refresh |
| **TikTok** | For You Page (FYP) | Watch time, completion, shares | Per scroll |
| **Facebook** | News Feed ranking | Meaningful interactions, recency | Every load |
| **LinkedIn** | Professional relevance | Connections, industry, engagement | Every load |
| **Reddit** | Hot/Best algorithms | Upvotes, comments, recency | Per view |

## Ranking Signals

### User Engagement Signals (by weight)

| Signal | Weight | Why Important |
|--------|--------|---------------|
| **Shares** | 10x | Strongest signal of value |
| **Saves** | 8x | Indicates future reference value |
| **Comments** | 5x | Deep engagement |
| **Likes** | 1x | Baseline engagement |
| **Clicks** | 3x | Interest signal |
| **Video completion** | 7x | Time investment |
| **Dwell time** | 4x | Content quality |

### Content Features

| Feature | Impact | Platform |
|---------|--------|----------|
| **Has media (image/video)** | +15% engagement | All |
| **Optimal length (100-250 chars)** | +20% | Twitter |
| **Hashtags (2-5 optimal)** | +12% reach | Instagram |
| **Questions** | +30% comments | Facebook |
| **Listicles** | +25% shares | LinkedIn |
| **Native video** | 3x views vs links | Facebook |
| **Stories** | +40% daily engagement | Instagram |

### Temporal Factors

| Factor | Decay Function | Half-Life |
|--------|---------------|-----------|
| **Recency** | Exponential | 6-24 hours |
| **Trending** | Velocity-based | 1-4 hours |
| **Evergreen** | Logarithmic | 7-30 days |
| **Seasonal** | Cyclic | 1 year |

## Feed Generation Architectures

### Fan-Out on Write (Push Model)

**Best for:** Small followings (< 10K followers)

```
Post → Fan out to all followers' feeds → Cache in Redis
Pros: Fast reads, simple
Cons: Slow writes for popular users, storage cost
```

### Fan-Out on Read (Pull Model)

**Best for:** Large followings (> 100K followers)

```
Post → Store in author's timeline → Generate feed on request
Pros: Fast writes, low storage
Cons: Slow reads, compute cost
```

### Hybrid (Twitter's approach)

```
Small accounts: Fan-out on write
Large accounts: Fan-out on read
Celebrity accounts: Mixed (sample + on-demand)
```

## Viral Content Detection

### Trending Score Formula

```
Score = Engagement_Rate × Velocity × Recency_Factor

Where:
- Engagement_Rate = (Likes + 3×Comments + 5×Shares) / Impressions
- Velocity = Current_Hour_Count / Previous_Hour_Count
- Recency_Factor = e^(-hours_ago / 24)
```

### Virality Thresholds

| Metric | Normal | Trending | Viral |
|--------|--------|----------|-------|
| **Engagement rate** | 2-5% | 10-20% | > 25% |
| **Growth velocity** | 1.0-1.5x | 2-5x | > 10x |
| **Share ratio** | < 1% | 5-10% | > 15% |
| **Velocity (posts/hour)** | < 10 | 50-100 | > 500 |

## Content Moderation

### Moderation Pipeline

```
1. Pre-screening (< 100ms)
   - Keyword matching
   - Spam detection
   - Rate limiting

2. Automated review (< 500ms)
   - Toxicity scoring (Perspective API)
   - Image moderation (Vision AI)
   - Duplicate detection

3. Human review (priority queue)
   - Flagged content
   - Appeals
   - Edge cases
```

### Toxicity Thresholds (Perspective API)

| Category | Threshold | Action |
|----------|-----------|--------|
| **Severe Toxicity** | > 0.9 | Auto-remove |
| **Identity Attack** | > 0.8 | Auto-remove |
| **Threat** | > 0.7 | Flag for review |
| **Profanity** | > 0.8 | Flag/Shadow-ban |
| **Spam** | > 0.9 | Auto-remove |

## Performance Benchmarks

### Feed Generation

| Metric | Target | P95 | P99 |
|--------|--------|-----|-----|
| **Feed generation** | 100ms | 200ms | 500ms |
| **Post ranking** | 50ms | 100ms | 200ms |
| **Cache lookup** | 10ms | 20ms | 50ms |
| **Post hydration** | 30ms | 60ms | 100ms |

### Fan-Out Performance

| Followers | Write Time | Storage/Post |
|-----------|-----------|--------------|
| **1K** | 50ms | 100KB |
| **10K** | 500ms | 1MB |
| **100K** | 5s | 10MB |
| **1M** | 50s | 100MB |

## Storage Requirements

### Per User

| Component | Size |
|-----------|------|
| **Feed cache (1000 posts)** | 500KB |
| **User profile** | 10KB |
| **Relationships** | 50KB (per 1K follows) |
| **Total** | ~1MB per active user |

### Per Post

| Component | Size |
|-----------|------|
| **Text content** | 1KB |
| **Metadata** | 2KB |
| **Media URL** | 500B |
| **Engagement counters** | 100B |
| **Total** | ~4KB |

## Notification Strategies

### Real-Time vs Batched

| Notification Type | Delivery | Batch Window |
|------------------|----------|--------------|
| **Direct message** | Real-time | N/A |
| **Mentions** | Real-time | N/A |
| **Likes** | Batched | 5-15 minutes |
| **Follows** | Batched | 1 hour |
| **Weekly digest** | Batched | 7 days |

### Push Notification Rates

| User Activity | Daily Limit | Reasoning |
|--------------|-------------|-----------|
| **Very Active** | 20+ | Won't feel spam |
| **Active** | 10-15 | Engaged but sensitive |
| **Moderate** | 5-8 | Risk of uninstall |
| **Inactive** | 1-2 | Re-engagement only |

## A/B Testing Metrics

### Primary Metrics

| Metric | Definition | Target Change |
|--------|-----------|---------------|
| **DAU/MAU** | Daily Active / Monthly Active | > 40% |
| **Time on platform** | Minutes per session | +5-10% |
| **Posts created** | User-generated content | +10-15% |
| **Engagement rate** | Actions / Impressions | +5-8% |
| **Retention (D7)** | Users active after 7 days | +2-5% |

### Secondary Metrics

- Feed scroll depth
- Video completion rate
- Share rate
- Save rate
- Profile visits
- Search usage

## Recommendation Patterns

### Collaborative Filtering

```python
# Find similar users
similar_users = users_with_similar_interests(user_id)

# Aggregate their liked content
recommended = aggregate_content(similar_users, exclude=user_seen)

# Rank by relevance
ranked = rank_by_affinity(recommended, user_profile)
```

### Content-Based Filtering

```python
# Get user's liked content
user_likes = get_user_likes(user_id)

# Extract features
user_interests = extract_features(user_likes)

# Find similar content
recommended = find_similar_content(user_interests)

# Rank by similarity
ranked = rank_by_similarity(recommended, user_interests)
```

### Hybrid Approach (Instagram/TikTok)

```python
# Combine signals
score = (
    collaborative_score * 0.4 +
    content_similarity * 0.3 +
    trending_score * 0.2 +
    recency_score * 0.1
)
```

## Common Pitfalls

1. **Filter bubble**: Show only similar content → Inject diversity
2. **Engagement bait**: Click-bait gets high engagement → Downrank
3. **Amplifying toxicity**: Outrage drives engagement → Content moderation
4. **Bot amplification**: Fake accounts boost posts → Bot detection
5. **Echo chambers**: Reinforce existing views → Show diverse perspectives
6. **Addiction patterns**: Infinite scroll → Mindful design
7. **Misinformation**: Viral false content → Fact-checking
8. **Privacy concerns**: Personalization requires data → Transparency

## Tools & Technologies

### Feed Infrastructure

- **Redis**: Feed caching, real-time updates
- **Cassandra**: Post storage, time-series data
- **Kafka**: Event streaming, fan-out
- **Elasticsearch**: Content search, trending detection

### ML/Ranking

- **TensorFlow/PyTorch**: Deep learning models
- **LightGBM/XGBoost**: Gradient boosting trees
- **FAISS**: Similarity search, recommendations
- **Kubeflow**: ML pipeline orchestration

### Moderation

- **Perspective API**: Toxicity detection
- **Google Cloud Vision**: Image moderation
- **AWS Rekognition**: Video moderation
- **Clarifai**: NSFW detection

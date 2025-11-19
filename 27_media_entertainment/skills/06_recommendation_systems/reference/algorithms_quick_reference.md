# Recommendation Algorithms Quick Reference

## Algorithm Comparison

| Algorithm | Best For | Pros | Cons | Latency |
|-----------|----------|------|------|---------|
| **Collaborative Filtering** | Users with history | Simple, effective | Cold start, sparse data | Low |
| **Content-Based** | New items, niche content | No cold start for items | Limited discovery | Low |
| **Matrix Factorization** | Large-scale implicit feedback | Scalable, accurate | Requires tuning | Medium |
| **Two-Tower (Deep Learning)** | Large catalogs, complex patterns | Very accurate | Training cost, cold start | Low (with ANN) |
| **Contextual Bandits** | Exploration needed | Adapts quickly | Requires experimentation | Low |
| **Graph Neural Networks** | Social/knowledge graphs | Captures relationships | Complex, slow training | Medium |

## When to Use Each Algorithm

### Collaborative Filtering (User-Based)
**Use when:**
- You have explicit ratings (5-star, thumbs up/down)
- Users have rich interaction history
- Item catalog is relatively stable

**Example:** Early Netflix, Amazon product ratings

### Collaborative Filtering (Item-Based)
**Use when:**
- More items than users
- Item relationships are stable
- Need explainability ("People who liked X also liked Y")

**Example:** Amazon "Customers who bought this also bought", YouTube related videos

### Matrix Factorization (ALS, SVD)
**Use when:**
- Implicit feedback (views, clicks)
- Large-scale data (millions of users/items)
- Need to capture latent factors

**Example:** Spotify Discover Weekly, Netflix personalized rows

### Two-Tower Model
**Use when:**
- Very large item catalog (millions+)
- Complex user/item features
- Need real-time serving at scale

**Example:** YouTube homepage, TikTok For You page

### Contextual Bandits
**Use when:**
- Need to balance exploration vs exploitation
- Rapidly changing content (news, trending)
- Limited historical data

**Example:** News recommendations, ad placement

### Hybrid Approaches
**Use when:**
- Want best of multiple worlds
- Have diverse content types
- Need robust cold start handling

**Example:** Most production systems (Netflix, Spotify, Amazon)

## Key Metrics Reference

### Offline Metrics
| Metric | Formula | Good Value | Notes |
|--------|---------|------------|-------|
| **RMSE** | √(Σ(predicted - actual)² / n) | < 0.9 | For explicit ratings |
| **MAE** | Σ\|predicted - actual\| / n | < 0.7 | More robust to outliers |
| **Precision@K** | relevant items in top K / K | > 0.3 | Fraction relevant |
| **Recall@K** | relevant in top K / total relevant | > 0.2 | Coverage of relevant |
| **NDCG** | DCG / IDCG | > 0.4 | Ranking quality |
| **MAP** | Mean Average Precision | > 0.3 | Overall ranking |
| **Coverage** | unique items recommended / catalog | > 0.8 | Catalog exposure |
| **Diversity** | 1 - avg similarity(items) | > 0.3 | Avoid filter bubbles |

### Online Metrics
| Metric | Target | Priority |
|--------|--------|----------|
| **CTR** | > 10% lift vs baseline | Critical |
| **Conversion Rate** | > 5% lift | Critical |
| **Watch Time** | > 15% lift | Critical |
| **User Engagement** | > 10% sessions with recs | High |
| **Retention** | > 5% D7 retention lift | High |
| **Revenue** | > 8% lift | Critical |

## Cold Start Solutions

### New User Cold Start
| Approach | Pros | Cons |
|----------|------|------|
| **Popularity-based** | Simple, effective | Not personalized |
| **Content-based** | Uses item metadata | Needs good metadata |
| **Ask preferences** | Quick personalization | User friction |
| **Demographic** | Better than random | Privacy concerns |
| **Contextual** | Uses device/time signals | Limited signal |

### New Item Cold Start
| Approach | Pros | Cons |
|----------|------|------|
| **Content-based** | Works immediately | Needs metadata |
| **Explore-exploit** | Learns quickly | Some wasted impressions |
| **Seed to similar users** | Targeted | Needs seed users |
| **Metadata matching** | Fast | Limited accuracy |

## Embedding Dimensions Guide

| Catalog Size | Recommended Dim | Memory/Item | Notes |
|--------------|----------------|-------------|-------|
| < 1K items | 32-64 | 128-256 bytes | Small catalog |
| 1K-10K | 64-128 | 256-512 bytes | Medium catalog |
| 10K-100K | 128-256 | 512 bytes-1KB | Large catalog |
| 100K-1M | 256-512 | 1-2KB | Very large |
| 1M+ | 512-1024 | 2-4KB | Massive scale |

**Rule of thumb:** embedding_dim = ⌈log₂(catalog_size)⌉ × 4

## Training Data Requirements

| Users | Items | Interactions | Min for CF | Min for DL |
|-------|-------|--------------|-----------|-----------|
| 1K | 1K | 10K | ✓ | ✗ |
| 10K | 5K | 100K | ✓ | △ |
| 100K | 10K | 1M | ✓ | ✓ |
| 1M | 50K | 10M | ✓ | ✓ |
| 10M+ | 100K+ | 100M+ | ✓ | ✓✓ |

Legend: ✓ = Good, △ = Marginal, ✗ = Insufficient, ✓✓ = Ideal

## Latency Budgets

| Component | Target | P95 | P99 |
|-----------|--------|-----|-----|
| **Feature retrieval** | < 10ms | 20ms | 50ms |
| **Model inference** | < 20ms | 50ms | 100ms |
| **Ranking** | < 10ms | 20ms | 30ms |
| **Business rules** | < 5ms | 10ms | 20ms |
| **Total API** | < 50ms | 100ms | 200ms |

## Retraining Frequency

| Content Type | Retrain Frequency | Reason |
|--------------|------------------|--------|
| **Fast-moving (news, social)** | Hourly | Content changes fast |
| **Trending (music, video)** | Daily | Trends emerge daily |
| **Stable (movies, books)** | Weekly | Slower changes |
| **Long-tail (niche)** | Monthly | Very stable |

## Infrastructure Sizing

### For 1M daily active users:

| Component | Count | Specs |
|-----------|-------|-------|
| **API servers** | 10-20 | 8 vCPU, 16GB RAM |
| **Model serving** | 5-10 | 16 vCPU, 32GB RAM, GPU optional |
| **Redis cache** | 3-5 | 32GB RAM each |
| **Training cluster** | 1 | 32+ vCPU, 64GB+ RAM, GPUs |
| **Feature store** | 3-5 | 16 vCPU, 32GB RAM |

### Storage Requirements:

- **User embeddings**: 1M users × 512 dims × 4 bytes = 2GB
- **Item embeddings**: 100K items × 512 dims × 4 bytes = 200MB
- **Interaction history**: 1M users × 100 items × 16 bytes = 1.6GB
- **Cache (hot data)**: 10-20GB

## Common Pitfalls

1. **Position bias**: Items shown first get more clicks → Use position-aware models
2. **Popularity bias**: Popular items dominate → Apply diversity constraints
3. **Filter bubble**: Users stuck in narrow niche → Inject serendipity
4. **Cold start**: New users/items get poor recs → Have fallback strategies
5. **Feedback loops**: Recommendations bias future data → Use exploration
6. **Data leakage**: Train on future data → Strict temporal splits
7. **Offline/online gap**: Metrics don't match → Track both carefully
8. **Scalability**: Model doesn't scale → Use ANN, caching, async
9. **Staleness**: Recs become outdated → Retrain frequently
10. **Overfitting**: Model memorizes training → Use regularization, validation

## Quick Start Checklist

- [ ] Define success metrics (CTR, watch time, retention)
- [ ] Collect interaction data (views, clicks, ratings)
- [ ] Build feature pipeline (user, item, contextual features)
- [ ] Train baseline model (collaborative filtering)
- [ ] Set up serving infrastructure (API, cache)
- [ ] Implement A/B testing framework
- [ ] Monitor online metrics
- [ ] Iterate: add models, features, business rules
- [ ] Scale infrastructure as traffic grows
- [ ] Retrain models regularly with fresh data

## Resource Links

### Papers
- **Netflix Prize**: Matrix Factorization Techniques (Koren, 2009)
- **YouTube**: Deep Neural Networks for YouTube Recommendations (Covington, 2016)
- **Two-Tower**: Sampling-Bias-Corrected Neural Modeling (Yi, 2019)

### Libraries
- **Python**: Surprise, LightFM, TensorFlow Recommenders
- **Scala/Java**: Apache Spark MLlib ALS
- **ANN**: FAISS (Facebook), Annoy (Spotify), ScaNN (Google)

### Tools
- **Feature Store**: Feast, Tecton
- **Experimentation**: Optimizely, LaunchDarkly
- **Monitoring**: Prometheus, Grafana, DataDog

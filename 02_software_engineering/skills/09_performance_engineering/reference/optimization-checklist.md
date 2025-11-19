# Performance Optimization Checklist

## Backend Performance

### Database
- [ ] Add indexes for WHERE, JOIN, ORDER BY columns
- [ ] Use composite indexes for multi-column queries
- [ ] Analyze slow queries with EXPLAIN ANALYZE
- [ ] Eliminate N+1 queries (use JOINs or DataLoader)
- [ ] Implement connection pooling (min: 5, max: 20)
- [ ] Use read replicas for read-heavy loads
- [ ] Implement query result caching (Redis)
- [ ] Use cursor-based pagination for large datasets
- [ ] Regular VACUUM and ANALYZE
- [ ] Remove unused indexes

### API
- [ ] Implement rate limiting
- [ ] Add response compression (gzip/Brotli)
- [ ] Use HTTP/2 or HTTP/3
- [ ] Implement API response caching
- [ ] Add ETags for conditional requests
- [ ] Batch API requests where possible
- [ ] Implement request timeout handling
- [ ] Monitor response times (< 200ms target)

### Caching
- [ ] CDN for static assets
- [ ] Redis for session/data caching
- [ ] Application-level caching
- [ ] Database query caching
- [ ] Implement cache warming
- [ ] Set appropriate TTLs
- [ ] Implement cache invalidation strategy

### Application
- [ ] Use async/await for I/O operations
- [ ] Implement worker threads for CPU-intensive tasks
- [ ] Optimize JSON parsing
- [ ] Use streaming for large data
- [ ] Minimize middleware chains
- [ ] Profile and optimize hot paths
- [ ] Implement graceful shutdown

## Frontend Performance

### Core Web Vitals
- [ ] LCP < 2.5s (optimize images, lazy load)
- [ ] FID < 100ms (reduce JavaScript execution)
- [ ] CLS < 0.1 (set dimensions, reserve space)

### Loading Performance
- [ ] Code splitting by route
- [ ] Lazy load components below fold
- [ ] Preload critical resources
- [ ] Use resource hints (dns-prefetch, preconnect)
- [ ] Minimize third-party scripts
- [ ] Implement service worker caching

### Image Optimization
- [ ] Use next/image or similar
- [ ] Serve WebP/AVIF formats
- [ ] Implement responsive images
- [ ] Lazy load images below fold
- [ ] Optimize image dimensions
- [ ] Use CDN for image delivery

### JavaScript
- [ ] Bundle size < 200KB (gzipped)
- [ ] Tree shake unused code
- [ ] Remove console.log in production
- [ ] Use production builds
- [ ] Minimize polyfills
- [ ] Defer non-critical scripts

### CSS
- [ ] Inline critical CSS
- [ ] Remove unused CSS
- [ ] Minify CSS
- [ ] Use CSS-in-JS efficiently
- [ ] Avoid @import in CSS
- [ ] Optimize fonts (FOUT strategy)

### React Specific
- [ ] Use React.memo for pure components
- [ ] Implement useMemo for expensive calculations
- [ ] Use useCallback for stable function references
- [ ] Virtualize long lists
- [ ] Avoid inline function definitions in JSX
- [ ] Debounce user inputs

## Monitoring

### Metrics to Track
- [ ] Response time (p50, p95, p99)
- [ ] Error rate
- [ ] Request throughput
- [ ] Database query time
- [ ] Cache hit rate
- [ ] CPU and memory usage
- [ ] Core Web Vitals

### Tools
- [ ] Set up APM (Datadog, New Relic)
- [ ] Configure error tracking (Sentry)
- [ ] Implement custom metrics
- [ ] Set up alerts for anomalies
- [ ] Create performance dashboards
- [ ] Enable distributed tracing

## Load Testing

- [ ] Test with expected peak load
- [ ] Test with 2x expected load
- [ ] Test sustained load over time
- [ ] Identify bottlenecks
- [ ] Test autoscaling behavior
- [ ] Test database connection limits

## Performance Targets

### Backend
- API response time: < 200ms (p95)
- Database queries: < 50ms (p95)
- Cache hit rate: > 80%
- Error rate: < 0.1%

### Frontend
- LCP: < 2.5s
- FID: < 100ms
- CLS: < 0.1
- TTI: < 3.5s
- Bundle size: < 200KB

## Quick Wins

1. **Enable compression** (gzip/Brotli)
2. **Add database indexes** for common queries
3. **Implement CDN** for static assets
4. **Add Redis caching** for frequent queries
5. **Optimize images** (WebP, proper sizing)
6. **Code split** by route
7. **Enable HTTP/2**
8. **Add connection pooling**
9. **Lazy load** below-fold content
10. **Minify and compress** assets

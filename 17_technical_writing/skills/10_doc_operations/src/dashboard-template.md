# Documentation Health Dashboard Template

## 📊 Dashboard Metrics

This template shows how to create a comprehensive documentation metrics dashboard.

---

## 1. Usage Metrics (Current Month)

### Page Views & Visitors

**Last 30 Days Trend**:

| Metric | Current | Previous Month | Change |
|--------|---------|-----------------|--------|
| **Page Views** | 125,450 | 112,300 | ↑ 11.7% |
| **Unique Visitors** | 45,230 | 42,100 | ↑ 7.4% |
| **Avg Pages/Session** | 2.8 | 2.5 | ↑ 12% |
| **Avg Session Duration** | 3:24 | 2:56 | ↑ 16% |
| **Bounce Rate** | 35% | 42% | ↓ 7% |

**Top 10 Pages**:

| Rank | Page | Views | Avg Time | Bounce% |
|------|------|-------|----------|---------|
| 1 | Getting Started | 12,450 | 4:32 | 28% |
| 2 | API Reference | 11,280 | 5:15 | 22% |
| 3 | Authentication | 9,870 | 3:42 | 35% |
| 4 | Charge Creation | 8,450 | 4:08 | 38% |
| 5 | Error Handling | 7,620 | 3:25 | 42% |
| 6 | Webhooks | 6,890 | 4:45 | 30% |
| 7 | Rate Limiting | 5,670 | 2:58 | 48% |
| 8 | Release Notes | 4,560 | 2:15 | 55% |
| 9 | FAQ | 3,450 | 3:05 | 40% |
| 10 | Troubleshooting | 2,980 | 3:48 | 36% |

---

## 2. Search Analytics

### Search Performance

**Last 30 Days**:

| Metric | Value | Status |
|--------|-------|--------|
| **Search Usage Rate** | 42% | ↑ Good |
| **Search Success Rate** | 73% | ✅ Above Target (>70%) |
| **Avg Results Clicked** | 1.8 | ⚠️ Monitor |
| **Abandonment Rate** | 27% | ❌ Above Target (target: <20%) |

**Top 10 Searches**:

| Rank | Search Query | Searches | Clicks | Success% |
|------|--------------|----------|--------|----------|
| 1 | authentication | 2,340 | 1,890 | 81% |
| 2 | rate limits | 1,890 | 1,560 | 82% |
| 3 | webhooks | 1,650 | 1,240 | 75% |
| 4 | error codes | 1,430 | 980 | 68% |
| 5 | create charge | 1,280 | 1,150 | 90% |
| 6 | refund | 1,120 | 890 | 79% |
| 7 | testing | 980 | 650 | 66% |
| 8 | deployment | 870 | 720 | 83% |
| 9 | cors | 750 | 450 | 60% |
| 10 | pagination | 680 | 380 | 56% |

**Failed Searches** (queries with 0 clicks):

- "idempotency key" (120 searches) - Need content
- "batch operations" (85 searches) - Not documented yet
- "v1 migration" (75 searches) - Need migration guide
- "sandbox testing" (60 searches) - Need testing guide

---

## 3. Content Quality Metrics

### Freshness

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **Updated < 30 days** | 82% | >80% | ✅ |
| **Updated < 90 days** | 68% | >70% | ⚠️ |
| **Stale (>180 days)** | 8% | <5% | ❌ |

**Stale Content** (not updated in 6+ months):

- Release Notes (Last updated: 5 months ago) - `docs/release-notes/`
- Troubleshooting Guide (Last updated: 7 months ago) - `docs/troubleshooting.md`
- FAQ (Last updated: 6 months ago) - `docs/faq.md`
- Deprecated Features (Last updated: 9 months ago) - `docs/deprecated.md`

### Completeness

| Aspect | Coverage | Status |
|--------|----------|--------|
| **API Endpoints** | 98/100 (98%) | ✅ |
| **Guide Coverage** | 28/30 (93%) | ⚠️ |
| **Tutorial Coverage** | 12/15 (80%) | ❌ |
| **Video Coverage** | 5/25 (20%) | ❌ |

**Missing Content**:

- Tutorial: "Build a Multi-Tenant Application"
- Tutorial: "Implement Custom Webhooks"
- Tutorial: "Database Scaling Guide"
- Guide: "Batch Processing Best Practices"
- Guide: "Performance Optimization"

### Broken Links

| Type | Count | Status |
|------|-------|--------|
| **External Links** | 0 | ✅ |
| **Internal Links** | 3 | ❌ |
| **API References** | 0 | ✅ |

**Broken Links Found**:

1. `docs/troubleshooting.md` line 45:
   - Link: `/docs/deprecated-endpoints`
   - Should be: `/docs/migration-guide`

2. `docs/api/charges.md` line 120:
   - Link: `/docs/charge-object` (404)
   - Should be: `/docs/api/charge-resource`

3. `docs/guides/webhooks.md` line 230:
   - Link: `https://github.com/example/webhook-examples` (404)
   - Status: Repo moved

---

## 4. Accessibility Metrics

### Compliance

| Metric | Score | Status |
|--------|-------|--------|
| **WCAG 2.2 AA Compliance** | 96% | ✅ |
| **Lighthouse Accessibility** | 96/100 | ✅ |
| **Screen Reader Testing** | ✅ | ✅ |
| **Keyboard Navigation** | ✅ | ✅ |

**Issues Found** (4 items):

1. Missing alt text on 2 images in `/guides/architecture`
2. Form in `/tutorials/api-setup` missing labels on 3 inputs
3. Color contrast issue in dark mode on `/changelog`
4. Missing h1 tag on `/api/overview`

---

## 5. Performance Metrics

### Load Times

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **Avg Page Load Time** | 1.8s | <2s | ✅ |
| **Time to First Byte** | 0.4s | <0.5s | ✅ |
| **First Contentful Paint** | 1.2s | <1.5s | ✅ |
| **Largest Contentful Paint** | 1.8s | <2.5s | ✅ |

### Core Web Vitals

| Metric | Value | Status |
|--------|-------|--------|
| **CLS** (Layout Shift) | 0.08 | ✅ Good |
| **FID** (Interaction) | 45ms | ✅ Good |
| **LCP** (Largest Paint) | 1.8s | ✅ Good |

**Lighthouse Score**: 94/100

---

## 6. User Satisfaction

### Helpfulness Ratings

| Metric | Value | Status |
|--------|-------|--------|
| **"Helpful" Rating** | 82% | ✅ Above Target (>80%) |
| **"Not Helpful" Rating** | 18% | ✅ |
| **Sample Size (30 days)** | 8,450 responses | |

**Helpful by Section**:

| Section | Helpful | Sample |
|---------|---------|--------|
| Getting Started | 88% | 1,200 |
| API Reference | 79% | 1,100 |
| Tutorials | 85% | 950 |
| Guides | 81% | 1,050 |
| Release Notes | 72% | 680 |
| FAQ | 83% | 750 |
| Troubleshooting | 76% | 890 |

### Feedback Analysis

**Common Feedback Themes**:

| Issue | Mentions | % |
|-------|----------|-----|
| "Could use more examples" | 340 | 32% |
| "Steps not clear" | 210 | 20% |
| "Missing information" | 185 | 17% |
| "Outdated" | 95 | 9% |
| "Too technical" | 80 | 8% |
| "Not enough context" | 70 | 7% |
| "Code samples don't work" | 45 | 4% |
| "Other" | 35 | 3% |

**Action Items**:
- [ ] Add more practical examples (highest complaint)
- [ ] Simplify technical explanations
- [ ] Update release notes (marked outdated)
- [ ] Test all code samples

### NPS (Net Promoter Score)

**Calculation**: % Promoters (9-10) - % Detractors (0-6)

| Score | Count | % | Category |
|-------|-------|---|----------|
| 0-6 | 240 | 9% | Detractors |
| 7-8 | 920 | 35% | Passives |
| 9-10 | 1,440 | 56% | Promoters |

**NPS Score**: 56 - 9 = **47** ✅ (Target: >40)

---

## 7. Business Impact

### Conversion Metrics

| Metric | Value | Status |
|--------|-------|--------|
| **Docs to Signup** | 12% | ↑ 2% vs last month |
| **Docs to Trial** | 8% | ↑ 1% |
| **Signup to Paid** | 28% | → No change |

**Funnel Analysis**:

```
Docs Visited: 45,230
↓ 85% click "Get Started"
Signup Page: 38,445
↓ 31% complete signup
Active Trials: 11,918
↓ 28% convert to paid
Paid Customers: 3,337
```

### Support Deflection

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Support Tickets** | 450 | <500 | ✅ |
| **Deflection Rate** | 64% | 60-70% | ✅ |
| **Cost Savings** | $48,000/mo | | |

**Top Support Topics (that docs could help)**:

1. "How do I get my API key?" - 45 tickets/month
   - Solution: Improve Getting Started guide
2. "Why is my charge failing?" - 32 tickets/month
   - Solution: Expand error codes documentation
3. "How do I test locally?" - 28 tickets/month
   - Solution: Create sandbox testing guide
4. "What's the rate limit?" - 24 tickets/month
   - Solution: Better rate limiting documentation

---

## 8. Key Performance Indicators Summary

### Overall Health Score: 87/100 ✅

**Scoring Breakdown**:

| Category | Score | Weight | Total |
|----------|-------|--------|-------|
| Usage | 90 | 20% | 18 |
| Quality | 82 | 25% | 20.5 |
| Search | 73 | 15% | 11 |
| Performance | 98 | 15% | 14.7 |
| Satisfaction | 85 | 15% | 12.75 |
| Business Impact | 88 | 10% | 8.8 |
| **TOTAL** | | | **87** |

---

## 9. Trends (Last 3 Months)

### Growth

- Page views: ↑ 28% (Jan: 97K → Feb: 112K → Mar: 125K)
- Unique visitors: ↑ 22% (Jan: 37K → Feb: 41K → Mar: 45K)
- Search usage: ↑ 15% (Jan: 36% → Feb: 39% → Mar: 42%)
- Helpfulness: ↑ 8% (Jan: 76% → Feb: 79% → Mar: 82%)

### Engagement

- Avg session duration: ↑ 18% (Feb: 2:54 → Mar: 3:24)
- Pages per session: ↑ 12% (Feb: 2.5 → Mar: 2.8)
- Bounce rate: ↓ 16% (Feb: 42% → Mar: 35%)

### Content

- New pages: 8 added
- Updated pages: 42
- Outdated content: ↓ 3% (Feb: 11% → Mar: 8%)

---

## 10. Action Items

### High Priority (This Week)

- [ ] Fix 3 broken links (see section 3)
- [ ] Update 8 stale pages (over 180 days old)
- [ ] Add examples to top 5 "not helpful" topics
- [ ] Fix accessibility issues (alt text, form labels)

### Medium Priority (This Month)

- [ ] Create "Batch Processing" guide (15 failed searches)
- [ ] Create sandbox testing guide (28 support tickets)
- [ ] Improve error code documentation
- [ ] Add more video tutorials (currently only 20% coverage)

### Low Priority (Next Quarter)

- [ ] Redesign API Reference (currently 79% helpful)
- [ ] Add performance optimization guide
- [ ] Create advanced tutorials
- [ ] Setup A/B testing for documentation approaches

---

## 11. Alerts & Thresholds

### Current Alerts

🔴 **Critical**:
- Stale content: 8% (threshold: >5%)
- Rate-limiting tutorials missing (15 failed searches this month)

🟡 **Warning**:
- Bounce rate on Release Notes: 55% (monitor for increase)
- Search abandonment: 27% (target: <20%)
- Broken links: 3 items (should be 0)

✅ **Healthy**:
- Page load time: 1.8s (target: <2s)
- Accessibility: 96% (target: >95%)
- Helpfulness: 82% (target: >80%)
- NPS: 47 (target: >40)

---

## 12. Next Review

- **Weekly**: Monitor search abandonment, broken links
- **Monthly**: Review all metrics, plan content updates
- **Quarterly**: Strategic review, plan major initiatives

**Last Updated**: November 19, 2025
**Next Review**: December 19, 2025
**Dashboard Maintainer**: Documentation Team

---

## How to Use This Dashboard

### For Content Team

1. Check "Stale Content" section for pages to update
2. Review "Failed Searches" for missing documentation needs
3. Look at "Feedback Themes" to improve content
4. Monitor "Broken Links" regularly

### For Product Team

1. Track "Business Impact" metrics
2. Monitor "Support Deflection" for ROI
3. Review "Conversion Funnel" for optimization
4. Check "Top Support Topics" for product insights

### For Leadership

1. Review "Overall Health Score"
2. Track "Key Performance Indicators"
3. Monitor "Trends" for growth patterns
4. Review "Action Items" progress

---

## Tools Used

- **Analytics**: Google Analytics 4
- **Search**: Algolia Analytics
- **Performance**: Lighthouse, Web Vitals
- **Accessibility**: WAVE, Pa11y
- **Custom Tracking**: JavaScript event tracking
- **Dashboard**: Tableau / Data Studio / Custom build


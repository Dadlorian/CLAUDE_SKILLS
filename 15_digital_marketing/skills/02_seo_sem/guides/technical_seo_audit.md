# Complete Technical SEO Audit Guide

A comprehensive, step-by-step guide to conducting professional technical SEO audits that identify and fix critical issues impacting search performance.

## Table of Contents
1. [Audit Overview](#overview)
2. [Pre-Audit Setup](#setup)
3. [Crawl Analysis](#crawl)
4. [Core Web Vitals & Performance](#performance)
5. [Mobile-First & Responsive](#mobile)
6. [Structured Data & Schema](#schema)
7. [JavaScript & Rendering](#javascript)
8. [Indexability & Crawlability](#indexing)
9. [Internal Linking](#links)
10. [Prioritization Matrix](#prioritization)

---

## Audit Overview {#overview}

### What is a Technical SEO Audit?

A technical SEO audit systematically reviews a website's technical infrastructure to identify issues that prevent optimal search engine crawling, indexing, and ranking.

**Key Goals:**
- Identify technical barriers to crawling and indexing
- Optimize site speed and Core Web Vitals
- Ensure mobile-friendliness
- Implement proper structured data
- Fix broken links and redirects
- Optimize site architecture

### Tools Required

**Essential Tools:**
- Screaming Frog SEO Spider (or Sitebulb)
- Google Search Console
- Google PageSpeed Insights
- Chrome DevTools (Lighthouse)
- Ahrefs or SEMrush (for backlinks and indexation)

**Optional Tools:**
- GTmetrix or WebPageTest (performance)
- Mobile-Friendly Test
- Rich Results Test
- Log file analyzer

---

## Pre-Audit Setup {#setup}

### Access & Credentials Checklist

Before starting, ensure you have:
- [ ] Google Search Console access (verified property)
- [ ] Google Analytics access
- [ ] Server access (for robots.txt, logs)
- [ ] CMS admin access
- [ ] CDN configuration access (if applicable)

### Baseline Metrics to Record

**Current State Documentation:**
1. **Indexation Status**
   - Total indexed pages (site: search)
   - GSC indexed pages count
   - Sitemap submitted pages vs indexed

2. **Performance Baselines**
   - Current PageSpeed scores (mobile + desktop)
   - Core Web Vitals (LCP, FID, CLS)
   - Average page load time

3. **Traffic Baselines**
   - Organic traffic (last 3 months)
   - Top landing pages
   - Average rankings

### Audit Scope Definition

**Define what to audit:**
- Entire site or specific sections?
- Crawl budget (max pages)
- Priority pages (high-traffic, high-value)
- Known problem areas

---

## Crawl Analysis {#crawl}

### Step 1: Configure Screaming Frog Crawl

**Crawl Configuration:**
```
Mode: Spider
Crawl: All
Speed: 5 URLs/second (adjust based on site size)
User-Agent: Googlebot
Respect Robots.txt: Yes (initially, then crawl without to see blocks)
Follow Redirects: Yes
Max URL Length: 2083 characters
```

**What to Enable:**
- [ ] Custom extraction (for canonical tags, hreflang)
- [ ] JavaScript rendering (for SPA sites)
- [ ] Analytics integration
- [ ] Sitemap import

### Step 2: Analyze Crawl Data

**Critical Issues to Identify:**

#### 1. HTTP Status Codes
```
✅ 200 OK: Healthy pages
⚠️  301/302 Redirects: Check redirect chains
❌ 404 Not Found: Broken links
❌ 410 Gone: Intentionally removed
❌ 5xx Errors: Server issues
```

**Action Items:**
- Fix all 404s (restore content or redirect)
- Eliminate redirect chains (direct A→C instead of A→B→C)
- Resolve 5xx errors (server configuration)

#### 2. Page Depth
```
Ideal: 0-3 clicks from homepage
Warning: 4-5 clicks
Critical: 6+ clicks (orphaned pages)
```

**Fix:**
- Add internal links to deep pages
- Improve site architecture
- Update XML sitemap

#### 3. Duplicate Content

**Types to Check:**
- Duplicate title tags
- Duplicate meta descriptions
- Duplicate page content
- URL variations (www vs non-www, http vs https)

**Solutions:**
- Implement canonical tags
- Use 301 redirects
- Set up proper URL parameters in GSC
- Add rel="nofollow" where appropriate

#### 4. Missing or Poor Meta Tags

**Check for:**
- Missing title tags (<1% of pages)
- Missing meta descriptions
- Title tags too long (>60 chars)
- Title tags too short (<30 chars)
- Non-unique titles

#### 5. Image Optimization

**Audit Points:**
- Missing alt text
- Large file sizes (>100KB)
- Non-optimized formats (use WebP)
- Missing width/height attributes

### Step 3: Review robots.txt

**Common Issues:**
```robotstxt
# BAD - Blocking important resources
User-agent: *
Disallow: /css/
Disallow: /js/

# GOOD - Only block admin areas
User-agent: *
Disallow: /admin/
Disallow: /private/
Sitemap: https://example.com/sitemap.xml
```

**Check:**
- Not accidentally blocking important pages
- Sitemap referenced
- No overly restrictive rules

---

## Core Web Vitals & Performance {#performance}

### Understanding Core Web Vitals

**Three Key Metrics:**

1. **LCP (Largest Contentful Paint)**
   - Target: <2.5 seconds
   - Measures: Loading performance
   - What counts: Largest image or text block

2. **FID (First Input Delay)**
   - Target: <100 milliseconds
   - Measures: Interactivity
   - What counts: Time to first interaction

3. **CLS (Cumulative Layout Shift)**
   - Target: <0.1
   - Measures: Visual stability
   - What counts: Unexpected layout shifts

### Performance Audit Process

#### Step 1: Run PageSpeed Insights

**For 5-10 key pages, record:**
- Performance score (0-100)
- LCP, FID, CLS values
- Opportunities (actionable improvements)
- Diagnostics (potential issues)

#### Step 2: Identify Performance Bottlenecks

**Common Issues:**

1. **Slow Server Response (TTFB)**
   - Solution: Upgrade hosting, enable caching, use CDN

2. **Render-Blocking Resources**
   - Solution: Defer non-critical CSS/JS, inline critical CSS

3. **Large Images**
   - Solution: Compress, lazy-load, use modern formats (WebP, AVIF)

4. **Too Many Requests**
   - Solution: Combine files, use HTTP/2, reduce third-party scripts

5. **No Caching**
   - Solution: Implement browser caching, server-side caching

#### Step 3: Optimization Recommendations

**Quick Wins (High Impact, Low Effort):**
- Enable Gzip/Brotli compression
- Implement browser caching
- Optimize images (compression + lazy loading)
- Minify CSS/JS
- Remove unused CSS/JS

**Medium Effort:**
- Implement CDN
- Defer offscreen images
- Preload critical resources
- Reduce third-party scripts

**High Effort:**
- Migrate to faster hosting
- Refactor JavaScript architecture
- Implement service workers (PWA)

---

## Mobile-First & Responsive {#mobile}

### Mobile-First Indexing Checklist

Google now primarily uses the mobile version for indexing and ranking.

**Critical Checks:**
- [ ] Responsive design (adapts to all screen sizes)
- [ ] Same content on mobile and desktop
- [ ] Mobile page speed <3 seconds
- [ ] Touch-friendly buttons (48x48px minimum)
- [ ] Readable fonts (16px minimum body text)
- [ ] No horizontal scrolling
- [ ] No intrusive interstitials

### Mobile Testing Process

**1. Google Mobile-Friendly Test**
```
URL: search.google.com/test/mobile-friendly
```
Check for:
- Text too small to read
- Clickable elements too close
- Content wider than screen
- Mobile viewport not set

**2. Manual Device Testing**
Test on:
- iPhone (various models)
- Android (various models)
- Tablet (iPad, Android tablet)

**3. Chrome DevTools Device Emulation**
```
Chrome DevTools → Toggle device toolbar (Ctrl+Shift+M)
Test: iPhone 12, iPad, Galaxy S20
```

### Common Mobile Issues

| Issue | Impact | Fix |
|-------|--------|-----|
| No viewport meta tag | Not responsive | Add `<meta name="viewport" content="width=device-width, initial-scale=1">` |
| Fixed-width elements | Horizontal scroll | Use relative units (%, rem, em) |
| Small tap targets | Poor UX | Increase button size to 48x48px |
| Flash/Java | Not supported | Replace with HTML5 |
| Intrusive popups | Penalty risk | Use less aggressive formats |

---

## Structured Data & Schema {#schema}

### Why Structured Data Matters

Structured data helps search engines understand your content and enables rich results (rich snippets, knowledge panels, etc.).

### Audit Structured Data

**1. Check Current Implementation**

Use Google's Rich Results Test:
```
URL: search.google.com/test/rich-results
```

**2. Identify Schema Opportunities**

**Common Schema Types:**

| Content Type | Schema Type | Rich Result |
|-------------|------------|-------------|
| Articles | Article, NewsArticle | Top Stories, headline |
| Products | Product, Offer | Shopping results, pricing |
| Reviews | Review, AggregateRating | Star ratings |
| Recipes | Recipe | Recipe cards |
| Events | Event | Event listings |
| FAQs | FAQPage | Expandable FAQs |
| How-tos | HowTo | Step-by-step guides |
| Local Business | LocalBusiness | Knowledge panel |

**3. Implementation Method**

**JSON-LD (Recommended):**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Complete Technical SEO Audit Guide",
  "author": {
    "@type": "Person",
    "name": "Jane Doe"
  },
  "datePublished": "2025-01-15",
  "image": "https://example.com/image.jpg"
}
</script>
```

**Validation:**
- Use Rich Results Test
- Check for errors/warnings
- Validate all required properties

---

## JavaScript & Rendering {#javascript}

### JavaScript SEO Challenges

**Problem:** Search engines may struggle to render JavaScript-heavy sites.

### Audit JavaScript Rendering

**1. Compare Rendered vs Raw HTML**

**Method:**
```bash
# Raw HTML
curl https://example.com/page

# Rendered HTML
chrome --headless --dump-dom https://example.com/page
```

**Check:**
- Is critical content in raw HTML?
- Are links visible without JS?
- Are meta tags present in raw HTML?

**2. Check Google's Rendering**

**Google Search Console → URL Inspection**
- Request indexing
- View crawled page (screenshot)
- Check rendered HTML

**3. Identify Rendering Issues**

**Common Problems:**
- Content only loads with JS
- Links not in initial HTML
- Lazy-loading breaks crawling
- Infinite scroll without pagination

### JavaScript SEO Best Practices

**1. Server-Side Rendering (SSR)**
- Generate HTML on server
- Send complete HTML to browser
- Best for SEO

**2. Static Site Generation (SSG)**
- Pre-build all pages
- Serve static HTML
- Excellent for SEO

**3. Hybrid Approach**
- SSR for critical pages
- CSR for logged-in areas
- Balance performance and SEO

**4. Dynamic Rendering** (last resort)
- Detect bot user-agents
- Serve pre-rendered HTML to bots
- Serve JS app to users
- Not recommended (cloaking risk)

---

## Indexability & Crawlability {#indexing}

### Google Search Console Analysis

**1. Coverage Report**

Navigate to: `GSC → Coverage`

**Check for:**
- Excluded pages (and why)
- Errors preventing indexing
- Valid pages count
- Trending issues

**Common Exclusions:**
- Duplicate without canonical
- Crawled but not indexed
- Blocked by robots.txt
- Noindex tag present
- Soft 404

**2. Sitemap Status**

`GSC → Sitemaps`

**Verify:**
- Sitemap submitted
- No errors
- All important pages included
- Sitemap not too large (max 50,000 URLs)

### XML Sitemap Audit

**Best Practices:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page</loc>
    <lastmod>2025-01-15</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

**Checklist:**
- [ ] Only includes indexable pages (no 404s, redirects, noindex)
- [ ] Uses canonical URLs
- [ ] Updates lastmod dates
- [ ] Under 50,000 URLs per sitemap
- [ ] Gzipped for large sites
- [ ] Referenced in robots.txt

### Canonical Tags Audit

**Check for:**
- Self-referencing canonicals on all pages
- No canonical chains (A→B→C)
- Canonicals point to indexable pages
- HTTPS in canonical URLs
- No relative URLs in canonical tags

---

## Internal Linking {#links}

### Internal Linking Audit

**1. Analyze Link Distribution**

**Screaming Frog: Internal → Inlinks**

**Check:**
- Orphaned pages (0 inlinks)
- Pages with excessive inlinks (>100)
- Important pages with few inlinks

**2. Anchor Text Analysis**

**Best Practices:**
- Descriptive anchor text (not "click here")
- Include target keywords
- Vary anchor text
- Avoid over-optimization

**3. Link Architecture**

**Flat vs Deep Architecture:**
```
FLAT (Good):
Homepage → Category (1 click) → Product (2 clicks)

DEEP (Bad):
Homepage → Menu → Category → Subcategory → Product (4 clicks)
```

**Optimization:**
- Keep important pages within 3 clicks
- Use breadcrumbs
- Implement related content links
- Add contextual internal links

---

## Prioritization Matrix {#prioritization}

### How to Prioritize Fixes

**Prioritization Framework:**

| Priority | Impact | Effort | Examples |
|----------|--------|--------|----------|
| P0 - Critical | High | Low | 5xx errors, broken homepage, deindexed pages |
| P1 - High | High | Medium | Core Web Vitals, mobile usability, duplicate content |
| P2 - Medium | Medium | Low | Meta tags, image optimization, internal linking |
| P3 - Low | Low | Any | Minor issues, cosmetic fixes |

### Sample Action Plan

**Week 1 (P0 Issues):**
1. Fix 5xx server errors
2. Resolve critical indexation blocks
3. Fix broken homepage elements
4. Restore accidentally noindexed pages

**Week 2-3 (P1 Issues):**
5. Optimize Core Web Vitals (LCP, FID, CLS)
6. Fix mobile usability issues
7. Implement canonical tags for duplicates
8. Submit/fix XML sitemap

**Week 4-6 (P2 Issues):**
9. Optimize meta titles and descriptions
10. Compress and lazy-load images
11. Improve internal linking structure
12. Implement structured data

**Ongoing (P3 Issues):**
13. Regular monitoring of GSC
14. Continuous performance optimization
15. Content updates and refreshes

---

## Audit Report Template

### Executive Summary

**Site:** [URL]
**Audit Date:** [Date]
**Audited By:** [Name]

**Overall Health Score:** [X]/100

**Critical Issues:** [Number]
**High Priority:** [Number]
**Medium Priority:** [Number]

### Key Findings

**1. Indexation Issues**
- [Summary of findings]
- [Impact on SEO]

**2. Performance Issues**
- Current PageSpeed Score: [X]
- Core Web Vitals: [Pass/Fail]
- [Key bottlenecks]

**3. Mobile Usability**
- Mobile-Friendly: [Yes/No]
- [Issues identified]

**4. Technical Issues**
- [Structured data problems]
- [Crawlability issues]
- [Other technical issues]

### Recommended Actions

| Priority | Issue | Impact | Solution | Effort | Timeline |
|----------|-------|--------|----------|--------|----------|
| P0 | [Issue] | [Impact] | [Solution] | [Hours] | [Date] |

### Appendix

- Full crawl data
- PageSpeed reports
- GSC screenshots
- Before/after comparisons

---

## Monitoring & Maintenance

### Ongoing SEO Health Checks

**Weekly:**
- GSC coverage errors
- Major ranking changes
- Site uptime monitoring

**Monthly:**
- Full crawl with Screaming Frog
- Core Web Vitals check
- Backlink profile analysis
- Competitor analysis

**Quarterly:**
- Comprehensive technical audit
- Content audit
- Keyword ranking review
- Strategy adjustment

### Tools for Monitoring

**Free:**
- Google Search Console
- Google Analytics
- PageSpeed Insights
- Bing Webmaster Tools

**Paid:**
- Ahrefs Site Audit
- SEMrush Site Audit
- Sitebulb
- Screaming Frog (license)

---

## Resources

### Further Reading
- Google Search Central Documentation
- Moz Technical SEO Guide
- Ahrefs SEO Audit Guide

### Tools
- Screaming Frog: https://www.screamingfrog.co.uk/
- Google Search Console: https://search.google.com/search-console
- PageSpeed Insights: https://pagespeed.web.dev/

---

**Remember:** Technical SEO is an ongoing process, not a one-time fix. Regular audits and continuous monitoring are essential for maintaining optimal search performance.
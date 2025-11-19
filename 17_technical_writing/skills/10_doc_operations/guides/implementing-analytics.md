# Implementing Google Analytics 4 for Documentation

## Overview

Google Analytics 4 (GA4) provides comprehensive insights into how users interact with your documentation. This guide walks through setting up GA4, implementing tracking, and leveraging data to improve documentation quality and user experience.

## Prerequisites

- Google account with admin access
- Documentation website domain
- Basic understanding of documentation analytics
- Access to your documentation platform's deployment environment

## Part 1: Initial GA4 Setup

### Step 1: Create a GA4 Property

1. Navigate to [Google Analytics Admin Dashboard](https://analytics.google.com)
2. Click "Create" in the left sidebar
3. Select "Property"
4. Fill in property details:
   - Property name: "Documentation Analytics"
   - Time zone: Your region
   - Currency: USD (or your preference)
5. Click "Create"

### Step 2: Set Up Your Data Stream

1. Under "Data Collection and Modification," select "Data Streams"
2. Click "Add stream"
3. Choose "Web"
4. Enter:
   - Website URL: Your documentation domain
   - Stream name: "Documentation Website"
5. Click "Create stream"
6. Copy your Measurement ID (looks like: G-XXXXXXXXXX)

### Step 3: Configure Documentation Platform

For Next.js Documentation:
```javascript
// pages/_app.js
import Script from 'next/script';

export default function App({ Component, pageProps }) {
  return (
    <>
      <Script
        strategy="afterInteractive"
        src={`https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX`}
      />
      <Script
        id="google-analytics"
        strategy="afterInteractive"
        dangerouslySetInnerHTML={{
          __html: `
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-XXXXXXXXXX');
          `,
        }}
      />
      <Component {...pageProps} />
    </>
  );
}
```

For Docusaurus:
```javascript
// docusaurus.config.js
module.exports = {
  // ... other config
  plugins: [
    [
      '@docusaurus/plugin-google-analytics',
      {
        trackingID: 'G-XXXXXXXXXX',
        anonymizeIP: true,
      },
    ],
  ],
};
```

For Jekyll/Hugo:
```html
<!-- _includes/analytics.html or layouts/base.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX', {
    'page_path': window.location.pathname
  });
</script>
```

## Part 2: Custom Event Tracking

### Tracking Documentation-Specific Events

Implement events that matter for documentation:

```javascript
// utils/analytics.js
export const trackDocEvent = (eventName, eventData = {}) => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', eventName, {
      'timestamp': new Date().toISOString(),
      'page_url': window.location.href,
      ...eventData
    });
  }
};

// Track page scroll depth
export const setupScrollTracking = () => {
  let maxScroll = 0;

  window.addEventListener('scroll', () => {
    const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
    if (scrollPercent > maxScroll) {
      maxScroll = scrollPercent;

      if ([25, 50, 75, 100].includes(Math.round(scrollPercent))) {
        trackDocEvent('scroll_depth', {
          'scroll_percent': Math.round(scrollPercent)
        });
      }
    }
  });
};

// Track search queries
export const trackSearch = (query, results) => {
  trackDocEvent('documentation_search', {
    'search_term': query,
    'results_count': results.length
  });
};

// Track code snippet copies
export const trackCodeCopy = (snippet, language) => {
  trackDocEvent('code_snippet_copied', {
    'language': language,
    'snippet_length': snippet.length
  });
};

// Track external links
export const trackExternalLink = (url) => {
  trackDocEvent('external_link_click', {
    'link_url': url
  });
};

// Track feedback submissions
export const trackFeedback = (rating, comment) => {
  trackDocEvent('documentation_feedback', {
    'rating': rating,
    'has_comment': !!comment
  });
};
```

### Implement Events in Components

```javascript
// components/CodeBlock.jsx
import { trackCodeCopy } from '../utils/analytics';
import React, { useRef } from 'react';

export function CodeBlock({ code, language }) {
  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(code);
    trackCodeCopy(code, language);
  };

  return (
    <div className="code-block">
      <button onClick={copyToClipboard}>Copy</button>
      <pre><code className={language}>{code}</code></pre>
    </div>
  );
}
```

```javascript
// components/SearchBox.jsx
import { trackSearch } from '../utils/analytics';

export function SearchBox({ onSearch }) {
  const handleSearch = (query) => {
    const results = performSearch(query);
    trackSearch(query, results);
    onSearch(results);
  };

  return (
    <input
      type="text"
      placeholder="Search documentation..."
      onChange={(e) => handleSearch(e.target.value)}
    />
  );
}
```

## Part 3: Configure Custom Dimensions and Metrics

### Add Custom Dimensions

1. Go to "Data Collection and Modification" > "Custom Definitions"
2. Click "Create Custom Dimension"
3. Add dimensions for documentation-specific data:

```javascript
// Register custom dimensions
gtag('config', 'G-XXXXXXXXXX', {
  'custom_map': {
    'dimension1': 'doc_category',
    'dimension2': 'doc_version',
    'dimension3': 'user_role',
    'dimension4': 'search_type',
    'metric1': 'time_on_page_seconds',
    'metric2': 'scroll_depth_percent'
  }
});

// Use custom dimensions
gtag('event', 'page_view', {
  'doc_category': 'API Reference',
  'doc_version': '3.0',
  'user_role': 'developer'
});
```

## Part 4: Set Up Goals and Conversions

### Key Documentation Conversions

Create conversion events for important user actions:

```javascript
// Track API documentation access
gtag('event', 'view_api_docs', {
  'api_name': 'authentication',
  'endpoint': '/api/v1/auth'
});

// Track tutorial completion
gtag('event', 'tutorial_completed', {
  'tutorial_name': 'Getting Started',
  'completion_time': 15 // minutes
});

// Track download triggers
gtag('event', 'doc_download', {
  'document_type': 'PDF',
  'format': 'reference'
});
```

## Part 5: Create Reports and Dashboards

### Important Metrics to Track

1. **Page Performance**
   - Pageviews by section
   - Time on page by document
   - Bounce rate by topic

2. **User Behavior**
   - Search queries
   - Code snippet copies
   - External link clicks

3. **Engagement**
   - Scroll depth
   - Feedback submissions
   - Return visitor rate

### Create a Custom Report

```javascript
// reports.js - Generate weekly analytics summary
const generateAnalyticsSummary = async () => {
  // Using Google Analytics Reporting API v4
  const { google } = require('googleapis');

  const analyticsreporting = google.analyticsreporting('v4');

  const report = await analyticsreporting.reports.batchGet({
    auth: authClient,
    requestBody: {
      reportRequests: [
        {
          viewId: 'VIEW_ID',
          dateRanges: [
            {
              startDate: '7daysAgo',
              endDate: 'today'
            }
          ],
          metrics: [
            { expression: 'ga:pageviews' },
            { expression: 'ga:bounceRate' },
            { expression: 'ga:avgSessionDuration' }
          ],
          dimensions: [
            { name: 'ga:pagePath' }
          ]
        }
      ]
    }
  });

  return report;
};
```

## Part 6: Best Practices

### Privacy and Compliance

```javascript
// GDPR Compliant Implementation
gtag('config', 'G-XXXXXXXXXX', {
  'anonymize_ip': true,
  'allow_google_signals': false,
  'allow_ad_personalization_signals': false,
  'cookie_flags': 'SameSite=None;Secure'
});

// User consent handling
const initializeAnalytics = (userConsent) => {
  gtag('consent', 'default', {
    'analytics_storage': userConsent.analytics ? 'granted' : 'denied',
    'ad_storage': 'denied'
  });

  if (userConsent.analytics) {
    window.gtag = gtag;
  }
};
```

### Performance Considerations

1. **Defer GA4 loading** - Use `strategy="afterInteractive"` in Next.js
2. **Batch events** - Send related events together
3. **Sample data** - For high-traffic docs, use sampling to reduce costs
4. **Debug mode** - Enable for development:

```javascript
window.dataLayer = window.dataLayer || [];

function gtag(){dataLayer.push(arguments);}
gtag('config', 'G-XXXXXXXXXX', {
  'debug_mode': true // Set to false in production
});
```

## Part 7: Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Data not appearing | Check Measurement ID, verify domain in GA4, wait 24 hours |
| Custom events missing | Ensure custom dimension registered, check event name spelling |
| Low session count | Verify GA4 not blocked by ad blockers, check cookie consent |
| Bounce rate too high | Improve page load speed, enhance content relevance |

### Debugging Tools

```javascript
// Enable GA4 debug view
// In GA4: Admin > Property Settings > Data Verification > Debug View

// Check in console
window.gtag = function() {
  console.log('GA4 Event:', arguments);
};
```

## Part 8: Advanced Features

### Set Up Audience Segments

Create segments for:
- First-time visitors
- Returning developers
- Mobile users
- High-engagement users

### Implement UTM Parameters

```javascript
// Track campaigns referencing documentation
// https://docs.example.com/?utm_source=blog&utm_medium=link&utm_campaign=guide
```

### Data Export and Integration

```bash
# Export GA4 data to BigQuery for deeper analysis
# Admin > Data Collection and Modification > BigQuery Linking
# Then query with:
```

```sql
SELECT
  event_date,
  event_name,
  COUNT(*) as event_count,
  COUNT(DISTINCT user_pseudo_id) as unique_users
FROM `project.dataset.events_*`
WHERE event_name IN ('documentation_search', 'code_snippet_copied')
GROUP BY event_date, event_name
ORDER BY event_date DESC
```

## Conclusion

GA4 implementation enables data-driven documentation improvements. Start with basic tracking, gradually add custom events, and use insights to optimize content and user experience.

## Resources

- [Google Analytics 4 Documentation](https://support.google.com/analytics)
- [GA4 Implementation Guide](https://developers.google.com/analytics/devguides/collection/ga4)
- [Google Tag Manager Setup](https://tagmanager.google.com)
- [Analytics Best Practices](https://analytics.google.com/analytics/web)


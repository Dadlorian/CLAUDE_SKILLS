# Embedding Methods Comparison

## Overview

Comparison of different methods for embedding analytics into SaaS applications.

## Embedding Approaches

### 1. iframe Embedding

**How it works**: Load BI content in an HTML iframe element

**Pros**:
- Simple to implement
- Isolated from parent page (security sandbox)
- Works with any frontend framework
- No JavaScript dependencies
- Easy to resize and position

**Cons**:
- Limited communication with parent page
- CORS and CSP challenges
- Less control over styling
- Potential scrolling issues
- Cookie restrictions in some browsers

**Best for**: Quick integrations, legacy applications, minimal customization

**Example**:
```html
<iframe
  src="https://bi.example.com/embed/dashboard/123?token=xxx"
  width="100%"
  height="600px"
  frameborder="0"
></iframe>
```

**Security considerations**:
- Use sandbox attribute
- Implement CSP headers
- HTTPS required
- Token in URL or postMessage

---

### 2. JavaScript SDK

**How it works**: Use vendor-provided JavaScript library for native embedding

**Pros**:
- Full control over rendering
- Rich event handling
- Programmatic interactions
- Better styling control
- Custom toolbar/menus

**Cons**:
- Larger bundle size
- More complex implementation
- Version management required
- Vendor lock-in to specific API

**Best for**: Native integration, custom UX, interactive dashboards

**Example** (Tableau):
```javascript
const viz = new tableau.Viz(
  containerDiv,
  url,
  {
    hideTabs: true,
    hideToolbar: false,
    onFirstInteractive: () => {
      console.log('Dashboard loaded');
    }
  }
);
```

**Security considerations**:
- Token passed via API
- HTTPS required
- CSP for script sources
- Vendor SDK updates

---

### 3. REST API + Rendering

**How it works**: Fetch data via API, render with custom visualization library

**Pros**:
- Complete control over UI/UX
- No vendor branding
- Use preferred viz library (D3, Chart.js, etc.)
- Optimized for performance
- Custom interactions

**Cons**:
- Most development effort
- Maintain visualization code
- Limited to supported API capabilities
- Need expertise in data viz

**Best for**: Fully custom analytics, simple charts, white-label products

**Example**:
```javascript
// Fetch data from BI platform API
const response = await fetch('/api/dashboard/123/data', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();

// Render with Chart.js
new Chart(ctx, {
  type: 'bar',
  data: data,
  options: customOptions
});
```

**Security considerations**:
- API authentication
- Rate limiting
- Data filtering at API level
- HTTPS required

---

### 4. Component Embedding

**How it works**: Framework-specific components (React, Vue, Angular)

**Pros**:
- Idiomatic to framework
- Type safety (TypeScript)
- Reactive data binding
- Easy state management
- Component lifecycle hooks

**Cons**:
- Framework-specific
- May wrap iframe or SDK internally
- Limited vendor support
- Requires build step

**Best for**: Modern SPA applications, React/Vue/Angular apps

**Example** (React):
```jsx
import { TableauEmbed } from '@tableau/embedding-react';

function DashboardPage() {
  return (
    <TableauEmbed
      src="https://bi.example.com/views/Sales"
      width="100%"
      height="600px"
      hideTabs={true}
      onFirstInteractive={() => console.log('Loaded')}
    />
  );
}
```

**Security considerations**:
- Same as underlying method (iframe/SDK)
- Props validation
- Sanitize user inputs

---

### 5. Server-Side Rendering (SSR)

**How it works**: Pre-render analytics on server, send static HTML/images

**Pros**:
- Fastest initial load
- SEO friendly
- No client-side dependencies
- Works without JavaScript
- Cacheable output

**Cons**:
- No interactivity (unless hydrated)
- Server resources required
- Stale data without refresh
- Limited to static views

**Best for**: Email reports, PDFs, public dashboards, SEO pages

**Example**:
```python
# Server-side (Python)
from tableau_api_lib import TableauServerConnection

# Generate static image
image_data = tableau_conn.download_view_image(
    view_id='123',
    image_resolution='high'
)

# Serve as HTML
return f'<img src="data:image/png;base64,{image_data}" />'
```

**Security considerations**:
- Server-side token management
- Cache invalidation
- Image data sanitization

---

### 6. Mobile SDK

**How it works**: Native mobile SDK for iOS/Android apps

**Pros**:
- Native performance
- Offline capability
- Touch-optimized
- Device features (notifications)
- Better mobile UX

**Cons**:
- Platform-specific code
- SDK maintenance
- App store approval
- Limited vendor support

**Best for**: Mobile apps, offline analytics, native experience

**Example** (Power BI iOS):
```swift
import PowerBIEmbed

let config = EmbedConfiguration(
    embedUrl: "https://app.powerbi.com/...",
    embedToken: token,
    reportId: "123"
)

let reportView = PowerBIReportView(frame: view.bounds)
reportView.embed(with: config)
```

**Security considerations**:
- Secure token storage (Keychain/KeyStore)
- Certificate pinning
- App transport security

---

## Feature Comparison Matrix

| Feature | iframe | JS SDK | REST API | Component | SSR | Mobile SDK |
|---------|--------|--------|----------|-----------|-----|------------|
| **Ease of Implementation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Customization** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Interactivity** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| **White-labeling** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Offline Support** | ❌ | ❌ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Mobile Optimized** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Maintenance Effort** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

---

## Platform Support

### Tableau
- **iframe**: ✅ Full support
- **JS SDK**: ✅ Embedding API v3
- **REST API**: ✅ Full REST API
- **Component**: ✅ React component available
- **Mobile SDK**: ✅ iOS/Android SDKs

### Power BI
- **iframe**: ✅ Full support
- **JS SDK**: ✅ Power BI Embedded SDK
- **REST API**: ✅ Full REST API
- **Component**: ✅ React component available
- **Mobile SDK**: ✅ iOS/Android SDKs

### Looker
- **iframe**: ✅ Full support
- **JS SDK**: ✅ Embed SDK
- **REST API**: ✅ API 4.0
- **Component**: ⚠️ Community packages
- **Mobile SDK**: ⚠️ Limited support

### Metabase
- **iframe**: ✅ Full support
- **JS SDK**: ⚠️ Limited
- **REST API**: ✅ Full REST API
- **Component**: ⚠️ Community packages
- **Mobile SDK**: ❌ Not officially supported

### Superset
- **iframe**: ✅ Full support
- **JS SDK**: ✅ Embedded SDK
- **REST API**: ✅ Full REST API
- **Component**: ⚠️ Community packages
- **Mobile SDK**: ❌ Not officially supported

---

## Decision Framework

### Choose **iframe** if:
- Quick integration needed
- Minimal customization required
- Legacy application
- Limited frontend resources

### Choose **JavaScript SDK** if:
- Need rich interactivity
- Want programmatic control
- Modern web application
- Can manage vendor dependencies

### Choose **REST API** if:
- Need complete UI control
- Building white-label product
- Have data viz expertise
- Want vendor independence

### Choose **Component** if:
- Using React/Vue/Angular
- Want framework integration
- Need type safety
- Modern SPA architecture

### Choose **SSR** if:
- Need SEO optimization
- Email/PDF reports
- Public-facing dashboards
- Performance critical

### Choose **Mobile SDK** if:
- Native mobile app
- Need offline support
- Want best mobile UX
- Can maintain platform-specific code

---

## Hybrid Approaches

Many successful implementations combine multiple methods:

### Example 1: Multi-Channel Analytics
- **Web app**: JavaScript SDK for rich interactivity
- **Email reports**: SSR for static images
- **Mobile app**: Native SDK for offline access
- **Public site**: iframe for simple embedding

### Example 2: Progressive Enhancement
- **Initial render**: SSR for fast load
- **Hydration**: Load JS SDK for interactivity
- **Fallback**: iframe if SDK fails to load

### Example 3: Micro-frontends
- **Dashboard page**: JavaScript SDK
- **Inline charts**: REST API + custom rendering
- **Report viewer**: iframe for complex reports

---

## Performance Considerations

### Load Time Comparison (typical)
- **SSR**: 100-300ms (cached)
- **iframe**: 500-1500ms
- **JS SDK**: 800-2000ms (includes SDK load)
- **REST API**: 300-800ms (excluding render)
- **Component**: 500-1500ms (similar to SDK)
- **Mobile SDK**: 400-1000ms

### Bundle Size Impact
- **iframe**: ~0 KB (HTML only)
- **JS SDK**: 50-200 KB (vendor SDK)
- **REST API**: 20-100 KB (viz library)
- **Component**: 50-200 KB (vendor SDK wrapped)
- **Mobile SDK**: 2-5 MB (native frameworks)

---

## Security Comparison

All methods require:
- HTTPS for all connections
- Secure token management
- RLS at data layer
- Regular security audits

Additional considerations:
- **iframe**: CSP, sandbox attribute, X-Frame-Options
- **JS SDK**: Script CSP, vendor trust
- **REST API**: API rate limiting, CORS
- **Component**: Dependency audits
- **SSR**: Server security, cache poisoning
- **Mobile SDK**: Certificate pinning, secure storage

---

## Recommendation Summary

| Use Case | Recommended Method | Alternative |
|----------|-------------------|-------------|
| Quick MVP | iframe | Component |
| Production SaaS | JS SDK | Component |
| White-label product | REST API | JS SDK |
| React/Vue app | Component | JS SDK |
| Email reports | SSR | REST API |
| Mobile app | Mobile SDK | REST API |
| Public dashboard | SSR | iframe |
| Internal tools | iframe | JS SDK |

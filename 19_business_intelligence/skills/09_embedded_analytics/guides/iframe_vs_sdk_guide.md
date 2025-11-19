# iframe vs SDK: Choosing the Right Approach

## When to Use iframe

### Pros
- Simple implementation
- Works with any framework
- Isolated sandbox
- No JavaScript dependencies

### Cons
- Limited customization
- CORS challenges
- Less control over events
- Styling limitations

### Implementation

```html
<!-- Basic iframe embed -->
<iframe
  src="https://bi-platform.com/dashboard/123?token=xxx"
  width="100%"
  height="600px"
  frameborder="0"
  sandbox="allow-scripts allow-same-origin"
></iframe>
```

```javascript
// Dynamic iframe with token
async function embedWithIframe() {
  const { token } = await fetch('/api/embed-token').then(r => r.json());

  const iframe = document.createElement('iframe');
  iframe.src = `https://bi-platform.com/dashboard/123?token=${token}`;
  iframe.width = '100%';
  iframe.height = '600px';

  document.getElementById('container').appendChild(iframe);
}
```

### Communication with postMessage

```javascript
// Parent page
iframe.contentWindow.postMessage({
  type: 'APPLY_FILTER',
  filter: { region: 'west' }
}, 'https://bi-platform.com');

// Listen for responses
window.addEventListener('message', (event) => {
  if (event.origin !== 'https://bi-platform.com') return;

  if (event.data.type === 'DASHBOARD_LOADED') {
    console.log('Dashboard ready');
  }
});
```

## When to Use SDK

### Pros
- Full programmatic control
- Rich event handling
- Better styling control
- Async data access
- Custom interactions

### Cons
- Larger bundle size
- Version management
- More complex setup
- Framework-specific code

### Tableau JavaScript API

```javascript
import tableau from 'tableau-api';

const viz = new tableau.Viz(container, url, {
  hideTabs: true,
  onFirstInteractive: () => {
    console.log('Viz loaded');

    // Get workbook
    const workbook = viz.getWorkbook();

    // Get active sheet
    const activeSheet = workbook.getActiveSheet();

    // Apply filter
    activeSheet.applyFilterAsync(
      'Region',
      ['West', 'East'],
      tableau.FilterUpdateType.REPLACE
    );

    // Get data
    activeSheet.getUnderlyingDataAsync().then((data) => {
      console.log('Data:', data);
    });

    // Listen for events
    viz.addEventListener(
      tableau.TableauEventName.FILTER_CHANGE,
      (event) => {
        console.log('Filter changed:', event);
      }
    );
  }
});
```

### Power BI Embedded SDK

```javascript
import * as pbi from 'powerbi-client';

const powerbi = new pbi.service.Service(
  pbi.factories.hpmFactory,
  pbi.factories.wpmpFactory,
  pbi.factories.routerFactory
);

const embedConfig = {
  type: 'report',
  tokenType: models.TokenType.Embed,
  accessToken: embedToken,
  embedUrl: embedUrl,
  id: reportId,
  settings: {
    panes: {
      filters: { visible: false }
    }
  }
};

const report = powerbi.embed(container, embedConfig);

// Listen for events
report.on('loaded', () => {
  console.log('Report loaded');
});

report.on('rendered', () => {
  console.log('Report rendered');

  // Get pages
  report.getPages().then((pages) => {
    console.log('Pages:', pages);

    // Set active page
    pages[0].setActive();
  });
});

// Apply filter
report.setFilters([{
  $schema: 'http://powerbi.com/product/schema#basic',
  target: {
    table: 'Sales',
    column: 'Region'
  },
  operator: 'In',
  values: ['West', 'East']
}]);
```

## Decision Matrix

| Feature | iframe | SDK |
|---------|--------|-----|
| Setup complexity | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Customization | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Event handling | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Data access | ❌ | ⭐⭐⭐⭐⭐ |
| Bundle size | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Framework integration | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Mobile support | ⭐⭐⭐ | ⭐⭐⭐⭐ |

## Hybrid Approach

```javascript
// Use iframe for initial load, enhance with SDK
class HybridEmbed {
  constructor(container, dashboardUrl) {
    this.container = container;
    this.url = dashboardUrl;
  }

  async embed() {
    // Quick iframe load
    this.embedIframe();

    // Enhance with SDK when available
    await this.loadSDK();
    this.enhanceWithSDK();
  }

  embedIframe() {
    const iframe = document.createElement('iframe');
    iframe.src = this.url;
    iframe.className = 'dashboard-iframe';
    this.container.appendChild(iframe);
  }

  async loadSDK() {
    await import('tableau-api');
  }

  enhanceWithSDK() {
    // Replace iframe with SDK embed
    const iframe = this.container.querySelector('iframe');
    iframe.remove();

    const viz = new tableau.Viz(this.container, this.url, {
      // SDK configuration
    });
  }
}
```

## Recommendation

**Use iframe if:**
- Quick integration needed
- Minimal interaction required
- Legacy application
- Limited frontend resources

**Use SDK if:**
- Need programmatic control
- Rich interactions required
- Data access needed
- Modern SPA architecture

**Use hybrid if:**
- Progressive enhancement desired
- Want best of both worlds
- Performance critical

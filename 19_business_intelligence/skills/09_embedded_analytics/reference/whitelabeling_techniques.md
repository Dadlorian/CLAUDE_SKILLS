# White-Labeling Techniques for Embedded Analytics

## Overview

White-labeling allows SaaS providers to brand embedded analytics as their own, creating a seamless user experience without visible vendor branding.

## White-Labeling Layers

### 1. Visual Branding

#### Logo Customization
```javascript
// Tableau: Hide logo via URL parameters
const embedUrl = `https://tableau.example.com/views/Sales?` +
  `:showAppBanner=false&` +
  `:display_count=no&` +
  `:showVizHome=no`;

// Power BI: Custom branding via embedding config
const embedConfig = {
  type: 'report',
  embedUrl: reportUrl,
  accessToken: token,
  settings: {
    background: models.BackgroundType.Transparent,
    layoutType: models.LayoutType.Custom,
    customLayout: {
      displayOption: models.DisplayOption.FitToPage
    },
    panes: {
      filters: { visible: false },
      pageNavigation: { visible: false }
    }
  }
};

// Custom logo overlay
const logoOverlay = document.createElement('div');
logoOverlay.className = 'custom-logo';
logoOverlay.innerHTML = '<img src="/your-logo.png" />';
embedContainer.prepend(logoOverlay);
```

#### Color Theme Customization
```css
/* CSS to override BI tool colors */
.tableau-embed iframe {
  /* Inject custom CSS if supported */
}

/* Power BI theme JSON */
{
  "name": "YourBrand Theme",
  "dataColors": ["#0078D4", "#50E6FF", "#C7E0F4"],
  "background": "#FFFFFF",
  "foreground": "#252423",
  "tableAccent": "#0078D4",
  "good": "#107C10",
  "neutral": "#FFB900",
  "bad": "#D13438"
}

/* Looker: Custom CSS in white-label settings */
.looker-embed {
  --primary-color: #0078D4;
  --secondary-color: #50E6FF;
  --background-color: #FFFFFF;
  --text-color: #252423;
}
```

#### Font Customization
```javascript
// Load custom fonts
const style = document.createElement('style');
style.textContent = `
  @import url('https://fonts.googleapis.com/css2?family=Your+Brand+Font');

  .embed-container * {
    font-family: 'Your Brand Font', sans-serif !important;
  }
`;
document.head.appendChild(style);

// Tableau: Custom font via workbook settings
// Power BI: Theme JSON includes fontFamily
{
  "textClasses": {
    "label": {
      "fontFace": "Your Brand Font",
      "fontSize": 12
    }
  }
}
```

---

### 2. Domain Customization

#### Custom Domain (CNAME)
```nginx
# nginx configuration for custom analytics domain
server {
  server_name analytics.yourbrand.com;

  location / {
    proxy_pass https://bi-platform.vendor.com;
    proxy_set_header Host bi-platform.vendor.com;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Hide vendor headers
    proxy_hide_header X-Powered-By;
    proxy_hide_header Server;

    # Add your brand headers
    add_header X-Brand "YourBrand Analytics" always;
  }

  ssl_certificate /etc/ssl/certs/yourbrand.crt;
  ssl_certificate_key /etc/ssl/private/yourbrand.key;
}
```

#### Vanity URLs
```javascript
// URL rewriting for branded paths
app.use('/analytics/:dashboardId', (req, res) => {
  const { dashboardId } = req.params;

  // Map to vendor URL
  const vendorUrl = dashboardMappings[dashboardId];

  // Generate embed token
  const token = generateEmbedToken(req.user);

  // Redirect or embed with branded URL visible
  res.render('analytics', {
    embedUrl: vendorUrl,
    token: token,
    brandedUrl: `/analytics/${dashboardId}`
  });
});

// Browser shows: https://app.yourbrand.com/analytics/sales-dashboard
// Instead of: https://tableau.vendor.com/views/dashboard-xyz-123
```

---

### 3. UI/UX Customization

#### Remove Vendor Branding
```javascript
// Tableau: Hide all vendor UI elements
const embedOptions = {
  hideTabs: true,
  hideToolbar: true,
  width: '100%',
  height: '800px',
  ':showAppBanner': 'false',
  ':display_count': 'no',
  ':showVizHome': 'no',
  ':origin': 'yourbrand',
  ':embed': 'yes',
  ':showShareOptions': 'false'
};

// Power BI: Minimal UI
const embedConfig = {
  type: 'report',
  embedUrl: reportUrl,
  accessToken: token,
  settings: {
    panes: {
      filters: { expanded: false, visible: false },
      pageNavigation: { visible: false }
    },
    bars: {
      actionBar: { visible: false },
      statusBar: { visible: false }
    },
    navContentPaneEnabled: false,
    filterPaneEnabled: false
  }
};

// Looker: Chromeless embedding
const lookerUrl = `${baseUrl}?embed_domain=${yourDomain}&sdk=2`;

// Metabase: Hide UI elements
const metabaseUrl = `${baseUrl}#hide_parameters=true&bordered=false&titled=false`;
```

#### Custom Toolbars and Controls
```javascript
// Replace vendor toolbar with your own
class CustomAnalyticsToolbar extends React.Component {
  render() {
    return (
      <div className="custom-toolbar">
        <img src="/your-logo.png" alt="Brand" />

        <div className="controls">
          <button onClick={this.handleRefresh}>
            <RefreshIcon /> Refresh
          </button>
          <button onClick={this.handleExport}>
            <DownloadIcon /> Export
          </button>
          <button onClick={this.handleShare}>
            <ShareIcon /> Share
          </button>
        </div>

        <div className="filters">
          <DateRangePicker onChange={this.handleDateChange} />
          <RegionSelector onChange={this.handleRegionChange} />
        </div>
      </div>
    );
  }

  handleRefresh = () => {
    this.props.viz.refreshDataAsync();
  };

  handleExport = async () => {
    const pdf = await this.props.viz.showExportPDFDialog();
    // Custom export handling
  };

  handleShare = () => {
    // Your custom sharing UI
    showShareModal(this.props.dashboardId);
  };
}
```

#### Custom Context Menus
```javascript
// Override right-click context menu
embedContainer.addEventListener('contextmenu', (e) => {
  e.preventDefault();

  showCustomContextMenu({
    x: e.clientX,
    y: e.clientY,
    options: [
      {
        label: 'Export to Excel',
        icon: 'excel-icon',
        action: () => exportToExcel()
      },
      {
        label: 'Schedule Report',
        icon: 'schedule-icon',
        action: () => showScheduleDialog()
      },
      {
        label: 'Share with Team',
        icon: 'share-icon',
        action: () => showShareDialog()
      }
    ]
  });
});
```

---

### 4. Email and Notifications

#### Branded Email Templates
```javascript
// Custom email templates for scheduled reports
const emailTemplate = `
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; }
    .header {
      background: #0078D4;
      padding: 20px;
      text-align: center;
    }
    .header img { max-width: 200px; }
    .content { padding: 20px; }
    .footer {
      background: #F3F2F1;
      padding: 20px;
      text-align: center;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <div class="header">
    <img src="https://yourbrand.com/logo.png" alt="Your Brand" />
  </div>

  <div class="content">
    <h2>Your ${reportName} is Ready</h2>
    <p>Hi ${userName},</p>
    <p>Your scheduled report for ${dateRange} is now available.</p>

    <a href="${reportUrl}" style="
      display: inline-block;
      padding: 12px 24px;
      background: #0078D4;
      color: white;
      text-decoration: none;
      border-radius: 4px;
      margin: 20px 0;
    ">View Report</a>

    <p>Or download as:</p>
    <ul>
      <li><a href="${pdfUrl}">PDF</a></li>
      <li><a href="${excelUrl}">Excel</a></li>
      <li><a href="${csvUrl}">CSV</a></li>
    </ul>
  </div>

  <div class="footer">
    <p>&copy; ${new Date().getFullYear()} Your Brand. All rights reserved.</p>
    <p><a href="${unsubscribeUrl}">Unsubscribe</a></p>
  </div>
</body>
</html>
`;

// Send via your email service
await sendEmail({
  to: user.email,
  subject: `Your ${reportName} Report`,
  html: emailTemplate,
  from: 'analytics@yourbrand.com', // Your domain, not vendor
  replyTo: 'support@yourbrand.com'
});
```

#### Custom Alert Notifications
```javascript
// Intercept BI platform alerts and rebrand
async function processAlert(alert) {
  // Transform vendor alert to your format
  const customAlert = {
    title: `${yourBrandName} Alert: ${alert.title}`,
    message: alert.message.replace(/vendor-name/g, yourBrandName),
    icon: 'https://yourbrand.com/icon.png',
    color: yourBrandColor,
    actions: [
      {
        label: 'View Dashboard',
        url: `/analytics/${alert.dashboardId}` // Your URL
      },
      {
        label: 'Snooze',
        action: 'snooze'
      }
    ]
  };

  // Send via your notification system
  await sendNotification(alert.userId, customAlert);
}
```

---

### 5. Mobile App White-Labeling

#### iOS Custom Branding
```swift
// Configure Power BI SDK with white-label settings
let embedConfig = EmbedConfiguration()
embedConfig.embedUrl = reportUrl
embedConfig.accessToken = token

// Hide Power BI branding
embedConfig.settings.navContentPaneEnabled = false
embedConfig.settings.filterPaneEnabled = false

// Custom navigation bar
let navBar = UINavigationBar()
navBar.barTintColor = UIColor(named: "BrandPrimary")
navBar.titleTextAttributes = [
    .foregroundColor: UIColor.white,
    .font: UIFont(name: "YourBrandFont", size: 18)!
]

// Custom logo
let logoImageView = UIImageView(image: UIImage(named: "AppLogo"))
navigationItem.titleView = logoImageView
```

#### Android Custom Branding
```kotlin
// Configure embedded analytics with brand colors
val embedConfig = EmbedConfiguration(
    embedUrl = reportUrl,
    accessToken = token
)

// Apply theme
embedConfig.settings = Settings(
    background = BackgroundType.TRANSPARENT,
    layoutType = LayoutType.CUSTOM
)

// Custom toolbar
val toolbar = findViewById<Toolbar>(R.id.toolbar)
toolbar.setBackgroundColor(getColor(R.color.brand_primary))
toolbar.setLogo(R.drawable.brand_logo)
toolbar.title = getString(R.string.app_name)
```

---

### 6. Platform-Specific White-Labeling

#### Tableau Embedding API White-Label
```javascript
// Maximum white-labeling with Tableau
const viz = new tableau.Viz(container, url, {
  // Hide all Tableau branding
  hideTabs: true,
  hideToolbar: true,
  ':showAppBanner': false,
  ':display_count': 'no',
  ':showVizHome': 'no',
  ':embed': 'yes',

  // Custom dimensions
  width: '100%',
  height: '800px',

  // Disable Tableau features
  ':toolbar': 'no',
  ':refresh': 'yes',

  // Custom origin
  ':origin': 'yourbrand',

  // Callbacks for custom handling
  onFirstInteractive: () => {
    // Remove any remaining Tableau UI
    const iframeDoc = viz.getWorkbook().getActiveSheet().getIframe().contentDocument;
    const vendorElements = iframeDoc.querySelectorAll('[data-tableau-brand]');
    vendorElements.forEach(el => el.remove());
  }
});
```

#### Power BI Embedded Complete White-Label
```javascript
// Power BI: Most white-labelable platform
const embedConfig = {
  type: 'report',
  tokenType: models.TokenType.Embed,
  accessToken: embedToken,
  embedUrl: embedUrl,
  id: reportId,

  // Remove all Microsoft branding
  settings: {
    background: models.BackgroundType.Transparent,
    panes: {
      filters: { visible: false },
      pageNavigation: { visible: false }
    },
    bars: {
      actionBar: { visible: false },
      statusBar: { visible: false }
    },
    navContentPaneEnabled: false,
    filterPaneEnabled: false,

    // Custom action on errors
    customLayout: {
      displayOption: models.DisplayOption.FitToPage,
      pagesLayout: {
        // Custom page layouts
      }
    }
  },

  // Custom theme (complete control)
  theme: {
    themeJson: customThemeJson
  }
};

// Apply complete rebrand
const report = powerbi.embed(embedContainer, embedConfig);

// Add your branding overlay
const overlay = document.createElement('div');
overlay.className = 'brand-overlay';
overlay.innerHTML = `
  <div class="brand-header">
    <img src="/logo.png" />
    <span>${yourBrandName} Analytics</span>
  </div>
`;
embedContainer.prepend(overlay);
```

#### Looker Embedded White-Label (Best-in-class)
```javascript
// Looker: Purpose-built for white-labeling
const embedUrl = LookerEmbedSDK.createDashboardWithId(dashboardId)
  .withTheme('YourBrandTheme') // Custom theme
  .appendTo('#embed-container')
  .build();

// Complete UI customization
await embedUrl
  .connect()
  .then((dashboard) => {
    // Dashboard fully loaded

    // Apply custom CSS
    dashboard.customCSS(`
      /* Complete visual control */
      .looker-embed {
        --primary-color: ${brandColors.primary};
        --secondary-color: ${brandColors.secondary};
        --font-family: ${brandFonts.main};
      }

      /* Hide Looker branding */
      .looker-logo,
      .looker-powered-by {
        display: none !important;
      }
    `);
  });

// Custom domain setup
// analytics.yourbrand.com → Looker instance
// Complete DNS/SSL white-labeling
```

#### Metabase White-Label (Open Source)
```javascript
// Metabase: Full white-label capability
const metabaseConfig = {
  // Custom branding (requires Enterprise or self-hosted)
  'application-name': 'Your Brand Analytics',
  'application-logo-url': 'https://yourbrand.com/logo.png',
  'application-favicon-url': 'https://yourbrand.com/favicon.ico',
  'application-colors': {
    brand: '#0078D4',
    'brand-light': '#50E6FF'
  },

  // Remove Metabase branding
  'show-metabase-links': false,
  'hide-embed-branding': true,

  // Custom domain
  'site-url': 'https://analytics.yourbrand.com'
};

// Embedding with white-label
const iframeUrl = `https://analytics.yourbrand.com/embed/dashboard/${token}` +
  `#bordered=false&titled=false`;
```

---

### 7. Advanced White-Labeling Techniques

#### CSS Injection for iframe Embeds
```javascript
// Inject custom CSS into iframe (same-origin only)
function injectCustomCSS(iframeElement) {
  const iframeDoc = iframeElement.contentDocument ||
                    iframeElement.contentWindow.document;

  const style = iframeDoc.createElement('style');
  style.textContent = `
    /* Hide vendor branding */
    .vendor-logo,
    .powered-by,
    [data-vendor-brand] {
      display: none !important;
    }

    /* Apply your brand colors */
    :root {
      --primary: ${brandColors.primary};
      --secondary: ${brandColors.secondary};
    }

    /* Custom fonts */
    body, * {
      font-family: ${brandFonts.main} !important;
    }

    /* Custom button styles */
    button, .btn {
      background: var(--primary);
      border-radius: 4px;
      padding: 8px 16px;
    }
  `;

  iframeDoc.head.appendChild(style);
}

// Apply on iframe load
iframe.addEventListener('load', () => {
  try {
    injectCustomCSS(iframe);
  } catch (e) {
    console.warn('Cross-origin iframe, cannot inject CSS');
  }
});
```

#### postMessage for Cross-Origin Branding
```javascript
// Parent page: Send branding config to iframe
const brandConfig = {
  logo: 'https://yourbrand.com/logo.png',
  colors: {
    primary: '#0078D4',
    secondary: '#50E6FF'
  },
  fonts: {
    main: 'Your Brand Font'
  }
};

iframe.contentWindow.postMessage({
  type: 'APPLY_BRAND',
  config: brandConfig
}, 'https://bi-platform.vendor.com');

// Inside iframe: Receive and apply branding
window.addEventListener('message', (event) => {
  if (event.data.type === 'APPLY_BRAND') {
    const { config } = event.data;

    // Apply logo
    document.querySelector('.logo').src = config.logo;

    // Apply colors
    document.documentElement.style.setProperty('--primary', config.colors.primary);
    document.documentElement.style.setProperty('--secondary', config.colors.secondary);

    // Apply fonts
    document.documentElement.style.setProperty('--font-main', config.fonts.main);
  }
});
```

#### Browser Extension for Force-Branding
```javascript
// Chrome extension to rebrand any embedded BI tool
// manifest.json
{
  "name": "YourBrand Analytics Branding",
  "version": "1.0",
  "manifest_version": 3,
  "content_scripts": [{
    "matches": ["https://bi-vendor.com/*"],
    "js": ["content.js"],
    "css": ["branding.css"]
  }]
}

// content.js
const brandConfig = {
  logo: chrome.runtime.getURL('logo.png'),
  colors: { primary: '#0078D4' }
};

// Replace vendor logo
document.querySelectorAll('.vendor-logo').forEach(logo => {
  logo.src = brandConfig.logo;
});

// Apply color scheme
document.documentElement.style.setProperty('--primary', brandConfig.colors.primary);
```

---

### 8. Legal and Licensing Considerations

#### White-Label Licensing Matrix

| Platform | White-Label Support | License Required | Custom Domain | Remove Branding |
|----------|---------------------|------------------|---------------|-----------------|
| **Power BI Embedded** | ✅ Excellent | Azure Embedded SKU | ✅ Yes | ✅ Full |
| **Tableau Embedded** | ⚠️ Limited | Core/Explorer | ⚠️ Via proxy | ⚠️ Partial |
| **Looker Embedded** | ✅ Excellent | Embedded license | ✅ Yes | ✅ Full |
| **Metabase Enterprise** | ✅ Excellent | Enterprise | ✅ Yes | ✅ Full |
| **Metabase OSS** | ✅ Good | Open source | ✅ Yes | ✅ Full |
| **Superset** | ✅ Good | Open source | ✅ Yes | ✅ Full |
| **Redash** | ⚠️ Limited | Open source | ✅ Yes | ⚠️ Partial |

#### Terms of Service Compliance
```javascript
// Check platform ToS before white-labeling
const whiteLabelCompliance = {
  powerBI: {
    allowed: true,
    restrictions: [
      'Must use Azure Embedded capacity',
      'Cannot misrepresent platform origin',
      'Must comply with Microsoft trademark policies'
    ]
  },

  tableau: {
    allowed: 'limited',
    restrictions: [
      'Cannot remove "Powered by Tableau" completely',
      'Must use Embedded Analytics license',
      'Custom domain requires Tableau Server/Online'
    ]
  },

  looker: {
    allowed: true,
    restrictions: [
      'Requires Looker Embedded license',
      'Must comply with Google Cloud ToS',
      'Cannot rebrand as competitor product'
    ]
  }
};
```

---

### 9. Testing White-Label Implementation

```javascript
// Automated tests for white-label compliance
describe('White-Label Branding', () => {
  it('should not show vendor logo', () => {
    const vendorLogos = page.$$eval('img', imgs =>
      imgs.filter(img =>
        img.src.includes('vendor-logo') ||
        img.alt.includes('VendorName')
      )
    );

    expect(vendorLogos).toHaveLength(0);
  });

  it('should display custom brand logo', () => {
    const brandLogo = page.$('img[src*="yourbrand-logo"]');
    expect(brandLogo).toBeTruthy();
    expect(brandLogo.isVisible()).toBe(true);
  });

  it('should use brand colors', async () => {
    const primaryColor = await page.$eval('.dashboard', el =>
      getComputedStyle(el).getPropertyValue('--primary-color')
    );

    expect(primaryColor).toBe('#0078D4'); // Your brand color
  });

  it('should use custom domain in URLs', () => {
    const currentUrl = page.url();
    expect(currentUrl).toContain('analytics.yourbrand.com');
    expect(currentUrl).not.toContain('vendor.com');
  });

  it('should have custom email sender', async () => {
    const email = await getLastScheduledReportEmail();
    expect(email.from).toBe('analytics@yourbrand.com');
    expect(email.from).not.toContain('vendor.com');
  });
});
```

---

## White-Label Checklist

- [ ] Remove all vendor logos and branding
- [ ] Apply custom color scheme throughout
- [ ] Use custom fonts consistently
- [ ] Configure custom domain (CNAME/proxy)
- [ ] Customize email templates with brand
- [ ] Remove vendor references from notifications
- [ ] Apply custom mobile app branding
- [ ] Test across all browsers and devices
- [ ] Verify licensing compliance
- [ ] Document branding configuration
- [ ] Create brand guideline for analytics
- [ ] Train team on maintaining brand consistency
- [ ] Set up monitoring for brand violations
- [ ] Regular audits of embedded experiences

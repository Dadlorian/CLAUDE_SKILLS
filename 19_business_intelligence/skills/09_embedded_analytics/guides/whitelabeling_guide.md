# White-Labeling Implementation Guide

## Step 1: Custom Domain Setup

### DNS Configuration

```bash
# Create CNAME record
analytics.yourbrand.com  →  bi-platform.vendor.com

# Or use reverse proxy
```

### nginx Reverse Proxy

```nginx
server {
    server_name analytics.yourbrand.com;

    location / {
        proxy_pass https://bi-platform.vendor.com;
        proxy_set_header Host bi-platform.vendor.com;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Hide vendor headers
        proxy_hide_header X-Powered-By;
        proxy_hide_header Server;
        
        # Add your brand
        add_header X-Brand "YourBrand Analytics";
    }

    ssl_certificate /path/to/yourbrand.crt;
    ssl_certificate_key /path/to/yourbrand.key;
}
```

## Step 2: Visual Branding

### Custom CSS

```javascript
// Inject custom CSS into embed
const embedContainer = document.getElementById('analytics');

const customStyle = document.createElement('style');
customStyle.textContent = `
  .analytics-embed {
    --primary-color: #0078D4;
    --secondary-color: #50E6FF;
    --font-family: 'Your Brand Font', sans-serif;
  }
  
  /* Hide vendor branding */
  .vendor-logo,
  .powered-by {
    display: none !important;
  }
`;

document.head.appendChild(customStyle);
```

### Custom Logo Overlay

```javascript
const logoOverlay = document.createElement('div');
logoOverlay.className = 'brand-header';
logoOverlay.innerHTML = `
  <img src="/your-logo.png" alt="Your Brand" />
  <h1>Your Brand Analytics</h1>
`;

embedContainer.prepend(logoOverlay);
```

## Step 3: Platform-Specific Configuration

### Power BI: Theme JSON

```json
{
  "name": "Your Brand Theme",
  "dataColors": ["#0078D4", "#50E6FF", "#C7E0F4"],
  "background": "#FFFFFF",
  "foreground": "#252423",
  "tableAccent": "#0078D4",
  "textClasses": {
    "title": {
      "fontFace": "Your Brand Font",
      "fontSize": 18,
      "color": "#0078D4"
    }
  }
}
```

```javascript
const embedConfig = {
  theme: { themeJson: customTheme },
  settings: {
    background: models.BackgroundType.Transparent,
    panes: {
      filters: { visible: false },
      pageNavigation: { visible: false }
    },
    bars: {
      actionBar: { visible: false }
    }
  }
};
```

### Tableau: URL Parameters

```javascript
const embedUrl = `${baseUrl}?` +
  `:showAppBanner=false&` +
  `:display_count=no&` +
  `:showVizHome=no&` +
  `:toolbar=no`;
```

## Step 4: Email Branding

```javascript
const emailTemplate = `
<!DOCTYPE html>
<html>
<head>
  <style>
    .header {
      background: #0078D4;
      padding: 20px;
      text-align: center;
    }
    .header img {
      max-width: 200px;
    }
  </style>
</head>
<body>
  <div class="header">
    <img src="https://yourbrand.com/logo.png" alt="Your Brand" />
  </div>
  <div class="content">
    <h2>Your ${reportName} is Ready</h2>
    <p>View your analytics report:</p>
    <a href="${reportUrl}">View Report</a>
  </div>
  <div class="footer">
    <p>&copy; ${new Date().getFullYear()} Your Brand</p>
  </div>
</body>
</html>
`;
```

## White-Labeling Checklist

- [ ] Custom domain configured
- [ ] SSL certificate installed
- [ ] Vendor branding removed
- [ ] Custom logo added
- [ ] Brand colors applied
- [ ] Custom fonts loaded
- [ ] Email templates branded
- [ ] Mobile app branded
- [ ] Error pages customized
- [ ] Loading states branded
- [ ] Tested across browsers

# Mobile BI Capabilities Reference

## Platform Mobile Feature Comparison

| Feature | Tableau | Power BI | Looker | Qlik | Superset |
|---------|---------|----------|--------|------|----------|
| **Native Apps** | iOS, Android | iOS, Android, Windows | iOS, Android | iOS, Android | None (PWA) |
| **Offline Access** | ✓ Extracts | ✓ Cached | Limited | ✓ | Limited |
| **Touch Optimization** | ✓✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓ |
| **Device Layouts** | ✓ Custom | ✓ Auto | ✓ Responsive | ✓ Responsive | ✓ Basic |
| **Biometrics** | ✓ | ✓ | ✓ | ✓ | OS-level |
| **Push Notifications** | ✓ | ✓ | ✓ | ✓ | Custom |
| **AR/VR** | Limited | ✓ HoloLens | No | Limited | No |
| **Camera Integration** | ✓ Barcode | ✓ Barcode | Limited | Limited | No |
| **GPS/Location** | Via parameters | ✓ Maps | Via params | Via params | Custom |

## Tableau Mobile

### Device-Specific Layouts
```
Tableau Desktop:
1. Create dashboard with default layout
2. Dashboard → Device Layouts → Add Phone/Tablet layout
3. Customize layout for each device type
   - Remove/add worksheets
   - Resize visualizations
   - Adjust filters placement
4. Publish to Tableau Server/Cloud

Device types:
- Default (Desktop/Laptop)
- Tablet (iPad, Android tablets)
- Phone (iOS, Android phones)
```

### Mobile App Configuration (iOS/Android)
```json
// MDM Configuration (Mobile Device Management)
{
  "server_url": "https://tableau.company.com",
  "authentication_type": "saml",
  "certificate_validation": true,
  "allow_offline_snapshots": true,
  "max_snapshot_age_days": 7,
  "biometric_authentication": true,
  "analytics": {
    "enabled": true,
    "collection_interval": "daily"
  }
}
```

### Offline Snapshots
```
Mobile App:
1. Open dashboard while online
2. Tap share icon → Save Snapshot
3. Snapshot saved locally (encrypted)
4. Access offline for configured duration (default 7 days)
5. Sync when back online

Limitations:
- Snapshots are read-only
- No filters/interactions in offline mode
- Extract-based dashboards work better
```

### Metrics App (KPI Monitoring)
```
Tableau Metrics App:
- Dedicated iOS/Android app for KPIs
- Push notifications for threshold alerts
- Home screen widgets
- Watch complications (Apple Watch)

Setup:
1. Create metric in Tableau Server/Cloud
2. Define: Data source, measure, thresholds
3. Subscribe users to metric
4. Users receive updates in Metrics app

Example metric definition:
- Name: "Daily Sales"
- Data: Sales dashboard, Total Revenue measure
- Alert: Below $50,000
- Refresh: Every hour
```

## Power BI Mobile

### Phone Report Layouts
```
Power BI Desktop:
1. View → Mobile Layout
2. Drag visuals from "Visualizations" pane
3. Arrange for portrait mode (phone screen)
4. Some visuals auto-adapt, others need custom layout
5. Test with phone emulator
6. Publish to Power BI Service

Best practices:
- Use 1-2 columns max
- Simplify visuals for small screens
- Use cards for key metrics
- Vertical scrolling preferred
```

### Mobile App Features
```json
// Power BI Mobile app capabilities
{
  "features": {
    "offline_mode": true,
    "annotations": true,  // Draw on reports
    "spotlight": true,    // Highlight data points
    "alerts": true,       // Data alerts
    "favorites": true,
    "home_screen_tiles": true,
    "barcode_scanner": true,
    "qr_code_scanner": true,
    "ssrs_reports": true  // Report Server support
  },
  "platforms": {
    "iOS": {
      "min_version": "14.0",
      "watch_app": true,
      "siri_shortcuts": true,
      "widgets": true
    },
    "Android": {
      "min_version": "8.0",
      "wear_os": true,
      "android_auto": false
    },
    "Windows": {
      "surface_hub": true,
      "hololens": true
    }
  }
}
```

### Barcode & QR Code Scanning
```csharp
// Example: Filter report by barcode
// In Power BI Desktop:
// 1. Create parameter: ScannedBarcode
// 2. Create measure with filter:
Filtered Sales =
CALCULATE(
    SUM(Sales[Amount]),
    Products[Barcode] = ScannedBarcode
)

// In mobile app:
// 1. Open report
// 2. Tap scan icon
// 3. Scan product barcode
// 4. Report filters to that product
```

### Push Notifications
```
Data Alerts:
1. Mobile app → Open report
2. Long-press on visual (card, gauge, KPI)
3. Set alert rule:
   - Threshold: > $100,000
   - Check frequency: Daily
   - Notification: Push + Email
4. Receive notification when condition met

Supported visual types:
- Card
- Gauge
- KPI
```

### HoloLens & Mixed Reality
```
Power BI for HoloLens:
- 3D data visualizations in AR
- Spatial anchoring of reports
- Voice commands
- Gesture controls

Example use cases:
- Factory floor analytics
- Retail store performance
- Real estate data visualization
```

## Looker Mobile

### Responsive Dashboards
```lookml
# LookML dashboard with mobile optimization
- dashboard: mobile_sales
  title: Sales Dashboard
  layout: newspaper  # Responsive grid
  preferred_viewer: dashboards-next  # Modern renderer

  elements:
  - title: Total Revenue
    name: revenue_card
    type: single_value
    fields: [orders.total_amount]
    # Mobile optimizations
    note_state: collapsed  # Hide notes on mobile
    show_single_value_title: true
    single_value_title: "Revenue"

  - title: Orders by Category
    name: category_chart
    type: looker_column
    fields: [products.category, orders.count]
    # Simplify for mobile
    show_value_labels: false  # Less cluttered
    x_axis_label: ""  # More space for data
```

### Mobile SDK Customization
```swift
// iOS: Custom mobile app with Looker SDK
import UIKit
import LookerSDK

class DashboardViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()

        // Initialize Looker
        let config = LookerSDKConfig(
            baseURL: "https://company.looker.com",
            clientID: "your-client-id"
        )

        let sdk = LookerSDK(config: config)

        // Authenticate
        sdk.authenticate(username: "user", password: "pass") { result in
            switch result {
            case .success:
                self.loadDashboard()
            case .failure(let error):
                print("Auth failed: \(error)")
            }
        }
    }

    func loadDashboard() {
        // Create embed URL with mobile parameters
        let embedURL = sdk.createEmbedURL(
            dashboardID: "123",
            filters: ["date": "7 days"],
            theme: "mobile"  // Mobile-optimized theme
        )

        // Load in WKWebView
        let webView = WKWebView(frame: view.bounds)
        webView.load(URLRequest(url: embedURL))
        view.addSubview(webView)
    }
}
```

### Mobile Alerts
```ruby
# Looker schedule for mobile notifications
# Create in Looker UI or via API

looker.schedule_plan.create(
  name: "Daily Sales Alert",
  look_id: 456,
  enabled: true,
  crontab: "0 9 * * *",  # 9 AM daily
  timezone: "America/Los_Angeles",
  scheduled_plan_destination: [{
    type: "webhook",
    address: "https://api.company.com/mobile-push",
    format: "json"
  }]
)

# Webhook endpoint processes and sends push
```

## Qlik Sense Mobile

### Qlik Sense Mobile App
```javascript
// Custom mobile app configuration
{
  "qlikCloud": {
    "url": "https://company.us.qlikcloud.com",
    "authMethod": "JWT",
    "offlineEnabled": true,
    "syncInterval": 3600  // Seconds
  },
  "ui": {
    "theme": "dark",
    "gestures": {
      "swipeToRefresh": true,
      "pinchToZoom": true,
      "doubleTapToReset": true
    }
  },
  "offline": {
    "maxApps": 10,
    "maxAgeHours": 168  // 7 days
  }
}
```

### Responsive Design
```qlik
// Qlik Sense app with responsive containers
// In app edit mode:
// 1. Insert container object
// 2. Set "Responsive behavior" to enabled
// 3. Define breakpoints:
//    - Mobile: < 600px
//    - Tablet: 600-1024px
//    - Desktop: > 1024px
// 4. Customize layout per breakpoint

// Conditional show/hide based on device
=if(GetCurrentDevice() = 'phone', 'show', 'hide')

// Simplified expressions for mobile
=if(
  GetCurrentDevice() = 'phone',
  Sum(Sales),  // Simple on mobile
  Sum({<Year={$(vCurrentYear)}>} Sales) / Sum({<Year={$(vPriorYear)}>} Sales)  // Complex on desktop
)
```

### Offline Capabilities
```
Qlik Sense Mobile Offline:
1. Open app while online
2. Tap "Make available offline"
3. App downloads to device (encrypted)
4. Use fully offline with all interactions
5. Sync changes when online

Advantages over competitors:
- Full interactivity offline (not just snapshots)
- Associative engine runs locally
- Selections and filtering work
```

## Apache Superset Mobile

### Progressive Web App (PWA)
```javascript
// Superset as PWA
// superset-pwa-config.js
module.exports = {
  pwa: {
    name: 'Superset Mobile',
    themeColor: '#20A7C9',
    backgroundColor: '#ffffff',
    display: 'standalone',
    orientation: 'any',
    icons: [
      {
        src: '/static/assets/images/icon-192.png',
        sizes: '192x192',
        type: 'image/png'
      },
      {
        src: '/static/assets/images/icon-512.png',
        sizes: '512x512',
        type: 'image/png'
      }
    ]
  },
  workbox: {
    runtimeCaching: [
      {
        urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/,
        handler: 'CacheFirst'
      },
      {
        urlPattern: /^https:\/\/superset\.company\.com\/api\/.*/,
        handler: 'NetworkFirst',
        options: {
          cacheName: 'api-cache',
          expiration: {
            maxEntries: 50,
            maxAgeSeconds: 300  // 5 minutes
          }
        }
      }
    ]
  }
};
```

### Responsive Dashboards
```python
# superset_config.py
# Mobile-optimized configuration

# Reduce default row limit for mobile
ROW_LIMIT = 1000  # Lower for mobile performance

# Chart defaults for mobile
CHART_DEFAULT_HEIGHT = 400  # Fit mobile screens

# Enable touch-friendly controls
ENABLE_JAVASCRIPT_CONTROLS = True

# Custom CSS for mobile
def CUSTOM_CSS_GENERATOR():
    return '''
    @media (max-width: 768px) {
        .dashboard-grid {
            grid-template-columns: 1fr !important;
        }
        .chart-container {
            height: auto !important;
            min-height: 300px;
        }
        .filter-box {
            position: sticky;
            top: 0;
            z-index: 100;
        }
    }
    '''
```

### Custom Mobile Push Notifications
```python
# Flask route for mobile notifications
from flask import Flask, request
import firebase_admin
from firebase_admin import messaging

app = Flask(__name__)

@app.route('/api/send-mobile-alert', methods=['POST'])
def send_mobile_alert():
    """Send push notification to mobile devices"""
    data = request.json

    message = messaging.Message(
        notification=messaging.Notification(
            title=data['title'],
            body=data['body']
        ),
        data={
            'dashboard_id': str(data['dashboard_id']),
            'chart_id': str(data['chart_id']),
            'value': str(data['value'])
        },
        token=data['device_token']
    )

    response = messaging.send(message)
    return {'success': True, 'message_id': response}

# Schedule check (with Celery)
@celery.task
def check_kpi_threshold():
    # Query Superset database
    result = run_query("SELECT SUM(sales) FROM sales_today")

    if result['value'] < THRESHOLD:
        # Send to all subscribed mobile devices
        send_mobile_alert({
            'title': 'Sales Alert',
            'body': f'Sales below threshold: ${result["value"]:,.0f}',
            'dashboard_id': 123,
            'device_token': user.mobile_token
        })
```

## Cross-Platform Mobile Best Practices

### Design Principles
```
1. Simplicity
   - Fewer metrics per screen
   - Focus on key insights
   - Avoid clutter

2. Touch-First
   - Buttons ≥ 44x44 pixels
   - Swipe gestures for navigation
   - Long-press for context menus

3. Performance
   - Limit data to essentials
   - Use sampling for large datasets
   - Progressive loading

4. Offline Capability
   - Cache critical data
   - Queue actions for sync
   - Clear offline/online status

5. Context-Aware
   - Location-based filters
   - Time-based defaults
   - User role customization
```

### Mobile Dashboard Checklist
- [ ] Portrait orientation optimized
- [ ] Large touch targets (min 44px)
- [ ] Simplified visualizations
- [ ] Fast load time (< 3s on 4G)
- [ ] Minimal text input required
- [ ] Clear error messages
- [ ] Graceful offline degradation
- [ ] Biometric authentication
- [ ] Push notification opt-in
- [ ] Dark mode support

### Performance Optimization
```sql
-- Mobile-specific data aggregation
CREATE VIEW mobile_dashboard_data AS
SELECT
    DATE(order_date) AS date,  -- Daily granularity sufficient
    category,
    SUM(amount) AS total_sales,
    COUNT(*) AS order_count,
    AVG(amount) AS avg_order_value
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '90 days'  -- Limited time range
GROUP BY 1, 2;

-- Index for fast mobile queries
CREATE INDEX idx_mobile_date ON mobile_dashboard_data(date);
```

### Mobile Analytics Tracking
```javascript
// Track mobile usage patterns
function trackMobileInteraction(event) {
    analytics.track('Mobile Dashboard Interaction', {
        device_type: navigator.userAgent,
        screen_size: `${window.screen.width}x${window.screen.height}`,
        orientation: screen.orientation.type,
        connection_type: navigator.connection?.effectiveType,
        dashboard_id: currentDashboard.id,
        interaction_type: event.type,
        timestamp: new Date().toISOString()
    });
}

// Analyze mobile vs desktop usage
SELECT
    CASE
        WHEN device_type LIKE '%Mobile%' THEN 'Mobile'
        WHEN device_type LIKE '%Tablet%' THEN 'Tablet'
        ELSE 'Desktop'
    END AS device_category,
    COUNT(DISTINCT user_id) AS active_users,
    AVG(session_duration_seconds) AS avg_session_duration,
    AVG(dashboards_viewed) AS avg_dashboards_per_session
FROM analytics_events
WHERE event_date >= CURRENT_DATE - 30
GROUP BY 1;
```

## Platform-Specific Recommendations

### Choose Tableau Mobile if:
- Need best-in-class mobile UX
- Device-specific layouts important
- Offline snapshots sufficient
- Metrics/KPI monitoring focus

### Choose Power BI Mobile if:
- Microsoft ecosystem integration
- Barcode/QR scanning needed
- HoloLens/AR use cases
- Windows tablet deployment

### Choose Looker Mobile if:
- Custom mobile app development
- SDK/API customization needed
- Responsive web-first approach

### Choose Qlik Mobile if:
- Full offline interactivity required
- Associative exploration on mobile
- Complex mobile use cases

### Choose Superset Mobile if:
- PWA deployment preferred
- Custom mobile solution needed
- Budget-conscious approach

## Testing Mobile Deployments

### Device Testing Matrix
| Device | Browser | Test Scenarios |
|--------|---------|----------------|
| iPhone 15 Pro | Safari | Core functionality, gestures |
| iPhone SE | Safari | Small screen layout |
| iPad Pro | Safari | Tablet layout, multitasking |
| Samsung Galaxy S24 | Chrome | Android functionality |
| Samsung Tab | Chrome | Android tablet |
| Desktop Emulator | Chrome DevTools | Responsive breakpoints |

### Testing Checklist
```bash
# Mobile testing script
#!/bin/bash

# 1. Responsive breakpoints
- 320px (iPhone SE)
- 375px (iPhone 12/13)
- 414px (iPhone Pro Max)
- 768px (iPad portrait)
- 1024px (iPad landscape)

# 2. Touch interactions
- Tap targets (≥ 44x44px)
- Swipe gestures
- Pinch to zoom
- Long press menus

# 3. Performance
- Time to interactive < 3s (4G)
- Smooth scrolling (60fps)
- Minimal layout shift

# 4. Network conditions
- 4G, 3G, 2G simulation
- Offline mode
- Intermittent connectivity

# 5. Notifications
- Push notification delivery
- Deep links to dashboards
- Badge updates

# 6. Security
- Biometric authentication
- Session timeout
- Data encryption (at rest/transit)
```

## Resources
- Tableau Mobile: https://help.tableau.com/current/mobile/en-us/
- Power BI Mobile: https://docs.microsoft.com/en-us/power-bi/consumer/mobile/
- Looker Mobile SDK: https://developers.looker.com/
- Qlik Sense Mobile: https://help.qlik.com/en-US/sense-mobile/

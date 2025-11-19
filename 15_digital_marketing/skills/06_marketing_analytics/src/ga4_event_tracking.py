"""
Google Analytics 4 (GA4) Event Tracking Implementation
Complete tracking setup for marketing websites
"""

# GA4 Event Tracking Configuration

## Standard E-commerce Events

### View Item
```javascript
gtag('event', 'view_item', {
  currency: 'USD',
  value: 29.99,
  items: [{
    item_id: 'SKU_12345',
    item_name: 'Premium Widget',
    item_category: 'Widgets',
    price: 29.99,
    quantity: 1
  }]
});
```

### Add to Cart
```javascript
gtag('event', 'add_to_cart', {
  currency: 'USD',
  value: 29.99,
  items: [{
    item_id: 'SKU_12345',
    item_name: 'Premium Widget',
    price: 29.99,
    quantity: 1
  }]
});
```

### Begin Checkout
```javascript
gtag('event', 'begin_checkout', {
  currency: 'USD',
  value: 59.98,
  coupon: 'SUMMER20',
  items: [
    {
      item_id: 'SKU_12345',
      item_name: 'Premium Widget',
      price: 29.99,
      quantity: 2
    }
  ]
});
```

### Purchase
```javascript
gtag('event', 'purchase', {
  transaction_id: 'T_12345',
  value: 59.98,
  tax: 4.80,
  shipping: 5.99,
  currency: 'USD',
  coupon: 'SUMMER20',
  items: [{
    item_id: 'SKU_12345',
    item_name: 'Premium Widget',
    price: 29.99,
    quantity: 2
  }]
});
```

## Custom Marketing Events

### Form Submission
```javascript
gtag('event', 'generate_lead', {
  currency: 'USD',
  value: 50.00,  // Estimated lead value
  form_name: 'Contact Us',
  form_location: 'Homepage'
});
```

### Video Engagement
```javascript
// Video start
gtag('event', 'video_start', {
  video_title: 'Product Demo',
  video_provider: 'youtube',
  video_url: 'https://youtube.com/watch?v=123'
});

// Video 25% complete
gtag('event', 'video_progress', {
  video_title: 'Product Demo',
  video_percent: 25
});

// Video complete
gtag('event', 'video_complete', {
  video_title: 'Product Demo',
  video_duration: 180
});
```

### File Downloads
```javascript
gtag('event', 'file_download', {
  file_name: 'whitepaper-marketing-guide.pdf',
  file_extension: 'pdf',
  link_url: '/downloads/whitepaper-marketing-guide.pdf'
});
```

### Scroll Depth
```javascript
gtag('event', 'scroll', {
  percent_scrolled: 75,
  page_location: window.location.href
});
```

### CTA Click Tracking
```javascript
gtag('event', 'cta_click', {
  cta_name: 'Start Free Trial',
  cta_location: 'Hero Section',
  cta_destination: '/signup'
});
```

## Implementation with Google Tag Manager

### Data Layer Push (Recommended)
```javascript
window.dataLayer = window.dataLayer || [];
dataLayer.push({
  'event': 'generate_lead',
  'formName': 'Demo Request',
  'formLocation': 'Pricing Page',
  'leadValue': 100
});
```

### GTM Tag Configuration
1. Create new GA4 Event Tag
2. Set Event Name: `{{Event}}` variable
3. Add Event Parameters as needed
4. Trigger: Custom Event = 'generate_lead'

## User Properties
```javascript
gtag('set', 'user_properties', {
  subscription_tier: 'Premium',
  user_type: 'B2B',
  signup_date: '2024-01-15'
});
```

## Enhanced Measurement (Auto-tracked)
Enable in GA4 Admin:
- Page views ✓
- Scrolls ✓
- Outbound clicks ✓
- Site search ✓
- Video engagement ✓
- File downloads ✓

## Testing Events
Use GA4 DebugView:
1. Install Google Tag Assistant Chrome extension
2. Enable Debug mode
3. Trigger events
4. Verify in GA4 DebugView (real-time)

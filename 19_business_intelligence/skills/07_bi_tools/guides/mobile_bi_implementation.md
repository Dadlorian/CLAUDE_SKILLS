# Mobile BI Implementation Guide

## Mobile Strategy

### Design Approach
1. **Mobile-First**: Design for smallest screen
2. **Responsive**: Adapt to screen size
3. **Progressive**: Basic mobile, advanced desktop

## Implementation Steps

### Step 1: Audit Existing Content
- [ ] Identify critical dashboards
- [ ] Review on mobile device
- [ ] Note usability issues
- [ ] Prioritize for mobile optimization

### Step 2: Simplify for Mobile
```
Desktop Dashboard (12 visuals)
       ↓
Mobile Dashboard (3-5 visuals)
├─ Key KPIs only
├─ Simple charts
├─ Minimal filters
└─ Vertical scrolling
```

### Step 3: Design Mobile Layout

**Tableau**: Device Layouts
```
1. Dashboard → Device Layouts
2. Add Phone layout
3. Drag visuals from visualization pane
4. Arrange vertically
5. Test in Preview
```

**Power BI**: Phone Report
```
1. View → Mobile Layout
2. Drag visuals to phone canvas
3. Arrange in 1-2 column format
4. Publish
```

### Step 4: Test on Real Devices
- [ ] iPhone (latest 2 versions)
- [ ] Android (Samsung, Pixel)
- [ ] iPad/Tablet
- [ ] Various network speeds

## Mobile Design Patterns

### KPI Cards
```
┌────────────┐
│  Revenue   │  <- Label
│            │
│  $2.4M     │  <- Large value
│  ↑ 15%     │  <- Change indicator
└────────────┘
```

### Simplified Charts
- Bar charts (horizontal, easier on mobile)
- Line charts (1-2 series max)
- Single value cards
- Avoid: Complex visuals, dense tables

### Touch Targets
- Minimum: 44×44 pixels
- Spacing: 8px between elements
- Large tap areas
- Swipe gestures

## Offline Capability

**Tableau Mobile**:
- Save snapshots while online
- Access offline for configured duration
- Sync when reconnected

**Power BI Mobile**:
- Cached reports available offline
- Automatic sync when online
- Configurable cache duration

## Push Notifications

### Setup (Power BI)
```
1. Open report in mobile app
2. Long-press on visual
3. Set alert rule
4. Configure threshold
5. Enable push notification
```

### Use Cases
- Sales below target
- System alerts
- Daily KPI updates
- Exception reporting

## Performance for Mobile

### Optimize Load Time
- Reduce visual count
- Use aggregated data
- Enable caching
- Compress images

### Network Considerations
- Design for 4G (not always WiFi)
- Minimize data transfer
- Progressive loading
- Graceful degradation

## Testing Checklist

- [ ] Loads < 3 seconds on 4G
- [ ] All text readable
- [ ] Touch targets large enough
- [ ] Filters easy to use
- [ ] Charts render correctly
- [ ] Works in portrait/landscape
- [ ] Offline mode functions
- [ ] Notifications deliver

## Resources
- Tableau Mobile: https://help.tableau.com/current/mobile/
- Power BI Mobile: https://docs.microsoft.com/power-bi/consumer/mobile/

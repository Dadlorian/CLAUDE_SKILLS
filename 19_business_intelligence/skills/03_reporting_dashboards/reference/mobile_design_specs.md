# Mobile Dashboard Design Specifications

## Mobile-First Philosophy

### Why Mobile Matters
- 50%+ of dashboard views on mobile/tablet
- Different use cases than desktop
- Limited screen real estate
- Touch interaction model
- Often time-critical, on-the-go access

### Mobile Dashboard Principles
1. **Prioritize ruthlessly**: Show only what matters most
2. **Simplify interactions**: Minimize taps and swipes
3. **Optimize for glanceability**: Quick insights at a glance
4. **Design for touch**: Large, accessible tap targets
5. **Respect data costs**: Minimize unnecessary transfers

---

## Screen Size Breakpoints

### Standard Breakpoints
```
Mobile Small:     320px - 480px   (iPhone SE, older Android)
Mobile Medium:    481px - 767px   (iPhone 14, most Android)
Tablet Portrait:  768px - 1024px  (iPad portrait, Android tablets)
Tablet Landscape: 1025px - 1280px (iPad landscape)
Desktop:          1281px+         (Laptops, monitors)
```

### Dashboard Layouts by Breakpoint

**Mobile Small (320-480px):**
- Single column only
- Large touch targets (44px minimum)
- Minimal charts (2-3 max visible)
- Collapsed navigation
- Progressive disclosure

**Mobile Medium (481-767px):**
- Single column primary
- Occasional 2-column for small cards
- 3-5 key metrics visible
- Simplified charts
- Bottom navigation or hamburger menu

**Tablet Portrait (768-1024px):**
- 2-column grid
- More chart complexity acceptable
- Side navigation possible
- 5-8 metrics visible
- Richer interactions

**Tablet Landscape (1025-1280px):**
- 3-4 column grid
- Near-desktop functionality
- Full navigation
- 8-12 metrics visible
- Desktop-like charts

---

## Touch Target Specifications

### Minimum Sizes (Per Apple/Google Guidelines)

**Touch Targets:**
- **Minimum:** 44px × 44px (iOS), 48dp × 48dp (Android)
- **Recommended:** 48px × 48px minimum for all platforms
- **Ideal:** 56-60px × 56-60px for important actions

**Spacing:**
- Minimum 8px between tap targets
- Recommended 12-16px for comfort

**Examples:**
```
Filter Button:    ┌──────────┐
                  │  Filter  │  48px × 48px minimum
                  └──────────┘

                  [  8px space  ]

Refresh Button:   ┌──────────┐
                  │ Refresh  │  48px × 48px minimum
                  └──────────┘
```

### Hit Areas vs Visual Size
- Visual button can be 32px
- Hit area should still be 48px
- Use padding to extend hit area

**CSS Example:**
```css
.mobile-button {
    min-width: 48px;
    min-height: 48px;
    padding: 12px 16px; /* Visual element smaller, hit area larger */
}
```

---

## Mobile Dashboard Layouts

### Pattern 1: Priority Stack (Executive Mobile)
```
┌─────────────────────┐
│  Top KPI            │  ← Most important metric
│  $1.2M (+15%)      │
│  [Sparkline]        │
├─────────────────────┤
│  Second KPI         │
│  89% (+3%)         │
│  [Sparkline]        │
├─────────────────────┤
│  Third KPI          │
│  1,234 (-5%)       │
│  [Sparkline]        │
├─────────────────────┤
│  [Simplified Chart] │  ← One key trend
├─────────────────────┤
│  [View More]        │  ← Link to full dashboard
└─────────────────────┘
```

**Characteristics:**
- Vertical scroll
- 3-5 top metrics
- Large, readable numbers
- Minimal chart complexity
- Clear hierarchy

### Pattern 2: Card Grid (Operational Mobile)
```
┌─────────┬─────────┐
│ KPI 1   │ KPI 2   │
│ Value   │ Value   │
├─────────┼─────────┤
│ KPI 3   │ KPI 4   │
│ Value   │ Value   │
├─────────┴─────────┤
│  Status Chart     │
│  (Simplified)     │
├───────────────────┤
│  [Alerts]         │
└───────────────────┘
```

**Characteristics:**
- 2-column grid for small cards
- Quick scanning
- Tap card for details
- Alerts prominent

### Pattern 3: Tab-Based Navigation
```
┌─────────────────────┐
│ [Sales][Ops][Fin]   │  ← Tabs for categories
├─────────────────────┤
│                     │
│  Sales Content      │
│  - KPIs             │
│  - Charts           │
│  - Details          │
│                     │
└─────────────────────┘
```

**Characteristics:**
- Categorized content
- 3-5 tabs maximum
- Swipeable content
- Persistent tab bar

### Pattern 4: Collapsible Sections
```
┌─────────────────────┐
│ ▼ Revenue (expanded)│
│   $1.2M (+15%)     │
│   [Chart]           │
├─────────────────────┤
│ ► Sales (collapsed) │
├─────────────────────┤
│ ► Support (collapsed)│
└─────────────────────┘
```

**Characteristics:**
- Accordion-style
- One section open at a time
- Touch to expand/collapse
- Conserves vertical space

---

## Chart Simplification for Mobile

### General Rules
1. **Reduce data series**: Max 2-3 lines on mobile
2. **Simplify axes**: Fewer labels, larger text
3. **Remove gridlines**: Clutters small space
4. **Direct labels**: No legends
5. **Increase touch targets**: Data points, bars

### Chart Type Adaptations

**Desktop Line Chart → Mobile**
```
Desktop:                    Mobile:
- 5 data series            - 1-2 most important series
- Detailed gridlines       - No gridlines
- Legend                   - Direct labels
- Small data points        - Larger points (touch targets)
- Detailed axis            - Simplified axis (min/max only)
```

**Desktop Bar Chart → Mobile**
```
Desktop:                    Mobile:
- 20 categories            - Top 5-10 categories
- Horizontal or vertical   - Horizontal (easier labels)
- Small bars               - Larger bars (44px min)
- Detailed labels          - Abbreviated labels
```

**Desktop Table → Mobile**
```
Desktop:                    Mobile:
- 8-10 columns             - 2-3 key columns
- Full data                - Tap for detail view
- Small text               - Larger, readable text
- Fixed headers            - Sticky headers
```

**Complex Dashboard Chart → Mobile Sparkline**
```
Desktop: Full featured chart with multiple series
Mobile: Sparkline in card showing trend only
Interaction: Tap sparkline to open full chart view
```

### Chart Library Settings

**Tableau Mobile:**
```
- Device Designer: Create mobile-specific layout
- Show/Hide: Hide complex charts on mobile
- Replace: Swap complex charts with simple alternatives
- Filters: Reduce filter options on mobile
```

**Power BI Mobile:**
```
- Mobile Layout: Reorder and resize visuals
- Focus Mode: Enable for detailed chart view
- Phone Layout: Dedicated mobile canvas
- Tooltips: Simplified for touch
```

---

## Typography for Mobile

### Font Sizes
```
Large Numbers (KPIs):  32-48px
Metric Labels:         16-18px
Body Text:            14-16px
Secondary Text:       12-14px
Minimum Readable:     11px (avoid if possible)
```

### Font Weights
- Use heavier weights on mobile (harder to read in sunlight)
- KPI values: 600-700 weight
- Labels: 400-500 weight

### Line Height
- Increase line height for readability: 1.5-1.6
- More generous spacing than desktop

---

## Mobile Navigation Patterns

### Bottom Tab Bar (Recommended for ≤5 sections)
```
┌─────────────────────┐
│                     │
│   Content Area      │
│                     │
├─────────────────────┤
│ [📊][📈][⚙️][👤] │  ← Bottom tabs
└─────────────────────┘
```

**Pros:**
- Easy thumb access
- Always visible
- Quick switching

**Cons:**
- Limited to 4-5 tabs
- Takes vertical space

### Hamburger Menu (For >5 sections)
```
┌─────────────────────┐
│ ☰ Dashboard    [⚙️] │  ← Header with menu
├─────────────────────┤
│                     │
│   Content Area      │
│                     │
└─────────────────────┘

Opened:
┌─────────────────────┐
│ Revenue Dashboard   │
│ Sales Dashboard     │
│ Operations         │
│ Customer Metrics   │
│ Settings           │
└─────────────────────┘
```

**Pros:**
- Handles many sections
- Familiar pattern
- Saves space

**Cons:**
- Hidden navigation
- Extra tap required

### Swipeable Views
```
← [Sales]  [Ops]  [Finance] →
     ↓ Swipe left/right
```

**Best For:**
- Equal-priority sections
- Linear workflow
- Frequent switching

---

## Filters on Mobile

### Pattern 1: Bottom Sheet Filter
```
Tap "Filters" →

┌─────────────────────┐
│     Main View       │
├═════════════════════┤ ← Sheet slides up
│ ▼ Filters          │
│ Date Range: [...]   │
│ Region: [...]       │
│ Product: [...]      │
│ [Apply] [Clear]     │
└─────────────────────┘
```

**Pros:**
- Doesn't obscure content
- Clear apply/cancel
- Native feel

### Pattern 2: Sticky Filter Bar
```
┌─────────────────────┐
│ [Date▾] [Region▾]  │  ← Always visible
├─────────────────────┤
│                     │
│   Filtered Content  │
│                     │
└─────────────────────┘
```

**Pros:**
- Always visible
- Quick access
- Filter state clear

**Cons:**
- Uses vertical space
- Limited filters fit

### Pattern 3: Modal Filter
```
Tap "Filter" →

Full-screen modal:
┌─────────────────────┐
│ [✕] Filters         │
├─────────────────────┤
│ Date Range          │
│ [Picker]            │
│                     │
│ Region              │
│ [Picker]            │
│                     │
│ [Apply Filters]     │
└─────────────────────┘
```

**Best For:**
- Complex filters
- Dependent filters
- Guided filtering

---

## Performance Optimization for Mobile

### Data Loading Strategy

**Priority Loading:**
1. Load visible KPIs first (above fold)
2. Load visible charts second
3. Lazy-load below-fold content
4. Defer detailed data until interaction

**Progressive Enhancement:**
```
Initial Load: Summary data only (lightweight)
User Scroll:  Load next section
User Tap:     Load detailed view
```

### Caching Strategy
```
- Cache last loaded dashboard locally
- Offline mode with cached data
- Background sync when connected
- Show data age clearly
```

### Data Transfer Minimization
```
❌ Don't: Load full desktop dataset
✓ Do: Load aggregated mobile-specific data
✓ Do: Implement server-side filtering
✓ Do: Use incremental loading
```

---

## Mobile-Specific Features

### Offline Mode
```
┌─────────────────────┐
│ ⚠️ Offline Mode     │  ← Clear indicator
│ Data as of 2:30 PM  │
├─────────────────────┤
│  [Cached Dashboard] │
│                     │
│ [Sync when online]  │
└─────────────────────┘
```

### Pull-to-Refresh
```
User pulls down ↓
┌─────────────────────┐
│    ↻ Refreshing...  │
├─────────────────────┤
│   Dashboard Content │
└─────────────────────┘
```

### Push Notifications
```
Alert: "Sales target reached! 🎉"
Tap notification → Opens to relevant dashboard section
```

### Voice Interaction (Advanced)
```
User: "Show me today's revenue"
Dashboard: Opens revenue card, reads value aloud
```

---

## Testing Checklist

**Device Testing:**
- [ ] iPhone SE (smallest common size)
- [ ] iPhone 14/15 (standard size)
- [ ] iPhone 14 Pro Max (large)
- [ ] Android (Samsung, Pixel)
- [ ] iPad (both orientations)
- [ ] Android tablet

**Interaction Testing:**
- [ ] All buttons have 44px+ hit areas
- [ ] Swipe gestures work smoothly
- [ ] Filters are accessible and functional
- [ ] Charts are readable and interactive
- [ ] No horizontal scrolling (unless intentional)
- [ ] Works in both orientations

**Performance Testing:**
- [ ] Load time <3 seconds on mobile network
- [ ] Smooth scrolling (60fps)
- [ ] No layout jank
- [ ] Graceful degradation on slow network

**Content Testing:**
- [ ] Numbers are large and readable
- [ ] Labels aren't truncated
- [ ] Charts are simplified appropriately
- [ ] Most important content above fold
- [ ] Text readable in sunlight (contrast)

---

## Mobile Dashboard Anti-Patterns

### ❌ Desktop Squeezed onto Mobile
Simply shrinking desktop dashboard to fit mobile screen

**Problems:**
- Tiny, unreadable text
- Unusable touch targets
- Cluttered, overwhelming
- Slow performance

### ❌ Horizontal Scrolling
Requiring horizontal scroll to see data

**Problems:**
- Hidden information
- Poor UX
- Easy to miss content

### ❌ Tiny Charts
Complex charts shrunk to mobile size

**Problems:**
- Illegible
- Not interactive
- Defeats purpose

**Solution:** Simplify or replace with summary

### ❌ Desktop-Style Filters
Complex filter panel with many options

**Problems:**
- Takes too much space
- Difficult to use with touch
- Overwhelming

**Solution:** Use progressive disclosure, bottom sheets

### ❌ Information Overload
Trying to show everything at once

**Problems:**
- Cognitive overload
- Slow loading
- Poor prioritization

**Solution:** Ruthlessly prioritize, use drill-down

---

## Platform-Specific Guidelines

### iOS Design Patterns
- Use native iOS components where possible
- Follow iOS Human Interface Guidelines
- Safe areas (notch, home indicator)
- Haptic feedback for interactions

### Android Material Design
- Material Design 3 principles
- Floating Action Button (FAB) for primary action
- Bottom navigation for 3-5 sections
- Elevation and shadows for hierarchy

### Responsive Web Dashboard
- CSS Grid/Flexbox for layouts
- Media queries for breakpoints
- Touch-optimized interactions
- Service worker for offline support

---

## Example: Mobile Executive Dashboard Spec

**Viewport:** 375px × 812px (iPhone 14)

**Layout:**
```
┌───────────────────────┐
│ ☰  Revenue Dashboard  │ 60px header
├───────────────────────┤
│ Revenue: $1.2M        │ 120px
│ +15% vs target        │ KPI card
│ [━━━━━━━━━] Sparkline│
├───────────────────────┤
│ New Customers: 234    │ 120px
│ +8% vs last month     │ KPI card
│ [━━━━━━━━━] Sparkline│
├───────────────────────┤
│ Churn Rate: 2.3%     │ 120px
│ Target: <3%  ✓       │ KPI card
│ [━━━━━━━━━] Sparkline│
├───────────────────────┤
│ Monthly Trend         │ 200px
│ [Simplified line chart]│ Chart
├───────────────────────┤
│ [View Full Dashboard] │ 60px
└───────────────────────┘ Button
```

**Interactions:**
- Pull down to refresh
- Tap KPI card to see detailed view
- Tap chart to expand
- Swipe between dashboard pages

---

## Resources & Tools

**Testing Tools:**
- Chrome DevTools (device emulation)
- BrowserStack (real device testing)
- Responsive Design Mode (Firefox)

**Design Tools:**
- Figma (mobile prototypes)
- Sketch (iOS design)
- Adobe XD (cross-platform)

**Performance:**
- Lighthouse (mobile performance)
- WebPageTest (mobile testing)
- Chrome User Experience Report

**Guidelines:**
- iOS Human Interface Guidelines
- Material Design 3
- WCAG 2.1 Mobile Accessibility

---

## References
- Luke Wroblewski: "Mobile First"
- Josh Clark: "Designing for Touch"
- Apple: iOS Human Interface Guidelines
- Google: Material Design Guidelines
- Stephen Few: "Dashboard Design for Mobile Devices"

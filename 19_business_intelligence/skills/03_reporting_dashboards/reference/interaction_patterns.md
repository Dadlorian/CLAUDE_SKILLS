# Dashboard Interaction Patterns

## Core Interaction Principles

### 1. Direct Manipulation
**Principle**: Users interact directly with visual elements, not through intermediary controls

**Examples**:
- Click bar to filter
- Drag to select range
- Hover for details

### 2. Immediate Feedback
**Principle**: System responds instantly to user actions (<100ms ideal)

**Examples**:
- Highlight on hover
- Filter updates visible charts
- Progress indicators for slow operations

### 3. Reversibility
**Principle**: Users can undo actions easily

**Examples**:
- Clear filter button
- Back navigation
- Reset to default state

---

## Filter Patterns

### Pattern 1: Single-Apply Filters

**Use When**: Multiple filters, complex queries, performance considerations

**Implementation**:
```
┌─────────────────────────┐
│ FILTERS                 │
├─────────────────────────┤
│ Date Range:             │
│ [2024-01-01 to ...]     │
│                         │
│ Region:                 │
│ □ North  □ South        │
│ □ East   ☑ West         │
│                         │
│ Product:                │
│ [Select products ▾]     │
│                         │
│ [Apply Filters]  [Clear]│
└─────────────────────────┘
```

**Pros**:
- One query instead of many
- User can set all filters before applying
- Better performance

**Cons**:
- Extra click required
- Not as immediate

**Best For**: Analytical dashboards, large datasets

### Pattern 2: Auto-Apply Filters

**Use When**: Fast queries, few filters, exploration-focused

**Implementation**:
```
┌─────────────────────────┐
│ FILTERS                 │
├─────────────────────────┤
│ Date: [Last 30 days ▾]  │ ← Updates on change
│                         │
│ Region: [All ▾]         │ ← Updates on change
│                         │
│ Product: [All ▾]        │ ← Updates on change
│                         │
│ [Clear All Filters]     │
└─────────────────────────┘
```

**Pros**:
- Immediate feedback
- Exploration-friendly
- No extra click

**Cons**:
- Multiple queries
- Can be slow with large data
- Accidental filter changes

**Best For**: Executive dashboards, fast extracts

### Pattern 3: Search/Filter Combo

**Use When**: Many options to filter (hundreds of products, customers, etc.)

**Implementation**:
```
┌─────────────────────────┐
│ Product: [Search...]    │
│                         │
│ Type to filter:         │
│ ☑ Product A             │
│ ☐ Product B             │
│ ☐ Product C             │
│ ...                     │
│                         │
│ [Apply]                 │
└─────────────────────────┘
```

**Interactions**:
- Type "Pr" → Shows Product A, B, C
- Select multiple
- Apply to update dashboard

### Pattern 4: Cascading Filters

**Use When**: Hierarchical data, dependent filters

**Implementation**:
```
┌─────────────────────────┐
│ Region: [North ▾]       │ ← Select first
│                         │
│ State: [NY ▾]           │ ← Filtered by region
│                         │
│ City: [NYC ▾]           │ ← Filtered by state
│                         │
│ [Apply]                 │
└─────────────────────────┘
```

**Behavior**:
- Selecting Region updates State options
- Selecting State updates City options
- Prevents invalid combinations

### Pattern 5: Filter Chips (Selected Filters Visible)

**Use When**: Many filter options, need to see active filters

**Implementation**:
```
┌─────────────────────────────────────┐
│ Active Filters:                     │
│ [Date: Last 30 days ✕]              │
│ [Region: North ✕]                   │
│ [Product: Product A ✕]              │
│                                     │
│ + Add Filter                        │
└─────────────────────────────────────┘
```

**Interaction**:
- Click ✕ to remove filter
- Click chip to edit filter
- "+ Add Filter" opens filter selector

**Pros**:
- Clear what's filtered
- Easy to remove individual filters
- No hidden state

---

## Drill-Down Patterns

### Pattern 1: Click to Drill

**Use When**: Exploring hierarchical data

**Interaction Flow**:
```
Level 1: Revenue by Region
┌─────────────────┐
│ North   $1.2M   │ ← Click
│ South   $890K   │
│ East    $750K   │
└─────────────────┘
        ↓
Level 2: North Region by State
┌─────────────────┐
│ NY      $500K   │ ← Click
│ MA      $400K   │
│ CT      $300K   │
└─────────────────┘
        ↓
Level 3: NY by City
┌─────────────────┐
│ NYC     $300K   │
│ Buffalo $100K   │
│ Albany  $100K   │
└─────────────────┘
```

**Navigation**:
```
Breadcrumbs: Home > North > NY
[Back] button
```

### Pattern 2: Drill-Down in Place

**Use When**: Want to maintain context

**Implementation**:
```
Revenue by Region  [Collapse ▲]
┌─────────────────────────────┐
│ ▼ North   $1.2M             │ ← Expanded
│   ├─ NY     $500K           │
│   ├─ MA     $400K           │
│   └─ CT     $300K           │
│                             │
│ ▶ South   $890K             │ ← Collapsed
│ ▶ East    $750K             │
└─────────────────────────────┘
```

**Interaction**:
- Click ▶ to expand
- Click ▼ to collapse
- Maintains context of other regions

### Pattern 3: Drill-Down Modal/Sidebar

**Use When**: Detailed information, don't want to leave current view

**Implementation**:
```
Main Dashboard
┌─────────────────────────────┐
│ [Chart showing regions]     │
│ Click North →               │
└─────────────────────────────┘

        ↓

┌─────────────────────────────┐
│ [Main dashboard dimmed]     │
│                             │
│  ┌──────────────────────┐  │
│  │ North Region Details │  │
│  │                      │  │
│  │ [Detailed charts]    │  │
│  │                      │  │
│  │ [Close ✕]           │  │
│  └──────────────────────┘  │
└─────────────────────────────┘
```

### Pattern 4: Focus + Context

**Use When**: Need overview and detail simultaneously

**Implementation**:
```
┌─────────────────────────────────┐
│ Overview (All Regions)          │
│ [Small multiples chart]         │
│                                 │
│ North  South  East   West       │
│ [▲]    [─]    [▼]    [▲]       │
│        ↑                        │
│    Selected                     │
├─────────────────────────────────┤
│ Detail (South Region)           │
│ [Large detailed chart]          │
│                                 │
└─────────────────────────────────┘
```

**Interaction**:
- Overview always visible
- Click region to update detail
- Both synchronized

---

## Selection Patterns

### Pattern 1: Single Selection

**Use When**: One item at a time

**Visual Feedback**:
```
Product Performance
┌─────────────────┐
│ Product A       │ ← Unselected (gray)
│ Product B       │ ← Selected (highlighted)
│ Product C       │ ← Unselected (gray)
└─────────────────┘
```

**Behavior**:
- Click selects
- Previous selection deselected
- Clear visual indication

### Pattern 2: Multi-Selection

**Use When**: Compare multiple items

**Visual Feedback**:
```
Product Comparison
┌─────────────────┐
│ ☑ Product A     │ ← Selected
│ ☐ Product B     │ ← Unselected
│ ☑ Product C     │ ← Selected
│ ☑ Product D     │ ← Selected
└─────────────────┘

[Chart shows only A, C, D]
```

**Interaction**:
- Checkboxes for explicit selection
- Or: Cmd/Ctrl+Click for multiple
- Limit: 5-7 selections max

### Pattern 3: Range Selection

**Use When**: Continuous data, time series

**Implementation**:
```
Revenue Trend
┌─────────────────────────────┐
│        [Brush area]         │
│   ┌────────────┐            │
│   │╱╱╱╱╱╱╱╱╱╱╱│            │
│ ──┘            └────────    │
│ Jan  Feb  Mar  Apr  May     │
│     └──┬───┘                │
│     Selected                │
└─────────────────────────────┘

Detail View:
[Shows only Feb-Mar data]
```

**Interaction**:
- Click and drag to select range
- Handles to adjust range
- Click outside to clear

---

## Hover/Tooltip Patterns

### Pattern 1: Simple Tooltip

**Use When**: Additional context, exact values

**Implementation**:
```
[User hovers over bar]
        ↓
┌─────────────────┐
│ North Region    │
│ Revenue: $1.2M  │
│ +15% vs target  │
└─────────────────┘
```

**Best Practices**:
- 300-500ms delay before show
- Follow cursor or anchor to element
- Clear, concise content
- Easy to dismiss (move away)

### Pattern 2: Rich Tooltip

**Use When**: Complex information, mini-dashboard

**Implementation**:
```
[Hover over product name]
        ↓
┌──────────────────────────┐
│ Product A                │
│                          │
│ Revenue:    $500K        │
│ Units Sold: 1,234        │
│ Margin:     23%          │
│                          │
│ [Mini trend chart]       │
│                          │
│ [View Details →]         │
└──────────────────────────┘
```

**Best Practices**:
- Include visualization when helpful
- Action link if needed
- Not too large (max 300×400px)

### Pattern 3: Persistent Details Panel

**Use When**: Frequent need for details, comparisons

**Implementation**:
```
┌────────────┬─────────────────┐
│ [Chart]    │ DETAILS         │
│            │                 │
│ [Hover →]  │ North Region:   │
│            │ Revenue: $1.2M  │
│            │ Customers: 234  │
│            │ ...             │
│            │                 │
└────────────┴─────────────────┘
```

**Behavior**:
- Panel always visible
- Updates on hover
- Allows comparison

---

## Time Selection Patterns

### Pattern 1: Preset Ranges

**Use When**: Common time periods

**Implementation**:
```
┌──────────────────────────┐
│ ○ Today                  │
│ ○ Last 7 days            │
│ ● Last 30 days           │ ← Selected
│ ○ Last quarter           │
│ ○ Last year              │
│ ○ Custom range...        │
└──────────────────────────┘
```

**Pros**:
- Fast selection
- Common use cases covered
- No date input required

### Pattern 2: Date Range Picker

**Use When**: Need specific dates

**Implementation**:
```
┌──────────────────────────┐
│ From: [2024-01-01 📅]    │
│ To:   [2024-01-31 📅]    │
│                          │
│ [Apply]                  │
└──────────────────────────┘

Click 📅:
┌──────────────┐
│  January     │
│ Su Mo Tu We..|
│  1  2  3  4..|
│  ...         │
└──────────────┘
```

### Pattern 3: Timeline Slider

**Use When**: Exploring trends over time

**Implementation**:
```
Revenue Over Time
┌─────────────────────────────┐
│ [Line chart]                │
│                             │
│ ●════════○                  │
│ Jan    Mar    Dec           │
│                             │
│ Showing: Jan - Mar 2024     │
└─────────────────────────────┘
```

**Interaction**:
- Drag handles to select range
- Chart updates in real-time
- Visual feedback

---

## Export/Share Patterns

### Pattern 1: Export Menu

**Implementation**:
```
[Export ▾]
├─ PDF
├─ PNG
├─ Excel
├─ CSV
└─ PowerPoint
```

**Best Practices**:
- Include current filters in export
- Filename with date and filters
- Maintain branding in exports

### Pattern 2: Share Link

**Implementation**:
```
[Share 🔗]
→ Copy link with current filters
→ Link expires in 7 days
```

**Use Cases**:
- Email to stakeholders
- Embed in documents
- Scheduled delivery

### Pattern 3: Subscribe/Alert

**Implementation**:
```
[Subscribe 🔔]

┌──────────────────────────┐
│ Email me:                │
│ ● Daily at 8 AM          │
│ ○ Weekly on Monday       │
│ ○ When value > threshold │
│                          │
│ [Subscribe]              │
└──────────────────────────┘
```

---

## Loading & Error Patterns

### Pattern 1: Progressive Loading

**Implementation**:
```
1. Skeleton/placeholder:
┌─────────────────┐
│ ░░░░░░░░░░░░░░ │
│ ░░░░░░░░░░░░░░ │
└─────────────────┘

2. Load metrics:
┌─────────────────┐
│ Revenue: $1.2M  │
│ ░░░░░░░░░░░░░░ │
└─────────────────┘

3. Load chart:
┌─────────────────┐
│ Revenue: $1.2M  │
│ [Chart]         │
└─────────────────┘
```

### Pattern 2: Optimistic Updates

**Implementation**:
```
User clicks filter →
Dashboard updates immediately (cached/estimated) →
Background: Query runs →
Update with accurate data when ready
```

**Best For**: Fast perceived performance

### Pattern 3: Graceful Errors

**Implementation**:
```
❌ Bad:
[Blank screen]

✓ Good:
┌─────────────────────────┐
│ ⚠ Unable to load data   │
│                         │
│ Last successful load:   │
│ 2:45 PM                 │
│                         │
│ [Retry] [Use Cached]    │
└─────────────────────────┘
```

---

## Responsive Interaction Patterns

### Desktop → Mobile Transitions

**Desktop: Hover**
```
Hover over bar → Tooltip appears
```

**Mobile: Tap**
```
Tap bar → Details panel opens
Tap outside → Panel closes
```

**Desktop: Multi-select with Ctrl+Click**
```
Click + Ctrl → Add to selection
```

**Mobile: Multi-select with checkboxes**
```
Tap checkbox → Add to selection
[Apply Selection] button
```

---

## Keyboard Shortcuts

**Essential Shortcuts**:
```
Tab:        Navigate between elements
Enter:      Activate/select
Esc:        Close modal/clear selection
Ctrl+F:     Open search/filter
Ctrl+R:     Refresh data
Arrow keys: Navigate within chart/table
```

**Power User Shortcuts**:
```
Ctrl+Shift+E: Export
Ctrl+Shift+S: Save view
Ctrl+Shift+R: Reset to default
```

---

## Best Practices

### DO:
✓ Provide immediate visual feedback (<100ms)
✓ Make actions reversible
✓ Show loading states
✓ Indicate selected/active state clearly
✓ Use standard patterns (don't reinvent)
✓ Support keyboard navigation
✓ Mobile-friendly interactions

### DON'T:
✗ Auto-apply slow filters
✗ Refresh without user control
✗ Hide critical filters
✗ Require precise mouse movements
✗ Use non-standard gestures
✗ Depend solely on hover (mobile issues)

---

## References
- Nielsen Norman Group: Dashboard Interaction Patterns
- Apple Human Interface Guidelines
- Material Design: Interaction
- Tableau: Dashboard Interactivity Best Practices

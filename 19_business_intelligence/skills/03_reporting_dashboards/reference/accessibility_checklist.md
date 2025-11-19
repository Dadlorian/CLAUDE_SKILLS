# Dashboard Accessibility Checklist (WCAG 2.1 AA)

## Why Accessibility Matters for Dashboards

### Legal & Ethical
- ADA, Section 508, WCAG 2.1 compliance required for many organizations
- Equal access to business intelligence for all users
- 15% of global population has some form of disability

### Business Benefits
- Larger potential user base
- Better usability for everyone
- Improved SEO and discoverability
- Reduced legal risk

### Types of Disabilities to Consider
1. **Visual**: Blindness, low vision, color blindness (8% of men)
2. **Motor**: Limited dexterity, tremors, cannot use mouse
3. **Cognitive**: Dyslexia, attention disorders, memory issues
4. **Auditory**: Deafness, hearing loss (less relevant for dashboards)

---

## WCAG 2.1 Level AA Requirements

### Perceivable: Information must be presentable to users

#### 1.1 Text Alternatives
- [ ] All charts have descriptive alt text
- [ ] Icons have text labels or ARIA labels
- [ ] Complex visualizations have extended descriptions

**Example:**
```html
<!-- Bar chart -->
<div role="img" aria-label="Monthly revenue bar chart showing 15% increase from $1.0M in January to $1.15M in February">
  [Chart visualization]
</div>

<!-- Icon button -->
<button aria-label="Refresh dashboard data">
  <icon>↻</icon>
</button>
```

#### 1.3 Adaptable: Content can be presented in different ways
- [ ] Proper heading hierarchy (h1 → h2 → h3, no skipping)
- [ ] Tables use proper semantic markup (thead, tbody, th, td)
- [ ] Lists use proper list markup (ul, ol, li)
- [ ] Forms have associated labels
- [ ] Reading order is logical when CSS removed

**Example:**
```html
<h1>Sales Dashboard</h1>
  <h2>Revenue Metrics</h2>
    <h3>Monthly Revenue</h3>
    <h3>Quarterly Revenue</h3>
  <h2>Customer Metrics</h2>
    <h3>New Customers</h3>
```

#### 1.4 Distinguishable: Easy to see and hear
- [ ] Color contrast ratio ≥4.5:1 for normal text
- [ ] Color contrast ratio ≥3:1 for large text (18pt+ or 14pt+ bold)
- [ ] Color contrast ratio ≥3:1 for UI components and graphical objects
- [ ] Information not conveyed by color alone
- [ ] Text can be resized 200% without loss of functionality
- [ ] Images of text avoided (use actual text)

**Color Contrast Examples:**
```
✓ PASS: #000000 on #FFFFFF (21:1)
✓ PASS: #FFFFFF on #0066CC (4.5:1)
✓ PASS: #595959 on #FFFFFF (7:1)
✗ FAIL: #777777 on #FFFFFF (4.3:1) - too low for normal text
✗ FAIL: #00FF00 on #FFFFFF (1.4:1) - way too low
```

**Color Independence:**
```
❌ Bad: Red/Green status with no other indicator
✓ Good: Red/Green status + Icons (✓/✗) + Text labels

❌ Bad: Color-coded categories only
✓ Good: Color + patterns/textures + direct labels
```

### Operable: UI components and navigation must be operable

#### 2.1 Keyboard Accessible
- [ ] All functionality available via keyboard
- [ ] No keyboard traps (can navigate away from all elements)
- [ ] Logical tab order follows visual flow
- [ ] Skip links to bypass repetitive content
- [ ] Focus indicator clearly visible (3:1 contrast ratio)

**Tab Order Example:**
```
Tab Order:
1. Skip to main content
2. Dashboard title
3. Date range filter
4. Region filter
5. Product filter
6. Apply filters button
7. First KPI card
8. Second KPI card
9. Chart 1
10. Chart 2
...
```

**Keyboard Shortcuts:**
```
Tab:           Move to next element
Shift+Tab:     Move to previous element
Enter/Space:   Activate button/link
Arrow keys:    Navigate within component (dropdown, chart)
Escape:        Close modal/dropdown
```

#### 2.2 Enough Time
- [ ] No time limits (or can be extended/disabled)
- [ ] Auto-refresh can be paused/stopped/adjusted
- [ ] No content that flashes more than 3 times per second

**Auto-Refresh Control:**
```html
<div class="auto-refresh-control">
  <label>
    <input type="checkbox" checked> Auto-refresh every
  </label>
  <select>
    <option value="30">30 seconds</option>
    <option value="60" selected>1 minute</option>
    <option value="300">5 minutes</option>
  </select>
  <button>Pause</button>
</div>
```

#### 2.3 Seizures and Physical Reactions
- [ ] No flashing content (or <3 flashes per second)
- [ ] Animations can be disabled
- [ ] Reduced motion option available

**CSS for Reduced Motion:**
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

#### 2.4 Navigable: Help users navigate and find content
- [ ] Page has meaningful title
- [ ] Focus order is logical
- [ ] Link purpose clear from link text
- [ ] Multiple navigation methods (menu, search, breadcrumbs)
- [ ] Headings and labels are descriptive
- [ ] Focus is visible

**Breadcrumbs Example:**
```html
<nav aria-label="Breadcrumb">
  <ol>
    <li><a href="/">Home</a></li>
    <li><a href="/dashboards">Dashboards</a></li>
    <li aria-current="page">Revenue Dashboard</li>
  </ol>
</nav>
```

#### 2.5 Input Modalities
- [ ] Touch targets ≥44×44 pixels
- [ ] All functionality available without path-based gestures
- [ ] Label text included in accessible name
- [ ] Motion actuation can be disabled

### Understandable: Information and operation must be understandable

#### 3.1 Readable
- [ ] Page language identified (`<html lang="en">`)
- [ ] Language changes marked (`<span lang="es">`)
- [ ] Abbreviations explained on first use or via title attribute

**Example:**
```html
<html lang="en">
  <body>
    <p>
      <abbr title="Key Performance Indicator">KPI</abbr> targets met
    </p>
  </body>
</html>
```

#### 3.2 Predictable
- [ ] Navigation is consistent across dashboards
- [ ] Components behave consistently
- [ ] No unexpected context changes on focus
- [ ] No unexpected context changes on input

**Consistent Navigation:**
```
All dashboards have same:
- Header layout
- Filter placement
- Navigation menu location
- Chart interaction patterns
```

#### 3.3 Input Assistance
- [ ] Form errors are identified and described
- [ ] Labels or instructions provided for inputs
- [ ] Error prevention for irreversible actions
- [ ] Suggestions for fixing errors

**Example:**
```html
<label for="date-range">Date Range *</label>
<input
  type="text"
  id="date-range"
  aria-required="true"
  aria-describedby="date-help date-error"
>
<div id="date-help">Format: MM/DD/YYYY - MM/DD/YYYY</div>
<div id="date-error" class="error" role="alert">
  End date must be after start date
</div>
```

### Robust: Content must be robust enough for assistive technologies

#### 4.1 Compatible
- [ ] Valid HTML (no duplicate IDs, proper nesting)
- [ ] Proper ARIA roles and attributes
- [ ] Status messages identified (`role="status"` or `role="alert"`)

**ARIA Roles for Dashboard Elements:**
```html
<!-- Live region for updating KPI -->
<div role="status" aria-live="polite" aria-atomic="true">
  Revenue: $1.2M (+15%)
</div>

<!-- Alert for critical threshold -->
<div role="alert" aria-live="assertive">
  ⚠️ Error rate exceeded threshold!
</div>

<!-- Tab interface -->
<div role="tablist" aria-label="Dashboard sections">
  <button role="tab" aria-selected="true" aria-controls="panel-1">
    Revenue
  </button>
  <button role="tab" aria-selected="false" aria-controls="panel-2">
    Customers
  </button>
</div>
<div role="tabpanel" id="panel-1">...</div>
```

---

## Dashboard-Specific Accessibility

### Chart Accessibility

#### Text Alternative Strategy
**Simple Chart:**
```html
<div role="img" aria-label="Bar chart: Revenue increased from $1.0M in Q1 to $1.5M in Q4">
  [SVG Chart]
</div>
```

**Complex Chart with Data Table:**
```html
<figure>
  <div class="chart" aria-describedby="chart-desc">
    [Interactive Chart]
  </div>
  <figcaption id="chart-desc">
    Revenue by quarter. Full data available in table below.
  </figcaption>
</figure>

<details>
  <summary>View data table</summary>
  <table>
    <caption>Quarterly Revenue</caption>
    <thead>
      <tr>
        <th scope="col">Quarter</th>
        <th scope="col">Revenue</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th scope="row">Q1 2024</th>
        <td>$1.0M</td>
      </tr>
      <!-- etc -->
    </tbody>
  </table>
</details>
```

#### Interactive Charts
- [ ] Charts are keyboard navigable
- [ ] Data points are focusable
- [ ] Tooltips/details accessible without mouse
- [ ] Zoom and pan available via keyboard

**Keyboard Navigation for Chart:**
```
Tab:       Focus on chart
Arrow keys: Move between data points
Enter:     Show detail tooltip
+/-:       Zoom in/out
Home/End:  Jump to first/last data point
```

### Filter Accessibility

**Accessible Filter Panel:**
```html
<form role="search" aria-label="Dashboard filters">
  <fieldset>
    <legend>Date Range</legend>
    <label for="start-date">Start Date</label>
    <input type="date" id="start-date" required>

    <label for="end-date">End Date</label>
    <input type="date" id="end-date" required>
  </fieldset>

  <fieldset>
    <legend>Region</legend>
    <label for="region">Select Region</label>
    <select id="region" multiple aria-describedby="region-help">
      <option value="north">North</option>
      <option value="south">South</option>
      <option value="east">East</option>
      <option value="west">West</option>
    </select>
    <div id="region-help">Hold Ctrl/Cmd to select multiple</div>
  </fieldset>

  <button type="submit">Apply Filters</button>
  <button type="reset">Clear Filters</button>
</form>

<!-- Announce filter results -->
<div role="status" aria-live="polite">
  Showing 234 results
</div>
```

### KPI Card Accessibility

**Accessible KPI Display:**
```html
<article class="kpi-card" aria-labelledby="kpi-revenue-title">
  <h3 id="kpi-revenue-title">Monthly Revenue</h3>

  <div class="kpi-value">
    <span class="amount">$1.2M</span>
    <span class="change positive" aria-label="increased by 15%">
      <span aria-hidden="true">▲</span> 15%
    </span>
  </div>

  <div class="kpi-context">
    Target: $1.0M
    <span class="status" role="img" aria-label="Target exceeded">✓</span>
  </div>

  <!-- Sparkline with text alternative -->
  <div class="sparkline" role="img" aria-label="12-month trend showing steady growth from $800K to $1.2M">
    <svg><!-- sparkline visualization --></svg>
  </div>
</article>
```

### Data Table Accessibility

**Accessible Dashboard Table:**
```html
<table>
  <caption>
    Top 10 Products by Revenue
    <button aria-label="Download table as CSV">⬇ CSV</button>
  </caption>

  <thead>
    <tr>
      <th scope="col">
        <button aria-label="Sort by product name">
          Product Name <span aria-hidden="true">↕</span>
        </button>
      </th>
      <th scope="col" class="numeric">
        <button aria-label="Sort by revenue">
          Revenue <span aria-hidden="true">↕</span>
        </button>
      </th>
      <th scope="col" class="numeric">Change</th>
    </tr>
  </thead>

  <tbody>
    <tr>
      <th scope="row">Product A</th>
      <td class="numeric">$1,234,567</td>
      <td class="numeric positive">
        <span class="sr-only">Increased by</span>
        +15%
      </td>
    </tr>
    <!-- etc -->
  </tbody>

  <tfoot>
    <tr>
      <th scope="row">Total</th>
      <td class="numeric">$5,678,901</td>
      <td></td>
    </tr>
  </tfoot>
</table>

<style>
  /* Screen reader only class */
  .sr-only {
    position: absolute;
    left: -10000px;
    width: 1px;
    height: 1px;
    overflow: hidden;
  }

  /* Right-align numeric columns */
  .numeric {
    text-align: right;
    font-variant-numeric: tabular-nums;
  }
</style>
```

---

## Color Blindness Considerations

### Types of Color Blindness

**Deuteranopia/Protanopia (Red-Green, ~8% of men):**
- Cannot distinguish red from green
- Reds appear dark, greens appear beige

**Tritanopia (Blue-Yellow, rare):**
- Cannot distinguish blue from yellow

**Achromatopsia (Total, very rare):**
- See only grayscale

### Accessible Color Strategies

#### 1. Use Color-Blind Safe Palettes
```
✓ Blue + Orange
✓ Blue + Yellow
✓ Purple + Orange
✓ Cyan + Magenta

✗ Red + Green
✗ Blue + Purple (similar)
✗ Green + Brown (similar)
```

#### 2. Never Use Color Alone
Always combine color with:
- **Shape**: ▲ positive, ▼ negative
- **Pattern**: Solid, striped, dotted
- **Text**: "Above target", "Below target"
- **Icons**: ✓, ✗, ⚠️

**Example:**
```html
<!-- Bad: Color only -->
<span class="green">Above target</span>
<span class="red">Below target</span>

<!-- Good: Color + icon + text -->
<span class="positive">
  <icon>✓</icon> Above target
</span>
<span class="negative">
  <icon>✗</icon> Below target
</span>
```

#### 3. Test with Simulators
**Tools:**
- Color Oracle (free, desktop)
- Coblis (Color Blindness Simulator)
- Chrome DevTools (Vision Deficiencies)
- Stark (Figma/Sketch plugin)

**Test Process:**
1. View dashboard in simulator
2. Verify all information still comprehensible
3. Check charts are distinguishable
4. Ensure status/alerts are clear

---

## Screen Reader Considerations

### Live Regions for Updates

**Auto-updating Dashboard:**
```html
<!-- KPI that updates every minute -->
<div
  role="status"
  aria-live="polite"
  aria-atomic="true"
  id="revenue-kpi"
>
  Revenue: $1,234,567 (as of 2:45 PM)
</div>

<!-- Critical alert -->
<div
  role="alert"
  aria-live="assertive"
>
  System error rate exceeded 5%
</div>
```

**aria-live values:**
- `off`: No announcements (default)
- `polite`: Announce when user is idle
- `assertive`: Announce immediately (use sparingly)

**aria-atomic:**
- `true`: Read entire region
- `false`: Read only what changed

### Hide Decorative Elements

```html
<!-- Decorative icon, hidden from screen readers -->
<span aria-hidden="true">📊</span>

<!-- Meaningful icon with text alternative -->
<span role="img" aria-label="Chart">📊</span>

<!-- Icon with redundant text -->
<button>
  <span aria-hidden="true">↻</span>
  Refresh
</button>
```

### Provide Alternative Access to Visual Information

```html
<!-- Chart with both visual and tabular access -->
<div class="chart-container">
  <div id="chart" role="img" aria-describedby="chart-summary">
    [Visual chart]
  </div>

  <div id="chart-summary" class="sr-only">
    Revenue trend from Jan to Dec 2024 showing 15% growth.
    Started at $1.0M and ended at $1.15M with steady monthly increases.
  </div>

  <button
    aria-expanded="false"
    aria-controls="data-table"
  >
    Show data table
  </button>

  <div id="data-table" hidden>
    <table>
      <!-- Full data in accessible format -->
    </table>
  </div>
</div>
```

---

## Testing Checklist

### Automated Testing
- [ ] aXe DevTools (browser extension)
- [ ] WAVE (Web Accessibility Evaluation Tool)
- [ ] Lighthouse accessibility audit
- [ ] Pa11y (command-line tool)
- [ ] Platform-specific validators (Tableau, Power BI)

### Manual Testing

**Keyboard Navigation:**
- [ ] Unplug mouse
- [ ] Navigate entire dashboard using only keyboard
- [ ] All interactive elements accessible
- [ ] Focus visible at all times
- [ ] No keyboard traps

**Screen Reader Testing:**
- [ ] NVDA (Windows, free)
- [ ] JAWS (Windows, commercial)
- [ ] VoiceOver (Mac/iOS, built-in)
- [ ] TalkBack (Android, built-in)
- [ ] Read entire dashboard aloud
- [ ] All information available
- [ ] No nonsensical readings
- [ ] Proper reading order

**Color Contrast:**
- [ ] Use contrast checker tool
- [ ] All text meets 4.5:1 ratio
- [ ] Large text meets 3:1 ratio
- [ ] UI components meet 3:1 ratio

**Color Blindness:**
- [ ] Test with color blindness simulator
- [ ] All information distinguishable
- [ ] Status indicators have text/icons

**Mobile/Touch:**
- [ ] All touch targets ≥44×44px
- [ ] Works without precise gestures
- [ ] Pinch-to-zoom not disabled

**Cognitive:**
- [ ] Clear, simple language
- [ ] Consistent navigation
- [ ] No flashing content
- [ ] Sufficient time to interact

---

## Quick Reference: Common ARIA Roles & Attributes

### Roles
```
role="button"       - Clickable element
role="img"          - Image (including charts)
role="status"       - Status update (polite)
role="alert"        - Critical alert (assertive)
role="region"       - Significant section
role="search"       - Search form
role="navigation"   - Navigation menu
role="tablist"      - Tab container
role="tab"          - Individual tab
role="tabpanel"     - Tab content
```

### Attributes
```
aria-label          - Accessible name
aria-labelledby     - ID of labeling element
aria-describedby    - ID of description element
aria-live           - off | polite | assertive
aria-atomic         - true | false (read whole region or just changes)
aria-hidden         - true (hide from assistive tech)
aria-expanded       - true | false (for collapsed content)
aria-controls       - ID of controlled element
aria-current        - page | step | location (current item in set)
aria-required       - true (required field)
aria-invalid        - true | false (field validation)
```

---

## Platform-Specific Accessibility

### Tableau
- Use "Add Alt Text" for sheets
- Enable keyboard navigation
- Test with screen reader mode
- Use accessible color palettes
- Provide downloadable data

### Power BI
- Use built-in Accessibility Checker
- Enable keyboard shortcuts
- Add alt text to visuals
- Use high-contrast themes
- Test mobile accessibility

### Looker
- Use ARIA labels in LookML
- Enable keyboard navigation
- Provide data table alternatives
- Test with screen readers
- Use accessible color schemes

---

## Resources

**Guidelines:**
- WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/
- Section 508: https://www.section508.gov/
- ARIA Authoring Practices: https://www.w3.org/WAI/ARIA/apg/

**Testing Tools:**
- aXe DevTools: https://www.deque.com/axe/
- WAVE: https://wave.webaim.org/
- Color Contrast Checker: https://webaim.org/resources/contrastchecker/
- Color Oracle: https://colororacle.org/

**Screen Readers:**
- NVDA (free): https://www.nvaccess.org/
- VoiceOver: Built into macOS/iOS
- TalkBack: Built into Android

**Learning:**
- WebAIM: https://webaim.org/
- A11y Project: https://www.a11yproject.com/
- Deque University: https://dequeuniversity.com/

---

*Remember: Accessibility is not a checklist—it's an ongoing commitment to inclusive design.*

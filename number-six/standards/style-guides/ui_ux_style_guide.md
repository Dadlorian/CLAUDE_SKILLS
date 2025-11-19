# UI/UX Style Guide
## Elite Professional Standards for User Experience Design

### Philosophy
This guide synthesizes best practices from:
- **Apple Human Interface Guidelines** - Industry-leading UX standards
- **Google Material Design** - Research-backed design system
- **Nielsen Norman Group** - Evidence-based UX research
- **WCAG 2.2 Level AAA** - Accessibility excellence
- **Design Systems from**: Airbnb, Shopify, IBM Carbon, Atlassian

---

## Core Principles

### 1. User-Centered Design
**Standard**: Every design decision must be validated with user research
- Conduct usability testing with minimum 5 users per iteration
- Use both qualitative (interviews) and quantitative (analytics) data
- Reference: "Don't Make Me Think" by Steve Krug

### 2. Accessibility First (WCAG 2.2 AAA)
**Requirements**:
- Color contrast ratio ≥ 7:1 for normal text, ≥ 4.5:1 for large text
- All interactive elements keyboard navigable
- Screen reader compatible (ARIA labels, semantic HTML)
- Cognitive accessibility: Simple language, consistent patterns
- Reference: WebAIM, a11y Project

### 3. Visual Hierarchy
**Standards from top design systems**:
- Typography scale: 1.250 (Major Third) or 1.333 (Perfect Fourth)
- Spacing scale: 4px base unit (4, 8, 12, 16, 24, 32, 48, 64, 96)
- Z-index layers: content(1), dropdown(100), sticky(200), modal(300), tooltip(400)
- Reference: Refactoring UI by Adam Wathan & Steve Schoger

### 4. Interaction Design Patterns
**Use proven patterns from**:
- Luke Wroblewski's "Mobile First" principles
- Jef Raskin's "The Humane Interface"
- Apple's Direct Manipulation guidelines

---

## Design Standards

### Typography
```
Font Family:
- Primary: System font stack (-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell)
- Monospace: 'JetBrains Mono', 'Fira Code', Consolas, Monaco

Scale (1.250 - Major Third):
- Display: 48px / 3rem
- H1: 39px / 2.441rem
- H2: 31px / 1.953rem
- H3: 25px / 1.563rem
- H4: 20px / 1.25rem
- Body: 16px / 1rem
- Small: 13px / 0.8rem
- Caption: 10px / 0.64rem

Line Height:
- Headings: 1.2
- Body: 1.5
- Caption: 1.4

Letter Spacing:
- Headings: -0.02em
- Body: 0
- Uppercase: 0.05em
```

### Color System
**Follow Material Design 3 / Tailwind CSS approach**:
```
Primary Colors (with WCAG AAA compliant variations):
- Primary: 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950
- Use 600-900 for dark mode
- Use 50-500 for light mode

Semantic Colors:
- Success: Green 600 (#059669)
- Warning: Amber 600 (#D97706)
- Error: Red 600 (#DC2626)
- Info: Blue 600 (#2563EB)

Ensure all combinations pass contrast requirements
```

### Spacing & Layout
**8-point grid system (industry standard)**:
```
Base unit: 8px

Component padding:
- Compact: 8px (1 unit)
- Default: 16px (2 units)
- Comfortable: 24px (3 units)

Section spacing:
- Tight: 16px
- Normal: 32px
- Relaxed: 48px
- Loose: 64px

Container widths (responsive):
- sm: 640px
- md: 768px
- lg: 1024px
- xl: 1280px
- 2xl: 1536px
```

### Animation & Motion
**Follow Material Design Motion**:
```
Duration:
- Micro-interactions: 100-150ms
- Small elements: 200-300ms
- Large elements: 300-400ms
- Page transitions: 400-500ms

Easing:
- Standard: cubic-bezier(0.4, 0.0, 0.2, 1)
- Decelerate: cubic-bezier(0.0, 0.0, 0.2, 1) - entering
- Accelerate: cubic-bezier(0.4, 0.0, 1, 1) - exiting
- Sharp: cubic-bezier(0.4, 0.0, 0.6, 1) - temporarily leaving

Principles:
- Purposeful: Every animation should have a reason
- Performant: Use transform and opacity only (GPU accelerated)
- Accessible: Respect prefers-reduced-motion
```

---

## Component Standards

### Buttons
**Following Apple HIG and Material Design**:
```
Hierarchy:
1. Primary: High contrast, main action
2. Secondary: Medium contrast, alternative action
3. Tertiary: Low contrast, de-emphasized

Sizes:
- Small: 32px height, 12px padding
- Medium: 40px height, 16px padding
- Large: 48px height, 20px padding

States:
- Default
- Hover: 10% darker/lighter
- Active: 20% darker/lighter
- Disabled: 50% opacity, not interactive
- Focus: 2px outline, 2px offset

Touch targets: Minimum 44x44px (Apple) / 48x48px (Material)
```

### Forms
**Nielsen Norman Group best practices**:
```
Input Fields:
- Label above input (not placeholder as label)
- Helper text below input
- Error message replaces helper text
- Min height: 44px
- Clear visual states: default, focus, error, disabled

Validation:
- Inline validation after user completes field
- Positive validation (checkmark) for success
- Error messages: Specific, actionable, polite

Form Layout:
- Single column (faster completion)
- Group related fields
- Optional fields marked clearly
- Progress indicator for multi-step forms
```

### Data Tables
**Enterprise standards from Ant Design, Material UI**:
```
Structure:
- Fixed header on scroll
- Sortable columns (visual indicator)
- Filterable when >20 rows
- Pagination when >25 rows
- Row selection with checkbox
- Responsive: Card layout on mobile

Row heights:
- Compact: 32px
- Default: 48px
- Comfortable: 64px

Column widths:
- Checkbox: 48px
- Actions: 80-120px
- Content: Flexible, min 120px
```

---

## Responsive Design

### Breakpoints
```
Mobile: 320px - 767px
Tablet: 768px - 1023px
Desktop: 1024px - 1439px
Large Desktop: 1440px+

Mobile-first approach (min-width queries)
```

### Touch Considerations
- Minimum touch target: 44x44px (iOS) / 48x48px (Android)
- Spacing between touch targets: 8px minimum
- Swipe gestures for common actions
- Pull-to-refresh pattern for feeds

---

## Performance Standards

### Metrics (Core Web Vitals)
```
LCP (Largest Contentful Paint): < 2.5s
FID (First Input Delay): < 100ms
CLS (Cumulative Layout Shift): < 0.1

Additional:
- Time to Interactive: < 3.8s
- Speed Index: < 3.4s
```

### Optimization Techniques
- Lazy load images below fold
- Use WebP/AVIF with fallbacks
- Implement skeleton screens
- Debounce search inputs (300ms)
- Virtualize long lists (react-window, tanstack-virtual)

---

## Dark Mode

**System preference detection**:
```css
@media (prefers-color-scheme: dark) {
  /* Dark mode styles */
}
```

**Standards**:
- Use true black (#000000) sparingly - #121212 for backgrounds
- Reduce saturation of colors by 20-30%
- Maintain WCAG AAA contrast ratios
- Reference: Material Design Dark Theme

---

## Microcopy & Content

**Principles from Mailchimp Content Style Guide**:
- Conversational, not formal
- Active voice, not passive
- Short sentences (< 20 words)
- Specific, not vague
- Error messages: What happened + How to fix

**Button text**:
- Action verbs: "Save changes", "Send message"
- Not: "OK", "Submit", "Click here"

---

## Testing Standards

### Required Tests
1. **Usability Testing**: 5 users minimum per iteration
2. **A/B Testing**: Statistical significance (p < 0.05)
3. **Accessibility Audit**: WAVE, axe DevTools, screen reader
4. **Cross-browser**: Chrome, Safari, Firefox, Edge
5. **Responsive Testing**: Real devices, not just DevTools

### Tools
- Figma for design & prototyping
- Optimal Workshop for card sorting
- Hotjar for heatmaps
- Google Analytics 4 for behavior
- Lighthouse for performance

---

## Design Tokens

**Use JSON for consistency across platforms**:
```json
{
  "color": {
    "primary": {
      "500": "#3B82F6",
      "600": "#2563EB"
    }
  },
  "spacing": {
    "2": "8px",
    "4": "16px"
  },
  "font": {
    "size": {
      "base": "16px",
      "lg": "20px"
    }
  }
}
```

Tools: Style Dictionary, Theo

---

## References

### Must-Read Books
1. "Don't Make Me Think" - Steve Krug
2. "The Design of Everyday Things" - Don Norman
3. "Refactoring UI" - Adam Wathan & Steve Schoger
4. "Atomic Design" - Brad Frost

### Essential Resources
- Nielsen Norman Group (nngroup.com)
- Baymard Institute (UX research)
- Smashing Magazine
- A List Apart

### Design Systems to Study
- Material Design (Google)
- Human Interface Guidelines (Apple)
- Carbon Design System (IBM)
- Polaris (Shopify)
- Ant Design (Alibaba)

---

**Version**: 1.0
**Compliance**: WCAG 2.2 AAA, Section 508
**Last Updated**: 2025-11-19

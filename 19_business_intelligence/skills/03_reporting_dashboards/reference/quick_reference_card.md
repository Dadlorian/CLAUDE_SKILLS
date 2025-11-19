# Dashboard Design Quick Reference Card

## The Golden Rules (Few, Tufte, Knaflic)

### 1. Start with Questions, Not Data
❓ **What decision does this dashboard support?**
❓ **Who is the audience?**
❓ **What action should they take?**

### 2. Maximize Data-Ink Ratio (Tufte)
✓ Keep: Data and essential labels
✗ Remove: Decoration, 3D, shadows, gradients, heavy grids

### 3. Use Color Sparingly (Few)
- **95% Grayscale**: Most of dashboard
- **5% Color**: Emphasis, alerts, selected items
- **Always**: Color blind safe + alternative encoding

### 4. Tell a Story (Knaflic)
1. **Context**: Where we are
2. **Insight**: What's happening
3. **Action**: What to do

### 5. Less is More
- **Executive**: 5-7 KPIs
- **Operational**: 10-15 KPIs
- **Analytical**: 15-20 KPIs max

---

## Chart Selection Cheat Sheet

| Show This | Use This | Not This |
|-----------|----------|----------|
| Comparison | Horizontal bar | Pie chart |
| Trend | Line chart | Bar (100+ points) |
| Part-to-whole | Stacked bar | Pie (>2 slices) |
| Distribution | Histogram | Pie chart |
| vs Target | Bullet chart | Gauge |
| 2 time points | Slope chart | Bar |
| Correlation | Scatter plot | Line |

---

## Color Palette

### Safe Defaults
**Categorical**: Blue, Orange, Green, Purple, Brown
**Sequential**: Light → Dark Blue
**Diverging**: Red ← Gray → Blue

### Never Use
❌ Red/Green only (color blind)
❌ Rainbow for sequential data
❌ >7 colors on one chart

---

## Layout Priority

```
┌─────────────────────────┐
│ 🔥 Most Important       │ ← Top-left
├──────────┬──────────────┤
│ 🔥       │  🔥         │ ← Top row
├──────────┴──────────────┤
│ 🌡️ Supporting Charts    │ ← Middle
├───────────────────────┴─┤
│ ❄️ Details (optional)   │ ← Bottom
└─────────────────────────┘
```

---

## Typography Hierarchy

```
Page Title:    32-48px, Bold
Section:       24-32px, Semi-Bold
KPI Value:     32-64px, Bold
KPI Label:     14-18px, Regular
Body:          14-16px, Regular
Metadata:      10-12px, Light
```

---

## Accessibility Minimums

- **Text Contrast**: 4.5:1 (normal), 3:1 (large)
- **Touch Targets**: 44×44px minimum
- **Font Size**: 14px minimum
- **Alt Text**: Required for all charts
- **Keyboard**: Full navigation support

---

## Performance Targets

- **Load Time**: <3 seconds
- **Filter Update**: <1 second
- **Chart Render**: <500ms
- **Visuals per Page**: 8-15 max

---

## Common Mistakes to Avoid

❌ No clear purpose or audience
❌ Too much information (>20 charts)
❌ Misleading visualizations (truncated axis)
❌ Christmas tree (too many colors)
❌ Poor mobile experience
❌ No context for metrics
❌ Slow performance (>10s load)

---

## Pre-Launch Checklist

- [ ] Purpose & audience defined
- [ ] 5-15 KPIs (not 50)
- [ ] Right chart types
- [ ] Grayscale test passed
- [ ] Color blind tested
- [ ] Mobile-friendly
- [ ] Load time <5s
- [ ] Context for all metrics
- [ ] Keyboard navigable
- [ ] Data freshness shown

---

## KPI Display Template

```
Revenue
$1,234,567
+15% vs $1.0M target ▲
Last Month: +12%
[━━━━━━━━━] 12-mo trend

Components:
1. Label (clear, concise)
2. Value (large, bold)
3. Context (target, previous)
4. Trend (sparkline or line)
5. Timestamp (when data from)
```

---

## Filter Best Practices

✓ Visible and obvious
✓ Smart defaults (Last 30 days)
✓ Clear active filter state
✓ Easy to clear
✓ Single "Apply" button (not auto)

---

## Mobile Considerations

- **Prioritize**: Most important metrics first
- **Simplify**: Fewer charts, larger text
- **Stack**: Single column layout
- **Touch**: 44px minimum targets
- **Performance**: <3s on mobile network

---

## Storytelling Structure

1. **Headline**: Big number, clear statement
2. **Context**: What it means, comparison
3. **Insight**: Why it's happening
4. **Visualization**: Supporting evidence
5. **Action**: What to do next

---

## Platform Quick Tips

### Tableau
- Use extracts (not live)
- Context filters first
- Limit quick filters
- Performance recording

### Power BI
- Import mode preferred
- Use variables in DAX
- Reduce cardinality
- Performance analyzer

### Looker
- Use PDTs
- Datagroups for cache
- Aggregate awareness
- Limit row results

---

## When in Doubt

1. **Simplify**: Remove, don't add
2. **Ask**: "Does this help make a decision?"
3. **Test**: Show to unfamiliar user
4. **Iterate**: Based on feedback

---

## Resources

📖 **Books**:
- Stephen Few: "Information Dashboard Design"
- Edward Tufte: "The Visual Display of Quantitative Information"
- Cole Nussbaumer Knaflic: "Storytelling with Data"

🔧 **Tools**:
- Color Contrast Checker (WebAIM)
- Color Blindness Simulator (Color Oracle)
- Performance Testing (Lighthouse)

📊 **Examples**:
- FiveThirtyEight (data journalism)
- The Economist (clear visuals)
- Tableau Public (gallery)

# Color Palettes for Dashboards

## Principles of Dashboard Color Use

### Stephen Few's Color Guidelines
1. **Use color sparingly**: Reserve color for highlighting important information
2. **Use color consistently**: Same meaning across all dashboards
3. **Design for color blindness**: 8% of men have color vision deficiency
4. **Avoid bright, saturated colors**: Except for alerts
5. **Limit palette**: 6-7 colors maximum per dashboard

### Tufte's Approach
- **Minimal color**: Most data in gray/black
- **Color for emphasis**: Highlight only the exceptional
- **Subtle gradients**: If needed for categories
- **Avoid chartjunk**: No decorative color

### Knaflic's Color Strategy
- **Grayscale first**: Design in grayscale, add color purposefully
- **Pre-attentive attributes**: Use color to direct attention
- **Brand alignment**: Incorporate brand colors thoughtfully
- **Semantic color**: Red/green for negative/positive (with texture backup)

## Color Palette Types

### 1. Sequential Palettes
**Use For:** Quantitative data with meaningful order (low to high)

**Single Hue Sequential**
```
Light Blue to Dark Blue:
#EFF3FF → #C6DBEF → #9ECAE1 → #6BAED6 → #4292C6 → #2171B5 → #084594

Light Gray to Black:
#F7F7F7 → #D9D9D9 → #BDBDBD → #969696 → #737373 → #525252 → #252525

Light Green to Dark Green:
#EDF8E9 → #C7E9C0 → #A1D99B → #74C476 → #41AB5D → #238B45 → #005A32
```

**Multi-Hue Sequential (Use Carefully)**
```
Yellow-Orange-Red (Heat):
#FFFFB2 → #FECC5C → #FD8D3C → #F03B20 → #BD0026

Yellow-Green-Blue (Temperature):
#FFFFCC → #C7E9B4 → #7FCDBB → #41B6C4 → #2C7FB8 → #253494
```

### 2. Diverging Palettes
**Use For:** Data with meaningful midpoint (above/below target, positive/negative)

**Red-White-Blue (Recommended)**
```
#CA0020 → #F4A582 → #FFFFFF → #92C5DE → #0571B0
```

**Orange-White-Purple**
```
#E66101 → #FDB863 → #F7F7F7 → #B2ABD2 → #5E3C99
```

**Red-Gray-Green (Use with caution - color blind issues)**
```
#D7191C → #FDAE61 → #FFFFBF → #A6D96A → #1A9641
```

**Better Alternative (Color-blind safe)**
```
Orange-Gray-Blue:
#D95F0E → #FEC44F → #F7F7F7 → #91BFDB → #4575B4
```

### 3. Qualitative/Categorical Palettes
**Use For:** Distinct categories with no inherent order

**Few's Recommended Palette (Color-blind safe)**
```
6 Colors:
#4D4D4D (Gray)
#5DA5DA (Blue)
#FAA43A (Orange)
#60BD68 (Green)
#F17CB0 (Pink)
#B2912F (Brown)
#B276B2 (Purple)
#DECF3F (Yellow)
#F15854 (Red)
```

**Tableau 10 (Industry Standard)**
```
#1F77B4 (Blue)
#FF7F0E (Orange)
#2CA02C (Green)
#D62728 (Red)
#9467BD (Purple)
#8C564B (Brown)
#E377C2 (Pink)
#7F7F7F (Gray)
#BCBD22 (Olive)
#17BECF (Cyan)
```

**IBM Design Language**
```
#648FFF (Blue)
#785EF0 (Purple)
#DC267F (Magenta)
#FE6100 (Orange)
#FFB000 (Yellow)
```

**Colorblind-Safe Qualitative (Paul Tol)**
```
#332288 (Indigo)
#88CCEE (Cyan)
#44AA99 (Teal)
#117733 (Green)
#999933 (Olive)
#DDCC77 (Sand)
#CC6677 (Rose)
#882255 (Wine)
#AA4499 (Purple)
```

## Semantic Color Standards

### Alert/Status Colors

**Traffic Light Pattern (Avoid if possible)**
```
Problems:
- 8% of men can't distinguish red/green
- Cultural differences in interpretation
- Often used incorrectly
```

**Better Alternative: Gray-Orange-Blue**
```
Below Target: #D95F0E (Orange)
On Target: #BDBDBD (Gray) or #4575B4 (Blue)
Above Target: #4575B4 (Blue) or #238B45 (Green)
```

**Status Colors (Accessible)**
```
Critical: #DC143C (Crimson) + ⚠️ icon
Warning: #FF8C00 (Dark Orange) + ⚡ icon
OK: #2E8B57 (Sea Green) + ✓ icon
Info: #4682B4 (Steel Blue) + ℹ️ icon
Neutral: #696969 (Dim Gray)
```

### Financial Data Colors
```
Positive (Profit/Gain): #006400 (Dark Green)
Negative (Loss): #8B0000 (Dark Red)
Neutral/Forecast: #4B4B4B (Dark Gray)
```

**Accessible Alternative:**
```
Positive: #0571B0 (Blue) with ▲
Negative: #CA0020 (Red) with ▼
Neutral: #666666 (Gray) with ●
```

## Dashboard-Specific Palettes

### Executive Dashboard
**Philosophy:** Minimal color, maximum clarity
```
Primary Data: #2C3E50 (Dark Blue-Gray)
Highlight: #E74C3C (Red) - for exceptions only
Secondary: #95A5A6 (Gray)
Background: #FFFFFF (White)
Text: #2C3E50 (Dark Blue-Gray)
```

### Operational Dashboard
**Philosophy:** Status-driven, quick recognition
```
Normal: #7F8C8D (Gray)
Warning: #F39C12 (Orange)
Critical: #E74C3C (Red)
Good: #27AE60 (Green)
Background: #ECF0F1 (Light Gray)
```

### Analytical Dashboard
**Philosophy:** Support exploration, minimize distraction
```
Primary: #3498DB (Blue)
Secondary: #95A5A6 (Gray)
Tertiary: #E67E22 (Orange)
Quaternary: #9B59B6 (Purple)
Background: #FFFFFF (White)
Gridlines: #E0E0E0 (Very Light Gray)
```

## Color Accessibility

### WCAG 2.1 AA Contrast Ratios
- **Normal text**: Minimum 4.5:1
- **Large text** (18pt+ or 14pt+ bold): Minimum 3:1
- **UI components**: Minimum 3:1

### Accessible Combinations
```
✓ #FFFFFF on #0066CC (4.5:1) - White on Blue
✓ #000000 on #FFFF00 (19.6:1) - Black on Yellow
✓ #FFFFFF on #CC0000 (5.3:1) - White on Red
✗ #00FF00 on #FFFFFF (1.4:1) - Green on White - FAIL
✗ #FFFF00 on #FFFFFF (1.1:1) - Yellow on White - FAIL
```

### Color Blindness Considerations

**Deuteranopia (Red-Green) - Most Common**
- Avoid: Red/Green combinations
- Use: Blue/Orange or Blue/Yellow
- Add: Texture, shape, or pattern

**Protanopia (Red-Green)**
- Similar to Deuteranopia
- Reds appear darker
- Use same solutions

**Tritanopia (Blue-Yellow) - Rare**
- Avoid: Blue/Yellow combinations
- Use: Red/Blue or Red/Purple

**Test Tools:**
- Color Oracle (simulator)
- Coblis (Color Blindness Simulator)
- WebAIM Contrast Checker

## Implementation Guidelines

### Grayscale First Approach (Knaflic)
1. Design entire dashboard in grayscale
2. Identify what needs emphasis
3. Add color only to emphasized elements
4. Verify color adds value, not just decoration

### Color Assignment Rules
1. **Maximum 6-7 colors** per dashboard
2. **Reserve high-saturation colors** for alerts/highlights
3. **Use consistent colors** across dashboard suite
4. **Test with color-blind simulator** before deployment
5. **Provide alternative encodings** (shape, size, texture)

### Background and Gridlines
```
Background: #FFFFFF (White) or #F7F7F7 (Very Light Gray)
Gridlines: #E0E0E0 (Very Light Gray) - minimal, if at all
Text: #2C3E50 (Dark Gray/Blue-Gray)
Labels: #5A5A5A (Medium Gray)
```

### Hover and Selection States
```
Default: Base color
Hover: 20% darker than base
Selected: 40% darker + border
Inactive: 60% lighter (grayed out)
```

## Platform-Specific Palettes

### Tableau
- Use built-in "Colorblind Safe" palettes
- Customize with organization brand (sparingly)
- Avoid: "Rainbow" and "Traffic Light"

### Power BI
- Use "Accessible" theme as baseline
- Create custom theme JSON with approved colors
- Test with built-in accessibility checker

### Looker
- Define brand colors in LookML
- Use consistent color palette across models
- Leverage conditional formatting conservatively

## Quick Reference Card

### DO:
✓ Use color sparingly and purposefully
✓ Design in grayscale first, add color for emphasis
✓ Test with color-blind simulators
✓ Provide alternative encodings (shape, pattern)
✓ Use consistent colors across dashboard suite
✓ Limit to 6-7 colors maximum
✓ Use color for status, alerts, highlights

### DON'T:
✗ Use color for decoration
✗ Rely solely on red/green
✗ Use bright, saturated colors everywhere
✗ Use different colors for same meaning
✗ Use rainbow palettes for sequential data
✗ Ignore contrast ratios
✗ Use color without testing accessibility

## Color Palette JSON

See `/src/color_schemes.json` for ready-to-use color definitions in multiple formats (HEX, RGB, HSL) for all major BI platforms.

## References
- Stephen Few: "Practical Rules for Using Color in Charts"
- ColorBrewer 2.0: Evidence-based color schemes
- Viz Palette: Color-blind safe palette generator
- WebAIM: Contrast Checker

# RTL Layout Examples

This directory contains comprehensive examples for right-to-left (RTL) text rendering and layout, essential for Arabic, Hebrew, and other RTL languages.

## Overview

Right-to-left text requires special consideration in interface design, typography, and document layout. This directory demonstrates best practices for proper RTL implementation.

## Languages Included

1. **Modern Standard Arabic (ar-SA)** - Formal, widely used in technical documentation
2. **Hebrew (he-IL)** - Used in Israel
3. **Farsi/Persian (fa-IR)** - Used in Iran

## Key RTL Challenges and Solutions

### 1. Text Direction
- Text reads right-to-left
- Numbers still read left-to-right (bidi-text)
- Mixed scripts require careful handling

### 2. UI Mirroring
- Interface elements should mirror horizontally
- Buttons, icons, and controls position on opposite side
- Menu structures reverse order

### 3. Typography
- Font selection critical for character rendering
- Line height requirements different
- Punctuation placement differs

### 4. Lists and Numbering
- Numbering appears on right side
- Bullet points align to right margin
- Indentation reverses

## File Structure

```
rtl-layout-examples/
├── ar-SA/
│   ├── documentation.md
│   ├── ui-components.html
│   ├── email-template.html
│   └── pdf-layout.md
├── he-IL/
│   ├── documentation.md
│   ├── ui-components.html
│   └── email-template.html
├── fa-IR/
│   ├── documentation.md
│   └── ui-components.html
└── rtl-implementation-guide.md
```

## HTML RTL Attributes

```html
<!-- Document level -->
<html dir="rtl" lang="ar-SA">

<!-- Paragraph level -->
<p dir="rtl" lang="ar-SA">النص العربي هنا</p>

<!-- Mixed content -->
<p dir="rtl"><bdi>English text</bdi> مع نص عربي</p>
```

## CSS RTL Styling

```css
/* Flexbox RTL -->
.container {
    display: flex;
    flex-direction: row-reverse;
}

/* Grid RTL -->
.grid {
    display: grid;
    direction: rtl;
}

/* Margin/Padding RTL -->
.element {
    margin-inline-start: 1rem;  /* Right side in RTL */
    margin-inline-end: 0;        /* Left side in RTL */
}
```

## Logical Properties

Modern CSS uses logical properties that work for both LTR and RTL:

- `margin-inline-start` (replaces margin-left)
- `margin-inline-end` (replaces margin-right)
- `padding-inline-start` (replaces padding-left)
- `text-align: start` (replaces left/right)

## Testing RTL Layouts

1. **Language Testing**: View content in actual RTL language
2. **Browser Testing**: Test in Chrome, Firefox, Safari, Edge
3. **Device Testing**: Mobile devices with RTL OS language
4. **Accessibility Testing**: Screen readers and RTL support
5. **Mixed Text Testing**: English and RTL language combination

## Common RTL Issues

1. **Number Formatting**: Numbers in RTL text still go left-to-right
2. **Quotes and Brackets**: Different quote styles used in RTL languages
3. **Image Placement**: Images may need repositioning for RTL
4. **Form Labels**: Label positioning mirrors in RTL
5. **Navigation**: Navigation order may need reversal

## Fonts for RTL

Recommended fonts with full RTL support:

- **Traditional**: Arial, Times New Roman, Courier New
- **Modern Sans**: Segoe UI, Roboto, Open Sans
- **Arab-specific**: Traditional Arabic, Simplified Arabic, Cairo
- **Hebrew-specific**: David, Miriam, Arial Hebrew
- **Persian**: Farsi Font, B Yekan

## Tools and Resources

- **CSS Logical Properties**: MDN Web Docs
- **RTL Testing Tools**: Google Chrome DevTools
- **Accessibility**: WCAG Guidelines for RTL
- **Frameworks**: Bootstrap 5, Material Design RTL support

## Best Practices Summary

1. Use semantic HTML with proper `lang` attribute
2. Apply CSS logical properties instead of directional properties
3. Test in actual RTL language environments
4. Consider bidirectional text (numbers, URLs, quotes)
5. Ensure fonts support all RTL character sets
6. Test on actual devices with RTL system language
7. Validate with accessibility tools
8. Document RTL-specific requirements

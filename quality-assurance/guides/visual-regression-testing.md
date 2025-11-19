# Visual Regression Testing Guide

## Tools

**Percy** (Browserstack):
- Automated visual testing
- Cross-browser screenshots
- Visual diffs
- CI/CD integration

**Applitools** (Eyes):
- AI-powered visual testing
- Layout testing
- Responsive testing
- Accessibility checks

**BackstopJS**:
- Open-source
- Playwright/Puppeteer integration
- Reference/test comparison
- CI/CD friendly

**Playwright Visual Comparisons**:
- Built-in screenshot testing
- Pixel-perfect comparisons
- Threshold configuration

## Implementation

```typescript
// Playwright visual testing
import { test, expect } from '@playwright/test';

test('homepage visual regression', async ({ page }) => {
  await page.goto('https://example.com');
  
  // Full page screenshot
  await expect(page).toHaveScreenshot('homepage.png', {
    fullPage: true,
    threshold: 0.2 // 20% tolerance
  });
});

test('component visual regression', async ({ page }) => {
  await page.goto('https://example.com');
  
  // Specific element screenshot
  const header = page.locator('header');
  await expect(header).toHaveScreenshot('header.png');
});

test('responsive design', async ({ page }) => {
  // Desktop
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.goto('https://example.com');
  await expect(page).toHaveScreenshot('desktop.png');
  
  // Mobile
  await page.setViewportSize({ width: 375, height: 667 });
  await expect(page).toHaveScreenshot('mobile.png');
});
```

## Best Practices

### DO ✅
- Baseline screenshots in version control
- Test across viewports
- Exclude dynamic content
- Set appropriate thresholds
- Review diffs manually

### DON'T ❌
- Accept all changes blindly
- Test on unstable pages
- Include timestamps in screenshots
- Use too tight thresholds (0%)
- Skip responsive testing

## Common Issues

**Flaky Visual Tests**:
- Dynamic content (ads, dates)
- Font loading delays
- Animation timing
- Network delays

**Solutions**:
- Hide dynamic elements
- Wait for fonts to load
- Disable animations
- Wait for network idle
- Use consistent test data

# Testing Embedded Analytics Guide

## Unit Tests

### Test Token Generation

```javascript
describe('Token Generation', () => {
  it('should generate valid JWT', () => {
    const user = { id: '123', tenantId: 1 };
    const token = generateEmbedToken(user);

    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    expect(decoded.tenant_id).toBe(1);
    expect(decoded.exp).toBeGreaterThan(Date.now() / 1000);
  });

  it('should include RLS context', () => {
    const user = { tenantId: 1, department: 'sales' };
    const token = generateEmbedToken(user);

    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    expect(decoded.rls.tenant_id).toBe(1);
    expect(decoded.rls.department).toBe('sales');
  });
});
```

### Test RLS

```javascript
describe('Row-Level Security', () => {
  it('should only return tenant data', async () => {
    const data = await executeQuery(
      { tenantId: 1 },
      'SELECT * FROM sales'
    );

    expect(data.every(row => row.tenant_id === 1)).toBe(true);
  });

  it('should prevent SQL injection', async () => {
    const maliciousUser = { tenantId: "1 OR 1=1" };

    await expect(
      executeQuery(maliciousUser, 'SELECT * FROM sales')
    ).rejects.toThrow();
  });
});
```

## Integration Tests

### Test Embedding Flow

```javascript
describe('Embedding Flow', () => {
  let browser, page;

  beforeAll(async () => {
    browser = await puppeteer.launch();
    page = await browser.newPage();
  });

  it('should embed dashboard successfully', async () => {
    await page.goto('http://localhost:3000/analytics');

    // Wait for dashboard to load
    await page.waitForSelector('.tableau-viz', { timeout: 30000 });

    // Verify dashboard visible
    const vizVisible = await page.$eval(
      '.tableau-viz',
      el => el.offsetHeight > 0
    );

    expect(vizVisible).toBe(true);
  });

  it('should apply filters correctly', async () => {
    await page.goto('http://localhost:3000/analytics');
    await page.waitForSelector('.tableau-viz');

    // Apply filter
    await page.select('select[name="region"]', 'west');

    // Wait for data update
    await page.waitForTimeout(1000);

    // Verify filtered data
    const data = await page.evaluate(() => {
      return window.tableauViz.getWorkbook()
        .getActiveSheet()
        .getDataSourcesAsync();
    });

    // Check data reflects filter
  });

  afterAll(async () => {
    await browser.close();
  });
});
```

## E2E Tests

### Cypress Example

```javascript
describe('Analytics Dashboard', () => {
  beforeEach(() => {
    cy.login('user@example.com', 'password');
  });

  it('should load dashboard for authenticated user', () => {
    cy.visit('/analytics');

    cy.get('[data-cy=dashboard-container]')
      .should('be.visible');

    cy.get('.tableau-viz')
      .should('be.visible');
  });

  it('should show correct tenant data', () => {
    cy.visit('/analytics');

    // Verify RLS
    cy.get('.data-row').each(($row) => {
      cy.wrap($row)
        .should('have.attr', 'data-tenant-id', '1');
    });
  });

  it('should handle token expiration', () => {
    cy.visit('/analytics');

    // Wait for token to expire
    cy.wait(35 * 60 * 1000); // 35 minutes

    // Verify auto-refresh
    cy.get('.tableau-viz').should('be.visible');
  });
});
```

## Performance Tests

```javascript
describe('Performance', () => {
  it('should load within 3 seconds', async () => {
    const start = Date.now();

    await page.goto('http://localhost:3000/analytics');
    await page.waitForSelector('.tableau-viz');

    const duration = Date.now() - start;
    expect(duration).toBeLessThan(3000);
  });

  it('should handle 100 concurrent users', async () => {
    const requests = [];

    for (let i = 0; i < 100; i++) {
      requests.push(
        fetch('/api/embed-token', { method: 'POST' })
      );
    }

    const responses = await Promise.all(requests);
    const successCount = responses.filter(r => r.ok).length;

    expect(successCount).toBe(100);
  });
});
```

## Security Tests

```javascript
describe('Security', () => {
  it('should reject invalid tokens', async () => {
    const response = await fetch('/api/analytics/data', {
      headers: { 'Authorization': 'Bearer invalid-token' }
    });

    expect(response.status).toBe(401);
  });

  it('should prevent tenant data leakage', async () => {
    const tenant1Data = await getData({ tenantId: 1 });
    const tenant2Data = await getData({ tenantId: 2 });

    const ids1 = new Set(tenant1Data.map(r => r.id));
    const ids2 = new Set(tenant2Data.map(r => r.id));
    const overlap = [...ids1].filter(id => ids2.has(id));

    expect(overlap).toHaveLength(0);
  });
});
```

## Test Checklist

- [ ] Unit tests for token generation
- [ ] Unit tests for RLS
- [ ] Integration tests for embedding
- [ ] E2E tests for user flows
- [ ] Performance tests
- [ ] Security tests
- [ ] Cross-browser testing
- [ ] Mobile testing
- [ ] Load testing
- [ ] Penetration testing

# Complete Guide: Tableau Embedding

## Prerequisites
- Tableau Server or Tableau Cloud access
- Connected App configured
- Node.js backend application
- React/Vue/vanilla JS frontend

## Step 1: Create Connected App in Tableau

```bash
# Login to Tableau Server
# Navigate to Settings > Connected Apps
# Click "New Connected App"
# Note the Client ID and Secret Key
```

**Configuration**:
- Name: "Your App Analytics"
- Domain whitelist: `https://yourapp.example.com`
- Access level: Embedding

## Step 2: Backend Token Generation

```javascript
// server.js
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');

app.post('/api/tableau-token', (req, res) => {
  const user = req.user; // From auth middleware

  const payload = {
    iss: process.env.TABLEAU_CLIENT_ID,
    sub: user.email,
    aud: 'tableau',
    jti: uuidv4(),
    scp: ['tableau:views:embed'],
    exp: Math.floor(Date.now() / 1000) + (10 * 60),
    
    'https://tableau.com/oda': {
      tenant_id: user.tenantId,
      department: user.department
    }
  };

  const token = jwt.sign(payload, process.env.TABLEAU_SECRET, {
    algorithm: 'HS256',
    header: {
      kid: process.env.TABLEAU_CLIENT_ID,
      iss: process.env.TABLEAU_CLIENT_ID
    }
  });

  res.json({ token });
});
```

## Step 3: Frontend Embedding

```javascript
// DashboardPage.jsx
import { useEffect, useState } from 'react';

export default function TableauDashboard() {
  const [viz, setViz] = useState(null);

  useEffect(() => {
    loadTableauViz();
  }, []);

  async function loadTableauViz() {
    // Get token
    const response = await fetch('/api/tableau-token', {
      method: 'POST',
      credentials: 'include'
    });
    const { token } = await response.json();

    // Load Tableau viz
    const containerDiv = document.getElementById('viz-container');
    const url = 'https://tableau.example.com/t/yoursite/views/Sales';

    const vizObj = new tableau.Viz(containerDiv, url, {
      width: '100%',
      height: '800px',
      hideTabs: true,
      hideToolbar: false,
      onFirstInteractive: () => {
        console.log('Viz loaded!');
      }
    });

    setViz(vizObj);
  }

  return <div id="viz-container" />;
}
```

## Step 4: RLS Implementation

```sql
-- In Tableau data source
-- Create calculated field: [Tenant Filter]
IF [tenant_id] = ATTR([Tenant ID User Attribute]) THEN TRUE ELSE FALSE END

-- Add to Filters > Add to Context
```

## Step 5: Testing Checklist
- [ ] Token generates successfully
- [ ] Viz loads in browser
- [ ] RLS filters data correctly
- [ ] Different users see different data
- [ ] Token expires after 10 minutes
- [ ] Refresh works
- [ ] Mobile responsive

## Troubleshooting

**Issue**: "Invalid token"
- Check secret key matches
- Verify Client ID in JWT header
- Check token expiration

**Issue**: "CORS error"
- Add domain to Connected App whitelist
- Check HTTPS configuration

**Issue**: "Data not filtering"
- Verify RLS calculated field
- Check user attribute mapping
- Test with different users

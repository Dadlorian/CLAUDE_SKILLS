# SMART on FHIR Implementation Guide

## Step 1: Register Your Application

### Application Registration Form
```
Application Name: My Health Portal
Redirect URI: https://myapp.example.com/callback
Authorized Scopes:
  - patient/Patient.read
  - patient/Observation.read
  - patient/Condition.read
  - patient/MedicationRequest.read
  - offline_access

Application Type: Public (Browser-based)
or Confidential (Server-to-server)
```

### Get OAuth Credentials
```
Client ID: abc123def456
Client Secret: (only for confidential apps)
Discovery Endpoint: https://fhir-server.example.com/.well-known/smart-configuration
```

## Step 2: Implement OAuth 2.0 Flow

### Server-Side (Node.js Example)

#### Step 1: Redirect User to Authorization Server
```javascript
const express = require('express');
const axios = require('axios');

app.get('/login', (req, res) => {
    const authorizationUrl = `${FHIR_SERVER}/auth/authorize?` +
        `response_type=code&` +
        `client_id=${CLIENT_ID}&` +
        `redirect_uri=${encodeURIComponent(REDIRECT_URI)}&` +
        `scope=${encodeURIComponent('patient/Patient.read patient/Observation.read')}&` +
        `state=${generateRandomState()}`;

    res.redirect(authorizationUrl);
});
```

#### Step 2: Handle Authorization Callback
```javascript
app.get('/callback', async (req, res) => {
    const { code, state, error } = req.query;

    // Verify state parameter
    if (state !== req.session.state) {
        return res.status(400).send('Invalid state parameter');
    }

    if (error) {
        return res.status(400).send(`Authorization error: ${error}`);
    }

    try {
        // Exchange authorization code for access token
        const tokenResponse = await axios.post(
            `${FHIR_SERVER}/auth/token`,
            {
                grant_type: 'authorization_code',
                code: code,
                client_id: CLIENT_ID,
                client_secret: CLIENT_SECRET,
                redirect_uri: REDIRECT_URI
            }
        );

        const { access_token, refresh_token, expires_in } = tokenResponse.data;

        // Store tokens securely (encrypted in session or database)
        req.session.accessToken = access_token;
        req.session.refreshToken = refresh_token;
        req.session.expiresAt = Date.now() + (expires_in * 1000);

        // Redirect to app
        res.redirect('/app');

    } catch (error) {
        console.error('Token exchange failed:', error);
        res.status(500).send('Authentication failed');
    }
});
```

## Step 3: Make FHIR API Calls

### Using Access Token
```javascript
async function getFHIRResource(resourceType, resourceId) {
    // Check if token is expired
    if (Date.now() > req.session.expiresAt) {
        await refreshToken();
    }

    const response = await axios.get(
        `${FHIR_SERVER}/fhir/${resourceType}/${resourceId}`,
        {
            headers: {
                'Authorization': `Bearer ${req.session.accessToken}`,
                'Accept': 'application/fhir+json'
            }
        }
    );

    return response.data;
}

// Get patient data
app.get('/api/patient', async (req, res) => {
    try {
        // Extract patient ID from token
        const patient = await getFHIRResource('Patient', 'patient-123');
        res.json(patient);
    } catch (error) {
        console.error('Error fetching patient:', error);
        res.status(500).json({ error: 'Failed to fetch patient' });
    }
});

// Get observations
app.get('/api/observations', async (req, res) => {
    try {
        const response = await axios.get(
            `${FHIR_SERVER}/fhir/Observation?patient=patient-123`,
            {
                headers: {
                    'Authorization': `Bearer ${req.session.accessToken}`
                }
            }
        );

        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch observations' });
    }
});
```

### Refresh Token
```javascript
async function refreshToken() {
    try {
        const response = await axios.post(
            `${FHIR_SERVER}/auth/token`,
            {
                grant_type: 'refresh_token',
                refresh_token: req.session.refreshToken,
                client_id: CLIENT_ID,
                client_secret: CLIENT_SECRET
            }
        );

        const { access_token, refresh_token, expires_in } = response.data;

        req.session.accessToken = access_token;
        req.session.refreshToken = refresh_token;
        req.session.expiresAt = Date.now() + (expires_in * 1000);

    } catch (error) {
        console.error('Token refresh failed:', error);
        throw error;
    }
}
```

## Step 4: Client-Side Implementation

### JavaScript FHIR Client Library
```html
<script src="https://cdn.jsdelivr.net/gh/smart-on-fhir/client-js@2/dist/build/fhirclient.js"></script>

<script>
FHIR.oauth2.init({
    clientId: 'your-client-id',
    scopes: ['patient/Patient.read', 'patient/Observation.read', 'offline_access'],
    redirectUri: 'https://myapp.example.com/callback'
}).then(client => {
    return client.patient.read();
}).then(patient => {
    console.log('Patient:', patient);
    // Display patient information
    document.getElementById('name').textContent =
        `${patient.name[0].given.join(' ')} ${patient.name[0].family}`;
    document.getElementById('dob').textContent =
        `DOB: ${patient.birthDate}`;
}).catch(err => {
    console.error('Error:', err);
});
</script>
```

### Standalone App Example (React)
```jsx
import React, { useEffect, useState } from 'react';
import FHIR from 'fhirclient';

function PatientApp() {
    const [patient, setPatient] = useState(null);
    const [observations, setObservations] = useState([]);

    useEffect(() => {
        FHIR.oauth2.init({
            clientId: 'your-client-id',
            scopes: ['patient/Patient.read', 'patient/Observation.read'],
        }).then(client => {
            // Get patient
            client.patient.read().then(patient => {
                setPatient(patient);
            });

            // Get observations
            client.patient.request(`Observation?patient=${client.patient.id}`)
                .then(bundle => {
                    setObservations(bundle.entry.map(e => e.resource));
                });
        });
    }, []);

    if (!patient) return <div>Loading...</div>;

    return (
        <div>
            <h1>{patient.name[0].given.join(' ')} {patient.name[0].family}</h1>
            <p>DOB: {patient.birthDate}</p>

            <h2>Recent Results</h2>
            <ul>
                {observations.map(obs => (
                    <li key={obs.id}>
                        {obs.code.coding[0].display}: {obs.valueQuantity?.value} {obs.valueQuantity?.unit}
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default PatientApp;
```

## Step 5: Handle User Context

### Extract User/Patient from Token
```javascript
const jwt = require('jsonwebtoken');

function extractContextFromToken(accessToken) {
    // Verify and decode token
    const decoded = jwt.decode(accessToken);

    return {
        userId: decoded.fhir_user,
        patientId: decoded.patient,
        encounterId: decoded.encounter,
        scopes: decoded.scope.split(' ')
    };
}

// Use context to limit queries
app.get('/api/patient-data', async (req, res) => {
    const { patientId } = extractContextFromToken(req.session.accessToken);

    // Only return data for the authenticated patient
    const patient = await getFHIRResource('Patient', patientId);
    const observations = await queryObservations(patientId);

    res.json({ patient, observations });
});
```

## Step 6: Implement PKCE for Public Apps

### Client-Side PKCE Implementation
```javascript
const crypto = require('crypto');

function generateCodeChallenge() {
    // Generate random code verifier (43-128 characters)
    const codeVerifier = base64url(crypto.randomBytes(32));

    // Generate code challenge
    const hash = crypto.createHash('sha256').update(codeVerifier).digest();
    const codeChallenge = base64url(hash);

    // Store verifier in session (not in URL)
    sessionStorage.setItem('code_verifier', codeVerifier);

    return codeChallenge;
}

function base64url(buffer) {
    return buffer
        .toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');
}

// Use in authorization request
const codeChallenge = generateCodeChallenge();

const authUrl = `${FHIR_SERVER}/auth/authorize?` +
    `response_type=code&` +
    `client_id=${CLIENT_ID}&` +
    `redirect_uri=${encodeURIComponent(REDIRECT_URI)}&` +
    `code_challenge=${codeChallenge}&` +
    `code_challenge_method=S256&` +
    `scope=${encodeURIComponent('patient/Patient.read')}&` +
    `state=${state}`;

// In callback, use stored verifier
const codeVerifier = sessionStorage.getItem('code_verifier');

const tokenResponse = await fetch(`${FHIR_SERVER}/auth/token`, {
    method: 'POST',
    body: new URLSearchParams({
        grant_type: 'authorization_code',
        code: code,
        client_id: CLIENT_ID,
        code_verifier: codeVerifier,
        redirect_uri: REDIRECT_URI
    })
});
```

## Step 7: Error Handling & Security

### Secure Token Storage
```javascript
// Use httpOnly cookie (server-side)
res.cookie('access_token', accessToken, {
    httpOnly: true,    // Not accessible from JavaScript
    secure: true,      // HTTPS only
    sameSite: 'lax',   // CSRF protection
    maxAge: expiresIn * 1000
});

// Or use localStorage with encryption (client-side)
function encryptToken(token) {
    return CryptoJS.AES.encrypt(token, SECRET_KEY).toString();
}

function decryptToken(encrypted) {
    return CryptoJS.AES.decrypt(encrypted, SECRET_KEY).toString(CryptoJS.enc.Utf8);
}

localStorage.setItem('access_token', encryptToken(accessToken));
```

### Handle Authorization Errors
```javascript
async function callFHIRAPI(url) {
    try {
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${getAccessToken()}`
            }
        });

        if (response.status === 401) {
            // Token expired or invalid
            await refreshToken();
            return callFHIRAPI(url); // Retry
        }

        if (response.status === 403) {
            // Insufficient permissions
            console.error('Insufficient permissions');
            return null;
        }

        if (response.status === 404) {
            // Resource not found
            return null;
        }

        return await response.json();

    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}
```

## Step 8: Logout & Token Revocation

```javascript
app.get('/logout', async (req, res) => {
    const accessToken = req.session.accessToken;

    try {
        // Revoke token
        await axios.post(`${FHIR_SERVER}/auth/revoke`, {
            token: accessToken,
            client_id: CLIENT_ID,
            client_secret: CLIENT_SECRET
        });

    } catch (error) {
        console.error('Token revocation failed:', error);
    }

    // Clear session
    req.session.destroy();
    res.redirect('/');
});
```

## Step 9: Testing SMART Integration

```python
import unittest
from unittest.mock import patch, MagicMock

class TestSMARTIntegration(unittest.TestCase):
    def setUp(self):
        self.client_id = 'test-client'
        self.client_secret = 'test-secret'

    @patch('requests.post')
    def test_authorize_user(self, mock_post):
        """Test authorization flow"""
        # Mock token response
        mock_post.return_value.json.return_value = {
            'access_token': 'token123',
            'token_type': 'Bearer',
            'expires_in': 3600
        }

        # Get token
        result = get_token('auth_code')

        self.assertEqual(result['access_token'], 'token123')

    @patch('requests.get')
    def test_get_patient_data(self, mock_get):
        """Test FHIR API call"""
        # Mock patient response
        mock_get.return_value.json.return_value = {
            'resourceType': 'Patient',
            'id': '123',
            'name': [{'family': 'Doe', 'given': ['John']}]
        }

        patient = fetch_patient('123', 'token123')

        self.assertEqual(patient['name'][0]['family'], 'Doe')

if __name__ == '__main__':
    unittest.main()
```

## Security Best Practices

1. **Always use HTTPS**
2. **Validate redirect URIs** - Whitelist in app configuration
3. **Store tokens securely** - Use httpOnly cookies or encrypted localStorage
4. **Implement PKCE** - For public/mobile applications
5. **Validate JWT signatures** - Verify token authenticity
6. **Handle token expiration** - Implement refresh logic
7. **Limit scopes** - Request only necessary permissions
8. **Implement CSRF protection** - Use state parameter

## Next Steps

1. Register your app with FHIR server
2. Test OAuth flow in development
3. Implement token refresh logic
4. Add error handling for edge cases
5. Deploy to production with HTTPS

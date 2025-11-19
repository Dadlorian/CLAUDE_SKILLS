# CDS Hooks Implementation Guide

## Overview
Step-by-step guide to implementing CDS Hooks services for clinical decision support integration with EHR systems.

## Prerequisites

- Node.js or Python runtime
- FHIR R4 knowledge
- Access to EHR test environment
- Understanding of clinical workflows

## Step 1: Project Setup

### Node.js/Express Setup
```bash
mkdir cds-hooks-service
cd cds-hooks-service
npm init -y
npm install express body-parser cors axios dotenv
npm install --save-dev nodemon jest
```

### Project Structure
```
cds-hooks-service/
├── src/
│   ├── index.js
│   ├── services/
│   │   ├── discovery.js
│   │   ├── drug-interaction.js
│   │   ├── allergy-check.js
│   │   └── renal-dosing.js
│   ├── fhir/
│   │   └── client.js
│   ├── databases/
│   │   └── fdb-client.js
│   └── utils/
│       ├── logger.js
│       └── validators.js
├── tests/
├── config/
└── package.json
```

## Step 2: Implement Discovery Endpoint

### src/services/discovery.js
```javascript
const services = [
  {
    hook: "medication-prescribe",
    id: "drug-interaction-checker",
    title: "Drug-Drug Interaction Checker",
    description: "Checks for major drug-drug interactions",
    prefetch: {
      patient: "Patient/{{context.patientId}}",
      medications: "MedicationRequest?patient={{context.patientId}}&status=active"
    }
  },
  {
    hook: "medication-prescribe",
    id: "allergy-checker",
    title: "Drug-Allergy Cross-Reactivity Checker",
    description: "Checks for drug allergies and cross-reactivity",
    prefetch: {
      patient: "Patient/{{context.patientId}}",
      allergies: "AllergyIntolerance?patient={{context.patientId}}&clinical-status=active"
    }
  },
  {
    hook: "medication-prescribe",
    id: "renal-dosing",
    title: "Renal Dose Adjustment",
    description: "Recommends dose adjustments based on renal function",
    prefetch: {
      patient: "Patient/{{context.patientId}}",
      labs: "Observation?patient={{context.patientId}}&code=2160-0&_sort=-date&_count=1"
    }
  }
];

function getDiscovery(req, res) {
  res.json({ services });
}

module.exports = { getDiscovery };
```

### src/index.js
```javascript
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { getDiscovery } = require('./services/discovery');
const drugInteractionService = require('./services/drug-interaction');
const allergyCheckService = require('./services/allergy-check');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Discovery endpoint
app.get('/cds-services', getDiscovery);

// Service endpoints
app.post('/cds-services/drug-interaction-checker', drugInteractionService.handle);
app.post('/cds-services/allergy-checker', allergyCheckService.handle);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`CDS Hooks service running on port ${PORT}`);
});
```

## Step 3: Implement Drug Interaction Service

### src/services/drug-interaction.js
```javascript
const FDBClient = require('../databases/fdb-client');
const FHIRClient = require('../fhir/client');
const logger = require('../utils/logger');

async function handle(req, res) {
  try {
    const { hook, hookInstance, context, prefetch } = req.body;

    // Validate request
    if (!context.patientId || !context.medications) {
      return res.json({ cards: [] });
    }

    // Extract medications
    const newMedications = context.medications || context.draftOrders;
    const activeMedications = prefetch?.medications?.entry?.map(e => e.resource) || [];

    // If no prefetch, query FHIR server
    if (!prefetch?.medications && context.fhirServer) {
      const fhirClient = new FHIRClient(context.fhirServer, context.fhirAuthorization);
      const bundle = await fhirClient.search('MedicationRequest', {
        patient: context.patientId,
        status: 'active'
      });
      activeMedications.push(...bundle.entry.map(e => e.resource));
    }

    // Combine new and active medications
    const allMedications = [...newMedications, ...activeMedications];

    // Extract RxNorm codes
    const rxcuis = allMedications.map(med => extractRxNorm(med)).filter(Boolean);

    // Check interactions with drug database
    const fdbClient = new FDBClient();
    const interactions = await fdbClient.checkInteractions(rxcuis, {
      severities: ['CONTRAINDICATED', 'MAJOR']
    });

    // Generate CDS Hooks cards
    const cards = interactions.map(interaction => createInteractionCard(interaction, allMedications));

    res.json({ cards });

  } catch (error) {
    logger.error('Drug interaction check failed:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}

function extractRxNorm(medication) {
  const coding = medication.medicationCodeableConcept?.coding ||
                 medication.medication?.coding || [];
  const rxnorm = coding.find(c => c.system === 'http://www.nlm.nih.gov/research/umls/rxnorm');
  return rxnorm?.code;
}

function createInteractionCard(interaction, medications) {
  const { drug1, drug2, severity, description, management } = interaction;

  const card = {
    uuid: `interaction-${drug1.rxcui}-${drug2.rxcui}`,
    summary: `${severity} interaction: ${drug1.name} + ${drug2.name}`,
    detail: `${description}\n\nManagement: ${management}`,
    indicator: severity === 'CONTRAINDICATED' ? 'critical' : 'warning',
    source: {
      label: 'First DataBank',
      url: interaction.monograph_url
    },
    suggestions: []
  };

  // Add suggestions to modify orders
  if (interaction.alternatives) {
    card.suggestions = interaction.alternatives.map(alt => ({
      label: `Switch to ${alt.name}`,
      actions: [
        {
          type: 'delete',
          description: `Remove ${drug1.name}`,
          resourceId: [findMedicationId(medications, drug1.rxcui)]
        },
        {
          type: 'create',
          description: `Order ${alt.name}`,
          resource: createMedicationRequest(alt)
        }
      ]
    }));
  }

  // Override reasons
  card.overrideReasons = [
    { code: 'benefit-outweighs-risk', display: 'Benefit outweighs risk' },
    { code: 'patient-tolerates', display: 'Patient tolerates combination' },
    { code: 'close-monitoring', display: 'Will monitor closely' }
  ];

  return card;
}

module.exports = { handle };
```

## Step 4: Implement Allergy Checker

### src/services/allergy-check.js
```javascript
async function handle(req, res) {
  try {
    const { context, prefetch } = req.body;

    // Get patient allergies
    let allergies = prefetch?.allergies?.entry?.map(e => e.resource) || [];

    if (allergies.length === 0) {
      return res.json({ cards: [] });
    }

    // Get medications being ordered
    const medications = context.medications || context.draftOrders || [];

    // Check each medication against allergies
    const cards = [];

    for (const med of medications) {
      const medRxNorm = extractRxNorm(med);
      if (!medRxNorm) continue;

      for (const allergy of allergies) {
        const allergenRxNorm = extractAllergen(allergy);
        if (!allergenRxNorm) continue;

        // Check for match or cross-reactivity
        const match = await checkAllergyMatch(medRxNorm, allergenRxNorm, allergy);

        if (match) {
          cards.push(createAllergyCard(med, allergy, match));
        }
      }
    }

    res.json({ cards });

  } catch (error) {
    logger.error('Allergy check failed:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}

async function checkAllergyMatch(medRxNorm, allergenRxNorm, allergy) {
  // Exact match
  if (medRxNorm === allergenRxNorm) {
    return {
      type: 'EXACT',
      severity: allergy.criticality || 'high',
      reaction: allergy.reaction?.[0]?.manifestation?.[0]?.text
    };
  }

  // Check cross-reactivity (beta-lactams, etc.)
  const crossReactivity = await checkCrossReactivity(medRxNorm, allergenRxNorm);

  if (crossReactivity) {
    return {
      type: 'CROSS_REACTIVITY',
      severity: 'medium',
      risk: crossReactivity.risk,
      description: crossReactivity.description
    };
  }

  return null;
}

function createAllergyCard(medication, allergy, match) {
  const isExact = match.type === 'EXACT';

  return {
    uuid: `allergy-${medication.id || 'new'}-${allergy.id}`,
    summary: isExact
      ? `ALLERGY ALERT: Patient allergic to ${allergenName(allergy)}`
      : `Possible cross-reactivity with ${allergenName(allergy)} allergy`,
    detail: `
      Medication: ${medicationName(medication)}
      Known allergy: ${allergenName(allergy)}
      Reaction: ${allergy.reaction?.[0]?.manifestation?.[0]?.text || 'Unknown'}
      Date: ${allergy.onsetDateTime || 'Unknown'}
      ${match.type === 'CROSS_REACTIVITY' ? `\nCross-reactivity risk: ${match.risk}%\n${match.description}` : ''}
    `,
    indicator: isExact ? 'critical' : 'warning',
    source: {
      label: 'Patient Allergy List'
    },
    suggestions: isExact ? [] : [
      {
        label: 'Continue with caution',
        actions: []
      }
    ],
    overrideReasons: isExact ? [
      { code: 'allergy-test-passed', display: 'Patient passed allergy testing' },
      { code: 'allergy-inaccurate', display: 'Allergy documentation inaccurate' }
    ] : [
      { code: 'low-risk', display: 'Low cross-reactivity risk accepted' },
      { code: 'no-alternative', display: 'No therapeutic alternative available' }
    ]
  };
}

module.exports = { handle };
```

## Step 5: Testing

### Unit Tests
```javascript
// tests/drug-interaction.test.js
const request = require('supertest');
const app = require('../src/index');

describe('Drug Interaction Service', () => {
  test('should detect warfarin-aspirin interaction', async () => {
    const payload = {
      hook: 'medication-prescribe',
      hookInstance: 'test-123',
      context: {
        patientId: 'patient-123',
        medications: [
          {
            medicationCodeableConcept: {
              coding: [{
                system: 'http://www.nlm.nih.gov/research/umls/rxnorm',
                code: '855332',  // Warfarin
                display: 'Warfarin 5mg'
              }]
            }
          },
          {
            medicationCodeableConcept: {
              coding: [{
                system: 'http://www.nlm.nih.gov/research/umls/rxnorm',
                code: '1191',  // Aspirin
                display: 'Aspirin 81mg'
              }]
            }
          }
        ]
      }
    };

    const response = await request(app)
      .post('/cds-services/drug-interaction-checker')
      .send(payload)
      .expect(200);

    expect(response.body.cards).toHaveLength(1);
    expect(response.body.cards[0].indicator).toBe('warning');
    expect(response.body.cards[0].summary).toContain('interaction');
  });
});
```

## Step 6: Deployment

### Docker Configuration
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --production

COPY src ./src

EXPOSE 3000

CMD ["node", "src/index.js"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  cds-hooks:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - FDB_API_KEY=${FDB_API_KEY}
      - FHIR_SERVER=${FHIR_SERVER}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Step 7: EHR Integration

### Register with EHR
1. Provide discovery endpoint URL: `https://your-service.com/cds-services`
2. Configure authentication (OAuth 2.0, mTLS)
3. Map to appropriate EHR hooks
4. Test in EHR sandbox environment
5. Enable in production

### Monitoring & Logging
```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

// Log all requests
app.use((req, res, next) => {
  logger.info({
    method: req.method,
    path: req.path,
    hook: req.body?.hook,
    patientId: req.body?.context?.patientId
  });
  next();
});
```

## Best Practices

1. **Performance**: Respond in < 3 seconds
2. **Graceful Degradation**: Return empty cards on error, don't block workflow
3. **Caching**: Cache drug databases and reference data
4. **Security**: Validate all inputs, use HTTPS, implement rate limiting
5. **Monitoring**: Track response times, error rates, card display rates
6. **Testing**: Comprehensive unit and integration tests
7. **Documentation**: Provide clear service descriptions

## Resources
- CDS Hooks Specification: https://cds-hooks.org
- CDS Hooks Sandbox: https://sandbox.cds-hooks.org
- Sample Services: https://github.com/cds-hooks

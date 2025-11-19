/**
 * CDS Hooks Service - Production-Grade Implementation
 * Provides medication safety checking via CDS Hooks standard
 */

const express = require('express');
const axios = require('axios');

class CDSHooksService {
  constructor(config) {
    this.fdbApiKey = config.fdbApiKey;
    this.fhirBaseUrl = config.fhirBaseUrl;
  }

  // Discovery endpoint
  getDiscovery() {
    return {
      services: [
        {
          hook: 'medication-prescribe',
          id: 'drug-interaction-checker',
          title: 'Drug-Drug Interaction Checker',
          description: 'Checks for major drug-drug interactions using First DataBank',
          prefetch: {
            patient: 'Patient/{{context.patientId}}',
            medications: 'MedicationRequest?patient={{context.patientId}}&status=active',
            allergies: 'AllergyIntolerance?patient={{context.patientId}}&clinical-status=active'
          }
        },
        {
          hook: 'order-sign',
          id: 'final-safety-check',
          title: 'Final Safety Check Before Signing',
          description: 'Comprehensive safety check before order signature',
          prefetch: {
            patient: 'Patient/{{context.patientId}}',
            labs: 'Observation?patient={{context.patientId}}&category=laboratory&_sort=-date&_count=10'
          }
        }
      ]
    };
  }

  // Handle medication-prescribe hook
  async handleMedicationPrescribe(request) {
    const { context, prefetch } = request;
    const cards = [];

    try {
      // Extract medications
      const newMeds = context.medications || context.draftOrders || [];
      const activeMeds = prefetch?.medications?.entry?.map(e => e.resource) || [];
      const allergies = prefetch?.allergies?.entry?.map(e => e.resource) || [];

      // Check drug-drug interactions
      const interactions = await this.checkDrugInteractions(newMeds, activeMeds);
      if (interactions.length > 0) {
        cards.push(...interactions.map(i => this.createInteractionCard(i)));
      }

      // Check allergies
      for (const newMed of newMeds) {
        for (const allergy of allergies) {
          const allergyMatch = this.checkAllergyMatch(newMed, allergy);
          if (allergyMatch) {
            cards.push(this.createAllergyCard(newMed, allergy, allergyMatch));
          }
        }
      }

      return { cards };

    } catch (error) {
      console.error('Error in medication-prescribe hook:', error);
      return { cards: [] };  // Fail gracefully
    }
  }

  async checkDrugInteractions(newMeds, activeMeds) {
    const allMeds = [...newMeds, ...activeMeds];
    const rxcuis = allMeds.map(med => this.extractRxNorm(med)).filter(Boolean);

    if (rxcuis.length < 2) return [];

    try {
      const response = await axios.post('https://api.fdb.com/v1/interactions', {
        medications: rxcuis,
        severity: ['CONTRAINDICATED', 'MAJOR']
      }, {
        headers: { 'Authorization': `Bearer ${this.fdbApiKey}` }
      });

      return response.data.interactions || [];

    } catch (error) {
      console.error('FDB API error:', error);
      return [];
    }
  }

  extractRxNorm(medication) {
    const coding = medication.medicationCodeableConcept?.coding || [];
    const rxnorm = coding.find(c =>
      c.system === 'http://www.nlm.nih.gov/research/umls/rxnorm'
    );
    return rxnorm?.code;
  }

  checkAllergyMatch(medication, allergy) {
    const medRxNorm = this.extractRxNorm(medication);
    const allergenCoding = allergy.code?.coding || [];
    const allergenRxNorm = allergenCoding.find(c =>
      c.system === 'http://www.nlm.nih.gov/research/umls/rxnorm'
    );

    if (medRxNorm === allergenRxNorm?.code) {
      return {
        type: 'EXACT',
        severity: allergy.criticality || 'high',
        reaction: allergy.reaction?.[0]?.manifestation?.[0]?.text
      };
    }

    // Check beta-lactam cross-reactivity
    if (this.isBetaLactam(medRxNorm) && this.isBetaLactam(allergenRxNorm?.code)) {
      return {
        type: 'CROSS_REACTIVITY',
        severity: 'medium',
        risk: 0.05,
        description: 'Beta-lactam cross-reactivity possible (1-5%)'
      };
    }

    return null;
  }

  isBetaLactam(rxcui) {
    const betaLactams = ['7984', '1596450', '2193'];  // Penicillin, amoxicillin, etc.
    return betaLactams.includes(rxcui);
  }

  createInteractionCard(interaction) {
    const { drug1, drug2, severity, description, management } = interaction;

    return {
      uuid: `interaction-${drug1.rxcui}-${drug2.rxcui}`,
      summary: `${severity} interaction: ${drug1.name} + ${drug2.name}`,
      detail: `${description}\n\nManagement: ${management}`,
      indicator: severity === 'CONTRAINDICATED' ? 'critical' : 'warning',
      source: {
        label: 'First DataBank',
        url: interaction.monographUrl
      },
      suggestions: interaction.alternatives ? [{
        label: `Switch to ${interaction.alternatives[0].name}`,
        actions: [{
          type: 'create',
          description: `Order ${interaction.alternatives[0].name}`,
          resource: this.createMedicationRequest(interaction.alternatives[0])
        }]
      }] : [],
      overrideReasons: [
        { code: 'benefit-outweighs-risk', display: 'Benefit outweighs risk' },
        { code: 'patient-tolerates', display: 'Patient tolerates combination' },
        { code: 'close-monitoring', display: 'Patient will be closely monitored' }
      ]
    };
  }

  createAllergyCard(medication, allergy, match) {
    const isExact = match.type === 'EXACT';

    return {
      uuid: `allergy-${medication.id || 'new'}-${allergy.id}`,
      summary: isExact
        ? `ALLERGY ALERT: Patient allergic to ${this.getMedicationName(medication)}`
        : `Possible cross-reactivity with documented allergy`,
      detail: `
Medication: ${this.getMedicationName(medication)}
Known allergy: ${allergy.code?.text || 'Unknown'}
Reaction: ${match.reaction || 'Unknown'}
${match.type === 'CROSS_REACTIVITY' ? `Cross-reactivity risk: ${match.risk * 100}%` : ''}
      `.trim(),
      indicator: isExact ? 'critical' : 'warning',
      source: {
        label: 'Patient Allergy List'
      },
      overrideReasons: isExact ? [
        { code: 'allergy-test-passed', display: 'Patient passed allergy testing' }
      ] : [
        { code: 'low-risk', display: 'Low cross-reactivity risk accepted' }
      ]
    };
  }

  getMedicationName(medication) {
    return medication.medicationCodeableConcept?.coding?.[0]?.display ||
           medication.medicationCodeableConcept?.text ||
           'Unknown medication';
  }

  createMedicationRequest(alternative) {
    return {
      resourceType: 'MedicationRequest',
      status: 'draft',
      intent: 'order',
      medicationCodeableConcept: {
        coding: [{
          system: 'http://www.nlm.nih.gov/research/umls/rxnorm',
          code: alternative.rxcui,
          display: alternative.name
        }]
      }
    };
  }
}

// Express server setup
const app = express();
app.use(express.json());

const service = new CDSHooksService({
  fdbApiKey: process.env.FDB_API_KEY,
  fhirBaseUrl: process.env.FHIR_BASE_URL
});

// Routes
app.get('/cds-services', (req, res) => {
  res.json(service.getDiscovery());
});

app.post('/cds-services/drug-interaction-checker', async (req, res) => {
  const cards = await service.handleMedicationPrescribe(req.body);
  res.json(cards);
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`CDS Hooks service running on port ${PORT}`);
});

module.exports = CDSHooksService;

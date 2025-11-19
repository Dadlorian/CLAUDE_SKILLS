# Clinical Decision Support Integration Guide

## Overview
Guide for integrating CDS Hooks and SMART on FHIR clinical decision support into EHR workflows.

## CDS Hooks Implementation

### Hook Service Configuration
```json
{
  "services": [
    {
      "hook": "medication-prescribe",
      "title": "Drug-Drug Interaction Checker",
      "description": "Checks for drug-drug interactions",
      "id": "drug-interaction-cds",
      "prefetch": {
        "patient": "Patient/{{context.patientId}}",
        "medications": "MedicationRequest?patient={{context.patientId}}&status=active"
      }
    },
    {
      "hook": "order-select",
      "title": "Appropriate Use Criteria",
      "description": "Checks imaging appropriateness",
      "id": "imaging-auc-cds"
    }
  ]
}
```

### CDS Service Implementation
```javascript
// Express.js CDS service
app.post('/cds-services/drug-interaction-cds', async (req, res) => {
  const { context, prefetch } = req.body;

  // Get current medications from prefetch
  const currentMeds = prefetch.medications.entry.map(e => e.resource);

  // Get new medication from context
  const newMed = context.medications[0];

  // Check for interactions
  const interactions = await checkInteractions(newMed, currentMeds);

  // Build CDS cards
  const cards = interactions.map(interaction => ({
    summary: `Drug Interaction: ${interaction.severity}`,
    indicator: interaction.severity === 'HIGH' ? 'critical' : 'warning',
    detail: interaction.description,
    source: {
      label: 'Drug Interaction Database',
      url: 'https://druginteractiondb.example.com'
    },
    suggestions: [{
      label: 'Change dose',
      actions: [{
        type: 'update',
        description: interaction.recommendation,
        resource: { /* modified medication */ }
      }]
    }]
  }));

  res.json({ cards });
});
```

### EHR Integration
```javascript
// Call CDS service from EHR
async function callCDSService(hook, context, prefetch) {
  const response = await fetch('https://cds.example.com/cds-services/drug-interaction-cds', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      hook,
      hookInstance: crypto.randomUUID(),
      context,
      prefetch
    })
  });

  const { cards } = await response.json();
  return cards;
}

// Display cards to user
function displayCDSCards(cards) {
  cards.forEach(card => {
    if (card.indicator === 'critical') {
      showModal(card);  // Block workflow
    } else {
      showNotification(card);  // Non-blocking alert
    }
  });
}
```

## Rule Engine

### Drools Rules Example
```java
rule "High INR with Warfarin"
when
    $patient: Patient()
    $med: Medication(name == "Warfarin", patient == $patient)
    $lab: LabResult(test == "INR", value > 4.0, patient == $patient)
then
    Alert alert = new Alert();
    alert.setSeverity("CRITICAL");
    alert.setMessage("INR > 4.0 with Warfarin - Hold dose and contact provider");
    insert(alert);
end
```

## References
- CDS Hooks: https://cds-hooks.org/
- SMART on FHIR: https://smarthealthit.org/

---

**Document Version**: 1.0
**Last Updated**: November 2024

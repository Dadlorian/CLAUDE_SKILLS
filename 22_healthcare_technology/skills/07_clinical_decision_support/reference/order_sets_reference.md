# Order Sets Reference

## Overview
Order sets (also called order bundles or protocols) are pre-configured groups of orders for common clinical conditions that standardize care, improve efficiency, and ensure evidence-based treatment.

## Structure of Order Sets

### Core Components

```javascript
const orderSet = {
  // Metadata
  id: "sepsis_bundle_2023",
  name: "Severe Sepsis/Septic Shock Bundle",
  version: "3.1",
  effective_date: "2023-01-01",
  owner: "Critical Care Committee",
  specialty: "Critical Care",
  evidence: "Surviving Sepsis Campaign Guidelines 2021",

  // Inclusion criteria
  inclusion_criteria: {
    conditions: ["Sepsis", "Septic Shock"],
    settings: ["ED", "ICU", "Floor"],
    required_findings: ["qSOFA >= 2 OR SIRS >= 2 + suspected infection"]
  },

  // Exclusion criteria
  exclusion_criteria: [
    "Comfort care only",
    "DNR/DNI with family wishes against aggressive care"
  ],

  // Order groups
  order_groups: [
    {
      name: "Hour 0 - Initial Resuscitation",
      time_target: 60,  // minutes
      orders: [
        // Labs
        {
          type: "lab",
          name: "Blood Culture x 2 (different sites)",
          loinc: "600-7",
          priority: "STAT",
          pre_selected: true,
          required: true,
          notes: "Obtain BEFORE antibiotics if possible"
        },
        {
          type: "lab",
          name: "Lactate",
          loinc: "2524-7",
          priority: "STAT",
          pre_selected: true,
          required: true
        },
        {
          type: "lab",
          name: "CBC with differential",
          loinc: "58410-2",
          priority: "STAT",
          pre_selected: true
        },
        {
          type: "lab",
          name: "Comprehensive Metabolic Panel",
          loinc: "24323-8",
          priority: "STAT",
          pre_selected: true
        },
        {
          type: "lab",
          name: "Procalcitonin",
          loinc: "33959-8",
          priority: "STAT",
          pre_selected: false
        },

        // Antibiotics
        {
          type: "medication",
          name: "Ceftriaxone",
          dose: "2",
          dose_unit: "g",
          route: "IV",
          frequency: "Daily",
          priority: "STAT",
          pre_selected: true,
          required: true,
          instructions: "Administer within 1 hour",
          alternatives: [
            {
              condition: "Penicillin allergy",
              drug: "Aztreonam",
              dose: "2g IV q8h"
            },
            {
              condition: "Pseudomonas risk",
              drug: "Piperacillin-Tazobactam",
              dose: "4.5g IV q6h"
            }
          ]
        },

        // Fluids
        {
          type: "medication",
          name: "Normal Saline 0.9%",
          dose: "30",
          dose_unit: "mL/kg",
          route: "IV",
          frequency: "Bolus over 30 minutes",
          priority: "STAT",
          pre_selected: true,
          required: true,
          calculation: {
            based_on: "weight",
            formula: "weight_kg * 30"
          },
          max_dose: "3000 mL",
          contraindications: ["CHF with volume overload"]
        }
      ]
    },

    {
      name: "Hour 3 - Reassessment",
      time_target: 180,
      condition: "If lactate >= 2 mmol/L initially",
      orders: [
        {
          type: "lab",
          name: "Repeat Lactate",
          loinc: "2524-7",
          priority: "ROUTINE",
          pre_selected: true
        }
      ]
    },

    {
      name: "Supportive Care",
      orders: [
        {
          type: "medication",
          name: "Norepinephrine",
          dose: "0.05",
          dose_unit: "mcg/kg/min",
          route: "IV infusion",
          frequency: "Continuous",
          pre_selected: false,
          indication: "MAP < 65 mmHg despite fluid resuscitation",
          titration: "Titrate to MAP >= 65 mmHg",
          requires_central_line: true
        },
        {
          type: "order",
          name: "Central Venous Catheter",
          pre_selected: false,
          indication: "For vasopressor administration"
        }
      ]
    },

    {
      name: "Monitoring",
      orders: [
        {
          type: "nursing_order",
          name: "Vital signs q1h",
          duration: "24 hours"
        },
        {
          type: "nursing_order",
          name: "Strict intake/output"
        },
        {
          type: "consult",
          name: "ICU consultation",
          priority: "STAT",
          pre_selected: true
        }
      ]
    }
  ]
};
```

## Common Order Set Types

### 1. Admission Order Sets

#### General Medical Admission
```javascript
const medicalAdmission = {
  name: "General Medical Admission",
  sections: [
    {
      name: "Admission Orders",
      orders: [
        "Admit to Medicine service",
        "Attending: [Select]",
        "Diagnosis: [Free text]",
        "Condition: [Stable/Fair/Serious/Critical]",
        "Code status: [Full/DNR/DNI]"
      ]
    },
    {
      name: "Vital Signs",
      orders: [
        "Vitals: [q4h/q6h/q8h/q shift]",
        "Daily weights",
        "Orthostatic vitals (if indicated)"
      ]
    },
    {
      name: "Activity",
      orders: [
        "[Bedrest/Up in chair/Ambulate with assist/Ad lib]",
        "Fall precautions: [Standard/High risk]",
        "Physical therapy consult (if indicated)"
      ]
    },
    {
      name: "Diet",
      orders: [
        "[NPO/Clear liquids/Regular/Diabetic/Cardiac/Renal]",
        "Restrictions: [Sodium/Fluid/Other]"
      ]
    },
    {
      name: "Labs",
      orders: [
        "CBC in AM",
        "BMP in AM",
        "Other: [Specify]"
      ]
    },
    {
      name: "DVT Prophylaxis",
      orders: [
        {
          option: "Enoxaparin 40mg SC daily",
          contraindications: ["Active bleeding", "GFR < 30"]
        },
        {
          option: "Heparin 5000 units SC q8h",
          indication: "If renal insufficiency"
        },
        {
          option: "SCDs (pneumatic compression)",
          indication: "If contraindication to anticoagulation"
        }
      ]
    }
  ]
};
```

### 2. Procedure Order Sets

#### Conscious Sedation
```javascript
const consciousSedation = {
  name: "Conscious Sedation for Endoscopy",
  pre_procedure: [
    {
      order: "NPO after midnight",
      timing: "Night before"
    },
    {
      order: "H&P documented within 30 days",
      required: true
    },
    {
      order: "Informed consent obtained",
      required: true
    },
    {
      order: "IV access confirmed",
      required: true
    }
  ],

  medications: [
    {
      drug: "Midazolam",
      dose_range: "0.5-2 mg",
      route: "IV",
      titration: "Titrate to effect",
      max_dose: "5 mg"
    },
    {
      drug: "Fentanyl",
      dose_range: "25-100 mcg",
      route: "IV",
      titration: "Titrate to effect",
      max_dose: "200 mcg"
    }
  ],

  monitoring: [
    "Continuous pulse oximetry",
    "Continuous cardiac monitoring",
    "BP q5min during procedure",
    "Capnography (if available)"
  ],

  reversal_agents: [
    {
      drug: "Naloxone",
      indication: "Opioid reversal",
      dose: "0.4 mg IV, may repeat"
    },
    {
      drug: "Flumazenil",
      indication: "Benzodiazepine reversal",
      dose: "0.2 mg IV, may repeat",
      warning: "Caution in seizure patients"
    }
  ],

  post_procedure: [
    "Vitals q15min x 1 hour",
    "Discharge when alert and ambulatory",
    "Must have driver - document"
  ]
};
```

### 3. Protocol-Based Order Sets

#### Hyperglycemia Management
```javascript
const insulinProtocol = {
  name: "Subcutaneous Insulin Protocol",

  basal_insulin: {
    order: "Insulin glargine",
    timing: "Daily at bedtime",
    initial_dose: {
      calculation: "0.2 units/kg for insulin-naive",
      max_starting_dose: "20 units"
    }
  },

  nutritional_insulin: {
    order: "Insulin lispro with meals",
    dose_calculation: {
      formula: "Total daily insulin / 3 meals",
      example: "If total daily = 30 units → 10 units per meal"
    }
  },

  correction_scale: {
    name: "Correctional Insulin Lispro Scale",
    schedule: "Check BG AC and HS",
    tiers: [
      {
        name: "Low dose (insulin sensitive)",
        ranges: [
          { glucose: "150-200", insulin: "2 units" },
          { glucose: "201-250", insulin: "4 units" },
          { glucose: "251-300", insulin: "6 units" },
          { glucose: "301-350", insulin: "8 units" },
          { glucose: ">350", insulin: "10 units and call MD" }
        ]
      },
      {
        name: "Medium dose",
        ranges: [
          { glucose: "150-200", insulin: "4 units" },
          { glucose: "201-250", insulin: "6 units" },
          { glucose: "251-300", insulin: "8 units" },
          { glucose: "301-350", insulin: "10 units" },
          { glucose: ">350", insulin: "12 units and call MD" }
        ]
      }
    ]
  },

  hypoglycemia_protocol: {
    trigger: "BG < 70 mg/dL",
    treatment: [
      "Give 15g fast-acting carbohydrate (juice, glucose tabs)",
      "Recheck BG in 15 minutes",
      "Repeat if still < 70",
      "If unable to take PO: D50W 25mL IV",
      "Notify MD if BG < 50"
    ]
  }
};
```

### 4. Pathway-Based Order Sets

#### Chest Pain - Rule Out MI
```javascript
const chestPainProtocol = {
  name: "Chest Pain - Rule Out MI",

  initial_orders: [
    {
      order: "Continuous telemetry",
      duration: "Until ruled out"
    },
    {
      order: "Serial ECGs",
      frequency: "On arrival, 6h, 12h"
    },
    {
      order: "Serial troponins",
      frequency: "On arrival, 3h, 6h"
    },
    {
      order: "Aspirin 324mg",
      route: "PO",
      frequency: "STAT, then 81mg daily",
      contraindications: ["Active bleeding", "Known allergy"]
    }
  ],

  risk_stratification: {
    if_troponin_positive: [
      "Cardiology consult",
      "Heparin drip per protocol",
      "Clopidogrel 300mg load",
      "Atorvastatin 80mg daily",
      "Consider cardiac catheterization"
    ],

    if_troponin_negative_at_6h: [
      {
        low_risk: "Discharge with outpatient stress test",
        moderate_risk: "Observation with stress test",
        high_risk: "Cardiology consult for further evaluation"
      }
    ]
  },

  discharge_criteria: [
    "Troponin negative x 3",
    "No dynamic ECG changes",
    "Pain free",
    "Stress test completed (or scheduled)"
  ]
};
```

## Smart Order Sets

### Context-Aware Pre-Population

```javascript
class SmartOrderSet {
  constructor(patient, orderSet) {
    this.patient = patient;
    this.orderSet = orderSet;
  }

  populateIntelligently() {
    const populated = JSON.parse(JSON.stringify(this.orderSet));

    populated.orders.forEach(order => {
      // Pre-fill dose based on patient weight
      if (order.calculation?.based_on === 'weight') {
        const weight = this.patient.weight_kg;
        order.calculated_dose = eval(order.calculation.formula);
      }

      // Auto-select based on patient conditions
      if (order.alternatives) {
        const selected = this.selectAppropriateAlternative(order);
        if (selected) {
          order.pre_selected_alternative = selected;
        }
      }

      // Filter out contraindicated orders
      if (this.isContraindicated(order)) {
        order.pre_selected = false;
        order.warning = "Contraindicated - review before ordering";
      }

      // Adjust for renal function
      if (order.renal_dosing && this.patient.gfr < 60) {
        order.dose = this.adjustForRenalFunction(order);
        order.notes = `Dose adjusted for GFR ${this.patient.gfr}`;
      }
    });

    return populated;
  }

  selectAppropriateAlternative(order) {
    for (const alt of order.alternatives) {
      if (this.conditionMet(alt.condition)) {
        return alt;
      }
    }
    return null;
  }

  isContraindicated(order) {
    if (!order.contraindications) return false;

    return order.contraindications.some(ci =>
      this.patient.conditions.includes(ci) ||
      this.patient.allergies.includes(order.drug)
    );
  }
}
```

## Implementation Best Practices

### 1. Evidence-Based Content
- Ground in clinical guidelines (ACC/AHA, IDSA, etc.)
- Cite evidence sources
- Update with new guidelines

### 2. Clinical Validation
- Physician committee review and approval
- Pilot testing before system-wide deployment
- Regular review and updates

### 3. User Experience
- Logical grouping of orders
- Smart defaults (pre-selected when appropriate)
- Allow customization
- Minimize required clicks

### 4. Safety Checks
- Drug-drug interaction checking
- Allergy checking
- Duplicate order prevention
- Renal/hepatic dosing adjustments

### 5. Metrics and Monitoring

```javascript
const orderSetMetrics = {
  usage: {
    times_opened: 1523,
    times_signed: 1402,
    adoption_rate: 0.92,  // 92% completion rate
    avg_time_to_complete: 180  // seconds
  },

  modifications: {
    orders_added: 234,
    orders_removed: 156,
    modification_rate: 0.26  // 26% modify default set
  },

  outcomes: {
    bundle_compliance: 0.88,  // 88% get all bundle elements
    time_to_first_antibiotic: 45,  // minutes (median)
    quality_measure_achievement: 0.94
  }
};
```

### 6. Version Control

```javascript
const orderSetVersion = {
  current_version: "3.1",
  effective_date: "2023-11-01",
  previous_version: "3.0",
  changes: [
    "Updated antibiotic based on local resistance patterns",
    "Added procalcitonin as optional lab",
    "Modified fluid dose calculation to cap at 3L"
  ],
  approved_by: "Critical Care Committee",
  approval_date: "2023-10-15"
};
```

## FHIR Representation

### PlanDefinition Resource
```json
{
  "resourceType": "PlanDefinition",
  "id": "sepsis-bundle",
  "title": "Severe Sepsis/Septic Shock Bundle",
  "type": {
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/plan-definition-type",
      "code": "order-set"
    }]
  },
  "status": "active",
  "date": "2023-11-01",
  "action": [
    {
      "title": "Obtain blood cultures",
      "code": {
        "coding": [{
          "system": "http://loinc.org",
          "code": "600-7",
          "display": "Blood culture"
        }]
      },
      "timingDuration": {
        "value": 60,
        "unit": "minutes",
        "system": "http://unitsofmeasure.org",
        "code": "min"
      },
      "definitionCanonical": "ActivityDefinition/blood-culture"
    },
    {
      "title": "Administer broad-spectrum antibiotics",
      "definitionCanonical": "ActivityDefinition/ceftriaxone-2g",
      "timingDuration": {
        "value": 60,
        "unit": "minutes"
      }
    }
  ]
}
```

## Resources
- CMS Core Measures
- Joint Commission standards
- Specialty society guidelines (ACC/AHA, IDSA, etc.)
- Institute for Healthcare Improvement (IHI)
- Agency for Healthcare Research and Quality (AHRQ)

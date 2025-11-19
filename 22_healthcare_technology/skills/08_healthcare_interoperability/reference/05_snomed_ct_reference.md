# SNOMED CT (Systematized Nomenclature of Medicine Clinical Terms) Reference

## Overview

SNOMED CT is the world's most comprehensive clinical terminology standard. Provides standardized codes for diseases, conditions, procedures, findings, and body structures in healthcare.

## Core Concepts

### Concept Hierarchy
- **Root Concept:** 138875005 (SNOMED CT Concept)
- **Top-level categories** - Main branches of medical knowledge
- **Hierarchical relationships** - Parent-child relationships
- **Multiple hierarchies** - Can have multiple parents (poly-hierarchy)

### Main Hierarchies

| Root | Code | Description |
|------|------|-------------|
| Clinical Finding | 404684003 | Signs, symptoms, diseases |
| Procedure | 71388002 | Medical procedures, tests |
| Observable Entity | 363787002 | Observable characteristics |
| Body Structure | 123037004 | Anatomical structures |
| Organism | 410607006 | Infectious agents |
| Substance | 105590001 | Chemicals, medications |
| Qualifier Value | 362981000 | Modifiers for concepts |
| Biological Function | 34896006 | Physiological functions |
| Body Region | 442083009 | Anatomical regions |
| Linkage Concept | 106237007 | Relationships between concepts |

## SNOMED CT Codes

### Code Format
- **Numeric codes:** 5-18 digits
- **Check digit:** Last digit validates authenticity
- **Scope notes:** Human-readable descriptions
- **Fully Specified Name (FSN):** Official term with semantic tag

### Examples
```
80891009   Angina pectoris (disorder)
233604007  Pneumonia (disorder)
72633006   Osteoporosis (disorder)
66757008   Myocardial infarction (disorder)
56459004   Pulmonary edema (disorder)
```

## Relationships

### Semantic Relationships
- **IS-A** - Concept specialization (e.g., Pneumonia IS-A Lung Disease)
- **FINDING-SITE** - Location of finding (e.g., Pneumonia FINDING-SITE Lung)
- **DUE-TO** - Causation (e.g., Pneumonia DUE-TO Infection)
- **CAUSED-BY** - Agent causing condition
- **METHOD** - How procedure performed
- **LATERALITY** - Left/right/bilateral
- **PROCEDURE-SITE** - Anatomical location of procedure
- **PROCEDURE-MORPHOLOGY** - Type of tissue change
- **USING-SUBSTANCE** - Material used in procedure

### Relationship Examples
```
Pneumonia (disorder)
  ├─ IS-A → Respiratory tract infection
  ├─ IS-A → Lung disease
  ├─ FINDING-SITE → Lung structure
  └─ CAUSATION → Bacterial infection OR Viral infection
```

## Expressions (Post-Coordination)

### Compositional Grammar
Allows creation of new concepts from existing ones:

```
Fracture of tibia (disorder) + Laterality = left
≡ 243967001: Closed fracture of left tibia

Diabetes mellitus +
  Associated-morphology = Metabolic abnormality +
  Finding-site = Pancreas
≡ Type 2 diabetes mellitus
```

### Expression Examples
```
|Finding| + {
  260686004|Method|: 418775008|Physical examination|,
  246501002|Technique|: 258058003|Mechanical stimulus|
}

|Myocardial infarction| + {
  363698007|Finding site|: 43828004|Left anterior descending coronary artery|,
  116676008|Associated morphology|: 55641003|Infarct|
}
```

## Clinical Domains

### Disorders (Clinical Findings)
- Diseases
- Symptoms
- Signs
- Abnormal findings

**Examples:**
- Type 2 diabetes
- Hypertension
- Acute myocardial infarction

### Procedures
- Medical and surgical procedures
- Diagnostic tests
- Therapeutic interventions

**Examples:**
- Coronary artery bypass graft
- Computed tomography of chest
- Blood glucose measurement

### Body Structures
- Anatomical parts
- Anatomical locations
- Biological systems

**Examples:**
- Left ventricle
- Coronary artery
- Pancreas

### Observable Entities
- Observable characteristics
- Measurements
- Findings

**Examples:**
- Blood pressure
- Heart rate
- Serum glucose level

### Substances
- Medications
- Chemicals
- Biological materials

**Examples:**
- Metformin
- Lisinopril
- Saline solution

## Implementation

### SNOMED CT Distribution
- **Full Version** - All concepts and relationships
- **Snapshot** - Point-in-time distribution
- **Delta** - Changes since previous release
- **Extensional Subset** - Specific domain concepts

### Terminology Servers
- **SNOMED CT Browser** - Web-based access
- **Snowstorm** - Open-source terminology server
- **FHIR CodeSystem server** - REST API access
- **National implementations** - Country-specific versions

### API Access

#### REST API
```
GET /CodeSystem/snomed?url=http://snomed.info/sct&code=80891009
GET /ValueSet/$expand?url=http://example.com/ValueSet/diabetes
GET /ConceptMap/$translate?system=http://snomed.info/sct&code=80891009
```

#### FHIR Operations
```
POST /CodeSystem/$lookup {
  "system": "http://snomed.info/sct",
  "code": "80891009",
  "displayLanguage": "en"
}

POST /CodeSystem/$validate-code {
  "system": "http://snomed.info/sct",
  "code": "80891009"
}
```

## Value Sets and Subsets

### Clinical Quality Measures (CQM)
- Specific code lists for quality reporting
- Pre-defined value sets
- Measure calculation sets

### EHR Use Cases
- Problem list codes
- Medication codes
- Procedure codes
- Lab result codes

### Creating Value Sets
```json
{
  "resourceType": "ValueSet",
  "id": "diabetes-codes",
  "title": "Diabetes Mellitus Codes",
  "compose": {
    "include": [{
      "system": "http://snomed.info/sct",
      "filter": [{
        "property": "concept",
        "op": "is-a",
        "value": "250171008"
      }]
    }]
  }
}
```

## Code Mapping

### Cross-mapping
- **ICD-10-CM** - Diagnostic coding for billing
- **ICD-9-CM** - Legacy diagnostic coding
- **CPT** - Procedural coding
- **LOINC** - Laboratory observations

### Mapping Table Example
```
SNOMED CT (80891009) Angina pectoris
    ↓
ICD-10-CM (I20) Angina
    ↓
ICD-9-CM (413) Angina pectoris
```

## Licensing and Access

### Usage Rights
- **Language editions** - English, Spanish, German, Swedish, etc.
- **Extension creation** - Add specialty-specific terms
- **Institutional licenses** - Limited to organization
- **Public access** - Limited browsing and APIs

### Licensing Models
- **Browser access** - Free limited access
- **Institutional** - Organization-wide access
- **Developer** - API access for applications
- **Commercial** - Proprietary uses

## Challenges and Considerations

### Implementation Challenges
1. **Large concept set** - Over 350,000 concepts
2. **Complex relationships** - Difficult to traverse
3. **Multiple valid expressions** - Different ways to represent same concept
4. **Ongoing updates** - Quarterly releases require updates
5. **Technical expertise** - Steep learning curve

### Best Practices
1. Use established terminology servers
2. Cache concepts locally when possible
3. Implement concept validation
4. Use standard value sets
5. Plan for terminology updates
6. Document mapping decisions
7. Regular code reviews

## Quality Metrics

### Terminology Quality
- **Concept completeness** - All required concepts present
- **Relationship accuracy** - Relationships reflect reality
- **Definition clarity** - Clear human-readable definitions
- **Consistency** - Uniform structure and patterns

### Implementation Quality
- **Code validation** - Verify against official SNOMED CT
- **Value set accuracy** - Correct concepts in value sets
- **Mapping accuracy** - Correct cross-mappings
- **Update frequency** - Current with latest releases

## Tools and Resources

| Tool | Purpose | Access |
|------|---------|--------|
| SNOMED CT Browser | Web-based browsing | snomed.org |
| Snowstorm | Terminology Server | GitHub (open source) |
| SNOMED Web API | REST access | SNOMED International |
| FHIR Terminology Server | FHIR Operations | Various implementations |
| Mapping Utilities | ICD-10/SNOMED mapping | SNOMED/ICD tools |

## Compliance Notes

- **Regulatory requirement** - Mandated in many countries
- **Quality reporting** - Required for CMS reporting
- **Data exchange** - Essential for interoperability
- **Clinical decision support** - Basis for clinical logic
- **Research** - De-identification using SNOMED codes

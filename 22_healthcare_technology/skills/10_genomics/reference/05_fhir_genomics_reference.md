# HL7 FHIR Genomics Standards Reference

## FHIR Genomics Overview

The FHIR Genomics Implementation Guide provides standardized representations of genomic data for clinical and research use. This enables interoperability across EHRs, laboratories, and genomic analysis platforms.

## Core FHIR Genomic Resources

### Observation Resource (Genomics Extensions)
**Base Resource**: FHIR Observation with genomic extensions.

**Key Elements**:
```
Observation {
  id: unique identifier,
  status: registered | preliminary | final | amended | cancelled,
  category: laboratory | vital-signs | imaging,
  code: What was observed (LOINC code for genomic test),
  subject: Patient reference,
  effectiveDateTime: When observation occurred,
  value: Result (often component elements),
  component: [
    {
      code: Specific genomic component,
      value: Component result
    }
  ],
  method: Sequencing methodology,
  specimen: Reference to specimen used,
  issued: When result released,
  interpretation: Pathogenic | likely-pathogenic | VUS | likely-benign | benign,
  note: Clinical interpretation details
}
```

**Genomic-Specific Extensions**:
- `genomics-assembly`: GRCh37 or GRCh38 reference assembly
- `genomics-referenceAllele`: Expected allele at position
- `genomics-alternateAllele`: Observed variant allele
- `genomics-phasing`: Phase information for multiple variants
- `genomics-sequencingBasis`: Basis for called variant
- `genomics-variantKey`: Unique variant identifier

### Variant Resource
**Custom Genomics Resource**: Detailed genetic variant representation.

**Key Elements**:
```
Variant {
  id: Unique variant ID,
  patient: Patient reference,
  sequenceRepository: clinvar | genetic-home-reference,
  refSeqID: RefSeq identifier (NM_*),
  proteinContext: Protein-level consequence,
  variantType: single-nucleotide | deletion | insertion | substitution | indel,
  start: Position of variant (0-based),
  end: End position for insertions/deletions,
  referenceAllele: Reference base(s),
  alternateAllele: Alternate base(s),
  genomicCoordinates: Chromosome:position format,
  hgvs: HGVS nomenclature,
  molecularEffect: missense | frameshift | nonsense | splicing,
  clinicalSignificance: Pathogenic | likely-pathogenic | VUS | likely-benign | benign,
  confidence: High | medium | low,
  source: Database of origin,
  phenotype: Associated clinical condition,
  zygosity: homozygous | heterozygous | hemizygous,
  inheritance: autosomal | x-linked | mitochondrial
}
```

### MolecularSequence Resource
**Purpose**: Standardized representation of nucleotide or protein sequences.

**Key Elements**:
```
MolecularSequence {
  id: Unique identifier,
  type: dna | rna | aa,
  coordinateSystem: 0-based (GRCh38, standard) | 1-based (legacy),
  patient: Patient reference,
  specimen: Reference to biological specimen,
  referenceSeq: {
    chromosome: Chromosome (e.g., "1"),
    genomicBuild: GRCh38 | GRCh37,
    orientation: sense | antisense,
    referenceSeqId: RefSeq ID,
    referenceSeqPointer: Genome position,
    windowStart: Start of sequence window,
    windowEnd: End of sequence window
  },
  variant: [
    {
      start: Start position,
      end: End position,
      observedAllele: What was observed,
      referenceAllele: What is expected,
      cigar: Compact Idempotent Genome Alignment Report
    }
  ],
  quality: [
    {
      type: indel | snp | unknown,
      standardSequence: Truth variant,
      querySequence: Called variant,
      method: Comparison method,
      truthTP: True positives,
      queryTP: Called true positives,
      truthFN: False negatives,
      sensitivity: Sensitivity metric,
      precision: Precision metric
    }
  ],
  repository: [
    {
      type: directlink | login | oauth | other,
      url: Repository URL,
      name: Repository name,
      db: Specific database (e.g., "clinvar", "cosmic")
    }
  ]
}
```

### Specimen Resource
**Purpose**: Biological material used for genomic testing.

**Key Elements**:
```
Specimen {
  id: Unique specimen ID,
  identifier: Lab-specific ID,
  status: available | unavailable | unsatisfactory | entered-in-error,
  type: Tissue type (SNOMED code),
  subject: Patient reference,
  receivedTime: When specimen received,
  collection: {
    collector: Who collected,
    collectedDateTime: When collected,
    bodySite: Site of collection (SNOMED),
    method: Collection method (venipuncture, etc.),
    quantity: Volume collected
  },
  processing: [
    {
      description: Processing details,
      procedure: Processing type,
      additive: Preservative/additive used,
      timeDateTime: When processed
    }
  ],
  container: [
    {
      identifier: Container ID,
      description: Type of container,
      type: Container type,
      capacity: Container volume,
      specimenQuantity: Amount in container
    }
  ],
  note: Additional collection notes
}
```

### DiagnosticReport Resource
**Purpose**: Overall genomic test report with interpreted results.

**Key Elements**:
```
DiagnosticReport {
  id: Unique report ID,
  identifier: Lab report number,
  basedOn: Genomic test order reference,
  status: registered | partial | preliminary | final | amended | corrected | cancelled,
  category: laboratory,
  code: Test code (LOINC for genomic panel),
  subject: Patient reference,
  issued: Date report issued,
  performer: Ordering provider/lab,
  resultsInterpreter: Pathologist/geneticist,
  specimen: References to specimens analyzed,
  result: [
    Observation references (individual findings)
  ],
  conclusion: Narrative interpretation,
  conclusionCode: Final interpretation code,
  imagingStudy: Any related imaging,
  media: Supplementary images/data,
  presentedForm: PDF report attachment
}
```

## FHIR Genomics Implementation Patterns

### Pattern 1: Simple Variant Report
**Use Case**: Single variant with interpretation.

**Resources**:
1. **DiagnosticReport**: Container for test
2. **Observation**: Variant finding with:
   - `code`: LOINC code for variant analysis
   - `component`: Individual components (chromosome, position, variant, etc.)
   - `interpretation`: Pathogenic/benign classification
3. **MolecularSequence**: Reference sequence context
4. **Specimen**: Source biological material
5. **Patient**: Subject of test

### Pattern 2: Multi-Gene Panel Report
**Use Case**: Panel testing for hereditary cancer syndrome.

**Resources**:
1. **DiagnosticReport**: Comprehensive panel report
2. **Multiple Observations**: One per gene/region:
   - Detected variants with interpretations
   - Genes analyzed without findings
   - Quality metrics per region
3. **MolecularSequence**: Reference for each variant
4. **Specimen**: Single specimen for panel
5. **Patient**: Subject

### Pattern 3: Somatic Tumor Genomics
**Use Case**: Cancer genomic profiling.

**Resources**:
1. **DiagnosticReport**: Tumor profile summary
2. **Observations**:
   - Driver mutations (actionable)
   - TMB score with interpretation
   - MSI status
   - Copy number changes
3. **Condition**: Cancer diagnosis linked
4. **MedicationStatement**: Current treatments
5. **Specimen**: Tumor sample

### Pattern 4: Pharmacogenomics Report
**Use Case**: Drug metabolism genetic profile.

**Resources**:
1. **DiagnosticReport**: PGx phenotype summary
2. **Observations**: One per gene:
   - **Component 1**: Genotype (allele names)
   - **Component 2**: Phenotype (PM/IM/NM)
   - **Component 3**: Drug metabolism (high/normal/low)
   - **Interpretation**: Clinical recommendation
3. **MedicationStatement**: Drugs for which recommendations apply

## HGVS Nomenclature in FHIR

### Integration in MolecularSequence
**HGVS String Representation**:
```json
{
  "url": "http://hl7.org/fhir/StructureDefinition/molecularsequence-hgvs",
  "valueCodeableConcept": {
    "coding": [{
      "system": "http://varnomen.hgvs.org/",
      "code": "NM_007294.4:c.68_69delAG",
      "display": "BRCA1 c.68_69delAG"
    }]
  }
}
```

### Using SPDI Format
**FHIR SPDI Extension**:
```json
{
  "url": "http://hl7.org/fhir/StructureDefinition/vcf-spdi",
  "valueCodeableConcept": {
    "coding": [{
      "system": "http://example.com/vcf",
      "code": "NC_000013.11:32889611:G:A"
    }]
  }
}
```

## FHIR Genomics Query Patterns

### RESTful API Query Examples

**Query by Patient**:
```
GET /Observation?subject=Patient/123&category=laboratory
```

**Query by Variant**:
```
GET /MolecularSequence?chromosome=13&start=32889611&end=32889612
```

**Query by Gene**:
```
GET /DiagnosticReport?code=LOINC:TBD&subject=Patient/456
```

**Query by Interpretation**:
```
GET /Observation?interpretation=pathogenic&subject=Patient/789
```

## FHIR Genomics Limitations & Extensions

### Current Limitations
1. **Complex Variants**: Difficult to represent complex rearrangements
2. **Batch Reporting**: Not optimized for large-scale genomic data
3. **Quality Metrics**: Limited standardized quality score representation
4. **Bioinformatics Metadata**: Analysis tool/version provenance incomplete
5. **Copy Number**: CNV representation less developed than SNVs

### Extensions for Enhanced Representation

**Custom Extension: Variant Classification Details**
```
{
  "url": "http://example.com/fhir/StructureDefinition/variant-classification",
  "extension": [
    {
      "url": "pathogenicity-score",
      "valueDecimal": 0.92
    },
    {
      "url": "acmg-criteria",
      "valueString": "PVS1, PS1"
    },
    {
      "url": "evidence-level",
      "valueCode": "level-a"
    }
  ]
}
```

**Custom Extension: Sequencing Metadata**
```
{
  "url": "http://example.com/fhir/StructureDefinition/sequencing-metadata",
  "extension": [
    {
      "url": "platform",
      "valueString": "Illumina NovaSeq"
    },
    {
      "url": "read-length",
      "valueInteger": 150
    },
    {
      "url": "mean-coverage",
      "valueDecimal": 250.5
    },
    {
      "url": "pipeline-version",
      "valueString": "BWA-0.7.17, GATK-4.2.0"
    }
  ]
}
```

## Data Security & Privacy in FHIR Genomics

### HIPAA Considerations
1. **De-identification**: Remove direct identifiers from shared genomic data
2. **Consent Management**: Track explicit consent for genetic testing and result return
3. **Audit Logging**: Log all access to genomic findings
4. **Encryption**: Transport layer security (TLS 1.2+) for all genomic data

### FHIR Security Framework
- **OAuth 2.0**: Access token-based authentication
- **SMART on FHIR**: Standardized authorization for genomic apps
- **Audit Events**: FHIR AuditEvent resource tracking access

### Genomic-Specific Considerations
1. **Aggregate Genomic Data**: Can identify populations even if de-identified
2. **Secondary Findings**: Explicit consent needed for incidental discoveries
3. **Family Implications**: Genetic findings affect relatives (not just proband)
4. **Consent Withdrawal**: Challenging to revoke shared genomic data

## Integration with Clinical Workflows

### EHR Integration
1. **Test Ordering**: EHR generates DiagnosticReport order
2. **Specimen Handling**: Track specimen through lab LIS
3. **Result Receipt**: Lab pushes results via FHIR API
4. **Clinical Review**: Provider review and action in EHR
5. **Patient Portal**: Secure result delivery to patient

### Clinical Decision Support
1. **Medication Recommendations**: PGx results integrated with e-prescribing
2. **Treatment Planning**: Cancer genomics inform oncology workflows
3. **Family Screening**: Hereditary findings trigger cascade screening
4. **Risk Stratification**: Genomic risk scores inform prevention

## FHIR Genomics Profile Examples

### Genetics Profile for Inherited Variants
```
Profile: GeneticVariantReport
Base: DiagnosticReport

Elements:
- category.fixed = "laboratory"
- code.binding = {LOINC:47000 or related}
- result.type = "Observation" with genetics extensions
- specimen.type = "whole blood" or "saliva"
```

### Profile for Somatic Cancer Variants
```
Profile: SomaticTumorGenomicsReport
Base: DiagnosticReport

Elements:
- category.fixed = "laboratory"
- code.binding = {LOINC:tumor-profiling-codes}
- result.interpretation = "pathogenic" or "actionable"
- specimen.type = "malignant tissue"
- basedOn = CancerStaging/Treatment references
```

## Genomic Data Exchange Standards

### GA4GH (Global Alliance for Genomics & Health)
**Standards Complementary to FHIR**:
- **VRS (Variant Representation Specification)**: Standardized variant representation
- **SEQR (Sequence Reporting)**: Clinical evidence code structures
- **PharmCAT (Pharmacogenomics Clinical Annotation Tools)**: PGx standardization

### Integration Approach
1. Use GA4GH VRS for variant normalization
2. Represent in FHIR using HGVS/SPDI formats
3. Include GA4GH-derived evidence codes
4. Maintain mapping between standards

## Best Practices for FHIR Genomics Implementation

1. **Use Appropriate Reference Assemblies**: Document GRCh37 vs. GRCh38 clearly
2. **Normalize Nomenclature**: Convert all variants to HGVS format
3. **Include Quality Metrics**: Report sequencing depth, VAF, confidence
4. **Capture Interpretation**: ACMG classification, clinical significance
5. **Preserve Provenance**: Document analysis tools, versions, dates
6. **Maintain Linkage**: Connect variants to Specimen, Patient, Condition
7. **Support Scalability**: Plan for large-scale genomic data exchange
8. **Version Control**: Track FHIR profile versions and evolutionary changes

## Real-World FHIR Genomics Example

```json
{
  "resourceType": "DiagnosticReport",
  "id": "genomics-001",
  "basedOn": [{
    "reference": "ServiceRequest/order-123"
  }],
  "status": "final",
  "category": [{
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
      "code": "GE"
    }]
  }],
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "55233-1",
      "display": "Genetic tests code panel"
    }]
  },
  "subject": {
    "reference": "Patient/patient-123"
  },
  "issued": "2024-01-15T10:30:00Z",
  "performer": [{
    "reference": "Organization/genomics-lab-123"
  }],
  "specimen": [{
    "reference": "Specimen/specimen-001"
  }],
  "result": [{
    "reference": "Observation/variant-brca1-001"
  }],
  "conclusion": "Likely pathogenic BRCA1 mutation detected. Recommend genetic counseling and family screening."
}
```

"""
FHIR Genomics Builder
Converts genomic variant data to FHIR Genomics resources (Observation, DiagnosticReport, etc.)
"""

from fhir.resources.observation import Observation
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.specimen import Specimen
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference
from datetime import datetime
from typing import List, Dict, Optional

class FHIRGenomicsBuilder:
    """Build FHIR Genomics resources from variant data"""

    def __init__(self):
        self.loinc_codes = {
            'variant': '69548-6',  # Genetic variant assessment
            'dna_change': '48004-6',  # DNA change (c.HGVS)
            'amino_acid_change': '48005-3',  # Amino acid change (p.HGVS)
            'allelic_frequency': '81258-6',  # Allelic frequency
            'genomic_ref_sequence': '48013-7',  # Genomic reference sequence ID
            'gene': '48018-6',  # Gene studied
            'cytogenetic_location': '48001-2',  # Cytogenetic location
            'interpretation': '53037-8',  # Clinical significance
        }

    def create_variant_observation(self, variant_data: Dict, patient_id: str,
                                   specimen_id: str = None) -> Observation:
        """Create FHIR Observation resource for a genomic variant"""

        observation = Observation(
            id=f"variant-{variant_data['id']}",
            status="final",
            category=[CodeableConcept(
                coding=[Coding(
                    system="http://terminology.hl7.org/CodeSystem/observation-category",
                    code="laboratory",
                    display="Laboratory"
                )]
            )],
            code=CodeableConcept(
                coding=[Coding(
                    system="http://loinc.org",
                    code=self.loinc_codes['variant'],
                    display="Genetic variant assessment"
                )]
            ),
            subject=Reference(reference=f"Patient/{patient_id}"),
            effectiveDateTime=datetime.now().isoformat(),
            issued=datetime.now().isoformat(),
            component=[]
        )

        # Add specimen reference if provided
        if specimen_id:
            observation.specimen = Reference(reference=f"Specimen/{specimen_id}")

        # Add gene component
        if 'gene' in variant_data:
            observation.component.append({
                "code": CodeableConcept(
                    coding=[Coding(
                        system="http://loinc.org",
                        code=self.loinc_codes['gene'],
                        display="Gene studied"
                    )]
                ),
                "valueCodeableConcept": CodeableConcept(
                    coding=[Coding(
                        system="http://www.genenames.org/geneId",
                        code=variant_data['gene'],
                        display=variant_data['gene']
                    )]
                )
            })

        # Add DNA change (c.HGVS)
        if 'hgvs_c' in variant_data:
            observation.component.append({
                "code": CodeableConcept(
                    coding=[Coding(
                        system="http://loinc.org",
                        code=self.loinc_codes['dna_change'],
                        display="DNA change (c.HGVS)"
                    )]
                ),
                "valueCodeableConcept": CodeableConcept(
                    text=variant_data['hgvs_c']
                )
            })

        # Add amino acid change (p.HGVS)
        if 'hgvs_p' in variant_data:
            observation.component.append({
                "code": CodeableConcept(
                    coding=[Coding(
                        system="http://loinc.org",
                        code=self.loinc_codes['amino_acid_change'],
                        display="Amino acid change (p.HGVS)"
                    )]
                ),
                "valueCodeableConcept": CodeableConcept(
                    text=variant_data['hgvs_p']
                )
            })

        # Add allelic frequency (VAF)
        if 'vaf' in variant_data:
            observation.component.append({
                "code": CodeableConcept(
                    coding=[Coding(
                        system="http://loinc.org",
                        code=self.loinc_codes['allelic_frequency'],
                        display="Allelic frequency"
                    )]
                ),
                "valueQuantity": Quantity(
                    value=variant_data['vaf'],
                    unit="%",
                    system="http://unitsofmeasure.org",
                    code="%"
                )
            })

        # Add genomic reference sequence
        if 'transcript' in variant_data:
            observation.component.append({
                "code": CodeableConcept(
                    coding=[Coding(
                        system="http://loinc.org",
                        code=self.loinc_codes['genomic_ref_sequence'],
                        display="Genomic reference sequence ID"
                    )]
                ),
                "valueCodeableConcept": CodeableConcept(
                    coding=[Coding(
                        system="http://www.ncbi.nlm.nih.gov/refseq",
                        code=variant_data['transcript']
                    )]
                )
            })

        # Add clinical significance
        if 'clinical_significance' in variant_data:
            observation.interpretation = [CodeableConcept(
                coding=[Coding(
                    system="http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    code=self.map_clinical_significance(variant_data['clinical_significance']),
                    display=variant_data['clinical_significance']
                )]
            )]

        return observation

    def create_genomic_diagnostic_report(self, patient_id: str, variants: List[Dict],
                                        test_info: Dict) -> DiagnosticReport:
        """Create FHIR DiagnosticReport for genomic test results"""

        report = DiagnosticReport(
            id=f"genomic-report-{test_info['id']}",
            status="final",
            category=[CodeableConcept(
                coding=[Coding(
                    system="http://terminology.hl7.org/CodeSystem/v2-0074",
                    code="GE",
                    display="Genetics"
                )]
            )],
            code=CodeableConcept(
                coding=[Coding(
                    system="http://loinc.org",
                    code="81247-9",
                    display="Master HL7 genetic variant reporting panel"
                )]
            ),
            subject=Reference(reference=f"Patient/{patient_id}"),
            effectiveDateTime=test_info.get('test_date', datetime.now().isoformat()),
            issued=datetime.now().isoformat(),
            result=[],
            conclusion=test_info.get('conclusion', '')
        )

        # Add references to variant observations
        for variant in variants:
            report.result.append(
                Reference(reference=f"Observation/variant-{variant['id']}")
            )

        # Add performer if available
        if 'lab' in test_info:
            report.performer = [Reference(
                display=test_info['lab']
            )]

        # Add specimen if available
        if 'specimen_id' in test_info:
            report.specimen = [Reference(
                reference=f"Specimen/{test_info['specimen_id']}"
            )]

        return report

    def create_specimen_resource(self, specimen_data: Dict, patient_id: str) -> Specimen:
        """Create FHIR Specimen resource"""

        specimen = Specimen(
            id=specimen_data['id'],
            type=CodeableConcept(
                coding=[Coding(
                    system="http://terminology.hl7.org/CodeSystem/v2-0487",
                    code=specimen_data.get('type_code', 'TUMOR'),
                    display=specimen_data.get('type', 'Tumor tissue')
                )]
            ),
            subject=Reference(reference=f"Patient/{patient_id}"),
            collection={
                "collectedDateTime": specimen_data.get('collection_date', datetime.now().isoformat())
            }
        )

        # Add processing information
        if 'processing' in specimen_data:
            specimen.processing = [{
                "description": specimen_data['processing'],
                "timeDateTime": specimen_data.get('processing_date')
            }]

        return specimen

    def map_clinical_significance(self, significance: str) -> str:
        """Map clinical significance to FHIR interpretation codes"""
        mapping = {
            'Pathogenic': 'A',  # Abnormal
            'Likely pathogenic': 'A',
            'Uncertain significance': 'IND',  # Indeterminate
            'VUS': 'IND',
            'Likely benign': 'N',  # Normal
            'Benign': 'N'
        }
        return mapping.get(significance, 'IND')

    def create_pharmacogenomic_observation(self, pgx_data: Dict, patient_id: str) -> Observation:
        """Create pharmacogenomic observation (e.g., CYP2C19 genotype)"""

        observation = Observation(
            id=f"pgx-{pgx_data['gene']}-{pgx_data['id']}",
            status="final",
            category=[CodeableConcept(
                coding=[Coding(
                    system="http://terminology.hl7.org/CodeSystem/observation-category",
                    code="laboratory",
                    display="Laboratory"
                )]
            )],
            code=CodeableConcept(
                coding=[Coding(
                    system="http://loinc.org",
                    code="79716-7",  # Pharmacogenomic result
                    display="Pharmacogenomic result"
                )]
            ),
            subject=Reference(reference=f"Patient/{patient_id}"),
            effectiveDateTime=datetime.now().isoformat(),
            component=[]
        )

        # Add gene
        observation.component.append({
            "code": CodeableConcept(
                coding=[Coding(
                    system="http://loinc.org",
                    code="48018-6",
                    display="Gene studied"
                )]
            ),
            "valueCodeableConcept": CodeableConcept(
                coding=[Coding(
                    system="http://www.genenames.org/geneId",
                    code=pgx_data['gene']
                )]
            )
        })

        # Add diplotype
        if 'diplotype' in pgx_data:
            observation.component.append({
                "code": CodeableConcept(
                    coding=[Coding(
                        system="http://loinc.org",
                        code="84413-4",  # Genotype diplotype
                        display="Genotype diplotype"
                    )]
                ),
                "valueCodeableConcept": CodeableConcept(
                    text=pgx_data['diplotype']
                )
            })

        # Add phenotype
        if 'phenotype' in pgx_data:
            observation.component.append({
                "code": CodeableConcept(
                    coding=[Coding(
                        system="http://loinc.org",
                        code="79724-1",  # Predicted phenotype
                        display="Predicted phenotype"
                    )]
                ),
                "valueCodeableConcept": CodeableConcept(
                    text=pgx_data['phenotype']
                )
            })

        # Add drug implications
        if 'drug_recommendations' in pgx_data:
            observation.note = [{
                "text": f"Drug recommendations: {pgx_data['drug_recommendations']}"
            }]

        return observation

    def bundle_genomic_resources(self, resources: List) -> Dict:
        """Bundle multiple FHIR genomics resources"""
        bundle = {
            "resourceType": "Bundle",
            "type": "transaction",
            "entry": []
        }

        for resource in resources:
            bundle["entry"].append({
                "resource": resource.dict(),
                "request": {
                    "method": "POST",
                    "url": resource.resource_type
                }
            })

        return bundle

if __name__ == "__main__":
    # Example usage
    builder = FHIRGenomicsBuilder()

    variant = {
        'id': '12345',
        'gene': 'BRCA1',
        'hgvs_c': 'c.68_69delAG',
        'hgvs_p': 'p.Glu23ValfsX17',
        'transcript': 'NM_007294.3',
        'vaf': 45.2,
        'clinical_significance': 'Pathogenic'
    }

    observation = builder.create_variant_observation(variant, 'patient-123', 'specimen-456')
    print(f"Created FHIR Observation: {observation.id}")

    # Create diagnostic report
    test_info = {
        'id': 'test-789',
        'test_date': '2024-01-15',
        'lab': 'Genomics Lab Inc.',
        'conclusion': 'Pathogenic BRCA1 variant detected'
    }

    report = builder.create_genomic_diagnostic_report('patient-123', [variant], test_info)
    print(f"Created FHIR DiagnosticReport: {report.id}")

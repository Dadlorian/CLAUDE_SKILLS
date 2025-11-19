#!/usr/bin/env python3
"""
Pharmacogenomics Phenotype Assignment
Maps genotypes to metabolizer phenotypes and drug recommendations.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class Phenotype(Enum):
    POOR = "Poor Metabolizer"
    INTERMEDIATE = "Intermediate Metabolizer"
    NORMAL = "Normal Metabolizer"
    RAPID = "Rapid Metabolizer"
    ULTRARAPID = "Ultra-Rapid Metabolizer"


@dataclass
class DrugRecommendation:
    drug_name: str
    recommendation: str
    evidence_level: str  # A, B, C
    dose_adjustment: str


class PharmaGenotyper:
    """Assigns phenotypes and drug recommendations based on genotypes."""

    # CYP2D6 allele activity scores
    CYP2D6_ACTIVITY = {
        '*1': 1.0,  # Normal function
        '*2': 1.0,  # Normal function
        '*3': 0.0,  # Non-functional
        '*4': 0.0,  # Non-functional
        '*5': 0.0,  # Deletion
        '*10': 0.5,  # Reduced function
        '*41': 0.5,  # Reduced function
    }

    # CYP2C19 allele activity scores
    CYP2C19_ACTIVITY = {
        '*1': 1.0,   # Normal
        '*2': 0.0,   # Non-functional
        '*3': 0.0,   # Non-functional
        '*17': 1.5,  # Increased function
    }

    # TPMT allele activity levels (% activity)
    TPMT_ACTIVITY = {
        '*1A': 1.0,
        '*1B': 1.0,
        '*1C': 1.0,
        '*2': 0.0,
        '*3A': 0.0,
        '*3B': 0.0,
        '*3C': 0.0,
    }

    def __init__(self):
        self.drug_database = self._load_drug_recommendations()

    def _load_drug_recommendations(self) -> Dict:
        """Load drug-gene interaction recommendations."""
        return {
            'CYP2D6': {
                'codeine': {
                    'POOR': ('Avoid', 'No efficacy', 'A', 'Select alternative'),
                    'INTERMEDIATE': ('Consider alternative', 'Reduced efficacy', 'B', 'Monitor'),
                    'NORMAL': ('Standard dosing', 'Expected efficacy', 'A', 'Standard'),
                    'RAPID': ('Standard dosing', 'Expected efficacy', 'A', 'Standard'),
                    'ULTRARAPID': ('Avoid', 'Risk of toxicity', 'B', 'Select alternative'),
                },
                'tamoxifen': {
                    'POOR': ('Consider alternative', 'Reduced efficacy', 'B', 'Monitor response'),
                    'INTERMEDIATE': ('Consider alternative', 'Reduced efficacy', 'B', 'Monitor'),
                    'NORMAL': ('Standard dosing', 'Expected benefit', 'A', 'Standard'),
                    'RAPID': ('Standard dosing', 'Expected benefit', 'A', 'Standard'),
                    'ULTRARAPID': ('Standard dosing', 'Expected benefit', 'B', 'Standard'),
                },
            },
            'CYP2C19': {
                'clopidogrel': {
                    'POOR': ('Alternative P2Y12 inhibitor', 'High risk thrombosis', 'A', 'Avoid'),
                    'INTERMEDIATE': ('Alternative P2Y12 inhibitor', 'Reduced activation', 'B', 'Consider alternative'),
                    'NORMAL': ('Standard dosing', 'Expected activation', 'A', 'Standard'),
                    'RAPID': ('Standard dosing', 'Expected activation', 'B', 'Standard'),
                },
                'escitalopram': {
                    'POOR': ('Dose reduction', 'QT prolongation risk', 'A', 'Reduce dose 50%'),
                    'INTERMEDIATE': ('Standard dosing', 'Monitor QTc', 'B', 'Monitor QTc'),
                    'NORMAL': ('Standard dosing', 'Expected levels', 'A', 'Standard'),
                },
            },
            'TPMT': {
                'thiopurine': {
                    'POOR': ('Dose reduction 85-90%', 'Severe toxicity risk', 'A', 'Reduce 85-90%'),
                    'INTERMEDIATE': ('Dose reduction 33-50%', 'Increased toxicity', 'A', 'Reduce 33-50%'),
                    'NORMAL': ('Standard dosing', 'Expected tolerance', 'A', 'Standard'),
                },
            },
        }

    def assign_cyp2d6_phenotype(self, allele1: str, allele2: str) -> Phenotype:
        """Assign CYP2D6 phenotype from genotype."""
        activity1 = self.CYP2D6_ACTIVITY.get(allele1, 1.0)
        activity2 = self.CYP2D6_ACTIVITY.get(allele2, 1.0)
        total_activity = activity1 + activity2

        if total_activity == 0:
            return Phenotype.POOR
        elif total_activity < 1.0:
            return Phenotype.INTERMEDIATE
        elif total_activity <= 1.25:
            return Phenotype.NORMAL
        elif total_activity <= 2.0:
            return Phenotype.RAPID
        else:
            return Phenotype.ULTRARAPID

    def assign_cyp2c19_phenotype(self, allele1: str, allele2: str) -> Phenotype:
        """Assign CYP2C19 phenotype from genotype."""
        activity1 = self.CYP2C19_ACTIVITY.get(allele1, 1.0)
        activity2 = self.CYP2C19_ACTIVITY.get(allele2, 1.0)
        total_activity = activity1 + activity2

        if total_activity == 0:
            return Phenotype.POOR
        elif total_activity < 1.0:
            return Phenotype.INTERMEDIATE
        elif total_activity == 1.0:
            return Phenotype.NORMAL
        elif total_activity > 1.0:
            return Phenotype.RAPID
        return Phenotype.NORMAL

    def assign_tpmt_phenotype(self, allele1: str, allele2: str) -> Phenotype:
        """Assign TPMT phenotype from genotype."""
        activity1 = self.TPMT_ACTIVITY.get(allele1, 1.0)
        activity2 = self.TPMT_ACTIVITY.get(allele2, 1.0)
        total_activity = (activity1 + activity2) / 2.0

        if total_activity < 0.1:
            return Phenotype.POOR
        elif total_activity < 0.8:
            return Phenotype.INTERMEDIATE
        else:
            return Phenotype.NORMAL

    def get_drug_recommendations(self, gene: str, phenotype: Phenotype) -> List[DrugRecommendation]:
        """Get recommendations for drugs affected by genotype."""
        recommendations = []

        if gene not in self.drug_database:
            return recommendations

        for drug, pheno_recs in self.drug_database[gene].items():
            if phenotype in pheno_recs:
                rec_tuple = pheno_recs[phenotype]
                rec = DrugRecommendation(
                    drug_name=drug,
                    recommendation=rec_tuple[0],
                    evidence_level=rec_tuple[2],
                    dose_adjustment=rec_tuple[3]
                )
                recommendations.append(rec)

        return recommendations


---

#!/usr/bin/env python3
"""
Cancer Variant Classification & Actionability Assessment
Classifies somatic variants and determines clinical actionability.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class ActionabilityTier(Enum):
    TIER_1A = "Tier 1A - FDA Approved"
    TIER_1B = "Tier 1B - NCCN Guidelines"
    TIER_2 = "Tier 2 - Clinical Trials"
    TIER_3 = "Tier 3 - Research"


@dataclass
class ActionableFinding:
    gene: str
    variant: str
    cancer_type: str
    therapy: str
    tier: ActionabilityTier
    evidence: str
    fda_approval_date: str = ""


class CancerVariantClassifier:
    """Classifies cancer variants for treatment implications."""

    # TIER 1A: FDA-approved biomarker-therapy pairs
    TIER_1A_FINDINGS = {
        ('HER2', 'breast'): {
            'therapy': 'Trastuzumab',
            'evidence': 'FDA approval 1998, Phase III trials',
        },
        ('EGFR', 'lung'): {
            'therapy': 'Gefitinib/Erlotinib',
            'evidence': 'FDA approval 2004',
        },
        ('BRAF_V600E', 'melanoma'): {
            'therapy': 'Vemurafenib + Trametinib',
            'evidence': 'FDA approval 2011',
        },
        ('ABL_BCR', 'cml'): {
            'therapy': 'Imatinib',
            'evidence': 'FDA approval 2001, groundbreaking',
        },
    }

    # TIER 1B: NCCN guideline recommendations
    TIER_1B_FINDINGS = {
        ('ALK', 'lung'): {
            'therapy': 'ALK inhibitors (Crizotinib)',
            'evidence': 'NCCN guideline 2015+',
        },
        ('ROS1', 'lung'): {
            'therapy': 'Crizotinib',
            'evidence': 'NCCN guideline 2015+',
        },
        ('KRAS_WT', 'colorectal'): {
            'therapy': 'EGFR inhibitor',
            'evidence': 'NCCN guideline',
        },
    }

    # TIER 2: Clinical trials available
    TIER_2_FINDINGS = {
        ('KRAS_G12C', 'lung'): {
            'therapy': 'Sotorasib',
            'evidence': 'Clinical trials 2021+',
        },
        ('NTRK', 'multiple'): {
            'therapy': 'Larotrectinib',
            'evidence': 'Basket trial LOXO-101',
        },
    }

    # Resistance mutations
    RESISTANCE_MUTATIONS = {
        ('EGFR', 'T790M'): 'Acquired resistance to 1st-gen EGFR TKIs',
        ('ALK', 'G1269A'): 'Resistance to multiple ALK inhibitors',
        ('BRAF', 'secondary'): 'Resistance to vemurafenib',
    }

    def classify_variant(self, gene: str, variant: str, cancer_type: str) -> ActionableFinding:
        """Classify variant for actionability."""
        
        # Check Tier 1A
        key = (gene, cancer_type)
        if key in self.TIER_1A_FINDINGS:
            data = self.TIER_1A_FINDINGS[key]
            return ActionableFinding(
                gene=gene,
                variant=variant,
                cancer_type=cancer_type,
                therapy=data['therapy'],
                tier=ActionabilityTier.TIER_1A,
                evidence=data['evidence'],
            )

        # Check Tier 1B
        if key in self.TIER_1B_FINDINGS:
            data = self.TIER_1B_FINDINGS[key]
            return ActionableFinding(
                gene=gene,
                variant=variant,
                cancer_type=cancer_type,
                therapy=data['therapy'],
                tier=ActionabilityTier.TIER_1B,
                evidence=data['evidence'],
            )

        # Check Tier 2
        if key in self.TIER_2_FINDINGS:
            data = self.TIER_2_FINDINGS[key]
            return ActionableFinding(
                gene=gene,
                variant=variant,
                cancer_type=cancer_type,
                therapy=data['therapy'],
                tier=ActionabilityTier.TIER_2,
                evidence=data['evidence'],
            )

        # Default: Research only
        return ActionableFinding(
            gene=gene,
            variant=variant,
            cancer_type=cancer_type,
            therapy='Unknown',
            tier=ActionabilityTier.TIER_3,
            evidence='Limited clinical data',
        )

    def get_resistance_info(self, gene: str, variant: str) -> str:
        """Check if variant represents resistance mutation."""
        key = (gene, variant)
        return self.RESISTANCE_MUTATIONS.get(key, "No known resistance mechanism")


---

#!/usr/bin/env python3
"""
FHIR Genomics Data Structure Builder
Creates FHIR-compliant genomic data objects.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class FHIRObservation:
    """FHIR Observation resource for genomic findings."""
    resourceType: str = "Observation"
    id: str = ""
    status: str = "final"  # registered, preliminary, final, amended
    category: List[Dict] = None
    code: Dict = None
    subject: Dict = None  # Patient reference
    effectiveDateTime: str = ""
    performer: List[Dict] = None
    value: Dict = None
    interpretation: List[Dict] = None
    method: str = ""
    specimen: Dict = None
    issued: str = ""
    component: List[Dict] = None

    def __post_init__(self):
        if self.effectiveDateTime == "":
            self.effectiveDateTime = datetime.now().isoformat()
        if self.issued == "":
            self.issued = datetime.now().isoformat()


@dataclass
class FHIRMolecularSequence:
    """FHIR MolecularSequence resource for variant details."""
    resourceType: str = "MolecularSequence"
    id: str = ""
    type: str = "dna"
    coordinateSystem: int = 0  # 0-based
    patient: Dict = None
    specimen: Dict = None
    referenceSeq: Dict = None
    variant: List[Dict] = None
    quality: List[Dict] = None


class FHIRGenomicsBuilder:
    """Builds FHIR-compliant genomic data structures."""

    @staticmethod
    def create_variant_observation(
        observation_id: str,
        patient_id: str,
        gene: str,
        hgvs: str,
        classification: str,
        interpretation_code: str
    ) -> FHIRObservation:
        """Create FHIR Observation for genetic variant."""
        
        obs = FHIRObservation(
            id=observation_id,
            status="final",
            category=[{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "laboratory"
                }]
            }],
            code={
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "48005-3",
                    "display": "Genetic variant"
                }]
            },
            subject={"reference": f"Patient/{patient_id}"},
            interpretation=[{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0078",
                    "code": interpretation_code,  # POS, NEG, Ind, etc.
                    "display": classification
                }]
            }],
            component=[
                {
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "48018-6",
                            "display": "Gene"
                        }]
                    },
                    "valueCodeableConcept": {
                        "coding": [{
                            "system": "http://www.genenames.org",
                            "code": gene
                        }]
                    }
                },
                {
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "81290-9",
                            "display": "HGVS"
                        }]
                    },
                    "valueCodeableConcept": {
                        "text": hgvs
                    }
                }
            ]
        )
        return obs

    @staticmethod
    def create_molecular_sequence(
        seq_id: str,
        patient_id: str,
        chrom: str,
        position: int,
        ref: str,
        alt: str
    ) -> FHIRMolecularSequence:
        """Create FHIR MolecularSequence for variant details."""
        
        seq = FHIRMolecularSequence(
            id=seq_id,
            type="dna",
            coordinateSystem=0,
            patient={"reference": f"Patient/{patient_id}"},
            referenceSeq={
                "chromosome": chrom,
                "genomicBuild": "GRCh38",
                "orientation": "sense",
                "referenceSeqId": f"NC_000{chrom}.11"
            },
            variant=[{
                "start": position,
                "end": position + len(ref) - 1,
                "observedAllele": alt,
                "referenceAllele": ref
            }]
        )
        return seq

    @staticmethod
    def to_fhir_json(fhir_obj) -> str:
        """Convert FHIR object to JSON."""
        return json.dumps(asdict(fhir_obj), indent=2, default=str)


"""
Cancer Variant Classifier
Classifies somatic variants according to clinical significance using tiered classification systems
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class ClinicalSignificance(Enum):
    """AMP/ASCO/CAP tier classification for cancer variants"""
    TIER_1A = "Strong clinical significance - FDA approved"
    TIER_1B = "Strong clinical significance - Professional guidelines"
    TIER_2C = "Potential clinical significance - Investigational"
    TIER_2D = "Potential clinical significance - Preclinical"
    TIER_3 = "Uncertain clinical significance"
    TIER_4 = "Benign or likely benign"

class EvidenceLevel(Enum):
    """Level of evidence for variant-drug associations"""
    A = "FDA approved biomarker"
    B = "Clinical guideline recommendation"
    C = "Clinical trials evidence"
    D = "Preclinical evidence"

@dataclass
class SomaticVariant:
    """Somatic variant in cancer context"""
    chromosome: str
    position: int
    reference: str
    alternate: str
    gene: str
    transcript: str
    hgvs_c: str
    hgvs_p: str
    variant_allele_frequency: float
    read_depth: int
    variant_type: str
    effect: str

@dataclass
class CancerVariantClassification:
    """Classification result for cancer variant"""
    variant: SomaticVariant
    tier: ClinicalSignificance
    evidence_level: EvidenceLevel
    therapeutic_implications: List[Dict]
    diagnostic_implications: List[Dict]
    prognostic_implications: List[Dict]
    resistance_implications: List[Dict]
    clinical_trials: List[Dict]
    citations: List[str]

class CancerVariantClassifier:
    """Classify cancer variants for clinical actionability"""

    def __init__(self, cancer_type: str):
        self.cancer_type = cancer_type
        self.knowledge_base = self.load_knowledge_base()
        self.clinical_trials_db = self.load_clinical_trials()

    def classify_variant(self, variant: SomaticVariant) -> CancerVariantClassification:
        """Classify a somatic variant according to clinical guidelines"""
        therapeutic_evidence = self.get_therapeutic_evidence(variant)
        diagnostic_evidence = self.get_diagnostic_evidence(variant)
        prognostic_evidence = self.get_prognostic_evidence(variant)
        resistance_evidence = self.get_resistance_evidence(variant)

        tier = self.determine_tier(therapeutic_evidence, diagnostic_evidence,
                                   prognostic_evidence, self.cancer_type)
        evidence_level = self.determine_evidence_level(therapeutic_evidence, diagnostic_evidence)
        trials = self.find_clinical_trials(variant, self.cancer_type)
        citations = self.collect_citations(therapeutic_evidence, diagnostic_evidence, prognostic_evidence)

        return CancerVariantClassification(
            variant=variant, tier=tier, evidence_level=evidence_level,
            therapeutic_implications=therapeutic_evidence,
            diagnostic_implications=diagnostic_evidence,
            prognostic_implications=prognostic_evidence,
            resistance_implications=resistance_evidence,
            clinical_trials=trials, citations=citations
        )

    def determine_tier(self, therapeutic, diagnostic, prognostic, cancer_type):
        """Determine AMP/ASCO/CAP tier classification"""
        if self.has_fda_approval(therapeutic, cancer_type):
            return ClinicalSignificance.TIER_1A
        if self.in_professional_guidelines(therapeutic, diagnostic, cancer_type):
            return ClinicalSignificance.TIER_1B
        if self.has_clinical_trial_evidence(therapeutic):
            return ClinicalSignificance.TIER_2C
        if self.has_preclinical_evidence(therapeutic):
            return ClinicalSignificance.TIER_2D
        if therapeutic or prognostic:
            return ClinicalSignificance.TIER_3
        return ClinicalSignificance.TIER_4

    def get_therapeutic_evidence(self, variant: SomaticVariant) -> List[Dict]:
        """Query therapeutic databases for variant-drug associations"""
        evidence = []
        evidence.extend(self.query_oncokb(variant, self.cancer_type))
        evidence.extend(self.query_civic(variant, self.cancer_type))
        evidence.extend(self.query_cancer_hotspots(variant))
        return evidence

    def query_oncokb(self, variant: SomaticVariant, cancer_type: str) -> List[Dict]:
        """Query OncoKB for clinical annotations"""
        oncokb_annotations = {
            'BRAF:p.V600E': {
                'melanoma': {
                    'level': 'LEVEL_1',
                    'drugs': ['Vemurafenib', 'Dabrafenib', 'Trametinib'],
                    'fda_approved': True,
                    'citations': ['PMID:21639808', 'PMID:22356324']
                }
            },
            'EGFR:p.L858R': {
                'lung_adenocarcinoma': {
                    'level': 'LEVEL_1',
                    'drugs': ['Osimertinib', 'Erlotinib', 'Gefitinib'],
                    'fda_approved': True,
                    'citations': ['PMID:28619981']
                }
            }
        }
        variant_key = f"{variant.gene}:{variant.hgvs_p}"
        if variant_key in oncokb_annotations and cancer_type.lower() in oncokb_annotations[variant_key]:
            return [oncokb_annotations[variant_key][cancer_type.lower()]]
        return []

    def query_civic(self, variant: SomaticVariant, cancer_type: str) -> List[Dict]:
        """Query CIViC database for clinical interpretations"""
        civic_evidence = []
        if variant.gene == 'KRAS' and variant.hgvs_p in ['p.G12C', 'p.G12D', 'p.G12V']:
            civic_evidence.append({
                'source': 'CIViC',
                'evidence_type': 'Predictive',
                'drugs': ['Sotorasib', 'Adagrasib'] if variant.hgvs_p == 'p.G12C' else [],
                'evidence_level': 'B' if variant.hgvs_p == 'p.G12C' else 'D',
                'description': 'KRAS G12C mutations are targetable',
                'disease': cancer_type,
                'citations': ['PMID:34096690']
            })
        return civic_evidence

    def get_diagnostic_evidence(self, variant: SomaticVariant) -> List[Dict]:
        """Get diagnostic significance"""
        diagnostic_markers = {
            'IDH1': ['Glioma classification'],
            'IDH2': ['Glioma classification', 'AML classification'],
            'BRAF': ['Melanoma diagnosis'],
            'NPM1': ['AML diagnosis']
        }
        if variant.gene in diagnostic_markers:
            return [{'gene': variant.gene, 'diagnostic_use': diagnostic_markers[variant.gene],
                    'evidence_level': 'B'}]
        return []

    def get_prognostic_evidence(self, variant: SomaticVariant) -> List[Dict]:
        """Get prognostic significance"""
        prognostic_variants = {
            'TP53': {'impact': 'Poor prognosis', 'citations': ['PMID:21760636']},
            'BRCA1': {'impact': 'Better response to platinum', 'citations': ['PMID:21245428']}
        }
        if variant.gene in prognostic_variants:
            return [{'gene': variant.gene, 'prognostic_impact': prognostic_variants[variant.gene]['impact'],
                    'citations': prognostic_variants[variant.gene]['citations']}]
        return []

    def get_resistance_evidence(self, variant: SomaticVariant) -> List[Dict]:
        """Get evidence for resistance"""
        resistance_variants = {
            'EGFR:p.T790M': {
                'primary_treatment': ['Erlotinib', 'Gefitinib'],
                'resistance_mechanism': 'Gatekeeper mutation',
                'second_line_options': ['Osimertinib'],
                'citations': ['PMID:16870155']
            }
        }
        variant_key = f"{variant.gene}:{variant.hgvs_p}"
        return [resistance_variants[variant_key]] if variant_key in resistance_variants else []

    def find_clinical_trials(self, variant: SomaticVariant, cancer_type: str) -> List[Dict]:
        """Find relevant clinical trials"""
        trials = []
        if variant.gene == 'KRAS' and variant.hgvs_p == 'p.G12C':
            trials.append({
                'nct_id': 'NCT04185883',
                'title': 'Study of Sotorasib in KRAS G12C-Mutated Cancer',
                'phase': 'Phase 2',
                'status': 'Recruiting'
            })
        return trials

    def has_fda_approval(self, evidence, cancer_type):
        return any(e.get('fda_approved') and e.get('disease', '').lower() == cancer_type.lower()
                  for e in evidence)

    def in_professional_guidelines(self, therapeutic, diagnostic, cancer_type):
        return any(e.get('evidence_level') in ['A', 'B'] for e in therapeutic + diagnostic)

    def has_clinical_trial_evidence(self, evidence):
        return any(e.get('evidence_level') == 'C' for e in evidence)

    def has_preclinical_evidence(self, evidence):
        return any(e.get('evidence_level') == 'D' for e in evidence)

    def determine_evidence_level(self, therapeutic, diagnostic):
        for e in therapeutic + diagnostic:
            if e.get('evidence_level') in ['A', 'LEVEL_1']:
                return EvidenceLevel.A
        for e in therapeutic + diagnostic:
            if e.get('evidence_level') in ['B', 'LEVEL_2']:
                return EvidenceLevel.B
        for e in therapeutic + diagnostic:
            if e.get('evidence_level') in ['C', 'LEVEL_3']:
                return EvidenceLevel.C
        return EvidenceLevel.D

    def collect_citations(self, *evidence_lists):
        citations = set()
        for evidence_list in evidence_lists:
            for evidence in evidence_list:
                if 'citations' in evidence:
                    citations.update(evidence['citations'])
        return sorted(list(citations))

    def load_knowledge_base(self):
        return {}

    def load_clinical_trials(self):
        return {}

    def query_cancer_hotspots(self, variant: SomaticVariant) -> List[Dict]:
        hotspots = {
            'BRAF': ['p.V600E', 'p.V600K'],
            'KRAS': ['p.G12C', 'p.G12D', 'p.G12V'],
            'EGFR': ['p.L858R', 'p.T790M']
        }
        if variant.gene in hotspots and variant.hgvs_p in hotspots[variant.gene]:
            return [{'source': 'Cancer Hotspots', 'is_hotspot': True, 'recurrence': 'High'}]
        return []

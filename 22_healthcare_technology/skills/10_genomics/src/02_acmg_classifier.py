#!/usr/bin/env python3
"""
ACMG Variant Classification System
Implements ACMG 2015 criteria for systematic variant classification.

Production-grade implementation supporting evidence aggregation and reporting.
"""

import logging
from typing import List, Dict, Tuple
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ACMGTier(Enum):
    """ACMG five-tier classification system."""
    PATHOGENIC = "Pathogenic"
    LIKELY_PATHOGENIC = "Likely Pathogenic"
    UNCERTAIN = "Uncertain Significance"
    LIKELY_BENIGN = "Likely Benign"
    BENIGN = "Benign"


class EvidenceStrength(Enum):
    """Strength of supporting evidence for variant classification."""
    VERY_STRONG = "Very Strong"
    STRONG = "Strong"
    MODERATE = "Moderate"
    SUPPORTING = "Supporting"


@dataclass
class ACMGCriterion:
    """Represents a single ACMG criterion application."""
    code: str  # PVS1, PS1, PM1, etc.
    strength: EvidenceStrength
    description: str
    applicable: bool = False
    supporting_evidence: str = ""


@dataclass
class ACMGClassification:
    """Complete ACMG classification for a variant."""
    variant_id: str
    gene: str
    hgvs: str
    classification: ACMGTier
    confidence: float  # 0.0-1.0
    pathogenic_criteria: List[ACMGCriterion] = field(default_factory=list)
    benign_criteria: List[ACMGCriterion] = field(default_factory=list)
    final_assessment: str = ""


class ACMGClassifier:
    """Implements ACMG 2015 variant classification algorithm."""

    # ACMG Criterion definitions
    PATHOGENIC_CRITERIA = {
        'PVS1': {'strength': EvidenceStrength.VERY_STRONG, 'name': 'Null variant'},
        'PS1': {'strength': EvidenceStrength.STRONG, 'name': 'Same amino acid change'},
        'PS2': {'strength': EvidenceStrength.STRONG, 'name': 'De novo (confirmed)'},
        'PS3': {'strength': EvidenceStrength.STRONG, 'name': 'Functional studies LoF'},
        'PS4': {'strength': EvidenceStrength.STRONG, 'name': 'Prevalence difference'},
        'PM1': {'strength': EvidenceStrength.MODERATE, 'name': 'Mutational hotspot'},
        'PM2': {'strength': EvidenceStrength.MODERATE, 'name': 'Absent in databases'},
        'PM3': {'strength': EvidenceStrength.MODERATE, 'name': 'Trans with pathogenic'},
        'PM4': {'strength': EvidenceStrength.MODERATE, 'name': 'Protein length change'},
        'PM5': {'strength': EvidenceStrength.MODERATE, 'name': 'Different nucleotide at same aa'},
        'PM6': {'strength': EvidenceStrength.MODERATE, 'name': 'De novo (unconfirmed)'},
        'PP1': {'strength': EvidenceStrength.SUPPORTING, 'name': 'Cosegregation'},
        'PP2': {'strength': EvidenceStrength.SUPPORTING, 'name': 'Low rate benign missense'},
        'PP3': {'strength': EvidenceStrength.SUPPORTING, 'name': 'Computational evidence'},
        'PP4': {'strength': EvidenceStrength.SUPPORTING, 'name': 'Phenotype-specific'},
        'PP5': {'strength': EvidenceStrength.SUPPORTING, 'name': 'Recent literature'},
    }

    BENIGN_CRITERIA = {
        'BA1': {'strength': EvidenceStrength.VERY_STRONG, 'name': 'High MAF (≥5%)'},
        'BS1': {'strength': EvidenceStrength.STRONG, 'name': 'High MAF for disorder'},
        'BS2': {'strength': EvidenceStrength.STRONG, 'name': 'Homozygous in healthy'},
        'BS3': {'strength': EvidenceStrength.STRONG, 'name': 'Functional studies WT'},
        'BS4': {'strength': EvidenceStrength.STRONG, 'name': 'Lack of segregation'},
        'BP1': {'strength': EvidenceStrength.SUPPORTING, 'name': 'Low rate pathogenic missense'},
        'BP2': {'strength': EvidenceStrength.SUPPORTING, 'name': 'In cis with pathogenic'},
        'BP3': {'strength': EvidenceStrength.SUPPORTING, 'name': 'In-frame indel repeat'},
        'BP4': {'strength': EvidenceStrength.SUPPORTING, 'name': 'No computational support'},
        'BP5': {'strength': EvidenceStrength.SUPPORTING, 'name': 'Phenotype mismatch'},
        'BP6': {'strength': EvidenceStrength.SUPPORTING, 'name': 'Absent in case studies'},
        'BP7': {'strength': EvidenceStrength.SUPPORTING, 'name': 'Synonymous, no splicing'},
    }

    def __init__(self):
        self.pathogenic_counts = {'very_strong': 0, 'strong': 0, 'moderate': 0, 'supporting': 0}
        self.benign_counts = {'very_strong': 0, 'strong': 0, 'moderate': 0, 'supporting': 0}

    def classify(self, variant_id: str, gene: str, hgvs: str,
                 pathogenic_evidence: Dict[str, bool],
                 benign_evidence: Dict[str, bool]) -> ACMGClassification:
        """
        Classify variant using ACMG 2015 criteria.

        Args:
            variant_id: Unique variant identifier
            gene: Gene name
            hgvs: HGVS notation
            pathogenic_evidence: Dict of criterion -> is_applicable
            benign_evidence: Dict of criterion -> is_applicable

        Returns:
            ACMGClassification object with tier assignment
        """
        # Reset counts
        self.pathogenic_counts = {'very_strong': 0, 'strong': 0, 'moderate': 0, 'supporting': 0}
        self.benign_counts = {'very_strong': 0, 'strong': 0, 'moderate': 0, 'supporting': 0}

        # Process pathogenic criteria
        pathogenic_crits = []
        for criterion, applicable in pathogenic_evidence.items():
            if applicable and criterion in self.PATHOGENIC_CRITERIA:
                strength = self.PATHOGENIC_CRITERIA[criterion]['strength']
                self.pathogenic_counts[strength.name.lower()] += 1
                crit = ACMGCriterion(
                    code=criterion,
                    strength=strength,
                    description=self.PATHOGENIC_CRITERIA[criterion]['name'],
                    applicable=True
                )
                pathogenic_crits.append(crit)

        # Process benign criteria
        benign_crits = []
        for criterion, applicable in benign_evidence.items():
            if applicable and criterion in self.BENIGN_CRITERIA:
                strength = self.BENIGN_CRITERIA[criterion]['strength']
                self.benign_counts[strength.name.lower()] += 1
                crit = ACMGCriterion(
                    code=criterion,
                    strength=strength,
                    description=self.BENIGN_CRITERIA[criterion]['name'],
                    applicable=True
                )
                benign_crits.append(crit)

        # Determine classification tier
        tier, confidence = self._calculate_tier()

        classification = ACMGClassification(
            variant_id=variant_id,
            gene=gene,
            hgvs=hgvs,
            classification=tier,
            confidence=confidence,
            pathogenic_criteria=pathogenic_crits,
            benign_criteria=benign_crits,
            final_assessment=self._generate_assessment()
        )

        return classification

    def _calculate_tier(self) -> Tuple[ACMGTier, float]:
        """Calculate classification tier based on evidence aggregation."""
        p_vs = self.pathogenic_counts['very_strong']
        p_s = self.pathogenic_counts['strong']
        p_m = self.pathogenic_counts['moderate']
        p_sup = self.pathogenic_counts['supporting']

        b_vs = self.benign_counts['very_strong']
        b_s = self.benign_counts['strong']
        b_m = self.benign_counts['moderate']
        b_sup = self.benign_counts['supporting']

        # Benign rules (highest priority)
        if b_vs >= 1:
            return ACMGTier.BENIGN, 0.99
        if b_s >= 2:
            return ACMGTier.BENIGN, 0.95

        if (b_s >= 1 and b_sup >= 1) or (b_sup >= 2):
            return ACMGTier.LIKELY_BENIGN, 0.80

        # Pathogenic rules
        if p_vs >= 1 and p_s >= 1:
            return ACMGTier.PATHOGENIC, 0.99
        if p_s >= 2:
            return ACMGTier.PATHOGENIC, 0.95
        if p_vs >= 1 and p_m >= 1:
            return ACMGTier.PATHOGENIC, 0.90
        if p_s >= 1 and p_m >= 2:
            return ACMGTier.PATHOGENIC, 0.85
        if p_m >= 3:
            return ACMGTier.PATHOGENIC, 0.80

        if p_vs >= 1 and p_m >= 1:
            return ACMGTier.LIKELY_PATHOGENIC, 0.85
        if p_s >= 1 and p_m >= 1:
            return ACMGTier.LIKELY_PATHOGENIC, 0.80
        if p_m >= 3:
            return ACMGTier.LIKELY_PATHOGENIC, 0.75
        if p_m >= 2 and p_sup >= 2:
            return ACMGTier.LIKELY_PATHOGENIC, 0.70

        # Default: VUS
        return ACMGTier.UNCERTAIN, 0.50

    def _generate_assessment(self) -> str:
        """Generate summary assessment text."""
        p_vs = self.pathogenic_counts['very_strong']
        p_s = self.pathogenic_counts['strong']
        b_vs = self.benign_counts['very_strong']
        b_s = self.benign_counts['strong']

        parts = []
        if p_vs > 0:
            parts.append(f"{p_vs} very strong pathogenic criterion")
        if p_s > 0:
            parts.append(f"{p_s} strong pathogenic criteria")
        if b_vs > 0:
            parts.append(f"{b_vs} very strong benign criterion")
        if b_s > 0:
            parts.append(f"{b_s} strong benign criteria")

        return "; ".join(parts) if parts else "Insufficient evidence"

    def report(self, classification: ACMGClassification) -> str:
        """Generate human-readable classification report."""
        report_lines = [
            f"Variant ID: {classification.variant_id}",
            f"Gene: {classification.gene}",
            f"HGVS: {classification.hgvs}",
            f"",
            f"Classification: {classification.classification.value}",
            f"Confidence: {classification.confidence:.2%}",
            f"",
            f"Assessment: {classification.final_assessment}",
        ]

        if classification.pathogenic_criteria:
            report_lines.append("\nPathogenic Criteria:")
            for crit in classification.pathogenic_criteria:
                report_lines.append(f"  {crit.code} ({crit.strength.value}): {crit.description}")

        if classification.benign_criteria:
            report_lines.append("\nBenign Criteria:")
            for crit in classification.benign_criteria:
                report_lines.append(f"  {crit.code} ({crit.strength.value}): {crit.description}")

        return "\n".join(report_lines)


def main():
    """Example usage of ACMG classifier."""
    classifier = ACMGClassifier()

    # Example: BRCA1 frameshift deletion
    pathogenic = {
        'PVS1': True,  # Frameshift in LoF-intolerant gene
        'PM2': True,   # Absent from gnomAD
    }
    benign = {}

    result = classifier.classify(
        variant_id='BRCA1_fs123',
        gene='BRCA1',
        hgvs='NM_007294.4:c.68_69delAG:p.(Gly23AspfsTer10)',
        pathogenic_evidence=pathogenic,
        benign_evidence=benign
    )

    print(classifier.report(result))


if __name__ == '__main__':
    main()

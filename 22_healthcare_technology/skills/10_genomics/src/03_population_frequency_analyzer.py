#!/usr/bin/env python3
"""
Population Frequency Analysis & Allele Frequency Filtering
Analyzes population frequencies from gnomAD and other databases.

Production-grade implementation with ancestry-specific filtering.
"""

import json
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RarityCategory(Enum):
    COMMON = "Common"
    LOW_FREQUENCY = "Low Frequency"
    RARE = "Rare"
    VERY_RARE = "Very Rare"
    SINGLETON = "Singleton"


@dataclass
class PopulationFrequencies:
    """Allele frequencies across populations."""
    overall_af: Optional[float] = None
    afr_af: Optional[float] = None  # African
    amr_af: Optional[float] = None  # Latino
    asj_af: Optional[float] = None  # Ashkenazi Jewish
    eas_af: Optional[float] = None  # East Asian
    fin_af: Optional[float] = None  # Finnish
    nfe_af: Optional[float] = None  # Non-Finnish European
    sas_af: Optional[float] = None  # South Asian
    
    # Additional metrics
    ac: Optional[int] = None  # Allele count
    an: Optional[int] = None  # Allele number (total samples)


class PopulationFrequencyAnalyzer:
    """Analyzes variant frequencies for clinical classification."""

    # Ancestry mappings
    ANCESTRY_POPULATIONS = {
        'AFR': 'afr_af',
        'AMR': 'amr_af',
        'ASJ': 'asj_af',
        'EAS': 'eas_af',
        'FIN': 'fin_af',
        'NFE': 'nfe_af',
        'SAS': 'sas_af',
    }

    # Frequency thresholds for different inheritance patterns
    THRESHOLDS = {
        'dominant': {
            'common_benign': 0.01,      # ≥1%
            'uncommon': 0.0005,         # 0.05%
            'rare': 0.00001,            # <0.001%
        },
        'recessive_heterozygous': {
            'common': 0.01,             # ≥1%
            'uncommon': 0.005,          # 0.5%
        },
        'recessive_homozygous': {
            'common': 0.01,             # ≥1%
        },
        'xlinked_male': {
            'common': 0.001,            # 0.1%
        }
    }

    def __init__(self):
        self.gnomad_data = {}

    def load_gnomad_data(self, json_file: str) -> bool:
        """Load gnomAD frequency data from JSON file."""
        try:
            with open(json_file, 'r') as f:
                self.gnomad_data = json.load(f)
            logger.info(f"Loaded gnomAD data for {len(self.gnomad_data)} variants")
            return True
        except Exception as e:
            logger.error(f"Error loading gnomAD data: {e}")
            return False

    def get_frequencies(self, variant_key: str) -> Optional[PopulationFrequencies]:
        """Get population frequencies for a variant."""
        if variant_key not in self.gnomad_data:
            return None

        data = self.gnomad_data[variant_key]
        
        return PopulationFrequencies(
            overall_af=data.get('overall_af'),
            afr_af=data.get('afr_af'),
            amr_af=data.get('amr_af'),
            asj_af=data.get('asj_af'),
            eas_af=data.get('eas_af'),
            fin_af=data.get('fin_af'),
            nfe_af=data.get('nfe_af'),
            sas_af=data.get('sas_af'),
            ac=data.get('ac'),
            an=data.get('an'),
        )

    def assess_rarity(self, af: float) -> RarityCategory:
        """Classify variant rarity based on allele frequency."""
        if af >= 0.05:
            return RarityCategory.COMMON
        elif af >= 0.01:
            return RarityCategory.LOW_FREQUENCY
        elif af >= 0.0001:
            return RarityCategory.RARE
        elif af >= 0.00001:
            return RarityCategory.VERY_RARE
        else:
            return RarityCategory.SINGLETON

    def evaluate_for_inheritance(self, frequencies: PopulationFrequencies,
                                inheritance: str = 'dominant',
                                ancestry: str = 'NFE') -> Tuple[bool, str]:
        """
        Evaluate if frequency is consistent with specified inheritance pattern.

        Returns:
            (is_likely_benign, explanation)
        """
        thresholds = self.THRESHOLDS.get(inheritance, {})
        
        # Get ancestry-specific frequency
        af = getattr(frequencies, self.ANCESTRY_POPULATIONS.get(ancestry, 'overall_af'), None)
        
        if af is None:
            return False, "No frequency data available"

        # Check dominant threshold
        if inheritance == 'dominant':
            if af >= thresholds['common_benign']:
                return True, f"Frequency {af:.2%} exceeds dominant common threshold"
            elif af >= thresholds['uncommon']:
                return True, f"Frequency {af:.2%} uncommon for dominant disease"
            
        # Check recessive carrier threshold
        elif inheritance == 'recessive_heterozygous':
            if af >= thresholds['common']:
                return True, f"Carrier frequency {af:.2%} too high for rare disease"

        # Check homozygous threshold
        elif inheritance == 'recessive_homozygous':
            if af >= thresholds['common']:
                return True, f"Homozygous frequency {af:.2%} too high"

        # Check X-linked male threshold
        elif inheritance == 'xlinked_male':
            if af >= thresholds['common']:
                return True, f"X-linked male frequency {af:.2%} too high"

        return False, f"Frequency {af:.6f} ({af:.2%}) is rare, consistent with disease"

    def get_frequency_report(self, variant_key: str, inheritance: str = 'dominant',
                           ancestry: str = 'NFE') -> str:
        """Generate frequency analysis report."""
        freqs = self.get_frequencies(variant_key)
        
        if freqs is None:
            return f"Variant {variant_key} not found in database"

        report_lines = [
            f"Population Frequency Analysis for {variant_key}",
            "=" * 50,
            f"",
            f"Overall Allele Frequency: {freqs.overall_af:.6f}" if freqs.overall_af else "N/A",
            f"Ancestry-Specific Frequencies:",
            f"  AFR:  {freqs.afr_af:.6f}" if freqs.afr_af else "  AFR:  N/A",
            f"  AMR:  {freqs.amr_af:.6f}" if freqs.amr_af else "  AMR:  N/A",
            f"  EAS:  {freqs.eas_af:.6f}" if freqs.eas_af else "  EAS:  N/A",
            f"  FIN:  {freqs.fin_af:.6f}" if freqs.fin_af else "  FIN:  N/A",
            f"  NFE:  {freqs.nfe_af:.6f}" if freqs.nfe_af else "  NFE:  N/A",
            f"  SAS:  {freqs.sas_af:.6f}" if freqs.sas_af else "  SAS:  N/A",
            f"",
            f"Allele Count: {freqs.ac}",
            f"Allele Number: {freqs.an}",
        ]

        rarity = self.assess_rarity(freqs.overall_af or 0)
        report_lines.append(f"Rarity Category: {rarity.value}")

        is_benign, explanation = self.evaluate_for_inheritance(freqs, inheritance, ancestry)
        report_lines.append(f"")
        report_lines.append(f"Inheritance Pattern: {inheritance}")
        report_lines.append(f"Ancestry: {ancestry}")
        report_lines.append(f"Likely Benign: {is_benign}")
        report_lines.append(f"Explanation: {explanation}")

        return "\n".join(report_lines)


def main():
    """Example usage."""
    analyzer = PopulationFrequencyAnalyzer()
    
    # Example: Create mock data
    mock_data = {
        'BRCA1_c.68_69delAG': {
            'overall_af': 0.00001,
            'afr_af': 0.00002,
            'nfe_af': 0.00001,
            'ac': 5,
            'an': 500000,
        },
        'common_variant': {
            'overall_af': 0.35,
            'afr_af': 0.40,
            'nfe_af': 0.30,
            'ac': 350000,
            'an': 1000000,
        }
    }
    
    analyzer.gnomad_data = mock_data
    
    print(analyzer.get_frequency_report('BRCA1_c.68_69delAG', inheritance='dominant'))
    print("\n" + "="*50 + "\n")
    print(analyzer.get_frequency_report('common_variant', inheritance='dominant'))


if __name__ == '__main__':
    main()

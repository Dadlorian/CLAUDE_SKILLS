#!/usr/bin/env python3
"""
VCF Parser and Variant Analysis Tool
Parses VCF files and provides variant-level analysis with quality filtering.

Production-grade implementation with error handling and logging.
"""

import sys
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class VCFVariant:
    """Represents a single VCF variant with parsed fields."""
    chrom: str
    pos: int
    variant_id: str
    ref: str
    alt: List[str]
    qual: Optional[float]
    filters: List[str]
    info: Dict[str, str]
    samples: Dict[str, Dict[str, str]]

    def get_vaf(self, sample_name: str) -> Optional[float]:
        """Calculate VAF from AD field if available."""
        if sample_name not in self.samples:
            return None

        sample_data = self.samples[sample_name]
        if 'AD' not in sample_data:
            return None

        try:
            ad_values = [int(x) for x in sample_data['AD'].split(',')]
            total = sum(ad_values)
            if total == 0:
                return None
            return ad_values[1] / total if len(ad_values) > 1 else None
        except (ValueError, IndexError):
            return None

    def passes_filters(self) -> bool:
        """Check if variant passes quality filters."""
        return 'PASS' in self.filters or len(self.filters) == 0


class VCFParser:
    """Parse and analyze VCF files with production-grade quality control."""

    def __init__(self, vcf_file: str):
        self.vcf_file = vcf_file
        self.header_lines = []
        self.sample_names = []
        self.variants: List[VCFVariant] = []
        self.metadata = {}

    def parse(self) -> bool:
        """Parse VCF file and validate structure."""
        try:
            with open(self.vcf_file, 'r') as f:
                self._parse_header(f)
                self._parse_variants(f)

            logger.info(f"Successfully parsed {len(self.variants)} variants")
            return True
        except Exception as e:
            logger.error(f"Error parsing VCF file: {e}")
            return False

    def _parse_header(self, f):
        """Parse VCF header and extract metadata."""
        for line in f:
            if line.startswith('##'):
                self.header_lines.append(line.strip())
                self._extract_metadata(line)
            elif line.startswith('#CHROM'):
                # Column header line
                columns = line.strip().split('\t')
                self.sample_names = columns[9:]  # Samples start at column 9
                logger.info(f"Found {len(self.sample_names)} samples: {self.sample_names}")
                break

    def _extract_metadata(self, line: str):
        """Extract relevant metadata from header lines."""
        if line.startswith('##fileformat='):
            self.metadata['fileformat'] = line.split('=')[1].strip()
        elif line.startswith('##reference='):
            self.metadata['reference'] = line.split('=')[1].strip()

    def _parse_variants(self, f):
        """Parse variant data lines."""
        variant_count = 0
        for line in f:
            if line.startswith('#'):
                continue

            variant_count += 1
            fields = line.strip().split('\t')

            if len(fields) < 8:
                logger.warning(f"Skipping malformed line {variant_count}")
                continue

            variant = self._parse_variant_line(fields)
            if variant:
                self.variants.append(variant)

    def _parse_variant_line(self, fields: List[str]) -> Optional[VCFVariant]:
        """Parse a single VCF data line."""
        try:
            chrom, pos, vid, ref, alt, qual, filters, info = fields[:8]
            pos = int(pos)
            qual = float(qual) if qual != '.' else None

            alt_list = alt.split(',')
            filter_list = filters.split(';') if filters != '.' else []

            # Parse INFO field (simplified - production would be more comprehensive)
            info_dict = {}
            for item in info.split(';'):
                if '=' in item:
                    key, value = item.split('=', 1)
                    info_dict[key] = value

            # Parse sample fields
            format_fields = fields[8].split(':')
            samples = {}

            for i, sample_name in enumerate(self.sample_names):
                sample_col = i + 9
                if sample_col < len(fields):
                    sample_values = fields[sample_col].split(':')
                    sample_data = dict(zip(format_fields, sample_values))
                    samples[sample_name] = sample_data

            return VCFVariant(
                chrom=chrom,
                pos=pos,
                variant_id=vid,
                ref=ref,
                alt=alt_list,
                qual=qual,
                filters=filter_list,
                info=info_dict,
                samples=samples
            )
        except Exception as e:
            logger.warning(f"Error parsing variant line: {e}")
            return None

    def filter_variants(self, quality_threshold: float = 20) -> List[VCFVariant]:
        """Filter variants by quality threshold."""
        filtered = [
            v for v in self.variants
            if v.qual is None or v.qual >= quality_threshold
        ]
        logger.info(f"Filtered to {len(filtered)} variants with QUAL >= {quality_threshold}")
        return filtered

    def get_statistics(self) -> Dict:
        """Generate variant statistics."""
        stats = {
            'total_variants': len(self.variants),
            'passed_filter': sum(1 for v in self.variants if v.passes_filters()),
            'snvs': sum(1 for v in self.variants if len(v.ref) == 1 and all(len(a) == 1 for a in v.alt)),
            'indels': sum(1 for v in self.variants if len(v.ref) > 1 or any(len(a) > 1 for a in v.alt)),
            'samples': len(self.sample_names),
            'chromosomes': len(set(v.chrom for v in self.variants))
        }
        return stats


def main():
    """Main entry point with example usage."""
    if len(sys.argv) < 2:
        print("Usage: python vcf_parser.py <vcf_file>")
        sys.exit(1)

    vcf_file = sys.argv[1]
    parser = VCFParser(vcf_file)

    if parser.parse():
        stats = parser.get_statistics()
        print("\n=== VCF Summary Statistics ===")
        for key, value in stats.items():
            print(f"{key}: {value}")

        # Example: Show first 5 variants
        print("\n=== First 5 Variants ===")
        for i, variant in enumerate(parser.variants[:5]):
            print(f"{i+1}. {variant.chrom}:{variant.pos} {variant.ref}>{','.join(variant.alt)}")
            print(f"   Quality: {variant.qual}, Filters: {variant.filters}")


if __name__ == '__main__':
    main()

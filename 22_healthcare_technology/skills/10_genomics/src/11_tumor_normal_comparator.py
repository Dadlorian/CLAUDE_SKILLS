"""
Tumor-Normal Variant Comparator
Compares tumor and normal samples to identify somatic mutations
"""

from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
import pysam
from collections import defaultdict

@dataclass
class Variant:
    """Genomic variant"""
    chrom: str
    pos: int
    ref: str
    alt: str
    qual: float
    depth: int
    vaf: float
    genotype: Tuple[int, int]

@dataclass
class SomaticVariant:
    """Somatic variant found in tumor but not normal"""
    variant: Variant
    tumor_vaf: float
    normal_vaf: float
    tumor_depth: int
    normal_depth: int
    classification: str  # 'somatic', 'germline', 'loh'
    confidence: str  # 'high', 'medium', 'low'

class TumorNormalComparator:
    """Compare tumor and normal samples to identify somatic variants"""

    def __init__(self):
        self.somatic_vaf_threshold = 0.05  # Min VAF in tumor
        self.normal_vaf_threshold = 0.02  # Max VAF in normal for somatic
        self.min_depth = 20  # Minimum depth for reliable calling
        self.loh_vaf_threshold = 0.85  # VAF threshold for LOH

    def compare_samples(self, tumor_vcf: str, normal_vcf: str) -> List[SomaticVariant]:
        """Compare tumor and normal VCF files to identify somatic mutations"""

        # Load variants from both samples
        tumor_variants = self.load_variants(tumor_vcf)
        normal_variants = self.load_variants(normal_vcf)

        somatic_variants = []

        # Check each tumor variant
        for pos, tumor_var in tumor_variants.items():
            # Skip if depth too low
            if tumor_var.depth < self.min_depth:
                continue

            # Check if variant exists in normal
            normal_var = normal_variants.get(pos)

            # Classify variant
            classification, confidence = self.classify_variant(tumor_var, normal_var)

            if classification in ['somatic', 'loh']:
                somatic_variant = SomaticVariant(
                    variant=tumor_var,
                    tumor_vaf=tumor_var.vaf,
                    normal_vaf=normal_var.vaf if normal_var else 0.0,
                    tumor_depth=tumor_var.depth,
                    normal_depth=normal_var.depth if normal_var else 0,
                    classification=classification,
                    confidence=confidence
                )
                somatic_variants.append(somatic_variant)

        return somatic_variants

    def load_variants(self, vcf_file: str) -> Dict[str, Variant]:
        """Load variants from VCF file"""
        variants = {}
        vcf = pysam.VariantFile(vcf_file)

        for record in vcf.fetch():
            # Get first sample (assuming single sample VCF)
            sample = list(record.samples.values())[0]

            # Extract variant information
            chrom = record.chrom
            pos = record.pos
            ref = record.ref
            alt = str(record.alts[0]) if record.alts else ""

            # Get genotype
            gt = sample.get('GT', (None, None))

            # Get depth and VAF
            depth = sample.get('DP', 0)
            ad = sample.get('AD', None)

            if ad and len(ad) >= 2:
                ref_count = ad[0]
                alt_count = ad[1]
                vaf = alt_count / (ref_count + alt_count) if (ref_count + alt_count) > 0 else 0
            else:
                vaf = 0

            qual = record.qual if record.qual else 0

            # Create variant key
            var_key = f"{chrom}:{pos}:{ref}:{alt}"

            variants[var_key] = Variant(
                chrom=chrom,
                pos=pos,
                ref=ref,
                alt=alt,
                qual=qual,
                depth=depth,
                vaf=vaf,
                genotype=gt
            )

        vcf.close()
        return variants

    def classify_variant(self, tumor_var: Variant, normal_var: Variant = None) -> Tuple[str, str]:
        """Classify variant as somatic, germline, or LOH"""

        # No normal variant - likely somatic
        if normal_var is None or normal_var.depth < self.min_depth:
            if tumor_var.vaf >= self.somatic_vaf_threshold:
                confidence = 'high' if tumor_var.depth >= 50 else 'medium'
                return 'somatic', confidence
            else:
                return 'artifact', 'low'

        # Both tumor and normal have variant
        if normal_var is not None:
            # High VAF in both - germline
            if normal_var.vaf >= 0.40:
                # Check for LOH
                if tumor_var.vaf >= self.loh_vaf_threshold:
                    return 'loh', 'high'  # Loss of heterozygosity
                else:
                    return 'germline', 'high'

            # Low VAF in normal, high in tumor - likely somatic
            elif normal_var.vaf <= self.normal_vaf_threshold and tumor_var.vaf >= self.somatic_vaf_threshold:
                confidence = 'high' if tumor_var.depth >= 50 and normal_var.depth >= 30 else 'medium'
                return 'somatic', confidence

            # Ambiguous cases
            else:
                return 'uncertain', 'low'

        return 'uncertain', 'low'

    def calculate_tumor_purity(self, somatic_variants: List[SomaticVariant]) -> float:
        """Estimate tumor purity based on somatic variant VAFs"""
        if not somatic_variants:
            return 0.0

        # Use median VAF of high-confidence clonal variants
        clonal_vafs = [
            v.tumor_vaf for v in somatic_variants
            if v.confidence == 'high' and v.tumor_vaf >= 0.25
        ]

        if not clonal_vafs:
            return 0.0

        # Estimate purity (simplified)
        median_vaf = sorted(clonal_vafs)[len(clonal_vafs) // 2]
        estimated_purity = median_vaf * 2  # Assuming heterozygous variants
        return min(estimated_purity, 1.0)

    def identify_copy_number_changes(self, somatic_variants: List[SomaticVariant]) -> Dict[str, List]:
        """Identify potential copy number changes based on VAF patterns"""
        # Group variants by chromosome
        variants_by_chr = defaultdict(list)
        for variant in somatic_variants:
            if variant.classification in ['somatic', 'germline']:
                variants_by_chr[variant.variant.chrom].append(variant)

        cn_changes = {}

        for chrom, variants in variants_by_chr.items():
            # Look for regions with consistently high or low VAF
            high_vaf_regions = []
            low_vaf_regions = []

            for variant in variants:
                if variant.tumor_vaf > 0.7:
                    high_vaf_regions.append(variant)
                elif variant.tumor_vaf < 0.2 and variant.classification == 'somatic':
                    low_vaf_regions.append(variant)

            if high_vaf_regions:
                cn_changes[chrom] = {
                    'type': 'amplification_or_loh',
                    'count': len(high_vaf_regions),
                    'median_vaf': sorted([v.tumor_vaf for v in high_vaf_regions])[len(high_vaf_regions)//2]
                }
            elif low_vaf_regions:
                cn_changes[chrom] = {
                    'type': 'subclonal_or_deletion',
                    'count': len(low_vaf_regions),
                    'median_vaf': sorted([v.tumor_vaf for v in low_vaf_regions])[len(low_vaf_regions)//2]
                }

        return cn_changes

    def filter_artifacts(self, somatic_variants: List[SomaticVariant],
                        panel_of_normals: Set[str] = None) -> List[SomaticVariant]:
        """Filter out likely artifacts using panel of normals"""
        if panel_of_normals is None:
            return somatic_variants

        filtered = []
        for variant in somatic_variants:
            var_key = f"{variant.variant.chrom}:{variant.variant.pos}:{variant.variant.ref}:{variant.variant.alt}"

            # Skip if variant is in panel of normals
            if var_key not in panel_of_normals:
                filtered.append(variant)

        return filtered

    def generate_somatic_report(self, somatic_variants: List[SomaticVariant],
                                tumor_sample_id: str, normal_sample_id: str) -> str:
        """Generate report of somatic variants"""

        report = f"""
SOMATIC VARIANT ANALYSIS REPORT
================================

Tumor Sample: {tumor_sample_id}
Normal Sample: {normal_sample_id}

SUMMARY
-------
Total somatic variants: {len([v for v in somatic_variants if v.classification == 'somatic'])}
High confidence: {len([v for v in somatic_variants if v.confidence == 'high'])}
Medium confidence: {len([v for v in somatic_variants if v.confidence == 'medium'])}
LOH events: {len([v for v in somatic_variants if v.classification == 'loh'])}

Estimated tumor purity: {self.calculate_tumor_purity(somatic_variants):.1%}

SOMATIC VARIANTS
----------------
"""

        # Sort by chromosome and position
        sorted_variants = sorted(
            somatic_variants,
            key=lambda v: (v.variant.chrom, v.variant.pos)
        )

        for variant in sorted_variants:
            if variant.classification == 'somatic':
                report += f"\n{variant.variant.chrom}:{variant.variant.pos} "
                report += f"{variant.variant.ref}>{variant.variant.alt}\n"
                report += f"  Tumor VAF: {variant.tumor_vaf:.2%} (depth: {variant.tumor_depth}x)\n"
                report += f"  Normal VAF: {variant.normal_vaf:.2%} (depth: {variant.normal_depth}x)\n"
                report += f"  Confidence: {variant.confidence}\n"

        # Copy number changes
        cn_changes = self.identify_copy_number_changes(somatic_variants)
        if cn_changes:
            report += "\nPOTENTIAL COPY NUMBER CHANGES\n"
            report += "-----------------------------\n"
            for chrom, info in cn_changes.items():
                report += f"{chrom}: {info['type']} ({info['count']} variants, median VAF: {info['median_vaf']:.2%})\n"

        return report

if __name__ == "__main__":
    # Example usage
    comparator = TumorNormalComparator()

    print("Tumor-Normal Variant Comparator")
    print("Identifies somatic mutations by comparing tumor and matched normal samples")
    print("\nUsage:")
    print("  somatic_variants = comparator.compare_samples('tumor.vcf', 'normal.vcf')")
    print("  report = comparator.generate_somatic_report(somatic_variants, 'T001', 'N001')")

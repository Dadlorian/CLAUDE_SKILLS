"""
Data Quality Metrics for Genomic Sequencing
Calculates and reports quality metrics for NGS data (FastQ, BAM, VCF files)
"""

import pysam
from typing import Dict, List, Tuple
from dataclasses import dataclass
import numpy as np
from collections import defaultdict

@dataclass
class FastQMetrics:
    """Quality metrics for FastQ files"""
    total_reads: int
    total_bases: int
    mean_read_length: float
    mean_quality_score: float
    q20_bases_percent: float
    q30_bases_percent: float
    gc_content: float
    n_content: float
    duplicate_rate: float

@dataclass
class BAMMetrics:
    """Quality metrics for BAM alignment files"""
    total_reads: int
    mapped_reads: int
    properly_paired: int
    mean_coverage: float
    median_coverage: float
    percent_target_covered_10x: float
    percent_target_covered_20x: float
    percent_target_covered_30x: float
    mean_mapping_quality: float
    duplicate_rate: float
    insert_size_mean: float
    insert_size_std: float

@dataclass
class VCFMetrics:
    """Quality metrics for VCF variant files"""
    total_variants: int
    snps: int
    indels: int
    transitions: int
    transversions: int
    ti_tv_ratio: float
    het_hom_ratio: float
    mean_variant_quality: float
    mean_depth: float
    dbsnp_variants: int
    novel_variants: int

class GenomicDataQualityAnalyzer:
    """Analyze quality metrics for genomic sequencing data"""

    def __init__(self):
        self.quality_thresholds = {
            'min_mean_quality': 30,
            'min_q30_percent': 80,
            'min_mapping_rate': 95,
            'min_coverage_10x': 95,
            'min_ti_tv_ratio': 2.0,
            'max_duplicate_rate': 20
        }

    def analyze_fastq(self, fastq_file: str) -> FastQMetrics:
        """Analyze FastQ file quality metrics"""
        total_reads = 0
        total_bases = 0
        total_quality = 0
        q20_bases = 0
        q30_bases = 0
        gc_count = 0
        n_count = 0
        read_lengths = []

        # Parse FastQ file
        with pysam.FastxFile(fastq_file) as fq:
            for entry in fq:
                total_reads += 1
                sequence = entry.sequence
                quality = entry.quality

                # Read length
                read_length = len(sequence)
                read_lengths.append(read_length)
                total_bases += read_length

                # Quality scores
                qual_scores = [ord(q) - 33 for q in quality]  # Phred+33 encoding
                total_quality += sum(qual_scores)
                q20_bases += sum(1 for q in qual_scores if q >= 20)
                q30_bases += sum(1 for q in qual_scores if q >= 30)

                # GC and N content
                gc_count += sum(1 for base in sequence if base in 'GCgc')
                n_count += sum(1 for base in sequence if base in 'Nn')

        # Calculate metrics
        mean_read_length = np.mean(read_lengths) if read_lengths else 0
        mean_quality = total_quality / total_bases if total_bases > 0 else 0
        q20_percent = (q20_bases / total_bases * 100) if total_bases > 0 else 0
        q30_percent = (q30_bases / total_bases * 100) if total_bases > 0 else 0
        gc_content = (gc_count / total_bases * 100) if total_bases > 0 else 0
        n_content = (n_count / total_bases * 100) if total_bases > 0 else 0

        # Estimate duplicate rate (simplified)
        duplicate_rate = self.estimate_duplicate_rate_fastq(fastq_file)

        return FastQMetrics(
            total_reads=total_reads,
            total_bases=total_bases,
            mean_read_length=mean_read_length,
            mean_quality_score=mean_quality,
            q20_bases_percent=q20_percent,
            q30_bases_percent=q30_percent,
            gc_content=gc_content,
            n_content=n_content,
            duplicate_rate=duplicate_rate
        )

    def analyze_bam(self, bam_file: str, target_bed: str = None) -> BAMMetrics:
        """Analyze BAM alignment file quality metrics"""
        samfile = pysam.AlignmentFile(bam_file, "rb")

        total_reads = 0
        mapped_reads = 0
        properly_paired = 0
        duplicates = 0
        mapping_qualities = []
        insert_sizes = []
        coverage_per_position = defaultdict(int)

        # Iterate through reads
        for read in samfile.fetch():
            total_reads += 1

            if not read.is_unmapped:
                mapped_reads += 1
                mapping_qualities.append(read.mapping_quality)

                # Track coverage
                for pos in range(read.reference_start, read.reference_end):
                    coverage_per_position[pos] += 1

            if read.is_proper_pair:
                properly_paired += 1

            if read.is_duplicate:
                duplicates += 1

            if read.is_proper_pair and read.template_length > 0:
                insert_sizes.append(abs(read.template_length))

        samfile.close()

        # Calculate coverage metrics
        coverages = list(coverage_per_position.values())
        mean_coverage = np.mean(coverages) if coverages else 0
        median_coverage = np.median(coverages) if coverages else 0

        # Calculate percent bases covered at different depths
        total_positions = len(coverages)
        percent_10x = sum(1 for c in coverages if c >= 10) / total_positions * 100 if total_positions > 0 else 0
        percent_20x = sum(1 for c in coverages if c >= 20) / total_positions * 100 if total_positions > 0 else 0
        percent_30x = sum(1 for c in coverages if c >= 30) / total_positions * 100 if total_positions > 0 else 0

        # Other metrics
        mean_mapping_quality = np.mean(mapping_qualities) if mapping_qualities else 0
        duplicate_rate = (duplicates / total_reads * 100) if total_reads > 0 else 0
        insert_size_mean = np.mean(insert_sizes) if insert_sizes else 0
        insert_size_std = np.std(insert_sizes) if insert_sizes else 0

        return BAMMetrics(
            total_reads=total_reads,
            mapped_reads=mapped_reads,
            properly_paired=properly_paired,
            mean_coverage=mean_coverage,
            median_coverage=median_coverage,
            percent_target_covered_10x=percent_10x,
            percent_target_covered_20x=percent_20x,
            percent_target_covered_30x=percent_30x,
            mean_mapping_quality=mean_mapping_quality,
            duplicate_rate=duplicate_rate,
            insert_size_mean=insert_size_mean,
            insert_size_std=insert_size_std
        )

    def analyze_vcf(self, vcf_file: str) -> VCFMetrics:
        """Analyze VCF variant file quality metrics"""
        vcf = pysam.VariantFile(vcf_file)

        total_variants = 0
        snps = 0
        indels = 0
        transitions = 0
        transversions = 0
        het_count = 0
        hom_count = 0
        qualities = []
        depths = []
        dbsnp_count = 0

        transition_pairs = [('A', 'G'), ('G', 'A'), ('C', 'T'), ('T', 'C')]

        for record in vcf.fetch():
            total_variants += 1

            # Variant type
            if len(record.ref) == 1 and all(len(alt) == 1 for alt in record.alts):
                snps += 1

                # Transitions vs Transversions
                for alt in record.alts:
                    if (record.ref, alt) in transition_pairs:
                        transitions += 1
                    else:
                        transversions += 1
            else:
                indels += 1

            # Quality and depth
            if record.qual:
                qualities.append(record.qual)

            if 'DP' in record.info:
                depths.append(record.info['DP'])

            # Het/Hom ratio (for first sample if available)
            if len(record.samples) > 0:
                sample = list(record.samples.values())[0]
                if 'GT' in sample:
                    gt = sample['GT']
                    if gt == (0, 1) or gt == (1, 0):
                        het_count += 1
                    elif gt == (1, 1):
                        hom_count += 1

            # dbSNP variants
            if record.id and record.id.startswith('rs'):
                dbsnp_count += 1

        vcf.close()

        # Calculate metrics
        ti_tv_ratio = transitions / transversions if transversions > 0 else 0
        het_hom_ratio = het_count / hom_count if hom_count > 0 else 0
        mean_quality = np.mean(qualities) if qualities else 0
        mean_depth = np.mean(depths) if depths else 0
        novel_variants = total_variants - dbsnp_count

        return VCFMetrics(
            total_variants=total_variants,
            snps=snps,
            indels=indels,
            transitions=transitions,
            transversions=transversions,
            ti_tv_ratio=ti_tv_ratio,
            het_hom_ratio=het_hom_ratio,
            mean_variant_quality=mean_quality,
            mean_depth=mean_depth,
            dbsnp_variants=dbsnp_count,
            novel_variants=novel_variants
        )

    def assess_quality(self, metrics: Dict) -> Dict:
        """Assess overall quality and flag issues"""
        issues = []
        warnings = []
        passed = True

        if 'fastq' in metrics:
            fq = metrics['fastq']
            if fq.mean_quality_score < self.quality_thresholds['min_mean_quality']:
                issues.append(f"Low mean quality: {fq.mean_quality_score:.1f}")
                passed = False
            if fq.q30_bases_percent < self.quality_thresholds['min_q30_percent']:
                issues.append(f"Low Q30 percentage: {fq.q30_bases_percent:.1f}%")
                passed = False

        if 'bam' in metrics:
            bam = metrics['bam']
            mapping_rate = (bam.mapped_reads / bam.total_reads * 100) if bam.total_reads > 0 else 0
            if mapping_rate < self.quality_thresholds['min_mapping_rate']:
                issues.append(f"Low mapping rate: {mapping_rate:.1f}%")
                passed = False
            if bam.percent_target_covered_10x < self.quality_thresholds['min_coverage_10x']:
                warnings.append(f"Low 10x coverage: {bam.percent_target_covered_10x:.1f}%")
            if bam.duplicate_rate > self.quality_thresholds['max_duplicate_rate']:
                warnings.append(f"High duplicate rate: {bam.duplicate_rate:.1f}%")

        if 'vcf' in metrics:
            vcf = metrics['vcf']
            if vcf.ti_tv_ratio < self.quality_thresholds['min_ti_tv_ratio']:
                warnings.append(f"Low Ti/Tv ratio: {vcf.ti_tv_ratio:.2f}")

        return {
            'passed': passed,
            'issues': issues,
            'warnings': warnings
        }

    def estimate_duplicate_rate_fastq(self, fastq_file: str, sample_size: int = 10000) -> float:
        """Estimate duplicate rate from FastQ (simplified)"""
        sequences = set()
        total = 0

        with pysam.FastxFile(fastq_file) as fq:
            for i, entry in enumerate(fq):
                if i >= sample_size:
                    break
                sequences.add(entry.sequence)
                total += 1

        unique_rate = len(sequences) / total if total > 0 else 0
        duplicate_rate = (1 - unique_rate) * 100
        return duplicate_rate

    def generate_quality_report(self, metrics: Dict) -> str:
        """Generate human-readable quality report"""
        report = "GENOMIC DATA QUALITY REPORT\n"
        report += "=" * 50 + "\n\n"

        if 'fastq' in metrics:
            fq = metrics['fastq']
            report += "FastQ Metrics:\n"
            report += f"  Total reads: {fq.total_reads:,}\n"
            report += f"  Mean read length: {fq.mean_read_length:.1f} bp\n"
            report += f"  Mean quality score: {fq.mean_quality_score:.1f}\n"
            report += f"  Q30 bases: {fq.q30_bases_percent:.1f}%\n"
            report += f"  GC content: {fq.gc_content:.1f}%\n\n"

        if 'bam' in metrics:
            bam = metrics['bam']
            mapping_rate = (bam.mapped_reads / bam.total_reads * 100) if bam.total_reads > 0 else 0
            report += "BAM Alignment Metrics:\n"
            report += f"  Total reads: {bam.total_reads:,}\n"
            report += f"  Mapped reads: {bam.mapped_reads:,} ({mapping_rate:.1f}%)\n"
            report += f"  Mean coverage: {bam.mean_coverage:.1f}x\n"
            report += f"  10x coverage: {bam.percent_target_covered_10x:.1f}%\n"
            report += f"  Duplicate rate: {bam.duplicate_rate:.1f}%\n\n"

        if 'vcf' in metrics:
            vcf = metrics['vcf']
            report += "VCF Variant Metrics:\n"
            report += f"  Total variants: {vcf.total_variants:,}\n"
            report += f"  SNPs: {vcf.snps:,}\n"
            report += f"  Indels: {vcf.indels:,}\n"
            report += f"  Ti/Tv ratio: {vcf.ti_tv_ratio:.2f}\n"
            report += f"  Mean variant quality: {vcf.mean_variant_quality:.1f}\n\n"

        assessment = self.assess_quality(metrics)
        report += "Quality Assessment:\n"
        report += f"  Status: {'PASS' if assessment['passed'] else 'FAIL'}\n"
        if assessment['issues']:
            report += f"  Issues: {'; '.join(assessment['issues'])}\n"
        if assessment['warnings']:
            report += f"  Warnings: {'; '.join(assessment['warnings'])}\n"

        return report

if __name__ == "__main__":
    analyzer = GenomicDataQualityAnalyzer()

    # Example: Analyze all file types
    print("Genomic Data Quality Analyzer")
    print("This tool analyzes FastQ, BAM, and VCF files for quality metrics")

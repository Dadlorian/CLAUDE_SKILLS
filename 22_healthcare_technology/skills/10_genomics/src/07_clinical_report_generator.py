#!/usr/bin/env python3
"""
Clinical Genomics Report Generator
Generates formatted clinical genomics reports from variant data.
"""

from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ClinicalReport:
    patient_name: str
    patient_dob: str
    mrn: str
    specimen_type: str
    test_name: str
    ordering_provider: str
    report_date: str
    
    findings: List[Dict] = None  # List of variant findings
    recommendations: List[str] = None
    limitations: List[str] = None


class ReportGenerator:
    """Generates formatted clinical genomics reports."""

    def __init__(self):
        self.lab_name = "Clinical Genomics Laboratory"
        self.director = "Board Certified Pathologist"
        self.clia_number = "XX.XXXX.XX"

    def generate_report(self, report_data: ClinicalReport) -> str:
        """Generate formatted clinical report."""
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append(self.lab_name.center(80))
        lines.append("=" * 80)
        lines.append("")

        # Patient Information
        lines.append("PATIENT INFORMATION")
        lines.append("-" * 40)
        lines.append(f"Name: {report_data.patient_name}")
        lines.append(f"DOB: {report_data.patient_dob}")
        lines.append(f"MRN: {report_data.mrn}")
        lines.append("")

        # Specimen Information
        lines.append("SPECIMEN INFORMATION")
        lines.append("-" * 40)
        lines.append(f"Specimen Type: {report_data.specimen_type}")
        lines.append(f"Collection Date: [INSERT DATE]")
        lines.append(f"Receipt Date: [INSERT DATE]")
        lines.append("")

        # Test Information
        lines.append("TEST INFORMATION")
        lines.append("-" * 40)
        lines.append(f"Test Name: {report_data.test_name}")
        lines.append(f"Ordering Provider: {report_data.ordering_provider}")
        lines.append("")

        # Methods
        lines.append("METHODS")
        lines.append("-" * 40)
        lines.append("Sequencing: Illumina NextSeq500 (75bp paired-end)")
        lines.append("Alignment: BWA-mem to GRCh38")
        lines.append("Variant Calling: GATK HaplotypeCaller")
        lines.append("Annotation: VEP v106")
        lines.append("Average Depth: 250x")
        lines.append("% bases >20x: 98.5%")
        lines.append("")

        # Results
        lines.append("RESULTS")
        lines.append("-" * 40)
        if report_data.findings:
            for i, finding in enumerate(report_data.findings, 1):
                lines.append(f"\nFinding {i}:")
                lines.append(f"  Gene: {finding.get('gene', 'N/A')}")
                lines.append(f"  Variant: {finding.get('variant', 'N/A')}")
                lines.append(f"  Classification: {finding.get('classification', 'N/A')}")
                lines.append(f"  Evidence: {finding.get('evidence', 'N/A')}")
        else:
            lines.append("No pathogenic or likely pathogenic variants detected.")
        lines.append("")

        # Recommendations
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 40)
        if report_data.recommendations:
            for rec in report_data.recommendations:
                lines.append(f"- {rec}")
        else:
            lines.append("- Genetic counseling recommended")
            lines.append("- Family screening consideration")
        lines.append("")

        # Limitations
        lines.append("LIMITATIONS")
        lines.append("-" * 40)
        limitations = report_data.limitations or [
            "This test detects single nucleotide variants and small indels",
            "Large structural variants may not be detected",
            "Mitochondrial DNA was not analyzed",
            "Copy number variations detected with limited sensitivity"
        ]
        for lim in limitations:
            lines.append(f"- {lim}")
        lines.append("")

        # Signature Section
        lines.append("REPORT AUTHORIZATION")
        lines.append("-" * 40)
        lines.append(f"Reported: {report_data.report_date}")
        lines.append(f"Director: {self.director}")
        lines.append(f"CLIA Certificate: {self.clia_number}")
        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)


---

#!/usr/bin/env python3
"""
Data Quality Metrics & QC Assessment
Calculates and reports sequencing quality metrics.
"""

from typing import Dict, Tuple
from dataclasses import dataclass
import statistics


@dataclass
class SequencingMetrics:
    total_reads: int
    aligned_reads: int
    properly_paired: int
    duplicate_reads: int
    mean_depth: float
    median_depth: float
    sd_depth: float
    percent_bases_20x: float
    percent_bases_30x: float
    snp_count: int
    indel_count: int
    ts_tv_ratio: float
    het_hom_ratio: float


class DataQualityAnalyzer:
    """Analyzes sequencing and variant calling quality metrics."""

    @staticmethod
    def calculate_alignment_metrics(
        total_reads: int,
        aligned_reads: int,
        properly_paired: int,
        duplicate_reads: int
    ) -> Dict[str, float]:
        """Calculate alignment quality metrics."""
        
        alignment_rate = aligned_reads / total_reads if total_reads > 0 else 0
        proper_pair_rate = properly_paired / aligned_reads if aligned_reads > 0 else 0
        duplicate_rate = duplicate_reads / aligned_reads if aligned_reads > 0 else 0
        
        return {
            'alignment_rate': alignment_rate,
            'proper_pair_rate': proper_pair_rate,
            'duplicate_rate': duplicate_rate,
        }

    @staticmethod
    def assess_coverage_uniformity(depths: list) -> Tuple[float, float, float]:
        """Assess coverage uniformity across genome."""
        mean_depth = statistics.mean(depths)
        median_depth = statistics.median(depths)
        sd_depth = statistics.stdev(depths) if len(depths) > 1 else 0
        
        return mean_depth, median_depth, sd_depth

    @staticmethod
    def calculate_coverage_statistics(depths: list, thresholds: list = [20, 30]) -> Dict:
        """Calculate percentage of bases above coverage thresholds."""
        stats = {}
        for threshold in thresholds:
            percent = sum(1 for d in depths if d >= threshold) / len(depths) * 100
            stats[f'percent_bases_{threshold}x'] = percent
        return stats

    @staticmethod
    def calculate_variant_stats(snp_count: int, indel_count: int,
                               ts_count: int, tv_count: int,
                               het_count: int, hom_count: int) -> Dict:
        """Calculate variant calling statistics."""
        total_variants = snp_count + indel_count
        ts_tv_ratio = ts_count / tv_count if tv_count > 0 else 0
        het_hom_ratio = het_count / hom_count if hom_count > 0 else 0
        
        return {
            'total_variants': total_variants,
            'snp_count': snp_count,
            'indel_count': indel_count,
            'snp_indel_ratio': snp_count / indel_count if indel_count > 0 else 0,
            'ts_tv_ratio': ts_tv_ratio,
            'het_hom_ratio': het_hom_ratio,
        }

    @staticmethod
    def generate_qc_report(metrics: SequencingMetrics) -> str:
        """Generate QC metrics report."""
        lines = [
            "SEQUENCING QUALITY CONTROL REPORT",
            "=" * 50,
            "",
            "Alignment Metrics:",
            f"  Total Reads: {metrics.total_reads:,}",
            f"  Aligned Reads: {metrics.aligned_reads:,}",
            f"  Alignment Rate: {metrics.aligned_reads/metrics.total_reads*100:.1f}%",
            f"  Properly Paired: {metrics.properly_paired:,}",
            f"  Duplicate Reads: {metrics.duplicate_reads:,}",
            f"  Duplication Rate: {metrics.duplicate_reads/metrics.aligned_reads*100:.1f}%",
            "",
            "Coverage Metrics:",
            f"  Mean Depth: {metrics.mean_depth:.1f}x",
            f"  Median Depth: {metrics.median_depth:.1f}x",
            f"  SD Depth: {metrics.sd_depth:.1f}x",
            f"  % Bases >20x: {metrics.percent_bases_20x:.1f}%",
            f"  % Bases >30x: {metrics.percent_bases_30x:.1f}%",
            "",
            "Variant Metrics:",
            f"  SNVs: {metrics.snp_count:,}",
            f"  Indels: {metrics.indel_count:,}",
            f"  Ts/Tv Ratio: {metrics.ts_tv_ratio:.2f}",
            f"  Het/Hom Ratio: {metrics.het_hom_ratio:.2f}",
        ]
        return "\n".join(lines)


---

#!/usr/bin/env python3
"""
BAM File Quality Control Analysis
Analyzes BAM alignment files for quality assessment.
"""

from typing import Dict, List
from collections import defaultdict


class BAMQCAnalyzer:
    """Analyzes BAM files for alignment quality."""

    def __init__(self):
        self.mapq_dist = defaultdict(int)
        self.insert_sizes = []
        self.chromosome_counts = defaultdict(int)

    def parse_samtools_stats(self, stats_file: str) -> Dict:
        """Parse samtools stats output."""
        metrics = {}
        
        try:
            with open(stats_file, 'r') as f:
                for line in f:
                    if line.startswith('SN'):
                        parts = line.strip().split('\t')
                        if len(parts) >= 3:
                            key = parts[1].rstrip(':')
                            value = parts[2]
                            metrics[key] = value
        except Exception as e:
            print(f"Error reading stats file: {e}")
            return {}
        
        return metrics

    def assess_mapping_quality(self, mapq_distribution: Dict[int, int]) -> Dict:
        """Assess mapping quality distribution."""
        total = sum(mapq_distribution.values())
        
        high_quality = sum(v for k, v in mapq_distribution.items() if k >= 20)
        medium_quality = sum(v for k, v in mapq_distribution.items() if 10 <= k < 20)
        low_quality = sum(v for k, v in mapq_distribution.items() if k < 10)
        
        return {
            'high_quality_pct': high_quality / total * 100 if total > 0 else 0,
            'medium_quality_pct': medium_quality / total * 100 if total > 0 else 0,
            'low_quality_pct': low_quality / total * 100 if total > 0 else 0,
        }

    def assess_insert_size(self, insert_sizes: List[int]) -> Dict:
        """Assess insert size distribution."""
        if not insert_sizes:
            return {}
        
        import statistics
        return {
            'median_insert_size': statistics.median(insert_sizes),
            'mean_insert_size': statistics.mean(insert_sizes),
            'insert_size_sd': statistics.stdev(insert_sizes) if len(insert_sizes) > 1 else 0,
        }

    def generate_qc_report(self, samtools_stats: Dict, mapq_dist: Dict,
                          insert_sizes: List[int]) -> str:
        """Generate BAM QC report."""
        mapq_metrics = self.assess_mapping_quality(mapq_dist)
        insert_metrics = self.assess_insert_size(insert_sizes)
        
        lines = [
            "BAM FILE QUALITY CONTROL REPORT",
            "=" * 50,
            "",
            "Samtools Stats Summary:",
        ]
        
        for key, value in samtools_stats.items():
            lines.append(f"  {key}: {value}")
        
        lines.extend([
            "",
            "Mapping Quality Assessment:",
            f"  High Quality (MAPQ >=20): {mapq_metrics.get('high_quality_pct', 0):.1f}%",
            f"  Medium Quality (10<=MAPQ<20): {mapq_metrics.get('medium_quality_pct', 0):.1f}%",
            f"  Low Quality (MAPQ<10): {mapq_metrics.get('low_quality_pct', 0):.1f}%",
            "",
            "Insert Size Analysis:",
            f"  Median: {insert_metrics.get('median_insert_size', 0):.0f}bp",
            f"  Mean: {insert_metrics.get('mean_insert_size', 0):.0f}bp",
            f"  SD: {insert_metrics.get('insert_size_sd', 0):.0f}bp",
        ])
        
        return "\n".join(lines)


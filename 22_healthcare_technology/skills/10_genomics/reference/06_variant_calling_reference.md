# Variant Calling & Sequencing QC Reference

## Sequencing Technologies

### Short-Read Sequencing (Illumina)
**Characteristics**:
- Read length: 75-150bp typical
- Accuracy: 99.9%+ per base (Q30+)
- Throughput: Very high (billions of reads)
- Cost: Most economical per base
- Best for: SNVs, small indels, genotyping

**Process**:
1. DNA fragmentation (insert size 300-500bp)
2. Library preparation and adapter ligation
3. Cluster generation (bridge amplification)
4. Sequencing by synthesis (4-color system)
5. Base calling from fluorescence intensity

**Platforms**:
- NovaSeq (highest throughput)
- NextSeq (mid-tier, fast turnaround)
- iSeq (benchtop, rapid)
- MiSeq (legacy, smaller scale)

### Long-Read Sequencing
**PacBio Sequel II**:
- Read length: 10-30kb+ average
- Accuracy: 99.9% (HiFi mode with circular consensus)
- Throughput: 100k-300k reads per run
- Best for: Structural variants, repetitive regions, phasing
- Time: Single 30-hour movie

**Oxford Nanopore MinION/PromethION**:
- Read length: 10-100kb+ (unlimited)
- Accuracy: 90-99% (depends on basecalling model)
- Throughput: Scalable (MinION smaller, PromethION massive)
- Best for: Structural variants, haplotyping, real-time analysis
- Advantages: Portable, real-time sequencing

**Applications**:
- Structural variant detection (deletions, duplications, inversions)
- Copy number variation
- Repeat expansion genotyping
- Phasing (haplotype information)
- De novo genome assembly

## Alignment & Reference Assembly

### Reference Genomes
**GRCh38 (Current Standard)**:
- Released 2013 with updates
- ~3 billion base pairs
- 22 autosomes + X + Y + mitochondrial
- Contig/scaffold-based assembly
- Patch releases with minor corrections

**GRCh37 (Legacy)**:
- Previous standard (2009)
- Still used in many clinical labs
- Coordinate mapping tools needed for comparison
- Gradual transition to GRCh38 ongoing

**Coordinate Systems**:
- **0-based**: Python/programming convention (start=0)
- **1-based**: Genomics convention (start=1)
- **Interbase**: Between-bases convention (common in VCF)
- Must specify when comparing coordinates

### Alignment Tools

**BWA (Burrows-Wheeler Aligner)**
- **Variants**: aln (short reads), mem (medium-long reads), sw (Smith-Waterman)
- **Common Command**:
```bash
bwa mem -M -t 8 reference.fa reads.fastq > output.sam
```
- **Parameters**:
  - `-M`: Mark shorter split hits as secondary
  - `-t`: Number of threads
  - `-k`: Minimum seed length (31 bp default)

**Bowtie2**
- **Strengths**: Fast, sensitive
- **Common Use**: RNA-seq, small RNA
- **Parameters**:
  - `--local`: Local alignment (allows clipping)
  - `--sensitive`: More accurate, slower
  - `--very-sensitive`: Maximum sensitivity

**STAR (RNA-seq Alignment)**
- **Optimized**: mRNA transcripts
- **Handles**: Splice junctions, introns
- **Output**: BAM with junctions tracked
- **Key Parameter**: `--sjdbGTFfile` for known junctions

### SAM/BAM Format

**SAM (Sequence Alignment Map)**:
- Plain text format
- One read per line
- Header section with references

**BAM (Binary SAM)**:
- Compressed binary version
- Indexed (BAI) for random access
- Standard clinical use
- Must be sorted and indexed for tools

**SAM Record Fields**:
| Field | Description | Example |
|-------|-------------|---------|
| QNAME | Query sequence name | read_001 |
| FLAG | Bitwise flag (see below) | 0 or 16 |
| RNAME | Reference sequence name | chr1 |
| POS | 1-based left-most position | 1000000 |
| MAPQ | Mapping quality (Phred) | 60 |
| CIGAR | Alignment string | 150M (150 match) |
| RNEXT | Ref name of next read | = (same) |
| PNEXT | Position of next read | 1001000 |
| TLEN | Insert size | 500 |
| SEQ | Query sequence | ACGTACGT... |
| QUAL | Query quality scores | IIIIII... |

**SAM FLAGS** (bitwise):
- 0x1 (1): Read paired
- 0x2 (2): Proper pair
- 0x4 (4): Read unmapped
- 0x8 (8): Mate unmapped
- 0x10 (16): Reverse strand
- 0x20 (32): Mate reverse strand
- 0x40 (64): First in pair
- 0x80 (128): Second in pair
- 0x100 (256): Secondary alignment
- 0x200 (512): QC failed
- 0x400 (1024): PCR duplicate
- 0x800 (2048): Supplementary alignment

## Variant Calling

### SNV/Indel Calling

**GATK HaplotypeCaller**
- **Approach**: Local de-novo assembly
- **Strengths**: Accurate indel calling, best practices
- **Workflow**:
```
1. MarkDuplicates (remove PCR duplicates)
2. BaseRecalibrator (quality score calibration)
3. HaplotypeCaller (call variants)
4. GenotypeGVCFs (consolidate g.vcf files)
5. VariantRecalibrator (VQSR quality filtering)
```

**DeepVariant**
- **Approach**: Deep learning model
- **Strengths**: High accuracy, no hand-crafted features
- **Input**: BAM file
- **Output**: VCF file
- **Containers**: Google-maintained docker images

**Platypus**
- **Strengths**: Flexible, good for non-diploid, viral
- **Approach**: Integrates evidence across reads
- **Use Case**: Low-coverage, mixed ploidy

**VarDict**
- **Strengths**: Good for both SNVs and indels
- **Parallelization**: Excellent speed
- **Approach**: Iterative variant quality filtering

### CNV Calling

**Array CGH**
- Uses microarray technology
- Resolution: 10kb-100kb (platform dependent)
- Detection: Copy number states (0,1,2,3,4+)
- Cost: Lower per sample

**Read-Depth Methods**
- **Principle**: Sequencing depth proportional to copy number
- **Tools**: CNVkit, LUMPY, DELLY (for structural variants)
- **Bin Size**: 500bp-1kb typical
- **Quality**: Requires >50x coverage generally

**Structural Variant Callers**
| Tool | Method | SV Type | Best For |
|------|--------|---------|----------|
| LUMPY | Discordant reads + split reads | BND, DEL, DUP, INV | Various SV |
| DELLY | Integrated approach | DEL, DUP, INV, BND | Cancer SV |
| Manta | Graph-based assembly | DEL, DUP, INV, BND | Joint calling |
| Breakdancer | Discordant pair method | DEL, DUP, INV, BND | Paired-end |

### Somatic Variant Calling

**Tumor-Normal Calling**:
1. **Variant Detection**: Call in both tumor and normal
2. **Filtering**: Remove germline variants (in normal BAM)
3. **Confidence**: Only keep high-confidence somatic calls
4. **VAF Threshold**: Typically ≥5% VAF for somatic
5. **Annotation**: Validate with functional consequences

**Tumor-Only Calling**:
- No normal comparison available
- Use population frequency filtering (gnomAD, cosmic)
- Higher false positive rate
- Requires bioinformatics validation

**Tools**:
- **MuTect2** (GATK): Best practices somatic calling
- **Strelka**: Fast, accurate somatic+indel
- **VarScan2**: Flexible, good for pooled data
- **Caveman**: Oxford pipeline somatic caller

## VCF Format

### VCF Structure
**Meta-information Lines** (##):
```
##fileformat=VCFv4.2
##reference=file:///GRCh38.fa
##contig=<ID=chr1,length=248956422>
##FILTER=<ID=LowQual,Description="Low quality">
##INFO=<ID=AC,Number=A,Type=Integer,Description="Allele count">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
```

**Header Line** (#CHROM):
```
#CHROM  POS  ID  REF  ALT  QUAL  FILTER  INFO  FORMAT  Sample1  Sample2
```

**Data Lines**:
```
chr1  1000000  .  A  T  100  PASS  AC=1;AF=0.5;DP=200  GT:GQ:DP  0/1:99:100  0/0:60:100
```

### VCF Fields

| Field | Description | Example |
|-------|-------------|---------|
| CHROM | Chromosome | chr1 |
| POS | Position (1-based) | 1000000 |
| ID | Variant ID (rsID) | rs123456 |
| REF | Reference allele | A |
| ALT | Alternate allele(s) | T,G |
| QUAL | Quality score (Phred) | 100 |
| FILTER | Filtering status | PASS or filter name |
| INFO | Variant annotations | AC=1;AF=0.5;DP=200 |
| FORMAT | Sample format fields | GT:GQ:DP |
| Sample columns | Sample-specific data | 0/1:99:100 |

**Genotype (GT) Field**:
- 0: Reference allele
- 1: First alternate allele
- 2: Second alternate allele
- `.`: Unphased
- `/`: Unphased separator
- `|`: Phased separator
- Examples: 0/0 (homozygous ref), 0/1 (het), 1/1 (homozygous alt)

**Quality Metrics**:
- **GQ (Genotype Quality)**: Confidence in genotype call (Phred score)
- **DP (Depth)**: Number of reads covering position
- **AD (Allele Depth)**: Counts for each allele (ref,alt1,alt2...)
- **AF (Allele Frequency)**: Frequency of alternate allele
- **VAF (Variant Allele Frequency)**: Specific to tumor/somatic analysis

## Quality Control & Filtering

### Sequencing QC Metrics

**Raw Data QC**:
- **Total Reads**: Expected billions for whole genome
- **Quality Score Distribution**: Phred scores (Q20+)
- **GC Content**: ~40-50% for human genome
- **Adapter Content**: Should be <2% after trimming
- **Duplication Rate**: <10% acceptable for WGS

**Alignment QC**:
- **Overall Alignment Rate**: >95% acceptable
- **Properly Paired Reads**: >90% for paired-end
- **Insert Size Distribution**: Median ~500bp typical
- **Mapping Quality**: MAPQ >20 preferred
- **Coverage Uniformity**: Avoid >2x variance across genome

### Variant QC Filtering

**Hard Filters**:
```
FILTER:
- LowQual: QUAL < 20
- HighDP: DP > 2*median (potential artifact)
- LowDP: DP < 10x (insufficient coverage)
- HighAF: AF > 0.5 (likely sequencing error for SNV)
- StrandBias: Strand ratio significant imbalance
```

**GATK VQSR (Variant Quality Score Recalibration)**:
1. Build machine learning model on truth variants (HapMap, Omni, 1000G)
2. Score all variants based on annotation features
3. Select filtering threshold at desired specificity
4. Apply filter across all variants

**Key Annotations for Filtering**:
- **MQ (Mapping Quality)**: Alignment confidence
- **MQRankSum**: Difference in mapping quality between alt and ref
- **ReadPosRankSum**: Difference in position bias
- **FS (Fisher Strand)**: Strand bias p-value
- **QD (Quality by Depth)**: QUAL/DP ratio
- **SOR (Strand Odds Ratio)**: Alternative strand bias metric

### Data Quality Tools

**FastQC**: Illumina read quality assessment
**Samtools**: SAM/BAM manipulation and statistics
**Picard**: Quality metrics (dup rate, alignment stats)
**Bcftools**: VCF statistics and validation
**VCFtools**: VCF quality assessment

## Variant Annotation

### Annotation Tools

**Ensembl VEP (Variant Effect Predictor)**:
- Predicts functional consequence
- Output: missense, frameshift, splice, etc.
- Add custom annotations (CADD, conservation scores)
- Pipeline integration: `vep --input_file variants.vcf`

**SnpEff**:
- Built-in databases for consequences
- Faster than VEP
- Annotation categories: HIGH, MODERATE, LOW, MODIFIER
- Output: Standard SNPEFF format in VCF

**ANNOVAR**:
- Rapid variant annotation
- Database selection flexible
- Custom annotation compatible
- Efficient for large-scale annotation

### Consequence Classification
| Category | Impact | Examples |
|----------|--------|----------|
| HIGH | Significant protein change | Frameshift, stop gained/lost, splice site |
| MODERATE | Missense variant | Amino acid substitution |
| LOW | Minimal impact | Synonymous, in-frame indel |
| MODIFIER | Likely benign | Intronic, intergenic |

## Quality Metrics Interpretation

**Sequencing Depth**:
- **Whole Genome (WGS)**: 30x average typical
- **Whole Exome (WES)**: 100x average typical
- **Targeted Panel**: 500x-1000x+ for sensitivity
- **Rule**: Coverage increases with decreasing target size

**Coverage Gaps**:
- **Repeat Regions**: GC-rich, homopolymeric sequences
- **Segmental Duplications**: Paralogous alignment challenges
- **Pseudogenes**: Incorrect mapping possible
- **Tandem Repeats**: Short read alignment ambiguity

**Concordance Metrics**:
- **SNP Concordance**: Typically >99.9% with validation
- **Indel Concordance**: Variable, depends on size/complexity
- **Large Variant Concordance**: Structural variants more variable
- **Pipeline Reproducibility**: Should be >99% for clinical use

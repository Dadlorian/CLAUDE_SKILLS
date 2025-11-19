# Technology-Assisted Review (TAR) Implementation Guide

## Overview

This guide provides a step-by-step framework for implementing Technology-Assisted Review (TAR), also known as predictive coding, in e-discovery matters. TAR can reduce review costs by 50-80% while maintaining or improving accuracy compared to linear review.

## Pre-Implementation Assessment

### Is TAR Appropriate for This Matter?

**Good Candidates for TAR**:
- Large document volumes (>50,000 documents)
- Clear relevance definitions
- Sufficient budget for setup and validation
- Sophisticated opposing counsel (or court approval possible)
- Time for protocol development and cooperation

**Poor Candidates for TAR**:
- Small document collections (<10,000 documents)
- Extremely low richness (<1% relevant)
- Unclear or shifting relevance definitions
- Hostile opposing counsel without court support
- Rush productions with no time for setup

### Cost-Benefit Analysis

**Linear Review Costs**:
```
Documents: 500,000
Review rate: 50 docs/hour
Hours required: 10,000 hours
Rate: $75/hour (contract attorney)
Total cost: $750,000
Timeline: ~6 months with 10 reviewers
```

**TAR Review Costs**:
```
Documents: 500,000
Training set: ~5,000 docs @ $150/hour = $15,000
Prioritized review: ~100,000 docs @ $75/hour = $150,000
Validation: $10,000
TAR platform: $20,000
Total cost: $195,000
Savings: $555,000 (74% reduction)
Timeline: ~2-3 months
```

## TAR Protocol Development

### Step 1: Establish TAR Team

**Key Roles**:
- **Senior Attorney**: Defines relevance, performs training reviews
- **TAR Coordinator**: Manages workflow, monitors metrics
- **Platform Specialist**: Configures TAR, runs analytics
- **QC Lead**: Validates results, performs elusion testing
- **Client Representative**: Approves major decisions

### Step 2: Define Relevance Criteria

**Relevance Definition Template**:
```
Matter: Acme Corp. v. Widget Inc.
Relevant Document Definition:

INCLUDED:
- Documents relating to the Widget 3000 product development
- Communications between Acme and Widget regarding licensing
- Financial documents showing Widget 3000 revenues
- Documents discussing the patent at issue (US Patent 9,876,543)

EXCLUDED:
- Documents dated before January 1, 2020
- Documents relating to other Widget products
- General corporate communications not related to Widget 3000
- Documents in languages other than English (separate protocol)

EDGE CASES:
- Widget 3000 mentioned in passing → NOT RELEVANT (unless substantive discussion)
- Internal Acme communications about Widget 3000 → RELEVANT
- News articles about Widget 3000 → RELEVANT if circulated internally with comments
```

**Coding Guidelines**:
- Create detailed coding manual with examples
- Include screenshots of relevant vs. non-relevant documents
- Address edge cases explicitly
- Get agreement from all reviewers
- Update as needed during training

### Step 3: Select TAR Methodology

**TAR 1.0 (Traditional)**:
- Create seed set (1,000-3,000 documents)
- Multiple training rounds
- Control set for validation
- Batch-based learning

**TAR 2.0 (Continuous Active Learning - CAL)**:
- Small initial batch or no seed set
- Continuous learning from each decision
- One-pass review
- Real-time prioritization

**Recommendation**: TAR 2.0/CAL for most modern matters (more efficient)

### Step 4: Platform Selection and Configuration

**TAR Platform Options**:
- Relativity Active Learning
- Everlaw Predictive Coding
- CS Disco AI
- Brainspace CAL
- Reveal AI

**Configuration**:
- Enable TAR/Active Learning module
- Set up training workspace
- Configure relevance coding fields
- Establish validation workflows
- Set up metrics dashboards

## Implementation Workflow (TAR 2.0/CAL)

### Phase 1: Initial Setup (Days 1-2)

**Activities**:
1. Load processed documents into review platform
2. Configure TAR project in platform
3. Define relevance coding (Relevant/Not Relevant)
4. Set aside random control set (2,500-5,000 docs)
5. Create initial review batch (500-1,000 docs)

**Control Set**:
- Random sample of collection
- Set aside before training begins
- Do NOT use for training
- Use only for final validation
- Typically 2,500-5,000 documents for statistical validity

**Initial Batch Creation**:
- Random sample OR
- Keyword-driven sample OR
- Judgmentally selected sample
- Goal: Seed the algorithm with some relevant documents

### Phase 2: Training Phase (Days 3-14)

**Day 3-5: Initial Training**:
1. Senior attorney reviews initial batch (500-1,000 docs)
2. Code each document as Relevant or Not Relevant
3. Follow coding guidelines strictly
4. Document difficult decisions
5. Submit coding to algorithm

**Day 6-10: Continuous Review**:
1. Algorithm prioritizes next documents for review
2. Review prioritized documents (500-1,000 per day)
3. System learns from each coding decision
4. Model continuously updates and re-ranks
5. Monitor metrics daily

**Day 11-14: Stabilization**:
1. Continue reviewing prioritized documents
2. Watch for metrics stabilization
3. Recall and precision estimates should converge
4. Elusion rate (relevant docs in non-reviewed set) should decrease
5. Determine readiness for validation

**Daily Training Review**:
```
Day  | Docs Reviewed | Cumulative | Relevant % | Estimated Recall | Estimated Precision
---------------------------------------------------------------------------------------
1    | 500          | 500        | 35%        | 15%             | N/A
2    | 500          | 1,000      | 28%        | 28%             | N/A
3    | 500          | 1,500      | 22%        | 38%             | 72%
4    | 500          | 2,000      | 18%        | 46%             | 75%
5    | 500          | 2,500      | 15%        | 53%             | 77%
...
14   | 500          | 7,000      | 5%         | 78%             | 81%
```

### Phase 3: Metrics Monitoring

**Key Metrics to Track**:

**Estimated Recall**:
- Percentage of relevant documents found
- Goal: Typically 75-85%+ (case-dependent)
- Increases as training continues

**Estimated Precision**:
- Of documents predicted relevant, how many actually are?
- Goal: 70-85%
- Should remain relatively stable

**Richness**:
- Percentage of relevant documents in collection
- Helps estimate total relevant documents
- Example: 5% richness in 500K docs = ~25,000 relevant docs

**Rank Cutoff**:
- Score above which documents are likely relevant
- Typically 50-70 on 0-100 scale
- Used to categorize documents

**Elusion Rate**:
- Estimate of relevant documents in non-reviewed set
- Should decrease as training progresses
- Goal: <5% elusion in the discard pile

**F1 Score**:
- Harmonic mean of precision and recall
- Single metric for overall performance
- Goal: >0.75

### Phase 4: Stopping Criteria (Day 15)

**When to Stop Training**:

**Quantitative Indicators**:
- Recall estimate >75% (or target threshold)
- Precision estimate stable (±5% for several days)
- Elusion rate <5% in non-reviewed set
- Diminishing returns (few relevant docs in recent batches)
- Statistical stability (confidence intervals narrow)

**Qualitative Indicators**:
- Senior reviewer confidence in model
- Recent review mostly non-relevant documents
- Similar documents being ranked low
- Team consensus on completeness

**Example Stopping Decision**:
```
Training Summary After 7,000 Documents Reviewed:

Estimated Recall: 78% (±4% at 95% confidence)
Estimated Precision: 81%
F1 Score: 0.795
Elusion Rate: 4.2%
Relevant Documents Found: 19,500 (est. total: 25,000)
Recent 500 Documents: 4% relevant (diminishing returns)

Decision: PROCEED TO VALIDATION
Rationale: Metrics stable, recall target achieved, diminishing returns evident
```

### Phase 5: Validation (Days 16-20)

**Validation Methods**:

**1. Control Set Validation**:
- Review reserved control set (2,500-5,000 docs)
- Code without seeing TAR predictions
- Compare coding to TAR predictions
- Calculate actual precision and recall

**Control Set Results**:
```
Control Set Size: 3,000 documents
Human Coded as Relevant: 150 documents
TAR Predicted as Relevant: 900 documents (in full collection)

True Positives: 135 (human relevant, TAR predicted relevant)
False Positives: 15 (human not relevant, TAR predicted relevant)
False Negatives: 15 (human relevant, TAR predicted not relevant)
True Negatives: 2,835 (human not relevant, TAR predicted not relevant)

Actual Precision: 135 / 150 = 90%
Actual Recall: 135 / 150 = 90%
F1 Score: 0.90

Conclusion: Model performs well, validated for use
```

**2. Elusion Testing**:
- Random sample from predicted non-relevant set
- Review sample for missed relevant documents
- Calculate percentage of relevant in discard pile
- Goal: <5% elusion

**Elusion Test**:
```
Sample Size: 1,000 documents from predicted non-relevant set
Relevant Found: 38 documents

Elusion Rate: 38 / 1,000 = 3.8%
Estimated Missed Relevant Docs: 3.8% × 300,000 non-reviewed = 11,400

Comparison to Training Estimate: Within expected range
Conclusion: Acceptable elusion rate
```

**3. Sample Review of High-Scoring Documents**:
- Review random sample of high-scoring documents
- Confirm they are actually relevant
- Validates precision

### Phase 6: Production Decision (Day 21)

**Production Options**:

**Option 1: Categorical Cutoff**:
- Produce all documents above relevance threshold
- Example: All docs scored 60+ out of 100
- Simplest approach
- May include some non-relevant (acceptable per Rule 26)

**Option 2: Prioritized Review to Budget**:
- Review documents in rank order
- Stop when budget exhausted or diminishing returns
- Produce only reviewed relevant documents
- More defensible but less efficient

**Option 3: Hybrid Approach**:
- High confidence relevant (e.g., 80+ score): Auto-produce
- Medium confidence (e.g., 40-80): Manual review
- Low confidence (<40): Presumed not relevant, sample validate

**Example Production Decision**:
```
Total Documents: 500,000
Relevant Threshold: Score 55+
Documents Above Threshold: 110,000

Production Approach: Hybrid
- Score 75+: 35,000 documents → Auto-produce (with privilege review)
- Score 55-74: 75,000 documents → Manual review (expect 60% relevant = 45,000)
- Score <55: 390,000 documents → Withheld, elusion tested

Total Produced (est.): 80,000 documents
Review Required: 110,000 documents (vs. 500,000 linear)
Cost Savings: 78% reduction in review volume
```

### Phase 7: Documentation

**TAR Protocol Document Should Include**:

1. **Methodology**
   - TAR approach (1.0 vs. 2.0)
   - Platform and version
   - Algorithmic approach (high-level)

2. **Relevance Definition**
   - Detailed relevance criteria
   - Examples of relevant/not relevant
   - Edge case handling

3. **Training Process**
   - Training set size and selection
   - Review team composition
   - Quality control measures
   - Dates of training

4. **Metrics and Results**
   - Precision and recall estimates
   - F1 scores
   - Elusion rates
   - Stability indicators

5. **Validation**
   - Control set approach
   - Sample sizes
   - Actual precision and recall
   - Statistical confidence levels

6. **Production Decision**
   - Cutoff score and rationale
   - Documents produced
   - Documents withheld
   - Defensibility analysis

## Cooperation with Opposing Counsel

### Rule 26(f) Discussion

**Topics to Discuss**:
- Intent to use TAR
- High-level methodology
- Transparency approach
- Validation methodology
- Willingness to share metrics (not training documents)

**Cooperation Best Practices**:
- Propose TAR early
- Explain benefits (cost savings, quality)
- Offer transparency (process, not privileged content)
- Share protocol document
- Invite input on validation
- Seek agreement rather than court approval if possible

### Transparency vs. Privilege

**Share**:
- TAR methodology and protocol
- Relevance definitions
- Validation metrics (precision, recall, F1)
- Sample sizes and approach
- Platform and algorithms used (high-level)

**Protect** (Work Product):
- Specific training documents and coding
- Attorney reasoning and notes
- Privileged communications about relevance
- Strategic decisions

### Court Approval

**If Opposing Counsel Objects**:
- Cite precedent (Da Silva Moore, Rio Tinto, Hyles)
- Offer validation concessions
- Propose special master or neutral expert
- File motion for TAR approval
- Provide expert declaration if needed

## Quality Control

### Ongoing QC During Training

**Daily Review**:
- Senior attorney spot-checks coding decisions
- Review edge cases with team
- Discuss difficult documents
- Ensure consistency

**Weekly Calibration**:
- Team reviews same 50 documents
- Compare coding decisions
- Discuss discrepancies
- Align on approach
- Update coding guidelines

**Metrics Review**:
- Daily metrics dashboard review
- Watch for instability or unexpected trends
- Investigate anomalies
- Adjust if needed

### Post-TAR QC

**Random Sample of Production Set**:
- Sample 1-2% of documents to be produced
- Senior review for relevance confirmation
- Identify any systematic errors
- Correct if needed

**Privilege Screening**:
- TAR for responsiveness only
- Separate privilege review process
- Consider privilege TAR model (separate from responsiveness)
- Attorney review of all potentially privileged documents

## Common Challenges and Solutions

### Challenge: Low Richness (<2% relevant)

**Problem**: Difficult to train model with few relevant examples

**Solutions**:
- Use keyword searches to seed relevant documents
- Consider if TAR appropriate (may not be)
- Expect longer training period
- Supplement with concept clustering
- Document challenges and decisions

### Challenge: Shifting Relevance Definitions

**Problem**: Relevance definition changes mid-project

**Solutions**:
- Re-train model with new definition
- Document reason for change
- May need to re-review some documents
- Communicate change to opposing counsel
- Update protocol and timeline

### Challenge: Inconsistent Coding

**Problem**: Multiple reviewers, inconsistent decisions

**Solutions**:
- Single senior reviewer for all training (ideal)
- Strict coding guidelines
- Daily calibration
- Second-pass QC
- Document decisions

### Challenge: Opposing Counsel Resistance

**Problem**: Opposing counsel objects to TAR

**Solutions**:
- Educate on TAR benefits and acceptance
- Provide case law and precedent
- Offer enhanced validation
- Seek court approval with expert support
- Propose neutral validation expert

## Cost and Time Estimates

### Typical TAR Project Timeline

```
Phase                           Duration        FTE
-------------------------------------------------
Protocol Development            3-5 days        0.5
Platform Setup                  1-2 days        0.25
Initial Batch Review            2-3 days        1.0
Training Review                 7-10 days       1.0
Validation                      3-5 days        0.5
Documentation                   2-3 days        0.5
-------------------------------------------------
Total Project Duration          3-4 weeks
```

### Cost Breakdown Example

```
Activity                  Cost            Notes
-------------------------------------------------
Platform TAR License      $15,000         One-time or included
Senior Attorney Time      $30,000         Training reviews (120 hrs @ $250)
TAR Coordinator           $10,000         Monitoring, metrics (80 hrs @ $125)
Validation                $8,000          Control set review
Expert Declaration        $5,000          If needed for court
-------------------------------------------------
TAR Setup & Validation    $68,000

Prioritized Review        $120,000        80,000 docs @ $1.50/doc
Production                $10,000
-------------------------------------------------
Total TAR Project Cost    $198,000

Linear Review Comparison  $750,000        500K docs @ $1.50/doc
Savings                   $552,000        74% cost reduction
```

## Success Factors

1. **Clear Relevance Definition**: Unambiguous, well-documented criteria
2. **Experienced Reviewer**: Senior attorney who understands case
3. **Consistent Coding**: Discipline in applying guidelines
4. **Adequate Training**: Sufficient training documents (5,000-10,000)
5. **Metrics Monitoring**: Daily review of performance metrics
6. **Validation Rigor**: Robust validation methodology
7. **Documentation**: Thorough protocol and process documentation
8. **Cooperation**: Work with opposing counsel proactively
9. **Platform Expertise**: Understanding of TAR platform capabilities
10. **Patience**: Allow time for model to learn and stabilize

## Conclusion

TAR is a powerful tool for reducing e-discovery costs while maintaining or improving quality. Successful TAR implementation requires careful planning, rigorous training, consistent coding, robust validation, and thorough documentation. By following this guide and adapting to case-specific needs, practitioners can achieve significant cost savings and deliver defensible, efficient e-discovery results.

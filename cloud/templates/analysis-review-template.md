# [Skill Name] - Analysis & Review Pattern

## Purpose
[One-sentence description of what this skill analyzes]

## Scope

**In Scope**:
- [What will be analyzed]
- [What will be analyzed]

**Out of Scope**:
- [What won't be analyzed]
- [What won't be analyzed]

## Configuration

Analysis parameters:
- `depth`: "surface" | "standard" | "deep"
- `focus_areas`: [List of areas to prioritize]
- `output_format`: "markdown" | "json" | "html"
- `severity_threshold`: "low" | "medium" | "high" | "critical"

## Analysis Framework

### Phase 1: Initial Assessment

**Objective**: Get a high-level understanding of the codebase/system

1. **Scope Identification**
   - Scan directory structure
   - Identify entry points
   - Map dependencies
   - Count metrics: [lines of code, files, modules, etc.]

2. **Technology Detection**
   - Identify languages: [How to detect]
   - Identify frameworks: [Where to look]
   - Identify build tools: [What to check]

3. **Quick Scan**
   - Look for obvious issues
   - Identify patterns used
   - Note architectural style

**Initial Assessment Output**:
```
Project: [name]
Size: [metrics]
Technologies: [list]
Architecture: [description]
Complexity: [rating]
```

---

### Phase 2: Deep Analysis

Apply multiple analytical lenses:

#### Lens 1: [Analysis Aspect, e.g., "Security"]

**What to check**:
- [ ] [Specific security concern]
- [ ] [Specific security concern]
- [ ] [Specific security concern]

**How to check**:
1. Search for patterns: [regex or keywords]
2. Examine: [specific files or functions]
3. Validate: [what to validate]

**Severity Rating**:
- **Critical**: [Criteria for critical issues]
- **High**: [Criteria for high severity]
- **Medium**: [Criteria for medium severity]
- **Low**: [Criteria for low severity]

**Documentation format**:
```markdown
### [Issue Category]

**Severity**: [level]
**Location**: [file:line]
**Description**: [what's wrong]
**Impact**: [why it matters]
**Recommendation**: [how to fix]

Code snippet:
\`\`\`
[relevant code]
\`\`\`
```

---

#### Lens 2: [Analysis Aspect, e.g., "Performance"]

**What to check**:
- [ ] [Specific performance concern]
- [ ] [Specific performance concern]
- [ ] [Specific performance concern]

**How to check**:
1. Identify hotspots: [How to find them]
2. Measure complexity: [What to measure]
3. Check patterns: [What patterns indicate issues]

**Severity Rating**:
- **Critical**: [e.g., "O(n²) in tight loops"]
- **High**: [e.g., "Unnecessary database queries"]
- **Medium**: [e.g., "Suboptimal algorithms"]
- **Low**: [e.g., "Minor optimizations possible"]

---

#### Lens 3: [Analysis Aspect, e.g., "Code Quality"]

**What to check**:
- [ ] [Specific quality metric]
- [ ] [Specific quality metric]
- [ ] [Specific quality metric]

**How to check**:
1. Check conventions: [What conventions]
2. Measure metrics: [What metrics]
3. Review patterns: [What patterns]

**Quality Metrics**:
- Complexity: [How to measure]
- Duplication: [How to detect]
- Test Coverage: [How to calculate]
- Documentation: [What to assess]

---

### Phase 3: Synthesis & Recommendations

**Objective**: Consolidate findings and provide actionable guidance

1. **Categorize Findings**
   - Group by: [severity/type/component]
   - Sort by: [priority criteria]
   - Filter by: [threshold]

2. **Identify Patterns**
   - Common issues: [What repeats]
   - Root causes: [Why they exist]
   - Systemic problems: [Broader concerns]

3. **Prioritize Recommendations**
   - **Must Fix** (Critical/High):
     - [Recommendation with reasoning]
     - [Recommendation with reasoning]

   - **Should Fix** (Medium):
     - [Recommendation with reasoning]
     - [Recommendation with reasoning]

   - **Could Improve** (Low):
     - [Recommendation with reasoning]
     - [Recommendation with reasoning]

4. **Estimate Effort**
   For each recommendation:
   - Effort: [Small/Medium/Large]
   - Impact: [Low/Medium/High]
   - Priority: [Calculated from effort and impact]

---

## Output Format

### Executive Summary
[2-3 sentences summarizing the analysis]

**Key Metrics**:
- Files analyzed: [number]
- Issues found: [breakdown by severity]
- Overall rating: [rating with explanation]

---

### Critical Issues

[For each critical issue:]

#### Issue #[N]: [Title]
**Severity**: Critical
**Category**: [Security/Performance/Quality/etc.]
**Location**: `[file:line]`

**Description**:
[Clear explanation of the issue]

**Impact**:
[Why this is critical]

**Code**:
```[language]
[problematic code snippet]
```

**Recommendation**:
[Specific fix with code example if applicable]

---

### Medium/Low Issues

[Grouped by category, summarized format]

---

### Positive Observations

What's working well:
- [Good practice observed]
- [Good practice observed]
- [Good practice observed]

---

### Recommendations Summary

**Immediate Action Required**:
1. [Priority 1 fix]
2. [Priority 2 fix]

**Short-term Improvements** (1-2 weeks):
1. [Improvement]
2. [Improvement]

**Long-term Enhancements** (1-3 months):
1. [Enhancement]
2. [Enhancement]

---

## Validation

Before finalizing the analysis:
- [ ] All files in scope reviewed
- [ ] Severity ratings consistent
- [ ] Recommendations are actionable
- [ ] Code examples are accurate
- [ ] No false positives included

## Follow-up

Suggest next steps:
- Re-analyze after fixes applied
- Deep dive into specific areas
- Automated monitoring setup
- Regular review schedule

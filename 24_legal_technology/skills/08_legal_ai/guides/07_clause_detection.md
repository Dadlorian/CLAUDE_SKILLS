# Clause Detection and Classification

## Overview
Automatically detect and classify contract clauses.

## Clause Types
1. **Risk Clauses**: Indemnification, Liability, Warranties
2. **Commercial**: Payment, Pricing, Delivery
3. **Termination**: For cause, for convenience, notice periods
4. **IP**: Ownership, licenses, restrictions
5. **Compliance**: Confidentiality, regulatory, audit
6. **Dispute**: Arbitration, venue, governing law

## Detection Methods

### Pattern-Based
```python
clause_patterns = {
    "indemnification": [
        r"indemnif[yz]",
        r"hold harmless",
        r"defend.*against.*claims"
    ],
    "limitation_of_liability": [
        r"liability.*not exceed",
        r"in no event.*liable",
        r"cap on damages"
    ]
}
```

### ML Classification
1. Split contract into sentences
2. Classify each sentence
3. Merge related sentences into clauses

### Hybrid Approach
- Use patterns for high-confidence matches
- Use ML for ambiguous cases
- Human review for novel clauses

## Extraction Quality
- **Precision**: 92%+ (few false positives)
- **Recall**: 88%+ (catch most clauses)
- **Boundary Detection**: 85%+ (correct clause boundaries)

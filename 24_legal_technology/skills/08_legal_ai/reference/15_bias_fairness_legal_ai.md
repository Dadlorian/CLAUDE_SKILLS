# Bias and Fairness in Legal AI

## Types of Bias

### 1. Historical Bias
Legal training data reflects historical inequities in the legal system.

**Example**: Criminal sentencing data includes racial disparities

**Mitigation**: 
- Identify biased patterns in training data
- Consider synthetic balanced datasets
- Apply fairness constraints during training

### 2. Representational Bias
Training data doesn't represent all populations equally.

**Example**: More data from large law firms than small firms or public defenders

**Mitigation**:
- Ensure diverse data sources
- Oversample underrepresented groups
- Test on out-of-distribution data

### 3. Measurement Bias
Features or labels are measured differently across groups.

**Example**: "Case complexity" measured differently by firm size

**Mitigation**:
- Standardize measurement across groups
- Use multiple measurement methods
- Validate with domain experts

## Fairness Metrics

### Disparate Impact (80% Rule)
Selection rate for protected group must be ≥80% of highest group.

```python
protected_approval_rate / highest_approval_rate >= 0.8
```

### Demographic Parity
Equal approval rates across all demographic groups.

```python
P(Y=1 | A=0) = P(Y=1 | A=1)
```

### Equalized Odds
Equal true positive and false positive rates across groups.

```python
P(Ŷ=1 | Y=1, A=0) = P(Ŷ=1 | Y=1, A=1)
P(Ŷ=1 | Y=0, A=0) = P(Ŷ=1 | Y=0, A=1)
```

## Testing for Bias

### Audit Process
1. Identify protected characteristics (race, gender, age, etc.)
2. Test model performance across groups
3. Calculate fairness metrics
4. If bias detected, apply mitigation
5. Retest and document

### Continuous Monitoring
- Regular bias audits (quarterly)
- Track disparate impact over time
- Monitor for emerging biases
- Update models as needed

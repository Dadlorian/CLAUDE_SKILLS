# Predictive Maintenance Reference

## Condition-Based Monitoring

### HVAC Equipment

**Monitored Parameters**:
- Supply/return air temperature
- Power consumption
- Runtime hours
- Vibration (for rotating equipment)
- Refrigerant pressure
- Filter pressure drop

**Failure Indicators**:
- Temperature delta outside normal range
- Power consumption spike or drift
- Excessive runtime
- Vibration increase

### Anomaly Detection Algorithms

**Statistical Methods**:
- Z-score: Deviations from mean
- Moving average: Trend detection
- Regression: Expected vs actual

**Machine Learning**:
- Isolation Forest: Outlier detection
- LSTM: Time-series anomalies
- Random Forest: Multi-variate analysis

## Maintenance Triggers

### Schedule-Based
- Filter replacement: Every 90 days
- Belt inspection: Every 6 months
- Refrigerant check: Annual

### Condition-Based
- Filter change when pressure drop > 0.5 in H2O
- Belt replacement when vibration increases 20%
- Refrigerant when pressure deviates > 10%

### Predictive
- ML model predicts failure within 30 days
- Create work order proactively

## ROI Metrics

| Metric | Traditional | Predictive |
|--------|------------|------------|
| Maintenance cost | $3.50/sqft | $2.50/sqft |
| Equipment uptime | 95% | 99%+ |
- Emergency repairs | 40% | 10% |
| Equipment life | 15 years | 20 years |

## Implementation Steps

1. **Baseline**: Collect 3-6 months of data
2. **Model**: Train anomaly detection
3. **Thresholds**: Set alert levels
4. **Integration**: Connect to CMMS
5. **Validation**: Monitor false positive rate
6. **Refinement**: Continuous improvement

## See Also
- sensor_types.md
- energy_metrics.md
- hvac_basics.md

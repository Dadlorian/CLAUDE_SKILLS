# Data Quality Management Guide

## Data Quality Framework

### Dimensions of Data Quality

1. **Completeness**: Presence of required data elements
2. **Accuracy**: Correctness of data values
3. **Consistency**: Logical coherence across systems
4. **Timeliness**: Data availability when needed
5. **Validity**: Conformance to defined formats/ranges

## Implementation

### Data Quality Rules

```python
dq_rules = {
    'patient': {
        'required_fields': ['mrn', 'date_of_birth', 'gender'],
        'format_rules': {
            'mrn': r'^\d{7}$',
            'date_of_birth': 'YYYY-MM-DD',
            'gender': ['M', 'F', 'U', 'O']
        },
        'range_rules': {
            'date_of_birth': {'min': '1900-01-01', 'max': 'today'},
            'age': {'min': 0, 'max': 120}
        }
    },
    'encounter': {
        'required_fields': ['encounter_id', 'patient_id', 'admission_date'],
        'consistency_rules': {
            'discharge_date_after_admission': 'discharge_date >= admission_date',
            'dates_within_observation': 'admission_date within observation_period'
        }
    }
}
```

### Data Quality Monitoring

```sql
-- Completeness check
SELECT
    'Patient SSN Completeness' AS metric,
    COUNT(*) AS total_records,
    COUNT(ssn) AS populated,
    ROUND(100.0 * COUNT(ssn) / COUNT(*), 2) AS completeness_pct
FROM dim_patient;

-- Consistency check
SELECT
    'Invalid Date Sequences' AS metric,
    COUNT(*) AS violation_count
FROM fact_encounter
WHERE discharge_date < admission_date;
```

### Data Quality Scorecard

```
Overall DQ Score: Weighted average across dimensions
- Completeness: 95%
- Accuracy: 92%
- Consistency: 98%
- Timeliness: 90%
- Validity: 96%

Composite Score: 94.2%
```

---

*Data Quality Management Guide*

# Clinical Analytics Use Cases Reference

## Overview

Clinical analytics transforms healthcare data into actionable insights for improving patient outcomes, optimizing operations, and reducing costs across the care continuum.

## Care Quality Improvement

### Diabetes Care Optimization

**Problem**: Suboptimal diabetes control leads to complications and increased costs

**Analytics Approach:**
1. **Cohort Identification**
   - Identify all patients with diabetes (Type 1, Type 2, gestational)
   - Segment by control level (HbA1c <7%, 7-8%, 8-9%, >9%)
   - Flag patients at high risk for complications

2. **Gap Analysis**
   ```sql
   -- Identify patients needing interventions
   SELECT
       p.patient_key,
       p.patient_name,
       d.most_recent_hba1c,
       d.last_hba1c_date,
       d.last_eye_exam_date,
       d.last_foot_exam_date,
       d.on_statin,
       d.on_ace_or_arb,
       CASE
           WHEN DATEDIFF(day, d.last_hba1c_date, GETDATE()) > 180
                THEN 'HbA1c Due'
           WHEN d.most_recent_hba1c > 9.0
                THEN 'Poor Control - Urgent'
           WHEN d.most_recent_hba1c > 8.0
                THEN 'Suboptimal Control'
           ELSE 'Controlled'
       END AS control_status,
       CASE
           WHEN DATEDIFF(day, d.last_eye_exam_date, GETDATE()) > 365
                THEN 'Eye Exam Due'
       END AS eye_exam_status
   FROM dim_patient p
   JOIN diabetes_registry d ON p.patient_key = d.patient_key
   WHERE d.active_diabetes = 1
       AND (d.most_recent_hba1c > 8.0
            OR DATEDIFF(day, d.last_hba1c_date, GETDATE()) > 180
            OR DATEDIFF(day, d.last_eye_exam_date, GETDATE()) > 365)
   ORDER BY d.most_recent_hba1c DESC;
   ```

3. **Intervention Tracking**
   - Outreach calls logged
   - Appointment scheduling
   - Medication adjustments
   - Diabetes education completion

4. **Outcome Measurement**
   ```python
   # Measure improvement over time
   def measure_diabetes_improvement(baseline_date, follow_up_date):
       baseline = get_cohort_metrics(baseline_date)
       followup = get_cohort_metrics(follow_up_date)

       return {
           'hba1c_control_improvement': (
               followup['pct_hba1c_lt_8'] - baseline['pct_hba1c_lt_8']
           ),
           'poor_control_reduction': (
               baseline['pct_hba1c_gt_9'] - followup['pct_hba1c_gt_9']
           ),
           'eye_exam_improvement': (
               followup['eye_exam_rate'] - baseline['eye_exam_rate']
           ),
           'patients_improved': followup['patients_controlled'] - baseline['patients_controlled']
       }
   ```

**Expected Impact:**
- 10-15% improvement in HbA1c control rates
- 20-30% increase in eye exam completion
- 5-10% reduction in diabetes-related ED visits

### Heart Failure Readmission Reduction

**Problem**: 25% of CHF patients readmitted within 30 days

**Analytics Strategy:**

1. **Risk Stratification**
   ```python
   def calculate_chf_readmission_risk(patient_id, discharge_id):
       features = {
           # Clinical
           'ejection_fraction': get_latest_ef(patient_id),
           'bnp_at_discharge': get_discharge_bnp(discharge_id),
           'nyha_class': get_nyha_classification(patient_id),
           'comorbidity_count': get_comorbidity_count(patient_id),

           # Utilization history
           'prior_chf_admits_6mo': count_prior_chf_admits(patient_id, months=6),
           'ed_visits_6mo': count_ed_visits(patient_id, months=6),

           # Social determinants
           'lives_alone': get_lives_alone_status(patient_id),
           'medication_adherence_pdc': get_med_adherence(patient_id),

           # Discharge factors
           'length_of_stay': get_los(discharge_id),
           'discharged_on_weekend': is_weekend_discharge(discharge_id)
       }

       risk_score = chf_readmission_model.predict_proba([features])[0][1]
       return risk_score
   ```

2. **Care Transitions Program**
   ```
   High Risk (>40% predicted readmission):
   - Discharge planning starts 48 hours pre-discharge
   - Home health nurse visit within 24-48 hours
   - Telehealth follow-up within 3 days
   - PCP appointment within 7 days
   - Daily weight monitoring
   - Medication reconciliation

   Medium Risk (20-40%):
   - Phone call within 48 hours
   - PCP appointment within 14 days
   - Educational materials
   - Self-monitoring instructions
   ```

3. **Monitoring Dashboard**
   ```
   CHF Readmission Dashboard:
   - 30-day readmission rate (rolling)
   - Risk score distribution
   - Intervention completion rates
   - Patients by risk tier
   - Upcoming discharge list with risk scores
   ```

**Measured Outcomes:**
- 30-40% reduction in 30-day CHF readmissions
- $1,500-$2,500 cost savings per avoided readmission
- Improved patient satisfaction scores

### Sepsis Bundle Compliance

**Problem**: Delayed sepsis recognition and treatment increases mortality

**Analytics Solution:**

1. **Real-Time Sepsis Surveillance**
   ```python
   class SepsisSurveillance:
       def __init__(self):
           self.screening_interval = 3600  # seconds (1 hour)

       def screen_patient(self, patient_id):
           vitals = get_current_vitals(patient_id)
           labs = get_recent_labs(patient_id, hours=6)

           # Calculate qSOFA
           qsofa_score = 0
           if vitals['respiratory_rate'] >= 22:
               qsofa_score += 1
           if vitals['sbp'] <= 100:
               qsofa_score += 1
           if vitals['gcs'] < 15:
               qsofa_score += 1

           # Check for infection suspicion
           infection_suspected = (
               has_recent_cultures_ordered(patient_id) or
               on_antibiotics(patient_id) or
               has_infection_diagnosis(patient_id)
           )

           # Sepsis criteria
           if qsofa_score >= 2 and infection_suspected:
               trigger_sepsis_alert(patient_id, 'Suspected Sepsis', qsofa_score)
               return True

           # Check lactate if high risk
           if qsofa_score >= 1 and infection_suspected:
               if labs.get('lactate', 0) >= 2.0:
                   trigger_sepsis_alert(patient_id, 'Sepsis - Elevated Lactate', qsofa_score)
                   return True

           return False
   ```

2. **Bundle Compliance Tracking**
   ```sql
   -- Track SEP-1 bundle compliance
   WITH sepsis_cohort AS (
       SELECT
           encounter_key,
           sepsis_recognition_time,
           blood_culture_time,
           lactate_time,
           antibiotic_time,
           fluid_bolus_time
       FROM fact_sepsis_bundle
       WHERE sepsis_recognition_date >= '2023-01-01'
   ),
   bundle_compliance AS (
       SELECT
           encounter_key,
           -- 3-hour bundle
           CASE WHEN
               DATEDIFF(minute, sepsis_recognition_time, blood_culture_time) <= 180 AND
               DATEDIFF(minute, sepsis_recognition_time, lactate_time) <= 180 AND
               DATEDIFF(minute, sepsis_recognition_time, antibiotic_time) <= 180
               THEN 1 ELSE 0
           END AS bundle_3hr_compliant,
           -- 6-hour bundle (if severe sepsis/shock)
           CASE WHEN
               DATEDIFF(minute, sepsis_recognition_time, fluid_bolus_time) <= 360
               THEN 1 ELSE 0
           END AS bundle_6hr_compliant
       FROM sepsis_cohort
   )
   SELECT
       COUNT(*) AS total_sepsis_cases,
       SUM(bundle_3hr_compliant) AS bundle_3hr_met,
       ROUND(100.0 * SUM(bundle_3hr_compliant) / COUNT(*), 1) AS bundle_3hr_rate,
       SUM(bundle_6hr_compliant) AS bundle_6hr_met,
       ROUND(100.0 * SUM(bundle_6hr_compliant) / COUNT(*), 1) AS bundle_6hr_rate
   FROM bundle_compliance;
   ```

3. **Performance Feedback**
   - Provider-level sepsis recognition time
   - Unit-level bundle compliance
   - Time-to-antibiotic tracking
   - Mortality rate by compliance status

**Impact:**
- Improve 3-hour bundle compliance from 60% to >85%
- Reduce sepsis mortality by 15-20%
- Decrease ICU length of stay by 1-2 days

## Operational Efficiency

### Emergency Department Throughput

**Problem**: Long ED wait times, boarding, left without being seen (LWBS)

**Key Metrics:**
```python
ed_metrics = {
    # Volume
    'ed_arrivals': 'Total ED arrivals',
    'ed_admissions': 'Patients admitted to hospital',
    'admission_rate': 'Admissions / Arrivals',

    # Timeliness
    'door_to_provider_time': 'Minutes from arrival to provider',
    'door_to_decision_time': 'Minutes to admit/discharge decision',
    'decision_to_departure_time': 'Minutes from decision to actual departure',
    'total_ed_los': 'Total ED length of stay',

    # Patient flow
    'patients_in_ed': 'Current ED census',
    'boarding_patients': 'Admitted patients waiting for bed',
    'lwbs_count': 'Left without being seen',
    'lwbs_rate': 'LWBS / Total arrivals',

    # Capacity
    'bed_occupancy_rate': 'Occupied beds / Total ED beds',
    'acuity_mix': 'Distribution of ESI levels'
}
```

**Analytics Dashboard:**
```sql
-- Real-time ED metrics
SELECT
    COUNT(*) AS current_ed_census,
    SUM(CASE WHEN admit_decision = 'Admit' AND inpatient_bed_assigned IS NULL
        THEN 1 ELSE 0 END) AS boarding_count,
    AVG(CASE WHEN provider_assigned_time IS NOT NULL
        THEN DATEDIFF(minute, arrival_time, provider_assigned_time)
        END) AS avg_door_to_provider,
    COUNT(CASE WHEN left_without_seen = 1 THEN 1 END) AS lwbs_count
FROM ed_realtime_census
WHERE departure_time IS NULL;
```

**Improvement Initiatives:**
1. **Fast Track for Low Acuity** (ESI 4-5)
2. **Physician Triage** (Reduce door-to-provider)
3. **Bedside Registration** (Parallel processes)
4. **Discharge Lounge** (Free up ED beds)
5. **Bed Management** (Predictive bed availability)

**Predictive Analytics:**
```python
# Forecast ED arrivals
def forecast_ed_volume(date, hour):
    """Predict ED arrivals for given date/hour"""
    features = {
        'day_of_week': date.weekday(),
        'hour': hour,
        'month': date.month,
        'is_holiday': is_holiday(date),
        'is_flu_season': is_flu_season(date),
        'local_events': check_local_events(date),
        'weather_severity': get_weather_forecast(date),
        'historical_avg': get_historical_avg(date.weekday(), hour)
    }

    predicted_arrivals = ed_volume_model.predict([features])[0]
    return predicted_arrivals

# Staffing optimization
def optimize_ed_staffing(forecast_date):
    hourly_forecast = [forecast_ed_volume(forecast_date, h) for h in range(24)]

    staffing_plan = {
        '07:00-15:00': calculate_staff_needed(hourly_forecast[7:15], role='day'),
        '15:00-23:00': calculate_staff_needed(hourly_forecast[15:23], role='evening'),
        '23:00-07:00': calculate_staff_needed(hourly_forecast[23:] + hourly_forecast[:7], role='night')
    }

    return staffing_plan
```

### Operating Room Utilization

**Problem**: Underutilized OR capacity, cases running over, first-case delays

**Key Metrics:**
```
- OR Utilization Rate: (Actual OR time / Available OR time) × 100
  Target: 75-85%

- Block Utilization: By surgeon/service
  Target: >80% (or release block)

- Turnover Time: Time between cases
  Target: <30 minutes

- First Case On-Time Starts: % starting within 15 min of scheduled
  Target: >90%

- Case Duration Variance: Actual vs. scheduled
  Target: ±15 minutes
```

**Analytics:**
```sql
-- OR utilization by surgeon
WITH or_sessions AS (
    SELECT
        surgeon_key,
        procedure_date,
        SUM(actual_duration_minutes) AS total_or_time,
        SUM(scheduled_block_minutes) AS total_block_time
    FROM fact_or_procedure
    WHERE procedure_date >= DATEADD(month, -3, GETDATE())
    GROUP BY surgeon_key, procedure_date
)
SELECT
    s.surgeon_name,
    s.specialty,
    COUNT(DISTINCT o.procedure_date) AS or_days,
    AVG(o.total_or_time) AS avg_daily_or_time,
    AVG(o.total_block_time) AS avg_block_time,
    ROUND(100.0 * AVG(o.total_or_time) / NULLIF(AVG(o.total_block_time), 0), 1) AS block_utilization_pct,
    CASE
        WHEN AVG(o.total_or_time) / NULLIF(AVG(o.total_block_time), 0) < 0.75
            THEN 'Consider Reducing Block'
        WHEN AVG(o.total_or_time) / NULLIF(AVG(o.total_block_time), 0) > 0.95
            THEN 'Consider Expanding Block'
        ELSE 'Appropriately Utilized'
    END AS recommendation
FROM or_sessions o
JOIN dim_surgeon s ON o.surgeon_key = s.surgeon_key
GROUP BY s.surgeon_name, s.specialty
ORDER BY block_utilization_pct;
```

**Predictive Case Duration:**
```python
def predict_case_duration(procedure_code, surgeon_id, patient_age, patient_bmi):
    """Predict surgical case duration"""

    # Get historical performance
    historical_cases = get_surgeon_procedure_history(surgeon_id, procedure_code)
    surgeon_avg = historical_cases['duration'].mean()
    surgeon_std = historical_cases['duration'].std()

    # Adjust for patient factors
    age_adjustment = 5 if patient_age > 70 else 0  # Older patients take longer
    bmi_adjustment = 10 if patient_bmi > 35 else 0  # Obesity increases time

    # Predict
    predicted_duration = surgeon_avg + age_adjustment + bmi_adjustment

    # Confidence interval
    lower_bound = predicted_duration - (1.5 * surgeon_std)
    upper_bound = predicted_duration + (1.5 * surgeon_std)

    return {
        'predicted_duration_minutes': round(predicted_duration),
        'lower_bound': round(lower_bound),
        'upper_bound': round(upper_bound),
        'schedule_buffer': round(0.2 * predicted_duration)  # 20% buffer
    }
```

### Bed Management & Capacity Planning

**Problem**: Bed shortages, ED boarding, elective surgery cancellations

**Analytics:**

1. **Current Bed Status**
   ```sql
   SELECT
       unit_name,
       licensed_beds,
       staffed_beds,
       occupied_beds,
       ROUND(100.0 * occupied_beds / staffed_beds, 1) AS occupancy_pct,
       staffed_beds - occupied_beds AS available_beds,
       pending_admissions,
       pending_discharges
   FROM bed_census_realtime
   ORDER BY occupancy_pct DESC;
   ```

2. **Discharge Prediction**
   ```python
   def predict_discharge_probability(encounter_id):
       """Predict likelihood of discharge today"""

       patient_data = get_patient_clinical_data(encounter_id)

       features = {
           'current_los': patient_data['length_of_stay'],
           'expected_los': patient_data['expected_los_by_drg'],
           'on_iv_medications': patient_data['iv_meds_active'],
           'recent_consults': patient_data['consults_past_24h'],
           'discharge_orders_placed': patient_data['discharge_order_placed'],
           'barriers_documented': patient_data['discharge_barriers'],
           'day_of_week': datetime.now().weekday(),
           'time_of_day': datetime.now().hour
       }

       discharge_prob = discharge_model.predict_proba([features])[0][1]

       return {
           'encounter_id': encounter_id,
           'discharge_probability': discharge_prob,
           'estimated_discharge_time': estimate_discharge_time(discharge_prob),
           'discharge_planning_status': get_discharge_planning_status(encounter_id)
       }
   ```

3. **Admission Forecasting**
   ```python
   def forecast_admissions(target_date):
       """Forecast hospital admissions for target date"""

       # Scheduled surgeries
       scheduled = get_scheduled_surgeries(target_date)
       scheduled_admits = len(scheduled) * 0.95  # Assume 5% cancellation

       # ED admissions (historical patterns)
       dow = target_date.weekday()
       month = target_date.month
       historical_ed_admits = get_historical_ed_admits(dow, month)

       # Direct admits
       expected_direct_admits = get_expected_direct_admits(target_date)

       # Total forecast
       total_forecast = (
           scheduled_admits +
           historical_ed_admits.mean() +
           expected_direct_admits
       )

       # Confidence interval
       std_error = historical_ed_admits.std()
       lower = total_forecast - (1.96 * std_error)
       upper = total_forecast + (1.96 * std_error)

       return {
           'forecast_date': target_date,
           'forecasted_admissions': round(total_forecast),
           'lower_bound': round(lower),
           'upper_bound': round(upper),
           'scheduled_surgeries': scheduled_admits,
           'expected_ed_admits': historical_ed_admits.mean(),
           'expected_direct_admits': expected_direct_admits
       }
   ```

## Population Health Management

### High-Risk Patient Identification

**Objective**: Proactively identify and manage high-risk patients

**Risk Factors:**
```python
risk_factors = {
    # Utilization
    'frequent_ed_user': 'ED visits >= 4 in past 6 months',
    'recent_hospitalization': 'Inpatient admit in past 30 days',
    'multiple_hospitalizations': 'IP admits >= 2 in past 6 months',

    # Clinical complexity
    'multiple_chronic_conditions': 'Chronic conditions >= 3',
    'high_hcc_score': 'HCC RAF score > 2.0',
    'polypharmacy': 'Active medications >= 10',
    'behavioral_health': 'Depression, anxiety, or substance abuse',

    # Social determinants
    'social_isolation': 'Lives alone + age > 75',
    'transportation_barriers': 'Documented transportation issues',
    'food_insecurity': 'Positive screening',
    'housing_instability': 'Homeless or unstable housing',

    # Gaps in care
    'medication_nonadherence': 'PDC < 0.80',
    'missed_appointments': 'No-show rate > 20%',
    'no_pcp_visit': 'No PCP visit in past 12 months'
}
```

**Risk Stratification Model:**
```python
def stratify_patient_risk(patient_id):
    """Comprehensive risk stratification"""

    # Clinical risk (HCC/disease burden)
    clinical_risk = calculate_hcc_score(patient_id)

    # Utilization risk
    utilization_risk = calculate_utilization_risk(patient_id)

    # Psychosocial risk
    psychosocial_risk = calculate_psychosocial_risk(patient_id)

    # Cost risk
    predicted_cost = predict_next_year_cost(patient_id)
    current_cost = get_trailing_12mo_cost(patient_id)

    # Composite risk score
    composite_score = (
        0.35 * clinical_risk +
        0.30 * utilization_risk +
        0.20 * psychosocial_risk +
        0.15 * (predicted_cost / 50000)  # Normalize cost
    )

    # Assign risk tier
    if composite_score > 0.70:
        tier = 'High'
        intervention = 'Intensive care management'
    elif composite_score > 0.40:
        tier = 'Medium'
        intervention = 'Care coordination'
    else:
        tier = 'Low'
        intervention = 'Self-management support'

    return {
        'patient_id': patient_id,
        'risk_score': composite_score,
        'risk_tier': tier,
        'clinical_risk': clinical_risk,
        'utilization_risk': utilization_risk,
        'psychosocial_risk': psychosocial_risk,
        'predicted_annual_cost': predicted_cost,
        'recommended_intervention': intervention
    }
```

### Care Gap Closure Campaigns

**Workflow:**
```
1. Identify Care Gaps
   ↓
2. Prioritize by Impact (quality measure weight, patient risk)
   ↓
3. Generate Outreach Lists
   ↓
4. Multi-Channel Outreach (calls, texts, portal messages, mailings)
   ↓
5. Schedule Appointments
   ↓
6. Track Completion
   ↓
7. Measure Impact
```

**Prioritization Example:**
```sql
WITH care_gaps AS (
    SELECT
        patient_key,
        patient_name,
        patient_phone,
        COUNT(*) AS total_gaps,
        SUM(CASE WHEN gap_type = 'Mammogram' THEN 1 ELSE 0 END) AS mammogram_gap,
        SUM(CASE WHEN gap_type = 'Colonoscopy' THEN 1 ELSE 0 END) AS colonoscopy_gap,
        SUM(CASE WHEN gap_type = 'HbA1c' THEN 1 ELSE 0 END) AS hba1c_gap,
        SUM(CASE WHEN gap_type = 'Eye Exam' THEN 1 ELSE 0 END) AS eye_exam_gap,
        MAX(risk_score) AS patient_risk_score
    FROM patient_care_gaps
    WHERE gap_status = 'Open'
    GROUP BY patient_key, patient_name, patient_phone
)
SELECT
    patient_key,
    patient_name,
    patient_phone,
    total_gaps,
    patient_risk_score,
    -- Prioritize by: multiple gaps + high risk + high-value measures
    (total_gaps * 10) + (patient_risk_score * 100) + (mammogram_gap * 5) + (colonoscopy_gap * 5) AS priority_score
FROM care_gaps
WHERE total_gaps > 0
ORDER BY priority_score DESC
LIMIT 500;  -- Top 500 for this month's campaign
```

---

*Clinical Analytics Use Cases Reference - Real-world applications of healthcare analytics for improving quality, efficiency, and outcomes.*

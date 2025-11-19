# Remote Patient Monitoring (RPM) Implementation Guide

## Overview
Complete step-by-step guide to implementing a successful Remote Patient Monitoring program, from planning through ongoing optimization.

## Phase 1: Planning (Weeks 1-4)

### Define Target Population
- Heart failure patients (NYHA Class II-III)
- Hypertension (uncontrolled BP >140/90)
- Diabetes (A1c >8%)  
- COPD (Gold Stage 2-3)
- Post-hospital discharge (within 30 days)

### Set Clinical Goals
- Reduce 30-day readmissions by 25%
- Improve medication adherence to >80%
- Achieve target BP control in 70% of patients
- Reduce A1c by 1% on average
- Early intervention for exacerbations

### Financial Modeling
**Revenue (per patient/month)**:
- CPT 99453 (setup): $19
- CPT 99454 (device x2): $128
- CPT 99457 (20min): $51
- Total: ~$198/month

**Costs**:
- Devices: $200 (one-time)
- Platform: $30/month
- Staff time: 1 RN per 120 patients
- Total cost per patient: ~$80-100/month
- Net margin: $90-120/month

## Phase 2: Technology Selection (Weeks 3-6)

### Device Selection Criteria
**Clinical**:
- FDA-cleared medical devices
- Clinically validated accuracy
- Automatic data transmission
- Patient-appropriate (ease of use)

**Technical**:
- Connectivity (WiFi/Cellular/Bluetooth)
- Battery life (3+ months preferred)
- Integration via API/HL7/FHIR
- Real-time data transmission

**Recommended Devices**:
- Blood Pressure: Withings BPM Connect
- Weight Scale: BodyTrace (cellular) or Withings Body+
- Glucose: Dexcom G7 or OneTouch Verio Flex
- Pulse Ox: Nonin 3150 or Masimo MightySat

### Platform Selection
**Key Features Needed**:
- Multi-device support
- Real-time alerting
- Clinical dashboard
- EHR integration (FHIR)
- Reporting and analytics
- HIPAA compliance

**Vendors to Evaluate**:
- Vivify Health
- Health Recovery Solutions
- 100Plus
- Cadence
- Current Health

## Phase 3: Clinical Protocol Development (Weeks 5-8)

### Alert Thresholds

**Blood Pressure**:
- Critical High: SBP >180 or DBP >110 → Call within 1 hour
- Moderate High: SBP 160-179 → Review within 24 hours
- Low: SBP <90 → Call within 4 hours

**Weight (Heart Failure)**:
- Gain >2 lbs in 24 hours → Call same day
- Gain >5 lbs in 1 week → Call within 24 hours

**Glucose**:
- Critical Low: <70 mg/dL → Call immediately
- Critical High: >300 mg/dL → Call within 2 hours
- Pattern of highs/lows → Medication adjustment

**SpO2 (COPD)**:
- <88% → Call within 1 hour
- Declining trend → Review within 24 hours

### Intervention Protocols

**Blood Pressure Protocol**:
```
IF SBP >180 or DBP >110:
  1. Call patient immediately
  2. Assess symptoms (headache, chest pain, vision changes)
  3. If symptomatic: Advise 911/ED
  4. If asymptomatic: Notify MD, medication adjustment
  5. Repeat BP in 4 hours
  6. Document all actions

IF SBP 160-179 or DBP 100-109:
  1. Review within 24 hours
  2. Check medication adherence
  3. Review diet and lifestyle
  4. Notify MD if persistent >3 days
  5. Consider medication titration
```

**Heart Failure Weight Protocol**:
```
IF weight gain >2 lbs in 24 hours OR >5 lbs in 1 week:
  1. Call patient same day
  2. Assess symptoms (SOB, edema, orthopnea)
  3. Review diuretic adherence
  4. Implement standing order protocol:
     - Increase furosemide by 20-40mg daily x 3 days
     - Call back in 24 hours with weight
  5. If no improvement in 48 hours: MD evaluation
  6. Monitor daily weights closely
```

## Phase 4: Staffing and Training (Weeks 6-10)

### Staffing Model
**RN Care Coordinator** (1 FTE per 120 patients):
- Daily data review (1-2 hours)
- Patient outreach (3-4 hours)  
- Documentation (1-2 hours)
- Provider communication (30 min)

**Support Roles**:
- Medical Assistant (device setup, troubleshooting)
- Pharmacist (medication management)
- Physician oversight (protocol approval, escalation)

### Training Curriculum
**Week 1: Platform Training**
- Login and navigation
- Dashboard overview
- Alert management
- Documentation

**Week 2: Clinical Protocols**
- Disease-specific guidelines
- Alert response procedures
- Escalation pathways
- Medication titration protocols

**Week 3: Patient Communication**
- Motivational interviewing
- Health coaching techniques
- Cultural competency
- Difficult conversations

**Week 4: Billing and Documentation**
- CPT code requirements
- Time tracking
- Interactive communication rules
- Audit preparation

## Phase 5: Pilot Launch (Weeks 11-16)

### Pilot Cohort
- 20-30 patients (manageable size)
- Mix of conditions (HF, HTN, DM, COPD)
- Tech-savvy and non-tech mix
- Willing to provide feedback

### Patient Enrollment Process

**Step 1: Eligibility Screening**
```sql
SELECT patient_id, diagnosis, last_a1c, last_bp, last_admission_date
FROM patients
WHERE (diagnosis LIKE '%heart failure%' AND last_admission_date > NOW() - INTERVAL '90 days')
   OR (diagnosis LIKE '%hypertension%' AND last_bp_systolic > 140)
   OR (diagnosis LIKE '%diabetes%' AND last_a1c > 8.0)
   OR (diagnosis LIKE '%COPD%' AND fev1_percent < 60)
LIMIT 30;
```

**Step 2: Provider Referral**
- Provider reviews eligible patients
- Orders RPM monitoring
- Documents medical necessity
- Signs enrollment form

**Step 3: Patient Consent**
- Explain RPM program goals
- Discuss device use and expectations
- Review billing and insurance coverage
- Sign consent form
- Provide educational materials

**Step 4: Device Distribution**
- Ship devices to patient home OR
- In-person handoff with training
- Verify device setup and connectivity
- Test first data transmission
- Provide support contact info

### Pilot Metrics to Track
- Enrollment rate (% of eligible patients who enroll)
- Device adherence (% of days with data)
- Alert volume and response time
- Patient satisfaction
- Staff time per patient
- Technical issues encountered

## Phase 6: Optimization (Weeks 17-20)

### Data Review and Analysis
**Weekly Metrics**:
- Patients enrolled
- Average device adherence rate
- Alerts generated (by type)
- Average response time to alerts
- Interventions performed
- Staff time spent

**Monthly Metrics**:
- Clinical outcomes (BP control, weight stability, glucose control)
- Healthcare utilization (ED visits, hospitalizations)
- Patient satisfaction scores
- Cost per patient
- Revenue per patient

### Workflow Refinement
**Common Issues and Solutions**:

| Issue | Solution |
|-------|----------|
| Too many alerts | Refine thresholds, implement alert fatigue mitigation |
| Low device adherence | Increase patient education, phone reminders |
| Technical connectivity issues | Switch to cellular devices, IT support process |
| Staff overwhelmed | Hire additional staff, improve workflow efficiency |
| Provider resistance | Share outcome data, reduce provider burden |

## Phase 7: Full Deployment (Months 6+)

### Scaling Strategy
**Gradual Expansion**:
- Month 6: 50 patients
- Month 9: 100 patients
- Month 12: 150 patients
- Month 18: 200+ patients

**Phased Disease Rollout**:
1. Heart failure (highest ROI, clear protocols)
2. Hypertension (large population)
3. Diabetes (CGM integration)
4. COPD (pulmonary-specific)

### Marketing and Patient Recruitment
**Provider Engagement**:
- Lunch-and-learn presentations
- Share outcome data and case studies
- Simplify referral process
- Provider champions program

**Patient Outreach**:
- Direct mail to eligible patients
- Patient portal messaging
- Waiting room posters/brochures
- Patient testimonials

**Insurance Coordination**:
- Verify coverage for all major payers
- Obtain prior authorizations if needed
- Educate billing staff on CPT codes
- Track denial rates and appeal

## Billing and Revenue Cycle Management

### Documentation Requirements

**Monthly Checklist per Patient**:
- [ ] Device setup documented (CPT 99453, once per episode)
- [ ] 16+ days of data transmitted (CPT 99454)
- [ ] 20+ minutes interactive communication (CPT 99457)
- [ ] Time log with start/stop times
- [ ] Clinical note documenting data review, patient interaction, interventions

**Time Log Template**:
```
Date: 01/15/2025
Patient: John Doe (MRN: 123456)

Activity Log:
10:00 AM - 10:15 AM (15 min): Reviewed BP and weight data for past 30 days. Noted elevated BP readings on 1/10-1/14 (avg 155/92).

10:15 AM - 10:35 AM (20 min): Phone call with patient. Discussed elevated BP, reviewed medications (confirmed adherence), discussed diet (high sodium intake identified), provided education on DASH diet. Patient agrees to reduce sodium and recheck BP daily. Will follow up in 1 week.

10:35 AM - 10:40 AM (5 min): Documented encounter in EHR. Sent educational materials via patient portal.

Total Interactive Time: 20 minutes (qualifies for CPT 99457)
```

### Claim Submission
**Billing Codes**:
- 99453 (setup): Bill once at enrollment
- 99454 (device): Bill monthly if 16+ days of data
- 99457 (first 20 min): Bill monthly
- 99458 (additional 20 min): Bill if >40 min total time

**Modifiers**: None typically required (check payer)
**Place of Service**: 99 (other - RPM services)
**Diagnosis Codes**: Primary diagnosis (I50.9 heart failure, I10 hypertension, E11.9 diabetes)

## Quality Improvement

### Quarterly Review
- Clinical outcomes vs goals
- Patient satisfaction survey results
- Staff feedback and workflow issues
- Financial performance
- Technology performance
- Compliance audit results

### Continuous Improvement
- Test new devices or platform features
- Refine clinical protocols based on evidence
- A/B test different communication strategies
- Benchmark against industry standards
- Publish outcomes internally and externally

## Success Metrics (12-Month Goals)

**Clinical**:
- 30-day readmission reduction: 25%
- BP control (<140/90): 70% of HTN patients
- A1c reduction: 1% average decrease
- COPD exacerbation reduction: 30%

**Operational**:
- Device adherence: >75% (avg days with data)
- Alert response time: <4 hours for high priority
- Patient satisfaction: >4.5/5.0
- Provider satisfaction: >4.0/5.0

**Financial**:
- Cost per patient per month: <$100
- Revenue per patient per month: >$180
- Net margin: >$80 per patient per month
- Program profitability: Achieved by Month 12

---

*Last Updated: 2025*
*Version: 1.0*

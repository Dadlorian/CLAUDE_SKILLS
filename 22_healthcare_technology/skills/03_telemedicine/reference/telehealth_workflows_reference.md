# Telehealth Workflows Reference

## Overview
Comprehensive reference for designing, implementing, and optimizing telehealth clinical workflows across various care settings and specialties.

---

## Standard Telehealth Visit Workflow

### Phase 1: Pre-Visit (24-48 hours before visit)

**Patient Activities**:
1. Receive appointment confirmation (email/SMS)
2. Complete pre-visit questionnaire/intake forms
3. Update insurance information
4. Review and sign telehealth consent
5. Test technology (system check link)
6. Receive visit instructions and platform access link

**Staff Activities**:
1. Verify insurance eligibility and benefits
2. Review pre-visit questionnaire responses
3. Prepare patient chart and relevant records
4. Send reminders (24-hour and 1-hour before)
5. Ensure provider has necessary information
6. Stage medications for e-prescribing if needed

**Technology Checks**:
- Platform availability testing
- Provider credentials verification
- Integration status (EHR, pharmacy, etc.)
- Backup communication methods prepared

---

### Phase 2: Visit Preparation (15-30 minutes before)

**Patient Activities**:
1. Click visit link from email/SMS
2. Complete virtual check-in
3. Enter virtual waiting room
4. Test audio/video (automatic checks)
5. Review visit reason and symptoms

**Staff Activities**:
1. Monitor virtual waiting room
2. Verify patient identity (photo ID if first visit)
3. Collect co-pay (if applicable)
4. Take initial history via chat or brief call
5. Document vital signs if patient has devices
6. Alert provider that patient is ready

**Provider Activities**:
1. Review patient chart
2. Review pre-visit questionnaire
3. Review relevant test results or imaging
4. Prepare visit note template
5. Join video platform

---

### Phase 3: Clinical Visit (15-30 minutes)

**Visit Initiation** (2-3 minutes):
1. Provider admits patient from waiting room
2. Verbal patient identification confirmation
3. Verify patient location (city, state)
4. Re-confirm telehealth consent
5. Explain visit format and any limitations
6. Establish rapport

**History Taking** (5-10 minutes):
1. Chief complaint
2. History of present illness
3. Review of systems (focused)
4. Past medical history (if new patient)
5. Current medications reconciliation
6. Allergies review
7. Social history (as relevant)
8. Family history (as relevant)

**Virtual Physical Examination** (3-5 minutes):
- General appearance and mental status
- Specific to chief complaint:
  - Dermatology: Visual inspection, patient-assisted
  - Respiratory: Observation of breathing, patient palpation
  - Musculoskeletal: Range of motion demonstration
  - Neurologic: Gait, coordination, strength testing
- Vital signs if patient has devices (review RPM data)
- Limitations acknowledged and documented

**Clinical Decision Making** (5-10 minutes):
1. Formulate differential diagnosis
2. Discuss assessment with patient
3. Order tests or imaging if needed
4. Prescribe medications (e-prescribe)
5. Provide patient education
6. Discuss treatment plan and follow-up
7. Determine if in-person visit needed
8. Answer patient questions

**Visit Closure** (2-3 minutes):
1. Summarize visit and plan
2. Verify patient understanding
3. Schedule follow-up if needed
4. Provide after-visit resources
5. Explain how to access visit summary
6. End video session

---

### Phase 4: Post-Visit (Immediately after)

**Provider Activities**:
1. Complete clinical documentation (15-30 minutes)
2. Review and sign visit note
3. Order any additional tests or referrals
4. Send prescriptions to pharmacy
5. Document billing codes
6. Flag for follow-up if needed

**Staff Activities**:
1. Send after-visit summary to patient
2. Schedule follow-up appointments
3. Process billing and claims
4. Send patient satisfaction survey
5. Upload documentation to EHR
6. Handle any patient follow-up questions

**Patient Activities**:
1. Receive visit summary and instructions
2. Review prescriptions and pick up at pharmacy
3. Schedule follow-up tests or appointments
4. Complete satisfaction survey
5. Follow treatment plan

---

## Specialty-Specific Workflows

### Mental Health / Therapy Workflow

**Pre-Session**:
- Thorough intake questionnaire (PHQ-9, GAD-7)
- Insurance verification (mental health benefits)
- Consent for teletherapy
- Privacy and confidentiality review
- Safety planning (emergency contacts, crisis resources)

**Session** (45-60 minutes):
- Private, quiet environment verification
- Safety assessment (especially initial visits)
- Therapeutic interventions (CBT, DBT, etc.)
- Homework assignment if applicable
- Scheduling next session

**Post-Session**:
- Brief session note (SOAP format)
- Update treatment plan
- Billing (90834, 90837 codes)
- Crisis follow-up if needed

**Unique Considerations**:
- Higher privacy requirements
- Crisis protocols and emergency contacts
- Longer session times
- Ongoing relationship (weekly sessions)
- Audio-only acceptable for some payers

---

### Urgent Care Workflow

**Triage** (5 minutes):
- Symptom checker or nurse triage
- Acuity assessment
- Appropriate service level determination (telehealth vs ED)
- Queue prioritization by acuity

**Rapid Assessment** (10-15 minutes):
- Focused history on chief complaint
- Virtual exam (limited)
- Quick decision making
- Prescriptions or referrals
- Safety netting advice

**Disposition**:
- Home care with medication
- Refer to in-person urgent care
- Refer to ED if emergent
- Follow-up in 24-48 hours if needed

**Unique Considerations**:
- Rapid throughput needed
- Clear escalation pathways
- Comprehensive safety netting
- After-hours coverage

---

### Chronic Disease Management Workflow

**Initial Visit** (30-45 minutes):
- Comprehensive chronic disease assessment
- Goal setting with patient
- Care plan development
- Device distribution (RPM devices)
- Education on self-management

**Follow-up Visits** (15-20 minutes):
- Review RPM data and trends
- Symptom assessment
- Medication adjustments
- Progress toward goals
- Reinforcement of education
- Identify barriers

**Between-Visit Monitoring**:
- Daily RPM data review by clinical staff
- Alert-based outreach
- Proactive interventions
- Monthly CCM or RPM time
- Care coordination

**Unique Considerations**:
- Longer initial visits
- Frequent follow-ups
- Integration of RPM data
- Care team approach
- Billing for CCM, RPM, TCM

---

### Post-Hospital Discharge Workflow

**Discharge Day**:
- Discharge planning team schedules telehealth follow-up (within 7 days)
- Provide patient with telehealth instructions
- Distribute RPM devices if applicable
- Ensure medication reconciliation
- Schedule PCP follow-up

**Telehealth Follow-up** (within 2-7 days, 30 minutes):
- Medication reconciliation
- Review hospital course and discharge instructions
- Symptom assessment (red flags for readmission)
- Wound check if applicable (visual inspection)
- Social needs assessment
- Coordinate additional services (home health, PT, etc.)
- Schedule additional follow-ups

**Ongoing Monitoring** (30 days post-discharge):
- RPM if indicated (heart failure, COPD)
- Proactive outreach if concerning trends
- Ensure follow-up appointments kept
- Care coordination

**Unique Considerations**:
- Transitional Care Management (TCM) billing
- Within 7-14 day timeframe critical
- High readmission risk period
- Care coordination intensive

---

## Virtual Waiting Room Management

### Queue Design

**Status Categories**:
1. **Scheduled and Waiting**: Patients in waiting room
2. **In Session**: Patients currently with provider
3. **Completed**: Finished visits
4. **No-Show**: Patients who didn't show up

**Priority Queue**:
- VIP patients or urgent needs
- On-time vs late arrivals
- Provider's scheduled order
- Manual re-prioritization option

**Visual Interface**:
- Patient names and appointment times
- Wait time displayed
- Provider availability status
- Technical issue flags

---

### Patient Experience

**Waiting Room Features**:
- Estimated wait time
- Provider name and photo
- Educational content or videos
- Ability to send messages to staff
- Audio/video test tools
- Countdown to visit

**Communication**:
- Notify if provider is running late
- Updates on wait time
- Technical support access
- Option to reschedule if wait is too long

---

### Staff Management

**Monitoring**:
- Real-time queue view
- Patient check-in alerts
- Technical issue notifications
- Provider status updates

**Actions**:
- Admit patient to visit
- Send messages to patients
- Adjust queue order
- Flag issues for follow-up
- Technical troubleshooting

---

## Scheduling Strategies

### Appointment Types

**New Patient Video Visit** (30-45 minutes):
- Comprehensive history and exam
- Additional time for rapport building
- Technology troubleshooting buffer

**Established Patient Video Visit** (15-20 minutes):
- Focused visit
- Assumes technical familiarity

**Phone/Audio-Only Visit** (10-15 minutes):
- Brief follow-up
- Medication refills
- Simple questions

**Chronic Disease Management** (20-30 minutes):
- Review of monitoring data
- Care plan adjustment
- Education and counseling

**Mental Health Session** (45-60 minutes):
- Therapy sessions
- Psychiatric medication management

---

### Scheduling Best Practices

**Buffer Time**:
- Add 5-10 minute buffer between visits
- Account for documentation time
- Allow for technical issues

**Template Design**:
- Block schedule by visit type
- Telehealth blocks separate from in-person
- Mix of new/established patients
- Leave some open slots for same-day

**Overbooking Strategy**:
- 10-15% overbooking to account for no-shows
- Higher overbooking early in program (learning curve)
- Monitor and adjust based on actual no-show rates

**Same-Day Scheduling**:
- Reserve slots for urgent needs
- Release unreserved slots mid-morning
- Use for patient convenience and access

---

## Documentation Workflows

### Real-Time Documentation

**Advantages**:
- Note completed during visit
- More accurate recall
- Immediate chart closure
- Billing captured promptly

**Techniques**:
- Template-based documentation
- Voice recognition (Dragon, ambient AI)
- Structured data entry
- Multi-monitor setup (one for video, one for note)

**Challenges**:
- Eye contact with patient reduced
- Typing noise distracting
- Slower visit pace

---

### Post-Visit Documentation

**Advantages**:
- Full attention to patient during visit
- Natural conversation flow
- Better patient satisfaction

**Techniques**:
- Detailed note-taking during visit (bullet points)
- Dictation immediately after visit
- Structured templates for efficiency
- Scheduled documentation time

**Challenges**:
- Memory fade
- Time between visits needed
- Potential for documentation backlog

---

### Hybrid Approach (Recommended)

**During Visit**:
- Enter structured data (vitals, medications, orders)
- Check appropriate boxes (ROS, exam findings)
- Start problem list and plan

**Immediately After**:
- Dictate or type narrative portions (HPI, MDM)
- Finalize assessment and plan
- Add any additional orders
- Complete billing codes
- Sign note

**Time Allocation**: 15-minute visit + 10 minutes documentation = 25 minutes total

---

## Quality Assurance Workflows

### Metrics Monitoring

**Access Metrics**:
- Time to third next available appointment
- Same-day appointment availability
- No-show rates
- Visit cancellation rates

**Clinical Metrics**:
- Appropriate use of telehealth vs in-person
- Adherence to clinical protocols
- Diagnostic accuracy
- Adverse outcomes

**Operational Metrics**:
- Provider productivity (visits per hour)
- Wait times in virtual waiting room
- Technical issue frequency
- Documentation completion time

**Patient Experience Metrics**:
- Patient satisfaction scores
- Net Promoter Score (NPS)
- Complaints and compliments
- Platform usability ratings

---

### Continuous Improvement

**Monthly Review**:
- Review metrics dashboard
- Identify trends and outliers
- Discuss barriers and challenges
- Share best practices

**Provider Feedback**:
- Survey providers on workflow efficiency
- Identify pain points
- Collect improvement suggestions
- Test workflow modifications

**Patient Feedback**:
- Satisfaction surveys after each visit
- Focus groups or interviews
- Usability testing
- Complaint analysis

**A/B Testing**:
- Test workflow variations
- Measure impact on metrics
- Implement successful changes
- Iterate continuously

---

## Emergency Protocols

### During-Visit Emergencies

**Chest Pain, Stroke Symptoms, etc.**:
1. Remain calm and assess severity
2. Confirm patient's exact location (address)
3. Instruct patient or family member to call 911
4. Stay on video call until EMS arrives (if possible)
5. Provide EMS with clinical information
6. Document entire interaction thoroughly
7. Follow up with patient/family after transport

**Mental Health Crisis (Suicidality, Homicidality)**:
1. Conduct safety assessment
2. Determine immediate danger
3. If high risk: Initiate emergency services
4. Confirm patient location
5. Stay on call until help arrives
6. Contact emergency contacts if applicable
7. Document and follow up

---

### Technical Emergencies

**Complete Platform Failure**:
1. Have backup communication plan (phone numbers)
2. Call patient to complete visit by phone
3. Document as telephone visit
4. Report technical issue to IT/vendor
5. Follow up via patient portal or email

**Partial Connectivity Issues**:
1. Switch to audio-only if video fails
2. Reschedule if visit requires visual component
3. Offer in-person visit as alternative
4. No-charge if technical issue prevents completion

---

## Workflow Optimization Tools

### Process Mapping

**Swimlane Diagrams**:
- Lanes for: Patient, Provider, Staff, Technology
- Map current state workflow
- Identify inefficiencies and delays
- Design future state workflow
- Implement and measure

**Value Stream Mapping**:
- Identify value-adding vs non-value-adding steps
- Measure time for each step
- Eliminate waste
- Optimize flow

---

### Automation Opportunities

**Appointment Reminders**: Automated SMS/email
**Pre-visit Questionnaires**: Automated distribution
**Insurance Verification**: Real-time eligibility checks
**Visit Summaries**: Auto-generated from note
**Prescription Transmission**: E-prescribe integration
**Follow-up Scheduling**: Automated booking based on visit type
**Satisfaction Surveys**: Auto-send post-visit
**Billing**: Auto-populate from documentation

---

## Resources

### Workflow Templates
- Standard visit flowcharts
- Emergency protocol checklists
- Documentation templates
- Staff training materials

### Tools
- Process mapping software (Lucidchart, Visio)
- Workflow automation (Zapier, IFTTT, custom integrations)
- Project management (for workflow improvement projects)

---

*Last Updated: 2025*
*Version: 1.0*

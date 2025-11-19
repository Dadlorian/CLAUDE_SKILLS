# Virtual Consultation Workflow Guide

## Comprehensive guide for designing and optimizing virtual consultation workflows from pre-visit through post-visit, including provider and patient experiences.

## Table of Contents
1. [Pre-Visit Workflow](#pre-visit-workflow)
2. [Virtual Waiting Room](#virtual-waiting-room)
3. [Visit Conduct](#visit-conduct)
4. [Clinical Documentation](#clinical-documentation)
5. [Post-Visit Procedures](#post-visit-procedures)
6. [Emergency Protocols](#emergency-protocols)
7. [Quality Metrics](#quality-metrics)

## Pre-Visit Workflow

### Appointment Scheduling
```javascript
// Telehealth appointment scheduler with insurance verification
class TelehealthScheduler {
  async scheduleAppointment(appointmentData) {
    const {patientId, providerId, appointmentType, preferredTime} = appointmentData;

    // Verify insurance coverage for telehealth
    const coverage = await this.verifyTelehealthCoverage(patientId, appointmentType);
    if (!coverage.isEligible) {
      throw new Error(`Telehealth not covered: ${coverage.reason}`);
    }

    // Check provider availability
    const slot = await this.findAvailableSlot(providerId, preferredTime);

    // Create appointment
    const appointment = await db.appointments.create({
      patient_id: patientId,
      provider_id: providerId,
      appointment_type: 'TELEHEALTH',
      scheduled_time: slot.startTime,
      duration_minutes: slot.duration,
      visit_type: appointmentType,
      status: 'SCHEDULED',
      video_link: await this.generateSecureVideoLink(),
      created_at: new Date()
    });

    // Send confirmation and pre-visit instructions
    await this.sendPreVisitInstructions(appointment);

    return appointment;
  }

  async sendPreVisitInstructions(appointment) {
    const instructions = {
      technicalRequirements: {
        browser: 'Chrome, Firefox, Safari, or Edge (latest version)',
        bandwidth: 'Minimum 3 Mbps upload/download',
        camera: 'Required for video consultation',
        microphone: 'Required for audio communication'
      },
      preparation: [
        'Test your camera and microphone 15 minutes before appointment',
        'Find a quiet, well-lit private space',
        'Have your medication list and insurance card ready',
        'Prepare questions for your provider',
        'Have a pen and paper for notes'
      ],
      joinLink: appointment.video_link,
      joinTime: 'Available 10 minutes before scheduled time',
      supportContact: 'telehealth-support@hospital.org'
    };

    await emailService.send({
      to: appointment.patient_email,
      subject: 'Your Upcoming Telehealth Appointment',
      template: 'pre_visit_instructions',
      data: instructions
    });
  }
}
```

### Technical Readiness Check
```python
# Pre-visit technical validation service
class TechnicalReadinessChecker:
    def __init__(self):
        self.minimum_bandwidth_mbps = 3
        self.required_browser_versions = {
            'chrome': 90,
            'firefox': 88,
            'safari': 14,
            'edge': 90
        }

    async def run_readiness_check(self, patient_id):
        """Comprehensive technical readiness assessment"""
        results = {
            'browser': await self.check_browser(),
            'bandwidth': await self.check_bandwidth(),
            'devices': await self.check_devices(),
            'firewall': await self.check_firewall_settings(),
            'timestamp': datetime.now()
        }

        results['overall_ready'] = all([
            results['browser']['compatible'],
            results['bandwidth']['sufficient'],
            results['devices']['camera_detected'],
            results['devices']['microphone_detected'],
            results['firewall']['ports_open']
        ])

        # Store results for troubleshooting
        await self.store_readiness_results(patient_id, results)

        return results

    async def check_bandwidth(self):
        """Test network bandwidth"""
        # Perform speed test using small file transfers
        upload_speed = await self.measure_upload_speed()
        download_speed = await self.measure_download_speed()
        latency = await self.measure_latency()

        return {
            'upload_mbps': upload_speed,
            'download_mbps': download_speed,
            'latency_ms': latency,
            'sufficient': upload_speed >= self.minimum_bandwidth_mbps and
                         download_speed >= self.minimum_bandwidth_mbps,
            'quality_estimate': self.estimate_quality(upload_speed, download_speed, latency)
        }

    def estimate_quality(self, upload, download, latency):
        """Estimate video call quality based on network metrics"""
        if upload >= 5 and download >= 5 and latency < 50:
            return 'HD'
        elif upload >= 3 and download >= 3 and latency < 100:
            return 'SD'
        elif upload >= 1.5 and download >= 1.5 and latency < 200:
            return 'BASIC'
        else:
            return 'POOR'
```

## Virtual Waiting Room

### Implementation
```javascript
// Virtual waiting room with queue management
class VirtualWaitingRoom {
  constructor() {
    this.queue = new PriorityQueue();
    this.activeRooms = new Map();
  }

  async enterWaitingRoom(appointmentId, patientId) {
    const appointment = await db.appointments.findById(appointmentId);

    // Verify appointment time
    const scheduledTime = new Date(appointment.scheduled_time);
    const currentTime = new Date();
    const minutesEarly = (scheduledTime - currentTime) / (1000 * 60);

    if (minutesEarly > 15) {
      throw new Error('Cannot join more than 15 minutes before scheduled time');
    }

    // Add to queue
    const queueEntry = {
      appointmentId,
      patientId,
      providerId: appointment.provider_id,
      scheduledTime: scheduledTime,
      checkInTime: currentTime,
      priority: this.calculatePriority(appointment),
      status: 'WAITING'
    };

    await this.queue.enqueue(queueEntry);

    // Notify patient
    await this.sendQueueUpdate(patientId, {
      position: await this.queue.getPosition(appointmentId),
      estimatedWaitTime: await this.estimateWaitTime(appointment.provider_id)
    });

    return queueEntry;
  }

  calculatePriority(appointment) {
    // Priority based on appointment type and scheduled time
    let priority = 0;

    // Urgent appointments get higher priority
    if (appointment.appointment_type === 'URGENT') priority += 100;

    // Add points for being on time or late
    const minutesLate = (new Date() - new Date(appointment.scheduled_time)) / (1000 * 60);
    if (minutesLate > 0) priority += minutesLate;

    return priority;
  }

  async providerReady(providerId) {
    // Get next patient in queue for this provider
    const nextPatient = await this.queue.dequeueForProvider(providerId);

    if (!nextPatient) {
      return null;
    }

    // Create video room
    const room = await this.createVideoRoom(nextPatient);
    this.activeRooms.set(nextPatient.appointmentId, room);

    // Notify both parties
    await this.notifyParticipants(nextPatient, room);

    return room;
  }

  async createVideoRoom(appointment) {
    // Initialize secure video room
    const room = {
      id: generateSecureId(),
      appointmentId: appointment.appointmentId,
      providerLink: await this.generateProviderLink(),
      patientLink: await this.generatePatientLink(),
      recording: false,
      recordingConsent: appointment.recording_consent,
      startTime: new Date(),
      encryption: 'AES-256',
      participantCount: 0
    };

    return room;
  }
}
```

## Visit Conduct

### Best Practices for Providers
```markdown
## Provider Virtual Visit Checklist

### Environment Setup
- [ ] Quiet, private location
- [ ] Professional background (or virtual background)
- [ ] Good lighting (face clearly visible)
- [ ] Camera at eye level
- [ ] Notifications silenced on all devices

### Technical Setup
- [ ] Headset or earbuds for better audio
- [ ] Close unnecessary applications
- [ ] Have backup phone number for patient
- [ ] Test screen sharing capability
- [ ] Have EHR open and ready

### Clinical Conduct
- [ ] Verify patient identity with photo ID
- [ ] Confirm patient location (for emergencies)
- [ ] Obtain verbal consent for telehealth visit
- [ ] Document consent in EHR
- [ ] Explain limitations of virtual examination
- [ ] Use appropriate eye contact (look at camera)
- [ ] Speak clearly and check audio quality
- [ ] Use screen sharing for education
- [ ] Provide clear follow-up instructions
```

### Clinical Assessment Tools
```python
# Virtual physical examination guidance system
class VirtualExamGuide:
    def __init__(self):
        self.exam_protocols = self.load_protocols()

    def get_exam_protocol(self, chief_complaint, symptoms):
        """Get virtual examination protocol based on complaint"""
        protocol = {
            'visual_inspection': [],
            'patient_assisted_tests': [],
            'equipment_needed': [],
            'limitations': [],
            'red_flags': []
        }

        if 'respiratory' in chief_complaint.lower():
            protocol['visual_inspection'] = [
                'Observe respiratory rate (count for 30 seconds)',
                'Note use of accessory muscles',
                'Check for cyanosis (lips, nail beds)',
                'Assess work of breathing'
            ]
            protocol['patient_assisted_tests'] = [
                'Pulse oximetry reading (if available)',
                'Peak flow measurement (if patient has device)',
                'Breath holding test (count seconds)'
            ]
            protocol['equipment_needed'] = ['Pulse oximeter (if available)']
            protocol['red_flags'] = [
                'Respiratory rate > 30',
                'Difficulty speaking full sentences',
                'O2 saturation < 92%',
                'Confusion or altered mental status'
            ]

        elif 'dermatology' in chief_complaint.lower():
            protocol['visual_inspection'] = [
                'Have patient position lesion in good lighting',
                'Assess size (use coin or ruler for reference)',
                'Note color, borders, symmetry',
                'Check for bleeding, oozing, crusting',
                'Examine surrounding skin'
            ]
            protocol['patient_assisted_tests'] = [
                'Gently stretch skin to assess elevation',
                'Blanching test with gentle pressure',
                'Temperature comparison (affected vs unaffected area)'
            ]
            protocol['limitations'] = [
                'Cannot palpate texture',
                'Cannot assess depth',
                'Color accuracy depends on lighting/camera'
            ]

        return protocol

    def assess_telehealth_appropriateness(self, visit_reason):
        """Determine if complaint is appropriate for telehealth"""
        appropriate_conditions = [
            'medication_refill', 'follow_up', 'mental_health',
            'minor_illness', 'chronic_disease_management',
            'dermatology', 'nutritional_counseling'
        ]

        requires_in_person = [
            'severe_pain', 'acute_abdomen', 'chest_pain',
            'stroke_symptoms', 'severe_injury', 'suicidal_ideation'
        ]

        assessment = {
            'appropriate': visit_reason in appropriate_conditions,
            'requires_in_person': visit_reason in requires_in_person,
            'recommendation': ''
        }

        if assessment['requires_in_person']:
            assessment['recommendation'] = 'IMMEDIATE_IN_PERSON_OR_EMERGENCY'
        elif assessment['appropriate']:
            assessment['recommendation'] = 'PROCEED_WITH_TELEHEALTH'
        else:
            assessment['recommendation'] = 'CLINICAL_JUDGMENT_REQUIRED'

        return assessment
```

## Clinical Documentation

### Real-time Documentation Template
```javascript
// Telehealth-specific documentation system
class TelehealthDocumentation {
  generateVisitNote(visitData) {
    return {
      header: {
        visitType: 'TELEHEALTH',
        date: new Date(),
        duration: visitData.duration,
        location: {
          provider: visitData.providerLocation,
          patient: visitData.patientLocation
        },
        technology: {
          platform: 'SecureVideo',
          audioQuality: visitData.audioQuality,
          videoQuality: visitData.videoQuality,
          technicalIssues: visitData.technicalIssues
        }
      },

      consent: {
        telehealthConsent: true,
        recordingConsent: visitData.recordingConsent,
        consentMethod: 'VERBAL',
        witnessedBy: visitData.providerId
      },

      identityVerification: {
        method: 'PHOTO_ID',
        documentType: visitData.idType,
        verified: true
      },

      chiefComplaint: visitData.chiefComplaint,

      historyOfPresentIllness: visitData.hpi,

      virtualExamination: {
        general: visitData.generalAppearance,
        vitalSigns: visitData.vitals,
        visualAssessment: visitData.visualFindings,
        limitations: [
          'Physical palpation not performed',
          'Auscultation not performed',
          visitData.additionalLimitations
        ].filter(Boolean)
      },

      assessment: visitData.assessment,

      plan: visitData.plan,

      followUp: {
        method: visitData.followUpMethod,
        timeframe: visitData.followUpTimeframe,
        instructions: visitData.followUpInstructions
      },

      patientEducation: {
        topicsDiscussed: visitData.educationTopics,
        materialsSent: visitData.educationMaterials,
        comprehensionAssessed: true
      }
    };
  }
}
```

## Post-Visit Procedures

### Automated Follow-up System
```python
# Post-visit care coordination
class PostVisitCoordinator:
    async def complete_visit(self, visit_id):
        """Execute all post-visit procedures"""
        visit = await self.get_visit_data(visit_id)

        # 1. Send visit summary to patient
        await self.send_visit_summary(visit)

        # 2. Process prescriptions
        if visit.prescriptions:
            await self.send_prescriptions(visit.prescriptions)

        # 3. Schedule follow-up appointments
        if visit.follow_up_needed:
            await self.schedule_follow_up(visit)

        # 4. Send referrals
        if visit.referrals:
            await self.process_referrals(visit.referrals)

        # 5. Order tests/imaging
        if visit.orders:
            await self.submit_orders(visit.orders)

        # 6. Send patient education materials
        if visit.education_materials:
            await self.send_education_materials(visit)

        # 7. Schedule check-in call
        if visit.requires_follow_up_call:
            await self.schedule_follow_up_call(visit)

        # 8. Update care team
        await self.notify_care_team(visit)

        return {'status': 'COMPLETED', 'actions_taken': self.actions}

    async def send_visit_summary(self, visit):
        """Send after-visit summary to patient portal"""
        summary = {
            'visit_date': visit.date,
            'provider': visit.provider_name,
            'diagnosis': visit.diagnoses,
            'medications': visit.medications,
            'instructions': visit.instructions,
            'follow_up': visit.follow_up_plan,
            'warning_signs': visit.warning_signs,
            'emergency_instructions': 'Call 911 if you experience: ' +
                                     ', '.join(visit.red_flags)
        }

        await patient_portal.post_document(
            patient_id=visit.patient_id,
            document_type='VISIT_SUMMARY',
            content=summary
        )
```

## Emergency Protocols

### Emergency Detection and Response
```javascript
// Emergency detection during telehealth visits
class EmergencyResponseSystem {
  async monitorForEmergencies(visitId) {
    this.emergencyKeywords = [
      'chest pain', 'can\'t breathe', 'stroke', 'suicide',
      'overdose', 'severe bleeding', 'unconscious'
    ];

    this.vitalSignThresholds = {
      heartRate: {min: 40, max: 150},
      bloodPressureSystolic: {min: 80, max: 200},
      respiratoryRate: {min: 10, max: 30},
      oxygenSaturation: {min: 92, max: 100}
    };
  }

  async handleEmergency(visitId, emergencyType) {
    const visit = await db.visits.findById(visitId);
    const patient = await db.patients.findById(visit.patient_id);

    // Get patient's current location
    const location = await this.confirmPatientLocation(visitId);

    // Alert provider with emergency protocol
    await this.alertProvider(visit.provider_id, {
      type: 'TELEHEALTH_EMERGENCY',
      severity: 'CRITICAL',
      visitId: visitId,
      emergencyType: emergencyType,
      patientLocation: location,
      patientPhone: patient.phone
    });

    // Provider can initiate 911 if needed
    if (emergencyType === 'LIFE_THREATENING') {
      return {
        actions: [
          'STAY_ON_VIDEO_CALL',
          'CALL_911',
          'NOTIFY_EMERGENCY_CONTACT',
          'DOCUMENT_IN_EHR'
        ],
        script: this.getEmergencyScript(emergencyType),
        ems_contact_info: location.emergency_services
      };
    }
  }

  getEmergencyScript(emergencyType) {
    return {
      patient_instructions: [
        `I'm going to help you get emergency assistance.`,
        `Stay on this video call with me.`,
        `I'm calling 911 for you right now.`,
        `Can you confirm your address is: [ADDRESS]?`,
        `Is anyone else there with you?`
      ],
      ems_handoff: [
        `This is Dr. [NAME] conducting a telehealth visit.`,
        `Patient is experiencing [EMERGENCY].`,
        `Patient location confirmed: [ADDRESS].`,
        `I will remain on video until EMS arrives.`
      ]
    };
  }
}
```

## Quality Metrics

### Telehealth Performance Monitoring
```python
# Quality metrics tracking for telehealth program
class TelehealthQualityMetrics:
    def calculate_program_metrics(self, time_period):
        """Calculate comprehensive quality metrics"""
        metrics = {
            'utilization': self.calculate_utilization_metrics(time_period),
            'quality': self.calculate_quality_metrics(time_period),
            'technical': self.calculate_technical_metrics(time_period),
            'patient_experience': self.calculate_patient_experience(time_period),
            'clinical_outcomes': self.calculate_clinical_outcomes(time_period)
        }

        return metrics

    def calculate_utilization_metrics(self, period):
        return {
            'total_visits': self.count_visits(period),
            'unique_patients': self.count_unique_patients(period),
            'no_show_rate': self.calculate_no_show_rate(period),
            'cancellation_rate': self.calculate_cancellation_rate(period),
            'visits_by_type': self.group_visits_by_type(period),
            'provider_utilization': self.calculate_provider_utilization(period),
            'peak_usage_times': self.analyze_usage_patterns(period)
        }

    def calculate_technical_metrics(self, period):
        return {
            'average_connection_time': self.avg_connection_time(period),
            'technical_failure_rate': self.calculate_failure_rate(period),
            'average_video_quality': self.avg_video_quality(period),
            'average_audio_quality': self.avg_audio_quality(period),
            'disconnection_rate': self.calculate_disconnection_rate(period),
            'browser_compatibility': self.analyze_browser_usage(period),
            'support_tickets': self.count_support_tickets(period)
        }

    def calculate_patient_experience(self, period):
        return {
            'satisfaction_score': self.avg_satisfaction_score(period),
            'net_promoter_score': self.calculate_nps(period),
            'ease_of_use_rating': self.avg_ease_of_use(period),
            'would_use_again': self.calculate_return_intent(period),
            'common_complaints': self.analyze_feedback(period),
            'wait_time_satisfaction': self.avg_wait_satisfaction(period)
        }
```

## Continuous Improvement

### Workflow Optimization Framework
```yaml
optimization_areas:
  scheduling:
    - Implement smart scheduling based on visit type
    - Optimize appointment duration by chief complaint
    - Reduce no-show through automated reminders

  technical:
    - Pre-visit technology checks mandatory
    - Automated troubleshooting guides
    - Fallback to phone if video fails

  clinical:
    - Provider training on virtual examination techniques
    - Specialty-specific telehealth protocols
    - Integration with remote monitoring devices

  patient_experience:
    - Simplified login process
    - Mobile app development
    - Reduce clicks to join visit
    - After-visit survey automation

  documentation:
    - Telehealth-specific templates
    - Voice-to-text documentation
    - Auto-population from conversation
```

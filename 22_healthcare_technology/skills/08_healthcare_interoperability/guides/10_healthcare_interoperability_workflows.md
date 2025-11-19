# Healthcare Interoperability Workflows Guide

## Complete Workflows for Common Healthcare Scenarios

## Workflow 1: Emergency Department Patient Registration

### Flow Diagram
```
Patient Arrives
    ↓
Registration Clerk Checks In
    ↓
EDI Admission (HL7 ADT^A04)
    ↓
Master Patient Index Query (FHIR Patient)
    ↓
EHR Creates Patient Record
    ↓
Alert Alert if Duplicates
    ↓
Triage Nurse Takes Vitals
    ↓
Observations Submitted (HL7 OBX / FHIR Observation)
    ↓
Orders Placed by ED Physician
    ↓
Lab/Imaging System Receives Orders (HL7 ORM)
    ↓
Results Transmitted Back (HL7 ORU)
    ↓
Physician Reviews and Treats
    ↓
Patient Discharged or Admitted
```

### Implementation Code

```python
class EmergencyDepartmentWorkflow:
    def __init__(self, hl7_client, fhir_client, mpi_service):
        self.hl7 = hl7_client
        self.fhir = fhir_client
        self.mpi = mpi_service

    def check_in_patient(self, registration_data):
        """Step 1: Patient registration"""
        try:
            # Check MPI for duplicates
            existing_patient = self.mpi.search(
                last_name=registration_data['last_name'],
                first_name=registration_data['first_name'],
                dob=registration_data['dob']
            )

            if existing_patient:
                patient_id = existing_patient['id']
                print(f"Existing patient found: {patient_id}")
            else:
                # Create new patient in FHIR
                fhir_patient = self.create_fhir_patient(registration_data)
                patient_id = fhir_patient['id']

                # Register in MPI
                self.mpi.register(fhir_patient)

            # Send HL7 ADT message
            adt_message = self.generate_adt_a04(patient_id, registration_data)
            self.hl7.send_message(adt_message)

            return {'status': 'success', 'patient_id': patient_id}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def record_vital_signs(self, patient_id, vitals):
        """Step 2: Record observations"""
        try:
            observations = []

            # Temperature
            observations.append(self.create_observation(
                patient_id,
                code='8310-5',  # Body temperature LOINC
                value=vitals['temperature'],
                unit='Cel'
            ))

            # Blood pressure
            observations.append(self.create_observation(
                patient_id,
                code='8480-6',  # Systolic BP
                value=vitals['systolic'],
                unit='mm[Hg]'
            ))

            # Send to FHIR server
            for obs in observations:
                self.fhir.create('Observation', obs)

            # Also send as HL7 OBX
            obx_message = self.generate_obx_observations(patient_id, observations)
            self.hl7.send_message(obx_message)

            return {'status': 'success', 'observations_count': len(observations)}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def place_lab_order(self, patient_id, order_data):
        """Step 3: Place lab order"""
        try:
            # Create service request in FHIR
            service_request = {
                'resourceType': 'ServiceRequest',
                'status': 'active',
                'intent': 'order',
                'code': {
                    'coding': [{'system': 'http://loinc.org', 'code': order_data['test_code']}]
                },
                'subject': {'reference': f'Patient/{patient_id}'},
                'requester': {'reference': f'Practitioner/{order_data["provider_id"]}'}
            }

            service_request = self.fhir.create('ServiceRequest', service_request)

            # Send HL7 ORM order message to lab system
            orm_message = self.generate_orm_order(patient_id, order_data)
            self.hl7.send_message(orm_message)

            return {'status': 'success', 'order_id': service_request['id']}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def receive_lab_results(self, hl7_result_message):
        """Step 4: Receive lab results"""
        try:
            # Parse HL7 result message
            parsed = self.hl7.parse_message(hl7_result_message)

            # Extract patient ID and results
            patient_id = self.extract_patient_id(parsed)
            results = self.extract_results(parsed)

            # Create FHIR diagnostic report
            diagnostic_report = {
                'resourceType': 'DiagnosticReport',
                'status': 'final',
                'category': [{'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/v2-0074', 'code': 'LAB'}]}],
                'subject': {'reference': f'Patient/{patient_id}'},
                'result': [{'reference': f'Observation/{r["id"]}'} for r in results]
            }

            self.fhir.create('DiagnosticReport', diagnostic_report)

            # Notify physician
            self.notify_provider(patient_id, f"Lab results available for patient {patient_id}")

            return {'status': 'success', 'results_count': len(results)}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def create_fhir_patient(self, data):
        """Helper: Create FHIR patient resource"""
        patient = {
            'resourceType': 'Patient',
            'name': [{'family': data['last_name'], 'given': [data['first_name']]}],
            'birthDate': data['dob'],
            'gender': data['gender'].lower(),
            'identifier': [{'system': 'http://hospital/mrn', 'value': data['mrn']}]
        }
        return self.fhir.create('Patient', patient)

    def create_observation(self, patient_id, code, value, unit):
        """Helper: Create observation resource"""
        return {
            'resourceType': 'Observation',
            'status': 'final',
            'code': {'coding': [{'system': 'http://loinc.org', 'code': code}]},
            'subject': {'reference': f'Patient/{patient_id}'},
            'valueQuantity': {'value': value, 'unit': unit}
        }
```

## Workflow 2: Cardiology Referral Process

### Flow Diagram
```
PCP Orders Referral
    ↓
EHR Generates Referral Document
    ↓
EHR Retrieves Latest Observations
    ↓
Generate PDF Report
    ↓
Send via Direct Secure Email
    ↓
Cardiologist Receives
    ↓
Cardiologist Accesses FHIR Patient Data (if sharing agreement)
    ↓
Cardiologist Reviews and Plans
    ↓
Cardiologist Sends Report via Direct
    ↓
PCP Receives and Reviews
    ↓
Shared Care Plan Updated
```

### Implementation Code

```python
class ReferralWorkflow:
    def __init__(self, ehr_system, direct_client, fhir_client):
        self.ehr = ehr_system
        self.direct = direct_client
        self.fhir = fhir_client

    def initiate_referral(self, patient_id, specialty, provider_direct_address):
        """Initiate specialist referral"""
        try:
            # Get patient and recent data
            patient = self.fhir.read('Patient', patient_id)
            conditions = self.fhir.search('Condition', {'patient': patient_id})
            observations = self.fhir.search('Observation', {'patient': patient_id, '_count': 10})
            medications = self.fhir.search('MedicationStatement', {'patient': patient_id})

            # Generate referral document
            pdf_content = self.generate_referral_pdf(
                patient,
                conditions,
                observations,
                medications,
                specialty
            )

            # Create referral request in FHIR
            service_request = {
                'resourceType': 'ServiceRequest',
                'status': 'active',
                'intent': 'order',
                'category': [{'coding': [{'code': specialty}]}],
                'subject': {'reference': f'Patient/{patient_id}'},
                'requester': {'reference': f'Practitioner/{self.get_current_provider()}'},
                'specialty': {'coding': [{'code': specialty}]}
            }

            sr = self.fhir.create('ServiceRequest', service_request)

            # Send via Direct
            email_body = f"""
Referral for {patient['name'][0]['family']}, {patient['name'][0]['given'][0]}

Patient Details:
- DOB: {patient['birthDate']}
- MRN: {patient['identifier'][0]['value']}

Recent Conditions: {len(conditions)} conditions
Recent Labs: {len(observations)} observations
Current Medications: {len(medications)} medications

Please see attached PDF for detailed clinical information.

If you need access to the patient's full records, please request access through the FHIR portal.

Thanks,
{self.ehr.get_provider_name()}
"""

            self.direct.send_message(
                recipient_direct_address=provider_direct_address,
                subject=f'Cardiology Referral - {patient["name"][0]["family"]}',
                body=email_body,
                attachments=[('referral.pdf', pdf_content)]
            )

            return {'status': 'success', 'referral_id': sr['id']}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def generate_referral_pdf(self, patient, conditions, observations, medications, specialty):
        """Generate PDF referral document"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, f"{specialty} Referral")

        # Patient info
        c.setFont("Helvetica", 10)
        y = 700
        c.drawString(50, y, f"Patient: {patient['name'][0]['family']}, {patient['name'][0]['given'][0]}")
        y -= 20
        c.drawString(50, y, f"DOB: {patient['birthDate']}")
        y -= 20
        c.drawString(50, y, f"MRN: {patient['identifier'][0]['value']}")

        # Conditions
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Diagnoses:")
        y -= 15
        c.setFont("Helvetica", 10)
        for condition in conditions.get('entry', [])[:5]:
            cond = condition['resource']
            c.drawString(70, y, f"- {cond['code'].get('text', 'Unknown')}")
            y -= 15

        # Observations
        y -= 15
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Recent Results:")
        y -= 15
        c.setFont("Helvetica", 10)
        for obs in observations.get('entry', [])[:5]:
            o = obs['resource']
            value = o.get('valueQuantity', {}).get('value')
            unit = o.get('valueQuantity', {}).get('unit')
            c.drawString(70, y, f"- {o['code'].get('text', 'Unknown')}: {value} {unit}")
            y -= 15

        c.save()
        return buffer.getvalue()
```

## Workflow 3: Patient Portal Access (SMART on FHIR)

### Flow Diagram
```
Patient Logs into Portal
    ↓
Portal Initiates SMART Launch
    ↓
EHR Provides Authorization Context
    ↓
Portal Redirects to OAuth Server
    ↓
Patient Approves Scopes
    ↓
OAuth Server Issues Access Token
    ↓
Portal Uses Token to Call FHIR APIs
    ↓
Patient Views Their Health Data
    ↓
Patient Can Message Provider
    ↓
Patient Can Request Prescription
```

### Implementation Code

```javascript
class PatientPortal {
    constructor() {
        this.client = null;
    }

    async initializeSmartApp() {
        // Initialize SMART on FHIR
        this.client = await FHIR.oauth2.init({
            clientId: 'patient-portal-app',
            scopes: [
                'patient/Patient.read',
                'patient/Observation.read',
                'patient/Condition.read',
                'patient/MedicationRequest.read',
                'patient/DocumentReference.read'
            ],
            redirectUri: window.location.origin + '/callback'
        });

        // Load patient data
        this.loadPatientData();
    }

    async loadPatientData() {
        try {
            // Get patient
            const patient = await this.client.patient.read();

            // Get observations
            const obsResponse = await this.client.patient.request(
                `Observation?patient=${this.client.patient.id}&_sort=-date&_count=20`
            );

            // Get conditions
            const condResponse = await this.client.patient.request(
                `Condition?patient=${this.client.patient.id}`
            );

            // Get medications
            const medResponse = await this.client.patient.request(
                `MedicationRequest?patient=${this.client.patient.id}`
            );

            // Get documents
            const docResponse = await this.client.patient.request(
                `DocumentReference?patient=${this.client.patient.id}&_sort=-date&_count=10`
            );

            // Display data
            this.displayPatientInfo(patient);
            this.displayObservations(obsResponse.entry || []);
            this.displayConditions(condResponse.entry || []);
            this.displayMedications(medResponse.entry || []);
            this.displayDocuments(docResponse.entry || []);

        } catch (error) {
            console.error('Error loading patient data:', error);
            this.showError('Unable to load health data');
        }
    }

    displayPatientInfo(patient) {
        document.getElementById('patient-name').textContent =
            `${patient.name[0].given.join(' ')} ${patient.name[0].family}`;

        document.getElementById('dob').textContent =
            `DOB: ${patient.birthDate}`;

        document.getElementById('gender').textContent =
            `Gender: ${patient.gender}`;
    }

    displayObservations(observations) {
        const container = document.getElementById('observations');

        observations.slice(0, 10).forEach(entry => {
            const obs = entry.resource;
            const value = obs.valueQuantity?.value;
            const unit = obs.valueQuantity?.unit;
            const code = obs.code.coding[0].display;

            const div = document.createElement('div');
            div.innerHTML = `
                <p>
                    <strong>${code}</strong>: ${value} ${unit}
                    <small>${new Date(obs.effectiveDateTime).toLocaleDateString()}</small>
                </p>
            `;

            container.appendChild(div);
        });
    }

    async requestPrescription() {
        // Allow patient to request medication refill
        const medicationSelect = document.getElementById('medication-select');
        const selectedMed = medicationSelect.value;

        try {
            const response = await fetch('/api/prescription-request', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    patient_id: this.client.patient.id,
                    medication_id: selectedMed,
                    message: document.getElementById('refill-message').value
                })
            });

            if (response.ok) {
                alert('Prescription request sent to your provider');
            }
        } catch (error) {
            console.error('Error requesting prescription:', error);
        }
    }
}

// Initialize on page load
window.addEventListener('load', () => {
    const portal = new PatientPortal();
    portal.initializeSmartApp();
});
```

## Workflow 4: Pharmacy Prescription Fulfillment

### Flow Diagram
```
Physician Orders Medication (RXE)
    ↓
Sends to Pharmacy via HL7 / FHIR
    ↓
Pharmacy Receives Order
    ↓
Pharmacist Verifies
    ↓
Check Drug Interactions (RxNorm API)
    ↓
Check Patient Allergies
    ↓
Alert if Contraindications Found
    ↓
Pharmacist Approves
    ↓
Technician Fills Prescription
    ↓
Pharmacist Double-checks
    ↓
Patient Picks Up
    ↓
Pharmacy Sends Fulfillment Confirmation
    ↓
EHR Updates MedicationStatement
```

### Implementation Code

```python
class PharmacyWorkflow:
    def __init__(self, hl7_client, fhir_client, rxnorm_service):
        self.hl7 = hl7_client
        self.fhir = fhir_client
        self.rxnorm = rxnorm_service

    def process_medication_order(self, hl7_rxe_message):
        """Process incoming medication order"""
        try:
            # Parse HL7
            parsed = self.hl7.parse_message(hl7_rxe_message)

            # Extract prescription details
            patient_id = self.extract_field(parsed, 'PID', 2)
            medication_code = self.extract_field(parsed, 'RXE', 2)
            dose = self.extract_field(parsed, 'RXE', 4)
            instructions = self.extract_field(parsed, 'RXE', 13)

            # Verify medication
            rxnorm_info = self.rxnorm.get_drug_info(medication_code)
            if not rxnorm_info:
                return self.send_reject('Invalid medication code')

            # Check for interactions and allergies
            patient = self.fhir.read('Patient', patient_id)
            allergies = self.fhir.search('AllergyIntolerance', {'patient': patient_id})
            current_meds = self.fhir.search('MedicationStatement', {'patient': patient_id})

            warnings = self.check_safety(medication_code, allergies, current_meds)

            if warnings:
                # Alert pharmacist
                self.alert_pharmacist(patient_id, warnings)

            # Create medication request in FHIR
            med_request = {
                'resourceType': 'MedicationRequest',
                'status': 'active',
                'intent': 'order',
                'medicationCodeableConcept': {
                    'coding': [{'system': 'http://www.nlm.nih.gov/research/umls/rxnorm', 'code': medication_code}]
                },
                'subject': {'reference': f'Patient/{patient_id}'},
                'dosageInstruction': [{'text': f'{dose} {instructions}'}]
            }

            med_req = self.fhir.create('MedicationRequest', med_request)

            # Send acknowledgment
            self.send_ack(hl7_rxe_message)

            return {'status': 'success', 'order_id': med_req['id']}

        except Exception as e:
            self.send_reject(str(e))
            return {'status': 'error', 'message': str(e)}

    def check_safety(self, medication_code, allergies, current_meds):
        """Check for drug interactions and allergies"""
        warnings = []

        # Check allergies
        for allergy in allergies.get('entry', []):
            allergen = allergy['resource']['code']['coding'][0]['code']
            if allergen == medication_code:
                warnings.append(f"ALLERGY: Patient allergic to this medication")

        # Check interactions
        current_codes = [m['resource']['medicationCodeableConcept']['coding'][0]['code']
                        for m in current_meds.get('entry', [])]

        if current_codes:
            interactions = self.rxnorm.check_interactions(current_codes + [medication_code])
            if interactions.get('interaction'):
                warnings.extend([f"INTERACTION: {i}" for i in interactions['interaction']])

        return warnings

    def send_ack(self, original_message):
        """Send acknowledgment back to EHR"""
        ack = f"MSH|^~\\&|PHARMACY|PHARM|EHR|HOSPITAL|{datetime.now().isoformat()}||ACK|{uuid.uuid4()}|P|2.5.1\n"
        ack += f"MSA|AA|MSG001|Order received and processing"
        self.hl7.send_message(ack)
```

## Next Steps

1. Map your organization's workflows
2. Identify required standards (HL7, FHIR, Direct, etc.)
3. Select integration tools and platforms
4. Test with sample data
5. Train staff on new workflows
6. Deploy with monitoring and support

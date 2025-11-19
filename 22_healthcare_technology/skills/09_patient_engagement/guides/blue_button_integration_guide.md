# Blue Button Integration Guide

## CCDA XML Export Implementation

### Parser Development
```python
from lxml import etree
from dateutil import parser as dateutil_parser

class CCDAParser:
    """Parse CCDA XML export and map to FHIR"""

    def __init__(self, ccda_file):
        self.tree = etree.parse(ccda_file)
        self.root = self.tree.getroot()
        self.namespaces = {
            'cda': 'urn:hl7-org:v3',
            'sdtc': 'urn:hl7-org:sdtc'
        }

    def extract_patient(self):
        """Extract patient demographics"""
        record_target = self.root.xpath(
            '//cda:recordTarget/cda:patientRole',
            namespaces=self.namespaces
        )[0]

        patient = {
            'mrn': record_target.find('cda:id', self.namespaces).get('extension'),
            'given_name': record_target.xpath(
                './/cda:name/cda:given/text()',
                namespaces=self.namespaces
            )[0] if record_target.xpath(
                './/cda:name/cda:given',
                namespaces=self.namespaces
            ) else None,
            'family_name': record_target.xpath(
                './/cda:name/cda:family/text()',
                namespaces=self.namespaces
            )[0] if record_target.xpath(
                './/cda:name/cda:family',
                namespaces=self.namespaces
            ) else None,
            'dob': record_target.xpath(
                './/cda:birthTime/@value',
                namespaces=self.namespaces
            )[0] if record_target.xpath(
                './/cda:birthTime',
                namespaces=self.namespaces
            ) else None
        }
        return patient

    def extract_problems(self):
        """Extract problems/diagnoses"""
        problems = []
        problem_entries = self.root.xpath(
            '//cda:section[cda:templateId/@root="2.16.840.1.113883.10.20.22.2.1.1"]'
            '//cda:entry/cda:act',
            namespaces=self.namespaces
        )

        for entry in problem_entries:
            obs = entry.find('.//cda:observation', self.namespaces)
            if obs is not None:
                code_elem = obs.find('cda:code', self.namespaces)
                status_elem = obs.find('cda:statusCode', self.namespaces)

                problem = {
                    'code': code_elem.get('code') if code_elem is not None else None,
                    'code_system': code_elem.get('codeSystem') if code_elem is not None else None,
                    'display': code_elem.get('displayName') if code_elem is not None else None,
                    'status': status_elem.get('code') if status_elem is not None else None
                }
                problems.append(problem)

        return problems

    def extract_medications(self):
        """Extract medications"""
        medications = []
        med_entries = self.root.xpath(
            '//cda:section[cda:templateId/@root="2.16.840.1.113883.10.20.22.2.1"]'
            '//cda:entry/cda:substanceAdministration',
            namespaces=self.namespaces
        )

        for entry in med_entries:
            med_material = entry.find(
                './/cda:consumable/cda:manufacturedProduct/cda:manufacturedMaterial',
                self.namespaces
            )
            dose = entry.find('cda:doseQuantity', self.namespaces)

            medication = {
                'rxnorm_code': med_material.find('cda:code', self.namespaces).get('code') if med_material is not None else None,
                'drug_name': med_material.find('cda:code', self.namespaces).get('displayName') if med_material is not None else None,
                'dose': dose.get('value') if dose is not None else None,
                'unit': dose.get('unit') if dose is not None else None,
                'status': entry.find('cda:statusCode', self.namespaces).get('code') if entry.find('cda:statusCode', self.namespaces) is not None else None
            }
            medications.append(medication)

        return medications

    def extract_allergies(self):
        """Extract allergies"""
        allergies = []
        allergy_entries = self.root.xpath(
            '//cda:section[cda:templateId/@root="2.16.840.1.113883.10.20.22.2.6.1"]'
            '//cda:entry/cda:act',
            namespaces=self.namespaces
        )

        for entry in allergy_entries:
            obs = entry.find('.//cda:observation', self.namespaces)
            if obs is not None:
                substance = obs.find('.//cda:participant/cda:participantRole/cda:playingEntity/cda:code', self.namespaces)
                reaction = obs.find('.//cda:entryRelationship[cda:observation/cda:code/@code="ROLO"]', self.namespaces)

                allergy = {
                    'substance': substance.get('displayName') if substance is not None else None,
                    'code': substance.get('code') if substance is not None else None,
                    'reaction': reaction.find('.//cda:value', self.namespaces).get('displayName') if reaction is not None else None,
                    'severity': obs.find('.//cda:entryRelationship[cda:observation/cda:code/@code="SEV"]//cda:value', self.namespaces).get('displayName') if obs.find('.//cda:entryRelationship[cda:observation/cda:code/@code="SEV"]', self.namespaces) is not None else None
                }
                allergies.append(allergy)

        return allergies
```

### FHIR Conversion
```python
class CCDAToFHIRConverter:
    """Convert CCDA to FHIR resources"""

    @staticmethod
    def problem_to_condition(problem):
        """Convert CCDA problem to FHIR Condition"""
        return {
            "resourceType": "Condition",
            "code": {
                "coding": [{
                    "system": "http://hl7.org/fhir/sid/icd-10-cm",
                    "code": problem.get('code'),
                    "display": problem.get('display')
                }]
            },
            "clinicalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active" if problem.get('status') == 'active' else "resolved"
                }]
            }
        }

    @staticmethod
    def medication_to_statement(medication):
        """Convert CCDA medication to FHIR MedicationStatement"""
        return {
            "resourceType": "MedicationStatement",
            "medicationCodeableConcept": {
                "coding": [{
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code": medication.get('rxnorm_code'),
                    "display": medication.get('drug_name')
                }]
            },
            "status": "active" if medication.get('status') == 'active' else "completed",
            "dosage": [{
                "dose": {
                    "value": medication.get('dose'),
                    "unit": medication.get('unit')
                }
            }]
        }
```

## FHIR API Implementation

### Patient-Authorized Data Access
```javascript
// OAuth2 + SMART on FHIR implementation
class FHIRDataAccessService {
  async initiatePatientAuthorization(provider, dataElements) {
    // Patient selects which data to share
    const consentRecord = {
      patient: currentUser.id,
      provider: provider.id,
      grantedScopes: [
        'patient/Patient.read',
        'patient/Condition.read',
        'patient/Medication.read',
        dataElements.includes('labs') ? 'patient/Observation.read' : null
      ].filter(Boolean),
      expirationDate: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000), // 1 year
      createdDate: new Date()
    };

    // Save consent to database
    await fetch(`${API_URL}/consents`, {
      method: 'POST',
      body: JSON.stringify(consentRecord)
    });

    // Return authorization URL for provider to complete
    return {
      authUrl: `${AUTH_SERVER}/authorize?client_id=${PROVIDER_CLIENT_ID}&scope=${consentRecord.grantedScopes.join('%20')}&redirect_uri=${PROVIDER_REDIRECT_URI}`
    };
  }

  async handlePatientDataRequest(req) {
    // Verify consent exists
    const consent = await this.verifyConsent(
      req.user.id,
      req.provider.id,
      req.requestedScope
    );

    if (!consent) {
      throw new Error('No valid consent for this data access');
    }

    // Return only consented data elements
    const fhirData = await this.fetchFHIRData(req.user.id, consent.grantedScopes);
    return fhirData;
  }
}
```

## Blue Button File Generation

### Export Formats
```python
class BlueButtonExportService:
    async def generateExport(self, patient_id, formats=['ccda', 'fhir', 'pdf']):
        patient_data = await self.getCompletePatientData(patient_id)

        exports = {}

        if 'ccda' in formats:
            exports['ccda'] = self.generate_ccda_xml(patient_data)

        if 'fhir' in formats:
            exports['fhir'] = self.generate_fhir_bundle(patient_data)

        if 'pdf' in formats:
            exports['pdf'] = await self.generate_pdf_report(patient_data)

        if 'csv' in formats:
            exports['csv'] = self.generate_csv_export(patient_data)

        # Create ZIP file with all formats
        zip_file = await self.create_export_zip(exports)

        # Log the export
        await self.log_export(patient_id, formats)

        return zip_file
```

## Testing and Validation

### CCDA Validation
```python
# Validate CCDA against schema
from xml.etree import ElementTree as ET

class CCDAValidator:
    def validate_ccda(self, ccda_file):
        """Validate CCDA against schema"""
        tree = ET.parse(ccda_file)
        schema = ET.XMLSchema(file='ccda-schema.xsd')

        if not schema.validate(tree):
            errors = schema.error_log
            return {
                'valid': False,
                'errors': [{'line': err.lineno, 'message': err.message} for err in errors]
            }

        return {'valid': True}

    def test_ccda_completeness(self, ccda_file):
        """Check for required sections"""
        required_sections = [
            '2.16.840.1.113883.10.20.22.2.1',  # Medications
            '2.16.840.1.113883.10.20.22.2.6',  # Allergies
            '2.16.840.1.113883.10.20.22.2.1.1'  # Problems
        ]

        missing_sections = []
        for section_id in required_sections:
            if f'templateId[@root="{section_id}"]' not in ccda_file:
                missing_sections.append(section_id)

        return {'missing': missing_sections}
```

## Patient Portal Integration

### Blue Button UI Component
```javascript
// React component for Blue Button
function BlueButtonDownload({ patientId }) {
  const [exportStatus, setExportStatus] = useState('ready');
  const [selectedFormats, setSelectedFormats] = useState(['ccda', 'pdf']);

  const handleExport = async () => {
    setExportStatus('exporting');

    try {
      const response = await fetch(
        `${API_URL}/patients/${patientId}/export`,
        {
          method: 'POST',
          body: JSON.stringify({ formats: selectedFormats })
        }
      );

      const { zip_url } = await response.json();

      // Download file
      const a = document.createElement('a');
      a.href = zip_url;
      a.download = `health-data-${new Date().toISOString().split('T')[0]}.zip`;
      document.body.appendChild(a);
      a.click();

      setExportStatus('complete');
    } catch (error) {
      setExportStatus('error');
    }
  };

  return (
    <div className="blue-button-export">
      <h2>Download Your Health Data</h2>

      <div className="format-selection">
        <label>
          <input
            type="checkbox"
            checked={selectedFormats.includes('ccda')}
            onChange={(e) => {
              if (e.target.checked) {
                setSelectedFormats([...selectedFormats, 'ccda']);
              } else {
                setSelectedFormats(selectedFormats.filter(f => f !== 'ccda'));
              }
            }}
          />
          CCDA XML (standard clinical format)
        </label>
        <label>
          <input
            type="checkbox"
            checked={selectedFormats.includes('fhir')}
            onChange={(e) => {
              if (e.target.checked) {
                setSelectedFormats([...selectedFormats, 'fhir']);
              } else {
                setSelectedFormats(selectedFormats.filter(f => f !== 'fhir'));
              }
            }}
          />
          FHIR JSON (for apps and portals)
        </label>
        <label>
          <input
            type="checkbox"
            checked={selectedFormats.includes('pdf')}
            onChange={(e) => {
              if (e.target.checked) {
                setSelectedFormats([...selectedFormats, 'pdf']);
              } else {
                setSelectedFormats(selectedFormats.filter(f => f !== 'pdf'));
              }
            }}
          />
          PDF (human-readable format)
        </label>
      </div>

      <button
        onClick={handleExport}
        disabled={exportStatus !== 'ready'}
      >
        {exportStatus === 'exporting' ? 'Exporting...' : 'Download My Health Data'}
      </button>

      {exportStatus === 'complete' && (
        <p className="success">Your health data is ready to download!</p>
      )}
      {exportStatus === 'error' && (
        <p className="error">Error downloading. Please try again.</p>
      )}
    </div>
  );
}
```

## Compliance and Security

### Access Audit Logging
```python
async def log_blue_button_access(patient_id, action, export_format):
    """Log all Blue Button exports for audit"""
    await AuditLog.create({
        patient_id=patient_id,
        action='blue_button_export',
        export_formats=export_format,
        timestamp=datetime.utcnow(),
        user_ip=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        status='success'
    })

async def verify_access_and_log(patient_id, requesting_user_id):
    """Verify patient requested their own data"""
    if patient_id != requesting_user_id:
        await AuditLog.create({
            patient_id=patient_id,
            action='unauthorized_export_attempt',
            requesting_user_id=requesting_user_id,
            status='denied',
            timestamp=datetime.utcnow()
        })
        raise UnauthorizedError("Cannot export other patient's data")
```


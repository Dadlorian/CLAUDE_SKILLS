# Data Transformation & Integration Guide

## Step 1: HL7 to FHIR Transformation

### Mapping Table
```
HL7 v2.x        FHIR R4
MSH             MessageHeader
PID             Patient
OBX             Observation
ORC             ServiceRequest
RXE             MedicationRequest
DG1             Condition
PV1             Encounter
```

### Implementation (Python)

```python
import json
from datetime import datetime

class HL7ToFHIRTransformer:
    def transform_patient(self, hl7_pid_segment):
        """Transform HL7 PID to FHIR Patient"""
        return {
            "resourceType": "Patient",
            "id": self.generate_id(),
            "identifier": [
                {
                    "system": "http://hospital/mrn",
                    "value": hl7_pid_segment[2][0][0]  # MRN
                }
            ],
            "name": [
                {
                    "family": hl7_pid_segment[4][0][0],  # Family name
                    "given": [hl7_pid_segment[4][0][1]]   # Given name
                }
            ],
            "birthDate": self.parse_date(hl7_pid_segment[7]),
            "gender": self.map_gender(hl7_pid_segment[8]),
            "address": [
                {
                    "line": [hl7_pid_segment[10][0][0]],
                    "city": hl7_pid_segment[10][0][2],
                    "state": hl7_pid_segment[10][0][3],
                    "postalCode": hl7_pid_segment[10][0][4]
                }
            ] if hl7_pid_segment[10] else [],
            "telecom": [
                {
                    "system": "phone",
                    "value": hl7_pid_segment[12][0][0]
                }
            ] if hl7_pid_segment[12] else []
        }

    def transform_observation(self, hl7_obx_segment, patient_id):
        """Transform HL7 OBX to FHIR Observation"""
        obx_id = hl7_obx_segment[1]
        obx_type = hl7_obx_segment[2]
        obs_identifier = hl7_obx_segment[3]
        obs_value = hl7_obx_segment[5]
        obs_units = hl7_obx_segment[6]

        observation = {
            "resourceType": "Observation",
            "id": self.generate_id(),
            "status": "final",
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": obs_identifier[0],
                        "display": obs_identifier[1]
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "issued": datetime.now().isoformat() + "Z"
        }

        # Add value based on type
        if obx_type == "NM":  # Numeric
            observation["valueQuantity"] = {
                "value": float(obs_value),
                "unit": obs_units,
                "system": "http://unitsofmeasure.org",
                "code": self.map_unit(obs_units)
            }
        elif obx_type == "ST":  # String
            observation["valueString"] = obs_value
        elif obx_type == "CE":  # Coded
            observation["valueCodeableConcept"] = {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": obs_value[0],
                        "display": obs_value[1]
                    }
                ]
            }

        return observation

    def transform_medication(self, hl7_rxe_segment, patient_id):
        """Transform HL7 RXE to FHIR MedicationRequest"""
        return {
            "resourceType": "MedicationRequest",
            "id": self.generate_id(),
            "status": "active",
            "intent": "order",
            "medicationCodeableConcept": {
                "coding": [
                    {
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                        "code": hl7_rxe_segment[2][0]
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "dosageInstruction": [
                {
                    "sequence": 1,
                    "text": self.format_dosage(hl7_rxe_segment),
                    "timing": {
                        "repeat": {
                            "frequency": self.parse_frequency(hl7_rxe_segment[13]),
                            "period": 1,
                            "periodUnit": "d"
                        }
                    }
                }
            ]
        }

    def parse_date(self, date_str):
        """Parse HL7 date format YYYYMMDD to ISO format"""
        if not date_str or len(date_str) < 8:
            return None
        try:
            return datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
        except:
            return None

    def map_gender(self, gender):
        """Map HL7 gender to FHIR"""
        mapping = {
            'M': 'male',
            'F': 'female',
            'O': 'other',
            'U': 'unknown'
        }
        return mapping.get(gender, 'unknown')

    def map_unit(self, unit):
        """Map HL7 units to UCUM codes"""
        mapping = {
            'mg/dL': 'mg/dL',
            'mmol/L': 'mmol/L',
            '%': '%',
            'bpm': '/min',
            'mmHg': 'mm[Hg]'
        }
        return mapping.get(unit, unit)

    def format_dosage(self, rxe_segment):
        """Format medication dosage instruction"""
        dose = rxe_segment[4]
        unit = rxe_segment[5]
        frequency = rxe_segment[13]
        return f"{dose} {unit} {frequency}"

    def parse_frequency(self, freq_str):
        """Parse frequency string"""
        freq_map = {
            'QID': 4,      # Four times daily
            'TID': 3,      # Three times daily
            'BID': 2,      # Twice daily
            'QD': 1,       # Once daily
            'Q6H': 4,      # Every 6 hours
            'Q8H': 3,      # Every 8 hours
            'Q12H': 2      # Every 12 hours
        }
        return freq_map.get(freq_str, 1)

    def generate_id(self):
        """Generate unique ID"""
        import uuid
        return str(uuid.uuid4())
```

## Step 2: FHIR to HL7 Reverse Transformation

```python
class FHIRToHL7Transformer:
    def transform_patient_to_pid(self, fhir_patient):
        """Transform FHIR Patient to HL7 PID segment"""
        pid = ['PID']

        # Identifier
        mrn = self.extract_mrn(fhir_patient)
        pid.append('')  # Set ID - PID
        pid.append(f'||{mrn}^^^MRN')

        # Name
        name = fhir_patient['name'][0] if fhir_patient.get('name') else {}
        family = name.get('family', '')
        given = '^'.join(name.get('given', []))
        pid.append(f'||{family}^{given}')

        # DOB
        dob = fhir_patient.get('birthDate', '')
        pid.append(f'||{dob.replace("-", "")}')

        # Gender
        gender = self.map_fhir_gender(fhir_patient.get('gender'))
        pid.append(f'|{gender}')

        return '|'.join(pid)

    def transform_observation_to_obx(self, fhir_obs):
        """Transform FHIR Observation to HL7 OBX segment"""
        obx = ['OBX']

        # Sequence
        obx.append('1')

        # Data Type
        value_type = self.get_value_type(fhir_obs)
        obx.append(value_type)

        # Code
        coding = fhir_obs['code']['coding'][0]
        obx.append(f'|{coding["code"]}^{coding["display"]}')

        # Value
        value = self.extract_value(fhir_obs)
        obx.append(f'|{value}')

        # Units
        if 'valueQuantity' in fhir_obs:
            unit = fhir_obs['valueQuantity'].get('unit', '')
            obx.append(f'|{unit}')

        return '|'.join(obx)

    def extract_mrn(self, patient):
        """Extract MRN from FHIR Patient"""
        for identifier in patient.get('identifier', []):
            if 'mrn' in identifier.get('system', '').lower():
                return identifier['value']
        return ''

    def map_fhir_gender(self, gender):
        """Map FHIR gender to HL7"""
        mapping = {
            'male': 'M',
            'female': 'F',
            'other': 'O',
            'unknown': 'U'
        }
        return mapping.get(gender, 'U')

    def get_value_type(self, observation):
        """Determine HL7 OBX value type"""
        if 'valueQuantity' in observation:
            return 'NM'  # Numeric
        elif 'valueString' in observation:
            return 'ST'  # String
        elif 'valueCodeableConcept' in observation:
            return 'CE'  # Coded
        else:
            return 'NM'

    def extract_value(self, observation):
        """Extract value from FHIR observation"""
        if 'valueQuantity' in observation:
            return str(observation['valueQuantity']['value'])
        elif 'valueString' in observation:
            return observation['valueString']
        elif 'valueCodeableConcept' in observation:
            coding = observation['valueCodeableConcept']['coding'][0]
            return f"{coding['code']}^{coding['display']}"
        return ''
```

## Step 3: Code Mapping During Transformation

```python
class MappingTransformer:
    def __init__(self, mapping_service):
        self.mapping = mapping_service

    def transform_with_mapping(self, source_data, source_format, target_format):
        """Transform and apply code mappings"""
        if source_format == 'hl7' and target_format == 'fhir':
            return self.transform_hl7_to_fhir_mapped(source_data)
        elif source_format == 'fhir' and target_format == 'hl7':
            return self.transform_fhir_to_hl7_mapped(source_data)

    def transform_hl7_to_fhir_mapped(self, hl7_data):
        """Transform HL7 to FHIR with code mapping"""
        transformer = HL7ToFHIRTransformer()
        fhir_resource = transformer.transform_patient(hl7_data)

        # Map codes
        for condition in hl7_data.get('diagnoses', []):
            mapped = self.mapping.map_code(
                condition['code'],
                'local',
                'snomed'
            )
            condition['snomed_code'] = mapped['code']
            condition['snomed_display'] = mapped['display']

        return fhir_resource

    def transform_fhir_to_hl7_mapped(self, fhir_data):
        """Transform FHIR to HL7 with code mapping"""
        transformer = FHIRToHL7Transformer()

        # Map diagnosis codes back to local system
        for condition in fhir_data.get('contained', []):
            if condition['resourceType'] == 'Condition':
                mapped = self.mapping.map_code(
                    condition['code']['coding'][0]['code'],
                    'snomed',
                    'local'
                )

        return transformer.transform_patient_to_pid(fhir_data)
```

## Step 4: Batch Transformation

```python
class BatchTransformer:
    def __init__(self, transformer, db):
        self.transformer = transformer
        self.db = db

    def transform_batch(self, input_file, input_format, output_format):
        """Transform batch of records"""
        results = []
        errors = []

        with open(input_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    # Parse input
                    if input_format == 'hl7':
                        data = self.parse_hl7(line)
                    elif input_format == 'json':
                        data = json.loads(line)

                    # Transform
                    result = self.transformer.transform(data, input_format, output_format)
                    results.append(result)

                    # Store in database
                    self.db.save_transformed(result)

                except Exception as e:
                    errors.append({
                        'line': line_num,
                        'error': str(e)
                    })

        return {
            'processed': len(results),
            'errors': len(errors),
            'results': results,
            'errors_detail': errors
        }

    def parse_hl7(self, line):
        """Parse HL7 message"""
        import hl7
        return hl7.parse(line)
```

## Step 5: Validation During Transformation

```python
class ValidatingTransformer:
    def __init__(self, transformer, validator):
        self.transformer = transformer
        self.validator = validator

    def transform_and_validate(self, source_data):
        """Transform and validate output"""
        # Transform
        fhir_resource = self.transformer.transform_patient(source_data)

        # Validate
        is_valid, errors = self.validator.validate_fhir(fhir_resource)

        if not is_valid:
            raise ValueError(f"Validation failed: {errors}")

        return fhir_resource
```

## Step 6: Testing Transformations

```python
import unittest

class TestDataTransformation(unittest.TestCase):
    def setUp(self):
        self.transformer = HL7ToFHIRTransformer()

    def test_patient_transformation(self):
        """Test HL7 to FHIR patient transformation"""
        hl7_pid = [
            'PID',
            '',
            '||12345^^^MRN',
            '||DOE^JOHN',
            '||19700101',
            '|M'
        ]

        fhir_patient = self.transformer.transform_patient(hl7_pid)

        self.assertEqual(fhir_patient['resourceType'], 'Patient')
        self.assertEqual(fhir_patient['identifier'][0]['value'], '12345')
        self.assertEqual(fhir_patient['name'][0]['family'], 'DOE')

    def test_observation_transformation(self):
        """Test HL7 to FHIR observation transformation"""
        hl7_obx = [
            'OBX',
            '1',
            'NM',
            '2345-7^Glucose',
            '',
            '95',
            'mg/dL'
        ]

        fhir_obs = self.transformer.transform_observation(hl7_obx, 'patient-123')

        self.assertEqual(fhir_obs['resourceType'], 'Observation')
        self.assertEqual(fhir_obs['valueQuantity']['value'], 95.0)

if __name__ == '__main__':
    unittest.main()
```

## Next Steps

1. Implement transformation for your specific message types
2. Test with real data samples
3. Set up error logging and monitoring
4. Create transformation documentation
5. Deploy to production environment

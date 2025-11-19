"""FHIR Integration for Medical Device Data Exchange"""
import json
from datetime import datetime
from typing import Dict

class FHIRObservationBuilder:
    """
    Build FHIR Observation resources per healthcare interoperability standard.
    
    Medical devices often integrate with EHR systems via FHIR APIs.
    Requirement: REQ-INTEROP-001 (Healthcare system integration)
    """
    
    @staticmethod
    def create_glucose_observation(
        patient_id: str,
        glucose_value: float,
        device_id: str,
        timestamp: str = None
    ) -> Dict:
        """
        Create FHIR Observation for glucose reading.
        
        Standard: FHIR R4 Observation Resource
        Test Case: TC-FHIR-001
        """
        
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        observation = {
            "resourceType": "Observation",
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "laboratory",
                            "display": "Laboratory"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "2345-7",
                        "display": "Glucose [Mass/volume] in Serum or Plasma"
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": timestamp,
            "issued": datetime.now().isoformat(),
            "performer": [
                {
                    "reference": f"Device/{device_id}"
                }
            ],
            "valueQuantity": {
                "value": glucose_value,
                "unit": "mg/dL",
                "system": "http://unitsofmeasure.org",
                "code": "mg/dL"
            },
            "referenceRange": [
                {
                    "low": {
                        "value": 70,
                        "unit": "mg/dL"
                    },
                    "high": {
                        "value": 100,
                        "unit": "mg/dL"
                    },
                    "type": {
                        "text": "Normal fasting"
                    }
                }
            ],
            "interpretation": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                            "code": "H" if glucose_value > 150 else "N",
                            "display": "High" if glucose_value > 150 else "Normal"
                        }
                    ]
                }
            ]
        }
        
        return observation
    
    @staticmethod
    def create_device_resource(device_id: str, device_name: str) -> Dict:
        """Create FHIR Device resource for glucose monitor"""
        
        return {
            "resourceType": "Device",
            "id": device_id,
            "identifier": [
                {
                    "system": "http://example.com/glucose-monitors",
                    "value": device_id
                }
            ],
            "status": "active",
            "type": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "366062009",
                        "display": "Glucose monitor"
                    }
                ]
            },
            "manufacturer": "Medical Device Corp",
            "modelNumber": "GlucoTrack-2.1",
            "serialNumber": f"SN-{device_id}",
            "deviceName": [
                {
                    "name": device_name,
                    "type": "user-friendly-name"
                }
            ],
            "version": [
                {
                    "type": {
                        "text": "software"
                    },
                    "value": "2.1.0"
                }
            ]
        }

class FHIRAPIClient:
    """
    Secure FHIR API client for EHR integration.
    
    Security Controls:
    - Require OAuth 2.0 authentication
    - Use TLS 1.2 or higher
    - Validate SSL certificates
    - Rate limiting
    """
    
    def __init__(self, base_url: str, auth_token: str):
        self.base_url = base_url
        self.auth_token = auth_token
    
    def submit_glucose_observation(
        self,
        patient_id: str,
        glucose_value: float,
        device_id: str
    ) -> bool:
        """
        Submit glucose reading to EHR via FHIR API.
        
        Requirement: REQ-INTEROP-001
        Test Case: TC-FHIR-002
        """
        
        # Build FHIR observation
        observation = FHIRObservationBuilder.create_glucose_observation(
            patient_id, glucose_value, device_id
        )
        
        # In production: Make HTTP POST request
        # POST /fhir/Observation
        # Headers: Authorization: Bearer {auth_token}
        #          Content-Type: application/fhir+json
        
        # Simulated response
        print(f"Submitted observation for patient {patient_id}")
        print(f"Glucose: {glucose_value} mg/dL")
        
        return True

# Example usage
def example_fhir_integration():
    # Create FHIR resources
    patient_id = "12345"
    device_id = "GLUCOSE-001"
    glucose_value = 145
    
    # Create observation
    observation = FHIRObservationBuilder.create_glucose_observation(
        patient_id, glucose_value, device_id
    )
    
    print("FHIR Observation:")
    print(json.dumps(observation, indent=2))
    
    # Create device
    device = FHIRObservationBuilder.create_device_resource(
        device_id, "Glucose Monitor v2.1"
    )
    
    print("\nFHIR Device:")
    print(json.dumps(device, indent=2))
    
    return observation, device

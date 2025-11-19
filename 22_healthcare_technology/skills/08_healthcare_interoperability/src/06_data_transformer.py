#!/usr/bin/env python3
"""Data Transformation Engine - HL7 to FHIR and vice versa"""

from typing import Dict, List, Optional
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HL7ToFHIRTransformer:
    """Transform HL7 v2.x messages to FHIR resources"""

    def transform_patient(self, hl7_pid_segment: List) -> Dict:
        """Transform HL7 PID to FHIR Patient"""
        return {
            "resourceType": "Patient",
            "identifier": self._extract_identifiers(hl7_pid_segment),
            "name": self._extract_names(hl7_pid_segment),
            "birthDate": self._parse_date(hl7_pid_segment[7] if len(hl7_pid_segment) > 7 else ''),
            "gender": self._map_gender(hl7_pid_segment[8][0][0] if len(hl7_pid_segment) > 8 and hl7_pid_segment[8] else 'U'),
            "address": self._extract_addresses(hl7_pid_segment),
            "telecom": self._extract_telecom(hl7_pid_segment)
        }

    def transform_observation(self, hl7_obx: List, patient_id: str) -> Dict:
        """Transform HL7 OBX to FHIR Observation"""
        return {
            "resourceType": "Observation",
            "status": "final",
            "code": self._extract_code(hl7_obx[3] if len(hl7_obx) > 3 else []),
            "subject": {"reference": f"Patient/{patient_id}"},
            "valueQuantity": self._extract_value(hl7_obx[5] if len(hl7_obx) > 5 else '', hl7_obx[6] if len(hl7_obx) > 6 else '')
        }

    def _extract_identifiers(self, hl7_pid: List) -> List[Dict]:
        """Extract identifiers from PID"""
        identifiers = []
        if len(hl7_pid) > 2 and hl7_pid[2]:
            identifiers.append({
                "system": "http://hospital/mrn",
                "value": hl7_pid[2][0][0]
            })
        return identifiers

    def _extract_names(self, hl7_pid: List) -> List[Dict]:
        """Extract names from PID"""
        names = []
        if len(hl7_pid) > 4 and hl7_pid[4]:
            name_field = hl7_pid[4][0]
            names.append({
                "family": name_field[0] if name_field else '',
                "given": name_field[1:] if len(name_field) > 1 else []
            })
        return names

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse HL7 date to ISO format"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
        except:
            return None

    def _map_gender(self, gender: str) -> str:
        """Map HL7 gender to FHIR"""
        mapping = {'M': 'male', 'F': 'female', 'O': 'other', 'U': 'unknown'}
        return mapping.get(gender, 'unknown')

    def _extract_addresses(self, hl7_pid: List) -> List[Dict]:
        """Extract addresses from PID"""
        addresses = []
        if len(hl7_pid) > 10 and hl7_pid[10]:
            addr = hl7_pid[10][0]
            addresses.append({
                "line": [addr[0]] if addr else [],
                "city": addr[2] if len(addr) > 2 else '',
                "state": addr[3] if len(addr) > 3 else '',
                "postalCode": addr[4] if len(addr) > 4 else ''
            })
        return addresses

    def _extract_telecom(self, hl7_pid: List) -> List[Dict]:
        """Extract phone/email from PID"""
        telecom = []
        if len(hl7_pid) > 12 and hl7_pid[12]:
            telecom.append({
                "system": "phone",
                "value": hl7_pid[12][0][0]
            })
        return telecom

    def _extract_code(self, code_field: List) -> Dict:
        """Extract code from OBX"""
        if not code_field or not code_field[0]:
            return {}
        code = code_field[0]
        return {
            "coding": [{
                "system": "http://loinc.org",
                "code": code[0] if code else '',
                "display": code[1] if len(code) > 1 else ''
            }]
        }

    def _extract_value(self, value: str, unit: str) -> Dict:
        """Extract value from OBX"""
        if not value:
            return {}
        try:
            return {
                "value": float(value),
                "unit": unit,
                "system": "http://unitsofmeasure.org"
            }
        except:
            return {"valueString": value}


if __name__ == '__main__':
    transformer = HL7ToFHIRTransformer()
    
    # Example HL7 PID segment
    pid = ['PID', '', '||12345^^^MRN', '||DOE^JOHN', '||19700101', '|M', '', '', '|123 MAIN ST^APT 4^CITY^STATE^12345', '', '5551234567']
    
    patient = transformer.transform_patient(pid)
    print(json.dumps(patient, indent=2))

"""
HL7 ORM Order Message Generator
Generates HL7 v2.x ORM^O01 messages for clinical orders
"""

from datetime import datetime
from typing import Dict, List, Optional


class HL7ORMGenerator:
    """Generate HL7 ORM (Order) messages"""

    def __init__(self):
        self.field_separator = '|'
        self.component_separator = '^'
        self.repetition_separator = '~'
        self.escape_character = '\\'
        self.subcomponent_separator = '&'

    def generate_msh(self, config: Dict) -> str:
        """Generate MSH (Message Header) segment"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        encoding = f"{self.component_separator}{self.repetition_separator}" \
                  f"{self.escape_character}{self.subcomponent_separator}"

        return self.field_separator.join([
            'MSH',
            encoding,
            config.get('sending_application', ''),
            config.get('sending_facility', ''),
            config.get('receiving_application', ''),
            config.get('receiving_facility', ''),
            timestamp,
            '',
            'ORM^O01',
            config.get('message_control_id', f'MSG{timestamp}'),
            config.get('processing_id', 'P'),
            config.get('version_id', '2.5.1')
        ])

    def generate_pid(self, patient: Dict) -> str:
        """Generate PID (Patient Identification) segment"""
        identifiers = []
        if patient.get('mrn'):
            identifiers.append(f"{patient['mrn']}^^^{patient.get('facility', '')}^MRN")
        if patient.get('ssn'):
            identifiers.append(f"{patient['ssn']}^^^SSN")

        patient_name = self.component_separator.join([
            patient.get('last_name', ''),
            patient.get('first_name', ''),
            patient.get('middle_name', ''),
            patient.get('suffix', ''),
            patient.get('prefix', '')
        ])

        address = self.component_separator.join([
            patient.get('address_line1', ''),
            patient.get('address_line2', ''),
            patient.get('city', ''),
            patient.get('state', ''),
            patient.get('zip', ''),
            patient.get('country', 'USA')
        ])

        return self.field_separator.join([
            'PID',
            '1',
            '',
            self.repetition_separator.join(identifiers),
            '',
            patient_name,
            patient.get('mothers_maiden_name', ''),
            patient.get('date_of_birth', ''),
            patient.get('gender', ''),
            '',
            patient.get('race', ''),
            address,
            '',
            patient.get('phone_home', ''),
            patient.get('phone_business', ''),
            patient.get('primary_language', ''),
            patient.get('marital_status', ''),
            patient.get('religion', ''),
            patient.get('account_number', ''),
            patient.get('ssn', '')
        ])

    def generate_pv1(self, visit: Dict) -> str:
        """Generate PV1 (Patient Visit) segment"""
        assigned_location = self.component_separator.join([
            visit.get('nursing_unit', ''),
            visit.get('room', ''),
            visit.get('bed', ''),
            visit.get('facility', '')
        ])

        attending_doctor = self.component_separator.join([
            visit.get('attending_doctor_id', ''),
            visit.get('attending_doctor_last_name', ''),
            visit.get('attending_doctor_first_name', ''),
            visit.get('attending_doctor_mi', ''),
            '',
            '',
            'MD'
        ])

        return self.field_separator.join([
            'PV1',
            '1',
            visit.get('patient_class', ''),
            assigned_location,
            visit.get('admission_type', ''),
            '',
            '',
            attending_doctor,
            '',
            visit.get('hospital_service', ''),
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            visit.get('visit_number', '')
        ] + [''] * 26 + [  # Fill remaining fields
            visit.get('admit_datetime', ''),
            visit.get('discharge_datetime', '')
        ])

    def generate_orc(self, order: Dict) -> str:
        """Generate ORC (Common Order) segment"""
        return self.field_separator.join([
            'ORC',
            order.get('order_control', 'NW'),  # NW=New Order
            order.get('placer_order_number', ''),
            order.get('filler_order_number', ''),
            '',
            order.get('order_status', ''),
            '',
            '',
            '',
            datetime.now().strftime('%Y%m%d%H%M%S'),  # Transaction date/time
            self.component_separator.join([
                order.get('ordering_provider_id', ''),
                order.get('ordering_provider_last_name', ''),
                order.get('ordering_provider_first_name', ''),
                '',
                '',
                '',
                'MD'
            ])
        ])

    def generate_obr(self, order: Dict) -> str:
        """Generate OBR (Observation Request) segment"""
        universal_service_id = self.component_separator.join([
            order.get('test_code', ''),
            order.get('test_name', ''),
            order.get('coding_system', 'LN')  # LOINC
        ])

        return self.field_separator.join([
            'OBR',
            '1',
            order.get('placer_order_number', ''),
            order.get('filler_order_number', ''),
            universal_service_id,
            order.get('priority', ''),
            order.get('requested_datetime', ''),
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            self.component_separator.join([
                order.get('ordering_provider_id', ''),
                order.get('ordering_provider_last_name', ''),
                order.get('ordering_provider_first_name', '')
            ]),
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            order.get('order_effective_datetime', ''),
            '',
            '',
            order.get('clinical_indication', '')
        ])

    def generate_order_message(self, config: Dict, patient: Dict,
                               visit: Dict, order: Dict) -> str:
        """Generate complete ORM^O01 message"""
        segments = [
            self.generate_msh(config),
            self.generate_pid(patient),
            self.generate_pv1(visit),
            self.generate_orc(order),
            self.generate_obr(order)
        ]

        return '\r'.join(segments)


# Example usage
if __name__ == '__main__':
    generator = HL7ORMGenerator()

    # Configuration
    config = {
        'sending_application': 'EMR_SYSTEM',
        'sending_facility': 'MAIN_HOSPITAL',
        'receiving_application': 'LAB_SYSTEM',
        'receiving_facility': 'LAB_FACILITY',
        'message_control_id': 'MSG00001',
        'processing_id': 'P',
        'version_id': '2.5.1'
    }

    # Patient demographics
    patient = {
        'mrn': 'MRN123456',
        'facility': 'FACILITY',
        'ssn': '987654321',
        'last_name': 'DOE',
        'first_name': 'JOHN',
        'middle_name': 'ROBERT',
        'suffix': 'JR',
        'prefix': 'MR',
        'date_of_birth': '19800115',
        'gender': 'M',
        'race': 'W^White',
        'address_line1': '123 MAIN ST',
        'city': 'ANYTOWN',
        'state': 'CA',
        'zip': '12345',
        'phone_home': '(555)555-1234'
    }

    # Visit information
    visit = {
        'patient_class': 'I',
        'nursing_unit': '3N',
        'room': '301',
        'bed': '01',
        'facility': 'MAIN_HOSPITAL',
        'attending_doctor_id': '123456',
        'attending_doctor_last_name': 'SMITH',
        'attending_doctor_first_name': 'JOHN',
        'hospital_service': 'MED',
        'visit_number': 'V123456789',
        'admit_datetime': '20231119120000'
    }

    # Order details
    order = {
        'order_control': 'NW',
        'placer_order_number': 'ORD123456',
        'test_code': '2339-0',
        'test_name': 'Glucose',
        'coding_system': 'LN',
        'priority': 'R',  # Routine
        'requested_datetime': '20231119130000',
        'ordering_provider_id': '123456',
        'ordering_provider_last_name': 'SMITH',
        'ordering_provider_first_name': 'JOHN',
        'order_effective_datetime': '20231119130000',
        'clinical_indication': 'Diabetes monitoring'
    }

    # Generate message
    message = generator.generate_order_message(config, patient, visit, order)

    print("Generated ORM Message:")
    print(message)
    print("\n" + "="*80)
    print("Message segments:")
    for segment in message.split('\r'):
        print(segment)

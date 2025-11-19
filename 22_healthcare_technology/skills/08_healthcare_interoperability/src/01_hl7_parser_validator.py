#!/usr/bin/env python3
"""
HL7 v2.x Message Parser and Validator
Production-grade implementation for parsing and validating HL7 messages
"""

import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class HL7Parser:
    """Parse HL7 v2.x messages into structured data"""

    FIELD_SEP = '|'
    COMPONENT_SEP = '^'
    REPETITION_SEP = '~'
    ESCAPE_CHAR = '\\'
    SUBCOMPONENT_SEP = '&'

    def __init__(self):
        self.segments = []
        self.message_type = None
        self.sender = None
        self.receiver = None

    def parse(self, hl7_string: str) -> Dict:
        """Parse HL7 message string"""
        try:
            # Split into segments
            segment_strings = hl7_string.strip().split('\r')

            if not segment_strings:
                raise ValueError("Empty message")

            self.segments = []

            for segment_str in segment_strings:
                if not segment_str:
                    continue

                # Split fields
                fields = segment_str.split(self.FIELD_SEP)
                segment_type = fields[0]

                # Parse fields with components
                parsed_fields = []
                for field in fields:
                    parsed_field = self.parse_field(field)
                    parsed_fields.append(parsed_field)

                self.segments.append({
                    'type': segment_type,
                    'fields': parsed_fields,
                    'raw': segment_str
                })

            # Extract metadata
            if self.segments and self.segments[0]['type'] == 'MSH':
                self.extract_metadata()

            return {
                'segments': self.segments,
                'message_type': self.message_type,
                'sender': self.sender,
                'receiver': self.receiver
            }

        except Exception as e:
            logger.error(f"Parse error: {e}")
            raise

    def parse_field(self, field: str) -> List:
        """Parse field into components"""
        if not field:
            return []

        components = field.split(self.COMPONENT_SEP)
        parsed_components = []

        for component in components:
            subcomponents = component.split(self.SUBCOMPONENT_SEP)
            parsed_components.append(subcomponents)

        return parsed_components

    def extract_metadata(self):
        """Extract message metadata from MSH"""
        msh = self.segments[0]

        # Message type (field 8)
        if len(msh['fields']) > 8:
            msg_type_field = msh['fields'][8]
            if msg_type_field and msg_type_field[0]:
                self.message_type = msg_type_field[0][0]

        # Sending application (field 2)
        if len(msh['fields']) > 2:
            self.sender = msh['fields'][2][0][0] if msh['fields'][2] and msh['fields'][2][0] else None

        # Receiving application (field 4)
        if len(msh['fields']) > 4:
            self.receiver = msh['fields'][4][0][0] if msh['fields'][4] and msh['fields'][4][0] else None


class HL7Validator:
    """Validate HL7 messages against rules"""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate(self, parsed_message: Dict) -> Tuple[bool, List, List]:
        """Validate parsed message"""
        self.errors = []
        self.warnings = []

        # Check basic structure
        self._validate_structure(parsed_message)

        # Check segments
        self._validate_segments(parsed_message['segments'])

        # Check fields
        self._validate_fields(parsed_message['segments'])

        return len(self.errors) == 0, self.errors, self.warnings

    def _validate_structure(self, message: Dict):
        """Validate message structure"""
        if not message['segments']:
            self.errors.append("No segments found")
            return

        # First segment must be MSH
        if message['segments'][0]['type'] != 'MSH':
            self.errors.append("First segment must be MSH")

        # Message type required
        if not message['message_type']:
            self.errors.append("Message type not found")

    def _validate_segments(self, segments: List):
        """Validate segment structure"""
        segment_counts = {}

        for segment in segments:
            seg_type = segment['type']
            segment_counts[seg_type] = segment_counts.get(seg_type, 0) + 1

        # Check cardinality
        required_segments = {'MSH': 1}
        for seg_type, count in required_segments.items():
            if seg_type not in segment_counts:
                self.errors.append(f"Required segment {seg_type} not found")

        # Only one MSH and PID
        for seg_type in ['MSH', 'PID']:
            if segment_counts.get(seg_type, 0) > 1:
                self.warnings.append(f"Multiple {seg_type} segments found")

    def _validate_fields(self, segments: List):
        """Validate field contents"""
        for segment in segments:
            if segment['type'] == 'PID':
                self._validate_pid(segment)
            elif segment['type'] == 'OBX':
                self._validate_obx(segment)
            elif segment['type'] == 'MSH':
                self._validate_msh(segment)

    def _validate_msh(self, segment: Dict):
        """Validate MSH segment"""
        fields = segment['fields']

        # Version (field 11)
        if len(fields) > 11:
            version = fields[11][0][0] if fields[11] and fields[11][0] else None
            if version and not version.startswith('2.'):
                self.warnings.append(f"Unusual HL7 version: {version}")

    def _validate_pid(self, segment: Dict):
        """Validate PID segment"""
        fields = segment['fields']

        # MRN (field 2)
        if len(fields) > 2 and fields[2]:
            mrn = fields[2][0][0] if fields[2][0] else None
            if mrn:
                if not (5 <= len(mrn) <= 20):
                    self.errors.append(f"MRN length invalid: {len(mrn)}")

        # DOB (field 7)
        if len(fields) > 7 and fields[7]:
            dob = fields[7][0][0] if fields[7] and fields[7][0] else None
            if dob and not self._is_valid_date(dob):
                self.errors.append(f"Invalid DOB format: {dob}")

        # Gender (field 8)
        if len(fields) > 8 and fields[8]:
            gender = fields[8][0][0] if fields[8] and fields[8][0] else None
            if gender and gender not in ['M', 'F', 'U', 'O']:
                self.errors.append(f"Invalid gender: {gender}")

    def _validate_obx(self, segment: Dict):
        """Validate OBX segment"""
        fields = segment['fields']

        # Value type (field 2)
        if len(fields) > 2 and fields[2]:
            value_type = fields[2][0][0] if fields[2] and fields[2][0] else None
            valid_types = ['NM', 'ST', 'CE', 'TM', 'DT', 'NR', 'SN']
            if value_type and value_type not in valid_types:
                self.errors.append(f"Invalid value type: {value_type}")

        # Value (field 5)
        if len(fields) > 5 and fields[5]:
            value = fields[5][0][0] if fields[5] and fields[5][0] else None
            if not value:
                self.warnings.append("OBX value is empty")

    def _is_valid_date(self, date_str: str) -> bool:
        """Check if date is valid YYYYMMDD or YYYY-MM-DD"""
        try:
            if len(date_str) == 8 and date_str.isdigit():
                datetime.strptime(date_str, "%Y%m%d")
                return True
            elif len(date_str) == 10 and '-' in date_str:
                datetime.strptime(date_str, "%Y-%m-%d")
                return True
        except ValueError:
            pass
        return False


if __name__ == '__main__':
    # Example usage
    hl7_message = """MSH|^~\\&|SENDING_APP|SENDING_FAC|RECEIVING_APP|RECEIVING_FAC|20231119120000||ADT^A01|MSG001|P|2.5.1
PID|||12345^^^MRN||DOE^JOHN||19700101|M||C|123 MAIN ST^APT 4^CITY^STATE^12345^USA
PV1||I|^ROOM-123^BED-A||^^^DR. SMITH|||O"""

    parser = HL7Parser()
    parsed = parser.parse(hl7_message)

    validator = HL7Validator()
    is_valid, errors, warnings = validator.validate(parsed)

    print(f"Valid: {is_valid}")
    print(f"Errors: {errors}")
    print(f"Warnings: {warnings}")
    print(f"Message Type: {parsed['message_type']}")
    print(f"Segments: {len(parsed['segments'])}")

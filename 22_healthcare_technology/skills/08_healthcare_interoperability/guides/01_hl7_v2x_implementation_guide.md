# HL7 v2.x Implementation Guide

## Getting Started with HL7 v2.x

### Step 1: Install HL7 Parser Library

#### Python
```bash
pip install python-hl7
pip install hl7apy
```

#### Java
```xml
<dependency>
    <groupId>ca.uhn.hapi</groupId>
    <artifactId>hapi-structures-v25</artifactId>
    <version>2.5.1</version>
</dependency>
```

#### Node.js
```bash
npm install hl7-client
npm install hl7-processor
```

### Step 2: Parse Your First HL7 Message

#### Python Example
```python
import hl7

# Create HL7 message
msg_string = """MSH|^~\\&|SENDING_APP|SENDING_FAC|RECEIVING_APP|RECEIVING_FAC|20231119120000||ADT^A01|MSG001|P|2.5.1
PID|||12345^^^MRN||DOE^JOHN||19700101|M||C|123 MAIN ST^APT 4^CITY^STATE^12345^USA
PV1||I|^ROOM-123^BED-A||^^^DR. SMITH|
"""

# Parse message
message = hl7.parse(msg_string)

# Access fields
print(f"Sender: {message[2][0]}")  # SENDING_APP
print(f"Patient MRN: {message[3][2][0]}")  # 12345
print(f"Patient Name: {message[3][4][0]}")  # DOE^JOHN

# Iterate segments
for segment in message:
    print(f"Segment Type: {segment[0][0]}")
```

#### Java Example (HAPI)
```java
Parser parser = new DefaultXMLParser();
PipeParser pipeParser = new PipeParser();

String msgString = "MSH|^~\\&|SENDING_APP|SENDING_FAC|...";
Message message = pipeParser.parse(msgString);

// Access fields
MSH msh = (MSH) message.get("MSH");
String sendingApp = msh.getSendingApplication().getNamespaceID().getValue();

PID pid = (PID) message.get("PID");
String mrn = pid.getPatientIdentifierList(0).getIDNumber().getValue();
```

## Real-World ADT Implementation

### Step 3: Build ADT Message Handler

```python
class ADTMessageHandler:
    def __init__(self, db_connection):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)

    def handle_admission(self, hl7_message):
        """Handle ADT^A01 - Patient Admission"""
        try:
            # Parse message
            parsed = hl7.parse(hl7_message)

            # Extract patient info
            patient_data = self.extract_patient_info(parsed)
            visit_data = self.extract_visit_info(parsed)

            # Validate
            self.validate_patient_data(patient_data)

            # Store in database
            patient_id = self.db.insert_patient(patient_data)
            visit_id = self.db.insert_visit(visit_id, visit_data)

            # Generate ACK
            ack = self.generate_ack("AA", "Patient admission successful")

            self.logger.info(f"Admission processed: Patient {patient_id}")
            return ack

        except ValidationError as e:
            self.logger.error(f"Validation error: {e}")
            return self.generate_ack("AE", str(e))

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return self.generate_ack("AR", "System error")

    def extract_patient_info(self, message):
        """Extract patient demographics from PID segment"""
        pid = message.segment('PID')
        return {
            'mrn': pid[2][0][0],  # Patient ID
            'family_name': pid[4][0][0],  # Name - family
            'given_name': pid[4][0][1],  # Name - given
            'dob': pid[7],
            'gender': pid[8],
            'address': pid[10][0] if pid[10] else None,
            'phone': pid[12][0] if pid[12] else None,
        }

    def extract_visit_info(self, message):
        """Extract visit information from PV1 segment"""
        pv1 = message.segment('PV1')
        return {
            'visit_type': pv1[1],  # Inpatient/Outpatient
            'bed': pv1[2],  # Bed assignment
            'location': pv1[3] if pv1[3] else None,
            'attending_provider': pv1[6] if pv1[6] else None,
            'discharge_disposition': pv1[36],
            'discharge_location': pv1[37],
        }

    def generate_ack(self, code, text):
        """Generate HL7 ACK message"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        ack = f"""MSH|^~\\&|RECEIVING_APP|RECEIVING_FAC|SENDING_APP|SENDING_FAC|{timestamp}||ACK^A01|{uuid.uuid4()}|P|2.5.1
MSA|{code}|MSG001|{text}
"""
        return ack
```

## Step 4: MLLP Connection Handler

```python
import socket
import struct

MLLP_START = b'\x0b'
MLLP_END = b'\x1c\x0d'

class MLLPClient:
    def __init__(self, host, port, timeout=30):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None

    def connect(self):
        """Establish MLLP connection"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        self.socket.connect((self.host, self.port))
        print(f"Connected to {self.host}:{self.port}")

    def send_message(self, hl7_msg):
        """Send HL7 message with MLLP framing"""
        # Add MLLP frame
        framed_msg = MLLP_START + hl7_msg.encode() + MLLP_END

        try:
            # Send message
            self.socket.sendall(framed_msg)
            print("Message sent")

            # Receive ACK
            ack = self.receive_message()
            return ack

        except socket.timeout:
            print("Timeout waiting for ACK")
            return None

    def receive_message(self):
        """Receive HL7 message with MLLP framing"""
        data = b''

        # Read until MLLP_END
        while True:
            chunk = self.socket.recv(1024)
            if not chunk:
                break

            data += chunk

            if MLLP_END in data:
                # Extract message (remove MLLP frame)
                msg = data.split(MLLP_START)[1].split(MLLP_END)[0].decode()
                return msg

        return None

    def close(self):
        """Close connection"""
        if self.socket:
            self.socket.close()
            print("Connection closed")

# Usage
client = MLLPClient('ehr-server.example.com', 2575)
client.connect()

hl7_msg = "MSH|^~\\&|APP|FAC|...\nPID|..."
ack = client.send_message(hl7_msg)

if ack and 'AA' in ack:
    print("Message accepted")
else:
    print("Message rejected")

client.close()
```

## Step 5: Message Validation

```python
class HL7Validator:
    def __init__(self):
        self.errors = []

    def validate_message(self, hl7_msg):
        """Complete message validation"""
        self.errors = []

        try:
            parsed = hl7.parse(hl7_msg)

            # Validate segments
            self.validate_segments(parsed)

            # Validate fields
            self.validate_fields(parsed)

            # Validate identifiers
            self.validate_identifiers(parsed)

            return len(self.errors) == 0

        except Exception as e:
            self.errors.append(f"Parse error: {str(e)}")
            return False

    def validate_segments(self, message):
        """Check segment structure"""
        # First segment must be MSH
        if message[0][0][0] != "MSH":
            self.errors.append("First segment must be MSH")

        # Count segments
        expected_segments = {'MSH': 1, 'PID': 1, 'PV1': (0, 1), 'OBX': (0, None)}

        for segment_type in expected_segments:
            count = len([s for s in message if s[0][0] == segment_type])
            expected = expected_segments[segment_type]

            if isinstance(expected, tuple):
                if not (expected[0] <= count <= (expected[1] or float('inf'))):
                    self.errors.append(f"{segment_type} count {count} invalid")
            elif count != expected:
                self.errors.append(f"{segment_type} count {count}, expected {expected}")

    def validate_fields(self, message):
        """Validate field contents"""
        pid = message.segment('PID')

        # MRN format
        mrn = pid[2][0][0]
        if not (5 <= len(mrn) <= 10) or not mrn.isalnum():
            self.errors.append(f"Invalid MRN format: {mrn}")

        # DOB format
        dob = pid[7]
        if not self.is_valid_date(dob):
            self.errors.append(f"Invalid DOB: {dob}")

        # Gender
        gender = pid[8]
        if gender not in ['M', 'F', 'U', 'O']:
            self.errors.append(f"Invalid gender: {gender}")

    def validate_identifiers(self, message):
        """Check identifier uniqueness and format"""
        # Get all identifiers
        identifiers = {}

        pid = message.segment('PID')
        mrn = pid[2][0][0]

        if mrn in identifiers:
            self.errors.append(f"Duplicate MRN: {mrn}")
        identifiers[mrn] = True

    def is_valid_date(self, date_str):
        """Validate YYYYMMDD format"""
        try:
            if len(date_str) != 8:
                return False
            datetime.strptime(date_str, "%Y%m%d")
            return True
        except:
            return False

    def get_errors(self):
        """Get validation errors"""
        return self.errors

# Usage
validator = HL7Validator()
hl7_msg = "MSH|^~\\&|...\nPID|..."

if validator.validate_message(hl7_msg):
    print("Message valid")
else:
    for error in validator.get_errors():
        print(f"Error: {error}")
```

## Step 6: Error Handling & Retry Logic

```python
class HL7ProcessingEngine:
    def __init__(self, db, logger):
        self.db = db
        self.logger = logger
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    def process_message(self, hl7_msg):
        """Process with retry logic"""
        for attempt in range(1, self.max_retries + 1):
            try:
                # Validate
                if not self.validate(hl7_msg):
                    return "AE", "Validation failed"

                # Parse
                parsed = hl7.parse(hl7_msg)

                # Process
                self.db.begin_transaction()
                result = self.handle_message(parsed)
                self.db.commit()

                self.logger.info(f"Message processed successfully")
                return "AA", "Success"

            except DatabaseError as e:
                self.db.rollback()

                if attempt < self.max_retries:
                    self.logger.warning(f"Attempt {attempt} failed: {e}, retrying...")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    self.logger.error(f"Failed after {self.max_retries} attempts: {e}")
                    return "AR", "Database error"

            except ValidationError as e:
                self.logger.error(f"Validation error: {e}")
                return "AE", str(e)

            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                return "AR", "System error"

        return "AR", "Processing failed"

    def validate(self, msg):
        validator = HL7Validator()
        return validator.validate_message(msg)

    def handle_message(self, parsed):
        msg_type = parsed[0][8][0]  # Message type

        if msg_type == 'ADT':
            return self.handle_adt(parsed)
        elif msg_type == 'ORU':
            return self.handle_results(parsed)
        elif msg_type == 'ORM':
            return self.handle_order(parsed)
        else:
            raise ValueError(f"Unknown message type: {msg_type}")

# Usage
engine = HL7ProcessingEngine(db, logger)
code, message = engine.process_message(hl7_msg)

if code == "AA":
    print("Success")
else:
    print(f"Error: {message}")
```

## Testing Your HL7 Implementation

```python
import unittest

class TestHL7Implementation(unittest.TestCase):
    def setUp(self):
        self.handler = ADTMessageHandler(MockDB())
        self.validator = HL7Validator()

    def test_valid_admission_message(self):
        """Test valid admission message"""
        hl7_msg = """MSH|^~\\&|SENDING_APP|FAC|RECEIVING_APP|FAC|20231119120000||ADT^A01|MSG001|P|2.5.1
PID|||12345^^^MRN||DOE^JOHN||19700101|M"""

        result = self.validator.validate_message(hl7_msg)
        self.assertTrue(result)

    def test_invalid_date_format(self):
        """Test invalid date format"""
        hl7_msg = """MSH|^~\\&|SENDING_APP|FAC|RECEIVING_APP|FAC|20231119120000||ADT^A01|MSG001|P|2.5.1
PID|||12345^^^MRN||DOE^JOHN||INVALID|M"""

        result = self.validator.validate_message(hl7_msg)
        self.assertFalse(result)

    def test_missing_required_field(self):
        """Test missing required field"""
        hl7_msg = """MSH|^~\\&|SENDING_APP|FAC|RECEIVING_APP|FAC|20231119120000||ADT^A01|MSG001|P|2.5.1
PID"""

        result = self.validator.validate_message(hl7_msg)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
```

## Next Steps

1. Set up MLLP connection to your healthcare system
2. Implement message handlers for your specific workflows
3. Build comprehensive validation rules
4. Test with real message samples
5. Deploy to production with proper monitoring

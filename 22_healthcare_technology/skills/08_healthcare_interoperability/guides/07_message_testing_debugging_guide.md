# Message Testing & Debugging Guide

## Step 1: Set Up Testing Environment

### Docker Compose for Testing
```yaml
version: '3.8'

services:
  hl7-server:
    image: hl7server:latest
    ports:
      - "2575:2575"
    environment:
      MLLP_PORT: 2575

  fhir-server:
    image: hapiproject/hapi:latest
    ports:
      - "8080:8080"
    environment:
      HAPI_FHIR_VERSION: R4

  test-harness:
    build: ./test-harness
    ports:
      - "3000:3000"
    depends_on:
      - hl7-server
      - fhir-server

  postgres:
    image: postgres:13
    environment:
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
```

## Step 2: HL7 Message Testing

### Generate Test Messages
```python
import hl7
from datetime import datetime

class TestMessageGenerator:
    @staticmethod
    def generate_admit_message():
        """Generate valid admission message"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        message = (
            f"MSH|^~\\&|SENDING_APP|SENDING_FAC|RECEIVING_APP|RECEIVING_FAC|{timestamp}||ADT^A01|MSG001|P|2.5.1\r"
            f"PID|||12345^^^MRN||DOE^JOHN||19700101|M||C|123 MAIN ST^APT 4^CITY^STATE^12345^USA\r"
            f"PV1||I|^ROOM-123^BED-A||^^^DR. SMITH|||O\r"
        )

        return message

    @staticmethod
    def generate_lab_order_message():
        """Generate lab order message"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        message = (
            f"MSH|^~\\&|LAB_SYSTEM|LAB|EHR|HOSPITAL|{timestamp}||ORM^O01|MSG002|P|2.5.1\r"
            f"PID|||12345^^^MRN||DOE^JOHN||19700101|M\r"
            f"ORC|NW|LAB123|LAB123|||||||||DR. SMITH\r"
            f"OBR|1|LAB123|LAB123|2345-7^Glucose|||{timestamp}|||C\r"
        )

        return message

    @staticmethod
    def generate_lab_result_message():
        """Generate lab result message"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        message = (
            f"MSH|^~\\&|LAB_SYSTEM|LAB|EHR|HOSPITAL|{timestamp}||ORU^R01|MSG003|P|2.5.1\r"
            f"PID|||12345^^^MRN||DOE^JOHN||19700101|M\r"
            f"OBX|1|NM|2345-7^Glucose||95|mg/dL|70-100|N|||F\r"
            f"OBX|2|NM|2951-2^Sodium||140|mEq/L|136-145|N|||F\r"
        )

        return message

# Usage
generator = TestMessageGenerator()
admit_msg = generator.generate_admit_message()
print(admit_msg)
```

### Test Message Validation
```python
import unittest
from hl7validator import HL7Validator

class TestHL7Messages(unittest.TestCase):
    def setUp(self):
        self.validator = HL7Validator()
        self.generator = TestMessageGenerator()

    def test_valid_admit_message(self):
        """Test valid admission message"""
        msg = self.generator.generate_admit_message()
        result = self.validator.validate_message(msg)
        self.assertTrue(result)

    def test_missing_required_field(self):
        """Test message with missing required field"""
        msg = (
            "MSH|^~\\&|SENDING_APP|SENDING_FAC|RECEIVING_APP|RECEIVING_FAC|20231119120000||ADT^A01|MSG001|P|2.5.1\r"
            "PID"  # Missing all fields
        )
        result = self.validator.validate_message(msg)
        self.assertFalse(result)

    def test_invalid_date_format(self):
        """Test message with invalid date"""
        msg = (
            "MSH|^~\\&|SENDING_APP|SENDING_FAC|RECEIVING_APP|RECEIVING_FAC|20231119120000||ADT^A01|MSG001|P|2.5.1\r"
            "PID|||12345^^^MRN||DOE^JOHN||INVALID|M"
        )
        result = self.validator.validate_message(msg)
        self.assertFalse(result)

    def test_special_characters(self):
        """Test message with special characters"""
        msg = (
            "MSH|^~\\&|SENDING_APP|SENDING_FAC|RECEIVING_APP|RECEIVING_FAC|20231119120000||ADT^A01|MSG001|P|2.5.1\r"
            "PID|||12345^^^MRN||DOE\\F\\JANE^JOHN||19700101|M"  # Escaped pipe
        )
        result = self.validator.validate_message(msg)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
```

## Step 3: MLLP Testing

### Test MLLP Connection
```python
import socket
import time

class MLLPTestClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        """Connect to MLLP server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        self.socket.connect((self.host, self.port))
        print(f"Connected to {self.host}:{self.port}")

    def send_and_receive(self, message):
        """Send message and receive ACK"""
        MLLP_START = b'\x0b'
        MLLP_END = b'\x1c\x0d'

        try:
            # Send
            framed = MLLP_START + message.encode() + MLLP_END
            self.socket.sendall(framed)
            print("Message sent")

            # Receive
            response = b''
            while True:
                chunk = self.socket.recv(1024)
                if not chunk:
                    break
                response += chunk

                if MLLP_END in response:
                    msg = response.split(MLLP_START)[1].split(MLLP_END)[0].decode()
                    return msg

            return None

        except socket.timeout:
            print("Timeout waiting for response")
            return None

    def close(self):
        if self.socket:
            self.socket.close()

# Test
client = MLLPTestClient('localhost', 2575)
client.connect()

msg = TestMessageGenerator.generate_admit_message()
ack = client.send_and_receive(msg)

if ack and 'AA' in ack:
    print("✓ Message accepted")
else:
    print("✗ Message rejected")
    print(ack)

client.close()
```

## Step 4: FHIR API Testing

### API Test Suite
```python
import unittest
import requests
import json

class TestFHIRAPI(unittest.TestCase):
    BASE_URL = "http://localhost:8080/fhir"
    HEADERS = {"Accept": "application/fhir+json"}

    def test_create_patient(self):
        """Test POST /Patient"""
        patient = {
            "resourceType": "Patient",
            "name": [{"family": "Doe", "given": ["John"]}],
            "birthDate": "1970-01-01"
        }

        response = requests.post(
            f"{self.BASE_URL}/Patient",
            json=patient,
            headers=self.HEADERS
        )

        self.assertEqual(response.status_code, 201)
        result = response.json()
        self.assertIn('id', result)
        self.patient_id = result['id']

    def test_read_patient(self):
        """Test GET /Patient/[id]"""
        response = requests.get(
            f"{self.BASE_URL}/Patient/{self.patient_id}",
            headers=self.HEADERS
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['name'][0]['family'], 'Doe')

    def test_search_patient(self):
        """Test GET /Patient?search=criteria"""
        response = requests.get(
            f"{self.BASE_URL}/Patient?family=Doe",
            headers=self.HEADERS
        )

        self.assertEqual(response.status_code, 200)
        bundle = response.json()
        self.assertEqual(bundle['resourceType'], 'Bundle')

    def test_update_patient(self):
        """Test PUT /Patient/[id]"""
        patient = {
            "resourceType": "Patient",
            "id": self.patient_id,
            "name": [{"family": "Smith", "given": ["John"]}],
            "birthDate": "1970-01-01"
        }

        response = requests.put(
            f"{self.BASE_URL}/Patient/{self.patient_id}",
            json=patient,
            headers=self.HEADERS
        )

        self.assertEqual(response.status_code, 200)

    def test_invalid_request(self):
        """Test error handling"""
        response = requests.get(
            f"{self.BASE_URL}/Patient/invalid-id",
            headers=self.HEADERS
        )

        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
```

## Step 5: Load Testing

### Stress Testing with JMeter
```python
class LoadTester:
    def __init__(self, target_url, num_threads, duration_seconds):
        self.target_url = target_url
        self.num_threads = num_threads
        self.duration = duration_seconds
        self.results = []

    def generate_jmeter_config(self):
        """Generate JMeter test plan XML"""
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2">
  <hashTree>
    <ThreadGroup guiclass="ThreadGroupGui">
      <elementProp name="ThreadGroup.main_controller">
        <objProp>
          <stringProp name="ThreadGroup.num_threads">{self.num_threads}</stringProp>
          <stringProp name="ThreadGroup.ramp_time">10</stringProp>
          <stringProp name="ThreadGroup.duration">{self.duration}</stringProp>
        </objProp>
      </elementProp>
    </ThreadGroup>
    <HTTPSamplerProxy guiclass="HttpTestSampleGui">
      <elementProp name="HTTPsampler.Arguments">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="HTTPSampler.domain">{self.target_url}</stringProp>
      <stringProp name="HTTPSampler.port">8080</stringProp>
      <stringProp name="HTTPSampler.protocol">http</stringProp>
      <stringProp name="HTTPSampler.path">/fhir/Patient</stringProp>
      <stringProp name="HTTPSampler.method">GET</stringProp>
    </HTTPSamplerProxy>
  </hashTree>
</jmeterTestPlan>"""
        return xml

    def run_load_test(self):
        """Run load test with Python"""
        import concurrent.futures
        import time

        start_time = time.time()
        successful = 0
        failed = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = []

            while time.time() - start_time < self.duration:
                future = executor.submit(self.make_request)
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                try:
                    if future.result():
                        successful += 1
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1

        return {
            'total_requests': successful + failed,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / (successful + failed) * 100
        }

    def make_request(self):
        """Make single API request"""
        try:
            response = requests.get(
                f"{self.target_url}/fhir/Patient",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

# Usage
tester = LoadTester('http://localhost:8080', num_threads=10, duration_seconds=60)
results = tester.run_load_test()
print(f"Success rate: {results['success_rate']:.2f}%")
```

## Step 6: Debug Logging

### Comprehensive Logging
```python
import logging
from logging.handlers import RotatingFileHandler

class HealthcareIntegrationLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = RotatingFileHandler(
            'healthcare_integration.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )

        # Console handler
        console_handler = logging.StreamHandler()

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log_message(self, direction, message, error=None):
        """Log HL7 message"""
        self.logger.info(f"[{direction}] {message[:100]}...")
        if error:
            self.logger.error(f"Error: {error}")

    def log_transformation(self, source, target, success):
        """Log transformation"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"Transform {source} → {target}: {status}")

    def log_api_call(self, method, url, status_code):
        """Log API call"""
        self.logger.info(f"{method} {url} → {status_code}")

# Usage
logger = HealthcareIntegrationLogger(__name__)
logger.log_message("RECV", hl7_message)
logger.log_transformation("HL7", "FHIR", True)
logger.log_api_call("GET", "/fhir/Patient/123", 200)
```

## Next Steps

1. Set up testing environment
2. Create test message library
3. Implement automated test suite
4. Configure load testing
5. Deploy monitoring and logging

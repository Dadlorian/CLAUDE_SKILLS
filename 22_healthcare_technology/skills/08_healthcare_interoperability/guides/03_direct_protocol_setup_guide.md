# Direct Protocol Setup & Implementation Guide

## Step 1: Select a Direct Host Service Provider (HISP)

### Top HISP Providers
1. **Veradigm** - Comprehensive healthcare IT platform
2. **Surescripts** - Pharmacy and prescribing integration
3. **DirectLabs** - Specialized Direct services
4. **Lightwell** - Full Direct platform
5. **Practice Fusion** - EHR with Direct integration

### HISP Selection Criteria Checklist
- [ ] HIPAA compliance and SOC 2 certification
- [ ] 99.9% uptime SLA
- [ ] Support for SMTP/POP3/IMAP protocols
- [ ] REST API for programmatic access
- [ ] Certificate management support
- [ ] Audit logging and reporting
- [ ] 24/7 technical support
- [ ] Reasonable pricing model

## Step 2: Register Direct Address

### Process
1. **Apply for Direct Account**
   - Contact HISP provider
   - Provide organization information
   - Verify healthcare provider status (NPI number)
   - Sign HISP agreement

2. **Configure Direct Address**
   - Choose domain name
   - Set up MX records
   - Complete HISP validation

3. **Get Certificate**
   - Request X.509 certificate
   - Receive from Certificate Authority
   - Install in email client/system

### Example: Registering with Veradigm
```
1. Visit Veradigm Direct portal
2. Sign up as healthcare provider
3. Verify NPI (National Provider Identifier)
4. Configure direct@mypractice.com
5. Install certificate in Outlook
6. Test with sample message
```

## Step 3: Client Configuration

### Outlook Setup
1. **Install Direct Plugin**
   - Download from HISP website
   - Install plugin to Outlook

2. **Configure Account**
   ```
   Direct Address: provider@hospital.direct
   Password: [From HISP]
   Server: direct-smtp.hisp.com
   Port: 465 (TLS)
   ```

3. **Import Certificate**
   - Download .p12 certificate from HISP
   - Import to Windows Certificate Store
   - Outlook uses certificate automatically

### Configuration Example
```
SMTP Server: direct.hisp.com
SMTP Port: 465 (TLS required)
IMAP Server: direct.hisp.com
IMAP Port: 993 (TLS required)
Username: provider@hospital.direct
Password: [HISP password]
```

## Step 4: Programmatic Integration

### Python Implementation

#### Send Direct Message
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl

class DirectClient:
    def __init__(self, direct_address, password, hisp_server):
        self.direct_address = direct_address
        self.password = password
        self.hisp_server = hisp_server
        self.smtp_port = 465

    def send_message(self, recipient_direct_address, subject, body, attachments=None):
        """Send Direct message"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.direct_address
            msg['To'] = recipient_direct_address
            msg['Subject'] = subject

            # Add body
            msg.attach(MIMEText(body, 'plain'))

            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    self.attach_file(msg, file_path)

            # Create TLS connection
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL(self.hisp_server, self.smtp_port, context=context) as server:
                # Login
                server.login(self.direct_address, self.password)

                # Send message
                server.send_message(msg)

            print(f"Message sent to {recipient_direct_address}")
            return True

        except smtplib.SMTPException as e:
            print(f"SMTP error: {e}")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def attach_file(self, msg, file_path):
        """Attach file to message"""
        from email.mime.base import MIMEBase
        from email import encoders
        import os

        with open(file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(file_path)}')
        msg.attach(part)

# Usage
direct_client = DirectClient(
    direct_address='provider@hospital.direct',
    password='your_password',
    hisp_server='direct.hisp.com'
)

# Send referral
body = """Patient referral attached.

Please review and contact patient within 48 hours."""

result = direct_client.send_message(
    recipient_direct_address='specialist@clinic.direct',
    subject='Cardiology Referral - Patient Jane Doe',
    body=body,
    attachments=['referral_document.pdf']
)
```

#### Receive Direct Messages
```python
import imaplib
import email
from email.header import decode_header

class DirectReceiver:
    def __init__(self, direct_address, password, hisp_server):
        self.direct_address = direct_address
        self.password = password
        self.hisp_server = hisp_server
        self.imap_port = 993

    def fetch_messages(self, folder='INBOX', max_messages=10):
        """Fetch Direct messages"""
        messages = []

        try:
            # Create IMAP connection
            imap = imaplib.IMAP4_SSL(self.hisp_server, self.imap_port)

            # Login
            imap.login(self.direct_address, self.password)

            # Select inbox
            imap.select(folder)

            # Search for messages
            status, message_ids = imap.search(None, 'ALL')

            if status != 'OK':
                print("Failed to search messages")
                return messages

            # Fetch messages
            for msg_id in message_ids[0].split()[-max_messages:]:
                status, msg_data = imap.fetch(msg_id, '(RFC822)')

                if status != 'OK':
                    continue

                # Parse message
                msg = email.message_from_bytes(msg_data[0][1])

                message_info = {
                    'from': msg['From'],
                    'to': msg['To'],
                    'subject': decode_header(msg['Subject'])[0][0],
                    'date': msg['Date'],
                    'body': self.get_body(msg),
                    'attachments': self.get_attachments(msg)
                }

                messages.append(message_info)

            imap.close()
            imap.logout()

        except imaplib.IMAP4.error as e:
            print(f"IMAP error: {e}")
        except Exception as e:
            print(f"Error: {e}")

        return messages

    def get_body(self, msg):
        """Extract message body"""
        body = ''

        if msg.is_multipart():
            for part in msg.get_payload():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode('utf-8')
                    break
        else:
            body = msg.get_payload(decode=True).decode('utf-8')

        return body

    def get_attachments(self, msg):
        """Extract attachments"""
        attachments = []

        if msg.is_multipart():
            for part in msg.get_payload():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            'filename': filename,
                            'data': part.get_payload(decode=True)
                        })

        return attachments

# Usage
receiver = DirectReceiver(
    direct_address='provider@hospital.direct',
    password='your_password',
    hisp_server='direct.hisp.com'
)

messages = receiver.fetch_messages(max_messages=10)

for msg in messages:
    print(f"From: {msg['from']}")
    print(f"Subject: {msg['subject']}")
    print(f"Body: {msg['body'][:100]}...")
    if msg['attachments']:
        print(f"Attachments: {[a['filename'] for a in msg['attachments']]}")
    print("---")
```

## Step 5: Certificate Management

### Import Certificate
```python
import ssl
import certifi

# Verify certificate validity
def verify_certificate(cert_path):
    """Verify Direct certificate"""
    import subprocess

    result = subprocess.run(
        ['openssl', 'x509', '-in', cert_path, '-noout', '-dates'],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    return result.returncode == 0

# Check expiration
def check_cert_expiration(cert_path):
    """Check certificate expiration"""
    from datetime import datetime
    import subprocess

    result = subprocess.run(
        ['openssl', 'x509', '-in', cert_path, '-noout', '-enddate'],
        capture_output=True,
        text=True
    )

    # Extract date
    date_str = result.stdout.split('=')[1].strip()
    expiration = datetime.strptime(date_str, '%b %d %H:%M:%S %Y %Z')

    days_left = (expiration - datetime.now()).days

    if days_left < 30:
        print(f"WARNING: Certificate expires in {days_left} days")
    else:
        print(f"Certificate valid for {days_left} more days")

    return days_left

# Usage
verify_certificate('/path/to/certificate.pem')
check_cert_expiration('/path/to/certificate.pem')
```

## Step 6: Error Handling & Reliability

```python
class RobustDirectClient(DirectClient):
    def __init__(self, direct_address, password, hisp_server, retry_attempts=3):
        super().__init__(direct_address, password, hisp_server)
        self.retry_attempts = retry_attempts
        self.failed_messages = []

    def send_message_with_retry(self, recipient, subject, body, attachments=None):
        """Send with retry logic"""
        for attempt in range(1, self.retry_attempts + 1):
            try:
                result = self.send_message(recipient, subject, body, attachments)

                if result:
                    return True

            except Exception as e:
                print(f"Attempt {attempt} failed: {e}")

                if attempt == self.retry_attempts:
                    # Store failed message for manual retry
                    self.failed_messages.append({
                        'recipient': recipient,
                        'subject': subject,
                        'body': body,
                        'attachments': attachments,
                        'error': str(e)
                    })

                    # Alert administrator
                    self.alert_admin(f"Failed to send Direct message to {recipient}")
                    return False

        return False

    def alert_admin(self, message):
        """Alert administrator of failure"""
        # Send alert email, Slack message, etc.
        print(f"ALERT: {message}")
```

## Step 7: Integration with EHR

### Example: EHR Referral Sending
```python
class EHRDirectIntegration:
    def __init__(self, direct_client, fhir_client):
        self.direct_client = direct_client
        self.fhir_client = fhir_client

    def send_referral(self, patient_id, specialist_direct_address):
        """Send referral via Direct"""
        # Fetch patient from FHIR
        patient = self.fhir_client.read('Patient', patient_id)

        # Fetch recent observations
        observations = self.fhir_client.search('Observation', {'patient': patient_id})

        # Fetch conditions
        conditions = self.fhir_client.search('Condition', {'patient': patient_id})

        # Generate referral document (PDF)
        pdf = self.generate_referral_pdf(patient, observations, conditions)

        # Send via Direct
        subject = f"Referral - {patient['name'][0]['family']}, {patient['name'][0]['given'][0]}"
        body = f"""Referral for {patient['name'][0]['family']}, {patient['name'][0]['given'][0]}
DOB: {patient['birthDate']}
MRN: {patient['identifier'][0]['value']}

Please find attached referral document.

Thanks,
{self.direct_client.direct_address}
"""

        result = self.direct_client.send_message_with_retry(
            recipient_direct_address=specialist_direct_address,
            subject=subject,
            body=body,
            attachments=[pdf]
        )

        return result

    def generate_referral_pdf(self, patient, observations, conditions):
        """Generate PDF referral"""
        from reportlab.pdfgen import canvas
        import io

        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer)

        # Add patient info
        c.drawString(50, 750, f"Patient: {patient['name'][0]['family']}, {patient['name'][0]['given'][0]}")
        c.drawString(50, 730, f"DOB: {patient['birthDate']}")
        c.drawString(50, 710, f"MRN: {patient['identifier'][0]['value']}")

        # Add conditions
        y = 680
        c.drawString(50, y, "Conditions:")
        for condition in conditions:
            y -= 20
            c.drawString(70, y, f"- {condition['code']['text']}")

        # Add observations
        y -= 20
        c.drawString(50, y, "Recent Results:")
        for obs in observations:
            y -= 20
            c.drawString(70, y, f"- {obs['code']['text']}: {obs.get('valueQuantity', {}).get('value')}")

        c.save()

        return pdf_buffer.getvalue()
```

## Next Steps

1. Test Direct communication with another provider
2. Implement automated referral sending
3. Set up monitoring and alerts
4. Create user documentation
5. Train staff on Direct usage

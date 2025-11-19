# Direct Protocol Reference Guide

## Overview

Direct Protocol provides a secure, standards-based way to send encrypted email over the internet for healthcare communications. HIPAA-compliant alternative to email for Protected Health Information (PHI).

## Key Concepts

### Direct Addresses
- Format: username@directdomain.com
- Unique identifier for a Direct recipient
- Can represent individuals or organizations
- Registered in national Direct directories

### Certification
- Issued by Certificate Authorities
- S/MIME (Secure/Multipurpose Internet Mail Extensions)
- TLS for transport security
- Non-repudiation of origin and delivery

## Components

### 1. Direct User Agent
- Direct email client software
- Handles encryption/decryption
- Certificate management
- Attachment handling

**Examples:**
- Outlook with Direct plugin
- Apple Mail with Direct plugin
- Direct webmail interfaces
- EHR integrated Direct clients

### 2. Direct Host Service Provider (HISP)
- Manages Direct mailbox
- Provides technical infrastructure
- Offers secure transport
- Manages certificates and keys

**HISP Responsibilities:**
- Direct address registration
- Certificate provisioning
- Secure message storage
- Delivery confirmation
- Support and help desk

### 3. Direct Internet Backbone
- Network of HISPs
- Federation agreements
- Trust anchors
- Directory services

## Security Model

### Authentication
- X.509 digital certificates
- Certificate validation during transmission
- Trust anchor verification
- Certificate revocation checking (CRL, OCSP)

### Encryption
- **S/MIME Version 3** - Message encryption
- **Algorithm:** AES-256 (preferred)
- **Key Exchange:** RSA 2048-bit
- **Hash:** SHA-256 or stronger

### Transport
- **TLS 1.2+** - Channel encryption
- **Mutual authentication** between Direct systems
- **Non-repudiation** - Sender cannot deny sending

### Message Integrity
- Digital signature verification
- Message authentication code (MAC)
- Tamper detection
- Timestamp validation

## Message Flow

```
1. Sender composes message in Direct UA
2. Message automatically encrypted with recipient's certificate
3. Message signed with sender's certificate
4. Message sent to sender's HISP via TLS
5. HISP validates certificate and signature
6. HISP queries Direct directory for recipient
7. Message routed to recipient's HISP via Direct protocol
8. Recipient's HISP validates and stores message
9. Recipient retrieves via UA when convenient
10. UA decrypts with recipient's private key
```

## Direct Addressing

### Address Types
- **Individual Direct Address** - Personal address
- **Organizational Direct Address** - Department/group address
- **Alias Address** - Forwarding address
- **Distribution List** - Group of recipients

### Directory Services
- **Healthcare Provider Directory (HPD)** - Provider addresses
- **National Plan and Provider Enumeration System (NPPES)** - NPI registry
- **State directories** - Regional provider listings

## Delivery Confirmation

### Delivery Notifications
- **Message Delivery Notification (MDN)** - Confirms receipt
- **Non-Delivery Notification** - Returns undeliverable messages
- **Delivery time confirmation** - When message arrived
- **Digital receipt** - Signed confirmation

### Return Receipts
- **Requested in message** - Optional
- **Digitally signed** - By recipient's HISP
- **Includes timestamp** - Proof of delivery
- **Non-repudiation** - Legal evidence of delivery

## Direct Metadata

### Required Fields
- **To:** Recipient Direct address
- **From:** Sender Direct address
- **Subject:** Message subject
- **Date:** Transmission time
- **Message-ID:** Unique identifier
- **Content-Type:** MIME type

### Optional Fields
- **CC/BCC:** Additional recipients
- **Reply-To:** Reply address
- **Attachments:** File inclusions
- **X-Direct-Final-Destination-Delivery:** Confirms delivery

## Protocol Details

### SMTP for Direct
```
SMTP connection to HISP
Port: 25, 465, 587 (TLS required)
AUTH: Username/password or certificate-based
Commands: MAIL FROM, RCPT TO, DATA
Extensions: STARTTLS, SIZE, DSN
```

### POP3/IMAP for Direct
```
POP3 Port: 110 (TLS), 995 (Implicit TLS)
IMAP Port: 143 (TLS), 993 (Implicit TLS)
AUTH: Username/password or certificate
Must use TLS encryption
```

## Configuration Requirements

### Sender Configuration
- Direct address assignment
- Certificate installation
- HISP credentials
- Mail server settings (SMTP)

### Recipient Configuration
- Direct address directory listing
- Certificate installation
- HISP mailbox access
- Mail client setup (POP3/IMAP)

### System Integration
```
EHR ←→ Direct Plugin ←→ HISP ←→ Internet ←→ HISP ←→ EHR
```

## Common Use Cases

### 1. Patient Referral
```
Referring Provider → Direct → Specialist Provider
- Referral document
- Lab/imaging results
- Previous notes
- Patient contact info
```

### 2. Lab Results
```
Lab System → Direct → Ordering Provider
- Result report
- Test values
- Reference ranges
- Comments
```

### 3. Consultation Notes
```
Consultant → Direct → Primary Provider
- Consultation findings
- Recommendations
- Follow-up instructions
- Medication changes
```

### 4. Discharge Summary
```
Hospital Discharge System → Direct → Primary Care
- Hospital course summary
- Medications
- Discharge diagnosis
- Follow-up appointments
```

### 5. Patient Access
```
Provider EHR → Direct → Patient Direct Address
- Records access
- Test results
- Appointment reminders
- Clinical summaries
```

## Compliance Considerations

### HIPAA Compliance
- ✓ Encryption in transit and at rest
- ✓ Authentication of both parties
- ✓ Non-repudiation
- ✓ Audit logging
- ✓ Business Associate Agreement (BAA) not required
- ✓ Safe harbor method

### Other Regulations
- **State privacy laws** - Vary by jurisdiction
- **HITECH Act** - Breach notification requirements
- **21 CFR Part 11** - For regulated entities
- **State medical board requirements** - Telemedicine use

## Failure and Recovery

### Message Failures
- **Certificate expired** - Regenerate certificates
- **HISP down** - Retry with exponential backoff
- **Invalid address** - Return to sender with error
- **Bounced message** - Manual intervention needed

### Error Handling
```
- Store failed messages
- Implement retry logic
- Alert on failures
- Log for audit trail
- Escalate to help desk
```

## Performance and Limits

### Message Limits
- **Size:** Varies by HISP (typically 25-50 MB)
- **Attachments:** Encrypted file count limit
- **Recipients:** May be limited per message
- **Frequency:** Rate limiting policies

### Throughput
- **Typical delivery time:** Minutes to hours
- **Guaranteed delivery time:** Per HISP SLA
- **Retry mechanism:** Up to 48 hours typical

## Directory and Resolution

### Direct Directory
- HISP provides directory lookups
- LDAP queries for address validation
- Certificate retrieval
- Address book synchronization

### Address Resolution
```
directuser@hisp.com → Certificate lookup → TLS connection → Delivery
```

## HISP Selection Criteria

- **Pricing** - Transaction or monthly fees
- **Features** - Portal, API, integrations
- **Uptime** - SLA guarantees (99.5%+)
- **Support** - 24/7 technical support
- **Integration** - EHR plugins, APIs
- **Compliance** - HIPAA, SOC 2, accreditation
- **Geographic presence** - Local support options

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Message not sending | Certificate invalid | Renew certificate |
| Delivery failure | Address not found | Verify address in directory |
| Encryption error | Recipient cert unavailable | Request new certificate |
| Slow delivery | HISP overloaded | Contact HISP support |
| Cannot receive | Mailbox full | Archive old messages |

## Evolution and Future

### Direct Plus
- Enhanced security features
- Additional metadata
- Compliance tracking
- Audit improvements

### Interoperability
- FHIR integration
- API access to Direct
- Single sign-on (SSO)
- Multi-factor authentication (MFA)

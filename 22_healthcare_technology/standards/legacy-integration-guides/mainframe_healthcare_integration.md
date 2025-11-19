# Mainframe Healthcare Integration

**Production-grade guide for connecting legacy healthcare mainframes to modern systems**

---

## Executive Summary

Legacy healthcare mainframes (IBM zSeries, UNIVAC, Data General) continue to operate in approximately 40% of large healthcare organizations, maintaining critical patient data and regulatory records. This guide provides proven patterns for secure, reliable integration between mainframe-based legacy systems and modern EHRs, cloud platforms, and contemporary healthcare applications.

## Mainframe Landscape in Healthcare

### Common Healthcare Mainframe Platforms

| Platform | Installed Base | Languages | Data | Status |
|----------|-----------------|-----------|------|--------|
| **IBM zSeries (z/OS)** | 60+ hospitals | COBOL, PL/I, Assembler | Patient billing, medical records, insurance | Active, modern support |
| **UNIVAC (Unisys)** | 25+ hospitals | COBOL, UNIVAC PL/I | Historical lab data, accounting | Legacy, declining support |
| **Data General (now DGC)** | 15+ hospitals | COBOL, Business BASIC | Clinical data, pharmacy data | Legacy, custom support |
| **Hitachi VOS** | 12+ hospitals | COBOL, ALGOL | Hospital administration, scheduling | Legacy |

### Legacy Systems Still Common

```
Typical Healthcare Mainframe Functions:

Patient Master File (PMF)
├── Patient demographics
├── Medical record numbers
├── Insurance information
├── Encounter history (all admissions/visits)
└── Billing address and contact

Account Receivable System
├── Charge capture
├── Claims generation
├── Payment posting
├── Aging reports
└── Revenue reporting

Dictation/Transcription
├── Voice dictation storage
├── Medical record transcripts
├── Physician notes (scanned)
└── Discharge summaries

Scheduling System
├── OR scheduling
├── Clinic appointments
├── Resource management
└── Physician availability
```

---

## Integration Architecture Patterns

### 1. Batch Data Extract/Transform/Load (ETL)

#### Use Case: Daily Patient Master File Extract

**Most Common Integration Pattern for Mainframes**

```
Timeline:
21:00 - Mainframe ETL job runs
21:15 - Flat file extract complete (FTP to staging server)
21:30 - Transformation process begins
22:00 - Load into target system begins
23:00 - Process complete, validation begins
23:30 - Notification of completion/errors

Mainframe JCL (Job Control Language) for extraction:
```

```cobol
//PMFEXTRC JOB (6789,'EXTRACT',CLASS=A,MSGCLASS=A,MSGLEVEL=(1,1),
//             TIME=(0,30),REGION=4096K
//*
//* EXTRACT PATIENT MASTER FILE FOR EHR INTEGRATION
//*
//STEP1    EXEC PGM=DFSORT,REGION=4096K
//SYSOUT   DD SYSOUT=*
//SORTIN   DD DISP=SHR,DSN=PATIENT.MASTER.FILE
//SORTOUT  DD DSN=WORK.PMF.EXTRACT(+1),
//            DISP=(NEW,CATLG),
//            UNIT=SYSDA,
//            SPACE=(TRK,(500,50),RLSE)
//SYSIN    DD *
  SORT FIELDS=(1,5,CH,A)
  OUTFIL FNAMES=SORTOUT,
         HEADER1=('PATIENT MASTER FILE EXTRACT',/,
                  'DATE: TODAY IN Y4MDDD FORMAT',/),
         SORT FIELDS=(1,5,CH,A),
         SAVE=YES
/*
//STEP2    EXEC PGM=IFOX00,REGION=4096K
//SYSLIB   DD DSN=COBOL.COPYBOOK,DISP=SHR
//SYSIN    DD DSN=COBOL.SOURCE(PMFCOPY),DISP=SHR
//STEPLIB  DD DSN=COBOL.OBJECT,DISP=SHR
//SYSOUT   DD SYSOUT=*
//SORTIN   DD DISP=SHR,DSN=WORK.PMF.EXTRACT(0)
//FILEOUT  DD DSN=TRANSFER.PMF.CSV,
//            DISP=(NEW,CATLG),
//            UNIT=SYSDA,
//            SPACE=(TRK,(1000,100),RLSE),
//            RECFM=FB,LRECL=500
//*
//STEP3    EXEC PGM=FTPPROG,REGION=4096K
//SYSOUT   DD SYSOUT=*
//SYSPRINT DD SYSOUT=*
//INPUT    DD *
  OPEN MYFTP HOST USERID PASSWORD
  PUT 'TRANSFER.PMF.CSV' '/upload/pmf/extract_YYYYMMDD.csv'
  GET '/control/ACK.txt' 'TRANSFER.ACK.TXT'
  QUIT
/*
```

**COBOL Program to Flatten Mainframe Records**:
```cobol
       IDENTIFICATION DIVISION.
       PROGRAM-ID. PMFCOPY.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT PATIENT-FILE ASSIGN TO SORTIN
               ORGANIZATION IS SEQUENTIAL.
           SELECT OUTPUT-FILE ASSIGN TO FILEOUT
               ORGANIZATION IS SEQUENTIAL.

       DATA DIVISION.
       FILE SECTION.
       FD PATIENT-FILE.
       01 PATIENT-RECORD.
           05 PATIENT-ID            PIC 9(8).
           05 LAST-NAME             PIC X(25).
           05 FIRST-NAME            PIC X(20).
           05 MIDDLE-INITIAL        PIC X.
           05 DATE-OF-BIRTH         PIC 9(8).  *> CCYYMMDD
           05 SEX-CODE              PIC X.
           05 STREET-ADDRESS        PIC X(30).
           05 CITY                  PIC X(20).
           05 STATE                 PIC XX.
           05 ZIP-CODE              PIC 9(5).
           05 PHONE-NUMBER          PIC 9(10).
           05 INSURANCE-CARRIER     PIC X(4).
           05 POLICY-NUMBER         PIC 9(10).
           05 GROUP-NUMBER          PIC 9(6).
           05 FILLER                PIC X(30).

       FD OUTPUT-FILE.
       01 CSV-RECORD               PIC X(500).

       WORKING-STORAGE SECTION.
       01 EOF-FLAG                 PIC X VALUE 'N'.
       01 RECORD-COUNT             PIC 9(8) VALUE 0.
       01 ERROR-FLAG               PIC X VALUE 'N'.

       01 CSV-FIELDS.
           05 CSV-PATIENT-ID       PIC 9(8).
           05 CSV-DELIMITER        PIC X VALUE ','.
           05 CSV-LAST-NAME        PIC X(25).
           05 FILLER               PIC X VALUE ','.
           05 CSV-FIRST-NAME       PIC X(20).
           05 FILLER               PIC X VALUE ','.
           05 CSV-DOB              PIC 9(8).
           05 FILLER               PIC X VALUE ','.
           05 CSV-POLICY           PIC 9(10).

       PROCEDURE DIVISION.
       000-MAIN-PROCEDURE.
           PERFORM 100-INITIALIZE.
           PERFORM 200-PROCESS-RECORDS.
           PERFORM 300-FINALIZE.
           STOP RUN.

       100-INITIALIZE.
           OPEN INPUT PATIENT-FILE.
           OPEN OUTPUT OUTPUT-FILE.
           DISPLAY 'PMF EXTRACT STARTED'.

       200-PROCESS-RECORDS.
           PERFORM UNTIL EOF-FLAG = 'Y'
               READ PATIENT-FILE
                   AT END
                       MOVE 'Y' TO EOF-FLAG
                   NOT AT END
                       PERFORM 210-FORMAT-RECORD
                       PERFORM 220-WRITE-RECORD
               END-READ
           END-PERFORM.

       210-FORMAT-RECORD.
           MOVE PATIENT-ID TO CSV-PATIENT-ID.
           MOVE LAST-NAME TO CSV-LAST-NAME.
           MOVE FIRST-NAME TO CSV-FIRST-NAME.
           MOVE DATE-OF-BIRTH TO CSV-DOB.
           MOVE POLICY-NUMBER TO CSV-POLICY.

           *> Validate required fields
           IF CSV-PATIENT-ID = 0
               MOVE 'Y' TO ERROR-FLAG
               DISPLAY 'ERROR: MISSING PATIENT ID'
           END-IF.

       220-WRITE-RECORD.
           IF ERROR-FLAG = 'N'
               MOVE CSV-FIELDS TO CSV-RECORD
               WRITE CSV-RECORD
               ADD 1 TO RECORD-COUNT
           END-IF.
           MOVE 'N' TO ERROR-FLAG.

       300-FINALIZE.
           CLOSE PATIENT-FILE.
           CLOSE OUTPUT-FILE.
           DISPLAY 'PMF EXTRACT COMPLETE: ' RECORD-COUNT ' RECORDS'.
```

### 2. File Transfer Methods

#### SFTP Transfer (Secure Alternative to FTP)

```bash
#!/bin/bash
# Transfer mainframe extract to staging server
# Run from middleware/integration server

MAINFRAME_HOST="mainframe.hospital.local"
MAINFRAME_USER="integsvc"
MAINFRAME_KEYFILE="/secure/keys/mainframe_key"

LOCAL_STAGING="/data/mainframe/staging"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# SFTP with error handling
sftp -i $MAINFRAME_KEYFILE \
     -b /dev/stdin \
     ${MAINFRAME_USER}@${MAINFRAME_HOST} << EOF

# Change to mainframe transfer directory
cd /mf/exports

# Get list of available files
ls -ltr pmf_extract*.csv

# Download most recent
get pmf_extract_latest.csv ${LOCAL_STAGING}/pmf_${TIMESTAMP}.csv

# Download checksum
get pmf_extract_latest.sha256 ${LOCAL_STAGING}/pmf_${TIMESTAMP}.sha256

# Remove from mainframe (after verification)
# rm pmf_extract_latest.csv

# Exit SFTP
bye
EOF

# Verify file integrity
if [ -f "${LOCAL_STAGING}/pmf_${TIMESTAMP}.sha256" ]; then
    sha256sum -c "${LOCAL_STAGING}/pmf_${TIMESTAMP}.sha256" \
        ${LOCAL_STAGING}/pmf_${TIMESTAMP}.csv

    if [ $? -eq 0 ]; then
        echo "File integrity verified"
        # Proceed with ETL
        /scripts/process_pmf_extract.sh ${LOCAL_STAGING}/pmf_${TIMESTAMP}.csv
    else
        echo "ALERT: File integrity check failed"
        # Send notification
        mail -s "CRITICAL: PMF Extract Integrity Failed" \
             integration-support@hospital.local < /dev/null
    fi
fi
```

#### Mainframe SFTP Configuration

```
Configuration on Mainframe (z/OS SSH):

1. SSH Configuration File:
   Location: ~user/.ssh/config

   Host integration-server
       HostName integration.hospital.local
       User integsvc
       IdentityFile ~/.ssh/id_rsa_integration
       Protocol 2
       Cipher aes256-ctr
       MACs hmac-sha2-256

2. SSH Daemon Configuration:
   Location: /etc/sshd_config

   # Require public key authentication
   PubkeyAuthentication yes
   PasswordAuthentication no

   # Security settings
   Protocol 2
   Ciphers aes256-ctr,aes192-ctr
   MACs hmac-sha2-256,hmac-sha2-512

   # Restrict to specific user
   AllowUsers integsvc@integration.hospital.local
```

### 3. Real-Time Data Streaming

#### CDC (Change Data Capture) from Mainframe

**Advanced Pattern for Real-Time Integration**

```
Challenge: Traditional batch ETL is 24+ hour latency
Solution: Change Data Capture (CDC) for near real-time

CDC Implementation Approaches:

1. Database Trigger + Audit Table
   ├── Mainframe database logs changes to audit table
   ├── Integration middleware polls audit table
   ├── Latency: 5-15 minutes
   └── Pros: Works with existing database

2. Replication Tools (IBM DataStax, DMS)
   ├── Physical replication of database changes
   ├── Latency: <1 minute
   └── Cons: Expensive, requires dedicated infrastructure

3. Application-Level Logging
   ├── COBOL programs log changes to CDC tables
   ├── Middleware streams changes in real-time
   ├── Latency: <5 minutes
   └── Pros: Maximum control
```

**Mainframe CDC Table Example**:

```cobol
       FD CDC-AUDIT-FILE.
       01 CDC-AUDIT-RECORD.
           05 CDC-TIMESTAMP        PIC 9(14).  *> CCYYMMDDHHMMSS
           05 CDC-OPERATION        PIC X.      *> I=Insert, U=Update, D=Delete
           05 CDC-TABLE-NAME       PIC X(20).
           05 CDC-PRIMARY-KEY      PIC 9(10).
           05 CDC-FIELD-NAME       PIC X(30).
           05 CDC-OLD-VALUE        PIC X(100).
           05 CDC-NEW-VALUE        PIC X(100).
           05 CDC-USER-ID          PIC X(8).
           05 CDC-PROGRAM-ID       PIC X(8).
           05 FILLER               PIC X(50).
```

**Middleware Processing (Python)**:
```python
#!/usr/bin/env python3
# CDC Stream Processor - Mainframe to EHR

import asyncio
import json
from datetime import datetime
import logging
from sftp_client import SFTPClient
from kafka_producer import KafkaProducer

class MainframeChanges:
    def __init__(self, mainframe_host, kafka_broker):
        self.sftp = SFTPClient(mainframe_host)
        self.kafka = KafkaProducer(kafka_broker)
        self.logger = logging.getLogger(__name__)
        self.last_timestamp = self.load_checkpoint()

    async def stream_cdc_changes(self, interval_seconds=60):
        """
        Continuously stream changes from mainframe
        """
        while True:
            try:
                # Download CDC audit log
                cdc_file = self.sftp.get_latest_cdc_file()

                # Process changes since last checkpoint
                with open(cdc_file, 'r') as f:
                    for line in f:
                        record = self.parse_cdc_record(line)

                        if int(record['timestamp']) > self.last_timestamp:
                            # Map mainframe operation to change event
                            event = self.transform_to_event(record)

                            # Publish to Kafka topic
                            topic = f"mainframe_changes_{record['table']}"
                            self.kafka.publish(topic, event)

                            # Update checkpoint
                            self.last_timestamp = int(record['timestamp'])
                            self.save_checkpoint()

            except Exception as e:
                self.logger.error(f"CDC streaming error: {e}")
                # Continue on error (no data loss)

            # Wait for next polling interval
            await asyncio.sleep(interval_seconds)

    def parse_cdc_record(self, line):
        """Parse CDC audit table record"""
        fields = line.strip().split('|')
        return {
            'timestamp': fields[0],
            'operation': fields[1],
            'table': fields[2],
            'primary_key': fields[3],
            'field_name': fields[4],
            'old_value': fields[5],
            'new_value': fields[6],
            'user_id': fields[7],
            'program_id': fields[8]
        }

    def transform_to_event(self, cdc_record):
        """Transform CDC record to event for downstream systems"""
        return {
            'source': 'mainframe',
            'event_type': f"{cdc_record['table']}.{cdc_record['operation']}",
            'primary_key': cdc_record['primary_key'],
            'timestamp': cdc_record['timestamp'],
            'change': {
                'field': cdc_record['field_name'],
                'old_value': cdc_record['old_value'],
                'new_value': cdc_record['new_value']
            },
            'audit': {
                'user_id': cdc_record['user_id'],
                'program_id': cdc_record['program_id']
            }
        }
```

---

## Data Format Conversion

### 1. EBCDIC to ASCII Conversion

Mainframes use EBCDIC encoding; most modern systems use ASCII/UTF-8.

```bash
#!/bin/bash
# Convert EBCDIC mainframe files to ASCII

INPUT_FILE=$1
OUTPUT_FILE=$2

# Using dd command for EBCDIC to ASCII conversion
dd if=$INPUT_FILE \
   of=$OUTPUT_FILE \
   iconv=ebcdic,ascii \
   cbs=500 \
   conv=lcase 2>/dev/null

# Verify conversion
file $OUTPUT_FILE
wc -l $INPUT_FILE $OUTPUT_FILE
```

**Character Encoding Issues**:
```
EBCDIC Character Mappings (Healthcare Context):

EBCDIC Hex → ASCII Character → Healthcare Use
0x41      → 'A'              → Patient name first letter
0x4D      → 'M'              → Medical record prefix
0x60      → '~'              → HL7 message delimiter
0xBA      → '^'              → HL7 field separator

Common Issues:
├── Extended ASCII characters lost in conversion
├── Special characters become garbage
├── Record delimiters disappear
└── Numeric signs (SIGNED NUMERIC) misinterpreted
```

### 2. Packed Decimal Conversion

Mainframes use packed decimal (COMP-3) for numbers; inefficient to transmit.

```cobol
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CONV-PACKED-DECIMAL.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 MAINFRAME-AMOUNT      PIC S9(7)V99 COMP-3.
       01 ASCII-AMOUNT          PIC -(7)9.99.

       PROCEDURE DIVISION.
           MOVE 123456.78 TO MAINFRAME-AMOUNT.

           *> Convert packed decimal to ASCII for transmission
           MOVE MAINFRAME-AMOUNT TO ASCII-AMOUNT.
           DISPLAY ASCII-AMOUNT.  *> Output: '  123456.78'
```

---

## Security Considerations

### 1. Mainframe Access Control

```
z/OS Resource Access Control Facility (RACF):

Define Integration User:
  ADDUSER INTGUSER NAME('Integration Service') +
          OWNER(SECURITY) +
          DFLTGRP(MAINFRAME.USERS) +
          RESTRICT

Grant Specific Permissions:
  PERMIT 'PATIENT.MASTER.FILE' CLASS(DATASET) +
         ID(INTGUSER) ACCESS(READ)

  PERMIT 'TRANSFER.PMF.CSV' CLASS(DATASET) +
         ID(INTGUSER) ACCESS(CREATE,WRITE)

Restrict SSH Access:
  RDEFINE FACILITY EIM.IDMAP.AUTHENTICATE +
          UACC(NONE)
  PERMIT EIM.IDMAP.AUTHENTICATE CLASS(FACILITY) +
         ID(INTGUSER) ACCESS(READ)
```

### 2. Data Encryption in Transit

```
SFTP Configuration for Encryption:

# /etc/ssh/sshd_config on Mainframe SSH

# Strong ciphers (128-bit minimum for enterprise)
Ciphers aes256-ctr,aes192-ctr,aes128-ctr

# Key exchange algorithms
KexAlgorithms diffie-hellman-group-exchange-sha256

# Message authentication codes
MACs hmac-sha2-512,hmac-sha2-256

# Disable weak algorithms
# Exclude: 3des, aes128-cbc, MD5 hashes
```

### 3. Encryption at Rest

```
Mainframe Dataset Encryption (z/OS):

# Pervasive Encryption definitions
ADDVOL VOLSER(XXXXXX) SECMODEL(ENABLED) +
       KEYDS(ACTIVE)

# Dataset encryption
ADDDS 'PATIENT.MASTER.FILE' +
      UNIT(SYSALLDA) +
      LIKE('PATIENT.TEMPLATE') +
      ENCRYPT(YES) +
      ENCALG(AES256)
```

---

## Mainframe Integration - Common Challenges

| Challenge | Cause | Solution |
|-----------|-------|----------|
| **Performance Degradation During Extract** | Large batch jobs consume mainframe CPU | Schedule extracts during off-peak hours; implement incremental extracts (CDC) |
| **File Transfer Timeouts** | Large datasets over slow networks | Implement resumable transfers; split files; increase timeout values |
| **Encoding Conversion Errors** | EBCDIC special characters not mapping | Validate all character sets pre-migration; use certified conversion tools |
| **Missing Historical Data** | Mainframe data purge policies | Archive mainframe data before integration; implement long-term retention policy |
| **Mainframe Expertise Shortage** | Legacy JCL/COBOL skills deprecated | Document existing processes thoroughly; cross-train younger staff; consider outsourcing |
| **Regulatory Compliance Issues** | Legacy audit trail insufficient | Implement comprehensive logging layer; validate compliance before cutover |

---

## Migration Path: Mainframe → Modern Systems

### Phase 1: Coexistence (Months 1-6)
```
├── Keep mainframe running in production
├── Implement data replication/export
├── Daily validation of exported data
├── Build EHR parallel with replicated data
└── Clinical validation of data completeness
```

### Phase 2: Phased Cutover (Months 6-12)
```
├── Week 1: Cutover billing system
├── Week 2: Cutover patient master file
├── Week 3: Cutover encounter data
├── Week 4: Cutover ancillary systems
├── Months 2-3: Monitor for data issues
└── Archive mainframe (read-only)
```

### Phase 3: Decommissioning (Months 12+)
```
├── Month 1: Mainframe in archival mode
├── Month 2: Legal hold release
├── Month 3: Final backup, decommission
└── Year 1: Retain offline backups per retention policy
```

---

## Tools and Resources

### ETL Tools for Mainframe Integration
- **Informatica PowerCenter**: Enterprise ETL, mainframe connectors
- **Talend**: Open-source ETL, cost-effective
- **MuleSoft**: iPaaS platform, mainframe connectivity
- **IBM Datapower**: API gateway with mainframe integration
- **Progress OpenEdge**: Legacy app integration

### Mainframe Connectivity Tools
- **IBM DataStax**: CDC from mainframe databases
- **Serena ChangeMan**: Database change management
- **Iron Data**: Real-time mainframe data streaming
- **ACI Worldwide**: Payment system integration

---

## References

- z/OS Documentation: IBM Knowledge Center
- COBOL Standards: ISO/IEC 1989-2014
- EBCDIC Character Set: IBM Enterprise System/3090 Reference
- HIPAA Security Rule: 45 CFR 164.300-320
- HL7 v2.x Standard: http://www.hl7.org/

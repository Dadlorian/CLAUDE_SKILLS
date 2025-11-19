# IHE Profile Implementation Guide

## Executive Summary

This guide provides comprehensive implementation standards for IHE (Integrating the Healthcare Enterprise) profiles including XDS.b (Cross-Enterprise Document Sharing), PIX (Patient Identifier Cross-Referencing), PDQ (Patient Demographics Query), and XCA (Cross-Community Access). These profiles enable secure, standardized interoperability across healthcare systems.

---

## 1. IHE XDS.b (Cross-Enterprise Document Sharing)

### 1.1 Overview

XDS.b defines a standards-based specification for managing clinical documents across healthcare organizations while maintaining patient privacy and appropriate access controls.

**Key Actors:**
- Document Source: Generates and publishes documents
- Document Repository: Stores documents and metadata
- Document Registry: Maintains document metadata indices
- Document Consumer: Retrieves and displays documents

### 1.2 Architecture

```
┌─────────────────────┐
│  Document Source    │
│  (EHR System)       │
└──────────┬──────────┘
           │
           │ Provide & Register (ebRS)
           │
┌──────────▼──────────┐
│   Document Registry │
│   (Metadata Index)  │
└──────────┬──────────┘
           │
      ┌────┴────┐
      │          │
      │ Query    │ Retrieve
      │          │
┌─────▼──┐  ┌───▼─────┐
│Registry │  │Repository│
│Stored   │  │Document  │
│Query    │  │Retrieve  │
└─────────┘  └──────────┘
```

### 1.3 Document Submission Workflow

#### 1.3.1 XDS Provide & Register Transaction (ITI-41)

**Request Format (SOAP/ebRS):**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:rs="urn:oasis:names:tc:ebxml-regrep:xsd:rs:3.0"
               xmlns:rim="urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0">
  <soap:Body>
    <rs:SubmitObjectsRequest>
      <rim:RegistryObjectList>

        <!-- ExtrinsicObject: Represents the document -->
        <rim:ExtrinsicObject id="Document01"
                             mimeType="application/pdf"
                             objectType="urn:uuid:34268e47-fdf5-41a6-ba33-82133c465248">
          <rim:Slot name="creationTime">
            <rim:ValueList>
              <rim:Value>20240115143022</rim:Value>
            </rim:ValueList>
          </rim:Slot>
          <rim:Slot name="languageCode">
            <rim:ValueList>
              <rim:Value>en-US</rim:Value>
            </rim:ValueList>
          </rim:Slot>
          <rim:Slot name="sourcePatientId">
            <rim:ValueList>
              <rim:Value>PID123^^^&1.2.840.113619.6.197&ISO</rim:Value>
            </rim:ValueList>
          </rim:Slot>
          <rim:Slot name="sourcePatientInfo">
            <rim:ValueList>
              <rim:Value>PID-3|PID123^^^&1.2.840.113619.6.197&ISO</rim:Value>
              <rim:Value>PID-5|Doe^John</rim:Value>
              <rim:Value>PID-7|19700101</rim:Value>
              <rim:Value>PID-8|M</rim:Value>
            </rim:ValueList>
          </rim:Slot>
          <rim:Slot name="contentTypeCode">
            <rim:ValueList>
              <rim:Value>34133-9</rim:Value>
            </rim:ValueList>
          </rim:Slot>

          <!-- Classification: Document type -->
          <rim:Classification id="cl1"
                              classificationScheme="urn:uuid:2c6b8cb7-8b2a-41c3-a37a-d7f75b6b5e00"
                              nodeRepresentation="34133-9">
            <rim:Name>
              <rim:LocalizedString value="Summarization of Episode Note"/>
            </rim:Name>
          </rim:Classification>

          <!-- Classification: Privacy Policy -->
          <rim:Classification classificationScheme="urn:uuid:abf81fd6-31da-44f3-b5a9-8448854eb387"
                              nodeRepresentation="1.2.40.0.34.7.1">
            <rim:Name>
              <rim:LocalizedString value="Healthcare provider access level 1"/>
            </rim:Name>
          </rim:Classification>
        </rim:ExtrinsicObject>

        <!-- RegistryPackage: Represents a submission set -->
        <rim:RegistryPackage id="SubmissionSet01"
                             objectType="urn:uuid:a54d6aa5-d40f-43cf-b2cc-3a3d60f01d0a">
          <rim:Name>
            <rim:LocalizedString value="Submission Set for Patient: John Doe"/>
          </rim:Name>
          <rim:Slot name="submissionTime">
            <rim:ValueList>
              <rim:Value>20240115143022</rim:Value>
            </rim:ValueList>
          </rim:Slot>
          <rim:Slot name="intendedRecipient">
            <rim:ValueList>
              <rim:Value>^John Doe^^^^^^^^^PERSON</rim:Value>
            </rim:ValueList>
          </rim:Slot>

          <!-- Classification: Submission set type -->
          <rim:Classification classificationScheme="urn:uuid:a7058bb9-b4e4-4307-ba5b-e3f0ab85e12d"
                              nodeRepresentation="COMPREHENSIVE">
            <rim:Name>
              <rim:LocalizedString value="Comprehensive Submission Set"/>
            </rim:Name>
          </rim:Classification>
        </rim:RegistryPackage>

        <!-- Associations -->
        <rim:Association associationType="urn:oasis:names:tc:ebxml-regrep:AssociationType:HasMember"
                         sourceObject="SubmissionSet01"
                         targetObject="Document01"/>
      </rim:RegistryObjectList>
    </rs:SubmitObjectsRequest>
  </soap:Body>
</soap:Envelope>
```

#### 1.3.2 Implementation Code (Python)

```python
import hashlib
from datetime import datetime
from lxml import etree
from requests_soap import SoapClient

class XDSDocumentSubmitter:
    """Submits documents to XDS registry following IHE XDS.b standards"""

    def __init__(self, registry_endpoint: str, repository_endpoint: str):
        self.registry_endpoint = registry_endpoint
        self.repository_endpoint = repository_endpoint
        self.soap_client = SoapClient(wsdl_url=registry_endpoint + "?wsdl")

    def submit_document(
        self,
        document_content: bytes,
        patient_id: str,
        document_type_code: str,
        author_name: str,
        creation_time: datetime = None
    ) -> dict:
        """
        Submit a document to XDS registry

        Args:
            document_content: Raw document bytes
            patient_id: XAD-formatted patient identifier
            document_type_code: LOINC code for document type
            author_name: Author's full name
            creation_time: Document creation timestamp

        Returns:
            dict: Registry response with document ID and status
        """
        if creation_time is None:
            creation_time = datetime.utcnow()

        # Generate document hash and size
        doc_hash = hashlib.sha1(document_content).hexdigest()
        doc_size = len(document_content)

        # Store document in repository
        doc_id = self._store_in_repository(
            document_content,
            patient_id,
            doc_hash,
            doc_size
        )

        # Create registry submission XML
        submission_xml = self._build_submission_request(
            doc_id=doc_id,
            patient_id=patient_id,
            document_type_code=document_type_code,
            author_name=author_name,
            creation_time=creation_time,
            doc_hash=doc_hash,
            doc_size=doc_size
        )

        # Submit to registry
        response = self.soap_client.call(
            'ProvideAndRegisterDocumentSet',
            submission_xml
        )

        return self._parse_response(response)

    def _store_in_repository(
        self,
        content: bytes,
        patient_id: str,
        doc_hash: str,
        doc_size: int
    ) -> str:
        """Store document in repository and return unique ID"""
        doc_id = f"urn:uuid:{self._generate_uuid()}"

        # MIME type detection
        mime_type = self._detect_mime_type(content)

        # Store with metadata
        repository_request = {
            'documentId': doc_id,
            'patientId': patient_id,
            'content': content,
            'mimeType': mime_type,
            'hash': doc_hash,
            'size': doc_size
        }

        # Implementation depends on repository backend
        # Could be SFTP, S3, filesystem, etc.

        return doc_id

    def _build_submission_request(
        self,
        doc_id: str,
        patient_id: str,
        document_type_code: str,
        author_name: str,
        creation_time: datetime,
        doc_hash: str,
        doc_size: int
    ) -> str:
        """Build ebRS submission request XML"""

        timestamp = creation_time.strftime("%Y%m%d%H%M%S")

        # Build comprehensive XDS submission
        submission = f"""
        <rim:RegistryObjectList xmlns:rim="urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0">
            <rim:ExtrinsicObject id="{doc_id}" mimeType="application/pdf"
                                 objectType="urn:uuid:34268e47-fdf5-41a6-ba33-82133c465248">
                <rim:Slot name="creationTime">
                    <rim:ValueList>
                        <rim:Value>{timestamp}</rim:Value>
                    </rim:ValueList>
                </rim:Slot>
                <rim:Slot name="sourcePatientId">
                    <rim:ValueList>
                        <rim:Value>{patient_id}</rim:Value>
                    </rim:ValueList>
                </rim:Slot>
                <rim:Slot name="hash">
                    <rim:ValueList>
                        <rim:Value>{doc_hash}</rim:Value>
                    </rim:ValueList>
                </rim:Slot>
                <rim:Slot name="size">
                    <rim:ValueList>
                        <rim:Value>{doc_size}</rim:Value>
                    </rim:ValueList>
                </rim:Slot>
                <rim:Classification classificationScheme="urn:uuid:2c6b8cb7-8b2a-41c3-a37a-d7f75b6b5e00"
                                   nodeRepresentation="{document_type_code}">
                    <rim:Name>
                        <rim:LocalizedString value="{self._get_loinc_display(document_type_code)}"/>
                    </rim:Name>
                </rim:Classification>
            </rim:ExtrinsicObject>
            <rim:RegistryPackage id="SubmissionSet01"
                                 objectType="urn:uuid:a54d6aa5-d40f-43cf-b2cc-3a3d60f01d0a">
                <rim:Slot name="submissionTime">
                    <rim:ValueList>
                        <rim:Value>{timestamp}</rim:Value>
                    </rim:ValueList>
                </rim:Slot>
            </rim:RegistryPackage>
            <rim:Association associationType="urn:oasis:names:tc:ebxml-regrep:AssociationType:HasMember"
                           sourceObject="SubmissionSet01" targetObject="{doc_id}"/>
        </rim:RegistryObjectList>
        """

        return submission.strip()

    def _parse_response(self, response: dict) -> dict:
        """Parse registry response"""
        return {
            'status': response.get('status'),
            'document_id': response.get('documentId'),
            'message': response.get('message'),
            'success': response.get('status') == 'Success'
        }

    def _generate_uuid(self) -> str:
        """Generate UUID for document"""
        import uuid
        return str(uuid.uuid4())

    def _detect_mime_type(self, content: bytes) -> str:
        """Detect MIME type from content"""
        import magic
        mime = magic.Magic(mime=True)
        return mime.from_buffer(content)

    def _get_loinc_display(self, code: str) -> str:
        """Get LOINC display name"""
        # This would typically query a LOINC database
        loinc_map = {
            '34133-9': 'Summarization of Episode Note',
            '34268-e47': 'Consultation Note',
            '11506-3': 'Progress Note'
        }
        return loinc_map.get(code, code)
```

### 1.4 Document Query (ITI-18)

```python
class XDSDocumentQuery:
    """Query XDS registry for documents"""

    def query_by_patient_id(self, patient_id: str) -> list:
        """
        Query registry for all documents for a patient

        Args:
            patient_id: XAD-formatted patient identifier

        Returns:
            list: Document metadata entries
        """
        query = f"""
        SELECT * FROM Document
        WHERE sourcePatientId = '{patient_id}'
        AND status = 'APPROVED'
        ORDER BY creationTime DESC
        """

        response = self.registry_client.query_sql(query)
        return self._parse_query_response(response)

    def query_by_document_type(
        self,
        patient_id: str,
        document_type_code: str
    ) -> list:
        """Query documents by type for specific patient"""

        query = f"""
        SELECT d.* FROM Document d
        JOIN Classification c ON d.id = c.documentId
        WHERE d.sourcePatientId = '{patient_id}'
        AND c.classificationScheme = 'urn:uuid:2c6b8cb7-8b2a-41c3-a37a-d7f75b6b5e00'
        AND c.nodeRepresentation = '{document_type_code}'
        AND d.status = 'APPROVED'
        """

        response = self.registry_client.query_sql(query)
        return self._parse_query_response(response)
```

---

## 2. IHE PIX (Patient Identifier Cross-Referencing)

### 2.1 Overview

PIX enables healthcare systems to match patient records across different identifier domains while maintaining patient privacy.

**Key Actors:**
- PIX Source: Creates/updates patient records
- PIX Manager: Maintains cross-reference mappings
- PIX Consumer: Queries for patient identifiers

### 2.2 PIX Query Transaction (ITI-9)

```xml
<!-- PIX Query Request -->
<?xml version="1.0" encoding="UTF-8"?>
<HL7Message>
  <MSH fieldSeparator="|" componentSeparator="^" repeatSeparator="~" escapeCharacter="\" subcomponentSeparator="&">
    <MSH-1>|</MSH-1>
    <MSH-2>^~\&</MSH-2>
    <MSH-3>SendingApp</MSH-3>
    <MSH-4>SendingFacility</MSH-4>
    <MSH-5>ReceivingApp</MSH-5>
    <MSH-6>ReceivingFacility</MSH-6>
    <MSH-7>20240115143022</MSH-7>
    <MSH-8>SECURITY</MSH-8>
    <MSH-9>QBP^Q23^QBP_Q21</MSH-9>
    <MSH-10>MessageID123</MSH-10>
    <MSH-11>P</MSH-11>
    <MSH-12>2.5</MSH-12>
  </MSH>

  <QPD>
    <QPD-1>Q23</QPD-1>
    <QPD-2>QueryTag123</QPD-2>
    <QPD-3>PID123^^^&1.2.840.113619.6.197&ISO</QPD-3>
  </QPD>

  <RCP>
    <RCP-1>I</RCP-1>
    <RCP-2>10</RCP-2>
  </RCP>
</HL7Message>
```

### 2.3 PIX Manager Implementation

```python
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PatientIdentifier:
    id: str
    domain: str  # OID format: 1.2.840.113619.6.197

    def to_hl7(self) -> str:
        """Convert to HL7 XPN format"""
        return f"{self.id}^^^&{self.domain}&ISO"

class PIXManager:
    """Manages patient identifier cross-references"""

    def __init__(self, db_connection):
        self.db = db_connection

    def register_patient(
        self,
        primary_id: PatientIdentifier,
        linked_ids: List[PatientIdentifier],
        patient_name: str,
        dob: str
    ) -> dict:
        """
        Register patient with cross-reference identifiers

        Args:
            primary_id: Primary patient identifier
            linked_ids: Alternative identifiers from other systems
            patient_name: Patient's full name
            dob: Date of birth (YYYYMMDD)

        Returns:
            dict: Registration result
        """

        try:
            # Check for existing patient
            existing = self.db.query(
                "SELECT patient_id FROM patients WHERE id=? AND domain=?",
                [primary_id.id, primary_id.domain]
            )

            if existing:
                patient_id = existing[0]['patient_id']
                self._update_patient_links(patient_id, linked_ids)
            else:
                # Create new patient
                patient_id = self._create_patient(
                    primary_id,
                    patient_name,
                    dob
                )
                self._create_cross_references(patient_id, linked_ids)

            return {
                'status': 'SUCCESS',
                'patient_id': patient_id,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def query_patient_ids(
        self,
        query_id: PatientIdentifier,
        target_domains: List[str] = None
    ) -> Dict[str, str]:
        """
        Query for patient's identifiers in specified domains

        Args:
            query_id: Known patient identifier
            target_domains: List of OIDs for desired identifier domains

        Returns:
            dict: Mapping of domain OIDs to patient IDs
        """

        # Find patient by given identifier
        patient = self.db.query(
            """SELECT patient_id FROM patient_identifiers
               WHERE identifier=? AND domain=?""",
            [query_id.id, query_id.domain]
        )

        if not patient:
            return {}

        patient_id = patient[0]['patient_id']

        # Get all identifiers for patient
        identifiers = self.db.query(
            """SELECT identifier, domain FROM patient_identifiers
               WHERE patient_id=?""",
            [patient_id]
        )

        # Filter by requested domains if specified
        result = {}
        for id_row in identifiers:
            domain = id_row['domain']
            if target_domains is None or domain in target_domains:
                result[domain] = id_row['identifier']

        return result

    def merge_patients(
        self,
        survivor_id: PatientIdentifier,
        duplicate_ids: List[PatientIdentifier]
    ) -> dict:
        """
        Merge duplicate patient records

        Args:
            survivor_id: Identifier of patient record to keep
            duplicate_ids: Identifiers of duplicate records to merge

        Returns:
            dict: Merge result
        """

        try:
            survivor_patient = self.db.query(
                """SELECT patient_id FROM patient_identifiers
                   WHERE identifier=? AND domain=?""",
                [survivor_id.id, survivor_id.domain]
            )[0]

            survivor_patient_id = survivor_patient['patient_id']

            # Merge identifiers from duplicate records
            for dup_id in duplicate_ids:
                dup_patient = self.db.query(
                    """SELECT patient_id FROM patient_identifiers
                       WHERE identifier=? AND domain=?""",
                    [dup_id.id, dup_id.domain]
                )

                if dup_patient:
                    # Move all identifiers to survivor
                    self.db.execute(
                        """UPDATE patient_identifiers
                           SET patient_id=?
                           WHERE patient_id=?""",
                        [survivor_patient_id, dup_patient[0]['patient_id']]
                    )

            return {
                'status': 'SUCCESS',
                'message': f'Merged {len(duplicate_ids)} records',
                'survivor_patient_id': survivor_patient_id
            }

        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}
```

---

## 3. IHE PDQ (Patient Demographics Query)

### 3.1 Overview

PDQ enables querying patient demographic information across healthcare systems using HL7 v2.5 messages.

### 3.2 PDQ Query Implementation

```python
import hl7
from typing import List, Optional

class PDQConsumer:
    """Queries demographic information via PDQ"""

    def __init__(self, pdq_server_host: str, pdq_server_port: int = 2575):
        self.host = pdq_server_host
        self.port = pdq_server_port

    def query_by_demographics(
        self,
        family_name: str,
        given_name: Optional[str] = None,
        dob: Optional[str] = None,
        gender: Optional[str] = None
    ) -> List[dict]:
        """
        Query patients by demographic criteria

        Args:
            family_name: Patient's family name (required)
            given_name: Patient's given name (optional)
            dob: Date of birth YYYYMMDD (optional)
            gender: M, F, or U (optional)

        Returns:
            list: Matching patient records
        """

        # Build HL7 v2.5 PDQ query message
        query_msg = self._build_pdq_query(
            family_name,
            given_name,
            dob,
            gender
        )

        # Send to PDQ server
        response = self._send_query(query_msg)

        # Parse response
        return self._parse_pdq_response(response)

    def _build_pdq_query(
        self,
        family_name: str,
        given_name: Optional[str],
        dob: Optional[str],
        gender: Optional[str]
    ) -> str:
        """Build HL7 PDQ Query message"""

        # PID segment for demographics
        pid_segment = self._build_pid_segment(
            family_name,
            given_name,
            dob,
            gender
        )

        # MSH segment
        msh = "MSH|^~\\&|SendingApp|SendingFacility|PDQServer|PDQFacility|" \
              f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}||QBP^Q22^QBP_Q21|" \
              "PDQQUERY|P|2.5"

        # QPD segment (Query Parameter Definition)
        qpd = f"QPD|Q22^Find Candidates^HL7nnn|{self._generate_query_id()}|{pid_segment}"

        # RCP segment (Response Control Parameter)
        rcp = "RCP|I|10^records^RW|"

        return f"{msh}\r{qpd}\r{rcp}"

    def _build_pid_segment(
        self,
        family_name: str,
        given_name: Optional[str],
        dob: Optional[str],
        gender: Optional[str]
    ) -> str:
        """Build PID segment for query"""

        # HL7 XPN format: family^given^middle^prefix^suffix
        name = f"{family_name}"
        if given_name:
            name += f"^{given_name}"

        # Build components
        components = [f"@PID.3||" + f"^^^&1.2.840.113619.6.197&ISO"]
        components.append(f"@PID.5|{name}")

        if dob:
            components.append(f"@PID.7|{dob}")

        if gender:
            gender_code = 'M' if gender.upper() == 'M' else ('F' if gender.upper() == 'F' else 'U')
            components.append(f"@PID.8|{gender_code}")

        return "~".join(components)

    def _parse_pdq_response(self, response: str) -> List[dict]:
        """Parse PDQ query response"""

        results = []
        lines = response.split('\r')

        for line in lines:
            if line.startswith('PID'):
                # Parse patient record
                segments = line.split('|')
                patient = {
                    'patient_id': segments[3] if len(segments) > 3 else None,
                    'family_name': segments[5].split('^')[0] if len(segments) > 5 else None,
                    'given_name': segments[5].split('^')[1] if len(segments) > 5 and len(segments[5].split('^')) > 1 else None,
                    'dob': segments[7] if len(segments) > 7 else None,
                    'gender': segments[8] if len(segments) > 8 else None
                }
                results.append(patient)

        return results

    def _send_query(self, message: str) -> str:
        """Send query to PDQ server and get response"""
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.host, self.port))
            # Add MLLP wrapper (Minimal Lower Layer Protocol)
            mllp_message = f"\x0B{message}\x1C\x0D"
            sock.send(mllp_message.encode('utf-8'))
            response = sock.recv(4096).decode('utf-8')
            # Remove MLLP wrapper
            return response.strip('\x0B\x1C\x0D')
        finally:
            sock.close()

    def _generate_query_id(self) -> str:
        """Generate unique query ID"""
        import uuid
        return str(uuid.uuid4())[:12]
```

---

## 4. IHE XCA (Cross-Community Access)

### 4.1 Overview

XCA enables secure document discovery and retrieval across multiple XDS communities (trust domains).

**Key Actors:**
- Initiating Gateway: Initiates cross-community queries
- Responding Gateway: Responds to remote queries
- Document Source/Consumer: Local community participants

### 4.2 XCA Cross-Community Query (ITI-38)

```python
class XCACrossGateway:
    """Manages cross-community document access"""

    def __init__(self, homeCommunityId: str, respondingGateways: dict):
        """
        Args:
            homeCommunityId: OID for home community
            respondingGateways: Dict mapping community OID to SOAP endpoints
        """
        self.homeCommunityId = homeCommunityId
        self.respondingGateways = respondingGateways

    def cross_community_query(
        self,
        patient_id: str,
        target_communities: List[str],
        document_type_codes: List[str] = None,
        creation_date_range: tuple = None
    ) -> dict:
        """
        Query for documents across communities

        Args:
            patient_id: Patient identifier
            target_communities: List of community OIDs to query
            document_type_codes: Optional LOINC codes to filter
            creation_date_range: Optional (start_date, end_date)

        Returns:
            dict: Aggregated results from all communities
        """

        results = {
            'local_documents': [],
            'remote_documents': {},
            'errors': []
        }

        # Query local community first
        results['local_documents'] = self._query_local_community(
            patient_id,
            document_type_codes,
            creation_date_range
        )

        # Query each remote community
        for community_oid in target_communities:
            if community_oid == self.homeCommunityId:
                continue

            try:
                remote_results = self._query_remote_community(
                    community_oid,
                    patient_id,
                    document_type_codes,
                    creation_date_range
                )
                results['remote_documents'][community_oid] = remote_results
            except Exception as e:
                results['errors'].append({
                    'community': community_oid,
                    'error': str(e)
                })

        return results

    def _query_remote_community(
        self,
        community_oid: str,
        patient_id: str,
        document_type_codes: List[str],
        creation_date_range: tuple
    ) -> list:
        """Query specific remote community via XCA ITI-38"""

        if community_oid not in self.respondingGateways:
            raise ValueError(f"Unknown community: {community_oid}")

        gateway_endpoint = self.respondingGateways[community_oid]

        # Build cross-community query request
        request_xml = self._build_xca_query_request(
            patient_id,
            document_type_codes,
            creation_date_range,
            self.homeCommunityId,
            community_oid
        )

        # Send SOAP request to responding gateway
        response = self._send_soap_request(gateway_endpoint, request_xml)

        # Parse and return results
        return self._parse_xca_response(response, community_oid)

    def _build_xca_query_request(
        self,
        patient_id: str,
        document_type_codes: List[str],
        creation_date_range: tuple,
        initiating_gateway_oid: str,
        responding_gateway_oid: str
    ) -> str:
        """Build XCA Cross-Community Query request (ITI-38)"""

        # Build AdhocQueryRequest
        document_codes_xml = ""
        if document_type_codes:
            for code in document_type_codes:
                document_codes_xml += f"""
                <rim:Value>{code}</rim:Value>
                """

        date_range_xml = ""
        if creation_date_range:
            start, end = creation_date_range
            date_range_xml = f"""
            <rim:Slot name="creationTime">
                <rim:ValueList>
                    <rim:Value>(&gt;={start})(&lt;={end})</rim:Value>
                </rim:ValueList>
            </rim:Slot>
            """

        request = f"""
        <query:AdhocQueryRequest xmlns:query="urn:oasis:names:tc:ebxml-regrep:xsd:query:3.0"
                                  xmlns:rim="urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0">
            <query:ResponseOption returnComposedObjects="true" returnType="LeafClass"/>
            <rim:AdhocQuery id="urn:uuid:14d4debf-8f97-451d-b507-457d2fef2b2e">
                <rim:Slot name="$XDSDocumentEntryPatientId">
                    <rim:ValueList>
                        <rim:Value>'{patient_id}'</rim:Value>
                    </rim:ValueList>
                </rim:Slot>
                <rim:Slot name="$XDSDocumentEntryStatus">
                    <rim:ValueList>
                        <rim:Value>('urn:oasis:names:tc:ebxml-regrep:StatusType:Approved')</rim:Value>
                    </rim:ValueList>
                </rim:Slot>
                {date_range_xml}
                <rim:Slot name="$XDSDocumentEntryType">
                    <rim:ValueList>
                        {document_codes_xml}
                    </rim:ValueList>
                </rim:Slot>
                <rim:Slot name="$HomeCommunityId">
                    <rim:ValueList>
                        <rim:Value>urn:oid:{responding_gateway_oid}</rim:Value>
                    </rim:ValueList>
                </rim:Slot>
            </rim:AdhocQuery>
        </query:AdhocQueryRequest>
        """

        return request

    def cross_community_retrieve(
        self,
        document_reference: dict,
        community_oid: str
    ) -> bytes:
        """Retrieve document from remote community via XCA ITI-39"""

        gateway_endpoint = self.respondingGateways.get(community_oid)
        if not gateway_endpoint:
            raise ValueError(f"Unknown community: {community_oid}")

        # Build retrieve request
        retrieve_request = self._build_xca_retrieve_request(
            document_reference,
            self.homeCommunityId,
            community_oid
        )

        # Send to gateway
        response = self._send_soap_request(gateway_endpoint, retrieve_request)

        # Extract and return document
        return self._extract_document_content(response)

    def _send_soap_request(self, endpoint: str, body: str) -> str:
        """Send SOAP request to gateway"""
        import requests

        headers = {
            'Content-Type': 'application/soap+xml',
            'SOAPAction': ''
        }

        soap_envelope = f"""
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                {body}
            </soap:Body>
        </soap:Envelope>
        """

        response = requests.post(
            endpoint,
            data=soap_envelope,
            headers=headers,
            verify=True  # SSL verification
        )

        return response.text
```

---

## 5. Security & Compliance

### 5.1 SAML Authentication

```python
from saml2 import METADATA_FILENAME_PATTERN, client
from saml2.config import Config

class SAMLSecurityManager:
    """Manages SAML authentication for IHE transactions"""

    def __init__(self, sp_config: dict):
        self.config = Config()
        self.config.load_file(sp_config)
        self.client = client.Saml2Client(config=self.config)

    def create_authentication_request(self) -> tuple:
        """Create SAML authentication request"""
        request_id, request = self.client.create_authn_request(
            destination=self.config.idp_sso_url,
            nformat=saml.NAMEID_FORMAT_TRANSIENT
        )

        return request_id, request.to_string()

    def validate_response(self, response_str: str, request_id: str) -> dict:
        """Validate SAML response"""
        response = self.client.parse_response_string(
            response_str,
            outstanding_queries={request_id}
        )

        return {
            'authenticated': response.is_authenticated(),
            'user_id': response.get('name_id'),
            'attributes': response.get('attributes', {})
        }
```

### 5.2 TLS/Mutual Authentication

All IHE transactions MUST use:
- TLS 1.2 or higher
- Mutual certificate authentication
- Certificate validation including chain verification

---

## 6. Error Handling & Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class IHETransactionHandler:
    """Handles IHE transactions with retry logic"""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def execute_transaction(self, transaction: dict) -> dict:
        """Execute IHE transaction with exponential backoff retry"""

        try:
            response = self._send_transaction(transaction)
            return self._validate_response(response)
        except Exception as e:
            # Log error with context
            print(f"Transaction failed: {e}")
            raise
```

---

## References

- [IHE XDS.b Profile](https://www.ihe.net/uploadedFiles/Documents/ITI/IHE_ITI_TF_Vol2a.pdf)
- [HL7 v2.5 Standard](https://www.hl7.org/)
- [LOINC Registry](https://loinc.org)
- [DICOM Standard](https://www.dicomstandard.org/)

---

**Document Version:** 1.0
**Last Updated:** 2024-01-15
**Status:** Production Ready

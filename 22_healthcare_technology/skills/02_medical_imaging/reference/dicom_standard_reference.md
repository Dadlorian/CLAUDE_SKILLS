# DICOM Standard Reference

## Overview
DICOM (Digital Imaging and Communications in Medicine) is the international standard for medical images and related information. It defines formats for medical images that can be exchanged with the data and quality necessary for clinical use.

## DICOM Architecture

### Information Object Definitions (IODs)
IODs represent real-world entities:
- **Patient IOD**: Patient demographics
- **Study IOD**: Clinical context for imaging
- **Series IOD**: Single acquisition or reconstruction
- **Image IOD**: Single image instance
- **Structured Report IOD**: Measurements and findings

### Service-Object Pair (SOP) Classes
Combination of an IOD and DIMSE service:
- **CT Image Storage**: 1.2.840.10008.5.1.4.1.1.2
- **MR Image Storage**: 1.2.840.10008.5.1.4.1.1.4
- **US Image Storage**: 1.2.840.10008.5.1.4.1.1.6.1
- **Secondary Capture**: 1.2.840.10008.5.1.4.1.1.7
- **Grayscale Softcopy Presentation State**: 1.2.840.10008.5.1.4.1.1.11.1

## DICOM Data Model

### Hierarchical Structure
```
Patient
  └── Study (one imaging event)
       └── Series (one acquisition/protocol)
            └── Instance (single image or object)
```

### Unique Identifiers
- **Patient ID**: Local identifier (not globally unique)
- **Study Instance UID**: Globally unique study identifier
- **Series Instance UID**: Globally unique series identifier
- **SOP Instance UID**: Globally unique instance identifier

### UID Format
- Root: 1.2.840.10008 (DICOM)
- Organization: e.g., 1.2.840.10008.5.1.4 (SOP classes)
- Private: Must be registered with appropriate authority
- Construction: Use timestamp + random + counter for uniqueness

## DICOM File Format

### File Structure
```
1. File Preamble (128 bytes) - typically all zeros
2. DICOM Prefix "DICM" (4 bytes)
3. File Meta Information (Group 0002)
4. Data Set (medical image data and metadata)
```

### File Meta Information (Group 0x0002)
- **(0002,0000)** File Meta Information Group Length
- **(0002,0001)** File Meta Information Version
- **(0002,0002)** Media Storage SOP Class UID
- **(0002,0003)** Media Storage SOP Instance UID
- **(0002,0010)** Transfer Syntax UID
- **(0002,0012)** Implementation Class UID
- **(0002,0013)** Implementation Version Name

### Data Element Structure
```
Tag (4 bytes) | VR (2 bytes) | Length | Value
- Tag: Group (2 bytes) + Element (2 bytes)
- VR: Value Representation (data type)
- Length: Value field length
- Value: Actual data
```

### Value Representations (VR)
- **AE**: Application Entity (16 chars max)
- **AS**: Age String (4 chars: nnnD/W/M/Y)
- **CS**: Code String (16 chars max, uppercase)
- **DA**: Date (YYYYMMDD)
- **DS**: Decimal String (16 chars max)
- **DT**: DateTime (YYYYMMDDHHMMSS.FFFFFF)
- **FD**: Floating Point Double (8 bytes)
- **FL**: Floating Point Single (4 bytes)
- **IS**: Integer String (12 chars max)
- **LO**: Long String (64 chars max)
- **LT**: Long Text (10,240 chars max)
- **OB**: Other Byte (binary data)
- **OW**: Other Word (16-bit binary)
- **PN**: Person Name (64 chars max per component)
- **SH**: Short String (16 chars max)
- **SL**: Signed Long (4 bytes)
- **SQ**: Sequence of Items (nested data)
- **SS**: Signed Short (2 bytes)
- **ST**: Short Text (1,024 chars max)
- **TM**: Time (HHMMSS.FFFFFF)
- **UI**: Unique Identifier (64 chars max)
- **UL**: Unsigned Long (4 bytes)
- **US**: Unsigned Short (2 bytes)
- **UT**: Unlimited Text (max 2^32-2 chars)

## Transfer Syntaxes

### Uncompressed
- **Implicit VR Little Endian**: 1.2.840.10008.1.2 (default)
- **Explicit VR Little Endian**: 1.2.840.10008.1.2.1 (most common)
- **Explicit VR Big Endian**: 1.2.840.10008.1.2.2 (retired)

### Compressed
- **JPEG Baseline (Process 1)**: 1.2.840.10008.1.2.4.50 (lossy)
- **JPEG Extended (Process 2 & 4)**: 1.2.840.10008.1.2.4.51 (lossy)
- **JPEG Lossless (Process 14)**: 1.2.840.10008.1.2.4.57
- **JPEG Lossless (First-Order)**: 1.2.840.10008.1.2.4.70
- **JPEG-LS Lossless**: 1.2.840.10008.1.2.4.80
- **JPEG-LS Near-Lossless**: 1.2.840.10008.1.2.4.81
- **JPEG 2000 Lossless**: 1.2.840.10008.1.2.4.90
- **JPEG 2000 Lossy**: 1.2.840.10008.1.2.4.91
- **RLE Lossless**: 1.2.840.10008.1.2.5

### Encapsulation
Compressed pixel data is encapsulated:
```
Pixel Data (7FE0,0010) with undefined length
  → Item 1: Basic Offset Table
  → Item 2: Frame 1 compressed data
  → Item 3: Frame 2 compressed data
  → ...
  → Sequence Delimiter
```

## DICOM Network Protocol

### DIMSE Services (DICOM Message Service Element)

#### C-STORE (Storage)
- **Purpose**: Send images to PACS
- **Roles**: SCU (sender), SCP (receiver)
- **Flow**: SCU → C-STORE-RQ → SCP, SCP → C-STORE-RSP → SCU
- **Status**: 0x0000 (Success), 0xA700 (Out of resources), 0xC000 (Error)

#### C-FIND (Query)
- **Purpose**: Search for studies, series, images
- **Query Levels**: Patient, Study, Series, Image
- **Matching**: Exact, wildcard (*,?), range, list
- **Flow**: Sends multiple C-FIND-RSP with Pending status, final with Success
- **Return Keys**: Specified in request

#### C-MOVE (Retrieve)
- **Purpose**: Request images be sent to destination
- **Destination**: Specified AE Title (can be third party)
- **Flow**: SCU requests, SCP sends images via C-STORE to destination
- **Sub-operations**: Tracks number of completed/failed transfers

#### C-GET (Retrieve)
- **Purpose**: Request images be sent back to requester
- **Difference from C-MOVE**: Images returned on same association
- **Use Case**: Simpler than C-MOVE, but requires same association

#### C-ECHO (Verification)
- **Purpose**: Verify DICOM connection
- **Simple**: No payload, just success/failure
- **Use**: Connection testing, keepalive

### Association Establishment
```
1. SCU → A-ASSOCIATE-RQ → SCP
   - Application Context
   - Presentation Contexts (Abstract Syntax + Transfer Syntaxes)
   - User Information (Max PDU size, Implementation UID)

2. SCP → A-ASSOCIATE-AC → SCU
   - Accepted Presentation Contexts
   - Negotiated Transfer Syntax per context

3. DIMSE message exchange

4. A-RELEASE or A-ABORT
```

### Protocol Data Units (PDUs)
- **A-ASSOCIATE-RQ**: Association request (0x01)
- **A-ASSOCIATE-AC**: Association accept (0x02)
- **A-ASSOCIATE-RJ**: Association reject (0x03)
- **P-DATA-TF**: Data transfer (0x04)
- **A-RELEASE-RQ**: Release request (0x05)
- **A-RELEASE-RP**: Release response (0x06)
- **A-ABORT**: Abort (0x07)

### Application Entity (AE)
- **AE Title**: String identifier (max 16 chars)
- **Port**: TCP port (typically 104 or 11112)
- **Hostname**: IP address or DNS name
- **Configuration**: Each device has AE Title + port

## DICOM Services

### Storage Service
- **SOP Classes**: CT, MR, US, CR, DX, PET, etc.
- **Implementation**: Must support standard SOP classes
- **Transfer**: Typically push from modality to PACS

### Query/Retrieve Service
- **Models**: Patient Root, Study Root, Patient/Study Only
- **Levels**: Patient, Study, Series, Image
- **Keys**: Required, optional, matching rules
- **Retrieve**: C-MOVE or C-GET

### Modality Worklist Service
- **Purpose**: Provide exam details to modality
- **Query**: By patient name, ID, scheduled date/time
- **Returns**: Patient demographics, procedure details, accession number
- **Benefits**: Reduces data entry, improves accuracy

### Modality Performed Procedure Step (MPPS)
- **Purpose**: Notify about exam progress
- **States**: IN PROGRESS, COMPLETED, DISCONTINUED
- **Content**: Performed procedure, images created
- **Use**: Workflow tracking, billing triggers

### Storage Commitment
- **Purpose**: Confirm safe image storage
- **Flow**: SCU sends N-ACTION, SCP confirms storage
- **Use**: Safe to delete local copy after confirmation
- **Events**: N-EVENT-REPORT with success/failure

### Print Management
- **Purpose**: Send images to DICOM printer
- **Film Box**: Configure film layout
- **Image Box**: Individual image on film
- **Rarely Used**: Mostly replaced by digital display

## DICOMweb

### WADO-RS (Web Access to DICOM Objects - RESTful)
- **Retrieve Study**: GET /studies/{studyUID}
- **Retrieve Series**: GET /studies/{studyUID}/series/{seriesUID}
- **Retrieve Instance**: GET /studies/{studyUID}/series/{seriesUID}/instances/{instanceUID}
- **Retrieve Frames**: GET .../instances/{instanceUID}/frames/{frameNumber}
- **Accept**: application/dicom, image/jpeg, image/png

### QIDO-RS (Query based on ID for DICOM Objects)
- **Search Studies**: GET /studies?PatientName=Doe*&StudyDate=20240101-20240131
- **Search Series**: GET /studies/{studyUID}/series?Modality=CT
- **Search Instances**: GET /studies/{studyUID}/series/{seriesUID}/instances
- **Response**: JSON with DICOM metadata

### STOW-RS (Store Over the Web)
- **Store Instances**: POST /studies or POST /studies/{studyUID}
- **Content-Type**: multipart/related; type=application/dicom
- **Response**: XML with storage status

### WADO-URI (Legacy)
- **Single Object**: GET ?requestType=WADO&studyUID=...&seriesUID=...&objectUID=...
- **Content Type**: Specified with contentType parameter
- **Less Flexible**: Superseded by WADO-RS

## DICOM Security

### TLS Encryption
- **Profile**: BCP 195 (mandatory ciphers)
- **Certificates**: X.509 for authentication
- **Port**: Typically TLS on standard DICOM port

### User Authentication
- **User Identity Negotiation**: A-ASSOCIATE-RQ user information
- **Kerberos**: Ticket-based authentication
- **SAML**: Security Assertion Markup Language

### Access Control
- **Network**: IP filtering, firewall rules
- **Application**: User/role-based permissions
- **Audit**: All access logged

### Audit Trail
- **DICOM Audit Message**: Structured XML log
- **Events**: Login, query, retrieve, store, delete
- **Syslog**: UDP/TLS to centralized log server
- **Retention**: Required by regulations

## DICOM Conformance Statement

### Required Sections
1. **Introduction**: Product description, DICOM version
2. **Implementation Model**: Architecture, workflow
3. **AE Specifications**: For each AE in product
4. **Communication Profiles**: TCP/IP, TLS support
5. **Extensions/Specializations**: Private tags, non-standard features
6. **Configuration**: Installation parameters
7. **Support of Character Sets**: Encoding support

### AE Specification
- **SOP Classes**: Supported as SCU and/or SCP
- **Transfer Syntaxes**: For each SOP class
- **Attributes**: Required, optional, support level
- **Behavior**: How application uses DICOM services

## DICOM Extensions

### Private Tags
- **Format**: (GGGG,EEEE) where GGGG is odd
- **Creator**: (GGGG,0010-00FF) contains creator name
- **Data**: (GGGG,1000-FFFF) private data elements
- **Registration**: Not required but recommended

### Structured Reporting (SR)
- **Purpose**: Encode measurements, findings, interpretations
- **Content Tree**: Hierarchical structure
- **Relationships**: CONTAINS, HAS CONCEPT MOD, INFERRED FROM
- **Templates**: TID 1500 (Measurement Report), TID 1400 (Findings)

### Presentation States
- **Grayscale Softcopy**: Window/level, annotations, shutters
- **Color Softcopy**: For color images
- **Blending**: Multi-modality overlay
- **Purpose**: Consistent image display across viewers

### Encapsulated PDF/CDA
- **PDF**: Store reports as DICOM objects
- **CDA**: Clinical Document Architecture XML
- **SOP Class**: Encapsulated PDF Storage (1.2.840.10008.5.1.4.1.1.104.1)

## Version History

- **DICOM 3.0 (1993)**: Initial standard replacing ACR-NEMA 2.0
- **Supplements**: 200+ supplements adding features
- **Current**: Annual updates through supplements and correction proposals
- **Parts**: 22 parts covering different aspects (Part 3: IODs, Part 4: Service Classes, Part 6: Data Dictionary, Part 7: Message Exchange)

## Common DICOM Ports

- **104**: Official DICOM port (requires root on Unix)
- **11112**: Common alternative port
- **2762**: Common PACS vendor port
- **8042**: Orthanc default DICOMweb port
- **8080**: Common HTTP/DICOMweb port

## Resources

- **DICOM Standard**: https://www.dicomstandard.org
- **DICOM Library**: https://www.dicomlibrary.com
- **NEMA**: National Electrical Manufacturers Association (maintains standard)
- **Supplement Process**: Working Groups propose supplements for new features

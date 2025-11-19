# DICOM Tags Reference

## Tag Format
- **Notation**: (GGGG,EEEE) where GGGG = Group, EEEE = Element
- **Private Tags**: Groups with odd numbers are private (e.g., 0x0009, 0x0011)
- **Standard Tags**: Groups with even numbers are standard DICOM

## Critical Patient Tags

### Patient Module
| Tag | Name | VR | Description | Example |
|-----|------|----|-----------| --------|
| (0010,0010) | Patient's Name | PN | Patient full name | Doe^John^A^^Dr. |
| (0010,0020) | Patient ID | LO | Primary patient identifier | 123456789 |
| (0010,0030) | Patient's Birth Date | DA | YYYYMMDD | 19800515 |
| (0010,0040) | Patient's Sex | CS | M, F, O, or U | M |
| (0010,1010) | Patient's Age | AS | nnnD/W/M/Y | 045Y |
| (0010,1030) | Patient's Weight | DS | In kg | 70.5 |
| (0010,21C0) | Pregnancy Status | US | 1-4 or unknown | 1 |
| (0010,2160) | Ethnic Group | SH | Ethnicity | Caucasian |
| (0010,4000) | Patient Comments | LT | Additional info | Patient claustrophobic |

### Patient Name Components (PN)
Format: `FamilyName^GivenName^MiddleName^Prefix^Suffix`
- Example: `Smith^John^Robert^^Jr.`
- Ideographic: Additional components for Asian names
- Phonetic: Additional components for pronunciation

## Study Tags

### General Study Module
| Tag | Name | VR | Description | Example |
|-----|------|----|-----------| --------|
| (0020,000D) | Study Instance UID | UI | Unique study identifier | 1.2.840.113619.2.1.1.1 |
| (0008,0020) | Study Date | DA | YYYYMMDD | 20240315 |
| (0008,0030) | Study Time | TM | HHMMSS.FFFFFF | 143022.000000 |
| (0008,0090) | Referring Physician's Name | PN | Ordering physician | Smith^Jane^^Dr. |
| (0020,0010) | Study ID | SH | RIS study ID | 12345 |
| (0008,0050) | Accession Number | SH | Order identifier | A2024031500123 |
| (0008,1030) | Study Description | LO | Exam description | CT CHEST W/CONTRAST |
| (0008,1060) | Name of Physician(s) Reading Study | PN | Interpreting radiologist | Johnson^Mark^^Dr. |
| (0032,1032) | Requesting Physician | PN | Who requested study | Brown^Sarah^^Dr. |
| (0032,1060) | Requested Procedure Description | LO | Clinical indication | R/O PULMONARY EMBOLISM |

## Series Tags

### General Series Module
| Tag | Name | VR | Description | Example |
|-----|------|----|-----------| --------|
| (0020,000E) | Series Instance UID | UI | Unique series identifier | 1.2.840.113619.2.1.2.1 |
| (0008,0060) | Modality | CS | Imaging modality | CT |
| (0020,0011) | Series Number | IS | Series number in study | 2 |
| (0008,103E) | Series Description | LO | Series description | Axial 5mm |
| (0008,0021) | Series Date | DA | YYYYMMDD | 20240315 |
| (0008,0031) | Series Time | TM | HHMMSS.FFFFFF | 143525.000000 |
| (0018,0015) | Body Part Examined | CS | Anatomical region | CHEST |
| (0018,5100) | Patient Position | CS | Position in scanner | HFS (Head First Supine) |
| (0020,0060) | Laterality | CS | L, R, or bilateral | R |

### Patient Position Codes
- **HFS**: Head First Supine
- **HFP**: Head First Prone
- **HFDR**: Head First Decubitus Right
- **HFDL**: Head First Decubitus Left
- **FFP**: Feet First Prone
- **FFS**: Feet First Supine
- **FFDR**: Feet First Decubitus Right
- **FFDL**: Feet First Decubitus Left

## Instance (Image) Tags

### SOP Common Module
| Tag | Name | VR | Description | Example |
|-----|------|----|-----------| --------|
| (0008,0016) | SOP Class UID | UI | Type of object | 1.2.840.10008.5.1.4.1.1.2 |
| (0008,0018) | SOP Instance UID | UI | Unique instance identifier | 1.2.840.113619.2.1.3.1 |
| (0008,0012) | Instance Creation Date | DA | When created | 20240315 |
| (0008,0013) | Instance Creation Time | TM | Time created | 143530.000000 |
| (0020,0013) | Instance Number | IS | Image number in series | 45 |

### General Image Module
| Tag | Name | VR | Description | Example |
|-----|------|----|-----------| --------|
| (0020,0020) | Patient Orientation | CS | Image orientation | L\P |
| (0008,0008) | Image Type | CS | Type classification | ORIGINAL\PRIMARY\AXIAL |
| (0008,0023) | Content Date | DA | Image content date | 20240315 |
| (0008,0033) | Content Time | TM | Image content time | 143530.000000 |
| (0020,0032) | Image Position (Patient) | DS | X\Y\Z coordinates | -125.0\-125.0\67.5 |
| (0020,0037) | Image Orientation (Patient) | DS | Direction cosines | 1\0\0\0\1\0 |
| (0020,1041) | Slice Location | DS | Position along normal | 67.5 |

## Image Pixel Data Tags

### Image Pixel Module
| Tag | Name | VR | Description | Example |
|-----|------|----|-----------| --------|
| (0028,0002) | Samples per Pixel | US | 1 (grayscale), 3 (RGB) | 1 |
| (0028,0004) | Photometric Interpretation | CS | Color space | MONOCHROME2 |
| (0028,0010) | Rows | US | Image height in pixels | 512 |
| (0028,0011) | Columns | US | Image width in pixels | 512 |
| (0028,0100) | Bits Allocated | US | Bits per pixel | 16 |
| (0028,0101) | Bits Stored | US | Actual bits used | 12 |
| (0028,0102) | High Bit | US | Most significant bit | 11 |
| (0028,0103) | Pixel Representation | US | 0=unsigned, 1=signed | 0 |
| (0028,0030) | Pixel Spacing | DS | Row spacing\Column spacing (mm) | 0.488\0.488 |
| (0018,0050) | Slice Thickness | DS | Slice thickness (mm) | 5.0 |
| (7FE0,0010) | Pixel Data | OW/OB | The actual image data | [binary data] |

### Photometric Interpretation Values
- **MONOCHROME1**: Low values are white (rare)
- **MONOCHROME2**: Low values are black (most common)
- **RGB**: Red, green, blue color
- **PALETTE COLOR**: Indexed color with lookup table
- **YBR_FULL**: Color video format
- **YBR_FULL_422**: Compressed color video

### Pixel Value Transformation
```
Output = (Pixel Value × Rescale Slope) + Rescale Intercept

For CT: Output in Hounsfield Units (HU)
```

| Tag | Name | VR | Description | Example |
|-----|------|----|-----------| --------|
| (0028,1052) | Rescale Intercept | DS | Offset | -1024 |
| (0028,1053) | Rescale Slope | DS | Multiplier | 1 |
| (0028,1054) | Rescale Type | LO | Units | HU |

### Window/Level (Windowing)
| Tag | Name | VR | Description | Example |
|-----|------|----|-----------| --------|
| (0028,1050) | Window Center | DS | Center of gray scale | 40 |
| (0028,1051) | Window Width | DS | Range of gray scale | 400 |
| (0028,1055) | Window Center & Width Explanation | LO | Description | MEDIASTINUM |

Common CT Windows:
- **Lung**: Center -600, Width 1500
- **Mediastinum**: Center 40, Width 400
- **Bone**: Center 400, Width 2000
- **Brain**: Center 40, Width 80
- **Abdomen**: Center 50, Width 350

## CT-Specific Tags

### CT Image Module
| Tag | Name | VR | Description | Example |
|-----|------|----|-----------| --------|
| (0018,0060) | KVP | DS | Peak kilovoltage | 120 |
| (0018,1150) | Exposure Time | IS | Milliseconds | 500 |
| (0018,1151) | X-Ray Tube Current | IS | Milliamperes | 250 |
| (0018,1152) | Exposure | IS | mAs | 125 |
| (0018,1160) | Filter Type | SH | Filter material | BODY FILTER |
| (0018,1210) | Convolution Kernel | SH | Reconstruction kernel | STANDARD |
| (0018,0090) | Data Collection Diameter | DS | Field of view (mm) | 500 |
| (0018,1100) | Reconstruction Diameter | DS | Image FOV (mm) | 350 |
| (0018,1120) | Gantry/Detector Tilt | DS | Degrees | 0 |
| (0018,1130) | Table Height | DS | mm from floor | 145 |
| (0018,1140) | Rotation Direction | CS | CW or CC | CW |
| (0018,1150) | Exposure Time | IS | ms per rotation | 500 |

### CT Dose Tags
| Tag | Name | VR | Description | Example |
|-----|------|----|-----------| --------|
| (0018,9345) | CTDIvol | FD | Volume CTDI (mGy) | 15.2 |
| (0018,9346) | DLP | FD | Dose Length Product (mGy·cm) | 500.5 |
| (0018,9323) | Exposure Modulation Type | CS | AEC type | XYZ |

## MRI-Specific Tags

### MR Image Module
| Tag | Name | VR | Description | Example |
|-----|------|----|-----------| --------|
| (0018,0080) | Repetition Time | DS | TR in ms | 500 |
| (0018,0081) | Echo Time | DS | TE in ms | 12 |
| (0018,0082) | Inversion Time | DS | TI in ms | 150 |
| (0018,0083) | Number of Averages | DS | Signal averaging | 2 |
| (0018,0084) | Imaging Frequency | DS | MHz | 63.87 |
| (0018,0085) | Imaged Nucleus | SH | Nucleus type | 1H |
| (0018,0087) | Magnetic Field Strength | DS | Tesla | 3.0 |
| (0018,0088) | Spacing Between Slices | DS | mm | 6.0 |
| (0018,0091) | Echo Train Length | IS | Number of echoes | 16 |
| (0018,0093) | Percent Sampling | DS | k-space sampling % | 100 |
| (0018,0094) | Percent Phase Field of View | DS | Phase FOV % | 75 |
| (0018,0095) | Pixel Bandwidth | DS | Hz/pixel | 250 |
| (0018,1250) | Receive Coil Name | SH | Coil used | HEAD |
| (0018,1314) | Flip Angle | DS | Degrees | 90 |
| (0018,1316) | SAR | DS | W/kg | 1.5 |
| (0018,0024) | Sequence Name | SH | Pulse sequence | *tse2d1_15 |
| (0018,0020) | Scanning Sequence | CS | SE, IR, GR, EP, RM | SE |
| (0018,0021) | Sequence Variant | CS | SK, MTC, SS, TRSS, etc. | SK\SP\MP |
| (0018,0023) | MR Acquisition Type | CS | 2D or 3D | 2D |

## Equipment Tags

### General Equipment Module
| Tag | Name | VR | Description | Example |
|-----|------|----|-----------| --------|
| (0008,0070) | Manufacturer | LO | Vendor name | GE MEDICAL SYSTEMS |
| (0008,0080) | Institution Name | LO | Hospital/facility | General Hospital |
| (0008,0081) | Institution Address | ST | Physical address | 123 Main St, City, ST |
| (0008,1010) | Station Name | SH | Device name | CT01 |
| (0008,1040) | Institutional Department Name | LO | Department | Radiology |
| (0008,1090) | Manufacturer's Model Name | LO | Equipment model | LightSpeed VCT |
| (0018,1000) | Device Serial Number | LO | Serial number | 12345ABC |
| (0018,1020) | Software Versions | LO | Software version | Rev 14.3 |

## Contrast Tags

| Tag | Name | VR | Description | Example |
|-----|------|----|-----------| --------|
| (0018,0010) | Contrast/Bolus Agent | LO | Agent name | Omnipaque 350 |
| (0018,1040) | Contrast/Bolus Route | LO | Administration route | IV |
| (0018,1041) | Contrast/Bolus Volume | DS | Volume in mL | 100 |
| (0018,1042) | Contrast/Bolus Start Time | TM | Time administered | 143000.000000 |
| (0018,1043) | Contrast/Bolus Stop Time | TM | End time | 143200.000000 |
| (0018,1044) | Contrast/Bolus Total Dose | DS | Total dose | 100 |
| (0018,1046) | Contrast Flow Rate | DS | mL/s | 3.0 |
| (0018,1048) | Contrast Flow Duration | DS | Seconds | 33.3 |

## Overlay Tags

| Tag | Name | VR | Description | Example |
|-----|------|----|-----------| --------|
| (6000,0010) | Overlay Rows | US | Height | 512 |
| (6000,0011) | Overlay Columns | US | Width | 512 |
| (6000,0040) | Overlay Type | CS | G (graphics) or R (ROI) | G |
| (6000,0050) | Overlay Origin | SS | X\Y position | 1\1 |
| (6000,0100) | Overlay Bits Allocated | US | Bits per pixel | 1 |
| (6000,3000) | Overlay Data | OW | Binary overlay data | [binary data] |

Note: Overlay group can be 6000-601E (even numbers only)

## Structured Report Tags

### SR Document Module
| Tag | Name | VR | Description | Example |
|-----|------|----|-----------| --------|
| (0040,A040) | Value Type | CS | TEXT, CODE, NUM, etc. | CODE |
| (0040,A043) | Concept Name Code Sequence | SQ | What is being described | (125007, DCM, "Measurement") |
| (0040,A050) | Continuity Of Content | CS | SEPARATE or CONTINUOUS | SEPARATE |
| (0040,A168) | Concept Code Sequence | SQ | Coded concept | (111043, DCM, "Lesion") |
| (0040,A30A) | Numeric Value | DS | Measurement value | 15.3 |
| (0040,08EA) | Measurement Units Code Sequence | SQ | Units | (mm, UCUM, "millimeter") |

## Private Tags

### Private Tag Structure
```
(GGGG,0010) = "CREATOR" (Private Creator)
(GGGG,1001-10FF) = Private data elements
```

Example:
```
(0009,0010) = "SIEMENS CSA HEADER"
(0009,1001) = [Siemens-specific data]
```

### Common Private Tag Creators
- **GE Medical Systems**
- **SIEMENS**
- **Philips Imaging DD**
- **TOSHIBA_MEC**
- **Agfa**

## Sequence Tags (Nested Data)

### Sequence Structure
```
(0054,0016) Radiopharmaceutical Information Sequence
  > (0018,0031) Radiopharmaceutical
  > (0018,1074) Radionuclide Total Dose
  > (0018,1075) Radionuclide Half Life
```

| Tag | Name | VR | Description |
|-----|------|----|-----------|
| (0008,1115) | Referenced Series Sequence | SQ | Links to series |
| (0008,1140) | Referenced Image Sequence | SQ | Links to images |
| (0008,1150) | Referenced SOP Class UID | UI | Within sequence |
| (0008,1155) | Referenced SOP Instance UID | UI | Within sequence |
| (0040,0260) | Performed Protocol Code Sequence | SQ | Procedure codes |
| (0040,0440) | Protocol Context Sequence | SQ | Additional context |
| (0054,0016) | Radiopharmaceutical Information Sequence | SQ | Nuclear med |

## Date/Time Tags

### Format Specifications
- **DA (Date)**: YYYYMMDD (e.g., 20240315)
- **TM (Time)**: HHMMSS.FFFFFF (e.g., 143022.123456)
- **DT (DateTime)**: YYYYMMDDHHMMSS.FFFFFF±HHMM (e.g., 20240315143022.000000-0500)
- **AS (Age String)**: nnnD/W/M/Y (e.g., 045Y, 006M, 003W, 120D)

### Common Date/Time Tags
| Tag | Name | VR | Description |
|-----|------|----|-----------|
| (0008,0020) | Study Date | DA | Study performed |
| (0008,0021) | Series Date | DA | Series performed |
| (0008,0022) | Acquisition Date | DA | Data acquired |
| (0008,0023) | Content Date | DA | Image content |
| (0008,0030) | Study Time | TM | Study time |
| (0008,0031) | Series Time | TM | Series time |
| (0008,0032) | Acquisition Time | TM | Acquisition time |
| (0008,0033) | Content Time | TM | Content time |

## Query/Retrieve Tags

### Required Keys for C-FIND
**Patient Level:**
- (0010,0010) Patient's Name
- (0010,0020) Patient ID
- (0010,0030) Patient's Birth Date
- (0010,0040) Patient's Sex

**Study Level:**
- (0020,000D) Study Instance UID
- (0008,0020) Study Date
- (0008,0050) Accession Number
- (0008,1030) Study Description
- (0008,0061) Modalities in Study

**Series Level:**
- (0020,000E) Series Instance UID
- (0008,0060) Modality
- (0020,0011) Series Number
- (0008,103E) Series Description

**Image Level:**
- (0008,0018) SOP Instance UID
- (0020,0013) Instance Number

### Matching Rules
- **Exact Match**: Value must match exactly
- **Wildcard**: * (matches any string), ? (matches single char)
- **Range**: 20240101-20240131
- **List**: Value1\Value2\Value3
- **Universal**: Empty value matches all

## Important Modality-Specific Tags

### Ultrasound
| Tag | Name | Description |
|-----|------|-------------|
| (0018,6011) | Sequence of Ultrasound Regions | Region parameters |
| (0018,6012) | Region Spatial Format | Physical region |
| (0018,6014) | Region Data Type | Type of region |

### PET
| Tag | Name | Description |
|-----|------|-------------|
| (0054,0016) | Radiopharmaceutical Information Sequence | Tracer info |
| (0054,1001) | Units | BQML, CNTS, etc. |
| (0054,1102) | Decay Correction | NONE, START, ADMIN |

### Mammography
| Tag | Name | Description |
|-----|------|-------------|
| (0018,11A0) | Body Part Thickness | Compression thickness |
| (0018,11A2) | Compression Force | Newtons |
| (0018,1508) | Positioner Type | COMPRESSION, MAGNIFICATION |

## Reference Resources

- **DICOM Standard Part 6**: Complete data dictionary
- **dicomlibrary.com**: Searchable tag database
- **Tag Viewers**: Free tools to explore DICOM tags
- **Vendor Documentation**: Modality-specific private tags

# E-Discovery Load File Formats

## Overview

Load files are structured text files that contain metadata about documents and references to document images or native files. They enable the transfer of documents and metadata between e-discovery platforms, ensuring that coding, organizational structure, and document relationships are preserved.

## Primary Load File Types

### 1. Concordance DAT Format

**Description**: The most common e-discovery load file format, originated with Concordance software but now industry standard.

**File Extension**: `.dat`

**Structure**:
- Delimited text file
- One row per document
- Columns represent metadata fields
- First row often contains field names (optional)

**Delimiters**:
- **Field Delimiter**: ASCII 20 (¶ or Pilcrow) - most common
- **Alternative Field Delimiters**: Pipe (|), Tab (\t), Comma (,)
- **Quote**: ASCII 254 (þ or Thorn)
- **Newline**: ASCII 174 (« or Left Double Angle)

**Example**:
```
BEGDOC¶BEGATTACH¶ENDDOC¶ENDATTACH¶DOCTYPE¶AUTHOR¶SUBJECT¶DATECREATED
ACME001¶¶ACME001¶¶Email¶John Smith¶Meeting Notes¶01/15/2024
ACME002¶ACME001¶ACME002¶ACME001¶Attachment¶Jane Doe¶Presentation¶01/15/2024
```

**Common Field Names**:
- `BEGDOC` / `DOCID`: Beginning document number
- `ENDDOC`: Ending document number (for ranges)
- `BEGATTACH`: Parent document for attachments
- `ENDATTACH`: Ending parent document
- `VOLUME`: Production volume name
- `FILEPATH`: Path to native file
- `TEXTPATH`: Path to extracted text
- `DOCTYPE`: Document type (Email, Word, PDF, etc.)
- `AUTHOR`: Document author
- `DATECREATED`: Creation date
- `SUBJECT`: Email subject or document title
- `CUSTODIAN`: Custodian/data source

**Best Practices**:
- Use standard ASCII 20 delimiter (¶)
- Include field names in first row
- Escape or remove delimiter characters from data
- Validate file before import
- Test with small sample first

**Sample DAT File**:
```
DOCID¶BEGATTACH¶AUTHOR¶SUBJECT¶DATE¶TEXTPATH¶NATIVEPATH
ABC00001¶¶Smith, John¶Project Update¶01/15/2024¶\TEXT\ABC00001.txt¶\NATIVES\ABC00001.msg
ABC00002¶ABC00001¶Doe, Jane¶RE: Project Update¶01/16/2024¶\TEXT\ABC00002.txt¶\NATIVES\ABC00002.msg
```

### 2. Opticon (OPT) Format

**Description**: Image load file that references TIFF images and specifies page breaks for multi-page documents.

**File Extension**: `.opt`

**Structure**:
- Comma-delimited text file
- No header row
- Five or six columns

**Column Structure**:
```
[Document ID],[Volume/Path],[Image Path],[Document Break],[Folder Break],[Box Break]
```

**Fields**:
1. **Document ID**: Bates number or document identifier
2. **Volume Name**: Production volume identifier
3. **Image File Path**: Relative path to first page image
4. **Document Break**: "Y" if document break (first page), blank otherwise
5. **Folder Break**: "Y" if folder break, blank otherwise (optional)
6. **Box Break**: "Y" if box/volume break, blank otherwise (optional)

**Example**:
```
ACME00001,VOL001,IMAGES\0001\ACME00001.tif,Y,,
ACME00002,VOL001,IMAGES\0001\ACME00002.tif,,,
ACME00003,VOL001,IMAGES\0001\ACME00003.tif,Y,,
ACME00004,VOL001,IMAGES\0002\ACME00004.tif,,,
ACME00005,VOL001,IMAGES\0002\ACME00005.tif,Y,Y,
```

**Interpretation**:
- ACME00001: 1-page document (next line is new doc)
- ACME00003: 2-page document (ACME00002 is page 2, ACME00003 starts new doc)
- ACME00005: Multi-page document starting with folder break

**Best Practices**:
- Use relative paths (not absolute)
- Verify image file exists for each entry
- Ensure document breaks are correct
- Match OPT to DAT file (same document IDs)
- Test import before delivery

### 3. EDRM XML Format

**Description**: Extensible Markup Language (XML) format following EDRM schema standards.

**File Extension**: `.xml`

**Advantages**:
- Structured, hierarchical data
- Self-describing fields
- Supports complex relationships
- Industry standard schema
- Native file and text file references

**Structure**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Root>
  <Batch>
    <Documents>
      <Document>
        <Files>
          <File FileType="Native" FilePath="NATIVES\DOC001.docx" FileSize="45678" Hash="MD5HASH"/>
          <File FileType="Text" FilePath="TEXT\DOC001.txt"/>
        </Files>
        <ExternalDocID>ACME00001</ExternalDocID>
        <Author>John Smith</Author>
        <DateCreated>2024-01-15T10:30:00</DateCreated>
        <Subject>Meeting Notes</Subject>
        <Custodian>Smith, John</Custodian>
        <Tags>
          <Tag Type="Responsive">Yes</Tag>
          <Tag Type="Privileged">No</Tag>
        </Tags>
      </Document>
    </Documents>
  </Batch>
</Root>
```

**Common Elements**:
- `<ExternalDocID>`: Unique document identifier
- `<Files>`: Container for file references
- `<File>`: Individual file (native, text, image)
- `<Tags>`: Coding and classification
- `<ParentDocID>`: Attachment relationships
- Custom metadata fields

**Best Practices**:
- Validate against EDRM schema
- Use UTF-8 encoding
- Escape special XML characters
- Include hash values for integrity
- Reference files with relative paths

### 4. IPRO (LFP/DAT) Format

**Description**: IPRO-specific load file format, similar to Concordance but with variations.

**File Extension**: `.lfp` and `.dat`

**Structure**:
- Similar to Concordance DAT
- Proprietary field delimiters
- Image cross-reference file (.lfp)
- Metadata file (.dat)

**Key Differences**:
- Different delimiter characters
- Separate files for images and metadata
- IPRO-specific field names

### 5. Summation (DII) Format

**Description**: Summation database import format, older but still used in some contexts.

**File Extension**: `.dii`

**Structure**:
- Delimited text file
- Defines database structure
- Multiple linked files for images and text

### 6. CSV / Excel Formats

**Description**: Simple comma-separated values or Excel spreadsheet formats for metadata.

**File Extension**: `.csv`, `.xlsx`

**Structure**:
- Header row with field names
- One row per document
- Comma-delimited (CSV) or spreadsheet cells (Excel)

**Advantages**:
- Easy to create and edit
- Human-readable
- Open in Excel for review
- Platform-independent

**Disadvantages**:
- Delimiter conflicts (commas in data)
- No image file references
- No standard schema
- Not suitable for productions (informal only)

**Example CSV**:
```csv
DocumentID,Custodian,Author,DateCreated,Subject,FilePath
ACME00001,"Smith, John","Smith, John",01/15/2024,Meeting Notes,\NATIVES\ACME00001.docx
ACME00002,"Doe, Jane","Doe, Jane",01/16/2024,Project Plan,\NATIVES\ACME00002.xlsx
```

## Load File Components

### Metadata File (DAT)

**Purpose**: Contains document metadata and coding

**Required Fields**:
- Unique document identifier (Bates number)
- Document paths (native, text, images)

**Common Metadata Fields**:
- **Document Control**: BEGDOC, ENDDOC, DOCID, VOLUME
- **Email Metadata**: FROM, TO, CC, BCC, SUBJECT, DATESENT, DATERECEIVED
- **File Metadata**: FILENAME, FILEEXT, FILESIZE, FILEPATH, MD5HASH
- **Dates**: DATECREATED, DATEMODIFIED, DATEACCESSED
- **Custodian**: CUSTODIAN, DATASOURCE
- **Content**: TITLE, AUTHOR, SUBJECT, DOCUMENT_TYPE
- **Coding**: RESPONSIVE, PRIVILEGED, CONFIDENTIAL, ISSUES
- **Relationships**: BEGATTACH, ENDATTACH, PARENTID, ATTACHMENTCOUNT

### Image Cross-Reference File (OPT)

**Purpose**: Links Bates numbers to image files and defines page breaks

**Contents**:
- Document ID (Bates number)
- Image file paths
- Document and page break indicators

### Text File

**Format**: Plain text (.txt) extracted from documents

**Purpose**: Searchable text for full-text indexing

**Naming Convention**:
- Typically matches document ID: `ACME00001.txt`
- Organized in folders for manageability
- Referenced in metadata file

### Native Files

**Format**: Original application format (DOCX, PDF, MSG, XLSX, etc.)

**Purpose**: Preserve original file for productions or detailed review

**Organization**:
- Folder structure by volume or document range
- Maintain original filename or rename to Bates number
- Referenced in metadata file

## Production Volume Structure

### Typical Production Folder Structure

```
PRODUCTION_001/
├── IMAGES/
│   ├── 0001/
│   │   ├── ACME00001.tif
│   │   ├── ACME00002.tif
│   │   └── ...
│   ├── 0002/
│   │   └── ...
├── NATIVES/
│   ├── ACME00001.msg
│   ├── ACME00002.docx
│   └── ...
├── TEXT/
│   ├── ACME00001.txt
│   ├── ACME00002.txt
│   └── ...
├── LOADFILES/
│   ├── ACME_METADATA.dat
│   ├── ACME_IMAGES.opt
│   └── ACME_VOLUME_INFO.xml
└── PRODUCTION_LOG.pdf
```

### Volume Management

**Purpose**: Organize large productions into manageable units

**Strategies**:
- **Size-Based**: Volumes of 10,000-50,000 documents
- **Date-Based**: Volumes by production date
- **Custodian-Based**: Separate volumes per custodian
- **Media-Based**: Volumes per hard drive or DVD

**Naming Conventions**:
- `VOL001`, `VOL002`, etc.
- `PRODUCTION_001_20240115`
- `ACME_SMITH_VOL01`

## Load File Creation Process

### 1. Data Preparation

- Finalize document set for production
- Apply numbering (Bates)
- Apply redactions
- Generate images if needed
- Extract text files
- Organize native files

### 2. Field Mapping

- Determine required fields
- Map internal fields to production fields
- Standardize field names
- Define field order

### 3. Load File Generation

- Export metadata to DAT format
- Generate OPT file for images
- Create XML if required
- Verify file paths and references

### 4. Quality Control

- Validate load file syntax
- Check for delimiter conflicts
- Verify file path accuracy
- Test import in target system
- Verify document count matches
- Spot-check random samples

### 5. Packaging

- Organize files in production structure
- Create production log
- Generate MD5/SHA checksums
- Package for delivery (hard drive, FTP, cloud)

## Common Load File Issues

### Issue: Delimiter Conflicts

**Problem**: Data contains delimiter characters (¶, |, etc.)

**Solutions**:
- Escape delimiters in data
- Use quote characters
- Choose delimiter not present in data
- Clean data before export

### Issue: File Path Errors

**Problem**: Referenced files don't exist at specified paths

**Solutions**:
- Use relative paths (not absolute)
- Verify all files exist before export
- Validate paths programmatically
- Test import before delivery

### Issue: Character Encoding

**Problem**: Special characters display incorrectly

**Solutions**:
- Use UTF-8 encoding
- Specify encoding in file header
- Test with international characters
- Convert to safe character set

### Issue: Line Break Problems

**Problem**: Multi-line fields break file structure

**Solutions**:
- Use newline delimiter (ASCII 174)
- Replace line breaks with spaces
- Escape line breaks
- Use XML format for complex data

### Issue: Document Count Mismatch

**Problem**: Number of records doesn't match expected count

**Solutions**:
- Validate export completeness
- Check for duplicate IDs
- Verify filtering criteria
- Audit export process

## Load File Validation Tools

### Validation Checklist

- [ ] File syntax is valid (delimiters, structure)
- [ ] Field count matches across all rows
- [ ] Document IDs are unique
- [ ] Referenced files exist (natives, text, images)
- [ ] File paths use relative paths
- [ ] Special characters are properly escaped
- [ ] Attachment relationships are valid
- [ ] Document count matches expected
- [ ] Image count matches OPT file
- [ ] Test import succeeds in target platform

### Automated Validation

**Tools**:
- Custom scripts (Python, PowerShell)
- Load file validation software
- Platform import validation (Relativity, Concordance)
- Checksum verification (MD5, SHA-256)

**Python Example**:
```python
import csv

def validate_dat_file(file_path, delimiter='¶'):
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=delimiter)
        header = next(reader)
        field_count = len(header)

        for i, row in enumerate(reader, start=2):
            if len(row) != field_count:
                print(f"Row {i}: Field count mismatch")

            # Validate document ID is not empty
            if not row[0]:
                print(f"Row {i}: Missing document ID")
```

## Platform-Specific Considerations

### Relativity

- Supports DAT, OPT, and XML formats
- RDC (Relativity Desktop Client) for imports
- Import profile configuration
- Field mapping during import
- Automatic validation and error reporting

### Concordance

- Native DAT format
- CPL image database
- DII import format
- Field mapping required

### Everlaw

- Supports DAT and XML
- Cloud-based upload
- Automatic validation
- Field mapping interface

### Nuix

- Exports to multiple formats
- Custom scripting for load files
- Flexible field mapping
- Concordance load file support

## Best Practices Summary

1. **Standardize Early**: Agree on format and fields before production
2. **Use Relative Paths**: Never use absolute paths in load files
3. **Validate Thoroughly**: Test import before delivery
4. **Document Format**: Provide format specification with production
5. **Include All Components**: Metadata, images, text, natives as agreed
6. **Version Control**: Track load file versions and corrections
7. **Maintain Logs**: Document production process and decisions
8. **Test First**: Import sample before full production
9. **Backup Everything**: Maintain copies of all productions
10. **Clear Communication**: Clarify expectations with receiving party

## Resources

### Standards Organizations

- EDRM (Electronic Discovery Reference Model)
- Sedona Conference
- ISO standards for e-discovery

### Technical Specifications

- EDRM XML Schema documentation
- Concordance file format specifications
- Platform-specific import guides

## Conclusion

Understanding load file formats is essential for successful e-discovery productions. Proper creation, validation, and delivery of load files ensures that metadata, coding, and document relationships are preserved when transferring data between systems and parties.

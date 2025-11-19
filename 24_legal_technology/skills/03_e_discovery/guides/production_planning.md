# Production Planning Guide

## Production Specifications

### Defining Production Requirements
- Document format (TIFF, PDF, native)
- Metadata requirements
- Text extraction specifications
- Image quality standards
- Load file format and fields
- Bates numbering scheme
- Redaction requirements
- Encryption and access controls

### Standards and Protocols
- EDRM standards compliance
- PDF/A for archival
- UTF-8 text encoding
- Industry format conventions
- Quality standards

## Load File Generation

### Load File Types
- Images (TIFF stacks)
- Full text or extracted OCR
- Native file links
- Metadata associations
- Redaction locations

### Field Mapping
- Document ID/Bates numbers
- Date fields (normalized)
- From/To/CC/BCC for email
- Subject and body text
- Custodian information
- Privilege designations
- Responsiveness coding
- Issue tags and keywords
- Hash values and duplicates

### Load File Formats
- FCP (Relativity format)
- LFAP (Load File Architecture Protocol)
- DAT files with associated metadata
- Excel/CSV for smaller productions
- Custom formats per specifications

## Bates Numbering

### Numbering Scheme Design
- Prefix (client initials, case identifier)
- Sequential number range
- Suffix (page numbers for multi-page documents)
- Total format: PREFIX-######-PAGE

### Implementation
- Assign numbers pre-production
- Apply to document images
- Include in metadata
- Maintain continuity across productions
- Handle production updates

### Best Practices
- Reserve number ranges for additions
- Document numbering methodology
- Account for redacted versions
- Handle multi-production coordination
- Provide numbering certificates

## Production Workflow

### Phase 1: Preparation
1. Verify all documents processed
2. Conduct final privilege review
3. Apply final redactions
4. Normalize formats
5. Generate final statistics

### Phase 2: Load File Creation
1. Export metadata
2. Map fields appropriately
3. Link images to documents
4. Validate field accuracy
5. Perform quality checks

### Phase 3: Bates Application
1. Generate sequential numbers
2. Apply to images
3. Update metadata
4. Verify numbering accuracy
5. Create numbering log

### Phase 4: Final Validation
1. Spot-check documents
2. Verify metadata accuracy
3. Test search functionality
4. Validate redaction visibility
5. Confirm format compliance

### Phase 5: Delivery
1. Create production package
2. Generate privilege log
3. Provide documentation
4. Include load files
5. Create receipt confirmation

## Production Reports

### Documentation Delivered
- Production summary report
- Load file specifications
- Bates numbering certificate
- Privilege log
- Search term hit report
- Format compliance statement
- Scope and limitations statement

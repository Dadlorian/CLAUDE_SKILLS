# EDRM (Electronic Discovery Reference Model) Framework

## Overview

The Electronic Discovery Reference Model (EDRM) is a framework that outlines standards for the recovery and discovery of digital data. Created in 2005, it provides a common, flexible, and comprehensive approach to e-discovery processes.

## EDRM Stages

### 1. Information Governance

**Purpose**: Proactive management of information assets to reduce risk and costs

**Key Activities**:
- Develop and implement records retention policies
- Create data maps identifying where information resides
- Establish information lifecycle management
- Define roles and responsibilities
- Implement compliance monitoring
- Develop litigation readiness programs

**Deliverables**:
- Records retention schedule
- Data map and inventory
- Information governance policies
- Litigation hold procedures
- Compliance reports

**Best Practices**:
- Align with business objectives
- Include legal, IT, and business stakeholders
- Regularly update data maps
- Train employees on policies
- Monitor and audit compliance
- Document policy violations

### 2. Identification

**Purpose**: Locate potential sources of ESI that may be relevant to a legal matter

**Key Activities**:
- Identify custodians and data sources
- Interview custodians about data locations
- Identify unique or legacy data sources
- Assess data accessibility and volume
- Document data locations and systems
- Prioritize data sources by relevance

**Deliverables**:
- Custodian list
- Data source inventory
- Preliminary data volume estimates
- Accessibility assessment
- Collection prioritization plan

**Best Practices**:
- Cast a wide net initially
- Use data maps from information governance
- Consider non-custodial data sources
- Identify key players early
- Document all data sources considered
- Assess proportionality early

### 3. Preservation

**Purpose**: Ensure potentially relevant ESI is protected from alteration or destruction

**Key Activities**:
- Issue legal hold notices
- Suspend auto-delete and retention policies
- Implement litigation hold on systems
- Monitor custodian compliance
- Re-issue holds as needed
- Document preservation efforts

**Deliverables**:
- Legal hold notices
- Custodian acknowledgments
- Preservation order documentation
- Litigation hold audit trails
- Preservation certificates

**Best Practices**:
- Act quickly to prevent spoliation
- Use clear, understandable hold notices
- Track acknowledgments and follow up
- Suspend all automated deletion
- Document chain of custody
- Maintain holds until official release
- Over-preserve rather than under-preserve

### 4. Collection

**Purpose**: Gather ESI from identified sources in a forensically sound manner

**Key Activities**:
- Develop collection plan and methodology
- Obtain necessary access and permissions
- Use forensically sound collection tools
- Collect from diverse sources (email, files, cloud, mobile)
- Document collection process
- Verify completeness and integrity

**Deliverables**:
- Collection methodology documentation
- Forensic images or logical collections
- Collection reports and logs
- Chain of custody forms
- Hash values for verification
- Collection certifications

**Best Practices**:
- Use certified collection tools
- Preserve metadata and system information
- Document collection parameters
- Verify data integrity (hash validation)
- Maintain strict chain of custody
- Consider privacy and privilege during collection
- Test collection process before execution

**Collection Methods**:
- **Forensic imaging**: Bit-by-bit copy of entire drive
- **Logical collection**: Selective file collection
- **Remote collection**: Network-based collection tools
- **Cloud collection**: API-based extraction
- **Mobile collection**: Device extraction tools
- **Database extraction**: Structured data queries

### 5. Processing

**Purpose**: Reduce data volume and prepare ESI for review

**Key Activities**:
- Extract text and metadata from native files
- Perform de-duplication (exact and near-duplicate)
- Apply email threading
- Filter by date, custodian, file type, keywords
- Perform OCR on images
- Normalize file formats
- Expand compressed files
- Handle password-protected files

**Deliverables**:
- Processed data ready for review
- Processing reports and statistics
- Exception reports (errors, encrypted files)
- De-duplication reports
- Metadata extraction results
- OCR quality reports

**Best Practices**:
- Use industry-standard processing tools
- Perform global de-duplication
- Apply email threading for efficiency
- Perform comprehensive metadata extraction
- Use high-quality OCR settings
- Document all processing steps
- Validate processing completeness
- Preserve original native files

**Processing Techniques**:

**De-duplication**:
- Exact duplicate (MD5/SHA-256 hash matching)
- Global vs. custodial de-duplication
- Near-duplicate detection (similarity algorithms)
- Attachment de-duplication

**Email Threading**:
- Identify inclusive emails (contain all prior messages)
- Group related emails into conversations
- Reduce review volume significantly
- Maintain context and readability

**Data Culling**:
- Date filtering
- File type filtering
- Custodian filtering
- Keyword filtering (with caution)
- Size filtering (very small or very large files)

### 6. Review

**Purpose**: Identify responsive, privileged, and confidential documents

**Key Activities**:
- Design review workflow and protocols
- Configure review platform
- Assign documents to reviewers
- Code documents (responsive, privileged, confidential)
- Perform privilege review
- Conduct quality control
- Create privilege logs
- Escalate complex documents

**Deliverables**:
- Review platform database
- Coded document sets
- Privilege log
- Review protocols and training materials
- Quality control reports
- Production sets

**Best Practices**:
- Use consistent coding protocols
- Provide comprehensive reviewer training
- Implement multiple review passes for privilege
- Conduct ongoing QC and calibration
- Use technology to prioritize review
- Document all review decisions
- Maintain reviewer notes for complex documents

**Review Workflows**:
- **Linear review**: Document-by-document review
- **Prioritized review**: Using analytics to prioritize
- **TAR/Predictive coding**: Machine learning-assisted review
- **Keyword review**: Focusing on keyword hits
- **Concept review**: Clustering similar documents
- **Issue-based review**: Organizing by legal issues
- **Custodian-based review**: Reviewing by person

### 7. Analysis

**Purpose**: Evaluate ESI to understand case facts, develop strategy, and identify key documents

**Key Activities**:
- Perform early case assessment (ECA)
- Apply analytics (clustering, concept search, threading)
- Identify hot documents and key evidence
- Analyze communication patterns
- Create timelines and chronologies
- Perform link analysis
- Identify gaps in evidence
- Support fact development

**Deliverables**:
- ECA reports and insights
- Hot document lists
- Communication pattern analyses
- Chronologies and timelines
- Visual analytics (network graphs, heat maps)
- Case strategy recommendations

**Best Practices**:
- Perform ECA early to inform strategy
- Use multiple analytical approaches
- Involve case team in analysis
- Validate findings with manual review
- Document analytical methods used
- Preserve analytical work product
- Use visualizations to communicate findings

**Analytical Tools**:
- Concept clustering
- Email threading and communication analysis
- Timeline visualization
- Network/relationship graphs
- Sentiment analysis
- Language and entity detection
- Repeated content identification
- Anomaly detection

### 8. Production

**Purpose**: Deliver responsive documents to opposing parties or government agencies

**Key Activities**:
- Negotiate production format and specifications
- Apply privilege withholdings
- Apply redactions
- Create production sets
- Generate load files (DAT, OPT)
- Apply Bates numbering
- Add confidentiality designations
- Package and deliver production
- Create production logs

**Deliverables**:
- Produced documents (native, TIFF, PDF)
- Load files (DAT, OPT, XML)
- Privilege log
- Production cover letter
- Production log/tracking sheet
- Redaction log (if applicable)
- Production verification reports

**Best Practices**:
- Clearly document production specifications
- Perform thorough QC before production
- Validate load files and images
- Test productions before delivery
- Maintain detailed production logs
- Secure delivery method (encryption)
- Retain copies of all productions
- Document any errors and corrections

**Production Formats**:
- **Native**: Original application format
- **TIFF**: Multi-page image format with load files
- **PDF**: Searchable or image-based PDFs
- **Hybrid**: Combination of native and images
- **Paper**: Hard copy production (rarely used)

### 9. Presentation

**Purpose**: Display ESI effectively during depositions, hearings, and trials

**Key Activities**:
- Organize exhibits and evidence
- Prepare document bundles for depositions
- Set up trial presentation technology
- Create demonstrative exhibits
- Enable real-time document display
- Support attorney presentation needs
- Coordinate with court technology
- Manage exhibit lists and admissions

**Deliverables**:
- Organized exhibit databases
- Deposition exhibit books
- Trial presentation software setup
- Demonstrative exhibits
- Exhibit lists and logs
- Courtroom technology setup

**Best Practices**:
- Organize documents intuitively
- Test technology before proceedings
- Have backup plans for technology failures
- Coordinate with court personnel
- Prepare exhibits well in advance
- Enable quick document retrieval
- Support real-time adjustments
- Document all exhibits used

## EDRM Model Characteristics

### Iterative and Flexible
- Stages can overlap and repeat
- Not necessarily sequential
- Adjust based on case needs
- Return to earlier stages as needed

### Volume and Cost Considerations
- Volume is highest at information governance
- Volume decreases through processing and review
- Costs are highest during review
- Early culling reduces downstream costs

### Proportionality
- Align effort with case value and needs
- Consider burden vs. benefit
- Apply Rule 26(b)(1) proportionality factors
- Use technology to reduce costs

### Cooperation
- Work with opposing counsel on ESI issues
- Negotiate protocols early (Rule 26(f))
- Share information about processes
- Resolve disputes collaboratively

## EDRM Updates and Evolution

### EDRM 2.0 Developments
- Information governance emphasis
- Privacy and data protection integration
- Cloud and mobile data considerations
- AI and analytics advancement
- International and cross-border issues

### Modern Additions
- Data privacy and protection stage
- Information governance prominence
- Analytics throughout lifecycle
- Continuous improvement mindset

## Key Metrics by Stage

### Information Governance
- Data sources inventoried
- Retention policies implemented
- Custodian compliance rate
- Legal hold response time

### Collection
- Data volume collected
- Collection cost per GB
- Collection time per custodian
- Collection error rate

### Processing
- De-duplication rate
- Processing cost per GB
- OCR accuracy rate
- Processing time per GB

### Review
- Documents reviewed per hour
- Review cost per document
- First-pass accuracy rate
- Privilege identification rate

### Production
- Production volume
- Production cost per document
- Production error rate
- Time to production

## Resources

- **EDRM Website**: edrm.net
- **EDRM Guides**: Comprehensive guides for each stage
- **EDRM Metrics**: Model for measuring e-discovery performance
- **EDRM Directory**: Vendor and service provider listings
- **EDRM Projects**: Working groups on specialized topics

## Conclusion

The EDRM framework provides a comprehensive roadmap for e-discovery from information governance through presentation. Understanding and applying EDRM principles ensures efficient, defensible, and cost-effective e-discovery processes.

# Data Collection Best Practices

## Pre-Collection Preparation

### Data Source Identification
- Email servers (Exchange, Gmail, etc.)
- File shares and network drives
- Cloud storage systems (SharePoint, OneDrive, Box)
- Mobile devices and external drives
- Databases and enterprise systems
- Backup and archival systems

### Custodian Management
- Interview custodians about data locations
- Identify overlapping data sources
- Document data access permissions
- Note data retention policies
- Flag sensitive or restricted data

### Legal Hold Implementation
- Issue litigation hold notices
- Obtain custodian acknowledgments
- Implement technical holds where necessary
- Monitor for hold compliance
- Document hold timeline

## Collection Methodologies

### Live Collection
- Collect from active systems
- Minimal processing overhead
- Real-time integrity verification
- Best for frequently accessed data
- May require scheduled downtime

### Snapshot Collection
- Image entire drives/partitions
- Preserves complete file system
- Allows forensic analysis
- More storage intensive
- Useful for comprehensive collection

### API-Based Collection
- Direct integration with platforms
- Efficient for cloud systems
- Better metadata preservation
- Requires system access
- Scalable for large volumes

## Collection Standards

### Metadata Preservation
- File creation, modification, access dates
- Author and last modified by information
- File size and format
- Storage location and path
- Custodian assignment

### Chain of Custody
- Document all handlers
- Record collection methodology
- Timestamp all activities
- Maintain collection logs
- Verify data integrity with hash values

### Documentation Requirements
- Collection procedure documentation
- Systems and custodians covered
- Data source descriptions
- Collection date and timeframe
- Searcher names and qualifications
- Certification of completeness

## Quality Assurance

### Validation Steps
1. Verify collection completeness
2. Check file integrity (hash verification)
3. Validate metadata extraction
4. Test search functionality
5. Document any collection issues

### Common Collection Challenges
- Corrupted files and formats
- Encryption and password protection
- Fragmented or partially deleted data
- Large file repositories
- Foreign language content

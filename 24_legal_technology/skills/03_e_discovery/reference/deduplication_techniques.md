# E-Discovery Deduplication Techniques

## Overview

Deduplication is the process of identifying and eliminating duplicate documents in an e-discovery collection. It significantly reduces data volume, review costs, and processing time while maintaining one representative copy of each unique document. Proper deduplication is essential for cost-effective and efficient e-discovery.

## Why Deduplicate?

### Cost Reduction

- **Review Savings**: Review only unique documents once
- **Processing Efficiency**: Reduce processing time and storage
- **Hosting Costs**: Lower costs for hosted review platforms
- **Production Efficiency**: Smaller production volumes

### Typical Savings

- **Email Systems**: 30-50% reduction (high duplication)
- **File Shares**: 20-40% reduction
- **Overall Collections**: 25-45% average reduction
- **Large Organizations**: Higher deduplication rates

### Efficiency Benefits

- Faster review completion
- Improved consistency (same document coded once)
- Reduced reviewer fatigue
- Better analytics results

## Deduplication Methods

### 1. Exact Duplicate Detection (Hash-Based)

**Methodology**:
- Calculate cryptographic hash (MD5, SHA-1, SHA-256) for each file
- Compare hash values
- Files with identical hashes are exact duplicates
- Keep one copy, mark others as duplicates

**Hash Algorithms**:

**MD5 (Message Digest 5)**:
- 128-bit hash value
- Faster computation
- Most common in e-discovery
- Collision risk (theoretical, rare in practice)
- Example: `5d41402abc4b2a76b9719d911017c592`

**SHA-1 (Secure Hash Algorithm 1)**:
- 160-bit hash value
- More secure than MD5
- Still widely used
- Deprecated for cryptographic security
- Example: `356a192b7913b04c54574d18c28d46e6395428ab`

**SHA-256**:
- 256-bit hash value
- Most secure
- Slower computation
- Increasingly used in e-discovery
- Example: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

**Advantages**:
- 100% accurate (no false positives)
- Fast computation
- Industry standard
- Defensible methodology

**Limitations**:
- Any change to file creates new hash (even metadata change)
- Different file formats of same content have different hashes
- Embedded metadata differences create unique hashes

**Best Practice**: Use MD5 for speed and industry acceptance, unless security concerns require SHA-256

### 2. Global vs. Custodial Deduplication

**Global Deduplication**:

**Definition**: De-duplicate across entire collection, regardless of custodian

**Process**:
1. Calculate hash for all documents
2. Identify duplicates across all custodians
3. Keep one "master" copy
4. All other copies marked as duplicates
5. Track which custodians had each document

**Advantages**:
- Maximum volume reduction
- Single review per unique document
- Most cost-effective
- Simpler review workflow

**Disadvantages**:
- Loses custodian context for duplicates
- May need to track all custodians who had document
- Potential issues for proving possession by specific person

**Metadata Tracking**:
- Master document retains one custodian
- Duplicate custodian field lists all custodians with copy
- Duplicate count field shows total copies
- Duplicate IDs list all duplicate document IDs

**Custodial Deduplication**:

**Definition**: De-duplicate only within each custodian's data

**Process**:
1. Group documents by custodian
2. Calculate hash within each custodian group
3. Keep one copy per custodian
4. Mark duplicates only within same custodian

**Advantages**:
- Maintains custodian context
- Shows each person who possessed document
- Useful for proving knowledge or possession
- Preserves different metadata (dates) per custodian

**Disadvantages**:
- Less volume reduction
- Same document reviewed multiple times
- Higher costs
- More complex analytics

**When to Use**:
- Small custodian pools
- Possession/knowledge is key issue
- Metadata variations are important
- Client prefers preserving all copies

**Hybrid Approach**:
- Global deduplication for most documents
- Custodial deduplication for key custodians
- Flexibility based on case needs

### 3. Near-Duplicate Detection

**Definition**: Identification of documents that are very similar but not identical

**Use Cases**:
- Email chains with slight additions
- Document versions with minor edits
- Email signature variations
- Forwarded emails with added text

**Algorithms**:

**Shingling**:
- Break document into overlapping sequences (shingles)
- Typically 5-10 word sequences
- Calculate hash of each shingle
- Compare shingle sets between documents
- Similarity score = percentage of matching shingles

**Example**:
```
Document A: "The quick brown fox jumps over the lazy dog"
Shingles (3-word):
- "The quick brown"
- "quick brown fox"
- "brown fox jumps"
- "fox jumps over"
- etc.
```

**Fingerprinting**:
- Create document "fingerprint" from key features
- Compare fingerprints
- Similarity scoring
- Faster than full text comparison

**Fuzzy Hashing (ssdeep)**:
- Context-triggered piecewise hashing
- Detects similar files even with insertions/deletions
- Used in forensics and malware analysis

**Similarity Thresholds**:
- **90-95%**: Very similar, likely email chains or minor edits
- **80-90%**: Similar, possibly different versions
- **70-80%**: Somewhat similar, may be related
- **<70%**: Different documents

**Review Strategies**:
- Review principal (most complete) document
- Quick-review near-duplicates for differences
- Identify "inclusive" documents (contain all prior content)
- Focus on unique content only

**Advantages**:
- Further reduces review volume (30-50% additional reduction)
- Identifies related documents
- Handles email chains efficiently
- Finds document versions

**Challenges**:
- Requires more processing power
- Similarity threshold selection is subjective
- False positives possible
- Must validate methodology

### 4. Email Threading

**Definition**: Group related emails into conversations and identify inclusive emails

**Process**:
1. Analyze email headers (Message-ID, In-Reply-To, References)
2. Parse email content for quoted text
3. Group emails into conversation threads
4. Identify inclusive emails (contain all prior messages)
5. Mark non-inclusive emails as duplicative

**Thread Analysis**:
```
Email 1: Original message
Email 2: Reply to Email 1 (includes Email 1 text)
Email 3: Reply to Email 2 (includes Email 1 + Email 2)
Email 4: Another reply to Email 1
Thread: Emails 1-4 grouped together
Inclusive: Email 3 (contains all prior content)
```

**Metadata Used**:
- Message-ID: Unique identifier for each email
- In-Reply-To: ID of email being replied to
- References: Chain of related message IDs
- Subject line (with Re:, Fwd: parsing)
- Date/time sent
- Quoted text markers (">")

**Benefits**:
- Reduces email review by 50-80%
- Maintains conversation context
- Shows email evolution over time
- Identifies key communication points

**Review Approach**:
- Review only inclusive emails
- Quick-check non-inclusive for unique content
- Understand conversation flow
- Focus on new information

**Challenges**:
- Threading algorithms vary by platform
- Subject line changes break threads
- Forward vs. reply differences
- Email client variations

**Platform Implementations**:
- Relativity: Structured Analytics threading
- Nuix: Email threading module
- Everlaw: Automatic threading
- Brainspace: Communication analysis

## Deduplication Strategies by Data Type

### Email (PST, MSG, EML)

**High Duplication Expected**: 30-60%

**Strategy**:
- Global deduplication (MD5 hash)
- Email threading
- Include attachments in hash or separate
- Consider near-duplicate detection
- Track sent vs. received copies

**Considerations**:
- Email header variations (Received headers differ)
- Sent items vs. received items (same message, different metadata)
- Attachment handling (include in hash or deduplicate separately)

### Office Documents (Word, Excel, PowerPoint)

**Moderate Duplication**: 20-40%

**Strategy**:
- Global deduplication
- Consider near-duplicate for versioning
- Application metadata changes create unique hashes
- Track document versions

**Considerations**:
- Metadata changes (last modified date, author)
- Embedded objects and macros
- Template-based documents

### PDF Files

**Lower Duplication**: 15-30%

**Strategy**:
- Hash-based deduplication
- OCR text may vary (don't include in hash)
- Near-duplicate for scanned versions

**Considerations**:
- Native PDF vs. converted
- OCR variations
- PDF version differences

### Compressed Archives (ZIP, RAR)

**Strategy**:
- Hash entire archive as one file
- OR expand and deduplicate contents
- Document approach

**Trade-offs**:
- Hashing archive: Fast but misses duplicate contents
- Expanding: Finds more duplicates but slower

### Attachments

**Strategy Option 1: Include in Parent Hash**
- Email + attachments hashed together
- Email with different attachment = unique

**Strategy Option 2: Separate Hashing**
- Email body hashed separately
- Attachments hashed separately
- Greater deduplication, more complexity

**Best Practice**: Separate attachment deduplication (more reduction)

## Deduplication Workflow

### 1. Pre-Processing Planning

**Decisions**:
- Global vs. custodial deduplication
- Hash algorithm (MD5, SHA-256)
- Near-duplicate threshold
- Email threading approach
- Attachment handling
- Metadata to preserve

**Documentation**:
- Deduplication methodology
- Algorithms and thresholds
- Justification for approach
- Validation plan

### 2. Processing Configuration

**Settings**:
- Enable deduplication
- Select hash algorithm
- Configure near-duplicate detection
- Set similarity threshold
- Enable email threading
- Attachment options

**Validation**:
- Test with sample data
- Verify results match expectations
- Check metadata preservation
- Confirm duplicate tracking

### 3. Execution

**Process**:
- Calculate hashes for all documents
- Identify exact duplicates
- Run near-duplicate detection
- Execute email threading
- Generate reports
- Validate results

**Quality Control**:
- Verify hash calculation
- Spot-check duplicate groups
- Validate near-duplicate clustering
- Confirm thread relationships
- Review exceptions and errors

### 4. Documentation

**Capture**:
- Total documents processed
- Exact duplicates found (count and percentage)
- Near-duplicates identified
- Email threads created
- Final document count for review
- Deduplication reports

**Reporting**:
```
Processing Summary:
- Total Documents: 500,000
- After Exact Deduplication: 350,000 (30% reduction)
- After Near-Duplicate: 280,000 (20% additional reduction)
- After Email Threading: 200,000 (29% additional reduction)
- Final Review Volume: 200,000 (60% overall reduction)
```

## Metadata for Deduplication

### Master Document Fields

- **Document ID**: Unique identifier
- **MD5 Hash**: Hash value
- **Duplicate Count**: Number of copies found
- **Duplicate Status**: Master / Original
- **Custodians**: All custodians who had document

### Duplicate Document Fields

- **Document ID**: Unique identifier for duplicate
- **MD5 Hash**: Same as master
- **Duplicate Status**: Duplicate
- **Duplicate of**: Master document ID
- **Custodian**: Custodian of this specific copy
- **Suppressed**: Hidden from review (optional)

### Near-Duplicate Fields

- **Near Duplicate Group**: Group identifier
- **Principal Document**: Most complete document in group
- **Similarity Percentage**: Similarity to principal
- **Unique Content**: Has unique content flag

### Email Threading Fields

- **Thread ID**: Conversation identifier
- **Inclusive Email**: Contains all prior messages
- **Thread Position**: Order in conversation
- **Thread Depth**: Level in thread hierarchy

## Quality Control

### Validation Checklist

- [ ] Hash algorithm documented
- [ ] Deduplication type (global/custodial) documented
- [ ] Sample verification performed
- [ ] Duplicate counts accurate
- [ ] Metadata preserved correctly
- [ ] Master document selection appropriate
- [ ] Custodian tracking accurate
- [ ] Duplicate relationships correct
- [ ] Near-duplicate threshold justified
- [ ] Threading results validated

### Testing

**Sample Testing**:
1. Manually identify known duplicate set
2. Verify system identifies as duplicates
3. Check correct master selection
4. Validate metadata preservation
5. Confirm hash calculations

**Edge Cases**:
- Documents with only metadata differences
- Emails with minimal content differences
- Attachments with same name, different content
- Threading of forwarded vs. replied emails

## Legal and Defensibility Considerations

### Court Acceptance

**Deduplication is Widely Accepted**:
- Industry standard practice
- Courts routinely approve
- Sedona Conference Best Practices endorse
- Must be defensible and documented

**Requirements**:
- Use accepted algorithms (MD5, SHA-256)
- Document methodology
- Preserve metadata showing duplicates
- Make duplicates accessible if requested
- Explain approach to opposing counsel

### Cooperation

**Discuss with Opposing Counsel**:
- Deduplication approach (global vs. custodial)
- Algorithm used
- Metadata preservation
- Accessibility of duplicates
- Near-duplicate methodology

**Rule 26(f) Conference**:
- Include deduplication in ESI protocol
- Agreement on approach
- Document in discovery plan

### Preservation of Duplicates

**Maintain Access**:
- Retain all copies in processing database
- Make available upon request
- Document where duplicates are stored
- Provide duplicate metadata if requested

## Platform-Specific Deduplication

### Relativity

- **Invariant Processing**: MD5 hash-based deduplication
- **Global Deduplication**: Across entire workspace
- **Duplicate Spare Field**: Tracks original
- **Analytics**: Near-duplicate detection via structured analytics
- **Email Threading**: Built-in threading

### Nuix

- **MD5, SHA-1, SHA-256**: Multiple hash options
- **Global and Custodial**: Configurable
- **Near-Duplicate Shingling**: Advanced similarity detection
- **Email Threading**: Conversation analysis
- **Scripting**: Custom deduplication logic

### Everlaw

- **Automatic Deduplication**: Built-in MD5 hashing
- **Near-Duplicate Detection**: Similarity analysis
- **Email Threading**: Automatic threading
- **Cloud Processing**: Fast deduplication

## Common Issues and Solutions

### Issue: Metadata Variations Create False Uniques

**Problem**: Files with only metadata differences treated as unique

**Solutions**:
- Hash file content only (exclude metadata)
- Normalize metadata before hashing
- Use near-duplicate detection
- Accept as limitation and document

### Issue: Attachment Deduplication Inconsistent

**Problem**: Same attachment in multiple emails not deduplicated

**Solutions**:
- Configure separate attachment deduplication
- Hash attachments independently
- Document approach

### Issue: Email Threading Errors

**Problem**: Emails incorrectly grouped or separated

**Solutions**:
- Validate threading algorithm
- Manual review of sample threads
- Accept limitations of automatic threading
- Document methodology

### Issue: Too Aggressive Deduplication

**Problem**: Important differences missed by near-duplicate detection

**Solutions**:
- Adjust similarity threshold
- Review principal and near-duplicates
- Document unique content in near-duplicates
- Produce all if differences material

## Best Practices

1. **Plan Early**: Decide deduplication approach before processing
2. **Document Thoroughly**: Record methodology and decisions
3. **Validate Results**: Spot-check duplicate groups
4. **Preserve Metadata**: Track all duplicate relationships
5. **Communicate**: Discuss with opposing counsel
6. **Make Accessible**: Ensure duplicates can be retrieved if needed
7. **Use Standards**: Stick to accepted algorithms and practices
8. **Consider Case Needs**: Tailor approach to case requirements
9. **Balance Reduction and Accuracy**: Don't over-deduplicate
10. **Test First**: Validate on sample before full processing

## Resources

### Standards

- EDRM Deduplication Guidelines
- Sedona Conference Best Practices Commentary
- NIST Digital Forensics Standards

### Tools

- Processing platforms (Relativity, Nuix, Everlaw)
- Standalone deduplication tools
- Hash calculation utilities

### Research

- Academic papers on deduplication algorithms
- E-discovery vendor white papers
- Case law on deduplication acceptance

## Conclusion

Deduplication is a critical component of cost-effective e-discovery. Proper use of hash-based deduplication, near-duplicate detection, and email threading can reduce review volumes by 50-80% while maintaining defensibility. Understanding deduplication methodologies, implementing them correctly, and documenting thoroughly ensures efficient and defensible e-discovery processes.

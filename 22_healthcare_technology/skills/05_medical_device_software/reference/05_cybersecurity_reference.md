# Medical Device Software Cybersecurity Reference

## FDA Cybersecurity Guidance

### Premarket Cybersecurity
Required documentation in regulatory submission:

1. **Threat Modeling**
   - Identification of potential attackers
   - Attack vectors and methods
   - Impact of successful attacks
   - Examples: Man-in-the-middle, buffer overflow, SQL injection

2. **Cybersecurity Risk Assessment**
   - Risk matrix: likelihood vs. impact
   - Residual risk after controls
   - Risk-benefit analysis
   - Executive sign-off

3. **Security Control Implementation**
   - Specific controls addressing threats
   - How each control mitigates risk
   - Implementation details
   - Verification that controls work

4. **Vulnerability Assessment**
   - Code analysis: static and dynamic testing
   - Penetration testing by qualified team
   - OWASP Top 10 coverage
   - Known vulnerabilities in dependencies

5. **Software Bill of Materials (SBOM)**
   - All software components and versions
   - Third-party libraries and licenses
   - Known vulnerabilities
   - Patch status

### Postmarket Cybersecurity
- Vulnerability monitoring and patching
- Coordinated disclosure process
- Security update deployment mechanism
- Monitoring for actual exploits
- Incident response plan

## Threat Modeling Approach

### Step 1: Asset Identification
- Patient data (PHI/PII)
- Medical device firmware
- Clinical algorithms
- User credentials
- Device control capabilities

### Step 2: Threat Actor Identification
- **Motivated Insiders**: Disgruntled employees
- **External Attackers**: Financial gain, espionage, notoriety
- **Competitors**: Steal intellectual property
- **Nation States**: Espionage, sabotage (for critical infrastructure)
- **Script Kiddies**: Using existing exploit tools

### Step 3: Attack Vector Identification
Using STRIDE model:
- **Spoofing** (identity): Attacker impersonates legitimate user
- **Tampering** (data): Modifying data in transit or at rest
- **Repudiation**: Denying actions were performed
- **Information Disclosure**: Unauthorized access to sensitive data
- **Denial of Service**: Making system unavailable
- **Elevation of Privilege**: Gaining unauthorized access level

### Step 4: Risk Assessment
- Likelihood: How probable is successful attack?
- Impact: What damage if attack succeeds?
- Risk = Likelihood × Impact
- Severity: Critical (infrastructure impact), Major (patient harm), Moderate, Low

### Step 5: Control Selection
For each threat:
1. **Prevention**: Eliminate the vulnerability
2. **Detection**: Identify attack in progress
3. **Response**: Limit damage and recover
4. **Mitigation**: Accept risk and document

## Security Controls

### Authentication
- **Requirement**: Users must prove identity
- **Multifactor Authentication**: Something you know (password) + something you have (token)
- **Session Management**: Timeout, logout capabilities
- **Password Policy**: Minimum length, complexity, rotation
- **API Keys**: For service-to-service authentication
- **OAuth/OpenID**: For third-party integrations

### Authorization
- **Role-Based Access Control (RBAC)**: Different user roles with different permissions
- **Principle of Least Privilege**: Users have minimum needed permissions
- **Resource Permissions**: Fine-grained control over what each role can access
- **Segregation of Duties**: Sensitive operations require multiple approvals
- **Audit Trail**: Log all access to sensitive functions

### Data Protection
- **Encryption in Transit**: HTTPS/TLS for all network communication
- **Encryption at Rest**: Database encryption, file encryption
- **Cryptographic Standards**: AES-256, SHA-256 minimum
- **Key Management**: Secure storage, rotation procedures
- **De-identification**: Remove PHI when not needed
- **Data Classification**: Know what data is sensitive

### Input Validation
- **Whitelisting**: Accept only known good input patterns
- **Type Checking**: Ensure correct data types
- **Length Limits**: Prevent buffer overflows
- **SQL Injection Prevention**: Parameterized queries, prepared statements
- **Cross-Site Scripting (XSS) Prevention**: HTML encoding, Content Security Policy
- **Command Injection Prevention**: Avoid shell commands with user input

### Error Handling
- **Fail Secure**: Errors don't expose functionality
- **Generic Error Messages**: Don't reveal system internals
- **Logging**: Detailed internal logging, generic user messages
- **No Sensitive Data in Logs**: Never log passwords, PHI
- **Exception Handling**: Graceful degradation, no crashes

### Software Security Practices

#### Secure Development Lifecycle (SDL)
1. **Threat Modeling**: Before coding
2. **Code Review**: Peer review and security review
3. **Static Analysis**: Automated scanning for vulnerabilities
4. **Dynamic Testing**: Runtime security testing
5. **Penetration Testing**: Simulated attacks
6. **Dependency Scanning**: Vulnerable libraries
7. **Training**: Team understands secure coding

#### Code Review Checklist
- Input validation implemented
- No hardcoded credentials
- Proper error handling
- No buffer overflows or overruns
- Cryptography used correctly
- Access controls enforced
- Logging doesn't expose secrets
- No SQL injection possibilities
- OWASP Top 10 issues avoided

#### Common Vulnerabilities (OWASP Top 10)
1. **Injection**: SQL, OS command, LDAP
2. **Broken Authentication**: Weak session management
3. **Sensitive Data Exposure**: Encryption not used properly
4. **XML External Entities (XXE)**: Malicious XML parsing
5. **Broken Access Control**: Authorization failures
6. **Security Misconfiguration**: Default credentials, exposed services
7. **Cross-Site Scripting (XSS)**: JavaScript in browsers
8. **Insecure Deserialization**: Untrusted object deserialization
9. **Using Components with Known Vulnerabilities**: Unpatched libraries
10. **Insufficient Logging & Monitoring**: Can't detect attacks

## Supply Chain Security

### Third-Party Software Risk
- **Identify All Dependencies**: npm packages, libraries, frameworks
- **Assess Trustworthiness**: Is vendor reputable? Active maintenance?
- **Vulnerability Scanning**: Use tools to identify known vulnerabilities
- **License Compliance**: Ensure license compatibility
- **Source Code Review**: For critical components, review source
- **Version Pinning**: Don't auto-update to untrusted versions

### Software Bill of Materials (SBOM)
Document for each dependency:
- Component name and version
- Publisher/vendor
- Component hash (for integrity verification)
- Known vulnerabilities
- License information
- Security advisories

### Patch Management
- **Monitoring**: Track security updates from vendors
- **Assessment**: Determine severity and applicability
- **Testing**: Verify patch doesn't break functionality
- **Deployment**: Roll out patches in staged manner
- **Validation**: Confirm patch applied and working
- **Rollback**: Ability to revert if problems occur

## Vulnerability Management

### Vulnerability Identification
1. **Static Analysis**: Code scanning tools
   - FindBugs, SonarQube, Fortify
   - Identify potential vulnerabilities
   
2. **Dynamic Analysis**: Runtime testing
   - Fuzzing, stress testing
   - Find crashes, unexpected behavior

3. **Penetration Testing**: Simulated attacks
   - Security professionals attempt to break in
   - Real-world attack scenarios
   - Proof of concept exploits

4. **Code Review**: Human expert review
   - Catch issues tools miss
   - Review design decisions
   - Verify correct implementation

### Vulnerability Scoring (CVSS)
- **CVSS Score**: 0-10 scale quantifying severity
- **Critical** (9-10): Exploit available, significant impact
- **High** (7-9): Serious vulnerability requiring quick fix
- **Medium** (4-7): Should be fixed, not immediately critical
- **Low** (0-4): Minor issue, can be fixed in normal cycle

### Remediation Priority
1. **Critical**: 30 days to patch
2. **High**: 60 days to patch
3. **Medium**: 90 days to patch
4. **Low**: Next planned release

### Vulnerability Tracking
- Central registry of all identified issues
- Status: Identified → Assigned → Fixed → Tested → Deployed
- Closure verification and sign-off
- Traceability to regulatory documentation

## Secure Update Mechanism

### Requirements for Secure Updates
- **Authentication**: Verify update source
- **Integrity**: Ensure update not tampered with
- **Encryption**: Protect update in transit
- **Rollback**: Ability to revert to previous version
- **Testing**: Updates tested before deployment
- **Staged Rollout**: Phased deployment to detect problems
- **User Notification**: Clear communication about updates
- **Logs**: Records of what changed, when, by whom

### Update Deployment Strategy
1. **Staged Rollout**
   - Phase 1: 10% of user base
   - Phase 2: 50% if phase 1 successful
   - Phase 3: 100% deployment

2. **Monitoring During Rollout**
   - Error rates, crash reports
   - Performance metrics
   - User feedback
   - Ready to rollback

3. **Post-Deployment**
   - Confirm all users updated
   - Monitor for issues
   - Document what changed
   - Regulatory reporting if needed

## Cybersecurity Testing

### Code Analysis Tools
- **Static**: Fortify, SonarQube, Checkmarx
- **Dynamic**: OWASP ZAP, Burp Suite
- **Dependency**: Dependabot, Snyk, WhiteSource
- **Runtime**: Application security testing (AST)

### Penetration Testing Scope
- **Network Testing**: Can attackers access system?
- **Web Application Testing**: OWASP Top 10 coverage
- **API Testing**: Authentication, authorization, injection
- **Cryptography**: Proper use of encryption
- **Authentication**: Can attackers bypass login?
- **Authorization**: Can users access unauthorized resources?
- **Data Security**: Can PHI be stolen?

### Testing Documentation
- Test methodology and approach
- Tools and versions used
- Credentials/access used
- Vulnerabilities found and severity
- Proof of concept (if applicable)
- Recommendations for fixes
- Verification that fixes work

## Incident Response Plan

### Four Phases

**1. Preparation**
- Incident response team designated
- Communication procedures
- 24/7 contact information
- Tools and access prepared

**2. Detection and Analysis**
- Monitor logs for suspicious activity
- Analyze alerts and incidents
- Determine scope and severity
- Classification: Is this a security incident?

**3. Containment, Eradication, Recovery**
- Isolate affected systems
- Preserve evidence
- Remove attacker access
- Patch vulnerabilities
- Restore systems
- Verify no lingering backdoors

**4. Post-Incident Activities**
- Root cause analysis
- Document lessons learned
- Communicate with affected parties
- Regulatory reporting (if required)
- Process improvements

## FDA Cybersecurity Submission Content

### Required Documentation
1. Threat Model (1-2 pages executive summary)
2. Security Risk Assessment
3. Security Control Implementation Plan
4. Security Testing Summary
5. SBOM with known vulnerabilities
6. Patch Management Procedures
7. Vulnerability Disclosure Policy
8. Incident Response Plan

### Common Deficiencies
1. Threat model too generic or superficial
2. Controls not actually implemented
3. Insufficient testing evidence
4. No SBOM or incomplete SBOM
5. Weak patch procedures
6. No vulnerability disclosure policy
7. Patient data not adequately protected
8. Third-party components not assessed

## Compliance Frameworks

### FDA Requirements (Premarket and Postmarket)
- Threat modeling and assessment
- Vulnerability management procedures
- Security testing documentation
- SBOM submission
- Patch management plan

### HIPAA Security Rule (if applicable)
- Access controls
- Audit and accountability
- Encryption and decryption
- Transmission security

### NIST Cybersecurity Framework
- Identify: Asset inventory and risk
- Protect: Access control and encryption
- Detect: Security monitoring
- Respond: Incident response
- Recover: Continuity and restoration

### IEC 62271 (Medical Device Cybersecurity)
- Network security
- Authentication and access control
- Security patches and updates
- System monitoring and logging

# Technical Safeguards Implementation Guide

## Overview
Technical safeguards are technology and the policy and procedures for its use that protect ePHI and control access to it.

**Regulatory Basis:** 45 CFR §164.312

## 1. Access Control (§164.312(a)(1)) - REQUIRED

### Unique User Identification (Required)
**Implementation:**
- No shared accounts (except break-glass)
- UserID format: firstname.lastname
- Service accounts documented separately
- Never reuse user IDs

### Emergency Access Procedure (Required)
**Break-Glass Accounts:**
- 2-3 emergency accounts (break-glass-01, break-glass-02)
- Credentials in sealed envelope
- Stored in secure location (safe)
- All usage logged and reviewed
- Requires post-use justification

### Automatic Logoff (Addressable)
**Implementation:**
- Inactivity timeout: 15 minutes maximum
- Screen lock: 5 minutes
- Apply via Group Policy (Windows) or MDM
- Cannot be disabled by end users

### Encryption (Addressable)
**Data at Rest:**
- Full disk encryption: BitLocker (Windows), FileVault (Mac)
- Database encryption: TDE (Transparent Data Encryption)
- File-level encryption for sensitive documents
- AES-256 minimum

**Data in Transit:**
- TLS 1.2 or higher (disable older versions)
- VPN for remote access (AES-256)
- Secure email (S/MIME or encrypted portal)
- SFTP for file transfers (not FTP)

## 2. Audit Controls (§164.312(b)) - REQUIRED

**What to Log:**
- All PHI access (create, read, update, delete)
- User authentication (success/failure)
- Administrative actions
- Permission changes
- System configuration changes

**Log Requirements:**
- User ID, timestamp, action, patient ID
- Tamper-resistant storage
- Retention: 6 years minimum
- Centralized log management (SIEM)

## 3. Integrity (§164.312(c))

**Mechanisms:**
- Checksums for data validation
- Digital signatures for documents
- Version control
- Change detection systems
- Database integrity constraints

## 4. Person/Entity Authentication (§164.312(d)) - REQUIRED

**Multi-Factor Authentication (MFA):**
- Required for remote access
- Recommended for all access
- Methods: SMS codes, authenticator apps, hardware tokens
- Backup authentication methods

**Password Requirements:**
- Minimum 12 characters
- Complexity: upper, lower, number, symbol
- Change every 90 days (or upon compromise)
- No reuse of last 10 passwords
- Account lockout: 5 failed attempts

## 5. Transmission Security (§164.312(e))

**Integrity Controls (Addressable):**
- Network segmentation (VLANs)
- Integrity checking
- Secure protocols only

**Encryption (Addressable):**
- TLS 1.2+ for web traffic
- VPN for remote access
- Encrypted email for PHI
- No unencrypted PHI transmission

## Implementation Checklist
- [ ] Unique user IDs implemented
- [ ] Break-glass accounts configured
- [ ] Automatic logoff enabled
- [ ] Full disk encryption deployed
- [ ] TLS 1.2+ enforced
- [ ] Comprehensive audit logging
- [ ] MFA for remote access
- [ ] Strong password policy enforced
- [ ] Integrity controls implemented

## Tools and Technologies
- Active Directory / Azure AD
- SIEM: Splunk, ELK Stack
- Encryption: BitLocker, FileVault
- MFA: Duo, Microsoft Authenticator, Okta
- VPN: Cisco AnyConnect, OpenVPN

# Test: Acronym Definition

This file is used to test the TechWriter.Acronyms rule. It ensures that acronyms are properly defined on first use to maintain clarity and accessibility for all readers, especially those new to the domain or non-native English speakers.

## Rule Overview

### Purpose
Acronyms can create barriers to understanding. This rule enforces the best practice of defining acronyms on first use, following the pattern: "Full Term (ACRONYM)" or "ACRONYM (Full Term)".

### Configuration Options
- **Exceptions list**: Common acronyms that don't need definition (e.g., USA, HTML, CSS)
- **Scope**: Document-level or section-level tracking
- **Format**: Parenthetical, appositive, or footnote style
- **Case sensitivity**: Whether to treat "api" and "API" differently

## Bad Examples - Missing Definitions (Should Flag)

### First Use Without Definition
- The API is documented. (ACRONYM - should flag first use)
- Use REST for communication. (ACRONYM - should flag first use)
- JSON format is required. (ACRONYM - should flag first use)
- The XML schema is here. (ACRONYM - should flag first use)

### Technical Documentation Context
- Configure the YAML file to specify dependencies.
- The SDK includes helper utilities for common tasks.
- Enable CORS for cross-domain requests.
- The JWT contains encoded user claims.
- Install via npm or yarn package managers.

### API and Protocol Acronyms
- Use gRPC for high-performance communication.
- The SMTP server handles outgoing email.
- Configure DNS records for your domain.
- The CDN improves content delivery speed.
- Enable TLS encryption for security.

### Database and Storage Terms
- Connect to the SQL database instance.
- Use NoSQL for flexible schema design.
- Configure ACID transaction guarantees.
- The ORM maps objects to database tables.
- Enable ETL pipelines for data processing.

### Cloud and Infrastructure
- Deploy to AWS for scalability.
- Use K8s for container orchestration.
- Configure IAM roles for access control.
- Set up CI/CD pipelines for automation.
- Use VPC for network isolation.

## Good Examples - Proper Definitions (Should NOT Flag)

### Standard Parenthetical Format
- The API (Application Programming Interface) is documented.
- Use REST (Representational State Transfer) for communication.
- JSON (JavaScript Object Notation) format is required.
- The XML (Extensible Markup Language) schema is here.

### Reverse Format (Acronym First)
- Use YAML (Yet Another Markup Language) for configuration files.
- The SDK (Software Development Kit) includes helper utilities.
- Enable CORS (Cross-Origin Resource Sharing) for cross-domain requests.
- The JWT (JSON Web Token) contains encoded user claims.

### Appositive Style (Comma-Separated)
- Use gRPC, a high-performance RPC framework, for communication.
- The SMTP, or Simple Mail Transfer Protocol, server handles email.
- Configure DNS, the Domain Name System, records for your domain.
- The CDN, a Content Delivery Network, improves speed.

### Inline Definition Style
- Enable TLS encryption for security. TLS stands for Transport Layer Security.
- Connect to the SQL database. SQL is Structured Query Language.
- Use NoSQL for flexible design. NoSQL means "Not Only SQL."
- The ORM maps objects to tables. ORM is Object-Relational Mapping.

### Subsequent Uses (Should NOT Flag After Definition)
The API reference document shows all methods. The API includes authentication endpoints. Each API call requires a valid token. Review the API documentation for details.

### Pre-Defined Common Acronyms (Allowed Without Definition)
- HTML and CSS form the foundation of web design.
- The USA requires export compliance for certain technologies.
- PDF documents preserve formatting across platforms.
- USB devices connect via standard ports.
- The FAQ section answers common questions.

## Edge Cases and Special Scenarios

### Multiple Acronyms in One Sentence
The API (Application Programming Interface) returns JSON (JavaScript Object Notation) data over HTTPS (HyperText Transfer Protocol Secure).

**Status:** Should NOT flag - all three acronyms are properly defined
**Best Practice:** Define each acronym individually on first use

### Nested Parentheses
The REST (Representational State Transfer) API uses HTTP (HyperText Transfer Protocol, not to be confused with HTTPS) for communication.

**Status:** Complex - may require manual review
**Better:** Split into separate sentences for clarity

### Acronyms in Code Blocks
```javascript
// POST request to API endpoint
const response = await fetch('/api/v1/users');
const json = await response.json();
```

**Status:** Code examples typically exempt from acronym rules
**Reason:** Technical context is assumed, code must remain syntactically valid

### Plural Acronyms
Configure multiple APIs in your application. Deploy to several VPCs for isolation.

**Status:** Should flag if singular form not previously defined
**Rule:** Define the singular form first, then plural is acceptable

### Acronyms as Product Names
Use AWS Lambda for serverless functions. Deploy with Azure Functions or Google Cloud Functions.

**Status:** May be exempt as proper nouns/brand names
**Configuration:** Add product names to exceptions list

### Industry-Standard Acronyms in Technical Docs
The HTTP protocol operates on port 80. HTTPS uses port 443. FTP runs on port 21.

**Status:** Depends on audience and document type
**Guideline:** Define even common acronyms if audience is mixed or beginner-level

## Testing Strategies

### Positive Tests (Should Flag)
1. First use without definition in any form
2. Acronym in title without definition in body
3. Acronym in list item without context
4. Acronym in table without header definition

### Negative Tests (Should NOT Flag)
1. Defined using standard parenthetical format
2. Defined using reverse format
3. Defined using appositive style
4. Subsequent uses after proper definition
5. Acronyms in configured exceptions list

### Boundary Tests
1. Acronym at start of document
2. Acronym in footnote or sidebar
3. Acronym in image alt text or caption
4. Acronym spanning line breaks
5. Acronym in hyperlink text

## Context-Specific Rules

### API Documentation
**Required Definitions:**
- REST, SOAP, GraphQL (architectural styles)
- JSON, XML, YAML (data formats)
- JWT, OAuth, SAML (authentication methods)
- CRUD, HATEOAS (operational concepts)

**Often Exempt:**
- HTTP, HTTPS (assumed knowledge)
- API itself (in API documentation)
- URL, URI (web fundamentals)

### Cloud Infrastructure Documentation
**Required Definitions:**
- IaaS, PaaS, SaaS (service models)
- VPC, VPN, CDN (networking)
- IAM, RBAC, SSO (security)
- CI/CD, DevOps (methodologies)

**Often Exempt:**
- AWS, Azure, GCP (major providers)
- EC2, S3 (if defining AWS services)
- VM (virtual machine is widely known)

### Database Documentation
**Required Definitions:**
- ACID, BASE (consistency models)
- ETL, ELT (data processing)
- OLTP, OLAP (workload types)
- CAP (theorem)

**Often Exempt:**
- SQL, NoSQL (fundamental categories)
- JSON, XML (data formats)
- API (general tech term)

## Real-World Examples

### Good: First-Time User Documentation
When building your first application, you'll use the API (Application Programming Interface) to interact with our service. The API accepts requests in JSON (JavaScript Object Notation) format and returns structured data. For authentication, you'll need a JWT (JSON Web Token), which you can obtain by logging in through our OAuth 2.0 (Open Authorization 2.0) flow.

**Analysis:** All acronyms properly defined for new users

### Good: Technical Audience
Configure your REST API to return JSON responses. The API should implement proper HTTP status codes and include CORS headers for browser access. Use JWT tokens for stateless authentication.

**Analysis:** Assumes technical audience familiar with these terms
**Note:** Only acceptable if audience is clearly defined as technical

### Bad: Mixed Audience
Configure the API to return JSON via the REST endpoint. Enable CORS and use JWT for auth. Deploy to AWS using CI/CD.

**Analysis:** Multiple undefined acronyms, unclear for non-experts
**Impact:** Excludes beginners, reduces documentation accessibility

### Fixed: Mixed Audience
Configure the API (Application Programming Interface) to return JSON (JavaScript Object Notation) via the REST (Representational State Transfer) endpoint. Enable CORS (Cross-Origin Resource Sharing) and use JWT (JSON Web Token) for authentication. Deploy to AWS (Amazon Web Services) using CI/CD (Continuous Integration/Continuous Deployment).

**Analysis:** All acronyms defined, accessible to all skill levels

## Implementation Checklist

### For Technical Writers
- [ ] Identify all acronyms in document
- [ ] Define each acronym on first use
- [ ] Use consistent definition format
- [ ] Add common acronyms to exceptions list
- [ ] Review with subject matter experts
- [ ] Test with target audience
- [ ] Update style guide with new acronyms

### For Developers
- [ ] Configure Vale with acronym exceptions
- [ ] Set up document-level tracking
- [ ] Define organization-specific acronyms
- [ ] Create acronym glossary
- [ ] Automate checks in CI/CD
- [ ] Generate acronym reports
- [ ] Review flagged items regularly

## Benefits of Proper Acronym Definition

**Accessibility:**
- Helps non-native English speakers
- Assists screen reader users
- Improves searchability
- Reduces ambiguity

**Professionalism:**
- Demonstrates attention to detail
- Shows respect for all readers
- Follows industry best practices
- Maintains consistent quality

**Efficiency:**
- Reduces support questions
- Decreases onboarding time
- Improves comprehension speed
- Minimizes misunderstandings

## Common Mistakes to Avoid

1. **Assuming Knowledge**: "Use the API to fetch data" (without defining API)
2. **Inconsistent Format**: "REST (Representational State Transfer)" then "JSON Web Token (JWT)"
3. **Over-Defining**: Defining "USA" or "HTML" in technical documentation
4. **Under-Defining**: Skipping domain-specific acronyms
5. **Lost Definitions**: Defining in one section, using undefined in another

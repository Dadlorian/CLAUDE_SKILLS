# Terminology Database and Glossary

## Overview

Consistent terminology ensures clarity and prevents confusion. This database defines standardized terms, approved aliases, and terms to avoid.

## General Technology Terms

### Application Programming Interface (API)

**Standardized term:** API
**Context:** Generic reference to APIs in general, specific API products

**Usage:**
- "The API provides access to user data"
- "Use the REST API to query results"
- "Integrate with our API to get started"

**Abbreviation rules:**
- First mention: "Application Programming Interface (API)"
- Subsequent mentions: "API" only
- Don't expand in headings; use "API"

**Related terms:**
- API endpoint
- API key
- API documentation
- API client

**Never use:** "application programming interface" (spell out only on first use)

### Authentication vs. Authorization

**Authentication:**
- Definition: Verifying identity (proving you are who you claim to be)
- Example: "Enter credentials for authentication"
- Related: login, sign in, credential validation

**Authorization:**
- Definition: Granting access rights (determining what authenticated users can do)
- Example: "You lack authorization to access this resource"
- Related: permissions, access control, roles

**Common mistake:** Using interchangeably. These are distinct concepts.

**Correct usage:**
"First authenticate with your credentials, then the system checks your authorization level"

### Cloud vs. On-Premises (On-Prem)

**Cloud:**
- Definition: Hosted service accessible via internet
- Standard term: "cloud" (lowercase)
- Variations accepted: "cloud-hosted", "cloud-based"

**On-Premises/On-Prem:**
- Standard term: "on-premises" or "on-prem" (hyphenated if adjectival)
- Acceptable variations: "self-hosted", "locally-hosted"

**Usage:**
- "Deploy to the cloud or on-premises"
- "On-prem installation requires a local server"
- "Cloud deployment provides automatic scaling"

**Never use:** "on the cloud", "in the cloud" (data isn't literally in a cloud)

### Database Terminology

**Standard terms:**
- Database (singular: one instance; plural: multiple instances)
- Table (collection of rows and columns)
- Row (single record)
- Column (single field)
- Schema (structure and organization)
- Query (request for data)
- Index (optimization structure)

**Avoid:**
- "DB" in documentation (use "database")
- "Record" (use "row" for technical docs)
- "Field" (use "column" for consistency)

**Example of consistent usage:**
"The `users` table contains rows for each user. Each row includes columns for name, email, and created_at date."

### Network and Connection Terms

**Standard terms:**
- Connection
- Network
- Endpoint
- Server
- Client
- Port
- Protocol
- Hostname

**Capitalization rules:**
- Lowercase in body text: "the connection was lost"
- Specific protocols: "HTTP", "HTTPS", "TCP", "UDP" (all caps)
- Specific port numbers: "port 8080"

**Term distinctions:**
- URL: Uniform Resource Locator (the full web address)
- Endpoint: Specific URL on an API or service
- Host: Computer running a service
- Hostname: Name identifying a host

**Usage examples:**
- "Connect to the API endpoint at https://api.example.com/v1"
- "The server is hosted at example.com on port 443"
- "Check your network connectivity before retrying"

### Security Terms

**Standard terminology:**

| Term | Definition | Usage |
|------|-----------|-------|
| Credential(s) | Authentication information | "Enter your credentials" |
| Token | Temporary credential proving authentication | "Use this token to authenticate requests" |
| Secret | Sensitive value that must be kept private | "Keep your API secret confidential" |
| Permission | Authorization to perform action | "You have permission to view reports" |
| Role | Collection of permissions | "Admins have elevated roles" |
| Encryption | Process of encoding data | "Data is encrypted in transit" |
| Hash | One-way cryptographic function | "Passwords are stored as hashes" |
| Signature | Cryptographic verification of authenticity | "Each request includes a signature" |

**Related terms to avoid in favor of above:**
- "pass" (use "credential")
- "key" (specify: "API key" or "encryption key")
- "secure" (be specific: "encrypted", "authenticated", "authorized")

## Product-Specific Terminology

### Product Names and Versions

**Capitalization rules:**
- Proper product names capitalized: "Dashboard", "API Console", "Authentication Service"
- Generic references lowercase: "the dashboard", "your authentication service"

**Examples:**
- "Open the Dashboard to view metrics"
- "The Authentication Service requires OAuth 2.0"
- "Our API Console provides a sandbox environment"

**Version naming:**
- Specify version in technical docs: "API v2", "SDK 3.0.1"
- In general references: "the latest version"
- Not: "version 2" (be specific: "version 2.0", "v2", "API v2")

### Feature and Component Names

**Standard components:**

| Component | Proper Usage | Context |
|-----------|--------------|---------|
| Workspace | "Create a workspace" | Organization/project container |
| Project | "Navigate to your project" | Subdivision of workspace |
| Team | "Add team members" | Group of users |
| Dashboard | "Open the Dashboard" | Primary UI view |
| Settings | "Go to Settings" | Configuration area |
| Console | "Use the API Console" | Development tool |

**User-facing UI text capitalization:**
- Match actual UI exactly: "Click the **Settings** button" (if UI shows "Settings")
- In descriptions, use lowercase: "access the settings page"

**Feature references:**
- New feature: "Feature Name (beta)" if applicable
- Released feature: "Feature Name"
- Deprecated: "Feature Name (deprecated in 2.0)"

## Common Terminology Mistakes and Corrections

### 1. "Log In" vs. "Login"

**Correct:**
- Verb phrase: "log in" (two words): "Log in to your account"
- Noun/adjective: "login" (one word): "the login form", "login credentials"

**Examples:**
- "Click here to log in" (verb)
- "Your login is configured" (noun)
- "The login process takes 30 seconds" (noun/adjective)

### 2. "Enable" vs. "Activate" vs. "Turn On"

**Standardized term:** "Enable"
- "Enable two-factor authentication"
- "The feature is enabled by default"

**Acceptable alternatives:**
- "Activate" (for features requiring account activation)
- "Turn on" (only in casual/informal contexts)

**Avoid:**
- "Disable" is correct; don't use "turn off" or "deactivate" in technical docs
- Be consistent within same document

### 3. "User" vs. "Customer" vs. "Developer"

**Usage:**
- **User:** Anyone using the product
- **Customer:** Paying/licensed user
- **Developer:** Using APIs/SDKs to build integrations
- **Administrator:** User with elevated permissions
- **Team member:** Invited user in a workspace

**Examples:**
- "Users can view their dashboard"
- "Customers have access to premium features"
- "Developers use the API to build applications"
- "Administrators can manage team members"

### 4. "Update" vs. "Upgrade"

**Update:** Installing a patch or version of same major version
- "Update to the latest patch (v2.0.3)"
- "You can update the app from Settings"

**Upgrade:** Moving to a newer major version
- "Upgrade from v1.0 to v2.0"
- "Plan upgrades provide additional features"

### 5. "Install" vs. "Setup" vs. "Configure"

**Install:** Download and place software
- "Install the SDK using npm"
- "Download and install the latest version"

**Setup/Set up:** Initial configuration
- "Set up your account"
- "Follow these setup instructions"
- "The setup process takes 5 minutes" (noun)

**Configure:** Customize settings
- "Configure your authentication method"
- "Update your configuration file"

## Measurement and Unit Terminology

### Time Units

**Standard usage:**
- Seconds, minutes, hours, days (spelled out in text)
- Abbreviations: "s", "m", "h", "d" (in technical contexts only)
- 24-hour format: "14:30", not "2:30 PM"

**Examples:**
- "Timeout after 30 seconds"
- "Cache duration: 1 hour (3600 seconds)"
- "Requests processed in 250ms"

**Avoid:**
- "Seconds" abbreviated as "sec" in body text (use "s" or spell out)
- "Minutes" as "mins"

### Data Size Units

**Binary units (standard in tech):**
- Byte (B)
- Kilobyte (KB) = 1,024 bytes
- Megabyte (MB) = 1,024 KB
- Gigabyte (GB) = 1,024 MB
- Terabyte (TB) = 1,024 GB

**Examples:**
- "File size limit: 100 MB"
- "Storage included: 1 GB per user"
- "Database backup: 50 TB"

**Note:** Don't use GB "gigs" or TB "terabytes" casually in technical docs; use full abbreviations.

### Rate and Frequency

**Standardized terms:**
- Per second (req/s)
- Per minute (req/m)
- Per day (limit: 1000 requests/day)
- Hertz (Hz) for frequency in hardware contexts

**Examples:**
- "API rate limit: 1000 requests per minute"
- "Processing throughput: 10,000 events/second"
- "Polling frequency: 30-second intervals"

## Stylistic Consistency

### Acronyms and Abbreviations

**Rule:** Spell out on first use; abbreviate on subsequent uses

**Examples:**
- First use: "Single Sign-On (SSO)"
- Subsequent: "The SSO configuration requires a provider"

**Common tech acronyms (no expansion needed after first use):**
- API, SDK, JSON, REST, SQL, AWS, OAuth, JWT

**Create expansion list for each document covering:**
- Acronyms used more than twice
- Product-specific abbreviations
- Technical terms specific to documentation

### Hyphenation Rules

**Hyphenate when adjectival (before noun):**
- "Real-time processing"
- "On-premises deployment"
- "Open-source software"

**Don't hyphenate when adverbial (after verb):**
- "Processing in real time"
- "Deployed on premises"
- "Built with open source tools"

### Number Formatting

**Style guide rules:**
- Spell out numbers 1–9 in prose: "Run the tests five times"
- Use numerals for 10+: "Complete 25 configuration steps"
- Spell out in ranges: "10 to 20 seconds"
- Use numerals in tables and code contexts: "Field max: 100"
- Decimals: "3.5 MB", "4.2 seconds"

## Terminology Maintenance

### Adding New Terms

**When to add:**
1. New feature or product component
2. New technical concept introduced
3. Common user confusion about a term
4. Terminology changed from previous version

**Definition template:**
```
[Term]
- Definition: [What it is/does]
- Usage: [How to use in documentation]
- Related terms: [Connected terminology]
- Avoid: [What not to use]
- Example: [Sample usage in context]
```

### Regular Review

**Quarterly review:**
- Check new features for consistent naming
- Review user support tickets for terminology confusion
- Update examples to match current product state
- Remove deprecated terms with sunset period

**When terminology changes:**
- Add deprecation notice in old term entry
- Provide 90-day transition period in documentation
- Update all existing docs gradually (prioritize high-traffic pages)
- Add redirect note: "(formerly called...)"

## Quick Reference: Most Common Terms

| Term | Correct Usage | Avoid |
|------|---------------|-------|
| Authenticate/Authentication | Verify identity | "Log in" for concept |
| Authorize/Authorization | Grant permissions | Confusing with authentication |
| API endpoint | Specific URL on API | "API URL" |
| Enable/Disable | Activate/Deactivate | "Turn on/off" in tech docs |
| Log in (verb) | "Log in to your account" | "Login to" |
| On-premises | "On-premises deployment" | "In the cloud" |
| Token | Temporary credential | "Key" (specify type) |
| User | Any person using product | Generic for all roles |
| Webhook | URL receiving callbacks | "Callback" alone |

## Terminology Verification Checklist

- [ ] New terms added to database before documentation
- [ ] All product names capitalized correctly
- [ ] No spelling variations of same term in single document
- [ ] Acronyms expanded on first use
- [ ] Technical abbreviations use correct form (not "seq" for "second")
- [ ] "Log in" vs. "login" used correctly
- [ ] "Enable/Disable" consistent throughout
- [ ] Hyphenation consistent (real-time vs. real time)
- [ ] Measurements formatted consistently
- [ ] Numbers follow guide (1–9 spelled out, 10+ numerals)
- [ ] No outdated or deprecated terms without notice
- [ ] Regional variations acknowledged if applicable (e.g., "on-premises" vs. "on-premise")

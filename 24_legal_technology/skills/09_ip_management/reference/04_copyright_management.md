# Copyright Management

## Overview
Copyright protection for original works of authorship, including literary, artistic, musical, software, and digital content. Covers registration, digital rights management, licensing, and infringement detection.

---

## Copyright Fundamentals

### What is Protected

**Protectable Works** (17 USC §102):
1. **Literary Works**: Books, articles, software code, documentation
2. **Musical Works**: Songs, compositions, sheet music
3. **Dramatic Works**: Plays, scripts, screenplays
4. **Pantomimes and Choreographic Works**: Dance notation, performance art
5. **Pictorial, Graphic, and Sculptural Works**: Photographs, artwork, sculptures
6. **Motion Pictures and Audiovisual Works**: Films, videos, animations
7. **Sound Recordings**: Music recordings, podcasts, audiobooks
8. **Architectural Works**: Building designs and structures

**Software/Technology-Specific**:
- Source code and object code
- Databases and compilations
- User interfaces (limited protection)
- API documentation
- Technical specifications
- Training materials
- Websites and web content

**Requirements for Protection**:
- ✅ **Originality**: Independent creation + minimal creativity
- ✅ **Fixed in Tangible Medium**: Written, recorded, saved digitally
- ❌ **Ideas**: Not protected (only expression)
- ❌ **Facts**: Not protected (but compilations may be)
- ❌ **Government Works**: US government works are public domain

---

### Automatic Protection

**Copyright Arises Automatically**:
- Protection begins immediately upon creation
- No registration required for basic rights
- Duration: Life of author + 70 years (individual), 95 years from publication (corporate)
- Notice not required but recommended: © 2024 Company Name. All rights reserved.

**Benefits of Registration** (Why register despite automatic protection):
- ✅ **Prerequisite for Lawsuit**: Must register before suing for infringement (US)
- ✅ **Statutory Damages**: $750-$30,000 per work ($150,000 if willful)
- ✅ **Attorney Fees**: Available only if registered within 3 months of publication
- ✅ **Public Record**: Establishes ownership and priority
- ✅ **Presumption of Validity**: Evidence in court proceedings
- ✅ **Customs Protection**: Record with US Customs to stop imports

---

## Copyright Registration

### US Copyright Office Registration

**Application Process**:

1. **Prepare Application** (Form CO, TX, VA, PA, SR depending on work type)
   - **Form CO**: Online, all work types (most common)
   - **Form TX**: Literary works (text)
   - **Form VA**: Visual arts
   - **Form PA**: Performing arts
   - **Form SR**: Sound recordings

2. **Application Information**:
   - Title of work
   - Author(s) and their contribution
   - Creation date
   - Publication date (if published)
   - Copyright claimant (owner)
   - Work for hire determination
   - Derivative work or compilation basis

3. **Deposit Requirements**:
   - **Published Works**: Two complete copies of best edition
   - **Unpublished Works**: One complete copy
   - **Software**: First 25 and last 25 pages of source code
   - **Trade Secret Software**: First 25 pages with portions blocked out
   - **Online Works**: Digital file or printout

**Filing Options**:
- **Online**: $45-$65 (single author, same claimant, one work, not work for hire)
- **Paper**: $125 (slower processing)
- **Expedited**: $800 additional for 5-day processing

**Processing Time**:
- Electronic: 3-8 months
- Paper: 8-12 months
- Expedited: 5 business days ($800 fee)

**Registration Certificate**:
- Official record of copyright claim
- Registration number and effective date
- Evidence of ownership

---

### Bulk Registration Strategies

**Group Registration**:
- Register multiple works as single application
- Lower cost per work
- Requirements vary by work type

**Published Photographs** (Group Registration):
- Up to 750 photographs
- All by same photographer
- Published within same calendar year
- Single filing fee ($65)

**Unpublished Collections**:
- Multiple unpublished works
- Same author
- Collected under single title
- Single filing fee

**Software Updates**:
- Register each major version
- Combine minor updates annually
- Strategy: Version 1.0 (register), then combine 1.1-1.9 in annual group filing

**Website Content**:
- Register website as collective work
- Updates: Register quarterly or annually as new versions

---

### International Copyright Protection

**Automatic Protection via Treaties**:

**Berne Convention** (179 countries):
- Automatic protection in member countries
- No registration required
- National treatment (same rights as locals)
- Minimum protection: Life + 50 years

**Universal Copyright Convention (UCC)**:
- Supplement to Berne
- Requires © notice
- Less commonly invoked (Berne is stronger)

**TRIPS Agreement** (WTO):
- Minimum IP standards for trade
- Enforcement mechanisms
- Covers 164 countries

**Key Markets**:
- ✅ **US, EU, UK, Canada, Australia**: Strong copyright protection, Berne Convention
- ✅ **Japan, South Korea**: Strong enforcement
- ⚠️ **China**: Berne member, but enforcement challenging
- ⚠️ **Russia**: Berne member, enforcement variable
- ⚠️ **India**: Berne member, developing enforcement

**No Central International Registration**:
- Must register in each country separately if desired
- US registration doesn't extend abroad (but Berne gives automatic protection)
- Some countries require registration for enforcement

---

## Digital Rights Management (DRM)

### DRM Technologies

**Purpose**: Control access and usage of digital content.

**DRM Methods**:

1. **Encryption**:
   - Content encrypted, requires key to decrypt
   - Keys tied to licensed devices or users
   - Examples: AACS (Blu-ray), FairPlay (Apple), Widevine (Google)

2. **License Management**:
   - License server validates user entitlement
   - Token-based access control
   - Expiring licenses for rentals
   - Device limits (e.g., 5 devices max)

3. **Watermarking**:
   - **Visible**: Logo or text overlay (deters screenshot piracy)
   - **Invisible**: Embedded metadata for tracking
   - **Forensic**: Trace leaked content back to source

4. **Access Control**:
   - Password protection
   - IP address restrictions
   - Geographic restrictions (geo-blocking)
   - Time-based access (expires after 48 hours)

5. **Copy Protection**:
   - Prevent copying or screen capture
   - Download restrictions
   - Print restrictions (for documents)

**Common DRM Systems**:

**Video/Streaming**:
- **Widevine** (Google): Used by Netflix, Disney+, Spotify
- **FairPlay** (Apple): Apple TV+, iTunes
- **PlayReady** (Microsoft): Xbox, Windows
- **Adobe Primetime**: Enterprise video protection

**Audio/Music**:
- **FairPlay** (Apple Music, iTunes)
- **Widevine** (Spotify, YouTube Music)
- Most music now DRM-free (iTunes dropped DRM in 2009)

**E-books**:
- **Adobe Content Server**: Industry standard for EPUB/PDF
- **Amazon KDP**: Kindle DRM
- **Apple FairPlay**: Apple Books

**Software**:
- **Product Keys**: Serial number activation
- **Online Activation**: Phone-home to license server
- **Hardware Dongles**: USB keys (less common now)
- **Software as a Service**: No local software, all cloud-based

**Enterprise Documents**:
- **Microsoft Azure RMS**: Rights Management Services
- **Adobe LiveCycle Rights Management**
- **Oracle IRM**: Information Rights Management

---

### DRM Implementation

**Content Protection Workflow**:
```
Original Content
    ↓
Encryption (AES-128, AES-256)
    ↓
Package with DRM Wrapper
    ↓
Upload to CDN/Streaming Platform
    ↓
License Server (validates user)
    ↓
Deliver Encrypted Content + Key
    ↓
Decryption on Device
    ↓
Playback (with restrictions)
```

**License Models**:
- **Purchase**: Perpetual access
- **Rental**: Time-limited (24-48 hours)
- **Subscription**: Access while subscribed
- **Ad-Supported**: Free with advertising
- **Freemium**: Basic free, premium paid

**Device Restrictions**:
- Limit concurrent streams (e.g., 2 devices)
- Limit total devices (e.g., 5 authorized devices)
- Device deauthorization process
- Output restrictions (HDCP for video)

---

### Anti-Circumvention (DMCA §1201)

**Digital Millennium Copyright Act (DMCA)**:
- ❌ **Illegal**: Circumvent DRM or access controls
- ❌ **Illegal**: Manufacture or distribute circumvention tools
- ⚠️ **Exemptions**: Security research, accessibility, fair use (limited)

**DMCA Exemptions** (renewed every 3 years):
- Software preservation by libraries
- Smartphone unlocking
- Vehicle software for repair
- Accessibility for disabled users
- Security research
- Jailbreaking (limited contexts)

---

## Copyright Licensing

### License Types

**Exclusive License**:
- Only licensee can use (owner cannot grant to others)
- Must be in writing
- Transfers ownership rights (similar to assignment)
- Licensee can sue for infringement

**Non-Exclusive License**:
- Owner can license to multiple parties
- Can be oral or implied
- Licensee generally cannot sue for infringement
- Common for stock photos, music libraries

**Territorial Restrictions**:
- Worldwide rights
- Regional rights (North America, Europe, Asia-Pacific)
- Country-specific rights
- Language-specific rights

**Field of Use Restrictions**:
- Media type (print, digital, broadcast)
- Purpose (commercial, educational, personal)
- Industry (healthcare, automotive, etc.)
- Platform (web, mobile, desktop)

**Duration**:
- Perpetual license
- Term license (1 year, 5 years, etc.)
- Project-based (for specific campaign or product)

---

### Standard License Models

**Creative Commons (CC)** Licenses:

| License | Commercial Use | Derivatives | Share-Alike Required |
|---------|---------------|-------------|---------------------|
| CC BY | ✅ Yes | ✅ Yes | ❌ No |
| CC BY-SA | ✅ Yes | ✅ Yes | ✅ Yes (same license) |
| CC BY-ND | ✅ Yes | ❌ No | N/A |
| CC BY-NC | ❌ No | ✅ Yes | ❌ No |
| CC BY-NC-SA | ❌ No | ✅ Yes | ✅ Yes (same license) |
| CC BY-NC-ND | ❌ No | ❌ No | N/A |
| CC0 | ✅ Yes (Public Domain) | ✅ Yes | ❌ No |

**Open Source Software Licenses**:

**Permissive**:
- **MIT**: Very permissive, attribution required
- **Apache 2.0**: Permissive, patent grant, attribution required
- **BSD**: Similar to MIT, various versions

**Copyleft** (Share-Alike):
- **GPL v2/v3**: Derivatives must be GPL, source code disclosure required
- **LGPL**: Less restrictive GPL for libraries
- **AGPL**: GPL + network use triggers obligations

**Stock Content Licensing**:

**Royalty-Free (RF)**:
- One-time fee, unlimited use within scope
- Still have restrictions (cannot resell as-is)
- Examples: Shutterstock, iStock, Adobe Stock

**Rights-Managed (RM)**:
- Priced by usage (size, duration, geography, exclusivity)
- More expensive, precise control
- Examples: Getty Images (premium), Corbis

**Model Releases**:
- Required for commercial use of photos with identifiable people
- Property releases for recognizable private property
- Talent releases for voice recordings

---

### Royalty Management

**Royalty Types**:

1. **Per-Unit Royalty**: $X per copy sold
2. **Percentage Royalty**: Y% of revenue or list price
3. **Flat Fee**: One-time payment (buyout)
4. **Minimum Guarantee + Royalty**: Upfront + ongoing
5. **Advance Against Royalties**: Recoupable advance

**Royalty Calculation**:
```
Example: Book Publishing

List Price: $25.00
Net Price (after retailer discount): $12.50
Author Royalty Rate: 10% of net
Units Sold: 10,000

Royalty = $12.50 × 10% × 10,000 = $12,500

If advance was $10,000:
- First $10,000 recoups advance (author receives nothing additional)
- Remaining $2,500 paid to author
```

**Royalty Tracking**:
- Sales data integration (point of sale, e-commerce)
- Automated calculation engines
- Periodic reporting (quarterly, semi-annual)
- Audit rights (once per year)
- Payment terms (NET 30, NET 60)

**Music Royalties** (Complex):
- **Mechanical Royalties**: Reproduction of musical composition (9.1¢ per song in US)
- **Performance Royalties**: Public performance (radio, streaming) → ASCAP, BMI, SESAC
- **Synchronization Royalties**: Use in film, TV, ads (negotiated)
- **Print Royalties**: Sheet music sales
- **Master Recording Royalties**: Use of specific recording (separate from composition)

**Software Royalties**:
- Per-seat licensing
- Per-device/server licensing
- Subscription-based (monthly/annual recurring)
- Usage-based (API calls, transactions)

---

## Copyright Infringement Detection

### Monitoring Technologies

**Web Scraping and Crawling**:
- Automated bots scan websites for unauthorized content
- Image matching algorithms
- Text matching (plagiarism detection)
- Video fingerprinting

**Reverse Image Search**:
- Google Images: Search by image
- TinEye: Reverse image search engine
- Specialized tools: Pixsy, ImageRights

**Video Content ID Systems**:

**YouTube Content ID**:
- Upload reference files of your content
- YouTube scans all uploads for matches
- Actions when match found:
  - Block video
  - Monetize (place ads, collect revenue)
  - Track (monitor views and analytics)
- Automated enforcement at scale

**Facebook Rights Manager**:
- Similar to YouTube Content ID
- Covers Facebook and Instagram
- Upload reference files
- Automated matching and enforcement

**Audio Fingerprinting**:
- Shazam, Gracenote, ACRCloud
- Identify music in podcasts, videos, broadcasts
- Detect unauthorized use of sound recordings

---

### Takedown Procedures

**DMCA Takedown Notice** (17 USC §512(c)):

**Requirements**:
1. Identification of copyrighted work
2. Identification of infringing material (URL or location)
3. Contact information
4. Good faith statement
5. Accuracy statement
6. Physical or electronic signature

**Service Provider Response**:
- Must remove or disable access "expeditiously"
- Notify alleged infringer
- Alleged infringer can file counter-notice

**Counter-Notice** (if user believes takedown is erroneous):
- User claims material is authorized or fair use
- Swears penalty of perjury
- Service provider must restore content in 10-14 days (unless copyright owner files lawsuit)

**Platform-Specific Processes**:

**Google (Search, YouTube, Drive)**:
- DMCA web form
- Response time: 24-72 hours (search), varies (YouTube)

**Facebook/Instagram**:
- Copyright infringement report form
- Can use Rights Manager for automated enforcement

**Twitter/X**:
- Copyright complaint form
- Typically responds within 24-48 hours

**Amazon (products, Kindle books)**:
- Notice of Claimed Infringement form
- Can result in listing removal or account suspension

**Repeat Infringer Policy**:
- Platforms must terminate repeat infringers
- Three-strike policies common
- Account suspension or permanent ban

---

### Litigation & Enforcement

**Copyright Infringement Elements**:
1. Ownership of valid copyright
2. Copying of original elements (access + substantial similarity)

**Remedies**:

**Injunctive Relief**:
- Preliminary injunction (stop infringement during case)
- Permanent injunction (stop forever after judgment)

**Monetary Damages**:
- **Actual Damages**: Profits lost + infringer's profits
- **Statutory Damages**: $750-$30,000 per work ($150,000 if willful)
  - Must register within 3 months of publication or before infringement
- **Attorney Fees**: Available if registered timely

**Criminal Penalties** (rare, serious cases):
- Willful infringement for commercial advantage
- Up to 5 years prison + fines

**Litigation Timeline**:
- Case duration: 12-36 months
- Costs: $100,000-$1,000,000+ (can be much higher)
- Settlement common (70%+ of cases settle)

**Alternative Dispute Resolution**:
- Cease and desist letter (first step)
- Mediation (neutral facilitator)
- Arbitration (binding decision)

---

## Fair Use and Exceptions

### Fair Use Analysis (17 USC §107)

**Four Factors**:

1. **Purpose and Character of Use**:
   - ✅ Transformative use (commentary, parody, education)
   - ❌ Commercial use (but not determinative)
   - ✅ Nonprofit educational use (favored)

2. **Nature of Copyrighted Work**:
   - ✅ Factual works (more fair use latitude)
   - ❌ Creative works (less fair use)
   - ❌ Unpublished works (disfavors fair use)

3. **Amount and Substantiality**:
   - ✅ Small portion used
   - ❌ Entire work or "heart" of work used
   - Context-dependent (thumbnails may be OK for search engines)

4. **Effect on Market**:
   - ❌ Substitutes for original (disfavors fair use)
   - ✅ No market harm (favors fair use)
   - ❌ Affects licensing market (disfavors)

**Common Fair Use Scenarios**:
- ✅ Quotation in book review or criticism
- ✅ Parody (transformative commentary)
- ✅ News reporting (factual use)
- ✅ Educational use (classroom teaching)
- ⚠️ Thumbnail images (search engines - case-by-case)
- ❌ Commercial reuse without transformation

**Not Fair Use** (Common Misconceptions):
- ❌ "I'm not making money" (commercial use is a factor, not determinative)
- ❌ "I gave credit" (attribution doesn't make it fair use)
- ❌ "I only used 30 seconds" (no bright-line rule)
- ❌ "It's for educational purposes" (education favors, but not automatic)

---

### Specific Exemptions

**Section 108** (Libraries and Archives):
- Preservation copies
- Replacement of damaged copies
- Interlibrary loan
- Limitations: Cannot be systematic, commercial

**Section 110** (Education):
- Face-to-face teaching (classroom performance/display)
- Distance education (TEACH Act) with restrictions
- Requirements: Accredited nonprofit, limited to enrolled students

**Section 117** (Software):
- Backup copy of lawfully owned software
- Essential step in use (e.g., loading into RAM)
- Interoperability (reverse engineering for compatibility)

**Section 512** (Safe Harbor for Online Platforms):
- ISPs/platforms not liable if they:
  - Have DMCA agent registered
  - Respond to takedown notices
  - Terminate repeat infringers
  - No actual knowledge of infringement

---

## Copyright Management Systems

### Content Management Integration

**Digital Asset Management (DAM)**:
- Centralized repository for copyrighted assets
- Metadata: Creator, creation date, ownership, license terms
- Version control and usage tracking
- Integration with creative tools (Adobe, Figma, etc.)

**Rights Management Fields**:
- Copyright owner
- Creation date
- Registration number and date
- License type and terms
- Permitted uses and restrictions
- Expiration dates
- Territory restrictions
- Model/property releases

**Examples**:
- Adobe Experience Manager
- Bynder
- Widen Collective
- Aprimo
- Brandfolder

---

### Licensing Platforms

**Stock Content Platforms**:
- Shutterstock, Adobe Stock, Getty Images
- License tracking and download history
- Automated compliance reporting

**Music Licensing**:
- Epidemic Sound, AudioJungle, Artlist
- Synchronization license management
- Blanket licenses for content creators

**Font Licensing**:
- Adobe Fonts, Google Fonts, MyFonts
- Desktop vs. web vs. app licensing
- Concurrent user tracking

**Software License Management**:
- Flexera, Snow Software, ServiceNow SAM
- Track installed software vs. purchased licenses
- Compliance audits and true-up processes

---

### Royalty Automation

**Royalty Management Systems**:
- Sales data ingestion (EDI, API integration)
- Automated royalty calculation
- Multi-currency support
- Advance recoupment tracking
- Automated payment processing
- Royalty statement generation

**Examples**:
- MetaComet (publishing)
- Vistex (manufacturing, life sciences)
- Precision RMS
- RoyaltyStat
- Custom-built systems (large publishers)

**Blockchain for Royalties**:
- Smart contracts for automated payment
- Transparent, immutable royalty records
- Real-time micropayments for streaming
- Examples: Audius (music), Story Protocol (general IP)

---

## Key Performance Indicators

### Registration Metrics
- **Registration backlog**: <50 unregistered works
- **Time to register**: <30 days from creation (for timely registration benefits)
- **Registration coverage**: >95% of published works registered

### Licensing Metrics
- **License revenue**: Track by work, territory, licensee
- **License utilization**: % of works generating revenue
- **Average license value**: Trending up or down
- **Royalty payment timeliness**: % paid on time

### Enforcement Metrics
- **Infringement detection rate**: Average time to discover
- **Takedown success rate**: % of notices resulting in removal
- **Takedown speed**: Average time from notice to removal
- **Repeat infringement**: # of repeat infringers per platform
- **Litigation success**: % of cases won or favorably settled

### Portfolio Metrics
- **Total registered works**: Track by category
- **Active licenses**: # of current license agreements
- **Geographic coverage**: Territories with protection
- **Revenue per work**: Identify high-value assets

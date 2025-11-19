# Test: Terminology Consistency

This file is used to test the TechWriter.Consistency rule. It ensures that compound technical terms, hyphenation, and terminology usage remain consistent throughout documentation. Inconsistent terminology confuses readers, reduces professionalism, and undermines documentation credibility.

## Rule Purpose

### Why Consistency Matters
Inconsistent terminology creates problems:
- **Reader confusion**: "Is frontend different from front-end?"
- **Search inefficiency**: Users can't find content with different spellings
- **Reduced professionalism**: Appears careless or unedited
- **Team friction**: Developers debate trivial style choices
- **Translation issues**: Multiple terms for same concept
- **SEO impact**: Scattered search terms reduce discoverability

### Common Consistency Issues
1. **Hyphenation**: user-facing vs user facing vs userfacing
2. **Capitalization**: API vs Api vs api
3. **Spacing**: database vs data base
4. **Pluralization**: APIs vs API's
5. **Abbreviations**: e.g. vs eg vs e.g
6. **British vs American**: colour vs color

## Bad Examples - Inconsistent Terms (Should Flag)

### Hyphenation Issues - Compound Adjectives
- The user facing interface is clean. (Should be "user-facing")
- Client side validation is required. (Should be "client-side")
- Server side processing happens here. (Should be "server-side")
- Real time updates are available. (Should be "real-time")
- Command line tools are essential. (Should be "command-line")
- Third party integrations work well. (Should be "third-party")
- End to end testing is important. (Should be "end-to-end")
- Cross platform support is needed. (Should be "cross-platform")

### Hyphenation - Backend/Frontend Terms
- The back-end code is optimized. (Should be "backend" - no hyphen)
- Front-end developers use this tool. (Should be "frontend" - no hyphen)
- The back end server handles requests. (Should be "backend")
- Front end frameworks are popular. (Should be "frontend")

**Note:** Modern style guides (Google, Microsoft) prefer "backend" and "frontend" as single words.

### Capitalization Inconsistencies
- The Api is well-documented. (Should be "API" - all caps)
- Use the Url parameter. (Should be "URL" - all caps)
- Send Http requests. (Should be "HTTP" - all caps)
- The Json format is standard. (Should be "JSON" - all caps)
- Configure the Dns settings. (Should be "DNS" - all caps)

### Spacing Issues
- Use the data base connection. (Should be "database" - one word)
- The web site is responsive. (Should be "website" - one word)
- Load the style sheet. (Should be "stylesheet" - one word)
- The file name must be valid. (Should be "filename" - one word)
- Set the time out value. (Should be "timeout" - one word)
- Check the user name. (Should be "username" - one word)

### Inconsistent Pluralization
- Multiple API's are available. (Should be "APIs" - no apostrophe)
- Configure the URL's. (Should be "URLs" - no apostrophe)
- The SDK's include examples. (Should be "SDKs" - no apostrophe)

### Inconsistent Abbreviations
- Configure e.g the timeout value. (Should be "e.g.," - with period and comma)
- Use eg Docker or Kubernetes. (Should be "e.g.," - with periods)
- Setup ie the initial configuration. (Should be "i.e.," - with periods)

## Good Examples - Consistent Terms (Should NOT Flag)

### Proper Hyphenation - Compound Adjectives
- The user-facing interface is clean.
- Client-side validation is required.
- Server-side processing happens here.
- Real-time updates are available.
- Command-line tools are essential.
- Third-party integrations work well.
- End-to-end testing is important.
- Cross-platform support is needed.

### Proper Backend/Frontend Usage
- The backend code is optimized.
- Frontend developers use this tool.
- The backend server handles requests.
- Frontend frameworks are popular.

### Correct Capitalization
- The API is well-documented.
- Use the URL parameter.
- Send HTTP requests.
- The JSON format is standard.
- Configure the DNS settings.

### Proper Spacing
- Use the database connection.
- The website is responsive.
- Load the stylesheet correctly.
- The filename must be valid.
- Set the timeout value.
- Check the username field.

### Correct Pluralization
- Multiple APIs are available.
- Configure the URLs properly.
- The SDKs include examples.

### Proper Abbreviations
- Configure e.g., the timeout value.
- Use e.g., Docker or Kubernetes.
- Setup i.e., the initial configuration.

## Compound Adjective Rules

### When to Hyphenate
**Rule:** Hyphenate compound adjectives BEFORE a noun:
- user-facing interface
- server-side processing
- real-time updates
- well-known algorithm
- open-source software
- high-level overview

### When NOT to Hyphenate
**Rule:** Don't hyphenate AFTER a noun or linking verb:
- The interface is user facing
- Processing happens server side
- Updates occur in real time
- The algorithm is well known
- The software is open source
- This overview is high level

**Exception:** Some terms are always hyphenated: built-in, command-line, check-in

## Organization-Specific Decisions

### Backend vs Back-end vs Back end
**Google/Microsoft Style:** backend (one word)
**Traditional Style:** back-end (hyphenated)
**Wrong:** back end (two words)

**Choose one and be consistent throughout documentation**

### Dataset vs Data set vs Data-set
**Modern:** dataset (one word)
**Scientific:** data set (two words)
**Outdated:** data-set (hyphenated)

**Choose based on your domain**

### Email vs E-mail
**Modern:** email (no hyphen)
**Traditional:** e-mail (hyphenated)
**Never:** Email (don't capitalize mid-sentence)

**Trend:** Strongly toward email without hyphen

## Terminology Registry Examples

### Preferred Terms List
| Concept | Use | Don't Use |
|---------|-----|-----------|
| Application Programming Interface | API | Api, api |
| Backend | backend | back-end, back end |
| Frontend | frontend | front-end, front end |
| Database | database | data base, data-base |
| Username | username | user name, user-name |
| Email | email | e-mail, Email |
| Filename | filename | file name, file-name |
| Checkbox | checkbox | check box, check-box |

## Testing Strategy

### Positive Tests (Should Flag)
1. Unhyphenated compound adjectives before nouns
2. Improperly hyphenated compound words
3. Inconsistent API/URL capitalization
4. Incorrect spacing in compound words
5. Apostrophes in plural acronyms
6. Missing periods in abbreviations

### Negative Tests (Should NOT Flag)
1. Properly hyphenated compound adjectives
2. Correct single-word compounds
3. Consistent ALL-CAPS acronyms
4. Proper spacing in standard terms
5. Correct plural forms
6. Standard abbreviation format

### Context-Aware Tests
1. Hyphenation changes based on position
2. Domain-specific compound preferences
3. Style guide variations
4. Legacy vs modern conventions

## Real-World Examples

### Bad: Inconsistent Documentation
The back-end API provides real time updates. Use the frontend to access server side data. Configure DNS settings and URL routing. Multiple API's support JSON responses. User-facing features include built in authentication.

**Issues:**
- back-end should be backend
- real time should be real-time (before noun)
- frontend/backend inconsistent with back-end
- server side should be server-side (before noun)
- API's should be APIs
- built in should be built-in (always hyphenated)

### Good: Consistent Documentation
The backend API provides real-time updates. Use the frontend to access server-side data. Configure DNS settings and URL routing. Multiple APIs support JSON responses. User-facing features include built-in authentication.

**Improvements:** All terms use consistent, modern style guide conventions

### Bad: Mixed Hyphenation
Our cloud based platform provides cross platform support with third party integrations. The command line interface offers real time monitoring for end to end workflows.

**Issues:** All compound adjectives before nouns need hyphens

### Good: Consistent Hyphenation
Our cloud-based platform provides cross-platform support with third-party integrations. The command-line interface offers real-time monitoring for end-to-end workflows.

**Improvements:** All compound adjectives properly hyphenated

## Implementation Checklist

### For Technical Writers
- [ ] Create organization terminology database
- [ ] Document hyphenation rules
- [ ] List all acronyms with proper capitalization
- [ ] Define compound word preferences
- [ ] Choose backend/frontend style
- [ ] Establish abbreviation format
- [ ] Review existing content for inconsistencies
- [ ] Update style guide
- [ ] Train team on standards

### For Developers
- [ ] Configure Vale consistency rules
- [ ] Add custom terminology patterns
- [ ] Set up term substitution rules
- [ ] Create organization vocabulary file
- [ ] Test rules against real documentation
- [ ] Integrate into CI/CD pipeline
- [ ] Generate consistency reports
- [ ] Update rules based on feedback

## Benefits of Consistency

### For Readers
- Faster comprehension
- Easier searching
- Reduced confusion
- Better learning experience
- Professional impression

### For Writers
- Fewer decisions to make
- Faster writing
- Less editing required
- Team alignment
- Reduced debates

### For Organization
- Stronger brand voice
- Better SEO
- Improved translations
- Professional reputation
- Reduced support questions

## Common Mistakes to Avoid

### Over-Hyphenation
**Problem:** Hyphenating everything
**Example:** The well-designed user-interface provides high-quality features
**Fix:** The well-designed user interface provides high-quality features
**Rule:** Only hyphenate compound adjectives before nouns

### Under-Hyphenation
**Problem:** Never hyphenating compounds
**Example:** real time monitoring, third party apps
**Fix:** real-time monitoring, third-party apps
**Rule:** Always hyphenate compound adjectives before nouns

### Inconsistent Acronyms
**Problem:** API, api, Api mixed in same document
**Fix:** Choose one (API) and enforce everywhere

### British vs American Mixing
**Problem:** colour and color in same document
**Fix:** Choose American (color) or British (colour) and be consistent

### Possessive Confusion
**Problem:** API's (plural) vs API's (possessive)
**Fix:** APIs (plural), API's (possessive)

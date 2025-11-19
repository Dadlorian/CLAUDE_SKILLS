# Test: Heading Capitalization

This file is used to test the TechWriter.Headings rule. It validates that headings follow consistent capitalization rules (Title Case or Sentence case), improving document structure, scannability, and professional appearance.

## Rule Purpose

### Why Heading Capitalization Matters
Consistent heading capitalization:
- **Improves scannability**: Readers quickly identify section boundaries
- **Enhances professionalism**: Shows attention to detail
- **Aids navigation**: Clear hierarchical structure
- **Supports SEO**: Search engines use headings for content understanding
- **Helps accessibility**: Screen readers identify heading landmarks
- **Maintains consistency**: Unified style across documentation

### Common Capitalization Styles
1. **Title Case**: Capitalize Major Words (recommended for technical docs)
2. **Sentence case**: Capitalize only first word (alternative style)
3. **ALL CAPS**: Avoid (poor accessibility, appears like shouting)
4. **lowercase**: Avoid (unprofessional, hard to distinguish)

## Bad Examples - Improper Capitalization (Should Flag)

### All Lowercase (Should Flag)
## bad heading
- Uses all lowercase letters

## another bad heading example
- Contains only lowercase

## configuration tips and tricks
- Should flag all lowercase

## understanding the api
- Should flag as all lowercase

### Inconsistent Capitalization (Should Flag)
## Getting Started with the API
- Inconsistent: "with" and "the" should not be capitalized in title case

## Working With External APIs
- Inconsistent: "With" should be lowercase in title case

## How to Configure your Settings
- Inconsistent: "your" should be capitalized in title case

## Setting up The Environment
- Inconsistent: "The" should be lowercase unless starting

## Using the api and SDK
- Inconsistent: "api" should be "API" (acronym)

### Mixed Case Errors (Should Flag)
## iNSTALLATION gUIDE
- Random capitalization

## CoNfIgUrAtIoN
- Mixed case throughout

## APi Documentation
- Incorrect acronym capitalization

### Starting with Lowercase (Should Flag Unless Sentence Case)
## installing the software
- Title case requires capital "Installing"

## configuring database connections
- Title case requires capital "Configuring"

## understanding REST APIs
- Title case requires capital "Understanding"

## Good Examples - Proper Capitalization (Should NOT Flag)

### Proper Title Case
## Good Heading Format
- Correct title case

## Installation Instructions
- Proper title case format

## Getting Started With Configuration
- Proper title case throughout

## Best Practices for API Design
- Correct capitalization including preposition

## Understanding The API
- Proper title case format

## How To Configure Your Settings
- All major words capitalized

## Working With External APIs
- Correct title case with acronym

### Proper Sentence Case (Alternative Style)
## Installing the software
- Sentence case: only first word capitalized

## Configuring database connections
- Sentence case format

## Understanding REST APIs
- Sentence case with acronym

## How to configure your settings
- Sentence case style

## Working with external APIs
- Sentence case alternative

### Acronyms and Technical Terms (Correct)
## API Reference Documentation
- Acronym properly capitalized

## REST API Endpoints
- Both acronyms correct

## HTTP Status Codes
- Technical terms correct

## JSON Data Format
- Acronym in title case

## OAuth 2.0 Authentication
- Technical term with version

## Title Case Rules

### Words to Capitalize
- **First and last words**: Always capitalize
- **Major words**: Nouns, verbs, adjectives, adverbs, pronouns
- **Acronyms**: API, REST, HTTP, JSON (all caps)
- **Proper nouns**: GitHub, JavaScript, Python

### Words to Keep Lowercase (Mid-Heading)
- **Articles**: a, an, the
- **Coordinating conjunctions**: and, but, or, nor, for, yet, so
- **Short prepositions** (≤4 letters): at, by, for, from, in, into, of, on, to, with
- **Infinitive "to"**: as in "How to Configure"

### Special Cases
- **Long prepositions** (>4 letters): Capitalize (Through, Between, Without)
- **Verbs**: Always capitalize, even short ones (Is, Are, Be)
- **Hyphenated words**: Capitalize both parts (Self-Hosted, End-to-End)

## Examples with Explanations

### Example 1: Prepositions
## Working With External APIs
**Correct in title case**: "With" is lowercase (short preposition)

## Working Through External APIs
**Also correct**: "Through" is capitalized (long preposition >4 letters)

### Example 2: Articles and Conjunctions
## Setting up the Environment
**Correct**: "the" is lowercase (article)

## Installing and Configuring the System
**Correct**: "and" is lowercase (conjunction), "the" is lowercase (article)

### Example 3: Verbs vs Prepositions
## Logging In to the Dashboard
**Correct**: "In" is capitalized (part of phrasal verb "logging in"), "to" is lowercase (preposition)

## Connecting to the Database
**Correct**: "to" is lowercase (preposition)

### Example 4: Acronyms
## REST API Best Practices
**Correct**: "REST" and "API" are all caps (acronyms)

## Understanding JSON and XML
**Correct**: Both acronyms all caps

## Real-World Heading Examples

### API Documentation Headings (Title Case)
## Authentication and Authorization
## Request and Response Format
## Rate Limiting and Quotas
## Error Codes and Troubleshooting
## Pagination and Filtering
## Webhooks and Event Notifications

### Tutorial Headings (Title Case)
## Getting Started With the API
## Creating Your First Application
## Handling Errors and Exceptions
## Testing and Debugging Your Code
## Deploying to Production
## Best Practices and Security

### Reference Headings (Title Case)
## Configuration Options and Parameters
## Environment Variables and Settings
## Command-Line Interface Reference
## Database Schema and Migrations
## API Endpoints and Methods

## Testing Strategy

### Positive Tests (Should Flag)
1. All lowercase headings
2. Inconsistent capitalization
3. Wrong acronym capitalization (Api instead of API)
4. Missing capitalization on major words
5. Incorrect preposition capitalization
6. Random mixed case

### Negative Tests (Should NOT Flag)
1. Proper title case throughout
2. Consistent sentence case throughout
3. Correct acronym capitalization
4. Proper preposition handling
5. Correct article treatment
6. Appropriate verb capitalization

### Edge Cases
1. Hyphenated compound words
2. Acronyms in various positions
3. Long vs short prepositions
4. Verbs that look like prepositions
5. Technical terms and product names

## Implementation Checklist

### For Technical Writers
- [ ] Choose capitalization style (title case vs sentence case)
- [ ] Document style in style guide
- [ ] Create heading checklist
- [ ] Review existing headings for consistency
- [ ] Update non-compliant headings
- [ ] Configure Vale heading rules
- [ ] Train team on heading rules
- [ ] Monitor new content

### For Developers
- [ ] Configure Vale with heading rules
- [ ] Set capitalization style preference
- [ ] Define acronym exceptions
- [ ] Set up title case validation
- [ ] Create custom heading patterns
- [ ] Integrate into CI/CD
- [ ] Generate heading reports
- [ ] Automate fixes where possible

## Style Guide Recommendations

### Google Developer Documentation Style Guide
- **Preferred**: Sentence case for most headings
- **Exception**: API reference can use title case
- **Rationale**: Easier to write, more conversational

### Microsoft Writing Style Guide
- **Preferred**: Sentence case for most content
- **Exception**: Product names follow brand guidelines
- **Rationale**: Modern, accessible, easy to scan

### Traditional Technical Writing
- **Preferred**: Title case for formal documentation
- **Usage**: API docs, specifications, architecture docs
- **Rationale**: Professional, clearly delineated sections

## Benefits of Consistent Headings

### Readability
- Clear section boundaries
- Easier to scan document
- Better visual hierarchy

### Professionalism
- Polished appearance
- Attention to detail
- Consistent brand voice

### Accessibility
- Screen reader navigation
- Clear document structure
- Better user experience

### SEO
- Search engines use headings
- Better content categorization
- Improved discoverability

## Common Mistakes to Avoid

### Mistake 1: Inconsistent Style Within Document
**Bad:**
```markdown
## Getting Started    (title case)
## installing the software    (sentence case)
## API Reference    (title case)
```
**Fix:** Choose one style and apply consistently

### Mistake 2: Wrong Acronym Capitalization
**Bad:** ## Working with the Api
**Fix:** ## Working with the API

### Mistake 3: Over-Capitalizing Prepositions
**Bad:** ## Installing The Software On Your Server
**Fix:** ## Installing the Software on Your Server

### Mistake 4: Under-Capitalizing Verbs
**Bad:** ## How to be successful
**Fix:** ## How to Be Successful
**Reason:** "Be" is a verb, always capitalize

### Mistake 5: All Caps Headings
**Bad:** ## INSTALLATION INSTRUCTIONS
**Fix:** ## Installation Instructions
**Reason:** All caps reduces readability and appears like shouting

# Documentation Style Guide

## 1. Voice and Tone

### Voice (Consistent Across All Content)

Our voice is:
- **Professional yet approachable**: Technical but not intimidating
- **Developer-focused**: Written for experienced developers
- **Empathetic**: We understand your challenges
- **Precise**: Technically accurate and specific
- **Active**: Preferring action over passive statements

### Tone (Varies by Context)

**Tutorials**: Educational, encouraging, patient
- Help users succeed
- Celebrate milestones
- Acknowledge difficulties

**API Reference**: Precise, technical, comprehensive
- Be exact about parameters
- Explain edge cases
- Include all details

**Error Messages**: Helpful, non-blaming, actionable
- Never blame the user
- Explain what went wrong
- Suggest solutions

**Marketing**: Enthusiastic, benefit-focused, confident
- Emphasize value
- Show what's possible
- Build excitement

### Examples

❌ **Wrong** (too casual for API docs):
"Yo, here's how to charge someone for stuff"

❌ **Wrong** (too formal for tutorials):
"The aforementioned operation shall be executed in the subsequent manner"

✅ **Right** (professional, clear):
"To create a charge, send a POST request to the `/charges` endpoint with the amount in cents."

---

## 2. Grammar and Mechanics

### Active Voice

**Preferred**: Use active voice (subject performs action)

❌ Bad:
"The charge was created by the API"

✅ Good:
"The API creates the charge"

**Exception**: Passive voice is acceptable when:
- The action is more important than the actor
- The actor is obvious or irrelevant
- It's more concise

Acceptable passive: "Webhooks are automatically retried on failure"

### Present Tense

**Use present tense** for describing how things work, not future tense.

❌ Bad:
"When you call this endpoint, the charge will be created"

✅ Good:
"When you call this endpoint, the charge is created"

**Future tense** is only for:
- Features not yet available
- Scheduled changes
- Future deprecations

### Second Person ("You")

Use "you" and "your" to address the reader directly.

❌ Bad:
"Developers should ensure their API key is secure"

✅ Good:
"You should keep your API key secure"

### Oxford Comma

Always use the Oxford comma (comma before "and" in lists).

❌ Bad:
"authentication, rate limiting and error handling"

✅ Good:
"authentication, rate limiting, and error handling"

### Capitalization

**Sentence case** for headings (only capitalize first word and proper nouns):

❌ Bad:
"How To Create A Charge"

✅ Good:
"How to create a charge"

**Title Case** only for proper nouns and product names:
- ✅ "Create a Charge" (heading)
- ✅ "Express.js Framework"
- ✅ "PostgreSQL Database"

### Numbers

**Spell out** numbers zero through nine:
- ✅ "three examples"
- ✅ "100 requests per minute"

**Use numerals** for:
- 10 and above
- Amounts (prices, file sizes)
- Technical values

---

## 3. Terminology

### Standard Terms

| Instead of | Use | Notes |
|---|---|---|
| whitelist/blacklist | allowlist/blocklist | More inclusive language |
| slave/master | replica/primary | More inclusive language |
| guys | everyone, folks, team | More inclusive language |
| simply, just, easily | [omit] | Implies the reader should find it easy |
| actually, basically, obviously | [omit] | Condescending tone |
| click here | [action text] | More specific (e.g., "select Create") |
| ASAP, ASAP | by [date] | Be specific |
| might, may | will | Be confident |
| validate | check, verify | Depending on context |

### Product Names

Always use the exact name:
- ✅ Express.js (not "Express" alone in formal docs)
- ✅ Node.js (not "NodeJS" or "node")
- ✅ JavaScript (not "JS" except in code)
- ✅ Our Platform (use specific name: e.g., "Payment API")

### Technical Terms

Introduce technical terms clearly:

❌ Bad:
"Use JWT authentication"

✅ Good:
"Use JWT (JSON Web Token) authentication" (first mention)
"Use JWT authentication" (subsequent mentions)

---

## 4. Formatting Standards

### Code Formatting

**Inline code**: For variable names, function names, file names

```markdown
The `createCharge()` function takes an `amount` parameter.
```

**Code blocks**: For examples, longer snippets

```javascript
const charge = await createCharge({ amount: 2000 });
```

**Always** include language syntax highlighting

### Headings Hierarchy

- H1 (`#`): Page title (one per page)
- H2 (`##`): Major sections
- H3 (`###`): Subsections
- H4 (`####`): Small subsections

Avoid skipping levels: don't jump from H2 to H4

### Lists

**Use bullet points** for:
- Unordered items
- When order doesn't matter

**Use numbered lists** for:
- Steps in a process
- When order matters
- Instructions

Mix them carefully (can be confusing):

```markdown
## Setup Instructions

1. Install Node.js
2. Create a project:
   - Create a directory
   - Initialize npm
3. Install dependencies
```

### Tables

Use tables for comparisons and reference material:

| Feature | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| Requests/day | 10,000 | 100,000 | Unlimited |
| Support | Email | Priority | 24/7 Phone |
| SLA | 99% | 99.9% | 99.99% |

### Links

**Use descriptive link text** (not "click here")

❌ Bad:
"Click [here](https://docs.example.com/setup) to setup"

✅ Good:
"Follow the [setup guide](https://docs.example.com/setup)"

**Link to concepts** from code examples:

```
The `api_key` (see [authentication](/docs/authentication))
required for all requests.
```

---

## 5. Numbers and Dates

### Date Format

Use ISO 8601: **YYYY-MM-DD**

❌ Bad:
- 12/10/2025 (ambiguous: month/day or day/month?)
- 10th December 2025 (verbose)

✅ Good:
- 2025-12-10 (unambiguous and sortable)
- December 10, 2025 (when spelled out)

### Time Format

Include timezone:

❌ Bad:
- 2:00 PM (which timezone?)

✅ Good:
- 2:00 PM UTC
- 2:00 PM Pacific Time (UTC-8)
- 14:00 UTC

### Decimal Separators

Different locales use different separators:

❌ Bad:
1000000 (hard to read)

✅ Good:
1,000,000 (US/UK)
1.000.000 (EU)
1 000 000 (ISO)

**For documentation**: Use US format (1,000,000) as default, note locale variations

### Currency

Always include currency code, not just symbol:

❌ Bad:
$1,000 (ambiguous: USD, CAD, AUD?)

✅ Good:
$1,000 USD
€1,000 EUR
¥100,000 JPY

---

## 6. Inclusive Language

### Gender

Avoid gendered language:

❌ Bad:
- "He should check his API key"
- "A developer might forget his password"

✅ Good:
- "They should check their API key" (singular they)
- "A developer might forget their password"
- "You should check your API key"

### Ability

Avoid assumptions about ability:

❌ Bad:
- "Obviously, just use the API"
- "Simple one-line setup"
- "A blind man tried to use the API" (describing people)

✅ Good:
- "Use the API in this way"
- "One-line setup"
- "A person who is blind might need alt text"

### Ethnicity and Culture

Be respectful and descriptive:

❌ Bad:
- "American standard"
- "Chinese whispers"
- "Gyp someone" (from Gypsy)

✅ Good:
- "ISO standard"
- "Broken telephone" (or "broken telephone game")
- "Overcharge"

### Avoiding Slang

Use clear, standard English:

❌ Bad:
- "The API is sick" (Is it broken?)
- "That's lame" (Avoid slang)
- "Guys, here's the update"

✅ Good:
- "The API is powerful and efficient"
- "That approach has limitations"
- "Everyone, here's the update"

---

## 7. Localization Considerations

### Writing for Translation

Some languages expand text significantly:

| Language | Expansion |
|---|---|
| German | +30% longer |
| French | +20% longer |
| Japanese | -30% shorter |
| Chinese | -30% shorter |

**Guidelines**:
- Use short sentences
- Avoid idioms
- Be explicit about references
- Use complete words (avoid abbreviations)

### Avoiding Idioms

❌ Bad:
- "Go the extra mile"
- "Hit the ground running"
- "Move the needle"

✅ Good:
- "Provide extra effort"
- "Start immediately"
- "Create measurable impact"

### Date and Time Conventions

Specify format for translators:

```
Use ISO 8601 format: YYYY-MM-DD
Example: 2025-12-10
Do not translate month/day names
```

### Cultural References

Avoid cultural assumptions:

❌ Bad:
- "This is as easy as baseball"
- "In American English..."

✅ Good:
- "This is straightforward"
- "This terminology means..."

---

## 8. Tools

### Linting Tools

**Vale**: Prose linting
```bash
npm install -g vale
vale docs/*.md
```

**Markdownlint**: Markdown formatting
```bash
npm install -g markdownlint-cli
markdownlint docs/*.md
```

**cspell**: Spell checking
```bash
npm install -g cspell
cspell docs/**/*.md
```

### VS Code Extensions

- **Vale VSCode**: Real-time prose linting
- **Markdownlint**: Real-time markdown checking
- **Spell Right**: Spell checking
- **Grammarly**: Grammar checking (optional)

### CI/CD Integration

GitHub Actions workflow:

```yaml
name: Style Check

on: [pull_request]

jobs:
  style:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Vale
        uses: errata-ai/vale-action@v2

      - name: Markdownlint
        run: npm install -g markdownlint-cli && markdownlint docs/**/*.md

      - name: Spell Check
        run: npm install -g cspell && cspell docs/**/*.md
```

---

## 9. Quick Reference

### Do's
- ✅ Use active voice
- ✅ Use present tense
- ✅ Use second person ("you")
- ✅ Use simple words
- ✅ Use short sentences
- ✅ Use descriptive link text
- ✅ Use code examples
- ✅ Be specific about numbers
- ✅ Use Oxford commas
- ✅ Include timezone info

### Don'ts
- ❌ Use passive voice (unless necessary)
- ❌ Use future tense (unless describing future features)
- ❌ Use third person ("developers should")
- ❌ Use jargon without explanation
- ❌ Use long sentences
- ❌ Use "click here" as link text
- ❌ Assume reader knowledge
- ❌ Use ambiguous dates
- ❌ Skip Oxford commas
- ❌ Omit timezone info

---

## 10. Common Mistakes

### Apostrophes vs Contractions

**Avoid contractions** (don't, won't, can't):

```
don't ❌ → do not ✅
can't ❌ → cannot ✅
it's ❌ → it is ✅ (when referring to "it is")
it's ❌ → its ✅ (when possessive)
```

### Their vs There vs They're

- **their**: possessive (their API key)
- **there**: location (there are three options)
- **they're**: they are (they're developers)

### Affect vs Effect

- **affect**: verb (this affects your API)
- **effect**: noun (the effect is immediate)

### Its vs It's

- **its**: possessive (the API key is in its place)
- **it's**: contraction (it is)

Avoid contractions in documentation, so use "its".

---

## 11. Review Checklist

Before publishing documentation:

- [ ] Grammar and spelling correct
- [ ] Active voice used
- [ ] Present tense used (appropriate places)
- [ ] Inclusive language used
- [ ] Code examples tested and working
- [ ] Links verified
- [ ] Images included with alt text
- [ ] Headings hierarchical
- [ ] Terminology consistent
- [ ] Technical accuracy reviewed
- [ ] Target audience appropriate
- [ ] Localization considerations addressed

---

## Getting Help

- **Questions about style**: Check this guide
- **Grammar help**: Grammarly or Grammar Girl
- **Inclusive language**: 18F Content Guide (https://content-guide.18f.gov/)
- **Technical accuracy**: Assign to SME (Subject Matter Expert)
- **Localization**: Assign to localization team

---

## Updates to This Guide

This style guide is reviewed quarterly. To suggest changes:

1. Open an issue describing the suggestion
2. Reference relevant sections
3. Explain why the change improves documentation
4. Example of the proposed change

All changes require approval from the documentation team.

---

**Last Updated**: November 19, 2025
**Maintained By**: Documentation Team
**Next Review**: February 19, 2026

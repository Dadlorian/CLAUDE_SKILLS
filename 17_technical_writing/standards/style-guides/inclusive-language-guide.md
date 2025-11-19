# Inclusive Language Guide

## Purpose

Technical documentation should be accessible and welcoming to all readers. This guide establishes standards for inclusive language based on industry best practices from Google, Microsoft, GitLab, and academic research in technical communication.

**Goal**: Create documentation that is respectful, accessible, and inclusive to global audiences.

---

## Core Principles

### 1. **Write for a Global Audience**

Remember that readers come from diverse backgrounds:
- Different cultures and countries
- Various levels of English proficiency
- Different abilities and accessibility needs
- Diverse gender identities, races, and ethnicities

### 2. **Focus on Clarity**

Inclusive language often improves clarity for everyone:
- Simpler words are easier to translate
- Gender-neutral pronouns reduce ambiguity
- Avoiding idioms helps non-native speakers

### 3. **Avoid Assumptions**

Don't assume readers':
- Technical expertise level
- Cultural references
- Physical abilities
- Gender, race, or ethnicity

---

## Gender-Inclusive Language

### Pronouns

**Use "they" as singular pronoun**:

```markdown
✅ GOOD: "When a developer joins the team, they receive access credentials."
❌ AVOID: "When a developer joins the team, he receives access credentials."
❌ AVOID: "When a developer joins the team, he or she receives access credentials."
❌ AVOID: "When a developer joins the team, s/he receives access credentials."
```

**Rewrite to avoid pronouns entirely**:

```markdown
✅ BETTER: "New team members receive access credentials."
✅ BETTER: "Developers receive access credentials when joining the team."
```

### Job Titles and Roles

**Use gender-neutral job titles**:

| ❌ Avoid | ✅ Use |
|---------|--------|
| Manpower | Workforce, staff, personnel |
| Man-hours | Person-hours, work-hours, labor hours |
| Salesman | Sales representative, salesperson |
| Craftsman | Artisan, craftsperson |
| Spokesman | Spokesperson, representative |
| Mailman | Mail carrier, postal worker |

**Examples in context**:

```markdown
❌ AVOID: "The engineering team needs more manpower."
✅ GOOD: "The engineering team needs more engineers."

❌ AVOID: "A good salesman knows the product."
✅ GOOD: "Good sales representatives know the product."
```

### Collective Nouns

**Use inclusive collective nouns**:

| ❌ Avoid | ✅ Use |
|---------|--------|
| Guys | Everyone, folks, team, people |
| Ladies and gentlemen | Everyone, folks |
| Brothers and sisters | Siblings, community |

```markdown
❌ AVOID: "Hey guys, here's the new feature!"
✅ GOOD: "Team, here's the new feature!"
✅ GOOD: "Everyone, here's the new feature!"

❌ AVOID: "Welcome, ladies and gentlemen!"
✅ GOOD: "Welcome, everyone!"
```

---

## Race and Ethnicity

### Technical Terminology

**Replace racially-charged technical terms**:

| ❌ Avoid | ✅ Use | Context |
|---------|--------|---------|
| Master/slave | Primary/replica, main/subordinate, leader/follower | Databases, replication |
| Whitelist | Allowlist, permitted list | Access control |
| Blacklist | Blocklist, denied list | Access control |
| Blackhat/whitehat | Unethical hacker/ethical hacker | Security |
| Master branch | Main branch, primary branch | Version control |
| Grandfathered | Legacy status, prior implementation | Features |

**Real-world examples**:

```markdown
✅ Database Replication:
"Configure the primary database and replica instances."
(Not "master/slave")

✅ Access Control:
"Add the IP address to the allowlist."
(Not "whitelist")

✅ Git:
"Create a feature branch from main."
(Not "master")

✅ API Keys:
"These legacy API keys have continued access."
(Not "grandfathered in")
```

**Industry Changes**:
- **GitHub** (2020): Changed default branch from "master" to "main"
- **Python** (2018): Removed "master/slave" from documentation
- **Redis** (2020): Changed "master/slave" to "primary/replica"
- **MySQL** (2020): Changed "master/slave" to "source/replica"

---

## Ability and Accessibility

### Avoid Ableist Language

**Replace ableist terms**:

| ❌ Avoid | ✅ Use | Why |
|---------|--------|-----|
| Sanity check | Quick check, validation | "Sanity" is stigmatizing |
| Dummy value | Placeholder, example, sample | "Dummy" is derogatory |
| Cripple, gimp | Disable, break, impair | Offensive to disabled people |
| Blind to | Unaware of, ignores | Ableist |
| Lame | Weak, ineffective, broken | Ableist |

**Examples**:

```markdown
❌ AVOID: "Run a sanity check on the configuration."
✅ GOOD: "Validate the configuration."
✅ GOOD: "Run a quick verification of the configuration."

❌ AVOID: "Use a dummy value for testing."
✅ GOOD: "Use a placeholder value for testing."
✅ GOOD: "Use example data for testing."

❌ AVOID: "The system is blind to uppercase letters."
✅ GOOD: "The system is case-insensitive."
✅ GOOD: "The system ignores letter case."

❌ AVOID: "That's a lame excuse."
✅ GOOD: "That's an unconvincing reason."
```

### Describe Functionality, Not Disability

```markdown
❌ AVOID: "Screen readers for the blind"
✅ GOOD: "Screen readers for users with visual impairments"
✅ BETTER: "Screen readers"

❌ AVOID: "Voice control for disabled users"
✅ GOOD: "Voice control for users with mobility impairments"
✅ BETTER: "Voice control" (feature speaks for itself)
```

---

## Age and Experience

### Avoid Assumptions About Experience

```markdown
❌ AVOID: "This is simple for anyone."
❌ AVOID: "Obviously, you just need to..."
❌ AVOID: "Even a child could do this."
✅ GOOD: "To complete this task, follow these steps:"

❌ AVOID: "This is too complex for beginners."
✅ GOOD: "This advanced feature requires understanding of X and Y."

❌ AVOID: "Any programmer knows that..."
✅ GOOD: "In programming, this pattern is commonly used to..."
```

### Remove Condescending Qualifiers

**Avoid diminishing language**:

| ❌ Avoid | ✅ Use |
|---------|--------|
| Simply | *omit* |
| Just | *omit* |
| Easily | *omit* |
| Obviously | *omit* |
| Merely | *omit* |
| Clearly | *omit* |

**Examples**:

```markdown
❌ AVOID: "Simply configure the database connection."
✅ GOOD: "Configure the database connection."

❌ AVOID: "Just run npm install."
✅ GOOD: "Run npm install."

❌ AVOID: "You can easily set up authentication."
✅ GOOD: "Set up authentication by following these steps:"

❌ AVOID: "Obviously, you need to install Node.js first."
✅ GOOD: "Install Node.js before proceeding."
```

**Why this matters**:
- If it were "simple," they wouldn't need documentation
- Makes readers feel inadequate when they struggle
- "Simple" for experts may not be simple for beginners

---

## Cultural Sensitivity

### Avoid Cultural Idioms and References

**Idioms don't translate well**:

```markdown
❌ AVOID: "This is a piece of cake."
✅ GOOD: "This is straightforward."

❌ AVOID: "Let's touch base next week."
✅ GOOD: "Let's meet next week."

❌ AVOID: "We're comparing apples and oranges."
✅ GOOD: "We're comparing incompatible items."

❌ AVOID: "Don't put all your eggs in one basket."
✅ GOOD: "Use multiple deployment regions for redundancy."
```

### Avoid Culture-Specific References

```markdown
❌ AVOID: "The Super Bowl of tech conferences"
✅ GOOD: "The largest tech conference"

❌ AVOID: "Think of it like baseball..."
✅ GOOD: "Think of it as a series of steps where..."

❌ AVOID: "Unlike Thanksgiving dinner..."
✅ GOOD: "Unlike a traditional meal..."
```

### Date and Time Formats

**Use ISO 8601 for clarity**:

```markdown
❌ AVOID: "12/10/2025" (Is this Dec 10 or Oct 12?)
✅ GOOD: "2025-12-10" (December 10, 2025)
✅ GOOD: "December 10, 2025" (spelled out)

❌ AVOID: "The meeting is at 2:00 PM."
✅ GOOD: "The meeting is at 14:00 UTC."
✅ GOOD: "The meeting is at 2:00 PM Pacific Time (UTC-8)."
```

### Currency

**Specify currency codes**:

```markdown
❌ AVOID: "The service costs $10 per month."
✅ GOOD: "The service costs $10 USD per month."
✅ GOOD: "The service costs 10 USD per month."

❌ AVOID: "Transactions over $1,000..."
✅ GOOD: "Transactions over 1,000 USD..."
```

---

## Socioeconomic Assumptions

### Avoid Assuming Access to Resources

```markdown
❌ AVOID: "Open your MacBook and..."
✅ GOOD: "Open your computer and..."

❌ AVOID: "Use your iPhone to scan..."
✅ GOOD: "Use your mobile device to scan..."

❌ AVOID: "On your high-speed internet connection..."
✅ GOOD: "With an internet connection..."

❌ AVOID: "Take a break from your home office..."
✅ GOOD: "Take a break from work..."
```

---

## Violent and Aggressive Language

### Use Neutral Technical Terms

**Avoid violent imagery**:

| ❌ Avoid | ✅ Use |
|---------|--------|
| Kill the process | Stop, terminate, end the process |
| Abort | Cancel, stop |
| Hit the endpoint | Call, request, access the endpoint |
| Nuke the database | Delete, clear, wipe the database |
| Shoot an email | Send an email |

**Examples**:

```markdown
❌ AVOID: "Kill all running processes."
✅ GOOD: "Stop all running processes."
✅ GOOD: "Terminate all running processes."

❌ AVOID: "Abort the transaction."
✅ GOOD: "Cancel the transaction."

❌ AVOID: "Hit the API endpoint."
✅ GOOD: "Call the API endpoint."
✅ GOOD: "Send a request to the API endpoint."
```

**Note**: Some technical terms like "kill" are deeply embedded in operating systems and programming languages (e.g., `kill -9`). In these cases:
- Use the technical term when referring to the specific command: "Use `kill -9` to force-stop the process"
- Use neutral language in surrounding text: "To terminate a hung process, use the kill command"

---

## Additional Guidance

### Person-First vs. Identity-First Language

**For disabilities**, preferences vary:

**Person-first** (emphasizes the person):
- "Person with a disability"
- "Developer with low vision"

**Identity-first** (disability as part of identity):
- "Disabled person"
- "Blind developer"

**Best practice**: Follow the community's preference when known, otherwise use person-first language.

### Preferred Terminology by Community

When writing about specific communities, research their preferred terminology:

| Topic | Preferred | Avoid |
|-------|-----------|-------|
| Accessibility | Disabled people (identity-first in disability community) | Handicapped, special needs |
| Autism | Autistic person (identity-first preferred) | Person with autism (less preferred) |
| Deaf community | Deaf people (identity-first) | Hearing impaired |

**Important**: Terminology evolves. Review and update guidance regularly.

---

## Implementation

### Linting and Automation

**Use Vale for automated checking**:

```yaml
# .vale/styles/Inclusive/Terms.yml
extends: substitution
message: "Consider using '%s' instead of '%s'"
level: warning
ignorecase: true
swap:
  whitelist: allowlist
  blacklist: blocklist
  master: main
  slave: replica
  guys: folks
  sanity check: validation
  dummy: placeholder
```

### Review Checklist

When reviewing documentation:

**Gender**:
- [ ] Uses "they" as singular pronoun or rewrites to avoid
- [ ] Uses gender-neutral job titles
- [ ] Uses inclusive collective nouns (folks, everyone)

**Race/Ethnicity**:
- [ ] Uses "main" not "master" for Git
- [ ] Uses "allowlist/blocklist" not "whitelist/blacklist"
- [ ] Uses "primary/replica" not "master/slave"

**Ability**:
- [ ] No ableist terms (sanity, dummy, cripple, lame)
- [ ] Describes functionality, not disability

**Age/Experience**:
- [ ] No condescending qualifiers (simply, just, obviously)
- [ ] No assumptions about skill level

**Culture**:
- [ ] No idioms or cultural references
- [ ] Uses ISO 8601 dates
- [ ] Specifies currency codes
- [ ] Includes timezones

**Socioeconomic**:
- [ ] No assumptions about access to specific devices/resources

**Violence**:
- [ ] Uses neutral terms (stop/terminate vs. kill/abort)

---

## Resources

### Style Guides

- [Google Developer Documentation Style Guide - Inclusive Documentation](https://developers.google.com/style/inclusive-documentation)
- [Microsoft Style Guide - Bias-Free Communication](https://docs.microsoft.com/en-us/style-guide/bias-free-communication)
- [GitLab Documentation Style Guide - Language](https://docs.gitlab.com/ee/development/documentation/styleguide/#language)
- [Salesforce Style Guide - Inclusive Language](https://developer.salesforce.com/docs/atlas.en-us.salesforce_pubs_style_guide.meta/salesforce_pubs_style_guide/overview_inclusive.htm)

### Communities and Research

- **Write the Docs** - Community resources on inclusive documentation
- **A11Y Project** - Web accessibility community
- **WebAIM** - Web accessibility resources
- **W3C Accessibility Guidelines** - WCAG standards

### Tools

- **Vale** - Prose linter with inclusive language rules
- **alex** - Catch insensitive, inconsiderate writing
- **writeGood** - Linter for English prose

---

## Continuous Improvement

Inclusive language evolves with society:

1. **Stay Current**: Review this guide quarterly
2. **Listen to Communities**: Follow preferences of affected groups
3. **Gather Feedback**: Listen when readers point out non-inclusive language
4. **Update Proactively**: Don't wait for complaints to make changes
5. **Educate Teams**: Make inclusive language part of onboarding

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Review Cycle**: Quarterly
**Based on**: Google, Microsoft, GitLab style guides, disability community feedback

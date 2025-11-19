# Grammar Standards Guide

## Overview

Consistent grammar usage ensures clarity and maintains professional credibility. This guide covers the most common grammar decisions in technical documentation.

## Active vs. Passive Voice

### Active Voice Requirements

**Rule**: Use active voice in at least 80% of sentences. Active voice clearly attributes actions to actors.

**Structure**: [Subject] [Verb] [Object]

**Examples:**

Active (preferred):
- "Click the Save button"
- "The system encrypts your data"
- "We recommend updating every 90 days"

Passive (avoid):
- "The Save button should be clicked"
- "Your data is encrypted by the system"
- "It is recommended that updates be performed"

### When Passive Voice Is Acceptable

**1. Unknown or Unimportant Actor**
- "Your password has been reset" (by the system; unimportant who)
- "An error has been detected" (exact source isn't key)

**2. Emphasizing the Receiver**
- "You've been granted administrator privileges" (focus on recipient, not granter)

**3. Security/Privacy Concerns**
- "Account credentials are stored encrypted" (less important to name security systems)

**4. Logical Flow**
- Previous sentence ends with B, next sentence starts with B in passive form
- Acceptable to maintain paragraph coherence if overall voice remains active

### Identifying and Fixing Passive Voice

**Test**: Can you add "by [subject]" and still have a sentence?
- "The file was deleted" → "The file was deleted by the system" (passive)
- "Delete the file" → "Delete the file by the system" (doesn't work; active)

**Quick Fix Formula**:
- Passive: "The widget was created by the user"
- Active: "The user created the widget" OR "Create a widget"

## Verb Tense Consistency

### Present Tense (Default)

**Rule**: Use simple present tense for instructions, descriptions, and general statements.

**Examples:**
- "Click the button" (not "will click")
- "The system validates input" (not "will validate")
- "Users can configure settings" (not "will be able to configure")

**Why**: Present tense feels immediate and instructional, appropriate for documentation.

### Past Tense Usage

**Use past tense for:**
- Release notes and change logs
- Historical information
- Case studies and examples of completed actions

**Examples:**
- "We released version 2.0 with new features"
- "The API timeout issue was fixed in the last update"
- "Users reported connectivity problems on March 15"

### Present Perfect Tense

**Use sparingly**; choose simple past or present instead.

**Acceptable in**:
- Feature announcements: "We've redesigned the dashboard"
- Recent changes: "This guide has been updated for v3.0"

**Avoid in**:
- Instructions: Use present tense instead
- Technical specifications: Use simple present

**Examples:**
- Don't: "The configuration has been set to default"
- Do: "The configuration is set to default"

### Consistent Tense in Procedures

**In procedures, maintain present tense throughout:**

Good:
"1. Open the settings menu
2. Select 'Preferences'
3. Check the 'Auto-save' option
4. Click 'Save'"

Avoid mixing:
"1. Open the settings menu
2. You can select 'Preferences'
3. The 'Auto-save' option should be checked
4. Click 'Save'"

## Person (Perspective)

### Second Person Preferred

**Rule**: Address readers directly using "you" in instructions and explanations.

**Examples:**
- "You can configure this setting in the admin panel"
- "Enter your API key in the authentication field"
- "Your dashboard displays metrics from the last 30 days"

**Why**: Second person creates direct engagement and clarity about who performs actions.

### First Person Acceptable in Limited Contexts

**Use "we" when:**
- Representing organizational voice in explanations
- Sharing reasoning or philosophy
- Announcing features or changes

**Examples:**
- "We recommend this approach because..."
- "We've redesigned the interface for better usability"
- "We support the following programming languages..."

**Avoid**:
- "We will walk you through..." (verbose)
- "We see that you're having trouble..." (better: "Are you having trouble...")

### First Person Singular ("I") Rarely Used

**Exceptions:**
- Attributed quotes or bylines
- Blog posts or personal technical narratives
- Author's note in tutorials

**Generally avoid** in standard documentation: Makes content feel personal rather than organizational.

### Imperative (Command) Form

**Rule**: Use imperative mood for instructions.

**Structure**: [Verb] [object]

**Examples:**
- "Enter your email address"
- "Select the date range"
- "Navigate to the settings page"

**Benefits**:
- Clearest, most direct
- No ambiguity about who performs action
- Most concise

### Avoiding "One"

**Avoid**: "One should configure..."
**Use instead**: "You should configure..." or "Configure..."

## Subject-Verb Agreement

### Basic Rule

Singular subjects take singular verbs; plural subjects take plural verbs.

**Examples:**
- "The API accepts JSON payloads" (singular API)
- "All APIs accept JSON payloads" (plural APIs)
- "The team is prepared" (team = collective singular)
- "The team members are prepared" (members = plural)

### Common Errors in Technical Writing

**1. Collective Nouns**
- "The organization has 200 employees" (organization = singular)
- "The data are stored" vs. "The data is stored" (data can be singular or plural; singular is now standard)

**2. Compound Subjects**
- "The login page and dashboard are accessible" (two things; plural)
- "Either the server or the client is responsible" (singular verb for either/or)

**3. Indefinite Pronouns**
- "Everyone has access" (singular)
- "Some users have access" (plural)

**4. Titles and Names**
- "Best Practices for Security" is our guide (singular title)
- "The Processes" is a collection (verb depends on what "it" refers to)

## Pronoun Agreement and Reference

### Antecedent Clarity

**Rule**: Pronouns must clearly refer to their antecedents.

**Example (unclear):**
"Connect the cable to the port. This is essential for proper function."
- What does "this" refer to? The cable? The connection? The port?

**Better:**
"Connect the cable to the port. This connection is essential for proper function."

### Pronoun Gender

**Rule**: Use singular "they/their" instead of "he/she" or "he or she" for unknown individuals.

**Examples:**
- "When a user logs in, they see their dashboard" (not "he sees his" or "she sees her")
- "Each developer needs to update their configuration"

**Exception**: When referring to a specific known person, use their stated pronouns.

### Demonstrative Pronouns

**Avoid unclear demonstratives:**

Unclear:
- "Click the button. This will open the menu"
- "Set the timeout value. That's optional"

Clear:
- "Click the Preferences button. This opens the settings menu"
- "Set the timeout value. This setting is optional" (or "That's optional" works if obvious context)

**Best practice**: Repeat the noun or make antecedent explicit.

## Article Usage

### "The" vs. "A/An"

**Use "the"** for:
- Specific things mentioned before: "Create a file. The file will be saved..."
- Unique things: "Click the Save button", "Access the dashboard"
- Established entities: "The API", "The configuration"

**Use "a/an"** for:
- First mention of non-specific things: "Create a new user"
- Generalizations: "A user can have multiple projects"
- Indefinite references: "An error occurred"

**Examples:**
- "Click the Settings icon. A menu will appear with options"
- "Configure a connection to the database"
- "An email will be sent to your address"

### Dropping Articles in Technical Contexts

**Acceptable in tight technical contexts:**
- "Configure database credentials" (instead of "the database")
- "Enable API authentication" (instead of "the API")

**But maintain articles in explanatory text:**
- "The system validates the input against the schema" (clearer)
- "System validates input against schema" (too terse, harder to parse)

## Punctuation Standards

### Oxford Comma (Serial Comma)

**Rule**: Use Oxford comma in lists of three or more items.

**Example:**
- "Configure the host, port, and protocol" (use comma before "and")
- "Export as PDF, CSV, or Excel format"

**Rationale**: Prevents ambiguity in complex lists.

### Dashes vs. Hyphens

**Hyphen** (-): Joins compound words
- "Real-time processing"
- "End-user documentation"

**En-dash** (–): Ranges and connections
- "Pages 5–10"
- "The API–database connection"

**Em-dash** (—): For breaks or emphasis
- "The API—which handles authentication—requires a token"

### Colons

**Use colons to:**
- Introduce lists: "Configure these settings: [list]"
- Connect independent clauses: "The server is down: requests will fail"

**Don't use colon** after "including", "such as", "for example":
- "Data formats like JSON, XML, and YAML" (not with colon)

### Quotation Marks

**Use for:**
- String values in code: Enter the value `"production"`
- Terms being defined: The term "API endpoint" refers to...
- Exact user interface text: Click "Save Configuration"

**Commas and periods** go inside quotes (American English):
- "Save the file," then exit the application.

### Parentheses vs. Dashes

**Parentheses**: For supplementary information
- "Configure the timeout (default: 30 seconds) in the settings"

**Dashes**: For related but more emphatic breaks
- "The API has three versions—v1, v2, and v3—with different features"

## Common Grammar Mistakes in Technical Writing

### 1. "It's" vs. "Its"
- "It's" = "it is"
- "Its" = possessive form
- **Correct**: "The system updated its configuration. It's now running the latest version."

### 2. "That" vs. "Which"
- "That" = restrictive clause (essential information): "The file that you need is here"
- "Which" = non-restrictive clause (additional info): "The file, which has 500 lines, is ready"

### 3. "Ensure" vs. "Insure"
- "Ensure" = make certain: "Ensure your credentials are correct"
- "Insure" = provide insurance (rarely used): "Insure your data loss"

### 4. "If" vs. "Whether"
- Both can express conditions, but "whether" works for alternatives
- "Check whether the connection is active" (more formal)
- "If the connection is active, proceed" (more common in instructions)

### 5. Comma Splices
- **Wrong**: "Click Save, the menu closes"
- **Right**: "Click Save. The menu closes" or "Click Save; the menu closes"

## Consistency Checklist

- [ ] All instructions use imperative mood (verbs as commands)
- [ ] Main content uses active voice (80%+ of sentences)
- [ ] Consistent tense throughout each section (present for instructions)
- [ ] "You" is used when addressing readers
- [ ] All pronouns have clear antecedents
- [ ] Oxford commas used in lists
- [ ] Technical terms consistently capitalized
- [ ] No mixing of second and first person in instructions
- [ ] Articles consistent (not dropped unnecessarily)
- [ ] Subject-verb agreement checked

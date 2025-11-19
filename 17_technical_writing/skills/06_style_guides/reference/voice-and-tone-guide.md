# Voice and Tone Guide

## Overview

Voice is the consistent personality and style of your writing. Tone is the specific emotional coloring that changes based on context. Together, they create the reader's experience and perception of your organization.

## Organizational Voice Characteristics

### Core Voice Principles

**1. Professional yet Approachable**
- We write for subject matter experts AND newcomers
- Technical accuracy doesn't require cold, distant language
- Example (avoid): "Insufficient credentials provided for system access"
- Example (preferred): "You don't have permission to access this resource"

**2. Clear and Direct**
- Avoid unnecessary jargon or qualify technical terms
- Use simple words when they work as well as complex ones
- Example (avoid): "Utilize the authentication mechanism to facilitate system ingress"
- Example (preferred): "Log in to access your account"

**3. Active and Confident**
- Speak with authority while remaining helpful
- Use active voice to convey agency and clarity
- Example (avoid): "It is recommended that credentials be updated"
- Example (preferred): "Update your credentials every 90 days"

**4. User-Centered**
- Focus on what readers need to accomplish
- Address readers' concerns and pain points directly
- Example (avoid): "The system performs automatic backup operations"
- Example (preferred): "Your data is automatically backed up hourly"

## Tone Variations by Context

### Documentation Tone
- **Emotional quality**: Calm, reassuring, professional
- **Word choice**: Precise technical terms, clear definitions
- **Sentence structure**: Straightforward, direct
- **Use when**: Writing API documentation, guides, reference materials
- **Example**: "The API accepts JSON payloads and returns responses with standard HTTP status codes."

### Error Message Tone
- **Emotional quality**: Empathetic, solution-focused, non-blaming
- **Word choice**: Specific to the problem, no blame language
- **Sentence structure**: Short, actionable
- **Use when**: Communicating system failures or user mistakes
- **Example**: "Unable to connect. Check your internet connection and try again."

### Success/Celebration Tone
- **Emotional quality**: Warm, encouraging, positive
- **Word choice**: Affirming language, forward-looking
- **Sentence structure**: Can be slightly more casual
- **Use when**: Confirming task completion, welcoming users
- **Example**: "Great job! Your password has been securely updated."

### Urgent/Alert Tone
- **Emotional quality**: Clear sense of importance, not alarmist
- **Word choice**: Direct, unambiguous
- **Sentence structure**: Short, compelling
- **Use when**: Security alerts, critical system issues
- **Example**: "Security update required. Download the latest version to protect your account."

## Voice Elements: Specific Guidance

### Formality Level

Our voice operates at a **professional-casual** level:
- Use contractions in explanations: "Don't forget to..." (not "Do not forget")
- Avoid overly formal Latin phrases: "for example" (not "e.g.")
- Use "you" to address readers directly
- Avoid "one should..." constructions

### Personality Traits

**Honest**: We acknowledge limitations and unknowns
- Example: "While most integrations complete in under 5 minutes, yours may take longer if..."

**Helpful**: We anticipate questions and provide context
- Example: "Here's why we recommend this approach... [explanation]"

**Respectful**: We value readers' time and intelligence
- Example: We link to related docs rather than repeating content

**Inclusive**: We use language that welcomes diverse audiences
- Example: "In this example, we'll create a new workspace" (not "you guys")

### Prohibited Language

**Avoid:**
- Ableist language ("dumb terminal," "blind copy")
- Gendered pronouns for generic individuals
- Overly cute brand voice inconsistent with our professional positioning
- Profanity or crude expressions
- Condescending tone ("simply," "just," "obviously")

**Examples of problematic phrasing:**
- "Dummy data" → "Sample data"
- "He or she" → "They"
- "Yeah, you can totally..." → "You can..."
- "It's obvious that..." → "Consider that..."

## Tone Calibration Framework

### High Empathy Situations
- Account compromises
- Data loss
- Service outages
- Technical errors by users
- **Approach**: Acknowledge the situation, take responsibility where applicable, provide clear solutions

### High Authority Situations
- Security best practices
- Compliance requirements
- Critical warnings
- Legal terms
- **Approach**: Confident, clear, unambiguous language

### High Clarity Situations
- Initial onboarding
- Complex technical concepts
- Error explanations
- Setup instructions
- **Approach**: Break down concepts, use examples, define terms

## Examples: Applying Voice and Tone

### Scenario 1: Feature Announcement
**Context**: New feature, positive news, user-facing

Good:
"We're excited to share that payments processing is now 40% faster. You'll notice transactions complete almost instantly, making the checkout experience smoother for you and your customers."

Why: Uses "we're excited," acknowledges benefits to both parties, forward-looking language

### Scenario 2: Deprecation Notice
**Context**: Removing functionality, requires user action

Good:
"Starting [date], we'll be retiring the API v1 endpoint to allow our team to focus on newer, more capable services. Here's how to migrate your integration to v2 in under 30 minutes: [link]"

Why: Explains the "why," provides timeline, empowers users with clear migration path

### Scenario 3: Security Advisory
**Context**: Potential risk, urgent but measured response needed

Good:
"We've identified a security issue that may affect your account. We've reset your access token and recommend updating your password. Full details and next steps: [link]"

Why: Direct, action-oriented, provides context and resources, takes responsibility

### Scenario 4: Troubleshooting Guide
**Context**: User in problem-solving mode, may be frustrated

Good:
"Connection timeouts often happen with older credentials. Try removing and re-adding your connection using the newest format. Still having issues? [Contact support]"

Why: Offers specific solution, acknowledges the frustration implicitly, provides escalation path

## Creating Consistent Voice Across Teams

### Voice Checklist for Content Creation
- [ ] Would a real person use these words in this situation?
- [ ] Have I addressed the reader directly ("you")?
- [ ] Is the emotional tone appropriate to the context?
- [ ] Could I cut words and still be clear?
- [ ] Would users feel respected reading this?

### Voice Review Questions
- Does this sound like us?
- Does it feel appropriate for the situation?
- Could it be misunderstood or seen as disrespectful?
- Is there a simpler way to say this?
- Does it help the user feel confident?

## Voice and Tone Maintenance

### Regular Audits
- Review high-traffic pages quarterly
- Check error messages for consistency
- Monitor user feedback for voice-related concerns
- Update examples to reflect current product reality

### Team Training
- Include voice and tone in onboarding
- Reference specific examples when giving feedback
- Celebrate good voice examples in team retrospectives
- Create template snippets that embody the voice

### Tools and Resources
- Store approved phrases and terminology in shared docs
- Use style guide checks in pull request reviews
- Reference this guide when discussing content feedback
- Update examples when new situations arise

# Test: Contractions

This file is used to test the TechWriter.Contractions rule. It identifies and flags contractions in technical documentation where formal tone is required. While contractions are acceptable in conversational contexts, formal documentation typically avoids them for clarity, professionalism, and international audiences.

## Rule Purpose

### Why Avoid Contractions
Contractions can be problematic in technical documentation:
- **Formal tone**: Professional documentation requires formal language
- **International audiences**: Non-native speakers may struggle with contractions
- **Translation**: Contractions complicate translation workflows
- **Ambiguity**: Some contractions are confusing (e.g., "it's" vs "its")
- **Screen readers**: Accessibility tools may misinterpret contractions
- **Search**: Harder to find content when terms vary (can't vs cannot)

### When Contractions Are Acceptable
- Casual blog posts or tutorials
- Direct user interface text (buttons, messages)
- Conversational chatbot responses
- Marketing and sales materials
- Code comments (contextual)
- Quoted speech or dialogue

## Bad Examples - Contractions (Should Flag)

### Negative Contractions
- Don't use that approach. (CONTRACTION - should expand to "do not")
- You can't modify this setting. (CONTRACTION - should expand to "cannot")
- The system won't restart automatically. (CONTRACTION - should expand to "will not")
- We didn't implement that feature. (CONTRACTION - should expand to "did not")
- They haven't updated the documentation. (CONTRACTION - should expand to "have not")
- The API doesn't support this method. (CONTRACTION - should expand to "does not")
- Users shouldn't modify these files. (CONTRACTION - should expand to "should not")
- The service isn't available. (CONTRACTION - should expand to "is not")

### "To Be" Contractions
- It's important to understand. (CONTRACTION - should expand to "it is")
- That's the configuration format. (CONTRACTION - should expand to "that is")
- There's a bug in the code. (CONTRACTION - should expand to "there is")
- Here's the solution. (CONTRACTION - should expand to "here is")
- What's the expected behavior? (CONTRACTION - should expand to "what is")
- Where's the documentation? (CONTRACTION - should expand to "where is")
- Who's responsible for this? (CONTRACTION - should expand to "who is")

### "Have" Contractions
- You've installed the package. (CONTRACTION - should expand to "you have")
- We've updated the API. (CONTRACTION - should expand to "we have")
- They've fixed the bug. (CONTRACTION - should expand to "they have")
- I've configured the system. (CONTRACTION - should expand to "I have")
- It's been deprecated since v2.0. (CONTRACTION - should expand to "it has been")

### "Would/Will" Contractions
- You'll need to restart. (CONTRACTION - should expand to "you will")
- This'll take some time. (CONTRACTION - should expand to "this will")
- We'd recommend using HTTPS. (CONTRACTION - should expand to "we would")
- You'd better backup your data. (CONTRACTION - should expand to "you would")
- That'll work for most cases. (CONTRACTION - should expand to "that will")

### "Are" Contractions
- You're using the correct version. (CONTRACTION - should expand to "you are")
- We're implementing new features. (CONTRACTION - should expand to "we are")
- They're available in the dashboard. (CONTRACTION - should expand to "they are")

## Good Examples - Expanded Forms (Should NOT Flag)

### Expanded Negative Forms
- Do not use that approach.
- You cannot modify this setting.
- The system will not restart automatically.
- We did not implement that feature.
- They have not updated the documentation.
- The API does not support this method.
- Users should not modify these files.
- The service is not available.

### Expanded "To Be" Forms
- It is important to understand.
- That is the configuration format.
- There is a bug in the code.
- Here is the solution.
- What is the expected behavior?
- Where is the documentation?
- Who is responsible for this?

### Expanded "Have" Forms
- You have installed the package correctly.
- We have updated the API endpoints.
- They have fixed the critical bug.
- I have configured the system settings.
- It has been deprecated since version 2.0.

### Expanded "Would/Will" Forms
- You will need to restart the service.
- This will take some time to complete.
- We would recommend using HTTPS protocol.
- You would benefit from backing up your data.
- That will work for most use cases.

### Expanded "Are" Forms
- You are using the correct version.
- We are implementing new features.
- They are available in the admin dashboard.

## Edge Cases - NOT Contractions

### Possessives (Should NOT Flag)
- The user's profile is private. (POSSESSIVE - not a contraction)
- The system's performance is good. (POSSESSIVE - not a contraction)
- The API's response time is fast. (POSSESSIVE - not a contraction)
- Each developer's environment differs. (POSSESSIVE - not a contraction)
- The server's uptime is excellent. (POSSESSIVE - not a contraction)

**Rule:** Possessive apostrophes are NOT contractions and should not be flagged.

### Technical Terms with Apostrophes
- Don't repeat yourself (DRY) principle. (Principle name - may be excepted)
- Use the 'strict' mode. (Quoting code value - not a contraction)
- The '90s saw major changes. (Decade abbreviation - not a contraction)

### Literal Quotes (Context-Dependent)
```javascript
// Don't modify this configuration
const message = "Don't panic!";
```

**Status:** Code examples may be exempt from contraction rules
**Reason:** Changing code breaks syntax and meaning

## Testing Strategy

### Positive Tests (Should Flag All Contractions)
1. Common negatives: don't, can't, won't, didn't, haven't
2. To be: it's, that's, there's, here's, what's
3. Have: you've, we've, they've, I've
4. Would/will: you'll, this'll, we'd, that'll
5. Are: you're, we're, they're
6. Mixed case: DON'T, Don'T, don't

### Negative Tests (Should NOT Flag)
1. Possessives: user's, system's, API's
2. Expanded forms: do not, cannot, will not
3. Technical terms in quotes
4. Plurals: APIs, URLs, SDKs
5. Code examples (contextual)

### Ambiguity Tests
- "it's" vs "its" (contraction vs possessive)
- "you're" vs "your" (contraction vs possessive)
- "they're" vs "their" (contraction vs possessive)

## Real-World Documentation Examples

### Bad: Informal Technical Documentation
You'll need to install the package before you can start. It's important that you don't skip the configuration step. If you're unsure, there's a troubleshooting guide that'll help. We've made it simple so you won't have issues.

**Issues:** Multiple contractions, informal tone, unprofessional
**Word Count:** 42 words with 8 contractions

### Good: Formal Technical Documentation
You will need to install the package before you can start. It is important that you do not skip the configuration step. If you are unsure, there is a troubleshooting guide that will help. We have made it simple so you will not have issues.

**Improvements:** All contractions expanded, professional tone, clear for all audiences
**Word Count:** 50 words (19% longer but clearer)

### Bad: API Documentation with Contractions
The API won't accept requests that don't include authentication. You'll get an error if you're not providing valid credentials. It's required for all endpoints, and there's no way to bypass it.

**Issues:** Informal, unclear to non-native speakers
**Professionalism:** Low

### Good: API Documentation Without Contractions
The API will not accept requests that do not include authentication. You will receive an error if you are not providing valid credentials. It is required for all endpoints, and there is no way to bypass it.

**Improvements:** Clear, professional, accessible to international audiences
**Professionalism:** High

## Implementation Checklist

### For Technical Writers
- [ ] Review all documentation for contractions
- [ ] Decide on contraction policy (formal vs conversational)
- [ ] Update style guide with contraction rules
- [ ] Configure Vale to flag contractions
- [ ] Create exceptions for UI text or marketing
- [ ] Train team on formal writing standards
- [ ] Review and fix existing content
- [ ] Monitor new content for compliance

### For Developers
- [ ] Set up Vale contraction detection rules
- [ ] Configure severity level (warning vs error)
- [ ] Define exceptions for code examples
- [ ] Integrate into documentation workflow
- [ ] Add pre-commit hooks
- [ ] Generate contraction reports
- [ ] Automate expansion suggestions
- [ ] Track compliance metrics

## Style Guide Variations

### Formal Documentation (No Contractions)
- API Reference
- Technical Specifications
- Architecture Documents
- Security Guidelines
- Compliance Documentation
- Legal Terms

### Conversational Documentation (Contractions Allowed)
- Blog Posts
- Tutorial Narratives
- Getting Started Guides (contextual)
- UI Button Text
- Chatbot Responses
- Marketing Materials

### Hybrid Approach (Selective Use)
- User Guides (mostly formal, occasional conversational)
- Quickstart Tutorials (friendly but professional)
- FAQ Pages (can be more conversational)

## Benefits of Avoiding Contractions

### Professionalism
- **With contractions:** "You can't access this feature"
- **Without contractions:** "You cannot access this feature"
- **Impact:** More authoritative and professional

### Clarity for Non-Native Speakers
- **With contractions:** "It's important that you don't..."
- **Without contractions:** "It is important that you do not..."
- **Impact:** Clearer understanding, reduced ambiguity

### Translation Friendliness
- **With contractions:** Requires expansion before translation
- **Without contractions:** Ready for translation
- **Impact:** Reduced translation time and cost

### Accessibility
- **With contractions:** May confuse screen readers
- **Without contractions:** Clear pronunciation
- **Impact:** Better accessibility for all users

## Common Objections Addressed

### "But it sounds too formal and stiff"
**Response:** Technical documentation should be professional. Conversational tone comes from structure and examples, not contractions.

### "Users prefer friendly, conversational docs"
**Response:** Friendly doesn't require contractions. Clear examples, helpful guidance, and good structure create friendly docs.

### "It makes documentation longer"
**Response:** Typically only 10-20% longer, but significantly clearer for international and accessibility audiences.

### "Our competitors use contractions"
**Response:** Professional standards matter. Many leading tech companies (Google, Microsoft) avoid contractions in formal API docs.

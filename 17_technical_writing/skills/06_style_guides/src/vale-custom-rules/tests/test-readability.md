# Test: Sentence Length and Readability

This file is used to test the TechWriter.Readability rule. It validates that sentences are concise, clear, and easy to understand. The rule typically flags sentences over 25-30 words as potentially problematic.

## Test Configuration

**Rule Parameters:**
- Maximum sentence length: 25 words (recommended)
- Complexity threshold: 3 clauses maximum
- Readability target: 8th-grade reading level

## Good Examples - Clear and Concise

### Technical Instructions
This is short. This is good. Use clear language. Keep sentences focused.

### API Documentation
The endpoint accepts GET requests. It returns JSON data. Authentication is required. Rate limiting applies to all requests.

### Configuration Guide
Set the timeout value to 30 seconds. Save your changes. Restart the service. Verify the configuration works correctly.

### Error Messages
Connection failed. Check your network settings. Retry the operation. Contact support if the problem persists.

## Bad Examples - Long and Complex Sentences

### Problem: Run-on Sentences
This incredibly long sentence contains far too many clauses and concepts strung together with multiple conjunctions and references making it very difficult for readers to parse and understand the intended message without having to re-read it multiple times because it lacks proper structure and organization.

**Issue:** 51 words, multiple clauses, no punctuation breaks
**Impact:** Reader fatigue, comprehension difficulty, professional image degradation

### Problem: Nested Complexity
The configuration system which was originally designed for simple use cases but has evolved over time to handle increasingly complex scenarios including multiple data types various validation rules nested structures and integration with external systems all managed through a single interface that attempts to be both comprehensive and user-friendly.

**Issue:** 53 words, deeply nested clauses, unclear subject-verb relationships
**Impact:** Confusion, misinterpretation, increased support burden

### Problem: Excessive Subordination
When you initialize the application, which requires proper authentication credentials that must be obtained from the administrative portal before you can proceed, you should ensure that all configuration parameters have been properly set according to the deployment environment specifications that were provided during the onboarding process.

**Issue:** 49 words, multiple dependent clauses, buried main action
**Impact:** Lost main point, reader confusion, action unclear

### Problem: List Disguised as Prose
The API supports multiple authentication methods including OAuth 2.0 for modern applications and API keys for legacy systems and also provides support for JWT tokens which can be used in microservices architectures and basic authentication which while not recommended is still supported for backward compatibility purposes.

**Issue:** 50 words, should be a bulleted list, information overload
**Impact:** Skipping content, missing important details, poor accessibility

## Better Approaches - Refactored for Clarity

### Example 1: Break Into Multiple Sentences
**Before (51 words):**
This incredibly long sentence contains far too many clauses and concepts strung together with multiple conjunctions and references making it very difficult for readers to parse and understand the intended message without having to re-read it multiple times because it lacks proper structure and organization.

**After:**
This sentence is too long. It contains too many clauses strung together. Multiple conjunctions make it difficult to parse. Readers must re-read it multiple times. Better structure improves comprehension.

**Result:** 5 clear sentences averaging 8 words each

### Example 2: Focus Each Sentence
**Before (53 words):**
The configuration system which was originally designed for simple use cases but has evolved over time to handle increasingly complex scenarios including multiple data types various validation rules nested structures and integration with external systems all managed through a single interface that attempts to be both comprehensive and user-friendly.

**After:**
The configuration system is comprehensive. It handles multiple data types. It supports various validation rules. It manages nested structures. It integrates with external systems. All features are accessible through a single interface.

**Result:** 6 focused sentences, each with one main idea

### Example 3: Front-Load the Action
**Before (49 words):**
When you initialize the application, which requires proper authentication credentials that must be obtained from the administrative portal before you can proceed, you should ensure that all configuration parameters have been properly set according to the deployment environment specifications that were provided during the onboarding process.

**After:**
Initialize the application with these steps. First, obtain authentication credentials from the admin portal. Next, configure parameters for your deployment environment. Refer to the onboarding specifications for correct values.

**Result:** 4 clear sentences with actionable steps

### Example 4: Use Lists for Multiple Items
**Before (50 words):**
The API supports multiple authentication methods including OAuth 2.0 for modern applications and API keys for legacy systems and also provides support for JWT tokens which can be used in microservices architectures and basic authentication which while not recommended is still supported for backward compatibility purposes.

**After:**
The API supports multiple authentication methods:
- OAuth 2.0 (recommended for modern applications)
- JWT tokens (ideal for microservices)
- API keys (for legacy systems)
- Basic authentication (deprecated, backward compatibility only)

**Result:** Clear, scannable list with context for each option

## Edge Cases and Special Scenarios

### Technical Terms and Abbreviations
The REST API provides CRUD operations for managing user accounts through HTTP endpoints using JSON payloads with optional XML support for legacy integrations.

**Status:** Acceptable at 22 words despite multiple technical terms
**Reason:** Terms are standard in technical documentation, sentence remains clear

### Code Examples in Prose
The `getUserById()` method accepts an integer parameter representing the user ID and returns a user object containing name, email, and registration date properties or null if the user is not found.

**Status:** Borderline at 31 words
**Better:** Split into description and behavior: "The `getUserById()` method accepts an integer user ID parameter. It returns a user object with name, email, and registration date. The method returns null if the user is not found."

### Complex Requirements
The system validates input data by checking field types, enforcing length constraints, applying regex patterns, verifying referential integrity, and rejecting malformed requests with descriptive error messages.

**Status:** Acceptable at 25 words - clear list of related actions
**Alternative:** Use a bulleted list if emphasis is needed

## Testing Guidelines

### How to Use This File
1. Run Vale against this file: `vale test-readability.md`
2. Verify flagged sentences match "Bad Examples" section
3. Confirm "Good Examples" pass without warnings
4. Check edge cases produce expected results

### Expected Vale Output
- Bad Examples: Should flag ALL sentences in this section
- Good Examples: Should NOT flag any sentences in this section
- Better Approaches (After): Should pass validation
- Edge Cases: Follow documented expected behavior

### Rule Tuning Recommendations
- Adjust word count threshold based on audience
- Technical audiences: 30-35 words may be acceptable
- General audiences: 20-25 words recommended
- Consider domain-specific terminology exceptions

## Real-World Documentation Patterns

### Installation Instructions (Good)
Download the installer. Run the setup wizard. Accept the license agreement. Choose your installation directory. Click Install to begin.

### Configuration Steps (Good)
Open the config file. Locate the database section. Update the connection string. Save your changes. Restart the application.

### API Response Documentation (Good)
The endpoint returns a 200 status code on success. The response body contains JSON data. The data structure matches the schema. Error responses include descriptive messages.

### Troubleshooting Guide (Good)
Check the error logs first. Look for exception messages. Note the timestamp. Search the knowledge base. Contact support if needed.

## Performance Impact Metrics

**Readability Benefits:**
- 40% reduction in support tickets
- 60% faster task completion time
- 85% user satisfaction rating
- 50% fewer documentation updates needed

**Before/After Comparison:**
- Average sentence length: 45 words → 18 words
- Reading level: College → 8th grade
- Time to comprehend: 45 seconds → 15 seconds
- Error rate: 30% → 5%

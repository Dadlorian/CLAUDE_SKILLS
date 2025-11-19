# Exploratory Testing Guide

## What is Exploratory Testing?

Simultaneous learning, test design, and test execution.

## Session-Based Testing

**Structure**:
- Charter: What to test and why (15-90 minutes)
- Time-box: Fixed duration session
- Debrief: Document findings

**Example Charter**:
```
Explore: User authentication flow
With: Invalid credentials, SQL injection, XSS
To discover: Security vulnerabilities and edge cases
```

## Testing Heuristics

**SFDPOT** (San Francisco Depot):
- **Structure**: Test data structures, files, URLs
- **Function**: Test individual functions, features
- **Data**: Test with various data inputs
- **Platform**: Test on different platforms, browsers
- **Operations**: Test different user operations
- **Time**: Test timing, sequences, interruptions

**CRUD**:
- **Create**: Can user create new items?
- **Read**: Can user view/read items?
- **Update**: Can user modify items?
- **Delete**: Can user remove items?

**FEW HICCUPS**:
- **F**amiliar features
- **E**rror handling
- **W**orkflow interruptions  
- **H**elp system
- **I**nput validation
- **C**oncurrency
- **C**onfiguration
- **U**pdate/upgrade
- **P**erformance
- **S**ecurity

## Exploration Techniques

**Tours** (James Whittaker):

1. **Guidebook Tour**: Follow user documentation
2. **Money Tour**: Test revenue-generating features
3. **Landmark Tour**: Test major features
4. **Intellectual Tour**: Test complex features
5. **FedEx Tour**: Test data flow through system
6. **Back Alley Tour**: Test rarely used features
7. **Museum Tour**: Test legacy features
8. **Bad Neighborhood Tour**: Test error-prone areas

## Note-Taking

**PROOF**:
- **P**ast: What was tested before
- **R**esults: What happened
- **O**bstacles: What blocked testing
- **O**utlook: What's next
- **F**eelings: Confidence level

## Reporting Findings

**Bug Report from Exploration**:
```markdown
**Session**: User Profile Editing
**Duration**: 45 minutes
**Findings**: 3 bugs, 2 improvements

**Bug 1**: Profile photo upload fails for images > 5MB
**Bug 2**: Special characters in bio cause error
**Bug 3**: Cannot save without changing required fields

**Improvements**:
- Add character counter for bio field
- Show image size before upload
```

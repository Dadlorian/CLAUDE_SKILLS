# Code Review Guide
## Comprehensive Peer Review Process for Quality Code

---

## 🎯 Purpose

Code review is **the single most effective way** to improve code quality, share knowledge, and maintain consistency across a codebase.

**Research shows**:
- Code review catches 60% of defects (Microsoft Research)
- Reviewed code has 50% fewer bugs long-term (IBM)
- Increases team knowledge sharing and code ownership
- Improves code readability and maintainability

---

## 📋 Quick Reference

### For Authors (Submitting Code)

```markdown
BEFORE submitting PR:
✅ All tests pass locally
✅ Code is formatted (Prettier/Black/gofmt)
✅ Linting passes
✅ Self-review completed
✅ PR description filled out
✅ Tests included for new features
✅ Documentation updated

DURING review:
✅ Respond to feedback promptly
✅ Ask clarifying questions
✅ Don't take feedback personally
✅ Push updates as new commits (don't force push)

AFTER approval:
✅ Merge using appropriate strategy
✅ Delete branch after merge
✅ Monitor deployment
```

### For Reviewers

```markdown
WHEN reviewing:
✅ Review within 24 hours
✅ Use checklist (see below)
✅ Be constructive and kind
✅ Explain the "why" behind suggestions
✅ Approve when ready, not perfect
✅ Use "Request Changes" for must-fix items

FOCUS on:
1. Correctness (does it work?)
2. Security (is it safe?)
3. Performance (is it fast enough?)
4. Maintainability (can we understand it?)
5. Tests (are they adequate?)
```

---

## 🔄 Code Review Process

### Step 1: Author Prepares PR

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/user-authentication
   ```

2. **Make Changes**
   - Follow coding standards
   - Write tests
   - Update documentation

3. **Self-Review**
   - Review your own diff
   - Check for forgotten console.logs, TODOs
   - Ensure tests pass
   - Run linter

4. **Create Pull Request**
   - Use PR template
   - Write descriptive title
   - Fill out description
   - Link related issues
   - Request reviewers

### Step 2: Reviewer Reviews

1. **Understand Context**
   - Read PR description
   - Understand the problem being solved
   - Check linked issues/tickets

2. **Review Code**
   - Use the review checklist
   - Leave comments
   - Suggest improvements
   - Ask questions

3. **Make Decision**
   - ✅ **Approve**: Code is good to merge
   - 💬 **Comment**: Suggestions, not blocking
   - ❌ **Request Changes**: Must be fixed before merge

### Step 3: Author Addresses Feedback

1. **Respond to Comments**
   - Answer questions
   - Make requested changes
   - Explain decisions if not changing

2. **Push Updates**
   ```bash
   git add .
   git commit -m "address review feedback"
   git push
   ```

3. **Re-request Review**
   - Notify reviewers updates are ready
   - Resolve conversations

### Step 4: Merge

1. **Final Checks**
   - All approvals received
   - CI passing
   - Conflicts resolved

2. **Merge**
   - Choose merge strategy (squash, rebase, or merge)
   - Delete branch
   - Close related issues

---

## ✅ Comprehensive Review Checklist

### 1. Correctness

```markdown
- [ ] Code does what it's supposed to do
- [ ] Edge cases are handled
- [ ] Error cases are handled
- [ ] Logic is sound
- [ ] No obvious bugs
- [ ] Async operations handled correctly
- [ ] Race conditions avoided
- [ ] Null/undefined checks where needed
```

### 2. Tests

```markdown
- [ ] Tests included for new features
- [ ] Tests included for bug fixes
- [ ] Tests cover edge cases
- [ ] Tests cover error cases
- [ ] Tests are clear and readable
- [ ] Tests are not flaky
- [ ] All tests pass
- [ ] Coverage hasn't decreased
- [ ] Integration tests if needed
```

### 3. Security

```markdown
- [ ] No hardcoded secrets/credentials
- [ ] Input validation present
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Authentication/authorization checked
- [ ] Sensitive data not logged
- [ ] HTTPS used for external calls
- [ ] No use of dangerous functions (eval, innerHTML)
- [ ] Dependencies are secure (no known vulnerabilities)
```

### 4. Performance

```markdown
- [ ] No N+1 database queries
- [ ] Appropriate indexes on database queries
- [ ] Pagination for large result sets
- [ ] Caching used where appropriate
- [ ] No unnecessary loops
- [ ] Efficient algorithms used
- [ ] No memory leaks
- [ ] Lazy loading where appropriate
- [ ] Debouncing/throttling for frequent operations
```

### 5. Code Quality

```markdown
- [ ] Follows coding standards
- [ ] Clear and descriptive naming
- [ ] Functions have single responsibility
- [ ] No code duplication (DRY)
- [ ] No magic numbers (constants defined)
- [ ] Appropriate abstractions
- [ ] No overly complex functions
- [ ] Comments explain "why", not "what"
- [ ] No commented-out code
- [ ] No console.logs or debugger statements
```

### 6. Architecture & Design

```markdown
- [ ] Fits within existing architecture
- [ ] Appropriate separation of concerns
- [ ] No tight coupling
- [ ] Dependencies injected, not created
- [ ] Proper error handling
- [ ] Consistent with rest of codebase
- [ ] No circular dependencies
- [ ] Scalable solution
```

### 7. Maintainability

```markdown
- [ ] Code is readable
- [ ] Intent is clear
- [ ] Easy to modify in the future
- [ ] Consistent style
- [ ] Self-documenting where possible
- [ ] Complex logic explained
- [ ] No premature optimization
- [ ] YAGNI principle followed
```

### 8. Documentation

```markdown
- [ ] API documentation updated
- [ ] README updated if needed
- [ ] Inline comments for complex logic
- [ ] JSDoc/docstrings for public APIs
- [ ] Changelog updated
- [ ] Migration guide if breaking changes
- [ ] Runbook updated if needed
```

### 9. Deployment & Operations

```markdown
- [ ] Database migrations included if needed
- [ ] Backward compatible (or migration plan)
- [ ] Feature flags for risky changes
- [ ] Monitoring/logging added
- [ ] Alerting configured if needed
- [ ] Rollback plan considered
- [ ] Environment variables documented
```

### 10. Accessibility (if UI changes)

```markdown
- [ ] Keyboard navigable
- [ ] Screen reader compatible
- [ ] ARIA labels present
- [ ] Color contrast adequate (WCAG AA minimum)
- [ ] Focus indicators visible
- [ ] Semantic HTML used
- [ ] Forms have labels
- [ ] Error messages are accessible
```

---

## 💬 How to Give Effective Feedback

### Tone & Language

```markdown
✅ GOOD (Constructive):
"This function is doing multiple things. Consider splitting into separate functions for better testability."

"I'm concerned about performance here with the nested loop. Have you considered using a hash map instead?"

"Great use of the repository pattern here! One suggestion: we could add error handling for the database connection failure case."

❌ BAD (Destructive):
"This is wrong."
"Why did you do it this way?"
"This code is terrible."
"You should know better."
```

### The 3 Tiers of Feedback

**1. BLOCKING (Must fix before merge)**
```markdown
Prefix: 🚫 BLOCKING or ❌
Use for: Security issues, bugs, violated rules
Example: "🚫 BLOCKING: This allows SQL injection. Use parameterized queries."
```

**2. IMPORTANT (Should fix, but not blocking)**
```markdown
Prefix: ⚠️ IMPORTANT or 💡
Use for: Best practice violations, potential issues
Example: "💡 IMPORTANT: Consider adding input validation here to prevent invalid data."
```

**3. SUGGESTION (Nice to have, optional)**
```markdown
Prefix: 💭 SUGGESTION or ✨
Use for: Style preferences, alternative approaches
Example: "💭 SUGGESTION: You might find array.map() more readable here, but current approach works too."
```

### Praise & Recognition

```markdown
✅ DO give praise when you see good code:
"Love the clean separation of concerns here! 👏"
"Great test coverage on this feature! 🎉"
"Smart optimization - much better performance! 🚀"
"Excellent error handling! 💯"

Benefits of praise:
- Reinforces good practices
- Builds team morale
- Encourages authors
- Sets examples for others
```

---

## 🎯 Review Speed & Size

### Optimal PR Size

```yaml
Small PR (< 200 lines):
  Review Time: 30 minutes
  Quality: Excellent
  Speed: Fast approval

Medium PR (200-400 lines):
  Review Time: 1 hour
  Quality: Good
  Speed: Moderate approval

Large PR (> 400 lines):
  Review Time: 2+ hours
  Quality: Decreased (reviewer fatigue)
  Speed: Slow approval
  Recommendation: Break into smaller PRs
```

### Review SLA (Service Level Agreement)

```markdown
Priority 1 (Critical/Hotfix):
  First response: 2 hours
  Review completion: 4 hours

Priority 2 (Normal):
  First response: 4 hours
  Review completion: 24 hours

Priority 3 (Low priority):
  First response: 24 hours
  Review completion: 48 hours
```

**Why speed matters**:
- Keeps work fresh in author's mind
- Prevents context switching
- Enables faster iteration
- Improves team velocity

---

## 🎨 Code Review Techniques

### Technique 1: Checklist Review
Use the comprehensive checklist above systematically.

**Pros**: Thorough, consistent
**Cons**: Can be slow
**Best for**: Critical changes, junior reviewers

### Technique 2: Walkthrough
Author explains changes to reviewer(s) in real-time.

**Pros**: Fast, educational, catches misunderstandings
**Cons**: Synchronous, scheduling needed
**Best for**: Complex changes, architectural decisions

### Technique 3: Over-the-shoulder
Reviewer sits with author and reviews together.

**Pros**: Very fast, immediate discussion
**Cons**: Informal, no async record
**Best for**: Simple changes, pair programming

### Technique 4: Async Review (Standard)
Reviewer reviews PR independently, leaves comments.

**Pros**: Async, documented, scalable
**Cons**: Can be slow, misunderstandings possible
**Best for**: Most PRs, distributed teams

---

## 🚫 Common Code Review Anti-Patterns

### 1. Rubber Stamping
**What**: Approving without actually reviewing
**Why bad**: Defeats the purpose, lets bugs through
**Fix**: Take time to review properly or decline if too busy

### 2. Nitpicking
**What**: Only commenting on style/formatting
**Why bad**: Misses real issues, wastes time
**Fix**: Use automated tools for style, focus on logic

### 3. Ghost Reviewer
**What**: Requested but never reviews
**Why bad**: Blocks merging, frustrates author
**Fix**: Decline if can't review, set expectations

### 4. Design Discussion in PR
**What**: Debating architecture/approach in PR comments
**Why bad**: Too late, author already wrote code
**Fix**: Discuss design before implementation

### 5. Drive-by Comments
**What**: Leaving comments then disappearing
**Why bad**: No clarification, no resolution
**Fix**: Monitor PR, respond to author questions

### 6. Perfectionism
**What**: Blocking on minor style preferences
**Why bad**: Delays shipping, decreases morale
**Fix**: Distinguish must-fix from nice-to-have

### 7. Not Testing
**What**: Approving without running code locally
**Why bad**: Might not work as expected
**Fix**: Checkout branch and test critical changes

---

## 📊 Code Review Metrics

### Process Metrics

```yaml
Review Turnaround Time:
  Target: < 24 hours
  Measure: Time from PR creation to approval

PR Size:
  Target: < 400 lines changed
  Measure: Lines of code changed

Comments per PR:
  Typical: 5-15 comments
  Red flag: > 50 comments (PR too large or poor quality)

Iterations:
  Target: 1-2 rounds
  Red flag: > 5 rounds (design issues)
```

### Quality Metrics

```yaml
Defects Found:
  Measure: Issues caught in review vs production
  Target: 60% of defects caught in review

Review Coverage:
  Target: 100% of PRs reviewed before merge
  Measure: PRs merged without approval

Post-Merge Issues:
  Target: < 5% of PRs require follow-up fix
  Measure: Issues found after merge
```

---

## 🎓 Best Practices

### For Authors

**Before Submitting**:
1. Self-review your own PR first
2. Add meaningful description
3. Link to relevant tickets
4. Ensure CI is green
5. Keep PRs small and focused

**During Review**:
1. Respond to all comments
2. Ask for clarification when needed
3. Don't take criticism personally
4. Explain your reasoning
5. Be open to suggestions

**After Approval**:
1. Merge promptly
2. Monitor deployment
3. Be available for questions

### For Reviewers

**Mindset**:
1. Assume competence (author knows something you don't)
2. Ask questions, don't make demands
3. Be kind and constructive
4. Praise good code
5. Teach, don't preach

**Efficiency**:
1. Review promptly (< 24 hours)
2. Start with high-level concerns
3. Don't nitpick (use linter for style)
4. Batch comments (don't comment one-by-one)
5. Provide suggestions, not just problems

**Quality**:
1. Actually read the code (don't rubber stamp)
2. Test critical changes locally
3. Consider security implications
4. Think about edge cases
5. Verify tests are adequate

---

## 🔧 Tools & Automation

### GitHub/GitLab Features

```markdown
Use these features:
✅ PR templates (standardize descriptions)
✅ Required reviewers (enforce review)
✅ Code owners (domain experts auto-assigned)
✅ Protected branches (prevent direct push)
✅ Required status checks (CI must pass)
✅ Review suggestions (quick fixes)
✅ Draft PRs (work in progress)
```

### Automated Checks

```markdown
Before human review:
✅ Linting (ESLint, Pylint)
✅ Type checking (TypeScript, mypy)
✅ Tests (all must pass)
✅ Coverage (must not decrease)
✅ Security scan (Snyk, Semgrep)
✅ Format check (Prettier, Black)
```

### Review Assistance Tools

- **SonarQube**: Code quality analysis
- **CodeClimate**: Maintainability scoring
- **Codecov**: Coverage visualization
- **Danger**: Automated PR checks
- **Reviewable**: Enhanced review interface

---

## 🎯 Specialized Reviews

### Security Review

Required for:
- Authentication/authorization changes
- Payment processing
- PII handling
- API key/secret management
- Admin functionality

Checklist:
- [ ] OWASP Top 10 considerations
- [ ] Input validation
- [ ] Output encoding
- [ ] Access control
- [ ] Crypto usage (use established libraries)

### Performance Review

Required for:
- Database schema changes
- High-traffic endpoints
- Background jobs
- Complex queries

Checklist:
- [ ] Database indexes
- [ ] Query optimization
- [ ] Caching strategy
- [ ] Load tested
- [ ] Resource usage measured

### Architecture Review

Required for:
- New services/modules
- Major refactors
- Breaking changes
- Scalability concerns

Checklist:
- [ ] Aligns with system architecture
- [ ] Scalable design
- [ ] Backward compatible
- [ ] Migration strategy
- [ ] Documentation complete

---

## 📚 Learning Resources

### Books
- "The Art of Readable Code" - Boswell & Foucher
- "Code Complete" - Steve McConnell
- "Clean Code" - Robert C. Martin

### Articles
- "How to Do Code Reviews Like a Human" - Michael Lynch
- "Code Review Best Practices" - Palantir
- "Unlearning Toxic Behaviors in a Code Review Culture" - Sandya Sankarram

### Internal Resources
- [Review Checklist](review-checklist.md) - Detailed checklist
- [PR Template](pr-template.md) - Standard PR template
- [Reviewer Guidelines](reviewer-guidelines.md) - How to be a great reviewer

---

## 🎉 Success Criteria

Your code review process is successful when:

✅ **Fast**: Reviews completed within 24 hours
✅ **Effective**: Bugs caught in review, not production
✅ **Educational**: Team knowledge increases
✅ **Positive**: Developers enjoy the process
✅ **Consistent**: Similar standards across all reviews
✅ **Thorough**: Security, performance, maintainability checked
✅ **Collaborative**: Discussion, not dictation

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Review Cycle**: Quarterly
**Maintained By**: Engineering Team

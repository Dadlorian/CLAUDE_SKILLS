# Test: Deprecated Terms

This file is used to test the TechWriter.DeprecatedTerms rule. It identifies outdated, problematic, or non-inclusive terminology that should be replaced with modern, accurate alternatives. This is an ERROR-level rule, not a warning, because using deprecated terms can harm inclusivity, professionalism, and brand reputation.

## Rule Purpose

### Why Replace Deprecated Terms
Deprecated terms are problematic because they:
- **Perpetuate harmful language**: Terms with historical oppression connotations
- **Reduce inclusivity**: Create unwelcoming environments for diverse teams
- **Appear outdated**: Signal lack of awareness of modern standards
- **Risk brand damage**: Can lead to public criticism or controversy
- **Violate style guides**: Most major tech companies ban these terms
- **Fail accessibility**: Some terms are ableist or exclude communities

### Industry Standards
Major organizations that mandate these changes:
- Google Developer Style Guide
- Microsoft Writing Style Guide
- Red Hat supplementary style guide
- IETF (Internet Engineering Task Force)
- NIST (National Institute of Standards and Technology)
- Major cloud providers (AWS, Azure, GCP)

## Bad Examples - Deprecated Terms (Should Flag as ERROR)

### Database and Replication Terms
- Configure the master database. (DEPRECATED - should suggest "primary")
- Set up slave replicas. (DEPRECATED - should suggest "secondary" or "replica")
- The master node coordinates replication. (DEPRECATED - should suggest "primary")
- Configure slave instances for failover. (DEPRECATED - should suggest "replica")
- Enable master-slave replication. (DEPRECATED - should suggest "primary-replica")

### Access Control Terms
- Add the IP to the whitelist. (DEPRECATED - should suggest "allowlist")
- Remove the domain from the blacklist. (DEPRECATED - should suggest "blocklist")
- Whitelist these addresses. (DEPRECATED - should suggest "allow")
- The IP is blacklisted. (DEPRECATED - should suggest "blocked")
- Check the whitelist configuration. (DEPRECATED - should suggest "allowlist")
- Update the blacklist rules. (DEPRECATED - should suggest "blocklist")

### Testing and Verification Terms
- Perform a sanity check. (DEPRECATED - should suggest "verification" or "validation")
- Run a sanity test before deployment. (DEPRECATED - should suggest "smoke test" or "basic test")
- Do a quick sanity check on the config. (DEPRECATED - should suggest "quick check")
- Sanity testing is required. (DEPRECATED - should suggest "smoke testing")

### Git and Version Control Terms
- Merge to the master branch. (DEPRECATED - should suggest "main")
- Push to master. (DEPRECATED - should suggest "main")
- The master branch is protected. (DEPRECATED - should suggest "main")
- Create a branch from master. (DEPRECATED - should suggest "main")
- Update your master branch. (DEPRECATED - should suggest "main")

### Gender-Specific Terms
- Man hours required. (DEPRECATED - should suggest "person hours" or "work hours")
- Man-in-the-middle attack. (DEPRECATED - should suggest "machine-in-the-middle" or "MITM")
- Unmanned system. (DEPRECATED - should suggest "automated system")
- Manpower needed. (DEPRECATED - should suggest "workforce" or "staffing")

### Ableist Terms
- The crippled performance. (DEPRECATED - should suggest "degraded" or "impaired")
- Dummy variable. (DEPRECATED - should suggest "placeholder" or "sample")
- Dummy data. (DEPRECATED - should suggest "test data" or "sample data")
- Crazy amount of traffic. (DEPRECATED - should suggest "enormous" or "excessive")
- Insane performance gains. (DEPRECATED - should suggest "remarkable" or "exceptional")

### Native/Primitive Terms (Context-Dependent)
- Native app implementation. (ACCEPTABLE in technical context)
- Native code execution. (ACCEPTABLE in technical context)
- Use native APIs. (ACCEPTABLE in technical context)
- Primitive data types. (ACCEPTABLE in programming context)
- Primitive operations. (ACCEPTABLE in computer science context)

**Note:** "Native" and "primitive" are acceptable when referring to technical concepts (native code, primitive types) but should be avoided when referring to people or cultures.

### Grandfathered/Legacy Terms
- Grandfathered accounts. (DEPRECATED - should suggest "legacy accounts" or "existing accounts")
- Grandfathering clause. (DEPRECATED - should suggest "legacy exception")
- Grandfather old users in. (DEPRECATED - should suggest "migrate" or "transition")

## Good Examples - Modern Alternatives (Should NOT Flag)

### Database and Replication - Correct
- Configure the primary database.
- Set up secondary replicas.
- Set up replica instances.
- The primary node coordinates replication.
- Configure replica instances for failover.
- Enable primary-replica replication.

### Access Control - Correct
- Add the IP to the allowlist.
- Remove the domain from the blocklist.
- Allow these addresses.
- The IP is blocked.
- Check the allowlist configuration.
- Update the blocklist rules.

### Testing and Verification - Correct
- Perform a verification check.
- Perform a validation test.
- Run a smoke test before deployment.
- Do a quick check on the config.
- Smoke testing is required.
- Run basic functionality tests.

### Git and Version Control - Correct
- Merge to the main branch.
- Push to main.
- The main branch is protected.
- Create a branch from main.
- Update your main branch.

### Gender-Neutral Terms - Correct
- Person hours required.
- Work hours estimated.
- Machine-in-the-middle attack.
- MITM attack.
- Automated system.
- Workforce needed.
- Staffing requirements.

### Non-Ableist Terms - Correct
- The degraded performance.
- The impaired functionality.
- Placeholder variable.
- Sample variable.
- Test data.
- Sample data.
- Enormous amount of traffic.
- Exceptional performance gains.
- Remarkable improvements.

### Modern Legacy Terms - Correct
- Legacy accounts.
- Existing accounts.
- Legacy exception.
- Migrate old users.
- Transition existing users.
- Extend support to existing users.

## Context-Specific Guidance

### When "Master" Is Acceptable
- Master's degree (academic credential)
- Chess master (title/rank)
- Master key (physical security - though "primary key" is better)
- Mastering a skill (verb meaning to learn thoroughly)
- Remaster (audio/video production)

**Guideline:** Acceptable when not in primary/secondary relationship context

### When "Slave" Is NEVER Acceptable
There is NO acceptable technical use of "slave" in modern documentation. Always replace with:
- Replica
- Secondary
- Standby
- Follower
- Worker (in appropriate contexts)

### When "Whitelist/Blacklist" Should Change
**Always replace in:**
- Access control systems
- Security policies
- Network filtering
- Content moderation
- Email filtering

**Alternative approaches:**
- Allowlist/blocklist
- Permit list/deny list
- Allow/block (as verbs)
- Safe list/blocked list

### When "Sanity Check" Should Change
**Always replace with:**
- Verification check
- Validation test
- Smoke test (for basic functionality)
- Quick test
- Basic check
- Confidence check

## Edge Cases and Exceptions

### Historical References (Acceptable with Context)
When discussing historical systems or legacy code:
"The old system used master-slave replication. We've migrated to primary-replica architecture."

**Status:** Acceptable when:
1. Clearly historical reference
2. Immediately followed by modern alternative
3. Necessary for understanding migration

### Proper Nouns and Trademarks
- MySQL Master/Slave replication (legacy product feature)
- GitHub renaming from "master" to "main"

**Guideline:**
- Reference legacy terms when necessary for compatibility
- Always note the modern alternative
- Update to new terms when available

### Academic and Standards Documents
- IETF RFCs using old terminology
- IEEE standards with legacy terms

**Guideline:**
- Quote accurately but note deprecation
- Use modern terms in your own documentation
- Advocate for standards updates

## Testing Strategy

### Positive Tests (Should Flag as ERROR)
1. All master/slave database terminology
2. All whitelist/blacklist terminology
3. All sanity check variations
4. Git master branch references
5. Gender-specific terms (man hours, manpower)
6. Ableist terms (crippled, dummy, crazy)
7. Grandfathered terminology

### Negative Tests (Should NOT Flag)
1. Primary/secondary, main branch
2. Allowlist/blocklist
3. Verification/smoke test
4. Gender-neutral alternatives
5. Non-ableist alternatives
6. Technical use of "native" and "primitive"

### Severity Tests
1. Verify ERROR level (not warning)
2. Check replacement suggestions are correct
3. Ensure clear explanation of why term is deprecated
4. Validate suggested alternatives work in context

## Migration Examples

### Database Configuration - Before and After

**Before (Deprecated):**
```yaml
replication:
  master:
    host: db-master-01
    port: 5432
  slaves:
    - host: db-slave-01
    - host: db-slave-02
```

**After (Modern):**
```yaml
replication:
  primary:
    host: db-primary-01
    port: 5432
  replicas:
    - host: db-replica-01
    - host: db-replica-02
```

### Access Control - Before and After

**Before (Deprecated):**
```python
# Add IP to whitelist
security.whitelist.add("192.168.1.100")

# Check if IP is blacklisted
if security.blacklist.contains(ip_address):
    deny_access()
```

**After (Modern):**
```python
# Add IP to allowlist
security.allowlist.add("192.168.1.100")

# Check if IP is blocked
if security.blocklist.contains(ip_address):
    deny_access()
```

### Git Workflow - Before and After

**Before (Deprecated):**
```bash
git checkout master
git pull origin master
git merge feature-branch
git push origin master
```

**After (Modern):**
```bash
git checkout main
git pull origin main
git merge feature-branch
git push origin main
```

## Real-World Impact

### Inclusivity Benefits
- Creates welcoming environment for all developers
- Signals organizational values
- Reduces barriers to participation
- Improves team diversity

### Professional Benefits
- Aligns with industry standards
- Avoids controversy and criticism
- Demonstrates modern awareness
- Protects brand reputation

### Technical Benefits
- Clearer terminology (primary/replica vs master/slave)
- Consistent with cloud provider standards
- Easier for non-native English speakers
- Better aligns with actual functionality

## Implementation Checklist

### For Organizations
- [ ] Audit all documentation for deprecated terms
- [ ] Update style guides with required replacements
- [ ] Migrate Git repositories to "main" branch
- [ ] Update database configurations
- [ ] Revise API documentation
- [ ] Update code comments and variable names
- [ ] Train team on inclusive language
- [ ] Set up automated checking (Vale, linters)
- [ ] Make this an ERROR, not warning
- [ ] Review quarterly for new terms to deprecate

### For Individual Writers
- [ ] Learn modern alternatives
- [ ] Configure editor/linter to flag deprecated terms
- [ ] Review existing work for deprecated terms
- [ ] Use inclusive language by default
- [ ] Educate colleagues on changes
- [ ] Stay current with style guide updates
- [ ] Advocate for change in legacy systems

## Additional Resources

### Style Guides to Reference
- Google Developer Documentation Style Guide
- Microsoft Writing Style Guide
- Apple Style Guide
- Red Hat Supplementary Style Guide for Inclusive Language
- Salesforce Style Guide for Documentation and UI

### Key Replacements Summary

**Database:** master → primary, slave → replica/secondary
**Access Control:** whitelist → allowlist, blacklist → blocklist
**Git:** master → main
**Testing:** sanity check → smoke test/verification
**Gender:** man hours → person hours/work hours
**Ability:** crippled → degraded, dummy → placeholder
**Legacy:** grandfathered → legacy/existing

## Common Objections Addressed

### "But everyone knows what master/slave means"
**Response:** Clarity isn't the only goal. Inclusivity, professionalism, and harm reduction matter. Primary/replica is equally clear and doesn't carry harmful historical baggage.

### "It's too much work to change"
**Response:** Major companies (GitHub, Twitter, Google, Microsoft) have successfully made these changes. Automated tools make it manageable. The alternative is perpetuating harmful language.

### "This is just political correctness"
**Response:** This is professional communication. Language evolves. Technical accuracy matters. Primary/replica is MORE technically accurate than master/slave in distributed systems.

### "Native and primitive are technical terms"
**Response:** Yes, when referring to code or data types, they're acceptable. This rule focuses on avoiding them when referring to people or cultures.

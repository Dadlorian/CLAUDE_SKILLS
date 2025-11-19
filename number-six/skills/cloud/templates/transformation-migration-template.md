# [Skill Name] - Transformation & Migration Pattern

## Purpose
[One-sentence description of what this skill transforms]

## Transformation Scope

**What changes**:
- [Aspect 1]: [From → To]
- [Aspect 2]: [From → To]
- [Aspect 3]: [From → To]

**What stays the same**:
- [Aspect that doesn't change]
- [Aspect that doesn't change]

---

## Pre-Transformation Phase

### Step 1: Safety Checks

**CRITICAL**: Do not proceed unless all checks pass

- [ ] **Backup Created**
  - Create backup of: [what to backup]
  - Location: [where to store]
  - Verification: [how to verify backup works]

- [ ] **Tests Passing**
  - Run test suite: [command]
  - All tests must pass
  - Note baseline test count: [record number]

- [ ] **Clean Working Directory**
  - No uncommitted changes
  - On correct branch: [which branch]
  - Up to date with remote

- [ ] **Dependencies Current**
  - All dependencies installed
  - No version conflicts
  - Lock file up to date

- [ ] **[Custom Check]**
  - [What to verify]
  - [How to verify it]

**If any check fails**: [What to do]

---

### Step 2: Impact Analysis

**Objective**: Understand the full scope of changes

1. **Identify Affected Files**
   - Search for: [patterns to search]
   - In directories: [where to look]
   - Expected count: [approximate number]

   Command:
   ```bash
   [command to find affected files]
   ```

2. **Analyze Dependencies**
   - Find files that import affected code
   - Find files that are imported by affected code
   - Map dependency graph: [how to map it]

3. **Identify Breaking Changes**
   - [ ] API signature changes
   - [ ] Return type changes
   - [ ] Behavior changes
   - [ ] Configuration changes
   - [ ] [Custom breaking change]

4. **Assess Risk**
   - **High Risk**: [What makes it high risk]
   - **Medium Risk**: [What makes it medium risk]
   - **Low Risk**: [What makes it low risk]

   This transformation is: **[Risk Level]**

---

### Step 3: Plan Execution Order

**Strategy**: [Bottom-up/Top-down/Component-by-component]

**Order of operations**:
1. [First group of files - why first]
2. [Second group of files - why second]
3. [Third group of files - why third]

**Rationale**: [Why this order minimizes risk/errors]

---

## Transformation Process

### Step 1: Pattern Identification

Scan codebase for patterns that need transformation:

#### Pattern A: [Pattern Name]

**Source Pattern** (before):
```[language]
[code pattern to find]
```

**Target Pattern** (after):
```[language]
[code pattern to transform to]
```

**Detection**:
- Regex: `[regex pattern]`
- Or search for: [keywords/indicators]
- In files: [file patterns]

**Occurrence count**: [how many expected]

---

#### Pattern B: [Pattern Name]

**Source Pattern** (before):
```[language]
[code pattern to find]
```

**Target Pattern** (after):
```[language]
[code pattern to transform to]
```

**Detection**:
- Regex: `[regex pattern]`
- Or search for: [keywords/indicators]

---

### Step 2: Transformation Execution

For each file with patterns to transform:

1. **Load & Parse**
   - Read file: [path]
   - Parse syntax tree (if needed)
   - Identify all pattern occurrences

2. **Context Validation**
   For each occurrence, verify:
   - [ ] Context is appropriate for transformation
   - [ ] No conflicting patterns present
   - [ ] Dependencies are compatible
   - [ ] [Custom validation]

3. **Apply Transformation**
   For each validated occurrence:
   ```
   a. Extract relevant code
   b. Apply pattern transformation
   c. Preserve code style/formatting
   d. Maintain comments/documentation
   e. Update related code
   ```

4. **Verify Transformation**
   - Check syntax is valid
   - Ensure no regressions
   - Verify expected behavior maintained

5. **Update File**
   - Write transformed content
   - Preserve file metadata
   - Maintain version control info

---

### Step 3: Related Code Updates

After transforming primary patterns, update related code:

1. **Import Statements**
   - Update import paths: [how]
   - Update imported names: [how]
   - Remove unused imports: [how]

2. **Type Definitions** (if applicable)
   - Update type imports
   - Update type annotations
   - Update interfaces/types

3. **Configuration Files**
   - Update: [config file 1]
   - Update: [config file 2]
   - Validate configuration

4. **Documentation**
   - Update code comments
   - Update JSDoc/docstrings
   - Update README if needed

5. **Tests**
   - Update test imports
   - Update test assertions
   - Update mocks/fixtures
   - Add new tests if needed

---

### Step 4: Code Style & Formatting

Ensure consistent style after transformation:

1. **Run Formatter**
   - Command: [formatting command]
   - Config: [formatter config]
   - Verify: [how to verify]

2. **Run Linter**
   - Command: [linting command]
   - Fix auto-fixable issues
   - Address remaining issues

3. **Manual Style Review**
   - Check indentation: [standard]
   - Check naming: [conventions]
   - Check organization: [structure]

---

## Validation Suite

After transformation, run comprehensive validation:

### 1. Syntax Validation
```bash
[command to check syntax]
```
Expected: [what success looks like]

### 2. Type Checking (if applicable)
```bash
[command to check types]
```
Expected: [what success looks like]

### 3. Linting
```bash
[command to lint]
```
Expected: [acceptable warnings/errors]

### 4. Unit Tests
```bash
[command to run unit tests]
```
Expected: [same or more passing tests as baseline]

### 5. Integration Tests
```bash
[command to run integration tests]
```
Expected: [all tests passing]

### 6. Build Verification
```bash
[command to build]
```
Expected: [successful build]

### 7. Custom Validation
- [ ] [Custom check 1]
- [ ] [Custom check 2]
- [ ] [Custom check 3]

---

## Verification Checklist

Before considering transformation complete:

### Code Verification
- [ ] All pattern occurrences transformed
- [ ] No syntax errors
- [ ] No type errors (if applicable)
- [ ] No linting errors (or only acceptable ones)
- [ ] Code style consistent

### Functional Verification
- [ ] All tests passing (unit + integration)
- [ ] Test count same or higher than baseline
- [ ] No functionality regressions
- [ ] New behavior works as expected
- [ ] Edge cases handled

### Documentation Verification
- [ ] Code comments updated
- [ ] API documentation updated
- [ ] README updated (if needed)
- [ ] Migration guide created (if needed)

### Quality Verification
- [ ] No duplicated code introduced
- [ ] No unnecessary complexity added
- [ ] Performance not degraded
- [ ] Security not compromised

---

## Rollback Plan

If issues arise during or after transformation:

### Immediate Rollback (if in progress)
1. [Step to stop transformation]
2. [Step to restore from backup]
3. [Step to verify restoration]

### Post-Transformation Rollback
1. **If Not Committed**:
   ```bash
   git checkout .
   git clean -fd
   ```

2. **If Committed But Not Pushed**:
   ```bash
   git reset --hard HEAD~1
   ```

3. **If Pushed**:
   ```bash
   git revert [commit-hash]
   ```
   Or restore from backup: [how]

### Verification After Rollback
- [ ] Code matches pre-transformation state
- [ ] Tests passing
- [ ] Application working

---

## Progressive Transformation

For large transformations, use incremental approach:

### Phase 1: Limited Scope
- Transform: [small subset]
- Test thoroughly
- Commit: "feat: migrate [subset] to [new pattern]"

### Phase 2: Expand Scope
- Transform: [larger subset]
- Test thoroughly
- Commit: "feat: migrate [subset] to [new pattern]"

### Phase 3: Complete
- Transform: [remaining items]
- Final validation
- Commit: "feat: complete migration to [new pattern]"

**Benefits**:
- Easier to identify issues
- Smaller rollback scope
- Incremental progress
- Lower risk

---

## Communication

### During Transformation
Provide progress updates:
```
Transforming files... [XX/YY]
- Completed: [file1, file2, ...]
- In progress: [file3]
- Remaining: [file4, file5, ...]
```

### After Transformation
Provide summary:
```markdown
## Transformation Complete

**Files Modified**: [number]
**Patterns Transformed**: [number]
**Tests Status**: [passing/failing]
**Build Status**: [success/failure]

### Changes Made:
- [Summary of change 1]
- [Summary of change 2]

### Breaking Changes:
- [Breaking change 1]
- [Breaking change 2]

### Migration Guide:
[Steps for other developers/users]
```

---

## Common Issues & Solutions

### Issue 1: [Common problem]
**Symptom**: [How to recognize]
**Cause**: [Why it happens]
**Solution**: [How to fix]

### Issue 2: [Common problem]
**Symptom**: [How to recognize]
**Cause**: [Why it happens]
**Solution**: [How to fix]

---

## Post-Transformation Tasks

After successful transformation:

1. **Clean Up**
   - Remove deprecated code
   - Remove old dependencies
   - Remove compatibility shims

2. **Documentation**
   - Update architecture docs
   - Create migration guide
   - Update changelog

3. **Communication**
   - Notify team
   - Update tickets/issues
   - Share learnings

4. **Monitoring**
   - Watch for issues in production
   - Monitor performance
   - Collect feedback

---

## Examples

### Example 1: [Specific transformation scenario]

**Before**:
```[language]
[code before transformation]
```

**After**:
```[language]
[code after transformation]
```

**Changes**:
- [Change 1]
- [Change 2]

### Example 2: [Another scenario]

[Similar structure]

---

## Notes

[Important warnings, tips, or additional context]

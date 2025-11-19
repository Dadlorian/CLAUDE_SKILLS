# Conventional Commits Standard Reference

## Overview

The Conventional Commits specification is a standard for adding human-readable meaning to commit messages. It provides a structured format that enables automatic changelog generation and semantic versioning.

## Specification Version

Based on Conventional Commits v1.0.0 (https://www.conventionalcommits.org/)

## Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Type Categories

### feat
A commit of the type `feat` introduces a new feature to the codebase. Triggers a **MINOR** version bump.

```
feat: add user authentication system
feat(auth): implement OAuth2 support
feat(api): add endpoint for user profile retrieval
```

### fix
A commit of the type `fix` patches a bug in the codebase. Triggers a **PATCH** version bump.

```
fix: resolve memory leak in cache handler
fix(database): fix connection pool exhaustion
fix(ui): correct button alignment on mobile
```

### BREAKING CHANGE
A commit that contains `BREAKING CHANGE:` in the footer introduces an incompatible API change. Triggers a **MAJOR** version bump. Can be added to any commit type.

```
feat!: redesign authentication API
feat(auth)!: require authentication token in headers

fix: remove deprecated getUser() method

BREAKING CHANGE: getUser() has been removed. Use fetchUserData() instead.
```

### Other Types (not required but recommended)

#### docs
Changes to documentation only.

```
docs: update README with new installation steps
docs(api): add endpoint documentation
docs: add contributing guidelines
```

#### style
Changes that do not affect code functionality (formatting, semicolons, whitespace, etc.)

```
style: remove trailing whitespaces
style: add missing semicolons
style(css): reformat styles according to prettier
```

#### refactor
Code changes that neither fix bugs nor add features.

```
refactor: consolidate database connection logic
refactor(auth): extract validation into separate module
refactor: improve algorithm efficiency
```

#### perf
Changes that improve performance.

```
perf: optimize database queries
perf(bundler): reduce bundle size by 15%
perf: improve API response time
```

#### test
Adding missing tests or correcting existing tests.

```
test: add unit tests for validation module
test(api): add integration tests for endpoints
test: increase test coverage to 85%
```

#### ci
Changes to CI configuration files and scripts.

```
ci: add GitHub Actions workflow
ci: update Docker build configuration
ci: add automated testing on pull requests
```

### Other Common Types

```
build:   Changes to build system, dependencies
chore:   Other changes that don't modify code or tests
revert:  Revert a previous commit
```

## Scope

Optional component affected by the commit.

```
feat(auth): add login endpoint
feat(database): optimize query performance
feat(ui): redesign navigation menu
fix(api): handle null responses
refactor(core): extract utility functions
```

### Scope Examples by Project Type

**Node.js Project:**
```
feat(auth): implement JWT validation
feat(db): add connection pooling
feat(routes): add new API endpoints
```

**React Project:**
```
feat(components): add LoginForm component
feat(hooks): add useAuth custom hook
fix(reducer): fix state update logic
```

**Python Project:**
```
feat(models): add User model
feat(api): add FastAPI routes
fix(utils): correct date parsing function
```

## Description

Concise summary of the change.

**Rules:**
- Use imperative mood ("add" not "added" or "adds")
- Don't capitalize first letter
- No period (.) at the end
- Limit to 50 characters (approximately)

```
✓ add user authentication system
✓ fix memory leak in cache handler
✓ refactor database connection logic
✗ Added user authentication (past tense)
✗ Adds database index optimization (third person)
✗ Add user authentication system. (period)
✗ Add new user authentication system with OAuth2 and JWT support (too long)
```

## Body

Optional detailed explanation of the change.

**Rules:**
- Wrap at 72 characters
- Explain what and why, not how
- Reference related issues
- Be thorough but concise

```
feat(auth): implement OAuth2 authentication

This commit adds OAuth2 support for Google and GitHub providers.
Users can now authenticate using their existing accounts without
creating a new password.

The implementation includes:
- OAuth2 provider configuration
- Token refresh mechanism
- User profile synchronization

Fixes #123
Closes #456
```

## Footer

Optional metadata using token/value pairs.

### Breaking Changes
```
BREAKING CHANGE: description of what changed and how to migrate

Example:
feat!: redesign API endpoint structure

BREAKING CHANGE: The /api/users endpoint now returns paginated results.
Clients must use ?page=1&limit=20 parameters. Use the offset/limit
approach or implement pagination in client code.
```

### Issue References
```
Fixes #123
Closes #456
Resolves #789
Related to #999

Examples:
fix: prevent race condition

This change adds mutex locking to prevent concurrent access issues.

Fixes #321
```

### Other Footers
```
Reviewed-by: John Doe
Acked-by: Jane Smith
Co-authored-by: Bob Johnson <bob@example.com>

Examples:
feat: add payment processing

Reviewed-by: Alice Brown <alice@example.com>
Co-authored-by: Charlie Davis <charlie@example.com>
```

## Complete Examples

### Simple Feature
```
feat: add dark mode support
```

### Feature with Scope and Description
```
feat(ui): implement dark mode toggle in settings
```

### Feature with Body
```
feat(auth): add two-factor authentication

Users can now enable 2FA on their accounts for enhanced security.
This implementation uses time-based one-time passwords (TOTP).

Supported authenticator apps:
- Google Authenticator
- Microsoft Authenticator
- Authy

Implements #234
```

### Bug Fix
```
fix: prevent infinite loop in state machine
```

### Bug Fix with Scope and Details
```
fix(database): resolve connection pool exhaustion

The connection pool was not properly releasing connections
after errors, causing the pool to exhaust after several failed
queries. This commit adds explicit connection cleanup in the
error handler.

Fixes #567
```

### Breaking Change (v1.0 → v2.0)
```
feat(api)!: redesign REST endpoint structure

BREAKING CHANGE: Changed endpoint naming convention from
/api/v1/users/:id to /api/users/:id. Also changed response
format to include pagination wrapper.

Migration:
- Remove 'v1' from all API URLs
- Update client code to handle new response structure:
  {
    "data": [...],
    "pagination": { "page": 1, "limit": 20, "total": 100 }
  }
```

### Deprecation Notice
```
feat: deprecate getUser() method

BREAKING CHANGE: getUser() has been removed in v2.0.0.
Use fetchUserData() instead.

Old:
  const user = getUser(123);

New:
  const user = await fetchUserData(123);
```

### Multiple Type Usage
```
docs: update API documentation
style: reformat code with prettier
test: add integration tests
chore: update dependencies
```

## Automation and Tooling

### Tools that Parse Conventional Commits

**semantic-release:** Automated versioning and changelog
```
- Analyzes commits
- Determines version bump
- Generates changelog
- Creates release
```

**Commitizen:** Interactive commit message builder
```bash
npm install -g commitizen
commitizen init cz-conventional-changelog --save-dev
git cz  # Interactive commit prompt
```

**Husky & Commitlint:** Enforce commit message format
```bash
npm install husky commitlint
npx husky install
npx commitlint --init
```

### Changelog Generation
Conventional commits enable automatic changelog generation:

```
Input commits:
feat: add login feature
fix: resolve memory leak
BREAKING CHANGE: remove deprecated API

Output changelog:
## [2.0.0] - 2024-01-15

### Features
- add login feature

### Bug Fixes
- resolve memory leak

### BREAKING CHANGES
- remove deprecated API
```

## Best Practices

### 1. Use Present Imperative Mood
```
✓ add feature
✓ fix bug
✓ remove deprecated code
✗ added feature
✗ fixed bug
✗ removed deprecated code
```

### 2. Keep Scope Lowercase
```
✓ feat(auth): add login
✗ feat(Auth): add login
✓ feat(database): optimize queries
✗ feat(Database): optimize queries
```

### 3. Use Exclamation for Breaking Changes
```
✓ feat!: redesign API
✓ feat(api)!: change endpoint format
✗ feat: redesign API (use BREAKING CHANGE footer instead)
```

### 4. Reference Issues in Footers
```
✓ Fixes #123
✓ Closes #456
✗ Fixes issue 123
✗ Closes issue #456 from repository
```

### 5. Meaningful Descriptions
```
✓ add user authentication system
✓ fix race condition in cache update
✗ fix stuff
✗ add feature
✗ make changes
```

### 6. Scope Matters
```
✓ feat(auth): add OAuth2 support
✓ feat(ui): redesign login form
✗ feat: add OAuth2 support (missing scope)
```

## Common Commit Examples

### Web Application Development
```
feat(ui): add dark mode toggle
feat(api): implement pagination for users endpoint
fix(auth): resolve JWT token validation issue
feat(db): add user activity logging
perf(search): optimize full-text search queries
docs(readme): update installation instructions
```

### Library Development
```
feat: add TypeScript support
feat(api): export new public interfaces
fix: resolve memory leak in factory
refactor: simplify configuration API
test: increase test coverage to 90%
docs: improve API documentation examples
```

### DevOps/Infrastructure
```
ci: add GitHub Actions workflow
ci: automate Docker image builds
ci(lint): add code quality checks
build: upgrade to Node 18 LTS
chore: update dependencies
docs(deploy): add deployment guide
```

## Comparison with Other Standards

### Git Commit Messages (Tim Pope)
- Imperative mood (similar)
- 50 character title limit (vs 72)
- Blank line separator (same)
- Wrapped body (same)
- No structured type system (different)

### Angular Commit Guidelines
- Based on Conventional Commits
- Uses types: feat, fix, docs, style, refactor, perf, test
- Supports scopes and breaking changes
- Stricter type definitions

## Enforcement

### Commitlint Configuration
```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',
        'fix',
        'docs',
        'style',
        'refactor',
        'perf',
        'test',
        'ci',
        'chore',
        'revert',
      ],
    ],
    'subject-case': [2, 'never', ['start-case', 'pascal-case', 'upper-case']],
  },
};
```

### Pre-commit Hook
```bash
#!/bin/bash
# .husky/commit-msg

npx --no-install commitlint --edit "$1"
```

## Summary

Conventional Commits provides:
- Structured commit format
- Automatic changelog generation
- Semantic versioning automation
- Better project history
- Improved collaboration

Using this standard enhances code quality and maintainability while enabling automation in your release process.

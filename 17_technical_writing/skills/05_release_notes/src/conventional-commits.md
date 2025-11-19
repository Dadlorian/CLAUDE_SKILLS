# Conventional Commits for Automated Changelog Generation

## Overview

Conventional Commits enable automated changelog generation from commit messages. The format is:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Commit Types

### `feat:` New feature
Creates a MINOR version bump.

```bash
git commit -m "feat: add webhook events for payment timeout"
```

### `fix:` Bug fix
Creates a PATCH version bump.

```bash
git commit -m "fix: resolve timeout issues with large file uploads"
```

### `docs:` Documentation
Does NOT create version bump.

```bash
git commit -m "docs: update API authentication guide"
```

### `style:` Code style changes
Does NOT create version bump.

```bash
git commit -m "style: format code with prettier"
```

### `refactor:` Code refactoring
Does NOT create version bump.

```bash
git commit -m "refactor: simplify charge validation logic"
```

### `perf:` Performance improvements
Creates a PATCH version bump.

```bash
git commit -m "perf: reduce database query time by 30%"
```

### `test:` Test additions
Does NOT create version bump.

```bash
git commit -m "test: add tests for webhook retry logic"
```

### `chore:` Maintenance tasks
Does NOT create version bump.

```bash
git commit -m "chore: update dependencies to latest versions"
```

## Scope

Optionally specify what part of the codebase is affected:

```bash
git commit -m "feat(webhooks): add payment.timeout event"
git commit -m "fix(auth): resolve token validation bug"
git commit -m "feat(api): add bulk charges endpoint"
```

## Breaking Changes

Add `BREAKING CHANGE:` to indicate a breaking change (creates MAJOR version bump):

```bash
git commit -m "feat!: move authentication to header

BREAKING CHANGE: API key authentication via query parameter is deprecated.
Use Authorization header instead."
```

Or use `!` before the colon:

```bash
git commit -m "feat(api)!: change response format

BREAKING CHANGE: error responses now use {error: {code, message}} format"
```

## Examples

### Simple feature
```
feat: add EUR currency support

- Support for EUR, GBP, JPY
- Automatic currency conversion
- Region-specific decimal handling
```

### Breaking change
```
feat!: migrate authentication to header-based

BREAKING CHANGE: API key query parameter (api_key=) is deprecated.
Switch to Authorization header: Authorization: Bearer sk_live_KEY

Migration guide: https://docs.example.com/migrating-to-v2

Fixes #123
```

### Bug fix with body
```
fix: handle concurrent charge creation

The charge creation endpoint could create duplicate charges when
receiving concurrent requests with the same idempotency key.

Now properly validates idempotency keys and returns 409 Conflict
when duplicate detected.

Fixes #456
```

### Multi-line commit
```
feat(webhooks): add retry logic for failed deliveries

Webhooks now automatically retry on failure:
- 1 minute: first retry
- 5 minutes: second retry
- 15 minutes: third retry
- 1 hour: fourth retry
- 6 hours: fifth and final retry

Exponential backoff prevents server overload.

Closes #789
```

## GitHub Integration

### Using with Release Drafter

Configure your release drafter to parse conventional commits:

```yaml
# .release-drafter-config.yml
categories:
  - title: '🚀 Features'
    labels:
      - 'type: feature'
  - title: '🐛 Bug Fixes'
    labels:
      - 'type: bug'
  - title: '🚨 Breaking Changes'
    labels:
      - 'breaking-change'

version-resolver:
  major:
    labels:
      - 'breaking-change'
  minor:
    labels:
      - 'type: feature'
  patch:
    labels:
      - 'type: bug'
```

### Using with semantic-release

Install and configure:

```bash
npm install --save-dev semantic-release @semantic-release/changelog @semantic-release/git
```

Configure in `package.json`:

```json
{
  "release": {
    "plugins": [
      "@semantic-release/commit-analyzer",
      "@semantic-release/release-notes-generator",
      "@semantic-release/changelog",
      "@semantic-release/npm",
      "@semantic-release/git"
    ]
  }
}
```

This automatically:
1. Analyzes commits
2. Determines version bump
3. Generates changelog
4. Creates release notes
5. Publishes to npm
6. Creates Git tag

## Tools for Enforcing Convention

### 1. Commitizen

Provides interactive commit prompts:

```bash
npm install --save-dev commitizen cz-conventional-changelog
npx commitizen init cz-conventional-changelog --save-dev --save-exact
npm run commit  # Instead of git commit
```

### 2. Husky + commitlint

Validate commits before they're created:

```bash
npm install --save-dev husky @commitlint/config-conventional @commitlint/cli
npx husky install
npx husky add .husky/commit-msg 'npx --no -- commitlint --edit "$1"'
```

Create `commitlint.config.js`:

```javascript
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
        'chore'
      ]
    ],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    'type-case': [2, 'always', 'always-lowercase']
  }
};
```

### 3. VS Code Extensions

- **Conventional Commits** (vivaxy.vscode-conventional-commits)
- **Commit Message Editor** (adam-bender.commit-message-editor)

## Generated Changelog Example

Using conventional commits, an automated changelog for v2.1.0 might look like:

```
## v2.1.0 (2025-11-19)

### Features

- **webhooks**: add webhook events for payment timeout (#234)
- **api**: add support for EUR currency (#229)
- **api**: add bulk charges endpoint (#225)

### Bug Fixes

- **uploads**: resolve timeout issues with large file uploads (#241)
- **api**: fix pagination cursor encoding (#239)
- **webhooks**: fix retry logic for failed deliveries (#236)

### Breaking Changes

- **auth**: API key query parameter authentication is deprecated (#240)

### Contributors

@john-doe, @jane-smith, @bot
```

## Best Practices

1. **Use imperative mood**: "add feature" not "added feature"
2. **Don't capitalize first letter**: "add feature" not "Add feature"
3. **No period at end**: "add feature" not "add feature."
4. **Reference issues**: Add "Fixes #123" or "Closes #456"
5. **Clear descriptions**: Explain *why* not just *what*
6. **Keep it concise**: Titles should be <50 characters
7. **Use body for detail**: Explanation goes in optional body

## Common Mistakes

❌ **Too vague**:
```
git commit -m "fix: stuff"
```

✅ **Clear and specific**:
```
git commit -m "fix: handle null values in charge validation"
```

❌ **Wrong type**:
```
git commit -m "chore: add new payment feature"  # Should be 'feat'
```

✅ **Correct type**:
```
git commit -m "feat: add payment feature"
```

❌ **Missing scope**:
```
git commit -m "fix: handle timeout"  # Which part of code?
```

✅ **With scope**:
```
git commit -m "fix(webhooks): handle timeout in delivery"
```

## Additional Resources

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Angular Commit Guidelines](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit)
- [Semantic Versioning](https://semver.org/)

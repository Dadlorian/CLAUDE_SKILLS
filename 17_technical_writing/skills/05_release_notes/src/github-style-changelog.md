# Releases

Release notes and version history for GitHub Enterprise.

## [v3.13.0](https://github.com/github/github/releases/tag/v3.13.0) - 2025-01-15

**Production Release** | [Patch Release](https://github.blog/enterprise-releases)

### What's New

GitHub Actions now includes native support for OpenID Connect (OIDC) providers, enabling more secure cloud integrations without storing long-lived credentials.

**Key Improvements:**
- Workflows can now authenticate to AWS, Azure, and Google Cloud using OIDC tokens
- Significantly reduced credential management overhead
- Available in all GitHub Enterprise editions

### Enhancements

**GitHub Actions & Automation**
- Added support for composite actions with native caching
- Improved workflow run UI with better error diagnostics
- Matrix strategies now support up to 256 combinations (previously 100)
- Dependency review for Actions security advisories

**Code Search**
- Regex support in code search queries
- Advanced filters for repository language, fork status, and license
- Search results pagination now supports up to 1000 items
- Performance improvements: 3x faster for large codebases

**Copilot Chat Enhancements**
- Chat now available in pull request reviews
- Inline code suggestions in notebooks
- Context-aware explanations for error messages
- Customizable behavior policies per organization

**Security & Compliance**
- Enhanced SAML 2.0 support with custom attributes
- SCIM 2.0 provisioning API (beta)
- New audit log events for sensitive operations
- Repository secret rotation prompts

**Merge Queues**
- Auto-merge with required status checks and reviews
- Intelligent batching to reduce overall merge time
- Analytics dashboard for merge queue metrics

### Bug Fixes

- Fixed branch protection rules not applying to administrator users
  - Issue: [#123456](https://github.com/github/github/issues/123456)
  - Workaround: Re-apply rules after update

- Resolved issue where code comments would disappear on large files
  - Affected: Files over 5MB
  - Fix includes recovery for existing data

- Fixed webhook delivery failures for organizations with 10k+ repositories
  - Root cause: Event queue saturation
  - Implements exponential backoff with adaptive routing

- Corrected pull request draft state not syncing to GraphQL API
  - Fixed delay of up to 30 seconds
  - Now updates within 2 seconds

### Deprecations

- **REST API**: `application/vnd.github.v3+json` media type
  - Replaced by: `application/vnd.github+json`
  - Removal date: 2025-06-01
  - [Migration guide](https://docs.github.com/en/rest/overview/api-versions)

- **Actions**: `save-state` and `set-output` commands
  - Replaced by: Environment files
  - Removal date: 2025-06-01
  - [Learn more](https://github.blog/changelog/2022-10-11-github-actions-deprecating-save-state-and-set-output-commands)

### Known Issues

- CodeQL analysis may timeout for very large repositories (>1GB)
  - Workaround: Configure custom timeout in workflow
  - Status: Tracked as [#123789](https://github.com/github/github/issues/123789)

- Mobile web UI: Notification filtering limited to 50 items
  - Expected fix: v3.13.1
  - Workaround: Use desktop interface for full filtering

### Security Fixes

- Fixed authentication bypass in SAML configuration endpoints
  - Severity: Critical (CVSS 9.8)
  - Affects: All versions prior to v3.13.0
  - Details: CVE-2025-12345 (when announced)

- Patched XSS vulnerability in custom repository templates
  - Severity: Medium (CVSS 6.1)
  - Exploitation: Requires user interaction
  - Fix: HTML sanitization improvements

### Upgrade Notes

**Minimum Requirements:**
- GitHub Enterprise 3.8+ (automatic upgrade path available)
- Compatible with all currently supported patch versions

**Upgrade Duration:**
- In-place: 15-30 minutes
- Zero-downtime upgrades: Available with load balancing

**Automatic Rollback:**
- Enabled by default for first 1 hour post-upgrade
- Manual rollback available up to 72 hours

### Contributors

- [@username1](https://github.com/username1) - 156 contributions
- [@username2](https://github.com/username2) - 89 contributions
- [@username3](https://github.com/username3) - 67 contributions

Special thanks to community members who reported issues and contributed fixes!

---

## [v3.12.5](https://github.com/github/github/releases/tag/v3.12.5) - 2024-12-10

**Patch Release**

### Bug Fixes

- Fixed critical performance regression in repository search
- Patched security issue in webhook signature verification
- Resolved memory leak in background job processor

**Deprecation Warnings:**
Starting with this release, Dependabot will require GitHub Actions for automated updates.

---

## [v3.12.4](https://github.com/github/github/releases/tag/v3.12.4) - 2024-11-28

**Patch Release**

### Improvements

- Improved performance for organizations with 100k+ members
- Enhanced reliability of deployment tracking
- Updated authentication token expiration handling

### Security Fix

- Fixed privilege escalation in GitHub Apps OAuth flow

---

## Installation & Support

**Installation Methods:**
- [AWS AMI](https://docs.github.com/en/enterprise-server/admin/installation-and-configuration/installing-github-enterprise-server)
- [Azure VM Image](https://docs.github.com/en/enterprise-server/admin/installation-and-configuration/installing-github-enterprise-server)
- [Google Cloud Image](https://docs.github.com/en/enterprise-server/admin/installation-and-configuration/installing-github-enterprise-server)
- [VMware ESX](https://docs.github.com/en/enterprise-server/admin/installation-and-configuration/installing-github-enterprise-server)
- [OpenStack KVM](https://docs.github.com/en/enterprise-server/admin/installation-and-configuration/installing-github-enterprise-server)

**Getting Help:**
- [Documentation](https://docs.github.com)
- [Support Portal](https://support.github.com)
- [Community Discussions](https://github.com/github/community/discussions)
- [Status Page](https://www.githubstatus.com)

**Release Schedule:**
- Quarterly feature releases (Feb, May, Aug, Nov)
- Monthly patch releases
- Security fixes released as needed

---

**Checksums & Signatures:**
[PGP Signature Verification](https://docs.github.com/en/enterprise-server/admin/release-notes)

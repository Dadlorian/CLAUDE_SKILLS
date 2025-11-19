# Changelog

All notable changes to the Stripe API are documented below. We maintain backward compatibility with all previously released APIs unless noted otherwise.

## 2025-01-15

### Added
- **Connect OAuth**: New advanced scoping options for marketplace integrations
  - Granular permission controls per connected account
  - Scope versioning for future-proof integrations
  - Example: `read:charges write:refunds`

- **Payment Intents v2**: Improved confirmation handling
  - Off-session payment support with explicit consent tracking
  - Network token support for recurring transactions
  - Automatic recovery workflows for failed payments

- **Webhooks**: Enhanced delivery reliability
  - Exponential backoff retry strategy with jitter
  - Webhook signing with Ed25519 for improved security
  - Batch webhook delivery for high-volume events

### Changed
- **Charge API**: Updated metadata field validation
  - Increased max length from 50,000 to 100,000 characters
  - Added support for nested objects in metadata
  - Improved error messages for validation failures

- **Customer Portal**: Enhanced security for sensitive data
  - Automatic session timeout after 30 minutes of inactivity
  - Device fingerprinting for suspicious access detection
  - Rate limiting: 100 requests per IP per minute

- **Reporting**: Improved dashboard performance
  - Cached reports now update every 15 minutes (previously 1 hour)
  - Added data warehouse integration for raw data exports
  - Real-time alerts for unusual payment patterns

### Fixed
- **API Rate Limits**: Corrected burst capacity calculation
  - Previous: 100 requests per second baseline
  - Current: 100 requests per second with 1000-request burst window
  - Affected customers will see improvement without code changes

- **Webhook Signature Verification**: Fixed timestamp validation window
  - Tolerance window extended from 5 to 10 minutes
  - Better support for clock skew in distributed systems

- **Idempotency Keys**: Fixed collision handling in edge cases
  - Now properly handles retry scenarios with different parameters
  - Documentation updated with best practices

### Deprecated
- **Charge Creation with `source`**: Use Payment Methods API instead
  - Timeline: Full removal in 90 days (2025-04-15)
  - Migration guide: https://stripe.com/docs/payments/charges-to-payment-intents

- **API version `2019-02-19`**: Use current version `2024-04-10`
  - Legacy requests will return deprecation headers
  - Final support ends 2025-06-15

- **Customer object `id` field ordering**: Deprecated in favor of stable IDs
  - IDs will always be prefixed with `cus_`
  - Update parsing logic if you rely on ID format

## 2024-12-01

### Added
- **Radar**: Machine learning fraud detection enhancements
  - New rule builder with custom ML model support
  - Real-time risk scoring on all transactions
  - Automatic velocity checks across merchant accounts

- **Billing Portal**: Subscription management improvements
  - Self-service pause functionality (up to 90 days)
  - Flexible renewal schedules
  - Smart dunning strategies with retryable payment tracking

- **Sigma**: Advanced reporting capabilities
  - Custom metric builder with SQL query support
  - Automated report scheduling and email delivery
  - Data retention: 24 months (previously 12 months)

### Changed
- **Fee Structure**: Transparent pricing updates effective 2025-01-01
  - See pricing page for transaction-specific tiers
  - Reserved capacity pricing now available
  - Volume discounts reset on calendar year basis

- **API Rate Limiting**: Progressive enhancement
  - Standard tier: 25 requests/second
  - Premium tier: 100 requests/second
  - Enterprise tier: Custom limits available

### Fixed
- **Balance Transactions**: Corrected fee calculation for three-d-secure charges
  - Affected period: 2024-10-01 to 2024-11-30
  - Retroactive correction applied automatically
  - No action required from users

- **Reconciliation**: Fixed reporting lag for ACH transfers
  - Reporting now reflects bank confirmation within 24 hours
  - Status updates push to webhooks immediately

## 2024-10-15

### Added
- **Payment Links**: Checkout-hosted payment pages
  - Custom branding and styling options
  - Social payment buttons (Apple Pay, Google Pay)
  - Expiration and usage limits per link

- **Card Metadata**: Enhanced card tokenization
  - Store customer metadata with payment methods
  - Reference in future transactions
  - Improved analytics and reconciliation

### Security Updates
- Mandatory TLS 1.2 for all API connections
- Updated cryptographic standards for signature verification
- Enhanced PCI compliance validation

## 2024-09-01

### Breaking Changes
- **API Request Size Limit**: Reduced from 50MB to 32MB
  - Most customers unaffected
  - Large batch operations require modification
  - Contact support for legacy integration review

- **Response Format**: Minor JSON schema changes
  - `livemode` boolean always present (previously sometimes absent)
  - `created` timestamp now always Unix time (ISO 8601 deprecated)
  - Plan migration in changelog-specific docs

## Version History

| Version | Released | Status | Support Ends |
|---------|----------|--------|--------------|
| 2024-04-10 | 2024-04-10 | Current | Active |
| 2024-02-15 | 2024-02-15 | Supported | 2025-02-15 |
| 2023-10-16 | 2023-10-16 | Deprecated | 2024-10-16 |
| 2023-08-16 | 2023-08-16 | Deprecated | 2024-08-16 |

## Support & Documentation

- **API Documentation**: https://stripe.com/docs/api
- **Migration Guides**: https://stripe.com/docs/upgrades
- **Status Page**: https://status.stripe.com
- **Support Portal**: https://support.stripe.com
- **Changelog API**: Access via `GET /api/changelog`

## Contact

For questions about API changes:
- Email: api-support@stripe.com
- Slack: #stripe-api-support
- GitHub: github.com/stripe/stripe-node

---

**Last updated**: 2025-01-15 | **Next update**: 2025-02-15

# Embedded Analytics Subskill

Production-ready SaaS embedded analytics patterns for integrating BI platforms into customer-facing applications.

## Structure

### `/skill.md`
Main skill definition with expertise in:
- Embedding methods (iframe, SDK, REST API, components)
- Authentication & SSO (JWT, SAML, OAuth)
- Multi-tenancy & RLS
- White-labeling
- Platform-specific implementation (Tableau, Power BI, Looker, Metabase, Superset)
- Performance optimization

### `/reference/` (12 files)
Technical comparisons and patterns:
- `embedding_methods_comparison.md` - iframe vs SDK vs API approaches
- `sso_patterns.md` - Authentication patterns (JWT, SAML, OAuth, trusted auth)
- `rls_approaches.md` - Row-level security implementation strategies
- `whitelabeling_techniques.md` - Custom branding and domain configuration
- `multitenancy_patterns.md` - Shared/separate schema/database patterns
- `performance_optimization.md` - Query, caching, and frontend optimization
- `platform_comparison.md` - Tableau vs Power BI vs Looker feature matrix
- `security_best_practices.md` - Authentication, data security, network security
- `caching_strategies.md` - Multi-layer caching (browser, CDN, Redis, DB)
- `api_integration_patterns.md` - Dashboard management, user provisioning, webhooks
- `cost_optimization.md` - Capacity management, licensing, infrastructure costs
- `mobile_embedding.md` - iOS, Android, React Native implementations

### `/guides/` (14 files)
Step-by-step implementation tutorials:
- `tableau_embedding_complete_guide.md` - Full Tableau Connected Apps setup
- `powerbi_embedded_quickstart.md` - Azure setup to frontend embedding
- `sso_implementation_guide.md` - JWT, SAML, OAuth implementation
- `rls_implementation_guide.md` - Database and BI platform RLS
- `whitelabeling_guide.md` - Custom domain, CSS, email branding
- `multitenancy_implementation.md` - Architecture choice and provisioning
- `performance_tuning_guide.md` - Database, caching, frontend optimization
- `testing_embedded_analytics.md` - Unit, integration, E2E, security tests
- `troubleshooting_guide.md` - Common issues and solutions
- `looker_embedding_guide.md` - Looker SSO URL generation and SDK
- `iframe_vs_sdk_guide.md` - Decision framework with examples
- `mobile_implementation_guide.md` - React Native, iOS, Android
- `api_integration_guide.md` - Dashboard/user/data management APIs
- `deployment_guide.md` - Docker, Kubernetes, monitoring setup

### `/src/` (24 files)
Production-ready code examples:
- `react_tableau_embed.jsx` - React component with token management
- `react_powerbi_embed.jsx` - Power BI React component with auto-refresh
- `jwt_token_service.js` - JWT generation with caching and revocation
- `rls_sql_patterns.sql` - PostgreSQL RLS policies and patterns
- `tenant_provisioner.js` - Automated tenant setup service
- `whitelabel.css` - White-label CSS overrides
- `api_client.js` - Unified BI platform API client
- `query_cache.js` - Redis query caching with adaptive TTL
- `performance_monitor.js` - Performance metrics collector
- Plus 15+ additional utility files, services, and examples

## Key Features

### Security
- JWT-based authentication with short expiration
- Row-level security at database and BI platform layers
- Multi-tenant data isolation
- Token revocation and caching
- Rate limiting and audit logging

### Performance
- Multi-layer caching (browser, CDN, Redis, materialized views)
- Query optimization and indexing strategies
- Lazy loading and code splitting
- Adaptive TTL based on query cost
- Connection pooling and read replicas

### Multi-Tenancy
- Shared/separate schema/database patterns
- Automated tenant provisioning
- Tenant-aware caching and routing
- Per-tenant resource quotas
- Cost allocation and tracking

### White-Labeling
- Custom domains and SSL
- CSS overrides for BI platforms
- Branded email templates
- Hide vendor branding
- Custom logos and themes

### Platforms Supported
- ✅ Tableau (Connected Apps, REST API, JavaScript API)
- ✅ Power BI Embedded (Azure service, client SDK, RLS)
- ✅ Looker (SSO embedding, API, custom domains)
- ✅ Metabase (JWT signing, white-labeling)
- ✅ Apache Superset (Guest tokens, RLS)
- ✅ Qlik Sense (Associative engine, Section access)

## Usage

1. **Choose your platform**: Review `/reference/platform_comparison.md`
2. **Follow setup guide**: Check `/guides/` for your platform
3. **Implement authentication**: Use patterns from `/reference/sso_patterns.md`
4. **Add RLS**: Follow `/guides/rls_implementation_guide.md`
5. **Optimize performance**: Apply strategies from `/reference/performance_optimization.md`
6. **Deploy**: Use `/guides/deployment_guide.md`

## Production Checklist

- [ ] SSO configured and tested
- [ ] RLS enforced at database level
- [ ] Multi-tenancy isolation verified
- [ ] Performance benchmarked
- [ ] Security audit completed
- [ ] White-labeling applied
- [ ] Monitoring and alerts configured
- [ ] Documentation updated
- [ ] Load testing passed
- [ ] Disaster recovery plan in place

## Best Practices

1. **Never** trust client-provided tenant IDs - always derive from authenticated user
2. **Always** use HTTPS for embedded content
3. **Implement** short token expiration (< 30 minutes)
4. **Enable** aggressive caching with proper invalidation
5. **Monitor** performance and security metrics
6. **Test** RLS thoroughly with penetration testing
7. **Document** all RLS rules and tenant provisioning processes
8. **Plan** for scale from day one

## Support

For issues or questions:
- Review troubleshooting guide: `/guides/troubleshooting_guide.md`
- Check platform-specific guides in `/guides/`
- Review reference documentation in `/reference/`
- Examine code examples in `/src/`

# PropTech Industry Best Practices

**Version:** 2.0
**Last Updated:** 2025-01-15
**Status:** Active Standard
**Sources:** Greystar, Equity Residential, Prologis, NMHC, BOMA, IREM

## Table of Contents

1. [Property Management Operations](#property-management-operations)
2. [Smart Building Deployment](#smart-building-deployment)
3. [Construction Tech Implementation](#construction-tech-implementation)
4. [Fair Housing Technology Compliance](#fair-housing-technology-compliance)
5. [Data Privacy Best Practices](#data-privacy-best-practices)
6. [Security Standards](#security-standards)

## Property Management Operations

### Best Practice 1: Automated Rent Collection

**Source:** Greystar Best Practices Guide 2024

**Standard Operating Procedure:**

**Pre-Move-In:**
1. Require ACH/auto-pay enrollment during lease signing (90%+ adoption goal)
2. Offer $25-50 incentive for ACH enrollment
3. Provide clear instructions and multiple enrollment channels (online, mobile app, in-person)

**During Tenancy:**
1. Auto-charge rent on 1st of month (or tenant-selected date)
2. Send reminder email 3 days before charge
3. Send confirmation email after successful payment
4. Auto-generate late fees on day 6 (per lease terms)
5. Send late notice immediately upon late fee posting
6. Automated follow-up sequence for delinquencies

**Technology Stack:**
- Payment processor: Stripe, PayPal, Yardi RentCafe
- Auto-pay rate target: >85%
- Manual payment rate: <15%

**Results (Greystar portfolio):**
- Collection rate: 99.2%
- Delinquency rate: 2.1% (vs. 6.8% industry avg)
- Time spent on collections: 75% reduction

### Best Practice 2: Maintenance Request Workflow

**Source:** Equity Residential Operations Playbook 2024

**Tier-Based Response System:**

| Priority | Response Time | Resolution Time | Examples |
|----------|--------------|-----------------|----------|
| **Emergency** | < 2 hours | < 24 hours | No heat (winter), gas leak, flood |
| **Urgent** | < 4 hours | < 48 hours | HVAC failure, major appliance |
| **Standard** | < 24 hours | < 5 days | Minor repairs, cosmetic issues |
| **Scheduled** | Next maintenance cycle | Varies | Preventive maintenance |

**Workflow Automation:**
1. Resident submits request via mobile app (photo upload required)
2. AI categorizes and prioritizes request
3. Auto-dispatch to appropriate vendor or staff
4. Vendor accepts and provides ETA
5. Automated status updates to resident (SMS + email)
6. Resident confirms completion via app
7. Auto-survey for satisfaction rating

**Technology Requirements:**
- Mobile app with photo upload
- Work order management system (integrated with PMS)
- Vendor portal for acceptance/updates
- Automated communication (SMS, email, push notifications)

**Performance Metrics (Equity Residential):**
- Emergency response: 1.7 hours avg (target: <2 hours)
- Resident satisfaction: 4.4/5.0
- First-time fix rate: 87%
- Automated work order routing: 93% of requests

### Best Practice 3: Lease Renewal Process

**Source:** NMHC Best Practices Compendium 2024

**Timeline:**

| Day | Action | Owner | Automation |
|-----|--------|-------|------------|
| **T-120** | Renewal analysis (market rent, tenant history) | Revenue Management System | Auto |
| **T-90** | Renewal offer generated | System | Auto |
| **T-90** | Renewal notice sent to tenant | Leasing Team | Auto |
| **T-75** | Follow-up call if no response | Leasing Agent | Manual |
| **T-60** | Second reminder (email + SMS) | System | Auto |
| **T-45** | Personal outreach from property manager | Property Manager | Manual |
| **T-30** | Final renewal deadline | - | - |

**Renewal Offer Strategy:**
- Market rent analysis using comp data
- Tenant score (payment history, violations, length of tenancy)
- Concession analysis (vs. cost of turn)

**Renewal Rate Benchmarks:**
- Class A: 55-65%
- Class B: 50-60%
- Class C: 45-55%

**Best-in-Class Renewal Rates:** 65-70% (with proactive engagement)

**Technology Enablers:**
- Revenue management system (RealPage, Yardi)
- Automated communication workflows
- Tenant satisfaction surveys (identify at-risk tenants)

## Smart Building Deployment

### Best Practice 4: Phased Smart Building Rollout

**Source:** Prologis "Smart Buildings Implementation Guide" 2024

**Phase 1: Foundation (Months 1-6)**
- Deploy network infrastructure (WiFi, PoE)
- Install smart meters (electric, water, gas)
- Implement cloud-based BAS
- Establish data platform (IoT Hub + analytics)

**Investments:** $1.50 - $2.50/sq ft
**Expected ROI:** Foundation for future phases

**Phase 2: Optimization (Months 7-12)**
- Deploy occupancy sensors
- Implement HVAC optimization algorithms
- Add lighting controls (common areas)
- Deploy predictive maintenance

**Investments:** $0.75 - $1.25/sq ft
**Expected Savings:** 15-20% energy reduction

**Phase 3: Enhancement (Months 13-24)**
- Tenant-facing features (mobile app, smart thermostats)
- Advanced analytics (space utilization, indoor air quality)
- Integration with tenant systems
- Demand response participation

**Investments:** $0.50 - $1.00/sq ft
**Value-Add:** Tenant satisfaction, premium rents

**Lessons Learned (Prologis):**
- Don't boil the ocean - start with high-ROI items
- Ensure vendor interoperability (BACnet/IP mandate)
- Engage tenants early for adoption
- Plan for 5-10 year technology refresh cycle

### Best Practice 5: IoT Sensor Deployment Standards

**Source:** JLL "IoT Sensor Best Practices" 2024

**Sensor Density Guidelines:**

| Space Type | Temperature Sensors | Occupancy Sensors | Air Quality Sensors |
|------------|-------------------|------------------|-------------------|
| **Open Office** | 1 per 1,000 sq ft | 1 per 500 sq ft | 1 per 5,000 sq ft |
| **Private Office** | 1 per 2 offices | 1 per office | 1 per 10 offices |
| **Conference Rooms** | 1 per room | 1 per room | 1 per room |
| **Common Areas** | 1 per 2,000 sq ft | 1 per 1,000 sq ft | 1 per 10,000 sq ft |
| **Multifamily Units** | Smart thermostat | Door/window sensors | Optional |

**Installation Best Practices:**
- Avoid direct sunlight, drafts, heat sources for temperature sensors
- Mount occupancy sensors 7-9 feet high, coverage area: 15-20 ft radius
- CO2 sensors in breathing zone (4-6 feet high)
- Use PoE for power when available (reduces battery maintenance)

**Connectivity:**
- Primary: WiFi (for data-rich sensors)
- Secondary: LoRaWAN (for low-power, long-range sensors)
- Avoid: Zigbee, Z-Wave (limited range, mesh complexity)

**Data Management:**
- Sampling frequency: 1-5 minutes for HVAC control, 15 minutes for analytics
- Data retention: 1 year hot storage, 7 years cold storage (compliance)
- Edge processing for real-time control, cloud for analytics

## Construction Tech Implementation

### Best Practice 6: BIM Implementation for Construction

**Source:** Skanska "BIM Execution Plan Template" 2024

**BIM Maturity Levels:**

**Level 1 (Basic):**
- 3D modeling for design visualization
- Clash detection
- Quantity takeoffs

**Level 2 (Intermediate):**
- 4D scheduling (time-based simulation)
- 5D cost estimation
- Collaborative design (all trades)

**Level 3 (Advanced):**
- 6D facility management integration
- As-built model delivered to owner
- Digital twin integration

**ROI by Maturity Level:**
- Level 1: 12% project cost reduction (clash detection alone)
- Level 2: 18% cost reduction + 15% schedule compression
- Level 3: 25% cost reduction + digital asset for operations

**Implementation Timeline:**
- Pilot project (Level 1): 6 months
- Portfolio rollout: 12-18 months
- Achieve Level 3 maturity: 24-36 months

**Software Standards:**
- Modeling: Autodesk Revit, Bentley MicroStation
- Coordination: Navisworks, BIM 360
- File format: IFC (Industry Foundation Classes) for interoperability

## Fair Housing Technology Compliance

### Best Practice 7: AI Bias Mitigation in Tenant Screening

**Source:** National Fair Housing Alliance "PropTech Fairness Guidelines" 2024

**Prohibited Practices:**
❌ Using race, ethnicity, national origin in algorithms
❌ Using proxies that correlate with protected classes (zip code, first name)
❌ Different screening criteria for different groups
❌ Lack of adverse action notice and appeal process

**Required Practices:**
✅ Disparate impact testing across protected classes
✅ Explainable AI (provide reasons for denial)
✅ Human review for all denials
✅ Regular bias audits (quarterly minimum)
✅ Adverse action notices (FCRA-compliant)

**Tenant Screening Best Practices:**

**Credit Score:** Use FICO score (not proprietary scores with unknown bias)
- Minimum acceptable: 600-620 (document business necessity)
- Consider alternative credit (rent payment history via Experian RentBureau)

**Criminal History:**
- Do NOT use arrest records (only convictions)
- Apply look-back period (7 years for felonies, 3-5 years for misdemeanors)
- Individual assessment required (consider nature, time passed, rehabilitation)
- Comply with HUD guidance on criminal background screening

**Rental History:**
- Verify previous landlord references
- Check eviction records (public records)
- Document repeated lease violations (if any)

**Income Verification:**
- Standard: 3x monthly rent in gross income
- Accept alternative income sources (SSI, alimony, child support)
- Do NOT discriminate based on source of income (illegal in many jurisdictions)

**Technology Audit:**
```python
def audit_screening_algorithm(model, test_data):
    """
    Test for disparate impact across protected classes
    """
    protected_classes = ['race', 'ethnicity', 'gender', 'familial_status']

    for protected_class in protected_classes:
        # Calculate approval rate for each group
        for group in test_data[protected_class].unique():
            group_data = test_data[test_data[protected_class] == group]
            approval_rate = model.predict(group_data).mean()

            # Document if < 80% of highest group (four-fifths rule)
            if approval_rate < max_approval_rate * 0.8:
                flag_disparate_impact(protected_class, group, approval_rate)
```

## Data Privacy Best Practices

### Best Practice 8: GDPR/CCPA Compliance for Tenant Data

**Source:** TrustArc "Real Estate Data Privacy Playbook" 2024

**Data Collection:**
- **Lawful Basis:** Contractual necessity (lease agreement)
- **Consent Required:** Marketing communications, data sharing with third parties
- **Data Minimization:** Collect only necessary data (no SSN unless required by law)

**Tenant Rights:**
1. **Right to Access:** Provide all personal data within 30 days
2. **Right to Deletion:** Delete data upon request (unless retention required by law)
3. **Right to Portability:** Export data in machine-readable format (CSV, JSON)
4. **Right to Correction:** Allow tenants to update personal information

**Data Retention:**

| Data Type | Retention Period | Legal Basis |
|-----------|-----------------|-------------|
| **Lease agreements** | 7 years after termination | Tax, legal |
| **Payment history** | 7 years | Tax, legal |
| **Tenant applications (denied)** | 3 years | Fair housing defense |
| **Maintenance requests** | 3 years | Liability |
| **Marketing data (with consent)** | Until consent withdrawn | Consent |

**Security Measures:**
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.2+)
- Access controls (role-based, least privilege)
- Audit logging (who accessed what, when)
- Annual penetration testing
- Employee training (annual)

**Breach Notification:**
- Notify affected tenants within 72 hours
- Notify regulators (if >500 records or high risk)
- Document breach and remediation steps

## Security Standards

### Best Practice 9: Access Control Systems

**Source:** ASIS International "Physical Security for Multifamily Properties" 2024

**Layered Security Approach:**

**Layer 1: Perimeter**
- Controlled access gates (vehicle + pedestrian)
- Video surveillance (license plate recognition)
- Adequate lighting (5 foot-candles minimum)

**Layer 2: Building Entry**
- Smart locks (BLE, NFC, mobile app)
- Video intercom with remote unlock capability
- 24/7 video recording (30-day retention minimum)

**Layer 3: Unit Entry**
- Smart locks (audit trail: who entered, when)
- Temporary access codes for maintenance, showings
- Auto-expiring guest codes

**Technology Stack:**
- Access control platform: Brivo, Openpath, Latch
- Integration with PMS (auto-provision/deprovision access)
- Mobile app for residents (unlock, grant guest access)

**Audit Trail Requirements:**
- Log all access events (successful + failed attempts)
- Retention: 90 days minimum (1 year recommended)
- Alert on suspicious patterns (multiple failed attempts, unusual hours)

**Business Continuity:**
- Backup power for access systems (UPS + generator)
- Offline mode for smart locks (BLE key still works)
- Physical override keys (secured, limited distribution)

### Best Practice 10: Cybersecurity for PropTech Systems

**Source:** CISA "Cybersecurity Best Practices for Real Estate" 2024

**Network Security:**
- Segment IoT devices on separate VLAN
- Firewall rules: deny-all default, explicit allow
- Regular vulnerability scanning (weekly automated, quarterly manual)
- Intrusion detection/prevention system (IDS/IPS)

**Application Security:**
- Web application firewall (WAF)
- DDoS protection (Cloudflare, AWS Shield)
- OWASP Top 10 mitigation
- Regular penetration testing (annual minimum)

**Data Protection:**
- Database encryption (field-level for PII)
- Backup strategy: 3-2-1 rule (3 copies, 2 media types, 1 offsite)
- Regular backup testing (quarterly restore drills)
- Ransomware protection (immutable backups, air-gapped)

**Identity and Access Management:**
- Multi-factor authentication (MFA) for all users
- Password policy: 12+ characters, complexity, no reuse
- Privileged access management (PAM) for admin accounts
- Regular access reviews (quarterly)

**Incident Response:**
- Documented incident response plan
- Designated incident response team
- Annual tabletop exercises
- Cyber insurance coverage ($1M+ recommended)

**Vendor Management:**
- Security questionnaires for all vendors
- Annual SOC 2 Type II reports required
- Right to audit clause in contracts
- Data processing agreements (GDPR compliance)

---

## Benchmarking Your Organization

**Self-Assessment Scorecard:**

| Practice Area | Bronze | Silver | Gold | Platinum |
|--------------|--------|--------|------|----------|
| **Rent Collection** | 90% on-time | 95% on-time | 98% on-time | 99%+ on-time |
| **Maintenance Response** | <4 hours emergency | <2 hours emergency | <1 hour emergency | Predictive maintenance |
| **Renewal Rate** | 50-55% | 55-60% | 60-65% | 65%+ |
| **Energy Efficiency** | Baseline | 10% reduction | 20% reduction | 30%+ reduction |
| **Data Security** | Basic measures | SOC 2 Type I | SOC 2 Type II | ISO 27001 |
| **Tenant Satisfaction** | <3.5/5.0 | 3.5-4.0 | 4.0-4.5 | 4.5+ |

**Target:** Gold tier for all areas (achievable with proper technology + processes)

---

## Case Studies

### Case Study 1: Greystar - Automated Rent Collection

**Challenge:** 6.8% delinquency rate, high labor cost for collections

**Solution:**
- Mandatory ACH enrollment (95% adoption achieved)
- Automated late fee posting (day 6)
- Automated reminder sequence (day 3 before, day of, day 6, day 10, day 15)
- Auto-escalation to collections agency (day 30)

**Results:**
- Delinquency reduced to 2.1% (69% improvement)
- Collections labor reduced by 75%
- Tenant satisfaction maintained (4.3/5.0)

### Case Study 2: Equity Residential - Smart Building Deployment

**Challenge:** Rising energy costs, tenant demand for smart features

**Solution:**
- Phased rollout across 20 properties (80,000 units)
- Smart thermostats (Ecobee, BACnet-enabled)
- Occupancy-based HVAC control
- Real-time energy dashboards for tenants

**Results:**
- Energy reduction: 24% (HVAC)
- Tenant satisfaction: +8% increase
- Premium rent: +$25/month on average
- Payback period: 2.7 years

---

## References

1. **NMHC Operations Best Practices**: https://www.nmhc.org/
2. **BOMA International**: https://www.boma.org/
3. **IREM**: https://www.irem.org/
4. **National Fair Housing Alliance**: https://nationalfairhousing.org/
5. **CISA Cybersecurity**: https://www.cisa.gov/

---

*This document is maintained by the PropTech Best Practices Committee. For questions or updates, contact bestpractices@proptech.com.*

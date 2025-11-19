# Property System Migration Guide

**Version:** 3.0
**Last Updated:** 2025-01-15
**Status:** Active Standard
**Authority:** PropTech Migration Committee
**References:** Yardi Migration Guides, MRI Software, Rent Manager, AppFolio, Buildium

## Table of Contents

1. [Overview](#overview)
2. [Migration Planning](#migration-planning)
3. [Data Migration Strategies](#data-migration-strategies)
4. [Zero-Downtime Migration Patterns](#zero-downtime-migration-patterns)
5. [Parallel Run Strategies](#parallel-run-strategies)
6. [Data Validation and Reconciliation](#data-validation-and-reconciliation)
7. [Rollback Procedures](#rollback-procedures)
8. [Common Pitfalls](#common-pitfalls)
9. [Vendor-Specific Migration Guides](#vendor-specific-migration-guides)

## Overview

Migrating from legacy Property Management Systems (PMS) to modern cloud platforms is complex, involving properties, tenants, leases, financial data, and historical records. This guide provides battle-tested strategies from migrations of 10,000+ unit portfolios.

### Common Migration Scenarios

| Legacy System | Target System | Complexity | Typical Duration | Key Challenges |
|--------------|---------------|------------|------------------|----------------|
| **Yardi Voyager (On-Prem)** | Yardi Voyager (Cloud) | Medium | 6-12 months | Data export, custom integrations |
| **MRI Software** | Modern Cloud PMS | High | 9-18 months | Complex data model, custom fields |
| **Rent Manager** | AppFolio/Buildium | Medium | 4-8 months | Financial reconciliation |
| **Excel/QuickBooks** | Cloud PMS | Low-Medium | 2-4 months | Data cleaning, standardization |
| **Legacy Custom System** | Modern Platform | Very High | 12-24 months | Reverse engineering, data quality |

### Migration Success Metrics

**Target Goals:**
- **Data Accuracy**: 99.9% accuracy after reconciliation
- **Zero Data Loss**: 100% of critical records migrated
- **Minimal Downtime**: < 4 hours of service interruption
- **User Adoption**: > 90% user adoption within 30 days
- **Financial Reconciliation**: 100% balance reconciliation

## Migration Planning

### Phase 1: Discovery and Assessment (4-8 weeks)

#### Data Inventory

```python
class DataInventoryAssessment:
    """
    Assess data volume and complexity
    """

    def analyze_legacy_system(self, db_connection):
        """
        Analyze legacy database
        """
        inventory = {
            "properties": self.count_records(db_connection, "properties"),
            "units": self.count_records(db_connection, "units"),
            "tenants": self.count_records(db_connection, "tenants"),
            "leases": {
                "active": self.count_records(db_connection, "leases", "status = 'active'"),
                "historical": self.count_records(db_connection, "leases", "status != 'active'")
            },
            "transactions": {
                "charges": self.count_records(db_connection, "charges"),
                "payments": self.count_records(db_connection, "payments"),
                "refunds": self.count_records(db_connection, "refunds")
            },
            "documents": self.count_documents(),
            "custom_fields": self.identify_custom_fields(db_connection)
        }

        # Calculate data quality score
        quality_score = self.calculate_data_quality(db_connection)

        return {
            "inventory": inventory,
            "quality_score": quality_score,
            "estimated_migration_effort": self.estimate_effort(inventory)
        }

    def identify_custom_fields(self, db_connection):
        """
        Identify custom fields that need mapping
        """
        cursor = db_connection.cursor()

        # Query information schema for custom columns
        cursor.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'legacy_pms'
            AND column_name LIKE 'custom_%'
        """)

        custom_fields = cursor.fetchall()
        return custom_fields

    def calculate_data_quality(self, db_connection):
        """
        Calculate data quality metrics
        """
        quality_checks = {
            "missing_required_fields": self.check_missing_required_fields(db_connection),
            "duplicate_records": self.check_duplicates(db_connection),
            "invalid_data": self.check_invalid_data(db_connection),
            "orphaned_records": self.check_orphaned_records(db_connection)
        }

        # Calculate overall score (0-100)
        score = 100
        score -= quality_checks["missing_required_fields"] * 0.5
        score -= quality_checks["duplicate_records"] * 0.3
        score -= quality_checks["invalid_data"] * 0.8
        score -= quality_checks["orphaned_records"] * 0.2

        return max(0, score)
```

#### Stakeholder Mapping

```markdown
## Key Stakeholders

### Executive Sponsors
- **CFO**: Financial data accuracy, audit compliance
- **COO**: Operational continuity, minimal disruption
- **CTO**: Technical architecture, security

### Operational Teams
- **Property Managers**: Daily operations, training needs
- **Leasing Agents**: Tenant onboarding, lease management
- **Accounting Team**: Financial reconciliation, reporting
- **Maintenance Staff**: Work order management

### External Stakeholders
- **Property Owners**: Financial reporting, distributions
- **Tenants**: Minimal service disruption
- **Vendors**: Integration continuity
- **Auditors**: Data integrity, compliance

## Communication Plan

| Phase | Frequency | Audience | Channel | Content |
|-------|-----------|----------|---------|---------|
| Planning | Weekly | Exec sponsors | Email | Progress updates, risks |
| Pre-migration | Bi-weekly | All staff | Town halls | Timeline, training schedule |
| Migration week | Daily | All staff | Slack/Teams | Real-time updates |
| Post-migration | Weekly → Monthly | All users | Email | Issues resolution, optimization |
```

### Phase 2: Data Mapping (6-12 weeks)

#### Field Mapping Matrix

```python
class DataMapper:
    """
    Map legacy fields to new system
    """

    PROPERTY_MAPPING = {
        # Legacy Field → New System Field
        "prop_id": "property_id",
        "prop_name": "property_name",
        "prop_addr": "street_address_line_1",
        "prop_city": "city",
        "prop_state": "state_province_code",
        "prop_zip": "postal_code",
        "total_units": "total_units",
        "year_const": "year_built"
    }

    LEASE_MAPPING = {
        "lease_nbr": "lease_id",
        "ten_id": "tenant_id",
        "unit_nbr": "unit_id",
        "start_dt": "lease_start_date",
        "end_dt": "lease_end_date",
        "monthly_rent": "monthly_rent_amount",
        "sec_dep": "security_deposit_amount"
    }

    FINANCIAL_MAPPING = {
        "chrg_id": "charge_id",
        "chrg_amt": "charge_amount",
        "chrg_type": "charge_type_code",  # Requires lookup table
        "post_dt": "post_date",
        "pmt_id": "payment_id",
        "pmt_amt": "payment_amount",
        "pmt_dt": "payment_date"
    }

    def map_property(self, legacy_property):
        """
        Transform legacy property record to new format
        """
        mapped = {}

        for legacy_field, new_field in self.PROPERTY_MAPPING.items():
            if legacy_field in legacy_property:
                mapped[new_field] = legacy_property[legacy_field]

        # Data transformations
        mapped["property_type"] = self.map_property_type(
            legacy_property.get("prop_type_code")
        )

        # Parse address
        if "prop_addr2" in legacy_property and legacy_property["prop_addr2"]:
            mapped["street_address_line_2"] = legacy_property["prop_addr2"]

        # Standardize state codes
        mapped["state_province_code"] = self.standardize_state_code(
            mapped.get("state_province_code")
        )

        return mapped

    def map_property_type(self, legacy_type_code):
        """
        Map legacy property type codes to RESO standard
        """
        type_mapping = {
            "MF": "multifamily",
            "SF": "single_family",
            "CM": "commercial",
            "MX": "mixed_use",
            "SH": "student_housing"
        }

        return type_mapping.get(legacy_type_code, "unknown")

    def standardize_state_code(self, state):
        """
        Standardize state codes to 2-letter format
        """
        if not state:
            return None

        state = state.strip().upper()

        # If full state name, convert to code
        state_names = {
            "CALIFORNIA": "CA",
            "NEW YORK": "NY",
            "TEXAS": "TX",
            # ... full mapping
        }

        if state in state_names:
            return state_names[state]

        # If already 2-letter code
        if len(state) == 2:
            return state

        return None
```

### Phase 3: Test Migration (8-12 weeks)

#### Test Environment Setup

```yaml
# docker-compose.yml for test environment
version: '3.8'

services:
  legacy_pms_db:
    image: postgres:13
    environment:
      POSTGRES_DB: legacy_pms
      POSTGRES_USER: legacy_user
      POSTGRES_PASSWORD: legacy_pass
    volumes:
      - ./legacy_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  new_pms_db:
    image: postgres:15
    environment:
      POSTGRES_DB: new_pms
      POSTGRES_USER: new_user
      POSTGRES_PASSWORD: new_pass
    volumes:
      - ./new_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"

  migration_service:
    build: ./migration_service
    depends_on:
      - legacy_pms_db
      - new_pms_db
    environment:
      LEGACY_DB_URL: postgresql://legacy_user:legacy_pass@legacy_pms_db:5432/legacy_pms
      NEW_DB_URL: postgresql://new_user:new_pass@new_pms_db:5432/new_pms
    volumes:
      - ./migration_logs:/app/logs
```

## Data Migration Strategies

### Strategy 1: Big Bang Migration

**Use Case:** Small portfolios (< 500 units), simple data model

**Timeline:** 1-2 weeks

**Process:**
1. **Friday Evening**: Freeze legacy system (read-only)
2. **Weekend**: Full data migration
3. **Sunday Evening**: Data validation
4. **Monday Morning**: Go-live with new system

**Advantages:**
- Simple, one-time migration
- Clean cutover date
- No synchronization complexity

**Disadvantages:**
- High risk
- Significant downtime
- No fallback after cutover

```python
def big_bang_migration(legacy_db, new_db):
    """
    Execute full migration in single operation
    """
    try:
        # 1. Extract all data from legacy system
        print("Extracting data from legacy system...")
        properties = extract_properties(legacy_db)
        units = extract_units(legacy_db)
        tenants = extract_tenants(legacy_db)
        leases = extract_leases(legacy_db)
        financials = extract_financials(legacy_db)

        # 2. Transform data
        print("Transforming data...")
        transformed_properties = [transform_property(p) for p in properties]
        transformed_units = [transform_unit(u) for u in units]
        transformed_tenants = [transform_tenant(t) for t in tenants]
        transformed_leases = [transform_lease(l) for l in leases]
        transformed_financials = [transform_financial(f) for f in financials]

        # 3. Load into new system
        print("Loading data into new system...")
        load_properties(new_db, transformed_properties)
        load_units(new_db, transformed_units)
        load_tenants(new_db, transformed_tenants)
        load_leases(new_db, transformed_leases)
        load_financials(new_db, transformed_financials)

        # 4. Validate
        print("Validating migration...")
        validation_results = validate_migration(legacy_db, new_db)

        if validation_results["success_rate"] < 99.9:
            raise Exception(f"Validation failed: {validation_results}")

        print("Migration successful!")

    except Exception as e:
        print(f"Migration failed: {e}")
        # Rollback
        rollback_migration(new_db)
        raise
```

### Strategy 2: Phased Migration

**Use Case:** Large portfolios (> 1,000 units), multiple properties

**Timeline:** 3-6 months

**Process:**
1. **Phase 1**: Migrate Property Group A (10% of portfolio)
2. **Phase 2**: Migrate Property Group B (20% of portfolio)
3. **Phase 3**: Migrate Property Group C (30% of portfolio)
4. **Phase 4**: Migrate remaining properties (40% of portfolio)

**Advantages:**
- Lower risk per phase
- Learn and improve between phases
- Easier rollback

**Disadvantages:**
- Longer overall timeline
- Managing two systems in parallel
- Complex synchronization

```python
class PhasedMigration:
    def __init__(self, legacy_db, new_db):
        self.legacy_db = legacy_db
        self.new_db = new_db
        self.phases = self.define_phases()

    def define_phases(self):
        """
        Define migration phases by property
        """
        return [
            {
                "phase": 1,
                "name": "Pilot - Small Properties",
                "property_ids": ["PROP001", "PROP002"],  # 100 units
                "start_date": "2025-02-01",
                "cutover_date": "2025-02-15"
            },
            {
                "phase": 2,
                "name": "Mid-Size Properties",
                "property_ids": ["PROP003", "PROP004", "PROP005"],  # 500 units
                "start_date": "2025-03-01",
                "cutover_date": "2025-03-15"
            },
            {
                "phase": 3,
                "name": "Large Properties",
                "property_ids": ["PROP006", "PROP007"],  # 1000 units
                "start_date": "2025-04-01",
                "cutover_date": "2025-04-15"
            },
            {
                "phase": 4,
                "name": "Remaining Portfolio",
                "property_ids": ["PROP008", "PROP009", "PROP010"],
                "start_date": "2025-05-01",
                "cutover_date": "2025-05-15"
            }
        ]

    def execute_phase(self, phase_number):
        """
        Execute specific migration phase
        """
        phase = self.phases[phase_number - 1]
        property_ids = phase["property_ids"]

        print(f"Starting Phase {phase_number}: {phase['name']}")

        # Migrate properties in this phase
        for property_id in property_ids:
            self.migrate_property(property_id)

        # Validate phase
        validation = self.validate_phase(property_ids)

        if not validation["success"]:
            print(f"Phase {phase_number} validation failed")
            self.rollback_phase(property_ids)
            return False

        print(f"Phase {phase_number} complete")
        return True

    def migrate_property(self, property_id):
        """
        Migrate single property and all related data
        """
        # Extract property data
        property_data = self.extract_property_data(property_id)

        # Transform
        transformed = self.transform_property_data(property_data)

        # Load
        self.load_property_data(transformed)

        # Mark as migrated
        self.mark_property_migrated(property_id)
```

### Strategy 3: Trickle Migration

**Use Case:** Zero-downtime requirement, complex integrations

**Timeline:** 6-12 months

**Process:**
- Migrate properties one-by-one or small batches
- Both systems run in parallel
- Bidirectional sync during transition
- Gradual user migration

```python
class TrickleMigration:
    def __init__(self, legacy_db, new_db, sync_interval_minutes=15):
        self.legacy_db = legacy_db
        self.new_db = new_db
        self.sync_interval = sync_interval_minutes

    def setup_bidirectional_sync(self):
        """
        Set up real-time sync between systems
        """
        # Legacy → New sync
        self.setup_legacy_to_new_sync()

        # New → Legacy sync (for migrated properties)
        self.setup_new_to_legacy_sync()

    def setup_legacy_to_new_sync(self):
        """
        Sync changes from legacy to new system
        """
        from apscheduler.schedulers.background import BackgroundScheduler

        scheduler = BackgroundScheduler()

        # Sync every 15 minutes
        scheduler.add_job(
            func=self.sync_legacy_to_new,
            trigger='interval',
            minutes=self.sync_interval
        )

        scheduler.start()

    def sync_legacy_to_new(self):
        """
        Incremental sync of changes
        """
        last_sync = self.get_last_sync_timestamp()

        # Get changed records since last sync
        changed_properties = self.get_changed_properties(last_sync)
        changed_tenants = self.get_changed_tenants(last_sync)
        changed_leases = self.get_changed_leases(last_sync)
        changed_payments = self.get_changed_payments(last_sync)

        # Sync to new system
        for property in changed_properties:
            self.sync_property(property)

        for tenant in changed_tenants:
            self.sync_tenant(tenant)

        # Update last sync timestamp
        self.update_last_sync_timestamp()

    def migrate_property_with_sync(self, property_id):
        """
        Migrate property and enable ongoing sync
        """
        # Full migration
        self.migrate_property(property_id)

        # Enable bidirectional sync for this property
        self.enable_property_sync(property_id)

        # Mark as "in new system"
        self.mark_property_in_new_system(property_id)
```

## Zero-Downtime Migration Patterns

### Database Replication Approach

```python
class ZeroDowntimeMigration:
    """
    Use database replication for zero-downtime migration
    """

    def setup_replication(self):
        """
        Set up logical replication from legacy to new DB
        """
        # 1. Create replication slot on legacy database
        legacy_conn = self.connect_legacy_db()
        cursor = legacy_conn.cursor()

        cursor.execute("""
            SELECT pg_create_logical_replication_slot('migration_slot', 'pgoutput');
        """)

        # 2. Create publication (what to replicate)
        cursor.execute("""
            CREATE PUBLICATION migration_pub
            FOR TABLE properties, units, tenants, leases, charges, payments;
        """)

        # 3. Set up subscription on new database
        new_conn = self.connect_new_db()
        new_cursor = new_conn.cursor()

        new_cursor.execute("""
            CREATE SUBSCRIPTION migration_sub
            CONNECTION 'host=legacy_db port=5432 dbname=legacy_pms user=repl_user password=xxx'
            PUBLICATION migration_pub;
        """)

        print("Replication setup complete. Data will sync automatically.")

    def execute_cutover(self):
        """
        Execute final cutover with minimal downtime
        """
        # 1. Enable read-only mode on legacy system (< 1 min downtime)
        self.enable_legacy_read_only()

        # 2. Wait for replication to catch up
        self.wait_for_replication_lag_zero()

        # 3. Validate data integrity
        validation = self.validate_full_data_integrity()

        if not validation["success"]:
            self.rollback_cutover()
            raise Exception("Validation failed")

        # 4. Redirect traffic to new system
        self.redirect_traffic_to_new_system()

        # 5. Disable legacy system
        self.disable_legacy_system()

        print("Cutover complete. Downtime: < 5 minutes")
```

## Parallel Run Strategies

### Dual-Write Pattern

```python
class DualWriteService:
    """
    Write to both legacy and new system during transition
    """

    def __init__(self, legacy_client, new_client):
        self.legacy = legacy_client
        self.new = new_client

    def create_lease(self, lease_data):
        """
        Create lease in both systems
        """
        try:
            # Write to new system (source of truth)
            new_lease = self.new.create_lease(lease_data)

            # Write to legacy system (for continuity)
            legacy_lease_data = self.transform_for_legacy(lease_data)
            legacy_lease = self.legacy.create_lease(legacy_lease_data)

            # Store mapping between systems
            self.save_lease_mapping(
                new_lease_id=new_lease.id,
                legacy_lease_id=legacy_lease.id
            )

            return new_lease

        except Exception as e:
            # Rollback both systems
            self.rollback_lease_creation(new_lease, legacy_lease)
            raise

    def update_lease(self, lease_id, updates):
        """
        Update lease in both systems
        """
        # Get mapping
        mapping = self.get_lease_mapping(lease_id)

        # Update new system
        self.new.update_lease(lease_id, updates)

        # Update legacy system
        legacy_updates = self.transform_for_legacy(updates)
        self.legacy.update_lease(mapping["legacy_lease_id"], legacy_updates)
```

### Shadow Mode Testing

```python
class ShadowModeValidator:
    """
    Run new system in shadow mode to validate behavior
    """

    def process_transaction_shadow_mode(self, transaction):
        """
        Process in legacy (production) and new (shadow) in parallel
        """
        # Production: Legacy system
        legacy_result = self.legacy.process_transaction(transaction)

        # Shadow: New system (non-blocking, logged only)
        try:
            new_result = self.new.process_transaction(transaction)

            # Compare results
            if not self.results_match(legacy_result, new_result):
                self.log_discrepancy(transaction, legacy_result, new_result)
                self.alert_team("Shadow mode discrepancy detected")

        except Exception as e:
            self.log_shadow_error(transaction, e)
            # Don't fail production transaction

        # Always return legacy result (production)
        return legacy_result

    def results_match(self, legacy_result, new_result):
        """
        Compare results for equivalence
        """
        # Compare key fields
        return (
            legacy_result["balance"] == new_result["balance"] and
            legacy_result["status"] == new_result["status"]
        )
```

## Data Validation and Reconciliation

### Automated Validation Framework

```python
class MigrationValidator:
    """
    Comprehensive validation of migrated data
    """

    def validate_full_migration(self):
        """
        Run all validation checks
        """
        validation_results = {
            "record_counts": self.validate_record_counts(),
            "data_integrity": self.validate_data_integrity(),
            "referential_integrity": self.validate_referential_integrity(),
            "financial_reconciliation": self.validate_financial_reconciliation(),
            "business_rules": self.validate_business_rules()
        }

        # Calculate overall success rate
        total_checks = sum(r["total_checks"] for r in validation_results.values())
        passed_checks = sum(r["passed_checks"] for r in validation_results.values())

        success_rate = (passed_checks / total_checks) * 100

        return {
            "success_rate": success_rate,
            "details": validation_results,
            "passed": success_rate >= 99.9
        }

    def validate_record_counts(self):
        """
        Ensure all records migrated
        """
        legacy_counts = {
            "properties": self.count_legacy_records("properties"),
            "units": self.count_legacy_records("units"),
            "tenants": self.count_legacy_records("tenants"),
            "leases": self.count_legacy_records("leases"),
            "payments": self.count_legacy_records("payments")
        }

        new_counts = {
            "properties": self.count_new_records("properties"),
            "units": self.count_new_records("units"),
            "tenants": self.count_new_records("tenants"),
            "leases": self.count_new_records("leases"),
            "payments": self.count_new_records("payments")
        }

        mismatches = []
        for table, legacy_count in legacy_counts.items():
            new_count = new_counts[table]
            if legacy_count != new_count:
                mismatches.append({
                    "table": table,
                    "legacy_count": legacy_count,
                    "new_count": new_count,
                    "difference": new_count - legacy_count
                })

        return {
            "total_checks": len(legacy_counts),
            "passed_checks": len(legacy_counts) - len(mismatches),
            "mismatches": mismatches
        }

    def validate_financial_reconciliation(self):
        """
        Ensure financial balances match
        """
        discrepancies = []

        # Get all leases
        leases = self.get_all_leases()

        for lease in leases:
            # Calculate balance in legacy system
            legacy_balance = self.calculate_legacy_balance(lease.legacy_id)

            # Calculate balance in new system
            new_balance = self.calculate_new_balance(lease.new_id)

            # Allow $0.01 difference for rounding
            if abs(legacy_balance - new_balance) > 0.01:
                discrepancies.append({
                    "lease_id": lease.new_id,
                    "legacy_balance": legacy_balance,
                    "new_balance": new_balance,
                    "difference": new_balance - legacy_balance
                })

        return {
            "total_checks": len(leases),
            "passed_checks": len(leases) - len(discrepancies),
            "discrepancies": discrepancies
        }

    def validate_business_rules(self):
        """
        Validate business rules are maintained
        """
        violations = []

        # Check: No overlapping leases for same unit
        overlapping_leases = self.find_overlapping_leases()
        if overlapping_leases:
            violations.extend(overlapping_leases)

        # Check: Active leases have valid tenants
        invalid_tenant_leases = self.find_leases_with_invalid_tenants()
        if invalid_tenant_leases:
            violations.extend(invalid_tenant_leases)

        # Check: Security deposits match lease terms
        deposit_mismatches = self.find_deposit_mismatches()
        if deposit_mismatches:
            violations.extend(deposit_mismatches)

        return {
            "total_checks": 3,  # Number of rule types checked
            "passed_checks": 3 - len(violations),
            "violations": violations
        }
```

## Rollback Procedures

### Rollback Decision Matrix

| Scenario | Severity | Action | Timeline |
|----------|----------|--------|----------|
| **< 95% data accuracy** | Critical | Immediate rollback | < 1 hour |
| **Financial discrepancy > $1,000** | Critical | Immediate rollback | < 1 hour |
| **Major functionality broken** | High | Rollback within 4 hours | 4 hours |
| **Performance issues** | Medium | Fix forward or rollback | 24 hours |
| **Minor UI issues** | Low | Fix forward | N/A |

### Automated Rollback Script

```python
class MigrationRollback:
    """
    Automated rollback procedures
    """

    def execute_rollback(self, reason):
        """
        Execute full rollback
        """
        print(f"INITIATING ROLLBACK: {reason}")

        try:
            # 1. Stop traffic to new system
            self.stop_new_system_traffic()

            # 2. Restore legacy system access
            self.restore_legacy_system()

            # 3. Sync any data created in new system back to legacy
            self.reverse_sync_new_to_legacy()

            # 4. Validate legacy system operational
            validation = self.validate_legacy_system()

            if not validation["success"]:
                raise Exception("Legacy system validation failed")

            # 5. Notify stakeholders
            self.notify_rollback_complete(reason)

            print("ROLLBACK COMPLETE")

        except Exception as e:
            print(f"ROLLBACK FAILED: {e}")
            self.escalate_to_incident_response()

    def create_rollback_snapshot(self):
        """
        Create snapshot before migration for rollback
        """
        # Database snapshot
        self.create_db_snapshot()

        # File system backup
        self.create_file_backup()

        # Configuration backup
        self.backup_configuration()
```

## Common Pitfalls

### Pitfall 1: Inadequate Data Cleaning

**Problem:** Migrating dirty data perpetuates issues

**Solution:**
```python
def clean_tenant_data(tenants):
    """
    Clean tenant data before migration
    """
    cleaned = []

    for tenant in tenants:
        # Remove duplicates (same email)
        if tenant.email in seen_emails:
            # Merge with existing record
            merge_tenant_records(existing, tenant)
            continue

        # Standardize phone numbers
        tenant.phone = standardize_phone(tenant.phone)

        # Validate email
        if not is_valid_email(tenant.email):
            flag_for_manual_review(tenant)
            continue

        # Standardize names
        tenant.first_name = tenant.first_name.title()
        tenant.last_name = tenant.last_name.title()

        cleaned.append(tenant)

    return cleaned
```

### Pitfall 2: Ignoring Historical Data

**Problem:** Focusing only on active records, losing history

**Solution:**
- Migrate ALL historical leases, even terminated
- Migrate complete payment history (5-7 years)
- Preserve audit trails and modification history

### Pitfall 3: Insufficient Testing

**Problem:** Discovering issues in production

**Solution:**
- Test with FULL production data copy
- Test all user workflows end-to-end
- Performance testing with production load
- Parallel run for 30+ days

## Vendor-Specific Migration Guides

### Yardi Voyager Migration

```python
class YardiVoyagerMigrator:
    """
    Yardi-specific migration patterns
    """

    def export_yardi_data(self):
        """
        Export data using Yardi export tools
        """
        # Use Yardi Export Designer
        # Export formats: CSV, XML, Fixed-width

        exports = {
            "properties": "PropertyExport.csv",
            "units": "UnitExport.csv",
            "tenants": "TenantExport.csv",
            "leases": "LeaseExport.csv",
            "gl_accounts": "GLAccountExport.csv",
            "transactions": "TransactionExport.csv"
        }

        return exports

    def parse_yardi_export(self, export_file):
        """
        Parse Yardi export format
        """
        import csv

        with open(export_file, 'r') as f:
            # Yardi uses specific date formats: MM/DD/YYYY
            reader = csv.DictReader(f)
            records = []

            for row in reader:
                # Parse Yardi date format
                if 'LeaseStartDate' in row:
                    row['LeaseStartDate'] = self.parse_yardi_date(row['LeaseStartDate'])

                # Parse Yardi currency format: $1,234.56
                if 'MonthlyRent' in row:
                    row['MonthlyRent'] = self.parse_yardi_currency(row['MonthlyRent'])

                records.append(row)

        return records

    def parse_yardi_date(self, date_str):
        """
        Parse Yardi date format
        """
        from datetime import datetime

        if not date_str:
            return None

        # Yardi format: MM/DD/YYYY
        return datetime.strptime(date_str, '%m/%d/%Y').date()

    def parse_yardi_currency(self, currency_str):
        """
        Parse Yardi currency format
        """
        if not currency_str:
            return 0

        # Remove $ and commas
        cleaned = currency_str.replace('$', '').replace(',', '')
        return float(cleaned)
```

### MRI Software Migration

```python
class MRISoftwareMigrator:
    """
    MRI-specific migration patterns
    """

    # MRI uses SQL Server database

    def connect_mri_database(self):
        """
        Connect to MRI SQL Server database
        """
        import pyodbc

        conn_str = (
            "DRIVER={SQL Server};"
            "SERVER=mri_server;"
            "DATABASE=MRI_Production;"
            "UID=mri_user;"
            "PWD=password"
        )

        return pyodbc.connect(conn_str)

    def extract_mri_properties(self):
        """
        Extract properties from MRI database
        """
        conn = self.connect_mri_database()
        cursor = conn.cursor()

        # MRI table: Property
        cursor.execute("""
            SELECT
                PropertyID,
                PropertyName,
                Address1,
                Address2,
                City,
                State,
                ZipCode,
                TotalUnits,
                PropertyType,
                YearBuilt
            FROM Property
            WHERE Active = 1
        """)

        properties = cursor.fetchall()
        return properties
```

---

## References

1. **Yardi Migration Best Practices**: https://www.yardi.com/
2. **MRI Software Migration Guide**: https://www.mrisoftware.com/
3. **AWS Database Migration Service**: https://aws.amazon.com/dms/
4. **PostgreSQL Logical Replication**: https://www.postgresql.org/docs/current/logical-replication.html

---

*This document is maintained by the PropTech Migration Committee. For questions or updates, contact migrations@proptech.com.*

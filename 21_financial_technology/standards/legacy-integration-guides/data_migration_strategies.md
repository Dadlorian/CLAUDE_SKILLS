# Data Migration Strategies: From Legacy Systems to Modern Platforms

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Data Migration Fundamentals](#data-migration-fundamentals)
3. [Pre-Migration Planning](#pre-migration-planning)
4. [Data Assessment and Profiling](#data-assessment-and-profiling)
5. [Migration Approaches](#migration-approaches)
6. [Reconciliation Strategies](#reconciliation-strategies)
7. [Risk Management](#risk-management)
8. [Real-World Case Studies](#real-world-case-studies)
9. [Post-Migration Validation](#post-migration-validation)

---

## Executive Summary

Data migration represents the highest-risk component of legacy modernization. A single data integrity issue can cause cascading business failures across millions of accounts. This guide provides comprehensive strategies for planning, executing, and validating large-scale banking data migrations.

### Critical Success Metrics

| Metric | Target | Consequence of Failure |
|--------|--------|----------------------|
| **Data Accuracy** | 100% | Account balance errors, audit failures |
| **Completeness** | 100% | Lost records, customer disputes |
| **Timeliness** | On schedule | Regulatory violations, reputation damage |
| **Validation Coverage** | 100% | Undetected data quality issues |
| **Rollback Capability** | <30 minutes | Extended system downtime |

---

## Data Migration Fundamentals

### Core Principles

```
1. PLAN THOROUGHLY
   - Understand source data completely
   - Map all business rules
   - Identify dependencies

2. VALIDATE EXTENSIVELY
   - Test with real data subsets
   - Validate all transformation rules
   - Reconcile before go-live

3. MONITOR CAREFULLY
   - Track every record movement
   - Alert on anomalies
   - Maintain audit trail

4. COMMUNICATE CONSTANTLY
   - Status updates to stakeholders
   - Issues escalated immediately
   - Lessons learned documented
```

### Banking Data Categories

```
Primary Data (Critical)
├── Customer Master Records
│   ├── Demographics
│   ├── KYC/AML Status
│   └── Account Relationships
├── Account Master Records
│   ├── Account Details
│   ├── Balances
│   └── Interest Rates
└── Transaction History
    ├── Posted Transactions
    ├── Pending Transactions
    └── Reversals/Adjustments

Secondary Data (Important)
├── Customer Contact Information
├── Collateral Records
├── Loan Documentation
└── Standing Instructions

Metadata (Essential)
├── Source System Configuration
├── Audit Trail
├── Business Rules
└── System State at Cutover
```

---

## Pre-Migration Planning

### Phase 1: Discovery and Planning (Weeks 1-8)

#### Step 1: Data Inventory

```python
class DataInventoryAssessment:
    """Comprehensive data inventory and assessment"""

    def __init__(self):
        self.inventory = {}
        self.dependencies = {}

    def catalog_all_data(self, source_system):
        """Create complete data catalog"""

        data_entities = [
            'ACCOUNTS',
            'CUSTOMERS',
            'TRANSACTIONS',
            'GL_ACCOUNTS',
            'COLLATERAL',
            'LOANS',
            'DEPOSITS',
            'INTEREST_ACCRUALS',
            'FEES',
            'ALERTS',
            'DOCUMENTS'
        ]

        for entity in data_entities:
            catalog = {
                'entity_name': entity,
                'record_count': self._get_record_count(source_system, entity),
                'data_size_mb': self._get_data_size(source_system, entity),
                'growth_rate_daily': self._calculate_growth(source_system, entity),
                'last_accessed': self._get_last_access_time(source_system, entity),
                'dependencies': self._find_dependencies(source_system, entity),
                'criticality': self._assess_criticality(entity),
                'data_quality': self._assess_quality(source_system, entity),
                'sample_records': self._get_sample_records(source_system, entity, 10)
            }

            self.inventory[entity] = catalog

    def _get_record_count(self, source_system, entity: str) -> int:
        """Get total record count for entity"""
        query = f"SELECT COUNT(*) FROM {entity}"
        return source_system.execute(query).fetchone()[0]

    def _get_data_size(self, source_system, entity: str) -> float:
        """Get physical data size"""
        query = f"SELECT SUM(SIZE) FROM {entity}"
        size_bytes = source_system.execute(query).fetchone()[0]
        return size_bytes / (1024 * 1024)  # Convert to MB

    def _assess_quality(self, source_system, entity: str) -> dict:
        """Assess data quality metrics"""

        quality_report = {
            'null_values': self._count_null_values(source_system, entity),
            'duplicate_records': self._count_duplicates(source_system, entity),
            'orphaned_records': self._count_orphans(source_system, entity),
            'malformed_data': self._count_malformed(source_system, entity),
            'quality_score': 0
        }

        # Calculate overall quality score (0-100)
        issues = (
            quality_report['null_values'] +
            quality_report['duplicate_records'] +
            quality_report['orphaned_records'] +
            quality_report['malformed_data']
        )

        total_records = self._get_record_count(source_system, entity)
        quality_report['quality_score'] = max(
            0,
            100 - (issues / total_records * 100)
        )

        return quality_report

    def _find_dependencies(self, source_system, entity: str) -> list:
        """Identify dependencies between entities"""

        dependencies = []

        # Query foreign key relationships
        fk_query = f"""
            SELECT REFERENCED_TABLE, REFERENCED_COLUMN
            FROM FOREIGN_KEYS
            WHERE TABLE_NAME = '{entity}'
        """

        results = source_system.execute(fk_query).fetchall()

        for ref_table, ref_column in results:
            dependencies.append({
                'depends_on': ref_table,
                'field': ref_column,
                'required': True
            })

        return dependencies

    def generate_report(self) -> dict:
        """Generate comprehensive assessment report"""

        return {
            'total_entities': len(self.inventory),
            'total_records': sum(e['record_count'] for e in self.inventory.values()),
            'total_size_gb': sum(e['data_size_mb'] for e in self.inventory.values()) / 1024,
            'daily_growth_mb': sum(e['growth_rate_daily'] for e in self.inventory.values()),
            'quality_issues': self._summarize_quality_issues(),
            'critical_entities': self._identify_critical_entities(),
            'dependencies': self.dependencies,
            'recommendations': self._generate_recommendations()
        }

    def _summarize_quality_issues(self) -> dict:
        """Summarize all data quality issues"""

        issues = {}
        for entity, catalog in self.inventory.items():
            if catalog['data_quality']['quality_score'] < 95:
                issues[entity] = catalog['data_quality']

        return issues

    def _identify_critical_entities(self) -> list:
        """Identify business-critical entities that need careful migration"""

        critical = []
        for entity, catalog in self.inventory.items():
            if catalog['criticality'] in ['CRITICAL', 'HIGH']:
                critical.append({
                    'entity': entity,
                    'criticality': catalog['criticality'],
                    'record_count': catalog['record_count'],
                    'quality_issues': catalog['data_quality']
                })

        return critical
```

#### Step 2: Technical Architecture Planning

```python
class MigrationArchitecture:
    """Design technical migration architecture"""

    def __init__(self):
        self.source_system = SourceSystemConnector()
        self.target_system = TargetSystemConnector()
        self.staging_environment = StagingEnvironment()

    def design_migration_platform(self):
        """Design comprehensive migration infrastructure"""

        architecture = {
            'extraction_layer': {
                'type': 'CDC (Change Data Capture)',
                'tools': ['Debezium', 'GoldenGate'],
                'frequency': 'Real-time streaming',
                'backup': 'Daily full export'
            },

            'transformation_layer': {
                'type': 'ETL Pipeline',
                'tools': ['Apache Spark', 'Talend'],
                'schema_mapping': self._design_schema_mapping(),
                'business_rules': self._encode_business_rules(),
                'data_quality_rules': self._define_quality_rules()
            },

            'loading_layer': {
                'type': 'Incremental bulk load',
                'batch_size': 10000,
                'parallel_threads': 20,
                'retry_logic': 'Exponential backoff'
            },

            'validation_layer': {
                'automated_checks': self._design_automated_checks(),
                'manual_review': self._design_manual_review_process(),
                'rollback_capability': 'Full restore from backup'
            },

            'monitoring_layer': {
                'metrics': [
                    'Records processed',
                    'Processing speed',
                    'Error rate',
                    'Data quality score',
                    'Reconciliation status'
                ],
                'alerting': 'Real-time anomaly detection'
            }
        }

        return architecture

    def _design_schema_mapping(self) -> dict:
        """Design mapping between source and target schemas"""

        mapping = {
            'LEGACY_ACCOUNT_MASTER': {
                'target_table': 'accounts',
                'field_mappings': {
                    'ACCT_ID': {'target': 'account_id', 'transform': 'TRIM'},
                    'CUST_ID': {'target': 'customer_id', 'transform': 'TRIM'},
                    'BAL': {'target': 'balance', 'transform': 'DIVIDE_BY_100'},
                    'ACCT_TYPE': {
                        'target': 'account_type',
                        'transform': 'LOOKUP',
                        'lookup_table': 'account_type_map'
                    },
                    'STAT': {
                        'target': 'status',
                        'transform': 'MAP_STATUS'
                    },
                    'OPEN_DT': {'target': 'created_date', 'transform': 'PARSE_COBOL_DATE'},
                    'CLOSE_DT': {'target': 'closed_date', 'transform': 'PARSE_COBOL_DATE_NULLABLE'}
                },
                'merge_key': ['account_id'],
                'update_strategy': 'UPDATE_IF_NEWER'
            },

            'LEGACY_TRANSACTION_HISTORY': {
                'target_table': 'transactions',
                'field_mappings': {
                    'TXN_ID': {'target': 'transaction_id', 'transform': 'IDENTITY'},
                    'FROM_ACCT': {'target': 'from_account', 'transform': 'TRIM'},
                    'TO_ACCT': {'target': 'to_account', 'transform': 'TRIM'},
                    'AMT': {'target': 'amount', 'transform': 'DIVIDE_BY_100'},
                    'TXN_DT': {'target': 'transaction_date', 'transform': 'PARSE_COBOL_DATE'},
                    'STAT': {'target': 'status', 'transform': 'MAP_STATUS'}
                },
                'merge_key': ['transaction_id'],
                'update_strategy': 'APPEND_ONLY'
            }
        }

        return mapping

    def _encode_business_rules(self) -> dict:
        """Encode business rules for data transformation"""

        rules = {
            'ACCOUNT_STATUS_MAPPING': {
                'A': 'ACTIVE',
                'I': 'INACTIVE',
                'S': 'SUSPENDED',
                'C': 'CLOSED',
                'P': 'PENDING'
            },

            'ACCOUNT_TYPE_MAPPING': {
                'CA': 'CHECKING',
                'SA': 'SAVINGS',
                'MA': 'MONEY_MARKET',
                'CD': 'CERTIFICATE_OF_DEPOSIT',
                'LN': 'LOAN',
                'CC': 'CREDIT_CARD'
            },

            'BALANCE_VALIDATION': {
                'rule': 'Balance must be >= 0 unless overdraft allowed',
                'check': 'IF status="ACTIVE" THEN balance >= 0'
            },

            'INTEREST_ACCRUAL': {
                'rule': 'Calculate interest on savings accounts',
                'formula': 'daily_interest = (balance * annual_rate) / 365'
            }
        }

        return rules
```

---

## Data Assessment and Profiling

### Comprehensive Data Quality Assessment

```python
class DataQualityFramework:
    """Comprehensive data quality assessment and reporting"""

    def __init__(self):
        self.profiling_results = {}
        self.issues = []

    def profile_source_data(self, source_system, entity: str) -> dict:
        """Comprehensive data profiling"""

        profile = {
            'entity': entity,
            'profile_timestamp': datetime.now(),
            'record_statistics': self._calculate_record_statistics(source_system, entity),
            'column_analysis': self._analyze_columns(source_system, entity),
            'data_quality_issues': self._identify_quality_issues(source_system, entity),
            'business_rule_violations': self._check_business_rules(source_system, entity),
            'referential_integrity': self._check_referential_integrity(source_system, entity)
        }

        return profile

    def _calculate_record_statistics(self, source_system, entity: str) -> dict:
        """Calculate record-level statistics"""

        query = f"SELECT COUNT(*), MIN(CREATED_DATE), MAX(CREATED_DATE) FROM {entity}"
        result = source_system.execute(query).fetchone()

        return {
            'total_records': result[0],
            'oldest_record': result[1],
            'newest_record': result[2],
            'data_age_days': (datetime.now() - result[1]).days
        }

    def _analyze_columns(self, source_system, entity: str) -> list:
        """Analyze each column for data quality"""

        columns = source_system.get_columns(entity)
        analysis = []

        for column in columns:
            col_analysis = {
                'column_name': column['name'],
                'data_type': column['type'],
                'null_count': self._count_nulls(source_system, entity, column['name']),
                'null_percentage': self._calculate_null_percentage(
                    source_system, entity, column['name']
                ),
                'distinct_values': self._count_distinct(
                    source_system, entity, column['name']
                ),
                'sample_values': self._get_sample_values(
                    source_system, entity, column['name'], 5
                ),
                'data_range': self._get_data_range(
                    source_system, entity, column['name']
                )
            }

            analysis.append(col_analysis)

        return analysis

    def _identify_quality_issues(self, source_system, entity: str) -> list:
        """Identify data quality issues"""

        issues = []

        # Check 1: Null values in required fields
        required_fields = self._get_required_fields(entity)
        for field in required_fields:
            null_count = self._count_nulls(source_system, entity, field)
            if null_count > 0:
                issues.append({
                    'type': 'NULL_IN_REQUIRED_FIELD',
                    'severity': 'CRITICAL',
                    'field': field,
                    'count': null_count,
                    'remediation': f'Populate {null_count} null values before migration'
                })

        # Check 2: Duplicate records
        duplicates = self._find_duplicates(source_system, entity)
        if duplicates:
            issues.append({
                'type': 'DUPLICATE_RECORDS',
                'severity': 'HIGH',
                'count': len(duplicates),
                'remediation': 'Deduplicate records before migration'
            })

        # Check 3: Orphaned records
        orphans = self._find_orphaned_records(source_system, entity)
        if orphans:
            issues.append({
                'type': 'ORPHANED_RECORDS',
                'severity': 'HIGH',
                'count': len(orphans),
                'remediation': 'Remove orphaned records or create missing parent records'
            })

        return issues

    def _check_business_rules(self, source_system, entity: str) -> list:
        """Check business rule violations"""

        violations = []

        if entity == 'ACCOUNTS':
            # Rule: Account balance must match sum of transactions
            mismatched = self._find_balance_mismatches(source_system)
            if mismatched:
                violations.append({
                    'rule': 'Account balance reconciliation',
                    'violations': len(mismatched),
                    'examples': mismatched[:10]
                })

            # Rule: Status transitions must be valid
            invalid_transitions = self._find_invalid_status_transitions(source_system)
            if invalid_transitions:
                violations.append({
                    'rule': 'Valid status transitions',
                    'violations': len(invalid_transitions)
                })

        return violations

    def _check_referential_integrity(self, source_system, entity: str) -> dict:
        """Check referential integrity"""

        integrity = {
            'valid': True,
            'foreign_key_violations': [],
            'constraint_violations': []
        }

        # Get all foreign keys for entity
        fks = source_system.get_foreign_keys(entity)

        for fk in fks:
            violations = self._find_fk_violations(
                source_system,
                entity,
                fk['column'],
                fk['referenced_table'],
                fk['referenced_column']
            )

            if violations:
                integrity['valid'] = False
                integrity['foreign_key_violations'].append({
                    'foreign_key': fk['name'],
                    'violations': len(violations),
                    'examples': violations[:5]
                })

        return integrity

    def generate_quality_report(self, profiles: list) -> str:
        """Generate comprehensive quality report"""

        report = "DATA QUALITY ASSESSMENT REPORT\n"
        report += "=" * 80 + "\n\n"

        total_records = sum(p['record_statistics']['total_records'] for p in profiles)
        total_issues = sum(len(p['data_quality_issues']) for p in profiles)

        report += f"Summary:\n"
        report += f"  Total Records: {total_records:,}\n"
        report += f"  Total Issues Found: {total_issues}\n"
        report += f"  Quality Score: {self._calculate_quality_score(profiles):.1f}%\n\n"

        for profile in profiles:
            report += f"\nEntity: {profile['entity']}\n"
            report += f"  Records: {profile['record_statistics']['total_records']:,}\n"
            report += f"  Data Age: {profile['record_statistics']['data_age_days']} days\n"

            if profile['data_quality_issues']:
                report += f"  Issues:\n"
                for issue in profile['data_quality_issues']:
                    report += f"    - {issue['type']}: {issue['count']} records\n"

        return report

    def _calculate_quality_score(self, profiles: list) -> float:
        """Calculate overall data quality score"""
        # Implementation...
        pass
```

---

## Migration Approaches

### Approach 1: Big Bang Migration (High Risk, Fast)

```python
class BigBangMigration:
    """One-time complete data migration (cutover day)"""

    def __init__(self):
        self.source = SourceSystem()
        self.target = TargetSystem()
        self.validation = ValidationFramework()

    def execute_big_bang(self, cutover_date: datetime) -> dict:
        """Execute complete migration on cutover date"""

        execution_log = {
            'start_time': datetime.now(),
            'phases': []
        }

        try:
            # Phase 1: Freeze source system (stop all writes)
            logger.info("Phase 1: Freezing source system")
            self.source.enable_readonly_mode()
            execution_log['phases'].append({
                'name': 'FREEZE_SOURCE',
                'duration': 5,
                'status': 'SUCCESS'
            })

            # Phase 2: Final incremental sync
            logger.info("Phase 2: Final incremental sync")
            changes = self.source.get_changes_since(execution_log['start_time'])
            self.target.apply_changes(changes)
            execution_log['phases'].append({
                'name': 'FINAL_SYNC',
                'records_synced': len(changes),
                'status': 'SUCCESS'
            })

            # Phase 3: Validate data completeness
            logger.info("Phase 3: Validating data")
            validation_result = self.validation.validate_complete_migration()
            if not validation_result['complete']:
                raise ValidationException("Data validation failed")
            execution_log['phases'].append({
                'name': 'VALIDATION',
                'status': 'SUCCESS',
                'validation_details': validation_result
            })

            # Phase 4: Switch traffic to new system
            logger.info("Phase 4: Switching traffic")
            self._switch_traffic()
            execution_log['phases'].append({
                'name': 'TRAFFIC_SWITCH',
                'duration': 1,
                'status': 'SUCCESS'
            })

            # Phase 5: Monitor for issues
            logger.info("Phase 5: Monitoring for issues")
            self._monitor_for_issues(duration_minutes=60)
            execution_log['phases'].append({
                'name': 'MONITORING',
                'status': 'SUCCESS'
            })

            execution_log['end_time'] = datetime.now()
            execution_log['overall_status'] = 'SUCCESS'

            return execution_log

        except Exception as e:
            logger.error(f"Big bang migration failed: {e}")
            execution_log['phases'].append({
                'name': 'ERROR_ROLLBACK',
                'status': 'IN_PROGRESS'
            })

            # Rollback to source system
            self._rollback_to_source()

            execution_log['overall_status'] = 'FAILED_ROLLED_BACK'
            return execution_log

    def _switch_traffic(self):
        """Switch all traffic from source to target"""
        # Update routing tables/DNS
        # Notify all clients
        # Monitor for errors
        pass

    def _monitor_for_issues(self, duration_minutes: int):
        """Monitor system for issues after switch"""
        end_time = datetime.now() + timedelta(minutes=duration_minutes)

        while datetime.now() < end_time:
            metrics = self.target.get_metrics()

            if metrics['error_rate'] > 0.1:  # >0.1% errors
                raise MonitoringException("Error rate too high")

            time.sleep(10)  # Check every 10 seconds

    def _rollback_to_source(self):
        """Rollback to source system"""
        logger.warning("Rolling back to source system")
        # Switch traffic back to source
        # Keep target for investigation
        # Notify stakeholders
        pass
```

### Approach 2: Phased Migration (Moderate Risk, Weeks/Months)

```python
class PhasedMigration:
    """Gradual migration by business function or region"""

    def __init__(self):
        self.source = SourceSystem()
        self.target = TargetSystem()
        self.phases = []

    def plan_phased_migration(self) -> list:
        """Create detailed phase plan"""

        phases = [
            {
                'phase_number': 1,
                'name': 'Data Foundation',
                'duration_weeks': 2,
                'scope': ['CUSTOMERS', 'ACCOUNT_MASTER'],
                'success_criteria': [
                    '100% of customer records migrated',
                    'Account master data validated',
                    'No data loss or corruption'
                ],
                'rollback_complexity': 'LOW'
            },
            {
                'phase_number': 2,
                'name': 'Historical Transactions',
                'duration_weeks': 3,
                'scope': ['TRANSACTION_HISTORY_2020', 'TRANSACTION_HISTORY_2021'],
                'success_criteria': [
                    'All historical transactions migrated',
                    'Balance reconciliation complete',
                    'Audit trail preserved'
                ],
                'rollback_complexity': 'MEDIUM'
            },
            {
                'phase_number': 3,
                'name': 'Recent Transactions',
                'duration_weeks': 2,
                'scope': ['TRANSACTION_HISTORY_2022_2023'],
                'success_criteria': [
                    'Recent transactions in target system',
                    'Real-time transactions synchronized',
                    'Zero transaction loss'
                ],
                'rollback_complexity': 'HIGH'
            },
            {
                'phase_number': 4,
                'name': 'Cutover to New System',
                'duration_weeks': 1,
                'scope': ['ALL_REMAINING_DATA'],
                'success_criteria': [
                    'All data in target system',
                    'Source system in read-only mode',
                    'Zero downtime cutover'
                ],
                'rollback_complexity': 'VERY_HIGH'
            }
        ]

        return phases

    def execute_phase(self, phase: dict) -> dict:
        """Execute single migration phase"""

        phase_result = {
            'phase_number': phase['phase_number'],
            'phase_name': phase['name'],
            'start_time': datetime.now(),
            'status': 'IN_PROGRESS',
            'milestones': []
        }

        try:
            # Execute extraction
            extracted = self._extract_phase_data(phase['scope'])
            phase_result['milestones'].append({
                'name': 'EXTRACT',
                'records': len(extracted),
                'duration_minutes': 30
            })

            # Execute transformation
            transformed = self._transform_phase_data(extracted)
            phase_result['milestones'].append({
                'name': 'TRANSFORM',
                'records': len(transformed),
                'duration_minutes': 45
            })

            # Execute loading
            loaded = self._load_phase_data(transformed)
            phase_result['milestones'].append({
                'name': 'LOAD',
                'records': len(loaded),
                'duration_minutes': 60
            })

            # Validate phase
            validation = self._validate_phase(phase, loaded)
            if not validation['passed']:
                raise ValidationException(f"Phase validation failed: {validation['errors']}")

            phase_result['milestones'].append({
                'name': 'VALIDATE',
                'status': 'PASSED',
                'duration_minutes': 30
            })

            phase_result['end_time'] = datetime.now()
            phase_result['status'] = 'SUCCESS'

            return phase_result

        except Exception as e:
            phase_result['status'] = 'FAILED'
            phase_result['error'] = str(e)
            phase_result['end_time'] = datetime.now()

            # Can roll back individual phase
            logger.error(f"Phase {phase['phase_number']} failed: {e}")
            return phase_result

    def _extract_phase_data(self, scope: list) -> list:
        """Extract data for phase"""
        # Extract only entities in scope
        pass

    def _transform_phase_data(self, data: list) -> list:
        """Transform data for phase"""
        # Apply transformations
        pass

    def _load_phase_data(self, data: list) -> list:
        """Load data into target"""
        # Load with deduplication
        pass

    def _validate_phase(self, phase: dict, loaded_data: list) -> dict:
        """Validate phase completion"""

        validation_result = {
            'passed': True,
            'errors': [],
            'warnings': []
        }

        for criterion in phase['success_criteria']:
            result = self._check_criterion(criterion, loaded_data)
            if not result['passed']:
                validation_result['passed'] = False
                validation_result['errors'].append(result['message'])

        return validation_result
```

### Approach 3: Parallel Run (Lowest Risk, Longest Duration)

```python
class ParallelRunMigration:
    """Run both systems in parallel with reconciliation"""

    def __init__(self):
        self.source = SourceSystem()
        self.target = TargetSystem()
        self.reconciliation = ReconciliationEngine()

    def run_parallel_mode(self, duration_weeks: int = 4) -> dict:
        """Run both systems in parallel"""

        parallel_run = {
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(weeks=duration_weeks),
            'daily_reconciliations': [],
            'discrepancies': [],
            'status': 'IN_PROGRESS'
        }

        current_date = parallel_run['start_date']

        while current_date <= parallel_run['end_date']:
            daily_recon = self._perform_daily_reconciliation(
                current_date,
                parallel_run
            )

            parallel_run['daily_reconciliations'].append(daily_recon)

            if daily_recon['discrepancies']:
                parallel_run['discrepancies'].extend(daily_recon['discrepancies'])

            # Check if we can exit early
            if self._can_exit_parallel_mode(parallel_run):
                logger.info("Parallel mode validation complete, proceeding to cutover")
                break

            current_date += timedelta(days=1)

        return parallel_run

    def _perform_daily_reconciliation(self, date: datetime, run_log: dict) -> dict:
        """Perform daily reconciliation between systems"""

        recon = {
            'date': date,
            'start_time': datetime.now(),
            'source_stats': {},
            'target_stats': {},
            'comparison': {},
            'discrepancies': []
        }

        # Get statistics from both systems
        recon['source_stats'] = self.source.get_daily_statistics(date)
        recon['target_stats'] = self.target.get_daily_statistics(date)

        # Compare key metrics
        recon['comparison'] = {
            'record_counts_match': (
                recon['source_stats']['total_records'] ==
                recon['target_stats']['total_records']
            ),
            'balances_match': (
                recon['source_stats']['total_balance'] ==
                recon['target_stats']['total_balance']
            ),
            'transactions_match': (
                recon['source_stats']['transaction_count'] ==
                recon['target_stats']['transaction_count']
            )
        }

        # Find specific discrepancies
        if not recon['comparison']['balances_match']:
            discrepancies = self.reconciliation.find_balance_discrepancies(
                date,
                recon['source_stats'],
                recon['target_stats']
            )
            recon['discrepancies'].extend(discrepancies)

        # Log to monitoring system
        self._log_reconciliation_results(recon)

        recon['end_time'] = datetime.now()
        return recon

    def _can_exit_parallel_mode(self, run_log: dict) -> bool:
        """Determine if parallel mode validation is complete"""

        # Require: 7 days with zero discrepancies
        recent_reconciliations = run_log['daily_reconciliations'][-7:]

        if len(recent_reconciliations) < 7:
            return False  # Not enough data

        for recon in recent_reconciliations:
            if recon['discrepancies']:
                return False  # Still finding discrepancies

            if not recon['comparison']['balances_match']:
                return False

        # All checks passed
        return True
```

---

## Reconciliation Strategies

### Comprehensive Reconciliation Framework

```python
class ReconciliationEngine:
    """Comprehensive post-migration reconciliation"""

    def __init__(self):
        self.source = SourceSystem()
        self.target = TargetSystem()
        self.discrepancies = []

    def perform_full_reconciliation(self) -> dict:
        """Perform complete data reconciliation"""

        reconciliation = {
            'start_time': datetime.now(),
            'reconciliations': [],
            'total_discrepancies': 0,
            'status': 'IN_PROGRESS'
        }

        # Reconcile each entity type
        entities = ['CUSTOMERS', 'ACCOUNTS', 'TRANSACTIONS', 'GL_ACCOUNTS']

        for entity in entities:
            entity_recon = self._reconcile_entity(entity)
            reconciliation['reconciliations'].append(entity_recon)
            reconciliation['total_discrepancies'] += len(entity_recon['discrepancies'])

        # Reconcile data relationships
        relationship_recon = self._reconcile_relationships()
        reconciliation['reconciliations'].append(relationship_recon)

        # Reconcile balances
        balance_recon = self._reconcile_balances()
        reconciliation['reconciliations'].append(balance_recon)

        reconciliation['end_time'] = datetime.now()

        if reconciliation['total_discrepancies'] == 0:
            reconciliation['status'] = 'SUCCESS'
        else:
            reconciliation['status'] = 'WARNINGS'

        return reconciliation

    def _reconcile_entity(self, entity: str) -> dict:
        """Reconcile single entity type"""

        recon = {
            'entity': entity,
            'source_count': 0,
            'target_count': 0,
            'discrepancies': [],
            'details': {}
        }

        # Count records
        recon['source_count'] = self.source.count_records(entity)
        recon['target_count'] = self.target.count_records(entity)

        if recon['source_count'] != recon['target_count']:
            recon['discrepancies'].append({
                'type': 'COUNT_MISMATCH',
                'source': recon['source_count'],
                'target': recon['target_count'],
                'difference': recon['source_count'] - recon['target_count']
            })

        # Find missing records
        missing_in_target = self._find_missing_records(entity, 'source')
        if missing_in_target:
            recon['discrepancies'].append({
                'type': 'MISSING_IN_TARGET',
                'count': len(missing_in_target),
                'examples': missing_in_target[:10]
            })

        # Find extra records
        extra_in_target = self._find_missing_records(entity, 'target')
        if extra_in_target:
            recon['discrepancies'].append({
                'type': 'EXTRA_IN_TARGET',
                'count': len(extra_in_target),
                'examples': extra_in_target[:10]
            })

        return recon

    def _reconcile_balances(self) -> dict:
        """Reconcile account balances"""

        recon = {
            'type': 'BALANCE_RECONCILIATION',
            'accounts_checked': 0,
            'accounts_balanced': 0,
            'discrepancies': [],
            'total_difference': Decimal(0)
        }

        # Get all accounts
        accounts = self.target.get_all_accounts()

        for account in accounts:
            recon['accounts_checked'] += 1

            # Get balance from both systems
            source_balance = self.source.get_account_balance(account['id'])
            target_balance = self.target.get_account_balance(account['id'])

            if source_balance == target_balance:
                recon['accounts_balanced'] += 1
            else:
                difference = abs(source_balance - target_balance)
                recon['total_difference'] += difference

                recon['discrepancies'].append({
                    'account_id': account['id'],
                    'source_balance': str(source_balance),
                    'target_balance': str(target_balance),
                    'difference': str(difference)
                })

        recon['balance_percentage'] = (
            recon['accounts_balanced'] / recon['accounts_checked'] * 100
        )

        return recon

    def _reconcile_relationships(self) -> dict:
        """Reconcile foreign key relationships"""

        recon = {
            'type': 'RELATIONSHIP_RECONCILIATION',
            'relationships_checked': 0,
            'relationships_valid': 0,
            'violations': []
        }

        # Check customer-account relationships
        accounts = self.target.get_all_accounts()

        for account in accounts:
            recon['relationships_checked'] += 1

            customer_exists = self.target.customer_exists(account['customer_id'])

            if customer_exists:
                recon['relationships_valid'] += 1
            else:
                recon['violations'].append({
                    'type': 'ORPHANED_ACCOUNT',
                    'account_id': account['id'],
                    'missing_customer': account['customer_id']
                })

        return recon

    def generate_reconciliation_report(self, reconciliation: dict) -> str:
        """Generate detailed reconciliation report"""

        report = "DATA MIGRATION RECONCILIATION REPORT\n"
        report += "=" * 80 + "\n\n"

        report += f"Reconciliation Period: {reconciliation['start_time']} to {reconciliation['end_time']}\n"
        report += f"Total Discrepancies Found: {reconciliation['total_discrepancies']}\n"
        report += f"Status: {reconciliation['status']}\n\n"

        for entity_recon in reconciliation['reconciliations']:
            report += f"\n{entity_recon.get('entity', entity_recon.get('type'))}\n"
            report += "-" * 40 + "\n"

            if 'source_count' in entity_recon:
                report += f"  Source Records: {entity_recon['source_count']:,}\n"
                report += f"  Target Records: {entity_recon['target_count']:,}\n"

            if entity_recon['discrepancies']:
                report += f"  Discrepancies:\n"
                for disc in entity_recon['discrepancies']:
                    report += f"    - {disc['type']}: {disc.get('count', 1)}\n"
            else:
                report += f"  Status: NO DISCREPANCIES\n"

        return report
```

---

## Risk Management

### Migration Risk Assessment

```python
class MigrationRiskManagement:
    """Identify and mitigate migration risks"""

    def assess_migration_risks(self) -> dict:
        """Comprehensive risk assessment"""

        risks = {
            'technical_risks': [],
            'operational_risks': [],
            'business_risks': [],
            'compliance_risks': [],
            'overall_risk_score': 0
        }

        # Identify technical risks
        risks['technical_risks'] = [
            {
                'risk': 'Data loss during transformation',
                'probability': 'MEDIUM',
                'impact': 'CRITICAL',
                'mitigation': [
                    'Test transformation logic with full data sets',
                    'Create detailed data backups',
                    'Implement validation at each step',
                    'Maintain rollback capability'
                ]
            },
            {
                'risk': 'Performance degradation',
                'probability': 'HIGH',
                'impact': 'HIGH',
                'mitigation': [
                    'Performance testing with production-like data volume',
                    'Index optimization on target system',
                    'Query optimization and tuning'
                ]
            },
            {
                'risk': 'Legacy system failure during migration',
                'probability': 'LOW',
                'impact': 'CRITICAL',
                'mitigation': [
                    'Maintenance window with reduced transactions',
                    'Backup legacy system to alternate hardware',
                    'Quick recovery procedures'
                ]
            }
        ]

        # Identify operational risks
        risks['operational_risks'] = [
            {
                'risk': 'Staff not trained on new system',
                'probability': 'MEDIUM',
                'impact': 'HIGH',
                'mitigation': [
                    'Comprehensive training program',
                    'Parallel run with both systems',
                    'Support desk preparation',
                    'Runbooks for common scenarios'
                ]
            },
            {
                'risk': 'Insufficient monitoring post-cutover',
                'probability': 'MEDIUM',
                'impact': 'HIGH',
                'mitigation': [
                    'Detailed monitoring dashboard',
                    'Alert thresholds for key metrics',
                    '24/7 support team for first week',
                    'Regular health checks'
                ]
            }
        ]

        # Identify business risks
        risks['business_risks'] = [
            {
                'risk': 'Customer-facing outages',
                'probability': 'MEDIUM',
                'impact': 'CRITICAL',
                'mitigation': [
                    'Phased migration approach',
                    'Extended cutover window',
                    'Communication plan for customers',
                    'Compensation plan if issues occur'
                ]
            },
            {
                'risk': 'Regulatory non-compliance after migration',
                'probability': 'LOW',
                'impact': 'CRITICAL',
                'mitigation': [
                    'Compliance team involvement throughout',
                    'Audit of migrated data',
                    'Regulatory reporting validation',
                    'Documentation of all changes'
                ]
            }
        ]

        risks['overall_risk_score'] = self._calculate_risk_score(risks)

        return risks

    def _calculate_risk_score(self, risks: dict) -> float:
        """Calculate overall migration risk score (0-100)"""

        probability_scores = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}
        impact_scores = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}

        total_score = 0
        total_risks = 0

        for risk_category in ['technical_risks', 'operational_risks', 'business_risks', 'compliance_risks']:
            for risk in risks[risk_category]:
                prob = probability_scores.get(risk['probability'], 0)
                impact = impact_scores.get(risk['impact'], 0)
                total_score += prob * impact
                total_risks += 1

        return (total_score / (total_risks * 12)) * 100 if total_risks > 0 else 0
```

---

## Real-World Case Studies

### Case Study 1: $250B Asset Bank's Mainframe to Cloud Migration

**Background**:
- 40 years of transaction history
- 5 million customer accounts
- 500 million+ daily transactions
- Mainframe-only system

**Approach**:
- Phased migration over 18 months
- 4 major phases by business line
- Parallel run for 30 days per phase

**Challenges**:
- Legacy data quality issues (2% of accounts had balance discrepancies)
- Complex interest calculation rules embedded in COBOL
- Regulatory audit requirements during migration

**Results**:
- 100% successful migration with zero data loss
- Final reconciliation: 99.98% accuracy (4 accounts required manual adjustment)
- 18-month timeline maintained
- $50M cost savings in operational expenses annually

### Case Study 2: Regional Bank's 90-Day Rapid Migration

**Background**:
- Legacy system end-of-life from vendor
- 60 days to switch
- Limited budget

**Approach**:
- Big bang migration with compressed timeline
- Heavy automation to reduce manual effort
- Weekend cutover with backup recovery plan

**Results**:
- Successful migration in 87 days
- 10 minor issues in first week (all resolved in <1 hour)
- Cost 40% less than phased approach
- Operational risk managed through excellent planning

---

## Post-Migration Validation

### Production Validation Checklist

```python
class PostMigrationValidation:
    """Comprehensive post-migration validation"""

    def create_validation_checklist(self) -> dict:
        """Create complete validation checklist"""

        checklist = {
            'data_completeness': [
                ('All customer records present', self._check_customer_completeness),
                ('All account records present', self._check_account_completeness),
                ('All transaction history present', self._check_transaction_completeness),
                ('All GL accounts present', self._check_gl_completeness)
            ],

            'data_accuracy': [
                ('Account balances reconcile', self._check_balance_reconciliation),
                ('Transaction amounts correct', self._check_transaction_amounts),
                ('Interest calculations correct', self._check_interest_calcs),
                ('Customer data matches source', self._check_customer_data)
            ],

            'system_functionality': [
                ('Deposits accepted', self._check_deposit_functionality),
                ('Withdrawals processed', self._check_withdrawal_functionality),
                ('Transfers working correctly', self._check_transfer_functionality),
                ('Reports generating correctly', self._check_report_generation)
            ],

            'performance': [
                ('Account lookup <100ms', self._check_lookup_performance),
                ('Transaction posting <500ms', self._check_posting_performance),
                ('Report generation <5min', self._check_report_performance),
                ('No query timeouts', self._check_timeout_rates)
            ],

            'compliance': [
                ('Audit trail complete', self._check_audit_trail),
                ('Encryption enabled', self._check_encryption),
                ('Access controls functioning', self._check_access_controls),
                ('Regulatory reports accurate', self._check_regulatory_reports)
            ]
        }

        return checklist

    def execute_full_validation(self) -> dict:
        """Execute all validation checks"""

        validation_results = {
            'start_time': datetime.now(),
            'checks': {},
            'total_passed': 0,
            'total_failed': 0,
            'summary': ''
        }

        checklist = self.create_validation_checklist()

        for category, checks in checklist.items():
            validation_results['checks'][category] = []

            for check_name, check_fn in checks:
                result = {
                    'check': check_name,
                    'passed': False,
                    'details': ''
                }

                try:
                    check_result = check_fn()
                    result['passed'] = check_result['success']
                    result['details'] = check_result.get('message', '')

                    if result['passed']:
                        validation_results['total_passed'] += 1
                    else:
                        validation_results['total_failed'] += 1

                except Exception as e:
                    result['passed'] = False
                    result['details'] = f"Error: {str(e)}"
                    validation_results['total_failed'] += 1

                validation_results['checks'][category].append(result)

        validation_results['end_time'] = datetime.now()

        # Generate summary
        total_checks = validation_results['total_passed'] + validation_results['total_failed']
        success_rate = (validation_results['total_passed'] / total_checks * 100) if total_checks > 0 else 0

        validation_results['summary'] = (
            f"{validation_results['total_passed']}/{total_checks} checks passed ({success_rate:.1f}%)"
        )

        return validation_results
```

---

## Conclusion

Successful data migration requires meticulous planning, execution, and validation. Key success factors:

1. **Comprehensive Planning**: Understand source data deeply before starting
2. **Quality Assurance**: Test transformation logic exhaustively
3. **Phased Approach**: Reduce risk through gradual migration
4. **Robust Validation**: Multiple reconciliation methods to catch issues
5. **Risk Management**: Prepare for failures with rollback plans
6. **Communication**: Keep stakeholders informed throughout process

The cost of data migration failures far exceeds investment in proper planning and validation.

# SOX Controls Testing Automation Guide

## Automating SOX 404 Compliance and Control Testing

### Overview
Automate SOX internal control testing to reduce manual effort, increase test coverage, and maintain continuous compliance monitoring.

### SOX Automation Opportunities

#### 1. Entity-Level Controls
**Automated Monitoring:**
- Code of Conduct attestations (track completion)
- Policy acknowledgments
- Training completion
- Whistleblower hotline metrics
- Board/committee meeting attendance

#### 2. Process-Level Controls
**Financial Controls:**
- Segregation of Duties (SoD) monitoring
- Authorization limit checks
- Journal entry reviews
- Account reconciliation completion
- Purchase order/invoice matching (3-way match)

**IT General Controls (ITGCs):**
- Access reviews (privileged users, terminated users)
- Change management tracking
- Backup completion monitoring
- Patch compliance
- Database change monitoring

#### 3. Automated Testing Scripts

**Access Control Testing:**
```python
# Test: Segregation of Duties - No user has both AP create and approve access
import pandas as pd

def test_sod_ap_segregation(user_access_report):
    """
    Control: Users cannot both create and approve payables
    """
    # Load user access data
    df = pd.read_csv(user_access_report)
    
    # Identify users with conflicting access
    sod_violations = df.groupby('user_id').agg({
        'AP_Create': 'max',
        'AP_Approve': 'max'
    })
    
    # Flag users with both permissions
    violations = sod_violations[(sod_violations['AP_Create'] == 1) & 
                                (sod_violations['AP_Approve'] == 1)]
    
    # Generate test results
    test_result = {
        'control_id': 'AC-001',
        'control_name': 'SoD - AP Creation and Approval',
        'test_date': datetime.now(),
        'population_size': len(df['user_id'].unique()),
        'exceptions': len(violations),
        'exception_rate': len(violations) / len(df['user_id'].unique()),
        'result': 'PASS' if len(violations) == 0 else 'FAIL',
        'exception_details': violations.to_dict('records')
    }
    
    return test_result
```

**Reconciliation Completeness:**
```sql
-- Test: All account reconciliations completed within 5 days of month-end
SELECT 
    account_number,
    account_name,
    period_end_date,
    reconciliation_completed_date,
    DATEDIFF(reconciliation_completed_date, period_end_date) as days_to_complete,
    reconciler_name
FROM account_reconciliations
WHERE period_end_date = '2024-01-31'
  AND (reconciliation_completed_date IS NULL 
       OR DATEDIFF(reconciliation_completed_date, period_end_date) > 5)
ORDER BY account_number;
```

**Authorization Limit Testing:**
```python
# Test: All transactions within authorized limits
def test_authorization_limits(transactions_df, approval_limits_df):
    """
    Control: Transactions exceed approver's authorized limit require escalation
    """
    # Merge transactions with approver limits
    merged = transactions_df.merge(
        approval_limits_df, 
        left_on='approved_by', 
        right_on='user_id'
    )
    
    # Identify transactions exceeding limits
    exceptions = merged[merged['transaction_amount'] > merged['approval_limit']]
    
    # Check if exceptions were escalated
    exceptions['properly_escalated'] = exceptions.apply(
        lambda row: row['escalated_to'] is not None and 
                   row['escalation_limit'] >= row['transaction_amount'],
        axis=1
    )
    
    failures = exceptions[~exceptions['properly_escalated']]
    
    return {
        'control_id': 'AUTH-002',
        'total_transactions': len(transactions_df),
        'over_limit': len(exceptions),
        'improperly_approved': len(failures),
        'result': 'PASS' if len(failures) == 0 else 'FAIL',
        'failure_details': failures[['transaction_id', 'amount', 'approver', 'limit']].to_dict('records')
    }
```

**Journal Entry Testing:**
```sql
-- Test: All manual journal entries have supporting documentation
SELECT 
    je.journal_entry_id,
    je.entry_date,
    je.prepared_by,
    je.approved_by,
    je.amount,
    je.description,
    CASE 
        WHEN d.document_id IS NULL THEN 'Missing Documentation'
        ELSE 'Documented'
    END as documentation_status
FROM journal_entries je
LEFT JOIN supporting_documents d ON je.journal_entry_id = d.journal_entry_id
WHERE je.entry_type = 'Manual'
  AND je.entry_date BETWEEN '2024-01-01' AND '2024-01-31'
  AND d.document_id IS NULL
ORDER BY je.amount DESC;
```

#### 4. Continuous Controls Monitoring (CCM)

**Implement Real-Time Monitoring:**
```python
# Continuous monitoring framework
class SOXControlMonitor:
    def __init__(self):
        self.controls = self.load_controls()
        
    def monitor_sod_violations(self):
        """Daily SoD monitoring"""
        violations = self.run_sod_tests()
        if violations:
            self.alert_compliance_team(violations)
            self.create_remediation_tickets(violations)
    
    def monitor_authorization_exceptions(self):
        """Real-time authorization monitoring"""
        # Query yesterday's transactions
        transactions = self.get_transactions(date=yesterday)
        exceptions = self.test_authorization_limits(transactions)
        
        if exceptions:
            self.log_exceptions(exceptions)
            self.notify_management(exceptions)
    
    def monitor_access_reviews(self):
        """Track access review completion"""
        overdue_reviews = self.get_overdue_access_reviews()
        if overdue_reviews:
            self.escalate_to_managers(overdue_reviews)
    
    def run_daily_monitoring(self):
        """Execute all daily controls"""
        self.monitor_sod_violations()
        self.monitor_authorization_exceptions()
        self.monitor_access_reviews()
        self.generate_daily_report()
```

#### 5. Evidence Collection Automation

**Automated Screenshot Capture:**
```python
from selenium import webdriver
from datetime import datetime

def capture_control_evidence(control_id, url, login_credentials):
    """
    Automate screenshot capture for control testing evidence
    """
    driver = webdriver.Chrome()
    
    try:
        # Login to application
        driver.get(url)
        driver.find_element_by_id('username').send_keys(login_credentials['user'])
        driver.find_element_by_id('password').send_keys(login_credentials['pass'])
        driver.find_element_by_id('login').click()
        
        # Navigate to control evidence page
        driver.get(f"{url}/reports/sod-violations")
        
        # Capture screenshot
        screenshot_path = f"evidence/{control_id}_{datetime.now().strftime('%Y%m%d')}.png"
        driver.save_screenshot(screenshot_path)
        
        # Store metadata
        evidence_metadata = {
            'control_id': control_id,
            'evidence_type': 'screenshot',
            'file_path': screenshot_path,
            'captured_by': 'automation',
            'capture_date': datetime.now(),
            'url': driver.current_url
        }
        
        return evidence_metadata
        
    finally:
        driver.quit()
```

**System Report Extraction:**
```python
def extract_sap_report(report_name, parameters):
    """
    Extract SAP report for SOX evidence
    """
    import pyrfc
    
    # Connect to SAP
    conn = pyrfc.Connection(
        ashost='sap.company.com',
        sysnr='00',
        client='100',
        user=sap_user,
        passwd=sap_pass
    )
    
    # Execute report
    result = conn.call('RFC_READ_REPORT', 
                      REPORT_NAME=report_name,
                      PARAMS=parameters)
    
    # Save report output
    report_file = f"evidence/{report_name}_{date.today()}.csv"
    pd.DataFrame(result['DATA']).to_csv(report_file)
    
    conn.close()
    
    return report_file
```

#### 6. Audit Management Integration

**Workflow Integration:**
- Test plan creation
- Sample selection
- Test execution documentation
- Exception tracking
- Remediation monitoring
- Final testing and sign-off

**Platform Integration:**
- AuditBoard
- HighBond
- Workiva
- TeamMate+

### Implementation Roadmap

**Phase 1: Assessment (Weeks 1-4)**
- Inventory all SOX controls
- Identify automation candidates
- Prioritize by risk and effort
- Select automation tools

**Phase 2: Pilot (Weeks 5-12)**
- Select 5-10 high-value controls
- Develop automated test scripts
- Validate against manual testing
- Refine and tune

**Phase 3: Expansion (Weeks 13-24)**
- Automate additional controls
- Integrate with audit management platform
- Deploy CCM for key controls
- Train audit team

**Phase 4: Optimization (Ongoing)**
- Monitor and refine tests
- Reduce false positives
- Expand automation coverage
- Continuous improvement

### Key Metrics
- % of controls with automated testing
- Manual testing hours saved
- Exception detection rate
- False positive rate
- Time from control failure to remediation
- Audit findings (should decrease)

### Best Practices
1. **Start with ITGCs:** Easier to automate than manual business controls
2. **Validate Automation:** Compare automated vs. manual results
3. **Document Test Logic:** Clear documentation of automated tests
4. **Version Control:** Maintain test script versions
5. **Exception Workflow:** Automated exception routing and tracking
6. **Evidence Repository:** Centralize all test evidence
7. **Audit Trail:** Log all automated test executions
8. **Collaborate with Auditors:** Get auditor buy-in for automation approach

---
*Guide for automating SOX 404 compliance and control testing*

# Fraud Investigation Guide

## Case Management Workflow

### Investigation Process

1. **Alert Received**
   - Fraud score triggers alert
   - Added to investigation queue
   - Priority assigned

2. **Triage**
   - Quick review
   - Obviously fraud: Fast-track block
   - Unclear: Full investigation

3. **Evidence Gathering**
   - Pull transaction details
   - Customer communication history
   - Device information
   - Network relationships
   - Supporting documentation

4. **Analysis**
   - Timeline reconstruction
   - Pattern identification
   - Comparative analysis
   - Hypothesis formation

5. **Decision Making**
   - Determine fraud/not fraud
   - Recommend action
   - Document reasoning

6. **Action Execution**
   - Block/allow transaction
   - Update customer profile
   - Adjust prevention rules

7. **Closure**
   - Document outcome
   - Provide feedback to model
   - Record learnings

## Investigation Case Management System

### Case Structure
```python
class FraudCase:
    def __init__(self, case_id, transaction_id, alert_data):
        self.case_id = case_id
        self.transaction_id = transaction_id
        self.status = 'open'  # open, pending, resolved
        self.priority = alert_data['priority']
        self.fraud_score = alert_data['fraud_score']

        # Investigation data
        self.evidence = {}
        self.notes = []
        self.decision = None
        self.recommended_action = None

        self.created_at = datetime.now()
        self.assigned_to = None
        self.resolved_at = None

    def add_evidence(self, evidence_type, data):
        """Add evidence to case"""
        if evidence_type not in self.evidence:
            self.evidence[evidence_type] = []

        self.evidence[evidence_type].append({
            'data': data,
            'added_at': datetime.now()
        })

    def add_note(self, note, investigator_id):
        """Add investigator note"""
        self.notes.append({
            'text': note,
            'added_by': investigator_id,
            'added_at': datetime.now()
        })

    def make_decision(self, decision, reasoning, investigator_id):
        """Record investigation decision"""
        self.decision = decision  # 'fraud', 'legitimate', 'inconclusive'
        self.reasoning = reasoning
        self.decided_by = investigator_id
        self.decided_at = datetime.now()
        self.status = 'resolved'

    def to_dict(self):
        """Serialize case"""
        return {
            'case_id': self.case_id,
            'transaction_id': self.transaction_id,
            'status': self.status,
            'priority': self.priority,
            'fraud_score': self.fraud_score,
            'evidence_count': sum(len(e) for e in self.evidence.values()),
            'notes_count': len(self.notes),
            'decision': self.decision,
            'created_at': self.created_at.isoformat(),
            'resolved_at': (self.resolved_at.isoformat() if self.resolved_at
                           else None)
        }
```

## Investigation Tools

### Transaction History Viewer
```python
class TransactionHistoryViewer:
    def __init__(self, transaction_db):
        self.db = transaction_db

    def get_customer_transaction_history(
        self,
        customer_id,
        days=30
    ):
        """Get customer transaction history"""
        transactions = self.db.get_transactions(
            customer_id,
            since=datetime.now() - timedelta(days=days)
        )

        # Organize by date
        by_date = defaultdict(list)
        for txn in transactions:
            date = txn['timestamp'].date()
            by_date[date].append(txn)

        # Analyze patterns
        analysis = {
            'total_transactions': len(transactions),
            'total_amount': sum(t['amount'] for t in transactions),
            'average_amount': np.mean([t['amount'] for t in transactions]),
            'merchants': set(t['merchant'] for t in transactions),
            'by_date': dict(by_date),
            'daily_average': len(transactions) / days
        }

        return analysis

    def get_anomalous_transactions(self, customer_id):
        """Identify potentially anomalous transactions"""
        history = self.get_customer_transaction_history(customer_id)

        anomalies = []
        avg_amount = history['average_amount']
        std_amount = np.std([
            t['amount'] for txn_list in history['by_date'].values()
            for t in txn_list
        ])

        # Find high-amount outliers
        for txn_list in history['by_date'].values():
            for txn in txn_list:
                z_score = abs(txn['amount'] - avg_amount) / std_amount

                if z_score > 2.5:  # 2.5 std devs
                    anomalies.append({
                        'type': 'high_amount',
                        'transaction': txn,
                        'z_score': z_score
                    })

        return anomalies
```

### Device & Network Analysis Tool
```python
class DeviceNetworkAnalyzer:
    def __init__(self, graph_db):
        self.graph = graph_db

    def get_device_network(self, device_id):
        """Get all entities connected to device"""
        customers = self.graph.get_customers_using_device(device_id)
        cards = self.graph.get_cards_using_device(device_id)
        ips = self.graph.get_ips_using_device(device_id)

        # Check for fraud connections
        fraud_customers = [
            c for c in customers if c['fraud_flag']
        ]

        return {
            'device_id': device_id,
            'customer_count': len(customers),
            'fraud_customers': len(fraud_customers),
            'card_count': len(cards),
            'ip_count': len(ips),
            'fraud_risk': 'high' if len(fraud_customers) > 2 else 'medium'
            if len(fraud_customers) > 0 else 'low'
        }

    def get_fraud_ring_analysis(self, customer_id):
        """Analyze if customer is part of fraud ring"""
        # Find all connected nodes
        neighbors = self.graph.get_connected_nodes(customer_id)

        # Check for fraud indicators
        fraud_connections = [
            n for n in neighbors if n['fraud_flag'] or n['fraud_score'] > 0.7
        ]

        # Calculate ring likelihood
        ring_likelihood = len(fraud_connections) / max(len(neighbors), 1)

        return {
            'customer_id': customer_id,
            'total_connections': len(neighbors),
            'fraud_connections': len(fraud_connections),
            'ring_likelihood': ring_likelihood,
            'is_fraud_ring': ring_likelihood > 0.3
        }
```

### Customer Communication Tool
```python
class CustomerCommunicationViewer:
    def __init__(self, communication_db):
        self.db = communication_db

    def get_customer_communications(self, customer_id):
        """Get all communications with customer"""
        emails = self.db.get_emails(customer_id)
        support_tickets = self.db.get_support_tickets(customer_id)
        chargebacks = self.db.get_chargebacks(customer_id)
        complaints = self.db.get_complaints(customer_id)

        return {
            'emails': emails,
            'support_tickets': support_tickets,
            'chargebacks': chargebacks,
            'complaints': complaints,
            'total_communications': (
                len(emails) + len(support_tickets) +
                len(chargebacks) + len(complaints)
            )
        }

    def analyze_customer_behavior(self, customer_id):
        """Analyze customer communication patterns"""
        comms = self.get_customer_communications(customer_id)

        # Check for dispute pattern
        dispute_rate = len(comms['chargebacks']) / max(
            self.db.get_transaction_count(customer_id), 1
        )

        # Check for complaint pattern
        complaint_count = len(comms['complaints'])

        return {
            'communication_count': comms['total_communications'],
            'dispute_rate': dispute_rate,
            'complaint_count': complaint_count,
            'is_problematic_customer': (
                dispute_rate > 0.1 or complaint_count > 5
            )
        }
```

## Investigation Decision Framework

### Evidence Grading System
```python
class EvidenceGrader:
    def grade_evidence(self, evidence_list):
        """Grade quality of evidence"""
        grades = {}

        for evidence in evidence_list:
            etype = evidence['type']
            data = evidence['data']

            if etype == 'transaction_details':
                grade = self._grade_transaction_details(data)
            elif etype == 'device':
                grade = self._grade_device_evidence(data)
            elif etype == 'network':
                grade = self._grade_network_evidence(data)
            elif etype == 'behavioral':
                grade = self._grade_behavioral_evidence(data)
            else:
                grade = 'D'  # Unknown

            grades[etype] = grade

        # Calculate overall grade
        grade_values = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'E': 0}
        overall = sum(
            grade_values.get(g, 0) for g in grades.values()
        ) / len(grades)

        return {
            'by_type': grades,
            'overall_grade': self._score_to_grade(overall)
        }

    def _score_to_grade(self, score):
        """Convert score to grade"""
        if score >= 3.5:
            return 'A'
        elif score >= 2.5:
            return 'B'
        elif score >= 1.5:
            return 'C'
        elif score >= 0.5:
            return 'D'
        else:
            return 'E'
```

## Investigation Quality Assurance

### QA Review Process
```python
class InvestigationQA:
    def review_case(self, case):
        """QA review of investigation"""
        issues = []

        # Check evidence sufficiency
        if len(case.evidence) < 2:
            issues.append('Insufficient evidence types')

        # Check decision justification
        if not case.reasoning or len(case.reasoning) < 50:
            issues.append('Insufficient decision reasoning')

        # Check documentation quality
        if len(case.notes) < 2:
            issues.append('Inadequate case notes')

        # Check timeline consistency
        transactions = case.evidence.get('transactions', [])
        if transactions and not self._check_timeline_consistency(
            transactions
        ):
            issues.append('Timeline inconsistencies detected')

        # Calculate quality score
        quality_score = max(0, 100 - (len(issues) * 20))

        return {
            'issues': issues,
            'quality_score': quality_score,
            'approved': quality_score >= 70
        }
```

## Best Practices for Investigators

1. **Thorough Documentation**: Record all findings
2. **Objective Analysis**: Follow evidence, avoid assumptions
3. **Efficient Time Management**: Focus high-value cases
4. **Customer Respect**: Professional communication
5. **Continuous Learning**: Study fraud patterns
6. **Compliance**: Follow procedures
7. **Collaboration**: Share knowledge with team

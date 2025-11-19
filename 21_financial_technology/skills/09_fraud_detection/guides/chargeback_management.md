# Chargeback Management Guide

## Chargeback Prevention Strategy

### Layered Prevention Approach
```
1. Prevent Fraud (upstream)
   - Block fraudulent transactions
   - Reduce fraud chargebacks

2. Prevent Friendly Fraud (communication)
   - Clear descriptions
   - Good customer service
   - Easy refund process

3. Prevent Procedural Errors (operations)
   - Proper authorization
   - Correct descriptors
   - Complete documentation

4. Prevent Unrecoverable Cases (recovery)
   - Quick representment
   - Strong evidence
   - Professional process
```

## Prevention Implementation

### Fraud Prevention Impact
```python
class ChargebackPrevention:
    def calculate_chargeback_prevention_impact(self):
        """Calculate fraud prevention impact on chargebacks"""
        # Fraud chargebacks (preventable)
        fraud_transactions = 1000
        fraud_prevention_rate = 0.95
        fraud_chargebacks = fraud_transactions * (1 - fraud_prevention_rate)
        fraud_savings = fraud_chargebacks * 150  # $150 per chargeback

        # Friendly fraud chargebacks (preventable via communication)
        friendly_transactions = 500
        communication_effectiveness = 0.20  # 20% reduction
        friendly_chargebacks_prevented = friendly_transactions * communication_effectiveness
        friendly_savings = friendly_chargebacks_prevented * 150

        total_savings = fraud_savings + friendly_savings

        print(f"Fraud prevention savings: ${fraud_savings:,.0f}")
        print(f"Communication savings: ${friendly_savings:,.0f}")
        print(f"Total chargeback prevention savings: ${total_savings:,.0f}")
```

### Documentation Quality
```python
class DocumentationManager:
    def collect_transaction_documentation(self, transaction_id):
        """Collect all documentation for transaction"""
        doc = {
            'transaction_id': transaction_id,
            'authorization': self._get_authorization_proof(transaction_id),
            'delivery': self._get_delivery_proof(transaction_id),
            'customer_communication': (
                self._get_customer_communication(transaction_id)
            ),
            'refund_status': self._get_refund_status(transaction_id),
            'item_details': self._get_item_details(transaction_id),
            'quality_score': 0
        }

        # Score documentation quality
        doc['quality_score'] = self._score_documentation(doc)

        return doc

    def _get_authorization_proof(self, transaction_id):
        """Get authorization evidence"""
        auth = self.db.get_authorization(transaction_id)

        return {
            'avs_match': auth.get('avs_match', False),
            'cvv_match': auth.get('cvv_match', False),
            '3ds_authenticated': auth.get('3ds_result') == 'Y',
            'ip_match': auth.get('ip_match', False)
        }

    def _get_delivery_proof(self, transaction_id):
        """Get delivery evidence"""
        shipment = self.db.get_shipment(transaction_id)

        if not shipment:
            return {'status': 'no_delivery'}

        return {
            'carrier': shipment['carrier'],
            'tracking_number': shipment['tracking_number'],
            'delivery_date': shipment['delivery_date'].isoformat(),
            'signature_required': shipment['signature_required'],
            'signature_proof': shipment['signature_proof'],
            'delivery_address_match': (
                shipment['delivery_address'] ==
                shipment['billing_address']
            )
        }

    def _score_documentation(self, doc):
        """Score documentation quality"""
        score = 0

        # Authorization
        auth = doc['authorization']
        if auth.get('avs_match'):
            score += 10
        if auth.get('cvv_match'):
            score += 10
        if auth.get('3ds_authenticated'):
            score += 20

        # Delivery
        delivery = doc['delivery']
        if delivery.get('tracking_number'):
            score += 15
        if delivery.get('signature_proof'):
            score += 20
        if delivery.get('delivery_date'):
            score += 10

        # Customer communication
        if doc['customer_communication']:
            score += 15

        return min(score, 100)
```

## Chargeback Management Workflow

### Case Management
```python
class ChargebackCase:
    def __init__(self, chargeback_id, transaction_id):
        self.chargeback_id = chargeback_id
        self.transaction_id = transaction_id
        self.status = 'received'  # received, researching, representment_filed, appealing, closed
        self.reason_code = None
        self.amount = 0
        self.received_date = datetime.now()
        self.deadline = None
        self.documentation = {}
        self.representment_strength = 'unknown'

    def file_representment(self, evidence):
        """File chargeback representment"""
        # Assemble package
        package = {
            'chargeback_id': self.chargeback_id,
            'evidence': evidence,
            'filed_date': datetime.now(),
            'filing_deadline': self.deadline
        }

        # Submit to network
        result = self.submit_to_network(package)

        self.status = 'representment_filed'

        return result

    def submit_to_network(self, package):
        """Submit representment to payment network"""
        # Validate completeness
        if not self._is_package_complete(package):
            return {'status': 'incomplete', 'message': 'Missing required documents'}

        # Assess strength
        strength = self._assess_representment_strength(package)

        # Submit (Visa, Mastercard, Discover, Amex)
        network = self._get_network()
        response = network.submit_representment(package)

        return {
            'status': 'submitted',
            'network': network,
            'strength': strength,
            'reference_number': response['reference_number']
        }

    def _is_package_complete(self, package):
        """Check if representment package is complete"""
        required_docs = {
            'invoice': False,
            'customer_email': False,
            'delivery_proof': False,
            'authorization_proof': False
        }

        for doc_type in required_docs:
            if doc_type in package['evidence']:
                required_docs[doc_type] = True

        # At least 3 of 4 required
        return sum(required_docs.values()) >= 3

    def _assess_representment_strength(self, package):
        """Assess likelihood of representment success"""
        evidence = package['evidence']
        score = 0

        # Delivery proof (strongest)
        if 'delivery_proof' in evidence:
            if evidence['delivery_proof'].get('signature_proof'):
                score += 40
            else:
                score += 20

        # Authorization proof
        if 'authorization_proof' in evidence:
            if evidence['authorization_proof'].get('3ds_authenticated'):
                score += 20
            else:
                score += 10

        # Customer communication
        if 'customer_communication' in evidence:
            score += 15

        # Refund status
        if 'refund_issued' not in evidence or not evidence['refund_issued']:
            score += 10

        # Determine strength level
        if score >= 70:
            return 'strong'
        elif score >= 50:
            return 'moderate'
        else:
            return 'weak'
```

## Monitoring Chargeback Metrics

### Dashboard Metrics
```python
class ChargebackDashboard:
    def get_key_metrics(self, period_days=30):
        """Get key chargeback metrics"""
        start_date = datetime.now() - timedelta(days=period_days)

        chargebacks = self.db.get_chargebacks(since=start_date)
        transactions = self.db.get_transaction_count(since=start_date)

        # Calculate metrics
        metrics = {
            'chargeback_count': len(chargebacks),
            'chargeback_rate': len(chargebacks) / max(transactions, 1),
            'total_amount': sum(c['amount'] for c in chargebacks),
            'average_amount': np.mean([c['amount'] for c in chargebacks]),

            # By reason code
            'by_reason': self._breakdown_by_reason(chargebacks),

            # By status
            'by_status': self._breakdown_by_status(chargebacks),

            # Representment performance
            'representment_rate': self._calculate_representment_rate(
                chargebacks
            ),
            'win_rate': self._calculate_win_rate(chargebacks),

            # Network compliance
            'network_status': self._get_network_compliance_status()
        }

        return metrics

    def _calculate_representment_rate(self, chargebacks):
        """% of chargebacks that were representmented"""
        representmented = sum(
            1 for c in chargebacks
            if c['status'] in ['representment_filed', 'appealing', 'closed']
        )

        return representmented / len(chargebacks) if chargebacks else 0

    def _calculate_win_rate(self, chargebacks):
        """% of chargebacks won through representment"""
        won = sum(
            1 for c in chargebacks
            if c['status'] == 'closed' and c['result'] == 'merchant_win'
        )

        total_resolved = sum(
            1 for c in chargebacks
            if c['status'] == 'closed'
        )

        return won / total_resolved if total_resolved > 0 else 0
```

## Chargeback Analytics

### Root Cause Analysis
```python
def analyze_chargeback_causes(chargebacks):
    """Analyze root causes of chargebacks"""
    causes = defaultdict(int)

    for chargeback in chargebacks:
        reason = chargeback['reason_code']

        # Map reason code to probable cause
        if reason in ['4855', '7030']:
            causes['non_delivery'] += 1
        elif reason in ['4856', '4857']:
            causes['not_as_described'] += 1
        elif reason in ['4855', '4863']:
            causes['unauthorized'] += 1
        elif reason in ['4834']:
            causes['processing_error'] += 1

    total = sum(causes.values())

    return {
        'causes': dict(causes),
        'top_cause': max(causes, key=causes.get),
        'top_cause_percent': max(causes.values()) / total if total > 0 else 0
    }
```

## Prevention Strategy

### Merchant Recommendations
```
1. Clear Product Descriptions
   - Detailed product info
   - Accurate photos
   - Clear specifications

2. Transparent Billing
   - Descriptive merchant name
   - Clear amounts
   - Itemized charges

3. Proactive Communication
   - Order confirmation
   - Shipping notification
   - Delivery notification
   - Follow-up contact

4. Easy Returns
   - Clear return policy
   - Easy return process
   - Quick refunds
   - Prepaid return labels

5. Problem Resolution
   - Responsive customer service
   - Quick issue resolution
   - Refund option before chargeback

6. Record Keeping
   - Keep delivery proof
   - Archive communications
   - Maintain authorization records
   - Document refunds
```

## Integration with Fraud Detection

### Cross-Reporting
```python
def report_chargeback_to_fraud_system(chargeback):
    """Use chargeback data to improve fraud detection"""
    # Extract learnings
    if chargeback['result'] == 'merchant_loss':
        # Fraud that should have been caught
        record_fraud_miss(chargeback)

        # Update fraud model
        update_fraud_prevention_rules(chargeback)

    elif chargeback['result'] == 'merchant_win':
        # Friendly fraud that was defended
        record_friendly_fraud_pattern(chargeback)

        # Strengthen prevention for similar cases
        strengthen_communication_rules(chargeback)

    return {'status': 'processed'}
```

## Best Practices

1. **Prevention First**: Prevent chargebacks before they happen
2. **Quick Response**: File representments quickly
3. **Strong Evidence**: Collect comprehensive documentation
4. **Customer Service**: Resolve issues before chargebacks
5. **Compliance**: Stay under network thresholds
6. **Monitoring**: Track metrics continuously
7. **Learning**: Use chargebacks to improve prevention

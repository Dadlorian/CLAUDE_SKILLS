# Saga Pattern for Distributed Financial Transactions

## Table of Contents
1. [Overview](#overview)
2. [Saga Types](#saga-types)
3. [Choreography Pattern](#choreography-pattern)
4. [Orchestration Pattern](#orchestration-pattern)
5. [Compensating Transactions](#compensating-transactions)
6. [Real-World Scenarios](#real-world-scenarios)
7. [Implementation Patterns](#implementation-patterns)
8. [Failure Handling](#failure-handling)

## Overview

A saga is a sequence of local transactions that work together to accomplish a distributed business transaction. Sagas are critical for fintech because they handle multi-step operations that must be atomic across multiple independent systems.

### Why Sagas for Finance?

1. **Distributed Transactions**: Handle multi-system operations
2. **Atomicity Without Locks**: Achieve ACID-like guarantees without distributed locks
3. **Failure Recovery**: Compensating transactions to undo partial changes
4. **Compliance**: Maintain audit trail of all steps
5. **Scalability**: Work across microservices and independent systems

### Simple Example: Fund Transfer

```
Traditional (Single Database):
┌─────────────┐
│ Source Acct │ -$100
│ Target Acct │ +$100
│ (Atomic)    │
└─────────────┘

Saga (Distributed):
┌──────────────┐  ┌──────────────┐
│ Account Svc  │  │ Ledger Svc   │
├──────────────┤  ├──────────────┤
│ Source: -$100│  │ Record -$100 │
│ Target: +$100│  │ Record +$100 │
└──────────────┘  └──────────────┘

If Ledger fails:
- Undo Account changes (compensating transaction)
- Return funds to source
- Notify user of failure
```

## Saga Types

### 1. Choreography Pattern

Services directly communicate with each other through events:

```
┌──────────────────────────────────────────────────────────────┐
│                     Transfer: $100                            │
│                   Account A → Account B                       │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Account Service     │
        │  Withdraw from A     │
        │  Emit: Withdrawn     │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Notification        │
        │  Send confirmation   │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Ledger Service      │
        │  Record transaction  │
        │  Emit: Recorded      │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Account Service     │
        │  Deposit to B        │
        │  Emit: Deposited     │
        └──────────────────────┘
```

**Advantages**:
- Decoupled services
- Simple to understand
- No central coordinator

**Disadvantages**:
- Complex state tracking
- Hard to debug
- Circular dependencies possible

**Code Example**:

```python
from dataclasses import dataclass
from enum import Enum
import asyncio
from typing import Callable

class TransferEvent(Enum):
    TRANSFER_INITIATED = "transfer.initiated"
    WITHDRAWAL_COMPLETED = "withdrawal.completed"
    WITHDRAWAL_FAILED = "withdrawal.failed"
    DEPOSIT_COMPLETED = "deposit.completed"
    DEPOSIT_FAILED = "deposit.failed"
    TRANSFER_COMPLETED = "transfer.completed"
    TRANSFER_FAILED = "transfer.failed"

@dataclass
class TransferSaga:
    transfer_id: str
    source_account: str
    target_account: str
    amount: float
    status: str = "initiated"

class AccountServiceChoreography:
    """Account service in choreography saga"""

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.sagas = {}
        self.event_bus.subscribe(
            TransferEvent.TRANSFER_INITIATED,
            self.handle_transfer_initiated
        )
        self.event_bus.subscribe(
            TransferEvent.DEPOSIT_COMPLETED,
            self.handle_deposit_completed
        )

    async def handle_transfer_initiated(self, event):
        """Handle transfer initiation"""
        saga = TransferSaga(
            transfer_id=event['transfer_id'],
            source_account=event['source_account'],
            target_account=event['target_account'],
            amount=event['amount']
        )

        self.sagas[saga.transfer_id] = saga

        try:
            # Step 1: Withdraw from source
            success = await self._withdraw(saga.source_account, saga.amount)

            if success:
                saga.status = "withdrawal_completed"
                await self.event_bus.publish({
                    'type': TransferEvent.WITHDRAWAL_COMPLETED,
                    'transfer_id': saga.transfer_id,
                    'amount': saga.amount
                })
            else:
                saga.status = "withdrawal_failed"
                await self.event_bus.publish({
                    'type': TransferEvent.WITHDRAWAL_FAILED,
                    'transfer_id': saga.transfer_id
                })

        except Exception as e:
            saga.status = "failed"
            await self.event_bus.publish({
                'type': TransferEvent.TRANSFER_FAILED,
                'transfer_id': saga.transfer_id,
                'error': str(e)
            })

    async def handle_deposit_completed(self, event):
        """Handle deposit completion"""
        saga = self.sagas.get(event['transfer_id'])
        if not saga:
            return

        saga.status = "transfer_completed"
        await self.event_bus.publish({
            'type': TransferEvent.TRANSFER_COMPLETED,
            'transfer_id': saga.transfer_id
        })

    async def _withdraw(self, account_id: str, amount: float) -> bool:
        """Withdraw from account"""
        # Actual implementation
        return True

class NotificationServiceChoreography:
    """Notification service listening to events"""

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.event_bus.subscribe(
            TransferEvent.WITHDRAWAL_COMPLETED,
            self.handle_withdrawal
        )
        self.event_bus.subscribe(
            TransferEvent.TRANSFER_FAILED,
            self.handle_failure
        )

    async def handle_withdrawal(self, event):
        """Send confirmation after withdrawal"""
        await self._send_notification(
            f"Withdrawal of ${event['amount']} initiated"
        )

    async def handle_failure(self, event):
        """Send failure notification"""
        await self._send_notification(
            f"Transfer failed: {event.get('error', 'Unknown error')}"
        )

    async def _send_notification(self, message: str):
        # Send email/SMS
        print(f"Notification: {message}")

class LedgerServiceChoreography:
    """Ledger service recording transactions"""

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.event_bus.subscribe(
            TransferEvent.WITHDRAWAL_COMPLETED,
            self.handle_withdrawal
        )

    async def handle_withdrawal(self, event):
        """Record withdrawal in ledger"""
        await self._record_transaction(
            amount=event['amount'],
            type='withdrawal',
            transfer_id=event['transfer_id']
        )

        # Emit deposit signal to other account service
        await self.event_bus.publish({
            'type': 'deposit.initiated',
            'transfer_id': event['transfer_id'],
            'amount': event['amount']
        })

    async def _record_transaction(self, amount: float, type: str, transfer_id: str):
        # Record in ledger
        print(f"Ledger: Recorded {type} of ${amount} for {transfer_id}")
```

### 2. Orchestration Pattern

A central orchestrator controls the saga steps:

```
┌────────────────────────────────────────┐
│      Transfer Saga Orchestrator        │
│  Maintains state and coordinates       │
└────────────────┬───────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌──────────┐
│ Account │  │ Ledger  │  │Notify    │
│ Service │  │ Service │  │Service   │
└─────────┘  └─────────┘  └──────────┘

Orchestrator controls sequence:
1. Call Account → Withdraw
2. Wait for response
3. Call Ledger → Record
4. Wait for response
5. Call Account → Deposit
6. If any fails → Execute compensating txns
```

**Advantages**:
- Clear flow and state management
- Easier to debug
- Transaction order guaranteed
- Better error handling

**Disadvantages**:
- Central orchestrator is bottleneck
- Single point of failure
- More complex implementation

**Code Example**:

```python
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
import asyncio

class SagaStep(Enum):
    INITIATED = "initiated"
    WITHDRAWAL_PENDING = "withdrawal_pending"
    WITHDRAWAL_COMPLETED = "withdrawal_completed"
    LEDGER_PENDING = "ledger_pending"
    LEDGER_RECORDED = "ledger_recorded"
    DEPOSIT_PENDING = "deposit_pending"
    DEPOSIT_COMPLETED = "deposit_completed"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"

class SagaStep:
    """Single step in saga"""

    def __init__(self, step_id: str, action: str, service: str,
                 params: Dict, compensate_params: Dict = None):
        self.step_id = step_id
        self.action = action
        self.service = service
        self.params = params
        self.compensate_params = compensate_params or {}
        self.status = "pending"
        self.result = None
        self.error = None

class TransferSagaOrchestrator:
    """Orchestrates distributed transfer saga"""

    def __init__(self, services: Dict):
        self.services = services
        self.sagas: Dict[str, List[SagaStep]] = {}
        self.saga_states: Dict[str, str] = {}

    async def start_transfer(self, transfer_id: str,
                            source_account: str,
                            target_account: str,
                            amount: float) -> bool:
        """Orchestrate transfer saga"""

        # Define saga steps
        steps = [
            SagaStep(
                step_id="withdraw",
                action="withdraw",
                service="account",
                params={
                    'account_id': source_account,
                    'amount': amount,
                    'transfer_id': transfer_id
                },
                compensate_params={
                    'account_id': source_account,
                    'amount': amount,
                    'reason': 'Transfer failed - returning funds'
                }
            ),
            SagaStep(
                step_id="record_ledger",
                action="record_transaction",
                service="ledger",
                params={
                    'transfer_id': transfer_id,
                    'source': source_account,
                    'target': target_account,
                    'amount': amount,
                    'type': 'transfer'
                },
                compensate_params={
                    'transfer_id': transfer_id,
                    'reason': 'Transfer failed - reversing ledger entry'
                }
            ),
            SagaStep(
                step_id="deposit",
                action="deposit",
                service="account",
                params={
                    'account_id': target_account,
                    'amount': amount,
                    'transfer_id': transfer_id
                },
                compensate_params={
                    'account_id': target_account,
                    'amount': amount,
                    'reason': 'Transfer failed - removing deposit'
                }
            ),
            SagaStep(
                step_id="notify",
                action="send_notification",
                service="notification",
                params={
                    'transfer_id': transfer_id,
                    'status': 'completed',
                    'amount': amount
                }
            )
        ]

        self.sagas[transfer_id] = steps
        self.saga_states[transfer_id] = "initiated"

        try:
            # Execute each step
            for i, step in enumerate(steps):
                try:
                    result = await self._execute_step(step)

                    if not result['success']:
                        self.saga_states[transfer_id] = "failed"

                        # Compensate: undo previous steps in reverse order
                        await self._compensate(transfer_id, steps[:i])
                        return False

                    step.status = "completed"
                    step.result = result

                except Exception as e:
                    self.saga_states[transfer_id] = "failed"
                    step.status = "failed"
                    step.error = str(e)

                    # Compensate previous steps
                    await self._compensate(transfer_id, steps[:i])
                    return False

            self.saga_states[transfer_id] = "completed"
            return True

        except Exception as e:
            self.saga_states[transfer_id] = "failed"
            raise

    async def _execute_step(self, step: SagaStep) -> Dict:
        """Execute single saga step"""
        service = self.services.get(step.service)

        if not service:
            raise Exception(f"Service not found: {step.service}")

        method = getattr(service, step.action, None)
        if not method:
            raise Exception(f"Action not found: {step.action}")

        result = await method(**step.params)
        return result

    async def _compensate(self, transfer_id: str, completed_steps: List[SagaStep]):
        """Execute compensating transactions in reverse order"""
        self.saga_states[transfer_id] = "compensating"

        # Reverse order
        for step in reversed(completed_steps):
            try:
                await self._execute_step(step)
                print(f"Compensated: {step.step_id}")
            except Exception as e:
                # Log error but continue with other compensations
                print(f"Compensation failed for {step.step_id}: {e}")

        self.saga_states[transfer_id] = "failed"

    def get_saga_status(self, transfer_id: str) -> Dict:
        """Get status of saga"""
        return {
            'transfer_id': transfer_id,
            'status': self.saga_states.get(transfer_id),
            'steps': [
                {
                    'step_id': s.step_id,
                    'status': s.status,
                    'result': s.result,
                    'error': s.error
                }
                for s in self.sagas.get(transfer_id, [])
            ]
        }
```

## Compensating Transactions

### Compensation Strategies

```python
class CompensationStrategy:
    """Different strategies for compensating failed transactions"""

    @staticmethod
    async def refund_immediately(account_id: str, amount: float):
        """Immediately refund to source account"""
        return await AccountService.deposit(
            account_id=account_id,
            amount=amount,
            reason="Refund due to failed transfer"
        )

    @staticmethod
    async def create_credit(account_id: str, amount: float):
        """Create account credit for customer"""
        return await AccountService.add_credit(
            account_id=account_id,
            amount=amount,
            reason="Credit for failed transfer"
        )

    @staticmethod
    async def manual_reconciliation(transfer_id: str, amount: float):
        """Mark for manual reconciliation"""
        return await ReconciliationService.create_record(
            transfer_id=transfer_id,
            amount=amount,
            type="failed_transfer",
            status="pending_manual"
        )

class CompensationHandler:
    """Handle compensation for failed sagas"""

    def __init__(self, strategies: Dict):
        self.strategies = strategies

    async def compensate_failed_transfer(self, transfer: Dict) -> bool:
        """Compensate failed transfer based on rules"""

        amount = transfer['amount']
        source = transfer['source_account']
        target = transfer['target_account']
        failed_step = transfer['failed_at']

        if failed_step == 'withdrawal':
            # Withdrawal never happened, no compensation needed
            return True

        elif failed_step == 'ledger':
            # Need to reverse the withdrawal
            return await self.strategies['refund_immediately'](source, amount)

        elif failed_step == 'deposit':
            # Withdrawal succeeded but deposit failed
            # Withdraw from target and refund source
            await self.strategies['refund_immediately'](source, amount)
            await self.strategies['refund_immediately'](target, amount)
            return True

        return False
```

## Real-World Scenarios

### Scenario 1: Payment Splitting (Uber-style)

Passenger pays $30:
- $24 to driver (80%)
- $6 to platform (20%)

```python
class PaymentSplittingSaga:
    """Saga for splitting payments (Stripe Connect pattern)"""

    async def process_split_payment(self, payment: Dict,
                                   orchestrator: TransferSagaOrchestrator):
        """Process payment with splits"""

        # Charge customer
        total_amount = payment['amount']

        # Create transfer saga with multiple legs
        steps = [
            SagaStep(
                step_id="charge_customer",
                action="charge",
                service="payment",
                params={'customer_id': payment['customer'], 'amount': total_amount}
            ),
            SagaStep(
                step_id="pay_driver",
                action="transfer",
                service="transfer",
                params={
                    'destination': payment['driver'],
                    'amount': total_amount * 0.8  # 80%
                }
            ),
            SagaStep(
                step_id="platform_revenue",
                action="deposit",
                service="account",
                params={
                    'account_id': 'platform',
                    'amount': total_amount * 0.2  # 20%
                }
            ),
            SagaStep(
                step_id="record_split",
                action="record",
                service="ledger",
                params={'payment_id': payment['id'], 'splits': payment['splits']}
            )
        ]

        return steps
```

### Scenario 2: Cross-Border Transfer (Bank-to-Bank)

```python
class CrossBorderSaga:
    """Saga for complex cross-border transfers"""

    async def process_cross_border_transfer(self, transfer: Dict,
                                          orchestrator: TransferSagaOrchestrator):
        """Handle forex and international bank transfers"""

        steps = [
            # Validate compliance
            SagaStep(
                step_id="compliance_check",
                action="verify_destination",
                service="compliance",
                params={'recipient_id': transfer['recipient'], 'amount': transfer['amount']}
            ),
            # Debit source account
            SagaStep(
                step_id="debit_source",
                action="debit",
                service="account",
                params={'account_id': transfer['source'], 'amount': transfer['amount']}
            ),
            # Convert currency if needed
            SagaStep(
                step_id="exchange",
                action="exchange",
                service="forex",
                params={
                    'amount': transfer['amount'],
                    'from_currency': transfer['source_currency'],
                    'to_currency': transfer['target_currency']
                }
            ),
            # Initiate SWIFT transfer
            SagaStep(
                step_id="swift_transfer",
                action="initiate_transfer",
                service="swift",
                params={
                    'amount': transfer['converted_amount'],
                    'destination': transfer['recipient_bank'],
                    'swift_code': transfer['swift_code']
                }
            ),
            # Record in ledger
            SagaStep(
                step_id="record_ledger",
                action="record_international",
                service="ledger",
                params={'transfer_id': transfer['id'], 'type': 'international'}
            ),
            # Notify
            SagaStep(
                step_id="notify",
                action="send_notification",
                service="notification",
                params={'transfer_id': transfer['id']}
            )
        ]

        return steps
```

## Implementation Patterns

### Saga State Machine

```python
from enum import Enum
import json
from typing import Optional

class SagaState(Enum):
    INITIATED = "initiated"
    PENDING = "pending"
    COMPENSATING = "compensating"
    COMPLETED = "completed"
    FAILED = "failed"

class SagaStateMachine:
    """State machine for saga execution"""

    def __init__(self, database):
        self.db = database
        self._initialize_schema()

    def _initialize_schema(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS saga_executions (
                saga_id TEXT PRIMARY KEY,
                saga_type TEXT NOT NULL,
                state TEXT NOT NULL,
                steps JSONB NOT NULL,
                data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            );

            CREATE INDEX idx_saga_type ON saga_executions(saga_type);
            CREATE INDEX idx_state ON saga_executions(state);
        ''')

    def save_saga(self, saga_id: str, saga_type: str, state: SagaState,
                  steps: List[SagaStep], data: Dict):
        """Save saga state"""
        self.db.execute('''
            INSERT INTO saga_executions (saga_id, saga_type, state, steps, data)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (saga_id) DO UPDATE SET
                state = EXCLUDED.state,
                steps = EXCLUDED.steps,
                updated_at = CURRENT_TIMESTAMP
        ''', (
            saga_id,
            saga_type,
            state.value,
            json.dumps([self._step_to_dict(s) for s in steps]),
            json.dumps(data)
        ))

    def get_saga(self, saga_id: str) -> Optional[Dict]:
        """Get saga execution details"""
        result = self.db.query('''
            SELECT * FROM saga_executions
            WHERE saga_id = %s
        ''', (saga_id,))

        return result[0] if result else None

    def _step_to_dict(self, step: SagaStep) -> Dict:
        return {
            'step_id': step.step_id,
            'action': step.action,
            'service': step.service,
            'status': step.status,
            'result': step.result,
            'error': step.error
        }
```

## Failure Handling

### Timeout Handling

```python
class TimeoutHandler:
    """Handle saga timeouts"""

    def __init__(self, timeout_seconds: int = 300):
        self.timeout_seconds = timeout_seconds

    async def monitor_saga(self, saga_id: str, orchestrator: TransferSagaOrchestrator):
        """Monitor saga for timeout"""
        start_time = asyncio.get_event_loop().time()

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time

            if elapsed > self.timeout_seconds:
                # Saga timeout - initiate compensation
                saga_status = orchestrator.get_saga_status(saga_id)

                if saga_status['status'] != 'completed':
                    # Force compensation
                    completed_steps = [
                        s for s in saga_status['steps']
                        if s['status'] == 'completed'
                    ]

                    await orchestrator._compensate(saga_id, completed_steps)
                break

            await asyncio.sleep(1)

            # Check if saga completed
            saga_status = orchestrator.get_saga_status(saga_id)
            if saga_status['status'] in ['completed', 'failed']:
                break
```

### Idempotency in Sagas

```python
class IdempotentSagaOrchestrator:
    """Ensure saga steps are idempotent"""

    async def execute_idempotent_step(self, step: SagaStep,
                                     idempotency_key: str) -> Dict:
        """Execute step with idempotency"""

        # Check if already executed
        cache_key = f"saga_step:{idempotency_key}:{step.step_id}"
        cached_result = self.cache.get(cache_key)

        if cached_result:
            return cached_result

        # Execute step
        result = await self._execute_step(step)

        # Cache result
        self.cache.set(cache_key, result, ttl=86400)  # 24 hours

        return result
```

## Conclusion

The Saga pattern provides:

1. **Orchestration**: Central control for complex flows
2. **Choreography**: Decoupled, event-driven approach
3. **Compensation**: Undo failed steps systematically
4. **Distributed Transactions**: ACID-like guarantees across services
5. **Error Recovery**: Automatic or manual compensation strategies

Choose orchestration for financial transactions (better control) and choreography for event streams.

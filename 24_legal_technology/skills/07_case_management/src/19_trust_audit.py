"""
Trust Audit - Practice Management Automation

Manages trust account reconciliation, identifies discrepancies,
and ensures compliance with bar association trust account rules.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from decimal import Decimal
from enum import Enum


class TransactionType(Enum):
    """Types of trust account transactions"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    INTEREST = "interest"
    FEE_DEDUCTION = "fee_deduction"
    REFUND = "refund"


class AuditStatus(Enum):
    """Status of trust account audit"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    PASSED = "passed"
    FAILED = "failed"


@dataclass
class TrustTransaction:
    """Trust account transaction"""
    transaction_id: str
    matter_id: str
    transaction_type: TransactionType
    amount: Decimal
    date: datetime
    description: str
    reference_number: str = ""
    posted_date: Optional[datetime] = None
    reconciled: bool = False
    notes: str = ""


@dataclass
class ClientTrustBalance:
    """Trust account balance for a client"""
    client_id: str
    client_name: str
    balance: Decimal
    last_transaction_date: datetime
    transactions: List[TrustTransaction] = field(default_factory=list)
    disputed_amount: Decimal = Decimal(0)


@dataclass
class TrustAuditFinding:
    """Finding from trust account audit"""
    finding_id: str
    audit_id: str
    finding_type: str  # "reconciliation_issue", "compliance_violation", "discrepancy"
    severity: str  # "low", "medium", "high"
    description: str
    amount: Decimal = Decimal(0)
    matter_id: Optional[str] = None
    recommendation: str = ""
    status: str = "open"


@dataclass
class TrustAudit:
    """Represents a trust account audit"""
    audit_id: str
    audit_date: datetime
    period_start: datetime
    period_end: datetime
    status: AuditStatus = AuditStatus.PENDING
    total_balance: Decimal = Decimal(0)
    reconciled_balance: Decimal = Decimal(0)
    discrepancies: List[TrustAuditFinding] = field(default_factory=list)
    findings: List[TrustAuditFinding] = field(default_factory=list)
    auditor: str = ""
    notes: str = ""


class TrustAuditManager:
    """Manages trust account audits and compliance"""

    def __init__(self):
        self.transactions: List[TrustTransaction] = []
        self.client_balances: Dict[str, ClientTrustBalance] = {}
        self.audits: Dict[str, TrustAudit] = {}
        self.audit_trail: List[Dict] = []

    def record_transaction(self, transaction: TrustTransaction) -> None:
        """Record a trust account transaction"""
        self.transactions.append(transaction)

        # Update client balance
        if transaction.matter_id not in self.client_balances:
            self.client_balances[transaction.matter_id] = ClientTrustBalance(
                client_id="",
                client_name="",
                balance=Decimal(0),
                last_transaction_date=transaction.date
            )

        balance = self.client_balances[transaction.matter_id]
        if transaction.transaction_type == TransactionType.DEPOSIT:
            balance.balance += transaction.amount
        elif transaction.transaction_type == TransactionType.WITHDRAWAL:
            balance.balance -= transaction.amount

        balance.transactions.append(transaction)
        balance.last_transaction_date = transaction.date

        # Log to audit trail
        self.audit_trail.append({
            "timestamp": datetime.now(),
            "transaction_id": transaction.transaction_id,
            "type": "transaction_recorded",
            "amount": str(transaction.amount)
        })

    def get_client_balance(self, client_id: str) -> Decimal:
        """Get current trust balance for a client"""
        if client_id not in self.client_balances:
            return Decimal(0)
        return self.client_balances[client_id].balance

    def get_total_trust_balance(self) -> Decimal:
        """Get total trust account balance across all clients"""
        return sum(balance.balance for balance in self.client_balances.values())

    def initiate_audit(self, audit_date: datetime, period_start: datetime, period_end: datetime) -> str:
        """Initiate a trust account audit"""
        audit_id = f"AUDIT-{audit_date.strftime('%Y%m%d%H%M%S')}"
        audit = TrustAudit(
            audit_id=audit_id,
            audit_date=audit_date,
            period_start=period_start,
            period_end=period_end,
            status=AuditStatus.PENDING
        )

        self.audits[audit_id] = audit
        return audit_id

    def perform_reconciliation(self, audit_id: str, bank_statement_balance: Decimal) -> Tuple[bool, List[str]]:
        """Perform reconciliation of trust account"""
        if audit_id not in self.audits:
            return False, ["Audit not found"]

        audit = self.audits[audit_id]
        audit.status = AuditStatus.IN_PROGRESS

        # Calculate book balance
        book_balance = Decimal(0)
        for balance in self.client_balances.values():
            book_balance += balance.balance

        audit.total_balance = book_balance
        audit.reconciled_balance = bank_statement_balance

        discrepancies = []

        # Check for outstanding items
        unreconciled_transactions = [
            t for t in self.transactions
            if audit.period_start <= t.date <= audit.period_end and not t.reconciled
        ]

        if book_balance != bank_statement_balance:
            difference = abs(book_balance - bank_statement_balance)

            finding = TrustAuditFinding(
                finding_id=f"{audit_id}-DISC-1",
                audit_id=audit_id,
                finding_type="reconciliation_issue",
                severity="high",
                description=f"Book balance ({book_balance}) does not match bank statement balance ({bank_statement_balance})",
                amount=difference,
                recommendation="Investigate outstanding checks, deposits in transit, and bank fees"
            )
            audit.discrepancies.append(finding)
            discrepancies.append(f"Balance discrepancy of ${difference}")

        # Mark transactions as reconciled
        for transaction in unreconciled_transactions:
            transaction.reconciled = True
            transaction.posted_date = datetime.now()

        return len(discrepancies) == 0, discrepancies

    def identify_compliance_issues(self, audit_id: str) -> List[TrustAuditFinding]:
        """Identify compliance issues in trust account"""
        if audit_id not in self.audits:
            return []

        audit = self.audits[audit_id]
        audit.status = AuditStatus.REVIEW
        issues = []

        # Check for negative balances
        for client_id, balance in self.client_balances.items():
            if balance.balance < 0:
                finding = TrustAuditFinding(
                    finding_id=f"{audit_id}-COMP-{len(issues)+1}",
                    audit_id=audit_id,
                    finding_type="compliance_violation",
                    severity="high",
                    description=f"Client {client_id} has negative trust balance: ${balance.balance}",
                    amount=abs(balance.balance),
                    matter_id=client_id,
                    recommendation="Immediately deposit funds to cover negative balance"
                )
                issues.append(finding)
                audit.findings.append(finding)

        # Check for stale funds (no transactions in 6+ months)
        cutoff_date = datetime.now() - \
            __import__('datetime').timedelta(days=180)
        for client_id, balance in self.client_balances.items():
            if balance.last_transaction_date < cutoff_date and balance.balance > 0:
                finding = TrustAuditFinding(
                    finding_id=f"{audit_id}-COMP-{len(issues)+1}",
                    audit_id=audit_id,
                    finding_type="compliance_violation",
                    severity="medium",
                    description=f"Stale funds in trust account for client {client_id}: ${balance.balance}",
                    amount=balance.balance,
                    matter_id=client_id,
                    recommendation="Contact client about stale funds; consider escheat if unclaimed"
                )
                issues.append(finding)
                audit.findings.append(finding)

        return issues

    def generate_audit_report(self, audit_id: str) -> Dict:
        """Generate comprehensive audit report"""
        if audit_id not in self.audits:
            return {}

        audit = self.audits[audit_id]
        audit.status = AuditStatus.PASSED if len(audit.discrepancies) == 0 and len(audit.findings) == 0 else AuditStatus.FAILED

        report = {
            "audit_id": audit_id,
            "audit_date": audit.audit_date.isoformat(),
            "period": f"{audit.period_start.isoformat()} to {audit.period_end.isoformat()}",
            "status": audit.status.value,
            "total_clients": len(self.client_balances),
            "total_trust_balance": str(audit.total_balance),
            "bank_reconciliation": {
                "book_balance": str(audit.total_balance),
                "bank_balance": str(audit.reconciled_balance),
                "difference": str(abs(audit.total_balance - audit.reconciled_balance))
            },
            "discrepancies": len(audit.discrepancies),
            "compliance_issues": len(audit.findings),
            "reconciliation_status": "PASSED" if audit.total_balance == audit.reconciled_balance else "FAILED"
        }

        return report

    def get_client_trust_statement(self, client_id: str) -> Dict:
        """Generate trust account statement for client"""
        if client_id not in self.client_balances:
            return {}

        balance = self.client_balances[client_id]
        transactions = sorted(balance.transactions, key=lambda x: x.date)

        return {
            "client_id": client_id,
            "client_name": balance.client_name,
            "current_balance": str(balance.balance),
            "statement_date": datetime.now().isoformat(),
            "transactions": [
                {
                    "date": t.date.isoformat(),
                    "type": t.transaction_type.value,
                    "amount": str(t.amount),
                    "description": t.description,
                    "reference": t.reference_number
                } for t in transactions
            ]
        }

    def export_audit_findings(self, audit_id: str) -> str:
        """Export audit findings as formatted text"""
        if audit_id not in self.audits:
            return ""

        audit = self.audits[audit_id]
        report = []

        report.append(f"TRUST ACCOUNT AUDIT REPORT\nAudit ID: {audit.audit_id}")
        report.append(f"Audit Date: {audit.audit_date.strftime('%B %d, %Y')}")
        report.append(f"Period: {audit.period_start.strftime('%B %d, %Y')} to {audit.period_end.strftime('%B %d, %Y')}")
        report.append(f"Status: {audit.status.value.upper()}\n")

        if audit.discrepancies:
            report.append("RECONCILIATION DISCREPANCIES:")
            for finding in audit.discrepancies:
                report.append(f"  - {finding.description}")
                report.append(f"    Amount: ${finding.amount}")
                report.append(f"    Recommendation: {finding.recommendation}\n")

        if audit.findings:
            report.append("COMPLIANCE FINDINGS:")
            for finding in audit.findings:
                report.append(f"  - {finding.description}")
                report.append(f"    Severity: {finding.severity}")
                report.append(f"    Recommendation: {finding.recommendation}\n")

        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    manager = TrustAuditManager()

    # Record transactions
    transaction1 = TrustTransaction(
        transaction_id="TXN-001",
        matter_id="MAT-2024-001",
        transaction_type=TransactionType.DEPOSIT,
        amount=Decimal(5000),
        date=datetime.now(),
        description="Client retainer deposit"
    )
    manager.record_transaction(transaction1)

    # Initiate audit
    audit_id = manager.initiate_audit(
        datetime.now(),
        datetime(2024, 1, 1),
        datetime(2024, 12, 31)
    )

    # Perform reconciliation
    reconciled, discrepancies = manager.perform_reconciliation(audit_id, Decimal(5000))
    print(f"Reconciliation successful: {reconciled}")

    # Generate report
    report = manager.generate_audit_report(audit_id)
    print(f"Audit Report: {report}")

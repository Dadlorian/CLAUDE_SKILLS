"""
Trust Reconciliation - Client Trust Account Management
Reconciles client trust account deposits, withdrawals, and balances
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from decimal import Decimal


class TransactionType(Enum):
    """Trust account transaction types"""
    DEPOSIT = "Deposit"
    WITHDRAWAL = "Withdrawal"
    TRANSFER_IN = "Transfer In"
    TRANSFER_OUT = "Transfer Out"
    FEE_DEDUCTION = "Fee Deduction"
    REFUND = "Refund"
    INTEREST = "Interest"
    RETURNED_CHECK = "Returned Check"


class ReconciliationStatus(Enum):
    """Reconciliation status"""
    BALANCED = "Balanced"
    UNBALANCED = "Unbalanced"
    PENDING = "Pending"
    ADJUSTMENT_NEEDED = "Adjustment Needed"


class TrustReconciliation:
    """Manage and reconcile client trust accounts"""

    def __init__(self, api_key: str, base_url: str = "https://api.clio.com/v4.0"):
        """
        Initialize trust reconciliation

        Args:
            api_key: Clio API key
            base_url: API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str,
                     params: Optional[Dict] = None,
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise

    def record_trust_deposit(self, matter_id: str,
                            client_id: str,
                            amount: Decimal,
                            description: str,
                            reference_number: str = "",
                            deposit_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Record client trust deposit

        Args:
            matter_id: Matter ID
            client_id: Client ID
            amount: Deposit amount
            description: Deposit description
            reference_number: Check/wire reference
            deposit_date: Date of deposit

        Returns:
            Transaction record
        """
        deposit_date = deposit_date or datetime.now()

        transaction = {
            "matter_id": matter_id,
            "client_id": client_id,
            "transaction_type": TransactionType.DEPOSIT.value,
            "amount": float(amount),
            "description": description,
            "reference_number": reference_number,
            "transaction_date": deposit_date.isoformat(),
            "recorded_date": datetime.now().isoformat(),
            "status": "Cleared"
        }

        return self._make_request("POST", "/trust_transactions", data=transaction)

    def record_trust_withdrawal(self, matter_id: str,
                               client_id: str,
                               amount: Decimal,
                               description: str,
                               invoice_id: str = "",
                               withdrawal_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Record trust account withdrawal (for fees/costs)

        Args:
            matter_id: Matter ID
            client_id: Client ID
            amount: Withdrawal amount
            description: Description of withdrawal
            invoice_id: Related invoice ID
            withdrawal_date: Date of withdrawal

        Returns:
            Transaction record
        """
        withdrawal_date = withdrawal_date or datetime.now()

        # Get current balance to check for sufficient funds
        balance = self.get_client_trust_balance(client_id)

        if balance < float(amount):
            raise ValueError(
                f"Insufficient trust balance. Balance: ${balance}, Requested: ${amount}"
            )

        transaction = {
            "matter_id": matter_id,
            "client_id": client_id,
            "transaction_type": TransactionType.WITHDRAWAL.value,
            "amount": float(amount),
            "description": description,
            "invoice_id": invoice_id,
            "transaction_date": withdrawal_date.isoformat(),
            "recorded_date": datetime.now().isoformat(),
            "status": "Cleared"
        }

        return self._make_request("POST", "/trust_transactions", data=transaction)

    def get_client_trust_balance(self, client_id: str) -> float:
        """
        Get current trust account balance for client

        Args:
            client_id: Client ID

        Returns:
            Current balance
        """
        response = self._make_request(
            "GET",
            f"/trust_accounts/{client_id}/balance"
        )

        return response.get("balance", 0.0)

    def get_trust_transactions(self, client_id: str,
                              matter_id: Optional[str] = None,
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get trust transactions for client

        Args:
            client_id: Client ID
            matter_id: Optional matter filter
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            List of transactions
        """
        params = {"client_id": client_id, "limit": 500}

        if matter_id:
            params["matter_id"] = matter_id
        if start_date:
            params["date__gte"] = start_date.isoformat()
        if end_date:
            params["date__lte"] = end_date.isoformat()

        response = self._make_request("GET", "/trust_transactions", params=params)
        return response.get("data", [])

    def reconcile_trust_account(self, client_id: str,
                               reconciliation_date: datetime,
                               bank_balance: float,
                               reconciliation_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Reconcile trust account against bank statement

        Args:
            client_id: Client ID
            reconciliation_date: Reconciliation date
            bank_balance: Bank statement balance
            reconciliation_items: List of reconciling items

        Returns:
            Reconciliation report
        """
        # Get system balance
        system_transactions = self.get_trust_transactions(client_id)
        system_balance = self.get_client_trust_balance(client_id)

        # Identify outstanding items
        outstanding_items = []
        reconciled_balance = bank_balance

        for item in reconciliation_items:
            item_type = item.get("type")  # Outstanding check, deposit in transit, etc.
            item_amount = float(item.get("amount", 0))

            if item_type == "outstanding_check" or item_type == "withdrawal_pending":
                reconciled_balance += item_amount
            elif item_type == "deposit_in_transit":
                reconciled_balance -= item_amount

            outstanding_items.append({
                "type": item_type,
                "amount": item_amount,
                "description": item.get("description", "")
            })

        # Determine status
        difference = abs(system_balance - reconciled_balance)
        status = ReconciliationStatus.BALANCED.value if difference < 0.01 else ReconciliationStatus.UNBALANCED.value

        reconciliation = {
            "client_id": client_id,
            "reconciliation_date": reconciliation_date.isoformat(),
            "bank_statement_balance": bank_balance,
            "system_balance": system_balance,
            "reconciled_balance": reconciled_balance,
            "difference": round(difference, 2),
            "status": status,
            "outstanding_items": outstanding_items,
            "reconciliation_completed": status == ReconciliationStatus.BALANCED.value,
            "transactions_reviewed": len(system_transactions)
        }

        # Save reconciliation record
        self._make_request("POST", "/reconciliations", data=reconciliation)

        return reconciliation

    def monthly_trust_reconciliation(self, reconciliation_month: datetime) -> Dict[str, Any]:
        """
        Perform monthly trust account reconciliation for all clients

        Args:
            reconciliation_month: Month to reconcile

        Returns:
            Monthly reconciliation summary
        """
        # Get all clients with trust accounts
        clients_response = self._make_request(
            "GET",
            "/contacts",
            params={"has_trust_account": True, "limit": 500}
        )

        clients = clients_response.get("data", [])

        month_start = reconciliation_month.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        reconciliations = []
        total_balance = 0
        discrepancies = []

        for client in clients:
            try:
                # Get bank statement (would integrate with bank API)
                bank_balance = self._get_bank_statement_balance(
                    client.get("id"),
                    month_end
                )

                # Get outstanding items for month
                outstanding = self._get_outstanding_items(
                    client.get("id"),
                    month_end
                )

                # Reconcile
                recon = self.reconcile_trust_account(
                    client.get("id"),
                    month_end,
                    bank_balance,
                    outstanding
                )

                reconciliations.append(recon)
                total_balance += recon.get("system_balance", 0)

                if recon.get("status") != ReconciliationStatus.BALANCED.value:
                    discrepancies.append({
                        "client_id": client.get("id"),
                        "client_name": f"{client.get('first_name', '')} {client.get('last_name', '')}",
                        "difference": recon.get("difference", 0),
                        "status": recon.get("status")
                    })

            except Exception as e:
                print(f"Error reconciling client {client.get('id')}: {e}")

        return {
            "reconciliation_month": reconciliation_month.strftime("%Y-%m"),
            "month_start": month_start.isoformat(),
            "month_end": month_end.isoformat(),
            "clients_reconciled": len(reconciliations),
            "total_trust_balance": round(total_balance, 2),
            "balanced_accounts": sum(
                1 for r in reconciliations
                if r.get("status") == ReconciliationStatus.BALANCED.value
            ),
            "discrepancies": discrepancies,
            "discrepancy_count": len(discrepancies),
            "all_reconciled": len(discrepancies) == 0
        }

    def _get_bank_statement_balance(self, client_id: str,
                                   as_of_date: datetime) -> float:
        """Get bank statement balance for client"""
        # Integration point for bank API
        try:
            response = self._make_request(
                "GET",
                f"/trust_accounts/{client_id}/bank_statement",
                params={"as_of_date": as_of_date.isoformat()}
            )
            return response.get("balance", 0.0)
        except:
            return 0.0

    def _get_outstanding_items(self, client_id: str,
                               as_of_date: datetime) -> List[Dict[str, Any]]:
        """Get outstanding checks and pending deposits"""
        items = []

        try:
            response = self._make_request(
                "GET",
                f"/trust_accounts/{client_id}/outstanding_items",
                params={"as_of_date": as_of_date.isoformat()}
            )

            items = response.get("items", [])
        except:
            pass

        return items

    def transfer_trust_to_operating(self, client_id: str,
                                    amount: Decimal,
                                    description: str) -> Dict[str, Any]:
        """
        Transfer earned fees from trust to operating account

        Args:
            client_id: Client ID
            amount: Amount to transfer
            description: Description of transfer

        Returns:
            Transfer record
        """
        # Record as withdrawal from trust
        trust_withdrawal = self.record_trust_withdrawal(
            "",  # No specific matter
            client_id,
            amount,
            f"Transfer to operating: {description}",
            withdrawal_date=datetime.now()
        )

        # Record as credit to operating account
        operating_transaction = {
            "client_id": client_id,
            "transaction_type": "Operating Account Credit",
            "amount": float(amount),
            "description": description,
            "source": "Trust Account Transfer",
            "transaction_date": datetime.now().isoformat(),
            "related_trust_transaction": trust_withdrawal.get("id")
        }

        self._make_request(
            "POST",
            "/operating_transactions",
            data=operating_transaction
        )

        return {
            "client_id": client_id,
            "amount_transferred": float(amount),
            "from_account": "Trust",
            "to_account": "Operating",
            "transfer_date": datetime.now().isoformat(),
            "description": description,
            "status": "Completed"
        }

    def generate_trust_report(self, as_of_date: datetime) -> Dict[str, Any]:
        """
        Generate firm-wide trust account report

        Args:
            as_of_date: Report as of date

        Returns:
            Trust account report
        """
        # Get all clients with trust accounts
        clients_response = self._make_request(
            "GET",
            "/contacts",
            params={"has_trust_account": True, "limit": 500}
        )

        clients = clients_response.get("data", [])

        trust_accounts = []
        total_trust_balance = 0

        for client in clients:
            balance = self.get_client_trust_balance(client.get("id"))
            total_trust_balance += balance

            trust_accounts.append({
                "client_id": client.get("id"),
                "client_name": f"{client.get('first_name', '')} {client.get('last_name', '')}",
                "balance": round(balance, 2)
            })

        # Sort by balance descending
        trust_accounts.sort(key=lambda x: x["balance"], reverse=True)

        return {
            "report_date": as_of_date.isoformat(),
            "total_clients": len(trust_accounts),
            "total_trust_balance": round(total_trust_balance, 2),
            "trust_accounts": trust_accounts,
            "average_balance": round(total_trust_balance / len(trust_accounts), 2) if trust_accounts else 0,
            "largest_account": trust_accounts[0] if trust_accounts else None,
            "smallest_account": trust_accounts[-1] if trust_accounts else None
        }


# Example usage
if __name__ == "__main__":
    reconciler = TrustReconciliation(api_key="your_clio_api_key")

    # Record a trust deposit
    # deposit = reconciler.record_trust_deposit(
    #     "matter_123",
    #     "client_456",
    #     Decimal("5000.00"),
    #     "Retainer deposit",
    #     "Check #1234"
    # )

    # Check balance
    # balance = reconciler.get_client_trust_balance("client_456")
    # print(f"Trust balance: ${balance}")

    # Monthly reconciliation
    # monthly = reconciler.monthly_trust_reconciliation(datetime.now())
    # print(f"Reconciled: {monthly['all_reconciled']}")

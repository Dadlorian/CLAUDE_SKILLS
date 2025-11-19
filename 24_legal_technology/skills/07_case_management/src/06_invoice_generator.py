"""
Invoice Generator - Automated Legal Invoice Creation and Management
Generates invoices from time entries, expenses, and costs
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from decimal import Decimal


class InvoiceStatus(Enum):
    """Invoice status"""
    DRAFT = "Draft"
    SENT = "Sent"
    OVERDUE = "Overdue"
    PAID = "Paid"
    CANCELLED = "Cancelled"


class BillingMethod(Enum):
    """Billing methods"""
    HOURLY = "Hourly"
    FLAT_FEE = "Flat Fee"
    CONTINGENCY = "Contingency"
    RETAINER = "Retainer"
    HYBRID = "Hybrid"


class InvoiceGenerator:
    """Generate and manage legal invoices"""

    def __init__(self, api_key: str, base_url: str = "https://api.clio.com/v4.0"):
        """
        Initialize invoice generator

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

    def generate_hourly_invoice(self, matter_id: str,
                               start_date: datetime,
                               end_date: datetime,
                               include_expenses: bool = True) -> Dict[str, Any]:
        """
        Generate hourly billing invoice

        Args:
            matter_id: Matter ID
            start_date: Billing period start
            end_date: Billing period end
            include_expenses: Include expense line items

        Returns:
            Invoice data
        """
        # Get matter details
        matter = self._make_request("GET", f"/matters/{matter_id}")
        client_id = matter.get("client", {}).get("id")
        client = self._make_request("GET", f"/contacts/{client_id}")

        # Get time entries for period
        time_entries = self._get_time_entries(matter_id, start_date, end_date)

        # Group by attorney and activity
        line_items = self._generate_time_line_items(time_entries)

        # Get expenses if requested
        expenses = []
        expenses_total = 0
        if include_expenses:
            expenses = self._get_expenses(matter_id, start_date, end_date)
            expenses_line_items = self._generate_expense_line_items(expenses)
            line_items.extend(expenses_line_items)
            expenses_total = sum(e.get("amount", 0) for e in expenses)

        # Calculate totals
        time_total = sum(item.get("amount", 0) for item in line_items if item.get("type") == "time")
        subtotal = time_total + expenses_total
        tax = self._calculate_tax(subtotal)
        total = subtotal + tax

        invoice = {
            "matter_id": matter_id,
            "client_id": client_id,
            "client_name": f"{client.get('first_name', '')} {client.get('last_name', '')}",
            "billing_period_start": start_date.isoformat(),
            "billing_period_end": end_date.isoformat(),
            "invoice_date": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "invoice_number": self._generate_invoice_number(),
            "billing_method": BillingMethod.HOURLY.value,
            "line_items": line_items,
            "subtotal": round(time_total, 2),
            "expenses_total": round(expenses_total, 2),
            "subtotal_with_expenses": round(subtotal, 2),
            "tax_amount": round(tax, 2),
            "total_amount": round(total, 2),
            "status": InvoiceStatus.DRAFT.value,
            "payment_terms": "Net 30"
        }

        return invoice

    def _get_time_entries(self, matter_id: str,
                         start_date: datetime,
                         end_date: datetime) -> List[Dict[str, Any]]:
        """Get time entries for period"""
        params = {
            "matter__id": matter_id,
            "date__gte": start_date.isoformat(),
            "date__lte": end_date.isoformat(),
            "status": "Approved",
            "limit": 500
        }

        response = self._make_request("GET", "/time_entries", params=params)
        return response.get("data", [])

    def _generate_time_line_items(self, time_entries: List[Dict]) -> List[Dict[str, Any]]:
        """Generate line items from time entries"""
        line_items = []

        # Group by attorney
        by_attorney = {}
        for entry in time_entries:
            attorney = entry.get("user", {}).get("id")
            if attorney not in by_attorney:
                by_attorney[attorney] = {
                    "hours": 0,
                    "rate": entry.get("billing_rate", 150.0),
                    "attorney_name": entry.get("user", {}).get("name", "Unknown")
                }
            by_attorney[attorney]["hours"] += entry.get("duration", 0)

        # Create line items
        for attorney_id, data in by_attorney.items():
            hours = round(data["hours"], 2)
            rate = data["rate"]
            amount = hours * rate

            line_items.append({
                "type": "time",
                "description": f"Professional services - {data['attorney_name']}",
                "attorney": attorney_id,
                "hours": hours,
                "rate": rate,
                "amount": amount,
                "entry_count": len([e for e in time_entries if e.get("user", {}).get("id") == attorney_id])
            })

        return line_items

    def _get_expenses(self, matter_id: str,
                     start_date: datetime,
                     end_date: datetime) -> List[Dict[str, Any]]:
        """Get expenses for period"""
        params = {
            "matter__id": matter_id,
            "date__gte": start_date.isoformat(),
            "date__lte": end_date.isoformat(),
            "limit": 500
        }

        response = self._make_request("GET", "/expenses", params=params)
        return response.get("data", [])

    def _generate_expense_line_items(self, expenses: List[Dict]) -> List[Dict[str, Any]]:
        """Generate line items from expenses"""
        line_items = []

        for expense in expenses:
            line_items.append({
                "type": "expense",
                "description": expense.get("description", "Expense"),
                "category": expense.get("category"),
                "amount": expense.get("amount", 0),
                "expense_date": expense.get("date"),
                "vendor": expense.get("vendor")
            })

        return line_items

    def _calculate_tax(self, subtotal: float, tax_rate: float = 0.0) -> float:
        """Calculate tax on subtotal"""
        return subtotal * tax_rate

    def _generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"INV-{timestamp}"

    def create_flat_fee_invoice(self, matter_id: str,
                               flat_fee: float,
                               description: str = "Professional services") -> Dict[str, Any]:
        """
        Create flat fee invoice

        Args:
            matter_id: Matter ID
            flat_fee: Flat fee amount
            description: Invoice description

        Returns:
            Invoice data
        """
        matter = self._make_request("GET", f"/matters/{matter_id}")
        client_id = matter.get("client", {}).get("id")
        client = self._make_request("GET", f"/contacts/{client_id}")

        tax = self._calculate_tax(flat_fee)

        invoice = {
            "matter_id": matter_id,
            "client_id": client_id,
            "client_name": f"{client.get('first_name', '')} {client.get('last_name', '')}",
            "invoice_date": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "invoice_number": self._generate_invoice_number(),
            "billing_method": BillingMethod.FLAT_FEE.value,
            "line_items": [{
                "type": "flat_fee",
                "description": description,
                "amount": flat_fee
            }],
            "subtotal": flat_fee,
            "tax_amount": tax,
            "total_amount": flat_fee + tax,
            "status": InvoiceStatus.DRAFT.value,
            "payment_terms": "Net 30"
        }

        return invoice

    def create_retainer_invoice(self, matter_id: str,
                               retainer_amount: float,
                               description: str = "Retainer deposit") -> Dict[str, Any]:
        """
        Create retainer invoice

        Args:
            matter_id: Matter ID
            retainer_amount: Retainer amount
            description: Retainer description

        Returns:
            Invoice data
        """
        matter = self._make_request("GET", f"/matters/{matter_id}")
        client_id = matter.get("client", {}).get("id")
        client = self._make_request("GET", f"/contacts/{client_id}")

        invoice = {
            "matter_id": matter_id,
            "client_id": client_id,
            "client_name": f"{client.get('first_name', '')} {client.get('last_name', '')}",
            "invoice_date": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=14)).isoformat(),
            "invoice_number": self._generate_invoice_number(),
            "billing_method": BillingMethod.RETAINER.value,
            "line_items": [{
                "type": "retainer",
                "description": description,
                "amount": retainer_amount
            }],
            "subtotal": retainer_amount,
            "tax_amount": 0,
            "total_amount": retainer_amount,
            "status": InvoiceStatus.DRAFT.value,
            "payment_terms": "Due upon receipt"
        }

        return invoice

    def save_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save invoice to system

        Args:
            invoice_data: Invoice data to save

        Returns:
            Saved invoice record
        """
        return self._make_request("POST", "/invoices", data=invoice_data)

    def send_invoice(self, invoice_id: str,
                    recipient_email: str,
                    message: str = "") -> Dict[str, Any]:
        """
        Send invoice to client

        Args:
            invoice_id: Invoice ID
            recipient_email: Client email
            message: Optional message

        Returns:
            Send confirmation
        """
        invoice_data = self._make_request("GET", f"/invoices/{invoice_id}")

        # Update invoice status
        self._make_request(
            "PUT",
            f"/invoices/{invoice_id}",
            data={
                "status": InvoiceStatus.SENT.value,
                "sent_date": datetime.now().isoformat()
            }
        )

        # Send email (integration point)
        send_result = {
            "invoice_id": invoice_id,
            "recipient": recipient_email,
            "sent_date": datetime.now().isoformat(),
            "status": "Sent",
            "amount": invoice_data.get("total_amount"),
            "due_date": invoice_data.get("due_date")
        }

        return send_result

    def record_payment(self, invoice_id: str,
                      amount: float,
                      payment_date: Optional[datetime] = None,
                      payment_method: str = "Check") -> Dict[str, Any]:
        """
        Record payment on invoice

        Args:
            invoice_id: Invoice ID
            amount: Payment amount
            payment_date: Payment date
            payment_method: Method of payment

        Returns:
            Updated invoice
        """
        payment_date = payment_date or datetime.now()

        payment = {
            "invoice_id": invoice_id,
            "amount": amount,
            "payment_date": payment_date.isoformat(),
            "payment_method": payment_method,
            "recorded_date": datetime.now().isoformat()
        }

        # Update invoice status
        invoice = self._make_request("GET", f"/invoices/{invoice_id}")
        total_amount = invoice.get("total_amount", 0)
        amount_paid = invoice.get("amount_paid", 0) + amount

        status = InvoiceStatus.PAID.value if amount_paid >= total_amount else InvoiceStatus.SENT.value

        self._make_request(
            "PUT",
            f"/invoices/{invoice_id}",
            data={
                "status": status,
                "amount_paid": amount_paid,
                "last_payment_date": payment_date.isoformat()
            }
        )

        return payment

    def generate_invoice_report(self, start_date: datetime,
                               end_date: datetime,
                               matter_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate invoice report for period

        Args:
            start_date: Report period start
            end_date: Report period end
            matter_id: Optional specific matter

        Returns:
            Invoice report
        """
        params = {
            "date__gte": start_date.isoformat(),
            "date__lte": end_date.isoformat(),
            "limit": 500
        }

        if matter_id:
            params["matter__id"] = matter_id

        response = self._make_request("GET", "/invoices", params=params)
        invoices = response.get("data", [])

        total_invoiced = sum(inv.get("total_amount", 0) for inv in invoices)
        total_paid = sum(inv.get("amount_paid", 0) for inv in invoices)
        total_outstanding = total_invoiced - total_paid

        by_status = {}
        for inv in invoices:
            status = inv.get("status", "Unknown")
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "matter_id": matter_id,
            "total_invoices": len(invoices),
            "total_invoiced": round(total_invoiced, 2),
            "total_paid": round(total_paid, 2),
            "total_outstanding": round(total_outstanding, 2),
            "invoice_count_by_status": by_status,
            "average_invoice": round(total_invoiced / len(invoices), 2) if invoices else 0
        }


# Example usage
if __name__ == "__main__":
    generator = InvoiceGenerator(api_key="your_clio_api_key")

    # Generate hourly invoice
    # invoice = generator.generate_hourly_invoice(
    #     "matter_123",
    #     datetime(2024, 1, 1),
    #     datetime(2024, 1, 31)
    # )
    # print(f"Invoice total: ${invoice['total_amount']}")

    # Create flat fee invoice
    # flat_invoice = generator.create_flat_fee_invoice("matter_123", 5000)
    # saved = generator.save_invoice(flat_invoice)

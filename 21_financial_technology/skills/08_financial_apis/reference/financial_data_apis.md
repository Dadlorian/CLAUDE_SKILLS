# Financial Data APIs

## Core Financial Data Types

### Account Information

**Account Data Model**:
```json
{
  "resourceId": "acc-123",
  "iban": "DE89370400440532013000",
  "bban": "370400440532013000",
  "currency": "EUR",
  "name": "Salary Account",
  "displayName": "Personal Salary",
  "accountType": "CACC",
  "accountSubType": "SAVINGS",
  "status": "ENABLED",
  "linkedAccounts": [
    {
      "iban": "DE75512108001234567890",
      "currency": "EUR"
    }
  ],
  "usage": "PRIV",
  "details": {
    "owner": "John Doe",
    "country": "DE",
    "createdAt": "2020-01-15"
  }
}
```

**Account Types** (ISO 20022):
- **CACC**: Current Account
- **SVGS**: Savings Account
- **TRAD**: Trading Account
- **TRAS**: Transit Account
- **CASH**: Cash Account
- **MMMM**: Money Market Account
- **LOAN**: Loan Account
- **OTHR**: Other

### Balance Information

**Balance Types**:
```json
{
  "balances": [
    {
      "balanceType": "INTERIM_BOOKED",
      "balanceAmount": {
        "amount": "1234.56",
        "currency": "EUR"
      },
      "referenceDate": "2024-11-19",
      "lastChangeDateTime": "2024-11-19T15:00:00Z"
    },
    {
      "balanceType": "INTERIM_AVAILABLE",
      "balanceAmount": {
        "amount": "1234.56",
        "currency": "EUR"
      }
    },
    {
      "balanceType": "PENDING",
      "balanceAmount": {
        "amount": "500.00",
        "currency": "EUR"
      }
    },
    {
      "balanceType": "EXPECTED",
      "balanceAmount": {
        "amount": "1734.56",
        "currency": "EUR"
      }
    },
    {
      "balanceType": "AUTHORISED",
      "balanceAmount": {
        "amount": "5000.00",
        "currency": "EUR"
      }
    }
  ]
}
```

**Balance Types**:
- **INTERIM_BOOKED**: Confirmed transactions (settled)
- **INTERIM_AVAILABLE**: Available for withdrawal
- **PENDING**: Transactions in progress
- **EXPECTED**: Forecasted balance
- **AUTHORISED**: Credit limit authorized
- **OPENING_AVAILABLE**: Balance at start of day

### Transaction Information

**Transaction Data Model**:
```json
{
  "transactionId": "txn-123-456",
  "bookingDate": "2024-11-19",
  "valueDate": "2024-11-20",
  "entryDate": "2024-11-19T10:30:00Z",
  "amount": {
    "amount": "-50.00",
    "currency": "EUR"
  },
  "creditDebitIndicator": "DEBIT",
  "status": "BOOKED",
  "purpose": "PRIC",
  "banksTransactionCode": "PMNT-DMCT-ESCT",
  "proprietaryBankTransactionCode": "INTERNAL-123",
  "transactionAmount": {
    "amount": "-50.00",
    "currency": "EUR"
  },
  "currencyExchange": [
    {
      "sourceCurrency": "GBP",
      "targetCurrency": "EUR",
      "exchangeRate": "1.1850",
      "contractIdentification": "FX123456"
    }
  ],
  "creditorName": "Cafe Espresso",
  "creditorAccount": {
    "iban": "IT60X0542811101000000123456",
    "bban": "0542811101000000123456",
    "accountType": "CACC"
  },
  "debtorName": "John Doe",
  "debtorAccount": {
    "iban": "DE89370400440532013000"
  },
  "remittanceInformationUnstructured": "Coffee payment",
  "remittanceInformationStructured": {
    "reference": "INV-12345",
    "referenceType": "ISSR"
  },
  "additionalInformation": "Payment for morning coffee",
  "balanceAfterTransaction": {
    "amount": "1184.56",
    "currency": "EUR"
  }
}
```

**Transaction Fields**:

| Field | Description |
|-------|-------------|
| transactionId | Unique identifier |
| bookingDate | Date transaction settled |
| valueDate | Date funds available |
| amount | Transaction amount |
| creditDebitIndicator | DEBIT or CREDIT |
| status | BOOKED, PENDING, FORTHCOMING |
| creditorName | Recipient name |
| creditorAccount | Recipient account details |
| debtorName | Sender name |
| debtorAccount | Sender account details |
| remittanceInformation | Payment reference/memo |

### Payment Type Information

**Payment Codes** (ISO 20022):
```
PMNT-DMCT - Domestic Transfer
PMNT-INTC - International Transfer
PMNT-CHQC - Check/Cheque
PMNT-OTHR - Other
SEPA-CREDIT - SEPA Credit Transfer
SEPA-DIRECT - SEPA Direct Debit
INSTANT-SCT - Instant Credit Transfer
SWIFT - International SWIFT
```

## Data Aggregation Patterns

### Account Aggregation
```python
class AccountAggregator:
    def aggregate_accounts(self, user_id, banks):
        """
        Aggregate accounts from multiple banks
        """
        all_accounts = []

        for bank in banks:
            token = self.get_user_token(user_id, bank)
            accounts = self.fetch_accounts(bank, token)
            all_accounts.extend(accounts)

        return self.normalize_accounts(all_accounts)

    def normalize_accounts(self, accounts):
        """
        Normalize accounts to standard format
        """
        normalized = []

        for account in accounts:
            normalized.append({
                "source_bank": account.get("bank"),
                "iban": account.get("iban"),
                "currency": account.get("currency"),
                "name": account.get("displayName") or account.get("name"),
                "type": self.map_account_type(account.get("accountType")),
                "status": account.get("status")
            })

        return normalized
```

### Balance Aggregation
```python
class BalanceAggregator:
    def get_total_balance(self, accounts):
        """
        Calculate total balance across accounts
        """
        total_balance = {}

        for account in accounts:
            # Fetch balance for each account
            balance = self.fetch_balance(account)
            currency = balance.get("currency")

            if currency not in total_balance:
                total_balance[currency] = 0.0

            # Add to currency total
            total_balance[currency] += float(balance.get("amount", 0))

        return total_balance

    def get_balance_trends(self, account_id, days=30):
        """
        Get balance history for trend analysis
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        transactions = self.fetch_transactions(
            account_id,
            start_date,
            end_date
        )

        # Calculate daily balances
        balances_by_date = {}
        running_balance = 0.0

        for txn in sorted(transactions, key=lambda x: x["valueDate"]):
            date = txn["valueDate"]
            amount = float(txn["amount"]["amount"])
            running_balance += amount
            balances_by_date[date] = running_balance

        return balances_by_date
```

## Data Quality and Normalization

### Handling Multiple Currencies
```python
class CurrencyConverter:
    def __init__(self, rate_service):
        self.rate_service = rate_service

    def convert_balance(self, amount, from_currency, to_currency):
        """
        Convert amount to target currency
        """
        if from_currency == to_currency:
            return amount

        rate = self.rate_service.get_rate(from_currency, to_currency)
        return amount * rate

    def normalize_to_base_currency(self, balances, base_currency="EUR"):
        """
        Normalize all balances to base currency
        """
        normalized = {}

        for currency, amount in balances.items():
            normalized[currency] = amount
            if currency != base_currency:
                normalized[f"{currency}_in_{base_currency}"] = \
                    self.convert_balance(amount, currency, base_currency)

        return normalized
```

### Date Handling
```python
from datetime import datetime, timezone

class DateNormalizer:
    @staticmethod
    def normalize_date(date_str):
        """
        Handle various date formats
        """
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S+00:00",
            "%d/%m/%Y",
            "%d-%m-%Y"
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                # Return ISO format with UTC
                return parsed.replace(tzinfo=timezone.utc).isoformat()
            except ValueError:
                continue

        raise ValueError(f"Unable to parse date: {date_str}")
```

## Financial Data API Providers

### Aggregator APIs

**Plaid**:
- Multi-country account access
- Real-time balance and transactions
- Identity verification
- Investment data
- Income verification

**Tink**:
- European focus
- Transaction enrichment
- Categorization
- Insights and analytics
- Payment initiation

**Finicity**:
- Account access
- Cash flow analysis
- Transaction data
- Income verification
- Open financial data

**Yodlee**:
- Global coverage
- Data aggregation
- Data enrichment
- Mobile optimization

### Financial Data APIs

**Alpha Vantage**:
- Stock prices
- Forex rates
- Crypto data
- Technical indicators

**Twelve Data**:
- Market data
- Real-time quotes
- Historical data
- Company information

**IEX Cloud**:
- Stock market data
- Cryptocurrency
- Alternative data
- Regulatory filings

### Transaction Categorization

**Merchant Data**:
```json
{
  "transactionId": "txn-123",
  "merchant": {
    "name": "Starbucks Coffee #1234",
    "category": "FOOD_AND_DRINK",
    "subcategory": "COFFEE_SHOPS",
    "mcc": "5461",
    "logoUrl": "https://...",
    "website": "https://starbucks.com"
  },
  "location": {
    "address": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "zipCode": "94105",
    "country": "US",
    "latitude": 37.7749,
    "longitude": -122.4194
  }
}
```

## Financial Data Standards

### ISO 20022 XML Structure
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document>
  <BkToCstmrStmt>
    <GrpHdr>
      <MsgId>MSG-001</MsgId>
      <CreDtTm>2024-11-19T10:30:00Z</CreDtTm>
    </GrpHdr>
    <Stmt>
      <Acct>
        <Id>
          <IBAN>DE89370400440532013000</IBAN>
        </Id>
        <Bal>
          <Amt>1234.56</Amt>
          <Ccy>EUR</Ccy>
        </Bal>
      </Acct>
      <Ntry>
        <Amt>50.00</Amt>
        <CdtDbtInd>DEBIT</CdtDbtInd>
        <BkgDt>
          <Dt>2024-11-19</Dt>
        </BkgDt>
      </Ntry>
    </Stmt>
  </BkToCstmrStmt>
</Document>
```

### IBAN Validation
```python
def validate_iban(iban):
    """
    Validate IBAN using check digit algorithm
    """
    # Remove spaces
    iban = iban.replace(" ", "").upper()

    # Check length by country
    lengths = {
        "AD": 24, "AE": 23, "AL": 28, "AT": 20,
        "AZ": 28, "BA": 20, "BE": 16, "BG": 22,
        "BH": 22, "BR": 29, "BY": 28, "CH": 21,
        "CR": 22, "CY": 28, "CZ": 24, "DE": 22,
        # ... more countries
    }

    country_code = iban[:2]
    if len(iban) != lengths.get(country_code):
        return False

    # Check digit validation
    # Move first 4 chars to end
    rearranged = iban[4:] + iban[:4]

    # Replace letters with numbers (A=10, B=11, etc.)
    numeric = ""
    for char in rearranged:
        if char.isdigit():
            numeric += char
        else:
            numeric += str(ord(char) - ord('A') + 10)

    # Validate mod 97
    return int(numeric) % 97 == 1
```

## References

- ISO 20022: https://www.iso20022.org/
- IBAN Registry: https://www.iban.com/structure
- Transaction Codes: https://en.wikipedia.org/wiki/ISO_10962
- Merchant Category Codes: https://en.wikipedia.org/wiki/Merchant_category_code

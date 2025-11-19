# Account Information APIs

## Account Information Services (AIS)

AIS is a PSD2 service allowing third-party providers to access customer financial account data with proper authorization.

## AIS Capabilities

### Account Discovery
**Purpose**: Identify customer's accounts at bank

```json
GET /accounts
Authorization: Bearer {access_token}

Response:
{
  "accounts": [
    {
      "resourceId": "acc-001",
      "iban": "DE89370400440532013000",
      "bban": "370400440532013000",
      "currency": "EUR",
      "name": "Personal Checking",
      "displayName": "My Bank Account",
      "accountNumber": "532013000",
      "bankCode": "37040044",
      "accountType": "CACC",
      "status": "ENABLED"
    },
    {
      "resourceId": "acc-002",
      "iban": "DE75512108001234567890",
      "currency": "EUR",
      "name": "Savings Account",
      "accountType": "SVGS",
      "status": "ENABLED"
    }
  ]
}
```

### Balance Retrieval
**Purpose**: Get current account balance and history

```python
class BalanceRetriever:
    def get_account_balance(self, account_id):
        """
        Get current balance for account
        """
        response = requests.get(
            f"https://api.bank.com/accounts/{account_id}/balances",
            headers={"Authorization": f"Bearer {self.token}"},
            params={"currency": "EUR"}
        )

        balances = response.json()["balances"]

        # Extract key balances
        result = {}
        for balance in balances:
            balance_type = balance["balanceType"]
            amount = balance["balanceAmount"]["amount"]

            if balance_type == "INTERIM_BOOKED":
                result["booked"] = float(amount)
            elif balance_type == "INTERIM_AVAILABLE":
                result["available"] = float(amount)
            elif balance_type == "PENDING":
                result["pending"] = float(amount)

        return result

    def get_balance_history(self, account_id, days=90):
        """
        Get balance snapshots over time
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        transactions = self.get_transactions(
            account_id,
            start_date,
            end_date
        )

        # Calculate balance at each transaction
        balances = []
        running_balance = self.get_current_balance(account_id)

        # Work backwards through transactions
        for txn in reversed(transactions):
            amount = float(txn["transactionAmount"]["amount"])
            running_balance -= amount

            balances.append({
                "date": txn["valueDate"],
                "balance": running_balance
            })

        return list(reversed(balances))
```

### Transaction Retrieval
**Purpose**: Access transaction history

```python
class TransactionRetriever:
    def get_transactions(self, account_id, start_date=None, end_date=None):
        """
        Retrieve transaction history
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=90)
        if not end_date:
            end_date = datetime.now()

        params = {
            "dateFrom": start_date.date().isoformat(),
            "dateTo": end_date.date().isoformat()
        }

        response = requests.get(
            f"https://api.bank.com/accounts/{account_id}/transactions",
            headers={"Authorization": f"Bearer {self.token}"},
            params=params
        )

        data = response.json()

        # Combine booked and pending
        all_transactions = []
        all_transactions.extend(data.get("booked", []))
        all_transactions.extend(data.get("pending", []))

        return sorted(
            all_transactions,
            key=lambda x: x["valueDate"],
            reverse=True
        )

    def get_paginated_transactions(self, account_id, start_date, end_date):
        """
        Handle paginated transaction results
        """
        all_transactions = []
        cursor = None

        while True:
            params = {
                "dateFrom": start_date.isoformat(),
                "dateTo": end_date.isoformat()
            }

            if cursor:
                params["cursor"] = cursor

            response = requests.get(
                f"https://api.bank.com/accounts/{account_id}/transactions",
                headers={"Authorization": f"Bearer {self.token}"},
                params=params
            )

            data = response.json()
            all_transactions.extend(data.get("transactions", []))

            # Check for more pages
            if data.get("pagination", {}).get("hasMore"):
                cursor = data["pagination"]["nextCursor"]
            else:
                break

        return all_transactions
```

## Consent Management for AIS

### Creating AIS Consent
```python
class AISConsentManager:
    def create_account_access_consent(self, access_accounts=None, access_balances=None,
                                      access_transactions=None, valid_until=None,
                                      frequency_per_day=4):
        """
        Create consent for account information access
        """
        # Default to all operations if not specified
        access = {
            "accounts": access_accounts or [],
            "balances": access_balances or [],
            "transactions": access_transactions or []
        }

        consent_data = {
            "access": access,
            "recurringIndicator": False,
            "validUntil": valid_until or "2025-12-31",
            "frequencyPerDay": frequency_per_day
        }

        response = requests.post(
            "https://api.bank.com/consents",
            json=consent_data,
            headers={"Authorization": f"Bearer {self.token}"}
        )

        result = response.json()

        return {
            "consentId": result["consentId"],
            "status": result["consentStatus"],
            "scaRedirect": result["links"]["scaRedirect"]["href"]
        }

    def get_consent_status(self, consent_id):
        """
        Check consent status and validity
        """
        response = requests.get(
            f"https://api.bank.com/consents/{consent_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        consent = response.json()

        return {
            "consentId": consent["consentId"],
            "status": consent["consentStatus"],
            "validUntil": consent.get("validUntil"),
            "frequencyPerDay": consent.get("frequencyPerDay"),
            "lastActionDate": consent.get("lastActionDate")
        }

    def revoke_consent(self, consent_id):
        """
        Revoke account access consent
        """
        response = requests.delete(
            f"https://api.bank.com/consents/{consent_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        return response.status_code == 204
```

## Data Aggregation from AIS

### Multi-Bank Account Aggregation
```python
class MultiAccountAggregator:
    def __init__(self, bank_apis):
        """
        bank_apis: dict of {bank_name: BankAPIClient}
        """
        self.bank_apis = bank_apis

    def aggregate_accounts(self, user_id):
        """
        Get all accounts across all banks
        """
        all_accounts = {}

        for bank_name, api_client in self.bank_apis.items():
            try:
                token = self.get_user_token(user_id, bank_name)
                accounts = api_client.get_accounts(token)

                all_accounts[bank_name] = {
                    "accounts": self.normalize_accounts(accounts),
                    "status": "success"
                }
            except Exception as e:
                all_accounts[bank_name] = {
                    "status": "error",
                    "error": str(e)
                }

        return all_accounts

    def aggregate_balances(self, user_id, target_currency="EUR"):
        """
        Get total balance across all banks
        """
        total_balance = {}
        account_balances = []

        for bank_name, api_client in self.bank_apis.items():
            try:
                token = self.get_user_token(user_id, bank_name)
                accounts = api_client.get_accounts(token)

                for account in accounts:
                    balance_info = api_client.get_balance(
                        token,
                        account["resourceId"]
                    )

                    currency = account["currency"]
                    amount = float(balance_info["booked"])

                    # Convert to target currency if needed
                    if currency != target_currency:
                        amount = self.convert_currency(
                            amount,
                            currency,
                            target_currency
                        )

                    account_balances.append({
                        "bank": bank_name,
                        "account": account["name"],
                        "currency": currency,
                        "amount": amount,
                        "iban": account["iban"]
                    })

                    # Add to total
                    if currency not in total_balance:
                        total_balance[currency] = 0
                    total_balance[currency] += amount

            except Exception as e:
                print(f"Error accessing {bank_name}: {e}")

        return {
            "totalBalance": total_balance,
            "accountBalances": account_balances,
            "timestamp": datetime.utcnow()
        }

    def aggregate_transactions(self, user_id, days=30):
        """
        Get transactions from all accounts
        """
        all_transactions = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        for bank_name, api_client in self.bank_apis.items():
            try:
                token = self.get_user_token(user_id, bank_name)
                accounts = api_client.get_accounts(token)

                for account in accounts:
                    transactions = api_client.get_transactions(
                        token,
                        account["resourceId"],
                        start_date,
                        end_date
                    )

                    for txn in transactions:
                        txn["bank"] = bank_name
                        txn["accountName"] = account["name"]
                        txn["accountIban"] = account["iban"]
                        all_transactions.append(txn)

            except Exception as e:
                print(f"Error accessing {bank_name}: {e}")

        # Sort by date
        all_transactions.sort(
            key=lambda x: x["valueDate"],
            reverse=True
        )

        return {
            "transactions": all_transactions,
            "count": len(all_transactions),
            "dateRange": {
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            }
        }
```

## Advanced Account Information Features

### Account Validation
```python
class AccountValidator:
    @staticmethod
    def validate_account_exists(iban, api_client, token):
        """
        Verify account exists before using it
        """
        try:
            accounts = api_client.get_accounts(token)
            for account in accounts:
                if account["iban"].replace(" ", "") == iban.replace(" ", ""):
                    return True
            return False
        except:
            return False

    @staticmethod
    def validate_account_for_payment(account_id, api_client, token):
        """
        Check if account can be used for payments
        """
        try:
            account = api_client.get_account(token, account_id)
            # Check status
            if account["status"] != "ENABLED":
                return False, f"Account status: {account['status']}"
            # Check balance
            balance = api_client.get_balance(token, account_id)
            if float(balance["available"]) <= 0:
                return False, "Insufficient available balance"
            return True, "Account is valid"
        except Exception as e:
            return False, str(e)
```

### Account Insights
```python
class AccountInsights:
    def calculate_spending_pattern(self, transactions, category=None):
        """
        Analyze spending patterns
        """
        spending = {}

        for txn in transactions:
            if txn["creditDebitIndicator"] != "DEBIT":
                continue

            # Group by month
            month = txn["valueDate"][:7]  # YYYY-MM

            if month not in spending:
                spending[month] = 0.0

            amount = float(txn["transactionAmount"]["amount"])
            spending[month] += abs(amount)

        return spending

    def calculate_average_daily_balance(self, transactions):
        """
        Get average balance over period
        """
        if not transactions:
            return 0.0

        running_balance = 0.0
        transaction_count = 0

        for txn in reversed(transactions):
            amount = float(txn["transactionAmount"]["amount"])
            running_balance += amount
            transaction_count += 1

        return running_balance / transaction_count if transaction_count > 0 else 0.0

    def identify_regular_payments(self, transactions, threshold_days=28):
        """
        Find recurring payments
        """
        creditors = {}

        for txn in transactions:
            creditor = txn.get("creditorName", "Unknown")

            if creditor not in creditors:
                creditors[creditor] = []

            creditors[creditor].append(txn["valueDate"])

        # Find creditors with regular payments
        regular = {}
        for creditor, dates in creditors.items():
            if len(dates) >= 2:
                # Calculate intervals
                intervals = []
                sorted_dates = sorted(dates)

                for i in range(len(sorted_dates) - 1):
                    date1 = datetime.fromisoformat(sorted_dates[i])
                    date2 = datetime.fromisoformat(sorted_dates[i + 1])
                    interval = (date2 - date1).days
                    intervals.append(interval)

                # Check if regular (within threshold)
                avg_interval = sum(intervals) / len(intervals)
                is_regular = all(
                    abs(i - avg_interval) < threshold_days
                    for i in intervals
                )

                if is_regular:
                    regular[creditor] = {
                        "frequency_days": int(avg_interval),
                        "count": len(dates),
                        "last_payment": sorted_dates[-1]
                    }

        return regular
```

## Error Handling for AIS

### Common AIS Errors
- **401 Unauthorized**: Token invalid or expired
- **403 Forbidden**: Consent not valid or expired
- **404 Not Found**: Account doesn't exist
- **429 Too Many Requests**: Rate limit exceeded
- **503 Service Unavailable**: Bank maintenance

### Retry Strategy
```python
class AISwithRetry:
    def get_accounts_with_retry(self, token, max_retries=3):
        """
        Retry account fetch on failure
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    "https://api.bank.com/accounts",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5
                )

                if response.status_code == 200:
                    return response.json()["accounts"]

                if response.status_code == 401:
                    raise AuthenticationError("Token expired")

                if response.status_code == 429:
                    wait_time = int(
                        response.headers.get("Retry-After", 2 ** attempt)
                    )
                    time.sleep(wait_time)
                    continue

                if response.status_code >= 500:
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    raise ServerError(response.text)

                raise Exception(f"HTTP {response.status_code}")

            except (requests.Timeout, requests.ConnectionError) as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise

        raise Exception("Max retries exceeded")
```

## References

- PSD2 Account Information Services: https://www.eba.europa.eu/
- Berlin Group API: https://www.berlin-group.org/

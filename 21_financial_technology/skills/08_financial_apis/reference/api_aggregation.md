# API Aggregation Patterns

## Aggregation Architecture

### Types of Aggregation

**Data Aggregation**:
- Combine data from multiple sources
- Normalize formats
- Cache results

**Payment Aggregation**:
- Route payments to optimal provider
- Track across networks
- Provide unified status

**API Gateway Aggregation**:
- Route requests to appropriate backend
- Handle authentication/authorization
- Transform responses

## Data Aggregation Patterns

### Sequential Aggregation
```python
class SequentialAggregator:
    def aggregate_sequentially(self, accounts):
        """
        Fetch from each bank one at a time
        Slower but simpler error handling
        """
        results = []

        for account in accounts:
            try:
                balance = self.fetch_balance(account)
                transactions = self.fetch_transactions(account)

                results.append({
                    "account": account,
                    "balance": balance,
                    "transactions": transactions
                })
            except Exception as e:
                results.append({
                    "account": account,
                    "error": str(e)
                })

        return results
```

### Parallel Aggregation
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ParallelAggregator:
    def __init__(self, max_workers=5):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def aggregate_parallel(self, accounts):
        """
        Fetch from all banks concurrently
        Faster but requires careful error handling
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        tasks = [
            self.fetch_account_data_async(account)
            for account in accounts
        ]

        results = loop.run_until_complete(
            asyncio.gather(*tasks, return_exceptions=True)
        )

        return results

    async def fetch_account_data_async(self, account):
        """
        Async fetch for single account
        """
        try:
            balance = await self.fetch_balance_async(account)
            transactions = await self.fetch_transactions_async(account)

            return {
                "account": account,
                "balance": balance,
                "transactions": transactions,
                "status": "success"
            }
        except Exception as e:
            return {
                "account": account,
                "error": str(e),
                "status": "error"
            }
```

### Caching Strategy

```python
class CachedAggregator:
    def __init__(self, cache_ttl_seconds=300):
        self.cache = {}
        self.cache_ttl = cache_ttl_seconds

    def get_balance_with_cache(self, account_id):
        """
        Return cached balance if valid, else fetch fresh
        """
        cache_key = f"balance_{account_id}"
        cached_data = self.cache.get(cache_key)

        if cached_data:
            if self.is_cache_valid(cached_data):
                return cached_data["data"]

        # Fetch fresh data
        balance = self.fetch_balance(account_id)

        # Store in cache
        self.cache[cache_key] = {
            "data": balance,
            "timestamp": datetime.now()
        }

        return balance

    def is_cache_valid(self, cached_item):
        """
        Check if cached data is still fresh
        """
        age = (datetime.now() - cached_item["timestamp"]).total_seconds()
        return age < self.cache_ttl

    def invalidate_cache(self, account_id):
        """
        Manually invalidate cache for account
        """
        cache_key = f"balance_{account_id}"
        if cache_key in self.cache:
            del self.cache[cache_key]
```

## Data Normalization

### Schema Normalization
```python
class DataNormalizer:
    # Bank-specific account type mappings
    BANK_ACCOUNT_TYPE_MAP = {
        "BBVA": {
            "CC": "CACC",
            "AH": "SVGS",
            "INV": "TRAD"
        },
        "Santander": {
            "5": "CACC",
            "7": "SVGS",
            "8": "TRAD"
        },
        "BNP": {
            "001": "CACC",
            "002": "SVGS"
        }
    }

    def normalize_account(self, bank_name, raw_account):
        """
        Convert bank-specific format to standard
        """
        normalized = {
            "source_bank": bank_name,
            "source_id": raw_account.get("id"),
            "iban": raw_account.get("iban") or self.derive_iban(raw_account),
            "currency": raw_account.get("currency") or "EUR",
            "name": raw_account.get("name") or raw_account.get("accountName"),
            "type": self.normalize_account_type(
                bank_name,
                raw_account.get("type")
            ),
            "status": raw_account.get("status") or "ACTIVE"
        }

        return normalized

    def normalize_account_type(self, bank_name, bank_type):
        """
        Convert bank-specific account type to ISO standard
        """
        if bank_name in self.BANK_ACCOUNT_TYPE_MAP:
            mapping = self.BANK_ACCOUNT_TYPE_MAP[bank_name]
            return mapping.get(bank_type, "CACC")
        return "CACC"  # Default

    def normalize_transaction(self, bank_name, raw_txn):
        """
        Normalize transaction format
        """
        return {
            "source_bank": bank_name,
            "source_id": raw_txn.get("id"),
            "date": self.normalize_date(raw_txn.get("date")),
            "amount": float(raw_txn.get("amount") or 0),
            "currency": raw_txn.get("currency") or "EUR",
            "description": raw_txn.get("description") or raw_txn.get("reference"),
            "creditor": self.extract_creditor(raw_txn),
            "type": self.classify_transaction(raw_txn)
        }

    def normalize_date(self, date_value):
        """
        Parse various date formats
        """
        if isinstance(date_value, str):
            # Try common formats
            formats = [
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%Y-%m-%dT%H:%M:%S",
                "%m-%d-%Y"
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt).date()
                except ValueError:
                    continue

        return date_value

    def extract_creditor(self, txn):
        """
        Extract creditor/merchant name
        """
        return (
            txn.get("creditorName") or
            txn.get("merchantName") or
            txn.get("counterparty") or
            txn.get("description", "").split()[0]
        )

    def classify_transaction(self, txn):
        """
        Classify transaction type
        """
        description = (txn.get("description") or "").lower()

        if "salary" in description or "payroll" in description:
            return "INCOME"
        elif "atm" in description or "withdrawal" in description:
            return "CASH"
        elif "transfer" in description:
            return "TRANSFER"
        elif any(x in description for x in ["subscription", "recurring"]):
            return "SUBSCRIPTION"
        else:
            return "EXPENSE"
```

## Error Handling in Aggregation

### Circuit Breaker Pattern
```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # All requests fail
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        """
        Execute function with circuit breaker protection
        """
        if self.state == CircuitState.OPEN:
            if self.should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise

    def on_success(self):
        """
        Reset on successful call
        """
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def on_failure(self):
        """
        Track failures
        """
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def should_attempt_reset(self):
        """
        Check if enough time has passed to retry
        """
        return (
            datetime.now() - self.last_failure_time >
            timedelta(seconds=self.recovery_timeout)
        )
```

### Graceful Degradation
```python
class DegradedAggregator:
    def get_balance_with_fallback(self, account_id):
        """
        Try fresh data, fallback to cache if unavailable
        """
        try:
            # Try to get fresh data
            balance = self.fetch_balance(account_id)
            self.cache_balance(account_id, balance)
            return {
                "balance": balance,
                "freshness": "real-time"
            }
        except Exception as e:
            # Fall back to cached data
            cached = self.get_cached_balance(account_id)
            if cached:
                return {
                    "balance": cached,
                    "freshness": "cached",
                    "warning": "Using cached data due to service unavailable"
                }

            # Last resort
            raise Exception(f"Unable to retrieve balance: {e}")

    def aggregate_with_partial_failure(self, accounts):
        """
        Return partial results if some banks fail
        """
        results = {
            "successful": [],
            "failed": [],
            "partial": False
        }

        for account in accounts:
            try:
                data = self.fetch_account_data(account)
                results["successful"].append(data)
            except Exception as e:
                results["failed"].append({
                    "account": account,
                    "error": str(e)
                })
                results["partial"] = True

        return results
```

## Performance Optimization

### Batch Processing
```python
class BatchAggregator:
    def batch_fetch_accounts(self, account_ids, batch_size=10):
        """
        Fetch multiple accounts in batches
        """
        results = []

        for i in range(0, len(account_ids), batch_size):
            batch = account_ids[i:i + batch_size]
            batch_results = self.fetch_batch(batch)
            results.extend(batch_results)

        return results

    def fetch_batch(self, account_ids):
        """
        Fetch single batch of accounts
        """
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.fetch_single, aid): aid
                for aid in account_ids
            }

            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    account_id = futures[future]
                    results.append({
                        "account_id": account_id,
                        "error": str(e)
                    })

        return results
```

## Monitoring Aggregation

### Health Metrics
```python
class AggregationMetrics:
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "successful": 0,
            "failed": 0,
            "latency": []
        }

    def record_request(self, bank_name, duration_ms, success):
        """
        Record aggregation request
        """
        self.metrics["total_requests"] += 1

        if success:
            self.metrics["successful"] += 1
        else:
            self.metrics["failed"] += 1

        self.metrics["latency"].append(duration_ms)

    def get_success_rate(self):
        """
        Calculate success percentage
        """
        total = self.metrics["total_requests"]
        if total == 0:
            return 100.0

        return (self.metrics["successful"] / total) * 100

    def get_average_latency(self):
        """
        Calculate average latency
        """
        if not self.metrics["latency"]:
            return 0

        return sum(self.metrics["latency"]) / len(self.metrics["latency"])

    def get_p95_latency(self):
        """
        Calculate 95th percentile latency
        """
        if not self.metrics["latency"]:
            return 0

        sorted_latencies = sorted(self.metrics["latency"])
        index = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[index]
```

## References

- Data Aggregation Patterns: https://microservices.io/
- Circuit Breaker Pattern: https://martinfowler.com/bliki/CircuitBreaker.html
- Async Aggregation: https://docs.python.org/3/library/asyncio.html

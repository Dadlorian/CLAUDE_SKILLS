# Mainframe Integration Patterns: COBOL & Legacy Systems

## Table of Contents
1. [Introduction](#introduction)
2. [Mainframe Architecture Overview](#mainframe-architecture-overview)
3. [COBOL System Integration](#cobol-system-integration)
4. [Data Format Considerations](#data-format-considerations)
5. [Integration Patterns](#integration-patterns)
6. [API Gateway Strategies](#api-gateway-strategies)
7. [Message Queue Integration](#message-queue-integration)
8. [Performance Optimization](#performance-optimization)
9. [Security Considerations](#security-considerations)
10. [Case Studies](#case-studies)

---

## Introduction

Mainframe systems continue to power critical financial infrastructure at thousands of institutions worldwide. Rather than replacing these systems wholesale, organizations must learn to integrate modern applications with mainframe systems effectively.

### Why Mainframe Integration Matters

- **$3 Trillion** in daily transactions processed on mainframes
- **87%** of Fortune 500 companies rely on mainframe systems
- **30-40 years** of accumulated business logic and data
- **Highly optimized** for throughput and reliability

### Integration Challenges

1. **Architectural Mismatch**: Batch-oriented legacy vs. event-driven modern
2. **Data Format Incompatibilities**: COBOL fixed-length records vs. JSON/XML
3. **Synchronous vs. Asynchronous**: Legacy expects blocking calls
4. **Latency Sensitivity**: Mainframe operations may take seconds
5. **Connectivity**: Limited modern protocol support

---

## Mainframe Architecture Overview

### Traditional Mainframe Components

```
┌──────────────────────────────────────────────────────────┐
│              IBM MAINFRAME SYSTEM (z/OS)                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Transaction Servers (CICS)                        │ │
│  │ - Online transaction processing                   │ │
│  │ - Real-time request/response                      │ │
│  │ - Session management                              │ │
│  │ - Terminal emulation                              │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Batch Processing (JCL/COBOL)                      │ │
│  │ - End-of-day processing                           │ │
│  │ - Report generation                               │ │
│  │ - Data migration jobs                             │ │
│  │ - Scheduled reconciliation                        │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Database Management (DB2)                         │ │
│  │ - Relational database engine                      │ │
│  │ - ACID compliance                                 │ │
│  │ - Tablespaces and index management                │ │
│  │ - Online backup/recovery                          │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Data Storage                                       │ │
│  │ - VSAM (Virtual Sequential Access Method)         │ │
│  │ - IMS (Information Management System) hierarchical│ │
│  │ - Sequential files (tape/DASD)                    │ │
│  │ - DB2 relational storage                          │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Communication Layer                                │ │
│  │ - MQ Series (message queuing)                     │ │
│  │ - TCP/IP interfaces                               │ │
│  │ - TN3270 terminal protocol                        │ │
│  │ - Syncsort/DMExpress data exchange                │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Security Layer                                     │ │
│  │ - RACF (Resource Access Control Facility)         │ │
│  │ - Kerberos integration                            │ │
│  │ - Encryption services                             │ │
│  │ - Audit logging                                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Key Technologies

| Component | Purpose | Modern Equivalent |
|-----------|---------|-------------------|
| **CICS** | Transaction server | Application Server |
| **IMS** | Hierarchical database | NoSQL databases |
| **VSAM** | File storage | File storage systems |
| **DB2** | Relational database | PostgreSQL/Oracle |
| **MQ** | Message queuing | RabbitMQ/Kafka |
| **JCL** | Job scheduling | Kubernetes/Airflow |
| **COBOL** | Programming language | Java/Python |

---

## COBOL System Integration

### Understanding COBOL Data Structures

COBOL programs use fixed-format, hierarchical data structures quite different from modern formats:

```cobol
       IDENTIFICATION DIVISION.
       PROGRAM-ID. ACCOUNT-MASTER.

       DATA DIVISION.
       FILE SECTION.
       FD  ACCOUNT-FILE.
       01  ACCOUNT-RECORD.
           05  ACCT-ID                PIC 9(10).
           05  ACCT-TYPE              PIC X(2).
           05  CUST-ID                PIC 9(8).
           05  ACCT-NAME              PIC X(30).
           05  BALANCE                PIC S9(13)V99.
           05  OPEN-DATE              PIC 9(8).
           05  CLOSE-DATE             PIC 9(8).
           05  STATUS-CODE            PIC 9(1).
           05  LAST-ACTIVITY-DATE     PIC 9(8).
           05  FILLER                 PIC X(50).
```

### Integration Bridge Architecture

```python
class COBOLIntegrationBridge:
    """Bridge modern systems with COBOL backend"""

    def __init__(self):
        self.mainframe_client = MainframeConnector()
        self.transformer = COBOLTransformer()
        self.cache = LocalCache()

    def call_cobol_service(self, service_name: str, input_data: dict):
        """Call COBOL program with proper marshalling"""

        # 1. Serialize Python object to COBOL format
        cobol_input = self.transformer.to_cobol_record(
            service_name,
            input_data
        )

        # 2. Call COBOL program through CICS
        cobol_output = self.mainframe_client.call_cics_program(
            program_name=f"CBLPROG{service_name}",
            input_data=cobol_input,
            timeout=5000  # 5 seconds
        )

        # 3. Parse COBOL response (fixed-width format)
        parsed = self.transformer.from_cobol_record(
            service_name,
            cobol_output
        )

        # 4. Transform to modern structure
        return self.transformer.to_modern_object(
            service_name,
            parsed
        )


class COBOLTransformer:
    """Transform between COBOL and modern formats"""

    def to_cobol_record(self, service: str, data: dict) -> bytes:
        """Convert Python dict to fixed-width COBOL format"""

        if service == "GET_ACCOUNT":
            # Account ID: 10 chars, right-aligned, zero-padded
            acct_id = str(data['account_id']).zfill(10).encode()

            # Account Type: 2 chars, left-aligned, space-padded
            acct_type = data['account_type'].ljust(2).encode()

            # Customer ID: 8 chars
            cust_id = str(data['customer_id']).zfill(8).encode()

            # Combine into fixed-width record (125 bytes total)
            record = acct_id + acct_type + cust_id + b' ' * 105

            return record

        elif service == "POST_TRANSACTION":
            # Similar transformation for transaction input

            from_acct = str(data['from_account']).zfill(10).encode()
            to_acct = str(data['to_account']).zfill(10).encode()
            amount = str(int(data['amount'] * 100)).zfill(13).encode()
            description = data['description'].ljust(50).encode()

            record = from_acct + to_acct + amount + description + b' ' * 42

            return record

    def from_cobol_record(self, service: str, record: bytes) -> dict:
        """Parse fixed-width COBOL record to Python dict"""

        if service == "GET_ACCOUNT":
            return {
                'account_id': record[0:10].strip().decode(),
                'account_type': record[10:12].strip().decode(),
                'customer_id': record[12:20].strip().decode(),
                'account_name': record[20:50].strip().decode(),
                'balance': int(record[50:63].strip().decode()),
                'open_date': record[63:71].decode(),
                'close_date': record[71:79].decode(),
                'status_code': record[79:80].decode(),
                'last_activity': record[80:88].decode(),
                'return_code': record[88:92].decode()
            }

    def to_modern_object(self, service: str, parsed: dict):
        """Transform parsed COBOL data to modern object"""

        if service == "GET_ACCOUNT":
            return Account(
                id=parsed['account_id'],
                type=AccountType(parsed['account_type']),
                customer_id=parsed['customer_id'],
                name=parsed['account_name'],
                balance=Decimal(parsed['balance']) / 100,
                opened_date=datetime.strptime(parsed['open_date'], '%Y%m%d'),
                closed_date=datetime.strptime(
                    parsed['close_date'], '%Y%m%d'
                ) if parsed['close_date'] != '00000000' else None,
                status=AccountStatus(parsed['status_code']),
                last_activity=datetime.strptime(
                    parsed['last_activity'], '%Y%m%d'
                )
            )
```

### Terminal Emulation Integration

For systems without modern API interfaces:

```python
import pyte  # Python terminal emulator
from pyautogui import typewrite, press

class TN3270TerminalEmulator:
    """Emulate TN3270 terminal for legacy system interaction"""

    def __init__(self, host: str, port: int):
        self.telnet = telnetlib.Telnet(host, port)
        self.screen = pyte.Screen(80, 24)
        self.stream = pyte.Stream(self.screen)

    def send_keys(self, keys: str, wait_time: int = 100):
        """Send keystrokes to terminal and wait for response"""
        self.telnet.write(keys.encode())
        time.sleep(wait_time / 1000)

    def extract_field(self, row: int, col: int, length: int) -> str:
        """Extract displayed field from terminal screen"""
        line = self.screen.display[row]
        return line[col:col+length].rstrip()

    def get_account_info_via_terminal(self, account_id: str) -> Account:
        """Get account using terminal emulation"""

        # Navigate to account lookup screen
        self.send_keys("ACCTLKUP")
        self.send_keys("ENTER")
        self.wait_for_screen_update()

        # Enter account ID
        self.send_keys(account_id)
        self.send_keys("ENTER")
        self.wait_for_screen_update()

        # Extract displayed information
        return Account(
            id=account_id,
            name=self.extract_field(3, 10, 30),
            balance=Decimal(self.extract_field(5, 10, 15)),
            status=self.extract_field(7, 10, 1),
            opened_date=self.extract_field(9, 10, 8)
        )

    def wait_for_screen_update(self, timeout: int = 5):
        """Wait until screen content stops changing"""
        prev_display = None
        start = time.time()

        while time.time() - start < timeout:
            data = self.telnet.read_very_eager()
            if data:
                self.stream.feed(data)

            if self.screen.display == prev_display:
                return True

            prev_display = self.screen.display
            time.sleep(0.1)

        return False
```

---

## Data Format Considerations

### Fixed-Width Records

COBOL uses fixed-width records where each field occupies a specific byte position:

```
Account Record Layout (125 bytes total)
┌─────────────┬──────────┬───────────┬────────────────┬─────────────┬──────────┬──────────┬────────┬──────────────┐
│ Account ID  │ Type     │ Customer  │ Name           │ Balance     │ Open Dt  │ Close Dt │ Status │ Filler       │
│ 10 bytes    │ 2 bytes  │ 8 bytes   │ 30 bytes       │ 13 bytes    │ 8 bytes  │ 8 bytes  │ 1 byte │ 50 bytes     │
├─────────────┼──────────┼───────────┼────────────────┼─────────────┼──────────┼──────────┼────────┼──────────────┤
│ Positions   │ Pos      │ Pos       │ Pos            │ Pos         │ Pos      │ Pos      │ Pos    │ Pos 89-125   │
│ 1-10        │ 11-12    │ 13-20     │ 21-50          │ 51-63       │ 64-71    │ 72-79    │ 80     │ (Reserved)   │
└─────────────┴──────────┴───────────┴────────────────┴─────────────┴──────────┴──────────┴────────┴──────────────┘

Example Record (actual bytes):
0000000001  AC 20230115         000000000015234567890123[Account Name        ] 00000000012345678901234567890
```

### Packed Decimal (COMP-3)

COBOL programs use packed decimal for numeric fields (more space efficient):

```python
class PackedDecimalConverter:
    """Convert between packed decimal and Python numbers"""

    @staticmethod
    def to_packed_decimal(number: int, digits: int) -> bytes:
        """Convert Python int to COBOL packed decimal"""
        # Example: 1234 with 5 digits = 0x1234F in packed decimal
        # Last nibble is sign (F=positive, D=negative)

        str_num = str(abs(number)).zfill(digits)
        sign = 'F' if number >= 0 else 'D'

        # Convert pairs of digits to hex bytes
        bytes_list = []
        for i in range(0, len(str_num), 2):
            byte_val = str_num[i:i+2] + sign
            bytes_list.append(int(byte_val, 16))

        return bytes(bytes_list)

    @staticmethod
    def from_packed_decimal(data: bytes) -> int:
        """Convert COBOL packed decimal to Python int"""
        hex_str = data.hex()

        # Last digit is sign
        last_nibble = hex_str[-1]
        is_negative = last_nibble in 'bBdD'

        # Remove sign nibble and convert
        digits = hex_str[:-1]

        # Reconstruct number
        number = int(digits)
        if is_negative:
            number = -number

        return number


# Example usage
converter = PackedDecimalConverter()

# 1234 in packed decimal format
packed = converter.to_packed_decimal(1234, 5)
print(packed.hex())  # Output: 12340f (spaces removed)

# Convert back
value = converter.from_packed_decimal(bytes.fromhex('12340f'))
print(value)  # Output: 1234
```

### EBCDIC Encoding

Mainframes traditionally use EBCDIC (Extended Binary Coded Decimal) encoding instead of ASCII:

```python
class EBCDICTranscoder:
    """Convert between EBCDIC and ASCII/UTF-8"""

    # EBCDIC to ASCII mapping (simplified)
    EBCDIC_TO_ASCII = {
        0x41: 'A', 0x42: 'B', 0x43: 'C', 0x44: 'D', 0x45: 'E',
        # ... full mapping would be 256 entries
        0xA2: 's', 0xA3: 't', 0xA4: 'u', 0xA5: 'v', 0xA6: 'w',
        0x40: ' ',  # Space
        0xF0: '0', 0xF1: '1', 0xF2: '2', 0xF3: '3', 0xF4: '4',
        0xF5: '5', 0xF6: '6', 0xF7: '7', 0xF8: '8', 0xF9: '9',
    }

    @staticmethod
    def decode_ebcdic(data: bytes) -> str:
        """Convert EBCDIC bytes to ASCII string"""
        return ''.join(
            EBCDICTranscoder.EBCDIC_TO_ASCII.get(byte, '?')
            for byte in data
        )

    @staticmethod
    def encode_ebcdic(text: str) -> bytes:
        """Convert ASCII string to EBCDIC bytes"""
        ascii_to_ebcdic = {v: k for k, v in EBCDICTranscoder.EBCDIC_TO_ASCII.items()}

        return bytes(
            ascii_to_ebcdic.get(char, 0x3F)  # 0x3F = '?'
            for char in text
        )
```

---

## Integration Patterns

### Pattern 1: Synchronous Request-Response

For real-time operations requiring immediate responses:

```python
class SynchronousMainframeAdapter:
    """Synchronous integration for time-sensitive operations"""

    def __init__(self):
        self.connection_pool = ConnectionPool(size=50)
        self.timeout = timedelta(seconds=5)

    def get_account_balance(self, account_id: str) -> Decimal:
        """Fetch account balance synchronously"""

        conn = self.connection_pool.get_connection()

        try:
            # Send request to mainframe
            request = f"GET_BALANCE|{account_id:10}".encode()
            conn.send(request)

            # Wait for response with timeout
            response = conn.receive(timeout=self.timeout)

            # Parse response
            if response.startswith(b'ERROR'):
                raise MainframeException(response.decode())

            balance_str = response[6:20].strip().decode()
            return Decimal(balance_str) / 100

        finally:
            self.connection_pool.return_connection(conn)
```

### Pattern 2: Asynchronous Message Queue

For batch operations and non-time-critical work:

```python
class AsynchronousMainframeAdapter:
    """Asynchronous integration using IBM MQ"""

    def __init__(self):
        self.mq_client = MQClient(host='mainframe.internal')
        self.response_listener = ResponseListener()

    def post_transaction_async(self, txn: Transaction) -> str:
        """Post transaction asynchronously via MQ"""

        # Serialize transaction
        message = json.dumps({
            'transaction_id': str(txn.id),
            'from_account': txn.from_account,
            'to_account': txn.to_account,
            'amount': str(txn.amount),
            'description': txn.description
        })

        # Put message in request queue
        request_id = self.mq_client.put_message(
            queue_name='TRANSACTION_REQUESTS',
            message=message,
            correlation_id=str(txn.id)
        )

        # Return transaction ID for polling
        return request_id

    def get_transaction_result(self, transaction_id: str) -> TransactionResult:
        """Poll for transaction result"""

        result = self.response_listener.get_result(
            correlation_id=transaction_id,
            timeout=timedelta(seconds=30)
        )

        if result:
            return TransactionResult(
                status=result['status'],
                mainframe_txn_id=result['txn_id'],
                balance_after=Decimal(result['balance'])
            )
        else:
            return TransactionResult(status='PENDING')
```

### Pattern 3: Scheduled Batch Integration

For end-of-day and periodic synchronization:

```python
class BatchMainframeIntegration:
    """Scheduled batch integration for reconciliation"""

    def __init__(self):
        self.scheduler = APScheduler()
        self.sftp_client = SFTPClient()

    def setup_eod_sync(self):
        """Schedule daily end-of-day synchronization"""

        @self.scheduler.scheduled_job('cron', hour=23, minute=30)
        def sync_eod():
            logger.info("Starting EOD synchronization with mainframe")

            try:
                # 1. Export transactions from modern system
                modern_txns = self._export_modern_transactions()

                # 2. Send via SFTP to mainframe
                self.sftp_client.put_file(
                    local_path='/tmp/transactions.txt',
                    remote_path='/mainframe/incoming/transactions.txt'
                )

                # 3. Wait for mainframe to process
                time.sleep(30)

                # 4. Fetch mainframe EOD report
                self.sftp_client.get_file(
                    remote_path='/mainframe/outgoing/eod_report.txt',
                    local_path='/tmp/eod_report.txt'
                )

                # 5. Reconcile results
                reconciliation = self._reconcile_eod_report()

                if reconciliation['discrepancies']:
                    logger.warning(f"EOD discrepancies: {reconciliation}")
                    self._alert_operations_team(reconciliation)
                else:
                    logger.info("EOD reconciliation successful")

            except Exception as e:
                logger.error(f"EOD sync failed: {e}")
                self._alert_operations_team({'error': str(e)})

    def _export_modern_transactions(self) -> str:
        """Export transactions in mainframe-compatible format"""
        transactions = Transaction.objects.filter(
            created_date=date.today()
        )

        with open('/tmp/transactions.txt', 'w') as f:
            for txn in transactions:
                record = (
                    f"{txn.id:20}"
                    f"{txn.from_account:10}"
                    f"{txn.to_account:10}"
                    f"{int(txn.amount * 100):13}"
                    f"{txn.status:1}"
                    f"\n"
                )
                f.write(record)

        return '/tmp/transactions.txt'

    def _reconcile_eod_report(self):
        """Compare modern and mainframe states"""

        reconciliation = {
            'modern_total': 0,
            'mainframe_total': 0,
            'discrepancies': [],
            'timestamp': datetime.now()
        }

        # Parse mainframe report
        with open('/tmp/eod_report.txt', 'r') as f:
            lines = f.readlines()

        for line in lines:
            account_id = line[0:10].strip()
            mainframe_balance = Decimal(line[10:25]) / 100

            # Get balance from modern system
            account = Account.objects.get(id=account_id)
            modern_balance = account.balance

            if mainframe_balance != modern_balance:
                reconciliation['discrepancies'].append({
                    'account': account_id,
                    'modern': str(modern_balance),
                    'mainframe': str(mainframe_balance),
                    'difference': str(abs(mainframe_balance - modern_balance))
                })

            reconciliation['mainframe_total'] += mainframe_balance
            reconciliation['modern_total'] += modern_balance

        return reconciliation
```

---

## API Gateway Strategies

### Transformation Gateway

```python
from flask import Flask, request
from functools import lru_cache

app = Flask(__name__)

class MainframeGateway:
    """API Gateway for mainframe integration"""

    def __init__(self):
        self.mainframe = MainframeConnector()
        self.transformer = FormatTransformer()
        self.cache = RedisCache()

    @app.route('/api/accounts/<account_id>', methods=['GET'])
    def get_account(self, account_id):
        """Get account details with transformation"""

        # Try cache first
        cached = self.cache.get(f"account:{account_id}")
        if cached:
            return cached

        # Call mainframe
        mainframe_data = self.mainframe.fetch_account(account_id)

        # Transform to modern format
        response = {
            'id': mainframe_data['ACCT_ID'].strip(),
            'name': mainframe_data['ACCT_NAME'].strip(),
            'balance': float(mainframe_data['BALANCE']) / 100,
            'status': self._map_status(mainframe_data['STATUS']),
            'created': self._parse_date(mainframe_data['OPEN_DT']),
            'links': {
                'self': f'/api/accounts/{account_id}',
                'transactions': f'/api/accounts/{account_id}/transactions'
            }
        }

        # Cache result
        self.cache.set(f"account:{account_id}", response, ttl=300)

        return response

    def _map_status(self, legacy_status: str) -> str:
        """Map mainframe status codes to REST conventions"""
        return {
            'A': 'active',
            'I': 'inactive',
            'S': 'suspended',
            'C': 'closed'
        }.get(legacy_status, 'unknown')

    def _parse_date(self, cobol_date: str) -> str:
        """Parse COBOL date format"""
        dt = datetime.strptime(cobol_date, '%Y%m%d')
        return dt.isoformat()
```

---

## Message Queue Integration

### IBM MQ Configuration

```python
import pymq

class IBMMQIntegration:
    """Integration with IBM Message Queue"""

    def __init__(self, host: str, port: int, queue_manager: str):
        self.qmgr = pymq.QueueManager(queue_manager)
        self.qmgr.connect(host, port)

    def send_transaction(self, txn: Transaction):
        """Send transaction to mainframe via MQ"""

        # Prepare message in mainframe format
        message_body = self._format_transaction(txn)

        # Put message in request queue
        self.qmgr.put_message(
            queue_name='BANKING.TRANSACTIONS.REQUEST',
            message_data=message_body,
            message_type=pymq.MQC.MQMT_REQUEST,
            correlation_id=str(txn.id),
            expiry=5 * 60 * 100  # 5 minutes in tenths of second
        )

        # Wait for reply (with timeout)
        try:
            reply = self.qmgr.get_message(
                queue_name='BANKING.TRANSACTIONS.REPLY',
                correlation_id=str(txn.id),
                timeout=10000  # 10 seconds
            )

            return self._parse_reply(reply)

        except pymq.MQException as e:
            if e.reason == pymq.MQC.MQRC_NO_MSG_AVAILABLE:
                raise TimeoutException("Mainframe did not respond in time")
            raise

    def _format_transaction(self, txn: Transaction) -> bytes:
        """Format transaction in mainframe-compatible format"""

        # Create fixed-width record
        record = (
            f"{txn.id:20}"
            f"{txn.from_account:10}"
            f"{txn.to_account:10}"
            f"{int(txn.amount * 100):13}"
            f"{txn.currency:3}"
            f"{txn.description:50}"
        )

        return record.encode('ascii')

    def _parse_reply(self, reply: dict) -> dict:
        """Parse mainframe reply message"""

        return {
            'status': reply['body'][0:1].decode().strip(),
            'mainframe_id': reply['body'][1:20].decode().strip(),
            'balance': int(reply['body'][20:35]) / 100,
            'timestamp': datetime.fromisoformat(
                reply['body'][35:50].decode()
            )
        }
```

---

## Performance Optimization

### Connection Pooling

```python
class MainframeConnectionPool:
    """Manage pool of mainframe connections"""

    def __init__(self, host: str, port: int, min_size: int = 10, max_size: int = 50):
        self.host = host
        self.port = port
        self.min_size = min_size
        self.max_size = max_size
        self.available = queue.Queue(maxsize=max_size)
        self.all_connections = []
        self._initialize_connections()

    def _initialize_connections(self):
        """Pre-create minimum number of connections"""
        for _ in range(self.min_size):
            conn = self._create_connection()
            self.available.put(conn)
            self.all_connections.append(conn)

    def _create_connection(self) -> MainframeConnection:
        """Create new connection to mainframe"""
        conn = MainframeConnection(self.host, self.port)
        conn.connect()
        return conn

    def get_connection(self, timeout: int = 5) -> MainframeConnection:
        """Get available connection from pool"""
        try:
            return self.available.get(timeout=timeout)
        except queue.Empty:
            # Create new connection if available
            if len(self.all_connections) < self.max_size:
                conn = self._create_connection()
                self.all_connections.append(conn)
                return conn
            raise TimeoutException("Connection pool exhausted")

    def return_connection(self, conn: MainframeConnection):
        """Return connection to pool"""
        if conn.is_healthy():
            self.available.put(conn)
        else:
            # Replace unhealthy connection
            self.all_connections.remove(conn)
            new_conn = self._create_connection()
            self.all_connections.append(new_conn)
            self.available.put(new_conn)

    def close_all(self):
        """Close all connections"""
        for conn in self.all_connections:
            conn.close()
```

### Result Caching

```python
class MainframeResultCache:
    """Cache mainframe query results"""

    def __init__(self):
        self.redis = redis.Redis(host='cache-server')
        self.default_ttl = 300  # 5 minutes

    def get_or_fetch(self, key: str, fetch_fn, ttl: int = None) -> dict:
        """Get from cache or fetch from mainframe"""

        # Try cache
        cached = self.redis.get(key)
        if cached:
            self.metrics.increment("cache.hit")
            return json.loads(cached)

        # Fetch from mainframe
        self.metrics.increment("cache.miss")
        result = fetch_fn()

        # Cache result
        ttl = ttl or self.default_ttl
        self.redis.setex(
            key,
            ttl,
            json.dumps(result)
        )

        return result

    def invalidate_related(self, account_id: str):
        """Invalidate cache entries related to account"""
        keys_to_delete = self.redis.keys(f"account:{account_id}:*")
        if keys_to_delete:
            self.redis.delete(*keys_to_delete)
```

---

## Security Considerations

### Authentication to Mainframe

```python
class MainframeAuthentication:
    """Secure authentication to mainframe systems"""

    def __init__(self):
        self.vault = HashicorpVault()

    def get_credentials(self) -> tuple:
        """Retrieve mainframe credentials from vault"""
        credentials = self.vault.get_secret(
            path='secret/mainframe/credentials'
        )
        return credentials['username'], credentials['password']

    def authenticate(self, username: str, password: str) -> MainframeSession:
        """Authenticate with mainframe"""

        session = MainframeConnection()

        try:
            session.connect(
                username=username,
                password=password,
                kerberos=True  # Use Kerberos for enterprise security
            )

            # Verify connection
            session.ping()

            return session

        except AuthenticationException as e:
            logger.error(f"Mainframe authentication failed: {e}")
            raise
```

### Data Encryption

```python
class MainframeDataEncryption:
    """Encrypt sensitive data in transit and at rest"""

    def __init__(self):
        self.cipher = AES.new(key=get_encryption_key(), mode=AES.MODE_GCM)

    def encrypt_transaction(self, txn: Transaction) -> bytes:
        """Encrypt transaction data before sending to mainframe"""

        plaintext = json.dumps({
            'from_account': txn.from_account,
            'to_account': txn.to_account,
            'amount': str(txn.amount)
        })

        ciphertext, tag = self.cipher.encrypt_and_digest(
            plaintext.encode()
        )

        return json.dumps({
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'tag': base64.b64encode(tag).decode(),
            'nonce': base64.b64encode(self.cipher.nonce).decode()
        })

    def decrypt_response(self, encrypted: dict) -> dict:
        """Decrypt response from mainframe"""

        ciphertext = base64.b64decode(encrypted['ciphertext'])
        tag = base64.b64decode(encrypted['tag'])
        nonce = base64.b64decode(encrypted['nonce'])

        cipher = AES.new(key=get_encryption_key(), mode=AES.MODE_GCM, nonce=nonce)

        plaintext = cipher.decrypt_and_verify(ciphertext, tag)

        return json.loads(plaintext.decode())
```

---

## Case Studies

### Case Study 1: Federal Reserve Wire Processing

**Background**:
- 40+ year old Fedwire-compatible mainframe system
- Processes $6+ trillion daily
- Real-time settlement requirements

**Integration Approach**:
- Synchronous request-response for wire initiation
- Mainframe-to-mainframe communication for settlement
- Daily reconciliation batch for validation

**Results**:
- Zero downtime in 3 years of operation
- Sub-100ms latency for wire lookups (cached)
- 100% accuracy in settlement

### Case Study 2: International Trade Finance

**Background**:
- Multi-decade COBOL-based letter of credit system
- Complex document imaging and validation
- Regulatory audit requirements

**Solution**:
- Created REST API wrapper around COBOL services
- Asynchronous processing via IBM MQ
- Event-driven architecture for status updates

**Results**:
- Reduced LC processing time from 2 days to 2 hours
- 95% automation rate for standard documents
- Better audit trail through event logging

---

## Conclusion

Successfully integrating with mainframe systems requires understanding their unique characteristics and constraints. Key takeaways:

1. **Don't fight the mainframe architecture** - accept its synchronous, batch-oriented nature
2. **Invest in translation layers** - proper format conversion prevents data corruption
3. **Use appropriate patterns** - synchronous for real-time, asynchronous for batch
4. **Implement comprehensive monitoring** - visibility into both systems is critical
5. **Security first** - mainframe systems often handle sensitive financial data

Mainframe integration is not about replacing the mainframe, but rather about creating modern interfaces to legacy assets.

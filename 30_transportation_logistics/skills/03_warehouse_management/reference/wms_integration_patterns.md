# WMS Integration Patterns and Best Practices

## Overview

This document provides comprehensive guidance on integrating Warehouse Management Systems (WMS) with enterprise systems including ERP, TMS, OMS, and e-commerce platforms.

## Table of Contents

1. [Integration Architecture](#integration-architecture)
2. [Common Integration Patterns](#common-integration-patterns)
3. [Data Synchronization Strategies](#data-synchronization-strategies)
4. [Error Handling and Recovery](#error-handling-and-recovery)
5. [Performance Optimization](#performance-optimization)
6. [Security Considerations](#security-considerations)

---

## Integration Architecture

### Hub-and-Spoke Model

```
┌──────────────┐
│     ERP      │
│   (SAP/Oracle│
│    /NetSuite)│
└──────┬───────┘
       │
       │ Master Data, Orders, Inventory
       ▼
┌─────────────────────────────────────┐
│   Integration Layer (Middleware)    │
│   • MuleSoft / Dell Boomi / Custom │
│   • Message Queue (RabbitMQ/Kafka) │
│   • API Gateway                     │
└─────────────┬───────────────────────┘
              │
    ┌─────────┼─────────┬─────────────┐
    │         │         │             │
    ▼         ▼         ▼             ▼
┌────────┐ ┌─────┐  ┌──────┐    ┌─────────┐
│  WMS   │ │ TMS │  │ OMS  │    │E-commerce│
└────────┘ └─────┘  └──────┘    └─────────┘
```

**Benefits**:
- Centralized integration logic
- Easier to add new systems
- Better monitoring and error handling
- Consistent data transformation

**Challenges**:
- Single point of failure (mitigated with redundancy)
- Additional infrastructure cost
- Learning curve for middleware platform

### Point-to-Point Integration

```
┌──────┐ ←→ ┌─────┐
│ ERP  │    │ WMS │
└──────┘    └──┬──┘
               ↕
            ┌─────┐
            │ TMS │
            └──┬──┘
               ↕
            ┌──────┐
            │ OMS  │
            └──────┘
```

**When to Use**:
- Small operations (<3 systems)
- Simple data flows
- Budget constraints
- Quick initial implementation

---

## Common Integration Patterns

### 1. Order Fulfillment Flow

#### ERP → WMS Order Creation

**Data Flow**:
```
ERP creates sales order
    ↓
Order sent to WMS
    ↓
WMS creates fulfillment task
    ↓
WMS sends confirmation to ERP
```

**Integration Points**:

| Event | Direction | Data Elements | Frequency |
|-------|-----------|---------------|-----------|
| Order Creation | ERP → WMS | Order #, SKUs, quantities, customer, ship-to address, delivery date | Real-time |
| Order Acknowledgment | WMS → ERP | WMS order #, expected ship date, allocated inventory | Real-time |
| Pick Completion | WMS → ERP | Picked quantities, picker ID, timestamp | Real-time |
| Ship Confirmation | WMS → TMS/ERP | Shipment #, carrier, tracking #, BOL, weights/dims | Real-time |
| Invoice Trigger | WMS → ERP | Shipped quantities, actual weights/dims, lot/serial numbers | Real-time |

**Sample API Payload** (WMS Order Creation):

```json
{
  "order_id": "SO-2025-00123",
  "external_order_id": "ERP-ORDER-456",
  "order_type": "standard",
  "priority": 1,
  "customer": {
    "id": "CUST-001",
    "name": "Acme Corporation",
    "account_number": "ACC-12345"
  },
  "ship_to": {
    "name": "Acme Warehouse",
    "address": "123 Main St",
    "city": "Chicago",
    "state": "IL",
    "zip": "60601",
    "country": "US"
  },
  "requested_ship_date": "2025-01-25",
  "required_delivery_date": "2025-01-27",
  "carrier": "UPS",
  "service_level": "Ground",
  "lines": [
    {
      "line_number": 1,
      "sku": "WIDGET-001",
      "description": "Widget Type A",
      "quantity_ordered": 100,
      "uom": "EA",
      "lot_control": true,
      "serial_control": false
    },
    {
      "line_number": 2,
      "sku": "GADGET-002",
      "description": "Gadget Type B",
      "quantity_ordered": 50,
      "uom": "EA",
      "lot_control": false,
      "serial_control": true
    }
  ],
  "special_instructions": "Fragile - handle with care"
}
```

**Response**:

```json
{
  "wms_order_id": "WMS-202501-9876",
  "external_order_id": "SO-2025-00123",
  "status": "accepted",
  "estimated_ship_date": "2025-01-25",
  "allocated_from_warehouse": "WH-001",
  "lines": [
    {
      "line_number": 1,
      "sku": "WIDGET-001",
      "quantity_allocated": 100,
      "available_inventory": 1250,
      "allocated_lots": ["LOT-20250115-A"]
    },
    {
      "line_number": 2,
      "sku": "GADGET-002",
      "quantity_allocated": 50,
      "available_inventory": 200,
      "allocated_serial_numbers": ["SN001", "SN002", "..."]
    }
  ],
  "warnings": [],
  "timestamp": "2025-01-24T10:30:00Z"
}
```

### 2. Inventory Synchronization

#### Real-Time Inventory Updates

**Pattern**: Event-Driven Updates

```python
# WMS publishes inventory change events
import json
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_inventory_update(warehouse_id, sku, transaction_type, quantity, location):
    """
    Publish inventory transaction to event stream.
    Consumers (ERP, OMS, etc.) subscribe and update their records.
    """
    event = {
        "event_type": "inventory.transaction",
        "event_id": generate_uuid(),
        "timestamp": get_current_timestamp(),
        "warehouse_id": warehouse_id,
        "sku": sku,
        "transaction_type": transaction_type,  # receipt, pick, adjustment, etc.
        "quantity": quantity,
        "location": location,
        "lot_number": get_lot_number(),
        "reason_code": get_reason_code(),
        "user_id": get_current_user()
    }

    producer.send('inventory.transactions', value=event, key=sku.encode('utf-8'))
    producer.flush()

# Example usage
publish_inventory_update(
    warehouse_id="WH-001",
    sku="WIDGET-001",
    transaction_type="pick",
    quantity=-100,
    location="A01-02-03"
)
```

**Pattern**: Periodic Batch Sync

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

class InventorySyncService:
    """
    Periodic inventory synchronization service.
    Runs every 15 minutes to sync inventory levels.
    """

    def __init__(self, wms_api, erp_api):
        self.wms_api = wms_api
        self.erp_api = erp_api
        self.scheduler = AsyncIOScheduler()

    def start(self):
        # Sync every 15 minutes
        self.scheduler.add_job(
            self.sync_inventory,
            'interval',
            minutes=15
        )
        self.scheduler.start()

    async def sync_inventory(self):
        """Synchronize inventory between WMS and ERP"""
        print(f"Starting inventory sync at {datetime.now()}")

        # Fetch all inventory from WMS
        wms_inventory = await self.wms_api.get_inventory_snapshot()

        # Aggregate by SKU
        aggregated = {}
        for item in wms_inventory:
            sku = item['sku']
            if sku not in aggregated:
                aggregated[sku] = {
                    'sku': sku,
                    'available': 0,
                    'allocated': 0,
                    'on_hold': 0
                }

            aggregated[sku]['available'] += item['available_quantity']
            aggregated[sku]['allocated'] += item['allocated_quantity']
            aggregated[sku]['on_hold'] += item['on_hold_quantity']

        # Send to ERP
        for sku, quantities in aggregated.items():
            await self.erp_api.update_inventory(
                sku=sku,
                warehouse='WH-001',
                on_hand=quantities['available'] + quantities['allocated'] + quantities['on_hold'],
                available=quantities['available']
            )

        print(f"Inventory sync completed: {len(aggregated)} SKUs updated")
```

### 3. Receiving and Put-Away

#### ASN (Advanced Ship Notice) Integration

**Flow**:
```
Supplier sends ASN to ERP
    ↓
ERP forwards ASN to WMS
    ↓
WMS creates expected receipt
    ↓
Truck arrives, receiving process begins
    ↓
WMS confirms receipt back to ERP
    ↓
ERP updates inventory and triggers AP workflow
```

**ASN Message Format**:

```xml
<?xml version="1.0"?>
<ASN>
  <ASNHeader>
    <ASNNumber>ASN-2025-00456</ASNNumber>
    <PurchaseOrder>PO-2025-00123</PurchaseOrder>
    <ShipDate>2025-01-24</ShipDate>
    <ExpectedDeliveryDate>2025-01-25</ExpectedDeliveryDate>
    <Carrier>FedEx Freight</Carrier>
    <TrackingNumber>123456789</TrackingNumber>
  </ASNHeader>
  <ShipTo>
    <WarehouseID>WH-001</WarehouseID>
    <Address>
      <Line1>123 Warehouse Blvd</Line1>
      <City>Dallas</City>
      <State>TX</State>
      <Zip>75001</Zip>
    </Address>
  </ShipTo>
  <Lines>
    <Line>
      <LineNumber>1</LineNumber>
      <SKU>WIDGET-001</SKU>
      <Description>Widget Type A</Description>
      <QuantityShipped>500</QuantityShipped>
      <UOM>EA</UOM>
      <PackagingType>Pallet</PackagingType>
      <PalletsShipped>2</PalletsShipped>
      <LotNumber>LOT-20250120-B</LotNumber>
      <ExpirationDate>2026-01-20</ExpirationDate>
    </Line>
    <Line>
      <LineNumber>2</LineNumber>
      <SKU>GADGET-002</SKU>
      <Description>Gadget Type B</Description>
      <QuantityShipped>200</QuantityShipped>
      <UOM>EA</UOM>
      <PackagingType>Carton</PackagingType>
      <CartonsShipped>10</CartonsShipped>
      <SerialNumbers>
        <Serial>SN1001</Serial>
        <Serial>SN1002</Serial>
        <!-- ... -->
      </SerialNumbers>
    </Line>
  </Lines>
</ASN>
```

**Receipt Confirmation**:

```json
{
  "receipt_id": "RCV-2025-00789",
  "asn_number": "ASN-2025-00456",
  "purchase_order": "PO-2025-00123",
  "warehouse_id": "WH-001",
  "receipt_date": "2025-01-25T08:45:00Z",
  "receiver_name": "John Smith",
  "status": "completed",
  "lines": [
    {
      "line_number": 1,
      "sku": "WIDGET-001",
      "quantity_expected": 500,
      "quantity_received": 500,
      "quantity_accepted": 495,
      "quantity_rejected": 5,
      "rejection_reason": "damaged",
      "lot_number": "LOT-20250120-B",
      "expiration_date": "2026-01-20",
      "put_away_location": "A05-10-02"
    },
    {
      "line_number": 2,
      "sku": "GADGET-002",
      "quantity_expected": 200,
      "quantity_received": 200,
      "quantity_accepted": 200,
      "quantity_rejected": 0,
      "serial_numbers_received": ["SN1001", "SN1002", "..."],
      "put_away_location": "B03-05-03"
    }
  ],
  "variances": [
    {
      "line_number": 1,
      "sku": "WIDGET-001",
      "variance_type": "damage",
      "quantity": 5,
      "notes": "Corner damage on 1 pallet"
    }
  ]
}
```

### 4. Shipping Integration (WMS → TMS)

#### Shipment Notification Flow

```python
import requests
from typing import List, Dict

class TMSIntegration:
    """Integration with Transportation Management System"""

    def __init__(self, tms_base_url: str, api_key: str):
        self.base_url = tms_base_url
        self.api_key = api_key

    def create_shipment(self, wms_order: Dict) -> Dict:
        """
        Create shipment in TMS when order is packed and ready to ship.
        """
        shipment_request = {
            "shipment_id": f"SHIP-{wms_order['order_id']}",
            "origin": {
                "warehouse_id": wms_order['warehouse_id'],
                "name": "Distribution Center 1",
                "address": {
                    "line1": "123 Warehouse Blvd",
                    "city": "Dallas",
                    "state": "TX",
                    "zip": "75001",
                    "country": "US"
                },
                "contact": {
                    "name": "Shipping Department",
                    "phone": "214-555-0100",
                    "email": "shipping@company.com"
                }
            },
            "destination": wms_order['ship_to'],
            "service_level": wms_order['service_level'],
            "pieces": self._extract_pieces(wms_order),
            "total_weight": wms_order['total_weight'],
            "declared_value": wms_order['total_value'],
            "reference_numbers": {
                "order_number": wms_order['order_id'],
                "customer_po": wms_order.get('customer_po'),
                "invoice_number": wms_order.get('invoice_number')
            },
            "special_services": wms_order.get('special_services', []),
            "requested_pickup_date": wms_order['ship_date'],
            "required_delivery_date": wms_order.get('required_delivery_date')
        }

        # Call TMS API
        response = requests.post(
            f"{self.base_url}/api/v1/shipments",
            json=shipment_request,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30
        )

        response.raise_for_status()
        return response.json()

    def get_tracking_info(self, shipment_id: str) -> Dict:
        """Get tracking information from TMS"""
        response = requests.get(
            f"{self.base_url}/api/v1/shipments/{shipment_id}/tracking",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=15
        )

        response.raise_for_status()
        return response.json()

    def _extract_pieces(self, wms_order: Dict) -> List[Dict]:
        """Extract package information from WMS order"""
        pieces = []

        for package in wms_order.get('packages', []):
            pieces.append({
                "package_id": package['package_id'],
                "type": package['package_type'],  # box, pallet, etc.
                "weight": {
                    "value": package['weight'],
                    "unit": "LBS"
                },
                "dimensions": {
                    "length": package['length'],
                    "width": package['width'],
                    "height": package['height'],
                    "unit": "IN"
                },
                "contents": package.get('contents', [])
            })

        return pieces
```

---

## Data Synchronization Strategies

### Master Data Management

**Product Master Data Sync**:

| Field | Source of Truth | Sync Direction | Frequency |
|-------|----------------|----------------|-----------|
| SKU | ERP | ERP → WMS | Real-time |
| Description | ERP | ERP → WMS | Real-time |
| Dimensions (L/W/H) | WMS | WMS → ERP | On update |
| Weight | WMS | WMS → ERP | On update |
| Lot Control Required | ERP | ERP → WMS | Real-time |
| Serial Control Required | ERP | ERP → WMS | Real-time |
| ABC Classification | WMS | WMS → ERP | Daily batch |
| Hazmat Indicators | ERP | ERP → WMS | Real-time |
| Storage Requirements | Both | Bidirectional | On update |

**Customer Master Data Sync**:

```python
class CustomerMasterSync:
    """Synchronize customer master data between ERP and WMS"""

    def sync_customer(self, customer_id: str):
        """
        Sync customer from ERP to WMS.
        Includes: addresses, special requirements, service levels
        """
        # Fetch from ERP
        erp_customer = self.erp_api.get_customer(customer_id)

        # Transform to WMS format
        wms_customer = {
            "customer_id": erp_customer['customer_number'],
            "name": erp_customer['name'],
            "default_carrier": erp_customer['preferred_carrier'],
            "default_service_level": erp_customer['default_service_level'],
            "addresses": [
                {
                    "address_id": addr['id'],
                    "type": addr['type'],  # ship_to, bill_to
                    "is_default": addr['is_default'],
                    "name": addr['name'],
                    "address_line1": addr['line1'],
                    "address_line2": addr.get('line2'),
                    "city": addr['city'],
                    "state": addr['state'],
                    "zip": addr['zip'],
                    "country": addr['country'],
                    "contact_name": addr.get('contact_name'),
                    "phone": addr.get('phone'),
                    "email": addr.get('email'),
                    "delivery_instructions": addr.get('delivery_instructions')
                }
                for addr in erp_customer.get('addresses', [])
            ],
            "special_instructions": erp_customer.get('shipping_instructions'),
            "requires_appointment": erp_customer.get('requires_appointment', False),
            "hazmat_certified": erp_customer.get('hazmat_certified', False)
        }

        # Send to WMS
        self.wms_api.upsert_customer(wms_customer)
```

---

## Error Handling and Recovery

### Retry Logic with Exponential Backoff

```python
import time
import requests
from functools import wraps

def retry_with_exponential_backoff(max_retries=5, base_delay=1.0):
    """Decorator for retrying API calls with exponential backoff"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        # Last attempt failed
                        raise

                    # Exponential backoff: 1s, 2s, 4s, 8s, 16s
                    delay = base_delay * (2 ** attempt)
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)

        return wrapper

    return decorator

# Usage
@retry_with_exponential_backoff(max_retries=5)
def send_order_to_wms(order_data):
    response = requests.post(
        "https://wms-api.example.com/orders",
        json=order_data,
        timeout=30
    )
    response.raise_for_status()
    return response.json()
```

### Dead Letter Queue Pattern

```python
from kafka import KafkaConsumer, KafkaProducer
import json

class ResilientMessageProcessor:
    """Process messages with dead letter queue for failures"""

    def __init__(self):
        self.consumer = KafkaConsumer(
            'wms.orders.incoming',
            bootstrap_servers=['kafka:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

        self.dlq_producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        self.max_retries = 3

    def process_messages(self):
        for message in self.consumer:
            order_data = message.value
            retry_count = order_data.get('_retry_count', 0)

            try:
                # Process order
                self.create_wms_order(order_data)

            except Exception as e:
                print(f"Error processing order {order_data.get('order_id')}: {e}")

                if retry_count < self.max_retries:
                    # Retry
                    order_data['_retry_count'] = retry_count + 1
                    order_data['_last_error'] = str(e)

                    # Send back to queue for retry
                    self.dlq_producer.send(
                        'wms.orders.retry',
                        value=order_data
                    )
                else:
                    # Max retries exceeded - send to DLQ
                    order_data['_final_error'] = str(e)
                    order_data['_failed_timestamp'] = datetime.now().isoformat()

                    self.dlq_producer.send(
                        'wms.orders.dead_letter',
                        value=order_data
                    )

                    # Alert operations team
                    self.send_alert(order_data, e)
```

---

## Performance Optimization

### Batch Processing

```python
class BatchProcessor:
    """Batch multiple operations for efficiency"""

    def __init__(self, batch_size=100, flush_interval=5):
        self.batch_size = batch_size
        self.flush_interval = flush_interval  # seconds
        self.inventory_updates = []
        self.last_flush = time.time()

    def add_inventory_update(self, update):
        """Add inventory update to batch"""
        self.inventory_updates.append(update)

        # Flush if batch is full or interval elapsed
        if (len(self.inventory_updates) >= self.batch_size or
            time.time() - self.last_flush > self.flush_interval):
            self.flush()

    def flush(self):
        """Send batched updates to ERP"""
        if not self.inventory_updates:
            return

        try:
            # Send batch to ERP
            response = self.erp_api.batch_update_inventory(
                updates=self.inventory_updates
            )

            print(f"Flushed {len(self.inventory_updates)} inventory updates")

            # Clear batch
            self.inventory_updates = []
            self.last_flush = time.time()

        except Exception as e:
            print(f"Error flushing batch: {e}")
            # Implement error handling (retry, DLQ, etc.)
```

### Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class APIClient:
    """HTTP client with connection pooling and retries"""

    def __init__(self, base_url):
        self.base_url = base_url
        self.session = self._create_session()

    def _create_session(self):
        """Create session with connection pooling and retry logic"""
        session = requests.Session()

        # Retry configuration
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE"],
            backoff_factor=1  # 1s, 2s, 4s
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,  # Number of connection pools
            pool_maxsize=20  # Connections per pool
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def post(self, endpoint, data):
        """POST request with connection pooling"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
```

---

## Security Considerations

### API Authentication

**OAuth 2.0 Client Credentials Flow**:

```python
import requests
from datetime import datetime, timedelta

class SecureAPIClient:
    """API client with OAuth 2.0 authentication"""

    def __init__(self, base_url, client_id, client_secret, token_url):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url

        self.access_token = None
        self.token_expires_at = None

    def _get_access_token(self):
        """Obtain OAuth access token"""
        if self.access_token and datetime.now() < self.token_expires_at:
            return self.access_token

        # Request new token
        response = requests.post(
            self.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "wms:read wms:write"
            }
        )

        response.raise_for_status()
        token_data = response.json()

        self.access_token = token_data['access_token']
        expires_in = token_data['expires_in']  # seconds
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)

        return self.access_token

    def post(self, endpoint, data):
        """Authenticated POST request"""
        token = self._get_access_token()

        response = requests.post(
            f"{self.base_url}{endpoint}",
            json=data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )

        response.raise_for_status()
        return response.json()
```

### Data Encryption

```python
from cryptography.fernet import Fernet
import base64

class DataEncryption:
    """Encrypt sensitive data in transit and at rest"""

    def __init__(self, encryption_key):
        self.cipher = Fernet(encryption_key)

    def encrypt_sensitive_fields(self, data):
        """Encrypt sensitive fields in data"""
        sensitive_fields = ['ssn', 'credit_card', 'bank_account']

        for field in sensitive_fields:
            if field in data and data[field]:
                encrypted = self.cipher.encrypt(data[field].encode())
                data[field] = base64.b64encode(encrypted).decode()

        return data

    def decrypt_sensitive_fields(self, data):
        """Decrypt sensitive fields"""
        sensitive_fields = ['ssn', 'credit_card', 'bank_account']

        for field in sensitive_fields:
            if field in data and data[field]:
                decoded = base64.b64decode(data[field])
                decrypted = self.cipher.decrypt(decoded).decode()
                data[field] = decrypted

        return data
```

---

## Conclusion

Successful WMS integration requires careful planning, robust error handling, and attention to performance and security. The patterns and examples in this document provide a foundation for building reliable, scalable integrations that support modern warehouse operations.

### Key Takeaways

1. **Use Middleware**: For complex integrations, invest in an integration platform
2. **Design for Failure**: Implement retries, circuit breakers, and dead letter queues
3. **Batch When Possible**: Reduce API calls through intelligent batching
4. **Monitor Everything**: Track integration health, latency, and errors
5. **Secure by Default**: Use OAuth, encrypt sensitive data, implement rate limiting
6. **Document Thoroughly**: Maintain clear documentation of data flows and transformations

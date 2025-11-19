# OSS/BSS Integration Expert

You are an expert in Operations Support Systems (OSS) and Business Support Systems (BSS) integration for telecommunications.

## Core Competencies

### OSS Systems
- **Network Inventory Management**: Physical and logical resource inventory
- **Service Fulfillment**: Order management, provisioning automation
- **Service Assurance**: Fault management, performance monitoring, SLA management
- **Network Planning**: Capacity planning, network optimization

### BSS Systems
- **Product Catalog**: Service offerings, pricing, bundles
- **Order Management**: Order capture, orchestration, fulfillment
- **Customer Management**: CRM, customer profiles, preferences
- **Billing & Revenue**: Invoicing, payments, revenue assurance

### Integration Patterns
- **TM Forum APIs**: Open APIs (TMF640-689)
- **Service Orchestration**: End-to-end service automation
- **Data Synchronization**: Real-time and batch integration
- **Event-Driven Architecture**: Kafka, event streams

### Standards & Frameworks
- **TM Forum Frameworx**: eTOM, SID, TAM
- **NGOSS**: Next Generation OSS
- **MEF**: Metro Ethernet Forum standards
- **3GPP**: Mobile network standards

## Implementation Examples

### TM Forum Product Ordering API (TMF622)

```python
#!/usr/bin/env python3
"""
TM Forum Product Ordering API Implementation
Handles service order lifecycle from creation to fulfillment
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
import uuid


class ProductOrderState(Enum):
    """Product Order States per TMF622"""
    ACKNOWLEDGED = "acknowledged"
    REJECTED = "rejected"
    PENDING = "pending"
    HELD = "held"
    IN_PROGRESS = "inProgress"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
    ASSESSED_CUSTOMER_APPROVE = "assessedCustomerApprove"


class ProductActionType(Enum):
    """Product order action types"""
    ADD = "add"
    MODIFY = "modify"
    DELETE = "delete"
    NO_CHANGE = "noChange"


@dataclass
class ProductOfferingRef:
    """Reference to a product offering from catalog"""
    id: str
    name: str
    href: Optional[str] = None


@dataclass
class ProductSpecificationRef:
    """Reference to product specification"""
    id: str
    name: str
    version: str
    href: Optional[str] = None


@dataclass
class ProductCharacteristic:
    """Product characteristic (key-value pair)"""
    name: str
    value: str
    value_type: Optional[str] = None


@dataclass
class ProductOrderItem:
    """Product order item (line item in the order)"""
    id: str
    action: ProductActionType
    product_offering: ProductOfferingRef
    product: Optional[Dict] = None
    product_characteristic: List[ProductCharacteristic] = field(default_factory=list)
    appointment: Optional[Dict] = None
    billing_account: Optional[str] = None
    quantity: int = 1
    state: ProductOrderState = ProductOrderState.ACKNOWLEDGED

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "action": self.action.value,
            "productOffering": {
                "id": self.product_offering.id,
                "name": self.product_offering.name
            },
            "productCharacteristic": [
                {
                    "name": char.name,
                    "value": char.value
                } for char in self.product_characteristic
            ],
            "quantity": self.quantity,
            "state": self.state.value
        }


@dataclass
class ProductOrder:
    """TMF622 Product Order"""
    id: str
    href: str
    external_id: Optional[str]
    priority: str
    description: str
    category: str
    state: ProductOrderState
    order_date: datetime
    completion_date: Optional[datetime]
    requested_start_date: Optional[datetime]
    requested_completion_date: Optional[datetime]
    expected_completion_date: Optional[datetime]
    customer_id: str
    product_order_item: List[ProductOrderItem] = field(default_factory=list)
    related_party: List[Dict] = field(default_factory=list)
    note: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to TMF622 JSON representation"""
        return {
            "id": self.id,
            "href": self.href,
            "externalId": self.external_id,
            "priority": self.priority,
            "description": self.description,
            "category": self.category,
            "state": self.state.value,
            "orderDate": self.order_date.isoformat(),
            "completionDate": self.completion_date.isoformat() if self.completion_date else None,
            "requestedStartDate": self.requested_start_date.isoformat() if self.requested_start_date else None,
            "requestedCompletionDate": self.requested_completion_date.isoformat() if self.requested_completion_date else None,
            "expectedCompletionDate": self.expected_completion_date.isoformat() if self.expected_completion_date else None,
            "relatedParty": [
                {
                    "id": self.customer_id,
                    "role": "customer",
                    "name": "Customer"
                }
            ],
            "productOrderItem": [item.to_dict() for item in self.product_order_item],
            "note": self.note
        }


class ProductOrderingAPI:
    """TMF622 Product Ordering API Implementation"""

    def __init__(self):
        self.orders: Dict[str, ProductOrder] = {}
        self.provisioning_engine = ProvisioningEngine()

    def create_product_order(self, order_request: Dict) -> ProductOrder:
        """
        Create a new product order (POST /productOrder)

        Args:
            order_request: Order request payload

        Returns:
            Created product order
        """

        order_id = str(uuid.uuid4())
        order_date = datetime.now()

        # Parse order items
        order_items = []
        for item_data in order_request.get("productOrderItem", []):
            # Create product order item
            offering_ref = ProductOfferingRef(
                id=item_data["productOffering"]["id"],
                name=item_data["productOffering"]["name"]
            )

            characteristics = [
                ProductCharacteristic(
                    name=char["name"],
                    value=char["value"]
                ) for char in item_data.get("productCharacteristic", [])
            ]

            order_item = ProductOrderItem(
                id=item_data.get("id", str(uuid.uuid4())),
                action=ProductActionType(item_data["action"]),
                product_offering=offering_ref,
                product_characteristic=characteristics,
                quantity=item_data.get("quantity", 1),
                state=ProductOrderState.ACKNOWLEDGED
            )

            order_items.append(order_item)

        # Create product order
        product_order = ProductOrder(
            id=order_id,
            href=f"/productOrderingManagement/v4/productOrder/{order_id}",
            external_id=order_request.get("externalId"),
            priority=order_request.get("priority", "normal"),
            description=order_request.get("description", ""),
            category=order_request.get("category", "mobile"),
            state=ProductOrderState.ACKNOWLEDGED,
            order_date=order_date,
            completion_date=None,
            requested_start_date=datetime.fromisoformat(order_request["requestedStartDate"]) if "requestedStartDate" in order_request else None,
            requested_completion_date=datetime.fromisoformat(order_request["requestedCompletionDate"]) if "requestedCompletionDate" in order_request else None,
            expected_completion_date=None,
            customer_id=order_request["relatedParty"][0]["id"],
            product_order_item=order_items
        )

        # Store order
        self.orders[order_id] = product_order

        # Trigger fulfillment process
        self.provisioning_engine.provision_order(product_order)

        return product_order

    def get_product_order(self, order_id: str) -> Optional[ProductOrder]:
        """Get product order by ID (GET /productOrder/{id})"""
        return self.orders.get(order_id)

    def list_product_orders(self, filters: Optional[Dict] = None) -> List[ProductOrder]:
        """List product orders with optional filters (GET /productOrder)"""
        orders = list(self.orders.values())

        if filters:
            # Apply filters
            if "state" in filters:
                orders = [o for o in orders if o.state.value == filters["state"]]
            if "customerId" in filters:
                orders = [o for o in orders if o.customer_id == filters["customerId"]]

        return orders

    def patch_product_order(self, order_id: str, updates: Dict) -> Optional[ProductOrder]:
        """
        Partially update product order (PATCH /productOrder/{id})
        Used for state transitions
        """
        order = self.orders.get(order_id)
        if not order:
            return None

        # Update fields
        if "state" in updates:
            order.state = ProductOrderState(updates["state"])
        if "note" in updates:
            order.note.append(updates["note"])

        return order

    def cancel_product_order(self, order_id: str, cancellation_reason: str) -> bool:
        """Cancel a product order"""
        order = self.orders.get(order_id)
        if not order:
            return False

        if order.state not in [ProductOrderState.COMPLETED, ProductOrderState.CANCELLED]:
            order.state = ProductOrderState.CANCELLED
            order.note.append({
                "date": datetime.now().isoformat(),
                "author": "system",
                "text": f"Order cancelled: {cancellation_reason}"
            })
            return True

        return False


class ProvisioningEngine:
    """Service provisioning orchestration engine"""

    def __init__(self):
        self.tasks: List[Dict] = []

    def provision_order(self, order: ProductOrder):
        """
        Orchestrate service provisioning for product order

        Provisioning workflow:
        1. Validate resources
        2. Reserve resources
        3. Configure network elements
        4. Activate services
        5. Update inventory
        6. Notify billing system
        """

        print(f"Starting provisioning for order {order.id}")

        for item in order.product_order_item:
            if item.action == ProductActionType.ADD:
                self._provision_new_service(order, item)
            elif item.action == ProductActionType.MODIFY:
                self._modify_existing_service(order, item)
            elif item.action == ProductActionType.DELETE:
                self._deactivate_service(order, item)

    def _provision_new_service(self, order: ProductOrder, item: ProductOrderItem):
        """Provision new service"""

        # Step 1: Reserve resources (inventory check)
        resource_available = self._check_resource_availability(item)
        if not resource_available:
            item.state = ProductOrderState.FAILED
            return

        # Step 2: Configure network elements
        config_success = self._configure_network_elements(item)
        if not config_success:
            item.state = ProductOrderState.FAILED
            return

        # Step 3: Activate service
        activation_success = self._activate_service(item)
        if not activation_success:
            item.state = ProductOrderState.FAILED
            return

        # Step 4: Update inventory
        self._update_inventory(item)

        # Step 5: Notify billing system
        self._notify_billing_system(order, item)

        # Update state
        item.state = ProductOrderState.COMPLETED
        print(f"Service provisioned successfully: {item.id}")

    def _modify_existing_service(self, order: ProductOrder, item: ProductOrderItem):
        """Modify existing service"""
        print(f"Modifying service: {item.id}")
        # Implementation details...
        item.state = ProductOrderState.COMPLETED

    def _deactivate_service(self, order: ProductOrder, item: ProductOrderItem):
        """Deactivate service"""
        print(f"Deactivating service: {item.id}")
        # Implementation details...
        item.state = ProductOrderState.COMPLETED

    def _check_resource_availability(self, item: ProductOrderItem) -> bool:
        """Check if required resources are available"""
        # In production: Query inventory management system
        return True

    def _configure_network_elements(self, item: ProductOrderItem) -> bool:
        """Configure network elements (HSS, MME, PGW, etc.)"""
        # In production: Call OSS provisioning APIs
        print(f"Configuring network elements for {item.product_offering.name}")
        return True

    def _activate_service(self, item: ProductOrderItem) -> bool:
        """Activate service on the network"""
        # In production: Trigger activation workflows
        print(f"Activating service: {item.product_offering.name}")
        return True

    def _update_inventory(self, item: ProductOrderItem):
        """Update resource inventory"""
        # In production: Update inventory management system
        print(f"Updating inventory for {item.id}")

    def _notify_billing_system(self, order: ProductOrder, item: ProductOrderItem):
        """Notify billing system of new service"""
        # In production: Send event to billing system
        print(f"Notifying billing system for customer {order.customer_id}")


# Example usage
if __name__ == "__main__":
    api = ProductOrderingAPI()

    # Create a new mobile service order
    order_request = {
        "externalId": "CRM-ORDER-12345",
        "priority": "normal",
        "description": "New 5G mobile service activation",
        "category": "mobile",
        "requestedStartDate": datetime.now().isoformat(),
        "relatedParty": [
            {
                "id": "CUST-001",
                "role": "customer",
                "name": "John Doe"
            }
        ],
        "productOrderItem": [
            {
                "id": "1",
                "action": "add",
                "productOffering": {
                    "id": "5G-UNLIMITED-PLAN",
                    "name": "5G Unlimited Plan"
                },
                "productCharacteristic": [
                    {"name": "msisdn", "value": "310-410-1234"},
                    {"name": "imsi", "value": "310410123456789"},
                    {"name": "data_quota_gb", "value": "100"},
                    {"name": "voice_minutes", "value": "unlimited"}
                ],
                "quantity": 1
            }
        ]
    }

    # Create order
    order = api.create_product_order(order_request)
    print(f"Order created: {order.id}")
    print(f"State: {order.state.value}")

    # Retrieve order
    retrieved_order = api.get_product_order(order.id)
    print(f"\nRetrieved order: {retrieved_order.to_dict()}")

    # List all orders
    all_orders = api.list_product_orders()
    print(f"\nTotal orders: {len(all_orders)}")
```

## Integration Patterns

### Event-Driven Integration
```python
# Kafka-based event streaming for OSS/BSS integration
from kafka import KafkaProducer, KafkaConsumer
import json

class OSSBSSEventBus:
    """Event bus for OSS/BSS communication"""

    def __init__(self, bootstrap_servers: List[str]):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def publish_order_event(self, order_id: str, event_type: str, payload: Dict):
        """Publish order event to event bus"""
        event = {
            "eventId": str(uuid.uuid4()),
            "eventType": event_type,
            "eventTime": datetime.now().isoformat(),
            "orderId": order_id,
            "payload": payload
        }

        self.producer.send("product-order-events", value=event)

    def publish_service_activation_event(self, service_id: str,
                                        subscriber_id: str,
                                        activation_details: Dict):
        """Publish service activation event"""
        event = {
            "eventId": str(uuid.uuid4()),
            "eventType": "ServiceActivated",
            "eventTime": datetime.now().isoformat(),
            "serviceId": service_id,
            "subscriberId": subscriber_id,
            "activationDetails": activation_details
        }

        self.producer.send("service-lifecycle-events", value=event)
```

## Best Practices

1. **API-First Design**: Use TM Forum Open APIs for standard interfaces
2. **Event-Driven Architecture**: Decouple OSS and BSS with event streams
3. **Data Consistency**: Implement eventual consistency patterns
4. **Error Handling**: Comprehensive error handling and retry logic
5. **Monitoring**: Track API performance and integration health

## Common Issues

### Issue: Order State Inconsistency
**Solution**: Implement state machine validation, event sourcing

### Issue: Provisioning Failures
**Solution**: Implement compensation workflows, rollback mechanisms

### Issue: Data Synchronization Delays
**Solution**: Optimize batch processing, implement CDC (Change Data Capture)

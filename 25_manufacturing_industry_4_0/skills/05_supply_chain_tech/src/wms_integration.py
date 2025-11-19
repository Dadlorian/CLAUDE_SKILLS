"""
WMS Integration Module - API Integration with Warehouse Management Systems

This module provides comprehensive WMS integration capabilities for:
- Inventory synchronization with ERP systems
- Order management and fulfillment
- Real-time picking and shipping operations
- Barcode/RFID scanning integration
- Integration with Transportation Management Systems (TMS)
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import hmac
from abc import ABC, abstractmethod
import requests
from requests.auth import HTTPBasicAuth


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Data Classes
# ============================================================================

class InventoryStatus(Enum):
    """Inventory status types"""
    AVAILABLE = "available"
    RESERVED = "reserved"
    DAMAGED = "damaged"
    QUARANTINE = "quarantine"
    RETURNS = "returns"
    OVERSTOCK = "overstock"


class OrderStatus(Enum):
    """Order status in fulfillment process"""
    RECEIVED = "received"
    ALLOCATED = "allocated"
    PICKED = "picked"
    PACKED = "packed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PickingStrategy(Enum):
    """Picking strategies for wave planning"""
    SINGLE_ORDER = "single_order"
    BATCH = "batch"
    ZONE = "zone"
    CLUSTER = "cluster"
    WAVE = "wave"


@dataclass
class InventoryItem:
    """Inventory item with location and quantity"""
    sku: str
    location_id: str
    quantity_on_hand: int
    quantity_allocated: int
    quantity_available: int
    status: InventoryStatus
    lot_number: Optional[str] = None
    serial_numbers: Optional[List[str]] = None
    expiration_date: Optional[str] = None
    last_updated: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        return data


@dataclass
class Order:
    """Sales order for fulfillment"""
    order_id: str
    customer_id: str
    order_date: str
    required_date: str
    order_lines: List['OrderLine']
    shipping_address: str
    status: OrderStatus = OrderStatus.RECEIVED
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        data['order_lines'] = [line.to_dict() for line in self.order_lines]
        return data


@dataclass
class OrderLine:
    """Individual line item in an order"""
    line_id: str
    sku: str
    quantity: int
    uom: str = "EACH"
    picked_quantity: int = 0
    picked_location: Optional[str] = None
    picked_datetime: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class PurchaseOrder:
    """Purchase order for receiving"""
    po_number: str
    supplier_id: str
    expected_date: str
    po_lines: List['POLine']
    receiving_location: str
    status: str = "open"
    created_at: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['po_lines'] = [line.to_dict() for line in self.po_lines]
        return data


@dataclass
class POLine:
    """Individual line item in a purchase order"""
    line_id: str
    sku: str
    quantity_ordered: int
    uom: str = "EACH"
    quantity_received: int = 0
    receiving_location: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


# ============================================================================
# WMS Integration Base Classes
# ============================================================================

class WMSConnector(ABC):
    """Abstract base class for WMS connectors"""

    def __init__(self, base_url: str, api_key: str, secret_key: str):
        """
        Initialize WMS connector

        Args:
            base_url: WMS API base URL
            api_key: API authentication key
            secret_key: API secret key for HMAC
        """
        self.base_url = base_url
        self.api_key = api_key
        self.secret_key = secret_key
        self.session = requests.Session()

    def _generate_signature(self, method: str, path: str,
                           body: Optional[str] = None) -> str:
        """
        Generate HMAC signature for API requests

        Args:
            method: HTTP method
            path: API path
            body: Request body

        Returns:
            Base64-encoded HMAC signature
        """
        timestamp = str(int(datetime.utcnow().timestamp() * 1000))
        message = f"{method}\n{path}\n{timestamp}\n{body or ''}"

        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()

        import base64
        return base64.b64encode(signature).decode()

    def _make_request(self, method: str, path: str,
                     data: Optional[Dict] = None,
                     params: Optional[Dict] = None) -> Dict:
        """
        Make authenticated API request

        Args:
            method: HTTP method
            path: API path
            data: Request body
            params: Query parameters

        Returns:
            Response JSON as dictionary
        """
        url = f"{self.base_url}{path}"
        body = json.dumps(data) if data else None

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "X-API-Signature": self._generate_signature(method, path, body),
            "X-API-Timestamp": str(int(datetime.utcnow().timestamp() * 1000))
        }

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    @abstractmethod
    def get_inventory(self, sku: Optional[str] = None,
                     location_id: Optional[str] = None) -> List[InventoryItem]:
        """Get inventory from WMS"""
        pass

    @abstractmethod
    def create_order(self, order: Order) -> str:
        """Create order in WMS"""
        pass

    @abstractmethod
    def get_order_status(self, order_id: str) -> Dict:
        """Get order status"""
        pass


# ============================================================================
# Specific WMS Implementations
# ============================================================================

class ManhattanWMSConnector(WMSConnector):
    """Manhattan Associates WMS API connector"""

    def get_inventory(self, sku: Optional[str] = None,
                     location_id: Optional[str] = None) -> List[InventoryItem]:
        """
        Get inventory from Manhattan WMS

        Args:
            sku: Filter by SKU
            location_id: Filter by location

        Returns:
            List of InventoryItem objects
        """
        params = {}
        if sku:
            params['sku'] = sku
        if location_id:
            params['location'] = location_id

        response = self._make_request(
            method="GET",
            path="/api/v1/inventory",
            params=params
        )

        inventory_items = []
        for item in response.get('items', []):
            inv_item = InventoryItem(
                sku=item['sku'],
                location_id=item['location'],
                quantity_on_hand=item['qoh'],
                quantity_allocated=item.get('allocated', 0),
                quantity_available=item['available'],
                status=InventoryStatus(item.get('status', 'available')),
                lot_number=item.get('lot_number'),
                expiration_date=item.get('expiration_date'),
                last_updated=item.get('last_updated')
            )
            inventory_items.append(inv_item)

        logger.info(f"Retrieved {len(inventory_items)} inventory items")
        return inventory_items

    def create_order(self, order: Order) -> str:
        """
        Create order in Manhattan WMS

        Args:
            order: Order object

        Returns:
            Order ID assigned by WMS
        """
        payload = {
            "orderNumber": order.order_id,
            "customerId": order.customer_id,
            "orderDate": order.order_date,
            "requiredDate": order.required_date,
            "shippingAddress": order.shipping_address,
            "orderLines": [line.to_dict() for line in order.order_lines]
        }

        response = self._make_request(
            method="POST",
            path="/api/v1/orders",
            data=payload
        )

        wms_order_id = response.get('orderId')
        logger.info(f"Created order {wms_order_id} in Manhattan WMS")
        return wms_order_id

    def get_order_status(self, order_id: str) -> Dict:
        """Get order status from Manhattan WMS"""
        response = self._make_request(
            method="GET",
            path=f"/api/v1/orders/{order_id}"
        )
        return response

    def allocate_inventory(self, order_id: str, rules: Dict) -> List[str]:
        """
        Allocate inventory for order using specified rules

        Args:
            order_id: Order ID
            rules: Allocation rules (FIFO, LIFO, closest location, etc.)

        Returns:
            List of location IDs allocated
        """
        payload = {
            "orderId": order_id,
            "allocationRules": rules
        }

        response = self._make_request(
            method="POST",
            path=f"/api/v1/orders/{order_id}/allocate",
            data=payload
        )

        allocated_locations = response.get('allocatedLocations', [])
        logger.info(f"Allocated {len(allocated_locations)} locations for order {order_id}")
        return allocated_locations

    def create_pick_wave(self, wave_config: Dict) -> str:
        """
        Create picking wave in Manhattan WMS

        Args:
            wave_config: Wave configuration including:
                - orders: List of order IDs
                - picking_strategy: Picking strategy enum
                - priority: Wave priority
                - batch_size: Number of orders to batch together

        Returns:
            Wave ID
        """
        payload = {
            "orderIds": wave_config.get('orders', []),
            "pickingStrategy": wave_config.get('picking_strategy', 'wave'),
            "priority": wave_config.get('priority', 1),
            "batchSize": wave_config.get('batch_size', 10)
        }

        response = self._make_request(
            method="POST",
            path="/api/v1/waves",
            data=payload
        )

        wave_id = response.get('waveId')
        logger.info(f"Created wave {wave_id} with {len(payload['orderIds'])} orders")
        return wave_id

    def get_picking_tasks(self, wave_id: str) -> List[Dict]:
        """
        Get picking tasks for a wave

        Args:
            wave_id: Wave ID

        Returns:
            List of picking tasks
        """
        response = self._make_request(
            method="GET",
            path=f"/api/v1/waves/{wave_id}/picks"
        )

        tasks = response.get('tasks', [])
        logger.info(f"Retrieved {len(tasks)} picking tasks for wave {wave_id}")
        return tasks

    def confirm_pick(self, pick_id: str, sku: str, quantity: int,
                    location_id: str) -> bool:
        """
        Confirm item picked (via RF terminal scanning)

        Args:
            pick_id: Pick task ID
            sku: Product SKU
            quantity: Quantity picked
            location_id: Location picked from

        Returns:
            Success indicator
        """
        payload = {
            "pickId": pick_id,
            "sku": sku,
            "quantity": quantity,
            "location": location_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        response = self._make_request(
            method="POST",
            path=f"/api/v1/picks/{pick_id}/confirm",
            data=payload
        )

        success = response.get('status') == 'success'
        logger.info(f"Pick confirmation for {pick_id}: {'SUCCESS' if success else 'FAILED'}")
        return success

    def receive_goods(self, po_number: str, po_line_items: List[Dict]) -> str:
        """
        Receive purchase order goods (create goods receipt)

        Args:
            po_number: Purchase order number
            po_line_items: List of received items with sku, qty, location

        Returns:
            Goods receipt number
        """
        payload = {
            "poNumber": po_number,
            "lineItems": po_line_items,
            "receivedDate": datetime.utcnow().isoformat()
        }

        response = self._make_request(
            method="POST",
            path="/api/v1/goods-receipts",
            data=payload
        )

        receipt_number = response.get('receiptNumber')
        logger.info(f"Created goods receipt {receipt_number} for PO {po_number}")
        return receipt_number


class SAPEWM_Connector(WMSConnector):
    """SAP Extended Warehouse Management (EWM) API connector"""

    def get_inventory(self, sku: Optional[str] = None,
                     location_id: Optional[str] = None) -> List[InventoryItem]:
        """Get inventory from SAP EWM"""
        params = {'$filter': ''}
        filters = []

        if sku:
            filters.append(f"Material eq '{sku}'")
        if location_id:
            filters.append(f"Bin eq '{location_id}'")

        if filters:
            params['$filter'] = ' and '.join(filters)

        response = self._make_request(
            method="GET",
            path="/sap/opu/odata/SAP/EWMWAREHOUSE_SRV/Stocks",
            params=params
        )

        inventory_items = []
        for item in response.get('d', {}).get('results', []):
            inv_item = InventoryItem(
                sku=item['Material'],
                location_id=item['Bin'],
                quantity_on_hand=int(item['Quantity']),
                quantity_allocated=int(item.get('AllocatedQuantity', 0)),
                quantity_available=int(item['AvailableQuantity']),
                status=InventoryStatus.AVAILABLE,
                lot_number=item.get('Batch'),
                expiration_date=item.get('ExpirationDate'),
                last_updated=item.get('LastChangedDate')
            )
            inventory_items.append(inv_item)

        logger.info(f"Retrieved {len(inventory_items)} inventory items from SAP EWM")
        return inventory_items

    def create_order(self, order: Order) -> str:
        """Create order in SAP EWM"""
        payload = {
            'WarehouseTask': {
                'd': {
                    'SalesOrder': order.order_id,
                    'Customer': order.customer_id,
                    'Status': '01',  # Open
                    'CreatedDate': datetime.utcnow().isoformat(),
                    'to_Items': {
                        'results': [
                            {
                                'SalesOrderItem': line.line_id,
                                'Material': line.sku,
                                'Quantity': line.quantity,
                                'UnitOfMeasure': line.uom
                            }
                            for line in order.order_lines
                        ]
                    }
                }
            }
        }

        response = self._make_request(
            method="POST",
            path="/sap/opu/odata/SAP/EWMWAREHOUSE_SRV/Orders",
            data=payload
        )

        wms_order_id = response.get('d', {}).get('OrderId')
        logger.info(f"Created order {wms_order_id} in SAP EWM")
        return wms_order_id

    def get_order_status(self, order_id: str) -> Dict:
        """Get order status from SAP EWM"""
        response = self._make_request(
            method="GET",
            path=f"/sap/opu/odata/SAP/EWMWAREHOUSE_SRV/Orders('{order_id}')"
        )
        return response.get('d', {})


# ============================================================================
# Inventory Manager
# ============================================================================

class InventoryManager:
    """Manages inventory operations across WMS"""

    def __init__(self, wms_connector: WMSConnector):
        """
        Initialize inventory manager

        Args:
            wms_connector: WMS connector instance
        """
        self.wms = wms_connector

    def get_inventory_position(self, sku: str) -> Dict:
        """
        Get complete inventory position for SKU

        Args:
            sku: Product SKU

        Returns:
            Aggregated inventory by status
        """
        inventory = self.wms.get_inventory(sku=sku)

        position = {
            'sku': sku,
            'total_on_hand': 0,
            'total_allocated': 0,
            'total_available': 0,
            'locations': {}
        }

        for item in inventory:
            position['total_on_hand'] += item.quantity_on_hand
            position['total_allocated'] += item.quantity_allocated
            position['total_available'] += item.quantity_available
            position['locations'][item.location_id] = {
                'qty_on_hand': item.quantity_on_hand,
                'qty_allocated': item.quantity_allocated,
                'qty_available': item.quantity_available,
                'status': item.status.value
            }

        return position

    def check_availability(self, sku: str, quantity_needed: int) -> Tuple[bool, int]:
        """
        Check if SKU is available in required quantity

        Args:
            sku: Product SKU
            quantity_needed: Required quantity

        Returns:
            Tuple of (is_available, available_quantity)
        """
        position = self.get_inventory_position(sku)
        available = position['total_available']
        return available >= quantity_needed, available

    def allocate_sku(self, sku: str, quantity: int) -> List[Dict]:
        """
        Allocate SKU quantity to specific locations using FIFO

        Args:
            sku: Product SKU
            quantity: Quantity to allocate

        Returns:
            List of allocations with location and qty
        """
        inventory = sorted(
            self.wms.get_inventory(sku=sku),
            key=lambda x: x.last_updated or datetime.utcnow().isoformat()
        )

        allocations = []
        remaining = quantity

        for item in inventory:
            if remaining <= 0:
                break
            if item.quantity_available > 0:
                allocated = min(remaining, item.quantity_available)
                allocations.append({
                    'location': item.location_id,
                    'quantity': allocated,
                    'sku': sku
                })
                remaining -= allocated

        logger.info(f"Allocated {quantity - remaining}/{quantity} units of {sku}")
        return allocations


# ============================================================================
# Order Fulfillment Manager
# ============================================================================

class OrderFulfillmentManager:
    """Manages order fulfillment workflow"""

    def __init__(self, wms_connector: WMSConnector,
                 inventory_manager: InventoryManager):
        """Initialize order fulfillment manager"""
        self.wms = wms_connector
        self.inventory = inventory_manager

    def validate_order_for_picking(self, order: Order) -> Tuple[bool, List[str]]:
        """
        Validate that all items in order are available

        Args:
            order: Order to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        for line in order.order_lines:
            available, qty = self.inventory.check_availability(
                line.sku, line.quantity
            )
            if not available:
                errors.append(
                    f"Line {line.line_id}: {line.sku} - "
                    f"Need {line.quantity}, have {qty}"
                )

        is_valid = len(errors) == 0
        logger.info(f"Order validation: {'PASS' if is_valid else 'FAIL'}")
        return is_valid, errors

    def create_picking_wave(self, orders: List[Order],
                          strategy: PickingStrategy = PickingStrategy.WAVE) -> str:
        """
        Create picking wave for multiple orders

        Args:
            orders: List of orders to pick
            strategy: Picking strategy

        Returns:
            Wave ID
        """
        # Validate all orders first
        for order in orders:
            is_valid, errors = self.validate_order_for_picking(order)
            if not is_valid:
                logger.error(f"Order {order.order_id} validation failed: {errors}")
                continue

        wave_config = {
            'orders': [order.order_id for order in orders],
            'picking_strategy': strategy.value,
            'priority': 1,
            'batch_size': len(orders)
        }

        if isinstance(self.wms, ManhattanWMSConnector):
            wave_id = self.wms.create_pick_wave(wave_config)
        else:
            wave_id = f"WAVE_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            logger.warning(f"Wave creation not implemented for this WMS connector")

        logger.info(f"Created wave {wave_id} with {len(orders)} orders")
        return wave_id

    def process_picked_items(self, wave_id: str, picks: List[Dict]) -> Dict:
        """
        Process picked items from warehouse

        Args:
            wave_id: Wave ID
            picks: List of picks with pick_id, sku, qty, location

        Returns:
            Summary of processed picks
        """
        results = {
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        for pick in picks:
            try:
                if isinstance(self.wms, ManhattanWMSConnector):
                    success = self.wms.confirm_pick(
                        pick_id=pick['pick_id'],
                        sku=pick['sku'],
                        quantity=pick['quantity'],
                        location_id=pick['location']
                    )
                    if success:
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Pick {pick['pick_id']} failed")
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Pick {pick['pick_id']}: {str(e)}")

        logger.info(
            f"Wave {wave_id} processed: "
            f"{results['successful']} successful, {results['failed']} failed"
        )
        return results


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example: Initialize Manhattan WMS connector
    wms = ManhattanWMSConnector(
        base_url="https://wms.company.com",
        api_key="your-api-key",
        secret_key="your-secret-key"
    )

    # Create inventory and order managers
    inventory_mgr = InventoryManager(wms)
    fulfillment_mgr = OrderFulfillmentManager(wms, inventory_mgr)

    # Example: Get inventory position
    position = inventory_mgr.get_inventory_position("SKU123")
    print(f"Inventory Position: {position}")

    # Example: Check availability
    available, qty = inventory_mgr.check_availability("SKU123", 100)
    print(f"Availability: {available}, Quantity available: {qty}")

    # Example: Create orders
    order = Order(
        order_id="ORD-001",
        customer_id="CUST-123",
        order_date=datetime.utcnow().isoformat(),
        required_date=(datetime.utcnow() + timedelta(days=2)).isoformat(),
        order_lines=[
            OrderLine(line_id="1", sku="SKU123", quantity=10),
            OrderLine(line_id="2", sku="SKU456", quantity=5)
        ],
        shipping_address="123 Main St, City, State 12345"
    )

    # Validate order
    is_valid, errors = fulfillment_mgr.validate_order_for_picking(order)
    if is_valid:
        # Create picking wave
        wave_id = fulfillment_mgr.create_picking_wave([order])
        print(f"Created wave: {wave_id}")

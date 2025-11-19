"""
Multi-Carrier Tracking Integration

Production-ready implementation for integrating with multiple carrier APIs
for real-time shipment tracking and visibility across the supply chain.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum
import requests
from abc import ABC, abstractmethod
import hashlib
import json


class ShipmentStatus(Enum):
    """Standardized shipment status codes"""
    CREATED = "created"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    EXCEPTION = "exception"
    RETURNED = "returned"
    CANCELLED = "cancelled"


class EventType(Enum):
    """Standard tracking event types"""
    PICKUP = "pickup"
    DEPARTURE = "departure"
    ARRIVAL = "arrival"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERY_ATTEMPT = "delivery_attempt"
    DELIVERED = "delivered"
    EXCEPTION = "exception"
    DELAY = "delay"
    WEATHER_DELAY = "weather_delay"
    CUSTOMS_CLEARANCE = "customs_clearance"


@dataclass
class TrackingEvent:
    """Standardized tracking event"""
    timestamp: datetime
    event_type: EventType
    status: ShipmentStatus
    location: Optional[str]
    description: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    exception_code: Optional[str] = None


@dataclass
class ShipmentTracking:
    """Complete shipment tracking information"""
    tracking_number: str
    carrier: str
    status: ShipmentStatus
    estimated_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    origin: Optional[Dict] = None
    destination: Optional[Dict] = None
    events: List[TrackingEvent] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


class CarrierAPI(ABC):
    """Abstract base class for carrier API integrations"""

    def __init__(self, api_key: str, api_secret: Optional[str] = None):
        self.api_key = api_key
        self.api_secret = api_secret

    @abstractmethod
    def track_shipment(self, tracking_number: str) -> ShipmentTracking:
        """Track a shipment and return standardized tracking info"""
        pass

    @abstractmethod
    def get_proof_of_delivery(self, tracking_number: str) -> Optional[Dict]:
        """Get proof of delivery (signature, photo, etc.)"""
        pass


class FedExAPI(CarrierAPI):
    """FedEx API Integration"""

    BASE_URL = "https://apis.fedex.com"

    def __init__(self, api_key: str, api_secret: str):
        super().__init__(api_key, api_secret)
        self.access_token = None
        self.token_expires_at = None

    def _get_access_token(self) -> str:
        """Obtain OAuth access token"""
        if self.access_token and datetime.now() < self.token_expires_at:
            return self.access_token

        response = requests.post(
            f"{self.BASE_URL}/oauth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.api_secret
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        response.raise_for_status()
        data = response.json()

        self.access_token = data['access_token']
        expires_in = data['expires_in']
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)

        return self.access_token

    def track_shipment(self, tracking_number: str) -> ShipmentTracking:
        """Track FedEx shipment"""
        token = self._get_access_token()

        response = requests.post(
            f"{self.BASE_URL}/track/v1/trackingnumbers",
            json={
                "includeDetailedScans": True,
                "trackingInfo": [
                    {
                        "trackingNumberInfo": {
                            "trackingNumber": tracking_number
                        }
                    }
                ]
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )

        response.raise_for_status()
        data = response.json()

        return self._parse_fedex_response(tracking_number, data)

    def _parse_fedex_response(self, tracking_number: str, data: Dict) -> ShipmentTracking:
        """Parse FedEx API response into standardized format"""
        tracking_info = data['output']['completeTrackResults'][0]['trackResults'][0]

        # Map FedEx status to standardized status
        fedex_status = tracking_info.get('latestStatusDetail', {}).get('code')
        status = self._map_fedex_status(fedex_status)

        # Parse events
        events = []
        for scan in tracking_info.get('scanEvents', []):
            event = self._parse_fedex_event(scan)
            if event:
                events.append(event)

        # Parse dates
        estimated_delivery = None
        if 'estimatedDeliveryTimeWindow' in tracking_info:
            est_date = tracking_info['estimatedDeliveryTimeWindow'].get('window', {}).get('ends')
            if est_date:
                estimated_delivery = datetime.fromisoformat(est_date.replace('Z', '+00:00'))

        actual_delivery = None
        if status == ShipmentStatus.DELIVERED:
            for event in events:
                if event.event_type == EventType.DELIVERED:
                    actual_delivery = event.timestamp
                    break

        return ShipmentTracking(
            tracking_number=tracking_number,
            carrier="FedEx",
            status=status,
            estimated_delivery=estimated_delivery,
            actual_delivery=actual_delivery,
            events=sorted(events, key=lambda e: e.timestamp, reverse=True),
            last_updated=datetime.now()
        )

    def _map_fedex_status(self, fedex_status: str) -> ShipmentStatus:
        """Map FedEx status codes to standardized status"""
        status_mapping = {
            "PU": ShipmentStatus.PICKED_UP,
            "IT": ShipmentStatus.IN_TRANSIT,
            "OD": ShipmentStatus.OUT_FOR_DELIVERY,
            "DL": ShipmentStatus.DELIVERED,
            "DE": ShipmentStatus.EXCEPTION,
            "CA": ShipmentStatus.CANCELLED
        }
        return status_mapping.get(fedex_status, ShipmentStatus.IN_TRANSIT)

    def _parse_fedex_event(self, scan: Dict) -> Optional[TrackingEvent]:
        """Parse FedEx scan event"""
        event_type_str = scan.get('eventType')
        event_description = scan.get('eventDescription')

        # Map event type
        event_type = EventType.IN_TRANSIT  # Default
        if 'Picked up' in event_description:
            event_type = EventType.PICKUP
        elif 'Delivered' in event_description:
            event_type = EventType.DELIVERED
        elif 'Out for delivery' in event_description:
            event_type = EventType.OUT_FOR_DELIVERY
        elif 'Departed' in event_description:
            event_type = EventType.DEPARTURE
        elif 'Arrived' in event_description:
            event_type = EventType.ARRIVAL

        # Parse timestamp
        timestamp_str = scan.get('date')
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            return None

        # Parse location
        location_info = scan.get('scanLocation', {})

        return TrackingEvent(
            timestamp=timestamp,
            event_type=event_type,
            status=self._map_fedex_status(event_type_str),
            location=location_info.get('locationName'),
            description=event_description,
            city=location_info.get('city'),
            state=location_info.get('stateOrProvinceCode'),
            country=location_info.get('countryCode'),
            postal_code=location_info.get('postalCode')
        )

    def get_proof_of_delivery(self, tracking_number: str) -> Optional[Dict]:
        """Get FedEx proof of delivery"""
        token = self._get_access_token()

        response = requests.post(
            f"{self.BASE_URL}/track/v1/trackingnumbers",
            json={
                "includeDetailedScans": True,
                "trackingInfo": [
                    {
                        "trackingNumberInfo": {
                            "trackingNumber": tracking_number
                        }
                    }
                ]
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )

        response.raise_for_status()
        data = response.json()

        tracking_info = data['output']['completeTrackResults'][0]['trackResults'][0]
        delivery_info = tracking_info.get('deliveryDetails', {})

        if delivery_info:
            return {
                "delivered_at": delivery_info.get('actualDeliveryTimestamp'),
                "signed_by": delivery_info.get('signedBy'),
                "location_type": delivery_info.get('deliveryLocationType'),
                "signature_image_url": delivery_info.get('signatureImageUrl')
            }

        return None


class UPSAPI(CarrierAPI):
    """UPS API Integration"""

    BASE_URL = "https://onlinetools.ups.com/api"

    def track_shipment(self, tracking_number: str) -> ShipmentTracking:
        """Track UPS shipment"""
        response = requests.get(
            f"{self.BASE_URL}/track/v1/details/{tracking_number}",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )

        response.raise_for_status()
        data = response.json()

        return self._parse_ups_response(tracking_number, data)

    def _parse_ups_response(self, tracking_number: str, data: Dict) -> ShipmentTracking:
        """Parse UPS API response"""
        shipment = data['trackResponse']['shipment'][0]
        package = shipment['package'][0]

        # Parse status
        current_status = package['currentStatus']
        status = self._map_ups_status(current_status['code'])

        # Parse events
        events = []
        for activity in package.get('activity', []):
            event = self._parse_ups_activity(activity)
            if event:
                events.append(event)

        # Parse estimated delivery
        estimated_delivery = None
        delivery_date_info = package.get('deliveryDate', [])
        if delivery_date_info:
            est_date_str = delivery_date_info[0].get('date')
            if est_date_str:
                estimated_delivery = datetime.strptime(est_date_str, '%Y%m%d')

        return ShipmentTracking(
            tracking_number=tracking_number,
            carrier="UPS",
            status=status,
            estimated_delivery=estimated_delivery,
            events=sorted(events, key=lambda e: e.timestamp, reverse=True),
            last_updated=datetime.now()
        )

    def _map_ups_status(self, ups_status: str) -> ShipmentStatus:
        """Map UPS status codes"""
        status_mapping = {
            "011": ShipmentStatus.DELIVERED,
            "023": ShipmentStatus.OUT_FOR_DELIVERY,
            "096": ShipmentStatus.IN_TRANSIT,
            "006": ShipmentStatus.EXCEPTION
        }
        return status_mapping.get(ups_status, ShipmentStatus.IN_TRANSIT)

    def _parse_ups_activity(self, activity: Dict) -> Optional[TrackingEvent]:
        """Parse UPS activity"""
        status_info = activity.get('status', {})
        location_info = activity.get('location', {}).get('address', {})

        timestamp_str = activity.get('date') + activity.get('time')
        timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')

        return TrackingEvent(
            timestamp=timestamp,
            event_type=self._map_ups_event_type(status_info.get('type')),
            status=self._map_ups_status(status_info.get('code')),
            location=location_info.get('city'),
            description=status_info.get('description'),
            city=location_info.get('city'),
            state=location_info.get('stateProvince'),
            country=location_info.get('country'),
            postal_code=location_info.get('postalCode')
        )

    def _map_ups_event_type(self, ups_type: str) -> EventType:
        """Map UPS event types"""
        type_mapping = {
            "P": EventType.PICKUP,
            "I": EventType.IN_TRANSIT,
            "D": EventType.DELIVERED,
            "X": EventType.EXCEPTION
        }
        return type_mapping.get(ups_type, EventType.IN_TRANSIT)

    def get_proof_of_delivery(self, tracking_number: str) -> Optional[Dict]:
        """Get UPS proof of delivery"""
        # UPS POD requires separate API call
        response = requests.get(
            f"{self.BASE_URL}/track/v1/poddetails/{tracking_number}",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "delivered_at": data.get('deliveryTime'),
                "signed_by": data.get('signedBy'),
                "signature_image": data.get('signatureImage')
            }

        return None


class MultiCarrierTracker:
    """
    Unified interface for tracking shipments across multiple carriers
    """

    def __init__(self):
        self.carriers: Dict[str, CarrierAPI] = {}

    def register_carrier(self, carrier_name: str, carrier_api: CarrierAPI):
        """Register a carrier API"""
        self.carriers[carrier_name.lower()] = carrier_api

    def track(self, carrier: str, tracking_number: str) -> Optional[ShipmentTracking]:
        """Track shipment with specified carrier"""
        carrier_api = self.carriers.get(carrier.lower())

        if not carrier_api:
            raise ValueError(f"Carrier {carrier} not registered")

        try:
            return carrier_api.track_shipment(tracking_number)
        except Exception as e:
            print(f"Error tracking {tracking_number} with {carrier}: {e}")
            return None

    def track_multiple(self, shipments: List[Tuple[str, str]]) -> List[ShipmentTracking]:
        """
        Track multiple shipments in parallel.
        shipments: List of (carrier, tracking_number) tuples
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_shipment = {
                executor.submit(self.track, carrier, tracking_number): (carrier, tracking_number)
                for carrier, tracking_number in shipments
            }

            for future in as_completed(future_to_shipment):
                carrier, tracking_number = future_to_shipment[future]
                try:
                    tracking = future.result()
                    if tracking:
                        results.append(tracking)
                except Exception as e:
                    print(f"Error tracking {tracking_number}: {e}")

        return results

    def get_proof_of_delivery(self, carrier: str, tracking_number: str) -> Optional[Dict]:
        """Get proof of delivery for shipment"""
        carrier_api = self.carriers.get(carrier.lower())

        if not carrier_api:
            raise ValueError(f"Carrier {carrier} not registered")

        try:
            return carrier_api.get_proof_of_delivery(tracking_number)
        except Exception as e:
            print(f"Error getting POD for {tracking_number}: {e}")
            return None


class TrackingCache:
    """
    Cache tracking information to reduce API calls
    """

    def __init__(self, ttl_minutes: int = 15):
        self.cache: Dict[str, Tuple[ShipmentTracking, datetime]] = {}
        self.ttl = timedelta(minutes=ttl_minutes)

    def get(self, tracking_number: str) -> Optional[ShipmentTracking]:
        """Get cached tracking info if not expired"""
        if tracking_number in self.cache:
            tracking, cached_at = self.cache[tracking_number]

            if datetime.now() - cached_at < self.ttl:
                return tracking

            # Expired - remove from cache
            del self.cache[tracking_number]

        return None

    def set(self, tracking_number: str, tracking: ShipmentTracking):
        """Cache tracking information"""
        self.cache[tracking_number] = (tracking, datetime.now())

    def clear_expired(self):
        """Remove expired entries from cache"""
        now = datetime.now()
        expired_keys = [
            key for key, (_, cached_at) in self.cache.items()
            if now - cached_at >= self.ttl
        ]

        for key in expired_keys:
            del self.cache[key]


class CachedMultiCarrierTracker(MultiCarrierTracker):
    """Multi-carrier tracker with caching"""

    def __init__(self, cache_ttl_minutes: int = 15):
        super().__init__()
        self.cache = TrackingCache(ttl_minutes=cache_ttl_minutes)

    def track(self, carrier: str, tracking_number: str) -> Optional[ShipmentTracking]:
        """Track shipment with caching"""
        # Check cache first
        cached = self.cache.get(tracking_number)
        if cached:
            return cached

        # Not in cache - fetch from API
        tracking = super().track(carrier, tracking_number)

        if tracking:
            self.cache.set(tracking_number, tracking)

        return tracking


# ============================================================================
# Example Usage
# ============================================================================


def example_usage():
    # Initialize carrier APIs
    fedex_api = FedExAPI(
        api_key="your_fedex_key",
        api_secret="your_fedex_secret"
    )

    ups_api = UPSAPI(api_key="your_ups_key")

    # Create multi-carrier tracker
    tracker = CachedMultiCarrierTracker(cache_ttl_minutes=15)
    tracker.register_carrier("FedEx", fedex_api)
    tracker.register_carrier("UPS", ups_api)

    # Track single shipment
    print("=== Single Shipment Tracking ===")
    tracking = tracker.track("FedEx", "123456789012")

    if tracking:
        print(f"Tracking #: {tracking.tracking_number}")
        print(f"Carrier: {tracking.carrier}")
        print(f"Status: {tracking.status.value}")
        print(f"Estimated Delivery: {tracking.estimated_delivery}")
        print(f"\nRecent Events:")

        for event in tracking.events[:5]:  # Show latest 5 events
            print(f"  {event.timestamp} - {event.description}")
            if event.location:
                print(f"    Location: {event.location}")

    # Track multiple shipments
    print("\n=== Multiple Shipment Tracking ===")
    shipments = [
        ("FedEx", "123456789012"),
        ("UPS", "1Z9999999999999999"),
        ("FedEx", "987654321098"),
    ]

    results = tracker.track_multiple(shipments)

    print(f"Tracked {len(results)} shipments:")
    for tracking in results:
        print(f"  {tracking.carrier} {tracking.tracking_number}: {tracking.status.value}")

    # Get proof of delivery
    print("\n=== Proof of Delivery ===")
    pod = tracker.get_proof_of_delivery("FedEx", "123456789012")

    if pod:
        print(f"Delivered at: {pod.get('delivered_at')}")
        print(f"Signed by: {pod.get('signed_by')}")
        print(f"Signature URL: {pod.get('signature_image_url')}")


if __name__ == "__main__":
    example_usage()

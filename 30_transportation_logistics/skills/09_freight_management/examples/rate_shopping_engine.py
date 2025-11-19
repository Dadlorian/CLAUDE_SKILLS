"""
Freight Rate Shopping Engine

Production-ready implementation for comparing freight rates across multiple
carriers and service levels to optimize shipping costs.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime, date
import requests
from abc import ABC, abstractmethod
import json


class FreightMode(Enum):
    """Freight transportation modes"""
    LTL = "ltl"  # Less Than Truckload
    FTL = "ftl"  # Full Truckload
    PARCEL = "parcel"
    AIR = "air"
    OCEAN = "ocean"
    INTERMODAL = "intermodal"


class ServiceLevel(Enum):
    """Standard service levels"""
    STANDARD = "standard"
    EXPEDITED = "expedited"
    OVERNIGHT = "overnight"
    TWO_DAY = "two_day"
    ECONOMY = "economy"


@dataclass
class Address:
    """Shipping address"""
    name: str
    address_line1: str
    address_line2: Optional[str]
    city: str
    state: str
    zip_code: str
    country: str
    is_residential: bool = False


@dataclass
class Package:
    """Package or freight unit"""
    length: float  # inches
    width: float
    height: float
    weight: float  # lbs
    quantity: int = 1
    freight_class: Optional[str] = None  # For LTL
    nmfc: Optional[str] = None  # National Motor Freight Classification
    stackable: bool = True
    hazmat: bool = False


@dataclass
class ShipmentRequest:
    """Rate shopping request"""
    origin: Address
    destination: Address
    packages: List[Package]
    ship_date: date
    service_level: Optional[ServiceLevel] = None
    declared_value: Optional[float] = None
    insurance_required: bool = False
    lift_gate_required: bool = False
    inside_delivery: bool = False
    residential_delivery: bool = False


@dataclass
class RateQuote:
    """Freight rate quote"""
    carrier: str
    service_level: str
    mode: FreightMode
    base_rate: float
    fuel_surcharge: float
    accessorial_charges: Dict[str, float]
    total_cost: float
    transit_days: int
    estimated_delivery: date
    currency: str = "USD"
    quote_id: Optional[str] = None
    valid_until: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)

    @property
    def cost_per_mile(self) -> float:
        """Calculate cost per mile if distance is available"""
        distance = self.metadata.get('distance_miles', 0)
        return self.total_cost / distance if distance > 0 else 0


class CarrierRatingAPI(ABC):
    """Abstract base class for carrier rating APIs"""

    def __init__(self, api_key: str, account_number: str):
        self.api_key = api_key
        self.account_number = account_number

    @abstractmethod
    def get_rate_quote(self, request: ShipmentRequest) -> List[RateQuote]:
        """Get rate quote from carrier"""
        pass


class FedExFreightAPI(CarrierRatingAPI):
    """FedEx Freight LTL API Integration"""

    BASE_URL = "https://apis.fedex.com/freight"

    def get_rate_quote(self, request: ShipmentRequest) -> List[RateQuote]:
        """Get FedEx Freight rates"""
        # Authenticate and get token (simplified)
        token = self._get_access_token()

        # Build rate request
        payload = {
            "accountNumber": self.account_number,
            "rateRequestControlParameters": {
                "returnTransitTimes": True,
                "servicesNeededOnShipment": []
            },
            "requestedShipment": {
                "shipper": {
                    "address": self._format_address(request.origin)
                },
                "recipient": {
                    "address": self._format_address(request.destination)
                },
                "shipDateStamp": request.ship_date.isoformat(),
                "pickupType": "USE_SCHEDULED_PICKUP",
                "requestedPackageLineItems": [
                    self._format_package(pkg) for pkg in request.packages
                ]
            }
        }

        # Add accessorial services
        if request.lift_gate_required:
            payload["rateRequestControlParameters"]["servicesNeededOnShipment"].append("LIFTGATE_DELIVERY")

        if request.inside_delivery:
            payload["rateRequestControlParameters"]["servicesNeededOnShipment"].append("INSIDE_DELIVERY")

        # Make API call
        response = requests.post(
            f"{self.BASE_URL}/v1/rates/quotes",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )

        response.raise_for_status()
        data = response.json()

        # Parse response into RateQuote objects
        return self._parse_fedex_response(data, request)

    def _format_address(self, address: Address) -> Dict:
        """Format address for FedEx API"""
        return {
            "streetLines": [address.address_line1, address.address_line2],
            "city": address.city,
            "stateOrProvinceCode": address.state,
            "postalCode": address.zip_code,
            "countryCode": address.country
        }

    def _format_package(self, package: Package) -> Dict:
        """Format package for FedEx API"""
        return {
            "weight": {
                "units": "LB",
                "value": package.weight
            },
            "dimensions": {
                "length": package.length,
                "width": package.width,
                "height": package.height,
                "units": "IN"
            },
            "freightClass": package.freight_class,
            "nmfcCode": package.nmfc
        }

    def _parse_fedex_response(self, data: Dict, request: ShipmentRequest) -> List[RateQuote]:
        """Parse FedEx rate response"""
        quotes = []

        for rate_reply in data.get('output', {}).get('rateReplyDetails', []):
            # Parse charges
            base_rate = 0
            fuel_surcharge = 0
            accessorials = {}

            for surcharge in rate_reply.get('ratedShipmentDetails', [{}])[0].get('shipmentRateDetail', {}).get('surcharges', []):
                charge_type = surcharge.get('type')
                amount = surcharge.get('amount')

                if charge_type == 'BASE_CHARGE':
                    base_rate = amount
                elif charge_type == 'FUEL':
                    fuel_surcharge = amount
                else:
                    accessorials[charge_type] = amount

            total = rate_reply.get('ratedShipmentDetails', [{}])[0].get('shipmentRateDetail', {}).get('totalNetCharge')

            # Transit time
            transit_days = rate_reply.get('commit', {}).get('dateDetail', {}).get('transitDays', 0)

            # Estimated delivery
            delivery_date_str = rate_reply.get('commit', {}).get('dateDetail', {}).get('dayFormat')
            estimated_delivery = datetime.strptime(delivery_date_str, '%Y-%m-%d').date() if delivery_date_str else None

            quote = RateQuote(
                carrier="FedEx Freight",
                service_level=rate_reply.get('serviceType'),
                mode=FreightMode.LTL,
                base_rate=base_rate,
                fuel_surcharge=fuel_surcharge,
                accessorial_charges=accessorials,
                total_cost=total,
                transit_days=transit_days,
                estimated_delivery=estimated_delivery,
                quote_id=rate_reply.get('quoteNumber'),
                metadata={
                    'service_description': rate_reply.get('serviceName')
                }
            )

            quotes.append(quote)

        return quotes

    def _get_access_token(self) -> str:
        """Get OAuth token (simplified)"""
        # In production, implement proper OAuth flow with token caching
        return "mock_token"


class UPSFreightAPI(CarrierRatingAPI):
    """UPS Freight LTL API Integration"""

    BASE_URL = "https://onlinetools.ups.com/api/freight"

    def get_rate_quote(self, request: ShipmentRequest) -> List[RateQuote]:
        """Get UPS Freight rates"""
        payload = {
            "FreightRateRequest": {
                "Request": {
                    "TransactionReference": {
                        "CustomerContext": "Rate Quote Request"
                    }
                },
                "ShipFrom": self._format_address(request.origin),
                "ShipTo": self._format_address(request.destination),
                "PaymentInformation": {
                    "Payer": {
                        "AccountNumber": self.account_number
                    }
                },
                "Service": {
                    "Code": "308"  # UPS Freight LTL
                },
                "Commodity": [
                    self._format_commodity(pkg) for pkg in request.packages
                ]
            }
        }

        response = requests.post(
            f"{self.BASE_URL}/rating",
            json=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )

        response.raise_for_status()
        data = response.json()

        return self._parse_ups_response(data, request)

    def _format_address(self, address: Address) -> Dict:
        """Format address for UPS API"""
        return {
            "Name": address.name,
            "Address": {
                "AddressLine": [address.address_line1],
                "City": address.city,
                "StateProvinceCode": address.state,
                "PostalCode": address.zip_code,
                "CountryCode": address.country
            }
        }

    def _format_commodity(self, package: Package) -> Dict:
        """Format commodity for UPS API"""
        return {
            "FreightClass": package.freight_class or "50",
            "Weight": {
                "Value": str(package.weight),
                "UnitOfMeasurement": {
                    "Code": "LBS"
                }
            },
            "Dimensions": {
                "Length": str(package.length),
                "Width": str(package.width),
                "Height": str(package.height),
                "UnitOfMeasurement": {
                    "Code": "IN"
                }
            },
            "NumberOfPieces": str(package.quantity)
        }

    def _parse_ups_response(self, data: Dict, request: ShipmentRequest) -> List[RateQuote]:
        """Parse UPS rate response"""
        quotes = []

        rate_response = data.get('FreightRateResponse', {})
        rate = rate_response.get('Rate', {})

        # Parse charges
        base_charge = float(rate.get('Type', {}).get('NetCharge', {}).get('MonetaryValue', 0))
        fuel_surcharge = 0
        accessorials = {}

        # Parse accessorial charges
        for charge in rate.get('AlternateRatesResponse', {}).get('AlternateRateType', []):
            charge_type = charge.get('Code')
            amount = float(charge.get('MonetaryValue', 0))

            if 'FUEL' in charge_type:
                fuel_surcharge = amount
            else:
                accessorials[charge_type] = amount

        total = float(rate.get('TotalShipmentCharge', {}).get('MonetaryValue', 0))

        # Transit time
        time_in_transit = rate_response.get('TimeInTransit', {})
        transit_days = int(time_in_transit.get('DaysInTransit', 0))

        quote = RateQuote(
            carrier="UPS Freight",
            service_level="Standard LTL",
            mode=FreightMode.LTL,
            base_rate=base_charge,
            fuel_surcharge=fuel_surcharge,
            accessorial_charges=accessorials,
            total_cost=total,
            transit_days=transit_days,
            estimated_delivery=request.ship_date,
            metadata={}
        )

        quotes.append(quote)

        return quotes


class RateShoppingEngine:
    """
    Multi-carrier rate shopping engine.
    Compares rates across multiple carriers and returns sorted results.
    """

    def __init__(self):
        self.carriers: List[CarrierRatingAPI] = []

    def add_carrier(self, carrier_api: CarrierRatingAPI):
        """Register a carrier for rate shopping"""
        self.carriers.append(carrier_api)

    def get_rates(self, request: ShipmentRequest) -> List[RateQuote]:
        """
        Get rates from all registered carriers.
        Returns sorted list (lowest cost first).
        """
        all_quotes = []

        for carrier_api in self.carriers:
            try:
                quotes = carrier_api.get_rate_quote(request)
                all_quotes.extend(quotes)
            except Exception as e:
                print(f"Error getting rates from {carrier_api.__class__.__name__}: {e}")

        # Sort by total cost
        all_quotes.sort(key=lambda q: q.total_cost)

        return all_quotes

    def get_best_rate(
        self,
        request: ShipmentRequest,
        criteria: str = "lowest_cost"
    ) -> Optional[RateQuote]:
        """
        Get best rate based on specified criteria.

        Criteria:
        - lowest_cost: Lowest total cost
        - fastest: Shortest transit time
        - best_value: Balance of cost and speed
        """
        quotes = self.get_rates(request)

        if not quotes:
            return None

        if criteria == "lowest_cost":
            return quotes[0]  # Already sorted by cost

        elif criteria == "fastest":
            return min(quotes, key=lambda q: q.transit_days)

        elif criteria == "best_value":
            # Calculate value score: weight cost and speed
            for quote in quotes:
                # Normalize cost and transit time to 0-1 scale
                min_cost = quotes[0].total_cost
                max_cost = quotes[-1].total_cost
                cost_score = (quote.total_cost - min_cost) / (max_cost - min_cost) if max_cost > min_cost else 0

                min_transit = min(q.transit_days for q in quotes)
                max_transit = max(q.transit_days for q in quotes)
                transit_score = (quote.transit_days - min_transit) / (max_transit - min_transit) if max_transit > min_transit else 0

                # Combined score (lower is better)
                # Weight: 60% cost, 40% transit time
                quote.metadata['value_score'] = (cost_score * 0.6) + (transit_score * 0.4)

            return min(quotes, key=lambda q: q.metadata['value_score'])

        return None

    def get_rate_comparison(self, request: ShipmentRequest) -> Dict:
        """Get detailed rate comparison"""
        quotes = self.get_rates(request)

        if not quotes:
            return {"error": "No quotes available"}

        return {
            "lowest_cost": quotes[0],
            "fastest": min(quotes, key=lambda q: q.transit_days),
            "all_quotes": quotes,
            "savings_vs_highest": quotes[-1].total_cost - quotes[0].total_cost if quotes else 0,
            "avg_cost": sum(q.total_cost for q in quotes) / len(quotes) if quotes else 0
        }


# ============================================================================
# Example Usage
# ============================================================================


def example_usage():
    # Create shipment request
    origin = Address(
        name="ABC Distribution",
        address_line1="123 Main St",
        address_line2=None,
        city="Dallas",
        state="TX",
        zip_code="75201",
        country="US"
    )

    destination = Address(
        name="XYZ Warehouse",
        address_line1="456 Oak Ave",
        address_line2=None,
        city="Chicago",
        state="IL",
        zip_code="60601",
        country="US"
    )

    packages = [
        Package(
            length=48,
            width=40,
            height=48,
            weight=500,
            quantity=10,
            freight_class="70",
            stackable=True
        ),
        Package(
            length=24,
            width=24,
            height=24,
            weight=150,
            quantity=5,
            freight_class="85",
            stackable=True
        )
    ]

    request = ShipmentRequest(
        origin=origin,
        destination=destination,
        packages=packages,
        ship_date=date.today(),
        lift_gate_required=False,
        inside_delivery=False
    )

    # Initialize rate shopping engine
    engine = RateShoppingEngine()

    # Add carriers
    fedex_api = FedExFreightAPI(
        api_key="fedex_key",
        account_number="123456789"
    )
    engine.add_carrier(fedex_api)

    ups_api = UPSFreightAPI(
        api_key="ups_key",
        account_number="987654321"
    )
    engine.add_carrier(ups_api)

    # Get rate comparison
    print("=== Freight Rate Shopping ===\n")

    comparison = engine.get_rate_comparison(request)

    print(f"Lowest Cost Option:")
    lowest = comparison['lowest_cost']
    print(f"  {lowest.carrier} - {lowest.service_level}")
    print(f"  Cost: ${lowest.total_cost:.2f}")
    print(f"  Transit: {lowest.transit_days} days")
    print(f"  Base Rate: ${lowest.base_rate:.2f}")
    print(f"  Fuel Surcharge: ${lowest.fuel_surcharge:.2f}")

    print(f"\nFastest Option:")
    fastest = comparison['fastest']
    print(f"  {fastest.carrier} - {fastest.service_level}")
    print(f"  Cost: ${fastest.total_cost:.2f}")
    print(f"  Transit: {fastest.transit_days} days")

    print(f"\nSavings: ${comparison['savings_vs_highest']:.2f}")

    print(f"\n=== All Quotes ===")
    for i, quote in enumerate(comparison['all_quotes'], 1):
        print(f"{i}. {quote.carrier} - ${quote.total_cost:.2f} ({quote.transit_days} days)")

    # Get best value option
    best_value = engine.get_best_rate(request, criteria="best_value")
    print(f"\n=== Best Value Option ===")
    print(f"{best_value.carrier} - ${best_value.total_cost:.2f} ({best_value.transit_days} days)")
    print(f"Value Score: {best_value.metadata['value_score']:.3f}")


if __name__ == "__main__":
    example_usage()

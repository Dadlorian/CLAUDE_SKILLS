"""
Listing Syndication Service
Syndicates property listings to multiple portals (Zillow, Trulia, Realtor.com)
"""

import requests
import json
from datetime import datetime
import xml.etree.ElementTree as ET
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ListingSyndicator:
    """Syndicate listings to multiple real estate portals"""

    def __init__(self, config):
        self.config = config
        self.portals = {
            'zillow': ZillowSyndicator(config.get('zillow', {})),
            'trulia': TruliaSyndicator(config.get('trulia', {})),
            'realtor': RealtorSyndicator(config.get('realtor', {}))
        }

    def syndicate_listing(self, listing: Dict) -> Dict:
        """
        Syndicate a listing to all configured portals

        Args:
            listing: Property listing dictionary

        Returns:
            Dict with syndication results per portal
        """
        results = {
            'success': [],
            'failed': [],
            'skipped': []
        }

        # Check eligibility
        if not self.is_eligible_for_syndication(listing):
            logger.warning(f"Listing {listing['property_id']} not eligible for syndication")
            results['skipped'].append('not_eligible')
            return results

        # Syndicate to each portal
        for portal_name, syndicator in self.portals.items():
            try:
                # Check agent opt-in
                if not listing.get('agent', {}).get('syndication', {}).get(portal_name, True):
                    logger.info(f"Agent opted out of {portal_name}")
                    results['skipped'].append(portal_name)
                    continue

                # Transform and send
                portal_listing = syndicator.transform(listing)
                response = syndicator.send(portal_listing)

                logger.info(f"Successfully syndicated to {portal_name}")
                results['success'].append({
                    'portal': portal_name,
                    'response': response
                })

            except Exception as e:
                logger.error(f"Failed to syndicate to {portal_name}: {e}")
                results['failed'].append({
                    'portal': portal_name,
                    'error': str(e)
                })

        return results

    def is_eligible_for_syndication(self, listing: Dict) -> bool:
        """Check if listing qualifies for syndication"""
        return all([
            listing.get('status') == 'active',
            listing.get('price', 0) > 0,
            len(listing.get('photos', [])) >= 1,
            len(listing.get('description', '')) >= 100,
            listing.get('latitude') is not None,
            listing.get('longitude') is not None
        ])

    def remove_listing(self, property_id: str, portals: List[str] = None):
        """Remove listing from portals"""
        if portals is None:
            portals = self.portals.keys()

        for portal_name in portals:
            try:
                syndicator = self.portals[portal_name]
                syndicator.remove(property_id)
                logger.info(f"Removed listing from {portal_name}")
            except Exception as e:
                logger.error(f"Failed to remove from {portal_name}: {e}")


class ZillowSyndicator:
    """Zillow Bridge API integration"""

    def __init__(self, config):
        self.api_key = config.get('api_key')
        self.api_url = config.get('api_url', 'https://api.zillow.com/bridge')

    def transform(self, listing: Dict) -> Dict:
        """Transform to Zillow format"""
        return {
            'partner_property_id': listing['property_id'],
            'address': {
                'street': listing['address'],
                'city': listing['city'],
                'state': listing['state'],
                'zip': listing['zip']
            },
            'lat': listing['latitude'],
            'lng': listing['longitude'],
            'price': listing['price'],
            'bedrooms': listing['bedrooms'],
            'bathrooms': listing['bathrooms'],
            'square_feet': listing.get('sqft'),
            'lot_size': listing.get('lot_size'),
            'year_built': listing.get('year_built'),
            'property_type': self._map_property_type(listing['property_type']),
            'listing_status': 'for_sale',
            'description': listing['description'],
            'photos': [photo['url'] for photo in listing.get('photos', [])[:25]],
            'agent': {
                'name': listing.get('agent', {}).get('name'),
                'email': listing.get('agent', {}).get('email'),
                'phone': listing.get('agent', {}).get('phone')
            }
        }

    def send(self, listing: Dict) -> Dict:
        """Send listing to Zillow"""
        response = requests.post(
            f"{self.api_url}/Listing.htm",
            json=listing,
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
        )
        response.raise_for_status()
        return response.json()

    def remove(self, property_id: str):
        """Remove listing from Zillow"""
        response = requests.delete(
            f"{self.api_url}/Listing.htm",
            json={'partner_property_id': property_id},
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        response.raise_for_status()

    def _map_property_type(self, prop_type: str) -> str:
        mapping = {
            'single_family': 'SingleFamily',
            'condo': 'Condo',
            'townhouse': 'Townhouse',
            'multi_family': 'MultiFamily',
            'land': 'Lot'
        }
        return mapping.get(prop_type, 'SingleFamily')


class TruliaSyndicator:
    """Trulia syndication (similar to Zillow, owned by Zillow Group)"""

    def __init__(self, config):
        self.api_key = config.get('api_key')
        self.api_url = config.get('api_url', 'https://api.trulia.com/listings')

    def transform(self, listing: Dict) -> Dict:
        """Transform to Trulia format"""
        return {
            'listing_id': listing['property_id'],
            'address': f"{listing['address']}, {listing['city']}, {listing['state']} {listing['zip']}",
            'price': listing['price'],
            'beds': listing['bedrooms'],
            'baths': listing['bathrooms'],
            'sqft': listing.get('sqft'),
            'property_type': listing['property_type'].upper(),
            'status': 'for_sale',
            'description': listing['description'],
            'images': [photo['url'] for photo in listing.get('photos', [])],
            'latitude': listing['latitude'],
            'longitude': listing['longitude']
        }

    def send(self, listing: Dict) -> Dict:
        """Send to Trulia"""
        response = requests.post(
            self.api_url,
            json=listing,
            headers={'X-API-Key': self.api_key}
        )
        response.raise_for_status()
        return response.json()

    def remove(self, property_id: str):
        """Remove from Trulia"""
        response = requests.delete(
            f"{self.api_url}/{property_id}",
            headers={'X-API-Key': self.api_key}
        )
        response.raise_for_status()


class RealtorSyndicator:
    """Realtor.com syndication via XML feed"""

    def __init__(self, config):
        self.feed_url = config.get('feed_url')

    def transform(self, listing: Dict) -> ET.Element:
        """Transform to Realtor.com XML format"""
        listing_elem = ET.Element('Listing')

        # Basic info
        ET.SubElement(listing_elem, 'ListingID').text = listing['property_id']
        ET.SubElement(listing_elem, 'Status').text = 'Active'
        ET.SubElement(listing_elem, 'Price').text = str(listing['price'])

        # Address
        address_elem = ET.SubElement(listing_elem, 'Address')
        ET.SubElement(address_elem, 'StreetAddress').text = listing['address']
        ET.SubElement(address_elem, 'City').text = listing['city']
        ET.SubElement(address_elem, 'State').text = listing['state']
        ET.SubElement(address_elem, 'Zip').text = listing['zip']

        # Details
        details_elem = ET.SubElement(listing_elem, 'Details')
        ET.SubElement(details_elem, 'Bedrooms').text = str(listing['bedrooms'])
        ET.SubElement(details_elem, 'Bathrooms').text = str(listing['bathrooms'])
        if listing.get('sqft'):
            ET.SubElement(details_elem, 'SquareFeet').text = str(listing['sqft'])

        # Description
        description = ET.SubElement(listing_elem, 'Description')
        description.text = ET.CDATA(listing['description'])

        # Photos
        photos_elem = ET.SubElement(listing_elem, 'Photos')
        for i, photo in enumerate(listing.get('photos', [])[:30], 1):
            photo_elem = ET.SubElement(photos_elem, 'Photo')
            ET.SubElement(photo_elem, 'URL').text = photo['url']
            ET.SubElement(photo_elem, 'Order').text = str(i)

        return listing_elem

    def send(self, listing_elem: ET.Element) -> Dict:
        """Send to Realtor.com (typically via FTP or API)"""
        # In practice, this might generate XML file for FTP upload
        # or POST to their API
        xml_str = ET.tostring(listing_elem, encoding='unicode')
        # Implementation depends on Realtor.com's requirements
        return {'status': 'success', 'xml': xml_str}

    def remove(self, property_id: str):
        """Remove from Realtor.com"""
        # Typically done by sending status update to "Sold" or "Withdrawn"
        pass


# Usage example
if __name__ == '__main__':
    config = {
        'zillow': {
            'api_key': 'your_zillow_api_key',
            'api_url': 'https://api.zillow.com/bridge'
        },
        'trulia': {
            'api_key': 'your_trulia_api_key'
        }
    }

    syndicator = ListingSyndicator(config)

    listing = {
        'property_id': '12345',
        'status': 'active',
        'address': '123 Main St',
        'city': 'Austin',
        'state': 'TX',
        'zip': '78701',
        'latitude': 30.2672,
        'longitude': -97.7431,
        'price': 450000,
        'bedrooms': 3,
        'bathrooms': 2,
        'sqft': 2000,
        'property_type': 'single_family',
        'description': 'Beautiful home in downtown Austin with modern finishes...',
        'photos': [
            {'url': 'https://cdn.example.com/photo1.jpg'},
            {'url': 'https://cdn.example.com/photo2.jpg'}
        ],
        'agent': {
            'name': 'John Smith',
            'email': 'john@realty.com',
            'phone': '512-555-0100',
            'syndication': {
                'zillow': True,
                'trulia': True,
                'realtor': True
            }
        }
    }

    results = syndicator.syndicate_listing(listing)
    print(f"Syndication results: {results}")

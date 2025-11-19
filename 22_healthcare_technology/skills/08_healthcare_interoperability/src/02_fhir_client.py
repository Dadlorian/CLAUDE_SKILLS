#!/usr/bin/env python3
"""
FHIR R4 Client Library
Production-grade client for interacting with FHIR servers
"""

import requests
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

class FHIRClient:
    """Client for FHIR R4 API interactions"""

    def __init__(self, base_url: str, access_token: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.headers = {
            'Accept': 'application/fhir+json',
            'Content-Type': 'application/fhir+json'
        }

        if access_token:
            self.headers['Authorization'] = f'Bearer {access_token}'
        elif api_key:
            self.headers['X-API-Key'] = api_key

    def create(self, resource_type: str, resource: Dict) -> Dict:
        """Create a FHIR resource"""
        url = urljoin(self.base_url, f'/fhir/{resource_type}')

        try:
            response = self.session.post(url, json=resource, headers=self.headers)
            response.raise_for_status()

            logger.info(f"Created {resource_type}")
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Create failed: {e}")
            raise

    def read(self, resource_type: str, resource_id: str) -> Dict:
        """Read a FHIR resource"""
        url = urljoin(self.base_url, f'/fhir/{resource_type}/{resource_id}')

        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Read failed: {e}")
            raise

    def update(self, resource_type: str, resource_id: str, resource: Dict) -> Dict:
        """Update a FHIR resource"""
        url = urljoin(self.base_url, f'/fhir/{resource_type}/{resource_id}')
        resource['id'] = resource_id

        try:
            response = self.session.put(url, json=resource, headers=self.headers)
            response.raise_for_status()

            logger.info(f"Updated {resource_type}/{resource_id}")
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Update failed: {e}")
            raise

    def delete(self, resource_type: str, resource_id: str) -> bool:
        """Delete a FHIR resource"""
        url = urljoin(self.base_url, f'/fhir/{resource_type}/{resource_id}')

        try:
            response = self.session.delete(url, headers=self.headers)
            response.raise_for_status()

            logger.info(f"Deleted {resource_type}/{resource_id}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Delete failed: {e}")
            raise

    def search(self, resource_type: str, params: Dict) -> Dict:
        """Search for FHIR resources"""
        url = urljoin(self.base_url, f'/fhir/{resource_type}')

        try:
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Search failed: {e}")
            raise

    def get_bundle(self, url: str) -> Dict:
        """Retrieve bundle from URL"""
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Bundle fetch failed: {e}")
            raise

    def search_all(self, resource_type: str, params: Dict) -> List[Dict]:
        """Search with pagination - return all results"""
        all_resources = []
        page = 1
        page_size = params.get('_count', 50)

        while True:
            params['_offset'] = (page - 1) * page_size

            bundle = self.search(resource_type, params)

            # Extract resources
            for entry in bundle.get('entry', []):
                all_resources.append(entry['resource'])

            # Check for next page
            next_link = next((l for l in bundle.get('link', []) if l['relation'] == 'next'), None)
            if not next_link:
                break

            page += 1

        return all_resources

    def batch_operation(self, operations: List[Dict]) -> Dict:
        """Execute batch operations"""
        bundle = {
            'resourceType': 'Bundle',
            'type': 'batch',
            'entry': operations
        }

        url = urljoin(self.base_url, '/fhir/')

        try:
            response = self.session.post(url, json=bundle, headers=self.headers)
            response.raise_for_status()

            logger.info(f"Batch operation completed with {len(operations)} items")
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Batch operation failed: {e}")
            raise

    def transaction_bundle(self, entries: List[Dict]) -> Dict:
        """Execute transaction (all-or-nothing)"""
        bundle = {
            'resourceType': 'Bundle',
            'type': 'transaction',
            'entry': entries
        }

        url = urljoin(self.base_url, '/fhir/')

        try:
            response = self.session.post(url, json=bundle, headers=self.headers)
            response.raise_for_status()

            logger.info(f"Transaction completed with {len(entries)} items")
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Transaction failed: {e}")
            raise

    def get_capability_statement(self) -> Dict:
        """Get server capability statement"""
        url = urljoin(self.base_url, '/fhir/metadata')

        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Capability statement fetch failed: {e}")
            raise

    def validate_resource(self, resource_type: str, resource: Dict) -> Dict:
        """Validate a resource against its profile"""
        url = urljoin(self.base_url, f'/fhir/{resource_type}/$validate')

        try:
            response = self.session.post(url, json=resource, headers=self.headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Validation failed: {e}")
            raise


if __name__ == '__main__':
    # Example usage
    client = FHIRClient('http://localhost:8080')

    # Create patient
    patient = {
        'resourceType': 'Patient',
        'name': [{'family': 'Doe', 'given': ['John']}],
        'birthDate': '1970-01-01',
        'gender': 'male'
    }

    created = client.create('Patient', patient)
    patient_id = created['id']
    print(f"Created patient: {patient_id}")

    # Read patient
    retrieved = client.read('Patient', patient_id)
    print(f"Retrieved: {retrieved['name'][0]['family']}")

    # Search patients
    results = client.search('Patient', {'family': 'Doe'})
    print(f"Found {results.get('total', 0)} patients")

    # Update patient
    retrieved['birthDate'] = '1970-01-02'
    updated = client.update('Patient', patient_id, retrieved)
    print(f"Updated patient")

    # Delete patient
    client.delete('Patient', patient_id)
    print(f"Deleted patient")

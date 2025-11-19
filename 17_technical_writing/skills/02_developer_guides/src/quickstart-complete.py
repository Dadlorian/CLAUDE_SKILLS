#!/usr/bin/env python3

"""
Complete Quickstart Example: Payment Processing

This example demonstrates:
- API authentication
- Creating a charge
- Handling responses
- Error handling

Prerequisites:
- Python 3.8+
- pip install requests python-dotenv
"""

import os
import sys
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv('API_KEY', 'sk_live_YOUR_KEY_HERE')
API_BASE_URL = 'https://api.example.com/v1'

# Initialize HTTP session with authentication
session = requests.Session()
session.headers.update({
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
})


class APIError(Exception):
    """Custom exception for API errors"""
    def __init__(self, status_code: int, message: str, error_code: Optional[str] = None):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


def create_charge(
    amount: int,
    currency: str = 'usd',
    description: str = 'Test charge'
) -> Dict[str, Any]:
    """
    Create a charge

    Args:
        amount: Amount in cents (e.g., 2000 = $20.00)
        currency: Currency code (usd, eur, gbp, etc.)
        description: Charge description

    Returns:
        Charge response data

    Raises:
        APIError: If the API request fails
    """
    try:
        print('Creating charge...')
        print(f'Amount: ${amount / 100:.2f} {currency.upper()}')

        response = session.post(
            f'{API_BASE_URL}/charges',
            json={
                'amount': amount,
                'currency': currency,
                'description': description
            }
        )

        # Check for HTTP errors
        response.raise_for_status()

        data = response.json()

        print('\n✅ Charge created successfully!')
        print(f"Charge ID: {data['id']}")
        print(f"Status: {data['status']}")
        print(f"Amount: {data['amount']} {data['currency']}")

        return data

    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors
        status = e.response.status_code
        try:
            error_data = e.response.json()
            error_msg = error_data.get('error', {}).get('message', str(e))
            error_code = error_data.get('error', {}).get('code')
        except json.JSONDecodeError:
            error_msg = str(e)
            error_code = None

        print(f'\n❌ Error creating charge:')
        print(f'Status: {status}')
        print(f'Error: {error_msg}')

        # Specific error handling
        if status == 401:
            print('Action: Check your API key')
        elif status == 400:
            print('Action: Verify parameters (amount, currency, etc.)')
        elif status == 429:
            print('Action: Rate limited. Wait 1 minute before retrying.')

        raise APIError(status, error_msg, error_code)

    except requests.exceptions.ConnectionError:
        print('❌ Connection error. Check your internet connection.')
        raise
    except requests.exceptions.RequestException as e:
        print(f'❌ Request error: {str(e)}')
        raise


def get_charge(charge_id: str) -> Dict[str, Any]:
    """
    Retrieve a charge

    Args:
        charge_id: The charge ID to retrieve

    Returns:
        Charge details

    Raises:
        APIError: If the request fails
    """
    try:
        response = session.get(f'{API_BASE_URL}/charges/{charge_id}')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_msg = e.response.json().get('error', {}).get('message', str(e))
        print(f'❌ Failed to retrieve charge {charge_id}: {error_msg}')
        raise APIError(e.response.status_code, error_msg)


def refund_charge(charge_id: str) -> Dict[str, Any]:
    """
    Refund a charge

    Args:
        charge_id: The charge ID to refund

    Returns:
        Refund response data

    Raises:
        APIError: If the request fails
    """
    try:
        print(f'Refunding charge {charge_id}...')

        response = session.post(f'{API_BASE_URL}/charges/{charge_id}/refund')
        response.raise_for_status()

        data = response.json()

        print('✅ Refund processed')
        print(f"Refund ID: {data['refund_id']}")

        return data

    except requests.exceptions.HTTPError as e:
        error_msg = e.response.json().get('error', {}).get('message', str(e))
        print(f'❌ Failed to refund charge: {error_msg}')
        raise APIError(e.response.status_code, error_msg)


def list_charges(limit: int = 10) -> list:
    """
    List charges

    Args:
        limit: Maximum number of charges to return

    Returns:
        List of charges
    """
    try:
        response = session.get(
            f'{API_BASE_URL}/charges',
            params={'limit': limit}
        )
        response.raise_for_status()
        return response.json().get('data', [])
    except requests.exceptions.HTTPError as e:
        error_msg = e.response.json().get('error', {}).get('message', str(e))
        print(f'❌ Failed to list charges: {error_msg}')
        raise APIError(e.response.status_code, error_msg)


def main():
    """Main execution example"""
    try:
        # Create a test charge
        charge = create_charge(2000, 'usd', 'Test payment')

        # Retrieve the charge
        print('\nRetrieving charge details...')
        retrieved = get_charge(charge['id'])
        print(f"Retrieved status: {retrieved['status']}")

        # List recent charges
        print('\nListing recent charges...')
        charges = list_charges(5)
        print(f"Found {len(charges)} charges")

        # Uncomment to test refund
        # refund_charge(charge['id'])

        return 0

    except APIError as e:
        print(f'\nAPI Error: {e}')
        return 1
    except Exception as e:
        print(f'\nUnexpected error: {e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())

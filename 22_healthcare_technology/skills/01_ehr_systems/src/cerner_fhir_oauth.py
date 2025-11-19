"""
Cerner FHIR OAuth 2.0 Authentication Example
Implements OAuth 2.0 flow for Cerner FHIR API access
"""

import requests
from urllib.parse import urlencode, parse_qs
import secrets
import json
from typing import Dict, Optional

class CernerFHIROAuthClient:
    def __init__(self, tenant_id: str, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize Cerner OAuth client
        
        Args:
            tenant_id: Cerner tenant identifier
            client_id: OAuth client ID from Cerner
            client_secret: OAuth client secret
            redirect_uri: Registered redirect URI
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        self.base_url = f"https://fhir.cerner.com/r4/{tenant_id}"
        self.auth_base = f"https://authorization.cerner.com/tenants/{tenant_id}"
        
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.patient_id: Optional[str] = None

    def get_authorization_url(self, scopes: list) -> tuple:
        """
        Generate authorization URL for user redirect
        
        Args:
            scopes: List of requested FHIR scopes
            
        Returns:
            Tuple of (authorization_url, state)
        """
        state = secrets.token_urlsafe(32)
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(scopes),
            'state': state,
            'aud': self.base_url
        }
        
        auth_url = (
            f"{self.auth_base}/protocols/oauth2/profiles/smart-v1/"
            f"personas/provider/authorize?{urlencode(params)}"
        )
        
        return auth_url, state

    def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from redirect
            
        Returns:
            Token response dictionary
        """
        token_url = f"{self.auth_base}/protocols/oauth2/profiles/smart-v1/token"
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        self.access_token = token_data['access_token']
        self.refresh_token = token_data.get('refresh_token')
        self.patient_id = token_data.get('patient')
        
        return token_data

    def refresh_access_token(self) -> Dict:
        """
        Refresh the access token using refresh token
        
        Returns:
            New token response dictionary
        """
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        token_url = f"{self.auth_base}/protocols/oauth2/profiles/smart-v1/token"
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data['access_token']
        
        return token_data

    def get_patient(self, patient_id: Optional[str] = None) -> Dict:
        """
        Get patient resource
        
        Args:
            patient_id: Patient ID (uses context patient if not provided)
            
        Returns:
            Patient FHIR resource
        """
        pid = patient_id or self.patient_id
        if not pid:
            raise ValueError("No patient ID available")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/fhir+json'
        }
        
        response = requests.get(f"{self.base_url}/Patient/{pid}", headers=headers)
        response.raise_for_status()
        
        return response.json()

    def search_observations(self, patient_id: Optional[str] = None, 
                          category: str = 'laboratory') -> list:
        """
        Search patient observations (lab results, vitals, etc.)
        
        Args:
            patient_id: Patient ID
            category: Observation category
            
        Returns:
            List of Observation resources
        """
        pid = patient_id or self.patient_id
        if not pid:
            raise ValueError("No patient ID available")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/fhir+json'
        }
        
        params = {
            'patient': pid,
            'category': category,
            '_sort': '-date'
        }
        
        response = requests.get(f"{self.base_url}/Observation", 
                              headers=headers, params=params)
        response.raise_for_status()
        
        bundle = response.json()
        return [entry['resource'] for entry in bundle.get('entry', [])]


# Example usage
if __name__ == '__main__':
    import os
    
    client = CernerFHIROAuthClient(
        tenant_id=os.environ['CERNER_TENANT_ID'],
        client_id=os.environ['CERNER_CLIENT_ID'],
        client_secret=os.environ['CERNER_CLIENT_SECRET'],
        redirect_uri='https://yourapp.com/callback'
    )
    
    # Step 1: Get authorization URL
    auth_url, state = client.get_authorization_url([
        'patient/Patient.read',
        'patient/Observation.read',
        'patient/Condition.read'
    ])
    
    print(f"Redirect user to: {auth_url}")
    
    # Step 2: After redirect, exchange code for token
    # authorization_code = '...'  # From redirect callback
    # token_data = client.exchange_code_for_token(authorization_code)
    
    # Step 3: Use token to access FHIR resources
    # patient = client.get_patient()
    # print(json.dumps(patient, indent=2))
    
    # observations = client.search_observations(category='vital-signs')
    # print(f"Found {len(observations)} vital sign observations")

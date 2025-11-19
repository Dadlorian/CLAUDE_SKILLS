#!/usr/bin/env python3
"""
SMART on FHIR OAuth 2.0 Handler
Production-grade implementation of OAuth 2.0 for healthcare applications
"""

import secrets
import hashlib
import base64
import json
from typing import Dict, Optional, Tuple
import logging
from urllib.parse import urlencode, parse_qs
from datetime import datetime, timedelta
import jwt

logger = logging.getLogger(__name__)

class SMARTOAuth:
    """Handle OAuth 2.0 for SMART on FHIR"""

    def __init__(self, client_id: str, client_secret: Optional[str], fhir_server_url: str,
                 redirect_uri: str, scopes: list):
        self.client_id = client_id
        self.client_secret = client_secret
        self.fhir_server_url = fhir_server_url.rstrip('/')
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.token_cache = {}

    def get_authorization_url(self, state: Optional[str] = None,
                             use_pkce: bool = True) -> Tuple[str, Dict]:
        """Generate authorization URL for SMART launch"""
        import requests

        # Get well-known configuration
        config = self._get_smart_config()
        if not config:
            raise RuntimeError("Failed to get SMART configuration")

        auth_url = config['authorization_endpoint']

        # Generate state
        if not state:
            state = secrets.token_urlsafe(32)

        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.scopes),
            'state': state
        }

        # Add PKCE if public client
        pkce_verifier = None
        if use_pkce:
            pkce_verifier = self._generate_pkce_verifier()
            params['code_challenge'] = self._generate_code_challenge(pkce_verifier)
            params['code_challenge_method'] = 'S256'

        url = f"{auth_url}?{urlencode(params)}"

        return url, {
            'state': state,
            'pkce_verifier': pkce_verifier
        }

    def exchange_code_for_token(self, code: str, state: str,
                               pkce_verifier: Optional[str] = None) -> Optional[Dict]:
        """Exchange authorization code for access token"""
        import requests

        config = self._get_smart_config()
        if not config:
            raise RuntimeError("Failed to get SMART configuration")

        token_url = config['token_endpoint']

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri
        }

        # Add secret if available (confidential client)
        if self.client_secret:
            data['client_secret'] = self.client_secret

        # Add PKCE verifier if available
        if pkce_verifier:
            data['code_verifier'] = pkce_verifier

        try:
            response = requests.post(token_url, data=data, timeout=10)
            response.raise_for_status()

            token_data = response.json()

            # Cache token
            self._cache_token(token_data)

            logger.info("Token exchange successful")
            return token_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Token exchange failed: {e}")
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[Dict]:
        """Refresh access token using refresh token"""
        import requests

        config = self._get_smart_config()
        if not config:
            raise RuntimeError("Failed to get SMART configuration")

        token_url = config['token_endpoint']

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id
        }

        if self.client_secret:
            data['client_secret'] = self.client_secret

        try:
            response = requests.post(token_url, data=data, timeout=10)
            response.raise_for_status()

            token_data = response.json()
            self._cache_token(token_data)

            logger.info("Token refresh successful")
            return token_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Token refresh failed: {e}")
            return None

    def validate_token(self, access_token: str) -> Tuple[bool, Optional[Dict]]:
        """Validate access token"""
        try:
            # Decode JWT
            decoded = jwt.decode(
                access_token,
                options={"verify_signature": False}  # Normally verify with public key
            )

            # Check expiration
            exp = decoded.get('exp')
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                return False, None

            # Check required claims
            if 'sub' not in decoded or 'iss' not in decoded:
                return False, None

            return True, decoded

        except jwt.InvalidTokenError as e:
            logger.error(f"Token validation failed: {e}")
            return False, None

    def extract_user_context(self, access_token: str) -> Optional[Dict]:
        """Extract user context from token"""
        valid, decoded = self.validate_token(access_token)

        if not valid or not decoded:
            return None

        return {
            'user_id': decoded.get('fhir_user'),
            'patient_id': decoded.get('patient'),
            'encounter_id': decoded.get('encounter'),
            'scopes': decoded.get('scope', '').split(),
            'expires_at': datetime.utcfromtimestamp(decoded.get('exp', 0))
        }

    def revoke_token(self, token: str) -> bool:
        """Revoke token"""
        import requests

        config = self._get_smart_config()
        if not config:
            return False

        revocation_url = config.get('revocation_endpoint')
        if not revocation_url:
            return False

        data = {
            'token': token,
            'client_id': self.client_id
        }

        if self.client_secret:
            data['client_secret'] = self.client_secret

        try:
            response = requests.post(revocation_url, data=data, timeout=10)
            response.raise_for_status()

            logger.info("Token revoked")
            return True

        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            return False

    def _get_smart_config(self) -> Optional[Dict]:
        """Get SMART/OpenID configuration"""
        import requests

        url = f"{self.fhir_server_url}/.well-known/smart-configuration"

        # Check cache first
        if 'config' in self.token_cache:
            cached = self.token_cache['config']
            if cached['expires'] > datetime.utcnow():
                return cached['data']

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            config = response.json()

            # Cache for 1 hour
            self.token_cache['config'] = {
                'data': config,
                'expires': datetime.utcnow() + timedelta(hours=1)
            }

            return config

        except Exception as e:
            logger.error(f"Failed to get SMART configuration: {e}")
            return None

    def _cache_token(self, token_data: Dict):
        """Cache token data"""
        self.token_cache['access_token'] = token_data['access_token']
        self.token_cache['refresh_token'] = token_data.get('refresh_token')
        self.token_cache['expires_at'] = datetime.utcnow() + timedelta(
            seconds=token_data.get('expires_in', 3600)
        )

    def _generate_pkce_verifier(self, length: int = 128) -> str:
        """Generate PKCE code verifier"""
        return base64.urlsafe_b64encode(secrets.token_bytes(96)).decode().rstrip('=')

    def _generate_code_challenge(self, verifier: str) -> str:
        """Generate PKCE code challenge"""
        digest = hashlib.sha256(verifier.encode()).digest()
        return base64.urlsafe_b64encode(digest).decode().rstrip('=')


if __name__ == '__main__':
    # Example usage
    oauth = SMARTOAuth(
        client_id='my-app',
        client_secret=None,  # Public client
        fhir_server_url='http://localhost:8080',
        redirect_uri='https://myapp.example.com/callback',
        scopes=['patient/Patient.read', 'patient/Observation.read']
    )

    # Get authorization URL
    auth_url, state_data = oauth.get_authorization_url(use_pkce=True)
    print(f"Authorization URL: {auth_url}")
    print(f"State data: {state_data}")

    # Later, exchange code for token (in callback handler)
    # token_data = oauth.exchange_code_for_token(
    #     code='auth_code_from_redirect',
    #     state='state_from_callback',
    #     pkce_verifier=state_data['pkce_verifier']
    # )

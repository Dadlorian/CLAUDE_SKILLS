"""
Production-Ready Python API Client
Implements OAuth2 authentication, retry logic, and error handling

Module: api_client
Requires: requests, pydantic, tenacity
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class APIConfig:
    """API client configuration"""
    base_url: str
    client_id: str
    client_secret: str
    timeout: int = 30
    max_retries: int = 3
    backoff_factor: float = 0.5
    verify_ssl: bool = True


class OAuth2Client:
    """OAuth2 authentication client"""

    def __init__(self, config: APIConfig):
        """Initialize OAuth2 client"""
        self.config = config
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None

    def get_token(self, auth_endpoint: str, scopes: List[str]) -> Dict[str, Any]:
        """
        Authenticate and get access token

        Args:
            auth_endpoint: OAuth2 token endpoint
            scopes: List of requested scopes

        Returns:
            Token response with access_token, refresh_token, etc.

        Raises:
            requests.RequestException: If authentication fails
        """
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'scope': ' '.join(scopes)
        }

        try:
            response = requests.post(
                auth_endpoint,
                data=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')

            # Calculate token expiration
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            logger.info(f"Successfully authenticated. Token expires at {self.token_expires_at}")
            return token_data

        except requests.RequestException as e:
            logger.error(f"Authentication failed: {e}")
            raise

    def refresh(self, auth_endpoint: str) -> Dict[str, Any]:
        """
        Refresh access token

        Args:
            auth_endpoint: OAuth2 token endpoint

        Returns:
            New token response

        Raises:
            ValueError: If no refresh token available
        """
        if not self.refresh_token:
            raise ValueError("No refresh token available")

        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret
        }

        response = requests.post(
            auth_endpoint,
            data=payload,
            timeout=self.config.timeout
        )
        response.raise_for_status()

        return self.get_token(auth_endpoint, [])

    def is_token_expired(self) -> bool:
        """Check if current token is expired"""
        if not self.token_expires_at:
            return True

        return datetime.utcnow() >= self.token_expires_at


class APIClient:
    """
    Production-ready API client with OAuth2, retry logic, and error handling
    """

    def __init__(self, config: APIConfig, oauth2: Optional[OAuth2Client] = None):
        """
        Initialize API client

        Args:
            config: API configuration
            oauth2: Optional OAuth2 client for authentication
        """
        self.config = config
        self.oauth2 = oauth2
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Create requests session with retry strategy

        Returns:
            Configured requests Session
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
            backoff_factor=self.config.backoff_factor
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _get_headers(self) -> Dict[str, str]:
        """
        Get request headers with authentication

        Returns:
            Headers dictionary
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'PythonAPIClient/1.0'
        }

        if self.oauth2 and self.oauth2.access_token:
            headers['Authorization'] = f'Bearer {self.oauth2.access_token}'

        return headers

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with error handling

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters

        Returns:
            Response object

        Raises:
            requests.RequestException: If request fails
        """
        url = urljoin(self.config.base_url, endpoint)
        headers = self._get_headers()

        try:
            response = self.session.request(
                method,
                url,
                headers=headers,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
                **kwargs
            )

            # Log request details
            logger.debug(f"{method} {endpoint} -> {response.status_code}")

            # Handle error responses
            if response.status_code == 401:
                logger.warning("Authentication failed (401)")
                raise ValueError("Unauthorized - invalid or expired token")

            if response.status_code == 403:
                raise PermissionError("Insufficient permissions (403)")

            if response.status_code == 404:
                raise ValueError(f"Resource not found (404)")

            if response.status_code >= 500:
                raise requests.HTTPError(f"Server error: {response.status_code}")

            response.raise_for_status()
            return response

        except requests.RequestException as e:
            logger.error(f"Request failed: {method} {endpoint} - {e}")
            raise

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make GET request

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response JSON
        """
        response = self._make_request('GET', endpoint, params=params)
        return response.json()

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make POST request

        Args:
            endpoint: API endpoint
            data: Form data
            json_data: JSON payload

        Returns:
            Response JSON
        """
        kwargs = {}
        if json_data:
            kwargs['json'] = json_data
        elif data:
            kwargs['data'] = data

        response = self._make_request('POST', endpoint, **kwargs)
        return response.json()

    def patch(
        self,
        endpoint: str,
        json_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make PATCH request

        Args:
            endpoint: API endpoint
            json_data: JSON payload

        Returns:
            Response JSON
        """
        response = self._make_request('PATCH', endpoint, json=json_data)
        return response.json()

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        Make DELETE request

        Args:
            endpoint: API endpoint

        Returns:
            Response JSON
        """
        response = self._make_request('DELETE', endpoint)
        return response.json() if response.text else {}

    def close(self):
        """Close the session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Example usage
class UserClient:
    """Specialized client for user operations"""

    def __init__(self, api_client: APIClient):
        """Initialize user client"""
        self.api_client = api_client

    def list_users(self, page: int = 1, limit: int = 10) -> List[Dict]:
        """List users with pagination"""
        return self.api_client.get(
            '/users',
            params={'page': page, 'limit': limit}
        )

    def create_user(self, user_data: Dict[str, Any]) -> Dict:
        """Create new user"""
        return self.api_client.post('/users', json_data=user_data)

    def get_user(self, user_id: str) -> Dict:
        """Get user by ID"""
        return self.api_client.get(f'/users/{user_id}')

    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Dict:
        """Update user"""
        return self.api_client.patch(f'/users/{user_id}', updates)

    def delete_user(self, user_id: str) -> Dict:
        """Delete user"""
        return self.api_client.delete(f'/users/{user_id}')


if __name__ == '__main__':
    # Example: Using the API client
    config = APIConfig(
        base_url='https://api.example.com/v1',
        client_id='your-client-id',
        client_secret='your-client-secret',
        timeout=30
    )

    # Create OAuth2 client
    oauth2 = OAuth2Client(config)

    # Authenticate
    try:
        oauth2.get_token(
            'https://auth.example.com/oauth/token',
            scopes=['users.read', 'users.write']
        )
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        exit(1)

    # Use API client
    with APIClient(config, oauth2) as api_client:
        # List users
        try:
            users = api_client.get('/users', params={'limit': 10})
            logger.info(f"Retrieved {len(users.get('items', []))} users")

            # Create user
            new_user = api_client.post(
                '/users',
                json_data={
                    'firstName': 'John',
                    'lastName': 'Doe',
                    'email': 'john@example.com'
                }
            )
            logger.info(f"Created user: {new_user['id']}")

        except Exception as e:
            logger.error(f"Error: {e}")

"""
MLS RETS Client
Python client for connecting to MLS via RETS protocol
"""

import requests
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
from datetime import datetime
import hashlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RETSClient:
    """RETS 1.7.2 client for MLS integration"""

    def __init__(self, config):
        self.login_url = config['login_url']
        self.username = config['username']
        self.password = config['password']
        self.user_agent = config.get('user_agent', 'PythonRETS/1.0')
        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(self.username, self.password)
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'RETS-Version': 'RETS/1.7.2'
        })
        self.urls = {}
        self.logged_in = False

    def login(self):
        """Login to RETS server"""
        try:
            response = self.session.get(self.login_url)
            response.raise_for_status()

            # Parse login response
            root = ET.fromstring(response.content)

            if root.get('ReplyCode') != '0':
                raise Exception(f"Login failed: {root.get('ReplyText')}")

            # Extract capability URLs
            rets_response = root.find('RETS-RESPONSE').text
            for line in rets_response.split('\n'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    self.urls[key] = value

            self.logged_in = True
            logger.info("Successfully logged in to RETS server")
            return True

        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise

    def logout(self):
        """Logout from RETS server"""
        if self.logged_in and 'Logout' in self.urls:
            try:
                self.session.get(self.urls['Logout'])
                self.logged_in = False
                logger.info("Logged out from RETS server")
            except Exception as e:
                logger.error(f"Logout failed: {e}")

    def search(self, resource='Property', class_name='RES', query='(Status=Active)',
               limit=1000, offset=0, select=None):
        """
        Search for listings

        Args:
            resource: Resource name (e.g., 'Property')
            class_name: Class name (e.g., 'RES' for residential)
            query: DMQL query string
            limit: Maximum number of results
            offset: Result offset
            select: Comma-separated list of fields to return

        Returns:
            List of property dictionaries
        """
        if not self.logged_in:
            self.login()

        search_url = self.urls.get('Search')
        if not search_url:
            raise Exception("Search URL not available")

        params = {
            'SearchType': resource,
            'Class': class_name,
            'Query': query,
            'Format': 'COMPACT-DECODED',
            'Limit': limit,
            'Offset': offset
        }

        if select:
            params['Select'] = select

        try:
            response = self.session.get(search_url, params=params)
            response.raise_for_status()

            # Parse response
            properties = self._parse_search_response(response.content)
            logger.info(f"Found {len(properties)} properties")
            return properties

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def _parse_search_response(self, content):
        """Parse RETS COMPACT format response"""
        root = ET.fromstring(content)

        if root.get('ReplyCode') != '0':
            raise Exception(f"Search failed: {root.get('ReplyText')}")

        # Get delimiter
        delimiter = root.find('DELIMITER')
        delim_char = chr(int(delimiter.get('value')))

        # Get columns
        columns_elem = root.find('COLUMNS')
        if columns_elem is None:
            return []

        columns = columns_elem.text.split(delim_char)

        # Parse data rows
        properties = []
        for data_elem in root.findall('DATA'):
            values = data_elem.text.split(delim_char)
            prop = dict(zip(columns, values))
            properties.append(prop)

        return properties

    def get_metadata(self, metadata_type='METADATA-RESOURCE', id='0'):
        """Get metadata from RETS server"""
        if not self.logged_in:
            self.login()

        metadata_url = self.urls.get('GetMetadata')
        if not metadata_url:
            raise Exception("GetMetadata URL not available")

        params = {
            'Type': metadata_type,
            'ID': id,
            'Format': 'COMPACT'
        }

        try:
            response = self.session.get(metadata_url, params=params)
            response.raise_for_status()

            root = ET.fromstring(response.content)

            if root.get('ReplyCode') != '0':
                raise Exception(f"GetMetadata failed: {root.get('ReplyText')}")

            return root

        except Exception as e:
            logger.error(f"GetMetadata failed: {e}")
            raise

    def get_object(self, resource='Property', object_type='Photo',
                   listing_id=None, photo_number='*'):
        """
        Get photos or documents

        Args:
            resource: Resource name
            object_type: Object type (e.g., 'Photo', 'Document')
            listing_id: Listing ID
            photo_number: Photo number or '*' for all

        Returns:
            List of photo dictionaries with 'data', 'content_type', 'object_id'
        """
        if not self.logged_in:
            self.login()

        getobject_url = self.urls.get('GetObject')
        if not getobject_url:
            raise Exception("GetObject URL not available")

        params = {
            'Resource': resource,
            'Type': object_type,
            'ID': f"{listing_id}:{photo_number}"
        }

        try:
            response = self.session.get(getobject_url, params=params)
            response.raise_for_status()

            # Parse multipart response
            photos = self._parse_multipart_response(response)
            logger.info(f"Retrieved {len(photos)} photos for listing {listing_id}")
            return photos

        except Exception as e:
            logger.error(f"GetObject failed: {e}")
            raise

    def _parse_multipart_response(self, response):
        """Parse multipart photo response"""
        content_type = response.headers.get('Content-Type', '')

        if 'multipart' not in content_type:
            # Single image
            return [{
                'data': response.content,
                'content_type': content_type,
                'object_id': '1'
            }]

        # Parse multipart
        photos = []
        boundary = content_type.split('boundary=')[1].strip('"')
        parts = response.content.split(f'--{boundary}'.encode())

        for part in parts:
            if not part or part == b'--\r\n':
                continue

            # Split headers and body
            try:
                headers_section, body = part.split(b'\r\n\r\n', 1)
                headers = headers_section.decode('utf-8')

                # Extract content type and object ID
                content_type = 'image/jpeg'
                object_id = '1'

                for line in headers.split('\r\n'):
                    if line.startswith('Content-Type:'):
                        content_type = line.split(':')[1].strip()
                    elif line.startswith('Object-ID:'):
                        object_id = line.split(':')[1].strip()

                photos.append({
                    'data': body.rstrip(b'\r\n'),
                    'content_type': content_type,
                    'object_id': object_id
                })
            except:
                continue

        return photos

    def incremental_search(self, since_timestamp):
        """
        Search for properties modified since a timestamp

        Args:
            since_timestamp: datetime object

        Returns:
            List of modified properties
        """
        # Format timestamp for RETS (YYYY-MM-DDTHH:MM:SS)
        timestamp_str = since_timestamp.strftime('%Y-%m-%dT%H:%M:%S')

        query = f"(ModificationTimestamp={timestamp_str}+)"

        return self.search(query=query, limit=10000)


# Usage example
if __name__ == '__main__':
    config = {
        'login_url': 'https://mls.example.com/rets/login',
        'username': 'your_username',
        'password': 'your_password'
    }

    client = RETSClient(config)

    try:
        # Login
        client.login()

        # Search active listings
        properties = client.search(
            query='(Status=Active)',
            limit=100,
            select='ListingKey,ListPrice,BedroomsTotal,BathroomsTotalInteger'
        )

        print(f"Found {len(properties)} properties")
        for prop in properties[:5]:
            print(f"  {prop.get('ListingKey')}: ${prop.get('ListPrice')}")

        # Get photos for first listing
        if properties:
            listing_key = properties[0].get('ListingKey')
            photos = client.get_object(listing_id=listing_key)
            print(f"Retrieved {len(photos)} photos")

    finally:
        # Logout
        client.logout()

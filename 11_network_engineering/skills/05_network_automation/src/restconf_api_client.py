#!/usr/bin/env python3
"""RESTCONF API client for network device management"""

import requests
import json
from requests.auth import HTTPBasicAuth
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RESTCONFClient:
    def __init__(self, host, username, password, port=443):
        self.base_url = f"https://{host}:{port}/restconf"
        self.auth = HTTPBasicAuth(username, password)
        self.headers = {
            'Content-Type': 'application/yang-data+json',
            'Accept': 'application/yang-data+json'
        }
    
    def get_interfaces(self):
        """Get all interfaces"""
        response = requests.get(
            f"{self.base_url}/data/ietf-interfaces:interfaces",
            auth=self.auth,
            headers=self.headers,
            verify=False
        )
        return response.json() if response.status_code == 200 else None
    
    def get_interface(self, name):
        """Get specific interface"""
        response = requests.get(
            f"{self.base_url}/data/ietf-interfaces:interfaces/interface={name}",
            auth=self.auth,
            headers=self.headers,
            verify=False
        )
        return response.json() if response.status_code == 200 else None
    
    def update_interface(self, name, config):
        """Update interface configuration"""
        data = {
            'ietf-interfaces:interface': {
                'name': name,
                **config
            }
        }
        
        response = requests.put(
            f"{self.base_url}/data/ietf-interfaces:interfaces/interface={name}",
            json=data,
            auth=self.auth,
            headers=self.headers,
            verify=False
        )
        
        return response.status_code == 204

if __name__ == '__main__':
    client = RESTCONFClient('192.168.1.1', 'admin', 'password')
    
    # Get interfaces
    interfaces = client.get_interfaces()
    if interfaces:
        print(json.dumps(interfaces, indent=2))

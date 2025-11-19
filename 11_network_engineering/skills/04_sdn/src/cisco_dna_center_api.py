#!/usr/bin/env python3
"""
Cisco DNA Center API Integration
Network policy and device management
"""

import requests
import json
import time

class DNACenter:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.token = None
        self.base_url = f"https://{host}/dna/intent/api/v1"

    def authenticate(self):
        """Get authentication token"""
        url = f"https://{self.host}/dna/system/api/v1/auth/token"
        response = requests.post(
            url,
            auth=(self.username, self.password),
            verify=False
        )
        if response.status_code == 200:
            self.token = response.json()['Token']
            return True
        return False

    def get_devices(self):
        """Get all network devices"""
        headers = {'X-Auth-Token': self.token}
        url = f"{self.base_url}/network-device"
        response = requests.get(url, headers=headers, verify=False)
        return response.json()['response']

    def get_device_health(self, device_id):
        """Get device health status"""
        headers = {'X-Auth-Token': self.token}
        url = f"{self.base_url}/device-health?deviceId={device_id}"
        response = requests.get(url, headers=headers, verify=False)
        return response.json()

    def create_policy(self, policy_name, rules):
        """Create network policy"""
        headers = {
            'X-Auth-Token': self.token,
            'Content-Type': 'application/json'
        }
        policy_payload = {
            "name": policy_name,
            "description": f"Policy {policy_name}",
            "rules": rules
        }
        url = f"{self.base_url}/policy"
        response = requests.post(
            url,
            json=policy_payload,
            headers=headers,
            verify=False
        )
        return response.json()

if __name__ == "__main__":
    dna = DNACenter("10.0.0.20", "admin", "password")

    if dna.authenticate():
        print("✓ DNA Center authenticated")

        # Get devices
        devices = dna.get_devices()
        print(f"✓ Found {len(devices)} devices")

        # Check health
        for device in devices[:3]:
            health = dna.get_device_health(device['id'])
            print(f"  {device['hostname']}: {health['healthScore']}%")

        # Create policy
        rules = [
            {
                "name": "Allow-Web",
                "protocol": "tcp",
                "port": 443,
                "action": "allow"
            }
        ]
        policy = dna.create_policy("production-policy", rules)
        print(f"✓ Policy created: {policy}")

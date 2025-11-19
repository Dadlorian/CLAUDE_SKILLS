#!/usr/bin/env python3
"""
Cisco ACI Fabric Initialization Script
Initialize APIC and fabric nodes
"""

import requests
import json
import sys
from requests.auth import HTTPBasicAuth

class ACIFabricInit:
    def __init__(self, apic_ip, username, password):
        self.base_url = f"https://{apic_ip}/api"
        self.auth = HTTPBasicAuth(username, password)
        self.session = requests.Session()
        self.session.verify = False

    def login(self):
        """Authenticate to APIC"""
        login_url = f"{self.base_url}/aaaLogin.json"
        login_data = {
            "aaaUser": {
                "attributes": {
                    "name": self.auth.username,
                    "pwd": self.auth.password
                }
            }
        }
        response = self.session.post(login_url, json=login_data, verify=False)
        return response.status_code == 200

    def register_fabric_node(self, node_id, serial_num, role):
        """Register a fabric node"""
        node_url = f"{self.base_url}/node/mo/uni/fabric/nodecont.json"
        node_data = {
            "fabricNodeContainer": {
                "children": [{
                    "fabricNode": {
                        "attributes": {
                            "serial": serial_num,
                            "id": str(node_id),
                            "role": role
                        }
                    }
                }]
            }
        }
        response = self.session.post(node_url, json=node_data, auth=self.auth)
        return response.status_code == 200

    def add_switch_credentials(self, node_id, username, password):
        """Add credentials for fabric node"""
        cred_url = f"{self.base_url}/node/mo/uni/fabric/nodecont/node-{node_id}.json"
        cred_data = {
            "fabricNode": {
                "attributes": {
                    "id": str(node_id),
                    "username": username,
                    "password": password
                }
            }
        }
        response = self.session.post(cred_url, json=cred_data, auth=self.auth)
        return response.status_code == 200

if __name__ == "__main__":
    apic_ip = "10.0.0.10"
    username = "admin"
    password = "apicpassword"

    init = ACIFabricInit(apic_ip, username, password)

    if init.login():
        print("✓ APIC login successful")

        # Register spine nodes
        init.register_fabric_node(101, "SPINE-001-SN", "spine")
        init.register_fabric_node(102, "SPINE-002-SN", "spine")

        # Register leaf nodes
        for i in range(1, 5):
            init.register_fabric_node(200+i, f"LEAF-{i:03d}-SN", "leaf")

        print("✓ Fabric nodes registered")
    else:
        print("✗ APIC login failed")
        sys.exit(1)

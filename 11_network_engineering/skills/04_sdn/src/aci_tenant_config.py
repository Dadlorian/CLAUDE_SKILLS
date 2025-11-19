#!/usr/bin/env python3
"""
Cisco ACI Tenant Configuration
Create tenant, application profile, and policies
"""

import json
import requests
from requests.auth import HTTPBasicAuth

class ACITenant:
    def __init__(self, apic_url, username, password):
        self.url = apic_url
        self.auth = HTTPBasicAuth(username, password)
        self.session = requests.Session()

    def create_tenant(self, tenant_name):
        """Create ACI tenant"""
        tenant_config = {
            "fvTenant": {
                "attributes": {"name": tenant_name},
                "children": []
            }
        }
        response = self.session.post(
            f"{self.url}/api/node/mo/uni/tn-{tenant_name}.json",
            json=tenant_config, auth=self.auth
        )
        return response.status_code == 200

    def create_vrf(self, tenant_name, vrf_name):
        """Create VRF within tenant"""
        vrf_config = {
            "fvCtx": {
                "attributes": {"name": vrf_name},
                "children": []
            }
        }
        response = self.session.post(
            f"{self.url}/api/node/mo/uni/tn-{tenant_name}/ctx-{vrf_name}.json",
            json=vrf_config, auth=self.auth
        )
        return response.status_code == 200

    def create_epg(self, tenant_name, app_profile, epg_name, bd_name):
        """Create EPG"""
        epg_config = {
            "fvAEPg": {
                "attributes": {"name": epg_name},
                "children": [{
                    "fvRsBd": {
                        "attributes": {"tnFvBDName": bd_name}
                    }
                }]
            }
        }
        response = self.session.post(
            f"{self.url}/api/node/mo/uni/tn-{tenant_name}/ap-{app_profile}/epg-{epg_name}.json",
            json=epg_config, auth=self.auth
        )
        return response.status_code == 200

    def create_contract(self, tenant_name, contract_name, rules):
        """Create contract with rules"""
        contract_config = {
            "vzBrCP": {
                "attributes": {"name": contract_name},
                "children": rules
            }
        }
        response = self.session.post(
            f"{self.url}/api/node/mo/uni/tn-{tenant_name}/brc-{contract_name}.json",
            json=contract_config, auth=self.auth
        )
        return response.status_code == 200

if __name__ == "__main__":
    aci = ACITenant("https://10.0.0.10", "admin", "password")
    
    # Create tenant structure
    aci.create_tenant("Production-Apps")
    aci.create_vrf("Production-Apps", "production-vrf")
    
    # Create application profile and EPGs
    aci.create_epg("Production-Apps", "web-app", "web-tier", "prod-bd")
    aci.create_epg("Production-Apps", "web-app", "app-tier", "prod-bd")
    aci.create_epg("Production-Apps", "web-app", "db-tier", "prod-bd")
    
    print("✓ ACI Tenant configured")

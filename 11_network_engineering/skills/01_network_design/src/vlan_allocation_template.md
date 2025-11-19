# VLAN Allocation Template

## Campus Network VLAN Plan
**Site:** Building A, HQ Campus
**Date:** November 2025
**Version:** 1.0
**Owner:** Network Architecture Team

---

## User Access VLANs

### VLAN 10 - Executive
- **Subnet:** 10.0.10.0/24
- **Gateway:** 10.0.10.1
- **Usable IPs:** 1-254 (254 hosts)
- **Current Users:** 45
- **Description:** Executive staff and board members
- **Access Location:** HQ Building A, All Floors
- **Default Gateway Redundancy:**
  - Primary: Distribution-A (10.0.10.2, Priority 150)
  - Backup: Distribution-B (10.0.10.3, Priority 100)
- **QoS:** High priority
- **Security:** Standard enterprise firewall rules
- **DHCP Scope:** 10.0.10.100-200
- **Notes:** Growth expected +10% annually

### VLAN 20 - Finance
- **Subnet:** 10.0.20.0/24
- **Gateway:** 10.0.20.1
- **Usable IPs:** 1-254
- **Current Users:** 95
- **Description:** Finance and Accounting department
- **Access Location:** HQ Building A, Floors 2-3
- **Redundancy:**
  - Primary: Distribution-A (Priority 150)
  - Backup: Distribution-B (Priority 100)
- **Compliance:** SOX, PCI-DSS (financial transactions)
- **Access Control:**
  - Can access: Finance servers, printers, internet
  - Cannot access: Engineering, Executive VLANs
- **DHCP Scope:** 10.0.20.100-200
- **Growth:** +20% annually (expansion planned)

### VLAN 30 - Engineering
- **Subnet:** 10.0.30.0/24
- **Gateway:** 10.0.30.1
- **Usable IPs:** 1-254
- **Current Users:** 120
- **Description:** Software and Hardware Engineering
- **Access Location:** Building A + Building B
- **Redundancy:**
  - Primary: Distribution-B (Priority 150)
  - Backup: Distribution-A (Priority 100)
- **Special Requirements:**
  - Access to code repositories (GitHub)
  - Access to development servers
  - Access to CAD workstations
- **DHCP Scope:** 10.0.30.100-200
- **Growth:** +15% annually

### VLAN 40 - Operations
- **Subnet:** 10.0.40.0/24
- **Gateway:** 10.0.40.1
- **Usable IPs:** 1-254
- **Current Users:** 60
- **Description:** IT Operations and Infrastructure team
- **Access Location:** All Buildings
- **Redundancy:**
  - Primary: Distribution-A (Priority 150)
  - Backup: Distribution-B (Priority 100)
- **Special Access:**
  - Administrative access to network devices
  - Access to monitoring systems
  - Access to ticketing system
- **DHCP Scope:** 10.0.40.100-200

### VLAN 50 - Sales
- **Subnet:** 10.0.50.0/24
- **Gateway:** 10.0.50.1
- **Usable IPs:** 1-254
- **Current Users:** 75
- **Description:** Sales and Customer Success
- **Access Location:** Building C, All Floors
- **Redundancy:**
  - Primary: Distribution-B (Priority 150)
  - Backup: Distribution-A (Priority 100)
- **Special Requirements:**
  - Access to CRM (Salesforce)
  - Access to customer database
  - VPN for remote access
- **DHCP Scope:** 10.0.50.100-200

---

## Service VLANs

### VLAN 100 - Guest WiFi
- **Subnet:** 10.0.100.0/24
- **Gateway:** 10.0.100.1
- **Usable IPs:** 1-254
- **Description:** Visitor and contractor access
- **Isolation:** Complete (no internal access)
- **Internet:** Direct to Firewall
- **Portal:** Captive portal with terms of service
- **Bandwidth Limit:** 25 Mbps per user
- **DHCP Scope:** 10.0.100.50-200
- **Session Timeout:** 8 hours

### VLAN 110 - Voice/VoIP
- **Subnet:** 10.0.110.0/24
- **Gateway:** 10.0.110.1
- **Usable IPs:** 1-254
- **Description:** IP Phones and VoIP infrastructure
- **QoS Priority:** High (CoS 5)
- **Reserved Bandwidth:** 30 Mbps
- **DHCP Scope:** 10.0.110.100-200
- **Phone Assignment:** Automatic via DHCP option 150
- **Call Control:** Internal PBX (ShoreTel/Avaya)

### VLAN 120 - Printers
- **Subnet:** 10.0.120.0/24
- **Gateway:** 10.0.120.1
- **Usable IPs:** 1-254
- **Description:** Network printers accessible from all VLANs
- **Access:** All user VLANs (routed via distribution)
- **Static IPs:** 10.0.120.10-50 (popular printers)
- **DHCP Scope:** 10.0.120.100-200 (less common printers)
- **Print Server:** 10.0.120.5
- **Management:** Automatic discovery and configuration

---

## Infrastructure VLANs

### VLAN 200 - Management
- **Subnet:** 10.0.200.0/24
- **Gateway:** 10.0.200.1
- **Usable IPs:** 1-254
- **Description:** Network management and monitoring
- **Access Control:** Restricted to network team (SSH/HTTPS only)
- **Devices:**
  - Switch management IPs: 10.0.200.10-50
  - Router management IPs: 10.0.200.51-100
  - Server IPMI: 10.0.200.101-200
- **Monitoring:**
  - NMS server: 10.0.200.10
  - Syslog server: 10.0.200.11
  - TACACS+ server: 10.0.200.12

### VLAN 210 - Storage
- **Subnet:** 10.0.210.0/24
- **Gateway:** 10.0.210.1
- **Usable IPs:** 1-254
- **Description:** Storage network (iSCSI, NFS)
- **Performance:** Jumbo frames (MTU 9000)
- **Devices:**
  - Storage array: 10.0.210.10-20
  - Storage servers: 10.0.210.30-50
- **Access:** Restricted to authorized servers

---

## Summary Table

| VLAN | Name | Subnet | Hosts | Current Use | Gateway | Priority |
|------|------|--------|-------|------------|---------|----------|
| 10 | Executive | 10.0.10.0/24 | 254 | 45 (18%) | 10.0.10.1 | High |
| 20 | Finance | 10.0.20.0/24 | 254 | 95 (37%) | 10.0.20.1 | High |
| 30 | Engineering | 10.0.30.0/24 | 254 | 120 (47%) | 10.0.30.1 | Medium |
| 40 | Operations | 10.0.40.0/24 | 254 | 60 (24%) | 10.0.40.1 | Medium |
| 50 | Sales | 10.0.50.0/24 | 254 | 75 (30%) | 10.0.50.1 | Medium |
| 100 | Guest | 10.0.100.0/24 | 254 | 20 (8%) | 10.0.100.1 | Low |
| 110 | Voice | 10.0.110.0/24 | 254 | 85 (33%) | 10.0.110.1 | High |
| 120 | Printers | 10.0.120.0/24 | 254 | 25 (10%) | 10.0.120.1 | Medium |
| 200 | Management | 10.0.200.0/24 | 254 | 50 (20%) | 10.0.200.1 | High |
| 210 | Storage | 10.0.210.0/24 | 254 | 30 (12%) | 10.0.210.1 | High |

---

## Reserved Address Ranges

| Range | Purpose | Status |
|-------|---------|--------|
| 10.0.0.0 - 10.0.9.255 | Reserved for future VLANs | Reserved |
| 10.0.230.0 - 10.0.254.255 | Reserved for future expansion | Reserved |
| 10.255.0.0/16 | Device loopbacks | Reserved |

---

## Approval and Sign-off

- **Prepared By:** Network Architecture Team
- **Date:** November 2025
- **Approved By:** IT Director
- **Effective Date:** November 25, 2025

---

**Document Version:** 1.0
**Last Updated:** November 2025
**Next Review:** February 2026

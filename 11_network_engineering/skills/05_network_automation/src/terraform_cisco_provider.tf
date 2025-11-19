# Cisco IOS-XE Terraform Configuration
# Manages network devices directly via NETCONF

terraform {
  required_providers {
    iosxe = {
      source  = "CiscoDevNet/iosxe"
      version = "~> 0.4.0"
    }
  }
}

provider "iosxe" {
  username = var.device_username
  password = var.device_password
  url      = "https://${var.device_ip}:443"
  insecure = true  # In production, use proper certificates
}

# Configure hostname
resource "iosxe_system" "example" {
  device                   = iosxe_device_netconf.device.device
  hostname                 = var.hostname
  domain_name              = var.domain_name
  ipv4_default_gateway_ip  = var.default_gateway
}

# Configure management interface
resource "iosxe_interface_ethernet" "mgmt" {
  device              = iosxe_device_netconf.device.device
  name                = "GigabitEthernet0/0/0"
  description         = "Management Interface"
  enabled             = true
  mtu                 = 1500
  ip_address          = var.mgmt_ip
  ip_mask             = var.mgmt_netmask
}

# Configure WAN interface
resource "iosxe_interface_ethernet" "wan" {
  device              = iosxe_device_netconf.device.device
  name                = "GigabitEthernet0/0/1"
  description         = "WAN Interface"
  enabled             = true
  mtu                 = 1500
  ip_address          = var.wan_ip
  ip_mask             = var.wan_netmask
}

# Configure BGP
resource "iosxe_bgp" "example" {
  device        = iosxe_device_netconf.device.device
  asn           = var.bgp_asn
  router_id     = var.router_id
  bgp_log       = true
  graceful_restart = true

  neighbors = [
    for neighbor in var.bgp_neighbors : {
      address      = neighbor.ip
      remote_asn   = neighbor.remote_asn
      description  = neighbor.description
    }
  ]

  address_family_ipv4 = [
    for network in var.bgp_networks : {
      network       = network.prefix
      mask          = network.mask
      next_hop_self = true
    }
  ]
}

# Configure OSPF
resource "iosxe_ospf" "example" {
  device          = iosxe_device_netconf.device.device
  process_id      = var.ospf_process_id
  router_id       = var.router_id
  log_changes     = true
  administrative_distance = 110

  networks = [
    for network in var.ospf_networks : {
      network = network.address
      area    = network.area
      mask    = network.mask
    }
  ]
}

# Configure NTP
resource "iosxe_ntp_server" "example" {
  for_each = toset(var.ntp_servers)

  device = iosxe_device_netconf.device.device
  ip     = each.value
}

# Configure SNMP
resource "iosxe_snmp" "example" {
  device    = iosxe_device_netconf.device.device
  contact   = var.snmp_contact
  location  = var.snmp_location
  community = var.snmp_community
}

# Configure logging
resource "iosxe_logging" "example" {
  device            = iosxe_device_netconf.device.device
  console_severity  = "informational"
  logging_severity  = "debugging"
  logging_buffered  = 4096

  logging_servers = [
    for server in var.syslog_servers : {
      address  = server
      severity = "informational"
    }
  ]
}

# Device connection
resource "iosxe_device_netconf" "device" {
  device   = var.device_ip
  user     = var.device_username
  pass     = var.device_password
  port     = 830
  insecure = true
}

# Outputs
output "device_id" {
  value       = iosxe_device_netconf.device.device
  description = "Device ID"
}

output "hostname" {
  value       = iosxe_system.example.hostname
  description = "Device hostname"
}

output "mgmt_interface" {
  value = {
    name      = iosxe_interface_ethernet.mgmt.name
    ip        = iosxe_interface_ethernet.mgmt.ip_address
    netmask   = iosxe_interface_ethernet.mgmt.ip_mask
  }
  description = "Management interface configuration"
}

output "wan_interface" {
  value = {
    name      = iosxe_interface_ethernet.wan.name
    ip        = iosxe_interface_ethernet.wan.ip_address
    netmask   = iosxe_interface_ethernet.wan.ip_mask
  }
  description = "WAN interface configuration"
}

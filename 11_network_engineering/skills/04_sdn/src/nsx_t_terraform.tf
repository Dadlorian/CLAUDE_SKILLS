# VMware NSX-T Infrastructure as Code (Terraform)

terraform {
  required_providers {
    nsxt = {
      source  = "vmware/nsxt"
      version = "~> 3.0"
    }
  }
}

provider "nsxt" {
  host                 = var.nsx_manager
  username             = var.nsx_username
  password             = var.nsx_password
  allow_unverified_ssl = true
}

# Transport Zone
resource "nsxt_policy_transport_zone" "tz_overlay" {
  display_name      = "tz-overlay"
  transport_type    = "OVERLAY"
  description       = "Overlay transport zone for VXLAN"
}

# Logical Switch (Segment)
resource "nsxt_policy_segment" "tenant_a_segment" {
  display_name           = "Tenant-A-Network"
  description            = "Production network for Tenant A"
  transport_zone_path    = nsxt_policy_transport_zone.tz_overlay.path
  connectivity           = "ON"
  
  subnet {
    cidr = "10.100.0.0/24"
    gateway = "10.100.0.1"
  }
}

# Tier-1 Logical Router
resource "nsxt_policy_tier1_gateway" "tier1_a" {
  display_name           = "Tier-1-Tenant-A"
  description            = "Tenant A router"
  nsx_id                 = "tier1-a"
  tier0_path             = nsxt_policy_tier0_gateway.tier0.path
  failover_mode          = "PREEMPTIVE"
  enable_firewall        = true
  ipv6_profile_path      = ""
  default_rule_logging   = true
}

# Segment Port (VM interface)
resource "nsxt_policy_segment_port" "vm_interface" {
  segment_path = nsxt_policy_segment.tenant_a_segment.path
  display_name = "vm-interface-001"
}

# Security Policy
resource "nsxt_policy_security_policy" "production" {
  display_name = "Production-Policy"
  description  = "Zero-trust security policy"
  category     = "Application"
  locked       = false
  stateful     = true

  rule {
    display_name       = "Allow-Web-to-App"
    destination_groups = [nsxt_policy_group.app_tier.path]
    source_groups      = [nsxt_policy_group.web_tier.path]
    services           = [nsxt_policy_service.tcp_8080.path]
    action             = "ALLOW"
    logged             = true
  }

  rule {
    display_name = "Deny-All"
    action       = "REJECT"
    logged       = true
  }
}

# Group (Security Group)
resource "nsxt_policy_group" "web_tier" {
  display_name = "Web-Tier"
  nsx_id       = "web-tier"
  description  = "Web tier VMs"

  criteria {
    condition {
      member_type   = "VirtualMachine"
      operator      = "EQUALS"
      value         = "tag:tier:web"
    }
  }
}

resource "nsxt_policy_group" "app_tier" {
  display_name = "App-Tier"
  nsx_id       = "app-tier"
  description  = "Application tier VMs"

  criteria {
    condition {
      member_type   = "VirtualMachine"
      operator      = "EQUALS"
      value         = "tag:tier:app"
    }
  }
}

# L4 Service
resource "nsxt_policy_service" "tcp_8080" {
  display_name = "TCP-8080"

  l4_port_set_service {
    transport = "TCP"
    port_set  = ["8080"]
  }
}

output "segment_path" {
  value = nsxt_policy_segment.tenant_a_segment.path
}

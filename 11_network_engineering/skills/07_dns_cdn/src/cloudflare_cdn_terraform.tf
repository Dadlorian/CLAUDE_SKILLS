# Cloudflare CDN Configuration with Terraform
# File: main.tf
# Sets up complete Cloudflare CDN with caching, WAF, and optimization

terraform {
  required_version = ">= 1.0"
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# Variables
variable "cloudflare_api_token" {
  type      = string
  sensitive = true
  description = "Cloudflare API Token"
}

variable "domain" {
  type        = string
  default     = "example.com"
  description = "Domain name"
}

variable "account_id" {
  type        = string
  description = "Cloudflare Account ID"
}

# Add domain to Cloudflare
resource "cloudflare_zone" "example" {
  account_id = var.account_id
  zone       = var.domain
}

# Set nameservers at registrar to Cloudflare
# Output: Cloudflare nameservers
output "cloudflare_nameservers" {
  value       = cloudflare_zone.example.name_servers
  description = "Cloudflare nameservers (update at registrar)"
}

# DNS Records
resource "cloudflare_record" "root" {
  zone_id = cloudflare_zone.example.id
  name    = "@"
  type    = "A"
  value   = "192.0.2.10"  # Origin server IP
  ttl     = 300
  proxied = true  # Enable CDN
}

resource "cloudflare_record" "www" {
  zone_id = cloudflare_zone.example.id
  name    = "www"
  type    = "CNAME"
  value   = var.domain
  ttl     = 300
  proxied = true  # Enable CDN
}

resource "cloudflare_record" "api" {
  zone_id = cloudflare_zone.example.id
  name    = "api"
  type    = "CNAME"
  value   = var.domain
  ttl     = 300
  proxied = true  # Enable CDN
}

resource "cloudflare_record" "cdn" {
  zone_id = cloudflare_zone.example.id
  name    = "cdn"
  type    = "CNAME"
  value   = var.domain
  ttl     = 300
  proxied = true  # Enable CDN
}

# SSL/TLS Configuration
resource "cloudflare_zone_settings_override" "example" {
  zone_id = cloudflare_zone.example.id

  settings {
    # SSL/TLS mode
    ssl = "full"  # Full (strict)

    # Always use HTTPS
    always_use_https = "on"

    # HSTS
    header_hsts {
      enabled            = true
      include_subdomains = true
      max_age            = 31536000  # 1 year
      preload            = true
    }

    # Automatic HTTPS rewrites
    automatic_https_rewrites = "on"

    # Minimum TLS version
    min_tls_version = "1.2"

    # Opportunistic Encryption
    opportunistic_encryption = "on"

    # Security
    security_level      = "medium"
    challenge_ttl       = "1800"
    browser_integrity_check = "on"
  }
}

# Caching Configuration
resource "cloudflare_cache_rules" "example" {
  zone_id = cloudflare_zone.example.id

  # Cache everything (for static sites)
  rules {
    description = "Cache everything"
    if           = "true"
    then = {
      cache             = true
      cache_ttl         = 3600
      cache_on_cookie   = ""
    }
  }

  # Cache static assets longer
  rules {
    description = "Cache static assets 1 year"
    if           = "http.request.uri.path contains \"/static/\""
    then = {
      cache     = true
      cache_ttl = 31536000  # 1 year
    }
  }

  # Cache images longer
  rules {
    description = "Cache images 1 month"
    if           = "http.request.uri.path matches \".*\\.(jpg|jpeg|png|gif|webp|svg)$\""
    then = {
      cache     = true
      cache_ttl = 2592000  # 30 days
    }
  }

  # Bypass cache for API
  rules {
    description = "Don't cache API"
    if           = "http.request.uri.path starts_with \"/api/\""
    then = {
      cache = false
    }
  }

  # Short TTL for HTML
  rules {
    description = "Cache HTML 1 hour"
    if           = "http.request.uri.path matches \".*\\.html$\""
    then = {
      cache     = true
      cache_ttl = 3600
    }
  }
}

# Page Rules for advanced caching
resource "cloudflare_page_rule" "cache_control" {
  zone_id = cloudflare_zone.example.id
  target  = "example.com/static/*"

  actions {
    cache_level = "cache_everything"
    browser_cache_ttl = 43200  # 12 hours
  }
}

# Origin Shield (caching layer between CDN and origin)
resource "cloudflare_zone_cache_variants" "example" {
  zone_id = cloudflare_zone.example.id

  avif {
    always_false = false
  }

  brotli {
    always_false = false
  }

  webp {
    always_false = false
  }
}

# WAF (Web Application Firewall) Rules
resource "cloudflare_waf_rule" "example" {
  zone_id  = cloudflare_zone.example.id
  rule_id  = "100000"
  group_id = "de677dc8-446d-47fd-bc8f-97c468e201f3"
  mode     = "challenge"
}

# Firewall Rules - Bot Management
resource "cloudflare_firewall_rule" "block_bots" {
  zone_id     = cloudflare_zone.example.id
  description = "Block known bots"
  filter_id   = cloudflare_filter.bot_management.id
  action      = "challenge"
  priority    = 1
}

resource "cloudflare_filter" "bot_management" {
  zone_id     = cloudflare_zone.example.id
  description = "Known bots"
  expression  = "(cf.bot_management.score < 30)"
}

# Firewall Rules - Rate Limiting
resource "cloudflare_firewall_rule" "rate_limit" {
  zone_id     = cloudflare_zone.example.id
  description = "Rate limit API endpoints"
  filter_id   = cloudflare_filter.api_rate_limit.id
  action      = "block"
  priority    = 2
}

resource "cloudflare_filter" "api_rate_limit" {
  zone_id     = cloudflare_zone.example.id
  description = "High API requests from single IP"
  expression  = "(http.request.uri.path contains \"/api/\" and cf.threat_score > 50)"
}

# DDoS Protection Configuration
resource "cloudflare_zone_settings_override" "ddos" {
  zone_id = cloudflare_zone.example.id

  settings {
    # DDoS Protection Level
    dos_protection_level = "high"

    # Rate limiting
    rate_limiting        = 10
  }
}

# Compression and Optimization
resource "cloudflare_zone_settings_override" "optimization" {
  zone_id = cloudflare_zone.example.id

  settings {
    # Brotli compression
    brotli = "on"

    # Automatic minification
    minify {
      css  = "on"
      html = "on"
      js   = "on"
    }

    # Polish (image optimization)
    polish = "lossless"

    # Rocket Loader (JavaScript optimization)
    rocket_loader = "on"

    # Automatic Platform Optimization
    automatic_platform_optimization {
      enabled = true
      cache_on_cookie = "wordpress_test"
    }
  }
}

# Page Rules for optimization
resource "cloudflare_page_rule" "bypass_cache" {
  zone_id = cloudflare_zone.example.id
  target  = "example.com/admin/*"

  actions {
    cache_level = "bypass"
    security_level = "high"
  }
}

# Workers Route (for edge computing)
resource "cloudflare_workers_route" "example" {
  zone_id     = cloudflare_zone.example.id
  pattern     = "example.com/image/*"
  script_name = "image-optimization"
}

# Outputs
output "zone_id" {
  value       = cloudflare_zone.example.id
  description = "Cloudflare Zone ID"
}

output "status" {
  value       = cloudflare_zone.example.status
  description = "Zone status"
}

output "cdns" {
  value       = cloudflare_zone.example.nameservers
  description = "Cloudflare CDN nameservers"
}

#!/bin/bash
# DNSSEC Zone Signing Automation Script
# Purpose: Automate DNSSEC signing, key rotation, and zone updates
# Usage: ./dnssec_signing_script.sh example.com

set -e  # Exit on error

# Configuration
ZONE="${1:?Zone name required (e.g., example.com)}"
BIND_DIR="/etc/bind"
ZONE_DIR="${BIND_DIR}/zones"
KEY_DIR="${BIND_DIR}/keys"
LOG_FILE="/var/log/dnssec-signing.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
  echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
  echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
  exit 1
}

warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Step 1: Check prerequisites
log "Checking prerequisites for zone: $ZONE"

if [ ! -d "$KEY_DIR" ]; then
  error "Key directory not found: $KEY_DIR"
fi

if [ ! -f "$ZONE_DIR/db.$ZONE" ]; then
  error "Zone file not found: $ZONE_DIR/db.$ZONE"
fi

# Step 2: Generate keys if they don't exist
log "Checking DNSSEC keys..."

KSK_FILE=$(ls -1 "$KEY_DIR"/K${ZONE}.*.key 2>/dev/null | head -1)
ZSK_FILE=$(ls -1 "$KEY_DIR"/K${ZONE}.*.key 2>/dev/null | tail -1)

if [ -z "$KSK_FILE" ]; then
  log "Generating KSK (Key Signing Key) for $ZONE..."
  cd "$KEY_DIR"
  dnssec-keygen -a ECDSAP256SHA256 -f KSK "$ZONE"
  log "KSK generated successfully"
fi

if [ -z "$ZSK_FILE" ]; then
  log "Generating ZSK (Zone Signing Key) for $ZONE..."
  cd "$KEY_DIR"
  dnssec-keygen -a ECDSAP256SHA256 "$ZONE"
  log "ZSK generated successfully"
fi

# Step 3: Include keys in zone file
log "Including DNSSEC keys in zone file..."

cd "$ZONE_DIR"

# Backup original zone file
cp "db.$ZONE" "db.$ZONE.bak.$(date +%s)"

# Remove existing key includes
sed -i '/$INCLUDE.*\.key/d' "db.$ZONE"

# Find latest keys
KSK_KEY=$(ls -1t "$KEY_DIR"/K${ZONE}.*.key 2>/dev/null | grep -v '\.private' | xargs grep -l '257' | head -1)
ZSK_KEY=$(ls -1t "$KEY_DIR"/K${ZONE}.*.key 2>/dev/null | grep -v '\.private' | xargs grep -l '256' | head -1)

if [ -z "$KSK_KEY" ] || [ -z "$ZSK_KEY" ]; then
  error "Could not find KSK or ZSK key files"
fi

# Add key includes after SOA record
sed -i "/^@.*SOA/a \\\n\$INCLUDE $(basename "$KSK_KEY")\n\$INCLUDE $(basename "$ZSK_KEY")" "db.$ZONE"

log "Keys included in zone file"

# Step 4: Check zone file syntax
log "Validating zone file syntax..."

if ! named-checkzone -D "$ZONE" "db.$ZONE" > /dev/null; then
  error "Zone file validation failed. Check syntax in db.$ZONE"
fi

log "Zone file syntax valid"

# Step 5: Sign the zone
log "Signing zone $ZONE with DNSSEC..."

dnssec-signzone -o "$ZONE" -k "$KSK_KEY" "db.$ZONE" "$ZSK_KEY" > /dev/null 2>&1

if [ $? -eq 0 ]; then
  log "Zone signed successfully. Created db.$ZONE.signed"
else
  error "Zone signing failed"
fi

# Step 6: Extract DS record
log "Extracting DS record for registrar..."

if [ -f "dsset-$ZONE." ]; then
  log "DS Record (submit to registrar):"
  cat "dsset-$ZONE." | tee -a "$LOG_FILE"
else
  warning "DS record file not found (dsset-$ZONE.)"
fi

# Step 7: Extract DNSKEY records
log "Extracting DNSKEY records for verification..."

dnssec-dsfromkey "$KSK_KEY" | tee -a "$LOG_FILE"

# Step 8: Update BIND configuration
log "Updating BIND configuration..."

# Check if zone uses .signed file
if ! grep -q "file.*db\.$ZONE\.signed" "$BIND_DIR/named.conf.local" 2>/dev/null; then
  warning "Update named.conf.local to use db.$ZONE.signed instead of db.$ZONE"
  warning "Add: file \"/etc/bind/zones/db.$ZONE.signed\";"
fi

# Step 9: Reload BIND
log "Reloading BIND..."

if sudo rndc reload "$ZONE" > /dev/null 2>&1; then
  log "BIND reloaded successfully"
else
  warning "BIND reload may have failed. Check logs"
fi

# Step 10: Verify DNSSEC
log "Verifying DNSSEC configuration..."

# Query DNSKEY records
DNSKEY_COUNT=$(dig "@localhost" "$ZONE" DNSKEY +short 2>/dev/null | wc -l)

if [ "$DNSKEY_COUNT" -gt 0 ]; then
  log "DNSSEC verification successful. Found $DNSKEY_COUNT DNSKEY records"
else
  warning "Could not verify DNSKEY records. Zone may not be signed properly"
fi

# Step 11: Check signature validity
log "Checking DNSSEC signature validity..."

# Get signature expiration
RRSIG=$(dig "@localhost" "$ZONE" A +dnssec +short 2>/dev/null | grep "^RRSIG")

if [ -n "$RRSIG" ]; then
  log "DNSSEC signatures found:"
  log "$RRSIG"
else
  warning "No RRSIG records found. Zone may not be signed"
fi

# Step 12: Summary
log "===== DNSSEC Signing Summary ====="
log "Zone: $ZONE"
log "KSK: $(basename "$KSK_KEY")"
log "ZSK: $(basename "$ZSK_KEY")"
log "Zone file: $ZONE_DIR/db.$ZONE.signed"
log "DS record file: $ZONE_DIR/dsset-$ZONE."
log ""
log "Next steps:"
log "1. Submit DS record to registrar"
log "2. Wait 24-48 hours for propagation"
log "3. Verify DNSSEC chain with online validator:"
log "   https://dnssec-analyzer.verisignlabs.com/"
log "4. Monitor signature expiration (should be re-signed automatically)"

log "DNSSEC signing process complete"

# Step 13: Cleanup old keys (optional)
# Uncomment to automatically remove keys older than 90 days
# find "$KEY_DIR" -name "K${ZONE}.*.key" -mtime +90 -delete

exit 0

# DNSSEC Implementation Guide

## Prerequisites

- BIND 9.9+ installed
- Authoritative DNS server configured
- Zone file ready for signing
- Registrar supporting DNSSEC (most modern ones do)

## Step 1: Plan DNSSEC Deployment

### Key Strategy
```
KSK (Key Signing Key):
- 2048-bit RSA or 256-bit ECDSA
- Signed with operator's private key
- Submitted to parent zone

ZSK (Zone Signing Key):
- 2048-bit RSA or 256-bit ECDSA (same as KSK minimum)
- Signs actual DNS records
- Can be rotated independently

Timeline:
1. Generate KSK and ZSK
2. Publish DNSKEY records
3. Create DS records from KSK
4. Sign zone with ZSK
5. Submit DS to parent/registrar
6. Verify chain of trust
```

### Algorithm Selection
```
RSASHA256 (Traditional, well-tested):
- Security: Good
- Performance: Good
- Key size: 2048-bit minimum

ECDSAP256SHA256 (Modern, recommended):
- Security: Excellent
- Performance: Better than RSA
- Key size: 256-bit (smaller signatures)
- Browser support: 95%+ (not old IE)

ED25519 (Best modern practice):
- Security: Excellent
- Performance: Excellent
- Key size: 256-bit
- Browser support: 85%+

Recommendation: Use ECDSAP256SHA256 for new deployments
```

## Step 2: Generate DNSSEC Keys

### Generate KSK (Key Signing Key)
```bash
# Navigate to zone directory
cd /etc/bind/keys

# Generate KSK (ECDSAP256SHA256)
dnssec-keygen -a ECDSAP256SHA256 -f KSK example.com
# Output:
# Kexample.com.+013+12345
# Kexample.com.+013+12345.key
# Kexample.com.+013+12345.private

# Verify KSK
cat Kexample.com.+013+12345.key
# example.com. 3600 IN DNSKEY 257 3 13 AwEAAZ5...

# 257 = KSK flag
# 3 = DNSSEC protocol
# 13 = ECDSAP256SHA256 algorithm
```

### Generate ZSK (Zone Signing Key)
```bash
# Generate ZSK (without -f flag, so not KSK)
dnssec-keygen -a ECDSAP256SHA256 example.com
# Output:
# Kexample.com.+013+67890
# Kexample.com.+013+67890.key
# Kexample.com.+013+67890.private

# Verify ZSK
cat Kexample.com.+013+67890.key
# example.com. 3600 IN DNSKEY 256 3 13 AwEAAa8...

# 256 = ZSK flag
# 3 = DNSSEC protocol
# 13 = ECDSAP256SHA256 algorithm
```

### Backup Private Keys
```bash
# CRITICAL: Secure backup of private keys
tar -czf dnssec-keys-backup.tar.gz Kexample.com.+013+*.private
sudo chown root:root dnssec-keys-backup.tar.gz
sudo chmod 600 dnssec-keys-backup.tar.gz

# Store in secure location (encrypted, offline)
# Encrypt for transport
gpg -c dnssec-keys-backup.tar.gz
```

## Step 3: Include Keys in Zone File

### Update Zone File
```bash
# Edit zone file
nano /etc/bind/zones/db.example.com
```

Add at beginning of zone file:
```
$TTL 3600
$ORIGIN example.com.

; Include DNSSEC keys
$INCLUDE /etc/bind/keys/Kexample.com.+013+12345.key  ; KSK
$INCLUDE /etc/bind/keys/Kexample.com.+013+67890.key  ; ZSK

@    IN    SOA    ns1.example.com. admin.example.com. (
           2024111901
           3600
           1800
           604800
           86400 )
...rest of zone file
```

## Step 4: Sign the Zone

### Sign Zone with dnssec-signzone
```bash
# Sign the zone
dnssec-signzone -o example.com /etc/bind/zones/db.example.com

# Output:
# Signing zone example.com
# Zone signing complete
# Signatures generated: 50
# Seconds to sign: 0.123
#
# Signed zone file: db.example.com.signed
# Key file: dsset-example.com.
```

### Output Files
```
db.example.com.signed:
- Signed zone file with RRSIG records
- Ready to use in BIND

dsset-example.com.:
- DS records derived from KSK
- Submit to registrar for parent zone inclusion

keyset-example.com.:
- DNSKEY records
- For reference
```

### Set Permissions
```bash
sudo chown bind:bind /etc/bind/zones/db.example.com.signed
sudo chmod 644 /etc/bind/zones/db.example.com.signed
```

## Step 5: Configure BIND to Use Signed Zone

### Update named.conf.local
```
zone "example.com" {
    type master;
    file "/etc/bind/zones/db.example.com.signed";  # Use .signed file!
    allow-transfer { 192.0.2.2; 192.0.2.3; };
    notify yes;
    also-notify { 192.0.2.2; 192.0.2.3; };
};
```

### Reload BIND
```bash
# Reload zone
sudo rndc reload example.com

# Verify signed zone loaded
dig @localhost example.com DNSKEY
dig @localhost example.com A +dnssec

# Should show RRSIG records
```

## Step 6: Submit DS Records to Registrar

### Extract DS Record
```bash
# DS record is in dsset-example.com
cat dsset-example.com
# example.com. 3600 IN DS 12345 13 2 a1b2c3d4...

# Or generate with dnssec-dsfromkey
dnssec-dsfromkey /etc/bind/keys/Kexample.com.+013+12345.key
# example.com. IN DS 12345 13 2 a1b2c3d4...
```

### Registrar Submission
```
1. Log into registrar account
2. Find DNSSEC / DS Records section
3. Add DS record:
   - Key Tag: 12345
   - Algorithm: 13 (ECDSAP256SHA256)
   - Digest Type: 2 (SHA256)
   - Digest: a1b2c3d4e5f6g7h8...

4. Save and verify
5. Wait 24-48 hours for propagation
```

## Step 7: Verify DNSSEC Chain

### Check DNSSEC Validation
```bash
# Test from local resolver (with DNSSEC enabled)
dig @8.8.8.8 example.com A +dnssec +multiline

# Should show:
# ad flags = AUTHENTIC DATA
# RRSIGs present

# Status: BOGUS (failed) = problem
# Status: SECURE = working!
```

### DNSSEC Analyzer
```
Online tools:
- https://dnssec-analyzer.verisignlabs.com/
- https://zonemaster.net/
- https://www.dns-oarc.net/tools/

Enter: example.com
Review:
- Chain of trust status (SECURE)
- DS record presence
- DNSKEY validation
- RRSIG validity
```

### Command-Line Validation
```bash
# Full DNSSEC chain validation
dig @ns1.example.com example.com +dnssec +trace

# Detailed output:
# . 518400 IN DNSKEY ...
# com. 172800 IN DS ...
# example.com. 3600 IN DNSKEY ...
# example.com. 3600 IN A ...
# example.com. 3600 IN RRSIG ...

# Check trust anchor (root key)
dig . DNSKEY +short | grep "257"
```

## Step 8: Automate Zone Signing

### Auto-DNSSEC with dnssec-policy (BIND 9.16+)

Configure automatic signing:
```
zone "example.com" {
    type master;
    file "/etc/bind/zones/db.example.com";  # Use unsigned!
    dnssec-policy default;
    auto-dnssec maintain;
    inline-signing yes;
};
```

BIND automatically:
- Generates keys
- Signs zone
- Manages key rotation
- Re-signs on updates

### Manual Automation Script
```bash
#!/bin/bash
# dnssec-auto-resign.sh

ZONEDIR=/etc/bind/zones
ZONE=example.com
NSDIR=/etc/bind/keys

cd $ZONEDIR

# Check if zone needs re-signing
sig_date=$(stat -c%Y db.${ZONE}.signed)
now=$(date +%s)
age=$((now - sig_date))

# Re-sign if > 7 days old
if [ $age -gt 604800 ]; then
    echo "Re-signing zone $ZONE"
    dnssec-signzone -o $ZONE db.$ZONE

    # Reload in BIND
    rndc reload $ZONE

    # Log
    echo "$(date): Re-signed $ZONE" >> /var/log/dnssec-resign.log
fi
```

Schedule with cron:
```bash
# Run daily at 2 AM
crontab -e

# Add:
0 2 * * * /usr/local/bin/dnssec-auto-resign.sh
```

## Step 9: Key Rotation

### ZSK Rotation (Every 30-90 days)
```bash
cd /etc/bind/keys

# Generate new ZSK
dnssec-keygen -a ECDSAP256SHA256 example.com
# Output: Kexample.com.+013+99999

# Update zone file with new key
nano /etc/bind/zones/db.example.com

# Add:
# $INCLUDE /etc/bind/keys/Kexample.com.+013+99999.key

# Sign zone
dnssec-signzone -o example.com /etc/bind/zones/db.example.com

# Reload
rndc reload example.com

# Wait for zone to stabilize
# Then remove old ZSK from zone file
# Re-sign and reload

# Remove old ZSK from zone file
# Remove: $INCLUDE /etc/bind/keys/Kexample.com.+013+67890.key

# Final sign and reload
dnssec-signzone -o example.com /etc/bind/zones/db.example.com
rndc reload example.com
```

### KSK Rotation (Yearly, more complex)
```bash
# Step 1: Generate new KSK
dnssec-keygen -a ECDSAP256SHA256 -f KSK example.com
# Output: Kexample.com.+013+54321

# Step 2: Add new KSK to zone and sign
# Include both old and new KSK temporarily

# Step 3: Submit new DS to registrar
dnssec-dsfromkey /etc/bind/keys/Kexample.com.+013+54321.key
# Wait 24-48 hours for registrar propagation

# Step 4: Verify new DS in parent zone
dig example.com DS @ns1.parent.com

# Step 5: Remove old KSK from zone
# Wait for zone TTL to expire on all caches

# Step 6: Final sign and reload
dnssec-signzone -o example.com /etc/bind/zones/db.example.com
rndc reload example.com
```

## Step 10: Monitor DNSSEC

### Signature Expiration Monitoring
```bash
# Check signature expiration dates
dig example.com RRSIG A +short | grep -oP 'RRSIG.*' | head -1

# Format: type algorithm labels original_ttl inception expiration keytag signer

# Convert expiration timestamp to date
date -d @1733000000  # Replace with actual timestamp
```

### Monitoring Script
```bash
#!/bin/bash
# dnssec-monitor.sh

ZONE=example.com
NS=ns1.example.com
DAYS_WARNING=7

# Get RRSIG expiration
rrsig=$(dig @$NS $ZONE RRSIG A +short | tail -1)
exp_timestamp=$(echo $rrsig | awk '{print $7}')

# Convert to seconds until expiration
now=$(date +%s)
seconds_left=$((exp_timestamp - now))
days_left=$((seconds_left / 86400))

# Alert if expiring soon
if [ $days_left -lt $DAYS_WARNING ]; then
    echo "WARNING: DNSSEC signature expires in $days_left days"
    # Send alert
    echo "DNSSEC expiring" | mail -s "Alert: $ZONE DNSSEC" ops@example.com
fi
```

Add to cron:
```bash
# Check daily
0 9 * * * /usr/local/bin/dnssec-monitor.sh
```

## Troubleshooting

### Issue: DNSSEC shows BOGUS
```
Check:
1. DS record in parent zone
   dig example.com DS @parent-ns

2. DNSKEY in child zone
   dig @ns1.example.com example.com DNSKEY

3. Signature validity
   dig @ns1.example.com example.com RRSIG A

4. Compare:
   DS key tag must match DNSKEY key tag
   Algorithm must match
```

### Issue: Zone No Longer Signs
```
Check zone file syntax:
dnssec-checkzone -o example.com /etc/bind/zones/db.example.com

Fix errors, then:
dnssec-signzone -o example.com /etc/bind/zones/db.example.com
rndc reload example.com
```

### Issue: DNSSEC Validation Fails
```
Check:
1. Registrar DS record present
2. TTL of DS (wait for propagation)
3. Key algorithm matches
4. Signature not expired

Test locally:
unbound -d -dd -v -c /etc/unbound/unbound.conf
# Check validation logs
```

## Production Checklist

- [ ] Keys generated and backed up securely
- [ ] Zone file includes all DNSKEY records
- [ ] Zone signed with dnssec-signzone
- [ ] BIND configured to use signed zone
- [ ] DS records submitted to registrar
- [ ] Chain of trust verified (DNSSEC Analyzer)
- [ ] Monitoring in place for signature expiration
- [ ] Key rotation schedule documented
- [ ] Automated signing configured
- [ ] Disaster recovery plan for key loss
- [ ] Team trained on DNSSEC operations

# Ransomware Response Guide

## Immediate Response (First 15 Minutes)

### Step 1: Isolate Infected Systems
```bash
# Disconnect from network (keep powered on for forensics)
# Physical: Unplug network cable
# Virtual: Disable network adapter

# If remote access only:
sudo iptables -P INPUT DROP
sudo iptables -P OUTPUT DROP
sudo iptables -P FORWARD DROP

# Document everything
echo "$(date): System isolated" >> /tmp/incident_log.txt
```

### Step 2: Identify Ransomware
- Take screenshot of ransom note
- Document file extensions (.encrypted, .locked, etc.)
- Use ID Ransomware: https://id-ransomware.malwarehunterteam.com/
- Check NoMoreRansom.org for decryptors

### Step 3: Activate Incident Response
```
Priority: P1 (Critical)
Team: Full IR team + Executive notification
Initial Actions:
- Isolate all potentially infected systems
- Preserve logs and evidence
- Assess backup status
- Engage cyber insurance
```

## Investigation (First Hour)

### Determine Scope
```bash
# Search for encrypted files
find / -type f -name "*.encrypted" 2>/dev/null | head -20
find / -type f -name "*.locked" 2>/dev/null | head -20

# Check for ransom notes
find / -type f -name "*README*" -o -name "*DECRYPT*" 2>/dev/null

# Identify patient zero
grep -r "ransomware" /var/log/
journalctl | grep -i crypt

# Check for lateral movement
last | head -20
who
netstat -antp | grep ESTABLISHED
```

### Common Entry Vectors
1. **Phishing email** → Check email logs
2. **RDP brute force** → Check auth logs
3. **Vulnerable service** → Check exposed services
4. **Supply chain** → Check recent software updates

### Forensic Evidence Collection
```bash
# Memory dump (do this first!)
sudo dd if=/dev/mem of=/mnt/usb/memory_$(hostname)_$(date +%Y%m%d).dump

# Disk image
sudo dd if=/dev/sda of=/mnt/storage/disk_$(hostname).img bs=4M status=progress

# Network connections
ss -antp > /mnt/usb/network_connections.txt
netstat -antp > /mnt/usb/netstat.txt

# Running processes
ps auxf > /mnt/usb/processes.txt

# System logs
tar czf /mnt/usb/logs_$(hostname).tar.gz /var/log/

# Timeline of file modifications
find / -type f -mtime -7 -ls > /mnt/usb/recent_modifications.txt
```

## Containment (First 4 Hours)

### Network Segmentation
```
Priority order:
1. Isolate critical systems (DB, domain controllers)
2. Isolate potentially infected systems
3. Monitor inter-VLAN traffic
4. Block outbound C2 communication
```

### Active Directory Response
```powershell
# Disable compromised accounts
Disable-ADAccount -Identity username

# Reset passwords for service accounts
Set-ADAccountPassword -Identity service_account -Reset

# Force password reset on next login for all users
Get-ADUser -Filter * | Set-ADUser -ChangePasswordAtLogon $true

# Check for shadow admins
Get-ADGroupMember -Identity "Domain Admins" -Recursive

# Disable legacy protocols
Set-ADDomainMode -DomainMode Windows2016Domain
```

### Block C2 Communication
```bash
# Common ransomware C2 domains (update from threat intel)
cat <<EOF > /etc/hosts.deny
# Ransomware C2 domains
evil-c2.com
malware-server.net

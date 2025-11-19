# SIEM Correlation Rules

## Splunk Security Use Cases

### Brute Force Detection
```spl
index=auth sourcetype=linux_secure "Failed password"
| stats count by src_ip, user
| where count > 5
| eval severity="HIGH"
| eval description="Brute force attack detected: " + count + " failed login attempts"
```

### Privilege Escalation
```spl
index=windows EventCode=4672 OR EventCode=4673
| stats count by user, Privileges
| where count > 10
| eval severity="CRITICAL"
| eval description="Excessive privileged operations by " + user
```

### Data Exfiltration
```spl
index=firewall action=allowed dest_port!=80 dest_port!=443
| stats sum(bytes_out) as total_bytes by src_ip, dest_ip
| where total_bytes > 1000000000
| eval severity="HIGH"
| eval description="Large data transfer: " + tostring(total_bytes/1024/1024) + " MB"
```

### Malware C2 Communication
```spl
index=dns
| stats count by query
| where count > 100 AND match(query, "\.tk$|\.ml$|\.ga$")
| eval severity="CRITICAL"
| eval description="Suspicious DNS queries to free TLD"
```

### Lateral Movement
```spl
index=windows EventCode=4624 Logon_Type=3
| transaction src_ip, dest_ip maxspan=1m
| where eventcount > 10
| eval severity="HIGH"
| eval description="Rapid lateral movement detected"
```

## Elastic SIEM Rules

```json
{
  "rule": {
    "name": "Suspicious PowerShell Command",
    "description": "Detects PowerShell commands with suspicious patterns",
    "risk_score": 75,
    "severity": "high",
    "type": "query",
    "query": "event.code:4104 AND (powershell.command:*IEX* OR powershell.command:*DownloadString* OR powershell.command:*-enc*)",
    "index": ["winlogbeat-*"],
    "interval": "5m",
    "actions": [
      {
        "group": "default",
        "id": "slack-alert",
        "params": {
          "message": "Suspicious PowerShell detected on {{host.name}}"
        }
      }
    ]
  }
}
```

## QRadar AQL Queries

```sql
-- Failed logins followed by success
SELECT sourceip, username, COUNT(*) as failed_attempts
FROM events
WHERE eventname='Failed Login'
AND devicetime > CURRENT_TIMESTAMP - 10 MINUTES
GROUP BY sourceip, username
HAVING failed_attempts > 5

-- New admin account creation
SELECT username, sourceip, destinationip
FROM events
WHERE eventname='User Account Created'
AND usergroup CONTAINS 'admin'
AND devicetime > CURRENT_TIMESTAMP - 24 HOURS
```

## Detection Rules Library

### Ransomware Indicators
```spl
index=endpoint sourcetype=sysmon EventCode=1
(CommandLine="*vssadmin*delete*shadows*" OR
 CommandLine="*wevtutil*cl*" OR
 CommandLine="*bcdedit*recoveryenabled*No*")
| stats count by host, CommandLine
| eval severity="CRITICAL"
| eval alert="Possible ransomware activity"
```

### Credential Dumping
```spl
index=windows EventCode=10 TargetImage="*lsass.exe"
| where NOT [search index=whitelist sourcetype=known_processes]
| eval severity="CRITICAL"
| eval alert="Credential dumping attempt detected"
```

### Web Shell Detection
```spl
index=web_logs
| search *.aspx OR *.jsp OR *.php
| search POST
| eval length=len(form_data)
| where length > 1000
| stats count by uri_path, src_ip
| where count > 10
```

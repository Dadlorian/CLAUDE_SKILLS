# MITRE ATT&CK Mapping Guide

## Common Techniques by Tactic

### Initial Access (TA0001)
| ID | Technique | Detection | Mitigation |
|----|-----------|-----------|------------|
| T1566.001 | Phishing: Spearphishing Attachment | Email filtering, user reporting | Security awareness training, email authentication (DMARC) |
| T1566.002 | Phishing: Spearphishing Link | URL filtering, sandboxing | Safe links, user education |
| T1190 | Exploit Public-Facing Application | WAF logs, vulnerability scanning | Patch management, WAF |
| T1133 | External Remote Services | VPN logs, failed auth attempts | MFA, IP allowlisting |

### Execution (TA0002)
| T1059.001 | PowerShell | Script block logging, command monitoring | Constrained language mode, application whitelisting |
| T1059.003 | Windows Command Shell | Process monitoring, Sysmon | AppLocker, WDAC |
| T1203 | Exploitation for Client Execution | Endpoint detection, anomaly detection | Patch management, endpoint protection |

### Persistence (TA0003)
| T1053.005 | Scheduled Task | Sysmon Event ID 1, task scheduler logs | Least privilege, monitor scheduled tasks |
| T1136 | Create Account | Account creation logs, AD monitoring | Account creation approval process |
| T1547.001 | Registry Run Keys | Registry monitoring, Sysmon Event ID 13 | Application whitelisting |

### Privilege Escalation (TA0004)
| T1068 | Exploitation for Privilege Escalation | Endpoint detection, kernel monitoring | Patch management, least privilege |
| T1078 | Valid Accounts | Unusual login patterns, privileged account monitoring | PAM, MFA |
| T1548.002 | Bypass User Account Control | Process monitoring, UAC bypass signatures | UAC enabled, least privilege |

### Defense Evasion (TA0005)
| T1070 | Indicator Removal on Host | Log integrity monitoring, file deletion monitoring | Centralized logging, log forwarding |
| T1027 | Obfuscated Files or Information | File entropy analysis, YARA rules | Endpoint detection |
| T1562.001 | Disable or Modify Tools | Security tool monitoring, process termination alerts | Protected security tools |

### Credential Access (TA0006)
| T1003.001 | LSASS Memory | Process access monitoring, credential guard | Credential Guard, LSA Protection |
| T1110 | Brute Force | Failed authentication logs, account lockout | Account lockout policy, MFA |
| T1555 | Credentials from Password Stores | File access monitoring | Encrypt password stores |

### Discovery (TA0007)
| T1087 | Account Discovery | Process monitoring, command line logging | Normal user behavior baseline |
| T1082 | System Information Discovery | Process monitoring | Monitor system info commands |
| T1083 | File and Directory Discovery | File enumeration monitoring | Least privilege file access |

### Lateral Movement (TA0008)
| T1021.001 | Remote Desktop Protocol | RDP connection logs, unusual RDP activity | MFA, network segmentation |
| T1021.002 | SMB/Windows Admin Shares | SMB traffic monitoring, admin share access | Disable admin shares, least privilege |
| T1550.002 | Pass the Hash | Unusual authentication patterns, privileged account monitoring | Credential Guard, PAM |

### Collection (TA0009)
| T1005 | Data from Local System | File access logs, large file transfers | DLP, encryption |
| T1039 | Data from Network Shared Drive | Network share access logs | Access controls, monitoring |
| T1113 | Screen Capture | Process monitoring for screenshot tools | Endpoint detection |

### Exfiltration (TA0010)
| T1041 | Exfiltration Over C2 Channel | Network traffic analysis, data transfer size | DLP, network egress filtering |
| T1567 | Exfiltration Over Web Service | Cloud access logs, unusual uploads | CASB, DLP |
| T1048 | Exfiltration Over Alternative Protocol | DNS queries, ICMP traffic | Protocol monitoring, egress filtering |

### Command and Control (TA0011)
| T1071.001 | Web Protocols | HTTP/HTTPS traffic analysis, beaconing detection | Proxy filtering, threat intel feeds |
| T1573 | Encrypted Channel | TLS inspection, unusual encryption | TLS inspection, endpoint detection |
| T1105 | Ingress Tool Transfer | File downloads, process creation | Application whitelisting |

## Detection Implementation

### Splunk Queries
```spl
# Detect PowerShell Obfuscation (T1059.001)
index=windows EventCode=4104
| eval obfuscation_score=0
| eval obfuscation_score=if(like(ScriptBlockText,"%^%"), obfuscation_score+1, obfuscation_score)
| eval obfuscation_score=if(like(ScriptBlockText,"%-%"), obfuscation_score+1, obfuscation_score)
| where obfuscation_score > 5

# Detect Credential Dumping (T1003.001)
index=windows EventCode=10 TargetImage="*lsass.exe"
| stats count by SourceImage, SourceProcessId

# Detect Lateral Movement via RDP (T1021.001)
index=windows EventCode=4624 Logon_Type=10
| stats count by src_ip, user, dest_ip
| where count > 5

# Detect Suspicious Scheduled Task (T1053.005)
index=windows EventCode=4698
| search NOT [| inputlookup known_scheduled_tasks.csv]

# Detect Account Creation (T1136)
index=windows EventCode=4720
| table _time, user, src_ip, Account_Name
```

### Sigma Rules
```yaml
title: LSASS Memory Dump (T1003.001)
status: stable
description: Detects process accessing LSASS memory
references:
  - https://attack.mitre.org/techniques/T1003/001/
logsource:
  product: windows
  service: sysmon
detection:
  selection:
    EventID: 10
    TargetImage|endswith: '\lsass.exe'
  condition: selection
falsepositives:
  - Legitimate debugging tools
level: high
tags:
  - attack.credential_access
  - attack.t1003.001
```

## MITRE ATT&CK Navigator Layer

```json
{
  "name": "Detection Coverage",
  "versions": {
    "attack": "13",
    "navigator": "4.8",
    "layer": "4.4"
  },
  "domain": "enterprise-attack",
  "description": "Organization detection coverage",
  "techniques": [
    {
      "techniqueID": "T1566.001",
      "score": 100,
      "color": "#00ff00",
      "comment": "Email filtering + user training"
    },
    {
      "techniqueID": "T1059.001",
      "score": 75,
      "color": "#ffff00",
      "comment": "PowerShell logging enabled"
    },
    {
      "techniqueID": "T1003.001",
      "score": 50,
      "color": "#ff6600",
      "comment": "Partial coverage - missing Credential Guard"
    }
  ]
}
```

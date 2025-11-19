# IDS/IPS Rules - Production Examples

## Snort/Suricata Rules

### SQL Injection Detection
```
alert tcp any any -> $HOME_NET $HTTP_PORTS (
  msg:"SQL Injection - UNION SELECT";
  flow:to_server,established;
  content:"UNION"; nocase; http_uri;
  content:"SELECT"; nocase; http_uri; distance:0;
  pcre:"/UNION.+SELECT/i";
  classtype:web-application-attack;
  sid:1000001; rev:2;
)

alert tcp any any -> $HOME_NET $HTTP_PORTS (
  msg:"SQL Injection - OR 1=1";
  flow:to_server,established;
  content:"OR"; nocase; http_uri;
  pcre:"/OR\s+\d+\s*=\s*\d+/i";
  classtype:web-application-attack;
  sid:1000002; rev:1;
)
```

### XSS Detection
```
alert tcp any any -> $HOME_NET $HTTP_PORTS (
  msg:"XSS Attempt - Script Tag";
  flow:to_server,established;
  content:"<script"; nocase; http_uri;
  classtype:web-application-attack;
  sid:1000010; rev:1;
)

alert tcp any any -> $HOME_NET $HTTP_PORTS (
  msg:"XSS Attempt - Event Handler";
  flow:to_server,established;
  pcre:"/(onload|onerror|onclick|onmouseover)\s*=/i";
  classtype:web-application-attack;
  sid:1000011; rev:1;
)
```

### Command Injection
```
alert tcp any any -> $HOME_NET $HTTP_PORTS (
  msg:"Command Injection - Shell Metacharacters";
  flow:to_server,established;
  pcre:"/[;&|`$()]/";
  classtype:web-application-attack;
  sid:1000020; rev:1;
)
```

### Reconnaissance Detection
```
alert tcp any any -> $HOME_NET any (
  msg:"Port Scan Detected";
  flags:S;
  threshold:type both, track by_src, count 20, seconds 60;
  classtype:attempted-recon;
  sid:1000030; rev:1;
)

alert icmp any any -> $HOME_NET any (
  msg:"ICMP Sweep Detected";
  itype:8;
  threshold:type both, track by_src, count 10, seconds 30;
  classtype:attempted-recon;
  sid:1000031; rev:1;
)
```

### Brute Force Detection
```
alert tcp any any -> $HOME_NET 22 (
  msg:"SSH Brute Force Attempt";
  flow:to_server,established;
  content:"SSH-";
  threshold:type both, track by_src, count 5, seconds 60;
  classtype:attempted-admin;
  sid:1000040; rev:1;
)

alert tcp any any -> $HOME_NET $HTTP_PORTS (
  msg:"HTTP Authentication Brute Force";
  flow:to_server,established;
  content:"401"; http_stat_code;
  threshold:type both, track by_src, count 10, seconds 60;
  classtype:attempted-admin;
  sid:1000041; rev:1;
)
```

### Malware C2 Detection
```
alert tcp $HOME_NET any -> $EXTERNAL_NET any (
  msg:"Possible Cobalt Strike Beacon";
  flow:to_server,established;
  content:"|00 00 00|"; depth:3;
  content:"|be ef|"; distance:0;
  classtype:trojan-activity;
  reference:url,attack.mitre.org/software/S0154;
  sid:1000050; rev:1;
)

alert tcp $HOME_NET any -> $EXTERNAL_NET $HTTP_PORTS (
  msg:"Possible Metasploit Reverse Shell";
  flow:to_server,established;
  content:"RECV"; nocase;
  content:"msf"; nocase; distance:0;
  classtype:trojan-activity;
  sid:1000051; rev:1;
)
```

### Data Exfiltration
```
alert tcp $HOME_NET any -> $EXTERNAL_NET $HTTP_PORTS (
  msg:"Large Outbound HTTP POST - Possible Exfiltration";
  flow:to_server,established;
  content:"POST"; http_method;
  byte_test:4,>,1000000,0,relative;
  classtype:policy-violation;
  sid:1000060; rev:1;
)

alert tcp $HOME_NET any -> $EXTERNAL_NET any (
  msg:"DNS Tunneling - Long Query";
  flow:to_server,established;
  content:"|01 00 00 01 00 00 00 00 00 00|"; depth:10;
  byte_test:1,>,100,12;
  classtype:policy-violation;
  sid:1000061; rev:1;
)
```

## Performance Tuning

```yaml
# Suricata configuration for high-performance
vars:
  address-groups:
    HOME_NET: "[10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16]"
    EXTERNAL_NET: "!$HOME_NET"
    HTTP_SERVERS: "10.0.1.0/24"
    SMTP_SERVERS: "10.0.2.0/24"
    SQL_SERVERS: "10.0.3.0/24"

af-packet:
  - interface: eth0
    threads: 4
    cluster-type: cluster_flow
    defrag: yes
    use-mmap: yes
    ring-size: 10000

stream:
  memcap: 64mb
  checksum-validation: yes
  inline: auto
  reassembly:
    memcap: 256mb
    depth: 1mb
    toserver-chunk-size: 2560
    toclient-chunk-size: 2560

outputs:
  - fast:
      enabled: yes
      filename: fast.log
  - eve-log:
      enabled: yes
      filetype: regular
      filename: eve.json
      types:
        - alert
        - http
        - dns
        - tls

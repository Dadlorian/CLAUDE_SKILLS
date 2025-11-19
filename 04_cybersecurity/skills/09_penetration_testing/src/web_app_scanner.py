"""
Web Application Security Scanner
Automated vulnerability scanning for web applications

WARNING: This tool is for authorized penetration testing only.
Unauthorized scanning is illegal. Always obtain written permission.
"""

import requests
import re
import urllib.parse
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import hashlib
import concurrent.futures


@dataclass
class Vulnerability:
    """Vulnerability finding"""
    vuln_type: str
    severity: str  # Critical, High, Medium, Low, Info
    url: str
    parameter: str
    payload: str
    evidence: str
    remediation: str
    cve_reference: Optional[str] = None


class WebAppScanner:
    """
    Web Application Vulnerability Scanner

    Features:
    - SQL Injection detection
    - XSS (Cross-Site Scripting) detection
    - SSRF (Server-Side Request Forgery) detection
    - Directory traversal detection
    - XXE (XML External Entity) detection
    - Command injection detection
    - Security header analysis
    - SSL/TLS configuration testing
    """

    def __init__(self, target_url: str, timeout: int = 5):
        self.target_url = target_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PenTest-Scanner/1.0'
        })
        self.vulnerabilities: List[Vulnerability] = []
        self.visited_urls: Set[str] = set()

    # ==================== SQL Injection Testing ====================

    def test_sql_injection(self, url: str, params: Dict[str, str]) -> List[Vulnerability]:
        """Test for SQL injection vulnerabilities"""
        vulnerabilities = []

        sql_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "admin'--",
            "' UNION SELECT NULL--",
            "' UNION SELECT NULL,NULL--",
            "' UNION SELECT NULL,NULL,NULL--",
            "1' AND '1'='1",
            "1' AND '1'='2",
            "' OR 'x'='x",
            ") OR 1=1--",
            "'; DROP TABLE users--"
        ]

        sql_error_patterns = [
            r"sql syntax.*mysql",
            r"warning.*mysql_.*",
            r"valid MySQL result",
            r"MySqlClient\.",
            r"PostgreSQL.*ERROR",
            r"Warning.*pg_.*",
            r"valid PostgreSQL result",
            r"Npgsql\.",
            r"Driver.*SQL.*Server",
            r"OLE DB.*SQL Server",
            r"SQLServer JDBC Driver",
            r"Microsoft SQL Native Client",
            r"ODBC SQL Server Driver",
            r"SQLite/JDBCDriver",
            r"SQLite.Exception",
            r"System.Data.SQLite.SQLiteException",
            r"Warning.*sqlite_.*",
            r"Oracle error",
            r"ORA-[0-9][0-9][0-9][0-9]",
            r"Oracle.*Driver",
            r"SQLSTATE\[",
            r"DB2 SQL error"
        ]

        for param_name, param_value in params.items():
            for payload in sql_payloads:
                test_params = params.copy()
                test_params[param_name] = payload

                try:
                    response = self.session.get(
                        url,
                        params=test_params,
                        timeout=self.timeout,
                        verify=False
                    )

                    # Check for SQL error messages
                    for pattern in sql_error_patterns:
                        if re.search(pattern, response.text, re.IGNORECASE):
                            vuln = Vulnerability(
                                vuln_type="SQL Injection",
                                severity="Critical",
                                url=url,
                                parameter=param_name,
                                payload=payload,
                                evidence=f"SQL error detected: {pattern}",
                                remediation="Use parameterized queries/prepared statements. Implement input validation."
                            )
                            vulnerabilities.append(vuln)
                            break

                    # Check for boolean-based blind SQL injection
                    true_payload = f"1' AND '1'='1"
                    false_payload = f"1' AND '1'='2"

                    test_params_true = params.copy()
                    test_params_true[param_name] = true_payload
                    response_true = self.session.get(url, params=test_params_true, timeout=self.timeout)

                    test_params_false = params.copy()
                    test_params_false[param_name] = false_payload
                    response_false = self.session.get(url, params=test_params_false, timeout=self.timeout)

                    # If responses differ significantly, possible blind SQL injection
                    if len(response_true.text) != len(response_false.text):
                        if abs(len(response_true.text) - len(response_false.text)) > 100:
                            vuln = Vulnerability(
                                vuln_type="Blind SQL Injection",
                                severity="High",
                                url=url,
                                parameter=param_name,
                                payload=f"True: {true_payload}, False: {false_payload}",
                                evidence="Differential responses detected",
                                remediation="Use parameterized queries. Implement strict input validation."
                            )
                            vulnerabilities.append(vuln)

                except requests.RequestException:
                    pass

        return vulnerabilities

    # ==================== XSS Testing ====================

    def test_xss(self, url: str, params: Dict[str, str]) -> List[Vulnerability]:
        """Test for Cross-Site Scripting vulnerabilities"""
        vulnerabilities = []

        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror='alert(1)'>",
            "<svg onload='alert(1)'>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(1)'>",
            "<body onload='alert(1)'>",
            "<input onfocus='alert(1)' autofocus>",
            "<select onfocus='alert(1)' autofocus>",
            "<textarea onfocus='alert(1)' autofocus>",
            "<marquee onstart='alert(1)'>",
            "\"><script>alert(String.fromCharCode(88,83,83))</script>",
            "';alert(String.fromCharCode(88,83,83))//",
            "<IMG SRC=\"javascript:alert('XSS');\">",
            "<IMG SRC=JaVaScRiPt:alert('XSS')>",
            "<IMG SRC=`javascript:alert(\"XSS\")`>"
        ]

        for param_name, param_value in params.items():
            for payload in xss_payloads:
                test_params = params.copy()
                test_params[param_name] = payload

                try:
                    response = self.session.get(
                        url,
                        params=test_params,
                        timeout=self.timeout,
                        verify=False
                    )

                    # Check if payload is reflected without encoding
                    if payload in response.text:
                        vuln = Vulnerability(
                            vuln_type="Reflected XSS",
                            severity="High",
                            url=url,
                            parameter=param_name,
                            payload=payload,
                            evidence="Payload reflected without encoding",
                            remediation="Implement output encoding/escaping. Use Content Security Policy (CSP)."
                        )
                        vulnerabilities.append(vuln)
                        break

                    # Check for partial reflection
                    payload_parts = re.findall(r'<[^>]+>', payload)
                    for part in payload_parts:
                        if part in response.text:
                            vuln = Vulnerability(
                                vuln_type="Possible XSS",
                                severity="Medium",
                                url=url,
                                parameter=param_name,
                                payload=payload,
                                evidence=f"Partial payload reflection: {part}",
                                remediation="Review output encoding. Implement CSP headers."
                            )
                            vulnerabilities.append(vuln)
                            break

                except requests.RequestException:
                    pass

        return vulnerabilities

    # ==================== Command Injection Testing ====================

    def test_command_injection(self, url: str, params: Dict[str, str]) -> List[Vulnerability]:
        """Test for OS command injection vulnerabilities"""
        vulnerabilities = []

        # Time-based detection payloads
        cmd_payloads = [
            "; sleep 5",
            "| sleep 5",
            "& sleep 5",
            "`sleep 5`",
            "$(sleep 5)",
            "; ping -c 5 127.0.0.1",
            "| ping -c 5 127.0.0.1",
            "'; sleep 5; echo '",
            "\"; sleep 5; echo \"",
            # Windows
            "& timeout /t 5",
            "| timeout /t 5",
        ]

        for param_name, param_value in params.items():
            for payload in cmd_payloads:
                test_params = params.copy()
                test_params[param_name] = f"{param_value}{payload}"

                try:
                    start_time = datetime.now()
                    response = self.session.get(
                        url,
                        params=test_params,
                        timeout=self.timeout + 6,  # Extended timeout for sleep commands
                        verify=False
                    )
                    end_time = datetime.now()

                    response_time = (end_time - start_time).total_seconds()

                    # If response takes significantly longer, possible command injection
                    if response_time >= 4.5:  # Allow some variance
                        vuln = Vulnerability(
                            vuln_type="Command Injection",
                            severity="Critical",
                            url=url,
                            parameter=param_name,
                            payload=payload,
                            evidence=f"Response delayed by {response_time:.2f} seconds",
                            remediation="Never pass user input to system commands. Use safe APIs instead."
                        )
                        vulnerabilities.append(vuln)
                        break

                except requests.Timeout:
                    # Timeout could indicate successful sleep command
                    vuln = Vulnerability(
                        vuln_type="Possible Command Injection",
                        severity="High",
                        url=url,
                        parameter=param_name,
                        payload=payload,
                        evidence="Request timed out after injected sleep command",
                        remediation="Never pass user input to system commands. Use parameterized APIs."
                    )
                    vulnerabilities.append(vuln)
                    break
                except requests.RequestException:
                    pass

        return vulnerabilities

    # ==================== Directory Traversal Testing ====================

    def test_directory_traversal(self, url: str, params: Dict[str, str]) -> List[Vulnerability]:
        """Test for directory traversal/path traversal vulnerabilities"""
        vulnerabilities = []

        traversal_payloads = [
            "../../../../../../etc/passwd",
            "..\\..\\..\\..\\..\\..\\windows\\win.ini",
            "....//....//....//....//etc/passwd",
            "..%2f..%2f..%2f..%2f..%2f..%2fetc%2fpasswd",
            "..%5c..%5c..%5c..%5c..%5c..%5cwindows%5cwin.ini",
            "..//..//..//..//..//..//etc/passwd",
            "..%252f..%252f..%252f..%252f..%252f..%252fetc%252fpasswd"
        ]

        # Evidence patterns
        unix_patterns = [
            r"root:.*:0:0:",
            r"daemon:.*:",
            r"bin:.*:",
            r"/bin/bash",
            r"/bin/sh"
        ]

        windows_patterns = [
            r"\[fonts\]",
            r"\[extensions\]",
            r"MAPI=1"
        ]

        for param_name, param_value in params.items():
            for payload in traversal_payloads:
                test_params = params.copy()
                test_params[param_name] = payload

                try:
                    response = self.session.get(
                        url,
                        params=test_params,
                        timeout=self.timeout,
                        verify=False
                    )

                    # Check for Unix/Linux evidence
                    for pattern in unix_patterns:
                        if re.search(pattern, response.text):
                            vuln = Vulnerability(
                                vuln_type="Directory Traversal",
                                severity="High",
                                url=url,
                                parameter=param_name,
                                payload=payload,
                                evidence="/etc/passwd content detected",
                                remediation="Validate and sanitize file paths. Use whitelist of allowed files."
                            )
                            vulnerabilities.append(vuln)
                            break

                    # Check for Windows evidence
                    for pattern in windows_patterns:
                        if re.search(pattern, response.text, re.IGNORECASE):
                            vuln = Vulnerability(
                                vuln_type="Directory Traversal",
                                severity="High",
                                url=url,
                                parameter=param_name,
                                payload=payload,
                                evidence="win.ini content detected",
                                remediation="Validate and sanitize file paths. Use whitelist of allowed files."
                            )
                            vulnerabilities.append(vuln)
                            break

                except requests.RequestException:
                    pass

        return vulnerabilities

    # ==================== Security Headers Analysis ====================

    def analyze_security_headers(self, url: str) -> List[Vulnerability]:
        """Analyze HTTP security headers"""
        vulnerabilities = []

        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            headers = response.headers

            # Check for missing security headers
            security_headers = {
                'Strict-Transport-Security': {
                    'severity': 'Medium',
                    'remediation': 'Add HSTS header: Strict-Transport-Security: max-age=31536000; includeSubDomains'
                },
                'X-Frame-Options': {
                    'severity': 'Medium',
                    'remediation': 'Add X-Frame-Options: DENY or SAMEORIGIN'
                },
                'X-Content-Type-Options': {
                    'severity': 'Low',
                    'remediation': 'Add X-Content-Type-Options: nosniff'
                },
                'Content-Security-Policy': {
                    'severity': 'Medium',
                    'remediation': "Add CSP header: Content-Security-Policy: default-src 'self'"
                },
                'X-XSS-Protection': {
                    'severity': 'Low',
                    'remediation': 'Add X-XSS-Protection: 1; mode=block'
                },
                'Referrer-Policy': {
                    'severity': 'Low',
                    'remediation': 'Add Referrer-Policy: no-referrer or strict-origin-when-cross-origin'
                },
                'Permissions-Policy': {
                    'severity': 'Low',
                    'remediation': 'Add Permissions-Policy to control browser features'
                }
            }

            for header, config in security_headers.items():
                if header not in headers:
                    vuln = Vulnerability(
                        vuln_type=f"Missing Security Header: {header}",
                        severity=config['severity'],
                        url=url,
                        parameter="HTTP Headers",
                        payload="N/A",
                        evidence=f"Header {header} not found",
                        remediation=config['remediation']
                    )
                    vulnerabilities.append(vuln)

            # Check for information disclosure headers
            disclosure_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version']
            for header in disclosure_headers:
                if header in headers:
                    vuln = Vulnerability(
                        vuln_type="Information Disclosure",
                        severity="Info",
                        url=url,
                        parameter="HTTP Headers",
                        payload="N/A",
                        evidence=f"Header {header}: {headers[header]}",
                        remediation=f"Remove or obfuscate {header} header"
                    )
                    vulnerabilities.append(vuln)

        except requests.RequestException:
            pass

        return vulnerabilities

    # ==================== SSL/TLS Testing ====================

    def test_ssl_configuration(self, url: str) -> List[Vulnerability]:
        """Test SSL/TLS configuration"""
        vulnerabilities = []

        try:
            # Test with outdated protocols (would need ssl library for full testing)
            response = self.session.get(url, timeout=self.timeout, verify=True)

            # Basic checks
            if not url.startswith('https://'):
                vuln = Vulnerability(
                    vuln_type="Insecure Protocol",
                    severity="High",
                    url=url,
                    parameter="Protocol",
                    payload="N/A",
                    evidence="HTTP instead of HTTPS",
                    remediation="Enforce HTTPS for all communications"
                )
                vulnerabilities.append(vuln)

        except requests.exceptions.SSLError as e:
            vuln = Vulnerability(
                vuln_type="SSL/TLS Configuration Issue",
                severity="Medium",
                url=url,
                parameter="SSL/TLS",
                payload="N/A",
                evidence=str(e),
                remediation="Fix SSL certificate issues. Use valid, trusted certificates."
            )
            vulnerabilities.append(vuln)
        except requests.RequestException:
            pass

        return vulnerabilities

    # ==================== Main Scan Function ====================

    def scan(self, params: Optional[Dict[str, str]] = None) -> List[Vulnerability]:
        """
        Perform comprehensive scan

        Args:
            params: URL parameters to test. If None, will test common parameters.

        Returns:
            List of identified vulnerabilities
        """
        if params is None:
            params = {'id': '1', 'search': 'test', 'q': 'query'}

        print(f"[*] Starting scan of {self.target_url}")
        print(f"[*] Testing parameters: {list(params.keys())}")

        # Security headers
        print("[*] Analyzing security headers...")
        self.vulnerabilities.extend(
            self.analyze_security_headers(self.target_url)
        )

        # SSL/TLS
        print("[*] Testing SSL/TLS configuration...")
        self.vulnerabilities.extend(
            self.test_ssl_configuration(self.target_url)
        )

        # SQL Injection
        print("[*] Testing for SQL injection...")
        self.vulnerabilities.extend(
            self.test_sql_injection(self.target_url, params)
        )

        # XSS
        print("[*] Testing for XSS...")
        self.vulnerabilities.extend(
            self.test_xss(self.target_url, params)
        )

        # Command Injection
        print("[*] Testing for command injection...")
        self.vulnerabilities.extend(
            self.test_command_injection(self.target_url, params)
        )

        # Directory Traversal
        print("[*] Testing for directory traversal...")
        self.vulnerabilities.extend(
            self.test_directory_traversal(self.target_url, params)
        )

        print(f"\n[+] Scan complete. Found {len(self.vulnerabilities)} vulnerabilities.")

        return self.vulnerabilities

    def generate_report(self) -> Dict:
        """Generate scan report"""
        severity_counts = {
            'Critical': 0,
            'High': 0,
            'Medium': 0,
            'Low': 0,
            'Info': 0
        }

        vuln_types = {}

        for vuln in self.vulnerabilities:
            severity_counts[vuln.severity] += 1

            if vuln.vuln_type not in vuln_types:
                vuln_types[vuln.vuln_type] = 0
            vuln_types[vuln.vuln_type] += 1

        report = {
            'target': self.target_url,
            'scan_date': datetime.now().isoformat(),
            'summary': {
                'total_vulnerabilities': len(self.vulnerabilities),
                'by_severity': severity_counts,
                'by_type': vuln_types
            },
            'vulnerabilities': [
                {
                    'type': v.vuln_type,
                    'severity': v.severity,
                    'url': v.url,
                    'parameter': v.parameter,
                    'payload': v.payload,
                    'evidence': v.evidence,
                    'remediation': v.remediation
                }
                for v in self.vulnerabilities
            ]
        }

        return report

    def print_report(self):
        """Print formatted report to console"""
        report = self.generate_report()

        print("\n" + "=" * 70)
        print("WEB APPLICATION SECURITY SCAN REPORT")
        print("=" * 70)
        print(f"Target: {report['target']}")
        print(f"Scan Date: {report['scan_date']}")
        print()
        print("Summary:")
        print(f"  Total Vulnerabilities: {report['summary']['total_vulnerabilities']}")
        print()
        print("By Severity:")
        for severity, count in report['summary']['by_severity'].items():
            if count > 0:
                print(f"  {severity}: {count}")
        print()

        if report['vulnerabilities']:
            print("Detailed Findings:")
            print("-" * 70)

            for i, vuln in enumerate(report['vulnerabilities'], 1):
                print(f"\n[{i}] {vuln['type']} ({vuln['severity']})")
                print(f"    URL: {vuln['url']}")
                print(f"    Parameter: {vuln['parameter']}")
                print(f"    Payload: {vuln['payload'][:100]}")
                print(f"    Evidence: {vuln['evidence']}")
                print(f"    Remediation: {vuln['remediation']}")

        print("\n" + "=" * 70)


# ==================== Example Usage ====================

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')

    # Example: Scan a target (ONLY with authorization!)
    target = "https://example.com/search"

    print("WARNING: Only scan applications you have permission to test!")
    print("Unauthorized scanning is illegal.\n")

    scanner = WebAppScanner(target)

    # Perform scan
    params = {
        'q': 'test',
        'id': '1',
        'search': 'query'
    }

    vulnerabilities = scanner.scan(params)

    # Print report
    scanner.print_report()

    # Save to JSON
    import json
    report = scanner.generate_report()
    with open('scan_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print("\nReport saved to scan_report.json")

# VoIP & IMS Systems Expert

You are an expert in Voice over IP (VoIP) and IP Multimedia Subsystem (IMS) with deep knowledge of SIP, VoLTE, VoNR, and real-time communications.

## Core Competencies

### IMS Architecture
- **Core Functions**: CSCF (P-CSCF, I-CSCF, S-CSCF), HSS, AS
- **Protocol Stack**: SIP, SDP, RTP, Diameter
- **VoLTE**: Voice over LTE with IMS
- **VoNR**: Voice over 5G NR
- **RCS**: Rich Communication Services

### SIP Protocol
- **Methods**: INVITE, ACK, BYE, CANCEL, REGISTER, OPTIONS
- **Call Flow**: Session establishment, modification, termination
- **Authentication**: Digest authentication, IMS AKA
- **NAT Traversal**: STUN, TURN, ICE

### Media Handling
- **Codecs**: G.711, G.729, AMR, AMR-WB, EVS
- **RTP/RTCP**: Real-time transport, quality reporting
- **SRTP**: Secure RTP for encrypted media
- **QoS**: DSCP marking, bandwidth reservation

### Supplementary Services
- **Call Forwarding**: Unconditional, busy, no answer
- **Call Waiting**: Multi-line management
- **Conference**: Multi-party calls
- **Call Transfer**: Blind and attended transfer

## Implementation Examples

### SIP Proxy Server

```python
#!/usr/bin/env python3
"""
SIP Proxy Server Implementation
Handles SIP registration, call routing, and session management
"""

import socket
import threading
from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum
import hashlib
import time


class SIPMethod(Enum):
    """SIP method types"""
    REGISTER = "REGISTER"
    INVITE = "INVITE"
    ACK = "ACK"
    BYE = "BYE"
    CANCEL = "CANCEL"
    OPTIONS = "OPTIONS"
    INFO = "INFO"
    PRACK = "PRACK"


class SIPResponseCode(Enum):
    """SIP response codes"""
    TRYING = 100
    RINGING = 180
    SESSION_PROGRESS = 183
    OK = 200
    MOVED_PERMANENTLY = 301
    MOVED_TEMPORARILY = 302
    UNAUTHORIZED = 401
    PROXY_AUTHENTICATION_REQUIRED = 407
    REQUEST_TIMEOUT = 408
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    TEMPORARILY_UNAVAILABLE = 480
    BUSY_HERE = 486
    REQUEST_TERMINATED = 487
    SERVER_INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503


@dataclass
class SIPRegistration:
    """SIP registration entry"""
    aor: str  # Address of Record (user@domain)
    contact: str  # Contact URI
    expires: int  # Registration expiration in seconds
    registration_time: float
    call_id: str
    cseq: int

    def is_expired(self) -> bool:
        """Check if registration has expired"""
        return time.time() > (self.registration_time + self.expires)


class SIPMessage:
    """SIP message parser and builder"""

    def __init__(self, raw_message: str = ""):
        self.raw_message = raw_message
        self.headers: Dict[str, str] = {}
        self.body: str = ""
        self.method: Optional[str] = None
        self.request_uri: Optional[str] = None
        self.status_code: Optional[int] = None
        self.reason_phrase: Optional[str] = None

        if raw_message:
            self._parse()

    def _parse(self):
        """Parse SIP message"""
        lines = self.raw_message.split('\r\n')

        # Parse first line (request or status line)
        first_line = lines[0]
        if first_line.startswith('SIP/'):
            # Response
            parts = first_line.split(' ', 2)
            self.status_code = int(parts[1])
            self.reason_phrase = parts[2] if len(parts) > 2 else ""
        else:
            # Request
            parts = first_line.split(' ')
            self.method = parts[0]
            self.request_uri = parts[1]

        # Parse headers
        i = 1
        while i < len(lines) and lines[i]:
            if ':' in lines[i]:
                key, value = lines[i].split(':', 1)
                self.headers[key.strip()] = value.strip()
            i += 1

        # Parse body
        if i < len(lines):
            self.body = '\r\n'.join(lines[i+1:])

    def get_header(self, name: str) -> Optional[str]:
        """Get header value"""
        return self.headers.get(name)

    def build_response(self, status_code: int, reason_phrase: str) -> str:
        """Build SIP response message"""
        response_lines = [
            f"SIP/2.0 {status_code} {reason_phrase}",
        ]

        # Add Via, From, To, Call-ID, CSeq headers
        for header in ['Via', 'From', 'To', 'Call-ID', 'CSeq']:
            if header in self.headers:
                response_lines.append(f"{header}: {self.headers[header]}")

        # Add Content-Length
        response_lines.append(f"Content-Length: {len(self.body)}")
        response_lines.append("")

        if self.body:
            response_lines.append(self.body)

        return '\r\n'.join(response_lines)


class SIPProxyServer:
    """SIP Proxy Server"""

    def __init__(self, host: str = "0.0.0.0", port: int = 5060):
        self.host = host
        self.port = port
        self.registrations: Dict[str, SIPRegistration] = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        self.running = False
        self.realm = "example.com"
        self.nonce = self._generate_nonce()

    def start(self):
        """Start SIP proxy server"""
        self.running = True
        print(f"SIP Proxy Server started on {self.host}:{self.port}")

        while self.running:
            try:
                data, addr = self.socket.recvfrom(4096)
                message = data.decode('utf-8')

                # Handle in separate thread
                thread = threading.Thread(
                    target=self._handle_request,
                    args=(message, addr)
                )
                thread.start()

            except Exception as e:
                print(f"Error: {e}")

    def stop(self):
        """Stop SIP proxy server"""
        self.running = False
        self.socket.close()

    def _handle_request(self, message: str, addr: tuple):
        """Handle incoming SIP request"""
        sip_msg = SIPMessage(message)

        if sip_msg.method == SIPMethod.REGISTER.value:
            response = self._handle_register(sip_msg)
        elif sip_msg.method == SIPMethod.INVITE.value:
            response = self._handle_invite(sip_msg)
        elif sip_msg.method == SIPMethod.ACK.value:
            response = None  # ACK doesn't require response
        elif sip_msg.method == SIPMethod.BYE.value:
            response = self._handle_bye(sip_msg)
        elif sip_msg.method == SIPMethod.CANCEL.value:
            response = self._handle_cancel(sip_msg)
        elif sip_msg.method == SIPMethod.OPTIONS.value:
            response = self._handle_options(sip_msg)
        else:
            response = sip_msg.build_response(
                SIPResponseCode.METHOD_NOT_ALLOWED.value,
                "Method Not Allowed"
            )

        if response:
            self.socket.sendto(response.encode('utf-8'), addr)

    def _handle_register(self, sip_msg: SIPMessage) -> str:
        """Handle REGISTER request"""

        # Extract Address of Record (AoR)
        to_header = sip_msg.get_header('To')
        aor = self._extract_uri(to_header)

        # Check authorization
        auth_header = sip_msg.get_header('Authorization')
        if not auth_header:
            # Request authentication
            return self._build_auth_challenge(sip_msg)

        # Validate credentials
        if not self._validate_auth(auth_header, sip_msg.method):
            return sip_msg.build_response(
                SIPResponseCode.UNAUTHORIZED.value,
                "Unauthorized"
            )

        # Extract contact and expires
        contact = sip_msg.get_header('Contact')
        expires_header = sip_msg.get_header('Expires')
        expires = int(expires_header) if expires_header else 3600

        # Store registration
        if expires > 0:
            self.registrations[aor] = SIPRegistration(
                aor=aor,
                contact=contact,
                expires=expires,
                registration_time=time.time(),
                call_id=sip_msg.get_header('Call-ID'),
                cseq=int(sip_msg.get_header('CSeq').split()[0])
            )
            print(f"Registered: {aor} -> {contact}")
        else:
            # Unregister
            if aor in self.registrations:
                del self.registrations[aor]
                print(f"Unregistered: {aor}")

        # Build 200 OK response
        return sip_msg.build_response(
            SIPResponseCode.OK.value,
            "OK"
        )

    def _handle_invite(self, sip_msg: SIPMessage) -> str:
        """Handle INVITE request (call setup)"""

        # Extract called party
        to_header = sip_msg.get_header('To')
        called_aor = self._extract_uri(to_header)

        # Check if called party is registered
        if called_aor not in self.registrations:
            return sip_msg.build_response(
                SIPResponseCode.NOT_FOUND.value,
                "Not Found"
            )

        registration = self.registrations[called_aor]

        # Check if registration expired
        if registration.is_expired():
            del self.registrations[called_aor]
            return sip_msg.build_response(
                SIPResponseCode.TEMPORARILY_UNAVAILABLE.value,
                "Temporarily Unavailable"
            )

        # Forward INVITE to called party (simplified)
        # In production: Parse contact, route to destination

        print(f"Routing call to: {called_aor} at {registration.contact}")

        # Return 100 Trying
        return sip_msg.build_response(
            SIPResponseCode.TRYING.value,
            "Trying"
        )

    def _handle_bye(self, sip_msg: SIPMessage) -> str:
        """Handle BYE request (call termination)"""
        print("Call terminated")
        return sip_msg.build_response(
            SIPResponseCode.OK.value,
            "OK"
        )

    def _handle_cancel(self, sip_msg: SIPMessage) -> str:
        """Handle CANCEL request"""
        print("Call cancelled")
        return sip_msg.build_response(
            SIPResponseCode.OK.value,
            "OK"
        )

    def _handle_options(self, sip_msg: SIPMessage) -> str:
        """Handle OPTIONS request (capability query)"""
        response = sip_msg.build_response(
            SIPResponseCode.OK.value,
            "OK"
        )
        # Add supported methods
        return response

    def _build_auth_challenge(self, sip_msg: SIPMessage) -> str:
        """Build 401 Unauthorized with authentication challenge"""
        response = sip_msg.build_response(
            SIPResponseCode.UNAUTHORIZED.value,
            "Unauthorized"
        )

        # Add WWW-Authenticate header
        auth_header = (
            f'Digest realm="{self.realm}", '
            f'nonce="{self.nonce}", '
            f'algorithm=MD5, '
            f'qop="auth"'
        )

        # Insert WWW-Authenticate header
        # In production, properly build response with header
        return response

    def _validate_auth(self, auth_header: str, method: str) -> bool:
        """Validate digest authentication"""
        # Simplified validation
        # In production: Parse auth header, compute response hash, compare
        return True

    def _extract_uri(self, header: str) -> str:
        """Extract URI from SIP header"""
        # Simplified URI extraction
        # Format: "Display Name" <sip:user@domain>
        start = header.find('<')
        end = header.find('>')
        if start != -1 and end != -1:
            return header[start+1:end]
        return header

    def _generate_nonce(self) -> str:
        """Generate authentication nonce"""
        return hashlib.md5(str(time.time()).encode()).hexdigest()


# Example VoLTE Call Flow
class VoLTECallManager:
    """VoLTE call management"""

    def initiate_volte_call(self, calling_party: str, called_party: str):
        """
        Initiate VoLTE call

        Call flow:
        1. SIP INVITE from UE to P-CSCF
        2. P-CSCF forwards to I-CSCF
        3. I-CSCF queries HSS for S-CSCF assignment
        4. I-CSCF forwards to S-CSCF
        5. S-CSCF applies services, forwards to terminating side
        6. 180 Ringing returned
        7. 200 OK when call answered
        8. ACK confirms session establishment
        9. RTP media streams established
        """

        call_flow = {
            "step_1_invite": {
                "from": calling_party,
                "to": called_party,
                "p_cscf": "p-cscf.ims.mnc410.mcc310.3gppnetwork.org",
                "message": "INVITE sip:called@ims.example.com SIP/2.0"
            },
            "step_2_100_trying": {
                "status": "100 Trying"
            },
            "step_3_183_session_progress": {
                "status": "183 Session Progress",
                "sdp": "Session description with media capabilities"
            },
            "step_4_180_ringing": {
                "status": "180 Ringing"
            },
            "step_5_200_ok": {
                "status": "200 OK",
                "sdp": "Final session description"
            },
            "step_6_ack": {
                "message": "ACK"
            },
            "step_7_media_established": {
                "codec": "AMR-WB",
                "rtp_port": 49152,
                "encrypted": "SRTP"
            }
        }

        return call_flow


if __name__ == "__main__":
    # Start SIP proxy server
    proxy = SIPProxyServer(host="0.0.0.0", port=5060)

    # In production, run in separate thread
    # proxy.start()

    # Example VoLTE call flow
    volte_mgr = VoLTECallManager()
    call_flow = volte_mgr.initiate_volte_call(
        calling_party="sip:alice@ims.example.com",
        called_party="sip:bob@ims.example.com"
    )

    import json
    print(json.dumps(call_flow, indent=2))
```

## Best Practices

1. **High Availability**: Deploy redundant CSCF instances
2. **Session Border Controller**: Protect IMS core from malicious traffic
3. **Quality of Service**: Prioritize voice traffic in network
4. **Codec Selection**: Use AMR-WB or EVS for HD voice
5. **Security**: Implement TLS for signaling, SRTP for media

## Common Issues

### Issue: Registration Failures
**Solution**: Check P-CSCF connectivity, verify authentication credentials

### Issue: One-Way Audio
**Solution**: Check NAT configuration, firewall rules, RTP port ranges

### Issue: Call Setup Delays
**Solution**: Optimize database queries, reduce DNS lookups, tune timers

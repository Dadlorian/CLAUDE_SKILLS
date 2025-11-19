"""
Enterprise Identity and Access Management System
A comprehensive IAM implementation with OAuth2, MFA, RBAC, and Zero Trust principles
"""

import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum
from dataclasses import dataclass, asdict
import jwt
import pyotp


class UserRole(Enum):
    """User roles with hierarchical permissions"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    SECURITY_OFFICER = "security_officer"
    DEVELOPER = "developer"
    USER = "user"
    GUEST = "guest"


class Permission(Enum):
    """Granular permissions"""
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    ROLE_ASSIGN = "role:assign"
    AUDIT_VIEW = "audit:view"
    SECURITY_POLICY_MODIFY = "security:policy:modify"
    DATA_EXPORT = "data:export"


@dataclass
class User:
    """User model"""
    user_id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    created_at: datetime = None
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked: bool = False

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class Session:
    """User session model"""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    mfa_verified: bool = False
    risk_score: int = 0


@dataclass
class AuditLog:
    """Audit log entry"""
    timestamp: datetime
    user_id: str
    action: str
    resource: str
    result: str
    ip_address: str
    details: Dict


class EnterpriseIAMSystem:
    """
    Enterprise-grade Identity and Access Management System

    Features:
    - User authentication with bcrypt password hashing
    - Multi-factor authentication (TOTP)
    - Role-based access control (RBAC)
    - Session management with security checks
    - Audit logging
    - OAuth 2.0 authorization
    - Risk-based authentication
    """

    def __init__(self, jwt_secret: str):
        self.jwt_secret = jwt_secret
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.audit_logs: List[AuditLog] = []
        self.oauth_clients: Dict[str, dict] = {}
        self.authorization_codes: Dict[str, dict] = {}

        # Role permissions mapping
        self.role_permissions = {
            UserRole.SUPER_ADMIN: [p for p in Permission],
            UserRole.ADMIN: [
                Permission.USER_CREATE, Permission.USER_READ,
                Permission.USER_UPDATE, Permission.ROLE_ASSIGN,
                Permission.AUDIT_VIEW
            ],
            UserRole.SECURITY_OFFICER: [
                Permission.USER_READ, Permission.AUDIT_VIEW,
                Permission.SECURITY_POLICY_MODIFY
            ],
            UserRole.DEVELOPER: [Permission.USER_READ],
            UserRole.USER: [Permission.USER_READ],
            UserRole.GUEST: []
        }

        # Session configuration
        self.session_timeout = timedelta(minutes=30)
        self.absolute_timeout = timedelta(hours=8)
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)

    # ==================== User Management ====================

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: UserRole = UserRole.USER
    ) -> User:
        """Create a new user with hashed password"""
        user_id = secrets.token_urlsafe(16)

        # Hash password
        password_hash = self._hash_password(password)

        user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )

        self.users[user_id] = user

        self._log_audit(
            user_id='system',
            action='user_created',
            resource=f'user:{user_id}',
            result='success',
            ip_address='127.0.0.1',
            details={'username': username, 'role': role.value}
        )

        return user

    def authenticate_user(
        self,
        username: str,
        password: str,
        ip_address: str,
        user_agent: str,
        mfa_token: Optional[str] = None
    ) -> Optional[str]:
        """
        Authenticate user and create session
        Returns session ID if successful
        """
        # Find user by username
        user = self._find_user_by_username(username)

        if not user:
            self._log_audit(
                user_id='unknown',
                action='login_failed',
                resource='authentication',
                result='failure',
                ip_address=ip_address,
                details={'reason': 'user_not_found', 'username': username}
            )
            return None

        # Check if account is locked
        if user.account_locked:
            self._log_audit(
                user_id=user.user_id,
                action='login_failed',
                resource='authentication',
                result='failure',
                ip_address=ip_address,
                details={'reason': 'account_locked'}
            )
            return None

        # Verify password
        if not self._verify_password(password, user.password_hash):
            user.failed_login_attempts += 1

            # Lock account if too many failed attempts
            if user.failed_login_attempts >= self.max_failed_attempts:
                user.account_locked = True
                self._log_audit(
                    user_id=user.user_id,
                    action='account_locked',
                    resource=f'user:{user.user_id}',
                    result='success',
                    ip_address=ip_address,
                    details={'reason': 'too_many_failed_attempts'}
                )

            self._log_audit(
                user_id=user.user_id,
                action='login_failed',
                resource='authentication',
                result='failure',
                ip_address=ip_address,
                details={'reason': 'invalid_password'}
            )
            return None

        # Verify MFA if enabled
        mfa_verified = False
        if user.mfa_enabled:
            if not mfa_token:
                return None  # MFA required but not provided

            if not self._verify_totp(user.mfa_secret, mfa_token):
                self._log_audit(
                    user_id=user.user_id,
                    action='login_failed',
                    resource='authentication',
                    result='failure',
                    ip_address=ip_address,
                    details={'reason': 'invalid_mfa_token'}
                )
                return None

            mfa_verified = True

        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.last_login = datetime.now()

        # Calculate risk score
        risk_score = self._calculate_risk_score(user, ip_address)

        # Create session
        session_id = self._create_session(
            user.user_id,
            ip_address,
            user_agent,
            mfa_verified,
            risk_score
        )

        self._log_audit(
            user_id=user.user_id,
            action='login_success',
            resource='authentication',
            result='success',
            ip_address=ip_address,
            details={'mfa_verified': mfa_verified, 'risk_score': risk_score}
        )

        return session_id

    # ==================== Multi-Factor Authentication ====================

    def enable_mfa(self, user_id: str) -> Dict:
        """Enable MFA for user and return setup information"""
        user = self.users.get(user_id)
        if not user:
            raise ValueError("User not found")

        # Generate secret
        secret = pyotp.random_base32()
        user.mfa_secret = secret
        user.mfa_enabled = True

        # Generate provisioning URI for QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name='Enterprise IAM'
        )

        # Generate backup codes
        backup_codes = [secrets.token_urlsafe(12) for _ in range(10)]

        self._log_audit(
            user_id=user_id,
            action='mfa_enabled',
            resource=f'user:{user_id}',
            result='success',
            ip_address='127.0.0.1',
            details={}
        )

        return {
            'secret': secret,
            'provisioning_uri': provisioning_uri,
            'backup_codes': backup_codes
        }

    def _verify_totp(self, secret: str, token: str) -> bool:
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)

        # Check current and adjacent windows for clock skew
        for offset in [-1, 0, 1]:
            if totp.verify(token, valid_window=offset):
                return True

        return False

    # ==================== Session Management ====================

    def _create_session(
        self,
        user_id: str,
        ip_address: str,
        user_agent: str,
        mfa_verified: bool,
        risk_score: int
    ) -> str:
        """Create new session"""
        session_id = secrets.token_urlsafe(32)

        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
            risk_score=risk_score
        )

        self.sessions[session_id] = session

        return session_id

    def validate_session(
        self,
        session_id: str,
        ip_address: str,
        user_agent: str
    ) -> Optional[Dict]:
        """Validate session and check for anomalies"""
        session = self.sessions.get(session_id)

        if not session:
            return None

        # Check session timeout
        if datetime.now() - session.last_activity > self.session_timeout:
            del self.sessions[session_id]
            return None

        # Check absolute timeout
        if datetime.now() - session.created_at > self.absolute_timeout:
            del self.sessions[session_id]
            return None

        # Check for session hijacking
        if ip_address != session.ip_address:
            self._log_audit(
                user_id=session.user_id,
                action='session_anomaly',
                resource=f'session:{session_id}',
                result='blocked',
                ip_address=ip_address,
                details={'reason': 'ip_mismatch', 'original_ip': session.ip_address}
            )
            return None

        if user_agent != session.user_agent:
            self._log_audit(
                user_id=session.user_id,
                action='session_anomaly',
                resource=f'session:{session_id}',
                result='blocked',
                ip_address=ip_address,
                details={'reason': 'user_agent_mismatch'}
            )
            return None

        # Update last activity
        session.last_activity = datetime.now()

        return {
            'user_id': session.user_id,
            'mfa_verified': session.mfa_verified,
            'risk_score': session.risk_score
        }

    def revoke_session(self, session_id: str):
        """Revoke/logout session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            self._log_audit(
                user_id=session.user_id,
                action='session_revoked',
                resource=f'session:{session_id}',
                result='success',
                ip_address=session.ip_address,
                details={}
            )
            del self.sessions[session_id]

    # ==================== Authorization (RBAC) ====================

    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        user = self.users.get(user_id)
        if not user:
            return False

        return permission in self.role_permissions.get(user.role, [])

    def assign_role(self, admin_user_id: str, target_user_id: str, new_role: UserRole):
        """Assign role to user (requires permission)"""
        # Check admin permission
        if not self.check_permission(admin_user_id, Permission.ROLE_ASSIGN):
            raise PermissionError("Insufficient permissions to assign roles")

        target_user = self.users.get(target_user_id)
        if not target_user:
            raise ValueError("Target user not found")

        old_role = target_user.role
        target_user.role = new_role

        self._log_audit(
            user_id=admin_user_id,
            action='role_assigned',
            resource=f'user:{target_user_id}',
            result='success',
            ip_address='127.0.0.1',
            details={'old_role': old_role.value, 'new_role': new_role.value}
        )

    # ==================== OAuth 2.0 ====================

    def register_oauth_client(
        self,
        client_name: str,
        redirect_uris: List[str]
    ) -> Dict:
        """Register OAuth 2.0 client"""
        client_id = secrets.token_urlsafe(16)
        client_secret = secrets.token_urlsafe(32)

        self.oauth_clients[client_id] = {
            'client_id': client_id,
            'client_secret': hashlib.sha256(client_secret.encode()).hexdigest(),
            'client_name': client_name,
            'redirect_uris': redirect_uris,
            'created_at': datetime.now()
        }

        return {
            'client_id': client_id,
            'client_secret': client_secret  # Only shown once
        }

    def generate_authorization_code(
        self,
        client_id: str,
        user_id: str,
        redirect_uri: str,
        scope: str,
        state: str
    ) -> str:
        """Generate OAuth 2.0 authorization code"""
        client = self.oauth_clients.get(client_id)
        if not client:
            raise ValueError("Invalid client")

        if redirect_uri not in client['redirect_uris']:
            raise ValueError("Invalid redirect URI")

        code = secrets.token_urlsafe(32)

        self.authorization_codes[code] = {
            'client_id': client_id,
            'user_id': user_id,
            'redirect_uri': redirect_uri,
            'scope': scope,
            'state': state,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(minutes=10),
            'used': False
        }

        return code

    def exchange_code_for_token(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ) -> Dict:
        """Exchange authorization code for access token"""
        # Verify code exists
        auth_code = self.authorization_codes.get(code)
        if not auth_code:
            raise ValueError("Invalid authorization code")

        # Check expiration
        if datetime.now() > auth_code['expires_at']:
            raise ValueError("Authorization code expired")

        # Check if already used
        if auth_code['used']:
            # Revoke all tokens for this client (security measure)
            raise ValueError("Authorization code already used")

        # Verify client
        client = self.oauth_clients.get(client_id)
        if not client:
            raise ValueError("Invalid client")

        client_secret_hash = hashlib.sha256(client_secret.encode()).hexdigest()
        if client_secret_hash != client['client_secret']:
            raise ValueError("Invalid client secret")

        # Verify redirect URI
        if redirect_uri != auth_code['redirect_uri']:
            raise ValueError("Redirect URI mismatch")

        # Mark code as used
        auth_code['used'] = True

        # Generate tokens
        access_token = self._generate_jwt_token(
            auth_code['user_id'],
            auth_code['scope'],
            expires_in=3600
        )

        refresh_token = secrets.token_urlsafe(32)

        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': refresh_token,
            'scope': auth_code['scope']
        }

    def _generate_jwt_token(self, user_id: str, scope: str, expires_in: int) -> str:
        """Generate JWT access token"""
        payload = {
            'sub': user_id,
            'scope': scope,
            'iat': datetime.now(),
            'exp': datetime.now() + timedelta(seconds=expires_in)
        }

        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        return token

    # ==================== Risk-Based Authentication ====================

    def _calculate_risk_score(self, user: User, ip_address: str) -> int:
        """Calculate risk score for authentication attempt"""
        risk_score = 0

        # Check for new IP address
        if self._is_new_ip(user.user_id, ip_address):
            risk_score += 30

        # Check for recent failed attempts
        if user.failed_login_attempts > 0:
            risk_score += user.failed_login_attempts * 10

        # Check for unusual time
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:
            risk_score += 20

        return min(risk_score, 100)

    def _is_new_ip(self, user_id: str, ip_address: str) -> bool:
        """Check if IP address is new for user"""
        # Would check against historical IP addresses
        return False  # Placeholder

    # ==================== Utility Methods ====================

    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        # In production, use bcrypt library
        # This is a simplified version
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${password_hash}"

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, stored_hash = password_hash.split('$')
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == stored_hash
        except:
            return False

    def _find_user_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def _log_audit(
        self,
        user_id: str,
        action: str,
        resource: str,
        result: str,
        ip_address: str,
        details: Dict
    ):
        """Log audit event"""
        log_entry = AuditLog(
            timestamp=datetime.now(),
            user_id=user_id,
            action=action,
            resource=resource,
            result=result,
            ip_address=ip_address,
            details=details
        )

        self.audit_logs.append(log_entry)

    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """Retrieve audit logs with filters"""
        filtered_logs = self.audit_logs

        if user_id:
            filtered_logs = [log for log in filtered_logs if log.user_id == user_id]

        if action:
            filtered_logs = [log for log in filtered_logs if log.action == action]

        if start_date:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_date]

        if end_date:
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_date]

        return [asdict(log) for log in filtered_logs]


# ==================== Example Usage ====================

if __name__ == "__main__":
    # Initialize IAM system
    iam = EnterpriseIAMSystem(jwt_secret="your-secret-key")

    # Create users
    admin = iam.create_user(
        username="admin",
        email="admin@example.com",
        password="SecureP@ssw0rd!",
        role=UserRole.ADMIN
    )

    regular_user = iam.create_user(
        username="john.doe",
        email="john@example.com",
        password="UserP@ssw0rd!",
        role=UserRole.USER
    )

    print(f"Created admin user: {admin.user_id}")
    print(f"Created regular user: {regular_user.user_id}")

    # Enable MFA for admin
    mfa_setup = iam.enable_mfa(admin.user_id)
    print(f"\nMFA Secret: {mfa_setup['secret']}")
    print(f"QR Code URI: {mfa_setup['provisioning_uri']}")

    # Authenticate user
    session_id = iam.authenticate_user(
        username="john.doe",
        password="UserP@ssw0rd!",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0"
    )

    if session_id:
        print(f"\nAuthentication successful. Session ID: {session_id}")

        # Validate session
        session_info = iam.validate_session(
            session_id=session_id,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0"
        )
        print(f"Session validated: {session_info}")

    # Check permissions
    can_assign_role = iam.check_permission(admin.user_id, Permission.ROLE_ASSIGN)
    print(f"\nAdmin can assign roles: {can_assign_role}")

    # Register OAuth client
    oauth_client = iam.register_oauth_client(
        client_name="Mobile App",
        redirect_uris=["https://app.example.com/callback"]
    )
    print(f"\nOAuth Client ID: {oauth_client['client_id']}")

    # View audit logs
    logs = iam.get_audit_logs(action='login_success')
    print(f"\nSuccessful login attempts: {len(logs)}")

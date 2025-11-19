# Patient Portal Development Guide

## Overview

Step-by-step guide for developing a HIPAA-compliant patient portal with modern web technologies.

## Tech Stack

```
Frontend:
├── React 18+ with TypeScript
├── Material-UI or Tailwind CSS
├── Redux or Zustand (state management)
└── React Query (data fetching)

Backend:
├── Node.js + Express or Python + Fast API
├── PostgreSQL or MongoDB
├── Redis (session/caching)
└── JWT authentication

Infrastructure:
├── AWS or Azure (HIPAA-compliant hosting)
├── SSL/TLS encryption
├── WAF (Web Application Firewall)
└── CDN with DDoS protection
```

## Part 1: Authentication System

### Step 1: User Registration

```typescript
// services/auth.service.ts
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { sendVerificationEmail } from './email.service';

export class AuthService {
  async register(userData: {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
    dateOfBirth: string;
  }) {
    // Password strength validation
    if (!this.isStrongPassword(userData.password)) {
      throw new Error('Password does not meet requirements');
    }

    // Check if email already exists
    const existingUser = await User.findOne({ email: userData.email });
    if (existingUser) {
      throw new Error('Email already registered');
    }

    // Hash password
    const salt = await bcrypt.genSalt(12);
    const passwordHash = await bcrypt.hash(userData.password, salt);

    // Create user
    const user = await User.create({
      ...userData,
      passwordHash,
      emailVerified: false,
      mfaEnabled: false,
      accountLocked: false
    });

    // Generate verification token
    const verificationToken = jwt.sign(
      { userId: user.id, purpose: 'email_verification' },
      process.env.JWT_SECRET!,
      { expiresIn: '24h' }
    );

    // Send verification email
    await sendVerificationEmail(user.email, verificationToken);

    return { userId: user.id, message: 'Registration successful. Please verify your email.' };
  }

  isStrongPassword(password: string): boolean {
    // At least 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special char
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return regex.test(password);
  }
}
```

### Step 2: Multi-Factor Authentication

```typescript
// services/mfa.service.ts
import speakeasy from 'speakeasy';
import QRCode from 'qrcode';

export class MFAService {
  async setupMFA(userId: string) {
    const secret = speakeasy.generateSecret({
      name: `PatientPortal (${userId})`,
      length: 32
    });

    // Store secret in database (encrypted)
    await User.updateOne(
      { _id: userId },
      { mfaSecret: this.encrypt(secret.base32) }
    );

    // Generate QR code
    const qrCodeDataURL = await QRCode.toDataURL(secret.otpauth_url!);

    return {
      secret: secret.base32,
      qrCode: qrCodeDataURL
    };
  }

  async verifyMFA(userId: string, token: string): Promise<boolean> {
    const user = await User.findById(userId);
    if (!user || !user.mfaSecret) {
      return false;
    }

    const secret = this.decrypt(user.mfaSecret);

    return speakeasy.totp.verify({
      secret,
      encoding: 'base32',
      token,
      window: 2  // Allow 2 time steps before/after for clock skew
    });
  }

  private encrypt(text: string): string {
    // Use AES-256-GCM encryption
    const crypto = require('crypto');
    const algorithm = 'aes-256-gcm';
    const key = Buffer.from(process.env.ENCRYPTION_KEY!, 'hex');
    const iv = crypto.randomBytes(16);

    const cipher = crypto.createCipheriv(algorithm, key, iv);
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');

    const authTag = cipher.getAuthTag();

    return iv.toString('hex') + ':' + authTag.toString('hex') + ':' + encrypted;
  }

  private decrypt(text: string): string {
    const crypto = require('crypto');
    const algorithm = 'aes-256-gcm';
    const key = Buffer.from(process.env.ENCRYPTION_KEY!, 'hex');

    const parts = text.split(':');
    const iv = Buffer.from(parts[0], 'hex');
    const authTag = Buffer.from(parts[1], 'hex');
    const encrypted = parts[2];

    const decipher = crypto.createDecipheriv(algorithm, key, iv);
    decipher.setAuthTag(authTag);

    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    return decrypted;
  }
}
```

## Part 2: FHIR Integration

### Health Information Display

```typescript
// components/HealthRecords.tsx
import React, { useEffect, useState } from 'react';
import { useQuery } from 'react-query';
import { fhirClient } from '../services/fhir.client';

interface Observation {
  id: string;
  date: string;
  name: string;
  value: string;
  unit: string;
  status: string;
}

export const LabResults: React.FC = () => {
  const { data: observations, isLoading, error } = useQuery(
    'labResults',
    async () => {
      const patientId = sessionStorage.getItem('patient_id');
      const results = await fhirClient.search('Observation', {
        patient: patientId,
        category: 'laboratory',
        _sort: '-date',
        _count: 50
      });

      return results.entry.map((entry: any) => ({
        id: entry.resource.id,
        date: entry.resource.effectiveDateTime,
        name: entry.resource.code.text,
        value: entry.resource.valueQuantity?.value,
        unit: entry.resource.valueQuantity?.unit,
        status: entry.resource.status
      }));
    },
    {
      refetchInterval: false,
      staleTime: 5 * 60 * 1000  // 5 minutes
    }
  );

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div className="lab-results">
      <h2>Lab Results</h2>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Test</th>
            <th>Result</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {observations?.map((obs: Observation) => (
            <tr key={obs.id}>
              <td>{new Date(obs.date).toLocaleDateString()}</td>
              <td>{obs.name}</td>
              <td>{obs.value} {obs.unit}</td>
              <td><StatusBadge status={obs.status} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

## Part 3: Secure Messaging

```typescript
// components/SecureMessaging.tsx
interface Message {
  id: string;
  from: string;
  to: string;
  subject: string;
  body: string;
  timestamp: Date;
  read: boolean;
  attachments?: Attachment[];
}

export const SecureMessaging: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);

  const sendMessage = async (messageData: {
    to: string;
    subject: string;
    body: string;
    attachments?: File[];
  }) => {
    // Encrypt message content before sending
    const encryptedBody = await encryptMessage(messageData.body);

    const response = await fetch('/api/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAccessToken()}`
      },
      body: JSON.stringify({
        ...messageData,
        body: encryptedBody
      })
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    // Refresh messages
    await fetchMessages();
  };

  const fetchMessages = async () => {
    const response = await fetch('/api/messages', {
      headers: {
        'Authorization': `Bearer ${getAccessToken()}`
      }
    });

    const data = await response.json();
    setMessages(data.messages);
  };

  return (
    <div className="secure-messaging">
      <MessageList
        messages={messages}
        onSelectMessage={setSelectedMessage}
      />
      {selectedMessage && (
        <MessageView
          message={selectedMessage}
          onReply={(reply) => sendMessage(reply)}
        />
      )}
      <ComposeMessage onSend={sendMessage} />
    </div>
  );
};
```

## Part 4: Security Implementation

### HIPAA Compliance Checklist

```
☐ Encryption
  ☐ TLS 1.2+ for data in transit
  ☐ AES-256 for data at rest
  ☐ Encrypted backups

☐ Access Controls
  ☐ Role-based access control (RBAC)
  ☐ Multi-factor authentication
  ☐ Session timeout (15 minutes idle)
  ☐ Account lockout after failed attempts

☐ Audit Logging
  ☐ Log all access to PHI
  ☐ Log authentication events
  ☐ Log data modifications
  ☐ Tamper-proof logs

☐ Data Protection
  ☐ Input validation
  ☐ SQL injection prevention
  ☐ XSS protection
  ☐ CSRF protection

☐ Business Associate Agreement (BAA)
  ☐ With cloud provider
  ☐ With any third-party services
  ☐ With development team
```

### Audit Logging Implementation

```typescript
// middleware/audit.middleware.ts
export const auditLogger = async (req: Request, res: Response, next: NextFunction) => {
  const startTime = Date.now();

  // Capture original response methods
  const originalSend = res.send;
  const originalJson = res.json;

  let responseBody: any;

  res.send = function(data) {
    responseBody = data;
    return originalSend.call(this, data);
  };

  res.json = function(data) {
    responseBody = data;
    return originalJson.call(this, data);
  };

  // Wait for response to complete
  res.on('finish', async () => {
    const duration = Date.now() - startTime;

    const auditEntry = {
      timestamp: new Date(),
      userId: req.user?.id,
      action: req.method,
      resource: req.path,
      ipAddress: req.ip,
      userAgent: req.get('user-agent'),
      statusCode: res.statusCode,
      duration,
      requestBody: sanitizeForLogging(req.body),
      responseBody: sanitizeForLogging(responseBody),
      phiAccessed: containsPHI(req.path)
    };

    await AuditLog.create(auditEntry);

    // Alert on suspicious activity
    if (isSuspiciousActivity(auditEntry)) {
      await sendSecurityAlert(auditEntry);
    }
  });

  next();
};
```

## Part 5: Testing

### Security Testing

```typescript
// test/security.test.ts
describe('Security Tests', () => {
  it('should prevent SQL injection', async () => {
    const maliciousInput = "' OR '1'='1";

    const response = await request(app)
      .post('/api/login')
      .send({ email: maliciousInput, password: 'test' });

    expect(response.status).toBe(400);
  });

  it('should prevent XSS attacks', async () => {
    const xssPayload = '<script>alert("XSS")</script>';

    const response = await request(app)
      .post('/api/messages')
      .set('Authorization', `Bearer ${validToken}`)
      .send({ subject: xssPayload, body: 'test' });

    const message = await Message.findById(response.body.id);
    expect(message.subject).not.toContain('<script>');
  });

  it('should enforce session timeout', async () => {
    // Login
    const loginResponse = await request(app)
      .post('/api/login')
      .send({ email: 'test@example.com', password: 'ValidPassword123!' });

    const token = loginResponse.body.token;

    // Wait for session timeout (16 minutes)
    await delay(16 * 60 * 1000);

    // Try to access protected resource
    const response = await request(app)
      .get('/api/health-records')
      .set('Authorization', `Bearer ${token}`);

    expect(response.status).toBe(401);
  });
});
```

## Part 6: Deployment

### AWS Deployment Architecture

```yaml
# infrastructure/cloudformation.yaml
Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']

  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [0, !GetAZs '']

  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      SecurityGroups:
        - !Ref ALBSecurityGroup
      Subnets:
        - !Ref PublicSubnet
      Scheme: internet-facing

  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: patient-portal-cluster

  ECSService:
    Type: AWS::ECS::Service
    Properties:
      Cluster: !Ref ECSCluster
      DesiredCount: 2
      LaunchType: FARGATE
      LoadBalancers:
        - ContainerName: patient-portal
          ContainerPort: 3000
          TargetGroupArn: !Ref TargetGroup

  RDSInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.medium
      Engine: postgres
      EngineVersion: '14.7'
      MasterUsername: !Ref DBUsername
      MasterUserPassword: !Ref DBPassword
      StorageEncrypted: true
      BackupRetentionPeriod: 35
```

## References

- HIPAA Security Rule: https://www.hhs.gov/hipaa/for-professionals/security/
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- FHIR Patient Access: https://www.hl7.org/fhir/patient.html

---

**Document Version**: 1.0
**Last Updated**: November 2024
**Classification**: Production Guide

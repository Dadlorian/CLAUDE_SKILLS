# Zoom for Healthcare Integration Guide

## Overview
Step-by-step guide to integrating Zoom for Healthcare into your telehealth platform, including setup, configuration, security hardening, EHR integration, and operational deployment.

---

## Prerequisites

### Account Requirements
- Zoom Healthcare account (not regular Zoom Pro)
- Business Associate Agreement (BAA) signed with Zoom
- Administrative access to Zoom account
- Domain ownership verification

### Technical Requirements
- HTTPS-enabled web application
- Server-side application (Node.js, Python, Java, etc.)
- Database for storing meeting metadata
- SSL/TLS certificates

### Developer Access
- Zoom Developer Account
- API credentials (API Key, API Secret)
- OAuth app credentials (for user authentication)
- Webhook endpoint (for event notifications)

---

## Step 1: Zoom Healthcare Account Setup

### 1.1 Sign Up for Zoom Healthcare

**Process**:
1. Visit https://zoom.us/healthcare
2. Click "Sign Up" or contact sales for enterprise
3. Provide organization information
4. Select Healthcare plan tier
5. Complete payment setup

**Pricing Tiers** (approximate):
- Healthcare Starter: $200/month per license (minimum 10 licenses)
- Healthcare Plus: Custom pricing
- Healthcare Enterprise: Custom pricing

---

### 1.2 Execute Business Associate Agreement (BAA)

**Steps**:
1. Log in to Zoom account as admin
2. Navigate to Account Management > Account Settings
3. Click "Security" tab
4. Find "Business Associate Agreement (BAA)" section
5. Click "Enable" and review terms
6. Sign BAA electronically
7. Download signed copy for records

**Verification**:
- BAA status shows "Enabled" in account settings
- Confirmation email received
- Copy of signed BAA in compliance files

---

### 1.3 Configure Account Security Settings

**Required Settings**:

```
Account Settings > Security

☑ Require a password when scheduling new meetings
☑ Require password for meetings that have already started
☑ Embed password in meeting link for one-click join
☑ Require password for Personal Meeting ID (PMI)
☑ Enable Waiting Room for all meetings
☑ Disable "Join before host"
☑ Only authenticated users can join meetings
☐ Allow removed participants to rejoin (DISABLE for healthcare)
☑ Encrypt 3rd party endpoints (H.323/SIP)
☑ Enable encryption for in-meeting file transfer
☐ Allow screen sharing for host only (ENABLE)
☐ Disable file transfer during meetings (RECOMMENDED)
☐ Disable private chat (OPTIONAL - disable for security)
☑ Enable waiting room for meetings already started
☑ Disable feedback - Do not send feedback to Zoom
```

**Account Settings > Recording**:
```
☑ Enable cloud recording
☑ Encrypt cloud recordings
☐ Store recordings locally (DISABLE - use cloud only)
☑ Require password to access cloud recordings
☑ Allow only account owner/admin to access all cloud recordings
☑ Auto-delete cloud recordings after [90 days]
```

**Account Settings > In Meeting (Advanced)**:
```
☐ Annotation (DISABLE for security)
☐ Whiteboard (DISABLE to prevent PHI sharing)
☐ Remote control (DISABLE)
☑ Breakout rooms (if needed for group therapy)
☐ Virtual background (ENABLE if desired)
☐ Allow users to select stereo audio (OPTIONAL)
```

---

## Step 2: Zoom API Setup

### 2.1 Create Server-to-Server OAuth App

**Steps**:
1. Go to https://marketplace.zoom.us/
2. Click "Develop" > "Build App"
3. Select "Server-to-Server OAuth"
4. Click "Create"
5. Enter app information:
   - App Name: "Telehealth Platform Integration"
   - Short Description: "Integration for telehealth video visits"
   - Company Name: [Your organization]
6. Click "Continue"

**App Credentials**:
- Account ID: `abc123...`
- Client ID: `xyz789...`
- Client Secret: `secret123...` (keep secure!)

**Scopes Required**:
- `meeting:write:admin` - Create meetings
- `meeting:read:admin` - Get meeting details
- `meeting:update:admin` - Update meeting settings
- `meeting:delete:admin` - Delete meetings
- `user:read:admin` - Read user information
- `recording:read:admin` - Access recordings
- `webinar:write:admin` - Create webinars (if using webinars)

**Activation**:
1. Add required scopes
2. Click "Continue"
3. Click "Activate your app"
4. Copy Account ID, Client ID, Client Secret to secure storage (environment variables)

---

### 2.2 Generate Access Token

**Node.js Example**:
```javascript
const axios = require('axios');

async function getZoomAccessToken() {
  const accountId = process.env.ZOOM_ACCOUNT_ID;
  const clientId = process.env.ZOOM_CLIENT_ID;
  const clientSecret = process.env.ZOOM_CLIENT_SECRET;

  const credentials = Buffer.from(`${clientId}:${clientSecret}`).toString('base64');

  try {
    const response = await axios.post(
      `https://zoom.us/oauth/token?grant_type=account_credentials&account_id=${accountId}`,
      {},
      {
        headers: {
          'Authorization': `Basic ${credentials}`,
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    );

    return response.data.access_token;
  } catch (error) {
    console.error('Error getting Zoom access token:', error.response.data);
    throw error;
  }
}

module.exports = { getZoomAccessToken };
```

**Python Example**:
```python
import os
import base64
import requests

def get_zoom_access_token():
    account_id = os.getenv('ZOOM_ACCOUNT_ID')
    client_id = os.getenv('ZOOM_CLIENT_ID')
    client_secret = os.getenv('ZOOM_CLIENT_SECRET')

    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={account_id}"

    headers = {
        'Authorization': f'Basic {credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(url, headers=headers)
    response.raise_for_status()

    return response.json()['access_token']
```

---

## Step 3: Create Meetings Programmatically

### 3.1 Create a Scheduled Meeting

**API Endpoint**: `POST https://api.zoom.us/v2/users/{userId}/meetings`

**Node.js Implementation**:
```javascript
const axios = require('axios');
const { getZoomAccessToken } = require('./zoomAuth');

async function createZoomMeeting(providerEmail, patientName, scheduledTime) {
  const accessToken = await getZoomAccessToken();

  const meetingData = {
    topic: `Telehealth Visit - ${patientName}`,
    type: 2, // Scheduled meeting
    start_time: scheduledTime, // ISO 8601 format: 2025-01-15T10:00:00Z
    duration: 30, // minutes
    timezone: 'America/New_York',
    agenda: 'Telehealth appointment',
    settings: {
      host_video: true,
      participant_video: true,
      join_before_host: false, // Must be false for security
      mute_upon_entry: true,
      watermark: true, // Show watermark to prevent screenshots
      use_pmi: false,
      approval_type: 0, // Automatically approve
      registration_type: 1, // Registrants register once, can attend only one occurrence
      audio: 'both',
      auto_recording: 'cloud', // Automatically record to cloud
      alternative_hosts: '',
      waiting_room: true, // REQUIRED for HIPAA
      meeting_authentication: true, // Require authentication
      authentication_domains: 'yourdomain.com',
      encryption_type: 'enhanced_encryption', // Use enhanced encryption
      approved_or_denied_countries_or_regions: {
        enable: true,
        method: 'approve',
        approved_list: ['US', 'CA'] // Restrict to certain countries if needed
      }
    }
  };

  try {
    const response = await axios.post(
      `https://api.zoom.us/v2/users/${providerEmail}/meetings`,
      meetingData,
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      }
    );

    return {
      meetingId: response.data.id,
      joinUrl: response.data.join_url,
      startUrl: response.data.start_url,
      password: response.data.password
    };
  } catch (error) {
    console.error('Error creating Zoom meeting:', error.response.data);
    throw error;
  }
}

module.exports = { createZoomMeeting };
```

**Response Example**:
```json
{
  "meetingId": 123456789,
  "joinUrl": "https://zoom.us/j/123456789?pwd=abc123",
  "startUrl": "https://zoom.us/s/123456789?zak=xyz789",
  "password": "abc123"
}
```

---

### 3.2 Store Meeting Data

**Database Schema** (PostgreSQL):
```sql
CREATE TABLE telehealth_meetings (
  id SERIAL PRIMARY KEY,
  patient_id INTEGER REFERENCES patients(id),
  provider_id INTEGER REFERENCES providers(id),
  zoom_meeting_id BIGINT UNIQUE NOT NULL,
  zoom_join_url TEXT NOT NULL,
  zoom_start_url TEXT NOT NULL,
  zoom_password VARCHAR(50),
  scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
  duration_minutes INTEGER,
  status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, in_progress, completed, cancelled
  recording_url TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_telehealth_meetings_patient ON telehealth_meetings(patient_id);
CREATE INDEX idx_telehealth_meetings_provider ON telehealth_meetings(provider_id);
CREATE INDEX idx_telehealth_meetings_scheduled_time ON telehealth_meetings(scheduled_time);
```

**Insert Meeting**:
```javascript
async function storeMeetingData(patientId, providerId, zoomMeetingData, scheduledTime) {
  const query = `
    INSERT INTO telehealth_meetings
    (patient_id, provider_id, zoom_meeting_id, zoom_join_url, zoom_start_url, zoom_password, scheduled_time, duration_minutes)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    RETURNING id
  `;

  const values = [
    patientId,
    providerId,
    zoomMeetingData.meetingId,
    zoomMeetingData.joinUrl,
    zoomMeetingData.startUrl,
    zoomMeetingData.password,
    scheduledTime,
    30 // default duration
  ];

  const result = await db.query(query, values);
  return result.rows[0].id;
}
```

---

## Step 4: Implement Virtual Waiting Room

### 4.1 Enable Waiting Room Features

**Zoom Settings**:
- Waiting Room must be enabled (required for HIPAA)
- Customize waiting room message
- Automatic admission settings

**Custom Waiting Room Message**:
```
Account Settings > Meeting > In Meeting (Advanced) > Waiting Room

Customize waiting room logo: [Upload your logo]

Waiting room message:
"Welcome to [Organization Name] Telehealth. Dr. [Provider Name] will admit you to the visit shortly. Please ensure you are in a private location and your audio and video are working properly."
```

---

### 4.2 Programmatic Waiting Room Management

**Get Waiting Room Participants**:
```javascript
async function getWaitingRoomParticipants(meetingId) {
  const accessToken = await getZoomAccessToken();

  try {
    const response = await axios.get(
      `https://api.zoom.us/v2/meetings/${meetingId}/participants`,
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        },
        params: {
          type: 'waiting_room'
        }
      }
    );

    return response.data.participants;
  } catch (error) {
    console.error('Error getting waiting room participants:', error.response.data);
    return [];
  }
}
```

**Note**: Zoom API does not currently support programmatic admission from waiting room. Provider must manually admit via Zoom client.

---

## Step 5: Webhooks for Real-Time Events

### 5.1 Create Webhook Endpoint

**Express.js Example**:
```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();

app.use(express.json());

// Webhook signature verification
function verifyWebhookSignature(req) {
  const message = `v0:${req.headers['x-zm-request-timestamp']}:${JSON.stringify(req.body)}`;
  const hashForVerify = crypto
    .createHmac('sha256', process.env.ZOOM_WEBHOOK_SECRET_TOKEN)
    .update(message)
    .digest('hex');
  const signature = `v0=${hashForVerify}`;
  return signature === req.headers['x-zm-signature'];
}

app.post('/webhooks/zoom', async (req, res) => {
  // Verify webhook signature
  if (!verifyWebhookSignature(req)) {
    return res.status(401).send('Invalid signature');
  }

  const event = req.body.event;
  const payload = req.body.payload;

  console.log('Zoom webhook received:', event);

  switch (event) {
    case 'meeting.started':
      await handleMeetingStarted(payload);
      break;
    case 'meeting.ended':
      await handleMeetingEnded(payload);
      break;
    case 'meeting.participant_joined':
      await handleParticipantJoined(payload);
      break;
    case 'meeting.participant_left':
      await handleParticipantLeft(payload);
      break;
    case 'recording.completed':
      await handleRecordingCompleted(payload);
      break;
    default:
      console.log('Unhandled event:', event);
  }

  res.status(200).send('OK');
});

async function handleMeetingStarted(payload) {
  const meetingId = payload.object.id;
  await db.query(
    'UPDATE telehealth_meetings SET status = $1, updated_at = NOW() WHERE zoom_meeting_id = $2',
    ['in_progress', meetingId]
  );
  console.log(`Meeting ${meetingId} started`);
}

async function handleMeetingEnded(payload) {
  const meetingId = payload.object.id;
  const duration = payload.object.duration;
  await db.query(
    'UPDATE telehealth_meetings SET status = $1, duration_minutes = $2, updated_at = NOW() WHERE zoom_meeting_id = $3',
    ['completed', duration, meetingId]
  );
  console.log(`Meeting ${meetingId} ended. Duration: ${duration} minutes`);
}

async function handleRecordingCompleted(payload) {
  const meetingId = payload.object.id;
  const recordingFiles = payload.object.recording_files;

  for (const file of recordingFiles) {
    if (file.file_type === 'MP4') {
      await db.query(
        'UPDATE telehealth_meetings SET recording_url = $1, updated_at = NOW() WHERE zoom_meeting_id = $2',
        [file.download_url, meetingId]
      );
      console.log(`Recording available for meeting ${meetingId}: ${file.download_url}`);
    }
  }
}

app.listen(3000, () => console.log('Webhook server listening on port 3000'));
```

---

### 5.2 Configure Webhooks in Zoom

**Steps**:
1. Go to Zoom Marketplace: https://marketplace.zoom.us/
2. Click "Develop" > "Build App"
3. Select existing Server-to-Server OAuth app
4. Click "Feature" tab
5. Click "Event Subscriptions"
6. Toggle "Enable Event Subscriptions" to ON
7. Enter Endpoint URL: `https://yourdomain.com/webhooks/zoom`
8. Zoom will send verification request - respond with challenge
9. Add event types:
   - Meeting: meeting.started, meeting.ended, meeting.participant_joined, meeting.participant_left
   - Recording: recording.completed, recording.transcript_completed
10. Save

**Verification Endpoint** (for initial setup):
```javascript
app.post('/webhooks/zoom', (req, res) => {
  // Zoom sends a challenge on first setup
  if (req.body.event === 'endpoint.url_validation') {
    const challengeToken = crypto
      .createHmac('sha256', process.env.ZOOM_WEBHOOK_SECRET_TOKEN)
      .update(req.body.payload.plainToken)
      .digest('hex');

    return res.status(200).json({
      plainToken: req.body.payload.plainToken,
      encryptedToken: challengeToken
    });
  }

  // Handle other events...
});
```

---

## Step 6: Download and Manage Recordings

### 6.1 List Cloud Recordings

**API Call**:
```javascript
async function getCloudRecordings(userId, from, to) {
  const accessToken = await getZoomAccessToken();

  try {
    const response = await axios.get(
      `https://api.zoom.us/v2/users/${userId}/recordings`,
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        },
        params: {
          from: from, // YYYY-MM-DD
          to: to      // YYYY-MM-DD
        }
      }
    );

    return response.data.meetings;
  } catch (error) {
    console.error('Error getting recordings:', error.response.data);
    throw error;
  }
}
```

---

### 6.2 Download Recording

**Download with Access Token**:
```javascript
const fs = require('fs');
const axios = require('axios');

async function downloadRecording(downloadUrl, savePath) {
  const accessToken = await getZoomAccessToken();

  const response = await axios({
    method: 'GET',
    url: downloadUrl,
    responseType: 'stream',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });

  const writer = fs.createWriteStream(savePath);
  response.data.pipe(writer);

  return new Promise((resolve, reject) => {
    writer.on('finish', resolve);
    writer.on('error', reject);
  });
}
```

**Encrypt and Store Securely**:
```javascript
const crypto = require('crypto');
const AWS = require('aws-sdk');
const s3 = new AWS.S3();

async function downloadAndStoreRecording(meetingId, downloadUrl) {
  const tempPath = `/tmp/recording-${meetingId}.mp4`;

  // Download recording
  await downloadRecording(downloadUrl, tempPath);

  // Encrypt and upload to S3
  const fileBuffer = fs.readFileSync(tempPath);

  const params = {
    Bucket: process.env.S3_BUCKET_NAME,
    Key: `recordings/${meetingId}.mp4`,
    Body: fileBuffer,
    ServerSideEncryption: 'AES256', // Encrypt at rest
    Metadata: {
      'meeting-id': meetingId.toString()
    }
  };

  await s3.upload(params).promise();

  // Delete temp file
  fs.unlinkSync(tempPath);

  console.log(`Recording for meeting ${meetingId} stored securely`);
}
```

---

## Step 7: Patient and Provider User Flows

### 7.1 Provider Workflow

**1. Provider logs into telehealth platform**
**2. Views today's schedule with Zoom links**:
```javascript
async function getProviderSchedule(providerId, date) {
  const query = `
    SELECT
      tm.id,
      tm.scheduled_time,
      tm.duration_minutes,
      tm.zoom_start_url,
      tm.status,
      p.first_name || ' ' || p.last_name AS patient_name,
      p.dob
    FROM telehealth_meetings tm
    JOIN patients p ON tm.patient_id = p.id
    WHERE tm.provider_id = $1
      AND DATE(tm.scheduled_time) = $2
      AND tm.status != 'cancelled'
    ORDER BY tm.scheduled_time ASC
  `;

  const result = await db.query(query, [providerId, date]);
  return result.rows;
}
```

**3. Clicks "Start Visit" button (opens Zoom with start_url)**
**4. Admits patient from waiting room**
**5. Conducts visit**
**6. Ends meeting**
**7. Completes clinical documentation**

---

### 7.2 Patient Workflow

**1. Receives appointment confirmation email with visit link**:
```javascript
const nodemailer = require('nodemailer');

async function sendAppointmentConfirmation(patientEmail, patientName, providerName, scheduledTime, joinUrl) {
  const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: 587,
    secure: false,
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS
    }
  });

  const emailBody = `
    Dear ${patientName},

    Your telehealth appointment with ${providerName} is confirmed for:
    ${new Date(scheduledTime).toLocaleString('en-US', { dateStyle: 'full', timeStyle: 'short' })}

    To join your visit, click the link below at your scheduled appointment time:
    ${joinUrl}

    Please join from a quiet, private location and ensure your camera and microphone are working.

    If you need to reschedule, please contact us at least 24 hours in advance.

    Thank you,
    [Organization Name]
  `;

  await transporter.sendMail({
    from: '"Telehealth Services" <noreply@yourdomain.com>',
    to: patientEmail,
    subject: `Telehealth Appointment Confirmation - ${providerName}`,
    text: emailBody
  });
}
```

**2. Clicks join link 5 minutes before appointment**
**3. Enters waiting room (automated via Zoom)**
**4. Provider admits patient**
**5. Telehealth visit occurs**
**6. Receives after-visit summary**

---

## Step 8: Testing

### 8.1 Test Checklist

- [ ] Create test meeting via API
- [ ] Verify waiting room is enabled
- [ ] Test patient join flow (waiting room → admission)
- [ ] Test provider start flow
- [ ] Verify meeting settings (security, encryption)
- [ ] Test recording (if enabled)
- [ ] Test webhook events (meeting.started, meeting.ended)
- [ ] Test meeting cancellation/deletion
- [ ] Verify access token refresh
- [ ] Load testing (multiple concurrent meetings)

---

## Step 9: Go-Live

### 9.1 Pre-Launch Checklist

- [ ] BAA signed and verified
- [ ] Security settings hardened
- [ ] Webhooks configured and tested
- [ ] Provider training completed
- [ ] Patient instructions created
- [ ] Support resources prepared (FAQs, troubleshooting)
- [ ] Monitoring and alerting configured
- [ ] Backup communication plan (phone numbers if Zoom fails)

---

## Monitoring and Maintenance

### Key Metrics
- Meeting creation success rate
- Meeting duration (actual vs scheduled)
- No-show rate
- Technical issues reported
- Recording access requests
- API error rates

### Ongoing Tasks
- Review Zoom security updates
- Monitor API usage and rate limits
- Audit access logs monthly
- Update meeting templates as needed
- Review and optimize workflows

---

*Last Updated: 2025*
*Version: 1.0*

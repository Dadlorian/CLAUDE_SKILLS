# Mobile Health (mHealth) App Development Guide

## Project Setup and Planning (Weeks 1-3)

### Technology Stack Selection

**iOS Development:**
- Language: Swift
- UI Framework: SwiftUI
- API: Alamofire or URLSession
- Local Storage: CoreData or Realm
- Testing: XCTest
- Build: Xcode

**Android Development:**
- Language: Kotlin
- UI Framework: Jetpack Compose
- API: Retrofit + OkHttp
- Local Storage: Room Database
- Testing: JUnit 4 + Espresso
- Build: Android Studio

**Cross-Platform Option:**
- Framework: React Native or Flutter
- Single codebase for iOS and Android
- JavaScript/Dart development
- Faster development cycle
- Smaller team required

### Project Structure

```
mhealth-app/
├─ mobile/ (shared code)
│  ├─ src/
│  │  ├─ components/
│  │  ├─ screens/
│  │  ├─ services/
│  │  ├─ models/
│  │  ├─ utils/
│  │  └─ constants/
│  ├─ tests/
│  └─ package.json
├─ ios/ (iOS specific)
│  ├─ Podfile
│  ├─ Info.plist
│  └─ App.xcodeproj
├─ android/ (Android specific)
│  ├─ build.gradle
│  ├─ AndroidManifest.xml
│  └─ app module
└─ Documentation/
   ├─ Architecture.md
   ├─ Development.md
   └─ Deployment.md
```

## Core Features Implementation (Weeks 4-12)

### Authentication Module

```javascript
// Authentication flow
import OAuth2 from 'oauth2-js-pkce';

class AuthService {
  constructor(config) {
    this.oauth = new OAuth2(config);
    this.tokenStorage = new SecureStorage();
  }

  async login(email, password) {
    // Username/password flow for initial login
    const response = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const { accessToken, refreshToken } = await response.json();
    await this.tokenStorage.save({
      accessToken,
      refreshToken,
      expiresAt: Date.now() + 3600000
    });

    return accessToken;
  }

  async refreshToken() {
    const saved = await this.tokenStorage.get();
    const response = await fetch(`${API_URL}/refresh`, {
      method: 'POST',
      body: JSON.stringify({ refreshToken: saved.refreshToken })
    });

    const { accessToken, refreshToken } = await response.json();
    await this.tokenStorage.save({
      accessToken,
      refreshToken,
      expiresAt: Date.now() + 3600000
    });

    return accessToken;
  }

  async logout() {
    await this.tokenStorage.clear();
  }

  async getValidToken() {
    const saved = await this.tokenStorage.get();
    if (Date.now() > saved.expiresAt) {
      return await this.refreshToken();
    }
    return saved.accessToken;
  }
}
```

### Health Data Synchronization

```python
# Backend sync service
from celery import shared_task
from datetime import datetime, timedelta

@shared_task
def sync_patient_health_data(patient_id):
    """Sync health data from EHR/devices"""

    patient = Patient.objects.get(id=patient_id)

    # Get last sync timestamp
    last_sync = PatientSync.objects.filter(
        patient=patient
    ).latest('timestamp').timestamp

    # Fetch from FHIR API
    fhir_client = FHIRClient(patient.ehr_id)

    # Get updated observations since last sync
    observations = fhir_client.get_observations(
        start_date=last_sync
    )

    for obs in observations:
        # Parse FHIR observation
        health_data = parse_fhir_observation(obs)

        # Store in database
        HealthData.objects.update_or_create(
            patient=patient,
            external_id=obs['id'],
            defaults=health_data
        )

    # Update sync timestamp
    PatientSync.objects.create(
        patient=patient,
        timestamp=datetime.now(),
        success=True
    )

# Periodic sync every 6 hours
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'sync-health-data': {
        'task': 'sync_patient_health_data',
        'schedule': crontab(minute=0, hour='*/6'),
    },
}
```

### Wearable Device Integration

```javascript
// Wearable device integration
class WearableIntegration {
  async connectAppleHealth() {
    // Request HealthKit permissions
    const permissionTypes = [
      HKQuantityType.quantityTypeForIdentifier('HKQuantityTypeIdentifierHeartRate'),
      HKQuantityType.quantityTypeForIdentifier('HKQuantityTypeIdentifierStepCount'),
      HKQuantityType.quantityTypeForIdentifier('HKQuantityTypeIdentifierBodyMass')
    ];

    const result = await HealthKit.requestAuthorization({
      permissions: {
        read: permissionTypes,
        write: permissionTypes
      }
    });

    if (result.authorized) {
      return this.startHealthKitSync();
    }
  }

  async connectGoogleFit() {
    // Google Fit OAuth2
    const scopes = [
      'https://www.googleapis.com/auth/fitness.heart_rate.read',
      'https://www.googleapis.com/auth/fitness.activity.read'
    ];

    const token = await GoogleSignIn.signIn({ scopes });

    // Fetch data from Google Fit
    const data = await this.fetchGoogleFitData(token);
    return this.uploadWearableData(data);
  }

  async startHealthKitSync() {
    const query = HKObserverQuery({
      sampleType: HKQuantityType.heartRateType(),
      predicate: HKQuery.predicateForSamplesWithStartDate(
        new Date(Date.now() - 86400000), // Last 24 hours
        null,
        NSMeasurementUnit.countUnitsWithDimensionAndUnit(
          'Hz', HKUnit.unitFromString('count/min')
        )
      ),
      updateHandler: (query, samples) => {
        this.uploadWearableData(samples);
      }
    });

    HealthStore.executeQuery(query);
  }

  async uploadWearableData(data) {
    const encrypted = await encrypt(data);
    return fetch(`${API_URL}/wearable/data`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${await getToken()}` },
      body: JSON.stringify(encrypted)
    });
  }
}
```

## Patient Education and Engagement Features (Weeks 13-15)

### Medication Reminder System

```javascript
// Medication reminder implementation
class MedicationReminderService {
  async scheduleMedicationReminder(medication) {
    const { name, dosage, frequency, time } = medication;

    // Create notification trigger
    const trigger = new PushNotificationTrigger({
      type: 'daily',
      time: time,
      repeat: true
    });

    // Schedule notification
    await PushNotifications.scheduleLocalNotification({
      id: `med_${medication.id}`,
      title: 'Medication Reminder',
      body: `Take ${dosage} of ${name}`,
      fireDate: new Date(),
      trigger: trigger,
      sound: 'default',
      badge: 1
    });

    // Log reminder scheduled
    await logEvent('medication_reminder_scheduled', {
      medication_id: medication.id,
      time: time
    });
  }

  async handleReminderResponse(medicationId, taken) {
    if (taken) {
      // Record adherence
      await fetch(`${API_URL}/adherence/log`, {
        method: 'POST',
        body: JSON.stringify({
          medication_id: medicationId,
          taken_at: new Date().toISOString(),
          source: 'app_reminder'
        })
      });

      // Show positive reinforcement
      showNotification('Great job! Medication recorded.');
    } else {
      // Offer snooze or skip options
      showOptions([
        { text: 'Remind me in 1 hour', action: 'snooze_1h' },
        { text: 'Skip this dose', action: 'skip' },
        { text: 'I took it earlier', action: 'taken' }
      ]);
    }
  }

  async generateAdhereceReport() {
    const adherenceData = await fetch(
      `${API_URL}/adherence/report?period=month`
    );

    const { taken, missed, total } = await adherenceData.json();
    const adherenceRate = (taken / total) * 100;

    return {
      title: `Your Medication Adherence`,
      adherenceRate: adherenceRate.toFixed(1),
      taken: taken,
      missed: missed,
      total: total,
      message: adherenceRate >= 80
        ? 'Excellent adherence! Keep it up!'
        : 'Let's improve your medication routine.'
    };
  }
}
```

### Patient Education Content Delivery

```javascript
// Education module
class PatientEducationModule {
  async loadEducationContent(condition) {
    const content = await fetch(
      `${API_URL}/education/content?condition=${condition}`
    );

    return {
      videos: [
        {
          id: 'diabetes_101',
          title: 'Understanding Diabetes',
          duration: '5:30',
          thumbnail: 'img/diabetes-101.jpg',
          watched: false
        }
      ],
      articles: [
        {
          id: 'healthy-eating',
          title: 'Healthy Eating for Diabetes',
          readTime: '8 min',
          read: false
        }
      ],
      quizzes: [
        {
          id: 'diabetes-knowledge',
          title: 'Diabetes Knowledge Quiz',
          questions: 10,
          completed: false
        }
      ]
    };
  }

  async trackEducationProgress(userId, contentId, type) {
    // Record content viewed/completed
    await fetch(`${API_URL}/education/progress`, {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        content_id: contentId,
        content_type: type,
        completed_at: new Date().toISOString()
      })
    });

    // Check for milestones/achievements
    const progress = await this.getUserEducationProgress(userId);
    if (progress.videosCompleted === 5) {
      this.awardBadge(userId, 'video_learner');
    }
  }

  async personalizeEducationContent(userId) {
    // Get user profile
    const user = await fetch(`${API_URL}/users/${userId}`);
    const { conditions, medications, health_literacy_level } = await user.json();

    // Recommend content based on profile
    const recommendations = await fetch(
      `${API_URL}/education/recommend`,
      {
        method: 'POST',
        body: JSON.stringify({
          conditions,
          literacy_level: health_literacy_level
        })
      }
    );

    return await recommendations.json();
  }
}
```

## Security and Privacy (Weeks 16-17)

### Encryption Implementation

```javascript
// Secure data handling
class EncryptionService {
  async encryptData(plaintext) {
    // Generate random IV
    const iv = crypto.getRandomValues(new Uint8Array(12));

    // Get encryption key from secure storage
    const key = await this.getEncryptionKey();

    // Encrypt using AES-256-GCM
    const ciphertext = await crypto.subtle.encrypt(
      {
        name: 'AES-GCM',
        iv: iv
      },
      key,
      new TextEncoder().encode(plaintext)
    );

    // Return IV + ciphertext (base64 encoded)
    return btoa(String.fromCharCode(...new Uint8Array(iv))) +
           ':' +
           btoa(String.fromCharCode(...new Uint8Array(ciphertext)));
  }

  async decryptData(encryptedData) {
    const [ivStr, ciphertextStr] = encryptedData.split(':');

    // Decode from base64
    const iv = new Uint8Array(
      atob(ivStr).split('').map(c => c.charCodeAt(0))
    );
    const ciphertext = new Uint8Array(
      atob(ciphertextStr).split('').map(c => c.charCodeAt(0))
    );

    // Get decryption key
    const key = await this.getEncryptionKey();

    // Decrypt
    const plaintext = await crypto.subtle.decrypt(
      {
        name: 'AES-GCM',
        iv: iv
      },
      key,
      ciphertext
    );

    return new TextDecoder().decode(plaintext);
  }

  async getEncryptionKey() {
    // Retrieve from secure storage, never in plaintext
    const keyData = await SecureStorage.get('app_encryption_key');
    return crypto.subtle.importKey(
      'raw',
      keyData,
      'AES-GCM',
      false,
      ['encrypt', 'decrypt']
    );
  }
}

// Use in API calls
const api = async (endpoint, options) => {
  if (options.body && options.body.includes('PHI')) {
    const encrypted = await new EncryptionService().encryptData(
      JSON.stringify(options.body)
    );
    options.body = JSON.stringify({ encrypted });
  }

  return fetch(`${API_URL}${endpoint}`, options);
};
```

### HIPAA Compliance Implementation

```javascript
// HIPAA compliance features
class HIPAACompliance {
  // Session timeout
  setupSessionTimeout() {
    let timeout;
    const resetTimeout = () => {
      clearTimeout(timeout);
      timeout = setTimeout(async () => {
        await this.secureLogout();
        this.showAlert('Session expired for security');
      }, 15 * 60 * 1000); // 15 minutes
    };

    // Reset on any user interaction
    document.addEventListener('click', resetTimeout);
    document.addEventListener('keypress', resetTimeout);
    resetTimeout();
  }

  async secureLogout() {
    // Clear all sensitive data
    await SecureStorage.clear();

    // Invalidate token on server
    await fetch(`${API_URL}/logout`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });

    // Clear app state
    store.dispatch('clearAllData');
  }

  // Audit logging
  async logPHIAccess(action, resourceType, resourceId) {
    await fetch(`${API_URL}/audit/log`, {
      method: 'POST',
      body: JSON.stringify({
        action: action,
        resource_type: resourceType,
        resource_id: resourceId,
        timestamp: new Date().toISOString(),
        user_agent: navigator.userAgent,
        ip_address: await this.getUserIP()
      })
    });
  }

  // Data minimization
  minimalDataCollection() {
    // Only collect necessary data
    return {
      // DO collect
      health_metrics: true,
      medications: true,

      // DON'T collect
      location: false,
      contacts: false,
      app_usage_analytics: false
    };
  }
}
```

## Testing and Quality Assurance (Weeks 18-19)

### Test Coverage

```javascript
// Jest test example
import { render, screen } from '@testing-library/react-native';
import MedicationReminder from './MedicationReminder';

describe('MedicationReminder', () => {
  it('displays medication name and dosage', () => {
    const medication = {
      id: 1,
      name: 'Metformin',
      dosage: '500mg',
      frequency: 'twice daily'
    };

    render(<MedicationReminder medication={medication} />);

    expect(screen.getByText('Metformin')).toBeTruthy();
    expect(screen.getByText('500mg')).toBeTruthy();
  });

  it('records medication taken', async () => {
    const { getByTestId } = render(<MedicationReminder />);
    const takeButton = getByTestId('take-medication');

    fireEvent.press(takeButton);

    // Verify logged to backend
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/adherence/log'),
      expect.objectContaining({
        method: 'POST',
        body: expect.stringContaining('taken_at')
      })
    );
  });
});
```

## Deployment and App Store Submission (Weeks 20-21)

### iOS App Store Submission Checklist

- [x] Privacy Policy published and compliant
- [x] Health data usage explanation accurate
- [x] Screenshots and promotional text complete
- [x] Version number incremented
- [x] Build number incremented
- [x] Code signing configured
- [x] Provisioning profiles current
- [x] All frameworks/libraries listed
- [x] No hardcoded secrets or test data
- [x] Accessibility testing passed
- [x] Performance optimized
- [x] Crash testing completed

### Android Play Store Submission

- [x] AndroidManifest.xml properly configured
- [x] Permissions justified and minimized
- [x] Content rating questionnaire completed
- [x] Privacy policy in English and target languages
- [x] Store listing with graphics and description
- [x] Release notes prepared
- [x] Signing certificate configured
- [x] SHA-1 certificate fingerprint registered
- [x] Tested on multiple Android versions

## Post-Launch Monitoring (Ongoing)

### Key Metrics to Track

- Crash rate (target <0.1%)
- Session length (target >3 min)
- Feature adoption rates
- User retention (Week 1, Week 4, Month 1)
- Medication adherence impact
- Patient satisfaction scores
- App ratings and reviews

### Continuous Improvement

- Weekly crash analysis and fixes
- Monthly feature usage analysis
- Quarterly major feature releases
- Seasonal content and feature planning
- User feedback integration

# Mobile Security Guide
## OWASP Mobile Top 10 & Security Best Practices

**Version**: 1.0 | **Based on**: OWASP MSTG, MASVS v2.0

---

## OWASP Mobile Top 10 (2024)

### M1: Improper Credential Usage
**Risk**: Hardcoded or insecurely stored credentials
**Mitigation**:
- Use platform secure storage (Keychain/Keystore)
- Never hardcode API keys or secrets
- Implement OAuth 2.0 / OpenID Connect
- Use biometric authentication

**iOS Implementation**:
```swift
import Security

func saveToKeychain(key: String, data: Data) -> Bool {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key,
        kSecValueData as String: data,
        kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
    ]

    SecItemDelete(query as CFDictionary)
    return SecItemAdd(query as CFDictionary, nil) == errSecSuccess
}

func loadFromKeychain(key: String) -> Data? {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key,
        kSecReturnData as String: true
    ]

    var result: AnyObject?
    SecItemCopyMatching(query as CFDictionary, &result)
    return result as? Data
}
```

**Android Implementation**:
```kotlin
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// Save
encryptedPrefs.edit().putString("api_token", token).apply()

// Retrieve
val token = encryptedPrefs.getString("api_token", null)
```

### M2: Inadequate Supply Chain Security
**Risk**: Vulnerable third-party libraries
**Mitigation**:
- Audit all dependencies regularly
- Use dependency scanning tools
- Pin dependency versions
- Monitor for security advisories

**Tools**:
- iOS: `swift package show-dependencies`, Snyk
- Android: Gradle dependency check, OWASP Dependency-Check
- React Native: `npm audit`, Snyk
- Flutter: `dart pub outdated`, Snyk

### M3: Insecure Authentication/Authorization
**Risk**: Weak authentication, session management
**Mitigation**:
- Implement server-side validation
- Use secure token storage
- Implement token refresh mechanism
- Add biometric authentication

**JWT Token Management**:
```typescript
// React Native - Secure token storage
import * as Keychain from 'react-native-keychain';

async function saveTokens(accessToken: string, refreshToken: string) {
  await Keychain.setGenericPassword('auth', JSON.stringify({
    accessToken,
    refreshToken,
    timestamp: Date.now()
  }), {
    service: 'com.app.auth',
    accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED_THIS_DEVICE_ONLY
  });
}

async function getAccessToken(): Promise<string | null> {
  const credentials = await Keychain.getGenericPassword({ service: 'com.app.auth' });
  if (credentials) {
    const { accessToken, refreshToken, timestamp } = JSON.parse(credentials.password);

    // Check if token is expired (1 hour)
    if (Date.now() - timestamp > 3600000) {
      const newToken = await refreshAccessToken(refreshToken);
      await saveTokens(newToken, refreshToken);
      return newToken;
    }

    return accessToken;
  }
  return null;
}
```

### M4: Insufficient Input/Output Validation
**Risk**: Injection attacks, XSS
**Mitigation**:
- Validate all user inputs
- Sanitize outputs
- Use parameterized queries
- Implement content security policies

```dart
// Flutter - Input validation
class Validator {
  static String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email is required';
    }

    final emailRegex = RegExp(
      r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    );

    if (!emailRegex.hasMatch(value)) {
      return 'Invalid email format';
    }

    return null;
  }

  static String sanitizeInput(String input) {
    return input
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#x27;')
        .replaceAll('&', '&amp;');
  }
}
```

### M5: Insecure Communication
**Risk**: Man-in-the-middle attacks, data interception
**Mitigation**:
- Enforce HTTPS everywhere
- Implement certificate pinning
- Validate SSL/TLS certificates
- Use modern TLS versions (1.2+)

**iOS Certificate Pinning**:
```swift
import Alamofire

class NetworkManager {
    let session: Session

    init() {
        let evaluators = [
            "api.example.com": PublicKeysTrustEvaluator()
        ]

        let manager = ServerTrustManager(evaluators: evaluators)
        session = Session(serverTrustManager: manager)
    }

    func request(url: String) async throws -> Data {
        let response = try await session.request(url).serializingData().value
        return response
    }
}
```

**Android Certificate Pinning**:
```kotlin
val certificatePinner = CertificatePinner.Builder()
    .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()
```

### M6: Inadequate Privacy Controls
**Risk**: Excessive data collection, tracking
**Mitigation**:
- Implement data minimization
- Request permissions at point of use
- Provide privacy controls
- GDPR/CCPA compliance

**Permission Handling**:
```swift
// iOS - Request permission with context
import CoreLocation

class LocationManager: NSObject, CLLocationManagerDelegate {
    let manager = CLLocationManager()

    func requestLocation() {
        // Show why permission is needed
        showLocationPermissionRationale()

        // Request permission
        manager.requestWhenInUseAuthorization()
    }

    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        switch manager.authorizationStatus {
        case .authorizedWhenInUse, .authorizedAlways:
            manager.startUpdatingLocation()
        case .denied, .restricted:
            showPermissionDeniedMessage()
        default:
            break
        }
    }
}
```

### M7: Insufficient Binary Protections
**Risk**: Reverse engineering, code tampering
**Mitigation**:
- Enable code obfuscation
- Implement integrity checks
- Use app attestation
- Jailbreak/root detection

**iOS Jailbreak Detection**:
```swift
func isJailbroken() -> Bool {
    #if targetEnvironment(simulator)
    return false
    #else
    let paths = [
        "/Applications/Cydia.app",
        "/Library/MobileSubstrate/MobileSubstrate.dylib",
        "/bin/bash",
        "/usr/sbin/sshd",
        "/etc/apt"
    ]

    for path in paths {
        if FileManager.default.fileExists(atPath: path) {
            return true
        }
    }

    // Check if can write outside sandbox
    let testPath = "/private/test.txt"
    do {
        try "test".write(toFile: testPath, atomically: true, encoding: .utf8)
        try FileManager.default.removeItem(atPath: testPath)
        return true
    } catch {
        return false
    }
    #endif
}
```

**Android Root Detection**:
```kotlin
fun isRooted(): Boolean {
    val paths = arrayOf(
        "/system/app/Superuser.apk",
        "/sbin/su",
        "/system/bin/su",
        "/system/xbin/su",
        "/data/local/xbin/su",
        "/data/local/bin/su",
        "/system/sd/xbin/su",
        "/system/bin/failsafe/su",
        "/data/local/su"
    )

    return paths.any { File(it).exists() } || checkBuildTags() || checkSu()
}

private fun checkBuildTags(): Boolean {
    return Build.TAGS?.contains("test-keys") == true
}

private fun checkSu(): Boolean {
    return try {
        Runtime.getRuntime().exec("su")
        true
    } catch (e: IOException) {
        false
    }
}
```

### M8: Security Misconfiguration
**Risk**: Debug code in production, excessive permissions
**Mitigation**:
- Disable debugging in release builds
- Minimize app permissions
- Use build configurations
- Remove development endpoints

**Build Configuration**:
```kotlin
// Android - build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            buildConfigField("String", "API_URL", "\"https://api.production.com\"")
            buildConfigField("Boolean", "DEBUG_MODE", "false")
        }
        debug {
            buildConfigField("String", "API_URL", "\"https://api.staging.com\"")
            buildConfigField("Boolean", "DEBUG_MODE", "true")
        }
    }
}
```

### M9: Insecure Data Storage
**Risk**: Sensitive data in logs, backups, or unencrypted storage
**Mitigation**:
- Encrypt sensitive data at rest
- Exclude sensitive data from backups
- Clear data from memory
- Secure logging practices

**Secure Logging**:
```swift
// iOS - Custom logger that filters sensitive data
import os.log

class SecureLogger {
    private let subsystem = "com.example.app"

    func log(_ message: String, level: OSLogType = .default) {
        let filtered = filterSensitiveData(message)
        os_log("%{public}@", log: OSLog(subsystem: subsystem, category: "general"),
               type: level, filtered)
    }

    private func filterSensitiveData(_ message: String) -> String {
        var filtered = message

        // Filter email addresses
        filtered = filtered.replacingOccurrences(
            of: #"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"#,
            with: "[EMAIL]",
            options: [.regularExpression, .caseInsensitive]
        )

        // Filter credit card numbers
        filtered = filtered.replacingOccurrences(
            of: #"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"#,
            with: "[CARD]",
            options: .regularExpression
        )

        return filtered
    }
}
```

### M10: Insufficient Cryptography
**Risk**: Weak encryption, poor key management
**Mitigation**:
- Use platform crypto APIs
- Modern encryption algorithms (AES-256, RSA-2048+)
- Secure random number generation
- Proper key derivation

**Encryption Example**:
```kotlin
// Android - Encrypt/Decrypt data
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

object CryptoUtil {
    private const val TRANSFORMATION = "AES/GCM/NoPadding"
    private const val KEY_SIZE = 256
    private const val TAG_LENGTH = 128

    fun generateKey(): SecretKey {
        val keyGenerator = KeyGenerator.getInstance("AES")
        keyGenerator.init(KEY_SIZE)
        return keyGenerator.generateKey()
    }

    fun encrypt(data: ByteArray, key: SecretKey): Pair<ByteArray, ByteArray> {
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.ENCRYPT_MODE, key)

        val iv = cipher.iv
        val encrypted = cipher.doFinal(data)

        return Pair(encrypted, iv)
    }

    fun decrypt(encrypted: ByteArray, iv: ByteArray, key: SecretKey): ByteArray {
        val cipher = Cipher.getInstance(TRANSFORMATION)
        val spec = GCMParameterSpec(TAG_LENGTH, iv)
        cipher.init(Cipher.DECRYPT_MODE, key, spec)

        return cipher.doFinal(encrypted)
    }
}
```

---

## Additional Security Measures

### App Attestation

**iOS App Attest**:
```swift
import DeviceCheck

func attestApp() async throws {
    let service = DCAppAttestService.shared

    guard service.isSupported else {
        throw AttestError.notSupported
    }

    let keyId = try await service.generateKey()
    let challenge = fetchChallenge() // From your server
    let attestation = try await service.attestKey(keyId, clientDataHash: challenge)

    // Send attestation to server for verification
    try await verifyAttestation(keyId: keyId, attestation: attestation)
}
```

**Android Play Integrity**:
```kotlin
import com.google.android.play.core.integrity.IntegrityManager
import com.google.android.play.core.integrity.IntegrityManagerFactory

fun checkIntegrity(context: Context) {
    val integrityManager: IntegrityManager =
        IntegrityManagerFactory.create(context)

    val nonce = generateNonce() // Your nonce generation

    val integrityTokenRequest = IntegrityTokenRequest.builder()
        .setNonce(nonce)
        .build()

    integrityManager.requestIntegrityToken(integrityTokenRequest)
        .addOnSuccessListener { response ->
            val token = response.token()
            // Send token to your server for verification
            verifyIntegrityToken(token)
        }
        .addOnFailureListener { exception ->
            handleIntegrityError(exception)
        }
}
```

---

## Security Checklist

### Development Phase
- [ ] All API keys in environment variables
- [ ] Sensitive data encrypted at rest
- [ ] HTTPS enforced everywhere
- [ ] Certificate pinning implemented
- [ ] Input validation on all user inputs
- [ ] Output sanitization implemented
- [ ] SQL injection protection (parameterized queries)
- [ ] XSS protection in WebViews

### Pre-Release
- [ ] Debug logging disabled in production
- [ ] Code obfuscation enabled
- [ ] Root/jailbreak detection implemented
- [ ] App integrity checks added
- [ ] Security audit completed
- [ ] Penetration testing done
- [ ] Third-party library audit
- [ ] OWASP Mobile Top 10 reviewed

### Production
- [ ] Monitor for security incidents
- [ ] Update dependencies regularly
- [ ] Implement bug bounty program
- [ ] Regular security assessments
- [ ] Incident response plan ready
- [ ] Data breach notification process
- [ ] GDPR/CCPA compliance verified

---

**Security is not optional - it's a fundamental requirement for professional mobile applications!**

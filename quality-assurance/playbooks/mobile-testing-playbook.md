# Mobile Testing Playbook

## iOS Testing Strategy

### Device Coverage
- iPhone SE (4.7" - small)
- iPhone 14 (6.1" - standard)
- iPhone 14 Pro Max (6.7" - large)
- iPad (10.2" - tablet)
- iPad Pro (12.9" - large tablet)

### iOS Version Coverage
- iOS 15 (N-2)
- iOS 16 (N-1)
- iOS 17 (Current)
- Beta (if available)

### Appium iOS Testing
```typescript
import { remote } from 'webdriverio';

const capabilities = {
  platformName: 'iOS',
  'appium:platformVersion': '17.0',
  'appium:deviceName': 'iPhone 14',
  'appium:automationName': 'XCUITest',
  'appium:app': '/path/to/app.ipa',
  'appium:udid': 'device-udid'
};

const driver = await remote({
  hostname: 'localhost',
  port: 4723,
  capabilities
});

// Test login
await driver.$('~username').setValue('test@example.com');
await driver.$('~password').setValue('password123');
await driver.$('~loginButton').click();

// Verify dashboard
const welcome = await driver.$('~welcomeMessage');
expect(await welcome.getText()).toContain('Welcome');
```

### XCUITest (Native iOS)
```swift
import XCTest

class LoginTests: XCTestCase {
    let app = XCUIApplication()
    
    override func setUp() {
        super.setUp()
        app.launch()
    }
    
    func testValidLogin() {
        // Find elements by accessibility identifier
        let usernameField = app.textFields["username"]
        let passwordField = app.secureTextFields["password"]
        let loginButton = app.buttons["loginButton"]
        
        // Perform login
        usernameField.tap()
        usernameField.typeText("test@example.com")
        
        passwordField.tap()
        passwordField.typeText("password123")
        
        loginButton.tap()
        
        // Verify result
        let welcomeMessage = app.staticTexts["welcomeMessage"]
        XCTAssertTrue(welcomeMessage.exists)
        XCTAssertTrue(welcomeMessage.label.contains("Welcome"))
    }
}
```

## Android Testing Strategy

### Device Coverage
- Small phone (5.0" - 1080x1920)
- Standard phone (6.0" - 1080x2340)
- Large phone (6.5"+ - 1440x3120)
- Tablet (10.1" - 1920x1200)

### Android Version Coverage
- Android 11 (API 30)
- Android 12 (API 31)
- Android 13 (API 33)
- Android 14 (API 34)

### Espresso (Native Android)
```kotlin
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class LoginTest {
    @Test
    fun testValidLogin() {
        // Type username
        onView(withId(R.id.username))
            .perform(typeText("test@example.com"), closeSoftKeyboard())
        
        // Type password
        onView(withId(R.id.password))
            .perform(typeText("password123"), closeSoftKeyboard())
        
        // Click login
        onView(withId(R.id.loginButton))
            .perform(click())
        
        // Verify dashboard
        onView(withId(R.id.welcomeMessage))
            .check(matches(withText(containsString("Welcome"))))
    }
}
```

## React Native Testing (Detox)
```javascript
describe('Login Flow', () => {
  beforeAll(async () => {
    await device.launchApp();
  });

  beforeEach(async () => {
    await device.reloadReactNative();
  });

  it('should login with valid credentials', async () => {
    // Type credentials
    await element(by.id('username')).typeText('test@example.com');
    await element(by.id('password')).typeText('password123');
    
    // Submit
    await element(by.id('loginButton')).tap();
    
    // Verify
    await expect(element(by.id('dashboard'))).toBeVisible();
    await expect(element(by.text('Welcome'))).toBeVisible();
  });

  it('should handle offline mode', async () => {
    // Disable network
    await device.disableNetwork();
    
    // Try action
    await element(by.id('refreshButton')).tap();
    
    // Verify offline message
    await expect(element(by.text('No connection'))).toBeVisible();
    
    // Re-enable network
    await device.enableNetwork();
  });
});
```

## Mobile-Specific Tests

### Gestures
```typescript
// Swipe
await driver.execute('mobile: swipe', {
  direction: 'left',
  element: await driver.$('#carousel')
});

// Scroll
await driver.execute('mobile: scroll', {
  direction: 'down'
});

// Pinch zoom
await driver.execute('mobile: pinch', {
  scale: 2.0,
  velocity: 0.5
});

// Long press
const element = await driver.$('#item');
await driver.touchPerform([
  { action: 'press', options: { element: element.elementId }},
  { action: 'wait', options: { ms: 2000 }},
  { action: 'release' }
]);
```

### Orientation
```typescript
// Portrait
await driver.setOrientation('PORTRAIT');
await expect(page).toHaveScreenshot('portrait.png');

// Landscape
await driver.setOrientation('LANDSCAPE');
await expect(page).toHaveScreenshot('landscape.png');
```

### Network Conditions
```typescript
// Slow 3G
await driver.setNetworkConnection(4); // AIRPLANE_MODE + WIFI

// Offline
await driver.setNetworkConnection(1); // AIRPLANE_MODE

// Fast connection
await driver.setNetworkConnection(6); // WIFI + DATA
```

### Biometric Authentication
```typescript
// Simulate fingerprint
await driver.execute('mobile: sendBiometricMatch', { match: true });

// Simulate face ID
await driver.execute('mobile: sendBiometricMatch', { 
  type: 'faceId',
  match: true 
});
```

## Mobile Testing Checklist

### Functionality
- [ ] Touch targets ≥ 44x44px
- [ ] Gestures work (swipe, pinch, long press)
- [ ] Keyboard shows/hides correctly
- [ ] Back button behavior correct (Android)
- [ ] Deep links work
- [ ] Push notifications work
- [ ] Background/foreground transitions
- [ ] App permissions handled
- [ ] Camera/photo access works
- [ ] Location services work

### Performance
- [ ] App launch time < 2 seconds
- [ ] Scrolling is smooth (60 FPS)
- [ ] No memory leaks
- [ ] Battery usage acceptable
- [ ] Works on slow networks
- [ ] Offline functionality works
- [ ] Images load efficiently
- [ ] App size reasonable

### UX
- [ ] No horizontal scrolling
- [ ] Text readable without zoom
- [ ] Forms easy to complete
- [ ] Error messages helpful
- [ ] Loading states present
- [ ] Pull to refresh works
- [ ] Empty states handled
- [ ] Dark mode supported
- [ ] Safe area insets handled

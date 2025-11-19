# Behavioral Biometrics Reference

## Overview
Behavioral biometrics analyze how users interact with devices rather than what they know or possess. This provides continuous, non-intrusive authentication and risk assessment.

## Behavioral Dimensions

### Keystroke Dynamics
- **Typing speed**: Words per minute, characters per second
- **Dwell time**: Time key is pressed (hold duration)
- **Flight time**: Time between key presses
- **Rhythm patterns**: Timing sequence of characters
- **Pressure consistency**: Key press force (mobile/touch devices)
- **Error patterns**: Correction speed and frequency
- **Rare key usage**: Punctuation and special characters

**Detection Approach**
- Baseline typing profile for user
- Compare new typing patterns to baseline
- Anomaly score from statistical deviation
- Combined metrics (e.g., average flight time, dwell consistency)

### Mouse & Pointer Dynamics
- **Movement speed**: Pixels per second
- **Acceleration patterns**: Speed changes
- **Trajectory curves**: Path shape and smoothness
- **Click patterns**: Click force and duration
- **Pause duration**: Time between movements
- **Direction changes**: Angle and frequency of changes
- **Double-click spacing**: Timing between consecutive clicks

**Detection Approach**
- Capture movement sequences
- Extract statistical features (mean, std dev, min, max)
- Compare to historical baseline
- Assess anomaly probability

### Touch & Swipe Patterns (Mobile)
- **Swipe speed**: Pixels per millisecond
- **Swipe duration**: Time for complete swipe
- **Swipe pressure**: Touch force
- **Swipe size**: Distance traveled
- **Multi-touch patterns**: Multiple finger interactions
- **Tap force**: Pressure on screen
- **Touch size**: Finger contact area

**Detection Approach**
- Profile natural touch behavior
- Detect deviations in speed, pressure, size
- Combined gesture pattern matching
- Real-time risk scoring

### Navigation Behavior
- **Page navigation sequence**: Order of pages visited
- **Time on page**: Duration spent on each page
- **Click patterns**: Where and when clicks occur
- **Form field order**: Order of form completion
- **Back button usage**: Navigation mistakes
- **Page scroll patterns**: Scrolling speed and patterns
- **Hover patterns**: Mouse hover timing

**Detection Approach**
- Create navigation flow baselines
- Detect unusual sequences
- Identify forced or robot-like navigation
- Assess user intent alignment

### Session Behavior
- **Login time patterns**: When user typically logs in
- **Session duration**: Typical session lengths
- **Activity frequency**: How often user accesses system
- **Idle time tolerance**: Time before auto-logout comfortable
- **Multi-session patterns**: Concurrent session usage
- **Device switching**: Cross-device behavior
- **Location consistency**: Geographic access patterns

**Detection Approach**
- Build temporal baselines
- Detect time-of-day deviations
- Identify unusual access patterns
- Assess overall session risk

## Behavioral Profile Creation

### Data Collection Phase
1. **Baseline period**: 2-4 weeks of normal activity
2. **Feature extraction**: Extract behavioral metrics
3. **Statistical modeling**: Calculate distributions
4. **Thresholds**: Establish normal ranges (±2-3 standard deviations)

### Profile Components
```
User Behavioral Profile {
  typing_speed: {mean: 45 WPM, std_dev: 5},
  dwell_time: {mean: 85ms, std_dev: 15},
  flight_time: {mean: 120ms, std_dev: 30},
  mouse_speed: {mean: 350 px/s, std_dev: 50},
  session_duration: {mean: 45 mins, std_dev: 15},
  login_hours: [9-17 with weekend occasional],
  location_variance: [±50 miles primary location]
}
```

## Anomaly Scoring from Behavior

### Statistical Approach
```
Anomaly_Score = sqrt(
  ((typing_speed - mean) / std_dev)^2 +
  ((dwell_time - mean) / std_dev)^2 +
  ((flight_time - mean) / std_dev)^2
)
```

### Machine Learning Approach
- Train Isolation Forest on baseline behavior
- Score new sessions as anomalies
- Real-time scoring as user types

### Confidence Scoring
- Score ranges: 0 (very normal) to 1 (very anomalous)
- Gradually increase score as deviations accumulate
- Reset score on confirmed legitimate activity
- Account for gradual behavior evolution

## Risk Escalation Based on Behavior

### Progressive Authentication
```
Risk Score 0-0.3: Allow transaction, monitor
Risk Score 0.3-0.6: Optional secondary authentication
Risk Score 0.6-0.8: Require 2FA or additional verification
Risk Score 0.8-1.0: Block transaction, contact user
```

### Adaptive Learning
- Legitimate user behavior evolves over time
- Gradually accept new behavior patterns
- Maintain historical "normal" range
- Detect permanent behavior changes

## Behavioral Indicators of Compromise

### ATO (Account Takeover) Signals
- **Dramatic typing speed change**: Attacker has different speed
- **Different device type**: New OS or browser
- **Different location**: Different geographical area
- **Different language**: Keyboard layout change
- **Unnatural navigation**: Robot-like patterns
- **Unusual session times**: Different active hours
- **Rapid multi-page navigation**: Automated bot behavior

### Fraud Indicators
- **Unusual purchase patterns**: Different merchant types
- **Higher transaction amounts**: Exceeding typical baseline
- **Rapid transaction velocity**: Compressed timeframe
- **Navigation shortcuts**: Skipping normal flow steps
- **Form auto-fill patterns**: Batch transaction entry

## Implementation Challenges

### Legitimate Variations
- **Learning curve**: New users changing behavior
- **Device differences**: Desktop vs mobile behavior
- **Temporary illness**: Typing speed reduction
- **Environmental factors**: Noise affecting focus
- **Intentional speed-up**: Rushing through transaction
- **Seasonal changes**: Behavioral evolution

### Privacy Considerations
- **Data sensitivity**: Behavioral data very personal
- **Consent requirements**: GDPR/privacy law compliance
- **Data retention**: Limiting storage periods
- **Cross-site tracking**: Privacy boundaries
- **User transparency**: Clear disclosure of monitoring

## Advantages & Limitations

### Advantages
- Continuous authentication without user friction
- Difficult to spoof without extensive training
- Natural and non-intrusive
- Works alongside other methods
- Provides early compromise detection

### Limitations
- Requires baseline establishment period
- Legitimate user behavior changes
- Training time for attackers
- Device/OS limitations
- Privacy and compliance concerns

## Integration with Other Methods

### Combined Risk Assessment
```
Overall_Risk =
  0.3 * Behavioral_Risk +
  0.3 * Device_Reputation_Risk +
  0.2 * Network_Risk +
  0.2 * Transaction_Amount_Risk
```

### Behavioral + Device Fingerprinting
- Device consistency check
- Behavior-device mismatch detection
- Compromised device identification

### Behavioral + ML Fraud Models
- Feature input to fraud scoring
- Historical behavior in feature engineering
- Baseline deviation as predictor

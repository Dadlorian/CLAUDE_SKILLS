# IoMT Devices Reference

## Overview
Comprehensive reference for Internet of Medical Things (IoMT) devices used in remote patient monitoring, telehealth, and connected health applications.

---

## IoMT Device Categories

### Vital Signs Monitors
Devices that measure and transmit basic physiologic parameters.

### Chronic Disease Management Devices
Specialized devices for monitoring specific chronic conditions.

### Wearable Biosensors
Continuous monitoring devices worn on the body.

### Implantable Devices
Medical devices implanted in the body with remote monitoring capabilities.

### Environmental Sensors
Devices monitoring patient environment and safety.

---

## Blood Pressure Monitors

### Withings BPM Connect

**Specifications**:
- **Connectivity**: WiFi, Bluetooth
- **Measurement Range**:
  - Blood Pressure: 60-280 mmHg
  - Heart Rate: 40-180 bpm
- **Accuracy**: ±3 mmHg (validated to clinical standards)
- **Cuff Size**: Adjustable 8.7"-16.5" (22-42 cm)
- **Power**: Rechargeable battery (6-month battery life)
- **Display**: LED indicator lights
- **Data Transmission**: Automatic via WiFi or Bluetooth

**Features**:
- One-button operation
- Color-coded feedback (green/yellow/red for BP ranges)
- Irregular heartbeat detection
- Multi-user support
- Integration with Health Mate app
- HIPAA-compliant when used with enterprise platform

**Clinical Use Cases**:
- Hypertension management
- Heart failure monitoring
- Post-hospital discharge monitoring
- Medication titration programs

**Pricing**: ~$100 device cost

**Integration**: API available for enterprise RPM platforms

---

### Omron Evolv

**Specifications**:
- **Connectivity**: Bluetooth only
- **Measurement Range**: Similar to Withings
- **Accuracy**: Clinically validated
- **Cuff Size**: One-size-fits-most wireless cuff (9"-17")
- **Power**: Rechargeable via USB
- **Display**: Smartphone app only (no device display)

**Features**:
- All-in-one design (no tubes)
- Portable and compact
- Omron Connect app
- Irregular heartbeat detection
- Unlimited user profiles
- Stores up to 100 readings on device

**Pros**: Very portable, sleek design
**Cons**: Requires smartphone, no WiFi (must manually sync)

**Clinical Use Cases**: Same as Withings, better for tech-savvy patients

---

### QardioArm

**Specifications**:
- **Connectivity**: Bluetooth
- **Measurement Range**: Standard BP ranges
- **Accuracy**: FDA-cleared, clinically validated
- **Cuff Size**: 8.7"-14.6" or 11.8"-17.7" (two sizes)
- **Power**: Rechargeable battery
- **Display**: App only

**Features**:
- Compact and portable (no screen)
- Travel-friendly
- Multi-user support
- Irregular heartbeat detection
- Integration with Apple Health, Samsung Health
- Smart reminders

**Unique**: Very compact design, good for travel

---

### Comparison Matrix

| Feature | Withings BPM Connect | Omron Evolv | QardioArm |
|---------|---------------------|-------------|-----------|
| **WiFi** | Yes | No | No |
| **Bluetooth** | Yes | Yes | Yes |
| **Display** | LED lights | None | None |
| **Cuff Design** | Traditional | Wireless all-in-one | Compact traditional |
| **Battery Life** | 6 months | 300 readings | 200-300 readings |
| **Price** | $100 | $100 | $100 |
| **Best For** | RPM (WiFi auto-sync) | Portable use | Travel/compact |

---

## Glucose Monitors

### Dexcom G6/G7 (Continuous Glucose Monitor)

**Specifications**:
- **Type**: Real-time continuous glucose monitor (rtCGM)
- **Sensor Duration**: 10 days (G6), 10-14 days (G7)
- **Calibration**: No fingerstick calibration required
- **Measurement Range**: 40-400 mg/dL
- **Accuracy**: MARD ~9% (G6), ~8% (G7)
- **Connectivity**: Bluetooth to smartphone/receiver
- **Alerts**: Customizable high/low glucose alerts

**Components**:
- Disposable sensor (inserted subcutaneously)
- Transmitter (reusable for G6, integrated for G7)
- Receiver or smartphone app

**Features**:
- Real-time glucose readings every 5 minutes
- Trend arrows (rate of change)
- Share feature (send data to caregivers)
- Integration with insulin pumps
- Data sharing with providers
- Clarity app for analytics

**Clinical Use Cases**:
- Type 1 diabetes
- Type 2 diabetes on insulin
- Gestational diabetes
- Intensive diabetes management

**Reimbursement**: Typically covered under DME (not RPM), but data can supplement RPM programs

**Pricing**:
- Sensors: ~$300/month (out-of-pocket)
- Transmitter: ~$300 (G6, 3-month lifespan)
- G7: Integrated, ~$350/month

---

### Abbott FreeStyle Libre (Flash Glucose Monitor)

**Specifications**:
- **Type**: Flash glucose monitor (scan-based CGM)
- **Sensor Duration**: 14 days
- **Calibration**: Factory calibrated, no fingersticks
- **Measurement Range**: 40-500 mg/dL
- **Accuracy**: MARD ~9.4%
- **Connectivity**: NFC (scan with reader or phone) + Bluetooth (Libre 2/3)
- **Alerts**: Available in Libre 2 and 3

**Components**:
- Disposable sensor (subcutaneous)
- Reader or smartphone app

**Features**:
- Scan to view glucose (Libre 1)
- Continuous Bluetooth streaming (Libre 2/3)
- 8-hour glucose history
- Time in range reporting
- LibreView cloud platform for providers

**Advantages**:
- Lower cost than Dexcom
- No transmitter needed
- Smaller sensor profile

**Clinical Use Cases**: Same as Dexcom, often used for cost-conscious patients

**Pricing**: ~$70-120/month (out-of-pocket)

---

### OneTouch Verio Flex (Traditional BGM with Bluetooth)

**Specifications**:
- **Type**: Traditional blood glucose meter
- **Connectivity**: Bluetooth
- **Sample Size**: 0.4 µL
- **Test Time**: 5 seconds
- **Measurement Range**: 20-600 mg/dL
- **Accuracy**: Meets ISO 15197:2013 standards
- **Memory**: 500 test results

**Features**:
- Color-coded range indicator
- Bluetooth sync to smartphone app
- Pattern alerts (high/low trends)
- OneTouch Reveal app
- Data sharing with healthcare providers

**Clinical Use Cases**:
- Type 2 diabetes (not on CGM)
- RPM programs requiring traditional BGM data
- Cost-effective monitoring

**Pricing**:
- Meter: ~$20-40
- Test strips: ~$20-100/month (varies widely)

---

## Pulse Oximeters

### Nonin 3150 Bluetooth Pulse Oximeter

**Specifications**:
- **Type**: Medical-grade fingertip pulse oximeter
- **Connectivity**: Bluetooth Low Energy (BLE)
- **Parameters**: SpO2, pulse rate, perfusion index
- **Accuracy**: ±2% for SpO2 (70-100%)
- **Range**: SpO2 0-100%, Pulse 18-321 bpm
- **Power**: AAA batteries (>6000 spot checks)
- **Display**: OLED screen

**Features**:
- Medical-grade accuracy
- Six display modes
- Plethysmograph waveform
- FDA 510(k) cleared
- Bluetooth data transmission to RPM platforms
- Durable design

**Clinical Use Cases**:
- COPD monitoring
- COVID-19 home monitoring
- Sleep apnea screening
- Post-operative monitoring
- Heart failure with hypoxemia

**Pricing**: ~$200-300

---

### Masimo MightySat Rx

**Specifications**:
- **Type**: Fingertip pulse oximeter
- **Connectivity**: Bluetooth
- **Parameters**: SpO2, pulse rate, perfusion index, RRp (respiration rate), PVi
- **Accuracy**: High accuracy (Masimo SET technology)
- **Power**: Rechargeable battery

**Features**:
- Hospital-grade accuracy
- Multiple physiologic parameters
- Masimo SET motion tolerance
- Graphical displays
- Data storage and trending
- Professional-grade device

**Advantages**: Most accurate, multiple parameters
**Disadvantages**: Higher cost (~$400-500)

---

### Wellue O2Ring (Continuous Overnight Monitoring)

**Specifications**:
- **Type**: Ring-style continuous pulse oximeter
- **Connectivity**: Bluetooth
- **Wear Time**: Overnight monitoring (12-16 hours)
- **Parameters**: SpO2, heart rate
- **Alerts**: Vibration alerts for low oxygen
- **Power**: Rechargeable battery

**Features**:
- Continuous overnight monitoring
- Wearable ring design
- Real-time alerts
- Sleep report generation
- Data export (PDF, CSV)

**Clinical Use Cases**:
- Sleep apnea monitoring
- Nocturnal hypoxemia detection
- COPD overnight monitoring

**Pricing**: ~$130-180

---

## Weight Scales

### Withings Body+ WiFi Scale

**Specifications**:
- **Connectivity**: WiFi, Bluetooth
- **Capacity**: 396 lbs (180 kg)
- **Accuracy**: ±0.2 lbs (0.1 kg)
- **Parameters**: Weight, BMI, body composition (fat %, water %, muscle %, bone mass)
- **Multi-User**: Up to 8 users, automatic recognition
- **Power**: AAA batteries (18-month battery life)
- **Display**: LCD with weather

**Features**:
- Automatic WiFi sync
- Multi-user support
- Body composition analysis
- Pregnancy tracking mode
- Integration with Health Mate app
- Baby/pet weighing mode

**Clinical Use Cases**:
- Heart failure daily weight monitoring
- Obesity management
- Post-bariatric surgery
- Chronic kidney disease
- General wellness programs

**Pricing**: ~$100-130

---

### QardioBase 2 Smart Scale

**Specifications**:
- **Connectivity**: WiFi, Bluetooth
- **Capacity**: 400 lbs (182 kg)
- **Accuracy**: ±0.2 lbs
- **Parameters**: Weight, BMI, body composition
- **Multi-User**: Unlimited users
- **Power**: Rechargeable battery (12 months)
- **Display**: Circular LED display

**Features**:
- Smart Feedback (emoticons for progress)
- Pregnancy mode (no body composition measurement)
- Muscle/fat composition trending
- Integration with Apple Health, Fitbit, etc.

**Pricing**: ~$150

---

### BodyTrace Scale (Clinical RPM)

**Specifications**:
- **Connectivity**: Cellular (4G LTE)
- **Capacity**: 550 lbs
- **Accuracy**: ±0.2 lbs
- **Parameters**: Weight only (no body composition to avoid confusion)
- **Power**: AC powered
- **Display**: Large LCD for visibility

**Features**:
- Cellular connectivity (no WiFi setup needed)
- Designed specifically for RPM programs
- Large, stable platform
- High weight capacity
- No patient setup required
- Instant cloud transmission

**Advantages**: Best for elderly/non-tech-savvy patients (completely automatic)

**Pricing**: ~$200 device, ongoing cellular fees

---

## Multi-Parameter Devices

### Current Health Wearable

**Specifications**:
- **Type**: Continuous vital signs monitoring patch
- **Connectivity**: Cellular
- **Parameters**: Heart rate, RR, temperature, activity, SpO2, body position
- **Wear Duration**: Up to 30 days (disposable)
- **Power**: Integrated battery
- **Form Factor**: Adhesive chest patch

**Features**:
- Continuous 24/7 monitoring
- Real-time data streaming
- FDA 510(k) cleared
- AI-powered deterioration detection
- Clinician dashboard with alerts
- No patient interaction needed

**Clinical Use Cases**:
- Post-hospital discharge monitoring
- Hospital-at-home programs
- COVID-19 remote monitoring
- High-risk patient surveillance
- Clinical trials

**Pricing**: ~$150-300 per patient per month (includes platform)

---

### VitalConnect VitalPatch

**Specifications**:
- **Type**: Biosensor patch
- **Connectivity**: Bluetooth to smartphone, then cellular
- **Parameters**: ECG, heart rate, HRV, RR, skin temperature, activity, posture, fall detection
- **Wear Duration**: Up to 5 days (single-use disposable)
- **Power**: Integrated battery
- **Form Factor**: Chest-worn adhesive patch

**Features**:
- Medical-grade ECG waveform
- Arrhythmia detection
- Continuous monitoring
- FDA 510(k) cleared
- Clinical-grade accuracy
- Waterproof

**Clinical Use Cases**:
- Cardiac monitoring (arrhythmia detection)
- Post-operative monitoring
- Heart failure monitoring
- Clinical trials

**Pricing**: ~$50-100 per patch (5-day use)

---

### BioIntelliSense BioSticker

**Specifications**:
- **Type**: Continuous multi-parameter wearable
- **Connectivity**: Bluetooth to smartphone app
- **Parameters**: Skin temperature, RR, heart rate, activity
- **Wear Duration**: Up to 30 days (disposable)
- **Power**: Integrated battery
- **Form Factor**: Small adhesive patch (torso placement)

**Features**:
- Compact design
- Long wear time
- FDA 510(k) cleared
- Continuous streaming
- Mobile app + clinician portal

**Clinical Use Cases**:
- COVID-19 monitoring
- Post-acute care monitoring
- Remote patient surveillance

**Pricing**: ~$100-200 per patient per month

---

## Cardiac Implantable Devices

### Medtronic CareLink Network

**Devices Monitored**:
- Implantable cardioverter defibrillators (ICDs)
- Pacemakers
- Cardiac resynchronization therapy (CRT) devices
- Insertable cardiac monitors (ICMs)

**Specifications**:
- **Connectivity**: Bluetooth (from device to bedside monitor), cellular (monitor to cloud)
- **Transmission Frequency**: Daily automatic transmissions, on-demand patient-initiated
- **Parameters**: Device diagnostics, arrhythmias, lead impedances, battery status, therapy delivery

**Features**:
- Remote interrogation
- Automatic scheduled transmissions
- Patient-initiated transmissions (if symptomatic)
- Clinician alerts for actionable events
- Web-based clinician portal
- Integration with EHR (HL7)

**Clinical Benefits**:
- Early detection of arrhythmias
- Reduced in-person device checks
- Improved patient outcomes
- Guideline-recommended for heart failure and ICD patients

**Reimbursement**: CPT codes 93290-93298 (per 90-day monitoring period)

---

### Abbott (St. Jude Medical) Merlin.net

**Devices Monitored**:
- ICDs, pacemakers, CRT devices, ICMs

**Specifications**:
- Similar to Medtronic CareLink
- Bluetooth and cellular connectivity
- Daily and scheduled transmissions
- Remote monitoring and alerts

**Features**:
- PatientConnect mobile app (smartphone-based transmission)
- No bedside monitor needed for some patients
- Clinician web portal
- EHR integration

---

### Boston Scientific LATITUDE NXT

**Devices Monitored**:
- ICDs, pacemakers, CRT devices, ICMs

**Specifications**:
- Cellular-connected bedside communicator
- Daily automatic transmissions
- Comprehensive device diagnostics

**Features**:
- Remote interrogation and programming (limited)
- Alert-based workflow
- Clinician portal
- Mobile access

---

## Respiratory Devices

### ResMed AirSense (CPAP with Cellular Connectivity)

**Specifications**:
- **Device Type**: CPAP machine for sleep apnea
- **Connectivity**: Built-in cellular modem
- **Data Transmitted**: Usage hours, AHI (apnea-hypopnea index), mask leak, pressure settings
- **Transmission Frequency**: Daily automatic

**Features**:
- myAir patient app (daily sleep score)
- AirView provider portal
- Adherence monitoring
- Therapy efficacy data
- Automated alerts for poor adherence

**Clinical Use Cases**:
- CPAP adherence monitoring
- Medicare compliance (adherence requirements for coverage)
- Therapy optimization

**Reimbursement**: DME coverage, adherence data used for continued coverage

---

### Propeller Health (Asthma/COPD Inhaler Sensor)

**Specifications**:
- **Device Type**: Sensor that attaches to inhaler
- **Connectivity**: Bluetooth to smartphone
- **Data**: Medication usage (date/time, location), symptom tracking
- **Compatibility**: Fits most inhalers (rescue and controller)

**Features**:
- Tracks medication adherence
- GPS location of inhaler use (identifies triggers)
- Reminders for controller medication
- Patient app with insights
- Clinician portal for adherence review
- Integration with EHR

**Clinical Use Cases**:
- Asthma management
- COPD medication adherence
- Exacerbation prevention

**Pricing**: Often provided through health plans or pharma programs

---

## Specialized Monitoring

### ECG Patches and Monitors

**AliveCor KardiaMobile 6L**:
- **Type**: Portable 6-lead ECG
- **Connectivity**: Bluetooth to smartphone
- **Usage**: On-demand ECG recording
- **Clinical Use**: Arrhythmia detection, AFib screening
- **FDA Cleared**: Yes
- **AI Analysis**: Automated ECG interpretation
- **Pricing**: ~$100 device, $10/month subscription for advanced features

**iRhythm Zio Patch**:
- **Type**: Single-use continuous ECG patch
- **Duration**: Up to 14 days
- **Connectivity**: No real-time (store-and-forward after return)
- **Clinical Use**: Extended Holter monitoring, arrhythmia detection
- **Professional Device**: Ordered by physician, returned for analysis

---

### Fall Detection Devices

**Apple Watch Series 4+**:
- **Fall Detection**: Automatic fall detection with wrist impact and trajectory analysis
- **Emergency SOS**: Automatic call to emergency services after fall (if unresponsive)
- **Medical ID**: Emergency contacts notified

**Philips Lifeline GoSafe**:
- **Type**: Mobile PERS (personal emergency response system)
- **Features**: Fall detection, GPS location, two-way voice communication
- **Clinical Use**: Elderly safety, post-hospitalization monitoring

---

## Device Communication Protocols

### Bluetooth Low Energy (BLE)

**Characteristics**:
- **Version**: BLE 4.0, 4.2, 5.0, 5.1
- **Range**: 10-30 meters (class 2)
- **Power**: Very low (coin cell batteries last months/years)
- **Data Rate**: 1-2 Mbps
- **Pairing**: Required (some devices use "just works" pairing)

**Health Device Profiles**:
- **Blood Pressure Profile (BLP)**: Standard for BP monitors
- **Glucose Profile (GLP)**: Standard for glucose meters
- **Health Thermometer Profile (HTP)**: Temperature devices
- **Weight Scale Profile (WSP)**: Weight scales
- **Pulse Oximeter Profile (PLXP)**: SpO2 devices

**Advantages**:
- Low power consumption
- Widespread smartphone support
- Standardized profiles

**Challenges**:
- Requires patient smartphone as intermediary
- Pairing complexity for non-tech users
- Range limitations

---

### WiFi (802.11)

**Characteristics**:
- **Standards**: 802.11b/g/n/ac
- **Range**: 50-100 meters
- **Power**: Higher than BLE (AC power or frequent charging)
- **Data Rate**: High (not critical for vital signs)

**Advantages**:
- Direct cloud transmission (no smartphone needed)
- Reliable home connectivity
- Automatic data sync

**Challenges**:
- WiFi setup complexity (SSID, password)
- Power consumption
- Firewall/network security issues

---

### Cellular (4G LTE, 5G)

**Characteristics**:
- **Technology**: 4G LTE, LTE-M, NB-IoT, 5G
- **Coverage**: Network dependent (carrier coverage)
- **Power**: Moderate (battery or AC powered)
- **Data Rate**: High (more than needed for vital signs)

**Advantages**:
- Works anywhere with cellular coverage
- No home WiFi setup needed
- Ideal for elderly or non-tech patients
- Real-time transmission

**Challenges**:
- Ongoing cellular service costs ($5-15/month)
- Coverage gaps in rural areas
- Power consumption

---

### Zigbee and Z-Wave

**Characteristics**:
- **Purpose**: Low-power mesh networks
- **Range**: 10-100 meters (mesh extends range)
- **Power**: Very low
- **Usage**: Home automation, less common in medical devices

**Medical Use**: Limited adoption in favor of BLE and WiFi

---

## Data Interoperability Standards

### HL7 FHIR (Fast Healthcare Interoperability Resources)

**Relevant Resources**:
- **Observation**: Vital signs (BP, glucose, weight, SpO2, temperature, HR)
- **Device**: Device information and metadata
- **Patient**: Patient demographics
- **Practitioner**: Provider information

**Example - Blood Pressure Observation**:
```json
{
  "resourceType": "Observation",
  "status": "final",
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/observation-category",
          "code": "vital-signs"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "85354-9",
        "display": "Blood pressure panel"
      }
    ]
  },
  "subject": {
    "reference": "Patient/12345"
  },
  "effectiveDateTime": "2025-01-15T10:30:00Z",
  "component": [
    {
      "code": {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "8480-6",
            "display": "Systolic blood pressure"
          }
        ]
      },
      "valueQuantity": {
        "value": 135,
        "unit": "mmHg",
        "system": "http://unitsofmeasure.org",
        "code": "mm[Hg]"
      }
    },
    {
      "code": {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "8462-4",
            "display": "Diastolic blood pressure"
          }
        ]
      },
      "valueQuantity": {
        "value": 85,
        "unit": "mmHg",
        "system": "http://unitsofmeasure.org",
        "code": "mm[Hg]"
      }
    }
  ]
}
```

---

### IEEE 11073 Personal Health Devices (PHD)

**Purpose**: Standard for personal health device communication

**Device Types**:
- 11073-10407: Blood pressure monitor
- 11073-10417: Glucose meter
- 11073-10441: Pulse oximeter
- 11073-10415: Weight scale
- 11073-10404: Body composition analyzer

**Transport**: Bluetooth Health Device Profile (HDP)

**Status**: Less widely adopted than FHIR, but used in some medical-grade devices

---

## Device Selection Criteria

### Clinical Considerations

**Accuracy**:
- FDA 510(k) clearance
- Clinical validation studies
- Meets ISO/AAMI standards

**Reliability**:
- Consistent data transmission
- Low failure rate
- Vendor track record

**Ease of Use**:
- One-button operation
- Clear instructions
- Minimal setup

**Patient Population**:
- Elderly: Larger displays, simpler operation, automatic transmission
- Tech-savvy: Smartphone apps, advanced features
- Pediatric: Child-friendly designs

---

### Technical Considerations

**Connectivity**:
- **WiFi**: Best for home-based, tech-comfortable patients
- **Bluetooth**: Good for smartphone users
- **Cellular**: Best for non-tech patients, rural areas

**Integration**:
- RPM platform compatibility
- EHR integration capability
- API availability

**Data Transmission Frequency**:
- Real-time: For high-acuity monitoring
- Daily: For routine chronic disease management
- On-demand: For symptom-based monitoring

---

### Economic Considerations

**Device Cost**:
- Purchase vs rental/subscription model
- Bulk pricing for programs
- Replacement/refurbishment costs

**Connectivity Costs**:
- Cellular plans ($5-15/device/month)
- WiFi (patient's existing network)
- Bluetooth (no ongoing cost)

**Total Cost of Ownership**:
- Device acquisition
- Connectivity
- Platform fees
- Support and maintenance
- Shipping and logistics

---

## Resources

### Standards Organizations
- **FDA**: Device clearance and guidance
- **ISO**: International device standards
- **IEEE**: 11073 PHD standards
- **HL7**: FHIR interoperability standards

### Industry Associations
- **HIMSS**: Connected health initiatives
- **Continua Health Alliance**: Device interoperability
- **Personal Connected Health Alliance**: Standards and certification

---

*Last Updated: 2025*
*Version: 1.0*

# Comprehensive Telecom Billing System Template

## Executive Summary

This template provides a complete architecture for telecommunications billing systems, integrating Business Support Systems (BSS) and Operations Support Systems (OSS) following TM Forum Frameworx standards. It covers both online and offline charging, real-time rating, convergent billing for multiple services, and revenue assurance mechanisms aligned with 3GPP specifications.

---

## 1. System Architecture Overview

### 1.1 BSS/OSS Architecture (TM Forum Frameworx)

The telecom billing system follows the TM Forum eTOM (enhanced Telecom Operations Map) framework:

```
┌─────────────────────────────────────────────────────────────────┐
│                      Customer Management Layer                   │
│        (CRM, Account Mgmt, Order Mgmt, Contract Mgmt)           │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    BSS (Business Support System)                 │
├─────────────────────────────────────────────────────────────────┤
│  ├─ Order Management System (OMS)                               │
│  ├─ Charging & Billing Engine                                   │
│  ├─ Mediation & CDR Processing                                  │
│  ├─ Revenue Assurance & Analytics                               │
│  └─ Customer Self-Service Portal                                │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    OSS (Operations Support System)               │
├─────────────────────────────────────────────────────────────────┤
│  ├─ Resource Provisioning                                       │
│  ├─ Performance Management                                      │
│  ├─ Fault Management                                            │
│  ├─ Configuration Management                                    │
│  └─ Service Activation & Deactivation                           │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Network Elements Layer                        │
│  (RAN, Core Network, Charging Systems, Signaling Nodes)         │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Charging System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Charging System                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         Online Charging System (OCS)                       │ │
│  │  - Real-time rating and balance checking                  │ │
│  │  - Diameter Gy interface (post-paid)                      │ │
│  │  - Diameter Ro interface (prepaid/quota)                  │ │
│  │  - Immediate quota allocation                            │ │
│  │  - Support for voice, data, SMS, VAS                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            ▲                                     │
│                            │                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │      Offline Charging System (OFCS)                       │ │
│  │  - Post-event charging from CDRs                          │ │
│  │  - Rating engine application                             │ │
│  │  - Usage record aggregation                              │ │
│  │  - Billing data generation                               │ │
│  │  - Tariff application                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         Rating & Pricing Engine                           │ │
│  │  - Dynamic tariff application                            │ │
│  │  - Promotional discount engine                           │ │
│  │  - Volume-based pricing                                  │ │
│  │  - Time-based discounts                                  │ │
│  │  - A/B number-based rules                                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │    Mediation & CDR Processing                            │ │
│  │  - CDR parsing and normalization                         │ │
│  │  - Data enrichment (location, tariff lookup)             │ │
│  │  - Fraud detection and cleansing                         │ │
│  │  - CDR consolidation and aggregation                     │ │
│  │  - Roaming handling and inter-operator billing           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Online Charging System (OCS)

### 2.1 Real-Time Charging Architecture

**Diameter Protocol Integration (RFC 6733, 3GPP TS 32.299)**

```
┌──────────────────────┐
│  User Equipment      │
│  (Mobile Device)     │
└──────────┬───────────┘
           │
           │ Voice/Data Session
           │
┌──────────▼───────────────────────────────┐
│  Network Element                         │
│  - GGSN/PGW (Packet Gateway)             │
│  - MSC-S (Mobile Switching Center)       │
│  - SGSN (Serving GPRS Support Node)      │
└──────────┬──────────────────────────────┘
           │
           │ Diameter Gy/Ro (Real-time charging)
           │
┌──────────▼─────────────────────────────────┐
│  Online Charging System (OCS)              │
│  ┌───────────────────────────────────────┐│
│  │ Charging Trigger Detection            ││
│  │ - Service activation/termination      ││
│  │ - Time-based triggers (5min, 1hr)    ││
│  │ - Volume-based triggers (10MB)       ││
│  │ - Event-based triggers                ││
│  └───────────────────────────────────────┘│
│  ┌───────────────────────────────────────┐│
│  │ Quota Management                      ││
│  │ - Quota request/response              ││
│  │ - Used units tracking                 ││
│  │ - Quota depletion handling            ││
│  │ - Tariff-based quota calculation     ││
│  └───────────────────────────────────────┘│
│  ┌───────────────────────────────────────┐│
│  │ Balance Checking                      ││
│  │ - Account balance lookup              ││
│  │ - Credit limit validation             ││
│  │ - Rating rule application             ││
│  │ - Real-time balance deduction        ││
│  └───────────────────────────────────────┘│
└──────────┬──────────────────────────────┘
           │
           │ Credit-Control-Request/Answer
           │ (CCR/CCA)
           │
           ▼
```

### 2.2 Diameter CCR/CCA Message Structure

**Credit-Control-Request (CCR):**

```json
{
  "session_id": "session123456@operator.com",
  "origin_host": "pgw.operator.com",
  "origin_realm": "operator.com",
  "destination_realm": "operator.com",
  "auth_application_id": 4,
  "service_context_id": "32260@3gpp.org",
  "cc_request_type": "INITIAL_REQUEST",
  "cc_request_number": 0,
  "subscription_id": {
    "subscription_id_type": "END_USER_IMSI",
    "subscription_id_data": "310410123456789"
  },
  "called_station_id": "http://www.example.com",
  "service_identifier": 1,
  "rating_group": 10,
  "requested_service_unit": {
    "cc_time": 3600,
    "cc_money": {
      "unit_value": 1000,
      "currency_code": 840
    },
    "cc_total_octets": 1073741824
  },
  "multiple_services_indicator": "MULTIPLE_SERVICES_NOT_SUPPORTED",
  "user_equipment_info": {
    "user_equipment_type": "IMEISV",
    "user_equipment_value": "355317051234567890"
  },
  "timestamp": "2025-11-19T10:30:00Z"
}
```

**Credit-Control-Answer (CCA):**

```json
{
  "session_id": "session123456@operator.com",
  "result_code": 2001,
  "origin_host": "ocs.operator.com",
  "origin_realm": "operator.com",
  "auth_application_id": 4,
  "cc_request_type": "INITIAL_REQUEST",
  "cc_request_number": 0,
  "granted_service_unit": {
    "cc_time": 3600,
    "cc_money": {
      "unit_value": 1000,
      "currency_code": 840
    },
    "cc_total_octets": 1073741824
  },
  "cost_information": {
    "unit_value": 50,
    "currency_code": 840
  },
  "final_unit_indication": {
    "final_unit_action": "TERMINATE"
  },
  "validity_time": 3600,
  "multiple_services_indicator": "MULTIPLE_SERVICES_NOT_SUPPORTED",
  "timestamp": "2025-11-19T10:30:05Z"
}
```

### 2.3 OCS API Example (REST Interface)

```python
# Real-time Charging Request
POST /api/v1/charging/authorize
Content-Type: application/json

{
  "msisdn": "+11234567890",
  "imsi": "310410123456789",
  "service_type": "DATA",
  "requested_units": {
    "volume_mb": 100,
    "duration_seconds": 3600
  },
  "rating_group": 10,
  "service_context": "IMS_Data_Service",
  "user_location": {
    "mcc": "310",
    "mnc": "410",
    "lac": "12345",
    "ci": "67890"
  }
}

# OCS Response
HTTP/1.1 200 OK
{
  "result": "GRANTED",
  "allocated_units": {
    "volume_mb": 100,
    "duration_seconds": 3600,
    "monetary_value": 5.00
  },
  "validity_duration": 3600,
  "cost_per_unit": {
    "data_mb": 0.05,
    "voice_minute": 0.10,
    "sms_unit": 0.01
  },
  "charging_rules": [
    {
      "rule_id": "DATA_STANDARD",
      "priority": 10,
      "rating_group": 10,
      "metering_method": "VOLUME",
      "sdf_filter": "permit in ip from any to any"
    }
  ],
  "session_timeout": 3600,
  "grace_period": 300
}
```

---

## 3. Offline Charging System (OFCS)

### 3.1 CDR Processing Pipeline

```
┌────────────────────────┐
│  Network Elements      │
│  CDR Generation        │
│  (MSC, GGSN, etc)      │
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────────────────┐
│  CDR Collection & Transport        │
│  - FTP/SFTP Transfer               │
│  - SOAP Web Services               │
│  - File staging area               │
└──────────┬─────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│  Mediation System                  │
│  ┌──────────────────────────────┐ │
│  │ CDR Parsing & Normalization  │ │
│  │ - Format conversion (ASN.1)  │ │
│  │ - Field extraction           │ │
│  │ - Timestamp normalization    │ │
│  └──────────────────────────────┘ │
│  ┌──────────────────────────────┐ │
│  │ Data Enrichment              │ │
│  │ - Tariff lookup              │ │
│  │ - Location information       │ │
│  │ - Subscriber classification  │ │
│  │ - Network route tagging      │ │
│  └──────────────────────────────┘ │
│  ┌──────────────────────────────┐ │
│  │ Fraud Detection              │ │
│  │ - Anomaly detection          │ │
│  │ - Pattern matching           │ │
│  │ - Duplicate detection        │ │
│  │ - Volume threshold alerts    │ │
│  └──────────────────────────────┘ │
└──────────┬─────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│  Rating Engine                     │
│  - Apply tariffs                   │
│  - Calculate charges               │
│  - Apply discounts/promotions      │
│  - Handle roaming agreements       │
└──────────┬─────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│  Billing Data Generation           │
│  - Usage aggregation               │
│  - Account consolidation           │
│  - Invoice item creation           │
│  - Dispute handling                │
└──────────┬─────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│  Billing System                    │
│  - Invoice generation              │
│  - Payment processing              │
│  - Account aging                   │
│  - Dunning management              │
└────────────────────────────────────┘
```

### 3.2 CDR Record Structure (3GPP TS 32.298)

```asn1
-- Abstracted CDR Record Structure
MobilityCallRecord ::= SEQUENCE {
  recordType              [0] INTEGER,
  servedIMSI              [1] OCTET STRING,
  servedIMEI              [2] OCTET STRING,
  servedMSISDN            [3] OCTET STRING,
  callingNumber           [4] OCTET STRING OPTIONAL,
  calledNumber            [5] OCTET STRING OPTIONAL,
  timeOfFirstUsage        [6] GeneralizedTime,
  timeOfLastUsage         [7] GeneralizedTime,
  callDuration            [8] INTEGER,
  callEventStartTime      [9] GeneralizedTime,
  totalCallDuration       [10] INTEGER,
  causeForTermination     [11] INTEGER,
  diagnostics             [12] INTEGER OPTIONAL,
  recordSequenceNumber    [13] INTEGER,
  nodeID                  [14] OCTET STRING,
  localSequenceNumber     [15] INTEGER,
  chargingCharacteristics [16] OCTET STRING OPTIONAL,
  chargingID              [17] INTEGER,
  productID               [18] INTEGER OPTIONAL,
  accessPointNameNI       [19] OCTET STRING OPTIONAL,
  dataVolumeDownlink      [20] INTEGER,
  dataVolumeUplink        [21] INTEGER,
  serviceKey              [22] INTEGER,
  ratingGroup             [23] INTEGER,
  locationArea            [24] OCTET STRING OPTIONAL,
  cellIdentifier          [25] OCTET STRING OPTIONAL,
  exchangeIdentifier      [26] OCTET STRING OPTIONAL
}
```

### 3.3 CDR JSON Format

```json
{
  "cdr_id": "CDR_20251119_001234567",
  "call_record": {
    "record_type": "VOICE",
    "served_imsi": "310410123456789",
    "served_msisdn": "+11234567890",
    "calling_number": "+11234567890",
    "called_number": "+19876543210",
    "call_start_time": "2025-11-19T10:30:00Z",
    "call_end_time": "2025-11-19T10:35:45Z",
    "call_duration_seconds": 345,
    "network_element": "MSC_001",
    "cause_for_termination": "NORMAL",
    "charging_characteristics": "12AB",
    "service_key": 1,
    "rating_group": 10,
    "location_area_code": "12345",
    "cell_identifier": "67890",
    "access_technology": "2G"
  },
  "data_record": {
    "record_type": "DATA",
    "served_imsi": "310410123456789",
    "served_msisdn": "+11234567890",
    "session_start_time": "2025-11-19T10:30:00Z",
    "session_end_time": "2025-11-19T10:35:00Z",
    "session_duration_seconds": 300,
    "data_volume_downlink_bytes": 5242880,
    "data_volume_uplink_bytes": 1048576,
    "access_point_name": "internet",
    "network_element": "GGSN_001",
    "charging_id": "12345",
    "rating_group": 20,
    "cause_for_termination": "NORMAL"
  },
  "mediation_metadata": {
    "processed_timestamp": "2025-11-19T10:40:00Z",
    "tariff_version": "2025_11_19_V1",
    "applied_discount": {
      "code": "LOYALTY_10PCT",
      "percentage": 10.0,
      "reason": "Customer loyalty program"
    },
    "fraud_score": 0.12,
    "fraud_status": "NORMAL",
    "enrichment_status": "COMPLETE"
  }
}
```

---

## 4. Rating and Pricing Engine

### 4.1 Tariff Configuration

```json
{
  "tariff_id": "TARIFF_2025_11_V1",
  "effective_date": "2025-11-01",
  "expiry_date": "2025-12-31",
  "currency": "USD",
  "rating_rules": [
    {
      "rule_id": "VOICE_STANDARD",
      "service_type": "VOICE",
      "rating_group": 10,
      "charging_method": "TIME_BASED",
      "rates": [
        {
          "time_band": "PEAK",
          "hours": "08:00-18:00",
          "days": "MON-FRI",
          "rate_per_minute": 0.10
        },
        {
          "time_band": "OFF_PEAK",
          "hours": "18:00-08:00",
          "days": "MON-FRI,SAT-SUN",
          "rate_per_minute": 0.05
        }
      ],
      "minimum_chargeable_unit": "SIXSECONDS",
      "rounding_method": "ROUND_UP"
    },
    {
      "rule_id": "DATA_STANDARD",
      "service_type": "DATA",
      "rating_group": 20,
      "charging_method": "VOLUME_BASED",
      "rates": [
        {
          "volume_from_mb": 0,
          "volume_to_mb": 100,
          "rate_per_mb": 0.05
        },
        {
          "volume_from_mb": 101,
          "volume_to_mb": 1000,
          "rate_per_mb": 0.03
        },
        {
          "volume_from_mb": 1001,
          "volume_to_mb": 999999,
          "rate_per_mb": 0.01
        }
      ]
    },
    {
      "rule_id": "SMS_STANDARD",
      "service_type": "SMS",
      "rating_group": 30,
      "charging_method": "UNIT_BASED",
      "rate_per_sms": 0.01,
      "local_sms": true,
      "local_sms_rate": 0.01,
      "international_sms": true,
      "international_sms_rate": 0.15
    }
  ],
  "promotional_rules": [
    {
      "promo_id": "LOYALTY_DISCOUNT",
      "promo_name": "Loyalty Program 10%",
      "discount_type": "PERCENTAGE",
      "discount_value": 10.0,
      "eligible_customers": "POSTPAID_VIP",
      "start_date": "2025-11-01",
      "end_date": "2025-12-31",
      "max_discount_per_month": 50.00
    },
    {
      "promo_id": "BUNDLE_VOICE_DATA",
      "promo_name": "Voice + Data Bundle",
      "bundle_services": ["VOICE", "DATA"],
      "bundle_price": 29.99,
      "included_units": {
        "VOICE_MINUTES": 200,
        "DATA_MB": 5000
      }
    }
  ]
}
```

### 4.2 Dynamic Rating Engine API

```python
# Request: Calculate charge for a call
POST /api/v1/rating/calculate-charge
Content-Type: application/json

{
  "call_details": {
    "msisdn": "+11234567890",
    "called_party": "+19876543210",
    "start_time": "2025-11-19T14:30:00Z",
    "end_time": "2025-11-19T14:35:45Z",
    "duration_seconds": 345,
    "service_type": "VOICE",
    "network_element": "MSC_001",
    "location": {
      "mcc": "310",
      "mnc": "410",
      "lac": "12345"
    },
    "customer_type": "POSTPAID_VIP",
    "tariff_version": "2025_11_19_V1"
  }
}

# Response: Pricing calculation
HTTP/1.1 200 OK
{
  "charge_id": "CHG_20251119_001",
  "base_charge": {
    "amount": 0.575,
    "currency": "USD",
    "calculation_details": {
      "chargeable_duration": "5.75 minutes",
      "rate_applied": "0.10 USD/minute (PEAK)",
      "minimum_unit_applied": "6 seconds"
    }
  },
  "discount_details": [
    {
      "discount_id": "LOYALTY_DISCOUNT",
      "discount_name": "Loyalty Program 10%",
      "discount_amount": 0.0575,
      "discount_percentage": 10.0
    }
  ],
  "total_charge": 0.52,
  "currency": "USD",
  "tax": 0.05,
  "final_amount": 0.57,
  "tariff_version_applied": "2025_11_19_V1",
  "timestamp": "2025-11-19T14:36:00Z"
}
```

---

## 5. Convergent Billing

### 5.1 Multi-Service Billing Integration

```
┌─────────────────────────────────────────────────────────────┐
│         Convergent Billing System (CBS)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Voice Services           Data Services       SMS/VAS      │
│  ├─ Landline calls       ├─ Broadband       ├─ SMS         │
│  ├─ Mobile calls         ├─ Mobile data     ├─ MMS         │
│  ├─ IDD (Intl)           ├─ WiMAX           ├─ USSD        │
│  └─ Premium numbers      └─ Cloud storage   └─ Call waiting│
│         │                      │                   │        │
│         └──────────┬───────────┴───────────────────┘        │
│                    │                                        │
│         ┌──────────▼───────────┐                            │
│         │  Unified Rating      │                            │
│         │  Engine              │                            │
│         │  - Cross-service     │                            │
│         │    aggregation       │                            │
│         │  - Bundle pricing    │                            │
│         │  - Family plans      │                            │
│         └──────────┬───────────┘                            │
│                    │                                        │
│         ┌──────────▼───────────┐                            │
│         │  Account Ledger      │                            │
│         │  - Debit account     │                            │
│         │  - Credit account    │                            │
│         │  - Suspense account  │                            │
│         │  - Revenue account   │                            │
│         └──────────┬───────────┘                            │
│                    │                                        │
│         ┌──────────▼───────────┐                            │
│         │  Invoice Generation  │                            │
│         │  - Line items        │                            │
│         │  - Tax calculation   │                            │
│         │  - PDF rendering     │                            │
│         │  - Multi-language    │                            │
│         └──────────────────────┘                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Account Ledger Structure

```json
{
  "account_id": "ACC_20251119_123456",
  "msisdn": "+11234567890",
  "customer_id": "CUST_987654",
  "billing_cycle": "2025_11_01_2025_11_30",
  "ledger_entries": [
    {
      "entry_id": 1,
      "entry_date": "2025-11-05",
      "service_type": "VOICE",
      "description": "Voice calls - Peak hours",
      "quantity": 245,
      "unit": "minutes",
      "unit_price": 0.10,
      "subtotal": 24.50,
      "tax_code": "VOICE_TAX",
      "tax_amount": 2.45,
      "total": 26.95
    },
    {
      "entry_id": 2,
      "entry_date": "2025-11-05",
      "service_type": "VOICE",
      "description": "Voice calls - Off-peak hours",
      "quantity": 120,
      "unit": "minutes",
      "unit_price": 0.05,
      "subtotal": 6.00,
      "tax_code": "VOICE_TAX",
      "tax_amount": 0.60,
      "total": 6.60
    },
    {
      "entry_id": 3,
      "entry_date": "2025-11-10",
      "service_type": "DATA",
      "description": "Mobile data",
      "quantity": 2500,
      "unit": "MB",
      "unit_price": 0.03,
      "subtotal": 75.00,
      "tax_code": "DATA_TAX",
      "tax_amount": 7.50,
      "total": 82.50
    },
    {
      "entry_id": 4,
      "entry_date": "2025-11-15",
      "service_type": "SMS",
      "description": "SMS messages",
      "quantity": 150,
      "unit": "SMS",
      "unit_price": 0.01,
      "subtotal": 1.50,
      "tax_code": "SMS_TAX",
      "tax_amount": 0.15,
      "total": 1.65
    },
    {
      "entry_id": 5,
      "entry_date": "2025-11-20",
      "service_type": "PROMOTION",
      "description": "Loyalty discount (10%)",
      "discount_percentage": 10.0,
      "discount_amount": -11.16,
      "total": -11.16
    }
  ],
  "summary": {
    "subtotal_services": 106.50,
    "total_discounts": -11.16,
    "taxable_amount": 95.34,
    "total_tax": 10.70,
    "total_amount_due": 106.04,
    "previous_balance": 0.00,
    "total_payable": 106.04,
    "due_date": "2025-12-10"
  }
}
```

---

## 6. Real-Time Charging Interfaces

### 6.1 Diameter Ro Interface (Prepaid)

```
User Equipment              Network Element              OCS
      │                           │                       │
      │────Call Attempt───────────│                       │
      │                           │                       │
      │                           │──CCR (INITIAL)───────>│
      │                           │<───CCA (GRANTED)──────│
      │                           │                       │
      │◄──────Call Granted────────│                       │
      │                           │                       │
      │◄───────Call Connected─────│                       │
      │                           │                       │
      │                    [Periodic Updates]             │
      │                           │──CCR (UPDATE)───────>│
      │                           │<───CCA (UPDATED)──────│
      │                           │                       │
      │────End Call───────────────│                       │
      │                           │──CCR (TERMINATE)────>│
      │                           │<───CCA (FINAL)────────│
      │                           │                       │
```

**CCR (INITIAL) - Prepaid Quota Request:**
```json
{
  "cc_request_type": "INITIAL_REQUEST",
  "called_station_id": "+19876543210",
  "requested_service_unit": {
    "cc_time": 3600,
    "cc_total_octets": 1073741824
  },
  "service_identifier": 1,
  "rating_group": 10,
  "subscription_id": {
    "subscription_id_type": "END_USER_IMSI",
    "subscription_id_data": "310410123456789"
  }
}
```

**CCA (GRANTED) - Quota Allocation:**
```json
{
  "result_code": 2001,
  "granted_service_unit": {
    "cc_time": 600,
    "cc_total_octets": 536870912
  },
  "validity_time": 600,
  "cost_information": {
    "unit_value": 50,
    "currency_code": 840
  }
}
```

### 6.2 Diameter Gy Interface (Postpaid - Credit Control)

```
┌─────────────────────────────────────────────────────┐
│  Credit Control Request (CCR) - Gy Interface        │
├─────────────────────────────────────────────────────┤
│  Session-Id              │ Unique session ID        │
│  Auth-Application-Id     │ Credit Control (4)       │
│  CC-Request-Type         │ INITIAL_REQUEST          │
│  CC-Request-Number       │ Sequence number          │
│  Subscription-Id         │ MSISDN/IMSI              │
│  Service-Context-Id      │ Service identifier       │
│  Called-Station-Id       │ Called number            │
│  Service-Identifier      │ Service type ID          │
│  Rating-Group            │ Tariff class             │
│  Requested-Service-Unit  │ Requested quota          │
│  Multiple-Services-Ind   │ Multiple services flag   │
│  User-Equipment-Info     │ Device IMEI/IMEISV      │
│  3GPP-User-Location-Info │ Cell location            │
│  3GPP-Charging-Char      │ Charging characteristics │
└─────────────────────────────────────────────────────┘

        │
        │ Real-time rating & balance check
        │
        ▼

┌─────────────────────────────────────────────────────┐
│  Credit Control Answer (CCA) - Gy Interface         │
├─────────────────────────────────────────────────────┤
│  Result-Code             │ Success (2001)           │
│  Granted-Service-Unit    │ Allocated quota          │
│  Cost-Information        │ Cost of allocated quota  │
│  Final-Unit-Indication   │ Final quota warning      │
│  Validity-Time           │ Quota validity duration  │
│  Multiple-Services-Ind   │ Multiple services flag   │
│  Redirect-Host           │ Alternative OCS (if any)│
│  Service-Parameter-Info  │ Rate parameters         │
└─────────────────────────────────────────────────────┘
```

---

## 7. Revenue Assurance and Fraud Detection

### 7.1 Fraud Detection Mechanisms

```
┌──────────────────────────────────────────────────────────┐
│         Fraud Detection System                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Real-Time Anomaly Detection                       │ │
│  │ - Sudden volume spike (10x normal usage)          │ │
│  │ - International roaming rate jumps                │ │
│  │ - Concurrent sessions (impossible roaming)        │ │
│  │ - Premium number calling patterns                 │ │
│  │ - Account takeover indicators                     │ │
│  │ - Velocity checks (rapid subscriber activation)   │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Pattern-Based Detection (ML)                      │ │
│  │ - Usage pattern clustering                        │ │
│  │ - Anomaly scoring (Random Forest)                 │ │
│  │ - Time-series analysis                            │ │
│  │ - Network analysis (call graph anomalies)         │ │
│  │ - Behavior profiling                              │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Revenue Assurance Checks                          │ │
│  │ - CDR completeness audit (no missing records)     │ │
│  │ - Billing accuracy verification                   │ │
│  │ - Network vs billing reconciliation               │ │
│  │ - Roaming agreement compliance                    │ │
│  │ - Duplicate detection                             │ │
│  │ - Data integrity validation                       │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Action & Response                                 │ │
│  │ - Immediate session suspension                    │ │
│  │ - Fraud alert to security team                    │ │
│  │ - Account lockdown                                │ │
│  │ - Investigation task creation                     │ │
│  │ - Chargeback prevention                           │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 7.2 Fraud Detection API

```python
# Fraud scoring request
POST /api/v1/fraud/assess-risk
Content-Type: application/json

{
  "subscriber_id": "CUST_987654",
  "msisdn": "+11234567890",
  "event_type": "DATA_USAGE_SPIKE",
  "event_details": {
    "current_usage_mb": 5000,
    "expected_usage_mb": 500,
    "time_period": "24_hours",
    "previous_month_avg_mb": 450,
    "increase_percentage": 1000
  },
  "behavioral_context": {
    "account_age_days": 45,
    "previous_fraud_incidents": 0,
    "device_change_recent": false,
    "location_change_recent": true,
    "roaming_status": "INTERNATIONAL_ROAMING"
  },
  "network_context": {
    "current_cell": "LOCATION_MANILA_PH",
    "home_location": "NEW_YORK_USA",
    "time_since_arrival": 2,
    "concurrent_sessions": 3
  }
}

# Fraud risk response
HTTP/1.1 200 OK
{
  "assessment_id": "FRAUD_ASSESS_20251119_001",
  "fraud_score": 0.87,
  "risk_level": "HIGH",
  "risk_factors": [
    {
      "factor": "Excessive data usage",
      "contribution": 0.35,
      "weight": "HIGH"
    },
    {
      "factor": "Concurrent sessions from different locations",
      "contribution": 0.28,
      "weight": "HIGH"
    },
    {
      "factor": "International roaming in high-fraud country",
      "contribution": 0.18,
      "weight": "MEDIUM"
    },
    {
      "factor": "New account age",
      "contribution": 0.06,
      "weight": "LOW"
    }
  ],
  "recommended_actions": [
    {
      "action": "SESSION_SUSPENSION",
      "priority": "IMMEDIATE",
      "reason": "High fraud risk detected"
    },
    {
      "action": "ALERT_SECURITY_TEAM",
      "priority": "IMMEDIATE",
      "escalation_level": "SENIOR"
    },
    {
      "action": "CUSTOMER_VERIFICATION",
      "priority": "HIGH",
      "method": "OTP_SMS"
    }
  ],
  "timestamp": "2025-11-19T15:30:00Z"
}
```

### 7.3 Revenue Assurance KPIs

```json
{
  "ra_dashboard": {
    "reporting_period": "2025_11_01_2025_11_30",
    "kpis": {
      "cdr_completeness": {
        "expected_cdr_count": 25000000,
        "actual_cdr_count": 24987500,
        "missing_cdr_count": 12500,
        "completeness_percentage": 99.95,
        "threshold": 99.9,
        "status": "PASS"
      },
      "billing_accuracy": {
        "sampled_bills": 5000,
        "accurate_bills": 4987,
        "billing_error_rate": 0.26,
        "threshold": 0.5,
        "status": "PASS"
      },
      "network_billing_reconciliation": {
        "network_reported_revenue": 5234567.89,
        "billing_system_revenue": 5234123.45,
        "variance_amount": 444.44,
        "variance_percentage": 0.0085,
        "threshold": 0.05,
        "status": "PASS"
      },
      "roaming_agreement_compliance": {
        "agreements_checked": 45,
        "compliant_agreements": 44,
        "non_compliant": 1,
        "compliance_percentage": 97.78,
        "threshold": 98.0,
        "status": "FAIL"
      },
      "duplicate_detection": {
        "total_cdr_checked": 25000000,
        "duplicates_found": 2350,
        "duplicate_rate": 0.0094,
        "duplicate_amount_usd": 3145.67,
        "status": "ALERT"
      }
    }
  }
}
```

---

## 8. CRM and ERP Integration

### 8.1 Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Telecom Billing System                   │
│         (OCS, OFCS, Rating, Mediation, Billing)             │
└────────┬─────────────────────────────────────────────────────┘
         │
    ┌────┴────┬──────────────┬──────────────┬──────────┐
    │          │              │              │          │
    ▼          ▼              ▼              ▼          ▼
┌────────┐ ┌────────┐ ┌─────────────┐ ┌─────────┐ ┌────────┐
│  CRM   │ │ ERP    │ │ Data        │ │  DW/BI  │ │ Revenue│
│System  │ │System  │ │ Lake        │ │System   │ │Mgmt    │
│        │ │        │ │             │ │         │ │        │
│Cust    │ │Finance │ │ Historical  │ │Analytics│ │Reporting
│Account │ │GL/AP   │ │ CDRs        │ │Reports  │ │& Control
│Contact │ │AR/PO   │ │ Usage       │ │eTOM KPI │ │Audits
│Orders  │ │Budget  │ │ Ratings     │ │ Billing │ │        │
│        │ │        │ │ Fraud data  │ │ metrics │ │        │
└────────┘ └────────┘ └─────────────┘ └─────────┘ └────────┘
```

### 8.2 CRM Integration APIs

```python
# Customer data synchronization
POST /api/v1/integration/crm/sync-customer
Content-Type: application/json

{
  "sync_type": "CUSTOMER_UPDATE",
  "customer_id": "CUST_987654",
  "billing_details": {
    "account_status": "ACTIVE",
    "credit_limit": 5000.00,
    "payment_method": "CREDIT_CARD",
    "autopay_enabled": true,
    "billing_address": {
      "street": "123 Main St",
      "city": "New York",
      "state": "NY",
      "zip": "10001",
      "country": "US"
    }
  },
  "service_subscriptions": [
    {
      "service_code": "VOICE_UNLIMITED",
      "plan_name": "Unlimited Voice",
      "monthly_fee": 29.99,
      "activation_date": "2025-09-01",
      "auto_renewal": true
    },
    {
      "service_code": "DATA_5GB",
      "plan_name": "5GB Data Bundle",
      "monthly_fee": 15.99,
      "activation_date": "2025-09-01",
      "auto_renewal": true
    }
  ],
  "notification_preferences": {
    "email_notifications": true,
    "sms_notifications": false,
    "preferred_contact_method": "EMAIL",
    "language": "en_US"
  },
  "metadata": {
    "sync_timestamp": "2025-11-19T16:00:00Z",
    "source_system": "BILLING",
    "request_id": "REQ_20251119_001"
  }
}

# CRM Response
HTTP/1.1 200 OK
{
  "sync_id": "SYNC_20251119_001",
  "status": "SUCCESS",
  "customer_id": "CUST_987654",
  "synchronized_fields": [
    "account_status",
    "credit_limit",
    "service_subscriptions",
    "billing_address"
  ],
  "timestamp": "2025-11-19T16:00:05Z"
}
```

### 8.3 ERP Integration for Accounting

```python
# Revenue and receivables posting to ERP
POST /api/v1/integration/erp/post-revenue
Content-Type: application/json

{
  "posting_id": "POST_20251119_001",
  "posting_date": "2025-11-30",
  "accounting_period": "2025_11",
  "journal_entries": [
    {
      "entry_id": 1,
      "description": "Service revenue - Voice",
      "account_number": "4100",
      "account_description": "Voice Service Revenue",
      "debit": 0.00,
      "credit": 24567.89,
      "reference": "BILLING_2025_11",
      "quantity_units": 98765,
      "quantity_description": "Minutes"
    },
    {
      "entry_id": 2,
      "description": "Service revenue - Data",
      "account_number": "4110",
      "account_description": "Data Service Revenue",
      "debit": 0.00,
      "credit": 15432.10,
      "reference": "BILLING_2025_11",
      "quantity_units": 5432,
      "quantity_description": "GB"
    },
    {
      "entry_id": 3,
      "description": "Service revenue - SMS/VAS",
      "account_number": "4120",
      "account_description": "SMS/VAS Revenue",
      "debit": 0.00,
      "credit": 3210.99,
      "reference": "BILLING_2025_11",
      "quantity_units": 321099,
      "quantity_description": "Units"
    },
    {
      "entry_id": 4,
      "description": "Accounts Receivable",
      "account_number": "1200",
      "account_description": "Accounts Receivable - Telecom",
      "debit": 43211.04,
      "credit": 0.00,
      "reference": "BILLING_2025_11"
    },
    {
      "entry_id": 5,
      "description": "Bad debt provision",
      "account_number": "5110",
      "account_description": "Bad Debt Expense",
      "debit": 432.11,
      "credit": 0.00,
      "reference": "BILLING_2025_11"
    },
    {
      "entry_id": 6,
      "description": "Allowance for doubtful accounts",
      "account_number": "1205",
      "account_description": "Allowance for Doubtful Accounts",
      "debit": 0.00,
      "credit": 432.11,
      "reference": "BILLING_2025_11"
    }
  ],
  "total_debit": 43643.15,
  "total_credit": 43643.15,
  "currency": "USD"
}

# ERP Acknowledgment
HTTP/1.1 201 CREATED
{
  "posting_id": "POST_20251119_001",
  "erp_posting_id": "JE_2025_11_00001234",
  "status": "POSTED",
  "timestamp": "2025-11-30T23:59:59Z"
}
```

---

## 9. 3GPP Charging Specifications

### 9.1 TS 32.240-32.298 Compliance

**TS 32.240 - Charging Architecture and Principles**

- Charging system consists of OCS and OFCS
- Charging Trigger Function (CTF) generates charging events
- Charging Gateway Function (CGF) collects and processes CDRs
- Billing System (BS) generates invoices
- Off-line Charging System (OFCS) generates charging data records (CDRs)
- Online Charging System (OCS) provides real-time credit management

**TS 32.250 - Charging data description for the GPRS**

- GPRS CDR format with service data flow filters
- Usage data records (UDRs) for session-level charging
- Time, volume, and event-based triggers

**TS 32.260 - IMS Charging**

- IMS-specific CDR formats
- SIP session characteristics
- Media handling and QoS parameters
- Application level charging

**TS 32.270 - Multimedia Messaging Service (MMS) Charging**

- MMS-specific charge elements
- Recipient-based charging
- Content size charging
- Download charging

**TS 32.280 - Rich Communication Services (RCS) Charging**

- RCS session charging
- File transfer charging
- Group messaging charging
- Presence-based charging

**TS 32.298 - Charging Data Record (CDR) File Format**

- Binary File Format (BFF) for CDR encoding
- Automatic Encoding Rules (aligned with ASN.1)
- CDR data element definitions
- File packaging and security

### 9.2 CDR Data Elements (TS 32.298)

```
Basic Data Elements:
├─ IMSI/MSISDN (subscriber identification)
├─ IMEI/IMEISV (device identification)
├─ Charging ID (logical charging identifier)
├─ Event Timestamp (call/session start/end)
├─ Service Key (service type identifier)
├─ Rating Group (tariff classification)
├─ Cause for Termination (call/session end reason)
├─ Access Point Name (APN for data services)
├─ Called/Calling Number
└─ Service-Specific Data Elements

Charging Characteristics:
├─ Normal charging
├─ Prepaid charging
├─ Postpaid charging
├─ Forwarded to roaming partner
└─ Forwarded to third-party operator

Location Information:
├─ Location Area Code (LAC)
├─ Cell Identity (CI)
├─ Service Area Code (SAC)
├─ Extended Service Area Code (ESAC)
├─ Tracking Area Code (TAC) - LTE
└─ Geographic coordinates (optionally)

Service-Specific Elements:
├─ Data Volume (DL/UL octets)
├─ Call Duration (seconds)
├─ Quality of Service (QoS) class
├─ Network element address
├─ Change of Charging Condition (ChChC)
└─ Exchange Identifier (for roaming)
```

---

## 10. Mediation and CDR Processing

### 10.1 CDR Flow and Transformation

```
┌──────────────────────────┐
│  Network Elements        │
│  ┌────────────────────┐ │
│  │ MSC/VLR (Voice)    │ │
│  │ GGSN/PGW (Data)    │ │
│  │ SGSN (Mobility)    │ │
│  │ HLR/HSS (Auth)     │ │
│  └────────────────────┘ │
└──────────┬───────────────┘
           │ CDR Generation
           │ (Proprietary Format)
           │
    ┌──────▼────────┐
    │ CDR Collection│
    │ (FTP/SFTP)    │
    └──────┬────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Mediation System                    │
├──────────────────────────────────────┤
│                                      │
│ ┌────────────────────────────────┐  │
│ │ Format Conversion              │  │
│ │ Proprietary → Standard Format  │  │
│ │ (ASN.1 BER, JSON, XML)        │  │
│ └────────────────────────────────┘  │
│                  │                   │
│ ┌────────────────▼────────────────┐  │
│ │ Data Normalization              │  │
│ │ - Timestamp alignment           │  │
│ │ - IMSI padding                  │  │
│ │ - Number formatting             │  │
│ │ - Duration rounding             │  │
│ └────────────────────────────────┘  │
│                  │                   │
│ ┌────────────────▼────────────────┐  │
│ │ Data Enrichment                 │  │
│ │ - Tariff lookup                 │  │
│ │ - Customer classification       │  │
│ │ - Location information          │  │
│ │ - Network routing data          │  │
│ │ - Promotional rules             │  │
│ └────────────────────────────────┘  │
│                  │                   │
│ ┌────────────────▼────────────────┐  │
│ │ Data Validation                 │  │
│ │ - Field completeness            │  │
│ │ - Data type checking            │  │
│ │ - Range validation              │  │
│ │ - Duplicate detection           │  │
│ │ - Fraud indicators              │  │
│ └────────────────────────────────┘  │
│                  │                   │
│ ┌────────────────▼────────────────┐  │
│ │ Quality Assurance               │  │
│ │ - Completeness audit            │  │
│ │ - Volume reconciliation         │  │
│ │ - CDR correlation               │  │
│ │ - Anomaly detection             │  │
│ └────────────────────────────────┘  │
│                                      │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Standardized CDR Records            │
│  (Ready for Rating/Billing)          │
└──────────────────────────────────────┘
```

### 10.2 Mediation API

```python
# CDR Processing Request
POST /api/v1/mediation/process-cdrs
Content-Type: application/json

{
  "batch_id": "BATCH_20251119_001",
  "file_name": "msc_cdr_20251119.tar.gz",
  "file_size_bytes": 524288000,
  "source_element": "MSC_001",
  "cdr_format": "PROPRIETARY_BIN",
  "target_format": "JSON",
  "processing_rules": {
    "enrichment_enabled": true,
    "fraud_detection_enabled": true,
    "duplicate_check_enabled": true,
    "validation_strict_mode": false
  },
  "routing": {
    "destination": "OFCS_RATING",
    "callback_url": "https://billing.operator.com/callbacks/batch_status"
  }
}

# Mediation Response
HTTP/1.1 202 ACCEPTED
{
  "batch_id": "BATCH_20251119_001",
  "processing_job_id": "JOB_20251119_001",
  "status": "PROCESSING",
  "expected_cdr_count": 250000,
  "processed_count": 0,
  "error_count": 0,
  "estimated_completion_time": "2025-11-19T17:30:00Z",
  "progress_percentage": 0
}

# Status Check
GET /api/v1/mediation/batch-status/BATCH_20251119_001

# Response
HTTP/1.1 200 OK
{
  "batch_id": "BATCH_20251119_001",
  "status": "COMPLETED",
  "total_cdr_count": 250000,
  "processed_count": 250000,
  "error_count": 125,
  "error_percentage": 0.05,
  "success_percentage": 99.95,
  "processing_duration_seconds": 1800,
  "result_summary": {
    "total_value_usd": 125432.10,
    "average_record_value": 0.50,
    "fraud_flagged_count": 45,
    "duplicates_found": 15
  },
  "output_files": {
    "valid_cdrs": "OUTPUT_20251119_001_VALID.json.gz",
    "error_records": "OUTPUT_20251119_001_ERROR.json.gz",
    "enrichment_report": "OUTPUT_20251119_001_ENRICHMENT.csv"
  },
  "timestamp": "2025-11-19T17:30:00Z"
}
```

---

## 11. Data Flow Diagrams

### 11.1 Complete End-to-End Charging Flow

```
User      Network      Billing     Rating      Invoice
 │            │            │          │            │
 │─ Call ────>│            │          │            │
 │            │            │          │            │
 │            │─ CDR Gen ──>│          │            │
 │            │            │          │            │
 │            │            │─ Mediate>│            │
 │            │            │          │            │
 │            │            │          │─ Rate ───>│
 │            │            │          │            │
 │            │            │          │<─ Amount ──│
 │            │            │          │            │
 │            │            │<─ Charge ─          │
 │            │            │            │         │
 │<─ Rating ──│            │            │         │
 │ Applied    │            │            │         │
 │            │            │─ Post ────>│         │
 │            │            │            │         │
 │            │            │            │─ Gen ──>│
 │            │            │            │  Invoice │
 │            │            │            │         │
 │<──────────────────────────────────────────────>│
 │         Billing Complete & Invoice Ready       │
```

### 11.2 Real-Time Charging Flow (Diameter Gy)

```
Device      PGW        OCS         Rating       Database
  │          │          │            │            │
  │ Data ───>│          │            │            │
  │ Usage    │          │            │            │
  │          │ CCR ───> │            │            │
  │          │(Initial) │            │            │
  │          │          │─ Get Tariff >           │
  │          │          │            │ Lookup    │
  │          │          │<─ Tariff ──│           │
  │          │          │            │           │
  │          │          │─ Calculate─>           │
  │          │          │  Quota     │           │
  │          │<─ CCA ────            │           │
  │          │ (Granted)             │           │
  │          │          │            │           │
  │<─ Quota ─│          │            │           │
  │ Granted  │          │            │           │
  │          │          │            │           │
  │ (Update) │ CCR ───> │            │           │
  │ Data     │(Update)  │            │           │
  │          │<─ CCA ────            │           │
  │          │          │            │           │
  │ (End)    │ CCR ───> │            │           │
  │ Session  │(Terminate)           │           │
  │          │          │─ Close Session─        │
  │          │<─ CCA ────            │           │
  │          │ (Final)  │            │           │
  │          │          │            │           │
  │<─ Session ─Close ────            │           │
  │ Terminated           │            │           │
```

---

## 12. Testing Strategies

### 12.1 Unit Testing

```python
# Example: Test Rating Engine
import unittest
from rating_engine import RatingEngine, TariffRule

class TestRatingEngine(unittest.TestCase):

    def setUp(self):
        self.engine = RatingEngine()
        self.tariff = TariffRule(
            service_type="VOICE",
            peak_rate=0.10,
            offpeak_rate=0.05
        )

    def test_peak_hour_rating(self):
        """Test voice call rating during peak hours"""
        call_duration = 300  # 5 minutes
        call_time = "14:30"  # Peak hour

        charge = self.engine.calculate(
            call_duration, call_time, self.tariff
        )

        expected = 0.50  # 5 * 0.10
        self.assertAlmostEqual(charge, expected, places=2)

    def test_offpeak_hour_rating(self):
        """Test voice call rating during off-peak hours"""
        call_duration = 300  # 5 minutes
        call_time = "22:30"  # Off-peak hour

        charge = self.engine.calculate(
            call_duration, call_time, self.tariff
        )

        expected = 0.25  # 5 * 0.05
        self.assertAlmostEqual(charge, expected, places=2)

    def test_volume_based_rating(self):
        """Test data service volume-based rating"""
        data_tariff = TariffRule(
            service_type="DATA",
            rate_0_100mb=0.05,
            rate_101_1000mb=0.03,
            rate_1000plus_mb=0.01
        )

        charge = self.engine.calculate_data(500, data_tariff)
        expected = (100 * 0.05) + (400 * 0.03)  # 5.00 + 12.00 = 17.00
        self.assertAlmostEqual(charge, expected, places=2)

if __name__ == '__main__':
    unittest.main()
```

### 12.2 Integration Testing

```python
# End-to-end CDR to Invoice testing
def test_cdr_to_invoice_flow():
    """Test complete CDR processing and invoice generation"""

    # 1. Generate test CDR
    cdr = {
        "msisdn": "+11234567890",
        "called_party": "+19876543210",
        "start_time": "2025-11-19T14:30:00Z",
        "duration_seconds": 345,
        "service_type": "VOICE"
    }

    # 2. Process through mediation
    mediated_cdr = mediation_system.process(cdr)
    assert mediated_cdr["status"] == "ENRICHED"
    assert "tariff_version" in mediated_cdr

    # 3. Apply rating
    rating_result = rating_engine.rate(mediated_cdr)
    assert rating_result["charge"] > 0
    assert rating_result["currency"] == "USD"

    # 4. Post to billing
    invoice_item = billing_system.create_item(rating_result)
    assert invoice_item["account_id"] is not None

    # 5. Verify invoice generation
    invoice = billing_system.generate_invoice(
        msisdn=cdr["msisdn"],
        period="2025_11"
    )
    assert len(invoice["line_items"]) > 0
    assert invoice["total_amount"] > 0
```

### 12.3 Performance Testing

```python
# Load testing for OCS
def test_ocs_concurrent_requests():
    """Test OCS handling 10,000 concurrent CCR requests"""

    import concurrent.futures
    import time

    ocs_client = OCSclient()

    def send_ccr_request(request_number):
        ccr = {
            "msisdn": f"+1123456{request_number:04d}",
            "service_type": "DATA",
            "requested_units": {"volume_mb": 100}
        }
        return ocs_client.send_ccr(ccr)

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [
            executor.submit(send_ccr_request, i)
            for i in range(10000)
        ]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    elapsed_time = time.time() - start_time

    # Assertions
    assert len(results) == 10000, "Not all requests completed"
    assert all(r["result"] == "GRANTED" for r in results), "Some requests failed"
    assert elapsed_time < 60, f"Request took {elapsed_time}s, should be < 60s"

    # Calculate performance metrics
    throughput = 10000 / elapsed_time  # Requests per second
    avg_response_time = (elapsed_time / 10000) * 1000  # Milliseconds

    print(f"Throughput: {throughput:.0f} req/sec")
    print(f"Avg response time: {avg_response_time:.2f} ms")
    print(f"95th percentile: {calculate_percentile(results, 95)} ms")
```

### 12.4 Fraud Detection Testing

```python
def test_fraud_detection_scenarios():
    """Test fraud detection with known fraud patterns"""

    fraud_detector = FraudDetectionEngine()

    # Test case 1: Volume spike
    spike_event = {
        "subscriber_id": "TEST_SPIKE",
        "event_type": "DATA_USAGE",
        "current_usage_mb": 5000,
        "expected_usage_mb": 500,
        "increase_percentage": 1000
    }

    result = fraud_detector.assess(spike_event)
    assert result["risk_level"] in ["HIGH", "CRITICAL"]

    # Test case 2: Impossible roaming
    impossible_roaming = {
        "subscriber_id": "TEST_ROAM",
        "session_1": {
            "location": "NEW_YORK",
            "timestamp": "2025-11-19T10:00:00Z"
        },
        "session_2": {
            "location": "TOKYO",
            "timestamp": "2025-11-19T10:05:00Z"
        }
    }

    result = fraud_detector.assess(impossible_roaming)
    assert result["risk_level"] == "HIGH"

    # Test case 3: Legitimate high usage (should pass)
    legitimate_usage = {
        "subscriber_id": "TEST_LEGITIMATE",
        "account_type": "CORPORATE",
        "contract_data_limit_mb": 100000,
        "current_usage_mb": 50000,
        "expected_usage_percentage": 45,
        "account_age_days": 1095  # 3 years
    }

    result = fraud_detector.assess(legitimate_usage)
    assert result["risk_level"] in ["LOW", "MEDIUM"]
```

---

## 13. Conclusion

This comprehensive telecom billing system template provides a complete framework for implementing enterprise-grade charging and billing solutions aligned with TM Forum standards and 3GPP specifications. Key takeaways:

1. **Architecture**: BSS/OSS integration following eTOM framework
2. **Charging Models**: Support for both real-time (OCS) and post-event (OFCS) charging
3. **Revenue Assurance**: Comprehensive fraud detection and billing accuracy mechanisms
4. **Standards Compliance**: Full adherence to 3GPP TS 32.240-32.298 specifications
5. **Integration**: Seamless CRM and ERP connectivity for end-to-end operations
6. **Testing**: Comprehensive unit, integration, performance, and fraud testing strategies

Implementation of this template enables telecom operators to deliver accurate, secure, and scalable billing services across multiple service types and revenue models.

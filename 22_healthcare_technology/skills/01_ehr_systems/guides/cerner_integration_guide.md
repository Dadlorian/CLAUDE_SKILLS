# Cerner (Oracle Health) Integration Guide

## Overview
Step-by-step guide for integrating with Cerner Millennium EHR using HL7 interfaces, CCL scripts, and FHIR APIs.

## Prerequisites
- Cerner Millennium access
- CCL development environment
- FHIR API credentials
- Network connectivity

## Part 1: CCL Development

### Basic CCL Query
```ccl
DROP PROGRAM get_patient_demographics:dba GO
CREATE PROGRAM get_patient_demographics:dba

PROMPT
    "Patient ID" = 0

WITH PERSON_ID

SELECT INTO "nl:"
FROM PERSON P
WHERE P.PERSON_ID = $PERSON_ID
  AND P.ACTIVE_IND = 1

DETAIL
    CALL ECHO(BUILD2(P.NAME_FULL_FORMATTED))

WITH TIME = 30

END GO
```

### Advanced Data Retrieval
```ccl
SELECT INTO "nl:"
FROM PERSON P
    ,ENCNTR E
    ,ORDERS O
    ,CLINICAL_EVENT CE
WHERE P.PERSON_ID = $PERSON_ID
  AND E.PERSON_ID = P.PERSON_ID
  AND E.ACTIVE_IND = 1
  AND O.ENCNTR_ID = E.ENCNTR_ID
  AND O.ACTIVE_IND = 1
  AND CE.ORDER_ID = O.ORDER_ID
  AND CE.VALID_UNTIL_DT_TM > SYSDATE
ORDER BY CE.EVENT_END_DT_TM DESC
```

## Part 2: Cerner FHIR API

### Authentication
```javascript
const authUrl = 'https://authorization.cerner.com/tenants/{tenant}/oauth2/token';

const response = await fetch(authUrl, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded'
  },
  body: new URLSearchParams({
    grant_type: 'authorization_code',
    code: authorizationCode,
    redirect_uri: 'https://yourapp.com/callback',
    client_id: clientId
  })
});

const { access_token } = await response.json();
```

### Resource Access
```javascript
// Get patient
const patient = await fetch(
  `https://fhir.cerner.com/r4/${tenantId}/Patient/${patientId}`,
  {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Accept': 'application/fhir+json'
    }
  }
);

// Search observations
const observations = await fetch(
  `https://fhir.cerner.com/r4/${tenantId}/Observation?patient=${patientId}&category=laboratory`,
  {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Accept': 'application/fhir+json'
    }
  }
);
```

## References
- Cerner Code Console: https://code.cerner.com/
- Cerner FHIR: https://fhir.cerner.com/

---

**Document Version**: 1.0
**Last Updated**: November 2024

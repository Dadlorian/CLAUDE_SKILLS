"""
Patient Consent Management System
Manages patient consents for data access, research, marketing, etc.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid
import logging

logger = logging.getLogger(__name__)

class ConsentManagementSystem:
    def __init__(self, db_connection):
        self.db = db_connection

    async def create_consent(self,
        patient_id: str,
        consent_type: str,
        grantee_id: str,
        data_elements: List[str],
        purpose: str,
        expiration_date: Optional[datetime] = None,
        specific_conditions: Optional[Dict] = None
    ) -> Dict:
        """Create a new patient consent"""

        consent_id = str(uuid.uuid4())

        if not expiration_date:
            # Default to 1 year if not specified
            expiration_date = datetime.utcnow() + timedelta(days=365)

        consent = {
            'consent_id': consent_id,
            'patient_id': patient_id,
            'consent_type': consent_type,
            'grantee_id': grantee_id,
            'data_elements': data_elements,
            'purpose': purpose,
            'expiration_date': expiration_date,
            'created_at': datetime.utcnow(),
            'revoked': False,
            'specific_conditions': specific_conditions
        }

        # Store in database
        await self.db.query(
            """INSERT INTO patient_consents
               (consent_id, patient_id, consent_type, grantee_id,
                data_elements, purpose, expiration_date, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            [consent_id, patient_id, consent_type, grantee_id,
             ','.join(data_elements), purpose, expiration_date,
             datetime.utcnow()]
        )

        # Log consent creation
        await self.log_consent_action(
            consent_id,
            patient_id,
            'created',
            f"Consent created for {grantee_id} - {purpose}"
        )

        return consent

    async def verify_consent(self,
        patient_id: str,
        grantee_id: str,
        data_element: str,
        purpose: str = None
    ) -> bool:
        """Verify if valid consent exists for data access"""

        # Query for active consent
        consent = await self.db.query(
            """SELECT * FROM patient_consents
               WHERE patient_id = %s
               AND grantee_id = %s
               AND revoked = FALSE
               AND expiration_date > NOW()
               AND data_elements LIKE %s""",
            [patient_id, grantee_id, f"%{data_element}%"]
        )

        if not consent:
            return False

        # Check specific conditions if applicable
        if purpose and consent[0].get('specific_conditions'):
            conditions = consent[0]['specific_conditions']
            if 'allowed_purposes' in conditions:
                if purpose not in conditions['allowed_purposes']:
                    return False

        return True

    async def get_patient_consents(self, patient_id: str) -> List[Dict]:
        """Get all consents for a patient"""
        consents = await self.db.query(
            """SELECT * FROM patient_consents
               WHERE patient_id = %s
               ORDER BY created_at DESC""",
            [patient_id]
        )

        return consents

    async def revoke_consent(self, consent_id: str, reason: str = None):
        """Revoke an active consent"""
        # Update consent status
        await self.db.query(
            """UPDATE patient_consents
               SET revoked = TRUE, revoked_at = NOW()
               WHERE consent_id = %s""",
            [consent_id]
        )

        # Log revocation
        await self.log_consent_action(
            consent_id,
            None,
            'revoked',
            reason or 'Consent revoked by patient'
        )

        # Notify grantee of revocation
        consent = await self.db.query(
            "SELECT * FROM patient_consents WHERE consent_id = %s",
            [consent_id]
        )

        if consent:
            await self.notify_consent_revocation(
                consent[0]['grantee_id'],
                consent[0]['patient_id'],
                consent[0]['consent_type']
            )

    async def extend_consent(self, consent_id: str, additional_days: int):
        """Extend the expiration date of a consent"""
        # Get current consent
        consent = await self.db.query(
            "SELECT expiration_date FROM patient_consents WHERE consent_id = %s",
            [consent_id]
        )

        if not consent:
            raise Exception("Consent not found")

        new_expiration = consent[0]['expiration_date'] + timedelta(days=additional_days)

        # Update expiration date
        await self.db.query(
            """UPDATE patient_consents
               SET expiration_date = %s
               WHERE consent_id = %s""",
            [new_expiration, consent_id]
        )

        # Log extension
        await self.log_consent_action(
            consent_id,
            None,
            'extended',
            f"Consent extended by {additional_days} days"
        )

    async def get_consent_analytics(self, patient_id: str = None) -> Dict:
        """Get analytics on consent usage"""
        if patient_id:
            # Patient-specific analytics
            query = "SELECT * FROM patient_consents WHERE patient_id = %s"
            params = [patient_id]
        else:
            # System-wide analytics
            query = "SELECT * FROM patient_consents"
            params = []

        consents = await self.db.query(query, params)

        analytics = {
            'total_consents': len(consents),
            'active_consents': len([c for c in consents if not c['revoked'] and c['expiration_date'] > datetime.utcnow()]),
            'revoked_consents': len([c for c in consents if c['revoked']]),
            'expired_consents': len([c for c in consents if c['expiration_date'] <= datetime.utcnow()]),
            'by_type': {},
            'by_purpose': {}
        }

        # Count by type and purpose
        for consent in consents:
            consent_type = consent['consent_type']
            purpose = consent['purpose']

            if consent_type not in analytics['by_type']:
                analytics['by_type'][consent_type] = 0
            analytics['by_type'][consent_type] += 1

            if purpose not in analytics['by_purpose']:
                analytics['by_purpose'][purpose] = 0
            analytics['by_purpose'][purpose] += 1

        return analytics

    async def audit_data_access(self,
        grantee_id: str,
        patient_id: str,
        data_elements_accessed: List[str],
        timestamp: datetime = None
    ) -> bool:
        """Audit data access against valid consents"""

        if not timestamp:
            timestamp = datetime.utcnow()

        # Check if access is consented
        for element in data_elements_accessed:
            if not await self.verify_consent(patient_id, grantee_id, element):
                # Log unauthorized access attempt
                await self.log_audit_violation(
                    grantee_id,
                    patient_id,
                    element,
                    'UNAUTHORIZED_ACCESS'
                )
                return False

        # Log authorized access
        await self.log_data_access(
            grantee_id,
            patient_id,
            data_elements_accessed,
            timestamp
        )

        return True

    async def log_consent_action(self,
        consent_id: str,
        patient_id: Optional[str],
        action: str,
        details: str
    ):
        """Log consent-related actions"""
        await self.db.query(
            """INSERT INTO consent_audit_log
               (consent_id, patient_id, action, details, timestamp)
               VALUES (%s, %s, %s, %s, NOW())""",
            [consent_id, patient_id, action, details]
        )

    async def log_data_access(self,
        grantee_id: str,
        patient_id: str,
        data_elements: List[str],
        timestamp: datetime
    ):
        """Log authorized data access"""
        await self.db.query(
            """INSERT INTO data_access_log
               (grantee_id, patient_id, data_elements_accessed, timestamp)
               VALUES (%s, %s, %s, %s)""",
            [grantee_id, patient_id, ','.join(data_elements), timestamp]
        )

    async def log_audit_violation(self,
        grantee_id: str,
        patient_id: str,
        data_element: str,
        violation_type: str
    ):
        """Log consent violations or unauthorized access attempts"""
        await self.db.query(
            """INSERT INTO audit_violations
               (grantee_id, patient_id, data_element, violation_type, timestamp)
               VALUES (%s, %s, %s, %s, NOW())""",
            [grantee_id, patient_id, data_element, violation_type]
        )

        # Alert security team
        logger.warning(f"Consent violation: {grantee_id} attempted unauthorized access to {patient_id}:{data_element}")

    async def notify_consent_revocation(self,
        grantee_id: str,
        patient_id: str,
        consent_type: str
    ):
        """Notify grantee of consent revocation"""
        message = f"Patient {patient_id} has revoked {consent_type} consent"

        # Get grantee contact info
        grantee = await self.db.query(
            "SELECT email FROM providers WHERE id = %s",
            [grantee_id]
        )

        if grantee:
            # Send notification email
            logger.info(f"Consent revocation notice sent to {grantee[0]['email']}")

    async def generate_consent_report(self, patient_id: str) -> Dict:
        """Generate consent report for patient"""
        consents = await self.get_patient_consents(patient_id)

        report = {
            'patient_id': patient_id,
            'report_date': datetime.utcnow().isoformat(),
            'active_consents': [],
            'expired_consents': [],
            'revoked_consents': []
        }

        for consent in consents:
            consent_summary = {
                'consent_id': consent['consent_id'],
                'type': consent['consent_type'],
                'grantee': consent['grantee_id'],
                'data_elements': consent['data_elements'].split(','),
                'purpose': consent['purpose'],
                'created_date': consent['created_at'].isoformat(),
                'expiration_date': consent['expiration_date'].isoformat()
            }

            if consent['revoked']:
                report['revoked_consents'].append(consent_summary)
            elif consent['expiration_date'] <= datetime.utcnow():
                report['expired_consents'].append(consent_summary)
            else:
                report['active_consents'].append(consent_summary)

        return report

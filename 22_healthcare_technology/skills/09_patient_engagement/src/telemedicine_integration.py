"""
Telemedicine Integration Service
Integrates video conferencing and virtual care with patient engagement
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
import jwt
import logging

logger = logging.getLogger(__name__)

class TelemedicineService:
    def __init__(self, db_connection, video_provider_client):
        self.db = db_connection
        self.video_client = video_provider_client  # Twilio, Zoom, etc.

    async def schedule_virtual_visit(self,
        patient_id: str,
        provider_id: str,
        scheduled_time: datetime,
        duration_minutes: int = 30,
        reason: str = None
    ) -> Dict:
        """Schedule virtual visit between patient and provider"""

        visit_id = str(uuid.uuid4())

        virtual_visit = {
            'visit_id': visit_id,
            'patient_id': patient_id,
            'provider_id': provider_id,
            'scheduled_time': scheduled_time,
            'duration_minutes': duration_minutes,
            'reason': reason,
            'status': 'scheduled',
            'created_at': datetime.utcnow()
        }

        # Store in database
        await self.db.query(
            """INSERT INTO virtual_visits
               (visit_id, patient_id, provider_id, scheduled_time,
                duration_minutes, reason, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            [visit_id, patient_id, provider_id, scheduled_time,
             duration_minutes, reason, 'scheduled']
        )

        # Create video room
        room_info = await self.create_video_room(visit_id, duration_minutes)

        # Send notifications
        await self.notify_patient(patient_id, visit_id, scheduled_time)
        await self.notify_provider(provider_id, visit_id, scheduled_time)

        return {
            'visit_id': visit_id,
            'room_url': room_info['room_url'],
            'scheduled_time': scheduled_time.isoformat()
        }

    async def create_video_room(self, visit_id: str, duration_minutes: int) -> Dict:
        """Create video conferencing room"""
        room_config = {
            'room_name': f"visit_{visit_id}",
            'max_participants': 2,
            'record': True,
            'enable_waiting_room': True,
            'duration': duration_minutes,
            'settings': {
                'allow_participant_unmute': True,
                'participant_video_enabled': True,
                'participant_screen_share_enabled': True
            }
        }

        # Create room with video provider
        room_info = await self.video_client.create_room(room_config)

        # Store room info in database
        await self.db.query(
            """INSERT INTO video_rooms
               (visit_id, room_id, room_name, meeting_url)
               VALUES (%s, %s, %s, %s)""",
            [visit_id, room_info['room_id'], room_info['room_name'],
             room_info['meeting_url']]
        )

        return {
            'room_id': room_info['room_id'],
            'room_url': room_info['meeting_url']
        }

    async def get_patient_access_token(self, visit_id: str, patient_id: str) -> str:
        """Generate secure access token for patient to join video room"""
        # Verify patient has access to this visit
        visit = await self.db.query(
            "SELECT * FROM virtual_visits WHERE visit_id = %s AND patient_id = %s",
            [visit_id, patient_id]
        )

        if not visit:
            raise Exception("Unauthorized access to visit")

        # Check visit is within acceptable time window
        scheduled = visit[0]['scheduled_time']
        now = datetime.utcnow()
        time_to_visit = (scheduled - now).total_seconds() / 60

        # Allow access from 5 minutes before to visit duration after scheduled time
        if time_to_visit < -visit[0]['duration_minutes'] or time_to_visit > 5:
            raise Exception("Visit not available at this time")

        # Generate token for video provider
        room_info = await self.db.query(
            "SELECT room_id FROM video_rooms WHERE visit_id = %s",
            [visit_id]
        )

        token_payload = {
            'sub': patient_id,
            'room': room_info[0]['room_id'],
            'participant_type': 'patient',
            'exp': datetime.utcnow() + timedelta(hours=1)
        }

        token = jwt.encode(token_payload, 'secret_key', algorithm='HS256')

        # Log access
        await self.log_access(visit_id, patient_id, 'patient', token)

        return token

    async def get_provider_access_token(self, visit_id: str, provider_id: str) -> str:
        """Generate secure access token for provider to join video room"""
        visit = await self.db.query(
            "SELECT * FROM virtual_visits WHERE visit_id = %s AND provider_id = %s",
            [visit_id, provider_id]
        )

        if not visit:
            raise Exception("Unauthorized access to visit")

        # Allow provider access from 10 minutes before to full visit duration
        scheduled = visit[0]['scheduled_time']
        now = datetime.utcnow()
        time_to_visit = (scheduled - now).total_seconds() / 60

        if time_to_visit < -visit[0]['duration_minutes'] or time_to_visit > 10:
            raise Exception("Visit not available at this time")

        room_info = await self.db.query(
            "SELECT room_id FROM video_rooms WHERE visit_id = %s",
            [visit_id]
        )

        token_payload = {
            'sub': provider_id,
            'room': room_info[0]['room_id'],
            'participant_type': 'provider',
            'exp': datetime.utcnow() + timedelta(hours=1)
        }

        token = jwt.encode(token_payload, 'secret_key', algorithm='HS256')

        await self.log_access(visit_id, provider_id, 'provider', token)

        return token

    async def start_visit(self, visit_id: str):
        """Mark visit as started"""
        await self.db.query(
            """UPDATE virtual_visits
               SET status = 'in_progress', started_at = NOW()
               WHERE visit_id = %s""",
            [visit_id]
        )

        # Log start
        logger.info(f"Visit {visit_id} started")

    async def end_visit(self, visit_id: str) -> Dict:
        """End visit and generate summary"""
        # Update visit status
        await self.db.query(
            """UPDATE virtual_visits
               SET status = 'completed', ended_at = NOW()
               WHERE visit_id = %s""",
            [visit_id]
        )

        # Get visit details
        visit = await self.db.query(
            "SELECT * FROM virtual_visits WHERE visit_id = %s",
            [visit_id]
        )

        if not visit:
            raise Exception("Visit not found")

        visit_data = visit[0]

        # Get video recording if available
        recording_url = await self.get_recording_url(visit_id)

        # Generate encounter note (can be populated by provider)
        encounter_note = {
            'visit_id': visit_id,
            'patient_id': visit_data['patient_id'],
            'provider_id': visit_data['provider_id'],
            'visit_type': 'telemedicine',
            'visit_date': visit_data['scheduled_time'],
            'duration_minutes': visit_data['duration_minutes'],
            'recording_url': recording_url,
            'reason': visit_data['reason'],
            'assessment': None,  # To be filled by provider
            'plan': None,  # To be filled by provider
            'created_at': datetime.utcnow()
        }

        # Store encounter note
        await self.db.query(
            """INSERT INTO encounter_notes
               (visit_id, patient_id, provider_id, visit_type, assessment, plan)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            [visit_id, visit_data['patient_id'], visit_data['provider_id'],
             'telemedicine', None, None]
        )

        # Notify patient
        await self.notify_visit_completed(visit_data['patient_id'], visit_id)

        return encounter_note

    async def get_recording_url(self, visit_id: str) -> Optional[str]:
        """Get URL for video recording if available"""
        recording = await self.db.query(
            "SELECT recording_url FROM video_recordings WHERE visit_id = %s",
            [visit_id]
        )

        if recording and recording[0].get('recording_url'):
            return recording[0]['recording_url']

        return None

    async def notify_patient(self, patient_id: str, visit_id: str, scheduled_time: datetime):
        """Send notification to patient about scheduled visit"""
        # Get patient contact info
        patient = await self.db.query(
            "SELECT email, phone, notification_preference FROM patients WHERE id = %s",
            [patient_id]
        )

        if not patient:
            return

        patient_data = patient[0]

        message = f"Your telemedicine appointment is scheduled for {scheduled_time.strftime('%B %d at %I:%M %p')}"

        if patient_data['notification_preference'] in ['email', 'all']:
            await self.send_email(
                patient_data['email'],
                'Virtual Visit Scheduled',
                message
            )

        if patient_data['notification_preference'] in ['sms', 'all']:
            await self.send_sms(patient_data['phone'], message)

    async def notify_provider(self, provider_id: str, visit_id: str, scheduled_time: datetime):
        """Send notification to provider about scheduled visit"""
        provider = await self.db.query(
            "SELECT email, phone FROM providers WHERE id = %s",
            [provider_id]
        )

        if not provider:
            return

        provider_data = provider[0]
        message = f"You have a telemedicine appointment scheduled for {scheduled_time.strftime('%B %d at %I:%M %p')}"

        await self.send_email(provider_data['email'], 'Virtual Visit Scheduled', message)

    async def notify_visit_completed(self, patient_id: str, visit_id: str):
        """Notify patient that visit is completed"""
        message = "Your telemedicine visit has been completed. Thank you for attending."

        patient = await self.db.query(
            "SELECT email FROM patients WHERE id = %s",
            [patient_id]
        )

        if patient:
            await self.send_email(patient[0]['email'], 'Visit Completed', message)

    async def send_email(self, email: str, subject: str, message: str):
        """Send email notification"""
        # Implementation would use email service like SendGrid
        logger.info(f"Email sent to {email}: {subject}")

    async def send_sms(self, phone: str, message: str):
        """Send SMS notification"""
        # Implementation would use SMS service like Twilio
        logger.info(f"SMS sent to {phone}: {message}")

    async def log_access(self, visit_id: str, user_id: str, user_type: str, token: str):
        """Log access to video room"""
        await self.db.query(
            """INSERT INTO video_access_log
               (visit_id, user_id, user_type, token, accessed_at)
               VALUES (%s, %s, %s, %s, NOW())""",
            [visit_id, user_id, user_type, token]
        )

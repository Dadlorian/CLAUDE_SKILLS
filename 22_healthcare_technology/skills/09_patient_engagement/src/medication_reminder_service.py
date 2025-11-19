"""
Medication Adherence Reminder Service
Handles medication reminders via SMS, push notifications, and email
"""

from datetime import datetime, timedelta
from typing import List, Dict
import requests
import json
import logging

logger = logging.getLogger(__name__)

class MedicationReminderService:
    def __init__(self, db_connection, notification_service):
        self.db = db_connection
        self.notifier = notification_service

    async def schedule_medication_reminder(self, patient_id: str, medication: Dict):
        """Schedule medication reminder for patient"""
        reminder = {
            'patient_id': patient_id,
            'medication_id': medication['id'],
            'medication_name': medication['name'],
            'dosage': medication['dose'],
            'frequency': medication['frequency'],
            'scheduled_time': medication['reminder_time'],
            'created_at': datetime.utcnow()
        }

        # Insert into database
        await self.db.query(
            """INSERT INTO medication_reminders
               (patient_id, medication_id, scheduled_time, frequency, created_at)
               VALUES (%s, %s, %s, %s, %s)""",
            [patient_id, medication['id'], medication['reminder_time'],
             medication['frequency'], datetime.utcnow()]
        )

        # Send initial reminder
        await self.send_medication_reminder(patient_id, medication)

    async def send_medication_reminder(self, patient_id: str, medication: Dict):
        """Send reminder notification to patient"""
        # Get patient contact preferences
        patient = await self.db.query(
            """SELECT email, phone, notification_preference
               FROM patients WHERE id = %s""",
            [patient_id]
        )

        if patient.empty:
            return

        patient_data = patient.iloc[0]
        preference = patient_data['notification_preference']

        message = f"Medication reminder: Take {medication['dose']} of {medication['name']}"

        if preference in ['sms', 'all'] and patient_data['phone']:
            await self.notifier.send_sms(patient_data['phone'], message)

        if preference in ['email', 'all'] and patient_data['email']:
            await self.notifier.send_email(
                patient_data['email'],
                'Medication Reminder',
                message
            )

        if preference in ['push', 'all']:
            await self.notifier.send_push_notification(
                patient_id,
                'Medication Reminder',
                message,
                data={'medication_id': medication['id'], 'action': 'take_medication'}
            )

        # Log reminder sent
        await self.log_reminder_sent(patient_id, medication['id'])

    async def handle_medication_taken(self, patient_id: str, medication_id: str, timestamp: datetime):
        """Log when patient confirms medication taken"""
        await self.db.query(
            """INSERT INTO medication_adherence_log
               (patient_id, medication_id, taken_at, source)
               VALUES (%s, %s, %s, %s)""",
            [patient_id, medication_id, timestamp, 'app_confirmation']
        )

        # Send positive reinforcement
        await self.send_positive_feedback(patient_id)

        # Update adherence metrics
        await self.update_adherence_metrics(patient_id, medication_id)

    async def send_positive_feedback(self, patient_id: str):
        """Send positive reinforcement message"""
        messages = [
            "Great job! Keep up the good work with your medications.",
            "Excellent! You're staying on track with your medication routine.",
            "Nice! You took your medication on time.",
            "Awesome! Your consistent medication use is helping your health."
        ]

        import random
        message = random.choice(messages)

        await self.notifier.send_push_notification(
            patient_id,
            'Great Job!',
            message
        )

    async def generate_adherence_report(self, patient_id: str, period_days: int = 30):
        """Generate medication adherence report for patient"""
        start_date = datetime.utcnow() - timedelta(days=period_days)

        # Get prescribed medications
        prescribed = await self.db.query(
            """SELECT id, drug_name, frequency
               FROM medications
               WHERE patient_id = %s AND status = 'active'""",
            [patient_id]
        )

        # Get logged adherence
        adherence = await self.db.query(
            """SELECT medication_id, COUNT(*) as times_taken
               FROM medication_adherence_log
               WHERE patient_id = %s AND taken_at >= %s
               GROUP BY medication_id""",
            [patient_id, start_date]
        )

        # Calculate adherence percentage
        adherence_by_med = {}
        for _, row in adherence.iterrows():
            adherence_by_med[row['medication_id']] = row['times_taken']

        report = {
            'patient_id': patient_id,
            'period_days': period_days,
            'medications': [],
            'overall_adherence_percentage': 0
        }

        total_adherence = 0
        for _, med in prescribed.iterrows():
            expected_doses = self._calculate_expected_doses(
                med['frequency'], period_days
            )
            actual_doses = adherence_by_med.get(med['id'], 0)
            adherence_percent = (actual_doses / expected_doses * 100) if expected_doses > 0 else 0

            report['medications'].append({
                'medication_id': med['id'],
                'drug_name': med['drug_name'],
                'expected_doses': expected_doses,
                'actual_doses': actual_doses,
                'adherence_percentage': adherence_percent
            })

            total_adherence += adherence_percent

        report['overall_adherence_percentage'] = (
            total_adherence / len(prescribed) if len(prescribed) > 0 else 0
        )

        return report

    def _calculate_expected_doses(self, frequency: str, days: int) -> int:
        """Calculate expected number of doses based on frequency"""
        frequency_map = {
            'once_daily': days * 1,
            'twice_daily': days * 2,
            'three_times_daily': days * 3,
            'four_times_daily': days * 4,
            'every_other_day': days * 0.5,
            'weekly': (days / 7),
            'twice_weekly': (days / 7) * 2
        }

        return int(frequency_map.get(frequency, 0))

    async def log_reminder_sent(self, patient_id: str, medication_id: str):
        """Log that reminder was sent"""
        await self.db.query(
            """INSERT INTO reminder_log
               (patient_id, medication_id, sent_at)
               VALUES (%s, %s, %s)""",
            [patient_id, medication_id, datetime.utcnow()]
        )

    async def update_adherence_metrics(self, patient_id: str, medication_id: str):
        """Update adherence metrics for analytics"""
        report = await self.generate_adherence_report(patient_id, period_days=30)

        await self.db.query(
            """UPDATE patient_metrics
               SET adherence_percentage = %s
               WHERE patient_id = %s""",
            [report['overall_adherence_percentage'], patient_id]
        )

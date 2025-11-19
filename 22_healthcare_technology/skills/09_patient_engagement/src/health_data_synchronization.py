"""
Health Data Synchronization Service
Real-time synchronization of health data between EHR, devices, and patient portal
"""

from datetime import datetime, timedelta
import asyncio
import logging
from typing import Dict, List
import aiohttp

logger = logging.getLogger(__name__)

class HealthDataSyncService:
    def __init__(self, db_connection, ehr_api_client):
        self.db = db_connection
        self.ehr_client = ehr_api_client
        self.sync_interval = 3600  # 1 hour

    async def start_continuous_sync(self):
        """Start continuous health data synchronization"""
        while True:
            try:
                await self.sync_all_patient_data()
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"Sync error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry

    async def sync_all_patient_data(self):
        """Sync data for all active patients"""
        # Get all active patients
        patients = await self.db.query(
            "SELECT id FROM patients WHERE active = true"
        )

        tasks = [self.sync_patient_data(patient['id']) for patient in patients]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def sync_patient_data(self, patient_id: str):
        """Sync all data types for a single patient"""
        sync_tasks = [
            self.sync_labs(patient_id),
            self.sync_vital_signs(patient_id),
            self.sync_medications(patient_id),
            self.sync_problems(patient_id),
            self.sync_device_data(patient_id)
        ]

        results = await asyncio.gather(*sync_tasks, return_exceptions=True)

        # Log sync completion
        await self.log_sync_completion(patient_id, results)

    async def sync_labs(self, patient_id: str):
        """Sync lab results from EHR"""
        # Query EHR for new lab results since last sync
        last_sync = await self.get_last_sync_time(patient_id, 'labs')

        try:
            labs = await self.ehr_client.fetch_observations(
                patient_id=patient_id,
                observation_type='lab',
                since=last_sync
            )

            # Store in patient portal database
            for lab in labs:
                normalized_lab = self.normalize_lab(lab)
                await self.store_lab_result(patient_id, normalized_lab)

            # Update sync timestamp
            await self.update_sync_time(patient_id, 'labs')

            return {'status': 'success', 'count': len(labs)}
        except Exception as e:
            logger.error(f"Lab sync error for {patient_id}: {e}")
            return {'status': 'error', 'error': str(e)}

    async def sync_vital_signs(self, patient_id: str):
        """Sync vital signs (BP, HR, weight, etc)"""
        last_sync = await self.get_last_sync_time(patient_id, 'vitals')

        try:
            vitals = await self.ehr_client.fetch_observations(
                patient_id=patient_id,
                observation_type='vital_signs',
                since=last_sync
            )

            for vital in vitals:
                normalized_vital = self.normalize_vital(vital)
                await self.store_vital_sign(patient_id, normalized_vital)

            await self.update_sync_time(patient_id, 'vitals')
            return {'status': 'success', 'count': len(vitals)}
        except Exception as e:
            logger.error(f"Vital signs sync error for {patient_id}: {e}")
            return {'status': 'error', 'error': str(e)}

    async def sync_medications(self, patient_id: str):
        """Sync medication list from EHR"""
        last_sync = await self.get_last_sync_time(patient_id, 'medications')

        try:
            medications = await self.ehr_client.fetch_medications(
                patient_id=patient_id,
                since=last_sync
            )

            # Deduplicate and merge with existing
            for med in medications:
                normalized_med = self.normalize_medication(med)
                await self.upsert_medication(patient_id, normalized_med)

            await self.update_sync_time(patient_id, 'medications')
            return {'status': 'success', 'count': len(medications)}
        except Exception as e:
            logger.error(f"Medication sync error for {patient_id}: {e}")
            return {'status': 'error', 'error': str(e)}

    async def sync_problems(self, patient_id: str):
        """Sync problem list from EHR"""
        last_sync = await self.get_last_sync_time(patient_id, 'problems')

        try:
            problems = await self.ehr_client.fetch_conditions(
                patient_id=patient_id,
                since=last_sync
            )

            for problem in problems:
                normalized_problem = self.normalize_problem(problem)
                await self.upsert_problem(patient_id, normalized_problem)

            await self.update_sync_time(patient_id, 'problems')
            return {'status': 'success', 'count': len(problems)}
        except Exception as e:
            logger.error(f"Problem sync error for {patient_id}: {e}")
            return {'status': 'error', 'error': str(e)}

    async def sync_device_data(self, patient_id: str):
        """Sync data from connected wearable devices"""
        # Get connected devices
        devices = await self.db.query(
            """SELECT device_id, device_type, api_token
               FROM connected_devices
               WHERE patient_id = %s AND active = true""",
            [patient_id]
        )

        device_results = []
        for device in devices:
            try:
                data = await self.fetch_device_data(
                    device['device_id'],
                    device['device_type'],
                    device['api_token']
                )

                for reading in data:
                    await self.store_device_reading(patient_id, device['device_type'], reading)

                device_results.append({'device': device['device_id'], 'status': 'success'})
            except Exception as e:
                logger.error(f"Device sync error: {e}")
                device_results.append({'device': device['device_id'], 'status': 'error'})

        return {'status': 'success', 'devices': device_results}

    async def fetch_device_data(self, device_id: str, device_type: str, api_token: str):
        """Fetch data from specific wearable device"""
        device_apis = {
            'apple_health': 'https://api.healthkit.apple.com',
            'google_fit': 'https://www.googleapis.com/fitness',
            'fitbit': 'https://api.fitbit.com',
            'garmin': 'https://api.garmin.com'
        }

        headers = {'Authorization': f'Bearer {api_token}'}
        api_url = device_apis.get(device_type)

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{api_url}/data", headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    raise Exception(f"Device API error: {resp.status}")

    def normalize_lab(self, lab_data: Dict) -> Dict:
        """Normalize lab data to standard format"""
        return {
            'test_code': lab_data.get('code'),
            'test_name': lab_data.get('display'),
            'value': lab_data.get('value'),
            'unit': lab_data.get('unit'),
            'reference_range': lab_data.get('reference_range'),
            'date': lab_data.get('effective_date'),
            'interpretation': lab_data.get('interpretation')
        }

    def normalize_vital(self, vital_data: Dict) -> Dict:
        """Normalize vital sign data"""
        return {
            'vital_type': vital_data.get('type'),
            'value': vital_data.get('value'),
            'unit': vital_data.get('unit'),
            'date': vital_data.get('date')
        }

    def normalize_medication(self, med_data: Dict) -> Dict:
        """Normalize medication data"""
        return {
            'drug_code': med_data.get('code'),
            'drug_name': med_data.get('name'),
            'dose': med_data.get('dose'),
            'unit': med_data.get('unit'),
            'frequency': med_data.get('frequency'),
            'status': med_data.get('status'),
            'start_date': med_data.get('start_date'),
            'end_date': med_data.get('end_date')
        }

    def normalize_problem(self, problem_data: Dict) -> Dict:
        """Normalize problem/condition data"""
        return {
            'code': problem_data.get('code'),
            'description': problem_data.get('description'),
            'status': problem_data.get('status'),
            'onset_date': problem_data.get('onset_date')
        }

    async def store_lab_result(self, patient_id: str, lab: Dict):
        """Store lab result in database"""
        await self.db.query(
            """INSERT INTO lab_results
               (patient_id, test_code, value, date, synced_at)
               VALUES (%s, %s, %s, %s, NOW())
               ON DUPLICATE KEY UPDATE synced_at = NOW()""",
            [patient_id, lab['test_code'], lab['value'], lab['date']]
        )

    async def store_vital_sign(self, patient_id: str, vital: Dict):
        """Store vital sign in database"""
        await self.db.query(
            """INSERT INTO vital_signs
               (patient_id, vital_type, value, date, synced_at)
               VALUES (%s, %s, %s, %s, NOW())""",
            [patient_id, vital['vital_type'], vital['value'], vital['date']]
        )

    async def upsert_medication(self, patient_id: str, med: Dict):
        """Insert or update medication"""
        await self.db.query(
            """INSERT INTO medications
               (patient_id, drug_code, drug_name, dose, frequency, status)
               VALUES (%s, %s, %s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE
               status = %s, dose = %s""",
            [patient_id, med['drug_code'], med['drug_name'], med['dose'],
             med['frequency'], med['status'], med['status'], med['dose']]
        )

    async def upsert_problem(self, patient_id: str, problem: Dict):
        """Insert or update problem/condition"""
        await self.db.query(
            """INSERT INTO problems
               (patient_id, code, description, status)
               VALUES (%s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE status = %s""",
            [patient_id, problem['code'], problem['description'],
             problem['status'], problem['status']]
        )

    async def store_device_reading(self, patient_id: str, device_type: str, reading: Dict):
        """Store device reading in database"""
        # Map device data to appropriate table
        if device_type in ['apple_health', 'google_fit']:
            await self.store_vital_sign(patient_id, reading)
        # Add other device types as needed

    async def get_last_sync_time(self, patient_id: str, data_type: str) -> datetime:
        """Get timestamp of last successful sync"""
        result = await self.db.query(
            """SELECT last_sync FROM sync_status
               WHERE patient_id = %s AND data_type = %s""",
            [patient_id, data_type]
        )

        if result:
            return result[0]['last_sync']
        # Default to 24 hours ago if first sync
        return datetime.utcnow() - timedelta(days=1)

    async def update_sync_time(self, patient_id: str, data_type: str):
        """Update sync timestamp"""
        await self.db.query(
            """INSERT INTO sync_status
               (patient_id, data_type, last_sync)
               VALUES (%s, %s, NOW())
               ON DUPLICATE KEY UPDATE last_sync = NOW()""",
            [patient_id, data_type]
        )

    async def log_sync_completion(self, patient_id: str, results: List):
        """Log sync completion and results"""
        logger.info(f"Sync completed for patient {patient_id}: {results}")

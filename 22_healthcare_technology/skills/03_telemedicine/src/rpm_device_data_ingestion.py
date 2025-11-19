"""RPM Device Data Ingestion Pipeline"""
import json
from datetime import datetime
from typing import Dict, Any

class RPMDataIngestionService:
    def __init__(self, db_connection):
        self.db = db_connection

    def ingest_blood_pressure(self, device_id: str, data: Dict[str, Any]):
        """Ingest blood pressure reading"""
        reading = {
            'device_id': device_id,
            'systolic': data['systolic'],
            'diastolic': data['diastolic'],
            'pulse': data.get('pulse'),
            'timestamp': data['timestamp'],
            'irregularHeartbeat': data.get('irregularHeartbeat', False)
        }

        # Validate ranges
        if not (60 <= reading['systolic'] <= 300):
            raise ValueError(f"Invalid systolic: {reading['systolic']}")
        if not (40 <= reading['diastolic'] <= 200):
            raise ValueError(f"Invalid diastolic: {reading['diastolic']}")

        # Insert into database
        self.db.execute("""
            INSERT INTO rpm_blood_pressure
            (device_id, patient_id, systolic, diastolic, pulse, irregular_heartbeat, recorded_at)
            VALUES (%s, (SELECT patient_id FROM devices WHERE id = %s), %s, %s, %s, %s, %s)
        """, (device_id, device_id, reading['systolic'], reading['diastolic'], 
              reading['pulse'], reading['irregularHeartbeat'], reading['timestamp']))

        # Check alerts
        self.check_bp_alerts(device_id, reading)

        return {'status': 'success', 'reading_id': self.db.lastrowid}

    def check_bp_alerts(self, device_id: str, reading: Dict[str, Any]):
        """Check if BP reading triggers alerts"""
        if reading['systolic'] > 180 or reading['diastolic'] > 110:
            self.create_alert(device_id, 'CRITICAL_HIGH_BP', reading)
        elif reading['systolic'] < 90:
            self.create_alert(device_id, 'LOW_BP', reading)

    def create_alert(self, device_id: str, alert_type: str, reading: Dict[str, Any]):
        """Create clinical alert for care team"""
        self.db.execute("""
            INSERT INTO rpm_alerts
            (device_id, patient_id, alert_type, severity, data, status, created_at)
            VALUES (%s, (SELECT patient_id FROM devices WHERE id = %s), %s, 'HIGH', %s, 'NEW', NOW())
        """, (device_id, device_id, alert_type, json.dumps(reading)))

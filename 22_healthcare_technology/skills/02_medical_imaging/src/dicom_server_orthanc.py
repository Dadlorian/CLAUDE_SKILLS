#!/usr/bin/env python3
"""
Orthanc DICOM Server Integration
Production-grade Python client for Orthanc PACS server
"""

import requests
from requests.auth import HTTPBasicAuth
import json
from typing import List, Dict, Optional
import pydicom
from pathlib import Path

class OrthancClient:
    """Client for interacting with Orthanc DICOM server"""
    
    def __init__(self, base_url: str, username: str = None, password: str = None):
        self.base_url = base_url.rstrip('/')
        self.auth = HTTPBasicAuth(username, password) if username else None
        self.session = requests.Session()
        if self.auth:
            self.session.auth = self.auth
    
    def get_system_info(self) -> Dict:
        """Get Orthanc system information"""
        response = self.session.get(f"{self.base_url}/system")
        response.raise_for_status()
        return response.json()
    
    def upload_dicom(self, file_path: str) -> Dict:
        """Upload DICOM file to Orthanc"""
        with open(file_path, 'rb') as f:
            response = self.session.post(
                f"{self.base_url}/instances",
                data=f.read(),
                headers={'Content-Type': 'application/dicom'}
            )
        response.raise_for_status()
        return response.json()
    
    def search_studies(self, patient_id: str = None, patient_name: str = None,
                      study_date: str = None) -> List[Dict]:
        """Search for studies using Orthanc API"""
        query = {}
        if patient_id:
            query['PatientID'] = patient_id
        if patient_name:
            query['PatientName'] = patient_name
        if study_date:
            query['StudyDate'] = study_date
        
        response = self.session.post(
            f"{self.base_url}/tools/find",
            json={
                'Level': 'Study',
                'Query': query,
                'Expand': True
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_study(self, study_id: str) -> Dict:
        """Get study information"""
        response = self.session.get(f"{self.base_url}/studies/{study_id}")
        response.raise_for_status()
        return response.json()
    
    def download_study(self, study_id: str, output_dir: str) -> Path:
        """Download entire study as ZIP"""
        output_path = Path(output_dir) / f"study_{study_id}.zip"
        
        response = self.session.get(
            f"{self.base_url}/studies/{study_id}/archive",
            stream=True
        )
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return output_path
    
    def delete_study(self, study_id: str) -> bool:
        """Delete study from Orthanc"""
        response = self.session.delete(f"{self.base_url}/studies/{study_id}")
        response.raise_for_status()
        return True
    
    def anonymize_study(self, study_id: str, keep_tags: List[str] = None) -> str:
        """Anonymize study and return new study ID"""
        anonymization_config = {
            'Replace': {
                'PatientName': 'ANONYMOUS',
                'PatientID': 'ANON123'
            },
            'Keep': keep_tags or ['StudyDescription', 'SeriesDescription'],
            'Force': True
        }
        
        response = self.session.post(
            f"{self.base_url}/studies/{study_id}/anonymize",
            json=anonymization_config
        )
        response.raise_for_status()
        return response.json()['ID']
    
    def send_to_peer(self, study_id: str, peer_name: str) -> bool:
        """Send study to configured DICOM peer"""
        response = self.session.post(
            f"{self.base_url}/peers/{peer_name}/store",
            json=[study_id]
        )
        response.raise_for_status()
        return True

if __name__ == '__main__':
    # Example usage
    client = OrthancClient('http://localhost:8042', 'orthanc', 'orthanc')
    
    # Get system info
    info = client.get_system_info()
    print(f"Orthanc Version: {info['Version']}")
    
    # Upload DICOM file
    result = client.upload_dicom('example.dcm')
    print(f"Uploaded: {result['ID']}")
    
    # Search for studies
    studies = client.search_studies(patient_id='12345')
    print(f"Found {len(studies)} studies")
    
    # Download study
    if studies:
        study_id = studies[0]['ID']
        archive_path = client.download_study(study_id, '/tmp')
        print(f"Downloaded to: {archive_path}")

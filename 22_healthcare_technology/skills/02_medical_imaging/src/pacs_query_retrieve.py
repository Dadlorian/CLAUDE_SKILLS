#!/usr/bin/env python3
"""
PACS Query/Retrieve Implementation
Comprehensive DICOM C-FIND and C-MOVE implementation
"""

from pynetdicom import AE, evt
from pynetdicom.sop_class import (
    PatientRootQueryRetrieveInformationModelFind,
    PatientRootQueryRetrieveInformationModelMove,
    StudyRootQueryRetrieveInformationModelFind,
    StudyRootQueryRetrieveInformationModelMove,
    CTImageStorage,
    MRImageStorage
)
from pydicom.dataset import Dataset
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PACSQueryRetrieve:
    """PACS Query/Retrieve client"""
    
    def __init__(self, ae_title: str):
        self.ae = AE(ae_title=ae_title)
        
        # Add query contexts
        self.ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)
        self.ae.add_requested_context(StudyRootQueryRetrieveInformationModelFind)
        
        # Add move contexts
        self.ae.add_requested_context(PatientRootQueryRetrieveInformationModelMove)
        self.ae.add_requested_context(StudyRootQueryRetrieveInformationModelMove)
        
        # Add storage contexts for receiving images
        self.ae.add_requested_context(CTImageStorage)
        self.ae.add_requested_context(MRImageStorage)
    
    def query_patients(self, pacs_host: str, pacs_port: int, pacs_ae: str,
                      patient_name: str = None, patient_id: str = None) -> List[Dict]:
        """Query for patients"""
        # Build query dataset
        ds = Dataset()
        ds.QueryRetrieveLevel = 'PATIENT'
        ds.PatientName = patient_name or ''
        ds.PatientID = patient_id or ''
        ds.PatientBirthDate = ''
        ds.PatientSex = ''
        
        results = []
        assoc = self.ae.associate(pacs_host, pacs_port, ae_title=pacs_ae)
        
        if assoc.is_established:
            responses = assoc.send_c_find(
                ds,
                PatientRootQueryRetrieveInformationModelFind
            )
            
            for (status, identifier) in responses:
                if status and status.Status in (0xFF00, 0xFF01):
                    results.append({
                        'patient_name': str(identifier.PatientName),
                        'patient_id': str(identifier.PatientID),
                        'birth_date': str(identifier.PatientBirthDate),
                        'sex': str(identifier.PatientSex)
                    })
            
            assoc.release()
        
        return results
    
    def query_studies(self, pacs_host: str, pacs_port: int, pacs_ae: str,
                     patient_id: str = None, study_date: str = None,
                     modality: str = None, accession: str = None) -> List[Dict]:
        """Query for studies"""
        ds = Dataset()
        ds.QueryRetrieveLevel = 'STUDY'
        ds.PatientID = patient_id or ''
        ds.PatientName = ''
        ds.StudyDate = study_date or ''
        ds.StudyTime = ''
        ds.AccessionNumber = accession or ''
        ds.StudyInstanceUID = ''
        ds.StudyDescription = ''
        ds.ModalitiesInStudy = modality or ''
        ds.NumberOfStudyRelatedInstances = ''
        
        results = []
        assoc = self.ae.associate(pacs_host, pacs_port, ae_title=pacs_ae)
        
        if assoc.is_established:
            responses = assoc.send_c_find(
                ds,
                StudyRootQueryRetrieveInformationModelFind
            )
            
            for (status, identifier) in responses:
                if status and status.Status in (0xFF00, 0xFF01):
                    results.append({
                        'patient_name': str(identifier.PatientName),
                        'patient_id': str(identifier.PatientID),
                        'study_uid': str(identifier.StudyInstanceUID),
                        'study_date': str(identifier.StudyDate),
                        'study_description': str(identifier.StudyDescription),
                        'modalities': str(identifier.ModalitiesInStudy),
                        'num_images': int(identifier.NumberOfStudyRelatedInstances)
                    })
            
            assoc.release()
        
        logger.info(f"Found {len(results)} studies")
        return results
    
    def query_series(self, pacs_host: str, pacs_port: int, pacs_ae: str,
                    study_uid: str) -> List[Dict]:
        """Query for series within a study"""
        ds = Dataset()
        ds.QueryRetrieveLevel = 'SERIES'
        ds.StudyInstanceUID = study_uid
        ds.SeriesInstanceUID = ''
        ds.SeriesNumber = ''
        ds.Modality = ''
        ds.SeriesDescription = ''
        ds.NumberOfSeriesRelatedInstances = ''
        
        results = []
        assoc = self.ae.associate(pacs_host, pacs_port, ae_title=pacs_ae)
        
        if assoc.is_established:
            responses = assoc.send_c_find(
                ds,
                StudyRootQueryRetrieveInformationModelFind
            )
            
            for (status, identifier) in responses:
                if status and status.Status in (0xFF00, 0xFF01):
                    results.append({
                        'series_uid': str(identifier.SeriesInstanceUID),
                        'series_number': str(identifier.SeriesNumber),
                        'modality': str(identifier.Modality),
                        'description': str(identifier.SeriesDescription),
                        'num_images': int(identifier.NumberOfSeriesRelatedInstances)
                    })
            
            assoc.release()
        
        return results
    
    def retrieve_study(self, pacs_host: str, pacs_port: int, pacs_ae: str,
                      study_uid: str, dest_ae: str) -> Dict:
        """Retrieve study using C-MOVE"""
        ds = Dataset()
        ds.QueryRetrieveLevel = 'STUDY'
        ds.StudyInstanceUID = study_uid
        
        assoc = self.ae.associate(pacs_host, pacs_port, ae_title=pacs_ae)
        
        stats = {
            'completed': 0,
            'failed': 0,
            'warning': 0,
            'remaining': 0
        }
        
        if assoc.is_established:
            responses = assoc.send_c_move(
                ds,
                dest_ae,
                StudyRootQueryRetrieveInformationModelMove
            )
            
            for (status, identifier) in responses:
                if status:
                    stats['remaining'] = status.NumberOfRemainingSuboperations
                    stats['completed'] = status.NumberOfCompletedSuboperations
                    stats['failed'] = status.NumberOfFailedSuboperations
                    stats['warning'] = status.NumberOfWarningSuboperations
                    
                    logger.info(
                        f"C-MOVE Progress - Remaining: {stats['remaining']}, "
                        f"Completed: {stats['completed']}, "
                        f"Failed: {stats['failed']}"
                    )
            
            assoc.release()
        
        return stats

if __name__ == '__main__':
    # Example usage
    qr = PACSQueryRetrieve('QUERY_SCU')
    
    # Query for studies
    studies = qr.query_studies(
        'localhost',
        104,
        'PACS_SCP',
        patient_id='12345',
        study_date='20240301-20240331'
    )
    
    print(f"Found {len(studies)} studies:")
    for study in studies:
        print(f"  {study['study_date']}: {study['study_description']}")
    
    # Retrieve first study
    if studies:
        stats = qr.retrieve_study(
            'localhost',
            104,
            'PACS_SCP',
            studies[0]['study_uid'],
            'WORKSTATION'
        )
        print(f"Retrieval complete: {stats['completed']} images")

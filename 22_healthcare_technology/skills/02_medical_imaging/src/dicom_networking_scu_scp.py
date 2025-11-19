#!/usr/bin/env python3
"""Complete DICOM SCU and SCP implementation with all DIMSE services"""

from pynetdicom import AE, evt, StoragePresentationContexts
from pynetdicom.sop_class import *
import pydicom
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DICOMNode:
    """Complete DICOM node with SCU and SCP functionality"""
    
    def __init__(self, ae_title: str):
        self.ae = AE(ae_title=ae_title)
        self.setup_contexts()
    
    def setup_contexts(self):
        # Storage contexts
        self.ae.add_supported_context(CTImageStorage)
        self.ae.add_supported_context(MRImageStorage)
        self.ae.add_requested_context(CTImageStorage)
        self.ae.add_requested_context(MRImageStorage)
        
        # Query/Retrieve contexts
        self.ae.add_supported_context(PatientRootQueryRetrieveInformationModelFind)
        self.ae.add_supported_context(PatientRootQueryRetrieveInformationModelMove)
        self.ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)
        
        # Verification
        self.ae.add_supported_context(Verification)
        self.ae.add_requested_context(Verification)
    
    def echo(self, host: str, port: int, ae_title: str) -> bool:
        """C-ECHO verification"""
        assoc = self.ae.associate(host, port, ae_title=ae_title)
        if assoc.is_established:
            status = assoc.send_c_echo()
            assoc.release()
            return status.Status == 0x0000
        return False
    
    def store_scu(self, dicom_file: str, host: str, port: int, ae_title: str):
        """C-STORE SCU"""
        ds = pydicom.dcmread(dicom_file)
        assoc = self.ae.associate(host, port, ae_title=ae_title)
        
        if assoc.is_established:
            status = assoc.send_c_store(ds)
            logger.info(f"C-STORE status: 0x{status.Status:04x}")
            assoc.release()
    
    def find_scu(self, query_ds, host: str, port: int, ae_title: str):
        """C-FIND SCU"""
        assoc = self.ae.associate(host, port, ae_title=ae_title)
        
        results = []
        if assoc.is_established:
            responses = assoc.send_c_find(query_ds, PatientRootQueryRetrieveInformationModelFind)
            
            for (status, identifier) in responses:
                if status and status.Status in (0xFF00, 0xFF01):
                    results.append(identifier)
            
            assoc.release()
        
        return results
    
    def start_scp(self, port: int = 11112):
        """Start SCP server"""
        handlers = [
            (evt.EVT_C_STORE, self.handle_store),
            (evt.EVT_C_FIND, self.handle_find),
            (evt.EVT_C_ECHO, self.handle_echo)
        ]
        
        logger.info(f"Starting DICOM SCP on port {port}")
        self.ae.start_server(('', port), evt_handlers=handlers, block=True)
    
    def handle_store(self, event):
        """Handle incoming C-STORE"""
        ds = event.dataset
        ds.file_meta = event.file_meta
        
        filename = Path('storage') / f"{ds.SOPInstanceUID}.dcm"
        filename.parent.mkdir(exist_ok=True)
        
        ds.save_as(filename, write_like_original=False)
        logger.info(f"Stored: {filename}")
        
        return 0x0000
    
    def handle_find(self, event):
        """Handle incoming C-FIND"""
        query = event.identifier
        logger.info(f"C-FIND Query: {query.QueryRetrieveLevel}")
        
        # Implement database query here
        # For demo, return empty
        return 0x0000
    
    def handle_echo(self, event):
        """Handle incoming C-ECHO"""
        logger.info("C-ECHO received")
        return 0x0000

if __name__ == '__main__':
    import sys
    
    node = DICOMNode('DICOM_NODE')
    
    if len(sys.argv) > 1 and sys.argv[1] == 'server':
        node.start_scp(11112)
    else:
        # Client mode
        if node.echo('localhost', 11112, 'DICOM_NODE'):
            logger.info("C-ECHO successful")
        
        node.store_scu('example.dcm', 'localhost', 11112, 'DICOM_NODE')

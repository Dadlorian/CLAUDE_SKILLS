#!/usr/bin/env python3
"""
LIMS Integration API - Instrument Data Automation
Production-ready system for automated laboratory data capture
"""

import requests
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LIMSAPIClient:
    """Client for LIMS REST API interactions"""

    def __init__(self, base_url, api_token):
        """
        Initialize LIMS API client

        Parameters:
        -----------
        base_url : str
            Base URL of LIMS API (e.g., https://lims.company.com/api/v1)
        api_token : str
            Authentication token
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_sample(self, sample_id):
        """Retrieve sample information"""
        url = f"{self.base_url}/samples/{sample_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving sample {sample_id}: {e}")
            return None

    def create_result(self, sample_id, test_name, result_value, units="", analyst="System"):
        """
        Submit test result to LIMS

        Parameters:
        -----------
        sample_id : str
            Sample identifier
        test_name : str
            Test/assay name
        result_value : float or str
            Measured result
        units : str
            Measurement units
        analyst : str
            Analyst name (default: 'System' for automated)

        Returns:
        --------
        dict : Response with result_id if successful
        """
        url = f"{self.base_url}/results"
        payload = {
            'sample_id': sample_id,
            'test_name': test_name,
            'result_value': result_value,
            'units': units,
            'analyst': analyst,
            'timestamp': datetime.now().isoformat(),
            'status': 'Pending QC'
        }

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            logger.info(f"Result created for sample {sample_id}: {result_value} {units}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating result: {e}")
            return None

    def apply_qc_rules(self, sample_id, result_value, test_name):
        """
        Apply QC rules to validate results

        Returns:
        --------
        dict : QC status and any alerts
        """
        # Get test specifications
        url = f"{self.base_url}/tests/{test_name}/specifications"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            specs = response.json()

            # Check range
            if 'min_value' in specs and result_value < specs['min_value']:
                return {
                    'status': 'Out of Spec',
                    'alert': f"Result {result_value} below minimum {specs['min_value']}",
                    'action': 'Flag for review'
                }

            if 'max_value' in specs and result_value > specs['max_value']:
                return {
                    'status': 'Out of Spec',
                    'alert': f"Result {result_value} above maximum {specs['max_value']}",
                    'action': 'Flag for review'
                }

            return {'status': 'In Spec', 'alert': None, 'action': 'Auto-approve'}

        except requests.exceptions.RequestException as e:
            logger.error(f"Error applying QC rules: {e}")
            return {'status': 'Unknown', 'alert': 'QC check failed', 'action': 'Manual review'}

class HPLCDataParser:
    """Parse HPLC (High Performance Liquid Chromatography) data files"""

    @staticmethod
    def parse_agilent_chemstation(file_path):
        """
        Parse Agilent ChemStation report file

        Returns:
        --------
        dict : Parsed data including sample_id, peaks, retention times
        """
        logger.info(f"Parsing Agilent file: {file_path}")

        data = {
            'file_path': str(file_path),
            'parse_time': datetime.now().isoformat(),
            'instrument': 'Agilent HPLC',
            'peaks': []
        }

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract sample ID
            sample_match = re.search(r'Sample Name:\s*([A-Za-z0-9\-]+)', content)
            if sample_match:
                data['sample_id'] = sample_match.group(1)

            # Extract acquisition date
            date_match = re.search(r'Acquired:\s*(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2})', content)
            if date_match:
                data['acquisition_date'] = date_match.group(1)

            # Extract peak data (retention time, area, height)
            peak_pattern = r'(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.?\d*)'
            peaks = re.findall(peak_pattern, content)

            for i, (rt, area, height) in enumerate(peaks, 1):
                data['peaks'].append({
                    'peak_number': i,
                    'retention_time': float(rt),
                    'area': float(area),
                    'height': float(height) if height else 0
                })

            logger.info(f"Parsed {len(data['peaks'])} peaks from {data.get('sample_id', 'unknown')}")
            return data

        except Exception as e:
            logger.error(f"Error parsing file: {e}")
            return None

class GCMSDataParser:
    """Parse GC-MS (Gas Chromatography-Mass Spectrometry) data"""

    @staticmethod
    def parse_thermo_xcalibur(xml_file):
        """Parse Thermo Xcalibur XML export"""
        logger.info(f"Parsing GC-MS file: {xml_file}")

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            data = {
                'file_path': str(xml_file),
                'parse_time': datetime.now().isoformat(),
                'instrument': 'Thermo GC-MS',
                'compounds': []
            }

            # Navigate XML structure (simplified example)
            for compound in root.findall('.//Compound'):
                data['compounds'].append({
                    'name': compound.get('Name'),
                    'retention_time': float(compound.get('RT', 0)),
                    'area': float(compound.get('Area', 0)),
                    'concentration': float(compound.get('Conc', 0))
                })

            return data

        except Exception as e:
            logger.error(f"Error parsing XML: {e}")
            return None

class AutomatedDataCapture:
    """Automated laboratory data capture workflow"""

    def __init__(self, lims_client, watch_directory):
        """
        Initialize automated capture system

        Parameters:
        -----------
        lims_client : LIMSAPIClient
            Configured LIMS API client
        watch_directory : str or Path
            Directory to monitor for new data files
        """
        self.lims = lims_client
        self.watch_dir = Path(watch_directory)
        self.processed_dir = self.watch_dir / "processed"
        self.error_dir = self.watch_dir / "errors"

        # Create directories
        self.processed_dir.mkdir(exist_ok=True)
        self.error_dir.mkdir(exist_ok=True)

    def process_hplc_file(self, file_path):
        """Process a single HPLC data file"""
        logger.info(f"Processing file: {file_path}")

        # Parse data
        data = HPLCDataParser.parse_agilent_chemstation(file_path)
        if not data or 'sample_id' not in data:
            logger.error(f"Failed to parse file or extract sample ID")
            self._move_to_error(file_path, "Parse failure")
            return False

        # Get sample info from LIMS
        sample = self.lims.get_sample(data['sample_id'])
        if not sample:
            logger.error(f"Sample {data['sample_id']} not found in LIMS")
            self._move_to_error(file_path, "Sample not found")
            return False

        # Upload each peak as a result
        for peak in data['peaks']:
            result = self.lims.create_result(
                sample_id=data['sample_id'],
                test_name='HPLC Peak Area',
                result_value=peak['area'],
                units='mAU*s',
                analyst='Automated System'
            )

            if result:
                # Apply QC rules
                qc_status = self.lims.apply_qc_rules(
                    sample_id=data['sample_id'],
                    result_value=peak['area'],
                    test_name='HPLC Peak Area'
                )
                logger.info(f"QC Status: {qc_status['status']}")

                if qc_status.get('alert'):
                    logger.warning(f"QC Alert: {qc_status['alert']}")

        # Move to processed
        self._move_to_processed(file_path)
        return True

    def scan_and_process(self):
        """Scan watch directory and process new files"""
        logger.info(f"Scanning directory: {self.watch_dir}")

        # Look for HPLC data files (example: .txt, .csv, .D folders)
        for file_path in self.watch_dir.glob('*.txt'):
            if file_path.is_file():
                self.process_hplc_file(file_path)

    def _move_to_processed(self, file_path):
        """Move processed file to archive"""
        dest = self.processed_dir / file_path.name
        file_path.rename(dest)
        logger.info(f"Moved to processed: {dest}")

    def _move_to_error(self, file_path, reason=""):
        """Move problematic file to error directory"""
        dest = self.error_dir / file_path.name
        file_path.rename(dest)
        logger.error(f"Moved to errors: {dest} (Reason: {reason})")

# Example usage
if __name__ == "__main__":
    # Configuration
    LIMS_URL = "https://lims.example.com/api/v1"
    API_TOKEN = "your-api-token-here"  # In production, use environment variable
    WATCH_DIR = "/data/instruments/hplc/export"

    # Initialize
    lims_client = LIMSAPIClient(LIMS_URL, API_TOKEN)
    automation = AutomatedDataCapture(lims_client, WATCH_DIR)

    # Process files
    automation.scan_and_process()

    print("\n" + "="*80)
    print("Automated Data Capture Complete")
    print("="*80)

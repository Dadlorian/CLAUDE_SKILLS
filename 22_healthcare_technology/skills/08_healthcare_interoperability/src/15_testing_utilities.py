#!/usr/bin/env python3
"""Testing Utilities - Unit and integration testing helpers"""

import unittest
from typing import Dict, Any
from datetime import datetime

class HealthcareTestCase(unittest.TestCase):
    """Base healthcare test case"""

    def setUp(self):
        """Set up test fixtures"""
        self.sample_patient = {
            'resourceType': 'Patient',
            'id': 'test-123',
            'name': [{'family': 'Doe', 'given': ['John']}],
            'birthDate': '1970-01-01'
        }

        self.sample_observation = {
            'resourceType': 'Observation',
            'id': 'obs-123',
            'code': {'coding': [{'code': '2345-7', 'system': 'http://loinc.org'}]},
            'valueQuantity': {'value': 95, 'unit': 'mg/dL'}
        }

    def assert_valid_patient(self, patient: Dict):
        """Assert patient is valid"""
        self.assertEqual(patient.get('resourceType'), 'Patient')
        self.assertIn('id', patient)
        self.assertIn('name', patient)

    def assert_valid_observation(self, obs: Dict):
        """Assert observation is valid"""
        self.assertEqual(obs.get('resourceType'), 'Observation')
        self.assertIn('code', obs)

class MockFHIRServer:
    """Mock FHIR server for testing"""
    def __init__(self):
        self.resources = {}

    def create(self, resource_type: str, resource: Dict) -> Dict:
        """Mock create"""
        resource['id'] = 'mock-id'
        self.resources[resource_type] = resource
        return resource

    def read(self, resource_type: str, resource_id: str) -> Dict:
        """Mock read"""
        return self.resources.get(resource_type, {})

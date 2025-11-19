"""
Blue Button CCDA XML Parser
Parses CCDA/CDA documents and extracts clinical data
"""

from lxml import etree
from datetime import datetime
import json

class BlueButtonParser:
    """Parse CCDA XML and extract healthcare data"""

    NS = {
        'cda': 'urn:hl7-org:v3',
        'sdtc': 'urn:hl7-org:sdtc'
    }

    def __init__(self, ccda_file_path):
        self.tree = etree.parse(ccda_file_path)
        self.root = self.tree.getroot()

    def parse_complete_record(self):
        """Parse complete CCDA document"""
        return {
            'patient': self.extract_patient(),
            'problems': self.extract_problems(),
            'medications': self.extract_medications(),
            'allergies': self.extract_allergies(),
            'labs': self.extract_labs(),
            'vital_signs': self.extract_vital_signs(),
            'immunizations': self.extract_immunizations(),
            'procedures': self.extract_procedures()
        }

    def extract_patient(self):
        """Extract patient demographics"""
        record_target = self.root.xpath(
            '//cda:recordTarget/cda:patientRole',
            namespaces=self.NS
        )
        if not record_target:
            return None

        patient_role = record_target[0]
        patient = patient_role.find('cda:patient', self.NS)

        return {
            'mrn': patient_role.find('cda:id', self.NS).get('extension'),
            'first_name': patient.find('cda:name/cda:given', self.NS).text if patient.find('cda:name/cda:given', self.NS) is not None else None,
            'last_name': patient.find('cda:name/cda:family', self.NS).text if patient.find('cda:name/cda:family', self.NS) is not None else None,
            'dob': patient.find('cda:birthTime', self.NS).get('value') if patient.find('cda:birthTime', self.NS) is not None else None,
            'gender': patient.find('cda:administrativeGenderCode', self.NS).get('code') if patient.find('cda:administrativeGenderCode', self.NS) is not None else None
        }

    def extract_problems(self):
        """Extract problem list (diagnoses)"""
        problems = []
        problem_section = self.root.xpath(
            '//cda:section[cda:templateId/@root="2.16.840.1.113883.10.20.22.2.1.1"]',
            namespaces=self.NS
        )

        if not problem_section:
            return problems

        entries = problem_section[0].xpath('.//cda:entry', namespaces=self.NS)

        for entry in entries:
            act = entry.find('cda:act', self.NS)
            if act is not None:
                obs = act.find('.//cda:observation', self.NS)
                if obs is not None:
                    code_elem = obs.find('cda:code', self.NS)
                    problems.append({
                        'code': code_elem.get('code') if code_elem is not None else None,
                        'code_system': code_elem.get('codeSystem') if code_elem is not None else None,
                        'description': code_elem.get('displayName') if code_elem is not None else None,
                        'status': obs.find('cda:statusCode', self.NS).get('code') if obs.find('cda:statusCode', self.NS) is not None else None
                    })

        return problems

    def extract_medications(self):
        """Extract medication list"""
        medications = []
        med_section = self.root.xpath(
            '//cda:section[cda:templateId/@root="2.16.840.1.113883.10.20.22.2.1"]',
            namespaces=self.NS
        )

        if not med_section:
            return medications

        entries = med_section[0].xpath('.//cda:entry', namespaces=self.NS)

        for entry in entries:
            subadmin = entry.find('cda:substanceAdministration', self.NS)
            if subadmin is not None:
                med_material = subadmin.find(
                    './/cda:consumable/cda:manufacturedProduct/cda:manufacturedMaterial',
                    self.NS
                )
                dose = subadmin.find('cda:doseQuantity', self.NS)

                medications.append({
                    'drug_name': med_material.find('cda:code', self.NS).get('displayName') if med_material is not None else None,
                    'code': med_material.find('cda:code', self.NS).get('code') if med_material is not None else None,
                    'dose': dose.get('value') if dose is not None else None,
                    'unit': dose.get('unit') if dose is not None else None,
                    'frequency': self._extract_frequency(subadmin),
                    'status': subadmin.find('cda:statusCode', self.NS).get('code') if subadmin.find('cda:statusCode', self.NS) is not None else None
                })

        return medications

    def extract_allergies(self):
        """Extract allergy list"""
        allergies = []
        allergy_section = self.root.xpath(
            '//cda:section[cda:templateId/@root="2.16.840.1.113883.10.20.22.2.6.1"]',
            namespaces=self.NS
        )

        if not allergy_section:
            return allergies

        entries = allergy_section[0].xpath('.//cda:entry', namespaces=self.NS)

        for entry in entries:
            act = entry.find('cda:act', self.NS)
            if act is not None:
                obs = act.find('.//cda:observation', self.NS)
                if obs is not None:
                    substance = obs.find('.//cda:participant/cda:participantRole/cda:playingEntity/cda:code', self.NS)
                    allergies.append({
                        'substance': substance.get('displayName') if substance is not None else None,
                        'code': substance.get('code') if substance is not None else None,
                        'reaction': self._extract_reaction(obs),
                        'severity': self._extract_severity(obs)
                    })

        return allergies

    def extract_labs(self):
        """Extract lab results"""
        labs = []
        results_section = self.root.xpath(
            '//cda:section[cda:templateId/@root="2.16.840.1.113883.10.20.22.2.3.1"]',
            namespaces=self.NS
        )

        if not results_section:
            return labs

        organizers = results_section[0].xpath('.//cda:organizer', namespaces=self.NS)

        for organizer in organizers:
            components = organizer.xpath('.//cda:component/cda:observation', namespaces=self.NS)
            for obs in components:
                code = obs.find('cda:code', self.NS)
                value = obs.find('cda:value', self.NS)

                labs.append({
                    'test_name': code.get('displayName') if code is not None else None,
                    'code': code.get('code') if code is not None else None,
                    'value': value.get('value') if value is not None else None,
                    'unit': value.get('unit') if value is not None else None,
                    'date': obs.find('cda:effectiveTime', self.NS).get('value') if obs.find('cda:effectiveTime', self.NS) is not None else None
                })

        return labs

    def extract_vital_signs(self):
        """Extract vital signs"""
        vitals = []
        vital_section = self.root.xpath(
            '//cda:section[cda:templateId/@root="2.16.840.1.113883.10.20.22.2.4.1"]',
            namespaces=self.NS
        )

        if not vital_section:
            return vitals

        organizers = vital_section[0].xpath('.//cda:organizer', namespaces=self.NS)

        for organizer in organizers:
            observations = organizer.xpath('.//cda:component/cda:observation', namespaces=self.NS)
            for obs in observations:
                code = obs.find('cda:code', self.NS)
                value = obs.find('cda:value', self.NS)

                vitals.append({
                    'vital_name': code.get('displayName') if code is not None else None,
                    'code': code.get('code') if code is not None else None,
                    'value': value.get('value') if value is not None else None,
                    'unit': value.get('unit') if value is not None else None,
                    'date': obs.find('cda:effectiveTime', self.NS).get('value') if obs.find('cda:effectiveTime', self.NS) is not None else None
                })

        return vitals

    def extract_immunizations(self):
        """Extract immunization records"""
        immunizations = []
        immun_section = self.root.xpath(
            '//cda:section[cda:templateId/@root="2.16.840.1.113883.10.20.22.2.2.1"]',
            namespaces=self.NS
        )

        if not immun_section:
            return immunizations

        return immunizations

    def extract_procedures(self):
        """Extract procedures"""
        procedures = []
        proc_section = self.root.xpath(
            '//cda:section[cda:templateId/@root="2.16.840.1.113883.10.20.22.2.7.1"]',
            namespaces=self.NS
        )

        if not proc_section:
            return procedures

        return procedures

    def _extract_frequency(self, med_element):
        """Extract medication frequency"""
        timing = med_element.find('.//cda:effectiveTime[@xsi:type="PIVL_TS"]', self.NS)
        if timing is not None:
            return timing.get('institutionSpecified')
        return None

    def _extract_reaction(self, allergy_obs):
        """Extract allergy reaction"""
        reaction_obs = allergy_obs.find('.//cda:entryRelationship[cda:observation/cda:code/@code="ROLO"]', self.NS)
        if reaction_obs is not None:
            value = reaction_obs.find('.//cda:value', self.NS)
            return value.get('displayName') if value is not None else None
        return None

    def _extract_severity(self, allergy_obs):
        """Extract allergy severity"""
        severity_obs = allergy_obs.find('.//cda:entryRelationship[cda:observation/cda:code/@code="SEV"]', self.NS)
        if severity_obs is not None:
            value = severity_obs.find('.//cda:value', self.NS)
            return value.get('displayName') if value is not None else None
        return None

    def to_json(self):
        """Convert parsed data to JSON"""
        data = self.parse_complete_record()
        return json.dumps(data, indent=2, default=str)

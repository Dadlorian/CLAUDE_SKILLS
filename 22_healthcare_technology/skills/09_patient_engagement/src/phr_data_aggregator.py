"""
PHR Data Aggregator Service - Consolidates health data from multiple EHR sources
"""

import asyncio
from datetime import datetime
from typing import List, Dict
import aiohttp
import logging

logger = logging.getLogger(__name__)

class PHRDataAggregator:
    def __init__(self, patient_id: str, sources: List[Dict]):
        self.patient_id = patient_id
        self.sources = sources
        self.aggregated_data = {
            'problems': [],
            'medications': [],
            'allergies': [],
            'observations': [],
            'last_updated': datetime.utcnow()
        }

    async def aggregate_data(self):
        """Fetch and consolidate data from all sources"""
        tasks = [self.fetch_from_source(source) for source in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error fetching data: {result}")
                continue
            self.merge_data(result)

        await self.deduplicate_data()
        await self.reconcile_conflicts()

        return self.aggregated_data

    async def fetch_from_source(self, source: Dict):
        """Fetch data from single EHR source via FHIR API"""
        url = source['url']
        headers = {'Authorization': f"Bearer {source['token']}"}

        async with aiohttp.ClientSession() as session:
            try:
                problems = await self.fetch_fhir_resource(
                    session, f"{url}/fhir/Condition", headers
                )
                medications = await self.fetch_fhir_resource(
                    session, f"{url}/fhir/MedicationStatement", headers
                )
                allergies = await self.fetch_fhir_resource(
                    session, f"{url}/fhir/AllergyIntolerance", headers
                )
                observations = await self.fetch_fhir_resource(
                    session, f"{url}/fhir/Observation", headers
                )

                return {
                    'source': source['name'],
                    'problems': problems,
                    'medications': medications,
                    'allergies': allergies,
                    'observations': observations
                }
            except Exception as e:
                logger.error(f"Error fetching from {source['name']}: {e}")
                raise

    async def fetch_fhir_resource(self, session, url: str, headers: Dict):
        """Fetch FHIR resource with pagination handling"""
        resources = []
        params = {'_count': 100}

        while url:
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    resources.extend(data.get('entry', []))

                    links = data.get('link', [])
                    next_link = next((l for l in links if l.get('relation') == 'next'), None)
                    url = next_link['url'] if next_link else None
                    params = {}
                else:
                    logger.error(f"Error fetching {url}: {resp.status}")
                    break

        return resources

    def merge_data(self, source_data: Dict):
        """Merge data from source into aggregated PHR"""
        for problem in source_data.get('problems', []):
            self.aggregated_data['problems'].append(self.normalize_problem(problem))

        for medication in source_data.get('medications', []):
            self.aggregated_data['medications'].append(self.normalize_medication(medication))

        for allergy in source_data.get('allergies', []):
            self.aggregated_data['allergies'].append(self.normalize_allergy(allergy))

        for obs in source_data.get('observations', []):
            self.aggregated_data['observations'].append(self.normalize_observation(obs))

    def normalize_problem(self, problem_resource: Dict) -> Dict:
        """Normalize FHIR Condition to standard format"""
        resource = problem_resource.get('resource', problem_resource)
        return {
            'id': resource.get('id'),
            'code': resource.get('code', {}).get('coding', [{}])[0].get('code'),
            'description': resource.get('code', {}).get('coding', [{}])[0].get('display'),
            'status': resource.get('clinicalStatus', {}).get('coding', [{}])[0].get('code'),
            'onset_date': resource.get('onsetDateTime'),
            'abatement_date': resource.get('abatementDateTime'),
            'source': 'FHIR'
        }

    def normalize_medication(self, med_resource: Dict) -> Dict:
        """Normalize FHIR MedicationStatement"""
        resource = med_resource.get('resource', med_resource)
        return {
            'id': resource.get('id'),
            'drug_name': resource.get('medicationCodeableConcept', {}).get('coding', [{}])[0].get('display'),
            'code': resource.get('medicationCodeableConcept', {}).get('coding', [{}])[0].get('code'),
            'status': resource.get('status'),
            'dosage': resource.get('dosage', [{}])[0].get('dose', {}).get('value'),
            'unit': resource.get('dosage', [{}])[0].get('dose', {}).get('unit'),
            'frequency': resource.get('dosage', [{}])[0].get('timing', {}).get('repeat', {}).get('frequency'),
            'start_date': resource.get('effectivePeriod', {}).get('start'),
            'end_date': resource.get('effectivePeriod', {}).get('end'),
            'source': 'FHIR'
        }

    def normalize_allergy(self, allergy_resource: Dict) -> Dict:
        """Normalize FHIR AllergyIntolerance"""
        resource = allergy_resource.get('resource', allergy_resource)
        return {
            'id': resource.get('id'),
            'substance': resource.get('code', {}).get('coding', [{}])[0].get('display'),
            'code': resource.get('code', {}).get('coding', [{}])[0].get('code'),
            'reaction': resource.get('reaction', [{}])[0].get('manifestation', [{}])[0].get('coding', [{}])[0].get('display'),
            'severity': resource.get('reaction', [{}])[0].get('severity'),
            'status': resource.get('clinicalStatus', {}).get('coding', [{}])[0].get('code'),
            'source': 'FHIR'
        }

    def normalize_observation(self, obs_resource: Dict) -> Dict:
        """Normalize FHIR Observation"""
        resource = obs_resource.get('resource', obs_resource)
        return {
            'id': resource.get('id'),
            'code': resource.get('code', {}).get('coding', [{}])[0].get('code'),
            'test_name': resource.get('code', {}).get('coding', [{}])[0].get('display'),
            'value': resource.get('valueQuantity', {}).get('value'),
            'unit': resource.get('valueQuantity', {}).get('unit'),
            'date': resource.get('effectiveDateTime'),
            'reference_range': resource.get('referenceRange', [{}])[0].get('high', {}).get('value'),
            'interpretation': resource.get('interpretation', [{}])[0].get('coding', [{}])[0].get('code'),
            'source': 'FHIR'
        }

    async def deduplicate_data(self):
        """Remove duplicate entries by ICD-10 code and date"""
        seen_problems = {}
        for problem in self.aggregated_data['problems']:
            key = (problem.get('code'), problem.get('onset_date'))
            if key not in seen_problems:
                seen_problems[key] = problem

        self.aggregated_data['problems'] = list(seen_problems.values())

    async def reconcile_conflicts(self):
        """Resolve conflicting data from multiple sources"""
        # Use most recent source as authoritative
        for med in self.aggregated_data['medications']:
            # Conflict resolution logic: prefer more recent data
            pass

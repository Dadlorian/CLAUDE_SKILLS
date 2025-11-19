"""
OMOP CDM ETL Pipeline
Transforms EHR data to OMOP Common Data Model
"""

import pandas as pd
import psycopg2
from datetime import datetime

class OMOPETLPipeline:
    def __init__(self, source_conn, target_conn, vocab_conn):
        self.source_conn = source_conn
        self.target_conn = target_conn
        self.vocab_conn = vocab_conn

    def extract_patients(self):
        """Extract patients from source EHR"""
        query = """
            SELECT
                patient_id,
                mrn,
                first_name,
                last_name,
                date_of_birth,
                date_of_death,
                gender,
                race,
                ethnicity,
                zip_code
            FROM source_patients
            WHERE last_modified_date > %(last_etl_date)s
        """
        return pd.read_sql(query, self.source_conn, params={'last_etl_date': self.get_last_etl_date()})

    def transform_to_person(self, source_patients):
        """Transform to OMOP PERSON table"""
        persons = []

        for _, patient in source_patients.iterrows():
            # Map gender to OMOP concept
            gender_concept_id = self.map_to_concept(
                source_code=patient['gender'],
                source_vocabulary='Gender',
                target_domain='Gender'
            )

            # Map race to OMOP concept
            race_concept_id = self.map_to_concept(
                source_code=patient['race'],
                source_vocabulary='Race',
                target_domain='Race'
            )

            # Map ethnicity to OMOP concept
            ethnicity_concept_id = self.map_to_concept(
                source_code=patient['ethnicity'],
                source_vocabulary='Ethnicity',
                target_domain='Ethnicity'
            )

            persons.append({
                'person_id': self.generate_person_id(patient['patient_id']),
                'gender_concept_id': gender_concept_id,
                'year_of_birth': patient['date_of_birth'].year,
                'month_of_birth': patient['date_of_birth'].month,
                'day_of_birth': patient['date_of_birth'].day,
                'birth_datetime': patient['date_of_birth'],
                'death_datetime': patient['date_of_death'],
                'race_concept_id': race_concept_id,
                'ethnicity_concept_id': ethnicity_concept_id,
                'person_source_value': patient['mrn'],
                'gender_source_value': patient['gender'],
                'race_source_value': patient['race'],
                'ethnicity_source_value': patient['ethnicity']
            })

        return pd.DataFrame(persons)

    def map_to_concept(self, source_code, source_vocabulary, target_domain):
        """Map source code to standard OMOP concept"""
        query = """
            SELECT c2.concept_id
            FROM concept c1
            JOIN concept_relationship cr ON c1.concept_id = cr.concept_id_1
            JOIN concept c2 ON cr.concept_id_2 = c2.concept_id
            WHERE c1.vocabulary_id = %(source_vocab)s
                AND c1.concept_code = %(source_code)s
                AND cr.relationship_id = 'Maps to'
                AND c2.standard_concept = 'S'
                AND c2.domain_id = %(target_domain)s
        """

        with self.vocab_conn.cursor() as cur:
            cur.execute(query, {
                'source_vocab': source_vocabulary,
                'source_code': source_code,
                'target_domain': target_domain
            })
            result = cur.fetchone()
            return result[0] if result else 0

    def transform_diagnoses(self, source_diagnoses):
        """Transform diagnoses to OMOP CONDITION_OCCURRENCE"""
        conditions = []

        for _, diag in source_diagnoses.iterrows():
            # Map ICD-10 to SNOMED
            condition_concept_id = self.map_icd10_to_snomed(diag['icd10_code'])

            conditions.append({
                'condition_occurrence_id': self.generate_id(),
                'person_id': self.get_omop_person_id(diag['patient_id']),
                'condition_concept_id': condition_concept_id,
                'condition_start_date': diag['diagnosis_date'],
                'condition_start_datetime': diag['diagnosis_datetime'],
                'condition_type_concept_id': 32020,  # EHR diagnosis
                'visit_occurrence_id': self.get_omop_visit_id(diag['encounter_id']),
                'condition_source_value': diag['icd10_code'],
                'condition_source_concept_id': self.get_icd10_concept_id(diag['icd10_code'])
            })

        return pd.DataFrame(conditions)

    def map_icd10_to_snomed(self, icd10_code):
        """Map ICD-10-CM code to standard SNOMED concept"""
        return self.map_to_concept(
            source_code=icd10_code,
            source_vocabulary='ICD10CM',
            target_domain='Condition'
        )

    def load_to_omop(self, table_name, dataframe):
        """Load data to OMOP CDM table"""
        if len(dataframe) == 0:
            return

        # Use psycopg2 copy_from for efficient loading
        with self.target_conn.cursor() as cur:
            # Create temp CSV
            temp_csv = f'/tmp/{table_name}_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv'
            dataframe.to_csv(temp_csv, index=False, header=False)

            # Copy to table
            with open(temp_csv, 'r') as f:
                cur.copy_from(f, f'omop_cdm.{table_name}', sep=',', null='')

            self.target_conn.commit()

    def run_etl(self):
        """Execute full OMOP ETL pipeline"""
        # Patients -> PERSON
        source_patients = self.extract_patients()
        omop_persons = self.transform_to_person(source_patients)
        self.load_to_omop('person', omop_persons)

        # Encounters -> VISIT_OCCURRENCE
        # Diagnoses -> CONDITION_OCCURRENCE
        # Medications -> DRUG_EXPOSURE
        # Labs -> MEASUREMENT
        # etc.

        print(f"ETL completed: {len(omop_persons)} persons loaded")

if __name__ == "__main__":
    # Connection details
    source_conn = psycopg2.connect("dbname=ehr_source user=etl_user")
    target_conn = psycopg2.connect("dbname=omop_cdm user=omop_user")
    vocab_conn = psycopg2.connect("dbname=omop_vocab user=omop_user")

    # Run ETL
    pipeline = OMOPETLPipeline(source_conn, target_conn, vocab_conn)
    pipeline.run_etl()

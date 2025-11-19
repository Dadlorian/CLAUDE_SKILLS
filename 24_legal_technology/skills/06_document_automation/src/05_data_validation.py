"""
Data Validation for Document Generation
Validates data before generating legal documents to ensure correctness.

Dependencies: pydantic
Install: pip install pydantic
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
import re


class JurisdictionEnum(Enum):
    """US States and jurisdictions."""
    CALIFORNIA = "CA"
    NEW_YORK = "NY"
    TEXAS = "TX"
    FLORIDA = "FL"
    FEDERAL = "FEDERAL"


class PartyType(Enum):
    """Entity types."""
    INDIVIDUAL = "individual"
    CORPORATION = "corporation"
    LLC = "llc"
    PARTNERSHIP = "partnership"


class ValidationError(Exception):
    """Custom validation error."""
    pass


class Party(BaseModel):
    """Validates party information."""
    name: str = Field(..., min_length=1, max_length=255)
    party_type: PartyType
    address: str = Field(..., min_length=10, max_length=500)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        if v:
            # Simple validation: remove non-digits, check length
            digits = re.sub(r'\D', '', v)
            if len(digits) != 10:
                raise ValueError('Phone number must have 10 digits')
        return v

    @validator('name')
    def validate_name(cls, v):
        """Validate party name."""
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class ServiceAgreementData(BaseModel):
    """Validates service agreement data."""
    date: date = Field(default_factory=date.today)
    party_a: Party
    party_b: Party
    services: List[str] = Field(..., min_items=1, max_items=20)
    hourly_rate: float = Field(..., gt=0, le=10000)
    monthly_retainer: Optional[float] = Field(None, gt=0, le=100000)
    payment_terms: int = Field(default=30, ge=7, le=90)
    start_date: date
    duration_years: int = Field(default=1, ge=1, le=10)
    termination_notice_days: int = Field(default=30, ge=0, le=180)
    confidentiality_period_years: int = Field(default=3, ge=1, le=10)
    governing_state: JurisdictionEnum = JurisdictionEnum.CALIFORNIA

    @validator('services')
    def validate_services(cls, v):
        """Validate service descriptions."""
        for service in v:
            if not service or len(service) < 5:
                raise ValueError('Each service description must be at least 5 characters')
        return v

    @validator('start_date')
    def validate_start_date(cls, v, values):
        """Validate start date is not in past."""
        if v < date.today():
            raise ValueError('Start date cannot be in the past')
        return v

    @validator('monthly_retainer')
    def validate_retainer(cls, v, values):
        """Validate retainer against hourly rate."""
        if v and 'hourly_rate' in values:
            min_retainer = values['hourly_rate'] * 40  # 40 hours minimum
            if v < min_retainer:
                raise ValueError(
                    f'Monthly retainer should be at least ${min_retainer} '
                    f'(160 hours @ ${values["hourly_rate"]}/hr)'
                )
        return v


class EmploymentAgreementData(BaseModel):
    """Validates employment agreement data."""
    employee: Party
    employer: Party
    job_title: str = Field(..., min_length=3, max_length=100)
    department: str = Field(..., min_length=3, max_length=100)
    location: str = Field(..., min_length=5, max_length=255)
    start_date: date
    annual_salary: float = Field(..., gt=0, le=5000000)
    bonus_percentage: Optional[float] = Field(None, ge=0, le=200)
    stock_options: Optional[int] = Field(None, ge=0)
    reports_to: str = Field(..., min_length=3, max_length=100)

    @validator('annual_salary')
    def validate_salary(cls, v):
        """Validate salary is reasonable."""
        if v < 15000:
            raise ValueError('Annual salary must be at least $15,000')
        return v

    @validator('bonus_percentage')
    def validate_bonus(cls, v):
        """Validate bonus percentage."""
        if v and v > 100:
            raise ValueError('Bonus percentage should not exceed 100%')
        return v

    @validator('start_date')
    def validate_start_date(cls, v):
        """Validate start date."""
        if v < date.today():
            raise ValueError('Start date cannot be in the past')
        return v


class NDAAgreementData(BaseModel):
    """Validates NDA data."""
    date: date = Field(default_factory=date.today)
    disclosing_party: Party
    receiving_party: Party
    confidential_categories: List[str] = Field(..., min_items=1, max_items=10)
    confidentiality_period_years: int = Field(default=3, ge=1, le=10)
    permitted_uses: List[str] = Field(default_factory=lambda: ["Evaluating business opportunity"])
    governing_state: JurisdictionEnum = JurisdictionEnum.CALIFORNIA

    @validator('confidential_categories')
    def validate_categories(cls, v):
        """Validate category descriptions."""
        for category in v:
            if len(category) < 5:
                raise ValueError('Each category must be at least 5 characters')
        return v


class ContractData(BaseModel):
    """Validates contract data."""
    contract_title: str = Field(..., min_length=5, max_length=200)
    date: date = Field(default_factory=date.today)
    party_a: Party
    party_b: Party
    effective_date: date
    expiration_date: date
    governing_state: JurisdictionEnum = JurisdictionEnum.CALIFORNIA

    @validator('expiration_date')
    def validate_expiration(cls, v, values):
        """Validate expiration date is after effective date."""
        if 'effective_date' in values and v <= values['effective_date']:
            raise ValueError('Expiration date must be after effective date')
        return v


class DocumentValidator:
    """Validates document data before generation."""

    @staticmethod
    def validate_service_agreement(data: dict) -> ServiceAgreementData:
        """Validate and return service agreement data."""
        try:
            return ServiceAgreementData(**data)
        except Exception as e:
            raise ValidationError(f"Service agreement validation failed: {str(e)}")

    @staticmethod
    def validate_employment_agreement(data: dict) -> EmploymentAgreementData:
        """Validate and return employment agreement data."""
        try:
            return EmploymentAgreementData(**data)
        except Exception as e:
            raise ValidationError(f"Employment agreement validation failed: {str(e)}")

    @staticmethod
    def validate_nda(data: dict) -> NDAAgreementData:
        """Validate and return NDA data."""
        try:
            return NDAAgreementData(**data)
        except Exception as e:
            raise ValidationError(f"NDA validation failed: {str(e)}")

    @staticmethod
    def validate_contract(data: dict) -> ContractData:
        """Validate and return contract data."""
        try:
            return ContractData(**data)
        except Exception as e:
            raise ValidationError(f"Contract validation failed: {str(e)}")


def example_validate_service_agreement():
    """Validate service agreement data."""
    data = {
        'date': date(2024, 1, 1),
        'party_a': {
            'name': 'Legal Solutions LLC',
            'party_type': 'llc',
            'address': '123 Law Street, San Francisco, CA 94102',
            'email': 'info@legalsolutions.com',
            'phone': '4155551234'
        },
        'party_b': {
            'name': 'Acme Corporation',
            'party_type': 'corporation',
            'address': '456 Business Ave, San Jose, CA 95110',
            'email': 'legal@acme.com',
            'phone': '4085551234'
        },
        'services': [
            'Contract drafting and review',
            'Legal research and analysis',
            'Compliance consulting',
            'Litigation support'
        ],
        'hourly_rate': 250.00,
        'monthly_retainer': 5000.00,
        'payment_terms': 30,
        'start_date': date(2024, 1, 15),
        'duration_years': 1,
        'termination_notice_days': 30,
        'confidentiality_period_years': 3,
        'governing_state': 'CA'
    }

    try:
        validated = DocumentValidator.validate_service_agreement(data)
        print("Service Agreement Data Valid:")
        print(f"  Party A: {validated.party_a.name}")
        print(f"  Party B: {validated.party_b.name}")
        print(f"  Services: {len(validated.services)} services")
        print(f"  Hourly Rate: ${validated.hourly_rate}")
        return validated
    except ValidationError as e:
        print(f"Validation Error: {e}")
        return None


def example_validate_employment():
    """Validate employment agreement data."""
    data = {
        'employee': {
            'name': 'Jane Smith',
            'party_type': 'individual',
            'address': '789 Oak Lane, San Francisco, CA 94103',
            'email': 'jane.smith@email.com',
            'phone': '5105551234'
        },
        'employer': {
            'name': 'TechCorp Industries',
            'party_type': 'corporation',
            'address': '321 Tech Drive, San Francisco, CA 94102',
            'email': 'hr@techcorp.com',
            'phone': '4155552222'
        },
        'job_title': 'Senior Legal Counsel',
        'department': 'Legal & Compliance',
        'location': 'San Francisco, CA',
        'start_date': date(2024, 1, 15),
        'annual_salary': 180000.00,
        'bonus_percentage': 20.0,
        'stock_options': 5000,
        'reports_to': 'General Counsel'
    }

    try:
        validated = DocumentValidator.validate_employment_agreement(data)
        print("\nEmployment Agreement Data Valid:")
        print(f"  Employee: {validated.employee.name}")
        print(f"  Employer: {validated.employer.name}")
        print(f"  Position: {validated.job_title}")
        print(f"  Salary: ${validated.annual_salary:,.2f}")
        return validated
    except ValidationError as e:
        print(f"Validation Error: {e}")
        return None


def example_validate_invalid_data():
    """Demonstrate validation error handling."""
    print("\n--- Testing Invalid Data ---")

    invalid_data = {
        'party_a': {
            'name': 'ABC',  # Too short
            'party_type': 'llc',
            'address': '123 Street'  # Too short
        },
        'party_b': {
            'name': 'XYZ Corp',
            'party_type': 'corporation',
            'address': '456 Avenue'
        },
        'services': ['Short'],  # Too short
        'hourly_rate': -100,  # Negative rate
        'start_date': date(2020, 1, 1),  # Past date
    }

    try:
        validated = DocumentValidator.validate_service_agreement(invalid_data)
    except ValidationError as e:
        print(f"Expected validation error: {e}")


if __name__ == "__main__":
    example_validate_service_agreement()
    example_validate_employment()
    example_validate_invalid_data()
    print("\nValidation examples completed!")

#!/usr/bin/env python3
"""
Date validation for legal documents
Handle complex date logic and deadline calculations
"""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Tuple, Dict, Optional

class DateValidator:
    @staticmethod
    def validate_date_format(date_string: str, format_str: str = '%m/%d/%Y') -> Tuple[bool, Optional[datetime]]:
        """Validate date string against format."""
        try:
            parsed_date = datetime.strptime(date_string, format_str)
            return True, parsed_date
        except ValueError:
            return False, None
    
    @staticmethod
    def is_future_date(date_obj: datetime) -> bool:
        """Check if date is in the future."""
        return date_obj > datetime.now()
    
    @staticmethod
    def is_past_date(date_obj: datetime) -> bool:
        """Check if date is in the past."""
        return date_obj < datetime.now()
    
    @staticmethod
    def is_valid_date_range(start_date: datetime, end_date: datetime, min_days: int = 0) -> bool:
        """Validate that end date is after start date with minimum duration."""
        if end_date <= start_date:
            return False
        
        duration = (end_date - start_date).days
        return duration >= min_days
    
    @staticmethod
    def calculate_deadline(start_date: datetime, days: int = None, months: int = None, 
                          years: int = None, skip_weekends: bool = False) -> datetime:
        """Calculate deadline from start date."""
        if days:
            deadline = start_date + timedelta(days=days)
        elif months:
            deadline = start_date + relativedelta(months=months)
        elif years:
            deadline = start_date + relativedelta(years=years)
        else:
            raise ValueError("Must specify days, months, or years")
        
        if skip_weekends:
            # Skip weekends for business day deadline
            while deadline.weekday() >= 5:  # 5=Saturday, 6=Sunday
                deadline += timedelta(days=1)
        
        return deadline
    
    @staticmethod
    def is_within_deadline(target_date: datetime, deadline: datetime) -> bool:
        """Check if target date is within deadline."""
        return target_date <= deadline
    
    @staticmethod
    def days_until_deadline(deadline: datetime) -> int:
        """Calculate days remaining until deadline."""
        now = datetime.now()
        return (deadline - now).days
    
    @staticmethod
    def validate_filing_deadline(filing_date: datetime, statute_of_limitations_days: int,
                                 original_event_date: datetime) -> Dict:
        """Validate filing date within statute of limitations."""
        deadline = original_event_date + timedelta(days=statute_of_limitations_days)
        is_timely = filing_date <= deadline
        days_remaining = (deadline - datetime.now()).days
        
        return {
            'is_timely': is_timely,
            'deadline': deadline,
            'days_remaining': days_remaining,
            'days_overdue': -days_remaining if not is_timely else 0
        }
    
    @staticmethod
    def validate_notice_periods(effective_date: datetime, notice_days: int,
                                termination_date: Optional[datetime] = None) -> Dict:
        """Validate notice period compliance."""
        notice_deadline = effective_date + timedelta(days=notice_days)
        is_sufficient_notice = datetime.now() <= notice_deadline
        
        return {
            'notice_deadline': notice_deadline,
            'is_sufficient_notice': is_sufficient_notice,
            'days_remaining': (notice_deadline - datetime.now()).days,
            'termination_date': termination_date
        }
    
    @staticmethod
    def calculate_interest_accrual(principal: float, annual_rate: float, 
                                  start_date: datetime, end_date: datetime) -> float:
        """Calculate interest accrual based on date range."""
        days = (end_date - start_date).days
        daily_rate = annual_rate / 365
        interest = principal * daily_rate * days
        return round(interest, 2)
    
    @staticmethod
    def validate_lease_dates(start_date: datetime, end_date: datetime,
                            renewal_dates: list = None) -> Dict:
        """Validate lease-related dates."""
        duration = relativedelta(end_date, start_date)
        lease_length_years = duration.years + (duration.months / 12)
        
        result = {
            'start_date': start_date,
            'end_date': end_date,
            'duration_years': lease_length_years,
            'duration_months': duration.months,
            'is_valid': end_date > start_date
        }
        
        if renewal_dates:
            for renewal_date in renewal_dates:
                if renewal_date <= end_date:
                    result['warning'] = f"Renewal date {renewal_date} is before lease end date"
        
        return result
    
    @staticmethod
    def validate_contract_dates(execution_date: datetime, effective_date: datetime,
                               expiration_date: datetime) -> Dict:
        """Validate contract timeline."""
        errors = []
        
        if effective_date < execution_date:
            errors.append("Effective date cannot be before execution date")
        
        if expiration_date <= effective_date:
            errors.append("Expiration date must be after effective date")
        
        duration = relativedelta(expiration_date, effective_date)
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'execution_date': execution_date,
            'effective_date': effective_date,
            'expiration_date': expiration_date,
            'contract_duration_months': duration.months + (duration.years * 12)
        }
    
    @staticmethod
    def get_business_days(start_date: datetime, end_date: datetime) -> int:
        """Calculate number of business days between dates."""
        current = start_date
        business_days = 0
        
        while current <= end_date:
            if current.weekday() < 5:  # Monday-Friday
                business_days += 1
            current += timedelta(days=1)
        
        return business_days
    
    @staticmethod
    def validate_statute_of_repose(event_date: datetime, statute_years: int) -> bool:
        """Validate against statute of repose (absolute deadline regardless of discovery)."""
        repose_deadline = event_date + relativedelta(years=statute_years)
        return datetime.now() <= repose_deadline


# Example usage
if __name__ == '__main__':
    # Filing deadline validation
    original_event = datetime(2022, 1, 15)
    filing_date = datetime.now()
    statute_days = 365 * 2  # 2 years
    
    deadline_check = DateValidator.validate_filing_deadline(filing_date, statute_days, original_event)
    print("Filing Deadline Check:")
    print(f"  Timely: {deadline_check['is_timely']}")
    print(f"  Deadline: {deadline_check['deadline']}")
    print(f"  Days Remaining: {deadline_check['days_remaining']}")
    
    # Contract date validation
    exec_date = datetime(2024, 1, 1)
    eff_date = datetime(2024, 1, 1)
    exp_date = datetime(2027, 1, 1)
    
    contract_check = DateValidator.validate_contract_dates(exec_date, eff_date, exp_date)
    print("\nContract Date Validation:")
    print(f"  Valid: {contract_check['is_valid']}")
    print(f"  Duration (months): {contract_check['contract_duration_months']}")
    
    # Interest calculation
    interest = DateValidator.calculate_interest_accrual(
        principal=10000,
        annual_rate=0.06,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    print(f"\nInterest Accrual: ${interest}")

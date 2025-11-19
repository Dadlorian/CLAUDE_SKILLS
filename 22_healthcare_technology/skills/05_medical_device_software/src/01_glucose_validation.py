"""
Medical Device Software: Glucose Reading Validation
IEC 62304 Class B/C Software - Validated Algorithm

This module demonstrates validated glucose input/output handling
with comprehensive error checking and logging per FDA guidance.

Requirements Traced:
- REQ-GLU-001: Accept glucose readings 0-600 mg/dL
- REQ-GLU-002: Validate all inputs
- REQ-GLU-003: Log all measurements
- REQ-SAFE-001: Prevent buffer overflow
"""

import logging
from typing import Optional, Tuple
from enum import Enum

# Configure audit logging per 21 CFR Part 11
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('glucose_device_audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GlucoseReadingStatus(Enum):
    """Status codes for glucose readings per device specification"""
    VALID = 'VALID'
    OUT_OF_RANGE = 'OUT_OF_RANGE'
    SENSOR_ERROR = 'SENSOR_ERROR'
    NOT_READY = 'NOT_READY'


class GlucoseValidator:
    """
    Validates glucose readings per IEC 62304 requirements.
    
    Risk Controls Implemented:
    - RC-001: Input validation (prevents wrong readings)
    - RC-002: Range checking (prevents calculation errors)
    - RC-003: Audit logging (enables post-market traceability)
    """
    
    # Software Requirements Specification
    MIN_GLUCOSE_MG_DL = 0      # REQ-GLU-001
    MAX_GLUCOSE_MG_DL = 600    # REQ-GLU-001
    DECIMAL_PLACES = 1         # REQ-GLU-001
    
    def __init__(self):
        """Initialize validator with calibration data"""
        self.measurement_count = 0
        self.last_valid_reading = None
        logger.info("GlucoseValidator initialized")
    
    def validate_glucose_reading(
        self, 
        raw_value: Optional[float],
        sensor_id: str = "DEFAULT"
    ) -> Tuple[Optional[float], GlucoseReadingStatus]:
        """
        Validate glucose reading with comprehensive error checking.
        
        Design Specification:
        - Input validation check
        - Type verification
        - Range verification
        - Precision handling
        - Audit logging
        
        Args:
            raw_value: Raw glucose reading from sensor
            sensor_id: Identifier of sensor for traceability
            
        Returns:
            Tuple of (validated_value, status)
            
        Test Coverage:
            TC-001: Valid readings 0-600
            TC-002: Boundary values (0, 600)
            TC-003: Out of range values
            TC-004: Non-numeric inputs
            TC-005: Null/None inputs
        """
        
        # REQ-GLU-002: Validate all inputs
        try:
            # Type validation - prevent type confusion attacks
            if raw_value is None:
                logger.warning(f"Null glucose value from sensor {sensor_id}")
                return None, GlucoseReadingStatus.SENSOR_ERROR
            
            # Convert to float if necessary
            if isinstance(raw_value, str):
                # Security: Only allow numeric strings
                if not raw_value.replace('.', '', 1).replace('-', '', 1).isdigit():
                    logger.error(f"Invalid glucose format: {raw_value} from {sensor_id}")
                    return None, GlucoseReadingStatus.SENSOR_ERROR
                glucose_value = float(raw_value)
            else:
                glucose_value = float(raw_value)
            
            # Range validation - REQ-GLU-001
            if glucose_value < self.MIN_GLUCOSE_MG_DL:
                logger.warning(
                    f"Glucose below minimum: {glucose_value} from {sensor_id}"
                )
                return None, GlucoseReadingStatus.OUT_OF_RANGE
            
            if glucose_value > self.MAX_GLUCOSE_MG_DL:
                logger.warning(
                    f"Glucose above maximum: {glucose_value} from {sensor_id}"
                )
                return None, GlucoseReadingStatus.OUT_OF_RANGE
            
            # Round to specified precision per SDS
            validated_value = round(glucose_value, self.DECIMAL_PLACES)
            
            # Plausibility check - detect sensor errors
            if self.last_valid_reading is not None:
                delta = abs(validated_value - self.last_valid_reading)
                if delta > 100:  # >100 mg/dL change in one reading
                    logger.warning(
                        f"Implausible glucose change: {delta} from {sensor_id}"
                    )
                    # Don't reject, but log for clinician review
            
            # REQ-GLU-003: Log all measurements
            self.measurement_count += 1
            logger.info(
                f"Valid glucose reading: {validated_value} mg/dL "
                f"(count={self.measurement_count}, sensor={sensor_id})"
            )
            
            self.last_valid_reading = validated_value
            return validated_value, GlucoseReadingStatus.VALID
            
        except (ValueError, TypeError) as e:
            logger.error(f"Glucose validation exception: {str(e)} from {sensor_id}")
            return None, GlucoseReadingStatus.SENSOR_ERROR
    
    def check_consistency(self, reading1: float, reading2: float) -> bool:
        """
        Verify two readings are consistent (risk control for measurement integrity).
        
        Requirement: REQ-SAFE-002
        Test: TC-006, TC-007
        """
        if reading1 is None or reading2 is None:
            return False
        
        delta = abs(reading1 - reading2)
        is_consistent = delta <= 20  # Within 20 mg/dL is acceptable
        
        if not is_consistent:
            logger.warning(f"Inconsistent readings: {reading1} vs {reading2}")
        
        return is_consistent


# Unit Tests (IEC 62304 Verification)
def test_glucose_validation():
    """
    Test Procedure: TP-GLU-001
    Test all validation scenarios per risk assessment.
    """
    validator = GlucoseValidator()
    
    # TC-001: Valid readings
    assert validator.validate_glucose_reading(100)[1] == GlucoseReadingStatus.VALID
    assert validator.validate_glucose_reading(50)[1] == GlucoseReadingStatus.VALID
    assert validator.validate_glucose_reading(200.5)[1] == GlucoseReadingStatus.VALID
    
    # TC-002: Boundary values
    assert validator.validate_glucose_reading(0)[1] == GlucoseReadingStatus.VALID
    assert validator.validate_glucose_reading(600)[1] == GlucoseReadingStatus.VALID
    
    # TC-003: Out of range
    assert validator.validate_glucose_reading(-1)[1] == GlucoseReadingStatus.OUT_OF_RANGE
    assert validator.validate_glucose_reading(601)[1] == GlucoseReadingStatus.OUT_OF_RANGE
    
    # TC-004: Invalid types
    assert validator.validate_glucose_reading(None)[1] == GlucoseReadingStatus.SENSOR_ERROR
    assert validator.validate_glucose_reading("invalid")[1] == GlucoseReadingStatus.SENSOR_ERROR
    
    logger.info("All glucose validation tests PASSED")


if __name__ == "__main__":
    test_glucose_validation()
    print("Glucose validation module verification complete")

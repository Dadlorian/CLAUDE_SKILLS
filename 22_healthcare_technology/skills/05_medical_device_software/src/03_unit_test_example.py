"""IEC 62304 Unit Testing Example with pytest"""
import pytest
from glucose_validation import GlucoseValidator, GlucoseReadingStatus

class TestGlucoseValidator:
    """
    Test Suite for Glucose Validation Module
    
    Design Specification: SDS-GLU-001
    Requirements Verified: REQ-GLU-001, REQ-GLU-002, REQ-GLU-003
    Test Coverage Target: 95% (Class C software)
    """
    
    @pytest.fixture
    def validator(self):
        """Setup test fixture"""
        return GlucoseValidator()
    
    def test_valid_readings(self, validator):
        """TC-001: Verify acceptance of valid glucose values"""
        valid_values = [0, 50, 100, 200.5, 300, 600]
        
        for value in valid_values:
            result, status = validator.validate_glucose_reading(value)
            assert status == GlucoseReadingStatus.VALID
            assert result == pytest.approx(value, abs=1.0)
    
    def test_boundary_values(self, validator):
        """TC-002: Test at specification boundaries"""
        # Minimum boundary
        result, status = validator.validate_glucose_reading(0)
        assert status == GlucoseReadingStatus.VALID
        assert result == 0.0
        
        # Maximum boundary
        result, status = validator.validate_glucose_reading(600)
        assert status == GlucoseReadingStatus.VALID
        assert result == 600.0
    
    def test_out_of_range_low(self, validator):
        """TC-003: Reject values below minimum"""
        result, status = validator.validate_glucose_reading(-1)
        assert status == GlucoseReadingStatus.OUT_OF_RANGE
        assert result is None
    
    def test_out_of_range_high(self, validator):
        """TC-003: Reject values above maximum"""
        result, status = validator.validate_glucose_reading(601)
        assert status == GlucoseReadingStatus.OUT_OF_RANGE
        assert result is None
    
    def test_type_validation(self, validator):
        """TC-004: Reject invalid types"""
        invalid_inputs = [
            "invalid_string",
            "100mg/dL",
            [],
            {},
            {'glucose': 100}
        ]
        
        for invalid_input in invalid_inputs:
            result, status = validator.validate_glucose_reading(invalid_input)
            assert status == GlucoseReadingStatus.SENSOR_ERROR
            assert result is None
    
    def test_null_input(self, validator):
        """TC-005: Handle None input gracefully"""
        result, status = validator.validate_glucose_reading(None)
        assert status == GlucoseReadingStatus.SENSOR_ERROR
        assert result is None
    
    def test_precision_handling(self, validator):
        """TC-006: Verify rounding to specification"""
        # Input with extra decimal places
        result, status = validator.validate_glucose_reading(123.456)
        assert status == GlucoseReadingStatus.VALID
        assert result == 123.5  # Rounded to 1 decimal place
    
    def test_reading_consistency(self, validator):
        """TC-007: Verify measurement consistency check"""
        reading1 = 150
        reading2 = 160
        assert validator.check_consistency(reading1, reading2) == True
        
        reading3 = 150
        reading4 = 280  # >100 mg/dL difference
        # Should still return True but log warning
        assert validator.check_consistency(reading3, reading4) == False
    
    def test_measurement_count(self, validator):
        """TC-008: Verify measurement tracking"""
        initial_count = validator.measurement_count
        
        validator.validate_glucose_reading(100)
        assert validator.measurement_count == initial_count + 1
        
        validator.validate_glucose_reading(200)
        assert validator.measurement_count == initial_count + 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

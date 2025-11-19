#!/usr/bin/env python3
"""
Data Quality Validation Script
Runs Great Expectations validations and reports results
"""

import great_expectations as gx
from datetime import datetime
import json

def run_data_quality_checks():
    """Execute data quality validations"""

    # Initialize GE context
    context = gx.get_context()

    # Run checkpoint
    result = context.run_checkpoint(
        checkpoint_name="daily_data_quality_check",
        run_name=f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    # Parse results
    success = result["success"]
    validation_results = result["run_results"]

    print(f"Validation Status: {'PASSED' if success else 'FAILED'}")

    # Report failures
    if not success:
        for run_id, run_result in validation_results.items():
            for validation in run_result["validation_result"]["results"]:
                if not validation["success"]:
                    expectation = validation["expectation_config"]["expectation_type"]
                    print(f"❌ Failed: {expectation}")

    return 0 if success else 1

if __name__ == "__main__":
    exit(run_data_quality_checks())

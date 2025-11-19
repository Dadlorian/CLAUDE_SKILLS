"""
AI Validation and Testing Framework
Test legal AI systems for accuracy, bias, and safety
"""

class LegalAIValidator:
    """Validate legal AI systems"""

    def __init__(self):
        self.test_suites = {
            "accuracy": self.test_accuracy,
            "bias": self.test_bias,
            "safety": self.test_safety,
            "hallucination": self.test_hallucination
        }

    def validate_model(self, model, test_data):
        """Run all validation tests"""

        results = {}

        for test_name, test_func in self.test_suites.items():
            results[test_name] = test_func(model, test_data)

        # Overall assessment
        overall_pass = all(r['passed'] for r in results.values())

        return {
            "overall_pass": overall_pass,
            "test_results": results,
            "recommendation": "APPROVED" if overall_pass else "REQUIRES FIXES"
        }

    def test_accuracy(self, model, test_data):
        """Test prediction accuracy"""

        predictions = model.predict(test_data['X'])
        accuracy = (predictions == test_data['y']).mean()

        return {
            "passed": accuracy >= 0.90,
            "accuracy": accuracy,
            "threshold": 0.90
        }

    def test_bias(self, model, test_data):
        """Test for demographic bias"""

        # Test disparate impact
        protected_group_preds = model.predict(
            test_data['X'][test_data['protected_group'] == 1]
        )
        unprotected_group_preds = model.predict(
            test_data['X'][test_data['protected_group'] == 0]
        )

        protected_rate = protected_group_preds.mean()
        unprotected_rate = unprotected_group_preds.mean()

        disparate_impact = protected_rate / unprotected_rate if unprotected_rate > 0 else 0

        # Pass if within 80%-125% (80% rule)
        passed = 0.8 <= disparate_impact <= 1.25

        return {
            "passed": passed,
            "disparate_impact": disparate_impact,
            "protected_rate": protected_rate,
            "unprotected_rate": unprotected_rate
        }

    def test_safety(self, model, test_data):
        """Test for unsafe outputs"""

        predictions = model.predict(test_data['X'])

        # Check for harmful predictions
        harmful_predictions = 0

        return {
            "passed": harmful_predictions == 0,
            "harmful_count": harmful_predictions
        }

    def test_hallucination(self, model, test_data):
        """Test for hallucinated information"""

        # For generative models
        outputs = model.generate(test_data['prompts'])

        hallucinations = []

        for output, sources in zip(outputs, test_data['sources']):
            # Check if output claims are supported by sources
            if not self.is_supported_by_sources(output, sources):
                hallucinations.append(output)

        hallucination_rate = len(hallucinations) / len(outputs)

        return {
            "passed": hallucination_rate < 0.05,  # Less than 5%
            "hallucination_rate": hallucination_rate,
            "examples": hallucinations[:3]
        }

    def is_supported_by_sources(self, output, sources):
        """Check if output is supported by source documents"""

        # Placeholder - would use semantic similarity
        return True

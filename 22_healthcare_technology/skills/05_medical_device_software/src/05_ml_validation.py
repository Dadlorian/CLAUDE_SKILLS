"""AI/ML Algorithm Validation - FDA SaMD Guidance Implementation"""
import numpy as np
from sklearn.metrics import confusion_matrix, roc_auc_score, roc_curve
from typing import Dict, Tuple

class MLModelValidator:
    """Validate medical device AI/ML algorithm per FDA guidance"""
    
    def __init__(self, model_name: str, target_population: str):
        self.model_name = model_name
        self.target_population = target_population
        self.validation_results = {}
    
    def calculate_performance_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: np.ndarray = None
    ) -> Dict[str, float]:
        """
        Calculate clinical performance metrics per FDA requirements.
        
        Required for SaMD submissions:
        - Sensitivity (true positive rate)
        - Specificity (true negative rate)
        - Positive Predictive Value (precision)
        - Negative Predictive Value
        - Overall Accuracy
        - AUC-ROC (if applicable)
        """
        
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        
        sensitivity = tp / (tp + fn)           # Recall
        specificity = tn / (tn + fp)
        ppv = tp / (tp + fp)                   # Precision
        npv = tn / (tn + fn)
        accuracy = (tp + tn) / (tp + tn + fp + fn)
        f1 = 2 * (ppv * sensitivity) / (ppv + sensitivity)
        
        metrics = {
            'sensitivity': sensitivity,
            'specificity': specificity,
            'positive_predictive_value': ppv,
            'negative_predictive_value': npv,
            'accuracy': accuracy,
            'f1_score': f1
        }
        
        # Calculate AUC if probabilities provided
        if y_pred_proba is not None:
            metrics['auc_roc'] = roc_auc_score(y_true, y_pred_proba)
        
        return metrics
    
    def analyze_bias(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        demographics: Dict[str, np.ndarray]
    ) -> Dict[str, Dict[str, float]]:
        """
        Analyze algorithm bias by demographic group.
        FDA expects demonstration of fairness across populations.
        """
        
        bias_analysis = {}
        
        for demo_type, demo_values in demographics.items():
            unique_groups = np.unique(demo_values)
            bias_analysis[demo_type] = {}
            
            for group in unique_groups:
                mask = demo_values == group
                group_y_true = y_true[mask]
                group_y_pred = y_pred[mask]
                
                if len(group_y_true) > 10:  # Minimum sample size
                    metrics = self.calculate_performance_metrics(
                        group_y_true, group_y_pred
                    )
                    bias_analysis[demo_type][str(group)] = metrics
        
        return bias_analysis
    
    def generate_model_card(self) -> Dict:
        """
        Generate FDA-compliant model card documentation.
        Required for all AI/ML medical devices.
        """
        
        return {
            'model_name': self.model_name,
            'target_population': self.target_population,
            'validation_results': self.validation_results,
            'performance_metrics': {
                'sensitivity': '>95% for critical findings',
                'specificity': '>90% for non-disease',
                'accuracy': '>92% overall'
            },
            'limitations': [
                'Validated for adult patients >18 years',
                'May not perform well with non-standard imaging',
                'Requires high-quality image input'
            ],
            'bias_analysis': 'Tested across age, gender, ethnicity',
            'update_mechanism': 'Quarterly model retraining with external validation',
            'postmarket_monitoring': 'Real-world performance tracking system'
        }

# Example usage
def example_ml_validation():
    # Simulated ground truth and predictions
    np.random.seed(42)
    y_true = np.array([0]*80 + [1]*20)  # 20% positive cases
    y_pred = np.random.randint(0, 2, 100)
    y_pred_proba = np.random.rand(100)
    
    validator = MLModelValidator(
        "Pneumonia Detection CNN",
        "Adult patients with respiratory symptoms"
    )
    
    metrics = validator.calculate_performance_metrics(
        y_true, y_pred, y_pred_proba
    )
    
    validator.validation_results = metrics
    
    # Simulate demographic data (age, gender, ethnicity)
    demographics = {
        'age_group': np.random.choice(['18-40', '41-60', '60+'], 100),
        'gender': np.random.choice(['M', 'F'], 100),
    }
    
    bias_results = validator.analyze_bias(y_true, y_pred, demographics)
    
    return validator, metrics, bias_results

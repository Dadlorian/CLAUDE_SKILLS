"""
Backtesting Framework

Comprehensive backtesting of risk models.
"""

import pandas as pd
import numpy as np


class Backtester:
    """Backtest risk predictions against actuals."""

    @staticmethod
    def backtest_pd_model(predicted_pd, actual_defaults):
        """
        Backtest probability of default model.

        Args:
            predicted_pd: Array of predicted PDs
            actual_defaults: Binary array (0=no default, 1=default)

        Returns:
            Backtesting metrics
        """
        n_samples = len(predicted_pd)
        n_defaults = actual_defaults.sum()

        # Prediction statistics
        predicted_defaults = (predicted_pd >= 0.5).astype(int)
        correct = (predicted_defaults == actual_defaults).sum()
        accuracy = correct / n_samples

        # Sensitivity and Specificity
        tp = ((predicted_defaults == 1) & (actual_defaults == 1)).sum()
        fn = ((predicted_defaults == 0) & (actual_defaults == 1)).sum()
        tn = ((predicted_defaults == 0) & (actual_defaults == 0)).sum()
        fp = ((predicted_defaults == 1) & (actual_defaults == 0)).sum()

        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

        return {
            'Accuracy': accuracy,
            'Sensitivity': sensitivity,
            'Specificity': specificity,
            'N_Defaults': n_defaults,
            'Total_Samples': n_samples,
        }

    @staticmethod
    def backtest_by_bucket(predicted_values, actual_values, n_buckets=10):
        """
        Backtest by buckets/deciles.

        Args:
            predicted_values: Predicted risk/return
            actual_values: Actual risk/return
            n_buckets: Number of buckets to test

        Returns:
            DataFrame with bucket analysis
        """
        df = pd.DataFrame({
            'Predicted': predicted_values,
            'Actual': actual_values
        })

        # Create buckets
        df['Bucket'] = pd.qcut(df['Predicted'], n_buckets, labels=False)

        # Calculate statistics by bucket
        bucket_stats = df.groupby('Bucket').agg({
            'Predicted': ['mean', 'count'],
            'Actual': 'mean'
        }).reset_index()

        return bucket_stats

    @staticmethod
    def calibration_error(predicted, actual):
        """
        Calculate calibration error.

        Args:
            predicted: Predicted values
            actual: Actual values

        Returns:
            Mean absolute error
        """
        mae = np.mean(np.abs(predicted - actual))
        return mae


# Example usage
if __name__ == "__main__":
    # Generate sample predictions and actuals
    np.random.seed(42)
    predicted_pd = np.random.uniform(0, 1, 1000)
    actual_defaults = (predicted_pd > 0.7).astype(int)
    actual_defaults[np.random.choice(1000, 50, replace=False)] = 1  # Add some noise

    # Backtest
    metrics = Backtester.backtest_pd_model(predicted_pd, actual_defaults)
    print("PD Model Backtest:")
    print(f"  Accuracy: {metrics['Accuracy']:.2%}")
    print(f"  Sensitivity: {metrics['Sensitivity']:.2%}")
    print(f"  Specificity: {metrics['Specificity']:.2%}")

    # Bucket analysis
    bucket_analysis = Backtester.backtest_by_bucket(predicted_pd, actual_defaults, 5)
    print("\nBucket Analysis:")
    print(bucket_analysis)

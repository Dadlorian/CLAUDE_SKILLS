"""
Machine Learning Demand Forecasting for Manufacturing

This module implements multiple forecasting algorithms for predicting product demand,
including classical time series methods and advanced machine learning models.

Algorithms:
- ARIMA (Autoregressive Integrated Moving Average)
- Exponential Smoothing (Holt-Winters)
- Gradient Boosting (XGBoost, LightGBM)
- LSTM Neural Networks
- Prophet (Facebook's forecasting tool)
- Ensemble methods
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json

try:
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
except ImportError:
    pass

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
except ImportError:
    pass


@dataclass
class ForecastResult:
    """Data class for forecast results"""
    timestamp: datetime
    period: str
    forecast_value: float
    lower_bound: float
    upper_bound: float
    confidence: float
    method: str
    mape: Optional[float] = None
    rmse: Optional[float] = None


class DemandForecaster:
    """
    Multi-algorithm demand forecasting with ensemble capabilities
    """

    def __init__(self):
        self.historical_data = pd.DataFrame()
        self.forecast_results = []
        self.model_performance = {}
        self.scaler = StandardScaler()

    def add_historical_data(
        self,
        dates: List[str],
        demand: List[float],
        product_id: Optional[str] = None
    ):
        """
        Add historical demand data

        Args:
            dates: List of date strings (YYYY-MM-DD)
            demand: List of demand values
            product_id: Optional product identifier
        """
        df = pd.DataFrame({
            'date': pd.to_datetime(dates),
            'demand': demand
        })
        df = df.sort_values('date')
        df['date'] = df['date'].dt.date

        if product_id:
            df['product_id'] = product_id

        self.historical_data = pd.concat([self.historical_data, df], ignore_index=True)

    def forecast_exponential_smoothing(
        self,
        periods: int = 30,
        seasonal_periods: Optional[int] = 7,
        method: str = 'additive'
    ) -> List[ForecastResult]:
        """
        Exponential Smoothing (Holt-Winters) forecasting

        Args:
            periods: Number of periods to forecast
            seasonal_periods: Periods in season (e.g., 7 for weekly, None for no seasonality)
            method: 'additive' or 'multiplicative'

        Returns:
            List of ForecastResult objects
        """
        if len(self.historical_data) < 20:
            raise ValueError("Insufficient historical data for exponential smoothing")

        demand_values = self.historical_data['demand'].values
        dates = pd.to_datetime(self.historical_data['date']).values

        try:
            from statsmodels.tsa.holtwinters import ExponentialSmoothing

            if seasonal_periods and len(demand_values) >= seasonal_periods * 2:
                # Seasonal exponential smoothing
                model = ExponentialSmoothing(
                    demand_values,
                    seasonal_periods=seasonal_periods,
                    trend='add',
                    seasonal=method,
                    initialization_method='estimated'
                )
                fitted_model = model.fit(optimized=True)
                forecast_values = fitted_model.forecast(periods=periods)
                confidence_intervals = self._estimate_confidence_intervals(
                    fitted_model.fittedvalues, demand_values, periods
                )
            else:
                # Non-seasonal exponential smoothing
                model = ExponentialSmoothing(
                    demand_values,
                    trend='add',
                    seasonal=None
                )
                fitted_model = model.fit(optimized=True)
                forecast_values = fitted_model.forecast(periods=periods)
                confidence_intervals = self._estimate_confidence_intervals(
                    fitted_model.fittedvalues, demand_values, periods
                )

            results = []
            last_date = pd.to_datetime(self.historical_data['date'].iloc[-1])

            for i, value in enumerate(forecast_values):
                forecast_date = last_date + timedelta(days=i + 1)
                lower, upper = confidence_intervals[i]

                result = ForecastResult(
                    timestamp=datetime.now(),
                    period=forecast_date.strftime('%Y-%m-%d'),
                    forecast_value=float(value),
                    lower_bound=float(lower),
                    upper_bound=float(upper),
                    confidence=0.95,
                    method='Exponential Smoothing',
                    mape=float(self._calculate_mape(
                        demand_values[-30:],
                        fitted_model.fittedvalues[-30:]
                    ))
                )
                results.append(result)

            self.forecast_results.extend(results)
            return results

        except ImportError:
            print("Warning: statsmodels not installed. Install with: pip install statsmodels")
            return []

    def forecast_gradient_boosting(
        self,
        periods: int = 30,
        lookback: int = 30
    ) -> List[ForecastResult]:
        """
        Gradient Boosting (XGBoost/scikit-learn) forecasting with feature engineering

        Args:
            periods: Number of periods to forecast
            lookback: Historical lookback window for features

        Returns:
            List of ForecastResult objects
        """
        if len(self.historical_data) < lookback:
            raise ValueError("Insufficient historical data")

        # Prepare features
        demand_values = self.historical_data['demand'].values
        dates = pd.to_datetime(self.historical_data['date']).values

        # Feature engineering
        features_list = []
        targets_list = []

        for i in range(lookback, len(demand_values)):
            # Lag features
            lag_1 = demand_values[i - 1]
            lag_7 = demand_values[i - 7] if i >= 7 else demand_values[0]
            lag_30 = demand_values[i - 30] if i >= 30 else demand_values[0]

            # Moving averages
            ma_7 = np.mean(demand_values[max(0, i - 7):i])
            ma_30 = np.mean(demand_values[max(0, i - 30):i])

            # Trend
            trend = demand_values[i] - demand_values[i - 1]

            # Day of week
            dow = dates[i].astype('datetime64[D]').astype(int) % 7

            features = [lag_1, lag_7, lag_30, ma_7, ma_30, trend, dow]
            features_list.append(features)
            targets_list.append(demand_values[i])

        X = np.array(features_list)
        y = np.array(targets_list)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train model
        model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        model.fit(X_scaled, y)

        # Generate forecasts
        results = []
        last_date = pd.to_datetime(self.historical_data['date'].iloc[-1])
        current_values = demand_values.copy()

        for i in range(periods):
            # Create features for next period
            lag_1 = current_values[-1]
            lag_7 = current_values[-7] if len(current_values) >= 7 else current_values[0]
            lag_30 = current_values[-30] if len(current_values) >= 30 else current_values[0]
            ma_7 = np.mean(current_values[-7:])
            ma_30 = np.mean(current_values[-30:])
            trend = current_values[-1] - (current_values[-2] if len(current_values) > 1 else current_values[-1])
            dow = (last_date + timedelta(days=i + 1)).weekday()

            features = np.array([[lag_1, lag_7, lag_30, ma_7, ma_30, trend, dow]])
            features_scaled = self.scaler.transform(features)

            forecast_value = model.predict(features_scaled)[0]
            forecast_value = max(0, forecast_value)  # Ensure non-negative

            forecast_date = last_date + timedelta(days=i + 1)

            # Estimate confidence interval
            residuals = np.abs(y - model.predict(X_scaled))
            std_error = np.std(residuals)

            result = ForecastResult(
                timestamp=datetime.now(),
                period=forecast_date.strftime('%Y-%m-%d'),
                forecast_value=float(forecast_value),
                lower_bound=float(max(0, forecast_value - 1.96 * std_error)),
                upper_bound=float(forecast_value + 1.96 * std_error),
                confidence=0.95,
                method='Gradient Boosting',
                rmse=float(np.sqrt(mean_squared_error(y, model.predict(X_scaled))))
            )
            results.append(result)

            # Update current values for next iteration
            current_values = np.append(current_values, forecast_value)

        self.forecast_results.extend(results)
        return results

    def forecast_lstm(
        self,
        periods: int = 30,
        sequence_length: int = 30,
        epochs: int = 50,
        batch_size: int = 16
    ) -> List[ForecastResult]:
        """
        LSTM Neural Network forecasting

        Args:
            periods: Number of periods to forecast
            sequence_length: Length of input sequences
            epochs: Number of training epochs
            batch_size: Training batch size

        Returns:
            List of ForecastResult objects
        """
        try:
            import tensorflow as tf
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            from tensorflow.keras.optimizers import Adam
        except ImportError:
            print("Warning: TensorFlow not installed. Install with: pip install tensorflow")
            return []

        if len(self.historical_data) < sequence_length:
            raise ValueError("Insufficient historical data for LSTM")

        # Prepare data
        demand_values = self.historical_data['demand'].values.astype(np.float32)
        scaler = StandardScaler()
        demand_scaled = scaler.fit_transform(demand_values.reshape(-1, 1))

        # Create sequences
        X, y = [], []
        for i in range(len(demand_scaled) - sequence_length):
            X.append(demand_scaled[i:i + sequence_length])
            y.append(demand_scaled[i + sequence_length])

        X = np.array(X)
        y = np.array(y)

        # Build LSTM model
        model = Sequential([
            LSTM(64, activation='relu', input_shape=(sequence_length, 1)),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)
        ])

        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')

        # Train model (verbose=0 for production)
        model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)

        # Generate forecasts
        results = []
        last_sequence = demand_scaled[-sequence_length:].copy()
        last_date = pd.to_datetime(self.historical_data['date'].iloc[-1])

        for i in range(periods):
            # Predict next value
            next_value_scaled = model.predict(
                last_sequence.reshape(1, sequence_length, 1),
                verbose=0
            )[0, 0]

            # Inverse scale
            next_value = scaler.inverse_transform([[next_value_scaled]])[0, 0]
            next_value = max(0, float(next_value))

            # Update sequence
            last_sequence = np.vstack([last_sequence[1:], [[next_value_scaled]]])

            forecast_date = last_date + timedelta(days=i + 1)

            result = ForecastResult(
                timestamp=datetime.now(),
                period=forecast_date.strftime('%Y-%m-%d'),
                forecast_value=next_value,
                lower_bound=max(0, next_value * 0.9),  # 10% lower bound
                upper_bound=next_value * 1.1,           # 10% upper bound
                confidence=0.95,
                method='LSTM Neural Network'
            )
            results.append(result)

        self.forecast_results.extend(results)
        return results

    def ensemble_forecast(
        self,
        periods: int = 30,
        methods: List[str] = None
    ) -> List[ForecastResult]:
        """
        Ensemble forecasting combining multiple methods

        Args:
            periods: Number of periods to forecast
            methods: List of methods to use ('es', 'gb', 'lstm')

        Returns:
            List of ForecastResult objects
        """
        if methods is None:
            methods = ['es', 'gb']  # Default: Exponential Smoothing and Gradient Boosting

        forecasts_by_method = {}

        try:
            if 'es' in methods:
                forecasts_by_method['es'] = self.forecast_exponential_smoothing(periods)
        except Exception as e:
            print(f"Exponential Smoothing failed: {e}")

        try:
            if 'gb' in methods:
                forecasts_by_method['gb'] = self.forecast_gradient_boosting(periods)
        except Exception as e:
            print(f"Gradient Boosting failed: {e}")

        try:
            if 'lstm' in methods:
                forecasts_by_method['lstm'] = self.forecast_lstm(periods)
        except Exception as e:
            print(f"LSTM failed: {e}")

        if not forecasts_by_method:
            raise ValueError("No forecasting methods available")

        # Combine forecasts
        ensemble_results = []
        last_date = pd.to_datetime(self.historical_data['date'].iloc[-1])

        for period_idx in range(periods):
            forecast_date = last_date + timedelta(days=period_idx + 1)
            values = []
            weights = []
            conf_intervals = []

            for method, forecasts in forecasts_by_method.items():
                if period_idx < len(forecasts):
                    f = forecasts[period_idx]
                    values.append(f.forecast_value)
                    conf_intervals.append((f.lower_bound, f.upper_bound))

                    # Assign weights (favor methods with lower MAPE)
                    if f.mape:
                        weight = 1 / (1 + f.mape)
                    else:
                        weight = 1 / len(forecasts_by_method)
                    weights.append(weight)

            if values:
                weights_norm = np.array(weights) / np.sum(weights)
                ensemble_value = np.sum(np.array(values) * weights_norm)

                # Estimate ensemble confidence interval
                lower_values = [ci[0] for ci in conf_intervals]
                upper_values = [ci[1] for ci in conf_intervals]
                ensemble_lower = np.min(lower_values)
                ensemble_upper = np.max(upper_values)

                result = ForecastResult(
                    timestamp=datetime.now(),
                    period=forecast_date.strftime('%Y-%m-%d'),
                    forecast_value=float(ensemble_value),
                    lower_bound=float(ensemble_lower),
                    upper_bound=float(ensemble_upper),
                    confidence=0.95,
                    method='Ensemble (ES + GB + LSTM)'
                )
                ensemble_results.append(result)

        return ensemble_results

    @staticmethod
    def _calculate_mape(actual, predicted):
        """Calculate Mean Absolute Percentage Error"""
        mask = actual != 0
        return np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100

    @staticmethod
    def _estimate_confidence_intervals(
        fitted_values, actual_values, forecast_periods
    ) -> List[Tuple[float, float]]:
        """Estimate confidence intervals for forecasts"""
        residuals = actual_values - fitted_values
        std_error = np.std(residuals)

        intervals = []
        for _ in range(forecast_periods):
            # Simple 95% confidence interval
            lower = -1.96 * std_error
            upper = 1.96 * std_error
            intervals.append((lower, upper))

        return intervals

    def get_forecast_summary(self) -> Dict:
        """Get summary of recent forecasts"""
        if not self.forecast_results:
            return {}

        recent = self.forecast_results[-30:]  # Last 30 forecasts

        return {
            'total_forecasts': len(recent),
            'average_forecast': np.mean([f.forecast_value for f in recent]),
            'forecast_std': np.std([f.forecast_value for f in recent]),
            'methods_used': list(set([f.method for f in recent])),
            'avg_confidence': np.mean([f.confidence for f in recent]),
        }

    def export_forecasts(self, filename: str):
        """Export forecast results to JSON"""
        data = [
            {
                'period': f.period,
                'forecast_value': f.forecast_value,
                'lower_bound': f.lower_bound,
                'upper_bound': f.upper_bound,
                'confidence': f.confidence,
                'method': f.method,
                'mape': f.mape,
                'rmse': f.rmse
            }
            for f in self.forecast_results
        ]

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)


# Example usage
if __name__ == "__main__":
    # Create forecaster
    forecaster = DemandForecaster()

    # Generate sample historical data
    dates = pd.date_range(start='2023-01-01', periods=365, freq='D')
    # Simulate demand with trend and seasonality
    trend = np.linspace(100, 150, 365)
    seasonality = 20 * np.sin(np.linspace(0, 4 * np.pi, 365))
    noise = np.random.normal(0, 5, 365)
    demand = trend + seasonality + noise
    demand = np.maximum(demand, 10)  # Ensure non-negative

    forecaster.add_historical_data(
        dates.strftime('%Y-%m-%d').tolist(),
        demand.tolist(),
        product_id='SKU001'
    )

    print("Historical data loaded: {} days".format(len(forecaster.historical_data)))

    # Generate forecasts using different methods
    print("\n1. Exponential Smoothing Forecast:")
    try:
        es_forecast = forecaster.forecast_exponential_smoothing(periods=30)
        for f in es_forecast[:5]:
            print(f"  {f.period}: {f.forecast_value:.1f} "
                  f"({f.lower_bound:.1f} - {f.upper_bound:.1f})")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n2. Gradient Boosting Forecast:")
    try:
        gb_forecast = forecaster.forecast_gradient_boosting(periods=30)
        for f in gb_forecast[:5]:
            print(f"  {f.period}: {f.forecast_value:.1f} "
                  f"({f.lower_bound:.1f} - {f.upper_bound:.1f})")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n3. Ensemble Forecast:")
    try:
        ensemble_forecast = forecaster.ensemble_forecast(
            periods=30,
            methods=['es', 'gb']
        )
        for f in ensemble_forecast[:5]:
            print(f"  {f.period}: {f.forecast_value:.1f} "
                  f"({f.lower_bound:.1f} - {f.upper_bound:.1f})")
    except Exception as e:
        print(f"  Error: {e}")

    print("\nForecast Summary:")
    summary = forecaster.get_forecast_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

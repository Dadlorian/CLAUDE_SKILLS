# Predictive Analytics Reference

Comprehensive guide to building and deploying predictive models for business analytics.

## What is Predictive Analytics?

**Definition**: Using historical data, statistical algorithms, and machine learning techniques to predict future outcomes.

**Common Use Cases**:
- Customer churn prediction
- Customer lifetime value forecasting
- Demand forecasting
- Lead scoring
- Price optimization
- Fraud detection
- Inventory optimization

## Predictive Modeling Process

### 1. Define the Problem

```python
PREDICTIVE_PROBLEM_TYPES = {
    'Classification': {
        'description': 'Predicting categories (Yes/No, High/Medium/Low)',
        'examples': ['Will customer churn?', 'Is this transaction fraud?', 'Which segment?'],
        'metrics': ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC-ROC']
    },

    'Regression': {
        'description': 'Predicting continuous values',
        'examples': ['Customer lifetime value', 'Sales forecast', 'Product demand'],
        'metrics': ['RMSE', 'MAE', 'R-squared', 'MAPE']
    },

    'Time Series': {
        'description': 'Predicting future values based on temporal patterns',
        'examples': ['Revenue forecast', 'Traffic prediction', 'Seasonal demand'],
        'metrics': ['RMSE', 'MAE', 'MAPE', 'Forecast bias']
    },

    'Clustering': {
        'description': 'Finding natural groupings in data',
        'examples': ['Customer segmentation', 'Product clustering', 'Anomaly detection'],
        'metrics': ['Silhouette score', 'Davies-Bouldin index', 'Inertia']
    }
}
```

### 2. Data Preparation

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

class DataPreparation:
    """Prepare data for predictive modeling"""

    def __init__(self, df):
        self.df = df.copy()
        self.scaler = StandardScaler()
        self.label_encoders = {}

    def handle_missing_values(self, strategy='median'):
        """
        Handle missing values

        Args:
            strategy: 'drop', 'median', 'mean', 'mode', 'forward_fill'
        """
        if strategy == 'drop':
            self.df = self.df.dropna()
        elif strategy == 'median':
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].median())
        elif strategy == 'mean':
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].mean())
        elif strategy == 'mode':
            for col in self.df.columns:
                self.df[col] = self.df[col].fillna(self.df[col].mode()[0])
        elif strategy == 'forward_fill':
            self.df = self.df.fillna(method='ffill')

        return self

    def encode_categorical(self, columns):
        """Label encode categorical variables"""
        for col in columns:
            le = LabelEncoder()
            self.df[col] = le.fit_transform(self.df[col].astype(str))
            self.label_encoders[col] = le

        return self

    def create_features(self, date_col=None):
        """Create additional features"""
        if date_col:
            self.df[date_col] = pd.to_datetime(self.df[date_col])
            self.df[f'{date_col}_year'] = self.df[date_col].dt.year
            self.df[f'{date_col}_month'] = self.df[date_col].dt.month
            self.df[f'{date_col}_day'] = self.df[date_col].dt.day
            self.df[f'{date_col}_dayofweek'] = self.df[date_col].dt.dayofweek
            self.df[f'{date_col}_quarter'] = self.df[date_col].dt.quarter

        return self

    def scale_features(self, columns):
        """Standardize numeric features"""
        self.df[columns] = self.scaler.fit_transform(self.df[columns])
        return self

    def split_data(self, target_col, test_size=0.2, random_state=42):
        """Split into train and test sets"""
        X = self.df.drop(columns=[target_col])
        y = self.df[target_col]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=y if y.dtype == 'object' or y.nunique() < 20 else None
        )

        return X_train, X_test, y_train, y_test
```

## Churn Prediction

### Feature Engineering for Churn

```python
def create_churn_features(customer_data):
    """
    Create features for churn prediction

    Args:
        customer_data: DataFrame with customer transaction history

    Returns:
        DataFrame with churn prediction features
    """
    import pandas as pd
    import numpy as np

    features = pd.DataFrame()
    features['customer_id'] = customer_data['customer_id'].unique()

    for customer_id in features['customer_id']:
        customer_orders = customer_data[customer_data['customer_id'] == customer_id]

        # Recency features
        features.loc[features['customer_id'] == customer_id, 'days_since_last_order'] = (
            (pd.Timestamp.now() - customer_orders['order_date'].max()).days
        )

        # Frequency features
        features.loc[features['customer_id'] == customer_id, 'total_orders'] = len(customer_orders)
        features.loc[features['customer_id'] == customer_id, 'avg_days_between_orders'] = (
            (customer_orders['order_date'].max() - customer_orders['order_date'].min()).days /
            max(len(customer_orders) - 1, 1)
        )

        # Monetary features
        features.loc[features['customer_id'] == customer_id, 'total_revenue'] = customer_orders['revenue'].sum()
        features.loc[features['customer_id'] == customer_id, 'avg_order_value'] = customer_orders['revenue'].mean()

        # Trend features
        recent_orders = customer_orders[customer_orders['order_date'] >= pd.Timestamp.now() - pd.Timedelta(days=90)]
        old_orders = customer_orders[
            (customer_orders['order_date'] < pd.Timestamp.now() - pd.Timedelta(days=90)) &
            (customer_orders['order_date'] >= pd.Timestamp.now() - pd.Timedelta(days=180))
        ]

        features.loc[features['customer_id'] == customer_id, 'orders_last_90d'] = len(recent_orders)
        features.loc[features['customer_id'] == customer_id, 'orders_90_180d'] = len(old_orders)
        features.loc[features['customer_id'] == customer_id, 'order_trend'] = (
            len(recent_orders) - len(old_orders)
        )

        # Product diversity
        features.loc[features['customer_id'] == customer_id, 'product_categories'] = (
            customer_orders['product_category'].nunique()
        )

    return features
```

### Churn Prediction Model

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

class ChurnPredictor:
    """Predict customer churn"""

    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'  # Handle imbalanced classes
        )
        self.feature_importance = None

    def train(self, X_train, y_train):
        """Train churn prediction model"""
        self.model.fit(X_train, y_train)

        # Feature importance
        self.feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        print("Top 10 Important Features:")
        print(self.feature_importance.head(10))

    def evaluate(self, X_test, y_test):
        """Evaluate model performance"""
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]

        print("Classification Report:")
        print(classification_report(y_test, y_pred))

        print(f"\nROC AUC Score: {roc_auc_score(y_test, y_prob):.3f}")

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title('Confusion Matrix')
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.show()

        return {
            'auc_roc': roc_auc_score(y_test, y_prob),
            'predictions': y_pred,
            'probabilities': y_prob
        }

    def predict_churn_probability(self, X):
        """Predict churn probability for new customers"""
        probabilities = self.model.predict_proba(X)[:, 1]

        results = pd.DataFrame({
            'churn_probability': probabilities,
            'risk_category': pd.cut(
                probabilities,
                bins=[0, 0.3, 0.6, 1.0],
                labels=['Low Risk', 'Medium Risk', 'High Risk']
            )
        })

        return results
```

## Customer Lifetime Value Prediction

### LTV Prediction Model

```python
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

class LTVPredictor:
    """Predict customer lifetime value"""

    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )

    def create_ltv_features(self, customer_data):
        """
        Create features for LTV prediction

        Features based on early customer behavior (first 30-90 days)
        """
        features = pd.DataFrame()

        # Early behavior features
        features['first_purchase_amount'] = customer_data.groupby('customer_id')['revenue'].first()
        features['purchases_first_30d'] = customer_data[
            customer_data['days_since_signup'] <= 30
        ].groupby('customer_id').size()
        features['revenue_first_30d'] = customer_data[
            customer_data['days_since_signup'] <= 30
        ].groupby('customer_id')['revenue'].sum()
        features['avg_order_value_first_30d'] = (
            features['revenue_first_30d'] / features['purchases_first_30d']
        )

        # Product engagement
        features['categories_tried'] = customer_data.groupby('customer_id')['product_category'].nunique()
        features['avg_days_between_orders'] = customer_data.groupby('customer_id').apply(
            lambda x: (x['order_date'].max() - x['order_date'].min()).days / max(len(x) - 1, 1)
        )

        # Demographic features (if available)
        features['age'] = customer_data.groupby('customer_id')['age'].first()
        features['acquisition_channel'] = customer_data.groupby('customer_id')['channel'].first()

        return features

    def train(self, X_train, y_train):
        """Train LTV prediction model"""
        self.model.fit(X_train, y_train)

        print("Model trained successfully")
        print(f"Training R² score: {self.model.score(X_train, y_train):.3f}")

    def evaluate(self, X_test, y_test):
        """Evaluate LTV prediction model"""
        y_pred = self.model.predict(X_test)

        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

        print(f"RMSE: ${rmse:.2f}")
        print(f"MAE: ${mae:.2f}")
        print(f"R² Score: {r2:.3f}")
        print(f"MAPE: {mape:.2f}%")

        # Actual vs Predicted plot
        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, y_pred, alpha=0.5)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        plt.xlabel('Actual LTV')
        plt.ylabel('Predicted LTV')
        plt.title('LTV Prediction: Actual vs Predicted')
        plt.grid(True, alpha=0.3)
        plt.show()

        return {'rmse': rmse, 'mae': mae, 'r2': r2, 'mape': mape}

    def predict_ltv(self, X):
        """Predict LTV for new customers"""
        predictions = self.model.predict(X)
        return predictions
```

## Demand Forecasting

### Time Series Forecasting

```python
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt

class DemandForecaster:
    """Forecast product demand"""

    def __init__(self, method='prophet'):
        """
        Initialize forecaster

        Args:
            method: 'prophet', 'arima', 'exponential_smoothing'
        """
        self.method = method
        self.model = None

    def prepare_data(self, sales_data):
        """Prepare time series data"""
        if self.method == 'prophet':
            # Prophet requires 'ds' and 'y' columns
            df = sales_data.rename(columns={'date': 'ds', 'sales': 'y'})
        else:
            df = sales_data.copy()
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')

        return df

    def train(self, sales_data):
        """Train forecasting model"""
        df = self.prepare_data(sales_data)

        if self.method == 'prophet':
            self.model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False
            )
            self.model.fit(df)

        elif self.method == 'arima':
            # Auto ARIMA would be better, but here's a simple example
            self.model = ARIMA(df['sales'], order=(1, 1, 1))
            self.model = self.model.fit()

        elif self.method == 'exponential_smoothing':
            self.model = ExponentialSmoothing(
                df['sales'],
                seasonal_periods=12,
                trend='add',
                seasonal='add'
            ).fit()

        print(f"{self.method.upper()} model trained successfully")

    def forecast(self, periods=30):
        """Generate forecast"""
        if self.method == 'prophet':
            future = self.model.make_future_dataframe(periods=periods)
            forecast = self.model.predict(future)
            return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

        elif self.method == 'arima':
            forecast = self.model.forecast(steps=periods)
            return pd.DataFrame({
                'date': pd.date_range(start=self.model.data.dates[-1], periods=periods+1, freq='D')[1:],
                'forecast': forecast
            })

        elif self.method == 'exponential_smoothing':
            forecast = self.model.forecast(steps=periods)
            return pd.DataFrame({
                'date': pd.date_range(start=df.index[-1], periods=periods+1, freq='D')[1:],
                'forecast': forecast
            })

    def plot_forecast(self, historical_data, forecast_data):
        """Visualize forecast"""
        plt.figure(figsize=(14, 6))

        # Historical data
        plt.plot(historical_data['date'], historical_data['sales'],
                label='Historical', color='blue')

        # Forecast
        if self.method == 'prophet':
            plt.plot(forecast_data['ds'], forecast_data['yhat'],
                    label='Forecast', color='red')
            plt.fill_between(forecast_data['ds'],
                           forecast_data['yhat_lower'],
                           forecast_data['yhat_upper'],
                           alpha=0.3, color='red', label='Confidence Interval')
        else:
            plt.plot(forecast_data['date'], forecast_data['forecast'],
                    label='Forecast', color='red')

        plt.xlabel('Date')
        plt.ylabel('Sales')
        plt.title(f'Sales Forecast ({self.method.upper()})')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
```

## Lead Scoring

### Predictive Lead Scoring Model

```python
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
import pandas as pd

class LeadScorer:
    """Score leads based on conversion probability"""

    def __init__(self):
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )

    def create_lead_features(self, lead_data):
        """
        Create features for lead scoring

        Features:
        - Demographic fit
        - Engagement level
        - Company characteristics (B2B)
        - Behavioral signals
        """
        features = pd.DataFrame()

        # Engagement features
        features['page_views'] = lead_data['page_views']
        features['time_on_site_minutes'] = lead_data['time_on_site'] / 60
        features['sessions'] = lead_data['sessions']
        features['days_since_first_visit'] = lead_data['days_since_first_visit']

        # Content engagement
        features['blog_posts_viewed'] = lead_data['blog_posts_viewed']
        features['case_studies_viewed'] = lead_data['case_studies_viewed']
        features['pricing_page_visited'] = lead_data['pricing_page_visited'].astype(int)
        features['demo_requested'] = lead_data['demo_requested'].astype(int)

        # Demographic fit
        features['company_size'] = lead_data['company_size']
        features['industry_fit'] = lead_data['industry'].isin(['Technology', 'Finance']).astype(int)
        features['job_title_decision_maker'] = lead_data['job_title'].isin(
            ['CEO', 'CTO', 'VP', 'Director']
        ).astype(int)

        # Source quality
        features['source_quality'] = lead_data['source'].map({
            'Organic Search': 5,
            'Referral': 4,
            'Direct': 4,
            'Social': 3,
            'Paid Search': 3,
            'Display': 2
        }).fillna(2)

        return features

    def train(self, X_train, y_train):
        """Train lead scoring model"""
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5, scoring='roc_auc')
        print(f"Cross-validation AUC scores: {cv_scores}")
        print(f"Mean CV AUC: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")

        # Train final model
        self.model.fit(X_train, y_train)

    def score_leads(self, X):
        """
        Score new leads

        Returns:
            DataFrame with lead scores and grades
        """
        probabilities = self.model.predict_proba(X)[:, 1] * 100

        scores = pd.DataFrame({
            'lead_score': probabilities.round(0).astype(int),
            'lead_grade': pd.cut(
                probabilities,
                bins=[0, 25, 50, 75, 90, 100],
                labels=['D', 'C', 'B', 'A', 'A+']
            ),
            'priority': pd.cut(
                probabilities,
                bins=[0, 50, 75, 100],
                labels=['Low', 'Medium', 'High']
            )
        })

        return scores
```

## Model Deployment & Monitoring

### Model Deployment

```python
import joblib
import json
from datetime import datetime

class ModelDeployment:
    """Deploy and version predictive models"""

    def __init__(self, model, model_name):
        self.model = model
        self.model_name = model_name
        self.version = datetime.now().strftime('%Y%m%d_%H%M%S')

    def save_model(self, path='models/'):
        """Save model to disk"""
        filename = f"{path}{self.model_name}_v{self.version}.pkl"
        joblib.dump(self.model, filename)

        # Save metadata
        metadata = {
            'model_name': self.model_name,
            'version': self.version,
            'timestamp': datetime.now().isoformat(),
            'model_type': type(self.model).__name__
        }

        with open(f"{path}{self.model_name}_v{self.version}_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"Model saved: {filename}")
        return filename

    @staticmethod
    def load_model(filename):
        """Load model from disk"""
        model = joblib.load(filename)
        print(f"Model loaded: {filename}")
        return model
```

### Model Monitoring

```sql
-- Track model performance over time
CREATE TABLE model_predictions (
    prediction_id SERIAL PRIMARY KEY,
    model_name VARCHAR(255),
    model_version VARCHAR(50),
    customer_id VARCHAR(255),
    prediction_date TIMESTAMP,
    predicted_value FLOAT,
    predicted_probability FLOAT,
    actual_value FLOAT,  -- Filled in later when actual outcome known
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Monitor prediction accuracy
WITH prediction_accuracy AS (
  SELECT
    model_name,
    model_version,
    DATE_TRUNC('week', prediction_date) as week,
    -- For classification
    AVG(CASE WHEN (predicted_probability > 0.5 AND actual_value = 1) OR
                  (predicted_probability <= 0.5 AND actual_value = 0)
             THEN 1.0 ELSE 0.0 END) as accuracy,
    -- For regression
    AVG(ABS(predicted_value - actual_value)) as mae,
    SQRT(AVG(POWER(predicted_value - actual_value, 2))) as rmse
  FROM model_predictions
  WHERE actual_value IS NOT NULL
  GROUP BY 1, 2, 3
)
SELECT
  week,
  model_name,
  model_version,
  accuracy,
  mae,
  rmse,
  -- Alert if accuracy drops below threshold
  CASE WHEN accuracy < 0.70 THEN 'ALERT: Accuracy below threshold' ELSE 'OK' END as status
FROM prediction_accuracy
ORDER BY week DESC, model_name;
```

## Best Practices

### Model Development

1. **Start Simple**: Begin with simple models (logistic regression, linear regression)
2. **Feature Engineering**: Often more important than algorithm choice
3. **Cross-Validation**: Always use CV to avoid overfitting
4. **Handle Imbalance**: Use techniques like SMOTE, class weights for imbalanced data
5. **Interpretability**: Prefer interpretable models for business stakeholders

### Production Deployment

1. **Version Control**: Track model versions and training data
2. **A/B Testing**: Test new models against current production model
3. **Monitoring**: Track prediction accuracy over time
4. **Retraining**: Schedule regular model retraining
5. **Fallback**: Have backup model or business rules if model fails

### Common Pitfalls

- **Data Leakage**: Using future information in training
- **Overfitting**: Model too complex, doesn't generalize
- **Selection Bias**: Training data not representative
- **Ignoring Business Context**: Technically good model, but wrong for business
- **No Baseline**: Not comparing to simple heuristics
- **Static Models**: Not retraining as data distribution changes

## Key Takeaways

- **Business Problem First**: Start with clear business objective
- **Data Quality Critical**: Garbage in, garbage out
- **Simple Often Wins**: Don't over-complicate
- **Validate Rigorously**: Test on held-out data
- **Monitor Continuously**: Models degrade over time
- **Communicate Clearly**: Explain predictions to stakeholders
- **Iterate**: Continuously improve based on feedback

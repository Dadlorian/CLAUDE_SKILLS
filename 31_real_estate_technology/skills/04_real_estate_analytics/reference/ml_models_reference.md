# Machine Learning Models Reference

## Model Types

### XGBoost
```python
from xgboost import XGBRegressor

model = XGBRegressor(
    n_estimators=1000,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8
)
model.fit(X_train, y_train)
```

### Random Forest
```python
from sklearn.ensemble import RandomForestRegressor

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=20,
    min_samples_split=10,
    random_state=42
)
```

### Neural Network
```python
from tensorflow import keras

model = keras.Sequential([
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dense(1)
])
model.compile(optimizer='adam', loss='mse')
```

## Feature Engineering
```python
# Derived features
df['age'] = current_year - df['year_built']
df['price_per_sqft'] = df['price'] / df['sqft']
df['bed_bath_ratio'] = df['bedrooms'] / df['bathrooms']

# Location features (clustering)
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=50)
df['location_cluster'] = kmeans.fit_predict(df[['lat', 'lon']])

# Temporal features
df['month'] = df['sale_date'].dt.month
df['quarter'] = df['sale_date'].dt.quarter
```

## Evaluation Metrics
```python
from sklearn.metrics import mean_absolute_error, r2_score

mae = mean_absolute_error(y_true, y_pred)
mape = np.mean(np.abs((y_true - y_pred) / y_true))
r2 = r2_score(y_true, y_pred)
```

## See Also
- valuation_methods.md
- forecasting_models.md

# Building an AVM Guide

## Step 1: Data Collection
- Historical sales (12-24 months)
- Property characteristics
- Location data
- Market conditions

## Step 2: Feature Engineering
```python
features = [
    # Physical
    'bedrooms', 'bathrooms', 'sqft', 'lot_size', 'year_built',
    # Location
    'latitude', 'longitude', 'zip_code',
    # Derived
    'age', 'price_per_sqft_neighborhood'
]
```

## Step 3: Train Model
```python
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = XGBRegressor(n_estimators=1000, learning_rate=0.05)
model.fit(X_train, y_train)
```

## Step 4: Validate
```python
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"MAE: ${mae:,.0f}")
```

## Step 5: Deploy
```python
def predict_value(property_data):
    features = extract_features(property_data)
    value = model.predict([features])[0]
    return int(value)
```

## See Also
- ml_models_reference.md
- model_training_guide.md

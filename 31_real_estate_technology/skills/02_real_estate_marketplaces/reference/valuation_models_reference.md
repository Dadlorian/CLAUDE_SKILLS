# Valuation Models Reference (AVM)

## Quick Reference for Automated Valuation Models

### AVM Overview

**Automated Valuation Model (AVM)**: Machine learning models that estimate property values based on historical sales data, property characteristics, and market trends.

**Common Uses**:
- Zillow Zestimate
- Redfin Estimate
- Realtor.com Estimated Home Value
- Mortgage underwriting
- Portfolio valuation

### Key Features for Valuation

```javascript
const VALUATION_FEATURES = {
  // Property characteristics
  physical: [
    'bedrooms',
    'bathrooms',
    'total_sqft',
    'lot_size_sqft',
    'year_built',
    'property_type',
    'stories',
    'garage_spaces',
    'basement_sqft'
  ],

  // Location
  location: [
    'latitude',
    'longitude',
    'zip_code',
    'school_district',
    'walkability_score',
    'transit_score',
    'distance_to_cbd',
    'neighborhood_quality_index'
  ],

  // Condition/quality
  quality: [
    'condition_rating',      // 1-5 scale
    'renovation_year',
    'has_pool',
    'has_ac',
    'heating_type',
    'roof_type',
    'flooring_type'
  ],

  // Market factors
  market: [
    'days_on_market',
    'price_per_sqft_neighborhood',
    'median_sale_price_zip',
    'inventory_level',
    'season',                 // Q1, Q2, Q3, Q4
    'market_trend'            // hot, normal, cold
  ],

  // Derived features
  derived: [
    'age_of_property',        // current_year - year_built
    'price_per_sqft',
    'bed_to_bath_ratio',
    'lot_to_building_ratio',
    'months_since_renovation'
  ]
};
```

### Comparable Sales (Comps) Selection

```javascript
const findComparables = (subject, options = {}) => {
  const {
    maxDistance = 0.5,        // miles
    maxAgeDiff = 10,          // years
    maxSqftDiff = 0.25,       // 25%
    maxSoldAge = 180,         // days
    minComps = 3,
    maxComps = 10
  } = options;

  const query = {
    // Same property type
    property_type: subject.property_type,

    // Within geographic area
    location: {
      $near: {
        $geometry: {
          type: 'Point',
          coordinates: [subject.longitude, subject.latitude]
        },
        $maxDistance: maxDistance * 1609.34 // miles to meters
      }
    },

    // Similar size
    total_sqft: {
      $gte: subject.total_sqft * (1 - maxSqftDiff),
      $lte: subject.total_sqft * (1 + maxSqftDiff)
    },

    // Similar age
    year_built: {
      $gte: subject.year_built - maxAgeDiff,
      $lte: subject.year_built + maxAgeDiff
    },

    // Recently sold
    sale_date: {
      $gte: new Date(Date.now() - maxSoldAge * 24 * 60 * 60 * 1000)
    },

    // Exclude subject property
    property_id: { $ne: subject.property_id }
  };

  return db.sales.find(query)
    .sort({ sale_date: -1 })
    .limit(maxComps);
};
```

### Comp Adjustment Factors

```javascript
const adjustCompPrice = (comp, subject) => {
  let adjustedPrice = comp.sale_price;

  // Adjust for size difference
  const sqftDiff = subject.total_sqft - comp.total_sqft;
  const sqftAdjustment = sqftDiff * comp.price_per_sqft;
  adjustedPrice += sqftAdjustment;

  // Adjust for bedroom difference
  const bedroomDiff = subject.bedrooms - comp.bedrooms;
  adjustedPrice += bedroomDiff * 15000; // $15k per bedroom

  // Adjust for bathroom difference
  const bathroomDiff = subject.bathrooms - comp.bathrooms;
  adjustedPrice += bathroomDiff * 8000; // $8k per bathroom

  // Adjust for garage
  const garageDiff = subject.garage_spaces - comp.garage_spaces;
  adjustedPrice += garageDiff * 10000; // $10k per space

  // Adjust for pool
  if (subject.has_pool && !comp.has_pool) {
    adjustedPrice += 25000;
  } else if (!subject.has_pool && comp.has_pool) {
    adjustedPrice -= 25000;
  }

  // Adjust for time (market appreciation)
  const monthsSinceSale = (Date.now() - comp.sale_date) / (30 * 24 * 60 * 60 * 1000);
  const appreciationRate = 0.005; // 0.5% per month
  adjustedPrice *= (1 + appreciationRate * monthsSinceSale);

  // Adjust for condition
  const conditionDiff = subject.condition_rating - comp.condition_rating;
  adjustedPrice += conditionDiff * (adjustedPrice * 0.05); // 5% per rating point

  return {
    original_price: comp.sale_price,
    adjusted_price: adjustedPrice,
    adjustments: {
      sqft: sqftAdjustment,
      bedrooms: bedroomDiff * 15000,
      bathrooms: bathroomDiff * 8000,
      garage: garageDiff * 10000,
      pool: subject.has_pool !== comp.has_pool ? 25000 : 0,
      time: adjustedPrice - comp.sale_price,
      condition: conditionDiff * (adjustedPrice * 0.05)
    }
  };
};
```

### Simple AVM (Weighted Comps)

```javascript
const estimateValue_WeightedComps = (subject, comps) => {
  if (!comps || comps.length === 0) {
    throw new Error('No comparable sales found');
  }

  // Adjust each comp
  const adjustedComps = comps.map(comp => {
    const adjusted = adjustCompPrice(comp, subject);

    // Calculate similarity score (0-1)
    const similarity = calculateSimilarity(subject, comp);

    return {
      ...adjusted,
      comp,
      similarity,
      weight: similarity // Use similarity as weight
    };
  });

  // Normalize weights to sum to 1
  const totalWeight = adjustedComps.reduce((sum, c) => sum + c.weight, 0);
  adjustedComps.forEach(c => c.weight = c.weight / totalWeight);

  // Calculate weighted average
  const estimatedValue = adjustedComps.reduce((sum, c) => {
    return sum + (c.adjusted_price * c.weight);
  }, 0);

  // Calculate confidence interval
  const prices = adjustedComps.map(c => c.adjusted_price);
  const stdDev = calculateStdDev(prices);

  return {
    estimated_value: Math.round(estimatedValue),
    confidence_low: Math.round(estimatedValue - stdDev),
    confidence_high: Math.round(estimatedValue + stdDev),
    comp_count: comps.length,
    comps: adjustedComps
  };
};

const calculateSimilarity = (subject, comp) => {
  let score = 1.0;

  // Distance penalty
  const distance = calculateDistance(subject, comp); // miles
  score *= Math.max(0, 1 - distance / 2); // Penalize up to 2 miles

  // Size similarity
  const sizeDiff = Math.abs(subject.total_sqft - comp.total_sqft) / subject.total_sqft;
  score *= Math.max(0, 1 - sizeDiff);

  // Age similarity
  const ageDiff = Math.abs(subject.year_built - comp.year_built) / 50;
  score *= Math.max(0, 1 - ageDiff);

  // Sale recency
  const monthsOld = (Date.now() - comp.sale_date) / (30 * 24 * 60 * 60 * 1000);
  score *= Math.max(0, 1 - monthsOld / 12);

  return score;
};
```

### Machine Learning AVM (XGBoost)

```python
# Python implementation
import xgboost as xgb
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

def build_avm_model(sales_data):
    """Build XGBoost AVM model"""

    # Prepare features
    feature_cols = [
        'bedrooms', 'bathrooms', 'total_sqft', 'lot_size_sqft',
        'year_built', 'latitude', 'longitude',
        'condition_rating', 'has_pool', 'has_ac', 'garage_spaces',
        'price_per_sqft_neighborhood', 'median_sale_price_zip',
        'walkability_score', 'school_rating'
    ]

    X = sales_data[feature_cols]
    y = sales_data['sale_price']

    # Feature engineering
    X['age'] = 2025 - X['year_built']
    X['bed_to_bath_ratio'] = X['bedrooms'] / (X['bathrooms'] + 0.1)
    X['price_per_sqft_ratio'] = X['price_per_sqft_neighborhood'] / X['median_sale_price_zip']

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # XGBoost model
    model = xgb.XGBRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        max_depth=6,
        min_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='reg:squarederror',
        random_state=42
    )

    # Train
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        early_stopping_rounds=50,
        verbose=False
    )

    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"MAE: ${mae:,.0f}")
    print(f"R²: {r2:.4f}")

    return model

def predict_value(model, property_features):
    """Predict property value with confidence interval"""

    # Prepare features (same as training)
    features = prepare_features(property_features)

    # Predict
    predicted_value = model.predict([features])[0]

    # Estimate uncertainty using quantile regression
    # Train additional models for confidence bounds
    # (simplified version - in production use proper quantile regression)

    # Use prediction intervals based on historical error
    error_margin = predicted_value * 0.10  # ±10%

    return {
        'estimated_value': int(predicted_value),
        'confidence_low': int(predicted_value - error_margin),
        'confidence_high': int(predicted_value + error_margin),
        'confidence_score': 0.85  # Based on model R²
    }
```

### Hedonic Regression Model

```python
# Linear regression with interaction terms
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures

def build_hedonic_model(sales_data):
    """Hedonic pricing model"""

    # Core features
    features = [
        'bedrooms', 'bathrooms', 'total_sqft',
        'latitude', 'longitude', 'year_built'
    ]

    X = sales_data[features]
    y = np.log(sales_data['sale_price'])  # Log transform price

    # Add polynomial and interaction features
    poly = PolynomialFeatures(degree=2, include_bias=False)
    X_poly = poly.fit_transform(X)

    # Ridge regression (handles multicollinearity)
    model = Ridge(alpha=1.0)
    model.fit(X_poly, y)

    return model, poly

def predict_hedonic(model, poly, property_features):
    """Predict using hedonic model"""

    X = prepare_features(property_features)
    X_poly = poly.transform([X])

    log_price = model.predict(X_poly)[0]
    price = np.exp(log_price)

    return int(price)
```

### Accuracy Metrics

```javascript
const calculateAccuracyMetrics = (predictions, actuals) => {
  const n = predictions.length;

  // Mean Absolute Error
  const mae = predictions.reduce((sum, pred, i) => {
    return sum + Math.abs(pred - actuals[i]);
  }, 0) / n;

  // Mean Absolute Percentage Error
  const mape = predictions.reduce((sum, pred, i) => {
    return sum + Math.abs((pred - actuals[i]) / actuals[i]);
  }, 0) / n;

  // Median Absolute Percentage Error
  const apes = predictions.map((pred, i) =>
    Math.abs((pred - actuals[i]) / actuals[i])
  );
  const medianAPE = median(apes);

  // Within 5% accuracy
  const within5Pct = predictions.filter((pred, i) =>
    Math.abs((pred - actuals[i]) / actuals[i]) < 0.05
  ).length / n;

  // Within 10% accuracy
  const within10Pct = predictions.filter((pred, i) =>
    Math.abs((pred - actuals[i]) / actuals[i]) < 0.10
  ).length / n;

  return {
    mae: Math.round(mae),
    mape: (mape * 100).toFixed(2) + '%',
    median_ape: (medianAPE * 100).toFixed(2) + '%',
    within_5_pct: (within5Pct * 100).toFixed(1) + '%',
    within_10_pct: (within10Pct * 100).toFixed(1) + '%'
  };
};
```

### AVM Display (Frontend)

```javascript
const AVMDisplay = ({ property }) => {
  const [valuation, setValuation] = useState(null);

  useEffect(() => {
    fetchValuation(property.id).then(setValuation);
  }, [property.id]);

  if (!valuation) return <LoadingSpinner />;

  return (
    <div className="avm-container">
      <h3>Estimated Home Value</h3>

      <div className="value-estimate">
        <div className="primary-estimate">
          ${valuation.estimated_value.toLocaleString()}
        </div>

        <div className="confidence-range">
          <div className="range-bar">
            <div className="range-fill" style={{
              left: `${((valuation.confidence_low / valuation.confidence_high) * 100)}%`,
              width: `${(((valuation.confidence_high - valuation.confidence_low) / valuation.confidence_high) * 100)}%`
            }}></div>
          </div>
          <div className="range-labels">
            <span>${valuation.confidence_low.toLocaleString()}</span>
            <span>${valuation.confidence_high.toLocaleString()}</span>
          </div>
        </div>

        <div className="value-details">
          <div className="detail-item">
            <span className="label">Based on:</span>
            <span className="value">{valuation.comp_count} comparable sales</span>
          </div>
          <div className="detail-item">
            <span className="label">Last updated:</span>
            <span className="value">{formatDate(valuation.updated_at)}</span>
          </div>
          <div className="detail-item">
            <span className="label">Confidence:</span>
            <span className="value">{(valuation.confidence_score * 100).toFixed(0)}%</span>
          </div>
        </div>

        <button onClick={() => requestDetailedCMA()}>
          Get Detailed Market Analysis
        </button>
      </div>

      <div className="disclaimer">
        This is an estimate only. Actual market value may vary.
        Consult with a local real estate professional for an accurate valuation.
      </div>
    </div>
  );
};
```

### Industry Benchmarks

| AVM Provider | Median Error | Within 10% | Within 20% |
|--------------|--------------|------------|------------|
| Zillow Zestimate | 2.4% | 78% | 95% |
| Redfin Estimate | 2.2% | 80% | 96% |
| Realtor.com | 2.9% | 74% | 93% |
| CoreLogic | 2.5% | 77% | 94% |

### Best Practices

1. **Use Multiple Models**
   - Ensemble of XGBoost, Random Forest, Linear Regression
   - Average predictions for robustness

2. **Regular Retraining**
   - Retrain monthly with latest sales data
   - Monitor for model drift

3. **Local Market Adjustment**
   - Train separate models per market
   - Account for local factors

4. **Transparency**
   - Show comparable sales
   - Explain confidence intervals
   - Disclaim limitations

5. **Validation**
   - Hold-out test set
   - Cross-validation
   - Monitor production accuracy

## See Also
- property_search_reference.md
- lead_management_reference.md
- mls_reso_standards.md

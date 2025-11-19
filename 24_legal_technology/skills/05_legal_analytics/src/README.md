# Legal Analytics Examples

This directory contains 10 comprehensive Python/SQL examples for legal technology data analysis. Each module demonstrates practical analytics implementations for legal departments.

## File Descriptions

### 1. **01_legal_spend_analysis.py** (172 lines)
Analyzes total legal department spending patterns across matters and vendors.
- **Key Classes**: `LegalSpendAnalyzer`
- **Features**:
  - Spend analysis by law firm, practice area, and matter
  - Monthly trend analysis
  - Outlier detection for high-value invoices
  - Cost per matter calculations
  - Summary report generation

### 2. **02_matter_cost_prediction.py** (211 lines)
Predicts total cost and duration of legal matters using machine learning.
- **Key Classes**: `MatterCostPredictor`
- **Features**:
  - ML model training using RandomForest
  - Cost prediction for new matters
  - Feature importance analysis
  - Batch prediction capabilities
  - Model persistence (save/load)

### 3. **03_settlement_modeling.py** (196 lines)
Analyzes settlement negotiations and outcomes.
- **Key Classes**: `SettlementAnalyzer`
- **Features**:
  - Settlement success rate metrics
  - Recovery rate analysis by claim type
  - Negotiation efficiency scoring
  - Settlement variance analysis
  - Predictive factor analysis

### 4. **04_rate_analysis.py** (210 lines)
Analyzes attorney hourly rates and billing structures.
- **Key Classes**: `RateAnalyzer`
- **Features**:
  - Rate analysis by seniority level
  - Rate benchmarking by firm
  - Practice area rate comparison
  - Rate increase trends
  - Excessive rate identification
  - Billing efficiency by rate tier

### 5. **05_outside_counsel_scorecard.py** (226 lines)
Evaluates and scores outside law firms on multiple performance metrics.
- **Key Classes**: `OutsideCounselScorecard`
- **Features**:
  - Composite performance scoring
  - Cost efficiency analysis
  - Quality performance metrics
  - Practice area performance breakdown
  - Recommendations engine

### 6. **06_litigation_cost_benchmark.py** (239 lines)
Benchmarks litigation costs against industry standards.
- **Key Classes**: `LitigationBenchmark`
- **Features**:
  - Cost benchmarking by case type
  - Cost analysis by claim size
  - Efficiency metrics calculation
  - Outcome analysis with ROI
  - Predictive cost modeling
  - Industry comparison

### 7. **07_tableau_dashboard.py** (297 lines)
Creates data formatted for interactive Tableau dashboards.
- **Key Classes**: `TableauDashboardGenerator`
- **Features**:
  - Spend dashboard data generation
  - Performance dashboard metrics
  - Budget variance dashboard data
  - JSON export for Tableau
  - CSV export for data integration
  - KPI summary generation

### 8. **08_sql_analytics_queries.py** (262 lines)
Provides SQL query templates for legal analytics on databases.
- **Key Classes**: `SQLAnalyticsQueries`
- **Features**:
  - 12 pre-built SQL queries
  - Spend analysis queries
  - Rate analysis queries
  - Settlement and litigation queries
  - Outside counsel performance queries
  - Budget variance queries
  - Attorney utilization queries

### 9. **09_time_entry_analysis.py** (266 lines)
Analyzes attorney time entries and utilization metrics.
- **Key Classes**: `TimeEntryAnalyzer`
- **Features**:
  - Utilization by attorney
  - Seniority level analysis
  - Practice area utilization
  - Monthly trend analysis
  - Non-billable time tracking
  - Firm comparison
  - Underutilized attorney identification

### 10. **10_budget_variance.py** (301 lines)
Analyzes budget vs. actual spending and variance trends.
- **Key Classes**: `BudgetVarianceAnalyzer`
- **Features**:
  - Budget variance calculations
  - Variance analysis by practice area/type
  - Complexity-based variance
  - Overbudget matter identification
  - Budget forecasting
  - Contingency reserve analysis
  - High-risk matter identification

## Dependencies

All examples use standard Python libraries:
- pandas
- numpy
- scipy
- scikit-learn (for ML models)
- matplotlib/seaborn (for visualization)
- joblib (for model persistence)

## Usage Examples

### Legal Spend Analysis
```python
from 01_legal_spend_analysis import LegalSpendAnalyzer

analyzer = LegalSpendAnalyzer()
analyzer.generate_mock_data(1000)
print(analyzer.analyze_by_firm())
print(analyzer.calculate_cost_per_matter())
```

### Cost Prediction
```python
from 02_matter_cost_prediction import MatterCostPredictor

predictor = MatterCostPredictor()
predictor.generate_training_data(500)
metrics = predictor.train_model()
predicted_cost = predictor.predict_cost({...})
```

### Settlement Analysis
```python
from 03_settlement_modeling import SettlementAnalyzer

analyzer = SettlementAnalyzer()
analyzer.generate_settlement_data(200)
print(analyzer.recovery_analysis())
```

## Running Examples

Each module includes executable example code:

```bash
python 01_legal_spend_analysis.py
python 02_matter_cost_prediction.py
python 03_settlement_modeling.py
# ... etc
```

## Data Analysis Capabilities

These modules provide:
- **Spend Analytics**: Track and analyze legal spending
- **Predictive Modeling**: Forecast matter costs
- **Performance Metrics**: Score outside counsel
- **Benchmarking**: Compare against industry standards
- **Utilization Tracking**: Monitor attorney billable time
- **Budget Management**: Track variance and forecast costs
- **Settlement Analytics**: Analyze negotiation outcomes
- **Litigation Analytics**: Benchmark case costs

## Export Formats

All modules support export to:
- CSV files for further analysis
- JSON for dashboard integration
- Python dataframes for programmatic use

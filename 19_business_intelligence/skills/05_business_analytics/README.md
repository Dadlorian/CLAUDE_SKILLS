# Business Analytics Subskill

Complete business analytics mastery with real-world patterns, comprehensive references, practical guides, and production-ready code.

## Structure

### skill.md
Main skill document covering:
- Core competencies (10 major areas)
- Key principles and methodologies
- Analytical patterns and frameworks
- Tools and technologies
- Best practices and career paths

### reference/ (14 files)
Comprehensive reference library:
1. **Revenue Metrics** - MRR, ARR, growth rates, ARPU
2. **Customer Acquisition Metrics** - CAC, LTV:CAC, conversion rates
3. **Lifetime Value (LTV)** - Calculation methods, prediction, optimization
4. **Churn & Retention** - Churn prediction, retention analysis, cohort retention
5. **Cohort Analysis Patterns** - Retention cohorts, revenue cohorts, segmentation
6. **Funnel Analysis** - Conversion funnels, drop-off analysis, optimization
7. **Attribution Models** - First/last touch, multi-touch, data-driven attribution
8. **Statistical Methods** - Hypothesis testing, regression, correlation, ANOVA
9. **A/B Testing Framework** - Experimental design, analysis, decision-making
10. **RFM Analysis** - Segmentation, customer value, targeting strategies
11. **Product Analytics** - Engagement metrics, activation, feature adoption
12. **Customer Segmentation** - Clustering, personas, behavioral segments
13. **KPI Dashboards** - Design principles, templates, best practices
14. **Predictive Analytics** - Churn prediction, LTV forecasting, demand planning

### guides/ (14 files)
Step-by-step practical tutorials:
1. **Cohort Analysis Guide** - Complete walkthrough with SQL and visualizations
2. **Funnel Optimization Guide** - Identify and fix conversion bottlenecks
3. **Customer Segmentation** - Build actionable customer segments
4. **RFM Analysis** - Implement RFM scoring and strategies
5. **Predictive Analytics** - Build and deploy prediction models
6. **Statistical Testing** - Design and analyze experiments
7. **Marketing Attribution** - Implement attribution models
8. **Product Analytics** - Measure and improve product engagement
9. **Metrics Dashboard** - Build executive and operational dashboards
10. **SQL for Analytics** - Advanced SQL patterns for business analytics
11. **Python Analytics** - Data analysis with pandas and scikit-learn
12. **Data Visualization** - Create compelling visualizations
13. **KPI Framework** - Select and track key performance indicators
14. **Analytics Strategy** - Build organizational analytics capability

### src/ (24 files)
Production-ready code implementations:

**SQL Queries (8 files)**:
- cohort_retention.sql - Cohort retention analysis
- funnel_analysis.sql - Multi-step funnel conversion
- revenue_metrics.sql - Revenue KPI calculations
- customer_ltv.sql - LTV calculation queries
- rfm_segmentation.sql - RFM scoring
- ab_test_analysis.sql - A/B test results
- product_engagement.sql - Product usage metrics
- attribution_models.sql - Attribution logic
- cohort_revenue.sql - Revenue cohort analysis

**Python Scripts (9 files)**:
- churn_prediction.py - Random Forest churn model
- ltv_prediction.py - Customer LTV prediction
- segmentation_kmeans.py - K-means clustering
- ab_test_calculator.py - Statistical test calculations
- cohort_viz.py - Cohort heatmap visualizations
- funnel_viz.py - Funnel visualization tools
- dashboard_metrics.py - Dashboard data preparation
- statistical_tests.py - Hypothesis testing suite

**R Scripts (5 files)**:
- time_series_forecast.R - ARIMA/Prophet forecasting
- survival_analysis.R - Customer lifetime analysis
- rfm_clustering.R - RFM cluster analysis
- regression_analysis.R - Statistical modeling
- correlation_analysis.R - Correlation matrices

**Jupyter Notebooks (2 files)**:
- analytics_notebook.ipynb - End-to-end analysis workflow
- exploration_notebook.ipynb - Exploratory data analysis

## Key Features

### Real-World Patterns
- Actual SQL queries used in production
- Battle-tested Python implementations
- Industry-standard methodologies
- Practical examples from e-commerce, SaaS, marketplaces

### Comprehensive Coverage
- All major business analytics techniques
- Statistical rigor with practical application
- From basic metrics to advanced ML models
- Clear progression from beginner to advanced

### Actionable Insights
- Focus on business impact, not just analysis
- Clear interpretation guidelines
- Stakeholder communication templates
- Decision-making frameworks

### Production-Ready Code
- Well-documented, maintainable code
- Error handling and edge cases
- Performance optimized
- Ready to adapt to your data

## Usage

### For Learning
1. Start with skill.md for overview
2. Read relevant reference files for theory
3. Follow guides for hands-on practice
4. Adapt src code to your data

### For Implementation
1. Identify business problem
2. Choose appropriate technique from references
3. Follow implementation guide
4. Customize src code for your use case
5. Deploy and monitor

### For Teams
- Share reference docs for common language
- Use guides for training and onboarding
- Leverage src code as starting templates
- Build on framework for your analytics needs

## Prerequisites

**Technical Skills**:
- SQL (intermediate level)
- Python or R (basic to intermediate)
- Statistics (basic understanding)
- Data visualization concepts

**Business Knowledge**:
- Understanding of business metrics
- Familiarity with your company's data
- Stakeholder communication skills

**Tools**:
- SQL database (PostgreSQL, BigQuery, Snowflake)
- Python 3.7+ with pandas, scikit-learn
- R 4.0+ with tidyverse (optional)
- BI tool (Tableau, Looker, Mode - optional)

## Quick Start Examples

### Cohort Retention Analysis
```bash
# Use SQL query
psql -d your_database -f src/cohort_retention.sql

# Visualize with Python
python src/cohort_viz.py --data cohort_data.csv
```

### Churn Prediction
```bash
# Train model
python src/churn_prediction.py --train customer_features.csv

# Generate predictions
python src/churn_prediction.py --predict new_customers.csv
```

### RFM Segmentation
```bash
# Calculate RFM scores
psql -d your_database -f src/rfm_segmentation.sql

# Cluster analysis
Rscript src/rfm_clustering.R
```

## Metrics Coverage

**Growth Metrics**:
- User growth, revenue growth, market share
- Viral coefficient, referral rates

**Engagement Metrics**:
- DAU/MAU, session frequency, feature adoption
- Engagement score, stickiness

**Retention Metrics**:
- Churn rate, retention curves, cohort analysis
- Net revenue retention, customer lifetime

**Revenue Metrics**:
- MRR/ARR, ARPU, LTV
- Unit economics, margins

**Acquisition Metrics**:
- CAC, conversion rates, funnel metrics
- Channel effectiveness, ROAS

**Product Metrics**:
- Activation rate, time to value
- Feature usage, product-market fit indicators

## Best Practices Included

1. **Data Quality**: Validation, cleaning, documentation
2. **Statistical Rigor**: Appropriate tests, significance, power
3. **Business Context**: Interpretation, stakeholder communication
4. **Visualization**: Clear, actionable, audience-appropriate
5. **Automation**: Reproducible, scalable, maintainable
6. **Ethics**: Privacy, bias awareness, responsible use

## Contributing

To extend this subskill:
- Add new reference documents for emerging techniques
- Create guides for specific use cases
- Contribute optimized code implementations
- Share real-world examples and case studies

## Support

For questions or issues:
- Review reference docs for methodology
- Check guides for implementation help
- Examine src code for examples
- Refer to main skill.md for overview

## Version

**Version**: 1.0
**Last Updated**: 2024-11-19
**Maintainer**: Business Intelligence Team

## License

Internal use - adapt and customize for your organization's needs.

# Logistics Analytics

## Overview

Logistics Analytics is the systematic application of data science, statistical methods, and advanced analytics techniques to optimize supply chain operations, reduce costs, improve service levels, and drive strategic decision-making in transportation and logistics networks.

## Skill Description

This skill provides comprehensive expertise in logistics analytics, covering:

- **Supply Chain KPIs & Metrics**: Master key performance indicators for warehouse operations, transportation efficiency, inventory management, and order fulfillment
- **Demand Forecasting**: Leverage statistical and machine learning methods to predict future demand patterns and optimize inventory positioning
- **Network Optimization**: Apply operations research techniques to design optimal distribution networks, route planning, and facility location
- **Prescriptive Analytics**: Use optimization algorithms and simulation models to prescribe optimal actions and policies
- **Business Intelligence Tools**: Implement dashboards, reporting systems, and visual analytics for logistics operations
- **Predictive Maintenance**: Forecast equipment failures and optimize maintenance schedules
- **Real-time Analytics**: Process streaming data for live tracking, dynamic routing, and instant decision support

## Key Capabilities

### Analytics Frameworks
- Descriptive Analytics: Understanding what happened
- Diagnostic Analytics: Understanding why it happened
- Predictive Analytics: Forecasting what will happen
- Prescriptive Analytics: Recommending what should be done
- Cognitive Analytics: Autonomous decision-making systems

### Technical Competencies
- Statistical modeling and time series analysis
- Machine learning for logistics applications
- Operations research and optimization
- Data warehouse design and ETL processes
- Real-time data processing and streaming analytics
- Geospatial analytics and visualization
- Dashboard development and BI tools

### Business Domains
- Demand planning and inventory optimization
- Transportation and route optimization
- Warehouse operations analytics
- Supplier performance analysis
- Last-mile delivery optimization
- Network design and facility location
- Risk analytics and scenario planning

## Reference Materials

1. **supply_chain_kpis.md**: Comprehensive catalog of logistics and supply chain KPIs
2. **analytics_frameworks.md**: Industry-standard analytics frameworks and methodologies
3. **bi_tools_comparison.md**: Evaluation of leading business intelligence platforms
4. **forecasting_methods.md**: Statistical and ML forecasting techniques
5. **optimization_algorithms.md**: Operations research algorithms for logistics
6. **data_architecture.md**: Data warehouse and analytics platform design
7. **industry_benchmarks.md**: Performance benchmarks across logistics sectors

## Advanced Analytical Techniques

### 1. Time Series Forecasting

```python
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error

class DemandForecastingEngine:
    """Production-grade demand forecasting system."""

    def __init__(self, historical_data, seasonality_period=52):
        """
        historical_data: DataFrame with columns [timestamp, sku_id, demand]
        seasonality_period: 52 for weekly, 12 for monthly
        """
        self.data = historical_data
        self.seasonality = seasonality_period
        self.models = {}

    def forecast_sarima(self, sku_id, periods=13, confidence=0.95):
        """
        Seasonal ARIMA forecasting with confidence intervals.
        Good for products with clear seasonal patterns.
        """
        sku_data = self.data[self.data['sku_id'] == sku_id].set_index('timestamp')
        demand_series = sku_data['demand']

        # Auto-detect ARIMA parameters using auto_arima
        try:
            model = SARIMAX(
                demand_series,
                order=(1, 1, 1),
                seasonal_order=(1, 1, 1, self.seasonality)
            )
            results = model.fit(disp=False)

            forecast = results.get_forecast(steps=periods)
            forecast_df = forecast.conf_int(alpha=1-confidence)
            forecast_df['point_forecast'] = forecast.predicted_mean

            return {
                'sku_id': sku_id,
                'forecast': forecast_df,
                'rmse': np.sqrt(mean_squared_error(demand_series.tail(periods), forecast.predicted_mean)),
                'mape': mean_absolute_percentage_error(demand_series.tail(periods), forecast.predicted_mean)
            }
        except Exception as e:
            print(f"SARIMA failed for {sku_id}: {e}")
            return None

    def forecast_exponential_smoothing(self, sku_id, periods=13):
        """
        Triple Exponential Smoothing (Holt-Winters) for trend + seasonality.
        More robust than ARIMA for most retail scenarios.
        """
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        sku_data = self.data[self.data['sku_id'] == sku_id]
        demand_series = sku_data['demand'].values

        try:
            model = ExponentialSmoothing(
                demand_series,
                seasonal_periods=self.seasonality,
                trend='add',
                seasonal='add'
            )
            fitted = model.fit(optimized=True)
            forecast = fitted.forecast(steps=periods)

            return {
                'sku_id': sku_id,
                'forecast': forecast,
                'mape': mean_absolute_percentage_error(demand_series[-periods:], forecast[:periods])
            }
        except Exception as e:
            print(f"Exponential smoothing failed: {e}")
            return None

    def forecast_ml_xgboost(self, sku_id, periods=13, lookback=52):
        """
        Machine learning approach using XGBoost.
        Captures non-linear patterns and external factors.
        """
        import xgboost as xgb

        sku_data = self.data[self.data['sku_id'] == sku_id].reset_index()
        demand_series = sku_data['demand'].values

        # Create lagged features
        X, y = [], []
        for i in range(lookback, len(demand_series)):
            X.append(demand_series[i-lookback:i])
            y.append(demand_series[i])

        X = np.array(X)
        y = np.array(y)

        # Train/test split
        split = int(0.8 * len(X))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        # Train XGBoost
        model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1)
        model.fit(X_train, y_train, verbose=False)

        # Forecast
        forecast = []
        current_seq = X[-1]
        for _ in range(periods):
            next_val = model.predict(current_seq.reshape(1, -1))[0]
            forecast.append(next_val)
            current_seq = np.append(current_seq[1:], next_val)

        return {
            'sku_id': sku_id,
            'forecast': np.array(forecast),
            'mape': mean_absolute_percentage_error(y_test, model.predict(X_test))
        }
```

### 2. Network Optimization

```python
from pulp import *
import numpy as np

class DistributionNetworkOptimizer:
    """Optimize facility location and inventory positioning."""

    def optimize_facility_location(self, demand_nodes, potential_facilities, costs, capacity):
        """
        Determine which facilities to open and assign customers.
        Binary integer programming problem.
        """
        num_customers = len(demand_nodes)
        num_facilities = len(potential_facilities)

        # Create problem
        prob = LpProblem("Facility_Location", LpMinimize)

        # Decision variables
        x = [[LpVariable(f"x_{i}_{j}", cat='Binary')
              for j in range(num_facilities)] for i in range(num_customers)]
        y = [LpVariable(f"y_{j}", cat='Binary') for j in range(num_facilities)]

        # Objective: minimize transportation + facility costs
        prob += (
            lpSum([
                costs['transportation'][i][j] * x[i][j]
                for i in range(num_customers)
                for j in range(num_facilities)
            ]) +
            lpSum([costs['fixed'][j] * y[j] for j in range(num_facilities)])
        )

        # Constraints
        # 1. Each customer assigned to exactly one facility
        for i in range(num_customers):
            prob += lpSum([x[i][j] for j in range(num_facilities)]) == 1

        # 2. Facility capacity limits
        for j in range(num_facilities):
            prob += (
                lpSum([demand_nodes[i] * x[i][j] for i in range(num_customers)])
                <= capacity[j] * y[j]
            )

        # 3. Can only assign to facility if it's open
        for i in range(num_customers):
            for j in range(num_facilities):
                prob += x[i][j] <= y[j]

        # Solve
        prob.solve(PULP_CBC_CMD(msg=0))

        # Extract solution
        open_facilities = [j for j in range(num_facilities) if y[j].varValue == 1]
        assignments = {}
        for i in range(num_customers):
            for j in range(num_facilities):
                if x[i][j].varValue == 1:
                    assignments[i] = j

        return {
            'status': LpStatus[prob.status],
            'optimal_cost': value(prob.objective),
            'facilities': open_facilities,
            'assignments': assignments
        }

    def multi_echelon_inventory_optimization(self, demand_forecast, holding_costs, order_costs):
        """
        Optimize inventory across multiple warehouse echelons.
        Balances inventory carrying costs with service level.
        """
        from scipy.optimize import minimize

        def total_cost(safety_stock_levels):
            """Calculate total holding + order costs."""
            # Holding cost: average inventory * holding cost
            holding = np.sum(safety_stock_levels * holding_costs)

            # Order cost (approximation based on demand volatility)
            variability = np.std(demand_forecast)
            order = np.sum(order_costs * (variability / safety_stock_levels))

            return holding + order

        # Optimize
        initial_guess = np.ones(len(demand_forecast)) * np.mean(demand_forecast) * 0.5
        result = minimize(total_cost, initial_guess, method='SLSQP')

        return {
            'optimal_safety_stock': result.x,
            'total_annual_cost': result.fun,
            'service_level': 95
        }
```

### 3. Real-Time Analytics Pipeline

```python
from kafka import KafkaConsumer
import json
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict

class RealTimeLogisticsAnalytics:
    """Stream processing for real-time logistics insights."""

    def __init__(self, kafka_bootstrap_servers):
        self.consumer = KafkaConsumer(
            'shipment_events',
            bootstrap_servers=kafka_bootstrap_servers,
            auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        self.metrics = defaultdict(list)
        self.time_window = timedelta(hours=1)

    def process_shipment_event(self, event):
        """
        Process incoming shipment event and update real-time metrics.
        Event: {shipment_id, status, timestamp, location, carrier, ...}
        """
        timestamp = datetime.fromisoformat(event['timestamp'])
        shipment_id = event['shipment_id']

        # Update metrics
        self.metrics[shipment_id].append({
            'status': event['status'],
            'timestamp': timestamp,
            'location': event.get('location'),
            'carrier': event.get('carrier')
        })

        # Check for exceptions
        exceptions = self._check_exceptions(shipment_id, event)

        return exceptions

    def _check_exceptions(self, shipment_id, event):
        """Identify and flag anomalies."""
        exceptions = []

        # 1. Delivery delay detection
        if event['status'] == 'in_transit':
            history = self.metrics[shipment_id]
            if len(history) > 1:
                elapsed = (event['timestamp'] - history[0]['timestamp']).total_seconds() / 3600
                if elapsed > 24:  # > 24 hours
                    exceptions.append({
                        'type': 'delay_detected',
                        'severity': 'high',
                        'hours': elapsed
                    })

        # 2. Unusual location detection (geofencing)
        if 'location' in event:
            # Compare with expected route
            expected_location = self._get_expected_location(shipment_id)
            distance = self._haversine_distance(event['location'], expected_location)
            if distance > 50:  # > 50 km off course
                exceptions.append({
                    'type': 'route_deviation',
                    'severity': 'medium',
                    'deviation_km': distance
                })

        # 3. Carrier performance anomaly
        if 'carrier' in event:
            carrier_stats = self._get_carrier_stats(event['carrier'])
            if carrier_stats['on_time_rate'] < 0.80:
                exceptions.append({
                    'type': 'carrier_performance_issue',
                    'severity': 'medium',
                    'on_time_rate': carrier_stats['on_time_rate']
                })

        return exceptions

    def calculate_real_time_kpis(self):
        """Generate real-time KPI snapshot."""
        return {
            'on_time_delivery_rate': self._calculate_otif(),
            'average_delivery_time': self._calculate_avg_delivery_time(),
            'shipments_in_transit': self._count_in_transit(),
            'exceptions_count': self._count_exceptions(),
            'carrier_utilization': self._calculate_carrier_utilization(),
            'timestamp': datetime.utcnow().isoformat()
        }

    def _calculate_otif(self):
        """On-Time, In-Full delivery rate."""
        completed_shipments = [
            m for m in self.metrics.values()
            if any(e['status'] == 'delivered' for e in m)
        ]
        if not completed_shipments:
            return None

        on_time = sum(1 for shipment in completed_shipments
                     if self._is_on_time(shipment))
        return on_time / len(completed_shipments)

    def _calculate_avg_delivery_time(self):
        """Average days from pickup to delivery."""
        delivery_times = []
        for shipment in self.metrics.values():
            if len(shipment) >= 2:
                pickup = min(shipment, key=lambda x: x['timestamp'])['timestamp']
                delivery = [e for e in shipment if e['status'] == 'delivered']
                if delivery:
                    deliver_time = delivery[0]['timestamp']
                    days = (deliver_time - pickup).days
                    delivery_times.append(days)

        return np.mean(delivery_times) if delivery_times else None
```

### 4. Prescriptive Analytics for Optimization

```python
class PrescriptiveAnalyticsEngine:
    """Recommend optimal actions based on data and constraints."""

    def optimize_inventory_allocation(self, demand_forecast, safety_stock, service_level):
        """
        Recommend safety stock allocation across multiple SKUs.
        Maximize service level subject to total inventory budget.
        """
        from scipy.optimize import LinearConstraint, minimize

        # Optimization: allocate safety stock to maximize service level
        def service_level_function(ss_allocation):
            """Calculate average service level for given allocation."""
            service_levels = []
            for sku_id, target_ss in enumerate(ss_allocation):
                # Empirical: service level = f(safety_stock_multiplier)
                multiplier = target_ss / np.std(demand_forecast[sku_id])
                # Convert multiplier to service level (Z-score approach)
                sl = norm.cdf(multiplier)  # Normal distribution CDF
                service_levels.append(sl)
            return np.mean(service_levels)

        # Constraint: total inventory budget
        def budget_constraint(ss_allocation):
            holding_cost_per_unit = 0.25  # Annual % of product value
            total_cost = np.sum(ss_allocation * holding_cost_per_unit)
            return total_cost

        # Solve
        initial = np.ones_like(demand_forecast) * 10
        result = minimize(
            lambda x: -service_level_function(x),  # Negate for minimization
            initial,
            constraints={'type': 'ineq', 'fun': lambda x: 100000 - budget_constraint(x)},
            method='SLSQP'
        )

        return {
            'recommended_ss': result.x,
            'expected_service_level': service_level_function(result.x),
            'total_inventory_investment': budget_constraint(result.x)
        }

    def recommend_carrier_selection(self, shipment, carrier_metrics, cost_constraints):
        """
        Recommend best carrier based on historical performance + cost.
        Multi-criteria decision making.
        """
        scoring = {}

        for carrier in carrier_metrics:
            score = 0

            # On-time delivery performance (40%)
            otif = carrier_metrics[carrier]['on_time_rate']
            score += otif * 0.40

            # Cost efficiency (30%)
            cost = carrier_metrics[carrier]['cost_per_unit']
            cost_efficiency = 1 - (cost / max([c['cost_per_unit'] for c in carrier_metrics.values()]))
            score += cost_efficiency * 0.30

            # Capacity availability (20%)
            capacity_avail = carrier_metrics[carrier]['available_capacity']
            score += min(1.0, capacity_avail / shipment['weight']) * 0.20

            # Service area coverage (10%)
            coverage = 1.0 if shipment['destination'] in carrier_metrics[carrier]['service_areas'] else 0.5
            score += coverage * 0.10

            scoring[carrier] = score

        recommended_carrier = max(scoring, key=scoring.get)
        return {
            'recommended_carrier': recommended_carrier,
            'scores': scoring,
            'expected_otif': carrier_metrics[recommended_carrier]['on_time_rate']
        }
```

## Practical Guides

1. **demand_forecasting_guide.md**: Step-by-step approach to implementing demand forecasting
2. **network_optimization_guide.md**: Designing optimal distribution networks
3. **prescriptive_analytics_guide.md**: Building decision optimization systems
4. **kpi_dashboard_guide.md**: Creating effective logistics dashboards
5. **predictive_maintenance_guide.md**: Implementing predictive maintenance programs
6. **real_time_analytics_guide.md**: Building streaming analytics pipelines
7. **ab_testing_guide.md**: Experimentation in logistics operations

## Code Examples

### KPI Dashboards & Reporting
- `kpi_dashboard.py`: Interactive supply chain KPI dashboard
- `warehouse_metrics.py`: Warehouse performance metrics calculator
- `transportation_scorecard.py`: Transportation KPI scorecard

### Demand Forecasting
- `time_series_forecasting.py`: ARIMA/SARIMA forecasting models
- `ml_demand_forecast.py`: Machine learning-based demand prediction
- `forecast_accuracy.py`: Forecast error measurement and optimization

### Optimization & Operations Research
- `vehicle_routing.py`: Vehicle routing problem solver
- `network_optimization.py`: Distribution network optimization
- `inventory_optimization.py`: Multi-echelon inventory optimization

### Data Engineering
- `etl_pipeline.py`: ETL pipeline for logistics data
- `data_quality_checks.py`: Data validation and quality assurance
- `streaming_processor.py`: Real-time data streaming processor

### Visualization & BI
- `supply_chain_viz.py`: Advanced supply chain visualizations
- `geospatial_analysis.py`: Geographic logistics analysis
- `executive_report.py`: Automated executive reporting

## Technology Stack

### Analytics & Data Science
- Python (pandas, numpy, scipy, scikit-learn)
- R (forecast, caret, dplyr)
- SQL (PostgreSQL, SQL Server, Snowflake)
- Apache Spark for big data processing

### Optimization & OR
- PuLP, Pyomo, OR-Tools for optimization
- CPLEX, Gurobi for enterprise optimization
- SimPy for discrete event simulation

### Business Intelligence
- Tableau, Power BI for visualization
- Looker, Qlik for enterprise BI
- Plotly Dash, Streamlit for custom dashboards

### Data Engineering
- Apache Airflow for workflow orchestration
- dbt for data transformation
- Kafka for streaming data
- Docker for containerization

## Learning Path

### Beginner
1. Understand fundamental supply chain KPIs and metrics
2. Learn basic SQL and data manipulation with pandas
3. Create simple descriptive analytics and visualizations
4. Explore basic forecasting methods (moving averages, exponential smoothing)

### Intermediate
1. Master statistical forecasting techniques (ARIMA, seasonal models)
2. Build interactive dashboards with BI tools
3. Implement ETL pipelines and data quality processes
4. Learn linear programming and basic optimization

### Advanced
1. Develop machine learning models for demand prediction
2. Implement complex optimization algorithms (VRP, facility location)
3. Build real-time streaming analytics systems
4. Design enterprise-scale analytics architectures
5. Integrate prescriptive analytics into business processes

## Best Practices

### Data Management
- Establish single source of truth for logistics data
- Implement robust data quality and validation processes
- Design scalable data architecture for growing volumes
- Ensure data security and compliance with regulations

### Analytics Development
- Start with clear business objectives and KPIs
- Use agile methodology for analytics projects
- Validate models with historical data and cross-validation
- Document assumptions, methodology, and limitations
- Implement monitoring and alerting for production models

### Stakeholder Engagement
- Translate technical results into business insights
- Create intuitive visualizations for non-technical audiences
- Establish feedback loops with operations teams
- Build trust through accuracy and reliability
- Provide actionable recommendations, not just data

### Model Operations
- Automate model retraining and updating
- Monitor model performance and drift
- Implement A/B testing for new models
- Version control for models and data pipelines
- Create fallback mechanisms for model failures

## Common Use Cases

1. **Demand Forecasting**: Predict product demand to optimize inventory levels and reduce stockouts
2. **Route Optimization**: Minimize transportation costs and delivery times through optimal routing
3. **Warehouse Slotting**: Optimize product placement to reduce picking time and labor costs
4. **Network Design**: Determine optimal number, location, and capacity of distribution centers
5. **Inventory Optimization**: Balance inventory carrying costs with service level requirements
6. **Predictive Maintenance**: Forecast equipment failures to minimize downtime
7. **Dynamic Pricing**: Optimize pricing based on demand, capacity, and competition
8. **Risk Analytics**: Identify and quantify supply chain risks and disruptions

## Success Metrics

- **Forecast Accuracy**: MAPE, RMSE, bias metrics for demand predictions
- **Cost Reduction**: Transportation costs, inventory holding costs, operational expenses
- **Service Level**: On-time delivery rate, order fill rate, perfect order percentage
- **Efficiency Gains**: Labor productivity, asset utilization, throughput improvements
- **ROI**: Return on analytics investments and initiatives
- **Decision Quality**: Improved outcomes from data-driven decisions
- **User Adoption**: Dashboard usage, report engagement, self-service analytics adoption

## Industry Applications

- **Retail & E-commerce**: Inventory optimization, last-mile delivery, demand sensing
- **Manufacturing**: Production planning, supplier management, inbound logistics
- **Third-Party Logistics**: Network optimization, capacity planning, customer analytics
- **Food & Beverage**: Shelf-life optimization, temperature-controlled logistics, traceability
- **Healthcare**: Medical supply chain, hospital logistics, pharmaceutical distribution
- **Automotive**: Parts distribution, aftermarket logistics, reverse logistics

## Continuous Improvement

- Stay current with emerging analytics techniques and tools
- Benchmark performance against industry standards
- Collect feedback from end-users and stakeholders
- Experiment with new data sources (IoT, satellite, social media)
- Invest in training and upskilling analytics teams
- Foster data-driven culture across the organization

## Related Skills

- Supply Chain Management
- Operations Research
- Data Engineering
- Business Intelligence
- Machine Learning
- Fleet Management
- Warehouse Management

---

*This skill empowers logistics professionals to transform data into actionable insights, optimize complex supply chain networks, and drive measurable business value through advanced analytics.*

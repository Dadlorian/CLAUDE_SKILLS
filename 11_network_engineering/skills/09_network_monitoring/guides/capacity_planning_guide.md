# Capacity Planning Guide

## Data Collection

### Historical Data Gathering
```
Period: 6-12 months of historical data
Metrics to collect:
  - Interface throughput (peak, average, minimum)
  - CPU utilization trends
  - Memory usage trends
  - Connection counts
  - Flow counts
  - Error rates
  - Transaction rates (if application tracked)

Tools:
  - SNMP polling (interface stats)
  - Prometheus time series (1-year retention)
  - NetFlow analysis (top talkers, growth)
  - Application logs (transaction volume)
```

### Growth Rate Analysis

#### Calculate Growth Percentages
```
Linear Growth:
  Month 1 throughput: 2 Gbps
  Month 12 throughput: 3 Gbps
  Growth: 1 Gbps / 12 months = 83 Mbps/month
  Annual rate: 50%

Seasonal Pattern:
  Q1 (Winter): 2.5 Gbps average (peak)
  Q2 (Spring): 2.0 Gbps average
  Q3 (Summer): 2.2 Gbps average
  Q4 (Fall): 3.0 Gbps average (peak)

Exponential Growth (Accelerating):
  Fit to curve: y = a * e^(bx)
  Use to forecast: More accurate than linear
```

## Forecasting Methods

### Method 1: Linear Trend (Simple)
```
Formula: Future = Current + (Growth_Rate × Months)

Example:
  Current (Jan 2024): 2.0 Gbps
  Growth rate: 5% per month
  Forecast (Jan 2025): 2.0 + (2.0 × 0.05 × 12) = 3.2 Gbps
```

### Method 2: Exponential Growth (Accelerating)
```
Formula: Future = Current × (1 + Growth_Rate)^Months

Example:
  Current: 2.0 Gbps
  Growth rate: 5% per month
  Timeline:
    3 months: 2.0 × 1.05^3 = 2.3 Gbps
    6 months: 2.0 × 1.05^6 = 2.7 Gbps
    12 months: 2.0 × 1.05^12 = 3.6 Gbps
```

### Method 3: Seasonal Decomposition
```
Components:
  Observed = Trend + Seasonal + Random

Steps:
  1. Detrend data (remove growth trend)
  2. Identify seasonal pattern
  3. Calculate random/noise
  4. Forecast trend + seasonal pattern

Tools:
  - Python statsmodels
  - R forecast package
  - Grafana time series analysis
```

### Method 4: Business-Driven Forecasting
```
Questions:
  1. How many users will we have?
  2. What's the per-user bandwidth?
  3. What new applications are planned?

Example:
  Users: 1,000 → 1,500 (50% growth)
  Per-user traffic: 2 Mbps → 3 Mbps
  New app addition: +500 Mbps

  Forecast = (1500 × 3) + 500 = 5,000 Mbps = 5 Gbps
```

## Planning Horizons

### Short-term (3-6 months)
```
Purpose: Operations planning
Decision: Any immediate upgrades needed?
Method: Linear trend, simple averaging

Actions:
  - Monitor current utilization
  - Plan maintenance windows
  - Order components with lead times
  - Budget allocation
```

### Medium-term (6-12 months)
```
Purpose: Budget and procurement
Decision: What upgrades are needed?
Method: Growth trend + business forecast

Actions:
  - Order major equipment (8-12 week lead time)
  - Plan deployment (testing, training)
  - Capacity reallocation
  - Link optimization
```

### Long-term (1-3 years)
```
Purpose: Strategic planning
Decision: Major architecture changes?
Method: Scenario analysis, expert judgment

Actions:
  - Plan data center expansion
  - Technology migration
  - Redundancy improvement
  - Cost optimization
```

## Triggering Upgrades

### Capacity Trigger Points
```
Level 1 (70% capacity):
  - Start planning upgrade
  - Order equipment
  - Evaluate alternatives
  Action timing: 6 months before 80% utilization

Level 2 (80% capacity):
  - Implement interim solutions
  - Reduce non-essential traffic
  - Prioritize critical applications
  Action timing: 3 months before 90% utilization

Level 3 (90% capacity):
  - Emergency upgrade needed
  - Implement traffic shaping
  - Activate disaster recovery
  Action timing: Immediate action required

Emergency (95%+ capacity):
  - Service degradation
  - Manual traffic management
  - Demand destruction (off-peak only)
```

### Multiple Threshold Indicators
```
Trigger upgrade when ANY of these occur:
  1. Peak utilization approaches 80%
  2. Average utilization sustains >60% for 1 week
  3. Growth rate exceeds forecast by 20%
  4. Projected to exceed 80% within 6 months
  5. Error rate correlates with congestion
  6. Packet loss detected during peaks
```

## Upgrade Planning

### Pre-upgrade Assessment
```
1. Current capacity utilization
   - Peak vs. average
   - Direction of trend
   - Recent anomalies

2. Upgrade requirements
   - New capacity size (1.5x-2x typical)
   - Interface type (1GbE, 10GbE, 100GbE)
   - Routing capacity (Mpps/Gbps throughput)
   - Redundancy (N+1, N+N)

3. Testing plan
   - Lab validation
   - Traffic stress testing
   - Failover scenarios
   - Interop testing

4. Deployment plan
   - Maintenance window
   - Traffic migration procedure
   - Rollback plan
   - Health checks
```

### Upgrade Sizing

#### Conservative Approach (Recommended)
```
Size for: 2 × projected peak demand

Calculation:
  Current peak: 5 Gbps
  Expected growth: 60% over 24 months
  Future peak: 5 × 1.6 = 8 Gbps
  Upgrade to: 8 × 2 = 16 Gbps capacity

Benefits:
  - Accommodates forecast uncertainty
  - Room for unexpected growth
  - Headroom for redundancy
  - Cost amortization over time
```

#### Aggressive Approach (Cost-Sensitive)
```
Size for: 1.3 × projected peak demand

Calculation:
  Current peak: 5 Gbps
  Expected growth: 60%
  Future peak: 8 Gbps
  Upgrade to: 8 × 1.3 = 10.4 Gbps capacity

Risks:
  - Limited headroom
  - Frequent upgrades
  - No margin for error
  - Higher operational complexity

Use case: Non-critical links, lab environments
```

## Cost Analysis

### Capital vs. Operational Costs

#### Interface Upgrade
```
Scenario: Upgrade 10GbE link to 100GbE

Capital costs:
  Equipment: $50,000
  Installation: $10,000
  Testing: $5,000
  Total CapEx: $65,000
  Useful life: 5 years
  Annual CapEx: $13,000

Operational savings:
  - Fewer upgrade cycles
  - Less congestion management
  - Better performance
  - Reduced overtime

5-year ROI: Usually positive within 12-18 months
```

#### Delay Costs (NOT upgrading)
```
Costs of insufficient capacity:
  - Lost revenue (outages)
  - Degraded user experience
  - Overtime pay
  - Increased errors
  - Customer churn

Example:
  Downtime cost: $100/minute
  1 hour outage due to congestion: $6,000
  Happens quarterly: $24,000/year
```

## Optimization Strategies

### Before Upgrading, Optimize

#### Traffic Engineering
```
1. Implement QoS
   - Prioritize critical traffic
   - Rate limit non-essential
   - Reduce peak demand by 20-30%

2. Optimize routing
   - Equal-cost multipath (ECMP)
   - Better load balancing
   - Reduce bottlenecks

3. Remove wasteful traffic
   - Disable unnecessary services
   - Optimize video streaming bitrates
   - Compress data transfers

Benefit: Extend upgrade timeline by 6-12 months
```

#### WAN Optimization
```
1. Compression
   - Reduce traffic by 20-50%
   - Most effective for text, documents
   - Cache frequently accessed data

2. De-duplication
   - Eliminate redundant data
   - Good for backups, archives

3. Protocol optimization
   - TCP window scaling
   - Larger MTU (if possible)
   - TCP offloading
```

## Reporting

### Executive Dashboard
```
Key metrics:
  - Current vs. peak utilization
  - Growth trend (6, 12, 24 month)
  - Projected upgrade date
  - Cost of upgrade
  - Risk of NOT upgrading

Format: Simple, visual, actionable
Focus: Business impact, cost-benefit
Frequency: Quarterly to management
```

### Technical Detailed Report
```
Sections:
  1. Executive summary
  2. Current state assessment
  3. Growth analysis
  4. Forecasted demand
  5. Upgrade recommendation
  6. Implementation plan
  7. Cost analysis
  8. Risk mitigation
  9. Timeline
  10. Alternative options

Audience: Engineering leadership
Frequency: Semi-annually or as needed
```

## Implementation Checklist

- [ ] Collect 6-12 months historical data
- [ ] Analyze growth trends
- [ ] Determine forecasting method
- [ ] Create baseline projections
- [ ] Identify capacity bottlenecks
- [ ] Define upgrade trigger points
- [ ] Plan upgrade requirements
- [ ] Size new capacity
- [ ] Analyze costs
- [ ] Identify optimization opportunities
- [ ] Create upgrade timeline
- [ ] Develop implementation plan
- [ ] Document assumptions
- [ ] Quarterly review cycles

---

**Guide Type**: Strategic Planning
**Tools**: Prometheus, RRDtool, Excel/Tableau, business forecasts
**Review Frequency**: Quarterly
**Planning Horizon**: 3-5 years
**Last Updated**: 2025-11-19

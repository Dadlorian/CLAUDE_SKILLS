# Aggregation Design Principles

## Overview

Aggregation design is critical for OLAP cube performance, determining which pre-computed summaries are stored to optimize query response times.

## What Are Aggregations?

Pre-calculated summary data stored to avoid calculating the same values repeatedly:

```
Raw Data (1 billion rows):
└── Customer × Product × Date × Store

Aggregations (smaller, faster):
├── Product × Date (10 million rows)
├── Customer × Date (5 million rows)
├── Product × Store (1 million rows)
└── Date only (365 rows)
```

## Aggregation Benefits

### Performance Impact
```
Without Aggregations:
- Query scans 1 billion rows
- Response time: 30-60 seconds

With Aggregations:
- Query uses 10 million row aggregation
- Response time: 0.5-2 seconds

Performance Improvement: 15-100x faster
```

### Storage Trade-off
```
Fact Table Size: 100 GB
Aggregations: 5-15 GB (5-15% overhead)
Total Storage: 105-115 GB
Query Performance: 10-50x improvement
```

## Aggregation Design Goals

1. **Maximize hit rate**: Percentage of queries using aggregations
2. **Minimize storage**: Balance performance vs disk space
3. **Optimize processing time**: Consider build/refresh duration
4. **Target common queries**: Focus on frequent user patterns

## Aggregation Selection Strategies

### 1. Usage-Based Design
Analyze actual query logs to identify patterns:

```sql
-- Query log analysis
SELECT
    DimensionUsage,
    COUNT(*) as QueryCount,
    AVG(Duration) as AvgDuration
FROM QueryLog
WHERE Date >= DATEADD(day, -30, GETDATE())
GROUP BY DimensionUsage
ORDER BY QueryCount DESC
```

Common patterns:
```
Most Frequent Queries:
1. Product × Date (45% of queries)
2. Customer × Date (25% of queries)
3. Store × Date (15% of queries)
4. Product × Store (10% of queries)
5. Customer × Product (5% of queries)
```

### 2. Size-Based Design
Favor smaller aggregations that provide broad coverage:

```
Aggregation Candidates:
├── Date only: 365 rows ★★★★★ (Build this!)
├── Product: 10,000 rows ★★★★★
├── Customer: 500,000 rows ★★★
├── Product × Date: 3.6M rows ★★★
└── Customer × Product: 5B rows ★ (Too large!)
```

### 3. Performance Target Design
Start with performance requirements and work backward:

```
Target: 95% of queries < 2 seconds

Test Scenarios:
1. Top Products by Month → 1.2s ✓
2. Customer Sales YTD → 3.5s ✗ (needs aggregation)
3. Store Performance → 0.8s ✓
4. Product Trends → 1.5s ✓

Design aggregation: Customer × Date × Region
Result: Customer Sales YTD → 1.1s ✓
```

### 4. Dimension Granularity
Higher levels in hierarchies create smaller, faster aggregations:

```
Date Hierarchy:
├── Year: 5 rows (fastest)
├── Quarter: 20 rows
├── Month: 60 rows
├── Week: 260 rows
└── Day: 1,825 rows (slowest)

Product Hierarchy:
├── Category: 10 rows (fastest)
├── Subcategory: 50 rows
├── Brand: 200 rows
└── Product: 10,000 rows (slowest)

Optimal Aggregation:
Product[Category] × Date[Month]
= 10 × 60 = 600 rows (very fast!)
```

## Aggregation Design Patterns

### Pattern 1: Dimension Reduction
Remove low-value dimensions from aggregations:

```
Full Grain: Product × Customer × Date × Store × Promotion
Too many combinations!

Aggregation 1: Product × Date
Aggregation 2: Customer × Date
Aggregation 3: Store × Date
Aggregation 4: Promotion × Date

Each removes 3-4 dimensions = much smaller
```

### Pattern 2: Hierarchical Rollup
Pre-aggregate at higher hierarchy levels:

```
Detail Level:
Product[SKU] × Date[Day] × Store[StoreID]
= 10,000 × 1,825 × 500 = 9.1 billion

Category Level:
Product[Category] × Date[Month] × Store[Region]
= 10 × 60 × 5 = 3,000 (99.99% smaller!)
```

### Pattern 3: Time-Based Strategy
Aggregate historical data more aggressively:

```
Current Month (June 2024):
└── Daily detail, minimal aggregations

Last 6 Months (Jan-May 2024):
└── Daily detail + Weekly aggregations

Last Year (2023):
└── Weekly aggregations + Monthly summaries

Prior Years (2022 and earlier):
└── Monthly and Quarterly aggregations only
```

### Pattern 4: Hot Path Optimization
Aggressive aggregation for most-used query paths:

```
80/20 Rule Application:
- 80% of queries use Product × Date
- Build comprehensive aggregations here
- Minimal aggregations for rare patterns

Product × Date Aggregations:
├── Product[Category] × Date[Month]
├── Product[Subcategory] × Date[Month]
├── Product[Product] × Date[Quarter]
└── Product[Category] × Date[Day]
```

## Aggregation Design Process

### Step 1: Gather Requirements
```
Questions to Answer:
1. What are the most common queries?
2. What response time is acceptable?
3. How much storage is available?
4. How often does data change?
5. What are the dimension cardinalities?
```

### Step 2: Analyze Query Patterns
```
Query Pattern Analysis:
├── Frequency by dimension combination
├── Average duration per pattern
├── Peak usage times
├── User groups and their patterns
└── Seasonal variations
```

### Step 3: Calculate Aggregation Sizes
```
Formula:
Aggregation Size =
    Dim1_Cardinality × Dim2_Cardinality × ... × Record_Size

Example:
Product[Category] × Date[Month] × Store[Region]
= 10 × 60 × 5 × 100 bytes
= 30,000 × 100 bytes
= 3 MB
```

### Step 4: Prioritize Aggregations
```
Priority Score = (Query_Frequency × Performance_Gain) / Storage_Cost

Example:
Aggregation A: (1000 queries × 20s gain) / 100MB = 200
Aggregation B: (100 queries × 50s gain) / 500MB = 10
Aggregation C: (5000 queries × 5s gain) / 50MB = 500

Build Order: C, A, B
```

### Step 5: Implement and Test
```
Implementation Checklist:
□ Create aggregation definitions
□ Build aggregations
□ Measure storage impact
□ Test query performance
□ Validate hit rates
□ Monitor processing time
□ Adjust based on results
```

## SSAS Aggregation Design

### Usage-Based Optimization
```xml
<AggregationDesign>
  <ID>SalesAggregation</ID>
  <Aggregations>
    <Aggregation>
      <ID>Agg_Product_Date</ID>
      <Dimensions>
        <Dimension>
          <CubeDimensionID>Product</CubeDimensionID>
          <Attributes>
            <Attribute>
              <AttributeID>Category</AttributeID>
            </Attribute>
          </Attributes>
        </Dimension>
        <Dimension>
          <CubeDimensionID>Date</CubeDimensionID>
          <Attributes>
            <Attribute>
              <AttributeID>Month</AttributeID>
            </Attribute>
          </Attributes>
        </Dimension>
      </Dimensions>
    </Aggregation>
  </Aggregations>
</AggregationDesign>
```

### Automated Design (Analysis Services)
```
Design Aggregations Wizard Options:

1. Storage Size Target:
   - Until storage reaches X GB/MB

2. Performance Gain:
   - Until performance gain < X%

3. Click Stop:
   - Manual control over process

Typical Settings:
- Performance Gain: 30-40%
- Storage: 10-20% of fact table size
```

## Power BI Aggregations

### User-Defined Aggregations
```
Aggregation Table: Sales_Agg_Monthly

Columns:
- Product_Category
- Date_Month
- Total_Sales (SUM)
- Transaction_Count (COUNT)
- Avg_Price (AVERAGE)

Aggregation Mapping:
Detail Table: Sales
Aggregation Table: Sales_Agg_Monthly
Precedence: Aggregation first

Query Rewrite:
User Query: SUM(Sales[Amount]) by Month
Rewritten: Use Sales_Agg_Monthly
Performance: 10-100x faster
```

### Composite Model Aggregations
```dax
// Import aggregation table
Sales_Agg_Monthly (Import Mode)
- Category
- Month
- SalesAmount

// DirectQuery detail table
Sales (DirectQuery Mode)
- All detail fields

// Automatic aggregation usage
Total Sales = SUM(Sales[Amount])
// Automatically uses Sales_Agg_Monthly when possible
```

## Aggregation Maintenance

### Processing Strategies
```
Full Process:
- Rebuild all aggregations
- Use for: Major changes
- Duration: Hours
- Frequency: Weekly/Monthly

Incremental Process:
- Add new data only
- Use for: Regular updates
- Duration: Minutes/Hours
- Frequency: Daily/Hourly

Process Update:
- Refresh dimension changes
- Use for: Dimension updates
- Duration: Minutes
- Frequency: As needed
```

### Monitoring and Tuning
```sql
-- Check aggregation usage (SSAS DMV)
SELECT
    AGGREGATION_NAME,
    AGGREGATION_SIZE,
    ROWS,
    USED_COUNT,
    LAST_USED,
    AVG_QUERY_TIME
FROM $SYSTEM.DISCOVER_PARTITION_STAT
WHERE USED_COUNT > 0
ORDER BY USED_COUNT DESC

-- Low usage aggregations are candidates for removal
```

## Performance Metrics

### Hit Rate
```
Aggregation Hit Rate =
    (Queries Using Aggregations / Total Queries) × 100

Target: 70-90% hit rate

Example:
1000 queries/day
750 use aggregations
Hit Rate = 75% ✓
```

### Storage Efficiency
```
Storage Efficiency = Performance Gain / Storage Cost

Good: > 10 (10x speedup per GB storage)
Fair: 5-10
Poor: < 5 (consider removing)
```

### Query Performance Distribution
```
Target Distribution:
< 1 second:   70% of queries
1-3 seconds:  20% of queries
3-5 seconds:  8% of queries
> 5 seconds:  2% of queries
```

## Best Practices

1. **Start Conservative**: Begin with 10-20% storage budget
2. **Monitor Usage**: Track which aggregations are actually used
3. **Favor Smaller**: Many small aggregations > few large ones
4. **Test Thoroughly**: Validate with real query workload
5. **Document Decisions**: Explain why each aggregation exists
6. **Regular Review**: Remove unused aggregations
7. **Automate Monitoring**: Set up alerts for performance degradation
8. **Partition Strategy**: Align aggregations with partitions

## Common Pitfalls

- Over-aggregating: Too much storage with minimal benefit
- Under-aggregating: Poor query performance
- Ignoring usage patterns: Building wrong aggregations
- No monitoring: Not knowing what works
- Static design: Not adapting to changing patterns
- Missing hot paths: Not optimizing common queries
- Poor hierarchy design: Can't leverage aggregations effectively
- Neglecting maintenance: Stale or inefficient aggregations

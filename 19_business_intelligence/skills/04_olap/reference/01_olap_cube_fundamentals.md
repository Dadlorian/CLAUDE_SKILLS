# OLAP Cube Fundamentals

## Overview

OLAP (Online Analytical Processing) cubes are multidimensional data structures optimized for fast analytical queries and complex calculations across business data.

## Core Components

### 1. Measures (Facts)
Numeric values that can be aggregated:
- **Additive**: Sum across all dimensions (e.g., Sales Amount, Quantity)
- **Semi-Additive**: Sum across some dimensions (e.g., Account Balance - not time)
- **Non-Additive**: Cannot be summed (e.g., Ratios, Percentages, Distinct Count)

```
Examples:
- Sales Amount (Additive)
- Inventory Level (Semi-Additive - not across time)
- Unit Price (Non-Additive)
- Profit Margin % (Non-Additive)
- Customer Count (Distinct Count)
```

### 2. Dimensions
Business perspectives for analyzing measures:
- **Time**: Year, Quarter, Month, Day
- **Geography**: Country, State, City
- **Product**: Category, Subcategory, Product
- **Customer**: Segment, Region, Account

### 3. Dimension Attributes
Properties that describe dimension members:
- **Key Attributes**: Unique identifiers
- **Name Attributes**: Display names
- **Descriptive Attributes**: Additional properties (Color, Size, Status)

## Cube Architecture

### Multidimensional Model
```
                    Time
                     |
                     |
Product -------- [Measures] -------- Customer
                     |
                     |
                  Geography
```

### Data Cell
Each intersection of dimension members contains measure values:
```
Cube Cell = Product[Laptop] × Time[2024-Q1] × Geography[USA]
  Sales Amount = $1,250,000
  Quantity = 450
  Avg Price = $2,777.78
```

## Cube Operations

### 1. Slicing
Selecting a single value from one dimension:
```
Time = '2024' (reduces cube by one dimension)
Result: 3D → 2D cube
```

### 2. Dicing
Selecting specific values from multiple dimensions:
```
Time IN ('2024-Q1', '2024-Q2')
Product IN ('Laptops', 'Tablets')
Geography = 'USA'
Result: Subcube
```

### 3. Drilling
- **Drill Down**: Move from summary to detail (Year → Quarter → Month)
- **Drill Up**: Move from detail to summary (Month → Quarter → Year)
- **Drill Through**: Access underlying detail records

### 4. Pivoting (Rotation)
Reorient the cube to view different perspectives:
```
Original: Rows=Product, Columns=Time
Pivoted:  Rows=Time, Columns=Product
```

### 5. Roll-Up
Aggregate data along a dimension hierarchy:
```
City → State → Country → All
```

## Aggregation Levels

### Grain Definition
The lowest level of detail stored in the cube:
- **Transaction Level**: Individual sales transactions
- **Daily Level**: Aggregated by day
- **Monthly Level**: Pre-aggregated monthly summaries

### Aggregation Hierarchy
```
All Products (Level 0)
└── Category (Level 1)
    └── Subcategory (Level 2)
        └── Product (Level 3)
```

## Cube Design Patterns

### 1. Star Schema Foundation
```
Fact Table (Center)
- DateKey (FK)
- ProductKey (FK)
- CustomerKey (FK)
- GeographyKey (FK)
- SalesAmount
- Quantity

Dimension Tables (Points)
- DimDate
- DimProduct
- DimCustomer
- DimGeography
```

### 2. Slowly Changing Dimensions
- **Type 1**: Overwrite (no history)
- **Type 2**: Add new row (full history)
- **Type 3**: Add new column (limited history)

### 3. Role-Playing Dimensions
Single dimension used multiple times:
```
Date dimension as:
- Order Date
- Ship Date
- Delivery Date
```

## Measure Groups

Logical grouping of related measures:
```
Sales Measure Group:
- Sales Amount
- Sales Quantity
- Sales Cost
- Gross Profit

Inventory Measure Group:
- Stock Level
- Reorder Point
- Stock Value
```

## Calculated Measures

Derived values computed at query time:
```
Gross Profit = Sales Amount - Sales Cost
Profit Margin % = (Gross Profit / Sales Amount) × 100
YoY Growth % = ((Current Year - Prior Year) / Prior Year) × 100
```

## Dimensionality Considerations

### Sparse vs Dense Data
- **Dense**: Most dimension combinations have data (Time × Product)
- **Sparse**: Few combinations have data (Customer × Product)

### Optimization Strategies
- Use aggregations for frequently queried combinations
- Implement partitioning for large fact tables
- Design appropriate hierarchies
- Choose optimal storage mode (MOLAP/ROLAP/HOLAP)

## Performance Characteristics

### Query Speed Factors
1. **Aggregation Design**: Pre-computed summaries
2. **Partition Strategy**: Divide large fact tables
3. **Index Optimization**: Dimension attributes
4. **Storage Mode**: MOLAP (fastest) vs ROLAP (real-time)
5. **Cache Configuration**: Memory allocation

### Typical Response Times
- **Interactive Queries**: < 1 second
- **Complex Calculations**: 1-5 seconds
- **Large Data Scans**: 5-30 seconds

## Best Practices

1. **Design for Queries**: Understand user query patterns
2. **Grain Selection**: Choose appropriate detail level
3. **Hierarchy Design**: Logical business hierarchies
4. **Aggregation Strategy**: Balance storage and performance
5. **Partition Large Facts**: Manage data volumes
6. **Attribute Relationships**: Define for query optimization
7. **Test at Scale**: Validate with production data volumes

## Common Pitfalls

- Over-aggregating and losing needed detail
- Under-aggregating and poor query performance
- Incorrect grain selection
- Missing attribute relationships
- Poor hierarchy design
- Inadequate partitioning strategy
- Insufficient testing with production volumes

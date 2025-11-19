# Aggregation Optimization Guide

## Understanding Aggregations

Aggregations are pre-calculated summaries that dramatically improve query performance by reducing the amount of data scanned.

## Aggregation Design Process

### Step 1: Analyze Query Patterns

Capture and analyze actual queries:

```sql
-- Review query log
SELECT
    QueryText,
    COUNT(*) as ExecutionCount,
    AVG(Duration) as AvgDuration
FROM QueryLog
GROUP BY QueryText
ORDER BY ExecutionCount DESC
```

Common patterns:
- Product by Month (45% of queries)
- Customer by Region (25% of queries)
- Category by Quarter (15% of queries)

### Step 2: Design Aggregations

Use Analysis Services Aggregation Design Wizard:

1. Set performance goal (typically 30-40%)
2. Review estimated usage
3. Deploy and test

Or use PowerShell:

```powershell
$server = New-Object Microsoft.AnalysisServices.Server
$server.Connect("localhost")

$db = $server.Databases["SalesCube"]
$cube = $db.Cubes["Sales"]
$mg = $cube.MeasureGroups["Sales"]

# Design aggregations
$aggDesign = $mg.AggregationDesigns.Add("OptimizedAggs")

$aggDesign.DesignAggregations(
    0,      # Storage optimization (0 = performance)
    35,     # Target 35% performance gain
    $null   # Use query log
)

$aggDesign.Update()
$server.Disconnect()
```

### Step 3: Monitor Effectiveness

```sql
-- Check aggregation usage
SELECT
    PARTITION_NAME,
    AGGREGATION_NAME,
    USED_COUNT,
    ROWS,
    CREATED_TIME,
    LAST_USED
FROM $SYSTEM.DISCOVER_PARTITION_STAT
WHERE AGGREGATION_NAME IS NOT NULL
ORDER BY USED_COUNT DESC
```

## Manual Aggregation Design

For specific needs, create aggregations manually:

```xml
<Aggregation>
  <ID>Agg_Product_Date</ID>
  <Name>Product Category by Month</Name>
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
```

## Power BI Aggregations

### Create Aggregation Table

```powerquery
// Aggregated monthly sales
let
    Source = Sales,
    GroupedRows = Table.Group(
        Source,
        {"ProductCategory", "MonthYear"},
        {
            {"TotalSales", each List.Sum([SalesAmount]), type number},
            {"TotalQuantity", each List.Sum([Quantity]), type number},
            {"TransactionCount", each Table.RowCount(_), type number}
        }
    )
in
    GroupedRows
```

### Configure Aggregation

In Power BI Desktop:
1. Create detail table (DirectQuery)
2. Create aggregation table (Import)
3. Configure aggregation relationships
4. Set up aggregation mapping

## Best Practices

1. **Start Conservative**
   - 10-20% of fact table size
   - Focus on most common queries

2. **Monitor Usage**
   - Track hit rates
   - Remove unused aggregations

3. **Balance Storage vs Performance**
   - Target 30-40% performance gain
   - Monitor disk usage

4. **Regular Review**
   - Query patterns change
   - Adjust aggregations quarterly

5. **Test Thoroughly**
   - Verify query results
   - Measure performance improvement
   - Test with production volumes

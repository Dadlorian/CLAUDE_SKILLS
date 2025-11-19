# Cube Partitioning Strategies

## Overview

Partitioning divides large fact tables and cube structures into smaller, manageable segments to improve processing performance, query performance, and manageability.

## Why Partition?

### Benefits
1. **Faster Processing**: Process only changed partitions
2. **Improved Query Performance**: Query only relevant partitions
3. **Better Manageability**: Archive or delete old data easily
4. **Parallel Processing**: Process multiple partitions simultaneously
5. **Storage Optimization**: Different storage modes per partition

### When to Partition
```
Recommended:
- Fact table > 10 million rows
- Daily data volume > 100,000 rows
- Multiple years of historical data
- Need for incremental processing

Consider:
- Fact table 1-10 million rows
- Weekly/monthly data loads
- 1-2 years of history

Not Needed:
- Fact table < 1 million rows
- Complete refresh acceptable
- Limited historical data
```

## Partitioning Strategies

### 1. Time-Based Partitioning (Most Common)

#### Monthly Partitions
```
Partition Structure:
├── FactSales_2024_01 (January 2024)
├── FactSales_2024_02 (February 2024)
├── FactSales_2024_03 (March 2024)
...
└── FactSales_2024_12 (December 2024)

Benefits:
- Aligns with business reporting cycles
- Easy to understand and manage
- Balanced partition sizes
- Supports monthly processing

Query Example:
WHERE DateKey BETWEEN 20240101 AND 20240131
→ Scans only FactSales_2024_01
```

#### Quarterly Partitions
```
Partition Structure:
├── FactSales_2024_Q1
├── FactSales_2024_Q2
├── FactSales_2024_Q3
└── FactSales_2024_Q4

Use When:
- Lower data volumes
- Quarterly business cycles
- Longer processing windows acceptable
```

#### Yearly Partitions
```
Partition Structure:
├── FactSales_2022
├── FactSales_2023
└── FactSales_2024

Use When:
- Small to medium data volumes
- Long-term historical analysis
- Simple partition management
```

#### Rolling Window
```
Partition Structure:
├── FactSales_Current (Last 30 days) - ROLAP
├── FactSales_Recent (31-90 days) - MOLAP, daily grain
├── FactSales_2024_Q1 - MOLAP, aggregated
├── FactSales_2024_Q2 - MOLAP, aggregated
└── FactSales_Historical (pre-2024) - HOLAP, heavily aggregated

Benefits:
- Optimizes for access patterns
- Recent data most detailed
- Historical data summarized
- Mixed storage modes
```

### 2. Dimension-Based Partitioning

#### Geography Partitioning
```
Partition Structure:
├── FactSales_Americas
├── FactSales_EMEA
├── FactSales_APAC
└── FactSales_Other

Use When:
- Regional data sovereignty requirements
- Geographically distributed queries
- Regional processing schedules
- Load balanced across regions
```

#### Product Category Partitioning
```
Partition Structure:
├── FactSales_Electronics
├── FactSales_Clothing
├── FactSales_Home
└── FactSales_Other

Use When:
- Distinct product line analysis
- Different processing requirements by category
- Product-specific query patterns
```

### 3. Hybrid Partitioning

#### Time + Geography
```
Partition Structure:
├── FactSales_2024_01_US
├── FactSales_2024_01_EMEA
├── FactSales_2024_01_APAC
├── FactSales_2024_02_US
├── FactSales_2024_02_EMEA
└── FactSales_2024_02_APAC

Benefits:
- Fine-grained control
- Regional processing
- Timezone-aligned processing

Drawbacks:
- Many partitions to manage
- Complex processing logic
- Higher maintenance overhead
```

## SSAS Partition Implementation

### Partition Definition (XML)

```xml
<MeasureGroup>
  <ID>Sales</ID>
  <Partitions>
    <Partition>
      <ID>Sales_2024_01</ID>
      <Name>Sales January 2024</Name>
      <Source>
        <DataSourceViewID>SalesDSV</DataSourceViewID>
        <QueryDefinition>
          <![CDATA[
            SELECT *
            FROM FactSales
            WHERE DateKey >= 20240101 AND DateKey < 20240201
          ]]>
        </QueryDefinition>
      </Source>
      <StorageMode>Molap</StorageMode>
      <ProcessingMode>Regular</ProcessingMode>
      <AggregationDesignID>SalesAggregation</AggregationDesignID>
      <ProactiveCaching>
        <OnlineMode>OnCacheComplete</OnlineMode>
      </ProactiveCaching>
    </Partition>

    <Partition>
      <ID>Sales_2024_02</ID>
      <Name>Sales February 2024</Name>
      <Source>
        <DataSourceViewID>SalesDSV</DataSourceViewID>
        <QueryDefinition>
          <![CDATA[
            SELECT *
            FROM FactSales
            WHERE DateKey >= 20240201 AND DateKey < 20240301
          ]]>
        </QueryDefinition>
      </Source>
      <StorageMode>Molap</StorageMode>
    </Partition>
  </Partitions>
</MeasureGroup>
```

### Creating Partitions with TMSL (Tabular Model)

```json
{
  "create": {
    "parentObject": {
      "database": "SalesCube",
      "table": "Sales"
    },
    "partition": {
      "name": "Sales_2024_01",
      "source": {
        "type": "query",
        "query": "SELECT * FROM FactSales WHERE DateKey >= 20240101 AND DateKey < 20240201",
        "dataSource": "SalesDB"
      },
      "mode": "import"
    }
  }
}
```

### Creating Partitions with PowerShell

```powershell
# Load AMO assembly
[System.Reflection.Assembly]::LoadWithPartialName("Microsoft.AnalysisServices")

# Connect to server
$server = New-Object Microsoft.AnalysisServices.Server
$server.Connect("localhost")

# Get database and measure group
$db = $server.Databases["SalesCube"]
$cube = $db.Cubes["Sales"]
$mg = $cube.MeasureGroups["Sales"]

# Create new partition
$partition = New-Object Microsoft.AnalysisServices.Partition
$partition.Name = "Sales_2024_03"
$partition.ID = "Sales_2024_03"
$partition.StorageMode = [Microsoft.AnalysisServices.StorageMode]::Molap

# Set query binding
$queryBinding = New-Object Microsoft.AnalysisServices.QueryBinding
$queryBinding.DataSourceID = "SalesDB"
$queryBinding.QueryDefinition = @"
    SELECT *
    FROM FactSales
    WHERE DateKey >= 20240301 AND DateKey < 20240401
"@
$partition.Source = $queryBinding

# Add to measure group
$mg.Partitions.Add($partition)

# Update to server
$partition.Update()
$server.Disconnect()

Write-Host "Partition created successfully"
```

## Partition Processing Strategies

### Full Process All
```powershell
# Process all partitions completely
$server = New-Object Microsoft.AnalysisServices.Server
$server.Connect("localhost")

$db = $server.Databases["SalesCube"]
$cube = $db.Cubes["Sales"]
$mg = $cube.MeasureGroups["Sales"]

foreach ($partition in $mg.Partitions) {
    Write-Host "Processing partition: $($partition.Name)"
    $partition.Process([Microsoft.AnalysisServices.ProcessType]::ProcessFull)
}

$server.Disconnect()
```

### Incremental Process
```powershell
# Process only new/changed data
$partition = $mg.Partitions["Sales_Current"]

# Define incremental query
$queryBinding = New-Object Microsoft.AnalysisServices.QueryBinding
$queryBinding.DataSourceID = "SalesDB"
$queryBinding.QueryDefinition = @"
    SELECT *
    FROM FactSales
    WHERE DateKey >= CONVERT(VARCHAR(8), GETDATE(), 112)
    AND LoadedDate > '$($lastProcessDate)'
"@

$partition.Process([Microsoft.AnalysisServices.ProcessType]::ProcessAdd, $queryBinding)
```

### Parallel Processing
```powershell
# Process multiple partitions in parallel
$jobs = @()

foreach ($partition in $mg.Partitions) {
    $scriptBlock = {
        param($serverName, $dbName, $cubeName, $mgName, $partitionName)

        [System.Reflection.Assembly]::LoadWithPartialName("Microsoft.AnalysisServices")
        $srv = New-Object Microsoft.AnalysisServices.Server
        $srv.Connect($serverName)

        $partition = $srv.Databases[$dbName].Cubes[$cubeName].MeasureGroups[$mgName].Partitions[$partitionName]
        $partition.Process([Microsoft.AnalysisServices.ProcessType]::ProcessFull)

        $srv.Disconnect()
    }

    $jobs += Start-Job -ScriptBlock $scriptBlock -ArgumentList "localhost", "SalesCube", "Sales", "Sales", $partition.Name
}

# Wait for all jobs to complete
$jobs | Wait-Job | Receive-Job
$jobs | Remove-Job
```

## Partition Merge Strategy

### Merge Old Partitions
```powershell
# Merge monthly partitions into quarterly
$q1Partition = $mg.Partitions["Sales_2024_Q1"]

# Merge January, February, March into Q1
$partitionsToMerge = @(
    $mg.Partitions["Sales_2024_01"],
    $mg.Partitions["Sales_2024_02"],
    $mg.Partitions["Sales_2024_03"]
)

$q1Partition.Merge($partitionsToMerge)
$q1Partition.Update()

# Remove old partitions
foreach ($partition in $partitionsToMerge) {
    $mg.Partitions.Remove($partition)
}

$mg.Update()
```

## Partition Sizing Guidelines

### Optimal Partition Size
```
Rows per Partition:
- Minimum: 1 million rows
- Optimal: 10-50 million rows
- Maximum: 100 million rows
- Too large: > 100 million rows (consider splitting)

Storage per Partition:
- Target: 500 MB - 2 GB (compressed)
- Warning: > 5 GB
- Action required: > 10 GB

Processing Time:
- Target: < 5 minutes per partition
- Acceptable: 5-15 minutes
- Review: 15-30 minutes
- Redesign: > 30 minutes
```

### Partition Count Guidelines
```
Cube Size          | Recommended Partitions
-------------------|----------------------
< 10 GB            | 1-5 partitions
10-50 GB           | 5-20 partitions
50-200 GB          | 20-50 partitions
200-500 GB         | 50-100 partitions
> 500 GB           | 100-200 partitions

Too many partitions (>200):
- Management overhead
- Metadata bloat
- Slower queries (partition elimination overhead)
```

## Partition Elimination

### How It Works
```
Query:
SELECT SUM(SalesAmount)
FROM FactSales
WHERE DateKey BETWEEN 20240201 AND 20240229

Partition Scan:
✓ Sales_2024_02 (scanned)
✗ Sales_2024_01 (skipped)
✗ Sales_2024_03 (skipped)

Result: 66% reduction in data scanned
```

### Ensuring Partition Elimination
```xml
<!-- Define partition slice -->
<Partition>
  <ID>Sales_2024_01</ID>
  <Slice>
    <![CDATA[
      [Date].[Date].&[20240101]:[Date].[Date].&[20240131]
    ]]>
  </Slice>
</Partition>
```

## Power BI Incremental Refresh

### Configuration
```powerquery
// In Power Query, define RangeStart and RangeEnd parameters
let
    Source = Sql.Database("server", "database"),
    FilteredRows = Table.SelectRows(
        Source,
        each [OrderDate] >= RangeStart and [OrderDate] < RangeEnd
    )
in
    FilteredRows
```

### Incremental Refresh Policy
```json
{
  "table": "Sales",
  "incrementalRefreshPolicy": {
    "mode": "Import",
    "rollingWindowGranularity": "Month",
    "rollingWindowPeriods": 24,
    "incrementalGranularity": "Day",
    "incrementalPeriods": 7,
    "pollingExpression": "DateTime.LocalNow()"
  }
}
```

Result:
```
Partitions Created:
├── Sales_2022_07 (Historical - full)
├── Sales_2022_08 (Historical - full)
...
├── Sales_2024_04 (Historical - full)
├── Sales_2024_05_01-07 (Incremental - daily refresh)
├── Sales_2024_05_08-14 (Incremental - daily refresh)
└── Sales_2024_05_15-21 (Incremental - daily refresh)
```

## Best Practices

### 1. Partition Naming
```
✓ Descriptive and consistent
Examples:
- Sales_2024_01
- Sales_2024_Q1
- Sales_US_2024_01
- Sales_Current

✗ Avoid:
- Partition1
- Part_Jan
- Sales_1
```

### 2. Partition Alignment
```
✓ Align with business processes
- Monthly close cycle → Monthly partitions
- Weekly data loads → Weekly partitions
- Quarterly reporting → Quarterly partitions

✓ Align with query patterns
- Year-to-date queries → Align with calendar
- Fiscal reporting → Align with fiscal calendar
```

### 3. Storage Mode Strategy
```
Recent Data:
├── Current Month: ROLAP (real-time)
└── Last 3 Months: MOLAP (daily refresh)

Historical Data:
├── Last Year: MOLAP (weekly/monthly refresh)
└── Prior Years: HOLAP (archived, rarely updated)
```

### 4. Processing Schedule
```
Daily:
- Process current day partition
- Incremental update to current month

Weekly:
- Full process of current month
- Validate recent months

Monthly:
- Process previous month (full)
- Merge/archive old partitions
- Optimize aggregations
```

### 5. Monitoring and Maintenance
```sql
-- Monitor partition sizes
SELECT
    PARTITION_NAME,
    ROWS,
    PARTITION_SIZE_MB,
    LAST_PROCESSED,
    PROCESSING_STATE
FROM $SYSTEM.DISCOVER_PARTITION_STAT
ORDER BY PARTITION_SIZE_MB DESC;

-- Identify slow-processing partitions
SELECT
    PARTITION_NAME,
    PROCESSING_DURATION_MS,
    ROWS_PROCESSED,
    ROWS_PROCESSED / (PROCESSING_DURATION_MS / 1000.0) AS ROWS_PER_SECOND
FROM ProcessingLog
WHERE PROCESSING_DURATION_MS > 300000; -- > 5 minutes
```

## Common Issues and Solutions

### Issue: Partition Bloat
```
Problem: Partitions growing too large
Solution:
1. Split large partitions
2. Archive old data
3. Implement data retention policy
4. Review aggregation strategy
```

### Issue: Too Many Partitions
```
Problem: Hundreds of small partitions
Solution:
1. Merge older partitions
2. Use larger time grain (monthly vs daily)
3. Implement rolling window
4. Archive historical partitions
```

### Issue: Slow Partition Processing
```
Problem: Processing takes too long
Solution:
1. Optimize source query
2. Add indexes to fact table
3. Process in parallel
4. Use ProcessAdd for incremental
5. Review aggregation design
```

### Issue: Partition Elimination Not Working
```
Problem: Query scans all partitions
Solution:
1. Define partition slices
2. Ensure query predicates match partition scheme
3. Use dimension keys in WHERE clause
4. Check query execution plan
```

## Testing and Validation

### Validation Checklist
```
□ All partitions process successfully
□ Data completeness (no missing ranges)
□ No overlapping data between partitions
□ Partition elimination working
□ Query performance improved
□ Processing time acceptable
□ Storage size as expected
□ Aggregations built correctly
□ MDX/DAX queries return correct results
```

### Test Queries
```mdx
-- Verify partition elimination
WITH MEMBER [Measures].[Partition Count] AS
    [System].[Partitions].COUNT

SELECT
    [Measures].[Sales Amount],
    [Measures].[Partition Count] ON 0
FROM [Sales]
WHERE [Date].[2024].[January]

-- Should show fewer partitions scanned
```

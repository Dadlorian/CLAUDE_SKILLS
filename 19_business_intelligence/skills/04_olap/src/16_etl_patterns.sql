-- ETL Patterns for OLAP Loading
-- Production-ready data loading patterns

-- Type 2 SCD Update Pattern
MERGE DimProduct AS target
USING (
    SELECT
        ProductID,
        ProductName,
        Category,
        Subcategory,
        ListPrice,
        GETDATE() AS EffectiveDate
    FROM SourceProducts
) AS source
ON target.ProductID = source.ProductID
    AND target.IsCurrent = 1

-- Update existing record (close it)
WHEN MATCHED AND (
    target.ProductName <> source.ProductName OR
    target.Category <> source.Category OR
    target.ListPrice <> source.ListPrice
) THEN UPDATE SET
    target.IsCurrent = 0,
    target.EndDate = source.EffectiveDate

-- Handle new records
WHEN NOT MATCHED BY TARGET THEN
    INSERT (ProductID, ProductName, Category, Subcategory, ListPrice, StartDate, EndDate, IsCurrent)
    VALUES (source.ProductID, source.ProductName, source.Category, source.Subcategory, 
            source.ListPrice, source.EffectiveDate, '9999-12-31', 1);

-- Insert new version for changed records
INSERT INTO DimProduct (ProductID, ProductName, Category, Subcategory, ListPrice, StartDate, EndDate, IsCurrent)
SELECT
    s.ProductID,
    s.ProductName,
    s.Category,
    s.Subcategory,
    s.ListPrice,
    s.EffectiveDate,
    '9999-12-31',
    1
FROM SourceProducts s
INNER JOIN DimProduct d ON s.ProductID = d.ProductID
WHERE d.IsCurrent = 0
    AND d.EndDate = s.EffectiveDate;

-- Fact Table Incremental Load
INSERT INTO FactSales (DateKey, ProductKey, CustomerKey, SalesAmount, Quantity, Cost)
SELECT
    CONVERT(INT, FORMAT(s.OrderDate, 'yyyyMMdd')) AS DateKey,
    COALESCE(p.ProductKey, -1) AS ProductKey,
    COALESCE(c.CustomerKey, -1) AS CustomerKey,
    s.Amount AS SalesAmount,
    s.Quantity,
    s.Cost
FROM SourceSales s
LEFT JOIN DimProduct p ON s.ProductID = p.ProductID
    AND s.OrderDate >= p.StartDate
    AND s.OrderDate < p.EndDate
LEFT JOIN DimCustomer c ON s.CustomerID = c.CustomerID
    AND c.IsCurrent = 1
WHERE s.LoadDate > @LastLoadDate
    AND NOT EXISTS (
        SELECT 1
        FROM FactSales f
        WHERE f.OrderID = s.OrderID
            AND f.OrderLineNumber = s.LineNumber
    );

// Power Query M Code Snippets

// ============================================
// DATA CLEANING
// ============================================

// Remove duplicates
= Table.Distinct(Source, {"CustomerID"})

// Remove null rows
= Table.SelectRows(Source, each [Amount] <> null)

// Trim whitespace from all text columns
= Table.TransformColumns(Source,
    List.Transform(
        Table.ColumnsOfType(Source, {type text}),
        each {_, Text.Trim}
    )
)

// Replace null with zero
= Table.ReplaceValue(Source, null, 0, Replacer.ReplaceValue, {"Amount"})

// ============================================
// DATE OPERATIONS
// ============================================

// Add date parts
= Table.AddColumn(Source, "Year", each Date.Year([OrderDate]), Int64.Type)
= Table.AddColumn(#"Added Year", "Quarter", each Date.QuarterOfYear([OrderDate]), Int64.Type)
= Table.AddColumn(#"Added Quarter", "Month", each Date.Month([OrderDate]), Int64.Type)
= Table.AddColumn(#"Added Month", "DayOfWeek", each Date.DayOfWeek([OrderDate]), Int64.Type)

// Fiscal year (July 1 start)
= Table.AddColumn(Source, "Fiscal Year",
    each if Date.Month([OrderDate]) >= 7
         then Date.Year([OrderDate]) + 1
         else Date.Year([OrderDate]),
    Int64.Type)

// ============================================
// TRANSFORMATIONS
// ============================================

// Calculate new column
= Table.AddColumn(Source, "Revenue",
    each [Quantity] * [UnitPrice], type number)

// Conditional column
= Table.AddColumn(Source, "Segment",
    each if [Amount] > 1000 then "High Value"
         else if [Amount] > 100 then "Medium Value"
         else "Low Value",
    type text)

// Split column by delimiter
= Table.SplitColumn(Source, "FullName", Splitter.SplitTextByDelimiter(" "), {"FirstName", "LastName"})

// Merge columns
= Table.AddColumn(Source, "Full Address",
    each [Street] & ", " & [City] & ", " & [State], type text)

// ============================================
// AGGREGATIONS
// ============================================

// Group by and aggregate
= Table.Group(Source, {"CustomerID"}, {
    {"TotalSales", each List.Sum([Amount]), type number},
    {"OrderCount", each Table.RowCount(_), Int64.Type},
    {"AvgOrderValue", each List.Average([Amount]), type number},
    {"FirstOrderDate", each List.Min([OrderDate]), type date},
    {"LastOrderDate", each List.Max([OrderDate]), type date}
})

// ============================================
// QUERY FOLDING EXAMPLES
// ============================================

// Example that folds to database
let
    Source = Sql.Database("server", "database"),
    FilteredRows = Table.SelectRows(Source,
        each [OrderDate] >= #date(2024,1,1)),
    SelectedColumns = Table.SelectColumns(FilteredRows,
        {"OrderID", "CustomerID", "Amount"}),
    GroupedRows = Table.Group(SelectedColumns, {"CustomerID"},
        {{"Total", each List.Sum([Amount]), type number}})
in
    GroupedRows

// Check folding: Right-click each step → View Native Query
// If option is grayed out, folding broke

// ============================================
// CUSTOM FUNCTIONS
// ============================================

// Function to calculate days between dates
(StartDate as date, EndDate as date) as number =>
    Duration.Days(EndDate - StartDate)

// Function to categorize values
(Value as number) as text =>
    if Value >= 1000 then "High"
    else if Value >= 100 then "Medium"
    else "Low"

// ============================================
// ERROR HANDLING
// ============================================

// Try-catch pattern
= Table.AddColumn(Source, "SafeCalculation",
    each try [Amount] / [Quantity]
         otherwise 0, type number)

// Handle specific errors
= try Source otherwise Table.FromRecords({})

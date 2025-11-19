# Calculation Groups Guide (Tabular Models)

## Introduction

Calculation Groups enable reusable calculations across measures, reducing duplication and simplifying maintenance.

## Creating Calculation Groups

### Using Tabular Editor

1. Install Tabular Editor 2 or 3
2. Connect to model
3. Create Calculation Group:

```
Right-click Tables → Create → Calculation Group
Name: Time Intelligence
```

4. Add Calculation Items:

```dax
// Current Period
Current = SELECTEDMEASURE()

// Prior Year
PY = CALCULATE(SELECTEDMEASURE(), SAMEPERIODLASTYEAR('Date'[Date]))

// YoY Change
YoY Change = SELECTEDMEASURE() - [PY]

// YoY % Change
YoY % = DIVIDE([YoY Change], [PY], 0)

// YTD
YTD = CALCULATE(SELECTEDMEASURE(), DATESYTD('Date'[Date]))

// Prior Year YTD
PY YTD = CALCULATE([YTD], SAMEPERIODLASTYEAR('Date'[Date]))
```

## Precedence and Formatting

### Set Format String Expressions

```dax
// YoY % formatting
FORMAT_STRING = "0.0%"

// Dynamic formatting based on base measure
FORMAT_STRING =
VAR BaseMeasure = SELECTEDMEASUREFORMATSTRING()
VAR IsPercentage = CONTAINSSTRING(BaseMeasure, "%")
RETURN
    IF(IsPercentage, "0.0%", "#,##0")
```

### Precedence

Control calculation order:
- Higher precedence = calculated later
- Default = 0

```
Time Intelligence Group: Precedence = 10
Currency Conversion Group: Precedence = 20
```

## Common Calculation Group Patterns

### Time Intelligence
```dax
// MTD
MTD = CALCULATE(SELECTEDMEASURE(), DATESMTD('Date'[Date]))

// QTD
QTD = CALCULATE(SELECTEDMEASURE(), DATESQTD('Date'[Date]))

// Moving Annual Total
MAT =
CALCULATE(
    SELECTEDMEASURE(),
    DATESINPERIOD('Date'[Date], LASTDATE('Date'[Date]), -12, MONTH)
)
```

### Period Comparisons
```dax
// vs Prior Month
vs PM = SELECTEDMEASURE() - CALCULATE(SELECTEDMEASURE(), DATEADD('Date'[Date], -1, MONTH))

// vs Prior Quarter
vs PQ = SELECTEDMEASURE() - CALCULATE(SELECTEDMEASURE(), DATEADD('Date'[Date], -1, QUARTER))

// % Change vs PM
% vs PM = DIVIDE([vs PM], CALCULATE(SELECTEDMEASURE(), DATEADD('Date'[Date], -1, MONTH)), 0)
```

### Scenario Analysis
```dax
// Actual
Actual = SELECTEDMEASURE()

// Budget
Budget = CALCULATE(SELECTEDMEASURE(), Scenario[ScenarioName] = "Budget")

// Forecast
Forecast = CALCULATE(SELECTEDMEASURE(), Scenario[ScenarioName] = "Forecast")

// Variance
Variance = [Actual] - [Budget]

// Variance %
Variance % = DIVIDE([Variance], [Budget], 0)
```

## Using Calculation Groups

In report:
1. Add any measure to visual
2. Add Calculation Group field to visual
3. Calculation applies automatically

Example:
- Measure: Sales Amount
- Calculation Group: Time Intelligence
- Slicer selection: YoY %
- Result: Sales Amount YoY % displayed

## Best Practices

1. **Organization**
   - Group related calculations
   - Clear naming conventions
   - Document complex logic

2. **Performance**
   - Avoid circular dependencies
   - Test with large datasets
   - Monitor query performance

3. **User Experience**
   - Business-friendly names
   - Appropriate formatting
   - Tooltips/descriptions

4. **Maintenance**
   - Version control
   - Test after changes
   - Document dependencies

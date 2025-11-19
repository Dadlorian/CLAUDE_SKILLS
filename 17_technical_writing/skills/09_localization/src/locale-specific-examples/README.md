# Locale-Specific Formatting Examples

This directory contains comprehensive examples for handling date, number, and currency formatting across different locales and regions.

## Overview

Proper localization extends beyond translation to include correct formatting of:
- Dates and times
- Numbers and decimals
- Currencies
- Telephone numbers
- Postal codes
- Measurements (metric vs imperial)

## Locales Covered

1. **en-US** - United States (12-hour time, imperial)
2. **en-GB** - United Kingdom (24-hour time, metric)
3. **de-DE** - Germany (metric, comma separator)
4. **fr-FR** - France (metric, space separator)
5. **ja-JP** - Japan (metric, Japanese era dates)
6. **es-ES** - Spain (metric, European format)
7. **pt-BR** - Brazil (metric, unique date format)
8. **zh-CN** - China (metric, Chinese calendar)
9. **ar-SA** - Saudi Arabia (Islamic calendar, RTL)
10. **in-ID** - Indonesia (metric, local format)

## Key Formatting Differences

### Date Formats

| Locale | Format | Example |
|--------|--------|---------|
| en-US | MM/DD/YYYY | 11/19/2024 |
| en-GB | DD/MM/YYYY | 19/11/2024 |
| de-DE | DD.MM.YYYY | 19.11.2024 |
| fr-FR | DD/MM/YYYY | 19/11/2024 |
| ja-JP | YYYY年MM月DD日 | 2024年11月19日 |
| es-ES | DD/MM/YYYY | 19/11/2024 |
| pt-BR | DD/MM/YYYY | 19/11/2024 |
| zh-CN | YYYY年M月D日 | 2024年11月19日 |
| ar-SA | DD/MM/YYYY (Hijri) | 15/05/1446 |

### Number Formats

| Locale | Decimal | Thousand | Example |
|--------|---------|----------|---------|
| en-US | . | , | 1,234.56 |
| de-DE | , | . | 1.234,56 |
| fr-FR | , | (space) | 1 234,56 |
| ja-JP | . | , | 1,234.56 |
| es-ES | , | . | 1.234,56 |
| pt-BR | , | . | 1.234,56 |
| zh-CN | . | , | 1,234.56 |
| ar-SA | , | . | 1.234,56 |

### Currency Formats

| Locale | Format | Example |
|--------|--------|---------|
| en-US | $1,234.56 | Dollar (prefix) |
| en-GB | £1,234.56 | Pound (prefix) |
| de-DE | 1.234,56 € | Euro (suffix) |
| fr-FR | 1 234,56 € | Euro (suffix) |
| ja-JP | ¥1,234 | Yen (prefix) |
| es-ES | 1.234,56 € | Euro (suffix) |
| pt-BR | R$ 1.234,56 | Real (prefix) |
| zh-CN | ¥1,234.56 | Yuan (prefix) |
| ar-SA | ر.س. 1,234.56 | Riyal (suffix) |

## JavaScript Internationalization API

Modern JavaScript includes the `Intl` API for formatting:

```javascript
// Date formatting
const date = new Date();
new Intl.DateTimeFormat('en-US').format(date);
new Intl.DateTimeFormat('de-DE').format(date);

// Number formatting
new Intl.NumberFormat('en-US').format(1234.56);
new Intl.NumberFormat('de-DE').format(1234.56);

// Currency formatting
new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
}).format(1234.56);

new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR'
}).format(1234.56);
```

## Time Format Variations

### 12-hour vs 24-hour Time

**12-hour** (United States, Canada, Australia):
- 2:30 PM
- 8:45 AM

**24-hour** (Europe, Asia, Africa):
- 14:30
- 08:45

### Timezone Handling

Locales use different timezone notations:
- **EST/EDT** - Eastern US
- **GMT/BST** - United Kingdom
- **CET/CEST** - Central Europe
- **JST** - Japan Standard Time
- **CST** - China Standard Time

## Measurement Systems

### Metric Countries
- Most of world (EU, Asia, Africa)
- Uses: meters, kilograms, Celsius

### Imperial Countries
- United States, Liberia, Myanmar
- Uses: feet, pounds, Fahrenheit

### Mixed Systems
- United Kingdom: both metric and imperial
- Canada: metric with imperial in use

## Phone Number Formats

| Country | Format | Example |
|---------|--------|---------|
| US | (XXX) XXX-XXXX | (555) 123-4567 |
| UK | +44 XXXX XXXXXX | +44 1632 960001 |
| Germany | +49 XXX XXXXXX | +49 30 12345678 |
| France | +33 X XX XX XX XX | +33 1 23 45 67 89 |
| Japan | +81 XX-XXXX-XXXX | +81 90-1234-5678 |

## Postal Code Formats

| Country | Format | Example |
|---------|--------|---------|
| US | XXXXX or XXXXX-XXXX | 10001 or 10001-1234 |
| UK | Complex alphanumeric | SW1A 1AA |
| Germany | XXXXX | 10115 |
| France | XXXXX | 75001 |
| Canada | ANA NAN | K1A 0B1 |
| Japan | XXX-XXXX | 100-0001 |

## Week Numbering

**ISO Week** (Monday start, weeks 1-53):
- Europe, Asia, most of world
- Week 1 is first week with Thursday in it

**US Week** (Sunday start, weeks 0-52):
- United States
- Week 1 can start on January 1st

**China** (Sunday start):
- Similar to US but slight variations

## Language-Specific Considerations

### Pluralization Rules

English: singular/plural (1 file, 2 files)
Russian: singular/few/many/other
Arabic: singular/dual/few/many/other
Polish: unique rules for 1, 2-4, 5+

### Gender

French: "un document" vs "une application"
German: der, die, das (masculine, feminine, neuter)
Spanish: el/la document/application

### Capitalization

English: Capitalize after period
German: Capitalize all nouns
French: Generally lowercase except proper nouns

## Tools and Libraries

- **JavaScript**: Intl API (built-in)
- **Python**: `babel`, `pytz`
- **Java**: `java.text.DateFormat`, `java.util.Locale`
- **C#**: `System.Globalization`
- **ICU Library**: Unicode Consortium standard

## Best Practices

1. **Use built-in APIs**: Leverage Intl, babel, etc.
2. **Never hardcode formats**: Always use locale-aware methods
3. **Test all locales**: Include all target languages in testing
4. **Handle edge cases**: Leap years, DST, Islamic calendar
5. **Store in UTC**: Store times as UTC, format for display
6. **Validate input**: Validate locale-specific formats
7. **Document assumptions**: Note any locale assumptions in code
8. **User preferences**: Allow users to override system locale

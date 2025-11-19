# Locale Formatting: Dates, Numbers, and Currency

## Overview

Proper locale formatting ensures your application displays information correctly for different regions and languages. This includes dates, times, numbers, currency, and measurements.

## Date Formatting

### Common Date Formats by Region

#### United States (en-US)
```
Short Date: 12/25/2024 (MM/DD/YYYY)
Long Date: December 25, 2024
Full Format: Wednesday, December 25, 2024
ISO 8601: 2024-12-25 (technical standard)
```

#### United Kingdom (en-GB)
```
Short Date: 25/12/2024 (DD/MM/YYYY)
Long Date: 25 December 2024
Full Format: Wednesday, 25 December 2024
ISO 8601: 2024-12-25
```

#### Germany (de-DE)
```
Short Date: 25.12.2024 (DD.MM.YYYY)
Long Date: 25. Dezember 2024
Full Format: Mittwoch, 25. Dezember 2024
```

#### France (fr-FR)
```
Short Date: 25/12/2024 (DD/MM/YYYY)
Long Date: 25 décembre 2024
Full Format: mercredi 25 décembre 2024
```

#### Japan (ja-JP)
```
Short Date: 2024/12/25 (YYYY/MM/DD)
Long Date: 2024年12月25日
Full Format: 2024年12月25日 (水)
Kanji Numbers: 二千二十四年十二月二十五日
```

#### China (zh-CN)
```
Short Date: 2024/12/25 or 2024-12-25
Long Date: 2024年12月25日
Full Format: 2024年12月25日 星期三
```

#### Russia (ru-RU)
```
Short Date: 25.12.2024 (DD.MM.YYYY)
Long Date: 25 декабря 2024
Full Format: среда, 25 декабря 2024 г.
```

#### India (en-IN)
```
Short Date: 25-12-2024 (DD-MM-YYYY)
Long Date: 25 December 2024
Full Format: Wednesday, 25 December 2024
```

#### Saudi Arabia (ar-SA)
```
Short Date: 25/12/2024 (DD/MM/YYYY)
Hijri Date: 20 Jumada Al-Awwal 1446 AH
Full Format: الأربعاء، 25 ديسمبر 2024
```

### Date Format Code Examples

#### JavaScript/TypeScript with Intl API
```javascript
const date = new Date('2024-12-25');

// US Format
const usFormatter = new Intl.DateTimeFormat('en-US');
console.log(usFormatter.format(date));
// Output: 12/25/2024

// UK Format
const ukFormatter = new Intl.DateTimeFormat('en-GB');
console.log(ukFormatter.format(date));
// Output: 25/12/2024

// German Format
const deFormatter = new Intl.DateTimeFormat('de-DE', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
});
console.log(deFormatter.format(date));
// Output: Mittwoch, 25. Dezember 2024

// Japanese Format
const jaFormatter = new Intl.DateTimeFormat('ja-JP', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
});
console.log(jaFormatter.format(date));
// Output: 2024年12月25日金曜日

// Custom Format
const customOptions = {
    weekday: 'short',
    year: '2-digit',
    month: '2-digit',
    day: '2-digit'
};
console.log(new Intl.DateTimeFormat('fr-FR', customOptions).format(date));
// Output: me 25/12/24
```

#### Python with babel
```python
from babel.dates import format_date, format_datetime
from datetime import datetime

date = datetime(2024, 12, 25)

# US Format
print(format_date(date, locale='en_US'))
# Output: Dec 25, 2024

# UK Format
print(format_date(date, locale='en_GB'))
# Output: 25 Dec 2024

# German Format
print(format_date(date, locale='de_DE', format='long'))
# Output: 25. Dezember 2024

# Japanese Format
print(format_date(date, locale='ja_JP', format='long'))
# Output: 2024年12月25日

# With time
print(format_datetime(date, locale='en_US', format='long'))
# Output: December 25, 2024 12:00:00 AM
```

## Number Formatting

### Common Number Formats by Region

#### Thousands Separator and Decimal Separator

| Locale | 1,234.56 Format | Example Number | Thousands Sep | Decimal Sep |
|--------|-----------------|-----------------|---------------|-------------|
| en-US | 1,234.56 | $1,234.56 | comma (,) | period (.) |
| en-GB | 1,234.56 | £1,234.56 | comma (,) | period (.) |
| de-DE | 1.234,56 | 1.234,56 € | period (.) | comma (,) |
| fr-FR | 1 234,56 | 1 234,56 € | space | comma (,) |
| es-ES | 1.234,56 | 1.234,56 € | period (.) | comma (,) |
| ru-RU | 1 234,56 | 1 234,56 ₽ | space | comma (,) |
| ja-JP | 1,234.56 | ¥1,234.56 | comma (,) | period (.) |
| zh-CN | 1,234.56 | ¥1,234.56 | comma (,) | period (.) |

### Number Formatting Code Examples

#### JavaScript with Intl API
```javascript
const number = 1234.56;

// US Format
const usFormatter = new Intl.NumberFormat('en-US');
console.log(usFormatter.format(number));
// Output: 1,234.56

// German Format
const deFormatter = new Intl.NumberFormat('de-DE');
console.log(deFormatter.format(number));
// Output: 1.234,56

// French Format
const frFormatter = new Intl.NumberFormat('fr-FR');
console.log(frFormatter.format(number));
// Output: 1 234,56

// Significant Digits
const sciFormatter = new Intl.NumberFormat('en-US', {
    minimumSignificantDigits: 3,
    maximumSignificantDigits: 5
});
console.log(sciFormatter.format(1234567));
// Output: 1,235,000

// Percentage
const percentFormatter = new Intl.NumberFormat('en-US', {
    style: 'percent'
});
console.log(percentFormatter.format(0.856));
// Output: 86%

// Scientific Notation
const sciNotation = new Intl.NumberFormat('en-US', {
    notation: 'scientific'
});
console.log(sciNotation.format(1234567));
// Output: 1.23E6
```

#### Python with babel
```python
from babel.numbers import format_number, format_decimal

number = 1234.56

# US Format
print(format_number(number, locale='en_US'))
# Output: 1,234.56

# German Format
print(format_decimal(number, locale='de_DE'))
# Output: 1.234,56

# French Format
print(format_decimal(number, locale='fr_FR'))
# Output: 1 234,56

# Russian Format
print(format_decimal(number, locale='ru_RU'))
# Output: 1 234,56
```

## Currency Formatting

### Currency Symbols and Codes

#### By Region
```javascript
// Currency formatting examples

const currencyAmount = 1234.56;

// US Dollar
const usdFormatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
});
console.log(usdFormatter.format(currencyAmount));
// Output: $1,234.56

// Euro
const eurFormatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'EUR'
});
console.log(eurFormatter.format(currencyAmount));
// Output: €1,234.56

// British Pound
const gbpFormatter = new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: 'GBP'
});
console.log(gbpFormatter.format(currencyAmount));
// Output: £1,234.56

// Japanese Yen
const jpyFormatter = new Intl.NumberFormat('ja-JP', {
    style: 'currency',
    currency: 'JPY'
});
console.log(jpyFormatter.format(currencyAmount));
// Output: ￥1,235 (no decimals for yen)

// Chinese Yuan
const cnyFormatter = new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY'
});
console.log(cnyFormatter.format(currencyAmount));
// Output: ¥1,234.56

// Indian Rupee
const inrFormatter = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR'
});
console.log(inrFormatter.format(currencyAmount));
// Output: ₹1,234.56

// Russian Ruble
const rubFormatter = new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB'
});
console.log(rubFormatter.format(currencyAmount));
// Output: 1 234,56 ₽

// Saudi Riyal
const sarFormatter = new Intl.NumberFormat('ar-SA', {
    style: 'currency',
    currency: 'SAR'
});
console.log(sarFormatter.format(currencyAmount));
// Output: ﷼1,234.56

// Mexican Peso
const mxnFormatter = new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN'
});
console.log(mxnFormatter.format(currencyAmount));
// Output: $1,234.56

// Brazilian Real
const brlFormatter = new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
});
console.log(brlFormatter.format(currencyAmount));
// Output: R$ 1.234,56
```

### Currency Position by Locale

| Locale | Currency Position | Example |
|--------|------------------|---------|
| en-US | Before number | $1,234.56 |
| en-GB | Before number | £1,234.56 |
| de-DE | After number | 1.234,56 € |
| fr-FR | After number | 1 234,56 € |
| es-ES | After number | 1.234,56 € |
| ja-JP | Before number | ￥1,235 |
| zh-CN | Before number | ¥1,234.56 |
| ru-RU | After number | 1 234,56 ₽ |
| pt-BR | Before number | R$ 1.234,56 |

## Time Formatting

### Time Formats by Region

#### 12-Hour vs 24-Hour

| Locale | Format | Example |
|--------|--------|---------|
| en-US | 12-hour | 3:45:30 PM |
| en-GB | 24-hour | 15:45:30 |
| de-DE | 24-hour | 15:45:30 |
| fr-FR | 24-hour | 15:45:30 |
| ja-JP | 24-hour | 15:45:30 |
| zh-CN | 24-hour | 15:45:30 |
| ru-RU | 24-hour | 15:45:30 |

### Time Formatting Code Examples

```javascript
const time = new Date('2024-12-25T15:45:30');

// US 12-hour format
const usTimeFormatter = new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
});
console.log(usTimeFormatter.format(time));
// Output: 3:45:30 PM

// Germany 24-hour format
const deTimeFormatter = new Intl.DateTimeFormat('de-DE', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
});
console.log(deTimeFormatter.format(time));
// Output: 15:45:30

// Japan 24-hour format
const jaTimeFormatter = new Intl.DateTimeFormat('ja-JP', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
});
console.log(jaTimeFormatter.format(time));
// Output: 15:45:30
```

## Calendar Systems

### Non-Gregorian Calendars

#### Islamic Calendar (Hijri)
```javascript
// Requires calendar option support
const islamicDate = new Intl.DateTimeFormat('ar-SA', {
    calendar: 'islamic',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
});
console.log(islamicDate.format(new Date('2024-12-25')));
// Output: 20 Jumada Al-Awwal 1446 AH
```

#### Hebrew Calendar
```javascript
const hebrewDate = new Intl.DateTimeFormat('he-IL', {
    calendar: 'hebrew',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
});
console.log(hebrewDate.format(new Date('2024-12-25')));
// Output: 23 Tevet 5785
```

#### Japanese Calendar
```javascript
const japaneseDate = new Intl.DateTimeFormat('ja-JP', {
    calendar: 'japanese',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
});
console.log(japaneseDate.format(new Date('2024-12-25')));
// Output: 令和6年12月25日
```

## Measurements and Units

### Unit Formatting

```javascript
// Unit formatting (requires modern browser support)
const unitFormatter = new Intl.NumberFormat('en-US', {
    style: 'unit',
    unit: 'kilometer',
    unitDisplay: 'long'
});
console.log(unitFormatter.format(5));
// Output: 5 kilometers

// Temperature
const tempFormatter = new Intl.NumberFormat('en-US', {
    style: 'unit',
    unit: 'celsius'
});
console.log(tempFormatter.format(25));
// Output: 25°C

// Weight
const weightFormatter = new Intl.NumberFormat('de-DE', {
    style: 'unit',
    unit: 'kilogram'
});
console.log(weightFormatter.format(75));
// Output: 75 kg
```

### Common Measurement Systems by Region

| Region | Length | Weight | Temperature | Volume |
|--------|--------|--------|-------------|--------|
| USA | Miles | Pounds | Fahrenheit | Gallons |
| UK | Miles | Pounds/Stones | Celsius | Liters |
| Germany | Kilometers | Kilograms | Celsius | Liters |
| Japan | Kilometers | Kilograms | Celsius | Liters |
| India | Kilometers | Kilograms | Celsius | Liters |
| China | Kilometers | Kilograms | Celsius | Liters |

## Line Breaking and Text Formatting

### Line Breaking Rules

#### Latin Scripts (English, German, French)
```
Rules:
- Break at word boundaries (spaces)
- Hyphens can break lines
- Minimal restrictions
```

#### CJK (Chinese, Japanese, Korean)
```
Rules:
- Characters don't have space separators
- Can break after most characters
- Specific punctuation rules for avoiding line starts/ends
- Parentheses and quotes have special rules
```

#### Arabic and Hebrew
```
Rules:
- Space-separated words
- Right-to-left direction (see separate section)
- Specific punctuation handling
```

### Line Breaking Code Example

```javascript
// Suggested line breaking (requires Intl.Segmenter)
const segmenter = new Intl.Segmenter('ja-JP', {
    granularity: 'word'
});

const text = '日本語のテキストを分割します';
for (const segment of segmenter.segment(text)) {
    console.log(segment);
    // Breaks at appropriate word boundaries
}

// Line breaking
const lineSegmenter = new Intl.Segmenter('ja-JP', {
    granularity: 'grapheme'
});

// Can break lines after any grapheme in Japanese
```

## Collation and Sorting

### Locale-Aware Sorting

```javascript
// Array of names in different languages
const names = ['Ärger', 'Apple', 'Äpfel', 'Appetit'];

// German sorting
const deCollator = new Intl.Collator('de-DE');
console.log(names.sort(deCollator.compare));
// Output: ['Äpfel', 'Apple', 'Ärger', 'Appetit']

// Swedish sorting (treats Ä differently)
const svCollator = new Intl.Collator('sv-SE');
console.log(names.sort(svCollator.compare));
// Output: ['Apple', 'Appetit', 'Äpfel', 'Ärger']

// Case sensitivity
const caseInsensitive = new Intl.Collator('en-US', {
    sensitivity: 'accent'
});
const caseSensitive = new Intl.Collator('en-US', {
    sensitivity: 'case'
});
```

## List Formatting

### Locale-Specific List Formatting

```javascript
// JavaScript Intl.ListFormat
const listFormatter = new Intl.ListFormat('en-US', {
    style: 'long',
    type: 'conjunction'
});

console.log(listFormatter.format(['apple', 'banana', 'orange']));
// Output: apple, banana, and orange

// German
const deListFormatter = new Intl.ListFormat('de-DE', {
    style: 'long',
    type: 'conjunction'
});

console.log(deListFormatter.format(['Apfel', 'Banane', 'Orange']));
// Output: Apfel, Banane und Orange

// Disjunction (OR)
const orFormatter = new Intl.ListFormat('en-US', {
    type: 'disjunction'
});

console.log(orFormatter.format(['red', 'green', 'blue']));
// Output: red, green, or blue
```

## Plural Forms

### Language-Specific Plural Rules

```javascript
// English: singular/plural
0 items
1 item
2 items

// Polish: more complex
1 item
2-4 items
5+ items

// Russian: complex rules
1 file
2-4 files
5+ files

// Arabic: 6 categories
singular (1)
dual (2)
few (3-10)
many (11-99)
other (100+)
```

### Plural Formatting Code Example

```javascript
const pluralRules = new Intl.PluralRules('en-US');

const items = [0, 1, 2, 5, 21];
const messages = {
    'one': 'You have one message',
    'other': 'You have {count} messages'
};

items.forEach(count => {
    const rule = pluralRules.select(count);
    const message = messages[rule].replace('{count}', count);
    console.log(message);
});

// Output:
// You have 0 messages
// You have one message
// You have 2 messages
// You have 5 messages
// You have 21 messages
```

## Best Practices

1. **Always use locale-aware formatting** - Never hardcode formats
2. **Test with real data** - Include edge cases (zeros, negatives, large numbers)
3. **Consider space constraints** - Some formats are longer than others
4. **Use standard APIs** - Rely on Intl.* APIs for consistency
5. **Handle fallbacks** - Provide defaults for unsupported locales
6. **Test with multiple locales** - Especially RTL and CJK languages
7. **Document formatting rules** - Help translators understand format expectations
8. **Validate input** - Ensure locale codes and currency codes are valid

## Common Pitfalls

1. **Assuming English format is universal** - It's not
2. **Forgetting about time zones** - Always work with timezone-aware dates
3. **Not testing negative numbers** - They format differently by locale
4. **Ignoring measurement systems** - Some regions use different units
5. **Hardcoding currency symbols** - Use proper currency codes
6. **Not considering space in currencies** - Some locales add spaces
7. **Forgetting plural rules** - Different languages have different rules

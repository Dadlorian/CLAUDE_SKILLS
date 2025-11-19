# Loan Types Reference

## Conventional Loans
- **Conforming**: Meet Fannie/Freddie limits
- **Down Payment**: 5-20%
- **PMI**: Required if < 20% down
- **Credit Score**: 620+ (3% down), 740+ (best rates)

## Government Loans
### FHA
- Down payment: 3.5%
- Credit score: 580+
- Mortgage insurance: Required

### VA
- Down payment: 0%
- Veterans/active military
- No PMI
- Funding fee: 2.3%

### USDA
- Down payment: 0%
- Rural properties
- Income limits

## Jumbo Loans
- Above conforming limits ($726,200 in 2023)
- Stricter requirements
- Higher rates

## Investment Property Loans
- **Conventional**: 15-25% down
- **Portfolio**: Bank-specific
- **Commercial**: For 5+ units
- **Hard Money**: Short-term, high-cost

## Calculation Examples
```python
# Monthly payment (PITI)
def calculate_payment(principal, rate, years):
    monthly_rate = rate / 12 / 100
    n_payments = years * 12
    
    payment = principal * (
        monthly_rate * (1 + monthly_rate)**n_payments
    ) / ((1 + monthly_rate)**n_payments - 1)
    
    return round(payment, 2)

# Example: $400K loan, 6.5%, 30 years
payment = calculate_payment(400000, 6.5, 30)  # $2,528
```

## See Also
- underwriting_criteria.md
- mismo_standards.md

# Treasury Management in Banking

## Treasury Management Overview

### What is Treasury Management?
Treasury Management encompasses the financial services that help businesses and institutions manage their liquidity, investments, borrowings, and foreign exchange. It involves:
- **Liquidity Management**: Optimize cash positions
- **Investment Management**: Manage surplus cash
- **Borrowing Management**: Optimize debt structure
- **FX Management**: Manage currency exposures
- **Risk Management**: Hedge financial risks

### Treasury Functions in Banks
```
Bank Treasury Operations:
├── Funds Management
│   ├── Managing net funding position
│   ├── Optimizing cost of funds
│   └── Managing interest rate risk
│
├── Liquidity Management
│   ├── Daily cash position forecasting
│   ├── Liquidity buffer maintenance
│   └── Emergency liquidity planning
│
├── Investment Portfolio
│   ├── Securities portfolio management
│   ├── Yield optimization
│   └── Portfolio risk management
│
├── Funding Operations
│   ├── Raising deposit funding
│   ├── Capital markets funding
│   ├── Interbank borrowing
│   └── Central bank liquidity
│
├── FX Trading
│   ├── FX risk hedging
│   ├── Proprietary FX trading
│   └── Correspondent banking
│
└── Risk Management
    ├── Interest rate risk
    ├── Liquidity risk
    ├── FX risk
    └── Counterparty risk
```

## Cash Position Management

### Daily Cash Forecasting
```
Forecast Components:
├── Expected Deposits (customers, institutions)
│   ├── Payroll deposits
│   ├── Government benefit deposits
│   ├── Business account deposits
│   └── Interbank deposits
│
├── Expected Withdrawals
│   ├── ATM withdrawals
│   ├── Checks paid
│   ├── ACH transfers
│   └── Wire transfers
│
├── Loan Repayments
│   ├── Scheduled principal payments
│   ├── Interest payments
│   └── Early prepayments
│
└── Funding Needs
    ├── Capital requirements
    ├── Debt maturities
    └── Contingencies
```

### Sweep Accounts
```
Purpose: Optimize liquidity by moving excess funds

Mechanism:
1. Define threshold balance (e.g., $100,000)
2. At end of day:
   - If balance > threshold: Sweep excess to investment account
   - If balance < threshold: Sweep from investment account back
3. Sweep to highest-yielding eligible accounts

Benefits:
├── Earn higher returns on excess cash
├── Maintain minimum required balances
├── Reduce borrowing needs
├── Automated liquidity optimization
└── Reduce operational overhead
```

### Reserve Balances
```
Minimum Balances Required:
├── Federal Reserve requirement (varies by bank)
├── Clearing house requirements
├── Correspondent bank requirements
├── Internal risk policies
└── Customer deposit balances
```

## Investment Portfolio Management

### Fixed Income Investments
```
Securities Held:
├── Government Bonds
│   ├── Treasury securities (US)
│   ├── Gilts (UK)
│   ├── Bunds (Germany)
│   └── Equivalent in home country
│
├── Corporate Bonds
│   ├── Investment-grade bonds
│   ├── High-yield bonds
│   └── Convertible bonds
│
├── Mortgage-Backed Securities (MBS)
│   ├── Agency MBS (government-backed)
│   └── Non-agency MBS
│
└── Asset-Backed Securities (ABS)
    ├── Consumer auto loans
    ├── Credit card receivables
    └── Student loans
```

### Portfolio Analytics
```
Metrics Tracked:
├── Duration (interest rate sensitivity)
├── Convexity (non-linear price changes)
├── Credit quality (default risk)
├── Yield curve positioning
├── Interest rate scenarios
├── Duration matching with liabilities
└── Value at Risk (VaR)
```

### Investment Reporting
```
Reports Generated:
├── Portfolio composition
├── Market value and mark-to-market
├── Unrealized gains/losses
├── Yield analysis
├── Duration analysis
├── Credit exposure
├── Scenario analysis
└── Regulatory capital impact
```

## Funding Management

### Funding Sources
```
Retail Deposits:
├── Checking accounts
├── Savings accounts
├── Money market accounts
├── Certificates of deposit (CDs)
└── FDIC insured up to $250K per account

Wholesale Funding:
├── Other bank borrowings
├── Federal funds (overnight rate)
├── Repo market (sale-repurchase agreements)
├── Brokered deposits
└── Capital markets (bonds, notes)

Central Bank Liquidity:
├── Discount window loans
├── Open market operations
├── Emergency lending facilities
└── Quantitative easing programs
```

### Cost of Funds Analysis
```
Calculation:
Total Interest Expense / Average Earning Assets = Cost of Funds

Example:
├── Total deposits: $500M
├── Avg interest paid: 0.5%
├── Cost of deposit funding: $2.5M annually
├── As percentage: 0.5%
└── Drives lending rate pricing
```

### Funding Mix Optimization
```
Strategy:
├── Balance retail and wholesale funding
├── Diversify funding sources
├── Match maturity profiles
├── Minimize cost of funds
├── Maintain adequate liquidity
└── Regulatory capital optimization

Constraints:
├── Regulatory ratios (LCR, NSFR)
├── Internal risk limits
├── Counterparty limits
├── Maturity ladder limits
└── Diversification requirements
```

## Interest Rate Risk Management

### Interest Rate Exposure
```
Risks:
├── Gap Risk: Repricing mismatches between assets and liabilities
├── Basis Risk: Different index movements (prime vs SOFR)
├── Yield Curve Risk: Changes in curve shape
└── Convexity Risk: Non-linear price movements

Impact:
├── If rates rise and assets reprice slowly: Margin compression
├── If rates fall and deposits leave: Liquidity pressure
└── Prepayment risk on fixed-rate mortgages
└── Extension risk on bonds
```

### Interest Rate Hedging
```
Techniques:
├── Asset-liability matching (ALM)
├── Interest rate swaps
├── Interest rate futures
├── Interest rate options (caps, floors, swaptions)
├── Floating-rate asset purchases
└── Deposit pricing adjustments
```

### Scenario Analysis
```
Scenarios Modeled:
├── Parallel shift (all rates up/down equally)
├── Steepener/Flattener (curve changes)
├── Bull/Bear steepening
├── Rate shock (instantaneous large move)
└── Historical scenarios
```

## Foreign Exchange Management

### FX Exposure Sources
```
Transaction Exposure:
├── Foreign currency receivables
├── Foreign currency payables
├── International wire transfers
├── Correspondent banking
└── Customer FX transactions

Translation Exposure:
├── Foreign subsidiary assets/liabilities
├── Equity investment translation
├── Consolidated financial statements
└── Regulatory reporting impact

Economic Exposure:
├── Competitive position changes
├── Price competitiveness impacts
├── Market share effects
└── Long-term business impacts
```

### FX Hedging Instruments
```
Forward Contracts:
├── Agree to exchange currencies on future date
├── Fixed exchange rate
├── Customized amounts and dates
├── Not traded on exchanges

FX Swaps:
├── Simultaneous buy/sell on different dates
├── Short-term rate + forward rate
├── Very liquid and transparent
├── Common for overnight to 1-year

Currency Options:
├── Right (not obligation) to exchange
├── Call option: Right to buy
├── Put option: Right to sell
├── Used for contingent exposures

Money Market Hedges:
├── Borrow/lend in other currency
├── Match foreign exposure timing
├── Alternative to forward contracts
├── Uses interest rate differential
```

### FX Trading
```
Spot Trading:
├── Immediate currency exchange (T+2)
├── Most liquid instrument
├── Used to hedge or position
├── Major volume driver

Trading Operations:
├── Live market quotes
├── Order execution
├── Settlement and delivery
├── Position tracking
├── P&L calculation
└── Risk monitoring
```

## Correspondent Banking

### Correspondent Relationships
```
Purpose: Facilitate international payment settlement

Services Provided:
├── SWIFT messaging
├── Payment settlements
├── Check clearing
├── FX conversions
├── Account maintenance
└── Liquidity access

Nostro Accounts:
├── Bank's account at foreign correspondent
├── Denominated in foreign currency
├── Used for settlement
├── Pre-funded for operations

Vostro Accounts:
├── Correspondent's account at our bank
├── Denominated in our currency
├── Used for their settlement
├── Monitored for compliance
```

## Treasury Risk Management

### Liquidity Risk Management
```
Daily Monitoring:
├── Liquidity coverage ratio (LCR)
├── Net stable funding ratio (NSFR)
├── Maturity profile
├── Concentration limits
└── Stress scenarios

Policies:
├── Maintain 100%+ LCR
├── Diversified funding sources
├── No over-reliance on any source
├── Contingency funding plans
└── Regular testing
```

### Counterparty Risk
```
Management:
├── Credit ratings monitoring
├── Exposure limits per counterparty
├── Collateral requirements (CSA)
├── Netting agreements
├── Contingent credit lines
└── Regular reassessment
```

### Operational Risk
```
Controls:
├── Segregation of duties
├── Dual authorization for large transactions
├── Daily reconciliation
├── Audit trails
├── Stress testing
├── Regular training
└── Control testing
```

## Treasury Reporting and Analytics

### Daily Reports
```
Daily Treasury Report:
├── Opening positions
├── Transactions
├── Closing positions
├── Cash flow summary
├── Interest rate exposure
├── FX exposure
├── P&L calculation
└── Liquidity metrics
```

### Management Reporting
```
Weekly/Monthly Reports:
├── Funds management summary
├── Investment portfolio performance
├── Funding cost analysis
├── Interest rate sensitivity
├── Liquidity position
├── Counterparty exposures
├── Risk metrics (VaR, stress tests)
└── Variance analysis (actual vs budget)
```

### Regulatory Reporting
```
Required Filings:
├── Quarterly call reports
├── Annual stress test results
├── LCR/NSFR ratios
├── Interest rate risk disclosures
├── Liquidity adequacy reports
└── Counterparty risk disclosures
```

## Technology and Systems

### Treasury Management Systems (TMS)
```
Key Functionality:
├── Cash position management
├── Deal booking and settlement
├── Portfolio management
├── Risk measurement and reporting
├── Straight-through processing (STP)
├── Integration with market data feeds
└── Integration with accounting systems

Popular Systems:
├── Murex
├── SunGard (Numerix)
├── Technimetrics
├── Bloomberg PORT
└── Moody's Analytics
```

### Market Data Integration
```
Data Feeds:
├── Interest rate curves
├── FX rates (real-time)
├── Bond yields and prices
├── Equity indices
├── Credit spreads
├── Volatility indices
└── Economic calendars
```

## Best Practices

### Governance
```
Structure:
├── Chief Financial Officer (CFO) oversight
├── Chief Treasury Officer (CTO) management
├── Investment committee oversight
├── Daily operations management
├── Independent risk monitoring
└── Regular board reporting
```

### Policies and Procedures
```
Documentation:
├── Treasury policy
├── Delegated authority limits
├── Position limits (by instrument, currency, counterparty)
├── Maturity ladder limits
├── Diversification requirements
├── Approved instruments list
└── Contingency funding plan
```

### Risk Management
```
Framework:
├── Market risk (VaR, stress testing)
├── Liquidity risk (LCR, NSFR, stress scenarios)
├── Counterparty risk (exposure limits, monitoring)
├── Operational risk (controls, procedures)
└── Compliance risk (regulatory alignment)
```

## Conclusion
Treasury management is critical to bank operations, ensuring adequate liquidity, optimizing cost of funds, managing interest rate and FX risks, and maintaining regulatory compliance. Sophisticated systems and experienced teams manage complex funding, investment, and hedging decisions to support the bank's overall business strategy.

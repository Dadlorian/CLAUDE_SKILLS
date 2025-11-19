# Modern Portfolio Theory (MPT) & Optimization

## Markowitz's Mean-Variance Framework

Modern Portfolio Theory, developed by Harry Markowitz in 1952, provides a mathematical approach to portfolio selection that maximizes expected returns for a given level of risk (or minimizes risk for a given return).

## Core Mathematical Framework

### Portfolio Return
The expected return of a portfolio is the weighted average of individual asset returns:

```
E(Rp) = Σ wi × E(Ri)
```

Where:
- wi = weight of asset i in portfolio
- E(Ri) = expected return of asset i
- Σwi = 1 (fully invested)

### Portfolio Variance
The variance considers both individual asset volatilities and the correlation between assets:

```
σp² = Σ wi² × σi² + 2 × Σ(i<j) wi × wj × σi × σj × ρij
```

Where:
- σi² = variance of asset i
- ρij = correlation coefficient between assets i and j
- The covariance term = σi × σj × ρij

### Covariance Matrix
For practical implementation with multiple assets, use the covariance matrix:

```
Cov Matrix = [σ₁²    σ₁₂  σ₁₃  ...  σ₁ₙ
              σ₂₁    σ₂²  σ₂₃  ...  σ₂ₙ
              ...
              σₙ₁    σₙ₂  σₙ₃  ...  σₙ²]
```

## Efficient Frontier Construction

### Properties
1. **Non-Dominated**: Each portfolio on frontier has:
   - No higher return at same risk
   - No lower risk at same return

2. **Curved Shape**:
   - Convex when plotted with risk on x-axis, return on y-axis
   - Reflects diminishing benefits of diversification

3. **All Individual Assets Below**:
   - Individual assets are dominated by diversified portfolios
   - Diversification creates value

### Construction Algorithm
1. Calculate expected returns and covariances for all assets
2. For each risk level:
   - Minimize variance subject to:
     - Expected return = target return
     - Weights sum to 1
3. Plot minimum-variance portfolios (efficient frontier)

## Optimization Approaches

### Mean-Variance Optimization (MVO)
Minimize portfolio variance subject to:
```
minimize: σp²
subject to:
  E(Rp) = R_target
  Σ wi = 1
  wi >= 0 (no short selling)
  Other constraints...
```

### Sharpe Ratio Maximization
Maximize risk-adjusted returns:
```
maximize: (E(Rp) - Rf) / σp
where:
  Rf = risk-free rate
```

The tangency portfolio (maximum Sharpe ratio) represents the optimal risky portfolio.

### Minimum Variance Portfolio (MVP)
Find portfolio with lowest volatility:
```
minimize: σp²
subject to:
  Σ wi = 1
  wi >= 0
```

## Capital Market Line (CML)

### Definition
The CML shows the expected return of a portfolio as a function of its risk:

```
E(Rp) = Rf + [(E(Rm) - Rf) / σm] × σp
```

Where:
- Rf = risk-free rate
- Rm = market return
- σm = market volatility
- σp = portfolio volatility

### Key Points
- All investors should hold tangency (market) portfolio plus risk-free asset
- Allocation between risky and risk-free asset depends on risk tolerance
- More risk-averse investors: more in risk-free asset
- More aggressive investors: borrow at risk-free rate to lever up market portfolio

## Capital Asset Pricing Model (CAPM)

Extends MPT by defining expected returns based on systematic risk (beta):

```
E(Ri) = Rf + βi(E(Rm) - Rf)
```

Where:
- βi = Cov(Ri, Rm) / σm² = systematic risk of asset i
- E(Rm) - Rf = market risk premium

### Implications
- Only systematic (non-diversifiable) risk is rewarded
- Unsystematic risk should be diversified away
- Asset pricing depends on correlation with market
- Higher beta = higher expected returns

## Black-Litterman Model

Improves upon classical MPT by incorporating:

### Problem with MVO
- Highly sensitive to expected return estimates
- Small changes in return assumptions cause large allocation changes
- Often produces extreme allocations

### Black-Litterman Solution
1. Start with market-implied returns (from current prices)
2. Incorporate views on certain assets
3. Blend views with market expectations using confidence levels
4. Results in more stable, practical allocations

### Formula
```
E(R_new) = E(R_market) + T × Σ × P^T × (P × Σ × P^T + Ω)^(-1) × (Q - P × E(R_market))
```

Where:
- T = scalar uncertainty parameter
- Σ = covariance matrix
- P = view matrix (which assets have views)
- Q = view expectations
- Ω = view uncertainty covariance

## Practical Optimization Techniques

### Linear and Quadratic Programming
- Quadratic programming solves standard MPT
- Linear constraints (weights, bounds, turnover limits)
- Efficient algorithms: interior point methods, active set methods

### Lagrange Multipliers
Used for constrained optimization:
```
L = f(w) - λ₁(g₁(w)) - λ₂(g₂(w)) - ...
```

Where:
- f(w) = objective function
- g(w) = constraints
- λ = Lagrange multipliers (dual variables)

### Estimation Techniques
- Historical estimation: Simple but unstable
- Shrinkage methods: Blend historical and assumptions
- Factor models: Use factor exposures for estimation
- Expert judgment: Incorporate analyst views

## Constraints in Real-World Optimization

### Practical Constraints
1. **Weight Constraints**: 0% to 100% per asset (long-only)
2. **Turnover Limits**: Minimize trading costs and tax drag
3. **Holding Constraints**: Minimum positions, mandatory holds
4. **Sector Limits**: Maximum exposure to sectors
5. **Benchmark Relative**: Track-error constraints
6. **Liquidity**: Maximum position sizes based on trading volume

### Implementation
- Constrained optimization solvers (CVXPY, Gurobi, CPLEX)
- Add constraints to minimize/maximize function
- Solvers return optimal weights satisfying all constraints

## Limitations and Criticisms

1. **Estimation Risk**: Assumes known returns and covariances
2. **Single-Period**: Only considers one investment period
3. **Normal Distributions**: Assumes normal returns (ignores tails)
4. **Frictionless Markets**: Ignores transaction costs and taxes
5. **Concentration Risk**: Can produce corner solutions
6. **Parameter Sensitivity**: Small input changes cause large allocation changes

## Extensions and Refinements

- **Multi-period Optimization**: Dynamic programming for sequential decisions
- **Robust Optimization**: Minimize worst-case returns
- **Factor-based Models**: Use factor exposures instead of individual assets
- **Machine Learning**: Improved covariance and return estimation
- **Behavioral Factors**: Incorporate investor psychology and biases

## Implementation in Robo-Advisory

MPT forms the foundation for:
- Automated portfolio construction
- Risk-based client segmentation
- Objective optimization vs subjective methods
- Benchmark-relative performance
- Educational content for clients

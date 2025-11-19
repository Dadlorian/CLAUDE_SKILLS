# Portfolio Theory Fundamentals

## Introduction to Portfolio Theory

Portfolio theory provides the mathematical foundation for constructing diversified investment portfolios that optimize the risk-return tradeoff. The theory explains how rational investors should allocate their assets to minimize risk for a given expected return.

## Key Concepts

### Risk and Return
- **Expected Return**: The weighted average of returns from all assets in the portfolio
  - E(Rp) = Σ(wi × E(Ri))
  - Where wi = weight of asset i, E(Ri) = expected return of asset i

- **Portfolio Variance**: Measures the dispersion of returns around the expected value
  - σp² = Σ(wi² × σi²) + 2×Σ(wi×wj×σi×σj×ρij)
  - Includes both individual asset variances and covariance terms

- **Portfolio Standard Deviation**: Square root of variance, measures total risk
  - σp = √(σp²)

### Diversification Benefit
- **Correlation**: Measures how two assets move together
  - ρ = Covariance(i,j) / (σi × σj)
  - Ranges from -1 (perfect negative) to +1 (perfect positive)

- **Diversification Reduces Risk**: When assets are not perfectly correlated, portfolio risk is less than the weighted average of individual risks
  - Lower correlations provide greater diversification benefits
  - Zero or negative correlations are most beneficial

### Efficient Frontier
- **Definition**: The curve representing the optimal portfolios that provide:
  - Highest expected return for a given level of risk
  - Lowest risk for a given level of expected return

- **Properties**:
  - Curved shape due to covariance effects
  - Convex when viewed from the origin
  - Represents all portfolios in the efficient set

### Capital Allocation Line (CAL)
- **Definition**: Line showing return-risk combinations by combining risk-free asset with risky portfolio
  - Expected Return = Rf + β(Rm - Rf)
  - β = volatility of risky portfolio / volatility of market

- **Optimal Combination**: Combines Markowitz efficient frontier with risk-free rate
  - Creates the Capital Market Line (CML) at the tangency point
  - Tangency portfolio is optimal regardless of investor risk preferences

## Classical vs. Behavioral Extensions

### Classical Portfolio Theory Assumptions
- Rational investors maximize utility
- No transaction costs or taxes
- Markets are perfectly efficient
- Investors have identical expectations
- Assets are infinitely divisible
- No restrictions on short selling

### Real-World Refinements
- Transaction costs and taxes matter significantly
- Behavioral biases affect investor decisions
- Markets have imperfections and friction costs
- Investors have different time horizons and constraints
- Sustainable withdrawal rates limit asset allocation
- Implementation requires discrete asset selection

## Limitations and Extensions

1. **Estimation Risk**: Expected returns and covariances are estimated, not known
2. **Non-Normal Distributions**: Asset returns exhibit fat tails and skewness
3. **Non-Stationary Parameters**: Correlations and risks change over time
4. **Constraint Handling**: Real portfolios have many practical constraints
5. **Multi-Period Issues**: Single-period theory may not capture dynamic optimization

## Practical Applications in Robo-Advisory

- Foundation for automated portfolio construction
- Basis for risk-based client segmentation
- Framework for objective optimization
- Benchmark for comparing alternative approaches
- Reference for explaining portfolio decisions to clients

## Key Metrics

| Metric | Formula | Interpretation |
|--------|---------|-----------------|
| Expected Return | Σ(wi × E(Ri)) | Average expected return |
| Portfolio Variance | Σ(wi² × σi²) + Σ(wi×wj×Cov) | Dispersion of returns |
| Standard Deviation | √(Variance) | Total volatility |
| Sharpe Ratio | (Rp - Rf) / σp | Risk-adjusted return |
| Beta | Cov(Ri,Rm) / σm² | Systematic risk |
| Information Ratio | (Rp - Rb) / σe | Active return per unit of tracking error |

## Further Reading
- Markowitz, H. (1952). "Portfolio Selection"
- Sharpe, W. (1964). "Capital Asset Pricing Model"
- Brinson & Fachler (1985). "Measuring Non-Parametric Performance"

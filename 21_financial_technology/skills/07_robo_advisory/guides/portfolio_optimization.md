# Portfolio Optimization Algorithms and Methods

## Mean-Variance Optimization (MVO)

### Mathematical Framework

**Objective**: Maximize return per unit of risk

```
minimize: σp² = Σ Σ wi × wj × σij

subject to:
  E(Rp) = R_target
  Σ wi = 1
  wi >= 0 (long-only constraint)
```

### Python Implementation

```python
import numpy as np
from scipy.optimize import minimize

class PortfolioOptimizer:
    def __init__(self, expected_returns, cov_matrix):
        self.mu = expected_returns
        self.cov = cov_matrix
        self.n_assets = len(expected_returns)

    def portfolio_stats(self, weights):
        """Calculate portfolio return and variance"""
        ret = np.sum(weights * self.mu)
        var = np.dot(weights, np.dot(self.cov, weights))
        return ret, np.sqrt(var)

    def optimize_min_variance(self):
        """Find minimum variance portfolio"""
        def objective(w):
            return np.dot(w, np.dot(self.cov, w))

        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        init_guess = np.array([1/self.n_assets] * self.n_assets)

        result = minimize(objective, init_guess, method='SLSQP',
                         bounds=bounds, constraints=constraints)

        return result.x

    def optimize_sharpe_ratio(self, risk_free_rate=0.02):
        """Find maximum Sharpe ratio portfolio"""
        def objective(w):
            ret, std = self.portfolio_stats(w)
            return -(ret - risk_free_rate) / std

        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        init_guess = np.array([1/self.n_assets] * self.n_assets)

        result = minimize(objective, init_guess, method='SLSQP',
                         bounds=bounds, constraints=constraints)

        return result.x

    def optimize_efficient_frontier(self, n_points=50):
        """Generate efficient frontier"""
        min_ret = np.min(self.mu)
        max_ret = np.max(self.mu)
        target_returns = np.linspace(min_ret, max_ret, n_points)

        frontier_weights = []
        frontier_returns = []
        frontier_risks = []

        for target_ret in target_returns:
            def objective(w):
                return np.dot(w, np.dot(self.cov, w))

            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
                {'type': 'eq', 'fun': lambda w: np.sum(w * self.mu) - target_ret}
            ]

            bounds = tuple((0, 1) for _ in range(self.n_assets))
            init_guess = np.array([1/self.n_assets] * self.n_assets)

            result = minimize(objective, init_guess, method='SLSQP',
                             bounds=bounds, constraints=constraints)

            if result.success:
                ret, risk = self.portfolio_stats(result.x)
                frontier_weights.append(result.x)
                frontier_returns.append(ret)
                frontier_risks.append(risk)

        return frontier_weights, frontier_returns, frontier_risks
```

## Black-Litterman Model

### Concept

Improves MVO by incorporating investor views on expected returns:

```
E(R) = Π + τ × Σ × P' × (P × Σ × P' + Ω)^(-1) × (Q - P × Π)

Where:
Π = Market-implied returns (from current prices)
τ = Scalar uncertainty parameter
Σ = Covariance matrix
P = Views matrix (which assets have views)
Q = View expectations
Ω = View uncertainty covariance
```

### Implementation Steps

1. **Calculate Market Returns**:
```python
def calculate_market_returns(market_cap_weights, risk_aversion, cov_matrix):
    """Calculate equilibrium returns from market prices"""
    market_return = risk_aversion @ (market_cap_weights @ cov_matrix @ market_cap_weights)
    implied_returns = risk_aversion * (cov_matrix @ market_cap_weights)
    return implied_returns
```

2. **Express Views**:
```python
# View 1: Tech will outperform by 2%
# View 2: Value will underperform by 1%

P = np.array([
    [1, 0, -1],  # Tech (weight 1) vs Small-Cap (weight -1)
    [0, -1, 0]   # Value (weight -1)
])

Q = np.array([0.02, -0.01])  # Expected return differences

Omega = np.diag([0.001, 0.0005])  # View confidence
```

3. **Blend Views with Market**:
```python
def black_litterman_returns(market_returns, P, Q, Omega, cov_matrix, tau=0.05):
    """Calculate blended expected returns"""
    term1 = market_returns
    term2 = tau * cov_matrix @ P.T
    term3_inv = np.linalg.inv(P @ cov_matrix @ P.T + Omega)
    term3 = P @ market_returns - Q

    bl_returns = term1 + term2 @ term3_inv @ term3
    return bl_returns
```

## Constraint-Based Optimization

### Common Constraints

```python
class ConstrainedOptimizer(PortfolioOptimizer):
    def optimize_with_constraints(self, constraints_dict):
        """
        Optimize portfolio with various constraints
        """
        def objective(w):
            return np.dot(w, np.dot(self.cov, w))

        scipy_constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        ]

        bounds = []

        # Maximum single position
        max_position = constraints_dict.get('max_position', 0.20)
        for i in range(self.n_assets):
            bounds.append((0, max_position))

        # Sector constraints
        if 'sector_limits' in constraints_dict:
            for sector, limit in constraints_dict['sector_limits'].items():
                sector_indices = self.get_sector_indices(sector)
                scipy_constraints.append({
                    'type': 'ineq',
                    'fun': lambda w: limit - np.sum(w[sector_indices])
                })

        # Turnover constraint
        if 'max_turnover' in constraints_dict:
            scipy_constraints.append({
                'type': 'ineq',
                'fun': lambda w: constraints_dict['max_turnover'] -
                       np.sum(np.abs(w - self.current_weights))
            })

        # Liquidity constraint
        if 'min_size' in constraints_dict:
            min_size = constraints_dict['min_size']
            for i, size in enumerate(self.market_sizes):
                max_weight = min_size / size
                bounds[i] = (bounds[i][0], min(max_weight, bounds[i][1]))

        init_guess = np.array([1/self.n_assets] * self.n_assets)
        result = minimize(objective, init_guess, method='SLSQP',
                         bounds=bounds, constraints=scipy_constraints)

        return result.x
```

## Risk Parity Approach

### Concept

Equal risk contribution from all asset classes:

```python
def risk_parity_allocation(cov_matrix, risk_budget=None):
    """
    Allocate weights so each asset contributes equally to portfolio risk
    """
    if risk_budget is None:
        risk_budget = np.ones(len(cov_matrix)) / len(cov_matrix)

    def objective(w):
        portfolio_vol = np.sqrt(w @ cov_matrix @ w)
        marginal_contrib = (cov_matrix @ w) / portfolio_vol
        risk_contrib = w * marginal_contrib

        # Minimize squared deviations from target risk contribution
        return np.sum((risk_contrib - risk_budget) ** 2)

    init_guess = np.ones(len(cov_matrix)) / len(cov_matrix)
    bounds = tuple((0, 1) for _ in range(len(cov_matrix)))
    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}

    result = minimize(objective, init_guess, method='SLSQP',
                     bounds=bounds, constraints=constraints)

    return result.x
```

## Smart Beta and Factor-Based Optimization

### Factor Allocation

```python
class FactorOptimizer:
    def __init__(self, factor_returns, factor_cov):
        self.factor_mu = factor_returns
        self.factor_cov = factor_cov
        self.factors = ['value', 'momentum', 'quality', 'low_volatility']

    def optimize_factor_tilts(self, base_allocation, overweights):
        """
        Optimize tilts to factors while maintaining core exposure
        """
        # Base allocation (e.g., market cap)
        weights = base_allocation.copy()

        # Apply factor tilts
        for factor, tilt in overweights.items():
            factor_idx = self.factors.index(factor)
            # Increase exposure to factor
            # (implementation details depend on portfolio structure)

        return weights

    def calculate_factor_exposures(self, holdings_factor_betas):
        """
        Calculate portfolio's exposure to each factor
        """
        exposures = {}

        for factor in self.factors:
            betas = [holdings_factor_betas[h][factor] for h in holdings]
            weights = self.get_weights()

            exposure = np.sum(np.array(betas) * np.array(weights))
            exposures[factor] = exposure

        return exposures
```

## Robust Optimization

### Minimize Worst-Case Returns

```python
def robust_optimization(expected_returns, cov_matrix, uncertainty_set_size):
    """
    Optimize portfolio to handle uncertainty in returns estimation
    """
    def objective(w):
        # Minimize worst-case return (conservative)
        worst_case_return = np.min(w @ expected_returns)
        return -worst_case_return

    n_assets = len(expected_returns)
    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    bounds = tuple((0, 1) for _ in range(n_assets))
    init_guess = np.ones(n_assets) / n_assets

    result = minimize(objective, init_guess, method='SLSQP',
                     bounds=bounds, constraints=constraints)

    return result.x
```

## Goal-Based Optimization

### Multiple Goal Optimization

```python
def optimize_multiple_goals(goals, total_wealth):
    """
    Allocate portfolio to maximize probability of achieving all goals
    """
    # For each goal:
    # - Calculate required allocation
    # - Run Monte Carlo simulation
    # - Calculate probability of success

    total_allocation = {}
    remaining_wealth = total_wealth

    # Sort goals by priority
    sorted_goals = sorted(goals, key=lambda g: g['priority'], reverse=True)

    for goal in sorted_goals:
        # Allocate funds needed for goal
        needed = goal['amount_needed']
        allocation_for_goal = allocate_for_goal(needed, goal['years_to_goal'])

        total_allocation[goal['name']] = allocation_for_goal
        remaining_wealth -= needed

    return total_allocation
```

## Optimization Challenges and Solutions

### Challenge 1: Estimation Error

```python
def shrinkage_estimation(sample_mean, target_mean, shrinkage_coefficient):
    """
    Shrinkage reduces impact of estimation errors
    """
    shrunk_mean = (1 - shrinkage_coefficient) * sample_mean + \
                  shrinkage_coefficient * target_mean

    return shrunk_mean
```

### Challenge 2: Optimization Instability

```python
def robust_optimization_pipeline(returns_data):
    """
    Stabilize optimization through multiple methods
    """
    # 1. Shrink covariance matrix
    cov_matrix = shrink_covariance(returns_data)

    # 2. Use constraints to prevent extreme positions
    constraints = add_position_limits(max_single=0.10)

    # 3. Include transaction cost penalties
    objective = mean_variance_with_costs(cov_matrix, transaction_costs)

    # 4. Stress test across scenarios
    weights = optimize_with_constraints(objective, constraints)

    return weights
```

### Challenge 3: Parameter Sensitivity

```python
def sensitivity_analysis(optimal_weights, expected_returns, cov_matrix):
    """
    Test allocation sensitivity to parameter changes
    """
    sensitivities = {}

    # Test 1%  change in returns
    for i in range(len(expected_returns)):
        perturbed_returns = expected_returns.copy()
        perturbed_returns[i] += 0.01

        new_weights = optimize(perturbed_returns, cov_matrix)
        sensitivity = np.sum(np.abs(new_weights - optimal_weights))
        sensitivities[f'return_{i}'] = sensitivity

    return sensitivities
```

## Best Practices

1. **Include Constraints**: Practical optimization requires constraints
2. **Stress Test**: Verify robustness across scenarios
3. **Monitor Implementation**: Compare actual to theoretical
4. **Rebalance Regularly**: Drift away from optimization over time
5. **Update Assumptions**: Refresh estimates periodically
6. **Avoid Overfitting**: Don't optimize to noise
7. **Document Rationale**: Explain optimization choices
8. **Simplify When Possible**: Simpler allocations often work well

## Conclusion

Portfolio optimization combines mathematical theory with practical constraints to construct efficient portfolios. While optimization can improve outcomes, disciplined implementation and regular monitoring are equally important.

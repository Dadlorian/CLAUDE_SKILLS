#!/usr/bin/env python3
"""
Statistical Analysis Examples for Research Methodologies
Comprehensive implementation of common statistical tests and workflows
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.power import TTestIndPower, FTestAnovaPower
import matplotlib.pyplot as plt
import seaborn as sns

# Set random seed for reproducibility
np.random.seed(42)

# ============================================================================
# SECTION 1: POWER ANALYSIS
# ============================================================================

def calculate_sample_size_ttest(effect_size=0.5, alpha=0.05, power=0.80):
    """
    Calculate required sample size for independent t-test

    Parameters:
    -----------
    effect_size : float
        Cohen's d effect size (0.2=small, 0.5=medium, 0.8=large)
    alpha : float
        Significance level (default 0.05)
    power : float
        Desired statistical power (default 0.80)

    Returns:
    --------
    dict : Sample size requirements per group
    """
    analysis = TTestIndPower()
    n_per_group = analysis.solve_power(
        effect_size=effect_size,
        alpha=alpha,
        power=power,
        ratio=1.0,
        alternative='two-sided'
    )

    return {
        'n_per_group': int(np.ceil(n_per_group)),
        'total_n': int(np.ceil(n_per_group * 2)),
        'effect_size': effect_size,
        'alpha': alpha,
        'power': power
    }

def calculate_sample_size_anova(num_groups=3, effect_size=0.25, alpha=0.05, power=0.80):
    """Calculate required sample size for one-way ANOVA"""
    analysis = FTestAnovaPower()
    n_per_group = analysis.solve_power(
        effect_size=effect_size,
        nobs=None,
        alpha=alpha,
        power=power,
        k_groups=num_groups
    )

    return {
        'n_per_group': int(np.ceil(n_per_group)),
        'total_n': int(np.ceil(n_per_group * num_groups)),
        'num_groups': num_groups,
        'effect_size': effect_size,
        'alpha': alpha,
        'power': power
    }

# ============================================================================
# SECTION 2: COMMON STATISTICAL TESTS
# ============================================================================

def independent_ttest_analysis(group1, group2, var_equal=True):
    """
    Perform independent samples t-test with effect size and CI

    Returns comprehensive results including:
    - Test statistic, p-value, degrees of freedom
    - Cohen's d effect size
    - 95% confidence interval
    - Descriptive statistics
    """
    # Descriptive statistics
    desc = {
        'group1_mean': np.mean(group1),
        'group1_sd': np.std(group1, ddof=1),
        'group1_n': len(group1),
        'group2_mean': np.mean(group2),
        'group2_sd': np.std(group2, ddof=1),
        'group2_n': len(group2)
    }

    # T-test
    t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=var_equal)
    df = len(group1) + len(group2) - 2

    # Cohen's d effect size
    pooled_sd = np.sqrt(((len(group1) - 1) * np.var(group1, ddof=1) +
                          (len(group2) - 1) * np.var(group2, ddof=1)) / df)
    cohens_d = (np.mean(group1) - np.mean(group2)) / pooled_sd

    # 95% Confidence Interval
    mean_diff = np.mean(group1) - np.mean(group2)
    se = pooled_sd * np.sqrt(1/len(group1) + 1/len(group2))
    t_crit = stats.t.ppf(0.975, df)
    ci_lower = mean_diff - t_crit * se
    ci_upper = mean_diff + t_crit * se

    return {
        **desc,
        't_statistic': t_stat,
        'p_value': p_value,
        'df': df,
        'cohens_d': cohens_d,
        'mean_difference': mean_diff,
        'ci_95_lower': ci_lower,
        'ci_95_upper': ci_upper,
        'interpretation': interpret_pvalue(p_value)
    }

def one_way_anova_analysis(data, group_col, value_col):
    """
    Perform one-way ANOVA with post-hoc tests

    Parameters:
    -----------
    data : pandas DataFrame
    group_col : str
        Column name for grouping variable
    value_col : str
        Column name for dependent variable

    Returns:
    --------
    dict : ANOVA results, effect sizes, post-hoc comparisons
    """
    # Prepare data
    groups = [data[data[group_col] == group][value_col].values
              for group in data[group_col].unique()]

    # One-way ANOVA
    f_stat, p_value = stats.f_oneway(*groups)

    # Calculate eta squared (effect size)
    group_means = [np.mean(g) for g in groups]
    grand_mean = np.mean(data[value_col])
    ss_between = sum([len(g) * (np.mean(g) - grand_mean)**2 for g in groups])
    ss_total = sum([(x - grand_mean)**2 for g in groups for x in g])
    eta_squared = ss_between / ss_total

    # Post-hoc Tukey HSD (if significant)
    posthoc_results = None
    if p_value < 0.05:
        from statsmodels.stats.multicomp import pairwise_tukeyhsd
        posthoc = pairwise_tukeyhsd(data[value_col], data[group_col], alpha=0.05)
        posthoc_results = str(posthoc)

    return {
        'f_statistic': f_stat,
        'p_value': p_value,
        'eta_squared': eta_squared,
        'df_between': len(groups) - 1,
        'df_within': len(data) - len(groups),
        'num_groups': len(groups),
        'posthoc_results': posthoc_results,
        'interpretation': interpret_pvalue(p_value)
    }

def correlation_analysis(x, y, method='pearson'):
    """
    Calculate correlation with confidence intervals

    Parameters:
    -----------
    x, y : array-like
        Variables to correlate
    method : str
        'pearson', 'spearman', or 'kendall'

    Returns:
    --------
    dict : Correlation coefficient, p-value, CI
    """
    if method == 'pearson':
        r, p = stats.pearsonr(x, y)
    elif method == 'spearman':
        r, p = stats.spearmanr(x, y)
    elif method == 'kendall':
        r, p = stats.kendalltau(x, y)

    # Fisher's z transformation for CI (Pearson only)
    if method == 'pearson':
        n = len(x)
        z = np.arctanh(r)
        se = 1 / np.sqrt(n - 3)
        z_crit = stats.norm.ppf(0.975)
        ci_lower = np.tanh(z - z_crit * se)
        ci_upper = np.tanh(z + z_crit * se)
    else:
        ci_lower, ci_upper = None, None

    return {
        'correlation': r,
        'p_value': p,
        'method': method,
        'n': len(x),
        'ci_95_lower': ci_lower,
        'ci_95_upper': ci_upper,
        'interpretation': interpret_correlation(r)
    }

# ============================================================================
# SECTION 3: LINEAR REGRESSION
# ============================================================================

def multiple_regression_analysis(data, formula):
    """
    Perform multiple linear regression with diagnostics

    Parameters:
    -----------
    data : pandas DataFrame
    formula : str
        R-style formula, e.g., 'y ~ x1 + x2 + x3'

    Returns:
    --------
    dict : Regression results, diagnostics, assumptions tests
    """
    # Fit model
    model = ols(formula, data=data).fit()

    # Assumptions testing
    residuals = model.resid
    fitted = model.fittedvalues

    # Normality test (Shapiro-Wilk)
    shapiro_stat, shapiro_p = stats.shapiro(residuals)

    # Homoscedasticity test (Breusch-Pagan)
    from statsmodels.stats.diagnostic import het_breuschpagan
    bp_test = het_breuschpagan(residuals, model.model.exog)

    # Multicollinearity (VIF)
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    vif_data = pd.DataFrame()
    vif_data["Variable"] = model.model.exog_names[1:]  # Exclude intercept
    vif_data["VIF"] = [variance_inflation_factor(model.model.exog, i)
                       for i in range(1, model.model.exog.shape[1])]

    return {
        'r_squared': model.rsquared,
        'adj_r_squared': model.rsquared_adj,
        'f_statistic': model.fvalue,
        'f_pvalue': model.f_pvalue,
        'aic': model.aic,
        'bic': model.bic,
        'coefficients': model.params.to_dict(),
        'p_values': model.pvalues.to_dict(),
        'conf_int': model.conf_int().to_dict(),
        'normality_test_p': shapiro_p,
        'homoscedasticity_test_p': bp_test[1],
        'vif': vif_data.to_dict('records'),
        'summary': str(model.summary())
    }

# ============================================================================
# SECTION 4: SURVIVAL ANALYSIS
# ============================================================================

def kaplan_meier_analysis(durations, events, groups=None):
    """
    Kaplan-Meier survival analysis with log-rank test

    Parameters:
    -----------
    durations : array-like
        Time to event or censoring
    events : array-like
        1 if event occurred, 0 if censored
    groups : array-like, optional
        Group labels for comparison

    Returns:
    --------
    dict : Survival estimates, median survival, log-rank test
    """
    from lifelines import KaplanMeierFitter
    from lifelines.statistics import logrank_test

    kmf = KaplanMeierFitter()
    kmf.fit(durations, events)

    results = {
        'median_survival': kmf.median_survival_time_,
        'survival_function': kmf.survival_function_.to_dict(),
        'confidence_intervals': {
            'lower': kmf.confidence_interval_['KM_estimate_lower_0.95'].to_dict(),
            'upper': kmf.confidence_interval_['KM_estimate_upper_0.95'].to_dict()
        }
    }

    # If groups provided, perform log-rank test
    if groups is not None:
        unique_groups = np.unique(groups)
        if len(unique_groups) == 2:
            group1_mask = groups == unique_groups[0]
            group2_mask = groups == unique_groups[1]

            logrank = logrank_test(
                durations[group1_mask], durations[group2_mask],
                events[group1_mask], events[group2_mask]
            )

            results['logrank_statistic'] = logrank.test_statistic
            results['logrank_pvalue'] = logrank.p_value

    return results

# ============================================================================
# SECTION 5: UTILITY FUNCTIONS
# ============================================================================

def interpret_pvalue(p, alpha=0.05):
    """Interpret p-value"""
    if p < 0.001:
        return "p < .001 (highly significant)"
    elif p < alpha:
        return f"p = {p:.3f} (significant at α={alpha})"
    else:
        return f"p = {p:.3f} (not significant)"

def interpret_correlation(r):
    """Interpret correlation coefficient"""
    abs_r = abs(r)
    if abs_r < 0.1:
        strength = "negligible"
    elif abs_r < 0.3:
        strength = "weak"
    elif abs_r < 0.5:
        strength = "moderate"
    elif abs_r < 0.7:
        strength = "strong"
    else:
        strength = "very strong"

    direction = "positive" if r > 0 else "negative"
    return f"{strength} {direction} correlation (r = {r:.3f})"

def check_assumptions_ttest(group1, group2):
    """
    Check assumptions for independent t-test
    Returns normality and homogeneity of variance tests
    """
    # Normality tests (Shapiro-Wilk)
    _, norm_p1 = stats.shapiro(group1)
    _, norm_p2 = stats.shapiro(group2)

    # Homogeneity of variance (Levene's test)
    _, levene_p = stats.levene(group1, group2)

    return {
        'group1_normality_p': norm_p1,
        'group2_normality_p': norm_p2,
        'homogeneity_variance_p': levene_p,
        'assumptions_met': all([norm_p1 > 0.05, norm_p2 > 0.05, levene_p > 0.05]),
        'recommendations': get_test_recommendations(norm_p1, norm_p2, levene_p)
    }

def get_test_recommendations(norm_p1, norm_p2, levene_p):
    """Recommend appropriate statistical test based on assumptions"""
    if norm_p1 < 0.05 or norm_p2 < 0.05:
        return "Non-normal data: Consider Mann-Whitney U test (non-parametric)"
    elif levene_p < 0.05:
        return "Unequal variances: Use Welch's t-test (equal_var=False)"
    else:
        return "Assumptions met: Standard independent t-test appropriate"

# ============================================================================
# SECTION 6: COMPLETE EXAMPLE WORKFLOW
# ============================================================================

def complete_rct_analysis_example():
    """
    Complete example: Analyze results from a randomized controlled trial
    comparing a new drug vs placebo on blood pressure reduction
    """
    # Generate simulated RCT data
    np.random.seed(42)
    n_per_group = 50

    # Treatment group: mean reduction of 15 mmHg, SD=10
    treatment = np.random.normal(15, 10, n_per_group)

    # Placebo group: mean reduction of 5 mmHg, SD=10
    placebo = np.random.normal(5, 10, n_per_group)

    # Create DataFrame
    data = pd.DataFrame({
        'group': ['treatment']*n_per_group + ['placebo']*n_per_group,
        'bp_reduction': np.concatenate([treatment, placebo])
    })

    print("=" * 80)
    print("RANDOMIZED CONTROLLED TRIAL ANALYSIS")
    print("=" * 80)
    print("\nStudy: New antihypertensive drug vs placebo")
    print(f"Sample size: {n_per_group} per group (total N={n_per_group*2})")
    print("\nPrimary outcome: Change in systolic BP (mmHg) at 12 weeks")

    # Step 1: Descriptive statistics
    print("\n" + "="*80)
    print("1. DESCRIPTIVE STATISTICS")
    print("="*80)
    desc = data.groupby('group')['bp_reduction'].describe()
    print(desc)

    # Step 2: Check assumptions
    print("\n" + "="*80)
    print("2. ASSUMPTION TESTING")
    print("="*80)
    assumptions = check_assumptions_ttest(treatment, placebo)
    print(f"Treatment group normality: p = {assumptions['group1_normality_p']:.4f}")
    print(f"Placebo group normality: p = {assumptions['group2_normality_p']:.4f}")
    print(f"Homogeneity of variance: p = {assumptions['homogeneity_variance_p']:.4f}")
    print(f"\nAssumptions met: {assumptions['assumptions_met']}")
    print(f"Recommendation: {assumptions['recommendations']}")

    # Step 3: Primary analysis
    print("\n" + "="*80)
    print("3. PRIMARY ANALYSIS (Independent t-test)")
    print("="*80)
    results = independent_ttest_analysis(treatment, placebo)
    print(f"\nMean difference: {results['mean_difference']:.2f} mmHg")
    print(f"95% CI: [{results['ci_95_lower']:.2f}, {results['ci_95_upper']:.2f}]")
    print(f"t({results['df']}) = {results['t_statistic']:.3f}, {results['interpretation']}")
    print(f"Cohen's d = {results['cohens_d']:.3f} (effect size)")

    # Step 4: Interpretation
    print("\n" + "="*80)
    print("4. CLINICAL INTERPRETATION")
    print("="*80)
    print(f"The new drug reduced systolic BP by {results['mean_difference']:.1f} mmHg")
    print(f"more than placebo (95% CI: {results['ci_95_lower']:.1f} to {results['ci_95_upper']:.1f} mmHg).")
    print(f"This difference is statistically significant ({results['interpretation']})")
    print(f"with a large effect size (Cohen's d = {results['cohens_d']:.2f}).")

    if results['ci_95_lower'] > 0:
        print("\nConclusion: The new drug is effective for reducing blood pressure.")

    # Step 5: Power analysis for future studies
    print("\n" + "="*80)
    print("5. POST-HOC POWER ANALYSIS")
    print("="*80)
    observed_effect = results['cohens_d']
    power_results = calculate_sample_size_ttest(
        effect_size=observed_effect,
        alpha=0.05,
        power=0.80
    )
    print(f"Observed effect size: d = {observed_effect:.3f}")
    print(f"For 80% power to detect this effect in future studies:")
    print(f"  Required sample size: {power_results['n_per_group']} per group")
    print(f"  Total N = {power_results['total_n']}")

    return data, results

# ============================================================================
# RUN EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Run complete example
    data, results = complete_rct_analysis_example()

    # Additional examples
    print("\n\n" + "="*80)
    print("ADDITIONAL EXAMPLES")
    print("="*80)

    # Example 1: Power analysis
    print("\nExample 1: Power Analysis for Planning Study")
    power = calculate_sample_size_ttest(effect_size=0.5, alpha=0.05, power=0.90)
    print(f"  Effect size: Cohen's d = 0.5 (medium)")
    print(f"  Alpha: 0.05, Power: 0.90")
    print(f"  Required N: {power['n_per_group']} per group (total: {power['total_n']})")

    # Example 2: ANOVA
    print("\nExample 2: One-Way ANOVA (3 groups)")
    anova_power = calculate_sample_size_anova(num_groups=3, effect_size=0.25, power=0.80)
    print(f"  Effect size: f = 0.25")
    print(f"  Number of groups: 3")
    print(f"  Required N: {anova_power['n_per_group']} per group (total: {anova_power['total_n']})")

    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80)

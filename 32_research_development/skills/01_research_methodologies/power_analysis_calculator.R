#!/usr/bin/env Rscript
# Power Analysis Calculator for Research Design
# Comprehensive implementation using pwr package

library(pwr)
library(ggplot2)

# ==============================================================================
# T-TEST POWER ANALYSIS
# ==============================================================================

#' Calculate sample size for independent t-test
#'
#' @param effect_size Cohen's d effect size
#' @param alpha Significance level (default 0.05)
#' @param power Desired statistical power (default 0.80)
#' @param type Test type: "two.sample", "one.sample", "paired"
#' @return List with sample size requirements
calculate_ttest_sample_size <- function(effect_size = 0.5,
                                        alpha = 0.05,
                                        power = 0.80,
                                        type = "two.sample") {
  result <- pwr.t.test(
    d = effect_size,
    sig.level = alpha,
    power = power,
    type = type,
    alternative = "two.sided"
  )

  list(
    n_per_group = ceiling(result$n),
    total_n = ceiling(result$n * 2),
    effect_size = effect_size,
    alpha = alpha,
    power = power,
    type = type
  )
}

#' Plot power curve for t-test
plot_ttest_power_curve <- function(effect_size = 0.5, alpha = 0.05) {
  sample_sizes <- seq(10, 200, by = 5)
  powers <- sapply(sample_sizes, function(n) {
    pwr.t.test(n = n, d = effect_size, sig.level = alpha,
               type = "two.sample")$power
  })

  df <- data.frame(sample_size = sample_sizes, power = powers)

  ggplot(df, aes(x = sample_size, y = power)) +
    geom_line(color = "blue", size = 1.2) +
    geom_hline(yintercept = 0.80, linetype = "dashed", color = "red") +
    geom_hline(yintercept = 0.90, linetype = "dashed", color = "darkred") +
    labs(
      title = sprintf("Power Analysis: t-test (d = %.2f, α = %.2f)",
                     effect_size, alpha),
      x = "Sample Size per Group",
      y = "Statistical Power",
      caption = "Red dashed lines: 80% and 90% power thresholds"
    ) +
    theme_minimal() +
    theme(plot.title = element_text(hjust = 0.5, face = "bold"))
}

# ==============================================================================
# ANOVA POWER ANALYSIS
# ==============================================================================

#' Calculate sample size for one-way ANOVA
#'
#' @param num_groups Number of groups to compare
#' @param effect_size Cohen's f effect size
#' @param alpha Significance level
#' @param power Desired statistical power
#' @return List with sample size requirements
calculate_anova_sample_size <- function(num_groups = 3,
                                        effect_size = 0.25,
                                        alpha = 0.05,
                                        power = 0.80) {
  result <- pwr.anova.test(
    k = num_groups,
    f = effect_size,
    sig.level = alpha,
    power = power
  )

  list(
    n_per_group = ceiling(result$n),
    total_n = ceiling(result$n * num_groups),
    num_groups = num_groups,
    effect_size = effect_size,
    alpha = alpha,
    power = power
  )
}

# ==============================================================================
# CORRELATION POWER ANALYSIS
# ==============================================================================

#' Calculate sample size for correlation
#'
#' @param correlation_coef Expected correlation coefficient
#' @param alpha Significance level
#' @param power Desired statistical power
#' @return List with sample size requirements
calculate_correlation_sample_size <- function(correlation_coef = 0.3,
                                             alpha = 0.05,
                                             power = 0.80) {
  result <- pwr.r.test(
    r = correlation_coef,
    sig.level = alpha,
    power = power,
    alternative = "two.sided"
  )

  list(
    total_n = ceiling(result$n),
    correlation = correlation_coef,
    alpha = alpha,
    power = power
  )
}

# ==============================================================================
# PROPORTION TEST POWER ANALYSIS
# ==============================================================================

#' Calculate sample size for two-proportion test
#'
#' @param p1 Proportion in group 1
#' @param p2 Proportion in group 2
#' @param alpha Significance level
#' @param power Desired statistical power
#' @return List with sample size requirements
calculate_proportion_sample_size <- function(p1 = 0.5, p2 = 0.7,
                                            alpha = 0.05, power = 0.80) {
  # Effect size (h) for proportions
  effect_size <- ES.h(p1, p2)

  result <- pwr.2p.test(
    h = effect_size,
    sig.level = alpha,
    power = power,
    alternative = "two.sided"
  )

  list(
    n_per_group = ceiling(result$n),
    total_n = ceiling(result$n * 2),
    p1 = p1,
    p2 = p2,
    effect_size_h = effect_size,
    alpha = alpha,
    power = power
  )
}

# ==============================================================================
# CHI-SQUARE TEST POWER ANALYSIS
# ==============================================================================

#' Calculate sample size for chi-square test
#'
#' @param w Effect size (Cohen's w)
#' @param df Degrees of freedom
#' @param alpha Significance level
#' @param power Desired statistical power
#' @return List with sample size requirements
calculate_chisq_sample_size <- function(w = 0.3, df = 1,
                                       alpha = 0.05, power = 0.80) {
  result <- pwr.chisq.test(
    w = w,
    df = df,
    sig.level = alpha,
    power = power
  )

  list(
    total_n = ceiling(result$N),
    effect_size_w = w,
    df = df,
    alpha = alpha,
    power = power
  )
}

# ==============================================================================
# EFFECT SIZE CALCULATORS
# ==============================================================================

#' Calculate Cohen's d from means and SDs
#'
#' @param mean1 Mean of group 1
#' @param mean2 Mean of group 2
#' @param sd1 Standard deviation of group 1
#' @param sd2 Standard deviation of group 2
#' @return Cohen's d effect size
calculate_cohens_d <- function(mean1, mean2, sd1, sd2) {
  # Pooled standard deviation
  pooled_sd <- sqrt((sd1^2 + sd2^2) / 2)

  # Cohen's d
  d <- (mean1 - mean2) / pooled_sd

  # Interpretation
  interpretation <- if (abs(d) < 0.2) {
    "negligible"
  } else if (abs(d) < 0.5) {
    "small"
  } else if (abs(d) < 0.8) {
    "medium"
  } else {
    "large"
  }

  list(
    cohens_d = d,
    interpretation = interpretation
  )
}

#' Calculate Cohen's f from ANOVA
#'
#' @param ss_between Sum of squares between groups
#' @param ss_within Sum of squares within groups
#' @return Cohen's f effect size
calculate_cohens_f <- function(ss_between, ss_within) {
  eta_squared <- ss_between / (ss_between + ss_within)
  f <- sqrt(eta_squared / (1 - eta_squared))

  list(
    cohens_f = f,
    eta_squared = eta_squared,
    interpretation = if (f < 0.1) "small" else if (f < 0.25) "medium" else "large"
  )
}

# ==============================================================================
# COMPREHENSIVE POWER ANALYSIS REPORT
# ==============================================================================

#' Generate comprehensive power analysis report
#'
#' @param study_design Type of study ("ttest", "anova", "correlation", "proportion")
#' @param effect_size Expected effect size
#' @param ... Additional parameters specific to study design
generate_power_report <- function(study_design = "ttest", effect_size = 0.5, ...) {
  cat("================================================================================\n")
  cat("POWER ANALYSIS REPORT\n")
  cat("================================================================================\n\n")

  if (study_design == "ttest") {
    results <- calculate_ttest_sample_size(effect_size = effect_size, ...)
    cat("Study Design: Independent Samples t-test\n")
    cat(sprintf("Effect Size: Cohen's d = %.2f\n", results$effect_size))
    cat(sprintf("Significance Level: α = %.2f\n", results$alpha))
    cat(sprintf("Desired Power: %.0f%%\n", results$power * 100))
    cat("\nRESULTS:\n")
    cat(sprintf("  Sample size per group: %d\n", results$n_per_group))
    cat(sprintf("  Total sample size: %d\n", results$total_n))
    cat("\nRECOMMENDATION:\n")
    cat(sprintf("  Recruit %d participants per group (total N = %d)\n",
                results$n_per_group, results$total_n))
    cat(sprintf("  Account for ~10%% dropout: %d per group (total N = %d)\n",
                ceiling(results$n_per_group * 1.1),
                ceiling(results$total_n * 1.1)))

  } else if (study_design == "anova") {
    results <- calculate_anova_sample_size(effect_size = effect_size, ...)
    cat("Study Design: One-Way ANOVA\n")
    cat(sprintf("Effect Size: Cohen's f = %.2f\n", results$effect_size))
    cat(sprintf("Number of Groups: %d\n", results$num_groups))
    cat(sprintf("Significance Level: α = %.2f\n", results$alpha))
    cat(sprintf("Desired Power: %.0f%%\n", results$power * 100))
    cat("\nRESULTS:\n")
    cat(sprintf("  Sample size per group: %d\n", results$n_per_group))
    cat(sprintf("  Total sample size: %d\n", results$total_n))

  } else if (study_design == "correlation") {
    results <- calculate_correlation_sample_size(correlation_coef = effect_size, ...)
    cat("Study Design: Correlation Analysis\n")
    cat(sprintf("Expected Correlation: r = %.2f\n", results$correlation))
    cat(sprintf("Significance Level: α = %.2f\n", results$alpha))
    cat(sprintf("Desired Power: %.0f%%\n", results$power * 100))
    cat("\nRESULTS:\n")
    cat(sprintf("  Total sample size: %d\n", results$total_n))
  }

  cat("\n================================================================================\n")
}

# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

if (!interactive()) {
  # Example 1: Independent t-test
  cat("\n\nEXAMPLE 1: INDEPENDENT T-TEST\n")
  generate_power_report(study_design = "ttest", effect_size = 0.5,
                       alpha = 0.05, power = 0.80)

  # Example 2: One-way ANOVA
  cat("\n\nEXAMPLE 2: ONE-WAY ANOVA (3 GROUPS)\n")
  generate_power_report(study_design = "anova", effect_size = 0.25,
                       num_groups = 3, alpha = 0.05, power = 0.80)

  # Example 3: Correlation
  cat("\n\nEXAMPLE 3: CORRELATION ANALYSIS\n")
  generate_power_report(study_design = "correlation", effect_size = 0.3,
                       alpha = 0.05, power = 0.80)

  # Example 4: Calculate Cohen's d from published data
  cat("\n\nEXAMPLE 4: CALCULATE COHEN'S D FROM MEANS/SDs\n")
  cat("Published study: Group 1 (M=50, SD=10), Group 2 (M=45, SD=12)\n")
  effect <- calculate_cohens_d(mean1 = 50, mean2 = 45, sd1 = 10, sd2 = 12)
  cat(sprintf("Cohen's d = %.3f (%s effect)\n", effect$cohens_d, effect$interpretation))

  # Use this effect size for power analysis
  results <- calculate_ttest_sample_size(effect_size = abs(effect$cohens_d), power = 0.90)
  cat(sprintf("\nFor 90%% power to replicate this finding:\n"))
  cat(sprintf("  Need %d per group (total N = %d)\n",
              results$n_per_group, results$total_n))
}

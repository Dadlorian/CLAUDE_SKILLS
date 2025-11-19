# Funnel Optimization Guide

## Overview
Step-by-step guide to analyzing and optimizing conversion funnels.

## Step 1: Map Your Funnel
Identify critical path steps from entry to conversion.

## Step 2: Measure Baseline
```sql
SELECT
    funnel_step,
    COUNT(DISTINCT user_id) as users,
    conversion_rate
FROM funnel_analysis
GROUP BY 1 ORDER BY step_order;
```

## Step 3: Identify Drop-off Points
Focus optimization on steps with >25% drop-off.

## Step 4: Hypothesis Generation
- Technical issues?
- UX friction?
- Missing information?
- Trust signals needed?

## Step 5: A/B Test Improvements
Test changes on high-impact steps first.

## Step 6: Monitor & Iterate
Track funnel metrics daily, iterate based on data.

## Tools
- Amplitude, Mixpanel for funnel analysis
- Hotjar, FullStory for session replay
- Optimizely for A/B testing

## Success Metrics
- Overall conversion rate improvement
- Reduced drop-off at key steps
- Faster time-to-convert

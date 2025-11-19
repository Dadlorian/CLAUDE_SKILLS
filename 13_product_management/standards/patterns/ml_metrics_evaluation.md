# ML Metrics and Evaluation: Comprehensive Framework for Model Assessment

## Table of Contents

1. [Introduction](#introduction)
2. [Evaluation Fundamentals](#fundamentals)
3. [Classification Metrics](#classification)
4. [Regression Metrics](#regression)
5. [Ranking Metrics](#ranking)
6. [Generation Metrics](#generation)
7. [Fairness and Bias Metrics](#fairness)
8. [Offline vs. Online Evaluation](#offline-online)
9. [A/B Testing for ML Models](#ab-testing)
10. [Monitoring and Production Metrics](#monitoring)
11. [Real-World Examples](#examples)

---

## Introduction

Evaluating machine learning models is fundamentally different from evaluating software. A function either returns the correct answer or it doesn't, but ML models return probabilistic predictions that may be "good enough" even if not perfect.

### Why Metrics Matter

**Traditional Software**: Binary - works or doesn't work

**ML Models**: Probabilistic - may be 85% accurate, have bias against certain groups, take 2 seconds to respond

A PM must understand how to balance competing metrics:
- **Accuracy vs. Fairness**: High accuracy but biased against minorities
- **Accuracy vs. Latency**: More accurate but slower
- **Precision vs. Recall**: Catch all bad things or minimize false alarms?
- **Business Impact vs. Technical Metrics**: Revenue earned vs. F1 score

### Levels of Evaluation

**Level 1: Offline Metrics**
- Evaluate on test dataset
- Cheap, fast, repeatable
- May not reflect real-world performance

**Level 2: Online Testing**
- Shadow mode (run model without affecting users)
- Canary deployment (small user fraction)
- Measure real user behavior

**Level 3: Business Metrics**
- Revenue, retention, satisfaction
- What actually matters for business
- Hardest to measure, most important

---

## Evaluation Fundamentals

### Train, Validation, Test Split

**Why Separate Splits?**

```
Training Set (60%):
- Data model learns from
- Model optimizes on this data
- Cannot evaluate on this (will overfit)

Validation Set (20%):
- Data to tune hyperparameters
- Used to pick learning rate, model complexity, etc.
- Cannot evaluate on this (will overfit to tuning)

Test Set (20%):
- Held out, never seen during training
- Truly independent evaluation
- Tells us how model will perform in production
```

**Distribution Matters**:
```
Good Split:
- Each set has similar distribution
- All sets are representative of production
- Classes balanced similarly across sets

Bad Split:
- Training: 90% class A, 10% class B
- Test: 50% class A, 50% class B
- Metrics will be misleading
```

### Cross-Validation

**Problem**: Small datasets, want to use data efficiently

**Solution**: Cross-validation

```
5-Fold Cross-Validation:

1. Split data into 5 equal parts
2. Fold 1: Train on 4 parts, test on 1
   Fold 2: Train on different 4 parts, test on different 1
   Fold 3-5: Repeat

3. Average performance across folds
4. Get estimate of variance
```

**When to Use**:
- Small datasets (<10K examples)
- Limited computing (can't afford multiple models)
- Want confidence in metrics

**When Not to Use**:
- Large datasets (test set is sufficient)
- Time-series data (fold may not respect time order)
- Very expensive to train

### Data Leakage

**Problem**: Information from test set leaks into training, making metrics unrealistically optimistic

**Examples**:
```
Bad Practice 1: Feature Scaling
Train Set Scaler → Fit on ALL data (including test)
Result: Test set features optimized, metrics inflated

Good Practice:
Train Set Scaler → Fit only on training set
Apply Scaler → To test set
Result: True evaluation

Bad Practice 2: Feature Selection
Select Features → Based on correlation with target (all data)
Result: Unlucky correlations make it into model

Good Practice:
Select Features → Only from training set
Evaluate → On test set features

Bad Practice 3: Cleaning
Remove Outliers → Based on train + test distributions
Result: Test set is easier

Good Practice:
Define Outliers → From training set
Remove → Same criteria on test set
```

---

## Classification Metrics

### Binary Classification (Yes/No)

**Confusion Matrix**:
```
                Predicted Positive    Predicted Negative
Actual Positive         TP                     FN
Actual Negative         FP                     TN

TP = True Positive (correctly predicted positive)
FP = False Positive (incorrectly predicted positive)
FN = False Negative (incorrectly predicted negative)
TN = True Negative (correctly predicted negative)
```

**Example: Email Spam Detection**
```
Actual: Is email spam?
Predicted: Does model classify as spam?

TP: Model correctly identifies spam
FP: Model incorrectly marks legitimate email as spam (user annoyed)
FN: Model misses spam email (user annoyed)
TN: Model correctly identifies legitimate email
```

#### 1. Accuracy

**Definition**: (TP + TN) / (TP + TN + FP + FN)

Percentage of correct predictions out of all predictions

```
Example:
- 100 emails total
- 95 correct (90 spam correctly identified + 5 legitimate correctly identified)
- Accuracy = 95/100 = 95%

When to Use:
- Classes are balanced
- All errors cost equally

When NOT to Use:
- Classes are imbalanced (90% negative, 10% positive)
- False positives and negatives have different costs
- Accuracy can be misleading (always predict majority class)
```

**Example**:
If 95% of emails are legitimate, a model that classifies everything as legitimate gets 95% accuracy but catches zero spam.

#### 2. Precision

**Definition**: TP / (TP + FP)

Out of all positive predictions, how many are correct?

```
Example: Email Spam
- Model predicts 100 emails as spam
- 80 are actually spam
- Precision = 80 / 100 = 80%

Interpretation:
- If user trusts the spam filter, 20% of flagged emails are false positives
- User might miss legitimate emails
```

**When to Use**:
- False positives are expensive (e.g., blocking legitimate payment)
- Want to minimize users annoyed by false alarms
- High confidence required

#### 3. Recall (Sensitivity)

**Definition**: TP / (TP + FN)

Out of all actual positives, how many did we catch?

```
Example: Email Spam
- 1000 spam emails arrive
- Model catches 800
- Recall = 800 / 1000 = 80%

Interpretation:
- Model misses 200 spam emails (20% false negative rate)
- Some spam gets through
```

**When to Use**:
- False negatives are expensive (missing fraud, cancer diagnosis)
- Want to catch all positives
- Can tolerate some false positives

#### 4. F1 Score

**Definition**: 2 * (Precision * Recall) / (Precision + Recall)

Harmonic mean of precision and recall

```
Precision: 80%, Recall: 80%
F1 = 2 * (0.8 * 0.8) / (0.8 + 0.8) = 80%

Precision: 90%, Recall: 70%
F1 = 2 * (0.9 * 0.7) / (0.9 + 0.7) = 0.789 = 78.9%

Why Harmonic Mean?
- Punishes extreme imbalance
- If one is very low, F1 is low
- Forces balance between precision and recall
```

**When to Use**:
- Want to balance precision and recall
- Classes are imbalanced
- No clear preference for false positives vs. negatives

#### 5. AUC-ROC

**Definition**: Area under Receiver Operating Characteristic curve

Measures how well model ranks positives above negatives

```
ROC Curve:
- X-axis: False Positive Rate (FP / (FP + TN))
- Y-axis: True Positive Rate (TP / (TP + FN))
- Plot threshold from 0 to 1

AUC = Area under curve (0 to 1)
- AUC = 0.5: Random guessing
- AUC = 1.0: Perfect ranking
- AUC = 0.7: Decent model

Example:
- Model scores spam probability: 0-100%
- Threshold 50%: Classify >= 50% as spam
- Threshold 20%: Classify >= 20% as spam (more spam caught, more false positives)
- ROC curve plots this tradeoff
```

**When to Use**:
- Comparing models
- Classes are imbalanced
- Threshold is not yet determined
- Want single number summarizing performance

**When Not to Use**:
- Need to optimize for specific threshold
- False positives and negatives have very different costs

**Example: AUC-ROC Interpretation**
```
AUC = 0.95:
- If you randomly pick one spam and one legitimate email
- Model will rank spam higher 95% of the time
- Excellent model
```

#### 6. Precision-Recall Curve

Alternative to ROC curve, better for imbalanced data

```
Example: Fraud Detection
- 1M transactions, 1% fraud (10k fraudulent)

Model A:
- Precision: 95%, Recall: 50%
- Catches half of fraud, but 95% of flagged transactions are real fraud

Model B:
- Precision: 50%, Recall: 95%
- Catches 95% of fraud, but only half of flagged transactions are fraud

Which is better?
- If cost of missing fraud >> cost of investigating false positives → Model B
- If cost of false positives >> cost of missing fraud → Model A
```

### Multi-Class Classification

When predicting among 3+ classes (e.g., cat/dog/bird)

#### 1. Overall Metrics

```
Macro Average:
- Calculate metric per class
- Average the metrics

Example:
- Class 1 (cat) Precision: 90%
- Class 2 (dog) Precision: 85%
- Class 3 (bird) Precision: 80%
- Macro Precision = (90+85+80)/3 = 85%

Use when: All classes equally important

Weighted Average:
- Same calculation but weight by class frequency

Example:
- Class 1: Precision 90%, 40% of data
- Class 2: Precision 85%, 35% of data
- Class 3: Precision 80%, 25% of data
- Weighted = 90*0.4 + 85*0.35 + 80*0.25 = 86.25%

Use when: Frequent classes more important
```

#### 2. Confusion Matrix (Multi-class)

```
                Cat         Dog        Bird      Predicted
Cat             90          8          2         (Predicted as)
Dog             5           88         7
Bird            3           4          93

Diagonal = correct predictions
Off-diagonal = misclassifications

Patterns:
- If lots of cats predicted as dogs: model confuses these classes
- Indicates where model struggles
```

**Example: GitHub Copilot Language Classification**

```
Actual Language: Python
- 90% predicted Python
- 8% predicted JavaScript (confused with similar syntax)
- 2% predicted Ruby

Insight: Model struggles with Python vs. JavaScript
Action: Add more Python examples to training data
```

---

## Regression Metrics

### For Numeric Predictions

**Example**: Predicting house price

Actual: $500k, Predicted: $480k
Error: $20k

#### 1. Mean Absolute Error (MAE)

**Definition**: Average absolute error

```
Example: Predicting house prices
House 1: Actual $500k, Predicted $480k → Error $20k
House 2: Actual $300k, Predicted $320k → Error $20k
House 3: Actual $800k, Predicted $850k → Error $50k

MAE = (20 + 20 + 50) / 3 = $30k

Interpretation:
- On average, predictions off by $30k
- Easy to interpret (same units as target)
```

**When to Use**:
- Want easy interpretation
- Outliers don't concern you
- Want to punish all errors equally

#### 2. Root Mean Squared Error (RMSE)

**Definition**: Square root of average squared error

```
House 1: Error 20k → Squared: 400M
House 2: Error 20k → Squared: 400M
House 3: Error 50k → Squared: 2.5B

RMSE = sqrt((400M + 400M + 2.5B) / 3) = sqrt(1.1B) = $33k

Why Square?
- Penalizes large errors more
- Large error (50k) squared is 2500x larger than medium error (20k) squared
- Makes outliers matter more
```

**When to Use**:
- Outliers are important to minimize
- Want to penalize large errors more
- Standard metric for many problems

#### 3. R-Squared (Coefficient of Determination)

**Definition**: How much variance does model explain?

```
Total Variance = Sum of squared errors from mean
Model Variance = Sum of squared errors from predictions

R² = 1 - (Model Variance / Total Variance)

Range: 0 to 1 (or negative if worse than mean)

Example:
- R² = 1.0: Perfect model
- R² = 0.7: Model explains 70% of variance
- R² = 0: Model no better than predicting mean
- R² < 0: Model worse than predicting mean
```

**When to Use**:
- Want to compare to baseline (predicting mean)
- Want normalized metric (0-1 scale)
- Want to measure proportion of variance explained

#### 4. Mean Absolute Percentage Error (MAPE)

**Definition**: Average percentage error

```
House 1: Actual $500k, Predicted $480k → Error $20k → 4% error
House 2: Actual $300k, Predicted $320k → Error $20k → 6.7% error
House 3: Actual $800k, Predicted $850k → Error $50k → 6.25% error

MAPE = (4 + 6.7 + 6.25) / 3 = 5.65%

Interpretation:
- On average, predictions off by 5.65%
- Scales with actual value (good for comparing across different ranges)
```

**When to Use**:
- Comparing across different scales
- Percentage error is meaningful
- Values vary widely (thousands to millions)

**When Not to Use**:
- When actual values are close to zero (division by zero)
- When you have negative values

---

## Ranking Metrics

### For Recommendation and Ranking Systems

**Example**: Search engine returns 10 results, user cares about top results

#### 1. Mean Average Precision (MAP)

**Definition**: Average precision at each k position, averaged across queries

```
Query 1: Return 10 results
Relevant results are at positions: 2, 5, 8
- Precision@1: 0/1 = 0%
- Precision@2: 1/2 = 50%
- Precision@5: 2/5 = 40%
- Precision@8: 3/8 = 37.5%
- Precision@10: 3/10 = 30%

AP = (0 + 0.5 + 0.4 + 0.375 + 0.3) / 5 = 0.315 = 31.5%

With 100 queries, average AP = MAP
```

**Interpretation**:
- Where are relevant results positioned?
- Penalizes having relevant items deep in list

**Example**: GitHub Copilot Code Suggestions
```
Query: "Write a function to sum an array"

Results returned:
1. Irrelevant
2. Relevant (partially correct)
3. Irrelevant
4. Very Relevant (exactly what needed)
5-10. Various

At position 2: Correct answer partially there
At position 4: Best answer there

MAP measures: Are relevant results ranked early?
```

#### 2. Normalized Discounted Cumulative Gain (NDCG)

**Definition**: Considers relevance score and position

```
Relevance scores: 0 (irrelevant), 1 (somewhat relevant), 2 (very relevant)

Position 1: Relevance 2 → Gain = 2
Position 2: Relevance 1 → Gain = 1 / log2(3) = 0.63
Position 3: Relevance 0 → Gain = 0

DCG = 2 + 0.63 + 0 = 2.63

Ideal ranking (sorted by relevance):
Position 1: Relevance 2
Position 2: Relevance 2
Position 3: Relevance 1

IDCG = 2 + 2/log2(3) + 1/log2(4) = 2 + 1.26 + 0.5 = 3.76

NDCG = DCG / IDCG = 2.63 / 3.76 = 0.70
```

**When to Use**:
- Ranking has different levels of relevance (not just relevant/irrelevant)
- Position matters (earlier results matter more)
- Want single normalized metric (0-1)

#### 3. Click-Through Rate (CTR)

**Definition**: (Clicks on result) / (Times result shown)

```
Baseline: 2% CTR
Model A: 2.1% CTR
Model B: 2.2% CTR

Model B is 10% better relative improvement
```

**When to Use**:
- Online setting (can measure actual clicks)
- Quick metric to compare ranking changes
- Practical importance (more clicks = more value)

**When Not to Use**:
- Offline (no click data)
- When relevant items may not be clicked (user doesn't scroll)
- Biased by position (higher results get more clicks anyway)

### Example: ChatGPT Suggestion Ranking

```
User starts typing: "def sum_"

Copilot suggests completions ranked by confidence:
1. "sum_array" (95% confidence)
2. "sum_list" (92% confidence)
3. "sum_numbers" (88% confidence)

Metrics:
- Does user accept #1? (Acceptance rate)
- Are top suggestions correct? (Precision@1, Precision@3)
- How far down is correct answer? (MRR = Mean Reciprocal Rank)

MRR = 1 / (position of first correct suggestion)
If correct at position 2: MRR = 1/2 = 0.5
If correct at position 1: MRR = 1/1 = 1.0
```

---

## Generation Metrics

### For Generated Text Quality

**Example**: Machine translation, summarization, text generation

#### 1. BLEU (BiLingual Evaluation Understudy)

**Definition**: Compares generated text to reference text

```
Generated: "The cat is on the mat"
Reference: "The cat sat on the mat"

N-gram matches:
- 1-gram (word): "the", "cat", "on", "the", "mat" = 5/6 = 83%
- 2-gram (word pairs): "the cat", "cat is", "on the", "the mat" = 1/5 matches
- More complex calculation considering n-grams of size 1-4

BLEU = 0-100 scale
- 0: No overlap
- 100: Perfect match

Score interpretation:
- 0-20: Bad
- 20-40: Okay
- 40-60: Good
- 60-80: Very good
- 80-100: Near perfect
```

**Limitations**:
- Doesn't account for synonyms (good synonyms not counted)
- Short references penalized
- Multiple valid translations get lower scores

**When to Use**:
- Machine translation
- Text summarization
- Quick evaluation metric
- Comparing versions

#### 2. ROUGE (Recall-Oriented Understudy for Gisting Evaluation)

**Definition**: Similar to BLEU but focuses on recall

```
Generated Summary: "The meeting discussed budget and hiring plans"
Reference: "The budget meeting covered hiring plans"

Shared n-grams:
- "budget", "meeting", "and", "hiring", "plans", "the" (unordered)
- ROUGE-1 (unigram): 6 shared / 7 in reference = 0.86

Interpretation:
- Higher if generated summary captures more of reference
- Good for summarization
```

**When to Use**:
- Summarization tasks
- When recall more important than precision
- Multiple reference summaries available

#### 3. Human Evaluation

**Problem**: Automatic metrics don't correlate perfectly with human judgment

**Solution**: Have humans rate outputs

```
Evaluation Criteria:

Relevance: Does output address the request?
- 1: Not relevant
- 2: Somewhat relevant
- 3: Highly relevant

Fluency: Is output well-written and grammatical?
- 1: Many errors
- 2: Some errors
- 3: No errors

Factuality: Is output accurate?
- 1: Contains false information
- 2: Mixed accuracy
- 3: Completely accurate

Average across multiple raters (usually 3-5)
```

**Examples**:

```
ChatGPT Answer Quality:
- Have 100 humans rate responses (1-5 scale)
- Average rating = quality metric
- Compare across models

Midjourney Image Quality:
- Present pairs of images
- Ask which is better
- Calculate preference score
- Track improvement over time
```

**When to Use**:
- Evaluating generation quality
- Complex subjective tasks
- Comparing models
- Production monitoring

**Cost**: Expensive (~$5-10 per evaluation)

#### 4. Task-Specific Metrics

```
Machine Translation:
- METEOR: Considers synonyms and word order
- TER (Translation Error Rate): Edits needed to match reference

Summarization:
- ROUGE-L: Longest common subsequence match
- BERTScore: Uses BERT embeddings to compare semantic similarity

Code Generation:
- Pass@k: Does generated code pass test cases?
- Execution match: Does generated code produce correct output?

Dialogue:
- BLEU for response similarity
- Dialogue acts: Is dialogue move appropriate?
- Information retrieval: Is factual info correct?
```

**Example: GitHub Copilot Evaluation**
```
Test Suite: 1000 code completion tasks

Pass@1: Does first suggestion compile and pass tests?
- 70% of suggestions work immediately

Pass@10: Do any of top 10 suggestions work?
- 85% have working solution in top 10

Pass@100: Do any of top 100 suggestions work?
- 93% would be solved if user looked through top 100

This shows model usually has right idea, sometimes needs tweaking.
```

---

## Fairness and Bias Metrics

### Defining Fairness

**Problem**: Models can have systematically worse performance for some groups

**Example: Hiring Model**
```
Model trained on historical hiring data
- Favors candidates from top universities
- Top universities had gender/racial biases in past

Result:
- Male candidates: 80% acceptance rate
- Female candidates: 60% acceptance rate
- Model perpetuates historical bias
```

### Fairness Metrics

#### 1. Demographic Parity

**Definition**: Different groups receive equal outcomes (regardless of qualifications)

```
Hiring Model:
- Males hired: 80%
- Females hired: 60%
- Demographic parity NOT satisfied

Target: Equal outcomes across groups
```

**Criticism**: Ignores differences in qualifications

#### 2. Equal Opportunity

**Definition**: Equal true positive rate across groups (among those who should be positive)

```
Qualified Candidates:
- Qualified males: 100
- Qualified females: 100

Model Predictions:
- Qualified males hired: 80 (80% true positive rate)
- Qualified females hired: 60 (60% true positive rate)
- Equal opportunity NOT satisfied

Target: Both groups have ~80% chance of getting positive prediction if qualified
```

**Advantage**: Considers qualifications

#### 3. Equalized Odds

**Definition**: Equal false positive rate AND equal true positive rate

```
Qualified Candidates:
- Males: TP Rate 80%, FP Rate 10%
- Females: TP Rate 60%, FP Rate 5%
- Equalized odds NOT satisfied

Target: Both rates equal across groups
```

**Strictest fairness metric**

#### 4. Calibration

**Definition**: When model predicts 80% confidence, actual positive rate is ~80%

```
All Predictions with 80% Confidence:
- 10,000 predictions at 80% confidence from males
- 8000 actually positive = 80% accuracy
- 10,000 predictions at 80% confidence from females
- 7000 actually positive = 70% accuracy
- Not calibrated (different groups have different actual rates)
```

**Advantage**: Different fairness meaning - model prediction confidence matches reality

### Measuring Bias

#### 1. Representation Bias

**Definition**: Are underrepresented groups in training data?

```
Training Data:
- Males: 70% of data
- Females: 30% of data
- LGBTQ+: 5% of data

Result:
- Model likely performs better on majority groups
- Minority groups underrepresented in training
```

**Mitigation**:
- Oversample minority groups
- Collect more diverse data
- Use fairness-aware sampling

#### 2. Label Bias

**Definition**: Are labels systematically biased for some groups?

```
Resume Screening Labels (Historical Data):
- For same resume, if name is "John" → hired 80%
- For same resume, if name is "Jamal" → hired 50%
- Labels are biased by race

Result:
- Model learns racial bias from data
```

**Mitigation**:
- Re-label historical data carefully
- Use anonymous resumes
- Test for label bias before training

#### 3. Performance Bias

**Definition**: Does model perform worse for some groups?

```
Face Recognition Accuracy:
- Light skin: 99% accuracy
- Dark skin: 92% accuracy
- Performance biased toward light skin (major issue in production!)
```

**Mitigation**:
- Test performance on balanced groups
- Add minority group examples to training
- Fine-tune model specifically for underperforming groups

### Fairness Metrics in Practice

**Example: ChatGPT Bias Testing**

```
Test: Bias in recommendations
Prompt: "Recommend people for programming roles"

Without mentioning groups:
Model generates list. Check:
- Are women underrepresented?
- Are minorities underrepresented?
- Do people from non-elite schools get recommended?

Test: Fairness in explanations
Prompt: "Why is this candidate a good engineer?"

Group A: Recommendation focuses on technical skills
Group B: Recommendation focuses on leadership/people skills

Unequal metrics are evidence of bias
```

**Example: Midjourney Fairness Concerns**

```
Test: Diversity of generated people
Prompt: "Generate an image of a doctor"

Results:
- Mostly older men
- Mostly light-skinned people
- Not diverse

Issue: Training data (internet images) biased toward stereotypes
Solution:
- Add fairness loss during training
- Include diverse examples
- Monitor generated demographics
```

---

## Offline vs. Online Evaluation

### Offline Evaluation

**Definition**: Evaluate on historical test data before deploying

**Pros**:
- Fast and cheap
- Can evaluate quickly
- Reproducible
- No risk to users

**Cons**:
- Test data may not represent production
- Data distribution changes over time
- Users may behave differently
- Doesn't measure real impact

**Methods**:

1. **Historical A/B Test Data**
   - Use data from past A/B test
   - Compare old and new models on same data
   - Correlates reasonably with online performance

2. **Replay Old Data**
   - Take old production traffic
   - Run both models on same requests
   - Compare predictions

3. **Synthetic Data**
   - Create test cases that might appear in production
   - Test edge cases
   - Test different user segments

### Online Evaluation

**Definition**: Measure actual user behavior with model in production

**Pros**:
- Measures real impact
- Captures user behavior
- True measure of value
- Finds unforeseen issues

**Cons**:
- Slow (need enough users/time)
- Expensive (may hurt some users)
- Statistical noise
- Need infrastructure for online testing

#### Shadow Mode

**Approach**: Run new model in parallel without affecting users

```
Architecture:
User Request
  ↓
Current Model (production)
  ↓
New Model (shadow, not used)
  ↓
Compare Predictions
  ↓
Log Differences
  ↓
Return Current Model's Result

Benefits:
- Zero risk to users (current model used)
- Can compare predictions
- Can detect issues before launch
- Unlimited test time

Metrics Collected:
- Agreement rate (how often do models agree?)
- Cases where they disagree
- If we know ground truth, accuracy of both

Example: ChatGPT New Version
- Run new version in parallel
- Compare responses
- Collect human feedback on both
- If new version better, schedule rollout
```

#### Canary Deployment

**Approach**: Deploy new model to small user fraction

```
Week 1: Deploy to 1% of users
Week 2: If good, 5% of users
Week 3: If good, 20% of users
Week 4: If good, 100% of users

Monitoring:
- Error rate (is it higher?)
- User satisfaction (thumbs up/down)
- Latency (is it slower?)
- Business metrics (revenue impact)

Rollback Plan:
- If any metric degrades, immediately roll back

Example: Midjourney Model Update
- Deploy to 5% of Pro users first
- Monitor image quality ratings
- Check for increased complaints
- If okay, gradually roll out to all users
```

#### A/B Testing (see below for details)

---

## A/B Testing for ML Models

### A/B Testing Framework

**Goal**: Determine if Model B is better than Model A

```
Setup:
Control Group (Model A): 50% of users
Treatment Group (Model B): 50% of users

Run Time: 1-2 weeks (need enough data)

Metrics Tracked:
- Primary Metric: What we care about most
- Secondary Metrics: Other metrics of interest
- Guardrail Metrics: Things we hope don't get worse
```

### Designing A/B Tests

#### 1. Choose Metrics

**Primary Metric**: What really matters

```
Examples:
- e-commerce: Conversion rate (did they buy?)
- Search: Click-through rate (did they click results?)
- Chat: User satisfaction rating
- Code generation: Acceptance rate (did user accept suggestion?)
- Image generation: Rating of images

Choose one primary metric
- Avoid multiple comparisons problem
- Clearer interpretation
```

**Secondary Metrics**: Supporting metrics

```
Example for conversion rate primary metric:
- Time on site
- Items added to cart
- User retention
- Cost to acquire user

Help explain what changed
```

**Guardrail Metrics**: Things we hope don't break

```
Example for image generation:
- Primary: User satisfaction rating
- Guardrails:
  - Latency doesn't increase >10%
  - Error rate doesn't increase >1%
  - Costs don't increase >20%

If any guardrail broken, stop test and rollback
```

#### 2. Sample Size Calculation

**Problem**: Need enough users to detect real difference

```
Baseline metrics:
- Current conversion rate: 2%
- Want to detect: 10% relative increase (2% → 2.2%)
- Confidence: 95% (allow 5% false positive rate)
- Power: 80% (detect 80% of real effects)

Sample size calculation:
- ~50,000 users per group needed
- Run time: ~2 weeks (50M users/day need less time)

More users needed if:
- Smaller expected improvement
- Higher required confidence
- Want to detect for subgroups
- More volatile metric
```

**Tools**: Online calculators or power analysis libraries

#### 3. Statistical Significance

**Problem**: Did improvement happen by chance or is it real?

**p-value**: Probability of observed result by chance if no real effect

```
p-value = 0.05 means:
- 5% chance we'd see this result if Model B is actually same as Model A
- 95% confidence Model B is actually different
- Standard threshold: p < 0.05

Example:
Model A: 2.0% conversion
Model B: 2.2% conversion
p-value: 0.03

Conclusion: 97% confident Model B is better
```

**Confidence Interval**:

```
"Model B is 2.2% ± 0.1% conversion rate"
- Could be as low as 2.1% or as high as 2.3%
- 95% confident true value in this range
```

#### 4. Running the Test

**Duration**:
- Long enough to account for variation
- At least one full week (captures weekday/weekend patterns)
- Longer for noisy metrics

**Randomization**:
- Randomly assign users to control/treatment
- Stratify if needed (ensure each group has same user types)

**Monitoring**:
- Check daily for obvious issues
- But don't stop early just because one group ahead
- Allows "peeking" but must adjust statistics

### Interpreting A/B Test Results

#### Scenario 1: B is Significantly Better

```
Model A: 2.0% conversion
Model B: 2.2% conversion
p-value: 0.03

Action: Deploy Model B!
```

#### Scenario 2: No Significant Difference

```
Model A: 2.0% conversion
Model B: 2.01% conversion
p-value: 0.50

Action: Metrics are similar
- Could flip a coin (no real difference)
- Choose based on other factors (speed, cost, simplicity)
- Consider other metrics
```

#### Scenario 3: B is Significantly Worse

```
Model A: 2.0% conversion
Model B: 1.95% conversion
p-value: 0.04

Action: Stick with Model A
- B hurts conversion
- Root cause analysis needed
```

#### Scenario 4: Mixed Results

```
Primary Metric (Conversion):
- Model A: 2.0%
- Model B: 2.05%
- p-value: 0.10 (not significant)

Secondary Metrics:
- User satisfaction: B is significantly better
- Cost: B is significantly cheaper
- Latency: B is significantly faster

Action: Depends on goals
- If satisfaction important: Choose B despite conversion not significant
- Document the decision
```

### Example: GitHub Copilot A/B Test

**Hypothesis**: Better prompt engineering increases acceptance rate

```
Control Group: Current prompting strategy
Treatment Group: New prompt with more context

Metrics:
Primary: Code acceptance rate (% of suggestions users accept)
Secondary: Time to write next line, user satisfaction
Guardrails: Latency <1s, error rate <0.1%

Results After 2 Weeks:
- Control: 35.2% acceptance (2M suggestions)
- Treatment: 36.1% acceptance (2M suggestions)
- Difference: 0.9% (relative 2.6% improvement)
- p-value: 0.02 (significant!)

Decision: Deploy new prompting strategy
- Improves user experience
- Meaningful improvement
- No guardrails broken
```

---

## Monitoring and Production Metrics

### Why Monitor ML Models?

**Problem**: Models degrade over time

```
Model Performance Over Time:
Launch: 85% accuracy
After 1 month: 84% accuracy
After 3 months: 82% accuracy

Why?
- Data distribution changed (world changed)
- Bugs in production system
- Natural drift in user behavior
- Model was overfit to training data

Need to detect degradation and retrain
```

### Production Monitoring System

```
LLM/ML Model in Production
         ↓
  Prediction Made
         ↓
  ┌─────┴─────┐
  ↓           ↓
User Accepts  System Gets Result
  ↓           ↓
Record Signal Monitor
  ↓
Feedback Loop
```

#### Metrics to Monitor

**1. Model Performance Metrics**

```
Real-time Dashboard:
- Accuracy (if we know ground truth)
- Precision/Recall
- AUC-ROC
- F1 score

Updated: Every hour, day, week
Alerts: If metrics drop >1% from baseline

Example: ChatGPT
- Track user ratings (1-5 stars)
- Track thumbs up/down on responses
- Measure hallucination rate
```

**2. System Health Metrics**

```
- Latency: Is inference fast?
  - p50, p95, p99
  - Alert if p95 > 2x baseline

- Throughput: How many requests/minute?
  - Alert if drop suggests system issues

- Error Rate: Predictions failing?
  - Alert if >0.1%

- Resource Usage:
  - CPU, memory, GPU usage
  - Alert if approaching limits
```

**3. User Behavior Metrics**

```
- Engagement: Are users using it?
  - Daily active users
  - Sessions per user
  - Queries per user

- Satisfaction: Are they happy?
  - Rating distribution
  - Thumbs up/down ratio
  - Net Promoter Score (NPS)

- Retention: Do they keep using?
  - Day 7 retention
  - Month 1 retention

- Churn: Are they leaving?
  - User drop-off rate
  - Subscription cancellation rate
```

**4. Business Metrics**

```
- Revenue: Is it profitable?
  - Total revenue
  - Revenue per user
  - Revenue per inference

- Cost: What does it cost to run?
  - Infrastructure cost
  - Cost per inference
  - Gross margin

- ROI: Is it worth it?
  - Revenue vs. Cost
```

**5. Fairness/Safety Metrics**

```
- Bias: Performance across groups?
  - Accuracy by demographic group
  - Alert if gap >5%

- Safety: Are outputs safe?
  - Toxic output rate
  - Hallucination rate
  - Refusal rate (on sensitive requests)

- Drift: Has data distribution changed?
  - Compare current data to training data
  - Alert if significant shift
```

### Alerting Strategy

**Alerts should be**:
- Actionable (someone can fix it)
- High signal (low false alarm rate)
- Timely (alert before serious damage)

```
Example Alert:
Name: Model Accuracy Drop
Metric: Accuracy
Baseline: 85%
Threshold: If drops below 83% for 1 hour
Action: Page on-call engineer
Runbook: "Check recent model deployment, check data quality, consider rollback"

Example Alert:
Name: High Latency
Metric: p95 Latency
Baseline: 500ms
Threshold: If exceeds 1000ms for 15 minutes
Action: Email team
Runbook: "Check server load, check for new feature causing slowness"
```

### Retraining Pipeline

**When to Retrain**:

```
Schedule-Based:
- Retrain every Monday
- Retrain every month
- Simple, predictable

Performance-Based:
- Retrain if accuracy drops >2%
- Retrain if fairness metric changes
- Responsive to issues

Data-Based:
- Retrain if distribution shift detected
- Retrain after N new examples
- Data-driven approach

Hybrid:
- Minimum monthly retrain
- Additional retrain if performance drops
- Best approach
```

**Retraining Process**:

```
1. Collect new data
   - Gather production data
   - Include human feedback/labels
   - Filter bad data

2. Prepare data
   - Clean data
   - Handle missing values
   - Stratify train/test split

3. Train models
   - Train multiple candidates
   - Hyperparameter tuning
   - Hold-out test evaluation

4. Evaluate
   - Compare to current model
   - Check fairness metrics
   - Verify no catastrophic regressions

5. Approve
   - Get human approval
   - Document decision
   - Record model version

6. Deploy
   - Shadow mode first
   - Canary deployment
   - Monitor closely

7. Monitor
   - Track performance
   - Monitor user impact
   - Be ready to rollback
```

### Example: Monitoring ML Fraud Detection

```
Fraud Detection Model in Production

Metrics Monitored:
- FPR (false positive rate): % legitimate transactions flagged
  Target: <0.5%
  Alert: If >1% (customers complaining about blocked transactions)

- FNR (false negative rate): % fraud not caught
  Target: <2%
  Alert: If >5% (fraud spike)

- Latency: Time to score transaction
  Target: <50ms
  Alert: If >100ms (impacts checkout)

- Model drift: Has fraud pattern changed?
  Track: Feature distributions over time
  Alert: If major shift (fraud patterns evolving)

Daily Report:
- FPR: 0.48% ✓
- FNR: 1.2% ✓
- Latency p95: 45ms ✓
- 3 fraud patterns detected ⚠️

Action: Investigate new fraud patterns, consider model update
```

---

## Real-World Examples

### Example 1: ChatGPT Evaluation

**Challenge**: How do you evaluate conversational AI?

**Metrics Used**:

1. **User Feedback**
   - Thumbs up/down on every response
   - 5-star rating on conversation
   - Tracks sentiment of feedback

2. **Conversation Quality**
   - Length of conversations (engaged users)
   - Follow-up rate (do users continue?)
   - Error reporting (do users report issues?)

3. **Specific Capabilities**
   - Code execution tests: Can it generate working code?
   - Factual accuracy: Does it provide correct information?
   - Reasoning tasks: Complex multi-step problems

4. **Safety**
   - Harmful output rate: % of responses inappropriate
   - Toxicity: Does it generate toxic content?
   - Refusal accuracy: Does it refuse harmful requests?

**Monitoring in Production**:
```
Dashboard tracks:
- Daily thumbs up/down ratio
- Common complaints (unclear answer, factually wrong, etc.)
- Model version performance
- Response latency

Alerts:
- Thumbs down ratio >10%
- Latency p95 >3s
- Harmful content spike
```

### Example 2: Midjourney Image Generation Evaluation

**Challenge**: How do you evaluate subjective creative output?

**Metrics Used**:

1. **User Satisfaction**
   - Upvoting/favoriting images (user satisfaction)
   - Acceptance rate: % of generated images users use
   - Iterations to satisfaction: How many versions until happy?

2. **Quality Dimensions**
   - Visual quality (sharpness, color, composition)
   - Prompt adherence (does image match request?)
   - Diversity (do variations look different?)
   - Safety (no inappropriate content)

3. **Generation Metrics**
   - Speed: Time to generate 4 variations
   - Success rate: % of generations that complete
   - Cost: Compute resources per generation

4. **A/B Tests**
   - New model vs. old: Which do users prefer?
   - Compare on same prompts
   - Collect user votes on which is better

**Monitoring in Production**:
```
Weekly Report:
- Generation speed: 45s avg (good)
- Success rate: 99.2% (acceptable)
- User satisfaction rating: 4.1/5 (good)
- Upvote ratio: 35% (typical)
- Most common feedback: "More detail requested" (insight)

Action: Consider model update focusing on detail
```

### Example 3: GitHub Copilot Code Completion Evaluation

**Challenge**: How do you measure code suggestion quality?

**Metrics Used**:

1. **Acceptance Metrics**
   - Acceptance rate: % of suggestions user accepts
   - Latency to acceptance: Time between suggestion and acceptance
   - Completion time saved

2. **Quality Metrics**
   - Code correctness: Does accepted code run?
   - Syntax correctness: Does it compile?
   - Test passage: Does it pass unit tests?

3. **Productivity Metrics**
   - Lines completed per hour
   - Function completion rate
   - Context switches (does it reduce?)

4. **Demographic Fairness**
   - Acceptance rate by programming language
   - Acceptance rate by skill level (junior vs. senior)
   - Performance by code type (frontend, backend, tests)

5. **Safety**
   - Security vulnerabilities suggested
   - Deprecated API usage
   - Code smells

**A/B Testing**:
```
Test: Better context inclusion

Control: Current context window
Treatment: Larger context window

Results after 2 weeks:
- Control: 35% acceptance rate
- Treatment: 37.2% acceptance rate
- Difference: +2.2% (p=0.001, significant)

Secondary metrics:
- Quality: No difference
- Latency: -10ms (faster, good!)

Conclusion: Larger context is better
Deploy to 100% of users
```

**Monitoring Production**:
```
Real-time Dashboard:
- Suggestions per day: 1.2B
- Acceptance rate: 35.4%
- Avg latency: 850ms
- Error rate: 0.02%

Language Breakdown:
- Python: 38% acceptance
- JavaScript: 35% acceptance
- TypeScript: 36% acceptance
- Java: 32% acceptance

Insight: Lower acceptance for Java. Consider Java-specific tuning.
```

---

## Conclusion

Evaluating ML models requires:

1. **Multiple Perspectives**
   - Technical metrics (accuracy, latency)
   - User perspective (satisfaction, value)
   - Business perspective (revenue, ROI)
   - Ethical perspective (fairness, safety)

2. **Right Metrics for Right Context**
   - Use metrics aligned with goals
   - Don't optimize for wrong metrics
   - Monitor multiple dimensions

3. **Offline vs. Online**
   - Start with offline evaluation (fast, cheap)
   - Validate online with real users
   - Use A/B testing for final validation

4. **Continuous Monitoring**
   - Models degrade over time
   - Monitor production carefully
   - Retrain when performance drops
   - Be ready to rollback quickly

5. **Ethical Responsibility**
   - Fairness matters as much as accuracy
   - Monitor for bias and discrimination
   - Test on diverse populations
   - Be transparent with users

The best ML products balance technical excellence with user value and ethical responsibility.


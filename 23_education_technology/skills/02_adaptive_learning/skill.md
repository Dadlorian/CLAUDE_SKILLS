# Adaptive Learning Skill

## Purpose

You are an expert in adaptive learning systems, AI-powered personalization, knowledge tracing algorithms, and individualized learning path generation. You design systems that adjust content difficulty, pacing, and modality based on real-time learner performance. Your expertise spans Bayesian and deep learning-based knowledge modeling, learner profiling, and dynamic curriculum sequencing.

## Core Competencies

### Knowledge Tracing Algorithms

**Bayesian Knowledge Tracing (BKT)**:
- **P(L0)**: Initial knowledge probability (prior belief about learner's starting state)
- **P(T)**: Learning/transition probability (probability learner gains skill after attempt)
- **P(G)**: Guess probability (probability correct response despite not knowing)
- **P(S)**: Slip probability (probability incorrect response despite knowing)
- **Update mechanism**: Uses EM algorithm to update belief state after each observation
- **Strengths**: Interpretable, well-established, works with limited data
- **Limitations**: Assumes independence between skills, struggles with complex skill hierarchies

```python
class BayesianKnowledgeTracer:
    """
    Classical BKT model for skill mastery estimation.

    Parameters:
    - p_L0: Prior probability learner knows skill
    - p_T: Transition probability (learning rate)
    - p_G: Guess probability
    - p_S: Slip probability
    """

    def __init__(self, p_L0=0.1, p_T=0.3, p_G=0.1, p_S=0.1):
        self.p_L0 = p_L0  # Initial knowledge
        self.p_T = p_T    # Learning rate
        self.p_G = p_G    # Guess probability
        self.p_S = p_S    # Slip probability
        self.p_L = p_L0   # Current knowledge estimate

    def update_belief(self, observed_correct):
        """Update knowledge belief after learner attempt."""
        if observed_correct:
            # P(L|correct) = P(correct|L) * P(L) / P(correct)
            numerator = (1 - self.p_S) * self.p_L
            denominator = (1 - self.p_S) * self.p_L + self.p_G * (1 - self.p_L)
        else:
            # P(L|incorrect) = P(incorrect|L) * P(L) / P(incorrect)
            numerator = self.p_S * self.p_L
            denominator = self.p_S * self.p_L + (1 - self.p_G) * (1 - self.p_L)

        self.p_L = numerator / denominator if denominator > 0 else 0

        # Transition: learner may have learned
        self.p_L = self.p_L * (1 - self.p_T) + (1 - self.p_L) * self.p_T

        return self.p_L

    def get_mastery_probability(self):
        """Return current estimate of skill mastery (threshold: 0.95)."""
        return self.p_L > 0.95
```

**Deep Knowledge Tracing (DKT)**:
- **Architecture**: LSTM/GRU neural networks that process sequence of attempts
- **Input**: Problem ID, correctness of previous attempt
- **Output**: Prediction of next attempt correctness
- **Advantages**:
  - Captures complex temporal patterns and skill interactions
  - Better performance on large datasets (>1000 students per skill)
  - Learns non-linear relationships automatically
- **Limitations**: Black-box model (less interpretable), requires substantial training data, prone to overfitting

```python
import torch
import torch.nn as nn

class DeepKnowledgeTracer(nn.Module):
    """
    LSTM-based Deep Knowledge Tracing model.
    Learns representations of student knowledge and skill dynamics.
    """

    def __init__(self, num_problems, hidden_size=200, num_layers=1, dropout=0.5):
        super().__init__()
        self.num_problems = num_problems
        self.hidden_size = hidden_size

        # Input embedding: (problem_id, correctness) -> embedding
        self.problem_embed = nn.Embedding(num_problems, hidden_size)
        self.lstm = nn.LSTM(
            hidden_size * 2,  # problem embedding + correctness one-hot
            hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        self.fc = nn.Linear(hidden_size, num_problems)

    def forward(self, problem_ids, correctness):
        """
        Args:
            problem_ids: (batch, seq_len) problem indices
            correctness: (batch, seq_len) binary correctness values

        Returns:
            predictions: (batch, seq_len, num_problems) logits for next problem
        """
        # Embed problems and concatenate with correctness
        problem_embeddings = self.problem_embed(problem_ids)
        correctness_encoded = correctness.unsqueeze(-1).float()
        correctness_expanded = correctness_encoded.expand_as(problem_embeddings)

        x = torch.cat([problem_embeddings, correctness_expanded], dim=-1)

        # LSTM forward pass
        lstm_out, _ = self.lstm(x)

        # Predict correctness for next problem
        predictions = self.fc(lstm_out)
        return predictions
```

**Item Response Theory (IRT)**:
- **1PL (Rasch Model)**: Only difficulty parameter; assumes equal discrimination
- **2PL Model**: Difficulty + discrimination parameters; standard for CAT
- **3PL Model**: Includes pseudo-guessing parameter; accounts for lucky guesses
- **Application in CAT**: Select next item to maximize information gain about learner ability
- **Formula**: P(correct) = c + (1-c) / (1 + exp(-a(θ-b)))
  - θ: Learner ability
  - b: Item difficulty
  - a: Item discrimination
  - c: Pseudo-guessing parameter

### Personalization Strategies

**Content Sequencing**:
- **Prerequisite chains**: Build dependency graph (e.g., Fractions → Decimals → Percentages)
- **Zone of Proximal Development (ZPD)**: Present items just beyond current ability level
- **Difficulty calibration**: Select items with ~60-70% success rate for optimal learning
- **Vertical scaffolding**: Provide prerequisite review when needed

**Difficulty Calibration**:
```python
class AdaptiveSequencer:
    """Sequence content based on learner ability and prerequisites."""

    def select_next_item(self, learner_ability, available_items, attempt_history):
        """
        Select optimal next item using difficulty calibration.
        Goal: ~65% success probability (sweet spot for learning)
        """
        # Filter by prerequisites
        unlocked = self.filter_prerequisites(available_items, attempt_history)

        # Rank by proximity to learner ability
        scored = []
        for item in unlocked:
            ideal_difficulty = learner_ability + 0.3  # Slightly above ability
            difficulty_gap = abs(item.difficulty - ideal_difficulty)

            # Also consider how long since item was attempted
            freshness = self.days_since_attempt(item.id, learner_id) / 30.0

            # Weighted score: prefer items near ability, prefer less recent
            score = -difficulty_gap + 0.2 * freshness
            scored.append((score, item))

        return max(scored, key=lambda x: x[0])[1]
```

**Multi-Modal Content Delivery**:
- **Visual**: Diagrams, infographics, animations, 3D visualizations
- **Auditory**: Lectures, podcasts, text-to-speech, explanations
- **Kinesthetic**: Simulations, interactive drag-and-drop, hands-on labs
- **Reading/Writing**: Text passages, note-taking, written explanations
- **Preference detection**: Implicit (track engagement by modality) vs. explicit (VARK questionnaire)

**Spaced Repetition Scheduling**:
- **SM-2 Algorithm**: Classic approach, optimizes for ~90% retention
- **FSRS (Free Spaced Repetition Scheduler)**: Modern algorithm with better parameters
- **Scheduling function**: Days until next review = (interval) * (ease_factor)
- **Retention target**: Balance between 85-95% (too high = excessive reviewing; too low = frequent failures)

```python
class SpacedRepetitionScheduler:
    """Optimal scheduling based on forgetting curve."""

    def schedule_review(self, item_id, quality_of_response, previous_interval=1):
        """
        SM-2 algorithm for spaced repetition.
        quality_of_response: 0-5 (0=complete blackout, 5=perfect response)
        """
        EASE_MIN = 1.3

        # Initialize ease factor for new items
        if not hasattr(self, f'ease_{item_id}'):
            setattr(self, f'ease_{item_id}', 2.5)

        ease = getattr(self, f'ease_{item_id}')

        # Update ease factor based on response quality
        new_ease = ease + (0.1 - (5 - quality_of_response) * (0.08 + (5 - quality_of_response) * 0.02))
        new_ease = max(EASE_MIN, new_ease)
        setattr(self, f'ease_{item_id}', new_ease)

        # Calculate next review interval
        if quality_of_response < 3:  # Failed response
            interval = 1  # Review again tomorrow
        else:
            interval = previous_interval * new_ease

        return {
            'next_review_days': int(interval),
            'ease_factor': new_ease,
            'retention_probability': 0.95 ** (interval / 7)  # Rough estimate
        }
```

**Remediation and Acceleration**:
- **Remediation pathways**: When learner struggles, offer prerequisite review and scaffolding
- **Acceleration pathways**: For advanced learners, skip mastered content and jump to extensions
- **Branching logic**: Rule-based (if score < 60%, do remediation) or ML-based

### Architecture & Design Patterns

**Learner Profile Model**:
```python
class LearnerProfile:
    """
    Complete profile tracking learner's knowledge, preferences, and progress.
    """

    def __init__(self, learner_id):
        self.learner_id = learner_id

        # Knowledge state: skill -> mastery probability
        self.skill_knowledge = {}  # {skill_id: probability}

        # Learning preferences
        self.preferred_modalities = {}  # {modality: engagement_score}
        self.learning_pace = 'normal'  # fast/normal/slow
        self.interaction_style = 'exploratory'  # linear/exploratory

        # Performance metrics
        self.attempt_history = []  # [{problem_id, correct, time, date}]
        self.engagement_score = 0.5
        self.frustration_level = 0.0

        # Goals and milestones
        self.learning_goals = []
        self.milestones_reached = []

    def update_knowledge_state(self, skill_id, tracer_output):
        """Update skill mastery based on knowledge tracing."""
        self.skill_knowledge[skill_id] = tracer_output

    def infer_learning_style(self):
        """Infer learning modality preferences from engagement data."""
        modality_engagement = {}
        for attempt in self.attempt_history[-100:]:  # Last 100 attempts
            modality = attempt['modality']
            engagement = attempt['time_spent'] / attempt['duration']
            modality_engagement[modality] = modality_engagement.get(modality, 0) + engagement

        return modality_engagement

    def get_recommended_difficulty(self):
        """Return recommended difficulty level for next item."""
        avg_ability = sum(self.skill_knowledge.values()) / len(self.skill_knowledge)
        # Account for learning pace preference
        if self.learning_pace == 'fast':
            return avg_ability + 0.5
        elif self.learning_pace == 'slow':
            return avg_ability
        else:
            return avg_ability + 0.25
```

### Technical Implementation

**System Architecture**:
1. **Real-time Event Stream**: Capture every learner interaction (attempt, time, modality)
2. **Knowledge Tracing Service**: Run BKT/DKT to update skill estimates
3. **Sequencing Engine**: Select next content based on current state
4. **Personalization Engine**: Customize delivery (modality, difficulty, pacing)
5. **Analytics Dashboard**: Track learning progress and identify at-risk students

**Integration with LMS**:
- xAPI events for all learner interactions
- Learning Record Store (LRS) for persistent tracking
- WebHooks to trigger content sequence updates
- REST API for real-time personalization decisions

### Best Practices

1. **Avoid Over-Adaptation**: Too much personalization can reduce exposure to diverse content
2. **Maintain Challenge**: Balance between success rate (~70%) and novelty
3. **Explainability**: Show learners why content was selected
4. **Privacy**: Secure learner data; comply with FERPA, GDPR
5. **A/B Testing**: Validate improvements before full deployment
6. **Human in the Loop**: Allow instructors to override recommendations

### Tools & Technologies

- **Knowledge Tracing**: Scikit-learn (BKT), PyTorch (DKT), TensorFlow
- **Content Management**: Neo4j (prerequisites graph), PostgreSQL
- **Analytics**: Apache Spark, Airflow (ETL), Jupyter notebooks
- **ML Frameworks**: XGBoost, LightGBM for learner ability prediction
- **Deployment**: Docker, Kubernetes, FastAPI for real-time decisions

### Production ML Model Deployment & Monitoring

**Real-Time Prediction Service**:
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow
import numpy as np

app = FastAPI(title="Adaptive Learning API")

# Load model from MLflow
model = mlflow.pytorch.load_model("models:/dkt-model/production")

class PredictionRequest(BaseModel):
    student_id: str
    problem_ids: list[int]
    correctness: list[bool]

class PredictionResponse(BaseModel):
    student_id: str
    predictions: dict[int, float]
    confidence: float
    recommended_difficulty: float

@app.post("/predict", response_model=PredictionResponse)
async def predict_next_problem(request: PredictionRequest):
    """
    Real-time prediction API for adaptive content selection.
    Returns probability of success on each problem.
    """
    try:
        # Prepare input tensors
        problem_tensor = torch.tensor([request.problem_ids])
        correctness_tensor = torch.tensor([request.correctness]).float()

        # Run inference
        with torch.no_grad():
            predictions = model(problem_tensor, correctness_tensor)

        # Convert to probabilities
        probs = torch.sigmoid(predictions[0, -1, :]).numpy()

        # Track prediction latency
        from prometheus_client import Histogram
        prediction_latency = Histogram('adaptive_prediction_seconds', 'Prediction latency')

        return PredictionResponse(
            student_id=request.student_id,
            predictions={i: float(probs[i]) for i in range(len(probs))},
            confidence=float(np.std(probs)),
            recommended_difficulty=float(np.mean(probs))
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model_version": "v1.2.3"}
```

**Model Training Pipeline (MLflow)**:
```python
import mlflow
import mlflow.pytorch
from sklearn.model_selection import train_test_split

class AdaptiveLearningMLOps:
    """MLOps practices for adaptive learning models."""

    def train_and_log_model(self, training_data, validation_data):
        """
        Train DKT model with experiment tracking.
        Logs: Parameters, metrics, model artifact, training graphs.
        """
        mlflow.set_experiment("adaptive-learning-dkt")

        with mlflow.start_run(run_name="dkt-training"):
            # Log parameters
            params = {
                'hidden_size': 200,
                'num_layers': 2,
                'dropout': 0.5,
                'learning_rate': 0.001,
                'batch_size': 32,
                'epochs': 50
            }
            mlflow.log_params(params)

            # Initialize model
            model = DeepKnowledgeTracer(
                num_problems=training_data.num_problems,
                hidden_size=params['hidden_size'],
                num_layers=params['num_layers'],
                dropout=params['dropout']
            )

            # Train model
            optimizer = torch.optim.Adam(model.parameters(), lr=params['learning_rate'])
            criterion = nn.BCEWithLogitsLoss()

            for epoch in range(params['epochs']):
                train_loss = self.train_epoch(model, training_data, optimizer, criterion)
                val_loss, val_auc = self.validate_epoch(model, validation_data, criterion)

                # Log metrics
                mlflow.log_metrics({
                    'train_loss': train_loss,
                    'val_loss': val_loss,
                    'val_auc': val_auc
                }, step=epoch)

                # Early stopping
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if patience_counter >= 5:
                        break

            # Log model
            mlflow.pytorch.log_model(model, "model")

            # Log training artifacts
            mlflow.log_artifact("training_curves.png")

            return model

    def evaluate_model_quality(self, model, test_data):
        """
        Comprehensive model evaluation.
        Metrics: AUC, accuracy, calibration, fairness.
        """
        from sklearn.metrics import roc_auc_score, accuracy_score, calibration_curve

        predictions = []
        actuals = []

        with torch.no_grad():
            for batch in test_data:
                preds = model(batch['problem_ids'], batch['correctness'])
                predictions.extend(preds.cpu().numpy().flatten())
                actuals.extend(batch['labels'].cpu().numpy().flatten())

        # ROC-AUC
        auc = roc_auc_score(actuals, predictions)

        # Accuracy
        binary_preds = [1 if p > 0.5 else 0 for p in predictions]
        accuracy = accuracy_score(actuals, binary_preds)

        # Calibration (are predicted probabilities accurate?)
        prob_true, prob_pred = calibration_curve(actuals, predictions, n_bins=10)
        calibration_error = np.mean(np.abs(prob_true - prob_pred))

        return {
            'auc': auc,
            'accuracy': accuracy,
            'calibration_error': calibration_error
        }

    def monitor_model_drift(self, production_predictions, ground_truth):
        """
        Detect when model performance degrades in production.
        Alert if AUC drops below threshold or prediction distribution shifts.
        """
        from scipy.stats import ks_2samp

        # Calculate production AUC
        production_auc = roc_auc_score(ground_truth, production_predictions)

        # Compare to baseline (training AUC)
        baseline_auc = 0.85  # From training
        auc_drop = baseline_auc - production_auc

        if auc_drop > 0.05:  # 5% drop threshold
            self.alert_model_degradation(auc_drop)

        # Check prediction distribution shift
        training_preds = self.load_training_predictions()
        ks_statistic, p_value = ks_2samp(training_preds, production_predictions)

        if p_value < 0.05:  # Significant distribution shift
            self.alert_distribution_shift(ks_statistic, p_value)

    def a_b_test_models(self, model_a, model_b, test_students):
        """
        A/B test two models to see which performs better.
        Split students randomly, measure learning outcomes.
        """
        import random

        group_a = random.sample(test_students, len(test_students) // 2)
        group_b = [s for s in test_students if s not in group_a]

        # Track outcomes for each group
        outcomes_a = self.run_adaptive_learning(model_a, group_a, duration_days=30)
        outcomes_b = self.run_adaptive_learning(model_b, group_b, duration_days=30)

        # Statistical test (t-test for final scores)
        from scipy.stats import ttest_ind
        t_stat, p_value = ttest_ind(outcomes_a['final_scores'], outcomes_b['final_scores'])

        return {
            'model_a_mean': np.mean(outcomes_a['final_scores']),
            'model_b_mean': np.mean(outcomes_b['final_scores']),
            'statistical_significance': p_value < 0.05,
            'winner': 'model_a' if np.mean(outcomes_a['final_scores']) > np.mean(outcomes_b['final_scores']) else 'model_b'
        }
```

**Automated Model Retraining**:
```python
import airflow
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': True,
    'email': ['ml-alerts@university.edu'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'adaptive_learning_model_retrain',
    default_args=default_args,
    description='Weekly model retraining pipeline',
    schedule_interval='0 2 * * 0',  # Sunday 2am
    catchup=False
)

def extract_training_data():
    """Extract last 90 days of student interactions."""
    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(days=90)

    # Query database for recent attempts
    query = """
    SELECT student_id, problem_id, correct, timestamp
    FROM student_attempts
    WHERE timestamp > %s
    ORDER BY student_id, timestamp
    """
    # Execute and return data

def preprocess_data(raw_data):
    """Convert raw data to model input format."""
    # Group by student, create sequences
    # Apply data augmentation if needed
    pass

def train_candidate_model(training_data):
    """Train new model version."""
    mlops = AdaptiveLearningMLOps()
    model = mlops.train_and_log_model(training_data, validation_data)
    return model

def evaluate_candidate_model(model, test_data):
    """Evaluate on hold-out test set."""
    mlops = AdaptiveLearningMLOps()
    metrics = mlops.evaluate_model_quality(model, test_data)

    # Compare to production model
    if metrics['auc'] > 0.85 and metrics['calibration_error'] < 0.1:
        return 'promote_to_production'
    else:
        return 'reject_model'

def promote_model_to_production(model):
    """Replace production model if candidate is better."""
    mlflow.register_model(
        model_uri=f"runs:/{mlflow.active_run().info.run_id}/model",
        name="dkt-model",
        tags={"stage": "production"}
    )

# Define tasks
extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_training_data,
    dag=dag
)

preprocess_task = PythonOperator(
    task_id='preprocess',
    python_callable=preprocess_data,
    dag=dag
)

train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_candidate_model,
    dag=dag
)

evaluate_task = PythonOperator(
    task_id='evaluate_model',
    python_callable=evaluate_candidate_model,
    dag=dag
)

promote_task = PythonOperator(
    task_id='promote_model',
    python_callable=promote_model_to_production,
    dag=dag
)

# Task dependencies
extract_task >> preprocess_task >> train_task >> evaluate_task >> promote_task
```

### Research & References

- **Foundational**: Corbett & Anderson (2000) "Knowledge Tracing: Modeling the Acquisition of Procedural Knowledge"
- **Deep Learning**: Piech et al. (2015) "Deep Knowledge Tracing"
- **Modern Approaches**: Wilson et al. (2016) "Estimating Student Knowledge During Collaborative Tutoring with Bayesian Networks"
- **Conferences**: Learning @ Scale, ITS (Intelligent Tutoring Systems), EDM (Educational Data Mining)

### Challenges & Considerations

1. **Data Quality**: Incomplete or noisy attempt data affects accuracy
2. **Skill Granularity**: Too fine-grained skills = data sparsity; too coarse = loss of detail
3. **Cold Start Problem**: Limited data for new students; use item-based or content-based approaches
4. **Concept Drift**: Student knowledge changes over long periods; update models regularly
5. **Fairness**: Ensure adaptive systems don't amplify educational gaps

### Implementation Challenges & Solutions

**Cold Start Problem**:
```python
class ColdStartStrategy:
    """Handle new students with no learning history."""

    def collaborative_filtering(self, new_student_profile):
        """
        Find similar students with more history.
        Example: New student is interested in Python.
        Find other Python learners, use their path as recommendation.
        """
        # K-NN: Find K nearest neighbors in student feature space
        # Use average performance of similar students
        similar_students = self.find_similar_students(new_student_profile)
        recommended_items = self.get_common_items(similar_students)
        return recommended_items

    def content_based_recommendations(self):
        """
        Recommend based on item attributes, not student history.
        Example: If student views video on Loops,
        recommend next video on Functions (detected similar topics).
        """
        pass

    def hybrid_approach(self):
        """Combine multiple strategies."""
        collaborative = self.collaborative_filtering(student)
        content_based = self.content_based_recommendations(student)
        combined = self.merge_recommendations(collaborative, content_based)
        return combined
```

**Concept Drift** (Student knowledge changes):
```python
class ConceptDriftHandling:
    """Update models regularly to reflect learning evolution."""

    def sliding_window_training(self, all_attempts, window_size_days=30):
        """
        Train models on recent attempts only (last 30 days).
        Forget very old data that may not reflect current performance.
        """
        import datetime
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=window_size_days)
        recent_attempts = [a for a in all_attempts if a['date'] > cutoff_date]

        # Train knowledge tracing model on recent data
        model = self.train_bkt_model(recent_attempts)
        return model

    def decay_old_observations(self, all_attempts, decay_factor=0.9):
        """
        Give more weight to recent attempts.
        Formula: weight = decay_factor ^ (days_ago)
        """
        weights = []
        for attempt in all_attempts:
            days_ago = (datetime.datetime.now() - attempt['date']).days
            weight = decay_factor ** days_ago
            weights.append(weight)

        # Use weighted observations in training
        return weights
```

**Fairness & Bias**:
```python
class AdaptiveLearningFairness:
    """Ensure adaptive systems don't amplify disparities."""

    def detect_bias(self, model_predictions, student_groups):
        """
        Measure if model is fair across demographic groups.
        Example: Does model recommend advanced content equally
        to students from different racial backgrounds?
        """
        predictions_by_group = {}
        for group_name, student_ids in student_groups.items():
            group_predictions = [model_predictions[sid] for sid in student_ids]
            avg_difficulty = sum(p['difficulty'] for p in group_predictions) / len(group_predictions)
            predictions_by_group[group_name] = avg_difficulty

        # Check for disparities
        max_diff = max(predictions_by_group.values()) - min(predictions_by_group.values())
        if max_diff > 0.2:  # Threshold: 0.2 difficulty units
            return {
                'fairness_alert': True,
                'predictions_by_group': predictions_by_group,
                'disparity_score': max_diff
            }

    def mitigate_bias(self, model):
        """
        Techniques to reduce bias:
        1. Stratified training: Ensure training data balanced across groups
        2. Fairness constraints: Penalize unequal treatment
        3. Post-processing: Adjust recommendations to be more equitable
        """
        pass

    def track_long_term_outcomes(self, students, timeline_years=4):
        """
        Does personalization improve outcomes for all groups long-term?
        Measure graduation rates, major selection, career success by group.
        """
        pass
```

### Real-World Examples & Case Studies

**Duolingo's Adaptive Learning**:
- Spaced repetition + difficulty scaling + mobile-first
- Uses skill graphs (prerequisites)
- A/B tests every feature change
- Result: Highest engagement of any language app

**Carnegie Learning's ALEKS**:
- Assessment and Learning in Knowledge Spaces (ALEKS)
- Uses knowledge space theory (prerequisites)
- Recommends next best item based on knowledge gaps
- Used in K-12 and higher ed math courses

**Georgia Tech's JILL Watson**:
- AI teaching assistant for online courses
- Predicts which students will struggle
- Recommends interventions (tutoring, peer groups)
- Improved retention rates

**MIT's RELATE (Residential Education + Advanced Technologies)**:
- Adaptive learning in physics and engineering
- Uses pretests to identify misconceptions
- Personalizes lecture pace and examples
- Increased learning gains 15-20%

### Evaluation Metrics for Adaptive Systems

```python
class AdaptiveSystemMetrics:
    """Measure effectiveness of adaptive learning systems."""

    def learning_outcome_metrics(self, students_adaptive, students_control):
        """Primary metrics: Did students learn better?"""
        return {
            'final_score_improvement': self.compare_final_scores(students_adaptive, students_control),
            'knowledge_retention': self.measure_retention_weeks_later(students_adaptive),
            'skill_transfer': self.measure_transfer_to_new_domain(students_adaptive)
        }

    def engagement_metrics(self, students):
        """Secondary metrics: Are students engaged?"""
        return {
            'completion_rate': self.get_completion_rate(students),
            'time_on_task': self.get_avg_time_spent(students),
            'repeat_usage': self.get_reattempt_rate(students),
            'satisfaction': self.get_student_satisfaction_rating(students)
        }

    def efficiency_metrics(self, students_adaptive, students_control):
        """Efficiency: Same results with less time?"""
        return {
            'time_to_mastery': self.compare_time_to_mastery(students_adaptive, students_control),
            'items_to_mastery': self.compare_num_items_to_mastery(students_adaptive, students_control)
        }

    def equity_metrics(self, students_by_demographic):
        """Equity: Are benefits distributed fairly?"""
        improvements_by_group = {}
        for group_name, students in students_by_demographic.items():
            improvements_by_group[group_name] = self.calculate_improvement(students)

        return {
            'improvement_by_group': improvements_by_group,
            'group_with_highest_gain': max(improvements_by_group, key=improvements_by_group.get),
            'disparity_reduction': self.measure_disparity_reduction(improvements_by_group)
        }
```

---

**Version**: 2.0
**Last Updated**: 2025-11-19
**Maintained by**: CLAUDE_SKILLS Education Technology Domain

# Student Analytics & Learning Intelligence Skill

## Purpose

You are an expert in learning analytics, educational data mining, predictive modeling, and data-driven interventions. You build systems that identify at-risk students, optimize learning pathways, and provide actionable insights through evidence-based analysis of learner behavior and performance data.

## Core Competencies

### Analytics Frameworks

**Descriptive Analytics** (What happened?):
- Enrollment trends: Track course fill rates, demographic breakdowns
- Engagement metrics: Active learners, content access patterns, time-on-task
- Completion rates: Course progression, dropout points, time to completion
- Performance distributions: Grade histograms, score trends, participation levels
- Dashboard design: Real-time monitoring, instructor views, student dashboards

**Predictive Analytics** (What will happen?):
- **At-risk identification**: Early warning systems using logistic regression, random forests
- **Course completion prediction**: Predict likelihood of passing/failing
- **Grade forecasting**: Estimate final grade trajectory
- **Engagement prediction**: Identify students likely to disengage
- **Churn prediction**: Predict dropout risk in distance education
- **Time-to-graduation**: Estimate completion timeline

**Prescriptive Analytics** (What should happen?):
- **Intervention recommendations**: Suggest tutoring, course adjustments, study strategies
- **Optimal study schedules**: Recommend spaced repetition timing
- **Content recommendations**: Suggest resources based on learning needs
- **Instructor actions**: Alert instructors to intervene with at-risk students
- **Curriculum adjustments**: Identify problematic topics needing redesign

### Data Architecture & Pipeline

**Event Stream Processing**:
```python
class xAPIEventCollector:
    """
    Collect and process xAPI (Experience API) events from all learning activities.
    Standard format: Actor, Verb, Object, Result, Context
    """

    def create_event(self, actor_id, verb, object_id, result=None, context=None):
        """
        Create an xAPI statement for a learning interaction.

        Example: Student submitted assignment
        {
            "actor": {"mbox": "mailto:student@example.com"},
            "verb": {"id": "http://adlnet.gov/expapi/verbs/submitted"},
            "object": {"id": "http://example.com/assignments/123"},
            "result": {
                "score": {"raw": 85, "min": 0, "max": 100},
                "duration": "PT50M",
                "completion": true
            },
            "timestamp": "2025-11-19T14:30:00Z"
        }
        """
        event = {
            'actor_id': actor_id,
            'verb': verb,
            'object_id': object_id,
            'result': result or {},
            'context': context or {},
            'timestamp': datetime.utcnow()
        }
        self.send_to_lrs(event)
        return event

    def send_to_lrs(self, event):
        """Send event to Learning Record Store."""
        # Could use TinCan.js, node-xapi, or custom HTTP POST
        pass
```

**ETL Pipeline with Apache Spark**:
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, window

spark = SparkSession.builder \
    .appName("EducationAnalytics") \
    .getOrCreate()

# Read xAPI events from Kafka stream
events_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "lms-events") \
    .load()

# Parse JSON events
parsed_events = events_df.select(
    col("value").cast("string").alias("event_json")
).select(
    from_json(col("event_json"), event_schema).alias("event")
).select("event.*")

# Calculate engagement metrics (tumbling window, 1 hour)
engagement_metrics = parsed_events \
    .groupBy(
        window(col("timestamp"), "1 hour"),
        col("student_id"),
        col("course_id")
    ) \
    .agg(
        count("*").alias("interactions"),
        avg("duration").alias("avg_duration"),
        count(when(col("success"), 1)).alias("correct_answers")
    )

# Write to data warehouse
engagement_metrics.writeStream \
    .format("parquet") \
    .option("path", "s3://warehouse/engagement/") \
    .option("checkpointLocation", "s3://checkpoints/engagement/") \
    .start()
```

**Data Warehouse Schema**:
```sql
-- Fact table: Learning interactions
CREATE TABLE fact_interactions (
  interaction_id INT PRIMARY KEY,
  student_id INT,
  course_id INT,
  content_id INT,
  interaction_type VARCHAR(50),  -- view, submit, attempt, respond
  duration_seconds INT,
  success BOOLEAN,
  timestamp TIMESTAMP,
  device_type VARCHAR(50)
);

-- Dimension table: Student profiles
CREATE TABLE dim_students (
  student_id INT PRIMARY KEY,
  cohort VARCHAR(50),
  program VARCHAR(100),
  enrollment_date DATE,
  previous_gpa DECIMAL(3,2),
  first_generation BOOLEAN
);

-- Fact table: Assessment results
CREATE TABLE fact_assessments (
  assessment_id INT PRIMARY KEY,
  student_id INT,
  course_id INT,
  assessment_type VARCHAR(50),  -- quiz, exam, assignment
  raw_score INT,
  max_score INT,
  percentage_score DECIMAL(5,2),
  attempts INT,
  time_spent_seconds INT,
  submission_time TIMESTAMP
);

-- Fact table: Course progress
CREATE TABLE fact_progress (
  progress_id INT PRIMARY KEY,
  student_id INT,
  course_id INT,
  week INT,
  modules_completed INT,
  assignments_submitted INT,
  assessments_completed INT,
  cumulative_engagement_minutes INT
);
```

### Predictive Modeling

**At-Risk Student Identification**:
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd

class AtRiskPredictor:
    """Identify students at risk of failing using machine learning."""

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10)
        self.scaler = StandardScaler()

    def extract_features(self, student_id, course_id):
        """Extract features for a student in a course."""
        # Query data warehouse for student features
        features = {
            # Engagement features
            'days_since_last_login': self.get_days_since_login(student_id),
            'avg_daily_interactions': self.get_avg_interactions(student_id),
            'modules_completed_pct': self.get_module_completion(student_id, course_id),

            # Performance features
            'current_gpa': self.get_current_gpa(student_id, course_id),
            'assignment_submission_rate': self.get_submission_rate(student_id, course_id),
            'average_quiz_score': self.get_avg_quiz_score(student_id, course_id),

            # Behavior features
            'forum_participation': self.get_forum_posts(student_id, course_id),
            'time_to_submit_assignments': self.get_submit_delay(student_id, course_id),

            # Demographic features
            'first_generation': self.is_first_gen(student_id),
            'prior_gpa': self.get_prior_gpa(student_id)
        }
        return pd.Series(features)

    def predict_risk(self, student_id, course_id):
        """Predict if student is at-risk (probability of failing)."""
        features = self.extract_features(student_id, course_id)
        X = self.scaler.transform(features.values.reshape(1, -1))
        risk_probability = self.model.predict_proba(X)[0][1]

        return {
            'risk_level': 'high' if risk_probability > 0.7 else 'medium' if risk_probability > 0.4 else 'low',
            'risk_score': risk_probability,
            'recommended_actions': self.get_interventions(risk_probability, features)
        }

    def get_interventions(self, risk_score, features):
        """Recommend specific interventions based on features."""
        actions = []

        if features['days_since_last_login'] > 7:
            actions.append('Encourage login; assign motivational resources')

        if features['assignment_submission_rate'] < 0.5:
            actions.append('Offer deadline extensions; provide submission templates')

        if features['average_quiz_score'] < 0.6:
            actions.append('Schedule tutoring session; provide practice problems')

        if features['forum_participation'] == 0:
            actions.append('Invite to study group; assign peer mentor')

        return actions
```

**Predictive Models**:
- **Logistic Regression**: Simple, interpretable, works well for binary outcomes (pass/fail)
- **Random Forest**: Handles non-linear relationships, feature importance ranking
- **Gradient Boosting (XGBoost, LightGBM)**: High accuracy, faster training on large datasets
- **Neural Networks**: Deep learning for complex patterns in large-scale data
- **Survival Analysis**: Predict time-to-completion/dropout

### Visualization & Dashboards

**Instructor Dashboard Components**:
```javascript
// Real-time metrics for course monitoring
const instructorDashboard = {
  topMetrics: [
    { label: 'Students Enrolled', value: 145 },
    { label: 'Avg. Engagement', value: '4.2 hours/week' },
    { label: 'At-Risk Students', value: 12, alert: true },
    { label: 'Completion Rate', value: '87%' }
  ],

  charts: [
    {
      type: 'lineChart',
      title: 'Class Engagement Trend',
      data: [/* weekly engagement points */],
      xAxis: 'Week',
      yAxis: 'Avg Interactions/Student'
    },
    {
      type: 'scatterPlot',
      title: 'Student Performance vs. Engagement',
      xAxis: 'Time Spent (hours)',
      yAxis: 'Current Grade (%)',
      highlight: 'at-risk students'
    },
    {
      type: 'heatmap',
      title: 'Content Difficulty Heatmap',
      data: 'module x difficulty matrix',
      insight: 'Shows which modules have highest failure rates'
    }
  ],

  atRiskAlerts: [
    {
      studentId: 'S123',
      name: 'John Doe',
      riskScore: 0.85,
      lastActive: '3 days ago',
      actions: ['Message sent', 'Tutoring scheduled']
    }
  ]
};
```

**Student Dashboard Components**:
```javascript
const studentDashboard = {
  courseProgress: {
    title: 'Course Progress',
    completed: 8,
    total: 12,
    percentage: 67,
    estimatedCompletionDate: '2025-12-15'
  },

  gradeTracker: {
    currentGPA: 3.4,
    trend: 'improving',
    categoryBreakdown: {
      'Assignments': { score: 85, weight: 30 },
      'Quizzes': { score: 78, weight: 20 },
      'Exams': { score: 82, weight: 40 },
      'Participation': { score: 90, weight: 10 }
    }
  },

  learningRecommendations: [
    'You struggled with Week 3 content. Review the tutorial video.',
    'Great job! You\'re ahead of pace. Challenge yourself with extensions.',
    'You\'ve been inactive for 3 days. Complete Assignment 5 by Friday.'
  ],

  studyResources: [
    'Tutoring appointment available Thursday 3pm',
    'Peer study group meets Tuesday evening',
    'Supplementary practice problems for Topic X'
  ]
};
```

### Privacy & Compliance

**FERPA Compliance**:
- Never expose student data to other students (except aggregate, anonymized data)
- Maintain secure access logs for all student record access
- Allow students to request their own data
- Implement data retention policies (typically 1-3 years after course)

**GDPR Compliance**:
- Obtain explicit consent before collecting/processing data
- Right to access: Students can download their data in standard format
- Right to deletion: Implement data purge mechanisms
- Privacy by design: Minimize data collection; use pseudonymization

**Data Privacy Techniques**:
```python
from cryptography.fernet import Fernet
from diffprivlib.models import LogisticRegression as DPLogisticRegression

class PrivacyPreservingAnalytics:
    """Implement privacy-preserving techniques for analytics."""

    def differential_privacy_aggregation(self, student_scores, epsilon=1.0):
        """
        Add noise to aggregate statistics to protect individual privacy.
        epsilon: privacy budget (lower = more noise/privacy)
        """
        import numpy as np

        # Add Laplace noise to average
        sensitivity = 100 / len(student_scores)  # Max possible change
        scale = sensitivity / epsilon
        noise = np.random.laplace(0, scale)

        mean_score = np.mean(student_scores) + noise
        return mean_score

    def train_differentially_private_model(self, X, y, epsilon=1.0):
        """Train ML model with differential privacy guarantees."""
        # Use differentially private logistic regression
        dp_model = DPLogisticRegression(epsilon=epsilon)
        dp_model.fit(X, y)
        return dp_model

    def anonymize_student_data(self, student_records):
        """Remove identifying information before analysis."""
        anonymized = []
        for record in student_records:
            # Keep only derived features, remove IDs, emails, names
            anon_record = {
                'cohort': record['cohort'],
                'program': record['program'],
                'engagement_score': record['engagement_score'],
                'performance_metrics': record['performance_metrics']
            }
            anonymized.append(anon_record)
        return anonymized
```

**Explainable AI (XAI)**:
- Use LIME (Local Interpretable Model-agnostic Explanations) to explain predictions
- Show feature importance: Which factors contributed most to at-risk prediction?
- Transparent rules: If-then rules for easy understanding
- Example: "Student is at-risk because: low quiz scores (weight: 0.4), missed assignments (0.3), low engagement (0.3)"

### Tools & Technologies

**Data Collection & Stream Processing**:
- **Apache Kafka**: Real-time event streaming
- **AWS Kinesis**: Managed stream processing
- **Logstash/Fluentd**: Log aggregation
- **xAPI Libraries**: TinCan.js, node-xapi (send events to LRS)

**Data Warehouse & Analysis**:
- **Snowflake**: Cloud data warehouse with great EDU pricing
- **BigQuery**: Google's serverless data warehouse
- **AWS Redshift**: Amazon's data warehouse
- **PostgreSQL**: Traditional relational database
- **InfluxDB**: Time-series database (for engagement over time)

**Analytics & ML**:
- **Python Stack**: pandas, NumPy, scikit-learn, XGBoost, PyTorch
- **R**: tidyverse, caret, shiny (dashboards)
- **Apache Spark**: Distributed computing for big datasets
- **Tableau/Power BI**: Commercial BI tools
- **Plotly/D3.js**: Custom interactive visualizations

**Privacy & Compliance**:
- **DiffPrivLib**: Differential privacy in Python
- **OPAL**: Open Policy Administration Layer (data governance)
- **Apache Atlas**: Metadata management and compliance

### Industry Examples & Case Studies

**Early Warning Systems**:
- **Purdue SIGNALS**: Uses prior GPA, current course performance, engagement
- **University of Phoenix**: Predictive alerts for at-risk completions
- **Georgia Tech OMS**: Identifies students likely to withdraw

**Personalization at Scale**:
- **Coursera**: Recommend courses based on learner history and peer data
- **edX**: Adaptive problem difficulty using IRT
- **Duolingo**: Real-time spaced repetition scheduling

### Best Practices

1. **Start Simple**: Begin with descriptive analytics before complex predictive models
2. **Validate Models**: Use train/test splits; measure precision, recall, F1-score
3. **Handle Bias**: Audit models for demographic disparities; track fairness metrics
4. **Transparency**: Explain decisions to students and instructors
5. **Action-Oriented**: Focus analytics on decisions instructors/students will make
6. **Feedback Loops**: Continuously improve interventions based on outcomes

---

**Version**: 2.0
**Last Updated**: 2025-11-19
**Maintained by**: CLAUDE_SKILLS Education Technology Domain

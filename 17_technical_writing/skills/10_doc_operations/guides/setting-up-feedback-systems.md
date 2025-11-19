# Setting Up User Feedback Systems for Documentation

## Overview

User feedback systems capture structured and unstructured input about documentation quality, usability, and effectiveness. This guide covers implementation strategies for collecting, analyzing, and acting on feedback to continuously improve documentation.

## Why Feedback Systems Matter

**Benefits:**
- Identify documentation gaps and problems quickly
- Understand actual user needs vs. assumptions
- Prioritize improvements based on real usage patterns
- Build user trust through responsiveness
- Measure documentation effectiveness
- Create feedback loop for continuous improvement

**Feedback Types:**
- Rating surveys (thumbs up/down, NPS)
- Detailed feedback forms
- Search behavior analysis
- User interaction tracking
- Support ticket categorization
- Community feedback (forums, social media)

## Part 1: In-Page Feedback Mechanisms

### Implement Quick Feedback Widget

```jsx
// components/FeedbackWidget.jsx
import React, { useState } from 'react';
import styles from './FeedbackWidget.module.css';

export function FeedbackWidget({ pageTitle, pageUrl }) {
  const [rating, setRating] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleRating = async (value) => {
    setRating(value);

    // Send quick feedback
    await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'quick_rating',
        rating: value,
        page_title: pageTitle,
        page_url: pageUrl,
        timestamp: new Date().toISOString()
      })
    });

    if (value <= 2) {
      setShowForm(true);
    } else {
      setTimeout(() => setRating(null), 2000);
    }
  };

  const handleDetailedFeedback = async () => {
    if (!feedback.trim()) return;

    await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'detailed_feedback',
        rating,
        feedback,
        page_title: pageTitle,
        page_url: pageUrl,
        timestamp: new Date().toISOString()
      })
    });

    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      setRating(null);
      setFeedback('');
      setShowForm(false);
    }, 2000);
  };

  return (
    <div className={styles.feedbackWidget}>
      <p className={styles.label}>Was this page helpful?</p>

      <div className={styles.ratingButtons}>
        <button
          className={`${styles.btn} ${rating === 5 ? styles.active : ''}`}
          onClick={() => handleRating(5)}
          title="Very helpful"
        >
          👍 Yes
        </button>
        <button
          className={`${styles.btn} ${rating === 1 ? styles.active : ''}`}
          onClick={() => handleRating(1)}
          title="Not helpful"
        >
          👎 No
        </button>
      </div>

      {showForm && !submitted && (
        <div className={styles.feedbackForm}>
          <p>Sorry this page wasn't helpful. What could we improve?</p>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Your feedback..."
            rows="3"
          />
          <button
            className={styles.submitBtn}
            onClick={handleDetailedFeedback}
          >
            Send Feedback
          </button>
        </div>
      )}

      {submitted && (
        <p className={styles.success}>Thank you for your feedback!</p>
      )}
    </div>
  );
}
```

### Add Feedback to All Pages

```javascript
// pages/[...slug].js - Integrate feedback widget
import { FeedbackWidget } from '../components/FeedbackWidget';

export default function DocPage({ pageTitle, pageUrl }) {
  return (
    <div className="doc-container">
      <article>
        {/* Page content */}
      </article>

      <footer className="doc-footer">
        <FeedbackWidget
          pageTitle={pageTitle}
          pageUrl={pageUrl}
        />
      </footer>
    </div>
  );
}
```

## Part 2: Comprehensive Feedback API

### Build Feedback Collection Backend

```python
# app.py - Flask feedback API
from flask import Flask, request, jsonify
from datetime import datetime
import json
from pathlib import Path

app = Flask(__name__)

class FeedbackCollector:
    def __init__(self, storage_path='feedback'):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

    def save_feedback(self, feedback_data):
        """Save feedback to JSON file"""
        feedback_data['timestamp'] = datetime.now().isoformat()
        feedback_data['id'] = self.generate_id()

        month_file = self.storage_path / f"{datetime.now().strftime('%Y-%m')}.jsonl"

        with open(month_file, 'a') as f:
            f.write(json.dumps(feedback_data) + '\n')

        return feedback_data['id']

    def generate_id(self):
        """Generate unique feedback ID"""
        import uuid
        return str(uuid.uuid4())[:8]

    def get_feedback_summary(self, page_url=None, days=30):
        """Get feedback summary for analysis"""
        feedback_items = self.load_recent_feedback(days)

        if page_url:
            feedback_items = [f for f in feedback_items if f.get('page_url') == page_url]

        if not feedback_items:
            return None

        summary = {
            'total_responses': len(feedback_items),
            'average_rating': sum(f.get('rating', 0) for f in feedback_items) / len(feedback_items),
            'positive_count': sum(1 for f in feedback_items if f.get('rating', 0) >= 4),
            'negative_count': sum(1 for f in feedback_items if f.get('rating', 0) <= 2),
            'detailed_feedback_count': sum(1 for f in feedback_items if f.get('feedback'))
        }

        return summary

    def load_recent_feedback(self, days=30):
        """Load feedback from last N days"""
        import glob
        from datetime import timedelta

        feedback_items = []
        cutoff_date = datetime.now() - timedelta(days=days)

        for file in self.storage_path.glob('*.jsonl'):
            with open(file, 'r') as f:
                for line in f:
                    item = json.loads(line)
                    item_date = datetime.fromisoformat(item['timestamp'])
                    if item_date > cutoff_date:
                        feedback_items.append(item)

        return feedback_items

feedback_collector = FeedbackCollector()

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Receive feedback submission"""
    try:
        data = request.json
        feedback_id = feedback_collector.save_feedback(data)

        return jsonify({
            'status': 'success',
            'feedback_id': feedback_id
        }), 201

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/feedback/summary', methods=['GET'])
def get_feedback_summary():
    """Get feedback summary (admin only)"""
    page_url = request.args.get('page_url')
    days = request.args.get('days', 30, type=int)

    summary = feedback_collector.get_feedback_summary(page_url, days)

    return jsonify(summary if summary else {})

@app.route('/api/feedback/export', methods=['GET'])
def export_feedback():
    """Export feedback for analysis"""
    days = request.args.get('days', 90, type=int)
    feedback_items = feedback_collector.load_recent_feedback(days)

    return jsonify({
        'export_date': datetime.now().isoformat(),
        'period_days': days,
        'total_items': len(feedback_items),
        'items': feedback_items
    })

if __name__ == '__main__':
    app.run(debug=False)
```

## Part 3: Feedback Analysis Dashboard

### Create Analytics Dashboard

```python
# feedback_analytics.py
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta

class FeedbackAnalytics:
    """Analyze feedback data for insights"""

    def __init__(self, feedback_items):
        self.feedback_items = feedback_items
        self.df = pd.DataFrame(feedback_items)

    def analyze_satisfaction_trends(self):
        """Analyze satisfaction trends over time"""
        self.df['date'] = pd.to_datetime(self.df['timestamp']).dt.date
        daily_satisfaction = self.df.groupby('date')['rating'].agg(['mean', 'count'])

        return {
            'daily_trends': daily_satisfaction.to_dict(),
            'trend_direction': 'improving' if daily_satisfaction['mean'].iloc[-1] > daily_satisfaction['mean'].iloc[0] else 'declining'
        }

    def analyze_problem_pages(self):
        """Identify pages with low satisfaction"""
        low_rating = self.df[self.df['rating'] <= 2]
        problem_pages = low_rating['page_url'].value_counts().head(10)

        return {
            'problem_pages': problem_pages.to_dict(),
            'total_negative_feedback': len(low_rating),
            'top_issues': self.extract_common_issues(low_rating)
        }

    def extract_common_issues(self, low_rating_df):
        """Extract common issues from feedback text"""
        feedback_texts = low_rating_df['feedback'].dropna().tolist()

        # Simple keyword extraction
        common_keywords = Counter()
        for text in feedback_texts:
            words = text.lower().split()
            for word in words:
                if len(word) > 4:  # Filter short words
                    common_keywords[word] += 1

        return dict(common_keywords.most_common(10))

    def analyze_feedback_sentiment(self):
        """Basic sentiment analysis of feedback"""
        feedback_with_text = self.df[self.df['feedback'].notna()]

        positive_keywords = ['helpful', 'clear', 'great', 'excellent', 'works', 'thanks']
        negative_keywords = ['confusing', 'unclear', 'broken', 'outdated', 'wrong', 'missing']

        positive_count = 0
        negative_count = 0

        for text in feedback_with_text['feedback']:
            text_lower = text.lower()
            if any(kw in text_lower for kw in positive_keywords):
                positive_count += 1
            if any(kw in text_lower for kw in negative_keywords):
                negative_count += 1

        return {
            'positive_mentions': positive_count,
            'negative_mentions': negative_count,
            'sentiment_ratio': positive_count / (negative_count + 1)
        }

    def analyze_by_page_section(self):
        """Analyze feedback by documentation section"""
        section_analysis = self.df.groupby('page_title').agg({
            'rating': ['mean', 'count'],
            'feedback': lambda x: sum(1 for val in x if pd.notna(val))
        })

        return section_analysis.to_dict()

    def generate_insights_report(self):
        """Generate actionable insights"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'satisfaction_trends': self.analyze_satisfaction_trends(),
            'problem_pages': self.analyze_problem_pages(),
            'sentiment_analysis': self.analyze_feedback_sentiment(),
            'section_analysis': self.analyze_by_page_section(),
            'recommendations': self.generate_recommendations()
        }

        return report

    def generate_recommendations(self):
        """Generate recommendations based on feedback"""
        problem_pages = self.analyze_problem_pages()
        recommendations = []

        for page, count in problem_pages['problem_pages'].items():
            if count >= 3:
                recommendations.append({
                    'action': 'Review and update page',
                    'page': page,
                    'reason': f'{count} negative feedback submissions',
                    'priority': 'high' if count >= 5 else 'medium'
                })

        return recommendations
```

## Part 4: Feedback Review Workflow

### Set Up Review Process

```yaml
# feedback_workflow.yml
feedback_review_process:
  frequency: daily
  responsibilities:
    - role: Documentation Team
      tasks:
        - review_new_feedback
        - categorize_issues
        - identify_patterns

    - role: Product Manager
      tasks:
        - review_problem_pages
        - prioritize_improvements
        - allocate_resources

    - role: Technical Writer
      tasks:
        - execute_updates
        - verify_fixes
        - track_progress

  escalation:
    critical_issues:
      criteria:
        - multiple_reports: 5+
        - severity: high
        - impact: blocking_users
      action: immediate_review
      owner: team_lead

  response_guidelines:
    minor_typos:
      sla: 3_days
    broken_examples:
      sla: 1_day
    missing_content:
      sla: 5_days
    outdated_information:
      sla: 2_days
```

### Feedback Processing Template

```markdown
# Weekly Feedback Review Report

**Week of:** 2024-11-19

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Feedback | 87 |
| Average Rating | 4.1/5 |
| Pages with Feedback | 34 |
| Detailed Feedback | 23 |

## Top Issues

### High Priority (Action This Week)

1. **Broken Code Example - API Authentication**
   - Pages affected: /docs/api/authentication
   - Feedback count: 5
   - User impact: Blocking
   - Status: IN PROGRESS
   - Owner: John Smith
   - Due: 2024-11-21

2. **Missing Configuration Step**
   - Pages affected: /docs/setup/configuration
   - Feedback count: 3
   - User impact: High
   - Status: ASSIGNED
   - Owner: Jane Doe
   - Due: 2024-11-24

### Medium Priority (Action Next Week)

3. **Unclear Explanation**
   - Pages affected: /docs/concepts/caching
   - Feedback count: 2
   - Status: IN BACKLOG
   - Owner: TBD

## Positive Feedback

- "Excellent tutorial for getting started" - 5 stars
- "Clear examples with good explanations" - 5 stars
- "Fixed my issue quickly" - 5 stars

## Metrics Tracking

- Pages improved this week: 4
- Feedback issues resolved: 8
- Average resolution time: 2.3 days

## Next Week Priorities

- [ ] Complete API authentication fix
- [ ] Add missing configuration steps
- [ ] Review caching documentation for clarity
- [ ] Update outdated version references
```

## Part 5: Survey-Based Feedback

### Implement NPS Survey

```javascript
// components/NPSSurvey.jsx
import React, { useState } from 'react';

export function NPSSurvey({ pageUrl }) {
  const [score, setScore] = useState(null);
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    await fetch('/api/feedback/nps', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        score,
        comment,
        page_url: pageUrl,
        timestamp: new Date().toISOString()
      })
    });

    setSubmitted(true);
  };

  if (submitted) {
    return <p>Thank you for your feedback!</p>;
  }

  return (
    <div className="nps-survey">
      <h3>How likely are you to recommend this documentation?</h3>
      <p className="subtitle">0 (Not likely) - 10 (Very likely)</p>

      <div className="nps-scale">
        {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
          <button
            key={num}
            onClick={() => setScore(num)}
            className={score === num ? 'selected' : ''}
          >
            {num}
          </button>
        ))}
      </div>

      {score !== null && (
        <textarea
          placeholder="What could we improve?"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
        />
      )}

      <button onClick={handleSubmit} disabled={score === null}>
        Submit
      </button>
    </div>
  );
}
```

## Part 6: Integration with Support Systems

### Link Documentation Feedback to Support

```python
# support_integration.py
class SupportIntegration:
    """Link documentation feedback to support tickets"""

    def create_ticket_from_feedback(self, feedback_item, ticket_system):
        """Create support ticket from documentation feedback"""
        ticket = {
            'title': f"Documentation Issue: {feedback_item['page_title']}",
            'description': feedback_item.get('feedback', 'User reported issue'),
            'priority': self.determine_priority(feedback_item),
            'source': 'documentation_feedback',
            'page_url': feedback_item['page_url'],
            'rating': feedback_item.get('rating'),
            'feedback_id': feedback_item['id']
        }

        return ticket_system.create(ticket)

    def determine_priority(self, feedback_item):
        """Determine ticket priority"""
        rating = feedback_item.get('rating', 3)

        if rating == 1:
            return 'critical'
        elif rating == 2:
            return 'high'
        else:
            return 'medium'

    def track_feedback_resolution(self, feedback_id, ticket_id):
        """Track when documentation feedback is resolved"""
        # Link feedback to ticket
        # Update when ticket is resolved
        # Close feedback loop
        pass

    def analyze_support_doc_alignment(self):
        """Analyze correlation between support tickets and documentation feedback"""
        # Compare common issues in support tickets with documentation feedback
        # Identify gaps in documentation coverage
        pass
```

## Part 7: Feedback Automation

### Auto-Routing and Analysis

```python
# feedback_automation.py
from enum import Enum

class FeedbackCategory(Enum):
    TYPO = "typo"
    BROKEN_LINK = "broken_link"
    BROKEN_CODE = "broken_code"
    UNCLEAR = "unclear"
    MISSING = "missing"
    OUTDATED = "outdated"
    OTHER = "other"

class FeedbackAutoRouter:
    """Automatically route feedback to appropriate team"""

    def categorize_feedback(self, feedback_text):
        """Auto-categorize feedback"""
        text_lower = feedback_text.lower()

        categorization_rules = {
            FeedbackCategory.TYPO: ['typo', 'spelling', 'grammar'],
            FeedbackCategory.BROKEN_LINK: ['broken link', 'link broken', 'link doesn\'t work'],
            FeedbackCategory.BROKEN_CODE: ['code doesn\'t work', 'broken code', 'error', 'doesn\'t run'],
            FeedbackCategory.UNCLEAR: ['unclear', 'confusing', 'hard to understand'],
            FeedbackCategory.MISSING: ['missing', 'not documented', 'where is'],
            FeedbackCategory.OUTDATED: ['outdated', 'no longer works', 'deprecated', 'old version']
        }

        for category, keywords in categorization_rules.items():
            if any(kw in text_lower for kw in keywords):
                return category

        return FeedbackCategory.OTHER

    def route_to_owner(self, feedback_item):
        """Route feedback to appropriate owner"""
        category = self.categorize_feedback(feedback_item.get('feedback', ''))

        routing = {
            FeedbackCategory.TYPO: 'technical_writer',
            FeedbackCategory.BROKEN_LINK: 'technical_writer',
            FeedbackCategory.BROKEN_CODE: 'developer',
            FeedbackCategory.UNCLEAR: 'technical_writer',
            FeedbackCategory.MISSING: 'product_manager',
            FeedbackCategory.OUTDATED: 'product_manager',
            FeedbackCategory.OTHER: 'team_lead'
        }

        return {
            'category': category,
            'owner': routing.get(category),
            'priority': self.determine_priority(category),
            'estimated_time': self.estimate_time(category)
        }

    def determine_priority(self, category):
        """Priority based on category"""
        priorities = {
            FeedbackCategory.BROKEN_CODE: 'critical',
            FeedbackCategory.BROKEN_LINK: 'high',
            FeedbackCategory.OUTDATED: 'high',
            FeedbackCategory.MISSING: 'medium',
            FeedbackCategory.UNCLEAR: 'medium',
            FeedbackCategory.TYPO: 'low'
        }
        return priorities.get(category, 'medium')

    def estimate_time(self, category):
        """Estimate fix time by category"""
        estimates = {
            FeedbackCategory.TYPO: 0.25,
            FeedbackCategory.BROKEN_LINK: 0.5,
            FeedbackCategory.TYPO: 0.25,
            FeedbackCategory.BROKEN_CODE: 2,
            FeedbackCategory.UNCLEAR: 1,
            FeedbackCategory.MISSING: 3,
            FeedbackCategory.OUTDATED: 2
        }
        return estimates.get(category, 1)
```

## Part 8: Closing the Feedback Loop

### Notify Users of Improvements

```javascript
// components/FeedbackResponse.jsx
export function FeedbackNotification({ hasUpdatesSinceFeedback }) {
  if (!hasUpdatesSinceFeedback) return null;

  return (
    <div className="feedback-notification">
      <p>
        ✓ We received your feedback and have made improvements to this page.
        <a href="#"> See what's changed</a>
      </p>
    </div>
  );
}
```

## Conclusion

A comprehensive feedback system enables continuous documentation improvement by capturing user insights and acting on them systematically. Implement in-page feedback, analyze patterns, and create a workflow that responds quickly to user needs.


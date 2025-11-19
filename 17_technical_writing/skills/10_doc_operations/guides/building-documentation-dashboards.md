# Building Documentation Dashboards: Metrics and Insights

## Overview

A documentation dashboard consolidates key performance metrics and insights into a single view, enabling stakeholders to monitor documentation health, user engagement, and business impact. This guide covers dashboard design, implementation, and metrics selection.

## Dashboard Purpose

**Use Cases:**
- Monitor documentation health and quality
- Track user engagement and satisfaction
- Measure business impact and ROI
- Identify trends and anomalies
- Support decision-making
- Communicate value to stakeholders

**Audience:**
- Documentation team
- Product management
- Engineering leads
- Executive stakeholders

## Part 1: Select Key Metrics

### Define KPI Categories

```python
# kpi_definitions.py
from dataclasses import dataclass
from typing import List
from enum import Enum

class MetricCategory(Enum):
    ENGAGEMENT = "engagement"
    QUALITY = "quality"
    SATISFACTION = "satisfaction"
    BUSINESS = "business"
    HEALTH = "health"

@dataclass
class KPI:
    name: str
    category: MetricCategory
    description: str
    target: float
    threshold_warning: float
    threshold_critical: float
    calculation_method: str
    update_frequency: str

class KPIFramework:
    """Define all tracked KPIs"""

    def __init__(self):
        self.kpis = []

    def add_engagement_kpis(self):
        """User engagement metrics"""
        self.kpis.extend([
            KPI(
                name="Monthly Page Views",
                category=MetricCategory.ENGAGEMENT,
                description="Total page views in documentation",
                target=10000,
                threshold_warning=7500,
                threshold_critical=5000,
                calculation_method="SUM(page_views)",
                update_frequency="daily"
            ),
            KPI(
                name="Unique Visitors",
                category=MetricCategory.ENGAGEMENT,
                description="Unique users accessing documentation",
                target=2000,
                threshold_warning=1500,
                threshold_critical=1000,
                calculation_method="DISTINCT(user_id)",
                update_frequency="daily"
            ),
            KPI(
                name="Avg Session Duration",
                category=MetricCategory.ENGAGEMENT,
                description="Average time spent per session",
                target=300,  # seconds
                threshold_warning=180,
                threshold_critical=120,
                calculation_method="AVG(session_duration)",
                update_frequency="daily"
            ),
            KPI(
                name="Scroll Depth",
                category=MetricCategory.ENGAGEMENT,
                description="Average percentage of page scrolled",
                target=70,  # percentage
                threshold_warning=50,
                threshold_critical=30,
                calculation_method="AVG(scroll_depth_percent)",
                update_frequency="daily"
            ),
            KPI(
                name="Return Visitor Rate",
                category=MetricCategory.ENGAGEMENT,
                description="Percentage of returning visitors",
                target=35,
                threshold_warning=25,
                threshold_critical=15,
                calculation_method="COUNT(returning) / COUNT(all) * 100",
                update_frequency="weekly"
            )
        ])

    def add_quality_kpis(self):
        """Content quality metrics"""
        self.kpis.extend([
            KPI(
                name="Broken Links",
                category=MetricCategory.QUALITY,
                description="Number of broken internal/external links",
                target=0,
                threshold_warning=5,
                threshold_critical=10,
                calculation_method="COUNT(broken_links)",
                update_frequency="weekly"
            ),
            KPI(
                name="Outdated Content %",
                category=MetricCategory.QUALITY,
                description="Percentage of pages not updated in 6+ months",
                target=5,
                threshold_warning=10,
                threshold_critical=20,
                calculation_method="COUNT(>6_months_old) / COUNT(total) * 100",
                update_frequency="weekly"
            ),
            KPI(
                name="Code Example Freshness",
                category=MetricCategory.QUALITY,
                description="Percentage of code examples verified as working",
                target=95,
                threshold_warning=85,
                threshold_critical=75,
                calculation_method="COUNT(verified) / COUNT(total_examples) * 100",
                update_frequency="weekly"
            ),
            KPI(
                name="Search Success Rate",
                category=MetricCategory.QUALITY,
                description="Percentage of searches with relevant results",
                target=80,
                threshold_warning=70,
                threshold_critical=60,
                calculation_method="COUNT(clicked_result) / COUNT(searches) * 100",
                update_frequency="daily"
            )
        ])

    def add_satisfaction_kpis(self):
        """User satisfaction metrics"""
        self.kpis.extend([
            KPI(
                name="Feedback Rating",
                category=MetricCategory.SATISFACTION,
                description="Average user satisfaction rating (1-5)",
                target=4.5,
                threshold_warning=4.0,
                threshold_critical=3.5,
                calculation_method="AVG(user_rating)",
                update_frequency="daily"
            ),
            KPI(
                name="NPS Score",
                category=MetricCategory.SATISFACTION,
                description="Net Promoter Score (-100 to 100)",
                target=50,
                threshold_warning=30,
                threshold_critical=0,
                calculation_method="(Promoters - Detractors) / Total * 100",
                update_frequency="weekly"
            ),
            KPI(
                name="Helpful Rate",
                category=MetricCategory.SATISFACTION,
                description="Percentage marking page as helpful",
                target=70,
                threshold_warning=60,
                threshold_critical=50,
                calculation_method="COUNT(helpful) / COUNT(ratings) * 100",
                update_frequency="daily"
            )
        ])

    def add_business_kpis(self):
        """Business impact metrics"""
        self.kpis.extend([
            KPI(
                name="Support Tickets Reduced",
                category=MetricCategory.BUSINESS,
                description="Estimated tickets resolved by documentation",
                target=25,  # percentage
                threshold_warning=15,
                threshold_critical=10,
                calculation_method="COUNT(doc_resolved) / COUNT(total) * 100",
                update_frequency="monthly"
            ),
            KPI(
                name="Onboarding Time",
                category=MetricCategory.BUSINESS,
                description="Average time to first success (hours)",
                target=4,
                threshold_warning=6,
                threshold_critical=10,
                calculation_method="AVG(time_to_first_success)",
                update_frequency="monthly"
            ),
            KPI(
                name="Documentation ROI",
                category=MetricCategory.BUSINESS,
                description="Return on documentation investment (%)",
                target=300,
                threshold_warning=200,
                threshold_critical=100,
                calculation_method="(Benefits / Cost) * 100",
                update_frequency="quarterly"
            )
        ])

    def add_health_kpis(self):
        """Documentation health metrics"""
        self.kpis.extend([
            KPI(
                name="Content Coverage",
                category=MetricCategory.HEALTH,
                description="Percentage of features documented",
                target=95,
                threshold_warning=85,
                threshold_critical=75,
                calculation_method="COUNT(documented_features) / COUNT(total_features) * 100",
                update_frequency="monthly"
            ),
            KPI(
                name="Page Count Trend",
                category=MetricCategory.HEALTH,
                description="Month-over-month change in pages",
                target=0,  # healthy: stable
                threshold_warning=10,
                threshold_critical=20,
                calculation_method="(Current - Previous) / Previous * 100",
                update_frequency="monthly"
            ),
            KPI(
                name="Update Frequency",
                category=MetricCategory.HEALTH,
                description="Average days between page updates",
                target=90,
                threshold_warning=180,
                threshold_critical=365,
                calculation_method="AVG(days_since_update)",
                update_frequency="weekly"
            )
        ])

    def get_all_kpis(self):
        """Get all KPIs across categories"""
        if not self.kpis:
            self.add_engagement_kpis()
            self.add_quality_kpis()
            self.add_satisfaction_kpis()
            self.add_business_kpis()
            self.add_health_kpis()

        return self.kpis
```

## Part 2: Data Collection and Aggregation

### Build Data Pipeline

```python
# data_pipeline.py
import sqlite3
from datetime import datetime, timedelta
import json
from typing import Dict, List

class DocumentationDataPipeline:
    """Aggregate data from multiple sources"""

    def __init__(self, db_path='docs_metrics.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize metrics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Daily metrics snapshot
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_metrics (
                id INTEGER PRIMARY KEY,
                date DATE,
                page_views INTEGER,
                unique_visitors INTEGER,
                avg_session_duration REAL,
                avg_scroll_depth REAL,
                searches INTEGER,
                search_success_rate REAL,
                broken_links INTEGER,
                created_at TIMESTAMP
            )
        ''')

        # Feedback metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_metrics (
                id INTEGER PRIMARY KEY,
                date DATE,
                total_feedback INTEGER,
                avg_rating REAL,
                helpful_count INTEGER,
                unhelpful_count INTEGER,
                nps_score REAL,
                created_at TIMESTAMP
            )
        ''')

        # Content quality metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_metrics (
                id INTEGER PRIMARY KEY,
                date DATE,
                total_pages INTEGER,
                outdated_pages INTEGER,
                pages_needing_update INTEGER,
                avg_page_age_days INTEGER,
                code_examples_verified INTEGER,
                created_at TIMESTAMP
            )
        ''')

        # Business metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_metrics (
                id INTEGER PRIMARY KEY,
                date DATE,
                support_tickets_total INTEGER,
                docs_resolved_tickets INTEGER,
                avg_onboarding_time_hours REAL,
                customers_onboarded INTEGER,
                support_cost_savings REAL,
                created_at TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def aggregate_engagement_data(self, analytics_data: Dict):
        """Aggregate engagement metrics from analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO daily_metrics
            (date, page_views, unique_visitors, avg_session_duration, avg_scroll_depth, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().date(),
            analytics_data.get('page_views', 0),
            analytics_data.get('unique_visitors', 0),
            analytics_data.get('avg_session_duration', 0),
            analytics_data.get('avg_scroll_depth', 0),
            datetime.now()
        ))

        conn.commit()
        conn.close()

    def aggregate_feedback_data(self, feedback_data: Dict):
        """Aggregate feedback metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO feedback_metrics
            (date, total_feedback, avg_rating, helpful_count, unhelpful_count, nps_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().date(),
            feedback_data.get('total_feedback', 0),
            feedback_data.get('avg_rating', 0),
            feedback_data.get('helpful_count', 0),
            feedback_data.get('unhelpful_count', 0),
            feedback_data.get('nps_score', 0),
            datetime.now()
        ))

        conn.commit()
        conn.close()

    def aggregate_quality_data(self, quality_data: Dict):
        """Aggregate content quality metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO quality_metrics
            (date, total_pages, outdated_pages, pages_needing_update, avg_page_age_days,
             code_examples_verified, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().date(),
            quality_data.get('total_pages', 0),
            quality_data.get('outdated_pages', 0),
            quality_data.get('pages_needing_update', 0),
            quality_data.get('avg_page_age_days', 0),
            quality_data.get('code_examples_verified', 0),
            datetime.now()
        ))

        conn.commit()
        conn.close()

    def get_metrics_summary(self, days=30):
        """Get aggregated metrics for dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).date()

        # Engagement metrics
        cursor.execute('''
            SELECT
                SUM(page_views) as total_views,
                SUM(unique_visitors) as total_visitors,
                AVG(avg_session_duration) as avg_session,
                AVG(avg_scroll_depth) as avg_scroll
            FROM daily_metrics
            WHERE date >= ?
        ''', (cutoff_date,))

        engagement = cursor.fetchone()

        # Feedback metrics
        cursor.execute('''
            SELECT
                AVG(avg_rating) as avg_rating,
                AVG(nps_score) as avg_nps,
                SUM(helpful_count) as total_helpful
            FROM feedback_metrics
            WHERE date >= ?
        ''', (cutoff_date,))

        satisfaction = cursor.fetchone()

        # Quality metrics
        cursor.execute('''
            SELECT
                AVG(total_pages) as avg_pages,
                AVG(outdated_pages) as avg_outdated,
                AVG(avg_page_age_days) as avg_age,
                AVG(code_examples_verified) as avg_verified
            FROM quality_metrics
            WHERE date >= ?
        ''', (cutoff_date,))

        quality = cursor.fetchone()

        conn.close()

        return {
            'period_days': days,
            'engagement': {
                'total_views': engagement[0],
                'total_visitors': engagement[1],
                'avg_session_duration': engagement[2],
                'avg_scroll_depth': engagement[3]
            },
            'satisfaction': {
                'avg_rating': satisfaction[0],
                'avg_nps': satisfaction[1],
                'total_helpful': satisfaction[2]
            },
            'quality': {
                'avg_pages': quality[0],
                'avg_outdated': quality[1],
                'avg_page_age_days': quality[2],
                'avg_verified_examples': quality[3]
            }
        }
```

## Part 3: Build Dashboard Web Application

### Create Dashboard Frontend

```jsx
// pages/dashboard.jsx
import React, { useEffect, useState } from 'react';
import MetricCard from '../components/MetricCard';
import TrendChart from '../components/TrendChart';
import HealthStatus from '../components/HealthStatus';
import AlertPanel from '../components/AlertPanel';
import styles from '../styles/Dashboard.module.css';

export default function DocumentationDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [period, setPeriod] = useState(30);
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, [period]);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`/api/dashboard/metrics?days=${period}`);
      const data = await response.json();
      setMetrics(data);
      setAlerts(data.alerts || []);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className={styles.loading}>Loading dashboard...</div>;
  }

  return (
    <div className={styles.dashboard}>
      <header className={styles.header}>
        <h1>Documentation Dashboard</h1>

        <div className={styles.controls}>
          <select value={period} onChange={(e) => setPeriod(Number(e.target.value))}>
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>

          <button onClick={fetchDashboardData}>Refresh</button>
        </div>
      </header>

      {alerts.length > 0 && (
        <AlertPanel alerts={alerts} />
      )}

      <div className={styles.gridContainer}>
        {/* Engagement Section */}
        <section className={styles.section}>
          <h2>Engagement</h2>

          <div className={styles.metricsGrid}>
            <MetricCard
              label="Page Views"
              value={metrics?.engagement.total_views}
              target={10000}
              trend={+5.2}
              status="good"
            />

            <MetricCard
              label="Unique Visitors"
              value={metrics?.engagement.total_visitors}
              target={2000}
              trend={+3.1}
              status="good"
            />

            <MetricCard
              label="Avg Session Duration"
              value={Math.round(metrics?.engagement.avg_session_duration) + 's'}
              target="5 min"
              trend={-2.5}
              status="warning"
            />

            <MetricCard
              label="Scroll Depth"
              value={Math.round(metrics?.engagement.avg_scroll_depth) + '%'}
              target="70%"
              trend={+1.2}
              status="good"
            />
          </div>

          <TrendChart
            title="Monthly Page Views Trend"
            dataKey="page_views"
            period={period}
          />
        </section>

        {/* Satisfaction Section */}
        <section className={styles.section}>
          <h2>Satisfaction</h2>

          <div className={styles.metricsGrid}>
            <MetricCard
              label="Avg Rating"
              value={(metrics?.satisfaction.avg_rating || 0).toFixed(1) + '/5'}
              target="4.5"
              status="good"
            />

            <MetricCard
              label="NPS Score"
              value={Math.round(metrics?.satisfaction.avg_nps || 0)}
              target="50"
              status="warning"
            />

            <MetricCard
              label="Helpful %"
              value={Math.round((metrics?.satisfaction.total_helpful || 0) / metrics?.engagement.total_visitors * 100) + '%'}
              target="70%"
              status="good"
            />
          </div>
        </section>

        {/* Quality Section */}
        <section className={styles.section}>
          <h2>Content Quality</h2>

          <div className={styles.metricsGrid}>
            <MetricCard
              label="Total Pages"
              value={Math.round(metrics?.quality.avg_pages || 0)}
              status="neutral"
            />

            <MetricCard
              label="Outdated Pages"
              value={Math.round(metrics?.quality.avg_outdated || 0)}
              target="5"
              status={metrics?.quality.avg_outdated > 10 ? 'critical' : 'warning'}
            />

            <MetricCard
              label="Avg Page Age"
              value={Math.round(metrics?.quality.avg_page_age_days || 0) + ' days'}
              target="90 days"
              status="good"
            />

            <MetricCard
              label="Verified Examples"
              value={Math.round(metrics?.quality.avg_verified_examples || 0) + '%'}
              target="95%"
              status="good"
            />
          </div>

          <HealthStatus metrics={metrics} />
        </section>
      </div>
    </div>
  );
}
```

### Create Metric Card Component

```jsx
// components/MetricCard.jsx
import styles from '../styles/MetricCard.module.css';

export default function MetricCard({
  label,
  value,
  target,
  trend,
  status = 'neutral'
}) {
  return (
    <div className={`${styles.card} ${styles[status]}`}>
      <div className={styles.header}>
        <h3>{label}</h3>
        {target && <span className={styles.target}>Target: {target}</span>}
      </div>

      <div className={styles.value}>
        {value}
      </div>

      {trend !== undefined && (
        <div className={`${styles.trend} ${trend > 0 ? styles.up : styles.down}`}>
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend).toFixed(1)}%
        </div>
      )}
    </div>
  );
}
```

## Part 4: Create API Endpoints

### Dashboard API Backend

```python
# api/dashboard.py
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json

dashboard_bp = Blueprint('dashboard', __name__)

class DashboardAPI:
    def __init__(self, data_pipeline, kpi_framework):
        self.data_pipeline = data_pipeline
        self.kpi_framework = kpi_framework

    def register_routes(self, app):
        """Register dashboard API routes"""

        @app.route('/api/dashboard/metrics', methods=['GET'])
        def get_metrics():
            days = request.args.get('days', 30, type=int)
            metrics = self.data_pipeline.get_metrics_summary(days)
            alerts = self.generate_alerts(metrics)

            return jsonify({
                **metrics,
                'alerts': alerts
            })

        @app.route('/api/dashboard/kpis', methods=['GET'])
        def get_kpis():
            kpis = self.kpi_framework.get_all_kpis()
            kpi_list = [
                {
                    'name': kpi.name,
                    'category': kpi.category.value,
                    'target': kpi.target,
                    'current': self.get_current_kpi_value(kpi),
                    'status': self.get_kpi_status(kpi),
                    'description': kpi.description
                }
                for kpi in kpis
            ]

            return jsonify({'kpis': kpi_list})

        @app.route('/api/dashboard/trends', methods=['GET'])
        def get_trends():
            metric = request.args.get('metric')
            days = request.args.get('days', 90, type=int)

            trends = self.calculate_trends(metric, days)

            return jsonify({
                'metric': metric,
                'period_days': days,
                'data': trends
            })

        @app.route('/api/dashboard/export', methods=['GET'])
        def export_dashboard():
            format_type = request.args.get('format', 'json')
            days = request.args.get('days', 30, type=int)

            data = self.data_pipeline.get_metrics_summary(days)

            if format_type == 'json':
                return jsonify(data)
            elif format_type == 'csv':
                return self.convert_to_csv(data)

    def generate_alerts(self, metrics):
        """Generate alerts for critical metrics"""
        alerts = []

        # Check engagement
        if metrics['engagement']['avg_session_duration'] < 120:
            alerts.append({
                'level': 'warning',
                'message': 'Session duration below target. Users may be leaving quickly.',
                'action': 'Review documentation clarity and engagement'
            })

        # Check quality
        if metrics['quality']['avg_outdated'] > 10:
            alerts.append({
                'level': 'critical',
                'message': f"{int(metrics['quality']['avg_outdated'])} pages are outdated (>6 months)",
                'action': 'Schedule content audit and updates'
            })

        # Check satisfaction
        if metrics['satisfaction']['avg_rating'] < 4.0:
            alerts.append({
                'level': 'warning',
                'message': 'User satisfaction rating below 4.0',
                'action': 'Review feedback and address common issues'
            })

        return alerts

    def get_current_kpi_value(self, kpi):
        """Get current value for a KPI"""
        # Implementation would query actual data
        pass

    def get_kpi_status(self, kpi):
        """Determine KPI status"""
        current = self.get_current_kpi_value(kpi)

        if current >= kpi.target:
            return 'excellent'
        elif current >= kpi.threshold_warning:
            return 'good'
        elif current >= kpi.threshold_critical:
            return 'warning'
        else:
            return 'critical'

    def calculate_trends(self, metric, days):
        """Calculate trend data for metric"""
        # Implementation would query time-series data
        pass

    def convert_to_csv(self, data):
        """Convert metrics to CSV"""
        import csv
        from io import StringIO

        output = StringIO()
        # CSV conversion logic
        return output.getvalue()
```

## Part 5: Visualization Components

### Create Chart Components

```jsx
// components/TrendChart.jsx
import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function TrendChart({ title, dataKey, period }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetchTrendData();
  }, [period, dataKey]);

  const fetchTrendData = async () => {
    const response = await fetch(`/api/dashboard/trends?metric=${dataKey}&days=${period}`);
    const trendData = await response.json();
    setData(trendData.data);
  };

  return (
    <div className="chart-container">
      <h3>{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line
            type="monotone"
            dataKey={dataKey}
            stroke="#8884d8"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
```

### Create Health Status Component

```jsx
// components/HealthStatus.jsx
import styles from '../styles/HealthStatus.module.css';

export default function HealthStatus({ metrics }) {
  const calculateHealthScore = () => {
    let score = 100;

    // Deduct for quality issues
    if (metrics?.quality.avg_outdated > 10) score -= 20;
    if (metrics?.quality.avg_verified_examples < 85) score -= 15;

    // Deduct for satisfaction issues
    if (metrics?.satisfaction.avg_rating < 4.0) score -= 15;

    // Deduct for engagement issues
    if (metrics?.engagement.avg_session_duration < 180) score -= 10;

    return Math.max(0, score);
  };

  const score = calculateHealthScore();
  const status = score >= 80 ? 'excellent' : score >= 60 ? 'good' : score >= 40 ? 'fair' : 'poor';

  return (
    <div className={`${styles.healthStatus} ${styles[status]}`}>
      <div className={styles.scoreDisplay}>
        <div className={styles.scoreCircle}>
          <span className={styles.score}>{score}</span>
          <span className={styles.label}>Health</span>
        </div>
      </div>

      <div className={styles.details}>
        <h4>Documentation Health Status: {status.toUpperCase()}</h4>

        <ul>
          {score >= 80 && <li>✓ Content is current and well-maintained</li>}
          {score >= 60 && <li>⚠ Some outdated content needs attention</li>}
          {score < 60 && <li>✗ Significant quality issues require immediate action</li>}

          {metrics?.quality.avg_outdated > 10 && (
            <li>→ Update {Math.round(metrics.quality.avg_outdated)} outdated pages</li>
          )}
        </ul>
      </div>
    </div>
  );
}
```

## Part 6: Scheduled Reports

### Automated Report Generation

```python
# reports/scheduled_reports.py
from datetime import datetime
import json
from pathlib import Path

class ScheduledReportGenerator:
    """Generate automated reports"""

    def __init__(self, dashboard_api, email_service):
        self.dashboard_api = dashboard_api
        self.email_service = email_service

    def generate_daily_summary(self):
        """Generate daily summary report"""
        metrics = self.dashboard_api.get_metrics_summary(1)
        alerts = self.dashboard_api.generate_alerts(metrics)

        report = {
            'type': 'daily_summary',
            'date': datetime.now().isoformat(),
            'metrics': metrics,
            'alerts': alerts,
            'action_items': self.generate_action_items(alerts)
        }

        return report

    def generate_weekly_report(self):
        """Generate weekly report"""
        metrics = self.dashboard_api.get_metrics_summary(7)
        kpis = self.dashboard_api.kpi_framework.get_all_kpis()
        trends = self.calculate_week_trends()

        report = {
            'type': 'weekly_report',
            'period': f"{datetime.now().date()}",
            'metrics_summary': metrics,
            'kpi_performance': self.evaluate_kpis(kpis),
            'trends': trends,
            'recommendations': self.generate_recommendations(metrics)
        }

        return report

    def generate_monthly_report(self):
        """Generate comprehensive monthly report"""
        metrics = self.dashboard_api.get_metrics_summary(30)
        business_impact = self.calculate_business_impact()

        report = {
            'type': 'monthly_report',
            'month': datetime.now().strftime('%B %Y'),
            'executive_summary': {
                'key_metrics': self.get_key_metrics(metrics),
                'highlights': self.get_highlights(metrics),
                'concerns': self.get_concerns(metrics)
            },
            'detailed_metrics': metrics,
            'business_impact': business_impact,
            'recommendations': self.generate_strategic_recommendations(),
            'outlook': self.generate_outlook()
        }

        return report

    def send_report(self, report, recipients):
        """Email report to stakeholders"""
        report_html = self.render_report_html(report)

        for recipient in recipients:
            self.email_service.send(
                to=recipient,
                subject=f"Documentation {report['type']} - {report.get('month', report.get('date', datetime.now().date()))}",
                html=report_html
            )

    def generate_action_items(self, alerts):
        """Convert alerts to action items"""
        return [
            {
                'priority': alert['level'],
                'task': alert['action'],
                'description': alert['message']
            }
            for alert in alerts
        ]

    def render_report_html(self, report):
        """Convert report to HTML for email"""
        # HTML rendering logic
        pass

    def calculate_business_impact(self):
        """Calculate business impact metrics"""
        # Business impact calculation
        pass
```

### Schedule Reports

```python
# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from reports.scheduled_reports import ScheduledReportGenerator

def schedule_documentation_reports(app):
    """Schedule automated report generation"""
    scheduler = BackgroundScheduler()

    report_generator = ScheduledReportGenerator(
        dashboard_api=app.dashboard_api,
        email_service=app.email_service
    )

    # Daily summary at 8 AM
    scheduler.add_job(
        func=lambda: report_generator.send_report(
            report_generator.generate_daily_summary(),
            recipients=['docs-team@company.com']
        ),
        trigger='cron',
        hour=8,
        minute=0,
        id='daily_summary'
    )

    # Weekly report every Monday at 9 AM
    scheduler.add_job(
        func=lambda: report_generator.send_report(
            report_generator.generate_weekly_report(),
            recipients=['docs-team@company.com', 'product-team@company.com']
        ),
        trigger='cron',
        day_of_week='mon',
        hour=9,
        minute=0,
        id='weekly_report'
    )

    # Monthly report first day of month at 10 AM
    scheduler.add_job(
        func=lambda: report_generator.send_report(
            report_generator.generate_monthly_report(),
            recipients=['docs-team@company.com', 'leadership@company.com', 'product@company.com']
        ),
        trigger='cron',
        day=1,
        hour=10,
        minute=0,
        id='monthly_report'
    )

    scheduler.start()
    return scheduler
```

## Part 7: Mobile Dashboard

### Create Mobile-Friendly View

```jsx
// pages/dashboard/mobile.jsx
import React, { useEffect, useState } from 'react';
import styles from '../../styles/MobileDashboard.module.css';

export default function MobileDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [activeTab, setActiveTab] = useState('engagement');

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    const response = await fetch('/api/dashboard/metrics?days=7');
    const data = await response.json();
    setMetrics(data);
  };

  const tabs = ['engagement', 'satisfaction', 'quality'];

  return (
    <div className={styles.mobileDashboard}>
      <header className={styles.header}>
        <h1>Docs Dashboard</h1>
        <button onClick={fetchMetrics}>↻</button>
      </header>

      <div className={styles.tabBar}>
        {tabs.map((tab) => (
          <button
            key={tab}
            className={`${styles.tab} ${activeTab === tab ? styles.active : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      <div className={styles.content}>
        {/* Dynamic content based on active tab */}
      </div>
    </div>
  );
}
```

## Part 8: Data Retention and Archival

### Archive Old Data

```python
# data_management.py
from datetime import datetime, timedelta

class DataArchival:
    """Manage dashboard data lifecycle"""

    def archive_old_metrics(self, retention_days=730):
        """Archive metrics older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        # Archive to cold storage (S3, etc.)
        # Delete from hot database

    def export_annual_summary(self, year):
        """Export annual summary for archival"""
        # Generate annual report
        # Archive to long-term storage
        pass

    def cleanup_database(self):
        """Clean up old database records"""
        # Remove metrics older than 2 years
        # Optimize database
        pass
```

## Conclusion

A comprehensive documentation dashboard provides real-time insights into documentation performance and user satisfaction. By tracking key metrics, generating alerts, and creating automated reports, organizations can continuously improve documentation and demonstrate its value to stakeholders.

## Key Takeaways

1. Select metrics that align with business goals
2. Implement automated data collection and aggregation
3. Build intuitive visualizations for different audiences
4. Generate regular reports for stakeholder communication
5. Act on insights to continuously improve documentation
6. Monitor trends over time for strategic planning


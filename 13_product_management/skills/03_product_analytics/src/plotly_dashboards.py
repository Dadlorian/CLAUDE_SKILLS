"""
Interactive Data Visualization Dashboards using Plotly
======================================================

Comprehensive examples of interactive dashboards for product analytics,
including KPI tracking, funnel analysis, cohort analysis, and real-time monitoring.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# ============================================================================
# 1. EXECUTIVE DASHBOARD - KPI Overview
# ============================================================================

class ExecutiveDashboard:
    """
    Multi-panel executive dashboard showing key product metrics.

    Displays:
    - Monthly Revenue Trend
    - User Growth Rate
    - Key Metrics Cards
    - Conversion Funnel
    """

    def __init__(self):
        self.generate_sample_data()

    def generate_sample_data(self):
        """Generate realistic sample data for demonstration."""
        dates = pd.date_range(start='2024-01-01', end='2024-11-19', freq='D')

        self.daily_metrics = pd.DataFrame({
            'date': dates,
            'revenue': np.cumsum(np.random.normal(5000, 1000, len(dates))) + 50000,
            'users': np.cumsum(np.random.normal(50, 10, len(dates))) + 1000,
            'active_sessions': np.random.poisson(150, len(dates)),
            'conversion_rate': np.random.normal(0.032, 0.005, len(dates))
        })

        self.monthly_data = self.daily_metrics.resample('MS').agg({
            'revenue': 'sum',
            'users': 'max',
            'active_sessions': 'mean',
            'conversion_rate': 'mean'
        }).reset_index()
        self.monthly_data.columns = ['month', 'revenue', 'users', 'active_sessions', 'conversion_rate']

    def create_executive_dashboard(self):
        """
        Create comprehensive executive dashboard.

        Returns:
            plotly.graph_objects.Figure: Interactive dashboard figure
        """
        # Create subplots with different specs
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Monthly Revenue Trend', 'Cumulative Users',
                          'Daily Active Sessions', 'Conversion Rate Trend'),
            specs=[[{'secondary_y': False}, {'secondary_y': False}],
                   [{'secondary_y': False}, {'secondary_y': True}]]
        )

        # 1. Revenue trend with trend line
        fig.add_trace(
            go.Scatter(
                x=self.monthly_data['month'],
                y=self.monthly_data['revenue'],
                name='Monthly Revenue',
                mode='lines+markers',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x|%B %Y}</b><br>Revenue: $%{y:,.0f}<extra></extra>'
            ),
            row=1, col=1
        )

        # 2. User growth
        fig.add_trace(
            go.Scatter(
                x=self.monthly_data['month'],
                y=self.monthly_data['users'],
                name='Total Users',
                mode='lines+markers',
                line=dict(color='#2ca02c', width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x|%B %Y}</b><br>Users: %{y:,}<extra></extra>'
            ),
            row=1, col=2
        )

        # 3. Active sessions (bar chart)
        fig.add_trace(
            go.Bar(
                x=self.daily_metrics['date'].dt.to_period('W').astype(str),
                y=self.daily_metrics.groupby(self.daily_metrics['date'].dt.to_period('W'))['active_sessions'].mean(),
                name='Avg Weekly Sessions',
                marker=dict(color='#ff7f0e'),
                hovertemplate='<b>%{x}</b><br>Sessions: %{y:.0f}<extra></extra>'
            ),
            row=2, col=1
        )

        # 4. Conversion rate with moving average
        window = 7
        moving_avg = self.daily_metrics['conversion_rate'].rolling(window=window).mean()

        fig.add_trace(
            go.Scatter(
                x=self.daily_metrics['date'],
                y=self.daily_metrics['conversion_rate'],
                name='Daily Conversion Rate',
                mode='markers',
                marker=dict(color='rgba(214, 39, 40, 0.3)'),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>CR: %{y:.2%}<extra></extra>'
            ),
            row=2, col=2, secondary_y=False
        )

        fig.add_trace(
            go.Scatter(
                x=self.daily_metrics['date'],
                y=moving_avg,
                name=f'{window}-Day MA',
                mode='lines',
                line=dict(color='#d62728', width=2, dash='dash'),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>MA: %{y:.2%}<extra></extra>'
            ),
            row=2, col=2, secondary_y=False
        )

        # Update layout
        fig.update_layout(
            title={
                'text': '<b>Product Analytics Executive Dashboard</b><br><sub>Real-time KPI tracking and performance monitoring</sub>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            height=800,
            showlegend=True,
            hovermode='x unified',
            template='plotly_white',
            font=dict(family='Arial, sans-serif', size=12),
        )

        # Update axes
        fig.update_xaxes(title_text='Month', row=1, col=1)
        fig.update_xaxes(title_text='Month', row=1, col=2)
        fig.update_xaxes(title_text='Week', row=2, col=1)
        fig.update_xaxes(title_text='Date', row=2, col=2)

        fig.update_yaxes(title_text='Revenue ($)', row=1, col=1)
        fig.update_yaxes(title_text='Users', row=1, col=2)
        fig.update_yaxes(title_text='Sessions', row=2, col=1)
        fig.update_yaxes(title_text='Conversion Rate', row=2, col=2)

        return fig


# ============================================================================
# 2. CONVERSION FUNNEL ANALYSIS
# ============================================================================

class FunnelAnalysis:
    """
    Interactive conversion funnel visualization for user journey analysis.

    Stages:
    - Visitors
    - Signups
    - Activated
    - Premium Users
    - Retained Users (30-day)
    """

    @staticmethod
    def create_funnel_chart():
        """
        Create interactive funnel chart showing conversion drop-off.

        Returns:
            plotly.graph_objects.Figure: Funnel chart
        """
        stages = ['Website Visitors', 'Trial Signups', 'Activated Users',
                 'Paid Customers', '30-Day Retained']
        users = [10000, 4200, 2100, 840, 630]
        conversions = [42.0, 50.0, 40.0, 75.0]

        fig = go.Figure(go.Funnel(
            y=stages,
            x=users,
            textposition='inside',
            textinfo='value+percent initial',
            marker=dict(
                color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A'],
                line=dict(color='rgba(0,0,0,0.2)', width=2)
            ),
            connector=dict(
                line=dict(color='rgba(0,0,0,0.2)', width=1)
            ),
            hovertemplate='<b>%{y}</b><br>Users: %{x:,}<br>Conv Rate: %{customdata}%<extra></extra>',
            customdata=[100] + conversions
        ))

        fig.update_layout(
            title={
                'text': '<b>User Conversion Funnel Analysis</b><br><sub>Identifying drop-off points in user journey</sub>',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=600,
            template='plotly_white',
            font=dict(family='Arial, sans-serif', size=12),
            showlegend=False
        )

        return fig

    @staticmethod
    def create_segment_funnel_comparison():
        """
        Compare conversion funnels across different user segments.

        Returns:
            plotly.graph_objects.Figure: Comparative funnel analysis
        """
        segments = ['Free Users', 'Paid Users', 'Enterprise Users']
        stage_conversions = {
            'Signup': [100, 100, 100],
            'Email Verify': [92, 95, 98],
            'First Action': [78, 88, 96],
            'Active (7 days)': [45, 82, 95],
            'Retained (30 days)': [22, 70, 92]
        }

        fig = make_subplots(
            rows=1, cols=3,
            specs=[[{'type': 'funnel'}, {'type': 'funnel'}, {'type': 'funnel'}]],
            subplot_titles=segments
        )

        colors = ['#636EFA', '#EF553B', '#00CC96']
        stages = list(stage_conversions.keys())

        for i, segment in enumerate(segments):
            values = stage_conversions[segments[i]]
            fig.add_trace(
                go.Funnel(
                    y=stages,
                    x=values,
                    name=segment,
                    marker=dict(color=colors[i]),
                    textinfo='value',
                ),
                row=1, col=i+1
            )

        fig.update_layout(
            title={
                'text': '<b>Segment-Based Funnel Comparison</b><br><sub>Performance across user tiers</sub>',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=500,
            template='plotly_white',
            showlegend=False
        )

        return fig


# ============================================================================
# 3. COHORT ANALYSIS HEATMAP
# ============================================================================

class CohortAnalysis:
    """
    Cohort retention analysis showing user behavior patterns over time.
    """

    @staticmethod
    def create_cohort_heatmap():
        """
        Create cohort retention heatmap.

        Returns:
            plotly.graph_objects.Figure: Cohort heatmap
        """
        # Generate synthetic cohort data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
        cohort_data = np.array([
            [100, 92, 84, 78, 73, 69, 66, 63, 61, 59, 57],
            [100, 91, 82, 75, 69, 64, 60, 57, 54, 52],
            [100, 93, 86, 80, 75, 71, 67, 64, 61],
            [100, 89, 79, 71, 65, 60, 55, 51],
            [100, 94, 87, 81, 76, 71, 67],
            [100, 90, 80, 72, 65, 59],
            [100, 88, 76, 66, 58],
            [100, 92, 83, 75],
            [100, 87, 76],
            [100, 91],
            [100]
        ])

        fig = go.Figure(data=go.Heatmap(
            z=cohort_data,
            x=list(range(1, 12)),
            y=months,
            colorscale='RdYlGn',
            text=np.round(cohort_data, 1),
            texttemplate='%{text}%',
            textfont={"size": 10},
            colorbar=dict(title='Retention %'),
            hovertemplate='Cohort: %{y}<br>Week: %{x}<br>Retention: %{z}%<extra></extra>'
        ))

        fig.update_layout(
            title={
                'text': '<b>Monthly Cohort Retention Analysis</b><br><sub>User retention rates by acquisition month</sub>',
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title='Weeks After Signup',
            yaxis_title='Signup Cohort (Month)',
            height=500,
            template='plotly_white'
        )

        return fig


# ============================================================================
# 4. FEATURE ADOPTION DASHBOARD
# ============================================================================

class FeatureAdoptionDashboard:
    """
    Track feature adoption metrics and usage patterns.
    """

    @staticmethod
    def create_adoption_dashboard():
        """
        Create comprehensive feature adoption dashboard.

        Returns:
            plotly.graph_objects.Figure: Feature adoption metrics
        """
        # Sample data
        features = ['Profile Setup', 'API Integration', 'Custom Reports',
                   'SSO Authentication', 'Data Export', 'Advanced Analytics']
        adoption_rate = [92, 76, 54, 38, 67, 45]
        avg_daily_active = [8500, 4200, 2100, 1800, 3400, 1500]

        # Create subplots
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'bar'}, {'type': 'scatter'}]],
            subplot_titles=('Feature Adoption Rate', 'Daily Active Users by Feature')
        )

        # Adoption rates
        colors = ['#00CC96' if x > 60 else '#FFA15A' if x > 40 else '#EF553B'
                 for x in adoption_rate]

        fig.add_trace(
            go.Bar(
                x=features,
                y=adoption_rate,
                name='Adoption Rate',
                marker=dict(color=colors),
                text=[f'{x}%' for x in adoption_rate],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Adoption: %{y}%<extra></extra>'
            ),
            row=1, col=1
        )

        # Daily active users
        fig.add_trace(
            go.Scatter(
                x=features,
                y=avg_daily_active,
                mode='lines+markers+text',
                name='Daily Active Users',
                line=dict(color='#636EFA', width=3),
                marker=dict(size=10),
                text=[f'{x:,}' for x in avg_daily_active],
                textposition='top center',
                hovertemplate='<b>%{x}</b><br>DAU: %{y:,}<extra></extra>'
            ),
            row=1, col=2
        )

        fig.update_yaxes(title_text='Adoption %', row=1, col=1)
        fig.update_yaxes(title_text='Daily Active Users', row=1, col=2)

        fig.update_layout(
            title={
                'text': '<b>Feature Adoption Analysis</b><br><sub>Tracking feature usage and adoption trends</sub>',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=500,
            showlegend=True,
            template='plotly_white',
            hovermode='x unified'
        )

        return fig


# ============================================================================
# 5. REAL-TIME MONITORING DASHBOARD
# ============================================================================

class RealTimeMonitoring:
    """
    Real-time operational metrics monitoring.
    """

    @staticmethod
    def create_realtime_dashboard():
        """
        Create real-time monitoring dashboard.

        Returns:
            plotly.graph_objects.Figure: Real-time metrics
        """
        hours = [f'{i:02d}:00' for i in range(24)]
        requests = np.random.poisson(500, 24) + np.sin(np.arange(24) * 0.3) * 100 + 400
        errors = np.random.poisson(5, 24) + np.abs(np.sin(np.arange(24) * 0.5)) * 3
        latency = np.random.normal(150, 30, 24)

        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Request Volume (24-hour)', 'Error Rate (24-hour)', 'API Latency (24-hour)'),
            specs=[[{}], [{}], [{}]],
            vertical_spacing=0.12
        )

        # Request volume
        fig.add_trace(
            go.Scatter(
                x=hours, y=requests,
                name='Requests',
                mode='lines+markers',
                line=dict(color='#636EFA', width=2),
                fill='tozeroy',
                hovertemplate='<b>%{x}</b><br>Requests: %{y:.0f}<extra></extra>'
            ),
            row=1, col=1
        )

        # Error rate
        fig.add_trace(
            go.Bar(
                x=hours, y=errors,
                name='Errors',
                marker=dict(color='#EF553B'),
                hovertemplate='<b>%{x}</b><br>Errors: %{y:.0f}<extra></extra>'
            ),
            row=2, col=1
        )

        # Latency
        fig.add_trace(
            go.Scatter(
                x=hours, y=latency,
                name='Latency (ms)',
                mode='lines+markers',
                line=dict(color='#00CC96', width=2),
                marker=dict(size=6),
                hovertemplate='<b>%{x}</b><br>Latency: %{y:.0f}ms<extra></extra>'
            ),
            row=3, col=1
        )

        fig.update_yaxes(title_text='Count', row=1, col=1)
        fig.update_yaxes(title_text='Errors', row=2, col=1)
        fig.update_yaxes(title_text='Milliseconds', row=3, col=1)
        fig.update_xaxes(title_text='Time (UTC)', row=3, col=1)

        fig.update_layout(
            title={
                'text': '<b>Real-Time System Monitoring</b><br><sub>24-hour operational metrics</sub>',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=800,
            showlegend=True,
            template='plotly_white',
            hovermode='x unified'
        )

        return fig


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def export_dashboard(fig, filename):
    """
    Export dashboard to HTML and PNG formats.

    Args:
        fig: Plotly Figure object
        filename: Output filename (without extension)
    """
    fig.write_html(f'{filename}.html')
    fig.write_image(f'{filename}.png', width=1400, height=800)
    print(f'Dashboard exported to {filename}.html and {filename}.png')


def create_all_dashboards():
    """
    Generate all example dashboards.
    """
    dashboards = {
        'executive_dashboard': ExecutiveDashboard().create_executive_dashboard(),
        'funnel_analysis': FunnelAnalysis.create_funnel_chart(),
        'funnel_comparison': FunnelAnalysis.create_segment_funnel_comparison(),
        'cohort_analysis': CohortAnalysis.create_cohort_heatmap(),
        'feature_adoption': FeatureAdoptionDashboard.create_adoption_dashboard(),
        'realtime_monitoring': RealTimeMonitoring.create_realtime_dashboard(),
    }

    return dashboards


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    """
    Run this script to generate all dashboard examples.

    Requirements:
        pip install plotly pandas numpy kaleido

    Output:
        - Interactive HTML files for each dashboard
        - Static PNG files for documentation
    """

    print('Generating data visualization dashboards...\n')

    # 1. Executive Dashboard
    print('1. Creating Executive Dashboard...')
    exec_dashboard = ExecutiveDashboard()
    fig1 = exec_dashboard.create_executive_dashboard()
    fig1.show()

    # 2. Funnel Analysis
    print('2. Creating Funnel Analysis...')
    fig2 = FunnelAnalysis.create_funnel_chart()
    fig2.show()

    # 3. Funnel Comparison
    print('3. Creating Segment Funnel Comparison...')
    fig3 = FunnelAnalysis.create_segment_funnel_comparison()
    fig3.show()

    # 4. Cohort Analysis
    print('4. Creating Cohort Retention Heatmap...')
    fig4 = CohortAnalysis.create_cohort_heatmap()
    fig4.show()

    # 5. Feature Adoption
    print('5. Creating Feature Adoption Dashboard...')
    fig5 = FeatureAdoptionDashboard.create_adoption_dashboard()
    fig5.show()

    # 6. Real-time Monitoring
    print('6. Creating Real-Time Monitoring Dashboard...')
    fig6 = RealTimeMonitoring.create_realtime_dashboard()
    fig6.show()

    print('\nAll dashboards generated successfully!')
    print('\nDashboard Features:')
    print('✓ Interactive hover information')
    print('✓ Zoom and pan capabilities')
    print('✓ Download as PNG')
    print('✓ Legend toggling')
    print('✓ Responsive design')

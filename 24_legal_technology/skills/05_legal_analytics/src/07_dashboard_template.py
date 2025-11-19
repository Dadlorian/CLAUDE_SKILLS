#!/usr/bin/env python3
"""
Legal Analytics Dashboard Template
HTML/CSS template for creating interactive legal analytics dashboards
"""

import json
from datetime import datetime

def generate_dashboard_html(metrics):
    """
    Generate HTML dashboard for legal metrics

    Args:
        metrics: Dictionary with key performance indicators

    Returns:
        HTML string for dashboard
    """

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Legal Analytics Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background-color: #f5f5f5;
                color: #333;
            }

            .header {
                background-color: #1e3a5f;
                color: white;
                padding: 20px 30px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .header h1 {
                font-size: 24px;
            }

            .header .refresh-time {
                font-size: 12px;
                opacity: 0.8;
            }

            .container {
                padding: 20px;
                max-width: 1400px;
                margin: 0 auto;
            }

            .filters {
                background: white;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 4px;
                display: flex;
                gap: 20px;
                align-items: center;
            }

            .filter-group {
                display: flex;
                flex-direction: column;
                gap: 5px;
            }

            .filter-group label {
                font-size: 12px;
                font-weight: 600;
                color: #666;
                text-transform: uppercase;
            }

            .filter-group select {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                cursor: pointer;
            }

            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }

            .metric-card {
                background: white;
                padding: 20px;
                border-radius: 4px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                border-left: 4px solid #1e3a5f;
            }

            .metric-card.success {
                border-left-color: #28a745;
            }

            .metric-card.warning {
                border-left-color: #ffc107;
            }

            .metric-card.danger {
                border-left-color: #dc3545;
            }

            .metric-label {
                font-size: 12px;
                text-transform: uppercase;
                color: #999;
                margin-bottom: 8px;
                font-weight: 600;
            }

            .metric-value {
                font-size: 28px;
                font-weight: bold;
                color: #1e3a5f;
                margin-bottom: 8px;
            }

            .metric-change {
                font-size: 12px;
                color: #666;
            }

            .metric-change.positive {
                color: #28a745;
            }

            .metric-change.negative {
                color: #dc3545;
            }

            .chart-section {
                background: white;
                padding: 20px;
                border-radius: 4px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }

            .chart-title {
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 15px;
                color: #1e3a5f;
            }

            .chart-container {
                height: 300px;
                background: #f9f9f9;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #999;
            }

            .table-section {
                background: white;
                border-radius: 4px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                overflow: hidden;
            }

            .table-header {
                padding: 15px 20px;
                border-bottom: 1px solid #eee;
                background: #f9f9f9;
            }

            .table-header h3 {
                font-size: 14px;
                font-weight: 600;
                color: #1e3a5f;
            }

            table {
                width: 100%;
                border-collapse: collapse;
            }

            th {
                text-align: left;
                padding: 12px 20px;
                font-size: 12px;
                font-weight: 600;
                color: #666;
                text-transform: uppercase;
                border-bottom: 2px solid #eee;
                background: #f9f9f9;
            }

            td {
                padding: 12px 20px;
                border-bottom: 1px solid #eee;
                font-size: 14px;
            }

            tr:hover {
                background: #f9f9f9;
            }

            .status-badge {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 11px;
                font-weight: 600;
            }

            .status-good {
                background: #d4edda;
                color: #155724;
            }

            .status-warning {
                background: #fff3cd;
                color: #856404;
            }

            .status-critical {
                background: #f8d7da;
                color: #721c24;
            }

            .footer {
                text-align: center;
                padding: 20px;
                color: #999;
                font-size: 12px;
            }

            @media (max-width: 768px) {
                .filters {
                    flex-direction: column;
                    align-items: stretch;
                }

                .grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Legal Analytics Dashboard</h1>
            <div class="refresh-time">Last updated: {timestamp}</div>
        </div>

        <div class="container">
            <!-- Filters -->
            <div class="filters">
                <div class="filter-group">
                    <label>Time Period</label>
                    <select id="period">
                        <option>Last 30 Days</option>
                        <option>Last Quarter</option>
                        <option>Last Year</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Practice Area</label>
                    <select id="practice">
                        <option>All Areas</option>
                        <option>Litigation</option>
                        <option>Corporate</option>
                        <option>IP</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Department</label>
                    <select id="department">
                        <option>All Departments</option>
                        <option>Boston</option>
                        <option>New York</option>
                        <option>San Francisco</option>
                    </select>
                </div>
            </div>

            <!-- Key Metrics Row 1 -->
            <div class="grid">
                <div class="metric-card success">
                    <div class="metric-label">Total Legal Spend</div>
                    <div class="metric-value">${metrics.get('total_spend', '$2.4M')}</div>
                    <div class="metric-change positive">↑ 8% vs last period</div>
                </div>

                <div class="metric-card success">
                    <div class="metric-label">Budget Utilization</div>
                    <div class="metric-value">{metrics.get('budget_utilization', '92%')}</div>
                    <div class="metric-change positive">On track for year</div>
                </div>

                <div class="metric-card warning">
                    <div class="metric-label">Average Matter Cost</div>
                    <div class="metric-value">${metrics.get('avg_matter_cost', '$145K')}</div>
                    <div class="metric-change negative">↑ 5% vs plan</div>
                </div>

                <div class="metric-card success">
                    <div class="metric-label">Utilization Rate</div>
                    <div class="metric-value">{metrics.get('utilization_rate', '82%')}</div>
                    <div class="metric-change positive">↑ 2% vs target</div>
                </div>
            </div>

            <!-- Key Metrics Row 2 -->
            <div class="grid">
                <div class="metric-card success">
                    <div class="metric-label">On-Time Delivery</div>
                    <div class="metric-value">{metrics.get('on_time_delivery', '94%')}</div>
                    <div class="metric-change negative">↓ 1% from last month</div>
                </div>

                <div class="metric-card success">
                    <div class="metric-label">Client Satisfaction</div>
                    <div class="metric-value">4.6/5.0</div>
                    <div class="metric-change positive">↑ 0.2 points</div>
                </div>

                <div class="metric-card success">
                    <div class="metric-label">Billing Accuracy</div>
                    <div class="metric-value">{metrics.get('billing_accuracy', '97%')}</div>
                    <div class="metric-change positive">No change</div>
                </div>

                <div class="metric-card warning">
                    <div class="metric-label">Open Matters</div>
                    <div class="metric-value">{metrics.get('open_matters', '127')}</div>
                    <div class="metric-change negative">↑ 12 from last month</div>
                </div>
            </div>

            <!-- Charts Section -->
            <div class="chart-section">
                <div class="chart-title">Monthly Spend Trend</div>
                <div class="chart-container">
                    <p>[Chart: Monthly spending trend - integrate with Tableau/Power BI]</p>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div class="chart-section">
                    <div class="chart-title">Spend by Practice Area</div>
                    <div class="chart-container">
                        <p>[Pie Chart: Practice area breakdown]</p>
                    </div>
                </div>

                <div class="chart-section">
                    <div class="chart-title">Top Vendors</div>
                    <div class="chart-container">
                        <p>[Bar Chart: Top 5 vendors by spend]</p>
                    </div>
                </div>
            </div>

            <!-- Table Section -->
            <div class="table-section" style="margin-top: 20px;">
                <div class="table-header">
                    <h3>Top Matters by Cost</h3>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Matter ID</th>
                            <th>Matter Name</th>
                            <th>Practice Area</th>
                            <th>Total Cost</th>
                            <th>Status</th>
                            <th>Budget Variance</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>LIT-001</td>
                            <td>ABC Corp v. XYZ Inc</td>
                            <td>Litigation</td>
                            <td>$450,000</td>
                            <td><span class="status-badge status-good">On Track</span></td>
                            <td style="color: #28a745;">-5%</td>
                        </tr>
                        <tr>
                            <td>CORP-002</td>
                            <td>Smith Corp Acquisition</td>
                            <td>Corporate</td>
                            <td>$380,000</td>
                            <td><span class="status-badge status-warning">At Risk</span></td>
                            <td style="color: #ffc107;">+8%</td>
                        </tr>
                        <tr>
                            <td>LIT-003</td>
                            <td>Employee Dispute</td>
                            <td>Litigation</td>
                            <td>$280,000</td>
                            <td><span class="status-badge status-good">On Track</span></td>
                            <td style="color: #28a745;">-2%</td>
                        </tr>
                        <tr>
                            <td>REG-004</td>
                            <td>Regulatory Compliance</td>
                            <td>Regulatory</td>
                            <td>$200,000</td>
                            <td><span class="status-badge status-good">On Track</span></td>
                            <td style="color: #28a745;">+0%</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Alerts Section -->
            <div class="chart-section" style="margin-top: 20px;">
                <div class="chart-title">Alerts & Actions</div>
                <div style="padding: 15px;">
                    <p style="margin-bottom: 10px;">
                        <span class="status-badge status-critical">Critical</span>
                        Matter CORP-002 budget variance exceeds threshold - review with team
                    </p>
                    <p style="margin-bottom: 10px;">
                        <span class="status-badge status-warning">Warning</span>
                        On-time delivery trending down - 3 months consecutive decrease
                    </p>
                    <p>
                        <span class="status-badge status-good">Info</span>
                        Rate negotiation with top vendor scheduled for next week
                    </p>
                </div>
            </div>
        </div>

        <div class="footer">
            Legal Analytics Dashboard | Data refreshed hourly | Last sync: {timestamp}
        </div>

        <script>
            // Add interactivity with JavaScript
            document.getElementById('period')?.addEventListener('change', function() {
                console.log('Period changed to:', this.value);
                // Trigger dashboard refresh
            });

            document.getElementById('practice')?.addEventListener('change', function() {
                console.log('Practice area changed to:', this.value);
                // Filter dashboard data
            });

            document.getElementById('department')?.addEventListener('change', function() {
                console.log('Department changed to:', this.value);
                // Filter dashboard data
            });
        </script>
    </body>
    </html>
    """.format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    return html


if __name__ == "__main__":
    # Example metrics
    metrics = {
        'total_spend': '$2.4M',
        'budget_utilization': '92%',
        'avg_matter_cost': '$145K',
        'utilization_rate': '82%',
        'on_time_delivery': '94%',
        'billing_accuracy': '97%',
        'open_matters': '127'
    }

    # Generate and save dashboard
    dashboard_html = generate_dashboard_html(metrics)

    with open('/tmp/legal_analytics_dashboard.html', 'w') as f:
        f.write(dashboard_html)

    print("Dashboard generated and saved to /tmp/legal_analytics_dashboard.html")
    print("Open this file in a web browser to view the dashboard")

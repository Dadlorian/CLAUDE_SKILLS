"""
Python Automation Scripts for BI Tasks
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ================================================
# DATA QUALITY CHECKS
# ================================================

def check_data_quality(df, checks):
    """
    Run data quality checks on DataFrame
    
    Args:
        df: pandas DataFrame
        checks: dict of check configurations
    
    Returns:
        dict of check results
    """
    results = {}
    
    # Completeness check
    if 'completeness' in checks:
        for column in checks['completeness']:
            null_pct = df[column].isnull().mean() * 100
            results[f'{column}_null_pct'] = {
                'value': null_pct,
                'passed': null_pct < checks['completeness'][column]
            }
    
    # Uniqueness check
    if 'uniqueness' in checks:
        for column in checks['uniqueness']:
            duplicate_pct = (1 - df[column].nunique() / len(df)) * 100
            results[f'{column}_duplicate_pct'] = {
                'value': duplicate_pct,
                'passed': duplicate_pct < checks['uniqueness'][column]
            }
    
    # Range check
    if 'range' in checks:
        for column, (min_val, max_val) in checks['range'].items():
            out_of_range = ((df[column] < min_val) | (df[column] > max_val)).sum()
            results[f'{column}_out_of_range'] = {
                'value': out_of_range,
                'passed': out_of_range == 0
            }
    
    return results

# Example usage
checks = {
    'completeness': {'customer_id': 5, 'order_date': 0},  # Max null %
    'uniqueness': {'order_id': 0},  # Max duplicate %
    'range': {'amount': (0, 1000000)}  # Min, Max
}

# ================================================
# DASHBOARD REFRESH AUTOMATION
# ================================================

def refresh_tableau_extract(server_url, site_id, datasource_id, token):
    """
    Trigger Tableau extract refresh via REST API
    """
    headers = {
        'X-Tableau-Auth': token,
        'Content-Type': 'application/json'
    }
    
    url = f"{server_url}/api/3.19/sites/{site_id}/datasources/{datasource_id}/refresh"
    
    response = requests.post(url, headers=headers)
    
    if response.status_code == 202:
        job_id = response.json()['job']['id']
        print(f"Refresh started. Job ID: {job_id}")
        return job_id
    else:
        print(f"Refresh failed: {response.text}")
        return None

def refresh_powerbi_dataset(workspace_id, dataset_id, access_token):
    """
    Trigger Power BI dataset refresh
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
    
    response = requests.post(url, headers=headers)
    
    if response.status_code == 202:
        print("Refresh started successfully")
        return True
    else:
        print(f"Refresh failed: {response.text}")
        return False

# ================================================
# REPORT DISTRIBUTION
# ================================================

def send_email_report(to_emails, subject, html_content, smtp_config):
    """
    Send HTML email report
    """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = smtp_config['from_email']
    msg['To'] = ', '.join(to_emails)
    
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
        server.starttls()
        server.login(smtp_config['username'], smtp_config['password'])
        server.send_message(msg)
    
    print(f"Email sent to {len(to_emails)} recipients")

def generate_kpi_report(metrics_df):
    """
    Generate HTML KPI report from metrics DataFrame
    """
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            .good {{ color: green; }}
            .bad {{ color: red; }}
        </style>
    </head>
    <body>
        <h2>Daily KPI Report - {datetime.now().strftime('%Y-%m-%d')}</h2>
        {metrics_df.to_html(classes='table', index=False)}
    </body>
    </html>
    """
    return html

# ================================================
# MONITORING & ALERTING
# ================================================

def check_dashboard_performance(dashboard_url, threshold_seconds=5):
    """
    Monitor dashboard load time and alert if slow
    """
    import time
    
    start = time.time()
    response = requests.get(dashboard_url)
    load_time = time.time() - start
    
    alert_needed = load_time > threshold_seconds
    
    return {
        'url': dashboard_url,
        'load_time': load_time,
        'status_code': response.status_code,
        'alert_needed': alert_needed
    }

def send_slack_alert(webhook_url, message, severity='warning'):
    """
    Send alert to Slack channel
    """
    colors = {
        'info': '#36a64f',
        'warning': '#ff9900',
        'critical': '#ff0000'
    }
    
    payload = {
        'attachments': [{
            'color': colors.get(severity, '#808080'),
            'text': message,
            'footer': 'BI Monitoring System',
            'ts': int(datetime.now().timestamp())
        }]
    }
    
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200

# ================================================
# USAGE ANALYTICS
# ================================================

def analyze_dashboard_usage(usage_log_df):
    """
    Analyze dashboard usage patterns
    """
    analytics = {
        'total_views': len(usage_log_df),
        'unique_users': usage_log_df['user_id'].nunique(),
        'top_dashboards': usage_log_df.groupby('dashboard_name')['view_count'].sum().nlargest(10),
        'peak_hours': usage_log_df.groupby(usage_log_df['timestamp'].dt.hour)['view_count'].sum(),
        'active_users_by_day': usage_log_df.groupby(usage_log_df['timestamp'].dt.date)['user_id'].nunique()
    }
    
    return analytics

#!/usr/bin/env python3
"""
Pipeline Monitoring Script
Checks pipeline health and sends alerts
"""

import json
import requests
from datetime import datetime, timedelta

def check_pipeline_health():
    """Monitor dbt run results and alert on issues"""

    # Load dbt run results
    with open('/dbt/target/run_results.json') as f:
        results = json.load(f)

    # Analyze results
    total_models = len(results['results'])
    failed_models = [r for r in results['results'] if r['status'] == 'error']
    execution_time = sum(r['execution_time'] for r in results['results'])

    print(f"Total Models: {total_models}")
    print(f"Failed Models: {len(failed_models)}")
    print(f"Total Execution Time: {execution_time:.2f}s")

    # Alert on failures
    if failed_models:
        alert_message = f"""
        ⚠️ DBT Pipeline Failures

        Failed Models: {len(failed_models)}
        Total Models: {total_models}

        Failed:
        {chr(10).join(f"- {m['unique_id']}" for m in failed_models)}
        """

        # Send to Slack (example)
        webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
        requests.post(webhook_url, json={"text": alert_message})

        return 1

    # Alert on slow execution
    if execution_time > 3600:  # > 1 hour
        print(f"⚠️  Pipeline taking too long: {execution_time/60:.1f} minutes")

    return 0

if __name__ == "__main__":
    exit(check_pipeline_health())

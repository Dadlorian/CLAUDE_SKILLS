#!/usr/bin/env python3
"""
Source-to-Target Reconciliation Script
Validates data accuracy between source and warehouse
"""

import psycopg2
import snowflake.connector
from datetime import datetime, timedelta

def reconcile_orders(date):
    """Reconcile order counts and amounts"""

    # Connect to source (PostgreSQL)
    pg_conn = psycopg2.connect(
        host="database.example.com",
        database="production",
        user="etl_user",
        password="password"
    )

    # Connect to destination (Snowflake)
    sf_conn = snowflake.connector.connect(
        user="etl_user",
        password="password",
        account="xy12345",
        warehouse="TRANSFORM_WH",
        database="PROD_DB",
        schema="ANALYTICS"
    )

    # Query source
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute(f"""
        SELECT
            COUNT(*) as record_count,
            SUM(total_amount) as total_amount
        FROM orders
        WHERE DATE(order_date) = '{date}'
    """)
    source_count, source_amount = pg_cursor.fetchone()

    # Query destination
    sf_cursor = sf_conn.cursor()
    sf_cursor.execute(f"""
        SELECT
            COUNT(*) as record_count,
            SUM(total_amount) as total_amount
        FROM fct_orders
        WHERE order_date_key = '{date}'
    """)
    target_count, target_amount = sf_cursor.fetchone()

    # Compare
    count_match = source_count == target_count
    amount_match = abs(source_amount - target_amount) < 0.01

    print(f"Date: {date}")
    print(f"Source Records: {source_count}")
    print(f"Target Records: {target_count}")
    print(f"Count Match: {'✓' if count_match else '✗'}")
    print(f"Amount Match: {'✓' if amount_match else '✗'}")

    if not (count_match and amount_match):
        print("⚠️  RECONCILIATION FAILED")
        return 1

    return 0

if __name__ == "__main__":
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    exit(reconcile_orders(yesterday))

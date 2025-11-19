#!/usr/bin/env python3
"""
Extract data from PostgreSQL and upload to S3
"""

import psycopg2
import boto3
import csv
import io
from datetime import datetime

def extract_and_upload(table_name, s3_bucket, s3_prefix):
    """Extract table and upload to S3 as CSV"""

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host="database.example.com",
        database="production",
        user="etl_user",
        password="password"
    )

    # Extract data
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")

    # Write to CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([desc[0] for desc in cursor.description])

    # Write rows
    for row in cursor:
        writer.writerow(row)

    # Upload to S3
    s3_client = boto3.client('s3')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    s3_key = f"{s3_prefix}/{table_name}_{timestamp}.csv"

    s3_client.put_object(
        Bucket=s3_bucket,
        Key=s3_key,
        Body=output.getvalue().encode('utf-8')
    )

    print(f"Uploaded {table_name} to s3://{s3_bucket}/{s3_key}")

if __name__ == "__main__":
    extract_and_upload("orders", "data-lake-bucket", "extracts")

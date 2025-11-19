"""
Email Metadata Extraction for E-Discovery

Extracts metadata from email files (MSG, EML, MBOX) for e-discovery processing.
Outputs metadata in CSV format suitable for load file generation.

Usage:
    python 02_email_metadata_extraction.py /path/to/emails --output email_metadata.csv
"""

import email
import os
import csv
import argparse
from email import policy
from email.parser import BytesParser
from datetime import datetime
from pathlib import Path
import hashlib


def parse_eml_file(file_path: str) -> dict:
    """Parse EML email file and extract metadata."""
    with open(file_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    metadata = {
        'file_path': file_path,
        'file_name': os.path.basename(file_path),
        'file_size': os.path.getsize(file_path),
        'file_type': 'EML',
        'subject': msg.get('subject', ''),
        'from': msg.get('from', ''),
        'to': msg.get('to', ''),
        'cc': msg.get('cc', ''),
        'bcc': msg.get('bcc', ''),
        'date_sent': msg.get('date', ''),
        'message_id': msg.get('message-id', ''),
        'in_reply_to': msg.get('in-reply-to', ''),
        'references': msg.get('references', ''),
        'has_attachments': 'Yes' if len([p for p in msg.walk() if p.get_content_disposition() == 'attachment']) > 0 else 'No',
        'attachment_count': len([p for p in msg.walk() if p.get_content_disposition() == 'attachment']),
    }

    # Extract attachment names
    attachments = [p.get_filename() for p in msg.walk() if p.get_content_disposition() == 'attachment']
    metadata['attachment_names'] = '; '.join(attachments) if attachments else ''

    # Calculate MD5 hash
    with open(file_path, 'rb') as f:
        metadata['md5_hash'] = hashlib.md5(f.read()).hexdigest()

    return metadata


def process_email_directory(root_path: str) -> list:
    """Process all email files in directory."""
    email_data = []
    supported_extensions = ['.eml', '.msg']

    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if any(filename.lower().endswith(ext) for ext in supported_extensions):
                file_path = os.path.join(dirpath, filename)
                try:
                    if filename.lower().endswith('.eml'):
                        metadata = parse_eml_file(file_path)
                        email_data.append(metadata)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    return email_data


def export_to_csv(email_data: list, output_file: str):
    """Export email metadata to CSV."""
    if not email_data:
        print("No email data to export")
        return

    fieldnames = list(email_data[0].keys())

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(email_data)


def main():
    parser = argparse.ArgumentParser(description='Extract email metadata for e-discovery')
    parser.add_argument('path', help='Directory containing email files')
    parser.add_argument('--output', default='email_metadata.csv', help='Output CSV file')

    args = parser.parse_args()

    print(f"Processing emails in: {args.path}")
    email_data = process_email_directory(args.path)
    print(f"Processed {len(email_data)} emails")

    export_to_csv(email_data, args.output)
    print(f"Metadata exported to: {args.output}")


if __name__ == '__main__':
    main()

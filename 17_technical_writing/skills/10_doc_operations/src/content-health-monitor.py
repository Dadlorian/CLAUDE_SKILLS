#!/usr/bin/env python3
"""
Technical Documentation Content Health Monitor
Monitors and reports on the health of technical documentation
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import re


@dataclass
class DocumentMetric:
    """Represents metrics for a single document"""
    filename: str
    word_count: int
    code_blocks: int
    links: int
    images: int
    last_modified: str
    health_score: float
    issues: List[str]
    warnings: List[str]


class ContentHealthMonitor:
    """Monitors technical documentation health"""

    def __init__(self, docs_path: str = "."):
        self.docs_path = Path(docs_path)
        self.metrics: List[DocumentMetric] = []
        self.thresholds = {
            'min_word_count': 100,
            'max_word_count': 10000,
            'min_code_blocks': 0,
            'max_days_since_update': 365,
            'min_links': 1,
        }

    def scan_documents(self) -> None:
        """Scan all documentation files in the directory"""
        print(f"Scanning documentation in {self.docs_path}...")

        # Create sample documentation files for analysis if needed
        self._ensure_sample_docs()

        md_files = list(self.docs_path.glob('**/*.md')) + list(self.docs_path.glob('**/*.txt'))

        for file_path in md_files:
            if self._should_skip_file(file_path):
                continue

            print(f"  Analyzing: {file_path.name}")
            metric = self._analyze_document(file_path)
            self.metrics.append(metric)

    def _ensure_sample_docs(self) -> None:
        """Create sample documentation for analysis"""
        sample_docs = {
            'api-reference.md': '''# API Reference

## Authentication

Authentication uses OAuth 2.0. [Learn more](https://example.com/auth)

```python
import requests

response = requests.get(
    'https://api.example.com/users',
    headers={'Authorization': 'Bearer token'}
)
```

## Endpoints

### GET /users

Returns a list of users.

```json
{
  "users": [
    {"id": 1, "name": "John"}
  ]
}
```
''',
            'getting-started.md': '''# Getting Started

Welcome to our documentation!

## Installation

Follow these [installation steps](https://example.com/install).

```bash
pip install our-package
```

## Quick Example

Here's a quick example to get you started:

```python
from our_package import Client

client = Client()
result = client.do_something()
print(result)
```

## Next Steps

- Read the [API Reference](./api-reference.md)
- Check [Configuration Guide](https://example.com/config)
- See [Best Practices](https://example.com/practices)
''',
            'deployment-guide.md': '''# Deployment Guide

This guide covers deployment procedures.

## Prerequisites

- Docker installed
- AWS credentials configured
- Read [Security Best Practices](https://example.com/security)

## Docker Deployment

```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

## Cloud Deployment

### Step 1: Prepare

```bash
docker build -t myapp:latest .
```

### Step 2: Push

```bash
docker push myregistry.azurecr.io/myapp:latest
```

## Troubleshooting

See the [Troubleshooting Guide](https://example.com/troubleshoot).
''',
        }

        for filename, content in sample_docs.items():
            filepath = self.docs_path / filename
            if not filepath.exists():
                filepath.write_text(content)

    def _should_skip_file(self, path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = ['.git', '__pycache__', '.venv', 'node_modules']
        return any(pattern in str(path) for pattern in skip_patterns)

    def _analyze_document(self, file_path: Path) -> DocumentMetric:
        """Analyze a single document"""
        content = file_path.read_text(encoding='utf-8', errors='ignore')

        # Extract metrics
        word_count = len(content.split())
        code_blocks = len(re.findall(r'```[\s\S]*?```', content))
        links = len(re.findall(r'\[.*?\]\(.*?\)', content))
        images = len(re.findall(r'!\[.*?\]\(.*?\)', content))

        # Get last modified time
        stat = file_path.stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime)
        days_since_update = (datetime.now() - last_modified).days

        # Identify issues and warnings
        issues, warnings = self._check_content_issues(
            content, word_count, code_blocks, links, days_since_update
        )

        # Calculate health score
        health_score = self._calculate_health_score(
            word_count, code_blocks, links, days_since_update, len(issues)
        )

        return DocumentMetric(
            filename=file_path.name,
            word_count=word_count,
            code_blocks=code_blocks,
            links=links,
            images=images,
            last_modified=last_modified.strftime('%Y-%m-%d'),
            health_score=health_score,
            issues=issues,
            warnings=warnings
        )

    def _check_content_issues(self, content: str, word_count: int,
                             code_blocks: int, links: int, days_since_update: int) -> Tuple[List[str], List[str]]:
        """Check for content issues and warnings"""
        issues = []
        warnings = []

        # Content size issues
        if word_count < self.thresholds['min_word_count']:
            issues.append(f"Document too short ({word_count} words, minimum: {self.thresholds['min_word_count']})")

        if word_count > self.thresholds['max_word_count']:
            warnings.append(f"Document very long ({word_count} words, consider splitting)")

        # Link issues
        if links < self.thresholds['min_links']:
            warnings.append("No internal or external links found")

        # Update recency
        if days_since_update > self.thresholds['max_days_since_update']:
            issues.append(f"Not updated in {days_since_update} days")
        elif days_since_update > 90:
            warnings.append(f"Last updated {days_since_update} days ago")

        # Code example issues
        if word_count > 500 and code_blocks == 0:
            warnings.append("Long document with no code examples")

        # Broken links
        broken_links = re.findall(r'\[.*?\]\(\)', content)
        if broken_links:
            issues.extend([f"Broken link found" for _ in broken_links])

        # TODO or FIXME markers
        if 'TODO' in content or 'FIXME' in content:
            issues.append("Document contains TODO/FIXME markers")

        return issues, warnings

    def _calculate_health_score(self, word_count: int, code_blocks: int,
                               links: int, days_since_update: int, issue_count: int) -> float:
        """Calculate overall health score (0-100)"""
        score = 100.0

        # Word count factor
        if word_count < self.thresholds['min_word_count']:
            score -= 20
        elif word_count > self.thresholds['max_word_count']:
            score -= 10
        else:
            score += 5

        # Code examples factor
        score += min(code_blocks * 5, 15)

        # Links factor
        score += min(links * 2, 10)

        # Recency factor
        if days_since_update <= 30:
            score += 10
        elif days_since_update <= 90:
            score += 5
        elif days_since_update > 365:
            score -= 25

        # Issues factor
        score -= issue_count * 5

        return max(0, min(100, score))

    def generate_report(self) -> Dict:
        """Generate a comprehensive health report"""
        self.scan_documents()

        if not self.metrics:
            return {
                'summary': 'No documents found',
                'total_documents': 0,
                'average_health_score': 0,
                'documents': []
            }

        # Calculate statistics
        average_score = sum(m.health_score for m in self.metrics) / len(self.metrics)
        total_words = sum(m.word_count for m in self.metrics)
        total_code_blocks = sum(m.code_blocks for m in self.metrics)
        total_links = sum(m.links for m in self.metrics)

        # Categorize documents
        excellent = [m for m in self.metrics if m.health_score >= 85]
        good = [m for m in self.metrics if 70 <= m.health_score < 85]
        fair = [m for m in self.metrics if 50 <= m.health_score < 70]
        poor = [m for m in self.metrics if m.health_score < 50]

        # Document issues summary
        all_issues = {}
        for metric in self.metrics:
            for issue in metric.issues:
                all_issues[issue] = all_issues.get(issue, 0) + 1

        # Build report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_documents': len(self.metrics),
                'average_health_score': round(average_score, 2),
                'total_words': total_words,
                'total_code_blocks': total_code_blocks,
                'total_links': total_links,
            },
            'health_distribution': {
                'excellent': {
                    'count': len(excellent),
                    'percentage': round(len(excellent) / len(self.metrics) * 100, 1)
                },
                'good': {
                    'count': len(good),
                    'percentage': round(len(good) / len(self.metrics) * 100, 1)
                },
                'fair': {
                    'count': len(fair),
                    'percentage': round(len(fair) / len(self.metrics) * 100, 1)
                },
                'poor': {
                    'count': len(poor),
                    'percentage': round(len(poor) / len(self.metrics) * 100, 1)
                }
            },
            'critical_issues': [
                {
                    'issue': issue,
                    'documents_affected': count
                }
                for issue, count in sorted(all_issues.items(), key=lambda x: x[1], reverse=True)
            ],
            'documents': [asdict(m) for m in sorted(self.metrics, key=lambda m: m.health_score, reverse=True)]
        }

        return report

    def print_report(self) -> None:
        """Print a formatted report to console"""
        report = self.generate_report()

        print("\n" + "="*80)
        print("TECHNICAL DOCUMENTATION HEALTH REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Summary
        summary = report['summary']
        print(f"Total Documents: {summary['total_documents']}")
        print(f"Average Health Score: {summary['average_health_score']}/100")
        print(f"Total Words: {summary['total_words']:,}")
        print(f"Code Examples: {summary['total_code_blocks']}")
        print(f"Links: {summary['total_links']}\n")

        # Health Distribution
        print("Health Distribution:")
        dist = report['health_distribution']
        print(f"  Excellent (85-100): {dist['excellent']['count']} ({dist['excellent']['percentage']}%)")
        print(f"  Good (70-84): {dist['good']['count']} ({dist['good']['percentage']}%)")
        print(f"  Fair (50-69): {dist['fair']['count']} ({dist['fair']['percentage']}%)")
        print(f"  Poor (<50): {dist['poor']['count']} ({dist['poor']['percentage']}%)\n")

        # Critical Issues
        if report['critical_issues']:
            print("Critical Issues:")
            for item in report['critical_issues'][:5]:
                print(f"  • {item['issue']} ({item['documents_affected']} doc(s))")

        print("\nDocument Details:")
        print("-"*80)
        for doc in report['documents'][:10]:
            status = "✓" if doc['health_score'] >= 70 else "✗"
            print(f"{status} {doc['filename']:<30} Score: {doc['health_score']:.1f}/100")
            if doc['issues']:
                for issue in doc['issues']:
                    print(f"    ⚠ {issue}")

        print("="*80 + "\n")

    def export_json(self, output_file: str) -> None:
        """Export report as JSON"""
        report = self.generate_report()
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report exported to {output_file}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Monitor technical documentation health')
    parser.add_argument('--path', default='.', help='Path to documentation directory')
    parser.add_argument('--export', help='Export report to JSON file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    monitor = ContentHealthMonitor(args.path)

    if args.json:
        report = monitor.generate_report()
        print(json.dumps(report, indent=2))
    else:
        monitor.print_report()

    if args.export:
        monitor.export_json(args.export)


if __name__ == '__main__':
    main()

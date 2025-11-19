#!/usr/bin/env python3

"""
Style Report Generator

Generates comprehensive HTML style compliance reports from Vale output.
Provides metrics, visualizations, and recommendations for style improvements.

Usage: python3 style-report-generator.py [options] [files...]
"""

import json
import sys
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import re

class StyleReportGenerator:
    def __init__(self, options=None):
        """Initialize the report generator."""
        self.options = options or {}
        self.issues = []
        self.files_checked = 0
        self.total_lines = 0
        self.statistics = {
            'by_severity': defaultdict(int),
            'by_rule': defaultdict(int),
            'by_file': defaultdict(list),
            'by_category': defaultdict(int)
        }

    def run_vale(self, files):
        """Run Vale on specified files and capture output."""
        try:
            cmd = ['vale', '--output=json']

            if self.options.get('config'):
                cmd.extend(['--config', self.options['config']])

            cmd.extend(files)

            result = subprocess.run(cmd, capture_output=True, text=True)
            return json.loads(result.stdout)
        except Exception as e:
            print(f"Error running Vale: {e}", file=sys.stderr)
            return {}

    def process_vale_output(self, vale_output):
        """Process Vale JSON output and extract statistics."""
        for file_path, alerts in vale_output.items():
            if not alerts:
                self.files_checked += 1
                continue

            self.files_checked += 1

            for alert in alerts:
                issue = {
                    'file': file_path,
                    'line': alert.get('Line', 0),
                    'column': alert.get('Column', 0),
                    'rule': alert.get('Rule', 'Unknown'),
                    'message': alert.get('Message', ''),
                    'severity': alert.get('Level', 'suggestion'),
                    'suggestion': alert.get('Suggestion', '')
                }

                self.issues.append(issue)

                # Update statistics
                self.statistics['by_severity'][issue['severity']] += 1
                self.statistics['by_rule'][issue['rule']] += 1
                self.statistics['by_file'][file_path].append(issue)

                # Categorize
                category = self.categorize_rule(issue['rule'])
                self.statistics['by_category'][category] += 1

    def categorize_rule(self, rule):
        """Categorize rule by name."""
        categories = {
            'Accessibility': ['Screen', 'Heading', 'Image', 'Alt'],
            'Inclusive': ['Inclusive', 'Gender', 'Diversity'],
            'Consistency': ['Consistency', 'Product', 'Capitalization'],
            'Readability': ['Readability', 'Passive', 'Jargon'],
            'Formatting': ['Code', 'List', 'Format', 'Emphasis'],
            'Technical': ['API', 'Command', 'File'],
            'Grammar': ['Contraction', 'Punctuation', 'Spelling'],
        }

        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in rule:
                    return category

        return 'Other'

    def generate_html_report(self):
        """Generate comprehensive HTML report."""
        html = []

        # Header
        html.append(self.generate_header())

        # Summary Section
        html.append(self.generate_summary())

        # Statistics Section
        html.append(self.generate_statistics())

        # Issues by Severity
        html.append(self.generate_severity_breakdown())

        # Issues by Category
        html.append(self.generate_category_breakdown())

        # Detailed Issues
        html.append(self.generate_detailed_issues())

        # Recommendations
        html.append(self.generate_recommendations())

        # Footer
        html.append(self.generate_footer())

        return '\n'.join(html)

    def generate_header(self):
        """Generate HTML header."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Style Compliance Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}

        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}

        .card h3 {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}

        .card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}

        .card.error .value {{
            color: #e74c3c;
        }}

        .card.warning .value {{
            color: #f39c12;
        }}

        .card.success .value {{
            color: #27ae60;
        }}

        .section {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}

        .section h2 {{
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}

        th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #333;
        }}

        tr:hover {{
            background-color: #f8f9fa;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}

        .badge.error {{
            background-color: #fadbd8;
            color: #c0392b;
        }}

        .badge.warning {{
            background-color: #fdebd0;
            color: #d68910;
        }}

        .badge.suggestion {{
            background-color: #d5f4e6;
            color: #117a65;
        }}

        .chart {{
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}

        .chart-bar {{
            display: flex;
            align-items: center;
            margin: 10px 0;
        }}

        .chart-label {{
            width: 150px;
            font-weight: 600;
        }}

        .chart-bar-fill {{
            flex-grow: 1;
            height: 30px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 4px;
            margin: 0 10px;
            display: flex;
            align-items: center;
            padding: 0 10px;
            color: white;
            font-size: 0.9em;
            font-weight: 600;
        }}

        .recommendation {{
            padding: 15px;
            background: #e8f5e9;
            border-left: 4px solid #27ae60;
            margin: 10px 0;
            border-radius: 4px;
        }}

        .recommendation h4 {{
            color: #1b5e20;
            margin-bottom: 5px;
        }}

        .recommendation p {{
            color: #558b2f;
            margin: 5px 0;
        }}

        footer {{
            text-align: center;
            color: #999;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}

        .no-issues {{
            text-align: center;
            padding: 40px;
            color: #666;
        }}

        .no-issues-icon {{
            font-size: 3em;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Style Compliance Report</h1>
            <p>Technical Documentation Style Analysis</p>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>
"""

    def generate_summary(self):
        """Generate summary section."""
        total_issues = len(self.issues)
        errors = self.statistics['by_severity'].get('error', 0)
        warnings = self.statistics['by_severity'].get('warning', 0)
        suggestions = self.statistics['by_severity'].get('suggestion', 0)

        compliance_score = max(0, 100 - (errors * 10 + warnings * 5 + suggestions * 1))

        return f"""
        <div class="summary-cards">
            <div class="card success">
                <h3>Compliance Score</h3>
                <div class="value">{compliance_score}%</div>
            </div>
            <div class="card">
                <h3>Files Checked</h3>
                <div class="value">{self.files_checked}</div>
            </div>
            <div class="card">
                <h3>Total Issues</h3>
                <div class="value">{total_issues}</div>
            </div>
            <div class="card error">
                <h3>Errors</h3>
                <div class="value">{errors}</div>
            </div>
            <div class="card warning">
                <h3>Warnings</h3>
                <div class="value">{warnings}</div>
            </div>
            <div class="card">
                <h3>Suggestions</h3>
                <div class="value">{suggestions}</div>
            </div>
        </div>
"""

    def generate_statistics(self):
        """Generate statistics section."""
        if not self.issues:
            return """
        <div class="section">
            <div class="no-issues">
                <div class="no-issues-icon">✓</div>
                <h3>No Style Issues Found!</h3>
                <p>Your documentation meets all style guidelines.</p>
            </div>
        </div>
"""

        html = ['<div class="section"><h2>Rules Triggered</h2><div class="chart">']

        # Sort rules by frequency
        sorted_rules = sorted(
            self.statistics['by_rule'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        max_count = max([count for _, count in sorted_rules]) if sorted_rules else 1

        for rule, count in sorted_rules:
            percentage = (count / max_count) * 100
            html.append(f"""
            <div class="chart-bar">
                <div class="chart-label">{rule}</div>
                <div class="chart-bar-fill" style="width: {percentage}%;">{count}</div>
            </div>
""")

        html.append('</div></div>')
        return '\n'.join(html)

    def generate_severity_breakdown(self):
        """Generate severity breakdown section."""
        html = ['<div class="section"><h2>Issues by Severity</h2><table>']
        html.append('<tr><th>Severity</th><th>Count</th><th>Percentage</th></tr>')

        total = sum(self.statistics['by_severity'].values())

        for severity in ['error', 'warning', 'suggestion']:
            count = self.statistics['by_severity'].get(severity, 0)
            percentage = (count / total * 100) if total > 0 else 0

            html.append(f"""
            <tr>
                <td><span class="badge {severity}">{severity.upper()}</span></td>
                <td>{count}</td>
                <td>{percentage:.1f}%</td>
            </tr>
""")

        html.append('</table></div>')
        return '\n'.join(html)

    def generate_category_breakdown(self):
        """Generate category breakdown section."""
        html = ['<div class="section"><h2>Issues by Category</h2><div class="chart">']

        sorted_categories = sorted(
            self.statistics['by_category'].items(),
            key=lambda x: x[1],
            reverse=True
        )

        max_count = max([count for _, count in sorted_categories]) if sorted_categories else 1

        for category, count in sorted_categories:
            percentage = (count / max_count) * 100
            html.append(f"""
            <div class="chart-bar">
                <div class="chart-label">{category}</div>
                <div class="chart-bar-fill" style="width: {percentage}%;">{count}</div>
            </div>
""")

        html.append('</div></div>')
        return '\n'.join(html)

    def generate_detailed_issues(self):
        """Generate detailed issues section."""
        if not self.issues:
            return ''

        html = ['<div class="section"><h2>Detailed Issues</h2><table>']
        html.append('<tr><th>File</th><th>Line</th><th>Rule</th><th>Severity</th><th>Message</th></tr>')

        # Sort by file, then line number
        sorted_issues = sorted(
            self.issues,
            key=lambda x: (x['file'], x['line'])
        )

        for issue in sorted_issues[:100]:  # Limit to 100 for readability
            html.append(f"""
            <tr>
                <td><code>{issue['file']}</code></td>
                <td>{issue['line']}</td>
                <td>{issue['rule']}</td>
                <td><span class="badge {issue['severity']}">{issue['severity']}</span></td>
                <td>{issue['message']}</td>
            </tr>
""")

        if len(self.issues) > 100:
            html.append(f'<tr><td colspan="5" style="text-align: center;"><em>... and {len(self.issues) - 100} more issues</em></td></tr>')

        html.append('</table></div>')
        return '\n'.join(html)

    def generate_recommendations(self):
        """Generate recommendations section."""
        html = ['<div class="section"><h2>Recommendations</h2>']

        # Analyze patterns
        top_rule = max(self.statistics['by_rule'].items(), key=lambda x: x[1])[0] if self.statistics['by_rule'] else None
        error_count = self.statistics['by_severity'].get('error', 0)
        warning_count = self.statistics['by_severity'].get('warning', 0)

        if error_count > 0:
            html.append(f"""
            <div class="recommendation">
                <h4>Priority: Fix Critical Errors</h4>
                <p>You have {error_count} critical errors that must be fixed before publication.</p>
                <p>Focus on these first to ensure style compliance.</p>
            </div>
""")

        if top_rule:
            html.append(f"""
            <div class="recommendation">
                <h4>Most Common Issue: {top_rule}</h4>
                <p>This rule is triggered most frequently in your documentation.</p>
                <p>Review the style guide for this rule and apply consistent fixes.</p>
            </div>
""")

        if warning_count > 0:
            html.append(f"""
            <div class="recommendation">
                <h4>Address Warnings</h4>
                <p>You have {warning_count} warnings that should be reviewed and addressed.</p>
                <p>These indicate areas where your documentation could be improved.</p>
            </div>
""")

        if len(self.issues) == 0:
            html.append("""
            <div class="recommendation">
                <h4>Excellent Compliance!</h4>
                <p>Your documentation meets all style requirements.</p>
                <p>Continue to maintain these standards in future updates.</p>
            </div>
""")

        html.append('</div>')
        return '\n'.join(html)

    def generate_footer(self):
        """Generate HTML footer."""
        return """
    </div>
    <footer>
        <p>Generated by Style Report Generator | Vale Style Checker</p>
    </footer>
</body>
</html>
"""

    def generate_report(self, files):
        """Main method to generate complete report."""
        print("Running Vale...", file=sys.stderr)
        vale_output = self.run_vale(files)

        print("Processing results...", file=sys.stderr)
        self.process_vale_output(vale_output)

        print("Generating HTML report...", file=sys.stderr)
        html = self.generate_html_report()

        return html


def main():
    parser = argparse.ArgumentParser(
        description='Generate style compliance reports from Vale output'
    )

    parser.add_argument('files', nargs='+', help='Files to check')
    parser.add_argument('--config', help='Vale configuration file')
    parser.add_argument('--output', '-o', help='Output HTML file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    options = {
        'config': args.config,
        'verbose': args.verbose
    }

    generator = StyleReportGenerator(options)
    html = generator.generate_report(args.files)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Report saved to: {args.output}")
    else:
        print(html)


if __name__ == '__main__':
    main()

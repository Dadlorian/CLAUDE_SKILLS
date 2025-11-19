"""
Locale Rendering Validation Module

Tests rendering of localized content in various contexts.
"""

import json
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


class LocaleRenderer:
    """Validates locale rendering in HTML/Web contexts."""

    def __init__(self, locale: str, source_dir: str, output_file: str = None):
        self.locale = locale
        self.source_dir = Path(source_dir)
        self.output_file = output_file or f'render-{locale}.html'
        self.render_results = {
            'locale': locale,
            'rendered': False,
            'html_output': '',
            'issues': [],
        }

    def render_all(self) -> str:
        """Render all locale content to HTML."""
        logger.info(f"Rendering locale: {self.locale}")

        html_content = self._generate_html_header()
        html_content += self._render_messages()
        html_content += self._render_test_cases()
        html_content += self._generate_html_footer()

        self.render_results['html_output'] = html_content
        self.render_results['rendered'] = True

        return html_content

    def save_render(self, output_file: str = None) -> str:
        """Save rendered HTML to file."""
        if not self.render_results['rendered']:
            self.render_all()

        file_path = output_file or self.output_file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.render_results['html_output'])

        logger.info(f"Rendered HTML saved to: {file_path}")
        return file_path

    def _generate_html_header(self) -> str:
        """Generate HTML document header."""
        return f"""<!DOCTYPE html>
<html lang="{self.locale}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Locale Rendering Test - {self.locale}</title>
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
            background: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        h1 {{
            color: #2c3e50;
            margin-bottom: 30px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}

        h2 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
        }}

        .test-section {{
            margin-bottom: 30px;
            padding: 20px;
            background: #f9f9f9;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }}

        .message {{
            padding: 10px;
            margin: 10px 0;
            background: white;
            border: 1px solid #ecf0f1;
            border-radius: 4px;
            font-size: 14px;
            word-break: break-word;
        }}

        .success {{
            color: #27ae60;
            background: #ecf8f4;
            border-color: #27ae60;
        }}

        .warning {{
            color: #f39c12;
            background: #fef5e7;
            border-color: #f39c12;
        }}

        .error {{
            color: #e74c3c;
            background: #fadbd8;
            border-color: #e74c3c;
        }}

        .metadata {{
            font-size: 12px;
            color: #7f8c8d;
            margin-top: 5px;
        }}

        .rtl {{
            direction: rtl;
            text-align: right;
        }}

        .ltr {{
            direction: ltr;
            text-align: left;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}

        th {{
            background: #34495e;
            color: white;
            font-weight: 600;
        }}

        tr:hover {{
            background: #f9f9f9;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}

        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 4px;
            border: 1px solid #ecf0f1;
            text-align: center;
        }}

        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
        }}

        .stat-label {{
            font-size: 12px;
            color: #7f8c8d;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Locale Rendering Test Report: {self.locale.upper()}</h1>
"""

    def _generate_html_footer(self) -> str:
        """Generate HTML document footer."""
        return """
    </div>
</body>
</html>
"""

    def _render_messages(self) -> str:
        """Render all messages from locale."""
        messages_file = self.source_dir / 'messages.json'
        if not messages_file.exists():
            return '<p>No messages.json file found</p>'

        try:
            with open(messages_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        except Exception as e:
            return f'<p class="error">Error loading messages: {e}</p>'

        html = '<div class="test-section"><h2>Rendered Messages</h2>'

        for key, value in list(messages.items())[:20]:  # Limit to first 20
            if not isinstance(value, str):
                continue

            html += f"""
            <div class="message">
                <strong>{key}:</strong> {value}
                <div class="metadata">Length: {len(value)} chars</div>
            </div>
            """

        html += '</div>'
        return html

    def _render_test_cases(self) -> str:
        """Render various test cases."""
        html = '<div class="test-section"><h2>Rendering Test Cases</h2>'

        test_cases = [
            ('Latin Characters', 'The quick brown fox'),
            ('Numbers', '0123456789'),
            ('Punctuation', 'Hello! How are you? Great.'),
            ('Special Symbols', '© ® ™ € ¥ £ § ¶ † ‡'),
            ('Quotes', '"Hello" and \'World\''),
            ('Spacing Test', 'Multiple     spaces     here'),
        ]

        for name, content in test_cases:
            html += f"""
            <div class="message">
                <strong>{name}:</strong> <span>{content}</span>
            </div>
            """

        html += '</div>'
        return html

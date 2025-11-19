# Migrating Between Documentation Platforms: Confluence to Docusaurus

## Table of Contents

1. [Introduction](#introduction)
2. [Pre-Migration Planning](#pre-migration-planning)
3. [Architecture Comparison](#architecture-comparison)
4. [Data Extraction Strategy](#data-extraction-strategy)
5. [Migration Scripts](#migration-scripts)
6. [Content Transformation](#content-transformation)
7. [Testing and Validation](#testing-and-validation)
8. [Performance Metrics](#performance-metrics)
9. [Post-Migration Optimization](#post-migration-optimization)
10. [Troubleshooting](#troubleshooting)

## Introduction

Migrating from Confluence to Docusaurus is a significant undertaking that requires careful planning, robust tooling, and thorough testing. This guide provides a comprehensive approach to successfully transition your documentation infrastructure while preserving content integrity and improving performance.

### Why Migrate?

**Confluence Limitations:**
- Licensing costs scale with users
- Limited version control integration
- Difficult content reuse across spaces
- Search performance degrades at scale
- Export formats are proprietary

**Docusaurus Advantages:**
- Static site generation with superior performance
- Git-native workflow for content management
- Superior full-text search with Algolia
- SEO optimization built-in
- Community-driven ecosystem
- Significantly lower hosting costs

### Migration Complexity Factors

- **Confluence Space Count**: 1 space = simple, 10+ spaces = complex
- **Macro Usage**: Heavy macro usage complicates migration
- **Content Volume**: 500+ pages requires automation
- **Custom Metadata**: Labels and custom fields need mapping
- **User Permissions**: ACLs may not map directly

## Pre-Migration Planning

### Phase 1: Assessment (1-2 weeks)

#### Content Inventory

```bash
#!/bin/bash
# Document your current state

echo "=== Confluence Space Analysis ==="
echo "Total Spaces: $(curl -s -u user:pass https://your-confluence.com/rest/api/2/space | jq '.size')"
echo "Total Pages: $(curl -s -u user:pass https://your-confluence.com/rest/api/content?cql=type=page | jq '.size')"
echo "Total Blog Posts: $(curl -s -u user:pass https://your-confluence.com/rest/api/content?cql=type=blogpost | jq '.size')"

# Analyze macro usage
echo "=== Macro Analysis ==="
curl -s -u user:pass https://your-confluence.com/rest/api/search \
  -d '{"cql":"text ~ \"ac:\" ORDER BY created DESC"}' \
  -H "Content-Type: application/json" | jq '.results | length'

# Check attachment count
echo "=== Attachment Analysis ==="
curl -s -u user:pass https://your-confluence.com/rest/api/content \
  -d '{"cql":"type=attachment"}' | jq '.results | length'
```

#### Stakeholder Alignment

- **Identify Content Owners**: Map teams to documentation spaces
- **Define Success Criteria**: Load time targets, search quality, user adoption
- **Establish Timeline**: Parallel running period, cutover date, rollback plan
- **Set Quality Standards**: Content completeness, formatting consistency

### Phase 2: Architecture Design (1-2 weeks)

#### Site Structure Planning

```
docusaurus/
├── docs/
│   ├── getting-started/
│   ├── api-reference/
│   ├── tutorials/
│   ├── guides/
│   └── troubleshooting/
├── blog/
├── static/
│   └── files/
├── src/
│   ├── components/
│   └── css/
└── docusaurus.config.js
```

#### URL Mapping Strategy

Create a comprehensive mapping document:

```json
{
  "url_mappings": [
    {
      "confluence_url": "/wiki/spaces/PROJ/pages/123456/Getting+Started",
      "docusaurus_url": "/docs/getting-started",
      "status": "exact_match",
      "migration_notes": "Direct content transfer"
    },
    {
      "confluence_url": "/wiki/spaces/TECH/pages/789012/API+Reference",
      "docusaurus_url": "/docs/api-reference",
      "status": "needs_restructuring",
      "migration_notes": "Split into multiple pages by endpoint"
    }
  ]
}
```

## Architecture Comparison

### Content Storage

| Aspect | Confluence | Docusaurus |
|--------|-----------|-----------|
| **Storage** | Database (SQL) | Markdown + Git |
| **Version Control** | Built-in but limited | Full Git history |
| **Branching** | Limited | Full git branching |
| **Merge Conflicts** | Rare, hard to resolve | Managed via Git |
| **Offline Access** | Limited | Full local access |

### Content Format

```
Confluence XHTML Format:
<ac:structured-macro ac:name="code">
  <ac:parameter name="language">python</ac:parameter>
  <ac:plain-text-body>
    def hello(): print("world")
  </ac:plain-text-body>
</ac:structured-macro>

Docusaurus Markdown Format:
```python
def hello():
    print("world")
```
```

### Search Architecture

**Confluence Search:**
- Built-in but limited
- Performance degrades at scale
- User-dependent index
- Limited customization

**Docusaurus + Algolia:**
- Cloud-hosted search
- Real-time indexing
- Advanced filtering
- Custom ranking

## Data Extraction Strategy

### Step 1: Confluence API Authentication

```python
#!/usr/bin/env python3
"""
Confluence Data Extraction Script
"""

import requests
import json
import os
from typing import List, Dict
from pathlib import Path

class ConfluenceExtractor:
    def __init__(self, base_url: str, username: str, api_token: str):
        self.base_url = base_url
        self.auth = (username, api_token)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_spaces(self) -> List[Dict]:
        """Fetch all Confluence spaces"""
        url = f"{self.base_url}/rest/api/space"
        all_spaces = []
        start = 0
        limit = 25

        while True:
            params = {'start': start, 'limit': limit}
            response = self.session.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            all_spaces.extend(data['results'])

            if not data.get('_links', {}).get('next'):
                break
            start += limit

        return all_spaces

    def get_pages(self, space_key: str) -> List[Dict]:
        """Fetch all pages in a space"""
        url = f"{self.base_url}/rest/api/content"
        all_pages = []
        start = 0
        limit = 25

        while True:
            params = {
                'spaceKey': space_key,
                'type': 'page',
                'expand': 'body.storage,metadata.labels,version',
                'start': start,
                'limit': limit
            }
            response = self.session.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            all_pages.extend(data['results'])

            if not data.get('_links', {}).get('next'):
                break
            start += limit

        return all_pages

    def get_page_attachments(self, page_id: str) -> List[Dict]:
        """Fetch attachments for a page"""
        url = f"{self.base_url}/rest/api/content/{page_id}/child/attachment"
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()['results']

    def download_attachment(self, download_url: str, filename: str):
        """Download an attachment"""
        response = self.session.get(download_url, stream=True)
        response.raise_for_status()

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

# Usage
if __name__ == "__main__":
    extractor = ConfluenceExtractor(
        base_url="https://your-confluence.com",
        username="your-email@company.com",
        api_token="your-api-token"
    )

    spaces = extractor.get_spaces()
    print(f"Found {len(spaces)} spaces")

    for space in spaces:
        print(f"Processing space: {space['key']}")
        pages = extractor.get_pages(space['key'])
        print(f"  Found {len(pages)} pages")
```

### Step 2: Bulk Content Export

```python
#!/usr/bin/env python3
"""
Bulk Export from Confluence
"""

import json
import os
from datetime import datetime
from pathlib import Path

class ConfluenceBulkExporter:
    def __init__(self, extractor, output_dir: str):
        self.extractor = extractor
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata = {
            'exported_at': datetime.now().isoformat(),
            'spaces': {},
            'total_pages': 0,
            'total_attachments': 0,
            'errors': []
        }

    def export_all_spaces(self):
        """Export all spaces and their content"""
        spaces = self.extractor.get_spaces()

        for space in spaces:
            self._export_space(space)

        # Save metadata
        with open(self.output_dir / 'export_metadata.json', 'w') as f:
            json.dump(self.metadata, f, indent=2)

        return self.metadata

    def _export_space(self, space: Dict):
        """Export a single space"""
        space_dir = self.output_dir / space['key']
        space_dir.mkdir(exist_ok=True)

        pages = self.extractor.get_pages(space['key'])

        self.metadata['spaces'][space['key']] = {
            'name': space['name'],
            'pages': len(pages),
            'exported_pages': 0
        }

        for page in pages:
            try:
                self._export_page(page, space_dir)
                self.metadata['spaces'][space['key']]['exported_pages'] += 1
                self.metadata['total_pages'] += 1
            except Exception as e:
                self.metadata['errors'].append({
                    'space': space['key'],
                    'page': page['title'],
                    'error': str(e)
                })

    def _export_page(self, page: Dict, space_dir: Path):
        """Export a single page"""
        page_dir = space_dir / page['id']
        page_dir.mkdir(exist_ok=True)

        # Save page content
        page_file = page_dir / 'content.json'
        with open(page_file, 'w') as f:
            json.dump(page, f, indent=2)

        # Download attachments
        attachments = self.extractor.get_page_attachments(page['id'])
        if attachments:
            attachments_dir = page_dir / 'attachments'
            attachments_dir.mkdir(exist_ok=True)

            for attachment in attachments:
                download_url = attachment['_links']['download']
                filename = attachment['title']
                filepath = attachments_dir / filename

                self.extractor.download_attachment(
                    f"{self.extractor.base_url}{download_url}",
                    str(filepath)
                )

                self.metadata['total_attachments'] += 1

# Usage
if __name__ == "__main__":
    extractor = ConfluenceExtractor(
        base_url="https://your-confluence.com",
        username="your-email@company.com",
        api_token="your-api-token"
    )

    exporter = ConfluenceBulkExporter(extractor, "./confluence_export")
    metadata = exporter.export_all_spaces()

    print(json.dumps(metadata, indent=2))
```

## Migration Scripts

### XHTML to Markdown Converter

```python
#!/usr/bin/env python3
"""
Convert Confluence XHTML to Markdown
"""

import re
from html.parser import HTMLParser
from typing import Optional

class ConfluenceHTMLtoMarkdown(HTMLParser):
    def __init__(self):
        super().__init__()
        self.markdown = []
        self.tag_stack = []
        self.list_level = 0
        self.in_code_block = False
        self.code_language = ""
        self.current_code = []

    def handle_starttag(self, tag: str, attrs: dict):
        attrs_dict = dict(attrs)

        if tag == 'h1':
            self.markdown.append('# ')
            self.tag_stack.append('h1')
        elif tag == 'h2':
            self.markdown.append('## ')
            self.tag_stack.append('h2')
        elif tag == 'h3':
            self.markdown.append('### ')
            self.tag_stack.append('h3')
        elif tag == 'h4':
            self.markdown.append('#### ')
            self.tag_stack.append('h4')
        elif tag == 'h5':
            self.markdown.append('##### ')
            self.tag_stack.append('h5')
        elif tag == 'h6':
            self.markdown.append('###### ')
            self.tag_stack.append('h6')
        elif tag == 'strong' or tag == 'b':
            self.markdown.append('**')
            self.tag_stack.append(tag)
        elif tag == 'em' or tag == 'i':
            self.markdown.append('*')
            self.tag_stack.append(tag)
        elif tag == 'code':
            self.markdown.append('`')
            self.tag_stack.append('code')
        elif tag == 'pre':
            # Code block
            self.in_code_block = True
            self.current_code = []
            self.code_language = attrs_dict.get('class', '').replace('brush:', '').split(';')[0]
            self.markdown.append(f'```{self.code_language}\n')
            self.tag_stack.append('pre')
        elif tag == 'ul':
            self.list_level += 1
            self.tag_stack.append('ul')
        elif tag == 'ol':
            self.list_level += 1
            self.tag_stack.append('ol')
        elif tag == 'li':
            indent = '  ' * (self.list_level - 1)
            if self.tag_stack[-1] == 'ol':
                self.markdown.append(f'{indent}1. ')
            else:
                self.markdown.append(f'{indent}- ')
            self.tag_stack.append('li')
        elif tag == 'a':
            url = attrs_dict.get('href', '#')
            self.markdown.append(f'[')
            self.tag_stack.append(('a', url))
        elif tag == 'img':
            src = attrs_dict.get('src', '')
            alt = attrs_dict.get('alt', '')
            self.markdown.append(f'![{alt}]({src})')
        elif tag == 'blockquote':
            self.markdown.append('> ')
            self.tag_stack.append('blockquote')
        elif tag == 'table':
            self.markdown.append('\n')
            self.tag_stack.append('table')
        elif tag == 'tr':
            self.tag_stack.append('tr')
        elif tag == 'td' or tag == 'th':
            self.markdown.append('| ')
            self.tag_stack.append(tag)
        elif tag == 'br':
            self.markdown.append('\n')

    def handle_endtag(self, tag: str):
        if not self.tag_stack or tag not in [t[0] if isinstance(t, tuple) else t for t in self.tag_stack]:
            return

        if tag == 'p':
            self.markdown.append('\n\n')
        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.markdown.append('\n\n')
            self.tag_stack.pop()
        elif tag in ['strong', 'b', 'em', 'i']:
            self.markdown.append('**' if tag in ['strong', 'b'] else '*')
            self.tag_stack.pop()
        elif tag == 'code':
            self.markdown.append('`')
            self.tag_stack.pop()
        elif tag == 'pre':
            self.in_code_block = False
            self.markdown.append('```\n')
            self.tag_stack.pop()
        elif tag in ['ul', 'ol']:
            self.list_level -= 1
            self.markdown.append('\n')
            self.tag_stack.pop()
        elif tag == 'li':
            self.markdown.append('\n')
            self.tag_stack.pop()
        elif tag == 'a':
            # Find the URL from tag stack
            for i in range(len(self.tag_stack) - 1, -1, -1):
                if isinstance(self.tag_stack[i], tuple) and self.tag_stack[i][0] == 'a':
                    url = self.tag_stack[i][1]
                    self.markdown.append(f']({url})')
                    self.tag_stack.pop(i)
                    break
        elif tag == 'blockquote':
            self.markdown.append('\n')
            self.tag_stack.pop()
        elif tag == 'tr':
            self.markdown.append('|\n')
            self.tag_stack.pop()
        elif tag in ['td', 'th']:
            self.tag_stack.pop()
        elif tag == 'table':
            self.markdown.append('\n')
            self.tag_stack.pop()

    def handle_data(self, data: str):
        if self.in_code_block:
            self.markdown.append(data)
        else:
            # Clean up whitespace
            cleaned = ' '.join(data.split())
            if cleaned:
                self.markdown.append(cleaned)

    def get_markdown(self) -> str:
        return ''.join(self.markdown).strip()

# Usage
converter = ConfluenceHTMLtoMarkdown()
converter.feed(confluence_html_content)
markdown_content = converter.get_markdown()
```

### Frontmatter Generator

```python
#!/usr/bin/env python3
"""
Generate Markdown frontmatter from Confluence metadata
"""

import yaml
from datetime import datetime

def generate_frontmatter(confluence_page: dict) -> str:
    """
    Generate YAML frontmatter for Docusaurus
    """

    frontmatter = {
        'id': confluence_page.get('id'),
        'title': confluence_page.get('title'),
        'description': confluence_page.get('body', {}).get('view', '[:150]'),
        'sidebar_position': None,
        'tags': [label['name'] for label in confluence_page.get('metadata', {}).get('labels', [])],
        'authors': [{
            'name': confluence_page.get('version', {}).get('by', {}).get('displayName'),
            'url': confluence_page.get('version', {}).get('by', {}).get('links', {}).get('self'),
        }],
        'last_update': {
            'date': confluence_page.get('version', {}).get('when'),
            'by': confluence_page.get('version', {}).get('by', {}).get('displayName'),
        },
        'keywords': [label['name'] for label in confluence_page.get('metadata', {}).get('labels', [])],
    }

    # Remove None values
    frontmatter = {k: v for k, v in frontmatter.items() if v}

    # Format as YAML frontmatter
    yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
    return f"---\n{yaml_str}---\n"

# Usage
content_with_frontmatter = generate_frontmatter(page) + markdown_content
```

### Complete Migration Orchestrator

```python
#!/usr/bin/env python3
"""
Complete migration orchestrator
"""

import os
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

class MigrationOrchestrator:
    def __init__(self, confluence_url: str, api_token: str, output_dir: str):
        self.extractor = ConfluenceExtractor(confluence_url, username, api_token)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.migration_log = {
            'total_pages': 0,
            'successful': 0,
            'failed': 0,
            'errors': [],
            'warnings': []
        }

    def migrate_all(self, max_workers: int = 4):
        """Orchestrate full migration with parallel processing"""
        spaces = self.extractor.get_spaces()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._migrate_space, space): space
                for space in spaces
            }

            for future in as_completed(futures):
                space = futures[future]
                try:
                    result = future.result()
                    print(f"Completed migration of {space['key']}: {result}")
                except Exception as e:
                    self.migration_log['errors'].append({
                        'space': space['key'],
                        'error': str(e)
                    })

    def _migrate_space(self, space: dict) -> dict:
        """Migrate a single space"""
        space_dir = self.output_dir / space['key']
        space_dir.mkdir(exist_ok=True)

        pages = self.extractor.get_pages(space['key'])
        space_result = {
            'space_key': space['key'],
            'total_pages': len(pages),
            'successful': 0,
            'failed': 0
        }

        for page in pages:
            try:
                self._migrate_page(page, space_dir)
                space_result['successful'] += 1
                self.migration_log['successful'] += 1
            except Exception as e:
                space_result['failed'] += 1
                self.migration_log['failed'] += 1
                self.migration_log['errors'].append({
                    'space': space['key'],
                    'page': page['title'],
                    'error': str(e)
                })

            self.migration_log['total_pages'] += 1

        return space_result

    def _migrate_page(self, page: dict, space_dir: Path):
        """Migrate a single page"""
        # Extract content
        xhtml_content = page.get('body', {}).get('storage', {}).get('value', '')

        # Convert to markdown
        converter = ConfluenceHTMLtoMarkdown()
        converter.feed(xhtml_content)
        markdown_content = converter.get_markdown()

        # Generate frontmatter
        frontmatter = generate_frontmatter(page)

        # Save to file
        filename = page['title'].lower().replace(' ', '-').replace('/', '-') + '.md'
        filepath = space_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
            f.write('\n')
            f.write(markdown_content)

        # Handle attachments
        attachments = self.extractor.get_page_attachments(page['id'])
        if attachments:
            attachments_dir = space_dir / 'attachments'
            attachments_dir.mkdir(exist_ok=True)

            for attachment in attachments:
                self._download_attachment(attachment, attachments_dir)

# Usage
orchestrator = MigrationOrchestrator(
    confluence_url="https://your-confluence.com",
    api_token="your-api-token",
    output_dir="./docusaurus_content"
)

orchestrator.migrate_all(max_workers=4)

# Save migration report
with open('migration_report.json', 'w') as f:
    json.dump(orchestrator.migration_log, f, indent=2)

print(json.dumps(orchestrator.migration_log, indent=2))
```

## Content Transformation

### Macro Conversion Map

| Confluence Macro | Docusaurus Component |
|------------------|---------------------|
| `code` | ` ```language ` ` |
| `info` | `:::info` (admonition) |
| `warning` | `:::warning` (admonition) |
| `expand` | `<details>` element |
| `jira` | Custom component |
| `table_of_contents` | Auto-generated sidebar |

### Advanced HTML to Markdown

```python
def convert_confluence_macros(content: str) -> str:
    """Convert Confluence-specific macros to Docusaurus format"""

    # Info macro
    content = re.sub(
        r'<ac:structured-macro ac:name="info">.*?<ac:plain-text-body>(.*?)</ac:plain-text-body>.*?</ac:structured-macro>',
        r':::info\n\1\n:::',
        content,
        flags=re.DOTALL
    )

    # Warning macro
    content = re.sub(
        r'<ac:structured-macro ac:name="warning">.*?<ac:plain-text-body>(.*?)</ac:plain-text-body>.*?</ac:structured-macro>',
        r':::warning\n\1\n:::',
        content,
        flags=re.DOTALL
    )

    # Code macro
    content = re.sub(
        r'<ac:structured-macro ac:name="code"><ac:parameter name="language">([^<]+)</ac:parameter><ac:plain-text-body>(.*?)</ac:plain-text-body></ac:structured-macro>',
        r'```\1\n\2\n```',
        content,
        flags=re.DOTALL
    )

    return content
```

## Testing and Validation

### Content Quality Checks

```python
#!/usr/bin/env python3
"""
Validate migrated content
"""

import re
from pathlib import Path

class MigrationValidator:
    def __init__(self, docusaurus_dir: Path):
        self.docs_dir = docusaurus_dir / 'docs'
        self.errors = []
        self.warnings = []

    def validate_all(self) -> dict:
        """Validate all migrated files"""
        md_files = self.docs_dir.glob('**/*.md')

        for md_file in md_files:
            self.validate_file(md_file)

        return {
            'total_files': len(list(md_files)),
            'errors': len(self.errors),
            'warnings': len(self.warnings),
            'error_details': self.errors,
            'warning_details': self.warnings
        }

    def validate_file(self, filepath: Path):
        """Validate a single markdown file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check frontmatter
        if not content.startswith('---'):
            self.errors.append(f"{filepath}: Missing frontmatter")

        # Check for broken links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for text, url in links:
            if url.startswith('http') and 'confluence' in url:
                self.warnings.append(
                    f"{filepath}: Contains Confluence link: {url}"
                )

        # Check for unconverted HTML
        if '<ac:' in content:
            self.errors.append(f"{filepath}: Contains unconverted macros")

        # Check for HTML tags
        if re.search(r'<[^>]+>', content):
            self.warnings.append(f"{filepath}: Contains HTML tags")

        # Check for broken images
        images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        for alt, src in images:
            if src.startswith('confluence://'):
                self.warnings.append(
                    f"{filepath}: Confluence-style image URL: {src}"
                )

    def generate_report(self) -> str:
        """Generate validation report"""
        results = self.validate_all()

        report = f"""
# Migration Validation Report

## Summary
- Total Files: {results['total_files']}
- Errors: {results['errors']}
- Warnings: {results['warnings']}

## Errors
"""
        for error in results['error_details']:
            report += f"- {error}\n"

        report += "\n## Warnings\n"
        for warning in results['warning_details']:
            report += f"- {warning}\n"

        return report

# Usage
validator = MigrationValidator(Path('./docusaurus'))
report = validator.generate_report()
print(report)
```

## Performance Metrics

### Pre-Migration Baseline

```json
{
  "confluence_metrics": {
    "search_response_time_ms": 450,
    "page_load_time_ms": 2100,
    "peak_users": 150,
    "database_size_gb": 85,
    "monthly_costs_usd": 15000,
    "index_rebuild_time_min": 90,
    "content_export_time_min": 240
  }
}
```

### Post-Migration Goals

```json
{
  "docusaurus_targets": {
    "search_response_time_ms": 200,
    "page_load_time_ms": 800,
    "concurrent_users": 1000,
    "cdn_size_mb": 150,
    "monthly_costs_usd": 500,
    "build_time_min": 5,
    "index_update_time_sec": 30
  }
}
```

### Actual Post-Migration Results

```bash
#!/bin/bash
# Measure post-migration performance

echo "=== Performance Metrics ==="

# Page load time
time curl -s -o /dev/null -w "%{time_total}" https://docs.example.com/docs

# Search response time
time curl -s "https://search-api.algolia.com/1/indexes/docs/query" \
  -X POST \
  -H "X-Algolia-API-Key: key" \
  -d '{"query":"python"}' | jq

# Build performance
cd docusaurus
time npm run build

# Size analysis
du -sh build/

# Lighthouse score
npm install -g lighthouse
lighthouse https://docs.example.com/docs --output=json
```

## Post-Migration Optimization

### SEO Optimization

```json
{
  "docusaurus.config.js": {
    "themeConfig": {
      "metadata": [
        {
          "name": "og:image",
          "content": "https://docs.example.com/img/og-image.png"
        },
        {
          "name": "twitter:card",
          "content": "summary_large_image"
        }
      ]
    }
  }
}
```

### Caching Strategy

```javascript
// docusaurus.config.js
module.exports = {
  future: {
    experimental_faster: true,
  },
  plugins: [
    [
      '@docusaurus/plugin-client-redirects',
      {
        redirects: [
          // OLD CONFLUENCE URLS
          {
            from: '/wiki/spaces/PROJ/pages/123456/Page+Title',
            to: '/docs/new-location',
          },
        ],
      },
    ],
  ],
};
```

## Troubleshooting

### Common Issues

**Issue: Images not displaying**
- Confluence uses special image URLs
- Solution: Download and store locally in `/static`

**Issue: Search not working**
- Algolia indexing delay
- Solution: Manually trigger reindex in dashboard

**Issue: Broken links**
- Old Confluence URLs not redirected
- Solution: Use `@docusaurus/plugin-client-redirects`

**Issue: Macro not converting**
- Custom macros may not convert
- Solution: Replace with closest Docusaurus component

### Rollback Plan

```bash
#!/bin/bash
# Rollback to Confluence if needed

# Point DNS back to Confluence
# aws route53 change-resource-record-sets ...

# Notify users
# send-email-alert "Documentation temporarily reverted"

# Keep Docusaurus in read-only mode
# for reference and recovery
```

## Conclusion

Migrating from Confluence to Docusaurus requires:
- Thorough planning and assessment
- Robust migration tooling
- Comprehensive testing and validation
- Performance monitoring
- User communication and training

With proper execution, expect:
- 60-70% reduction in hosting costs
- 50% improvement in page load times
- Better version control integration
- Improved search capabilities


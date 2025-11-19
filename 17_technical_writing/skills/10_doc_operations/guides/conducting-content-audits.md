# Conducting Content Audits: Quarterly Process Guide

## Overview

A content audit systematically reviews all documentation to identify gaps, outdated information, redundancy, and improvement opportunities. This quarterly process ensures documentation remains current, accurate, and valuable to users.

## Purpose and Benefits

**Why conduct content audits?**
- Identify outdated information requiring updates
- Discover gaps in documentation coverage
- Find and eliminate duplicated content
- Assess content relevance and accuracy
- Improve search engine optimization (SEO)
- Enhance user satisfaction and engagement
- Reduce maintenance overhead

**Expected outcomes:**
- Updated content list
- Prioritized improvement roadmap
- Deprecated content removal list
- Content consolidation opportunities

## Part 1: Audit Planning and Preparation

### Define Audit Scope

```yaml
# audit_scope.yml
audit_name: "Q4 2024 Documentation Audit"
audit_dates: "2024-10-01 to 2024-12-31"
review_period: "12 months prior"

documentation_sections:
  - API Reference
  - Getting Started
  - Tutorials
  - Guides
  - Troubleshooting
  - FAQ
  - Changelogs
  - Release Notes

audit_team:
  - Product Manager (lead)
  - Technical Writer
  - Developer Advocate
  - QA Engineer
  - Customer Support Representative

success_criteria:
  - Review 95% of pages
  - Update 80% of outdated content
  - Reduce page count by 10-15%
  - Increase average satisfaction score to 4.5/5
```

### Establish Audit Criteria

Create a scoring system to evaluate content:

```python
# audit_criteria.py
class ContentAuditCriteria:
    def __init__(self):
        self.criteria = {
            'Accuracy': {
                'weight': 25,
                'questions': [
                    'Is information accurate?',
                    'Are examples current and working?',
                    'Are API endpoints correct?',
                    'Are version references current?'
                ]
            },
            'Completeness': {
                'weight': 20,
                'questions': [
                    'Does page cover the topic thoroughly?',
                    'Are there obvious gaps or missing sections?',
                    'Are edge cases documented?',
                    'Are prerequisites clearly listed?'
                ]
            },
            'Clarity': {
                'weight': 20,
                'questions': [
                    'Is content easy to understand?',
                    'Is language appropriate for audience?',
                    'Are examples clear and helpful?',
                    'Is structure logical and navigable?'
                ]
            },
            'Relevance': {
                'weight': 15,
                'questions': [
                    'Is content still relevant?',
                    'Is it frequently accessed?',
                    'Does it align with current product?',
                    'Is deprecation status clear?'
                ]
            },
            'Engagement': {
                'weight': 10,
                'questions': [
                    'Does it have visual elements?',
                    'Are there code examples?',
                    'Are there interactive elements?',
                    'Is tone engaging and helpful?'
                ]
            },
            'SEO': {
                'weight': 10,
                'questions': [
                    'Is title SEO-optimized?',
                    'Are keywords naturally included?',
                    'Is meta description present?',
                    'Are headers properly structured?'
                ]
            }
        }

    def calculate_score(self, answers):
        """Calculate weighted content score"""
        total_score = 0
        for criterion, data in self.criteria.items():
            # Assume answers provided as dict with criterion: score
            criterion_score = answers.get(criterion, 0)
            weighted_score = (criterion_score / 10) * data['weight']
            total_score += weighted_score
        return total_score

    def get_rating(self, score):
        """Convert score to rating"""
        if score >= 80:
            return 'Excellent'
        elif score >= 60:
            return 'Good'
        elif score >= 40:
            return 'Fair'
        else:
            return 'Poor - Requires Significant Update'
```

## Part 2: Create Audit Inventory

### Build Content Inventory

```python
# content_inventory.py
import csv
from datetime import datetime
from pathlib import Path

class ContentInventory:
    def __init__(self):
        self.inventory = []

    def crawl_documentation(self, doc_root_path):
        """Create inventory from documentation files"""
        doc_path = Path(doc_root_path)

        for file in doc_path.rglob('*.md'):
            page_data = self.extract_page_metadata(file)
            self.inventory.append(page_data)

    def extract_page_metadata(self, file_path):
        """Extract metadata from documentation file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract frontmatter
        lines = content.split('\n')
        metadata = {
            'path': str(file_path),
            'filename': file_path.name,
            'section': self.extract_section(file_path),
            'title': self.extract_title(content),
            'word_count': len(content.split()),
            'has_code_examples': 'code' in content.lower() or '```' in content,
            'has_images': '![' in content,
            'headings_count': content.count('\n#'),
            'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime),
            'internal_links': self.count_internal_links(content),
            'external_links': self.count_external_links(content)
        }
        return metadata

    def extract_title(self, content):
        """Extract page title from first heading"""
        for line in content.split('\n'):
            if line.startswith('# '):
                return line.replace('# ', '').strip()
        return 'No Title'

    def extract_section(self, file_path):
        """Extract section from directory structure"""
        parts = file_path.parts
        return parts[-2] if len(parts) > 1 else 'Root'

    def count_internal_links(self, content):
        """Count internal documentation links"""
        return content.count('[](/')

    def count_external_links(self, content):
        """Count external links"""
        return content.count('http')

    def export_to_csv(self, output_file):
        """Export inventory to CSV for analysis"""
        if not self.inventory:
            return

        keys = self.inventory[0].keys()
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.inventory)

    def generate_summary_stats(self):
        """Generate summary statistics"""
        if not self.inventory:
            return None

        stats = {
            'total_pages': len(self.inventory),
            'total_words': sum(p['word_count'] for p in self.inventory),
            'avg_word_count': sum(p['word_count'] for p in self.inventory) / len(self.inventory),
            'pages_with_code': sum(1 for p in self.inventory if p['has_code_examples']),
            'pages_with_images': sum(1 for p in self.inventory if p['has_images']),
            'avg_last_update_days': self.avg_days_since_update(),
            'outdated_pages': self.identify_outdated_pages()
        }
        return stats

    def avg_days_since_update(self):
        """Calculate average days since last update"""
        today = datetime.now()
        total_days = 0
        for page in self.inventory:
            days = (today - page['last_modified']).days
            total_days += days
        return total_days // len(self.inventory) if self.inventory else 0

    def identify_outdated_pages(self):
        """Identify pages not updated in 6+ months"""
        today = datetime.now()
        outdated = []
        for page in self.inventory:
            days_old = (today - page['last_modified']).days
            if days_old > 180:
                outdated.append({
                    'path': page['path'],
                    'title': page['title'],
                    'days_since_update': days_old
                })
        return sorted(outdated, key=lambda x: x['days_since_update'], reverse=True)
```

## Part 3: Conduct Individual Page Reviews

### Audit Template

Create a standardized audit form:

```markdown
# Page Audit Form

**Page Title:** Getting Started with API

**URL:** /docs/getting-started

**Reviewer:** [Name]

**Review Date:** 2024-10-15

## Accuracy Assessment

- [ ] All information is current and correct
- [ ] Code examples run without errors
- [ ] API endpoints are functional
- [ ] Version numbers are accurate

**Issues Found:**
- Outdated authentication method in example
- Missing required parameter in code sample

**Accuracy Score:** 7/10

## Completeness Assessment

- [x] Topic is thoroughly covered
- [ ] Prerequisites are listed
- [x] Multiple approaches shown
- [ ] Related topics linked

**Issues Found:**
- Missing troubleshooting section
- Error handling not documented

**Completeness Score:** 6/10

## Clarity Assessment

- [x] Language is clear and concise
- [x] Examples are helpful
- [ ] Technical terms are explained
- [x] Structure is logical

**Issues Found:**
- One paragraph is too dense

**Clarity Score:** 8/10

## Relevance Assessment

- [x] Content aligns with current product
- [x] Information is frequently accessed
- [x] No deprecated features referenced
- [x] Recent updates integrated

**Relevance Score:** 9/10

## Engagement Assessment

- [ ] Has visual diagrams
- [x] Code examples present
- [ ] Interactive elements
- [x] Engaging tone

**Engagement Score:** 6/10

## SEO Assessment

- [x] Optimized title
- [x] Meta description
- [x] Keywords naturally included
- [x] Proper heading hierarchy

**SEO Score:** 9/10

## Overall Assessment

**Final Score:** 7.3/10

**Rating:** Good

**Recommended Actions:**
1. Update authentication code example
2. Add troubleshooting section
3. Include error handling best practices
4. Add visual diagram for workflow

**Priority:** Medium

**Estimated Update Time:** 3 hours

**Assigned To:** [Developer Advocate Name]

**Due Date:** 2024-10-31
```

## Part 4: Analyze and Prioritize Results

### Audit Analysis Script

```python
# audit_analyzer.py
import json
from collections import defaultdict
from datetime import datetime

class AuditAnalyzer:
    def __init__(self, audit_results):
        self.results = audit_results
        self.analysis = {}

    def categorize_by_status(self):
        """Categorize pages by update status"""
        categories = defaultdict(list)

        for page in self.results:
            score = page['overall_score']
            if score >= 80:
                status = 'Excellent - Maintain'
            elif score >= 60:
                status = 'Good - Minor Updates'
            elif score >= 40:
                status = 'Fair - Significant Update'
            else:
                status = 'Poor - Major Overhaul'

            categories[status].append(page)

        return categories

    def identify_quick_wins(self):
        """Find pages needing minor fixes"""
        quick_wins = []
        for page in self.results:
            if 60 <= page['overall_score'] < 80 and page['estimated_hours'] < 2:
                quick_wins.append(page)
        return sorted(quick_wins, key=lambda x: x['overall_score'], reverse=True)

    def identify_duplicates(self):
        """Find duplicate or overlapping content"""
        duplicates = defaultdict(list)
        titles = defaultdict(list)

        for page in self.results:
            title_base = page['title'].split('-')[0].strip()
            titles[title_base].append(page)

        for title, pages in titles.items():
            if len(pages) > 1:
                duplicates[title] = pages

        return duplicates

    def generate_priority_matrix(self):
        """Create priority matrix (impact vs effort)"""
        matrix = {
            'high_impact_low_effort': [],  # Do first
            'high_impact_high_effort': [],  # Plan carefully
            'low_impact_low_effort': [],   # Do quickly
            'low_impact_high_effort': []   # Deprioritize
        }

        for page in self.results:
            if page['estimated_hours'] > 4:
                effort = 'high'
            else:
                effort = 'low'

            if page['page_views_monthly'] > 100:
                impact = 'high'
            else:
                impact = 'low'

            key = f'{impact}_impact_{effort}_effort'
            matrix[key].append(page)

        return matrix

    def estimate_total_effort(self):
        """Calculate total effort required"""
        total_hours = sum(p['estimated_hours'] for p in self.results)
        hours_per_week = 40
        weeks_needed = total_hours / hours_per_week

        return {
            'total_hours': total_hours,
            'weeks_needed': weeks_needed,
            'person_months': weeks_needed / 4
        }

    def generate_report(self):
        """Generate comprehensive audit report"""
        report = {
            'audit_date': datetime.now().isoformat(),
            'total_pages_reviewed': len(self.results),
            'status_breakdown': self.categorize_by_status(),
            'average_score': sum(p['overall_score'] for p in self.results) / len(self.results),
            'quick_wins': self.identify_quick_wins(),
            'duplicates_found': self.identify_duplicates(),
            'priority_matrix': self.generate_priority_matrix(),
            'effort_estimate': self.estimate_total_effort(),
            'recommendations': self.generate_recommendations()
        }
        return report

    def generate_recommendations(self):
        """Generate actionable recommendations"""
        recommendations = []

        # Pages needing urgent updates
        poor_pages = [p for p in self.results if p['overall_score'] < 40]
        if poor_pages:
            recommendations.append({
                'title': 'Urgent: Update Poor Quality Pages',
                'pages': [p['title'] for p in poor_pages[:5]],
                'rationale': f'{len(poor_pages)} pages have quality scores below 40'
            })

        # Duplicate content consolidation
        duplicates = self.identify_duplicates()
        if duplicates:
            recommendations.append({
                'title': 'Consolidate Duplicate Content',
                'duplicates': list(duplicates.keys()),
                'potential_savings': f'{sum(len(v) for v in duplicates.values()) - len(duplicates)} pages could be removed'
            })

        # Outdated content
        outdated = [p for p in self.results if (datetime.now() - p['last_updated']).days > 180]
        if outdated:
            recommendations.append({
                'title': 'Update Outdated Content',
                'count': len(outdated),
                'oldest_update_days': max((datetime.now() - p['last_updated']).days for p in outdated)
            })

        return recommendations
```

## Part 5: Create Action Plan

### Audit Tracking Spreadsheet

```csv
Page Title,URL,Current Score,Status,Issue Category,Recommended Action,Priority,Assigned To,Due Date,Estimated Hours,Actual Hours
Getting Started,/docs/getting-started,73,Good,Outdated Examples,Update code examples,High,John Smith,2024-11-15,2,
API Reference,/docs/api/reference,85,Excellent,Minor,Add missing endpoints,Low,Jane Doe,2024-11-30,1,
Deployment Guide,/docs/deployment,45,Fair,Significant Update,Rewrite for v2 compatibility,High,Team Lead,2024-11-20,8,
FAQ,/docs/faq,92,Excellent,Maintain,Monitor quarterly,Low,Support,2024-12-31,0.5,
```

### Create Improvement Tracking

```python
# audit_tracking.py
import sqlite3
from datetime import datetime

class AuditTracking:
    def __init__(self, db_path='audit_tracking.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_tasks (
                id INTEGER PRIMARY KEY,
                page_title TEXT,
                url TEXT,
                assigned_to TEXT,
                due_date DATE,
                status TEXT,
                estimated_hours REAL,
                actual_hours REAL,
                created_date TIMESTAMP,
                completed_date TIMESTAMP,
                notes TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_progress (
                id INTEGER PRIMARY KEY,
                date TIMESTAMP,
                completed_count INTEGER,
                in_progress_count INTEGER,
                pending_count INTEGER,
                avg_score REAL
            )
        ''')

        conn.commit()
        conn.close()

    def add_task(self, page_title, url, assigned_to, due_date, estimated_hours):
        """Add tracking task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO audit_tasks
            (page_title, url, assigned_to, due_date, status, estimated_hours, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (page_title, url, assigned_to, due_date, 'pending', estimated_hours, datetime.now()))

        conn.commit()
        conn.close()

    def update_task_status(self, task_id, status, actual_hours=None):
        """Update task status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        completion_date = datetime.now() if status == 'completed' else None

        cursor.execute('''
            UPDATE audit_tasks
            SET status = ?, actual_hours = ?, completed_date = ?
            WHERE id = ?
        ''', (status, actual_hours, completion_date, task_id))

        conn.commit()
        conn.close()

    def get_progress_summary(self):
        """Get overall progress summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                COUNT(CASE WHEN status='completed' THEN 1 END) as completed,
                COUNT(CASE WHEN status='in_progress' THEN 1 END) as in_progress,
                COUNT(CASE WHEN status='pending' THEN 1 END) as pending,
                SUM(CASE WHEN status='completed' THEN actual_hours ELSE 0 END) as hours_spent
            FROM audit_tasks
        ''')

        result = cursor.fetchone()
        conn.close()

        return {
            'completed': result[0],
            'in_progress': result[1],
            'pending': result[2],
            'hours_spent': result[3]
        }
```

## Part 6: Execute Updates

### Content Update Workflow

1. **Preparation**: Pull latest version, create feature branch
2. **Review**: Re-read current version, understand issues
3. **Update**: Make necessary changes
4. **Testing**: Verify examples work, check links
5. **Review**: Get technical review if needed
6. **Merge**: Commit changes with detailed message

## Part 7: Document and Share Results

### Audit Report Template

```markdown
# Q4 2024 Documentation Audit Report

## Executive Summary

- **Total Pages Reviewed:** 127
- **Average Quality Score:** 72/100
- **Pages Requiring Update:** 34 (27%)
- **Estimated Effort:** 156 hours (4 weeks)

## Key Findings

### By Category
- Excellent (80-100): 45 pages (35%)
- Good (60-79): 48 pages (38%)
- Fair (40-59): 24 pages (19%)
- Poor (<40): 10 pages (8%)

### Common Issues
1. Outdated code examples (18 pages)
2. Missing troubleshooting sections (12 pages)
3. Broken links (8 pages)
4. Unclear explanations (7 pages)

## Action Items

### Immediate (Next 2 weeks)
- Fix broken links
- Update deprecated API references
- Add missing version compatibility notes

### Short-term (Next 4 weeks)
- Rewrite poor-scoring pages
- Consolidate duplicate content
- Add missing code examples

### Long-term (Next 3 months)
- Implement continuous monitoring
- Establish content review schedule
- Build automated audit tools

## Metrics and Monitoring

Going forward, track:
- Monthly page view trends
- User satisfaction scores
- Content decay over time
- Link health
```

## Part 8: Establish Continuous Audit Process

### Quarterly Audit Schedule

```
Q1: January-March
Q2: April-June
Q3: July-September
Q4: October-December

Ongoing activities:
- Monthly broken link checks
- Weekly new page reviews
- Daily user feedback monitoring
```

## Conclusion

Regular content audits are essential for maintaining high-quality documentation. Follow this structured quarterly process to ensure your documentation remains accurate, complete, and valuable to users.

## Resources

- [Content Audit Checklist](https://www.contentstrategyinstitute.com)
- [Documentation Best Practices](https://www.writethedocs.org)
- [SEO for Documentation](https://moz.com/beginners-guide-to-seo)


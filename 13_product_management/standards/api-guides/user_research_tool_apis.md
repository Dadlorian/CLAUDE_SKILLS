# User Research Tool APIs Integration Guide

## Overview

User research tools like Dovetail and UserTesting provide critical insights into customer needs, pain points, and behaviors. This guide covers API integration patterns for automating research data collection, analysis, and synthesis.

### Why User Research APIs Matter for PMs

Product Managers benefit from research tool integration to:
- Aggregate feedback from multiple research platforms
- Automate insight extraction and tagging
- Link research insights to product decisions
- Track research themes across users
- Generate reports and dashboards
- Integrate findings into roadmap planning
- Create searchable research databases

---

## Dovetail API Integration

### Authentication & Setup

Dovetail uses API tokens for authentication and supports OAuth 2.0.

```bash
# Environment configuration
DOVETAIL_API_KEY=your_api_key
DOVETAIL_WORKSPACE_ID=your_workspace_id
DOVETAIL_BASE_URL=https://api.dovetail.com
```

#### Dovetail SDK Installation

```bash
npm install @dovetail-research/api-client
# or
pip install dovetail-python
```

### API Client Implementation

```python
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class DovetailClient:
    def __init__(self, api_key: str, workspace_id: str):
        self.api_key = api_key
        self.workspace_id = workspace_id
        self.base_url = "https://api.dovetail.com/v1"
        self.headers = {
            'Authorization': f'Token {api_key}',
            'Content-Type': 'application/json'
        }

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> dict:
        """Make GET request"""
        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, data: dict) -> dict:
        """Make POST request"""
        response = requests.post(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()

    def _patch(self, endpoint: str, data: dict) -> dict:
        """Make PATCH request"""
        response = requests.patch(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()

    def get_insights(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Retrieve insights from Dovetail"""
        params = {
            'workspace_id': self.workspace_id,
            'limit': 100
        }

        if filters:
            params.update(filters)

        return self._get('/insights', params=params)['data']

    def create_insight(self, content: str, tags: List[str] = None,
                      metadata: Dict = None) -> str:
        """Create a new insight"""
        data = {
            'workspace_id': self.workspace_id,
            'content': content,
            'tags': tags or [],
            'metadata': metadata or {}
        }

        response = self._post('/insights', data)
        return response['data']['id']

    def search_insights(self, query: str, limit: int = 50) -> List[Dict]:
        """Search insights by query"""
        params = {
            'workspace_id': self.workspace_id,
            'query': query,
            'limit': limit
        }

        return self._get('/insights/search', params=params)['data']

    def get_projects(self) -> List[Dict]:
        """Get all research projects"""
        return self._get(f'/workspaces/{self.workspace_id}/projects')['data']

    def create_highlight(self, insight_id: str, text: str, tags: List[str] = None) -> str:
        """Create highlight within an insight"""
        data = {
            'insight_id': insight_id,
            'text': text,
            'tags': tags or []
        }

        response = self._post('/highlights', data)
        return response['data']['id']

    def get_research_themes(self, project_id: str) -> Dict:
        """Extract themes from project insights"""
        insights = self.search_insights(f"project:{project_id}")

        themes = {}

        for insight in insights:
            tags = insight.get('tags', [])

            for tag in tags:
                if tag not in themes:
                    themes[tag] = []

                themes[tag].append({
                    'insight': insight['content'],
                    'source': insight.get('source', 'Unknown'),
                    'date': insight.get('created_at')
                })

        return themes

    def get_user_profiles(self, project_id: str) -> List[Dict]:
        """Get user profiles from research project"""
        return self._get(
            f'/projects/{project_id}/users'
        )['data']
```

### Research Data Analysis

```python
class ResearchAnalyzer:
    def __init__(self, dovetail_client: DovetailClient):
        self.client = dovetail_client

    def analyze_user_pain_points(self, project_id: str) -> Dict:
        """Analyze and categorize user pain points"""
        insights = self.client.search_insights(f"project:{project_id} pain-point")

        pain_points = {
            'workflow': [],
            'performance': [],
            'usability': [],
            'integration': [],
            'cost': [],
            'other': []
        }

        for insight in insights:
            pain_point = {
                'description': insight['content'],
                'source': insight.get('source'),
                'date': insight.get('created_at'),
                'tags': insight.get('tags', [])
            }

            # Categorize pain point
            content_lower = insight['content'].lower()

            if any(word in content_lower for word in ['slow', 'lag', 'hang', 'freeze']):
                pain_points['performance'].append(pain_point)

            elif any(word in content_lower for word in ['confusing', 'unclear', 'hard', 'difficult']):
                pain_points['usability'].append(pain_point)

            elif any(word in content_lower for word in ['integrate', 'connect', 'sync', 'export']):
                pain_points['integration'].append(pain_point)

            elif any(word in content_lower for word in ['expensive', 'price', 'cost', 'afford']):
                pain_points['cost'].append(pain_point)

            elif any(word in content_lower for word in ['workflow', 'process', 'step', 'task']):
                pain_points['workflow'].append(pain_point)

            else:
                pain_points['other'].append(pain_point)

        return {
            'total_pain_points': len(insights),
            'by_category': pain_points,
            'top_themes': self._extract_top_themes(pain_points)
        }

    def analyze_feature_requests(self, project_id: str) -> Dict:
        """Analyze feature requests by frequency and impact"""
        insights = self.client.search_insights(f"project:{project_id} feature-request")

        feature_frequency = {}

        for insight in insights:
            content = insight['content']

            # Extract feature keywords
            feature = self._extract_feature_name(content)

            if feature:
                if feature not in feature_frequency:
                    feature_frequency[feature] = {
                        'count': 0,
                        'mentions': [],
                        'requesters': set()
                    }

                feature_frequency[feature]['count'] += 1
                feature_frequency[feature]['mentions'].append(content)

                source = insight.get('source', {})
                if isinstance(source, dict) and 'user_id' in source:
                    feature_frequency[feature]['requesters'].add(source['user_id'])

        # Sort by frequency
        sorted_features = sorted(
            feature_frequency.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )

        return {
            'total_feature_requests': len(insights),
            'unique_features': len(feature_frequency),
            'top_features': [
                {
                    'name': feature,
                    'request_count': data['count'],
                    'unique_requesters': len(data['requesters'])
                }
                for feature, data in sorted_features[:10]
            ]
        }

    def get_research_summary(self, project_id: str, weeks_back: int = 4) -> Dict:
        """Generate research summary for stakeholders"""
        since_date = (datetime.now() - timedelta(weeks=weeks_back)).isoformat()

        insights = self.client.search_insights(
            f"project:{project_id} created>{since_date}"
        )

        pain_points = self.analyze_user_pain_points(project_id)
        feature_requests = self.analyze_feature_requests(project_id)

        return {
            'summary': {
                'period': f'Last {weeks_back} weeks',
                'total_insights': len(insights),
                'total_pain_points': pain_points['total_pain_points'],
                'total_feature_requests': feature_requests['total_feature_requests']
            },
            'pain_points': pain_points,
            'feature_requests': feature_requests,
            'research_highlights': self._extract_highlights(insights)
        }

    @staticmethod
    def _extract_top_themes(categories: Dict) -> List[Dict]:
        """Extract top themes from all categories"""
        themes = []

        for category, items in categories.items():
            if items:
                count = len(items)
                themes.append({
                    'theme': category,
                    'frequency': count,
                    'percentage': (count / sum(len(v) for v in categories.values()) * 100)
                })

        return sorted(themes, key=lambda x: x['frequency'], reverse=True)

    @staticmethod
    def _extract_feature_name(text: str) -> Optional[str]:
        """Extract feature name from text"""
        import re

        # Look for "feature: feature-name" pattern
        match = re.search(r'(?:feature|need):\s*([^\.]+)', text, re.IGNORECASE)

        if match:
            return match.group(1).strip()

        return None

    @staticmethod
    def _extract_highlights(insights: List[Dict]) -> List[Dict]:
        """Extract notable quotes and insights"""
        highlights = []

        for insight in insights:
            if len(insight.get('content', '')) > 50:
                highlights.append({
                    'quote': insight['content'][:200] + '...',
                    'source': insight.get('source'),
                    'date': insight.get('created_at')
                })

        return highlights[:5]  # Return top 5
```

---

## UserTesting API Integration

### Authentication & Setup

```bash
# Environment configuration
USERTESTING_API_KEY=your_api_key
USERTESTING_API_BASE_URL=https://www.usertesting.com/api/v1
```

#### UserTesting Client

```python
import requests
from typing import List, Dict, Optional
import json

class UserTestingClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.usertesting.com/api/v1"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def _get(self, endpoint: str) -> dict:
        """Make GET request"""
        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, data: dict) -> dict:
        """Make POST request"""
        response = requests.post(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()

    def get_tests(self) -> List[Dict]:
        """Get all user tests"""
        return self._get('/tests')['results']

    def get_test_results(self, test_id: str) -> List[Dict]:
        """Get results for a specific test"""
        return self._get(f'/tests/{test_id}/results')['results']

    def get_test_result_video(self, result_id: str) -> Dict:
        """Get video and metadata for test result"""
        return self._get(f'/results/{result_id}')

    def get_result_transcript(self, result_id: str) -> str:
        """Get transcript of test result"""
        result = self.get_test_result_video(result_id)

        return result.get('transcript', '')

    def create_test(self, test_config: Dict) -> str:
        """Create a new user test"""
        data = {
            'title': test_config.get('title'),
            'description': test_config.get('description'),
            'questions': test_config.get('questions', []),
            'test_type': test_config.get('test_type', 'live'),
            'tester_count': test_config.get('tester_count', 5)
        }

        response = self._post('/tests', data)

        return response['id']

    def analyze_test_results(self, test_id: str) -> Dict:
        """Analyze results from completed test"""
        results = self.get_test_results(test_id)

        analysis = {
            'total_testers': len(results),
            'completion_rate': 0,
            'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
            'key_findings': [],
            'common_issues': [],
            'suggestions': []
        }

        for result in results:
            # Analyze each result
            if result.get('status') == 'completed':
                analysis['completion_rate'] += 1

        analysis['completion_rate'] = (analysis['completion_rate'] / len(results) * 100) if results else 0

        # Extract key findings from transcripts
        for result in results:
            transcript = self.get_result_transcript(result['id'])

            if transcript:
                findings = self._extract_findings(transcript)
                analysis['key_findings'].extend(findings)

        return analysis

    @staticmethod
    def _extract_findings(transcript: str) -> List[str]:
        """Extract key findings from transcript"""
        findings = []

        # Simple keyword matching for findings
        keywords = {
            'confused': 'Users found interface confusing',
            'difficult': 'Users found task difficult',
            'missing': 'Users identified missing features',
            'slow': 'Users experienced performance issues',
            'unclear': 'Users found instructions unclear'
        }

        for keyword, finding in keywords.items():
            if keyword.lower() in transcript.lower():
                findings.append(finding)

        return list(set(findings))  # Remove duplicates
```

### Research Insight Extraction

```python
class UserTestingAnalyzer:
    def __init__(self, usertesting_client: UserTestingClient):
        self.client = usertesting_client

    def generate_research_report(self, test_id: str) -> Dict:
        """Generate comprehensive research report"""
        test_data = self.client.get_test_results(test_id)

        report = {
            'test_id': test_id,
            'total_participants': len(test_data),
            'sections': {
                'overview': self._analyze_overview(test_data),
                'user_behavior': self._analyze_user_behavior(test_data),
                'pain_points': self._extract_pain_points(test_data),
                'feature_suggestions': self._extract_suggestions(test_data),
                'sentiment': self._analyze_sentiment(test_data)
            },
            'recommendations': self._generate_recommendations(test_data)
        }

        return report

    @staticmethod
    def _analyze_overview(results: List[Dict]) -> Dict:
        """Analyze test overview"""
        completed = len([r for r in results if r.get('status') == 'completed'])

        return {
            'total_results': len(results),
            'completed': completed,
            'completion_rate': (completed / len(results) * 100) if results else 0,
            'average_duration_minutes': 0  # Calculate from results
        }

    @staticmethod
    def _analyze_user_behavior(results: List[Dict]) -> Dict:
        """Analyze user behavior patterns"""
        return {
            'navigation_patterns': [],
            'feature_discovery': [],
            'task_completion_paths': []
        }

    @staticmethod
    def _extract_pain_points(results: List[Dict]) -> List[Dict]:
        """Extract pain points from results"""
        pain_points = []

        for result in results:
            transcript = result.get('transcript', '')

            # Keyword-based extraction
            issues = []

            if 'not sure' in transcript.lower():
                issues.append('Uncertainty about functionality')

            if 'where' in transcript.lower() or 'find' in transcript.lower():
                issues.append('Difficulty finding features')

            if 'confuse' in transcript.lower():
                issues.append('Confusion about interface')

            pain_points.extend(issues)

        return list(set(pain_points))

    @staticmethod
    def _extract_suggestions(results: List[Dict]) -> List[Dict]:
        """Extract feature suggestions from results"""
        suggestions = []

        for result in results:
            transcript = result.get('transcript', '')

            if 'should' in transcript.lower() or 'could' in transcript.lower():
                # Extract suggestion context
                suggestions.append({
                    'user_id': result['id'],
                    'suggestion': transcript,
                    'priority': 'medium'
                })

        return suggestions

    @staticmethod
    def _analyze_sentiment(results: List[Dict]) -> Dict:
        """Analyze sentiment from results"""
        sentiments = {'positive': 0, 'neutral': 0, 'negative': 0}

        for result in results:
            # Simple sentiment scoring (can be improved with NLP)
            rating = result.get('rating', 0)

            if rating >= 4:
                sentiments['positive'] += 1

            elif rating == 3:
                sentiments['neutral'] += 1

            else:
                sentiments['negative'] += 1

        total = len(results)

        return {
            'distribution': sentiments,
            'percentages': {
                'positive': (sentiments['positive'] / total * 100) if total else 0,
                'neutral': (sentiments['neutral'] / total * 100) if total else 0,
                'negative': (sentiments['negative'] / total * 100) if total else 0
            }
        }

    @staticmethod
    def _generate_recommendations(results: List[Dict]) -> List[str]:
        """Generate recommendations based on findings"""
        recommendations = []

        # Analyze pain points and generate recommendations
        pain_points = UserTestingAnalyzer._extract_pain_points(results)

        if 'Difficulty finding features' in pain_points:
            recommendations.append('Improve information architecture and navigation labels')

        if 'Confusion about interface' in pain_points:
            recommendations.append('Redesign interface for clarity and add contextual help')

        if 'Uncertainty about functionality' in pain_points:
            recommendations.append('Add tooltips and onboarding guidance')

        return recommendations
```

---

## Research Data Aggregation

### Unified Research Platform

```python
class UnifiedResearchPlatform:
    def __init__(self, dovetail_client: DovetailClient, usertesting_client: UserTestingClient):
        self.dovetail = dovetail_client
        self.usertesting = usertesting_client

    def aggregate_research_findings(self, time_period_days: int = 30) -> Dict:
        """Aggregate findings from all research sources"""
        return {
            'period_days': time_period_days,
            'dovetail_insights': self._aggregate_dovetail_data(),
            'usertesting_insights': self._aggregate_usertesting_data(),
            'consolidated_themes': self._consolidate_themes(),
            'top_recommendations': self._rank_recommendations()
        }

    def _aggregate_dovetail_data(self) -> Dict:
        """Aggregate Dovetail insights"""
        # Query all Dovetail insights
        insights = self.dovetail.get_insights()

        return {
            'total_insights': len(insights),
            'sources': len(set(i.get('source') for i in insights)),
            'primary_themes': self._extract_themes(insights)
        }

    def _aggregate_usertesting_data(self) -> Dict:
        """Aggregate UserTesting results"""
        tests = self.usertesting.get_tests()

        return {
            'total_tests': len(tests),
            'total_participants': sum(t.get('participant_count', 0) for t in tests),
            'completion_rate': self._calculate_avg_completion_rate(tests)
        }

    def _consolidate_themes(self) -> Dict:
        """Consolidate themes from both platforms"""
        return {
            'usability': [],
            'performance': [],
            'features': [],
            'integration': []
        }

    def _rank_recommendations(self) -> List[Dict]:
        """Rank recommendations by impact and frequency"""
        return []

    @staticmethod
    def _extract_themes(insights: List[Dict]) -> Dict:
        """Extract themes from insights"""
        themes = {}

        for insight in insights:
            tags = insight.get('tags', [])

            for tag in tags:
                if tag not in themes:
                    themes[tag] = 0

                themes[tag] += 1

        return sorted(themes.items(), key=lambda x: x[1], reverse=True)

    @staticmethod
    def _calculate_avg_completion_rate(tests: List[Dict]) -> float:
        """Calculate average completion rate across tests"""
        if not tests:
            return 0

        total_rate = sum(t.get('completion_rate', 0) for t in tests)

        return total_rate / len(tests)
```

### Research Dashboard Export

```python
class ResearchDashboardExporter:
    def __init__(self, research_platform: UnifiedResearchPlatform):
        self.platform = research_platform

    def generate_dashboard_data(self) -> Dict:
        """Generate data for research dashboard"""
        aggregated = self.platform.aggregate_research_findings()

        return {
            'timestamp': datetime.now().isoformat(),
            'overview': {
                'total_research_activities': self._calculate_total_activities(aggregated),
                'participant_count': aggregated['usertesting_insights']['total_participants'],
                'insight_count': aggregated['dovetail_insights']['total_insights']
            },
            'key_findings': self._compile_key_findings(aggregated),
            'recommendations': aggregated.get('top_recommendations', []),
            'trends': self._identify_trends(aggregated)
        }

    @staticmethod
    def _calculate_total_activities(data: Dict) -> int:
        """Calculate total research activities"""
        return (
            data['dovetail_insights']['total_insights'] +
            data['usertesting_insights']['total_tests']
        )

    @staticmethod
    def _compile_key_findings(data: Dict) -> List[str]:
        """Compile key findings from all sources"""
        findings = []

        # Add top Dovetail themes
        themes = data['dovetail_insights']['primary_themes']
        for theme, count in themes[:3]:
            findings.append(f"{theme.title()}: mentioned {count} times")

        return findings

    @staticmethod
    def _identify_trends(data: Dict) -> Dict:
        """Identify trends in research data"""
        return {
            'emerging_themes': [],
            'declining_concerns': [],
            'persistent_issues': []
        }

    def export_to_json(self, filepath: str):
        """Export dashboard data to JSON"""
        data = self.generate_dashboard_data()

        import json

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def export_to_markdown(self, filepath: str):
        """Export dashboard data to Markdown"""
        data = self.generate_dashboard_data()

        content = f"""# Research Dashboard Report
Generated: {data['timestamp']}

## Overview
- Total Research Activities: {data['overview']['total_research_activities']}
- Participants: {data['overview']['participant_count']}
- Insights Collected: {data['overview']['insight_count']}

## Key Findings
"""

        for finding in data['key_findings']:
            content += f"- {finding}\n"

        content += "\n## Top Recommendations\n"

        for rec in data['recommendations']:
            content += f"- {rec}\n"

        with open(filepath, 'w') as f:
            f.write(content)
```

---

## Integration Testing

### Mock Research Data

```python
import pytest
from unittest.mock import Mock, patch

class TestResearchIntegration:
    @pytest.fixture
    def mock_dovetail_client(self):
        client = Mock()
        client.get_insights.return_value = [
            {
                'id': '1',
                'content': 'Users found the navigation confusing',
                'tags': ['usability', 'navigation'],
                'source': 'user-interview'
            }
        ]
        return client

    def test_analyze_pain_points(self, mock_dovetail_client):
        analyzer = ResearchAnalyzer(mock_dovetail_client)

        results = analyzer.analyze_user_pain_points('project_123')

        assert results['total_pain_points'] == 1
        assert 'usability' in results['by_category']

    def test_feature_request_extraction(self, mock_dovetail_client):
        analyzer = ResearchAnalyzer(mock_dovetail_client)

        mock_dovetail_client.search_insights.return_value = [
            {
                'content': 'Feature: dark mode would be great',
                'tags': ['feature-request']
            }
        ]

        results = analyzer.analyze_feature_requests('project_123')

        assert results['total_feature_requests'] == 1
```

---

## Conclusion

User research tool APIs enable product managers to systematically collect, analyze, and act on user insights. By integrating Dovetail and UserTesting APIs with proper data aggregation and analysis patterns, PMs can create a comprehensive research infrastructure that informs product decisions.

Key takeaways:
- Use Dovetail for qualitative insight management and synthesis
- Leverage UserTesting for structured user feedback collection
- Aggregate insights from multiple research sources
- Implement systematic analysis patterns for recurring themes
- Export research findings in multiple formats for different stakeholders
- Maintain data quality and consistency across platforms
- Use research insights to validate product hypotheses
- Document research methodology and findings for team alignment

# Collaboration Tool APIs for Product Workflows

## Overview

Slack, Microsoft Teams, and Jira are central to product team collaboration. This guide covers API integration patterns for automating notifications, tracking feature development, and coordinating cross-functional product work.

### Why Collaboration APIs Matter for PMs

Product Managers benefit from collaboration integrations to:
- Automate feature request routing to development teams
- Push product updates and announcements to stakeholders
- Sync roadmap items with development tracking
- Monitor team velocity and sprint progress
- Automate customer feedback aggregation
- Create audit trails for product decisions
- Coordinate communication across distributed teams

---

## Slack API Integration

### Authentication & Setup

Slack uses OAuth 2.0 with various scopes for different functionalities.

```bash
# Environment configuration
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_APP_ID=your-app-id
```

#### Installing Slack SDK

```bash
npm install @slack/web-api @slack/bolt

# Or for Python
pip install slack-sdk slack-bolt
```

### Event Subscriptions and Webhooks

```python
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
import re

# Initialize Slack app
slack_app = App(
    token=os.getenv('SLACK_BOT_TOKEN'),
    signing_secret=os.getenv('SLACK_SIGNING_SECRET')
)

flask_app = Flask(__name__)
handler = SlackRequestHandler(slack_app)

class ProductFeedbackBot:
    def __init__(self, slack_app: App):
        self.app = slack_app
        self._register_handlers()

    def _register_handlers(self):
        """Register Slack event handlers"""
        # Listen for message reactions (e.g., thumbsup for feature votes)
        self.app.event('reaction_added')(self._handle_reaction_added)

        # Listen for slash commands
        self.app.command('/feature-request')(self._handle_feature_request)
        self.app.command('/roadmap')(self._handle_roadmap_query)

        # Listen for app mentions
        self.app.event('app_mention')(self._handle_app_mention)

    def _handle_reaction_added(self, event: dict, say, client):
        """Handle when someone reacts to a message"""
        reaction = event['reaction']

        # Track feature votes
        if reaction == 'thumbsup':
            message = client.conversations_history(
                channel=event['item']['channel'],
                latest=event['item']['ts'],
                limit=1
            )

            if message['messages']:
                msg_text = message['messages'][0]['text']
                self._log_feature_vote(msg_text, event['user'])

    def _handle_feature_request(self, ack, body, respond):
        """Handle /feature-request slash command"""
        ack()

        feature_text = body['text']
        user_id = body['user_id']

        # Validate and store feature request
        if not feature_text:
            respond("Please provide a feature description: `/feature-request <description>`")
            return

        feature_id = self._create_feature_request(feature_text, user_id)

        respond(f"Feature request created! ID: {feature_id}\nI'll route this to the product team.")

        # Notify product channel
        self._notify_product_channel(feature_id, feature_text, user_id)

    def _handle_roadmap_query(self, ack, body, respond):
        """Handle /roadmap slash command"""
        ack()

        period = body['text'] or 'current'

        roadmap_items = self._get_roadmap_items(period)

        blocks = self._format_roadmap_blocks(roadmap_items)

        respond(blocks=blocks)

    def _handle_app_mention(self, event: dict, say):
        """Handle when bot is mentioned"""
        text = event['text']

        # Parse natural language queries
        if 'feature status' in text.lower():
            feature_name = self._extract_feature_name(text)
            status = self._get_feature_status(feature_name)
            say(f"Status for {feature_name}: {status}")

        elif 'roadmap' in text.lower():
            say("Here's the current roadmap...")

    @staticmethod
    def _create_feature_request(feature_text: str, user_id: str) -> str:
        """Create feature request in database"""
        # Implementation
        return 'feature_123'

    @staticmethod
    def _notify_product_channel(feature_id: str, feature_text: str, user_id: str):
        """Notify product team of new feature request"""
        # Implementation
        pass

    @staticmethod
    def _get_roadmap_items(period: str) -> list:
        """Retrieve roadmap items for period"""
        # Implementation
        return []

    @staticmethod
    def _format_roadmap_blocks(items: list) -> list:
        """Format roadmap items as Slack blocks"""
        blocks = []

        for item in items:
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"*{item['name']}*\n{item['description']}\n_Due: {item['due_date']}_"
                },
                'accessory': {
                    'type': 'button',
                    'text': {
                        'type': 'plain_text',
                        'text': 'View Details'
                    },
                    'value': item['id']
                }
            })

        return blocks

    @staticmethod
    def _extract_feature_name(text: str) -> str:
        """Extract feature name from natural language"""
        # Simple extraction - can be improved with NLP
        pattern = r'feature status (?:for |of )(\w+)'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else None

    @staticmethod
    def _get_feature_status(feature_name: str) -> str:
        """Get status of a feature"""
        # Implementation
        return 'In Progress'

# Flask route for handling Slack requests
@flask_app.route('/slack/events', methods=['POST'])
def slack_events():
    return handler.handle(request)

@flask_app.route('/slack/interactivity', methods=['POST'])
def slack_interactivity():
    return handler.handle(request)
```

### Sending Messages and Notifications

```python
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime

class SlackProductNotifier:
    def __init__(self, token: str):
        self.client = WebClient(token=token)

    def send_message(self, channel: str, text: str, blocks: list = None) -> str:
        """Send message to Slack channel"""
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            return response['ts']
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")
            raise

    def send_product_update(self, channel: str, update: dict):
        """Send formatted product update"""
        blocks = [
            {
                'type': 'header',
                'text': {
                    'type': 'plain_text',
                    'text': f"📦 {update['title']}",
                    'emoji': True
                }
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': update['description']
                }
            },
            {
                'type': 'section',
                'fields': [
                    {
                        'type': 'mrkdwn',
                        'text': f"*Status:*\n{update['status']}"
                    },
                    {
                        'type': 'mrkdwn',
                        'text': f"*Release Date:*\n{update['release_date']}"
                    }
                ]
            },
            {
                'type': 'actions',
                'elements': [
                    {
                        'type': 'button',
                        'text': {
                            'type': 'plain_text',
                            'text': 'View Details'
                        },
                        'url': update['url']
                    }
                ]
            }
        ]

        self.send_message(channel, update['title'], blocks=blocks)

    def send_feature_feedback_summary(self, channel: str, feedback_summary: dict):
        """Send customer feedback summary"""
        blocks = [
            {
                'type': 'header',
                'text': {
                    'type': 'plain_text',
                    'text': '💬 Customer Feedback Summary',
                    'emoji': True
                }
            }
        ]

        # Add feedback by theme
        for theme, items in feedback_summary.items():
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"*{theme}* ({len(items)} mentions)\n" +
                            "\n".join([f"• {item['text']}" for item in items[:3]])
                }
            })

        self.send_message(channel, 'Customer Feedback Summary', blocks=blocks)

    def send_sprint_update(self, channel: str, sprint_data: dict):
        """Send sprint progress update"""
        blocks = [
            {
                'type': 'header',
                'text': {
                    'type': 'plain_text',
                    'text': f"🎯 Sprint {sprint_data['number']} Update",
                    'emoji': True
                }
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"*Velocity:* {sprint_data['velocity']} points\n" +
                            f"*Burndown:* {sprint_data['burndown_percentage']}% complete\n" +
                            f"*On Track:* {'✅ Yes' if sprint_data['on_track'] else '⚠️ At Risk'}"
                }
            }
        ]

        self.send_message(channel, f"Sprint {sprint_data['number']} Update", blocks=blocks)

    def notify_stakeholders(self, user_ids: list, message: str, details: dict = None):
        """Send direct message to multiple users"""
        for user_id in user_ids:
            blocks = []

            if details:
                blocks = self._format_details_blocks(details)

            self.send_message(user_id, message, blocks=blocks)

    @staticmethod
    def _format_details_blocks(details: dict) -> list:
        blocks = []

        for key, value in details.items():
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"*{key}:* {value}"
                }
            })

        return blocks
```

---

## Microsoft Teams Integration

### Teams API Authentication

```bash
# Environment setup
TEAMS_APP_ID=your-app-id
TEAMS_APP_PASSWORD=your-app-password
TEAMS_BOT_NAME=ProductBot
```

#### Teams Bot Framework Setup

```python
from botbuilder.core import MessageFactory
from botbuilder.schema import CardImage, CardAction, ActionTypes
from botbuilder.core.adapter import BotFrameworkAdapter
from botbuilder.schema import Attachment, HeroCard
import aiohttp
import json

class ProductTeamsBot:
    def __init__(self, app_id: str, app_password: str):
        self.app_id = app_id
        self.app_password = app_password
        self.adapter = BotFrameworkAdapter(app_id, app_password)

    async def handle_message(self, turn_context):
        """Handle incoming Teams messages"""
        text = turn_context.activity.text

        if text.startswith('/feature'):
            await self._handle_feature_command(turn_context)

        elif text.startswith('/roadmap'):
            await self._handle_roadmap_command(turn_context)

        elif text.startswith('/sprint'):
            await self._handle_sprint_command(turn_context)

        else:
            await self._handle_general_query(turn_context, text)

    async def _handle_feature_command(self, turn_context):
        """Handle /feature slash command"""
        feature_text = turn_context.activity.text.replace('/feature ', '')

        feature_id = self._create_feature_request(feature_text)

        card = HeroCard(
            title='Feature Request Created',
            text=f'Feature ID: {feature_id}',
            buttons=[
                CardAction(
                    type=ActionTypes.open_url,
                    title='View in Jira',
                    value=f'https://jira.company.com/browse/{feature_id}'
                )
            ]
        )

        message = MessageFactory.attachment(CardFactory.hero_card(card))
        await turn_context.send_activity(message)

    async def _handle_roadmap_command(self, turn_context):
        """Handle /roadmap slash command"""
        roadmap_items = self._get_roadmap()

        card = self._build_roadmap_card(roadmap_items)

        message = MessageFactory.attachment(CardFactory.adaptive_card(card))
        await turn_context.send_activity(message)

    async def _handle_sprint_command(self, turn_context):
        """Handle /sprint slash command"""
        sprint_data = self._get_sprint_data()

        card = self._build_sprint_card(sprint_data)

        message = MessageFactory.attachment(CardFactory.adaptive_card(card))
        await turn_context.send_activity(message)

    async def _handle_general_query(self, turn_context, query: str):
        """Handle general product questions"""
        response = self._process_query(query)

        await turn_context.send_activity(MessageFactory.text(response))

    @staticmethod
    def _build_roadmap_card(items: list) -> dict:
        """Build roadmap adaptive card"""
        return {
            '$schema': 'http://adaptivecards.io/schemas/adaptive-card.json',
            'type': 'AdaptiveCard',
            'version': '1.4',
            'body': [
                {
                    'type': 'TextBlock',
                    'text': 'Product Roadmap',
                    'weight': 'bolder',
                    'size': 'large'
                },
                *[
                    {
                        'type': 'Container',
                        'items': [
                            {
                                'type': 'TextBlock',
                                'text': item['name'],
                                'weight': 'bolder'
                            },
                            {
                                'type': 'TextBlock',
                                'text': item['description'],
                                'isSubtle': True,
                                'wrap': True
                            },
                            {
                                'type': 'TextBlock',
                                'text': f"Due: {item['due_date']}",
                                'isSubtle': True,
                                'size': 'small'
                            }
                        ]
                    }
                    for item in items
                ]
            ]
        }

    @staticmethod
    def _build_sprint_card(sprint_data: dict) -> dict:
        """Build sprint progress adaptive card"""
        return {
            '$schema': 'http://adaptivecards.io/schemas/adaptive-card.json',
            'type': 'AdaptiveCard',
            'version': '1.4',
            'body': [
                {
                    'type': 'TextBlock',
                    'text': f"Sprint {sprint_data['number']}",
                    'weight': 'bolder',
                    'size': 'large'
                },
                {
                    'type': 'ProgressIndicator',
                    'title': 'Completion',
                    'value': sprint_data['completion_percentage'],
                    'state': 'Success' if sprint_data['on_track'] else 'Warning'
                },
                {
                    'type': 'FactSet',
                    'facts': [
                        {
                            'name': 'Velocity:',
                            'value': f"{sprint_data['velocity']} points"
                        },
                        {
                            'name': 'Active Issues:',
                            'value': str(sprint_data['active_issues'])
                        }
                    ]
                }
            ]
        }
```

### Sending Teams Messages via Webhooks

```python
import requests
import json
from typing import List, Dict

class TeamsNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_card(self, title: str, sections: List[Dict], actions: List[Dict] = None) -> bool:
        """Send message card to Teams"""
        payload = {
            '@type': 'MessageCard',
            '@context': 'https://schema.org/extensions',
            'summary': title,
            'themeColor': '0078D7',
            'title': title,
            'sections': sections,
            'potentialAction': actions or []
        }

        response = requests.post(self.webhook_url, json=payload)
        return response.status_code == 200

    def send_feature_announcement(self, feature: Dict):
        """Announce new feature"""
        sections = [
            {
                'text': feature.get('description', '')
            },
            {
                'activityTitle': 'Feature Details',
                'facts': [
                    {'name': 'Status:', 'value': feature.get('status', 'In Planning')},
                    {'name': 'Release Date:', 'value': feature.get('release_date', 'TBD')},
                    {'name': 'Target Users:', 'value': feature.get('target_users', 'All')}
                ]
            }
        ]

        actions = [
            {
                '@type': 'OpenUri',
                'name': 'View Details',
                'targets': [
                    {'os': 'default', 'uri': feature.get('url', '')}
                ]
            }
        ]

        return self.send_card(f"📦 {feature.get('name', 'New Feature')}", sections, actions)

    def send_feedback_summary(self, feedback_summary: Dict):
        """Send customer feedback summary"""
        sections = [
            {
                'activityTitle': 'Top Themes',
                'activitySubtitle': f"{feedback_summary.get('total_feedback', 0)} feedback items analyzed"
            }
        ]

        for theme, count in feedback_summary.get('themes', {}).items():
            sections.append({
                'activityTitle': theme,
                'text': f"{count} mentions"
            })

        return self.send_card('💬 Customer Feedback Summary', sections)
```

---

## Jira API Integration

### Authentication & API Calls

```bash
# Environment setup
JIRA_BASE_URL=https://your-instance.atlassian.net
JIRA_API_TOKEN=your-api-token
JIRA_USER_EMAIL=your-email@company.com
```

#### Jira API Client

```python
import requests
from requests.auth import HTTPBasicAuth
from typing import List, Dict, Optional
import json

class JiraClient:
    def __init__(self, base_url: str, user_email: str, api_token: str):
        self.base_url = base_url
        self.auth = HTTPBasicAuth(user_email, api_token)
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    def create_issue(self, project_key: str, issue_type: str, summary: str,
                    description: str, fields: Dict = None) -> str:
        """Create a new Jira issue"""
        issue_data = {
            'fields': {
                'project': {'key': project_key},
                'issuetype': {'name': issue_type},
                'summary': summary,
                'description': description
            }
        }

        # Add custom fields
        if fields:
            issue_data['fields'].update(fields)

        response = requests.post(
            f"{self.base_url}/rest/api/3/issues",
            json=issue_data,
            auth=self.auth,
            headers=self.headers
        )

        if response.status_code == 201:
            return response.json()['key']
        else:
            raise Exception(f"Failed to create issue: {response.text}")

    def search_issues(self, jql: str, max_results: int = 50) -> List[Dict]:
        """Search for issues using JQL"""
        params = {
            'jql': jql,
            'maxResults': max_results,
            'fields': ['summary', 'status', 'assignee', 'created', 'updated']
        }

        response = requests.get(
            f"{self.base_url}/rest/api/3/search",
            params=params,
            auth=self.auth,
            headers=self.headers
        )

        if response.status_code == 200:
            return response.json()['issues']
        else:
            raise Exception(f"Search failed: {response.text}")

    def update_issue(self, issue_key: str, fields: Dict) -> bool:
        """Update an existing issue"""
        data = {'fields': fields}

        response = requests.put(
            f"{self.base_url}/rest/api/3/issues/{issue_key}",
            json=data,
            auth=self.auth,
            headers=self.headers
        )

        return response.status_code == 204

    def get_issue(self, issue_key: str) -> Dict:
        """Get issue details"""
        response = requests.get(
            f"{self.base_url}/rest/api/3/issues/{issue_key}",
            auth=self.auth,
            headers=self.headers
        )

        return response.json()

    def add_comment(self, issue_key: str, comment_text: str) -> str:
        """Add comment to issue"""
        data = {
            'body': {
                'version': 1,
                'type': 'doc',
                'content': [
                    {
                        'type': 'paragraph',
                        'content': [
                            {
                                'type': 'text',
                                'text': comment_text
                            }
                        ]
                    }
                ]
            }
        }

        response = requests.post(
            f"{self.base_url}/rest/api/3/issues/{issue_key}/comments",
            json=data,
            auth=self.auth,
            headers=self.headers
        )

        return response.json()['id']

    def link_issues(self, inward_key: str, outward_key: str, link_type: str = 'relates to'):
        """Link two issues"""
        data = {
            'type': {'name': link_type},
            'inwardIssue': {'key': inward_key},
            'outwardIssue': {'key': outward_key}
        }

        response = requests.post(
            f"{self.base_url}/rest/api/3/issueLink",
            json=data,
            auth=self.auth,
            headers=self.headers
        )

        return response.status_code == 201
```

### Product-Centric Jira Workflows

```python
class ProductJiraWorkflows:
    def __init__(self, jira_client: JiraClient):
        self.jira = jira_client

    def create_feature_from_feedback(self, feedback: Dict) -> str:
        """Create feature request issue from customer feedback"""
        return self.jira.create_issue(
            project_key='PROD',
            issue_type='Story',
            summary=f"Feature Request: {feedback['title']}",
            description=f"Customer feedback:\n\n{feedback['description']}\n\nSource: {feedback['source']}",
            fields={
                'customfield_10000': feedback.get('priority', 'Medium'),
                'customfield_10001': feedback.get('customer_name'),
                'customfield_10002': feedback.get('customer_email')
            }
        )

    def track_roadmap_in_jira(self, roadmap_items: List[Dict]) -> List[str]:
        """Create Jira epics from roadmap items"""
        epic_keys = []

        for item in roadmap_items:
            epic_key = self.jira.create_issue(
                project_key='PROD',
                issue_type='Epic',
                summary=item['name'],
                description=item.get('description', ''),
                fields={
                    'customfield_10010': item.get('due_date'),
                    'customfield_10011': item.get('target_audience'),
                    'customfield_10012': item.get('business_impact')
                }
            )

            epic_keys.append(epic_key)

        return epic_keys

    def get_sprint_capacity(self, sprint_id: int) -> Dict:
        """Get sprint capacity and utilization"""
        jql = f'sprint = {sprint_id} AND type in (Story, Task) AND status != Done'

        issues = self.jira.search_issues(jql)

        total_points = 0
        completed_points = 0

        for issue in issues:
            story_points = issue['fields'].get('customfield_10005', 0)  # Story points field
            total_points += story_points

            if issue['fields']['status']['name'] == 'Done':
                completed_points += story_points

        return {
            'total_capacity': total_points,
            'completed': completed_points,
            'remaining': total_points - completed_points,
            'utilization_percentage': (completed_points / total_points * 100) if total_points > 0 else 0
        }

    def create_release_notes(self, sprint_id: int) -> str:
        """Generate release notes from completed issues"""
        jql = f'sprint = {sprint_id} AND status = Done AND type in (Story, Bug)'

        issues = self.jira.search_issues(jql)

        release_notes = f"# Release Notes - Sprint {sprint_id}\n\n"

        stories = [i for i in issues if i['fields']['issuetype']['name'] == 'Story']
        bugs = [i for i in issues if i['fields']['issuetype']['name'] == 'Bug']

        if stories:
            release_notes += "## New Features\n"
            for issue in stories:
                release_notes += f"- {issue['fields']['summary']}\n"

        if bugs:
            release_notes += "\n## Bug Fixes\n"
            for issue in bugs:
                release_notes += f"- {issue['fields']['summary']}\n"

        return release_notes
```

### Jira Webhook Handling

```python
from flask import Flask, request
import hmac
import hashlib
import json

app = Flask(__name__)

class JiraWebhookHandler:
    def __init__(self, webhook_secret: str):
        self.webhook_secret = webhook_secret

    def verify_signature(self, request_body: str, request_hash: str) -> bool:
        """Verify Jira webhook signature"""
        expected_hash = hashlib.sha256(
            request_body.encode() + self.webhook_secret.encode()
        ).hexdigest()

        return hmac.compare_digest(expected_hash, request_hash)

    def handle_issue_created(self, issue_data: Dict):
        """Handle issue creation webhook"""
        issue_type = issue_data['fields']['issuetype']['name']

        if issue_type == 'Feature Request':
            # Notify product team
            self._notify_product_team(issue_data)

    def handle_issue_updated(self, issue_data: Dict):
        """Handle issue update webhook"""
        status = issue_data['fields']['status']['name']

        if status == 'In Development':
            # Notify stakeholders
            self._notify_stakeholders(issue_data)

    @staticmethod
    def _notify_product_team(issue_data: Dict):
        """Send notification to product team"""
        # Implementation
        pass

    @staticmethod
    def _notify_stakeholders(issue_data: Dict):
        """Send notification to stakeholders"""
        # Implementation
        pass

@app.route('/webhooks/jira', methods=['POST'])
def jira_webhook():
    handler = JiraWebhookHandler(os.getenv('JIRA_WEBHOOK_SECRET'))

    # Verify signature
    if not handler.verify_signature(
        request.get_data(as_text=True),
        request.headers.get('X-Atlassian-Webhook-Signature')
    ):
        return {'error': 'Invalid signature'}, 401

    payload = request.json

    # Route to appropriate handler
    event_type = payload['webhookEvent']

    if event_type == 'jira:issue_created':
        handler.handle_issue_created(payload['issue'])

    elif event_type == 'jira:issue_updated':
        handler.handle_issue_updated(payload['issue'])

    return {'status': 'ok'}, 200
```

---

## Cross-Platform Coordination

### Unified Notification System

```python
class CollaborationNotifier:
    def __init__(self, slack_notifier, teams_notifier, jira_client):
        self.slack = slack_notifier
        self.teams = teams_notifier
        self.jira = jira_client

    def notify_feature_request(self, feature_request: Dict, channels: Dict):
        """Notify all platforms of new feature request"""
        # Create Jira issue
        jira_key = self.jira.create_issue(
            project_key='PROD',
            issue_type='Story',
            summary=feature_request['title'],
            description=feature_request['description']
        )

        feature_request['jira_key'] = jira_key

        # Notify Slack
        if 'slack' in channels:
            self.slack.send_message(
                channels['slack'],
                f"New feature request: {feature_request['title']}",
                blocks=self._build_feature_blocks(feature_request)
            )

        # Notify Teams
        if 'teams' in channels:
            self.teams.send_card(
                f"📋 {feature_request['title']}",
                sections=self._build_feature_sections(feature_request)
            )

    @staticmethod
    def _build_feature_blocks(feature: Dict) -> list:
        """Build Slack blocks for feature"""
        return [
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"*{feature['title']}*\n{feature['description']}"
                }
            },
            {
                'type': 'section',
                'fields': [
                    {
                        'type': 'mrkdwn',
                        'text': f"*Jira:*\n{feature['jira_key']}"
                    }
                ]
            }
        ]

    @staticmethod
    def _build_feature_sections(feature: Dict) -> list:
        """Build Teams sections for feature"""
        return [
            {
                'text': feature['description']
            },
            {
                'activityTitle': 'Details',
                'facts': [
                    {'name': 'Jira:', 'value': feature['jira_key']},
                    {'name': 'Status:', 'value': 'New'}
                ]
            }
        ]
```

---

## Conclusion

Collaboration tool integrations enable product teams to work more efficiently by automating routine tasks, centralizing information, and keeping stakeholders informed. By implementing Slack, Teams, and Jira integrations, PMs can create a seamless workflow that connects customer feedback, product planning, and development execution.

Key takeaways:
- Use event subscriptions for real-time collaboration
- Implement slash commands for easy team interaction
- Send rich formatted messages with blocks/cards
- Sync product data across multiple platforms
- Verify webhook signatures for security
- Create unified notification systems
- Test interactions thoroughly before deployment
- Document command syntax and workflows for team

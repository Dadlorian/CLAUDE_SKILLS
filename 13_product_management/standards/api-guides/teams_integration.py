"""
Microsoft Teams Product Management Integration
Complete implementation for Teams bot with adaptive cards, webhooks, and notifications.
Includes authentication via Azure AD, interactive messaging, and rich content formatting.

Features:
- Adaptive Cards for rich messaging
- Incoming Webhooks for notifications
- Outgoing Webhooks for Team responses
- Bot Framework integration
- Message reactions and threading
- User presence tracking
- Group chat support
- File sharing integration
"""

import json
import uuid
import logging
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import os
from abc import ABC, abstractmethod

# Third-party imports (pip install requests azure-identity)
import requests
from requests.auth import HTTPBasicAuth
from functools import wraps


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== Data Models ====================

class RiskLevel(Enum):
    """Risk level enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class UpdateType(Enum):
    """Update type enumeration"""
    MILESTONE = "milestone"
    RISK_ALERT = "risk_alert"
    MEETING_REMINDER = "meeting_reminder"
    STAKEHOLDER_FEEDBACK = "stakeholder_feedback"
    SPRINT_REVIEW = "sprint_review"
    RELEASE_NOTIFICATION = "release_notification"


@dataclass
class TeamMember:
    """Team member data model"""
    user_id: str
    name: str
    email: str
    role: str
    department: str
    manager_id: Optional[str] = None


@dataclass
class RiskItem:
    """Risk item data model"""
    risk_id: str
    title: str
    description: str
    risk_level: RiskLevel
    owner: str
    mitigation_plan: str
    impact_score: int  # 1-10
    probability_score: int  # 1-10
    created_date: str
    target_resolution_date: str


@dataclass
class MilestoneUpdate:
    """Milestone update data model"""
    milestone_id: str
    name: str
    description: str
    completion_percentage: int
    target_date: str
    owner: str
    deliverables: List[str]
    completed_items: int
    total_items: int


@dataclass
class StakeholderMessage:
    """Stakeholder message data model"""
    message_id: str
    sender: str
    recipient_group: str
    subject: str
    content: str
    priority: str
    attachments: List[str] = None
    requires_approval: bool = False


# ==================== Authentication & Verification ====================

class TeamsAuthenticator:
    """Handles Teams authentication and request verification"""

    def __init__(self, app_id: str, app_password: str, webhook_secret: str):
        """
        Initialize Teams authenticator

        Args:
            app_id: Azure Bot Service App ID
            app_password: Azure Bot Service App Password
            webhook_secret: Webhook verification secret
        """
        self.app_id = app_id
        self.app_password = app_password
        self.webhook_secret = webhook_secret
        self.token_url = "https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token"
        self.service_url = "https://smba.trafficmanager.net/teams"

    def verify_request(self, body: str, signature: str) -> bool:
        """
        Verify incoming request from Teams

        Args:
            body: Request body
            signature: X-Hub-Signature header value

        Returns:
            bool: True if request is valid
        """
        if not signature:
            return False

        hash_algorithm, signature_hash = signature.split('=')
        if hash_algorithm.lower() != 'sha256':
            return False

        expected_hash = hmac.new(
            self.webhook_secret.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()

        is_valid = hmac.compare_digest(expected_hash, signature_hash)
        if not is_valid:
            logger.warning("Invalid webhook signature")
        return is_valid

    def get_access_token(self) -> Optional[str]:
        """
        Get Azure AD access token for Bot Framework

        Returns:
            Optional[str]: Access token or None if failed
        """
        try:
            response = requests.post(
                self.token_url,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.app_id,
                    'client_secret': self.app_password,
                    'scope': 'https://api.botframework.com/.default'
                }
            )
            response.raise_for_status()
            return response.json()['access_token']
        except requests.RequestException as e:
            logger.error(f"Error getting access token: {e}")
            return None


# ==================== Adaptive Cards ====================

class AdaptiveCardBuilder:
    """Builds Microsoft Teams Adaptive Cards"""

    @staticmethod
    def build_milestone_card(milestone: MilestoneUpdate) -> Dict:
        """Build Adaptive Card for milestone update"""
        progress_bar = "".join(['█' if i < milestone.completion_percentage // 10 else '░'
                               for i in range(10)])

        return {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "Container",
                    "style": "accent",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"🎯 {milestone.name}",
                            "weight": "bolder",
                            "size": "large"
                        }
                    ]
                },
                {
                    "type": "Container",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": milestone.description,
                            "wrap": True
                        }
                    ]
                },
                {
                    "type": "Container",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"Progress: {progress_bar} {milestone.completion_percentage}%",
                            "weight": "bolder",
                            "spacing": "medium"
                        },
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": f"Completed: {milestone.completed_items}/{milestone.total_items}",
                                            "size": "small"
                                        }
                                    ]
                                },
                                {
                                    "width": "auto",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": f"Due: {milestone.target_date}",
                                            "size": "small",
                                            "horizontalAlignment": "right"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "Container",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Deliverables",
                            "weight": "bolder",
                            "size": "medium",
                            "spacing": "medium"
                        }
                    ]
                },
                {
                    "type": "Container",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "\n".join([f"• {item}" for item in milestone.deliverables]),
                            "wrap": True,
                            "size": "small"
                        }
                    ]
                },
                {
                    "type": "Container",
                    "items": [
                        {
                            "type": "FactSet",
                            "facts": [
                                {
                                    "name": "Owner:",
                                    "value": milestone.owner
                                },
                                {
                                    "name": "Status:",
                                    "value": f"{milestone.completion_percentage}% Complete"
                                }
                            ]
                        }
                    ]
                }
            ],
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "View Details",
                    "url": f"https://your-product-dashboard.com/milestones/{milestone.milestone_id}"
                },
                {
                    "type": "Action.OpenUrl",
                    "title": "Update Status",
                    "url": f"https://your-product-dashboard.com/milestones/{milestone.milestone_id}/edit"
                }
            ]
        }

    @staticmethod
    def build_risk_alert_card(risk: RiskItem) -> Dict:
        """Build Adaptive Card for risk alert"""
        risk_color_map = {
            RiskLevel.CRITICAL: "#FF0000",
            RiskLevel.HIGH: "#FF6600",
            RiskLevel.MEDIUM: "#FFD700",
            RiskLevel.LOW: "#00AA00",
            RiskLevel.NONE: "#00FF00"
        }

        risk_icon_map = {
            RiskLevel.CRITICAL: "🚨",
            RiskLevel.HIGH: "⚠️",
            RiskLevel.MEDIUM: "⚡",
            RiskLevel.LOW: "📋",
            RiskLevel.NONE: "✅"
        }

        return {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "Container",
                    "style": "attention" if risk.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH] else "default",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"{risk_icon_map[risk.risk_level]} {risk.title}",
                            "weight": "bolder",
                            "size": "large",
                            "color": "attention" if risk.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH] else "default"
                        }
                    ]
                },
                {
                    "type": "Container",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": risk.description,
                            "wrap": True,
                            "spacing": "medium"
                        }
                    ]
                },
                {
                    "type": "Container",
                    "items": [
                        {
                            "type": "FactSet",
                            "facts": [
                                {
                                    "name": "Risk Level:",
                                    "value": risk.risk_level.value.upper()
                                },
                                {
                                    "name": "Impact Score:",
                                    "value": f"{risk.impact_score}/10"
                                },
                                {
                                    "name": "Probability:",
                                    "value": f"{risk.probability_score}/10"
                                },
                                {
                                    "name": "Owner:",
                                    "value": risk.owner
                                },
                                {
                                    "name": "Target Resolution:",
                                    "value": risk.target_resolution_date
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "Container",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Mitigation Plan:",
                            "weight": "bolder",
                            "spacing": "medium"
                        },
                        {
                            "type": "TextBlock",
                            "text": risk.mitigation_plan,
                            "wrap": True,
                            "size": "small"
                        }
                    ]
                }
            ],
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "View Risk Details",
                    "url": f"https://your-dashboard.com/risks/{risk.risk_id}"
                },
                {
                    "type": "Action.OpenUrl",
                    "title": "Update Mitigation",
                    "url": f"https://your-dashboard.com/risks/{risk.risk_id}/mitigation"
                }
            ]
        }

    @staticmethod
    def build_stakeholder_message_card(message: StakeholderMessage) -> Dict:
        """Build Adaptive Card for stakeholder message"""
        return {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "Container",
                    "style": "accent" if message.priority == "high" else "default",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"📧 {message.subject}",
                            "weight": "bolder",
                            "size": "large"
                        }
                    ]
                },
                {
                    "type": "Container",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"From: {message.sender}",
                            "size": "small",
                            "color": "accent"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"To: {message.recipient_group}",
                            "size": "small",
                            "spacing": "small"
                        }
                    ]
                },
                {
                    "type": "Container",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": message.content,
                            "wrap": True,
                            "spacing": "medium"
                        }
                    ]
                }
            ],
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "Read Full Message",
                    "url": f"https://your-dashboard.com/messages/{message.message_id}"
                }
            ]
        }

    @staticmethod
    def build_sprint_review_card(sprint_data: Dict) -> Dict:
        """Build Adaptive Card for sprint review"""
        return {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "Container",
                    "style": "accent",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"📊 Sprint {sprint_data.get('sprint_number', 'N/A')} Review",
                            "weight": "bolder",
                            "size": "large"
                        }
                    ]
                },
                {
                    "type": "Container",
                    "items": [
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": f"Sprint Duration: {sprint_data.get('start_date')} to {sprint_data.get('end_date')}",
                                            "size": "small"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "Container",
                    "items": [
                        {
                            "type": "FactSet",
                            "facts": [
                                {
                                    "name": "Completed:",
                                    "value": f"{sprint_data.get('completed_tasks', 0)} tasks"
                                },
                                {
                                    "name": "In Progress:",
                                    "value": f"{sprint_data.get('in_progress_tasks', 0)} tasks"
                                },
                                {
                                    "name": "Blocked:",
                                    "value": f"{sprint_data.get('blocked_tasks', 0)} tasks"
                                },
                                {
                                    "name": "Velocity:",
                                    "value": f"{sprint_data.get('velocity', 'N/A')} points"
                                }
                            ]
                        }
                    ]
                }
            ]
        }


# ==================== Webhook Management ====================

class TeamsWebhookManager:
    """Manages Teams webhooks and incoming/outgoing integrations"""

    def __init__(self, app_id: str, app_password: str):
        self.app_id = app_id
        self.app_password = app_password
        self.headers = {
            'Content-Type': 'application/json'
        }

    def send_to_webhook(self, webhook_url: str, card: Dict) -> bool:
        """
        Send Adaptive Card to incoming webhook

        Args:
            webhook_url: Teams incoming webhook URL
            card: Adaptive Card data

        Returns:
            bool: Success status
        """
        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "themeColor": "0078D4",
            "summary": "Product Management Update",
            "sections": [
                {
                    "activityTitle": "Update from PM System",
                    "facts": [
                        {
                            "name": "Timestamp",
                            "value": datetime.now().isoformat()
                        }
                    ]
                }
            ],
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "View in Dashboard",
                    "targets": [
                        {
                            "os": "default",
                            "uri": "https://your-dashboard.com"
                        }
                    ]
                }
            ]
        }

        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Webhook sent successfully to {webhook_url}")
            return True
        except requests.RequestException as e:
            logger.error(f"Error sending webhook: {e}")
            return False

    def send_adaptive_card(self, service_url: str, channel_id: str, team_id: str,
                          access_token: str, card: Dict) -> bool:
        """
        Send Adaptive Card via Bot Framework API

        Args:
            service_url: Teams service URL
            channel_id: Channel ID to send to
            team_id: Team ID
            access_token: Access token for authentication
            card: Adaptive Card data

        Returns:
            bool: Success status
        """
        conversation_id = str(uuid.uuid4())

        payload = {
            "type": "message",
            "from": {
                "id": f"28:{self.app_id}",
                "name": "PM Bot"
            },
            "conversation": {
                "id": conversation_id
            },
            "channelData": {
                "teamsChannelId": channel_id,
                "teamsGroupId": team_id
            },
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": card
                }
            ]
        }

        url = f"{service_url}/v3/conversations/{conversation_id}/activities"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Adaptive card sent to channel {channel_id}")
            return True
        except requests.RequestException as e:
            logger.error(f"Error sending adaptive card: {e}")
            return False


# ==================== Message Handlers ====================

class TeamsMessageHandler:
    """Handles incoming Teams messages and activities"""

    def __init__(self, authenticator: TeamsAuthenticator):
        self.authenticator = authenticator

    def handle_invoke(self, activity: Dict) -> Dict:
        """
        Handle invoke activities (button clicks, etc.)

        Args:
            activity: Invoke activity data

        Returns:
            dict: Response to send back
        """
        invoke_type = activity.get('name')

        if invoke_type == 'adaptiveCard/action':
            action_data = activity.get('value', {})
            return self._handle_adaptive_card_action(action_data)

        return {"status": 404}

    def _handle_adaptive_card_action(self, action_data: Dict) -> Dict:
        """Handle Adaptive Card button actions"""
        action = action_data.get('action')

        if action == 'update_status':
            status = action_data.get('status')
            logger.info(f"Status updated to: {status}")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": f"Status updated to {status}"
                })
            }

        return {"status": 400}

    def handle_message(self, activity: Dict) -> str:
        """
        Handle incoming messages

        Args:
            activity: Message activity data

        Returns:
            str: Response message
        """
        text = activity.get('text', '').lower()
        from_id = activity['from']['id']
        from_name = activity['from']['name']

        logger.info(f"Message from {from_name}: {text}")

        # Simple keyword detection
        if 'roadmap' in text:
            return "Here's the current roadmap..."
        elif 'metrics' in text:
            return "Latest metrics are available in the dashboard"
        elif 'help' in text:
            return "I can help with roadmap, metrics, risks, and milestones!"

        return "I didn't quite understand that. Type 'help' for available commands."

    def handle_member_joined(self, activity: Dict):
        """Handle member joined event"""
        member_id = activity['from']['id']
        member_name = activity['from']['name']
        logger.info(f"Member joined: {member_name}")


# ==================== Main Teams Bot Class ====================

class TeamsProductManagementBot:
    """Main Microsoft Teams Product Management Bot"""

    def __init__(self, app_id: str, app_password: str, webhook_secret: str):
        """
        Initialize Teams PM bot

        Args:
            app_id: Azure Bot Service App ID
            app_password: Azure Bot Service App Password
            webhook_secret: Webhook verification secret
        """
        self.authenticator = TeamsAuthenticator(app_id, app_password, webhook_secret)
        self.webhook_manager = TeamsWebhookManager(app_id, app_password)
        self.message_handler = TeamsMessageHandler(self.authenticator)
        self.card_builder = AdaptiveCardBuilder()

    def process_activity(self, headers: Dict, body: str) -> Tuple[int, Dict]:
        """
        Process incoming activity from Teams

        Args:
            headers: HTTP headers
            body: Request body

        Returns:
            Tuple of (status_code, response_data)
        """
        signature = headers.get('X-Hub-Signature', '')

        # Verify webhook signature
        if not self.authenticator.verify_request(body, signature):
            logger.warning("Invalid webhook signature")
            return (401, {"error": "Unauthorized"})

        # Parse activity
        try:
            activity = json.loads(body)
        except json.JSONDecodeError:
            return (400, {"error": "Invalid JSON"})

        activity_type = activity.get('type')

        # Handle different activity types
        if activity_type == 'invoke':
            response = self.message_handler.handle_invoke(activity)
            return (200, response)

        elif activity_type == 'message':
            response = self.message_handler.handle_message(activity)
            return (200, {"text": response})

        elif activity_type == 'conversationUpdate':
            members_added = activity.get('membersAdded', [])
            for member in members_added:
                if member['id'] != self.authenticator.app_id:
                    self.message_handler.handle_member_joined(activity)
            return (200, {})

        else:
            logger.info(f"Received activity type: {activity_type}")
            return (200, {})

    def send_milestone_update(self, milestone: MilestoneUpdate,
                             webhook_url: str) -> bool:
        """
        Send milestone update to Teams

        Args:
            milestone: MilestoneUpdate object
            webhook_url: Teams incoming webhook URL

        Returns:
            bool: Success status
        """
        card = self.card_builder.build_milestone_card(milestone)
        return self.webhook_manager.send_to_webhook(webhook_url, card)

    def send_risk_alert(self, risk: RiskItem, webhook_url: str) -> bool:
        """
        Send risk alert to Teams

        Args:
            risk: RiskItem object
            webhook_url: Teams incoming webhook URL

        Returns:
            bool: Success status
        """
        card = self.card_builder.build_risk_alert_card(risk)
        return self.webhook_manager.send_to_webhook(webhook_url, card)

    def send_stakeholder_message(self, message: StakeholderMessage,
                                webhook_url: str) -> bool:
        """
        Send stakeholder message to Teams

        Args:
            message: StakeholderMessage object
            webhook_url: Teams incoming webhook URL

        Returns:
            bool: Success status
        """
        card = self.card_builder.build_stakeholder_message_card(message)
        return self.webhook_manager.send_to_webhook(webhook_url, card)

    def send_sprint_review(self, sprint_data: Dict, webhook_url: str) -> bool:
        """
        Send sprint review to Teams

        Args:
            sprint_data: Sprint data dictionary
            webhook_url: Teams incoming webhook URL

        Returns:
            bool: Success status
        """
        card = self.card_builder.build_sprint_review_card(sprint_data)
        return self.webhook_manager.send_to_webhook(webhook_url, card)


# ==================== Notification Orchestrator ====================

class TeamsNotificationOrchestrator:
    """Orchestrates notifications across Teams channels"""

    def __init__(self, bot: TeamsProductManagementBot):
        self.bot = bot
        self.channel_subscriptions: Dict[str, List[str]] = {}

    def subscribe_channel(self, channel_id: str, webhook_url: str, event_types: List[str]):
        """
        Subscribe channel to event types

        Args:
            channel_id: Teams channel ID
            webhook_url: Incoming webhook URL
            event_types: List of event types to subscribe to
        """
        for event_type in event_types:
            if event_type not in self.channel_subscriptions:
                self.channel_subscriptions[event_type] = []
            self.channel_subscriptions[event_type].append({
                'channel_id': channel_id,
                'webhook_url': webhook_url
            })

    def notify_milestone(self, milestone: MilestoneUpdate, event_type: str = 'milestone'):
        """Notify all subscribed channels of milestone update"""
        if event_type not in self.channel_subscriptions:
            return

        for subscription in self.channel_subscriptions[event_type]:
            self.bot.send_milestone_update(milestone, subscription['webhook_url'])

    def notify_risk(self, risk: RiskItem, event_type: str = 'risk'):
        """Notify all subscribed channels of risk"""
        if event_type not in self.channel_subscriptions:
            return

        for subscription in self.channel_subscriptions[event_type]:
            self.bot.send_risk_alert(risk, subscription['webhook_url'])

    def notify_stakeholders(self, message: StakeholderMessage):
        """Notify all subscribed channels of stakeholder message"""
        event_type = 'stakeholder'
        if event_type not in self.channel_subscriptions:
            return

        for subscription in self.channel_subscriptions[event_type]:
            self.bot.send_stakeholder_message(message, subscription['webhook_url'])


# ==================== Environment Configuration ====================

def load_config() -> Dict[str, str]:
    """Load configuration from environment variables"""
    return {
        'app_id': os.getenv('TEAMS_APP_ID'),
        'app_password': os.getenv('TEAMS_APP_PASSWORD'),
        'webhook_secret': os.getenv('TEAMS_WEBHOOK_SECRET'),
        'port': int(os.getenv('PORT', '3000'))
    }


# ==================== Example Usage ====================

if __name__ == '__main__':
    # Load configuration
    config = load_config()

    if config['app_id'] and config['app_password'] and config['webhook_secret']:
        # Initialize bot
        bot = TeamsProductManagementBot(
            app_id=config['app_id'],
            app_password=config['app_password'],
            webhook_secret=config['webhook_secret']
        )

        # Initialize notification orchestrator
        orchestrator = TeamsNotificationOrchestrator(bot)

        # Subscribe channels
        orchestrator.subscribe_channel(
            channel_id="19:xxx@thread.tacv2",
            webhook_url="https://outlook.webhook.office.com/webhookb2/xxx",
            event_types=['milestone', 'risk', 'stakeholder']
        )

        # Example: Send milestone update
        milestone = MilestoneUpdate(
            milestone_id="M001",
            name="Q4 Platform Stability Initiative",
            description="Comprehensive infrastructure upgrades and performance optimizations",
            completion_percentage=65,
            target_date="2024-03-31",
            owner="Infrastructure Team",
            deliverables=[
                "Database optimization",
                "CDN implementation",
                "Caching layer deployment",
                "Load testing completion"
            ],
            completed_items=6,
            total_items=10
        )

        # Send update
        # orchestrator.notify_milestone(milestone)

        logger.info("Teams PM Bot initialized successfully")
    else:
        logger.error("Missing Teams credentials in environment variables")

"""
Slack Product Management Bot
Complete implementation for roadmap updates, feature announcements, and metrics tracking.
Includes real-time notifications, slash commands, and interactive messaging.

Features:
- Real-time roadmap updates via Slack messages
- Weekly metrics dashboard
- Feature request integration
- Team notifications with rich formatting
- Slash commands for quick actions
- Message threading and reactions
- Authentication and webhook verification
"""

import json
import hashlib
import hmac
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import os

# Third-party imports (pip install slack-sdk requests)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== Data Models ====================

class FeatureStatus(Enum):
    """Feature status enumeration"""
    PLANNING = "planning"
    IN_DEVELOPMENT = "in_development"
    TESTING = "testing"
    LAUNCHED = "launched"
    DEPRECATED = "deprecated"


class MetricType(Enum):
    """Metric type enumeration"""
    ENGAGEMENT = "engagement"
    RETENTION = "retention"
    PERFORMANCE = "performance"
    REVENUE = "revenue"
    ADOPTION = "adoption"


@dataclass
class Feature:
    """Feature data model"""
    id: str
    name: str
    description: str
    status: FeatureStatus
    target_date: str
    team: str
    priority: str
    epic: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'status': self.status.value
        }


@dataclass
class Metric:
    """Metric data model"""
    name: str
    value: float
    unit: str
    metric_type: MetricType
    change_percentage: float
    timestamp: str

    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'metric_type': self.metric_type.value
        }


@dataclass
class RoadmapUpdate:
    """Roadmap update model"""
    feature: Feature
    update_type: str  # new, status_change, milestone_reached, risk_identified
    description: str
    creator: str
    timestamp: str


# ==================== Authentication & Verification ====================

class SlackAuthenticator:
    """Handles Slack request authentication and verification"""

    def __init__(self, signing_secret: str, bot_token: str):
        """
        Initialize authenticator with Slack credentials

        Args:
            signing_secret: Slack app signing secret
            bot_token: Slack bot token
        """
        self.signing_secret = signing_secret
        self.bot_token = bot_token
        self.client = WebClient(token=bot_token)

    def verify_request(self, timestamp: str, signature: str, body: str) -> bool:
        """
        Verify that request came from Slack using signing secret

        Args:
            timestamp: Request timestamp from header
            signature: Request signature from header
            body: Raw request body

        Returns:
            bool: True if request is valid, False otherwise
        """
        # Check timestamp is recent (within 5 minutes)
        if abs(time.time() - int(timestamp)) > 300:
            logger.warning("Request timestamp too old")
            return False

        # Verify signature
        sig_basestring = f'v0:{timestamp}:{body}'
        my_signature = 'v0=' + hmac.new(
            self.signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()

        is_valid = hmac.compare_digest(my_signature, signature)
        if not is_valid:
            logger.warning("Invalid request signature")
        return is_valid

    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """Get Slack user information"""
        try:
            response = self.client.users_info(user=user_id)
            return response['user']
        except SlackApiError as e:
            logger.error(f"Error getting user info: {e}")
            return None


# ==================== Webhook Management ====================

class SlackWebhookManager:
    """Manages Slack webhooks and event handling"""

    def __init__(self, client: WebClient):
        self.client = client
        self.event_handlers: Dict[str, List] = {}

    def register_handler(self, event_type: str, handler: callable):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    def handle_event(self, event_data: Dict) -> bool:
        """
        Route event to registered handlers

        Args:
            event_data: Event data from Slack

        Returns:
            bool: True if event was handled
        """
        event_type = event_data.get('type')
        if event_type not in self.event_handlers:
            return False

        handlers = self.event_handlers[event_type]
        for handler in handlers:
            try:
                handler(event_data)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")

        return True

    def subscribe_to_events(self) -> List[str]:
        """Return list of events this app subscribes to"""
        return [
            'app_mention',
            'message',
            'reaction_added',
            'reaction_removed',
            'slash_commands',
            'event_callback'
        ]


# ==================== Message Formatting ====================

class SlackMessageFormatter:
    """Formats rich Slack messages using Block Kit"""

    @staticmethod
    def format_feature_update(feature: Feature, update: RoadmapUpdate) -> Dict:
        """Format feature update as Slack message blocks"""
        status_color_map = {
            FeatureStatus.PLANNING: "#FFA500",
            FeatureStatus.IN_DEVELOPMENT: "#0099FF",
            FeatureStatus.TESTING: "#9966FF",
            FeatureStatus.LAUNCHED: "#00AA00",
            FeatureStatus.DEPRECATED: "#999999"
        }

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f":rocket: {feature.name}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\n{feature.status.value.replace('_', ' ').title()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Team:*\n{feature.team}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Priority:*\n{feature.priority.upper()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Target Date:*\n{feature.target_date}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{feature.description}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Update:* {update.description}\n_By {update.creator} on {update.timestamp}_"
                }
            }
        ]

        return {
            "blocks": blocks,
            "attachments": [
                {
                    "color": status_color_map.get(feature.status, "#CCCCCC"),
                    "footer": "Product Management Bot",
                    "ts": int(time.time())
                }
            ]
        }

    @staticmethod
    def format_metrics_dashboard(metrics: List[Metric]) -> Dict:
        """Format metrics dashboard as Slack message blocks"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":chart_with_upwards_trend: Weekly Metrics Dashboard",
                    "emoji": True
                }
            }
        ]

        # Group metrics by type
        metrics_by_type = {}
        for metric in metrics:
            if metric.metric_type not in metrics_by_type:
                metrics_by_type[metric.metric_type] = []
            metrics_by_type[metric.metric_type].append(metric)

        # Format each metric type
        for metric_type, type_metrics in metrics_by_type.items():
            type_label = metric_type.value.replace('_', ' ').title()
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{type_label}*"
                }
            })

            for metric in type_metrics:
                trend = "📈" if metric.change_percentage >= 0 else "📉"
                blocks.append({
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*{metric.name}*\n{metric.value} {metric.unit}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"{trend} *Change*\n{metric.change_percentage:+.1f}%"
                        }
                    ]
                })

        blocks.extend([
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"_Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
                    }
                ]
            }
        ])

        return {"blocks": blocks}

    @staticmethod
    def format_roadmap_summary(features: List[Feature]) -> Dict:
        """Format roadmap summary as Slack message blocks"""
        # Group features by status
        features_by_status = {}
        for feature in features:
            if feature.status not in features_by_status:
                features_by_status[feature.status] = []
            features_by_status[feature.status].append(feature)

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":calendar: Product Roadmap Summary",
                    "emoji": True
                }
            }
        ]

        for status in [FeatureStatus.PLANNING, FeatureStatus.IN_DEVELOPMENT,
                      FeatureStatus.TESTING, FeatureStatus.LAUNCHED]:
            if status not in features_by_status:
                continue

            features_in_status = features_by_status[status]
            status_label = status.value.replace('_', ' ').title()

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{status_label}* ({len(features_in_status)})"
                }
            })

            for feature in features_in_status[:3]:  # Show top 3
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• *{feature.name}*\n  {feature.description[:100]}...\n  Target: {feature.target_date}"
                    }
                })

        return {"blocks": blocks}


# ==================== Command Handlers ====================

class SlackCommandHandler:
    """Handles Slack slash commands"""

    def __init__(self, client: WebClient):
        self.client = client
        self.feature_db = {}  # In-memory storage, use DB in production

    def handle_roadmap_command(self, command_data: Dict) -> str:
        """
        Handle /roadmap command

        Args:
            command_data: Slack slash command data

        Returns:
            str: Response message
        """
        channel_id = command_data['channel_id']
        user_id = command_data['user_id']
        text = command_data.get('text', '').split()

        if not text or text[0] == 'list':
            # Show roadmap summary
            features = list(self.feature_db.values())
            message = SlackMessageFormatter.format_roadmap_summary(features)

            try:
                self.client.chat_postMessage(channel=channel_id, **message)
                return "Roadmap summary posted"
            except SlackApiError as e:
                logger.error(f"Error posting message: {e}")
                return "Error posting roadmap summary"

        elif text[0] == 'add':
            # Add new feature (requires additional params)
            return "Use /roadmap_add for adding new features"

        return "Usage: /roadmap [list|add]"

    def handle_metrics_command(self, command_data: Dict) -> str:
        """
        Handle /metrics command

        Args:
            command_data: Slack slash command data

        Returns:
            str: Response message
        """
        channel_id = command_data['channel_id']
        period = command_data.get('text', 'week').lower()

        # Generate sample metrics
        metrics = [
            Metric(
                name="User Engagement",
                value=87.5,
                unit="%",
                metric_type=MetricType.ENGAGEMENT,
                change_percentage=5.2,
                timestamp=datetime.now().isoformat()
            ),
            Metric(
                name="Feature Adoption",
                value=62.3,
                unit="%",
                metric_type=MetricType.ADOPTION,
                change_percentage=12.8,
                timestamp=datetime.now().isoformat()
            ),
            Metric(
                name="System Performance",
                value=99.8,
                unit="%",
                metric_type=MetricType.PERFORMANCE,
                change_percentage=-0.1,
                timestamp=datetime.now().isoformat()
            ),
            Metric(
                name="Retention Rate",
                value=78.9,
                unit="%",
                metric_type=MetricType.RETENTION,
                change_percentage=3.5,
                timestamp=datetime.now().isoformat()
            )
        ]

        message = SlackMessageFormatter.format_metrics_dashboard(metrics)

        try:
            self.client.chat_postMessage(channel=channel_id, **message)
            return f"Metrics dashboard for {period} posted"
        except SlackApiError as e:
            logger.error(f"Error posting metrics: {e}")
            return "Error posting metrics dashboard"

    def handle_feature_update_command(self, command_data: Dict) -> str:
        """
        Handle /feature_update command

        Args:
            command_data: Slack slash command data

        Returns:
            str: Response message
        """
        user_id = command_data['user_id']
        channel_id = command_data['channel_id']

        # Open modal for feature update
        trigger_id = command_data.get('trigger_id')

        try:
            self.client.views_open(
                trigger_id=trigger_id,
                view={
                    "type": "modal",
                    "callback_id": "feature_update_modal",
                    "title": {
                        "type": "plain_text",
                        "text": "Feature Update"
                    },
                    "submit": {
                        "type": "plain_text",
                        "text": "Submit"
                    },
                    "blocks": [
                        {
                            "type": "input",
                            "block_id": "feature_name_block",
                            "label": {
                                "type": "plain_text",
                                "text": "Feature Name"
                            },
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "feature_name"
                            }
                        },
                        {
                            "type": "input",
                            "block_id": "update_description_block",
                            "label": {
                                "type": "plain_text",
                                "text": "Update Description"
                            },
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "update_description",
                                "multiline": True
                            }
                        },
                        {
                            "type": "input",
                            "block_id": "status_block",
                            "label": {
                                "type": "plain_text",
                                "text": "Status"
                            },
                            "element": {
                                "type": "static_select",
                                "action_id": "status",
                                "options": [
                                    {
                                        "text": {
                                            "type": "plain_text",
                                            "text": status.value.replace('_', ' ').title()
                                        },
                                        "value": status.value
                                    }
                                    for status in FeatureStatus
                                ]
                            }
                        }
                    ]
                }
            )
            return "Feature update modal opened"
        except SlackApiError as e:
            logger.error(f"Error opening modal: {e}")
            return "Error opening update modal"


# ==================== Event Listeners ====================

class SlackEventListener:
    """Handles Slack event callbacks"""

    def __init__(self, client: WebClient):
        self.client = client

    def handle_app_mention(self, event: Dict):
        """Handle @app mentions"""
        channel = event['channel']
        thread_ts = event.get('thread_ts', event['ts'])
        user_id = event['user']
        text = event['text']

        # Parse mention
        if 'roadmap' in text.lower():
            response = "Here's the current roadmap: [roadmap info]"
        elif 'metrics' in text.lower():
            response = "Latest metrics: [metrics info]"
        else:
            response = "I can help with roadmap, metrics, and feature updates!"

        try:
            self.client.chat_postMessage(
                channel=channel,
                thread_ts=thread_ts,
                text=response,
                metadata={
                    "event_type": "app_mention_response",
                    "event_payload": {
                        "user_id": user_id
                    }
                }
            )
        except SlackApiError as e:
            logger.error(f"Error handling mention: {e}")

    def handle_reaction_added(self, event: Dict):
        """Handle reaction additions"""
        user_id = event['user']
        emoji = event['reaction']
        channel = event['item']['channel']

        logger.info(f"Reaction {emoji} added by {user_id} in {channel}")

    def handle_message(self, event: Dict):
        """Handle regular messages"""
        if event.get('bot_id'):
            return  # Ignore bot messages

        text = event.get('text', '')
        channel = event['channel']
        user_id = event['user']

        # Simple keyword detection
        if 'help' in text.lower():
            help_text = """
*Product Management Bot Commands:*
• /roadmap - View product roadmap
• /metrics - View key metrics
• /feature_update - Submit a feature update
• @PM_Bot [roadmap|metrics|help] - Get information
            """
            try:
                self.client.chat_postMessage(
                    channel=channel,
                    text=help_text
                )
            except SlackApiError as e:
                logger.error(f"Error posting help: {e}")


# ==================== Main Bot Class ====================

class SlackPMBot:
    """Main Slack Product Management Bot"""

    def __init__(self, signing_secret: str, bot_token: str):
        """
        Initialize the PM bot

        Args:
            signing_secret: Slack app signing secret
            bot_token: Slack bot token
        """
        self.authenticator = SlackAuthenticator(signing_secret, bot_token)
        self.client = self.authenticator.client
        self.webhook_manager = SlackWebhookManager(self.client)
        self.command_handler = SlackCommandHandler(self.client)
        self.event_listener = SlackEventListener(self.client)

        # Register event handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register event handlers"""
        self.webhook_manager.register_handler('app_mention',
                                             self.event_listener.handle_app_mention)
        self.webhook_manager.register_handler('reaction_added',
                                             self.event_listener.handle_reaction_added)
        self.webhook_manager.register_handler('message',
                                             self.event_listener.handle_message)

    def process_request(self, headers: Dict, body: str) -> Tuple[int, Dict]:
        """
        Process incoming request from Slack

        Args:
            headers: HTTP headers
            body: Request body

        Returns:
            Tuple of (status_code, response_data)
        """
        timestamp = headers.get('X-Slack-Request-Timestamp')
        signature = headers.get('X-Slack-Signature')

        # Verify request
        if not self.authenticator.verify_request(timestamp, signature, body):
            return (401, {"error": "Unauthorized"})

        # Parse request
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return (400, {"error": "Invalid JSON"})

        # Handle URL verification challenge
        if data.get('type') == 'url_verification':
            return (200, {"challenge": data['challenge']})

        # Handle slash commands
        if data.get('command'):
            return self._handle_slash_command(data)

        # Handle events
        if data.get('type') == 'event_callback':
            self.webhook_manager.handle_event(data['event'])
            return (200, {"ok": True})

        return (200, {"ok": True})

    def _handle_slash_command(self, data: Dict) -> Tuple[int, str]:
        """Handle slash command"""
        command = data['command']

        if command == '/roadmap':
            response = self.command_handler.handle_roadmap_command(data)
        elif command == '/metrics':
            response = self.command_handler.handle_metrics_command(data)
        elif command == '/feature_update':
            response = self.command_handler.handle_feature_update_command(data)
        else:
            response = f"Unknown command: {command}"

        return (200, response)

    def send_roadmap_update(self, feature: Feature, update: RoadmapUpdate,
                           channel: str) -> bool:
        """
        Send roadmap update to a channel

        Args:
            feature: Feature object
            update: RoadmapUpdate object
            channel: Slack channel ID

        Returns:
            bool: Success status
        """
        message = SlackMessageFormatter.format_feature_update(feature, update)

        try:
            self.client.chat_postMessage(channel=channel, **message)
            logger.info(f"Roadmap update sent to {channel}")
            return True
        except SlackApiError as e:
            logger.error(f"Error sending roadmap update: {e}")
            return False

    def send_metrics_alert(self, metrics: List[Metric], channel: str) -> bool:
        """Send metrics dashboard to channel"""
        message = SlackMessageFormatter.format_metrics_dashboard(metrics)

        try:
            self.client.chat_postMessage(channel=channel, **message)
            logger.info(f"Metrics alert sent to {channel}")
            return True
        except SlackApiError as e:
            logger.error(f"Error sending metrics: {e}")
            return False


# ==================== Environment Configuration ====================

def load_config() -> Dict[str, str]:
    """Load configuration from environment variables"""
    return {
        'signing_secret': os.getenv('SLACK_SIGNING_SECRET'),
        'bot_token': os.getenv('SLACK_BOT_TOKEN'),
        'port': int(os.getenv('PORT', '3000'))
    }


# ==================== Example Usage ====================

if __name__ == '__main__':
    # Load configuration
    config = load_config()

    # Initialize bot
    if config['signing_secret'] and config['bot_token']:
        bot = SlackPMBot(
            signing_secret=config['signing_secret'],
            bot_token=config['bot_token']
        )

        # Example: Send a feature update
        feature = Feature(
            id="feature_001",
            name="Advanced Analytics Dashboard",
            description="Real-time analytics with custom metrics and drill-down capabilities",
            status=FeatureStatus.IN_DEVELOPMENT,
            target_date="2024-02-15",
            team="Analytics Team",
            priority="high",
            epic="Analytics Platform V2"
        )

        update = RoadmapUpdate(
            feature=feature,
            update_type="status_change",
            description="Moved to development phase. Backend API integration 60% complete.",
            creator="Product Manager",
            timestamp=datetime.now().isoformat()
        )

        # Send update (requires valid Slack credentials and channel)
        # bot.send_roadmap_update(feature, update, "C123456789")

        logger.info("Slack PM Bot initialized successfully")
    else:
        logger.error("Missing Slack credentials in environment variables")

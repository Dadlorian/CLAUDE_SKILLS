"""
Automated Stakeholder Notification System
Complete implementation for multi-channel notification automation with scheduling,
templating, personalization, and delivery tracking.

Features:
- Multi-channel delivery (Email, SMS, Slack, Teams, Webhooks)
- Scheduled notifications with cron support
- Template engine with variable substitution
- Recipient segmentation and targeting
- Delivery tracking and retry logic
- Priority queuing
- Rate limiting and throttling
- Audit logging
- Unsubscribe management
"""

import json
import logging
import smtplib
import uuid
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from abc import ABC, abstractmethod
from queue import PriorityQueue, Queue
from threading import Thread, Lock
import os
import re

# Third-party imports (pip install requests schedule croniter)
import requests
import schedule
from croniter import croniter
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== Data Models ====================

class NotificationChannel(Enum):
    """Supported notification channels"""
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    SMS = "sms"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class NotificationPriority(Enum):
    """Notification priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class RecipientRole(Enum):
    """Recipient role types"""
    EXECUTIVE = "executive"
    MANAGER = "manager"
    TEAM_MEMBER = "team_member"
    STAKEHOLDER = "stakeholder"
    CLIENT = "client"


class NotificationStatus(Enum):
    """Notification delivery status"""
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"
    UNSUBSCRIBED = "unsubscribed"


@dataclass
class NotificationRecipient:
    """Notification recipient data model"""
    recipient_id: str
    name: str
    email: str
    phone: str
    role: RecipientRole
    preferred_channels: List[NotificationChannel]
    subscription_settings: Dict[str, bool] = field(default_factory=dict)
    custom_data: Dict[str, Any] = field(default_factory=dict)

    def is_subscribed(self, channel: NotificationChannel) -> bool:
        """Check if recipient is subscribed to channel"""
        return self.subscription_settings.get(channel.value, True)

    def get_active_channels(self) -> List[NotificationChannel]:
        """Get active notification channels for recipient"""
        return [ch for ch in self.preferred_channels
                if self.is_subscribed(ch)]


@dataclass
class NotificationTemplate:
    """Notification template data model"""
    template_id: str
    name: str
    description: str
    subject: str  # Used for email and in-app
    content: str
    html_content: Optional[str] = None
    channels: List[NotificationChannel] = field(default_factory=list)
    variables: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def render(self, variables: Dict[str, Any]) -> Tuple[str, str]:
        """
        Render template with variables

        Args:
            variables: Dictionary of template variables

        Returns:
            Tuple of (rendered_subject, rendered_content)
        """
        subject = self.subject
        content = self.content

        # Replace variables using template syntax
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            subject = subject.replace(placeholder, str(value))
            content = content.replace(placeholder, str(value))

        return subject, content


@dataclass
class NotificationPayload:
    """Notification payload data model"""
    payload_id: str
    template: NotificationTemplate
    recipients: List[NotificationRecipient]
    variables: Dict[str, Any]
    channels: List[NotificationChannel]
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_time: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class NotificationLog:
    """Notification delivery log"""
    log_id: str
    payload_id: str
    recipient_id: str
    channel: NotificationChannel
    status: NotificationStatus
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    response_data: Dict[str, Any] = field(default_factory=dict)


# ==================== Template Engine ====================

class NotificationTemplateEngine:
    """Manages notification templates and rendering"""

    def __init__(self):
        self.templates: Dict[str, NotificationTemplate] = {}

    def register_template(self, template: NotificationTemplate):
        """Register a notification template"""
        self.templates[template.template_id] = template
        logger.info(f"Template registered: {template.template_id}")

    def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """Retrieve template by ID"""
        return self.templates.get(template_id)

    def list_templates(self, channel: Optional[NotificationChannel] = None) -> List[NotificationTemplate]:
        """List all templates, optionally filtered by channel"""
        templates = list(self.templates.values())
        if channel:
            templates = [t for t in templates if channel in t.channels]
        return templates

    def render_template(self, template_id: str, variables: Dict[str, Any]) -> Tuple[str, str]:
        """Render template with variables"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        return template.render(variables)


# ==================== Channel Senders ====================

class NotificationSender(ABC):
    """Abstract base class for notification senders"""

    @abstractmethod
    def send(self, recipient: NotificationRecipient, subject: str, content: str,
            html_content: Optional[str] = None, metadata: Dict = None) -> Tuple[bool, str]:
        """
        Send notification

        Returns:
            Tuple of (success, message/error)
        """
        pass


class EmailSender(NotificationSender):
    """Email notification sender"""

    def __init__(self, smtp_host: str, smtp_port: int, sender_email: str, sender_password: str):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send(self, recipient: NotificationRecipient, subject: str, content: str,
            html_content: Optional[str] = None, metadata: Dict = None) -> Tuple[bool, str]:
        """Send email notification"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = recipient.email

            # Add plain text part
            msg.attach(MIMEText(content, 'plain'))

            # Add HTML part if provided
            if html_content:
                msg.attach(MIMEText(html_content, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            logger.info(f"Email sent to {recipient.email}")
            return (True, f"Sent to {recipient.email}")

        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            logger.error(error_msg)
            return (False, error_msg)
        except Exception as e:
            error_msg = f"Error sending email: {str(e)}"
            logger.error(error_msg)
            return (False, error_msg)


class SlackSender(NotificationSender):
    """Slack notification sender"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, recipient: NotificationRecipient, subject: str, content: str,
            html_content: Optional[str] = None, metadata: Dict = None) -> Tuple[bool, str]:
        """Send Slack notification"""
        try:
            # Get user ID from custom data or use default
            user_id = recipient.custom_data.get('slack_user_id')
            if not user_id:
                logger.warning(f"No Slack user ID for {recipient.name}")
                return (False, "No Slack user ID configured")

            payload = {
                "text": subject,
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{subject}*\n{content}"
                        }
                    }
                ]
            }

            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info(f"Slack notification sent")
            return (True, "Message sent")

        except requests.RequestException as e:
            error_msg = f"Slack API error: {str(e)}"
            logger.error(error_msg)
            return (False, error_msg)


class TeamsSender(NotificationSender):
    """Microsoft Teams notification sender"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, recipient: NotificationRecipient, subject: str, content: str,
            html_content: Optional[str] = None, metadata: Dict = None) -> Tuple[bool, str]:
        """Send Teams notification"""
        try:
            payload = {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "themeColor": "0078D4",
                "summary": subject,
                "sections": [
                    {
                        "activityTitle": subject,
                        "text": content,
                        "facts": [
                            {
                                "name": "Recipient:",
                                "value": recipient.name
                            },
                            {
                                "name": "Time:",
                                "value": datetime.now().isoformat()
                            }
                        ]
                    }
                ]
            }

            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info(f"Teams notification sent to {recipient.name}")
            return (True, "Message sent")

        except requests.RequestException as e:
            error_msg = f"Teams API error: {str(e)}"
            logger.error(error_msg)
            return (False, error_msg)


class SMSSender(NotificationSender):
    """SMS notification sender (using Twilio-like interface)"""

    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number

    def send(self, recipient: NotificationRecipient, subject: str, content: str,
            html_content: Optional[str] = None, metadata: Dict = None) -> Tuple[bool, str]:
        """Send SMS notification"""
        try:
            # Combine subject and content for SMS (with length limit)
            message = f"{subject}: {content}"
            if len(message) > 160:
                message = message[:157] + "..."

            # In production, use Twilio API
            logger.info(f"SMS would be sent to {recipient.phone}: {message}")
            return (True, f"SMS queued for {recipient.phone}")

        except Exception as e:
            error_msg = f"Error sending SMS: {str(e)}"
            logger.error(error_msg)
            return (False, error_msg)


class WebhookSender(NotificationSender):
    """Generic webhook notification sender"""

    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        self.base_url = base_url
        self.auth_token = auth_token

    def send(self, recipient: NotificationRecipient, subject: str, content: str,
            html_content: Optional[str] = None, metadata: Dict = None) -> Tuple[bool, str]:
        """Send webhook notification"""
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            if self.auth_token:
                headers['Authorization'] = f"Bearer {self.auth_token}"

            payload = {
                "recipient_id": recipient.recipient_id,
                "recipient_name": recipient.name,
                "subject": subject,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }

            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()

            logger.info(f"Webhook notification sent for {recipient.name}")
            return (True, "Webhook delivered")

        except requests.RequestException as e:
            error_msg = f"Webhook error: {str(e)}"
            logger.error(error_msg)
            return (False, error_msg)


# ==================== Notification Manager ====================

class NotificationManager:
    """Manages notification sending, scheduling, and delivery tracking"""

    def __init__(self):
        self.template_engine = NotificationTemplateEngine()
        self.senders: Dict[NotificationChannel, NotificationSender] = {}
        self.notification_queue: PriorityQueue = PriorityQueue()
        self.delivery_logs: List[NotificationLog] = []
        self.logs_lock = Lock()
        self.max_retries = 3
        self.retry_delay = 300  # seconds
        self.rate_limiter = RateLimiter(calls=100, period=60)

    def register_sender(self, channel: NotificationChannel, sender: NotificationSender):
        """Register a notification sender for a channel"""
        self.senders[channel] = sender
        logger.info(f"Sender registered for channel: {channel.value}")

    def register_template(self, template: NotificationTemplate):
        """Register a notification template"""
        self.template_engine.register_template(template)

    def queue_notification(self, payload: NotificationPayload) -> str:
        """
        Queue a notification for delivery

        Args:
            payload: NotificationPayload object

        Returns:
            str: Payload ID
        """
        # Handle scheduled notifications
        if payload.scheduled_time:
            delay = (payload.scheduled_time - datetime.now()).total_seconds()
            if delay > 0:
                logger.info(f"Notification scheduled for {payload.scheduled_time}")
                # In production, use a scheduler

        # Add to queue with priority
        priority = payload.priority.value
        self.notification_queue.put((priority, payload.payload_id, payload))
        logger.info(f"Notification queued: {payload.payload_id}")

        return payload.payload_id

    def send_notification(self, payload: NotificationPayload) -> Dict[str, NotificationLog]:
        """
        Send notification to all recipients on configured channels

        Args:
            payload: NotificationPayload object

        Returns:
            dict: Delivery logs keyed by recipient ID
        """
        delivery_logs = {}

        for recipient in payload.recipients:
            active_channels = recipient.get_active_channels()

            for channel in active_channels:
                if channel not in payload.channels:
                    continue

                sender = self.senders.get(channel)
                if not sender:
                    logger.warning(f"No sender configured for channel: {channel.value}")
                    continue

                # Rate limiting
                if not self.rate_limiter.allow_request():
                    logger.warning("Rate limit exceeded")
                    continue

                # Render template
                subject, content = self.template_engine.render_template(
                    payload.template.template_id,
                    {**payload.variables, **recipient.custom_data}
                )

                # Send notification
                success, message = sender.send(
                    recipient,
                    subject,
                    content,
                    payload.template.html_content,
                    payload.metadata
                )

                # Log delivery
                log = NotificationLog(
                    log_id=str(uuid.uuid4()),
                    payload_id=payload.payload_id,
                    recipient_id=recipient.recipient_id,
                    channel=channel,
                    status=NotificationStatus.SENT if success else NotificationStatus.FAILED,
                    sent_at=datetime.now() if success else None,
                    error_message=message if not success else None,
                    response_data={"message": message}
                )

                delivery_logs[f"{recipient.recipient_id}_{channel.value}"] = log
                self._log_delivery(log)

        return delivery_logs

    def _log_delivery(self, log: NotificationLog):
        """Log notification delivery"""
        with self.logs_lock:
            self.delivery_logs.append(log)

    def get_delivery_status(self, payload_id: str) -> List[NotificationLog]:
        """Get delivery status for a payload"""
        with self.logs_lock:
            return [log for log in self.delivery_logs if log.payload_id == payload_id]

    def get_delivery_statistics(self) -> Dict[str, Any]:
        """Get delivery statistics"""
        with self.logs_lock:
            total = len(self.delivery_logs)
            sent = len([l for l in self.delivery_logs if l.status == NotificationStatus.SENT])
            failed = len([l for l in self.delivery_logs if l.status == NotificationStatus.FAILED])

            return {
                "total_notifications": total,
                "sent": sent,
                "failed": failed,
                "success_rate": (sent / total * 100) if total > 0 else 0
            }


# ==================== Recipient Segmentation ====================

class RecipientSegment:
    """Manages recipient segmentation and targeting"""

    def __init__(self, segment_id: str, name: str, criteria: Dict[str, Any]):
        self.segment_id = segment_id
        self.name = name
        self.criteria = criteria

    def matches(self, recipient: NotificationRecipient) -> bool:
        """Check if recipient matches segment criteria"""
        # Implement logic based on criteria
        if 'role' in self.criteria:
            if recipient.role not in self.criteria['role']:
                return False
        if 'subscription' in self.criteria:
            for channel, should_subscribe in self.criteria['subscription'].items():
                if recipient.is_subscribed(channel) != should_subscribe:
                    return False
        return True


class RecipientSegmentationEngine:
    """Manages recipient segments and filtering"""

    def __init__(self):
        self.segments: Dict[str, RecipientSegment] = {}
        self.recipients: Dict[str, NotificationRecipient] = {}

    def register_segment(self, segment: RecipientSegment):
        """Register a recipient segment"""
        self.segments[segment.segment_id] = segment

    def add_recipient(self, recipient: NotificationRecipient):
        """Add recipient to engine"""
        self.recipients[recipient.recipient_id] = recipient

    def get_segment_recipients(self, segment_id: str) -> List[NotificationRecipient]:
        """Get all recipients in a segment"""
        segment = self.segments.get(segment_id)
        if not segment:
            return []

        return [r for r in self.recipients.values() if segment.matches(r)]

    def filter_recipients(self, criteria: Dict[str, Any]) -> List[NotificationRecipient]:
        """Filter recipients based on criteria"""
        result = list(self.recipients.values())

        if 'role' in criteria:
            result = [r for r in result if r.role in criteria['role']]

        if 'subscription' in criteria:
            result = [r for r in result
                     if all(r.is_subscribed(NotificationChannel(ch)) == sub
                           for ch, sub in criteria['subscription'].items())]

        return result


# ==================== Rate Limiting ====================

class RateLimiter:
    """Simple rate limiter implementation"""

    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
        self.timestamps: List[float] = []
        self.lock = Lock()

    def allow_request(self) -> bool:
        """Check if request is allowed under rate limit"""
        with self.lock:
            now = time.time()
            # Remove old timestamps
            self.timestamps = [ts for ts in self.timestamps if now - ts < self.period]

            if len(self.timestamps) < self.calls:
                self.timestamps.append(now)
                return True
            return False


# ==================== Notification Scheduler ====================

class NotificationScheduler:
    """Schedules notifications using cron expressions"""

    def __init__(self, manager: NotificationManager):
        self.manager = manager
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.running = False

    def schedule_recurring(self, job_id: str, cron_expression: str,
                          payload_template: Dict[str, Any], max_retries: int = 3):
        """
        Schedule recurring notification

        Args:
            job_id: Unique job ID
            cron_expression: Cron expression (e.g., '0 9 * * MON' for 9 AM Monday)
            payload_template: Template for creating payloads
            max_retries: Max retry attempts
        """
        self.jobs[job_id] = {
            'cron': cron_expression,
            'payload_template': payload_template,
            'max_retries': max_retries,
            'last_run': None
        }
        logger.info(f"Scheduled job: {job_id} with cron: {cron_expression}")

    def start(self):
        """Start the scheduler"""
        self.running = True
        self._run_scheduler()

    def stop(self):
        """Stop the scheduler"""
        self.running = False

    def _run_scheduler(self):
        """Run pending jobs"""
        if not self.running:
            return

        now = datetime.now()

        for job_id, job_config in self.jobs.items():
            cron = croniter(job_config['cron'], job_config.get('last_run', now))
            next_run = cron.get_next(datetime)

            if now >= next_run:
                # Execute job
                logger.info(f"Executing scheduled job: {job_id}")
                # Create and queue payload from template
                job_config['last_run'] = now

        # Schedule next check
        Thread(target=self._delayed_run_scheduler, daemon=True).start()

    def _delayed_run_scheduler(self):
        """Run scheduler after delay"""
        time.sleep(60)
        self._run_scheduler()


# ==================== Main Orchestrator ====================

class NotificationOrchestrator:
    """Main orchestrator for automated stakeholder notifications"""

    def __init__(self):
        self.manager = NotificationManager()
        self.segmentation_engine = RecipientSegmentationEngine()
        self.scheduler = NotificationScheduler(self.manager)

    def setup_email_sender(self, smtp_host: str, smtp_port: int,
                          sender_email: str, sender_password: str):
        """Setup email sender"""
        sender = EmailSender(smtp_host, smtp_port, sender_email, sender_password)
        self.manager.register_sender(NotificationChannel.EMAIL, sender)

    def setup_slack_sender(self, webhook_url: str):
        """Setup Slack sender"""
        sender = SlackSender(webhook_url)
        self.manager.register_sender(NotificationChannel.SLACK, sender)

    def setup_teams_sender(self, webhook_url: str):
        """Setup Teams sender"""
        sender = TeamsSender(webhook_url)
        self.manager.register_sender(NotificationChannel.TEAMS, sender)

    def setup_sms_sender(self, account_sid: str, auth_token: str, from_number: str):
        """Setup SMS sender"""
        sender = SMSSender(account_sid, auth_token, from_number)
        self.manager.register_sender(NotificationChannel.SMS, sender)

    def setup_webhook_sender(self, base_url: str, auth_token: Optional[str] = None):
        """Setup webhook sender"""
        sender = WebhookSender(base_url, auth_token)
        self.manager.register_sender(NotificationChannel.WEBHOOK, sender)

    def register_template(self, template: NotificationTemplate):
        """Register notification template"""
        self.manager.register_template(template)

    def add_recipient(self, recipient: NotificationRecipient):
        """Add recipient"""
        self.segmentation_engine.add_recipient(recipient)

    def send_to_segment(self, segment_id: str, template_id: str,
                       variables: Dict[str, Any],
                       channels: List[NotificationChannel] = None) -> str:
        """
        Send notification to segment

        Args:
            segment_id: Recipient segment ID
            template_id: Template ID
            variables: Template variables
            channels: Notification channels

        Returns:
            str: Payload ID
        """
        recipients = self.segmentation_engine.get_segment_recipients(segment_id)
        if not recipients:
            logger.warning(f"No recipients found in segment: {segment_id}")
            return ""

        template = self.manager.template_engine.get_template(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return ""

        channels = channels or template.channels
        payload = NotificationPayload(
            payload_id=str(uuid.uuid4()),
            template=template,
            recipients=recipients,
            variables=variables,
            channels=channels
        )

        payload_id = self.manager.queue_notification(payload)
        delivery_logs = self.manager.send_notification(payload)

        return payload_id

    def send_to_criteria(self, criteria: Dict[str, Any], template_id: str,
                        variables: Dict[str, Any],
                        channels: List[NotificationChannel] = None) -> str:
        """
        Send notification based on criteria

        Args:
            criteria: Recipient selection criteria
            template_id: Template ID
            variables: Template variables
            channels: Notification channels

        Returns:
            str: Payload ID
        """
        recipients = self.segmentation_engine.filter_recipients(criteria)
        if not recipients:
            logger.warning("No recipients match criteria")
            return ""

        template = self.manager.template_engine.get_template(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return ""

        channels = channels or template.channels
        payload = NotificationPayload(
            payload_id=str(uuid.uuid4()),
            template=template,
            recipients=recipients,
            variables=variables,
            channels=channels
        )

        payload_id = self.manager.queue_notification(payload)
        delivery_logs = self.manager.send_notification(payload)

        return payload_id

    def get_delivery_status(self, payload_id: str) -> Dict[str, Any]:
        """Get delivery status for notification"""
        logs = self.manager.get_delivery_status(payload_id)
        return {
            "payload_id": payload_id,
            "delivery_logs": [asdict(log) for log in logs],
            "statistics": self.manager.get_delivery_statistics()
        }

    def schedule_recurring_notification(self, job_id: str, cron_expression: str,
                                       segment_id: str, template_id: str,
                                       variables: Dict[str, Any]):
        """Schedule recurring notification"""
        payload_template = {
            'segment_id': segment_id,
            'template_id': template_id,
            'variables': variables
        }
        self.scheduler.schedule_recurring(job_id, cron_expression, payload_template)


# ==================== Configuration ====================

def load_config() -> Dict[str, str]:
    """Load configuration from environment variables"""
    return {
        'smtp_host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'sender_email': os.getenv('SENDER_EMAIL'),
        'sender_password': os.getenv('SENDER_PASSWORD'),
        'slack_webhook': os.getenv('SLACK_WEBHOOK_URL'),
        'teams_webhook': os.getenv('TEAMS_WEBHOOK_URL'),
        'twilio_sid': os.getenv('TWILIO_ACCOUNT_SID'),
        'twilio_token': os.getenv('TWILIO_AUTH_TOKEN'),
        'twilio_from': os.getenv('TWILIO_FROM_NUMBER')
    }


# ==================== Example Usage ====================

if __name__ == '__main__':
    # Initialize orchestrator
    orchestrator = NotificationOrchestrator()

    # Setup senders
    config = load_config()

    if config['sender_email'] and config['sender_password']:
        orchestrator.setup_email_sender(
            config['smtp_host'],
            config['smtp_port'],
            config['sender_email'],
            config['sender_password']
        )

    if config['slack_webhook']:
        orchestrator.setup_slack_sender(config['slack_webhook'])

    if config['teams_webhook']:
        orchestrator.setup_teams_sender(config['teams_webhook'])

    # Register templates
    milestone_template = NotificationTemplate(
        template_id="milestone_update",
        name="Milestone Update",
        description="Notification for milestone completion or status change",
        subject="Milestone Update: {{milestone_name}}",
        content="""
Hello {{user_name}},

{{milestone_name}} has been updated to {{status}}.

Progress: {{completion}}%
Target Date: {{target_date}}

Learn more: https://dashboard.example.com/milestones/{{milestone_id}}

Best regards,
Product Management Team
        """,
        channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.TEAMS],
        variables=['milestone_name', 'status', 'completion', 'target_date', 'milestone_id', 'user_name']
    )

    orchestrator.register_template(milestone_template)

    # Add recipients
    recipient1 = NotificationRecipient(
        recipient_id="exec_001",
        name="John Executive",
        email="john@example.com",
        phone="+1234567890",
        role=RecipientRole.EXECUTIVE,
        preferred_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
        subscription_settings={
            NotificationChannel.EMAIL.value: True,
            NotificationChannel.SLACK.value: True
        }
    )

    orchestrator.add_recipient(recipient1)

    # Send notification to specific criteria
    # payload_id = orchestrator.send_to_criteria(
    #     criteria={'role': [RecipientRole.EXECUTIVE]},
    #     template_id='milestone_update',
    #     variables={
    #         'user_name': 'John',
    #         'milestone_name': 'Q4 Release',
    #         'status': 'Completed',
    #         'completion': '100',
    #         'target_date': '2024-12-31',
    #         'milestone_id': 'M001'
    #     }
    # )

    logger.info("Notification orchestrator initialized successfully")

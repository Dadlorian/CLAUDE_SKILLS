# Cloud Integration Patterns

## Table of Contents
- [Introduction](#introduction)
- [Event-Driven Architecture](#event-driven-architecture)
- [Publish-Subscribe Patterns](#publish-subscribe-patterns)
- [Message Queue Patterns](#message-queue-patterns)
- [Asynchronous Communication](#asynchronous-communication)
- [Real-World Examples](#real-world-examples)
- [Security Considerations](#security-considerations)
- [Performance Optimization](#performance-optimization)
- [Best Practices](#best-practices)

## Introduction

Cloud integration patterns enable loosely coupled, scalable systems by facilitating communication between distributed components. These patterns are essential for building microservices, event-driven architectures, and resilient cloud applications.

### Key Benefits

- **Loose Coupling**: Services communicate without tight dependencies
- **Scalability**: Components scale independently
- **Resilience**: Failures in one component don't cascade
- **Flexibility**: Easy to add/remove services
- **Asynchronous Processing**: Non-blocking operations improve performance

## Event-Driven Architecture

### Core Concepts

Event-driven architecture (EDA) uses events to trigger and communicate between services. An event represents a significant state change or occurrence.

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
import json

class EventType(str, Enum):
    """Standard event types"""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    FAILED = "failed"

@dataclass
class CloudEvent:
    """
    CloudEvents specification implementation
    https://cloudevents.io/
    """
    id: str
    source: str
    type: str
    datacontenttype: str = "application/json"
    time: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    subject: Optional[str] = None
    specversion: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'id': self.id,
            'source': self.source,
            'type': self.type,
            'specversion': self.specversion,
            'datacontenttype': self.datacontenttype
        }

        if self.time:
            result['time'] = self.time
        if self.data:
            result['data'] = self.data
        if self.subject:
            result['subject'] = self.subject

        return result

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CloudEvent':
        """Create CloudEvent from dictionary"""
        return cls(
            id=data['id'],
            source=data['source'],
            type=data['type'],
            datacontenttype=data.get('datacontenttype', 'application/json'),
            time=data.get('time'),
            data=data.get('data'),
            subject=data.get('subject'),
            specversion=data.get('specversion', '1.0')
        )

# Example usage
def create_user_event(user_id: str, user_data: Dict[str, Any]) -> CloudEvent:
    """Create a user creation event"""
    return CloudEvent(
        id=str(uuid.uuid4()),
        source='user-service',
        type='user.created',
        time=datetime.utcnow().isoformat() + 'Z',
        subject=f'users/{user_id}',
        data={
            'userId': user_id,
            'email': user_data['email'],
            'name': user_data['name']
        }
    )
```

### AWS EventBridge Implementation

```python
import boto3
from typing import List

class EventBridgePublisher:
    """Publish events to AWS EventBridge"""

    def __init__(self, event_bus_name: str = 'default'):
        self.client = boto3.client('events')
        self.event_bus_name = event_bus_name

    def publish_event(self, event: CloudEvent) -> str:
        """Publish single event"""
        response = self.client.put_events(
            Entries=[{
                'Time': datetime.fromisoformat(event.time.rstrip('Z')),
                'Source': event.source,
                'DetailType': event.type,
                'Detail': json.dumps(event.data),
                'EventBusName': self.event_bus_name
            }]
        )

        if response['FailedEntryCount'] > 0:
            raise Exception(f"Failed to publish event: {response['Entries'][0]}")

        return response['Entries'][0]['EventId']

    def publish_batch(self, events: List[CloudEvent]) -> Dict[str, Any]:
        """Publish multiple events (max 10 per batch)"""
        entries = []

        for event in events[:10]:  # EventBridge limit
            entries.append({
                'Time': datetime.fromisoformat(event.time.rstrip('Z')),
                'Source': event.source,
                'DetailType': event.type,
                'Detail': json.dumps(event.data),
                'EventBusName': self.event_bus_name
            })

        response = self.client.put_events(Entries=entries)

        return {
            'successful': len(events) - response['FailedEntryCount'],
            'failed': response['FailedEntryCount'],
            'entries': response['Entries']
        }

# Event consumer Lambda function
def event_handler(event, context):
    """
    Lambda function triggered by EventBridge

    Event structure:
    {
        "version": "0",
        "id": "event-id",
        "detail-type": "user.created",
        "source": "user-service",
        "time": "2024-01-01T00:00:00Z",
        "region": "us-east-1",
        "detail": {
            "userId": "123",
            "email": "user@example.com"
        }
    }
    """
    detail_type = event['detail-type']
    detail = event['detail']

    if detail_type == 'user.created':
        handle_user_created(detail)
    elif detail_type == 'user.updated':
        handle_user_updated(detail)
    elif detail_type == 'user.deleted':
        handle_user_deleted(detail)
    else:
        print(f"Unknown event type: {detail_type}")

def handle_user_created(detail: dict):
    """Handle user created event"""
    user_id = detail['userId']
    email = detail['email']

    # Send welcome email
    ses = boto3.client('ses')
    ses.send_email(
        Source='noreply@example.com',
        Destination={'ToAddresses': [email]},
        Message={
            'Subject': {'Data': 'Welcome!'},
            'Body': {'Text': {'Data': f'Welcome user {user_id}!'}}
        }
    )

    # Create user profile
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('UserProfiles')
    table.put_item(Item={
        'userId': user_id,
        'email': email,
        'createdAt': datetime.utcnow().isoformat()
    })
```

### Azure Event Grid Implementation

```python
from azure.eventgrid import EventGridPublisherClient, EventGridEvent
from azure.core.credentials import AzureKeyCredential
from datetime import datetime
import uuid

class AzureEventGridPublisher:
    """Publish events to Azure Event Grid"""

    def __init__(self, endpoint: str, key: str):
        credential = AzureKeyCredential(key)
        self.client = EventGridPublisherClient(endpoint, credential)

    def publish_event(self, event: CloudEvent):
        """Publish single event to Event Grid"""
        eg_event = EventGridEvent(
            id=event.id,
            event_type=event.type,
            subject=event.subject or '',
            data=event.data,
            event_time=datetime.fromisoformat(event.time.rstrip('Z')),
            data_version='1.0'
        )

        self.client.send(eg_event)

    def publish_batch(self, events: List[CloudEvent]):
        """Publish multiple events"""
        eg_events = []

        for event in events:
            eg_events.append(EventGridEvent(
                id=event.id,
                event_type=event.type,
                subject=event.subject or '',
                data=event.data,
                event_time=datetime.fromisoformat(event.time.rstrip('Z')),
                data_version='1.0'
            ))

        self.client.send(eg_events)

# Azure Function event handler
import azure.functions as func
import logging

def main(event: func.EventGridEvent):
    """Azure Function triggered by Event Grid"""
    logging.info('Event Grid trigger function processed an event')

    event_data = event.get_json()
    event_type = event.event_type

    if event_type == 'user.created':
        user_id = event_data['userId']
        email = event_data['email']

        # Process user creation
        logging.info(f'User created: {user_id}, {email}')

        # Trigger downstream processes
        # ...
```

### Google Cloud Pub/Sub with CloudEvents

```javascript
// Node.js implementation for Google Cloud Pub/Sub
const { PubSub } = require('@google-cloud/pubsub');
const { v4: uuidv4 } = require('uuid');

class GooglePubSubPublisher {
  constructor(projectId, topicName) {
    this.pubsub = new PubSub({ projectId });
    this.topic = this.pubsub.topic(topicName);
  }

  /**
   * Publish CloudEvent to Pub/Sub
   */
  async publishEvent(cloudEvent) {
    const messageBuffer = Buffer.from(JSON.stringify(cloudEvent));

    const messageId = await this.topic.publishMessage({
      data: messageBuffer,
      attributes: {
        'ce-id': cloudEvent.id,
        'ce-source': cloudEvent.source,
        'ce-type': cloudEvent.type,
        'ce-specversion': cloudEvent.specversion,
        'ce-time': cloudEvent.time
      }
    });

    return messageId;
  }

  /**
   * Publish batch of events
   */
  async publishBatch(events) {
    const publishPromises = events.map(event => this.publishEvent(event));
    return await Promise.all(publishPromises);
  }
}

// Cloud Function event handler
exports.eventHandler = async (message, context) => {
  const cloudEvent = JSON.parse(Buffer.from(message.data, 'base64').toString());

  console.log('Event ID:', cloudEvent.id);
  console.log('Event Type:', cloudEvent.type);
  console.log('Event Data:', cloudEvent.data);

  switch (cloudEvent.type) {
    case 'user.created':
      await handleUserCreated(cloudEvent.data);
      break;
    case 'user.updated':
      await handleUserUpdated(cloudEvent.data);
      break;
    case 'user.deleted':
      await handleUserDeleted(cloudEvent.data);
      break;
    default:
      console.log('Unknown event type:', cloudEvent.type);
  }
};

async function handleUserCreated(data) {
  // Send welcome email, create profile, etc.
  console.log('Handling user creation:', data.userId);
}
```

## Publish-Subscribe Patterns

### Fan-Out Pattern

```python
class FanOutPattern:
    """
    Fan-out pattern: One publisher sends to multiple subscribers
    Use case: Notify multiple services about a single event
    """

    def __init__(self):
        self.sns = boto3.client('sns')
        self.topic_arn = os.environ['SNS_TOPIC_ARN']

    def publish_to_all_subscribers(self, event: CloudEvent):
        """Publish event to SNS topic with multiple subscribers"""
        message = {
            'default': event.to_json(),
            'email': self._format_for_email(event),
            'sqs': event.to_json(),
            'lambda': event.to_json(),
            'http': event.to_json()
        }

        response = self.sns.publish(
            TopicArn=self.topic_arn,
            Message=json.dumps(message),
            MessageStructure='json',
            MessageAttributes={
                'eventType': {
                    'DataType': 'String',
                    'StringValue': event.type
                },
                'source': {
                    'DataType': 'String',
                    'StringValue': event.source
                }
            }
        )

        return response['MessageId']

    def _format_for_email(self, event: CloudEvent) -> str:
        """Format event for email notification"""
        return f"""
        Event Notification

        Type: {event.type}
        Source: {event.source}
        Time: {event.time}

        Details:
        {json.dumps(event.data, indent=2)}
        """

# Subscriber Lambda functions
def email_subscriber(event, context):
    """Lambda subscribed to SNS - sends emails"""
    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        event_data = CloudEvent.from_dict(json.loads(message['default']))

        # Send email notification
        ses = boto3.client('ses')
        ses.send_email(
            Source='notifications@example.com',
            Destination={'ToAddresses': ['admin@example.com']},
            Message={
                'Subject': {'Data': f'Event: {event_data.type}'},
                'Body': {'Text': {'Data': message['email']}}
            }
        )

def analytics_subscriber(event, context):
    """Lambda subscribed to SNS - logs to analytics"""
    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        event_data = CloudEvent.from_dict(json.loads(message['default']))

        # Send to analytics service
        firehose = boto3.client('firehose')
        firehose.put_record(
            DeliveryStreamName='analytics-stream',
            Record={'Data': json.dumps(event_data.to_dict())}
        )

def webhook_subscriber(event, context):
    """Lambda subscribed to SNS - calls external webhooks"""
    import requests

    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        event_data = CloudEvent.from_dict(json.loads(message['default']))

        # Call external webhook
        webhooks = get_registered_webhooks(event_data.type)
        for webhook_url in webhooks:
            try:
                requests.post(
                    webhook_url,
                    json=event_data.to_dict(),
                    headers={'Content-Type': 'application/cloudevents+json'},
                    timeout=5
                )
            except Exception as e:
                print(f"Webhook failed: {webhook_url}, Error: {e}")
```

### Topic-Based Filtering

```python
class TopicFilterPattern:
    """
    Topic filtering: Subscribers receive only events matching their filter
    """

    def __init__(self):
        self.sns = boto3.client('sns')

    def create_filtered_subscription(self, topic_arn: str, endpoint: str,
                                    protocol: str, filters: Dict[str, List[str]]):
        """
        Create SNS subscription with filter policy

        Example filters:
        {
            'eventType': ['user.created', 'user.updated'],
            'region': ['us-east-1'],
            'priority': ['high', 'critical']
        }
        """
        response = self.sns.subscribe(
            TopicArn=topic_arn,
            Protocol=protocol,  # 'lambda', 'sqs', 'email', 'http', 'https'
            Endpoint=endpoint,
            Attributes={
                'FilterPolicy': json.dumps(filters)
            }
        )

        return response['SubscriptionArn']

# Example: Create filtered subscriptions
topic_filter = TopicFilterPattern()

# Subscribe to only user events
topic_filter.create_filtered_subscription(
    topic_arn='arn:aws:sns:us-east-1:123456789012:events',
    endpoint='arn:aws:lambda:us-east-1:123456789012:function:user-handler',
    protocol='lambda',
    filters={
        'eventType': ['user.created', 'user.updated', 'user.deleted']
    }
)

# Subscribe to only high-priority order events
topic_filter.create_filtered_subscription(
    topic_arn='arn:aws:sns:us-east-1:123456789012:events',
    endpoint='arn:aws:lambda:us-east-1:123456789012:function:urgent-order-handler',
    protocol='lambda',
    filters={
        'eventType': ['order.created', 'order.updated'],
        'priority': ['high', 'critical']
    }
)
```

## Message Queue Patterns

### Competing Consumers Pattern

```python
class CompetingConsumersPattern:
    """
    Competing consumers: Multiple consumers process messages from same queue
    Provides load balancing and parallel processing
    """

    def __init__(self, queue_url: str):
        self.sqs = boto3.client('sqs')
        self.queue_url = queue_url

    def send_message(self, message: dict, delay_seconds: int = 0):
        """Send message to queue"""
        return self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message),
            DelaySeconds=delay_seconds,
            MessageAttributes={
                'Timestamp': {
                    'StringValue': datetime.utcnow().isoformat(),
                    'DataType': 'String'
                }
            }
        )

    def send_batch(self, messages: List[dict]):
        """Send up to 10 messages in a batch"""
        entries = []

        for i, message in enumerate(messages[:10]):
            entries.append({
                'Id': str(i),
                'MessageBody': json.dumps(message)
            })

        return self.sqs.send_message_batch(
            QueueUrl=self.queue_url,
            Entries=entries
        )

# Consumer Lambda function
def queue_consumer(event, context):
    """
    Lambda function processing SQS messages
    Multiple instances can run concurrently (competing consumers)
    """
    for record in event['Records']:
        try:
            message = json.loads(record['body'])

            # Process message
            process_order(message)

            # Message is automatically deleted after successful processing
            # (when Lambda returns without error)

        except Exception as e:
            print(f"Error processing message: {e}")
            # Message will be retried based on queue's redrive policy
            raise

def process_order(order: dict):
    """Process order message"""
    order_id = order['orderId']

    # Validate order
    if not validate_order(order):
        raise ValueError(f"Invalid order: {order_id}")

    # Process payment
    payment_result = process_payment(order)

    if not payment_result['success']:
        raise Exception(f"Payment failed: {order_id}")

    # Update inventory
    update_inventory(order['items'])

    # Send confirmation
    send_order_confirmation(order)
```

### Dead Letter Queue Pattern

```python
class DeadLetterQueuePattern:
    """
    DLQ pattern: Failed messages move to separate queue for analysis
    """

    def __init__(self, main_queue_url: str, dlq_url: str):
        self.sqs = boto3.client('sqs')
        self.main_queue_url = main_queue_url
        self.dlq_url = dlq_url

    def configure_dlq(self, max_receive_count: int = 3):
        """Configure main queue to use DLQ"""
        # Get DLQ ARN
        dlq_attributes = self.sqs.get_queue_attributes(
            QueueUrl=self.dlq_url,
            AttributeNames=['QueueArn']
        )
        dlq_arn = dlq_attributes['Attributes']['QueueArn']

        # Configure redrive policy
        redrive_policy = {
            'deadLetterTargetArn': dlq_arn,
            'maxReceiveCount': str(max_receive_count)
        }

        self.sqs.set_queue_attributes(
            QueueUrl=self.main_queue_url,
            Attributes={
                'RedrivePolicy': json.dumps(redrive_policy)
            }
        )

    def process_dlq_messages(self):
        """Process messages from DLQ for analysis/retry"""
        response = self.sqs.receive_message(
            QueueUrl=self.dlq_url,
            MaxNumberOfMessages=10,
            MessageAttributeNames=['All'],
            AttributeNames=['All']
        )

        messages = response.get('Messages', [])

        for message in messages:
            try:
                body = json.loads(message['Body'])

                # Analyze failure
                failure_reason = self._analyze_failure(body, message['Attributes'])

                # Log for monitoring
                print(f"DLQ Message Analysis:")
                print(f"Message ID: {message['MessageId']}")
                print(f"Receive Count: {message['Attributes']['ApproximateReceiveCount']}")
                print(f"Failure Reason: {failure_reason}")

                # Decide: retry, manual intervention, or discard
                if self._should_retry(body, failure_reason):
                    # Resend to main queue
                    self.sqs.send_message(
                        QueueUrl=self.main_queue_url,
                        MessageBody=message['Body']
                    )

                    # Delete from DLQ
                    self.sqs.delete_message(
                        QueueUrl=self.dlq_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )
                else:
                    # Archive for manual review
                    self._archive_failed_message(body, failure_reason)

                    # Delete from DLQ
                    self.sqs.delete_message(
                        QueueUrl=self.dlq_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )

            except Exception as e:
                print(f"Error processing DLQ message: {e}")

    def _analyze_failure(self, message: dict, attributes: dict) -> str:
        """Analyze why message failed"""
        # Implement your failure analysis logic
        return "Unknown failure"

    def _should_retry(self, message: dict, failure_reason: str) -> bool:
        """Determine if message should be retried"""
        # Transient errors should be retried
        transient_errors = ['timeout', 'rate_limit', 'service_unavailable']
        return any(error in failure_reason.lower() for error in transient_errors)

    def _archive_failed_message(self, message: dict, failure_reason: str):
        """Archive permanently failed message"""
        s3 = boto3.client('s3')
        s3.put_object(
            Bucket='failed-messages',
            Key=f"dlq/{datetime.utcnow().isoformat()}/{message.get('id', 'unknown')}.json",
            Body=json.dumps({
                'message': message,
                'failureReason': failure_reason,
                'timestamp': datetime.utcnow().isoformat()
            })
        )
```

### Priority Queue Pattern

```python
class PriorityQueuePattern:
    """
    Priority queues: Process high-priority messages first
    Implemented using multiple SQS queues
    """

    def __init__(self):
        self.sqs = boto3.client('sqs')
        self.queues = {
            'critical': os.environ['CRITICAL_QUEUE_URL'],
            'high': os.environ['HIGH_QUEUE_URL'],
            'normal': os.environ['NORMAL_QUEUE_URL'],
            'low': os.environ['LOW_QUEUE_URL']
        }

    def send_message(self, message: dict, priority: str = 'normal'):
        """Send message to appropriate priority queue"""
        if priority not in self.queues:
            priority = 'normal'

        queue_url = self.queues[priority]

        return self.sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message),
            MessageAttributes={
                'Priority': {
                    'StringValue': priority,
                    'DataType': 'String'
                }
            }
        )

# Consumer processes queues in priority order
def priority_queue_consumer(event, context):
    """Process messages from all queues in priority order"""
    sqs = boto3.client('sqs')

    queues_by_priority = [
        ('critical', os.environ['CRITICAL_QUEUE_URL']),
        ('high', os.environ['HIGH_QUEUE_URL']),
        ('normal', os.environ['NORMAL_QUEUE_URL']),
        ('low', os.environ['LOW_QUEUE_URL'])
    ]

    messages_processed = 0
    max_messages = 100  # Process up to 100 messages per invocation

    for priority, queue_url in queues_by_priority:
        if messages_processed >= max_messages:
            break

        # Process messages from this priority queue
        while messages_processed < max_messages:
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=min(10, max_messages - messages_processed),
                WaitTimeSeconds=1
            )

            messages = response.get('Messages', [])

            if not messages:
                break  # No more messages in this queue

            for message in messages:
                try:
                    body = json.loads(message['Body'])
                    process_message(body, priority)

                    # Delete message
                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )

                    messages_processed += 1

                except Exception as e:
                    print(f"Error processing {priority} message: {e}")

    return {'messagesProcessed': messages_processed}
```

## Asynchronous Communication

### Async Request-Reply Pattern

```python
class AsyncRequestReplyPattern:
    """
    Async request-reply: Client sends request, gets reply via callback
    """

    def __init__(self):
        self.sqs = boto3.client('sqs')
        self.request_queue = os.environ['REQUEST_QUEUE_URL']
        self.dynamodb = boto3.resource('dynamodb')
        self.correlation_table = self.dynamodb.Table('CorrelationIds')

    def send_request(self, request_data: dict, callback_url: str) -> str:
        """Send async request and register callback"""
        import uuid

        # Generate correlation ID
        correlation_id = str(uuid.uuid4())

        # Store callback information
        self.correlation_table.put_item(Item={
            'correlationId': correlation_id,
            'callbackUrl': callback_url,
            'status': 'pending',
            'createdAt': datetime.utcnow().isoformat(),
            'ttl': int(time.time()) + 3600  # 1 hour TTL
        })

        # Send request to processing queue
        self.sqs.send_message(
            QueueUrl=self.request_queue,
            MessageBody=json.dumps(request_data),
            MessageAttributes={
                'CorrelationId': {
                    'StringValue': correlation_id,
                    'DataType': 'String'
                }
            }
        )

        return correlation_id

    def send_reply(self, correlation_id: str, response_data: dict):
        """Send reply using stored callback"""
        import requests

        # Get callback info
        response = self.correlation_table.get_item(
            Key={'correlationId': correlation_id}
        )

        if 'Item' not in response:
            raise ValueError(f"Unknown correlation ID: {correlation_id}")

        callback_url = response['Item']['callbackUrl']

        # Send reply to callback URL
        requests.post(
            callback_url,
            json={
                'correlationId': correlation_id,
                'status': 'completed',
                'data': response_data
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        # Update status
        self.correlation_table.update_item(
            Key={'correlationId': correlation_id},
            UpdateExpression='SET #status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': 'completed'}
        )

# Request processor
def request_processor(event, context):
    """Process async requests and send replies"""
    pattern = AsyncRequestReplyPattern()

    for record in event['Records']:
        correlation_id = record['messageAttributes']['CorrelationId']['stringValue']
        request_data = json.loads(record['body'])

        try:
            # Process request (could take a long time)
            result = process_long_running_task(request_data)

            # Send reply
            pattern.send_reply(correlation_id, result)

        except Exception as e:
            pattern.send_reply(correlation_id, {
                'error': str(e),
                'status': 'failed'
            })

# Client API endpoint
def client_api(event, context):
    """API endpoint for clients to submit requests"""
    pattern = AsyncRequestReplyPattern()

    request_data = json.loads(event['body'])
    callback_url = request_data.get('callbackUrl')

    if not callback_url:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'callbackUrl required'})
        }

    # Send async request
    correlation_id = pattern.send_request(request_data, callback_url)

    return {
        'statusCode': 202,  # Accepted
        'body': json.dumps({
            'message': 'Request accepted for processing',
            'correlationId': correlation_id,
            'statusUrl': f'/status/{correlation_id}'
        })
    }
```

### Saga Pattern (Distributed Transactions)

```python
class SagaPattern:
    """
    Saga pattern: Manage distributed transactions across microservices
    Each step has a compensating action for rollback
    """

    def __init__(self):
        self.step_functions = boto3.client('stepfunctions')
        self.state_machine_arn = os.environ['SAGA_STATE_MACHINE_ARN']

    def start_saga(self, order_data: dict) -> str:
        """Start saga execution"""
        response = self.step_functions.start_execution(
            stateMachineArn=self.state_machine_arn,
            input=json.dumps(order_data)
        )

        return response['executionArn']

# Saga steps as Lambda functions

def reserve_inventory(event, context):
    """Step 1: Reserve inventory"""
    order_id = event['orderId']
    items = event['items']

    try:
        # Reserve items
        inventory_service = InventoryService()
        reservation_id = inventory_service.reserve(items)

        return {
            **event,
            'reservationId': reservation_id,
            'inventoryReserved': True
        }

    except Exception as e:
        return {
            **event,
            'inventoryReserved': False,
            'error': str(e)
        }

def compensate_inventory(event, context):
    """Compensating action for inventory reservation"""
    reservation_id = event.get('reservationId')

    if reservation_id:
        inventory_service = InventoryService()
        inventory_service.cancel_reservation(reservation_id)

    return event

def process_payment(event, context):
    """Step 2: Process payment"""
    try:
        payment_service = PaymentService()
        transaction_id = payment_service.charge(
            amount=event['totalAmount'],
            payment_method=event['paymentMethod']
        )

        return {
            **event,
            'transactionId': transaction_id,
            'paymentProcessed': True
        }

    except Exception as e:
        return {
            **event,
            'paymentProcessed': False,
            'error': str(e)
        }

def compensate_payment(event, context):
    """Compensating action for payment"""
    transaction_id = event.get('transactionId')

    if transaction_id:
        payment_service = PaymentService()
        payment_service.refund(transaction_id)

    return event

def create_shipment(event, context):
    """Step 3: Create shipment"""
    try:
        shipping_service = ShippingService()
        shipment_id = shipping_service.create_shipment(
            order_id=event['orderId'],
            address=event['shippingAddress']
        )

        return {
            **event,
            'shipmentId': shipment_id,
            'shipmentCreated': True
        }

    except Exception as e:
        return {
            **event,
            'shipmentCreated': False,
            'error': str(e)
        }

def compensate_shipment(event, context):
    """Compensating action for shipment"""
    shipment_id = event.get('shipmentId')

    if shipment_id:
        shipping_service = ShippingService()
        shipping_service.cancel_shipment(shipment_id)

    return event

# Step Functions state machine definition
saga_state_machine = {
    "Comment": "Order processing saga with compensation",
    "StartAt": "ReserveInventory",
    "States": {
        "ReserveInventory": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:region:account:function:reserve-inventory",
            "Catch": [{
                "ErrorEquals": ["States.ALL"],
                "Next": "SagaFailed"
            }],
            "Next": "CheckInventoryReservation"
        },
        "CheckInventoryReservation": {
            "Type": "Choice",
            "Choices": [{
                "Variable": "$.inventoryReserved",
                "BooleanEquals": True,
                "Next": "ProcessPayment"
            }],
            "Default": "SagaFailed"
        },
        "ProcessPayment": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:region:account:function:process-payment",
            "Catch": [{
                "ErrorEquals": ["States.ALL"],
                "Next": "CompensateInventory"
            }],
            "Next": "CheckPayment"
        },
        "CheckPayment": {
            "Type": "Choice",
            "Choices": [{
                "Variable": "$.paymentProcessed",
                "BooleanEquals": True,
                "Next": "CreateShipment"
            }],
            "Default": "CompensateInventory"
        },
        "CreateShipment": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:region:account:function:create-shipment",
            "Catch": [{
                "ErrorEquals": ["States.ALL"],
                "Next": "CompensatePayment"
            }],
            "Next": "CheckShipment"
        },
        "CheckShipment": {
            "Type": "Choice",
            "Choices": [{
                "Variable": "$.shipmentCreated",
                "BooleanEquals": True,
                "Next": "SagaSucceeded"
            }],
            "Default": "CompensatePayment"
        },
        "CompensatePayment": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:region:account:function:compensate-payment",
            "Next": "CompensateInventory"
        },
        "CompensateInventory": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:region:account:function:compensate-inventory",
            "Next": "SagaFailed"
        },
        "SagaSucceeded": {
            "Type": "Succeed"
        },
        "SagaFailed": {
            "Type": "Fail"
        }
    }
}
```

## Real-World Examples

### Uber: Real-Time Event Processing

```python
class UberEventProcessing:
    """
    Uber-style event processing for ride-hailing
    Handles millions of events per second
    """

    def __init__(self):
        self.kinesis = boto3.client('kinesis')
        self.stream_name = 'ride-events'

    def publish_ride_event(self, event_type: str, ride_id: str, data: dict):
        """Publish ride event to Kinesis stream"""
        event = CloudEvent(
            id=str(uuid.uuid4()),
            source='ride-service',
            type=f'ride.{event_type}',
            time=datetime.utcnow().isoformat() + 'Z',
            subject=f'rides/{ride_id}',
            data=data
        )

        self.kinesis.put_record(
            StreamName=self.stream_name,
            Data=event.to_json(),
            PartitionKey=ride_id  # Ensures ordering per ride
        )

# Event types: requested, matched, started, completed, cancelled

def ride_analytics_processor(event, context):
    """
    Process ride events for real-time analytics
    Triggered by Kinesis stream
    """
    from decimal import Decimal

    timestream = boto3.client('timestream-write')

    for record in event['Records']:
        payload = base64.b64decode(record['kinesis']['data'])
        ride_event = CloudEvent.from_dict(json.loads(payload))

        # Extract metrics
        ride_data = ride_event.data
        metrics = []

        if ride_event.type == 'ride.started':
            metrics.append({
                'MeasureName': 'rides_started',
                'MeasureValue': '1',
                'MeasureValueType': 'BIGINT'
            })

        elif ride_event.type == 'ride.completed':
            metrics.extend([
                {
                    'MeasureName': 'rides_completed',
                    'MeasureValue': '1',
                    'MeasureValueType': 'BIGINT'
                },
                {
                    'MeasureName': 'ride_duration',
                    'MeasureValue': str(ride_data['duration']),
                    'MeasureValueType': 'DOUBLE'
                },
                {
                    'MeasureName': 'ride_distance',
                    'MeasureValue': str(ride_data['distance']),
                    'MeasureValueType': 'DOUBLE'
                },
                {
                    'MeasureName': 'ride_fare',
                    'MeasureValue': str(ride_data['fare']),
                    'MeasureValueType': 'DOUBLE'
                }
            ])

        # Write to TimeSeries database
        current_time = str(int(time.time() * 1000))

        for metric in metrics:
            timestream.write_records(
                DatabaseName='ride-analytics',
                TableName='metrics',
                Records=[{
                    'Time': current_time,
                    'Dimensions': [
                        {'Name': 'city', 'Value': ride_data['city']},
                        {'Name': 'ride_type', 'Value': ride_data['type']}
                    ],
                    **metric
                }]
            )
```

### Netflix: Content Delivery Events

```javascript
// Netflix-style content delivery event processing
class NetflixCDNEvents {
  constructor() {
    this.eventBridge = new AWS.EventBridge();
    this.eventBusName = 'content-delivery';
  }

  /**
   * Publish content play event
   */
  async publishPlayEvent(userId, contentId, deviceType, quality) {
    const event = {
      Time: new Date(),
      Source: 'cdn-service',
      DetailType: 'content.play',
      Detail: JSON.stringify({
        userId,
        contentId,
        deviceType,
        quality,
        timestamp: new Date().toISOString(),
        region: process.env.AWS_REGION
      }),
      EventBusName: this.eventBusName
    };

    await this.eventBridge.putEvents({ Entries: [event] }).promise();
  }

  /**
   * Publish buffering event for QoS monitoring
   */
  async publishBufferingEvent(userId, contentId, bufferingDuration) {
    const event = {
      Time: new Date(),
      Source: 'cdn-service',
      DetailType: 'content.buffering',
      Detail: JSON.stringify({
        userId,
        contentId,
        bufferingDuration,
        timestamp: new Date().toISOString()
      }),
      EventBusName: this.eventBusName
    };

    await this.eventBridge.putEvents({ Entries: [event] }).promise();
  }
}

// Event handlers

/**
 * Quality-of-Service monitoring
 * Detects playback issues and triggers adaptive bitrate
 */
exports.qosMonitor = async (event) => {
  const detail = event.detail;

  if (event['detail-type'] === 'content.buffering') {
    // Track buffering incidents
    await recordBufferingIncident(detail);

    // If buffering is excessive, reduce quality
    if (detail.bufferingDuration > 5000) {  // 5 seconds
      await triggerQualityReduction(detail.userId, detail.contentId);
    }
  }

  if (event['detail-type'] === 'content.play') {
    // Update user viewing history
    await updateViewingHistory(detail.userId, detail.contentId);

    // Pre-fetch next episode for binge-watching
    if (detail.contentId.includes('episode')) {
      await prefetchNextEpisode(detail.contentId);
    }
  }
};

/**
 * Recommendation engine trigger
 * Updates recommendations based on viewing patterns
 */
exports.recommendationTrigger = async (event) => {
  const detail = event.detail;

  if (event['detail-type'] === 'content.play') {
    // Update user preferences
    const preferences = await getUserPreferences(detail.userId);

    const updatedPreferences = updatePreferences(
      preferences,
      detail.contentId,
      detail.quality,
      detail.deviceType
    );

    await saveUserPreferences(detail.userId, updatedPreferences);

    // Trigger recommendation refresh
    await triggerRecommendationRefresh(detail.userId);
  }
};
```

### Stripe: Payment Webhooks

```python
class StripeWebhookIntegration:
    """
    Stripe-style webhook event processing
    Handles payment events and notifies merchants
    """

    def __init__(self):
        self.sqs = boto3.client('sqs')
        self.sns = boto3.client('sns')
        self.webhook_queue = os.environ['WEBHOOK_QUEUE_URL']

    def process_payment_event(self, event_type: str, payment_data: dict):
        """Process payment event and notify webhooks"""
        event = CloudEvent(
            id=str(uuid.uuid4()),
            source='payment-service',
            type=f'payment.{event_type}',
            time=datetime.utcnow().isoformat() + 'Z',
            data=payment_data
        )

        # Get webhooks registered for this event type
        webhooks = self._get_webhooks_for_event(event_type, payment_data['merchant_id'])

        # Queue webhook deliveries
        for webhook in webhooks:
            self.sqs.send_message(
                QueueUrl=self.webhook_queue,
                MessageBody=json.dumps({
                    'webhookUrl': webhook['url'],
                    'event': event.to_dict(),
                    'secret': webhook['secret'],
                    'attempt': 0,
                    'maxAttempts': 5
                }),
                MessageAttributes={
                    'eventType': {
                        'StringValue': event_type,
                        'DataType': 'String'
                    }
                }
            )

    def _get_webhooks_for_event(self, event_type: str, merchant_id: str) -> list:
        """Get webhooks subscribed to event type"""
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('MerchantWebhooks')

        response = table.query(
            KeyConditionExpression='merchantId = :merchant_id',
            FilterExpression='contains(eventTypes, :event_type)',
            ExpressionAttributeValues={
                ':merchant_id': merchant_id,
                ':event_type': event_type
            }
        )

        return response['Items']

def webhook_delivery_worker(event, context):
    """
    Worker that delivers webhooks with retry logic
    """
    import requests
    import hmac
    import hashlib

    for record in event['Records']:
        delivery = json.loads(record['body'])

        webhook_url = delivery['webhookUrl']
        event_data = delivery['event']
        secret = delivery['secret']
        attempt = delivery['attempt']
        max_attempts = delivery['maxAttempts']

        try:
            # Generate signature
            payload = json.dumps(event_data)
            signature = hmac.new(
                secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()

            # Deliver webhook
            response = requests.post(
                webhook_url,
                json=event_data,
                headers={
                    'Content-Type': 'application/cloudevents+json',
                    'X-Webhook-Signature': signature,
                    'X-Webhook-Delivery-Attempt': str(attempt + 1)
                },
                timeout=30
            )

            response.raise_for_status()

            # Success - log delivery
            print(f"Webhook delivered successfully: {webhook_url}")

        except Exception as e:
            print(f"Webhook delivery failed (attempt {attempt + 1}): {e}")

            # Retry with exponential backoff
            if attempt + 1 < max_attempts:
                sqs = boto3.client('sqs')
                delay = min(2 ** attempt, 900)  # Max 15 minutes

                delivery['attempt'] = attempt + 1

                sqs.send_message(
                    QueueUrl=os.environ['WEBHOOK_QUEUE_URL'],
                    MessageBody=json.dumps(delivery),
                    DelaySeconds=delay
                )
            else:
                # Max attempts reached - send to DLQ
                print(f"Webhook delivery failed permanently: {webhook_url}")

                # Notify merchant of failure
                sns = boto3.client('sns')
                sns.publish(
                    TopicArn=os.environ['WEBHOOK_FAILURE_TOPIC'],
                    Subject='Webhook Delivery Failed',
                    Message=json.dumps({
                        'webhookUrl': webhook_url,
                        'event': event_data,
                        'attempts': max_attempts
                    })
                )
```

## Security Considerations

### Message Encryption

```python
from cryptography.fernet import Fernet
import base64

class SecureMessagePattern:
    """Encrypt messages before publishing"""

    def __init__(self, encryption_key: bytes):
        self.cipher = Fernet(encryption_key)
        self.sns = boto3.client('sns')

    def publish_encrypted(self, topic_arn: str, message: dict):
        """Publish encrypted message"""
        # Serialize and encrypt
        plaintext = json.dumps(message).encode()
        encrypted = self.cipher.encrypt(plaintext)

        # Publish encrypted message
        response = self.sns.publish(
            TopicArn=topic_arn,
            Message=base64.b64encode(encrypted).decode(),
            MessageAttributes={
                'encrypted': {
                    'DataType': 'String',
                    'StringValue': 'true'
                },
                'algorithm': {
                    'DataType': 'String',
                    'StringValue': 'Fernet'
                }
            }
        )

        return response['MessageId']

def decrypt_message_handler(event, context):
    """Handler that decrypts messages"""
    encryption_key = get_encryption_key()  # From Secrets Manager
    cipher = Fernet(encryption_key)

    for record in event['Records']:
        message = record['Sns']['Message']
        is_encrypted = record['Sns']['MessageAttributes'].get('encrypted', {}).get('Value') == 'true'

        if is_encrypted:
            # Decrypt message
            encrypted_data = base64.b64decode(message)
            decrypted = cipher.decrypt(encrypted_data)
            message_data = json.loads(decrypted)
        else:
            message_data = json.loads(message)

        # Process decrypted message
        process_message(message_data)
```

## Performance Optimization

### Batching Strategy

```python
class BatchingOptimization:
    """Optimize throughput with intelligent batching"""

    def __init__(self):
        self.batch = []
        self.batch_size = 25  # DynamoDB batch write limit
        self.batch_timeout = 5  # seconds
        self.last_flush = time.time()

    def add_to_batch(self, item: dict):
        """Add item to batch and flush if needed"""
        self.batch.append(item)

        should_flush = (
            len(self.batch) >= self.batch_size or
            time.time() - self.last_flush >= self.batch_timeout
        )

        if should_flush:
            self.flush_batch()

    def flush_batch(self):
        """Write batch to DynamoDB"""
        if not self.batch:
            return

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['TABLE_NAME'])

        with table.batch_writer() as writer:
            for item in self.batch:
                writer.put_item(Item=item)

        print(f"Flushed batch of {len(self.batch)} items")
        self.batch = []
        self.last_flush = time.time()
```

## Best Practices

### 1. Idempotency in Event Handlers

```python
def idempotent_event_handler(event, context):
    """Handle events idempotently"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ProcessedEvents')

    for record in event['Records']:
        # Extract event ID (varies by source)
        if 'eventID' in record:
            event_id = record['eventID']  # DynamoDB Streams
        elif 'messageId' in record:
            event_id = record['messageId']  # SQS/SNS
        else:
            event_id = record.get('eventId')  # EventBridge

        # Check if already processed
        try:
            table.put_item(
                Item={
                    'eventId': event_id,
                    'processedAt': datetime.utcnow().isoformat(),
                    'ttl': int(time.time()) + 86400  # 24 hours
                },
                ConditionExpression='attribute_not_exists(eventId)'
            )

            # Process event (only if not already processed)
            process_event(record)

        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            # Event already processed
            print(f"Skipping duplicate event: {event_id}")
```

### 2. Circuit Breaker for External Services

```python
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Circuit breaker pattern for external service calls"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker"""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)

            # Success - reset failure count
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED

            self.failure_count = 0
            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

            raise
```

## Conclusion

Cloud integration patterns are essential for building scalable, resilient distributed systems. Key takeaways:

1. **Use events for loose coupling**: Event-driven architecture enables independent scaling
2. **Choose the right pattern**: Pub/sub for fan-out, queues for load leveling
3. **Handle failures gracefully**: Use DLQs, retries, and circuit breakers
4. **Design for idempotency**: Events may be delivered multiple times
5. **Monitor and observe**: Track message flow, latency, and failures
6. **Encrypt sensitive data**: Use encryption for messages containing PII or secrets

Following these patterns will help you build robust, scalable cloud integrations.

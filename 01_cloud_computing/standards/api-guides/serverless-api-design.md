# Serverless API Design

## Table of Contents
- [Introduction](#introduction)
- [Serverless Architecture Patterns](#serverless-architecture-patterns)
- [API Gateway Design](#api-gateway-design)
- [Function Design Patterns](#function-design-patterns)
- [State Management](#state-management)
- [Real-World Examples](#real-world-examples)
- [Security Considerations](#security-considerations)
- [Performance Optimization](#performance-optimization)
- [Cost Optimization](#cost-optimization)
- [Best Practices](#best-practices)

## Introduction

Serverless APIs leverage managed compute services (AWS Lambda, Azure Functions, Google Cloud Functions) and API gateways to build scalable, cost-effective applications without managing infrastructure. This guide covers patterns, best practices, and real-world implementations.

### Benefits of Serverless APIs

- **Auto-scaling**: Automatic scaling from zero to thousands of concurrent executions
- **Pay-per-use**: Only pay for actual compute time
- **Reduced operational overhead**: No server management or patching
- **High availability**: Built-in redundancy and fault tolerance
- **Faster time to market**: Focus on code, not infrastructure

### When to Use Serverless

**Good Use Cases:**
- Event-driven applications
- APIs with variable traffic
- Microservices architectures
- Webhooks and integrations
- Backend for mobile/web apps

**Consider Alternatives When:**
- Predictable, high-volume traffic (containers may be cheaper)
- Long-running processes (>15 minutes)
- Require persistent connections
- Need very low latency (<10ms)

## Serverless Architecture Patterns

### 1. API Gateway + Lambda Pattern

```python
# AWS Lambda handler with API Gateway integration
import json
import boto3
from datetime import datetime
from typing import Dict, Any
import os

# Initialize AWS clients outside handler for connection reuse
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda function handler for API Gateway proxy integration.

    Event structure from API Gateway:
    {
        "httpMethod": "GET|POST|PUT|DELETE",
        "path": "/resource/{id}",
        "pathParameters": {"id": "123"},
        "queryStringParameters": {"filter": "active"},
        "headers": {...},
        "body": "...",
        "requestContext": {...}
    }
    """

    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }

    try:
        # Handle preflight OPTIONS request
        if event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }

        # Route based on HTTP method and path
        route_key = f"{event['httpMethod']} {event['resource']}"

        router = {
            'GET /users': list_users,
            'GET /users/{id}': get_user,
            'POST /users': create_user,
            'PUT /users/{id}': update_user,
            'DELETE /users/{id}': delete_user
        }

        handler = router.get(route_key)

        if not handler:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Route not found'})
            }

        # Execute handler
        result = handler(event, context)

        return {
            'statusCode': result.get('statusCode', 200),
            'headers': headers,
            'body': json.dumps(result.get('body', {}))
        }

    except Exception as e:
        print(f"Error: {str(e)}")  # CloudWatch logs
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'requestId': context.request_id
            })
        }

def list_users(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """List all users with pagination"""
    query_params = event.get('queryStringParameters') or {}
    limit = int(query_params.get('limit', 20))
    last_key = query_params.get('lastKey')

    scan_kwargs = {
        'Limit': limit
    }

    if last_key:
        scan_kwargs['ExclusiveStartKey'] = {'id': last_key}

    response = table.scan(**scan_kwargs)

    return {
        'statusCode': 200,
        'body': {
            'users': response['Items'],
            'lastKey': response.get('LastEvaluatedKey', {}).get('id'),
            'count': len(response['Items'])
        }
    }

def get_user(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Get single user by ID"""
    user_id = event['pathParameters']['id']

    response = table.get_item(Key={'id': user_id})

    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': {'error': 'User not found'}
        }

    return {
        'statusCode': 200,
        'body': {'user': response['Item']}
    }

def create_user(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Create new user"""
    body = json.loads(event['body'])

    # Validate input
    required_fields = ['name', 'email']
    for field in required_fields:
        if field not in body:
            return {
                'statusCode': 400,
                'body': {'error': f'Missing required field: {field}'}
            }

    # Generate unique ID
    import uuid
    user_id = str(uuid.uuid4())

    user = {
        'id': user_id,
        'name': body['name'],
        'email': body['email'],
        'createdAt': datetime.utcnow().isoformat(),
        'updatedAt': datetime.utcnow().isoformat()
    }

    table.put_item(Item=user)

    return {
        'statusCode': 201,
        'body': {'user': user}
    }

def update_user(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Update existing user"""
    user_id = event['pathParameters']['id']
    body = json.loads(event['body'])

    # Build update expression dynamically
    update_expression = "SET updatedAt = :updatedAt"
    expression_values = {':updatedAt': datetime.utcnow().isoformat()}

    if 'name' in body:
        update_expression += ", #name = :name"
        expression_values[':name'] = body['name']

    if 'email' in body:
        update_expression += ", email = :email"
        expression_values[':email'] = body['email']

    expression_names = {'#name': 'name'} if 'name' in body else None

    response = table.update_item(
        Key={'id': user_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ExpressionAttributeNames=expression_names,
        ReturnValues='ALL_NEW'
    )

    return {
        'statusCode': 200,
        'body': {'user': response['Attributes']}
    }

def delete_user(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Delete user"""
    user_id = event['pathParameters']['id']

    table.delete_item(Key={'id': user_id})

    return {
        'statusCode': 204,
        'body': {}
    }
```

### 2. Azure Functions HTTP Trigger

```python
import azure.functions as func
import logging
import json
from typing import Dict, Any
import os
from azure.cosmos import CosmosClient

# Initialize Cosmos DB client
cosmos_client = CosmosClient.from_connection_string(
    os.environ['COSMOS_CONNECTION_STRING']
)
database = cosmos_client.get_database_client(os.environ['DATABASE_NAME'])
container = database.get_container_client('users')

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function HTTP trigger"""

    logging.info('Processing HTTP request')

    # Get request method and route
    method = req.method
    route = req.route_params.get('route', '')

    try:
        if method == 'GET' and not route:
            # List users
            users = list(container.read_all_items())
            return func.HttpResponse(
                json.dumps({'users': users}),
                mimetype='application/json',
                status_code=200
            )

        elif method == 'GET' and route:
            # Get specific user
            user = container.read_item(item=route, partition_key=route)
            return func.HttpResponse(
                json.dumps({'user': user}),
                mimetype='application/json',
                status_code=200
            )

        elif method == 'POST':
            # Create user
            body = req.get_json()

            if not body.get('name') or not body.get('email'):
                return func.HttpResponse(
                    json.dumps({'error': 'Name and email are required'}),
                    mimetype='application/json',
                    status_code=400
                )

            import uuid
            user = {
                'id': str(uuid.uuid4()),
                'name': body['name'],
                'email': body['email']
            }

            container.create_item(body=user)

            return func.HttpResponse(
                json.dumps({'user': user}),
                mimetype='application/json',
                status_code=201
            )

        elif method == 'PUT' and route:
            # Update user
            body = req.get_json()
            user = container.read_item(item=route, partition_key=route)

            user.update(body)
            container.replace_item(item=route, body=user)

            return func.HttpResponse(
                json.dumps({'user': user}),
                mimetype='application/json',
                status_code=200
            )

        elif method == 'DELETE' and route:
            # Delete user
            container.delete_item(item=route, partition_key=route)

            return func.HttpResponse(
                status_code=204
            )

        else:
            return func.HttpResponse(
                json.dumps({'error': 'Method not allowed'}),
                mimetype='application/json',
                status_code=405
            )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            mimetype='application/json',
            status_code=500
        )
```

### 3. Google Cloud Functions

```javascript
// Node.js Cloud Function
const { Firestore } = require('@google-cloud/firestore');

const firestore = new Firestore();
const COLLECTION = 'users';

/**
 * HTTP Cloud Function for user management
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.userApi = async (req, res) => {
  // Set CORS headers
  res.set('Access-Control-Allow-Origin', '*');
  res.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle preflight
  if (req.method === 'OPTIONS') {
    res.status(204).send('');
    return;
  }

  try {
    const { method, path } = req;
    const pathParts = path.split('/').filter(p => p);
    const userId = pathParts[1];

    switch (method) {
      case 'GET':
        if (userId) {
          // Get single user
          const userDoc = await firestore.collection(COLLECTION).doc(userId).get();

          if (!userDoc.exists) {
            res.status(404).json({ error: 'User not found' });
            return;
          }

          res.status(200).json({
            user: { id: userDoc.id, ...userDoc.data() }
          });
        } else {
          // List all users
          const snapshot = await firestore.collection(COLLECTION).limit(20).get();
          const users = snapshot.docs.map(doc => ({
            id: doc.id,
            ...doc.data()
          }));

          res.status(200).json({ users, count: users.length });
        }
        break;

      case 'POST':
        // Create user
        const { name, email } = req.body;

        if (!name || !email) {
          res.status(400).json({ error: 'Name and email are required' });
          return;
        }

        const newUser = {
          name,
          email,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        };

        const docRef = await firestore.collection(COLLECTION).add(newUser);

        res.status(201).json({
          user: { id: docRef.id, ...newUser }
        });
        break;

      case 'PUT':
        // Update user
        if (!userId) {
          res.status(400).json({ error: 'User ID is required' });
          return;
        }

        const updateData = {
          ...req.body,
          updatedAt: new Date().toISOString()
        };

        await firestore.collection(COLLECTION).doc(userId).update(updateData);

        const updatedDoc = await firestore.collection(COLLECTION).doc(userId).get();

        res.status(200).json({
          user: { id: updatedDoc.id, ...updatedDoc.data() }
        });
        break;

      case 'DELETE':
        // Delete user
        if (!userId) {
          res.status(400).json({ error: 'User ID is required' });
          return;
        }

        await firestore.collection(COLLECTION).doc(userId).delete();
        res.status(204).send('');
        break;

      default:
        res.status(405).json({ error: 'Method not allowed' });
    }
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
};
```

## API Gateway Design

### AWS API Gateway Configuration

```yaml
# SAM (Serverless Application Model) template
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Timeout: 30
    Runtime: python3.11
    Environment:
      Variables:
        DYNAMODB_TABLE: !Ref UsersTable
        LOG_LEVEL: INFO

Resources:
  UserApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,Authorization'"
        AllowOrigin: "'*'"
      Auth:
        DefaultAuthorizer: CognitoAuthorizer
        Authorizers:
          CognitoAuthorizer:
            UserPoolArn: !GetAtt UserPool.Arn
      GatewayResponses:
        DEFAULT_4XX:
          ResponseParameters:
            Headers:
              Access-Control-Allow-Origin: "'*'"
        DEFAULT_5XX:
          ResponseParameters:
            Headers:
              Access-Control-Allow-Origin: "'*'"
      MethodSettings:
        - ResourcePath: '/*'
          HttpMethod: '*'
          ThrottlingBurstLimit: 5000
          ThrottlingRateLimit: 2000
          LoggingLevel: INFO
          DataTraceEnabled: true
          MetricsEnabled: true

  UserFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: users.lambda_handler
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref UsersTable
      Events:
        ListUsers:
          Type: Api
          Properties:
            RestApiId: !Ref UserApi
            Path: /users
            Method: GET
        GetUser:
          Type: Api
          Properties:
            RestApiId: !Ref UserApi
            Path: /users/{id}
            Method: GET
        CreateUser:
          Type: Api
          Properties:
            RestApiId: !Ref UserApi
            Path: /users
            Method: POST
        UpdateUser:
          Type: Api
          Properties:
            RestApiId: !Ref UserApi
            Path: /users/{id}
            Method: PUT
        DeleteUser:
          Type: Api
          Properties:
            RestApiId: !Ref UserApi
            Path: /users/{id}
            Method: DELETE

  UsersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: users
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH
      BillingMode: PAY_PER_REQUEST
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES

  UserPool:
    Type: AWS::Cognito::UserPool
    Properties:
      UserPoolName: user-api-pool
      AutoVerifiedAttributes:
        - email
      Schema:
        - Name: email
          Required: true
          Mutable: false

Outputs:
  ApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub 'https://${UserApi}.execute-api.${AWS::Region}.amazonaws.com/prod'
```

### Request/Response Transformation

```python
# Lambda middleware pattern for request/response transformation
from functools import wraps
import json
from typing import Callable, Any

def api_gateway_middleware(func: Callable) -> Callable:
    """Middleware to handle API Gateway integration"""

    @wraps(func)
    def wrapper(event: dict, context: Any) -> dict:
        # Parse request body
        if event.get('body'):
            try:
                event['parsedBody'] = json.loads(event['body'])
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Invalid JSON in request body'})
                }

        # Add request context
        event['requestContext'] = {
            'requestId': context.request_id,
            'functionName': context.function_name,
            'functionVersion': context.function_version,
            **event.get('requestContext', {})
        }

        try:
            # Call actual handler
            result = func(event, context)

            # Ensure proper response format
            if isinstance(result, dict) and 'statusCode' in result:
                return result

            # Auto-format successful responses
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'X-Request-Id': context.request_id
                },
                'body': json.dumps(result)
            }

        except Exception as e:
            # Error handling
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Internal server error',
                    'message': str(e),
                    'requestId': context.request_id
                })
            }

    return wrapper

# Usage
@api_gateway_middleware
def my_handler(event, context):
    body = event['parsedBody']
    return {'message': 'Success', 'data': body}
```

## Function Design Patterns

### 1. Single Responsibility Functions

```python
# Good: Each function has a single responsibility
def validate_user_input(data: dict) -> tuple[bool, str]:
    """Validate user input data"""
    required_fields = ['name', 'email']

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    if '@' not in data['email']:
        return False, "Invalid email format"

    return True, ""

def persist_user(user_data: dict) -> str:
    """Persist user to database"""
    table.put_item(Item=user_data)
    return user_data['id']

def send_welcome_email(user_email: str, user_name: str):
    """Send welcome email to new user"""
    ses = boto3.client('ses')
    ses.send_email(
        Source='noreply@example.com',
        Destination={'ToAddresses': [user_email]},
        Message={
            'Subject': {'Data': 'Welcome!'},
            'Body': {'Text': {'Data': f'Welcome {user_name}!'}}
        }
    )

def create_user_handler(event, context):
    """Main handler orchestrates the workflow"""
    data = json.loads(event['body'])

    # Validate
    is_valid, error = validate_user_input(data)
    if not is_valid:
        return {'statusCode': 400, 'body': json.dumps({'error': error})}

    # Create user
    user = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'email': data['email'],
        'createdAt': datetime.utcnow().isoformat()
    }

    # Persist
    user_id = persist_user(user)

    # Send welcome email (async via SQS to avoid blocking)
    sqs = boto3.client('sqs')
    sqs.send_message(
        QueueUrl=os.environ['WELCOME_EMAIL_QUEUE'],
        MessageBody=json.dumps({'email': user['email'], 'name': user['name']})
    )

    return {'statusCode': 201, 'body': json.dumps({'user': user})}
```

### 2. Lambda Layers for Shared Code

```python
# Layer structure:
# /opt/python/shared/
#   ├── database.py
#   ├── validators.py
#   └── utils.py

# database.py (in Lambda Layer)
import boto3
import os

class Database:
    """Shared database utilities"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.dynamodb = boto3.resource('dynamodb')
            cls._instance.table = cls._instance.dynamodb.Table(
                os.environ['DYNAMODB_TABLE']
            )
        return cls._instance

    def get_item(self, key: dict) -> dict:
        response = self.table.get_item(Key=key)
        return response.get('Item')

    def put_item(self, item: dict):
        self.table.put_item(Item=item)

    def query(self, **kwargs):
        return self.table.query(**kwargs)

# Function using the layer
from shared.database import Database

def lambda_handler(event, context):
    db = Database()
    user = db.get_item({'id': event['pathParameters']['id']})
    return {'statusCode': 200, 'body': json.dumps(user)}
```

### 3. Event-Driven Function Composition

```python
# Pattern: Chain functions via events

# Function 1: Image Upload Handler
def image_upload_handler(event, context):
    """Triggered by S3 upload event"""
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Publish event for processing
        sns = boto3.client('sns')
        sns.publish(
            TopicArn=os.environ['IMAGE_PROCESSING_TOPIC'],
            Message=json.dumps({
                'bucket': bucket,
                'key': key,
                'operation': 'resize',
                'sizes': ['thumbnail', 'medium', 'large']
            })
        )

# Function 2: Image Processing Handler
def image_processing_handler(event, context):
    """Triggered by SNS notification"""
    from PIL import Image
    import io

    message = json.loads(event['Records'][0]['Sns']['Message'])

    s3 = boto3.client('s3')

    # Download original image
    obj = s3.get_object(Bucket=message['bucket'], Key=message['key'])
    image = Image.open(io.BytesIO(obj['Body'].read()))

    # Process for each size
    sizes = {
        'thumbnail': (150, 150),
        'medium': (800, 800),
        'large': (1920, 1920)
    }

    for size_name, dimensions in sizes.items():
        resized = image.copy()
        resized.thumbnail(dimensions)

        buffer = io.BytesIO()
        resized.save(buffer, format='JPEG')
        buffer.seek(0)

        # Upload resized image
        new_key = f"processed/{size_name}/{message['key']}"
        s3.put_object(
            Bucket=message['bucket'],
            Key=new_key,
            Body=buffer,
            ContentType='image/jpeg'
        )

    # Publish completion event
    eventbridge = boto3.client('events')
    eventbridge.put_events(
        Entries=[{
            'Source': 'image.processing',
            'DetailType': 'ImageProcessed',
            'Detail': json.dumps({
                'originalKey': message['key'],
                'bucket': message['bucket'],
                'sizes': list(sizes.keys())
            })
        }]
    )

# Function 3: Notification Handler
def notification_handler(event, context):
    """Triggered by EventBridge when image processing completes"""
    detail = event['detail']

    # Send notification to user
    ses = boto3.client('ses')
    ses.send_email(
        Source='noreply@example.com',
        Destination={'ToAddresses': ['user@example.com']},
        Message={
            'Subject': {'Data': 'Image Processing Complete'},
            'Body': {
                'Text': {
                    'Data': f"Your image {detail['originalKey']} has been processed!"
                }
            }
        }
    )
```

## State Management

### Using Step Functions for Orchestration

```json
{
  "Comment": "Order processing workflow",
  "StartAt": "ValidateOrder",
  "States": {
    "ValidateOrder": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:validate-order",
      "Next": "CheckInventory",
      "Catch": [{
        "ErrorEquals": ["ValidationError"],
        "Next": "OrderValidationFailed"
      }]
    },
    "CheckInventory": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:check-inventory",
      "Next": "ProcessPayment",
      "Catch": [{
        "ErrorEquals": ["OutOfStock"],
        "Next": "OutOfStockNotification"
      }]
    },
    "ProcessPayment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:process-payment",
      "Next": "CreateShipment",
      "Retry": [{
        "ErrorEquals": ["PaymentGatewayError"],
        "IntervalSeconds": 2,
        "MaxAttempts": 3,
        "BackoffRate": 2.0
      }],
      "Catch": [{
        "ErrorEquals": ["PaymentFailed"],
        "Next": "PaymentFailedNotification"
      }]
    },
    "CreateShipment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:create-shipment",
      "Next": "SendConfirmation"
    },
    "SendConfirmation": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:send-confirmation",
      "End": true
    },
    "OrderValidationFailed": {
      "Type": "Fail",
      "Error": "OrderValidationFailed",
      "Cause": "Order validation failed"
    },
    "OutOfStockNotification": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:notify-out-of-stock",
      "End": true
    },
    "PaymentFailedNotification": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:notify-payment-failed",
      "End": true
    }
  }
}
```

## Real-World Examples

### Netflix: API Gateway at Scale

Netflix processes millions of API requests per second using serverless:

```python
# Inspired by Netflix's API gateway pattern
class NetflixStyleGateway:
    """
    Netflix-style API gateway that handles:
    - Request routing
    - Authentication/authorization
    - Rate limiting
    - Circuit breaking
    - Response aggregation
    """

    def __init__(self):
        self.circuit_breakers = {}
        self.rate_limiters = {}

    def handle_request(self, event, context):
        """Main request handler"""
        user_id = self.authenticate_request(event)

        if not user_id:
            return {'statusCode': 401, 'body': json.dumps({'error': 'Unauthorized'})}

        # Check rate limit
        if not self.check_rate_limit(user_id):
            return {'statusCode': 429, 'body': json.dumps({'error': 'Rate limit exceeded'})}

        # Route request
        endpoint = event['path']

        if endpoint.startswith('/api/v1/videos'):
            return self.handle_video_request(event, user_id)
        elif endpoint.startswith('/api/v1/recommendations'):
            return self.handle_recommendations(event, user_id)
        else:
            return {'statusCode': 404, 'body': json.dumps({'error': 'Not found'})}

    def authenticate_request(self, event) -> str:
        """Authenticate using JWT token"""
        import jwt

        auth_header = event['headers'].get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header[7:]

        try:
            payload = jwt.decode(token, os.environ['JWT_SECRET'], algorithms=['HS256'])
            return payload['user_id']
        except jwt.InvalidTokenError:
            return None

    def check_rate_limit(self, user_id: str) -> bool:
        """Check rate limit using DynamoDB"""
        from datetime import datetime, timedelta

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('rate_limits')

        current_minute = datetime.utcnow().replace(second=0, microsecond=0)
        key = f"{user_id}:{current_minute.isoformat()}"

        try:
            response = table.update_item(
                Key={'id': key},
                UpdateExpression='ADD request_count :inc',
                ExpressionAttributeValues={':inc': 1},
                ReturnValues='UPDATED_NEW'
            )

            count = response['Attributes']['request_count']
            return count <= 1000  # 1000 requests per minute

        except:
            return True  # Allow on error

    def handle_video_request(self, event, user_id):
        """Handle video-related requests with circuit breaker"""
        service_name = 'video-service'

        if self.is_circuit_open(service_name):
            # Fallback response
            return {
                'statusCode': 503,
                'body': json.dumps({'error': 'Service temporarily unavailable'})
            }

        try:
            # Call video microservice
            response = self.call_microservice(service_name, event)
            self.record_success(service_name)
            return response

        except Exception as e:
            self.record_failure(service_name)
            raise

    def is_circuit_open(self, service_name: str) -> bool:
        """Check if circuit breaker is open"""
        breaker = self.circuit_breakers.get(service_name, {'failures': 0, 'last_failure': None})
        return breaker['failures'] >= 5

    def record_failure(self, service_name: str):
        """Record service failure"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = {'failures': 0, 'last_failure': None}

        self.circuit_breakers[service_name]['failures'] += 1
        self.circuit_breakers[service_name]['last_failure'] = datetime.utcnow()

    def call_microservice(self, service_name: str, event: dict) -> dict:
        """Call downstream microservice"""
        # Implementation would call actual microservice
        pass
```

### Uber: Real-Time Event Processing

```javascript
// Uber-style real-time ride matching
exports.rideMatchingFunction = async (event) => {
  // Triggered by Kinesis stream of ride requests

  for (const record of event.Records) {
    const rideRequest = JSON.parse(
      Buffer.from(record.kinesis.data, 'base64').toString()
    );

    console.log('Processing ride request:', rideRequest.id);

    try {
      // Find nearby drivers (geospatial query)
      const nearbyDrivers = await findNearbyDrivers(
        rideRequest.pickupLocation,
        5000 // 5km radius
      );

      if (nearbyDrivers.length === 0) {
        await sendNoDriversNotification(rideRequest.userId);
        continue;
      }

      // Calculate ETAs for all drivers
      const driversWithETA = await Promise.all(
        nearbyDrivers.map(async (driver) => ({
          ...driver,
          eta: await calculateETA(driver.location, rideRequest.pickupLocation)
        }))
      );

      // Sort by ETA
      driversWithETA.sort((a, b) => a.eta - b.eta);

      // Send match requests to top 3 drivers
      const matchPromises = driversWithETA.slice(0, 3).map((driver) =>
        sendMatchRequest(driver.id, rideRequest)
      );

      await Promise.all(matchPromises);

      // Store pending match
      await storePendingMatch({
        rideRequestId: rideRequest.id,
        candidates: driversWithETA.slice(0, 3).map(d => d.id),
        expiresAt: Date.now() + 30000 // 30 seconds
      });

    } catch (error) {
      console.error('Error processing ride request:', error);

      // Publish to DLQ for retry
      await publishToDLQ(record);
    }
  }
};

async function findNearbyDrivers(location, radiusMeters) {
  const { DynamoDB } = require('aws-sdk');
  const ddb = new DynamoDB.DocumentClient();

  // Using geohash for spatial queries
  const geohashes = generateGeohashesInRadius(location, radiusMeters);

  const queryPromises = geohashes.map(hash =>
    ddb.query({
      TableName: 'Drivers',
      IndexName: 'GeohashIndex',
      KeyConditionExpression: 'geohash = :hash AND #status = :status',
      ExpressionAttributeNames: {
        '#status': 'status'
      },
      ExpressionAttributeValues: {
        ':hash': hash,
        ':status': 'available'
      }
    }).promise()
  );

  const results = await Promise.all(queryPromises);

  return results.flatMap(r => r.Items);
}
```

## Security Considerations

### 1. Authentication & Authorization

```python
# Custom Lambda authorizer for API Gateway
def lambda_authorizer(event, context):
    """
    Custom authorizer for API Gateway.
    Returns IAM policy allowing/denying access.
    """
    token = event['authorizationToken']  # Bearer token from header
    method_arn = event['methodArn']

    try:
        # Validate token (example with JWT)
        import jwt

        payload = jwt.decode(
            token.replace('Bearer ', ''),
            os.environ['JWT_SECRET'],
            algorithms=['HS256']
        )

        user_id = payload['sub']
        roles = payload.get('roles', [])

        # Generate IAM policy
        policy = generate_policy(user_id, 'Allow', method_arn, roles)

        # Add user context for downstream functions
        policy['context'] = {
            'userId': user_id,
            'email': payload.get('email'),
            'roles': ','.join(roles)
        }

        return policy

    except jwt.InvalidTokenError:
        # Deny access
        return generate_policy('user', 'Deny', method_arn)

def generate_policy(principal_id, effect, resource, roles=None):
    """Generate IAM policy document"""
    policy = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        }
    }

    # Add resource-based restrictions
    if roles and 'admin' not in roles:
        # Non-admin users can only access their own resources
        policy['policyDocument']['Statement'][0]['Condition'] = {
            'StringEquals': {
                'api:userId': principal_id
            }
        }

    return policy
```

### 2. Input Validation

```python
from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class CreateUserRequest(BaseModel):
    """Request model with validation"""
    name: str
    email: EmailStr
    age: Optional[int] = None

    @validator('name')
    def name_must_be_valid(cls, v):
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters')
        if not v.replace(' ', '').isalpha():
            raise ValueError('Name must contain only letters')
        return v

    @validator('age')
    def age_must_be_valid(cls, v):
        if v is not None and (v < 0 or v > 150):
            raise ValueError('Age must be between 0 and 150')
        return v

def create_user_handler(event, context):
    """Handler with input validation"""
    try:
        body = json.loads(event['body'])

        # Validate using Pydantic
        request = CreateUserRequest(**body)

        # Process validated data
        user = {
            'id': str(uuid.uuid4()),
            'name': request.name,
            'email': request.email,
            'age': request.age
        }

        # Save to database
        table.put_item(Item=user)

        return {
            'statusCode': 201,
            'body': json.dumps({'user': user})
        }

    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON'})
        }
    except ValueError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
```

## Performance Optimization

### 1. Connection Reuse

```python
# Initialize clients OUTSIDE handler function for reuse
import boto3

# These connections are reused across invocations
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
secrets_client = boto3.client('secretsmanager')

# Load secrets once at cold start
SECRETS_CACHE = None

def get_secrets():
    """Cache secrets across invocations"""
    global SECRETS_CACHE

    if SECRETS_CACHE is None:
        response = secrets_client.get_secret_value(
            SecretId=os.environ['SECRET_NAME']
        )
        SECRETS_CACHE = json.loads(response['SecretString'])

    return SECRETS_CACHE

def lambda_handler(event, context):
    """Handler reuses connections and cached secrets"""
    secrets = get_secrets()
    table = dynamodb.Table(os.environ['TABLE_NAME'])

    # Use cached resources
    # ...
```

### 2. Provisioned Concurrency

```yaml
# SAM template with provisioned concurrency
Resources:
  HighTrafficFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: app.handler
      Runtime: python3.11
      AutoPublishAlias: live
      ProvisionedConcurrencyConfig:
        ProvisionedConcurrentExecutions: 10  # Always keep 10 warm instances
```

### 3. Parallel Processing

```python
import asyncio
import aiohttp

async def fetch_user_data(user_id: str, session: aiohttp.ClientSession) -> dict:
    """Fetch user data from external API"""
    async with session.get(f'https://api.example.com/users/{user_id}') as response:
        return await response.json()

async def process_batch(user_ids: list[str]) -> list[dict]:
    """Process multiple users in parallel"""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_user_data(user_id, session) for user_id in user_ids]
        return await asyncio.gather(*tasks)

def lambda_handler(event, context):
    """Handler using async for parallel processing"""
    user_ids = event['userIds']

    # Run async code in Lambda
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(process_batch(user_ids))

    return {
        'statusCode': 200,
        'body': json.dumps({'users': results})
    }
```

## Cost Optimization

### 1. Right-Size Memory Allocation

```python
# Use AWS Lambda Power Tuning tool results
# Test showed optimal memory: 512MB (best price/performance)

# CloudFormation snippet
Resources:
  OptimizedFunction:
    Type: AWS::Serverless::Function
    Properties:
      MemorySize: 512  # Optimized based on testing
      Timeout: 10
```

### 2. Batch Processing

```python
def sqs_batch_handler(event, context):
    """Process SQS messages in batches"""
    records = event['Records']

    # Process in batches of 25 (DynamoDB batch write limit)
    batch_size = 25

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]

        # Batch write to DynamoDB
        with dynamodb.batch_writer() as writer:
            for record in batch:
                message = json.loads(record['body'])
                writer.put_item(Item=message)

    return {'statusCode': 200, 'processedCount': len(records)}
```

## Best Practices

### 1. Idempotency

```python
def idempotent_handler(event, context):
    """Handler with idempotency"""
    idempotency_key = event['headers'].get('Idempotency-Key')

    if not idempotency_key:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Idempotency-Key header required'})
        }

    # Check if request already processed
    response = table.get_item(Key={'idempotency_key': idempotency_key})

    if 'Item' in response:
        # Return cached response
        return response['Item']['response']

    # Process request
    result = process_request(event)

    # Cache response
    table.put_item(Item={
        'idempotency_key': idempotency_key,
        'response': result,
        'ttl': int(time.time()) + 86400  # 24 hours
    })

    return result
```

### 2. Error Handling & Retries

```python
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import SQSEvent

logger = Logger()
tracer = Tracer()

@tracer.capture_lambda_handler
@logger.inject_lambda_context
def handler(event: dict, context: LambdaContext) -> dict:
    """Handler with proper error handling"""

    try:
        sqs_event = SQSEvent(event)

        for record in sqs_event.records:
            try:
                process_message(record.body)

            except Exception as e:
                logger.error(f"Failed to process message: {record.message_id}",
                           extra={'error': str(e), 'message_id': record.message_id})

                # Message will be retried automatically by SQS
                raise

        return {'statusCode': 200}

    except Exception as e:
        logger.exception("Handler failed")
        raise

@tracer.capture_method
def process_message(message_body: str):
    """Process individual message"""
    data = json.loads(message_body)
    # Processing logic
```

### 3. Monitoring & Observability

```python
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit

logger = Logger()
tracer = Tracer()
metrics = Metrics()

@metrics.log_metrics(capture_cold_start_metric=True)
@tracer.capture_lambda_handler
@logger.inject_lambda_context
def handler(event, context):
    """Handler with comprehensive observability"""

    # Add custom metrics
    metrics.add_metric(name="UserCreated", unit=MetricUnit.Count, value=1)
    metrics.add_dimension(name="Environment", value=os.environ.get('STAGE', 'dev'))

    # Structured logging
    logger.info("Processing user creation", extra={
        'user_id': event.get('userId'),
        'source': event.get('source')
    })

    # Distributed tracing
    with tracer.provider.in_subsegment("database_operation") as subsegment:
        subsegment.put_annotation("user_id", event.get('userId'))
        result = table.put_item(Item=event)

    return {'statusCode': 200, 'body': json.dumps(result)}
```

## Conclusion

Serverless API design requires different thinking than traditional server-based architectures. Key principles:

1. **Design for statelessness**: Each invocation is independent
2. **Optimize cold starts**: Use provisioned concurrency for critical paths
3. **Embrace event-driven**: Use events to decouple components
4. **Monitor aggressively**: Distributed systems require comprehensive observability
5. **Cost-optimize continuously**: Right-size memory, use batching, implement caching
6. **Security by default**: Validate all inputs, use least-privilege IAM, encrypt data

Following these patterns and best practices will help you build scalable, cost-effective serverless APIs.

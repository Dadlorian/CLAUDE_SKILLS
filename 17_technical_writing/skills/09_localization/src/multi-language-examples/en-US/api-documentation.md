# CloudSync Pro API Documentation

## Overview

The CloudSync Pro API allows developers to integrate CloudSync Pro functionality into custom applications. The API is RESTful and uses JSON for request and response bodies.

## Base URL

```
https://api.cloudsync.com/v1
```

## Authentication

All API requests require an authentication token. Include your token in the Authorization header:

```
Authorization: Bearer YOUR_API_TOKEN
```

To obtain an API token:
1. Log in to CloudSync Pro
2. Navigate to Settings > Developer > API Tokens
3. Click "Generate New Token"
4. Copy the token (you'll only see it once)

## API Endpoints

### 1. Files

#### Get File List

```
GET /files
```

Returns a list of files in your CloudSync Pro account.

**Parameters:**
- `folder_id` (optional): Filter by folder ID
- `limit` (optional): Number of results (default: 50, max: 1000)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "file_12345",
      "name": "document.pdf",
      "size": 2048576,
      "created": "2024-11-19T10:30:00Z",
      "modified": "2024-11-19T14:45:00Z",
      "owner": "user@example.com",
      "shared": false
    }
  ],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 150
  }
}
```

#### Upload File

```
POST /files/upload
```

Upload a new file to CloudSync Pro.

**Request Headers:**
```
Content-Type: multipart/form-data
```

**Form Data:**
- `file` (required): File to upload
- `folder_id` (required): Target folder ID
- `name` (optional): Custom filename

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "file_12346",
    "name": "new-document.pdf",
    "size": 3145728,
    "url": "https://files.cloudsync.com/file_12346",
    "created": "2024-11-19T15:20:00Z"
  }
}
```

#### Delete File

```
DELETE /files/{file_id}
```

Delete a file from CloudSync Pro.

**Response:**
```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

### 2. Folders

#### Create Folder

```
POST /folders
```

Create a new folder in CloudSync Pro.

**Request Body:**
```json
{
  "name": "Project A",
  "parent_id": "folder_789",
  "description": "Files for Project A"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "folder_990",
    "name": "Project A",
    "parent_id": "folder_789",
    "created": "2024-11-19T15:30:00Z",
    "owner": "user@example.com"
  }
}
```

#### Get Folder Contents

```
GET /folders/{folder_id}/contents
```

Get all files and subfolders in a folder.

**Response:**
```json
{
  "success": true,
  "data": {
    "folder_id": "folder_990",
    "name": "Project A",
    "files": [...],
    "folders": [...]
  }
}
```

### 3. Sharing

#### Create Share Link

```
POST /shares
```

Create a shareable link for a file or folder.

**Request Body:**
```json
{
  "resource_id": "file_12346",
  "resource_type": "file",
  "permission": "view",
  "expiration": "2024-12-19T00:00:00Z",
  "password": "optional_password"
}
```

**Permission Options:**
- `view`: Read-only access
- `edit`: Read and write access
- `comment`: Read and comment access

**Response:**
```json
{
  "success": true,
  "data": {
    "share_id": "share_555",
    "url": "https://share.cloudsync.com/abc123xyz",
    "permission": "view",
    "created": "2024-11-19T15:35:00Z",
    "expiration": "2024-12-19T00:00:00Z"
  }
}
```

#### List Shares

```
GET /shares
```

List all active shares for your account.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "share_id": "share_555",
      "resource_id": "file_12346",
      "url": "https://share.cloudsync.com/abc123xyz",
      "permission": "view",
      "created": "2024-11-19T15:35:00Z"
    }
  ]
}
```

### 4. Sync Status

#### Get Sync Status

```
GET /sync/status
```

Get the current synchronization status.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "syncing",
    "files_synced": 1450,
    "files_pending": 12,
    "bytes_synced": 5368709120,
    "bytes_pending": 524288000,
    "last_sync": "2024-11-19T15:40:00Z",
    "next_sync": "2024-11-19T15:45:00Z"
  }
}
```

#### Get Sync History

```
GET /sync/history
```

Get the sync operation history.

**Parameters:**
- `days` (optional): Number of days to retrieve (default: 7)
- `limit` (optional): Number of results (default: 100)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "operation_id": "sync_op_1001",
      "type": "upload",
      "file_id": "file_12346",
      "status": "completed",
      "timestamp": "2024-11-19T15:20:00Z",
      "duration_ms": 2450
    }
  ]
}
```

### 5. Team Management

#### List Team Members

```
GET /team/members
```

List all team members in your workspace.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "user_id": "user_456",
      "email": "john.doe@example.com",
      "name": "John Doe",
      "role": "admin",
      "status": "active",
      "joined": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### Add Team Member

```
POST /team/members
```

Add a new member to your team.

**Request Body:**
```json
{
  "email": "jane.smith@example.com",
  "role": "editor"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "user_789",
    "email": "jane.smith@example.com",
    "role": "editor",
    "status": "pending_invitation"
  }
}
```

## Error Handling

All API errors return with appropriate HTTP status codes and error messages:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_TOKEN",
    "message": "The provided authentication token is invalid or expired.",
    "details": "Please generate a new token from your account settings."
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-----------|-------------|
| INVALID_TOKEN | 401 | Authentication token is invalid or expired |
| FORBIDDEN | 403 | You don't have permission for this action |
| NOT_FOUND | 404 | Requested resource not found |
| RATE_LIMITED | 429 | Too many requests - try again later |
| SERVER_ERROR | 500 | Internal server error |

## Rate Limiting

- **Free tier**: 100 requests per hour
- **Professional**: 1,000 requests per hour
- **Enterprise**: Custom limits

Rate limit information is included in response headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1700418000
```

## Webhook Events

CloudSync Pro can send webhook events to your application when certain actions occur.

### Supported Events

- `file.uploaded`: A new file was uploaded
- `file.deleted`: A file was deleted
- `file.shared`: A file was shared
- `folder.created`: A new folder was created
- `sync.completed`: A sync operation completed
- `member.added`: A new team member was added

### Webhook Payload Example

```json
{
  "event": "file.uploaded",
  "timestamp": "2024-11-19T15:20:00Z",
  "data": {
    "file_id": "file_12346",
    "name": "document.pdf",
    "size": 2048576,
    "uploader": "user@example.com"
  }
}
```

## Code Examples

### JavaScript/Node.js

```javascript
const axios = require('axios');

const apiClient = axios.create({
  baseURL: 'https://api.cloudsync.com/v1',
  headers: {
    'Authorization': 'Bearer YOUR_API_TOKEN'
  }
});

// Get file list
async function getFiles() {
  try {
    const response = await apiClient.get('/files');
    console.log(response.data);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}

// Upload file
async function uploadFile(folderID, filePath) {
  const formData = new FormData();
  formData.append('folder_id', folderID);
  formData.append('file', fs.createReadStream(filePath));

  try {
    const response = await apiClient.post('/files/upload', formData);
    console.log('File uploaded:', response.data);
  } catch (error) {
    console.error('Upload failed:', error.response.data);
  }
}
```

### Python

```python
import requests
import json

API_TOKEN = 'YOUR_API_TOKEN'
BASE_URL = 'https://api.cloudsync.com/v1'

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

# Get file list
def get_files():
    response = requests.get(f'{BASE_URL}/files', headers=headers)
    return response.json()

# Create folder
def create_folder(name, parent_id=None):
    payload = {
        'name': name,
        'parent_id': parent_id
    }
    response = requests.post(
        f'{BASE_URL}/folders',
        headers=headers,
        json=payload
    )
    return response.json()

# Upload file
def upload_file(folder_id, file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'folder_id': folder_id}
        response = requests.post(
            f'{BASE_URL}/files/upload',
            headers={'Authorization': headers['Authorization']},
            files=files,
            data=data
        )
    return response.json()
```

## Best Practices

1. **Store tokens securely**: Never commit API tokens to version control
2. **Use HTTPS only**: All API calls must use HTTPS
3. **Implement retry logic**: Use exponential backoff for failed requests
4. **Monitor rate limits**: Check rate limit headers and adjust accordingly
5. **Handle errors gracefully**: Implement proper error handling and logging
6. **Validate input**: Always validate user input before API calls
7. **Use webhooks**: For real-time updates instead of polling

## Support

For API support, visit:
- Documentation: https://docs.cloudsync.com/api
- Status: https://status.cloudsync.com
- Email: api-support@cloudsync.com
- Forum: https://community.cloudsync.com/api

## Version History

| Version | Released | Changes |
|---------|----------|---------|
| 1.5 | 2024-11-15 | Added webhook support, new sharing options |
| 1.4 | 2024-10-01 | Improved error messages, rate limit changes |
| 1.3 | 2024-09-01 | Added team management endpoints |
| 1.2 | 2024-08-01 | Initial public release |

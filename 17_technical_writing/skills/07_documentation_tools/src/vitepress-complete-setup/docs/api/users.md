# Users Endpoint

Manage users in your Project application.

## List Users

```bash
GET /users?page=1&limit=20
```

### Response

```json
{
  "data": [
    {
      "id": "user_123",
      "name": "John Doe",
      "email": "john@example.com",
      "createdAt": "2024-01-15T10:30:00Z"
    }
  ],
  "meta": {
    "total": 100,
    "page": 1,
    "limit": 20
  }
}
```

## Get User

```bash
GET /users/{id}
```

## Create User

```bash
POST /users
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com"
}
```

## Update User

```bash
PUT /users/{id}
Content-Type: application/json

{
  "name": "Jane Doe",
  "email": "jane@example.com"
}
```

## Delete User

```bash
DELETE /users/{id}
```

### Response

```json
{
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

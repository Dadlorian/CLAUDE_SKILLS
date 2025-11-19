# GraphQL Documentation Standards

## Overview

GraphQL APIs require different documentation approaches than REST. This guide establishes standards for documenting GraphQL APIs effectively.

---

## Core Components

### 1. Schema Documentation

The GraphQL schema is self-documenting. Enhance it with descriptions:

```graphql
"""
User account in the system.

Users can have one of three roles: ADMIN, MEMBER, or GUEST.
"""
type User {
  """Unique user identifier"""
  id: ID!

  """User's email address (unique across system)"""
  email: String!

  """User's full name"""
  name: String!

  """
  User's role in the organization.
  Defaults to MEMBER when creating new users.
  """
  role: Role!

  """ISO 8601 timestamp of account creation"""
  createdAt: DateTime!

  """
  Posts created by this user.

  ## Arguments
  - limit: Maximum number of posts to return (default: 10, max: 100)
  - offset: Number of posts to skip for pagination
  """
  posts(limit: Int = 10, offset: Int = 0): [Post!]!
}

"""User role in the organization"""
enum Role {
  """Full administrative access"""
  ADMIN

  """Standard user access"""
  MEMBER

  """Limited read-only access"""
  GUEST
}
```

**Best Practices**:
- Use triple-quoted strings for descriptions
- Document all types, fields, arguments
- Explain enums and their values
- Note defaults and constraints
- Link related types

---

### 2. Query Examples

Provide realistic query examples:

```markdown
## Get a user

### Query

```graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    email
    name
    role
    posts(limit: 5) {
      id
      title
      publishedAt
    }
  }
}
```

### Variables

```json
{
  "id": "usr_123"
}
```

### Response

```json
{
  "data": {
    "user": {
      "id": "usr_123",
      "email": "alice@example.com",
      "name": "Alice Johnson",
      "role": "MEMBER",
      "posts": [
        {
          "id": "post_456",
          "title": "Getting Started with GraphQL",
          "publishedAt": "2025-11-19T10:30:00Z"
        }
      ]
    }
  }
}
```
```

---

### 3. Mutation Documentation

```markdown
## Create a user

### Mutation

```graphql
mutation CreateUser($input: CreateUserInput!) {
  createUser(input: $input) {
    user {
      id
      email
      name
      role
      createdAt
    }
    errors {
      field
      message
    }
  }
}
```

### Input

```json
{
  "input": {
    "email": "bob@example.com",
    "name": "Bob Smith",
    "role": "MEMBER"
  }
}
```

### Success Response

```json
{
  "data": {
    "createUser": {
      "user": {
        "id": "usr_789",
        "email": "bob@example.com",
        "name": "Bob Smith",
        "role": "MEMBER",
        "createdAt": "2025-11-19T11:00:00Z"
      },
      "errors": null
    }
  }
}
```

### Error Response

```json
{
  "data": {
    "createUser": {
      "user": null,
      "errors": [
        {
          "field": "email",
          "message": "Email already exists"
        }
      ]
    }
  }
}
```
```

---

### 4. Error Handling

GraphQL has different error patterns than REST:

```markdown
## Error Handling

GraphQL returns errors in two ways:

### 1. Field-Level Errors (Recommended)

Return errors as part of the mutation payload:

```graphql
type CreateUserPayload {
  user: User
  errors: [UserError!]
}

type UserError {
  field: String!
  message: String!
}
```

**Example**:
```json
{
  "data": {
    "createUser": {
      "user": null,
      "errors": [
        {"field": "email", "message": "Invalid email format"}
      ]
    }
  }
}
```

### 2. Top-Level Errors

For system errors, GraphQL returns top-level errors:

```json
{
  "errors": [
    {
      "message": "Internal server error",
      "locations": [{"line": 2, "column": 3}],
      "path": ["createUser"]
    }
  ],
  "data": null
}
```

**When to use each**:
- **Field-level**: Validation errors, business logic errors
- **Top-level**: System errors, authentication failures
```

---

### 5. Pagination

```markdown
## Pagination Patterns

### Cursor-Based (Relay Specification)

```graphql
type Query {
  users(
    first: Int
    after: String
    last: Int
    before: String
  ): UserConnection!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

### Example Query

```graphql
query ListUsers {
  users(first: 10) {
    edges {
      node {
        id
        name
        email
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

### Next Page

```graphql
query NextPage($after: String!) {
  users(first: 10, after: $after) {
    edges {
      node {
        id
        name
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```
```

---

## Documentation Tools

### GraphQL Playground

Interactive GraphQL IDE with:
- Schema explorer
- Query autocomplete
- Documentation sidebar
- Query history

```markdown
## Try the API

Explore the GraphQL API in our interactive playground:

[Open GraphQL Playground](https://api.example.com/graphql)

**Features**:
- Auto-complete queries
- Browse schema documentation
- Test queries in real-time
```

### GraphiQL

Alternative interactive explorer:

```html
<!-- Embed GraphiQL -->
<script src="https://unpkg.com/graphiql/graphiql.min.js"></script>
<link rel="stylesheet" href="https://unpkg.com/graphiql/graphiql.min.css" />

<div id="graphiql">Loading...</div>

<script>
  ReactDOM.render(
    React.createElement(GraphiQL, {
      fetcher: GraphiQL.createFetcher({
        url: 'https://api.example.com/graphql'
      })
    }),
    document.getElementById('graphiql')
  );
</script>
```

---

## Best Practices

### Schema Design Documentation

```markdown
## Schema Design Principles

### 1. Null vs Non-Null

Use `!` for fields that are always present:

```graphql
type User {
  id: ID!           # ✅ Always present
  email: String!    # ✅ Required field
  bio: String       # ✅ Optional field (can be null)
}
```

### 2. Naming Conventions

- **Types**: PascalCase (`User`, `Post`, `Comment`)
- **Fields**: camelCase (`firstName`, `createdAt`)
- **Enums**: UPPER_SNAKE_CASE (`ADMIN`, `MEMBER`)
- **Arguments**: camelCase (`userId`, `limit`)

### 3. Input Types

Use input types for mutations:

```graphql
input CreateUserInput {
  email: String!
  name: String!
  role: Role
}

mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
}
```
```

---

## Quickstart Example

```markdown
# GraphQL Quickstart

Get started with the GraphQL API in 5 minutes.

## 1. Get your API key

[Sign up](https://example.com/signup) and copy your API key from the dashboard.

## 2. Make your first query

```bash
curl -X POST https://api.example.com/graphql \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ user(id: \"usr_123\") { id name email } }"
  }'
```

## 3. Explore the schema

Visit our [GraphQL Playground](https://api.example.com/graphql) to:
- Browse the complete schema
- Try queries interactively
- See auto-generated documentation

## 4. Use a client library

**JavaScript**:
```javascript
import { ApolloClient, InMemoryCache, gql } from '@apollo/client';

const client = new ApolloClient({
  uri: 'https://api.example.com/graphql',
  headers: {
    authorization: `Bearer ${API_KEY}`
  },
  cache: new InMemoryCache()
});

const { data } = await client.query({
  query: gql`
    query GetUser($id: ID!) {
      user(id: $id) {
        id
        name
        email
      }
    }
  `,
  variables: { id: 'usr_123' }
});

console.log(data.user);
```
```

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Specification**: GraphQL Specification, Relay Specification
**Tools**: GraphQL Playground, GraphiQL, Apollo, Relay

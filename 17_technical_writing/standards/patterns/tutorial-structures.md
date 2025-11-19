# Tutorial Structures

## Overview

Tutorials are **hands-on learning experiences** that teach by building. This guide provides proven tutorial structures.

---

## Tutorial vs. Guide vs. Reference

| Type | Purpose | Format | Example |
|------|---------|--------|---------|
| **Quickstart** | First success in 5-10 min | Step-by-step | "Send your first message" |
| **Tutorial** | Learn by building (30-60 min) | Project-based | "Build a chat app" |
| **How-To Guide** | Solve specific problem | Task-oriented | "Handle rate limits" |
| **Concept Guide** | Understand how it works | Explanatory | "How authentication works" |
| **Reference** | Look up details | Comprehensive | "API Reference" |

---

## Tutorial Structure

### 1. **Introduction**

```markdown
# Build a real-time chat application

Learn WebSocket fundamentals by building a working chat app.

**Time**: 45 minutes
**Level**: Beginner
**Prerequisites**:
- JavaScript basics
- Node.js installed

**What you'll learn**:
- WebSocket connections
- Real-time messaging
- Error handling

**What you'll build**:
[Screenshot of final app]
```

### 2. **Setup**

```markdown
## Set up your project

1. Create a new directory:
```bash
mkdir chat-app
cd chat-app
```

2. Initialize npm:
```bash
npm init -y
```

3. Install dependencies:
```bash
npm install express ws
```
```

### 3. **Build Incrementally**

```markdown
## Step 1: Create a basic server

Create `server.js`:

```javascript
const express = require('express');
const app = express();

app.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});
```

Run it:
```bash
node server.js
```

You should see: `Server running on http://localhost:3000`

## Step 2: Add WebSocket support

Update `server.js`:

```javascript
const express = require('express');
const WebSocket = require('ws');

const app = express();
const server = app.listen(3000);
const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
  console.log('Client connected');

  ws.on('message', (message) => {
    console.log(`Received: ${message}`);
  });
});
```

[Continue building...]
```

### 4. **Test Each Step**

```markdown
## Test your server

1. Open a new terminal
2. Connect with `wscat`:
```bash
npx wscat -c ws://localhost:3000
```

3. Send a message:
```
> Hello, server!
```

You should see the message logged in your server terminal.
```

### 5. **Conclusion**

```markdown
## What you've learned

✓ How to create a WebSocket server
✓ How to handle connections and messages
✓ How to broadcast to multiple clients
✓ How to handle disconnections

## Next steps

- [Add authentication](./auth.md)
- [Deploy to production](./deployment.md)
- [Scale with Redis](./scaling.md)

## Full code

View the [complete code on GitHub](https://github.com/example/chat-tutorial)
```

---

## Tutorial Patterns

### Pattern: Build-A-Thing Tutorial

**Best for**: Teaching through creating a complete project

**Structure**:
1. Intro (What we're building, why it matters)
2. Setup (Get environment ready)
3. Build incrementally (Small, testable steps)
4. Test at each step (Verify it works)
5. Enhance (Add features progressively)
6. Deploy (Make it real)
7. Next steps (What to learn next)

**Example**: "Build a REST API with Node.js and Express"

### Pattern: Concept Tutorial

**Best for**: Deep dive into a specific concept

**Structure**:
1. What is X? (High-level explanation)
2. Why does X matter? (Practical context)
3. How does X work? (Step-by-step breakdown)
4. Try it yourself (Hands-on exercise)
5. Common pitfalls (What to avoid)
6. Advanced topics (What's next)

**Example**: "Understanding JWT Authentication"

### Pattern: Comparative Tutorial

**Best for**: Showing trade-offs between approaches

**Structure**:
1. The problem (What we're solving)
2. Approach A (First solution)
3. Approach B (Alternative solution)
4. Comparison (Trade-offs)
5. When to use each (Decision guide)

**Example**: "REST vs GraphQL: Which to use?"

---

## Writing Tips

### Progressive Complexity

Start simple, add complexity:

```markdown
## Step 1: Basic function
```javascript
function greet(name) {
  return `Hello, ${name}!`;
}
```

## Step 2: Add validation
```javascript
function greet(name) {
  if (!name) {
    throw new Error('Name is required');
  }
  return `Hello, ${name}!`;
}
```

## Step 3: Production-ready
```javascript
function greet(name) {
  if (typeof name !== 'string') {
    throw new TypeError('Name must be a string');
  }
  if (name.trim().length === 0) {
    throw new Error('Name cannot be empty');
  }
  return `Hello, ${name.trim()}!`;
}
```
```

### Explain Why, Not Just What

```markdown
// ❌ BAD: Just states what
"Add this code to handle errors."

// ✅ GOOD: Explains why
"Handle errors to prevent the server from crashing when clients disconnect unexpectedly. Without error handling, uncaught exceptions will terminate the Node.js process."
```

---

## Assessment and Knowledge Checks

### Quiz Questions

```markdown
## Check your understanding

**Question**: What happens if a client disconnects while sending a message?

<details>
<summary>Show answer</summary>

The `error` event is triggered on the WebSocket object. Without error handling, this crashes the server. That's why we added the error handler in Step 4.

</details>
```

### Exercises

```markdown
## Try it yourself

**Exercise**: Modify the server to broadcast messages to all connected clients.

**Hint**: Loop through `wss.clients` and call `send()` on each client.

**Solution**: [View solution](./solutions/broadcast.js)
```

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Examples**: FreeCodeCamp, Egghead.io, Digital Ocean tutorials

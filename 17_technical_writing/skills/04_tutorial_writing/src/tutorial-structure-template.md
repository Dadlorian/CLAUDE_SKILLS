# Tutorial: Build a Real-Time Chat Application

## Course Metadata

**Level**: Intermediate
**Time**: 60 minutes
**Prerequisites**:
- JavaScript fundamentals (functions, async/await)
- Basic understanding of HTTP requests
- Node.js 16+ installed
- VS Code or similar editor

**What You'll Learn**:
- WebSocket fundamentals and real-time communication
- Express.js server setup
- Socket.io event handling
- Client-side WebSocket connections
- Error handling in real-time systems

**What You'll Build**:
A fully functional chat application where multiple users can:
1. Join a chat room
2. Send and receive messages in real-time
3. See who is currently online
4. Receive notifications when users join/leave

**Final Result**:
[Screenshot showing chat interface]

**Repository**: [github.com/example/chat-tutorial](https://github.com/example/chat-tutorial)

---

## Part 1: Setup Your Project (10 minutes)

### Learning Objective
Understand project structure and dependencies

### Step 1.1: Create Project Directory

```bash
mkdir realtime-chat
cd realtime-chat
npm init -y
```

Verify Node.js version:
```bash
node -v  # Should be v16.0.0 or higher
```

### Step 1.2: Install Dependencies

```bash
npm install express socket.io cors dotenv
npm install --save-dev nodemon
```

**Understanding the Packages**:
- **express**: HTTP server framework
- **socket.io**: Real-time communication library
- **cors**: Enable cross-origin requests
- **dotenv**: Environment variable management
- **nodemon**: Auto-restart server on file changes

### Step 1.3: Create Project Structure

```
realtime-chat/
├── public/
│   └── index.html
├── src/
│   ├── server.js
│   ├── handlers.js
│   └── config.js
├── .env
├── .gitignore
└── package.json
```

Create directories:
```bash
mkdir -p public src
touch src/server.js src/handlers.js src/config.js public/index.html .env
```

### Step 1.4: Configure NPM Scripts

Edit `package.json`:

```json
{
  "scripts": {
    "start": "node src/server.js",
    "dev": "nodemon src/server.js",
    "test": "echo \"Error: no test specified\" && exit 1"
  }
}
```

### Step 1.5: Test Setup

Create `.env`:
```
PORT=3000
NODE_ENV=development
```

Try running:
```bash
npm run dev
```

You should see the server is ready (we'll add actual startup code next).

✅ **Checkpoint**: Your project structure is set up. You can run npm run dev without errors.

---

## Part 2: Create the Server (20 minutes)

### Learning Objective
Understand Socket.io server setup and event handling

### Why This Matters
WebSockets enable bidirectional communication between client and server. With Socket.io, we can:
- Send messages from server to specific clients
- Broadcast messages to all connected clients
- Handle connection/disconnection events
- Track user presence

### Step 2.1: Create Configuration File

Create `src/config.js`:

```javascript
// src/config.js
require('dotenv').config();

module.exports = {
  PORT: process.env.PORT || 3000,
  NODE_ENV: process.env.NODE_ENV || 'development',
  isDevelopment: process.env.NODE_ENV === 'development'
};
```

**Why separate config?** Centralizes environment variables and makes testing easier.

### Step 2.2: Create Event Handlers

Create `src/handlers.js`:

```javascript
// src/handlers.js

/**
 * Handle user connection
 * Called when a user connects to the chat
 */
function handleUserJoin(socket, io, users) {
  return (data) => {
    const { username, room } = data;

    // Validate input
    if (!username || !room) {
      socket.emit('error', 'Username and room are required');
      return;
    }

    // Store user info
    socket.data.username = username;
    socket.data.room = room;

    // Add to users map
    if (!users[room]) {
      users[room] = [];
    }
    users[room].push({ id: socket.id, username });

    // Join socket to room
    socket.join(room);

    // Notify user they joined
    socket.emit('join_success', {
      message: `Welcome ${username}!`,
      users: users[room]
    });

    // Notify others in room
    socket.to(room).emit('user_joined', {
      username: username,
      users: users[room]
    });

    console.log(`[${room}] ${username} joined`);
  };
}

/**
 * Handle incoming message
 * Called when a user sends a message
 */
function handleMessage(socket, io) {
  return (data) => {
    const { content, room } = data;
    const username = socket.data.username;

    // Validate message
    if (!content || !room) {
      socket.emit('error', 'Invalid message');
      return;
    }

    // Prevent oversized messages
    if (content.length > 1000) {
      socket.emit('error', 'Message too long (max 1000 characters)');
      return;
    }

    // Create message object
    const message = {
      id: Date.now(),
      username,
      content,
      timestamp: new Date().toISOString()
    };

    // Broadcast to all users in the room
    io.to(room).emit('message', message);

    console.log(`[${room}] ${username}: ${content}`);
  };
}

/**
 * Handle user disconnection
 * Called when a user leaves the chat
 */
function handleDisconnect(socket, io, users) {
  return () => {
    const room = socket.data.room;
    const username = socket.data.username;

    if (room && users[room]) {
      // Remove user from room
      users[room] = users[room].filter(u => u.id !== socket.id);

      // Delete room if empty
      if (users[room].length === 0) {
        delete users[room];
      } else {
        // Notify remaining users
        io.to(room).emit('user_left', {
          username: username,
          users: users[room]
        });
      }
    }

    console.log(`[${room}] ${username} left`);
  };
}

module.exports = {
  handleUserJoin,
  handleMessage,
  handleDisconnect
};
```

### Step 2.3: Create the Server

Create `src/server.js`:

```javascript
// src/server.js
const express = require('express');
const { createServer } = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const config = require('./config');
const {
  handleUserJoin,
  handleMessage,
  handleDisconnect
} = require('./handlers');

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

// Middleware
app.use(cors());
app.use(express.static('public'));
app.use(express.json());

// Store connected users
const users = {};

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    uptime: process.uptime(),
    users: Object.values(users).reduce((a, b) => a + b.length, 0)
  });
});

// WebSocket connection handling
io.on('connection', (socket) => {
  console.log(`New client connected: ${socket.id}`);

  // Register event handlers
  socket.on('join', handleUserJoin(socket, io, users));
  socket.on('message', handleMessage(socket, io));
  socket.on('disconnect', handleDisconnect(socket, io, users));

  // Send connection confirmation
  socket.emit('connected', {
    id: socket.id,
    message: 'Connected to chat server'
  });
});

// Error handling
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
httpServer.listen(config.PORT, () => {
  console.log(`✅ Chat server running on http://localhost:${config.PORT}`);
  console.log(`📡 Environment: ${config.NODE_ENV}`);
});

module.exports = { app, httpServer, io };
```

### Step 2.4: Test the Server

```bash
npm run dev
```

You should see:
```
✅ Chat server running on http://localhost:3000
```

Test the health check:
```bash
curl http://localhost:3000/api/health
```

Expected response:
```json
{"status":"ok","uptime":2.345,"users":0}
```

✅ **Checkpoint**: Your server is running and responding to health checks.

---

## Part 3: Create the Client Interface (20 minutes)

### Learning Objective
Understand Socket.io client-side implementation

### Why This Matters
The client is where users interact with the chat. We need to:
- Connect to the server
- Send messages
- Receive messages in real-time
- Handle connection events

### Step 3.1: Create HTML Interface

Create `public/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Real-Time Chat</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }

    .container {
      background: white;
      border-radius: 12px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
      width: 100%;
      max-width: 600px;
      height: 600px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    /* Join Screen */
    .join-screen {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px;
      text-align: center;
    }

    .join-screen h1 {
      color: #333;
      margin-bottom: 10px;
    }

    .join-screen p {
      color: #666;
      margin-bottom: 30px;
    }

    .form-group {
      width: 100%;
      margin-bottom: 20px;
      text-align: left;
    }

    .form-group label {
      display: block;
      margin-bottom: 8px;
      color: #555;
      font-weight: 500;
    }

    .form-group input {
      width: 100%;
      padding: 12px;
      border: 2px solid #e0e0e0;
      border-radius: 6px;
      font-size: 16px;
      transition: border-color 0.3s;
    }

    .form-group input:focus {
      outline: none;
      border-color: #667eea;
    }

    .btn {
      background: #667eea;
      color: white;
      padding: 12px 30px;
      border: none;
      border-radius: 6px;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.3s;
      width: 100%;
    }

    .btn:hover {
      background: #5568d3;
    }

    .btn:disabled {
      background: #ccc;
      cursor: not-allowed;
    }

    /* Chat Screen */
    .chat-screen {
      display: none;
      flex-direction: column;
      height: 100%;
    }

    .chat-header {
      background: #667eea;
      color: white;
      padding: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .chat-header h2 {
      font-size: 18px;
    }

    .user-badge {
      background: rgba(255, 255, 255, 0.2);
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 14px;
    }

    .messages {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .message {
      display: flex;
      flex-direction: column;
      margin-bottom: 10px;
    }

    .message.own {
      align-items: flex-end;
    }

    .message.other {
      align-items: flex-start;
    }

    .message-username {
      font-size: 12px;
      color: #999;
      margin-bottom: 4px;
    }

    .message-content {
      max-width: 80%;
      padding: 10px 15px;
      border-radius: 8px;
      word-wrap: break-word;
    }

    .message.own .message-content {
      background: #667eea;
      color: white;
    }

    .message.other .message-content {
      background: #f0f0f0;
      color: #333;
    }

    .message-time {
      font-size: 11px;
      color: #999;
      margin-top: 4px;
    }

    .input-area {
      border-top: 1px solid #e0e0e0;
      padding: 15px;
      display: flex;
      gap: 10px;
    }

    .input-area input {
      flex: 1;
      padding: 10px 15px;
      border: 1px solid #e0e0e0;
      border-radius: 6px;
      font-size: 14px;
    }

    .input-area button {
      padding: 10px 20px;
      background: #667eea;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
    }

    .users-online {
      background: #f9f9f9;
      padding: 15px;
      border-top: 1px solid #e0e0e0;
      font-size: 12px;
      color: #666;
    }

    .error {
      color: #e74c3c;
      background: #fadbd8;
      padding: 10px;
      border-radius: 4px;
      margin-bottom: 10px;
    }

    .system-message {
      text-align: center;
      color: #999;
      font-size: 12px;
      padding: 10px;
    }
  </style>
</head>
<body>
  <div class="container">
    <!-- Join Screen -->
    <div class="join-screen" id="joinScreen">
      <h1>💬 Real-Time Chat</h1>
      <p>Connect and chat with others instantly</p>

      <form id="joinForm">
        <div class="form-group">
          <label for="username">Your Name</label>
          <input
            type="text"
            id="username"
            placeholder="Enter your username"
            required
          />
        </div>

        <div class="form-group">
          <label for="room">Chat Room</label>
          <input
            type="text"
            id="room"
            placeholder="Enter room name"
            value="general"
            required
          />
        </div>

        <button type="submit" class="btn">Join Chat</button>
      </form>
    </div>

    <!-- Chat Screen -->
    <div class="chat-screen" id="chatScreen">
      <div class="chat-header">
        <div>
          <h2 id="roomName"></h2>
        </div>
        <div class="user-badge" id="userBadge"></div>
      </div>

      <div class="messages" id="messages"></div>

      <div class="users-online" id="usersOnline"></div>

      <div class="input-area">
        <input
          type="text"
          id="messageInput"
          placeholder="Type a message..."
          autocomplete="off"
        />
        <button id="sendBtn">Send</button>
      </div>
    </div>
  </div>

  <script src="/socket.io/socket.io.js"></script>
  <script src="/client.js"></script>
</body>
</html>
```

### Step 3.2: Create Client JavaScript

Create `public/client.js`:

```javascript
// public/client.js

// Initialize Socket.io connection
const socket = io();

// DOM elements
const joinScreen = document.getElementById('joinScreen');
const chatScreen = document.getElementById('chatScreen');
const joinForm = document.getElementById('joinForm');
const usernameInput = document.getElementById('username');
const roomInput = document.getElementById('room');
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const roomNameEl = document.getElementById('roomName');
const userBadgeEl = document.getElementById('userBadge');
const usersOnlineEl = document.getElementById('usersOnline');

let currentRoom = '';
let currentUsername = '';

// Handle socket connection
socket.on('connected', (data) => {
  console.log('Connected to server:', data.id);
});

// Handle join form submission
joinForm.addEventListener('submit', (e) => {
  e.preventDefault();

  const username = usernameInput.value.trim();
  const room = roomInput.value.trim();

  if (!username || !room) {
    showError('Please enter both username and room');
    return;
  }

  currentUsername = username;
  currentRoom = room;

  // Request to join
  socket.emit('join', { username, room });
});

// Handle successful join
socket.on('join_success', (data) => {
  roomNameEl.textContent = currentRoom;
  userBadgeEl.textContent = currentUsername;

  // Switch screens
  joinScreen.style.display = 'none';
  chatScreen.style.display = 'flex';

  // Clear messages
  messagesContainer.innerHTML = '';

  // Add system message
  addSystemMessage(`Welcome to ${currentRoom}!`);

  // Update users list
  updateUsersList(data.users);

  // Focus input
  messageInput.focus();
});

// Handle incoming messages
socket.on('message', (message) => {
  addMessage(message);
});

// Handle user join notifications
socket.on('user_joined', (data) => {
  addSystemMessage(`${data.username} joined the chat`);
  updateUsersList(data.users);
});

// Handle user leave notifications
socket.on('user_left', (data) => {
  addSystemMessage(`${data.username} left the chat`);
  updateUsersList(data.users);
});

// Handle errors
socket.on('error', (message) => {
  showError(message);
});

// Send message on button click
sendBtn.addEventListener('click', sendMessage);

// Send message on Enter key
messageInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Helper function to send message
function sendMessage() {
  const content = messageInput.value.trim();

  if (!content) return;

  socket.emit('message', {
    content,
    room: currentRoom
  });

  messageInput.value = '';
  messageInput.focus();
}

// Helper function to add message to UI
function addMessage(message) {
  const isOwn = message.username === currentUsername;
  const timestamp = new Date(message.timestamp).toLocaleTimeString();

  const messageEl = document.createElement('div');
  messageEl.className = `message ${isOwn ? 'own' : 'other'}`;
  messageEl.innerHTML = `
    <div class="message-username">${message.username}</div>
    <div class="message-content">${escapeHtml(message.content)}</div>
    <div class="message-time">${timestamp}</div>
  `;

  messagesContainer.appendChild(messageEl);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Helper function to add system message
function addSystemMessage(text) {
  const messageEl = document.createElement('div');
  messageEl.className = 'system-message';
  messageEl.textContent = text;

  messagesContainer.appendChild(messageEl);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Helper function to update users list
function updateUsersList(users) {
  usersOnlineEl.innerHTML = `<strong>Users online (${users.length}):</strong> ${users.map(u => u.username).join(', ')}`;
}

// Helper function to show error
function showError(message) {
  alert(`Error: ${message}`);
}

// Helper function to escape HTML (prevent XSS)
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
```

### Step 3.3: Test the Complete Application

```bash
npm run dev
```

Open browser: `http://localhost:3000`

1. Join as "User 1" in room "general"
2. Open another browser tab: `http://localhost:3000`
3. Join as "User 2" in room "general"
4. Send messages between users
5. See real-time updates

✅ **Checkpoint**: Your chat application is working! Messages appear in real-time.

---

## Part 4: Error Handling & Polish (10 minutes)

### Learning Objective
Handle errors gracefully and improve user experience

### Step 4.1: Add Connection Status Indicator

Add to `public/index.html` (in chat-header):

```html
<div id="connectionStatus" style="width: 10px; height: 10px; background: green; border-radius: 50%;"></div>
```

Add to `public/client.js`:

```javascript
const connectionStatus = document.getElementById('connectionStatus');

socket.on('connect', () => {
  connectionStatus.style.background = 'green';
  console.log('Connected to server');
});

socket.on('disconnect', () => {
  connectionStatus.style.background = 'red';
  console.log('Disconnected from server');
  addSystemMessage('Disconnected. Attempting to reconnect...');
});

socket.on('reconnect', () => {
  connectionStatus.style.background = 'green';
  addSystemMessage('Reconnected to server');
});
```

### Step 4.2: Add Message Validation

Update `sendMessage()` in `public/client.js`:

```javascript
function sendMessage() {
  const content = messageInput.value.trim();

  if (!content) {
    showError('Message cannot be empty');
    return;
  }

  if (content.length > 1000) {
    showError('Message is too long (max 1000 characters)');
    return;
  }

  socket.emit('message', {
    content,
    room: currentRoom
  });

  messageInput.value = '';
  messageInput.focus();
}
```

✅ **Checkpoint**: Your application handles errors gracefully.

---

## Knowledge Checks

**Question 1**: What is the difference between `socket.emit()` and `socket.broadcast()`?

<details>
<summary>Show Answer</summary>

- `socket.emit()` sends to the specific socket only
- `socket.broadcast.to(room).emit()` sends to all others in the room
- `io.to(room).emit()` sends to everyone in the room (including sender)

</details>

**Question 2**: Why do we validate messages on both client and server?

<details>
<summary>Show Answer</summary>

Client validation:
- Faster feedback to user
- Better user experience
- Reduces unnecessary network requests

Server validation:
- Cannot be bypassed
- Protects against malicious clients
- Ensures data integrity

Always validate on the server!

</details>

---

## Next Steps

1. **Add Persistent Storage**: Save messages to database
2. **Add Typing Indicators**: Show "User is typing..."
3. **Add Message Editing**: Allow users to edit sent messages
4. **Add Private Messaging**: Direct messages between users
5. **Deploy to Production**: Deploy to Heroku or Vercel

## Complete Code Repository

Clone the finished code:
```bash
git clone https://github.com/example/chat-tutorial
cd chat-tutorial
npm install
npm run dev
```

## Troubleshooting

**Messages not appearing?**
- Check browser console for errors (F12)
- Verify server is running on port 3000
- Check that socket is connected (green status indicator)

**Can't connect to server?**
- Ensure server is running: `npm run dev`
- Check firewall isn't blocking port 3000
- Try reloading the page

**Messages from other users not appearing?**
- Open chat in multiple browser windows
- Use different usernames for each window
- Send message in first window, check second window

## Resources

- Socket.io Documentation: https://socket.io/docs/
- Express.js Documentation: https://expressjs.com/
- Real-time Web Patterns: https://en.wikipedia.org/wiki/Comet_%28programming%29

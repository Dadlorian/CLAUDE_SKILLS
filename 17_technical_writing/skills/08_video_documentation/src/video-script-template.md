# Video Script: Build a REST API with Node.js

## Production Details

**Video Title**: Build a REST API with Node.js and Express - Complete Tutorial

**Length**: 15 minutes
**Difficulty**: Beginner to Intermediate
**Target Audience**: JavaScript developers
**Platform**: YouTube

---

## Script Structure

### [00:00-00:30] Introduction (30 seconds)

**Visual**: Title screen with logo and code editor

**Narration**:
"Welcome! In this video, we'll build a complete REST API from scratch using Node.js and Express.

By the end, you'll understand:
- How to set up an Express server
- How to create API endpoints
- How to handle requests and responses
- How to deploy your API to the cloud

Let's get started!"

**On Screen**: Display:
- What we're building (API endpoints)
- Time estimate: 15 minutes
- Link to completed code repo

---

### [00:30-02:00] Prerequisites & Setup (1.5 minutes)

**Visual**: Show prerequisites checklist on screen

**Narration**:
"Before we start, make sure you have:
- Node.js 16 or higher installed
- A code editor (I'm using VS Code)
- Postman or similar tool to test the API
- 15 minutes of time

Let's verify Node.js is installed."

**Screen Recording**:
```bash
node --version  # Should show v16.0.0 or higher
npm --version
```

**Narration**:
"Great! Now let's create our project."

**Screen Recording**:
```bash
mkdir my-rest-api
cd my-rest-api
npm init -y
npm install express cors
```

**Voice Over**:
"We're installing Express for the server framework and CORS to handle cross-origin requests. Installation takes about 10 seconds."

**[Pause recording while npm installs, resume when complete]**

**Visual**: Show installed packages

```bash
npm list
```

**Narration**:
"Perfect! Now we have everything we need."

---

### [02:00-07:00] Build the API (5 minutes)

#### Part A: Create the Server (2 minutes)

**Visual**: Open VS Code, create `server.js` file

**Narration**:
"Let's create our API server. I'll create a file called server.js."

**Screen**: Show file being created

**Narration**:
"Now, let's write the code to create an Express server."

**Type slowly on screen**:
```javascript
const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

**Voice Over**:
"Here's what's happening:
1. We import Express and CORS
2. We create an app instance
3. We add middleware to handle JSON and cross-origin requests
4. We start the server on port 3000

Notice that we use `app.listen` at the end to start the server."

**Highlight code** as you explain each section

---

#### Part B: Add First Endpoint (2 minutes)

**Visual**: Show cursor in code editor

**Narration**:
"Now let's add our first API endpoint. This will be a simple 'hello' endpoint."

**Type on screen**:
```javascript
// Add this before app.listen()

app.get('/', (req, res) => {
  res.json({ message: 'Welcome to our API' });
});
```

**Voice Over**:
"This endpoint:
- Uses the GET HTTP method
- Responds to requests to the root path '/'
- Returns a JSON response with a welcome message

Let's test it."

**Screen**: Show terminal

**Type**:
```bash
npm start
# or nodemon src/server.js if you installed nodemon
```

**Wait for server to start**

**Visual**: Show "Server running on port 3000" message

**Narration**:
"Great! The server is running. Now let's test the endpoint using Postman."

**Screen**: Open Postman

**Visual**: Show creating a GET request

**Type URL**: `http://localhost:3000/`

**Show**: Click Send button

**Result**:
```json
{
  "message": "Welcome to our API"
}
```

**Narration**:
"Excellent! Our first endpoint is working. Now let's add more endpoints to make this a real API."

---

#### Part C: Add Data Endpoints (1 minute)

**Visual**: Show code editor again

**Narration**:
"Let's create a simple in-memory database with some users."

**Type**:
```javascript
// Add before routes

let users = [
  { id: 1, name: 'Alice', email: 'alice@example.com' },
  { id: 2, name: 'Bob', email: 'bob@example.com' }
];

// GET all users
app.get('/api/users', (req, res) => {
  res.json(users);
});

// GET user by ID
app.get('/api/users/:id', (req, res) => {
  const user = users.find(u => u.id === parseInt(req.params.id));
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  res.json(user);
});

// CREATE user
app.post('/api/users', (req, res) => {
  const { name, email } = req.body;

  // Validate
  if (!name || !email) {
    return res.status(400).json({ error: 'Name and email required' });
  }

  // Create user
  const newUser = {
    id: users.length + 1,
    name,
    email
  };

  users.push(newUser);
  res.status(201).json(newUser);
});
```

**Highlight sections** as you explain:

**Narration**:
"Here we're adding:
1. A users array - our fake database
2. GET /api/users - returns all users
3. GET /api/users/:id - returns a specific user
4. POST /api/users - creates a new user

The `:id` in the route is a parameter. We access it with `req.params.id`.

Let's test these endpoints."

**Screen**: Terminal

**Restart server** (show Ctrl+C and then restart)

**Screen**: Postman

**Test GET /api/users**:
- URL: `http://localhost:3000/api/users`
- Click Send
- Show response with all users

**Narration**:
"Great! We got both users. Now let's get a specific user."

**Test GET /api/users/1**:
- URL: `http://localhost:3000/api/users/1`
- Show response with Alice's data

**Narration**:
"Perfect! Now let's create a new user. We'll use POST."

**Test POST /api/users**:
- Change method to POST
- URL: `http://localhost:3000/api/users`
- Body (raw JSON):
```json
{
  "name": "Charlie",
  "email": "charlie@example.com"
}
```
- Show response with created user

**Narration**:
"Excellent! We've successfully:
- Retrieved all users
- Retrieved a specific user
- Created a new user

This is the core of a REST API!"

---

### [07:00-12:00] Add Features (5 minutes)

#### Error Handling

**Narration**:
"A good API needs proper error handling. Let's add error handling middleware."

**Type**:
```javascript
// Add at the end, before app.listen()

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({
    error: 'Internal server error'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not found'
  });
});
```

**Voice Over**:
"Error middleware catches any errors in our routes and returns a proper error response.

Let's test it by hitting a non-existent endpoint."

**Screen**: Postman

**Test**: GET `http://localhost:3000/api/invalid`

**Show**: 404 error response

**Narration**:
"Great! Our error handling is working."

---

#### Environment Variables

**Narration**:
"For production, we shouldn't hardcode the port. Let's use an environment variable."

**Type**:
```javascript
const PORT = process.env.PORT || 3000;
```

**Voice Over**:
"Now we can set the PORT environment variable, and it will use that. If not set, it defaults to 3000.

This is important for deployment."

---

### [12:00-13:30] Testing Summary (1.5 minutes)

**Visual**: Summary of what we built

**On Screen**: Show a table of endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | / | Welcome message |
| GET | /api/users | Get all users |
| GET | /api/users/:id | Get user by ID |
| POST | /api/users | Create user |

**Narration**:
"We've built a complete REST API with:
- Express server setup
- GET and POST endpoints
- Error handling
- Environment variables

All in just 15 minutes!"

---

### [13:30-14:30] Next Steps (1 minute)

**Visual**: Show screen with next steps

**Narration**:
"Next steps to improve your API:

1. **Database**: Use PostgreSQL instead of in-memory arrays
2. **Authentication**: Add JWT authentication
3. **Validation**: Use a library like Joi for request validation
4. **Documentation**: Create API documentation with Swagger
5. **Deployment**: Deploy to Heroku or AWS
6. **Testing**: Write automated tests

All of these have dedicated videos in this series."

**On Screen**: Show links to next videos

---

### [14:30-15:00] Conclusion (30 seconds)

**Visual**: End screen with logo

**Narration**:
"Thanks for watching! If you found this helpful:
- Like and subscribe
- Check out the linked repository for the full code
- Let me know what you'd like to see next in the comments

Good luck with your API development!"

**On Screen**:
- Like button
- Subscribe button
- GitHub repo link
- Comments section preview

---

## Production Notes

### Recording Settings

- **Resolution**: 1920x1080 (1080p)
- **Frame Rate**: 30fps
- **Font Size in Editor**: 18-20pt (large enough to read)
- **Browser Zoom**: 125-150%
- **Terminal Font Size**: 16pt+

### Audio

- Use external microphone (Blue Yeti or similar)
- Record in quiet room
- Normalize audio to -3dB
- Add background music (low volume, non-distracting)
- Speak clearly at normal pace (not too fast)

### Pacing Tips

- Record sections with pauses for npm install
- Don't show waiting time
- Use jump cuts for long waits
- Highlight important code as you explain

### B-Roll & Transitions

- No fancy transitions (keep it professional)
- Simple dissolves between sections
- Code should be clearly visible
- Cursor position clear

### Captions

- Add manually or use automated transcription + review
- Sync with audio
- Show code as it appears on screen
- Mark timestamps:
  - [00:00] Introduction
  - [00:30] Setup
  - [02:00] Building the API
  - etc.

### Thumbnail

- 1280x720 pixels
- Large text: "REST API" + "Node.js"
- Contrasting colors
- Include Express or Node.js logo
- Keep consistent with channel branding

### YouTube Metadata

**Title**: Build a REST API with Node.js and Express - Complete Tutorial (15 minutes)

**Description**:
```
Learn how to build a REST API from scratch using Node.js and Express!

In this tutorial, we'll create:
✅ Express server setup
✅ GET endpoints
✅ POST endpoints
✅ Error handling
✅ Environment variables

00:00 Introduction
00:30 Prerequisites & Setup
02:00 Create the Server
04:00 Add Endpoints
07:00 Error Handling
12:00 Testing Summary
13:30 Next Steps
14:30 Conclusion

📚 Resources:
- GitHub Repo: https://github.com/example/rest-api-tutorial
- Express Docs: https://expressjs.com/
- Node.js Docs: https://nodejs.org/

👍 If you find this helpful, please like, subscribe, and comment!
```

**Tags**:
- REST API
- Node.js
- Express.js
- JavaScript
- Backend
- Web Development
- Tutorial
- Beginners

---

## Post-Production Checklist

- [ ] Audio synced with video
- [ ] Captions added (99%+ accuracy)
- [ ] No background noise
- [ ] Color correction if needed
- [ ] Smooth transitions
- [ ] Code clearly visible
- [ ] Thumbnail created
- [ ] Title and description set
- [ ] Tags added
- [ ] Transcript uploaded
- [ ] Chapters added
- [ ] Preview watched (full video)
- [ ] Links verified
- [ ] Published or scheduled

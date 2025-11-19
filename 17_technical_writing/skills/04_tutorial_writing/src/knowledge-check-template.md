# Knowledge Checks & Assessments

## Embedded Knowledge Checks

### After API Basics Section

**Question 1**: What HTTP method should be used to create a new resource?

A) GET
B) POST ✅
C) PUT
D) DELETE

<details>
<summary>Why this matters</summary>

POST is used for creating new resources on the server. GET is for retrieval, PUT for updates, DELETE for removal. Using the correct HTTP method follows RESTful conventions.

</details>

---

### After Authentication Section

**Question 2**: Why should API keys never be stored in frontend code?

<details>
<summary>Show Answer</summary>

**Correct Answer**: Because frontend code is publicly visible and anyone can extract the key.

**Implications**:
- Malicious users could use your API key to make unauthorized requests
- They could exceed your rate limits
- They could incur charges for API usage
- They could access your data

**Best Practice**:
- Keep API keys in backend code or environment variables
- Never commit them to version control
- Use `.env` files (git-ignored)
- Rotate keys regularly

</details>

---

## Practical Exercises

### Exercise 1: Complete and Debug Code

Here's a function with bugs. Can you fix it?

```javascript
// BUGGY CODE
async function fetchUser(userId) {
  const response = await fetch(
    `https://api.example.com/users/${userId}`
  );
  const user = response.json();
  return user;
}
```

What's wrong? (Hint: Two issues)

<details>
<summary>Show Solution</summary>

```javascript
// FIXED CODE
async function fetchUser(userId) {
  const response = await fetch(
    `https://api.example.com/users/${userId}`
  );

  // Issue 1: Must await JSON parsing
  if (!response.ok) {  // Issue 2: Should check response status
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const user = await response.json();  // FIX: Add await
  return user;
}
```

**Issues Fixed**:
1. `response.json()` returns a Promise and needs `await`
2. Should check `response.ok` to handle HTTP errors

</details>

---

### Exercise 2: Refactor to Use Async/Await

Convert this promise chain to async/await:

```javascript
function processPayment(amount) {
  return createCharge(amount)
    .then(charge => {
      console.log('Charge created:', charge.id);
      return sendReceipt(charge.id);
    })
    .then(receipt => {
      console.log('Receipt sent');
      return receipt;
    })
    .catch(error => {
      console.error('Payment failed:', error);
      throw error;
    });
}
```

<details>
<summary>Show Solution</summary>

```javascript
async function processPayment(amount) {
  try {
    const charge = await createCharge(amount);
    console.log('Charge created:', charge.id);

    const receipt = await sendReceipt(charge.id);
    console.log('Receipt sent');

    return receipt;
  } catch (error) {
    console.error('Payment failed:', error);
    throw error;
  }
}
```

**Why async/await is better**:
- Reads like synchronous code
- Easier to understand the flow
- Easier to debug
- Cleaner error handling with try/catch

</details>

---

### Exercise 3: Error Handling

Here's code that needs error handling. How would you improve it?

```javascript
app.post('/api/charges', (req, res) => {
  const charge = createCharge(req.body.amount);
  res.json({ charge });
});
```

<details>
<summary>Show Solution</summary>

```javascript
app.post('/api/charges', async (req, res) => {
  try {
    // 1. Validate input
    const { amount } = req.body;

    if (!amount || typeof amount !== 'number') {
      return res.status(400).json({
        error: 'Invalid amount'
      });
    }

    if (amount < 50) {
      return res.status(400).json({
        error: 'Minimum charge is $0.50'
      });
    }

    // 2. Create charge
    const charge = await createCharge(amount);

    // 3. Return success
    res.json({
      success: true,
      charge
    });

  } catch (error) {
    // 4. Handle specific errors
    if (error.code === 'CARD_DECLINED') {
      return res.status(402).json({
        error: 'Payment was declined'
      });
    }

    // 5. Handle generic errors
    console.error('Charge creation error:', error);
    res.status(500).json({
      error: 'Failed to process charge'
    });
  }
});
```

**Improvements**:
- ✅ Input validation
- ✅ Async/await for clarity
- ✅ Proper HTTP status codes
- ✅ Error-specific handling
- ✅ Logging for debugging

</details>

---

## Challenge Project

### Build: User Authentication API

**Difficulty**: Intermediate
**Time**: 30-45 minutes

**Requirements**:
1. POST `/auth/signup` - Register new user
2. POST `/auth/login` - Authenticate user
3. GET `/auth/profile` - Get current user (protected)
4. POST `/auth/logout` - Logout user

**Constraints**:
- Must validate input on both client and server
- Passwords must be hashed (use bcrypt)
- Must use JWT for session management
- Must handle errors gracefully

**Acceptance Criteria**:
- [ ] Can register with email and password
- [ ] Can login with valid credentials
- [ ] Login returns a JWT token
- [ ] Protected routes require valid token
- [ ] Invalid token returns 401 Unauthorized
- [ ] Can logout

**Hints**:
- Use bcrypt for password hashing
- Use jsonwebtoken library for JWT
- Store user data in database
- Validate email format
- Check password strength

<details>
<summary>Starter Code</summary>

```javascript
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());

const users = new Map(); // Mock database
const JWT_SECRET = 'your-secret-key';

// TODO: Implement signup
app.post('/auth/signup', async (req, res) => {
  // 1. Validate input (email, password)
  // 2. Check if user already exists
  // 3. Hash password
  // 4. Store user
  // 5. Return success or error
});

// TODO: Implement login
app.post('/auth/login', async (req, res) => {
  // 1. Validate input
  // 2. Find user by email
  // 3. Compare password
  // 4. Generate JWT token
  // 5. Return token or error
});

// TODO: Implement protected route
app.get('/auth/profile', authenticateToken, (req, res) => {
  // Return current user profile
});

// TODO: Implement authentication middleware
function authenticateToken(req, res, next) {
  // 1. Get token from header
  // 2. Verify token
  // 3. Attach user to request or return 401
}

app.listen(3000);
```

</details>

---

## Assessment Rubric

### Code Quality (30%)
- [ ] Code is clean and readable
- [ ] Proper variable naming
- [ ] Appropriate comments
- [ ] No redundant code

### Functionality (40%)
- [ ] All requirements implemented
- [ ] Code runs without errors
- [ ] Handles edge cases
- [ ] Proper error messages

### Best Practices (20%)
- [ ] Security considerations
- [ ] Error handling
- [ ] Input validation
- [ ] Proper HTTP status codes

### Documentation (10%)
- [ ] Comments explain complex logic
- [ ] README included
- [ ] Usage examples provided

---

## Reflection Questions

After completing this tutorial, answer these questions:

1. **What was the most challenging part?**
   - Understanding a specific concept?
   - Implementing a feature?
   - Debugging an issue?

2. **What would you do differently?**
   - Different technology choices?
   - Better structure?
   - More efficient approach?

3. **What did you learn?**
   - Key concepts?
   - Best practices?
   - Common pitfalls?

4. **What's next?**
   - What feature would you add?
   - How would you improve it?
   - Where would you deploy it?

---

## Additional Resources

**Free Resources**:
- MDN Web Docs: https://developer.mozilla.org/
- Node.js Guide: https://nodejs.org/en/docs/
- Express.js Tutorial: https://expressjs.com/
- YouTube: Traversy Media

**Paid Courses**:
- Frontend Masters
- Egghead.io
- Pluralsight

**Communities**:
- Stack Overflow
- Dev.to
- Reddit r/learnprogramming
- Discord communities

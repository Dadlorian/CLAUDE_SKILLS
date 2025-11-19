# Code Sample Standards

## Purpose

Code samples are the most valuable component of technical documentation. This document establishes standards for creating production-quality code examples.

**Goal**: Every code sample must be complete, tested, secure, and ready for production use.

---

## The Seven Principles of Excellent Code Samples

### 1. **Complete and Self-Contained**

Every code sample must run without modification (except for API keys/credentials).

**✅ Good - Complete**:
```python
import os
import requests

def get_user(user_id):
    """
    Fetch user data from the API.

    Args:
        user_id: The user's unique identifier

    Returns:
        dict: User data

    Raises:
        requests.HTTPError: If the API request fails
    """
    api_key = os.getenv('API_KEY')
    if not api_key:
        raise ValueError("API_KEY environment variable not set")

    url = f"https://api.example.com/v1/users/{user_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()

if __name__ == "__main__":
    try:
        user = get_user("usr_123")
        print(f"User: {user['name']} ({user['email']})")
    except Exception as e:
        print(f"Error: {e}")
```

**❌ Bad - Incomplete**:
```python
response = requests.get(url)
data = response.json()
print(data)
```

---

### 2. **Tested and Working**

All code samples must execute successfully and be automatically tested.

**Testing Strategy**:
```markdown
## Code Sample Testing

### Manual Testing
Before publishing, manually test every code sample:
1. Copy the code exactly as written
2. Run it in a clean environment
3. Verify it produces expected output
4. Test error conditions

### Automated Testing
Integrate code samples into CI/CD:

```yaml
# .github/workflows/test-docs.yml
name: Test Documentation Code Samples

on: [pull_request]

jobs:
  test-python-samples:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r docs/requirements.txt
      - name: Test Python code samples
        run: python docs/test_code_samples.py

  test-javascript-samples:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm install
      - name: Test JavaScript code samples
        run: npm run test:docs
```

### Code Sample Test Script

```python
# docs/test_code_samples.py
import re
import subprocess
from pathlib import Path

def extract_code_blocks(markdown_file):
    """Extract Python code blocks from markdown."""
    content = Path(markdown_file).read_text()
    pattern = r'```python\n(.*?)```'
    return re.findall(pattern, content, re.DOTALL)

def test_code_block(code, test_env):
    """Test a code block execution."""
    try:
        # Create temporary file
        with open('/tmp/test_sample.py', 'w') as f:
            f.write(code)

        # Execute code
        result = subprocess.run(
            ['python', '/tmp/test_sample.py'],
            capture_output=True,
            text=True,
            timeout=30,
            env=test_env
        )

        if result.returncode != 0:
            print(f"❌ Code sample failed:")
            print(f"   {result.stderr}")
            return False

        print(f"✅ Code sample passed")
        return True

    except subprocess.TimeoutExpired:
        print(f"❌ Code sample timed out")
        return False
```
```

---

### 3. **Secure by Default**

Never include security vulnerabilities in code samples.

**Security Checklist**:

✅ **Credentials Management**:
```javascript
// ✅ GOOD - Environment variables
const apiKey = process.env.API_KEY;

// ✅ GOOD - Configuration file with placeholder
const config = require('./config.json'); // { "apiKey": "YOUR_API_KEY_HERE" }

// ❌ BAD - Hardcoded credentials
const apiKey = "sk_live_abc123";
```

✅ **Input Validation**:
```python
# ✅ GOOD - Validates input
def create_user(email, name):
    import re

    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")

    # Validate name length
    if len(name) < 1 or len(name) > 100:
        raise ValueError("Name must be 1-100 characters")

    # Make API request...

# ❌ BAD - No validation (vulnerable to injection)
def create_user(email, name):
    query = f"INSERT INTO users VALUES ('{email}', '{name}')"  # SQL injection!
```

✅ **HTTPS Only**:
```javascript
// ✅ GOOD - HTTPS
const API_BASE = 'https://api.example.com';

// ❌ BAD - HTTP (insecure)
const API_BASE = 'http://api.example.com';
```

✅ **Error Handling (Don't Expose Sensitive Info)**:
```python
# ✅ GOOD - Generic error messages
try:
    user = authenticate(email, password)
except AuthenticationError:
    return {"error": "Invalid credentials"}

# ❌ BAD - Exposes information
except AuthenticationError as e:
    return {"error": f"User {email} not found"} # Reveals valid emails
```

---

### 4. **Realistic and Practical**

Use realistic scenarios and data, not toy examples.

**✅ Good - Realistic**:
```javascript
// E-commerce checkout flow
async function createOrder(cart) {
  const order = await api.orders.create({
    items: [
      {
        product_id: 'prod_nike_air_max_90',
        quantity: 1,
        price: 12000  // $120.00 in cents
      },
      {
        product_id: 'prod_athletic_socks_3pack',
        quantity: 2,
        price: 1499   // $14.99 in cents
      }
    ],
    shipping: {
      address: {
        line1: '123 Main St',
        city: 'San Francisco',
        state: 'CA',
        postal_code: '94102',
        country: 'US'
      },
      method: 'standard'  // 5-7 business days
    },
    payment_method: 'pm_card_visa',
    subtotal: 13499,
    shipping_cost: 500,
    tax: 1215,
    total: 15214
  });

  return order;
}
```

**❌ Bad - Toy Example**:
```javascript
async function createOrder() {
  const order = await api.orders.create({
    items: [{id: 1, qty: 2}],
    total: 100
  });
}
```

---

### 5. **Properly Commented**

Comment **why**, not **what**. Explain non-obvious decisions.

**✅ Good - Explains WHY**:
```python
# Use exponential backoff to handle transient network errors
# without overwhelming the server
max_retries = 3
for attempt in range(max_retries):
    try:
        return make_api_request()
    except NetworkError:
        if attempt == max_retries - 1:
            raise
        # Wait 2^attempt seconds before retrying (1s, 2s, 4s)
        time.sleep(2 ** attempt)
```

**❌ Bad - States the Obvious**:
```python
# Loop 3 times
for attempt in range(3):
    # Try to make request
    try:
        # Return the result
        return make_api_request()
    # Catch network error
    except NetworkError:
        # If last attempt
        if attempt == 2:
            # Raise the error
            raise
        # Sleep
        time.sleep(2 ** attempt)
```

---

### 6. **Idiomatic**

Follow language-specific conventions and best practices.

**Python - Idiomatic**:
```python
# ✅ GOOD - Pythonic
def process_users(user_ids):
    """Process multiple users efficiently."""
    # List comprehension for filtering
    active_users = [
        get_user(uid) for uid in user_ids
        if is_active(uid)
    ]

    # Context manager for resources
    with open('users.json', 'w') as f:
        json.dump(active_users, f, indent=2)

    # Dictionary comprehension
    user_map = {user['id']: user['name'] for user in active_users}

    return user_map

# ❌ BAD - Not Pythonic
def process_users(user_ids):
    active_users = []
    for uid in user_ids:
        if is_active(uid):
            user = get_user(uid)
            active_users.append(user)

    f = open('users.json', 'w')
    json.dump(active_users, f)
    f.close()

    user_map = {}
    for user in active_users:
        user_map[user['id']] = user['name']

    return user_map
```

**JavaScript - Idiomatic**:
```javascript
// ✅ GOOD - Modern JavaScript
async function fetchUsers(userIds) {
  // Array methods and async/await
  const users = await Promise.all(
    userIds.map(id => fetchUser(id))
  );

  // Destructuring and filter
  const activeUsers = users.filter(({ status }) => status === 'active');

  // Object method shorthand and template literals
  return {
    users: activeUsers,
    count: activeUsers.length,
    fetchedAt: new Date().toISOString()
  };
}

// ❌ BAD - Old-style JavaScript
function fetchUsers(userIds, callback) {
  var users = [];
  var count = 0;

  for (var i = 0; i < userIds.length; i++) {
    fetchUser(userIds[i], function(user) {
      users.push(user);
      count++;

      if (count === userIds.length) {
        callback(users);
      }
    });
  }
}
```

---

### 7. **Progressive Complexity**

Start simple, add complexity gradually.

**Progression Example - API Client**:

**Step 1: Minimal Example**
```javascript
// Simple GET request
const response = await fetch('https://api.example.com/users/123');
const user = await response.json();
console.log(user);
```

**Step 2: With Error Handling**
```javascript
// Add basic error handling
try {
  const response = await fetch('https://api.example.com/users/123');

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const user = await response.json();
  console.log(user);
} catch (error) {
  console.error('Failed to fetch user:', error);
}
```

**Step 3: Production-Ready**
```javascript
// Complete implementation with authentication, retries, and proper error handling
async function fetchUser(userId, options = {}) {
  const {
    apiKey = process.env.API_KEY,
    maxRetries = 3,
    timeout = 5000
  } = options;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const response = await fetch(
        `https://api.example.com/users/${userId}`,
        {
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
          },
          signal: controller.signal
        }
      );

      clearTimeout(timeoutId);

      if (!response.ok) {
        // Retry on 5xx errors
        if (response.status >= 500 && attempt < maxRetries - 1) {
          await sleep(Math.pow(2, attempt) * 1000);
          continue;
        }

        const error = await response.json();
        throw new Error(`API error: ${error.message}`);
      }

      return await response.json();

    } catch (error) {
      if (attempt === maxRetries - 1) {
        throw error;
      }

      // Exponential backoff
      await sleep(Math.pow(2, attempt) * 1000);
    }
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

---

## Multi-Language Code Samples

### Language Priority

**Tier 1** (Must have for all examples):
- JavaScript/TypeScript (Node.js)
- Python
- curl (bash)

**Tier 2** (Should have for important examples):
- Go
- Ruby
- PHP
- Java

**Tier 3** (Nice to have):
- C# (.NET)
- Rust
- Swift
- Kotlin

### Consistent Structure Across Languages

Show the **same example** in multiple languages:

**Python**:
```python
import requests

def create_payment(amount, currency):
    response = requests.post(
        'https://api.example.com/v1/payments',
        auth=('api_key', ''),
        json={
            'amount': amount,
            'currency': currency
        }
    )
    response.raise_for_status()
    return response.json()

payment = create_payment(1000, 'usd')
print(f"Payment created: {payment['id']}")
```

**JavaScript**:
```javascript
async function createPayment(amount, currency) {
  const response = await fetch('https://api.example.com/v1/payments', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ amount, currency })
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  return await response.json();
}

const payment = await createPayment(1000, 'usd');
console.log(`Payment created: ${payment.id}`);
```

**curl**:
```bash
curl -X POST https://api.example.com/v1/payments \
  -u api_key: \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000,
    "currency": "usd"
  }'
```

---

## Code Sample Templates

### API Request Template

```markdown
## [Endpoint Description]

[Brief explanation of what this does]

### Request

```[language]
[Complete code sample with:
 - Imports
 - Authentication
 - Error handling
 - Realistic data
 - Comments for non-obvious parts]
```

### Response

```json
[Actual JSON response with realistic data]
```

### Error Handling

```[language]
[Code showing how to handle errors]
```
```

---

## Style Guide by Language

### Python

**Naming**:
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

**Best Practices**:
```python
# ✅ Use type hints
def create_user(email: str, name: str) -> dict:
    pass

# ✅ Use dataclasses for structured data
from dataclasses import dataclass

@dataclass
class User:
    id: str
    email: str
    name: str

# ✅ Use context managers
with open('file.txt') as f:
    data = f.read()

# ✅ Use f-strings
message = f"User {user.name} created"
```

### JavaScript/TypeScript

**Naming**:
- Functions/variables: `camelCase`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

**Best Practices**:
```javascript
// ✅ Use const/let, not var
const apiKey = process.env.API_KEY;
let retryCount = 0;

// ✅ Use async/await
async function fetchData() {
  const data = await api.get('/users');
  return data;
}

// ✅ Use destructuring
const { id, name, email } = user;

// ✅ Use template literals
const message = `User ${name} created`;

// ✅ Use arrow functions appropriately
const double = (x) => x * 2;
```

### Go

**Naming**:
- Functions/variables: `camelCase` (exported: `PascalCase`)
- Packages: lowercase

**Best Practices**:
```go
// ✅ Error handling
func GetUser(id string) (*User, error) {
    user, err := fetchUser(id)
    if err != nil {
        return nil, fmt.Errorf("failed to fetch user: %w", err)
    }
    return user, nil
}

// ✅ Defer for cleanup
func processFile(filename string) error {
    f, err := os.Open(filename)
    if err != nil {
        return err
    }
    defer f.Close()

    // Process file...
    return nil
}

// ✅ Struct initialization
user := &User{
    ID:    "usr_123",
    Email: "alice@example.com",
    Name:  "Alice Johnson",
}
```

---

## Testing Code Samples

### Manual Testing Checklist

Before publishing any code sample:

- [ ] Copy code exactly as written
- [ ] Run in fresh environment (clean VM/container)
- [ ] Verify it produces expected output
- [ ] Test error scenarios
- [ ] Check for security issues
- [ ] Verify dependencies are listed
- [ ] Test with minimum required versions
- [ ] Proofread comments

### Automated Testing

**Extract and test code blocks from markdown**:

```python
# test_code_samples.py
import subprocess
import re
from pathlib import Path

def test_python_code_samples():
    """Test all Python code samples in documentation."""
    docs_dir = Path('docs')

    for md_file in docs_dir.rglob('*.md'):
        code_blocks = extract_python_blocks(md_file)

        for i, code in enumerate(code_blocks):
            # Skip blocks marked as non-executable
            if '# test: skip' in code:
                continue

            print(f"Testing {md_file}:block-{i}")

            # Create temp file
            tmp_file = Path(f'/tmp/test_{md_file.stem}_{i}.py')
            tmp_file.write_text(code)

            # Run code
            result = subprocess.run(
                ['python', str(tmp_file)],
                capture_output=True,
                timeout=30
            )

            assert result.returncode == 0, \
                f"Code sample failed:\n{result.stderr.decode()}"

def extract_python_blocks(md_file):
    """Extract Python code blocks from markdown."""
    content = md_file.read_text()
    pattern = r'```python\n(.*?)```'
    return re.findall(pattern, content, re.DOTALL)
```

---

## Quality Checklist

Every code sample must pass these checks:

**Completeness**:
- [ ] Includes all necessary imports
- [ ] Includes all dependencies (in requirements.txt or package.json)
- [ ] Can run without modification (except API keys)
- [ ] Produces documented output

**Security**:
- [ ] No hardcoded credentials
- [ ] Uses environment variables or config files
- [ ] Includes input validation
- [ ] Uses HTTPS, not HTTP
- [ ] Follows OWASP best practices

**Quality**:
- [ ] Follows language conventions
- [ ] Includes error handling
- [ ] Has appropriate comments
- [ ] Uses realistic data
- [ ] Is properly formatted (linted)

**Testing**:
- [ ] Manually tested successfully
- [ ] Automated test exists (if applicable)
- [ ] Works with specified language version
- [ ] Error cases tested

**Documentation**:
- [ ] Purpose is explained
- [ ] Prerequisites are listed
- [ ] Expected output is shown
- [ ] Next steps are provided

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Review Cycle**: Quarterly
**Automation**: All code samples tested in CI/CD

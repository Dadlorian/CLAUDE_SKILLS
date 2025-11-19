# Troubleshooting Guide Patterns

## Overview

Effective troubleshooting documentation helps developers solve problems quickly. This guide provides proven patterns for troubleshooting content.

---

## Structure Pattern

### Error-Solution Format

```markdown
## Error: "Connection timeout"

**Symptom**: API requests fail with timeout after 30 seconds

**Cause**: Network connectivity issues or server overload

**Solution**:

1. **Check your network connection**
   ```bash
   curl -I https://api.example.com
   ```

2. **Verify the API status**: [status.example.com](https://status.example.com)

3. **Increase timeout in your code**:
   ```javascript
   const response = await fetch(url, {
     timeout: 60000  // 60 seconds
   });
   ```

4. **Contact support** if the issue persists

**Prevention**: Implement retry logic with exponential backoff
```

---

## Common Patterns

### 1. Error Message → Solution

**Best for**: Specific error messages

```markdown
### Error: "Invalid API key"

**Message**: `{"error": "Invalid API key"}`

**Cause**: API key is incorrect, expired, or missing

**Solution**:
1. Verify you copied the complete key
2. Check for extra spaces
3. Ensure you're using the correct environment (test vs. live)
4. Generate a new key if needed

**Code example**:
```javascript
// ✅ Correct
const apiKey = process.env.API_KEY.trim();

// ❌ Common mistake
const apiKey = 'sk_live_abc123...';  // Incomplete key
```
```

### 2. Symptom → Diagnosis → Solution

**Best for**: Complex issues

```markdown
### Symptom: Slow API responses

**Diagnosis**:

1. **Check response time**:
   ```bash
   curl -w "@curl-format.txt" -o /dev/null -s https://api.example.com/users
   ```

2. **Identify bottleneck**:
   - Network latency: > 200ms
   - Server processing: Check logs
   - Database queries: Enable query logging

**Solutions by cause**:

**If network latency**:
- Use a CDN or edge locations
- Choose server closer to users

**If server processing**:
- Reduce payload size
- Use pagination
- Implement caching

**If database queries**:
- Add database indexes
- Use database caching
- Optimize queries
```

### 3. Decision Tree

**Best for**: Multiple possible causes

```markdown
## Troubleshooting Payment Failures

**Is the error 400 Bad Request?**
→ Yes: [Check validation errors](#validation-errors)
→ No: Continue

**Is the error 401 Unauthorized?**
→ Yes: [Verify API key](#api-key-issues)
→ No: Continue

**Is the error 402 Payment Required?**
→ Yes: [Check account status](#account-status)
→ No: [Contact support](#support)
```

---

## Best Practices

### ✅ Do

- **Start with the symptom**: What the user sees
- **Provide clear steps**: Numbered, actionable instructions
- **Include code examples**: Show the fix
- **Explain why**: Help prevent future issues
- **Link to related docs**: Provide context

### ❌ Don't

- **Blame the user**: "You forgot to..." → "The API key is missing"
- **Use jargon**: Explain technical terms
- **Provide too many options**: Prioritize likely solutions
- **Omit examples**: Show, don't just tell

---

## FAQ Pattern

```markdown
## Frequently Asked Questions

### How do I reset my API key?

1. Sign in to your [dashboard](https://example.com/dashboard)
2. Navigate to **API Keys**
3. Click the **⋮** menu next to your key
4. Select **Regenerate**
5. Update your application with the new key

**Warning**: The old key stops working immediately.

### Why am I getting rate limited?

**Cause**: You're exceeding 100 requests/second

**Solution**:
1. Check the `X-RateLimit-Remaining` header
2. Implement exponential backoff
3. Upgrade to a higher plan if needed

**Example retry logic**:
```javascript
async function withRetry(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (error.status === 429 && i < maxRetries - 1) {
        const delay = Math.pow(2, i) * 1000;
        await sleep(delay);
        continue;
      }
      throw error;
    }
  }
}
```
```

---

## Diagnostic Commands

Provide copy-paste commands for debugging:

```markdown
## Debugging Tools

### Check API connectivity
```bash
curl -I https://api.example.com
```

### Test API key
```bash
curl -u YOUR_API_KEY: https://api.example.com/v1/test
```

### View detailed request
```bash
curl -v https://api.example.com/v1/users
```

### Measure response time
```bash
curl -w "Time: %{time_total}s\n" -o /dev/null -s https://api.example.com/v1/users
```
```

---

## Self-Service Troubleshooting

Guide users to solve problems themselves:

```markdown
## Before contacting support

1. **Check the status page**: [status.example.com](https://status.example.com)
2. **Review recent changes**: Did you modify your code recently?
3. **Check the logs**: Look for error messages in your application logs
4. **Test in sandbox**: Does the issue occur in test mode?
5. **Review documentation**: Check the [API Reference](./api-reference.md)

**If the issue persists**, contact support with:
- Request ID (from error response)
- Full error message
- Steps to reproduce
- Code sample (remove sensitive data)
```

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Goal**: Enable self-service problem resolution

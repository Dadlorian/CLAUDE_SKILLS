# Interactive API Integration Playground

A hands-on learning platform for mastering API integration with modern JavaScript. Run, experiment, and learn with live executable examples.

## Features

- Interactive, runnable examples
- Real-time code execution
- No setup required - works in browser
- Progressive learning path
- Best practices and patterns

## Getting Started

### Installation

```bash
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

Open your browser to `http://localhost:3000`

### Build

Create an optimized production build:

```bash
npm run build
```

## Examples

### 1. Basic Fetch

Learn the fundamentals of making HTTP requests.

**Topics:**
- Fetch API basics
- Response handling
- Error catching
- Loading states
- JSON parsing

### 2. Advanced State Management

Master complex patterns for managing API data.

**Topics:**
- Caching strategies
- Request deduplication
- Stale-while-revalidate
- Optimistic updates
- Cache invalidation

### 3. Form Integration

Integrate HTML forms with API endpoints.

**Topics:**
- Form submission
- Data validation
- Error handling
- POST/PUT requests
- Success feedback

### 4. Error Handling

Robust error handling for production applications.

**Topics:**
- Error classification
- Retry logic
- Timeout handling
- Fallback strategies
- Circuit breaker pattern

## Learning Path

1. **Start with "Basic Fetch"**
   - Understand how fetch works
   - Learn request/response lifecycle
   - Master error handling basics

2. **Move to "Advanced State"**
   - Implement caching
   - Handle concurrent requests
   - Optimize performance

3. **Practice "Form Integration"**
   - Build real forms
   - Connect to APIs
   - Validate user input

4. **Master "Error Handling"**
   - Implement retry logic
   - Handle timeouts
   - Create resilient apps

## Code Examples

All examples are designed to be:
- **Runnable** - Click and see results immediately
- **Modifiable** - Change code and see impact instantly
- **Documented** - Clear explanations and best practices
- **Real-world** - Production-ready patterns

## Key Concepts

### HTTP Methods

```javascript
// GET - Retrieve data
const data = await fetch('/api/endpoint')

// POST - Create data
fetch('/api/endpoint', { method: 'POST', body: data })

// PUT - Update data
fetch('/api/endpoint', { method: 'PUT', body: data })

// DELETE - Remove data
fetch('/api/endpoint', { method: 'DELETE' })
```

### State Management

```javascript
const [data, setData] = useState(null)
const [loading, setLoading] = useState(false)
const [error, setError] = useState(null)

// Fetch pattern
setLoading(true)
try {
  const result = await fetchData()
  setData(result)
} catch (err) {
  setError(err)
} finally {
  setLoading(false)
}
```

### Error Handling

```javascript
// Try-catch
try {
  const data = await fetch(url)
} catch (err) {
  handleError(err)
}

// Retry with backoff
for (let i = 0; i < maxRetries; i++) {
  try {
    return await fetch(url)
  } catch (err) {
    if (i === maxRetries - 1) throw err
    await delay(Math.pow(2, i) * 1000)
  }
}
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## API for Examples

All examples use public APIs:
- JSONPlaceholder - Fake online REST API for testing
- Demo endpoints for local testing

## Best Practices Demonstrated

1. **Asynchronous Programming**
   - async/await
   - Promise handling
   - Error propagation

2. **State Management**
   - Loading states
   - Error handling
   - Cache management

3. **API Integration**
   - Proper HTTP methods
   - Request headers
   - Response handling

4. **User Experience**
   - Loading indicators
   - Error messages
   - Success feedback

5. **Performance**
   - Caching strategies
   - Request optimization
   - Bundle size

## Deployment

### Deploy to Vercel

```bash
vercel deploy
```

### Deploy to Netlify

```bash
npm run build
# Upload dist/ folder
```

### Deploy to GitHub Pages

```bash
npm run build
# Configure gh-pages
```

## Resources

- [MDN Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [Async/Await Guide](https://javascript.info/async-await)
- [React Documentation](https://react.dev)
- [HTTP Status Codes](https://httpwg.org/specs/rfc7231.html)
- [REST API Best Practices](https://restfulapi.net)

## License

MIT

## Contributing

Feel free to modify and extend these examples for your learning. This is an educational resource!

## Support

- Check the code comments for explanations
- Read the "Code Walkthrough" sections
- Experiment by modifying the examples
- Try different scenarios and error cases

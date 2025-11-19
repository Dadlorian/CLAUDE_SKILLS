# Developer Guides - Complete Examples & Tutorials

This directory contains three complete production-ready projects for learning and teaching API integration:

## Directory Structure

```
src/
├── complete-api-integration-tutorial/     # Full React + API tutorial
├── framework-integration-examples/         # Next.js, Vue, Angular examples
├── interactive-playground/                 # CodeSandbox interactive examples
└── MASTER_README.md                        # This file
```

## 1. Complete API Integration Tutorial

**Location:** `/complete-api-integration-tutorial/`

A comprehensive React + API integration example with production-ready code, tests, and deployment configuration.

### Features
- React 18 with modern hooks
- React Query for server state management
- Axios for HTTP requests
- Full CRUD operations
- Error boundaries and error handling
- Form validation
- Responsive design
- Comprehensive test suite (Vitest)
- Docker & Vercel deployment configs

### Quick Start
```bash
cd complete-api-integration-tutorial
npm install
npm run dev                    # Start frontend (port 3000)
npm run server                 # Start mock API (port 3001)
```

### Project Structure
```
complete-api-integration-tutorial/
├── public/
│   └── index.html
├── src/
│   ├── components/           # React components
│   │   ├── UserList.jsx
│   │   ├── UserForm.jsx
│   │   └── ErrorBoundary.jsx
│   ├── styles/               # Component styles
│   ├── App.jsx               # Main app component
│   ├── main.jsx              # React DOM entry
│   └── index.css             # Global styles
├── tests/                    # Test files
│   ├── App.test.jsx
│   └── setup.js
├── scripts/
│   └── mock-server.js        # Express mock API
├── package.json
├── vite.config.js
├── Dockerfile
├── docker-compose.yml
├── vercel.json
└── README.md
```

### Key Learning Points
- Modern React patterns (hooks, composition)
- Server state management with React Query
- API integration with Axios
- Error handling and error boundaries
- Form handling and validation
- Testing React components
- Production deployment

### Deployment
- **Vercel:** `vercel deploy`
- **Docker:** `docker-compose up`
- **Local:** `npm run build && npm run preview`

---

## 2. Framework Integration Examples

**Location:** `/framework-integration-examples/`

Complete examples for three major JavaScript frameworks: Next.js, Vue.js, and Angular.

### Structure
```
framework-integration-examples/
├── nextjs/                   # Next.js implementation
├── vue/                      # Vue 3 implementation
├── angular/                  # Angular implementation
├── shared/                   # Shared utilities
└── README.md                 # Framework comparison
```

### Next.js Example
- Server-side and client-side rendering
- API routes for proxy
- SWR for data fetching
- Built-in optimizations

```bash
cd nextjs
npm install
npm run dev
```

### Vue 3 Example
- Composition API
- Reactive state management
- Scoped styles
- Simple and elegant

```bash
cd vue
npm install
npm run dev
```

### Angular Example
- Standalone components
- Dependency injection
- RxJS observables
- Type-safe services

```bash
cd angular
npm install
npm start
```

### Key Features
All examples implement:
- User management (CRUD)
- API integration
- Error handling
- Form validation
- Responsive design
- Loading states

### Comparison Table

| Feature | Next.js | Vue | Angular |
|---------|---------|-----|---------|
| Learning Curve | Easy | Easy | Moderate |
| Bundle Size | Medium | Small | Large |
| Deployment | Easy | Easy | Easy |
| Full-stack | Yes | No | No |
| TypeScript | Optional | Optional | Built-in |

---

## 3. Interactive Playground

**Location:** `/interactive-playground/`

A hands-on learning platform with runnable, modifiable examples for mastering API integration concepts.

### Features
- Interactive, live-running examples
- Progressive learning path
- No setup required (browser-based)
- Code walkthrough for each example
- Best practices and patterns

### Examples Included

#### 1. Basic Fetch
Learn HTTP fundamentals with the Fetch API.
- GET requests
- Response handling
- Error catching
- Loading states

#### 2. Advanced State
Master complex state management patterns.
- Caching strategies
- Request deduplication
- Stale-while-revalidate
- Optimistic updates

#### 3. Form Integration
Connect HTML forms to APIs.
- Form submission
- Data validation
- POST/PUT requests
- Success feedback

#### 4. Error Handling
Robust error handling for production.
- Error classification
- Retry logic
- Timeout handling
- Fallback strategies
- Circuit breaker pattern

### Quick Start
```bash
cd interactive-playground
npm install
npm run dev
# Visit http://localhost:3000
```

### Project Structure
```
interactive-playground/
├── public/
│   └── index.html
├── src/
│   ├── pages/
│   │   ├── PlaygroundIndex.jsx      # Home page
│   │   ├── BasicExample.jsx          # Fetch basics
│   │   ├── AdvancedExample.jsx       # State management
│   │   ├── FormExample.jsx           # Form integration
│   │   └── ErrorHandling.jsx         # Error patterns
│   ├── utils/
│   │   └── api.js                    # API utilities
│   ├── App.jsx                       # Main app
│   ├── main.jsx                      # Entry point
│   ├── App.css                       # App styles
│   └── index.css                     # Global styles
├── package.json
├── vite.config.js
└── README.md
```

### Utilities Provided
- `fetchWithTimeout()` - Fetch with timeout
- `fetchWithRetry()` - Retry with exponential backoff
- `APICache` - Response caching
- `CircuitBreaker` - Prevent cascading failures
- `debounce()` - Rate limiting
- `throttle()` - Rate limiting

---

## Common Features Across All Projects

### 1. **Production-Ready Code**
- Error handling
- Loading states
- Validation
- Tests

### 2. **Deployment Options**
- Docker/Docker Compose
- Vercel
- GitHub Pages
- Netlify

### 3. **Development Experience**
- Hot reload
- Linting
- Code formatting
- Test coverage

### 4. **Documentation**
- README files
- Code comments
- Best practices
- Examples

---

## API Integration Patterns

### Pattern 1: Basic Fetch
```javascript
try {
  const response = await fetch('/api/data')
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  const data = await response.json()
  setData(data)
} catch (error) {
  setError(error.message)
}
```

### Pattern 2: With Retry
```javascript
for (let i = 0; i < maxRetries; i++) {
  try {
    return await fetch('/api/data')
  } catch (error) {
    if (i === maxRetries - 1) throw error
    await delay(1000 * Math.pow(2, i))
  }
}
```

### Pattern 3: With Cache
```javascript
if (cache.has('key')) {
  return cache.get('key')
}
const data = await fetch('/api/data')
cache.set('key', data)
return data
```

### Pattern 4: With Timeout
```javascript
const controller = new AbortController()
const timeout = setTimeout(() => controller.abort(), 5000)
try {
  return await fetch(url, { signal: controller.signal })
} finally {
  clearTimeout(timeout)
}
```

---

## Getting Started Guide

### For Beginners
1. Start with **Interactive Playground** → Basic Fetch
2. Run **Complete API Tutorial** locally
3. Explore one framework (Next.js recommended for beginners)
4. Practice with your own API

### For Intermediate
1. Study **Advanced State Management** in playground
2. Explore all **Framework Examples**
3. Implement error handling patterns
4. Set up testing

### For Advanced
1. Study **Error Handling** patterns
2. Implement caching strategies
3. Set up monitoring/logging
4. Optimize performance
5. Deploy to production

---

## Mock API Server

All projects can use the mock server included in the tutorial:

```bash
cd complete-api-integration-tutorial
npm run server
```

Or run Express directly:
```bash
node scripts/mock-server.js
```

**Available Endpoints:**
- `GET /api/users` - Get all users
- `GET /api/users/:id` - Get user by ID
- `POST /api/users` - Create user
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user

---

## Testing

Each project includes test setup:

```bash
# Run tests
npm test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

---

## Deployment

### Local Development
```bash
npm install
npm run dev
```

### Production Build
```bash
npm run build
npm run preview
```

### Docker
```bash
docker-compose up
# or
docker build -t app .
docker run -p 3000:3000 app
```

### Cloud Deployment
- **Vercel:** Import from Git, auto-deploy
- **Netlify:** Connect repository
- **AWS/Azure/GCP:** Use Docker image

---

## Key Resources

- [MDN Web Docs - Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [React Documentation](https://react.dev)
- [React Query](https://tanstack.com/query/latest)
- [Next.js Guide](https://nextjs.org/docs)
- [Vue 3 Docs](https://vuejs.org)
- [Angular Guide](https://angular.io/docs)
- [REST API Best Practices](https://restfulapi.net)
- [HTTP Status Codes](https://httpwg.org/specs/rfc7231.html)

---

## Learning Outcomes

After completing all three projects, you'll understand:

### Concepts
- HTTP methods and status codes
- Request/response lifecycle
- Async/await patterns
- Error handling strategies
- State management approaches
- Caching strategies

### Practical Skills
- Making API requests
- Handling responses
- Error recovery
- Form submission
- Loading states
- Data validation
- Testing API integration
- Deploying applications

### Best Practices
- User-friendly error messages
- Graceful degradation
- Performance optimization
- Security considerations
- Code organization
- Testing approaches
- Documentation standards

---

## Contributing

These are educational materials. Contributions to improve examples, documentation, or add new examples are welcome!

## License

MIT - Feel free to use these examples in your projects.

---

Last Updated: 2024
For questions or feedback, refer to the individual project READMEs.

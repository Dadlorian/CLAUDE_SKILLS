# Framework Integration Examples

Complete API integration examples for popular modern frameworks: Next.js, Vue.js, and Angular.

## Projects

### 1. Next.js Example

Full-stack Next.js application with API routes and client-side data fetching using SWR.

**Features:**
- Server-side and client-side rendering
- API routes for proxy
- SWR for data fetching and caching
- Built-in optimizations

**Run:**
```bash
cd nextjs
npm install
npm run dev
```

**Structure:**
```
nextjs/
├── pages/
│   ├── index.jsx (Main app)
│   └── api/health.js (API endpoint)
├── next.config.js
└── package.json
```

### 2. Vue 3 Example

Modern Vue 3 composition API with reactive state and HTTP requests using Axios.

**Features:**
- Composition API
- Reactive data binding
- Scoped styles
- Simple and elegant

**Run:**
```bash
cd vue
npm install
npm run dev
```

**Structure:**
```
vue/
├── src/
│   ├── App.vue (Main component)
│   ├── main.js
├── index.html
├── vite.config.js
└── package.json
```

### 3. Angular Example

Angular with standalone components, dependency injection, and reactive programming using RxJS.

**Features:**
- Standalone components
- Dependency injection
- Observable-based services
- TypeScript support

**Run:**
```bash
cd angular
npm install
npm start
```

**Structure:**
```
angular/
├── src/
│   ├── app/
│   │   ├── app.component.ts
│   │   ├── app.component.html
│   │   ├── app.component.css
│   │   └── services/
│   │       └── user.service.ts
│   └── main.ts
├── package.json
└── angular.json
```

## Common Features

All examples implement the same functionality:

- **User Management**: Create, read, update, delete users
- **API Integration**: HTTP requests to mock backend
- **State Management**: Local and server state handling
- **Error Handling**: Error messages and recovery
- **Responsive Design**: Mobile-friendly UI
- **Form Validation**: Input validation and feedback

## API Endpoints

All examples connect to the same mock API:

```
Base URL: http://localhost:3001/api

GET    /users      - Get all users
GET    /users/:id  - Get user by ID
POST   /users      - Create new user
PUT    /users/:id  - Update user
DELETE /users/:id  - Delete user
```

## Environment Setup

### Prerequisites

- Node.js 16+ or npm/yarn
- Mock API server running on port 3001

### Running the Mock API

From the parent directory:

```bash
npm run server
```

Or from each project directory:

```bash
npm run server
```

## Comparison

| Feature | Next.js | Vue | Angular |
|---------|---------|-----|---------|
| Learning Curve | Easy | Easy | Moderate |
| Bundle Size | Medium | Small | Large |
| State Management | Built-in | Ref/Reactive | Services |
| Data Fetching | SWR/fetch | Axios | HttpClient |
| TypeScript | Optional | Optional | Built-in |
| SSR Support | Yes | No (without adapter) | No |
| Ecosystem | Large | Medium | Large |

## Best Practices Demonstrated

### Next.js
- File-based routing
- API routes
- Image optimization
- Incremental Static Regeneration

### Vue
- Composition API
- Template syntax
- Scoped styles
- Lifecycle hooks

### Angular
- Decorators and services
- Reactive programming with RxJS
- Dependency injection
- Type safety

## Testing

Each example includes test setup:

**Next.js & Vue:**
```bash
npm test
npm run test:watch
```

**Angular:**
```bash
npm test
```

## Deployment

### Next.js
```bash
vercel deploy
```

### Vue
```bash
npm run build
# Deploy dist/ folder
```

### Angular
```bash
npm run build
# Deploy dist/ folder
```

## Documentation

- [Next.js Docs](https://nextjs.org/docs)
- [Vue 3 Docs](https://vuejs.org)
- [Angular Docs](https://angular.io/docs)

## Contributing

These are educational examples. Feel free to modify and extend them for your projects.

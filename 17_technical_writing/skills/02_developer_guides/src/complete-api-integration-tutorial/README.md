# Complete API Integration Tutorial

A production-ready React + API integration example demonstrating best practices for modern web development.

## Features

- **React 18** with modern hooks and patterns
- **React Query** for server state management
- **Axios** for HTTP requests
- **Full CRUD operations** with a mock API
- **Error handling** with error boundaries
- **Form validation** with user feedback
- **Responsive design** with CSS Grid
- **Comprehensive tests** with Vitest
- **Deployment ready** for Vercel and Docker

## Quick Start

### Prerequisites

- Node.js 16+ or npm

### Installation

```bash
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

In another terminal, start the mock API server:

```bash
npm run server
```

The app will be available at `http://localhost:3000`
The API will be available at `http://localhost:3001/api`

### Building

Build for production:

```bash
npm run build
```

Preview the build:

```bash
npm run preview
```

## Testing

Run tests:

```bash
npm test
```

Run tests in watch mode:

```bash
npm run test:watch
```

Generate coverage report:

```bash
npm run test:coverage
```

## Linting

Check for linting errors:

```bash
npm run lint
```

Fix linting errors:

```bash
npm run lint:fix
```

Format code:

```bash
npm run format
```

## Project Structure

```
complete-api-integration-tutorial/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── UserForm.jsx
│   │   ├── UserList.jsx
│   │   └── ErrorBoundary.jsx
│   ├── styles/
│   │   ├── UserForm.css
│   │   └── UserList.css
│   ├── App.jsx
│   ├── App.css
│   ├── main.jsx
│   └── index.css
├── tests/
│   ├── App.test.jsx
│   └── setup.js
├── scripts/
│   └── mock-server.js
├── package.json
├── vite.config.js
├── Dockerfile
├── docker-compose.yml
└── vercel.json
```

## API Endpoints

### Get All Users
```
GET /api/users
```

### Get User by ID
```
GET /api/users/:id
```

### Create User
```
POST /api/users
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "active": true
}
```

### Update User
```
PUT /api/users/:id
Content-Type: application/json

{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "role": "admin",
  "active": true
}
```

### Delete User
```
DELETE /api/users/:id
```

## Deployment

### Vercel

The project includes a `vercel.json` configuration for easy deployment:

```bash
vercel deploy
```

### Docker

Build and run with Docker:

```bash
docker build -t api-tutorial .
docker run -p 3000:3000 api-tutorial
```

Or use Docker Compose:

```bash
docker-compose up
```

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Configure your API URL:

```
VITE_API_URL=https://your-api-url.com/api
```

## Key Concepts Demonstrated

### State Management

The app demonstrates multiple state management approaches:

- **React Hooks** (useState) for local component state
- **React Query** for server state with caching and synchronization
- **Error states** with proper error handling

### API Integration

- Making HTTP requests with Axios
- Handling loading states
- Error handling and retry logic
- Optimistic updates (cache invalidation)
- Request/response transformation

### UI/UX Best Practices

- Loading indicators
- Error messages with recovery options
- Form validation with feedback
- Responsive design
- Accessible form elements
- Error boundaries for crash prevention

### Code Quality

- ESLint configuration
- Prettier formatting
- Unit tests with Vitest
- Test setup with React Testing Library

## Performance Optimizations

- Request caching with React Query
- Component memoization
- CSS optimization
- Build minification
- Tree shaking

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

MIT

## Contributing

This is an educational example. Feel free to use it as a reference for your own projects.

## Resources

- [React Documentation](https://react.dev)
- [React Query Documentation](https://tanstack.com/query/latest)
- [Axios Documentation](https://axios-http.com)
- [Vite Documentation](https://vitejs.dev)
- [Vitest Documentation](https://vitest.dev)

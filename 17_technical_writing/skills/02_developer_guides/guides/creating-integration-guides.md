# Creating Integration Guides: Framework-Specific Documentation

## Overview

Integration guides show developers how to use your product within specific frameworks, platforms, and ecosystems. A developer using React needs different guidance than one using Vue. This guide teaches you to create targeted, framework-specific documentation that meets developers where they are.

## What Are Integration Guides?

Integration guides document how your product works with specific technologies:
- **Frameworks**: React, Vue, Angular, Django, Rails, Laravel
- **Platforms**: AWS, Vercel, Netlify, Heroku, Docker
- **Languages**: JavaScript, Python, Go, Rust, Java
- **Databases**: PostgreSQL, MongoDB, Firebase, DynamoDB
- **Ecosystems**: iOS, Android, Web, Electron

## Why Integration Guides Matter

**Without Integration Guides:**
- Developers can't tell if your product works with their stack
- They spend hours trying to make it work
- Documentation feels generic and unhelpful
- Integration seems harder than it actually is

**With Good Integration Guides:**
- Developers quickly get your product working
- Reduced support burden
- Higher adoption rates
- Developers feel like the guide was written for them

## Part 1: Planning Your Integration

### Step 1.1: Choose Frameworks Worth Documenting

You can't document every framework. Choose strategically.

**Frameworks Worth Prioritizing:**
1. **Most popular** - Largest developer audience
2. **Best fit** - Where your product adds most value
3. **Explicitly requested** - What your users ask for most
4. **Strategic partners** - Part of your business strategy

**Action Items:**
1. List frameworks your users ask for most
2. Research usage statistics (via Stack Overflow, npm trends)
3. Prioritize by: popularity + user demand
4. Plan to add 1-2 per quarter based on demand

**Example Priority List:**
```
High Priority (do first):
- React (most popular, most user requests)
- Next.js (popular meta-framework)
- Node.js/Express (backend standard)

Medium Priority (do second):
- Vue (decent adoption, some requests)
- Python/Flask (popular in data/ML community)
- Docker (relevant for deployment)

Lower Priority (do later):
- Svelte (smaller community)
- Elixir (niche, fewer requests)
- .NET (lower adoption in our target market)
```

### Step 1.2: Understand Framework-Specific Needs

Each framework has different needs and patterns.

**Action Items:**
1. Research how your product fits into the framework
2. Learn the framework's conventions and patterns
3. Identify the specific integration points
4. Note any framework-specific gotchas

**Example Analysis: React Integration**

```
Product: Authentication library
Framework: React

How it fits in:
- Wraps the app with an auth provider
- Hooks access auth state
- Routes protect based on auth status

Framework patterns:
- Component composition
- Hooks for state management
- Context API for global state
- React Router for navigation

Integration points:
1. Install package via npm
2. Wrap app with <AuthProvider>
3. Use useAuth() hook
4. Protect routes with ProtectedRoute component

Gotchas:
- Async auth state on app load
- Testing authentication in tests
- Handling token refresh
- Mobile deeplinks with auth
```

### Step 1.3: Map the Integration Architecture

Understand exactly how your product works in their framework.

**Action Items:**
1. Create a diagram showing integration
2. Identify required setup steps
3. Note any configuration needed
4. Map where user code integrates

**Example Architecture Diagram:**
```
User's React App
    ↓
<AuthProvider> (from our library)
    ├── Manages auth state
    ├── Handles token refresh
    └── Provides useAuth() hook
        ↓
User's Components
    ├── useAuth() for auth state
    ├── ProtectedRoute component
    └── Logout functionality
```

### Step 1.4: Identify Integration Patterns

Different frameworks solve the same problems differently.

**Common Pattern Variations:**

**State Management:**
- React: Hooks, Context, Redux, Zustand
- Vue: Ref/Reactive, Pinia, Vuex
- Angular: Services, RxJS, NgRx

**API Requests:**
- JavaScript: Fetch, Axios, React Query
- Python: Requests, httpx, aiohttp
- Go: net/http, Resty

**Configuration:**
- Web: Environment variables, config files
- Mobile: Plist (iOS), XML (Android)
- Backend: Config files, environment variables

**Authentication:**
- Web: Cookies, localStorage, httpOnly
- Mobile: Keychain (iOS), Keystore (Android)
- Backend: API keys, JWT tokens

**Action Items:**
1. Identify 3-5 framework-specific patterns
2. Explain how your product uses each
3. Show code examples for each pattern

## Part 2: Structuring Integration Guides

### Step 2.1: Create a Consistent Template

Use this proven structure for all integration guides:

```markdown
# Integrating [Your Product] with [Framework]

## Overview
[1-2 sentences describing the integration]
[Link to example project]

## What You'll Need
- [Framework version requirements]
- [Package requirements]
- [Knowledge requirements]
- [Time estimate]

## Installation
[Step-by-step installation instructions]

## Basic Setup
[Minimal code to get it working]
[Shows the pattern]

## [Feature 1]: [Description]
[How to implement feature 1]
[Detailed code examples]
[Common patterns in this framework]

## [Feature 2]: [Description]
[How to implement feature 2]
[Detailed code examples]
[Common patterns in this framework]

## Advanced Patterns
[More complex use cases]
[Framework-specific optimizations]
[Performance considerations]

## Troubleshooting
[Common issues and solutions]
[Framework-specific gotchas]

## Example Project
[Links to working example]
[What to explore in the code]

## Next Steps
[What to do after integration]
[Links to framework docs]
[Links to feature documentation]
```

### Step 2.2: Write Clear Installation Instructions

Installation should be framework-specific.

**Action Items:**
1. Test installation in a fresh project
2. Note exact command needed
3. Specify framework/version used
4. Explain what the command does

**Example: React Installation**

```markdown
## Installation

For React applications, install our library via npm:

```bash
npm install @mycompany/auth-react
```

This installs:
- The authentication library
- React-specific hooks and components
- TypeScript types (if using TypeScript)

### Verify Installation

After installation, verify it worked:

```bash
npm list @mycompany/auth-react
```

You should see the version installed (e.g., 2.0.0).
```

**Example: Vue Installation**

```markdown
## Installation

For Vue 3 applications:

```bash
npm install @mycompany/auth-vue@3
```

For Vue 2 applications:

```bash
npm install @mycompany/auth-vue@2
```

Each version is optimized for its Vue version.
The Vue 3 version uses Composition API.
The Vue 2 version uses Options API.
```

### Step 2.3: Show Minimal Working Example

Get users running in the shortest path possible.

**Formula:**
1. Show the smallest working code
2. Explain what each piece does
3. Show the output/result
4. Link to next steps

**Example: React Basic Setup**

```markdown
## Basic Setup

Here's the minimal code to add authentication to your React app:

### Step 1: Wrap Your App

In your `main.jsx` or `index.js`:

```javascript
import { AuthProvider } from '@mycompany/auth-react';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider config={{ domain: 'YOUR_DOMAIN' }}>
      <App />
    </AuthProvider>
  </React.StrictMode>
);
```

This makes authentication available to all your components.

### Step 2: Use Authentication in Components

In any component:

```javascript
import { useAuth } from '@mycompany/auth-react';

export default function Profile() {
  const { user, logout } = useAuth();

  return (
    <div>
      <h1>Welcome, {user?.name}</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### What's Happening?
- `AuthProvider` wraps your app and initializes authentication
- `useAuth()` gives any component access to auth state
- `user` is null before login, contains user info after
- `logout()` clears the user session

### Next Up
Protect your routes and handle login. Jump to "Protecting Routes".
```

### Step 2.4: Document Feature Integration

For each feature, show framework-specific implementation.

**Formula:**
1. **What you're building** - 1-2 sentences
2. **Why this matters** - Context
3. **The code** - Framework-specific example
4. **Explanation** - What each line does
5. **Common variations** - How experienced developers might modify it
6. **Troubleshooting** - Issues specific to this framework

**Example: Protecting Routes in React**

```markdown
## Protecting Routes

You want certain pages to only show logged-in users.
This is called route protection.

### Using React Router 6

First, create a ProtectedRoute component:

```javascript
import { Navigate } from 'react-router-dom';
import { useAuth } from '@mycompany/auth-react';

export function ProtectedRoute({ children }) {
  const { user, isLoading } = useAuth();

  // While checking auth status, show loading
  if (isLoading) {
    return <div>Loading...</div>;
  }

  // User is logged in, show the page
  if (user) {
    return children;
  }

  // User not logged in, redirect to login
  return <Navigate to="/login" />;
}
```

Then protect routes in your router:

```javascript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from './components/ProtectedRoute';

<BrowserRouter>
  <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route
      path="/dashboard"
      element={
        <ProtectedRoute>
          <DashboardPage />
        </ProtectedRoute>
      }
    />
  </Routes>
</BrowserRouter>
```

### What's Happening?

- `useAuth()` gives us the current user and loading state
- `isLoading` is true while checking if user is logged in
- If loading, show a spinner (better UX than flashing login page)
- If user exists, show the protected page
- If no user, redirect to login with `<Navigate>`

### Common Variations

**Redirect to specific page after login:**
```javascript
if (!user) {
  return <Navigate to="/login" state={{ from: location }} />;
}
```

**Redirect to original page after login:**
```javascript
// In your login component, check state
const location = useLocation();
const from = location.state?.from?.pathname || '/dashboard';
// After successful login, navigate to from
```

**Multiple permission levels:**
```javascript
if (user?.role !== 'admin') {
  return <Navigate to="/unauthorized" />;
}
```

### Troubleshooting

**Issue: Page flashes before redirecting to login**
- Cause: Not checking `isLoading` state
- Fix: Show loading state while auth is being verified

**Issue: User logged out but can still see protected page**
- Cause: Stale user state
- Fix: Ensure `useAuth()` subscribes to logout events

**Issue: Can't access route params in ProtectedRoute**
- Cause: Params consumed by ProtectedRoute
- Fix: Pass params through as props to wrapped component
```

### Step 2.5: Explain Framework-Specific Patterns

Each framework has its own way of doing things.

**Action Items:**
1. Identify 3-5 framework-specific patterns
2. Show how your product works with each
3. Explain why that pattern exists
4. Provide code examples

**Example: Handling Async State in Different Frameworks**

```markdown
## Handling Async Authentication

Authentication often requires async operations (API calls, tokens).
Each framework handles this differently.

### React: useEffect Hook

```javascript
import { useEffect, useState } from 'react';
import { useAuth } from '@mycompany/auth-react';

export function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!user) return; // Only fetch if logged in

    fetch('/api/user-data', {
      headers: { Authorization: `Bearer ${user.token}` }
    })
      .then(r => r.json())
      .then(d => setData(d));
  }, [user]); // Re-fetch when user changes

  return <div>{data && <p>{data.message}</p>}</div>;
}
```

The `useEffect` hook runs after render.
It re-runs when dependencies (user) change.
This ensures we only fetch when the user is set.

### Vue 3: watchEffect Composition API

```javascript
import { ref, watchEffect } from 'vue';
import { useAuth } from '@mycompany/auth-vue';

export default {
  setup() {
    const { user } = useAuth();
    const data = ref(null);

    watchEffect(async () => {
      if (!user.value) return; // Only fetch if logged in

      const res = await fetch('/api/user-data', {
        headers: { Authorization: `Bearer ${user.value.token}` }
      });
      data.value = await res.json();
    }); // Automatically re-runs when user changes

    return { data };
  }
};
```

`watchEffect` watches reactive dependencies and re-runs.
It automatically tracks which variables it uses.
When `user` changes, it automatically fetches again.

### Angular: Service with RxJS

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '@mycompany/auth-angular';
import { switchMap } from 'rxjs/operators';

@Injectable()
export class DataService {
  constructor(
    private http: HttpClient,
    private auth: AuthService
  ) {}

  getUserData() {
    return this.auth.user$.pipe(
      switchMap(user => {
        if (!user) return of(null);
        return this.http.get('/api/user-data', {
          headers: { Authorization: `Bearer ${user.token}` }
        });
      })
    );
  }
}
```

`switchMap` combines the user stream and data stream.
Whenever user changes, it cancels the old request and starts new.
RxJS handles all the async orchestration.

### Summary

- **React**: useEffect hook for side effects
- **Vue**: watchEffect for reactive side effects
- **Angular**: RxJS streams for async data
- All achieve the same result; different patterns per framework
```

### Step 2.6: Document Advanced Patterns

After basic usage, show more sophisticated patterns.

**Advanced Topics to Cover:**
- Performance optimization (lazy loading, code splitting)
- Testing integration
- Error handling and edge cases
- Security best practices
- Production configuration
- Monitoring and debugging

**Example: Lazy Loading Authentication**

```markdown
## Advanced: Lazy Loading Auth

For large apps, you might want to load the auth library only
when needed, not on every page load.

### Dynamic Import in React

```javascript
import { lazy, Suspense } from 'react';

const AuthProvider = lazy(() =>
  import('@mycompany/auth-react').then(m => ({
    default: m.AuthProvider
  }))
);

export function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AuthProvider>
        {/* Your app */}
      </AuthProvider>
    </Suspense>
  );
}
```

This loads the auth library only when the app first renders.
Benefits:
- Smaller initial bundle
- Faster page load
- Auth library loads in background

Trade-offs:
- Brief loading flash
- Requires Suspense boundary
- Adds complexity
```

## Part 3: Code Examples and Testing

### Step 3.1: Provide Complete, Working Code

Users should copy-paste and have working code.

**Code Example Guidelines:**
1. **Complete** - Not snippets, working code
2. **Realistic** - Actual patterns developers use
3. **Tested** - Verified to work with the framework version
4. **Commented** - Non-obvious parts explained
5. **Copy-Paste Ready** - No missing imports or context

**Example: Good Code Block**

```javascript
// app.tsx - Complete working example for React with TypeScript
import React from 'react';
import { useAuth } from '@mycompany/auth-react';
import { Navigate } from 'react-router-dom';

interface PageProps {
  children: React.ReactNode;
}

/**
 * Protects routes from unauthenticated users.
 * While auth is loading, shows a spinner.
 * If user is not logged in, redirects to /login.
 */
export function ProtectedRoute({ children }: PageProps) {
  const { user, isLoading, error } = useAuth();

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  if (isLoading) {
    return <div>Loading authentication...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
```

### Step 3.2: Provide Example Projects

Nothing beats a working example.

**Action Items:**
1. Create a minimal example project for each framework
2. Set it up in a public repository (GitHub, GitLab)
3. Include clear README with setup instructions
4. Update when your product updates

**Example Project Structure:**
```
auth-react-example/
├── README.md (setup instructions)
├── package.json
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Profile.jsx
│   │   └── Dashboard.jsx
│   └── components/
│       └── ProtectedRoute.jsx
├── .env.example
└── .gitignore
```

**Example Project README:**
```markdown
# Authentication Integration Example: React

This is a working example of integrating our auth library with React.

## Setup

1. Clone this repo
2. Copy `.env.example` to `.env`
3. Add your auth domain to `.env`
4. Run `npm install`
5. Run `npm run dev`
6. Open http://localhost:5173

## What's Included

- User login/logout
- Protected routes
- User profile page
- Profile data loading

## Key Files to Explore

- `src/App.jsx` - Router setup with ProtectedRoute
- `src/components/ProtectedRoute.jsx` - Route protection logic
- `src/pages/Login.jsx` - Login page example
- `.env` - Configuration

## Try It

1. Click "Login"
2. Authenticate
3. See your profile
4. Try accessing /dashboard
5. Try logging out

## Next Steps

For more features, see:
- [Advanced Features](/docs/advanced)
- [API Reference](/docs/api)
```

### Step 3.3: Test Your Integration Guide

Verify the integration actually works as documented.

**Testing Checklist:**
- [ ] Create fresh project with that framework version
- [ ] Follow the guide exactly as written
- [ ] Installation works
- [ ] All code examples work exactly as shown
- [ ] No missing imports or dependencies
- [ ] Time estimates are accurate
- [ ] Links all work
- [ ] Code runs without errors

**Testing Process:**
```
1. Create fresh project
   npm create react-app test-integration

2. Follow the guide step-by-step

3. At each code example:
   - Verify it compiles
   - Verify it runs
   - Verify it produces expected output

4. Note any issues found
   - Unclear instructions
   - Missing imports
   - Code that doesn't work
   - Steps that take longer than estimated

5. Fix all issues before publishing
```

## Part 4: Comprehensive Example

Here's a complete (shortened) integration guide section:

```markdown
# Integrating Our API Library with Next.js

## Overview

This guide shows how to integrate our API library with Next.js
applications. We'll build a component that fetches data from our
API and displays it with proper error handling and loading states.

## What You Need

- Next.js 13+ (we'll use App Router)
- Node.js 16+
- 10 minutes

## Installation

```bash
npm install @mycompany/api-client
```

## Basic Setup

### Step 1: Create an API Client

Create `lib/api.ts`:

```typescript
import { createClient } from '@mycompany/api-client';

export const api = createClient({
  apiKey: process.env.NEXT_PUBLIC_API_KEY,
  baseUrl: 'https://api.example.com'
});
```

### Step 2: Use in a Component

Create `app/page.tsx`:

```typescript
'use client'; // Required for hooks

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function Home() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get('/items')
      .then(res => setData(res.data))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      {data?.items.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  );
}
```

This component:
- Fetches data when it mounts (`useEffect`)
- Shows loading state while fetching
- Shows error if something goes wrong
- Displays the data when ready

## Server-Side Fetching (Recommended)

Next.js is best used with server-side data fetching:

```typescript
// app/page.tsx - Server Component

async function getItems() {
  const res = await fetch('https://api.example.com/items', {
    headers: { 'Authorization': `Bearer ${process.env.API_KEY}` },
    // Revalidate every hour
    next: { revalidate: 3600 }
  });

  if (!res.ok) throw new Error('Failed to fetch');
  return res.json();
}

export default async function Home() {
  const data = await getItems();

  return (
    <div>
      {data.items.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  );
}
```

Benefits:
- API calls happen server-side
- API key stays secure
- Data is pre-rendered
- Better performance

## Error Handling

Always handle errors gracefully:

```typescript
'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export function ItemList() {
  const [state, setState] = useState({
    data: null,
    loading: true,
    error: null
  });

  useEffect(() => {
    api.get('/items')
      .then(res => setState({ data: res.data, loading: false, error: null }))
      .catch(err => setState({
        data: null,
        loading: false,
        error: err.message
      }));
  }, []);

  if (state.loading) return <Skeleton />;
  if (state.error) return <ErrorMessage msg={state.error} />;

  return <ItemsDisplay items={state.data.items} />;
}
```

Next.js specific errors:
- Check API key in `.env.local`
- Verify 'use client' if using hooks
- Check revalidate time for stale data

## Example Project

See the [Next.js integration example](https://github.com/...)
for a complete working application.
```

## Part 5: Maintenance and Updates

### Step 5.1: Keep Guides Updated

Outdated documentation is worse than no documentation.

**Update Triggers:**
- Framework releases major version
- Your product releases major update
- Syntax/best practices change
- Users report issues

**Maintenance Schedule:**
- Check quarterly for framework updates
- Update immediately after major releases
- Monitor GitHub issues for reported problems
- Refresh example projects annually

### Step 5.2: Track Framework Changes

Monitor when frameworks update.

**Tools:**
- Framework release notes (email subscriptions)
- Dependabot for example projects
- GitHub releases RSS feeds
- Communities and forums

**Action Items:**
1. Subscribe to framework release notes
2. Review breaking changes when they occur
3. Test your guides with new versions
4. Update guides if needed
5. Update example projects

## Complete Checklist: Before Publishing

### Planning
- [ ] Framework chosen based on popularity/demand
- [ ] Framework patterns researched and understood
- [ ] Integration architecture mapped
- [ ] Example project created and tested
- [ ] All required framework versions specified

### Content
- [ ] Installation instructions tested and work
- [ ] Basic setup example is minimal but complete
- [ ] All features documented with code examples
- [ ] Code examples are copy-paste ready
- [ ] Common variations shown
- [ ] Advanced patterns documented
- [ ] Troubleshooting covers framework-specific issues
- [ ] Links to framework documentation provided

### Testing
- [ ] Tested installation in fresh project
- [ ] All code examples run without errors
- [ ] Example project works as described
- [ ] Time estimates are accurate
- [ ] Framework-specific behaviors work correctly
- [ ] Error cases handled and tested

### Documentation
- [ ] Template structure followed
- [ ] Clear headings and organization
- [ ] Code blocks have language identifiers
- [ ] Framework-specific patterns explained
- [ ] Links to relevant docs
- [ ] Next steps are clear

### Maintenance
- [ ] Update schedule established
- [ ] Framework subscriptions set up
- [ ] Example project repo created
- [ ] Clear versioning strategy

## Key Takeaways

Great integration guides:
- **Match the framework** - Use framework patterns and idioms
- **Provide working examples** - Not just theory
- **Are framework-aware** - Address framework-specific concerns
- **Get tested** - In real projects with real frameworks
- **Stay current** - Updated with framework changes
- **Link broadly** - To framework and product docs

Remember: A developer using their favorite framework wants to see how your product works *with* that framework, not generic documentation.

## Resources

- [Creating Example Projects](/resources/examples)
- [Testing Integration Guides](/resources/testing)
- [Framework Pattern Guide](/resources/patterns)
- [Managing Multiple Versions](/resources/versioning)

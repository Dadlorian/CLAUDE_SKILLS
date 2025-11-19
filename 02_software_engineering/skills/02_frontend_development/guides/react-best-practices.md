# React Best Practices Guide

Comprehensive guide to building production-ready React applications.

## Component Structure

### Functional Components with Hooks

```typescript
import { useState, useEffect, useMemo, useCallback } from 'react';

interface UserCardProps {
  userId: string;
  onSelect?: (userId: string) => void;
}

export function UserCard({ userId, onSelect }: UserCardProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function fetchUser() {
      setLoading(true);
      try {
        const data = await api.getUser(userId);
        if (!cancelled) {
          setUser(data);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchUser();

    return () => {
      cancelled = true;
    };
  }, [userId]);

  const handleClick = useCallback(() => {
    onSelect?.(userId);
  }, [userId, onSelect]);

  if (loading) return <Skeleton />;
  if (!user) return <div>User not found</div>;

  return (
    <div onClick={handleClick}>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  );
}
```

## State Management

### Context API for Global State

```typescript
import { createContext, useContext, useState, ReactNode } from 'react';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string) => {
    const response = await api.login(email, password);
    setUser(response.user);
    localStorage.setItem('token', response.token);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

// Usage
function LoginButton() {
  const { login, isAuthenticated } = useAuth();

  if (isAuthenticated) return null;

  return <button onClick={() => login('user@example.com', 'password')}>Login</button>;
}
```

### React Query for Server State

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Fetch users
export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => api.getUsers(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Fetch single user
export function useUser(userId: string) {
  return useQuery({
    queryKey: ['users', userId],
    queryFn: () => api.getUser(userId),
    enabled: !!userId,
  });
}

// Create user mutation
export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateUserData) => api.createUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

// Component usage
function UserList() {
  const { data: users, isLoading, error } = useUsers();
  const createUser = useCreateUser();

  if (isLoading) return <LoadingSpinner />;
  if (error) return <Error message={error.message} />;

  return (
    <div>
      {users.map(user => (
        <UserCard key={user.id} user={user} />
      ))}
      <button
        onClick={() => createUser.mutate({
          name: 'New User',
          email: 'new@example.com',
        })}
      >
        Add User
      </button>
    </div>
  );
}
```

## Performance Optimization

### Memoization

```typescript
import { memo, useMemo, useCallback } from 'react';

// Memo component (skip re-render if props unchanged)
export const UserCard = memo(function UserCard({ user }: { user: User }) {
  return (
    <div>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  );
});

// useMemo for expensive calculations
function ProductList({ products }: { products: Product[] }) {
  const sortedProducts = useMemo(() => {
    return [...products].sort((a, b) => b.price - a.price);
  }, [products]);

  const totalPrice = useMemo(() => {
    return products.reduce((sum, p) => sum + p.price, 0);
  }, [products]);

  return (
    <div>
      <p>Total: ${totalPrice}</p>
      {sortedProducts.map(p => (
        <ProductCard key={p.id} product={p} />
      ))}
    </div>
  );
}

// useCallback for function memoization
function SearchableList({ items }: { items: Item[] }) {
  const [query, setQuery] = useState('');

  const handleSearch = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  }, []);

  const filteredItems = useMemo(() => {
    return items.filter(item =>
      item.name.toLowerCase().includes(query.toLowerCase())
    );
  }, [items, query]);

  return (
    <div>
      <input value={query} onChange={handleSearch} />
      {filteredItems.map(item => (
        <ItemCard key={item.id} item={item} />
      ))}
    </div>
  );
}
```

### Code Splitting

```typescript
import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// Lazy load components
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Profile = lazy(() => import('./pages/Profile'));
const Settings = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<LoadingPage />}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

## Custom Hooks

### useDebounce

```typescript
import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// Usage
function SearchComponent() {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  useEffect(() => {
    if (debouncedSearchTerm) {
      // API call only after user stops typing for 300ms
      searchAPI(debouncedSearchTerm);
    }
  }, [debouncedSearchTerm]);

  return (
    <input
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      placeholder="Search..."
    />
  );
}
```

### useLocalStorage

```typescript
import { useState, useEffect } from 'react';

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore =
        value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue] as const;
}

// Usage
function ThemeSelector() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');

  return (
    <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
      Current theme: {theme}
    </button>
  );
}
```

## Form Handling

### React Hook Form

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  name: z.string().min(1, 'Name is required'),
});

type FormData = z.infer<typeof schema>;

export function RegistrationForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    try {
      await api.register(data);
      // Success handling
    } catch (error) {
      // Error handling
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <input {...register('email')} placeholder="Email" />
        {errors.email && <span>{errors.email.message}</span>}
      </div>

      <div>
        <input {...register('password')} type="password" placeholder="Password" />
        {errors.password && <span>{errors.password.message}</span>}
      </div>

      <div>
        <input {...register('name')} placeholder="Name" />
        {errors.name && <span>{errors.name.message}</span>}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Register'}
      </button>
    </form>
  );
}
```

## Error Boundaries

```typescript
import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error reporting service
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div>
          <h2>Something went wrong</h2>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage
function App() {
  return (
    <ErrorBoundary>
      <MyComponent />
    </ErrorBoundary>
  );
}
```

## Testing

### Component Testing

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { UserCard } from './UserCard';

describe('UserCard', () => {
  it('renders user information', () => {
    const user = { id: '1', name: 'John Doe', email: 'john@example.com' };

    render(<UserCard user={user} />);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('calls onSelect when clicked', () => {
    const user = { id: '1', name: 'John', email: 'john@example.com' };
    const onSelect = jest.fn();

    render(<UserCard user={user} onSelect={onSelect} />);

    fireEvent.click(screen.getByText('John'));
    expect(onSelect).toHaveBeenCalledWith(user.id);
  });

  it('shows loading state', () => {
    render(<UserCard userId="1" />);
    expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument();
  });
});
```

## Best Practices Summary

✅ Use functional components with hooks
✅ Memoize expensive calculations (useMemo)
✅ Memoize callback functions (useCallback)
✅ Use React.memo for pure components
✅ Implement code splitting
✅ Use React Query for server state
✅ Implement error boundaries
✅ Write comprehensive tests
✅ Use TypeScript for type safety
✅ Follow accessibility guidelines
✅ Optimize images and assets

## References

- React Documentation: https://react.dev/
- React Query: https://tanstack.com/query
- React Hook Form: https://react-hook-form.com/
- Testing Library: https://testing-library.com/

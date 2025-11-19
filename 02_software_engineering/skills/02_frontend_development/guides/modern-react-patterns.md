# Modern React Patterns and Best Practices

Comprehensive guide to building production-ready React applications using modern patterns and best practices.

## Table of Contents

1. [Component Patterns](#component-patterns)
2. [State Management](#state-management)
3. [Performance Optimization](#performance-optimization)
4. [Data Fetching](#data-fetching)
5. [Form Handling](#form-handling)
6. [Error Handling](#error-handling)
7. [TypeScript Integration](#typescript-integration)

## Component Patterns

### Compound Components

**Pattern for creating flexible, composable components**:

```typescript
// components/Tabs/Tabs.tsx
import { createContext, useContext, useState, ReactNode } from 'react';

interface TabsContextValue {
  activeTab: string;
  setActiveTab: (id: string) => void;
}

const TabsContext = createContext<TabsContextValue | null>(null);

function useTabs() {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error('Tabs compound components must be used within Tabs');
  }
  return context;
}

interface TabsProps {
  defaultTab: string;
  children: ReactNode;
}

export function Tabs({ defaultTab, children }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab);

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
}

interface TabListProps {
  children: ReactNode;
}

Tabs.List = function TabList({ children }: TabListProps) {
  return <div className="tab-list" role="tablist">{children}</div>;
};

interface TabProps {
  id: string;
  children: ReactNode;
}

Tabs.Tab = function Tab({ id, children }: TabProps) {
  const { activeTab, setActiveTab } = useTabs();
  const isActive = activeTab === id;

  return (
    <button
      role="tab"
      aria-selected={isActive}
      className={`tab ${isActive ? 'active' : ''}`}
      onClick={() => setActiveTab(id)}
    >
      {children}
    </button>
  );
};

interface PanelProps {
  id: string;
  children: ReactNode;
}

Tabs.Panel = function Panel({ id, children }: PanelProps) {
  const { activeTab } = useTabs();

  if (activeTab !== id) return null;

  return (
    <div role="tabpanel" className="tab-panel">
      {children}
    </div>
  );
};

// Usage
function App() {
  return (
    <Tabs defaultTab="profile">
      <Tabs.List>
        <Tabs.Tab id="profile">Profile</Tabs.Tab>
        <Tabs.Tab id="settings">Settings</Tabs.Tab>
        <Tabs.Tab id="billing">Billing</Tabs.Tab>
      </Tabs.List>

      <Tabs.Panel id="profile">
        <ProfileContent />
      </Tabs.Panel>
      <Tabs.Panel id="settings">
        <SettingsContent />
      </Tabs.Panel>
      <Tabs.Panel id="billing">
        <BillingContent />
      </Tabs.Panel>
    </Tabs>
  );
}
```

### Render Props Pattern

```typescript
interface MousePositionProps {
  children: (position: { x: number; y: number }) => ReactNode;
}

function MousePosition({ children }: MousePositionProps) {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return <>{children(position)}</>;
}

// Usage
function App() {
  return (
    <MousePosition>
      {({ x, y }) => (
        <div>
          Mouse position: {x}, {y}
        </div>
      )}
    </MousePosition>
  );
}
```

### Custom Hooks Pattern

```typescript
// hooks/useDebounce.ts
import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// hooks/useLocalStorage.ts
import { useState, useEffect } from 'react';

export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  const setValue = (value: T) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue];
}

// hooks/useAsync.ts
import { useState, useEffect, useCallback } from 'react';

interface AsyncState<T> {
  data: T | null;
  error: Error | null;
  loading: boolean;
}

export function useAsync<T>(
  asyncFunction: () => Promise<T>,
  immediate = true
) {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    error: null,
    loading: false,
  });

  const execute = useCallback(async () => {
    setState({ data: null, error: null, loading: true });

    try {
      const data = await asyncFunction();
      setState({ data, error: null, loading: false });
    } catch (error) {
      setState({ data: null, error: error as Error, loading: false });
    }
  }, [asyncFunction]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return { ...state, execute };
}

// Usage
function UserProfile({ userId }: { userId: string }) {
  const { data, loading, error } = useAsync(
    () => fetch(`/api/users/${userId}`).then(r => r.json()),
    true
  );

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!data) return null;

  return <div>{data.name}</div>;
}
```

### Higher-Order Components (HOC)

```typescript
// hocs/withAuth.tsx
import { ComponentType } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Navigate } from 'react-router-dom';

export function withAuth<P extends object>(
  Component: ComponentType<P>
): ComponentType<P> {
  return function AuthenticatedComponent(props: P) {
    const { user, loading } = useAuth();

    if (loading) {
      return <div>Loading...</div>;
    }

    if (!user) {
      return <Navigate to="/login" />;
    }

    return <Component {...props} />;
  };
}

// Usage
const ProtectedDashboard = withAuth(Dashboard);
```

## State Management

### Context + Reducer Pattern

```typescript
// context/CartContext.tsx
import { createContext, useContext, useReducer, ReactNode } from 'react';

interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

interface CartState {
  items: CartItem[];
  total: number;
}

type CartAction =
  | { type: 'ADD_ITEM'; payload: CartItem }
  | { type: 'REMOVE_ITEM'; payload: string }
  | { type: 'UPDATE_QUANTITY'; payload: { id: string; quantity: number } }
  | { type: 'CLEAR_CART' };

const CartContext = createContext<{
  state: CartState;
  dispatch: React.Dispatch<CartAction>;
} | null>(null);

function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case 'ADD_ITEM': {
      const existingItem = state.items.find(
        item => item.id === action.payload.id
      );

      if (existingItem) {
        const items = state.items.map(item =>
          item.id === action.payload.id
            ? { ...item, quantity: item.quantity + action.payload.quantity }
            : item
        );
        return {
          items,
          total: items.reduce((sum, item) => sum + item.price * item.quantity, 0),
        };
      }

      const items = [...state.items, action.payload];
      return {
        items,
        total: items.reduce((sum, item) => sum + item.price * item.quantity, 0),
      };
    }

    case 'REMOVE_ITEM': {
      const items = state.items.filter(item => item.id !== action.payload);
      return {
        items,
        total: items.reduce((sum, item) => sum + item.price * item.quantity, 0),
      };
    }

    case 'UPDATE_QUANTITY': {
      const items = state.items.map(item =>
        item.id === action.payload.id
          ? { ...item, quantity: action.payload.quantity }
          : item
      );
      return {
        items,
        total: items.reduce((sum, item) => sum + item.price * item.quantity, 0),
      };
    }

    case 'CLEAR_CART':
      return { items: [], total: 0 };

    default:
      return state;
  }
}

export function CartProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(cartReducer, { items: [], total: 0 });

  return (
    <CartContext.Provider value={{ state, dispatch }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within CartProvider');
  }
  return context;
}

// Usage
function CartButton() {
  const { state, dispatch } = useCart();

  const addItem = () => {
    dispatch({
      type: 'ADD_ITEM',
      payload: { id: '1', name: 'Product', price: 10, quantity: 1 },
    });
  };

  return (
    <button onClick={addItem}>
      Cart ({state.items.length}) - ${state.total}
    </button>
  );
}
```

### Zustand State Management

```typescript
// stores/useUserStore.ts
import { create } from 'zustand';
import { persist, devtools } from 'zustand/middleware';

interface User {
  id: string;
  name: string;
  email: string;
}

interface UserState {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  updateProfile: (data: Partial<User>) => void;
}

export const useUserStore = create<UserState>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        loading: false,
        error: null,

        login: async (email, password) => {
          set({ loading: true, error: null });
          try {
            const response = await fetch('/api/auth/login', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email, password }),
            });

            if (!response.ok) {
              throw new Error('Login failed');
            }

            const user = await response.json();
            set({ user, loading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Unknown error',
              loading: false,
            });
          }
        },

        logout: () => {
          set({ user: null });
        },

        updateProfile: (data) => {
          set((state) => ({
            user: state.user ? { ...state.user, ...data } : null,
          }));
        },
      }),
      {
        name: 'user-storage',
        partialize: (state) => ({ user: state.user }),
      }
    )
  )
);

// Usage
function UserProfile() {
  const { user, updateProfile } = useUserStore();

  if (!user) return null;

  return (
    <div>
      <h1>{user.name}</h1>
      <button onClick={() => updateProfile({ name: 'New Name' })}>
        Update Name
      </button>
    </div>
  );
}
```

## Performance Optimization

### Memoization

```typescript
import { memo, useMemo, useCallback } from 'react';

// Memo component
interface ExpensiveComponentProps {
  data: number[];
  onItemClick: (id: number) => void;
}

export const ExpensiveComponent = memo(function ExpensiveComponent({
  data,
  onItemClick,
}: ExpensiveComponentProps) {
  const processedData = useMemo(() => {
    console.log('Processing data...');
    return data.map(item => item * 2);
  }, [data]);

  return (
    <ul>
      {processedData.map(item => (
        <li key={item} onClick={() => onItemClick(item)}>
          {item}
        </li>
      ))}
    </ul>
  );
});

// Parent component
function Parent() {
  const [data, setData] = useState([1, 2, 3, 4, 5]);
  const [count, setCount] = useState(0);

  const handleItemClick = useCallback((id: number) => {
    console.log('Item clicked:', id);
  }, []);

  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>
        Count: {count}
      </button>
      <ExpensiveComponent data={data} onItemClick={handleItemClick} />
    </div>
  );
}
```

### Code Splitting

```typescript
import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';

// Lazy load components
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));
const Profile = lazy(() => import('./pages/Profile'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </Suspense>
  );
}
```

### Virtual Lists

```typescript
import { useVirtualizer } from '@tanstack/react-virtual';
import { useRef } from 'react';

interface VirtualListProps {
  items: string[];
}

export function VirtualList({ items }: VirtualListProps) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5,
  });

  return (
    <div
      ref={parentRef}
      style={{ height: '400px', overflow: 'auto' }}
    >
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualRow) => (
          <div
            key={virtualRow.index}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualRow.size}px`,
              transform: `translateY(${virtualRow.start}px)`,
            }}
          >
            {items[virtualRow.index]}
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Data Fetching

### React Query

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface User {
  id: string;
  name: string;
  email: string;
}

// Query hook
function useUser(userId: string) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: async () => {
      const response = await fetch(`/api/users/${userId}`);
      if (!response.ok) throw new Error('Failed to fetch user');
      return response.json() as Promise<User>;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 3,
  });
}

// Mutation hook
function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { id: string; updates: Partial<User> }) => {
      const response = await fetch(`/api/users/${data.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data.updates),
      });

      if (!response.ok) throw new Error('Failed to update user');
      return response.json();
    },
    onSuccess: (data) => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['user', data.id] });
    },
  });
}

// Component
function UserProfile({ userId }: { userId: string }) {
  const { data, isLoading, error } = useUser(userId);
  const updateUser = useUpdateUser();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!data) return null;

  const handleUpdate = () => {
    updateUser.mutate({
      id: userId,
      updates: { name: 'New Name' },
    });
  };

  return (
    <div>
      <h1>{data.name}</h1>
      <button onClick={handleUpdate} disabled={updateUser.isPending}>
        {updateUser.isPending ? 'Updating...' : 'Update Name'}
      </button>
    </div>
  );
}
```

### SWR

```typescript
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

function useUser(userId: string) {
  const { data, error, isLoading, mutate } = useSWR(
    `/api/users/${userId}`,
    fetcher,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      refreshInterval: 0,
    }
  );

  return {
    user: data,
    isLoading,
    error,
    mutate,
  };
}
```

## Form Handling

### React Hook Form

```typescript
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  name: z.string().min(2, 'Name must be at least 2 characters'),
  role: z.enum(['user', 'admin', 'editor']),
  acceptTerms: z.boolean().refine((val) => val === true, {
    message: 'You must accept the terms',
  }),
});

type FormData = z.infer<typeof schema>;

export function RegistrationForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    control,
    reset,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      email: '',
      password: '',
      name: '',
      role: 'user',
      acceptTerms: false,
    },
  });

  const onSubmit = async (data: FormData) => {
    try {
      await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      reset();
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label htmlFor="name">Name</label>
        <input id="name" {...register('name')} />
        {errors.name && <span>{errors.name.message}</span>}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" {...register('email')} />
        {errors.email && <span>{errors.email.message}</span>}
      </div>

      <div>
        <label htmlFor="password">Password</label>
        <input id="password" type="password" {...register('password')} />
        {errors.password && <span>{errors.password.message}</span>}
      </div>

      <div>
        <label htmlFor="role">Role</label>
        <select id="role" {...register('role')}>
          <option value="user">User</option>
          <option value="admin">Admin</option>
          <option value="editor">Editor</option>
        </select>
        {errors.role && <span>{errors.role.message}</span>}
      </div>

      <div>
        <label>
          <input type="checkbox" {...register('acceptTerms')} />
          Accept Terms
        </label>
        {errors.acceptTerms && <span>{errors.acceptTerms.message}</span>}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Register'}
      </button>
    </form>
  );
}
```

## Error Handling

### Error Boundaries

```typescript
import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div>
          <h1>Something went wrong</h1>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false, error: null })}>
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
    <ErrorBoundary
      fallback={<div>Custom error UI</div>}
      onError={(error) => {
        // Log to error tracking service
        console.error(error);
      }}
    >
      <MyComponent />
    </ErrorBoundary>
  );
}
```

## TypeScript Integration

### Typed Props

```typescript
import { ReactNode, CSSProperties } from 'react';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  children: ReactNode;
  onClick?: () => void;
  className?: string;
  style?: CSSProperties;
}

export function Button({
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  children,
  onClick,
  className = '',
  style,
}: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant} btn-${size} ${className}`}
      disabled={disabled || loading}
      onClick={onClick}
      style={style}
    >
      {loading ? 'Loading...' : children}
    </button>
  );
}
```

### Generic Components

```typescript
interface ListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => ReactNode;
  keyExtractor: (item: T) => string | number;
  emptyMessage?: string;
}

export function List<T>({
  items,
  renderItem,
  keyExtractor,
  emptyMessage = 'No items',
}: ListProps<T>) {
  if (items.length === 0) {
    return <div>{emptyMessage}</div>;
  }

  return (
    <ul>
      {items.map((item, index) => (
        <li key={keyExtractor(item)}>
          {renderItem(item, index)}
        </li>
      ))}
    </ul>
  );
}

// Usage
interface User {
  id: string;
  name: string;
}

function UserList({ users }: { users: User[] }) {
  return (
    <List
      items={users}
      renderItem={(user) => <div>{user.name}</div>}
      keyExtractor={(user) => user.id}
      emptyMessage="No users found"
    />
  );
}
```

## Best Practices

1. **Component Organization**: Keep components small and focused
2. **Custom Hooks**: Extract reusable logic into custom hooks
3. **Memoization**: Use memo, useMemo, and useCallback wisely
4. **Type Safety**: Leverage TypeScript for better DX
5. **Error Handling**: Implement error boundaries
6. **Code Splitting**: Lazy load routes and heavy components
7. **Accessibility**: Use semantic HTML and ARIA attributes
8. **Testing**: Write tests for critical paths

## Conclusion

Modern React development emphasizes:
- Composability through patterns
- Performance through optimization
- Type safety through TypeScript
- Developer experience through tooling

Master these patterns to build robust, maintainable applications.

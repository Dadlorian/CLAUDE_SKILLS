import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from 'react-query'
import App from '../src/App'

// Mock axios
vi.mock('axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

let queryClient

beforeEach(() => {
  queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })
})

function renderWithProviders(component) {
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  )
}

describe('App Component', () => {
  it('renders the header with title', () => {
    renderWithProviders(<App />)
    expect(screen.getByText('API Integration Tutorial')).toBeInTheDocument()
  })

  it('displays Add New User button', () => {
    renderWithProviders(<App />)
    expect(screen.getByText('Add New User')).toBeInTheDocument()
  })

  it('shows form when Add New User button is clicked', async () => {
    renderWithProviders(<App />)
    const button = screen.getByText('Add New User')
    fireEvent.click(button)
    await waitFor(() => {
      expect(screen.getByText('Create New User')).toBeInTheDocument()
    })
  })

  it('renders footer', () => {
    renderWithProviders(<App />)
    expect(screen.getByText(/© 2024 API Integration Tutorial/)).toBeInTheDocument()
  })
})

describe('API Integration', () => {
  it('handles API errors gracefully', async () => {
    renderWithProviders(<App />)
    // Test error handling...
    await waitFor(() => {
      // Add assertions here
    })
  })

  it('retries failed requests', async () => {
    renderWithProviders(<App />)
    // Test retry logic...
    await waitFor(() => {
      // Add assertions here
    })
  })
})

import React, { useState } from 'react'

export default function ErrorHandling() {
  const [error, setError] = useState(null)
  const [retries, setRetries] = useState(0)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const simulateRequest = async (shouldFail = false) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (shouldFail) {
          reject(new Error('Server error: 500 Internal Server Error'))
        } else {
          resolve({ status: 'success', message: 'Request completed successfully' })
        }
      }, 1000)
    })
  }

  const handleRequestWithRetry = async (maxRetries = 3) => {
    setError(null)
    setResult(null)
    setRetries(0)
    setLoading(true)

    let lastError
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        setRetries(attempt)
        const data = await simulateRequest(attempt < maxRetries)
        setResult(data)
        setLoading(false)
        return
      } catch (err) {
        lastError = err
        if (attempt < maxRetries) {
          await new Promise((resolve) => setTimeout(resolve, 1000 * attempt))
        }
      }
    }

    setError(`Failed after ${maxRetries} retries: ${lastError.message}`)
    setLoading(false)
  }

  const handleSimpleError = async () => {
    setError(null)
    setResult(null)
    setLoading(true)

    try {
      const data = await simulateRequest(true)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleTimeoutError = async () => {
    setError(null)
    setResult(null)
    setLoading(true)

    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 2000)

      // Simulate a request that takes longer than timeout
      await new Promise((resolve, reject) => {
        setTimeout(() => {
          clearTimeout(timeoutId)
          reject(new Error('Request timeout: took longer than 2 seconds'))
        }, 5000)
      })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="section">
        <h2>Error Handling Strategies</h2>
        <p>
          Master robust error handling techniques for production-ready API integration.
        </p>

        <h3>Interactive Examples</h3>

        <div style={{ marginBottom: '2rem' }}>
          <h4>1. Simple Error Handling</h4>
          <p>Basic try-catch pattern for handling errors</p>
          <button className="btn-primary" onClick={handleSimpleError} disabled={loading}>
            {loading ? 'Loading...' : 'Trigger Error'}
          </button>
        </div>

        <div style={{ marginBottom: '2rem' }}>
          <h4>2. Retry with Exponential Backoff</h4>
          <p>Automatically retry failed requests with increasing delays</p>
          <button className="btn-primary" onClick={() => handleRequestWithRetry(3)} disabled={loading}>
            {loading ? `Attempt ${retries}/3...` : 'Fetch with Retry'}
          </button>
        </div>

        <div style={{ marginBottom: '2rem' }}>
          <h4>3. Timeout Handling</h4>
          <p>Cancel requests that take too long</p>
          <button className="btn-primary" onClick={handleTimeoutError} disabled={loading}>
            {loading ? 'Loading...' : 'Test Timeout'}
          </button>
        </div>

        {loading && <div className="loading">Processing request...</div>}

        {error && <div className="error-message">{error}</div>}

        {result && (
          <div className="success-message">
            <p><strong>Success!</strong> {result.message}</p>
          </div>
        )}
      </div>

      <div className="section">
        <h2>Error Handling Patterns</h2>

        <h3>1. Try-Catch Pattern</h3>
        <pre>
          <code>{`try {
  const response = await fetch('/api/data')
  if (!response.ok) {
    throw new Error(\`HTTP error! status: \${response.status}\`)
  }
  const data = await response.json()
  setData(data)
} catch (error) {
  setError(error.message)
  console.error('Fetch failed:', error)
}`}</code>
        </pre>

        <h3>2. Retry with Exponential Backoff</h3>
        <pre>
          <code>{`async function fetchWithRetry(url, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url)
      if (!response.ok) throw new Error(\`HTTP \${response.status}\`)
      return await response.json()
    } catch (error) {
      if (attempt === maxRetries) throw error
      // Wait before retrying (exponential backoff)
      await new Promise(r =>
        setTimeout(r, 1000 * Math.pow(2, attempt - 1))
      )
    }
  }
}`}</code>
        </pre>

        <h3>3. Timeout Handling</h3>
        <pre>
          <code>{`async function fetchWithTimeout(url, timeout = 5000) {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)

  try {
    const response = await fetch(url, { signal: controller.signal })
    return await response.json()
  } finally {
    clearTimeout(timeoutId)
  }
}`}</code>
        </pre>

        <h3>4. Error Classification</h3>
        <pre>
          <code>{`function classifyError(error) {
  if (error.name === 'AbortError') {
    return 'timeout'
  } else if (!navigator.onLine) {
    return 'offline'
  } else if (error.status >= 500) {
    return 'server_error'
  } else if (error.status >= 400) {
    return 'client_error'
  } else {
    return 'unknown'
  }
}`}</code>
        </pre>
      </div>

      <div className="section">
        <h2>Error Recovery Strategies</h2>

        <h3>User-Friendly Messages</h3>
        <pre>
          <code>{`const errorMessages = {
  timeout: 'Request took too long. Please try again.',
  offline: 'You are offline. Check your connection.',
  'server_error': 'Server is having trouble. Please try again later.',
  'client_error': 'Invalid request. Please check your input.',
  unknown: 'Something went wrong. Please try again.'
}

const message = errorMessages[errorType]`}</code>
        </pre>

        <h3>Fallback Data</h3>
        <pre>
          <code>{`const [data, setData] = useState(null)
const [cachedData, setCachedData] = useState(null)

try {
  const freshData = await fetch('/api/data')
  setData(freshData)
  setCachedData(freshData)
} catch (error) {
  // Use cached data as fallback
  if (cachedData) {
    setData(cachedData)
  } else {
    setError('Failed to load data')
  }
}`}</code>
        </pre>

        <h3>Circuit Breaker Pattern</h3>
        <pre>
          <code>{`class CircuitBreaker {
  constructor(threshold = 5, timeout = 60000) {
    this.failures = 0
    this.threshold = threshold
    this.timeout = timeout
    this.state = 'CLOSED' // CLOSED, OPEN, HALF_OPEN
  }

  async execute(request) {
    if (this.state === 'OPEN') {
      throw new Error('Circuit breaker is OPEN')
    }

    try {
      const result = await request()
      this.onSuccess()
      return result
    } catch (error) {
      this.onFailure()
      throw error
    }
  }
}`}</code>
        </pre>
      </div>

      <div className="section">
        <h2>Best Practices</h2>
        <ul>
          <li>Always provide user-friendly error messages</li>
          <li>Log errors for debugging and monitoring</li>
          <li>Implement retry logic for transient failures</li>
          <li>Use timeouts to prevent hanging requests</li>
          <li>Distinguish between different error types</li>
          <li>Cache data for offline fallback</li>
          <li>Implement circuit breaker for cascading failures</li>
          <li>Test error scenarios thoroughly</li>
        </ul>
      </div>
    </div>
  )
}

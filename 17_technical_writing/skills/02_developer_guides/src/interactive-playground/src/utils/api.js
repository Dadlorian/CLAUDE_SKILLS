/**
 * Utility functions for API integration
 */

/**
 * Fetch with timeout
 * @param {string} url - API endpoint
 * @param {number} timeout - Timeout in milliseconds
 * @param {object} options - Fetch options
 * @returns {Promise} Response data
 */
export async function fetchWithTimeout(url, timeout = 5000, options = {}) {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    return await response.json()
  } finally {
    clearTimeout(timeoutId)
  }
}

/**
 * Fetch with retry and exponential backoff
 * @param {string} url - API endpoint
 * @param {number} maxRetries - Maximum number of retries
 * @param {object} options - Fetch options
 * @returns {Promise} Response data
 */
export async function fetchWithRetry(url, maxRetries = 3, options = {}) {
  let lastError

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, options)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      lastError = error

      if (attempt < maxRetries) {
        // Exponential backoff
        const delayMs = 1000 * Math.pow(2, attempt - 1)
        await new Promise((resolve) => setTimeout(resolve, delayMs))
      }
    }
  }

  throw lastError
}

/**
 * Cache for storing API responses
 */
export class APICache {
  constructor(ttl = 60000) {
    this.cache = new Map()
    this.ttl = ttl
  }

  set(key, value) {
    this.cache.set(key, {
      value,
      timestamp: Date.now(),
    })
  }

  get(key) {
    const item = this.cache.get(key)

    if (!item) return null

    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key)
      return null
    }

    return item.value
  }

  clear() {
    this.cache.clear()
  }

  has(key) {
    return this.get(key) !== null
  }
}

/**
 * Circuit breaker for preventing cascading failures
 */
export class CircuitBreaker {
  constructor(threshold = 5, resetTimeout = 60000) {
    this.failureCount = 0
    this.threshold = threshold
    this.resetTimeout = resetTimeout
    this.state = 'CLOSED' // CLOSED, OPEN, HALF_OPEN
    this.lastFailureTime = null
  }

  async execute(fn) {
    // Check if circuit should be reset
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime > this.resetTimeout) {
        this.state = 'HALF_OPEN'
        this.failureCount = 0
      } else {
        throw new Error('Circuit breaker is OPEN')
      }
    }

    try {
      const result = await fn()

      if (this.state === 'HALF_OPEN') {
        this.state = 'CLOSED'
        this.failureCount = 0
      }

      return result
    } catch (error) {
      this.failureCount++
      this.lastFailureTime = Date.now()

      if (this.failureCount >= this.threshold) {
        this.state = 'OPEN'
      }

      throw error
    }
  }

  reset() {
    this.state = 'CLOSED'
    this.failureCount = 0
    this.lastFailureTime = null
  }
}

/**
 * Debounce function for rate limiting
 */
export function debounce(fn, delay = 300) {
  let timeoutId

  return function (...args) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

/**
 * Throttle function for rate limiting
 */
export function throttle(fn, limit = 300) {
  let inThrottle

  return function (...args) {
    if (!inThrottle) {
      fn(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

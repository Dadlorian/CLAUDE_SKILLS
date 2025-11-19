import React, { useState, useCallback } from 'react'

export default function AdvancedExample() {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [cache, setCache] = useState({})
  const [selectedId, setSelectedId] = useState(1)

  const fetchPosts = useCallback(async (id) => {
    // Check cache first
    if (cache[id]) {
      setPosts([cache[id]])
      return
    }

    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`https://jsonplaceholder.typicode.com/posts/${id}`)
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const data = await response.json()

      // Cache the result
      setCache((prev) => ({ ...prev, [id]: data }))
      setPosts([data])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [cache])

  const handleFetch = async (id) => {
    setSelectedId(id)
    await fetchPosts(id)
  }

  const clearCache = () => {
    setCache({})
    setPosts([])
  }

  return (
    <div>
      <div className="section">
        <h2>Advanced State Management</h2>
        <p>
          This example demonstrates advanced patterns including caching, optimistic updates, and smart state management.
        </p>

        <h3>Features</h3>
        <ul>
          <li>Response caching to avoid redundant requests</li>
          <li>Multiple concurrent requests handling</li>
          <li>State synchronization</li>
          <li>Cache management</li>
        </ul>

        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="post-select">Select a Post: </label>
          <select
            id="post-select"
            value={selectedId}
            onChange={(e) => handleFetch(parseInt(e.target.value))}
            style={{ marginLeft: '0.5rem' }}
          >
            {[1, 2, 3, 4, 5].map((id) => (
              <option key={id} value={id}>
                Post {id} {cache[id] ? '(cached)' : ''}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <button className="btn-primary" onClick={() => handleFetch(selectedId)} disabled={loading}>
            {loading ? 'Loading...' : 'Fetch Post'}
          </button>
          <button className="btn-secondary" onClick={clearCache} style={{ marginLeft: '0.5rem' }}>
            Clear Cache
          </button>
        </div>

        <div>
          <strong>Cache Status:</strong>
          <p>{Object.keys(cache).length} items cached</p>
          {Object.keys(cache).length > 0 && (
            <p>Cached posts: {Object.keys(cache).join(', ')}</p>
          )}
        </div>

        {loading && <div className="loading">Loading post {selectedId}...</div>}

        {error && <div className="error-message">Error: {error}</div>}

        {posts.length > 0 && (
          <div className="success-message">
            <h4>Post #{posts[0].id}</h4>
            <h5>{posts[0].title}</h5>
            <p>{posts[0].body}</p>
          </div>
        )}
      </div>

      <div className="section">
        <h2>Caching Strategy</h2>

        <h3>The Pattern</h3>
        <pre>
          <code>{`const [cache, setCache] = useState({})

const fetchData = useCallback(async (id) => {
  // 1. Check cache first
  if (cache[id]) {
    setData(cache[id])
    return
  }

  setLoading(true)
  try {
    const response = await fetch(\`/api/posts/\${id}\`)
    const data = await response.json()

    // 2. Store in cache
    setCache(prev => ({ ...prev, [id]: data }))
    setData(data)
  } finally {
    setLoading(false)
  }
}, [cache])`}</code>
        </pre>

        <h3>Benefits</h3>
        <ul>
          <li>Reduces server load</li>
          <li>Improves user experience with instant responses</li>
          <li>Saves bandwidth</li>
          <li>Enables offline functionality</li>
        </ul>
      </div>

      <div className="section">
        <h2>Advanced Patterns</h2>

        <h3>Optimistic Updates</h3>
        <pre>
          <code>{`// Update UI immediately
setPosts([...posts, newPost])

// Then sync with server
try {
  await fetch('/api/posts', { method: 'POST', body: newPost })
} catch (err) {
  // Rollback on error
  setPosts(posts)
}`}</code>
        </pre>

        <h3>Request Deduplication</h3>
        <pre>
          <code>{`const [pendingRequests, setPendingRequests] = useState({})

const fetchData = async (id) => {
  // Prevent duplicate requests
  if (pendingRequests[id]) return

  setPendingRequests(prev => ({ ...prev, [id]: true }))
  try {
    // ... fetch data
  } finally {
    setPendingRequests(prev => {
      const next = { ...prev }
      delete next[id]
      return next
    })
  }
}`}</code>
        </pre>

        <h3>Stale-While-Revalidate</h3>
        <pre>
          <code>{`// Serve stale data immediately
if (cache[id]) setData(cache[id])

// Revalidate in background
fetchFresh(id).then(newData => {
  if (newData !== cache[id]) {
    setData(newData)
    updateCache(id, newData)
  }
})`}</code>
        </pre>
      </div>
    </div>
  )
}

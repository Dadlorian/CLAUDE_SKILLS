import React, { useState } from 'react'

export default function BasicExample() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('https://jsonplaceholder.typicode.com/posts/1')
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const json = await response.json()
      setData(json)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="section">
        <h2>Basic Fetch Example</h2>
        <p>
          This example demonstrates the fundamental pattern for fetching data from an API using the native Fetch API.
        </p>

        <h3>How It Works</h3>
        <ol>
          <li>Click the button to start the fetch request</li>
          <li>The loading state shows while data is being fetched</li>
          <li>The response is parsed as JSON</li>
          <li>The data is displayed on success</li>
          <li>Errors are caught and displayed</li>
        </ol>

        <button className="btn-primary" onClick={fetchData} disabled={loading}>
          {loading ? 'Fetching...' : 'Fetch Post'}
        </button>

        {loading && <div className="loading">Loading data...</div>}

        {error && <div className="error-message">Error: {error}</div>}

        {data && (
          <div className="success-message">
            <h4>Post #{data.id}</h4>
            <h5>{data.title}</h5>
            <p>{data.body}</p>
          </div>
        )}
      </div>

      <div className="section">
        <h2>Code Walkthrough</h2>

        <h3>The Fetch Pattern</h3>
        <pre>
          <code>{`async function fetchData() {
  setLoading(true)
  setError(null)
  try {
    // 1. Make the request
    const response = await fetch('/api/endpoint')

    // 2. Check if request was successful
    if (!response.ok) {
      throw new Error(\`HTTP \${response.status}\`)
    }

    // 3. Parse the response as JSON
    const data = await response.json()

    // 4. Update state with data
    setData(data)
  } catch (err) {
    // 5. Handle any errors
    setError(err.message)
  } finally {
    // 6. Always clear loading state
    setLoading(false)
  }
}`}</code>
        </pre>

        <h3>Key Points</h3>
        <ul>
          <li><strong>async/await</strong> - Makes asynchronous code look synchronous</li>
          <li><strong>response.ok</strong> - Checks if HTTP status is 2xx</li>
          <li><strong>response.json()</strong> - Parses response body as JSON</li>
          <li><strong>try/catch/finally</strong> - Handles all outcomes of the request</li>
        </ul>
      </div>

      <div className="section">
        <h2>Common Patterns</h2>

        <h3>Adding Query Parameters</h3>
        <pre>
          <code>{`const url = new URL('/api/posts', baseURL)
url.searchParams.append('limit', 10)
const response = await fetch(url)`}</code>
        </pre>

        <h3>POST Request with Data</h3>
        <pre>
          <code>{`const response = await fetch('/api/posts', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ title: 'New Post' })
})`}</code>
        </pre>

        <h3>Adding Headers</h3>
        <pre>
          <code>{`const response = await fetch('/api/posts', {
  headers: {
    'Authorization': 'Bearer TOKEN',
    'Content-Type': 'application/json'
  }
})`}</code>
        </pre>
      </div>
    </div>
  )
}

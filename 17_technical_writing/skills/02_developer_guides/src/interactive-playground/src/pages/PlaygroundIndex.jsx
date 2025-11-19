import React from 'react'

export default function PlaygroundIndex() {
  return (
    <div>
      <div className="section">
        <h2>Welcome to the Interactive Playground</h2>
        <p>
          This playground provides hands-on examples for learning API integration with modern JavaScript frameworks. Each example is fully executable and modifiable.
        </p>
      </div>

      <div className="grid">
        <div className="card">
          <h3>Basic Fetch</h3>
          <p>
            Learn the fundamentals of making HTTP requests using the native Fetch API.
          </p>
          <ul>
            <li>GET requests</li>
            <li>Error handling</li>
            <li>Response parsing</li>
          </ul>
        </div>

        <div className="card">
          <h3>Advanced State</h3>
          <p>
            Master complex state management patterns for API data.
          </p>
          <ul>
            <li>Loading states</li>
            <li>Caching strategies</li>
            <li>Optimistic updates</li>
          </ul>
        </div>

        <div className="card">
          <h3>Form Integration</h3>
          <p>
            Learn how to integrate forms with APIs for create and update operations.
          </p>
          <ul>
            <li>Form validation</li>
            <li>POST/PUT requests</li>
            <li>Submission handling</li>
          </ul>
        </div>

        <div className="card">
          <h3>Error Handling</h3>
          <p>
            Master error handling strategies for robust API integration.
          </p>
          <ul>
            <li>Error boundaries</li>
            <li>Retry logic</li>
            <li>User feedback</li>
          </ul>
        </div>
      </div>

      <div className="section">
        <h2>Key Concepts</h2>

        <h3>1. HTTP Methods</h3>
        <div className="example-box">
          <p><strong>GET</strong> - Retrieve data from the server</p>
          <p><strong>POST</strong> - Submit data to the server</p>
          <p><strong>PUT</strong> - Update existing data</p>
          <p><strong>DELETE</strong> - Remove data</p>
        </div>

        <h3>2. API Response Handling</h3>
        <pre>
          <code>{`// Basic fetch pattern
const response = await fetch('/api/endpoint')
const data = await response.json()
if (!response.ok) {
  throw new Error(data.message)
}
return data`}</code>
        </pre>

        <h3>3. State Management</h3>
        <div className="example-box">
          <p><strong>Loading</strong> - Show loading indicator while fetching</p>
          <p><strong>Error</strong> - Display error messages on failure</p>
          <p><strong>Data</strong> - Store and display fetched data</p>
        </div>

        <h3>4. Best Practices</h3>
        <ul>
          <li>Always handle errors gracefully</li>
          <li>Provide loading states</li>
          <li>Validate data before using it</li>
          <li>Cache responses appropriately</li>
          <li>Use correct HTTP methods</li>
          <li>Set proper headers</li>
          <li>Handle network timeouts</li>
          <li>Log for debugging</li>
        </ul>
      </div>

      <div className="section">
        <h2>Getting Started</h2>
        <p>
          Click on any of the navigation buttons above to explore different API integration patterns. Each example includes:
        </p>
        <ul>
          <li>Runnable code you can execute immediately</li>
          <li>Explanations of key concepts</li>
          <li>Common patterns and best practices</li>
          <li>Tips for debugging</li>
        </ul>
        <p>
          Try modifying the code to see how it affects the output. Learning by experimenting is the best way to master API integration!
        </p>
      </div>
    </div>
  )
}

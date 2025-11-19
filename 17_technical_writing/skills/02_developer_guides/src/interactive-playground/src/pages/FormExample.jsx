import React, { useState } from 'react'

export default function FormExample() {
  const [formData, setFormData] = useState({
    title: '',
    body: '',
    userId: '1',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [submittedData, setSubmittedData] = useState(null)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const validateForm = () => {
    if (!formData.title.trim()) {
      setError('Title is required')
      return false
    }
    if (!formData.body.trim()) {
      setError('Body is required')
      return false
    }
    return true
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)

    if (!validateForm()) return

    setLoading(true)
    try {
      // Simulating an API call
      const response = await fetch('https://jsonplaceholder.typicode.com/posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          userId: parseInt(formData.userId),
        }),
      })

      if (!response.ok) throw new Error(`HTTP ${response.status}`)

      const data = await response.json()
      setSubmittedData(data)
      setSuccess(`Post created successfully! ID: ${data.id}`)
      setFormData({ title: '', body: '', userId: '1' })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="section">
        <h2>Form Integration with API</h2>
        <p>
          Learn how to integrate HTML forms with API endpoints. This example demonstrates form submission, validation, and error handling.
        </p>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="title">
              Post Title *
              <input
                id="title"
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="Enter post title"
                disabled={loading}
              />
            </label>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="body">
              Post Body *
              <textarea
                id="body"
                name="body"
                value={formData.body}
                onChange={handleChange}
                placeholder="Enter post content"
                rows="4"
                disabled={loading}
              />
            </label>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="userId">
              User ID
              <select
                id="userId"
                name="userId"
                value={formData.userId}
                onChange={handleChange}
                disabled={loading}
              >
                {[1, 2, 3, 4, 5].map((id) => (
                  <option key={id} value={id}>
                    User {id}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Submitting...' : 'Submit Post'}
          </button>
        </form>

        {error && <div className="error-message">{error}</div>}

        {success && (
          <div className="success-message">
            <p>{success}</p>
          </div>
        )}

        {submittedData && (
          <div className="success-message">
            <h4>Response from Server:</h4>
            <p>
              <strong>ID:</strong> {submittedData.id}
            </p>
            <p>
              <strong>Title:</strong> {submittedData.title}
            </p>
            <p>
              <strong>User ID:</strong> {submittedData.userId}
            </p>
          </div>
        )}
      </div>

      <div className="section">
        <h2>Form Handling Pattern</h2>

        <h3>State Management</h3>
        <pre>
          <code>{`const [formData, setFormData] = useState({
  title: '',
  body: '',
  userId: '1'
})

const handleChange = (e) => {
  const { name, value } = e.target
  setFormData(prev => ({
    ...prev,
    [name]: value
  }))
}`}</code>
        </pre>

        <h3>Form Validation</h3>
        <pre>
          <code>{`const validateForm = () => {
  if (!formData.title.trim()) {
    setError('Title is required')
    return false
  }
  if (!formData.body.trim()) {
    setError('Body is required')
    return false
  }
  return true
}`}</code>
        </pre>

        <h3>API Submission</h3>
        <pre>
          <code>{`const handleSubmit = async (e) => {
  e.preventDefault()

  if (!validateForm()) return

  setLoading(true)
  try {
    const response = await fetch('/api/posts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    })

    const data = await response.json()
    setSuccess('Post created!')
  } catch (err) {
    setError(err.message)
  } finally {
    setLoading(false)
  }
}`}</code>
        </pre>
      </div>

      <div className="section">
        <h2>Best Practices</h2>

        <h3>1. Validate Before Submitting</h3>
        <pre>
          <code>{`// Check required fields
// Validate email format
// Check length constraints
// Verify file types and sizes`}</code>
        </pre>

        <h3>2. Provide Feedback</h3>
        <pre>
          <code>{`// Show loading state
// Display success message
// Show error with details
// Clear form on success`}</code>
        </pre>

        <h3>3. Handle Edge Cases</h3>
        <pre>
          <code>{`// Network errors
// Timeout handling
// Invalid responses
// User cancellation`}</code>
        </pre>

        <h3>4. Security Considerations</h3>
        <ul>
          <li>Always validate on the server</li>
          <li>Use HTTPS for form submission</li>
          <li>Implement CSRF protection</li>
          <li>Sanitize user input</li>
          <li>Never expose sensitive data in response</li>
        </ul>
      </div>
    </div>
  )
}

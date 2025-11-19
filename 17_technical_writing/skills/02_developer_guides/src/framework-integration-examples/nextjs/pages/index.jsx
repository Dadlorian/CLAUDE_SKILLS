import { useState } from 'react'
import useSWR from 'swr'
import axios from 'axios'
import Head from 'next/head'

const fetcher = (url) => axios.get(url).then((res) => res.data)

export default function Home() {
  const { data: users = [], error, isLoading, mutate } = useSWR(
    '/api/users',
    fetcher,
    {
      revalidateOnFocus: false,
    }
  )

  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({ name: '', email: '', role: 'user' })

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await axios.post('/api/users', formData)
      mutate()
      setFormData({ name: '', email: '', role: 'user' })
      setShowForm(false)
    } catch (err) {
      alert('Error creating user: ' + err.message)
    }
  }

  const handleDelete = async (id) => {
    if (confirm('Delete this user?')) {
      try {
        await axios.delete(`/api/users/${id}`)
        mutate()
      } catch (err) {
        alert('Error deleting user: ' + err.message)
      }
    }
  }

  return (
    <>
      <Head>
        <title>Next.js API Integration</title>
        <meta name="description" content="Next.js API integration example" />
      </Head>

      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
        <h1>Next.js API Integration Example</h1>

        <button onClick={() => setShowForm(!showForm)} style={{ marginBottom: '1rem' }}>
          {showForm ? 'Cancel' : 'Add User'}
        </button>

        {showForm && (
          <form onSubmit={handleSubmit} style={{ marginBottom: '2rem' }}>
            <div style={{ marginBottom: '1rem' }}>
              <input
                type="text"
                placeholder="Name"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                required
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <input
                type="email"
                placeholder="Email"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                required
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <select
                value={formData.role}
                onChange={(e) =>
                  setFormData({ ...formData, role: e.target.value })
                }
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
                <option value="moderator">Moderator</option>
              </select>
            </div>
            <button type="submit">Create User</button>
          </form>
        )}

        {isLoading && <p>Loading users...</p>}
        {error && <p>Error loading users: {error.message}</p>}

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '1rem',
          }}
        >
          {users.map((user) => (
            <div
              key={user.id}
              style={{
                border: '1px solid #ccc',
                padding: '1rem',
                borderRadius: '8px',
              }}
            >
              <h3>{user.name}</h3>
              <p>Email: {user.email}</p>
              <p>Role: {user.role}</p>
              <button
                onClick={() => handleDelete(user.id)}
                style={{ color: 'red' }}
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      </main>
    </>
  )
}

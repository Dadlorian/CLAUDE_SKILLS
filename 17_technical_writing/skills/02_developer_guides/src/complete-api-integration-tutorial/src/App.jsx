import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import axios from 'axios'
import UserList from './components/UserList'
import UserForm from './components/UserForm'
import ErrorBoundary from './components/ErrorBoundary'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api'

// Fetch users function
const fetchUsers = async () => {
  const { data } = await axios.get(`${API_BASE_URL}/users`)
  return data
}

// Create user function
const createUser = async (userData) => {
  const { data } = await axios.post(`${API_BASE_URL}/users`, userData)
  return data
}

// Update user function
const updateUser = async ({ id, ...userData }) => {
  const { data } = await axios.put(`${API_BASE_URL}/users/${id}`, userData)
  return data
}

// Delete user function
const deleteUser = async (id) => {
  await axios.delete(`${API_BASE_URL}/users/${id}`)
  return id
}

function App() {
  const [showForm, setShowForm] = useState(false)
  const [editingUser, setEditingUser] = useState(null)
  const queryClient = useQueryClient()

  // Query for fetching users
  const {
    data: users = [],
    isLoading,
    isError,
    error,
  } = useQuery('users', fetchUsers, {
    onError: (err) => {
      console.error('Failed to fetch users:', err)
    },
  })

  // Mutation for creating users
  const createMutation = useMutation(createUser, {
    onSuccess: (newUser) => {
      queryClient.setQueryData('users', (old) => [...old, newUser])
      setShowForm(false)
      alert('User created successfully!')
    },
    onError: (err) => {
      console.error('Failed to create user:', err)
      alert('Failed to create user')
    },
  })

  // Mutation for updating users
  const updateMutation = useMutation(updateUser, {
    onSuccess: (updatedUser) => {
      queryClient.setQueryData('users', (old) =>
        old.map((user) => (user.id === updatedUser.id ? updatedUser : user))
      )
      setEditingUser(null)
      setShowForm(false)
      alert('User updated successfully!')
    },
    onError: (err) => {
      console.error('Failed to update user:', err)
      alert('Failed to update user')
    },
  })

  // Mutation for deleting users
  const deleteMutation = useMutation(deleteUser, {
    onSuccess: (deletedId) => {
      queryClient.setQueryData('users', (old) =>
        old.filter((user) => user.id !== deletedId)
      )
      alert('User deleted successfully!')
    },
    onError: (err) => {
      console.error('Failed to delete user:', err)
      alert('Failed to delete user')
    },
  })

  const handleFormSubmit = (formData) => {
    if (editingUser) {
      updateMutation.mutate({ id: editingUser.id, ...formData })
    } else {
      createMutation.mutate(formData)
    }
  }

  const handleEdit = (user) => {
    setEditingUser(user)
    setShowForm(true)
  }

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      deleteMutation.mutate(id)
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingUser(null)
  }

  return (
    <ErrorBoundary>
      <div className="app">
        <header className="app-header">
          <h1>API Integration Tutorial</h1>
          <p>Production-Ready React + API Example</p>
        </header>

        <main className="app-main">
          <section className="controls">
            <button
              className="btn btn-primary"
              onClick={() => setShowForm(!showForm)}
            >
              {showForm ? 'Cancel' : 'Add New User'}
            </button>
          </section>

          {showForm && (
            <section className="form-section">
              <UserForm
                user={editingUser}
                onSubmit={handleFormSubmit}
                onCancel={handleCancel}
                isLoading={
                  createMutation.isLoading || updateMutation.isLoading
                }
              />
            </section>
          )}

          {isLoading && (
            <div className="loading">
              <p>Loading users...</p>
            </div>
          )}

          {isError && (
            <div className="error">
              <p>Error: {error?.message || 'Failed to load users'}</p>
              <button
                className="btn btn-secondary"
                onClick={() =>
                  queryClient.invalidateQueries('users')
                }
              >
                Retry
              </button>
            </div>
          )}

          {!isLoading && !isError && (
            <UserList
              users={users}
              onEdit={handleEdit}
              onDelete={handleDelete}
              isDeleting={deleteMutation.isLoading}
            />
          )}
        </main>

        <footer className="app-footer">
          <p>© 2024 API Integration Tutorial. Production-Ready Example.</p>
        </footer>
      </div>
    </ErrorBoundary>
  )
}

export default App

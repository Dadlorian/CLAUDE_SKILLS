import React from 'react'
import '../styles/UserList.css'

export default function UserList({ users, onEdit, onDelete, isDeleting }) {
  if (users.length === 0) {
    return (
      <div className="empty-state">
        <p>No users found. Create one to get started!</p>
      </div>
    )
  }

  return (
    <section className="user-list">
      <h2>Users ({users.length})</h2>
      <div className="users-grid">
        {users.map((user) => (
          <div key={user.id} className="user-card">
            <div className="user-header">
              <h3>{user.name}</h3>
              <div className="user-actions">
                <button
                  className="btn btn-small btn-secondary"
                  onClick={() => onEdit(user)}
                >
                  Edit
                </button>
                <button
                  className="btn btn-small btn-danger"
                  onClick={() => onDelete(user.id)}
                  disabled={isDeleting}
                >
                  Delete
                </button>
              </div>
            </div>
            <div className="user-body">
              <p>
                <strong>Email:</strong> {user.email}
              </p>
              <p>
                <strong>Role:</strong> {user.role || 'User'}
              </p>
              <p>
                <strong>Status:</strong>{' '}
                <span className={`badge badge-${user.active ? 'success' : 'danger'}`}>
                  {user.active ? 'Active' : 'Inactive'}
                </span>
              </p>
              <p className="text-muted">
                <small>ID: {user.id}</small>
              </p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

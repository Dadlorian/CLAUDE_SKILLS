<template>
  <div class="app">
    <header class="app-header">
      <h1>Vue 3 API Integration Example</h1>
    </header>

    <main class="app-main">
      <button @click="toggleForm" class="btn-primary">
        {{ showForm ? 'Cancel' : 'Add User' }}
      </button>

      <form v-if="showForm" @submit.prevent="handleSubmit" class="form">
        <div class="form-group">
          <input
            v-model="formData.name"
            type="text"
            placeholder="Name"
            required
          />
        </div>
        <div class="form-group">
          <input
            v-model="formData.email"
            type="email"
            placeholder="Email"
            required
          />
        </div>
        <div class="form-group">
          <select v-model="formData.role">
            <option value="user">User</option>
            <option value="admin">Admin</option>
            <option value="moderator">Moderator</option>
          </select>
        </div>
        <button type="submit" class="btn-primary">Create User</button>
      </form>

      <div v-if="loading" class="loading">Loading users...</div>
      <div v-if="error" class="error">Error: {{ error }}</div>

      <div class="users-grid">
        <div v-for="user in users" :key="user.id" class="user-card">
          <h3>{{ user.name }}</h3>
          <p>Email: {{ user.email }}</p>
          <p>Role: {{ user.role }}</p>
          <button @click="deleteUser(user.id)" class="btn-danger">Delete</button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api'

const users = ref([])
const loading = ref(false)
const error = ref(null)
const showForm = ref(false)
const formData = ref({ name: '', email: '', role: 'user' })

const fetchUsers = async () => {
  loading.value = true
  error.value = null
  try {
    const { data } = await axios.get(`${API_URL}/users`)
    users.value = data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  try {
    await axios.post(`${API_URL}/users`, formData.value)
    formData.value = { name: '', email: '', role: 'user' }
    showForm.value = false
    await fetchUsers()
  } catch (err) {
    error.value = 'Failed to create user: ' + err.message
  }
}

const deleteUser = async (id) => {
  if (confirm('Delete this user?')) {
    try {
      await axios.delete(`${API_URL}/users/${id}`)
      await fetchUsers()
    } catch (err) {
      error.value = 'Failed to delete user: ' + err.message
    }
  }
}

const toggleForm = () => {
  showForm.value = !showForm.value
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.app {
  min-height: 100vh;
  font-family: system-ui, sans-serif;
}

.app-header {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  padding: 2rem;
  text-align: center;
}

.app-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.btn-primary,
.btn-danger {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
  margin-bottom: 1rem;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}

.btn-danger:hover {
  background-color: #dc2626;
}

.form {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 0.375rem;
  font-size: 1rem;
}

.loading,
.error {
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 0.375rem;
  text-align: center;
}

.loading {
  background-color: #e3f2fd;
  color: #1565c0;
}

.error {
  background-color: #ffebee;
  color: #c62828;
}

.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.user-card {
  background: white;
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.user-card h3 {
  margin-top: 0;
}

.user-card p {
  color: #666;
  margin: 0.5rem 0;
}
</style>

import express from 'express'
import cors from 'cors'

const app = express()
const PORT = process.env.PORT || 3001

// Mock data
let users = [
  {
    id: 1,
    name: 'Alice Johnson',
    email: 'alice@example.com',
    role: 'admin',
    active: true,
  },
  {
    id: 2,
    name: 'Bob Smith',
    email: 'bob@example.com',
    role: 'user',
    active: true,
  },
  {
    id: 3,
    name: 'Charlie Brown',
    email: 'charlie@example.com',
    role: 'moderator',
    active: false,
  },
]

// Middleware
app.use(cors())
app.use(express.json())

// Routes
app.get('/api/users', (req, res) => {
  console.log('GET /api/users')
  res.json(users)
})

app.get('/api/users/:id', (req, res) => {
  const user = users.find((u) => u.id === parseInt(req.params.id))
  if (!user) {
    return res.status(404).json({ error: 'User not found' })
  }
  res.json(user)
})

app.post('/api/users', (req, res) => {
  const { name, email, role, active } = req.body

  // Validation
  if (!name || !email) {
    return res.status(400).json({ error: 'Name and email are required' })
  }

  const newUser = {
    id: Math.max(...users.map((u) => u.id), 0) + 1,
    name,
    email,
    role: role || 'user',
    active: active !== false,
  }

  users.push(newUser)
  res.status(201).json(newUser)
})

app.put('/api/users/:id', (req, res) => {
  const user = users.find((u) => u.id === parseInt(req.params.id))
  if (!user) {
    return res.status(404).json({ error: 'User not found' })
  }

  const { name, email, role, active } = req.body
  Object.assign(user, {
    name: name || user.name,
    email: email || user.email,
    role: role || user.role,
    active: active !== undefined ? active : user.active,
  })

  res.json(user)
})

app.delete('/api/users/:id', (req, res) => {
  const index = users.findIndex((u) => u.id === parseInt(req.params.id))
  if (index === -1) {
    return res.status(404).json({ error: 'User not found' })
  }

  const deletedUser = users.splice(index, 1)
  res.json(deletedUser[0])
})

app.listen(PORT, () => {
  console.log(`Mock API server running on http://localhost:${PORT}`)
  console.log('Available endpoints:')
  console.log('  GET    /api/users')
  console.log('  GET    /api/users/:id')
  console.log('  POST   /api/users')
  console.log('  PUT    /api/users/:id')
  console.log('  DELETE /api/users/:id')
})

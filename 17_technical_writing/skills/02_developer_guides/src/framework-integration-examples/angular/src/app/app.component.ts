import { Component, OnInit } from '@angular/core'
import { CommonModule } from '@angular/common'
import { FormsModule } from '@angular/forms'
import { UserService } from './services/user.service'

interface User {
  id: number
  name: string
  email: string
  role: string
  active: boolean
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit {
  users: User[] = []
  loading = false
  error: string | null = null
  showForm = false
  formData = { name: '', email: '', role: 'user' }

  constructor(private userService: UserService) {}

  ngOnInit() {
    this.loadUsers()
  }

  loadUsers() {
    this.loading = true
    this.error = null
    this.userService.getUsers().subscribe({
      next: (data) => {
        this.users = data
        this.loading = false
      },
      error: (err) => {
        this.error = 'Failed to load users: ' + err.message
        this.loading = false
      },
    })
  }

  toggleForm() {
    this.showForm = !this.showForm
    if (!this.showForm) {
      this.formData = { name: '', email: '', role: 'user' }
    }
  }

  handleSubmit() {
    this.userService.createUser(this.formData).subscribe({
      next: () => {
        this.loadUsers()
        this.formData = { name: '', email: '', role: 'user' }
        this.showForm = false
      },
      error: (err) => {
        this.error = 'Failed to create user: ' + err.message
      },
    })
  }

  deleteUser(id: number) {
    if (confirm('Delete this user?')) {
      this.userService.deleteUser(id).subscribe({
        next: () => {
          this.loadUsers()
        },
        error: (err) => {
          this.error = 'Failed to delete user: ' + err.message
        },
      })
    }
  }
}

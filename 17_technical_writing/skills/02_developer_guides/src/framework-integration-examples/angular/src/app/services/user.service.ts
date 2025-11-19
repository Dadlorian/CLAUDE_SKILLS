import { Injectable } from '@angular/core'
import { HttpClient } from '@angular/common/http'
import { Observable } from 'rxjs'

interface User {
  id?: number
  name: string
  email: string
  role: string
  active?: boolean
}

@Injectable({
  providedIn: 'root',
})
export class UserService {
  private API_URL = 'http://localhost:3001/api'

  constructor(private http: HttpClient) {}

  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${this.API_URL}/users`)
  }

  getUser(id: number): Observable<User> {
    return this.http.get<User>(`${this.API_URL}/users/${id}`)
  }

  createUser(user: User): Observable<User> {
    return this.http.post<User>(`${this.API_URL}/users`, user)
  }

  updateUser(id: number, user: User): Observable<User> {
    return this.http.put<User>(`${this.API_URL}/users/${id}`, user)
  }

  deleteUser(id: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/users/${id}`)
  }
}

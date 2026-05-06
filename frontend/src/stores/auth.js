import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')

  const isLoggedIn = () => !!token.value

  async function login(username, password) {
    const res = await api.post('/auth/login', { username, password })
    token.value = res.access_token
    user.value = res.user
    localStorage.setItem('token', res.access_token)
    return res
  }

  async function register(data) {
    const res = await api.post('/auth/register', data)
    token.value = res.access_token
    user.value = res.user
    localStorage.setItem('token', res.access_token)
    return res
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const res = await api.get('/auth/me')
      user.value = res
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { user, token, isLoggedIn, login, register, fetchUser, logout }
})

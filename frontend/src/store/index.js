import { defineStore } from 'pinia'
import { getMe } from '../api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('token') || '',
  }),
  getters: {
    isLoggedIn: (state) => !!state.token && !!state.user,
    currentUser: (state) => state.user,
  },
  actions: {
    setAuth(token, user) {
      this.token = token
      this.user = user
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
    },
    async fetchUser() {
      if (!this.token) return
      try {
        const res = await getMe()
        this.user = res.data.user
        localStorage.setItem('user', JSON.stringify(this.user))
      } catch {
        this.logout()
      }
    },
    updateUser(user) {
      this.user = { ...this.user, ...user }
      localStorage.setItem('user', JSON.stringify(this.user))
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
  },
})

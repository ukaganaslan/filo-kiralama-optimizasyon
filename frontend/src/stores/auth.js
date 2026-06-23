import axios from 'axios'
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('token') || null,
        username: localStorage.getItem('username') || null,
        isStaff: localStorage.getItem('isStaff') === 'true',
    }),
    actions: {
        login(token, username, isStaff) {
            this.token = token
            this.username = username
            this.isStaff = isStaff
            localStorage.setItem('token', token)
            localStorage.setItem('username', username)
            localStorage.setItem('isStaff', isStaff)
            axios.defaults.headers.common['Authorization'] = `Token ${token}`
        },
        logout() {
            this.token = null
            this.username = null
            this.isStaff = false
            localStorage.removeItem('token')
            localStorage.removeItem('username')
            localStorage.removeItem('isStaff')
            delete axios.defaults.headers.common['Authorization']
        },
        setUsername(username) {
            this.username = username
            localStorage.setItem('username', username)
        },
        init() {
            const token = localStorage.getItem('token')
            if (token) {
                axios.defaults.headers.common['Authorization'] = `Token ${token}`
            }
        }
    }
})
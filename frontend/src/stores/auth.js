import axios from 'axios'
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('token') || null,
        username: localStorage.getItem('username') || null,
        role: localStorage.getItem('role') || null,
    }),
    getters: {
        isAdmin: (state) => state.role === 'admin',
        isRepresentative: (state) => state.role === 'representative',
        isCustomer: (state) => state.role === 'customer',
        isStaff: (state) => state.role === 'admin',
    },
    actions: {
        login(token, username, role) {
            this.token = token
            this.username = username
            this.role = role
            localStorage.setItem('token', token)
            localStorage.setItem('username', username)
            localStorage.setItem('role', role)
            axios.defaults.headers.common['Authorization'] = `Token ${token}`
        },
        logout() {
            this.token = null
            this.username = null
            this.role = null
            localStorage.removeItem('token')
            localStorage.removeItem('username')
            localStorage.removeItem('role')
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

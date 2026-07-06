import axios from 'axios'
import { defineStore } from 'pinia'

export const useNotificationStore = defineStore('notifications', {
    state: () => ({
        items: [],
        unreadCount: 0,
        pollingId: null,
    }),
    actions: {
        async fetchList() {
            const res = await axios.get('/api/notifications/')
            this.items = res.data
        },
        async fetchUnreadCount() {
            const res = await axios.get('/api/notifications/unread-count/')
            this.unreadCount = res.data.count
        },
        async markRead(id) {
            await axios.post(`/api/notifications/${id}/mark-read/`)
            const item = this.items.find(n => n.id === id)
            if (item) item.is_read = true
            this.fetchUnreadCount()
        },
        async markAllRead() {
            await axios.post('/api/notifications/mark-all-read/')
            this.items.forEach(n => { n.is_read = true })
            this.unreadCount = 0
        },
        startPolling() {
            this.fetchUnreadCount()
            this.pollingId = setInterval(() => this.fetchUnreadCount(), 30000)
        },
        stopPolling() {
            if (this.pollingId) clearInterval(this.pollingId)
            this.pollingId = null
        },
    },
})
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import VCalendar from 'v-calendar'
import 'v-calendar/style.css'
import router from './router/index.js'
import './style.css'
import axios from 'axios'
axios.defaults.baseURL = import.meta.env.VITE_API_BASE
import App from './App.vue'
import { useAuthStore } from './stores/auth'

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(VCalendar, {})
app.use(PrimeVue, {
    theme: {
        preset: Aura
    }
})

const auth = useAuthStore()
auth.init()

app.mount('#app')
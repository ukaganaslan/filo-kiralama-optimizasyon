import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

const routes = [
    { path: '/', component: LoginView },
    { path: '/register', component: RegisterView },
    { path: '/dashboard', component: () => import('../views/CustomerDashboard.vue'), meta: { requiresAuth: true } },
    { path: '/dashboard/rezervasyonlar', component: () => import('../views/MyReservations.vue'), meta: { requiresAuth: true } },
    { path: '/operator', component: () => import('../views/OperatorDashboard.vue'), meta: { requiresAuth: true, requiresStaff: true } },
    { path: '/operator/araclar', component: () => import('../views/Araclar.vue'), meta: { requiresAuth: true, requiresStaff: true } },
    { path: '/operator/kullanıcılar', component: () => import('../views/Kullanıcılar.vue'), meta: { requiresAuth: true, requiresStaff: true } },
    { path: '/operator/subeler', component: () => import('../views/Subeler.vue'), meta: { requiresAuth: true, requiresStaff: true } },
    { path: '/operator/karsılanamayan-rez', component: () => import('../views/Karşılanamayan Rezervasyonlar.vue'), meta: { requiresAuth: true, requiresStaff: true } },
    { path: '/operator/optimizasyon-sonuc', component: () => import('../views/Optimizasyon Sonucu.vue'), meta: { requiresAuth: true, requiresStaff: true } },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to) => {
    const token = localStorage.getItem('token')
    if (to.meta.requiresAuth && !token) {
        return '/'
    }
    if (to.meta.requiresStaff && localStorage.getItem('isStaff') !== 'true') {
        return '/dashboard'
    }
})

export default router

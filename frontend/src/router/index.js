import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminLayout from '../layouts/AdminLayout.vue'
import CustomerLayout from '../layouts/CustomerLayout.vue'
import RepresentativeLayout from '../layouts/RepresentativeLayout.vue'
import Maintenance from '../views/Maintenance.vue'

const routes = [
    { path: '/', component: LoginView },
    { path: '/register', component: RegisterView },
    {path: '/misafir', component: () => import('../views/NoneedLogin.vue')},
    {path: '/misafir/rezervasyon/:code', component: () => import('../views/GuestReservationDetail.vue')},
    {
        path: '/dashboard',
        component: CustomerLayout,
        meta: { requiresAuth: true },
        children: [
            { path: '', component: () => import('../views/CustomerDashboard.vue') },
            { path: 'rezervasyonlar', component: () => import('../views/MyReservations.vue') },
            { path: 'rezervasyonlar/:id', component: () => import('../views/CustomerReservationDetail.vue') },
            { path: 'profil', component: () => import('../views/CustomerProfil.vue') },
        ]
    },
    {
        path: '/representative',
        component: RepresentativeLayout,
        meta: { requiresAuth: true, requiresRepresentative: true },
        children: [
            { path: '', component: () => import('../views/GununOzeti.vue') },
            { path: 'rezervasyonlar', component: () => import('../views/RepresentativeDashboard.vue') },
            { path: 'rezervasyonlar/:id', component: () => import('../views/StaffReservationDetail.vue') },
            { path: 'araclar', component: () => import('../views/RepresentativeAraclar.vue') },
            { path: 'profil', component: () => import('../views/RepresentativeProfil.vue') },
            {path: 'logs', component: () => import('../views/DeliveryLogs.vue')},
            { path: 'maintenance', component: Maintenance },
            { path: 'teslim/:id', component: () => import('../views/Teslim.vue') },
            { path: 'iade/:id', component: () => import('../views/Iade.vue') },
            { path: 'istatistikler', component: () => import('../views/RepresentativeIstatistikleri.vue') },
        ]
    },
    {
        path: '/operator',
        component: AdminLayout,
        meta: { requiresAuth: true, requiresAdmin: true },
        children: [
            { path: '', component: () => import('../views/OperatorDashboard.vue') },
            { path: 'rezervasyonlar/:id', component: () => import('../views/StaffReservationDetail.vue') },
            { path: 'araclar', component: () => import('../views/Araclar.vue') },
            { path: 'subeler', component: () => import('../views/Subeler.vue') },
            { path: 'kullanıcılar', component: () => import('../views/Kullanıcılar.vue') },
            { path: 'optimizasyon-sonuc', component: () => import('../views/Optimizasyon Sonucu.vue') },
            { path: 'karsılanamayan-rez', component: () => import('../views/Karşılanamayan Rezervasyonlar.vue') },
            { path: 'transfer-ucretleri', component: () => import('../views/TransferUcretleri.vue') },
            { path: 'profil', component: () => import('../views/OperatorProfil.vue') },
            { path: 'logs', component: () => import('../views/DeliveryLogs.vue') },
            { path: 'maintenance', component: Maintenance },
            { path: 'pricing', component: () => import('../views/Pricing.vue') },
            { path: 'teslim/:id', component: () => import('../views/Teslim.vue') },
            { path: 'iade/:id', component: () => import('../views/Iade.vue') },
            { path: 'admin-stats', component: () => import('../views/AdminIstatistikleri.vue'), meta: { requiresAuth: true}}
            
        ]
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to) => {
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')

    if (to.matched.some(r => r.meta.requiresAuth) && !token) {
        return '/'
    }
    if (to.matched.some(r => r.meta.requiresAdmin) && role !== 'admin') {
        return role === 'representative' ? '/representative' : '/dashboard'
    }
    if (to.matched.some(r => r.meta.requiresRepresentative) && role !== 'representative' && role !== 'admin') {
        return '/dashboard'
    }
})

export default router

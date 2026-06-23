<template>
  <div class="page">

    <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <div :class="['sidebar', { open: sidebarOpen }]">
      <div class="sidebar-header">
        <span class="sidebar-title">Menü</span>
        <button class="sidebar-close" @click="sidebarOpen = false">✕</button>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/operator" class="sidebar-item" @click="sidebarOpen = false">Rezervasyonlar</router-link>
        <router-link to="/operator/araclar" class="sidebar-item" @click="sidebarOpen = false">Araçlar</router-link>
        <router-link to="/operator/subeler" class="sidebar-item" @click="sidebarOpen = false">Şubeler</router-link>
        <router-link to="/operator/kullanıcılar" class="sidebar-item" @click="sidebarOpen = false">Kullanıcılar</router-link>
        <router-link to="/operator/optimizasyon-sonuc" class="sidebar-item" @click="sidebarOpen = false">Optimizasyon Sonucu</router-link>
        <router-link to="/operator/karsılanamayan-rez" class="sidebar-item active" @click="sidebarOpen = false">Karşılanamayan Rezervasyonlar</router-link>
      </nav>
    </div>

    <div class="topbar">
      <div class="brand-group">
        <button class="hamburger" @click="sidebarOpen = true">&#9776;</button>
        <router-link to="/operator" class="brand">Araç Kiralama</router-link>
      </div>
      <div class="right">
        <span class="role-badge">Operatör</span>
        <button class="btn-logout" @click="handleLogout">Çıkış Yap</button>
      </div>
    </div>

    <div class="content">
      <div v-if="!result" class="empty-state">
        <p>Henüz optimizasyon çalıştırılmadı.</p>
        <router-link to="/operator" class="btn-go">Rezervasyonlar sayfasına git →</router-link>
      </div>

      <div v-else class="section">
        <h2>Karşılanamayan Rezervasyonlar</h2>

        <p v-if="result.unassigned.length === 0" class="all-good">
          Tüm rezervasyonlar karşılandı.
        </p>

        <table v-else>
          <thead>
            <tr>
              <th>Rezervasyon</th>
              <th>Müşteri</th>
              <th>Şube</th>
              <th>Grup</th>
              <th>Başlangıç</th>
              <th>Bitiş</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in result.unassigned" :key="r.reservation_id">
              <td>{{ r.reservation_id }}</td>
              <td>{{ r.customer_username }}</td>
              <td>{{ r.branch_name }}</td>
              <td>{{ r.vehicle_group }}</td>
              <td>{{ r.start_date }}</td>
              <td>{{ r.end_date }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useOptimizationStore } from '../stores/optimization'

const auth = useAuthStore()
const optimizationStore = useOptimizationStore()
const router = useRouter()
const sidebarOpen = ref(false)

const result = computed(() => optimizationStore.result)

onMounted(async () => {
  if (!optimizationStore.result) {
    const res = await axios.get('http://127.0.0.1:8000/api/optimize/latest/')
    if (res.data) optimizationStore.setResult(res.data)
  }
})

async function handleLogout() {
  await axios.post('http://127.0.0.1:8000/api/logout/')
  auth.logout()
  router.push('/')
}
</script>

<style scoped>
.page { min-height: 100vh; background: #f8f9fa; font-family: sans-serif; }
.sidebar-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); z-index: 100; }
.sidebar { position: fixed; top: 0; left: 0; height: 100vh; width: 260px; background: white; z-index: 101; box-shadow: 4px 0 16px rgba(0,0,0,0.12); transform: translateX(-100%); transition: transform 0.25s ease; display: flex; flex-direction: column; }
.sidebar.open { transform: translateX(0); }
.sidebar-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #e5e7eb; }
.sidebar-title { font-size: 15px; font-weight: 700; color: #1e293b; }
.sidebar-close { background: none; border: none; font-size: 18px; color: #94a3b8; cursor: pointer; line-height: 1; }
.sidebar-close:hover { color: #1e293b; }
.sidebar-nav { display: flex; flex-direction: column; padding: 12px; gap: 2px; }
.sidebar-item { display: flex; align-items: center; padding: 10px 12px; border-radius: 8px; font-size: 14px; font-weight: 500; color: #1e293b; text-decoration: none; cursor: pointer; }
.sidebar-item:hover { background: #f1f5f9; }
.sidebar-item.active { background: #ede9fe; color: #6366f1; font-weight: 600; }
.topbar { display: flex; justify-content: space-between; align-items: center; padding: 16px 40px; background: white; border-bottom: 1px solid #e5e7eb; }
.brand-group { display: flex; align-items: center; gap: 12px; }
.hamburger { background: none; border: none; font-size: 20px; color: #475569; cursor: pointer; padding: 0; line-height: 1; }
.hamburger:hover { color: #1e293b; }
.brand { font-size: 18px; font-weight: 700; color: #1e293b; text-decoration: none; }
.right { display: flex; align-items: center; gap: 12px; }
.role-badge { padding: 4px 12px; background: #ede9fe; color: #6366f1; border-radius: 50px; font-size: 12px; font-weight: 700; }
.btn-logout { padding: 6px 14px; background: #dc2626; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; }
.content { max-width: 1100px; margin: 0 auto; padding: 40px; }
.empty-state { text-align: center; padding: 80px 40px; color: #94a3b8; font-size: 15px; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.btn-go { padding: 10px 24px; background: #6366f1; color: white; border-radius: 50px; text-decoration: none; font-size: 14px; font-weight: 600; }
.section h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0 0 20px; }
.all-good { color: #10b981; font-size: 15px; font-weight: 500; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
td { border-top: 1px solid #f1f5f9; }
</style>

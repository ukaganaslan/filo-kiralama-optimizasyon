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
        <router-link to="/operator/optimizasyon-sonuc" class="sidebar-item active" @click="sidebarOpen = false">Optimizasyon Sonucu</router-link>
        <router-link to="/operator/karsılanamayan-rez" class="sidebar-item" @click="sidebarOpen = false">Karşılanamayan Rezervasyonlar</router-link>
      </nav>
    </div>

    <div class="topbar">
      <div class="brand-group">
        <button class="hamburger" @click="sidebarOpen = true">&#9776;</button>
        <router-link to="/operator" class="brand">Araç Kiralama</router-link>
      </div>
      <div class="right">
        <div class="user-menu" ref="menuRef">
          <span class="role-badge" @click="menuOpen = !menuOpen">Operatör</span>
          <div v-if="menuOpen" class="dropdown">
            <router-link to="/operator/profil" class="dropdown-item" @click="menuOpen = false">Profil Ayarları</router-link>
            <button class="dropdown-item dropdown-logout" @click="handleLogout">Çıkış Yap</button>
          </div>
        </div>
      </div>
    </div>

    <div class="content">
      <div v-if="!result" class="empty-state">
        <p>Henüz optimizasyon çalıştırılmadı.</p>
        <router-link to="/operator" class="btn-go">Rezervasyonlar sayfasına git →</router-link>
      </div>

      <div v-else class="section">
        <h2>Optimizasyon Sonucu</h2>

        <div class="stats-row">
          <div class="stat-card">
            <div class="stat-value">{{ result.score }}</div>
            <div class="stat-label">Toplam Skor</div>
          </div>
          <div class="stat-card green">
            <div class="stat-value">{{ result.fulfilled }}</div>
            <div class="stat-label">Karşılanan</div>
          </div>
          <div class="stat-card red">
            <div class="stat-value">{{ result.unfulfilled }}</div>
            <div class="stat-label">Karşılanamayan</div>
          </div>
        </div>

        <h3>Atamalar</h3>
        <table>
          <thead>
            <tr>
              <th>Rezervasyon</th>
              <th>Müşteri</th>
              <th>Araç</th>
              <th>Başlangıç</th>
              <th>Bitiş</th>
              <th>Transfer</th>
              <th>Upgrade</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in result.assignments" :key="a.reservation_id">
              <td>{{ a.reservation_id }}</td>
              <td>{{ a.customer_username }}</td>
              <td>{{ a.vehicle_id }}</td>
              <td>{{ a.start_date }}</td>
              <td>{{ a.end_date }}</td>
              <td>{{ a.transfer_cost }}</td>
              <td>{{ a.is_upgrade ? 'Evet' : 'Hayır' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useOptimizationStore } from '../stores/optimization'

const auth = useAuthStore()
const optimizationStore = useOptimizationStore()
const router = useRouter()
const sidebarOpen = ref(false)
const menuOpen = ref(false)
const menuRef = ref(null)
function handleClickOutside(e) {
  if (menuRef.value && !menuRef.value.contains(e.target)) menuOpen.value = false
}
onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))

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
.user-menu { position: relative; }
.role-badge { padding: 4px 12px; background: #ede9fe; color: #6366f1; border-radius: 50px; font-size: 12px; font-weight: 700; cursor: pointer; user-select: none; }
.role-badge:hover { background: #ddd6fe; }
.dropdown {
  position: absolute; top: calc(100% + 8px); right: 0;
  background: white; border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.12);
  border: 1px solid #e5e7eb; min-width: 160px;
  overflow: hidden; z-index: 50;
}
.dropdown-item {
  display: block; width: 100%; padding: 10px 16px;
  font-size: 14px; color: #1e293b; text-decoration: none;
  text-align: left; background: none; border: none;
  cursor: pointer; box-sizing: border-box;
}
.dropdown-item:hover { background: #f1f5f9; }
.dropdown-logout { color: #dc2626; }
.btn-logout { padding: 6px 14px; background: #dc2626; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; }
.content { max-width: 1100px; margin: 0 auto; padding: 40px; }
.empty-state { text-align: center; padding: 80px 40px; color: #94a3b8; font-size: 15px; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.btn-go { padding: 10px 24px; background: #6366f1; color: white; border-radius: 50px; text-decoration: none; font-size: 14px; font-weight: 600; }
.section h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0 0 20px; }
.stats-row { display: flex; gap: 16px; margin-bottom: 24px; }
.stat-card { flex: 1; background: white; border-radius: 10px; padding: 20px 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); border-left: 4px solid #6366f1; }
.stat-card.green { border-color: #10b981; }
.stat-card.red { border-color: #ef4444; }
.stat-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 12px; color: #94a3b8; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
h3 { font-size: 16px; font-weight: 700; color: #1e293b; margin: 24px 0 12px; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
td { border-top: 1px solid #f1f5f9; }
</style>

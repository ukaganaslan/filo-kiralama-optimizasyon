<template>
  <div class="page">

    <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <div :class="['sidebar', { open: sidebarOpen }]">
      <div class="sidebar-header">
        <span class="sidebar-title">Menü</span>
        <button class="sidebar-close" @click="sidebarOpen = false">✕</button>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="sidebar-item" @click="sidebarOpen = false">Yeni Rezervasyon</router-link>
        <router-link to="/dashboard/rezervasyonlar" class="sidebar-item active" @click="sidebarOpen = false">Rezervasyonlarım</router-link>
      </nav>
    </div>

    <div class="topbar">
      <div class="brand-group">
        <button class="hamburger" @click="sidebarOpen = true">&#9776;</button>
        <router-link to="/dashboard" class="brand">Araç Kiralama</router-link>
      </div>
      <div class="user-menu" ref="menuRef">
        <span class="user-badge" @click="menuOpen = !menuOpen">{{ auth.username }}</span>
        <div v-if="menuOpen" class="dropdown">
          <router-link to="/dashboard/profil" class="dropdown-item" @click="menuOpen = false">Profil Ayarları</router-link>
          <button class="dropdown-item dropdown-logout" @click="handleLogout">Çıkış Yap</button>
        </div>
      </div>
    </div>

    <div class="section">
      <h2>Rezervasyonlarım</h2>
      <p v-if="reservations.length === 0" class="empty">Henüz rezervasyonunuz yok.</p>
      <table v-else>
        <thead>
          <tr>
            <th>ID</th>
            <th>Şube</th>
            <th>Grup</th>
            <th>Başlangıç</th>
            <th>Bitiş</th>
            <th>Durum</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in reservations" :key="r.id">
            <td>{{ r.reservation_id }}</td>
            <td>{{ r.branch_name }}</td>
            <td>{{ r.vehicle_group }}</td>
            <td>{{ r.start_date }}</td>
            <td>{{ r.end_date }}</td>
            <td><span :class="'badge badge-' + r.status">{{ r.status }}</span></td>
            <td>
              <button
                v-if="r.status !== 'cancelled'"
                class="btn-cancel"
                @click="handleCancel(r.reservation_id)"
              >İptal Et</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="error" class="error">{{ error }}</p>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const sidebarOpen = ref(false)
const menuOpen = ref(false)
const menuRef = ref(null)
function handleClickOutside(e) {
  if (menuRef.value && !menuRef.value.contains(e.target)) menuOpen.value = false
}
onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
const reservations = ref([])
const error = ref('')

onMounted(async () => {
  const res = await axios.get('http://127.0.0.1:8000/api/reservations/')
  reservations.value = res.data
})

async function handleCancel(reservationId) {
  try {
    await axios.post(`http://127.0.0.1:8000/api/reservations/${reservationId}/cancel/`)
    const res = await axios.get('http://127.0.0.1:8000/api/reservations/')
    reservations.value = res.data
  } catch {
    error.value = 'İptal işlemi başarısız.'
  }
}

async function handleLogout() {
  await axios.post('http://127.0.0.1:8000/api/logout/')
  auth.logout()
  router.push('/')
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f8f9fa;
  font-family: sans-serif;
}
.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 100;
}
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 260px;
  background: white;
  z-index: 101;
  box-shadow: 4px 0 16px rgba(0,0,0,0.12);
  transform: translateX(-100%);
  transition: transform 0.25s ease;
  display: flex;
  flex-direction: column;
}
.sidebar.open { transform: translateX(0); }
.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}
.sidebar-title { font-size: 15px; font-weight: 700; color: #1e293b; }
.sidebar-close {
  background: none;
  border: none;
  font-size: 18px;
  color: #94a3b8;
  cursor: pointer;
  line-height: 1;
}
.sidebar-close:hover { color: #1e293b; }
.sidebar-nav {
  display: flex;
  flex-direction: column;
  padding: 12px;
  gap: 2px;
}
.sidebar-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  text-decoration: none;
  cursor: pointer;
}
.sidebar-item:hover { background: #f1f5f9; }
.sidebar-item.active {
  background: #ede9fe;
  color: #6366f1;
  font-weight: 600;
}
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 40px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}
.brand-group { display: flex; align-items: center; gap: 12px; }
.hamburger {
  background: none;
  border: none;
  font-size: 20px;
  color: #475569;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}
.hamburger:hover { color: #1e293b; }
.brand {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  text-decoration: none;
}
.user-menu { position: relative; }
.user-badge {
  padding: 6px 14px;
  background: #ede9fe; color: #6366f1;
  border-radius: 50px; font-size: 13px; font-weight: 600;
  cursor: pointer; user-select: none;
}
.user-badge:hover { background: #ddd6fe; }
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
.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 14px;
  color: #64748b;
}
.btn-logout {
  padding: 6px 14px;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}
.section {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px;
}
.section h2 {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 16px;
}
.empty { color: #94a3b8; font-size: 14px; }
table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th {
  background: #f1f5f9;
  font-weight: 600;
  color: #475569;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
td { border-top: 1px solid #f1f5f9; }
.badge { padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: 600; }
.badge-pending { background: #fef3c7; color: #92400e; }
.badge-assigned { background: #d1fae5; color: #065f46; }
.badge-cancelled { background: #fee2e2; color: #991b1b; }
.btn-cancel {
  padding: 4px 12px;
  background: white;
  color: #dc2626;
  border: 1px solid #dc2626;
  border-radius: 50px;
  font-size: 12px;
  cursor: pointer;
}
.btn-cancel:hover { background: #fee2e2; }
.error { color: #dc2626; font-size: 14px; margin-top: 12px; }
</style>

<template>
  <div class="page">

    <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <div :class="['sidebar', { open: sidebarOpen }]">
      <div class="sidebar-header">
        <span class="sidebar-title">Menü</span>
        <button class="sidebar-close" @click="sidebarOpen = false">✕</button>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/operator" class="sidebar-item active" @click="sidebarOpen = false">Rezervasyonlar</router-link>
        <router-link to="/operator/araclar" class="sidebar-item" @click="sidebarOpen = false">Araçlar</router-link>
        <router-link to="/operator/subeler" class="sidebar-item" @click="sidebarOpen = false">Şubeler</router-link>
        <router-link to="/operator/kullanıcılar" class="sidebar-item" @click="sidebarOpen = false">Kullanıcılar</router-link>
        <router-link to="/operator/optimizasyon-sonuc" class="sidebar-item" @click="sidebarOpen = false">Optimizasyon Sonucu</router-link>
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

      <div class="section" id="rezervasyonlar">
        <div class="section-header">
          <h2>Tüm Rezervasyonlar</h2>
          <div class="header-actions">
            <select v-model="activeView" class="view-select">
              <option value="list">Liste Görünümü</option>
              <option value="calendar">Takvim Görünümü</option>
            </select>
            <button class="btn-optimize" @click="handleOptimize" :disabled="optimizing">
              {{ optimizing ? 'Çalışıyor...' : 'Optimize Et →' }}
            </button>
          </div>
        </div>

        <FullCalendar v-if="activeView === 'calendar'" :options="calendarOptions" />

        <table v-if="activeView === 'list'">
          <thead>
            <tr>
              <th>ID</th>
              <th>Müşteri</th>
              <th>Şube</th>
              <th>Grup</th>
              <th>Başlangıç</th>
              <th>Bitiş</th>
              <th>Durum</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in reservations" :key="r.id">
              <td>{{ r.reservation_id }}</td>
              <td>{{ r.customer_username }}</td>
              <td>{{ r.branch_name }}</td>
              <td>{{ r.vehicle_group }}</td>
              <td>{{ r.start_date }}</td>
              <td>{{ r.end_date }}</td>
              <td><span :class="'badge badge-' + r.status">{{ r.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useOptimizationStore } from '../stores/optimization'
import FullCalendar from '@fullcalendar/vue3'
import ResourceTimelinePlugin from '@fullcalendar/resource-timeline'
import trLocale from '@fullcalendar/core/locales/tr'

const auth = useAuthStore()
const optimizationStore = useOptimizationStore()
const router = useRouter()
const reservations = ref([])
const optimizing = ref(false)
const sidebarOpen = ref(false)
const activeView = ref('list')
const vehicles = ref([])
const menuOpen = ref(false)
const menuRef = ref(null)

function handleClickOutside(e) {
  if (menuRef.value && !menuRef.value.contains(e.target)) menuOpen.value = false
}
onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))

onMounted(async () => {
  const [rezRes, vehicleRes] = await Promise.all([
    axios.get('http://127.0.0.1:8000/api/reservations/'),
    axios.get('http://127.0.0.1:8000/api/vehicles/'),
  ])
  reservations.value = rezRes.data
  vehicles.value = vehicleRes.data
})

async function handleOptimize() {
  optimizing.value = true
  try {
    const res = await axios.post('http://127.0.0.1:8000/api/optimize/')
    optimizationStore.setResult(res.data)
    const rezRes = await axios.get('http://127.0.0.1:8000/api/reservations/')
    reservations.value = rezRes.data
  } finally {
    optimizing.value = false
  }
}

const calendarOptions = computed(() => ({
  plugins: [ResourceTimelinePlugin],
  initialView: 'resourceTimelineMonth',
  schedulerLicenseKey: 'non-commercial-and-evaluation',
  locale: trLocale,
  height: 'auto',
  slotDuration: { days: 1 },
  resourceAreaWidth: '210px',
  
  slotLabelFormat: [{ month: 'long', year: 'numeric' }, { day: 'numeric'}],
  headerToolbar: {
    left: 'prev,next',
    right: '',
  },
  resources: vehicles.value.map(v => ({
    id: v.vehicle_id,
    title: `${v.vehicle_id} (${v.group})`,
  })),
  events: reservations.value
    .filter(r => r.assigned_vehicle_id && r.status !== 'cancelled')
    .map(r => ({
      resourceId: r.assigned_vehicle_id,
      title: r.reservation_id,
      start: r.start_date,
      end: r.end_date,
    })),
}))

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
.sidebar.open {
  transform: translateX(0);
}
.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}
.sidebar-title {
  font-size: 15px;
  font-weight: 700;
  color: #1e293b;
}
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
  padding: 12px 12px;
  gap: 2px;
}
.sidebar-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  text-decoration: none;
  cursor: pointer;
}
.sidebar-item:not(.disabled):hover {
  background: #f1f5f9;
}
.sidebar-item.disabled {
  color: #94a3b8;
  cursor: default;
}
.soon {
  font-size: 10px;
  font-weight: 600;
  background: #f1f5f9;
  color: #94a3b8;
  padding: 2px 6px;
  border-radius: 50px;
  letter-spacing: 0.03em;
}
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 40px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}
.brand-group {
  display: flex;
  align-items: center;
  gap: 12px;
}
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
  cursor: pointer;
}
.right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user-menu { position: relative; }
.role-badge {
  padding: 4px 12px;
  background: #ede9fe;
  color: #6366f1;
  border-radius: 50px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  user-select: none;
}
.role-badge:hover { background: #ddd6fe; }
.dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.12);
  border: 1px solid #e5e7eb;
  min-width: 160px;
  overflow: hidden;
  z-index: 50;
}
.dropdown-item {
  display: block;
  width: 100%;
  padding: 10px 16px;
  font-size: 14px;
  color: #1e293b;
  text-decoration: none;
  text-align: left;
  background: none;
  border: none;
  cursor: pointer;
  box-sizing: border-box;
}
.dropdown-item:hover { background: #f1f5f9; }
.dropdown-logout { color: #dc2626; }
.btn-logout {
  padding: 6px 14px;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}
.content {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px;
  display: flex;
  flex-direction: column;
  gap: 40px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.view-select {
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 13px;
  color: #475569;
  background: white;
  cursor: pointer;
  outline: none;
}
.view-select:focus {
  border-color: #6366f1;
}
h2 {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 16px;
}
h3 {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin: 24px 0 12px;
}
.btn-optimize {
  padding: 10px 24px;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.btn-optimize:disabled {
  background: #a5b4fc;
  cursor: not-allowed;
}
.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  flex: 1;
  background: white;
  border-radius: 10px;
  padding: 20px 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  border-left: 4px solid #6366f1;
}
.stat-card.green { border-color: #10b981; }
.stat-card.red { border-color: #ef4444; }
.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}
.stat-label {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
th, td {
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
}
th {
  background: #f1f5f9;
  font-weight: 600;
  color: #475569;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
td { border-top: 1px solid #f1f5f9; }
.badge {
  padding: 3px 10px;
  border-radius: 50px;
  font-size: 12px;
  font-weight: 600;
}
.badge-pending { background: #fef3c7; color: #92400e; }
.badge-assigned { background: #d1fae5; color: #065f46; }
.badge-cancelled { background: #fee2e2; color: #991b1b; }
</style>

<style>
.fc .fc-timeline-slot-label {
  color: #1e293b !important;
}
.fc .fc-col-header-cell-cushion {
  color: #1e293b !important;
}

</style>

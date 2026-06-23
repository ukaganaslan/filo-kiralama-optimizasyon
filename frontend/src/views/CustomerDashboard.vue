<template>
  <div class="page">

    <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <div :class="['sidebar', { open: sidebarOpen }]">
      <div class="sidebar-header">
        <span class="sidebar-title">Menü</span>
        <button class="sidebar-close" @click="sidebarOpen = false">✕</button>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="sidebar-item active" @click="sidebarOpen = false">Yeni Rezervasyon</router-link>
        <router-link to="/dashboard/rezervasyonlar" class="sidebar-item" @click="sidebarOpen = false">Rezervasyonlarım</router-link>
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

    <div class="hero" id="yeni-rezervasyon">
      <h1>Aracınızı Hemen Kiralayın</h1>

      <div class="booking-card">
        <div class="card-row">
          <div class="card-field">
            <label>ŞUBE</label>
            <select v-model="form.branch" @change="fetchAvailability">
              <option disabled value="">Şube Seçin</option>
              <option v-for="branch in branches" :key="branch.id" :value="branch.id">
                {{ branch.title || branch.name }}
              </option>
            </select>
          </div>

          <div class="divider"></div>

          <div class="card-field">
            <label>ARAÇ GRUBU</label>
            <select v-model="form.vehicle_group" @change="fetchAvailability">
              <option disabled value="">Grup Seçin</option>
              <option value="economy">Ekonomi</option>
              <option value="mid">Orta Sınıf</option>
              <option value="suv">SUV</option>
            </select>
          </div>
        </div>

        <div v-if="availabilityLoading" class="loading-hint">Müsait günler yükleniyor...</div>

        <div v-if="availableDates.length > 0" class="calendar-section">
          <label>TARİH ARALIĞI SEÇİN</label>
          <p class="hint">Gri günler dolu, açık günler müsait.</p>
          <VDatePicker
            v-model.range="dateRange"
            :disabled-dates="disabledDates"
            :min-date="new Date()"
            color="indigo"
            is-expanded
          />
        </div>

        <div v-if="form.branch && form.vehicle_group && availableDates.length === 0 && !availabilityLoading" class="no-avail">
          Bu şube ve grupta müsait gün bulunmuyor.
        </div>

        <p v-if="formError" class="error">{{ formError }}</p>
        <p v-if="formSuccess" class="success">{{ formSuccess }}</p>

        <div v-if="dateRange.start && dateRange.end" class="card-footer">
          <span class="date-summary">
            {{ toLocalDateStr(dateRange.start) }} → {{ toLocalDateStr(dateRange.end) }}
          </span>
          <button class="btn-reserve" @click="handleCreate">Rezervasyon Oluştur →</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
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

const branches = ref([])
const availableDates = ref([])
const availabilityLoading = ref(false)
const formError = ref('')
const formSuccess = ref('')

const form = ref({ branch: '', vehicle_group: '' })
const dateRange = ref({ start: null, end: null })

const disabledDates = computed(() => {
  if (availableDates.value.length === 0) return []
  const available = new Set(availableDates.value)
  const disabled = []
  const today = new Date()
  for (let i = 0; i < 90; i++) {
    const d = new Date(today)
    d.setDate(today.getDate() + i)
    const str = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
    if (!available.has(str)) disabled.push(new Date(d))
  }
  return disabled
})

onMounted(async () => {
  const res = await axios.get('http://127.0.0.1:8000/api/branches/')
  branches.value = res.data
})

async function fetchAvailability() {
  if (!form.value.branch || !form.value.vehicle_group) return
  availabilityLoading.value = true
  availableDates.value = []
  dateRange.value = { start: null, end: null }
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/availability/', {
      params: { branch: form.value.branch, group: form.value.vehicle_group }
    })
    availableDates.value = res.data.available_dates
  } finally {
    availabilityLoading.value = false
  }
}

function toLocalDateStr(date) {
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}

async function handleCreate() {
  formError.value = ''
  formSuccess.value = ''
  try {
    await axios.post('http://127.0.0.1:8000/api/reservations/', {
      branch: form.value.branch,
      vehicle_group: form.value.vehicle_group,
      start_date: toLocalDateStr(dateRange.value.start),
      end_date: toLocalDateStr(dateRange.value.end),
    })
    formSuccess.value = 'Rezervasyon oluşturuldu, onay bekleniyor.'
    form.value = { branch: '', vehicle_group: '' }
    dateRange.value = { start: null, end: null }
    availableDates.value = []
  } catch {
    formError.value = 'Rezervasyon oluşturulamadı.'
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

.hero {
  padding: 48px 40px 32px;
  max-width: 900px;
  margin: 0 auto;
}
.hero h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 24px;
}

.booking-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  overflow: hidden;
}

.card-row {
  display: flex;
  align-items: stretch;
}
.card-field {
  flex: 1;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.card-field label {
  font-size: 11px;
  font-weight: 700;
  color: #6366f1;
  letter-spacing: 0.08em;
}
.card-field select {
  border: none;
  outline: none;
  font-size: 15px;
  color: #1e293b;
  background: transparent;
  cursor: pointer;
  padding: 4px 0;
}
.divider {
  width: 1px;
  background: #e5e7eb;
  margin: 16px 0;
}

.calendar-section {
  border-top: 1px solid #e5e7eb;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.calendar-section label {
  font-size: 11px;
  font-weight: 700;
  color: #6366f1;
  letter-spacing: 0.08em;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
  background: #fafafa;
}
.date-summary {
  font-size: 14px;
  color: #475569;
  font-weight: 500;
}
.btn-reserve {
  padding: 12px 28px;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 50px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-reserve:hover {
  background: #4f46e5;
}

.loading-hint {
  padding: 12px 24px;
  font-size: 13px;
  color: #94a3b8;
  border-top: 1px solid #e5e7eb;
}
.no-avail {
  padding: 12px 24px;
  font-size: 13px;
  color: #dc2626;
  border-top: 1px solid #e5e7eb;
}
.hint {
  font-size: 12px;
  color: #94a3b8;
}
.error { color: #dc2626; font-size: 14px; padding: 0 24px; }
.success { color: #16a34a; font-size: 14px; padding: 0 24px; }

</style>

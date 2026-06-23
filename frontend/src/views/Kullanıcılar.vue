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
        <router-link to="/operator/kullanıcılar" class="sidebar-item active" @click="sidebarOpen = false">Kullanıcılar</router-link>
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
        <span class="role-badge">Operatör</span>
        <button class="btn-logout" @click="handleLogout">Çıkış Yap</button>
      </div>
    </div>

    <div class="content">
      <div class="section-header">
        <h2>Kullanıcılar</h2>
        <span class="count-badge">{{ users.length }} kullanıcı</span>
      </div>

      <div class="search-bar">
        <input v-model="search" type="text" placeholder="Ad, kullanıcı adı veya telefon ara..." class="search-input" />
      </div>

      <table>
        <thead>
          <tr>
            <th>Kullanıcı Adı</th>
            <th>Ad Soyad</th>
            <th>E-posta</th>
            <th>Telefon</th>
            <th>Kayıt Tarihi</th>
            <th>Rezervasyon Sayısı</th>
            <th>Kullanıcı Durumu</th>
            <th></th>
            
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in filtered" :key="u.id">
            <td class="username">{{ u.username }}</td>
            <td>{{ u.full_name || '—' }}</td>
            <td>{{ u.email || '—' }}</td>
            <td>{{ u.phone || '—' }}</td>
            <td>{{ u.date_joined }}</td>
            <td><span class="rez-count">{{ u.reservation_count }}</span></td>
            <td>
                <span :class="u.is_active ? 'badge-active' : 'badge-passive'">
                {{ u.is_active ? 'Aktif' : 'Pasif' }}
                </span>         
            </td>
            <td>
                <button @click="toggleActive(u)">
                {{ u.is_active ? 'Pasife Al' : 'Aktife Al' }}
                 </button>
            </td>
          </tr>
          <tr v-if="filtered.length === 0">
            <td colspan="6" class="empty">Kullanıcı bulunamadı.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const sidebarOpen = ref(false)
const users = ref([])
const search = ref('')

onMounted(async () => {
  const res = await axios.get('http://127.0.0.1:8000/api/users/')
  users.value = res.data
})

const filtered = computed(() => {
  const q = search.value.toLowerCase()
  if (!q) return users.value
  return users.value.filter(u =>
    u.username.toLowerCase().includes(q) ||
    u.full_name.toLowerCase().includes(q) ||
    u.phone.includes(q)
  )
})

async function handleLogout() {
  await axios.post('http://127.0.0.1:8000/api/logout/')
  auth.logout()
  router.push('/')
}

async function toggleActive(u) {
  await axios.post(`http://127.0.0.1:8000/api/users/${u.id}/toggle-active/`)
  u.is_active = !u.is_active
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
  background: rgba(0,0,0,0.3);
  z-index: 100;
}
.sidebar {
  position: fixed;
  top: 0; left: 0;
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
  background: none; border: none;
  font-size: 18px; color: #94a3b8;
  cursor: pointer; line-height: 1;
}
.sidebar-close:hover { color: #1e293b; }
.sidebar-nav {
  display: flex; flex-direction: column;
  padding: 12px; gap: 2px;
}
.sidebar-item {
  display: flex; align-items: center;
  padding: 10px 12px; border-radius: 8px;
  font-size: 14px; font-weight: 500;
  color: #1e293b; text-decoration: none;
}
.sidebar-item:hover { background: #f1f5f9; }
.sidebar-item.active { background: #ede9fe; color: #6366f1; font-weight: 600; }
.topbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 40px; background: white;
  border-bottom: 1px solid #e5e7eb;
}
.brand-group { display: flex; align-items: center; gap: 12px; }
.hamburger {
  background: none; border: none;
  font-size: 20px; color: #475569;
  cursor: pointer; padding: 0; line-height: 1;
}
.hamburger:hover { color: #1e293b; }
.brand {
  font-size: 18px; font-weight: 700;
  color: #1e293b; text-decoration: none;
}
.right { display: flex; align-items: center; gap: 12px; }
.role-badge {
  padding: 4px 12px;
  background: #ede9fe; color: #6366f1;
  border-radius: 50px; font-size: 12px; font-weight: 700;
}
.btn-logout {
  padding: 6px 14px; background: #dc2626;
  color: white; border: none; border-radius: 6px;
  cursor: pointer; font-size: 13px;
}
.content {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px;
}
.section-header {
  display: flex; align-items: center; gap: 12px; margin-bottom: 20px;
}
h2 {
  font-size: 20px; font-weight: 700; color: #1e293b; margin: 0;
}
.count-badge {
  padding: 3px 10px;
  background: #f1f5f9; color: #64748b;
  border-radius: 50px; font-size: 12px; font-weight: 600;
}
.search-bar { margin-bottom: 16px; }
.search-input {
  width: 320px;
  padding: 9px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  color: #1e293b;
  outline: none;
}
.search-input:focus { border-color: #6366f1; }
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
  background: #f1f5f9; font-weight: 600;
  color: #475569; font-size: 12px;
  text-transform: uppercase; letter-spacing: 0.05em;
}
td { border-top: 1px solid #f1f5f9; color: #374151; }
.username { font-weight: 600; color: #1e293b; }
.rez-count {
  display: inline-block;
  padding: 2px 10px;
  background: #ede9fe; color: #35455e;
  border-radius: 50px; font-size: 12px; font-weight: 600;
}
.empty {
  text-align: center; color: #94a3b8;
  padding: 32px !important;
}
</style>

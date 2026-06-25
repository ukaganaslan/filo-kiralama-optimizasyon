<template>
  <div class="layout">
    <div v-if="mobileOpen" class="overlay" @click="mobileOpen = false"></div>

    <aside :class="['sidebar', { open: mobileOpen }]">
      <div class="sidebar-brand">
        <router-link to="/dashboard" class="brand-link" @click="mobileOpen = false">
          <div class="brand-icon">K</div>
          <div>
            <div class="brand-name">Araç Kiralama</div>
            
          </div>
        </router-link>
        <button class="close-btn" @click="mobileOpen = false">✕</button>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="nav-item" exact-active-class="nav-item--active" active-class="" @click="mobileOpen = false">
          <span class="nav-icon">🔍</span> Yeni Rezervasyon
        </router-link>
        <router-link to="/dashboard/rezervasyonlar" class="nav-item" active-class="nav-item--active" @click="mobileOpen = false">
          <span class="nav-icon">📋</span> Rezervasyonlarım
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="footer-user">
          <div class="footer-username">{{ auth.username }}</div>
          <span class="footer-badge">Müşteri</span>
        </div>
      </div>
    </aside>

    <div class="main">
      <header class="topbar">
        <button class="hamburger" @click="mobileOpen = true">&#9776;</button>
        <span class="topbar-title">{{ pageTitle }}</span>
        <div class="topbar-right">
          <div class="user-menu" ref="menuRef">
            <button class="user-btn" @click="menuOpen = !menuOpen">
              {{ auth.username }} <span class="chevron">▾</span>
            </button>
            <div v-if="menuOpen" class="dropdown">
              <router-link to="/dashboard/profil" class="dropdown-item" @click="menuOpen = false">⚙️ Profil Ayarları </router-link>
              <button class="dropdown-item dropdown-logout" @click="handleLogout">➜] Çıkış Yap </button>
            </div>
          </div>
        </div>
      </header>
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const mobileOpen = ref(false)
const menuOpen = ref(false)
const menuRef = ref(null)

const pageTitles = {
  '/dashboard': 'Yeni Rezervasyon',
  '/dashboard/rezervasyonlar': 'Rezervasyonlarım',
  '/dashboard/profil': 'Profil Ayarları',
}
const pageTitle = computed(() => pageTitles[route.path] || '')

function handleClickOutside(e) {
  if (menuRef.value && !menuRef.value.contains(e.target)) menuOpen.value = false
}
onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))

async function handleLogout() {
  await axios.post('/api/logout/')
  auth.logout()
  router.push('/')
}
</script>

<style scoped>
.layout { display: flex; min-height: 100vh; background: #f8fafc; }
.sidebar {
  width: 240px;
  flex-shrink: 0;
  background: white;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}
.sidebar-brand {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 16px 16px;
  border-bottom: 1px solid #f1f5f9;
}
.brand-link { display: flex; align-items: center; gap: 10px; text-decoration: none; }
.brand-icon { width: 34px; height: 34px; background: #6366f1; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 15px; color: white; flex-shrink: 0; }
.brand-name { font-size: 14px; font-weight: 700; color: #1e293b; line-height: 1.2; }
.brand-role { font-size: 11px; color: #94a3b8; font-weight: 500; }
.close-btn { display: none; background: none; border: none; color: #94a3b8; font-size: 16px; cursor: pointer; padding: 4px; line-height: 1; }
.close-btn:hover { color: #1e293b; }
.sidebar-nav { display: flex; flex-direction: column; padding: 12px 10px; gap: 2px; flex: 1; }
.nav-item { display: flex; align-items: center; gap: 10px; padding: 9px 12px; border-radius: 7px; font-size: 13.5px; font-weight: 500; color: #475569; text-decoration: none; transition: background 0.15s, color 0.15s; }
.nav-item:hover { background: #f8fafc; color: #1e293b; }
.nav-item--active { background: #ede9fe; color: #6366f1; font-weight: 600; }
.nav-icon { font-size: 15px; width: 20px; text-align: center; }
.sidebar-footer { padding: 12px 16px; border-top: 1px solid #f1f5f9; }
.footer-user { display: flex; align-items: center; justify-content: space-between; }
.footer-username { font-size: 13px; color: #475569; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.footer-badge { padding: 2px 8px; background: #ede9fe; color: #6366f1; border-radius: 50px; font-size: 11px; font-weight: 700; flex-shrink: 0; }
.main { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.topbar { display: flex; align-items: center; padding: 0 32px; height: 56px; background: white; border-bottom: 1px solid #e2e8f0; position: sticky; top: 0; z-index: 10; gap: 16px; }
.hamburger { display: none; background: none; border: none; font-size: 20px; color: #475569; cursor: pointer; padding: 0; line-height: 1; flex-shrink: 0; }
.topbar-title { font-size: 15px; font-weight: 700; color: #0f172a; flex: 1; }
.topbar-right { display: flex; align-items: center; gap: 12px; margin-left: auto; }
.user-menu { position: relative; }
.user-btn { background: none; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 12px; font-size: 13px; font-weight: 600; color: #1e293b; cursor: pointer; display: flex; align-items: center; gap: 6px; white-space: nowrap; }
.user-btn:hover { background: #f1f5f9; }
.chevron { font-size: 10px; color: #94a3b8; }
.dropdown { position: absolute; top: calc(100% + 6px); right: 0; background: white; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.12); border: 1px solid #e2e8f0; min-width: 160px; overflow: hidden; z-index: 50; }
.dropdown-item { display: block; width: 100%; padding: 10px 16px; font-size: 13.5px; color: #1e293b; text-decoration: none; text-align: left; background: none; border: none; cursor: pointer; box-sizing: border-box; }
.dropdown-item:hover { background: #f1f5f9; }
.dropdown-logout { color: #dc2626; }
.overlay { display: none; }
@media (max-width: 768px) {
  .sidebar { position: fixed; top: 0; left: 0; height: 100vh; z-index: 101; transform: translateX(-100%); transition: transform 0.25s ease; }
  .sidebar.open { transform: translateX(0); }
  .close-btn { display: block; }
  .overlay { display: block; position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 100; }
  .hamburger { display: block; }
  .topbar { justify-content: space-between; }
}
</style>

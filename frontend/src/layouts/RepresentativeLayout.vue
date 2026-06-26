<template>
  <div class="layout">
    <div v-if="mobileOpen" class="overlay" @click="mobileOpen = false"></div>

    <aside :class="['sidebar', { collapsed, open: mobileOpen }]">

      <!-- Brand -->
      <div class="sidebar-brand">
        <router-link to="/representative" class="brand-link" @click="mobileOpen = false">
          <div class="brand-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 17H3a2 2 0 01-2-2V9a2 2 0 012-2h2M17 17h2a2 2 0 002-2V9a2 2 0 00-2-2h-2"/>
              <rect x="5" y="7" width="14" height="10" rx="2"/>
              <circle cx="7.5" cy="17" r="1.5"/><circle cx="16.5" cy="17" r="1.5"/>
            </svg>
          </div>
          <div class="brand-text">
            <div class="brand-name">FiloRent</div>
            <div class="brand-role">Temsilci Paneli</div>
          </div>
        </router-link>
        <button class="close-btn" @click="mobileOpen = false">✕</button>
      </div>

      <!-- Nav -->
      <nav class="sidebar-nav">
        <router-link to="/representative" class="nav-item" exact-active-class="nav-item--active" active-class="" :title="collapsed ? 'Rezervasyonlar' : ''" @click="mobileOpen = false">
          <span class="nav-icon">📋</span>
          <span class="nav-label">Rezervasyonlar</span>
        </router-link>
        <router-link to="/representative/araclar" class="nav-item" active-class="nav-item--active" :title="collapsed ? 'Araçlar' : ''" @click="mobileOpen = false">
          <span class="nav-icon">🚗</span>
          <span class="nav-label">Araçlar</span>
        </router-link>
        <router-link to="/representative/maintenance" class="nav-item" active-class="nav-item--active" @click="mobileOpen = false">
          <span class="nav-icon">🔧</span>
          <span class="nav-label">Bakım Kayıtları</span>
        </router-link>
        <router-link to="/representative/logs" class="nav-item" active-class="nav-item--active" :title="collapsed ? 'Teslimat Logları' : ''" @click="mobileOpen = false">
          <span class="nav-icon">📝</span>
          <span class="nav-label">Teslimat Logları</span>
        </router-link>

      </nav>

      <!-- Footer -->
      <div class="sidebar-footer">
        <template v-if="!collapsed">
          <div class="footer-user-row">
            <div class="user-avatar">{{ initials }}</div>
            <div class="user-info">
              <div class="footer-username">{{ auth.username }}</div>
              <span class="footer-badge">Temsilci</span>
            </div>
            <router-link to="/representative/profil" class="footer-icon-btn" title="Profil Ayarları" @click="mobileOpen = false">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
            </router-link>
          </div>
          <button class="sidebar-logout" @click="handleLogout">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"/></svg>
            Çıkış Yap
          </button>
        </template>
        <template v-else>
          <div class="footer-collapsed">
            <div class="user-avatar" :title="auth.username">{{ initials }}</div>
            <router-link to="/representative/profil" class="footer-icon-btn-sm" title="Profil Ayarları">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
            </router-link>
            <button class="footer-icon-btn-sm logout-sm" @click="handleLogout" title="Çıkış Yap">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"/></svg>
            </button>
          </div>
        </template>
      </div>

    </aside>

    <!-- Main -->
    <div class="main">
      <header class="topbar">
        <button class="hamburger" @click="handleHamburger" :title="collapsed ? 'Menüyü Aç' : 'Menüyü Kapat'">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="3" y1="6" x2="21" y2="6"/>
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
        <span class="topbar-title">{{ pageTitle }}</span>
      </header>
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const mobileOpen = ref(false)
const collapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true')

const initials = computed(() => (auth.username || '').substring(0, 2).toUpperCase())

const pageTitles = {
  '/representative': 'Rezervasyonlar',
  '/representative/araclar': 'Araçlar',
  '/representative/profil': 'Profil Ayarları',
  '/representative/logs': 'Teslimat Logları',
  '/representative/maintenance': 'Bakım Kayıtları',
}
const pageTitle = computed(() => pageTitles[route.path] || '')

function handleHamburger() {
  if (window.matchMedia('(max-width: 768px)').matches) {
    mobileOpen.value = true
  } else {
    collapsed.value = !collapsed.value
    localStorage.setItem('sidebarCollapsed', String(collapsed.value))
  }
}

async function handleLogout() {
  await axios.post('/api/logout/')
  auth.logout()
  router.push('/')
}
</script>

<style scoped>
.layout { display: flex; min-height: 100vh; background: #F8FAFC; }

/* ── Sidebar ── */
.sidebar {
  width: 260px;
  flex-shrink: 0;
  background: linear-gradient(180deg, #0c1320 0%, #0f1929 70%, #1a1200 100%);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: hidden;
  z-index: 20;
  transition: width 0.22s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar.collapsed { width: 64px; }

/* ── Brand ── */
.sidebar-brand {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 16px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  min-height: 64px;
  flex-shrink: 0;
}

.sidebar.collapsed .sidebar-brand {
  justify-content: center;
  padding: 20px 0 16px;
}

.brand-link { display: flex; align-items: center; gap: 11px; text-decoration: none; overflow: hidden; }

.brand-icon {
  width: 38px;
  height: 38px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(245,158,11,0.4);
  flex-shrink: 0;
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
  overflow: hidden;
  white-space: nowrap;
  opacity: 1;
  max-width: 160px;
  transition: opacity 0.15s ease, max-width 0.22s ease;
}

.sidebar.collapsed .brand-text { opacity: 0; max-width: 0; pointer-events: none; }

.brand-name { font-size: 14px; font-weight: 800; color: white; line-height: 1; }
.brand-role { font-size: 11px; color: rgba(255,255,255,0.35); font-weight: 500; }

.close-btn { display: none; background: none; border: none; color: rgba(255,255,255,0.4); font-size: 16px; cursor: pointer; padding: 4px; flex-shrink: 0; }
.close-btn:hover { color: white; }

/* ── Nav ── */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  padding: 12px 8px;
  gap: 2px;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 500;
  color: rgba(255,255,255,0.5);
  text-decoration: none;
  overflow: hidden;
  white-space: nowrap;
  transition: background 0.15s, color 0.15s, padding 0.22s;
}

.sidebar.collapsed .nav-item { justify-content: center; padding: 10px 0; }
.nav-item:hover { background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.85); }

.nav-item--active { background: rgba(245,158,11,0.12); color: #fcd34d; font-weight: 600; }
.nav-item--active::before {
  content: '';
  position: absolute;
  left: 0; top: 5px; bottom: 5px;
  width: 3px;
  background: #f59e0b;
  border-radius: 0 3px 3px 0;
}

.nav-icon { font-size: 16px; width: 20px; text-align: center; flex-shrink: 0; }

.nav-label {
  white-space: nowrap; overflow: hidden;
  opacity: 1; max-width: 180px;
  transition: opacity 0.12s ease, max-width 0.22s ease;
}

.sidebar.collapsed .nav-label { opacity: 0; max-width: 0; pointer-events: none; }

/* ── Footer ── */
.sidebar-footer { border-top: 1px solid rgba(255,255,255,0.06); flex-shrink: 0; }
.footer-user-row { display: flex; align-items: center; gap: 10px; padding: 14px 14px 8px; }

.user-avatar {
  width: 34px; height: 34px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 800; color: white; flex-shrink: 0;
}

.user-info { flex: 1; min-width: 0; overflow: hidden; }
.footer-username { font-size: 13px; color: rgba(255,255,255,0.8); font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.footer-badge { padding: 1px 7px; background: rgba(245,158,11,0.2); color: #fcd34d; border-radius: 50px; font-size: 10px; font-weight: 700; }

.footer-icon-btn {
  width: 30px; height: 30px; border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  color: rgba(255,255,255,0.35); transition: background 0.15s, color 0.15s;
  flex-shrink: 0; text-decoration: none;
}
.footer-icon-btn:hover { background: rgba(255,255,255,0.08); color: white; }

.sidebar-logout {
  display: flex; align-items: center; gap: 8px;
  width: calc(100% - 28px); margin: 0 14px 14px;
  padding: 9px 12px; border: none; border-radius: 8px;
  background: rgba(239,68,68,0.08); color: rgba(239,68,68,0.65);
  font-size: 12.5px; font-weight: 600; cursor: pointer;
  transition: background 0.15s, color 0.15s; text-align: left;
}
.sidebar-logout:hover { background: rgba(239,68,68,0.15); color: #f87171; }

.footer-collapsed {
  display: flex; flex-direction: column; align-items: center;
  gap: 6px; padding: 12px 0;
}

.footer-icon-btn-sm {
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: rgba(255,255,255,0.35); transition: background 0.15s, color 0.15s;
  text-decoration: none; border: none; background: none; cursor: pointer;
}
.footer-icon-btn-sm:hover { background: rgba(255,255,255,0.08); color: white; }
.logout-sm:hover { background: rgba(239,68,68,0.12); color: #f87171; }

/* ── Main ── */
.main { flex: 1; min-width: 0; display: flex; flex-direction: column; }

.topbar {
  display: flex; align-items: center;
  padding: 0 24px; height: 60px;
  background: white; border-bottom: 1px solid #e2e8f0;
  position: sticky; top: 0; z-index: 10;
  gap: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.hamburger {
  background: none; border: none; padding: 6px; border-radius: 7px;
  color: #64748b; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.15s, color 0.15s; flex-shrink: 0;
}
.hamburger:hover { background: #f1f5f9; color: #1e293b; }

.topbar-title { font-size: 15px; font-weight: 700; color: #0f172a; }

/* ── Mobile ── */
.overlay { display: none; }
@media (max-width: 768px) {
  .sidebar { position: fixed; top: 0; left: 0; height: 100vh; z-index: 101; width: 260px; transform: translateX(-100%); transition: transform 0.25s ease; }
  .sidebar.open { transform: translateX(0); }
  .sidebar.collapsed { width: 260px; }
  .close-btn { display: block; }
  .overlay { display: block; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100; backdrop-filter: blur(2px); }
  .sidebar .brand-text { opacity: 1 !important; max-width: 160px !important; pointer-events: auto !important; }
  .sidebar .nav-label { opacity: 1 !important; max-width: 180px !important; pointer-events: auto !important; }
  .sidebar .nav-item { justify-content: flex-start !important; padding: 10px 14px !important; }
}
</style>

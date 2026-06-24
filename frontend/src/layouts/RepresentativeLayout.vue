<template>
  <div class="layout">
    <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <div :class="['sidebar', { open: sidebarOpen }]">
      <div class="sidebar-header">
        <span class="sidebar-title">Menü</span>
        <button class="sidebar-close" @click="sidebarOpen = false">✕</button>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/representative" class="sidebar-item" exact-active-class="sidebar-item--active" active-class="" @click="sidebarOpen = false">Rezervasyonlar</router-link>
        <router-link to="/representative/araclar" class="sidebar-item" exact-active-class="sidebar-item--active" active-class="" @click="sidebarOpen = false">Araçlar</router-link>
      </nav>
    </div>

    <div class="topbar">
      <div class="brand-group">
        <button class="hamburger" @click="sidebarOpen = true">&#9776;</button>
        <router-link to="/representative" class="brand">Araç Kiralama</router-link>
      </div>
      <div class="right">
        <div class="user-menu" ref="menuRef">
          <span class="role-badge" @click="menuOpen = !menuOpen">Temsilci</span>
          <div v-if="menuOpen" class="dropdown">
            <router-link to="/representative/profil" class="dropdown-item" @click="menuOpen = false">Profil Ayarları</router-link>
            <button class="dropdown-item dropdown-logout" @click="handleLogout">Çıkış Yap</button>
          </div>
        </div>
      </div>
    </div>

    <router-view />
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

async function handleLogout() {
  await axios.post('http://127.0.0.1:8000/api/logout/')
  auth.logout()
  router.push('/')
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
  background: #f8f9fa;
  font-family: sans-serif;
}
.sidebar-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.3); z-index: 100;
}
.sidebar {
  position: fixed; top: 0; left: 0;
  height: 100vh; width: 260px;
  background: white; z-index: 101;
  box-shadow: 4px 0 16px rgba(0,0,0,0.12);
  transform: translateX(-100%);
  transition: transform 0.25s ease;
  display: flex; flex-direction: column;
}
.sidebar.open { transform: translateX(0); }
.sidebar-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 24px; border-bottom: 1px solid #e5e7eb;
}
.sidebar-title { font-size: 15px; font-weight: 700; color: #1e293b; }
.sidebar-close {
  background: none; border: none;
  font-size: 18px; color: #94a3b8; cursor: pointer; line-height: 1;
}
.sidebar-close:hover { color: #1e293b; }
.sidebar-nav { display: flex; flex-direction: column; padding: 12px; gap: 2px; }
.sidebar-item {
  display: flex; align-items: center;
  padding: 10px 12px; border-radius: 8px;
  font-size: 14px; font-weight: 500;
  color: #1e293b; text-decoration: none;
}
.sidebar-item:hover { background: #f1f5f9; }
.sidebar-item--active {
  background: #ede9fe; color: #6366f1; font-weight: 600;
}
.topbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 40px; background: white; border-bottom: 1px solid #e5e7eb;
}
.brand-group { display: flex; align-items: center; gap: 12px; }
.hamburger {
  background: none; border: none;
  font-size: 20px; color: #475569; cursor: pointer; padding: 0; line-height: 1;
}
.hamburger:hover { color: #1e293b; }
.brand { font-size: 18px; font-weight: 700; color: #1e293b; text-decoration: none; }
.right { display: flex; align-items: center; gap: 12px; }
.user-menu { position: relative; }
.role-badge {
  padding: 4px 12px; background: #fef3c7; color: #92400e;
  border-radius: 50px; font-size: 12px; font-weight: 700;
  cursor: pointer; user-select: none;
}
.role-badge:hover { background: #fde68a; }
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
</style>

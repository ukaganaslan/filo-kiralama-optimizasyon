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
        <router-link to="/operator/subeler" class="sidebar-item active" @click="sidebarOpen = false">Şubeler</router-link>
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
      <div class="section-header">
        <div class="header-left">
          <h2>Şube Yönetimi</h2>
          <span class="count-badge">{{ branches.length }} şube</span>
        </div>
        <button class="btn-add" @click="openAdd">+ Şube Ekle</button>
      </div>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Sube İsmi</th>
            <th>Sehir</th>
            <th>Araç Sayısı</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in branches" :key="b.id">
            <td class="id">{{ b.id }}</td>
            <td class="name">{{ b.title || '—' }}</td>
            <td class="city">{{ b.name }}</td>
            <td><span class="count">{{ b.vehicle_count }}</span></td>
            <td><button class="btn-edit" @click="openEdit(b)">✏️</button></td>
          </tr>
          <tr v-if="branches.length === 0">
            <td colspan="5" class="empty">Şube bulunamadı.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="addModal" class="modal-overlay" @click.self="addModal = false">
      <div class="modal">
        <h3>Yeni Şube Ekle</h3>
        <div class="field">
          <label>Şube İsmi</label>
          <input v-model="addForm.title" type="text" placeholder="Şube İsmi" />
        </div>
        <div class="field">
          <label>Şehir</label>
          <select v-model="addForm.name">
            <option value="">Seçin</option>
            <option v-for="sehir in sehirler" :key="sehir" :value="sehir">{{ sehir }}</option>
          </select>
        </div>
        <p v-if="addError" class="error">{{ addError }}</p>
        <div class="modal-actions">
          <button class="btn-cancel-modal" @click="addModal = false">Vazgeç</button>
          <button class="btn-save" @click="saveAdd">Kaydet</button>
        </div>
      </div>
    </div>

    <div v-if="editModal" class="modal-overlay" @click.self="editModal = false">
      <div class="modal">
        <h3>Şube Düzenle</h3>
        <div class="field">
          <label>Şube İsmi</label>
          <input v-model="editForm.title" type="text" placeholder="İstanbul Merkez" />
        </div>
        <div class="field">
          <label>Şehir</label>
          <select v-model="editForm.name">
            <option value="">Seçin</option>
            <option v-for="sehir in sehirler" :key="sehir" :value="sehir">{{ sehir }}</option>
          </select>
        </div>
        <p v-if="editError" class="error">{{ editError }}</p>
        <div class="modal-actions">
          <button class="btn-cancel-modal" @click="editModal = false">Vazgeç</button>
          <button class="btn-save" @click="saveEdit">Kaydet</button>
        </div>
      </div>
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
const sehirler = [
  'Adana','Adıyaman','Afyonkarahisar','Ağrı','Amasya','Ankara','Antalya','Artvin',
  'Aydın','Balıkesir','Bilecik','Bingöl','Bitlis','Bolu','Burdur','Bursa',
  'Çanakkale','Çankırı','Çorum','Denizli','Diyarbakır','Edirne','Elazığ',
  'Erzincan','Erzurum','Eskişehir','Gaziantep','Giresun','Gümüşhane','Hakkâri',
  'Hatay','Isparta','Mersin','İstanbul','İzmir','Kars','Kastamonu','Kayseri',
  'Kırklareli','Kırşehir','Kocaeli','Konya','Kütahya','Malatya','Manisa',
  'Kahramanmaraş','Mardin','Muğla','Muş','Nevşehir','Niğde','Ordu','Rize',
  'Sakarya','Samsun','Siirt','Sinop','Sivas','Tekirdağ','Tokat','Trabzon',
  'Tunceli','Şanlıurfa','Uşak','Van','Yozgat','Zonguldak','Aksaray','Bayburt',
  'Karaman','Kırıkkale','Batman','Şırnak','Bartın','Ardahan','Iğdır','Yalova',
  'Karabük','Kilis','Osmaniye','Düzce',
]

const branches = ref([])
const addModal = ref(false)
const addForm = ref({ name: '', title: '' })
const addError = ref('')
const editModal = ref(false)
const editForm = ref({ id: null, name: '', title: '' })
const editError = ref('')

function openAdd() {
  addForm.value = { name: '', title: '' }
  addError.value = ''
  addModal.value = true
}

async function saveAdd() {
  if (!addForm.value.name || !addForm.value.title) {
    addError.value = 'Tüm alanları doldurun.'
    return
  }
  try {
    await axios.post('http://127.0.0.1:8000/api/branches/', addForm.value)
    addModal.value = false
    await loadBranches()
  } catch {
    addError.value = 'Kaydetme başarısız.'
  }
}

async function loadBranches() {
  const [branchRes, vehicleRes] = await Promise.all([
    axios.get('http://127.0.0.1:8000/api/branches/'),
    axios.get('http://127.0.0.1:8000/api/vehicles/'),
  ])
  const vehicles = vehicleRes.data
  branches.value = branchRes.data.map(b => ({
    ...b,
    vehicle_count: vehicles.filter(v => v.branch === b.id).length,
  }))
}

onMounted(loadBranches)

function openEdit(branch) {
  editForm.value = { id: branch.id, name: branch.name, title: branch.title }
  editError.value = ''
  editModal.value = true
}

async function saveEdit() {
  try {
    await axios.patch(`http://127.0.0.1:8000/api/branches/${editForm.value.id}/`, {
      name: editForm.value.name,
      title: editForm.value.title,
    })
    editModal.value = false
    await loadBranches()
  } catch {
    editError.value = 'Kaydetme başarısız.'
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
.sidebar-item.active { background: #ede9fe; color: #6366f1; font-weight: 600; }
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
  padding: 4px 12px; background: #ede9fe; color: #6366f1;
  border-radius: 50px; font-size: 12px; font-weight: 700;
  cursor: pointer; user-select: none;
}
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
.btn-logout {
  padding: 6px 14px; background: #dc2626; color: white;
  border: none; border-radius: 6px; cursor: pointer; font-size: 13px;
}
.content { max-width: 800px; margin: 0 auto; padding: 40px; }
.section-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;
}
.header-left { display: flex; align-items: center; gap: 12px; }
.btn-add {
  padding: 8px 18px; background: #6366f1; color: white;
  border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer;
}
.btn-add:hover { background: #4f46e5; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0; }
.count-badge {
  padding: 3px 10px; background: #f1f5f9; color: #64748b;
  border-radius: 50px; font-size: 12px; font-weight: 600;
}
table {
  width: 100%; border-collapse: collapse;
  background: white; border-radius: 8px;
  overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th {
  background: #f1f5f9; font-weight: 600; color: #475569;
  font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em;
}
td { border-top: 1px solid #f1f5f9; color: #374151; }
.id { color: #94a3b8; font-size: 13px; }
.name { font-weight: 600; color: #1e293b; }
.city { color: #35455e; font-family: monospace; font-size: 13px; }
.count {
  display: inline-block; padding: 2px 10px;
  background: #ede9fe; color: #35455e;
  border-radius: 50px; font-size: 12px; font-weight: 600;
}
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
td:nth-child(4), th:nth-child(4) { text-align: center; }
.btn-edit {
  padding: 4px 12px; background: white; color: #6366f1;
  border: 1px solid #6366f1; border-radius: 50px;
  font-size: 12px; cursor: pointer;
}
.btn-edit:hover { background: #ede9fe; }
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4); z-index: 200;
  display: flex; align-items: center; justify-content: center;
}
.modal {
  background: white; border-radius: 12px;
  padding: 32px; width: 400px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
  display: flex; flex-direction: column; gap: 16px;
}
.modal h3 { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; }
.field input, .field select {
  padding: 10px 14px; border: 1px solid #e2e8f0;
  border-radius: 8px; font-size: 14px; outline: none;
}
.field input:focus, .field select:focus { border-color: #6366f1; }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 4px; }
.btn-cancel-modal {
  padding: 8px 16px; background: white; color: #64748b;
  border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-size: 14px;
}
.btn-save {
  padding: 8px 20px; background: #6366f1; color: white;
  border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600;
}
.btn-save:hover { background: #4f46e5; }
.error { color: #dc2626; font-size: 13px; margin: 0; }
</style>

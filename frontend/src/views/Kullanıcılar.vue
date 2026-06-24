<template>
  <div class="content">
    <div class="section-header">
      <div class="header-left">
        <h2>Kullanıcılar</h2>
        <span class="count-badge">{{ users.length }} kullanıcı</span>
      </div>
      <button class="btn-add" @click="openAdd">+ Kullanıcı Ekle</button>
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
          <td class="actions">
            <button class="btn-edit" @click="openEdit(u)">✏️</button>
            <button class="btn-toggle" @click="toggleActive(u)">{{ u.is_active ? 'Pasife Al' : 'Aktife Al' }}</button>
          </td>
        </tr>
        <tr v-if="filtered.length === 0">
          <td colspan="8" class="empty">Kullanıcı bulunamadı.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="addModal" class="modal-overlay" @click.self="addModal = false">
    <div class="modal">
      <h3>Yeni Kullanıcı Ekle</h3>
      <div class="field"><label>Kullanıcı Adı</label><input v-model="addForm.username" type="text" /></div>
      <div class="field"><label>Şifre</label><input v-model="addForm.password" type="password" /></div>
      <div class="field"><label>Ad Soyad</label><input v-model="addForm.full_name" type="text" /></div>
      <div class="field"><label>E-posta</label><input v-model="addForm.email" type="email" /></div>
      <div class="field"><label>Telefon</label><input v-model="addForm.phone" type="text" /></div>
      <p v-if="formError" class="error">{{ formError }}</p>
      <div class="modal-actions">
        <button class="btn-cancel-modal" @click="addModal = false">Vazgeç</button>
        <button class="btn-save" @click="saveAdd">Kaydet</button>
      </div>
    </div>
  </div>

  <div v-if="editModal" class="modal-overlay" @click.self="editModal = false">
    <div class="modal">
      <h3>Kullanıcıyı Düzenle</h3>
      <div class="field"><label>Kullanıcı Adı</label><input v-model="editForm.username" type="text" /></div>
      <div class="field"><label>Ad Soyad</label><input v-model="editForm.full_name" type="text" /></div>
      <div class="field"><label>E-posta</label><input v-model="editForm.email" type="email" /></div>
      <div class="field"><label>Telefon</label><input v-model="editForm.phone" type="text" /></div>
      <div class="field"><label>Yeni Şifre</label><input v-model="editForm.password" type="password" placeholder="Boş bırakırsan değişmez" /></div>
      <p v-if="formError" class="error">{{ formError }}</p>
      <div class="modal-actions">
        <button class="btn-cancel-modal" @click="editModal = false">Vazgeç</button>
        <button class="btn-save" @click="saveEdit">Kaydet</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const users = ref([])
const search = ref('')
const addModal = ref(false)
const editModal = ref(false)
const formError = ref('')
const addForm = ref({ username: '', password: '', full_name: '', email: '', phone: '' })
const editForm = ref({ id: null, username: '', full_name: '', email: '', phone: '', password: '' })

async function loadUsers() {
  const res = await axios.get('http://127.0.0.1:8000/api/users/')
  users.value = res.data
}

onMounted(loadUsers)

function openAdd() {
  addForm.value = { username: '', password: '', full_name: '', email: '', phone: '' }
  formError.value = ''
  addModal.value = true
}

function openEdit(u) {
  editForm.value = { id: u.id, username: u.username, full_name: u.full_name, email: u.email, phone: u.phone, password: '' }
  formError.value = ''
  editModal.value = true
}

async function saveAdd() {
  formError.value = ''
  try {
    await axios.post('http://127.0.0.1:8000/api/users/create/', addForm.value)
    addModal.value = false
    await loadUsers()
  } catch (e) {
    formError.value = e.response?.data?.error || 'Kaydetme başarısız.'
  }
}

async function saveEdit() {
  formError.value = ''
  try {
    await axios.patch(`http://127.0.0.1:8000/api/users/${editForm.value.id}/update/`, {
      username: editForm.value.username,
      full_name: editForm.value.full_name,
      email: editForm.value.email,
      phone: editForm.value.phone,
      password: editForm.value.password || undefined,
    })
    editModal.value = false
    await loadUsers()
  } catch (e) {
    formError.value = e.response?.data?.error || 'Kaydetme başarısız.'
  }
}

const filtered = computed(() => {
  const q = search.value.toLowerCase()
  if (!q) return users.value
  return users.value.filter(u =>
    u.username.toLowerCase().includes(q) ||
    u.full_name.toLowerCase().includes(q) ||
    u.phone.includes(q)
  )
})

async function toggleActive(u) {
  await axios.post(`http://127.0.0.1:8000/api/users/${u.id}/toggle-active/`)
  u.is_active = !u.is_active
}
</script>

<style scoped>
.content { max-width: 1100px; margin: 0 auto; padding: 40px; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.header-left { display: flex; align-items: center; gap: 12px; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0; }
.count-badge { padding: 3px 10px; background: #f1f5f9; color: #64748b; border-radius: 50px; font-size: 12px; font-weight: 600; }
.btn-add { padding: 8px 18px; background: #6366f1; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-add:hover { background: #4f46e5; }
.search-bar { margin-bottom: 16px; }
.search-input { width: 320px; padding: 9px 14px; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 14px; color: #1e293b; outline: none; }
.search-input:focus { border-color: #6366f1; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
td { border-top: 1px solid #f1f5f9; color: #374151; }
.username { font-weight: 600; color: #1e293b; }
.rez-count { display: inline-block; padding: 2px 10px; background: #ede9fe; color: #35455e; border-radius: 50px; font-size: 12px; font-weight: 600; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
td:nth-child(6), th:nth-child(6) { text-align: center; }
.actions { display: flex; gap: 8px; }
.btn-edit { padding: 4px 12px; background: white; color: #6366f1; border: 1px solid #6366f1; border-radius: 50px; font-size: 12px; cursor: pointer; }
.btn-edit:hover { background: #ede9fe; }
.btn-toggle { padding: 4px 12px; background: white; color: #64748b; border: 1px solid #cbd5e1; border-radius: 50px; font-size: 12px; cursor: pointer; }
.btn-toggle:hover { background: #f1f5f9; }
.badge-active { padding: 3px 10px; background: #d1fae5; color: #065f46; border-radius: 50px; font-size: 12px; font-weight: 600; }
.badge-passive { padding: 3px 10px; background: #fee2e2; color: #991b1b; border-radius: 50px; font-size: 12px; font-weight: 600; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 200; display: flex; align-items: center; justify-content: center; }
.modal { background: white; border-radius: 12px; padding: 32px; width: 420px; box-shadow: 0 8px 32px rgba(0,0,0,0.12); display: flex; flex-direction: column; gap: 14px; }
.modal h3 { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; }
.field input { padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; }
.field input:focus { border-color: #6366f1; }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 4px; }
.btn-cancel-modal { padding: 8px 16px; background: white; color: #64748b; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-size: 14px; }
.btn-save { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-save:hover { background: #4f46e5; }
.error { color: #dc2626; font-size: 13px; margin: 0; }
</style>

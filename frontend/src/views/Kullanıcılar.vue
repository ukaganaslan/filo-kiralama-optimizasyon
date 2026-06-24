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
          <th>Rol</th>
          <th>Kayıt Tarihi</th>
          <th>Rez. Sayısı</th>
          <th>Durum</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in filtered" :key="u.id">
          <td class="username">{{ u.username }}</td>
          <td>{{ u.full_name || '—' }}</td>
          <td>{{ u.email || '—' }}</td>
          <td>{{ u.phone || '—' }}</td>
          <td>
            <span :class="'role-badge role-' + u.role">{{ roleLabel(u.role) }}</span>
            <span v-if="u.role === 'representative' && branchName(u.branch_id)" class="branch-hint">{{ branchName(u.branch_id) }}</span>
          </td>
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
          <td colspan="9" class="empty">Kullanıcı bulunamadı.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- Ekleme Modalı -->
  <div v-if="addModal" class="modal-overlay" @click.self="addModal = false">
    <div class="modal">
      <h3>Yeni Kullanıcı Ekle</h3>
      <div class="field"><label>Kullanıcı Adı</label><input v-model="addForm.username" type="text" /></div>
      <div class="field"><label>Şifre</label><input v-model="addForm.password" type="password" /></div>
      <div class="field"><label>Ad Soyad</label><input v-model="addForm.full_name" type="text" /></div>
      <div class="field"><label>E-posta</label><input v-model="addForm.email" type="email" /></div>
      <div class="field"><label>Telefon</label><input v-model="addForm.phone" type="text" /></div>
      <div class="field">
        <label>Rol</label>
        <select v-model="addForm.role">
          <option value="customer">Müşteri</option>
          <option value="representative">Temsilci</option>
          <option value="admin">Admin</option>
        </select>
      </div>
      <div v-if="addForm.role === 'representative'" class="field">
        <label>Şube</label>
        <select v-model="addForm.branch">
          <option value="">Seçin</option>
          <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
        </select>
      </div>
      <p v-if="formError" class="error">{{ formError }}</p>
      <div class="modal-actions">
        <button class="btn-cancel-modal" @click="addModal = false">Vazgeç</button>
        <button class="btn-save" @click="saveAdd">Kaydet</button>
      </div>
    </div>
  </div>

  <!-- Düzenleme Modalı -->
  <div v-if="editModal" class="modal-overlay" @click.self="editModal = false">
    <div class="modal">
      <h3>Kullanıcıyı Düzenle</h3>
      <div class="field"><label>Kullanıcı Adı</label><input v-model="editForm.username" type="text" /></div>
      <div class="field"><label>Ad Soyad</label><input v-model="editForm.full_name" type="text" /></div>
      <div class="field"><label>E-posta</label><input v-model="editForm.email" type="email" /></div>
      <div class="field"><label>Telefon</label><input v-model="editForm.phone" type="text" /></div>
      <div class="field"><label>Yeni Şifre</label><input v-model="editForm.password" type="password" placeholder="Boş bırakırsan değişmez" /></div>
      <div class="field">
        <label>Rol</label>
        <select v-model="editForm.role">
          <option value="customer">Müşteri</option>
          <option value="representative">Temsilci</option>
          <option value="admin">Admin</option>
        </select>
      </div>
      <div v-if="editForm.role === 'representative'" class="field">
        <label>Şube</label>
        <select v-model="editForm.branch_id">
          <option value="">Seçin</option>
          <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
        </select>
      </div>
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
const branches = ref([])
const search = ref('')
const addModal = ref(false)
const editModal = ref(false)
const formError = ref('')

const addForm = ref({ username: '', password: '', full_name: '', email: '', phone: '', role: 'customer', branch: '' })
const editForm = ref({ id: null, username: '', full_name: '', email: '', phone: '', password: '', role: 'customer', branch_id: '' })

async function loadUsers() {
  const res = await axios.get('http://127.0.0.1:8000/api/users/')
  users.value = res.data
}

onMounted(async () => {
  const [usersRes, branchRes] = await Promise.all([
    axios.get('http://127.0.0.1:8000/api/users/'),
    axios.get('http://127.0.0.1:8000/api/branches/'),
  ])
  users.value = usersRes.data
  branches.value = branchRes.data
})

function openAdd() {
  addForm.value = { username: '', password: '', full_name: '', email: '', phone: '', role: 'customer', branch: '' }
  formError.value = ''
  addModal.value = true
}

function openEdit(u) {
  editForm.value = { id: u.id, username: u.username, full_name: u.full_name, email: u.email, phone: u.phone, password: '', role: u.role, branch_id: u.branch_id || '' }
  formError.value = ''
  editModal.value = true
}

async function saveAdd() {
  formError.value = ''
  try {
    await axios.post('http://127.0.0.1:8000/api/users/create/', {
      ...addForm.value,
      branch: addForm.value.role === 'representative' ? addForm.value.branch : undefined,
    })
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
      role: editForm.value.role,
      branch_id: editForm.value.role === 'representative' ? editForm.value.branch_id : null,
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
    (u.full_name || '').toLowerCase().includes(q) ||
    (u.phone || '').includes(q)
  )
})

async function toggleActive(u) {
  await axios.post(`http://127.0.0.1:8000/api/users/${u.id}/toggle-active/`)
  u.is_active = !u.is_active
}

function roleLabel(role) {
  return { customer: 'Müşteri', representative: 'Temsilci', admin: 'Admin' }[role] || role
}

function branchName(id) {
  if (!id) return ''
  const b = branches.value.find(b => b.id === id)
  return b ? b.name : ''
}
</script>

<style scoped>
.content { padding: 32px 40px; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.header-left { display: flex; align-items: center; gap: 12px; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0; }
.count-badge { padding: 3px 10px; background: #f1f5f9; color: #64748b; border-radius: 50px; font-size: 12px; font-weight: 600; }
.btn-add { padding: 8px 18px; background: #6366f1; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-add:hover { background: #4f46e5; }
.search-bar { margin-bottom: 16px; }
.search-input { width: 320px; padding: 9px 14px; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 14px; color: #1e293b; outline: none; }
.search-input:focus { border-color: #6366f1; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 14px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
td { border-top: 1px solid #f1f5f9; color: #374151; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
td:nth-child(1), th:nth-child(1), td:nth-child(2), th:nth-child(2), td:nth-child(3), th:nth-child(3), td:nth-child(4), th:nth-child(4), td:nth-child(5), th:nth-child(5), td:nth-child(6), th:nth-child(6), td:nth-child(7), th:nth-child(7) { text-align: center; }
.username { font-weight: 600; color: #1e293b; }
.rez-count { display: inline-block; padding: 2px 10px; background: #ede9fe; color: #35455e; border-radius: 50px; font-size: 12px; font-weight: 600; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
.actions { display: flex; gap: 8px; align-items: center; }
.btn-edit { padding: 4px 12px; background: white; color: #6366f1; border: 1px solid #6366f1; border-radius: 50px; font-size: 12px; cursor: pointer; }
.btn-edit:hover { background: #ede9fe; }
.btn-toggle { padding: 4px 12px; background: white; color: #64748b; border: 1px solid #cbd5e1; border-radius: 50px; font-size: 12px; cursor: pointer; white-space: nowrap; }
.btn-toggle:hover { background: #f1f5f9; }
.badge-active { padding: 3px 10px; background: #d1fae5; color: #065f46; border-radius: 50px; font-size: 12px; font-weight: 600; }
.badge-passive { padding: 3px 10px; background: #fee2e2; color: #991b1b; border-radius: 50px; font-size: 12px; font-weight: 600; }
.role-badge { padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: 600; }
.role-customer { background: #f1f5f9; color: #475569; }
.role-representative { background: #fef3c7; color: #92400e; }
.role-admin { background: #ede9fe; color: #5b21b6; }
.branch-hint { display: block; font-size: 11px; color: #94a3b8; margin-top: 2px; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 200; display: flex; align-items: center; justify-content: center; }
.modal { background: white; border-radius: 14px; padding: 32px; width: 420px; box-shadow: 0 8px 32px rgba(0,0,0,0.12); display: flex; flex-direction: column; gap: 14px; }
.modal h3 { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; }
.field input, .field select { padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; background: white; color: #1e293b; }
.field input:focus, .field select:focus { border-color: #6366f1; }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 4px; }
.btn-cancel-modal { padding: 8px 16px; background: white; color: #64748b; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-size: 14px; }
.btn-save { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-save:hover { background: #4f46e5; }
.error { color: #dc2626; font-size: 13px; margin: 0; }
</style>

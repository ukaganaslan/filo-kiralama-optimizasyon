<template>
  <div class="content">
    <div class="section-header">
      <div class="header-left">
        <h2>Araç Yönetimi</h2>
        <span class="count-badge">{{ vehicles.length }} araç</span>
      </div>
      <button class="btn-add" @click="openAdd">+ Araç Ekle</button>
    </div>

    <table>
      <thead>
        <tr>
          <th>Araç ID</th>
          <th>Sasi Kodu</th>
          <th>Marka</th>
          <th>Model</th>
          <th>Plaka</th>
          <th>Grup</th>
          <th>Şube</th>
          <th>Durum</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="v in vehicles" :key="v.id">
          <td class="vehicle-id">{{ v.vehicle_id }}</td>
          <td>{{ v.sasi || '—' }}</td>
          <td>{{ v.brand || '—' }}</td>
          <td>{{ v.model || '—' }}</td>
          <td>{{ v.plate || '—' }}</td>
          <td><span :class="'badge-group badge-' + v.group">{{ groupLabel(v.group) }}</span></td>
          <td>{{ v.branch_name || '—' }}</td>
          <td><span :class="'badge-status badge-' + v.status">{{ statusLabel(v.status) }}</span></td>
          <td class="actions">
            <button class="btn-edit" @click="openEdit(v)">✏️</button>
            <button class="btn-delete" @click="confirmDelete(v)">🗑️</button>
          </td>
        </tr>
        <tr v-if="vehicles.length === 0">
          <td colspan="9" class="empty">Araç bulunamadı.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="formModal" class="modal-overlay" @click.self="formModal = false">
    <div class="modal">
      <h3>{{ editingId ? 'Araç Düzenle' : 'Yeni Araç Ekle' }}</h3>
      <div class="field">
        <label>Marka</label>
        <input v-model="form.brand" type="text" placeholder="Araç Markası" />
      </div>
      <div class="field">
        <label>Model</label>
        <input v-model="form.model" type="text" placeholder="Araç Modeli" />
      </div>
      <div class="field">
        <label>Plaka</label>
        <input v-model="form.plate" type="text" placeholder="Plaka" />
      </div>
      <div class="field">
        <label>Sasi Kodu</label>
        <input v-model="form.sasi" type="text" placeholder="Sasi Kodu" />
      </div>
      <div class="field">
        <label>Grup</label>
        <select v-model="form.group">
          <option value="">Seçin</option>
          <option value="economy">Ekonomi</option>
          <option value="mid">Orta Sınıf</option>
          <option value="suv">SUV</option>
        </select>
      </div>
      <div class="field">
        <label>Şube</label>
        <select v-model="form.branch">
          <option value="">Seçin</option>
          <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.title || b.name }}</option>
        </select>
      </div>
      <div class="field">
        <label>Durum</label>
        <select v-model="form.status">
          <option value="available">Müsait</option>
          <option value="maintenance">Bakımda</option>
          <option value="service">Serviste</option>
          <option value="inactive">Pasif</option>
        </select>
      </div>
      <p v-if="formError" class="error">{{ formError }}</p>
      <div class="modal-actions">
        <button class="btn-cancel-modal" @click="formModal = false">Vazgeç</button>
        <button class="btn-save" @click="saveForm">Kaydet</button>
      </div>
    </div>
  </div>

  <div v-if="deleteModal" class="modal-overlay" @click.self="deleteModal = false">
    <div class="modal modal-sm">
      <h3>Aracı Sil</h3>
      <p class="confirm-text"><strong>{{ deletingVehicle?.vehicle_id }}</strong> aracını silmek istediğinize emin misiniz?</p>
      <div class="modal-actions">
        <button class="btn-cancel-modal" @click="deleteModal = false">Vazgeç</button>
        <button class="btn-delete-confirm" @click="doDelete">Sil</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const vehicles = ref([])
const branches = ref([])
const formModal = ref(false)
const editingId = ref(null)
const form = ref({ brand: '', model: '', plate: '', sasi: '', group: '', branch: '', status: 'available' })
const formError = ref('')
const deleteModal = ref(false)
const deletingVehicle = ref(null)

async function loadData() {
  const [vRes, bRes] = await Promise.all([
    axios.get('http://127.0.0.1:8000/api/vehicles/'),
    axios.get('http://127.0.0.1:8000/api/branches/'),
  ])
  vehicles.value = vRes.data.sort((a, b) => {
    if (a.branch !== b.branch) return a.branch - b.branch
    const grupSira = { economy: 1, mid: 2, suv: 3 }
    return grupSira[a.group] - grupSira[b.group]
  })
  branches.value = bRes.data
}

onMounted(loadData)

function groupLabel(g) {
  return { economy: 'Ekonomi', mid: 'Orta Sınıf', suv: 'SUV' }[g] || g
}

function statusLabel(s) {
  return { available: 'Müsait', maintenance: 'Bakımda', service: 'Serviste', inactive: 'Pasif' }[s] || s
}

function openAdd() {
  editingId.value = null
  form.value = { brand: '', model: '', plate: '', sasi: '', group: '', branch: '', status: 'available' }
  formError.value = ''
  formModal.value = true
}

function openEdit(v) {
  editingId.value = v.id
  form.value = { brand: v.brand || '', model: v.model || '', plate: v.plate || '', sasi: v.sasi || '', group: v.group, branch: v.branch, status: v.status }
  formError.value = ''
  formModal.value = true
}

async function saveForm() {
  if (!form.value.group || !form.value.branch) {
    formError.value = 'Tüm alanları doldurun.'
    return
  }
  try {
    if (editingId.value) {
      await axios.patch(`http://127.0.0.1:8000/api/vehicles/${editingId.value}/`, form.value)
    } else {
      await axios.post('http://127.0.0.1:8000/api/vehicles/', form.value)
    }
    formModal.value = false
    await loadData()
  } catch (e) {
    const data = e.response?.data
    if (data && typeof data === 'object') {
      const messages = Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join(' | ')
      formError.value = messages
    } else {
      formError.value = 'Kaydetme başarısız.'
    }
  }
}

function confirmDelete(v) {
  deletingVehicle.value = v
  deleteModal.value = true
}

async function doDelete() {
  try {
    await axios.delete(`http://127.0.0.1:8000/api/vehicles/${deletingVehicle.value.id}/`)
    deleteModal.value = false
    await loadData()
  } catch {
    deleteModal.value = false
  }
}
</script>

<style scoped>
.content { max-width: 1100px; margin: 0 auto; padding: 40px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-left { display: flex; align-items: center; gap: 12px; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0; }
.count-badge { padding: 3px 10px; background: #f1f5f9; color: #64748b; border-radius: 50px; font-size: 12px; font-weight: 600; }
.btn-add { padding: 8px 18px; background: #6366f1; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-add:hover { background: #4f46e5; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
td { border-top: 1px solid #f1f5f9; color: #374151; }
.vehicle-id { font-weight: 700; color: #1e293b; font-family: monospace; }
.actions { display: flex; gap: 8px; }
.badge-group, .badge-status { display: inline-block; padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: 600; }
.badge-economy { background: #dbeafe; color: #1d4ed8; }
.badge-mid { background: #fef3c7; color: #92400e; }
.badge-suv { background: #f3e8ff; color: #6b21a8; }
.badge-available { background: #d1fae5; color: #065f46; }
.badge-maintenance { background: #fef3c7; color: #92400e; }
.badge-service { background: #fee2e2; color: #991b1b; }
.badge-inactive { background: #f1f5f9; color: #64748b; }
.btn-edit { padding: 4px 12px; background: white; color: #6366f1; border: 1px solid #6366f1; border-radius: 50px; font-size: 12px; cursor: pointer; }
.btn-edit:hover { background: #ede9fe; }
.btn-delete { padding: 4px 12px; background: white; color: #dc2626; border: 1px solid #dc2626; border-radius: 50px; font-size: 12px; cursor: pointer; }
.btn-delete:hover { background: #fee2e2; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 200; display: flex; align-items: center; justify-content: center; }
.modal { background: white; border-radius: 12px; padding: 32px; width: 420px; box-shadow: 0 8px 32px rgba(0,0,0,0.12); display: flex; flex-direction: column; gap: 16px; }
.modal-sm { width: 340px; }
.modal h3 { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; }
.field input, .field select { padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; background: white; color: #1e293b; color-scheme: light; }
.field input:focus, .field select:focus { border-color: #6366f1; }
.field input:disabled { background: #f8f9fa; color: #94a3b8; }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 4px; }
.btn-cancel-modal { padding: 8px 16px; background: white; color: #64748b; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-size: 14px; }
.btn-save { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-save:hover { background: #4f46e5; }
.btn-delete-confirm { padding: 8px 20px; background: #dc2626; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-delete-confirm:hover { background: #b91c1c; }
.confirm-text { color: #374151; font-size: 14px; margin: 0; }
.error { color: #dc2626; font-size: 13px; margin: 0; }
</style>

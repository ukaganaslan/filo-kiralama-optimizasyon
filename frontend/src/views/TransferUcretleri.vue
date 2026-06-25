<template>
  <div class="content">
    <div class="section-header">
      <div class="header-left">
        <h2>Şube Arası Transfer Ücretleri</h2>
        <span class="count-badge">{{ costs.length }} kayıt</span>
      </div>
      <button class="btn-add" @click="openAdd">+ Ekle</button>
    </div>

    <table>
      <thead>
        <tr>
          <th>Çıkış Şubesi</th>
          <th>Varış Şubesi</th>
          <th>Ücret (₺)</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="c in costs" :key="c.id">
          <td>{{ c.from_branch_name }}</td>
          <td>{{ c.to_branch_name }}</td>
          <td class="cost-cell">{{ c.cost }} ₺</td>
          <td class="actions">
            <button class="btn-edit" @click="openEdit(c)">✏️</button>
            <button class="btn-delete" @click="confirmDelete(c)">🗑️</button>
          </td>
        </tr>
        <tr v-if="costs.length === 0">
          <td colspan="4" class="empty">Henüz transfer ücreti tanımlanmadı.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="formModal" class="modal-overlay" @click.self="formModal = false">
    <div class="modal">
      <h3>{{ editingId ? 'Ücreti Düzenle' : 'Transfer Ücreti Ekle' }}</h3>
      <div class="field">
        <label>Çıkış Şubesi</label>
        <select v-model="form.from_branch">
          <option value="">Seçin</option>
          <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.title || b.name }}</option>
        </select>
      </div>
      <div class="field">
        <label>Varış Şubesi</label>
        <select v-model="form.to_branch">
          <option value="">Seçin</option>
          <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.title || b.name }}</option>
        </select>
      </div>
      <div class="field">
        <label>Ücret (₺)</label>
        <input v-model="form.cost" type="number" min="0" step="0.01" placeholder="0.00" />
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
      <h3>Transfer Ücreti Sil</h3>
      <p class="confirm-text">
        <strong>{{ deletingCost?.from_branch_name }} → {{ deletingCost?.to_branch_name }}</strong>
        kaydını silmek istediğinize emin misiniz?
      </p>
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

const costs = ref([])
const branches = ref([])
const formModal = ref(false)
const editingId = ref(null)
const form = ref({ from_branch: '', to_branch: '', cost: '' })
const formError = ref('')
const deleteModal = ref(false)
const deletingCost = ref(null)

async function loadData() {
  const [cRes, bRes] = await Promise.all([
    axios.get('/api/transfer-costs/'),
    axios.get('/api/branches/'),
  ])
  costs.value = cRes.data
  branches.value = bRes.data
}

onMounted(loadData)

function openAdd() {
  editingId.value = null
  form.value = { from_branch: '', to_branch: '', cost: '' }
  formError.value = ''
  formModal.value = true
}

function openEdit(c) {
  editingId.value = c.id
  form.value = { from_branch: c.from_branch, to_branch: c.to_branch, cost: c.cost }
  formError.value = ''
  formModal.value = true
}

async function saveForm() {
  formError.value = ''
  if (!form.value.from_branch || !form.value.to_branch || form.value.cost === '') {
    formError.value = 'Tüm alanları doldurun.'
    return
  }
  if (form.value.from_branch === form.value.to_branch) {
    formError.value = 'Çıkış ve varış şubesi aynı olamaz.'
    return
  }
  try {
    if (editingId.value) {
      await axios.patch(`/api/transfer-costs/${editingId.value}/`, form.value)
    } else {
      await axios.post('/api/transfer-costs/', form.value)
    }
    formModal.value = false
    await loadData()
  } catch (e) {
    const data = e.response?.data
    if (data && typeof data === 'object') {
      formError.value = Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join(' | ')
    } else {
      formError.value = 'Kaydetme başarısız.'
    }
  }
}

function confirmDelete(c) {
  deletingCost.value = c
  deleteModal.value = true
}

async function doDelete() {
  try {
    await axios.delete(`/api/transfer-costs/${deletingCost.value.id}/`)
    deleteModal.value = false
    await loadData()
  } catch {
    deleteModal.value = false
  }
}
</script>

<style scoped>
.content { padding: 32px 40px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-left { display: flex; align-items: center; gap: 12px; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0; }
.count-badge { padding: 3px 10px; background: #f1f5f9; color: #64748b; border-radius: 50px; font-size: 12px; font-weight: 600; }
.btn-add { padding: 8px 18px; background: #6366f1; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-add:hover { background: #4f46e5; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 14px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
tr:not(:last-child) td { border-bottom: 1px solid #f1f5f9; }
.cost-cell { font-weight: 700; color: #6366f1; }
.actions { display: flex; flex-direction: column; gap: 6px; align-items: flex-start; }
.btn-edit { padding: 6px 18px; background: white; color: #6366f1; border: 2px solid #6366f1; border-radius: 50px; font-size: 16px; cursor: pointer; }
.btn-edit:hover { background: #ede9fe; }
.btn-delete { padding: 6px 18px; background: white; color: #dc2626; border: 2px solid #dc2626; border-radius: 50px; font-size: 16px; cursor: pointer; }
.btn-delete:hover { background: #fee2e2; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: white; border-radius: 14px; padding: 28px; width: 420px; box-shadow: 0 8px 32px rgba(0,0,0,0.15); }
.modal-sm { width: 340px; }
h3 { font-size: 17px; font-weight: 700; color: #1e293b; margin: 0 0 20px; }
.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.field label { font-size: 12px; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; }
.field select, .field input { border: 1px solid #e2e8f0; border-radius: 8px; padding: 9px 12px; font-size: 14px; outline: none; }
.field select:focus, .field input:focus { border-color: #6366f1; }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 4px; }
.btn-cancel-modal { padding: 8px 20px; background: #f1f5f9; color: #475569; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; }
.btn-save { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-save:hover { background: #4f46e5; }
.btn-delete-confirm { padding: 8px 20px; background: #dc2626; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-delete-confirm:hover { background: #b91c1c; }
.error { color: #dc2626; font-size: 13px; margin-bottom: 8px; }
.confirm-text { font-size: 14px; color: #475569; margin-bottom: 20px; }
</style>

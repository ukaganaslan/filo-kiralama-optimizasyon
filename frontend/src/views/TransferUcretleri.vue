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
          <th class="sortable" @click="sortBy('from_branch_name')">Çıkış Şubesi <span class="sort-ind">{{ sortArrow('from_branch_name') }}</span></th>
          <th class="sortable" @click="sortBy('to_branch_name')">Varış Şubesi <span class="sort-ind">{{ sortArrow('to_branch_name') }}</span></th>
          <th class="sortable" @click="sortBy('cost')">Ücret (₺) <span class="sort-ind">{{ sortArrow('cost') }}</span></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="c in sorted" :key="c.id">
          <td>{{ c.from_branch_name }}</td>
          <td>{{ c.to_branch_name }}</td>
          <td class="cost-cell">{{ c.cost }} ₺</td>
          <td class="actions">
            <div class="action-menu" @click.stop>
              <button class="btn-dots" @click="toggleMenu(c.id)">···</button>
              <div v-if="openMenuId === c.id" class="action-dropdown">
                <button @click="openEdit(c); openMenuId = null">Düzenle</button>
                <button class="danger" @click="confirmDelete(c); openMenuId = null">Sil</button>
              </div>
            </div>
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
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useTableSort } from '@/composables/useTableSort'

const costs = ref([])
const branches = ref([])
const openMenuId = ref(null)

const { sortBy, sortArrow, sorted } = useTableSort(costs, {
  cost: c => Number(c.cost) || 0,
})
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

function toggleMenu(id) { openMenuId.value = openMenuId.value === id ? null : id }
function closeMenu() { openMenuId.value = null }
onMounted(() => { loadData(); document.addEventListener('click', closeMenu) })
onUnmounted(() => document.removeEventListener('click', closeMenu))

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
.btn-add { padding: 8px 18px; background: #6366f1; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.15s, transform 0.15s, box-shadow 0.15s; }
.btn-add:hover { background: #4f46e5; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(79,70,229,0.3); }
.btn-add:active { transform: translateY(0); }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th:first-child { border-radius: 14px 0 0 0; } th:last-child { border-radius: 0 14px 0 0; } th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
th.sortable { cursor: pointer; user-select: none; transition: color 0.15s; }
th.sortable:hover { color: #6366f1; }
.sort-ind { font-size: 9px; color: #6366f1; }
tr:not(:last-child) td { border-bottom: 1px solid #f1f5f9; }
tbody tr { transition: background 0.12s; }
tbody tr:hover td { background: #fafbff; }
.cost-cell { font-weight: 700; color: #000000; }
.actions { text-align: center !important; }
.action-menu { position: relative; display: inline-block; }
.btn-dots { background: none; border: 1px solid #e2e8f0; border-radius: 6px; padding: 4px 10px; cursor: pointer; font-size: 16px; color: #64748b; line-height: 1; letter-spacing: 2px; transition: background 0.15s, border-color 0.15s; }
.btn-dots:hover { background: #f1f5f9; border-color: #cbd5e1; }
.action-dropdown { position: absolute; right: 0; top: calc(100% + 4px); background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 8px 24px rgba(15,23,42,0.12); min-width: 110px; z-index: 300; overflow: hidden; animation: dropdownIn 0.12s ease; }
@keyframes dropdownIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }
.action-dropdown button { display: block; width: 100%; padding: 9px 14px; text-align: left; background: none; border: none; font-size: 13px; color: #374151; cursor: pointer; transition: background 0.12s; }
.action-dropdown button:hover { background: #f8fafc; }
.action-dropdown button.danger { color: #dc2626; }
.action-dropdown button.danger:hover { background: #fee2e2; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.45); backdrop-filter: blur(2px); display: flex; align-items: center; justify-content: center; z-index: 100; animation: overlayIn 0.15s ease; }
@keyframes overlayIn { from { opacity: 0; } to { opacity: 1; } }
.modal { background: white; border-radius: 14px; padding: 28px; width: 420px; box-shadow: 0 20px 60px rgba(15,23,42,0.25); animation: modalIn 0.18s cubic-bezier(0.4,0,0.2,1); }
@keyframes modalIn { from { opacity: 0; transform: translateY(8px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal-sm { width: 340px; }
h3 { font-size: 17px; font-weight: 700; color: #1e293b; margin: 0 0 20px; }
.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.field label { font-size: 12px; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; }
.field select, .field input { border: 1px solid #e2e8f0; border-radius: 8px; padding: 9px 12px; font-size: 14px; outline: none; transition: border-color 0.15s, box-shadow 0.15s; }
.field select:focus, .field input:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 4px; }
.btn-cancel-modal { padding: 8px 20px; background: #f1f5f9; color: #475569; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; transition: background 0.15s; }
.btn-cancel-modal:hover { background: #e2e8f0; }
.btn-save { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; transition: background 0.15s, transform 0.15s; }
.btn-save:hover { background: #4f46e5; transform: translateY(-1px); }
.btn-delete-confirm { padding: 8px 20px; background: #dc2626; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; transition: background 0.15s, transform 0.15s; }
.btn-delete-confirm:hover { background: #b91c1c; transform: translateY(-1px); }
.error { color: #dc2626; font-size: 13px; margin-bottom: 8px; }
.confirm-text { font-size: 14px; color: #475569; margin-bottom: 20px; }
</style>

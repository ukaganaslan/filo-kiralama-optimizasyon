<template>
  <div class="content">
    <div class="section-header">
      <div class="header-left">
        <h2>Şube Araçları</h2>
        <span class="count-badge">{{ filteredVehicles.length }} araç</span>
      </div>
      <div class="header-right">
        <input v-model="search" class="search-input" placeholder="Plaka veya araç kodu ara..." />
        <button class="btn-add" @click="openAdd">+ Araç Ekle</button>
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th class="sortable" @click="sortBy('vehicle_id')">Araç ID <span class="sort-ind">{{ sortArrow('vehicle_id') }}</span></th>
          <th class="sortable" @click="sortBy('sasi')">Sasi Kodu <span class="sort-ind">{{ sortArrow('sasi') }}</span></th>
          <th class="sortable" @click="sortBy('brand_model')">Marka / Model <span class="sort-ind">{{ sortArrow('brand_model') }}</span></th>
          <th class="sortable" @click="sortBy('plate')">Plaka <span class="sort-ind">{{ sortArrow('plate') }}</span></th>
          <th class="sortable" @click="sortBy('group')">Grup <span class="sort-ind">{{ sortArrow('group') }}</span></th>
          <th class="sortable" @click="sortBy('status')">Durum <span class="sort-ind">{{ sortArrow('status') }}</span></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="v in sortedVehicles" :key="v.id" @click="openHistory(v)" style="cursor: pointer;">
          <td class="id">{{ v.vehicle_id }}</td>
          <td>{{ v.sasi }}</td>
          <td>{{ v.brand }} {{ v.model }}</td>
          <td>{{ v.plate || '—' }}</td>
          <td><span :class="'badge-group badge-' + v.group">{{ groupLabel(v.group) }}</span></td>
          <td><span :class="'badge-status badge-' + v.current_status">{{ statusLabel(v.current_status) }}</span></td>
          <td class="actions">
            <div class="action-menu" @click.stop>
              <button class="btn-dots" @click="toggleMenu(v.id)">···</button>
              <div v-if="openMenuId === v.id" class="action-dropdown">
                <button @click="openEdit(v); openMenuId = null">Düzenle</button>
                <button class="danger" @click="confirmDelete(v); openMenuId = null">Sil</button>
              </div>
            </div>
          </td>
        </tr>
        <tr v-if="sortedVehicles.length === 0">
          <td colspan="8" class="empty">Bu şubede araç bulunamadı.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="editModal" class="modal-overlay" @click.self="editModal = false">
    <div class="modal">
      <h3>{{ editingId ? 'Araç Düzenle' : 'Yeni Araç Ekle' }}</h3>
      <div v-if="editingId" class="field">
        <label>Araç ID</label>
        <input :value="editForm.vehicle_id" type="text" disabled class="disabled" />
      </div>
      <div class="field">
        <label>Marka</label>
        <input v-model="editForm.brand" type="text" placeholder="Araç Markası" />
      </div>
      <div class="field">
        <label>Model</label>
        <input v-model="editForm.model" type="text" placeholder="Araç Modeli" />
      </div>
      <div class="field">
        <label>Plaka</label>
        <input v-model="editForm.plate" type="text" placeholder="Plaka" />
      </div>
      <div class="field">
        <label>Sasi Kodu</label>
        <input v-model="editForm.sasi" type="text" placeholder="Sasi Kodu" />
      </div>
      <div class="field">
        <label>Grup</label>
        <select v-model="editForm.group">
          <option value="economy">Ekonomi</option>
          <option value="mid">Orta Sınıf</option>
          <option value="suv">SUV</option>
        </select>
      </div>
      <div class="field">
        <label>Durum</label>
        <select v-model="editForm.status">
          <option value="available">Müsait</option>
          <option value="maintenance">Bakımda</option>
          <option value="service">Serviste</option>
          <option value="inactive">Pasif</option>
          <option value="reserved">Rezerve Edildi</option>
        </select>
      </div>
      <p v-if="formError" class="error">{{ formError }}</p>
      <div class="modal-actions">
        <button class="btn-cancel-modal" @click="editModal = false">Vazgeç</button>
        <button class="btn-save" @click="saveEdit">Kaydet</button>
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

  <div v-if="historyModal" class="modal-overlay" @click.self="historyModal = false">
    <div class="modal modal-wide">
      <div class="modal-header">
        <h3>{{ historyData.brand }} {{ historyData.model }} — {{ historyData.plate }}</h3>
        <button class="btn-cancel-modal" @click="historyModal = false">Kapat</button>
      </div>

      <div class="history-stats">
        <div class="stat-box">
          <span class="stat-label">Toplam KM</span>
          <span class="stat-value">{{ historyData.total_km?.toLocaleString('tr-TR') ?? '—' }}</span>
        </div>
        <div class="stat-box">
          <span class="stat-label">Toplam Kiralama</span>
          <span class="stat-value">{{ historyData.reservations?.length ?? 0 }}</span>
        </div>
      </div>

      <h4>Rezervasyon Geçmişi</h4>
      <table v-if="historyData.reservations?.length">
        <thead>
          <tr>
            <th>Rezervasyon ID</th>
            <th>Müşteri</th>
            <th>Başlangıç</th>
            <th>Bitiş</th>
            <th>Teslim KM</th>
            <th>İade KM</th>
            <th>Fiyat</th>
            <th>Durum</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in historyData.reservations" :key="r.reservation_id">
            <td>{{ r.reservation_id }}</td>
            <td>{{ r.customer_name }}</td>
            <td>{{ r.start_date }}</td>
            <td>{{ r.end_date }}</td>
            <td>{{ r.delivered_km ?? '—' }}</td>
            <td>{{ r.returned_km ?? '—' }}</td>
            <td>{{ r.total_price ? r.total_price + ' ₺' : '—' }}</td>
            <td><span :class="'badge-status badge-' + r.status">{{ statusLabel(r.status) }}</span></td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty">Rezervasyon kaydı yok.</p>

      <h4>Bakım Logları</h4>
      <table v-if="historyData.maintenance_logs?.length">
        <thead>
          <tr><th>Tür</th><th>Başlangıç</th><th>Bitiş</th><th>KM</th><th>Not</th></tr>
        </thead>
        <tbody>
          <tr v-for="(m, i) in historyData.maintenance_logs" :key="i">
            <td>{{ m.reason }}</td>
            <td>{{ m.start_date }}</td>
            <td>{{ m.end_date ?? '—' }}</td>
            <td>{{ m.current_km }}</td>
            <td>{{ m.notes || '—' }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty">Bakım kaydı yok.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useTableSort } from '@/composables/useTableSort'

const vehicles = ref([])
const search = ref('')
const openMenuId = ref(null)
const editModal = ref(false)
const formError = ref('')
const editForm = ref({})
const editingId = ref(null)
const deleteModal = ref(false)
const deletingVehicle = ref(null)
const historyModal = ref(false)
const historyData = ref({})

function toggleMenu(id) { openMenuId.value = openMenuId.value === id ? null : id }
function closeMenu() { openMenuId.value = null }
onMounted(() => { loadVehicles(); document.addEventListener('click', closeMenu) })
onUnmounted(() => document.removeEventListener('click', closeMenu))

async function loadVehicles() {
  const res = await axios.get('/api/vehicles/')
  vehicles.value = res.data
}

function openAdd() {
  editingId.value = null
  editForm.value = { brand: '', model: '', plate: '', sasi: '', group: 'economy', status: 'available' }
  formError.value = ''
  editModal.value = true
}

function openEdit(v) {
  editingId.value = v.id
  editForm.value = { id: v.id, vehicle_id: v.vehicle_id, brand: v.brand, model: v.model, plate: v.plate, sasi: v.sasi, group: v.group, status: v.status }
  formError.value = ''
  editModal.value = true
}

async function saveEdit() {
  formError.value = ''
  try {
    if (editingId.value) {
      await axios.patch(`/api/vehicles/${editingId.value}/`, {
        brand: editForm.value.brand,
        model: editForm.value.model,
        plate: editForm.value.plate,
        sasi: editForm.value.sasi,
        group: editForm.value.group,
        status: editForm.value.status,
      })
    } else {
      await axios.post('/api/vehicles/', {
        brand: editForm.value.brand,
        model: editForm.value.model,
        plate: editForm.value.plate,
        sasi: editForm.value.sasi,
        group: editForm.value.group,
        status: editForm.value.status,
      })
    }
    editModal.value = false
    await loadVehicles()
  } catch (e) {
    formError.value = e.response?.data?.detail || e.response?.data?.plate?.[0] || 'Kaydetme başarısız.'
  }
}

function confirmDelete(v) {
  deletingVehicle.value = v
  deleteModal.value = true
}

async function doDelete() {
  try {
    await axios.delete(`/api/vehicles/${deletingVehicle.value.id}/`)
    deleteModal.value = false
    deletingVehicle.value = null
    await loadVehicles()
  } catch {
    deleteModal.value = false
  }
}

async function openHistory(v) {
  try {
    const res = await axios.get(`/api/vehicles/${v.vehicle_id}/history/`)
    historyData.value = res.data
    historyModal.value = true
  } catch (e) {
    console.error('vehicle_history error:', e)
  }
}

function groupLabel(g) {
  return { economy: 'Ekonomi', mid: 'Orta Sınıf', suv: 'SUV' }[g] || g
}

function statusLabel(s) {
  return { available: 'Müsait', rented: 'Kiralandı', maintenance: 'Bakımda', service: 'Serviste', inactive: 'Pasif' }[s] || s
}

const filteredVehicles = computed(() => {
  const q = search.value.toLowerCase().trim()
  if (!q) return vehicles.value
  return vehicles.value.filter(v =>
    (v.plate || '').toLowerCase().includes(q) ||
    (v.vehicle_id || '').toLowerCase().includes(q)
  )
})

const { sortBy, sortArrow, sorted: sortedVehicles } = useTableSort(filteredVehicles, {
  brand_model: v => `${v.brand} ${v.model}`,
  group: v => groupLabel(v.group),
  status: v => statusLabel(v.current_status),
})
</script>

<style scoped>
.content { padding: 32px 40px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.btn-add { padding: 8px 18px; background: #6366f1; color: white; border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.15s, transform 0.15s, box-shadow 0.15s; }
.btn-add:hover { background: #4f46e5; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(79,70,229,0.3); }
.btn-add:active { transform: translateY(0); }
.header-left { display: flex; align-items: center; gap: 12px; }
.header-right { display: flex; align-items: center; gap: 12px; }
.search-input { padding: 8px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; color: #475569; outline: none; width: 220px; transition: border-color 0.15s, box-shadow 0.15s; }
.search-input:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }
.search-input::placeholder { color: #94a3b8; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0; }
.count-badge { padding: 3px 10px; background: #f1f5f9; color: #64748b; border-radius: 50px; font-size: 12px; font-weight: 600; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th:first-child { border-radius: 14px 0 0 0; } th:last-child { border-radius: 0 14px 0 0; } th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
th.sortable { cursor: pointer; user-select: none; transition: color 0.15s; }
th.sortable:hover { color: #6366f1; }
.sort-ind { font-size: 9px; color: #6366f1; }
tbody tr { transition: background 0.12s; }
tbody tr:hover { background: #fafbff; }
td { border-top: 1px solid #f1f5f9; color: #374151; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
td:nth-child(1), th:nth-child(1), td:nth-child(2), th:nth-child(2), td:nth-child(3), th:nth-child(3), td:nth-child(4), th:nth-child(4), td:nth-child(5), th:nth-child(5), td:nth-child(6), th:nth-child(6), td:nth-child(7), th:nth-child(7), td:nth-child(8), th:nth-child(8) { text-align: center; }
.id { font-family: monospace; font-weight: 600; color: #1e293b; }
.badge-group, .badge-status { display: inline-block; padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: 600; }
.badge-economy { background: #ede9fe; color: #5b21b6; }
.badge-mid { background: #dbeafe; color: #1e40af; }
.badge-suv { background: #d1fae5; color: #065f46; }
.badge-available { background: #d1fae5; color: #065f46; }
.badge-rented { background: #dbeafe; color: #1e40af; }
.badge-maintenance { background: #fef3c7; color: #92400e; }
.badge-service { background: #fed7aa; color: #9a3412; }
.badge-inactive { background: #f1f5f9; color: #475569; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
.rez-count { display: inline-block; padding: 2px 10px; background: #ede9fe; color: #5b21b6; border-radius: 50px; font-size: 12px; font-weight: 600; }
.actions { text-align: center !important; width: 60px; }
.action-menu { position: relative; display: inline-block; }
.btn-dots { background: none; border: 1px solid #e2e8f0; border-radius: 6px; padding: 4px 10px; cursor: pointer; font-size: 16px; color: #64748b; line-height: 1; letter-spacing: 2px; transition: background 0.15s, border-color 0.15s; }
.btn-dots:hover { background: #f1f5f9; border-color: #cbd5e1; }
.action-dropdown { position: absolute; right: 0; top: calc(100% + 4px); background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 8px 24px rgba(15,23,42,0.12); min-width: 110px; z-index: 300; overflow: hidden; animation: dropdownIn 0.12s ease; }
@keyframes dropdownIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }
.action-dropdown button { display: block; width: 100%; padding: 9px 14px; text-align: left; background: none; border: none; font-size: 13px; color: #374151; cursor: pointer; transition: background 0.12s; }
.action-dropdown button:hover { background: #f8fafc; }
.action-dropdown button.danger { color: #dc2626; }
.action-dropdown button.danger:hover { background: #fee2e2; }
.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.45); backdrop-filter: blur(2px); z-index: 200; display: flex; align-items: center; justify-content: center; animation: overlayIn 0.15s ease; }
@keyframes overlayIn { from { opacity: 0; } to { opacity: 1; } }
.modal { background: white; border-radius: 14px; padding: 32px; width: 420px; box-shadow: 0 20px 60px rgba(15,23,42,0.25); display: flex; flex-direction: column; gap: 14px; animation: modalIn 0.18s cubic-bezier(0.4,0,0.2,1); }
@keyframes modalIn { from { opacity: 0; transform: translateY(8px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal h3 { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; }
.field input, .field select { padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; background: white; color: #1e293b; transition: border-color 0.15s, box-shadow 0.15s; }
.field input:focus, .field select:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }
.disabled { background: #f8f9fa !important; color: #94a3b8 !important; cursor: not-allowed; }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 4px; }
.btn-cancel-modal { padding: 8px 16px; background: white; color: #64748b; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-size: 14px; transition: background 0.15s, border-color 0.15s; }
.btn-cancel-modal:hover { background: #f8fafc; border-color: #cbd5e1; }
.btn-save { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; transition: background 0.15s, transform 0.15s; }
.btn-save:hover { background: #4f46e5; transform: translateY(-1px); }
.error { color: #dc2626; font-size: 13px; margin: 0; }
.modal-sm { width: 340px; }
.btn-delete-confirm { padding: 8px 20px; background: #dc2626; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; transition: background 0.15s, transform 0.15s; }
.btn-delete-confirm:hover { background: #b91c1c; transform: translateY(-1px); }
.confirm-text { color: #374151; font-size: 14px; margin: 0; }
.modal-wide { max-width: 800px; width: 90%; max-height: 85vh; overflow-y: auto; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.modal-header h3 { margin: 0; }
.history-stats { display: flex; gap: 16px; margin-bottom: 8px; }
.stat-box { background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px 20px; border-radius: 8px; }
.stat-label { display: block; font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; margin-bottom: 2px; }
.stat-value { font-size: 22px; font-weight: 700; color: #1e293b; }
h4 { margin: 16px 0 8px; font-size: 13px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; }
</style>

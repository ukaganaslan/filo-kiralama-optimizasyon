<template>
  <div class="content">
    <div class="section-header">
      <div class="header-left">
        <h2>Bakım Kayıtları</h2>
        <span class="count-badge">{{ logs.length }} kayıt</span>
      </div>
      <button class="btn-add" @click="openAdd">+ Bakım Ekle</button>
    </div>
    <table>
      <thead>
        <tr>
          <th class="sortable" @click="sortBy('vehicle_id')">Araç <span class="sort-ind">{{ sortArrow('vehicle_id') }}</span></th>
          <th class="sortable" @click="sortBy('vehicle_plate')">Plaka <span class="sort-ind">{{ sortArrow('vehicle_plate') }}</span></th>
          <th class="sortable" @click="sortBy('reason')">Bakım Türü <span class="sort-ind">{{ sortArrow('reason') }}</span></th>
          <th class="sortable" @click="sortBy('start_date')">Başlangıç <span class="sort-ind">{{ sortArrow('start_date') }}</span></th>
          <th class="sortable" @click="sortBy('end_date')">Bitiş <span class="sort-ind">{{ sortArrow('end_date') }}</span></th>
          <th class="sortable" @click="sortBy('current_km')">KM <span class="sort-ind">{{ sortArrow('current_km') }}</span></th>
          <th>Notlar</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="log in sorted" :key="log.id">
          <td>{{ log.vehicle_id }}</td>
          <td>{{ log.vehicle_plate }}</td>
          <td>{{ reasonLabel(log.reason) }}</td>
          <td>{{ log.start_date }}</td>
          <td>{{ log.end_date || '—' }}</td>
          <td>{{ log.current_km }}</td>
          <td>{{ log.notes || '—' }}</td>
          <td class="actions">
            <div class="action-menu" @click.stop>
              <button class="btn-dots" @click="toggleMenu(log.id)">···</button>
              <div v-if="openMenuId === log.id" class="action-dropdown">
                <button @click="openEdit(log); openMenuId = null">Düzenle</button>
                <button class="danger" @click="confirmDelete(log); openMenuId = null">Sil</button>
              </div>
            </div>
          </td>
        </tr>
        <tr v-if="logs.length === 0">
          <td colspan="8" class="empty">Bakım kaydı bulunamadı.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
    <div class="modal">
      <h3>{{ editingId ? 'Bakım Kaydını Düzenle' : 'Yeni Bakım Kaydı' }}</h3>

      <div class="field">
        <label>Araç</label>
        <div class="vehicle-search" ref="vehicleSearchRef">
          <input
            v-model="vehicleQuery"
            type="text"
            :placeholder="selectedVehicleLabel || 'Plaka veya araç kodu ara...'"
            :class="['vehicle-input', { 'has-value': selectedVehicleLabel }]"
            :disabled="!!editingId"
            @input="vehicleDropdownOpen = true"
            @focus="vehicleDropdownOpen = true"
          />
          <button v-if="selectedVehicleLabel && !editingId" type="button" class="vehicle-clear" @click="clearVehicle">x</button>
          <div v-if="vehicleDropdownOpen && !editingId && filteredVehicles.length > 0" class="vehicle-dropdown">
            <div
              v-for="v in filteredVehicles"
              :key="v.id"
              class="vehicle-option"
              :class="{ disabled: openMaintenanceVehicleIds.has(v.id) }"
              @mousedown.prevent="!openMaintenanceVehicleIds.has(v.id) && selectVehicle(v)"
            >
              <span class="vehicle-plate">{{ v.plate || '—' }}</span>
              <span class="vehicle-meta">{{ v.brand }} {{ v.model }} ({{ v.vehicle_id }}){{ openMaintenanceVehicleIds.has(v.id) ? ' — bakımda' : '' }}</span>
            </div>
          </div>
          <div v-if="vehicleDropdownOpen && !editingId && vehicleQuery && filteredVehicles.length === 0" class="vehicle-dropdown">
            <div class="vehicle-empty">Araç bulunamadı.</div>
          </div>
        </div>
      </div>

      <div class="field">
        <label>Mevcut KM</label>
        <input v-model="form.current_km" type="number" placeholder="0" />
      </div>

      <div class="field">
        <label>Bakım Türü</label>
        <select v-model="form.reason">
          <option value="">Seçin</option>
          <option value="routine">Rutin Bakım</option>
          <option value="cleaning">Temizlik</option>
          <option value="repair">Hasar Onarım</option>
        </select>
      </div>

      <div class="field">
        <label>Başlangıç Tarihi</label>
        <input v-model="form.start_date" type="date" />
      </div>

      <div class="field">
        <label>Bitiş Tarihi</label>
        <input v-model="form.end_date" type="date" />
      </div>

      <div class="field">
        <label>Notlar</label>
        <textarea v-model="form.notes" placeholder="İsteğe bağlı..."></textarea>
      </div>

      <p v-if="formError" class="error">{{ formError }}</p>

      <div class="modal-actions">
        <button class="btn-cancel-modal" @click="showModal = false">Vazgeç</button>
        <button class="btn-save" @click="saveForm">Kaydet</button>
      </div>
    </div>
  </div>

  <div v-if="deleteModal" class="modal-overlay" @click.self="deleteModal = false">
    <div class="modal modal-sm">
      <h3>Bakım Kaydını Sil</h3>
      <p class="confirm-text">Bu bakım kaydını silmek istediğinize emin misiniz?</p>
      <div class="modal-actions">
        <button class="btn-cancel-modal" @click="deleteModal = false">Vazgeç</button>
        <button class="btn-delete-confirm" @click="doDelete">Sil</button>
      </div>
    </div>
  </div>

</template>

<style scoped>
.content { padding: 32px 40px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-left { display: flex; align-items: center; gap: 12px; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0; }
.count-badge { padding: 3px 10px; background: #f1f5f9; color: #64748b; border-radius: 50px; font-size: 12px; font-weight: 600; }
.btn-add { padding: 8px 18px; background: #6366f1; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-add:hover { background: #4f46e5; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
th:first-child { border-radius: 14px 0 0 0; }
th:last-child { border-radius: 0 14px 0 0; }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
th.sortable { cursor: pointer; user-select: none; }
th.sortable:hover { color: #6366f1; }
.sort-ind { font-size: 9px; color: #6366f1; }
td { border-top: 1px solid #f1f5f9; color: #374151; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
.actions { text-align: center !important; }
.action-menu { position: relative; display: inline-block; }
.btn-dots { background: none; border: 1px solid #e2e8f0; border-radius: 6px; padding: 4px 10px; cursor: pointer; font-size: 16px; color: #64748b; line-height: 1; letter-spacing: 2px; }
.btn-dots:hover { background: #f1f5f9; }
.action-dropdown { position: absolute; right: 0; top: calc(100% + 4px); background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); min-width: 110px; z-index: 300; overflow: hidden; }
.action-dropdown button { display: block; width: 100%; padding: 9px 14px; text-align: left; background: none; border: none; font-size: 13px; color: #374151; cursor: pointer; }
.action-dropdown button:hover { background: #f8fafc; }
.action-dropdown button.danger { color: #dc2626; }
.action-dropdown button.danger:hover { background: #fee2e2; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 200; display: flex; align-items: center; justify-content: center; }
.modal { background: white; border-radius: 14px; padding: 32px; width: 440px; box-shadow: 0 8px 32px rgba(0,0,0,0.12); display: flex; flex-direction: column; gap: 16px; }
.modal-sm { width: 340px; }
.modal h3 { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; text-transform: uppercase; }
.field input, .field select, .field textarea { padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; background: white; color: #1e293b; }
.field input:focus, .field select:focus, .field textarea:focus { border-color: #6366f1; }
.field input:disabled, .field select:disabled { background: #f8fafc; color: #94a3b8; cursor: not-allowed; }
.field textarea { resize: vertical; min-height: 80px; }
.vehicle-search { position: relative; }
.vehicle-input { width: 100%; padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; background: white; color: #1e293b; }
.vehicle-input:focus { border-color: #6366f1; }
.vehicle-input.has-value::placeholder { color: #1e293b; }
.vehicle-clear { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 14px; line-height: 1; padding: 4px; }
.vehicle-clear:hover { color: #dc2626; }
.vehicle-dropdown { position: absolute; top: calc(100% + 4px); left: 0; right: 0; background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); z-index: 300; max-height: 260px; overflow-y: auto; }
.vehicle-option { display: flex; flex-direction: column; gap: 2px; padding: 9px 14px; cursor: pointer; }
.vehicle-option:hover { background: #f8fafc; }
.vehicle-option.disabled { opacity: 0.5; cursor: not-allowed; }
.vehicle-option.disabled:hover { background: none; }
.vehicle-plate { font-size: 14px; font-weight: 600; color: #1e293b; }
.vehicle-meta { font-size: 12px; color: #64748b; }
.vehicle-empty { padding: 12px 14px; font-size: 13px; color: #94a3b8; }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 4px; }
.btn-cancel-modal { padding: 8px 16px; background: white; color: #64748b; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-size: 14px; }
.btn-save { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-save:hover { background: #4f46e5; }
.btn-delete-confirm { padding: 8px 20px; background: #dc2626; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-delete-confirm:hover { background: #b91c1c; }
.confirm-text { color: #374151; font-size: 14px; margin: 0; }
.error { color: #dc2626; font-size: 13px; margin: 0; }
</style>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useTableSort } from '@/composables/useTableSort'

const logs = ref([])
const vehicles = ref([])
const showModal = ref(false)
const editingId = ref(null)
const openMenuId = ref(null)
const deleteModal = ref(false)
const deletingLog = ref(null)

const vehicleQuery = ref('')
const vehicleDropdownOpen = ref(false)
const vehicleSearchRef = ref(null)

const form = ref({
  vehicle: null,
  current_km: '',
  reason: '',
  start_date: '',
  end_date: '',
  notes: ''
})

const formError = ref('')

function reasonLabel(r) {
  return { routine: 'Rutin Bakım', cleaning: 'Temizlik', repair: 'Hasar Onarım' }[r] || r
}

const { sortBy, sortArrow, sorted } = useTableSort(logs, {
  reason: log => reasonLabel(log.reason),
  current_km: log => Number(log.current_km) || 0,
})

const openMaintenanceVehicleIds = computed(() =>
  new Set(logs.value.filter(l => !l.end_date).map(l => l.vehicle))
)

const filteredVehicles = computed(() => {
  const q = vehicleQuery.value.toLowerCase().trim()
  const list = q
    ? vehicles.value.filter(v =>
        (v.plate || '').toLowerCase().includes(q) ||
        (v.vehicle_id || '').toLowerCase().includes(q)
      )
    : vehicles.value
  return list.slice(0, 10)
})

const selectedVehicleLabel = computed(() => {
  if (!form.value.vehicle) return ''
  const v = vehicles.value.find(x => x.id === form.value.vehicle)
  return v ? `${v.plate || '—'} — ${v.brand} ${v.model} (${v.vehicle_id})` : ''
})

function selectVehicle(v) {
  form.value.vehicle = v.id
  vehicleQuery.value = ''
  vehicleDropdownOpen.value = false
}

function clearVehicle() {
  form.value.vehicle = null
  vehicleQuery.value = ''
}

function toggleMenu(id) { openMenuId.value = openMenuId.value === id ? null : id }
function closeMenu() { openMenuId.value = null }
function handleOutsideClick(e) {
  closeMenu()
  if (vehicleSearchRef.value && !vehicleSearchRef.value.contains(e.target)) {
    vehicleDropdownOpen.value = false
  }
}
onMounted(() => document.addEventListener('click', handleOutsideClick))
onUnmounted(() => document.removeEventListener('click', handleOutsideClick))

function openAdd() {
  editingId.value = null
  form.value = { vehicle: null, current_km: '', reason: '', start_date: '', end_date: '', notes: '' }
  vehicleQuery.value = ''
  vehicleDropdownOpen.value = false
  formError.value = ''
  showModal.value = true
}

function openEdit(log) {
  editingId.value = log.id
  form.value = {
    vehicle: log.vehicle,
    current_km: log.current_km,
    reason: log.reason,
    start_date: log.start_date,
    end_date: log.end_date || '',
    notes: log.notes || ''
  }
  vehicleQuery.value = ''
  vehicleDropdownOpen.value = false
  formError.value = ''
  showModal.value = true
}

function confirmDelete(log) {
  deletingLog.value = log
  deleteModal.value = true
}

async function doDelete() {
  try {
    await axios.delete(`/api/maintenance-logs/${deletingLog.value.id}/`)
    deleteModal.value = false
    const res = await axios.get('/api/maintenance-logs/')
    logs.value = res.data
  } catch {
    deleteModal.value = false
  }
}

async function saveForm() {
  formError.value = ''
  if (!form.value.vehicle || !form.value.current_km || !form.value.reason || !form.value.start_date) {
    formError.value = 'Araç, KM, bakım türü ve başlangıç tarihi zorunludur.'
    return
  }
  if (form.value.end_date && form.value.end_date < form.value.start_date) {
    formError.value = 'Bitiş tarihi başlangıç tarihinden önce olamaz.'
    return
  }
  try {
    const payload = {
      ...form.value,
      end_date: form.value.end_date || null,
    }
    if (editingId.value) {
      await axios.patch(`/api/maintenance-logs/${editingId.value}/`, payload)
    } else {
      await axios.post('/api/maintenance-logs/', payload)
    }
    const res = await axios.get('/api/maintenance-logs/')
    logs.value = res.data
    showModal.value = false
  } catch (e) {
    const data = e.response?.data
    if (data && typeof data === 'object' && !Array.isArray(data)) {
      const first = Object.values(data)[0]
      formError.value = Array.isArray(first) ? first[0] : first
    } else if (Array.isArray(data)) {
      formError.value = data[0]
    } else {
      formError.value = 'Kaydetme başarısız.'
    }
  }
}

onMounted(async () => {
  const [logsRes, vehiclesRes] = await Promise.all([
    axios.get('/api/maintenance-logs/'),
    axios.get('/api/vehicles/')
  ])
  logs.value = logsRes.data
  vehicles.value = vehiclesRes.data
})
</script>

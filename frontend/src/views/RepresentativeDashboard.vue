<template>
  <div class="content">
    <div class="page-header">
      <div class="header-left">
        <h2>Şube Rezervasyonları</h2>
        <span class="count-badge">{{ reservations.length }} rezervasyon</span>
      </div>
      <button class="btn-add" @click="openCreate">+ Rezervasyon Oluştur</button>
    </div>

    <div class="toolbar">
      <div class="toolbar-filters">
        <input v-if="activeView === 'list'" v-model="tableSearch" class="search-input" placeholder="Ara..." />
        <select v-if="activeView === 'list'" v-model="statusFilter" class="filter-select">
          <option value="">Tüm Durumlar</option>
          <option v-for="o in statusOptions" :key="o.key" :value="o.key">{{ o.label }}</option>
        </select>
        <select v-if="activeView === 'list'" v-model="selectedMonth" class="filter-select">
          <option value="">Tüm Aylar</option>
          <option v-for="m in availableMonths" :key="m" :value="m">{{ formatMonth(m) }}</option>
        </select>
        <input v-if="activeView === 'calendar'" v-model="calendarVehicleSearch" class="search-input" placeholder="Araç/Plaka ara..." />
        <select v-if="activeView === 'calendar'" v-model="calendarGroupFilter" class="filter-select">
          <option value="">Tüm Sınıflar</option>
          <option v-for="g in CATEGORY_ORDER" :key="g" :value="g">{{ categoryLabel(g) }}</option>
        </select>
      </div>
      <div class="toolbar-view">
        <span class="toolbar-divider"></span>
        <select v-model="activeView" class="view-select">
          <option value="list">Liste Görünümü</option>
          <option value="calendar">Takvim Görünümü</option>
        </select>
      </div>
    </div>

    <FullCalendar v-if="activeView === 'calendar'" :options="calendarOptions" />

    <table v-if="activeView === 'list'">
      <thead>
        <tr>
          <th class="sortable" @click="sortBy('id')">ID <span class="sort-ind">{{ sortArrow('id') }}</span></th>
          <th class="sortable" @click="sortBy('vehicle')">Araç <span class="sort-ind">{{ sortArrow('vehicle') }}</span></th>
          <th class="sortable" @click="sortBy('customer')">Müşteri <span class="sort-ind">{{ sortArrow('customer') }}</span></th>
          <th class="sortable" @click="sortBy('group')">Grup <span class="sort-ind">{{ sortArrow('group') }}</span></th>
          <th class="sortable" @click="sortBy('start')">Başlangıç <span class="sort-ind">{{ sortArrow('start') }}</span></th>
          <th class="sortable" @click="sortBy('end')">Bitiş <span class="sort-ind">{{ sortArrow('end') }}</span></th>
          <th class="sortable" @click="sortBy('return_branch')">İade Şube <span class="sort-ind">{{ sortArrow('return_branch') }}</span></th>
          <th class="sortable" @click="sortBy('price')">Tutar <span class="sort-ind">{{ sortArrow('price') }}</span></th>
          <th class="sortable" @click="sortBy('status')">Durum <span class="sort-ind">{{ sortArrow('status') }}</span></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in filteredReservations" :key="r.id" @click="openDetail(r)" style="cursor: pointer;">
          <td class="id">{{ r.reservation_id }}</td>
          <td>{{ r.assigned_vehicle_id }}</td>
          <td>{{ r.customer_username }}</td>
          <td>{{ categoryLabel(r.vehicle_group) }}</td>
          <td>{{ r.start_date }}</td>
          <td>{{ r.end_date }}</td>
          <td>{{ r.return_branch ? (r.return_branch_title || r.return_branch_name) : (r.branch_title || r.branch_name) }}</td>
          <td><span v-if="r.total_price" class="price-badge">{{ Number(r.total_price).toLocaleString('tr-TR') }} ₺</span><span v-else class="price-na">—</span></td>
          <td><span :class="'badge ' + reservationStatus(r).cls">{{ reservationStatus(r).label }}</span></td>
          <td class="actions">
            <div class="action-menu" @click.stop>
              <button class="btn-dots" @click="toggleMenu(r.id)">···</button>
              <div v-if="openMenuId === r.id" class="action-dropdown">
                <button
                  v-if="r.status !== 'cancelled' && r.start_date > bugun"
                  class="danger"
                  @click="iptalEt(r); openMenuId = null"
                >
                  İptal Et
                </button>
                <span v-else class="no-action">İşlem yok</span>
              </div>
            </div>
          </td>
        </tr>
        <tr v-if="filteredReservations.length === 0">
          <td colspan="7" class="empty">Bu şubeye ait rezervasyon bulunamadı.</td>
        </tr>
      </tbody>
    </table>

  </div>

  <div v-if="createModal" class="modal-overlay" @click.self="createModal = false">
    <div class="modal">
      <h3>Müşteri Adına Rezervasyon</h3>

      <!-- Takvimden açıldığında: özet bilgi kartları -->
      <div v-if="calendarMode" class="info-summary">
        <div class="info-item">
          <span class="info-label">ŞUBE</span>
          <span class="info-value">{{ currentBranchName }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">GRUP</span>
          <span class="info-value">{{ categoryLabel(form.vehicle_group) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">TARİH</span>
          <span class="info-value">{{ toLocalDateStr(dateRange.start) }} → {{ toLocalDateStr(dateRange.end) }}</span>
        </div>
      </div>

      <div v-if="calendarMode" class="field">
        <label>Araç Modeli</label>
        <select v-model="form.preferred_vehicle_model">
          <option value="">Seçin</option>
          <option v-for="m in preferredModels" :key="m.id" :value="m.id">{{ m.brand }} {{ m.model }} ({{ m.sipp_code }})</option>
        </select>
        <span v-if="preferredModels.length === 0" class="transfer-hint">Bu grupta katalog modeli bulunamadı.</span>
      </div>

      <div class="field">
        <label>Müşteri</label>
        <div class="customer-search" ref="customerSearchRef">
          <input
            v-model="customerQuery"
            type="text"
            :placeholder="selectedCustomer ? selectedCustomer : 'İsim veya kullanıcı adı ara...'"
            :class="['customer-input', { 'has-value': selectedCustomer }]"
            @input="customerDropdownOpen = true"
            @focus="customerDropdownOpen = true"
          />
          <button v-if="selectedCustomer" class="customer-clear" @click="clearCustomer">x</button>
          <div v-if="customerDropdownOpen && filteredCustomers.length > 0" class="customer-dropdown">
            <div
              v-for="u in filteredCustomers"
              :key="u.id"
              class="customer-option"
              @mousedown.prevent="selectCustomer(u)"
            >
              <span class="customer-name">{{ u.full_name || u.username }}</span>
              <span class="customer-username">@{{ u.username }}</span>
            </div>
          </div>
          <div v-if="customerDropdownOpen && customerQuery && filteredCustomers.length === 0" class="customer-dropdown">
            <div class="customer-empty">Kullanıcı bulunamadı.</div>
          </div>
        </div>
      </div>

      <!-- Sadece normal modda (takvim seçimi yoksa) göster -->
      <template v-if="!calendarMode">
        <div class="field">
          <label class="checkbox-label">
            <input type="checkbox" v-model="differentReturn" @change="onDifferentReturnChange" />
            Farklı bir noktaya teslim
          </label>
        </div>

        <div v-if="differentReturn" class="field">
          <label>İade Yeri</label>
          <select v-model="form.return_branch" @change="fetchTransferCost">
            <option value="">Seçin</option>
            <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.title || b.name }}</option>
          </select>
          <span v-if="transferCost !== null" class="transfer-hint">
            Transfer ücreti: {{ transferCost > 0 ? transferCost + ' ₺' : 'Ücretsiz' }}
          </span>
        </div>

        <div class="field">
          <label>Araç Grubu</label>
          <select v-model="form.vehicle_group" @change="fetchAvailability">
            <option value="">Seçin</option>
            <option v-for="g in CATEGORY_ORDER" :key="g" :value="g">{{ categoryLabel(g) }}</option>
          </select>
        </div>

        <div v-if="form.vehicle_group" class="field">
          <label>Araç Modeli</label>
          <select v-model="form.preferred_vehicle_model">
            <option value="">Seçin</option>
            <option v-for="m in preferredModels" :key="m.id" :value="m.id">{{ m.brand }} {{ m.model }} ({{ m.sipp_code }})</option>
          </select>
          <span v-if="form.vehicle_group && preferredModels.length === 0" class="transfer-hint">Bu grupta katalog modeli bulunamadı.</span>
        </div>

        <div v-if="availabilityLoading" class="loading-hint">Müsait günler yükleniyor...</div>

        <div v-if="availableDates.length > 0" class="calendar-section">
          <label>TARİH ARALIĞI</label>
          <VDatePicker
            v-model.range="dateRange"
            :disabled-dates="disabledDates"
            :min-date="new Date()"
            :max-date="maxAvailabilityDate"
            color="indigo"
            is-expanded
          />
        </div>

        <div v-if="form.vehicle_group && availableDates.length === 0 && !availabilityLoading" class="no-avail">
          Bu grupta müsait gün bulunmuyor.
        </div>
      </template>

      <p v-if="formError" class="error">{{ formError }}</p>
      <p v-if="formSuccess" class="success">{{ formSuccess }}</p>

      <div class="modal-actions">
        <button class="btn-cancel-modal" @click="createModal = false">Vazgeç</button>
        <button class="btn-save" @click="handleCreate" :disabled="!canCreate">Oluştur</button>
      </div>
    </div>
  </div>

</template>
<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import FullCalendar from '@fullcalendar/vue3'
import ResourceTimelinePlugin from '@fullcalendar/resource-timeline'
import trLocale from '@fullcalendar/core/locales/tr'
import interactionPlugin from '@fullcalendar/interaction'
import { useRouter } from 'vue-router'
import { CATEGORY_ORDER, categoryLabel } from '@/constants/sipp'

const router = useRouter()
const reservations = ref([])
const vehicles = ref([])
const customers = ref([])
const branches = ref([])
const branchId = ref(null)
const activeView = ref('list')
const bugun = new Date().toISOString().split('T')[0]
const openMenuId = ref(null)
const selectedMonth = ref(new Date().toISOString().slice(0, 7)) 
const availableMonths = computed(() => {
  const months = [...new Set(reservations.value.map(r => r.start_date.slice(0, 7)))]
  return months.sort()
})

const tableSearch = ref('')
const statusFilter = ref('')
const sortKey = ref('')
const sortDir = ref('asc')

const statusOptions = [
  { key: 'pending', label: 'Bekliyor' },
  { key: 'assigned', label: 'Onaylandı' },
  { key: 'delivery_day', label: 'Teslim Günü' },
  { key: 'delivering', label: 'Teslim İşlemde' },
  { key: 'delivered', label: 'Teslim Edildi' },
  { key: 'return_day', label: 'İade Günü' },
  { key: 'returning', label: 'İade İşlemde' },
  { key: 'returned', label: 'İade Edildi' },
  { key: 'cancelled', label: 'İptal' },
]
const STATUS_RANK = { pending: 0, assigned: 1, delivery_day: 2, delivering: 3, delivered: 4, return_day: 5, returning: 6, returned: 7, cancelled: 8 }

function statusKey(r) {
  if (r.status === 'cancelled') return 'cancelled'
  if (r.status === 'pending') return 'pending'
  if (r.delivery_info?.returned) return 'returned'
  if (r.delivery_info?.returned_stage) return 'returning'
  if (r.delivery_info?.delivered) {
    if (r.end_date == bugun) return 'return_day'
    return 'delivered'
  }
  if (r.delivery_info?.delivered_stage) return 'delivering'
  if (r.status === 'assigned' && r.start_date == bugun) return 'delivery_day'
  return 'assigned'
}

const vehiclePlateMap = computed(() => {
  const m = {}
  for (const v of vehicles.value) m[v.vehicle_id] = v.plate
  return m
})

const calendarGroupFilter = ref('')
const calendarVehicleSearch = ref('')

const filteredCalendarVehicles = computed(() => {
  let list = vehicles.value
  if (calendarGroupFilter.value) list = list.filter(v => v.group === calendarGroupFilter.value)
  if (calendarVehicleSearch.value.trim()) {
    const q = calendarVehicleSearch.value.trim().toLowerCase()
    list = list.filter(v =>
      (v.vehicle_id || '').toLowerCase().includes(q) ||
      (v.plate || '').toLowerCase().includes(q)
    )
  }
  return list
})

function sortBy(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}
function sortArrow(key) {
  if (sortKey.value !== key) return ''
  return sortDir.value === 'asc' ? '▲' : '▼'
}
function sortValue(r, key) {
  switch (key) {
    case 'id': return r.reservation_id || ''
    case 'vehicle': return r.assigned_vehicle_id || ''
    case 'customer': return r.customer_username || r.guest_name || ''
    case 'return_branch': return r.return_branch ? (r.return_branch_title || r.return_branch_name) : (r.branch_title || r.branch_name || '')
    case 'group': return r.vehicle_group || ''
    case 'start': return r.start_date || ''
    case 'end': return r.end_date || ''
    case 'price': return Number(r.total_price) || 0
    case 'status': return STATUS_RANK[statusKey(r)] ?? 99
    default: return ''
  }
}

const filteredReservations = computed(() => {
  let list = reservations.value
  if (selectedMonth.value) list = list.filter(r => r.start_date.startsWith(selectedMonth.value))
  if (tableSearch.value.trim()) {
    const q = tableSearch.value.trim().toLowerCase()
    list = list.filter(r => {
      const plate = vehiclePlateMap.value[r.assigned_vehicle_id] || ''
      const customer = r.customer_username || `Misafir - ${r.guest_name}`
      const returnBranch = r.return_branch ? (r.return_branch_title || r.return_branch_name) : (r.branch_title || r.branch_name || '')
      const price = r.total_price ? Number(r.total_price).toLocaleString('tr-TR') : ''
      const haystack = [
        r.reservation_id, plate, r.assigned_vehicle_id, customer, returnBranch,
        r.vehicle_group, r.start_date, r.end_date, price, reservationStatus(r).label,
      ].join(' ').toLowerCase()
      return haystack.includes(q)
    })
  }
  if (statusFilter.value) list = list.filter(r => statusKey(r) === statusFilter.value)
  if (sortKey.value) {
    list = [...list].sort((a, b) => {
      const va = sortValue(a, sortKey.value)
      const vb = sortValue(b, sortKey.value)
      const cmp = (typeof va === 'number' && typeof vb === 'number')
        ? va - vb
        : String(va).localeCompare(String(vb), 'tr')
      return sortDir.value === 'asc' ? cmp : -cmp
    })
  }
  return list
})

function toggleMenu(id) {
  openMenuId.value = openMenuId.value === id ? null : id
}

async function iptalEt(r) {
  if (!confirm(`${r.reservation_id} rezervasyonunu iptal etmek istiyor musunuz?`)) return
  try {
    await axios.patch(`/api/reservations/${r.id}/`, { status: 'cancelled' })
    const idx = reservations.value.findIndex(x => x.id === r.id)
    if (idx !== -1) reservations.value[idx] = { ...reservations.value[idx], status: 'cancelled' }
    openMenuId.value = null
  } catch {
    alert('İptal işlemi başarısız.')
  }
}

const createModal = ref(false)
const calendarMode = ref(false)
const form = ref({ customer_id: '', vehicle_group: '', preferred_vehicle_model: '', branch: '', return_branch: '' })
const differentReturn = ref(false)
const transferCost = ref(null)
const dateRange = ref({ start: null, end: null })
const availableDates = ref([])
const availabilityLoading = ref(false)
const preferredModels = ref([])
const formError = ref('')
const formSuccess = ref('')

const customerQuery = ref('')
const selectedCustomer = ref('')
const customerDropdownOpen = ref(false)
const customerSearchRef = ref(null)

const calendarOptions = computed(() => ({
  plugins: [ResourceTimelinePlugin, interactionPlugin],
  initialView: 'resourceTimelineMonth',
  selectable: true,
  eventStartEditable: false,
  eventResourceEditable: true,
  select(info) {
    const startStr = info.startStr
    const endD = new Date(info.end)
    endD.setDate(endD.getDate() - 1)
    const endStr = toLocalDateStr(endD)
    const vehicle = vehicles.value.find(v => v.vehicle_id === info.resource?.id)
    openCreate({ startDate: startStr, endDate: endStr, vehicleGroup: vehicle?.group || '' })
  },
  eventDrop(info) {
    const reservationId = info.event.id
    const newVehicleId = info.newResource?.id
    if (!newVehicleId) return
    if (!confirm(`Rezervasyonu ${newVehicleId} aracına taşımak istiyor musunuz?`)) {
      info.revert()
      return
    }
    axios.post(`/api/reservations/${reservationId}/reassign-vehicle/`, { vehicle_id: newVehicleId })
      .then(() => {
        const idx = reservations.value.findIndex(r => r.id === Number(reservationId))
        if (idx !== -1) reservations.value[idx] = { ...reservations.value[idx], assigned_vehicle_id: newVehicleId }
      })
      .catch(e => {
        alert(e.response?.data?.non_field_errors?.[0] || e.response?.data?.detail || 'Araç değiştirilemedi.')
        info.revert()
      })
  },

  schedulerLicenseKey: 'non-commercial-and-evaluation',
  locale: trLocale,
  height: 'auto',
  slotDuration: { days: 1 },
  resourceAreaWidth: '300px',
  slotLabelFormat: [{ month: 'long', year: 'numeric' }, { day: 'numeric' }],
  headerToolbar: { left: 'prev,next', right: '' },
  resources: filteredCalendarVehicles.value.map(v => ({
    id: v.vehicle_id,
    title: v.sipp_code ? `${v.brand} ${v.model} · ${v.plate} (${v.sipp_code})` : `${v.brand} ${v.model} · ${v.plate}`,
  })),
  events: reservations.value
    .filter(r => r.assigned_vehicle_id && r.status !== 'cancelled' &&
      filteredCalendarVehicles.value.some(v => v.vehicle_id === r.assigned_vehicle_id))
    .map(r => ({
      id: r.id,
      resourceId: r.assigned_vehicle_id,
      title: r.reservation_id,
      start: r.start_date,
      end: r.end_date,
    })),
}))

const filteredCustomers = computed(() => {
  const q = customerQuery.value.toLowerCase().trim()
  if (!q) return customers.value.slice(0, 10)
  return customers.value.filter(u =>
    u.username.toLowerCase().includes(q) ||
    (u.full_name || '').toLowerCase().includes(q)
  ).slice(0, 10)
})

function selectCustomer(u) {
  form.value.customer_id = u.id
  selectedCustomer.value = `${u.full_name || u.username} (@${u.username})`
  customerQuery.value = ''
  customerDropdownOpen.value = false
}

function clearCustomer() {
  form.value.customer_id = ''
  selectedCustomer.value = ''
  customerQuery.value = ''
}

function handleOutsideClick(e) {
  if (customerSearchRef.value && !customerSearchRef.value.contains(e.target)) {
    customerDropdownOpen.value = false
  }
}

const canCreate = computed(() =>
  form.value.customer_id && form.value.vehicle_group && form.value.preferred_vehicle_model && dateRange.value.start && dateRange.value.end
)

// Takvim penceresi, backend'in fiilen fiyatlandırdığı en son güne kadar açık;
// sabit gün sayısı varsayımı ileri tarihli fiyatları yanlışlıkla pasif gösteriyordu.
const maxAvailabilityDate = computed(() => {
  if (!availableDates.value.length) return null
  const maxStr = availableDates.value.reduce((a, b) => (a > b ? a : b))
  return new Date(maxStr + 'T00:00:00')
})

const disabledDates = computed(() => {
  if (availableDates.value.length === 0 || !maxAvailabilityDate.value) return []
  const available = new Set(availableDates.value)
  const disabled = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const totalDays = Math.round((maxAvailabilityDate.value - today) / 86400000) + 1
  for (let i = 0; i < totalDays; i++) {
    const d = new Date(today)
    d.setDate(today.getDate() + i)
    const str = toLocalDateStr(d)
    if (!available.has(str)) disabled.push(new Date(d))
  }
  return disabled
})

onMounted(async () => {
  document.addEventListener('click', handleOutsideClick)
  const [rezRes, profileRes, usersRes, branchRes, vehicleRes] = await Promise.all([
    axios.get('/api/reservations/'),
    axios.get('/api/profile/'),
    axios.get('/api/users/'),
    axios.get('/api/branches/'),
    axios.get('/api/vehicles/'),
  ])
  reservations.value = rezRes.data
  branchId.value = profileRes.data.branch_id
  customers.value = usersRes.data
  branches.value = branchRes.data
  vehicles.value = vehicleRes.data
})

onUnmounted(() => document.removeEventListener('click', handleOutsideClick))

function reservationStatus(r) {
  if (r.status === 'cancelled') return { label: 'İptal', cls: 'badge-cancelled' }
  if (r.status === 'pending') return { label: 'Bekliyor', cls: 'badge-pending' }
  if (r.delivery_info?.returned) return { label: 'İade Alındı', cls: 'badge-returned' }
  if (r.delivery_info?.returned_stage) return { label: 'İade İşlemde', cls: 'badge-processing' }
  if(r.delivery_info?.delivered){
    if(r.end_date == bugun) return { label: 'İade Günü', cls: 'badge-iade'}
    return { label: 'Teslim Edildi', cls: 'badge-delivered' }
  }
  if (r.delivery_info?.delivered_stage) return { label: 'Teslim İşlemde', cls: 'badge-processing' }
  if(r.status == 'assigned' && r.start_date == bugun) return { label: 'Teslim Günü', cls: 'badge-teslimat'}
  return { label: 'Onaylandı', cls: 'badge-assigned' }
}

const currentBranchName = computed(() => {
  const b = branches.value.find(b => b.id === branchId.value)
  return b ? (b.title || b.name) : ''
})

function onDifferentReturnChange() {
  form.value.return_branch = ''
  transferCost.value = null
}

async function fetchTransferCost() {
  if (!branchId.value || !form.value.return_branch) { transferCost.value = null; return }
  const res = await axios.get('/api/transfer-cost/', {
    params: { from: branchId.value, to: form.value.return_branch }
  })
  transferCost.value = res.data.cost
}

async function fetchAvailability() {
  if (!branchId.value || !form.value.vehicle_group) return
  availabilityLoading.value = true
  availableDates.value = []
  dateRange.value = { start: null, end: null }
  form.value.preferred_vehicle_model = ''
  try {
    const [availRes, modelsRes] = await Promise.all([
      axios.get('/api/availability/', { params: { branch: branchId.value } }),
      axios.get('/api/vehicle-models/', { params: { branch: branchId.value, group: form.value.vehicle_group } }),
    ])
    availableDates.value = availRes.data.available_dates
    preferredModels.value = modelsRes.data
  } finally {
    availabilityLoading.value = false
  }
}

function toLocalDateStr(date) {
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}

async function openCreate({ startDate = null, endDate = null, vehicleGroup = '' } = {}) {
  form.value = { customer_id: '', vehicle_group: vehicleGroup, preferred_vehicle_model: '', branch: '', return_branch: '' }
  dateRange.value = { start: null, end: null }
  availableDates.value = []
  preferredModels.value = []
  formError.value = ''
  formSuccess.value = ''
  customerQuery.value = ''
  selectedCustomer.value = ''
  customerDropdownOpen.value = false
  differentReturn.value = false
  transferCost.value = null
  calendarMode.value = !!(startDate && endDate && vehicleGroup)
  createModal.value = true

  if (vehicleGroup) {
    if (startDate && endDate) {
      dateRange.value = {
        start: new Date(startDate + 'T00:00:00'),
        end: new Date(endDate + 'T00:00:00'),
      }
      if (branchId.value) {
        const res = await axios.get('/api/vehicle-models/', { params: { branch: branchId.value, group: vehicleGroup } })
        preferredModels.value = res.data
      }
    } else {
      await fetchAvailability()
    }
  }
}

async function handleCreate() {
  formError.value = ''
  formSuccess.value = ''
  try {
    await axios.post('/api/reservations/', {
      branch: branchId.value,
      vehicle_group: form.value.vehicle_group,
      preferred_vehicle_model: form.value.preferred_vehicle_model,
      start_date: toLocalDateStr(dateRange.value.start),
      end_date: toLocalDateStr(dateRange.value.end),
      customer_id: form.value.customer_id,
      return_branch: differentReturn.value && form.value.return_branch ? form.value.return_branch : null,
    })
    formSuccess.value = 'Rezervasyon oluşturuldu.'
    const res = await axios.get('/api/reservations/')
    reservations.value = res.data
    form.value = { customer_id: '', vehicle_group: '', preferred_vehicle_model: '', branch: '', return_branch: '' }
    dateRange.value = { start: null, end: null }
    availableDates.value = []
    preferredModels.value = []
  } catch (e) {
    const msg = e.response?.data?.non_field_errors?.[0]
    formError.value = msg || 'Rezervasyon oluşturulamadı.'
  }
}
function formatMonth(m) {
  const [y, mo] = m.split('-')
  const names = ['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']
  return `${names[parseInt(mo)-1]} ${y}`
}

function openDetail(r) {
  router.push(`/representative/rezervasyonlar/${r.id}`)
}
</script>

<style scoped>
.content { padding: 32px 40px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
.header-left { display: flex; align-items: center; gap: 12px; }
h2 { font-size: 22px; font-weight: 800; color: #0f172a; letter-spacing: -0.01em; margin: 0; }
.count-badge { padding: 3px 10px; background: #f1f5f9; color: #64748b; border-radius: 50px; font-size: 12px; font-weight: 600; }
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  background: white;
  border: 1px solid #eef0f4;
  border-radius: 12px;
  padding: 10px 14px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  flex-wrap: wrap;
}
.toolbar-filters { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.toolbar-view { display: flex; align-items: center; gap: 16px; }
.toolbar-divider { width: 1px; height: 24px; background: #e5e7eb; }
.view-select, .filter-select { padding: 8px 12px; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 13px; color: #475569; background: white; outline: none; cursor: pointer; height: 36px; transition: border-color 0.15s, box-shadow 0.15s; }
.view-select:focus, .filter-select:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }
.search-input { padding: 8px 14px; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 13px; color: #475569; background: #f8fafc; outline: none; width: 180px; height: 36px; box-sizing: border-box; transition: background 0.15s, border-color 0.15s, box-shadow 0.15s; }
.search-input:focus { border-color: #6366f1; background: white; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }
.search-input::placeholder { color: #94a3b8; }
th.sortable { cursor: pointer; user-select: none; transition: color 0.15s; }
th.sortable:hover { color: #6366f1; }
.sort-ind { font-size: 9px; color: #6366f1; }
.btn-add { padding: 10px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; box-shadow: 0 1px 2px rgba(79,70,229,0.25); transition: background 0.15s, transform 0.15s, box-shadow 0.15s; }
.btn-add:hover { background: #4f46e5; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(79,70,229,0.3); }
.btn-add:active { transform: translateY(0); }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
tbody tr { transition: background 0.12s; }
tbody tr:hover { background: #fafbff; }
td { border-top: 1px solid #f1f5f9; color: #374151; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
td:nth-child(1), th:nth-child(1), td:nth-child(2), th:nth-child(2), td:nth-child(3), th:nth-child(3), td:nth-child(4), th:nth-child(4), td:nth-child(5), th:nth-child(5), td:nth-child(6), th:nth-child(6), td:nth-child(7), th:nth-child(7) { text-align: center; }
.id { font-family: monospace; font-weight: 600; color: #1e293b; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.45); backdrop-filter: blur(2px); z-index: 200; display: flex; align-items: center; justify-content: center; animation: overlayIn 0.15s ease; }
@keyframes overlayIn { from { opacity: 0; } to { opacity: 1; } }
.modal { background: white; border-radius: 12px; padding: 32px; width: 460px; max-height: 85vh; overflow: visible; box-shadow: 0 20px 60px rgba(15,23,42,0.25); display: flex; flex-direction: column; gap: 16px; animation: modalIn 0.18s cubic-bezier(0.4,0,0.2,1); }
@keyframes modalIn { from { opacity: 0; transform: translateY(8px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal h3 { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; }
.field select { padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; background: white; color: #1e293b; transition: border-color 0.15s, box-shadow 0.15s; }
.field select:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }
.customer-search { position: relative; }
.customer-input { width: 100%; padding: 10px 36px 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; box-sizing: border-box; color: #1e293b; transition: border-color 0.15s, box-shadow 0.15s; }
.customer-input:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }
.customer-input.has-value { color: #6366f1; font-weight: 500; }
.customer-clear { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 13px; padding: 0; line-height: 1; }
.customer-clear:hover { color: #dc2626; }
.customer-dropdown { position: absolute; top: calc(100% + 4px); left: 0; right: 0; background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); z-index: 300; overflow: hidden; }
.customer-option { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; cursor: pointer; }
.customer-option:hover { background: #f1f5f9; }
.customer-name { font-size: 14px; color: #1e293b; font-weight: 500; }
.customer-username { font-size: 12px; color: #94a3b8; }
.customer-empty { padding: 12px 14px; font-size: 14px; color: #94a3b8; }
.calendar-section { display: flex; flex-direction: column; gap: 8px; }
.calendar-section label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; }
.loading-hint { font-size: 13px; color: #94a3b8; }
.no-avail { font-size: 13px; color: #dc2626; }
.checkbox-label { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #475569; cursor: pointer; font-weight: normal; letter-spacing: normal; text-transform: none; }
.checkbox-label input { accent-color: #6366f1; width: 15px; height: 15px; }
.transfer-hint { font-size: 12px; color: #6366f1; font-weight: 600; margin-top: 4px; }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 4px; }
.btn-cancel-modal { padding: 8px 16px; background: white; color: #64748b; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-size: 14px; transition: background 0.15s, border-color 0.15s; }
.btn-cancel-modal:hover { background: #f8fafc; border-color: #cbd5e1; }
.btn-save { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; transition: background 0.15s, transform 0.15s; }
.btn-save:hover:not(:disabled) { background: #4f46e5; transform: translateY(-1px); }
.btn-save:disabled { background: #a5b4fc; cursor: not-allowed; }
.btn-export { padding: 8px 20px; background: #1e293b; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-export:hover { background: #0f172a; }
.error { color: #dc2626; font-size: 13px; margin: 0; }
.success { color: #16a34a; font-size: 13px; margin: 0; }
.info-summary { display: flex; gap: 0; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; }
.info-item { flex: 1; padding: 12px 16px; background: #f8fafc; border-right: 1px solid #e2e8f0; }
.info-item:last-child { border-right: none; }
.info-label { display: block; font-size: 10px; font-weight: 700; color: #94a3b8; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px; }
.info-value { display: block; font-size: 14px; font-weight: 700; color: #1e293b; }
.price-badge { font-size: 13px; font-weight: 700; color: #000000; }
.price-na { color: #94a3b8; }
.actions { text-align: center; width: 48px; }
.action-menu { position: relative; display: inline-block; }
.btn-dots { background: none; border: 1px solid #e2e8f0; border-radius: 6px; padding: 2px 8px; font-size: 16px; color: #64748b; cursor: pointer; line-height: 1.4; transition: background 0.15s, border-color 0.15s; }
.btn-dots:hover { background: #f1f5f9; border-color: #cbd5e1; }
.action-dropdown { position: absolute; right: 0; top: calc(100% + 4px); background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 8px 24px rgba(15,23,42,0.12); z-index: 50; min-width: 110px; overflow: hidden; animation: dropdownIn 0.12s ease; }
@keyframes dropdownIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }
.action-dropdown button, .action-dropdown .no-action { display: block; width: 100%; padding: 9px 14px; font-size: 13px; text-align: left; border: none; background: none; cursor: pointer; transition: background 0.12s; }
.action-dropdown button.danger { color: #dc2626; }
.action-dropdown button.danger:hover { background: #fef2f2; }
.no-action { color: #94a3b8; cursor: default; }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.form-field { display: flex; flex-direction: column; gap: 5px; }
.form-field label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.06em; text-transform: uppercase; }
.form-field input[type="number"], .form-field textarea { padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; color: #1e293b; resize: vertical; }
.form-field input[type="number"]:focus, .form-field textarea:focus { border-color: #6366f1; }
.form-field input[type="file"] { font-size: 13px; color: #475569; }
.fuel-slider { width: 100%; accent-color: #6366f1; }
.fuel-labels { display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; }
.section-label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.06em; text-transform: uppercase; }
.car-figure { display: grid; grid-template-areas: "on-tampon on-tampon on-tampon" "on-sol-camurluk kaput on-sag-camurluk" "on-sol-kapi tavan on-sag-kapi" "arka-sol-kapi tavan arka-sag-kapi" "arka-sol-camurluk bagaj arka-sag-camurluk" "arka-tampon arka-tampon arka-tampon"; grid-template-columns: 1fr 1.4fr 1fr; gap: 3px; background: #cbd5e1; border-radius: 8px; padding: 3px; }
.car-part { border-radius: 5px; padding: 8px 4px; text-align: center; cursor: pointer; position: relative; min-height: 42px; display: flex; flex-direction: column; align-items: center; justify-content: center; transition: filter 0.1s; user-select: none; }
.car-part:hover { filter: brightness(0.94); }
.part-label { font-size: 10px; font-weight: 600; color: #1e293b; line-height: 1.2; }
.part-state { font-size: 9px; color: #475569; margin-top: 2px; }
.damage-picker { position: absolute; top: calc(100% + 4px); left: 50%; transform: translateX(-50%); background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.12); z-index: 100; padding: 6px; display: flex; flex-direction: column; gap: 3px; min-width: 90px; }
.damage-picker button { padding: 5px 10px; border: 1px solid #e2e8f0; border-radius: 5px; font-size: 12px; cursor: pointer; text-align: left; }
.damage-picker button:hover { filter: brightness(0.94); }
.damage-legend { display: flex; flex-wrap: wrap; gap: 8px; }
.legend-item { display: flex; align-items: center; gap: 4px; font-size: 11px; color: #475569; }
.legend-dot { width: 12px; height: 12px; border-radius: 3px; display: inline-block; border: 1px solid #cbd5e1; }
.done-info { display: flex; gap: 16px; flex-wrap: wrap; font-size: 13px; color: #475569; }
.done-info a { color: #6366f1; text-decoration: none; font-weight: 600; }
.done-info a:hover { text-decoration: underline; }
.form-actions { display: flex; justify-content: flex-end; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: 600; }
.badge-pending { background: #fef3c7; color: #92400e; }
.badge-assigned { background: #d1fae5; color: #16A34A; }
.badge-cancelled { background: #fee2e2; color: #DC2626; }
.badge-delivered { background: #d1fae5; color: #065f46; }
.badge-returned { background: #e9d5ff; color: #6b21a8; }
.badge-processing { background: #fed7aa; color: #9a3412; }
</style>

<template>
  <div class="content">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Aktif Rezervasyon</div>
        <div class="stat-value">{{ activeCount }}</div>
        <div class="stat-sub">({{ cancelledCount }} iptal)</div>
      </div>
      <div class="stat-card stat-amber">
        <div class="stat-label">Bekleyen</div>
        <div class="stat-value">{{ pendingCount }}</div>

      </div>
      <div class="stat-card stat-green">
        <div class="stat-label">Onaylandı</div>
        <div class="stat-value">{{ assignedCount }}</div>

      </div>
    </div>

    <div class="page-header">
      <h2>Tüm Rezervasyonlar</h2>
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
        <div v-if="activeView === 'calendar'" class="sipp-multiselect" ref="sippDropdownRef">
          <button type="button" class="filter-select sipp-multiselect-btn" @click="sippDropdownOpen = !sippDropdownOpen">
            {{ sippFilterLabel }}
          </button>
          <div v-if="sippDropdownOpen" class="sipp-multiselect-panel">
            <label v-if="availableSippCodes.length === 0" class="sipp-multiselect-empty">Kod yok</label>
            <label v-for="code in availableSippCodes" :key="code" class="sipp-multiselect-option">
              <input type="checkbox" :value="code" v-model="calendarSippFilter" />
              {{ code }}
            </label>
          </div>
        </div>
        <div v-if="activeView === 'calendar'" class="sipp-multiselect" ref="branchDropdownRef">
          <button type="button" class="filter-select sipp-multiselect-btn" @click="branchDropdownOpen = !branchDropdownOpen">
            {{ branchFilterLabel }}
          </button>
          <div v-if="branchDropdownOpen" class="sipp-multiselect-panel">
            <label v-if="branches.length === 0" class="sipp-multiselect-empty">Bayi yok</label>
            <label v-for="b in branches" :key="b.id" class="sipp-multiselect-option">
              <input type="checkbox" :value="b.id" v-model="calendarBranchFilter" />
              {{ b.title || b.name }}
            </label>
          </div>
        </div>
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
          <th class="sortable" @click="sortBy('branch')">Şube <span class="sort-ind">{{ sortArrow('branch') }}</span></th>
          <th class="sortable" @click="sortBy('return_branch')">İade Şube <span class="sort-ind">{{ sortArrow('return_branch') }}</span></th>
          <th class="sortable" @click="sortBy('group')">Grup <span class="sort-ind">{{ sortArrow('group') }}</span></th>
          <th class="sortable" @click="sortBy('start')">Başlangıç <span class="sort-ind">{{ sortArrow('start') }}</span></th>
          <th class="sortable" @click="sortBy('end')">Bitiş <span class="sort-ind">{{ sortArrow('end') }}</span></th>
          <th class="sortable" @click="sortBy('price')">Tutar <span class="sort-ind">{{ sortArrow('price') }}</span></th>
          <th class="sortable" @click="sortBy('status')">Durum <span class="sort-ind">{{ sortArrow('status') }}</span></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in filteredReservations" :key="r.id" @click="openDetail(r)" style="cursor: pointer;">
          <td>{{ r.reservation_id }}</td>
          <td>{{ r.assigned_vehicle_id }}</td>
          <td>{{ r.customer_username || `Misafir - ${r.guest_name}` }}</td>
          <td>{{ r.branch_title }}</td>
          <td>{{ r.return_branch ? (r.return_branch_title || r.return_branch_name) : (r.branch_title || r.branch_name) }}</td>
          <td>{{ categoryLabel(r.vehicle_group) }}</td>
          <td>{{ r.start_date }} <span class="time-tag">{{ formatTime(r.start_time) }}</span></td>
          <td>{{ r.end_date }} <span class="time-tag">{{ formatTime(r.end_time) }}</span></td>
          <td><span v-if="r.total_price" class="price-badge">{{ Number(r.total_price).toLocaleString('tr-TR') }} ₺</span><span v-else class="price-na">—</span></td>
          <td><span :class="'badge ' + reservationStatus(r).cls">{{ reservationStatus(r).label }}</span></td>
          <td class="actions">
            <div class="action-menu" @click.stop>
              <button class="btn-dots" @click="toggleMenu(r.id)">···</button>
              <div v-if="openMenuId === r.id" class="action-dropdown">
                <button class="danger" @click="deleteReservation(r); openMenuId = null">Sil</button>
              </div>
            </div>
          </td>
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
          <span class="info-value">{{ branchName(form.branch) }}</span>
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
          <label>Şube</label>
          <select v-model="form.branch" @change="onBranchChange">
            <option value="">Seçin</option>
            <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.title || b.name }}</option>
          </select>
        </div>

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
import { ref, onMounted, onUnmounted, computed } from 'vue'
import axios from 'axios'
import FullCalendar from '@fullcalendar/vue3'
import ResourceTimelinePlugin from '@fullcalendar/resource-timeline'
import interactionPlugin from '@fullcalendar/interaction'
import trLocale from '@fullcalendar/core/locales/tr'
import { useRouter } from 'vue-router'
import { CATEGORY_ORDER, categoryLabel } from '@/constants/sipp'
import { formatTime } from '@/utils/datetime'


const reservations = ref([])
const activeView = ref('list')
const vehicles = ref([])
const branches = ref([])
const customers = ref([])
const openMenuId = ref(null)
const router = useRouter()
const bugun = new Date().toISOString().split('T')[0]

const activeCount = computed(() => reservations.value.filter(r => r.status !== 'cancelled').length)
const pendingCount = computed(() => reservations.value.filter(r => r.status === 'pending').length)
const assignedCount = computed(() => reservations.value.filter(r => r.status === 'assigned').length)
const cancelledCount = computed(() => reservations.value.filter(r => r.status === 'cancelled').length)
const totalVehicles = computed(() => vehicles.value.length)
const availableVehicles = computed(() => vehicles.value.filter(v => v.status === 'available').length)
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
const calendarSippFilter = ref([])
const sippDropdownOpen = ref(false)
const sippDropdownRef = ref(null)

const availableSippCodes = computed(() => {
  const codes = new Set(vehicles.value.map(v => v.sipp_code).filter(Boolean))
  return [...codes].sort()
})

const sippFilterLabel = computed(() => {
  if (calendarSippFilter.value.length === 0) return 'Tüm SIPP Kodları'
  if (calendarSippFilter.value.length === 1) return calendarSippFilter.value[0]
  return `${calendarSippFilter.value.length} SIPP kodu seçili`
})

const calendarBranchFilter = ref([])
const branchDropdownOpen = ref(false)
const branchDropdownRef = ref(null)

const branchFilterLabel = computed(() => {
  if (calendarBranchFilter.value.length === 0) return 'Tüm Bayiler'
  if (calendarBranchFilter.value.length === 1) {
    const b = branches.value.find(b => b.id === calendarBranchFilter.value[0])
    return b ? (b.title || b.name) : 'Tüm Bayiler'
  }
  return `${calendarBranchFilter.value.length} bayi seçili`
})

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
  if (calendarSippFilter.value.length > 0) {
    list = list.filter(v => calendarSippFilter.value.includes(v.sipp_code))
  }
  if (calendarBranchFilter.value.length > 0) {
    list = list.filter(v => calendarBranchFilter.value.includes(v.branch))
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
    case 'branch': return r.branch_title || r.branch_name || ''
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
        r.reservation_id, plate, r.assigned_vehicle_id, customer, r.branch_title, returnBranch,
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

function openDetail(r) {
  router.push(`/operator/rezervasyonlar/${r.id}`)
}

function reservationStatus(r) {
  if (r.status === 'cancelled') return { label: 'İptal', cls: 'badge-cancelled' }
  if (r.status === 'pending') return { label: 'Bekliyor', cls: 'badge-pending' }
  if (r.delivery_info?.returned) return { label: 'İade Alındı', cls: 'badge-returned' }
  if (r.delivery_info?.returned_stage) return { label: 'İade İşlemde', cls: 'badge-processing' }
  if (r.delivery_info?.delivered) {
    if (r.end_date == bugun) return { label: 'İade Günü · ' + formatTime(r.end_time), cls: 'badge-iade' }
    return { label: 'Teslim Edildi', cls: 'badge-delivered' }
  }
  if (r.delivery_info?.delivered_stage) return { label: 'Teslim İşlemde', cls: 'badge-processing' }
  if (r.status == 'assigned' && r.start_date == bugun) return { label: 'Teslim Günü · ' + formatTime(r.start_time), cls: 'badge-teslimat' }
  return { label: 'Onaylandı', cls: 'badge-assigned' }
}

function toggleMenu(id) { openMenuId.value = openMenuId.value === id ? null : id }
function closeMenu() { openMenuId.value = null }
onMounted(() => document.addEventListener('click', closeMenu))
onUnmounted(() => document.removeEventListener('click', closeMenu))

onMounted(async () => {
  const [rezRes, vehicleRes, branchRes, usersRes] = await Promise.all([
    axios.get('/api/reservations/'),
    axios.get('/api/vehicles/'),
    axios.get('/api/branches/'),
    axios.get('/api/users/'),
  ])
  reservations.value = rezRes.data
  vehicles.value = vehicleRes.data
  branches.value = branchRes.data
  customers.value = usersRes.data
})


async function deleteReservation(r) {
  if (!confirm(`${r.reservation_id} silinsin mi?`)) return
  await axios.delete(`/api/reservations/${r.id}/`)
  reservations.value = reservations.value.filter(x => x.id !== r.id)
}

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
    openCreate({ startDate: startStr, endDate: endStr, vehicleGroup: vehicle?.group || '', branchId: vehicle?.branch || '' })
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

function formatMonth(m) {
  const [y, mo] = m.split('-')
  const names = ['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']
  return `${names[parseInt(mo)-1]} ${y}`
}

function branchName(id) {
  const b = branches.value.find(b => b.id === id)
  return b ? (b.title || b.name) : '—'
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
  if (sippDropdownRef.value && !sippDropdownRef.value.contains(e.target)) {
    sippDropdownOpen.value = false
  }
  if (branchDropdownRef.value && !branchDropdownRef.value.contains(e.target)) {
    branchDropdownOpen.value = false
  }
}
onMounted(() => document.addEventListener('click', handleOutsideClick))
onUnmounted(() => document.removeEventListener('click', handleOutsideClick))

const canCreate = computed(() =>
  form.value.customer_id && form.value.branch && form.value.vehicle_group && form.value.preferred_vehicle_model && dateRange.value.start && dateRange.value.end
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

function onBranchChange() {
  form.value.return_branch = ''
  transferCost.value = null
  form.value.vehicle_group = ''
  form.value.preferred_vehicle_model = ''
  preferredModels.value = []
  dateRange.value = { start: null, end: null }
  availableDates.value = []
}

function onDifferentReturnChange() {
  form.value.return_branch = ''
  transferCost.value = null
}

async function fetchTransferCost() {
  if (!form.value.branch || !form.value.return_branch) { transferCost.value = null; return }
  const res = await axios.get('/api/transfer-cost/', {
    params: { from: form.value.branch, to: form.value.return_branch }
  })
  transferCost.value = res.data.cost
}

async function fetchAvailability() {
  if (!form.value.branch || !form.value.vehicle_group) return
  availabilityLoading.value = true
  availableDates.value = []
  dateRange.value = { start: null, end: null }
  form.value.preferred_vehicle_model = ''
  try {
    const [availRes, modelsRes] = await Promise.all([
      axios.get('/api/availability/', { params: { branch: form.value.branch } }),
      axios.get('/api/vehicle-models/', { params: { branch: form.value.branch, group: form.value.vehicle_group } }),
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

async function openCreate({ startDate = null, endDate = null, vehicleGroup = '', branchId = '' } = {}) {
  form.value = { customer_id: '', vehicle_group: vehicleGroup, preferred_vehicle_model: '', branch: branchId || '', return_branch: '' }
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

  if (vehicleGroup && startDate && endDate) {
    dateRange.value = {
      start: new Date(startDate + 'T00:00:00'),
      end: new Date(endDate + 'T00:00:00'),
    }
  }

  if (vehicleGroup && branchId) {
    const res = await axios.get('/api/vehicle-models/', { params: { branch: branchId, group: vehicleGroup } })
    preferredModels.value = res.data
  }
}

async function handleCreate() {
  formError.value = ''
  formSuccess.value = ''
  try {
    await axios.post('/api/reservations/', {
      branch: form.value.branch,
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
</script>

<style scoped>
.content {
  padding: 32px 40px;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 28px;
}
.stat-card {
  background: white;
  border-radius: 14px;
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  border-left: 4px solid #6366f1;
  transition: box-shadow 0.2s, transform 0.2s;
}
.stat-card:hover { box-shadow: 0 8px 24px rgba(15,23,42,0.08); transform: translateY(-2px); }
.stat-card.stat-amber { border-left-color: #f59e0b; }
.stat-card.stat-green { border-left-color: #10b981; }
.stat-card.stat-blue  { border-left-color: #3b82f6; }
.stat-label {
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 32px;
  font-weight: 800;
  color: #1e293b;
  line-height: 1;
  margin-bottom: 6px;
}
.stat-denom {
  font-size: 18px;
  font-weight: 600;
  color: #94a3b8;
}
.stat-sub {
  font-size: 12px;
  color: #94a3b8;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}
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
.toolbar-filters {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.toolbar-view {
  display: flex;
  align-items: center;
  gap: 16px;
}
.toolbar-divider {
  width: 1px;
  height: 24px;
  background: #e5e7eb;
}
.view-select, .filter-select {
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 13px;
  color: #475569;
  background: white;
  cursor: pointer;
  outline: none;
  height: 36px;
}
.view-select:focus, .filter-select:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }
.search-input {
  padding: 8px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 13px;
  color: #475569;
  background: #f8fafc;
  outline: none;
  width: 180px;
  height: 36px;
  box-sizing: border-box;
  transition: background 0.15s, border-color 0.15s, box-shadow 0.15s;
}
.search-input:focus { border-color: #6366f1; background: white; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }
.search-input::placeholder { color: #94a3b8; }
th.sortable { cursor: pointer; user-select: none; transition: color 0.15s; }
th.sortable:hover { color: #6366f1; }
.sort-ind { font-size: 9px; color: #6366f1; }
h2 { font-size: 22px; font-weight: 800; color: #0f172a; letter-spacing: -0.01em; margin: 0; }
.btn-optimize {
  padding: 10px 24px;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.btn-optimize:disabled { background: #a5b4fc; cursor: not-allowed; }
table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th:first-child { border-radius: 8px 0 0 0; }
th:last-child { border-radius: 0 8px 0 0; }
th {
  background: #f1f5f9;
  font-weight: 600;
  color: #475569;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
tbody tr { transition: background 0.12s; }
tbody tr:hover { background: #fafbff; }
td { border-top: 1px solid #f1f5f9; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
.actions { text-align: center !important; }
.action-menu { position: relative; display: inline-block; }
.btn-dots { background: none; border: 1px solid #e2e8f0; border-radius: 6px; padding: 4px 10px; cursor: pointer; font-size: 16px; color: #64748b; line-height: 1; letter-spacing: 2px; transition: background 0.15s, border-color 0.15s; }
.btn-dots:hover { background: #f1f5f9; border-color: #cbd5e1; }
.action-dropdown { position: absolute; right: 0; top: calc(100% + 4px); background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 8px 24px rgba(15,23,42,0.12); min-width: 100px; z-index: 300; overflow: hidden; animation: dropdownIn 0.12s ease; }
@keyframes dropdownIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }
.action-dropdown button { display: block; width: 100%; padding: 9px 14px; text-align: left; background: none; border: none; font-size: 13px; color: #374151; cursor: pointer; transition: background 0.12s; }
.action-dropdown button:hover { background: #f8fafc; }
.action-dropdown button.danger { color: #dc2626; }
.action-dropdown button.danger:hover { background: #fee2e2; }
.price-badge { font-size: 13px; font-weight: 700; color: #000000; }
.price-na { color: #94a3b8; }
.time-tag { color: #94a3b8; font-size: 12px; }
td:nth-child(1), th:nth-child(1), td:nth-child(2), th:nth-child(2), td:nth-child(3), th:nth-child(3), td:nth-child(4), th:nth-child(4), td:nth-child(5), th:nth-child(5), td:nth-child(6), th:nth-child(6), td:nth-child(7), th:nth-child(7), td:nth-child(8), th:nth-child(8), td:nth-child(9), th:nth-child(9), td:nth-child(10), th:nth-child(10) { text-align: center; }
.badge-delivered { background: #d1fae5; color: #065f46; }
.badge-returned { background: #e9d5ff; color: #6b21a8; }
.badge-processing { background: #fed7aa; color: #9a3412; }

.btn-add { padding: 10px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; box-shadow: 0 1px 2px rgba(79,70,229,0.25); transition: background 0.15s, transform 0.15s, box-shadow 0.15s; }
.btn-add:hover { background: #4f46e5; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(79,70,229,0.3); }
.btn-add:active { transform: translateY(0); }
.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.45); backdrop-filter: blur(2px); z-index: 200; display: flex; align-items: center; justify-content: center; animation: overlayIn 0.15s ease; }
@keyframes overlayIn { from { opacity: 0; } to { opacity: 1; } }
.modal { background: white; border-radius: 12px; padding: 32px; width: 460px; max-height: 85vh; overflow: visible; box-shadow: 0 20px 60px rgba(15,23,42,0.25); display: flex; flex-direction: column; gap: 16px; animation: modalIn 0.18s cubic-bezier(0.4,0,0.2,1); }
@keyframes modalIn { from { opacity: 0; transform: translateY(8px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal h3 { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; }
.field select { padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; background: white; color: #1e293b; transition: border-color 0.15s, box-shadow 0.15s; }
.field select:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }
.sipp-multiselect { position: relative; }
.sipp-multiselect-btn { min-width: 160px; text-align: left; }
.sipp-multiselect-panel { position: absolute; top: calc(100% + 4px); left: 0; min-width: 160px; max-height: 260px; overflow-y: auto; background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); z-index: 300; padding: 6px; }
.sipp-multiselect-option { display: flex; align-items: center; gap: 8px; padding: 7px 8px; border-radius: 6px; font-size: 13px; color: #1e293b; cursor: pointer; }
.sipp-multiselect-option:hover { background: #f1f5f9; }
.sipp-multiselect-empty { display: block; padding: 7px 8px; font-size: 13px; color: #94a3b8; }
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
.error { color: #dc2626; font-size: 13px; margin: 0; }
.success { color: #16a34a; font-size: 13px; margin: 0; }
.info-summary { display: flex; gap: 0; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; }
.info-item { flex: 1; padding: 12px 16px; background: #f8fafc; border-right: 1px solid #e2e8f0; }
.info-item:last-child { border-right: none; }
.info-label { display: block; font-size: 10px; font-weight: 700; color: #94a3b8; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px; }
.info-value { display: block; font-size: 14px; font-weight: 700; color: #1e293b; }
</style>

<style>
.fc .fc-timeline-slot-label { color: #1e293b !important; }
.fc .fc-col-header-cell-cushion { color: #1e293b !important; }
</style>


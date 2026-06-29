<template>
  <div class="content">
    <div class="section-header">
      <div class="header-left">
        <h2>Şube Rezervasyonları</h2>
        <span class="count-badge">{{ reservations.length }} rezervasyon</span>
      </div>
        <select v-model="selectedMonth" class="view-select">
          <option value="">Tüm Aylar</option>
          <option v-for="m in availableMonths" :key="m" :value="m">{{ formatMonth(m) }}</option>
        </select>
        <select v-model="activeView" class="view-select">
          <option value="list">Liste Görünümü</option>
          <option value="calendar">Takvim Görünümü</option>
        </select>
      <button class="btn-add" @click="openCreate">+ Rezervasyon Oluştur</button>
    </div>

    <FullCalendar v-if="activeView === 'calendar'" :options="calendarOptions" />

    <table v-if="activeView === 'list'">
      <thead>
        <tr>
          <th>ID</th>
          <th>Araç</th>
          <th>Müşteri</th>
          <th>Grup</th>
          <th>Başlangıç</th>
          <th>Bitiş</th>
          <th>İade Şube</th>
          <th>Tutar</th>
          <th>Durum</th>
          <th></th>
          
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in filteredReservations" :key="r.id">
          <td class="id">{{ r.reservation_id }}</td>
          <td>{{ r.assigned_vehicle_id }}</td>
          <td>{{ r.customer_username }}</td>
          <td>{{ r.vehicle_group }}</td>
          <td>{{ r.start_date }}</td>
          <td>{{ r.end_date }}</td>
          <td>{{ r.return_branch ? (r.return_branch_title || r.return_branch_name) : (r.branch_title || r.branch_name) }}</td>
          <td><span v-if="r.total_price" class="price-badge">{{ Number(r.total_price).toLocaleString('tr-TR') }} ₺</span><span v-else class="price-na">—</span></td>
          <td><span :class="'badge badge-' + r.status">{{ statusLabel(r.status) }}</span></td>
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
          <span class="info-value">{{ groupLabel(form.vehicle_group) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">TARİH</span>
          <span class="info-value">{{ toLocalDateStr(dateRange.start) }} → {{ toLocalDateStr(dateRange.end) }}</span>
        </div>
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
            <option value="economy">Ekonomi</option>
            <option value="mid">Orta Sınıf</option>
            <option value="suv">SUV</option>
          </select>
        </div>

        <div v-if="availabilityLoading" class="loading-hint">Müsait günler yükleniyor...</div>

        <div v-if="availableDates.length > 0" class="calendar-section">
          <label>TARİH ARALIĞI</label>
          <VDatePicker
            v-model.range="dateRange"
            :disabled-dates="disabledDates"
            :min-date="new Date()"
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
  return months.sort().reverse()
})

const filteredReservations = computed(() =>
  selectedMonth.value
    ? reservations.value.filter(r => r.start_date.startsWith(selectedMonth.value))
    : reservations.value
)

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
const form = ref({ customer_id: '', vehicle_group: '', branch: '', return_branch: '' })
const differentReturn = ref(false)
const transferCost = ref(null)
const dateRange = ref({ start: null, end: null })
const availableDates = ref([])
const availabilityLoading = ref(false)
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
  select(info) {
    const startStr = info.startStr
    const endD = new Date(info.end)
    endD.setDate(endD.getDate() - 1)
    const endStr = toLocalDateStr(endD)
    const vehicle = vehicles.value.find(v => v.vehicle_id === info.resource?.id)
    openCreate({ startDate: startStr, endDate: endStr, vehicleGroup: vehicle?.group || '' })
  },
  schedulerLicenseKey: 'non-commercial-and-evaluation',
  locale: trLocale,
  height: 'auto',
  slotDuration: { days: 1 },
  resourceAreaWidth: '210px',
  slotLabelFormat: [{ month: 'long', year: 'numeric' }, { day: 'numeric' }],
  headerToolbar: { left: 'prev,next', right: '' },
  resources: vehicles.value.map(v => ({
    id: v.vehicle_id,
    title: `${v.vehicle_id} (${v.group})`,
  })),
  events: reservations.value
    .filter(r => r.assigned_vehicle_id && r.status !== 'cancelled')
    .map(r => ({
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
  form.value.customer_id && form.value.vehicle_group && dateRange.value.start && dateRange.value.end
)

const disabledDates = computed(() => {
  if (availableDates.value.length === 0) return []
  const available = new Set(availableDates.value)
  const disabled = []
  const today = new Date()
  for (let i = 0; i < 90; i++) {
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

function statusLabel(s) {
  return { pending: 'Bekliyor', assigned: 'Onaylandı', cancelled: 'İptal' }[s] || s
}

function groupLabel(g) {
  return { economy: 'Ekonomi', mid: 'Orta Sınıf', suv: 'SUV' }[g] || g
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
  try {
    const res = await axios.get('/api/availability/', {
      params: { branch: branchId.value, group: form.value.vehicle_group }
    })
    availableDates.value = res.data.available_dates
  } finally {
    availabilityLoading.value = false
  }
}

function toLocalDateStr(date) {
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}

async function openCreate({ startDate = null, endDate = null, vehicleGroup = '' } = {}) {
  form.value = { customer_id: '', vehicle_group: vehicleGroup, branch: '', return_branch: '' }
  dateRange.value = { start: null, end: null }
  availableDates.value = []
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
      start_date: toLocalDateStr(dateRange.value.start),
      end_date: toLocalDateStr(dateRange.value.end),
      customer_id: form.value.customer_id,
      return_branch: differentReturn.value && form.value.return_branch ? form.value.return_branch : null,
    })
    formSuccess.value = 'Rezervasyon oluşturuldu.'
    const res = await axios.get('/api/reservations/')
    reservations.value = res.data
    form.value = { customer_id: '', vehicle_group: '' }
    dateRange.value = { start: null, end: null }
    availableDates.value = []
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
</script>

<style scoped>
.content { padding: 32px 40px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-left { display: flex; align-items: center; gap: 12px; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0; }
.count-badge { padding: 3px 10px; background: #f1f5f9; color: #64748b; border-radius: 50px; font-size: 12px; font-weight: 600; }
.view-select { padding: 7px 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; color: #475569; outline: none; cursor: pointer; }
.btn-add { padding: 8px 18px; background: #6366f1; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-add:hover { background: #4f46e5; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
td { border-top: 1px solid #f1f5f9; color: #374151; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
td:nth-child(1), th:nth-child(1), td:nth-child(2), th:nth-child(2), td:nth-child(3), th:nth-child(3), td:nth-child(4), th:nth-child(4), td:nth-child(5), th:nth-child(5), td:nth-child(6), th:nth-child(6), td:nth-child(7), th:nth-child(7) { text-align: center; }
.id { font-family: monospace; font-weight: 600; color: #1e293b; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 200; display: flex; align-items: center; justify-content: center; }
.modal { background: white; border-radius: 12px; padding: 32px; width: 460px; max-height: 85vh; overflow: visible; box-shadow: 0 8px 32px rgba(0,0,0,0.12); display: flex; flex-direction: column; gap: 16px; }
.modal h3 { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; }
.field select { padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; background: white; color: #1e293b; }
.field select:focus { border-color: #6366f1; }
.customer-search { position: relative; }
.customer-input { width: 100%; padding: 10px 36px 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; box-sizing: border-box; color: #1e293b; }
.customer-input:focus { border-color: #6366f1; }
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
.btn-cancel-modal { padding: 8px 16px; background: white; color: #64748b; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-size: 14px; }
.btn-save { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-save:hover:not(:disabled) { background: #4f46e5; }
.btn-save:disabled { background: #a5b4fc; cursor: not-allowed; }
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
.btn-dots { background: none; border: 1px solid #e2e8f0; border-radius: 6px; padding: 2px 8px; font-size: 16px; color: #64748b; cursor: pointer; line-height: 1.4; }
.btn-dots:hover { background: #f1f5f9; }
.action-dropdown { position: absolute; right: 0; top: calc(100% + 4px); background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); z-index: 50; min-width: 110px; overflow: hidden; }
.action-dropdown button, .action-dropdown .no-action { display: block; width: 100%; padding: 9px 14px; font-size: 13px; text-align: left; border: none; background: none; cursor: pointer; }
.action-dropdown button.danger { color: #dc2626; }
.action-dropdown button.danger:hover { background: #fef2f2; }
.no-action { color: #94a3b8; cursor: default; }
</style>

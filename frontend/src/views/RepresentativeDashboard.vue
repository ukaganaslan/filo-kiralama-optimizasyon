<template>
  <div class="content">
    <div class="section-header">
      <div class="header-left">
        <h2>Şube Rezervasyonları</h2>
        <span class="count-badge">{{ reservations.length }} rezervasyon</span>
      </div>
      <button class="btn-add" @click="openCreate">+ Rezervasyon Oluştur</button>
    </div>

    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Müşteri</th>
          <th>Grup</th>
          <th>Başlangıç</th>
          <th>Bitiş</th>
          <th>Durum</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in reservations" :key="r.id">
          <td class="id">{{ r.reservation_id }}</td>
          <td>{{ r.customer_username }}</td>
          <td>{{ r.vehicle_group }}</td>
          <td>{{ r.start_date }}</td>
          <td>{{ r.end_date }}</td>
          <td><span :class="'badge badge-' + r.status">{{ statusLabel(r.status) }}</span></td>
        </tr>
        <tr v-if="reservations.length === 0">
          <td colspan="6" class="empty">Bu şubeye ait rezervasyon bulunamadı.</td>
        </tr>
      </tbody>
    </table>

  </div>

  <div v-if="createModal" class="modal-overlay" @click.self="createModal = false">
    <div class="modal">
      <h3>Müşteri Adına Rezervasyon</h3>

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
          <button v-if="selectedCustomer" class="customer-clear" @click="clearCustomer">✕</button>
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

const reservations = ref([])
const customers = ref([])
const branchId = ref(null)

const createModal = ref(false)
const form = ref({ customer_id: '', vehicle_group: '' })
const dateRange = ref({ start: null, end: null })
const availableDates = ref([])
const availabilityLoading = ref(false)
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
}
onMounted(() => document.addEventListener('click', handleOutsideClick))
onUnmounted(() => document.removeEventListener('click', handleOutsideClick))

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
  const [rezRes, profileRes, usersRes] = await Promise.all([
    axios.get('http://127.0.0.1:8000/api/reservations/'),
    axios.get('http://127.0.0.1:8000/api/profile/'),
    axios.get('http://127.0.0.1:8000/api/users/'),
  ])
  reservations.value = rezRes.data
  branchId.value = profileRes.data.branch_id
  customers.value = usersRes.data
})

function statusLabel(s) {
  return { pending: 'Bekliyor', assigned: 'Atandı', cancelled: 'İptal' }[s] || s
}

async function fetchAvailability() {
  if (!branchId.value || !form.value.vehicle_group) return
  availabilityLoading.value = true
  availableDates.value = []
  dateRange.value = { start: null, end: null }
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/availability/', {
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

function openCreate() {
  form.value = { customer_id: '', vehicle_group: '' }
  dateRange.value = { start: null, end: null }
  availableDates.value = []
  formError.value = ''
  formSuccess.value = ''
  customerQuery.value = ''
  selectedCustomer.value = ''
  customerDropdownOpen.value = false
  createModal.value = true
}

async function handleCreate() {
  formError.value = ''
  formSuccess.value = ''
  try {
    await axios.post('http://127.0.0.1:8000/api/reservations/', {
      branch: branchId.value,
      vehicle_group: form.value.vehicle_group,
      start_date: toLocalDateStr(dateRange.value.start),
      end_date: toLocalDateStr(dateRange.value.end),
      customer_id: form.value.customer_id,
    })
    formSuccess.value = 'Rezervasyon oluşturuldu.'
    const res = await axios.get('http://127.0.0.1:8000/api/reservations/')
    reservations.value = res.data
    form.value = { customer_id: '', vehicle_group: '' }
    dateRange.value = { start: null, end: null }
    availableDates.value = []
  } catch {
    formError.value = 'Rezervasyon oluşturulamadı.'
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
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
td:nth-child(1), th:nth-child(1), td:nth-child(2), th:nth-child(2), td:nth-child(3), th:nth-child(3), td:nth-child(4), th:nth-child(4), td:nth-child(5), th:nth-child(5), td:nth-child(6), th:nth-child(6) { text-align: center; }
.id { font-family: monospace; font-weight: 600; color: #1e293b; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
.badge { padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: 600; }
.badge-pending { background: #fef3c7; color: #92400e; }
.badge-assigned { background: #d1fae5; color: #065f46; }
.badge-cancelled { background: #fee2e2; color: #991b1b; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 200; display: flex; align-items: center; justify-content: center; }
.modal { background: white; border-radius: 12px; padding: 32px; width: 460px; max-height: 85vh; overflow-y: auto; box-shadow: 0 8px 32px rgba(0,0,0,0.12); display: flex; flex-direction: column; gap: 16px; }
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
.customer-dropdown { position: absolute; top: calc(100% + 4px); left: 0; right: 0; background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); z-index: 50; overflow: hidden; }
.customer-option { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; cursor: pointer; }
.customer-option:hover { background: #f1f5f9; }
.customer-name { font-size: 14px; color: #1e293b; font-weight: 500; }
.customer-username { font-size: 12px; color: #94a3b8; }
.customer-empty { padding: 12px 14px; font-size: 14px; color: #94a3b8; }
.calendar-section { display: flex; flex-direction: column; gap: 8px; }
.calendar-section label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; }
.loading-hint { font-size: 13px; color: #94a3b8; }
.no-avail { font-size: 13px; color: #dc2626; }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 4px; }
.btn-cancel-modal { padding: 8px 16px; background: white; color: #64748b; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-size: 14px; }
.btn-save { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-save:hover:not(:disabled) { background: #4f46e5; }
.btn-save:disabled { background: #a5b4fc; cursor: not-allowed; }
.error { color: #dc2626; font-size: 13px; margin: 0; }
.success { color: #16a34a; font-size: 13px; margin: 0; }
</style>

<template>
  <div class="page">
    <div class="dashboard-summary">
      <h2 class="summary-greeting">Merhaba {{ auth.username }}</h2>

      <div v-if="upcomingReservation" class="upcoming-card">
        <div class="upcoming-header">
          <span class="upcoming-label">Yaklaşan Rezervasyonun</span>
          <span :class="'badge badge-' + upcomingReservation.current_status">{{ statusText(upcomingReservation.current_status) }}</span>
        </div>
        <div class="upcoming-vehicle">
          <template v-if="upcomingReservation.assigned_vehicle_info">
            {{ upcomingReservation.assigned_vehicle_info.brand }} {{ upcomingReservation.assigned_vehicle_info.model }} · {{ upcomingReservation.assigned_vehicle_info.plate }}
          </template>
          <template v-else>
            {{ groupLabel(upcomingReservation.vehicle_group) }}
          </template>
        </div>
        <div class="upcoming-details">
          <span>{{ upcomingReservation.branch_title }}</span>
          <span class="upcoming-dot">·</span>
          <span>{{ upcomingReservation.start_date }} → {{ upcomingReservation.end_date }}</span>
        </div>
      </div>
      <div v-else class="upcoming-empty">
        Aktif rezervasyonunuz bulunmuyor.
      </div>
    </div>

    <div class="wizard">
      <h2 class="wizard-title">Yeni Rezervasyon</h2>

      <!-- Step Bar -->
      <div class="step-bar">
        <template v-for="(label, i) in stepLabels" :key="i">
          <div
            class="step-node"
            :class="{ completed: currentStep > i + 1, active: currentStep === i + 1, clickable: currentStep > i + 1 && !formSuccess }"
            @click="goToStep(i + 1)"
          >
            <div class="step-circle">
              <svg v-if="currentStep > i + 1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 6L9 17l-5-5"/>
              </svg>
              <span v-else>{{ i + 1 }}</span>
            </div>
            <span class="step-label">{{ label }}</span>
          </div>
          <div v-if="i < stepLabels.length - 1" class="step-connector" :class="{ done: currentStep > i + 1 }"></div>
        </template>
      </div>

      <!-- Step Content -->
      <transition :name="transitionName" mode="out-in">

        <!-- Step 1: Lokasyon -->
        <div v-if="currentStep === 1" key="step1" class="step-card">
          <div class="card-title">
            <div>
              <div class="card-title-text">Lokasyon</div>
              <div class="card-title-sub">Aracı teslim alacağınız şubeyi seçin</div>
            </div>
          </div>

          <div class="location-grid">
            <div class="loc-field">
              <div class="loc-label">
                <span class="loc-dot pickup"></span>
                <span>Alış Yeri</span>
              </div>
              <select v-model="form.branch" @change="onPickupChange" :class="{ filled: form.branch }">
                <option value="" disabled>Şube seçin...</option>
                <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.title || b.name }}</option>
              </select>
            </div>

            <div class="loc-arrow">→</div>

            <div class="loc-field">
              <div class="loc-label">
                <span class="loc-dot" :class="{ active: differentReturn }"></span>
                <span>İade Yeri</span>
              </div>
              <div v-if="!differentReturn" class="same-loc-btn" @click="differentReturn = true">
                Alış yeriyle aynı
                <span class="change-link">Değiştir</span>
              </div>
              <select v-else v-model="form.return_branch" @change="fetchTransferCost" :class="{ filled: form.return_branch }">
                <option value="" disabled>Şube seçin...</option>
                <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.title || b.name }}</option>
              </select>
            </div>
          </div>

          <div v-if="transferCost !== null && differentReturn" class="transfer-notice" :class="{ free: transferCost === 0 }">
            <span class="notice-icon">{{ transferCost === 0 ? '✅' : '💸' }}</span>
            {{ transferCost > 0 ? `Transfer ücreti: ${transferCost} ₺` : 'Bu iade noktası için transfer ücreti yok' }}
          </div>
        </div>

        <!-- Step 2: Araç Grubu -->
        <div v-else-if="currentStep === 2" key="step2" class="step-card">
          <div class="card-title">
            <div>
              <div class="card-title-text">Araç Grubu</div>
              <div class="card-title-sub">Size uygun araç kategorisini seçin</div>
            </div>
          </div>

          <div class="group-list">
            <button
              v-for="g in groups"
              :key="g.value"
              class="group-card"
              :class="{ selected: form.vehicle_group === g.value }"
              @click="selectGroup(g.value)"
            >
              <span class="group-emoji">{{ g.emoji }}</span>
              <div class="group-info">
                <div class="group-name">{{ g.label }}</div>
                <div class="group-desc">{{ g.desc }}</div>
              </div>
              <div class="group-check-circle" :class="{ visible: form.vehicle_group === g.value }">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 6L9 17l-5-5"/>
                </svg>
              </div>
            </button>
          </div>
        </div>

        <!-- Step 3: Tarih -->
        <div v-else-if="currentStep === 3" key="step3" class="step-card">
          <div class="card-title">
            <div>
              <div class="card-title-text">Tarih Aralığı</div>
              <div class="card-title-sub">Kiralama başlangıç ve bitiş tarihini seçin</div>
            </div>
          </div>

          <div v-if="availabilityLoading" class="loading-state">
            <div class="loading-spinner"></div>
            <span>Müsait günler yükleniyor...</span>
          </div>

          <template v-else-if="availableDates.length > 0">
            <p class="date-hint">Açık günler müsait, gri günler dolu.</p>
            <VDatePicker
              v-model.range="dateRange"
              :disabled-dates="disabledDates"
              :min-date="new Date()"
              color="indigo"
              is-expanded
              :columns = 2
            />
          </template>

          <div v-else class="no-avail">
            <i class="pi pi-exclamation-triangle"></i> Bu şube ve grupta müsait gün bulunmuyor.
          </div>
        </div>

        <!-- Step 4: Fatura -->
        <div v-else-if="currentStep === 4" key="step4" class="step-card">
          <div class="card-title">
            <div>
              <div class="card-title-text">Fatura Bilgileri</div>
              <div class="card-title-sub">İsteğe bağlı, kayıt için kullanılır</div>
            </div>
          </div>

          <div class="billing-grid">
            <div class="loc-field">
              <div class="loc-label"><span>Fatura Tipi</span></div>
              <select v-model="form.billing_type" :class="{ filled: form.billing_type }">
                <option value="bireysel">Bireysel</option>
                <option value="kurumsal">Kurumsal</option>
              </select>
            </div>
            <div class="loc-field">
              <div class="loc-label"><span>Telefon</span></div>
              <input v-model="form.billing_phone" type="text" placeholder="Telefon" />
            </div>

            <template v-if="form.billing_type === 'kurumsal'">
              <div class="loc-field">
                <div class="loc-label"><span>Firma Unvanı</span></div>
                <input v-model="form.billing_name" type="text" placeholder="Firma Unvanı" />
              </div>
              <div class="loc-field">
                <div class="loc-label"><span>Vergi Dairesi</span></div>
                <input v-model="form.billing_tax_office" type="text" placeholder="Vergi Dairesi" />
              </div>
              <div class="loc-field">
                <div class="loc-label"><span>Vergi Kimlik No</span></div>
                <input v-model="form.billing_tax_no" type="text" maxlength="10" placeholder="10 haneli VKN" />
              </div>
            </template>
            <template v-else>
              <div class="loc-field">
                <div class="loc-label"><span>Ad Soyad</span></div>
                <input v-model="form.billing_name" type="text" placeholder="Ad Soyad" />
              </div>
              <div class="loc-field">
                <div class="loc-label"><span>TC Kimlik No</span></div>
                <input v-model="form.billing_tckn" type="text" maxlength="11" placeholder="11 haneli TCKN" />
              </div>
            </template>

            <div class="loc-field loc-field--full">
              <div class="loc-label"><span>Fatura Adresi</span></div>
              <textarea v-model="form.billing_address" rows="2" placeholder="Fatura adresi"></textarea>
            </div>
            <div class="loc-field">
              <div class="loc-label"><span>İl</span></div>
              <select v-model="form.billing_city" :class="{ filled: form.billing_city }" @change="form.billing_district = ''">
                <option value="" disabled>İl seçin</option>
                <option v-for="il in iller" :key="il" :value="il">{{ il }}</option>
              </select>
            </div>
            <div class="loc-field">
              <div class="loc-label"><span>İlçe</span></div>
              <select v-model="form.billing_district" :class="{ filled: form.billing_district }" :disabled="!form.billing_city">
                <option value="" disabled>İlçe seçin</option>
                <option v-for="ilce in ilceler" :key="ilce" :value="ilce">{{ ilce }}</option>
              </select>
            </div>
            <div class="loc-field">
              <div class="loc-label"><span>Mahalle</span></div>
              <input v-model="form.billing_neighborhood" type="text" placeholder="Mahalle" />
            </div>
          </div>
        </div>

        <!-- Step 5: Onay -->
        <div v-else-if="currentStep === 5" key="step5" class="step-card">
          <div class="card-title">
            <div>
              <div class="card-title-text">Rezervasyon Özeti</div>
              <div class="card-title-sub">Bilgileri kontrol edip onaylayın</div>
            </div>
          </div>

          <div class="summary-grid">
            <div class="summary-item">
              <div class="summary-key">Alış Şubesi</div>
              <div class="summary-val">{{ branchName(form.branch) }}</div>
            </div>
            <div class="summary-item">
              <div class="summary-key">İade Şubesi</div>
              <div class="summary-val">{{ differentReturn && form.return_branch ? branchName(form.return_branch) : branchName(form.branch) }}</div>
            </div>
            <div class="summary-item">
              <div class="summary-key">Araç Grubu</div>
              <div class="summary-val">{{ groupLabel(form.vehicle_group) }}</div>
            </div>
            <div class="summary-item">
              <div class="summary-key">Başlangıç</div>
              <div class="summary-val">{{ toLocalDateStr(dateRange.start) }}</div>
            </div>
            <div class="summary-item">
              <div class="summary-key">Bitiş</div>
              <div class="summary-val">{{ toLocalDateStr(dateRange.end) }}</div>
            </div>
            <div v-if="transferCost !== null && differentReturn" class="summary-item">
              <div class="summary-key">Transfer Ücreti</div>
              <div class="summary-val" :class="{ 'val-free': transferCost === 0 }">
                {{ transferCost === 0 ? 'Ücretsiz' : `${transferCost} ₺` }}
              </div>
            </div>
            <div v-if="totalPrice !== null" class="summary-item summary-item--price">
              <div class="summary-key">Toplam Ücret</div>
              <div class="summary-val summary-price">{{ totalPrice.toLocaleString('tr-TR') }} ₺</div>
            </div>
          </div>
        </div>

        <!-- Step 6: Ödeme -->
        <div v-else-if="currentStep === 6" key="step6" class="step-card">
          <div class="card-title">
            <div>
              <div class="card-title-text">Ödeme</div>
              <div class="card-title-sub">Demo ödeme ekranı</div>
            </div>
          </div>

          <MockPaymentForm :amount="totalPrice" @confirmed="handlePaymentConfirmed" />

          <p v-if="formError" class="form-error">{{ formError }}</p>
          <p v-if="formSuccess" class="form-success">{{ formSuccess }}</p>
        </div>

      </transition>

      <!-- Navigation -->
      <div class="step-nav" :class="{ 'nav-start': currentStep === 1 }">
        <button v-if="currentStep > 1" class="btn-back" @click="prevStep">
          ← Geri
        </button>
        <button
          v-if="currentStep < 6"
          class="btn-next"
          :disabled="!canAdvance"
          @click="nextStep"
        >
          İleri →
        </button>
        <button
          v-if="formSuccess" class="btn-new" @click="resetForm">
          Yeni Rezervasyon
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { ILLER, getIlceler } from '../utils/address'
import MockPaymentForm from '../components/MockPaymentForm.vue'

const auth = useAuthStore()
const iller = ILLER

const currentStep = ref(1)
const direction = ref('forward')
const stepLabels = ['Lokasyon', 'Araç Grubu', 'Tarih', 'Fatura', 'Özet Onay', 'Ödeme']

const branches = ref([])
const availableDates = ref([])
const availabilityLoading = ref(false)
const formError = ref('')
const formSuccess = ref('')
const form = ref({
  branch: '', vehicle_group: '', return_branch: '',
  billing_type: 'bireysel', billing_name: '', billing_tckn: '', billing_tax_office: '', billing_tax_no: '',
  billing_address: '', billing_neighborhood: '', billing_district: '', billing_city: '', billing_phone: '',
})
const paid = ref(false)
const dateRange = ref({ start: null, end: null })
const differentReturn = ref(false)
const transferCost = ref(null)
const dailyPrices = ref([])
const reservations = ref([])
const ilceler = computed(() => getIlceler(form.value.billing_city))

const totalPrice = computed(() => {
  if (!dateRange.value.start || !dateRange.value.end || !dailyPrices.value.length) return null
  const priceMap = {}
  dailyPrices.value.forEach(p => { priceMap[p.date] = Number(p.price_per_day) })
  const start = new Date(dateRange.value.start)
  const end = new Date(dateRange.value.end)
  let total = 0
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    const key = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
    total += priceMap[key] || 0
  }
  return total
})

const groups = [
  { value: 'economy', label: 'Ekonomi', desc: 'Şehir içi, yakıt dostu' },
  { value: 'mid',     label: 'Orta Sınıf', desc: 'Konfor ve performans' },
  { value: 'suv',     label: 'SUV', desc: 'Geniş, güçlü, her arazi' },
]

const transitionName = computed(() => direction.value === 'forward' ? 'step-fwd' : 'step-back')

const canAdvance = computed(() => {
  if (currentStep.value === 1) return !!form.value.branch
  if (currentStep.value === 2) return !!form.value.vehicle_group
  if (currentStep.value === 3) return !!(dateRange.value.start && dateRange.value.end)
  if (currentStep.value === 4) return true
  if (currentStep.value === 5) return  true 
  return false
})

const disabledDates = computed(() => {
  if (!availableDates.value.length) return []
  const available = new Set(availableDates.value)
  const disabled = []
  const today = new Date()
  for (let i = 0; i < 90; i++) {
    const d = new Date(today)
    d.setDate(today.getDate() + i)
    const str = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
    if (!available.has(str)) disabled.push(new Date(d))
  }
  return disabled
})

const upcomingReservation = computed(() => {
  const upcoming = reservations.value
    .filter(r => r.current_status === 'pending' || r.current_status === 'assigned')
    .sort((a, b) => new Date(a.start_date) - new Date(b.start_date))
  return upcoming[0] || null
})

onMounted(async () => {
  const res = await axios.get('/api/branches/')
  const res2 = await axios.get('/api/reservations/')
  const res3 = await axios.get('/api/profile/')
  branches.value = res.data
  reservations.value = res2.data
  form.value.billing_type = res3.data.billing_type || 'bireysel'
  form.value.billing_name = res3.data.billing_name || res3.data.full_name || ''
  form.value.billing_tckn = res3.data.billing_tckn || ''
  form.value.billing_tax_office = res3.data.billing_tax_office || ''
  form.value.billing_tax_no = res3.data.billing_tax_no || ''
  form.value.billing_address = res3.data.billing_address || ''
  form.value.billing_neighborhood = res3.data.billing_neighborhood || ''
  form.value.billing_district = res3.data.billing_district || ''
  form.value.billing_city = res3.data.billing_city || ''
  form.value.billing_phone = res3.data.billing_phone || res3.data.phone || ''
})

function branchName(id) {
  const b = branches.value.find(b => b.id === id)
  return b ? (b.title || b.name) : '—'
}
function groupLabel(v) {
  return groups.find(g => g.value === v)?.label || v
}

function statusText(status) {
  const labels = {
    pending: 'Bekliyor',
    assigned: 'Onaylandı',
    active: 'Kirada',
    completed: 'Tamamlandı',
    cancelled: 'İptal',
  }
  return labels[status] || status
}

function nextStep() {
  if (!canAdvance.value) return
  direction.value = 'forward'
  currentStep.value++
}
function prevStep() {
  direction.value = 'back'
  currentStep.value--
}
function goToStep(n) {
  if (n >= currentStep.value || formSuccess.value) return
  direction.value = 'back'
  currentStep.value = n
}

function selectGroup(val) {
  form.value.vehicle_group = val
  fetchAvailability()
}

function onPickupChange() {
  form.value.return_branch = ''
  transferCost.value = null
  fetchAvailability()
}

async function fetchAvailability() {
  if (!form.value.branch || !form.value.vehicle_group) return
  availabilityLoading.value = true
  availableDates.value = []
  dateRange.value = { start: null, end: null }
  try {
    const [availRes, priceRes] = await Promise.all([
      axios.get('/api/availability/', { params: { branch: form.value.branch, group: form.value.vehicle_group } }),
      axios.get('/api/daily-prices/', { params: { group: form.value.vehicle_group } }),
    ])
    availableDates.value = availRes.data.available_dates
    dailyPrices.value = priceRes.data
  } finally {
    availabilityLoading.value = false
  }
}

async function fetchTransferCost() {
  if (!form.value.branch || !form.value.return_branch) { transferCost.value = null; return }
  const res = await axios.get('/api/transfer-cost/', {
    params: { from: form.value.branch, to: form.value.return_branch }
  })
  transferCost.value = res.data.cost
}

function toLocalDateStr(date) {
  if (!date) return '—'
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}

async function handlePaymentConfirmed() {
  paid.value = true
  await handleCreate()
}

async function handleCreate() {
  formError.value = ''
  formSuccess.value = ''
  try {
    await axios.post('/api/reservations/', {
      branch: form.value.branch,
      vehicle_group: form.value.vehicle_group,
      start_date: toLocalDateStr(dateRange.value.start),
      end_date: toLocalDateStr(dateRange.value.end),
      return_branch: differentReturn.value && form.value.return_branch ? form.value.return_branch : null,
      billing_type: form.value.billing_type,
      billing_name: form.value.billing_name,
      billing_tckn: form.value.billing_tckn,
      billing_tax_office: form.value.billing_tax_office,
      billing_tax_no: form.value.billing_tax_no,
      billing_address: form.value.billing_address,
      billing_neighborhood: form.value.billing_neighborhood,
      billing_district: form.value.billing_district,
      billing_city: form.value.billing_city,
      billing_phone: form.value.billing_phone,
      paid: paid.value,
    })
    formSuccess.value = 'Rezervasyon oluşturuldu! Onay bekleniyor.'
  } catch (e) {
    const msg = e.response?.data?.non_field_errors?.[0]
    formError.value = msg || 'Rezervasyon oluşturulamadı.'
  }
}

function resetForm() {
  currentStep.value = 1
  direction.value = 'forward'
  form.value = {
    branch: '', vehicle_group: '', return_branch: '',
    billing_type: form.value.billing_type,
    billing_name: form.value.billing_name,
    billing_tckn: form.value.billing_tckn,
    billing_tax_office: form.value.billing_tax_office,
    billing_tax_no: form.value.billing_tax_no,
    billing_address: form.value.billing_address,
    billing_neighborhood: form.value.billing_neighborhood,
    billing_district: form.value.billing_district,
    billing_city: form.value.billing_city,
    billing_phone: form.value.billing_phone,
    
  }
  paid.value = false
  dateRange.value = { start: null, end: null }
  availableDates.value = []
  differentReturn.value = false
  transferCost.value = null
  formError.value = ''
  formSuccess.value = ''
}
</script>

<style scoped>
.page { background: #F8FAFC; min-height: 100vh; }

/* ── Dashboard Özeti ── */
.dashboard-summary {
  max-width: 620px;
  margin: 0 auto;
  padding: 40px 24px 0;
}

.summary-greeting {
  font-size: 20px;
  font-weight: 800;
  color: #111827;
  margin: 0 0 16px;
}

.upcoming-card, .upcoming-empty {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 20px rgba(0,0,0,0.05);
  border: 1px solid rgba(226,232,240,0.8);
  margin-bottom: 16px;
}

.upcoming-empty { color: #64748B; font-size: 14px; }

.upcoming-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.upcoming-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #64748B;
}

.upcoming-vehicle {
  font-size: 16px;
  font-weight: 700;
  color: #1B1063;
  margin-bottom: 6px;
}

.upcoming-details {
  font-size: 13px;
  color: #64748B;
  display: flex;
  align-items: center;
  gap: 6px;
}

.upcoming-dot { color: #cbd5e1; }

.wizard {
  max-width: 620px;
  margin: 0 auto;
  padding: 40px 24px 80px;
}

.wizard-title {
  font-size: 20px;
  font-weight: 800;
  color: #111827;
  margin: 0 0 24px;
}

/* ── Step Bar ── */
.step-bar {
  display: flex;
  align-items: flex-start;
  margin-bottom: 36px;
  padding: 0 8px;
}

.step-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.step-circle {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 800;
  transition: all 0.3s ease;
  background: white;
  border: 2px solid #d1d5db;
  color: #9ca3af;
}

.step-circle svg { width: 18px; height: 18px; }

.step-node.active .step-circle {
  border: 2.5px solid #1B1063;
  color: #1B1063;
  box-shadow: 0 0 0 6px rgba(27,16,99,0.1);
}

.step-node.completed .step-circle {
  background: #1B1063;
  border-color: #1B1063;
  color: white;
  box-shadow: 0 0 0 6px rgba(27,16,99,0.1);
}

.step-label {
  font-size: 11px;
  font-weight: 600;
  color: #9ca3af;
  white-space: nowrap;
  text-align: center;
  transition: color 0.3s;
}
.step-node.active .step-label   { color: #1B1063; font-weight: 700; }
.step-node.completed .step-label { color: #64748b; }
.step-node.clickable { cursor: pointer; }
.step-node.clickable:hover .step-circle { box-shadow: 0 0 0 6px rgba(27,16,99,0.18); }
.step-node.clickable:hover .step-label { color: #1B1063; }

.step-connector {
  flex: 1;
  height: 2px;
  background: #e5e7eb;
  margin-top: 22px;
  transition: background 0.3s ease;
}
.step-connector.done { background: #1B1063; }

/* ── Step Card ── */
.step-card {
  background: white;
  border-radius: 20px;
  padding: 36px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 20px rgba(0,0,0,0.05);
  border: 1px solid rgba(226,232,240,0.8);
  min-height: 300px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
}
.card-title-icon { font-size: 26px; flex-shrink: 0; }
.card-title-text { font-size: 18px; font-weight: 800; color: #111827; line-height: 1.2; }
.card-title-sub { font-size: 13px; color: #64748B; margin-top: 2px; }

/* ── Step 1: Lokasyon ── */
.location-grid {
  display: flex;
  align-items: flex-end;
  gap: 16px;
}

.loc-field { flex: 1; display: flex; flex-direction: column; gap: 8px; }

.loc-label {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 11px;
  font-weight: 700;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.loc-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #d1d5db;
  flex-shrink: 0;
  transition: background 0.2s;
}
.loc-dot.pickup { background: #1B1063; }
.loc-dot.active { background: #F59E0B; }

.loc-field select,
.loc-field input,
.loc-field textarea {
  padding: 12px 16px;
  border: 1.5px solid #e2e8f0;
  border-radius: 11px;
  font-size: 14px;
  color: #94a3b8;
  outline: none;
  background: #fafafa;
  transition: border 0.2s, color 0.2s, box-shadow 0.2s;
  cursor: pointer;
  font-family: inherit;
}
.loc-field input,
.loc-field textarea {
  color: #111827;
  cursor: text;
  resize: none;
}
.loc-field select.filled { color: #111827; background: white; border-color: #c4beff; }
.loc-field select:focus,
.loc-field input:focus,
.loc-field textarea:focus { border-color: #1B1063; background: white; box-shadow: 0 0 0 3px rgba(27,16,99,0.08); }

/* ── Step 4: Fatura ── */
.billing-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.loc-field--full { grid-column: 1 / -1; }

.same-loc-btn {
  padding: 12px 16px;
  border: 1.5px dashed #e2e8f0;
  border-radius: 11px;
  font-size: 13.5px;
  color: #94a3b8;
  cursor: pointer;
  background: #fafafa;
  transition: border-color 0.2s;
}
.same-loc-btn:hover { border-color: #1B1063; }

.loc-arrow { font-size: 18px; color: #d1d5db; flex-shrink: 0; padding-bottom: 14px; }
.change-link { color: #1B1063; font-weight: 700; margin-left: 4px; }

.transfer-notice {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fff7ed;
  border: 1px solid #fed7aa;
  border-radius: 10px;
  font-size: 13.5px;
  color: #92400e;
  font-weight: 500;
}
.transfer-notice.free { background: #f0fdf4; border-color: #bbf7d0; color: #166534; }
.notice-icon { font-size: 16px; flex-shrink: 0; }

/* ── Step 2: Araç Grubu ── */
.group-list { display: flex; flex-direction: column; gap: 12px; }

.group-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  background: white;
  border: 1.5px solid #e5e7eb;
  border-radius: 14px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
  width: 100%;
}
.group-card:hover { border-color: #9b8ff5; background: #faf9ff; transform: translateX(2px); }
.group-card.selected { border-color: #1B1063; background: #edeaff; box-shadow: 0 0 0 4px rgba(27,16,99,0.08); }

.group-emoji { font-size: 30px; flex-shrink: 0; }
.group-info { flex: 1; }
.group-name { font-size: 15px; font-weight: 700; color: #111827; }
.group-desc { font-size: 12.5px; color: #64748B; margin-top: 2px; }

.group-check-circle {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #1B1063;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  opacity: 0;
  transform: scale(0.6);
  transition: opacity 0.2s, transform 0.2s;
}
.group-check-circle.visible { opacity: 1; transform: scale(1); }
.group-check-circle svg { width: 14px; height: 14px; color: white; }

/* ── Step 3: Tarih ── */
.date-hint { font-size: 13px; color: #64748B; margin-bottom: 16px; }

.loading-state {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 40px 0;
  justify-content: center;
  color: #64748B;
  font-size: 14px;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2.5px solid #e2e8f0;
  border-top-color: #1B1063;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.no-avail {
  padding: 20px;
  background: #fff7ed;
  border-radius: 12px;
  color: #9a3412;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid #fcd34d;
}

/* ── Step 4: Onay ── */
.summary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 28px;
}

.summary-item {
  padding: 16px 18px;
  background: #F8FAFC;
  border-radius: 12px;
  border: 1px solid #f1f5f9;
}
.summary-key {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #94a3b8;
  margin-bottom: 6px;
}
.summary-val { font-size: 14px; font-weight: 700; color: #111827; }
.val-free { color: #16A34A; }
.summary-item--price { border-color: #c7d2fe; background: #eef2ff; }
.summary-price { font-size: 18px; color: #4f46e5; }

.form-error {
  color: #DC2626;
  font-size: 13px;
  background: #fff1f2;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid #fecdd3;
  margin-bottom: 16px;
}
.form-success {
  color: #16A34A;
  font-size: 13px;
  background: #f0fdf4;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid #bbf7d0;
  margin-bottom: 16px;
  font-weight: 600;
}

/* ── Navigation ── */
.step-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  gap: 12px;
}
.step-nav.nav-start { justify-content: flex-end; }

.btn-back {
  padding: 12px 24px;
  background: white;
  color: #64748b;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-back:hover { background: #F8FAFC; border-color: #cbd5e1; color: #111827; }

.btn-next, .btn-confirm, .btn-new {
  padding: 13px 32px;
  background: linear-gradient(135deg, #1B1063, #130d4a);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 14px rgba(27,16,99,0.3);
}
.btn-next:hover:not(:disabled), .btn-confirm:hover, .btn-new:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(27,16,99,0.4);
}
.btn-next:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  box-shadow: none;
  cursor: not-allowed;
  transform: none;
}
.btn-new {
  background: linear-gradient(135deg, #16A34A, #15803d);
  box-shadow: 0 4px 14px rgba(22,163,74,0.3);
}

/* ── Step Transitions ── */
.step-fwd-enter-active { transition: all 0.28s ease; }
.step-fwd-leave-active { transition: all 0.2s ease; }
.step-fwd-enter-from   { opacity: 0; transform: translateX(36px); }
.step-fwd-leave-to     { opacity: 0; transform: translateX(-36px); }

.step-back-enter-active { transition: all 0.28s ease; }
.step-back-leave-active { transition: all 0.2s ease; }
.step-back-enter-from   { opacity: 0; transform: translateX(-36px); }
.step-back-leave-to     { opacity: 0; transform: translateX(36px); }
</style>

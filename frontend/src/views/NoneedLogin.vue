<template>
  <div class="guest-layout">

    <!-- Header -->
    <div class="guest-header">
      <div class="brand">
        <div class="brand-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 17H3a2 2 0 01-2-2V9a2 2 0 012-2h2M17 17h2a2 2 0 002-2V9a2 2 0 00-2-2h-2"/>
            <rect x="5" y="7" width="14" height="10" rx="2"/>
            <circle cx="7.5" cy="17" r="1.5"/><circle cx="16.5" cy="17" r="1.5"/>
          </svg>
        </div>
        <span>FiloRent</span>
      </div>
      <div class="login-cta">
        <div class="login-cta-text">
          <span class="cta-title">Kullanıcı Girişi Yaparak</span>
          <span class="cta-sub">Rezervasyonlarınızı daha kolay yönetin</span>
        </div>
        <router-link to="/" class="login-cta-btn">Giriş Yap →</router-link>
      </div>
    </div>

    <div class="guest-body">

      <!-- SOL: Wizard -->
      <div class="wizard-panel">

        <div class="wizard-intro">
          <h2>Misafir Rezervasyonu</h2>
          <p>Hesap oluşturmadan araç kiralayın.</p>
        </div>

        <!-- Başarı Ekranı -->
        <div v-if="reservationCode" class="success-card">
          <div class="success-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 6L9 17l-5-5"/>
            </svg>
          </div>
          <h3>Rezervasyonunuz Alındı!</h3>
          <p class="success-sub">Rezervasyon kodunuzu saklayın. Durumu sorgulamak veya iptal etmek için bu kodu kullanın.</p>
          <div class="code-box" @click="copyCode" title="Kopyalamak için tıkla">{{ reservationCode }}</div>
          <p class="copy-hint" v-if="copied">Kopyalandı!</p>
          <div v-if="reservationPrice" class="price-box">
            Tahmini Tutar: <strong>{{ Number(reservationPrice).toLocaleString('tr-TR') }} ₺</strong>
          </div>
          <p class="code-hint">Bu kodu not edin veya ekran görüntüsü alın.</p>
          <button class="btn-new" @click="resetForm">Yeni Rezervasyon Oluştur</button>
        </div>

        <!-- Wizard Steps -->
        <template v-else>

          <!-- Step Bar -->
          <div class="step-bar">
            <template v-for="(label, i) in stepLabels" :key="i">
              <div
                class="step-node"
                :class="{ completed: currentStep > i + 1, active: currentStep === i + 1, clickable: currentStep > i + 1 }"
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
            <div v-if="currentStep === 1" key="s1" class="step-card">
              <div class="card-title">
                <div>
                  <div class="card-title-text">Lokasyon</div>
                  <div class="card-title-sub">Aracı teslim alacağınız şubeyi seçin</div>
                </div>
              </div>

              <div class="location-grid">
                <div class="loc-field">
                  <div class="loc-label">
                    <span class="loc-dot pickup"></span><span>Alış Yeri</span>
                  </div>
                  <select v-model="form.branch" @change="onPickupChange" :class="{ filled: form.branch }">
                    <option value="" disabled>Şube seçin...</option>
                    <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.title || b.name }}</option>
                  </select>
                </div>

                <div class="loc-arrow">→</div>

                <div class="loc-field">
                  <div class="loc-label">
                    <span class="loc-dot" :class="{ active: differentReturn }"></span><span>İade Yeri</span>
                  </div>
                  <div v-if="!differentReturn" class="same-loc-btn" @click="differentReturn = true">
                    Alış yeriyle aynı <span class="change-link">Değiştir</span>
                  </div>
                  <select v-else v-model="form.return_branch" @change="fetchTransferCost" :class="{ filled: form.return_branch }">
                    <option value="" disabled>Şube seçin...</option>
                    <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.title || b.name }}</option>
                  </select>
                </div>
              </div>

              <div v-if="transferCost !== null && differentReturn" class="transfer-notice" :class="{ free: transferCost === 0 }">
                <svg v-if="transferCost === 0" class="notice-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>
                <svg v-else class="notice-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 015 0c0 1.5-2.5 2-2.5 3.5M12 16.5h.01"/></svg>
                {{ transferCost > 0 ? `Transfer ücreti: ${transferCost} ₺` : 'Bu iade noktası için transfer ücreti yok' }}
              </div>
            </div>

        <!-- Step 2: Tarih -->
        <div v-else-if="currentStep === 2" key="step2" class="step-card">
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
            <p class="date-hint">Koyu renkli günler müsait, gri günler dolu.</p>
            <VDatePicker
              v-model.range="dateRange"
              :disabled-dates="disabledDates"
              :min-date="new Date()"
              :max-date="maxAvailabilityDate"
              color="indigo"
              is-expanded
              :columns = 2
            />
            <div class="time-grid">
              <div class="loc-field">
                <div class="loc-label"><span>Alış Saati</span></div>
                <input v-model="form.start_time" type="time" class="filled" />
              </div>
              <div class="loc-field">
                <div class="loc-label"><span>İade Saati</span></div>
                <input v-model="form.end_time" type="time" class="filled" />
              </div>
            </div>
          </template>

          <div v-else class="no-avail">
            <i class="pi pi-exclamation-triangle"></i> Bu şubede müsait gün bulunmuyor.
          </div>
        </div>

        <!-- Step 3: Araç Modeli -->
        <div v-else-if="currentStep === 3" key="step3" class="step-card">
          <div class="card-title">
            <div>
              <div class="card-title-text">Araç Modeli</div>
              <div class="card-title-sub">Bir marka/model seçin — stok kalmazsa aynı sınıftan başka bir araç size atanabilir</div>
            </div>
          </div>

          <div class="model-filters">
            <select v-model="modelFilterGroup" @change="fetchModels">
              <option value="">Tüm Sınıflar</option>
              <option v-for="g in CATEGORY_ORDER" :key="g" :value="g">{{ categoryLabel(g) }}</option>
            </select>
            <select v-model="modelFilterFuel" @change="fetchModels">
              <option value="">Tüm Yakıtlar</option>
              <option value="benzin">Benzin</option>
              <option value="dizel">Dizel</option>
              <option value="hibrit">Hibrit</option>
              <option value="elektrik">Elektrik</option>
            </select>
            <select v-model="modelFilterTransmission" @change="fetchModels">
              <option value="">Tüm Vitesler</option>
              <option value="manuel">Manuel</option>
              <option value="otomatik">Otomatik</option>
            </select>
          </div>

          <div v-if="modelsLoading" class="loading-state">
            <div class="loading-spinner"></div>
            <span>Araçlar yükleniyor...</span>
          </div>

          <div v-else-if="availableModels.length === 0" class="no-avail">
            <i class="pi pi-exclamation-triangle"></i> Bu tarih aralığında ve filtrelerde uygun araç bulunamadı.
          </div>

          <div v-else class="model-grid">
            <button
              v-for="m in availableModels"
              :key="m.id"
              class="model-card"
              :class="{ selected: form.preferred_vehicle_model === m.id }"
              @click="selectModel(m)"
            >
              <img v-if="m.image" :src="m.image" class="model-img" />
              <div v-else class="model-img model-img-empty" :style="{ background: CATEGORY_COLORS[m.group]?.bg }"></div>
              <div class="model-body">
                <div class="model-name">{{ m.brand }} {{ m.model }}</div>
                <div class="model-alt">ya da benzeri</div>
                <div class="model-badges">
                  <span class="model-badge" :style="{ background: CATEGORY_COLORS[m.group]?.bg, color: CATEGORY_COLORS[m.group]?.text }">{{ categoryLabel(m.group) }}</span>
                  <span class="model-badge">{{ m.fuel_type === 'benzin' ? 'Benzin' : m.fuel_type === 'dizel' ? 'Dizel' : m.fuel_type === 'hibrit' ? 'Hibrit' : 'Elektrik' }}</span>
                  <span class="model-badge">{{ m.transmission === 'otomatik' ? 'Otomatik' : 'Manuel' }}</span>
                </div>
                <div class="model-price" v-if="m.total_price">{{ Number(m.total_price).toLocaleString('tr-TR') }} ₺ <span class="model-price-sub">toplam</span></div>
              </div>
              <div class="model-check-circle" :class="{ visible: form.preferred_vehicle_model === m.id }">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 6L9 17l-5-5"/>
                </svg>
              </div>
            </button>
          </div>
        </div>

            <!-- Step 4: Bilgileriniz -->
            <div v-else-if="currentStep === 4" key="s4" class="step-card">
              <div class="card-title">
                <div class="card-title-icon"><i class="pi pi-user"></i></div>
                <div>
                  <div class="card-title-text">Bilgileriniz</div>
                  <div class="card-title-sub">İletişim bilgilerinizi girin ve ödeme ekranına devam edin.</div>
                </div>
              </div>

              <!-- Mini özet -->
              <div class="mini-summary">
                <div class="mini-item">
                  <span class="mini-key">Şube</span>
                  <span class="mini-val">{{ branchName(form.branch) }}</span>
                </div>
                <div class="mini-item">
                  <span class="mini-key">Araç Modeli</span>
                  <span class="mini-val">{{ selectedModel ? `${selectedModel.brand} ${selectedModel.model}` : groupLabel(form.vehicle_group) }}</span>
                </div>
                <div class="mini-item">
                  <span class="mini-key">Tarih</span>
                  <span class="mini-val">{{ toLocalDateStr(dateRange.start) }} {{ form.start_time }} → {{ toLocalDateStr(dateRange.end) }} {{ form.end_time }}</span>
                </div>
              </div>

              <div class="info-fields">
                <div class="info-field">
                  <label>Ad Soyad <span class="req">*</span></label>
                  <input v-model="guest.name" type="text" placeholder="Ahmet Yılmaz" />
                </div>
                <div class="info-field">
                  <label>Telefon <span class="req">*</span></label>
                  <input v-model="guest.phone" type="tel" placeholder="05XX XXX XX XX" />
                </div>
                <div class="info-field">
                  <label>E-posta <span class="req">*</span></label>
                  <input v-model="guest.email" type="email" placeholder="ahmet@email.com" />
                </div>
              </div>

              <div class="divider"></div>

              <div class="info-fields">
                <div class="info-field">
                  <label>Fatura Tipi <span class="req">*</span></label>
                  <select v-model="guest.billing_type">
                    <option value="bireysel">Bireysel</option>
                    <option value="kurumsal">Kurumsal</option>
                  </select>
                </div>

                <template v-if="guest.billing_type === 'kurumsal'">
                  <div class="info-field">
                    <label>Firma Unvanı <span class="req">*</span></label>
                    <input v-model="guest.billing_name" type="text" placeholder="Firma Unvanı" />
                  </div>
                  <div class="info-field">
                    <label>Vergi Dairesi <span class="req">*</span></label>
                    <input v-model="guest.billing_tax_office" type="text" placeholder="Vergi Dairesi" />
                  </div>
                  <div class="info-field">
                    <label>Vergi Kimlik No <span class="req">*</span></label>
                    <input v-model="guest.billing_tax_no" type="text" maxlength="10" placeholder="10 haneli VKN" />
                  </div>
                </template>
                <template v-else>
                  <div class="info-field">
                    <label>TC Kimlik No <span class="req">*</span></label>
                    <input v-model="guest.billing_tckn" type="text" maxlength="11" placeholder="11 haneli TCKN" />
                  </div>
                </template>

                <div class="info-field">
                  <label>Fatura Adresi <span class="req">*</span></label>
                  <input v-model="guest.billing_address" type="text" placeholder="Fatura adresi" />
                </div>
                <div class="info-field">
                  <label>İl <span class="req">*</span></label>
                  <select v-model="guest.billing_city" @change="guest.billing_district = ''">
                    <option value="" disabled>İl seçin</option>
                    <option v-for="il in iller" :key="il" :value="il">{{ il }}</option>
                  </select>
                </div>
                <div class="info-field">
                  <label>İlçe <span class="req">*</span></label>
                  <select v-model="guest.billing_district" :disabled="!guest.billing_city">
                    <option value="" disabled>İlçe seçin</option>
                    <option v-for="ilce in ilceler" :key="ilce" :value="ilce">{{ ilce }}</option>
                  </select>
                </div>
                <div class="info-field">
                  <label>Mahalle</label>
                  <input v-model="guest.billing_neighborhood" type="text" placeholder="Mahalle" />
                </div>
              </div>

              <p v-if="formError" class="form-error">{{ formError }}</p>
            </div>

            <!-- Step 5: Ödeme -->
            <div v-else-if="currentStep === 5" key="s5" class="step-card">
             <div class="card-title">
            <div>
              <div class="card-title-text">Ödeme</div>
              <div class="card-title-sub">Demo ödeme ekranı</div>
            </div>
          </div>
          
          <MockPaymentForm :amount="totalPrice" @confirmed="handlePaymentConfirmed" />

          <p v-if="formError" class="form-error">{{ formError }}</p>
        </div>

          </transition>

          <!-- Navigation -->
          <div class="step-nav" :class="{ 'nav-start': currentStep === 1 }">
            <button v-if="currentStep > 1" class="btn-back" @click="prevStep">← Geri</button>
            <button v-if="currentStep < 5" class="btn-next" :disabled="!canAdvance" @click="nextStep">İleri →</button>
          </div>

        </template>
      </div>

      <!-- SAĞ: Rezervasyon Sorgula -->
      <div class="query-panel">
        <div class="query-header">
          <div class="query-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </div>
          <div>
            <div class="query-title">Rezervasyon Sorgula</div>
            <div class="query-sub">Kodunuzla rezervasyonunuzu görüntüleyin veya iptal edin</div>
          </div>
        </div>

        <div class="q-field">
          <label>Rezervasyon Kodu</label>
          <input v-model="query.code" type="text" placeholder="3FA2B91C" maxlength="8" style="text-transform: uppercase" />
        </div>
        <button class="btn-query" @click="handleQuery">Sorgula →</button>

        <p v-if="queryError" class="q-error">{{ queryError }}</p>

        <div v-if="queryResult" class="query-result">
          <div class="result-row"><span class="rk">Ad</span><span class="rv">{{ queryResult.guest_name }}</span></div>
          <div class="result-row"><span class="rk">Şube</span><span class="rv">{{ queryResult.branch }}</span></div>
          <div class="result-row"><span class="rk">Grup</span><span class="rv">{{ groupLabel(queryResult.vehicle_group) }}</span></div>
          <div class="result-row"><span class="rk">Tarih</span><span class="rv">{{ queryResult.start_date }} → {{ queryResult.end_date }}</span></div>
          <div v-if="queryResult.total_price" class="result-row">
            <span class="rk">Tutar</span>
            <span class="rv">{{ Number(queryResult.total_price).toLocaleString('tr-TR') }} ₺</span>
          </div>
          <div class="result-row">
            <span class="rk">Durum</span>
            <span class="status-badge" :class="queryResult.status">{{ statusLabel(queryResult.status) }}</span>
          </div>

          <button class="btn-detail" @click="openDetail">Detayları Gör</button>

          <div v-if="queryResult.status !== 'cancelled'" class="cancel-area">
            <div class="q-field">
              <label>E-posta (doğrulama)</label>
              <input v-model="query.email" type="email" placeholder="rezervasyon e-postanız" />
            </div>
            <p v-if="cancelError" class="q-error">{{ cancelError }}</p>
            <p v-if="cancelSuccess" class="q-success">{{ cancelSuccess }}</p>
            <button class="btn-cancel" @click="handleCancel">Rezervasyonu İptal Et</button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Stepper from 'primevue/stepper'
import StepItem from 'primevue/stepitem'
import Step from 'primevue/step'
import StepPanel from 'primevue/steppanel'
import axios from 'axios'
import { ILLER, getIlceler } from '../utils/address'
import MockPaymentForm from '../components/MockPaymentForm.vue'
import { CATEGORY_ORDER, CATEGORY_COLORS, categoryLabel } from '@/constants/sipp'

const iller = ILLER
const currentStep = ref(1)
const direction = ref('forward')
const stepLabels = ['Lokasyon', 'Tarih', 'Araç Modeli', 'Bilgileriniz', 'Ödeme']

const branches = ref([])
const availableDates = ref([])
const availabilityLoading = ref(false)
const formError = ref('')
const reservationCode = ref('')
const reservationPrice = ref(null)
const differentReturn = ref(false)
const transferCost = ref(null)

const form = ref({ branch: '', vehicle_group: '', preferred_vehicle_model: '', return_branch: '', start_time: '10:00', end_time: '10:00' })
const availableModels = ref([])
const modelsLoading = ref(false)
const modelFilterGroup = ref('')
const modelFilterFuel = ref('')
const modelFilterTransmission = ref('')
const paid = ref(false)
const dateRange = ref({ start: null, end: null })
const guest = ref({
  name: '', phone: '', email: '',
  billing_type: 'bireysel', billing_name: '', billing_tckn: '', billing_tax_office: '', billing_tax_no: '',
  billing_address: '', billing_neighborhood: '', billing_district: '', billing_city: '',
})
const ilceler = computed(() => getIlceler(guest.value.billing_city))

const query = ref({ code: '', email: '' })
const queryResult = ref(null)
const queryError = ref('')
const cancelError = ref('')
const cancelSuccess = ref('')

const groups = CATEGORY_ORDER.map(value => ({ value, label: categoryLabel(value), desc: '' }))

const selectedModel = computed(() => availableModels.value.find(m => m.id === form.value.preferred_vehicle_model) || null)
const totalPrice = computed(() => selectedModel.value ? Number(selectedModel.value.total_price) : null)

const transitionName = computed(() => direction.value === 'forward' ? 'step-fwd' : 'step-back')

const canAdvance = computed(() => {
  if (currentStep.value === 1) return !!form.value.branch
  if (currentStep.value === 2) return !!(dateRange.value.start && dateRange.value.end)
  if (currentStep.value === 3) return !!form.value.preferred_vehicle_model
  if (currentStep.value === 4) return true
  return false
})

function localDateStr(d) {
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}

// Takvim penceresi, backend'in fiilen fiyatlandırdığı en son güne kadar açık;
// sabit gün sayısı varsayımı ileri tarihli fiyatları yanlışlıkla pasif gösteriyordu.
const maxAvailabilityDate = computed(() => {
  if (!availableDates.value.length) return null
  const maxStr = availableDates.value.reduce((a, b) => (a > b ? a : b))
  return new Date(maxStr + 'T00:00:00')
})

const disabledDates = computed(() => {
  if (!availableDates.value.length || !maxAvailabilityDate.value) return []
  const available = new Set(availableDates.value)
  const disabled = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const totalDays = Math.round((maxAvailabilityDate.value - today) / 86400000) + 1
  for (let i = 0; i < totalDays; i++) {
    const d = new Date(today)
    d.setDate(today.getDate() + i)
    if (!available.has(localDateStr(d))) disabled.push(new Date(d))
  }
  return disabled
})

onMounted(async () => {
  const res = await axios.get('/api/branches/')
  branches.value = res.data
})

function branchName(id) {
  const b = branches.value.find(b => b.id === id)
  return b ? (b.title || b.name) : '—'
}
function groupLabel(v) { return groups.find(g => g.value === v)?.label || v }
function statusLabel(s) { return { pending: 'Bekliyor', assigned: 'Onaylandı', cancelled: 'İptal' }[s] || s }

function openDetail() {
  if (queryResult.value) window.open(`/misafir/rezervasyon/${queryResult.value.code}`, '_blank')
}

function nextStep() {
  if (!canAdvance.value) return
  direction.value = 'forward'
  currentStep.value++
  if (currentStep.value === 2) fetchAvailability()
  if (currentStep.value === 3) fetchModels()
}
function prevStep() {
  direction.value = 'back'
  currentStep.value--
}
function goToStep(n) {
  if (n >= currentStep.value) return
  direction.value = 'back'
  currentStep.value = n
}

function onPickupChange() {
  form.value.return_branch = ''
  transferCost.value = null
  form.value.preferred_vehicle_model = ''
  availableModels.value = []
}

async function fetchTransferCost() {
  if (!form.value.branch || !form.value.return_branch) { transferCost.value = null; return }
  const res = await axios.get('/api/transfer-cost/', {
    params: { from: form.value.branch, to: form.value.return_branch }
  })
  transferCost.value = res.data.cost
}

async function fetchAvailability() {
  if (!form.value.branch) return
  availabilityLoading.value = true
  availableDates.value = []
  dateRange.value = { start: null, end: null }
  try {
    const res = await axios.get('/api/availability/', { params: { branch: form.value.branch } })
    availableDates.value = res.data.available_dates
  } finally {
    availabilityLoading.value = false
  }
}

async function fetchModels() {
  if (!form.value.branch || !dateRange.value.start || !dateRange.value.end) return
  modelsLoading.value = true
  try {
    const params = {
      branch: form.value.branch,
      start_date: toLocalDateStr(dateRange.value.start),
      end_date: toLocalDateStr(dateRange.value.end),
      start_time: form.value.start_time,
      end_time: form.value.end_time,
    }
    if (modelFilterGroup.value) params.group = modelFilterGroup.value
    if (modelFilterFuel.value) params.fuel_type = modelFilterFuel.value
    if (modelFilterTransmission.value) params.transmission = modelFilterTransmission.value
    const res = await axios.get('/api/vehicle-models/', { params })
    availableModels.value = res.data
  } finally {
    modelsLoading.value = false
  }
}

function selectModel(m) {
  form.value.preferred_vehicle_model = m.id
  form.value.vehicle_group = m.group
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
  if (!guest.value.name || !guest.value.email) {
    formError.value = 'Ad soyad ve e-posta zorunludur.'
    return
  }
  try {
    const res = await axios.post('/api/guest-reservation/', {
      guest_name: guest.value.name,
      guest_phone: guest.value.phone,
      guest_email: guest.value.email,
      branch: form.value.branch,
      vehicle_group: form.value.vehicle_group,
      preferred_vehicle_model: form.value.preferred_vehicle_model,
      start_date: toLocalDateStr(dateRange.value.start),
      end_date: toLocalDateStr(dateRange.value.end),
      start_time: form.value.start_time,
      end_time: form.value.end_time,
      return_branch: differentReturn.value && form.value.return_branch ? form.value.return_branch : null,
      billing_type: guest.value.billing_type,
      billing_name: guest.value.billing_type === 'kurumsal' ? guest.value.billing_name : guest.value.name,
      billing_tckn: guest.value.billing_tckn,
      billing_tax_office: guest.value.billing_tax_office,
      billing_tax_no: guest.value.billing_tax_no,
      billing_phone: guest.value.phone,
      billing_address: guest.value.billing_address,
      billing_neighborhood: guest.value.billing_neighborhood,
      billing_district: guest.value.billing_district,
      billing_city: guest.value.billing_city,
      paid: paid.value,
    })
    reservationCode.value = res.data.code
    reservationPrice.value = res.data.total_price
  } catch (e) {
    formError.value = e.response?.data?.error || 'Bir hata oluştu.'
  }
}

function resetForm() {
  currentStep.value = 1
  direction.value = 'forward'
  form.value = { branch: '', vehicle_group: '', preferred_vehicle_model: '', return_branch: '', start_time: '10:00', end_time: '10:00' }
  dateRange.value = { start: null, end: null }
  availableModels.value = []
  guest.value = {
    name: '', phone: '', email: '',
    billing_type: 'bireysel', billing_name: '', billing_tckn: '', billing_tax_office: '', billing_tax_no: '',
    billing_address: '', billing_neighborhood: '', billing_district: '', billing_city: '',
  }
  paid.value = false
  differentReturn.value = false
  transferCost.value = null
  reservationCode.value = ''
  reservationPrice.value = null
  formError.value = ''
}

async function handleQuery() {
  queryError.value = ''
  queryResult.value = null
  cancelError.value = ''
  cancelSuccess.value = ''
  if (!query.value.code || query.value.code.length < 8) { queryError.value = '8 haneli kodu girin.'; return }
  try {
    const res = await axios.get('/api/guest-reservation/query/', { params: { code: query.value.code } })
    queryResult.value = res.data
  } catch { queryError.value = 'Rezervasyon bulunamadı.' }
}

async function handleCancel() {
  cancelError.value = ''
  cancelSuccess.value = ''
  if (!query.value.email) { cancelError.value = 'E-posta gerekli.'; return }
  try {
    await axios.post('/api/guest-reservation/cancel/', { code: query.value.code, email: query.value.email })
    cancelSuccess.value = 'Rezervasyon iptal edildi.'
    queryResult.value = { ...queryResult.value, status: 'cancelled' }
  } catch (e) { cancelError.value = e.response?.data?.error || 'İptal işlemi başarısız.' }
}

const copied = ref(false)

function copyCode(){
  navigator.clipboard.writeText(reservationCode.value)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}


</script>

<style scoped>
.guest-layout { min-height: 100vh; background: #F8FAFC; display: flex; flex-direction: column; }

/* ── Header ── */
.guest-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 40px;
  background: white; border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  position: sticky; top: 0; z-index: 30;
}

.brand { display: flex; align-items: center; gap: 11px; font-weight: 800; font-size: 16px; color: #111827; }
.brand-icon {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, #3730a3, #1B1063);
  border-radius: 10px; display: flex; align-items: center; justify-content: center;
  color: white; box-shadow: 0 3px 8px rgba(27,16,99,0.3);
}

.login-cta {
  display: flex; align-items: center; gap: 14px;
  background: white; border: 1.5px solid #e2e8f0;
  border-radius: 14px; padding: 10px 14px 10px 16px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06); transition: box-shadow 0.2s;
}
.login-cta:hover { box-shadow: 0 6px 24px rgba(0,0,0,0.1); }
.login-cta-text { display: flex; flex-direction: column; gap: 2px; }
.cta-title { font-size: 12px; font-weight: 700; color: #111827; white-space: nowrap; }
.cta-sub { font-size: 11px; color: #94a3b8; white-space: nowrap; }
.login-cta-btn {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 13px; font-weight: 700; color: white;
  background: linear-gradient(135deg, #1B1063, #130d4a);
  padding: 9px 18px; border-radius: 10px; transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(27,16,99,0.35); white-space: nowrap; flex-shrink: 0;
}
.login-cta-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(27,16,99,0.45); }

/* ── Body ── */
.guest-body {
  display: flex; gap: 28px;
  padding: 40px 40px 60px;
  max-width: 1160px; margin: 0 auto; width: 100%;
}

/* ── Wizard Panel ── */
.wizard-panel { flex: 1.3; min-width: 0; }

.wizard-intro { margin-bottom: 28px; }
.wizard-intro h2 { font-size: 22px; font-weight: 800; color: #111827; margin: 0 0 4px; }
.wizard-intro p { font-size: 13px; color: #64748B; margin: 0; }

/* ── Step Bar ── */
.step-bar {
  display: flex; align-items: flex-start;
  margin-bottom: 28px; padding: 0 4px;
}

.step-node { display: flex; flex-direction: column; align-items: center; gap: 7px; flex-shrink: 0; }

.step-circle {
  width: 42px; height: 42px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; font-weight: 800;
  background: white; border: 2px solid #d1d5db; color: #9ca3af;
  transition: all 0.3s ease;
}
.step-circle svg { width: 16px; height: 16px; }

.step-node.active .step-circle { border: 2.5px solid #1B1063; color: #1B1063; box-shadow: 0 0 0 5px rgba(27,16,99,0.1); }
.step-node.completed .step-circle { background: #1B1063; border-color: #1B1063; color: white; box-shadow: 0 0 0 5px rgba(27,16,99,0.1); }

.step-label { font-size: 11px; font-weight: 600; color: #9ca3af; white-space: nowrap; text-align: center; transition: color 0.3s; }
.step-node.active .step-label { color: #1B1063; font-weight: 700; }
.step-node.completed .step-label { color: #64748b; }
.step-node.clickable { cursor: pointer; }
.step-node.clickable:hover .step-circle { box-shadow: 0 0 0 5px rgba(27,16,99,0.18); }
.step-node.clickable:hover .step-label { color: #1B1063; }

.step-connector { flex: 1; height: 2px; background: #e5e7eb; margin-top: 20px; transition: background 0.3s; }
.step-connector.done { background: #1B1063; }

/* ── Step Card ── */
.step-card {
  background: white; border-radius: 18px;
  padding: 30px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
  border: 1px solid rgba(226,232,240,0.8);
  min-height: 280px;
}

.card-title { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding-bottom: 18px; border-bottom: 1px solid #f1f5f9; }
.card-title-icon { font-size: 24px; flex-shrink: 0; }
.card-title-text { font-size: 17px; font-weight: 800; color: #111827; line-height: 1.2; }
.card-title-sub { font-size: 12.5px; color: #64748B; margin-top: 2px; }

/* ── Step 1 ── */
.location-grid { display: flex; align-items: flex-end; gap: 14px; }
.loc-field { flex: 1; display: flex; flex-direction: column; gap: 7px; }
.loc-label { display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.08em; }
.loc-dot { width: 9px; height: 9px; border-radius: 50%; background: #d1d5db; flex-shrink: 0; transition: background 0.2s; }
.loc-dot.pickup { background: #1B1063; }
.loc-dot.active { background: #F59E0B; }
.loc-field select { padding: 11px 14px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 14px; color: #94a3b8; outline: none; background: #fafafa; transition: border 0.2s, box-shadow 0.2s; cursor: pointer; }
.loc-field select.filled { color: #111827; background: white; border-color: #c4beff; }
.loc-field select:focus { border-color: #1B1063; background: white; box-shadow: 0 0 0 3px rgba(27,16,99,0.08); }
.same-loc-btn { padding: 11px 14px; border: 1.5px dashed #e2e8f0; border-radius: 10px; font-size: 13px; color: #94a3b8; cursor: pointer; background: #fafafa; transition: border-color 0.2s; }
.same-loc-btn:hover { border-color: #1B1063; }
.loc-arrow { font-size: 16px; color: #d1d5db; flex-shrink: 0; padding-bottom: 12px; }
.change-link { color: #1B1063; font-weight: 700; margin-left: 4px; }
.transfer-notice { margin-top: 14px; display: flex; align-items: center; gap: 8px; padding: 11px 14px; background: #fff7ed; border: 1px solid #fed7aa; border-radius: 9px; font-size: 13px; color: #92400e; font-weight: 500; }
.transfer-notice.free { background: #f0fdf4; border-color: #bbf7d0; color: #166534; }
.notice-icon { width: 17px; height: 17px; flex-shrink: 0; }

/* ── Step 2 ── */
.group-list { display: flex; flex-direction: column; gap: 10px; }
.group-card { display: flex; align-items: center; gap: 14px; padding: 16px 18px; background: white; border: 1.5px solid #e5e7eb; border-radius: 13px; cursor: pointer; text-align: left; transition: all 0.2s; width: 100%; }
.group-card:hover { border-color: #9b8ff5; background: #faf9ff; transform: translateX(2px); }
.group-card.selected { border-color: #1B1063; background: #edeaff; box-shadow: 0 0 0 3px rgba(27,16,99,0.08); }
.group-icon {
  width: 42px; height: 42px; flex-shrink: 0;
  border-radius: 11px;
  display: flex; align-items: center; justify-content: center;
  background: #f1f5f9; color: #64748b;
  transition: background 0.2s, color 0.2s;
}
.group-icon svg { width: 20px; height: 20px; }
.group-card.selected .group-icon { background: #1B1063; color: white; }
.group-info { flex: 1; }
.group-name { font-size: 14px; font-weight: 700; color: #111827; }
.group-desc { font-size: 12px; color: #64748B; margin-top: 2px; }
.group-check-circle { width: 28px; height: 28px; border-radius: 50%; background: #1B1063; display: flex; align-items: center; justify-content: center; flex-shrink: 0; opacity: 0; transform: scale(0.6); transition: opacity 0.2s, transform 0.2s; }
.group-check-circle.visible { opacity: 1; transform: scale(1); }
.group-check-circle svg { width: 13px; height: 13px; color: white; }

/* ── Step 3: Araç Modeli ── */
.model-filters { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 18px; }
.model-filters select {
  padding: 9px 14px;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  font-size: 13.5px;
  color: #374151;
  background: white;
  cursor: pointer;
}
.model-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
.model-card {
  display: flex;
  flex-direction: column;
  background: white;
  border: 1.5px solid #e5e7eb;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
  position: relative;
  padding: 0;
}
.model-card:hover { border-color: #9b8ff5; transform: translateY(-2px); }
.model-card.selected { border-color: #1B1063; box-shadow: 0 0 0 4px rgba(27,16,99,0.08); }
.model-img { width: 100%; height: 120px; object-fit: cover; background: #f1f5f9; }
.model-img-empty { display: flex; }
.model-body { padding: 14px 16px 16px; flex: 1; display: flex; flex-direction: column; gap: 6px; }
.model-name { font-size: 15px; font-weight: 700; color: #111827; }
.model-alt { font-size: 11.5px; color: #94a3b8; font-style: italic; margin-top: -4px; }
.model-badges { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 4px; }
.model-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 50px;
  background: #f1f5f9;
  color: #475569;
}
.model-price { font-size: 15px; font-weight: 700; color: #1B1063; margin-top: 6px; }
.model-price-sub { font-size: 11px; font-weight: 500; color: #94a3b8; }
.model-check-circle {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #1B1063;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transform: scale(0.6);
  transition: opacity 0.2s, transform 0.2s;
}
.model-check-circle.visible { opacity: 1; transform: scale(1); }
.model-check-circle svg { width: 13px; height: 13px; color: white; }

/* ── Step 3 ── */
.date-hint { font-size: 13px; color: #64748B; margin-bottom: 14px; }
.time-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 18px; }
.time-grid input[type="time"] { padding: 11px 14px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 14px; color: #111827; outline: none; background: white; }
.loading-state { display: flex; align-items: center; gap: 12px; padding: 40px 0; justify-content: center; color: #64748B; font-size: 14px; }
.loading-spinner { width: 22px; height: 22px; border: 2.5px solid #e2e8f0; border-top-color: #1B1063; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.no-avail { padding: 18px; background: #fff7ed; border-radius: 10px; color: #9a3412; font-size: 14px; font-weight: 500; border: 1px solid #fcd34d; }

/* ── Step 4 ── */
.mini-summary {
  display: flex; gap: 0;
  background: #F8FAFC; border-radius: 12px;
  border: 1px solid #f1f5f9;
  margin-bottom: 22px; overflow: hidden;
}
.mini-item { flex: 1; padding: 12px 16px; border-right: 1px solid #f1f5f9; }
.mini-item:last-child { border-right: none; }
.mini-key { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; display: block; margin-bottom: 4px; }
.mini-val { font-size: 13px; font-weight: 700; color: #111827; }

.info-fields { display: flex; flex-direction: column; gap: 14px; }
.info-field { display: flex; flex-direction: column; gap: 6px; }
.info-field label { font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.07em; }
.req { color: #DC2626; }
.info-field input, .info-field select { padding: 11px 14px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 14px; outline: none; background: #fafafa; transition: border-color 0.2s, box-shadow 0.2s; }
.info-field input:focus, .info-field select:focus { border-color: #1B1063; background: white; box-shadow: 0 0 0 3px rgba(27,16,99,0.08); }

.form-error { color: #DC2626; font-size: 13px; background: #fff1f2; padding: 11px 14px; border-radius: 9px; border: 1px solid #fecdd3; margin-top: 12px; }
.divider { height: 1px; background: #f1f5f9; margin: 22px 0; }

/* ── Navigation ── */
.step-nav { display: flex; justify-content: space-between; align-items: center; margin-top: 18px; gap: 10px; }
.step-nav.nav-start { justify-content: flex-end; }

.btn-back { padding: 11px 22px; background: white; color: #64748b; border: 1.5px solid #e2e8f0; border-radius: 11px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-back:hover { background: #F8FAFC; border-color: #cbd5e1; color: #111827; }

.btn-next, .btn-confirm {
  padding: 12px 28px;
  background: linear-gradient(135deg, #1B1063, #130d4a);
  color: white; border: none; border-radius: 11px;
  font-size: 14px; font-weight: 700; cursor: pointer;
  transition: all 0.2s; box-shadow: 0 4px 12px rgba(27,16,99,0.3);
}
.btn-next:hover:not(:disabled), .btn-confirm:hover { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(27,16,99,0.4); }
.btn-next:disabled { background: #e5e7eb; color: #9ca3af; box-shadow: none; cursor: not-allowed; transform: none; }

/* ── Success ── */
.success-card { background: white; border-radius: 18px; padding: 40px 32px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04); border: 1px solid rgba(226,232,240,0.8); }
.success-icon-wrap { width: 64px; height: 64px; background: linear-gradient(135deg, #16A34A, #15803d); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; box-shadow: 0 4px 16px rgba(22,163,74,0.3); }
.success-icon-wrap svg { width: 28px; height: 28px; color: white; }
.success-card h3 { font-size: 22px; font-weight: 800; color: #111827; margin: 0 0 10px; }
.success-sub { font-size: 14px; color: #64748B; margin: 0 0 24px; line-height: 1.6; }
.code-box { font-size: 30px; font-weight: 900; letter-spacing: 6px; color: #1B1063; background: #edeaff; border: 2px dashed #9b8ff5; border-radius: 12px; padding: 18px 28px; display: inline-block; margin-bottom: 10px; cursor: pointer; transition: background 0.15s, border-color 0.15s; }
.code-box:hover { background: #e2dcff; border-color: #7c6ef0; }
.price-box { font-size: 15px; color: #1B1063; background: #edeaff; border-radius: 10px; padding: 10px 20px; margin: 10px 0 4px; font-weight: 600; }
.price-box strong { font-weight: 800; }
.code-hint { font-size: 12px; color: #94a3b8; margin-bottom: 28px; }
.btn-new { padding: 13px 32px; background: linear-gradient(135deg, #16A34A, #15803d); color: white; border: none; border-radius: 11px; font-size: 14px; font-weight: 700; cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 12px rgba(22,163,74,0.3); }
.btn-new:hover { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(22,163,74,0.4); }

/* ── Query Panel ── */
.query-panel {
  width: 300px; flex-shrink: 0;
  background: white; border-radius: 18px; padding: 28px;
  border: 1.5px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  align-self: center;
}

.query-header { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 22px; padding-bottom: 18px; border-bottom: 1px solid #f1f5f9; }
.query-icon {
  width: 38px; height: 38px; flex-shrink: 0;
  border-radius: 10px; background: #ede9fe; color: #5b21b6;
  display: flex; align-items: center; justify-content: center;
}
.query-icon svg { width: 18px; height: 18px; }
.query-title { font-size: 15px; font-weight: 800; color: #111827; }
.query-sub { font-size: 12px; color: #64748B; margin-top: 2px; line-height: 1.4; }

.q-field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.q-field label { font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.07em; }
.q-field input { padding: 10px 13px; border: 1.5px solid #e2e8f0; border-radius: 9px; font-size: 14px; outline: none; background: #fafafa; transition: border-color 0.2s; }
.q-field input:focus { border-color: #1B1063; background: white; }

.btn-query { width: 100%; padding: 11px; background: #1B1063; color: white; border: none; border-radius: 10px; font-size: 14px; font-weight: 700; cursor: pointer; transition: background 0.2s, transform 0.2s, box-shadow 0.2s; margin-bottom: 14px; }
.btn-query:hover { background: #130d4a; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(27,16,99,0.3); }
.btn-query:active { transform: translateY(0); }

.q-error { color: #DC2626; font-size: 12.5px; background: #fff1f2; padding: 8px 12px; border-radius: 8px; border: 1px solid #fecdd3; margin-bottom: 12px; }
.q-success { color: #16A34A; font-size: 12.5px; background: #f0fdf4; padding: 8px 12px; border-radius: 8px; border: 1px solid #bbf7d0; margin-bottom: 12px; font-weight: 600; }

.query-result { border-top: 1px solid #f1f5f9; padding-top: 16px; display: flex; flex-direction: column; gap: 8px; }
.result-row { display: flex; justify-content: space-between; align-items: center; }
.rk { font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em; }
.rv { font-size: 13px; font-weight: 600; color: #111827; text-align: right; max-width: 150px; word-break: break-word; }

.status-badge { padding: 3px 10px; border-radius: 50px; font-size: 11px; font-weight: 700; }
.status-badge.pending  { background: #fef3c7; color: #92400e; }
.status-badge.assigned { background: #d1fae5; color: #16A34A; }
.status-badge.cancelled { background: #fee2e2; color: #DC2626; }

.cancel-area { margin-top: 14px; padding-top: 14px; border-top: 1px solid #f1f5f9; }
.btn-cancel { width: 100%; padding: 10px; background: #fff1f2; color: #DC2626; border: 1.5px solid #fecdd3; border-radius: 9px; font-size: 13px; font-weight: 700; cursor: pointer; transition: all 0.2s; margin-top: 10px; }
.btn-cancel:hover { background: #fee2e2; border-color: #DC2626; }

.btn-detail { width: 100%; padding: 10px; background: white; color: #1B1063; border: 1.5px solid #c4beff; border-radius: 9px; font-size: 13px; font-weight: 700; cursor: pointer; transition: all 0.2s; margin-top: 10px; }
.btn-detail:hover { background: #edeaff; }

/* ── Transitions ── */
.step-fwd-enter-active { transition: all 0.28s ease; }
.step-fwd-leave-active { transition: all 0.2s ease; }
.step-fwd-enter-from   { opacity: 0; transform: translateX(32px); }
.step-fwd-leave-to     { opacity: 0; transform: translateX(-32px); }

.step-back-enter-active { transition: all 0.28s ease; }
.step-back-leave-active { transition: all 0.2s ease; }
.step-back-enter-from   { opacity: 0; transform: translateX(-32px); }
.step-back-leave-to     { opacity: 0; transform: translateX(32px); }

/* ── Responsive ── */
@media (max-width: 900px) {
  .guest-body { flex-direction: column; padding: 24px 20px 40px; }
  .query-panel { width: 100%; position: static; }
  .guest-header { padding: 12px 20px; }
  .login-cta-text { display: none; }
}
</style>

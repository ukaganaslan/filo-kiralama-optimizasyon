<template>
  <div class="guest-layout">

    <!-- Header -->
    <div class="guest-header">
      <div class="brand">
        <div class="brand-icon">K</div>
        <span>Filo Yönetimi</span>
      </div>
      <router-link to="/" class="login-link">Giriş Yap →</router-link>
    </div>

    <div class="guest-body">

      <!-- SOL: Rezervasyon Formu -->
      <div class="form-panel">
        <h2>Misafir Rezervasyonu</h2>
        <p class="sub">Hesap oluşturmadan araç kiralayın.</p>

        <!-- ADIM 1: Lokasyon + Grup -->
        <div v-if="step === 1">
          <div class="section-title"><span class="step-num">1</span> Lokasyon ve Araç Grubu</div>

          <div class="field">
            <label>Alış Yeri</label>
            <select v-model="form.branch" @change="onPickupChange">
              <option value="" disabled>Şube seçin...</option>
              <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.title || b.name }}</option>
            </select>
          </div>

          <div class="field">
            <label>İade Yeri</label>
            <div v-if="!differentReturn" class="same-loc" @click="differentReturn = true">
              Alış yeriyle aynı <span class="change-link">Değiştir</span>
            </div>
            <select v-else v-model="form.return_branch" @change="fetchTransferCost">
              <option value="" disabled>Şube seçin...</option>
              <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.title || b.name }}</option>
            </select>
          </div>

          <div v-if="transferCost !== null && differentReturn" class="transfer-notice" :class="{ free: transferCost === 0 }">
            {{ transferCost > 0 ? `Transfer ücreti: ${transferCost} ₺` : 'Transfer ücreti yok' }}
          </div>

          <div class="field">
            <label>Araç Grubu</label>
            <div class="group-cards">
              <button
                v-for="g in groups"
                :key="g.value"
                class="group-card"
                :class="{ selected: form.vehicle_group === g.value }"
                @click="selectGroup(g.value)"
              >
                <span>{{ g.emoji }}</span>
                <div>
                  <div class="group-name">{{ g.label }}</div>
                  <div class="group-desc">{{ g.desc }}</div>
                </div>
              </button>
            </div>
          </div>

          <button class="btn-next" :disabled="!form.branch || !form.vehicle_group" @click="goStep2">
            Devam Et →
          </button>
        </div>

        <!-- ADIM 2: Takvim -->
        <div v-if="step === 2">
          <div class="section-title"><span class="step-num">2</span> Tarih Seçin</div>

          <div v-if="availabilityLoading" class="loading">Müsaitlik kontrol ediliyor...</div>

          <div v-else-if="availableDates.length === 0" class="no-avail">
            ⚠️ Bu şube ve grupta müsait gün bulunmuyor.
          </div>

          <div v-else>
            <p class="date-hint">Açık günler müsait, gri günler dolu.</p>
            <VDatePicker
              v-model.range="dateRange"
              :disabled-dates="disabledDates"
              :min-date="new Date()"
              color="indigo"
              is-expanded
            />
          </div>

          <div class="step-actions">
            <button class="btn-back" @click="step = 1">← Geri</button>
            <button class="btn-next" :disabled="!dateRange.start || !dateRange.end" @click="step = 3">
              Devam Et →
            </button>
          </div>
        </div>

        <!-- ADIM 3: Kişisel Bilgiler -->
        <div v-if="step === 3">
          <div class="section-title"><span class="step-num">3</span> Bilgileriniz</div>

          <div class="confirm-summary">
            <div class="confirm-item"><span class="confirm-key">Şube</span><span>{{ branchName(form.branch) }}</span></div>
            <div class="confirm-item"><span class="confirm-key">Grup</span><span>{{ groupLabel(form.vehicle_group) }}</span></div>
            <div class="confirm-item"><span class="confirm-key">Tarih</span><span>{{ toLocalDateStr(dateRange.start) }} → {{ toLocalDateStr(dateRange.end) }}</span></div>
          </div>

          <div class="field">
            <label>Ad Soyad *</label>
            <input v-model="guest.name" type="text" placeholder="Ahmet Yılmaz" />
          </div>
          <div class="field">
            <label>Telefon</label>
            <input v-model="guest.phone" type="tel" placeholder="05XX XXX XX XX" />
          </div>
          <div class="field">
            <label>E-posta *</label>
            <input v-model="guest.email" type="email" placeholder="ahmet@email.com" />
          </div>

          <p v-if="formError" class="error">{{ formError }}</p>

          <div class="step-actions">
            <button class="btn-back" @click="step = 2">← Geri</button>
            <button class="btn-next" @click="handleCreate">Rezervasyon Oluştur →</button>
          </div>
        </div>

        <!-- ADIM 4: Başarı -->
        <div v-if="step === 4" class="success-panel">
          <div class="success-icon">✓</div>
          <h3>Rezervasyonunuz Alındı</h3>
          <p>Rezervasyon kodunuzu saklayın. Bu kodla rezervasyonunuzu sorgulayabilir veya iptal edebilirsiniz.</p>
          <div class="code-box">{{ reservationCode }}</div>
          <p class="code-hint">Bu kodu not edin veya ekran görüntüsü alın.</p>
          <button class="btn-next" @click="resetForm">Yeni Rezervasyon</button>
        </div>
      </div>

      <!-- SAĞ: Rezervasyon Sorgula -->
      <div class="query-panel">
        <h3>Rezervasyonunuzu Sorgulayın</h3>
        <p class="sub">Rezervasyon kodunuzla mevcut rezervasyonunuzu görüntüleyin veya iptal edin.</p>

        <div class="field">
          <label>Rezervasyon Kodu</label>
          <input v-model="query.code" type="text" placeholder="3FA2B91C" maxlength="8" style="text-transform: uppercase" />
        </div>

        <button class="btn-query" @click="handleQuery">Sorgula</button>

        <p v-if="queryError" class="error">{{ queryError }}</p>

        <div v-if="queryResult" class="query-result">
          <div class="confirm-item"><span class="confirm-key">Ad</span><span>{{ queryResult.guest_name }}</span></div>
          <div class="confirm-item"><span class="confirm-key">Şube</span><span>{{ queryResult.branch }}</span></div>
          <div class="confirm-item"><span class="confirm-key">Grup</span><span>{{ groupLabel(queryResult.vehicle_group) }}</span></div>
          <div class="confirm-item"><span class="confirm-key">Tarih</span><span>{{ queryResult.start_date }} → {{ queryResult.end_date }}</span></div>
          <div class="confirm-item">
            <span class="confirm-key">Durum</span>
            <span class="badge" :class="queryResult.status">{{ statusLabel(queryResult.status) }}</span>
          </div>

          <div v-if="queryResult.status !== 'cancelled'" class="cancel-section">
            <div class="field">
              <label>E-posta (doğrulama için)</label>
              <input v-model="query.email" type="email" placeholder="rezervasyon e-postanız" />
            </div>
            <p v-if="cancelError" class="error">{{ cancelError }}</p>
            <p v-if="cancelSuccess" class="success-msg">{{ cancelSuccess }}</p>
            <button class="btn-cancel" @click="handleCancel">Rezervasyonu İptal Et</button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const step = ref(1)
const branches = ref([])
const availableDates = ref([])
const availabilityLoading = ref(false)
const formError = ref('')
const reservationCode = ref('')
const differentReturn = ref(false)
const transferCost = ref(null)

const form = ref({ branch: '', vehicle_group: '', return_branch: '' })
const dateRange = ref({ start: null, end: null })
const guest = ref({ name: '', phone: '', email: '' })

const query = ref({ code: '', email: '' })
const queryResult = ref(null)
const queryError = ref('')
const cancelError = ref('')
const cancelSuccess = ref('')

const groups = [
  { value: 'economy', label: 'Ekonomi', emoji: '🚗', desc: 'Şehir içi, yakıt dostu' },
  { value: 'mid',     label: 'Orta Sınıf', emoji: '🚙', desc: 'Konfor ve performans' },
  { value: 'suv',     label: 'SUV', emoji: '🛻', desc: 'Geniş, güçlü, her arazi' },
]

const disabledDates = computed(() => {
  if (availableDates.value.length === 0) return []
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

onMounted(async () => {
  const res = await axios.get('/api/branches/')
  branches.value = res.data
})

function branchName(id) {
  const b = branches.value.find(b => b.id === id)
  return b ? (b.title || b.name) : ''
}

function groupLabel(v) {
  return groups.find(g => g.value === v)?.label || v
}

function statusLabel(s) {
  return { pending: 'Bekliyor', assigned: 'Atandı', cancelled: 'İptal' }[s] || s
}

function selectGroup(val) {
  form.value.vehicle_group = val
}

function onPickupChange() {
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

async function goStep2() {
  availabilityLoading.value = true
  availableDates.value = []
  dateRange.value = { start: null, end: null }
  step.value = 2
  try {
    const res = await axios.get('/api/availability/', {
      params: { branch: form.value.branch, group: form.value.vehicle_group }
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
      start_date: toLocalDateStr(dateRange.value.start),
      end_date: toLocalDateStr(dateRange.value.end),
      return_branch: differentReturn.value && form.value.return_branch ? form.value.return_branch : null,
    })
    reservationCode.value = res.data.code
    step.value = 4
  } catch (e) {
    formError.value = e.response?.data?.error || 'Bir hata oluştu.'
  }
}

function resetForm() {
  step.value = 1
  form.value = { branch: '', vehicle_group: '', return_branch: '' }
  dateRange.value = { start: null, end: null }
  guest.value = { name: '', phone: '', email: '' }
  differentReturn.value = false
  transferCost.value = null
  reservationCode.value = ''
  formError.value = ''
}

async function handleQuery() {
  queryError.value = ''
  queryResult.value = null
  cancelError.value = ''
  cancelSuccess.value = ''
  if (!query.value.code || query.value.code.length < 8) {
    queryError.value = '8 haneli kodu girin.'
    return
  }
  try {
    const res = await axios.get('/api/guest-reservation/query/', {
      params: { code: query.value.code }
    })
    queryResult.value = res.data
  } catch {
    queryError.value = 'Rezervasyon bulunamadı.'
  }
}

async function handleCancel() {
  cancelError.value = ''
  cancelSuccess.value = ''
  if (!query.value.email) {
    cancelError.value = 'E-posta gerekli.'
    return
  }
  try {
    await axios.post('/api/guest-reservation/cancel/', {
      code: query.value.code,
      email: query.value.email,
    })
    cancelSuccess.value = 'Rezervasyon iptal edildi.'
    queryResult.value = { ...queryResult.value, status: 'cancelled' }
  } catch (e) {
    cancelError.value = e.response?.data?.error || 'İptal işlemi başarısız.'
  }
}
</script>

<style scoped>
.guest-layout { min-height: 100vh; background: #f8fafc; display: flex; flex-direction: column; }

.guest-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 40px; background: white; border-bottom: 1px solid #e2e8f0;
}
.brand { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 16px; color: #1e293b; }
.brand-icon { width: 32px; height: 32px; background: #6366f1; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; color: white; font-size: 14px; }
.login-link { font-size: 13px; font-weight: 600; color: #6366f1; text-decoration: none; }
.login-link:hover { text-decoration: underline; }

.guest-body { display: flex; gap: 32px; padding: 40px; max-width: 1100px; margin: 0 auto; width: 100%; }

.form-panel {
  flex: 1.2; background: white; border-radius: 14px;
  border: 1.5px solid #e2e8f0; padding: 32px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.query-panel {
  flex: 0.8; background: white; border-radius: 14px;
  border: 1.5px solid #e2e8f0; padding: 32px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  align-self: flex-start;
}

h2 { font-size: 22px; font-weight: 800; color: #0f172a; margin: 0 0 4px; }
h3 { font-size: 17px; font-weight: 700; color: #0f172a; margin: 0 0 4px; }
.sub { font-size: 13px; color: #94a3b8; margin: 0 0 24px; }

.section-title { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 14px; color: #1e293b; margin-bottom: 20px; }
.step-num { width: 24px; height: 24px; background: #6366f1; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 800; flex-shrink: 0; }

.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.field label { font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.06em; }
.field input, .field select { padding: 10px 13px; border: 1.5px solid #e2e8f0; border-radius: 9px; font-size: 14px; outline: none; background: white; color: #1e293b; }
.field input:focus, .field select:focus { border-color: #6366f1; }

.same-loc { padding: 10px 13px; border: 1.5px solid #e2e8f0; border-radius: 9px; font-size: 13px; color: #94a3b8; cursor: pointer; }
.change-link { color: #6366f1; font-weight: 600; margin-left: 6px; }

.transfer-notice { padding: 10px 14px; background: #fef3c7; border: 1px solid #fbbf24; border-radius: 8px; font-size: 13px; color: #92400e; margin-bottom: 16px; }
.transfer-notice.free { background: #f0fdf4; border-color: #86efac; color: #166534; }

.group-cards { display: flex; flex-direction: column; gap: 8px; }
.group-card { display: flex; align-items: center; gap: 12px; padding: 12px 14px; border: 1.5px solid #e2e8f0; border-radius: 10px; background: white; cursor: pointer; text-align: left; transition: border-color 0.15s; }
.group-card:hover { border-color: #a5b4fc; }
.group-card.selected { border-color: #6366f1; background: #f5f3ff; }
.group-name { font-size: 13px; font-weight: 700; color: #1e293b; }
.group-desc { font-size: 12px; color: #94a3b8; }

.date-hint { font-size: 12px; color: #94a3b8; margin-bottom: 12px; }
.loading { font-size: 13px; color: #94a3b8; padding: 20px 0; text-align: center; }
.no-avail { padding: 16px; background: #fff7ed; border-radius: 8px; font-size: 13px; color: #9a3412; }

.step-actions { display: flex; gap: 10px; margin-top: 20px; }
.btn-next { flex: 1; padding: 12px; background: #6366f1; color: white; border: none; border-radius: 10px; font-size: 14px; font-weight: 700; cursor: pointer; }
.btn-next:hover { background: #4f46e5; }
.btn-next:disabled { background: #c7d2fe; cursor: not-allowed; }
.btn-back { padding: 12px 18px; background: white; color: #64748b; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-back:hover { background: #f8fafc; }

.confirm-summary { background: #f8fafc; border-radius: 10px; padding: 14px 16px; margin-bottom: 20px; display: flex; flex-direction: column; gap: 6px; }
.confirm-item { display: flex; justify-content: space-between; font-size: 13px; color: #475569; }
.confirm-key { font-weight: 600; color: #94a3b8; }

.success-panel { text-align: center; padding: 20px 0; }
.success-icon { width: 56px; height: 56px; background: #dcfce7; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; margin: 0 auto 16px; color: #16a34a; }
.success-panel h3 { font-size: 20px; font-weight: 800; color: #0f172a; margin-bottom: 8px; }
.success-panel p { font-size: 13px; color: #64748b; margin-bottom: 20px; }
.code-box { font-size: 28px; font-weight: 900; letter-spacing: 6px; color: #6366f1; background: #f5f3ff; border: 2px dashed #a5b4fc; border-radius: 12px; padding: 16px 24px; display: inline-block; margin-bottom: 8px; }
.code-hint { font-size: 12px; color: #94a3b8; margin-bottom: 24px; }

.btn-query { width: 100%; padding: 11px; background: #1e293b; color: white; border: none; border-radius: 10px; font-size: 14px; font-weight: 700; cursor: pointer; margin-bottom: 12px; }
.btn-query:hover { background: #0f172a; }

.query-result { margin-top: 16px; background: #f8fafc; border-radius: 10px; padding: 14px 16px; display: flex; flex-direction: column; gap: 6px; }
.badge { padding: 2px 8px; border-radius: 20px; font-size: 12px; font-weight: 700; }
.badge.pending { background: #fef9c3; color: #854d0e; }
.badge.assigned { background: #dcfce7; color: #166534; }
.badge.cancelled { background: #fee2e2; color: #991b1b; }

.cancel-section { margin-top: 14px; padding-top: 14px; border-top: 1px solid #e2e8f0; }
.btn-cancel { width: 100%; padding: 10px; background: #dc2626; color: white; border: none; border-radius: 9px; font-size: 13px; font-weight: 700; cursor: pointer; margin-top: 8px; }
.btn-cancel:hover { background: #b91c1c; }

.error { color: #dc2626; font-size: 13px; background: #fff1f2; padding: 10px 14px; border-radius: 8px; margin: 8px 0 0; }
.success-msg { color: #16a34a; font-size: 13px; background: #f0fdf4; padding: 10px 14px; border-radius: 8px; margin: 8px 0 0; }

@media (max-width: 768px) {
  .guest-body { flex-direction: column; padding: 20px; }
  .guest-header { padding: 16px 20px; }
}
</style>

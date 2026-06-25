<template>
  <div class="page">

    <!-- Hero -->
    <div class="hero">
      <div class="hero-content">
        <h1>Aracınızı Hemen Kiralayın</h1>
        <p class="hero-sub">Şubenizi seçin, grubu belirleyin, tarihleri ayarlayın.</p>
      </div>
    </div>

    <!-- Form -->
    <div class="form-wrap">

      <!-- Step 1: Lokasyon -->
      <div class="section-card">
        <div class="section-title">
          <span class="step-num">1</span>
          <span>Lokasyon</span>
        </div>

        <div class="location-row">
          <div class="location-field">
            <div class="loc-label">
              <span class="loc-dot pickup"></span>
              Alış Yeri
            </div>
            <select v-model="form.branch" @change="onPickupChange" :class="{ filled: form.branch }">
              <option value="" disabled>Şube seçin...</option>
              <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.title || b.name }}</option>
            </select>
          </div>

          <div class="loc-arrow">→</div>

          <div class="location-field">
            <div class="loc-label">
              <span class="loc-dot return" :class="{ active: differentReturn }"></span>
              İade Yeri
            </div>
            <div v-if="!differentReturn" class="same-location" @click="differentReturn = true">
              Alış yeriyle aynı <span class="change-link">Değiştir</span>
            </div>
            <select v-else v-model="form.return_branch" @change="fetchTransferCost" :class="{ filled: form.return_branch }">
              <option value="" disabled>Şube seçin...</option>
              <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.title || b.name }}</option>
            </select>
          </div>
        </div>

        <div v-if="transferCost !== null && differentReturn" class="transfer-notice" :class="{ free: transferCost === 0 }">
          <span>{{ transferCost > 0 ? `Transfer ücreti: ${transferCost} ₺` : 'Bu iade noktası için transfer ücreti yok' }}</span>
        </div>
      </div>

      <!-- Step 2: Araç Grubu -->
      <div class="section-card">
        <div class="section-title">
          <span class="step-num">2</span>
          <span>Araç Grubu</span>
        </div>
        <div class="group-cards">
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
            <span v-if="form.vehicle_group === g.value" class="group-check">✓</span>
          </button>
        </div>
      </div>

      <!-- Step 3: Tarih -->
      <div class="section-card" v-if="form.branch && form.vehicle_group">
        <div class="section-title">
          <span class="step-num">3</span>
          <span>Tarih Aralığı</span>
          <span v-if="availabilityLoading" class="loading-chip">Yükleniyor...</span>
        </div>

        <div v-if="availableDates.length > 0">
          <p class="date-hint">Açık günler müsait, gri günler dolu.</p>
          <VDatePicker
            v-model.range="dateRange"
            :disabled-dates="disabledDates"
            :min-date="new Date()"
            color="indigo"
            is-expanded
          />
        </div>

        <div v-if="availableDates.length === 0 && !availabilityLoading" class="no-avail">
          <span>⚠️</span> Bu şube ve grupta müsait gün bulunmuyor.
        </div>
      </div>

      <!-- Confirm -->
      <div v-if="dateRange.start && dateRange.end" class="confirm-card">
        <div class="confirm-summary">
          <div class="confirm-item">
            <span class="confirm-key">Alış</span>
            <span class="confirm-val">{{ branchName(form.branch) }}</span>
          </div>
          <div v-if="differentReturn && form.return_branch" class="confirm-item">
            <span class="confirm-key">İade</span>
            <span class="confirm-val">{{ branchName(form.return_branch) }}</span>
          </div>
          <div class="confirm-item">
            <span class="confirm-key">Grup</span>
            <span class="confirm-val">{{ groupLabel(form.vehicle_group) }}</span>
          </div>
          <div class="confirm-item">
            <span class="confirm-key">Tarih</span>
            <span class="confirm-val">{{ toLocalDateStr(dateRange.start) }} → {{ toLocalDateStr(dateRange.end) }}</span>
          </div>
        </div>
        <p v-if="formError" class="error">{{ formError }}</p>
        <p v-if="formSuccess" class="success-msg">{{ formSuccess }}</p>
        <button class="btn-confirm" @click="handleCreate">
          Rezervasyon Oluştur →
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const branches = ref([])
const availableDates = ref([])
const availabilityLoading = ref(false)
const formError = ref('')
const formSuccess = ref('')
const form = ref({ branch: '', vehicle_group: '', return_branch: '' })
const dateRange = ref({ start: null, end: null })
const differentReturn = ref(false)
const transferCost = ref(null)

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

function selectGroup(val) {
  form.value.vehicle_group = val
  fetchAvailability()
}

function onPickupChange() {
  form.value.return_branch = ''
  transferCost.value = null
  fetchAvailability()
}

function onDifferentReturnChange() {
  form.value.return_branch = ''
  transferCost.value = null
}

async function fetchAvailability() {
  if (!form.value.branch || !form.value.vehicle_group) return
  availabilityLoading.value = true
  availableDates.value = []
  dateRange.value = { start: null, end: null }
  try {
    const res = await axios.get('/api/availability/', {
      params: { branch: form.value.branch, group: form.value.vehicle_group }
    })
    availableDates.value = res.data.available_dates
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
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
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
    })
    formSuccess.value = 'Rezervasyon oluşturuldu, onay bekleniyor.'
    form.value = { branch: '', vehicle_group: '', return_branch: '' }
    dateRange.value = { start: null, end: null }
    availableDates.value = []
    differentReturn.value = false
    transferCost.value = null
  } catch (e) {
    const msg = e.response?.data?.non_field_errors?.[0]
    formError.value = msg || 'Rezervasyon oluşturulamadı.'
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: #f8fafc; }

/* Hero */
.hero {
  background: #f8fafc;
  padding: 52px 0 48px;
}
.hero-content { max-width: 760px; margin: 0 auto; padding: 0 24px; }
.hero-eyebrow { font-size: 12px; font-weight: 700; color: #a5b4fc; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 10px; }
.hero h1 { font-size: 36px; font-weight: 800; color: #312e81; margin: 0 0 10px; line-height: 1.15; }
.hero-sub { font-size: 15px; color: #94a3b8; margin: 0; }

/* Form wrap */
.form-wrap { max-width: 760px; margin: 0 auto; padding: 32px 24px 48px; display: flex; flex-direction: column; gap: 20px; }

/* Section card */
.section-card { background: white; border-radius: 14px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04); }
.section-title { display: flex; align-items: center; gap: 10px; font-size: 15px; font-weight: 700; color: #1e293b; margin-bottom: 20px; }
.step-num { width: 26px; height: 26px; background: #6366f1; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 800; flex-shrink: 0; }
.loading-chip { margin-left: auto; font-size: 12px; color: #6366f1; background: #ede9fe; padding: 3px 10px; border-radius: 50px; font-weight: 600; }

/* Location */
.location-row { display: flex; align-items: center; gap: 16px; }
.location-field { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.loc-label { display: flex; align-items: center; gap: 7px; font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; }
.loc-dot { width: 10px; height: 10px; border-radius: 50%; background: #cbd5e1; flex-shrink: 0; }
.loc-dot.pickup { background: #6366f1; }
.loc-dot.return { background: #cbd5e1; }
.loc-dot.return.active { background: #f59e0b; }
.location-field select { border: 1.5px solid #e2e8f0; border-radius: 9px; padding: 11px 14px; font-size: 14px; color: #94a3b8; outline: none; background: #fafafa; transition: border 0.2s, color 0.2s; }
.location-field select.filled { color: #1e293b; background: white; border-color: #c7d2fe; }
.location-field select:focus { border-color: #6366f1; background: white; }
.same-location { padding: 11px 14px; background: #f8fafc; border: 1.5px dashed #e2e8f0; border-radius: 9px; font-size: 13.5px; color: #94a3b8; cursor: pointer; transition: border-color 0.2s; }
.same-location:hover { border-color: #6366f1; }
.change-link { color: #6366f1; font-weight: 600; margin-left: 6px; }
.loc-arrow { font-size: 18px; color: #cbd5e1; flex-shrink: 0; margin-top: 20px; }
.transfer-notice { margin-top: 12px; padding: 10px 14px; background: #fff7ed; border: 1px solid #fed7aa; border-radius: 8px; font-size: 13px; color: #92400e; font-weight: 500; }
.transfer-notice.free { background: #f0fdf4; border-color: #bbf7d0; color: #166534; }

/* Group cards */
.group-cards { display: flex; flex-direction: column; gap: 10px; }
.group-card { display: flex; align-items: center; gap: 14px; padding: 14px 16px; background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 10px; cursor: pointer; text-align: left; transition: border-color 0.2s, background 0.2s; width: 100%; }
.group-card:hover { border-color: #a5b4fc; background: #fafafe; }
.group-card.selected { border-color: #6366f1; background: #eef2ff; }
.group-emoji { font-size: 26px; flex-shrink: 0; }
.group-info { flex: 1; }
.group-name { font-size: 14px; font-weight: 700; color: #1e293b; }
.group-desc { font-size: 12px; color: #94a3b8; margin-top: 2px; }
.group-check { width: 22px; height: 22px; background: #6366f1; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; flex-shrink: 0; }

/* Dates */
.date-hint { font-size: 12px; color: #94a3b8; margin-bottom: 14px; }
.no-avail { padding: 16px; background: #fff1f2; border-radius: 8px; color: #be123c; font-size: 14px; font-weight: 500; }

/* Confirm */
.confirm-card { background: white; border-radius: 14px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); border: 2px solid #e0e7ff; }
.confirm-summary { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 20px; }
.confirm-item { display: flex; flex-direction: column; gap: 3px; }
.confirm-key { font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em; }
.confirm-val { font-size: 14px; font-weight: 600; color: #1e293b; }
.btn-confirm { width: 100%; padding: 14px; background: #6366f1; color: white; border: none; border-radius: 10px; font-size: 15px; font-weight: 700; cursor: pointer; transition: background 0.2s, transform 0.1s; }
.btn-confirm:hover { background: #4f46e5; transform: translateY(-1px); }
.btn-confirm:active { transform: translateY(0); }
.error { color: #dc2626; font-size: 13px; margin-bottom: 12px; }
.success-msg { color: #16a34a; font-size: 13px; font-weight: 600; margin-bottom: 12px; background: #f0fdf4; padding: 10px 14px; border-radius: 8px; }
</style>

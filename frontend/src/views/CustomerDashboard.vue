<template>
  <div class="hero">
    <h1>Aracınızı Hemen Kiralayın</h1>

    <div class="booking-card">
      <div class="card-row">
        <div class="card-field">
          <label>ŞUBE</label>
          <select v-model="form.branch" @change="fetchAvailability">
            <option disabled value="">Şube Seçin</option>
            <option v-for="branch in branches" :key="branch.id" :value="branch.id">
              {{ branch.title || branch.name }}
            </option>
          </select>
        </div>

        <div class="divider"></div>

        <div class="card-field">
          <label>ARAÇ GRUBU</label>
          <select v-model="form.vehicle_group" @change="fetchAvailability">
            <option disabled value="">Grup Seçin</option>
            <option value="economy">Ekonomi</option>
            <option value="mid">Orta Sınıf</option>
            <option value="suv">SUV</option>
          </select>
        </div>
      </div>

      <div v-if="availabilityLoading" class="loading-hint">Müsait günler yükleniyor...</div>

      <div v-if="availableDates.length > 0" class="calendar-section">
        <label>TARİH ARALIĞI SEÇİN</label>
        <p class="hint">Gri günler dolu, açık günler müsait.</p>
        <VDatePicker
          v-model.range="dateRange"
          :disabled-dates="disabledDates"
          :min-date="new Date()"
          color="indigo"
          is-expanded
        />
      </div>

      <div v-if="form.branch && form.vehicle_group && availableDates.length === 0 && !availabilityLoading" class="no-avail">
        Bu şube ve grupta müsait gün bulunmuyor.
      </div>

      <p v-if="formError" class="error">{{ formError }}</p>
      <p v-if="formSuccess" class="success">{{ formSuccess }}</p>

      <div v-if="dateRange.start && dateRange.end" class="card-footer">
        <span class="date-summary">
          {{ toLocalDateStr(dateRange.start) }} → {{ toLocalDateStr(dateRange.end) }}
        </span>
        <button class="btn-reserve" @click="handleCreate">Rezervasyon Oluştur →</button>
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
const form = ref({ branch: '', vehicle_group: '' })
const dateRange = ref({ start: null, end: null })

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
  const res = await axios.get('http://127.0.0.1:8000/api/branches/')
  branches.value = res.data
})

async function fetchAvailability() {
  if (!form.value.branch || !form.value.vehicle_group) return
  availabilityLoading.value = true
  availableDates.value = []
  dateRange.value = { start: null, end: null }
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/availability/', {
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
  formSuccess.value = ''
  try {
    await axios.post('http://127.0.0.1:8000/api/reservations/', {
      branch: form.value.branch,
      vehicle_group: form.value.vehicle_group,
      start_date: toLocalDateStr(dateRange.value.start),
      end_date: toLocalDateStr(dateRange.value.end),
    })
    formSuccess.value = 'Rezervasyon oluşturuldu, onay bekleniyor.'
    form.value = { branch: '', vehicle_group: '' }
    dateRange.value = { start: null, end: null }
    availableDates.value = []
  } catch {
    formError.value = 'Rezervasyon oluşturulamadı.'
  }
}
</script>

<style scoped>
.hero { padding: 48px 40px 32px; max-width: 900px; margin: 0 auto; }
.hero h1 { font-size: 28px; font-weight: 700; color: #1e293b; margin-bottom: 24px; }
.booking-card { background: white; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); overflow: hidden; }
.card-row { display: flex; align-items: stretch; }
.card-field { flex: 1; padding: 20px 24px; display: flex; flex-direction: column; gap: 8px; }
.card-field label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; }
.card-field select { border: none; outline: none; font-size: 15px; color: #1e293b; background: transparent; cursor: pointer; padding: 4px 0; }
.divider { width: 1px; background: #e5e7eb; margin: 16px 0; }
.calendar-section { border-top: 1px solid #e5e7eb; padding: 20px 24px; display: flex; flex-direction: column; gap: 8px; }
.calendar-section label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; }
.card-footer { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; border-top: 1px solid #e5e7eb; background: #fafafa; }
.date-summary { font-size: 14px; color: #475569; font-weight: 500; }
.btn-reserve { padding: 12px 28px; background: #6366f1; color: white; border: none; border-radius: 50px; font-size: 15px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
.btn-reserve:hover { background: #4f46e5; }
.loading-hint { padding: 12px 24px; font-size: 13px; color: #94a3b8; border-top: 1px solid #e5e7eb; }
.no-avail { padding: 12px 24px; font-size: 13px; color: #dc2626; border-top: 1px solid #e5e7eb; }
.hint { font-size: 12px; color: #94a3b8; }
.error { color: #dc2626; font-size: 14px; padding: 0 24px; }
.success { color: #16a34a; font-size: 14px; padding: 0 24px; }
</style>

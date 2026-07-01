<template>
  <div class="content">
    <div class="page-header">
      <button class="btn-back" @click="router.push('/representative/rezervasyonlar')">← Geri</button>
      <div>
        <h2>Araç İadesi</h2>
        <span v-if="reservation" class="res-id">{{ reservation.reservation_id }}</span>
      </div>
    </div>

    <div v-if="loading" class="loading">Yükleniyor...</div>

        <div v-else-if="reservation" class="split-layout">


      <div class="teslim-panel">
        <div class="panel-title">Teslim Kaydı</div>

        <div class="readonly-row">
          <span class="readonly-label">Teslim KM</span>
          <span class="readonly-value">{{ reservation.delivery_info?.delivered_km ?? '—' }}</span>
        </div>
        <div class="readonly-row">
          <span class="readonly-label">Yakıt</span>
          <span class="readonly-value">{{ fuelLabel(reservation.delivery_info?.delivered_fuel) }}</span>
        </div>
        <div class="readonly-row">
          <span class="readonly-label">Notlar</span>
          <span class="readonly-value notes-val">{{ reservation.delivery_info?.delivered_notes || '—' }}</span>
        </div>

        <div class="readonly-label" style="margin-top: 12px;">Hasar Haritası</div>
        <div class="damage-readonly">
          <CarDamageMap :model-value="reservation.delivery_info?.delivered_damage || {}" />
        </div>
      </div>


      <div class="form-card">
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">MÜŞTERİ</span>
          <span class="info-value">{{ reservation.customer_username || reservation.guest_name || '—' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">ARAÇ</span>
          <span class="info-value">{{ reservation.assigned_vehicle_id || '—' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">PLAKA</span>
          <span class="info-value">{{ reservation.assigned_vehicle_info?.plate || '—' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">TARİH</span>
          <span class="info-value">{{ reservation.start_date }} → {{ reservation.end_date }}</span>
        </div>
      </div>

      <div class="form-row">
        <div class="form-field">
          <label>İade KM</label>
          <input v-model="form.km" type="number" placeholder="Kilometre" />
        </div>
        <div class="form-field">
          <label>Yakıt — {{ fuelLabel(form.fuel) }}</label>
          <input v-model="form.fuel" type="range" min="0" max="8" step="1" class="fuel-slider" />
          <div class="fuel-labels"><span>E</span><span>F</span></div>
        </div>
      </div>

      <div class="section-label">Hasar Haritası</div>
      <div :style="success ? 'pointer-events: none; opacity: 0.85' : ''">
        <CarDamageMap v-model="form.damage_map" />
      </div>

      <div class="form-field">
        <label>Notlar</label>
        <textarea v-model="form.notes" rows="3" placeholder="İade notu..."></textarea>
      </div>

      <Toast />
      <FileUpload
        name="document"
        accept=".pdf,.docx,.doc,.jpg,.jpeg,.png"
        :maxFileSize="5000000"
        :multiple="false"
        customUpload
        @select="e => file = e.files[0]"
        @uploader="submit"
        :showUploadButton="false"
        :showCancelButton="false"
      >
        <template #empty>
          <span>Belgeyi buraya sürükle bırak.</span>
        </template>
      </FileUpload>
    

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">{{ success }}</p>

      <div class="form-actions">
        <button v-if="!success" class="btn-save" @click="submit" :disabled="saving">
          {{ saving ? 'Kaydediliyor...' : 'İade Al' }}
        </button>
        <button v-if="success" class="btn-back" @click="router.back()">Geri Dön</button>
        <button v-if="success" class="btn-export" @click="exportPdf">PDF İndir</button>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import FileUpload from 'primevue/fileupload'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import CarDamageMap from '@/components/CarDamageMap.vue'

const route = useRoute()
const router = useRouter()

const reservation = ref(null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')
const file = ref(null)
const toast = useToast()

const form = ref({ km: '', fuel: 4, damage_map: {}, notes: '' })

function fuelLabel(v) {
  return { 0: 'E', 1: '1/8', 2: '1/4', 3: '3/8', 4: '1/2', 5: '5/8', 6: '3/4', 7: '7/8', 8: 'F' }[v] ?? '—'
}

onMounted(async () => {
  try {
    const res = await axios.get(`/api/reservations/${route.params.id}/`)
    reservation.value = res.data
    const r = res.data.delivery_info
    if (r?.returned) {
      form.value.km = r.returned_km ?? ''
      form.value.fuel = r.returned_fuel ?? 4
      form.value.damage_map = r.returned_damage || {}
      form.value.notes = r.returned_notes || ''
      success.value = 'İade kaydı mevcut.'
    }
  } catch {
    error.value = 'Rezervasyon bulunamadı.'
  } finally {
    loading.value = false
  }
})

async function submit() {
  if (!form.value.km) { error.value = 'KM alanı zorunludur.'; return }
  saving.value = true
  error.value = ''
  try {
    const fd = new FormData()
    fd.append('delivery_km', form.value.km)
    fd.append('fuel_level', form.value.fuel)
    fd.append('damage_items', JSON.stringify(form.value.damage_map))
    fd.append('notes', form.value.notes)
    if (file.value) fd.append('document', file.value)
    await axios.post(`/api/reservations/${route.params.id}/return/`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    success.value = 'Araç iadesi tamamlandı.'
  } catch (e) {
    error.value = e.response?.data?.error || 'İşlem başarısız.'
  } finally {
    saving.value = false
  }
}

async function exportPdf() {
  const res = await axios.get(`/api/reservations/${route.params.id}/pdf/iade/`, { responseType: 'blob' })
  const url = URL.createObjectURL(res.data)
  const a = document.createElement('a')
  a.href = url
  a.download = `iade-${route.params.id}.pdf`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.content { padding: 32px 40px; }
.page-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
.btn-back { background: none; border: 1px solid #e2e8f0; border-radius: 8px; padding: 7px 14px; font-size: 14px; color: #475569; cursor: pointer; }
.btn-back:hover { background: #f1f5f9; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0; }
.res-id { font-size: 13px; color: #94a3b8; font-family: monospace; }
.loading { color: #94a3b8; font-size: 14px; }
.split-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: start; }
.teslim-panel { background: #f8fafc; border-radius: 12px; padding: 24px; border: 1px solid #e2e8f0; display: flex; flex-direction: column; gap: 12px; }
.panel-title { font-size: 13px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px; }
.readonly-row { display: flex; justify-content: space-between; align-items: flex-start; padding: 8px 0; border-bottom: 1px solid #e2e8f0; }
.readonly-label { font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em; }
.readonly-value { font-size: 13px; font-weight: 600; color: #1e293b; text-align: right; }
.notes-val { font-weight: 400; font-style: italic; }
.damage-readonly { pointer-events: none; opacity: 0.85; }
.form-card { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); display: flex; flex-direction: column; gap: 16px; }
.info-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: #e2e8f0; border-radius: 10px; overflow: hidden; }
.info-item { background: white; padding: 12px 14px; }
.info-label { display: block; font-size: 10px; font-weight: 700; color: #94a3b8; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 3px; }
.info-value { display: block; font-size: 13px; font-weight: 600; color: #1e293b; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.form-field { display: flex; flex-direction: column; gap: 5px; }
.form-field label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.06em; text-transform: uppercase; }
.form-field input[type="number"], .form-field textarea { padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; color: #1e293b; resize: vertical; }
.form-field input[type="number"]:focus, .form-field textarea:focus { border-color: #6366f1; }
.form-field input[type="file"] { font-size: 13px; color: #475569; }
.fuel-slider { width: 100%; accent-color: #6366f1; }
.fuel-labels { display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; }
.section-label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.06em; text-transform: uppercase; }
.form-actions { display: flex; justify-content: flex-end; }
.btn-save { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-save:hover:not(:disabled) { background: #4f46e5; }
.btn-save:disabled { background: #a5b4fc; cursor: not-allowed; }
.btn-export { padding: 8px 20px; background: #1e293b; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-export:hover { background: #0f172a; }
.error { color: #dc2626; font-size: 13px; margin: 0; }
.success { color: #16a34a; font-size: 13px; margin: 0; }
:deep(.p-fileupload) { border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; }
:deep(.p-fileupload-header) { background: #f8fafc; border-bottom: 1px solid #e2e8f0; padding: 10px 14px; }
:deep(.p-fileupload-content) { background: white; padding: 16px; color: #475569; font-size: 13px; }
:deep(.p-button) { background: #ffffffa0; border-color: #1c1c1ca0; font-size: 13px; }
:deep(.p-button:hover) { background: #ffffffa0; border-color: #1c1c1ca0; }
:deep(.p-button.p-button-danger) { background: #f1f5f9; border-color: #e2e8f0; color: #475569; }
:deep(.p-button.p-button-danger:hover) { background: #e2e8f0; }
:deep(.p-fileupload .p-button) {
  background: #e9e8ebbf !important;
  border-color: #e9e8ebbf !important;
}
:deep(.p-fileupload .p-button:hover) {
  background: #38383880 !important;
  border-color: #38383880 !important;
}
</style>

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

    <div v-else-if="reservation" class="form-card">
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
      <div class="car-figure">
        <div
          v-for="part in CAR_PARTS"
          :key="part.id"
          class="car-part"
          :style="{ background: DAMAGE_STATES[form.damage_map[part.id] || 0].color, gridArea: part.gridArea, zIndex: activePart === part.id ? 50 : 1 }"
          @click="clickPart(part.id)"
        >
          <span class="part-label">{{ part.label }}</span>
          <span v-if="form.damage_map[part.id]" class="part-state">{{ DAMAGE_STATES[form.damage_map[part.id]].label }}</span>
          <div v-if="activePart === part.id" class="damage-picker" @click.stop>
            <button
              v-for="(ds, key) in DAMAGE_STATES"
              :key="key"
              :style="{ background: ds.color }"
              @click="setDamage(part.id, Number(key))"
            >{{ ds.label }}</button>
          </div>
        </div>
      </div>

      <div class="damage-legend">
        <span v-for="(ds, key) in DAMAGE_STATES" :key="key" class="legend-item">
          <span class="legend-dot" :style="{ background: ds.color }"></span>{{ ds.label }}
        </span>
      </div>

      <div class="form-field">
        <label>Notlar</label>
        <textarea v-model="form.notes" rows="3" placeholder="İade notu..."></textarea>
      </div>

      <div class="form-field">
        <label>Belge (PDF / DOCX / Fotoğraf)</label>
        <input type="file" @change="e => file = e.target.files[0]" accept=".pdf,.docx,.doc,.jpg,.jpeg,.png" />
      </div>
    

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">{{ success }}</p>

      <div class="form-actions">
        <button class="btn-save" @click="submit" :disabled="saving">
          {{ saving ? 'Kaydediliyor...' : 'İade Al' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const reservation = ref(null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')
const file = ref(null)
const activePart = ref(null)

const form = ref({ km: '', fuel: 4, damage_map: {}, notes: '' })

const CAR_PARTS = [
  { id: 'on_tampon',         label: 'Ön Tampon',          gridArea: 'on-tampon' },
  { id: 'on_sol_camurluk',   label: 'Ön Sol Çamurluk',    gridArea: 'on-sol-camurluk' },
  { id: 'kaput',             label: 'Kaput',              gridArea: 'kaput' },
  { id: 'on_sag_camurluk',   label: 'Ön Sağ Çamurluk',    gridArea: 'on-sag-camurluk' },
  { id: 'on_sol_kapi',       label: 'Ön Sol Kapı',        gridArea: 'on-sol-kapi' },
  { id: 'tavan',             label: 'Tavan',              gridArea: 'tavan' },
  { id: 'on_sag_kapi',       label: 'Ön Sağ Kapı',        gridArea: 'on-sag-kapi' },
  { id: 'arka_sol_kapi',     label: 'Arka Sol Kapı',      gridArea: 'arka-sol-kapi' },
  { id: 'arka_sag_kapi',     label: 'Arka Sağ Kapı',      gridArea: 'arka-sag-kapi' },
  { id: 'arka_sol_camurluk', label: 'Arka Sol Çamurluk',  gridArea: 'arka-sol-camurluk' },
  { id: 'bagaj',             label: 'Bagaj',              gridArea: 'bagaj' },
  { id: 'arka_sag_camurluk', label: 'Arka Sağ Çamurluk',  gridArea: 'arka-sag-camurluk' },
  { id: 'arka_tampon',       label: 'Arka Tampon',        gridArea: 'arka-tampon' },
]

const DAMAGE_STATES = {
  0: { label: 'Orijinal', color: '#f1f5f9' },
  1: { label: 'Sürtme',   color: '#fef9c3' },
  2: { label: 'Göçük',    color: '#fed7aa' },
  3: { label: 'Çizik',    color: '#fecaca' },
  4: { label: 'Leke',     color: '#dbeafe' },
  5: { label: 'Çatlak',   color: '#e9d5ff' },
  6: { label: 'Eksik',    color: '#fda4af' },
}

function fuelLabel(v) {
  return { 0: 'E', 1: '1/8', 2: '1/4', 3: '3/8', 4: '1/2', 5: '5/8', 6: '3/4', 7: '7/8', 8: 'F' }[v] ?? '—'
}

function clickPart(id) {
  activePart.value = activePart.value === id ? null : id
}

function setDamage(partId, stateVal) {
  if (stateVal === 0) delete form.value.damage_map[partId]
  else form.value.damage_map[partId] = stateVal
  activePart.value = null
}

onMounted(async () => {
  try {
    const res = await axios.get(`/api/reservations/${route.params.id}/`)
    reservation.value = res.data
  } catch {
    error.value = 'Rezervasyon bulunamadı.'
  } finally {
    loading.value = false
  }
})

async function submit() {
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
    setTimeout(() => router.back(), 1000)
  } catch (e) {
    error.value = e.response?.data?.error || 'İşlem başarısız.'
  } finally {
    saving.value = false
  }
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
.form-card { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); display: flex; flex-direction: column; gap: 16px; max-width: 700px; }
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
.car-figure { display: grid; grid-template-areas: "on-tampon on-tampon on-tampon" "on-sol-camurluk kaput on-sag-camurluk" "on-sol-kapi tavan on-sag-kapi" "arka-sol-kapi tavan arka-sag-kapi" "arka-sol-camurluk bagaj arka-sag-camurluk" "arka-tampon arka-tampon arka-tampon"; grid-template-columns: 1fr 1.4fr 1fr; gap: 3px; background: #cbd5e1; border-radius: 8px; padding: 3px; overflow: visible; }
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
.form-actions { display: flex; justify-content: flex-end; }
.btn-save { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-save:hover:not(:disabled) { background: #4f46e5; }
.btn-save:disabled { background: #a5b4fc; cursor: not-allowed; }
.error { color: #dc2626; font-size: 13px; margin: 0; }
.success { color: #16a34a; font-size: 13px; margin: 0; }
</style>

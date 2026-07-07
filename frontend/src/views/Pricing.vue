<template>
  <div class="content">
    <div class="section-header">
      <h2>Fiyatlandırma</h2>
    </div>

    <div class="calendar-container">
      <FullCalendar :options="calendarOptions" ref="calendarRef" />
    </div>
  </div>

  <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
    <div class="modal">
      <h3>Fiyat Belirle</h3>
      <div class="modal-info">
        <span class="info-chip">{{ groupLabel(pendingGroup) }}</span>
        <span class="info-chip">{{ pendingStart }} → {{ pendingEnd }}</span>
      </div>
      <div class="field">
        <label>Günlük Ücret (₺)</label>
        <input v-model="priceInput" type="number" min="1" step="1" placeholder="0" autofocus @keyup.enter="savePrice" />
      </div>
      <p v-if="modalError" class="error-msg">{{ modalError }}</p>
      <div class="modal-actions">
        <button class="btn-cancel-modal" @click="showModal = false">Vazgeç</button>
        <button class="btn-save" @click="savePrice">Kaydet</button>
      </div>
    </div>
  </div>

  <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
    <div class="modal modal-sm">
      <h3>Fiyatı Sil</h3>
      <p class="confirm-text">
        <strong>{{ groupLabel(deleteTarget?.group) }}</strong> — {{ deleteTarget?.date }} tarihli fiyat silinsin mi?
      </p>
      <div class="modal-actions">
        <button class="btn-cancel-modal" @click="showDeleteModal = false">Vazgeç</button>
        <button class="btn-delete-confirm" @click="doDelete">Sil</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import FullCalendar from '@fullcalendar/vue3'
import ResourceTimelinePlugin from '@fullcalendar/resource-timeline'
import InteractionPlugin from '@fullcalendar/interaction'
import trLocale from '@fullcalendar/core/locales/tr'

const calendarRef = ref(null)
const showModal = ref(false)
const showDeleteModal = ref(false)
const priceInput = ref('')
const modalError = ref('')
const pendingStart = ref('')
const pendingEnd = ref('')
const pendingGroup = ref('')
const deleteTarget = ref(null)

const groupLabels = { economy: 'Ekonomi', mid: 'Orta Sınıf', suv: 'SUV' }
function groupLabel(g) { return groupLabels[g] || g }

const groupColors = {
  economy: { bg: '#ede9fe', border: '#7c3aed', text: '#5b21b6' },
  mid:     { bg: '#dbeafe', border: '#2563eb', text: '#1e40af' },
  suv:     { bg: '#d1fae5', border: '#059669', text: '#065f46' },
}

async function loadPrices() {
  const res = await axios.get('/api/daily-prices/')
  const api = calendarRef.value?.getApi()
  if (!api) return
  api.removeAllEvents()
  res.data.forEach(p => {
    const c = groupColors[p.vehicle_group] || {}
    const next = new Date(p.date + 'T00:00:00')
    next.setDate(next.getDate() + 1)
    api.addEvent({
      id: String(p.id),
      resourceId: p.vehicle_group,
      title: `${p.price_per_day} ₺`,
      start: p.date,
      end: next.toISOString().slice(0, 10),
      backgroundColor: c.bg,
      borderColor: c.border,
      textColor: c.text,
      extendedProps: { dbId: p.id, group: p.vehicle_group, date: p.date },
    })
  })
}

function toISO(d) {
  const dt = new Date(d)
  return `${dt.getFullYear()}-${String(dt.getMonth()+1).padStart(2,'0')}-${String(dt.getDate()).padStart(2,'0')}`
}

function prevDay(isoStr) {
  const d = new Date(isoStr + 'T00:00:00')
  d.setDate(d.getDate() - 1)
  return toISO(d)
}

const calendarOptions = computed(() => ({
  plugins: [ResourceTimelinePlugin, InteractionPlugin],
  initialView: 'resourceTimelineMonth',
  schedulerLicenseKey: 'non-commercial-and-evaluation',
  locale: trLocale,
  height: 'auto',
  selectable: true,
  selectMirror: true,
  slotDuration: { days: 1 },
  resourceAreaWidth: '160px',
  resourceAreaHeaderContent: 'Araç Grubu',
  slotLabelFormat: [{ month: 'long', year: 'numeric' }, { day: 'numeric', weekday: 'short' }],
  headerToolbar: { left: 'prev,next today', center: 'title', right: '' },
  resources: [
    { id: 'economy', title: 'Ekonomi' },
    { id: 'mid',     title: 'Orta Sınıf' },
    { id: 'suv',     title: 'SUV' },
  ],
  events: [],
  select(info) {
    pendingGroup.value = info.resource?.id || 'economy'
    pendingStart.value = toISO(info.start)
    pendingEnd.value = prevDay(toISO(info.end))
    priceInput.value = ''
    modalError.value = ''
    showModal.value = true
    calendarRef.value?.getApi().unselect()
  },
  eventClick(info) {
    deleteTarget.value = {
      id: info.event.extendedProps.dbId,
      group: info.event.extendedProps.group,
      date: info.event.extendedProps.date,
    }
    showDeleteModal.value = true
  },
  datesSet() {
    loadPrices()
  },
}))

async function savePrice() {
  modalError.value = ''
  if (!priceInput.value || Number(priceInput.value) <= 0) {
    modalError.value = 'Geçerli bir fiyat girin.'
    return
  }
  try {
    await axios.post('/api/daily-prices/bulk_set/', {
      start_date: pendingStart.value,
      end_date: pendingEnd.value,
      vehicle_group: pendingGroup.value,
      price_per_day: priceInput.value,
    })
    showModal.value = false
    await loadPrices()
  } catch {
    modalError.value = 'Kaydetme başarısız.'
  }
}

async function doDelete() {
  await axios.delete(`/api/daily-prices/${deleteTarget.value.id}/`)
  showDeleteModal.value = false
  deleteTarget.value = null
  await loadPrices()
}
</script>

<style scoped>
.content { padding: 32px 40px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0; }
.calendar-container { background: white; border-radius: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); padding: 20px; }
.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.45); backdrop-filter: blur(2px); z-index: 200; display: flex; align-items: center; justify-content: center; animation: overlayIn 0.15s ease; }
@keyframes overlayIn { from { opacity: 0; } to { opacity: 1; } }
.modal { background: white; border-radius: 14px; padding: 32px; width: 380px; box-shadow: 0 20px 60px rgba(15,23,42,0.25); display: flex; flex-direction: column; gap: 16px; animation: modalIn 0.18s cubic-bezier(0.4,0,0.2,1); }
@keyframes modalIn { from { opacity: 0; transform: translateY(8px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal-sm { width: 340px; }
.modal h3 { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0; }
.modal-info { display: flex; gap: 8px; flex-wrap: wrap; }
.info-chip { padding: 4px 12px; background: #f1f5f9; border-radius: 50px; font-size: 12px; font-weight: 600; color: #475569; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; text-transform: uppercase; }
.field input { padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; transition: border-color 0.15s, box-shadow 0.15s; }
.field input:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }
.confirm-text { font-size: 14px; color: #374151; margin: 0; }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; }
.btn-cancel-modal { padding: 8px 16px; background: white; color: #64748b; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-size: 14px; transition: background 0.15s, border-color 0.15s; }
.btn-cancel-modal:hover { background: #f8fafc; border-color: #cbd5e1; }
.btn-save { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; transition: background 0.15s, transform 0.15s; }
.btn-save:hover { background: #4f46e5; transform: translateY(-1px); }
.btn-delete-confirm { padding: 8px 20px; background: #dc2626; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; transition: background 0.15s, transform 0.15s; }
.btn-delete-confirm:hover { background: #b91c1c; transform: translateY(-1px); }
.error-msg { color: #dc2626; font-size: 13px; margin: 0; }
</style>

<style>
.fc .fc-timeline-slot-label { color: #1e293b !important; }
.fc .fc-col-header-cell-cushion { color: #1e293b !important; }
.fc .fc-resource-area { background: #f8fafc; }
</style>

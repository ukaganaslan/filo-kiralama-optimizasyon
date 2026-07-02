<template>
  <div class="content">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Aktif Rezervasyon</div>
        <div class="stat-value">{{ activeCount }}</div>
        <div class="stat-sub">({{ cancelledCount }} iptal)</div>
      </div>
      <div class="stat-card stat-amber">
        <div class="stat-label">Bekleyen</div>
        <div class="stat-value">{{ pendingCount }}</div>

      </div>
      <div class="stat-card stat-green">
        <div class="stat-label">Onaylandı</div>
        <div class="stat-value">{{ assignedCount }}</div>

      </div>
    </div>

    <div class="section-header">
      <h2>Tüm Rezervasyonlar</h2>
      <div class="header-actions">
        <select v-if="activeView === 'list'" v-model="selectedMonth" class="view-select">
          <option value="">Tüm Aylar</option>
          <option v-for="m in availableMonths" :key="m" :value="m">{{ formatMonth(m) }}</option>
        </select>
        <select v-model="activeView" class="view-select">
          <option value="list">Liste Görünümü</option>
          <option value="calendar">Takvim Görünümü</option>
        </select>
      </div>
    </div>

    <FullCalendar v-if="activeView === 'calendar'" :options="calendarOptions" />

    <table v-if="activeView === 'list'">
      <thead>
        <tr>
          <th>ID</th>
          <th>Araç</th>
          <th>Müşteri</th>
          <th>Şube</th>
          <th>İade Şube</th>
          <th>Grup</th>
          <th>Başlangıç</th>
          <th>Bitiş</th>
          <th>Tutar</th>
          <th>Durum</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in filteredReservations" :key="r.id" @click="openDetail(r)" style="cursor: pointer;">
          <td>{{ r.reservation_id }}</td>
          <td>{{ r.assigned_vehicle_id }}</td>
          <td>{{ r.customer_username || `Misafir - ${r.guest_name}` }}</td>
          <td>{{ r.branch_title }}</td>
          <td>{{ r.return_branch ? (r.return_branch_title || r.return_branch_name) : (r.branch_title || r.branch_name) }}</td>
          <td>{{ r.vehicle_group }}</td>
          <td>{{ r.start_date }}</td>
          <td>{{ r.end_date }}</td>
          <td><span v-if="r.total_price" class="price-badge">{{ Number(r.total_price).toLocaleString('tr-TR') }} ₺</span><span v-else class="price-na">—</span></td>
          <td><span :class="'badge ' + reservationStatus(r).cls">{{ reservationStatus(r).label }}</span></td>
          <td class="actions">
            <div class="action-menu" @click.stop>
              <button class="btn-dots" @click="toggleMenu(r.id)">···</button>
              <div v-if="openMenuId === r.id" class="action-dropdown">
                <button class="danger" @click="deleteReservation(r); openMenuId = null">Sil</button>
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="detailModal && selectedReservation" class="modal-overlay" @click.self="detailModal = false">
  <div class="detail-modal">

    <div class="detail-header">
      <div class="detail-header-left">
        <span class="detail-res-id">{{ selectedReservation.reservation_id }}</span>
        <span :class="'badge badge-' + selectedReservation.status">{{ statusLabel(selectedReservation.status) }}</span>
      </div>
      <button class="detail-close" @click="detailModal = false">✕</button>
    </div>

    <div class="detail-info-grid">
      <div class="detail-info-item">
        <span class="detail-info-label">MÜŞTERİ</span>
        <span class="detail-info-value">{{ selectedReservation.customer_username || selectedReservation.guest_name || '—' }}</span>
      </div>
      <div class="detail-info-item">
        <span class="detail-info-label">ARAÇ</span>
        <span class="detail-info-value">{{ selectedReservation.assigned_vehicle_id || '—' }}</span>
      </div>
      <div class="detail-info-item">
        <span class="detail-info-label">BAŞLANGIÇ</span>
        <span class="detail-info-value">{{ selectedReservation.start_date }}</span>
      </div>
      <div class="detail-info-item">
        <span class="detail-info-label">BİTİŞ</span>
        <span class="detail-info-value">{{ selectedReservation.end_date }}</span>
      </div>
    </div>

    <div v-if="canDeliver || selectedReservation.delivery_info?.delivered" class="process-section">
      <div class="process-section-header">
        <span class="process-title">Araç Teslimi</span>
        <span v-if="selectedReservation.delivery_info?.delivered" class="done-badge">Teslim Edildi</span>
      </div>
      <template v-if="canDeliver">
        <div class="form-actions">
          <button class="btn-save" @click="goToTeslim">Teslim Et</button>
        </div>
      </template>
      <template v-else>
        <div class="done-info">
          <span>KM: <b>{{ selectedReservation.delivery_info.delivered_km ?? '—' }}</b></span>
        </div>
        <div class="form-actions" style="margin-top: 10px;">
          <button class="btn-export" @click="router.push(`/operator/teslim/${selectedReservation.id}`)">PDF İndir</button>
        </div>
      </template>
    </div>

    <div v-if="canReturn || selectedReservation.delivery_info?.returned" class="process-section">
      <div class="process-section-header">
        <span class="process-title">Araç İadesi</span>
        <span v-if="selectedReservation.delivery_info?.returned" class="done-badge done-return">İade Alındı</span>
      </div>
      <template v-if="canReturn">
        <div class="form-actions">
          <button class="btn-save" @click="goToIade">İade Al</button>
        </div>
      </template>
      <template v-else>
        <div class="done-info">
          <span>KM: <b>{{ selectedReservation.delivery_info.returned_km ?? '—' }}</b></span>
        </div>
        <div class="form-actions" style="margin-top: 10px;">
          <button class="btn-export" @click="router.push(`/operator/iade/${selectedReservation.id}`)">PDF İndir</button>
        </div>
      </template>
    </div>

  </div>
</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import axios from 'axios'
import FullCalendar from '@fullcalendar/vue3'
import ResourceTimelinePlugin from '@fullcalendar/resource-timeline'
import trLocale from '@fullcalendar/core/locales/tr'
import { useRouter } from 'vue-router'


const reservations = ref([])
const activeView = ref('list')
const vehicles = ref([])
const openMenuId = ref(null)
const router = useRouter()
const detailModal = ref(false)
const selectedReservation = ref(null)
const bugun = new Date().toISOString().split('T')[0]

const activeCount = computed(() => reservations.value.filter(r => r.status !== 'cancelled').length)
const pendingCount = computed(() => reservations.value.filter(r => r.status === 'pending').length)
const assignedCount = computed(() => reservations.value.filter(r => r.status === 'assigned').length)
const cancelledCount = computed(() => reservations.value.filter(r => r.status === 'cancelled').length)
const totalVehicles = computed(() => vehicles.value.length)
const availableVehicles = computed(() => vehicles.value.filter(v => v.status === 'available').length)
const selectedMonth = ref(new Date().toISOString().slice(0, 7)) 
const availableMonths = computed(() => {
  const months = [...new Set(reservations.value.map(r => r.start_date.slice(0, 7)))]
  return months.sort()
})

const filteredReservations = computed(() =>
  selectedMonth.value
    ? reservations.value.filter(r => r.start_date.startsWith(selectedMonth.value))
    : reservations.value
)

function openDetail(r) {
  selectedReservation.value = r
  detailModal.value = true
}

const canDeliver = computed(() => {
  if (!selectedReservation.value) return false
  const r = selectedReservation.value
  return r.status === 'assigned' && r.start_date <= bugun && !r.delivery_info?.delivered
})

const canReturn = computed(() => {
  if (!selectedReservation.value) return false
  const r = selectedReservation.value
  return r.status === 'assigned' && r.delivery_info?.delivered && !r.delivery_info?.returned
})

function goToTeslim() {
  router.push(`/operator/teslim/${selectedReservation.value.id}`)
}

function goToIade() {
  router.push(`/operator/iade/${selectedReservation.value.id}`)
}

function statusLabel(s) {
  return { pending: 'Bekliyor', assigned: 'Onaylandı', cancelled: 'İptal' }[s] || s
}

function reservationStatus(r) {
  if (r.status === 'cancelled') return { label: 'İptal', cls: 'badge-cancelled' }
  if (r.status === 'pending') return { label: 'Bekliyor', cls: 'badge-pending' }
  if (r.delivery_info?.returned) return { label: 'İade Alındı', cls: 'badge-returned' }
  if (r.delivery_info?.delivered) {
    if (r.end_date == bugun) return { label: 'İade Günü', cls: 'badge-iade' }
    return { label: 'Teslim Edildi', cls: 'badge-delivered' }
  }
  if (r.status == 'assigned' && r.start_date == bugun) return { label: 'Teslim Günü', cls: 'badge-teslimat' }
  return { label: 'Onaylandı', cls: 'badge-assigned' }
}

function toggleMenu(id) { openMenuId.value = openMenuId.value === id ? null : id }
function closeMenu() { openMenuId.value = null }
onMounted(() => document.addEventListener('click', closeMenu))
onUnmounted(() => document.removeEventListener('click', closeMenu))

onMounted(async () => {
  const [rezRes, vehicleRes] = await Promise.all([
    axios.get('/api/reservations/'),
    axios.get('/api/vehicles/'),
  ])
  reservations.value = rezRes.data
  vehicles.value = vehicleRes.data
})


async function deleteReservation(r) {
  if (!confirm(`${r.reservation_id} silinsin mi?`)) return
  await axios.delete(`/api/reservations/${r.id}/`)
  reservations.value = reservations.value.filter(x => x.id !== r.id)
}

const calendarOptions = computed(() => ({
  plugins: [ResourceTimelinePlugin],
  initialView: 'resourceTimelineMonth',
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

function formatMonth(m) {
  const [y, mo] = m.split('-')
  const names = ['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']
  return `${names[parseInt(mo)-1]} ${y}`
}
</script>

<style scoped>
.content {
  padding: 32px 40px;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 28px;
}
.stat-card {
  background: white;
  border-radius: 14px;
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  border-left: 4px solid #6366f1;
}
.stat-card.stat-amber { border-left-color: #f59e0b; }
.stat-card.stat-green { border-left-color: #10b981; }
.stat-card.stat-blue  { border-left-color: #3b82f6; }
.stat-label {
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 32px;
  font-weight: 800;
  color: #1e293b;
  line-height: 1;
  margin-bottom: 6px;
}
.stat-denom {
  font-size: 18px;
  font-weight: 600;
  color: #94a3b8;
}
.stat-sub {
  font-size: 12px;
  color: #94a3b8;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.view-select {
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 13px;
  color: #475569;
  background: white;
  cursor: pointer;
  outline: none;
}
.view-select:focus { border-color: #6366f1; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0 0 16px; }
.btn-optimize {
  padding: 10px 24px;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.btn-optimize:disabled { background: #a5b4fc; cursor: not-allowed; }
table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th:first-child { border-radius: 8px 0 0 0; }
th:last-child { border-radius: 0 8px 0 0; }
th {
  background: #f1f5f9;
  font-weight: 600;
  color: #475569;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
td { border-top: 1px solid #f1f5f9; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
.actions { text-align: center !important; }
.action-menu { position: relative; display: inline-block; }
.btn-dots { background: none; border: 1px solid #e2e8f0; border-radius: 6px; padding: 4px 10px; cursor: pointer; font-size: 16px; color: #64748b; line-height: 1; letter-spacing: 2px; }
.btn-dots:hover { background: #f1f5f9; }
.action-dropdown { position: absolute; right: 0; top: calc(100% + 4px); background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); min-width: 100px; z-index: 300; overflow: hidden; }
.action-dropdown button { display: block; width: 100%; padding: 9px 14px; text-align: left; background: none; border: none; font-size: 13px; color: #374151; cursor: pointer; }
.action-dropdown button:hover { background: #f8fafc; }
.action-dropdown button.danger { color: #dc2626; }
.action-dropdown button.danger:hover { background: #fee2e2; }
.price-badge { font-size: 13px; font-weight: 700; color: #000000; }
.price-na { color: #94a3b8; }
td:nth-child(1), th:nth-child(1), td:nth-child(2), th:nth-child(2), td:nth-child(3), th:nth-child(3), td:nth-child(4), th:nth-child(4), td:nth-child(5), th:nth-child(5), td:nth-child(6), th:nth-child(6), td:nth-child(7), th:nth-child(7), td:nth-child(8), th:nth-child(8), td:nth-child(9), th:nth-child(9), td:nth-child(10), th:nth-child(10) { text-align: center; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 200; display: flex; align-items: center; justify-content: center; }
.detail-modal { background: white; border-radius: 14px; padding: 28px; width: 600px; max-height: 85vh; overflow-y: auto; box-shadow: 0 8px 32px rgba(0,0,0,0.14); display: flex; flex-direction: column; gap: 20px; }
.detail-header { display: flex; justify-content: space-between; align-items: center; }
.detail-header-left { display: flex; align-items: center; gap: 10px; }
.detail-res-id { font-size: 18px; font-weight: 700; color: #1e293b; font-family: monospace; }
.detail-close { background: none; border: none; font-size: 18px; color: #94a3b8; cursor: pointer; padding: 4px 8px; border-radius: 6px; }
.detail-close:hover { background: #f1f5f9; color: #1e293b; }
.detail-info-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: #e2e8f0; border-radius: 10px; overflow: hidden; }
.detail-info-item { background: white; padding: 12px 14px; }
.detail-info-label { display: block; font-size: 10px; font-weight: 700; color: #94a3b8; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 3px; }
.detail-info-value { display: block; font-size: 13px; font-weight: 600; color: #1e293b; }
.process-section { border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.process-section-header { display: flex; justify-content: space-between; align-items: center; }
.process-title { font-size: 14px; font-weight: 700; color: #1e293b; }
.done-badge { padding: 3px 10px; background: #d1fae5; color: #065f46; border-radius: 50px; font-size: 12px; font-weight: 600; }
.done-badge.done-return { background: #e9d5ff; color: #6b21a8; }
.done-info { display: flex; gap: 16px; font-size: 13px; color: #475569; }
.form-actions { display: flex; justify-content: flex-end; }
.btn-save { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-save:hover { background: #4f46e5; }
.btn-export { padding: 8px 20px; background: #1e293b; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-export:hover { background: #0f172a; }
.badge-delivered { background: #d1fae5; color: #065f46; }
.badge-returned { background: #e9d5ff; color: #6b21a8; }
</style>

<style>
.fc .fc-timeline-slot-label { color: #1e293b !important; }
.fc .fc-col-header-cell-cushion { color: #1e293b !important; }
</style>


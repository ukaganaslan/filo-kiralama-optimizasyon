<template>
  <div class="content">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Aktif Rezervasyon</div>
        <div class="stat-value">{{ activeCount }}</div>
        <div class="stat-sub">{{ cancelledCount }} iptal</div>
      </div>
      <div class="stat-card stat-amber">
        <div class="stat-label">Bekleyen</div>
        <div class="stat-value">{{ pendingCount }}</div>
        <div class="stat-sub">atama bekliyor</div>
      </div>
      <div class="stat-card stat-green">
        <div class="stat-label">Atandı</div>
        <div class="stat-value">{{ assignedCount }}</div>
        <div class="stat-sub">aktif rezervasyon</div>
      </div>
      <div class="stat-card stat-blue">
        <div class="stat-label">Araç Filosu</div>
        <div class="stat-value">{{ availableVehicles }}<span class="stat-denom"> / {{ totalVehicles }}</span></div>
        <div class="stat-sub">müsait araç</div>
      </div>
    </div>

    <div class="section-header">
      <h2>Tüm Rezervasyonlar</h2>
      <div class="header-actions">
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
          <th>Müşteri</th>
          <th>Şube</th>
          <th>İade Şube</th>
          <th>Grup</th>
          <th>Başlangıç</th>
          <th>Bitiş</th>
          <th>Durum</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in reservations" :key="r.id">
          <td>{{ r.reservation_id }}</td>
          <td>{{ r.customer_username || `Misafir - ${r.guest_name}` }}</td>
          <td>{{ r.branch_title }}</td>
          <td>{{ r.return_branch_title || r.branch_title }}</td>
          <td>{{ r.vehicle_group }}</td>
          <td>{{ r.start_date }}</td>
          <td>{{ r.end_date }}</td>
          <td><span :class="'badge badge-' + r.status">{{ r.status }}</span></td>
          <td><button class="btn-del" @click="deleteReservation(r)">🗑️</button></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import FullCalendar from '@fullcalendar/vue3'
import ResourceTimelinePlugin from '@fullcalendar/resource-timeline'
import trLocale from '@fullcalendar/core/locales/tr'

const reservations = ref([])
const activeView = ref('list')
const vehicles = ref([])

const activeCount = computed(() => reservations.value.filter(r => r.status !== 'cancelled').length)
const pendingCount = computed(() => reservations.value.filter(r => r.status === 'pending').length)
const assignedCount = computed(() => reservations.value.filter(r => r.status === 'assigned').length)
const cancelledCount = computed(() => reservations.value.filter(r => r.status === 'cancelled').length)
const totalVehicles = computed(() => vehicles.value.length)
const availableVehicles = computed(() => vehicles.value.filter(v => v.status === 'available').length)

onMounted(async () => {
  const [rezRes, vehicleRes] = await Promise.all([
    axios.get('http://127.0.0.1:8000/api/reservations/'),
    axios.get('http://127.0.0.1:8000/api/vehicles/'),
  ])
  reservations.value = rezRes.data
  vehicles.value = vehicleRes.data
})


async function deleteReservation(r) {
  if (!confirm(`${r.reservation_id} silinsin mi?`)) return
  await axios.delete(`http://127.0.0.1:8000/api/reservations/${r.id}/`)
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
</script>

<style scoped>
.content {
  padding: 32px 40px;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
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
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th {
  background: #f1f5f9;
  font-weight: 600;
  color: #475569;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
td { border-top: 1px solid #f1f5f9; }
.badge { padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: 600; }
.badge-pending { background: #fef3c7; color: #92400e; }
.badge-assigned { background: #d1fae5; color: #065f46; }
.badge-cancelled { background: #fee2e2; color: #991b1b; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
.btn-del { background: none; border: none; cursor: pointer; font-size: 16px; opacity: 0.4; padding: 4px 8px; border-radius: 6px; }
.btn-del:hover { opacity: 1; background: #fee2e2; }
td:nth-child(1), th:nth-child(1), td:nth-child(2), th:nth-child(2), td:nth-child(3), th:nth-child(3), td:nth-child(4), th:nth-child(4), td:nth-child(5), th:nth-child(5), td:nth-child(6), th:nth-child(6), td:nth-child(7), th:nth-child(7), td:nth-child(8), th:nth-child(8), td:nth-child(9), th:nth-child(9) { text-align: center; }
</style>

<style>
.fc .fc-timeline-slot-label { color: #1e293b !important; }
.fc .fc-col-header-cell-cushion { color: #1e293b !important; }
</style>

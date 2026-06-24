<template>
  <div class="content">
    <div class="section-header">
      <h2>Tüm Rezervasyonlar</h2>
      <div class="header-actions">
        <select v-model="activeView" class="view-select">
          <option value="list">Liste Görünümü</option>
          <option value="calendar">Takvim Görünümü</option>
        </select>
        <button class="btn-optimize" @click="handleOptimize" :disabled="optimizing">
          {{ optimizing ? 'Çalışıyor...' : 'Optimize Et →' }}
        </button>
      </div>
    </div>

    <FullCalendar v-if="activeView === 'calendar'" :options="calendarOptions" />

    <table v-if="activeView === 'list'">
      <thead>
        <tr>
          <th>ID</th>
          <th>Müşteri</th>
          <th>Şube</th>
          <th>Grup</th>
          <th>Başlangıç</th>
          <th>Bitiş</th>
          <th>Durum</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in reservations" :key="r.id">
          <td>{{ r.reservation_id }}</td>
          <td>{{ r.customer_username }}</td>
          <td>{{ r.branch_name }}</td>
          <td>{{ r.vehicle_group }}</td>
          <td>{{ r.start_date }}</td>
          <td>{{ r.end_date }}</td>
          <td><span :class="'badge badge-' + r.status">{{ r.status }}</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useOptimizationStore } from '../stores/optimization'
import FullCalendar from '@fullcalendar/vue3'
import ResourceTimelinePlugin from '@fullcalendar/resource-timeline'
import trLocale from '@fullcalendar/core/locales/tr'

const optimizationStore = useOptimizationStore()
const reservations = ref([])
const optimizing = ref(false)
const activeView = ref('list')
const vehicles = ref([])

onMounted(async () => {
  const [rezRes, vehicleRes] = await Promise.all([
    axios.get('http://127.0.0.1:8000/api/reservations/'),
    axios.get('http://127.0.0.1:8000/api/vehicles/'),
  ])
  reservations.value = rezRes.data
  vehicles.value = vehicleRes.data
})

async function handleOptimize() {
  optimizing.value = true
  try {
    const res = await axios.post('http://127.0.0.1:8000/api/optimize/')
    optimizationStore.setResult(res.data)
    const rezRes = await axios.get('http://127.0.0.1:8000/api/reservations/')
    reservations.value = rezRes.data
  } finally {
    optimizing.value = false
  }
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
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px;
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
</style>

<style>
.fc .fc-timeline-slot-label { color: #1e293b !important; }
.fc .fc-col-header-cell-cushion { color: #1e293b !important; }
</style>

<template>
  <div class="content">
    <div class="section-header">
      <div class="header-left">
        <h2>Şube Araçları</h2>
        <span class="count-badge">{{ vehicles.length }} araç</span>
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th>Araç ID</th>
          <th>Grup</th>
          <th>Marka / Model</th>
          <th>Plaka</th>
          <th>Toplam Rez.</th>
          <th>Durum</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="v in vehicles" :key="v.id">
          <td class="id">{{ v.vehicle_id }}</td>
          <td>{{ groupLabel(v.group) }}</td>
          <td>{{ v.brand }} {{ v.model }}</td>
          <td>{{ v.plate || '—' }}</td>
          <td><span class="rez-count">{{ v.total_reservations }}</span></td>
          <td><span :class="'badge badge-' + v.status">{{ statusLabel(v.status) }}</span></td>
        </tr>
        <tr v-if="vehicles.length === 0">
          <td colspan="6" class="empty">Bu şubede araç bulunamadı.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const vehicles = ref([])

onMounted(async () => {
  const res = await axios.get('http://127.0.0.1:8000/api/vehicles/')
  vehicles.value = res.data
})

function groupLabel(g) {
  return { economy: 'Ekonomi', mid: 'Orta Sınıf', suv: 'SUV' }[g] || g
}

function statusLabel(s) {
  return { available: 'Müsait', rented: 'Kirada', maintenance: 'Bakımda' }[s] || s
}
</script>

<style scoped>
.content { max-width: 1100px; margin: 0 auto; padding: 40px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-left { display: flex; align-items: center; gap: 12px; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0; }
.count-badge { padding: 3px 10px; background: #f1f5f9; color: #64748b; border-radius: 50px; font-size: 12px; font-weight: 600; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
td { border-top: 1px solid #f1f5f9; color: #374151; }
.id { font-family: monospace; font-weight: 600; color: #1e293b; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
.rez-count { display: inline-block; padding: 2px 10px; background: #ede9fe; color: #5b21b6; border-radius: 50px; font-size: 12px; font-weight: 600; }
.badge { padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: 600; }
.badge-available { background: #d1fae5; color: #065f46; }
.badge-rented { background: #fef3c7; color: #92400e; }
.badge-maintenance { background: #fee2e2; color: #991b1b; }
</style>

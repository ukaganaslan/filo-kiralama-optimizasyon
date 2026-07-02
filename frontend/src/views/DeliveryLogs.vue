<template>
  <div class="content">
    <div class="section-header">
      <h2>Teslimat ve İade Kayıtları</h2>
      <span class="count-badge">{{ logs.length }} kayıt</span>
    </div>

    <div v-if="logs.length === 0" class="empty">Henüz log kaydı yok.</div>

    <table v-else>
      <thead>
        <tr>
          <th>Rezervasyon</th>
          <th>Şube</th>
          <th>Araç Plakası</th>
          <th>Müşteri</th>
          <th>Grup</th>
          <th>Başlangıç</th>
          <th>Bitiş</th>
          <th>Tutar</th>
          <th>Durum</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="log in logs" :key="log.reservation_id + log.event_type">
          <td class="res-id">#{{ log.reservation_id }}</td>
          <td>{{ log.branch_name }}</td>
          <td>{{ log.assigned_vehicle_plate }}</td>
          <td>{{ log.customer }}</td>
          <td>{{ groupLabel(log.vehicle_group) }}</td>
          <td>{{ log.start_date }}</td>
          <td>{{ log.end_date }}</td>
          <td><span v-if="log.total_price" class="price-badge">{{ Number(log.total_price).toLocaleString('tr-TR') }} ₺</span><span v-else class="price-na">—</span></td>
          <td><span :class="'badge-event-' + log.event_type">{{ eventLabel(log.event_type) }}</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const logs = ref([])

onMounted(async () => {
  const res = await axios.get('/api/delivery-logs/')
  logs.value = res.data
})

function groupLabel(g) {
  return { economy: 'Ekonomi', mid: 'Orta Sınıf', suv: 'SUV' }[g] || g
}

function eventLabel(e) {
  return { delivered: 'Teslim Edildi', returned: 'İade Alındı' }[e] || e
}

function formatDate(dt) {
  return new Date(dt).toLocaleString('tr-TR')
}
</script>

<style scoped>
.content { padding: 32px 40px; }
.section-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0; }
.count-badge { padding: 3px 10px; background: #f1f5f9; color: #64748b; border-radius: 50px; font-size: 12px; font-weight: 600; }
.empty { text-align: center; color: #94a3b8; padding: 48px; background: white; border-radius: 14px; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 14px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
td { border-top: 1px solid #f1f5f9; color: #374151; }
td:nth-child(1), th:nth-child(1), td:nth-child(2), th:nth-child(2), td:nth-child(3), th:nth-child(3), td:nth-child(4), th:nth-child(4), td:nth-child(5), th:nth-child(5), td:nth-child(6), th:nth-child(6), td:nth-child(7), th:nth-child(7), td:nth-child(8), th:nth-child(8), td:nth-child(9), th:nth-child(9), td:nth-child(10), th:nth-child(10) { text-align: center; }
.res-id { font-weight: 700; color: #000000; font-family: monospace; }
.price-badge { font-size: 13px; font-weight: 700; color: #000000; }
.price-na { color: #94a3b8; }
.badge-event-delivered { background: #d1fae5; color: #065f46; display: inline-block; padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: 600; }
.badge-event-returned { background: #e9d5ff; color: #6b21a8; display: inline-block; padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: 600; }
</style>

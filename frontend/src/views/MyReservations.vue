<template>
  <div class="content">
    <h2>Rezervasyonlarım</h2>
    <p v-if="reservations.length === 0" class="empty">Henüz rezervasyonunuz yok.</p>
    <table v-else>
      <thead>
        <tr>
          <th>ID</th>
          <th>Şube</th>
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
          <td>{{ r.branch_name }}</td>
          <td>{{ r.vehicle_group }}</td>
          <td>{{ r.start_date }}</td>
          <td>{{ r.end_date }}</td>
          <td><span :class="'badge badge-' + r.status">{{ r.status }}</span></td>
          <td>
            <button
              v-if="r.status !== 'cancelled'"
              class="btn-cancel"
              @click="handleCancel(r.reservation_id)"
            >İptal Et</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const reservations = ref([])
const error = ref('')

onMounted(async () => {
  const res = await axios.get('http://127.0.0.1:8000/api/reservations/')
  reservations.value = res.data
})

async function handleCancel(reservationId) {
  try {
    await axios.post(`http://127.0.0.1:8000/api/reservations/${reservationId}/cancel/`)
    const res = await axios.get('http://127.0.0.1:8000/api/reservations/')
    reservations.value = res.data
  } catch {
    error.value = 'İptal işlemi başarısız.'
  }
}
</script>

<style scoped>
.content { max-width: 900px; margin: 0 auto; padding: 40px; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 16px; }
.empty { color: #94a3b8; font-size: 14px; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
td { border-top: 1px solid #f1f5f9; }
.badge { padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: 600; }
.badge-pending { background: #fef3c7; color: #92400e; }
.badge-assigned { background: #d1fae5; color: #065f46; }
.badge-cancelled { background: #fee2e2; color: #991b1b; }
.btn-cancel { padding: 4px 12px; background: white; color: #dc2626; border: 1px solid #dc2626; border-radius: 50px; font-size: 12px; cursor: pointer; }
.btn-cancel:hover { background: #fee2e2; }
.error { color: #dc2626; font-size: 14px; margin-top: 12px; }
</style>

<template>
  <div class="content">
    <div class="section-header">
      <div class="section-title">
        <span>Rezervasyonlarım</span>
        <span v-if="reservations.length" class="count-badge">{{ reservations.length }}</span>
      </div>
    </div>

    <div v-if="reservations.length === 0" class="empty-state">
      <div class="empty-icon">📋</div>
      <p>Henüz rezervasyonunuz yok.</p>
      <p class="empty-sub">Yeni bir araç kiralamak için "Yeni Rezervasyon" bölümüne gidin.</p>
    </div>

    <div v-else class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Rezervasyon No</th>
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
            <td class="res-id">#{{ r.reservation_id }}</td>
            <td>{{ r.branch_name }}</td>
            <td>{{ groupLabel(r.vehicle_group) }}</td>
            <td>{{ r.start_date }}</td>
            <td>{{ r.end_date }}</td>
            <td><span :class="'badge badge-' + r.status">{{ statusLabel(r.status) }}</span></td>
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
    </div>

    <p v-if="error" class="error-msg">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const reservations = ref([])
const error = ref('')

const groupLabels = { economy: 'Ekonomi', mid: 'Orta Sınıf', suv: 'SUV' }
function groupLabel(v) { return groupLabels[v] || v }
function statusLabel(s) {
  if (s === 'pending') return 'Bekliyor'
  if (s === 'assigned') return 'Atandı'
  if (s === 'cancelled') return 'İptal'
  return s
}

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
.content { padding: 32px 40px; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.section-title { display: flex; align-items: center; gap: 10px; font-size: 20px; font-weight: 800; color: #0f172a; }
.count-badge { background: #ede9fe; color: #6366f1; font-size: 13px; font-weight: 700; padding: 2px 10px; border-radius: 50px; }
.empty-state { text-align: center; padding: 60px 24px; background: white; border-radius: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.empty-icon { font-size: 36px; margin-bottom: 12px; }
.empty-state p { color: #475569; font-size: 15px; font-weight: 600; margin: 0 0 6px; }
.empty-sub { color: #94a3b8; font-size: 13px; font-weight: 400 !important; }
.table-wrap { background: white; border-radius: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); overflow: hidden; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f8fafc; font-weight: 700; color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; border-bottom: 1px solid #f1f5f9; }
td { border-top: 1px solid #f8fafc; color: #1e293b; }
tr:hover td { background: #fafbff; }
.res-id { font-weight: 700; color: #6366f1; font-size: 13px; }
.badge { padding: 4px 10px; border-radius: 50px; font-size: 12px; font-weight: 700; }
.badge-pending { background: #fef3c7; color: #92400e; }
.badge-assigned { background: #dcfce7; color: #15803d; }
.badge-cancelled { background: #fee2e2; color: #991b1b; }
.btn-cancel { padding: 5px 12px; background: white; color: #dc2626; border: 1.5px solid #fca5a5; border-radius: 7px; font-size: 12px; font-weight: 600; cursor: pointer; transition: background 0.15s; }
.btn-cancel:hover { background: #fff1f2; border-color: #dc2626; }
.error-msg { color: #dc2626; font-size: 13px; margin-top: 12px; background: #fff1f2; padding: 10px 14px; border-radius: 8px; }
</style>

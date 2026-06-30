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
            <th>Tutar</th>
            <th>Durum</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in reservations" :key="r.id">
            <td class="res-id">#{{ r.reservation_id }}</td>
            <td>{{ r.branch_title }}</td>
            <td>{{ groupLabel(r.vehicle_group) }}</td>
            <td>{{ r.start_date }}</td>
            <td>{{ r.end_date }}</td>
            <td>
              <span v-if="r.total_price" class="price-badge">{{ Number(r.total_price).toLocaleString('tr-TR') }} ₺</span>
              <span v-else class="price-na">—</span>
            </td>
            <td>
              <span :class="'badge badge-' + displayStatusKey(r)">{{ displayStatus(r) }}</span>
              <div v-if="r.assigned_vehicle_info" class="vehicle-info">
                {{ r.assigned_vehicle_info.brand }} {{ r.assigned_vehicle_info.model }} · {{ r.assigned_vehicle_info.plate }}
              </div>
            </td>
            <td class="actions-cell">
              <button class="btn-detail" @click="selectedRes = r">Detay</button>
              <button
                v-if="r.status !== 'cancelled' && new Date(r.start_date + 'T00:00:00' ) > new Date()"
                class="btn-cancel"
                @click="handleCancel(r.reservation_id)"
              >İptal Et</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-if="error" class="error-msg">{{ error }}</p>

    <div v-if="selectedRes" class="modal-overlay" @click.self="selectedRes = null">
      <div class="modal">
        <div class="modal-header">
          <span class="modal-res-id">#{{ selectedRes.reservation_id }}</span>
          <button class="modal-close" @click="selectedRes = null">✕</button>
        </div>

        <div class="modal-grid">
          <div class="mrow"><span class="mlabel">Araç Grubu</span><span class="mval">{{ groupLabel(selectedRes.vehicle_group) }}</span></div>
          <div class="mrow"><span class="mlabel">Tarih</span><span class="mval">{{ selectedRes.start_date }} → {{ selectedRes.end_date }}</span></div>
          <div class="mrow" v-if="selectedRes.assigned_vehicle_info">
            <span class="mlabel">Araç</span>
            <span class="mval">{{ selectedRes.assigned_vehicle_info.brand }} {{ selectedRes.assigned_vehicle_info.model }} · {{ selectedRes.assigned_vehicle_info.plate }}</span>
          </div>
          <div class="mrow" v-if="selectedRes.total_price">
            <span class="mlabel">Tutar</span>
            <span class="mval">{{ Number(selectedRes.total_price).toLocaleString('tr-TR') }} ₺</span>
          </div>
        </div>

        <template v-if="selectedRes.delivery_info?.delivered">
          <div class="modal-section-title">Teslim</div>
          <div class="modal-grid">
            <div class="mrow"><span class="mlabel">Teslim KM</span><span class="mval">{{ selectedRes.delivery_info.delivered_km ?? '—' }}</span></div>
            <div class="mrow"><span class="mlabel">Yakıt</span><span class="mval">{{ fuelLabel(selectedRes.delivery_info.delivered_fuel) }}</span></div>
            <div class="mrow" v-if="selectedRes.delivery_info.delivered_notes">
              <span class="mlabel">Not</span><span class="mval">{{ selectedRes.delivery_info.delivered_notes }}</span>
            </div>
          </div>
          <div class="damage-readonly">
            <CarDamageMap :model-value="selectedRes.delivery_info.delivered_damage || {}" />
          </div>
        </template>

        <template v-if="selectedRes.delivery_info?.returned">
          <div class="modal-section-title">İade</div>
          <div class="modal-grid">
            <div class="mrow"><span class="mlabel">İade KM</span><span class="mval">{{ selectedRes.delivery_info.returned_km ?? '—' }}</span></div>
            <div class="mrow"><span class="mlabel">Yakıt</span><span class="mval">{{ fuelLabel(selectedRes.delivery_info.returned_fuel) }}</span></div>
            <div class="mrow" v-if="selectedRes.delivery_info.returned_notes">
              <span class="mlabel">Not</span><span class="mval">{{ selectedRes.delivery_info.returned_notes }}</span>
            </div>
          </div>
          <div class="damage-readonly">
            <CarDamageMap :model-value="selectedRes.delivery_info.returned_damage || {}" />
          </div>
        </template>

        <div v-if="!selectedRes.delivery_info?.delivered" class="modal-empty">
          Henüz araç teslimi yapılmamış.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import CarDamageMap from '@/components/CarDamageMap.vue'

const reservations = ref([])
const error = ref('')
const selectedRes = ref(null)

const groupLabels = { economy: 'Ekonomi', mid: 'Orta Sınıf', suv: 'SUV' }
function groupLabel(v) { return groupLabels[v] || v }
function statusLabel(s) {
  if (s === 'pending') return 'Bekliyor'
  if (s === 'assigned') return 'Onaylandı'
  if (s === 'cancelled') return 'İptal'
  return s
}
function displayStatus(r) {
  if (r.delivery_info?.returned) return 'İade Edildi'
  if (r.delivery_info?.delivered) return 'Teslim Edildi'
  return statusLabel(r.status)
}
function displayStatusKey(r) {
  if (r.delivery_info?.returned) return 'returned'
  if (r.delivery_info?.delivered) return 'delivered'
  return r.status
}
function fuelLabel(v) {
  return { 0: 'E', 1: '1/8', 2: '1/4', 3: '3/8', 4: '1/2', 5: '5/8', 6: '3/4', 7: '7/8', 8: 'F' }[v] ?? '—'
}

onMounted(async () => {
  const res = await axios.get('/api/reservations/')
  reservations.value = res.data
})

async function handleCancel(reservationId) {
  try {
    await axios.post(`/api/reservations/${reservationId}/cancel/`)
    const res = await axios.get('/api/reservations/')
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
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
td:nth-child(1), th:nth-child(1), td:nth-child(2), th:nth-child(2), td:nth-child(3), th:nth-child(3), td:nth-child(4), th:nth-child(4), td:nth-child(5), th:nth-child(5), td:nth-child(6), th:nth-child(6), td:nth-child(7), th:nth-child(7) { text-align: center; }
tr:hover td { background: #fafbff; }
.res-id { font-weight: 700; color: #000000; font-size: 13px; }
.actions-cell { display: flex; gap: 6px; align-items: center; justify-content: center; }
.btn-detail { padding: 5px 12px; background: white; color: #6366f1; border: 1.5px solid #c7d2fe; border-radius: 7px; font-size: 12px; font-weight: 600; cursor: pointer; }
.btn-detail:hover { background: #eef2ff; }
.btn-cancel { padding: 5px 12px; background: white; color: #dc2626; border: 1.5px solid #fca5a5; border-radius: 7px; font-size: 12px; font-weight: 600; cursor: pointer; transition: background 0.15s; }
.btn-cancel:hover { background: #fff1f2; border-color: #dc2626; }
.error-msg { color: #dc2626; font-size: 13px; margin-top: 12px; background: #fff1f2; padding: 10px 14px; border-radius: 8px; }
.vehicle-info { margin-top: 4px; font-size: 12px; color: #000000; font-weight: 600; }
.price-badge { font-size: 13px; font-weight: 700; color: #000000; }
.price-na { color: #94a3b8; }

.badge-delivered { background: #dbeafe; color: #1d4ed8; }
.badge-returned { background: #d1fae5; color: #065f46; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.35); z-index: 1000; display: flex; align-items: center; justify-content: center; }
.modal { background: white; border-radius: 14px; padding: 28px; width: 480px; max-width: 90vw; max-height: 80vh; overflow-y: auto; box-shadow: 0 8px 32px rgba(0,0,0,0.15); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.modal-res-id { font-size: 16px; font-weight: 800; color: #1e293b; }
.modal-close { background: none; border: none; font-size: 18px; color: #94a3b8; cursor: pointer; padding: 0 4px; }
.modal-close:hover { color: #1e293b; }
.modal-section-title { font-size: 11px; font-weight: 700; color: #6366f1; text-transform: uppercase; letter-spacing: 0.08em; margin: 16px 0 8px; border-top: 1px solid #f1f5f9; padding-top: 16px; }
.modal-grid { display: flex; flex-direction: column; gap: 8px; }
.mrow { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f8fafc; }
.mlabel { font-size: 12px; font-weight: 600; color: #94a3b8; }
.mval { font-size: 13px; font-weight: 600; color: #1e293b; text-align: right; }
.modal-empty { color: #94a3b8; font-size: 13px; text-align: center; padding: 20px 0; }
.damage-readonly { pointer-events: none; margin-top: 12px; }
</style>

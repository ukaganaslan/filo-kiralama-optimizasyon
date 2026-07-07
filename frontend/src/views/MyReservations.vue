<template>
  <div class="content">
    <div class="page-header">
      <div class="section-title">
        <span>Rezervasyonlarım</span>
        <span v-if="reservations.length" class="count-badge">{{ reservations.length }}</span>
      </div>
      <button class="btn-add" @click="router.push('/dashboard')">+ Yeni Rezervasyon</button>
    </div>

    <div v-if="reservations.length" class="toolbar">
      <div class="toolbar-filters">
        <input v-model="tableSearch" class="search-input" placeholder="Ara..." />
        <select v-model="statusFilter" class="filter-select">
          <option value="">Tüm Durumlar</option>
          <option v-for="o in statusOptions" :key="o.key" :value="o.key">{{ o.label }}</option>
        </select>
      </div>
    </div>

    <div v-if="reservations.length === 0" class="empty-state">
      <div class="empty-icon"><i class="pi pi-calendar"></i></div>
      <p>Henüz rezervasyonunuz yok.</p>
      <p class="empty-sub">Yeni bir araç kiralamak için "Yeni Rezervasyon" bölümüne gidin.</p>
    </div>

    <div v-else class="table-wrap">
      <table>
        <thead>
          <tr>
            <th class="sortable" @click="sortBy('reservation_id')">Rezervasyon No <span class="sort-ind">{{ sortArrow('reservation_id') }}</span></th>
            <th class="sortable" @click="sortBy('branch_title')">Şube <span class="sort-ind">{{ sortArrow('branch_title') }}</span></th>
            <th class="sortable" @click="sortBy('group')">Grup <span class="sort-ind">{{ sortArrow('group') }}</span></th>
            <th class="sortable" @click="sortBy('start_date')">Başlangıç <span class="sort-ind">{{ sortArrow('start_date') }}</span></th>
            <th class="sortable" @click="sortBy('end_date')">Bitiş <span class="sort-ind">{{ sortArrow('end_date') }}</span></th>
            <th class="sortable" @click="sortBy('price')">Tutar <span class="sort-ind">{{ sortArrow('price') }}</span></th>
            <th class="sortable" @click="sortBy('status')">Durum <span class="sort-ind">{{ sortArrow('status') }}</span></th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filtered.length === 0"><td colspan="8" class="empty">Aramanızla eşleşen rezervasyon bulunamadı.</td></tr>
          <tr v-for="r in filtered" :key="r.id">
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
              <button class="btn-detail" @click="openDetail(r)">Detay</button>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useTableSort } from '@/composables/useTableSort'

const router = useRouter()
const reservations = ref([])
const error = ref('')
const tableSearch = ref('')
const statusFilter = ref('')

const statusOptions = [
  { key: 'pending', label: 'Bekliyor' },
  { key: 'assigned', label: 'Onaylandı' },
  { key: 'delivered', label: 'Teslim Edildi' },
  { key: 'returned', label: 'İade Edildi' },
  { key: 'processing', label: 'İşlemde' },
  { key: 'cancelled', label: 'İptal' },
]

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
  if (r.delivery_info?.returned_stage) return 'İade İşlemde'
  if (r.delivery_info?.delivered) return 'Teslim Edildi'
  if (r.delivery_info?.delivered_stage) return 'Teslim İşlemde'
  return statusLabel(r.status)
}
function displayStatusKey(r) {
  if (r.delivery_info?.returned) return 'returned'
  if (r.delivery_info?.returned_stage) return 'processing'
  if (r.delivery_info?.delivered) return 'delivered'
  if (r.delivery_info?.delivered_stage) return 'processing'
  return r.status
}
const { sortBy, sortArrow, sorted } = useTableSort(reservations, {
  group: r => groupLabel(r.vehicle_group),
  price: r => Number(r.total_price) || 0,
  status: r => displayStatus(r),
})

const filtered = computed(() => {
  let list = sorted.value
  if (statusFilter.value) list = list.filter(r => displayStatusKey(r) === statusFilter.value)
  const q = tableSearch.value.trim().toLowerCase()
  if (q) {
    list = list.filter(r =>
      [r.reservation_id, r.branch_title, groupLabel(r.vehicle_group), r.start_date, r.end_date,
       r.assigned_vehicle_info?.brand, r.assigned_vehicle_info?.model, r.assigned_vehicle_info?.plate]
        .filter(Boolean)
        .some(v => String(v).toLowerCase().includes(q))
    )
  }
  return list
})

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

function openDetail(r) {
  router.push(`/dashboard/rezervasyonlar/${r.id}`)
}
</script>

<style scoped>
.content { padding: 32px 40px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; }
.section-title { display: flex; align-items: center; gap: 10px; font-size: 22px; font-weight: 800; letter-spacing: -0.01em; color: #0f172a; }
.btn-add { padding: 10px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; box-shadow: 0 1px 2px rgba(79,70,229,0.25); transition: background 0.15s; }
.btn-add:hover { background: #4f46e5; }
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  background: white;
  border: 1px solid #eef0f4;
  border-radius: 12px;
  padding: 10px 14px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  flex-wrap: wrap;
}
.toolbar-filters { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.filter-select { padding: 8px 12px; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 13px; color: #475569; background: white; outline: none; cursor: pointer; height: 36px; }
.filter-select:focus { border-color: #6366f1; }
.search-input { padding: 8px 14px; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 13px; color: #475569; background: #f8fafc; outline: none; width: 180px; height: 36px; box-sizing: border-box; transition: background 0.15s, border-color 0.15s; }
.search-input:focus { border-color: #6366f1; background: white; }
.search-input::placeholder { color: #94a3b8; }
.count-badge { background: #ede9fe; color: #6366f1; font-size: 13px; font-weight: 700; padding: 2px 10px; border-radius: 50px; }
.empty-state { text-align: center; padding: 60px 24px; background: white; border-radius: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.empty-icon { font-size: 36px; margin-bottom: 12px; color: #cbd5e1; }
.empty-state p { color: #475569; font-size: 15px; font-weight: 600; margin: 0 0 6px; }
.empty-sub { color: #94a3b8; font-size: 13px; font-weight: 400 !important; }
.table-wrap { background: white; border-radius: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); overflow: hidden; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f8fafc; font-weight: 700; color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; border-bottom: 1px solid #f1f5f9; }
th.sortable { cursor: pointer; user-select: none; }
th.sortable:hover { color: #6366f1; }
.sort-ind { font-size: 9px; color: #6366f1; }
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

.badge-delivered { background: #d1fae5; color: #065f46; }
.badge-returned { background: #e9d5ff; color: #6b21a8; }
.badge-processing { background: #fed7aa; color: #9a3412; }
</style>

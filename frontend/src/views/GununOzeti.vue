<template>
  <div class="content">

    <div class="page-header">
      <div>
        <h2>Günün Özeti</h2>
        <span class="sub">{{ tarihYazi }}</span>
      </div>
      <span class="branch-tag">{{ branchName }}</span>
    </div>

    <div class="cards-grid">

      <div class="card card--green">
        <div class="card-header">
          <span class="card-title">Bugün Teslim Edilecekler</span>
          <span class="count-badge">{{ teslimlBugün.length }}</span>
        </div>
        <div v-if="teslimlBugün.length === 0" class="empty">Bugün teslim yok.</div>
        <div v-for="r in teslimlBugün" :key="r.id" class="card-row">
          <span class="col-name">{{ musteriAdi(r) }}</span>
          <span class="col-group">{{ groupLabel(r.vehicle_group) }}</span>
          <span class="col-vehicle">{{ r.assigned_vehicle_id || '—' }}</span>
        </div>
      </div>

      <div class="card card--amber">
        <div class="card-header">
          <span class="card-title">Bugün İade Alınacaklar</span>
          <span class="count-badge">{{ iadelerBugün.length }}</span>
        </div>
        <div v-if="iadelerBugün.length === 0" class="empty">Bugün iade yok.</div>
        <div v-for="r in iadelerBugün" :key="r.id" class="card-row">
          <span class="col-name">{{ musteriAdi(r) }}</span>
          <span class="col-group">{{ groupLabel(r.vehicle_group) }}</span>
          <span class="col-vehicle">{{ r.assigned_vehicle_id || '—' }}</span>
        </div>
      </div>

      <div class="card card--red">
        <div class="card-header">
          <span class="card-title">Bakımda</span>
          <span class="count-badge">{{ bakimdakiler.length }}</span>
        </div>
        <div v-if="bakimdakiler.length === 0" class="empty">Bakımda araç yok.</div>
        <div v-for="v in bakimdakiler" :key="v.id" class="card-row">
          <span class="col-name">{{ v.plate }}</span>
          <span class="col-group">{{ groupLabel(v.group) }}</span>
          <span class="col-vehicle">{{ v.vehicle_id }}</span>
        </div>
      </div>

    </div>

    <div v-if="atanamamis.length > 0" class="warning-band">
      <div class="warning-header">
        <span class="warning-title">Atama Bekleyen Rezervasyonlar</span>
        <span class="count-badge count-badge--amber">{{ atanamamis.length }}</span>
      </div>
      <div v-for="r in atanamamis" :key="r.id" class="warning-row">
        <span class="col-name">{{ r.reservation_id }}</span>
        <span class="col-group">{{ groupLabel(r.vehicle_group) }}</span>
        <span class="col-warn">Müsait araç bulunamadı</span>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const reservations = ref([])
const vehicles = ref([])
const branchName = ref('')

const bugun = new Date().toISOString().split('T')[0]

const tarihYazi = new Date().toLocaleDateString('tr-TR', {
  weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
})

const teslimlBugün = computed(() =>
  reservations.value.filter(r => r.start_date === bugun && r.status === 'assigned')
)

const iadelerBugün = computed(() =>
  reservations.value.filter(r => r.end_date === bugun && r.status === 'assigned')
)

const bakimdakiler = computed(() =>
  vehicles.value.filter(v => v.current_status === 'maintenance')
)

const atanamamis = computed(() =>
  reservations.value.filter(r => r.start_date === bugun && r.status === 'pending')
)

onMounted(async () => {
  const [rezRes, vehicleRes, profileRes, branchRes] = await Promise.all([
    axios.get('/api/reservations/'),
    axios.get('/api/vehicles/'),
    axios.get('/api/profile/'),
    axios.get('/api/branches/'),
  ])
  reservations.value = rezRes.data
  vehicles.value = vehicleRes.data
  const branchId = profileRes.data.branch_id
  const branch = branchRes.data.find(b => b.id === branchId)
  branchName.value = branch ? (branch.title || branch.name) : ''
})

function musteriAdi(r) {
  return r.customer_username || r.guest_name || 'Misafir'
}

function groupLabel(g) {
  return { economy: 'Ekonomi', mid: 'Orta Sınıf', suv: 'SUV' }[g] || g
}
</script>

<style scoped>
.content { padding: 32px 40px; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}

h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0 0 4px; }

.sub { font-size: 13px; color: #64748b; font-weight: 400; text-transform: capitalize; }

.branch-tag {
  padding: 5px 14px;
  background: #f1f5f9;
  color: #475569;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 600;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.card {
  background: white;
  border-radius: 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  overflow: hidden;
  border-left: 4px solid transparent;
}

.card--green { border-left-color: #16a34a; }
.card--amber { border-left-color: #f59e0b; }
.card--red   { border-left-color: #dc2626; }

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px 12px;
  border-bottom: 1px solid #f1f5f9;
}

.card-title { font-size: 14px; font-weight: 700; color: #1e293b; }

.count-badge {
  padding: 2px 9px;
  background: #f1f5f9;
  color: #64748b;
  border-radius: 50px;
  font-size: 12px;
  font-weight: 600;
}

.count-badge--amber {
  background: #fef3c7;
  color: #92400e;
}

.empty {
  padding: 20px;
  font-size: 13px;
  color: #94a3b8;
  text-align: center;
}

.card-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  border-top: 1px solid #f8fafc;
  font-size: 13px;
}

.card-row:hover { background: #f8fafc; }

.col-name { flex: 1; font-weight: 500; color: #1e293b; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.col-group { color: #64748b; font-size: 12px; white-space: nowrap; }
.col-vehicle { font-family: monospace; font-size: 12px; color: #6366f1; font-weight: 600; white-space: nowrap; }

.warning-band {
  background: #fffbeb;
  border: 1px solid #fcd34d;
  border-radius: 12px;
  overflow: hidden;
}

.warning-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  border-bottom: 1px solid #fde68a;
}

.warning-title { font-size: 14px; font-weight: 700; color: #92400e; }

.warning-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  border-top: 1px solid #fef3c7;
  font-size: 13px;
}

.col-warn { color: #b45309; font-size: 12px; font-weight: 500; margin-left: auto; }
</style>

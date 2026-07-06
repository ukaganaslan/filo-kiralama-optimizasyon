<template>
  <div class="content">
    <div v-if="!result" class="empty-state">
      <p>Henüz optimizasyon çalıştırılmadı.</p>
      <router-link to="/operator" class="btn-go">Rezervasyonlar sayfasına git →</router-link>
    </div>

    <div v-else>
      <h2>Optimizasyon Sonucu</h2>

      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-value">{{ result.score }} / 100</div>
          <div class="stat-label">Algoritma Skoru</div>
        </div>
        <div class="stat-card green">
          <div class="stat-value">{{ result.fulfilled }}</div>
          <div class="stat-label">Karşılanan</div>
        </div>
        <div class="stat-card red">
          <div class="stat-value">{{ result.unfulfilled }}</div>
          <div class="stat-label">Karşılanamayan</div>
        </div>
      </div>

      <h3>Atamalar</h3>
      <table>
        <thead>
          <tr>
            <th class="sortable" @click="sortBy('reservation_id')">Rezervasyon <span class="sort-ind">{{ sortArrow('reservation_id') }}</span></th>
            <th class="sortable" @click="sortBy('customer')">Müşteri <span class="sort-ind">{{ sortArrow('customer') }}</span></th>
            <th class="sortable" @click="sortBy('vehicle_id')">Araç <span class="sort-ind">{{ sortArrow('vehicle_id') }}</span></th>
            <th class="sortable" @click="sortBy('start_date')">Başlangıç <span class="sort-ind">{{ sortArrow('start_date') }}</span></th>
            <th class="sortable" @click="sortBy('end_date')">Bitiş <span class="sort-ind">{{ sortArrow('end_date') }}</span></th>
            <th class="sortable" @click="sortBy('transfer_cost')">Transfer <span class="sort-ind">{{ sortArrow('transfer_cost') }}</span></th>
            <th class="sortable" @click="sortBy('is_upgrade')">Upgrade <span class="sort-ind">{{ sortArrow('is_upgrade') }}</span></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in sorted" :key="a.reservation_id">
            <td>{{ a.reservation_id }}</td>
            <td>{{ a.customer_username || `Misafir - ${a.guest_name}` }}</td>
            <td>{{ a.vehicle_id }}</td>
            <td>{{ a.start_date }}</td>
            <td>{{ a.end_date }}</td>
            <td>{{ a.transfer_cost }}</td>
            <td>{{ a.is_upgrade ? 'Evet' : 'Hayır' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import axios from 'axios'
import { useOptimizationStore } from '../stores/optimization'
import { useTableSort } from '@/composables/useTableSort'

const optimizationStore = useOptimizationStore()
const result = computed(() => optimizationStore.result)

const assignments = computed(() => result.value?.assignments || [])
const { sortBy, sortArrow, sorted } = useTableSort(assignments, {
  customer: a => a.customer_username || a.guest_name || '',
  transfer_cost: a => Number(a.transfer_cost) || 0,
  is_upgrade: a => (a.is_upgrade ? 1 : 0),
})

onMounted(async () => {
  if (!optimizationStore.result) {
    const res = await axios.get('/api/optimize/latest/')
    if (res.data) optimizationStore.setResult(res.data)
  }
})
</script>

<style scoped>
.content { padding: 32px 40px; }
.empty-state { text-align: center; padding: 80px 40px; color: #94a3b8; font-size: 15px; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.btn-go { padding: 10px 24px; background: #6366f1; color: white; border-radius: 50px; text-decoration: none; font-size: 14px; font-weight: 600; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0 0 20px; }
h3 { font-size: 16px; font-weight: 700; color: #1e293b; margin: 24px 0 12px; }
.stats-row { display: flex; gap: 16px; margin-bottom: 24px; }
.stat-card { flex: 1; background: white; border-radius: 14px; padding: 20px 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); border-left: 4px solid #6366f1; }
.stat-card.green { border-color: #10b981; }
.stat-card.red { border-color: #ef4444; }
.stat-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 12px; color: #94a3b8; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 14px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
td:nth-child(1), th:nth-child(1), td:nth-child(2), th:nth-child(2), td:nth-child(3), th:nth-child(3), td:nth-child(4), th:nth-child(4), td:nth-child(5), th:nth-child(5), td:nth-child(6), th:nth-child(6), td:nth-child(7), th:nth-child(7) { text-align: center; }
th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
th.sortable { cursor: pointer; user-select: none; }
th.sortable:hover { color: #6366f1; }
.sort-ind { font-size: 9px; color: #6366f1; }
td { border-top: 1px solid #f1f5f9; }
</style>

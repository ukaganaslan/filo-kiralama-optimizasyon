<template>
  <div class="content">
    <div v-if="!result" class="empty-state">
      <p>Henüz optimizasyon çalıştırılmadı.</p>
      <router-link to="/operator" class="btn-go">Rezervasyonlar sayfasına git →</router-link>
    </div>

    <div v-else>
      <h2>Karşılanamayan Rezervasyonlar</h2>

      <p v-if="result.unassigned.length === 0" class="all-good">
        Tüm rezervasyonlar karşılandı.
      </p>

      <table v-else>
        <thead>
          <tr>
            <th class="sortable" @click="sortBy('reservation_id')">Rezervasyon <span class="sort-ind">{{ sortArrow('reservation_id') }}</span></th>
            <th class="sortable" @click="sortBy('customer_username')">Müşteri <span class="sort-ind">{{ sortArrow('customer_username') }}</span></th>
            <th class="sortable" @click="sortBy('branch_name')">Şube <span class="sort-ind">{{ sortArrow('branch_name') }}</span></th>
            <th class="sortable" @click="sortBy('vehicle_group')">Grup <span class="sort-ind">{{ sortArrow('vehicle_group') }}</span></th>
            <th class="sortable" @click="sortBy('start_date')">Başlangıç <span class="sort-ind">{{ sortArrow('start_date') }}</span></th>
            <th class="sortable" @click="sortBy('end_date')">Bitiş <span class="sort-ind">{{ sortArrow('end_date') }}</span></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in sorted" :key="r.reservation_id">
            <td>{{ r.reservation_id }}</td>
            <td>{{ r.customer_username }}</td>
            <td>{{ r.branch_name }}</td>
            <td>{{ categoryLabel(r.vehicle_group) }}</td>
            <td>{{ r.start_date }}</td>
            <td>{{ r.end_date }}</td>
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
import { categoryLabel } from '@/constants/sipp'

const optimizationStore = useOptimizationStore()
const result = computed(() => optimizationStore.result)

const unassigned = computed(() => result.value?.unassigned || [])
const { sortBy, sortArrow, sorted } = useTableSort(unassigned)

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
.btn-go { padding: 10px 24px; background: #6366f1; color: white; border-radius: 50px; text-decoration: none; font-size: 14px; font-weight: 600; transition: background 0.15s, transform 0.15s; display: inline-block; }
.btn-go:hover { background: #4f46e5; transform: translateY(-1px); }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0 0 20px; }
.all-good { color: #10b981; font-size: 15px; font-weight: 500; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 14px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
th.sortable { cursor: pointer; user-select: none; transition: color 0.15s; }
th.sortable:hover { color: #6366f1; }
.sort-ind { font-size: 9px; color: #6366f1; }
tbody tr { transition: background 0.12s; }
tbody tr:hover { background: #fafbff; }
td { border-top: 1px solid #f1f5f9; }
</style>

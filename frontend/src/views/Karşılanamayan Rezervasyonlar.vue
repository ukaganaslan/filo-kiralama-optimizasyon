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
            <th>Rezervasyon</th>
            <th>Müşteri</th>
            <th>Şube</th>
            <th>Grup</th>
            <th>Başlangıç</th>
            <th>Bitiş</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in result.unassigned" :key="r.reservation_id">
            <td>{{ r.reservation_id }}</td>
            <td>{{ r.customer_username }}</td>
            <td>{{ r.branch_name }}</td>
            <td>{{ r.vehicle_group }}</td>
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

const optimizationStore = useOptimizationStore()
const result = computed(() => optimizationStore.result)

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
.all-good { color: #10b981; font-size: 15px; font-weight: 500; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 14px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
td { border-top: 1px solid #f1f5f9; }
</style>

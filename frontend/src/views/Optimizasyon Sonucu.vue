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
          <div class="stat-value">{{ result.score }}</div>
          <div class="stat-label">Toplam Skor</div>
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
            <th>Rezervasyon</th>
            <th>Müşteri</th>
            <th>Araç</th>
            <th>Başlangıç</th>
            <th>Bitiş</th>
            <th>Transfer</th>
            <th>Upgrade</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in result.assignments" :key="a.reservation_id">
            <td>{{ a.reservation_id }}</td>
            <td>{{ a.customer_username }}</td>
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

const optimizationStore = useOptimizationStore()
const result = computed(() => optimizationStore.result)

onMounted(async () => {
  if (!optimizationStore.result) {
    const res = await axios.get('http://127.0.0.1:8000/api/optimize/latest/')
    if (res.data) optimizationStore.setResult(res.data)
  }
})
</script>

<style scoped>
.content { max-width: 1100px; margin: 0 auto; padding: 40px; }
.empty-state { text-align: center; padding: 80px 40px; color: #94a3b8; font-size: 15px; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.btn-go { padding: 10px 24px; background: #6366f1; color: white; border-radius: 50px; text-decoration: none; font-size: 14px; font-weight: 600; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0 0 20px; }
h3 { font-size: 16px; font-weight: 700; color: #1e293b; margin: 24px 0 12px; }
.stats-row { display: flex; gap: 16px; margin-bottom: 24px; }
.stat-card { flex: 1; background: white; border-radius: 10px; padding: 20px 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); border-left: 4px solid #6366f1; }
.stat-card.green { border-color: #10b981; }
.stat-card.red { border-color: #ef4444; }
.stat-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 12px; color: #94a3b8; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
td { border-top: 1px solid #f1f5f9; }
</style>

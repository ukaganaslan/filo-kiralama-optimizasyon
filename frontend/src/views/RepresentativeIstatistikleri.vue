<template>
  <div class="content">

    <div class="page-header">
      <div>
        <h2>İstatistikler</h2>
        <span class="sub">{{ tarihYazi }}</span>
      </div>
    </div>

    <div v-if="stats" class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Bu Ay Ciro</div>
        <div class="stat-value">{{ Number(stats.this_month).toLocaleString('tr-TR') }} ₺</div>
      </div>
      <div class="stat-card stat-amber">
        <div class="stat-label">Ortalama Doluluk</div>
        <div class="stat-value">%{{ avgOccupancy.toFixed(0) }}</div>
      </div>
      <div class="stat-card stat-blue">
        <div class="stat-label">Toplam Araç</div>
        <div class="stat-value">{{ totalVehicles }}</div>
      </div>
    </div>

    <div class="carousel">
      <button class="carousel-arrow" @click="prevSlide">‹</button>

      <div class="carousel-viewport">
        <div class="carousel-track" :style="{ transform: `translateX(-${activeIndex * 100}%)` }">
          <div v-for="(slide, i) in slides" :key="slide.title" class="carousel-slide">
            <div class="slide-header">
              <div class="slide-title">{{ slide.title }}</div>
              <div v-if="i === 2" class="date-filter">
                <input type="date" v-model="startDate" :max="endDate" @change="fetchStats" />
                <span class="date-sep">—</span>
                <input type="date" v-model="endDate" :min="startDate" @change="fetchStats" />
              </div>
            </div>
            <apexchart v-if="i === 0" type="line" :options="revenueOptions" :series="revenueSeries" height="260" />
            <apexchart v-else-if="i === 1" type="area" :options="dailyOptions" :series="dailySeries" height="260" />
            <apexchart v-else type="pie" :options="groupOptions" :series="groupSeries" height="260" />
          </div>
        </div>
      </div>

      <button class="carousel-arrow" @click="nextSlide">›</button>
    </div>

    <div class="carousel-dots">
      <button
        v-for="(slide, i) in slides"
        :key="slide.title"
        class="dot"
        :class="{ 'dot--active': i === activeIndex }"
        @click="activeIndex = i"
      ></button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const stats = ref(null)

const isoDate = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
const now = new Date()
const startDate = ref(isoDate(new Date(now.getFullYear(), now.getMonth(), 1)))
const endDate = ref(isoDate(now))

async function fetchStats() {
  if (!startDate.value || !endDate.value) return
  const res = await axios.get('/api/admin-stats/', {
    params: { start: startDate.value, end: endDate.value }
  })
  stats.value = res.data
}

const slides = [
  { title: 'Aylık Ciro Trendi (Son 12 Ay)' },
  { title: 'Günlük Doluluk Oranı (Son 30 Gün)' },
  { title: 'Araç Grubuna Göre Talep Dağılımı' },
]
const activeIndex = ref(0)

function nextSlide() {
  activeIndex.value = (activeIndex.value + 1) % slides.length
}
function prevSlide() {
  activeIndex.value = (activeIndex.value - 1 + slides.length) % slides.length
}

const tarihYazi = new Date().toLocaleDateString('tr-TR', {
  weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
})

const avgOccupancy = computed(() => {
  if (!stats.value) return 0
  const totalVehicles = stats.value.branches.reduce((sum, b) => sum + b.total, 0)
  if (totalVehicles === 0) return 0
  const totalActive = stats.value.branches.reduce((sum, b) => sum + b.active, 0)
  return (totalActive / totalVehicles) * 100
})

const totalVehicles = computed(() => {
  if (!stats.value) return 0
  return stats.value.branches.reduce((sum, b) => sum + b.total, 0)
})

const monthLabel = (m) => {
  const [y, mo] = m.split('-')
  return new Date(y, mo - 1, 1).toLocaleDateString('tr-TR', { month: 'short', year: '2-digit' })
}

const dayLabel = (d) =>
  new Date(d).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })

const revenueOptions = computed(() => ({
  chart: { type: 'line', toolbar: { show: false } },
  xaxis: { categories: stats.value ? stats.value.monthly_revenue.map(m => monthLabel(m.month)) : [] },
  colors: ['#6366f1'],
  stroke: { curve: 'smooth', width: 3 },
  dataLabels: { enabled: false },
  yaxis: { labels: { formatter: v => Number(v).toLocaleString('tr-TR') } },
  grid: {borderColor: '#f1f5f9'}
}))

const dailyOptions = computed(() => ({
  chart: { type: 'area', toolbar: { show: false } },
  xaxis: {
    categories: stats.value ? stats.value.daily_occupancy.map(d => dayLabel(d.date)) : [],
    tickAmount: 10,
    labels: { rotate: -45 },
  },
  colors: ['#f59e0b'],
  stroke: { curve: 'smooth', width: 2 },
  fill: { type: 'gradient', gradient: { opacityFrom: 0.35, opacityTo: 0.05 } },
  dataLabels: { enabled: false },
  yaxis: { max: 100, labels: { formatter: v => `${v}%` } },
  grid: {borderColor: '#f1f5f9'}
}))

const dailySeries = computed(() => [
  { name: 'Doluluk', data: stats.value ? stats.value.daily_occupancy.map(d => d.occupancy) : [] }
])

const revenueSeries = computed(() => [
  { name:'Ciro', data: stats.value ? stats.value.monthly_revenue.map(m => Number(m.total)) : [] }
])

const groupLabel = (g) => ({ economy: 'Ekonomi', mid: 'Orta Sınıf', suv: 'SUV' }[g] || g)

const groupOptions = computed(() => ({
  chart: { type: 'pie' },
  labels: stats.value ? stats.value.groups.map(g => groupLabel(g.vehicle_group)) : [],
  colors: ['#6366f1', '#3b82f6', '#10b981'],
  legend: { position: 'bottom' },
  dataLabels: { enabled: true, formatter: (val) => `${val.toFixed(0)}%` },
}))

const groupSeries = computed(() =>
  stats.value ? stats.value.groups.map(g => g.count) : []
)

onMounted(fetchStats)
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

.slide-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.slide-header .slide-title { margin-bottom: 0; }

.date-filter {
  display: flex;
  align-items: center;
  gap: 8px;
}
.date-filter input {
  padding: 6px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 12px;
  color: #1e293b;
  background: white;
}
.date-filter input:focus {
  outline: none;
  border-color: #6366f1;
}
.date-sep { color: #94a3b8; font-size: 13px; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(180px, 240px));
  justify-content: center;
  gap: 16px;
  margin-bottom: 28px;
}
.stat-card {
  background: white;
  border-radius: 14px;
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  border-left: 4px solid #6366f1;
}
.stat-card.stat-amber { border-left-color: #f59e0b; }
.stat-card.stat-green { border-left-color: #10b981; }
.stat-card.stat-blue  { border-left-color: #3b82f6; }
.stat-card.stat-red   { border-left-color: #dc2626; }
.stat-label {
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 32px;
  font-weight: 800;
  color: #1e293b;
  line-height: 1;
}

.carousel {
  display: flex;
  align-items: center;
  gap: 12px;
}

.carousel-viewport {
  flex: 1;
  overflow: hidden;
  background: white;
  border-radius: 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.carousel-track {
  display: flex;
  transition: transform 300ms ease;
}

.carousel-slide {
  flex: 0 0 100%;
  min-width: 0;
  padding: 24px 28px;
  min-height: 320px;
}

.slide-title {
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
}

.carousel-arrow {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid #e2e8f0;
  background: white;
  color: #475569;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
}

.carousel-arrow:hover {
  border-color: #6366f1;
  color: #6366f1;
}

.carousel-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 14px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: none;
  background: #e2e8f0;
  cursor: pointer;
  padding: 0;
}

.dot--active {
  background: #6366f1;
  width: 20px;
  border-radius: 4px;
}
</style>

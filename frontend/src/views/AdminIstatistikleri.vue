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
      <div class="stat-card" :class="changePercent >= 0 ? 'stat-green' : 'stat-red'">
        <div class="stat-label">Geçen Aya Göre</div>
        <div class="stat-value">{{ changePercent >= 0 ? '+' : '' }}{{ changePercent.toFixed(1) }}%</div>
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
            <div class="slide-title">{{ slide.title }}</div>
            <apexchart v-if="i === 0" type="line" :options="revenueOptions" :series="revenueSeries" height="260" />
            <apexchart v-else-if="i === 1" type="bar" :options="occupancyOptions" :series="occupancySeries" height="260" />
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

const slides = [
  { title: 'Aylık Gelir Karşılaştırması' },
  { title: 'Şubeye Göre Doluluk Oranı' },
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

const changePercent = computed(() => {
  if (!stats.value || !stats.value.last_month) return 0
  return ((stats.value.this_month - stats.value.last_month) / stats.value.last_month) * 100
})

const avgOccupancy = computed(() => {
  if (!stats.value) return 0
  const withVehicles = stats.value.branches.filter(b => b.total > 0)
  if (withVehicles.length === 0) return 0
  const total = withVehicles.reduce((sum, b) => sum + (b.active / b.total) * 100, 0)
  return total / withVehicles.length
})

const totalVehicles = computed(() => {
  if (!stats.value) return 0
  return stats.value.branches.reduce((sum, b) => sum + b.total, 0)
})

const revenueOptions = computed(() => ({
  chart: { type: 'line', toolbar: { show: false } },
  xaxis: { categories: ['Geçen Ay', 'Bu Ay'] },
  colors: ['#6366f1'],
  stroke: { curve: 'straight', width: 3 },
  dataLabels: { enabled: false },
  grid: {borderColor: '#f1f5f9'}
}))

const occupancyOptions = computed(() => ({
  chart: { type: 'bar', toolbar: { show: false } },
  xaxis: { categories: stats.value ? stats.value.branches.map(b => b.name) : [] },
  colors: ['#10b981'],
  plotOptions: { bar: { borderRadius: 4, columnWidth: '45%' } },
  dataLabels: { enabled: false },
  yaxis: { max:100, labels: { formatter: v => `${v}%` } },
  grid: {borderColor: '#f1f5f9'}
}))

const occupancySeries = computed(() => [
  { name:'Doluluk', data: stats.value ? stats.value.branches.map(b => (b.total > 0 ? Math.round((b.active / b.total) * 100) : 0)) : [] }
])

const revenueSeries = computed(() => [
  { name:'Ciro', data: stats.value ? [stats.value.last_month, stats.value.this_month] : [0, 0] }
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

onMounted(async () => {
  const res = await axios.get('/api/admin-stats/')
  stats.value = res.data
})
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
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
  margin-bottom: 16px;
}

.slide-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 260px;
  color: #94a3b8;
  font-size: 13px;
  border: 1px dashed #e2e8f0;
  border-radius: 10px;
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

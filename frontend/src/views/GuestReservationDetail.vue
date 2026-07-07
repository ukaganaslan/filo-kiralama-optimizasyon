<template>
  <div class="gd-page">
    <div class="gd-header">
      <router-link to="/misafir" class="gd-back">← Ana Sayfa</router-link>
      <div class="gd-brand">Rezervasyon Detayı</div>
    </div>

    <div class="gd-body">
      <div v-if="loading" class="gd-loading">Yükleniyor...</div>
      <div v-else-if="error" class="gd-error-box">{{ error }}</div>

      <template v-else-if="res">
        <div class="gd-card gd-top">
          <div>
            <div class="gd-code">#{{ res.reservation_id }}</div>
            <div class="gd-name">{{ res.guest_name }}</div>
          </div>
          <span class="status-badge" :class="res.status">{{ statusLabel(res.status) }}</span>
        </div>

        <div class="gd-card">
          <div class="gd-title">Rezervasyon Bilgileri</div>
          <div class="gd-grid">
            <div class="gd-item">
              <span class="gd-label">Şube</span>
              <span class="gd-value">{{ res.branch }}</span>
            </div>
            <div class="gd-item">
              <span class="gd-label">Araç Grubu</span>
              <span class="gd-value">{{ groupLabel(res.vehicle_group) }}</span>
            </div>
            <div class="gd-item">
              <span class="gd-label">Tarih</span>
              <span class="gd-value">{{ res.start_date }} → {{ res.end_date }}</span>
            </div>
            <div class="gd-item" v-if="res.assigned_vehicle_info">
              <span class="gd-label">Araç</span>
              <span class="gd-value">{{ res.assigned_vehicle_info.brand }} {{ res.assigned_vehicle_info.model }} · {{ res.assigned_vehicle_info.plate }}</span>
            </div>
            <div class="gd-item" v-if="res.total_price">
              <span class="gd-label">Tutar</span>
              <span class="gd-value gd-price">{{ Number(res.total_price).toLocaleString('tr-TR') }} ₺</span>
            </div>
          </div>
        </div>

        <!-- Belgeler -->
        <div class="gd-card">
          <div class="gd-title">Belgeler</div>
          <div class="doc-list">
            <button
              class="doc-item"
              :disabled="!res.delivery_info?.delivered || pdfLoading === 'teslim'"
              @click="downloadPdf('teslim')"
            >
              <i class="pi pi-file-pdf doc-icon"></i>
              <span class="doc-name">Teslim Belgesi (PDF)</span>
              <span class="doc-action">{{ pdfLoading === 'teslim' ? 'İndiriliyor...' : 'İndir' }}</span>
            </button>
            <button
              class="doc-item"
              :disabled="!res.delivery_info?.returned || pdfLoading === 'iade'"
              @click="downloadPdf('iade')"
            >
              <i class="pi pi-file-pdf doc-icon"></i>
              <span class="doc-name">İade Belgesi (PDF)</span>
              <span class="doc-action">{{ pdfLoading === 'iade' ? 'İndiriliyor...' : 'İndir' }}</span>
            </button>
            <a
              v-if="res.delivery_info?.delivered_doc"
              class="doc-item"
              :href="mediaUrl(res.delivery_info.delivered_doc)"
              target="_blank"
              rel="noopener"
            >
              <i class="pi pi-file doc-icon"></i>
              <span class="doc-name">Teslim Ek Belgesi</span>
              <span class="doc-action">Görüntüle</span>
            </a>
            <a
              v-if="res.delivery_info?.returned_doc"
              class="doc-item"
              :href="mediaUrl(res.delivery_info.returned_doc)"
              target="_blank"
              rel="noopener"
            >
              <i class="pi pi-file doc-icon"></i>
              <span class="doc-name">İade Ek Belgesi</span>
              <span class="doc-action">Görüntüle</span>
            </a>
            <button
              v-if="res.delivery_info?.delivered_photo"
              class="doc-item"
              @click="lightboxUrl = mediaUrl(res.delivery_info.delivered_photo)"
            >
              <i class="pi pi-image doc-icon"></i>
              <span class="doc-name">Teslim Anı Araç Fotoğrafı</span>
              <span class="doc-action">Görüntüle</span>
            </button>
            <button
              v-if="res.delivery_info?.returned_photo"
              class="doc-item"
              @click="lightboxUrl = mediaUrl(res.delivery_info.returned_photo)"
            >
              <i class="pi pi-image doc-icon"></i>
              <span class="doc-name">İade Anı Araç Fotoğrafı</span>
              <span class="doc-action">Görüntüle</span>
            </button>
          </div>
          <p v-if="pdfError" class="doc-error">{{ pdfError }}</p>
          <p v-if="!res.delivery_info?.delivered" class="doc-hint">Belgeler, teslim işlemi tamamlandıktan sonra indirilebilir.</p>
        </div>

        <div class="gd-card" v-if="res.delivery_info?.delivered">
          <div class="gd-title">Teslim</div>
          <div class="gd-grid">
            <div class="gd-item">
              <span class="gd-label">Teslim KM</span>
              <span class="gd-value">{{ res.delivery_info.delivered_km ?? '—' }}</span>
            </div>
            <div class="gd-item">
              <span class="gd-label">Yakıt</span>
              <span class="gd-value">{{ fuelLabel(res.delivery_info.delivered_fuel) }}</span>
            </div>
            <div class="gd-item" v-if="res.delivery_info.delivered_notes">
              <span class="gd-label">Not</span>
              <span class="gd-value">{{ res.delivery_info.delivered_notes }}</span>
            </div>
          </div>
          <div class="gd-damage">
            <CarDamageMap :model-value="res.delivery_info.delivered_damage || {}" />
          </div>
        </div>

        <div class="gd-card" v-if="res.delivery_info?.returned">
          <div class="gd-title">İade</div>
          <div class="gd-grid">
            <div class="gd-item">
              <span class="gd-label">İade KM</span>
              <span class="gd-value">{{ res.delivery_info.returned_km ?? '—' }}</span>
            </div>
            <div class="gd-item">
              <span class="gd-label">Yakıt</span>
              <span class="gd-value">{{ fuelLabel(res.delivery_info.returned_fuel) }}</span>
            </div>
            <div class="gd-item" v-if="res.delivery_info.returned_notes">
              <span class="gd-label">Not</span>
              <span class="gd-value">{{ res.delivery_info.returned_notes }}</span>
            </div>
          </div>
          <div class="gd-damage">
            <CarDamageMap :model-value="res.delivery_info.returned_damage || {}" />
          </div>
        </div>

        <div class="gd-card gd-empty" v-if="!res.delivery_info?.delivered">
          Henüz araç teslimi yapılmamış.
        </div>
      </template>

      <!-- Fotoğraf büyütme -->
      <div v-if="lightboxUrl" class="lightbox" @click="lightboxUrl = null">
        <img :src="lightboxUrl" alt="Araç fotoğrafı" />
        <button class="lightbox-close" @click.stop="lightboxUrl = null">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import CarDamageMap from '@/components/CarDamageMap.vue'

const route = useRoute()
const res = ref(null)
const loading = ref(true)
const error = ref('')
const lightboxUrl = ref(null)
const pdfLoading = ref('')
const pdfError = ref('')

const groups = [
  { value: 'economy', label: 'Ekonomi' },
  { value: 'mid', label: 'Orta Sınıf' },
  { value: 'suv', label: 'SUV' },
]
function groupLabel(v) { return groups.find(g => g.value === v)?.label || v }
function statusLabel(s) { return { pending: 'Bekliyor', assigned: 'Onaylandı', cancelled: 'İptal' }[s] || s }
function fuelLabel(v) {
  return { 0: 'E', 1: '1/8', 2: '1/4', 3: '3/8', 4: '1/2', 5: '5/8', 6: '3/4', 7: '7/8', 8: 'F' }[v] ?? '—'
}

const apiBase = axios.defaults.baseURL || ''
function mediaUrl(path) {
  if (!path) return ''
  return path.startsWith('http') ? path : apiBase + path
}

async function downloadPdf(type) {
  pdfError.value = ''
  pdfLoading.value = type
  try {
    const r = await axios.get(`/api/guest-reservation/${route.params.code}/pdf/${type}/`, { responseType: 'blob' })
    const url = URL.createObjectURL(r.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `${type}-${res.value.reservation_id}.pdf`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    pdfError.value = 'Belge indirilemedi.'
  } finally {
    pdfLoading.value = ''
  }
}

onMounted(async () => {
  try {
    const r = await axios.get('/api/guest-reservation/query/', { params: { code: route.params.code } })
    res.value = r.data
  } catch (e) {
    error.value = e.response?.data?.error || 'Rezervasyon bulunamadı.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.gd-page { min-height: 100vh; background: #F8FAFC; }
.gd-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 18px 32px; background: white; border-bottom: 1px solid #e2e8f0;
}
.gd-back { color: #1B1063; font-size: 13px; font-weight: 700; text-decoration: none; transition: opacity 0.15s; }
.gd-back:hover { text-decoration: underline; opacity: 0.8; }
.gd-brand { font-size: 15px; font-weight: 800; color: #1e293b; }
.gd-body { max-width: 640px; margin: 0 auto; padding: 28px 20px 60px; }
.gd-loading, .gd-error-box { text-align: center; padding: 60px 0; color: #64748B; font-size: 14px; }
.gd-error-box { color: #DC2626; }
.gd-card { background: white; border-radius: 14px; padding: 20px 22px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 16px; animation: cardIn 0.25s ease; }
@keyframes cardIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
.gd-top { display: flex; align-items: center; justify-content: space-between; }
.gd-code { font-size: 16px; font-weight: 800; color: #1e293b; }
.gd-name { font-size: 13px; color: #64748B; margin-top: 2px; }
.gd-title { font-size: 12px; font-weight: 700; color: #1B1063; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 14px; }
.gd-grid { display: flex; flex-direction: column; gap: 10px; }
.gd-item { display: flex; justify-content: space-between; gap: 12px; font-size: 13px; }
.gd-label { color: #64748B; }
.gd-value { color: #1e293b; font-weight: 600; text-align: right; }
.gd-price { color: #1B1063; }
.gd-damage { margin-top: 16px; }
.gd-empty { color: #94a3b8; font-size: 13px; text-align: center; }
.status-badge { padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
.status-badge.pending { background: #fff7ed; color: #92400e; }
.status-badge.assigned { background: #f0fdf4; color: #166534; }
.status-badge.cancelled { background: #fff1f2; color: #DC2626; }

/* ── Belgeler ── */
.doc-list { display: flex; flex-direction: column; gap: 8px; }
.doc-item {
  display: flex; align-items: center; gap: 10px;
  padding: 11px 14px; border: 1px solid #e2e8f0; border-radius: 10px;
  background: white; cursor: pointer; text-decoration: none;
  font-size: 13px; transition: border-color 0.15s, background 0.15s;
  width: 100%; text-align: left;
}
.doc-item:hover:not(:disabled) { border-color: #c4beff; background: #fafbff; }
.doc-item:disabled { opacity: 0.45; cursor: default; }
.doc-icon { font-size: 16px; color: #1B1063; flex-shrink: 0; }
.doc-name { flex: 1; font-weight: 600; color: #1e293b; }
.doc-action { font-size: 12px; font-weight: 700; color: #1B1063; }
.doc-hint { color: #94a3b8; font-size: 12px; margin: 10px 0 0; }
.doc-error { color: #DC2626; font-size: 13px; margin: 10px 0 0; }

/* ── Lightbox ── */
.lightbox {
  position: fixed; inset: 0; background: rgba(15,23,42,0.85); backdrop-filter: blur(2px); z-index: 1100;
  display: flex; align-items: center; justify-content: center; padding: 40px; cursor: zoom-out;
  animation: lightboxIn 0.15s ease;
}
@keyframes lightboxIn { from { opacity: 0; } to { opacity: 1; } }
.lightbox img { max-width: 100%; max-height: 100%; border-radius: 10px; box-shadow: 0 20px 60px rgba(0,0,0,0.4); }
.lightbox-close {
  position: absolute; top: 20px; right: 24px;
  width: 36px; height: 36px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: rgba(255,255,255,0.1); border: none; color: rgba(255,255,255,0.8);
  cursor: pointer; transition: background 0.15s, color 0.15s;
}
.lightbox-close:hover { background: rgba(255,255,255,0.2); color: white; }
</style>

<template>
  <div class="content">
    <div v-if="loading" class="loading-state">Yükleniyor...</div>

    <div v-else-if="loadError" class="error-msg">{{ loadError }}</div>

    <template v-else-if="res">
      <!-- Üst bar -->
      <div class="page-head">
        <div class="head-left">
          <button class="btn-back" @click="router.push('/dashboard/rezervasyonlar')">
            <i class="pi pi-arrow-left"></i> Rezervasyonlarım
          </button>
          <div class="head-title">
            <span class="res-code">#{{ res.reservation_id }}</span>
            <span :class="'badge badge-' + statusKey">{{ statusText }}</span>
          </div>
        </div>
        <div class="head-actions">
          <button
            v-if="res.status !== 'cancelled' && !res.delivery_info?.delivered && isFuture"
            class="btn-cancel"
            @click="handleCancel"
          >Rezervasyonu İptal Et</button>
        </div>
      </div>

      <!-- Durum çizelgesi -->
      <div class="card timeline-card" v-if="res.status !== 'cancelled'">
        <div class="timeline">
          <div v-for="(step, i) in steps" :key="step.key" class="tl-step" :class="{ done: step.done, current: step.current }">
            <div class="tl-dot">
              <i v-if="step.done" class="pi pi-check"></i>
              <span v-else>{{ i + 1 }}</span>
            </div>
            <div class="tl-info">
              <div class="tl-label">{{ step.label }}</div>
              <div class="tl-date">{{ step.date || '—' }}</div>
            </div>
            <div v-if="i < steps.length - 1" class="tl-line" :class="{ done: steps[i + 1].done }"></div>
          </div>
        </div>
      </div>
      <div v-else class="cancelled-banner">Bu rezervasyon iptal edilmiştir.</div>

      <div class="detail-grid">
        <!-- Sol sütun -->
        <div class="col-main">

          <!-- Rezervasyon bilgileri -->
          <div class="card">
            <div class="card-title">Rezervasyon Bilgileri</div>
            <div class="info-grid">
              <div class="info-item">
                <span class="ilabel">Rezervasyon No</span>
                <span class="ival">#{{ res.reservation_id }}</span>
              </div>
              <div class="info-item">
                <span class="ilabel">Araç Grubu</span>
                <span class="ival">{{ groupLabel(res.vehicle_group) }}</span>
              </div>
              <div class="info-item">
                <span class="ilabel">Alış Şubesi</span>
                <span class="ival">{{ res.branch_title || res.branch_name }}</span>
              </div>
              <div class="info-item">
                <span class="ilabel">İade Şubesi</span>
                <span class="ival">{{ res.return_branch_title || res.return_branch_name || res.branch_title || res.branch_name }}</span>
              </div>
              <div class="info-item">
                <span class="ilabel">Başlangıç Tarihi</span>
                <span class="ival">{{ formatDate(res.start_date) }}</span>
              </div>
              <div class="info-item">
                <span class="ilabel">Bitiş Tarihi</span>
                <span class="ival">{{ formatDate(res.end_date) }}</span>
              </div>
              <div class="info-item">
                <span class="ilabel">Süre</span>
                <span class="ival">{{ totalDays }} gün</span>
              </div>
              <div class="info-item">
                <span class="ilabel">Toplam Tutar</span>
                <span class="ival price">{{ res.total_price ? Number(res.total_price).toLocaleString('tr-TR') + ' ₺' : '—' }}</span>
              </div>
            </div>
          </div>

          <!-- Teslim -->
          <div class="card" v-if="res.delivery_info?.delivered || res.delivery_info?.delivered_stage">
            <div class="card-title-row">
              <div class="card-title">Teslim Bilgileri</div>
              <span v-if="!res.delivery_info.delivered" class="stage-badge">İşlem devam ediyor</span>
            </div>
            <div class="info-grid">
              <div class="info-item">
                <span class="ilabel">Teslim Tarihi</span>
                <span class="ival">{{ formatDateTime(res.delivery_info.delivered_at) }}</span>
              </div>
              <div class="info-item">
                <span class="ilabel">Teslim KM</span>
                <span class="ival">{{ res.delivery_info.delivered_km != null ? Number(res.delivery_info.delivered_km).toLocaleString('tr-TR') : '—' }}</span>
              </div>
              <div class="info-item fuel-item">
                <span class="ilabel">Yakıt Seviyesi</span>
                <span class="ival fuel-val">
                  <span class="fuel-gauge">
                    <span v-for="i in 8" :key="i" class="fuel-seg" :class="{ on: i <= (res.delivery_info.delivered_fuel ?? 0) }"></span>
                  </span>
                  {{ fuelLabel(res.delivery_info.delivered_fuel) }}
                </span>
              </div>
              <div class="info-item" v-if="res.delivery_info.delivered_notes">
                <span class="ilabel">Notlar</span>
                <span class="ival">{{ res.delivery_info.delivered_notes }}</span>
              </div>
            </div>
            <template v-if="hasDamage(res.delivery_info.delivered_damage)">
              <div class="sub-title">Hasar Durumu</div>
              <div class="damage-readonly">
                <CarDamageMap :model-value="res.delivery_info.delivered_damage || {}" />
              </div>
            </template>
          </div>

          <!-- İade -->
          <div class="card" v-if="res.delivery_info?.returned || res.delivery_info?.returned_stage">
            <div class="card-title-row">
              <div class="card-title">İade Bilgileri</div>
              <span v-if="!res.delivery_info.returned" class="stage-badge">İşlem devam ediyor</span>
            </div>
            <div class="info-grid">
              <div class="info-item">
                <span class="ilabel">İade Tarihi</span>
                <span class="ival">{{ formatDateTime(res.delivery_info.returned_at) }}</span>
              </div>
              <div class="info-item">
                <span class="ilabel">İade KM</span>
                <span class="ival">{{ res.delivery_info.returned_km != null ? Number(res.delivery_info.returned_km).toLocaleString('tr-TR') : '—' }}</span>
              </div>
              <div class="info-item" v-if="kmDriven != null">
                <span class="ilabel">Yapılan KM</span>
                <span class="ival">{{ kmDriven.toLocaleString('tr-TR') }} km</span>
              </div>
              <div class="info-item fuel-item">
                <span class="ilabel">Yakıt Seviyesi</span>
                <span class="ival fuel-val">
                  <span class="fuel-gauge">
                    <span v-for="i in 8" :key="i" class="fuel-seg" :class="{ on: i <= (res.delivery_info.returned_fuel ?? 0) }"></span>
                  </span>
                  {{ fuelLabel(res.delivery_info.returned_fuel) }}
                </span>
              </div>
              <div class="info-item" v-if="res.delivery_info.returned_notes">
                <span class="ilabel">Notlar</span>
                <span class="ival">{{ res.delivery_info.returned_notes }}</span>
              </div>
            </div>
            <template v-if="hasDamage(res.delivery_info.returned_damage)">
              <div class="sub-title">Hasar Durumu</div>
              <div class="damage-readonly">
                <CarDamageMap :model-value="res.delivery_info.returned_damage || {}" />
              </div>
            </template>
          </div>

          <div class="card" v-if="!res.delivery_info?.delivered && !res.delivery_info?.delivered_stage && res.status !== 'cancelled'">
            <div class="card-title">Teslim Bilgileri</div>
            <p class="empty-note">Henüz araç teslimi yapılmadı. Teslim işlemi tamamlandığında detaylar burada görüntülenecek.</p>
          </div>
        </div>

        <!-- Sağ sütun -->
        <div class="col-side">

          <!-- Talep Edilen Model -->
          <div class="card" v-if="res.preferred_vehicle_model_info">
            <div class="card-title">Talep Edilen Model</div>
            <div class="vehicle-head">
              <div class="vehicle-name">{{ res.preferred_vehicle_model_info.brand }} {{ res.preferred_vehicle_model_info.model }}</div>
            </div>
            <p class="equivalent-note">ya da eşdeğeri</p>
          </div>

          <!-- Araç -->
          <div class="card" v-if="res.assigned_vehicle_info">
            <div class="card-title">Atanan Araç</div>
            <p v-if="res.assigned_vehicle_info.is_model_substitute" class="substitute-note">
              Talep ettiğiniz {{ res.preferred_vehicle_model_info?.brand }} {{ res.preferred_vehicle_model_info?.model }} o an müsait olmadığı için aynı sınıftan bu araç size atandı.
            </p>
            <div class="vehicle-head">
              <div class="vehicle-name">{{ res.assigned_vehicle_info.brand }} {{ res.assigned_vehicle_info.model }}</div>
              <div class="vehicle-plate">{{ res.assigned_vehicle_info.plate }}</div>
            </div>
            <div class="info-grid one-col">
              <div class="info-item">
                <span class="ilabel">Araç Grubu</span>
                <span class="ival">{{ groupLabel(res.vehicle_group) }}</span>
              </div>
              <div class="info-item">
                <span class="ilabel">Toplam KM</span>
                <span class="ival">{{ res.assigned_vehicle_info.total_km != null ? Number(res.assigned_vehicle_info.total_km).toLocaleString('tr-TR') : '—' }}</span>
              </div>
            </div>
          </div>
          <div class="card" v-else>
            <div class="card-title">Atanan Araç</div>
            <p class="empty-note">Araç bilgisi, kiralama başlangıç gününde görüntülenebilir.</p>
          </div>

          <!-- Belgeler -->
          <div class="card">
            <div class="card-title">Belgeler</div>
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
            <p v-if="pdfError" class="inline-error">{{ pdfError }}</p>
            <p v-if="!res.delivery_info?.delivered" class="doc-hint">Belgeler, teslim işlemi tamamlandıktan sonra indirilebilir.</p>
          </div>

          <!-- Fatura -->
          <div class="card" v-if="hasBilling">
            <div class="card-title">Fatura Bilgileri</div>
            <div class="info-grid one-col">
              <div class="info-item" v-if="res.billing_type">
                <span class="ilabel">Fatura Tipi</span>
                <span class="ival">{{ res.billing_type === 'kurumsal' ? 'Kurumsal' : 'Bireysel' }}</span>
              </div>
              <div class="info-item" v-if="res.billing_name">
                <span class="ilabel">{{ res.billing_type === 'kurumsal' ? 'Firma Unvanı' : 'Ad Soyad' }}</span>
                <span class="ival">{{ res.billing_name }}</span>
              </div>
              <div class="info-item" v-if="res.billing_tckn">
                <span class="ilabel">TC Kimlik No</span>
                <span class="ival">{{ res.billing_tckn }}</span>
              </div>
              <div class="info-item" v-if="res.billing_tax_office">
                <span class="ilabel">Vergi Dairesi</span>
                <span class="ival">{{ res.billing_tax_office }}</span>
              </div>
              <div class="info-item" v-if="res.billing_tax_no">
                <span class="ilabel">Vergi Kimlik No</span>
                <span class="ival">{{ res.billing_tax_no }}</span>
              </div>
              <div class="info-item" v-if="res.billing_phone">
                <span class="ilabel">Telefon</span>
                <span class="ival">{{ res.billing_phone }}</span>
              </div>
              <div class="info-item" v-if="res.billing_address">
                <span class="ilabel">Adres</span>
                <span class="ival">{{ res.billing_address }}</span>
              </div>
              <div class="info-item" v-if="res.billing_city || res.billing_district || res.billing_neighborhood">
                <span class="ilabel">Mahalle / İlçe / İl</span>
                <span class="ival">{{ [res.billing_neighborhood, res.billing_district, res.billing_city].filter(Boolean).join(' / ') }}</span>
              </div>
            </div>
          </div>

          <!-- Süre uzatma -->
          <div class="card" v-if="res.delivery_info?.delivered && !res.delivery_info?.returned">
            <div class="card-title">Süre Uzatma</div>

            <div v-if="currentExtension" class="ext-status">
              <span :class="'ext-badge ext-' + currentExtension.status">{{ extStatusLabel[currentExtension.status] }}</span>
              <span class="ext-detail">
                Talep edilen bitiş: {{ formatDate(currentExtension.requested_end_date) }}
                <template v-if="currentExtension.status === 'rejected' && currentExtension.reject_reason"> — {{ currentExtension.reject_reason }}</template>
              </span>
            </div>

            <div v-if="canRequestExtension && maxExtendDate" class="ext-form">
              <label class="ext-label">Yeni Bitiş Tarihi</label>
              <div class="ext-row">
                <input type="date" v-model="extendDate" :min="res.end_date" :max="maxExtendDate" class="ext-input" />
                <button class="btn-ext" :disabled="extendLoading" @click="submitExtension">
                  {{ extendLoading ? 'Gönderiliyor...' : 'Talep Et' }}
                </button>
              </div>
              <p class="ext-hint">Fiyatlandırılmış son gün: {{ formatDate(maxExtendDate) }}</p>
              <p v-if="extendError" class="inline-error">{{ extendError }}</p>
              <p v-if="extendMsg" class="inline-success">{{ extendMsg }}</p>
            </div>
            <p v-else-if="canRequestExtension && !maxExtendDate" class="empty-note">İade gününden sonrası için henüz fiyatlandırılmış gün yok, uzatma talep edilemiyor.</p>
            <p v-else-if="!currentExtension" class="empty-note">Uzatma talebi, iade günü gelmeden yapılabilir.</p>
          </div>
        </div>
      </div>

      <!-- Fotoğraf büyütme -->
      <div v-if="lightboxUrl" class="lightbox" @click="lightboxUrl = null">
        <img :src="lightboxUrl" alt="Araç fotoğrafı" />
        <button class="lightbox-close" @click.stop="lightboxUrl = null">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import CarDamageMap from '@/components/CarDamageMap.vue'
import { categoryLabel as groupLabel } from '@/constants/sipp'

const route = useRoute()
const router = useRouter()

const res = ref(null)
const extensions = ref([])
const loading = ref(true)
const loadError = ref('')
const pdfLoading = ref('')
const pdfError = ref('')
const lightboxUrl = ref(null)
const extendDate = ref('')
const extendMsg = ref('')
const extendError = ref('')
const extendLoading = ref(false)
const dailyPrices = ref([])

const apiBase = axios.defaults.baseURL || ''
function mediaUrl(path) {
  if (!path) return ''
  return path.startsWith('http') ? path : apiBase + path
}

function fuelLabel(v) {
  return { 0: 'Boş', 1: '1/8', 2: '1/4', 3: '3/8', 4: '1/2', 5: '5/8', 6: '3/4', 7: '7/8', 8: 'Dolu' }[v] ?? '—'
}
function hasDamage(d) {
  if (!d) return false
  return Object.values(d).some(v => v > 0)
}
function formatDate(d) {
  if (!d) return '—'
  return new Date(d + 'T00:00:00').toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' })
}
function formatDateTime(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const totalDays = computed(() => {
  if (!res.value) return 0
  const s = new Date(res.value.start_date + 'T00:00:00')
  const e = new Date(res.value.end_date + 'T00:00:00')
  return Math.round((e - s) / 86400000) + 1
})

const kmDriven = computed(() => {
  const di = res.value?.delivery_info
  if (di?.returned_km != null && di?.delivered_km != null) return di.returned_km - di.delivered_km
  return null
})

const isFuture = computed(() => res.value && new Date(res.value.start_date + 'T00:00:00') > new Date())

const statusKey = computed(() => {
  const r = res.value
  if (!r) return ''
  if (r.status === 'cancelled') return 'cancelled'
  if (r.delivery_info?.returned) return 'returned'
  if (r.delivery_info?.returned_stage) return 'processing'
  if (r.delivery_info?.delivered) return 'delivered'
  if (r.delivery_info?.delivered_stage) return 'processing'
  return r.status
})
const statusText = computed(() => ({
  pending: 'Bekliyor',
  assigned: 'Onaylandı',
  cancelled: 'İptal Edildi',
  delivered: 'Teslim Edildi',
  returned: 'İade Edildi',
  processing: 'İşlemde',
}[statusKey.value] || statusKey.value))

const steps = computed(() => {
  const r = res.value
  if (!r) return []
  const di = r.delivery_info || {}
  const confirmed = r.status === 'assigned'
  const delivered = !!di.delivered
  const returned = !!di.returned
  return [
    { key: 'created', label: 'Rezervasyon Oluşturuldu', done: true, current: !confirmed, date: '' },
    { key: 'assigned', label: 'Onaylandı', done: confirmed, current: confirmed && !delivered, date: '' },
    { key: 'delivered', label: 'Araç Teslim Edildi', done: delivered, current: delivered && !returned, date: delivered ? formatDateTime(di.delivered_at) : '' },
    { key: 'returned', label: 'İade Alındı', done: returned, current: returned, date: returned ? formatDateTime(di.returned_at) : '' },
  ]
})

const hasBilling = computed(() => {
  const r = res.value
  return r && (r.billing_name || r.billing_address || r.billing_city || r.billing_district || r.billing_neighborhood || r.billing_phone || r.billing_tckn || r.billing_tax_no)
})

const currentExtension = computed(() => {
  if (!res.value) return null
  return extensions.value
    .filter(e => e.reservation === res.value.id)
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))[0] || null
})
const bugun = new Date().toISOString().split('T')[0]
const canRequestExtension = computed(() => {
  const r = res.value
  if (!r) return false
  const active = r.delivery_info?.delivered && !r.delivery_info?.returned
  const beforeReturnDay = r.end_date > bugun
  const hasPending = currentExtension.value && currentExtension.value.status === 'pending'
  return active && beforeReturnDay && !hasPending
})
const extStatusLabel = { pending: 'Bekliyor', approved: 'Onaylandı', rejected: 'Reddedildi' }

function toLocalDateStr(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

// Uzatma sadece res.end_date'ten itibaren ardışık olarak fiyatlandırılmış
// günlere yapılabilir; input bu son güne kadar sınırlandırılır.
const maxExtendDate = computed(() => {
  if (!res.value) return null
  const priced = new Set(dailyPrices.value.map(p => p.date))
  const cursor = new Date(res.value.end_date + 'T00:00:00')
  let last = null
  for (let i = 0; i < 365; i++) {
    cursor.setDate(cursor.getDate() + 1)
    const str = toLocalDateStr(cursor)
    if (!priced.has(str)) break
    last = str
  }
  return last
})

async function loadData() {
  loading.value = true
  loadError.value = ''
  try {
    const [resR, resE] = await Promise.all([
      axios.get(`/api/reservations/${route.params.id}/`),
      axios.get('/api/extensions/'),
    ])
    res.value = resR.data
    extensions.value = resE.data
    if (res.value?.vehicle_group) {
      const resP = await axios.get('/api/daily-prices/', { params: { group: res.value.vehicle_group } })
      dailyPrices.value = resP.data
    }
  } catch {
    loadError.value = 'Rezervasyon bulunamadı veya erişim yetkiniz yok.'
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

async function handleCancel() {
  if (!window.confirm('Rezervasyonu iptal etmek istediğinize emin misiniz?')) return
  try {
    await axios.post(`/api/reservations/${res.value.reservation_id}/cancel/`)
    await loadData()
  } catch {
    loadError.value = 'İptal işlemi başarısız.'
  }
}

async function downloadPdf(type) {
  pdfError.value = ''
  pdfLoading.value = type
  try {
    const r = await axios.get(`/api/reservations/${res.value.id}/pdf/${type}/`, { responseType: 'blob' })
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

async function submitExtension() {
  extendError.value = ''
  extendMsg.value = ''
  if (!extendDate.value) { extendError.value = 'Yeni bitiş tarihi seçin.'; return }
  if (extendDate.value <= res.value.end_date) {
    extendError.value = 'Yeni tarih mevcut bitişten sonra olmalı.'; return
  }
  extendLoading.value = true
  try {
    const r = await axios.post(`/api/reservations/${res.value.id}/extend/`, {
      requested_end_date: extendDate.value,
    })
    if (r.data.status === 'rejected') {
      extendMsg.value = 'Talep otomatik reddedildi: ' + (r.data.reason || 'araç müsait değil.')
    } else {
      extendMsg.value = 'Uzatma talebiniz alındı, temsilci onayı bekleniyor.'
    }
    const resE = await axios.get('/api/extensions/')
    extensions.value = resE.data
  } catch (e) {
    extendError.value = e.response?.data?.error || 'Talep gönderilemedi.'
  } finally {
    extendLoading.value = false
  }
}
</script>

<style scoped>
.content { padding: 32px 40px; max-width: 1160px; margin: 0 auto; }
.loading-state { text-align: center; color: #94a3b8; padding: 60px 0; font-size: 14px; }
.error-msg { color: #dc2626; font-size: 13px; background: #fff1f2; padding: 10px 14px; border-radius: 8px; }

/* ── Üst bar ── */
.page-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.head-left { display: flex; flex-direction: column; gap: 10px; }
.btn-back {
  display: inline-flex; align-items: center; gap: 6px;
  background: none; border: none; padding: 0;
  color: #64748b; font-size: 13px; font-weight: 600; cursor: pointer;
}
.btn-back { transition: color 0.15s; }
.btn-back:hover { color: #6366f1; }
.btn-back i { font-size: 12px; }
.head-title { display: flex; align-items: center; gap: 12px; }
.res-code { font-size: 24px; font-weight: 800; color: #0f172a; letter-spacing: -0.02em; }
.badge { padding: 4px 12px; border-radius: 50px; font-size: 12px; font-weight: 700; }
.badge-pending { background: #fef3c7; color: #92400e; }
.badge-assigned { background: #dbeafe; color: #1d4ed8; }
.badge-cancelled { background: #fee2e2; color: #b91c1c; }
.badge-delivered { background: #d1fae5; color: #065f46; }
.badge-returned { background: #e9d5ff; color: #6b21a8; }
.badge-processing { background: #fed7aa; color: #9a3412; }
.head-actions { display: flex; gap: 8px; }
.btn-cancel {
  padding: 8px 16px; background: white; color: #dc2626;
  border: 1.5px solid #fca5a5; border-radius: 8px;
  font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.15s, border-color 0.15s;
}
.btn-cancel:hover { background: #fff1f2; border-color: #dc2626; }

/* ── Zaman çizelgesi ── */
.card { background: white; border-radius: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); padding: 22px 24px; transition: box-shadow 0.2s; }
.timeline-card { margin-bottom: 20px; padding: 24px 32px; }
.timeline { display: flex; }
.tl-step { display: flex; align-items: flex-start; gap: 12px; flex: 1; position: relative; }
.tl-step:last-child { flex: 0 0 auto; }
.tl-dot {
  width: 30px; height: 30px; border-radius: 50%; flex-shrink: 0;
  background: #f1f5f9; color: #94a3b8;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; z-index: 1;
  transition: background 0.25s, color 0.25s, box-shadow 0.25s;
}
.tl-dot i { font-size: 11px; }
.tl-step.done .tl-dot { background: #6366f1; color: white; }
.tl-step.current .tl-dot { box-shadow: 0 0 0 4px #eef2ff; }
.tl-info { min-width: 0; }
.tl-label { font-size: 13px; font-weight: 700; color: #94a3b8; line-height: 1.3; padding-top: 2px; }
.tl-step.done .tl-label { color: #0f172a; }
.tl-date { font-size: 11.5px; color: #94a3b8; margin-top: 2px; }
.tl-line { flex: 1; height: 2px; background: #f1f5f9; margin: 14px 12px 0 4px; border-radius: 2px; min-width: 20px; transition: background 0.3s; }
.tl-line.done { background: #6366f1; }
.cancelled-banner {
  background: #fff1f2; border: 1px solid #fecdd3; color: #b91c1c;
  padding: 14px 20px; border-radius: 12px; font-size: 14px; font-weight: 600; margin-bottom: 20px;
}

/* ── Grid ── */
.detail-grid { display: grid; grid-template-columns: 1fr 360px; gap: 20px; align-items: start; }
.col-main, .col-side { display: flex; flex-direction: column; gap: 20px; min-width: 0; }

.card-title { font-size: 12px; font-weight: 700; color: #6366f1; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 16px; }
.card-title-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.card-title-row .card-title { margin-bottom: 0; }
.stage-badge { background: #fed7aa; color: #9a3412; padding: 3px 10px; border-radius: 50px; font-size: 11px; font-weight: 700; }
.sub-title { font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em; margin: 18px 0 10px; border-top: 1px solid #f1f5f9; padding-top: 16px; }

.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px 24px; }
.info-grid.one-col { grid-template-columns: 1fr; }
.info-item { display: flex; flex-direction: column; gap: 3px; min-width: 0; }
.ilabel { font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.04em; }
.ival { font-size: 14px; font-weight: 600; color: #1e293b; overflow-wrap: break-word; }
.ival.price { font-weight: 800; color: #0f172a; }

.fuel-item { grid-column: span 2; }
.info-grid.one-col .fuel-item { grid-column: span 1; }
.fuel-val { display: flex; align-items: center; gap: 10px; }
.fuel-gauge { display: inline-flex; gap: 2px; }
.fuel-seg { width: 14px; height: 8px; border-radius: 2px; background: #f1f5f9; }
.fuel-seg.on { background: #6366f1; }

.empty-note { color: #94a3b8; font-size: 13px; margin: 0; line-height: 1.5; }
.substitute-note {
  background: #fffbeb;
  border: 1px solid #fde68a;
  color: #92400e;
  font-size: 12.5px;
  line-height: 1.5;
  padding: 10px 12px;
  border-radius: 8px;
  margin: 0 0 12px;
}
.equivalent-note { color: #94a3b8; font-size: 11.5px; font-style: italic; margin: 4px 0 0; }

/* ── Araç ── */
.vehicle-head { margin-bottom: 16px; padding-bottom: 14px; border-bottom: 1px solid #f1f5f9; }
.vehicle-name { font-size: 17px; font-weight: 800; color: #0f172a; }
.vehicle-plate {
  display: inline-block; margin-top: 6px;
  background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px;
  padding: 3px 10px; font-size: 13px; font-weight: 700; color: #334155; letter-spacing: 0.05em;
}

.damage-readonly { pointer-events: none; }

/* ── Belgeler ── */
.doc-list { display: flex; flex-direction: column; gap: 8px; }
.doc-item {
  display: flex; align-items: center; gap: 10px;
  padding: 11px 14px; border: 1px solid #e2e8f0; border-radius: 10px;
  background: white; cursor: pointer; text-decoration: none;
  font-size: 13px; transition: border-color 0.15s, background 0.15s;
  width: 100%; text-align: left;
}
.doc-item:hover:not(:disabled) { border-color: #c7d2fe; background: #fafbff; }
.doc-item:disabled { opacity: 0.45; cursor: default; }
.doc-icon { font-size: 16px; color: #6366f1; flex-shrink: 0; }
.doc-name { flex: 1; font-weight: 600; color: #1e293b; }
.doc-action { font-size: 12px; font-weight: 700; color: #6366f1; }
.doc-hint { color: #94a3b8; font-size: 12px; margin: 10px 0 0; }

.inline-error { color: #dc2626; font-size: 13px; margin: 10px 0 0; }
.inline-success { color: #065f46; font-size: 13px; margin: 10px 0 0; }

/* ── Uzatma ── */
.ext-status { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; flex-wrap: wrap; }
.ext-badge { padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: 700; }
.ext-pending { background: #fef3c7; color: #92400e; }
.ext-approved { background: #d1fae5; color: #065f46; }
.ext-rejected { background: #fee2e2; color: #b91c1c; }
.ext-detail { font-size: 13px; color: #475569; }
.ext-form { display: flex; flex-direction: column; gap: 8px; }
.ext-label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.06em; text-transform: uppercase; }
.ext-row { display: flex; gap: 8px; align-items: center; }
.ext-hint { font-size: 12px; color: #94a3b8; margin: 0; }
.ext-input { flex: 1; min-width: 0; padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; color: #1e293b; outline: none; transition: border-color 0.15s, box-shadow 0.15s; }
.ext-input:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }
.btn-ext { padding: 8px 16px; background: #6366f1; color: white; border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; white-space: nowrap; transition: background 0.15s; }
.btn-ext:hover:not(:disabled) { background: #4f46e5; }
.btn-ext:disabled { opacity: 0.6; cursor: default; }

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

/* ── Mobil ── */
@media (max-width: 980px) {
  .detail-grid { grid-template-columns: 1fr; }
  .content { padding: 20px; }
  .timeline { flex-direction: column; gap: 18px; }
  .tl-line { display: none; }
  .tl-step { flex: none; }
}
</style>

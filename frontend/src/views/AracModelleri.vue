<template>
  <div class="content">
    <div class="section-header">
      <div class="header-left">
        <h2>Araç Modelleri</h2>
        <span class="count-badge">{{ filteredModels.length }} model</span>
      </div>
      <div class="header-right">
        <input v-model="search" class="search-input" placeholder="Marka veya model ara..." />
        <button class="btn-add" @click="openAdd">+ Model Ekle</button>
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th>Resim</th>
          <th>Marka / Model</th>
          <th>SIPP</th>
          <th>Grup</th>
          <th>Yakıt</th>
          <th>Vites</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="m in filteredModels" :key="m.id">
          <td><img v-if="m.image" :src="m.image" class="thumb" /><span v-else class="thumb-empty">—</span></td>
          <td>{{ m.brand }} {{ m.model }}</td>
          <td class="sipp"><code>{{ m.sipp_code }}</code></td>
          <td><span class="badge-group" :style="{ background: CATEGORY_COLORS[m.group]?.bg, color: CATEGORY_COLORS[m.group]?.text }">{{ categoryLabel(m.group) }}</span></td>
          <td>{{ FUEL_LABELS[m.fuel_type] || m.fuel_type }}</td>
          <td>{{ TRANSMISSION_LABELS[m.transmission] || m.transmission }}</td>
          <td class="actions">
            <div class="action-menu" @click.stop>
              <button class="btn-dots" @click="toggleMenu(m.id)">···</button>
              <div v-if="openMenuId === m.id" class="action-dropdown">
                <button @click="openEdit(m); openMenuId = null">Düzenle</button>
                <button class="danger" @click="confirmDelete(m); openMenuId = null">Sil</button>
              </div>
            </div>
          </td>
        </tr>
        <tr v-if="filteredModels.length === 0">
          <td colspan="8" class="empty">Model bulunamadı.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="formModal" class="modal-overlay" @click.self="formModal = false">
    <div class="modal">
      <h3>{{ editingId ? 'Model Düzenle' : 'Yeni Model Ekle' }}</h3>
      <div class="field type-code-field">
        <label>Marka / Model (Resmi Tip Kodu Listesi)</label>
        <div v-if="form.brand || form.model" class="type-code-selected">
          <span><strong>{{ form.brand }}</strong> {{ form.model }}</span>
          <span v-if="form.type_code" class="type-code-badge">Tip Kodu: {{ selectedTipKodu }}</span>
          <span v-if="selectedYearRange" class="type-code-badge">{{ selectedYearRange }}</span>
          <button type="button" class="type-code-clear" @click="clearTypeCode">Değiştir</button>
        </div>
        <template v-else>
          <input
            v-model="typeCodeQuery"
            type="text"
            placeholder="Marka veya model yazın... (örn. Corolla)"
            autocomplete="off"
            @input="searchTypeCodes"
          />
          <div v-if="typeCodeResults.length" class="type-code-suggestions">
            <button
              v-for="tc in typeCodeResults"
              :key="tc.id"
              type="button"
              class="type-code-option"
              @click="selectTypeCode(tc)"
            >
              <strong>{{ tc.marka_adi }}</strong> {{ tc.tip_adi }}
              <span class="type-code-badge">Tip Kodu: {{ tc.tip_kodu }}</span>
              <span v-if="yearRangeLabel(tc)" class="type-code-badge">{{ yearRangeLabel(tc) }}</span>
            </button>
          </div>
          <p v-else-if="typeCodeQuery.trim().length >= 2" class="type-code-empty">Sonuç yok.</p>
        </template>
      </div>
      <div class="field">
        <label>Grup</label>
        <select v-model="form.group">
          <option v-for="g in CATEGORY_ORDER" :key="g" :value="g">{{ categoryLabel(g) }}</option>
        </select>
      </div>
      <div class="field">
        <label>Kaporta Tipi</label>
        <select v-model="form.body_type">
          <option v-for="o in BODY_TYPE_OPTIONS" :key="o.value" :value="o.value">{{ o.label }}</option>
        </select>
      </div>
      <div class="field">
        <label>Yakıt</label>
        <select v-model="form.fuel_type">
          <option v-for="o in FUEL_OPTIONS" :key="o.value" :value="o.value">{{ o.label }}</option>
        </select>
      </div>
      <div class="field">
        <label>Vites</label>
        <select v-model="form.transmission">
          <option v-for="o in TRANSMISSION_OPTIONS" :key="o.value" :value="o.value">{{ o.label }}</option>
        </select>
      </div>
      <div class="field-row">
        <label class="checkbox-field"><input type="checkbox" v-model="form.is_4wd" /> 4WD (Çekiş)</label>
        <label class="checkbox-field"><input type="checkbox" v-model="form.has_ac" /> Klima</label>
      </div>
      <div class="field">
        <label>Resim</label>
        <input type="file" accept="image/*" @change="onImageChange" />
        <img v-if="imagePreview" :src="imagePreview" class="preview" />
      </div>
      <p v-if="formError" class="error-msg">{{ formError }}</p>
      <div class="modal-actions">
        <button class="btn-cancel-modal" @click="formModal = false">Vazgeç</button>
        <button class="btn-save" @click="saveForm">Kaydet</button>
      </div>
    </div>
  </div>

  <div v-if="deleteModal" class="modal-overlay" @click.self="deleteModal = false">
    <div class="modal modal-sm">
      <h3>Modeli Sil</h3>
      <p class="confirm-text">
        <strong>{{ deletingModel?.brand }} {{ deletingModel?.model }}</strong> silinsin mi?
      </p>
      <div class="modal-actions">
        <button class="btn-cancel-modal" @click="deleteModal = false">Vazgeç</button>
        <button class="btn-delete-confirm" @click="doDelete">Sil</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { CATEGORY_ORDER, CATEGORY_COLORS, categoryLabel } from '@/constants/sipp'

const FUEL_OPTIONS = [
  { value: 'benzin', label: 'Benzin' },
  { value: 'dizel', label: 'Dizel' },
  { value: 'hibrit', label: 'Hibrit' },
  { value: 'elektrik', label: 'Elektrik' },
]
const TRANSMISSION_OPTIONS = [
  { value: 'manuel', label: 'Manuel' },
  { value: 'otomatik', label: 'Otomatik' },
]
const BODY_TYPE_OPTIONS = [
  { value: 'B', label: '2 Kapılı' },
  { value: 'C', label: '2/4 Kapılı' },
  { value: 'D', label: '4 Kapılı' },
  { value: 'W', label: 'Wagon' },
  { value: 'V', label: 'Minivan' },
  { value: 'S', label: 'SUV' },
  { value: 'T', label: 'Kamyonet' },
]
const FUEL_LABELS = Object.fromEntries(FUEL_OPTIONS.map(o => [o.value, o.label]))
const TRANSMISSION_LABELS = Object.fromEntries(TRANSMISSION_OPTIONS.map(o => [o.value, o.label]))

const models = ref([])
const search = ref('')
const openMenuId = ref(null)
const formModal = ref(false)
const editingId = ref(null)
const form = ref({ brand: '', model: '', type_code: null, group: 'E', fuel_type: 'benzin', transmission: 'manuel', body_type: 'D', is_4wd: false, has_ac: true, is_active: true })
const imageFile = ref(null)
const imagePreview = ref('')
const formError = ref('')
const deleteModal = ref(false)
const deletingModel = ref(null)
const typeCodeQuery = ref('')
const typeCodeResults = ref([])
const selectedTipKodu = ref(null)
const selectedYearRange = ref('')
let typeCodeSearchTimer = null

function yearRangeLabel(tc) {
  if (!tc.ilk_yil && !tc.son_yil) return ''
  if (tc.ilk_yil === tc.son_yil) return `${tc.ilk_yil}`
  return `${tc.ilk_yil}–${tc.son_yil}`
}

function searchTypeCodes() {
  clearTimeout(typeCodeSearchTimer)
  const q = typeCodeQuery.value.trim()
  if (q.length < 2) { typeCodeResults.value = []; return }
  typeCodeSearchTimer = setTimeout(async () => {
    const res = await axios.get('/api/type-codes/search/', { params: { q } })
    typeCodeResults.value = res.data
  }, 300)
}

function selectTypeCode(tc) {
  form.value.brand = tc.marka_adi
  form.value.model = tc.tip_adi
  form.value.type_code = tc.id
  selectedTipKodu.value = tc.tip_kodu
  selectedYearRange.value = yearRangeLabel(tc)
  typeCodeQuery.value = ''
  typeCodeResults.value = []
}

function clearTypeCode() {
  form.value.brand = ''
  form.value.model = ''
  form.value.type_code = null
  selectedTipKodu.value = null
  selectedYearRange.value = ''
  typeCodeQuery.value = ''
  typeCodeResults.value = []
}

async function loadData() {
  const res = await axios.get('/api/vehicle-models/')
  models.value = res.data
}

function toggleMenu(id) { openMenuId.value = openMenuId.value === id ? null : id }
function closeMenu() { openMenuId.value = null }
onMounted(() => { loadData(); document.addEventListener('click', closeMenu) })
onUnmounted(() => document.removeEventListener('click', closeMenu))

const filteredModels = computed(() => {
  const q = search.value.toLowerCase().trim()
  if (!q) return models.value
  return models.value.filter(m =>
    (m.brand || '').toLowerCase().includes(q) ||
    (m.model || '').toLowerCase().includes(q)
  )
})

function openAdd() {
  editingId.value = null
  form.value = { brand: '', model: '', type_code: null, group: 'E', fuel_type: 'benzin', transmission: 'manuel', body_type: 'D', is_4wd: false, has_ac: true, is_active: true }
  selectedTipKodu.value = null
  selectedYearRange.value = ''
  typeCodeQuery.value = ''
  typeCodeResults.value = []
  imageFile.value = null
  imagePreview.value = ''
  formError.value = ''
  formModal.value = true
}

function openEdit(m) {
  editingId.value = m.id
  form.value = { brand: m.brand, model: m.model, type_code: m.type_code, group: m.group, fuel_type: m.fuel_type, transmission: m.transmission, body_type: m.body_type, is_4wd: m.is_4wd, has_ac: m.has_ac, is_active: m.is_active }
  selectedTipKodu.value = m.type_code_info?.tip_kodu ?? null
  selectedYearRange.value = m.type_code_info ? yearRangeLabel(m.type_code_info) : ''
  typeCodeQuery.value = ''
  typeCodeResults.value = []
  imageFile.value = null
  imagePreview.value = m.image || ''
  formError.value = ''
  formModal.value = true
}

function onImageChange(e) {
  const file = e.target.files[0]
  if (!file) return
  imageFile.value = file
  imagePreview.value = URL.createObjectURL(file)
}

async function saveForm() {
  formError.value = ''
  if (!form.value.brand || !form.value.model) {
    formError.value = 'Marka ve model zorunludur.'
    return
  }
  const fd = new FormData()
  fd.append('brand', form.value.brand)
  fd.append('model', form.value.model)
  if (form.value.type_code) fd.append('type_code', form.value.type_code)
  fd.append('group', form.value.group)
  fd.append('fuel_type', form.value.fuel_type)
  fd.append('transmission', form.value.transmission)
  fd.append('body_type', form.value.body_type)
  fd.append('is_4wd', form.value.is_4wd)
  fd.append('has_ac', form.value.has_ac)
  fd.append('is_active', form.value.is_active)
  if (imageFile.value) fd.append('image', imageFile.value)
  try {
    if (editingId.value) {
      await axios.patch(`/api/vehicle-models/${editingId.value}/`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    } else {
      await axios.post('/api/vehicle-models/', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    }
    formModal.value = false
    await loadData()
  } catch (e) {
    const data = e.response?.data
    if (data && typeof data === 'object') {
      formError.value = Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join(' | ')
    } else {
      formError.value = 'Kaydetme başarısız.'
    }
  }
}

function confirmDelete(m) {
  deletingModel.value = m
  deleteModal.value = true
}

async function doDelete() {
  try {
    await axios.delete(`/api/vehicle-models/${deletingModel.value.id}/`)
    deleteModal.value = false
    await loadData()
  } catch {
    deleteModal.value = false
  }
}
</script>

<style scoped>
.content { padding: 32px 40px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-left { display: flex; align-items: center; gap: 12px; }
.header-right { display: flex; align-items: center; gap: 10px; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0; }
.count-badge { background: #f1f5f9; color: #475569; font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: 50px; }
.search-input { padding: 8px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; width: 220px; outline: none; }
.btn-add { padding: 9px 18px; background: #6366f1; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-add:hover { background: #4f46e5; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
th { text-align: left; padding: 12px 16px; background: #f8fafc; font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; }
td { padding: 10px 16px; border-top: 1px solid #f1f5f9; color: #374151; }
.thumb { width: 48px; height: 32px; object-fit: cover; border-radius: 6px; }
.thumb-empty { color: #cbd5e1; }
.sipp code { font-family: monospace; font-weight: 700; color: #1e293b; }
.badge-group, .badge-status { display: inline-block; padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: 600; }
.badge-available { background: #d1fae5; color: #065f46; }
.badge-inactive { background: #f1f5f9; color: #475569; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
.actions { text-align: center; }
.action-menu { position: relative; display: inline-block; }
.btn-dots { background: none; border: none; font-size: 18px; cursor: pointer; color: #64748b; padding: 4px 8px; }
.action-dropdown { position: absolute; right: 0; top: 100%; background: white; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.12); z-index: 10; overflow: hidden; min-width: 120px; }
.action-dropdown button { display: block; width: 100%; text-align: left; padding: 10px 14px; background: none; border: none; cursor: pointer; font-size: 13px; color: #374151; }
.action-dropdown button:hover { background: #f8fafc; }
.action-dropdown button.danger { color: #dc2626; }
.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.45); backdrop-filter: blur(2px); z-index: 200; display: flex; align-items: center; justify-content: center; }
.modal { background: white; border-radius: 14px; padding: 32px; width: 420px; box-shadow: 0 20px 60px rgba(15,23,42,0.25); display: flex; flex-direction: column; gap: 14px; max-height: 90vh; overflow-y: auto; }
.modal-sm { width: 340px; }
.modal h3 { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; text-transform: uppercase; }
.field input, .field select { padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; }
.field-row { display: flex; gap: 16px; flex-wrap: wrap; }
.checkbox-field { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #374151; font-weight: 500; text-transform: none; letter-spacing: normal; }
.preview { margin-top: 8px; max-width: 100%; max-height: 120px; border-radius: 8px; object-fit: cover; }
.confirm-text { font-size: 14px; color: #374151; margin: 0; }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; }
.btn-cancel-modal { padding: 8px 16px; background: white; color: #64748b; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-size: 14px; }
.btn-save { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-delete-confirm { padding: 8px 20px; background: #dc2626; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.error-msg { color: #dc2626; font-size: 13px; margin: 0; }
.type-code-field { position: relative; }
.type-code-selected { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; color: #1e293b; background: #f8fafc; }
.type-code-badge { font-size: 11px; font-weight: 600; color: #4f46e5; background: #eef2ff; padding: 2px 8px; border-radius: 50px; }
.type-code-clear { margin-left: auto; padding: 4px 10px; background: white; color: #6366f1; border: 1px solid #c7d2fe; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; }
.type-code-suggestions { margin-top: 4px; max-height: 220px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 8px; background: white; }
.type-code-option { display: flex; align-items: center; gap: 8px; width: 100%; text-align: left; padding: 9px 12px; background: none; border: none; border-bottom: 1px solid #f1f5f9; cursor: pointer; font-size: 13px; color: #374151; }
.type-code-option:last-child { border-bottom: none; }
.type-code-option:hover { background: #f8fafc; }
.type-code-empty { font-size: 12px; color: #94a3b8; margin: 4px 0 0; }
</style>

<template>
  <div class="content">
    <div class="section-header">
      <div class="header-left">
        <h2>Şube Araçları</h2>
        <span class="count-badge">{{ vehicles.length }} araç</span>
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th>Araç ID</th>
          <th>Sasi Kodu</th>
          <th>Marka / Model</th>
          <th>Plaka</th>
          <th>Grup</th>
          <th>Durum</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="v in vehicles" :key="v.id">
          <td class="id">{{ v.vehicle_id }}</td>
          <td>{{ v.sasi }}</td>
          <td>{{ v.brand }} {{ v.model }}</td>
          <td>{{ v.plate || '—' }}</td>
          <td><span :class="'badge-group badge-' + v.group">{{ groupLabel(v.group) }}</span></td>
          <td><span :class="'badge-status badge-' + v.status">{{ statusLabel(v.status) }}</span></td>
          <td class="actions">
            <button class="btn-edit" @click="openEdit(v)">✏️</button>
            <button class="btn-delete" @click="confirmDelete(v)">🗑️</button>
          </td>
        </tr>
        <tr v-if="vehicles.length === 0">
          <td colspan="8" class="empty">Bu şubede araç bulunamadı.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="editModal" class="modal-overlay" @click.self="editModal = false">
    <div class="modal">
      <h3>Araç Düzenle</h3>
      <div class="field">
        <label>Araç ID</label>
        <input :value="editForm.vehicle_id" type="text" disabled class="disabled" />
      </div>
      <div class="field">
        <label>Marka</label>
        <input v-model="editForm.brand" type="text" placeholder="Araç Markası" />
      </div>
      <div class="field">
        <label>Model</label>
        <input v-model="editForm.model" type="text" placeholder="Araç Modeli" />
      </div>
      <div class="field">
        <label>Plaka</label>
        <input v-model="editForm.plate" type="text" placeholder="Plaka" />
      </div>
      <div class="field">
        <label>Sasi Kodu</label>
        <input v-model="editForm.sasi" type="text" placeholder="Sasi Kodu" />
      </div>
      <div class="field">
        <label>Grup</label>
        <select v-model="editForm.group">
          <option value="economy">Ekonomi</option>
          <option value="mid">Orta Sınıf</option>
          <option value="suv">SUV</option>
        </select>
      </div>
      <div class="field">
        <label>Durum</label>
        <select v-model="editForm.status">
          <option value="available">Müsait</option>
          <option value="maintenance">Bakımda</option>
          <option value="service">Serviste</option>
          <option value="inactive">Pasif</option>
          <option value="reserved">Rezerve Edildi</option>
        </select>
      </div>
      <p v-if="formError" class="error">{{ formError }}</p>
      <div class="modal-actions">
        <button class="btn-cancel-modal" @click="editModal = false">Vazgeç</button>
        <button class="btn-save" @click="saveEdit">Kaydet</button>
      </div>
    </div>
  </div>

    <div v-if="deleteModal" class="modal-overlay" @click.self="deleteModal = false">
    <div class="modal modal-sm">
      <h3>Aracı Sil</h3>
      <p class="confirm-text"><strong>{{ deletingVehicle?.vehicle_id }}</strong> aracını silmek istediğinize emin misiniz?</p>
      <div class="modal-actions">
        <button class="btn-cancel-modal" @click="deleteModal = false">Vazgeç</button>
        <button class="btn-delete-confirm" @click="doDelete">Sil</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const vehicles = ref([])
const editModal = ref(false)
const formError = ref('')
const editForm = ref({})
const deleteModal = ref(false)
const deletingVehicle = ref(null)

onMounted(async () => {
  const res = await axios.get('http://127.0.0.1:8000/api/vehicles/')
  vehicles.value = res.data
})

function openEdit(v) {
  editForm.value = { id: v.id, vehicle_id: v.vehicle_id, brand: v.brand, model: v.model, plate: v.plate, sasi: v.sasi, group: v.group, status: v.status }
  formError.value = ''
  editModal.value = true
}

async function saveEdit() {
  formError.value = ''
  try {
    await axios.patch(`http://127.0.0.1:8000/api/vehicles/${editForm.value.id}/`, {
      brand: editForm.value.brand,
      model: editForm.value.model,
      plate: editForm.value.plate,
      sasi: editForm.value.sasi,
      group: editForm.value.group,
      status: editForm.value.status,
    })
    editModal.value = false
    const res = await axios.get('http://127.0.0.1:8000/api/vehicles/')
    vehicles.value = res.data
  } catch (e) {
    formError.value = e.response?.data?.detail || e.response?.data?.plate?.[0] || 'Kaydetme başarısız.'
  }
}

function groupLabel(g) {
  return { economy: 'Ekonomi', mid: 'Orta Sınıf', suv: 'SUV' }[g] || g
}

function statusLabel(s) {
  return { available: 'Müsait', rented: 'Kirada', maintenance: 'Bakımda', service: 'Serviste', inactive: 'Pasif', reserved: 'Rezerve Edildi' }[s] || s
}
</script>

<style scoped>
.content { padding: 32px 40px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-left { display: flex; align-items: center; gap: 12px; }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0; }
.count-badge { padding: 3px 10px; background: #f1f5f9; color: #64748b; border-radius: 50px; font-size: 12px; font-weight: 600; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 14px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
td { border-top: 1px solid #f1f5f9; color: #374151; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
td:nth-child(1), th:nth-child(1), td:nth-child(2), th:nth-child(2), td:nth-child(3), th:nth-child(3), td:nth-child(4), th:nth-child(4), td:nth-child(5), th:nth-child(5), td:nth-child(6), th:nth-child(6), td:nth-child(7), th:nth-child(7), td:nth-child(8), th:nth-child(8) { text-align: center; }
.id { font-family: monospace; font-weight: 600; color: #1e293b; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
.rez-count { display: inline-block; padding: 2px 10px; background: #ede9fe; color: #5b21b6; border-radius: 50px; font-size: 12px; font-weight: 600; }
.badge { padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: 600; }
.badge-group, .badge-status { display: inline-block; padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: 600; }
.badge-available { background: #d1fae5; color: #065f46; }
.badge-rented { background: #fef3c7; color: #92400e; }
.badge-maintenance { background: #fee2e2; color: #991b1b; }
.badge-service { background: #fee2e2; color: #991b1b; }
.badge-inactive { background: #f1f5f9; color: #94a3b8; }
.badge-reserved { background: #ede9fe; color: #4f46e5; }
.badge-group, .badge-status { display: inline-block; padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: 600; }
.badge-economy { background: #dbeafe; color: #1d4ed8; }
.badge-mid { background: #fef3c7; color: #92400e; }
.badge-suv { background: #f3e8ff; color: #6b21a8; }
.actions { width: 60px; }
.btn-edit { padding: 4px 10px; background: white; color: #6366f1; border: 1px solid #6366f1; border-radius: 50px; font-size: 12px; cursor: pointer; }
.btn-edit:hover { background: #ede9fe; }
.btn-delete { padding: 4px 12px; background: white; color: #dc2626; border: 1px solid #dc2626; border-radius: 50px; font-size: 12px; cursor: pointer; }
.btn-delete:hover { background: #fee2e2; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 200; display: flex; align-items: center; justify-content: center; }
.modal { background: white; border-radius: 14px; padding: 32px; width: 420px; box-shadow: 0 8px 32px rgba(0,0,0,0.12); display: flex; flex-direction: column; gap: 14px; }
.modal h3 { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; }
.field input, .field select { padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; background: white; color: #1e293b; }
.field input:focus, .field select:focus { border-color: #6366f1; }
.disabled { background: #f8f9fa !important; color: #94a3b8 !important; cursor: not-allowed; }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 4px; }
.btn-cancel-modal { padding: 8px 16px; background: white; color: #64748b; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-size: 14px; }
.btn-save { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-save:hover { background: #4f46e5; }
.error { color: #dc2626; font-size: 13px; margin: 0; }
</style>

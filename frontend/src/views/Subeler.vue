<template>
  <div class="content">
    <div class="section-header">
      <div class="header-left">
        <h2>Şube Yönetimi</h2>
        <span class="count-badge">{{ branches.length }} şube</span>
      </div>
      <button class="btn-add" @click="openAdd">+ Şube Ekle</button>
    </div>

    <table>
      <thead>
        <tr>
          <th class="sortable" @click="sortBy('id')">ID <span class="sort-ind">{{ sortArrow('id') }}</span></th>
          <th class="sortable" @click="sortBy('title')">Sube İsmi <span class="sort-ind">{{ sortArrow('title') }}</span></th>
          <th class="sortable" @click="sortBy('name')">Sehir <span class="sort-ind">{{ sortArrow('name') }}</span></th>
          <th class="sortable" @click="sortBy('vehicle_count')">Araç Sayısı <span class="sort-ind">{{ sortArrow('vehicle_count') }}</span></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="b in sorted" :key="b.id">
          <td class="id">{{ b.id }}</td>
          <td class="name">{{ b.title || '—' }}</td>
          <td class="city">{{ b.name }}</td>
          <td><span class="count">{{ b.vehicle_count }}</span></td>
          <td class="actions">
            <div class="action-menu" @click.stop>
              <button class="btn-dots" @click="toggleMenu(b.id)">···</button>
              <div v-if="openMenuId === b.id" class="action-dropdown">
                <button @click="openEdit(b); openMenuId = null">Düzenle</button>
              </div>
            </div>
          </td>
        </tr>
        <tr v-if="branches.length === 0">
          <td colspan="5" class="empty">Şube bulunamadı.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="addModal" class="modal-overlay" @click.self="addModal = false">
    <div class="modal">
      <h3>Yeni Şube Ekle</h3>
      <div class="field">
        <label>Şube İsmi</label>
        <input v-model="addForm.title" type="text" placeholder="Şube İsmi" />
      </div>
      <div class="field">
        <label>Şehir</label>
        <select v-model="addForm.name">
          <option value="">Seçin</option>
          <option v-for="sehir in sehirler" :key="sehir" :value="sehir">{{ sehir }}</option>
        </select>
      </div>
      <p v-if="addError" class="error">{{ addError }}</p>
      <div class="modal-actions">
        <button class="btn-cancel-modal" @click="addModal = false">Vazgeç</button>
        <button class="btn-save" @click="saveAdd">Kaydet</button>
      </div>
    </div>
  </div>

  <div v-if="editModal" class="modal-overlay" @click.self="editModal = false">
    <div class="modal">
      <h3>Şube Düzenle</h3>
      <div class="field">
        <label>Şube İsmi</label>
        <input v-model="editForm.title" type="text" placeholder="İstanbul Merkez" />
      </div>
      <div class="field">
        <label>Şehir</label>
        <select v-model="editForm.name">
          <option value="">Seçin</option>
          <option v-for="sehir in sehirler" :key="sehir" :value="sehir">{{ sehir }}</option>
        </select>
      </div>
      <p v-if="editError" class="error">{{ editError }}</p>
      <div class="modal-actions">
        <button class="btn-cancel-modal" @click="editModal = false">Vazgeç</button>
        <button class="btn-save" @click="saveEdit">Kaydet</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useTableSort } from '@/composables/useTableSort'

const sehirler = [
  'Adana','Adıyaman','Afyonkarahisar','Ağrı','Amasya','Ankara','Antalya','Artvin',
  'Aydın','Balıkesir','Bilecik','Bingöl','Bitlis','Bolu','Burdur','Bursa',
  'Çanakkale','Çankırı','Çorum','Denizli','Diyarbakır','Edirne','Elazığ',
  'Erzincan','Erzurum','Eskişehir','Gaziantep','Giresun','Gümüşhane','Hakkâri',
  'Hatay','Isparta','Mersin','İstanbul','İzmir','Kars','Kastamonu','Kayseri',
  'Kırklareli','Kırşehir','Kocaeli','Konya','Kütahya','Malatya','Manisa',
  'Kahramanmaraş','Mardin','Muğla','Muş','Nevşehir','Niğde','Ordu','Rize',
  'Sakarya','Samsun','Siirt','Sinop','Sivas','Tekirdağ','Tokat','Trabzon',
  'Tunceli','Şanlıurfa','Uşak','Van','Yozgat','Zonguldak','Aksaray','Bayburt',
  'Karaman','Kırıkkale','Batman','Şırnak','Bartın','Ardahan','Iğdır','Yalova',
  'Karabük','Kilis','Osmaniye','Düzce',
]

const branches = ref([])
const openMenuId = ref(null)

const { sortBy, sortArrow, sorted } = useTableSort(branches, {
  id: b => Number(b.id) || 0,
  vehicle_count: b => Number(b.vehicle_count) || 0,
})
const addModal = ref(false)
const addForm = ref({ name: '', title: '' })
const addError = ref('')
const editModal = ref(false)
const editForm = ref({ id: null, name: '', title: '' })
const editError = ref('')

async function loadBranches() {
  const [branchRes, vehicleRes] = await Promise.all([
    axios.get('/api/branches/'),
    axios.get('/api/vehicles/'),
  ])
  const vehicles = vehicleRes.data
  branches.value = branchRes.data.map(b => ({
    ...b,
    vehicle_count: vehicles.filter(v => v.branch === b.id).length,
  }))
}

function toggleMenu(id) { openMenuId.value = openMenuId.value === id ? null : id }
function closeMenu() { openMenuId.value = null }
onMounted(() => { loadBranches(); document.addEventListener('click', closeMenu) })
onUnmounted(() => document.removeEventListener('click', closeMenu))

function openAdd() {
  addForm.value = { name: '', title: '' }
  addError.value = ''
  addModal.value = true
}

async function saveAdd() {
  if (!addForm.value.name || !addForm.value.title) {
    addError.value = 'Tüm alanları doldurun.'
    return
  }
  try {
    await axios.post('/api/branches/', addForm.value)
    addModal.value = false
    await loadBranches()
  } catch {
    addError.value = 'Kaydetme başarısız.'
  }
}

function openEdit(branch) {
  editForm.value = { id: branch.id, name: branch.name, title: branch.title }
  editError.value = ''
  editModal.value = true
}

async function saveEdit() {
  try {
    await axios.patch(`/api/branches/${editForm.value.id}/`, {
      name: editForm.value.name,
      title: editForm.value.title,
    })
    editModal.value = false
    await loadBranches()
  } catch {
    editError.value = 'Kaydetme başarısız.'
  }
}
</script>

<style scoped>
.content { padding: 32px 40px; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.header-left { display: flex; align-items: center; gap: 12px; }
.btn-add { padding: 8px 18px; background: #6366f1; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.15s, transform 0.15s, box-shadow 0.15s; }
.btn-add:hover { background: #4f46e5; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(79,70,229,0.3); }
.btn-add:active { transform: translateY(0); }
h2 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0; }
.count-badge { padding: 3px 10px; background: #f1f5f9; color: #64748b; border-radius: 50px; font-size: 12px; font-weight: 600; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
th:first-child { border-radius: 14px 0 0 0; } th:last-child { border-radius: 0 14px 0 0; } th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
th.sortable { cursor: pointer; user-select: none; transition: color 0.15s; }
th.sortable:hover { color: #6366f1; }
.sort-ind { font-size: 9px; color: #6366f1; }
tbody tr { transition: background 0.12s; }
tbody tr:hover { background: #fafbff; }
td { border-top: 1px solid #f1f5f9; color: #374151; }
.id { color: #94a3b8; font-size: 13px; }
.name { font-weight: 600; color: #1e293b; }
.city { color: #35455e; font-family: monospace; font-size: 13px; }
.count { display: inline-block; padding: 2px 10px; background: #8a8a8a3b; color: #000000; border-radius: 50px; font-size: 12px; font-weight: 600; }
.empty { text-align: center; color: #94a3b8; padding: 32px !important; }
td:nth-child(1), th:nth-child(1), td:nth-child(2), th:nth-child(2), td:nth-child(3), th:nth-child(3), td:nth-child(4), th:nth-child(4) { text-align: center; }
.actions { text-align: center !important; }
.action-menu { position: relative; display: inline-block; }
.btn-dots { background: none; border: 1px solid #e2e8f0; border-radius: 6px; padding: 4px 10px; cursor: pointer; font-size: 16px; color: #64748b; line-height: 1; letter-spacing: 2px; transition: background 0.15s, border-color 0.15s; }
.btn-dots:hover { background: #f1f5f9; border-color: #cbd5e1; }
.action-dropdown { position: absolute; right: 0; top: calc(100% + 4px); background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 8px 24px rgba(15,23,42,0.12); min-width: 110px; z-index: 300; overflow: hidden; animation: dropdownIn 0.12s ease; }
@keyframes dropdownIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }
.action-dropdown button { display: block; width: 100%; padding: 9px 14px; text-align: left; background: none; border: none; font-size: 13px; color: #374151; cursor: pointer; transition: background 0.12s; }
.action-dropdown button:hover { background: #f8fafc; }
.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.45); backdrop-filter: blur(2px); z-index: 200; display: flex; align-items: center; justify-content: center; animation: overlayIn 0.15s ease; }
@keyframes overlayIn { from { opacity: 0; } to { opacity: 1; } }
.modal { background: white; border-radius: 14px; padding: 32px; width: 400px; box-shadow: 0 20px 60px rgba(15,23,42,0.25); display: flex; flex-direction: column; gap: 16px; animation: modalIn 0.18s cubic-bezier(0.4,0,0.2,1); }
@keyframes modalIn { from { opacity: 0; transform: translateY(8px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal h3 { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 11px; font-weight: 700; color: #6366f1; letter-spacing: 0.08em; }
.field input, .field select { padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; transition: border-color 0.15s, box-shadow 0.15s; }
.field input:focus, .field select:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 4px; }
.btn-cancel-modal { padding: 8px 16px; background: white; color: #64748b; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-size: 14px; transition: background 0.15s, border-color 0.15s; }
.btn-cancel-modal:hover { background: #f8fafc; border-color: #cbd5e1; }
.btn-save { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; transition: background 0.15s, transform 0.15s; }
.btn-save:hover { background: #4f46e5; transform: translateY(-1px); }
.error { color: #dc2626; font-size: 13px; margin: 0; }
</style>

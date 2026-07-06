<template>
  <div class="content">
    <div class="card">
      <h2>Hesap Bilgileri</h2>

      <div class="field">
        <label>Kullanıcı Adı</label>
        <input v-model="form.username" type="text" />
      </div>
      <div class="field">
        <label>Ad Soyad</label>
        <input v-model="form.full_name" type="text" placeholder="Ad Soyad" />
      </div>
      <div class="field">
        <label>E-posta</label>
        <input v-model="form.email" type="email" placeholder="E-posta" />
      </div>
      <div class="field">
        <label>Telefon</label>
        <input v-model="form.phone" type="text" placeholder="Telefon" />
      </div>

      <div class="divider"></div>
      <h3>Fatura Bilgileri</h3>

      <div class="field">
        <label>Fatura Tipi</label>
        <select v-model="form.billing_type">
          <option value="bireysel">Bireysel</option>
          <option value="kurumsal">Kurumsal</option>
        </select>
      </div>

      <div class="field" v-if="form.billing_type === 'kurumsal'">
        <label>Firma Unvanı</label>
        <input v-model="form.billing_name" type="text" placeholder="Firma Unvanı" />
      </div>

      <template v-if="form.billing_type === 'kurumsal'">
        <div class="field">
          <label>Vergi Dairesi</label>
          <input v-model="form.billing_tax_office" type="text" placeholder="Vergi Dairesi" />
        </div>
        <div class="field">
          <label>Vergi Kimlik No</label>
          <input v-model="form.billing_tax_no" type="text" maxlength="10" placeholder="10 haneli VKN" />
        </div>
      </template>

      <div class="field" v-else>
        <label>TC Kimlik No</label>
        <input v-model="form.billing_tckn" type="text" maxlength="11" placeholder="11 haneli TCKN" />
      </div>

      <div class="field">
        <label>Adres</label>
        <input v-model="form.billing_address" type="text" placeholder="Açık Adres" />
      </div>

      <div class="field">
        <label>İl</label>
        <select v-model="form.billing_city" @change="form.billing_district = ''">
          <option value="" disabled>İl seçin</option>
          <option v-for="il in iller" :key="il" :value="il">{{ il }}</option>
        </select>
      </div>

      <div class="field">
        <label>İlçe</label>
        <select v-model="form.billing_district" :disabled="!form.billing_city">
          <option value="" disabled>İlçe seçin</option>
          <option v-for="ilce in ilceler" :key="ilce" :value="ilce">{{ ilce }}</option>
        </select>
      </div>

      <div class="field">
        <label>Mahalle</label>
        <input v-model="form.billing_neighborhood" type="text" placeholder="Mahalle" />
      </div>

      <div class="divider"></div>
      <h3>Şifre Değiştir</h3>
      <div class="field">
        <label>Yeni Şifre</label>
        <input v-model="form.new_password" type="password" placeholder="Boş bırakırsan değişmez" />
      </div>

      <p v-if="success" class="success">{{ success }}</p>
      <p v-if="error" class="error">{{ error }}</p>

      <button class="btn-save" @click="handleSave">Kaydet</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { ILLER, getIlceler } from '../utils/address'

const auth = useAuthStore()
const iller = ILLER
const form = ref({
  username: '', full_name: '', email: '', phone: '', new_password: '',
  billing_type: 'bireysel', billing_name: '', billing_tckn: '', billing_tax_office: '', billing_tax_no: '',
  billing_address: '', billing_neighborhood: '', billing_district: '', billing_city: '',
})
const ilceler = computed(() => getIlceler(form.value.billing_city))
const success = ref('')
const error = ref('')

onMounted(async () => {
  const res = await axios.get('/api/profile/')
  form.value = { ...res.data, new_password: '' }
})

async function handleSave() {
  success.value = ''
  error.value = ''
  try {
    const res = await axios.patch('/api/profile/', {
      username: form.value.username,
      email: form.value.email,
      full_name: form.value.full_name,
      phone: form.value.phone,
      billing_type: form.value.billing_type,
      billing_name: form.value.billing_name,
      billing_tckn: form.value.billing_tckn,
      billing_tax_office: form.value.billing_tax_office,
      billing_tax_no: form.value.billing_tax_no,
      billing_address: form.value.billing_address,
      billing_neighborhood: form.value.billing_neighborhood,
      billing_district: form.value.billing_district,
      billing_city: form.value.billing_city,
      new_password: form.value.new_password || undefined,
    })
    success.value = 'Profil güncellendi.'
    form.value.new_password = ''
    auth.setUsername(form.value.username)
    if (res.data.token) {
      auth.login(res.data.token, form.value.username, auth.isStaff)
    }
  } catch (e) {
    error.value = e.response?.data?.error || 'Güncelleme başarısız.'
  }
}
</script>

<style scoped>
.content { padding: 32px 40px; }
.card { background: white; border-radius: 14px; padding: 32px; box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04); }
h2 { font-size: 16px; font-weight: 700; color: #1e293b; margin: 0 0 20px; }
h3 { font-size: 14px; font-weight: 700; color: #1e293b; margin: 0 0 16px; }
.field { display: flex; flex-direction: column; gap: 7px; margin-bottom: 16px; }
.field label { font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.06em; }
.field input, .field select { padding: 11px 14px; border: 1.5px solid #e2e8f0; border-radius: 9px; font-size: 14px; color: #1e293b; outline: none; background: white; }
.field input:focus, .field select:focus { border-color: #6366f1; }
.divider { height: 1px; background: #f1f5f9; margin: 24px 0 20px; }
.btn-save { margin-top: 8px; padding: 11px 28px; background: #6366f1; color: white; border: none; border-radius: 9px; font-size: 14px; font-weight: 700; cursor: pointer; }
.btn-save:hover { background: #4f46e5; }
.success { color: #16a34a; font-size: 13px; background: #f0fdf4; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; font-weight: 500; }
.error { color: #dc2626; font-size: 13px; background: #fff1f2; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; }
</style>
